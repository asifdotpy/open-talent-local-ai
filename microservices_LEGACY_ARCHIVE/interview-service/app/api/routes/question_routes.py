"""OpenTalent - Natural Language Question Builder API Routes
FastAPI endpoints for question generation service

Inspired by PeopleGPT's conversational search paradigm
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.question_builder import (
    InterviewQuestion,
    NaturalLanguagePrompt,
    NaturalLanguageQuestionBuilder,
    QuestionTemplate,
    get_question_builder,
)

router = APIRouter(tags=["Question Generation"])


class QuestionGenerationResponse(BaseModel):
    """Response from question generation endpoint"""

    questions: list[InterviewQuestion]
    total_questions: int
    total_duration: int  # Total expected interview duration
    must_ask_count: int  # Number of pinned questions
    nice_to_ask_count: int  # Number of optional questions
    metadata: dict


class PinQuestionRequest(BaseModel):
    """Request to pin/unpin a question"""

    question_index: int
    pinned: bool


@router.post(
    "/generate",
    response_model=QuestionGenerationResponse,
    summary="Generate interview questions from natural language",
    description="""
    Generate interview questions using natural language description.

    Inspired by PeopleGPT's search paradigm:
    - Describe what you want to assess in plain English
    - AI generates structured, insightful questions
    - No complex forms or Boolean operators needed

    Example prompts:
    - "Create questions to assess system design skills for senior backend engineer"
    - "Generate behavioral questions for product manager role focusing on stakeholder management"
    - "I need technical questions for a Python developer with 3-5 years experience"
    """,
)
async def generate_questions(
    prompt: NaturalLanguagePrompt,
    builder: NaturalLanguageQuestionBuilder = Depends(get_question_builder),
) -> QuestionGenerationResponse:
    """Generate interview questions from natural language prompt

    Args:
        prompt: Natural language description of interview needs
        builder: Question builder service (injected)

    Returns:
        QuestionGenerationResponse with generated questions

    Raises:
        HTTPException: If question generation fails
    """
    try:
        questions = await builder.generate_questions(prompt)

        # Calculate metadata
        total_duration = sum(q.expected_duration for q in questions)
        must_ask_count = sum(1 for q in questions if q.priority.value == "must_ask")
        nice_to_ask_count = len(questions) - must_ask_count

        return QuestionGenerationResponse(
            questions=questions,
            total_questions=len(questions),
            total_duration=total_duration,
            must_ask_count=must_ask_count,
            nice_to_ask_count=nice_to_ask_count,
            metadata={
                "source": "gpt-4o" if questions[0].ai_generated else "template",
                "prompt_used": prompt.prompt,
                "difficulty": prompt.difficulty.value,
                "job_title": prompt.job_title,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")


@router.get(
    "/templates",
    response_model=list[QuestionTemplate],
    summary="List available question templates",
    description="""
    List pre-built question templates for common roles.

    Similar to PeopleGPT's general presets:
    - Backend Engineer - Senior Level
    - Product Manager - B2B SaaS
    - Data Scientist - ML Focus
    - Frontend Engineer - React Expert

    Templates provide a quick start for standard interviews.
    """,
)
async def list_templates(
    job_role: Optional[str] = None,
    builder: NaturalLanguageQuestionBuilder = Depends(get_question_builder),
) -> list[QuestionTemplate]:
    """List available question templates

    Args:
        job_role: Optional filter by job role
        builder: Question builder service (injected)

    Returns:
        List of QuestionTemplate objects
    """
    return builder.list_templates(job_role=job_role)


@router.get(
    "/templates/{template_id}",
    response_model=QuestionTemplate,
    summary="Get a specific question template",
    description="Retrieve a specific question template by ID",
)
async def get_template(
    template_id: str, builder: NaturalLanguageQuestionBuilder = Depends(get_question_builder)
) -> QuestionTemplate:
    """Get a specific question template

    Args:
        template_id: Template identifier
        builder: Question builder service (injected)

    Returns:
        QuestionTemplate object

    Raises:
        HTTPException: If template not found
    """
    template = builder.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return template


@router.post(
    "/templates/{template_id}/use",
    response_model=QuestionGenerationResponse,
    summary="Generate questions from a template",
    description="""
    Use a pre-built template to generate questions.

    This is faster than natural language generation and provides
    consistent, well-tested questions for common roles.
    """,
)
async def use_template(
    template_id: str,
    num_questions: Optional[int] = None,
    builder: NaturalLanguageQuestionBuilder = Depends(get_question_builder),
) -> QuestionGenerationResponse:
    """Generate questions from a template

    Args:
        template_id: Template to use
        num_questions: Optional limit on number of questions
        builder: Question builder service (injected)

    Returns:
        QuestionGenerationResponse with template questions

    Raises:
        HTTPException: If template not found
    """
    template = builder.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    questions = template.questions
    if num_questions:
        questions = questions[:num_questions]

    # Calculate metadata
    total_duration = sum(q.expected_duration for q in questions)
    must_ask_count = sum(1 for q in questions if q.priority.value == "must_ask")
    nice_to_ask_count = len(questions) - must_ask_count

    return QuestionGenerationResponse(
        questions=questions,
        total_questions=len(questions),
        total_duration=total_duration,
        must_ask_count=must_ask_count,
        nice_to_ask_count=nice_to_ask_count,
        metadata={
            "source": "template",
            "template_id": template_id,
            "template_name": template.template_name,
        },
    )


@router.post(
    "/templates",
    response_model=QuestionTemplate,
    summary="Create custom question template",
    description="""
    Create a custom question template for your organization.

    Similar to PeopleGPT's organization presets - save frequently used
    question sets for reuse across your team.
    """,
)
async def create_template(
    template_name: str,
    description: str,
    questions: list[InterviewQuestion],
    job_roles: list[str],
    created_by: str,
    is_public: bool = False,
    builder: NaturalLanguageQuestionBuilder = Depends(get_question_builder),
) -> QuestionTemplate:
    """Create a custom question template

    Args:
        template_name: Name of the template
        description: What this template is for
        questions: List of questions in template
        job_roles: Applicable job roles
        created_by: User who created this
        is_public: Whether template is public
        builder: Question builder service (injected)

    Returns:
        Created QuestionTemplate
    """
    try:
        template = builder.create_custom_template(
            template_name=template_name,
            description=description,
            questions=questions,
            job_roles=job_roles,
            created_by=created_by,
            is_public=is_public,
        )
        return template

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.get(
    "/health",
    summary="Health check for question generation service",
    description="Check if question generation service is operational",
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "question-generation",
        "features": ["natural_language_generation", "template_management", "question_pinning"],
    }
