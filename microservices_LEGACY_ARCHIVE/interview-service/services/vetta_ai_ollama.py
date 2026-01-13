"""
Vetta AI Service - Ollama Integration
Simple alternative to the Unsloth-based service using Ollama for inference.

This module provides the same VettaAI interface but uses Ollama backend,
making it easier to deploy without heavy ML dependencies.

Prerequisites:
- Ollama installed and running (https://ollama.ai)
- Vetta AI model imported to Ollama: `ollama create vetta-granite-2b -f Modelfile`

Usage:
    from services.vetta_ai_ollama import get_vetta_ai

    vetta = get_vetta_ai()
    assessment = vetta.assess_candidate(...)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Check if ollama is available
try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("ollama package not available. Install with: pip install ollama")

logger = logging.getLogger(__name__)


class VettaAIOllama:
    """Vetta AI service using Ollama backend."""

    def __init__(self, model_name: str = "vetta-granite-2b"):
        """
        Initialize Vetta AI with Ollama backend.

        Args:
            model_name: Name of the Ollama model to use
        """
        self.model_name = model_name
        self.ollama_available = self._check_ollama()

        if self.ollama_available:
            logger.info(f"✅ Vetta AI initialized with Ollama model: {model_name}")
        else:
            logger.warning("⚠️  Ollama not available, using fallback mode")

    def _check_ollama(self) -> bool:
        """Check if Ollama is available and model exists."""
        if not OLLAMA_AVAILABLE:
            return False

        try:
            # Check if Ollama server is running
            models = ollama.list()

            # Check if our model exists
            model_names = [m["name"] for m in models.get("models", [])]
            if self.model_name not in model_names:
                logger.warning(
                    f"Model '{self.model_name}' not found in Ollama. Available: {model_names}"
                )
                logger.info(f"Create model with: ollama create {self.model_name} -f Modelfile")
                return False

            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False

    def _format_prompt(self, instruction: str, context: str = "") -> str:
        """
        Format prompt in Alpaca structure.

        Args:
            instruction: The instruction/task description
            context: Additional context or input

        Returns:
            Formatted prompt string
        """
        if context:
            prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{context}

### Response:
"""
        else:
            prompt = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
"""
        return prompt

    def generate(
        self,
        instruction: str,
        context: str = "",
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        Generate text using Ollama.

        Args:
            instruction: The task instruction
            context: Additional context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter

        Returns:
            Generated text
        """
        if not self.ollama_available:
            return self._fallback_generate(instruction, context)

        try:
            prompt = self._format_prompt(instruction, context)

            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens,
                },
            )

            return response["response"].strip()

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return self._fallback_generate(instruction, context)

    def _fallback_generate(self, instruction: str, context: str = "") -> str:
        """Fallback response when Ollama unavailable."""
        return f"[Fallback Mode] Processing: {instruction[:100]}... (Ollama not available)"

    def assess_candidate(
        self,
        candidate_info: str,
        job_description: str,
        role: str,
    ) -> Dict[str, Any]:
        """
        Assess candidate fit for a role.

        Args:
            candidate_info: Candidate background and skills
            job_description: Job requirements
            role: Role title

        Returns:
            Assessment with score, strengths, gaps, recommendation
        """
        instruction = f"""Assess this candidate for the {role} position.
Provide:
1. Overall skill score (1-10)
2. Key strengths
3. Skill gaps
4. Growth potential
5. Hiring recommendation

Be specific and actionable."""

        context = f"""Candidate: {candidate_info}

Job Requirements: {job_description}"""

        assessment_text = self.generate(instruction, context, max_tokens=300)

        return {
            "assessment": assessment_text,
            "candidate_info": candidate_info,
            "role": role,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def generate_interview_question(
        self,
        previous_responses: List[str],
        job_requirements: str,
        expertise_level: str = "intermediate",
    ) -> str:
        """
        Generate context-aware interview question.

        Args:
            previous_responses: List of candidate's previous answers
            job_requirements: Job requirements and skills
            expertise_level: beginner, intermediate, or advanced

        Returns:
            Interview question
        """
        instruction = f"""Generate a {expertise_level}-level interview question for a candidate.
The question should:
1. Build on previous conversation
2. Assess relevant skills
3. Be specific and practical
4. Allow for deep technical discussion"""

        context = f"""Previous responses:
{chr(10).join(f'- {r}' for r in previous_responses)}

Requirements: {job_requirements}"""

        question = self.generate(instruction, context, max_tokens=150)
        return question

    def generate_outreach_message(
        self,
        candidate_name: str,
        candidate_skills: str,
        role: str,
        company: str,
    ) -> str:
        """
        Generate personalized outreach message.

        Args:
            candidate_name: Candidate's name
            candidate_skills: Candidate's key skills
            role: Role title
            company: Company name

        Returns:
            Outreach message
        """
        instruction = f"""Write a personalized outreach message to {candidate_name}.
The message should:
1. Reference their specific skills
2. Explain the role opportunity
3. Be professional and engaging
4. Include a clear call-to-action
5. Be 3-4 sentences maximum"""

        context = f"""Candidate: {candidate_name}
Skills: {candidate_skills}
Role: {role}
Company: {company}"""

        message = self.generate(instruction, context, max_tokens=200)
        return message

    def score_candidate_quality(
        self,
        candidate_profile: str,
        job_requirements: str,
        scoring_criteria: List[str],
    ) -> Dict[str, Any]:
        """
        Score candidate quality across multiple criteria.

        Args:
            candidate_profile: Candidate background
            job_requirements: Job requirements
            scoring_criteria: List of criteria to score

        Returns:
            Scores and overall assessment
        """
        instruction = f"""Score this candidate on the following criteria (1-10 each):
{chr(10).join(f'- {c}' for c in scoring_criteria)}

Provide scores and brief justification for each."""

        context = f"""Candidate: {candidate_profile}

Requirements: {job_requirements}"""

        scoring_text = self.generate(instruction, context, max_tokens=300)

        return {
            "scoring": scoring_text,
            "criteria": scoring_criteria,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def analyze_response_sentiment(
        self,
        response_text: str,
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of candidate response.

        Args:
            response_text: Text to analyze

        Returns:
            Sentiment analysis (positive/negative/neutral, confidence, insights)
        """
        instruction = """Analyze the sentiment and tone of this response.
Provide:
1. Overall sentiment (positive/negative/neutral)
2. Confidence level (high/medium/low)
3. Key emotional indicators
4. Professional assessment"""

        context = f"Response: {response_text}"

        sentiment_text = self.generate(instruction, context, max_tokens=200)

        return {
            "sentiment_analysis": sentiment_text,
            "response_text": response_text,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information and status.

        Returns:
            Model metadata and status
        """
        info = {
            "model_name": self.model_name,
            "backend": "ollama",
            "loaded": self.ollama_available,
            "fallback_mode": not self.ollama_available,
            "version": "v4-ollama",
            "domains": [
                "interview",
                "sourcing",
                "search",
                "engagement",
                "discovery",
                "quality",
                "market",
                "integration",
            ],
        }

        if self.ollama_available:
            try:
                # Get model details from Ollama
                models = ollama.list()
                for model in models.get("models", []):
                    if model["name"] == self.model_name:
                        info["model_size"] = model.get("size", "unknown")
                        info["model_modified"] = model.get("modified_at", "unknown")
                        break
            except:
                pass

        return info


# Global singleton instance
_vetta_instance: Optional[VettaAIOllama] = None


def get_vetta_ai(model_name: str = "vetta-granite-2b") -> VettaAIOllama:
    """
    Get global VettaAI instance (singleton pattern).

    Args:
        model_name: Ollama model name

    Returns:
        VettaAIOllama instance
    """
    global _vetta_instance

    if _vetta_instance is None:
        _vetta_instance = VettaAIOllama(model_name=model_name)

    return _vetta_instance


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    vetta = get_vetta_ai()

    # Check status
    info = vetta.get_model_info()
    print(f"\n📊 Model Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")

    # Test assessment
    print("\n🧪 Testing candidate assessment...")
    assessment = vetta.assess_candidate(
        candidate_info="5 years Python, Django expert, built scalable APIs",
        job_description="Senior Python Developer - Python, AWS, System Design",
        role="Senior Python Developer",
    )
    print(f"Assessment: {assessment['assessment'][:200]}...")

    # Test question generation
    print("\n🧪 Testing question generation...")
    question = vetta.generate_interview_question(
        previous_responses=["I have 5 years of Python experience"],
        job_requirements="Python, AWS, System Design",
        expertise_level="intermediate",
    )
    print(f"Question: {question}")

    print("\n✅ Tests complete!")
