from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.interview_models import (
    AdaptationResponse,
    AdaptiveQuestionRequest,
    ConversationResponse,
    ConversationStatus,
    FollowupRequest,
    FollowupResponse,
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
    InterviewAdaptationRequest,
    QuestionGenerationResponse,
    SendMessageRequest,
    StartConversationRequest,
    StartConversationResponse,
)
from app.services.conversation_service import conversation_service
from app.services.job_description_service import job_description_service
from app.services.ollama_service import generate_questions_from_ollama

router = APIRouter()

router = APIRouter()


@router.post("/conversation/generate-questions", response_model=GenerateQuestionsResponse)
async def generate_questions(request: GenerateQuestionsRequest):
    """Generates interview questions based on a job description by calling the Ollama service."""
    try:
        # Call the Ollama service with the data from the request
        generated_data = generate_questions_from_ollama(
            job_description=request.job_description,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
        )
        return generated_data
    except ValueError as e:
        # Catches issues with the AI service's response format (e.g., bad JSON)
        raise HTTPException(
            status_code=502,  # Bad Gateway
            detail=f"Error processing AI service response: {e}",
        )
    except ConnectionError as e:
        # Catches issues with connecting to the AI service
        raise HTTPException(
            status_code=503,  # Service Unavailable
            detail=f"AI service is unavailable or failed: {e}",
        )
    except Exception as e:
        # Catch-all for any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected internal error occurred: {e}")


@router.post("/conversation/start", response_model=StartConversationResponse)
async def start_conversation(request: StartConversationRequest):
    """Start a new real-time interview conversation session.
    Dynamically loads job description if project_id/job_id provided.
    """
    try:
        # If job_description not provided directly, try to load it
        job_description = request.job_description

        # Check if we should load job description from project service
        if not job_description or job_description == "default":
            # Try to extract job_id from session_id or use default
            job_id = request.session_id.split("-")[-1] if "-" in request.session_id else None

            # Fetch job description from service
            job_data = await job_description_service.get_job_description(job_id=job_id)
            job_description = job_description_service.build_job_description_text(job_data)

        # Fetch candidate profile if candidate_id available
        candidate_profile = request.candidate_profile
        if not candidate_profile and hasattr(request, "candidate_id"):
            candidate_profile = await job_description_service.get_candidate_profile(
                request.candidate_id
            )

        result = await conversation_service.start_conversation(
            session_id=request.session_id,
            job_description=job_description,
            candidate_profile=candidate_profile,
            interview_type=request.interview_type,
            tone=request.tone,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start conversation: {e}")


@router.post("/conversation/message", response_model=ConversationResponse)
async def send_message(request: SendMessageRequest):
    """Send a message to an active conversation and get an adaptive response."""
    try:
        response = await conversation_service.process_message(
            session_id=request.session_id,
            message=request.message,
            message_type=request.message_type,
            metadata=request.metadata,
        )

        if response is None:
            raise HTTPException(
                status_code=404, detail="No active conversation found for this session"
            )

        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {e}")


@router.get("/conversation/status/{session_id}", response_model=ConversationStatus)
async def get_conversation_status(session_id: str):
    """Get the status of an active conversation."""
    try:
        status = await conversation_service.get_conversation_status(session_id)

        if status is None:
            raise HTTPException(
                status_code=404, detail="No active conversation found for this session"
            )

        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation status: {e}")


@router.post("/conversation/end/{session_id}")
async def end_conversation(session_id: str):
    """End an active conversation session."""
    try:
        success = await conversation_service.end_conversation(session_id)

        if not success:
            raise HTTPException(
                status_code=404, detail="No active conversation found for this session"
            )

        return {"message": "Conversation ended successfully", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end conversation: {e}")


# --- New Adaptive Question Generation Endpoints ---
@router.post(
    "/api/v1/conversation/generate-adaptive-question", response_model=QuestionGenerationResponse
)
async def generate_adaptive_question(request: AdaptiveQuestionRequest):
    """Generate the next adaptive interview question based on context."""
    try:
        result = await conversation_service.generate_adaptive_question(
            room_id=request.room_id,
            session_id=request.session_id,
            previous_responses=request.previous_responses,
            expertise_level=request.expertise_level,
            job_requirements=request.job_requirements,
            question_number=request.question_number,
            interview_phase=request.interview_phase,
            bias_mitigation=request.bias_mitigation,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")


@router.post("/api/v1/conversation/generate-followup", response_model=FollowupResponse)
async def generate_followup_questions(request: FollowupRequest):
    """Generate follow-up questions based on response analysis."""
    try:
        result = await conversation_service.generate_followup_questions(
            response_text=request.response_text,
            question_context=request.question_context,
            sentiment=request.sentiment,
            quality=request.quality,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Followup generation failed: {str(e)}")


@router.post("/api/v1/conversation/adapt-interview", response_model=AdaptationResponse)
async def adapt_interview_strategy(request: InterviewAdaptationRequest):
    """Generate interview adaptation recommendations."""
    try:
        result = await conversation_service.adapt_interview_strategy(
            current_phase=request.current_phase,
            time_remaining_minutes=request.time_remaining_minutes,
            performance_indicators=request.performance_indicators,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview adaptation failed: {str(e)}")


# Persona Switching Endpoints
class SwitchPersonaRequest(BaseModel):
    persona: str  # "technical", "behavioral", "hr"


class SwitchPersonaResponse(BaseModel):
    success: bool
    previous_persona: str
    current_persona: str
    message: str


class GetCurrentPersonaResponse(BaseModel):
    current_persona: str
    available_personas: list[str]


@router.post("/api/v1/persona/switch", response_model=SwitchPersonaResponse)
async def switch_interviewer_persona(request: SwitchPersonaRequest):
    """Switch to a different interviewer persona."""
    try:
        from app.services.modular_llm_service import modular_llm_service

        # Map persona names to model names
        persona_models = {
            "technical": "technical-interviewer",
            "behavioral": "behavioral-interviewer",
            "hr": "hr-interviewer",
        }

        if request.persona not in persona_models:
            raise HTTPException(
                status_code=400, detail=f"Invalid persona. Available: {list(persona_models.keys())}"
            )

        previous_persona = modular_llm_service.get_current_persona()
        target_model = persona_models[request.persona]

        modular_llm_service.switch_persona(target_model)

        return SwitchPersonaResponse(
            success=True,
            previous_persona=previous_persona,
            current_persona=target_model,
            message=f"Successfully switched to {request.persona} interviewer persona",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Persona switch failed: {str(e)}")


@router.get("/api/v1/persona/current", response_model=GetCurrentPersonaResponse)
async def get_current_persona():
    """Get the currently active interviewer persona."""
    try:
        from app.services.modular_llm_service import modular_llm_service

        current = modular_llm_service.get_current_persona()
        available = ["technical-interviewer", "behavioral-interviewer", "hr-interviewer"]

        return GetCurrentPersonaResponse(current_persona=current, available_personas=available)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current persona: {str(e)}")
