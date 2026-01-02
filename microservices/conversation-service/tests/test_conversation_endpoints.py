from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_generate_adaptive_question():
    """Test the adaptive question generation endpoint."""
    request_data = {
        "room_id": "test-room-123",
        "session_id": "test-session-456",
        "expertise_level": "intermediate",
        "job_requirements": "Python, Django, React",
        "question_number": 1,
        "interview_phase": "technical",
        "bias_mitigation": True,
    }

    response = client.post("/api/v1/conversation/generate-adaptive-question", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert "question" in data
    assert "question_number" in data
    assert "ai_metadata" in data
    assert data["question_number"] == 1
    assert "text" in data["question"]
    assert data["question"]["order"] == 1


def test_generate_followup_questions():
    """Test the follow-up question generation endpoint."""
    request_data = {
        "response_text": "I have experience with Python and Django.",
        "question_context": "Tell me about your technical background",
        "sentiment": {"polarity": 0.2, "subjectivity": 0.3},
        "quality": {"completeness": 0.8, "technical_accuracy": 0.9},
    }

    response = client.post("/api/v1/conversation/generate-followup", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert "questions" in data
    assert isinstance(data["questions"], list)
    assert len(data["questions"]) > 0

    # Check structure of first question
    question = data["questions"][0]
    assert "question" in question
    assert "priority" in question
    assert "reasoning" in question
    assert "expected_outcome" in question


def test_adapt_interview_strategy():
    """Test the interview adaptation endpoint."""
    request_data = {
        "current_phase": "technical",
        "time_remaining_minutes": 25,
        "performance_indicators": {"overall_score": 8.5, "sentiment_trend": "positive"},
    }

    response = client.post("/api/v1/conversation/adapt-interview", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert "adaptations" in data
    assert "recommendations" in data

    adaptations = data["adaptations"]
    assert "question_difficulty" in adaptations
    assert "focus_areas" in adaptations
    assert "time_adjustments" in adaptations
    assert "immediate_actions" in adaptations
    assert "strategy_changes" in adaptations


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
