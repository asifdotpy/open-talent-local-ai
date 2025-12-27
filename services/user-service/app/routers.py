import csv
import io
import os

# Import comprehensive schemas from root schemas.py
import sys
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_session
from .models import (
    User,
    UserActivity,
    UserPreferences,
    UserProfile,
    UserRole,
    UserSession,
    UserStatus,
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import ActivityLog as UserActivityRead
from schemas import ProfileCreate as UserProfileCreate
from schemas import ProfileResponse as UserProfileRead
from schemas import ProfileUpdate as UserProfileUpdate
from schemas import SessionInfo as UserSessionRead
from schemas import (
    UserCreate,  # User Core
    UserUpdate,  # User Core
)
from schemas import (
    UserPreferences as UserPreferencesRead,  # Base preferences model used for response
)
from schemas import UserResponse as UserRead


# Note: UserPreferencesCreate and UserPreferencesUpdate not in comprehensive schemas
# Define minimal versions here for backward compatibility
class UserPreferencesCreate(BaseModel):
    user_id: str
    notification_email: bool | None = True
    notification_sms: bool | None = False
    notification_push: bool | None = False
    theme: str | None = "light"
    language: str | None = "en"
    tenant_id: str | None = None


class UserPreferencesUpdate(BaseModel):
    notification_email: bool | None = None
    notification_sms: bool | None = None
    notification_push: bool | None = None
    theme: str | None = None
    language: str | None = None


# Legacy response schemas for simple endpoints
class RootResponse(BaseModel):
    service: str
    status: str


class SimpleHealthResponse(BaseModel):
    service: str
    status: str


from .utils import JWTClaims, get_jwt_claims, require_role

router = APIRouter()


@router.get("/", response_model=RootResponse)
async def root() -> RootResponse:
    """Standard root endpoint for service identification.

    Returns:
        A RootResponse containing the service name and current operational status.
    """
    return RootResponse(service="user", status="ok")


@router.get("/health", response_model=SimpleHealthResponse)
async def health() -> SimpleHealthResponse:
    """Standard health check endpoint for monitoring and orchestration.

    Returns:
        A SimpleHealthResponse confirming the service is operational.
    """
    return SimpleHealthResponse(service="user", status="healthy")


# ============================================================================
# USER CRUD ENDPOINTS
# ============================================================================


@router.get("/api/v1/users", response_model=list[UserRead])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    email: str | None = Query(None, description="Filter by email (partial match)"),
    role: UserRole | None = Query(None, description="Filter by role"),
    status: UserStatus | None = Query(None, description="Filter by status"),
    search: str | None = Query(None, description="Search by name, email, or location"),
    tenant_id: str | None = Query(None, description="Filter by tenant (admin only)"),
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> list[UserRead]:
    """List users with pagination and filtering. Enforces RLS by tenant_id."""
    query = select(User)

    filters = []

    # RLS: Enforce tenant isolation unless admin
    if claims.role != "admin":
        # Non-admin users can only see their own tenant
        if claims.tenant_id:
            filters.append(User.tenant_id == claims.tenant_id)
        else:
            # Users without tenant_id can only see their own record
            filters.append(User.email == claims.email)
    elif tenant_id:
        # Admin can filter by specific tenant
        filters.append(User.tenant_id == tenant_id)

    if email:
        filters.append(User.email.ilike(f"%{email}%"))
    if role:
        filters.append(User.role == role)
    if status:
        filters.append(User.status == status)
    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            User.first_name.ilike(f"%{search}%"),
            User.last_name.ilike(f"%{search}%"),
            User.location.ilike(f"%{search}%"),
        )
        filters.append(search_filter)

    if filters:
        query = query.where(and_(*filters))

    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await session.execute(query)
    users = result.scalars().all()

    return [UserRead.model_validate(user) for user in users]


@router.get("/api/v1/users/count", response_model=dict)
async def count_users(
    role: UserRole | None = Query(None),
    status: UserStatus | None = Query(None),
    tenant_id: str | None = Query(None, description="Filter by tenant (admin only)"),
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> dict:
    """Get user count with optional filters. Enforces RLS by tenant_id."""
    query = select(func.count(User.id))

    filters = []

    # RLS: Enforce tenant isolation unless admin
    if claims.role != "admin":
        if claims.tenant_id:
            filters.append(User.tenant_id == claims.tenant_id)
        else:
            filters.append(User.email == claims.email)
    elif tenant_id:
        filters.append(User.tenant_id == tenant_id)

    if role:
        filters.append(User.role == role)
    if status:
        filters.append(User.status == status)

    if filters:
        query = query.where(and_(*filters))

    result = await session.execute(query)
    count = result.scalar()

    return {"count": count}


@router.get("/api/v1/users/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserRead:
    """Get a specific user by ID. Enforces RLS by tenant_id.
    Accepts string ID to avoid 422 on non-UUIDs; returns 404 instead.
    Special handling for 'me' endpoint to get current user by email.
    """
    # Handle 'me' endpoint - get current user by email from claims
    if user_id == "me":
        result = await session.execute(select(User).where(User.email == claims.email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return UserRead.model_validate(user)

    # For all other IDs, try to parse as UUID
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        # Return 404 for non-UUID IDs (like "123")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result = await session.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # RLS: Check tenant access
    if claims.role != "admin":
        if (
            claims.tenant_id
            and user.tenant_id != claims.tenant_id
            or not claims.tenant_id
            and user.email != claims.email
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return UserRead.model_validate(user)


@router.post("/api/v1/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserRead:
    """Create a new user. RLS: Inherits tenant_id from JWT claims unless admin."""
    existing = await session.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    # RLS: Enforce tenant_id from claims unless admin
    tenant_id = payload.tenant_id
    if claims.role != "admin":
        tenant_id = claims.tenant_id  # Non-admin users create users in their own tenant

    user = User(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        role=payload.role,
        status=payload.status,
        bio=payload.bio,
        location=payload.location,
        avatar_url=payload.avatar_url,
        tenant_id=tenant_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


@router.patch("/api/v1/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserRead:
    """Update an existing user. Enforces RLS by tenant_id."""
    # Handle 'me' endpoint - get current user by email from claims
    if user_id == "me":
        result = await session.execute(select(User).where(User.email == claims.email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    else:
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        result = await session.execute(select(User).where(User.id == user_uuid))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # RLS: Check tenant access (only for non-'me' endpoints)
        if claims.role != "admin":
            if (
                claims.tenant_id
                and user.tenant_id != claims.tenant_id
                or not claims.tenant_id
                and user.email != claims.email
            ):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Check email uniqueness if changed
    if payload.email and payload.email != user.email:
        existing = await session.execute(select(User).where(User.email == payload.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    # Update fields that are provided
    for field, value in payload.model_dump(exclude_unset=True).items():
        # RLS: Non-admin cannot change tenant_id
        if field == "tenant_id" and claims.role != "admin":
            continue
        if value is not None:
            setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


# Also support PUT for update operations for compatibility with tests
@router.put("/api/v1/users/{user_id}", response_model=UserRead)
async def put_update_user(
    user_id: str,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserRead:
    return await update_user(user_id=user_id, payload=payload, session=session, claims=claims)


@router.delete("/api/v1/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(require_role("admin")),
):
    """Delete a user (soft delete by setting status to inactive). Admin only."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result = await session.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Soft delete
    user.status = UserStatus.INACTIVE
    user.updated_at = datetime.utcnow()
    await session.commit()


# ============================================================================
# USER PROFILE ENDPOINTS
# ============================================================================


@router.get("/api/v1/users/{user_id}/profile", response_model=UserProfileRead)
async def get_user_profile(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserProfileRead:
    """Get user profile."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    result = await session.execute(select(UserProfile).where(UserProfile.user_id == user_uuid))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return UserProfileRead.model_validate(profile)


@router.post(
    "/api/v1/users/{user_id}/profile",
    response_model=UserProfileRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_profile(
    user_id: str,
    payload: UserProfileCreate,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserProfileRead:
    """Create user profile."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verify user exists
    user_result = await session.execute(select(User).where(User.id == user_uuid))
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if profile already exists
    existing = await session.execute(select(UserProfile).where(UserProfile.user_id == user_uuid))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile already exists")

    profile = UserProfile(
        user_id=user_uuid,
        bio=payload.bio,
        phone=payload.phone,
        location=payload.location,
        company=payload.company,
        job_title=payload.job_title,
        avatar_url=payload.avatar_url,
        tenant_id=payload.tenant_id,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return UserProfileRead.model_validate(profile)


@router.patch("/api/v1/users/{user_id}/profile", response_model=UserProfileRead)
async def update_user_profile(
    user_id: str,
    payload: UserProfileUpdate,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserProfileRead:
    """Update user profile."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    result = await session.execute(select(UserProfile).where(UserProfile.user_id == user_uuid))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    profile.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(profile)
    return UserProfileRead.model_validate(profile)


@router.put("/api/v1/users/{user_id}/profile", response_model=UserProfileRead)
async def put_update_user_profile(
    user_id: str,
    payload: UserProfileUpdate,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserProfileRead:
    return await update_user_profile(
        user_id=user_id, payload=payload, session=session, claims=claims
    )


# Current user profile endpoints
@router.get("/api/v1/users/me/profile", response_model=UserProfileRead)
async def get_current_user_profile(
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserProfileRead:
    """Get current user's profile."""
    # Get user by email from claims
    result = await session.execute(select(User).where(User.email == claims.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Get profile for this user
    profile_result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return UserProfileRead.model_validate(profile)


@router.patch("/api/v1/users/me/profile", response_model=UserProfileRead)
async def update_current_user_profile(
    payload: UserProfileUpdate,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserProfileRead:
    """Update current user's profile."""
    # Get user by email from claims
    result = await session.execute(select(User).where(User.email == claims.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Get profile for this user
    profile_result = await session.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    profile.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(profile)
    return UserProfileRead.model_validate(profile)


# ============================================================================
# USER PREFERENCES ENDPOINTS
# ============================================================================


@router.get("/api/v1/users/{user_id}/preferences", response_model=UserPreferencesRead)
async def get_user_preferences(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserPreferencesRead:
    """Get user preferences."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found")

    result = await session.execute(
        select(UserPreferences).where(UserPreferences.user_id == user_uuid)
    )
    preferences = result.scalar_one_or_none()
    if not preferences:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found")
    return UserPreferencesRead.model_validate(preferences)


@router.post(
    "/api/v1/users/{user_id}/preferences",
    response_model=UserPreferencesRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_preferences(
    user_id: str,
    payload: UserPreferencesCreate,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserPreferencesRead:
    """Create user preferences."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verify user exists
    user_result = await session.execute(select(User).where(User.id == user_uuid))
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if preferences already exist
    existing = await session.execute(
        select(UserPreferences).where(UserPreferences.user_id == user_uuid)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Preferences already exist"
        )

    preferences = UserPreferences(
        user_id=user_uuid,
        notification_email=payload.notification_email,
        notification_sms=payload.notification_sms,
        notification_push=payload.notification_push,
        theme=payload.theme,
        language=payload.language,
        tenant_id=payload.tenant_id,
    )
    session.add(preferences)
    await session.commit()
    await session.refresh(preferences)
    return UserPreferencesRead.model_validate(preferences)


@router.patch("/api/v1/users/{user_id}/preferences", response_model=UserPreferencesRead)
async def update_user_preferences(
    user_id: str,
    payload: UserPreferencesUpdate,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserPreferencesRead:
    """Update user preferences."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found")

    result = await session.execute(
        select(UserPreferences).where(UserPreferences.user_id == user_uuid)
    )
    preferences = result.scalar_one_or_none()
    if not preferences:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(preferences, field, value)

    preferences.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(preferences)
    return UserPreferencesRead.model_validate(preferences)


@router.put("/api/v1/users/{user_id}/preferences", response_model=UserPreferencesRead)
async def put_update_user_preferences(
    user_id: str,
    payload: UserPreferencesUpdate,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserPreferencesRead:
    return await update_user_preferences(
        user_id=user_id, payload=payload, session=session, claims=claims
    )


# Current user preferences endpoints
@router.get("/api/v1/users/me/preferences", response_model=UserPreferencesRead)
async def get_current_user_preferences(
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserPreferencesRead:
    """Get current user's preferences."""
    # Get user by email from claims
    result = await session.execute(select(User).where(User.email == claims.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Get preferences for this user
    prefs_result = await session.execute(
        select(UserPreferences).where(UserPreferences.user_id == user.id)
    )
    preferences = prefs_result.scalar_one_or_none()
    if not preferences:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found")
    return UserPreferencesRead.model_validate(preferences)


@router.patch("/api/v1/users/me/preferences", response_model=UserPreferencesRead)
@router.put("/api/v1/users/me/preferences", response_model=UserPreferencesRead)
async def update_current_user_preferences(
    payload: UserPreferencesUpdate,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserPreferencesRead:
    """Update current user's preferences."""
    # Get user by email from claims
    result = await session.execute(select(User).where(User.email == claims.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Get preferences for this user
    prefs_result = await session.execute(
        select(UserPreferences).where(UserPreferences.user_id == user.id)
    )
    preferences = prefs_result.scalar_one_or_none()
    if not preferences:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preferences not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(preferences, field, value)

    preferences.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(preferences)
    return UserPreferencesRead.model_validate(preferences)


# ============================================================================
# USER ACTIVITY ENDPOINTS
# ============================================================================


@router.get("/api/v1/users/{user_id}/activity", response_model=list[UserActivityRead])
async def get_user_activity(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action: str | None = Query(None, description="Filter by action"),
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> list[UserActivityRead]:
    """Get user activity log."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return []

    query = select(UserActivity).where(UserActivity.user_id == user_uuid)

    if action:
        query = query.where(UserActivity.action == action)

    query = query.order_by(UserActivity.timestamp.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    activities = result.scalars().all()

    return [UserActivityRead.model_validate(activity) for activity in activities]


@router.post(
    "/api/v1/users/{user_id}/activity",
    response_model=UserActivityRead,
    status_code=status.HTTP_201_CREATED,
)
async def log_user_activity(
    user_id: str,
    action: str,
    resource: str | None = None,
    details: dict | None = None,
    tenant_id: str | None = None,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> UserActivityRead:
    """Log user activity."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verify user exists
    user_result = await session.execute(select(User).where(User.id == user_uuid))
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    activity = UserActivity(
        user_id=user_uuid,
        action=action,
        resource=resource,
        details=details,
        tenant_id=tenant_id,
    )
    session.add(activity)
    await session.commit()
    await session.refresh(activity)
    return UserActivityRead.model_validate(activity)


# ============================================================================
# USER SESSIONS ENDPOINTS
# ============================================================================


@router.get("/api/v1/users/{user_id}/sessions", response_model=list[UserSessionRead])
async def get_user_sessions(
    user_id: str,
    active_only: bool = Query(False, description="Show only active sessions"),
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> list[UserSessionRead]:
    """Get user sessions."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        return []

    query = select(UserSession).where(UserSession.user_id == user_uuid)

    if active_only:
        query = query.where(not UserSession.revoked)

    query = query.order_by(UserSession.last_seen.desc())
    result = await session.execute(query)
    sessions = result.scalars().all()

    return [UserSessionRead.model_validate(sess) for sess in sessions]


@router.delete(
    "/api/v1/users/{user_id}/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def revoke_user_session(
    user_id: str,
    session_id: str,
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
):
    """Revoke a user session."""
    try:
        user_uuid = UUID(user_id)
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    result = await session.execute(
        select(UserSession).where(
            and_(UserSession.id == session_uuid, UserSession.user_id == user_uuid)
        )
    )
    user_session = result.scalar_one_or_none()
    if not user_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    user_session.revoked = True
    await session.commit()


# ============================================================================
# BULK OPERATIONS
# ============================================================================


@router.post("/api/v1/users/bulk/import", response_model=dict)
async def bulk_import_users(
    file: UploadFile = File(..., description="CSV file with user data"),
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(require_role("admin", "recruiter")),
) -> dict:
    """Bulk import users from CSV file. RLS: Imports into claims tenant_id.

    CSV format: email,first_name,last_name,role,status,phone,location,tenant_id
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be CSV")

    content = await file.read()
    csv_text = content.decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(csv_text))

    created = 0
    skipped = 0
    errors = []

    for row_num, row in enumerate(csv_reader, start=2):
        try:
            email = row.get("email", "").strip()
            if not email:
                errors.append(f"Row {row_num}: Missing email")
                skipped += 1
                continue

            # Check if user exists
            existing = await session.execute(select(User).where(User.email == email))
            if existing.scalar_one_or_none():
                skipped += 1
                continue

            # RLS: Override tenant_id from CSV with claims tenant_id unless admin
            csv_tenant_id = row.get("tenant_id", "").strip() or None
            tenant_id = csv_tenant_id if claims.role == "admin" else claims.tenant_id

            user = User(
                email=email,
                first_name=row.get("first_name", "").strip() or None,
                last_name=row.get("last_name", "").strip() or None,
                phone=row.get("phone", "").strip() or None,
                role=UserRole(row.get("role", "candidate").strip()),
                status=UserStatus(row.get("status", "active").strip()),
                location=row.get("location", "").strip() or None,
                tenant_id=tenant_id,
            )
            session.add(user)
            created += 1
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
            skipped += 1

    await session.commit()

    return {
        "created": created,
        "skipped": skipped,
        "errors": errors,
    }


@router.get("/api/v1/users/bulk/export")
async def bulk_export_users(
    role: UserRole | None = Query(None),
    status: UserStatus | None = Query(None),
    tenant_id: str | None = Query(None, description="Filter by tenant (admin only)"),
    session: AsyncSession = Depends(get_session),
    claims: JWTClaims = Depends(get_jwt_claims),
) -> StreamingResponse:
    """Bulk export users to CSV file. Enforces RLS by tenant_id."""
    query = select(User)

    filters = []

    # RLS: Enforce tenant isolation unless admin
    if claims.role != "admin":
        if claims.tenant_id:
            filters.append(User.tenant_id == claims.tenant_id)
        else:
            filters.append(User.email == claims.email)
    elif tenant_id:
        filters.append(User.tenant_id == tenant_id)

    if role:
        filters.append(User.role == role)
    if status:
        filters.append(User.status == status)

    if filters:
        query = query.where(and_(*filters))

    result = await session.execute(query.order_by(User.created_at))
    users = result.scalars().all()

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "status",
            "phone",
            "location",
            "bio",
            "avatar_url",
            "tenant_id",
            "created_at",
            "updated_at",
            "last_login",
        ]
    )

    for user in users:
        writer.writerow(
            [
                str(user.id),
                user.email,
                user.first_name or "",
                user.last_name or "",
                user.role.value,
                user.status.value,
                user.phone or "",
                user.location or "",
                user.bio or "",
                user.avatar_url or "",
                user.tenant_id or "",
                user.created_at.isoformat(),
                user.updated_at.isoformat(),
                user.last_login.isoformat() if user.last_login else "",
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"},
    )
