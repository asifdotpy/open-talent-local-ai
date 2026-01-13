"""
Placeholder for the Conversation Service.
"""

from app.schemas.interview import CandidateProfile


def initiate_conversation(candidate_profile: CandidateProfile) -> str:
    """
    Initiates the conversation with the Conversation Service.
    In a real implementation, this would call the Conversation Service.
    """
    print("--- CONVERSATION SERVICE ---")
    print(f"Initiating conversation for: {candidate_profile.fullName}")
    first_question = (
        candidate_profile.initialQuestions[0].question
        if candidate_profile.initialQuestions
        else "Tell me about yourself."
    )
    print(f"First question: {first_question}")
    print("--- END CONVERSATION SERVICE ---")
    return first_question
