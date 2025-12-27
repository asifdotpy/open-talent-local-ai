"""In-process integration tests for Conversation Service.

Runs against the FastAPI app directly (no external server) using the
TestClient fixture from tests/conftest.py which forces mock LLM and
disables DB writes. Uses unique session IDs per test to avoid state
bleed.
"""

import time
import uuid

from fastapi.testclient import TestClient


def _unique_session(prefix: str = "sess") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


class TestConversationServiceIntegration:
    def test_health_endpoint(self, test_client: TestClient):
        resp = test_client.get("/health")
        assert resp.status_code == 200
        assert resp.json().get("status") == "healthy"

    def test_root_endpoint(self, test_client: TestClient):
        resp = test_client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "OpenTalent Conversation Service" in data.get("service", "")
        assert "documentation" in data

    def test_api_docs_redirect(self, test_client: TestClient):
        resp = test_client.get("/doc", follow_redirects=False)
        assert resp.status_code == 307
        assert resp.headers.get("location") == "/docs"

    def test_api_docs_info(self, test_client: TestClient):
        resp = test_client.get("/api-docs")
        assert resp.status_code == 200
        routes = [r["path"] for r in resp.json().get("routes", [])]
        assert "/conversation/generate-questions" in routes
        assert "/conversation/start" in routes
        assert "/conversation/message" in routes

    def test_generate_questions_valid_request(self, test_client: TestClient):
        payload = {
            "job_description": "Senior Python Developer with React experience",
            "num_questions": 3,
            "difficulty": "medium",
        }
        resp = test_client.post("/conversation/generate-questions", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data.get("questions", [])) == 3

    def test_generate_questions_minimal_request(self, test_client: TestClient):
        resp = test_client.post(
            "/conversation/generate-questions",
            json={"job_description": "Software Engineer"},
        )
        assert resp.status_code == 200
        assert len(resp.json().get("questions", [])) == 10

    def test_generate_questions_max_questions(self, test_client: TestClient):
        resp = test_client.post(
            "/conversation/generate-questions",
            json={"job_description": "Data Scientist", "num_questions": 25},
        )
        assert resp.status_code == 422

    def test_generate_questions_empty_description(self, test_client: TestClient):
        resp = test_client.post(
            "/conversation/generate-questions",
            json={"job_description": "", "num_questions": 2},
        )
        assert resp.status_code in [200, 422]

    def test_generate_questions_invalid_difficulty(self, test_client: TestClient):
        resp = test_client.post(
            "/conversation/generate-questions",
            json={"job_description": "Frontend", "num_questions": 2, "difficulty": "invalid"},
        )
        assert resp.status_code in [200, 422]

    def test_start_conversation_valid(self, test_client: TestClient):
        session_id = _unique_session("valid")
        resp = test_client.post(
            "/conversation/start",
            json={
                "session_id": session_id,
                "job_description": "Python Developer with Django experience",
                "interview_type": "technical",
                "tone": "professional",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == session_id
        assert data["status"] == "started"

    def test_start_conversation_minimal(self, test_client: TestClient):
        session_id = _unique_session("minimal")
        resp = test_client.post(
            "/conversation/start",
            json={"session_id": session_id, "job_description": "Software Engineer"},
        )
        assert resp.status_code == 200
        assert resp.json()["session_id"] == session_id

    def test_send_message_to_conversation(self, test_client: TestClient):
        session_id = _unique_session("msg")
        start = test_client.post(
            "/conversation/start",
            json={"session_id": session_id, "job_description": "Python Developer"},
        )
        assert start.status_code == 200

        resp = test_client.post(
            "/conversation/message",
            json={
                "session_id": session_id,
                "message": "I have 5 years of Python experience",
                "message_type": "transcript",
            },
        )
        assert resp.status_code == 200
        assert resp.json().get("session_id") == session_id

    def test_send_message_no_active_conversation(self, test_client: TestClient):
        resp = test_client.post(
            "/conversation/message",
            json={
                "session_id": "nonexistent-session",
                "message": "Hello",
                "message_type": "transcript",
            },
        )
        assert resp.status_code == 404

    def test_get_conversation_status(self, test_client: TestClient):
        session_id = _unique_session("status")
        start = test_client.post(
            "/conversation/start",
            json={"session_id": session_id, "job_description": "Java Developer"},
        )
        assert start.status_code == 200

        resp = test_client.get(f"/conversation/status/{session_id}")
        assert resp.status_code == 200
        assert resp.json().get("session_id") == session_id

    def test_get_conversation_status_not_found(self, test_client: TestClient):
        resp = test_client.get("/conversation/status/nonexistent-session")
        assert resp.status_code == 404

    def test_end_conversation(self, test_client: TestClient):
        session_id = _unique_session("end")
        start = test_client.post(
            "/conversation/start",
            json={"session_id": session_id, "job_description": "DevOps Engineer"},
        )
        assert start.status_code == 200

        resp = test_client.post(f"/conversation/end/{session_id}")
        assert resp.status_code == 200

    def test_end_conversation_not_found(self, test_client: TestClient):
        resp = test_client.post("/conversation/end/nonexistent-session")
        assert resp.status_code == 404

    def test_invalid_json_payload(self, test_client: TestClient):
        resp = test_client.post(
            "/conversation/generate-questions",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 422

    def test_missing_required_fields(self, test_client: TestClient):
        resp = test_client.post("/conversation/generate-questions", json={})
        assert resp.status_code == 422

    def test_performance_question_generation(self, test_client: TestClient):
        start = time.time()
        resp = test_client.post(
            "/conversation/generate-questions",
            json={
                "job_description": "Full Stack Developer with React and Node.js experience",
                "num_questions": 5,
            },
        )
        duration = time.time() - start
        assert resp.status_code == 200
        assert duration < 5.0

    def test_performance_conversation_flow(self, test_client: TestClient):
        session_id = _unique_session("perf")
        start = time.time()

        assert (
            test_client.post(
                "/conversation/start",
                json={"session_id": session_id, "job_description": "Python Developer"},
            ).status_code
            == 200
        )

        assert (
            test_client.post(
                "/conversation/message",
                json={
                    "session_id": session_id,
                    "message": "I have experience with Django and Flask",
                    "message_type": "transcript",
                },
            ).status_code
            == 200
        )

        assert test_client.get(f"/conversation/status/{session_id}").status_code == 200
        assert test_client.post(f"/conversation/end/{session_id}").status_code == 200

        assert time.time() - start < 10.0
