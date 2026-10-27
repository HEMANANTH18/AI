import json
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.agent_outputs import SchemeExplanation, SimplifiedSchemeOutput

SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native": "English"},
    "ta": {"name": "Tamil", "native": "தமிழ்"},
    "hi": {"name": "Hindi", "native": "हिन्दी"},
    "te": {"name": "Telugu", "native": "తెలుగు"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ"},
    "ml": {"name": "Malayalam", "native": "മലയാളം"},
    "bn": {"name": "Bengali", "native": "বাংলা"},
    "mr": {"name": "Marathi", "native": "मराठी"},
}

LOCALIZED_CAUTIONS = {
    "en": "Note: Official approval and exact disbursement depend upon verification by the competent government authority.",
    "ta": "குறிப்பு: இறுதி தகுதி மற்றும் பயன் ஒப்புதல் அரசு அதிகாரிகளின் ஆவண சரிபார்ப்புக்கு உட்பட்டது.",
    "hi": "नोट: आधिकारिक स्वीकृति और लाभ वितरण संबंधित सरकारी विभाग के सत्यापन पर निर्भर करता है।",
    "te": "గమనిక: అధికారిక ఆమోదం మరియు ప్రయోజనాల పంపిణీ సంబంధిత ప్రభుత్వ అధికారుల ధృవీకరణపై ఆధారపడి ఉంటుంది.",
    "kn": "ಸೂಚನೆ: ಅಧಿಕೃತ ಅನುಮೋದನೆ ಮತ್ತು ಸೌಲಭ್ಯ ವಿತರಣೆಯು ಸಂಬಂಧಿತ ಸರ್ಕಾರಿ ಪ್ರಾಧಿಕಾರದ ಪರಿಶೀಲನೆಗೆ ಒಳಪಟ್ಟಿರುತ್ತದೆ.",
    "ml": "കുറിപ്പ്: ഔദ്യോഗിക അംഗീകാരവും ആനുകൂല്യ വിതരണവും ബന്ധപ്പെട്ട സർക്കാർ അധികാരികളുടെ പരിശോധനയ്ക്ക് വിധേയമാണ്.",
    "bn": "দ্রষ্টব্য: সরকারী অনুমোদন এবং সুবিধা প্রদান সংশ্লিষ্ট সরকারী কর্তৃপক্ষের যাচাইকরণের উপর নির্ভর করে।",
    "mr": "टीप: अधिकृत मान्यता आणि लाभ वाटप संबंधित सरकारी प्राधिकरणाच्या पडताळणीवर अवलंबून आहे.",
}

LOCALIZED_TERMS = {
    "ta": {
        "Aadhaar Card": "ஆதார் அட்டை (Aadhaar Card)",
        "Aadhaar": "ஆதார் அட்டை (Aadhaar)",
        "Income Certificate": "வருமானச் சான்றிதழ் (Income Certificate)",
        "Community Certificate": "சாதிச் சான்றிதழ் (Community Certificate)",
        "Caste Certificate": "சாதிச் சான்றிதழ் (Caste Certificate)",
        "Ration Card": "குடும்ப அட்டை (Ration Card)",
        "Bank Account Details": "வங்கி கணக்கு விவரங்கள் (Bank Details)",
        "Bank Account": "வங்கி கணக்கு (Bank Account)",
        "Passport size photo": "பாஸ்போர்ட் அளவு புகைப்படம் (Passport Photo)",
        "Identity proof": "அடையாள அட்டை (ID Proof)",
        "Medical report": "மருத்துவ அறிக்கை (Medical Report)",
        "Land ownership": "நில உரிமை ஆவணங்கள் (Land Documents)",
        "Direct Benefit Transfer": "நேரடி பணப் பரிமாற்றம் (DBT)",
        "Scholarship": "கல்வி உதவித்தொகை (Scholarship)",
        "Monthly Pension": "மாதாந்திர ஓய்வூதியம் (Monthly Pension)",
        "Pension": "ஓய்வூதியம் (Pension)",
        "Financial grant": "நிதி உதவி மானியம் (Financial Grant)",
        "Status: Eligible based on available rules.": "நிலை: விதிமுறைகளின்படி தகுதி உறுதி செய்யப்பட்டது.",
        "Status: Potentially eligible.": "நிலை: சாத்தியமான தகுதி (ஆவண சரிபார்ப்பு தேவை).",
        "Applicable pan-India as a Central welfare program.": "மத்திய அரசின் திட்டமாக இந்தியா முழுவதும் பொருந்தும்.",
        "Tailored for farmers.": "விவசாயிகளுக்கான பிரத்யேக நலத்திட்டம்.",
        "Tailored for students.": "மாணவர்களுக்கான பிரத்யேக நலத்திட்டம்.",
        "Income satisfies welfare threshold": "வருமானம் நலத்திட்ட வரம்பிற்குள் உள்ளது",
    },
    "hi": {
        "Aadhaar Card": "आधार कार्ड (Aadhaar Card)",
        "Aadhaar": "आधार कार्ड (Aadhaar)",
        "Income Certificate": "आय प्रमाण पत्र (Income Certificate)",
        "Community Certificate": "जाति प्रमाण पत्र (Caste Certificate)",
        "Caste Certificate": "जाति प्रमाण पत्र (Caste Certificate)",
        "Ration Card": "राशन कार्ड (Ration Card)",
        "Bank Account Details": "बैंक खाता विवरण (Bank Details)",
        "Bank Account": "बैंक खाता (Bank Account)",
        "Passport size photo": "पासपोर्ट साइज फोटो (Passport Photo)",
        "Identity proof": "पहचान प्रमाण (ID Proof)",
        "Medical report": "चिकित्सा रिपोर्ट (Medical Report)",
        "Land ownership": "भूमि स्वामित्व दस्तावेज (Land Documents)",
        "Direct Benefit Transfer": "प्रत्यक्ष लाभ अंतरण (DBT)",
        "Scholarship": "छात्रवृत्ति (Scholarship)",
        "Monthly Pension": "मासिक पेंशन (Monthly Pension)",
        "Pension": "पेंशन (Pension)",
        "Financial grant": "वित्तीय अनुदान (Financial Grant)",
        "Status: Eligible based on available rules.": "स्थिति: उपलब्ध नियमों के अनुसार पात्रता सुनिश्चित।",
        "Status: Potentially eligible.": "स्थिति: संभावित रूप से पात्र (सत्यापन आवश्यक)।",
        "Applicable pan-India as a Central welfare program.": "केंद्रीय कल्याण योजना के रूप में पूरे भारत में लागू।",
        "Tailored for farmers.": "किसानों के लिए विशेष कल्याणकारी योजना।",
        "Tailored for students.": "छात्रों के लिए विशेष कल्याणकारी योजना।",
        "Income satisfies welfare threshold": "वार्षिक आय कल्याणकारी सीमा के अंतर्गत है",
    },
    "te": {
        "Aadhaar Card": "ఆధార్ కార్డు (Aadhaar Card)",
        "Income Certificate": "ఆదాయ ధృవీకరణ పత్రం (Income Certificate)",
        "Community Certificate": "కుల ధృవీకరణ పత్రం (Caste Certificate)",
        "Ration Card": "రేషన్ కార్డు (Ration Card)",
        "Bank Account Details": "బ్యాంకు ఖాతా వివరాలు (Bank Details)",
        "Scholarship": "ఉపకార వేతనం (Scholarship)",
        "Pension": "పింఛను (Pension)",
        "Status: Eligible based on available rules.": "స్థితి: నిబంధనల ప్రకారం అర్హత నిర్ధారించబడింది.",
        "Status: Potentially eligible.": "స్థితి: సంభావ్య అర్హత (ధృవీకరణ అవసరం).",
        "Applicable pan-India as a Central welfare program.": "కేంద్ర సంక్షేమ పథకంగా భారతదేశం అంతటా వర్తిస్తుంది.",
    },
    "kn": {
        "Aadhaar Card": "ಆಧಾರ್ ಕಾರ್ಡ್ (Aadhaar Card)",
        "Income Certificate": "ಆದಾಯ ಪ್ರಮಾಣಪತ್ರ (Income Certificate)",
        "Community Certificate": "ಜಾತಿ ಪ್ರಮಾಣಪತ್ರ (Caste Certificate)",
        "Ration Card": "ರೇಷನ್ ಕಾರ್ಡ್ (Ration Card)",
        "Bank Account Details": "ಬ್ಯಾಂಕ್ ಖಾತೆ ವಿವರಗಳು (Bank Details)",
        "Scholarship": "ವಿದ್ಯಾರ್ಥಿವೇತನ (Scholarship)",
        "Pension": "ಪಿಂಚಣಿ (Pension)",
        "Status: Eligible based on available rules.": "ಸ್ಥಿತಿ: ಲಭ್ಯವಿರುವ ನಿಯಮಗಳ ಪ್ರಕಾರ ಅರ್ಹತೆ ದೃಢಪಟ್ಟಿದೆ.",
        "Status: Potentially eligible.": "ಸ್ಥಿತಿ: ಸಂಭಾವ್ಯ ಅರ್ಹತೆ (ಪರಿಶೀಲನೆ ಅಗತ್ಯವಿದೆ).",
        "Applicable pan-India as a Central welfare program.": "ಕೇಂದ್ರ ಕಲ್ಯಾಣ ಯೋಜನೆಯಾಗಿ ಭಾರತದಾದ್ಯಂತ ಅನ್ವಯಿಸುತ್ತದೆ.",
    },
}

def translate_phrase(text: str, lang_code: str) -> str:
    if not text or lang_code not in LOCALIZED_TERMS:
        return text
    terms = LOCALIZED_TERMS[lang_code]
    res = text
    for eng, local in terms.items():
        if eng in res:
            res = res.replace(eng, local)
    return res

class LanguageSimplifierAgent:
    """Agent 4: Plain Language Simplifier & Multilingual Localizer."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client = None

    def _get_client(self):
        if not self._client and self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai client in simplifier: {e}")
                self._client = None
        return self._client

    def simplify(
        self,
        explanation: SchemeExplanation,
        target_language: str = "en"
    ) -> SimplifiedSchemeOutput:
        """Translates and simplifies a verified scheme explanation."""
        lang_code = target_language.lower()
        if lang_code not in SUPPORTED_LANGUAGES:
            lang_code = "en"

        caution_text = LOCALIZED_CAUTIONS.get(lang_code, LOCALIZED_CAUTIONS["en"])

        # If English and no translation needed, return clean English explanation
        if lang_code == "en":
            return SimplifiedSchemeOutput(
                language="en",
                scheme_id=explanation.scheme_id,
                localized_scheme_name=explanation.scheme_name,
                simple_explanation=explanation.eligibility_summary,
                benefits=explanation.benefits,
                eligibility_summary=explanation.eligibility_summary,
                application_steps=explanation.application_steps,
                required_documents=explanation.required_documents,
                official_application_url=explanation.official_application_url,
                important_cautions=[caution_text],
                is_fallback=False,
            )

        # 1. Try Gemini Multilingual Translation
        client = self._get_client()
        if client:
            try:
                res = self._simplify_with_gemini(client, explanation, lang_code)
                if res:
                    return res
            except Exception as e:
                logger.warning(f"Multilingual Gemini call failed for {lang_code}: {e}. Falling back to rule-based localization.")

        # 2. Deterministic Fallback Localization
        return self._simplify_fallback(explanation, lang_code, caution_text)

    def _simplify_with_gemini(
        self,
        client: Any,
        explanation: SchemeExplanation,
        lang_code: str
    ) -> Optional[SimplifiedSchemeOutput]:
        target_name = SUPPORTED_LANGUAGES[lang_code]["name"]
        native_name = SUPPORTED_LANGUAGES[lang_code]["native"]

        prompt = f"""You are the BenefitBridge AI Language Simplifier Agent.
Translate and simplify the following verified welfare scheme details into clear, accessible, citizen-friendly {target_name} ({native_name}).

RULES:
1. Preserve all numeric values, eligibility conditions, and facts accurately.
2. Keep the official scheme name or transliterate appropriately alongside the English name.
3. Keep the official application URL completely unchanged.
4. Use everyday, respectful, citizen-friendly language avoiding bureaucratic jargon.
5. Return strictly valid JSON:
{{
  "language": "{lang_code}",
  "scheme_id": "{explanation.scheme_id}",
  "localized_scheme_name": "{explanation.scheme_name}",
  "simple_explanation": "summary in {target_name}",
  "benefits": ["benefit in {target_name}"],
  "eligibility_summary": "eligibility summary in {target_name}",
  "application_steps": ["step in {target_name}"],
  "required_documents": ["document in {target_name}"],
  "official_application_url": "{explanation.official_application_url or ''}",
  "important_cautions": ["disclaimer in {target_name}"]
}}

FACTUAL CONTENT TO SIMPLIFY:
Scheme Name: {explanation.scheme_name}
Summary: {explanation.eligibility_summary}
Benefits: {json.dumps(explanation.benefits)}
Steps: {json.dumps(explanation.application_steps)}
Documents: {json.dumps(explanation.required_documents)}
URL: {explanation.official_application_url}
"""
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        if response and response.text:
            cleaned = response.text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            return SimplifiedSchemeOutput(
                language=lang_code,
                scheme_id=explanation.scheme_id,
                localized_scheme_name=data.get("localized_scheme_name", explanation.scheme_name),
                simple_explanation=data.get("simple_explanation", explanation.eligibility_summary),
                benefits=data.get("benefits", explanation.benefits),
                eligibility_summary=data.get("eligibility_summary", explanation.eligibility_summary),
                application_steps=data.get("application_steps", explanation.application_steps),
                required_documents=data.get("required_documents", explanation.required_documents),
                official_application_url=explanation.official_application_url,
                important_cautions=data.get("important_cautions", [LOCALIZED_CAUTIONS.get(lang_code, "")]),
                is_fallback=False,
            )
        return None

    def _simplify_fallback(
        self,
        explanation: SchemeExplanation,
        lang_code: str,
        caution: str
    ) -> SimplifiedSchemeOutput:
        """Fallback providing structured output when Gemini is offline."""
        translated_summary = translate_phrase(explanation.eligibility_summary, lang_code)
        translated_benefits = [translate_phrase(b, lang_code) for b in explanation.benefits]
        translated_docs = [translate_phrase(d, lang_code) for d in explanation.required_documents]
        translated_steps = [translate_phrase(s, lang_code) for s in explanation.application_steps]

        return SimplifiedSchemeOutput(
            language=lang_code,
            scheme_id=explanation.scheme_id,
            localized_scheme_name=explanation.scheme_name,
            simple_explanation=translated_summary,
            benefits=translated_benefits,
            eligibility_summary=translated_summary,
            application_steps=translated_steps,
            required_documents=translated_docs,
            official_application_url=explanation.official_application_url,
            important_cautions=[caution],
            is_fallback=True,
        )

language_simplifier_agent = LanguageSimplifierAgent()
