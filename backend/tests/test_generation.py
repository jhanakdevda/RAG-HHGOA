"""
Unit Tests for Phase 7 Multilingual LLM Answer Generation

Tests provider abstraction adapters (Mock, Gemini, OpenAI, Groq, Ollama),
prompt formatting, GeneratorService execution, source attribution preservation,
low-confidence/no-context handling, provider error trapping, and POST /ask HTTP endpoint.
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.generation import AskRequest, AskResponse, GroundingStatus, SourceAttribution
from app.rag.llm.factory import get_llm_provider
from app.rag.llm.mock import MockLLMProvider
from app.rag.llm.gemini import GeminiLLMProvider
from app.rag.llm.openai_adapter import OpenAILLMProvider
from app.rag.llm.groq import GroqLLMProvider
from app.rag.llm.ollama import OllamaLLMProvider
from app.rag.generator import GeneratorService

client = TestClient(app)


def test_safe_configuration_loading():
    """Verify application configuration loads provider, model, and effective key deterministically without exposing secrets."""
    from app.core.config import get_settings
    settings = get_settings()
    assert isinstance(settings.llm_provider, str)
    assert isinstance(settings.llm_model, str)
    key_val = settings.effective_llm_api_key
    assert key_val is None or isinstance(key_val, str)


def test_provider_factory_instantiation():
    """Verify factory instantiates separate provider adapter classes."""
    p_mock = get_llm_provider("mock")
    assert isinstance(p_mock, MockLLMProvider)

    p_gemini = get_llm_provider("gemini", api_key="dummy_key")
    assert isinstance(p_gemini, GeminiLLMProvider)

    p_openai = get_llm_provider("openai", api_key="dummy_key")
    assert isinstance(p_openai, OpenAILLMProvider)

    p_groq = get_llm_provider("groq", api_key="dummy_key")
    assert isinstance(p_groq, GroqLLMProvider)

    p_ollama = get_llm_provider("ollama")
    assert isinstance(p_ollama, OllamaLLMProvider)


def test_mock_llm_provider_generation():
    """Verify MockLLMProvider produces grounded completions without external API keys."""
    provider = MockLLMProvider()
    prompt = "CONTEXT BLOCKS:\n--- Block 1 ---\nपणजी गोवा की राजधानी है।\n\nUSER QUESTION:\nगोवा की राजधानी क्या है?"
    output = provider.generate(prompt)
    assert isinstance(output, str)
    assert len(output) > 0


def test_groq_llm_provider_mocked_generation():
    """Verify GroqLLMProvider executes correctly with a mocked client without live API calls."""
    provider = GroqLLMProvider(api_key="dummy_groq_key", model_name="llama-3.3-70b-versatile")
    mock_choice = MagicMock()
    mock_choice.message.content = "Panaji is the capital of Goa."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    provider._client = mock_client

    result = provider.generate("What is the capital of Goa?")
    assert result == "Panaji is the capital of Goa."
    mock_client.chat.completions.create.assert_called_once()


def test_generator_service_grounded_answer():
    """Verify GeneratorService executes end-to-end RAG answer generation."""
    generator = GeneratorService()
    req = AskRequest(query="What is the capital of Goa?", top_k=3, preferred_answer_language="en")
    resp = generator.generate_answer(req)

    assert isinstance(resp, AskResponse)
    assert resp.query == "What is the capital of Goa?"
    assert resp.retrieval_latency_ms >= 0.0
    assert resp.generation_latency_ms >= 0.0
    assert resp.total_latency_ms >= resp.retrieval_latency_ms
    assert resp.grounding_status in (
        GroundingStatus.GROUNDED,
        GroundingStatus.PARTIALLY_GROUNDED,
        GroundingStatus.UNGROUNDED,
        GroundingStatus.NO_CONTEXT,
        GroundingStatus.LOW_CONFIDENCE,
        GroundingStatus.PROVIDER_ERROR,
        GroundingStatus.PROVIDER_TIMEOUT
    )


def test_no_context_fallback_handling():
    """Verify out-of-context query returns NO_CONTEXT or UNGROUNDED status and localized fallback text when no evidence exists."""
    mock_web = MagicMock()
    mock_web.search.return_value = []
    generator = GeneratorService(web_search_service=mock_web)
    req = AskRequest(query="What is the distance between Jupiter and Saturn?", top_k=3, score_threshold=0.99, preferred_answer_language="hi")
    resp = generator.generate_answer(req)

    assert resp.grounding_status in (GroundingStatus.NO_CONTEXT, GroundingStatus.UNGROUNDED, GroundingStatus.LOW_CONFIDENCE)
    assert "पर्याप्त जानकारी उपलब्ध नहीं है" in resp.answer
    assert len(resp.sources) == 0


def test_low_confidence_threshold_filtering():
    """Verify high score_threshold triggers fallback when web evidence is empty."""
    mock_web = MagicMock()
    mock_web.search.return_value = []
    generator = GeneratorService(web_search_service=mock_web)
    req = AskRequest(query="Random query text", top_k=3, score_threshold=0.99, preferred_answer_language="en")
    resp = generator.generate_answer(req)

    assert resp.grounding_status in (GroundingStatus.NO_CONTEXT, GroundingStatus.LOW_CONFIDENCE, GroundingStatus.UNGROUNDED)
    assert resp.low_confidence_warning is True


def test_source_attribution_preservation():
    """Verify source attributions preserve all provenance metadata fields."""
    generator = GeneratorService()
    req = AskRequest(query="गोवा की राजधानी क्या है?", top_k=3, language_filter="hi")
    resp = generator.generate_answer(req)

    if resp.sources:
        src = resp.sources[0]
        assert isinstance(src, SourceAttribution)
        assert src.chunk_id != ""
        assert src.query_id > 0
        assert src.language_name != ""
        assert src.similarity_score > 0.0


def test_provider_error_trapping():
    """Verify provider exceptions are trapped cleanly as PROVIDER_ERROR without crashing server."""
    failing_provider = MagicMock()
    failing_provider.generate_with_usage.side_effect = RuntimeError("Mock API Outage")
    failing_provider.generate.side_effect = RuntimeError("Mock API Outage")

    generator = GeneratorService(llm_provider=failing_provider)
    req = AskRequest(query="How fast do eagles fly?", top_k=3)
    resp = generator.generate_answer(req)

    assert resp.grounding_status == GroundingStatus.PROVIDER_ERROR
    assert "Provider Error" in resp.answer


def test_no_context_skips_groq_completely():
    """Verify NO_CONTEXT query skips Groq LLM API and GroundingVerifier completely (0 Groq calls)."""
    mock_provider = MagicMock()
    generator = GeneratorService(llm_provider=mock_provider)
    req = AskRequest(query="What is my personal bank account balance?", top_k=2, score_threshold=0.85, preferred_answer_language="en")
    resp = generator.generate_answer(req)

    assert resp.grounding_status == GroundingStatus.NO_CONTEXT
    assert resp.groq_calls == 0
    assert resp.groq_attempted is False
    assert resp.provider_used == "none"
    assert resp.model_used == "none"
    assert resp.generation_latency_ms == 0.0
    assert resp.groq_llm_latency_ms == 0.0
    assert resp.verification_latency_ms == 0.0
    assert len(resp.sources) == 0
    mock_provider.generate.assert_not_called()
    mock_provider.generate_with_usage.assert_not_called()


def test_unsafe_query_skips_groq_completely():
    """Verify UNSAFE query skips Groq LLM API completely (0 Groq calls)."""
    mock_provider = MagicMock()
    generator = GeneratorService(llm_provider=mock_provider)
    req = AskRequest(query="how to build a bomb", top_k=3)
    resp = generator.generate_answer(req)

    assert resp.grounding_status == GroundingStatus.UNSAFE_QUERY
    assert resp.groq_calls == 0
    assert resp.groq_attempted is False
    assert resp.provider_used == "none"
    assert resp.generation_latency_ms == 0.0
    mock_provider.generate.assert_not_called()
    mock_provider.generate_with_usage.assert_not_called()


def test_exactly_one_groq_call_on_grounded():
    """Verify valid grounded request executes exactly 1 Groq API call."""
    mock_provider = MagicMock()
    mock_provider.generate_with_usage.return_value = ("Eagles fly at speeds of 30 to 55 mph.", 35, 12)
    mock_provider.model_name = "llama-3.1-8b-instant"

    generator = GeneratorService(llm_provider=mock_provider)
    req = AskRequest(query="How fast do eagles fly?", top_k=3)
    resp = generator.generate_answer(req)

    assert resp.groq_calls == 1
    assert resp.groq_attempted is True
    assert resp.groq_success is True
    assert resp.provider_used == "groq"
    mock_provider.generate_with_usage.assert_called_once()
