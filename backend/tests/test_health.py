"""Tests for the health check endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_expected_json() -> None:
    """Health endpoint should return 200 with the expected payload."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "project": "HH Goa Voice RAG",
        "stage": "backend foundation",
    }
