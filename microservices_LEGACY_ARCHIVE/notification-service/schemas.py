"""
Pydantic schemas for Notification Service
Defines request/response models for email, SMS, and push notifications
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class NotificationChannel(str, Enum):
    """Supported notification channels"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationPriority(str, Enum):
    """Notification priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailPayload(BaseModel):
    """Email notification payload"""

    to: EmailStr = Field(..., description="Recipient email address")
    subject: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)
    from_email: EmailStr | None = Field(None, description="Sender email address (optional)")
    from_name: str | None = Field(None, description="Sender display name")
    cc: list[EmailStr] | None = Field(None, description="CC recipients")
    bcc: list[EmailStr] | None = Field(None, description="BCC recipients")
    reply_to: EmailStr | None = Field(None, description="Reply-to address")
    html_body: str | None = Field(None, description="HTML version of the email body")
    attachments: list[dict[str, str]] | None = Field(None, description="Email attachments")
    template_id: str | None = Field(None, description="Template identifier for pre-defined emails")
    template_data: dict[str, Any] | None = Field(None, description="Data to populate template")
    priority: NotificationPriority = NotificationPriority.NORMAL


class SMSPayload(BaseModel):
    """SMS notification payload"""

    to: str = Field(
        ..., pattern=r"^\+?[1-9]\d{1,14}$", description="Recipient phone number in E.164 format"
    )
    message: str = Field(..., min_length=1, max_length=1600, description="SMS message content")
    from_number: str | None = Field(None, description="Sender phone number")
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_time: datetime | None = Field(None, description="Schedule SMS for future delivery")


class PushPayload(BaseModel):
    """Push notification payload"""

    user_id: str = Field(..., description="Target user identifier")
    title: str = Field(..., min_length=1, max_length=100)
    body: str = Field(..., min_length=1, max_length=500)
    icon: str | None = Field(None, description="Notification icon URL")
    image: str | None = Field(None, description="Notification image URL")
    click_action: str | None = Field(None, description="URL to navigate on click")
    data: dict[str, Any] | None = Field(None, description="Additional custom data payload")
    priority: NotificationPriority = NotificationPriority.NORMAL
    badge: int | None = Field(None, ge=0, description="Badge count for app icon")
    sound: str | None = Field("default", description="Notification sound")
    tag: str | None = Field(None, description="Notification tag for grouping")
    device_tokens: list[str] | None = Field(None, description="Specific device tokens to target")


class NotificationRequest(BaseModel):
    """Generic notification request"""

    channel: NotificationChannel
    recipient: str = Field(..., description="Recipient identifier (email, phone, user_id)")
    subject: str | None = None
    message: str = Field(..., min_length=1)
    data: dict[str, Any] | None = None
    priority: NotificationPriority = NotificationPriority.NORMAL


class NotificationResponse(BaseModel):
    """Notification send response"""

    notification_id: str
    status: str = Field(..., description="Status: 'sent', 'queued', 'failed'")
    channel: NotificationChannel
    recipient: str
    sent_at: datetime | None = None
    message: str | None = None


class BulkNotificationRequest(BaseModel):
    """Bulk notification request"""

    channel: NotificationChannel
    recipients: list[str] = Field(..., min_items=1, max_items=1000)
    subject: str | None = None
    message: str = Field(..., min_length=1)
    data: dict[str, Any] | None = None
    priority: NotificationPriority = NotificationPriority.NORMAL


class BulkNotificationResponse(BaseModel):
    """Bulk notification response"""

    batch_id: str
    total_count: int
    success_count: int
    failed_count: int
    notifications: list[NotificationResponse]


class NotificationStatus(BaseModel):
    """Notification delivery status"""

    notification_id: str
    status: str = Field(..., description="Status: 'pending', 'sent', 'delivered', 'read', 'failed'")
    channel: NotificationChannel
    recipient: str
    created_at: datetime
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    error_message: str | None = None


class NotificationPreference(BaseModel):
    """User notification preferences"""

    user_id: str
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    quiet_hours_start: str | None = Field(
        None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$", description="Quiet hours start time (HH:MM)"
    )
    quiet_hours_end: str | None = Field(
        None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$", description="Quiet hours end time (HH:MM)"
    )
    timezone: str = "UTC"


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str
    details: str | None = None


class SuccessResponse(BaseModel):
    """Standard success response"""

    message: str
    data: dict[str, Any] | None = None
