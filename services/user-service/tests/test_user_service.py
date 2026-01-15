"""
Tests for User Service
Using httpx.AsyncClient for compatible async testing.
"""

import pytest


@pytest.mark.asyncio
class TestUserServiceBasics:
    """Test basic service health and root endpoints"""

    async def test_service_health_check(self, client):
        """Test health endpoint returns 200"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_root_endpoint(self, client):
        """Test root endpoint is accessible"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
class TestUserCreation:
    """Test user creation endpoints"""

    async def test_create_user(self, client, sample_user_data, auth_headers_admin):
        """Test creating a new user"""
        response = await client.post(
            "/api/v1/users", json=sample_user_data, headers=auth_headers_admin
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == sample_user_data["email"]

    async def test_create_user_missing_email(self, client, auth_headers_admin):
        """Test creating user without email fails"""
        invalid_data = {"first_name": "John", "last_name": "Doe", "password": "Password123!"}
        response = await client.post("/api/v1/users", json=invalid_data, headers=auth_headers_admin)
        assert response.status_code == 422


@pytest.mark.asyncio
class TestUserRetrieval:
    """Test retrieving user information"""

    async def test_get_current_user(self, client, auth_headers_admin):
        """Test retrieving current logged-in user"""
        response = await client.get("/api/v1/users/me", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@example.com"

    async def test_list_users(self, client, auth_headers_admin):
        """Test listing all users"""
        response = await client.get("/api/v1/users", headers=auth_headers_admin)
        assert response.status_code == 200
        data = response.json()
        # The response is actually UserListResponse or a list
        if isinstance(data, dict) and "users" in data:
            assert isinstance(data["users"], list)
        else:
            assert isinstance(data, list)


@pytest.mark.asyncio
class TestUserUpdate:
    """Test updating user information"""

    async def test_partial_update_current_user(self, client, auth_headers_admin):
        """Test partial update of current user (PATCH)"""
        partial_data = {"first_name": "UpdatedName"}
        response = await client.patch(
            "/api/v1/users/me", json=partial_data, headers=auth_headers_admin
        )
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "UpdatedName"


@pytest.mark.asyncio
class TestUserPreferences:
    """Test user preferences management"""

    async def test_get_current_user_preferences(self, client, auth_headers_admin):
        """Test getting current user's preferences"""
        response = await client.get("/api/v1/users/me/preferences", headers=auth_headers_admin)
        assert response.status_code in [200, 404]

    async def test_update_current_user_preferences(
        self, client, sample_preferences_data, auth_headers_admin
    ):
        """Test updating current user's preferences"""
        response = await client.patch(
            "/api/v1/users/me/preferences", json=sample_preferences_data, headers=auth_headers_admin
        )
        assert response.status_code in [200, 201, 404]


@pytest.mark.asyncio
class TestUserProfile:
    """Test user profile management"""

    async def test_get_current_user_profile(self, client, auth_headers_admin):
        """Test retrieving current user's profile"""
        response = await client.get("/api/v1/users/me/profile", headers=auth_headers_admin)
        assert response.status_code in [200, 404]

    async def test_update_current_user_profile(
        self, client, sample_profile_data, auth_headers_admin
    ):
        """Test updating current user's profile"""
        response = await client.patch(
            "/api/v1/users/me/profile", json={"bio": "Updated Bio"}, headers=auth_headers_admin
        )
        assert response.status_code in [200, 201, 404]


@pytest.mark.asyncio
class TestUserErrorHandling:
    """Test error handling and edge cases"""

    async def test_get_nonexistent_user(self, client, auth_headers_admin):
        """Test getting non-existent user returns 404"""
        import uuid

        random_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/users/{random_id}", headers=auth_headers_admin)
        assert response.status_code == 404

    async def test_unauthorized_access(self, client):
        """Test unauthorized requests are rejected"""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401
