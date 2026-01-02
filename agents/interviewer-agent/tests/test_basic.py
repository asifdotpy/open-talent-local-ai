"""
Tests for Vetta AI Interviewer Agent
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["agent"] == "vetta-ai"
    assert "timestamp" in data


def test_get_interview_not_found():
    """Test getting non-existent interview"""
    response = client.get("/interviews/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Interview not found"


def test_get_next_question_not_found():
    """Test getting next question for non-existent interview"""
    response = client.get("/interviews/nonexistent/next-question")
    assert response.status_code == 404
    assert response.json()["detail"] == "Interview not found"


# Note: Integration tests would require running services
# and are better suited for separate test suite
