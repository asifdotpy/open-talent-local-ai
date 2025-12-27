from enum import Enum

from pydantic import BaseModel, EmailStr, Field, constr


# Enums
class Role(str, Enum):
    user = "user"
    admin = "admin"


# Auth
class LoginRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=1)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=1)
    first_name: constr(strip_whitespace=True, min_length=1) | None = None
    last_name: constr(strip_whitespace=True, min_length=1) | None = None


class TokenVerifyRequest(BaseModel):
    token: constr(min_length=1)


class TokenRefreshRequest(BaseModel):
    refresh_token: constr(min_length=1)


class ProfileResponse(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    roles: list[str]
    permissions: list[str]
    mfa_enabled: bool


# MFA
class MFAVerifyRequest(BaseModel):
    code: constr(min_length=1)


# Permissions
class PermissionCheckRequest(BaseModel):
    permission: constr(min_length=1)


# Encryption
class EncryptRequest(BaseModel):
    data: constr(min_length=1)


class DecryptRequest(BaseModel):
    encrypted: constr(min_length=1) | None = Field(default=None)
    ciphertext: constr(min_length=1) | None = Field(default=None)


# Password management
class ChangePasswordRequest(BaseModel):
    current_password: constr(min_length=1)
    new_password: constr(min_length=1)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetWithTokenRequest(BaseModel):
    token: constr(min_length=1)
    new_password: constr(min_length=1)


# Roles
class AssignRoleRequest(BaseModel):
    user_id: constr(min_length=1)
    role: Role


class RevokeRoleRequest(BaseModel):
    user_id: constr(min_length=1)
    role: Role
