"""
Pydantic schemas for Security Service
Defines request/response models for authentication, authorization, and encryption
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request payload"""

    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    """Authentication token response"""

    access_token: str
    token: str  # Alias for access_token
    refresh_token: str | None = None
    expires_in: int
    token_type: str = "bearer"


class UserRegistration(BaseModel):
    """User registration payload"""

    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="Must contain uppercase, lowercase, digits, and special characters",
    )
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    """User profile response"""

    email: EmailStr
    first_name: str
    last_name: str
    roles: list[str]
    permissions: list[str]
    mfa_enabled: bool


class RoleAssignment(BaseModel):
    """Role assignment payload"""

    user_id: str = Field(..., description="Email or user ID")
    role: str = Field(..., description="Role to assign (e.g., 'admin', 'user', 'recruiter')")


class PermissionCheck(BaseModel):
    """Permission check request"""

    permission: str = Field(
        ..., description="Permission to check (e.g., 'view_interviews', 'take_interview')"
    )


class PasswordChange(BaseModel):
    """Password change request"""

    current_password: str
    new_password: str = Field(..., min_length=8)


class PasswordResetRequest(BaseModel):
    """Password reset request"""

    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset with token"""

    token: str
    new_password: str = Field(..., min_length=8)


class TokenVerification(BaseModel):
    """Token verification request"""

    token: str


class MFASetupResponse(BaseModel):
    """MFA setup response"""

    secret: str
    qr_code: str


class MFAVerification(BaseModel):
    """MFA code verification"""

    code: str = Field(..., min_length=6, max_length=6)


class EncryptRequest(BaseModel):
    """Data encryption request"""

    data: str = Field(..., description="Plain text data to encrypt")


class EncryptResponse(BaseModel):
    """Encrypted data response"""

    encrypted: str
    ciphertext: str  # Alias for encrypted


class DecryptRequest(BaseModel):
    """Data decryption request"""

    encrypted: str | None = None
    ciphertext: str | None = None


class DecryptResponse(BaseModel):
    """Decrypted data response"""

    data: str
    plaintext: str  # Alias for data


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str
    details: str | None = None


class SuccessResponse(BaseModel):
    """Standard success response"""

    message: str
    data: dict | None = None
