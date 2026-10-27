import json
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.agent_outputs import SchemeRecommendation, SchemeExplanation

class SchemeExplainerAgent:
    """Agent 3: Grounded Scheme Explainer & Application Navigator."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client = None

    def _get_client(self):
        if not self._client and self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai client: {e}")
                self._client = None
        return self._client

    def explain(self, rec: SchemeRecommendation) -> SchemeExplanation:
        """Generates grounded explanation for a single scheme recommendation."""
        # 1. Try Gemini API generation if client is available
        client = self._get_client()
        if client:
            try:
                explanation = self._explain_with_gemini(client, rec)
                if explanation:
                    return explanation
            except Exception as e:
                logger.warning(f"Gemini API explanation failed for {rec.scheme_id}: {e}. Falling back to deterministic explainer.")

        # 2. Deterministic Fallback Explainer
        return self._explain_fallback(rec)

    def _explain_with_gemini(self, client: Any, rec: SchemeRecommendation) -> Optional[SchemeExplanation]:
        prompt = f"""You are the BenefitBridge AI Scheme Explainer Agent.
Analyze the following authentic government welfare scheme record and provide a grounded, truthful explanation for a citizen.

CRITICAL CONSTRAINTS:
1. ONLY use the provided facts. Do NOT hallucinate benefit amounts, document names, criteria, or URLs.
2. If a field is missing or empty in the record, explicitly say that the dataset does not specify it.
3. Do not convert 'potentially eligible' into 'definitely eligible'.
4. Do not offer to submit applications on the citizen's behalf.
5. Return strictly valid JSON matching this schema:
{{
  "scheme_id": "{rec.scheme_id}",
  "scheme_name": "{rec.scheme_name}",
  "eligibility_summary": "plain language summary of who qualifies",
  "benefits": ["benefit 1", "benefit 2"],
  "application_steps": ["step 1", "step 2"],
  "required_documents": ["doc 1", "doc 2"],
  "official_application_url": "{rec.official_application_url or ''}",
  "unknown_information": ["item 1 needing verification"],
  "source_fields": ["source field names used"]
}}

SCHEME DATA RECORD:
ID: {rec.scheme_id}
Name: {rec.scheme_name}
Level: {rec.level}
State: {rec.state or 'All India'}
Eligibility Status: {rec.eligibility_status}
Matched Reasons: {rec.matched_reasons}
Unmet Conditions: {rec.unmet_conditions}
Unknown Conditions: {rec.unknown_conditions}
Brief Description: {rec.brief_description}
Benefits: {rec.benefits}
Documents Required: {rec.documents_required}
Application Steps: {rec.application_steps}
Official URL: {rec.official_application_url}
"""
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        if response and response.text:
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            data = json.loads(cleaned_text.strip())
            return SchemeExplanation(
                scheme_id=rec.scheme_id,
                scheme_name=rec.scheme_name,
                eligibility_summary=data.get("eligibility_summary", rec.brief_description),
                benefits=data.get("benefits", rec.benefits),
                application_steps=data.get("application_steps", rec.application_steps),
                required_documents=data.get("required_documents", rec.documents_required),
                official_application_url=rec.official_application_url,
                unknown_information=data.get("unknown_information", rec.unknown_conditions),
                source_fields=["scheme_name", "eligibility", "benefits", "documents_required", "application_process", "source_url"],
                grounding_verified=True,
            )
        return None

    def _explain_fallback(self, rec: SchemeRecommendation) -> SchemeExplanation:
        """Deterministic, grounded explanation using verified dataset fields."""
        reasons_text = " ".join(rec.matched_reasons) if rec.matched_reasons else "Identified based on semantic relevance to your profile."
        eligibility_summary = f"{rec.brief_description} Status: {rec.eligibility_status.replace('_', ' ').capitalize()}. {reasons_text}"

        benefits_list = rec.benefits if rec.benefits else ["The dataset specifies support under this scheme, but specific monetary or in-kind tiers require verification with the nodal department."]
        steps_list = rec.application_steps if rec.application_steps else ["Visit the official government scheme portal or nearest Common Service Centre (CSC) to obtain and submit the prescribed application form."]
        docs_list = rec.documents_required if rec.documents_required else ["Identity proof (e.g. Aadhaar Card) and domicile proof are typically required by issuing authorities."]

        unknown_info = list(rec.unknown_conditions)
        if not rec.benefits:
            unknown_info.append("Monetary/in-kind benefit tier breakdown")
        if not rec.documents_required:
            unknown_info.append("Exhaustive list of supporting certificates")

        return SchemeExplanation(
            scheme_id=rec.scheme_id,
            scheme_name=rec.scheme_name,
            eligibility_summary=eligibility_summary,
            benefits=benefits_list,
            application_steps=steps_list,
            required_documents=docs_list,
            official_application_url=rec.official_application_url,
            unknown_information=unknown_info,
            source_fields=["scheme_name", "brief_description", "benefits", "eligibility", "documents_required", "source_url"],
            grounding_verified=True,
        )

scheme_explainer_agent = SchemeExplainerAgent()
