import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("test_client")
class TestMinimalPayloads:
    def test_generate_adaptive_question_minimal(self, test_client: TestClient):
        resp = test_client.post(
            "/api/v1/conversation/generate-adaptive-question",
            json={
                "room_id": "room-min",
                "session_id": "sess-min",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "question" in data
        q = data["question"]
        assert q["id"].startswith("q-room-min-")
        assert isinstance(q["order"], int)
        assert "ai_metadata" in q

    def test_generate_followup_minimal(self, test_client: TestClient):
        resp = test_client.post(
            "/api/v1/conversation/generate-followup",
            json={
                "response_text": "Short answer.",
                "question_context": "Basic question",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "questions" in data
        assert len(data["questions"]) >= 1

    def test_adapt_interview_minimal(self, test_client: TestClient):
        resp = test_client.post(
            "/api/v1/conversation/adapt-interview",
            json={
                "current_phase": "technical",
                "time_remaining_minutes": 5,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "adaptations" in data
        assert "recommendations" in data