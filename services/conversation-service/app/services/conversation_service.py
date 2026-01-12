import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any

import httpx

from app.core.constants import (
    CONVERSATION_TOPICS,
    INTERVIEW_PHASES,
    INTERVIEWER_SYSTEM_PROMPT,
    MOCK_GREETINGS,
    SENTIMENT_CONTEXT_TEMPLATE,
    TECH_KEYWORDS,
    USER_MESSAGE_TEMPLATE,
)

from .database_service import database_service
from .modular_sentiment_service import modular_sentiment_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
USE_MOCK = os.getenv("USE_MOCK_OLLAMA", "true").lower() == "true"
MODEL = os.getenv("OLLAMA_MODEL", "granite4:350m-h")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))
ENABLE_STREAMING = os.getenv("ENABLE_STREAMING_LLM", "true").lower() == "true"


class ConversationService:
    """Service for managing real-time interview conversations with adaptive questioning."""

    def __init__(self):
        self.active_conversations: dict[str, dict[str, Any]] = {}
        self.conversation_timeout = timedelta(minutes=60)  # Auto-cleanup after 1 hour
        self.ollama_client = httpx.AsyncClient(
            base_url=OLLAMA_HOST, timeout=httpx.Timeout(OLLAMA_TIMEOUT)
        )

    async def start_conversation(
        self,
        session_id: str,
        job_description: str,
        candidate_profile: dict[str, Any] | None = None,
        interview_type: str = "technical",
        tone: str = "professional",
    ) -> dict[str, Any]:
        """Initialize a new interview conversation session.

        Creates a unique conversation context, persists it to the database,
        and generates an initial greeting message for the candidate.

        Args:
            session_id: The interview session identifier.
            job_description: Structured job requirements or text description.
            candidate_profile: Optional dictionary containing candidate details.
            interview_type: The focus of the interview (e.g., 'technical', 'behavioral').
            tone: The desired conversational tone (e.g., 'professional', 'casual').

        Returns:
            A dictionary containing the new conversation_id and initial greeting.
        """
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"

        # Create conversation context
        context = {
            "conversation_id": conversation_id,
            "session_id": session_id,
            "job_description": job_description,
            "candidate_profile": candidate_profile or {},
            "interview_type": interview_type,
            "tone": tone,
            "status": "active",
            "messages": [],
            "current_topic": None,
            "question_count": 0,
            "start_time": datetime.now(),
            "last_activity": datetime.now(),
        }

        self.active_conversations[conversation_id] = context

        # Persist to database
        database_service.save_conversation(context)

        # Generate initial greeting
        initial_message = await self._generate_initial_message(context)

        logger.info(f"Started conversation {conversation_id} for session {session_id}")

        return {
            "conversation_id": conversation_id,
            "session_id": session_id,
            "initial_message": initial_message,
            "status": "started",
        }

    async def process_message(
        self,
        session_id: str,
        message: str,
        message_type: str = "transcript",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Process an incoming message from the candidate and generate an AI response.

        Updates the conversation history, performs sentiment analysis on candidate
        transcripts, and uses the LLM to generate an adaptive follow-up.

        Args:
            session_id: The interview session identifier.
            message: The content of the incoming message.
            message_type: Type of message ('transcript', 'user_input', 'system').
            metadata: Optional dictionary with additional message data.

        Returns:
            A dictionary containing the AI response and metadata, or None if session not found.
        """
        # Find conversation by session_id
        conversation = None
        for conv in self.active_conversations.values():
            if conv["session_id"] == session_id:
                conversation = conv
                break

        if not conversation:
            logger.warning(f"No active conversation found for session {session_id}")
            return None

        # Update conversation
        conversation["last_activity"] = datetime.now()
        conversation["messages"].append(
            {
                "type": message_type,
                "content": message,
                "timestamp": datetime.now(),
                "metadata": metadata or {},
            }
        )

        # Save message to database
        database_service.save_message(
            conversation_id=conversation["conversation_id"],
            message_type=message_type,
            content=message,
            speaker="candidate",
            confidence=metadata.get("confidence") if metadata else None,
            metadata=metadata,
        )

        # Perform sentiment analysis on candidate responses
        sentiment_result = None
        if message_type == "transcript" and message.strip():
            try:
                sentiment_result = await modular_sentiment_service.analyze_sentiment(message)
                logger.info(
                    f"Sentiment analysis: {sentiment_result.sentiment} (confidence: {sentiment_result.confidence:.2f})"
                )
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
                # Continue without sentiment analysis

        # Generate response based on message type
        if message_type == "transcript":
            response = await self._process_transcript(
                conversation, message, metadata, sentiment_result
            )
        elif message_type == "user_input":
            response = await self._process_user_input(conversation, message)
        else:
            response = await self._process_system_message(conversation, message)

        if response:
            conversation["messages"].append(
                {
                    "type": "response",
                    "content": response["response_text"],
                    "timestamp": datetime.now(),
                    "metadata": response.get("metadata", {}),
                }
            )

            # Save AI response to database
            database_service.save_message(
                conversation_id=conversation["conversation_id"],
                message_type="response",
                content=response["response_text"],
                speaker="ai",
                metadata=response.get("metadata"),
            )

            # Update conversation state in database
            database_service.save_conversation(conversation)

        return response

    async def get_conversation_status(self, session_id: str) -> dict[str, Any] | None:
        """Get the status of a conversation by session_id."""
        for conv in self.active_conversations.values():
            if conv["session_id"] == session_id:
                return {
                    "conversation_id": conv["conversation_id"],
                    "session_id": conv["session_id"],
                    "status": conv["status"],
                    "message_count": len(conv["messages"]),
                    "last_activity": conv["last_activity"],
                    "current_topic": conv["current_topic"],
                }

        return None

    async def end_conversation(self, session_id: str) -> bool:
        """End a conversation session."""
        for conv_id, conv in list(self.active_conversations.items()):
            if conv["session_id"] == session_id:
                conv["status"] = "completed"
                conv["end_time"] = datetime.now()

                # Persist final state to database
                database_service.save_conversation(conv)

                logger.info(f"Ended conversation {conv_id} for session {session_id}")
                return True

        return False

    async def _generate_initial_message(self, context: dict[str, Any]) -> str:
        """Generate the initial greeting message for the interview."""
        if USE_MOCK:
            return self._generate_mock_initial_message(context)

        # Real LLM implementation
        try:
            system_prompt = self._build_system_prompt(context)
            response = await self._call_ollama(
                system_prompt=system_prompt,
                user_message="Generate a warm, professional opening message to start the interview.",
                context=context,
            )
            return response
        except Exception as e:
            logger.error(f"Error generating initial message with LLM: {e}")
            # Fallback to default message
            return f"Hello! I'm excited to interview you for the {context['interview_type']} position. Let's begin with your background and experience."

    async def _process_transcript(
        self,
        conversation: dict[str, Any],
        transcript: str,
        metadata: dict[str, Any] | None = None,
        sentiment_result: Any | None = None,
    ) -> dict[str, Any]:
        """Process a speech transcript and generate an adaptive response."""
        if USE_MOCK:
            return self._generate_mock_transcript_response(
                conversation, transcript, metadata, sentiment_result
            )

        # Real LLM processing with adaptive questioning
        try:
            system_prompt = self._build_system_prompt(conversation)
            conversation_history = self._format_conversation_history(conversation)

            # Include sentiment context in the prompt if available
            sentiment_context = ""
            if sentiment_result:
                sentiment_context = SENTIMENT_CONTEXT_TEMPLATE.format(
                    sentiment=sentiment_result.sentiment,
                    confidence=sentiment_result.confidence,
                    scores=sentiment_result.scores,
                )

            user_message = USER_MESSAGE_TEMPLATE.format(
                transcript=transcript,
                sentiment_context=sentiment_context,
                conversation_history=conversation_history,
                current_topic=conversation.get("current_topic", "general"),
                question_count=conversation["question_count"],
            )

            response_text = await self._call_ollama(
                system_prompt=system_prompt, user_message=user_message, context=conversation
            )

            # Determine response type and topic
            response_type = self._classify_response_type(response_text)
            topic = self._determine_topic(transcript, response_text)

            conversation["current_topic"] = topic
            conversation["question_count"] += 1

            # Include sentiment metadata in response
            response_metadata = {
                "topic": topic,
                "question_number": conversation["question_count"],
                "confidence": 0.9,
                "llm_model": MODEL,
            }

            if sentiment_result:
                response_metadata["sentiment"] = {
                    "sentiment": sentiment_result.sentiment,
                    "confidence": sentiment_result.confidence,
                    "scores": sentiment_result.scores,
                    "model_used": sentiment_result.model_used,
                }

            return {
                "conversation_id": conversation["conversation_id"],
                "session_id": conversation["session_id"],
                "response_text": response_text,
                "response_type": response_type,
                "should_speak": True,
                "metadata": response_metadata,
            }

        except Exception as e:
            logger.error(f"Error processing transcript with LLM: {e}")
            # Fallback to mock response on error
            return self._generate_mock_transcript_response(conversation, transcript, metadata)

    async def _process_user_input(
        self, conversation: dict[str, Any], message: str
    ) -> dict[str, Any]:
        """Process direct user input (not from speech)."""
        return {
            "conversation_id": conversation["conversation_id"],
            "session_id": conversation["session_id"],
            "response_text": f"I understand you said: {message}. How does that relate to the role?",
            "response_type": "clarification",
            "should_speak": True,
        }

    async def _process_system_message(
        self, conversation: dict[str, Any], message: str
    ) -> dict[str, Any]:
        """Process system-level messages."""
        return {
            "conversation_id": conversation["conversation_id"],
            "session_id": conversation["session_id"],
            "response_text": "System message acknowledged.",
            "response_type": "acknowledgment",
            "should_speak": False,
        }

    def _generate_mock_initial_message(self, context: dict[str, Any]) -> str:
        """Generate a mock initial greeting."""
        greetings = [g.format(interview_type=context["interview_type"]) for g in MOCK_GREETINGS]
        return greetings[hash(context["session_id"]) % len(greetings)]

    def _generate_mock_transcript_response(
        self,
        conversation: dict[str, Any],
        transcript: str,
        metadata: dict[str, Any] | None = None,
        sentiment_result: Any | None = None,
    ) -> dict[str, Any]:
        """Generate mock responses based on transcript content."""
        transcript_lower = transcript.lower()
        conversation["question_count"] += 1

        # Simple keyword-based response logic
        if "experience" in transcript_lower or "worked" in transcript_lower:
            response_text = "That sounds like valuable experience! Can you walk me through a specific project where you applied these skills?"
            response_type = "question"
            topic = "project_details"

        elif "project" in transcript_lower or "built" in transcript_lower:
            response_text = "Interesting project! What were the biggest challenges you faced, and how did you overcome them?"
            response_type = "question"
            topic = "challenges"

        elif "challenge" in transcript_lower or "problem" in transcript_lower:
            response_text = "Problem-solving is key in our work. How do you typically approach complex technical issues?"
            response_type = "question"
            topic = "problem_solving"

        elif "team" in transcript_lower or "collaborate" in transcript_lower:
            response_text = "Team collaboration is essential. Can you give an example of how you've contributed to a team project?"
            response_type = "question"
            topic = "teamwork"

        elif len(conversation["messages"]) > 10:  # Long conversation
            response_text = "We've covered a lot of ground! Is there anything specific you'd like to discuss about the role or our company?"
            response_type = "question"
            topic = "wrap_up"

        else:
            # Default follow-up based on tech keywords
            tech_keywords = self._extract_tech_keywords(transcript)
            if tech_keywords:
                response_text = f"You mentioned {tech_keywords[0]}. Can you elaborate on your proficiency level and how you've used it professionally?"
                topic = "technical_depth"
            else:
                response_text = (
                    "That's helpful context. What motivated you to pursue this type of work?"
                )
                topic = "motivation"

            response_type = "question"

        conversation["current_topic"] = topic

        # Include sentiment metadata in response
        response_metadata = {
            "topic": topic,
            "question_number": conversation["question_count"],
            "confidence": 0.85,
        }

        if sentiment_result:
            response_metadata["sentiment"] = {
                "sentiment": sentiment_result.sentiment,
                "confidence": sentiment_result.confidence,
                "scores": sentiment_result.scores,
                "model_used": sentiment_result.model_used,
            }

        return {
            "conversation_id": conversation["conversation_id"],
            "session_id": conversation["session_id"],
            "response_text": response_text,
            "response_type": response_type,
            "should_speak": True,
            "metadata": response_metadata,
        }

    def _extract_tech_keywords(self, text: str) -> list[str]:
        """Extract technical keywords from text."""
        found = []
        text_lower = text.lower()
        for keyword in TECH_KEYWORDS:
            if keyword in text_lower:
                found.append(keyword)

        return found[:3]  # Return up to 3 keywords

    def _build_system_prompt(self, context: dict[str, Any]) -> str:
        """Build comprehensive system prompt for the LLM based on interview context."""
        job_desc = context.get("job_description", "software engineering position")
        interview_type = context.get("interview_type", "technical")
        tone = context.get("tone", "professional")
        question_count = context.get("question_count", 0)

        return INTERVIEWER_SYSTEM_PROMPT.format(
            interview_type=interview_type,
            job_description=job_desc,
            tone=tone,
            question_number=question_count + 1,
            interview_stage=self._get_interview_stage(question_count),
        )

    def _get_interview_stage(self, question_count: int) -> str:
        """Determine current interview stage based on question count."""
        if question_count == 0:
            return INTERVIEW_PHASES["introduction"]
        elif question_count < 3:
            return INTERVIEW_PHASES["early"]
        elif question_count < 6:
            return INTERVIEW_PHASES["middle"]
        elif question_count < 9:
            return INTERVIEW_PHASES["late"]
        else:
            return INTERVIEW_PHASES["closing"]

    def _format_conversation_history(self, conversation: dict[str, Any]) -> str:
        """Format recent conversation history for context."""
        messages = conversation.get("messages", [])
        history = []

        # Include last 4 exchanges for context
        for msg in messages[-8:]:
            if msg["type"] == "transcript":
                history.append(f"Candidate: {msg['content']}")
            elif msg["type"] == "response":
                history.append(f"Interviewer: {msg['content']}")

        return "\n".join(history) if history else "No prior conversation"

    def _classify_response_type(self, response_text: str) -> str:
        """Classify the type of response generated."""
        text_lower = response_text.lower()

        if "?" in response_text:
            return "question"
        elif any(word in text_lower for word in ["thank", "appreciate", "great", "excellent"]):
            return "feedback"
        elif any(word in text_lower for word in ["let's", "shall we", "moving on"]):
            return "transition"
        else:
            return "statement"

    def _determine_topic(self, transcript: str, response: str) -> str:
        """Determine conversation topic from transcript and response."""
        combined = (transcript + " " + response).lower()

        for topic, keywords in CONVERSATION_TOPICS.items():
            if any(keyword in combined for keyword in keywords):
                return topic

        return "general"

    async def _call_ollama(
        self, system_prompt: str, user_message: str, context: dict[str, Any]
    ) -> str:
        """Call Ollama API for LLM response with error handling."""
        try:
            if ENABLE_STREAMING:
                return await self._call_ollama_streaming(system_prompt, user_message, context)
            else:
                return await self._call_ollama_non_streaming(system_prompt, user_message, context)

        except httpx.TimeoutException:
            logger.error(f"Ollama API timeout after {OLLAMA_TIMEOUT}s")
            raise
        except httpx.RequestError as e:
            logger.error(f"Ollama API request error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}")
            raise

    async def _call_ollama_non_streaming(
        self, system_prompt: str, user_message: str, context: dict[str, Any]
    ) -> str:
        """Non-streaming Ollama API call."""
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 150,  # Keep responses concise
            },
        }

        logger.info(f"Calling Ollama API (non-streaming) with model {MODEL}")
        response = await self.ollama_client.post("/api/chat", json=payload)
        response.raise_for_status()

        result = response.json()
        return result["message"]["content"].strip()

    async def _call_ollama_streaming(
        self, system_prompt: str, user_message: str, context: dict[str, Any]
    ) -> str:
        """Streaming Ollama API call - collects full response."""
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": True,
            "options": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 150},
        }

        logger.info(f"Calling Ollama API (streaming) with model {MODEL}")
        full_response = []

        async with self.ollama_client.stream("POST", "/api/chat", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            content = chunk["message"]["content"]
                            full_response.append(content)

                            # Log progress for long responses
                            if len(full_response) % 10 == 0:
                                logger.debug(f"Streaming progress: {len(full_response)} chunks")
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse streaming chunk: {line}")
                        continue

        result = "".join(full_response).strip()
        logger.info(f"Streaming complete: {len(result)} characters")
        return result

    async def cleanup_expired_conversations(self):
        """Clean up conversations that have been inactive too long."""
        now = datetime.now()
        expired = []

        for conv_id, conv in self.active_conversations.items():
            if now - conv["last_activity"] > self.conversation_timeout:
                expired.append(conv_id)

        for conv_id in expired:
            del self.active_conversations[conv_id]
            logger.info(f"Cleaned up expired conversation {conv_id}")

    async def generate_adaptive_question(
        self,
        room_id: str,
        session_id: str,
        previous_responses: list[dict[str, Any]] = None,
        expertise_level: str = "intermediate",
        job_requirements: str = "",
        question_number: int = 1,
        interview_phase: str = "technical",
        bias_mitigation: bool = True,
    ) -> dict[str, Any]:
        """Generate the next adaptive interview question based on context."""
        if previous_responses is None:
            previous_responses = []
        try:
            # Generate question based on phase and expertise
            question_text = self._generate_question_for_phase(
                expertise_level, interview_phase, question_number
            )

            # Create question object
            from datetime import datetime

            question = {
                "id": f"q-{room_id}-{question_number}",
                "text": question_text,
                "order": question_number,
                "generated_at": datetime.now().isoformat(),
                "ai_metadata": {
                    "expertise_level": expertise_level,
                    "bias_score": 0.1,  # Placeholder
                    "sentiment_context": "neutral",
                    "difficulty": self._determine_difficulty(expertise_level),
                    "phase": interview_phase,
                },
            }

            return {
                "question": question,
                "question_number": question_number,
                "ai_metadata": question["ai_metadata"],
                "estimated_difficulty": question["ai_metadata"]["difficulty"],
                "bias_mitigation_applied": bias_mitigation,
            }
        except Exception as e:
            logger.error(f"Error generating adaptive question: {e}")
            raise

    async def generate_followup_questions(
        self,
        response_text: str,
        question_context: str,
        sentiment: dict[str, Any] = None,
        quality: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Generate follow-up questions based on response analysis."""
        if quality is None:
            quality = {}
        if sentiment is None:
            sentiment = {}
        try:
            questions = []

            # If response was too brief, ask for elaboration
            if quality.get("completeness", 0.5) < 0.6:
                questions.append(
                    {
                        "question": "Can you elaborate on that point with a specific example?",
                        "priority": 5,
                        "reasoning": "Response was brief and needs more detail",
                        "expected_outcome": "Better understanding of candidate's experience",
                    }
                )

            # If technical accuracy was low, probe deeper
            if quality.get("technical_accuracy", 0.5) < 0.6:
                questions.append(
                    {
                        "question": "Can you walk me through the technical details of how you would implement this?",
                        "priority": 4,
                        "reasoning": "Technical understanding needs clarification",
                        "expected_outcome": "Assessment of technical competence",
                    }
                )

            # If sentiment was negative, explore concerns
            if sentiment.get("polarity", 0) < -0.2:
                questions.append(
                    {
                        "question": "What challenges did you face with this approach, and how did you overcome them?",
                        "priority": 3,
                        "reasoning": "Negative sentiment indicates potential learning opportunity",
                        "expected_outcome": "Understanding of problem-solving approach",
                    }
                )

            # Always have a general follow-up
            questions.append(
                {
                    "question": "How does this experience relate to the requirements of this role?",
                    "priority": 2,
                    "reasoning": "Connect candidate experience to job requirements",
                    "expected_outcome": "Assessment of role fit",
                }
            )

            return {"questions": questions[:3]}
        except Exception as e:
            logger.error(f"Error generating followup questions: {e}")
            raise

    async def adapt_interview_strategy(
        self,
        current_phase: str,
        time_remaining_minutes: int,
        performance_indicators: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Generate interview adaptation recommendations."""
        if performance_indicators is None:
            performance_indicators = {}
        try:
            adaptations = {
                "question_difficulty": "medium",
                "focus_areas": ["technical_skills", "problem_solving"],
                "time_adjustments": {},
                "immediate_actions": [],
                "strategy_changes": [],
            }

            # Mock performance analysis (would come from analytics service)
            overall_score = performance_indicators.get("overall_score", 7.0)

            # Adjust difficulty based on performance
            if overall_score > 8:
                adaptations["question_difficulty"] = "advanced"
                adaptations["focus_areas"].append("leadership")
            elif overall_score < 6:
                adaptations["question_difficulty"] = "basic"
                adaptations["focus_areas"].append("fundamentals")

            # Time adjustments
            if time_remaining_minutes < 15 and overall_score > 7:
                adaptations["time_adjustments"]["early_termination"] = True
                adaptations["immediate_actions"].append(
                    "Consider concluding interview early - strong candidate"
                )
            elif time_remaining_minutes < 10:
                adaptations["immediate_actions"].append("Focus on key remaining questions")

            # Strategy changes based on sentiment
            sentiment_trend = performance_indicators.get("sentiment_trend", "neutral")
            if sentiment_trend == "negative":
                adaptations["strategy_changes"].append("Incorporate more positive reinforcement")
                adaptations["immediate_actions"].append("Address any concerns raised by candidate")

            return {"adaptations": adaptations, "recommendations": adaptations["immediate_actions"]}
        except Exception as e:
            logger.error(f"Error adapting interview strategy: {e}")
            raise

    def _generate_question_for_phase(
        self, expertise_level: str, phase: str, question_number: int
    ) -> str:
        """Generate a question appropriate for the interview phase and expertise level."""
        # Base questions by phase
        phase_questions = {
            "introduction": [
                "Can you tell me about your background and experience in software development?",
                "What initially drew you to programming and technology?",
                "Can you walk me through your typical development workflow?",
            ],
            "technical": [
                "Can you describe a challenging technical problem you've solved recently?",
                "How do you approach debugging and troubleshooting code issues?",
                "What are your thoughts on code quality and best practices?",
            ],
            "behavioral": [
                "Can you describe a situation where you had to work with a difficult team member?",
                "How do you handle tight deadlines and competing priorities?",
                "Tell me about a time when you received constructive criticism.",
            ],
            "closing": [
                "What are your career goals for the next few years?",
                "Do you have any questions about the role or our team?",
                "Is there anything else you'd like to share about your experience?",
            ],
        }

        # Adjust for expertise level
        if expertise_level == "beginner":
            # Simplify questions
            pass  # Use base questions
        elif expertise_level == "expert":
            # Make questions more advanced
            if phase == "technical":
                phase_questions[phase] = [
                    "Can you discuss your experience with system architecture and scalability?",
                    "How do you approach performance optimization in large-scale applications?",
                    "What are your thoughts on emerging technologies and their impact on software development?",
                ]

        # Get questions for phase
        questions = phase_questions.get(phase, phase_questions["technical"])

        # Return question based on number (cycle through available questions)
        return questions[(question_number - 1) % len(questions)]

    def _determine_difficulty(self, expertise_level: str) -> str:
        """Determine question difficulty based on expertise level."""
        difficulty_map = {
            "beginner": "basic",
            "intermediate": "medium",
            "advanced": "advanced",
            "expert": "advanced",
        }
        return difficulty_map.get(expertise_level, "medium")

    async def close(self):
        """Cleanup resources on shutdown."""
        await self.ollama_client.aclose()


# Global conversation service instance
conversation_service = ConversationService()
