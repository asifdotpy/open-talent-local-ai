"""Constants for the Conversation Service.

Centralizes configuration, magic values, and static data used across the service.
"""

# Technical Keywords for Extraction
TECH_KEYWORDS = [
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
]

# Conversation Topics and Associated Keywords
CONVERSATION_TOPICS = {
    "experience": ["experience", "worked", "years", "background"],
    "projects": ["project", "built", "developed", "created"],
    "technical": ["technical", "code", "algorithm", "design", "architecture"],
    "challenges": ["challenge", "problem", "difficult", "overcome"],
    "teamwork": ["team", "collaborate", "communication", "leadership"],
    "motivation": ["why", "motivated", "interested", "passion"],
    "wrap_up": ["questions", "anything else", "conclude", "final"],
}

# Interview Phases
INTERVIEW_PHASES = {
    "introduction": "Opening - Build rapport, understand background",
    "early": "Early - Explore recent experience and skills",
    "middle": "Middle - Deep dive into technical abilities and projects",
    "late": "Late - Assess problem-solving and team collaboration",
    "closing": "Closing - Wrap up, invite candidate questions",
}

# Mock Greetings
MOCK_GREETINGS = [
    "Hello! Welcome to your {interview_type} interview. I'm here to learn about your background and experience.",
    "Hi there! Thanks for joining this {interview_type} interview. Let's start with your professional journey.",
    "Good day! I'm looking forward to our {interview_type} conversation. Could you begin by telling me about yourself?",
]

# System Prompts
INTERVIEWER_SYSTEM_PROMPT = """You are an expert technical interviewer conducting a {interview_type} interview.

Interview Context:
- Position: {job_description}
- Tone: {tone} and conversational
- Current question: {question_number}

Your responsibilities:
1. Ask insightful, relevant questions about the candidate's experience and skills
2. Listen carefully to responses and ask adaptive follow-up questions
3. Assess technical depth, problem-solving ability, and communication skills
4. Keep questions focused and interview flowing naturally
5. Be encouraging while maintaining professional standards

Guidelines:
- Ask ONE question at a time
- Keep questions concise (2-3 sentences max)
- Build on previous answers naturally
- Vary question types (technical, behavioral, situational)
- Don't repeat topics already covered
- Conclude gracefully after 8-10 questions

Current interview stage: {interview_stage}"""

SENTIMENT_CONTEXT_TEMPLATE = """
Candidate's response sentiment: {sentiment} (confidence: {confidence:.2f})
Sentiment scores: {scores}

Use this sentiment information to adapt your response:
- If negative sentiment: Be more encouraging and understanding
- If positive sentiment: Build on their enthusiasm
- If neutral sentiment: Continue with standard questioning
"""

USER_MESSAGE_TEMPLATE = """Candidate's response: "{transcript}"

{sentiment_context}

Conversation context:
{conversation_history}

Generate an appropriate follow-up question or response based on:
1. The candidate's answer quality and depth
2. Current interview topic: {current_topic}
3. Number of questions asked: {question_count}
4. Job requirements from the description
5. Candidate's sentiment and emotional state

Provide a natural, conversational follow-up that advances the interview while being sensitive to the candidate's emotional state."""
