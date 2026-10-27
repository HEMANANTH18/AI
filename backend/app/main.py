import time
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Body, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.profile import CitizenProfile
from app.schemas.agent_outputs import (
    MultiAgentWorkflowResponse,
    EligibilityMatcherOutput,
    SimplifiedSchemeOutput,
)
from app.data.csv_loader import loader
from app.data.data_quality import assess_data_quality
from app.retrieval.vector_store import vector_store
from app.services.scheme_service import scheme_service
from app.services.conversation_service import conversation_service
from app.agents.language_simplifier import SUPPORTED_LANGUAGES, language_simplifier_agent
from app.agents.scheme_explainer import scheme_explainer_agent
from app.agents.eligibility_matcher import eligibility_matcher_agent
from app.orchestration.workflow import workflow_orchestrator

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing BenefitBridge AI backend services...")
    yield
    logger.info("BenefitBridge AI backend shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A Multi-Agent RAG Framework for Personalized Government Welfare Scheme Recommendation in India",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Request Models -----------------

class ChatMessageRequest(BaseModel):
    session_id: str
    message: str
    language: str = "en"
    profile_override: Optional[CitizenProfile] = None

class RecommendationRequest(BaseModel):
    profile: CitizenProfile
    top_k: int = 10
    language: str = "en"

class ResetSessionRequest(BaseModel):
    session_id: str

class LocalizeRecommendationsRequest(BaseModel):
    session_id: str
    language: str = "en"
    scheme_ids: List[str] = []

# ----------------- API Endpoints -----------------

@app.get("/api/health", tags=["System"])
def health_check():
    """System health check and index status."""
    is_stale, stale_msg = vector_store.is_stale()
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "schemes_loaded": len(loader.get_all()),
        "vector_store_records": vector_store.count(),
        "vector_store_status": "synced" if not is_stale else "needs_indexing",
        "vector_store_message": stale_msg,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "gemini_model": settings.GEMINI_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
    }

@app.get("/api/dataset/status", tags=["Dataset"])
def dataset_status():
    """Returns dataset metrics, data quality audit, and schema summary."""
    schemes = loader.get_all()
    quality = assess_data_quality(schemes)
    metadata = scheme_service.get_metadata()
    return {
        "dataset_profile": quality,
        "metadata": metadata,
        "authoritative_source": "schemes.csv (myScheme.gov.in)",
    }

@app.get("/api/schemes", tags=["Schemes"])
def list_or_search_schemes(
    query: Optional[str] = Query(None, description="Search term in title, description, or tags"),
    state: Optional[str] = Query(None, description="Filter by state or UT (Central included)"),
    category: Optional[str] = Query(None, description="Filter by scheme category"),
    benefit_type: Optional[str] = Query(None, description="Filter by benefit type (Cash, In Kind, Composite)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Search and browse verified government welfare schemes with filters."""
    return scheme_service.search_schemes(
        query=query,
        state=state,
        category=category,
        benefit_type=benefit_type,
        limit=limit,
        offset=offset
    )

@app.get("/api/schemes/{scheme_id}", tags=["Schemes"])
def get_scheme_detail(scheme_id: str):
    """Retrieve complete official scheme details by slug."""
    scheme = scheme_service.get_scheme_by_id(scheme_id)
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with ID '{scheme_id}' was not found in dataset."
        )
    return scheme

@app.post("/api/chat", response_model=MultiAgentWorkflowResponse, tags=["Conversational AI"])
def chat_turn(request: ChatMessageRequest):
    """
    Primary multi-agent conversation endpoint.
    Conducts interview, updates profile, checks eligibility, and generates multilingual recommendations.
    """
    response = workflow_orchestrator.run(
        session_id=request.session_id,
        user_message=request.message,
        target_language=request.language,
        direct_profile_override=request.profile_override
    )
    return response

@app.post("/api/recommendations", response_model=EligibilityMatcherOutput, tags=["Recommendation"])
def get_recommendations_for_profile(request: RecommendationRequest):
    """Direct profile eligibility matching and scoring without conversation turn."""
    return eligibility_matcher_agent.match(
        profile=request.profile,
        top_k=request.top_k,
        include_ineligible=False
    )

@app.get("/api/languages", tags=["Localization"])
def get_supported_languages():
    """List of supported Indian languages with native scripts."""
    return [
        {"code": code, "name": meta["name"], "native": meta["native"]}
        for code, meta in SUPPORTED_LANGUAGES.items()
    ]

@app.post("/api/localize-recommendations", response_model=List[SimplifiedSchemeOutput], tags=["Localization"])
def localize_recommendations(request: LocalizeRecommendationsRequest):
    """Dynamically re-localizes given scheme recommendations to the requested Indian language."""
    session = conversation_service.get_session(request.session_id)
    profile = session.profile if session else CitizenProfile()

    localized: List[SimplifiedSchemeOutput] = []
    for sid in request.scheme_ids:
        scheme = scheme_service.get_scheme_by_id(sid)
        if not scheme:
            continue
        rec = eligibility_matcher_agent.evaluate_scheme(scheme, profile)
        explanation = scheme_explainer_agent.explain(rec)
        simplified = language_simplifier_agent.simplify(explanation, target_language=request.language)
        localized.append(simplified)
    return localized

@app.post("/api/session/reset", tags=["Session"])
def reset_session(request: ResetSessionRequest):
    """Reset citizen profile and conversation history for a new interview."""
    session = conversation_service.reset_session(request.session_id)
    return {
        "status": "reset_successful",
        "session_id": session.session_id,
        "message": "Conversation session and profile reset successfully."
    }

@app.post("/api/index/rebuild", tags=["Administration"])
def rebuild_vector_index():
    """Triggers SentenceTransformers embedding and ChromaDB vector indexing."""
    schemes = loader.get_all()
    result = vector_store.build_index(schemes)
    return result
