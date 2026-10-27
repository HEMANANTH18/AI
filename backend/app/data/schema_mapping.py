import re
import html
from typing import List, Optional, Tuple, Dict, Any
from app.schemas.scheme import ParsedCriteria

def clean_text(text: Optional[str]) -> str:
    """Unescape HTML entities, normalize whitespaces, and clean text."""
    if not text or not isinstance(text, str):
        return ""
    text = html.unescape(text)
    # Normalize common non-standard whitespace / quotes
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def split_items(text: Optional[str], delimiters: str = ";|•") -> List[str]:
    """Split semi-structured strings into distinct non-empty items."""
    if not text or not isinstance(text, str):
        return []
    cleaned = clean_text(text)
    pattern = f"[{re.escape(delimiters)}]"
    parts = re.split(pattern, cleaned)
    items = []
    for p in parts:
        p_clean = p.strip()
        # Remove leading dashes or bullets
        p_clean = re.sub(r'^[-\*\d\.\)]+\s*', '', p_clean).strip()
        if p_clean and len(p_clean) > 2:
            items.append(p_clean)
    return items

def extract_criteria_from_text(eligibility_text: str, level: str, state: Optional[str]) -> ParsedCriteria:
    """
    Conservative, deterministic rule-based extractor for structured eligibility criteria
    from raw eligibility text and geographic metadata.
    """
    criteria = ParsedCriteria()
    text = clean_text(eligibility_text).lower()

    # Central vs State
    if str(level).strip().lower() == "central":
        criteria.is_central = True
        criteria.allowed_states = ["all india"]
    elif state and isinstance(state, str) and state.strip():
        clean_state = state.strip()
        criteria.allowed_states = [clean_state]
        criteria.is_central = False
    else:
        criteria.is_central = True
        criteria.allowed_states = ["all india"]

    # 1. Age extraction
    # Patterns like "between 18 and 60 years", "age of 18 to 35", "above 18 years", "at least 21 years", "up to 40 years"
    between_match = re.search(r'(?:between|age\s*(?:limit\s*)?(?:of)?)\s*(\d{1,2})\s*(?:and|to|-)\s*(\d{1,2})\s*(?:years|yrs)?', text)
    if between_match:
        try:
            a, b = int(between_match.group(1)), int(between_match.group(2))
            criteria.min_age = min(a, b)
            criteria.max_age = max(a, b)
        except ValueError:
            pass

    if criteria.min_age is None:
        min_match = re.search(r'(?:above|at\s*least|minimum\s*age\s*(?:of)?|completed)\s*(\d{1,2})\s*(?:years|yrs)?', text)
        if min_match:
            try:
                criteria.min_age = int(min_match.group(1))
            except ValueError:
                pass

    if criteria.max_age is None:
        max_match = re.search(r'(?:up\s*to|maximum\s*age\s*(?:of)?|below|not\s*exceeding)\s*(\d{1,2})\s*(?:years|yrs)?', text)
        if max_match:
            try:
                criteria.max_age = int(max_match.group(1))
            except ValueError:
                pass

    # 2. Income extraction (e.g., "income less than 2,00,000", "income up to 2.5 lakh", "not exceed Rs. 1,00,000")
    lakh_match = re.search(r'(?:income\s*(?:should\s*not\s*exceed|below|less\s*than|up\s*to)?\s*(?:rs\.?|inr|₹)?\s*([0-9\.]+)\s*lakh)', text)
    if lakh_match:
        try:
            val = float(lakh_match.group(1))
            criteria.max_income = val * 100000.0
        except ValueError:
            pass
    elif "below poverty line" in text or "bpl" in text:
        # Common national threshold proxy: ~1.2 Lakh
        criteria.max_income = 120000.0
    else:
        num_income_match = re.search(r'(?:income\s*(?:should\s*not\s*exceed|below|less\s*than|up\s*to)?\s*(?:rs\.?|inr|₹)?\s*([0-9,]{5,7}))', text)
        if num_income_match:
            try:
                raw_num = num_income_match.group(1).replace(',', '')
                val = float(raw_num)
                if 20000 <= val <= 2500000:
                    criteria.max_income = val
            except ValueError:
                pass

    # 3. Gender extraction
    has_women = bool(re.search(r'\b(women|woman|female|girl|widow|mother)\b', text))
    has_men_only = bool(re.search(r'\b(only\s*male|men\s*only)\b', text))
    if has_women and not has_men_only:
        # Check if restricted to women
        if re.search(r'\b(only\s*for\s*(?:women|girls|females)|applicable\s*to\s*women|women\s*beneficiar|pregnant|lactating)\b', text):
            criteria.allowed_genders = ["female"]
    if has_men_only:
        criteria.allowed_genders = ["male"]

    if "widow" in text:
        criteria.requires_widow = True

    # 4. Social Category / Caste extraction
    cats = []
    if re.search(r'\b(scheduled\s*caste|sc\b)', text):
        cats.append("SC")
    if re.search(r'\b(scheduled\s*tribe|st\b)', text):
        cats.append("ST")
    if re.search(r'\b(other\s*backward|obc\b)', text):
        cats.append("OBC")
    if re.search(r'\b(minority|minorities)\b', text):
        cats.append("Minority")
    if re.search(r'\b(general\s*category)\b', text):
        cats.append("General")
    criteria.allowed_categories = cats

    # 5. Occupations
    occs = []
    if re.search(r'\b(farmer|agriculture|cultivator|kisan)\b', text):
        occs.append("farmer")
    if re.search(r'\b(student|scholarship|school|college|studying|undergraduate|postgraduate)\b', text):
        occs.append("student")
    if re.search(r'\b(construction\s*worker|building\s*and\s*other\s*construction)\b', text):
        occs.append("construction_worker")
    if re.search(r'\b(artisan|weaver|handloom|craftsman)\b', text):
        occs.append("artisan")
    if re.search(r'\b(entrepreneur|startup|business|micro\s*enterprise|msme)\b', text):
        occs.append("entrepreneur")
    if re.search(r'\b(unemployed|job\s*seeker)\b', text):
        occs.append("unemployed")
    criteria.target_occupations = occs

    # 6. Disability
    if re.search(r'\b(person\s*with\s*disabilit|physically\s*handicapped|divyang|disability\s*of\s*at\s*least|locomotor)\b', text):
        criteria.requires_disability = True

    return criteria
