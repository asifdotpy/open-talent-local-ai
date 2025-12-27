"""Tests for the current Interview Service implementation (main.py)

Tests room management, WebRTC streaming, transcription, and AI intelligence features.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client for the interview service."""
    from main import app

    return TestClient(app)


@pytest.fixture
def sample_room_data():
    """Sample room creation data."""
    return {
        "interview_session_id": "session-123",
        "participants": [
            {"user_id": "interviewer-1", "display_name": "John Interviewer", "role": "interviewer"},
            {"user_id": "candidate-1", "display_name": "Jane Candidate", "role": "candidate"},
        ],
        "duration_minutes": 45,
        "job_id": "job-123",
        "job_description": "Senior Python Developer position",
    }


class TestRoomManagement:
    """Test room creation, joining, and management."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns correct response."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "OpenTalent Interview Service" in data["message"]
        assert "version" in data
        assert "active_rooms" in data

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert "components" in data
        assert "metrics" in data

    def test_create_room_success(self, client, sample_room_data):
        """Test successful room creation."""
        response = client.post("/api/v1/rooms/create", json=sample_room_data)
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "room_id" in data
        assert "room_name" in data
        assert "jitsi_url" in data
        assert data["interview_session_id"] == "session-123"
        assert "created_at" in data
        assert "expires_at" in data
        assert data["status"] == "created"
        assert len(data["participants"]) == 2
        assert data["max_duration_minutes"] == 45

    def test_create_room_missing_session_id(self, client):
        """Test room creation fails without session ID."""
        data = {
            "participants": [{"user_id": "test", "display_name": "Test", "role": "candidate"}],
            "duration_minutes": 30,
        }
        response = client.post("/api/v1/rooms/create", json=data)
        assert response.status_code == 422  # Pydantic validation error

    def test_create_room_invalid_duration(self, client):
        """Test room creation fails with invalid duration."""
        data = {
            "interview_session_id": "session-123",
            "participants": [{"user_id": "test", "display_name": "Test", "role": "candidate"}],
            "duration_minutes": 500,  # Too long
        }
        response = client.post("/api/v1/rooms/create", json=data)
        assert response.status_code == 400  # Manual validation error

    def test_join_room_success(self, client, sample_room_data):
        """Test successfully joining a room."""
        # First create a room
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        # Join the room
        join_data = {
            "participant": {
                "user_id": "new-participant",
                "display_name": "New User",
                "role": "observer",
            }
        }
        response = client.post(f"/api/v1/rooms/{room_id}/join", json=join_data)
        assert response.status_code == 200
        data = response.json()
        assert "Successfully joined room" in data["message"]
        assert data["participant_count"] == 3

    def test_join_nonexistent_room(self, client):
        """Test joining a room that doesn't exist."""
        join_data = {
            "participant": {"user_id": "test", "display_name": "Test User", "role": "candidate"}
        }
        response = client.post("/api/v1/rooms/nonexistent-room/join", json=join_data)
        assert response.status_code == 404

    def test_get_room_status(self, client, sample_room_data):
        """Test getting room status."""
        # Create a room first
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        # Get room status
        response = client.get(f"/api/v1/rooms/{room_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["room_id"] == room_id
        assert data["status"] == "created"
        assert len(data["participants"]) == 2

    def test_list_rooms(self, client, sample_room_data):
        """Test listing rooms."""
        # Create a room first
        client.post("/api/v1/rooms/create", json=sample_room_data)

        # List all rooms
        response = client.get("/api/v1/rooms")
        assert response.status_code == 200
        data = response.json()
        assert "rooms" in data
        assert "total_count" in data
        assert "active_count" in data
        assert data["total_count"] >= 1

    def test_end_room(self, client, sample_room_data):
        """Test ending a room."""
        # Create a room first
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        # End the room
        response = client.delete(f"/api/v1/rooms/{room_id}/end")
        assert response.status_code == 200
        data = response.json()
        assert "Room ended successfully" in data["message"]
        assert data["room_id"] == room_id


class TestWebRTCAudioStreaming:
    """Test WebRTC audio streaming endpoints."""

    @patch("httpx.AsyncClient")
    def test_start_webrtc_streaming_success(self, mock_client, client, sample_room_data):
        """Test starting WebRTC audio streaming."""
        # Create a room first
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        # Mock voice service response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ready", "connection_id": "voice-conn-123"}
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        # Start WebRTC streaming
        response = client.post(
            f"/api/v1/rooms/{room_id}/webrtc/start", params={"participant_id": "candidate-1"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["connection_id"].startswith("webrtc-")
        assert data["status"] == "ready"

    def test_start_webrtc_nonexistent_room(self, client):
        """Test starting WebRTC in nonexistent room."""
        response = client.post(
            "/api/v1/rooms/nonexistent/webrtc/start", params={"participant_id": "test"}
        )
        assert response.status_code == 404

    def test_get_webrtc_status(self, client, sample_room_data):
        """Test getting WebRTC status."""
        # Create a room first
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        response = client.get(f"/api/v1/rooms/{room_id}/webrtc/status")
        assert response.status_code == 200
        data = response.json()
        assert data["room_id"] == room_id
        assert "total_connections" in data
        assert "connections" in data


class TestTranscription:
    """Test transcription endpoints."""

    def test_get_transcription_history_empty(self, client, sample_room_data):
        """Test getting empty transcription history."""
        # Create a room first
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        response = client.get(f"/api/v1/rooms/{room_id}/transcription")
        assert response.status_code == 200
        data = response.json()
        assert data["room_id"] == room_id
        assert data["total_segments"] == 0
        assert len(data["segments"]) == 0

    def test_submit_transcription_segment(self, client, sample_room_data):
        """Test submitting transcription segment."""
        # Create a room first
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        segment_data = {
            "text": "Hello, this is a test transcription.",
            "start_time": 0.0,
            "end_time": 2.5,
            "confidence": 0.95,
            "speaker_id": "candidate-1",
            "is_final": True,
            "words": [
                {"word": "Hello", "start": 0.0, "end": 0.5, "confidence": 0.98},
                {"word": "this", "start": 0.5, "end": 0.8, "confidence": 0.96},
            ],
        }

        response = client.post(
            f"/api/v1/rooms/{room_id}/transcription",
            json=segment_data,
            params={"session_id": "session-123", "participant_id": "candidate-1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "segment_id" in data
        assert "clients_notified" in data

    def test_clear_transcription_history(self, client, sample_room_data):
        """Test clearing transcription history."""
        # Create a room first
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        response = client.delete(f"/api/v1/rooms/{room_id}/transcription")
        assert response.status_code == 200
        data = response.json()
        assert "Cleared" in data["message"]
        assert data["room_id"] == room_id

    def test_get_transcription_status(self, client):
        """Test getting transcription system status."""
        response = client.get("/api/v1/transcription/status")
        assert response.status_code == 200
        data = response.json()
        assert "active_websocket_connections" in data
        assert "rooms_with_transcription" in data
        assert "total_transcription_segments" in data


class TestAIIntelligence:
    """Test AI interview intelligence endpoints."""

    def test_get_next_question(self, client, sample_room_data):
        """Test getting next AI-generated question."""
        # Create a room first
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        # Mock conversation service
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "question": "Can you describe your experience with Python?",
                "difficulty": "medium",
                "bias_score": 0.1,
                "sentiment_context": "neutral",
            }
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            response = client.post(f"/api/v1/rooms/{room_id}/next-question", json={})
            assert response.status_code == 200
            data = response.json()
            assert "question" in data
            assert "question_number" in data
            assert "ai_metadata" in data

    def test_analyze_response(self, client, sample_room_data):
        """Test analyzing candidate response."""
        # Create a room first
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        analysis_data = {
            "question_id": "q-123",
            "response_text": "I have 5 years of experience with Python and Django.",
            "question_context": "Tell me about your Python experience.",
            "participant_id": "candidate-1",
        }

        response = client.post(f"/api/v1/rooms/{room_id}/analyze-response", json=analysis_data)
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "sentiment_summary" in data
        assert "quality_score" in data
        assert "bias_flags" in data
        assert "expertise_level" in data

    def test_adapt_interview_strategy(self, client, sample_room_data):
        """Test adapting interview strategy."""
        # Create a room first
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        adaptation_data = {
            "current_phase": "technical",
            "time_remaining_minutes": 25,
            "performance_indicators": {"sentiment_trend": "positive", "quality_score": 8.5},
        }

        response = client.post(f"/api/v1/rooms/{room_id}/adapt-interview", json=adaptation_data)
        assert response.status_code == 200
        data = response.json()
        assert "adaptations" in data
        assert "performance_summary" in data
        assert "recommendations" in data

    def test_get_intelligence_report(self, client, sample_room_data):
        """Test getting intelligence report."""
        # Create a room first
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        response = client.get(f"/api/v1/rooms/{room_id}/intelligence-report")
        assert response.status_code == 200
        data = response.json()
        assert "room_id" in data
        assert "report" in data
        assert "generated_at" in data


class TestInterviewStart:
    """Test interview start endpoint."""

    @patch("httpx.AsyncClient")
    def test_start_interview_success(self, mock_client, client, sample_room_data):
        """Test starting interview with voice service integration."""
        # Mock voice service response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "started", "session_id": "voice-session-123"}
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        response = client.post("/api/v1/interviews/start", json=sample_room_data)
        assert response.status_code == 200
        data = response.json()
        assert "room_id" in data
        assert "interview_session_id" in data
        assert "jitsi_url" in data

    @patch("httpx.AsyncClient")
    def test_start_interview_voice_service_failure(self, mock_client, client, sample_room_data):
        """Test interview start when voice service fails (should still work)."""
        # Mock voice service failure
        mock_client.return_value.__aenter__.return_value.post.side_effect = Exception(
            "Voice service down"
        )

        response = client.post("/api/v1/interviews/start", json=sample_room_data)
        assert response.status_code == 200  # Should still succeed
        data = response.json()
        assert "room_id" in data


class TestErrorHandling:
    """Test error handling across endpoints."""

    def test_get_nonexistent_room_status(self, client):
        """Test getting status of nonexistent room."""
        response = client.get("/api/v1/rooms/nonexistent-room/status")
        assert response.status_code == 404

    def test_join_ended_room(self, client, sample_room_data):
        """Test joining a room that has ended."""
        # Create and end a room
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]
        client.delete(f"/api/v1/rooms/{room_id}/end")

        # Try to join ended room
        join_data = {
            "participant": {"user_id": "test", "display_name": "Test User", "role": "candidate"}
        }
        response = client.post(f"/api/v1/rooms/{room_id}/join", json=join_data)
        assert response.status_code == 410  # Gone

    def test_webrtc_signaling_without_connection(self, client, sample_room_data):
        """Test WebRTC signaling without active connection."""
        # Create a room first
        create_response = client.post("/api/v1/rooms/create", json=sample_room_data)
        room_id = create_response.json()["room_id"]

        signal_data = {
            "type": "offer",
            "session_id": "session-123",
            "room_id": room_id,
            "participant_id": "candidate-1",
            "data": {"sdp": "fake-sdp"},
        }

        response = client.post(f"/api/v1/rooms/{room_id}/webrtc/signal", json=signal_data)
        assert response.status_code == 404  # No WebRTC connection found
