import asyncio
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import httpx
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from config import ALLOWED_ORIGINS, TIMEOUT_CONFIG, logger, setup_logging
from routes.vetta_routes import router as vetta_router
from routes.interview_routes import router as interview_router

# Configure logging
setup_logging()

app = FastAPI(
    title="OpenTalent - Interview Service",
    description="Manages Jitsi interview room infrastructure, lifecycle, and participants",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    logger.info(f"[{request_id}] {request.method} {request.url.path} - Request started")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )

    return response


# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include question builder routes
# app.include_router(question_router, prefix="/api/v1", tags=["question-builder"])

# Include Vetta AI routes
app.include_router(vetta_router)
app.include_router(interview_router, prefix="/api/v1")

# --- OpenAPI Documentation Routes ---


@app.get("/docs", include_in_schema=False)
async def docs_redirect():
    """Redirect to the principal Swagger UI documentation.

    Returns:
        A RedirectResponse to the /docs endpoint.
    """
    return RedirectResponse(url="/docs")


@app.get("/doc", include_in_schema=False)
async def doc_redirect():
    """Alternative redirect path for principal Swagger UI documentation.

    Returns:
        A RedirectResponse to the /docs endpoint.
    """
    return RedirectResponse(url="/docs")


@app.get("/api-docs", include_in_schema=False)
async def api_docs():
    """Comprehensive API documentation with route scanning."""
    routes_info = []

    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            # Skip documentation routes themselves
            if route.path in ["/docs", "/doc", "/api-docs", "/redoc", "/openapi.json"]:
                continue

            route_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, "name", "unknown"),
                "tags": getattr(route, "tags", []),
                "summary": getattr(route, "summary", ""),
                "description": getattr(route, "description", ""),
            }
            routes_info.append(route_info)

    # Group routes by tags
    routes_by_tag = {}
    untagged_routes = []

    for route in routes_info:
        if route["tags"]:
            for tag in route["tags"]:
                if tag not in routes_by_tag:
                    routes_by_tag[tag] = []
                routes_by_tag[tag].append(route)
        else:
            untagged_routes.append(route)

    return {
        "service": "Interview Service",
        "version": "1.0.0",
        "description": "Manages Jitsi interview room infrastructure, lifecycle, and participants",
        "base_url": "http://localhost:8004",
        "total_routes": len(routes_info),
        "routes_by_category": {"tagged_routes": routes_by_tag, "untagged_routes": untagged_routes},
        "categories": {
            "rooms": "Interview room management (create, join, leave, status)",
            "interviews": "Interview session lifecycle and orchestration",
            "questions": "AI-generated interview questions and assessment",
            "health": "Service health checks and monitoring",
        },
        "documentation_urls": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
            "api_docs": "/api-docs",
        },
        "last_updated": "2025-01-09",
    }


# --- Data Models ---


class RoomStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    ENDED = "ended"
    EXPIRED = "expired"


class ParticipantRole(str, Enum):
    CANDIDATE = "candidate"
    INTERVIEWER = "interviewer"
    OBSERVER = "observer"
    AI_AVATAR = "ai_avatar"


class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"


class Participant(BaseModel):
    user_id: str
    role: ParticipantRole
    display_name: str
    joined_at: datetime | None = None
    connection_status: ConnectionStatus = ConnectionStatus.CONNECTING


class RoomSecurity(BaseModel):
    password_protected: bool = False
    waiting_room_enabled: bool = False
    moderator_approval_required: bool = False
    recording_allowed: bool = True


class InterviewQuestion(BaseModel):
    """Interview question with AI metadata."""

    id: str
    text: str
    order: int
    generated_at: datetime
    ai_metadata: dict[str, Any] | None = {}


class InterviewAnswer(BaseModel):
    """Candidate's answer to an interview question."""

    question_id: str
    answer: str
    timestamp: datetime
    analysis: Optional["ResponseAnalysis"] = None


class FollowupQuestion(BaseModel):
    """Suggested follow-up question."""

    question: str = Field(..., description="Follow-up question text")
    priority: int = Field(..., description="Question priority (1-5, higher = more important)")
    reasoning: str = Field(..., description="Reason for suggesting this question")
    expected_outcome: str = Field(..., description="Expected learning outcome")


class InterviewRoom(BaseModel):
    """Interview room with full lifecycle management."""

    room_id: str
    room_name: str
    jitsi_url: str
    interview_session_id: str
    created_at: datetime
    expires_at: datetime
    status: RoomStatus = RoomStatus.CREATED
    participants: list[Participant] = Field(default_factory=list)
    security_settings: RoomSecurity = Field(default_factory=RoomSecurity)
    max_duration_minutes: int = 45
    current_question_index: int | None = None
    questions: list[InterviewQuestion] = Field(default_factory=list)
    responses: list["InterviewAnswer"] = Field(default_factory=list)
    response_analyses: list["ResponseAnalysis"] = Field(default_factory=list)
    interview_strategy: dict[str, Any] = Field(default_factory=dict)


class CreateRoomRequest(BaseModel):
    interview_session_id: str
    participants: list[Participant]
    duration_minutes: int = 45
    security_settings: RoomSecurity | None = None
    job_id: str | None = None  # NEW: Job/project ID for dynamic loading
    project_id: str | None = None  # NEW: Alternative to job_id
    job_description: str | None = None  # NEW: Direct job description (fallback)


class JoinRoomRequest(BaseModel):
    participant: Participant


# --- WebRTC Signaling Models ---


class WebRTCMessageType(str, Enum):
    OFFER = "offer"
    ANSWER = "answer"
    ICE_CANDIDATE = "ice_candidate"
    HANGUP = "hangup"
    READY = "ready"


class WebRTCSignal(BaseModel):
    type: WebRTCMessageType
    session_id: str
    room_id: str
    participant_id: str
    data: dict | None = None
    timestamp: datetime | None = None


class WebRTCConnection(BaseModel):
    connection_id: str
    session_id: str
    room_id: str
    participant_id: str
    status: str = "connecting"  # connecting, connected, failed, closed
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)


class AudioStreamConfig(BaseModel):
    sample_rate: int = 16000
    channels: int = 1
    enable_stt: bool = True
    enable_vad: bool = True
    enable_noise_reduction: bool = True
    real_time_transcription: bool = True


# --- WebSocket Live Transcription Models ---


class TranscriptionSegment(BaseModel):
    """Real-time transcription segment with timing information."""

    text: str
    start_time: float
    end_time: float
    confidence: float
    speaker_id: str | None = None
    is_final: bool = False
    words: list[dict] = []  # Word-level timing and confidence


class LiveTranscriptionUpdate(BaseModel):
    """Live transcription update message."""

    room_id: str
    session_id: str
    participant_id: str
    segment: TranscriptionSegment
    timestamp: datetime = Field(default_factory=datetime.now)


class WebSocketConnection(BaseModel):
    """WebSocket connection for live transcription."""

    connection_id: str
    room_id: str
    participant_id: str
    websocket: object | None = None  # FastAPI WebSocket object
    connected_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)


# --- AI Interview Intelligence Models ---


class SentimentAnalysis(BaseModel):
    """Sentiment analysis results for candidate responses."""

    polarity: float = Field(..., description="Sentiment polarity (-1 to 1, negative to positive)")
    subjectivity: float = Field(
        ..., description="Subjectivity score (0 to 1, objective to subjective)"
    )
    confidence: float = Field(..., description="Analysis confidence score")
    emotion: str = Field(..., description="Primary emotion detected")
    intensity: float = Field(..., description="Emotional intensity score")
    keywords: list[str] = Field(default_factory=list, description="Key emotional indicators")


class ResponseQuality(BaseModel):
    """Quality assessment of candidate responses."""

    overall_score: float = Field(..., description="Overall quality score (0-10)")
    completeness: float = Field(..., description="Response completeness score")
    relevance: float = Field(..., description="Relevance to question score")
    clarity: float = Field(..., description="Clarity and coherence score")
    technical_accuracy: float = Field(..., description="Technical accuracy score")
    strengths: list[str] = Field(default_factory=list, description="Response strengths")
    improvements: list[str] = Field(default_factory=list, description="Areas for improvement")


class BiasDetection(BaseModel):
    """Bias detection results in responses and interview process."""

    bias_score: float = Field(..., description="Overall bias score (0-1, higher = more biased)")
    flags: list[str] = Field(default_factory=list, description="Specific bias indicators detected")
    severity: str = Field(..., description="Bias severity level")
    categories: list[str] = Field(default_factory=list, description="Bias categories identified")
    recommendations: list[str] = Field(
        default_factory=list, description="Bias mitigation recommendations"
    )


class ExpertiseAssessment(BaseModel):
    """Assessment of candidate's expertise level."""

    level: str = Field(
        ..., description="Expertise level (beginner, intermediate, advanced, expert)"
    )
    confidence: float = Field(..., description="Assessment confidence score")
    technical_skills: list[str] = Field(
        default_factory=list, description="Identified technical skills"
    )
    knowledge_gaps: list[str] = Field(default_factory=list, description="Knowledge gaps identified")
    experience_years: int | None = Field(None, description="Estimated years of experience")


class FollowupQuestion(BaseModel):
    """Suggested follow-up question."""

    question: str = Field(..., description="Follow-up question text")
    priority: int = Field(..., description="Question priority (1-5, higher = more important)")
    reasoning: str = Field(..., description="Reason for suggesting this question")
    expected_outcome: str = Field(..., description="Expected learning outcome")


class ResponseAnalysis(BaseModel):
    """Comprehensive analysis of a candidate response."""

    response_id: str = Field(..., description="Unique identifier for this analysis")
    question_id: str = Field(..., description="ID of the question being analyzed")
    sentiment: SentimentAnalysis = Field(..., description="Sentiment analysis results")
    quality: ResponseQuality = Field(..., description="Content quality assessment")
    bias_detection: BiasDetection = Field(..., description="Bias detection results")
    expertise_assessment: ExpertiseAssessment = Field(..., description="Expertise level assessment")
    followup_suggestions: list[FollowupQuestion] = Field(
        default_factory=list, description="Suggested follow-up questions"
    )
    analyzed_at: datetime = Field(
        default_factory=datetime.now, description="When the analysis was performed"
    )


class NextQuestionRequest(BaseModel):
    """Request for next AI-generated question."""

    current_responses: list[InterviewAnswer] = Field(default_factory=list)
    job_requirements: str | None = None
    interview_phase: str | None = None


class ResponseAnalysisRequest(BaseModel):
    """Request for response analysis."""

    question_id: str
    response_text: str
    question_context: str
    participant_id: str


class InterviewAdaptationRequest(BaseModel):
    """Request for interview strategy adaptation."""

    current_phase: str
    time_remaining_minutes: int
    performance_indicators: dict[str, Any] = Field(default_factory=dict)


class InterviewPerformance(BaseModel):
    """Overall interview performance analysis."""

    overall_score: float
    sentiment_trend: str
    expertise_level: str
    bias_incidents: int
    quality_trend: str
    recommendations: list[str]


class InterviewAdaptation(BaseModel):
    """Interview adaptation recommendations."""

    question_difficulty: str
    focus_areas: list[str]
    time_adjustments: dict[str, Any]
    immediate_actions: list[str]
    strategy_changes: list[str]


class IntelligenceReport(BaseModel):
    """Comprehensive AI intelligence report."""

    summary: dict[str, Any]
    sentiment_analysis: dict[str, Any]
    bias_report: dict[str, Any]
    expertise_evaluation: dict[str, Any]
    quality_metrics: dict[str, Any]
    recommendations: list[str]
    interview_effectiveness: float


# --- In-Memory Storage (Replace with DB in production) ---
rooms_store: dict[str, InterviewRoom] = {}
webrtc_connections: dict[str, WebRTCConnection] = {}  # connection_id -> connection
websocket_connections: dict[str, WebSocketConnection] = {}  # connection_id -> ws_connection
transcription_history: dict[str, list[TranscriptionSegment]] = {}  # room_id -> segments

# --- API Endpoints ---


@app.get("/")
async def root():
    """Root endpoint for the Interview Service."""
    logger.info("Root endpoint accessed")
    active_rooms_count = len([r for r in rooms_store.values() if r.status == RoomStatus.ACTIVE])
    return {
        "message": "OpenTalent Interview Service - Room Infrastructure Management",
        "version": "1.0.0",
        "active_rooms": active_rooms_count,
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint for the Interview Service.

    Monitors in-memory room storage, active session counts, and service
    integration status.

    Returns:
        A dictionary containing health status, version, and room metrics.
    """
    logger.info("Health check requested")
    try:
        # Calculate room statistics
        active_rooms = len([r for r in rooms_store.values() if r.status == RoomStatus.ACTIVE])
        total_rooms = len(rooms_store)
        expired_rooms = len([r for r in rooms_store.values() if r.status == RoomStatus.EXPIRED])

        logger.debug(
            f"Room stats: {active_rooms} active, {total_rooms} total, {expired_rooms} expired"
        )

        status = {
            "status": "healthy",
            "service": "interview-infrastructure",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "api": "healthy",
                "room_management": "healthy",
                "jitsi_integration": "healthy",
            },
            "metrics": {
                "rooms_active": active_rooms,
                "rooms_total": total_rooms,
                "rooms_expired": expired_rooms,
                "memory_usage_rooms": len(rooms_store),
            },
        }

        # Health checks based on room metrics
        if active_rooms > 50:  # Threshold for high load
            logger.warning(f"High load detected: {active_rooms} active rooms")
            status["status"] = "degraded"
            status["components"]["room_management"] = "high_load"

        if total_rooms > 1000:  # Memory concern threshold
            logger.warning(f"High memory usage: {total_rooms} total rooms")
            status["status"] = "degraded"
            status["components"]["memory"] = "high_usage"

        logger.info("Health check completed successfully")
        return status

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "interview-infrastructure",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        )


@app.post("/api/v1/rooms/create", response_model=InterviewRoom)
async def create_interview_room(request: CreateRoomRequest):
    """Creates a new Jitsi interview room with full lifecycle management."""
    logger.info(f"Creating interview room for session: {request.interview_session_id}")
    try:
        # Input validation
        if not request.interview_session_id or not request.interview_session_id.strip():
            logger.error("Empty interview_session_id provided")
            raise HTTPException(status_code=400, detail="interview_session_id is required")

        if not request.participants or len(request.participants) == 0:
            logger.error("No participants provided for room creation")
            raise HTTPException(status_code=400, detail="At least one participant is required")

        if request.duration_minutes <= 0 or request.duration_minutes > 480:  # Max 8 hours
            logger.error(f"Invalid duration: {request.duration_minutes} minutes")
            raise HTTPException(
                status_code=400, detail="Duration must be between 1 and 480 minutes"
            )

        # Check for duplicate session
        existing_room = next(
            (
                r
                for r in rooms_store.values()
                if r.interview_session_id == request.interview_session_id
                and r.status != RoomStatus.ENDED
            ),
            None,
        )
        if existing_room:
            logger.warning(f"Room already exists for session {request.interview_session_id}")
            raise HTTPException(
                status_code=409,
                detail=f"Room already exists for session {request.interview_session_id}",
            )

        # Generate unique identifiers
        room_id = f"room-{uuid.uuid4().hex[:12]}"
        room_name = f"fios-interview-{request.interview_session_id}-{room_id[-6:]}"

        logger.debug(f"Generated room_id: {room_id}, room_name: {room_name}")

        # Create room configuration
        room = InterviewRoom(
            room_id=room_id,
            room_name=room_name,
            jitsi_url=f"https://meet.jit.si/{room_name}",
            interview_session_id=request.interview_session_id,
            created_at=datetime.now(),
            expires_at=datetime.now()
            + timedelta(minutes=request.duration_minutes + 15),  # 15min buffer
            status=RoomStatus.CREATED,
            participants=request.participants,
            security_settings=request.security_settings or RoomSecurity(),
            max_duration_minutes=request.duration_minutes,
        )

        # Store room
        rooms_store[room_id] = room

        logger.info(
            f"Interview room created successfully: {room_id} for {len(request.participants)} participants"
        )
        return room

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error creating room: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")


@app.post("/api/v1/interviews/start")
async def start_interview(request: CreateRoomRequest):
    """Start a new interview session with voice processing and conversation.
    Creates room and initializes voice service with adaptive conversation.
    """
    logger.info(f"Starting interview session: {request.interview_session_id}")

    try:
        # Create the room first
        room = InterviewRoom(
            room_id=f"room-{uuid.uuid4().hex[:12]}",
            room_name=f"interview-{request.interview_session_id}-{uuid.uuid4().hex[:6]}",
            jitsi_url=f"https://meet.jit.si/{uuid.uuid4().hex[:12]}",
            interview_session_id=request.interview_session_id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=request.duration_minutes + 15),
            status=RoomStatus.CREATED,
            participants=request.participants,
            security_settings=request.security_settings or RoomSecurity(),
            max_duration_minutes=request.duration_minutes,
        )

        rooms_store[room.room_id] = room

        # Start voice service session with conversation
        try:
            # Determine job description to use
            job_description = request.job_description
            if not job_description:
                # Use job_id or project_id if available for dynamic loading
                job_identifier = request.job_id or request.project_id
                if job_identifier:
                    job_description = f"Job ID: {job_identifier}"
                else:
                    job_description = "Software engineering position requiring Python, React, and cloud technologies"

            async with httpx.AsyncClient(timeout=10.0) as client:
                voice_response = await client.post(
                    "http://localhost:8002/webrtc/start",
                    json={
                        "session_id": request.interview_session_id,
                        "job_description": job_description,
                        "job_id": request.job_id,
                        "project_id": request.project_id,
                    },
                )

                if voice_response.status_code != 200:
                    logger.error(f"Failed to start voice service: {voice_response.text}")
                    # Continue anyway - room is created
                else:
                    logger.info(f"Voice service started for session {request.interview_session_id}")
        except Exception as e:
            logger.error(f"Failed to connect to voice service: {e}")
            # Continue - interview can still work without voice processing

        logger.info(
            f"Interview started: room={room.room_id}, session={request.interview_session_id}"
        )
        return room

    except Exception as e:
        logger.error(f"Failed to start interview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")


@app.post("/api/v1/rooms/{room_id}/join")
async def join_room(room_id: str, request: JoinRoomRequest):
    """Add a participant to an interview room."""
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    room = rooms_store[room_id]

    if room.status == RoomStatus.ENDED:
        raise HTTPException(status_code=410, detail="Room has ended")

    if room.status == RoomStatus.EXPIRED:
        raise HTTPException(status_code=410, detail="Room has expired")

    # Update participant status
    participant = request.participant
    participant.joined_at = datetime.now()
    participant.connection_status = ConnectionStatus.CONNECTED

    # Add or update participant
    existing_participant = next(
        (p for p in room.participants if p.user_id == participant.user_id), None
    )
    if existing_participant:
        existing_participant.connection_status = ConnectionStatus.CONNECTED
        existing_participant.joined_at = datetime.now()
    else:
        room.participants.append(participant)

    # Update room status to active if first real participant joins
    if room.status == RoomStatus.CREATED and any(
        p.role != ParticipantRole.AI_AVATAR for p in room.participants
    ):
        room.status = RoomStatus.ACTIVE

    rooms_store[room_id] = room

    return {
        "message": "Successfully joined room",
        "room_id": room_id,
        "participant_count": len(room.participants),
        "room_status": room.status,
    }


@app.delete("/api/v1/rooms/{room_id}/end")
async def end_room(room_id: str):
    """End an interview room and cleanup resources."""
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    room = rooms_store[room_id]

    if room.status == RoomStatus.ENDED:
        return {"message": "Room already ended"}

    # Update room status
    room.status = RoomStatus.ENDED

    # Disconnect all participants
    for participant in room.participants:
        participant.connection_status = ConnectionStatus.DISCONNECTED

    rooms_store[room_id] = room

    return {
        "message": "Room ended successfully",
        "room_id": room_id,
        "duration_minutes": (datetime.now() - room.created_at).total_seconds() / 60,
        "participants_count": len(room.participants),
    }


@app.get("/api/v1/rooms/{room_id}/status", response_model=InterviewRoom)
async def get_room_status(room_id: str):
    """Get current status and details of an interview room."""
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    room = rooms_store[room_id]

    # Auto-expire rooms that are past their expiration
    if datetime.now() > room.expires_at and room.status not in [
        RoomStatus.ENDED,
        RoomStatus.EXPIRED,
    ]:
        room.status = RoomStatus.EXPIRED
        rooms_store[room_id] = room

    return room


@app.get("/api/v1/rooms")
async def list_rooms(status: RoomStatus | None = None):
    """List all rooms, optionally filtered by status."""
    rooms = list(rooms_store.values())

    if status:
        rooms = [r for r in rooms if r.status == status]

    return {
        "rooms": rooms,
        "total_count": len(rooms),
        "active_count": len([r for r in rooms if r.status == RoomStatus.ACTIVE]),
    }


@app.get("/api/v1/rooms/{room_id}/participants")
async def get_room_participants(room_id: str):
    """Get list of participants in a room."""
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    room = rooms_store[room_id]

    return {
        "room_id": room_id,
        "participants": room.participants,
        "participant_count": len(room.participants),
        "connected_count": len(
            [p for p in room.participants if p.connection_status == ConnectionStatus.CONNECTED]
        ),
    }


# --- WebRTC Audio Streaming Endpoints ---


@app.post("/api/v1/rooms/{room_id}/webrtc/start", tags=["webrtc"])
async def start_webrtc_audio_stream(
    room_id: str, participant_id: str, config: AudioStreamConfig | None = None
):
    """Start WebRTC audio streaming for a participant in an interview room.

    This initializes the voice service WebRTC worker and establishes
    real-time audio streaming with STT, VAD, and optional TTS.
    """
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    room = rooms_store[room_id]
    if room.status not in [RoomStatus.ACTIVE, RoomStatus.CREATED]:
        raise HTTPException(status_code=400, detail="Room is not active")

    # Verify participant exists in room
    participant = next((p for p in room.participants if p.user_id == participant_id), None)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found in room")

    # Generate connection ID
    connection_id = f"webrtc-{room_id}-{participant_id}-{uuid.uuid4().hex[:8]}"

    # Create WebRTC connection record
    connection = WebRTCConnection(
        connection_id=connection_id,
        session_id=room.interview_session_id,
        room_id=room_id,
        participant_id=participant_id,
        status="initializing",
    )
    webrtc_connections[connection_id] = connection

    # Start voice service WebRTC session
    try:
        stream_config = config or AudioStreamConfig()

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
            voice_response = await client.post(
                "http://localhost:8002/webrtc/start",
                json={
                    "session_id": room.interview_session_id,
                    "connection_id": connection_id,
                    "room_id": room_id,
                    "participant_id": participant_id,
                    "config": {
                        "sample_rate": stream_config.sample_rate,
                        "channels": stream_config.channels,
                        "enable_stt": stream_config.enable_stt,
                        "enable_vad": stream_config.enable_vad,
                        "enable_noise_reduction": stream_config.enable_noise_reduction,
                        "real_time_transcription": stream_config.real_time_transcription,
                    },
                },
            )

            if voice_response.status_code != 200:
                logger.error(f"Failed to start voice service WebRTC: {voice_response.text}")
                connection.status = "failed"
                raise HTTPException(status_code=500, detail="Failed to initialize voice service")

            connection.status = "ready"
            logger.info(
                f"WebRTC audio streaming started for participant {participant_id} in room {room_id}"
            )

            return {
                "connection_id": connection_id,
                "status": "ready",
                "voice_service_status": voice_response.json(),
                "config": stream_config.dict(),
                "message": "WebRTC audio streaming initialized successfully",
            }

    except httpx.TimeoutException:
        logger.error(f"Timeout connecting to voice service for room {room_id}")
        connection.status = "failed"
        raise HTTPException(status_code=504, detail="Voice service timeout")
    except Exception as e:
        logger.error(f"Failed to start WebRTC streaming: {e}")
        connection.status = "failed"
        raise HTTPException(status_code=500, detail=f"Failed to start WebRTC streaming: {str(e)}")


@app.post("/api/v1/rooms/{room_id}/webrtc/signal", tags=["webrtc"])
async def webrtc_signaling(room_id: str, signal: WebRTCSignal):
    """Handle WebRTC signaling messages (offer, answer, ICE candidates).

    This endpoint acts as a signaling server, forwarding messages
    between participants and the voice service WebRTC worker.
    """
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    # Find the WebRTC connection
    connection = next(
        (
            c
            for c in webrtc_connections.values()
            if c.room_id == room_id and c.participant_id == signal.participant_id
        ),
        None,
    )
    if not connection:
        raise HTTPException(status_code=404, detail="WebRTC connection not found")

    # Update connection activity
    connection.last_activity = datetime.now()

    try:
        # Forward signal to voice service
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=2.0)) as client:
            voice_response = await client.post(
                "http://localhost:8002/webrtc/signal",
                json={
                    "connection_id": connection.connection_id,
                    "type": signal.type.value,
                    "data": signal.data,
                    "participant_id": signal.participant_id,
                    "room_id": room_id,
                    "session_id": signal.session_id,
                },
            )

            if voice_response.status_code != 200:
                logger.error(f"Voice service signaling failed: {voice_response.text}")
                raise HTTPException(status_code=500, detail="Signaling failed")

            logger.debug(
                f"WebRTC signal forwarded: {signal.type.value} for participant {signal.participant_id}"
            )

            return {
                "status": "forwarded",
                "response": voice_response.json() if voice_response.content else None,
            }

    except httpx.TimeoutException:
        logger.error(f"Timeout during WebRTC signaling for room {room_id}")
        raise HTTPException(status_code=504, detail="Signaling timeout")
    except Exception as e:
        logger.error(f"WebRTC signaling error: {e}")
        raise HTTPException(status_code=500, detail=f"Signaling error: {str(e)}")


@app.get("/api/v1/rooms/{room_id}/webrtc/status", tags=["webrtc"])
async def get_webrtc_status(room_id: str):
    """Get WebRTC connection status for all participants in a room."""
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    room_connections = [c for c in webrtc_connections.values() if c.room_id == room_id]

    return {
        "room_id": room_id,
        "total_connections": len(room_connections),
        "connections": [
            {
                "connection_id": c.connection_id,
                "participant_id": c.participant_id,
                "status": c.status,
                "created_at": c.created_at.isoformat(),
                "last_activity": c.last_activity.isoformat(),
            }
            for c in room_connections
        ],
    }


@app.delete("/api/v1/rooms/{room_id}/webrtc/stop", tags=["webrtc"])
async def stop_webrtc_audio_stream(room_id: str, participant_id: str | None = None):
    """Stop WebRTC audio streaming for a room or specific participant.

    If participant_id is not provided, stops all connections in the room.
    """
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    # Find connections to stop
    if participant_id:
        connections_to_stop = [
            c
            for c in webrtc_connections.values()
            if c.room_id == room_id and c.participant_id == participant_id
        ]
    else:
        connections_to_stop = [c for c in webrtc_connections.values() if c.room_id == room_id]

    if not connections_to_stop:
        return {"message": "No active WebRTC connections found"}

    stopped_connections = []

    for connection in connections_to_stop:
        try:
            # Stop voice service WebRTC session
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=2.0)) as client:
                voice_response = await client.post(
                    "http://localhost:8002/webrtc/stop",
                    json={
                        "connection_id": connection.connection_id,
                        "session_id": connection.session_id,
                    },
                )

                if voice_response.status_code == 200:
                    connection.status = "closed"
                    stopped_connections.append(connection.connection_id)
                    logger.info(f"WebRTC connection stopped: {connection.connection_id}")
                else:
                    logger.error(f"Failed to stop voice service WebRTC: {voice_response.text}")

        except Exception as e:
            logger.error(f"Error stopping WebRTC connection {connection.connection_id}: {e}")

    # Clean up closed connections after a delay
    asyncio.create_task(cleanup_closed_connections())

    return {
        "message": f"Stopped {len(stopped_connections)} WebRTC connections",
        "stopped_connections": stopped_connections,
        "total_requested": len(connections_to_stop),
    }


async def cleanup_closed_connections():
    """Clean up closed WebRTC connections after a delay."""
    await asyncio.sleep(30)  # Wait 30 seconds

    closed_connections = [
        cid for cid, conn in webrtc_connections.items() if conn.status == "closed"
    ]

    for connection_id in closed_connections:
        del webrtc_connections[connection_id]
        logger.debug(f"Cleaned up closed WebRTC connection: {connection_id}")


# --- WebSocket Live Transcription Endpoints ---


@app.websocket("/ws/transcription/{room_id}")
async def websocket_live_transcription(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for real-time transcription updates.

    Clients connect to receive live transcription segments as they are generated
    during the interview. Supports multiple clients per room.
    """
    await websocket.accept()

    # Generate connection ID
    connection_id = f"ws-{room_id}-{uuid.uuid4().hex[:8]}"

    # Create WebSocket connection record
    ws_connection = WebSocketConnection(
        connection_id=connection_id,
        room_id=room_id,
        participant_id="viewer",  # Default to viewer, can be updated
        websocket=websocket,
    )
    websocket_connections[connection_id] = ws_connection

    logger.info(f"WebSocket transcription client connected: {connection_id} for room {room_id}")

    try:
        # Send initial connection confirmation
        await websocket.send_json(
            {
                "type": "connection_established",
                "connection_id": connection_id,
                "room_id": room_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Send existing transcription history if available
        if room_id in transcription_history:
            await websocket.send_json(
                {
                    "type": "transcription_history",
                    "segments": [segment.dict() for segment in transcription_history[room_id]],
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for client messages (optional - clients can just listen)
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)

                # Handle client messages
                if data.get("type") == "ping":
                    await websocket.send_json(
                        {"type": "pong", "timestamp": datetime.now().isoformat()}
                    )
                elif data.get("type") == "request_history":
                    # Send transcription history
                    segments = transcription_history.get(room_id, [])
                    await websocket.send_json(
                        {
                            "type": "transcription_history",
                            "segments": [segment.dict() for segment in segments],
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                else:
                    logger.debug(f"Unknown WebSocket message type: {data.get('type')}")

            except TimeoutError:
                # Send keepalive ping
                await websocket.send_json({"type": "ping", "timestamp": datetime.now().isoformat()})

    except WebSocketDisconnect:
        logger.info(f"WebSocket transcription client disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket transcription error for {connection_id}: {e}")
    finally:
        # Clean up connection
        if connection_id in websocket_connections:
            del websocket_connections[connection_id]


@app.post("/api/v1/rooms/{room_id}/transcription", tags=["transcription"])
async def submit_transcription_segment(
    room_id: str, segment: TranscriptionSegment, session_id: str, participant_id: str
):
    """Submit a transcription segment from the voice service.

    This endpoint is called by the voice service when new transcription
    segments are available during WebRTC streaming.
    """
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    # Store transcription segment
    if room_id not in transcription_history:
        transcription_history[room_id] = []

    transcription_history[room_id].append(segment)

    # Create live update message
    update = LiveTranscriptionUpdate(
        room_id=room_id, session_id=session_id, participant_id=participant_id, segment=segment
    )

    # Broadcast to all WebSocket clients for this room
    try:
        await broadcast_transcription_update(room_id, update)
        logger.info(f"Broadcast completed for room {room_id}")
    except Exception as e:
        logger.error(f"Broadcast failed for room {room_id}: {e}")

    logger.info(f"Transcription segment stored for room {room_id}: '{segment.text[:50]}...'")

    return {
        "status": "stored",
        "segment_id": len(transcription_history[room_id]) - 1,
        "clients_notified": len(
            [c for c in websocket_connections.values() if c.room_id == room_id]
        ),
    }


async def broadcast_transcription_update(room_id: str, update: LiveTranscriptionUpdate):
    """Broadcast transcription update to all WebSocket clients in the room."""
    room_connections = [c for c in websocket_connections.values() if c.room_id == room_id]

    logger.info(
        f"Broadcasting transcription update for room {room_id} to {len(room_connections)} clients"
    )

    disconnected_clients = []

    for connection in room_connections:
        try:
            if connection.websocket:
                # Create fully JSON-serializable dict manually - ensure NO datetime objects
                segment_dict = {
                    "text": str(update.segment.text),
                    "start_time": float(update.segment.start_time),
                    "end_time": float(update.segment.end_time),
                    "confidence": float(update.segment.confidence),
                    "speaker_id": str(update.segment.speaker_id)
                    if update.segment.speaker_id
                    else None,
                    "is_final": bool(update.segment.is_final),
                    "words": list(update.segment.words) if update.segment.words else [],
                }

                update_data = {
                    "room_id": str(update.room_id),
                    "session_id": str(update.session_id),
                    "participant_id": str(update.participant_id),
                    "segment": segment_dict,
                    "timestamp": update.timestamp.isoformat()
                    if hasattr(update.timestamp, "isoformat")
                    else str(update.timestamp),
                }

                message = {
                    "type": "transcription_update",
                    "data": update_data,
                    "timestamp": datetime.now().isoformat(),
                }

                logger.debug(
                    f"Sending message to client {connection.connection_id}: type={message['type']}"
                )
                await connection.websocket.send_json(message)
                connection.last_activity = datetime.now()
                logger.info(
                    f"Successfully sent transcription update to client {connection.connection_id}"
                )
        except Exception as e:
            logger.error(
                f"Failed to send transcription update to client {connection.connection_id}: {e}"
            )
            logger.error(
                f"Message data types: segment.text={type(update.segment.text)}, timestamp={type(update.timestamp)}"
            )
            disconnected_clients.append(connection.connection_id)

    # Clean up disconnected clients
    for client_id in disconnected_clients:
        if client_id in websocket_connections:
            del websocket_connections[client_id]


@app.get("/api/v1/rooms/{room_id}/transcription", tags=["transcription"])
async def get_transcription_history(
    room_id: str, limit: int | None = None, offset: int | None = 0
):
    """Get transcription history for a room.

    Returns stored transcription segments with optional pagination.
    """
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    segments = transcription_history.get(room_id, [])

    # Apply pagination
    if offset:
        segments = segments[offset:]
    if limit:
        segments = segments[:limit]

    return {
        "room_id": room_id,
        "total_segments": len(transcription_history.get(room_id, [])),
        "segments": [segment.dict() for segment in segments],
        "returned_count": len(segments),
    }


@app.delete("/api/v1/rooms/{room_id}/transcription", tags=["transcription"])
async def clear_transcription_history(room_id: str):
    """Clear transcription history for a room.

    Useful for resetting transcription data or freeing memory.
    """
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    segment_count = len(transcription_history.get(room_id, []))

    if room_id in transcription_history:
        del transcription_history[room_id]

    logger.info(f"Cleared {segment_count} transcription segments for room {room_id}")

    return {"message": f"Cleared {segment_count} transcription segments", "room_id": room_id}


@app.get("/api/v1/transcription/status", tags=["transcription"])
async def get_transcription_status():
    """Get overall transcription system status.

    Returns statistics about active WebSocket connections and transcription data.
    """
    total_segments = sum(len(segments) for segments in transcription_history.values())
    active_rooms = len([r for r in transcription_history if r in rooms_store])

    return {
        "active_websocket_connections": len(websocket_connections),
        "rooms_with_transcription": len(transcription_history),
        "active_transcription_rooms": active_rooms,
        "total_transcription_segments": total_segments,
        "connections_by_room": {
            room_id: len([c for c in websocket_connections.values() if c.room_id == room_id])
            for room_id in transcription_history
        },
        "timestamp": datetime.now().isoformat(),
    }


# Legacy endpoints for backward compatibility


# --- AI Interview Intelligence Helper Functions ---


async def analyze_candidate_expertise(responses: list[InterviewAnswer]) -> str:
    """Analyze candidate's expertise level from their responses."""
    if not responses:
        return "unknown"

    # Simple heuristic based on response length and technical terms
    total_length = sum(len(r.answer) for r in responses)
    avg_length = total_length / len(responses)

    technical_indicators = [
        "algorithm",
        "database",
        "api",
        "framework",
        "architecture",
        "scalability",
    ]
    technical_count = sum(
        1 for r in responses for term in technical_indicators if term.lower() in r.answer.lower()
    )

    if avg_length > 500 and technical_count >= 3:
        return "expert"
    elif avg_length > 300 and technical_count >= 2:
        return "advanced"
    elif avg_length > 150 and technical_count >= 1:
        return "intermediate"
    else:
        return "beginner"


async def analyze_response_sentiment(response_text: str) -> SentimentAnalysis:
    """Analyze sentiment of candidate response using TextBlob."""
    try:
        from textblob import TextBlob

        blob = TextBlob(response_text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # Determine primary emotion
        if polarity > 0.3:
            emotion = "positive"
        elif polarity < -0.3:
            emotion = "negative"
        else:
            emotion = "neutral"

        # Extract emotional keywords
        positive_words = ["good", "great", "excellent", "amazing", "love", "enjoy"]
        negative_words = ["bad", "terrible", "hate", "difficult", "challenging", "struggle"]

        keywords = []
        for word in positive_words:
            if word in response_text.lower():
                keywords.append(word)
        for word in negative_words:
            if word in response_text.lower():
                keywords.append(word)

        return SentimentAnalysis(
            polarity=polarity,
            subjectivity=subjectivity,
            confidence=0.8,  # TextBlob confidence estimate
            emotion=emotion,
            intensity=abs(polarity),
            keywords=keywords[:5],  # Limit to top 5
        )
    except ImportError:
        # Fallback if TextBlob not available
        return SentimentAnalysis(
            polarity=0.0,
            subjectivity=0.5,
            confidence=0.5,
            emotion="neutral",
            intensity=0.0,
            keywords=[],
        )


async def analyze_response_quality(response_text: str, question_context: str) -> ResponseQuality:
    """Analyze the quality of a candidate response."""
    # Basic quality metrics
    length_score = min(len(response_text) / 200, 1.0) * 2.5  # Max 2.5 points for length

    # Relevance check (simple keyword matching)
    question_keywords = set(question_context.lower().split())
    response_keywords = set(response_text.lower().split())
    relevance_score = (
        len(question_keywords.intersection(response_keywords))
        / max(len(question_keywords), 1)
        * 2.5
    )

    # Clarity assessment (sentence structure)
    sentences = response_text.split(".")
    avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    clarity_score = max(
        0, 2.5 - abs(avg_sentence_length - 15) / 10
    )  # Optimal ~15 words per sentence

    # Technical accuracy (placeholder - would need domain-specific analysis)
    technical_score = 2.5  # Default medium score

    overall_score = (length_score + relevance_score + clarity_score + technical_score) / 4

    return ResponseQuality(
        overall_score=round(overall_score, 2),
        completeness=length_score / 2.5,
        relevance=relevance_score / 2.5,
        clarity=clarity_score / 2.5,
        technical_accuracy=technical_score / 2.5,
        strengths=[
            "Good length" if length_score > 2 else "",
            "Relevant content" if relevance_score > 2 else "",
        ],
        improvements=[
            "Add more detail" if length_score < 1.5 else "",
            "Improve clarity" if clarity_score < 1.5 else "",
        ],
    )


async def detect_response_bias(
    response_text: str, participants: list[Participant]
) -> BiasDetection:
    """Detect potential bias indicators in responses."""
    bias_flags = []
    categories = []
    severity = "low"

    # Gender bias indicators
    gender_terms = ["he", "she", "his", "her", "man", "woman", "guy", "girl"]
    gender_count = sum(1 for term in gender_terms if term in response_text.lower())
    if gender_count > 2:
        bias_flags.append("gender_stereotyping")
        categories.append("gender")

    # Age bias indicators
    age_terms = ["young", "old", "experienced", "junior", "senior", "generation"]
    age_count = sum(1 for term in age_terms if term in response_text.lower())
    if age_count > 1:
        bias_flags.append("age_bias")
        categories.append("age")

    # Cultural bias indicators
    cultural_terms = ["culture", "background", "ethnic", "nationality", "accent"]
    cultural_count = sum(1 for term in cultural_terms if term in response_text.lower())
    if cultural_count > 1:
        bias_flags.append("cultural_bias")
        categories.append("cultural")

    # Calculate severity
    total_flags = len(bias_flags)
    if total_flags >= 3:
        severity = "high"
    elif total_flags >= 2:
        severity = "medium"

    bias_score = min(total_flags * 0.2, 1.0)

    recommendations = []
    if "gender_stereotyping" in bias_flags:
        recommendations.append("Use gender-neutral language")
    if "age_bias" in bias_flags:
        recommendations.append("Focus on skills and experience, not age")
    if "cultural_bias" in bias_flags:
        recommendations.append("Emphasize universal competencies")

    return BiasDetection(
        bias_score=bias_score,
        flags=bias_flags,
        severity=severity,
        categories=categories,
        recommendations=recommendations,
    )


async def assess_response_expertise(
    response_text: str, question_context: str
) -> ExpertiseAssessment:
    """Assess candidate's expertise level from response."""
    # Technical skill detection
    technical_skills = []
    skill_keywords = {
        "python": ["python", "django", "flask", "pandas", "numpy"],
        "javascript": ["javascript", "react", "node", "typescript", "vue"],
        "database": ["sql", "postgresql", "mongodb", "redis", "mysql"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
        "system_design": ["architecture", "scalability", "microservices", "api"],
    }

    for category, keywords in skill_keywords.items():
        if any(kw in response_text.lower() for kw in keywords):
            technical_skills.append(category)

    # Experience estimation based on content
    experience_indicators = {
        "beginner": ["learning", "basic", "introduction", "tutorial"],
        "intermediate": ["experience", "worked on", "implemented", "developed"],
        "advanced": ["architected", "led", "optimized", "scaled"],
        "expert": ["designed systems", "mentored", "innovated", "pioneered"],
    }

    expertise_scores = dict.fromkeys(experience_indicators.keys(), 0)

    for level, indicators in experience_indicators.items():
        for indicator in indicators:
            if indicator in response_text.lower():
                expertise_scores[level] += 1

    # Determine expertise level
    max_score = max(expertise_scores.values())
    if max_score == 0:
        level = "intermediate"  # Default
    else:
        level = max(expertise_scores, key=expertise_scores.get)

    # Estimate years of experience
    years_estimate = {"beginner": 1, "intermediate": 3, "advanced": 5, "expert": 8}.get(level, 3)

    # Knowledge gaps (placeholder)
    knowledge_gaps = []
    if not technical_skills:
        knowledge_gaps.append("technical skills not demonstrated")

    return ExpertiseAssessment(
        level=level,
        confidence=0.7,
        technical_skills=technical_skills,
        knowledge_gaps=knowledge_gaps,
        experience_years=years_estimate,
    )


async def generate_followup_questions(
    response_text: str,
    question_context: str,
    sentiment: SentimentAnalysis,
    quality: ResponseQuality,
) -> list[FollowupQuestion]:
    """Generate follow-up questions based on response analysis."""
    questions = []

    # If response was too brief, ask for elaboration
    if quality.completeness < 0.6:
        questions.append(
            FollowupQuestion(
                question="Can you elaborate on that point with a specific example?",
                priority=5,
                reasoning="Response was brief and needs more detail",
                expected_outcome="Better understanding of candidate's experience",
            )
        )

    # If technical accuracy was low, probe deeper
    if quality.technical_accuracy < 0.6:
        questions.append(
            FollowupQuestion(
                question="Can you walk me through the technical details of how you would implement this?",
                priority=4,
                reasoning="Technical understanding needs clarification",
                expected_outcome="Assessment of technical competence",
            )
        )

    # If sentiment was negative, explore concerns
    if sentiment.polarity < -0.2:
        questions.append(
            FollowupQuestion(
                question="What challenges did you face with this approach, and how did you overcome them?",
                priority=3,
                reasoning="Negative sentiment indicates potential learning opportunity",
                expected_outcome="Understanding of problem-solving approach",
            )
        )

    # Always have a general follow-up
    questions.append(
        FollowupQuestion(
            question="How does this experience relate to the requirements of this role?",
            priority=2,
            reasoning="Connect candidate experience to job requirements",
            expected_outcome="Assessment of role fit",
        )
    )

    return questions[:3]  # Return top 3


def extract_job_requirements(room: InterviewRoom) -> str:
    """Extract job requirements from room metadata."""
    # This would typically come from room metadata or job description
    return "Software engineering position requiring Python, React, and cloud technologies"


def determine_interview_phase(question_number: int) -> str:
    """Determine current interview phase based on question number."""
    if question_number <= 3:
        return "introduction"
    elif question_number <= 7:
        return "technical"
    elif question_number <= 10:
        return "behavioral"
    else:
        return "closing"


async def generate_fallback_question(room: InterviewRoom, question_number: int) -> dict[str, Any]:
    """Generate a fallback question when AI service is unavailable."""
    fallback_questions = [
        "Can you tell me about your experience with software development?",
        "What programming languages are you most comfortable with?",
        "Describe a challenging project you've worked on and how you handled it.",
        "How do you approach learning new technologies?",
        "What are your career goals for the next few years?",
    ]

    question_text = fallback_questions[min(question_number - 1, len(fallback_questions) - 1)]

    question = InterviewQuestion(
        id=f"fallback-{room.room_id}-{question_number}",
        text=question_text,
        order=question_number,
        generated_at=datetime.now(),
        ai_metadata={"fallback": True},
    )

    return {
        "question": question,
        "question_number": question_number,
        "ai_metadata": question.ai_metadata,
        "estimated_difficulty": "medium",
        "bias_mitigation_applied": False,
    }


def generate_interview_recommendations(analysis: ResponseAnalysis) -> list[str]:
    """Generate interview recommendations based on analysis."""
    recommendations = []

    if analysis.sentiment.polarity < -0.3:
        recommendations.append("Address candidate concerns and provide positive reinforcement")

    if analysis.quality.overall_score < 6:
        recommendations.append("Consider additional technical questions to assess competence")

    if analysis.bias_detection.bias_score > 0.5:
        recommendations.append("Review questions for potential bias and ensure fairness")

    if analysis.expertise_assessment.level == "expert":
        recommendations.append("Explore leadership and architecture experience")

    return recommendations


async def analyze_interview_performance(room: InterviewRoom) -> InterviewPerformance:
    """Analyze overall interview performance."""
    analyses = getattr(room, "response_analyses", [])
    if not analyses:
        return InterviewPerformance(
            overall_score=5.0,
            sentiment_trend="neutral",
            expertise_level="unknown",
            bias_incidents=0,
            quality_trend="unknown",
            recommendations=["Continue with standard interview process"],
        )

    # Calculate averages
    avg_sentiment = sum(a.sentiment.polarity for a in analyses) / len(analyses)
    avg_quality = sum(a.quality.overall_score for a in analyses) / len(analyses)
    total_bias = sum(len(a.bias_detection.flags) for a in analyses)

    # Determine trends
    sentiment_trend = (
        "positive" if avg_sentiment > 0.2 else "negative" if avg_sentiment < -0.2 else "neutral"
    )
    quality_trend = "improving" if avg_quality > 7 else "declining" if avg_quality < 5 else "stable"

    # Expertise level (use latest assessment)
    expertise_level = analyses[-1].expertise_assessment.level if analyses else "unknown"

    overall_score = (avg_quality + (1 - total_bias * 0.1) * 10) / 2

    return InterviewPerformance(
        overall_score=round(overall_score, 2),
        sentiment_trend=sentiment_trend,
        expertise_level=expertise_level,
        bias_incidents=total_bias,
        quality_trend=quality_trend,
        recommendations=[
            "Continue monitoring candidate responses",
            "Adjust question difficulty as needed",
        ],
    )


async def generate_interview_adaptations(
    performance: InterviewPerformance, current_phase: str, time_remaining: int
) -> InterviewAdaptation:
    """Generate interview adaptation recommendations."""
    adaptations = {
        "question_difficulty": "medium",
        "focus_areas": ["technical_skills", "problem_solving"],
        "time_adjustments": {},
        "immediate_actions": [],
        "strategy_changes": [],
    }

    # Adjust difficulty based on performance
    if performance.overall_score > 8:
        adaptations["question_difficulty"] = "advanced"
        adaptations["focus_areas"].append("leadership")
    elif performance.overall_score < 6:
        adaptations["question_difficulty"] = "basic"
        adaptations["focus_areas"].append("fundamentals")

    # Time adjustments
    if time_remaining < 15 and performance.overall_score > 7:
        adaptations["time_adjustments"]["early_termination"] = True
        adaptations["immediate_actions"].append(
            "Consider concluding interview early - strong candidate"
        )
    elif time_remaining < 10:
        adaptations["immediate_actions"].append("Focus on key remaining questions")

    # Strategy changes based on sentiment
    if performance.sentiment_trend == "negative":
        adaptations["strategy_changes"].append("Incorporate more positive reinforcement")
        adaptations["immediate_actions"].append("Address any concerns raised by candidate")

    return InterviewAdaptation(**adaptations)


async def generate_intelligence_report(
    analyses: list[ResponseAnalysis], responses: list[InterviewAnswer], room: InterviewRoom
) -> IntelligenceReport:
    """Generate comprehensive AI intelligence report."""
    if not analyses:
        return IntelligenceReport(
            summary={"total_responses": 0, "average_quality": 0},
            sentiment_analysis={"overall_sentiment": "neutral"},
            bias_report={"total_incidents": 0},
            expertise_evaluation={"level": "unknown"},
            quality_metrics={"average_score": 0},
            recommendations=["Insufficient data for analysis"],
            interview_effectiveness=5.0,
        )

    # Summary statistics
    total_responses = len(responses)
    avg_quality = sum(a.quality.overall_score for a in analyses) / len(analyses)
    avg_sentiment = sum(a.sentiment.polarity for a in analyses) / len(analyses)

    # Sentiment analysis summary
    sentiment_distribution = {
        "positive": len([a for a in analyses if a.sentiment.polarity > 0.2]),
        "neutral": len([a for a in analyses if -0.2 <= a.sentiment.polarity <= 0.2]),
        "negative": len([a for a in analyses if a.sentiment.polarity < -0.2]),
    }

    # Bias report
    total_bias_incidents = sum(len(a.bias_detection.flags) for a in analyses)
    bias_categories = {}
    for a in analyses:
        for category in a.bias_detection.categories:
            bias_categories[category] = bias_categories.get(category, 0) + 1

    # Expertise evaluation
    expertise_levels = [a.expertise_assessment.level for a in analyses]
    most_common_expertise = (
        max(set(expertise_levels), key=expertise_levels.count) if expertise_levels else "unknown"
    )

    # Quality metrics
    quality_trends = {
        "completeness": sum(a.quality.completeness for a in analyses) / len(analyses),
        "relevance": sum(a.quality.relevance for a in analyses) / len(analyses),
        "clarity": sum(a.quality.clarity for a in analyses) / len(analyses),
        "technical_accuracy": sum(a.quality.technical_accuracy for a in analyses) / len(analyses),
    }

    # Generate recommendations
    recommendations = []
    if avg_quality < 6:
        recommendations.append("Consider additional training or skill development questions")
    if total_bias_incidents > 2:
        recommendations.append("Review interview process for bias mitigation")
    if avg_sentiment < -0.1:
        recommendations.append("Address candidate concerns and improve interview experience")
    if most_common_expertise == "expert":
        recommendations.append("Explore advanced technical and leadership capabilities")

    # Interview effectiveness score
    effectiveness = (avg_quality + (10 - total_bias_incidents) + (avg_sentiment + 1) * 5) / 3
    effectiveness = max(0, min(10, effectiveness))

    return IntelligenceReport(
        summary={
            "total_responses": total_responses,
            "average_quality": round(avg_quality, 2),
            "average_sentiment": round(avg_sentiment, 2),
            "duration_minutes": (datetime.now() - room.created_at).total_seconds() / 60,
        },
        sentiment_analysis={
            "overall_sentiment": "positive"
            if avg_sentiment > 0.2
            else "negative"
            if avg_sentiment < -0.2
            else "neutral",
            "distribution": sentiment_distribution,
            "emotional_intensity": sum(a.sentiment.intensity for a in analyses) / len(analyses),
        },
        bias_report={
            "total_incidents": total_bias_incidents,
            "categories": bias_categories,
            "severity_distribution": {
                "low": len([a for a in analyses if a.bias_detection.severity == "low"]),
                "medium": len([a for a in analyses if a.bias_detection.severity == "medium"]),
                "high": len([a for a in analyses if a.bias_detection.severity == "high"]),
            },
        },
        expertise_evaluation={
            "level": most_common_expertise,
            "technical_skills_identified": list(
                {skill for a in analyses for skill in a.expertise_assessment.technical_skills}
            ),
            "average_experience_years": sum(
                a.expertise_assessment.experience_years or 0 for a in analyses
            )
            / len(analyses),
        },
        quality_metrics={
            "average_score": round(avg_quality, 2),
            "trends": quality_trends,
            "strengths_distribution": {
                "high_quality": len([a for a in analyses if a.quality.overall_score >= 8]),
                "medium_quality": len([a for a in analyses if 6 <= a.quality.overall_score < 8]),
                "low_quality": len([a for a in analyses if a.quality.overall_score < 6]),
            },
        },
        recommendations=recommendations,
        interview_effectiveness=round(effectiveness, 2),
    )


# --- AI Interview Intelligence Endpoints ---


@app.post("/api/v1/rooms/{room_id}/next-question", tags=["ai-intelligence"])
async def get_next_ai_question(room_id: str, request: NextQuestionRequest):
    """Generate the next AI-powered interview question based on:
    - Previous responses and their quality
    - Candidate's expertise level assessment
    - Job requirements matching
    - Sentiment analysis of responses
    - Bias detection and mitigation.
    """
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    room = rooms_store[room_id]
    if room.status not in [RoomStatus.ACTIVE, RoomStatus.CREATED]:
        raise HTTPException(status_code=400, detail="Room is not active")

    try:
        # Get conversation context from previous responses
        previous_responses = []
        if hasattr(room, "responses") and room.responses:
            previous_responses = room.responses[-5:]  # Last 5 responses for context

        # Analyze candidate expertise from responses
        expertise_level = await analyze_candidate_expertise(previous_responses)

        # Get job requirements from room metadata
        job_requirements = extract_job_requirements(room)

        # Generate question using AI conversation service
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
            ai_response = await client.post(
                "http://localhost:8003/conversation/generate-adaptive-question",
                json={
                    "room_id": room_id,
                    "session_id": room.interview_session_id,
                    "previous_responses": [
                        r.dict() if hasattr(r, "dict") else r for r in previous_responses
                    ],
                    "expertise_level": expertise_level,
                    "job_requirements": job_requirements,
                    "question_number": len(previous_responses) + 1,
                    "interview_phase": determine_interview_phase(len(previous_responses) + 1),
                    "bias_mitigation": True,
                },
            )

            if ai_response.status_code != 200:
                logger.error(f"AI question generation failed: {ai_response.text}")
                # Fallback to basic question
                return await generate_fallback_question(room, len(previous_responses) + 1)

            question_data = ai_response.json()

            # Store question in room
            question = InterviewQuestion(
                id=f"q-{room_id}-{len(previous_responses) + 1}",
                text=question_data["question"],
                order=len(previous_responses) + 1,
                generated_at=datetime.now(),
                ai_metadata={
                    "expertise_level": expertise_level,
                    "bias_score": question_data.get("bias_score", 0.0),
                    "sentiment_context": question_data.get("sentiment_context", "neutral"),
                    "difficulty": question_data.get("difficulty", "medium"),
                },
            )

            if not hasattr(room, "questions"):
                room.questions = []
            room.questions.append(question)

            # Update room current question
            room.current_question_index = len(room.questions) - 1

            rooms_store[room_id] = room

            return {
                "question": question,
                "question_number": len(room.questions),
                "ai_metadata": question.ai_metadata,
                "estimated_difficulty": question_data.get("difficulty", "medium"),
                "bias_mitigation_applied": question_data.get("bias_mitigation_applied", False),
            }

    except Exception as e:
        logger.error(f"AI question generation failed: {e}")
        return await generate_fallback_question(room, len(previous_responses) + 1)


@app.post("/api/v1/rooms/{room_id}/analyze-response", tags=["ai-intelligence"])
async def analyze_candidate_response(room_id: str, request: ResponseAnalysisRequest):
    """Analyze candidate response with comprehensive AI intelligence:
    - Sentiment analysis for emotional context
    - Content quality assessment
    - Expertise level evaluation
    - Bias detection in response patterns
    - Follow-up question suggestions.
    """
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    room = rooms_store[room_id]

    try:
        # Perform sentiment analysis
        sentiment_result = await analyze_response_sentiment(request.response_text)

        # Analyze content quality
        quality_result = await analyze_response_quality(
            request.response_text, request.question_context
        )

        # Detect potential bias indicators
        bias_result = await detect_response_bias(request.response_text, room.participants)

        # Assess expertise level
        expertise_result = await assess_response_expertise(
            request.response_text, request.question_context
        )

        # Generate follow-up suggestions
        followup_suggestions = await generate_followup_questions(
            request.response_text, request.question_context, sentiment_result, quality_result
        )

        # Store analysis results
        analysis = ResponseAnalysis(
            response_id=f"resp-{room_id}-{request.question_id}",
            question_id=request.question_id,
            sentiment=sentiment_result,
            quality=quality_result,
            bias_detection=bias_result,
            expertise_assessment=expertise_result,
            followup_suggestions=followup_suggestions,
            analyzed_at=datetime.now(),
        )

        if not hasattr(room, "response_analyses"):
            room.response_analyses = []
        room.response_analyses.append(analysis)

        # Update room with response
        response_record = InterviewAnswer(
            question_id=request.question_id,
            answer=request.response_text,
            timestamp=datetime.now(),
            analysis=analysis,
        )

        if not hasattr(room, "responses"):
            room.responses = []
        room.responses.append(response_record)

        rooms_store[room_id] = room

        return {
            "analysis": analysis,
            "sentiment_summary": sentiment_result,
            "quality_score": quality_result.overall_score,
            "bias_flags": bias_result.flags,
            "expertise_level": expertise_result.level,
            "followup_questions": followup_suggestions[:3],  # Top 3 suggestions
            "recommendations": generate_interview_recommendations(analysis),
        }

    except Exception as e:
        logger.error(f"Response analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/v1/rooms/{room_id}/adapt-interview", tags=["ai-intelligence"])
async def adapt_interview_strategy(room_id: str, request: InterviewAdaptationRequest):
    """Adapt interview strategy based on candidate performance:
    - Adjust question difficulty
    - Modify interview focus areas
    - Suggest early termination or extension
    - Provide real-time feedback to interviewer.
    """
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    room = rooms_store[room_id]

    try:
        # Analyze overall interview performance
        performance_analysis = await analyze_interview_performance(room)

        # Generate adaptation recommendations
        adaptations = await generate_interview_adaptations(
            performance_analysis, request.current_phase, request.time_remaining_minutes
        )

        # Update room strategy
        if not hasattr(room, "interview_strategy"):
            room.interview_strategy = {}

        room.interview_strategy.update(
            {
                "adaptations": adaptations,
                "performance_analysis": performance_analysis,
                "adapted_at": datetime.now(),
                "current_phase": request.current_phase,
            }
        )

        rooms_store[room_id] = room

        return {
            "adaptations": adaptations,
            "performance_summary": performance_analysis,
            "strategy_update": room.interview_strategy,
            "recommendations": adaptations.immediate_actions,
        }

    except Exception as e:
        logger.error(f"Interview adaptation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Adaptation failed: {str(e)}")


@app.get("/api/v1/rooms/{room_id}/intelligence-report", tags=["ai-intelligence"])
async def get_interview_intelligence_report(room_id: str):
    """Generate comprehensive AI intelligence report for the interview:
    - Sentiment analysis summary
    - Bias detection results
    - Expertise assessment
    - Interview effectiveness metrics
    - Recommendations for improvement.
    """
    if room_id not in rooms_store:
        raise HTTPException(status_code=404, detail="Room not found")

    room = rooms_store[room_id]

    try:
        # Compile all analyses
        analyses = getattr(room, "response_analyses", [])
        responses = getattr(room, "responses", [])

        # Generate comprehensive report
        report = await generate_intelligence_report(analyses, responses, room)

        return {
            "room_id": room_id,
            "report": report,
            "generated_at": datetime.now().isoformat(),
            "total_responses": len(responses),
            "total_analyses": len(analyses),
        }

    except Exception as e:
        logger.error(f"Intelligence report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8004))
    host = os.environ.get("HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=port)
