"""
Tests for Granite Interview Service
Following TDD principles - tests written before implementation
Port: 8005
Purpose: Granite AI interview questions, scoring, analysis
"""

import pytest
import httpx
from typing import Dict, Any


@pytest.fixture
def granite_interview_service_url():
    return "http://localhost:8005"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=5.0)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def interview_session_data() -> Dict[str, Any]:
    return {
        "candidate_id": "candidate123",
        "job_id": "job123",
        "interview_type": "behavioral",
        "difficulty": "intermediate"
    }


@pytest.fixture
def answer_data() -> Dict[str, Any]:
    return {
        "question_id": "q123",
        "answer_text": "I would approach this by...",
        "confidence": 0.85
    }


class TestGraniteInterviewServiceBasics:
    @pytest.mark.asyncio
    async def test_service_health(self, granite_interview_service_url, async_client):
        response = await async_client.get(f"{granite_interview_service_url}/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_root_endpoint(self, granite_interview_service_url, async_client):
        response = await async_client.get(f"{granite_interview_service_url}/")
        assert response.status_code == 200


class TestQuestionGeneration:
    @pytest.mark.asyncio
    async def test_generate_questions(self, granite_interview_service_url, async_client, 
                                     interview_session_data, auth_headers):
        response = await async_client.post(
            f"{granite_interview_service_url}/api/v1/questions/generate",
            json=interview_session_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_get_question(self, granite_interview_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{granite_interview_service_url}/api/v1/questions/q123",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_next_question(self, granite_interview_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{granite_interview_service_url}/api/v1/interviews/int123/next-question",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]


class TestAnswerAnalysis:
    @pytest.mark.asyncio
    async def test_submit_answer(self, granite_interview_service_url, async_client, 
                                answer_data, auth_headers):
        response = await async_client.post(
            f"{granite_interview_service_url}/api/v1/interviews/int123/answers",
            json=answer_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_analyze_answer(self, granite_interview_service_url, async_client, 
                                 answer_data, auth_headers):
        response = await async_client.post(
            f"{granite_interview_service_url}/api/v1/interviews/int123/analyze",
            json=answer_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]
        if response.status_code == 200:
            data = response.json()
            assert "score" in data or "analysis" in data

    @pytest.mark.asyncio
    async def test_get_answer(self, granite_interview_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{granite_interview_service_url}/api/v1/interviews/int123/answers/ans123",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]


class TestInterviewSession:
    @pytest.mark.asyncio
    async def test_create_interview_session(self, granite_interview_service_url, async_client,
                                           interview_session_data, auth_headers):
        response = await async_client.post(
            f"{granite_interview_service_url}/api/v1/interviews",
            json=interview_session_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_get_interview_session(self, granite_interview_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{granite_interview_service_url}/api/v1/interviews/int123",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_end_interview_session(self, granite_interview_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{granite_interview_service_url}/api/v1/interviews/int123/end",
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]


class TestScoringAndAssessment:
    @pytest.mark.asyncio
    async def test_get_interview_score(self, granite_interview_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{granite_interview_service_url}/api/v1/interviews/int123/score",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_assessment_report(self, granite_interview_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{granite_interview_service_url}/api/v1/interviews/int123/assessment",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
