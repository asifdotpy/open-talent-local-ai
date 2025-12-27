"""
Market Intelligence Agent - OpenTalent Platform
Salary trends, competitor talent mapping, industry insights
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agents.shared import (
    CompetitorIntel,
    MarketInsight,
    MessageBus,
    MessagePriority,
    MessageType,
    SalaryTrend,
    SkillDemand,
    Topics,
    get_config,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

message_bus: Optional[MessageBus] = None
config = get_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global message_bus

    logger.info("Starting Market Intelligence Agent...")
    message_bus = MessageBus(config.redis_url)
    await message_bus.connect()

    # Subscribe to market intel requests
    await message_bus.subscribe(["agents:market_intel"], handle_intel_request)

    asyncio.create_task(message_bus.listen())
    logger.info("Market Intelligence Agent ready on port 8094")

    yield

    logger.info("Shutting down Market Intelligence Agent...")
    if message_bus:
        await message_bus.disconnect()


app = FastAPI(
    title="Market Intelligence Agent",
    description="Salary trends and market analysis",
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


class IntelRequest(BaseModel):
    """Market intelligence request"""

    job_title: str
    location: str = "United States"
    skills: list[str] = []


class IntelResult(BaseModel):
    """Market intelligence result"""

    job_title: str
    salary_range: dict[str, float]
    market_demand: str
    top_competitors: list[str]
    timestamp: datetime


async def handle_intel_request(message):
    """Handle market intelligence request"""
    logger.info(f"Received intel request: {message.payload}")

    try:
        pipeline_id = message.payload.get("pipeline_id")
        job_title = message.payload.get("job_title", "Software Engineer")
        location = message.payload.get("location", "United States")

        asyncio.create_task(gather_market_intel(pipeline_id, job_title, location))
    except Exception as e:
        logger.error(f"Error handling intel request: {e}")


async def gather_market_intel(pipeline_id: str, job_title: str, location: str):
    """
    Gather market intelligence

    Args:
        pipeline_id: Pipeline ID
        job_title: Job title
        location: Location
    """
    logger.info(f"Gathering market intel for {job_title} in {location}")

    try:
        # Gather salary data
        salary_data = await fetch_salary_trends(job_title, location)

        # Gather competitor data
        competitor_data = await fetch_competitor_intel(job_title, location)

        # Gather skill demand data
        skill_data = await fetch_skill_demand(job_title)

        # Create market insight
        insight = MarketInsight(
            job_title=job_title,
            location=location,
            salary_trends=[salary_data],
            competitor_intel=[competitor_data],
            skill_demand=[skill_data],
            generated_at=datetime.utcnow(),
        )

        # Publish market insight event
        await message_bus.publish_event(
            topic=Topics.MARKET_INTEL,
            source_agent="market-intelligence",
            message_type=MessageType.MARKET_INSIGHT,
            payload={
                "pipeline_id": pipeline_id,
                "insight": insight.model_dump(),
                "timestamp": datetime.utcnow().isoformat(),
            },
            priority=MessagePriority.LOW,
        )

        logger.info(f"Market intel gathered for {job_title}")
    except Exception as e:
        logger.error(f"Error gathering market intel: {e}")


async def fetch_salary_trends(job_title: str, location: str) -> SalaryTrend:
    """
    Fetch salary trend data

    Args:
        job_title: Job title
        location: Location

    Returns:
        Salary trend data
    """
    logger.info(f"Fetching salary trends for {job_title}")

    # Mock implementation - in production, use APIs like Glassdoor, Payscale
    await asyncio.sleep(1)

    return SalaryTrend(
        job_title=job_title,
        location=location,
        min_salary=80000.0,
        max_salary=150000.0,
        median_salary=115000.0,
        currency="USD",
        experience_level="mid",
        data_source="glassdoor",
        last_updated=datetime.utcnow(),
    )


async def fetch_competitor_intel(job_title: str, location: str) -> CompetitorIntel:
    """
    Fetch competitor intelligence

    Args:
        job_title: Job title
        location: Location

    Returns:
        Competitor intel data
    """
    logger.info(f"Fetching competitor intel for {job_title}")

    await asyncio.sleep(1)

    return CompetitorIntel(
        company_name="Tech Giant Inc",
        location=location,
        open_positions=25,
        hiring_rate="high",
        avg_tenure_months=36,
        benefits_score=8.5,
        culture_rating=4.2,
        data_source="linkedin",
    )


async def fetch_skill_demand(job_title: str) -> SkillDemand:
    """
    Fetch skill demand data

    Args:
        job_title: Job title

    Returns:
        Skill demand data
    """
    logger.info(f"Fetching skill demand for {job_title}")

    await asyncio.sleep(1)

    return SkillDemand(
        skill_name="Python",
        job_title=job_title,
        demand_level="high",
        growth_rate=15.5,
        avg_salary_impact=12000.0,
        trending_frameworks=["FastAPI", "Django", "Flask"],
        last_updated=datetime.utcnow(),
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "Market Intelligence Agent", "version": "1.0.0", "status": "operational"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    redis_healthy = message_bus and message_bus.redis_client is not None
    return {
        "status": "healthy" if redis_healthy else "degraded",
        "redis": "connected" if redis_healthy else "disconnected",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/analyze-market", response_model=IntelResult)
async def analyze_market(request: IntelRequest):
    """
    Analyze market for job title

    Args:
        request: Intelligence request

    Returns:
        Market intelligence
    """
    try:
        salary_data = await fetch_salary_trends(request.job_title, request.location)
        competitor_data = await fetch_competitor_intel(request.job_title, request.location)

        return IntelResult(
            job_title=request.job_title,
            salary_range={
                "min": salary_data.min_salary,
                "max": salary_data.max_salary,
                "median": salary_data.median_salary,
            },
            market_demand="high",
            top_competitors=[competitor_data.company_name],
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error analyzing market: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8094)
