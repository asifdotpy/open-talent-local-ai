"""
Boolean Mastery Agent - OpenTalent Platform
Advanced search query generation for talent discovery
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

    logger.info("Starting Boolean Mastery Agent...")
    message_bus = MessageBus(config.redis_url)
    await message_bus.connect()

    service_clients = ServiceClients(
        conversation_url=config.conversation_service_url,
        voice_url=config.voice_service_url,
        avatar_url=config.avatar_service_url,
        interview_url=config.interview_service_url,
        genkit_url=config.genkit_service_url,
    )

    # Subscribe to boolean query requests
    await message_bus.subscribe(["agents:boolean"], handle_query_request)

    asyncio.create_task(message_bus.listen())
    logger.info("Boolean Mastery Agent ready on port 8092")

    yield

    logger.info("Shutting down Boolean Mastery Agent...")
    if message_bus:
        await message_bus.disconnect()


app = FastAPI(
    title="Boolean Mastery Agent",
    description="Advanced search query generation",
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


class QueryRequest(BaseModel):
    """Query generation request"""

    job_description: str
    platform: str = "linkedin"
    include_synonyms: bool = True


class QueryResult(BaseModel):
    """Generated query result"""

    query: str
    platform: str
    keywords: list[str]
    timestamp: datetime


async def handle_query_request(message):
    """Handle query generation request"""
    logger.info(f"Received query request: {message.payload}")

    try:
        pipeline_id = message.payload.get("pipeline_id")
        job_description = message.payload.get("job_description")
        platforms = message.payload.get("platforms", ["linkedin"])

        # Generate queries for each platform
        for platform in platforms:
            asyncio.create_task(generate_and_publish_query(pipeline_id, job_description, platform))
    except Exception as e:
        logger.error(f"Error handling query request: {e}")


async def generate_and_publish_query(pipeline_id: str, job_description: str, platform: str):
    """
    Generate boolean query and publish

    Args:
        pipeline_id: Pipeline ID
        job_description: Job description
        platform: Target platform
    """
    logger.info(f"Generating {platform} query for pipeline {pipeline_id}")

    try:
        # Use Genkit service to generate query
        query_data = await service_clients.genkit.generate_boolean_query(
            search_terms=job_description, platform=platform
        )

        # Publish query generated event
        await message_bus.publish_event(
            topic=Topics.PIPELINE_EVENTS,
            source_agent="boolean-mastery",
            message_type=MessageType.PIPELINE_UPDATE,
            payload={
                "pipeline_id": pipeline_id,
                "platform": platform,
                "query": query_data.get("query"),
                "keywords": query_data.get("keywords", []),
                "timestamp": datetime.utcnow().isoformat(),
            },
            priority=MessagePriority.MEDIUM,
        )

        logger.info(f"Query generated for {platform}: {query_data.get('query')[:100]}...")
    except Exception as e:
        logger.error(f"Error generating query: {e}")


async def generate_linkedin_query(job_description: str) -> dict[str, Any]:
    """
    Generate LinkedIn boolean query

    Args:
        job_description: Job description

    Returns:
        Query data
    """
    # Extract key skills and requirements
    keywords = extract_keywords(job_description)

    # Build boolean query
    skills = " OR ".join([f'"{skill}"' for skill in keywords["skills"][:5]])
    titles = " OR ".join([f'"{title}"' for title in keywords["titles"][:3]])

    query = f"({titles}) AND ({skills})"

    return {
        "query": query,
        "keywords": keywords["skills"] + keywords["titles"],
        "platform": "linkedin",
    }


async def generate_github_query(job_description: str) -> dict[str, Any]:
    """
    Generate GitHub search query

    Args:
        job_description: Job description

    Returns:
        Query data
    """
    keywords = extract_keywords(job_description)

    # GitHub query format
    languages = " ".join([f"language:{lang}" for lang in keywords["languages"][:3]])
    skills = " ".join(keywords["skills"][:5])

    query = f"{skills} {languages}"

    return {
        "query": query,
        "keywords": keywords["skills"] + keywords["languages"],
        "platform": "github",
    }


def extract_keywords(job_description: str) -> dict[str, list[str]]:
    """
    Extract keywords from job description

    Args:
        job_description: Job description

    Returns:
        Dictionary of keyword categories
    """
    # Mock implementation - in production, use NLP
    return {
        "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Redis"],
        "titles": ["Software Engineer", "Backend Developer", "Python Developer"],
        "languages": ["python", "javascript", "typescript"],
        "frameworks": ["Django", "FastAPI", "Flask"],
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "Boolean Mastery Agent", "version": "1.0.0", "status": "operational"}


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


@app.post("/generate-query", response_model=QueryResult)
async def generate_query(request: QueryRequest):
    """
    Generate boolean query

    Args:
        request: Query request

    Returns:
        Generated query
    """
    try:
        query_data = await service_clients.genkit.generate_boolean_query(
            job_description=request.job_description, platform=request.platform
        )

        return QueryResult(
            query=query_data.get("query", ""),
            platform=request.platform,
            keywords=query_data.get("keywords", []),
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        logger.error(f"Error generating query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8092)
