from enum import Enum
from typing import Optional, List

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
    first_name: Optional[constr(strip_whitespace=True, min_length=1)] = None
    last_name: Optional[constr(strip_whitespace=True, min_length=1)] = None


class TokenVerifyRequest(BaseModel):
    token: constr(min_length=1)


class TokenRefreshRequest(BaseModel):
    refresh_token: constr(min_length=1)


class ProfileResponse(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str]
    permissions: List[str]
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
    encrypted: Optional[constr(min_length=1)] = Field(default=None)
    ciphertext: Optional[constr(min_length=1)] = Field(default=None)


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
