from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from .models import UserRole, UserStatus


class UserBase(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    role: UserRole = UserRole.CANDIDATE
    status: UserStatus = UserStatus.ACTIVE
    bio: str | None = None
    location: str | None = None
    avatar_url: str | None = None
    tenant_id: str | None = Field(default=None, max_length=64)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    """Partial update - all fields optional except email when used for full update"""

    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    role: UserRole | None = None
    status: UserStatus | None = None
    bio: str | None = None
    location: str | None = None
    avatar_url: str | None = None
    tenant_id: str | None = Field(default=None, max_length=64)


class UserRead(UserBase):
    id: str | UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileBase(BaseModel):
    bio: str | None = None
    phone: str | None = None
    location: str | None = None
    company: str | None = None
    job_title: str | None = None
    avatar_url: str | None = None
    tenant_id: str | None = Field(default=None, max_length=64)


class UserProfileCreate(UserProfileBase):
    user_id: str


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileRead(UserProfileBase):
    id: str | UUID
    user_id: str | UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPreferencesBase(BaseModel):
    notification_email: bool | None = True
    notification_sms: bool | None = False
    notification_push: bool | None = False
    theme: str | None = "light"
    language: str | None = "en"
    tenant_id: str | None = Field(default=None, max_length=64)


class UserPreferencesCreate(UserPreferencesBase):
    user_id: str


class UserPreferencesUpdate(UserPreferencesBase):
    pass


class UserPreferencesRead(UserPreferencesBase):
    id: str | UUID
    user_id: str | UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserActivityRead(BaseModel):
    id: str | UUID
    user_id: str | UUID
    action: str
    resource: str | None = None
    details: Any | None = None
    timestamp: datetime
    tenant_id: str | None = None

    class Config:
        from_attributes = True


class UserSessionRead(BaseModel):
    id: str | UUID
    user_id: str | UUID
    device: str | None = None
    ip: str | None = None
    user_agent: str | None = None
    last_seen: datetime
    revoked: bool
    tenant_id: str | None = None

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    service: str
    status: str


class RootResponse(BaseModel):
    service: str
    status: str
