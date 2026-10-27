import pytest
from app.agents.scheme_explainer import scheme_explainer_agent
from app.agents.language_simplifier import language_simplifier_agent, SUPPORTED_LANGUAGES
from app.schemas.agent_outputs import SchemeRecommendation

def test_scheme_explainer_grounded_fallback():
    rec = SchemeRecommendation(
        scheme_id="pm-kisan-test",
        scheme_name="PM Kisan Samman Nidhi",
        level="Central",
        state="All India",
        categories=["Agriculture"],
        eligibility_status="eligible_based_on_available_rules",
        match_score=0.92,
        brief_description="Direct income support of Rs 6000 per year for farmer families.",
        benefits=["Rs 6000 per year in 3 installments of Rs 2000 each."],
        documents_required=["Aadhaar Card", "Land ownership documents"],
        application_steps=["Register on PM-KISAN portal"],
        official_application_url="https://pmkisan.gov.in",
    )
    exp = scheme_explainer_agent.explain(rec)
    assert exp.scheme_id == "pm-kisan-test"
    assert exp.grounding_verified is True
    assert len(exp.benefits) > 0
    assert "pmkisan.gov.in" in exp.official_application_url

def test_language_simplifier_tamil_and_english():
    rec = SchemeRecommendation(
        scheme_id="test-1",
        scheme_name="Emergency Assistance",
        level="State",
        state="Tamil Nadu",
        eligibility_status="potentially_eligible",
        match_score=0.75,
        brief_description="Free ambulance and medical assistance.",
        benefits=["Ambulance transportation"],
        documents_required=["Identity proof"],
        application_steps=["Call 108"],
        official_application_url="https://example.gov.in",
    )
    exp = scheme_explainer_agent.explain(rec)

    # English
    en_res = language_simplifier_agent.simplify(exp, target_language="en")
    assert en_res.language == "en"
    assert en_res.official_application_url == "https://example.gov.in"

    # Tamil
    ta_res = language_simplifier_agent.simplify(exp, target_language="ta")
    assert ta_res.language == "ta"
    assert len(ta_res.important_cautions) > 0
    # Must preserve official URL exactly
    assert ta_res.official_application_url == "https://example.gov.in"
