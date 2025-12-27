"""
HTTP clients for OpenTalent microservices.
Implements retry logic, circuit breakers, and timeout configuration.
"""

import logging
from datetime import datetime
from typing import Any, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Simple circuit breaker implementation"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.is_open = False

    def call_succeeded(self):
        """Reset on successful call"""
        self.failures = 0
        self.is_open = False

    def call_failed(self):
        """Track failed call"""
        self.failures += 1
        self.last_failure_time = datetime.utcnow()

        if self.failures >= self.failure_threshold:
            self.is_open = True
            logger.warning(f"Circuit breaker opened after {self.failures} failures")

    def can_execute(self) -> bool:
        """Check if circuit allows execution"""
        if not self.is_open:
            return True

        # Check if timeout has passed
        if self.last_failure_time:
            elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
            if elapsed >= self.timeout:
                logger.info("Circuit breaker attempting reset")
                self.is_open = False
                self.failures = 0
                return True

        return False


class BaseServiceClient:
    """Base class for microservice clients"""

    def __init__(self, base_url: str, timeout: float = 30.0, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.circuit_breaker = CircuitBreaker()
        self.client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    async def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """
        Make HTTP request with retry logic

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for httpx

        Returns:
            httpx.Response
        """
        if not self.circuit_breaker.can_execute():
            raise Exception("Circuit breaker is open")

        url = f"{self.base_url}{endpoint}"

        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            self.circuit_breaker.call_succeeded()
            return response
        except Exception as e:
            self.circuit_breaker.call_failed()
            logger.error(f"Request failed: {method} {url} - {e}")
            raise

    async def get(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """GET request"""
        response = await self._request("GET", endpoint, **kwargs)
        return response.json()

    async def post(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """POST request"""
        response = await self._request("POST", endpoint, **kwargs)
        return response.json()

    async def put(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """PUT request"""
        response = await self._request("PUT", endpoint, **kwargs)
        return response.json()

    async def delete(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """DELETE request"""
        response = await self._request("DELETE", endpoint, **kwargs)
        return response.json()


class ConversationServiceClient(BaseServiceClient):
    """Client for Conversation Service (port 8003)"""

    def __init__(self, base_url: str = "http://localhost:8003"):
        super().__init__(base_url, timeout=20.0)

    async def generate_questions(
        self,
        job_description: str,
        job_title: Optional[str] = None,
        num_questions: int = 10,
        difficulty: str = "medium",
    ) -> dict[str, Any]:
        """
        Generate interview questions

        Args:
            job_description: Job description text
            job_title: Optional job title
            num_questions: Number of questions to generate
            difficulty: Question difficulty level

        Returns:
            Dict with questions array
        """
        return await self.post(
            "/conversation/generate-questions",
            json={
                "job_description": job_description,
                "job_title": job_title,
                "num_questions": num_questions,
                "difficulty": difficulty,
            },
        )


class VoiceServiceClient(BaseServiceClient):
    """Client for Voice Service (port 8002)"""

    def __init__(self, base_url: str = "http://localhost:8002"):
        super().__init__(base_url, timeout=60.0)

    async def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech

        Args:
            text: Text to convert

        Returns:
            Audio bytes (WAV format)
        """
        response = await self._request("POST", "/voice/tts", json={"text": text})
        return response.content

    async def speech_to_text(self, audio_file: bytes) -> str:
        """
        Convert speech to text

        Args:
            audio_file: Audio file bytes

        Returns:
            Transcribed text
        """
        files = {"audio_file": audio_file}
        response = await self._request("POST", "/voice/stt", files=files)
        return response.json()["text"]


class AvatarServiceClient(BaseServiceClient):
    """Client for Avatar Service (port 8001)"""

    def __init__(self, base_url: str = "http://localhost:8001"):
        super().__init__(base_url, timeout=120.0)

    async def generate_avatar(
        self,
        session_id: Optional[str] = None,
        turn_number: Optional[int] = None,
        still_mode: bool = True,
        expression_scale: float = 1.0,
        pose_style: int = 0,
    ) -> dict[str, Any]:
        """
        Generate avatar video

        Args:
            session_id: Optional session ID
            turn_number: Optional turn number
            still_mode: Still mode flag
            expression_scale: Expression scale
            pose_style: Pose style

        Returns:
            Dict with video_path and status
        """
        return await self.post(
            "/generate",
            json={
                "session_id": session_id,
                "turn_number": turn_number,
                "still_mode": still_mode,
                "expression_scale": expression_scale,
                "pose_style": pose_style,
            },
        )


class InterviewServiceClient(BaseServiceClient):
    """Client for Interview Service (port 8004)"""

    def __init__(self, base_url: str = "http://localhost:8004"):
        super().__init__(base_url, timeout=30.0)

    async def create_room(
        self, candidate_name: str, job_title: str, interview_type: str = "technical"
    ) -> dict[str, Any]:
        """
        Create interview room

        Args:
            candidate_name: Name of candidate
            job_title: Job title
            interview_type: Type of interview

        Returns:
            Dict with room_id, status, and jitsi_url
        """
        return await self.post(
            "/api/v1/rooms/create",
            json={
                "candidate_name": candidate_name,
                "job_title": job_title,
                "interview_type": interview_type,
            },
        )

    async def get_room(self, room_id: str) -> dict[str, Any]:
        """Get room details"""
        return await self.get(f"/api/v1/rooms/{room_id}")

    async def join_room(self, room_id: str) -> dict[str, Any]:
        """Join interview room"""
        return await self.post(f"/api/v1/rooms/{room_id}/join")

    async def end_room(self, room_id: str) -> dict[str, Any]:
        """End interview room"""
        return await self.delete(f"/api/v1/rooms/{room_id}/end")


class GenkitServiceClient(BaseServiceClient):
    """Client for Genkit Service (port 3400)"""

    def __init__(self, base_url: str = "http://localhost:3400"):
        super().__init__(base_url, timeout=30.0)

    async def generate_boolean_query(
        self, search_terms: str, platform: str = "linkedin"
    ) -> dict[str, Any]:
        """
        Generate boolean search query

        Args:
            search_terms: Search terms
            platform: Target platform

        Returns:
            Dict with query and explanation
        """
        return await self.post(
            "/generateBooleanQuery", json={"searchTerms": search_terms, "platform": platform}
        )

    async def generate_engagement_message(
        self, candidate_name: str, candidate_profile: str, job_description: str
    ) -> dict[str, Any]:
        """
        Generate personalized engagement message

        Args:
            candidate_name: Candidate name
            candidate_profile: Candidate profile summary
            job_description: Job description

        Returns:
            Dict with subject and message
        """
        return await self.post(
            "/generateEngagementMessage",
            json={
                "candidateName": candidate_name,
                "candidateProfile": candidate_profile,
                "jobDescription": job_description,
            },
        )

    async def score_candidate_quality(
        self, name: str, skills: list[str], experience: str
    ) -> dict[str, Any]:
        """
        Score candidate quality

        Args:
            name: Candidate name
            skills: List of skills
            experience: Experience summary

        Returns:
            Dict with score, reasoning, and qualityLevel
        """
        return await self.post(
            "/scoreCandidateQuality",
            json={"name": name, "skills": skills, "experience": experience},
        )


# Service client factory
class ServiceClients:
    """Factory for creating service clients"""

    def __init__(
        self,
        conversation_url: str = "http://localhost:8003",
        voice_url: str = "http://localhost:8002",
        avatar_url: str = "http://localhost:8001",
        interview_url: str = "http://localhost:8004",
        genkit_url: str = "http://localhost:3400",
    ):
        self.conversation = ConversationServiceClient(conversation_url)
        self.voice = VoiceServiceClient(voice_url)
        self.avatar = AvatarServiceClient(avatar_url)
        self.interview = InterviewServiceClient(interview_url)
        self.genkit = GenkitServiceClient(genkit_url)

    async def close_all(self):
        """Close all service clients"""
        await self.conversation.close()
        await self.voice.close()
        await self.avatar.close()
        await self.interview.close()
        await self.genkit.close()
