import time
from typing import Optional, Dict, Any, List
from app.core.logging_config import logger
from app.schemas.profile import CitizenProfile
from app.schemas.agent_outputs import (
    MultiAgentWorkflowResponse,
    SimplifiedSchemeOutput,
    SchemeRecommendation,
)
from app.agents.profile_collector import profile_collector_agent
from app.agents.eligibility_matcher import eligibility_matcher_agent
from app.agents.scheme_explainer import scheme_explainer_agent
from app.agents.language_simplifier import language_simplifier_agent
from app.services.conversation_service import conversation_service

class MultiAgentWorkflowOrchestrator:
    """Coordinates the 4-agent pipeline for personalized welfare scheme discovery."""

    def __init__(self):
        self.profile_agent = profile_collector_agent
        self.matcher_agent = eligibility_matcher_agent
        self.explainer_agent = scheme_explainer_agent
        self.simplifier_agent = language_simplifier_agent
        self.conv_service = conversation_service

    def run(
        self,
        session_id: str,
        user_message: str,
        target_language: str = "en",
        direct_profile_override: Optional[CitizenProfile] = None
    ) -> MultiAgentWorkflowResponse:
        total_start = time.perf_counter()
        latencies: Dict[str, float] = {}

        # 0. Session initialization
        session = self.conv_service.get_or_create_session(session_id, language=target_language)
        current_profile = direct_profile_override if direct_profile_override is not None else session.profile

        # 1. Agent 1: Profile Collector Agent
        t1 = time.perf_counter()
        extraction_res = self.profile_agent.process_turn(user_message, current_profile=current_profile)
        latencies["agent_1_profile_collector_ms"] = round((time.perf_counter() - t1) * 1000, 2)
        
        # Persist updated profile
        updated_profile = extraction_res.profile
        self.conv_service.update_profile(session_id, updated_profile)

        # If user message was purely a clarification or profile is still missing critical fields
        # and has zero matches, we return the clarification question immediately.
        # But if the user gave some keywords or profile has at least state or occupation,
        # we can provide preliminary matches alongside the follow-up question.
        recommendations: List[SimplifiedSchemeOutput] = []
        raw_recs: List[SchemeRecommendation] = []
        unmatched_reasons: List[str] = []

        should_run_matching = (
            updated_profile.state is not None or
            updated_profile.occupation is not None or
            updated_profile.query_text is not None or
            extraction_res.profile_complete
        )

        if should_run_matching:
            # 2. Agent 2: Eligibility Matcher Agent
            t2 = time.perf_counter()
            match_output = self.matcher_agent.match(updated_profile, top_k=5)
            raw_recs = match_output.recommendations
            unmatched_reasons = match_output.unmatched_reasons
            latencies["agent_2_eligibility_matcher_ms"] = round((time.perf_counter() - t2) * 1000, 2)

            # 3 & 4. Agent 3 (Explainer) and Agent 4 (Language Simplifier)
            t3_total = 0.0
            t4_total = 0.0

            for rec in raw_recs:
                # Agent 3: Explain
                t3 = time.perf_counter()
                explanation = self.explainer_agent.explain(rec)
                t3_total += (time.perf_counter() - t3)

                # Agent 4: Simplify & Localize
                t4 = time.perf_counter()
                simplified = self.simplifier_agent.simplify(explanation, target_language=target_language)
                t4_total += (time.perf_counter() - t4)

                recommendations.append(simplified)

            latencies["agent_3_scheme_explainer_ms"] = round(t3_total * 1000, 2)
            latencies["agent_4_language_simplifier_ms"] = round(t4_total * 1000, 2)
        else:
            latencies["agent_2_eligibility_matcher_ms"] = 0.0
            latencies["agent_3_scheme_explainer_ms"] = 0.0
            latencies["agent_4_language_simplifier_ms"] = 0.0

        total_elapsed_ms = round((time.perf_counter() - total_start) * 1000, 2)
        latencies["total_pipeline_ms"] = total_elapsed_ms

        # Record conversation history
        agent_reply_summary = (
            extraction_res.clarification_question
            if extraction_res.clarification_question and not recommendations
            else f"Recommended {len(recommendations)} schemes for your profile."
        )
        self.conv_service.record_turn(session_id, user_message, agent_reply_summary)

        return MultiAgentWorkflowResponse(
            session_id=session_id,
            language=target_language,
            profile=updated_profile,
            profile_complete=extraction_res.profile_complete,
            clarification_question=extraction_res.clarification_question,
            suggested_options=extraction_res.suggested_options,
            acknowledgement_text=extraction_res.acknowledgement_text,
            recommendations=recommendations,
            raw_recommendations=raw_recs,
            meta={
                "latencies": latencies,
                "matched_count": len(recommendations),
                "unmatched_reasons": unmatched_reasons,
                "extracted_fields": extraction_res.extracted_fields,
            }
        )

workflow_orchestrator = MultiAgentWorkflowOrchestrator()
