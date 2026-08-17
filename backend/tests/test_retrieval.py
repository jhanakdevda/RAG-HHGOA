"""
Unit Tests for Phase 6 Multilingual Retrieval Service

Tests query vector embedding, FAISS search, metadata lookup, language filtering,
score thresholding, low-confidence warning handling, latency instrumentation,
and LLM context string formatting.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.retrieval import RetrievalRequest, RetrievalResponse, RetrievalResult
from app.rag.retrieval import RetrievalService

client = TestClient(app)


def test_retrieval_service_initialization():
    """Verify RetrievalService initializes and loads vector store and metadata cache."""
    service = RetrievalService()
    service._ensure_loaded()
    assert service.vector_store is not None
    assert service.vector_store.ntotal > 0
    assert service._metadata_cache is not None
    assert len(service._metadata_cache) == service.vector_store.ntotal


def test_multilingual_query_retrieval():
    """Verify retrieval for queries across English and Indic languages."""
    service = RetrievalService()
    queries = [
        ("What is the capital of Goa?", None),
        ("गोवा की राजधानी क्या है?", "hi"),
        ("गोव्याची राजधानी कोणती आहे?", "mr"),
        ("গোয়ার রাজধানী কী?", "bn"),
        ("கோவாவின் தலைநகரம் எது?", "ta"),
        ("గోవా రాజధాని ఏది?", "te"),
        ("گوا کا دارالحکومت کون سا ہے؟", "ur"),
    ]

    for q_text, lang_filter in queries:
        req = RetrievalRequest(query=q_text, top_k=3, language_filter=lang_filter)
        resp = service.retrieve(req)

        assert isinstance(resp, RetrievalResponse)
        assert resp.query == q_text
        assert resp.latency_ms > 0
        assert "query_embedding_ms" in resp.latency_breakdown
        assert "faiss_search_ms" in resp.latency_breakdown
        assert "metadata_lookup_ms" in resp.latency_breakdown
        assert len(resp.results) > 0, f"Expected non-empty results for query '{q_text}' (lang={lang_filter})"


def test_language_filtering_strictness():
    """Verify language_filter strictly returns chunks belonging to requested language."""
    service = RetrievalService()

    req_hi = RetrievalRequest(query="गोवा की राजधानी क्या है?", top_k=5, language_filter="hi")
    resp_hi = service.retrieve(req_hi)
    assert len(resp_hi.results) > 0
    for res in resp_hi.results:
        lang_code = (res.chunk.language_code or "").lower()
        target_lang = (res.chunk.target_lang or "").lower()
        assert any(token in ("hi", "hindi", "hin_deva") for token in (lang_code, target_lang))

    req_bn = RetrievalRequest(query="গোয়ার রাজধানী কী?", top_k=5, language_filter="bn")
    resp_bn = service.retrieve(req_bn)
    assert len(resp_bn.results) > 0
    for res in resp_bn.results:
        lang_code = (res.chunk.language_code or "").lower()
        target_lang = (res.chunk.target_lang or "").lower()
        assert any(token in ("bn", "bengali", "ben_beng") for token in (lang_code, target_lang))


def test_score_threshold_filtering():
    """Verify score_threshold filters out chunks below threshold and sets low_confidence_warning."""
    service = RetrievalService()

    # Unreasonably high threshold to trigger low confidence
    req = RetrievalRequest(query="Random query text", top_k=5, score_threshold=0.99)
    resp = service.retrieve(req)

    assert len(resp.results) == 0
    assert resp.low_confidence_warning is True


def test_latency_instrumentation_fields():
    """Verify all latency timing breakdown fields are positive floats."""
    service = RetrievalService()
    req = RetrievalRequest(query="Panaji Goa tourism", top_k=3)
    resp = service.retrieve(req)

    breakdown = resp.latency_breakdown
    assert breakdown["query_embedding_ms"] >= 0.0
    assert breakdown["faiss_search_ms"] >= 0.0
    assert breakdown["metadata_lookup_ms"] >= 0.0
    assert resp.latency_ms >= breakdown["query_embedding_ms"]


def test_llm_context_formatting():
    """Verify format_context_for_llm constructs formatted context string."""
    service = RetrievalService()
    req = RetrievalRequest(query="Capital city of Goa", top_k=2)
    resp = service.retrieve(req)

    context_str = resp.format_context_for_llm()
    assert isinstance(context_str, str)
    assert len(context_str) > 0
    assert "--- Context Block 1" in context_str


def test_api_retrieve_endpoint():
    """Verify POST /retrieve HTTP endpoint returns valid RetrievalResponse JSON."""
    payload = {
        "query": "What is the capital of Goa?",
        "top_k": 3,
        "language_filter": None
    }
    response = client.post("/retrieve", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["query"] == "What is the capital of Goa?"
    assert "results" in data
    assert "latency_ms" in data
    assert "latency_breakdown" in data
    assert len(data["results"]) > 0
