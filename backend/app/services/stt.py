"""
Sarvam Speech-to-Text (STT) Service Integration (Phase 7)

Provides server-side audio transcription via Sarvam API (saaras:v1 / saarika:v2)
supporting English and 14 Indic target languages with latency measurement.
"""

import os
import time
from typing import Optional
import httpx

from app.core.config import get_settings
from app.models.stt import TranscribeResponse
from app.rag.retrieval import normalize_supported_language

SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"

OFFICIALLY_SUPPORTED_LANGUAGES = {"en", "hi", "mr", "gu"}

# Language code mapping to Sarvam BCP-47 identifiers (Officially supported: en, hi, mr, gu)
SARVAM_LANG_MAP = {
    "en": "en-IN",
    "hi": "hi-IN",
    "mr": "mr-IN",
    "gu": "gu-IN",
    "bn": "bn-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "pa": "pa-IN",
    "or": "od-IN",
    "ur": "ur-IN",
    "as": "as-IN",
    "ne": "ne-IN"
}


class SpeechToTextService:
    """Sarvam Speech-to-Text service abstraction handling audio transcription and latency measurement."""

    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = settings.sarvam_api_key or os.getenv("SARVAM_API_KEY")

    def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "recording.webm",
        language_code: Optional[str] = "en"
    ) -> TranscribeResponse:
        """
        Transcribes audio binary data using Sarvam STT REST API.

        :param audio_bytes: Raw audio byte content from client recording
        :param filename: Filename with extension (e.g. 'speech.webm', 'speech.wav')
        :param language_code: ISO/FLORES language code preference
        :return: TranscribeResponse object containing transcript and latency instrumentation
        """
        start_time = time.perf_counter()

        norm_code = normalize_supported_language(language_code, default="en")

        if not audio_bytes or len(audio_bytes) < 100:
            return TranscribeResponse(
                transcript="",
                language_code=norm_code,
                stt_latency_ms=round((time.perf_counter() - start_time) * 1000.0, 2),
                success=False,
                error_message="Audio recording is empty or too short."
            )

        sarvam_lang = SARVAM_LANG_MAP.get(norm_code, "en-IN")

        if not self.api_key:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return TranscribeResponse(
                transcript="",
                language_code=sarvam_lang,
                stt_latency_ms=round(latency_ms, 2),
                success=False,
                error_message="Sarvam STT API key not configured in .env."
            )

        headers = {
            "api-subscription-key": self.api_key
        }

        files = {
            "file": (filename, audio_bytes, "audio/webm")
        }

        data = {
            "model": "saarika:v2.5",
            "language_code": sarvam_lang
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(SARVAM_STT_URL, headers=headers, files=files, data=data)
                latency_ms = (time.perf_counter() - start_time) * 1000.0

                if response.status_code == 200:
                    resp_json = response.json()
                    transcript_text = resp_json.get("transcript", "").strip()
                    detected_lang = resp_json.get("language_code", sarvam_lang)

                    if not transcript_text:
                        return TranscribeResponse(
                            transcript="",
                            language_code=detected_lang,
                            stt_latency_ms=round(latency_ms, 2),
                            success=False,
                            error_message="No clear speech detected in recording."
                        )

                    return TranscribeResponse(
                        transcript=transcript_text,
                        language_code=detected_lang,
                        stt_latency_ms=round(latency_ms, 2),
                        success=True
                    )
                else:
                    err_msg = f"Sarvam STT API returned HTTP {response.status_code}: {response.text[:200]}"
                    return TranscribeResponse(
                        transcript="",
                        language_code=sarvam_lang,
                        stt_latency_ms=round(latency_ms, 2),
                        success=False,
                        error_message=err_msg
                    )
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return TranscribeResponse(
                transcript="",
                language_code=sarvam_lang,
                stt_latency_ms=round(latency_ms, 2),
                success=False,
                error_message=f"Sarvam STT connection error: {e}"
            )
