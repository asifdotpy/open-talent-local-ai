"""
Integration tests for User Service API endpoints.

Tests verify:
- Authentication requirements
- CRUD operations
- Tenant isolation
- Role-based access control
- Error handling
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from uuid import uuid4

from app.utils import JWTClaims


@pytest.mark.integration
@pytest.mark.asyncio
class TestHealthEndpoint:
    """Test health check endpoint."""

    async def test_health_check_no_auth(self, test_client: AsyncClient):
        """Health endpoint should not require authentication."""
        response = await test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "user"
        assert data["status"] == "healthy"


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserEndpoints:
    """Test user CRUD endpoints."""

    async def test_list_users_requires_auth(self, test_client: AsyncClient):
        """Listing users requires authentication."""
        response = await test_client.get("/api/v1/users")

        assert response.status_code == 401
        assert "authorization" in response.json()["detail"].lower()

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_list_users_with_auth(
        self,
        mock_verify,
        test_client: AsyncClient,
        admin_token: str,
    ):
        """Admin can list users."""
        mock_verify.return_value = {"valid": True, "email": "admin@example.com"}

        response = await test_client.get(
            "/api/v1/users", headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_create_user(
        self,
        mock_verify,
        test_client: AsyncClient,
        admin_token: str,
        sample_user_data: dict,
    ):
        """Admin can create users."""
        mock_verify.return_value = {"valid": True, "email": "admin@example.com"}

        response = await test_client.post(
            "/api/v1/users",
            json=sample_user_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["full_name"] == sample_user_data["full_name"]
        assert "id" in data
        assert "created_at" in data

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_get_user_by_id(
        self,
        mock_verify,
        test_client: AsyncClient,
        admin_token: str,
        sample_user_data: dict,
    ):
        """Get user by ID."""
        mock_verify.return_value = {"valid": True, "email": "admin@example.com"}

        # Create user first
        create_response = await test_client.post(
            "/api/v1/users",
            json=sample_user_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        user_id = create_response.json()["id"]

        # Get user
        response = await test_client.get(
            f"/api/v1/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == sample_user_data["email"]

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_get_nonexistent_user(
        self,
        mock_verify,
        test_client: AsyncClient,
        admin_token: str,
    ):
        """Get nonexistent user returns 404."""
        mock_verify.return_value = {"valid": True, "email": "admin@example.com"}

        fake_id = str(uuid4())
        response = await test_client.get(
            f"/api/v1/users/{fake_id}", headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_update_user(
        self,
        mock_verify,
        test_client: AsyncClient,
        admin_token: str,
        sample_user_data: dict,
    ):
        """Admin can update users."""
        mock_verify.return_value = {"valid": True, "email": "admin@example.com"}

        # Create user first
        create_response = await test_client.post(
            "/api/v1/users",
            json=sample_user_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        user_id = create_response.json()["id"]

        # Update user
        update_data = {"full_name": "Updated Name", "status": "inactive"}
        response = await test_client.put(
            f"/api/v1/users/{user_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["status"] == "inactive"

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_delete_user(
        self,
        mock_verify,
        test_client: AsyncClient,
        admin_token: str,
        sample_user_data: dict,
    ):
        """Admin can delete users."""
        mock_verify.return_value = {"valid": True, "email": "admin@example.com"}

        # Create user first
        create_response = await test_client.post(
            "/api/v1/users",
            json=sample_user_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        user_id = create_response.json()["id"]

        # Delete user
        response = await test_client.delete(
            f"/api/v1/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200

        # Verify user is deleted
        get_response = await test_client.get(
            f"/api/v1/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_response.status_code == 404

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_recruiter_tenant_isolation(
        self,
        mock_verify,
        test_client: AsyncClient,
        recruiter_token: str,
    ):
        """Recruiter can only see users in their tenant."""
        # Mock recruiter JWT claims
        mock_verify.return_value = {"valid": True, "email": "recruiter@tenant1.com"}

        response = await test_client.get(
            "/api/v1/users", headers={"Authorization": f"Bearer {recruiter_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # All returned users should be from same tenant
        for user in data:
            assert user["tenant_id"] == "tenant1"


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserProfileEndpoints:
    """Test user profile endpoints."""

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_create_user_profile(
        self,
        mock_verify,
        test_client: AsyncClient,
        admin_token: str,
        sample_user_data: dict,
        sample_profile_data: dict,
    ):
        """Create user profile."""
        mock_verify.return_value = {"valid": True, "email": "admin@example.com"}

        # Create user first
        user_response = await test_client.post(
            "/api/v1/users",
            json=sample_user_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        user_id = user_response.json()["id"]

        # Create profile
        response = await test_client.post(
            f"/api/v1/users/{user_id}/profile",
            json=sample_profile_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == sample_profile_data["phone"]
        assert data["location"] == sample_profile_data["location"]

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_get_user_profile(
        self,
        mock_verify,
        test_client: AsyncClient,
        admin_token: str,
        sample_user_data: dict,
        sample_profile_data: dict,
    ):
        """Get user profile."""
        mock_verify.return_value = {"valid": True, "email": "admin@example.com"}

        # Create user and profile
        user_response = await test_client.post(
            "/api/v1/users",
            json=sample_user_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        user_id = user_response.json()["id"]

        await test_client.post(
            f"/api/v1/users/{user_id}/profile",
            json=sample_profile_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # Get profile
        response = await test_client.get(
            f"/api/v1/users/{user_id}/profile", headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == sample_profile_data["phone"]


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserPreferencesEndpoints:
    """Test user preferences endpoints."""

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_create_user_preferences(
        self,
        mock_verify,
        test_client: AsyncClient,
        candidate_token: str,
        sample_user_data: dict,
        sample_preferences_data: dict,
    ):
        """Candidate can create their own preferences."""
        mock_verify.return_value = {"valid": True, "email": "candidate@example.com"}

        # Create user first (as admin)
        admin_token = candidate_token  # Reuse for simplicity
        user_response = await test_client.post(
            "/api/v1/users",
            json={**sample_user_data, "email": "candidate@example.com"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        user_id = user_response.json()["id"]

        # Create preferences
        response = await test_client.post(
            f"/api/v1/users/{user_id}/preferences",
            json=sample_preferences_data,
            headers={"Authorization": f"Bearer {candidate_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["language"] == sample_preferences_data["language"]
        assert data["theme"] == sample_preferences_data["theme"]


@pytest.mark.integration
@pytest.mark.asyncio
class TestSearchAndFilters:
    """Test search and filter functionality."""

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_search_users_by_email(
        self,
        mock_verify,
        test_client: AsyncClient,
        admin_token: str,
    ):
        """Search users by email."""
        mock_verify.return_value = {"valid": True, "email": "admin@example.com"}

        # Create test users
        await test_client.post(
            "/api/v1/users",
            json={
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "role": "candidate",
                "status": "active",
                "tenant_id": "tenant1",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # Search by email
        response = await test_client.get(
            "/api/v1/users?search=john.doe", headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any("john.doe" in user["email"].lower() for user in data)

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_filter_users_by_role(
        self,
        mock_verify,
        test_client: AsyncClient,
        admin_token: str,
    ):
        """Filter users by role."""
        mock_verify.return_value = {"valid": True, "email": "admin@example.com"}

        response = await test_client.get(
            "/api/v1/users?role=candidate", headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # All returned users should be candidates
        for user in data:
            assert user["role"] == "candidate"

    @patch("app.utils.verify_jwt_with_security_service")
    async def test_pagination(
        self,
        mock_verify,
        test_client: AsyncClient,
        admin_token: str,
    ):
        """Test pagination parameters."""
        mock_verify.return_value = {"valid": True, "email": "admin@example.com"}

        response = await test_client.get(
            "/api/v1/users?skip=0&limit=5", headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
