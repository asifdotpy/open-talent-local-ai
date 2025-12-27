"""
Tests for Security Service
Following TDD principles - tests written before implementation
Port: 8010
Purpose: Authentication, Authorization, Permissions, MFA, Encryption
"""

import importlib
import os
import time
from typing import Any

import httpx
import pytest
from httpx import ASGITransport

# Disable rate limiting for these tests to avoid 429 noise
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")


def _load_app():
    """Load a fresh FastAPI app instance for in-process testing."""
    os.environ.setdefault("SECURITY_SECRET_KEY", "TEST_SECRET_KEY")
    os.environ.setdefault("RATE_LIMIT_RULE", "100/minute")
    os.environ.setdefault("CORS_ALLOW_ORIGINS", "http://testserver")
    if "services.security-service.main" in importlib.sys.modules:
        del importlib.sys.modules["services.security-service.main"]
    spec = importlib.util.spec_from_file_location(
        "security_service_main",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py")),
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.app


@pytest.fixture
def security_service_url():
    """Base URL for security service"""
    return "http://testserver"


@pytest.fixture
async def async_client():
    """Async HTTP client wired to the app via ASGI transport (no external server)."""
    app = _load_app()
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver", timeout=5.0) as client:
        yield client


@pytest.fixture
def valid_credentials() -> dict[str, Any]:
    """Valid login credentials"""
    return {
        "email": "user@example.com",
        "password": "SecurePassword123!"
    }


@pytest.fixture
def invalid_credentials() -> dict[str, Any]:
    """Invalid login credentials"""
    return {
        "email": "user@example.com",
        "password": "wrongpassword"
    }


@pytest.fixture
def new_user_data() -> dict[str, Any]:
    """New user registration data with unique email"""
    timestamp = int(time.time() * 1000)
    return {
        "email": f"newuser+{timestamp}@example.com",
        "password": "SecurePassword123!",
        "first_name": "John",
        "last_name": "Doe"
    }


# ============================================================================
# SERVICE HEALTH & BASIC TESTS
# ============================================================================

class TestSecurityServiceBasics:
    """Test basic service health and root endpoints"""

    @pytest.mark.asyncio
    async def test_service_health_check(self, security_service_url, async_client):
        """Test health endpoint returns 200"""
        response = await async_client.get(f"{security_service_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data or "status" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self, security_service_url, async_client):
        """Test root endpoint is accessible"""
        response = await async_client.get(f"{security_service_url}/")
        assert response.status_code == 200


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Test user authentication functionality"""

    @pytest.mark.asyncio
    async def test_login_with_valid_credentials(self, security_service_url, async_client, valid_credentials):
        """Test login with valid credentials returns token"""
        response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "token" in data or "access_token" in data

    @pytest.mark.asyncio
    async def test_login_with_invalid_credentials(self, security_service_url, async_client, invalid_credentials):
        """Test login with invalid credentials fails"""
        response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=invalid_credentials
        )
        assert response.status_code in [401, 403, 400]

    @pytest.mark.asyncio
    async def test_login_missing_email(self, security_service_url, async_client):
        """Test login without email fails"""
        response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json={"password": "test123"}
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_login_missing_password(self, security_service_url, async_client):
        """Test login without password fails"""
        response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json={"email": "user@example.com"}
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_logout_endpoint(self, security_service_url, async_client, valid_credentials):
        """Test logout endpoint removes session"""
        # First login
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )

        if login_response.status_code == 200:
            token = login_response.json().get("token") or login_response.json().get("access_token")

            # Then logout
            headers = {"Authorization": f"Bearer {token}"}
            logout_response = await async_client.post(
                f"{security_service_url}/api/v1/auth/logout",
                headers=headers
            )
            assert logout_response.status_code in [200, 201, 204]


# ============================================================================
# REGISTRATION TESTS
# ============================================================================

class TestUserRegistration:
    """Test user registration functionality"""

    @pytest.mark.asyncio
    async def test_register_new_user(self, security_service_url, async_client, new_user_data):
        """Test registering a new user"""
        response = await async_client.post(
            f"{security_service_url}/api/v1/auth/register",
            json=new_user_data
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "user" in data or "id" in data or "email" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, security_service_url, async_client, new_user_data):
        """Test that duplicate email registration fails"""
        # First registration
        await async_client.post(
            f"{security_service_url}/api/v1/auth/register",
            json=new_user_data
        )

        # Second registration with same email
        response = await async_client.post(
            f"{security_service_url}/api/v1/auth/register",
            json=new_user_data
        )
        assert response.status_code in [400, 409]

    @pytest.mark.asyncio
    async def test_register_missing_email(self, security_service_url, async_client):
        """Test registration without email fails"""
        data = {
            "password": "SecurePassword123!",
            "first_name": "John"
        }
        response = await async_client.post(
            f"{security_service_url}/api/v1/auth/register",
            json=data
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_register_missing_password(self, security_service_url, async_client):
        """Test registration without password fails"""
        data = {
            "email": "user@example.com",
            "first_name": "John"
        }
        response = await async_client.post(
            f"{security_service_url}/api/v1/auth/register",
            json=data
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, security_service_url, async_client):
        """Test registration with invalid email fails"""
        data = {
            "email": "not-an-email",
            "password": "SecurePassword123!",
            "first_name": "John"
        }
        response = await async_client.post(
            f"{security_service_url}/api/v1/auth/register",
            json=data
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_register_weak_password(self, security_service_url, async_client):
        """Test registration with weak password fails"""
        data = {
            "email": "user@example.com",
            "password": "123",  # Too weak
            "first_name": "John"
        }
        response = await async_client.post(
            f"{security_service_url}/api/v1/auth/register",
            json=data
        )
        assert response.status_code in [400, 422]


# ============================================================================
# TOKEN & SESSION TESTS
# ============================================================================

class TestTokenManagement:
    """Test token and session management"""

    @pytest.mark.asyncio
    async def test_verify_token(self, security_service_url, async_client, valid_credentials):
        """Test token verification"""
        # Get token
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )

        if login_response.status_code == 200:
            token = login_response.json().get("token") or login_response.json().get("access_token")

            # Verify token
            response = await async_client.post(
                f"{security_service_url}/api/v1/auth/verify",
                json={"token": token}
            )
            assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_refresh_token(self, security_service_url, async_client, valid_credentials):
        """Test token refresh"""
        # Get token
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )

        if login_response.status_code == 200:
            refresh_token = login_response.json().get("refresh_token")

            if refresh_token:
                # Refresh token
                response = await async_client.post(
                    f"{security_service_url}/api/v1/auth/refresh",
                    json={"refresh_token": refresh_token}
                )
                assert response.status_code in [200, 201]
                assert "token" in response.json() or "access_token" in response.json()

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, security_service_url, async_client):
        """Test that invalid token is rejected"""
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        response = await async_client.get(
            f"{security_service_url}/api/v1/auth/profile",
            headers=headers
        )
        assert response.status_code in [401, 403]


# ============================================================================
# MFA (MULTI-FACTOR AUTHENTICATION) TESTS
# ============================================================================

class TestMultiFactorAuth:
    """Test MFA setup and verification"""

    @pytest.mark.asyncio
    async def test_setup_mfa(self, security_service_url, async_client, valid_credentials):
        """Test setting up MFA"""
        # Login first
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )

        if login_response.status_code == 200:
            token = login_response.json().get("token") or login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            # Setup MFA
            response = await async_client.post(
                f"{security_service_url}/api/v1/auth/mfa/setup",
                headers=headers
            )
            assert response.status_code in [200, 201]
            data = response.json()
            assert "secret" in data or "qr_code" in data

    @pytest.mark.asyncio
    async def test_verify_mfa(self, security_service_url, async_client, valid_credentials):
        """Test verifying MFA code"""
        # Login first
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )

        if login_response.status_code == 200:
            token = login_response.json().get("token") or login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            # Verify MFA (even if fails, endpoint should exist)
            response = await async_client.post(
                f"{security_service_url}/api/v1/auth/mfa/verify",
                json={"code": "123456"},
                headers=headers
            )
            # Should either succeed or return 400/422 for invalid code
            assert response.status_code in [200, 201, 400, 422]

    @pytest.mark.asyncio
    async def test_disable_mfa(self, security_service_url, async_client, valid_credentials):
        """Test disabling MFA"""
        # Login first
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )

        if login_response.status_code == 200:
            token = login_response.json().get("token") or login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            # Disable MFA
            response = await async_client.delete(
                f"{security_service_url}/api/v1/auth/mfa",
                headers=headers
            )
            assert response.status_code in [200, 201, 204]


# ============================================================================
# PERMISSION & AUTHORIZATION TESTS
# ============================================================================

class TestPermissions:
    """Test permission and authorization"""

    @pytest.mark.asyncio
    async def test_get_user_permissions(self, security_service_url, async_client, valid_credentials):
        """Test getting user permissions"""
        # Login first
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )

        if login_response.status_code == 200:
            token = login_response.json().get("token") or login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            # Get permissions
            response = await async_client.get(
                f"{security_service_url}/api/v1/auth/permissions",
                headers=headers
            )
            assert response.status_code == 200
            assert isinstance(response.json(), (dict, list))

    @pytest.mark.asyncio
    async def test_check_permission(self, security_service_url, async_client, valid_credentials):
        """Test checking if user has specific permission"""
        # Login first
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )

        if login_response.status_code == 200:
            token = login_response.json().get("token") or login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            # Check permission
            response = await async_client.post(
                f"{security_service_url}/api/v1/auth/permissions/check",
                json={"permission": "view_interviews"},
                headers=headers
            )
            assert response.status_code in [200, 201, 400, 403]


# ============================================================================
# ENCRYPTION & DATA SECURITY TESTS
# ============================================================================

class TestEncryption:
    """Test encryption functionality"""

    @pytest.mark.asyncio
    async def test_encrypt_data(self, security_service_url, async_client):
        """Test encrypting data"""
        data = {
            "data": "sensitive information"
        }
        response = await async_client.post(
            f"{security_service_url}/api/v1/encrypt",
            json=data
        )
        assert response.status_code in [200, 201]
        encrypted = response.json()
        assert "encrypted" in encrypted or "ciphertext" in encrypted

    @pytest.mark.asyncio
    async def test_decrypt_data(self, security_service_url, async_client):
        """Test decrypting data"""
        # First encrypt
        data = {"data": "sensitive information"}
        encrypt_response = await async_client.post(
            f"{security_service_url}/api/v1/encrypt",
            json=data
        )

        if encrypt_response.status_code == 200:
            encrypted_data = encrypt_response.json().get("encrypted") or encrypt_response.json().get("ciphertext")

            # Then decrypt
            response = await async_client.post(
                f"{security_service_url}/api/v1/decrypt",
                json={"encrypted": encrypted_data}
            )
            assert response.status_code in [200, 201]
            assert "data" in response.json() or "plaintext" in response.json()


# ============================================================================
# PASSWORD MANAGEMENT TESTS
# ============================================================================

class TestPasswordManagement:
    """Test password change and recovery"""

    @pytest.mark.asyncio
    async def test_change_password(self, security_service_url, async_client, valid_credentials):
        """Test changing password"""
        # Login first
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )

        if login_response.status_code == 200:
            token = login_response.json().get("token") or login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            # Change password
            response = await async_client.post(
                f"{security_service_url}/api/v1/auth/password/change",
                json={
                    "current_password": valid_credentials["password"],
                    "new_password": "NewSecurePassword123!"
                },
                headers=headers
            )
            assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_request_password_reset(self, security_service_url, async_client):
        """Test requesting password reset"""
        response = await async_client.post(
            f"{security_service_url}/api/v1/auth/password/reset-request",
            json={"email": "user@example.com"}
        )
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_reset_password_with_token(self, security_service_url, async_client):
        """Test resetting password with reset token"""
        response = await async_client.post(
            f"{security_service_url}/api/v1/auth/password/reset",
            json={
                "token": "reset_token_xyz",
                "new_password": "NewSecurePassword123!"
            }
        )
        # Should either succeed or return 400 for invalid token
        assert response.status_code in [200, 201, 400, 422]


# ============================================================================
# ROLE MANAGEMENT TESTS
# ============================================================================

class TestRoleManagement:
    """Test role management"""

    @pytest.mark.asyncio
    async def test_get_user_roles(self, security_service_url, async_client, valid_credentials):
        """Test getting user roles"""
        # Login first
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )

        if login_response.status_code == 200:
            token = login_response.json().get("token") or login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            # Get roles
            response = await async_client.get(
                f"{security_service_url}/api/v1/roles",
                headers=headers
            )
            assert response.status_code == 200
            assert isinstance(response.json(), (dict, list))

    @pytest.mark.asyncio
    async def test_assign_role(self, security_service_url, async_client, valid_credentials):
        """Test assigning role to user"""
        # Login first
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )

        if login_response.status_code == 200:
            token = login_response.json().get("token") or login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            # Assign role
            response = await async_client.post(
                f"{security_service_url}/api/v1/roles/assign",
                json={"user_id": "user123", "role": "admin"},
                headers=headers
            )
            assert response.status_code in [200, 201, 400, 403]

    @pytest.mark.asyncio
    async def test_revoke_role(self, security_service_url, async_client, valid_credentials):
        """Test revoking role from user"""
        # Login first
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json=valid_credentials
        )

        if login_response.status_code == 200:
            token = login_response.json().get("token") or login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}

            # Revoke role
            response = await async_client.request(
                "DELETE",
                f"{security_service_url}/api/v1/roles/revoke",
                json={"user_id": "user123", "role": "admin"},
                headers=headers,
            )
            assert response.status_code in [200, 201, 204, 400, 403]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestSecurityIntegration:
    """Test security service integration scenarios"""

    @pytest.mark.asyncio
    async def test_full_auth_flow(self, security_service_url, async_client, new_user_data):
        """Test complete authentication flow: register -> login -> access"""
        # Register
        register_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/register",
            json=new_user_data
        )
        assert register_response.status_code in [200, 201]

        # Login with same credentials
        login_response = await async_client.post(
            f"{security_service_url}/api/v1/auth/login",
            json={
                "email": new_user_data["email"],
                "password": new_user_data["password"]
            }
        )
        assert login_response.status_code == 200
        assert "token" in login_response.json() or "access_token" in login_response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
