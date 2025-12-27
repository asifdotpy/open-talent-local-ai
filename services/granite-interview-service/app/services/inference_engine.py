"""
Inference engine for interview intelligence using multiple AI models.

Provides high-level APIs for question generation, response analysis,
candidate assessment, and interview flow management.
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum

from ..config import settings
from ..models import model_registry

logger = logging.getLogger(__name__)

class InterviewPhase(Enum):
    """Phases of an interview."""
    INTRODUCTION = "introduction"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CULTURE_FIT = "culture_fit"
    CLOSING = "closing"

class QuestionType(Enum):
    """Types of interview questions."""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    CULTURE_FIT = "culture_fit"
    FOLLOW_UP = "follow_up"

@dataclass
class InterviewQuestion:
    """Represents an interview question."""
    question: str
    type: QuestionType
    phase: InterviewPhase
    difficulty: str  # easy, medium, hard
    skills_assessed: list[str]
    follow_up_questions: list[str] = None

@dataclass
class CandidateResponse:
    """Represents a candidate's response analysis."""
    response_text: str
    sentiment_score: float  # -1 to 1
    confidence_score: float  # 0 to 1
    key_points: list[str]
    strengths: list[str]
    weaknesses: list[str]
    technical_accuracy: float  # 0 to 1
    communication_score: float  # 0 to 1

@dataclass
class InterviewAssessment:
    """Overall interview assessment."""
    overall_score: float  # 0 to 100
    technical_score: float
    communication_score: float
    culture_fit_score: float
    recommendations: list[str]
    hire_recommendation: str  # "Strong Hire", "Hire", "Maybe", "No Hire"
    feedback_summary: str

class InferenceEngine:
    """Engine for AI-powered interview intelligence."""

    def __init__(self):
        self.default_model = settings.default_model

    def generate_interview_questions(
        self,
        job_description: str,
        candidate_experience: str,
        num_questions: int = 5,
        phase: InterviewPhase = InterviewPhase.TECHNICAL,
        model_name: str | None = None
    ) -> list[InterviewQuestion]:
        """Generate tailored interview questions based on a job description and candidate experience.

        Args:
            job_description: The text of the job description.
            candidate_experience: Description of the candidate's background.
            num_questions: Number of questions to generate.
            phase: The part of the interview to focus on.
            model_name: Optional specific model to use for generation.

        Returns:
            A list of InterviewQuestion objects.
        """

        model = model_name or self.default_model
        if model not in model_registry.get_loaded_models():
            raise ValueError(f"Model {model} not loaded")

        prompt = self._build_question_generation_prompt(
            job_description, candidate_experience, num_questions, phase
        )

        try:
            response = model_registry.generate_response(model, prompt)
            return self._parse_question_response(response, phase)
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return []

    def analyze_candidate_response(
        self,
        question: str,
        response: str,
        expected_skills: list[str],
        model_name: str | None = None
    ) -> CandidateResponse:
        """Analyze a candidate's response to a question."""

        model = model_name or self.default_model
        if model not in model_registry.get_loaded_models():
            raise ValueError(f"Model {model} not loaded")

        prompt = self._build_response_analysis_prompt(question, response, expected_skills)

        try:
            analysis_response = model_registry.generate_response(model, prompt)
            return self._parse_response_analysis(analysis_response, response)
        except Exception as e:
            logger.error(f"Error analyzing response: {e}")
            return CandidateResponse(
                response_text=response,
                sentiment_score=0.0,
                confidence_score=0.0,
                key_points=[],
                strengths=[],
                weaknesses=[],
                technical_accuracy=0.0,
                communication_score=0.0
            )

    def generate_follow_up_questions(
        self,
        original_question: str,
        candidate_response: str,
        num_questions: int = 2,
        model_name: str | None = None
    ) -> list[str]:
        """Generate relevant follow-up questions based on a candidate's previous response.

        Args:
            original_question: The question that was just answered.
            candidate_response: The text of the candidate's response.
            num_questions: Number of follow-ups to generate.
            model_name: Optional specific model to use.

        Returns:
            A list of follow-up question strings.
        """

        model = model_name or self.default_model
        if model not in model_registry.get_loaded_models():
            raise ValueError(f"Model {model} not loaded")

        prompt = self._build_follow_up_prompt(original_question, candidate_response, num_questions)

        try:
            response = model_registry.generate_response(model, prompt)
            return self._parse_follow_up_response(response)
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {e}")
            return []

    def assess_interview_overall(
        self,
        questions_and_responses: list[dict[str, str]],
        job_requirements: str,
        model_name: str | None = None
    ) -> InterviewAssessment:
        """Provide a comprehensive overall assessment of a candidate's entire interview performance.

        Args:
            questions_and_responses: A list of Q&A pairs from the interview.
            job_requirements: The skills and qualifications needed for the role.
            model_name: Optional specific model to use for assessment.

        Returns:
            An InterviewAssessment object summarizing scores and recommendations.
        """

        model = model_name or self.default_model
        if model not in model_registry.get_loaded_models():
            raise ValueError(f"Model {model} not loaded")

        prompt = self._build_assessment_prompt(questions_and_responses, job_requirements)

        try:
            response = model_registry.generate_response(model, prompt)
            return self._parse_assessment_response(response)
        except Exception as e:
            logger.error(f"Error generating assessment: {e}")
            return InterviewAssessment(
                overall_score=0.0,
                technical_score=0.0,
                communication_score=0.0,
                culture_fit_score=0.0,
                recommendations=[],
                hire_recommendation="Unable to assess",
                feedback_summary="Assessment failed due to technical error"
            )

    def _build_question_generation_prompt(
        self,
        job_description: str,
        candidate_experience: str,
        num_questions: int,
        phase: InterviewPhase
    ) -> str:
        """Construct the prompt for generating tailored interview questions.

        Args:
            job_description: The job description text.
            candidate_experience: Candidate background summary.
            num_questions: Target number of questions.
            phase: Current interview phase (Technical, Behavioral, etc.).

        Returns:
            The raw prompt string for the LLM.
        """

        return f"""You are an expert technical interviewer. Generate {num_questions} interview questions for the {phase.value} phase.

Job Description:
{job_description}

Candidate Experience:
{candidate_experience}

Requirements:
- Questions should be appropriate for the {phase.value} phase
- Include a mix of difficulty levels (easy, medium, hard)
- Focus on assessing key skills and competencies
- Questions should be behavioral and situational where appropriate

Format your response as a JSON array of objects with this structure:
[
  {{
    "question": "The interview question",
    "type": "technical|behavioral|situational|culture_fit",
    "difficulty": "easy|medium|hard",
    "skills_assessed": ["skill1", "skill2"],
    "follow_up_questions": ["follow_up1", "follow_up2"]
  }}
]

Generate exactly {num_questions} questions."""

    def _build_response_analysis_prompt(
        self,
        question: str,
        response: str,
        expected_skills: list[str]
    ) -> str:
        """Build prompt for response analysis."""

        return f"""Analyze this candidate's interview response as an expert interviewer.

Question: {question}

Candidate Response: {response}

Expected Skills: {', '.join(expected_skills)}

Provide a detailed analysis in the following JSON format:
{{
  "sentiment_score": -1.0 to 1.0 (negative to positive),
  "confidence_score": 0.0 to 1.0 (how confident/hesitant the response seems),
  "key_points": ["main point 1", "main point 2"],
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "technical_accuracy": 0.0 to 1.0 (accuracy of technical information),
  "communication_score": 0.0 to 1.0 (clarity and effectiveness of communication)
}}

Be objective and provide specific feedback."""

    def _build_follow_up_prompt(
        self,
        original_question: str,
        candidate_response: str,
        num_questions: int
    ) -> str:
        """Build prompt for follow-up questions."""

        return f"""Based on this interview question and candidate response, generate {num_questions} follow-up questions to dig deeper.

Original Question: {original_question}

Candidate Response: {candidate_response}

Requirements:
- Follow-up questions should explore areas that need clarification
- Questions should probe deeper into the candidate's experience
- Focus on specific examples or technical details
- Generate exactly {num_questions} questions

Format as a JSON array of strings:
["Follow-up question 1", "Follow-up question 2"]"""

    def _build_assessment_prompt(
        self,
        questions_and_responses: list[dict[str, str]],
        job_requirements: str
    ) -> str:
        """Build prompt for overall interview assessment."""

        qa_pairs = "\n\n".join([
            f"Q: {qa['question']}\nA: {qa['response']}"
            for qa in questions_and_responses
        ])

        return f"""Provide an overall assessment of this candidate's interview performance.

Job Requirements:
{job_requirements}

Interview Q&A:
{qa_pairs}

Provide assessment in this JSON format:
{{
  "overall_score": 0-100,
  "technical_score": 0-100,
  "communication_score": 0-100,
  "culture_fit_score": 0-100,
  "recommendations": ["recommendation 1", "recommendation 2"],
  "hire_recommendation": "Strong Hire|Hire|Maybe|No Hire",
  "feedback_summary": "Brief summary of candidate's performance"
}}

Be thorough and objective in your assessment."""

    def _parse_question_response(self, response: str, phase: InterviewPhase) -> list[InterviewQuestion]:
        """Parse question generation response."""
        try:
            questions_data = json.loads(response)
            questions = []

            for q_data in questions_data:
                question = InterviewQuestion(
                    question=q_data['question'],
                    type=QuestionType(q_data['type']),
                    phase=phase,
                    difficulty=q_data['difficulty'],
                    skills_assessed=q_data['skills_assessed'],
                    follow_up_questions=q_data.get('follow_up_questions', [])
                )
                questions.append(question)

            return questions
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing question response: {e}")
            return []

    def _parse_response_analysis(self, response: str, original_response: str) -> CandidateResponse:
        """Parse response analysis."""
        try:
            analysis = json.loads(response)
            return CandidateResponse(
                response_text=original_response,
                sentiment_score=float(analysis['sentiment_score']),
                confidence_score=float(analysis['confidence_score']),
                key_points=analysis['key_points'],
                strengths=analysis['strengths'],
                weaknesses=analysis['weaknesses'],
                technical_accuracy=float(analysis['technical_accuracy']),
                communication_score=float(analysis['communication_score'])
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing response analysis: {e}")
            return CandidateResponse(
                response_text=original_response,
                sentiment_score=0.0,
                confidence_score=0.0,
                key_points=[],
                strengths=[],
                weaknesses=[],
                technical_accuracy=0.0,
                communication_score=0.0
            )

    def _parse_follow_up_response(self, response: str) -> list[str]:
        """Parse follow-up questions response."""
        try:
            questions = json.loads(response)
            return questions if isinstance(questions, list) else []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing follow-up response: {e}")
            return []

    def _parse_assessment_response(self, response: str) -> InterviewAssessment:
        """Parse overall assessment response."""
        try:
            assessment = json.loads(response)
            return InterviewAssessment(
                overall_score=float(assessment['overall_score']),
                technical_score=float(assessment['technical_score']),
                communication_score=float(assessment['communication_score']),
                culture_fit_score=float(assessment['culture_fit_score']),
                recommendations=assessment['recommendations'],
                hire_recommendation=assessment['hire_recommendation'],
                feedback_summary=assessment['feedback_summary']
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing assessment response: {e}")
            return InterviewAssessment(
                overall_score=0.0,
                technical_score=0.0,
                communication_score=0.0,
                culture_fit_score=0.0,
                recommendations=[],
                hire_recommendation="Unable to assess",
                feedback_summary="Assessment parsing failed"
            )

# Global inference engine instance
inference_engine = InferenceEngine()
