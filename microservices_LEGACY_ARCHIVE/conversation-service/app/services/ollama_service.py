"""
Legacy Ollama Service - Now uses Modular LLM Service

This service maintains backward compatibility while using the new modular LLM service.
For new implementations, use modular_llm_service directly.
"""

import logging
from typing import Dict, Any
from .modular_llm_service import modular_llm_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_questions_from_ollama(
    job_description: str, num_questions: int, difficulty: str
) -> Dict[str, Any]:
    """
    Generates interview questions based on a job description.
    Now uses the modular LLM service for better provider flexibility.

    This function maintains the same interface for backward compatibility.
    """
    import asyncio

    async def _generate():
        system_prompt = f"""
You are an expert recruitment assistant. Your task is to generate a list of exactly {num_questions} interview questions of {difficulty} difficulty based on the provided job description.

You MUST return the questions in a specific JSON format. The root of the JSON object must be a single key "questions", which contains a list of question objects.

Each question object in the list must have the following four keys:
1. "id": An integer representing the question number (starting from 1).
2. "text": A string containing the question itself.
3. "category": A string describing the question's category (e.g., 'technical', 'behavioral', 'situational').
4. "expected_duration_seconds": An integer representing the estimated time to answer in seconds (e.g., 60, 90, 120).

Do not include any other text, explanations, or markdown formatting in your response. Your entire output must be only the JSON object.
"""

        user_prompt = f"Here is the job description:\n\n{job_description}"

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        try:
            # Use the modular LLM service
            response = await modular_llm_service.generate_json(
                prompt=full_prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "questions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "text": {"type": "string"},
                                    "category": {"type": "string"},
                                    "expected_duration_seconds": {"type": "integer"},
                                },
                                "required": ["id", "text", "category", "expected_duration_seconds"],
                            },
                        }
                    },
                    "required": ["questions"],
                },
            )

            logger.info("Successfully received and parsed questions from modular LLM service.")
            return response

        except Exception as e:
            logger.error(f"Modular LLM service failed: {e}")
            # Fallback to mock responses
            from .modular_llm_service import LLMProvider, LLMConfig, MockProvider

            mock_config = LLMConfig(provider=LLMProvider.MOCK, model="mock")
            mock_provider = MockProvider(mock_config)

            # Generate mock questions (same logic as before)
            return _generate_mock_questions(job_description, num_questions, difficulty)

    # Run the async function
    try:
        return asyncio.run(_generate())
    except Exception as e:
        logger.error(f"Failed to generate questions: {e}")
        return _generate_mock_questions(job_description, num_questions, difficulty)


def _generate_mock_questions(
    job_description: str, num_questions: int, difficulty: str
) -> Dict[str, Any]:
    """
    Generate mock interview questions for development/testing when Ollama is not available.
    """
    logger.info(f"Generating {num_questions} mock questions (difficulty: {difficulty})")

    # Extract keywords from job description for relevant questions
    keywords = _extract_keywords(job_description.lower())

    # Question templates based on difficulty
    question_templates = {
        "easy": [
            "Can you tell me about your experience with {tech}?",
            "What attracted you to this role?",
            "How do you handle working under pressure?",
            "Can you describe a project you've worked on?",
            "What are your strengths and weaknesses?",
        ],
        "medium": [
            "How would you approach solving {problem} in {tech}?",
            "Can you explain the difference between {concept1} and {concept2}?",
            "How do you stay updated with industry trends?",
            "Describe a challenging technical problem you solved.",
            "How do you ensure code quality in your work?",
        ],
        "hard": [
            "Design a system to handle {scale} users with {tech}.",
            "How would you optimize {process} for performance?",
            "Explain the trade-offs in choosing {tech1} over {tech2}.",
            "How would you debug a complex issue in production?",
            "Design an architecture for {requirement} with scalability in mind.",
        ],
    }

    templates = question_templates.get(difficulty.lower(), question_templates["medium"])

    # Categories for questions
    categories = ["technical", "behavioral", "situational", "problem-solving", "leadership"]

    # Duration ranges based on difficulty
    duration_ranges = {"easy": (30, 60), "medium": (60, 120), "hard": (120, 180)}
    min_duration, max_duration = duration_ranges.get(difficulty.lower(), (60, 120))

    questions = []
    for i in range(num_questions):
        template = random.choice(templates)
        category = random.choice(categories)
        duration = random.randint(min_duration, max_duration)

        # Replace placeholders in template
        question_text = template
        if "{tech}" in template:
            tech = random.choice(keywords) if keywords else "relevant technologies"
            question_text = question_text.replace("{tech}", tech)
        if "{problem}" in template:
            problem = random.choice(["scalability", "performance", "security", "user experience"])
            question_text = question_text.replace("{problem}", problem)
        if "{concept1}" in template and "{concept2}" in template:
            concepts = ["REST", "GraphQL", "SQL", "NoSQL", "microservices", "monoliths"]
            random.shuffle(concepts)
            question_text = question_text.replace("{concept1}", concepts[0])
            question_text = question_text.replace("{concept2}", concepts[1])
        if "{scale}" in template:
            scale = random.choice(["1M", "10M", "100M"])
            question_text = question_text.replace("{scale}", scale)
        if "{process}" in template:
            process = random.choice(["database queries", "API responses", "file processing"])
            question_text = question_text.replace("{process}", process)
        if "{tech1}" in template and "{tech2}" in template:
            techs = ["React", "Vue", "Angular", "Python", "Node.js", "Java"]
            random.shuffle(techs)
            question_text = question_text.replace("{tech1}", techs[0])
            question_text = question_text.replace("{tech2}", techs[1])
        if "{requirement}" in template:
            requirement = random.choice(
                ["real-time chat", "video streaming", "e-commerce platform"]
            )
            question_text = question_text.replace("{requirement}", requirement)

        questions.append(
            {
                "id": i + 1,
                "text": question_text,
                "category": category,
                "expected_duration_seconds": duration,
            }
        )

    logger.info(f"Generated {len(questions)} mock questions")
    return {"questions": questions}


def _extract_keywords(job_description: str) -> list:
    """Extract relevant technical keywords from job description."""
    tech_keywords = [
        "python",
        "javascript",
        "react",
        "node.js",
        "django",
        "flask",
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "linux",
        "git",
        "api",
        "rest",
        "graphql",
        "machine learning",
        "ai",
        "data science",
        "frontend",
        "backend",
        "devops",
        "testing",
        "agile",
        "scrum",
    ]

    found_keywords = []
    desc_lower = job_description.lower()
    for keyword in tech_keywords:
        if keyword in desc_lower:
            found_keywords.append(keyword)

    return found_keywords[:5]  # Limit to 5 keywords
