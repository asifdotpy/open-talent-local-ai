"""Unit Tests for Natural Language Question Builder Service.

Tests Ollama Granite4 integration, template generation, and question pinning logic
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from services.question_builder import (
    InterviewQuestion,
    NaturalLanguagePrompt,
    NaturalLanguageQuestionBuilder,
    QuestionDifficulty,
    QuestionPriority,
    QuestionTemplate,
    QuestionType,
)


@pytest.fixture
def question_builder():
    """Create question builder instance for testing."""
    return NaturalLanguageQuestionBuilder(
        ollama_base_url="http://localhost:11434"
    )


@pytest.fixture
def sample_prompt():
    """Sample natural language prompt."""
    return NaturalLanguagePrompt(
        prompt="Create questions to assess system design skills for senior backend engineer",
        job_title="Senior Backend Engineer",
        required_skills=["Python", "System Design", "Microservices"],
        company_culture=["Remote-first", "Fast-paced"],
        num_questions=5,
        difficulty=QuestionDifficulty.SENIOR,
        interview_duration=45,
    )


@pytest.mark.asyncio
async def test_generate_questions_with_ollama(question_builder, sample_prompt):
    """Test question generation with Ollama API."""
    # Mock Ollama response
    mock_ollama_response = """[
  {
    "question_text": "Describe a distributed system you designed. What were the key architectural decisions?",
    "question_type": "system_design",
    "difficulty": "senior",
    "priority": "must_ask",
    "expected_duration": 10,
    "evaluation_criteria": [
      "Understanding of distributed systems concepts",
      "Trade-off analysis",
      "Real-world experience"
    ],
    "follow_up_questions": [
      "How did you handle failure scenarios?",
      "What monitoring did you implement?"
    ],
    "skill_assessed": ["System Design", "Architecture", "Distributed Systems"]
  },
  {
    "question_text": "How would you optimize a slow database query handling millions of records?",
    "question_type": "technical",
    "difficulty": "senior",
    "priority": "must_ask",
    "expected_duration": 8,
    "evaluation_criteria": [
      "Query optimization techniques",
      "Indexing strategies",
      "Performance profiling"
    ],
    "follow_up_questions": [
      "What tools would you use for profiling?"
    ],
    "skill_assessed": ["Database Optimization", "SQL", "Performance"]
  }
]"""

    # Mock Ollama API call
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": mock_ollama_response}
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post:
        questions = await question_builder.generate_questions(sample_prompt)

    # Verify API call was made correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[1]["json"]["model"] == "granite4:350m-h"

    # Assertions
    assert len(questions) == 2
    assert all(isinstance(q, InterviewQuestion) for q in questions)

    # Check first question
    assert "distributed system" in questions[0].question_text.lower()
    assert questions[0].question_type == QuestionType.SYSTEM_DESIGN
    assert questions[0].difficulty == QuestionDifficulty.SENIOR
    assert questions[0].priority == QuestionPriority.MUST_ASK
    assert len(questions[0].evaluation_criteria) > 0
    assert len(questions[0].skill_assessed) > 0

    # Check second question
    assert "database" in questions[1].question_text.lower()
    assert questions[1].question_type == QuestionType.TECHNICAL
    assert questions[1].priority == QuestionPriority.MUST_ASK


@pytest.mark.asyncio
async def test_generate_questions_fallback_to_template(question_builder, sample_prompt):
    """Test fallback to template when Ollama fails."""
    # Mock Ollama API failure
    with patch("httpx.AsyncClient.post", side_effect=Exception("API Error")):
        questions = await question_builder.generate_questions(sample_prompt)

    # Should fall back to template
    assert len(questions) > 0
    assert all(isinstance(q, InterviewQuestion) for q in questions)
    # Template questions should not be marked as AI-generated
    # (though in current implementation they are - could be improved)


def test_list_templates(question_builder):
    """Test listing available templates."""
    templates = question_builder.list_templates()

    assert len(templates) >= 3  # We have 3 general templates
    assert all(isinstance(t, QuestionTemplate) for t in templates)
    assert any(t.template_id == "backend-senior" for t in templates)
    assert any(t.template_id == "product-manager" for t in templates)
    assert any(t.template_id == "data-scientist" for t in templates)


def test_list_templates_filtered_by_role(question_builder):
    """Test listing templates filtered by job role."""
    # Filter for backend roles
    templates = question_builder.list_templates(job_role="Backend Engineer")

    assert len(templates) >= 1
    assert any("Backend" in t.template_name for t in templates)


def test_get_specific_template(question_builder):
    """Test retrieving a specific template."""
    template = question_builder.get_template("backend-senior")

    assert template is not None
    assert template.template_id == "backend-senior"
    assert template.template_name == "Backend Engineer - Senior Level"
    assert len(template.questions) > 0

    # Check template questions
    for question in template.questions:
        assert isinstance(question, InterviewQuestion)
        assert question.difficulty == QuestionDifficulty.SENIOR


def test_get_nonexistent_template(question_builder):
    """Test retrieving a template that doesn't exist."""
    template = question_builder.get_template("nonexistent-template")

    assert template is None


def test_pin_question(question_builder):
    """Test pinning a question (make it must-ask)."""
    question = InterviewQuestion(
        question_text="Sample question",
        question_type=QuestionType.TECHNICAL,
        difficulty=QuestionDifficulty.SENIOR,
        priority=QuestionPriority.NICE_TO_ASK,
        expected_duration=5,
        evaluation_criteria=["Test criteria"],
        skill_assessed=["Python"],
    )

    # Initially nice-to-ask
    assert question.priority == QuestionPriority.NICE_TO_ASK

    # Pin it
    pinned_question = question_builder.pin_question(question)

    assert pinned_question.priority == QuestionPriority.MUST_ASK


def test_unpin_question(question_builder):
    """Test unpinning a question (make it nice-to-ask)."""
    question = InterviewQuestion(
        question_text="Sample question",
        question_type=QuestionType.TECHNICAL,
        difficulty=QuestionDifficulty.SENIOR,
        priority=QuestionPriority.MUST_ASK,
        expected_duration=5,
        evaluation_criteria=["Test criteria"],
        skill_assessed=["Python"],
    )

    # Initially must-ask
    assert question.priority == QuestionPriority.MUST_ASK

    # Unpin it
    unpinned_question = question_builder.unpin_question(question)

    assert unpinned_question.priority == QuestionPriority.NICE_TO_ASK


def test_create_custom_template(question_builder):
    """Test creating a custom template."""
    questions = [
        InterviewQuestion(
            question_text="Custom question 1",
            question_type=QuestionType.BEHAVIORAL,
            difficulty=QuestionDifficulty.MID_LEVEL,
            priority=QuestionPriority.MUST_ASK,
            expected_duration=5,
            evaluation_criteria=["Criteria 1"],
            skill_assessed=["Leadership"],
        ),
        InterviewQuestion(
            question_text="Custom question 2",
            question_type=QuestionType.TECHNICAL,
            difficulty=QuestionDifficulty.MID_LEVEL,
            priority=QuestionPriority.NICE_TO_ASK,
            expected_duration=8,
            evaluation_criteria=["Criteria 2"],
            skill_assessed=["Python"],
        ),
    ]

    template = question_builder.create_custom_template(
        template_name="Custom Engineering Template",
        description="Custom questions for our engineering team",
        questions=questions,
        job_roles=["Software Engineer", "DevOps Engineer"],
        created_by="test-user-123",
        is_public=False,
    )

    assert template.template_id == "custom-engineering-template"
    assert template.template_name == "Custom Engineering Template"
    assert len(template.questions) == 2
    assert template.is_public is False
    assert template.created_by == "test-user-123"
    assert template.usage_count == 0


def test_backend_template_content(question_builder):
    """Test backend template has proper questions."""
    template = question_builder.get_template("backend-senior")

    assert len(template.questions) >= 2

    # Check system design question exists
    system_design_questions = [
        q for q in template.questions if q.question_type == QuestionType.SYSTEM_DESIGN
    ]
    assert len(system_design_questions) > 0

    # Check all questions are senior level
    assert all(q.difficulty == QuestionDifficulty.SENIOR for q in template.questions)

    # Check at least one must-ask question
    must_ask_questions = [q for q in template.questions if q.priority == QuestionPriority.MUST_ASK]
    assert len(must_ask_questions) > 0


def test_product_manager_template_content(question_builder):
    """Test product manager template has behavioral questions."""
    template = question_builder.get_template("product-manager")

    assert len(template.questions) >= 1

    # Check behavioral question exists
    behavioral_questions = [
        q for q in template.questions if q.question_type == QuestionType.BEHAVIORAL
    ]
    assert len(behavioral_questions) > 0

    # Check prioritization skill is assessed
    prioritization_questions = [
        q for q in template.questions if "Prioritization" in q.skill_assessed
    ]
    assert len(prioritization_questions) > 0


def test_data_scientist_template_content(question_builder):
    """Test data scientist template has ML questions."""
    template = question_builder.get_template("data-scientist")

    assert len(template.questions) >= 1

    # Check for ML/technical questions
    ml_questions = [
        q
        for q in template.questions
        if "Machine Learning" in q.skill_assessed or q.question_type == QuestionType.TECHNICAL
    ]
    assert len(ml_questions) > 0


@pytest.mark.asyncio
async def test_ollama_response_parsing(question_builder, sample_prompt):
    """Test parsing Ollama response (direct JSON, no markdown wrapping)."""
    # Mock Ollama response (direct JSON)
    mock_ollama_response = """[
  {
    "question_text": "Test question",
    "question_type": "technical",
    "difficulty": "senior",
    "priority": "must_ask",
    "expected_duration": 5,
    "evaluation_criteria": ["Criteria 1"],
    "follow_up_questions": [],
    "skill_assessed": ["Python"]
  }
]"""

    mock_response = MagicMock()
    mock_response.json.return_value = {"response": mock_ollama_response}
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        questions = await question_builder.generate_questions(sample_prompt)

    assert len(questions) == 1
    assert questions[0].question_text == "Test question"


def test_prompt_validation():
    """Test that prompts with invalid data are rejected."""
    # Test negative num_questions
    with pytest.raises(Exception):
        NaturalLanguagePrompt(
            prompt="Test prompt",
            job_title="Test Engineer",
            required_skills=["Python"],
            company_culture=["Remote"],
            num_questions=-1,
        )

    # Test excessive num_questions
    with pytest.raises(Exception):
        NaturalLanguagePrompt(
            prompt="Test prompt",
            job_title="Test Engineer",
            required_skills=["Python"],
            company_culture=["Remote"],
            num_questions=100,  # Max is 20
        )


def test_question_metadata():
    """Test that questions have proper metadata."""
    question = InterviewQuestion(
        question_text="Test question",
        question_type=QuestionType.TECHNICAL,
        difficulty=QuestionDifficulty.SENIOR,
        priority=QuestionPriority.MUST_ASK,
        expected_duration=5,
        evaluation_criteria=["Criteria 1"],
        skill_assessed=["Python"],
        ai_generated=True,
    )

    assert question.ai_generated is True
    assert isinstance(question.generated_at, datetime)
    assert question.expected_duration == 5
    assert len(question.evaluation_criteria) > 0
