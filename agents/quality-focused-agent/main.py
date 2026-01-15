"""
Quality-Focused Agent - OpenTalent Platform
Candidate scoring, ranking, and bias detection
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agents.shared import (
    MessageBus,
    MessagePriority,
    MessageType,
    ServiceClients,
    Topics,
    get_config,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

message_bus: MessageBus | None = None
service_clients: ServiceClients | None = None
config = get_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global message_bus, service_clients

    logger.info("Starting Quality-Focused Agent...")
    message_bus = MessageBus(config.redis_url)
    await message_bus.connect()

    service_clients = ServiceClients(
        conversation_url=config.conversation_service_url,
        voice_url=config.voice_service_url,
        avatar_url=config.avatar_service_url,
        interview_url=config.interview_service_url,
        genkit_url=config.genkit_service_url,
    )

    # Subscribe to scoring requests
    await message_bus.subscribe(["agents:quality", Topics.CANDIDATE_EVENTS], handle_scoring_request)

    asyncio.create_task(message_bus.listen())
    logger.info("Quality-Focused Agent ready on port 8096")

    yield

    logger.info("Shutting down Quality-Focused Agent...")
    if message_bus:
        await message_bus.disconnect()


app = FastAPI(
    title="Quality-Focused Agent",
    description="Candidate scoring and quality assurance",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScoreRequest(BaseModel):
    """Scoring request model"""

    candidate_id: str
    job_description: str
    candidate_profile: dict[str, Any]


class ScoreResult(BaseModel):
    """Scoring result model"""

    candidate_id: str
    overall_score: float
    skill_match_score: float
    experience_score: float
    culture_fit_score: float
    bias_flags: list[str]
    recommendation: str
    timestamp: datetime


async def handle_scoring_request(message):
    """Handle scoring request"""
    logger.info(f"Received scoring request: {message.payload}")

    try:
        if message.message_type == MessageType.CANDIDATE_FOUND:
            # Auto-score new candidates
            candidate_data = message.payload.get("candidate")
            pipeline_id = message.payload.get("pipeline_id")

            if candidate_data:
                asyncio.create_task(score_candidate(pipeline_id, candidate_data))
        elif message.payload.get("action") == "start_scoring":
            pipeline_id = message.payload.get("pipeline_id")
            # Trigger batch scoring
            asyncio.create_task(score_pipeline_candidates(pipeline_id))
    except Exception as e:
        logger.error(f"Error handling scoring request: {e}")


async def score_candidate(pipeline_id: str, candidate_data: dict[str, Any]):
    """
    Score individual candidate

    Args:
        pipeline_id: Pipeline ID
        candidate_data: Candidate data
    """
    candidate_id = candidate_data.get("id")
    logger.info(f"Scoring candidate {candidate_id}")

    try:
        # Use Genkit service for AI-powered scoring
        score_data = await service_clients.genkit.score_candidate_quality(
            candidate_profile=candidate_data,
            job_description="Python Developer with 5+ years experience",  # TODO: Get from pipeline
        )

        overall_score = score_data.get("quality_score", 0)

        # Check for bias
        bias_flags = await detect_bias(candidate_data)

        # Determine recommendation
        recommendation = "reject"
        if overall_score >= 80:
            recommendation = "strong_hire"
        elif overall_score >= 70:
            recommendation = "hire"
        elif overall_score >= 60:
            recommendation = "maybe"

        # Publish scored event
        await message_bus.publish_event(
            topic=Topics.CANDIDATE_EVENTS,
            source_agent="quality-focused",
            message_type=MessageType.CANDIDATE_SCORED,
            payload={
                "pipeline_id": pipeline_id,
                "candidate_id": candidate_id,
                "quality_score": overall_score,
                "skill_match": score_data.get("skill_match", 0),
                "experience_match": score_data.get("experience_match", 0),
                "bias_flags": bias_flags,
                "recommendation": recommendation,
                "timestamp": datetime.utcnow().isoformat(),
            },
            priority=MessagePriority.HIGH if overall_score >= 80 else MessagePriority.MEDIUM,
        )

        logger.info(f"Scored candidate {candidate_id}: {overall_score}/100 ({recommendation})")
    except Exception as e:
        logger.error(f"Error scoring candidate: {e}")


async def score_pipeline_candidates(pipeline_id: str):
    """
    Score all candidates in pipeline

    Args:
        pipeline_id: Pipeline ID
    """
    logger.info(f"Scoring all candidates for pipeline {pipeline_id}")

    # Mock: In production, fetch candidates from database
    await asyncio.sleep(1)


async def detect_bias(candidate_data: dict[str, Any]) -> list[str]:
    """
    Detect potential bias in candidate evaluation

    Args:
        candidate_data: Candidate data

    Returns:
        List of bias flags
    """
    bias_flags = []

    # Check for common bias indicators
    name = candidate_data.get("name", "")
    location = candidate_data.get("location", "")

    # Gender bias check (simplified)
    # In production, use sophisticated NLP models

    # Geographic bias check
    if "experience_years" in candidate_data:
        exp = candidate_data["experience_years"]
        if exp < 3:
            bias_flags.append("potential_age_bias")

    # University bias check
    if "education" in candidate_data:
        education = candidate_data["education"]
        # Check if only considering elite universities

    return bias_flags


async def calculate_skill_match(candidate_skills: list[str], required_skills: list[str]) -> float:
    """
    Calculate skill match percentage

    Args:
        candidate_skills: Candidate skills
        required_skills: Required skills

    Returns:
        Match percentage
    """
    if not required_skills:
        return 100.0

    candidate_skills_lower = [s.lower() for s in candidate_skills]
    required_skills_lower = [s.lower() for s in required_skills]

    matches = sum(1 for skill in required_skills_lower if skill in candidate_skills_lower)

    return (matches / len(required_skills)) * 100


async def calculate_experience_score(candidate_years: int, required_years: int) -> float:
    """
    Calculate experience score

    Args:
        candidate_years: Candidate years of experience
        required_years: Required years

    Returns:
        Experience score
    """
    if candidate_years >= required_years:
        return 100.0
    elif candidate_years >= required_years * 0.7:
        return 80.0
    elif candidate_years >= required_years * 0.5:
        return 60.0
    else:
        return 40.0


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "Quality-Focused Agent", "version": "1.0.0", "status": "operational"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    redis_healthy = message_bus and message_bus.redis_client is not None
    genkit_healthy = service_clients is not None

    return {
        "status": "healthy" if (redis_healthy and genkit_healthy) else "degraded",
        "redis": "connected" if redis_healthy else "disconnected",
        "genkit": "available" if genkit_healthy else "unavailable",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/score", response_model=ScoreResult)
async def manual_score(request: ScoreRequest):
    """
    Manual scoring trigger

    Args:
        request: Score request

    Returns:
        Score result
    """
    try:
        # Score using Genkit
        score_data = await service_clients.genkit.score_candidate_quality(
            candidate_profile=request.candidate_profile, job_description=request.job_description
        )

        # Detect bias
        bias_flags = await detect_bias(request.candidate_profile)

        overall_score = score_data.get("quality_score", 0)

        # Recommendation
        recommendation = "reject"
        if overall_score >= 80:
            recommendation = "strong_hire"
        elif overall_score >= 70:
            recommendation = "hire"
        elif overall_score >= 60:
            recommendation = "maybe"

        return ScoreResult(
            candidate_id=request.candidate_id,
            overall_score=overall_score,
            skill_match_score=score_data.get("skill_match", 0),
            experience_score=score_data.get("experience_match", 0),
            culture_fit_score=score_data.get("culture_fit", 75.0),
            bias_flags=bias_flags,
            recommendation=recommendation,
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error scoring candidate: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8096)
