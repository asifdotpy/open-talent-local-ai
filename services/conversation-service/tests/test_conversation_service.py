"""In-process integration tests for Conversation Service.

Uses FastAPI TestClient to avoid requiring a running server on port 8014.
Relies on mock LLM/database flags set in tests/conftest.py.
"""

import uuid

from fastapi.testclient import TestClient


def _unique_session() -> str:
    return f"test-session-{uuid.uuid4().hex[:8]}"


class TestConversationServiceBasics:
    def test_service_health(self, test_client: TestClient):
        resp = test_client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "healthy"}

    def test_root_endpoint(self, test_client: TestClient):
        resp = test_client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("service") == "OpenTalent Conversation Service"


class TestConversationFlow:
    def test_start_and_status_and_end(self, test_client: TestClient):
        session_id = _unique_session()

        # Start
        start_resp = test_client.post(
            "/conversation/start",
            json={
                "session_id": session_id,
                "job_description": "Python developer role",
                "candidate_profile": {"name": "Test Candidate"},
                "interview_type": "technical",
                "tone": "friendly",
            },
        )
        assert start_resp.status_code == 200
        start_data = start_resp.json()
        assert start_data["session_id"] == session_id
        assert start_data["status"] == "started"
        conversation_id = start_data["conversation_id"]

        # Status
        status_resp = test_client.get(f"/conversation/status/{session_id}")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert status_data["session_id"] == session_id
        assert status_data["conversation_id"] == conversation_id

        # End
        end_resp = test_client.post(f"/conversation/end/{session_id}")
        assert end_resp.status_code == 200
        assert end_resp.json()["session_id"] == session_id

    def test_send_message_generates_response(self, test_client: TestClient):
        session_id = _unique_session()

        # Start a conversation first
        start_resp = test_client.post(
            "/conversation/start",
            json={
                "session_id": session_id,
                "job_description": "Data scientist role",
            },
        )
        assert start_resp.status_code == 200

        # Send message
        msg_resp = test_client.post(
            "/conversation/message",
            json={
                "session_id": session_id,
                "message": "Tell me about a project you enjoyed.",
                "message_type": "transcript",
            },
        )
        assert msg_resp.status_code == 200
        msg_data = msg_resp.json()
        assert msg_data["session_id"] == session_id
        assert msg_data["response_text"]
        assert msg_data["should_speak"] is True


class TestAdaptiveEndpoints:
    def test_generate_adaptive_question(self, test_client: TestClient):
        resp = test_client.post(
            "/api/v1/conversation/generate-adaptive-question",
            json={
                "room_id": "room-1",
                "session_id": _unique_session(),
                "previous_responses": [],
                "expertise_level": "intermediate",
                "job_requirements": "Python, FastAPI",
                "question_number": 1,
                "interview_phase": "technical",
                "bias_mitigation": True,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "question" in data
        assert data["question_number"] == 1

    def test_generate_followup(self, test_client: TestClient):
        resp = test_client.post(
            "/api/v1/conversation/generate-followup",
            json={
                "response_text": "I worked on a recommendation system using Python.",
                "question_context": "Tell me about your ML experience",
                "sentiment": {"polarity": 0.1},
                "quality": {"technical_accuracy": 0.8},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "questions" in data

    def test_adapt_interview_strategy(self, test_client: TestClient):
        resp = test_client.post(
            "/api/v1/conversation/adapt-interview",
            json={
                "current_phase": "technical",
                "time_remaining_minutes": 20,
                "performance_indicators": {"overall_score": 7.5},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "adaptations" in data
