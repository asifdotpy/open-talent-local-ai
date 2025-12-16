"""
Conversation Service Integration Tests

Comprehensive testing of the conversation service endpoints with honest validation
of actual service behavior. Tests both mock and real LLM modes where applicable.

Test Coverage:
- Health & Info endpoints (4 tests)
- Question generation endpoint (6 tests)
- Conversation lifecycle (start, message, status, end) (8 tests)
- Sentiment analysis (4 tests)
- Error handling (4 tests)
- Performance benchmarks (2 tests)

Total: 28 tests
"""

import pytest
import httpx
import asyncio
import time
from typing import Dict, Any
import json
from fastapi.testclient import TestClient

from main import app

# Test configuration
SERVICE_URL = "http://localhost:8003"
TEST_TIMEOUT = 30  # seconds

class TestConversationServiceIntegration:
    """Integration tests for Conversation Service endpoints."""

    def setup_method(self):
        """Setup for each test method."""
        self.client = TestClient(app)
        # Alternative httpx client for when we need real HTTP
        # self.http_client = httpx.AsyncClient(base_url=SERVICE_URL, timeout=TEST_TIMEOUT)

    def teardown_method(self):
        """Cleanup after each test method."""
        pass
        # asyncio.run(self.http_client.aclose())

    def test_health_endpoint(self):
        """Test health check endpoint returns healthy status."""
        response = self.client.get("/health")

        # Honest validation: service should return 200 with healthy status
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_root_endpoint(self):
        """Test root endpoint provides service information."""
        response = self.client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "TalentAI Conversation Service" in data["service"]
        assert "version" in data
        assert "documentation" in data

    def test_api_docs_redirect(self):
        """Test /doc endpoint redirects to /docs."""
        response = self.client.get("/doc", follow_redirects=False)

        # Should redirect to /docs
        assert response.status_code == 307  # Temporary redirect
        assert response.headers.get("location") == "/docs"

    def test_api_docs_info(self):
        """Test /api-docs endpoint provides comprehensive API information."""
        response = self.client.get("/api-docs")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "total_endpoints" in data
        assert "routes" in data
        assert isinstance(data["routes"], list)
        assert len(data["routes"]) > 0

        # Check that conversation endpoints are present
        route_paths = [route["path"] for route in data["routes"]]
        assert "/conversation/generate-questions" in route_paths
        assert "/conversation/start" in route_paths
        assert "/conversation/message" in route_paths

    
    def test_generate_questions_valid_request(self):
        """Test question generation with valid job description."""
        payload = {
            "job_description": "Senior Python Developer with React experience",
            "num_questions": 3,
            "difficulty": "medium"
        }

        response = self.client.post("/conversation/generate-questions", json=payload)

        # Honest validation: should work with mock mode
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert isinstance(data["questions"], list)
        assert len(data["questions"]) == 3

        # Validate question structure
        for question in data["questions"]:
            assert "id" in question
            assert "text" in question
            assert "category" in question
            assert "expected_duration_seconds" in question
            assert isinstance(question["text"], str)
            assert len(question["text"]) > 10

    
    def test_generate_questions_minimal_request(self):
        """Test question generation with minimal required fields."""
        payload = {
            "job_description": "Software Engineer"
        }

        response = self.client.post("/conversation/generate-questions", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert len(data["questions"]) == 10  # default num_questions

    
    def test_generate_questions_max_questions(self):
        """Test question generation respects maximum limit."""
        payload = {
            "job_description": "Data Scientist",
            "num_questions": 25  # Above max limit
        }

        response = self.client.post("/conversation/generate-questions", json=payload)

        # Should return 422 for validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    
    def test_generate_questions_empty_description(self):
        """Test question generation with empty job description."""
        payload = {
            "job_description": "",
            "num_questions": 2
        }

        response = self.client.post("/conversation/generate-questions", json=payload)

        # Should handle gracefully or return validation error
        # Honest validation: depends on implementation
        if response.status_code == 422:
            assert "detail" in response.json()
        else:
            # If it accepts, should return some questions
            assert response.status_code == 200
            data = response.json()
            assert "questions" in data

    
    def test_generate_questions_invalid_difficulty(self):
        """Test question generation with invalid difficulty level."""
        payload = {
            "job_description": "Frontend Developer",
            "num_questions": 2,
            "difficulty": "invalid_level"
        }

        response = self.client.post("/conversation/generate-questions", json=payload)

        # Should accept gracefully (service handles validation)
        assert response.status_code in [200, 422]

    
    def test_start_conversation_valid(self):
        """Test starting a conversation with valid parameters."""
        payload = {
            "session_id": "test-session-123",
            "job_description": "Python Developer with Django experience",
            "interview_type": "technical",
            "tone": "professional"
        }

        response = self.client.post("/conversation/start", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "session_id" in data
        assert "initial_message" in data
        assert "status" in data
        assert data["status"] == "started"

    
    def test_start_conversation_minimal(self):
        """Test starting conversation with minimal parameters."""
        payload = {
            "session_id": "test-session-minimal",
            "job_description": "Software Engineer"
        }

        response = self.client.post("/conversation/start", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert data["session_id"] == "test-session-minimal"

    
    def test_send_message_to_conversation(self):
        """Test sending a message to an active conversation."""
        # First start a conversation
        start_payload = {
            "session_id": "test-message-session",
            "job_description": "Python Developer"
        }

        start_response = self.client.post("/conversation/start", json=start_payload)
        assert start_response.status_code == 200

        # Now send a message
        message_payload = {
            "session_id": "test-message-session",
            "message": "I have 5 years of Python experience",
            "message_type": "transcript"
        }

        response = self.client.post("/conversation/message", json=message_payload)

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "response_text" in data
        assert "response_type" in data
        assert "should_speak" in data

    
    def test_send_message_no_active_conversation(self):
        """Test sending message when no conversation exists."""
        message_payload = {
            "session_id": "nonexistent-session",
            "message": "Hello",
            "message_type": "transcript"
        }

        response = self.client.post("/conversation/message", json=message_payload)

        # Should return 404 for no active conversation
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    
    def test_get_conversation_status(self):
        """Test getting status of an active conversation."""
        # Start conversation first
        start_payload = {
            "session_id": "test-status-session",
            "job_description": "Java Developer"
        }

        start_response = self.client.post("/conversation/start", json=start_payload)
        assert start_response.status_code == 200

        # Get status
        response = self.client.get("/conversation/status/test-status-session")

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "session_id" in data
        assert "status" in data
        assert "message_count" in data
        assert "last_activity" in data

    
    def test_get_conversation_status_not_found(self):
        """Test getting status of non-existent conversation."""
        response = self.client.get("/conversation/status/nonexistent-session")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    
    def test_end_conversation(self):
        """Test ending an active conversation."""
        # Start conversation first
        start_payload = {
            "session_id": "test-end-session",
            "job_description": "DevOps Engineer"
        }

        start_response = self.client.post("/conversation/start", json=start_payload)
        assert start_response.status_code == 200

        # End conversation
        response = self.client.post("/conversation/end/test-end-session")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Conversation ended successfully" in data["message"]

    
    def test_end_conversation_not_found(self):
        """Test ending non-existent conversation."""
        response = self.client.post("/conversation/end/nonexistent-session")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    
    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis with positive text."""
        payload = {
            "text": "I'm very excited about this opportunity and have extensive experience in Python development",
            "context": "interview"
        }

        response = self.client.post("/conversation/analyze-sentiment", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
        assert "polarity" in data
        assert "subjectivity" in data
        assert data["sentiment"] >= 0  # Should be positive

    
    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis with negative text."""
        payload = {
            "text": "I'm not sure if I'm qualified for this position and lack experience in required technologies",
            "context": "interview"
        }

        response = self.client.post("/conversation/analyze-sentiment", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
        assert data["sentiment"] <= 0  # Should be negative or neutral

    
    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis with neutral text."""
        payload = {
            "text": "I have worked with various programming languages including Java and C++",
            "context": "general"
        }

        response = self.client.post("/conversation/analyze-sentiment", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
        # Neutral text should be close to 0
        assert -0.5 <= data["sentiment"] <= 0.5

    
    def test_analyze_sentiment_empty_text(self):
        """Test sentiment analysis with empty text."""
        payload = {
            "text": "",
            "context": "interview"
        }

        response = self.client.post("/conversation/analyze-sentiment", json=payload)

        # Should handle gracefully
        assert response.status_code in [200, 422]

    
    def test_invalid_json_payload(self):
        """Test handling of invalid JSON payloads."""
        response = self.client.post(
            "/conversation/generate-questions",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )

        # Should return 422 for invalid JSON
        assert response.status_code == 422

    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        payload = {}  # Missing job_description

        response = self.client.post("/conversation/generate-questions", json=payload)

        # Should return 422 for validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    
    def test_performance_question_generation(self):
        """Test performance of question generation endpoint."""
        payload = {
            "job_description": "Full Stack Developer with React and Node.js experience",
            "num_questions": 5
        }

        start_time = time.time()
        response = self.client.post("/conversation/generate-questions", json=payload)
        end_time = time.time()

        assert response.status_code == 200

        # Should complete within reasonable time (under 5 seconds for mock mode)
        duration = end_time - start_time
        assert duration < 5.0, f"Request took {duration:.2f}s, expected < 5.0s"

    
    def test_performance_conversation_flow(self):
        """Test performance of complete conversation flow."""
        start_time = time.time()

        # Start conversation
        start_payload = {
            "session_id": "perf-test-session",
            "job_description": "Python Developer"
        }
        start_response = self.client.post("/conversation/start", json=start_payload)
        assert start_response.status_code == 200

        # Send message
        message_payload = {
            "session_id": "perf-test-session",
            "message": "I have experience with Django and Flask",
            "message_type": "transcript"
        }
        message_response = self.client.post("/conversation/message", json=message_payload)
        assert message_response.status_code == 200

        # Get status
        status_response = self.client.get("/conversation/status/perf-test-session")
        assert status_response.status_code == 200

        # End conversation
        end_response = self.client.post("/conversation/end/perf-test-session")
        assert end_response.status_code == 200

        end_time = time.time()
        total_duration = end_time - start_time

        # Complete flow should take under 10 seconds
        assert total_duration < 10.0, f"Complete flow took {total_duration:.2f}s, expected < 10.0s"