"""Conversation Service Unit Tests.

Unit tests for individual components of the conversation service.
Focus on service logic, models, and utilities without external dependencies.

Test Coverage:
- Conversation service methods
- Mock response generation
- Error handling
- Data validation
"""

from datetime import datetime
from unittest.mock import patch

import pytest
from app.models.interview_models import (
    ConversationResponse,
    GenerateQuestionsRequest,
    StartConversationRequest,
)
from app.services.conversation_service import ConversationService
from app.services.ollama_service import generate_questions_from_ollama


class TestConversationService:
    """Unit tests for ConversationService class."""

    def setup_method(self):
        """Setup for each test."""
        self.service = ConversationService()

    def test_initialization(self):
        """Test service initialization."""
        assert self.service.active_conversations == {}
        assert hasattr(self.service, "conversation_timeout")
        assert hasattr(self.service, "ollama_client")

    @pytest.mark.asyncio
    async def test_start_conversation_success(self):
        """Test successful conversation start."""
        request = StartConversationRequest(
            session_id="test-123",
            job_description="Python Developer",
            interview_type="technical",
            tone="professional",
        )

        with patch.object(self.service, "_generate_initial_message", return_value="Welcome!"):
            result = await self.service.start_conversation(
                session_id=request.session_id,
                job_description=request.job_description,
                interview_type=request.interview_type,
                tone=request.tone,
            )

            assert "conversation_id" in result
            assert result["session_id"] == "test-123"
            assert result["initial_message"] == "Welcome!"
            assert result["status"] == "started"

            # Check conversation was stored
            assert len(self.service.active_conversations) == 1

    @pytest.mark.asyncio
    async def test_process_message_transcript(self):
        """Test processing transcript message."""
        # Setup active conversation
        conv_id = "conv-test"
        self.service.active_conversations[conv_id] = {
            "conversation_id": conv_id,
            "session_id": "session-123",
            "messages": [],
            "question_count": 0,
            "current_topic": None,
            "last_activity": datetime.now(),
        }

        with patch.object(self.service, "_process_transcript") as mock_process:
            mock_process.return_value = {
                "conversation_id": conv_id,
                "session_id": "session-123",
                "response_text": "Good answer!",
                "response_type": "feedback",
                "should_speak": True,
            }

            result = await self.service.process_message(
                session_id="session-123",
                message="I have 3 years experience",
                message_type="transcript",
            )

            assert result["response_text"] == "Good answer!"
            mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_no_conversation(self):
        """Test processing message when no conversation exists."""
        result = await self.service.process_message(
            session_id="nonexistent", message="Hello", message_type="transcript"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_conversation_status_active(self):
        """Test getting status of active conversation."""
        conv_id = "conv-status"
        self.service.active_conversations[conv_id] = {
            "conversation_id": conv_id,
            "session_id": "session-status",
            "status": "active",
            "messages": [{"type": "test"}],
            "last_activity": datetime.now(),
            "current_topic": "experience",
        }

        result = await self.service.get_conversation_status("session-status")

        assert result is not None
        assert result["conversation_id"] == conv_id
        assert result["status"] == "active"
        assert result["message_count"] == 1

    @pytest.mark.asyncio
    async def test_get_conversation_status_not_found(self):
        """Test getting status of non-existent conversation."""
        result = await self.service.get_conversation_status("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_end_conversation_success(self):
        """Test successfully ending a conversation."""
        conv_id = "conv-end"
        self.service.active_conversations[conv_id] = {
            "conversation_id": conv_id,
            "session_id": "session-end",
            "status": "active",
        }

        result = await self.service.end_conversation("session-end")

        assert result is True
        assert self.service.active_conversations[conv_id]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_end_conversation_not_found(self):
        """Test ending non-existent conversation."""
        result = await self.service.end_conversation("nonexistent")

        assert result is False

    def test_generate_mock_initial_message(self):
        """Test mock initial message generation."""
        context = {"session_id": "test-123", "interview_type": "technical"}

        message = self.service._generate_mock_initial_message(context)

        assert isinstance(message, str)
        assert len(message) > 10
        assert "technical" in message.lower() or "interview" in message.lower()

    def test_generate_mock_transcript_response(self):
        """Test mock transcript response generation."""
        conversation = {
            "conversation_id": "conv-test",
            "session_id": "session-test",
            "messages": [],
            "question_count": 0,
        }

        result = self.service._generate_mock_transcript_response(
            conversation, "I have Python experience", None
        )

        assert "conversation_id" in result
        assert "response_text" in result
        assert "response_type" in result
        assert result["response_type"] == "question"
        assert conversation["question_count"] == 1

    def test_extract_tech_keywords(self):
        """Test technical keyword extraction."""
        text = "I work with Python, React, and PostgreSQL databases."

        keywords = self.service._extract_tech_keywords(text)

        assert "python" in keywords
        assert "react" in keywords
        assert "postgresql" in keywords

    def test_build_system_prompt(self):
        """Test system prompt building."""
        context = {
            "job_description": "Python Developer",
            "interview_type": "technical",
            "tone": "professional",
            "question_count": 2,
        }

        prompt = self.service._build_system_prompt(context)

        assert "Python Developer" in prompt
        assert "technical" in prompt
        assert "professional" in prompt
        assert "question: 3" in prompt

    def test_classify_response_type_question(self):
        """Test response type classification for questions."""
        response = "Can you tell me about your experience?"

        result = self.service._classify_response_type(response)

        assert result == "question"

    def test_classify_response_type_feedback(self):
        """Test response type classification for feedback."""
        response = "That's excellent work!"

        result = self.service._classify_response_type(response)

        assert result == "feedback"

    def test_determine_topic_experience(self):
        """Test topic determination for experience-related content."""
        transcript = "I have 5 years of software development experience"
        response = "That's impressive experience!"

        topic = self.service._determine_topic(transcript, response)

        assert topic == "experience"


class TestOllamaService:
    """Unit tests for Ollama service functions."""

    def test_generate_questions_success_mock(self):
        """Test successful question generation with mock responses."""
        request = GenerateQuestionsRequest(job_description="Software Engineer", num_questions=2)

        result = generate_questions_from_ollama(
            job_description=request.job_description,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
        )

        assert isinstance(result, dict)
        assert "questions" in result
        assert len(result["questions"]) == 2
        assert all(
            "id" in q and "text" in q and "category" in q and "expected_duration_seconds" in q
            for q in result["questions"]
        )

    def test_generate_questions_success_real(self):
        """Test successful question generation with real Ollama."""
        expected = {
            "questions": [
                {
                    "id": 1,
                    "text": "Tell me about yourself",
                    "category": "behavioral",
                    "expected_duration_seconds": 60,
                }
            ]
        }

        def fake_run(coro):
            coro.close()
            return expected

        with patch("app.services.ollama_service.USE_MOCK", False), patch(
            "app.services.ollama_service.asyncio.run", side_effect=fake_run
        ) as mock_run:
            result = generate_questions_from_ollama(
                job_description="Software Engineer", num_questions=1, difficulty="easy"
            )

            assert result == expected
            mock_run.assert_called_once()

    def test_generate_questions_ollama_error(self):
        """Test question generation with Ollama error."""

        def fake_run_error(coro):
            coro.close()
            raise Exception("Ollama connection failed")

        with patch("app.services.ollama_service.USE_MOCK", False), patch(
            "app.services.ollama_service.asyncio.run", side_effect=fake_run_error
        ):
            result = generate_questions_from_ollama(
                job_description="Test job", num_questions=1, difficulty="easy"
            )

            assert "questions" in result
            assert len(result["questions"]) == 1


class TestDataValidation:
    """Unit tests for data validation and models."""

    def test_generate_questions_request_valid(self):
        """Test valid GenerateQuestionsRequest creation."""
        request = GenerateQuestionsRequest(
            job_description="Python Developer", num_questions=5, difficulty="medium"
        )

        assert request.job_description == "Python Developer"
        assert request.num_questions == 5
        assert request.difficulty == "medium"

    def test_generate_questions_request_validation(self):
        """Test GenerateQuestionsRequest validation."""
        # Valid request
        request = GenerateQuestionsRequest(job_description="Developer", num_questions=10)
        assert request.num_questions == 10

        # Invalid num_questions (too high)
        with pytest.raises(ValueError):
            GenerateQuestionsRequest(job_description="Developer", num_questions=25)  # Above max

        # Invalid num_questions (too low)
        with pytest.raises(ValueError):
            GenerateQuestionsRequest(job_description="Developer", num_questions=0)  # Below min

    def test_conversation_response_model(self):
        """Test ConversationResponse model creation."""
        response = ConversationResponse(
            conversation_id="conv-123",
            session_id="session-123",
            response_text="That's a good answer!",
            response_type="feedback",
            should_speak=True,
            metadata={"confidence": 0.9},
        )

        assert response.conversation_id == "conv-123"
        assert response.response_text == "That's a good answer!"
        assert response.response_type == "feedback"
        assert response.should_speak is True
        assert response.metadata["confidence"] == 0.9
