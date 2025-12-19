"""
User Service - Pydantic Schemas
Comprehensive schema definitions for user management, profiles, and activity tracking
"""

from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# ============================================================================
# ENUMS
# ============================================================================

class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    RECRUITER = "recruiter"
    INTERVIEWER = "interviewer"
    CANDIDATE = "candidate"
    GUEST = "guest"
    SYSTEM = "system"


class ActivityType(str, Enum):
    """User activity types"""
    LOGIN = "login"
    LOGOUT = "logout"
    PROFILE_UPDATE = "profile_update"
    PASSWORD_CHANGE = "password_change"
    SETTINGS_UPDATE = "settings_update"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    APPLICATION_SUBMITTED = "application_submitted"
    FILE_UPLOADED = "file_uploaded"
    FILE_DOWNLOADED = "file_downloaded"


class NotificationPreference(str, Enum):
    """Notification preferences"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    NONE = "none"


class PrivacyLevel(str, Enum):
    """Profile privacy levels"""
    PUBLIC = "public"
    PRIVATE = "private"
    CONTACTS_ONLY = "contacts_only"


class Gender(str, Enum):
    """Gender options"""
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    OTHER = "other"


# ============================================================================
# USER CORE
# ============================================================================

class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')  # E.164 format
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+14155552671"
            }
        }
    )


class UserCreate(UserBase):
    """Create new user"""
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.CANDIDATE
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Update user (all fields optional)"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    """User response model"""
    user_id: str
    status: UserStatus
    role: UserRole
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    is_verified: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """List of users with pagination"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# USER PROFILE
# ============================================================================

class ProfileBase(BaseModel):
    """Base profile information"""
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[HttpUrl] = None
    location: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[datetime] = None
    gender: Optional[Gender] = None
    linkedin_url: Optional[HttpUrl] = None
    twitter_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    website_url: Optional[HttpUrl] = None


class ProfileCreate(ProfileBase):
    """Create user profile"""
    pass


class ProfileUpdate(ProfileBase):
    """Update user profile (all fields optional)"""
    pass


class ProfileResponse(ProfileBase):
    """Profile response"""
    user_id: str
    profile_id: str
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE
    profile_completion: int = Field(..., ge=0, le=100, description="Profile completion percentage")
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProfilePhotoUpload(BaseModel):
    """Profile photo upload"""
    photo_base64: str = Field(..., description="Base64-encoded image data")
    filename: str
    content_type: str = Field(..., pattern=r'^image/(jpeg|png|gif|webp)$')


# ============================================================================
# USER PREFERENCES
# ============================================================================

class UserPreferences(BaseModel):
    """User preferences"""
    language: str = Field("en", max_length=10)
    theme: str = Field("light", pattern=r'^(light|dark|auto)$')
    notifications_enabled: bool = True
    notification_channels: List[NotificationPreference] = [NotificationPreference.EMAIL]
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    marketing_emails: bool = False
    interview_reminders: bool = True
    reminder_minutes_before: int = Field(30, ge=5, le=1440)
    timezone: str = "UTC"
    date_format: str = Field("YYYY-MM-DD", max_length=20)
    time_format: str = Field("HH:mm", pattern=r'^(12h|24h|HH:mm|hh:mm A)$')
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "language": "en",
                "theme": "dark",
                "notifications_enabled": True,
                "notification_channels": ["email", "push"],
                "interview_reminders": True,
                "reminder_minutes_before": 30,
                "timezone": "America/New_York"
            }
        }
    )


class UserSettings(BaseModel):
    """User application settings"""
    auto_save: bool = True
    show_tutorials: bool = True
    compact_mode: bool = False
    sidebar_collapsed: bool = False
    items_per_page: int = Field(25, ge=10, le=100)
    enable_analytics: bool = True
    enable_keyboard_shortcuts: bool = True
    custom_settings: Optional[Dict[str, Any]] = None


# ============================================================================
# ACTIVITY TRACKING
# ============================================================================

class ActivityLog(BaseModel):
    """User activity log entry"""
    activity_id: str
    user_id: str
    activity_type: ActivityType
    description: str
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "activity_id": "act_123",
                "user_id": "user_456",
                "activity_type": "login",
                "description": "User logged in successfully",
                "ip_address": "192.168.1.1",
                "timestamp": "2025-12-17T10:30:00Z"
            }
        }
    )


class ActivityLogRequest(BaseModel):
    """Create activity log entry"""
    activity_type: ActivityType
    description: str
    metadata: Optional[Dict[str, Any]] = None


class SessionInfo(BaseModel):
    """User session information"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool


class LoginHistoryEntry(BaseModel):
    """Login history entry"""
    login_id: str
    user_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    location: Optional[str] = None
    success: bool
    failure_reason: Optional[str] = None


# ============================================================================
# SEARCH & FILTERING
# ============================================================================

class UserSearchRequest(BaseModel):
    """User search request"""
    query: Optional[str] = Field(None, min_length=1, max_length=200)
    roles: Optional[List[UserRole]] = None
    statuses: Optional[List[UserStatus]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_login_after: Optional[datetime] = None
    verified_only: bool = False
    page: int = Field(1, ge=1)
    page_size: int = Field(25, ge=1, le=100)
    sort_by: str = Field("created_at", pattern=r'^(created_at|updated_at|last_login|email|first_name|last_name)$')
    sort_order: str = Field("desc", pattern=r'^(asc|desc)$')


class UserFilterRequest(BaseModel):
    """User filter request"""
    filters: Dict[str, Any]
    page: int = Field(1, ge=1)
    page_size: int = Field(25, ge=1, le=100)


class UserBulkLookupRequest(BaseModel):
    """Bulk user lookup request"""
    user_ids: List[str] = Field(..., min_length=1, max_length=100)
    include_profiles: bool = False
    include_preferences: bool = False


# ============================================================================
# STATISTICS
# ============================================================================

class UserStatistics(BaseModel):
    """User statistics"""
    total_users: int
    active_users: int
    inactive_users: int
    suspended_users: int
    pending_users: int
    verified_users: int
    unverified_users: int
    users_by_role: Dict[UserRole, int]
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    active_sessions: int
    average_session_duration_minutes: float


# ============================================================================
# NOTIFICATIONS
# ============================================================================

class NotificationRequest(BaseModel):
    """Send notification to user"""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    channels: List[NotificationPreference]
    priority: str = Field("normal", pattern=r'^(low|normal|high|urgent)$')
    action_url: Optional[HttpUrl] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Notification"""
    notification_id: str
    user_id: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    action_url: Optional[str] = None


# ============================================================================
# INTEGRATION
# ============================================================================

class UserInviteRequest(BaseModel):
    """Invite user to platform"""
    email: EmailStr
    role: UserRole
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    message: Optional[str] = Field(None, max_length=500)


class UserInviteResponse(BaseModel):
    """User invite response"""
    invite_id: str
    email: str
    role: UserRole
    status: str
    created_at: datetime
    expires_at: datetime
    invite_url: str


class UserExportRequest(BaseModel):
    """Export user data"""
    user_id: str
    include_profile: bool = True
    include_activity: bool = True
    include_preferences: bool = True
    format: str = Field("json", pattern=r'^(json|csv|pdf)$')


class UserImportRequest(BaseModel):
    """Import users"""
    users: List[UserCreate] = Field(..., min_items=1, max_items=1000)
    skip_duplicates: bool = True
    send_invites: bool = False


# ============================================================================
# STATUS & HEALTH
# ============================================================================

class UserStatusUpdate(BaseModel):
    """Update user status"""
    status: UserStatus
    reason: Optional[str] = Field(None, max_length=200)


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., pattern=r'^(healthy|degraded|unhealthy)$')
    timestamp: datetime
    database_connected: bool
    cache_connected: bool
    total_users: int
    active_sessions: int
    uptime_seconds: float


# ============================================================================
# ERROR RESPONSES
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    field: str
    message: str
    value: Optional[Any] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    error: str = "Validation Error"
    details: List[ValidationErrorDetail]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
