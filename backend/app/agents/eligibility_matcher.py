from typing import List, Dict, Any, Tuple, Optional
from app.schemas.profile import CitizenProfile
from app.schemas.scheme import Scheme
from app.schemas.agent_outputs import (
    CriterionResult,
    SchemeRecommendation,
    EligibilityMatcherOutput,
)
from app.retrieval.hybrid_retriever import hybrid_retriever
from app.core.logging_config import logger

class EligibilityMatcherAgent:
    """Agent 2: Hybrid RAG Eligibility Matcher & Recommendation Scorer."""

    def __init__(self):
        self.retriever = hybrid_retriever

    def evaluate_scheme(
        self,
        scheme: Scheme,
        profile: CitizenProfile,
        semantic_score: float = 0.5
    ) -> SchemeRecommendation:
        """Evaluates explicit deterministic rules against citizen profile and computes match score."""
        criteria_results: List[CriterionResult] = []
        matched_reasons: List[str] = []
        unmet_conditions: List[str] = []
        unknown_conditions: List[str] = []

        parsed = scheme.parsed_criteria

        # 1. State Evaluation
        if parsed.is_central or scheme.level.lower() == "central" or (scheme.state and "all india" in scheme.state.lower()):
            criteria_results.append(CriterionResult(
                criterion="state",
                status="pass",
                reason="Central government scheme applicable across all Indian States and Union Territories.",
                source_text=f"Level: {scheme.level}"
            ))
            matched_reasons.append("Applicable pan-India as a Central welfare program.")
        elif profile.state and scheme.state:
            user_st = profile.state.strip().lower()
            sch_st = scheme.state.strip().lower()
            if user_st in sch_st or sch_st in user_st:
                criteria_results.append(CriterionResult(
                    criterion="state",
                    status="pass",
                    reason=f"Resident of applicable state: {scheme.state}.",
                    source_text=f"State: {scheme.state}"
                ))
                matched_reasons.append(f"Specifically enacted for residents of {scheme.state}.")
            else:
                criteria_results.append(CriterionResult(
                    criterion="state",
                    status="fail",
                    reason=f"Scheme is designated for {scheme.state}, but citizen resides in {profile.state}.",
                    source_text=f"State: {scheme.state}"
                ))
                unmet_conditions.append(f"Restricted to residents of {scheme.state}.")
        elif not profile.state and scheme.state:
            criteria_results.append(CriterionResult(
                criterion="state",
                status="unknown",
                reason=f"Requires residency in {scheme.state}, citizen state not specified.",
                source_text=f"State: {scheme.state}"
            ))
            unknown_conditions.append(f"Residency requirement in {scheme.state} requires verification.")
        else:
            criteria_results.append(CriterionResult(
                criterion="state",
                status="not_applicable",
                reason="No specific state restriction documented."
            ))

        # 2. Age Evaluation
        if parsed.min_age is not None or parsed.max_age is not None:
            if profile.age is not None:
                min_pass = (parsed.min_age is None or profile.age >= parsed.min_age)
                max_pass = (parsed.max_age is None or profile.age <= parsed.max_age)
                if min_pass and max_pass:
                    reason_str = f"Citizen age {profile.age} is within required range "
                    if parsed.min_age and parsed.max_age:
                        reason_str += f"({parsed.min_age} - {parsed.max_age} years)."
                    elif parsed.min_age:
                        reason_str += f"(minimum {parsed.min_age} years)."
                    else:
                        reason_str += f"(up to {parsed.max_age} years)."
                    criteria_results.append(CriterionResult(
                        criterion="age",
                        status="pass",
                        reason=reason_str,
                        source_text=scheme.eligibility_text[:120]
                    ))
                    matched_reasons.append(reason_str)
                else:
                    fail_str = f"Citizen age {profile.age} outside eligible boundary "
                    if parsed.min_age and profile.age < parsed.min_age:
                        fail_str += f"(requires at least {parsed.min_age} years)."
                    if parsed.max_age and profile.age > parsed.max_age:
                        fail_str += f"(requires age up to {parsed.max_age} years)."
                    criteria_results.append(CriterionResult(
                        criterion="age",
                        status="fail",
                        reason=fail_str,
                        source_text=scheme.eligibility_text[:120]
                    ))
                    unmet_conditions.append(fail_str)
            else:
                criteria_results.append(CriterionResult(
                    criterion="age",
                    status="unknown",
                    reason="Age limits specified in scheme, but citizen age is unverified.",
                    source_text=scheme.eligibility_text[:120]
                ))
                unknown_conditions.append("Specific age criteria must be verified against birth record.")
        else:
            criteria_results.append(CriterionResult(
                criterion="age",
                status="not_applicable",
                reason="No explicit age limit stated in scheme rules."
            ))

        # 3. Income Evaluation
        if parsed.max_income is not None:
            if profile.annual_income is not None:
                if profile.annual_income <= parsed.max_income:
                    criteria_results.append(CriterionResult(
                        criterion="income",
                        status="pass",
                        reason=f"Annual income ₹{profile.annual_income:,.0f} satisfies income ceiling (₹{parsed.max_income:,.0f}).",
                        source_text=scheme.eligibility_text[:120]
                    ))
                    matched_reasons.append(f"Income satisfies welfare threshold of ₹{parsed.max_income:,.0f}.")
                else:
                    criteria_results.append(CriterionResult(
                        criterion="income",
                        status="fail",
                        reason=f"Annual income ₹{profile.annual_income:,.0f} exceeds maximum threshold of ₹{parsed.max_income:,.0f}.",
                        source_text=scheme.eligibility_text[:120]
                    ))
                    unmet_conditions.append(f"Income exceeds prescribed ceiling of ₹{parsed.max_income:,.0f}.")
            else:
                criteria_results.append(CriterionResult(
                    criterion="income",
                    status="unknown",
                    reason=f"Scheme has income threshold of ₹{parsed.max_income:,.0f}, but citizen income was not provided.",
                    source_text=scheme.eligibility_text[:120]
                ))
                unknown_conditions.append(f"Income eligibility (cap of ₹{parsed.max_income:,.0f}) is unverified.")
        else:
            criteria_results.append(CriterionResult(
                criterion="income",
                status="not_applicable",
                reason="No explicit income ceiling mentioned."
            ))

        # 4. Gender Evaluation
        if parsed.allowed_genders:
            if profile.gender:
                if profile.gender.lower() in [g.lower() for g in parsed.allowed_genders]:
                    criteria_results.append(CriterionResult(
                        criterion="gender",
                        status="pass",
                        reason=f"Citizen gender matches targeted beneficiary group ({', '.join(parsed.allowed_genders)}).",
                        source_text=scheme.eligibility_text[:120]
                    ))
                    matched_reasons.append(f"Targeted to {', '.join(parsed.allowed_genders)} citizens.")
                else:
                    criteria_results.append(CriterionResult(
                        criterion="gender",
                        status="fail",
                        reason=f"Scheme is designated exclusively for {', '.join(parsed.allowed_genders)}, citizen is {profile.gender}.",
                        source_text=scheme.eligibility_text[:120]
                    ))
                    unmet_conditions.append(f"Designated exclusively for {', '.join(parsed.allowed_genders)} beneficiaries.")
            else:
                criteria_results.append(CriterionResult(
                    criterion="gender",
                    status="unknown",
                    reason=f"Restricted to {', '.join(parsed.allowed_genders)}, citizen gender not recorded.",
                    source_text=scheme.eligibility_text[:120]
                ))
                unknown_conditions.append(f"Gender eligibility ({', '.join(parsed.allowed_genders)}) not provided.")
        else:
            criteria_results.append(CriterionResult(
                criterion="gender",
                status="not_applicable",
                reason="Open to all genders."
            ))

        # 5. Social Category / Caste Evaluation
        if parsed.allowed_categories:
            if profile.social_category:
                if profile.social_category.upper() in [c.upper() for c in parsed.allowed_categories]:
                    criteria_results.append(CriterionResult(
                        criterion="social_category",
                        status="pass",
                        reason=f"Citizen category ({profile.social_category}) is among specified beneficiary categories.",
                        source_text=scheme.eligibility_text[:120]
                    ))
                    matched_reasons.append(f"Beneficiary category aligns with {profile.social_category} targeted support.")
                else:
                    # Category schemes often have specific provisions; mark fail if strictly limited
                    criteria_results.append(CriterionResult(
                        criterion="social_category",
                        status="fail",
                        reason=f"Scheme specifically targets {', '.join(parsed.allowed_categories)}, citizen belongs to {profile.social_category}.",
                        source_text=scheme.eligibility_text[:120]
                    ))
                    unmet_conditions.append(f"Scheme is targeted for {', '.join(parsed.allowed_categories)}.")
            else:
                criteria_results.append(CriterionResult(
                    criterion="social_category",
                    status="unknown",
                    reason=f"Scheme targets {', '.join(parsed.allowed_categories)}, citizen category not given.",
                    source_text=scheme.eligibility_text[:120]
                ))
                unknown_conditions.append(f"Requires verification of social category ({', '.join(parsed.allowed_categories)}).")
        else:
            criteria_results.append(CriterionResult(
                criterion="social_category",
                status="not_applicable",
                reason="Open across social categories."
            ))

        # 6. Occupation Evaluation
        if parsed.target_occupations:
            if profile.occupation:
                occ_norm = profile.occupation.lower()
                if occ_norm in [o.lower() for o in parsed.target_occupations]:
                    criteria_results.append(CriterionResult(
                        criterion="occupation",
                        status="pass",
                        reason=f"Citizen occupation ({profile.occupation}) directly matches targeted sector.",
                        source_text=f"Target: {', '.join(parsed.target_occupations)}"
                    ))
                    matched_reasons.append(f"Tailored for {profile.occupation}s.")
                else:
                    criteria_results.append(CriterionResult(
                        criterion="occupation",
                        status="unknown",
                        reason=f"Scheme emphasizes {', '.join(parsed.target_occupations)}; citizen is {profile.occupation}.",
                        source_text=f"Target: {', '.join(parsed.target_occupations)}"
                    ))
            else:
                criteria_results.append(CriterionResult(
                    criterion="occupation",
                    status="unknown",
                    reason=f"Scheme focuses on {', '.join(parsed.target_occupations)}, citizen occupation not specified."
                ))
        else:
            criteria_results.append(CriterionResult(
                criterion="occupation",
                status="not_applicable",
                reason="General occupation eligibility."
            ))

        # 7. Disability requirement check
        if parsed.requires_disability:
            if profile.disability is True:
                criteria_results.append(CriterionResult(
                    criterion="disability",
                    status="pass",
                    reason="Citizen fulfills disability welfare assistance criterion.",
                    source_text="Requires disability status"
                ))
                matched_reasons.append("Fulfills disability welfare criteria.")
            elif profile.disability is False:
                criteria_results.append(CriterionResult(
                    criterion="disability",
                    status="fail",
                    reason="Scheme requires disability / Divyangjan status, citizen has none.",
                    source_text="Requires disability status"
                ))
                unmet_conditions.append("Requires recognized disability status.")
            else:
                criteria_results.append(CriterionResult(
                    criterion="disability",
                    status="unknown",
                    reason="Scheme requires disability status, citizen status unrecorded."
                ))

        # Determine aggregate eligibility status
        has_failure = any(c.status == "fail" for c in criteria_results)
        passes_count = sum(1 for c in criteria_results if c.status == "pass")
        unknowns_count = sum(1 for c in criteria_results if c.status == "unknown")

        if has_failure:
            eligibility_status = "not_eligible_based_on_known_rules"
        elif passes_count >= 2 and unknowns_count == 0:
            eligibility_status = "eligible_based_on_available_rules"
        elif passes_count >= 1 or (passes_count == 0 and unknowns_count <= 2):
            eligibility_status = "potentially_eligible"
        else:
            eligibility_status = "insufficient_information"

        # Compute Weighted Relevance Score: Score(Si) = \sum w_k f_k(Si, U)
        # Weights: eligibility=0.35, semantic=0.30, state=0.15, occupation=0.10, completeness=0.10 (sum=1.0)
        f_eligibility = 1.0 if eligibility_status == "eligible_based_on_available_rules" else (0.75 if eligibility_status == "potentially_eligible" else (0.4 if eligibility_status == "insufficient_information" else 0.05))
        f_semantic = max(0.0, min(1.0, semantic_score))
        
        # State factor
        state_res = next((c for c in criteria_results if c.criterion == "state"), None)
        f_state = 1.0 if (state_res and state_res.status == "pass") else 0.4
        
        # Occupation factor
        occ_res = next((c for c in criteria_results if c.criterion == "occupation"), None)
        f_occupation = 1.0 if (occ_res and occ_res.status == "pass") else 0.5
        
        # Data completeness factor
        f_completeness = (0.5 if scheme.benefits else 0.0) + (0.3 if scheme.documents_required else 0.0) + (0.2 if scheme.application_steps else 0.0)

        match_score = (
            0.35 * f_eligibility +
            0.30 * f_semantic +
            0.15 * f_state +
            0.10 * f_occupation +
            0.10 * f_completeness
        )

        # Severe penalty if explicit failure occurs
        if has_failure:
            match_score = min(0.35, match_score * 0.4)

        match_score = round(max(0.01, min(0.99, match_score)), 3)

        return SchemeRecommendation(
            scheme_id=scheme.id,
            scheme_name=scheme.name,
            short_title=scheme.short_title,
            level=scheme.level,
            state=scheme.state,
            categories=scheme.categories,
            benefit_type=scheme.benefit_type,
            eligibility_status=eligibility_status,
            match_score=match_score,
            semantic_score=round(float(semantic_score), 3),
            criteria_results=criteria_results,
            matched_reasons=matched_reasons,
            unmet_conditions=unmet_conditions,
            unknown_conditions=unknown_conditions,
            brief_description=scheme.brief_description,
            benefits=scheme.benefits[:5],
            documents_required=scheme.documents_required[:6],
            application_steps=scheme.application_steps[:4],
            official_application_url=scheme.source_url if scheme.source_url.startswith("http") else None,
            source_record={
                "slug": scheme.id,
                "scheme_name": scheme.name,
                "level": scheme.level,
                "state": scheme.state,
                "department": scheme.department,
                "category": ", ".join(scheme.categories),
                "benefit_type": scheme.benefit_type,
            }
        )

    def match(
        self,
        profile: CitizenProfile,
        top_k: int = 10,
        include_ineligible: bool = False
    ) -> EligibilityMatcherOutput:
        """Runs hybrid candidate retrieval, evaluates criteria, and returns ranked recommendations."""
        # Retrieve candidate schemes
        candidates = self.retriever.retrieve(profile, top_k=top_k * 3)
        evaluated: List[SchemeRecommendation] = []
        unmatched_reasons: List[str] = []

        for scheme, sim in candidates:
            rec = self.evaluate_scheme(scheme, profile, semantic_score=sim)
            if not include_ineligible and rec.eligibility_status == "not_eligible_based_on_known_rules":
                unmatched_reasons.append(f"{rec.scheme_name}: {'; '.join(rec.unmet_conditions)}")
                continue
            evaluated.append(rec)

        # Sort recommendations: eligible first, then potentially eligible, ordered by match_score descending
        status_rank = {
            "eligible_based_on_available_rules": 4,
            "potentially_eligible": 3,
            "insufficient_information": 2,
            "not_eligible_based_on_known_rules": 1
        }
        evaluated.sort(key=lambda r: (status_rank.get(r.eligibility_status, 0), r.match_score), reverse=True)

        final_recs = evaluated[:top_k]
        matched_ids = [r.scheme_id for r in final_recs]

        return EligibilityMatcherOutput(
            matched_scheme_ids=matched_ids,
            recommendations=final_recs,
            total_evaluated=len(candidates),
            unmatched_reasons=unmatched_reasons[:5],
            requires_clarification=(len(final_recs) == 0 or (profile.state is None and profile.occupation is None))
        )

eligibility_matcher_agent = EligibilityMatcherAgent()
