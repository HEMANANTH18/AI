import pytest
from app.agents.eligibility_matcher import eligibility_matcher_agent
from app.schemas.profile import CitizenProfile
from app.schemas.scheme import Scheme, ParsedCriteria

def create_mock_scheme(
    scheme_id: str = "test-scheme",
    name: str = "Test Welfare Scheme",
    min_age: int = 18,
    max_age: int = 60,
    max_income: float = 200000.0,
    state: str = "Tamil Nadu",
    is_central: bool = False,
    genders: list = None
) -> Scheme:
    return Scheme(
        id=scheme_id,
        name=name,
        short_title="TWS",
        level="Central" if is_central else "State",
        state=state if not is_central else "All India",
        beneficiary_type="Individual",
        benefit_type="Cash",
        categories=["Social welfare"],
        brief_description="Support for citizens in need.",
        detailed_description="Detailed rules.",
        benefits=["Financial grant of Rs. 10,000"],
        eligibility_text=f"Must reside in {state}. Age {min_age}-{max_age}. Income below {max_income}.",
        application_mode="Online",
        application_steps=["Apply at portal"],
        documents_required=["Aadhaar", "Income Certificate"],
        source_url="https://www.myscheme.gov.in/schemes/test",
        parsed_criteria=ParsedCriteria(
            min_age=min_age,
            max_age=max_age,
            max_income=max_income,
            allowed_states=[state] if not is_central else ["all india"],
            allowed_genders=genders or [],
            is_central=is_central
        ),
        searchable_text="Test scheme search text"
    )

def test_explicit_pass_criteria():
    scheme = create_mock_scheme()
    profile = CitizenProfile(age=30, annual_income=150000, state="Tamil Nadu", occupation="farmer")
    rec = eligibility_matcher_agent.evaluate_scheme(scheme, profile, semantic_score=0.8)

    assert rec.eligibility_status in ["eligible_based_on_available_rules", "potentially_eligible"]
    assert rec.match_score > 0.5
    age_crit = next(c for c in rec.criteria_results if c.criterion == "age")
    assert age_crit.status == "pass"
    inc_crit = next(c for c in rec.criteria_results if c.criterion == "income")
    assert inc_crit.status == "pass"

def test_income_boundary_failure():
    scheme = create_mock_scheme(max_income=200000.0)
    profile = CitizenProfile(age=30, annual_income=350000, state="Tamil Nadu")
    rec = eligibility_matcher_agent.evaluate_scheme(scheme, profile, semantic_score=0.95)

    assert rec.eligibility_status == "not_eligible_based_on_known_rules"
    inc_crit = next(c for c in rec.criteria_results if c.criterion == "income")
    assert inc_crit.status == "fail"
    # Ensure high semantic similarity does NOT override deterministic failure
    assert rec.match_score < 0.40

def test_state_mismatch_failure():
    scheme = create_mock_scheme(state="Gujarat", is_central=False)
    profile = CitizenProfile(age=25, annual_income=100000, state="Tamil Nadu")
    rec = eligibility_matcher_agent.evaluate_scheme(scheme, profile)

    assert rec.eligibility_status == "not_eligible_based_on_known_rules"
    st_crit = next(c for c in rec.criteria_results if c.criterion == "state")
    assert st_crit.status == "fail"

def test_central_scheme_passes_all_states():
    scheme = create_mock_scheme(is_central=True)
    profile = CitizenProfile(age=35, annual_income=120000, state="Kerala")
    rec = eligibility_matcher_agent.evaluate_scheme(scheme, profile)

    st_crit = next(c for c in rec.criteria_results if c.criterion == "state")
    assert st_crit.status == "pass"
