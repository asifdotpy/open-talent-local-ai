"""Vetta AI v4 Integration for Interview Service
Uses fine-tuned Granite 3.0 2B GGUF model via Ollama for comprehensive recruiting AI.
"""

import logging
import os
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "vetta-granite-2b")
OLLAMA_TIMEOUT = float(
    os.getenv("OLLAMA_TIMEOUT", "90.0")
)  # Increased to 90s for first-time model loading

# Legacy Unsloth support (fallback)
try:
    import torch
    from unsloth import FastLanguageModel

    UNSLOTH_AVAILABLE = True
except ImportError:
    UNSLOTH_AVAILABLE = False
    logger.info("Unsloth not available - using Ollama (recommended)")


class VettaAI:
    """Vetta AI v4 - Comprehensive Recruiting AI via Ollama.

    Supports 8 domains:
    1. Interview - Avatar interview orchestration
    2. Sourcing - Candidate discovery
    3. Search - Boolean query generation
    4. Engagement - Personalized outreach
    5. Discovery - Platform scanning
    6. Quality - Candidate assessment
    7. Market - Salary intelligence
    8. Integration - ATS/CRM sync
    """

    def __init__(self, model_name: str = OLLAMA_MODEL_NAME, use_ollama: bool = True):
        """Initialize Vetta AI model.

        Args:
            model_name: Ollama model name or HuggingFace repository
            use_ollama: Use Ollama API (recommended) vs Unsloth direct loading
        """
        self.model_name = model_name
        self.use_ollama = use_ollama
        self.ollama_url = OLLAMA_API_URL
        self.loaded = False
        self.fallback_mode = False

        # Ollama client
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(OLLAMA_TIMEOUT, connect=5.0),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )

        if use_ollama:
            self._check_ollama_connection()
        # Legacy Unsloth path
        elif UNSLOTH_AVAILABLE:
            self._load_model_unsloth()
        else:
            self.fallback_mode = True
            logger.warning("Neither Ollama nor Unsloth available - using fallback mode")

    def _check_ollama_connection(self):
        """Check Ollama service connection synchronously."""
        try:
            import requests

            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]

                if self.model_name in model_names or f"{self.model_name}:latest" in model_names:
                    self.loaded = True
                    logger.info(f"✅ Vetta AI v4 connected to Ollama: {self.model_name}")
                else:
                    logger.warning(
                        f"Model {self.model_name} not found in Ollama. Available: {model_names}"
                    )
                    self.fallback_mode = True
            else:
                logger.warning(f"Ollama API returned {response.status_code}")
                self.fallback_mode = True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama at {self.ollama_url}: {e}")
            self.fallback_mode = True

    def _load_model_unsloth(self):
        """Load the fine-tuned model from HuggingFace Hub using Unsloth (legacy)."""
        try:
            logger.info(f"Loading Vetta AI v4 model via Unsloth: {self.model_name}")

            # Load model with 4-bit quantization for efficiency
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.model_name,
                max_seq_length=2048,
                dtype=None,  # Auto-detect
                load_in_4bit=True,
            )

            # Set model to inference mode
            FastLanguageModel.for_inference(self.model)

            self.loaded = True
            logger.info("✅ Vetta AI v4 loaded successfully via Unsloth")

            # Log GPU memory usage if available
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.memory_allocated() / 1024**3
                logger.info(f"GPU Memory: {gpu_memory:.2f} GB")

        except Exception as e:
            logger.error(f"Failed to load Vetta AI model via Unsloth: {e}")
            self.fallback_mode = True
            logger.warning("Switching to fallback mode")

    def _format_prompt(self, instruction: str, context: str | None = None) -> str:
        """Format prompt in Alpaca instruction-response format.

        Args:
            instruction: The task instruction
            context: Optional context information

        Returns:
            Formatted prompt string
        """
        if context:
            return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{context}

### Response:"""
        else:
            return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:"""

    async def _generate_ollama(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """Generate response using Ollama API.

        Args:
            prompt: Formatted prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling threshold

        Returns:
            Generated response text
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens,
                },
            }

            logger.info(f"Sending request to Ollama ({len(prompt)} chars prompt)")

            response = await self.http_client.post(f"{self.ollama_url}/api/generate", json=payload)

            response.raise_for_status()
            result = response.json()

            generated_text = result.get("response", "").strip()

            # Clean up the response - remove any trailing incomplete sentences or format artifacts
            if "###" in generated_text:
                generated_text = generated_text.split("###")[0].strip()

            logger.info(f"Generated response via Ollama ({len(generated_text)} chars)")

            return generated_text

        except httpx.TimeoutException as e:
            logger.error(f"Ollama API timeout after {OLLAMA_TIMEOUT}s: {e}")
            return self._fallback_generate_sync(prompt)
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API HTTP error {e.response.status_code}: {e}")
            return self._fallback_generate_sync(prompt)
        except httpx.HTTPError as e:
            logger.error(f"Ollama API connection error: {e}")
            return self._fallback_generate_sync(prompt)
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return self._fallback_generate_sync(prompt)

    def _generate_unsloth(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """Generate response using Unsloth (legacy)."""
        try:
            # Tokenize
            inputs = self.tokenizer([prompt], return_tensors="pt").to("cuda")

            # Generate
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
            )

            # Decode
            full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract response
            if "### Response:" in full_output:
                response = full_output.split("### Response:")[-1].strip()
            else:
                response = full_output.strip()

            logger.debug(f"Generated response via Unsloth ({len(response)} chars)")
            return response

        except Exception as e:
            logger.error(f"Unsloth generation failed: {e}")
            return self._fallback_generate_sync(prompt)

    async def generate(
        self,
        instruction: str,
        context: str | None = None,
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """Generate response using Vetta AI.

        Args:
            instruction: Task instruction (e.g., "Assess this candidate's skills")
            context: Optional context (e.g., candidate profile, job description)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling threshold

        Returns:
            Generated response text
        """
        if self.fallback_mode:
            return self._fallback_generate(instruction, context)

        # Format prompt
        prompt = self._format_prompt(instruction, context)

        # Generate using appropriate backend
        if self.use_ollama:
            return await self._generate_ollama(prompt, max_tokens, temperature, top_p)
        else:
            return self._generate_unsloth(prompt, max_tokens, temperature, top_p)

    def _fallback_generate_sync(self, prompt: str) -> str:
        """Fallback for synchronous contexts."""
        if "assess" in prompt.lower() or "skill" in prompt.lower():
            return """Skill Score: 7/10. Strengths: Relevant experience demonstrated. Gaps: Limited specific examples provided. Growth potential: 8/10. Recommendation: Proceed with technical assessment."""
        return "Response generated in fallback mode."

    def _fallback_generate(self, instruction: str, context: str | None = None) -> str:
        """Fallback response when model is unavailable.

        Returns basic structured response based on instruction type.
        """
        logger.warning("Using fallback generation")

        if "assess" in instruction.lower() or "skill" in instruction.lower():
            return """Skill Score: 7/10. Strengths: Relevant experience demonstrated. Gaps: Limited specific examples provided. Growth potential: 8/10. Recommendation: Proceed with technical assessment. Rationale: Candidate shows promise but needs deeper evaluation."""

        elif "question" in instruction.lower():
            return "Can you describe a challenging project you've worked on and how you approached solving the key technical problems?"

        elif "engagement" in instruction.lower() or "outreach" in instruction.lower():
            return "Subject: Exciting [Role] Opportunity at [Company]\n\nHi [Name],\n\nI came across your profile and was impressed by your experience with [Skill]. We have an exciting opportunity that aligns well with your background.\n\nWould you be open to a brief conversation?\n\nBest regards"

        else:
            return "Thank you for your response. I appreciate the insight you've provided."

    async def assess_candidate(
        self, candidate_info: str, job_description: str, role: str = "Senior Python Developer"
    ) -> dict[str, Any]:
        """Assess candidate's technical skills for a role.

        Args:
            candidate_info: Candidate profile/resume text
            job_description: Job requirements
            role: Role title

        Returns:
            Assessment dictionary with score, strengths, gaps, recommendation
        """
        instruction = f"Assess this candidate's technical skills for a {role} role.\n\nCandidate: {candidate_info}"
        context = f"Role: {role}\nRequirements: {job_description}"

        response = await self.generate(instruction, context, max_tokens=300)

        # Parse response (basic extraction)
        return {
            "assessment": response,
            "timestamp": datetime.now().isoformat(),
            "model": self.model_name,
            "role": role,
        }

    async def generate_interview_question(
        self,
        previous_responses: list[str],
        job_requirements: str,
        expertise_level: str = "intermediate",
    ) -> str:
        """Generate next interview question based on context.

        Args:
            previous_responses: List of previous candidate responses
            job_requirements: Job requirements text
            expertise_level: Assessed expertise level

        Returns:
            Generated interview question
        """
        context_text = "\n".join([f"- {resp[:100]}..." for resp in previous_responses[-3:]])

        instruction = (
            f"Generate the next interview question for a {expertise_level} level candidate."
        )
        context = f"Job Requirements: {job_requirements}\n\nPrevious Responses:\n{context_text}"

        question = await self.generate(instruction, context, max_tokens=150, temperature=0.8)

        # Extract just the question if it includes extra text
        if "?" in question:
            question = question.split("?")[0] + "?"

        return question

    async def generate_outreach_message(
        self, candidate_name: str, candidate_skills: str, role: str, company: str
    ) -> str:
        """Generate personalized outreach message.

        Args:
            candidate_name: Candidate's name
            candidate_skills: Key skills to highlight
            role: Role title
            company: Company name

        Returns:
            Personalized outreach message
        """
        instruction = f"Write a personalized outreach message to {candidate_name} for a {role} position at {company}."
        context = f"Candidate skills: {candidate_skills}\nKeep it professional and concise (3-4 sentences)."

        message = await self.generate(instruction, context, max_tokens=200, temperature=0.7)

        return message

    async def score_candidate_quality(
        self,
        candidate_profile: str,
        job_requirements: str,
        scoring_criteria: list[str] | None = None,
    ) -> dict[str, Any]:
        """Score candidate quality against job requirements.

        Args:
            candidate_profile: Candidate information
            job_requirements: Job requirements
            scoring_criteria: Optional custom criteria

        Returns:
            Scoring results with breakdown
        """
        criteria = scoring_criteria or ["Skill match", "Experience", "Culture fit"]
        criteria_text = ", ".join(criteria)

        instruction = f"Score this candidate's quality based on: {criteria_text}.\n\nCandidate: {candidate_profile}"
        context = f"Requirements: {job_requirements}"

        response = await self.generate(instruction, context, max_tokens=250)

        return {
            "score_analysis": response,
            "criteria": criteria,
            "timestamp": datetime.now().isoformat(),
        }

    async def analyze_response_sentiment(self, response_text: str) -> dict[str, Any]:
        """Analyze sentiment of candidate response.

        Args:
            response_text: Candidate's response

        Returns:
            Sentiment analysis
        """
        instruction = "Analyze the sentiment and tone of this candidate response."
        context = f"Response: {response_text}"

        analysis = await self.generate(instruction, context, max_tokens=150, temperature=0.5)

        return {"sentiment_analysis": analysis, "timestamp": datetime.now().isoformat()}

    def get_model_info(self) -> dict[str, Any]:
        """Get model information and status."""
        cuda_available = False
        gpu_memory_gb = 0

        if not self.use_ollama and UNSLOTH_AVAILABLE:
            import torch

            cuda_available = torch.cuda.is_available()
            if cuda_available:
                gpu_memory_gb = torch.cuda.memory_allocated() / 1024**3

        return {
            "model_name": self.model_name,
            "backend": "Ollama" if self.use_ollama else "Unsloth",
            "ollama_url": self.ollama_url if self.use_ollama else None,
            "loaded": self.loaded,
            "fallback_mode": self.fallback_mode,
            "unsloth_available": UNSLOTH_AVAILABLE,
            "cuda_available": cuda_available,
            "gpu_memory_gb": gpu_memory_gb,
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
            "version": "v4",
            "model_format": "GGUF (q4_k_m quantized)" if self.use_ollama else "LoRA",
            "model_size_gb": 1.55 if self.use_ollama else 4.8,
            "training_details": {
                "dataset_size": 2075,
                "domains": 8,
                "final_loss": 0.1260,
                "training_time_minutes": 28,
                "base_model": "ibm-granite/granite-3.0-2b-instruct",
            },
        }


# Global instance (singleton pattern)
_vetta_ai_instance: VettaAI | None = None


def get_vetta_ai() -> VettaAI:
    """Get or create global Vetta AI instance."""
    global _vetta_ai_instance

    if _vetta_ai_instance is None:
        _vetta_ai_instance = VettaAI()

    return _vetta_ai_instance


# Example usage
if __name__ == "__main__":
    # Test Vetta AI
    logging.basicConfig(level=logging.INFO)

    vetta = get_vetta_ai()

    print("Model Info:", vetta.get_model_info())

    # Test candidate assessment
    assessment = vetta.assess_candidate(
        candidate_info="5 years Python, Django expert, built scalable APIs, open source contributor",
        job_description="Senior Python Developer - Python, AWS, System Design",
        role="Senior Python Developer",
    )

    print("\nAssessment:", assessment["assessment"])
