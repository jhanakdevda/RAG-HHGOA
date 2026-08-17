"""
Unit Tests for Phase 9 Evaluation, Benchmarking & Production Reliability

Tests CORS middleware headers, evaluation dataset parsing, threshold overrides,
and API error trapping.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add project root to sys.path for scripts import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.main import app
from app.core.config import get_settings
from scripts.evaluate_rag_pipeline import load_sample_examples

client = TestClient(app)


def test_cors_middleware_configuration():
    """Verify CORS middleware responds with allowed origins headers."""
    response = client.options(
        "/ask",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_evaluation_dataset_sample_loading():
    """Verify evaluation dataset loader loads authentic MS MARCO-XI examples."""
    examples = load_sample_examples()
    assert len(examples) > 0
    assert examples[0].query != ""
    assert examples[0].passages is not None
    assert hasattr(examples[0].passages, "is_selected")


def test_configurable_threshold_settings():
    """Verify grounding thresholds are configurable via application settings."""
    settings = get_settings()
    assert settings.grounding_grounded_threshold == 0.70
    assert settings.grounding_partial_threshold == 0.45


def test_api_health_check_response():
    """Verify /health endpoint returns HTTP 200 with OK status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == "HH Goa Voice RAG"
