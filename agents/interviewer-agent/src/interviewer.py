"""
Core interviewer logic for Vetta AI
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class Interviewer:
    """Core interviewer logic"""

    def __init__(self):
        self.question_templates = {
            "technical": [
                "Can you walk me through your experience with {technology}?",
                "How would you approach solving {problem_type} problems?",
                "What are the key considerations when working with {domain}?",
            ],
            "behavioral": [
                "Tell me about a time when you faced {challenge}.",
                "How do you handle {situation} in a team environment?",
                "Describe your approach to {process}.",
            ],
            "situational": [
                "If you encountered {scenario}, how would you handle it?",
                "How would you prioritize {competing_demands}?",
                "What would you do if {constraint}?",
            ],
        }

    def generate_question(self, candidate_profile: dict, interview_history: dict) -> str:
        """Generate next interview question based on context"""
        try:
            # Analyze candidate profile
            skills = candidate_profile.get("skills", [])
            experience = candidate_profile.get("experience_years", 0)
            job_requirements = candidate_profile.get("job_requirements", {})

            # Determine question type based on interview progress
            question_index = interview_history.get("current_index", 0)

            if question_index < 3:
                # Early questions: technical skills
                question_type = "technical"
                context = self._select_technical_context(skills, job_requirements)
            elif question_index < 6:
                # Mid questions: behavioral
                question_type = "behavioral"
                context = self._select_behavioral_context()
            else:
                # Later questions: situational
                question_type = "situational"
                context = self._select_situational_context()

            # Select template and fill
            templates = self.question_templates[question_type]
            template = templates[question_index % len(templates)]

            question = template.format(**context)

            logger.info("Generated question", type=question_type, index=question_index)
            return question

        except Exception as e:
            logger.error("Error generating question", error=str(e))
            return "Can you tell me about your relevant experience for this position?"

    def evaluate_response(self, question: str, response: str, context: dict) -> dict[str, Any]:
        """Evaluate candidate response"""
        try:
            # Basic evaluation criteria
            evaluation = {
                "score": 7.0,  # Default good score
                "feedback": "Clear and relevant response",
                "strengths": ["Communication skills", "Technical knowledge"],
                "weaknesses": [],
                "recommendations": ["Consider providing more specific examples"],
            }

            # Analyze response length
            if len(response.split()) < 10:
                evaluation["score"] -= 1.0
                evaluation["weaknesses"].append("Response too brief")

            # Check for technical terms if technical question
            if "technical" in question.lower() and not any(
                term in response.lower()
                for term in ["code", "implementation", "solution", "approach"]
            ):
                evaluation["score"] -= 0.5
                evaluation["weaknesses"].append("Could be more technical")

            # Ensure score is within bounds
            evaluation["score"] = max(1.0, min(10.0, evaluation["score"]))

            logger.info("Evaluated response", score=evaluation["score"])
            return evaluation

        except Exception as e:
            logger.error("Error evaluating response", error=str(e))
            return {
                "score": 5.0,
                "feedback": "Response recorded",
                "strengths": [],
                "weaknesses": ["Evaluation error"],
                "recommendations": [],
            }

    def should_continue_interview(self, session_data: dict, evaluation: dict) -> bool:
        """Determine if interview should continue"""
        score = evaluation.get("score", 5.0)
        questions_asked = len(session_data.get("questions_asked", []))

        # Continue if score is decent and not too many questions
        return score >= 6.0 and questions_asked < 8

    def generate_final_assessment(self, interview_summary: dict) -> str:
        """Generate comprehensive final assessment"""
        try:
            scores = interview_summary.get("assessment_scores", {})
            responses = interview_summary.get("responses", [])

            avg_score = sum(scores.values()) / len(scores) if scores else 5.0

            assessment = f"""
Interview Assessment Summary:

Overall Score: {avg_score:.1f}/10

Key Findings:
- Technical Knowledge: {scores.get("technical", "N/A")}
- Communication: {scores.get("communication", "N/A")}
- Problem Solving: {scores.get("problem_solving", "N/A")}

Total Questions: {len(responses)}
Responses Analyzed: {len([r for r in responses if r.get("evaluation")])}

Recommendation: {"Strong candidate - proceed to next round" if avg_score >= 7.0 else "May need additional evaluation" if avg_score >= 5.0 else "Not recommended at this time"}
"""

            return assessment.strip()

        except Exception as e:
            logger.error("Error generating final assessment", error=str(e))
            return "Interview completed. Review individual responses for detailed assessment."

    def _select_technical_context(self, skills: list[str], job_requirements: dict) -> dict:
        """Select context for technical questions"""
        # Use job requirements or candidate skills
        technologies = job_requirements.get("technologies", skills)

        if technologies:
            technology = technologies[0] if technologies else "relevant technologies"
        else:
            technology = "relevant technologies"

        return {"technology": technology, "problem_type": "technical", "domain": technology}

    def _select_behavioral_context(self) -> dict:
        """Select context for behavioral questions"""
        return {
            "challenge": "a difficult technical problem",
            "situation": "conflicting priorities",
            "process": "code review",
        }

    def _select_situational_context(self) -> dict:
        """Select context for situational questions"""
        return {
            "scenario": "a production system outage",
            "competing_demands": "multiple urgent tasks",
            "constraint": "a tight deadline",
        }
