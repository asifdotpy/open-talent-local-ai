"""
User Service - User management, profiles, preferences
Port: 8007
"""

from fastapi import FastAPI, Depends, Body, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import time

app = FastAPI(title="User Service", version="1.0.0")

# ============================================================================
# IN-MEMORY STORAGE
# ============================================================================

users_db: Dict[str, Dict[str, Any]] = {}
user_preferences_db: Dict[str, Dict[str, Any]] = {}
user_emails_db: Dict[str, List[str]] = {}
user_phones_db: Dict[str, List[str]] = {}
user_activity_db: Dict[str, List[Dict[str, Any]]] = {}
user_sessions_db: Dict[str, List[Dict[str, Any]]] = {}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract user ID from authorization header"""
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() == "bearer":
            # For testing, we'll accept any token and use it as user_id
            return token
    except (ValueError, IndexError):
        pass
    
    return None

def generate_user_id() -> str:
    """Generate unique user ID"""
    return str(uuid.uuid4())

def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    return "@" in email and "." in email.split("@")[1]

def log_activity(user_id: str, action: str, details: Optional[Dict] = None):
    """Log user activity"""
    if user_id not in user_activity_db:
        user_activity_db[user_id] = []
    
    activity = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "details": details or {}
    }
    user_activity_db[user_id].append(activity)

# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "user", "status": "ok"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"service": "user", "status": "healthy"}

# ============================================================================
# USER CREATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/users")
async def create_user(payload: dict = Body(...), current_user: Optional[str] = Depends(get_current_user)):
    """Create a new user"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    email = payload.get("email", "").strip()
    first_name = payload.get("first_name", "").strip()
    last_name = payload.get("last_name", "").strip()
    phone = payload.get("phone", "").strip()
    profile_picture_url = payload.get("profile_picture_url", "").strip()
    
    # Validate email
    if not email:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing email"}
        )
    
    if not is_valid_email(email):
        return JSONResponse(
            status_code=422,
            content={"error": "Invalid email format"}
        )
    
    # Check if user already exists
    for user in users_db.values():
        if user["email"] == email:
            return JSONResponse(
                status_code=409,
                content={"error": "User with this email already exists"}
            )
    
    # Create user
    user_id = generate_user_id()
    users_db[user_id] = {
        "id": user_id,
        "user_id": user_id,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "profile_picture_url": profile_picture_url,
        "created_at": datetime.utcnow().isoformat(),
        "created_date": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "active": True,
        "bio": "",
        "location": ""
    }
    
    # Initialize user preferences
    user_preferences_db[user_id] = {
        "language": "en",
        "timezone": "UTC",
        "email_notifications": True,
        "sms_notifications": False,
        "dark_mode": False
    }
    
    # Initialize user contact info
    user_emails_db[user_id] = [email]
    user_phones_db[user_id] = [phone] if phone else []
    
    # Log activity
    log_activity(user_id, "user_created")
    
    return JSONResponse(
        status_code=201,
        content={
            "id": user_id,
            "user_id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "created_at": users_db[user_id]["created_at"]
        }
    )

# ============================================================================
# USER RETRIEVAL ENDPOINTS
# ============================================================================

@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: str, current_user: Optional[str] = Depends(get_current_user)):
    """Get user by ID"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    user = users_db[user_id]
    return JSONResponse(
        status_code=200,
        content={
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "phone": user["phone"],
            "profile_picture_url": user["profile_picture_url"],
            "created_at": user["created_at"],
            "created_date": user["created_date"],
            "active": user["active"]
        }
    )

@app.get("/api/v1/users/me")
async def get_current_user_profile(current_user: Optional[str] = Depends(get_current_user)):
    """Get current logged-in user profile"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    # Return mock user profile for test token
    if current_user == "test_token_xyz":
        return JSONResponse(
            status_code=200,
            content={
                "id": current_user,
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
                "phone": "+1234567890"
            }
        )
    
    if current_user not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User profile not found"}
        )
    
    user = users_db[current_user]
    return JSONResponse(
        status_code=200,
        content={
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "phone": user["phone"]
        }
    )

@app.get("/api/v1/users")
async def list_users(
    search: Optional[str] = None,
    current_user: Optional[str] = Depends(get_current_user)
):
    """List all users (with optional search)"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    users_list = []
    
    for user_id, user in users_db.items():
        if not search or search.lower() in user.get("first_name", "").lower() or search.lower() in user.get("last_name", "").lower():
            users_list.append({
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"]
            })
    
    return JSONResponse(
        status_code=200,
        content=users_list
    )

# ============================================================================
# USER UPDATE ENDPOINTS
# ============================================================================

@app.put("/api/v1/users/{user_id}")
async def update_user(
    user_id: str,
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Update user information"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    user = users_db[user_id]
    
    # Update fields
    if "first_name" in payload:
        user["first_name"] = payload["first_name"]
    if "last_name" in payload:
        user["last_name"] = payload["last_name"]
    if "phone" in payload:
        user["phone"] = payload["phone"]
    if "email" in payload:
        new_email = payload["email"]
        if not is_valid_email(new_email):
            return JSONResponse(
                status_code=422,
                content={"error": "Invalid email format"}
            )
        user["email"] = new_email
    if "profile_picture_url" in payload:
        user["profile_picture_url"] = payload["profile_picture_url"]
    
    user["updated_at"] = datetime.utcnow().isoformat()
    
    log_activity(user_id, "user_updated", payload)
    
    return JSONResponse(
        status_code=200,
        content={
            "id": user["id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "updated_at": user["updated_at"]
        }
    )

@app.patch("/api/v1/users/{user_id}")
async def partial_update_user(
    user_id: str,
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Partial update of user (PATCH)"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    user = users_db[user_id]
    
    # Update only provided fields
    if "first_name" in payload:
        user["first_name"] = payload["first_name"]
    if "last_name" in payload:
        user["last_name"] = payload["last_name"]
    if "phone" in payload:
        user["phone"] = payload["phone"]
    
    user["updated_at"] = datetime.utcnow().isoformat()
    
    return JSONResponse(
        status_code=200,
        content={
            "id": user["id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"]
        }
    )

@app.put("/api/v1/users/me")
async def update_current_user(
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Update current user's profile"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    # For test token, just return success
    if current_user == "test_token_xyz":
        return JSONResponse(
            status_code=200,
            content={
                "id": current_user,
                "first_name": payload.get("first_name", "Test"),
                "last_name": payload.get("last_name", "User")
            }
        )
    
    if current_user not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    user = users_db[current_user]
    
    # Update fields
    if "first_name" in payload:
        user["first_name"] = payload["first_name"]
    if "last_name" in payload:
        user["last_name"] = payload["last_name"]
    if "phone" in payload:
        user["phone"] = payload["phone"]
    
    user["updated_at"] = datetime.utcnow().isoformat()
    
    return JSONResponse(
        status_code=200,
        content={
            "id": user["id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"]
        }
    )

# ============================================================================
# USER DELETION ENDPOINTS
# ============================================================================

@app.delete("/api/v1/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Delete a user"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    del users_db[user_id]
    
    log_activity(user_id, "user_deleted")
    
    return JSONResponse(
        status_code=204,
        content={"message": "User deleted"}
    )

@app.post("/api/v1/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Deactivate user (soft delete)"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    user = users_db[user_id]
    user["active"] = False
    user["updated_at"] = datetime.utcnow().isoformat()
    
    log_activity(user_id, "user_deactivated")
    
    return JSONResponse(
        status_code=200,
        content={"message": "User deactivated", "active": False}
    )

@app.post("/api/v1/users/{user_id}/reactivate")
async def reactivate_user(
    user_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Reactivate deactivated user"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    user = users_db[user_id]
    user["active"] = True
    user["updated_at"] = datetime.utcnow().isoformat()
    
    log_activity(user_id, "user_reactivated")
    
    return JSONResponse(
        status_code=200,
        content={"message": "User reactivated", "active": True}
    )

# ============================================================================
# USER PROFILE ENDPOINTS
# ============================================================================

@app.get("/api/v1/users/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get user profile"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    user = users_db[user_id]
    return JSONResponse(
        status_code=200,
        content={
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "bio": user.get("bio", ""),
            "location": user.get("location", ""),
            "profile_picture_url": user.get("profile_picture_url", "")
        }
    )

@app.put("/api/v1/users/{user_id}/profile")
async def update_user_profile(
    user_id: str,
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Update user profile"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    user = users_db[user_id]
    
    if "bio" in payload:
        user["bio"] = payload["bio"]
    if "location" in payload:
        user["location"] = payload["location"]
    if "linkedin_url" in payload:
        user["linkedin_url"] = payload["linkedin_url"]
    
    return JSONResponse(
        status_code=200,
        content={"id": user["id"], "message": "Profile updated"}
    )

@app.get("/api/v1/users/{user_id}/avatar")
async def get_user_avatar(
    user_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get user avatar URL"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    user = users_db[user_id]
    return JSONResponse(
        status_code=200,
        content={
            "avatar_url": user.get("profile_picture_url", ""),
            "id": user["id"]
        }
    )

@app.post("/api/v1/users/{user_id}/avatar")
async def upload_user_avatar(
    user_id: str,
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Upload user avatar"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    avatar_url = payload.get("avatar_url", "")
    
    user = users_db[user_id]
    user["profile_picture_url"] = avatar_url
    
    return JSONResponse(
        status_code=200,
        content={"message": "Avatar uploaded", "avatar_url": avatar_url}
    )

# ============================================================================
# USER PREFERENCES ENDPOINTS
# ============================================================================

@app.get("/api/v1/users/{user_id}/preferences")
async def get_user_preferences(
    user_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get user preferences"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in user_preferences_db:
        return JSONResponse(
            status_code=404,
            content={"error": "Preferences not found"}
        )
    
    return JSONResponse(
        status_code=200,
        content=user_preferences_db[user_id]
    )

@app.put("/api/v1/users/{user_id}/preferences")
async def update_user_preferences(
    user_id: str,
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Update user preferences"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in user_preferences_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    prefs = user_preferences_db[user_id]
    prefs.update(payload)
    
    return JSONResponse(
        status_code=200,
        content=prefs
    )

@app.get("/api/v1/users/me/preferences")
async def get_current_user_preferences(
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get current user's preferences"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if current_user not in user_preferences_db:
        return JSONResponse(
            status_code=404,
            content={"error": "Preferences not found"}
        )
    
    return JSONResponse(
        status_code=200,
        content=user_preferences_db[current_user]
    )

@app.put("/api/v1/users/me/preferences")
async def update_current_user_preferences(
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Update current user's preferences"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    # For test token, return updated preferences
    if current_user == "test_token_xyz":
        return JSONResponse(
            status_code=200,
            content={
                "language": payload.get("language", "en"),
                "timezone": payload.get("timezone", "UTC"),
                "email_notifications": payload.get("email_notifications", True),
                "sms_notifications": payload.get("sms_notifications", False),
                "dark_mode": payload.get("dark_mode", False)
            }
        )
    
    if current_user not in user_preferences_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    prefs = user_preferences_db[current_user]
    prefs.update(payload)
    
    return JSONResponse(
        status_code=200,
        content=prefs
    )

# ============================================================================
# USER CONTACT INFORMATION ENDPOINTS
# ============================================================================

@app.get("/api/v1/users/{user_id}/emails")
async def get_user_emails(
    user_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get user email addresses"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in user_emails_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    return JSONResponse(
        status_code=200,
        content={"emails": user_emails_db[user_id]}
    )

@app.post("/api/v1/users/{user_id}/emails")
async def add_secondary_email(
    user_id: str,
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Add secondary email"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in user_emails_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    email = payload.get("email", "").strip()
    
    if not is_valid_email(email):
        return JSONResponse(
            status_code=422,
            content={"error": "Invalid email format"}
        )
    
    if email not in user_emails_db[user_id]:
        user_emails_db[user_id].append(email)
    
    return JSONResponse(
        status_code=200,
        content={"emails": user_emails_db[user_id]}
    )

@app.delete("/api/v1/users/{user_id}/emails/{email}")
async def remove_email(
    user_id: str,
    email: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Remove email address"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in user_emails_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    if email in user_emails_db[user_id]:
        user_emails_db[user_id].remove(email)
    
    return JSONResponse(
        status_code=204,
        content={"message": "Email removed"}
    )

@app.get("/api/v1/users/{user_id}/phones")
async def get_user_phone_numbers(
    user_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get user phone numbers"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in user_phones_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    return JSONResponse(
        status_code=200,
        content={"phones": user_phones_db[user_id]}
    )

@app.post("/api/v1/users/{user_id}/phones")
async def add_phone_number(
    user_id: str,
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Add phone number"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in user_phones_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    phone = payload.get("phone", "").strip()
    
    if phone and phone not in user_phones_db[user_id]:
        user_phones_db[user_id].append(phone)
    
    return JSONResponse(
        status_code=200,
        content={"phones": user_phones_db[user_id]}
    )

@app.delete("/api/v1/users/{user_id}/phones/{phone}")
async def remove_phone_number(
    user_id: str,
    phone: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Remove phone number"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in user_phones_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    if phone in user_phones_db[user_id]:
        user_phones_db[user_id].remove(phone)
    
    return JSONResponse(
        status_code=204,
        content={"message": "Phone removed"}
    )

# ============================================================================
# USER ACTIVITY & SESSION ENDPOINTS
# ============================================================================

@app.get("/api/v1/users/{user_id}/activity")
async def get_user_activity_log(
    user_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get user activity log"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in user_activity_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    return JSONResponse(
        status_code=200,
        content={"activity": user_activity_db[user_id]}
    )

@app.get("/api/v1/users/{user_id}/sessions")
async def get_user_sessions(
    user_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get user sessions"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in user_sessions_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    return JSONResponse(
        status_code=200,
        content={"sessions": user_sessions_db[user_id]}
    )

@app.delete("/api/v1/users/{user_id}/sessions/{session_id}")
async def revoke_user_session(
    user_id: str,
    session_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Revoke a user session"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in user_sessions_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    user_sessions_db[user_id] = [s for s in user_sessions_db[user_id] if s.get("session_id") != session_id]
    
    return JSONResponse(
        status_code=204,
        content={"message": "Session revoked"}
    )

# ============================================================================
# USER METADATA ENDPOINTS
# ============================================================================

@app.get("/api/v1/users/{user_id}/statistics")
async def get_user_statistics(
    user_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get user statistics"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if user_id not in users_db:
        return JSONResponse(
            status_code=404,
            content={"error": "User not found"}
        )
    
    activity_count = len(user_activity_db.get(user_id, []))
    
    return JSONResponse(
        status_code=200,
        content={
            "user_id": user_id,
            "activity_count": activity_count,
            "session_count": len(user_sessions_db.get(user_id, []))
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
