import os
import httpx
from typing import Dict, Any, Optional
import asyncio
from dotenv import load_dotenv

load_dotenv()


class OllamaLLMError(Exception):
    """Custom exception for Ollama LLM errors."""
    pass


class OllamaLLMService:
    """Service for handling LLM processing using local Ollama."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama LLM service.

        Args:
            base_url: The base URL for Ollama API (default: http://localhost:11434)
        """
        self.base_url = base_url
        self.model = os.environ.get("OLLAMA_MODEL", "granite4:350m-h")

    async def generate_interview_response(
        self,
        candidate_input: str,
        system_prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate interview response using local Ollama LLM.

        Args:
            candidate_input: The candidate's response or input
            system_prompt: System prompt for the LLM context
            context: Additional context (job description, interview stage, etc.)

        Returns:
            Generated response text for the interviewer
        """
        try:
            # Build the complete prompt
            full_prompt = self._build_interview_prompt(candidate_input, system_prompt, context)

            # Make request to local Ollama
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False,
                        "system": system_prompt
                    }
                )
                response.raise_for_status()

                result = response.json()
                return result.get("response", "").strip()

        except httpx.HTTPStatusError as e:
            raise OllamaLLMError(f"Ollama API request failed: {e.response.status_code} - {e.response.text}")
        except httpx.TimeoutException:
            raise OllamaLLMError("Ollama API request timed out")
        except Exception as e:
            raise OllamaLLMError(f"Unexpected error in Ollama LLM service: {str(e)}")

    async def generate_script_text(
        self,
        interview_context: Dict[str, Any],
        system_prompt: str
    ) -> str:
        """
        Generate script text for avatar video creation.

        Args:
            interview_context: Context about the interview (stage, questions, responses)
            system_prompt: System prompt defining the interviewer persona

        Returns:
            Script text for the avatar to speak
        """
        prompt = self._build_script_prompt(interview_context, system_prompt)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "system": system_prompt
                    }
                )
                response.raise_for_status()

                result = response.json()
                script_text = result.get("response", "").strip()

                # Clean up the script for voice synthesis
                return self._clean_script_for_voice(script_text)

        except Exception as e:
            raise OllamaLLMError(f"Failed to generate script text: {str(e)}")

    def _build_interview_prompt(
        self,
        candidate_input: str,
        system_prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build complete prompt for interview response generation."""
        prompt_parts = [
            "You are conducting a professional interview. Generate a response based on the candidate's input.",
            ""
        ]

        if context:
            if context.get("job_title"):
                prompt_parts.append(f"Position: {context['job_title']}")
            if context.get("interview_stage"):
                prompt_parts.append(f"Interview Stage: {context['interview_stage']}")
            if context.get("previous_questions"):
                prompt_parts.append(f"Previous Questions Asked: {context['previous_questions']}")
            prompt_parts.append("")

        prompt_parts.extend([
            f"Candidate Response: {candidate_input}",
            "",
            "Generate an appropriate follow-up question or response as the interviewer:",
        ])

        return "\n".join(prompt_parts)

    def _build_script_prompt(self, interview_context: Dict[str, Any], system_prompt: str) -> str:
        """Build prompt for script generation."""
        return f"""
Generate a natural, conversational script for an AI interviewer avatar based on this context:

Context: {interview_context}

Requirements:
- Keep response under 100 words for natural speech
- Sound professional but friendly
- Ask clear, specific questions
- Avoid filler words and repetition

Generate the script text only:
"""

    def _clean_script_for_voice(self, script_text: str) -> str:
        """Clean up script text for better voice synthesis."""
        # Remove unwanted characters and formatting
        cleaned = script_text.strip()

        # Remove any markdown formatting
        cleaned = cleaned.replace("**", "").replace("*", "")

        # Ensure proper sentence ending
        if not cleaned.endswith(('.', '!', '?')):
            cleaned += "."

        return cleaned

    async def health_check(self) -> bool:
        """Check if Ollama service is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False


# Example usage and testing
async def main():
    """Test the Ollama LLM service."""
    ollama = OllamaLLMService()

    # Test health check
    if not await ollama.health_check():
        print("❌ Ollama service not available")
        return

    print("✅ Ollama service is available")

    # Test interview response generation
    context = {
        "job_title": "Software Engineer",
        "interview_stage": "technical_screening",
        "previous_questions": ["Tell me about yourself"]
    }

    system_prompt = "You are Interview, a professional and friendly AI interviewer for technical positions."
    candidate_input = "I have 5 years of experience in Python dev and have worked on several web applications using FastAPI."

    try:
        response = await ollama.generate_interview_response(
            candidate_input=candidate_input,
            system_prompt=system_prompt,
            context=context
        )
        print(f"🤖 Generated Response: {response}")

        # Test script generation
        script = await ollama.generate_script_text(
            interview_context=context,
            system_prompt=system_prompt
        )
        print(f"📜 Generated Script: {script}")

    except OllamaLLMError as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())