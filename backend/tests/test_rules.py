import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.middleware.auth import get_current_user
from app.dependencies import get_firestore_client

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "test-user-123",
        "email": "test@example.com",
    }
    yield
    app.dependency_overrides.clear()


def test_create_rule_success():
    mock_db = MagicMock()
    
    # Mock existing docs to return rule #1, #2, #5
    doc1 = MagicMock()
    doc1.id = "1"
    doc1.to_dict.return_value = {"id": "1", "type": "formatting"}
    
    doc2 = MagicMock()
    doc2.id = "5"
    doc2.to_dict.return_value = {"id": "5", "type": "security"}
    
    mock_db.collection.return_value.stream.return_value = [doc1, doc2]
    mock_doc_ref = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    app.dependency_overrides[get_firestore_client] = lambda: mock_db

    response = client.post(
        "/api/v1/rules",
        json={
            "type": "Performance",
            "description": "Always index foreign keys used in high frequency JOIN clauses.",
        },
        headers={"Authorization": "Bearer mock-token"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["rule"]["id"] == "6"  # Max is 5 -> next is 6
    assert data["rule"]["type"] == "performance"
    assert "Always index foreign keys" in data["rule"]["description"]
    
    mock_db.collection.return_value.document.assert_called_with("6")
    mock_doc_ref.set.assert_called_once()


def test_create_rule_validation_error():
    response = client.post(
        "/api/v1/rules",
        json={
            "type": "",
            "description": "Too",  # Less than 5 chars
        },
        headers={"Authorization": "Bearer mock-token"},
    )
    assert response.status_code == 422  # Unprocessable entity (Pydantic validation)
