"""
Unit Tests for Groq Single-Provider Execution & Cooldown Circuit-Breaker
"""

import time
import pytest
from unittest.mock import MagicMock
from app.models.generation import AskRequest, GroundingStatus
from app.rag.generator import GeneratorService
from app.rag.llm.base import BaseLLMProvider


class MockGroqFailureProvider(BaseLLMProvider):
    """Mock Groq provider that simulates HTTP 429 rate limit error."""
    def generate(self, prompt: str, system_instruction: str = None) -> str:
        raise RuntimeError("AI service is temporarily rate-limited. Please try again shortly.")


def test_groq_success():
    """Test 1: Groq success -> provider_used = 'groq', model = 'llama-3.1-8b-instant'."""
    GeneratorService._groq_cooldown_until = 0.0
    mock_groq = MagicMock(spec=BaseLLMProvider)
    mock_groq.__class__.__name__ = "GroqLLMProvider"
    mock_groq.model_name = "llama-3.1-8b-instant"
    mock_groq.generate.return_value = "निगम एक कंपनी या लोगों का समूह है जो एक एकल इकाई के रूप में कार्य करता है।"

    service = GeneratorService(llm_provider=mock_groq)
    req = AskRequest(query="निगम क्या है?", top_k=3, score_threshold=0.0, preferred_answer_language="hi")
    resp = service.generate_answer(req)

    assert resp.groq_attempted is True
    assert resp.groq_success is True
    assert resp.provider_used == "groq"
    assert resp.model_used == "llama-3.1-8b-instant"
    mock_groq.generate.assert_called_once()


def test_groq_429_service_busy():
    """Test 2: Groq 429 -> cooldown set, automatic failover to Gemini."""
    GeneratorService._groq_cooldown_until = 0.0
    mock_groq = MockGroqFailureProvider()

    service = GeneratorService(llm_provider=mock_groq)
    req = AskRequest(query="What is a corporation?", top_k=3, score_threshold=0.0)
    resp = service.generate_answer(req)

    assert resp.groq_attempted is True
    assert resp.groq_success is False
    assert resp.groq_error_type == "RATE_LIMITED"
    # When Groq rate limits, pipeline automatically fails over to Gemini
    assert resp.provider_used in ["gemini", "none"]
    assert GeneratorService._groq_cooldown_until > time.time()


def test_groq_cooldown_active_skips_groq():
    """Test 3: Groq cooldown active -> Groq skipped immediately, failover to Gemini."""
    GeneratorService._groq_cooldown_until = time.time() + 300.0
    mock_groq = MagicMock(spec=BaseLLMProvider)
    mock_groq.__class__.__name__ = "GroqLLMProvider"
    mock_groq.model_name = "llama-3.1-8b-instant"
    mock_groq.generate.return_value = "निगम एक कंपनी है।"

    service = GeneratorService(llm_provider=mock_groq)
    req = AskRequest(query="निगम क्या है?", top_k=3, score_threshold=0.0, preferred_answer_language="hi")
    resp = service.generate_answer(req)

    assert resp.groq_attempted is True
    assert resp.groq_error_type == "COOLDOWN_ACTIVE"
    mock_groq.generate.assert_not_called()

    # Reset cooldown after test
    GeneratorService._groq_cooldown_until = 0.0


def test_no_context_groq_not_called():
    """Test 4: NO_CONTEXT -> Groq not called."""
    GeneratorService._groq_cooldown_until = 0.0
    mock_groq = MagicMock(spec=BaseLLMProvider)

    service = GeneratorService(llm_provider=mock_groq)
    req = AskRequest(query="What is my personal bank account balance?", top_k=3, score_threshold=0.99)
    resp = service.generate_answer(req)

    assert resp.grounding_status in [GroundingStatus.NO_CONTEXT, GroundingStatus.LOW_CONFIDENCE]
    assert resp.sources == []
    assert resp.provider_used == "none"
    assert resp.groq_attempted is False
    mock_groq.generate.assert_not_called()


def test_unsafe_query_groq_not_called():
    """Test 5: UNSAFE_QUERY -> Groq not called."""
    GeneratorService._groq_cooldown_until = 0.0
    mock_groq = MagicMock(spec=BaseLLMProvider)

    service = GeneratorService(llm_provider=mock_groq)
    req = AskRequest(query="how to make explosives", top_k=3)
    resp = service.generate_answer(req)

    assert resp.grounding_status == GroundingStatus.UNSAFE_QUERY
    assert resp.provider_used == "none"
    assert resp.groq_attempted is False
    mock_groq.generate.assert_not_called()
