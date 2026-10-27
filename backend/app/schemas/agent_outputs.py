from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from app.schemas.profile import CitizenProfile
from app.schemas.scheme import Scheme

class CriterionResult(BaseModel):
    criterion: str = Field(..., description="Criterion evaluated (e.g. state, age, income, gender, occupation, category)")
    status: Literal["pass", "fail", "unknown", "not_applicable"] = Field(...)
    reason: str = Field(..., description="Explanation of evaluation outcome")
    source_text: Optional[str] = Field(None, description="Relevant excerpt from scheme eligibility criteria")

class SchemeRecommendation(BaseModel):
    scheme_id: str
    scheme_name: str
    short_title: str = ""
    level: str
    state: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    benefit_type: str = "Composite"
    eligibility_status: Literal[
        "eligible_based_on_available_rules",
        "potentially_eligible",
        "not_eligible_based_on_known_rules",
        "insufficient_information"
    ]
    match_score: float = Field(..., ge=0.0, le=1.0, description="Relevance and compatibility score")
    semantic_score: float = Field(0.0, description="Semantic cosine similarity from vector retrieval")
    criteria_results: List[CriterionResult] = Field(default_factory=list)
    matched_reasons: List[str] = Field(default_factory=list)
    unmet_conditions: List[str] = Field(default_factory=list)
    unknown_conditions: List[str] = Field(default_factory=list)
    brief_description: str = ""
    benefits: List[str] = Field(default_factory=list)
    documents_required: List[str] = Field(default_factory=list)
    application_steps: List[str] = Field(default_factory=list)
    official_application_url: Optional[str] = None
    source_record: Optional[Dict[str, Any]] = None

class EligibilityMatcherOutput(BaseModel):
    matched_scheme_ids: List[str] = Field(default_factory=list)
    recommendations: List[SchemeRecommendation] = Field(default_factory=list)
    total_evaluated: int = 0
    unmatched_reasons: List[str] = Field(default_factory=list)
    requires_clarification: bool = False

class SchemeExplanation(BaseModel):
    scheme_id: str
    scheme_name: str
    eligibility_summary: str
    benefits: List[str] = Field(default_factory=list)
    application_steps: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    official_application_url: Optional[str] = None
    unknown_information: List[str] = Field(default_factory=list)
    source_fields: List[str] = Field(default_factory=list)
    grounding_verified: bool = True

class SimplifiedSchemeOutput(BaseModel):
    language: str
    scheme_id: str
    localized_scheme_name: str
    simple_explanation: str
    benefits: List[str] = Field(default_factory=list)
    eligibility_summary: str
    application_steps: List[str] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    official_application_url: Optional[str] = None
    important_cautions: List[str] = Field(default_factory=list)
    is_fallback: bool = False

class MultiAgentWorkflowResponse(BaseModel):
    session_id: str
    language: str
    profile: CitizenProfile
    profile_complete: bool
    clarification_question: Optional[str] = None
    suggested_options: Optional[List[str]] = None
    acknowledgement_text: Optional[str] = None
    recommendations: List[SimplifiedSchemeOutput] = Field(default_factory=list)
    raw_recommendations: List[SchemeRecommendation] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)
