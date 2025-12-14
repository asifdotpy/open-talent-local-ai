"""
Candidate Service - Candidate management, applications, profiles
Port: 8008
"""

from fastapi import FastAPI, Depends, Body, Header
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import time

app = FastAPI(title="Candidate Service", version="1.0.0")

# ============================================================================
# IN-MEMORY STORAGE
# ============================================================================

candidates_db: Dict[str, Dict[str, Any]] = {}
applications_db: Dict[str, Dict[str, Any]] = {}
candidate_skills_db: Dict[str, List[Dict[str, Any]]] = {}

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
            return token
    except (ValueError, IndexError):
        pass
    
    return None

def generate_id() -> str:
    """Generate unique ID"""
    return str(uuid.uuid4())

# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "candidate", "status": "ok"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"service": "candidate", "status": "healthy"}

# ============================================================================
# CANDIDATE MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/v1/candidates")
async def create_candidate(
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Create a new candidate"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    email = payload.get("email", "").strip()
    first_name = payload.get("first_name", "").strip()
    last_name = payload.get("last_name", "").strip()
    phone = payload.get("phone", "").strip()
    resume_url = payload.get("resume_url", "").strip()
    
    candidate_id = generate_id()
    candidates_db[candidate_id] = {
        "id": candidate_id,
        "candidate_id": candidate_id,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "resume_url": resume_url,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    candidate_skills_db[candidate_id] = []
    
    return JSONResponse(
        status_code=201,
        content={
            "id": candidate_id,
            "candidate_id": candidate_id,
            "email": email,
            "first_name": first_name
        }
    )

@app.get("/api/v1/candidates/{candidate_id}")
async def get_candidate(
    candidate_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get candidate by ID"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if candidate_id not in candidates_db:
        return JSONResponse(
            status_code=404,
            content={"error": "Candidate not found"}
        )
    
    candidate = candidates_db[candidate_id]
    return JSONResponse(
        status_code=200,
        content=candidate
    )

@app.get("/api/v1/candidates")
async def list_candidates(
    current_user: Optional[str] = Depends(get_current_user)
):
    """List all candidates"""
    if not current_user:
        return JSONResponse(
            status_code=403,
            content={"error": "Forbidden"}
        )
    
    return JSONResponse(
        status_code=200,
        content=list(candidates_db.values())
    )

@app.put("/api/v1/candidates/{candidate_id}")
async def update_candidate(
    candidate_id: str,
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Update candidate information"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if candidate_id not in candidates_db:
        return JSONResponse(
            status_code=404,
            content={"error": "Candidate not found"}
        )
    
    candidate = candidates_db[candidate_id]
    
    if "first_name" in payload:
        candidate["first_name"] = payload["first_name"]
    if "last_name" in payload:
        candidate["last_name"] = payload["last_name"]
    if "phone" in payload:
        candidate["phone"] = payload["phone"]
    if "resume_url" in payload:
        candidate["resume_url"] = payload["resume_url"]
    
    candidate["updated_at"] = datetime.utcnow().isoformat()
    
    return JSONResponse(
        status_code=200,
        content=candidate
    )

@app.delete("/api/v1/candidates/{candidate_id}")
async def delete_candidate(
    candidate_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Delete a candidate"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if candidate_id not in candidates_db:
        return JSONResponse(
            status_code=404,
            content={"error": "Candidate not found"}
        )
    
    del candidates_db[candidate_id]
    if candidate_id in candidate_skills_db:
        del candidate_skills_db[candidate_id]
    
    return JSONResponse(
        status_code=204,
        content={"message": "Candidate deleted"}
    )

# ============================================================================
# APPLICATION TRACKING ENDPOINTS
# ============================================================================

@app.post("/api/v1/applications")
async def create_application(
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Create a new application"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    job_id = payload.get("job_id", "").strip()
    candidate_id = payload.get("candidate_id", "").strip()
    status = payload.get("status", "applied").strip()
    cover_letter = payload.get("cover_letter", "").strip()
    
    app_id = generate_id()
    applications_db[app_id] = {
        "id": app_id,
        "application_id": app_id,
        "job_id": job_id,
        "candidate_id": candidate_id,
        "status": status,
        "cover_letter": cover_letter,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    return JSONResponse(
        status_code=201,
        content={
            "id": app_id,
            "application_id": app_id,
            "job_id": job_id,
            "candidate_id": candidate_id,
            "status": status
        }
    )

@app.get("/api/v1/applications")
async def get_applications(
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get all applications"""
    if not current_user:
        return JSONResponse(
            status_code=403,
            content={"error": "Forbidden"}
        )
    
    return JSONResponse(
        status_code=200,
        content=list(applications_db.values())
    )

@app.get("/api/v1/candidates/{candidate_id}/applications")
async def get_candidate_applications(
    candidate_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get applications for a candidate"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if candidate_id not in candidates_db:
        return JSONResponse(
            status_code=404,
            content={"error": "Candidate not found"}
        )
    
    candidate_apps = [
        app for app in applications_db.values()
        if app["candidate_id"] == candidate_id
    ]
    
    return JSONResponse(
        status_code=200,
        content=candidate_apps
    )

@app.patch("/api/v1/applications/{app_id}")
async def update_application_status(
    app_id: str,
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Update application status"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if app_id not in applications_db:
        return JSONResponse(
            status_code=404,
            content={"error": "Application not found"}
        )
    
    application = applications_db[app_id]
    
    if "status" in payload:
        application["status"] = payload["status"]
    
    application["updated_at"] = datetime.utcnow().isoformat()
    
    return JSONResponse(
        status_code=200,
        content=application
    )

# ============================================================================
# CANDIDATE PROFILE ENDPOINTS
# ============================================================================

@app.get("/api/v1/candidates/{candidate_id}/resume")
async def get_candidate_resume(
    candidate_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get candidate resume"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if candidate_id not in candidates_db:
        return JSONResponse(
            status_code=404,
            content={"error": "Candidate not found"}
        )
    
    candidate = candidates_db[candidate_id]
    return JSONResponse(
        status_code=200,
        content={
            "candidate_id": candidate_id,
            "resume_url": candidate.get("resume_url", "")
        }
    )

@app.post("/api/v1/candidates/{candidate_id}/resume")
async def upload_resume(
    candidate_id: str,
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Upload candidate resume"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if candidate_id not in candidates_db:
        return JSONResponse(
            status_code=404,
            content={"error": "Candidate not found"}
        )
    
    resume_url = payload.get("resume_url", "").strip()
    
    candidate = candidates_db[candidate_id]
    candidate["resume_url"] = resume_url
    candidate["updated_at"] = datetime.utcnow().isoformat()
    
    return JSONResponse(
        status_code=200,
        content={
            "candidate_id": candidate_id,
            "resume_url": resume_url,
            "message": "Resume uploaded"
        }
    )

@app.get("/api/v1/candidates/{candidate_id}/skills")
async def get_candidate_skills(
    candidate_id: str,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get candidate skills"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if candidate_id not in candidate_skills_db:
        return JSONResponse(
            status_code=404,
            content={"error": "Candidate not found"}
        )
    
    return JSONResponse(
        status_code=200,
        content={
            "candidate_id": candidate_id,
            "skills": candidate_skills_db[candidate_id]
        }
    )

@app.post("/api/v1/candidates/{candidate_id}/skills")
async def add_skill(
    candidate_id: str,
    payload: dict = Body(...),
    current_user: Optional[str] = Depends(get_current_user)
):
    """Add skill to candidate"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    if candidate_id not in candidate_skills_db:
        return JSONResponse(
            status_code=404,
            content={"error": "Candidate not found"}
        )
    
    skill = payload.get("skill", "").strip()
    proficiency = payload.get("proficiency", "intermediate").strip()
    
    candidate_skills_db[candidate_id].append({
        "skill": skill,
        "proficiency": proficiency,
        "added_at": datetime.utcnow().isoformat()
    })
    
    return JSONResponse(
        status_code=200,
        content={
            "candidate_id": candidate_id,
            "skill": skill,
            "proficiency": proficiency,
            "message": "Skill added"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
