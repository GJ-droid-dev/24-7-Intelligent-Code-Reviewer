# ============================================================
# Tests — Review CRUD Endpoints
# ============================================================

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
AUTH_HEADER = {"Authorization": "Bearer mock-test-token"}


def test_root_endpoint():
    """Root endpoint returns API operational status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["docs_url"] == "/docs"


def test_health_endpoint():
    """Health check endpoint returns 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


def test_submit_review_validation_error():
    """Submitting empty body or missing code returns 422."""
    response = client.post("/api/v1/reviews", json={}, headers=AUTH_HEADER)
    assert response.status_code == 422


def test_submit_review_success():
    """Submitting valid code returns 202 Accepted with reviewId and detected language."""
    payload = {
        "code": "def hello():\n    print('world')",
        "title": "Test Submission",
        "description": "A unit test submission",
    }
    response = client.post("/api/v1/reviews", json=payload, headers=AUTH_HEADER)
    assert response.status_code == 202
    data = response.json()
    assert "reviewId" in data
    assert data["language"] == "python"
    assert data["status"] in ("processing", "complete")


def test_get_review_not_found():
    """Requesting non-existent review returns 404."""
    response = client.get("/api/v1/reviews/non-existent-id", headers=AUTH_HEADER)
    assert response.status_code == 404
