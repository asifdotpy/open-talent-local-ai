"""
Personalized Engagement Agent - OpenTalent Platform
Custom outreach message creation and multi-channel communication
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime

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

    logger.info("Starting Personalized Engagement Agent...")
    message_bus = MessageBus(config.redis_url)
    await message_bus.connect()

    service_clients = ServiceClients(
        conversation_url=config.conversation_service_url,
        voice_url=config.voice_service_url,
        avatar_url=config.avatar_service_url,
        interview_url=config.interview_service_url,
        genkit_url=config.genkit_service_url,
    )

    # Subscribe to engagement requests
    await message_bus.subscribe(
        [Topics.ENGAGEMENT_EVENTS, "agents:engagement"], handle_engagement_request
    )

    asyncio.create_task(message_bus.listen())
    logger.info("Personalized Engagement Agent ready on port 8093")

    yield

    logger.info("Shutting down Personalized Engagement Agent...")
    if message_bus:
        await message_bus.disconnect()


app = FastAPI(
    title="Personalized Engagement Agent",
    description="Custom outreach and multi-channel communication",
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


class EngagementRequest(BaseModel):
    """Engagement request model"""

    candidate_id: str
    candidate_name: str
    candidate_email: str
    job_title: str
    company_name: str
    channel: str = "email"


class EngagementResult(BaseModel):
    """Engagement result model"""

    candidate_id: str
    message_sent: bool
    channel: str
    timestamp: datetime


async def handle_engagement_request(message):
    """Handle engagement request from coordinator"""
    logger.info(f"Received engagement request: {message.payload}")

    try:
        pipeline_id = message.payload.get("pipeline_id")
        candidate_id = message.payload.get("candidate_id")

        # Trigger engagement in background
        asyncio.create_task(send_outreach(pipeline_id, candidate_id))
    except Exception as e:
        logger.error(f"Error handling engagement request: {e}")


async def send_outreach(pipeline_id: str, candidate_id: str):
    """
    Send personalized outreach to candidate

    Args:
        pipeline_id: Pipeline ID
        candidate_id: Candidate ID
    """
    logger.info(f"Sending outreach to candidate {candidate_id}")

    try:
        # In production, fetch candidate from database
        candidate_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "current_role": "Software Engineer",
            "skills": ["Python", "Django"],
        }

        # Generate personalized message using Genkit
        message_data = await service_clients.genkit.generate_engagement_message(
            candidate_name=candidate_data["name"],
            candidate_role=candidate_data["current_role"],
            job_title="Senior Python Developer",
            company_name="OpenTalent",
        )

        # Send via email (mock)
        success = await send_email(
            to_email=candidate_data["email"],
            subject=message_data.get("subject", "Exciting Opportunity"),
            body=message_data.get("message", ""),
        )

        if success:
            # Publish outreach sent event
            await message_bus.publish_event(
                topic=Topics.ENGAGEMENT_EVENTS,
                source_agent="personalized-engagement",
                message_type=MessageType.OUTREACH_SENT,
                payload={
                    "pipeline_id": pipeline_id,
                    "candidate_id": candidate_id,
                    "channel": "email",
                    "message": message_data.get("message"),
                    "timestamp": datetime.utcnow().isoformat(),
                },
                priority=MessagePriority.HIGH,
            )

            logger.info(f"Outreach sent successfully to {candidate_id}")
    except Exception as e:
        logger.error(f"Error sending outreach: {e}")


async def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send email (mock implementation)

    Args:
        to_email: Recipient email
        subject: Email subject
        body: Email body

    Returns:
        Success status
    """
    logger.info(f"Sending email to {to_email}")
    logger.info(f"Subject: {subject}")
    logger.info(f"Body: {body[:100]}...")

    # Mock email sending
    await asyncio.sleep(1)
    return True


async def send_linkedin_message(profile_url: str, message: str) -> bool:
    """
    Send LinkedIn message (mock implementation)

    Args:
        profile_url: LinkedIn profile URL
        message: Message content

    Returns:
        Success status
    """
    logger.info(f"Sending LinkedIn message to {profile_url}")
    await asyncio.sleep(1)
    return True


async def send_whatsapp_message(phone: str, message: str) -> bool:
    """
    Send WhatsApp message (mock implementation)

    Args:
        phone: Phone number
        message: Message content

    Returns:
        Success status
    """
    logger.info(f"Sending WhatsApp message to {phone}")
    await asyncio.sleep(1)
    return True


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "Personalized Engagement Agent", "version": "1.0.0", "status": "operational"}


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


@app.post("/send-outreach", response_model=EngagementResult)
async def manual_outreach(request: EngagementRequest):
    """
    Manual outreach trigger

    Args:
        request: Engagement request

    Returns:
        Engagement result
    """
    try:
        # Generate message
        message_data = await service_clients.genkit.generate_engagement_message(
            candidate_name=request.candidate_name,
            candidate_role="Software Engineer",
            job_title=request.job_title,
            company_name=request.company_name,
        )

        # Send via selected channel
        success = False
        if request.channel == "email":
            success = await send_email(
                to_email=request.candidate_email,
                subject=message_data.get("subject", "Opportunity"),
                body=message_data.get("message", ""),
            )
        elif request.channel == "linkedin":
            success = await send_linkedin_message(
                profile_url=f"https://linkedin.com/in/{request.candidate_id}",
                message=message_data.get("message", ""),
            )

        return EngagementResult(
            candidate_id=request.candidate_id,
            message_sent=success,
            channel=request.channel,
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error sending outreach: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8093)
