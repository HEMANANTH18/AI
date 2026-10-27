import re
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.profile import CitizenProfile, ProfileExtractionResult

STATE_SYNONYMS = {
    "tn": "Tamil Nadu",
    "tamilnadu": "Tamil Nadu",
    "tamil nadu": "Tamil Nadu",
    "gujarat": "Gujarat",
    "gj": "Gujarat",
    "uttarakhand": "Uttarakhand",
    "uk": "Uttarakhand",
    "mp": "Madhya Pradesh",
    "madhya pradesh": "Madhya Pradesh",
    "up": "Uttar Pradesh",
    "uttar pradesh": "Uttar Pradesh",
    "mh": "Maharashtra",
    "maharashtra": "Maharashtra",
    "ap": "Andhra Pradesh",
    "andhra pradesh": "Andhra Pradesh",
    "andhra": "Andhra Pradesh",
    "telangana": "Telangana",
    "ts": "Telangana",
    "karnataka": "Karnataka",
    "ka": "Karnataka",
    "kerala": "Kerala",
    "kl": "Kerala",
    "rajasthan": "Rajasthan",
    "rj": "Rajasthan",
    "bihar": "Bihar",
    "br": "Bihar",
    "west bengal": "West Bengal",
    "wb": "West Bengal",
    "puducherry": "Puducherry",
    "py": "Puducherry",
    "pondicherry": "Puducherry",
    "goa": "Goa",
    "haryana": "Haryana",
    "hr": "Haryana",
    "punjab": "Punjab",
    "pb": "Punjab",
    "delhi": "Delhi",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "assam": "Assam",
}

OCCUPATION_SYNONYMS = {
    "farmer": "farmer",
    "agriculture": "farmer",
    "kisan": "farmer",
    "cultivator": "farmer",
    "farming": "farmer",
    "student": "student",
    "studying": "student",
    "scholar": "student",
    "unemployed": "unemployed",
    "job seeker": "unemployed",
    "construction worker": "construction_worker",
    "builder": "construction_worker",
    "mason": "construction_worker",
    "artisan": "artisan",
    "weaver": "artisan",
    "handloom": "artisan",
    "craftsman": "artisan",
    "self employed": "self_employed",
    "business": "self_employed",
    "shopkeeper": "self_employed",
    "salaried": "salaried",
    "private job": "salaried",
    "govt job": "salaried",
}

class ProfileCollectorAgent:
    """Agent 1: Conversational Profile Collector and Validator."""

    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY

    def process_turn(
        self,
        user_message: str,
        current_profile: Optional[CitizenProfile] = None
    ) -> ProfileExtractionResult:
        """Processes user message, updates profile state, validates, and asks targeted questions."""
        profile = current_profile.model_copy() if current_profile else CitizenProfile()
        text = user_message.strip()
        lower_text = text.lower()
        extracted: Dict[str, Any] = {}

        # 1. Stated query/intent
        if not profile.query_text and len(text) > 10:
            profile.query_text = text

        # 2. Age extraction
        age_match = re.search(r'\b(?:i am|i\'m|age(?: is)?|am)?\s*(\d{1,2})\s*(?:years old|yrs old|years|yrs)?\b', lower_text)
        if age_match:
            try:
                candidate_age = int(age_match.group(1))
                if 1 <= candidate_age <= 120 and candidate_age != 0:
                    profile.age = candidate_age
                    extracted["age"] = candidate_age
            except ValueError:
                pass

        # 3. Income extraction
        # e.g., "income 200000", "2 lakh", "2.5 lakhs", "1,50,000", "50k"
        lakh_match = re.search(r'(?:income\s*(?:is)?\s*)?(?:rs\.?|inr|₹)?\s*([0-9\.]+)\s*(?:lakh|lacs|lac|l)', lower_text)
        k_match = re.search(r'(?:income\s*(?:is)?\s*)?(?:rs\.?|inr|₹)?\s*([0-9\.]+)\s*k\b', lower_text)
        raw_income_match = re.search(r'(?:income\s*(?:is)?\s*)?(?:rs\.?|inr|₹)?\s*([0-9,]{5,7})\b', lower_text)

        if lakh_match:
            try:
                val = float(lakh_match.group(1)) * 100000.0
                profile.annual_income = val
                extracted["annual_income"] = val
            except ValueError:
                pass
        elif k_match:
            try:
                val = float(k_match.group(1)) * 1000.0
                profile.annual_income = val
                extracted["annual_income"] = val
            except ValueError:
                pass
        elif raw_income_match:
            try:
                val = float(raw_income_match.group(1).replace(',', ''))
                profile.annual_income = val
                extracted["annual_income"] = val
            except ValueError:
                pass

        # Check household vs individual income
        if "household" in lower_text or "family" in lower_text:
            profile.income_type = "household"
            extracted["income_type"] = "household"

        # 4. State extraction
        for kw, canonical_state in STATE_SYNONYMS.items():
            pattern = rf'\b{re.escape(kw)}\b'
            if re.search(pattern, lower_text):
                profile.state = canonical_state
                extracted["state"] = canonical_state
                break

        # 5. Occupation extraction
        for kw, canonical_occ in OCCUPATION_SYNONYMS.items():
            pattern = rf'\b{re.escape(kw)}\b'
            if re.search(pattern, lower_text):
                profile.occupation = canonical_occ
                extracted["occupation"] = canonical_occ
                break

        # 6. Gender extraction
        if re.search(r'\b(female|woman|girl|lady)\b', lower_text):
            profile.gender = "Female"
            extracted["gender"] = "Female"
        elif re.search(r'\b(male|man|boy|gentleman)\b', lower_text):
            profile.gender = "Male"
            extracted["gender"] = "Male"
        elif re.search(r'\b(transgender|trans)\b', lower_text):
            profile.gender = "Transgender"
            extracted["gender"] = "Transgender"

        # 7. Social Category / Caste extraction
        if re.search(r'\b(sc|scheduled caste)\b', lower_text):
            profile.social_category = "SC"
            extracted["social_category"] = "SC"
        elif re.search(r'\b(st|scheduled tribe)\b', lower_text):
            profile.social_category = "ST"
            extracted["social_category"] = "ST"
        elif re.search(r'\b(obc|other backward class|bc)\b', lower_text):
            profile.social_category = "OBC"
            extracted["social_category"] = "OBC"
        elif re.search(r'\b(minority|muslim|christian|sikh|jain|buddhist)\b', lower_text):
            profile.social_category = "Minority"
            extracted["social_category"] = "Minority"
        elif re.search(r'\b(general|oc|open category)\b', lower_text):
            profile.social_category = "General"
            extracted["social_category"] = "General"

        # 8. Education extraction
        if re.search(r'\b(post graduate|pg|master|mtech|mba|msc)\b', lower_text):
            profile.education = "post_graduate"
            extracted["education"] = "post_graduate"
        elif re.search(r'\b(graduate|college|degree|btech|bba|bsc|ba|bcom)\b', lower_text):
            profile.education = "graduate"
            extracted["education"] = "graduate"
        elif re.search(r'\b(12th|hsc|higher secondary|intermediate)\b', lower_text):
            profile.education = "higher_secondary"
            extracted["education"] = "higher_secondary"
        elif re.search(r'\b(10th|sslc|secondary|school)\b', lower_text):
            profile.education = "secondary"
            extracted["education"] = "secondary"

        # 9. Disability
        if re.search(r'\b(physically challenged|disabled|disability|divyang|handicapped)\b', lower_text):
            profile.disability = True
            extracted["disability"] = True
        elif re.search(r'\b(no disability|not disabled|none)\b', lower_text) and profile.disability is None:
            profile.disability = False
            extracted["disability"] = False

        # 10. Marital status
        if re.search(r'\b(widow|widower)\b', lower_text):
            profile.marital_status = "widow"
            extracted["marital_status"] = "widow"
        elif re.search(r'\b(married)\b', lower_text):
            profile.marital_status = "married"
            extracted["marital_status"] = "married"
        elif re.search(r'\b(single|unmarried)\b', lower_text):
            profile.marital_status = "single"
            extracted["marital_status"] = "single"

        # Check missing priority fields
        missing = []
        if profile.state is None:
            missing.append("state")
        if profile.age is None:
            missing.append("age")
        if profile.occupation is None:
            missing.append("occupation")
        if profile.annual_income is None:
            missing.append("annual_income")

        # Determine next clarification question
        question: Optional[str] = None
        suggested_options: Optional[List[str]] = None
        next_field: Optional[str] = None
        ack: Optional[str] = None

        if extracted:
            ack = "Thank you! I've recorded your " + ", ".join(extracted.keys()) + "."

        if "state" in missing:
            next_field = "state"
            question = "Which Indian State or Union Territory do you permanently reside in?"
            suggested_options = ["Tamil Nadu", "Gujarat", "Madhya Pradesh", "Uttarakhand", "Puducherry", "Rajasthan"]
        elif "occupation" in missing:
            next_field = "occupation"
            question = "What is your primary occupation or current status?"
            suggested_options = ["Farmer", "Student", "Construction Worker", "Self Employed", "Unemployed", "Salaried"]
        elif "age" in missing:
            next_field = "age"
            question = "Could you please specify your age in years?"
            suggested_options = ["18-25", "26-35", "36-50", "51-60", "60+"]
        elif "annual_income" in missing:
            next_field = "annual_income"
            question = "What is your approximate annual household or individual income (in INR)?"
            suggested_options = ["Under ₹1,00,000", "₹1,00,000 - ₹2,50,000", "₹2,50,000 - ₹5,00,000", "Above ₹5,00,000"]
        elif profile.gender is None:
            next_field = "gender"
            question = "What is your gender? (Certain welfare schemes have dedicated provisions for women, widows, or transgender citizens)."
            suggested_options = ["Male", "Female", "Transgender", "Prefer not to say"]
        elif profile.social_category is None:
            next_field = "social_category"
            question = "Which social category do you belong to? (Many state/central educational and welfare grants are category-specific)."
            suggested_options = ["General", "OBC", "SC", "ST", "Minority"]

        # Profile is considered sufficiently complete when state, occupation, age, and income are known
        is_complete = (profile.state is not None and profile.occupation is not None and profile.age is not None and profile.annual_income is not None)

        return ProfileExtractionResult(
            profile=profile,
            extracted_fields=extracted,
            missing_fields=missing,
            clarification_question=question,
            suggested_options=suggested_options,
            profile_complete=is_complete,
            next_recommended_field=next_field,
            acknowledgement_text=ack,
        )

profile_collector_agent = ProfileCollectorAgent()
