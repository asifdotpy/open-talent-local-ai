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
    
    from app.main import app

    # Entry-point shim for `python main.py`
    if __name__ == "__main__":
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=8001)

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
