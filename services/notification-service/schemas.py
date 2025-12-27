"""
Notification Service - Comprehensive Pydantic V2 Schemas
Generated: December 17, 2025
Coverage: 14 endpoints with full type safety
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class NotificationPriority(str, Enum):
    """Priority levels for notifications"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, Enum):
    """Notification delivery status"""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


class NotificationType(str, Enum):
    """Notification channel type"""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================


class EmailNotificationRequest(BaseModel):
    to: EmailStr
    subject: str = Field(..., min_length=1, strip_whitespace=True)
    html: str | None = ""
    text: str | None = None
    priority: NotificationPriority | None = Field(default=NotificationPriority.NORMAL)
    cc: list[EmailStr] | None = None
    bcc: list[EmailStr] | None = None
    attachments: list[str] | None = None  # File URLs


class SMSNotificationRequest(BaseModel):
    # E.164 phone format: optional +, up to 15 digits
    to: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$", strip_whitespace=True)
    text: str = Field(..., min_length=1, max_length=1600, strip_whitespace=True)
    priority: NotificationPriority | None = Field(default=NotificationPriority.NORMAL)


class PushNotificationRequest(BaseModel):
    to: str = Field(..., min_length=1, strip_whitespace=True)
    title: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    body: str = Field(..., min_length=1, max_length=500, strip_whitespace=True)
    data: dict[str, Any] | None = None
    priority: NotificationPriority | None = Field(default=NotificationPriority.NORMAL)
    icon: str | None = None
    action_url: str | None = None


class InAppNotificationRequest(BaseModel):
    """In-app notification request"""

    user_id: str
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    type: str = Field(..., pattern=r"^(info|success|warning|error)$")
    action_url: str | None = None
    data: dict[str, Any] | None = None


class BulkNotificationRequest(BaseModel):
    """Bulk notification request"""

    recipients: list[str] = Field(..., min_length=1, max_length=1000)
    notification_type: NotificationType
    template_id: str | None = None
    subject: str | None = None
    message: str = Field(..., min_length=1)
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: datetime | None = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================


class NotificationResponse(BaseModel):
    """Notification response"""

    id: str
    status: NotificationStatus
    message: str
    sent_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class BulkNotificationResponse(BaseModel):
    """Bulk notification response"""

    total: int
    sent: int
    failed: int
    pending: int
    notification_ids: list[str]


class NotificationHistoryResponse(BaseModel):
    """Notification history entry"""

    id: str
    notification_type: NotificationType
    recipient: str
    status: NotificationStatus
    subject: str | None = None
    sent_at: datetime
    delivered_at: datetime | None = None
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class NotificationHistoryListResponse(BaseModel):
    """Paginated notification history"""

    items: list[NotificationHistoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# TEMPLATE SCHEMAS
# ============================================================================


class TemplateBase(BaseModel):
    """Base template model"""

    name: str = Field(..., min_length=1, max_length=100)
    notification_type: NotificationType
    subject: str | None = Field(None, max_length=200)
    content: str = Field(..., min_length=1)
    variables: list[str] | None = None


class TemplateCreate(TemplateBase):
    """Create template request"""

    pass


class TemplateUpdate(BaseModel):
    """Update template request"""

    name: str | None = Field(None, min_length=1, max_length=100)
    subject: str | None = Field(None, max_length=200)
    content: str | None = None
    variables: list[str] | None = None


class TemplateResponse(TemplateBase):
    """Template response with metadata"""

    id: str
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class TemplateListResponse(BaseModel):
    """Paginated template list"""

    items: list[TemplateResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# PREFERENCES SCHEMAS
# ============================================================================


class NotificationPreferencesBase(BaseModel):
    """Base notification preferences"""

    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    marketing_emails: bool = False
    interview_reminders: bool = True
    application_updates: bool = True
    system_alerts: bool = True


class NotificationPreferencesCreate(NotificationPreferencesBase):
    """Create notification preferences"""

    user_id: str


class NotificationPreferencesUpdate(BaseModel):
    """Update notification preferences"""

    email_enabled: bool | None = None
    sms_enabled: bool | None = None
    push_enabled: bool | None = None
    in_app_enabled: bool | None = None
    marketing_emails: bool | None = None
    interview_reminders: bool | None = None
    application_updates: bool | None = None
    system_alerts: bool | None = None


class NotificationPreferencesResponse(NotificationPreferencesBase):
    """Notification preferences response"""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================


class NotificationAnalyticsRequest(BaseModel):
    """Notification analytics request"""

    start_date: datetime
    end_date: datetime
    notification_type: NotificationType | None = None


class NotificationAnalyticsResponse(BaseModel):
    """Notification analytics response"""

    total_sent: int
    total_delivered: int
    total_failed: int
    delivery_rate: float
    by_type: dict[str, int]
    by_status: dict[str, int]
    peak_hours: list[int]


# ============================================================================
# HEALTH & SERVICE INFO
# ============================================================================


class HealthCheckResponse(BaseModel):
    """Service health check"""

    status: str
    timestamp: datetime
    version: str
    email_provider_status: str
    sms_provider_status: str
    push_provider_status: str


class ErrorResponse(BaseModel):
    """Error response"""

    error: str
    detail: str | None = None
    timestamp: datetime
