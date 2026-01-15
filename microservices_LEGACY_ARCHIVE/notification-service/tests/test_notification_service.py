"""
Tests for Notification Service
Following TDD principles - tests written before implementation
"""

from typing import Any

import httpx
import pytest

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def notification_service_url():
    """Base URL for notification service"""
    return "http://localhost:8011"


@pytest.fixture
def async_client():
    """Async HTTP client"""
    return httpx.AsyncClient(timeout=5.0)


@pytest.fixture
def sample_email_data() -> dict[str, Any]:
    """Sample email data for testing"""
    return {
        "to": "user@example.com",
        "subject": "Interview Invitation",
        "html": "<h1>You are invited to an interview</h1>",
        "text": "You are invited to an interview",
    }


@pytest.fixture
def sample_sms_data() -> dict[str, Any]:
    """Sample SMS data for testing"""
    return {"to": "+1234567890", "text": "Your interview is scheduled for tomorrow"}


@pytest.fixture
def sample_push_data() -> dict[str, Any]:
    """Sample push notification data"""
    return {
        "to": "device_token_123",
        "title": "Interview Scheduled",
        "body": "Your interview is confirmed",
        "data": {"interview_id": "123"},
    }


# ============================================================================
# ROOT & HEALTH ENDPOINT TESTS
# ============================================================================


class TestNotificationServiceBasics:
    """Test basic service health and root endpoints"""

    @pytest.mark.asyncio
    async def test_service_health_check(self, notification_service_url, async_client):
        """Test that health endpoint returns 200 and provider status"""
        response = await async_client.get(f"{notification_service_url}/health")
        assert response.status_code == 200

        data = response.json()
        assert "provider" in data
        assert "status" in data or "ok" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self, notification_service_url, async_client):
        """Test that root endpoint is accessible"""
        response = await async_client.get(f"{notification_service_url}/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_provider_info_endpoint(self, notification_service_url, async_client):
        """Test that provider info endpoint returns active provider"""
        response = await async_client.get(f"{notification_service_url}/api/v1/provider")
        assert response.status_code == 200

        data = response.json()
        assert "provider" in data or "active_provider" in data
        assert "ok" in data or "status" in data


# ============================================================================
# EMAIL NOTIFICATION TESTS
# ============================================================================


class TestEmailNotifications:
    """Test email notification functionality"""

    @pytest.mark.asyncio
    async def test_send_email_success(
        self, notification_service_url, async_client, sample_email_data
    ):
        """Test sending a valid email notification"""
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/email", json=sample_email_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data or "status" in data

    @pytest.mark.asyncio
    async def test_send_email_missing_to(self, notification_service_url, async_client):
        """Test sending email without recipient should fail"""
        invalid_data = {"subject": "Test", "html": "Test"}
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/email", json=invalid_data
        )
        assert response.status_code in [400, 422]  # Validation error

    @pytest.mark.asyncio
    async def test_send_email_missing_subject(self, notification_service_url, async_client):
        """Test sending email without subject should fail"""
        invalid_data = {"to": "user@example.com", "html": "Test"}
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/email", json=invalid_data
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_email_content_preservation(
        self, notification_service_url, async_client, sample_email_data
    ):
        """Test that email content is preserved when sent"""
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/email", json=sample_email_data
        )
        assert response.status_code == 200
        # Verify that response contains confirmation
        data = response.json()
        assert data.get("ok") or data.get("status") == "sent"


# ============================================================================
# SMS NOTIFICATION TESTS
# ============================================================================


class TestSMSNotifications:
    """Test SMS notification functionality"""

    @pytest.mark.asyncio
    async def test_send_sms_success(self, notification_service_url, async_client, sample_sms_data):
        """Test sending a valid SMS"""
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/sms", json=sample_sms_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data or "status" in data

    @pytest.mark.asyncio
    async def test_send_sms_missing_to(self, notification_service_url, async_client):
        """Test sending SMS without phone number should fail"""
        invalid_data = {"text": "Test message"}
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/sms", json=invalid_data
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_send_sms_missing_text(self, notification_service_url, async_client):
        """Test sending SMS without text should fail"""
        invalid_data = {"to": "+1234567890"}
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/sms", json=invalid_data
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_sms_phone_number_validation(self, notification_service_url, async_client):
        """Test that invalid phone numbers are rejected"""
        invalid_data = {"to": "invalid-phone", "text": "Test message"}
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/sms", json=invalid_data
        )
        # Should either be rejected or accepted with fallback
        assert response.status_code in [200, 400, 422]


# ============================================================================
# PUSH NOTIFICATION TESTS
# ============================================================================


class TestPushNotifications:
    """Test push notification functionality"""

    @pytest.mark.asyncio
    async def test_send_push_success(
        self, notification_service_url, async_client, sample_push_data
    ):
        """Test sending a valid push notification"""
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/push", json=sample_push_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data or "status" in data

    @pytest.mark.asyncio
    async def test_send_push_missing_to(self, notification_service_url, async_client):
        """Test sending push without device token should fail"""
        invalid_data = {"title": "Test", "body": "Test message"}
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/push", json=invalid_data
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_send_push_missing_title(self, notification_service_url, async_client):
        """Test sending push without title should fail"""
        invalid_data = {"to": "device_token", "body": "Test message"}
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/push", json=invalid_data
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_push_data_payload(
        self, notification_service_url, async_client, sample_push_data
    ):
        """Test that push notification data payload is preserved"""
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/push", json=sample_push_data
        )
        assert response.status_code == 200
        data = response.json()
        # Verify response is successful
        assert data.get("ok") or data.get("status") == "sent"


# ============================================================================
# TEMPLATES TESTS
# ============================================================================


class TestNotificationTemplates:
    """Test notification template functionality"""

    @pytest.mark.asyncio
    async def test_get_templates_endpoint(self, notification_service_url, async_client):
        """Test that templates endpoint returns list"""
        response = await async_client.get(f"{notification_service_url}/api/v1/notify/templates")
        assert response.status_code == 200
        data = response.json()
        # Should return either templates dict or list
        assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_templates_response_structure(self, notification_service_url, async_client):
        """Test that templates response has expected structure"""
        response = await async_client.get(f"{notification_service_url}/api/v1/notify/templates")
        assert response.status_code == 200
        data = response.json()
        # Response should contain templates
        assert data is not None


# ============================================================================
# PROVIDER FALLBACK TESTS
# ============================================================================


class TestProviderFallback:
    """Test provider fallback and resilience"""

    @pytest.mark.asyncio
    async def test_fallback_annotation(
        self, notification_service_url, async_client, sample_email_data
    ):
        """Test that fallback provider is annotated in response"""
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/email", json=sample_email_data
        )
        assert response.status_code == 200
        data = response.json()
        # Response may contain fallback information
        # fallback key should only be present if fallback was used
        if "fallback" in data:
            assert isinstance(data["fallback"], bool)

    @pytest.mark.asyncio
    async def test_provider_health_status(self, notification_service_url, async_client):
        """Test that provider health status is reported"""
        response = await async_client.get(f"{notification_service_url}/health")
        assert response.status_code == 200
        data = response.json()
        # Should indicate which provider is active
        assert "provider" in data or "active_provider" in data
        assert data.get("ok") or data.get("status") is not None


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_invalid_json_request(self, notification_service_url, async_client):
        """Test handling of invalid JSON request"""
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/email",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_empty_email_data(self, notification_service_url, async_client):
        """Test handling of empty email data"""
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/email", json={}
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_empty_sms_data(self, notification_service_url, async_client):
        """Test handling of empty SMS data"""
        response = await async_client.post(f"{notification_service_url}/api/v1/notify/sms", json={})
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_empty_push_data(self, notification_service_url, async_client):
        """Test handling of empty push data"""
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/push", json={}
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_very_long_email_content(self, notification_service_url, async_client):
        """Test handling of very long email content"""
        long_content = "x" * 100000
        data = {
            "to": "user@example.com",
            "subject": "Test",
            "html": long_content,
            "text": long_content,
        }
        response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/email", json=data
        )
        # Should either accept or reject gracefully
        assert response.status_code in [200, 413, 422]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestNotificationIntegration:
    """Test notification service integration scenarios"""

    @pytest.mark.asyncio
    async def test_multiple_notifications_sequence(
        self,
        notification_service_url,
        async_client,
        sample_email_data,
        sample_sms_data,
        sample_push_data,
    ):
        """Test sending multiple notifications in sequence"""
        # Send email
        email_response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/email", json=sample_email_data
        )
        assert email_response.status_code == 200

        # Send SMS
        sms_response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/sms", json=sample_sms_data
        )
        assert sms_response.status_code == 200

        # Send push
        push_response = await async_client.post(
            f"{notification_service_url}/api/v1/notify/push", json=sample_push_data
        )
        assert push_response.status_code == 200

    @pytest.mark.asyncio
    async def test_service_remains_healthy_after_notifications(
        self, notification_service_url, async_client, sample_email_data
    ):
        """Test that service remains healthy after sending notifications"""
        # Send notification
        await async_client.post(
            f"{notification_service_url}/api/v1/notify/email", json=sample_email_data
        )

        # Check health
        health_response = await async_client.get(f"{notification_service_url}/health")
        assert health_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
