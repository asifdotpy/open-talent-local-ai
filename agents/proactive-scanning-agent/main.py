"""
Proactive Scanning Agent - TalentAI Platform
Multi-platform talent discovery (LinkedIn, GitHub, Stack Overflow)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import logging
import sys
import os
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.shared import (
    MessageBus,
    Topics,
    MessageType,
    MessagePriority,
    CandidateProfile,
    CandidateSource,
    CandidateStatus,
    SocialProfile,
    get_config
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

message_bus: Optional[MessageBus] = None
config = get_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global message_bus
    
    logger.info("Starting Proactive Scanning Agent...")
    message_bus = MessageBus(config.redis_url)
    await message_bus.connect()
    
    # Subscribe to scanning requests
    await message_bus.subscribe(
        ["agents:scanning"],
        handle_scanning_request
    )
    
    asyncio.create_task(message_bus.listen())
    logger.info("Proactive Scanning Agent ready on port 8091")
    
    yield
    
    logger.info("Shutting down Proactive Scanning Agent...")
    if message_bus:
        await message_bus.disconnect()


app = FastAPI(
    title="Proactive Scanning Agent",
    description="Multi-platform talent discovery",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    """Scan request model"""
    pipeline_id: str
    job_description: str
    platforms: List[str] = ["linkedin", "github"]
    target_count: int = 50


class ScanResult(BaseModel):
    """Scan result model"""
    candidates_found: int
    platforms_scanned: List[str]
    timestamp: datetime


async def handle_scanning_request(message):
    """Handle scanning request from coordinator"""
    logger.info(f"Received scanning request: {message.payload}")
    
    try:
        pipeline_id = message.payload.get("pipeline_id")
        job_description = message.payload.get("job_description")
        platforms = message.payload.get("platforms", ["linkedin", "github"])
        target_count = message.payload.get("target_count", 50)
        
        # Trigger scanning in background
        asyncio.create_task(
            scan_platforms(pipeline_id, job_description, platforms, target_count)
        )
    except Exception as e:
        logger.error(f"Error handling scanning request: {e}")


async def scan_platforms(
    pipeline_id: str,
    job_description: str,
    platforms: List[str],
    target_count: int
):
    """
    Scan platforms for candidates
    
    Args:
        pipeline_id: Pipeline ID
        job_description: Job description
        platforms: Platforms to scan
        target_count: Target number of candidates
    """
    logger.info(f"Scanning platforms: {platforms} for pipeline {pipeline_id}")
    
    candidates_found = 0
    
    for platform in platforms:
        if platform == "linkedin":
            count = await scan_linkedin(pipeline_id, job_description, target_count // len(platforms))
            candidates_found += count
        elif platform == "github":
            count = await scan_github(pipeline_id, job_description, target_count // len(platforms))
            candidates_found += count
        elif platform == "stackoverflow":
            count = await scan_stackoverflow(pipeline_id, job_description, target_count // len(platforms))
            candidates_found += count
    
    logger.info(f"Scanning complete: {candidates_found} candidates found")


async def scan_linkedin(pipeline_id: str, job_description: str, target: int) -> int:
    """
    Scan LinkedIn for candidates
    
    Args:
        pipeline_id: Pipeline ID
        job_description: Job description
        target: Target count
        
    Returns:
        Number of candidates found
    """
    logger.info(f"Scanning LinkedIn for {target} candidates")
    
    # Mock implementation - in production, use LinkedIn API or scraping
    await asyncio.sleep(2)  # Simulate API call
    
    # Generate mock candidates
    for i in range(min(target, 10)):
        candidate = CandidateProfile(
            id=f"linkedin_{pipeline_id}_{i}",
            name=f"LinkedIn Candidate {i}",
            email=f"candidate{i}@linkedin.example.com",
            phone="+1-555-0100",
            location="San Francisco, CA",
            current_role="Software Engineer",
            current_company="Tech Company",
            experience_years=5 + i,
            skills=["Python", "Django", "PostgreSQL", "AWS"],
            source=CandidateSource.LINKEDIN,
            status=CandidateStatus.NEW,
            social_profiles=[
                SocialProfile(
                    platform="linkedin",
                    url=f"https://linkedin.com/in/candidate{i}",
                    followers=1000 + i * 100
                )
            ],
            ai_insights={
                "relevance_score": 85 + i,
                "skill_match": "high",
                "experience_match": "medium"
            }
        )
        
        # Publish candidate found event
        await message_bus.publish_event(
            topic=Topics.CANDIDATE_EVENTS,
            source_agent="proactive-scanning",
            message_type=MessageType.CANDIDATE_FOUND,
            payload={
                "pipeline_id": pipeline_id,
                "candidate": candidate.model_dump(),
                "platform": "linkedin",
                "timestamp": datetime.utcnow().isoformat()
            },
            priority=MessagePriority.MEDIUM
        )
        
        await asyncio.sleep(0.5)  # Rate limiting
    
    return min(target, 10)


async def scan_github(pipeline_id: str, job_description: str, target: int) -> int:
    """
    Scan GitHub for candidates
    
    Args:
        pipeline_id: Pipeline ID
        job_description: Job description
        target: Target count
        
    Returns:
        Number of candidates found
    """
    logger.info(f"Scanning GitHub for {target} candidates")
    
    # Mock implementation - in production, use GitHub API
    await asyncio.sleep(2)
    
    for i in range(min(target, 10)):
        candidate = CandidateProfile(
            id=f"github_{pipeline_id}_{i}",
            name=f"GitHub Developer {i}",
            email=f"dev{i}@github.example.com",
            location="Remote",
            current_role="Open Source Contributor",
            experience_years=3 + i,
            skills=["Python", "FastAPI", "Docker", "Kubernetes"],
            source=CandidateSource.GITHUB,
            status=CandidateStatus.NEW,
            social_profiles=[
                SocialProfile(
                    platform="github",
                    url=f"https://github.com/developer{i}",
                    followers=500 + i * 50
                )
            ],
            ai_insights={
                "relevance_score": 80 + i,
                "github_activity": "high",
                "code_quality": "excellent"
            }
        )
        
        await message_bus.publish_event(
            topic=Topics.CANDIDATE_EVENTS,
            source_agent="proactive-scanning",
            message_type=MessageType.CANDIDATE_FOUND,
            payload={
                "pipeline_id": pipeline_id,
                "candidate": candidate.model_dump(),
                "platform": "github",
                "timestamp": datetime.utcnow().isoformat()
            },
            priority=MessagePriority.MEDIUM
        )
        
        await asyncio.sleep(0.5)
    
    return min(target, 10)


async def scan_stackoverflow(pipeline_id: str, job_description: str, target: int) -> int:
    """
    Scan Stack Overflow for candidates
    
    Args:
        pipeline_id: Pipeline ID
        job_description: Job description
        target: Target count
        
    Returns:
        Number of candidates found
    """
    logger.info(f"Scanning Stack Overflow for {target} candidates")
    
    await asyncio.sleep(2)
    
    for i in range(min(target, 5)):
        candidate = CandidateProfile(
            id=f"stackoverflow_{pipeline_id}_{i}",
            name=f"SO Expert {i}",
            email=f"expert{i}@stackoverflow.example.com",
            current_role="Senior Developer",
            experience_years=7 + i,
            skills=["Python", "Django", "Flask", "SQLAlchemy"],
            source=CandidateSource.REFERRAL,
            status=CandidateStatus.NEW,
            social_profiles=[
                SocialProfile(
                    platform="stackoverflow",
                    url=f"https://stackoverflow.com/users/{i}",
                    followers=2000 + i * 200
                )
            ],
            ai_insights={
                "relevance_score": 90 + i,
                "reputation": 10000 + i * 1000,
                "expertise_areas": ["python", "django", "web-development"]
            }
        )
        
        await message_bus.publish_event(
            topic=Topics.CANDIDATE_EVENTS,
            source_agent="proactive-scanning",
            message_type=MessageType.CANDIDATE_FOUND,
            payload={
                "pipeline_id": pipeline_id,
                "candidate": candidate.model_dump(),
                "platform": "stackoverflow",
                "timestamp": datetime.utcnow().isoformat()
            },
            priority=MessagePriority.HIGH
        )
        
        await asyncio.sleep(0.5)
    
    return min(target, 5)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Proactive Scanning Agent",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    redis_healthy = message_bus and message_bus.redis_client is not None
    return {
        "status": "healthy" if redis_healthy else "degraded",
        "redis": "connected" if redis_healthy else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/scan", response_model=ScanResult)
async def manual_scan(request: ScanRequest):
    """
    Manual scan trigger (for testing/admin)
    
    Args:
        request: Scan request
        
    Returns:
        Scan result
    """
    asyncio.create_task(
        scan_platforms(
            request.pipeline_id,
            request.job_description,
            request.platforms,
            request.target_count
        )
    )
    
    return ScanResult(
        candidates_found=0,  # Will be updated via events
        platforms_scanned=request.platforms,
        timestamp=datetime.utcnow()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8091)
