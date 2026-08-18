# ============================================================
# Tests — Authentication Middleware
# ============================================================

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_auth_missing_header():
    """Unauthenticated requests to protected endpoints return 401."""
    response = client.get("/api/v1/reviews")
    assert response.status_code == 401
    assert "Missing Authorization header" in response.json()["detail"]


def test_auth_invalid_header_format():
    """Malformed Authorization header returns 401."""
    response = client.get("/api/v1/reviews", headers={"Authorization": "Basic 12345"})
    assert response.status_code == 401
    assert "Invalid Authorization header format" in response.json()["detail"]


def test_auth_invalid_token():
    """Invalid token format returns 401."""
    response = client.get("/api/v1/reviews", headers={"Authorization": "Bearer invalid_bad_token"})
    assert response.status_code == 401


def test_auth_mock_token_in_test_env():
    """Mock test token resolves correctly in development/test environment."""
    response = client.get("/api/v1/reviews", headers={"Authorization": "Bearer mock-test-token"})
    # Should authenticate (200 or 500/mock db, but not 401)
    assert response.status_code != 401
