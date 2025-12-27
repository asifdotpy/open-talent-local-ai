"""Vetta AI API Routes for Interview Service
Provides REST endpoints for all Vetta AI v4 capabilities.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.vetta_ai import get_vetta_ai

router = APIRouter(prefix="/api/v1/vetta", tags=["vetta-ai"])


# Request/Response Models

class CandidateAssessmentRequest(BaseModel):
    """Request for candidate skill assessment."""
    candidate_info: str = Field(..., description="Candidate profile/resume text")
    job_description: str = Field(..., description="Job requirements and description")
    role: str = Field(default="Software Engineer", description="Role title")


class InterviewQuestionRequest(BaseModel):
    """Request for AI-generated interview question."""
    previous_responses: list[str] = Field(default_factory=list, description="Previous candidate responses")
    job_requirements: str = Field(..., description="Job requirements")
    expertise_level: str = Field(default="intermediate", description="Candidate expertise level")


class OutreachMessageRequest(BaseModel):
    """Request for personalized outreach message."""
    candidate_name: str = Field(..., description="Candidate's name")
    candidate_skills: str = Field(..., description="Key skills to highlight")
    role: str = Field(..., description="Role title")
    company: str = Field(..., description="Company name")


class QualityScoringRequest(BaseModel):
    """Request for candidate quality scoring."""
    candidate_profile: str = Field(..., description="Candidate information")
    job_requirements: str = Field(..., description="Job requirements")
    scoring_criteria: list[str] | None = Field(None, description="Custom scoring criteria")


class SentimentAnalysisRequest(BaseModel):
    """Request for response sentiment analysis."""
    response_text: str = Field(..., description="Candidate's response to analyze")


class GenerateRequest(BaseModel):
    """Generic generation request."""
    instruction: str = Field(..., description="Task instruction")
    context: str | None = Field(None, description="Optional context")
    max_tokens: int = Field(default=256, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Sampling temperature")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Nucleus sampling threshold")


# API Endpoints

@router.get("/info")
async def get_model_info():
    """Get Vetta AI model information and status.

    Returns model details, capabilities, and resource usage.
    """
    vetta = get_vetta_ai()
    return vetta.get_model_info()


@router.post("/generate")
async def generate_response(request: GenerateRequest):
    """Generate response using Vetta AI with custom instruction.

    Generic endpoint for any Vetta AI generation task.
    """
    try:
        vetta = get_vetta_ai()

        response = await vetta.generate(
            instruction=request.instruction,
            context=request.context,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p
        )

        return {
            "response": response,
            "instruction": request.instruction,
            "model": vetta.model_name,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/assess-candidate")
async def assess_candidate(request: CandidateAssessmentRequest):
    """Assess candidate's technical skills for a role.

    Returns comprehensive assessment with scores, strengths, gaps, and recommendations.
    """
    try:
        vetta = get_vetta_ai()

        assessment = await vetta.assess_candidate(
            candidate_info=request.candidate_info,
            job_description=request.job_description,
            role=request.role
        )

        return assessment

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.post("/generate-question")
async def generate_interview_question(request: InterviewQuestionRequest):
    """Generate next interview question based on context.

    Adapts questions based on previous responses and expertise level.
    """
    try:
        vetta = get_vetta_ai()

        question = await vetta.generate_interview_question(
            previous_responses=request.previous_responses,
            job_requirements=request.job_requirements,
            expertise_level=request.expertise_level
        )

        return {
            "question": question,
            "expertise_level": request.expertise_level,
            "context_responses": len(request.previous_responses),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")


@router.post("/generate-outreach")
async def generate_outreach_message(request: OutreachMessageRequest):
    """Generate personalized outreach message for candidate.

    Creates engaging, professional outreach tailored to candidate's skills.
    """
    try:
        vetta = get_vetta_ai()

        message = await vetta.generate_outreach_message(
            candidate_name=request.candidate_name,
            candidate_skills=request.candidate_skills,
            role=request.role,
            company=request.company
        )

        return {
            "message": message,
            "candidate_name": request.candidate_name,
            "role": request.role,
            "company": request.company,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outreach generation failed: {str(e)}")


@router.post("/score-quality")
async def score_candidate_quality(request: QualityScoringRequest):
    """Score candidate quality against job requirements.

    Provides detailed scoring breakdown across multiple criteria.
    """
    try:
        vetta = get_vetta_ai()

        scoring = await vetta.score_candidate_quality(
            candidate_profile=request.candidate_profile,
            job_requirements=request.job_requirements,
            scoring_criteria=request.scoring_criteria
        )

        return scoring

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality scoring failed: {str(e)}")


@router.post("/analyze-sentiment")
async def analyze_response_sentiment(request: SentimentAnalysisRequest):
    """Analyze sentiment and tone of candidate response.

    Helps assess candidate's emotional state and communication style.
    """
    try:
        vetta = get_vetta_ai()

        analysis = await vetta.analyze_response_sentiment(request.response_text)

        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")


@router.get("/health")
async def vetta_health_check():
    """Health check for Vetta AI service.

    Returns model status and readiness.
    """
    vetta = get_vetta_ai()
    info = vetta.get_model_info()

    status = "healthy" if info["loaded"] else "degraded"
    if info["fallback_mode"]:
        status = "fallback"

    return {
        "status": status,
        "model_loaded": info["loaded"],
        "fallback_mode": info["fallback_mode"],
        "cuda_available": info["cuda_available"],
        "timestamp": datetime.now().isoformat()
    }
