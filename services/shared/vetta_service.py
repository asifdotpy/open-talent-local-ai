#!/usr/bin/env python3
"""
Vetta AI Service Integration
Simple wrapper for integrating Vetta AI v4 into microservices
"""

from enum import Enum

import torch


class RecruitingTask(Enum):
    """Recruiting task types"""

    INTERVIEW = "interview"
    ASSESSMENT = "quality"
    SOURCING = "sourcing"
    SEARCH = "search"
    OUTREACH = "engagement"


class VettaService:
    """
    Lightweight Vetta AI service wrapper
    Use this in your microservices (interview-service, etc.)
    """

    def __init__(self, model_path: str = "asifdotpy/vetta-granite-2b-lora-v4"):
        """Initialize Vetta AI model"""
        from unsloth import FastLanguageModel

        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_path,
            max_seq_length=2048,
            dtype=None,
            load_in_4bit=True,
        )
        FastLanguageModel.for_inference(self.model)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def _format_prompt(self, instruction: str, context: str | None = None) -> str:
        """Format prompt in Alpaca style"""
        prompt = f"### Instruction:\n{instruction}"
        if context:
            prompt += f"\n\nContext:\n{context}"
        prompt += "\n\n### Response:"
        return prompt

    def generate(
        self,
        instruction: str,
        context: str | None = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate AI response

        Args:
            instruction: User instruction/question
            context: Optional context
            max_tokens: Max tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated response
        """
        prompt = self._format_prompt(instruction, context)
        inputs = self.tokenizer([prompt], return_tensors="pt").to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract response
        if "### Response:" in full_text:
            return full_text.split("### Response:")[-1].strip()
        return full_text.strip()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FastAPI Integration Example
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
Example FastAPI endpoint for interview service:

from fastapi import FastAPI
from vetta_service import VettaService

app = FastAPI()
vetta = VettaService()

@app.post("/interview/assess")
async def assess_candidate(
    candidate_info: str,
    job_requirements: str
):
    instruction = "Assess this candidate's technical skills"
    context = f"Candidate: {candidate_info}\\n\\nRole: {job_requirements}"

    assessment = vetta.generate(
        instruction=instruction,
        context=context,
        max_tokens=256,
        temperature=0.7
    )

    return {"assessment": assessment}
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Django Integration Example
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
Example Django view for interview assessment:

from django.http import JsonResponse
from vetta_service import VettaService

# Initialize once (singleton)
vetta = VettaService()

def assess_interview(request):
    candidate_info = request.POST.get('candidate_info')
    job_requirements = request.POST.get('job_requirements')

    instruction = "Assess this candidate's fit for the role"
    context = f"Candidate: {candidate_info}\\n\\nRole: {job_requirements}"

    assessment = vetta.generate(
        instruction=instruction,
        context=context
    )

    return JsonResponse({'assessment': assessment})
"""
