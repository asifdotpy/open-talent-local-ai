"""
Tests for Explainability Service
Following TDD principles - tests written before implementation
Port: 8013
Purpose: AI decision explanation, interpretability, transparency
"""

import pytest
import httpx
from typing import Dict, Any


@pytest.fixture
def explainability_service_url():
    return "http://localhost:8013"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=5.0)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}


class TestExplainabilityServiceBasics:
    @pytest.mark.asyncio
    async def test_service_health(self, explainability_service_url, async_client):
        response = await async_client.get(f"{explainability_service_url}/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_root_endpoint(self, explainability_service_url, async_client):
        response = await async_client.get(f"{explainability_service_url}/")
        assert response.status_code == 200


class TestDecisionExplanation:
    @pytest.mark.asyncio
    async def test_explain_score(self, explainability_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{explainability_service_url}/api/v1/explain/score",
            json={"interview_id": "int123", "score": 0.85},
            headers=auth_headers
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_explain_recommendation(self, explainability_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{explainability_service_url}/api/v1/explain/recommendation",
            json={"interview_id": "int123", "recommendation": "hire"},
            headers=auth_headers
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_explain_decision_path(self, explainability_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{explainability_service_url}/api/v1/explain/path",
            json={"interview_id": "int123"},
            headers=auth_headers
        )
        assert response.status_code in [200, 201]


class TestFeatureImportance:
    @pytest.mark.asyncio
    async def test_get_feature_importance(self, explainability_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{explainability_service_url}/api/v1/features/importance",
            headers=auth_headers
        )
        assert response.status_code in [200, 403]

    @pytest.mark.asyncio
    async def test_get_interview_feature_values(self, explainability_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{explainability_service_url}/api/v1/interviews/int123/features",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]


class TestTransparency:
    @pytest.mark.asyncio
    async def test_get_model_metadata(self, explainability_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{explainability_service_url}/api/v1/model/metadata",
            headers=auth_headers
        )
        assert response.status_code in [200, 403]

    @pytest.mark.asyncio
    async def test_get_decision_log(self, explainability_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{explainability_service_url}/api/v1/decisions/log",
            headers=auth_headers
        )
        assert response.status_code in [200, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
