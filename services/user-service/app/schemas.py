from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from .models import UserRole, UserStatus


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.CANDIDATE
    status: UserStatus = UserStatus.ACTIVE
    bio: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    tenant_id: Optional[str] = Field(default=None, max_length=64)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    """Partial update - all fields optional except email when used for full update"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    tenant_id: Optional[str] = Field(default=None, max_length=64)


class UserRead(UserBase):
    id: str | UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileBase(BaseModel):
    bio: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    avatar_url: Optional[str] = None
    tenant_id: Optional[str] = Field(default=None, max_length=64)


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
    notification_email: Optional[bool] = True
    notification_sms: Optional[bool] = False
    notification_push: Optional[bool] = False
    theme: Optional[str] = "light"
    language: Optional[str] = "en"
    tenant_id: Optional[str] = Field(default=None, max_length=64)


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
    resource: Optional[str] = None
    details: Optional[Any] = None
    timestamp: datetime
    tenant_id: Optional[str] = None

    class Config:
        from_attributes = True


class UserSessionRead(BaseModel):
    id: str | UUID
    user_id: str | UUID
    device: Optional[str] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    last_seen: datetime
    revoked: bool
    tenant_id: Optional[str] = None

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    service: str
    status: str


class RootResponse(BaseModel):
    service: str
    status: str
