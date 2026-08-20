"""
Grounded RAG Prompt Strategy & Multilingual Fallback Message Registry (Phase 8)

Provides system prompts with strict grounding instructions, boundary isolation for untrusted context data,
and localized fallback/safety messages across 14 Indic languages plus English.
"""

from typing import Dict

SYSTEM_GROUNDING_PROMPT = """Factual AI assistant for HH Goa Voice RAG.
RULES:
1. Answer using ONLY facts inside <untrusted_retrieved_context_data>.
2. Do NOT use outside knowledge or unverified claims.
3. If context is insufficient or missing, state context does not contain sufficient information.
4. Output a concise, clear grounded answer (1-3 sentences) in {target_language}. Translate facts into {target_language} if retrieved context is in another language.

{context_blocks}"""

# Localized fallback responses for insufficient context / ungrounded claims
INSUFFICIENT_CONTEXT_FALLBACK: Dict[str, str] = {
    "en": "The provided context does not contain sufficient information to answer this question.",
    "hi": "प्रदान किए गए संदर्भ में इस प्रश्न का उत्तर देने के लिए पर्याप्त जानकारी उपलब्ध नहीं है।",
    "mr": "प्रदान केलेल्या संदर्भात या प्रश्नाचे उत्तर देण्यासाठी पुरेशी माहिती उपलब्ध नाही.",
    "bn": "প্রদত্ত প্রসঙ্গে এই প্রশ্নের উত্তর দেওয়ার জন্য পর্যাপ্ত তথ্য নেই।",
    "ta": "வழங்கப்பட்ட சூழலில் இந்த கேள்விக்கு பதிலளிக்க போதிய தகவல்கள் இல்லை.",
    "te": "అందించిన సందర్భంలో ఈ ప్రశ్నకు సమాధానం ఇవ్వడానికి తగినంత సమాచారం లేదు.",
    "ur": "فراہم کردہ سیاق و سباق میں اس سوال کا جواب دینے کے لیے کافی معلومات موجود نہیں ہیں۔",
    "gu": "આપેલ સંદર્ભમાં આ પ્રશ્નનો જવાબ આપવા માટે પૂરતી માહિતી નથી.",
    "kn": "ನೀಡಿರುವ ಸಂದರ್ಭದಲ್ಲಿ ಈ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರಿಸಲು ಸಾಲಾದ ಮಾಹಿತಿ ಇಲ್ಲ.",
    "ml": "നൽകിയിട്ടുള്ള സന്ദർഭത്തിൽ ഈ ചോദ്യത്തിന് ഉത്തരം നൽകാൻ ആവശ്യമായ വിവരങ്ങൾ ലഭ്യമല്ല.",
    "ne": "प्रदान गरिएको सन्दर्भमा यस प्रश्नको उत्तर दिन पर्याप्त जानकारी उपलब्ध छैन।",
    "or": "ପ୍ରଦତ୍ତ ସନ୍ଦର୍ଭରେ ଏହି ପ୍ରଶ୍ନର ଉତ୍ତର ଦେବା ପାଇଁ ପର୍ଯ୍ୟାପ୍ତ ସୂଚନା ନାହିଁ।",
    "pa": "ਦਿੱਤੇ ਗਏ ਸੰਦਰਭ ਵਿੱਚ ਇਸ ਸਵਾਲ ਦਾ ਜਵਾਬ ਦੇਣ ਲਈ ਕਾਫੀ ਜਾਣਕਾਰੀ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।",
    "sa": "प्रदत्ते सन्दर्भे अस्य प्रश्नस्य उत्तरदानाय पर्याप्तं सूचना नास्ति।",
    "as": "প্ৰদত্ত প্ৰসংগত এই প্ৰশ্নৰ উত্তৰ দিবলৈ পৰ্যাপ্ত তথ্য নাই।",
}

# Localized safety rejection responses for malicious or unsafe queries
SAFETY_REJECTION_FALLBACK: Dict[str, str] = {
    "en": "Your request could not be processed as it violates safety guidelines.",
    "hi": "सुरक्षा दिशानिर्देशों के उल्लंघन के कारण आपका अनुरोध संसाधित नहीं किया जा सका।",
    "mr": "सुरक्षा मार्गदर्शक तत्त्वांचे उल्लंघन केल्यामुळे तुमची विनंती प्रक्रिया केली जाऊ शकली नाही.",
    "bn": "সুরক্ষা নির্দেশিকা লঙ্ঘনের কারণে আপনার অনুরোধ প্রক্রিয়া করা যায়নি।",
    "ta": "பாதுகாப்பு வழிகாட்டுதல்களை மீறியதால் உங்கள் கோரிக்கையை செயலாக்க முடியவில்லை.",
    "te": "రక్షణ మార్గదర్శకాలను ఉల్లంఘించినందున మీ అభ్యర్థన ప్రాసెస్ చేయబడలేదు.",
    "ur": "حفاظتی رہنما خطوط کی خلاف ورزی की وجہ سے آپ کی درخواست پر عمل نہیں کیا جا سکا۔",
}


def get_insufficient_context_message(lang_code: str) -> str:
    """Returns localized insufficient evidence message based on ISO or FLORES language code."""
    if not lang_code:
        return INSUFFICIENT_CONTEXT_FALLBACK["en"]

    clean_code = lang_code.strip().lower()

    for key, msg in INSUFFICIENT_CONTEXT_FALLBACK.items():
        if clean_code.startswith(key) or key in clean_code:
            return msg

    return INSUFFICIENT_CONTEXT_FALLBACK["en"]


def get_safety_rejection_message(lang_code: str) -> str:
    """Returns localized safety rejection message based on ISO or FLORES language code."""
    if not lang_code:
        return SAFETY_REJECTION_FALLBACK["en"]

    clean_code = lang_code.strip().lower()

    for key, msg in SAFETY_REJECTION_FALLBACK.items():
        if clean_code.startswith(key) or key in clean_code:
            return msg

    return SAFETY_REJECTION_FALLBACK["en"]
