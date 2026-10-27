import time
import json
from typing import Dict, Any, List
from app.schemas.profile import CitizenProfile
from app.orchestration.workflow import workflow_orchestrator
from app.evaluation.metrics import compute_percentiles

TEST_PROFILES = [
    CitizenProfile(age=35, annual_income=180000, state="Tamil Nadu", occupation="farmer", gender="Male"),
    CitizenProfile(age=21, annual_income=120000, state="Gujarat", occupation="student", social_category="ST"),
    CitizenProfile(age=42, annual_income=240000, state="Uttarakhand", occupation="artisan", gender="Female"),
    CitizenProfile(age=28, annual_income=90000, state="Puducherry", occupation="construction_worker", disability=False),
    CitizenProfile(age=55, annual_income=150000, state="Madhya Pradesh", occupation="farmer", marital_status="married"),
    CitizenProfile(age=32, annual_income=220000, state="Rajasthan", occupation="unemployed", gender="Female", marital_status="widow"),
    CitizenProfile(age=19, annual_income=80000, state="Tamil Nadu", occupation="student", social_category="SC"),
    CitizenProfile(age=48, annual_income=300000, state="Goa", occupation="self_employed", gender="Male"),
    CitizenProfile(age=26, annual_income=140000, state="Haryana", occupation="farmer", gender="Female"),
    CitizenProfile(age=62, annual_income=60000, state="Bihar", occupation="unemployed", disability=True),
]

def benchmark_latencies(runs: int = 10) -> Dict[str, Any]:
    print(f"Running latency benchmark across {runs} test scenarios...")
    a1_times = []
    a2_times = []
    a3_times = []
    a4_times = []
    total_times = []

    for i in range(runs):
        profile = TEST_PROFILES[i % len(TEST_PROFILES)]
        session_id = f"bench-latency-{i}"
        msg = f"I am a {profile.age} year old {profile.occupation} from {profile.state} with annual income {profile.annual_income}."
        
        resp = workflow_orchestrator.run(
            session_id=session_id,
            user_message=msg,
            target_language="en",
            direct_profile_override=profile
        )
        lats = resp.meta.get("latencies", {})
        a1_times.append(lats.get("agent_1_profile_collector_ms", 0.0))
        a2_times.append(lats.get("agent_2_eligibility_matcher_ms", 0.0))
        a3_times.append(lats.get("agent_3_scheme_explainer_ms", 0.0))
        a4_times.append(lats.get("agent_4_language_simplifier_ms", 0.0))
        total_times.append(lats.get("total_pipeline_ms", 0.0))

    results = {
        "runs": runs,
        "profile_collector_ms": compute_percentiles(a1_times),
        "eligibility_matcher_ms": compute_percentiles(a2_times),
        "scheme_explainer_ms": compute_percentiles(a3_times),
        "language_simplifier_ms": compute_percentiles(a4_times),
        "overall_pipeline_ms": compute_percentiles(total_times),
    }

    print("\n" + "=" * 65)
    print(" BenefitBridge AI — Agent-Wise Execution Latency Benchmark")
    print("=" * 65)
    print(f"{'Component':<32} | {'Mean (ms)':<10} | {'Median (ms)':<10} | {'P95 (ms)':<10}")
    print("-" * 65)
    print(f"{'Profile Collector Agent':<32} | {results['profile_collector_ms']['mean']:<10.2f} | {results['profile_collector_ms']['median']:<10.2f} | {results['profile_collector_ms']['p95']:<10.2f}")
    print(f"{'Eligibility Matcher Agent':<32} | {results['eligibility_matcher_ms']['mean']:<10.2f} | {results['eligibility_matcher_ms']['median']:<10.2f} | {results['eligibility_matcher_ms']['p95']:<10.2f}")
    print(f"{'Scheme Explainer Agent':<32} | {results['scheme_explainer_ms']['mean']:<10.2f} | {results['scheme_explainer_ms']['median']:<10.2f} | {results['scheme_explainer_ms']['p95']:<10.2f}")
    print(f"{'Language Simplifier Agent':<32} | {results['language_simplifier_ms']['mean']:<10.2f} | {results['language_simplifier_ms']['median']:<10.2f} | {results['language_simplifier_ms']['p95']:<10.2f}")
    print("-" * 65)
    print(f"{'Total Pipeline Response':<32} | {results['overall_pipeline_ms']['mean']:<10.2f} | {results['overall_pipeline_ms']['median']:<10.2f} | {results['overall_pipeline_ms']['p95']:<10.2f}")
    print("=" * 65)

    return results

if __name__ == "__main__":
    benchmark_latencies()
