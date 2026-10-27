import json
import time
from typing import List, Dict, Any, Set
from app.schemas.profile import CitizenProfile
from app.data.csv_loader import loader
from app.agents.eligibility_matcher import eligibility_matcher_agent
from app.evaluation.metrics import calculate_prf, precision_at_k

# Explicitly verified test scenarios reflecting real schemes in dataset
EVALUATION_SCENARIOS = [
    {
        "id": "scenario-1",
        "description": "Smallholder Farmer in Tamil Nadu seeking agricultural support",
        "profile": CitizenProfile(
            age=38,
            annual_income=150000,
            state="Tamil Nadu",
            occupation="farmer",
            gender="Male",
            social_category="OBC"
        ),
        "expected_categories": ["Agriculture,Rural & Environment", "Social welfare & Empowerment"],
        "mandatory_checks": {"state": "pass", "occupation": "pass"},
    },
    {
        "id": "scenario-2",
        "description": "ST Student in Gujarat seeking higher education / scholarship support",
        "profile": CitizenProfile(
            age=20,
            annual_income=120000,
            state="Gujarat",
            occupation="student",
            gender="Male",
            social_category="ST"
        ),
        "expected_categories": ["Education & Learning", "Social welfare & Empowerment"],
        "mandatory_checks": {"state": "pass", "social_category": "pass"},
    },
    {
        "id": "scenario-3",
        "description": "Construction Worker in Andhra Pradesh seeking welfare/skill stipend",
        "profile": CitizenProfile(
            age=29,
            annual_income=90000,
            state="Andhra Pradesh",
            occupation="construction_worker",
            gender="Male"
        ),
        "expected_categories": ["Social welfare & Empowerment", "Skills & Employment"],
        "mandatory_checks": {"state": "pass", "occupation": "pass"},
    },
    {
        "id": "scenario-4",
        "description": "Widow in Uttarakhand seeking social security assistance",
        "profile": CitizenProfile(
            age=45,
            annual_income=60000,
            state="Uttarakhand",
            occupation="unemployed",
            gender="Female",
            marital_status="widow"
        ),
        "expected_categories": ["Social welfare & Empowerment", "Health & Wellness"],
        "mandatory_checks": {"state": "pass", "gender": "pass"},
    },
    {
        "id": "scenario-5",
        "description": "Handloom Weaver / Artisan in Gujarat seeking yarn/craft subsidy",
        "profile": CitizenProfile(
            age=42,
            annual_income=110000,
            state="Gujarat",
            occupation="artisan",
            gender="Female"
        ),
        "expected_categories": ["Business & Entrepreneurship", "Social welfare & Empowerment"],
        "mandatory_checks": {"state": "pass", "occupation": "pass"},
    },
    {
        "id": "scenario-6",
        "description": "High-income applicant (Rs. 15,00,000) checking strict income-capped welfare",
        "profile": CitizenProfile(
            age=36,
            annual_income=1500000,
            state="Gujarat",
            occupation="salaried",
            gender="Male"
        ),
        "expected_categories": [],
        "mandatory_checks": {"income": "fail_expected_on_capped"},
    },
]

def run_evaluation() -> Dict[str, Any]:
    print("=" * 65)
    print(" BenefitBridge AI — Comprehensive System Evaluation Benchmark")
    print("=" * 65)
    loader.load_schemes()

    total_scenarios = len(EVALUATION_SCENARIOS)
    precision_scores = []
    recall_scores = []
    f1_scores = []
    correct_eligibility_matches = 0
    false_positives = 0
    total_evaluated_recs = 0

    detailed_results = []

    for sc in EVALUATION_SCENARIOS:
        prof = sc["profile"]
        res = eligibility_matcher_agent.match(prof, top_k=5, include_ineligible=True)
        recs = res.recommendations

        # Check eligibility correctness
        is_high_income_test = (prof.annual_income and prof.annual_income > 1000000)
        scenario_passes = True

        for r in recs:
            total_evaluated_recs += 1
            # If high income test, ensure income-capped schemes do not pass as eligible
            if is_high_income_test:
                inc_crit = next((c for c in r.criteria_results if c.criterion == "income"), None)
                if inc_crit and inc_crit.status == "pass":
                    false_positives += 1
                    scenario_passes = False

            # If specific state test, ensure other state specific schemes fail
            st_crit = next((c for c in r.criteria_results if c.criterion == "state"), None)
            if st_crit and st_crit.status == "fail" and r.eligibility_status == "eligible_based_on_available_rules":
                false_positives += 1
                scenario_passes = False

        if scenario_passes:
            correct_eligibility_matches += 1

        # Check category relevance alignment
        expected_cats = set(sc["expected_categories"])
        if expected_cats:
            matched_cat_count = 0
            for r in recs:
                if any(c in expected_cats for c in r.categories):
                    matched_cat_count += 1
            prec = matched_cat_count / max(1, len(recs))
            rec_rate = min(1.0, matched_cat_count / 3.0)  # expect at least 3 relevant candidates
            f1 = (2 * prec * rec_rate) / (prec + rec_rate) if (prec + rec_rate) > 0 else 0.0
            precision_scores.append(prec)
            recall_scores.append(rec_rate)
            f1_scores.append(f1)

        detailed_results.append({
            "scenario_id": sc["id"],
            "description": sc["description"],
            "matched_schemes_count": len(recs),
            "top_scheme": recs[0].scheme_name if recs else None,
            "top_score": recs[0].match_score if recs else 0.0,
            "top_status": recs[0].eligibility_status if recs else None,
        })

    avg_accuracy = round((correct_eligibility_matches / total_scenarios) * 100, 2)
    avg_precision = round((sum(precision_scores) / max(1, len(precision_scores))) * 100, 2)
    avg_recall = round((sum(recall_scores) / max(1, len(recall_scores))) * 100, 2)
    avg_f1 = round((sum(f1_scores) / max(1, len(f1_scores))) * 100, 2)
    fp_rate = round((false_positives / max(1, total_evaluated_recs)) * 100, 2)

    summary = {
        "total_test_scenarios": total_scenarios,
        "eligibility_accuracy_pct": avg_accuracy,
        "recommendation_precision_pct": avg_precision,
        "recommendation_recall_pct": avg_recall,
        "f1_score_pct": avg_f1,
        "false_positive_rate_pct": fp_rate,
        "detailed_scenarios": detailed_results,
    }

    print("\nBenchmark Evaluation Results:")
    print("-" * 50)
    print(f"Eligibility Accuracy:         {avg_accuracy}%")
    print(f"Recommendation Precision:     {avg_precision}%")
    print(f"Recommendation Recall:        {avg_recall}%")
    print(f"F1-Score:                     {avg_f1}%")
    print(f"False Positive Rate:          {fp_rate}%")
    print("-" * 50)

    # Save to JSON
    with open("evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("Machine-readable results written to evaluation_results.json\n")

    return summary

if __name__ == "__main__":
    run_evaluation()
