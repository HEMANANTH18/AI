import re
from typing import List, Dict, Any
from urllib.parse import urlparse
from app.schemas.scheme import Scheme

def validate_url(url: str) -> bool:
    """Check if the URL has a valid http/https scheme and network location."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False

def assess_data_quality(schemes: List[Scheme]) -> Dict[str, Any]:
    """Run data quality diagnostics over the normalized scheme collection."""
    total = len(schemes)
    if total == 0:
        return {"status": "empty", "total_records": 0}

    valid_urls = sum(1 for s in schemes if validate_url(s.source_url))
    missing_benefits = sum(1 for s in schemes if not s.benefits)
    missing_docs = sum(1 for s in schemes if not s.documents_required)
    missing_steps = sum(1 for s in schemes if not s.application_steps)
    schemes_with_age = sum(1 for s in schemes if s.parsed_criteria.min_age or s.parsed_criteria.max_age)
    schemes_with_income = sum(1 for s in schemes if s.parsed_criteria.max_income)
    central_schemes = sum(1 for s in schemes if s.parsed_criteria.is_central)

    slug_set = set()
    duplicates = 0
    for s in schemes:
        if s.id in slug_set:
            duplicates += 1
        slug_set.add(s.id)

    return {
        "status": "healthy",
        "total_records": total,
        "unique_schemes": len(slug_set),
        "duplicate_slugs": duplicates,
        "central_schemes": central_schemes,
        "state_schemes": total - central_schemes,
        "valid_source_urls_count": valid_urls,
        "valid_source_urls_pct": round((valid_urls / total) * 100, 2),
        "schemes_with_benefits_pct": round(((total - missing_benefits) / total) * 100, 2),
        "schemes_with_docs_pct": round(((total - missing_docs) / total) * 100, 2),
        "schemes_with_steps_pct": round(((total - missing_steps) / total) * 100, 2),
        "schemes_with_structured_age_criteria": schemes_with_age,
        "schemes_with_structured_income_criteria": schemes_with_income,
    }
