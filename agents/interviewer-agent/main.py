"""
Vetta AI - Interviewer Agent
Conducts AI-driven avatar interviews with candidates.

This agent manages the complete interview workflow:
- Starts interviews based on candidate profiles
- Generates contextual questions using LLM
- Evaluates candidate responses in real-time
- Adapts questioning based on expertise level
- Coordinates with avatar and voice services
- Provides comprehensive assessment scores
"""

import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import structlog
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add shared modules to path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from message_bus import MessageBus, Topics
from models import (
    AgentMessage,
    CandidateProfile,
    InterviewResult,
    InterviewSession,
    MessageType,
)
from service_clients import (
    AvatarServiceClient,
    CandidateServiceClient,
    ConversationServiceClient,
    VoiceServiceClient,
)

from config import Config

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global variables for lifespan
message_bus: MessageBus | None = None
config: Config | None = None
genkit_client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global message_bus, config, genkit_client

    # Startup
    config = Config()
    message_bus = MessageBus()
    genkit_client = httpx.AsyncClient(base_url=config.genkit_service_url, timeout=30.0)

    # Connect to Redis
    await message_bus.connect()

    # Subscribe to relevant topics
    await message_bus.subscribe(Topics.CANDIDATE_EVENTS, handle_candidate_event)
    await message_bus.subscribe(Topics.INTERVIEW_EVENTS, handle_interview_event)

    logger.info("Vetta AI Interviewer Agent started", port=config.interviewer_port)

    yield

    # Shutdown
    if genkit_client:
        await genkit_client.aclose()
    if message_bus:
        await message_bus.disconnect()
    logger.info("Vetta AI Interviewer Agent stopped")


# Initialize FastAPI app
app = FastAPI(
    title="Vetta AI - Interviewer Agent",
    description="""
    AI-driven avatar interview conductor for OpenTalent Platform.

    **Vetta AI** manages the complete interview workflow:
    - Starts interviews based on candidate profiles
    - Generates contextual questions using LLM
    - Evaluates candidate responses in real-time
    - Adapts questioning based on expertise level
    - Coordinates with avatar and voice services
    - Provides comprehensive assessment scores

    **API Documentation:**
    - Interactive Swagger UI: `/docs`
    - Alternative docs URL: `/doc`
    - ReDoc documentation: `/redoc`
    - OpenAPI schema: `/openapi.json`
    - API endpoints summary: `/api-docs`

    **Integration:**
    - Genkit Service: AI question generation and response evaluation
    - Voice Service: Text-to-speech for questions
    - Avatar Service: Real-time lip-sync animation
    - Candidate Service: Profile and result storage
    - Redis Message Bus: Event-driven communication
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Get service information and API documentation links."""
    return {
        "service": "Vetta AI - Interviewer Agent",
        "version": "1.0.0",
        "description": "AI-driven avatar interview conductor for OpenTalent Platform",
        "documentation": {
            "swagger_ui": "/docs",
            "alternative": "/doc",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
            "api_summary": "/api-docs",
        },
        "endpoints": {
            "health": "/health",
            "start_interview": "POST /interviews/start",
            "get_interview": "GET /interviews/{interview_id}",
            "submit_answer": "POST /interviews/{interview_id}/answer",
            "next_question": "GET /interviews/{interview_id}/next-question",
        },
        "active_interviews": len(active_interviews),
    }


@app.get("/doc", include_in_schema=False)
async def doc_redirect():
    """Alternative redirect to API documentation."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/docs")


@app.get("/api-docs", include_in_schema=False)
async def api_docs_info():
    """Get API documentation information and available endpoints."""
    routes_info = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            route_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, "name", "unknown"),
            }
            routes_info.append(route_info)

    return {
        "service": "Vetta AI Interviewer Agent API",
        "version": "1.0.0",
        "description": "AI-driven avatar interview conductor with real-time assessment",
        "total_endpoints": len(routes_info),
        "documentation_urls": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "active_interviews": len(active_interviews),
        "routes": routes_info,
        "integration_services": [
            "Genkit Service (AI flows)",
            "Voice Service (TTS)",
            "Avatar Service (lip-sync)",
            "Candidate Service (profiles)",
            "Redis Message Bus (events)",
        ],
    }


# In-memory storage for active interviews (use Redis in production)
active_interviews: dict[str, InterviewSession] = {}

# Service clients
candidate_client = CandidateServiceClient()
conversation_client = ConversationServiceClient()
voice_client = VoiceServiceClient()
avatar_client = AvatarServiceClient()


async def call_genkit_flow(flow_name: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """Call a Genkit flow via HTTP"""
    try:
        response = await genkit_client.post(
            f"/{flow_name}", json=input_data, headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error("Error calling Genkit flow", flow=flow_name, error=str(e))
        raise


async def handle_candidate_event(message: AgentMessage):
    """Handle candidate-related events"""
    try:
        if message.message_type == MessageType.CANDIDATE_READY_FOR_INTERVIEW:
            candidate_data = message.payload
            candidate = CandidateProfile(**candidate_data)

            # Auto-start interview for high-priority candidates
            if candidate.priority_score and candidate.priority_score >= 8.0:
                await start_interview_background(candidate)

        logger.info("Processed candidate event", message_type=message.message_type)
    except Exception as e:
        logger.error("Error handling candidate event", error=str(e), exc_info=True)


async def handle_interview_event(message: AgentMessage):
    """Handle interview-related events"""
    try:
        logger.info("Processed interview event", message_type=message.message_type)
    except Exception as e:
        logger.error("Error handling interview event", error=str(e), exc_info=True)


async def start_interview_background(candidate: CandidateProfile):
    """Background task to start interview for candidate"""
    try:
        interview_id = f"interview_{candidate.id}_{int(datetime.now().timestamp())}"

        # Create interview session
        session = InterviewSession(
            id=interview_id,
            candidate_id=candidate.id,
            status="starting",
            questions_asked=[],
            responses=[],
            assessment_scores={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        active_interviews[interview_id] = session

        # Notify avatar service to prepare
        await avatar_client.prepare_interview(candidate.id, interview_id)

        # Notify voice service
        await voice_client.prepare_session(interview_id)

        # Start the interview
        session.status = "active"
        session.current_question_index = 0

        # Generate first question
        first_question = await generate_question(candidate, session)

        # Send question via voice service
        await voice_client.send_text(first_question, interview_id)

        # Publish interview started event
        await message_bus.publish(
            Topics.INTERVIEW_EVENTS,
            AgentMessage(
                source_agent="vetta-ai",
                message_type=MessageType.INTERVIEW_STARTED,
                payload={
                    "interview_id": interview_id,
                    "candidate_id": candidate.id,
                    "first_question": first_question,
                },
                correlation_id=candidate.id,
            ),
        )

        logger.info("Interview started", interview_id=interview_id, candidate_id=candidate.id)

    except Exception as e:
        logger.error(
            "Error starting interview", candidate_id=candidate.id, error=str(e), exc_info=True
        )


async def generate_question(candidate: CandidateProfile, session: InterviewSession) -> str:
    """Generate next interview question using Genkit flow"""
    try:
        question_data = await call_genkit_flow(
            "generateInterviewQuestion",
            {
                "candidateProfile": candidate.dict(),
                "questionIndex": session.current_question_index,
                "previousQuestions": session.questions_asked,
            },
        )

        question = question_data["question"]
        session.questions_asked.append(question)
        session.updated_at = datetime.now()

        return question

    except Exception as e:
        logger.error("Error generating question", error=str(e), exc_info=True)
        return "Can you tell me about your relevant experience for this position?"


async def evaluate_response(
    candidate: CandidateProfile, session: InterviewSession, question: str, response: str
) -> dict[str, Any]:
    """Evaluate candidate response using Genkit flow"""
    try:
        evaluation_data = await call_genkit_flow(
            "evaluateInterviewResponse",
            {
                "question": question,
                "response": response,
                "candidateProfile": candidate.dict(),
                "interviewHistory": [
                    {
                        "question": r["question"],
                        "response": r["response"],
                        "evaluation": r.get("evaluation", {}),
                    }
                    for r in session.responses[-3:]  # Last 3 responses
                ],
            },
        )

        # Store response
        session.responses.append(
            {
                "question": question,
                "response": response,
                "evaluation": evaluation_data,
                "timestamp": datetime.now(),
            }
        )

        session.updated_at = datetime.now()

        return evaluation_data

    except Exception as e:
        logger.error("Error evaluating response", error=str(e), exc_info=True)
        return {
            "score": 5.0,
            "feedback": "Response recorded",
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
        }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "vetta-ai",
        "active_interviews": len(active_interviews),
        "genkit_connected": genkit_client is not None,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/interviews/start")
async def start_interview(candidate_id: str, background_tasks: BackgroundTasks):
    """Start a new interview for a candidate"""
    try:
        # Get candidate profile
        candidate_data = await candidate_client.get_candidate(candidate_id)
        candidate = CandidateProfile(**candidate_data)

        # Start interview in background
        background_tasks.add_task(start_interview_background, candidate)

        return {
            "message": "Interview starting",
            "candidate_id": candidate_id,
            "status": "scheduled",
        }

    except Exception as e:
        logger.error(
            "Error starting interview", candidate_id=candidate_id, error=str(e), exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to start interview")


@app.get("/interviews/{interview_id}")
async def get_interview_status(interview_id: str):
    """Get interview status and details"""
    if interview_id not in active_interviews:
        raise HTTPException(status_code=404, detail="Interview not found")

    session = active_interviews[interview_id]

    return {
        "interview_id": interview_id,
        "candidate_id": session.candidate_id,
        "status": session.status,
        "current_question_index": session.current_question_index,
        "questions_asked": len(session.questions_asked),
        "responses": len(session.responses),
        "assessment_scores": session.assessment_scores,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }


@app.post("/interviews/{interview_id}/answer")
async def submit_answer(interview_id: str, answer: str, background_tasks: BackgroundTasks):
    """Submit candidate's answer to current question"""
    if interview_id not in active_interviews:
        raise HTTPException(status_code=404, detail="Interview not found")

    session = active_interviews[interview_id]

    try:
        # Get candidate profile
        candidate_data = await candidate_client.get_candidate(session.candidate_id)
        candidate = CandidateProfile(**candidate_data)

        # Get current question
        current_question = session.questions_asked[-1] if session.questions_asked else ""

        # Evaluate response
        evaluation = await evaluate_response(candidate, session, current_question, answer)

        # Update assessment scores
        session.assessment_scores.update(
            {f"question_{len(session.responses)}": evaluation["score"]}
        )

        # Check if interview should continue
        should_continue = await should_continue_interview(session, evaluation)

        if should_continue and session.current_question_index < 10:  # Max 10 questions
            # Generate next question
            session.current_question_index += 1
            next_question = await generate_question(candidate, session)

            # Send next question via voice
            await voice_client.send_text(next_question, interview_id)

            response = {
                "message": "Answer recorded, next question sent",
                "evaluation": evaluation,
                "next_question": next_question,
            }
        else:
            # End interview
            session.status = "completed"
            final_assessment = await generate_final_assessment(session, candidate)

            # Save results
            interview_result = InterviewResult(
                id=interview_id,
                candidate_id=session.candidate_id,
                overall_score=sum(session.assessment_scores.values())
                / len(session.assessment_scores)
                if session.assessment_scores
                else 0,
                question_responses=session.responses,
                assessment_scores=session.assessment_scores,
                final_assessment=final_assessment,
                completed_at=datetime.now(),
            )

            # Save to candidate service
            await candidate_client.save_interview_result(interview_result.dict())

            # Publish completion event
            await message_bus.publish(
                Topics.INTERVIEW_EVENTS,
                AgentMessage(
                    source_agent="vetta-ai",
                    message_type=MessageType.INTERVIEW_COMPLETED,
                    payload=interview_result.dict(),
                    correlation_id=session.candidate_id,
                ),
            )

            response = {
                "message": "Interview completed",
                "evaluation": evaluation,
                "final_assessment": final_assessment,
                "overall_score": interview_result.overall_score,
            }

        return response

    except Exception as e:
        logger.error(
            "Error processing answer", interview_id=interview_id, error=str(e), exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to process answer")


@app.get("/interviews/{interview_id}/next-question")
async def get_next_question(interview_id: str):
    """Get the next question for the interview"""
    if interview_id not in active_interviews:
        raise HTTPException(status_code=404, detail="Interview not found")

    session = active_interviews[interview_id]

    if not session.questions_asked:
        return {"question": "Interview not started yet"}

    return {"question": session.questions_asked[-1]}


async def should_continue_interview(session: InterviewSession, evaluation: dict) -> bool:
    """Determine if interview should continue based on evaluation"""
    score = evaluation.get("score", 5.0)

    # Continue if score is above threshold and not too many questions asked
    return score >= 6.0 and len(session.questions_asked) < 8


async def generate_final_assessment(session: InterviewSession, candidate: CandidateProfile) -> str:
    """Generate final assessment using Genkit flow"""
    try:
        assessment_data = await call_genkit_flow(
            "generateFinalAssessment",
            {
                "candidateProfile": candidate.dict(),
                "interviewSummary": {
                    "totalQuestions": len(session.questions_asked),
                    "responses": session.responses,
                    "averageScore": sum(session.assessment_scores.values())
                    / len(session.assessment_scores)
                    if session.assessment_scores
                    else 5.0,
                },
            },
        )

        return f"""
Final Assessment:
Score: {assessment_data["overallScore"]}/10
Summary: {assessment_data["summary"]}
Feedback: {assessment_data["detailedFeedback"]}
Recommendation: {assessment_data["hireRecommendation"]}
"""

    except Exception as e:
        logger.error("Error generating final assessment", error=str(e), exc_info=True)
        avg_score = (
            sum(session.assessment_scores.values()) / len(session.assessment_scores)
            if session.assessment_scores
            else 5.0
        )
        return f"Interview completed with average score of {avg_score:.1f}/10"


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=config.interviewer_port if config else 8080, reload=True
    )
