"""
Candidate Service - Candidate management, applications, profiles
Port: 8008
"""

from fastapi import FastAPI, Depends, Body, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import uuid
import time

app = FastAPI(
    title="Candidate Service",
    version="1.0.0",
    description="Manage candidates, job applications, skills, and resumes"
)

# ============================================================================
# ENUMS - STRONGLY TYPED STATUS/PROFICIENCY VALUES
# ============================================================================

class ApplicationStatus(str, Enum):
    """Application status enumeration"""
    APPLIED = "applied"
    REVIEWING = "reviewing"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class SkillProficiency(str, Enum):
    """Skill proficiency enumeration"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CandidateCreate(BaseModel):
    """Schema for creating a candidate"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    resume_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "resume_url": "https://example.com/resume.pdf"
            }
        }

class CandidateUpdate(BaseModel):
    """Schema for updating a candidate"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    resume_url: Optional[str] = None

class CandidateResponse(BaseModel):
    """Schema for candidate response"""
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    resume_url: Optional[str]
    created_at: str
    updated_at: str

class ApplicationCreate(BaseModel):
    """Schema for creating an application"""
    candidate_id: str
    job_id: str
    cover_letter: Optional[str] = None
    status: ApplicationStatus = Field(default=ApplicationStatus.APPLIED)
    
    class Config:
        json_schema_extra = {
            "example": {
                "candidate_id": "uuid-here",
                "job_id": "job-123",
                "cover_letter": "I am interested in this position...",
                "status": "applied"
            }
        }

class ApplicationUpdate(BaseModel):
    """Schema for updating an application"""
    status: ApplicationStatus = Field(..., description="Application status must be one of: applied, reviewing, interview_scheduled, accepted, rejected")
    cover_letter: Optional[str] = None

class ApplicationResponse(BaseModel):
    """Schema for application response"""
    id: str
    job_id: str
    candidate_id: str
    status: ApplicationStatus
    cover_letter: Optional[str]
    created_at: str
    updated_at: str

class SkillCreate(BaseModel):
    """Schema for adding a skill"""
    skill: str = Field(..., min_length=1, max_length=100)
    proficiency: SkillProficiency = Field(default=SkillProficiency.INTERMEDIATE)
    
    class Config:
        json_schema_extra = {
            "example": {
                "skill": "Python",
                "proficiency": "advanced"
            }
        }

class SkillResponse(BaseModel):
    """Schema for skill response"""
    skill: str
    proficiency: SkillProficiency
    added_at: str

class SkillListResponse(BaseModel):
    """Schema for skill list response"""
    candidate_id: str
    skills: List[SkillResponse]

class ResumeResponse(BaseModel):
    """Schema for resume response"""
    candidate_id: str
    resume_url: str

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

@app.post(
    "/api/v1/candidates",
    tags=["candidates"],
    summary="Create a new candidate",
    description="Creates a new candidate record with email, name, and optional contact info",
    response_model=CandidateResponse,
    status_code=201,
    responses={
        201: {"description": "Candidate created successfully"},
        400: {"description": "Invalid input - missing or invalid fields"},
        401: {"description": "Unauthorized - missing authorization header"}
    }
)
async def create_candidate(
    payload: CandidateCreate,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Create a new candidate"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    candidate_id = generate_id()
    candidate = {
        "id": candidate_id,
        "candidate_id": candidate_id,
        "email": payload.email,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "phone": payload.phone,
        "resume_url": payload.resume_url,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    candidates_db[candidate_id] = candidate
    candidate_skills_db[candidate_id] = []
    
    return candidate

@app.get(
    "/api/v1/candidates/{candidate_id}",
    tags=["candidates"],
    summary="Get candidate by ID",
    response_model=CandidateResponse,
    responses={
        200: {"description": "Candidate found"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"}
    }
)
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
    return candidate

@app.get(
    "/api/v1/candidates",
    tags=["candidates"],
    summary="List all candidates",
    response_model=List[CandidateResponse],
    responses={
        200: {"description": "List of candidates"},
        403: {"description": "Forbidden"}
    }
)
async def list_candidates(
    current_user: Optional[str] = Depends(get_current_user)
):
    """List all candidates"""
    if not current_user:
        return JSONResponse(
            status_code=403,
            content={"error": "Forbidden"}
        )
    
    return list(candidates_db.values())

@app.put(
    "/api/v1/candidates/{candidate_id}",
    tags=["candidates"],
    summary="Update candidate information",
    response_model=CandidateResponse,
    responses={
        200: {"description": "Candidate updated successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"}
    }
)
async def update_candidate(
    candidate_id: str,
    payload: CandidateUpdate,
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
    
    # Only update provided fields
    update_data = payload.model_dump(exclude_unset=True)
    candidate.update(update_data)
    candidate["updated_at"] = datetime.utcnow().isoformat()
    
    return candidate

@app.delete(
    "/api/v1/candidates/{candidate_id}",
    tags=["candidates"],
    summary="Delete a candidate",
    status_code=204,
    responses={
        204: {"description": "Candidate deleted successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"}
    }
)
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
    
    return None

# ============================================================================
# APPLICATION TRACKING ENDPOINTS
# ============================================================================

@app.post(
    "/api/v1/applications",
    tags=["applications"],
    summary="Create a new application",
    response_model=ApplicationResponse,
    status_code=201,
    responses={
        201: {"description": "Application created successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"}
    }
)
async def create_application(
    payload: ApplicationCreate,
    current_user: Optional[str] = Depends(get_current_user)
):
    """Create a new application"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized"}
        )
    
    app_id = generate_id()
    application = {
        "id": app_id,
        "application_id": app_id,
        "job_id": payload.job_id,
        "candidate_id": payload.candidate_id,
        "status": payload.status,
        "cover_letter": payload.cover_letter,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    applications_db[app_id] = application
    
    return application

@app.get(
    "/api/v1/applications",
    tags=["applications"],
    summary="Get all applications",
    response_model=List[ApplicationResponse],
    responses={
        200: {"description": "List of applications"},
        403: {"description": "Forbidden"}
    }
)
async def get_applications(
    current_user: Optional[str] = Depends(get_current_user)
):
    """Get all applications"""
    if not current_user:
        return JSONResponse(
            status_code=403,
            content={"error": "Forbidden"}
        )
    
    return list(applications_db.values())

@app.get(
    "/api/v1/candidates/{candidate_id}/applications",
    tags=["applications"],
    summary="Get applications for a candidate",
    response_model=List[ApplicationResponse],
    responses={
        200: {"description": "List of candidate applications"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"}
    }
)
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
    
    return candidate_apps

@app.patch(
    "/api/v1/applications/{app_id}",
    tags=["applications"],
    summary="Update application status",
    response_model=ApplicationResponse,
    responses={
        200: {"description": "Application updated successfully"},
        400: {"description": "Invalid status"},
        401: {"description": "Unauthorized"},
        404: {"description": "Application not found"}
    }
)
async def update_application_status(
    app_id: str,
    payload: ApplicationUpdate,
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
    application["status"] = payload.status
    if payload.cover_letter:
        application["cover_letter"] = payload.cover_letter
    application["updated_at"] = datetime.utcnow().isoformat()
    
    return application

# ============================================================================
# CANDIDATE PROFILE ENDPOINTS
# ============================================================================

@app.get(
    "/api/v1/candidates/{candidate_id}/resume",
    tags=["resume"],
    summary="Get candidate resume",
    response_model=ResumeResponse,
    responses={
        200: {"description": "Resume found"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"}
    }
)
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
    return {
        "candidate_id": candidate_id,
        "resume_url": candidate.get("resume_url", "")
    }

@app.post(
    "/api/v1/candidates/{candidate_id}/resume",
    tags=["resume"],
    summary="Upload candidate resume",
    response_model=ResumeResponse,
    responses={
        200: {"description": "Resume uploaded successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"}
    }
)
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
    
    return {
        "candidate_id": candidate_id,
        "resume_url": resume_url
    }

@app.get(
    "/api/v1/candidates/{candidate_id}/skills",
    tags=["skills"],
    summary="Get candidate skills",
    response_model=SkillListResponse,
    responses={
        200: {"description": "Skills found"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"}
    }
)
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
    
    return {
        "candidate_id": candidate_id,
        "skills": candidate_skills_db[candidate_id]
    }

@app.post(
    "/api/v1/candidates/{candidate_id}/skills",
    tags=["skills"],
    summary="Add skill to candidate",
    response_model=SkillResponse,
    responses={
        200: {"description": "Skill added successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Candidate not found"}
    }
)
async def add_skill(
    candidate_id: str,
    payload: SkillCreate,
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
    
    skill_entry = {
        "skill": payload.skill,
        "proficiency": payload.proficiency,
        "added_at": datetime.utcnow().isoformat()
    }
    
    candidate_skills_db[candidate_id].append(skill_entry)
    
    return skill_entry

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
