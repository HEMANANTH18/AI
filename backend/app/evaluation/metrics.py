import math
from typing import List, Dict, Any, Set

def calculate_prf(
    retrieved_ids: List[str],
    relevant_ids: Set[str]
) -> Dict[str, float]:
    """Computes Precision, Recall, and F1-score for a single retrieval/recommendation result."""
    if not retrieved_ids:
        precision = 0.0
    else:
        relevant_retrieved = sum(1 for rid in retrieved_ids if rid in relevant_ids)
        precision = relevant_retrieved / len(retrieved_ids)

    if not relevant_ids:
        recall = 1.0 if not retrieved_ids else 0.0
    else:
        relevant_retrieved = sum(1 for rid in retrieved_ids if rid in relevant_ids)
        recall = relevant_retrieved / len(relevant_ids)

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = (2 * precision * recall) / (precision + recall)

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }

def precision_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    return sum(1 for rid in top_k if rid in relevant_ids) / len(top_k)

def compute_percentiles(values: List[float]) -> Dict[str, float]:
    """Calculates mean, median, and p95 latency."""
    if not values:
        return {"mean": 0.0, "median": 0.0, "p95": 0.0}
    sorted_v = sorted(values)
    n = len(sorted_v)
    mean_val = sum(sorted_v) / n
    median_val = sorted_v[n // 2]
    p95_idx = min(n - 1, math.ceil(0.95 * n) - 1)
    p95_val = sorted_v[p95_idx]
    return {
        "mean": round(mean_val, 2),
        "median": round(median_val, 2),
        "p95": round(p95_val, 2),
    }
