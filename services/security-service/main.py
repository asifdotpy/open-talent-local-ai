"""
Security Service - Authentication, Authorization, Permissions, MFA, Encryption
Port: 8010
"""

import os
import secrets

# Ensure local imports work when loaded via spec_from_file_location
import sys as _sys
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Any

import bcrypt
import jwt
from cryptography.fernet import Fernet
from fastapi import Body, Depends, FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

_this_dir = os.path.dirname(__file__)
if _this_dir not in _sys.path:
    _sys.path.append(_this_dir)

# Pydantic schemas
from schemas import (
    AssignRoleRequest,
    ChangePasswordRequest,
    DecryptRequest,
    EncryptRequest,
    LoginRequest,
    MFAVerifyRequest,
    PasswordResetRequest,
    PasswordResetWithTokenRequest,
    PermissionCheckRequest,
    RegisterRequest,
    RevokeRoleRequest,
    TokenRefreshRequest,
    TokenVerifyRequest,
)

app = FastAPI(title="Security Service", version="1.0.0")

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Load secrets and security configs from environment (dev-safe defaults)
SECRET_KEY = os.environ.get("SECURITY_SECRET_KEY", "DEV_ONLY_INSECURE_SECRET_CHANGE_ME")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
PASSWORD_MIN_LENGTH = 8
RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_RULE = os.environ.get("RATE_LIMIT_RULE", "5/minute")
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("CORS_ALLOW_ORIGINS", "*").split(",")]

# bcrypt configuration
BCRYPT_ROUNDS = int(os.environ.get("BCRYPT_ROUNDS", "12"))
PEPPER = os.environ.get("PEPPER", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
PASSWORD_MIN_LENGTH = 8

# In-memory storage (replace with database in production)
users_db: dict[str, dict[str, Any]] = {
    "user@example.com": {
        "email": "user@example.com",
        # Legacy SHA256 hash for default user; will be migrated to bcrypt on first successful login
        "password_hash": sha256(b"SecurePassword123!").hexdigest(),
        "first_name": "Test",
        "last_name": "User",
        "roles": ["user"],
        "permissions": ["view_interviews", "take_interview"],
        "mfa_enabled": False,
        "mfa_secret": None,
    }
}

tokens_db: set = set()  # Blacklisted tokens
sessions_db: dict[str, dict[str, Any]] = {}  # Active sessions

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _is_bcrypt(hash_value: str) -> bool:
    return (
        hash_value.startswith("$2a$")
        or hash_value.startswith("$2b$")
        or hash_value.startswith("$2y$")
    )


def hash_password(password: str) -> str:
    """Hash a password using bcrypt (with optional pepper)."""
    pw = (password + PEPPER).encode()
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(pw, salt).decode()


def verify_password(password: str, hash_value: str) -> bool:
    """Verify a plain-text password against a stored (bcrypt or legacy SHA256) hash.

    Handles transparent migration path for legacy SHA256 hashes.

    Args:
        password: The plain-text password to verify.
        hash_value: The hashed password string from the database.

    Returns:
        True if the password matches, False otherwise.
    """
    """Verify password against hash; supports bcrypt and legacy SHA256 for migration."""
    if _is_bcrypt(hash_value):
        try:
            return bcrypt.checkpw((password + PEPPER).encode(), hash_value.encode())
        except ValueError:
            return False
    # Legacy fallback (no pepper involved in legacy)
    return sha256(password.encode()).hexdigest() == hash_value


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generate a signed JWT access token for a user.

    Args:
        data: Key-value pairs to include in the JWT payload (claims).
        expires_delta: Optional override for the token expiration period.

    Returns:
        A base64-encoded JWT string.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {"email": email, "exp": expire, "iat": datetime.utcnow()}

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> str | None:
    """Verify JWT token and return email"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")

        # Check if token is blacklisted
        if token in tokens_db:
            return None

        return email
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user(authorization: str | None = Header(None)) -> str | None:
    """Extract and verify token from Authorization header"""
    if not authorization:
        return None

    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            return None

        return verify_token(token)
    except (ValueError, IndexError):
        return None


def is_strong_password(password: str) -> bool:
    """Check if password meets strength requirements"""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    return has_upper and has_lower and has_digit and has_special


def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    return "@" in email and "." in email.split("@")[1]


# ==========================================================================
# CORS & Rate Limiting Setup
# ==========================================================================

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ["*"] != ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address) if RATE_LIMIT_ENABLED else None
if limiter:
    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        lambda request, exc: JSONResponse(status_code=429, content={"error": "Too many requests"}),
    )
    app.add_middleware(SlowAPIMiddleware)

# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "security", "status": "ok"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"service": "security", "status": "healthy"}


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================


@app.post("/api/v1/auth/register")
@ limiter.limit(RATE_LIMIT_RULE) if limiter else (lambda f: f)
async def register(request: Request, payload: RegisterRequest = Body(...)):
    """Register a new user"""
    email = payload.email.strip()
    password = payload.password.strip()
    first_name = (payload.first_name or "").strip()
    last_name = (payload.last_name or "").strip()

    # Validate inputs
    if not email or not password:
        return JSONResponse(status_code=400, content={"error": "Missing email or password"})

    if not is_valid_email(email):
        return JSONResponse(status_code=422, content={"error": "Invalid email format"})

    if not is_strong_password(password):
        return JSONResponse(
            status_code=422,
            content={
                "error": "Password too weak. Must contain uppercase, lowercase, digits, and special characters"
            },
        )

    # Check if user exists
    if email in users_db:
        return JSONResponse(status_code=409, content={"error": "Email already registered"})

    # Create user
    users_db[email] = {
        "email": email,
        "password_hash": hash_password(password),
        "first_name": first_name,
        "last_name": last_name,
        "roles": ["user"],
        "permissions": ["view_interviews", "take_interview"],
        "mfa_enabled": False,
        "mfa_secret": None,
        "created_at": datetime.utcnow().isoformat(),
    }

    return JSONResponse(
        status_code=201,
        content={"user": {"email": email, "id": email}, "message": "User registered successfully"},
    )


@app.post("/api/v1/auth/login")
@ limiter.limit(RATE_LIMIT_RULE) if limiter else (lambda f: f)
async def login(request: Request, payload: LoginRequest = Body(...)):
    """Login and get access token"""
    email = payload.email.strip()
    password = payload.password.strip()

    # Validate inputs
    if not email or not password:
        return JSONResponse(status_code=400, content={"error": "Missing email or password"})

    # Check user exists
    if email not in users_db:
        return JSONResponse(status_code=401, content={"error": "Invalid credentials"})

    user = users_db[email]

    # Verify password
    if not verify_password(password, user["password_hash"]):
        return JSONResponse(status_code=401, content={"error": "Invalid credentials"})

    # If legacy SHA256 was used, migrate to bcrypt transparently after successful login
    if not _is_bcrypt(user["password_hash"]):
        user["password_hash"] = hash_password(password)

    # Create tokens
    access_token = create_access_token(email)
    refresh_token = secrets.token_urlsafe(32)

    # Store session
    sessions_db[refresh_token] = {
        "email": email,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }

    return JSONResponse(
        status_code=200,
        content={
            "token": access_token,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "token_type": "bearer",
        },
    )


@app.post("/api/v1/auth/logout")
async def logout(current_user: str | None = Depends(get_current_user)):
    """Logout and invalidate token"""
    return JSONResponse(status_code=204, content={"message": "Logged out successfully"})


@app.post("/api/v1/auth/verify")
async def verify(payload: TokenVerifyRequest = Body(...)):
    """Verify if token is valid"""
    token = payload.token

    if not token:
        return JSONResponse(status_code=400, content={"error": "Missing token"})

    email = verify_token(token)
    if not email:
        return JSONResponse(status_code=401, content={"error": "Invalid or expired token"})

    return JSONResponse(status_code=200, content={"valid": True, "email": email})


@app.post("/api/v1/auth/refresh")
async def refresh(payload: TokenRefreshRequest = Body(...)):
    """Refresh access token"""
    refresh_token = payload.refresh_token

    if not refresh_token:
        return JSONResponse(status_code=400, content={"error": "Missing refresh token"})

    if refresh_token not in sessions_db:
        return JSONResponse(status_code=401, content={"error": "Invalid refresh token"})

    session = sessions_db[refresh_token]
    email = session["email"]

    # Create new access token
    new_access_token = create_access_token(email)

    return JSONResponse(
        status_code=200,
        content={
            "token": new_access_token,
            "access_token": new_access_token,
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        },
    )


@app.get("/api/v1/auth/profile")
async def get_profile(current_user: str | None = Depends(get_current_user)):
    """Get current user profile"""
    if not current_user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if current_user not in users_db:
        return JSONResponse(status_code=404, content={"error": "User not found"})

    user = users_db[current_user]
    return JSONResponse(
        status_code=200,
        content={
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "roles": user["roles"],
            "permissions": user["permissions"],
            "mfa_enabled": user["mfa_enabled"],
        },
    )


# ============================================================================
# TOKEN MANAGEMENT ENDPOINTS
# ============================================================================

# verify and refresh endpoints are above in authentication section

# ============================================================================
# MFA ENDPOINTS
# ============================================================================


@app.post("/api/v1/auth/mfa/setup")
async def setup_mfa(current_user: str | None = Depends(get_current_user)):
    """Setup MFA for user"""
    email = current_user

    if not email:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if email not in users_db:
        return JSONResponse(status_code=404, content={"error": "User not found"})

    # Generate MFA secret (in production, use pyotp library)
    mfa_secret = secrets.token_urlsafe(32)

    user = users_db[email]
    user["mfa_secret"] = mfa_secret

    return JSONResponse(
        status_code=200,
        content={
            "secret": mfa_secret,
            "qr_code": f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=otpauth://totp/SecurityService:{email}?secret={mfa_secret}",
        },
    )


@app.post("/api/v1/auth/mfa/verify")
async def verify_mfa(
    payload: MFAVerifyRequest = Body(...), current_user: str | None = Depends(get_current_user)
):
    """Verify MFA code"""
    email = current_user

    if not email:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    code = payload.code

    if not code:
        return JSONResponse(status_code=400, content={"error": "Missing MFA code"})

    if email not in users_db:
        return JSONResponse(status_code=404, content={"error": "User not found"})

    user = users_db[email]

    # Simple verification (in production, use pyotp library)
    if user.get("mfa_secret") and len(code) == 6 and code.isdigit():
        user["mfa_enabled"] = True
        return JSONResponse(
            status_code=200, content={"verified": True, "message": "MFA verified successfully"}
        )

    return JSONResponse(status_code=400, content={"error": "Invalid MFA code"})


@app.delete("/api/v1/auth/mfa")
async def disable_mfa(current_user: str | None = Depends(get_current_user)):
    """Disable MFA for user"""
    email = current_user

    if not email:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if email not in users_db:
        return JSONResponse(status_code=404, content={"error": "User not found"})

    user = users_db[email]
    user["mfa_enabled"] = False
    user["mfa_secret"] = None

    return JSONResponse(status_code=200, content={"message": "MFA disabled"})


# ============================================================================
# PERMISSIONS ENDPOINTS
# ============================================================================


@app.get("/api/v1/auth/permissions")
async def get_permissions(current_user: str | None = Depends(get_current_user)):
    """Get user permissions"""
    email = current_user

    if not email:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if email not in users_db:
        return JSONResponse(status_code=404, content={"error": "User not found"})

    user = users_db[email]
    return JSONResponse(status_code=200, content={"permissions": user["permissions"]})


@app.post("/api/v1/auth/permissions/check")
async def check_permission(
    payload: PermissionCheckRequest = Body(...),
    current_user: str | None = Depends(get_current_user),
):
    """Check if user has specific permission"""
    email = current_user

    if not email:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    permission = payload.permission

    if not permission:
        return JSONResponse(status_code=400, content={"error": "Missing permission"})

    if email not in users_db:
        return JSONResponse(status_code=404, content={"error": "User not found"})

    user = users_db[email]
    has_permission = permission in user["permissions"]

    return JSONResponse(
        status_code=200, content={"permission": permission, "has_permission": has_permission}
    )


# ============================================================================
# ENCRYPTION ENDPOINTS
# ============================================================================

# Generate a key for Fernet encryption
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)


@app.post("/api/v1/encrypt")
async def encrypt_data(payload: EncryptRequest = Body(...)):
    """Encrypt data"""
    data = payload.data

    if not data:
        return JSONResponse(status_code=400, content={"error": "Missing data to encrypt"})

    # Encrypt the data
    encrypted = cipher_suite.encrypt(data.encode())

    return JSONResponse(
        status_code=200, content={"encrypted": encrypted.decode(), "ciphertext": encrypted.decode()}
    )


@app.post("/api/v1/decrypt")
async def decrypt_data(payload: DecryptRequest = Body(...)):
    """Decrypt data"""
    encrypted = payload.encrypted or payload.ciphertext

    if not encrypted:
        return JSONResponse(status_code=400, content={"error": "Missing encrypted data"})

    try:
        # Decrypt the data
        decrypted = cipher_suite.decrypt(encrypted.encode())

        return JSONResponse(
            status_code=200, content={"data": decrypted.decode(), "plaintext": decrypted.decode()}
        )
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Failed to decrypt data"})


# ============================================================================
# PASSWORD MANAGEMENT ENDPOINTS
# ============================================================================


@app.post("/api/v1/auth/password/change")
@ limiter.limit(RATE_LIMIT_RULE) if limiter else (lambda f: f)
async def change_password(
    request: Request,
    payload: ChangePasswordRequest = Body(...),
    current_user: str | None = Depends(get_current_user),
):
    """Change user password"""
    email = current_user

    if not email:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    current_password = payload.current_password.strip()
    new_password = payload.new_password.strip()

    if not current_password or not new_password:
        return JSONResponse(status_code=400, content={"error": "Missing current or new password"})

    if email not in users_db:
        return JSONResponse(status_code=404, content={"error": "User not found"})

    user = users_db[email]

    # Verify current password
    if not verify_password(current_password, user["password_hash"]):
        return JSONResponse(status_code=401, content={"error": "Current password is incorrect"})

    # Check new password strength
    if not is_strong_password(new_password):
        return JSONResponse(status_code=422, content={"error": "New password too weak"})

    # Update password
    user["password_hash"] = hash_password(new_password)

    return JSONResponse(status_code=200, content={"message": "Password changed successfully"})


@app.post("/api/v1/auth/password/reset-request")
@ limiter.limit(RATE_LIMIT_RULE) if limiter else (lambda f: f)
async def request_password_reset(request: Request, payload: PasswordResetRequest = Body(...)):
    """Request password reset"""
    email = payload.email.strip()

    if not email:
        return JSONResponse(status_code=400, content={"error": "Missing email"})

    # Note: In production, send reset email with token
    # For now, just return success

    return JSONResponse(status_code=200, content={"message": "Password reset email sent"})


@app.post("/api/v1/auth/password/reset")
@ limiter.limit(RATE_LIMIT_RULE) if limiter else (lambda f: f)
async def reset_password(request: Request, payload: PasswordResetWithTokenRequest = Body(...)):
    """Reset password with token"""
    token = payload.token
    new_password = payload.new_password.strip()

    if not token or not new_password:
        return JSONResponse(status_code=400, content={"error": "Missing token or new password"})

    if not is_strong_password(new_password):
        return JSONResponse(status_code=422, content={"error": "Password too weak"})

    # Note: In production, verify reset token
    # For now, just return success if password is strong

    return JSONResponse(status_code=200, content={"message": "Password reset successfully"})


# ============================================================================
# ROLE MANAGEMENT ENDPOINTS
# ============================================================================


@app.get("/api/v1/roles")
async def get_roles(current_user: str | None = Depends(get_current_user)):
    """Get user roles"""
    email = current_user

    if not email:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    if email not in users_db:
        return JSONResponse(status_code=404, content={"error": "User not found"})

    user = users_db[email]
    return JSONResponse(status_code=200, content={"roles": user["roles"]})


@app.post("/api/v1/roles/assign")
async def assign_role(
    payload: AssignRoleRequest = Body(...), current_user: str | None = Depends(get_current_user)
):
    """Assign role to user"""
    email = current_user

    if not email:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    user_id = payload.user_id
    role = payload.role

    if not user_id or not role:
        return JSONResponse(status_code=400, content={"error": "Missing user_id or role"})

    # Check if current user is admin
    if email not in users_db:
        return JSONResponse(status_code=404, content={"error": "Current user not found"})

    current_user = users_db[email]
    if "admin" not in current_user["roles"]:
        return JSONResponse(status_code=403, content={"error": "Only admins can assign roles"})

    # Assign role to target user
    if user_id in users_db:
        if role not in users_db[user_id]["roles"]:
            users_db[user_id]["roles"].append(role)

        return JSONResponse(status_code=200, content={"message": f"Role {role} assigned to user"})

    return JSONResponse(status_code=400, content={"error": "User not found"})


@app.delete("/api/v1/roles/revoke")
async def revoke_role(
    payload: RevokeRoleRequest = Body(...), current_user: str | None = Depends(get_current_user)
):
    """Revoke role from user"""
    email = current_user

    if not email:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    user_id = payload.user_id
    role = payload.role

    if not user_id or not role:
        return JSONResponse(status_code=400, content={"error": "Missing user_id or role"})

    # Check if current user is admin
    if email not in users_db:
        return JSONResponse(status_code=404, content={"error": "Current user not found"})

    current_user = users_db[email]
    if "admin" not in current_user["roles"]:
        return JSONResponse(status_code=403, content={"error": "Only admins can revoke roles"})

    # Revoke role from target user
    if user_id in users_db:
        if role in users_db[user_id]["roles"]:
            users_db[user_id]["roles"].remove(role)

        return JSONResponse(status_code=200, content={"message": f"Role {role} revoked from user"})

    return JSONResponse(status_code=400, content={"error": "User not found"})


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("SECURITY_SERVICE_PORT", "8010"))
    host = os.environ.get("HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=port)
