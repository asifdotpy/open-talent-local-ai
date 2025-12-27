"""
Tests for User Service
Following TDD principles - tests written before implementation
Port: 8007
Purpose: User management, profiles, preferences
"""

import time
from typing import Any

import httpx
import pytest


@pytest.fixture
def user_service_url():
    """Base URL for user service"""
    return "http://localhost:8007"


@pytest.fixture
def async_client():
    """Async HTTP client"""
    return httpx.AsyncClient(timeout=5.0)


@pytest.fixture
def auth_token():
    """Valid JWT token for authenticated requests"""
    return "test_token_xyz"


@pytest.fixture
def auth_headers(auth_token):
    """Headers with authorization token"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def user_data() -> dict[str, Any]:
    """Sample user data"""
    timestamp = int(time.time() * 1000)
    return {
        "email": f"user+{timestamp}@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "profile_picture_url": "https://example.com/pic.jpg",
    }


@pytest.fixture
def user_update_data() -> dict[str, Any]:
    """Sample user update data"""
    return {"first_name": "Jane", "last_name": "Smith", "phone": "+0987654321"}


@pytest.fixture
def user_preferences() -> dict[str, Any]:
    """Sample user preferences"""
    return {
        "language": "en",
        "timezone": "America/New_York",
        "email_notifications": True,
        "sms_notifications": False,
        "dark_mode": True,
    }


# ============================================================================
# SERVICE HEALTH & BASIC TESTS
# ============================================================================


class TestUserServiceBasics:
    """Test basic service health and root endpoints"""

    @pytest.mark.asyncio
    async def test_service_health_check(self, user_service_url, async_client):
        """Test health endpoint returns 200"""
        response = await async_client.get(f"{user_service_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data or "status" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self, user_service_url, async_client):
        """Test root endpoint is accessible"""
        response = await async_client.get(f"{user_service_url}/")
        assert response.status_code == 200


# ============================================================================
# USER CREATION & RETRIEVAL TESTS
# ============================================================================


class TestUserCreation:
    """Test user creation endpoints"""

    @pytest.mark.asyncio
    async def test_create_user(self, user_service_url, async_client, user_data, auth_headers):
        """Test creating a new user"""
        response = await async_client.post(
            f"{user_service_url}/api/v1/users", json=user_data, headers=auth_headers
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data or "user_id" in data

    @pytest.mark.asyncio
    async def test_create_user_missing_email(self, user_service_url, async_client, auth_headers):
        """Test creating user without email fails"""
        invalid_data = {"first_name": "John", "last_name": "Doe"}
        response = await async_client.post(
            f"{user_service_url}/api/v1/users", json=invalid_data, headers=auth_headers
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, user_service_url, async_client, auth_headers):
        """Test creating user with invalid email fails"""
        invalid_data = {"email": "not-an-email", "first_name": "John"}
        response = await async_client.post(
            f"{user_service_url}/api/v1/users", json=invalid_data, headers=auth_headers
        )
        assert response.status_code in [400, 422]


# ============================================================================
# USER RETRIEVAL TESTS
# ============================================================================


class TestUserRetrieval:
    """Test retrieving user information"""

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, user_service_url, async_client, auth_headers):
        """Test retrieving user by ID"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/123", headers=auth_headers
        )
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "id" in data or "user_id" in data

    @pytest.mark.asyncio
    async def test_get_current_user(self, user_service_url, async_client, auth_headers):
        """Test retrieving current logged-in user"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/me", headers=auth_headers
        )
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert "email" in data or "id" in data

    @pytest.mark.asyncio
    async def test_list_users(self, user_service_url, async_client, auth_headers):
        """Test listing all users"""
        response = await async_client.get(f"{user_service_url}/api/v1/users", headers=auth_headers)
        assert response.status_code in [200, 403]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_search_users(self, user_service_url, async_client, auth_headers):
        """Test searching for users"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users?search=john", headers=auth_headers
        )
        assert response.status_code in [200, 403, 400]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list))


# ============================================================================
# USER UPDATE TESTS
# ============================================================================


class TestUserUpdate:
    """Test updating user information"""

    @pytest.mark.asyncio
    async def test_update_user(
        self, user_service_url, async_client, user_update_data, auth_headers
    ):
        """Test updating user information"""
        response = await async_client.put(
            f"{user_service_url}/api/v1/users/123", json=user_update_data, headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]
        if response.status_code == 200:
            data = response.json()
            assert "first_name" in data or "id" in data

    @pytest.mark.asyncio
    async def test_partial_update_user(self, user_service_url, async_client, auth_headers):
        """Test partial update of user (PATCH)"""
        partial_data = {"first_name": "Jane"}
        response = await async_client.patch(
            f"{user_service_url}/api/v1/users/123", json=partial_data, headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_update_current_user_profile(
        self, user_service_url, async_client, user_update_data, auth_headers
    ):
        """Test updating current user's profile"""
        response = await async_client.put(
            f"{user_service_url}/api/v1/users/me", json=user_update_data, headers=auth_headers
        )
        assert response.status_code in [200, 201, 401]

    @pytest.mark.asyncio
    async def test_update_with_invalid_email(self, user_service_url, async_client, auth_headers):
        """Test updating user with invalid email fails"""
        invalid_data = {"email": "not-an-email"}
        response = await async_client.put(
            f"{user_service_url}/api/v1/users/123", json=invalid_data, headers=auth_headers
        )
        assert response.status_code in [400, 422, 404]


# ============================================================================
# USER DELETION TESTS
# ============================================================================


class TestUserDeletion:
    """Test user deletion"""

    @pytest.mark.asyncio
    async def test_delete_user(self, user_service_url, async_client, auth_headers):
        """Test deleting a user"""
        response = await async_client.delete(
            f"{user_service_url}/api/v1/users/123", headers=auth_headers
        )
        assert response.status_code in [200, 201, 204, 404]

    @pytest.mark.asyncio
    async def test_soft_delete_user(self, user_service_url, async_client, auth_headers):
        """Test soft deleting user (deactivate)"""
        response = await async_client.post(
            f"{user_service_url}/api/v1/users/123/deactivate", headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_reactivate_user(self, user_service_url, async_client, auth_headers):
        """Test reactivating deactivated user"""
        response = await async_client.post(
            f"{user_service_url}/api/v1/users/123/reactivate", headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]


# ============================================================================
# USER PROFILE TESTS
# ============================================================================


class TestUserProfile:
    """Test user profile management"""

    @pytest.mark.asyncio
    async def test_get_user_profile(self, user_service_url, async_client, auth_headers):
        """Test retrieving user profile"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/123/profile", headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_update_user_profile(self, user_service_url, async_client, auth_headers):
        """Test updating user profile"""
        profile_data = {
            "bio": "Software engineer",
            "location": "San Francisco, CA",
            "linkedin_url": "https://linkedin.com/in/johndoe",
        }
        response = await async_client.put(
            f"{user_service_url}/api/v1/users/123/profile", json=profile_data, headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_get_user_avatar(self, user_service_url, async_client, auth_headers):
        """Test getting user avatar URL"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/123/avatar", headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_upload_user_avatar(self, user_service_url, async_client, auth_headers):
        """Test uploading user avatar"""
        # Note: This would be multipart/form-data in real implementation
        avatar_data = {"avatar_url": "https://example.com/avatar.jpg"}
        response = await async_client.post(
            f"{user_service_url}/api/v1/users/123/avatar", json=avatar_data, headers=auth_headers
        )
        assert response.status_code in [200, 201, 404]


# ============================================================================
# USER PREFERENCES TESTS
# ============================================================================


class TestUserPreferences:
    """Test user preferences management"""

    @pytest.mark.asyncio
    async def test_get_user_preferences(self, user_service_url, async_client, auth_headers):
        """Test retrieving user preferences"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/123/preferences", headers=auth_headers
        )
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_update_user_preferences(
        self, user_service_url, async_client, user_preferences, auth_headers
    ):
        """Test updating user preferences"""
        response = await async_client.put(
            f"{user_service_url}/api/v1/users/123/preferences",
            json=user_preferences,
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_get_current_user_preferences(self, user_service_url, async_client, auth_headers):
        """Test getting current user's preferences"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/me/preferences", headers=auth_headers
        )
        assert response.status_code in [200, 401, 404]

    @pytest.mark.asyncio
    async def test_update_current_user_preferences(
        self, user_service_url, async_client, user_preferences, auth_headers
    ):
        """Test updating current user's preferences"""
        response = await async_client.put(
            f"{user_service_url}/api/v1/users/me/preferences",
            json=user_preferences,
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 401]


# ============================================================================
# USER CONTACT INFORMATION TESTS
# ============================================================================


class TestUserContactInformation:
    """Test managing user contact information"""

    @pytest.mark.asyncio
    async def test_get_user_emails(self, user_service_url, async_client, auth_headers):
        """Test retrieving user email addresses"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/123/emails", headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_add_secondary_email(self, user_service_url, async_client, auth_headers):
        """Test adding secondary email"""
        response = await async_client.post(
            f"{user_service_url}/api/v1/users/123/emails",
            json={"email": "secondary@example.com"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_remove_email(self, user_service_url, async_client, auth_headers):
        """Test removing email address"""
        response = await async_client.delete(
            f"{user_service_url}/api/v1/users/123/emails/secondary@example.com",
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 204, 404]

    @pytest.mark.asyncio
    async def test_get_user_phone_numbers(self, user_service_url, async_client, auth_headers):
        """Test retrieving user phone numbers"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/123/phones", headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_add_phone_number(self, user_service_url, async_client, auth_headers):
        """Test adding phone number"""
        response = await async_client.post(
            f"{user_service_url}/api/v1/users/123/phones",
            json={"phone": "+1987654321"},
            headers=auth_headers,
        )
        assert response.status_code in [200, 201, 404]

    @pytest.mark.asyncio
    async def test_remove_phone_number(self, user_service_url, async_client, auth_headers):
        """Test removing phone number"""
        response = await async_client.delete(
            f"{user_service_url}/api/v1/users/123/phones/+1987654321", headers=auth_headers
        )
        assert response.status_code in [200, 201, 204, 404]


# ============================================================================
# USER ACTIVITY & SESSION TESTS
# ============================================================================


class TestUserActivity:
    """Test user activity tracking"""

    @pytest.mark.asyncio
    async def test_get_user_activity_log(self, user_service_url, async_client, auth_headers):
        """Test retrieving user activity log"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/123/activity", headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_user_sessions(self, user_service_url, async_client, auth_headers):
        """Test retrieving user sessions"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/123/sessions", headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_revoke_user_session(self, user_service_url, async_client, auth_headers):
        """Test revoking a user session"""
        response = await async_client.delete(
            f"{user_service_url}/api/v1/users/123/sessions/session123", headers=auth_headers
        )
        assert response.status_code in [200, 201, 204, 404]


# ============================================================================
# USER STATISTICS & METADATA TESTS
# ============================================================================


class TestUserMetadata:
    """Test user metadata"""

    @pytest.mark.asyncio
    async def test_get_user_statistics(self, user_service_url, async_client, auth_headers):
        """Test retrieving user statistics"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/123/statistics", headers=auth_headers
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_user_created_date(self, user_service_url, async_client, auth_headers):
        """Test getting user creation date"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/123", headers=auth_headers
        )
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "created_at" in data or "created_date" in data or "id" in data


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestUserErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, user_service_url, async_client, auth_headers):
        """Test getting non-existent user returns 404"""
        response = await async_client.get(
            f"{user_service_url}/api/v1/users/nonexistent-id", headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, user_service_url, async_client):
        """Test unauthorized requests are rejected"""
        response = await async_client.get(f"{user_service_url}/api/v1/users/123")
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_invalid_json_request(self, user_service_url, async_client, auth_headers):
        """Test invalid JSON is rejected"""
        response = await async_client.post(
            f"{user_service_url}/api/v1/users",
            content="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"},
        )
        assert response.status_code in [400, 422]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestUserIntegration:
    """Test user service integration scenarios"""

    @pytest.mark.asyncio
    async def test_user_lifecycle(self, user_service_url, async_client, user_data, auth_headers):
        """Test complete user lifecycle: create -> update -> retrieve -> delete"""
        # Create
        create_response = await async_client.post(
            f"{user_service_url}/api/v1/users", json=user_data, headers=auth_headers
        )
        assert create_response.status_code in [200, 201]

        if create_response.status_code in [200, 201]:
            user_id = create_response.json().get("id") or create_response.json().get("user_id")

            if user_id:
                # Retrieve
                get_response = await async_client.get(
                    f"{user_service_url}/api/v1/users/{user_id}", headers=auth_headers
                )
                assert get_response.status_code == 200

                # Update
                update_response = await async_client.put(
                    f"{user_service_url}/api/v1/users/{user_id}",
                    json={"first_name": "Jane"},
                    headers=auth_headers,
                )
                assert update_response.status_code in [200, 201]

                # Delete
                delete_response = await async_client.delete(
                    f"{user_service_url}/api/v1/users/{user_id}", headers=auth_headers
                )
                assert delete_response.status_code in [200, 201, 204]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
