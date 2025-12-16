import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, Column, DateTime, String, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .database import Base


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class UserRole(str, Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"
    CANDIDATE = "candidate"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(SAEnum(UserRole, name="userrole"), nullable=False, default=UserRole.CANDIDATE)
    status = Column(SAEnum(UserStatus, name="userstatus"), nullable=False, default=UserStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    bio = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    phone = Column(String(30), nullable=True)
    tenant_id = Column(String(64), nullable=True, index=True)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    bio = Column(Text, nullable=True)
    phone = Column(String(30), nullable=True)
    location = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    avatar_uploaded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = Column(String(64), nullable=True, index=True)


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    notification_email = Column(Boolean, nullable=False, default=True)
    notification_sms = Column(Boolean, nullable=False, default=False)
    notification_push = Column(Boolean, nullable=False, default=False)
    theme = Column(String(20), nullable=True, default="light")
    language = Column(String(10), nullable=True, default="en")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant_id = Column(String(64), nullable=True, index=True)


class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=True)
    details = Column(JSONB, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    tenant_id = Column(String(64), nullable=True, index=True)


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    device = Column(String(100), nullable=True)
    ip = Column(String(64), nullable=True)
    user_agent = Column(Text, nullable=True)
    last_seen = Column(DateTime, nullable=False, default=datetime.utcnow)
    revoked = Column(Boolean, nullable=False, default=False)
    tenant_id = Column(String(64), nullable=True, index=True)
