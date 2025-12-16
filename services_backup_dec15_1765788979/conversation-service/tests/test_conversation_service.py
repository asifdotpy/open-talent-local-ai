"""
Tests for Conversation Service
Following TDD principles - tests written before implementation
Port: 8014
Purpose: Real-time conversation management, chat history
"""

import pytest
import httpx
from typing import Dict, Any


@pytest.fixture
def conversation_service_url():
    return "http://localhost:8014"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=5.0)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def message_data() -> Dict[str, Any]:
    return {
        "text": "Hello, how are you?",
        "sender_id": "user123",
        "conversation_id": "conv123"
    }


class TestConversationServiceBasics:
    @pytest.mark.asyncio
    async def test_service_health(self, conversation_service_url, async_client):
        response = await async_client.get(f"{conversation_service_url}/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_root_endpoint(self, conversation_service_url, async_client):
        response = await async_client.get(f"{conversation_service_url}/")
        assert response.status_code == 200


class TestConversationManagement:
    @pytest.mark.asyncio
    async def test_create_conversation(self, conversation_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{conversation_service_url}/api/v1/conversations",
            json={"participants": ["user1", "user2"]},
            headers=auth_headers
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_get_conversation(self, conversation_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{conversation_service_url}/api/v1/conversations/conv123",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_list_conversations(self, conversation_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{conversation_service_url}/api/v1/conversations",
            headers=auth_headers
        )
        assert response.status_code in [200, 403]

    @pytest.mark.asyncio
    async def test_end_conversation(self, conversation_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{conversation_service_url}/api/v1/conversations/conv123/end",
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]


class TestMessaging:
    @pytest.mark.asyncio
    async def test_send_message(self, conversation_service_url, async_client, message_data, auth_headers):
        response = await async_client.post(
            f"{conversation_service_url}/api/v1/messages",
            json=message_data,
            headers=auth_headers
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_get_messages(self, conversation_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{conversation_service_url}/api/v1/conversations/conv123/messages",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_message(self, conversation_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{conversation_service_url}/api/v1/messages/msg123",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_edit_message(self, conversation_service_url, async_client, auth_headers):
        response = await async_client.patch(
            f"{conversation_service_url}/api/v1/messages/msg123",
            json={"text": "Edited message"},
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_delete_message(self, conversation_service_url, async_client, auth_headers):
        response = await async_client.delete(
            f"{conversation_service_url}/api/v1/messages/msg123",
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 204, 404]


class TestConversationHistory:
    @pytest.mark.asyncio
    async def test_get_conversation_history(self, conversation_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{conversation_service_url}/api/v1/conversations/conv123/history",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_clear_history(self, conversation_service_url, async_client, auth_headers):
        response = await async_client.delete(
            f"{conversation_service_url}/api/v1/conversations/conv123/history",
            headers=auth_headers
        )
        assert response.status_code in [200, 201, 204, 404]

    @pytest.mark.asyncio
    async def test_export_conversation(self, conversation_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{conversation_service_url}/api/v1/conversations/conv123/export",
            headers=auth_headers
        )
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
