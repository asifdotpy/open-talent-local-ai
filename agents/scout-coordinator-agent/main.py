"""
Scout AI - Coordinator Agent for OpenTalent Platform
Orchestrates intelligent talent sourcing workflow across specialized agents.
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared import (
    AgentMessage,
    MessageBus,
    MessagePriority,
    MessageType,
    PipelineState,
    SourcingPipeline,
    Topics,
    get_config,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances
message_bus: Optional[MessageBus] = None
active_pipelines: dict[str, SourcingPipeline] = {}
active_connections: list[WebSocket] = []

# Configuration
config = get_config()


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global message_bus

    # Startup
    logger.info("Starting Scout AI Coordinator Agent...")
    message_bus = MessageBus(config.redis_url)
    await message_bus.connect()

    # Subscribe to agent events
    await message_bus.subscribe(
        [
            Topics.CANDIDATE_EVENTS,
            Topics.PIPELINE_EVENTS,
            Topics.ENGAGEMENT_EVENTS,
            Topics.MARKET_INTEL,
        ],
        handle_agent_event,
    )

    # Start message listener in background
    asyncio.create_task(message_bus.listen())
    logger.info("Scout AI ready on port 8090")

    yield

    # Shutdown
    logger.info("Shutting down Scout AI...")
    if message_bus:
        await message_bus.disconnect()


# Create FastAPI app
app = FastAPI(
    title="Scout AI - Coordinator Agent",
    description="Orchestrates intelligent talent sourcing workflow",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class StartPipelineRequest(BaseModel):
    """Request to start sourcing pipeline"""

    project_id: str
    job_description: str
    job_title: Optional[str] = None
    target_platforms: list[str] = ["linkedin", "github"]
    num_candidates_target: int = 50
    priority: str = "medium"


class PipelineStatusResponse(BaseModel):
    """Pipeline status response"""

    pipeline_id: str
    project_id: str
    state: str
    active_agents: list[str]
    candidates_found: int
    candidates_contacted: int
    candidates_responded: int
    interviews_scheduled: int
    progress_percentage: float
    started_at: datetime
    updated_at: datetime
    estimated_completion: Optional[datetime] = None


class PipelineListResponse(BaseModel):
    """List of pipelines"""

    pipelines: list[PipelineStatusResponse]
    total: int


# Event Handler
async def handle_agent_event(message: AgentMessage):
    """
    Handle events from specialized agents

    Args:
        message: Agent message
    """
    logger.info(f"Received event: {message.message_type} from {message.source_agent}")

    try:
        if message.message_type == MessageType.CANDIDATE_FOUND:
            await handle_candidate_found(message)
        elif message.message_type == MessageType.CANDIDATE_SCORED:
            await handle_candidate_scored(message)
        elif message.message_type == MessageType.OUTREACH_SENT:
            await handle_outreach_sent(message)
        elif message.message_type == MessageType.OUTREACH_RESPONSE:
            await handle_outreach_response(message)
        elif message.message_type == MessageType.PIPELINE_UPDATE:
            await handle_pipeline_update(message)
        elif message.message_type == MessageType.MARKET_INSIGHT:
            await handle_market_insight(message)
    except Exception as e:
        logger.error(f"Error handling event: {e}")

    # Broadcast event to all connected WebSockets
    await broadcast_event(message)


async def broadcast_event(message: AgentMessage):
    """Broadcast event to all connected clients"""
    if not active_connections:
        return

    dead_connections = []
    for connection in active_connections:
        try:
            await connection.send_json(
                {
                    "type": message.message_type.value
                    if hasattr(message.message_type, "value")
                    else str(message.message_type),
                    "payload": message.payload,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        except Exception:
            dead_connections.append(connection)

    for dead in dead_connections:
        active_connections.remove(dead)


async def handle_candidate_found(message: AgentMessage):
    """Handle candidate found event"""
    pipeline_id = message.payload.get("pipeline_id")
    if pipeline_id in active_pipelines:
        active_pipelines[pipeline_id].candidates_found += 1
        active_pipelines[pipeline_id].updated_at = datetime.utcnow()

        # If enough candidates, move to scoring phase
        if active_pipelines[pipeline_id].candidates_found >= 10:
            await transition_pipeline(pipeline_id, PipelineState.SCORING)


async def handle_candidate_scored(message: AgentMessage):
    """Handle candidate scored event"""
    pipeline_id = message.payload.get("pipeline_id")
    quality_score = message.payload.get("quality_score", 0)

    # If high quality candidate, trigger engagement
    if quality_score >= 70 and pipeline_id in active_pipelines:
        await trigger_engagement(pipeline_id, message.payload.get("candidate_id"))


async def handle_outreach_sent(message: AgentMessage):
    """Handle outreach sent event"""
    pipeline_id = message.payload.get("pipeline_id")
    if pipeline_id in active_pipelines:
        active_pipelines[pipeline_id].candidates_contacted += 1
        active_pipelines[pipeline_id].updated_at = datetime.utcnow()


async def handle_outreach_response(message: AgentMessage):
    """Handle outreach response event"""
    pipeline_id = message.payload.get("pipeline_id")
    if pipeline_id in active_pipelines:
        active_pipelines[pipeline_id].candidates_responded += 1
        active_pipelines[pipeline_id].updated_at = datetime.utcnow()

        # Trigger interview scheduling
        await trigger_interview(pipeline_id, message.payload.get("candidate_id"))


async def handle_pipeline_update(message: AgentMessage):
    """Handle pipeline update event"""
    pipeline_id = message.payload.get("pipeline_id")
    if pipeline_id in active_pipelines:
        active_pipelines[pipeline_id].updated_at = datetime.utcnow()


async def handle_market_insight(message: AgentMessage):
    """Handle market intelligence event"""
    logger.info(f"Market insight received: {message.payload.get('insight_type')}")


# Pipeline State Machine
async def transition_pipeline(pipeline_id: str, new_state: PipelineState):
    """
    Transition pipeline to new state

    Args:
        pipeline_id: Pipeline ID
        new_state: New pipeline state
    """
    if pipeline_id not in active_pipelines:
        return

    pipeline = active_pipelines[pipeline_id]
    old_state = pipeline.state
    pipeline.state = new_state
    pipeline.updated_at = datetime.utcnow()

    logger.info(f"Pipeline {pipeline_id} transitioned: {old_state} -> {new_state}")

    # Publish state change event
    await message_bus.publish_event(
        topic=Topics.PIPELINE_EVENTS,
        source_agent="scout-coordinator",
        message_type=MessageType.PIPELINE_UPDATE,
        payload={
            "pipeline_id": pipeline_id,
            "old_state": old_state,
            "new_state": new_state,
            "timestamp": datetime.utcnow().isoformat(),
        },
        priority=MessagePriority.HIGH,
    )

    # Trigger appropriate agents based on new state
    if new_state == PipelineState.SCORING:
        await activate_quality_agent(pipeline_id)
    elif new_state == PipelineState.ENGAGING:
        await activate_engagement_agent(pipeline_id)
    elif new_state == PipelineState.INTERVIEWING:
        await activate_interview_scheduling(pipeline_id)


async def activate_quality_agent(pipeline_id: str):
    """Activate quality-focused agent for scoring"""
    await message_bus.publish_event(
        topic="agents:quality",
        source_agent="scout-coordinator",
        message_type=MessageType.PIPELINE_UPDATE,
        payload={
            "pipeline_id": pipeline_id,
            "action": "start_scoring",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


async def activate_engagement_agent(pipeline_id: str):
    """Activate personalized engagement agent"""
    await message_bus.publish_event(
        topic="agents:engagement",
        source_agent="scout-coordinator",
        message_type=MessageType.PIPELINE_UPDATE,
        payload={
            "pipeline_id": pipeline_id,
            "action": "start_outreach",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


async def activate_interview_scheduling(pipeline_id: str):
    """Activate interview scheduling"""
    await message_bus.publish_event(
        topic=Topics.INTERVIEW_EVENTS,
        source_agent="scout-coordinator",
        message_type=MessageType.INTERVIEW_SCHEDULED,
        payload={
            "pipeline_id": pipeline_id,
            "action": "schedule_interviews",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


async def trigger_engagement(pipeline_id: str, candidate_id: str):
    """Trigger engagement for qualified candidate"""
    await message_bus.publish_event(
        topic=Topics.ENGAGEMENT_EVENTS,
        source_agent="scout-coordinator",
        message_type=MessageType.OUTREACH_SENT,
        payload={
            "pipeline_id": pipeline_id,
            "candidate_id": candidate_id,
            "action": "send_outreach",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


async def trigger_interview(pipeline_id: str, candidate_id: str):
    """Trigger interview scheduling"""
    await message_bus.publish_event(
        topic=Topics.INTERVIEW_EVENTS,
        source_agent="scout-coordinator",
        message_type=MessageType.INTERVIEW_SCHEDULED,
        payload={
            "pipeline_id": pipeline_id,
            "candidate_id": candidate_id,
            "action": "schedule_interview",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"New client connected. Total clients: {len(active_connections)}")
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total clients: {len(active_connections)}")


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Scout AI - Coordinator Agent",
        "version": "1.0.0",
        "status": "operational",
        "active_pipelines": len(active_pipelines),
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    redis_healthy = message_bus and message_bus.redis_client is not None
    return {
        "status": "healthy" if redis_healthy else "degraded",
        "redis": "connected" if redis_healthy else "disconnected",
        "active_pipelines": len(active_pipelines),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/pipelines/start", response_model=PipelineStatusResponse)
async def start_pipeline(request: StartPipelineRequest, background_tasks: BackgroundTasks):
    """
    Start a new sourcing pipeline

    Args:
        request: Pipeline start request
        background_tasks: FastAPI background tasks

    Returns:
        Pipeline status
    """
    # Generate pipeline ID
    pipeline_id = f"pipeline_{request.project_id}_{int(datetime.utcnow().timestamp())}"

    # Create pipeline
    pipeline = SourcingPipeline(
        id=pipeline_id,
        project_id=request.project_id,
        job_description=request.job_description,
        state=PipelineState.INITIATED,
        active_agents=[],
        candidates_found=0,
        candidates_contacted=0,
        candidates_responded=0,
        interviews_scheduled=0,
        interviews_completed=0,
    )

    active_pipelines[pipeline_id] = pipeline

    # Publish pipeline started event
    await message_bus.publish_event(
        topic=Topics.PIPELINE_EVENTS,
        source_agent="scout-coordinator",
        message_type=MessageType.PIPELINE_UPDATE,
        payload={
            "pipeline_id": pipeline_id,
            "project_id": request.project_id,
            "action": "started",
            "job_description": request.job_description,
            "platforms": request.target_platforms,
            "timestamp": datetime.utcnow().isoformat(),
        },
        priority=MessagePriority.HIGH,
    )

    # Start scanning phase in background
    background_tasks.add_task(initiate_scanning, pipeline_id, request)

    logger.info(f"Started pipeline {pipeline_id} for project {request.project_id}")

    return PipelineStatusResponse(
        pipeline_id=pipeline.id,
        project_id=pipeline.project_id,
        state=pipeline.state,
        active_agents=pipeline.active_agents,
        candidates_found=pipeline.candidates_found,
        candidates_contacted=pipeline.candidates_contacted,
        candidates_responded=pipeline.candidates_responded,
        interviews_scheduled=pipeline.interviews_scheduled,
        progress_percentage=0.0,
        started_at=pipeline.started_at,
        updated_at=pipeline.updated_at,
    )


async def initiate_scanning(pipeline_id: str, request: StartPipelineRequest):
    """
    Initiate scanning phase

    Args:
        pipeline_id: Pipeline ID
        request: Pipeline request
    """
    await asyncio.sleep(1)  # Brief delay

    # Transition to scanning state
    await transition_pipeline(pipeline_id, PipelineState.SCANNING)

    # Activate scanning agents
    await message_bus.publish_event(
        topic="agents:scanning",
        source_agent="scout-coordinator",
        message_type=MessageType.CANDIDATE_FOUND,
        payload={
            "pipeline_id": pipeline_id,
            "action": "start_scanning",
            "job_description": request.job_description,
            "platforms": request.target_platforms,
            "target_count": request.num_candidates_target,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

    # Activate boolean query generation
    await message_bus.publish_event(
        topic="agents:boolean",
        source_agent="scout-coordinator",
        message_type=MessageType.PIPELINE_UPDATE,
        payload={
            "pipeline_id": pipeline_id,
            "action": "generate_queries",
            "job_description": request.job_description,
            "platforms": request.target_platforms,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.get("/pipelines/{pipeline_id}", response_model=PipelineStatusResponse)
async def get_pipeline_status(pipeline_id: str):
    """
    Get pipeline status

    Args:
        pipeline_id: Pipeline ID

    Returns:
        Pipeline status
    """
    if pipeline_id not in active_pipelines:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline = active_pipelines[pipeline_id]

    # Calculate progress percentage
    total_stages = 5  # scanning, scoring, engaging, interviewing, completed
    current_stage = list(PipelineState).index(pipeline.state) + 1
    progress = (current_stage / total_stages) * 100

    return PipelineStatusResponse(
        pipeline_id=pipeline.id,
        project_id=pipeline.project_id,
        state=pipeline.state,
        active_agents=pipeline.active_agents,
        candidates_found=pipeline.candidates_found,
        candidates_contacted=pipeline.candidates_contacted,
        candidates_responded=pipeline.candidates_responded,
        interviews_scheduled=pipeline.interviews_scheduled,
        progress_percentage=progress,
        started_at=pipeline.started_at,
        updated_at=pipeline.updated_at,
    )


@app.get("/pipelines", response_model=PipelineListResponse)
async def list_pipelines(
    project_id: Optional[str] = None, state: Optional[str] = None, limit: int = 50
):
    """
    List all pipelines

    Args:
        project_id: Optional filter by project ID
        state: Optional filter by state
        limit: Max results

    Returns:
        List of pipelines
    """
    pipelines = list(active_pipelines.values())

    # Filter by project_id
    if project_id:
        pipelines = [p for p in pipelines if p.project_id == project_id]

    # Filter by state
    if state:
        pipelines = [p for p in pipelines if p.state == state]

    # Limit results
    pipelines = pipelines[:limit]

    # Convert to response models
    responses = []
    for pipeline in pipelines:
        total_stages = 5
        current_stage = list(PipelineState).index(pipeline.state) + 1
        progress = (current_stage / total_stages) * 100

        responses.append(
            PipelineStatusResponse(
                pipeline_id=pipeline.id,
                project_id=pipeline.project_id,
                state=pipeline.state,
                active_agents=pipeline.active_agents,
                candidates_found=pipeline.candidates_found,
                candidates_contacted=pipeline.candidates_contacted,
                candidates_responded=pipeline.candidates_responded,
                interviews_scheduled=pipeline.interviews_scheduled,
                progress_percentage=progress,
                started_at=pipeline.started_at,
                updated_at=pipeline.updated_at,
            )
        )

    return PipelineListResponse(pipelines=responses, total=len(responses))


@app.post("/pipelines/{pipeline_id}/pause")
async def pause_pipeline(pipeline_id: str):
    """Pause a pipeline"""
    if pipeline_id not in active_pipelines:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    await transition_pipeline(pipeline_id, PipelineState.PAUSED)

    return {"status": "paused", "pipeline_id": pipeline_id}


@app.post("/pipelines/{pipeline_id}/resume")
async def resume_pipeline(pipeline_id: str):
    """Resume a paused pipeline"""
    if pipeline_id not in active_pipelines:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline = active_pipelines[pipeline_id]

    # Resume at previous state
    if pipeline.state == PipelineState.PAUSED:
        await transition_pipeline(pipeline_id, PipelineState.SCANNING)

    return {"status": "resumed", "pipeline_id": pipeline_id}


@app.delete("/pipelines/{pipeline_id}")
async def stop_pipeline(pipeline_id: str):
    """Stop and remove a pipeline"""
    if pipeline_id not in active_pipelines:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    # Publish stop event
    await message_bus.publish_event(
        topic=Topics.PIPELINE_EVENTS,
        source_agent="scout-coordinator",
        message_type=MessageType.PIPELINE_UPDATE,
        payload={
            "pipeline_id": pipeline_id,
            "action": "stopped",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

    # Remove from active pipelines
    del active_pipelines[pipeline_id]

    return {"status": "stopped", "pipeline_id": pipeline_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8090)
