"""
Unit tests for Sarvam Speech-to-Text (STT) Service and FastAPI /transcribe endpoint (Phase 7)
"""

from fastapi.testclient import TestClient
from app.main import app
from app.services.stt import SpeechToTextService, SARVAM_LANG_MAP

client = TestClient(app)


def test_stt_language_code_mapping():
    """Verifies ISO/FLORES language code to Sarvam BCP-47 identifier mapping."""
    assert SARVAM_LANG_MAP["en"] == "en-IN"
    assert SARVAM_LANG_MAP["hi"] == "hi-IN"
    assert SARVAM_LANG_MAP["mr"] == "mr-IN"
    assert SARVAM_LANG_MAP["bn"] == "bn-IN"
    assert SARVAM_LANG_MAP["ta"] == "ta-IN"


def test_stt_service_empty_audio_handling():
    """Verifies STT service gracefully handles empty or invalid audio recording bytes."""
    service = SpeechToTextService()
    resp = service.transcribe_audio(b"short", language_code="hi")
    assert resp.success is False
    assert "empty or too short" in resp.error_message.lower()
    assert resp.stt_latency_ms >= 0.0


def test_stt_service_fallback_when_unauthenticated():
    """Verifies STT service returns clean unauthenticated error when Sarvam API key is unset."""
    service = SpeechToTextService(api_key="")
    mock_audio = b"RIFF" + b"\x00" * 200
    resp = service.transcribe_audio(mock_audio, language_code="en")
    assert resp.success is False
    assert "not configured" in resp.error_message.lower()
    assert resp.stt_latency_ms >= 0.0


def test_api_transcribe_endpoint_valid_audio():
    """Verifies POST /transcribe endpoint processes uploaded audio files."""
    dummy_wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00" + b"\x00" * 300
    files = {"file": ("test_speech.wav", dummy_wav_header, "audio/wav")}
    data = {"language": "hi"}

    response = client.post("/transcribe", files=files, data=data)
    assert response.status_code == 200
    json_data = response.json()
    assert "transcript" in json_data
    assert "stt_latency_ms" in json_data
    assert "success" in json_data
