"""
Desktop Integration Service - Main Application

Unified API gateway for OpenTalent Desktop App and microservices.
Lightweight, demo-focused implementation (Phase 0).
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.core.service_discovery import ServiceDiscovery
from app.models.schemas import (
    HealthResponse,
    InterviewConfig,
    InterviewResponseRequest,
    InterviewSession,
    Message,
    ModelInfo,
    ModelsResponse,
    StartInterviewRequest,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global service discovery
service_discovery: ServiceDiscovery | None = None
http_client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    global service_discovery, http_client

    logger.info("🚀 Starting Desktop Integration Service (Gateway) on port 8009...")
    logger.info("=" * 70)

    # Initialize service discovery
    service_discovery = ServiceDiscovery()

    # Initialize HTTP client
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(settings.service_timeout),
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
    )

    # Initial health check
    health = await service_discovery.check_all_services()
    online_count = health["summary"]["online"]
    total_count = health["summary"]["total"]
    logger.info(f"📊 Services Status: {online_count}/{total_count} services online")
    logger.info("=" * 70)

    # List all services
    for name, status in health["services"].items():
        icon = "✅" if status["status"] == "online" else "❌"
        visibility = "(hidden)" if name.startswith("_") else ""
        latency = f"{status.get('latencyMs', 'N/A')}ms" if status.get("latencyMs") else "N/A"
        logger.info(f"{icon} {name:30s} {status['status']:10s} {latency:>10s} {visibility}")

    logger.info("=" * 70)
    logger.info("✨ Gateway ready to serve requests!")

    yield

    # Cleanup
    logger.info("🛑 Shutting down Desktop Integration Service...")
    if http_client:
        await http_client.aclose()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="OpenTalent Desktop Integration Service",
    description="Unified API gateway for desktop app and microservices",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware for Electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health & Status Endpoints
# ============================================================================


@app.get("/health")
async def health_check() -> HealthResponse:
    """
    Get gateway and service health status.

    Returns overall status and per-service details for status bar.
    """
    if not service_discovery:
        raise HTTPException(status_code=503, detail="Service discovery not initialized")

    health = await service_discovery.check_all_services()

    return HealthResponse(
        status=health["status"],
        timestamp=datetime.now(),
        services=health["services"],
        summary=health["summary"],
    )


@app.get("/api/v1/system/status")
async def system_status() -> dict:
    """Get comprehensive system status."""
    if not service_discovery:
        raise HTTPException(status_code=503, detail="Service discovery not initialized")

    health = await service_discovery.check_all_services()

    # Filter out hidden services (those starting with _) from UI display
    visible_services = {k: v for k, v in health["services"].items() if not k.startswith("_")}
    visible_online = sum(1 for s in visible_services.values() if s["status"] == "online")
    visible_total = len(visible_services)

    return {
        "gateway_version": "0.1.0",
        "status": health["status"],
        "timestamp": datetime.now().isoformat(),
        "services_online": visible_online,
        "services_total": visible_total,
        "service_details": visible_services,
    }


# ============================================================================
# Service Registry Endpoint (NEW - Shows all 14 services)
# ============================================================================


@app.get("/api/v1/services")
async def list_services() -> dict:
    """
    List all 14 registered OpenTalent microservices.

    Returns registry with URLs and current status for each service.
    """
    if not service_discovery:
        raise HTTPException(status_code=503, detail="Service discovery not initialized")

    health = await service_discovery.check_all_services()

    # Organize services by category
    service_registry = {
        "core_services": {
            "scout-service": {
                "port": 8000,
                "url": health["services"].get("scout-service", {}).get("url", ""),
                "status": health["services"].get("scout-service", {}).get("status", "unknown"),
                "description": "Talent sourcing and resume parsing",
            },
            "user-service": {
                "port": 8001,
                "url": health["services"].get("user-service", {}).get("url", ""),
                "status": health["services"].get("user-service", {}).get("status", "unknown"),
                "description": "User management and authentication",
            },
            "candidate-service": {
                "port": 8006,
                "url": health["services"].get("candidate-service", {}).get("url", ""),
                "status": health["services"].get("candidate-service", {}).get("status", "unknown"),
                "description": "Candidate profile management",
            },
        },
        "ai_services": {
            "conversation-service": {
                "port": 8002,
                "url": health["services"].get("conversation-service", {}).get("url", ""),
                "status": health["services"]
                .get("conversation-service", {})
                .get("status", "unknown"),
                "description": "AI conversation and chat management",
            },
            "interview-service": {
                "port": 8005,
                "url": health["services"].get("interview-service", {}).get("url", ""),
                "status": health["services"].get("interview-service", {}).get("status", "unknown"),
                "description": "Interview orchestration and flow control",
            },
            "_granite-interview-service": {
                "port": 8005,
                "url": health["services"].get("_granite-interview-service", {}).get("url", ""),
                "status": health["services"]
                .get("_granite-interview-service", {})
                .get("status", "unknown"),
                "description": "Granite interview with custom training (internal)",
                "hidden": True,
            },
        },
        "media_services": {
            "voice-service": {
                "port": 8003,
                "url": health["services"].get("voice-service", {}).get("url", ""),
                "status": health["services"].get("voice-service", {}).get("status", "unknown"),
                "description": "Text-to-speech synthesis with Piper",
            },
            "avatar-service": {
                "port": 8004,
                "url": health["services"].get("avatar-service", {}).get("url", ""),
                "status": health["services"].get("avatar-service", {}).get("status", "unknown"),
                "description": "3D avatar rendering with phoneme lip-sync",
            },
        },
        "analytics_services": {
            "analytics-service": {
                "port": 8007,
                "url": health["services"].get("analytics-service", {}).get("url", ""),
                "status": health["services"].get("analytics-service", {}).get("status", "unknown"),
                "description": "Sentiment analysis and interview metrics",
            },
            "ai-auditing-service": {
                "port": 8012,
                "url": health["services"].get("ai-auditing-service", {}).get("url", ""),
                "status": health["services"]
                .get("ai-auditing-service", {})
                .get("status", "unknown"),
                "description": "AI bias detection and fairness auditing",
            },
            "explainability-service": {
                "port": 8013,
                "url": health["services"].get("explainability-service", {}).get("url", ""),
                "status": health["services"]
                .get("explainability-service", {})
                .get("status", "unknown"),
                "description": "AI decision explainability and interpretability",
            },
        },
        "infrastructure_services": {
            "security-service": {
                "port": 8010,
                "url": health["services"].get("security-service", {}).get("url", ""),
                "status": health["services"].get("security-service", {}).get("status", "unknown"),
                "description": "Authentication, encryption, and access control",
            },
            "notification-service": {
                "port": 8011,
                "url": health["services"].get("notification-service", {}).get("url", ""),
                "status": health["services"]
                .get("notification-service", {})
                .get("status", "unknown"),
                "description": "Email, SMS, and push notifications",
            },
        },
        "ai_engine": {
            "ollama": {
                "port": 11434,
                "url": health["services"].get("ollama", {}).get("url", ""),
                "status": health["services"].get("ollama", {}).get("status", "unknown"),
                "description": "Local Granite 4 AI model engine",
            }
        },
    }

    return {
        "total_services": len(service_discovery.services),
        "gateway": {"version": "0.1.0", "port": 8009},
        "service_registry": service_registry,
        "timestamp": datetime.now().isoformat(),
    }


# ============================================================================
# Model Management Endpoints
# ============================================================================

# Fallback models for when services are unavailable
FALLBACK_MODELS = [
    ModelInfo(
        id="vetta-granite-2b-gguf-v4",
        name="Granite 2B (Trained)",
        paramCount="2B",
        ramRequired="8-12 GB",
        downloadSize="1.2 GB",
        description="Custom trained on interview dataset",
        dataset="vetta-interviews",
        source="granite-interview-service",
    ),
    ModelInfo(
        id="llama3.2:1b",
        name="Llama 3.2 1B (Fallback)",
        paramCount="1B",
        ramRequired="4-6 GB",
        downloadSize="600 MB",
        description="Lightweight fallback model",
        dataset=None,
        source="ollama",
    ),
]


@app.get("/api/v1/models", response_model=ModelsResponse)
async def list_models() -> ModelsResponse:
    """
    List all available models from all sources.

    Merges models from granite-interview-service and ollama.
    Returns fallback if backends unavailable.
    """
    models: list[ModelInfo] = []

    if not service_discovery or not http_client:
        logger.warning("Service discovery or HTTP client not initialized")
        return ModelsResponse(models=FALLBACK_MODELS)

    # Try to get models from granite-interview-service
    try:
        url = await service_discovery.get_service_url("granite-interview-service")
        if url:
            response = await http_client.get(f"{url}/api/v1/models", timeout=5.0)
            if response.status_code == 200:
                granite_models = response.json().get("models", [])
                for model in granite_models:
                    models.append(
                        ModelInfo(
                            id=model.get("name", "unknown"),
                            name=model.get("display_name", model.get("name", "Unknown")),
                            paramCount=model.get("params", "unknown"),
                            ramRequired=model.get("memory", "unknown"),
                            downloadSize=model.get("size", "unknown"),
                            description=model.get("description", ""),
                            dataset=model.get("dataset", None),
                            source="granite-interview-service",
                        )
                    )
    except Exception as e:
        logger.warning(f"Could not fetch models from granite-interview-service: {e}")

    # Try to get models from ollama
    try:
        url = await service_discovery.get_service_url("ollama")
        if url:
            response = await http_client.get(f"{url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                ollama_models = response.json().get("models", [])
                for model in ollama_models[:3]:  # Limit to 3 models
                    models.append(
                        ModelInfo(
                            id=model.get("name", "unknown"),
                            name=model.get("name", "Unknown"),
                            paramCount="varies",
                            ramRequired="varies",
                            downloadSize=model.get("size", "unknown"),
                            description="Model from Ollama",
                            dataset=None,
                            source="ollama",
                        )
                    )
    except Exception as e:
        logger.warning(f"Could not fetch models from ollama: {e}")

    # Return fallback if no models found
    if not models:
        logger.info("Returning fallback models")
        return ModelsResponse(models=FALLBACK_MODELS)

    return ModelsResponse(models=models)


@app.post("/api/v1/models/select")
async def select_model(model_id: str) -> dict:
    """
    Select a specific model for interviews.

    Validates model exists in available models.
    """
    models_response = await list_models()
    available_ids = [m.id for m in models_response.models]

    if model_id not in available_ids:
        raise HTTPException(status_code=400, detail=f"Model {model_id} not found")

    return {"selected": model_id, "timestamp": datetime.now().isoformat()}


# =========================================================================
# Voice Service Endpoints (optional)
# =========================================================================


@app.post("/api/v1/voice/synthesize")
async def synthesize_speech(payload: dict) -> dict:
    """Proxy text-to-speech to voice-service when enabled."""
    if not settings.enable_voice:
        raise HTTPException(status_code=503, detail="Voice service disabled")

    if not service_discovery or not http_client:
        raise HTTPException(status_code=503, detail="Service discovery not initialized")

    url = await service_discovery.get_service_url("voice-service")
    if not url:
        raise HTTPException(status_code=503, detail="Voice service unavailable")

    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    try:
        response = await http_client.post(
            f"{url}/voice/tts",
            json={"text": text, "voice": payload.get("voice", "en-US-Neural2-C")},
        )
        return response.json()
    except Exception as e:
        logger.warning(f"Voice synthesis failed: {e}")
        raise HTTPException(status_code=502, detail="Voice synthesis failed")


@app.post("/api/v1/voice/transcribe")
async def transcribe_speech(payload: dict) -> dict:
    """Proxy speech-to-text transcription to voice-service when enabled."""
    if not settings.enable_voice:
        raise HTTPException(status_code=503, detail="Voice service disabled")

    if not service_discovery or not http_client:
        raise HTTPException(status_code=503, detail="Service discovery not initialized")

    url = await service_discovery.get_service_url("voice-service")
    if not url:
        raise HTTPException(status_code=503, detail="Voice service unavailable")

    # Forward the audio file or data to voice service
    # The payload should contain either audio_url or audio_base64
    if not payload.get("audio_url") and not payload.get("audio_base64"):
        raise HTTPException(status_code=400, detail="Either audio_url or audio_base64 is required")

    try:
        response = await http_client.post(
            f"{url}/voice/stt",
            json=payload,
        )
        return response.json()
    except Exception as e:
        logger.warning(f"Speech transcription failed: {e}")
        raise HTTPException(status_code=502, detail="Speech transcription failed")


# =========================================================================
# Scout Service Endpoints
# =========================================================================


@app.post("/api/v1/scout/search")
async def scout_search(payload: dict) -> dict:
    """Proxy candidate search to scout-service.

    Searches GitHub for developer candidates based on natural language query.
    Returns list of candidates with contact information and LinkedIn enrichment.
    """
    if not service_discovery or not http_client:
        raise HTTPException(status_code=503, detail="Service discovery not initialized")

    url = await service_discovery.get_service_url("scout-service")
    if not url:
        raise HTTPException(status_code=503, detail="Scout service unavailable")

    # Validate required fields
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="query is required")

    # Set defaults for optional fields
    search_payload = {
        "query": query,
        "location": payload.get("location", "Ireland"),
        "max_results": payload.get("max_results", 20),
        "use_ai_formatting": payload.get("use_ai_formatting", True),
    }

    try:
        response = await http_client.post(
            f"{url}/search",
            json=search_payload,
            timeout=30.0,  # Search can take longer
        )
        return response.json()
    except Exception as e:
        logger.warning(f"Scout search failed: {e}")
        raise HTTPException(status_code=502, detail="Scout search failed")


@app.get("/api/v1/scout/agents")
async def scout_agents() -> dict:
    """Get list of available scout agents for specialized searches.

    Returns registry of agent capabilities for talent sourcing.
    """
    if not service_discovery or not http_client:
        raise HTTPException(status_code=503, detail="Service discovery not initialized")

    url = await service_discovery.get_service_url("scout-service")
    if not url:
        raise HTTPException(status_code=503, detail="Scout service unavailable")

    try:
        response = await http_client.get(
            f"{url}/agents/registry",
            timeout=5.0,
        )
        return response.json()
    except Exception as e:
        logger.warning(f"Scout agents registry fetch failed: {e}")
        raise HTTPException(status_code=502, detail="Scout agents registry unavailable")


# =========================================================================
# Analytics Service Endpoints (optional)
# =========================================================================


@app.post("/api/v1/analytics/sentiment")
async def analyze_sentiment(payload: dict) -> dict:
    """Proxy sentiment analysis to analytics-service when enabled."""
    if not settings.enable_analytics:
        raise HTTPException(status_code=503, detail="Analytics service disabled")

    if not service_discovery or not http_client:
        raise HTTPException(status_code=503, detail="Service discovery not initialized")

    url = await service_discovery.get_service_url("analytics-service")
    if not url:
        raise HTTPException(status_code=503, detail="Analytics service unavailable")

    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    try:
        request_payload = {"text": text}
        if "context" in payload:
            request_payload["context"] = payload["context"]

        response = await http_client.post(f"{url}/api/v1/analyze/sentiment", json=request_payload)
        return response.json()
    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=502, detail="Sentiment analysis failed")


# =========================================================================
# Agents Endpoints (optional)
# =========================================================================


@app.post("/api/v1/agents/execute")
async def execute_agent(payload: dict) -> dict:
    """Proxy agent execution to agents-service when enabled."""
    if not settings.enable_agents or not settings.agents_url:
        raise HTTPException(status_code=503, detail="Agents service disabled")

    if not service_discovery or not http_client:
        raise HTTPException(status_code=503, detail="Service discovery not initialized")

    url = await service_discovery.get_service_url("agents-service")
    if not url:
        raise HTTPException(status_code=503, detail="Agents service unavailable")

    action = payload.get("action", "start")

    try:
        if action == "start":
            candidate_id = payload.get("candidate_id")
            if not candidate_id:
                raise HTTPException(status_code=400, detail="candidate_id is required for start")
            response = await http_client.post(
                f"{url}/interviews/start",
                params={"candidate_id": candidate_id},
            )
        elif action == "answer":
            interview_id = payload.get("interview_id")
            answer = payload.get("answer")
            if not interview_id or answer is None:
                raise HTTPException(
                    status_code=400, detail="interview_id and answer are required for answer"
                )
            response = await http_client.post(
                f"{url}/interviews/{interview_id}/answer",
                params={"answer": answer},
            )
        elif action == "status":
            interview_id = payload.get("interview_id")
            if not interview_id:
                raise HTTPException(status_code=400, detail="interview_id is required for status")
            response = await http_client.get(f"{url}/interviews/{interview_id}")
        elif action == "next_question":
            interview_id = payload.get("interview_id")
            if not interview_id:
                raise HTTPException(
                    status_code=400, detail="interview_id is required for next_question"
                )
            response = await http_client.get(f"{url}/interviews/{interview_id}/next-question")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported action: {action}")

        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Agent execution failed: {e}")
        raise HTTPException(status_code=502, detail="Agent execution failed")


# ============================================================================
# Interview Endpoints
# ============================================================================

# Interview prompt templates for fallback
INTERVIEW_PROMPTS = {
    "Software Engineer": {
        "system": """You are an experienced technical interviewer conducting a job interview for a Software Engineer position.

Your interview will consist of exactly {total_questions} questions covering core technical skills.

Guidelines:
- Introduce yourself as "OpenTalent Interviewer"
- Ask ONE question at a time and wait for response
- Be professional but friendly
- Number your questions (e.g., "Question 1:")
- After {total_questions} questions, thank the candidate and summarize

Start by saying: "Hello, I'm OpenTalent Interviewer. Question 1:" and then ask the first question.""",
        "questions": [
            "Tell me about a challenging technical problem you solved recently.",
            "How do you approach debugging a complex issue?",
            "What's your experience with system design?",
            "How do you stay updated with new technologies?",
            "Describe your approach to writing clean, maintainable code.",
        ],
    },
    "Product Manager": {
        "system": """You are an experienced interviewer conducting a job interview for a Product Manager position.

Your interview will consist of exactly {total_questions} questions covering product skills.

Guidelines:
- Introduce yourself as "OpenTalent Interviewer"
- Ask ONE question at a time
- Be professional but friendly
- Number your questions (e.g., "Question 1:")
- After {total_questions} questions, thank the candidate

Start by saying: "Hello, I'm OpenTalent Interviewer. Question 1:" and then ask the first question.""",
        "questions": [
            "Tell me about a product you launched and how you approached it.",
            "How do you prioritize features?",
            "How would you measure success for a new feature?",
            "Tell me about a time you had to make a difficult trade-off.",
            "How do you work with engineering and design teams?",
        ],
    },
    "Data Analyst": {
        "system": """You are an experienced interviewer conducting a job interview for a Data Analyst position.

Your interview will consist of exactly {total_questions} questions covering data analysis skills.

Guidelines:
- Introduce yourself as "OpenTalent Interviewer"
- Ask ONE question at a time
- Be professional but friendly
- Number your questions (e.g., "Question 1:")
- After {total_questions} questions, thank the candidate

Start by saying: "Hello, I'm OpenTalent Interviewer. Question 1:" and then ask the first question.""",
        "questions": [
            "Walk me through your approach to analyzing a dataset.",
            "What's your experience with SQL?",
            "How do you handle missing or bad data?",
            "Tell me about a dashboard or report you created.",
            "How do you communicate findings to non-technical stakeholders?",
        ],
    },
}


@app.post("/api/v1/interviews/start", response_model=InterviewSession)
async def start_interview(request: StartInterviewRequest) -> InterviewSession:
    """
    Start a new interview session.

    Routes to granite-interview-service if available, otherwise uses fallback templates.
    """
    if not http_client:
        raise HTTPException(status_code=503, detail="HTTP client not initialized")

    # Validate role
    if request.role not in INTERVIEW_PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {list(INTERVIEW_PROMPTS.keys())}",
        )

    # Try granite-interview-service first
    try:
        if service_discovery:
            url = await service_discovery.get_service_url("granite-interview-service")
            if url:
                response = await http_client.post(
                    f"{url}/api/v1/interviews/start",
                    json={
                        "role": request.role,
                        "model": request.model,
                        "total_questions": request.totalQuestions,
                    },
                    timeout=5.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    # Parse response and return as InterviewSession
                    messages = [
                        Message(
                            role="system",
                            content=INTERVIEW_PROMPTS[request.role]["system"].format(
                                total_questions=request.totalQuestions
                            ),
                        ),
                        Message(role="user", content="Please start the interview."),
                        Message(
                            role="assistant",
                            content=data.get(
                                "first_question",
                                f"Hello, I'm OpenTalent Interviewer. Question 1: {INTERVIEW_PROMPTS[request.role]['questions'][0]}",
                            ),
                        ),
                    ]

                    return InterviewSession(
                        config=InterviewConfig(
                            role=request.role,
                            model=request.model,
                            totalQuestions=request.totalQuestions,
                        ),
                        messages=messages,
                        currentQuestion=1,
                        isComplete=False,
                    )
    except Exception as e:
        logger.warning(f"Could not start interview via granite-interview-service: {e}")

    # Fallback: use template
    logger.info(f"Using fallback template for {request.role}")
    prompts = INTERVIEW_PROMPTS[request.role]

    messages = [
        Message(
            role="system",
            content=prompts["system"].format(total_questions=request.totalQuestions),
        ),
        Message(role="user", content="Please start the interview."),
        Message(
            role="assistant",
            content=f"Hello, I'm OpenTalent Interviewer. Question 1: {prompts['questions'][0]}",
        ),
    ]

    return InterviewSession(
        config=InterviewConfig(
            role=request.role,
            model=request.model,
            totalQuestions=request.totalQuestions,
        ),
        messages=messages,
        currentQuestion=1,
        isComplete=False,
    )


@app.post("/api/v1/interviews/respond", response_model=InterviewSession)
async def respond_to_interview(request: InterviewResponseRequest) -> InterviewSession:
    """
    Submit candidate response and get next question.

    Continues interview flow with next question or marks complete if all questions done.
    """
    if not request.session:
        raise HTTPException(status_code=400, detail="Session data required")

    session = request.session
    role = session.config.role
    total_questions = session.config.totalQuestions

    # Add user message
    session.messages.append(Message(role="user", content=request.message))

    # Try to get next question from granite-interview-service
    try:
        if service_discovery and http_client and session.currentQuestion < total_questions:
            url = await service_discovery.get_service_url("granite-interview-service")
            if url:
                response = await http_client.post(
                    f"{url}/api/v1/interviews/respond",
                    json={
                        "session_id": request.sessionId or "fallback",
                        "user_response": request.message,
                        "question_number": session.currentQuestion,
                    },
                    timeout=5.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    next_question = data.get(
                        "next_question",
                        f"Question {session.currentQuestion + 1}: Thank you for that response.",
                    )
                    session.messages.append(Message(role="assistant", content=next_question))
                    session.currentQuestion += 1

                    if session.currentQuestion > total_questions:
                        session.isComplete = True

                    return session
    except Exception as e:
        logger.warning(f"Could not get response from granite-interview-service: {e}")

    # Fallback: use template
    prompts = INTERVIEW_PROMPTS.get(role, INTERVIEW_PROMPTS["Software Engineer"])
    session.currentQuestion += 1

    if session.currentQuestion > total_questions:
        # Interview complete
        session.isComplete = True
        next_question = "Thank you for completing the interview. We appreciate your time!"
    else:
        # Get next templated question
        question_idx = min(session.currentQuestion - 1, len(prompts["questions"]) - 1)
        next_question = f"Question {session.currentQuestion}: {prompts['questions'][question_idx]}"

    session.messages.append(Message(role="assistant", content=next_question))

    return session


@app.post("/api/v1/interviews/summary")
async def get_interview_summary(session: InterviewSession) -> dict:
    """
    Get interview summary and assessment.

    Returns simple summary with question count and candidate info.
    """
    user_responses = [m for m in session.messages if m.role == "user"]
    response_count = len([r for r in user_responses if r.content != "Please start the interview."])

    return {
        "role": session.config.role,
        "questionsAsked": session.config.totalQuestions,
        "responsesGiven": response_count,
        "summary": f"""Interview Complete!

Role: {session.config.role}
Questions Asked: {session.config.totalQuestions}
Responses Provided: {response_count}

Thank you for participating in this OpenTalent interview.""",
        "timestamp": datetime.now().isoformat(),
    }


# ============================================================================
# Aggregate Endpoints
# ============================================================================


@app.get("/api/v1/dashboard")
async def get_dashboard() -> dict:
    """
    Get complete dashboard data in one request.

    Combines health, models, and system info for UI.
    """
    if not service_discovery:
        raise HTTPException(status_code=503, detail="Service discovery not initialized")

    health = await service_discovery.check_all_services()
    models = await list_models()

    return {
        "status": health["status"],
        "timestamp": datetime.now().isoformat(),
        "services": health["services"],
        "servicesSummary": health["summary"],
        "availableModels": [m.dict() for m in models.models],
        "gateway": {
            "version": "0.1.0",
            "port": settings.port,
        },
    }


# ============================================================================
# Root & Info Endpoints
# ============================================================================


@app.get("/")
async def root() -> dict:
    """Root endpoint with API info."""
    return {
        "service": "OpenTalent Desktop Integration Service",
        "version": "0.1.0",
        "description": "Unified API gateway for desktop app and microservices",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "models": "/api/v1/models",
            "interviews": "/api/v1/interviews/{action}",
            "scout_search": "/api/v1/scout/search",
            "scout_agents": "/api/v1/scout/agents",
            "voice_synthesize": "/api/v1/voice/synthesize",
            "voice_transcribe": "/api/v1/voice/transcribe",
            "dashboard": "/api/v1/dashboard",
            "docs": "/docs",
        },
    }


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
