"""
Tool Leverage Agent - OpenTalent Platform
ATS/CRM integration and external API orchestration
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
    MessageType,
    Topics,
    get_config,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

message_bus: MessageBus | None = None
config = get_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global message_bus

    logger.info("Starting Tool Leverage Agent...")
    message_bus = MessageBus(config.redis_url)
    await message_bus.connect()

    # Subscribe to sync requests
    await message_bus.subscribe(["agents:tools", Topics.CANDIDATE_EVENTS], handle_sync_request)

    asyncio.create_task(message_bus.listen())
    logger.info("Tool Leverage Agent ready on port 8095")

    yield

    logger.info("Shutting down Tool Leverage Agent...")
    if message_bus:
        await message_bus.disconnect()


app = FastAPI(
    title="Tool Leverage Agent",
    description="ATS/CRM integration and API orchestration",
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


class SyncRequest(BaseModel):
    """Data sync request"""

    candidate_id: str
    target_system: str  # "ats", "crm", "database"
    action: str = "create"  # "create", "update", "delete"


class SyncResult(BaseModel):
    """Sync result"""

    candidate_id: str
    system: str
    success: bool
    timestamp: datetime


async def handle_sync_request(message):
    """Handle data sync request"""
    logger.info(f"Received sync request: {message.payload}")

    try:
        if message.message_type == MessageType.CANDIDATE_FOUND:
            # Auto-sync new candidates to ATS
            candidate_data = message.payload.get("candidate")
            if candidate_data:
                asyncio.create_task(sync_to_ats(candidate_data))
        elif message.payload.get("action") == "sync":
            candidate_id = message.payload.get("candidate_id")
            target_system = message.payload.get("target_system", "ats")
            asyncio.create_task(sync_candidate(candidate_id, target_system))
    except Exception as e:
        logger.error(f"Error handling sync request: {e}")


async def sync_to_ats(candidate_data: dict[str, Any]):
    """
    Sync candidate to ATS

    Args:
        candidate_data: Candidate data
    """
    logger.info(f"Syncing candidate {candidate_data.get('id')} to ATS")

    try:
        # Mock ATS API call
        await asyncio.sleep(1)

        # Transform data for ATS
        ats_payload = {
            "first_name": candidate_data.get("name", "").split()[0],
            "last_name": " ".join(candidate_data.get("name", "").split()[1:]),
            "email": candidate_data.get("email"),
            "phone": candidate_data.get("phone"),
            "position": candidate_data.get("current_role"),
            "skills": candidate_data.get("skills", []),
            "source": candidate_data.get("source"),
            "custom_fields": {
                "ai_relevance_score": candidate_data.get("ai_insights", {}).get("relevance_score"),
                "experience_years": candidate_data.get("experience_years"),
            },
        }

        # Simulate API call
        success = await post_to_ats(ats_payload)

        if success:
            logger.info(f"Successfully synced {candidate_data.get('id')} to ATS")
        else:
            logger.error(f"Failed to sync {candidate_data.get('id')} to ATS")

    except Exception as e:
        logger.error(f"Error syncing to ATS: {e}")


async def sync_candidate(candidate_id: str, target_system: str):
    """
    Sync candidate to target system

    Args:
        candidate_id: Candidate ID
        target_system: Target system
    """
    logger.info(f"Syncing candidate {candidate_id} to {target_system}")

    # Mock implementation
    await asyncio.sleep(1)

    if target_system == "ats":
        success = await post_to_ats({"candidate_id": candidate_id})
    elif target_system == "crm":
        success = await post_to_crm({"candidate_id": candidate_id})
    else:
        success = False

    return success


async def post_to_ats(data: dict[str, Any]) -> bool:
    """
    Post data to ATS (mock)

    Args:
        data: Data to post

    Returns:
        Success status
    """
    logger.info(f"Posting to ATS: {data}")
    await asyncio.sleep(0.5)
    return True


async def post_to_crm(data: dict[str, Any]) -> bool:
    """
    Post data to CRM (mock)

    Args:
        data: Data to post

    Returns:
        Success status
    """
    logger.info(f"Posting to CRM: {data}")
    await asyncio.sleep(0.5)
    return True


async def fetch_from_contactout(email: str) -> dict[str, Any]:
    """
    Fetch contact data from ContactOut API

    Args:
        email: Email address

    Returns:
        Contact data
    """
    logger.info(f"Fetching from ContactOut: {email}")

    # Mock API call
    await asyncio.sleep(1)

    return {
        "email": email,
        "phone": "+1-555-0100",
        "linkedin": "https://linkedin.com/in/example",
        "confidence": 0.95,
    }


async def fetch_from_salesql(company: str) -> dict[str, Any]:
    """
    Fetch company data from SalesQL API

    Args:
        company: Company name

    Returns:
        Company data
    """
    logger.info(f"Fetching from SalesQL: {company}")

    await asyncio.sleep(1)

    return {
        "company_name": company,
        "industry": "Technology",
        "size": "1000-5000",
        "locations": ["San Francisco", "New York"],
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "Tool Leverage Agent", "version": "1.0.0", "status": "operational"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    redis_healthy = message_bus and message_bus.redis_client is not None
    return {
        "status": "healthy" if redis_healthy else "degraded",
        "redis": "connected" if redis_healthy else "disconnected",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/sync", response_model=SyncResult)
async def manual_sync(request: SyncRequest):
    """
    Manual sync trigger

    Args:
        request: Sync request

    Returns:
        Sync result
    """
    try:
        success = await sync_candidate(request.candidate_id, request.target_system)

        return SyncResult(
            candidate_id=request.candidate_id,
            system=request.target_system,
            success=success,
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error syncing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/enrich/{email}")
async def enrich_contact(email: str):
    """
    Enrich contact data using external APIs

    Args:
        email: Email address

    Returns:
        Enriched data
    """
    try:
        contactout_data = await fetch_from_contactout(email)

        return {
            "email": email,
            "enriched_data": contactout_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error enriching contact: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8095)
