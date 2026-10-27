import time
from typing import List, Dict, Any
from app.data.csv_loader import loader
from app.schemas.profile import CitizenProfile
from app.retrieval.hybrid_retriever import hybrid_retriever
from app.evaluation.metrics import precision_at_k

QUERIES = [
    {
        "intent": "PM Kisan Samman Nidhi agricultural cash transfer",
        "profile": CitizenProfile(occupation="farmer", state="Tamil Nadu", query_text="farmer direct cash income support"),
        "expected_terms": ["kisan", "farmer", "agriculture", "land"]
    },
    {
        "intent": "Post-matric scholarship for scheduled caste students",
        "profile": CitizenProfile(occupation="student", social_category="SC", state="Gujarat", query_text="post matric scholarship higher education"),
        "expected_terms": ["scholarship", "student", "education", "matric"]
    },
    {
        "intent": "Emergency medical ambulance service 108",
        "profile": CitizenProfile(state="Uttarakhand", query_text="emergency medical ambulance hospital patient transport 108"),
        "expected_terms": ["108", "ambulance", "emergency", "health", "medical"]
    },
    {
        "intent": "Handloom weaver yarn subsidy",
        "profile": CitizenProfile(occupation="artisan", state="Andhra Pradesh", query_text="handloom weaver yarn subsidy APCO"),
        "expected_terms": ["handloom", "weaver", "yarn", "artisan"]
    }
]

def benchmark_retrieval():
    print("=" * 65)
    print(" BenefitBridge AI — Retrieval Benchmark (Precision@k & Coverage)")
    print("=" * 65)
    loader.load_schemes()

    top_3_hits = []
    top_5_hits = []
    latencies = []

    for item in QUERIES:
        prof = item["profile"]
        expected = [t.lower() for t in item["expected_terms"]]

        t0 = time.perf_counter()
        candidates = hybrid_retriever.retrieve(prof, top_k=5)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed_ms)

        # Check term recall in top candidates
        top_3_text = " ".join([c[0].name.lower() + " " + c[0].brief_description.lower() for c in candidates[:3]])
        top_5_text = " ".join([c[0].name.lower() + " " + c[0].brief_description.lower() for c in candidates[:5]])

        p3 = sum(1 for t in expected if t in top_3_text) / len(expected)
        p5 = sum(1 for t in expected if t in top_5_text) / len(expected)

        top_3_hits.append(p3)
        top_5_hits.append(p5)

        print(f"Query Intent: '{item['intent']}'")
        print(f"  Latency: {elapsed_ms:.1f}ms | Precision@3: {p3*100:.1f}% | Precision@5: {p5*100:.1f}%")
        print(f"  Top Match: {candidates[0][0].name} (Score: {candidates[0][1]:.3f})\n")

    avg_p3 = (sum(top_3_hits) / len(top_3_hits)) * 100
    avg_p5 = (sum(top_5_hits) / len(top_5_hits)) * 100
    avg_lat = sum(latencies) / len(latencies)

    print("-" * 65)
    print(f"Average Retrieval Latency: {avg_lat:.2f} ms")
    print(f"Average Top-3 Keyword Hit Rate: {avg_p3:.1f}%")
    print(f"Average Top-5 Keyword Hit Rate: {avg_p5:.1f}%")
    print("=" * 65)

if __name__ == "__main__":
    benchmark_retrieval()
