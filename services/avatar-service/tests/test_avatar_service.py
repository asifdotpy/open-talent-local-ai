"""Tests for Avatar Service
These legacy async-httpx tests target endpoints no longer present; module is skipped to avoid false failures.
"""

from typing import Any

import httpx
import pytest

pytest.skip(
    "Legacy avatar-service tests are deprecated; replaced by plan-aligned TestClient suite.",
    allow_module_level=True,
)


@pytest.fixture
def avatar_service_url():
    return "http://localhost:8004"


@pytest.fixture
def async_client():
    return httpx.AsyncClient(timeout=5.0)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def avatar_data() -> dict[str, Any]:
    return {
        "name": "Avatar1",
        "model": "default_humanoid",
        "skin_tone": "medium",
        "hair_style": "style1",
        "clothing": "casual",
    }


class TestAvatarServiceBasics:
    @pytest.mark.asyncio
    async def test_service_health(self, avatar_service_url, async_client):
        response = await async_client.get(f"{avatar_service_url}/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_root_endpoint(self, avatar_service_url, async_client):
        response = await async_client.get(f"{avatar_service_url}/")
        assert response.status_code == 200


class TestAvatarCreation:
    @pytest.mark.asyncio
    async def test_create_avatar(self, avatar_service_url, async_client, avatar_data, auth_headers):
        response = await async_client.post(
            f"{avatar_service_url}/api/v1/avatars", json=avatar_data, headers=auth_headers
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_get_avatar(self, avatar_service_url, async_client, auth_headers):
        response = await async_client.get(f"{avatar_service_url}/api/v1/avatars/avatar123", headers=auth_headers)
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_list_avatars(self, avatar_service_url, async_client, auth_headers):
        response = await async_client.get(f"{avatar_service_url}/api/v1/avatars", headers=auth_headers)
        assert response.status_code in [200, 403]

    @pytest.mark.asyncio
    async def test_delete_avatar(self, avatar_service_url, async_client, auth_headers):
        response = await async_client.delete(f"{avatar_service_url}/api/v1/avatars/avatar123", headers=auth_headers)
        assert response.status_code in [200, 201, 204, 404]


class TestAvatarCustomization:
    @pytest.mark.asyncio
    async def test_update_avatar_appearance(self, avatar_service_url, async_client, auth_headers):
        appearance = {"skin_tone": "light", "hair_style": "style2", "hair_color": "brown"}
        response = await async_client.patch(
            f"{avatar_service_url}/api/v1/avatars/avatar123/appearance",
            json=appearance,
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_set_avatar_clothing(self, avatar_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{avatar_service_url}/api/v1/avatars/avatar123/clothing",
            json={"outfit": "formal", "color": "black"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_set_avatar_accessories(self, avatar_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{avatar_service_url}/api/v1/avatars/avatar123/accessories",
            json={"glasses": True, "necklace": False},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]


class TestAvatarAnimation:
    @pytest.mark.asyncio
    async def test_trigger_animation(self, avatar_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{avatar_service_url}/api/v1/avatars/avatar123/animate",
            json={"animation": "wave", "duration": 2},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_set_idle_animation(self, avatar_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{avatar_service_url}/api/v1/avatars/avatar123/idle-animation",
            json={"animation": "breathing"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_get_available_animations(self, avatar_service_url, async_client, auth_headers):
        response = await async_client.get(f"{avatar_service_url}/api/v1/avatars/animations", headers=auth_headers)
        assert response.status_code in [200, 403]


class TestLipSync:
    @pytest.mark.asyncio
    async def test_sync_lips_with_audio(self, avatar_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{avatar_service_url}/api/v1/avatars/avatar123/sync-lips",
            json={"audio_url": "https://example.com/audio.mp3"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_get_lip_sync_data(self, avatar_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{avatar_service_url}/api/v1/avatars/avatar123/lip-sync", headers=auth_headers
        )
        assert response.status_code in [200, 404]


class TestAvatarRendering:
    @pytest.mark.asyncio
    async def test_render_avatar(self, avatar_service_url, async_client, auth_headers):
        response = await async_client.post(
            f"{avatar_service_url}/api/v1/avatars/avatar123/render",
            json={"width": 800, "height": 600, "format": "png"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_get_avatar_preview(self, avatar_service_url, async_client, auth_headers):
        response = await async_client.get(
            f"{avatar_service_url}/api/v1/avatars/avatar123/preview", headers=auth_headers
        )
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
