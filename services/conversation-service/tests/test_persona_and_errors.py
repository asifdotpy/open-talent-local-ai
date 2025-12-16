"""Additional tests for Conversation Service

- Persona switching and current persona endpoints
- Generate-questions endpoint
- Error paths for non-existent sessions
- Message type variations
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("test_client")
class TestPersonaEndpoints:
    def test_switch_persona_success(self, test_client: TestClient):
        resp = test_client.post(
            "/api/v1/persona/switch",
            json={"persona": "technical"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["current_persona"] == "technical-interviewer"
        assert "previous_persona" in data

    def test_switch_persona_invalid(self, test_client: TestClient):
        resp = test_client.post(
            "/api/v1/persona/switch",
            json={"persona": "unknown"},
        )
        assert resp.status_code == 400
        data = resp.json()
        assert "Invalid persona" in data["detail"]

    def test_get_current_persona(self, test_client: TestClient):
        resp = test_client.get("/api/v1/persona/current")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["current_persona"], str)
        assert isinstance(data["available_personas"], list)
        assert {"technical-interviewer", "behavioral-interviewer", "hr-interviewer"}.issubset(
            set(data["available_personas"])
        )


@pytest.mark.usefixtures("test_client")
class TestGenerateQuestionsEndpoint:
    def test_generate_questions(self, test_client: TestClient):
        resp = test_client.post(
            "/conversation/generate-questions",
            json={
                "job_description": "Python role working with FastAPI",
                "num_questions": 3,
                "difficulty": "easy",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "questions" in data
        assert isinstance(data["questions"], list)
        assert len(data["questions"]) == 3
        for q in data["questions"]:
            assert set(q.keys()) == {"id", "text", "category", "expected_duration_seconds"}


@pytest.mark.usefixtures("test_client")
class TestErrorPaths:
    def test_status_nonexistent_session(self, test_client: TestClient):
        resp = test_client.get("/conversation/status/non-existent-session")
        assert resp.status_code == 404

    def test_end_nonexistent_session(self, test_client: TestClient):
        resp = test_client.post("/conversation/end/non-existent-session")
        assert resp.status_code == 404

    def test_send_message_nonexistent_session(self, test_client: TestClient):
        resp = test_client.post(
            "/conversation/message",
            json={
                "session_id": "non-existent-session",
                "message": "hello",
                "message_type": "transcript",
            },
        )
        assert resp.status_code == 404


@pytest.mark.usefixtures("test_client")
class TestMessageTypes:
    def test_message_type_variations(self, test_client: TestClient):
        # Start a conversation
        start = test_client.post(
            "/conversation/start",
            json={
                "session_id": "mt-session-1",
                "job_description": "Backend Python role",
            },
        )
        assert start.status_code == 200

        # user_input
        user_input = test_client.post(
            "/conversation/message",
            json={
                "session_id": "mt-session-1",
                "message": "User entered a direct message.",
                "message_type": "user_input",
            },
        )
        assert user_input.status_code == 200
        assert user_input.json()["should_speak"] is True

        # system message
        system_msg = test_client.post(
            "/conversation/message",
            json={
                "session_id": "mt-session-1",
                "message": "System maintenance notice.",
                "message_type": "system",
            },
        )
        assert system_msg.status_code == 200
        assert "System message acknowledged" in system_msg.json()["response_text"]
