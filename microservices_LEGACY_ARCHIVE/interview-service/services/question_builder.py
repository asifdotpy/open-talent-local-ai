"""OpenTalent - Natural Language Question Builder Service
Production-Ready - Multi-Model AI Question Generation with Ollama

Model Strategy:
- Primary: granite4:350m-h (configurable via QUESTION_BUILDER_MODEL)
- Fallback: smollm:135m (configurable via QUESTION_BUILDER_FALLBACK_MODEL)
- Advanced: Gemini API (configurable via QUESTION_BUILDER_ADVANCED_MODEL + GEMINI_API_KEY)
- Final Fallback: Pre-defined templates

Inspired by PeopleGPT's natural language question paradigm:
- 80%+ natural language usage over Boolean
- Conversational interface > Complex UI
- Smart defaults with customization options
- High-performance inference with Ollama SLM
- Template-based fallbacks for reliability

NOTE: Resume semantic search moved to separate Resume Analysis Service
      for better separation of concerns and scalability.
"""

import os
from datetime import datetime
from enum import Enum

import httpx
from pydantic import BaseModel, Field


class QuestionDifficulty(str, Enum):
    """Question difficulty levels"""

    JUNIOR = "junior"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"
    PRINCIPAL = "principal"
    EXECUTIVE = "executive"


class QuestionType(str, Enum):
    """Types of interview questions"""

    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    CULTURAL_FIT = "cultural_fit"
    PROBLEM_SOLVING = "problem_solving"
    LEADERSHIP = "leadership"
    SYSTEM_DESIGN = "system_design"


class QuestionPriority(str, Enum):
    """Question priority - inspired by PeopleGPT's pinned skills logic"""

    MUST_ASK = "must_ask"  # Pinned - AND logic
    NICE_TO_ASK = "nice_to_ask"  # Unpinned - OR logic


class InterviewQuestion(BaseModel):
    """Generated interview question with metadata"""

    question_text: str = Field(..., description="The actual question to ask")
    question_type: QuestionType = Field(..., description="Type of question")
    difficulty: QuestionDifficulty = Field(..., description="Difficulty level")
    priority: QuestionPriority = Field(
        default=QuestionPriority.NICE_TO_ASK, description="Must-ask vs nice-to-ask (pinned logic)"
    )
    expected_duration: int = Field(default=5, description="Expected answer duration in minutes")
    evaluation_criteria: list[str] = Field(default_factory=list, description="What to look for in the answer")
    follow_up_questions: list[str] = Field(default_factory=list, description="Suggested follow-up questions")
    skill_assessed: list[str] = Field(default_factory=list, description="Skills this question evaluates")
    ai_generated: bool = Field(default=True, description="Whether question was AI-generated")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When question was generated")


class NaturalLanguagePrompt(BaseModel):
    """Natural language input for question generation"""

    prompt: str = Field(..., description="Natural language description of what to assess")
    job_title: str | None = Field(default=None, description="Job title for context")
    required_skills: list[str] | None = Field(default=None, description="Required skills to assess")
    company_culture: list[str] | None = Field(default=None, description="Company culture values")
    num_questions: int = Field(default=5, description="Number of questions to generate", ge=1, le=20)
    difficulty: QuestionDifficulty = Field(default=QuestionDifficulty.MID_LEVEL, description="Target difficulty level")
    interview_duration: int = Field(default=45, description="Total interview duration in minutes")


class QuestionTemplate(BaseModel):
    """Reusable question template - inspired by PeopleGPT presets"""

    template_id: str = Field(..., description="Unique template identifier")
    template_name: str = Field(..., description="Human-readable template name")
    description: str = Field(..., description="What this template is for")
    job_roles: list[str] = Field(default_factory=list, description="Applicable job roles")
    questions: list[InterviewQuestion] = Field(default_factory=list, description="Pre-defined questions")
    is_public: bool = Field(default=True, description="Public template or organization-specific")
    created_by: str | None = Field(None, description="User who created this template")
    usage_count: int = Field(default=0, description="How many times this template has been used")


class NaturalLanguageQuestionBuilder:
    """Natural Language Question Builder Service with Ollama

    Inspired by PeopleGPT's conversational search paradigm:
    - Users describe what they want in plain English
    - AI generates structured questions with Ollama SLM inference
    - Smart defaults with pinning logic
    - Preset templates for common scenarios
    - Lightweight and production-ready (no vector database overhead)
    """

    def __init__(self, ollama_base_url: str | None = None):
        """Initialize the question builder with Ollama integration"""
        self.ollama_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        # Model selection with environment variables and fallback logic
        self.model_name = os.getenv("QUESTION_BUILDER_MODEL", "granite4:350m-h")  # Default: granite4
        self.fallback_model = os.getenv("QUESTION_BUILDER_FALLBACK_MODEL", "smollm:135m")  # Fallback: smollm
        self.advanced_model = os.getenv("QUESTION_BUILDER_ADVANCED_MODEL", "gemini")  # Advanced: Gemini

        # Get API keys
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        # Ollama client (REST API)
        self.client = httpx.AsyncClient(timeout=120.0)

        # Preset templates (General Presets - like PeopleGPT)
        self.general_templates = self._load_general_templates()

    def _load_general_templates(self) -> dict[str, QuestionTemplate]:
        """Load general preset templates
        Similar to PeopleGPT's "B2B Startups", "Fortune 50", etc.
        """
        return {
            "backend-senior": QuestionTemplate(
                template_id="backend-senior",
                template_name="Backend Engineer - Senior Level",
                description="Standard questions for senior backend engineering roles",
                job_roles=["Senior Backend Engineer", "Backend Lead", "Backend Architect"],
                questions=[
                    InterviewQuestion(
                        question_text="Describe a system you designed that handled 10M+ daily users. What architecture decisions did you make and why?",
                        question_type=QuestionType.SYSTEM_DESIGN,
                        difficulty=QuestionDifficulty.SENIOR,
                        priority=QuestionPriority.MUST_ASK,
                        expected_duration=10,
                        evaluation_criteria=[
                            "Understanding of scalability concepts",
                            "Trade-off analysis (CAP theorem, consistency vs availability)",
                            "Real-world experience with high-traffic systems",
                            "Monitoring and observability practices",
                        ],
                        skill_assessed=["System Design", "Scalability", "Architecture"],
                    ),
                    InterviewQuestion(
                        question_text="How would you design a real-time messaging service like Slack? Walk me through your approach from database selection to API design.",
                        question_type=QuestionType.SYSTEM_DESIGN,
                        difficulty=QuestionDifficulty.SENIOR,
                        priority=QuestionPriority.MUST_ASK,
                        expected_duration=15,
                        evaluation_criteria=[
                            "WebSocket vs polling considerations",
                            "Database choice (SQL vs NoSQL)",
                            "Message persistence strategy",
                            "Handling offline users and message delivery",
                        ],
                        follow_up_questions=[
                            "How would you handle message encryption?",
                            "What about file uploads and sharing?",
                            "How would you implement read receipts?",
                        ],
                        skill_assessed=["System Design", "Real-time Systems", "API Design"],
                    ),
                ],
                is_public=True,
                usage_count=0,
            ),
            "product-manager": QuestionTemplate(
                template_id="product-manager",
                template_name="Product Manager - B2B SaaS",
                description="Questions for product managers in B2B SaaS companies",
                job_roles=["Product Manager", "Senior PM", "Principal PM"],
                questions=[
                    InterviewQuestion(
                        question_text="Tell me about a time you had to prioritize features with limited engineering resources. How did you make the decision?",
                        question_type=QuestionType.BEHAVIORAL,
                        difficulty=QuestionDifficulty.MID_LEVEL,
                        priority=QuestionPriority.MUST_ASK,
                        expected_duration=8,
                        evaluation_criteria=[
                            "Framework for prioritization (RICE, MoSCoW, etc.)",
                            "Stakeholder management",
                            "Data-driven decision making",
                            "Communication with engineering",
                        ],
                        skill_assessed=[
                            "Prioritization",
                            "Stakeholder Management",
                            "Decision Making",
                        ],
                    )
                ],
                is_public=True,
                usage_count=0,
            ),
            "data-scientist": QuestionTemplate(
                template_id="data-scientist",
                template_name="Data Scientist - Machine Learning Focus",
                description="Technical questions for ML-focused data scientists",
                job_roles=["Data Scientist", "ML Engineer", "AI Engineer"],
                questions=[
                    InterviewQuestion(
                        question_text="Explain a machine learning model you built in production. What were the challenges with deployment and monitoring?",
                        question_type=QuestionType.TECHNICAL,
                        difficulty=QuestionDifficulty.SENIOR,
                        priority=QuestionPriority.MUST_ASK,
                        expected_duration=12,
                        evaluation_criteria=[
                            "Production ML experience",
                            "Model monitoring and drift detection",
                            "A/B testing and experimentation",
                            "MLOps practices",
                        ],
                        skill_assessed=["Machine Learning", "MLOps", "Production Systems"],
                    )
                ],
                is_public=True,
                usage_count=0,
            ),
        }

    async def generate_questions(self, prompt: NaturalLanguagePrompt) -> list[InterviewQuestion]:
        """Generate interview questions from natural language prompt using Ollama with fallback logic

        Model Priority (configurable via environment variables):
        1. Primary: QUESTION_BUILDER_MODEL (default: granite4:350m-h)
        2. Fallback: QUESTION_BUILDER_FALLBACK_MODEL (default: smollm:135m)
        3. Advanced: QUESTION_BUILDER_ADVANCED_MODEL (default: gemini) with GEMINI_API_KEY
        4. Template: Pre-defined question templates

        Inspired by PeopleGPT's natural language search:
        - User describes what they want in plain English
        - AI interprets intent and generates structured questions
        - No complex forms or configuration needed
        - High-performance Ollama SLM inference

        Args:
            prompt: Natural language description of interview needs

        Returns:
            List of generated interview questions
        """
        # Try primary model (Ollama)
        try:
            questions = await self._generate_with_ollama(prompt, self.model_name)
            return questions
        except Exception as e:
            print(f"Primary model ({self.model_name}) failed: {e}")

        # Try fallback model (Ollama)
        try:
            questions = await self._generate_with_ollama(prompt, self.fallback_model)
            return questions
        except Exception as e:
            print(f"Fallback model ({self.fallback_model}) failed: {e}")

        # Try advanced model (Gemini)
        try:
            questions = await self._generate_with_gemini(prompt)
            return questions
        except Exception as e:
            print(f"Advanced model ({self.advanced_model}) failed: {e}")

        # Final fallback to template-based generation
        print("All AI models failed. Falling back to templates.")
        return self._generate_from_template(prompt)

    async def _generate_with_ollama(self, prompt: NaturalLanguagePrompt, model_name: str) -> list[InterviewQuestion]:
        """Generate questions using Ollama with specified model"""
        response = await self.client.post(
            f"{self.ollama_base_url}/api/generate",
            json={
                "model": model_name,
                "prompt": self._build_job_description(prompt),
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.9, "num_predict": 2048},
            },
        )
        response.raise_for_status()
        result = response.json()

        # Parse Ollama response and create InterviewQuestion objects
        return self._parse_ollama_response(result, prompt)

    async def _generate_with_gemini(self, prompt: NaturalLanguagePrompt) -> list[InterviewQuestion]:
        """Generate questions using Google Gemini API"""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        import google.generativeai as genai

        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Build prompt for Gemini
        gemini_prompt = f"""You are an expert interview question generator. Generate exactly {prompt.num_questions} interview questions in JSON format.

Requirements:
- Output ONLY a JSON array, no other text
- Each question must have: question_text, question_type, difficulty, priority, expected_duration, evaluation_criteria, follow_up_questions, skill_assessed
- question_type must be one of: technical, behavioral, situational, cultural_fit, problem_solving, leadership, system_design
- difficulty must be one of: junior, mid_level, senior, principal, executive
- priority must be one of: must_ask, nice_to_ask
- Include at least 2 "must_ask" priority questions
- expected_duration in minutes (5-15)
- evaluation_criteria as array of strings
- follow_up_questions as array of strings
- skill_assessed as array of strings

Context:
Job Title: {prompt.job_title or "Software Engineer"}
Skills: {", ".join(prompt.required_skills) if prompt.required_skills else "General technical skills"}
Difficulty: {prompt.difficulty.value}
Duration: {prompt.interview_duration} minutes

Request: {prompt.prompt}

Output JSON array:"""

        # Generate with Gemini
        response = model.generate_content(gemini_prompt)

        # Parse Gemini response
        return self._parse_gemini_response(response.text, prompt)

    def _build_job_description(self, prompt: NaturalLanguagePrompt) -> str:
        """Build prompt for Ollama Granite4 model"""
        return f"""You are an expert interview question generator using the Granite4 enterprise model. Generate exactly {prompt.num_questions} interview questions in JSON format.

Requirements:
- Output ONLY a JSON array, no other text
- Each question must have: question_text, question_type, difficulty, priority, expected_duration, evaluation_criteria, follow_up_questions, skill_assessed
- question_type must be one of: technical, behavioral, situational, cultural_fit, problem_solving, leadership, system_design
- difficulty must be one of: junior, mid_level, senior, principal, executive
- priority must be one of: must_ask, nice_to_ask
- Include at least 2 "must_ask" priority questions
- expected_duration in minutes (5-15)
- evaluation_criteria as array of strings
- follow_up_questions as array of strings
- skill_assessed as array of strings

Context:
Job Title: {prompt.job_title or "Software Engineer"}
Skills: {", ".join(prompt.required_skills) if prompt.required_skills else "General technical skills"}
Difficulty: {prompt.difficulty.value}
Duration: {prompt.interview_duration} minutes

Request: {prompt.prompt}

Output JSON array:"""

    def _parse_ollama_response(self, response: dict, prompt: NaturalLanguagePrompt) -> list[InterviewQuestion]:
        """Parse Ollama response into InterviewQuestion objects"""
        import json
        import re

        try:
            # Extract content from Ollama response
            content = response.get("response", "")

            # Clean the content - remove control characters and fix common issues
            content = content.strip()

            # Handle malformed JSON from Ollama (common issue with Granite4)
            if content.startswith('["{') and content.endswith('"}]'):
                # Extract individual JSON objects
                json_objects = re.findall(r"\{[^}]*\}", content)
                if json_objects:
                    questions_data = []
                    for obj in json_objects:
                        try:
                            questions_data.append(json.loads(obj))
                        except:
                            continue
                else:
                    raise ValueError("Could not extract JSON objects")
            elif content.strip().startswith("[") or content.strip().startswith("{"):
                # Looks like JSON - try to extract just the JSON part
                json_start = content.find("[")
                json_end = content.rfind("]") + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    try:
                        questions_data = json.loads(json_content)
                    except json.JSONDecodeError:
                        # Try to find JSON in markdown code blocks
                        if "```json" in content:
                            json_start = content.find("```json") + 7
                            json_end = content.find("```", json_start)
                            if json_end > json_start:
                                content = content[json_start:json_end].strip()
                        elif "```" in content:
                            json_start = content.find("```") + 3
                            json_end = content.find("```", json_start)
                            if json_end > json_start:
                                content = content[json_start:json_end].strip()

                        questions_data = json.loads(content)
                else:
                    raise ValueError("Could not find valid JSON array")
            else:
                # Try to extract JSON from markdown code blocks
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    if json_end > json_start:
                        content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    if json_end > json_start:
                        content = content[json_start:json_end].strip()

                questions_data = json.loads(content)

            # Ensure we have a list
            if not isinstance(questions_data, list):
                questions_data = [questions_data]

            questions = []
            for q_data in questions_data:
                # Handle string duration values (e.g., "30 minutes" -> 30)
                duration = q_data.get("expected_duration", 5)
                if isinstance(duration, str):
                    # Extract number from string like "30 minutes"
                    match = re.search(r"\d+", duration)
                    duration = int(match.group()) if match else 5

                # Ensure duration is within reasonable bounds
                duration = max(1, min(30, duration))

                question = InterviewQuestion(
                    question_text=q_data["question_text"],
                    question_type=QuestionType(q_data["question_type"]),
                    difficulty=QuestionDifficulty(q_data["difficulty"]),
                    priority=QuestionPriority(q_data.get("priority", "nice_to_ask")),
                    expected_duration=duration,
                    evaluation_criteria=q_data.get("evaluation_criteria", []),
                    follow_up_questions=q_data.get("follow_up_questions", []),
                    skill_assessed=q_data.get("skill_assessed", []),
                    ai_generated=True,
                )
                questions.append(question)

            return questions

        except Exception as e:
            print(f"Error parsing Ollama response: {e}")
            print(f"Response content: {content[:500]}...")
            # Fallback to template
            return self._generate_from_template(prompt)

    def _parse_gemini_response(self, response_text: str, prompt: NaturalLanguagePrompt) -> list[InterviewQuestion]:
        """Parse Gemini API response into InterviewQuestion objects"""
        import json
        import re

        try:
            # Clean the response - Gemini might include markdown formatting
            content = response_text.strip()

            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                if json_end > json_start:
                    content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                if json_end > json_start:
                    content = content[json_start:json_end].strip()

            # Parse JSON
            questions_data = json.loads(content)

            # Ensure we have a list
            if not isinstance(questions_data, list):
                questions_data = [questions_data]

            questions = []
            for q_data in questions_data:
                # Handle string duration values
                duration = q_data.get("expected_duration", 5)
                if isinstance(duration, str):
                    match = re.search(r"\d+", duration)
                    duration = int(match.group()) if match else 5

                duration = max(1, min(30, duration))

                question = InterviewQuestion(
                    question_text=q_data["question_text"],
                    question_type=QuestionType(q_data["question_type"]),
                    difficulty=QuestionDifficulty(q_data["difficulty"]),
                    priority=QuestionPriority(q_data.get("priority", "nice_to_ask")),
                    expected_duration=duration,
                    evaluation_criteria=q_data.get("evaluation_criteria", []),
                    follow_up_questions=q_data.get("follow_up_questions", []),
                    skill_assessed=q_data.get("skill_assessed", []),
                    ai_generated=True,
                )
                questions.append(question)

            return questions

        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Response content: {response_text[:500]}...")
            # Fallback to template
            return self._generate_from_template(prompt)

    def _generate_from_template(self, prompt: NaturalLanguagePrompt) -> list[InterviewQuestion]:
        """Fallback: Generate questions from templates
        Used when GPT-4 API is unavailable or fails
        """
        # Try to match job title to template
        if prompt.job_title:
            job_lower = prompt.job_title.lower()

            if "backend" in job_lower or "server" in job_lower:
                template = self.general_templates["backend-senior"]
            elif "product" in job_lower:
                template = self.general_templates["product-manager"]
            elif "data" in job_lower or "ml" in job_lower or "machine learning" in job_lower:
                template = self.general_templates["data-scientist"]
            else:
                # Default to backend for prototype
                template = self.general_templates["backend-senior"]
        else:
            template = self.general_templates["backend-senior"]

        # Return template questions (limited to requested number)
        return template.questions[: prompt.num_questions]

    def get_template(self, template_id: str) -> QuestionTemplate | None:
        """Get a specific question template by ID"""
        return self.general_templates.get(template_id)

    def list_templates(self, job_role: str | None = None) -> list[QuestionTemplate]:
        """List available question templates

        Args:
            job_role: Filter templates by job role

        Returns:
            List of matching templates
        """
        templates = list(self.general_templates.values())

        if job_role:
            job_lower = job_role.lower()
            templates = [t for t in templates if any(job_lower in role.lower() for role in t.job_roles)]

        return templates

    def pin_question(self, question: InterviewQuestion) -> InterviewQuestion:
        """Pin a question (make it must-ask)
        Inspired by PeopleGPT's pinned skills logic
        """
        question.priority = QuestionPriority.MUST_ASK
        return question

    def unpin_question(self, question: InterviewQuestion) -> InterviewQuestion:
        """Unpin a question (make it nice-to-ask)
        Inspired by PeopleGPT's unpinned skills logic
        """
        question.priority = QuestionPriority.NICE_TO_ASK
        return question

    def create_custom_template(
        self,
        template_name: str,
        description: str,
        questions: list[InterviewQuestion],
        job_roles: list[str],
        created_by: str,
        is_public: bool = False,
    ) -> QuestionTemplate:
        """Create a custom question template
        Similar to PeopleGPT's organization presets

        Args:
            template_name: Name of the template
            description: What this template is for
            questions: List of questions in template
            job_roles: Applicable job roles
            created_by: User who created this
            is_public: Whether template is public or organization-specific

        Returns:
            Created QuestionTemplate
        """
        template_id = template_name.lower().replace(" ", "-")

        template = QuestionTemplate(
            template_id=template_id,
            template_name=template_name,
            description=description,
            job_roles=job_roles,
            questions=questions,
            is_public=is_public,
            created_by=created_by,
            usage_count=0,
        )

        return template


# Singleton instance
_question_builder: NaturalLanguageQuestionBuilder | None = None


def get_question_builder() -> NaturalLanguageQuestionBuilder:
    """Get or create singleton question builder instance"""
    global _question_builder
    if _question_builder is None:
        _question_builder = NaturalLanguageQuestionBuilder()
    return _question_builder
