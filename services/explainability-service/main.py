from datetime import datetime
from typing import Any

from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="OpenTalent Explainability Service API",
    description="AI explainability and transparency service for the OpenTalent platform.",
    version="1.0.0",
)


# Shared schemas
class ExplanationResponse(BaseModel):
    explanation_id: str
    timestamp: str
    summary: str
    details: dict[str, Any]
    confidence: float
    recommendations: list[str]


@app.get("/")
async def root():
    return {"message": "OpenTalent Explainability Service is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "explainability-service", "version": "1.0.0"}


@app.post("/api/v1/explain/score", response_model=ExplanationResponse)
async def explain_score(request: dict = Body(...)):
    interview_id = request.get("interview_id", "unknown")
    score = request.get("score", 0.0)

    explanation_id = f"exp_score_{interview_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return ExplanationResponse(
        explanation_id=explanation_id,
        timestamp=datetime.now().isoformat(),
        summary=f"Score explanation for interview {interview_id}",
        details={
            "score": score,
            "factors": ["Technical Accuracy", "Communication", "Problem Solving"],
            "model": "talent_ai_scoring_v1.3",
        },
        confidence=0.92,
        recommendations=["Focus on clarifying technical trade-offs"],
    )


@app.post("/api/v1/explain/recommendation", response_model=ExplanationResponse)
async def explain_recommendation(request: dict = Body(...)):
    interview_id = request.get("interview_id", "unknown")
    rec = request.get("recommendation", "hire")

    explanation_id = f"exp_rec_{interview_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return ExplanationResponse(
        explanation_id=explanation_id,
        timestamp=datetime.now().isoformat(),
        summary=f"Recommendation explanation for interview {interview_id}",
        details={
            "recommendation": rec,
            "logic": "Consistent high performance across core competency checks",
            "model": "talent_ai_hiring_v2.1",
        },
        confidence=0.88,
        recommendations=["Schedule final culture fit interview"],
    )


@app.post("/api/v1/explain/path")
async def explain_path(request: dict = Body(...)):
    interview_id = request.get("interview_id", "unknown")
    return {
        "interview_id": interview_id,
        "path": [
            "Skill Assessment",
            "Core Competency Check",
            "Behavioral Review",
            "Final Decision",
        ],
    }


@app.get("/api/v1/features/importance")
async def get_feature_importance():
    return {
        "importance": {
            "technical_skills": 0.45,
            "communication_clarity": 0.25,
            "industry_experience": 0.20,
            "problem_solving_approach": 0.10,
        }
    }


@app.get("/api/v1/interviews/{interview_id}/features")
async def get_interview_features(interview_id: str):
    return {
        "interview_id": interview_id,
        "features": {"clarity": 0.85, "technical_depth": 0.72, "responsiveness": 0.90},
    }


@app.get("/api/v1/model/metadata")
async def get_model_metadata():
    return {
        "model_name": "OpenTalent Interview AI Engine",
        "version": "2.1.4",
        "last_updated": "2025-11-25",
        "type": "Neural Scoring Engine",
        "parameters_count": "350M",
    }


@app.get("/api/v1/decisions/log")
async def get_decision_log():
    return {
        "total": 1,
        "log": [
            {
                "timestamp": datetime.now().isoformat(),
                "interview_id": "int123",
                "decision": "pass",
                "confidence": 0.94,
                "audited": True,
            }
        ],
    }


if __name__ == "__main__":
    import os

    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8013))
    uvicorn.run(app, host=host, port=port)
