#!/usr/bin/env python3
"""
Vetta AI v4 - Local Inference Script
Load and use the fine-tuned Granite 3.0 2B LoRA model for recruiting tasks

Use Cases:
1. Recruiter/Hiring Manager Chat - Dynamic system prompts for various recruiting tasks
2. AI Avatar Interview - Interview orchestration and candidate assessment

Model: asifdotpy/vetta-granite-2b-lora-v4
Dataset: 2,075 examples across 8 domains (sourcing, search, engagement, discovery, quality, market, integration, interview)
"""

import os
import torch
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class TaskType(Enum):
    """Recruiting task types supported by Vetta AI"""
    INTERVIEW = "interview"
    SOURCING = "sourcing"
    SEARCH = "search"
    ENGAGEMENT = "engagement"
    DISCOVERY = "discovery"
    QUALITY = "quality"
    MARKET = "market"
    INTEGRATION = "integration"


@dataclass
class SystemPrompt:
    """System prompts for different recruiting tasks"""
    
    INTERVIEW = """You are Vetta, an AI interviewer conducting professional candidate interviews.
Your role:
- Ask relevant, probing questions based on job requirements
- Evaluate candidate responses objectively
- Provide comprehensive assessment scores
- Adapt questioning based on candidate expertise
- Maintain professional, engaging conversation

Response format: Provide structured assessments with scores, strengths, gaps, and recommendations."""

    SOURCING = """You are Vetta, an AI sourcing specialist helping recruiters find top talent.
Your role:
- Identify candidate sourcing strategies
- Recommend talent pools and platforms
- Suggest outreach approaches
- Analyze candidate market availability

Response format: Provide actionable sourcing strategies with specific platforms and approaches."""

    SEARCH = """You are Vetta, an AI search expert generating optimized boolean queries.
Your role:
- Create platform-specific boolean search queries (LinkedIn, GitHub, etc.)
- Extract keywords from job descriptions
- Build advanced search strings with boolean logic
- Optimize queries for maximum relevant results

Response format: Provide boolean queries with explanations of search logic."""

    ENGAGEMENT = """You are Vetta, an AI engagement specialist crafting personalized outreach.
Your role:
- Generate personalized candidate outreach messages
- Recommend multi-channel communication strategies
- Suggest follow-up sequences
- Optimize engagement timing and tone

Response format: Provide personalized messages with engagement strategy recommendations."""

    DISCOVERY = """You are Vetta, an AI talent discovery agent scanning multiple platforms.
Your role:
- Identify promising candidates across platforms (LinkedIn, GitHub, Stack Overflow)
- Extract relevant profile data
- Match candidates to job requirements
- Prioritize candidates by fit score

Response format: Provide candidate profiles with match scores and key highlights."""

    QUALITY = """You are Vetta, an AI quality assessment expert evaluating candidates.
Your role:
- Score candidates using multiple criteria (skills, experience, culture fit)
- Calculate skill match percentages
- Identify strengths and gaps
- Detect potential bias in evaluation
- Provide hire/reject recommendations

Response format: Provide structured scores with detailed rationale and risk assessment."""

    MARKET = """You are Vetta, an AI market intelligence analyst providing competitive insights.
Your role:
- Analyze salary benchmarks and compensation trends
- Map competitor hiring activities
- Track skill demand and growth rates
- Provide data-driven market recommendations

Response format: Provide market data with actionable compensation and hiring insights."""

    INTEGRATION = """You are Vetta, an AI integration specialist managing ATS/CRM workflows.
Your role:
- Sync candidate data across systems
- Transform data formats for different platforms
- Manage API integrations and data flow
- Ensure data consistency and accuracy

Response format: Provide integration workflows with data mapping and sync strategies."""


class VettaAI:
    """
    Vetta AI v4 - Fine-tuned Granite 3.0 2B for recruiting
    Supports all 8 recruiting domains with dynamic system prompts
    """
    
    def __init__(
        self,
        model_name: str = "asifdotpy/vetta-granite-2b-lora-v4",
        max_seq_length: int = 2048,
        load_in_4bit: bool = True,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Initialize Vetta AI model
        
        Args:
            model_name: HuggingFace model repository
            max_seq_length: Maximum sequence length for generation
            load_in_4bit: Use 4-bit quantization (saves memory)
            device: Device to load model on (cuda/cpu)
        """
        self.model_name = model_name
        self.max_seq_length = max_seq_length
        self.device = device
        self.load_in_4bit = load_in_4bit
        
        print(f"🚀 Initializing Vetta AI v4...")
        print(f"   Model: {model_name}")
        print(f"   Device: {device}")
        print(f"   4-bit quantization: {load_in_4bit}")
        
        self._load_model()
        
    def _load_model(self):
        """Load the fine-tuned model and tokenizer"""
        try:
            from unsloth import FastLanguageModel
            
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.model_name,
                max_seq_length=self.max_seq_length,
                dtype=None,  # Auto-detect
                load_in_4bit=self.load_in_4bit,
            )
            
            # Enable inference mode for faster generation
            FastLanguageModel.for_inference(self.model)
            
            if torch.cuda.is_available():
                gpu_mem = torch.cuda.memory_allocated() / 1024**3
                print(f"✅ Model loaded | GPU Memory: {gpu_mem:.2f} GB")
            else:
                print(f"✅ Model loaded on CPU")
                
        except ImportError:
            print("❌ Error: 'unsloth' not installed")
            print("   Install: pip install unsloth")
            raise
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def generate(
        self,
        instruction: str,
        task_type: TaskType = TaskType.INTERVIEW,
        context: Optional[str] = None,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        repetition_penalty: float = 1.1,
    ) -> str:
        """
        Generate response for a given instruction
        
        Args:
            instruction: User instruction/question
            task_type: Type of recruiting task (determines system prompt)
            context: Optional context to include in prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0, higher = more creative)
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling parameter
            repetition_penalty: Penalty for repeating tokens
            
        Returns:
            Generated response text
        """
        # Get system prompt for task type
        system_prompt = getattr(SystemPrompt, task_type.value.upper())
        
        # Build prompt in Alpaca format
        prompt = f"{system_prompt}\n\n### Instruction:\n{instruction}"
        
        if context:
            prompt += f"\n\nContext:\n{context}"
        
        prompt += "\n\n### Response:"
        
        # Tokenize
        inputs = self.tokenizer([prompt], return_tensors="pt").to(self.device)
        
        # Generate
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        
        # Decode and extract response only
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract response after "### Response:"
        if "### Response:" in full_text:
            response = full_text.split("### Response:")[-1].strip()
        else:
            response = full_text.strip()
        
        return response
    
    def chat(
        self,
        instruction: str,
        task_type: TaskType = TaskType.INTERVIEW,
        context: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Simplified chat interface
        
        Args:
            instruction: User message
            task_type: Type of recruiting task
            context: Optional context
            **kwargs: Additional generation parameters
            
        Returns:
            AI response
        """
        return self.generate(instruction, task_type, context, **kwargs)
    
    def interview(
        self,
        question: str,
        candidate_info: Optional[str] = None,
        job_requirements: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Conduct interview questioning and assessment
        
        Args:
            question: Interview question or candidate response to evaluate
            candidate_info: Information about candidate
            job_requirements: Job role requirements
            **kwargs: Additional generation parameters
            
        Returns:
            Interview assessment or next question
        """
        context = []
        if candidate_info:
            context.append(f"Candidate: {candidate_info}")
        if job_requirements:
            context.append(f"Role: {job_requirements}")
        
        context_str = "\n".join(context) if context else None
        
        return self.generate(
            instruction=question,
            task_type=TaskType.INTERVIEW,
            context=context_str,
            **kwargs
        )
    
    def assess_candidate(
        self,
        candidate_profile: str,
        job_requirements: str,
        **kwargs
    ) -> str:
        """
        Assess candidate quality and fit
        
        Args:
            candidate_profile: Candidate background and skills
            job_requirements: Job requirements and criteria
            **kwargs: Additional generation parameters
            
        Returns:
            Comprehensive candidate assessment
        """
        instruction = f"Assess this candidate's fit for the role"
        context = f"Candidate: {candidate_profile}\n\nRole: {job_requirements}"
        
        return self.generate(
            instruction=instruction,
            task_type=TaskType.QUALITY,
            context=context,
            **kwargs
        )
    
    def generate_boolean_query(
        self,
        job_description: str,
        platform: str = "LinkedIn",
        **kwargs
    ) -> str:
        """
        Generate boolean search query for sourcing
        
        Args:
            job_description: Job description to extract keywords from
            platform: Target platform (LinkedIn, GitHub, etc.)
            **kwargs: Additional generation parameters
            
        Returns:
            Boolean search query
        """
        instruction = f"Generate a {platform} boolean search query for this role"
        context = f"Job Description:\n{job_description}"
        
        return self.generate(
            instruction=instruction,
            task_type=TaskType.SEARCH,
            context=context,
            **kwargs
        )
    
    def create_outreach_message(
        self,
        candidate_profile: str,
        job_info: str,
        channel: str = "Email",
        **kwargs
    ) -> str:
        """
        Generate personalized candidate outreach
        
        Args:
            candidate_profile: Candidate background
            job_info: Job opportunity details
            channel: Communication channel (Email, LinkedIn, etc.)
            **kwargs: Additional generation parameters
            
        Returns:
            Personalized outreach message
        """
        instruction = f"Create a personalized {channel} outreach message for this candidate"
        context = f"Candidate: {candidate_profile}\n\nOpportunity: {job_info}"
        
        return self.generate(
            instruction=instruction,
            task_type=TaskType.ENGAGEMENT,
            context=context,
            **kwargs
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Example Usage
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Example usage of Vetta AI for different recruiting tasks"""
    
    # Initialize Vetta AI
    vetta = VettaAI()
    
    print("\n" + "="*80)
    print("VETTA AI v4 - Recruiting Intelligence Demo")
    print("="*80)
    
    # ──────────────────────────────────────────────────────────────────────
    # Example 1: Interview Assessment
    # ──────────────────────────────────────────────────────────────────────
    print("\n📋 Example 1: Interview Assessment")
    print("-" * 80)
    
    response = vetta.interview(
        question="Assess this candidate's technical skills for a Senior Python Developer role.",
        candidate_info="5 years Python, Django expert, built scalable APIs, open source contributor",
        job_requirements="Senior Python Developer (Python, AWS, System Design)",
        max_new_tokens=256,
        temperature=0.7
    )
    print(response)
    
    # ──────────────────────────────────────────────────────────────────────
    # Example 2: Candidate Quality Assessment
    # ──────────────────────────────────────────────────────────────────────
    print("\n\n📊 Example 2: Candidate Quality Assessment")
    print("-" * 80)
    
    response = vetta.assess_candidate(
        candidate_profile="Frontend developer, 3 years React, TypeScript, built 5+ production apps",
        job_requirements="Senior Frontend Engineer - React, TypeScript, Design Systems",
        max_new_tokens=256
    )
    print(response)
    
    # ──────────────────────────────────────────────────────────────────────
    # Example 3: Boolean Search Query Generation
    # ──────────────────────────────────────────────────────────────────────
    print("\n\n🔍 Example 3: Boolean Search Query")
    print("-" * 80)
    
    response = vetta.generate_boolean_query(
        job_description="Looking for Machine Learning Engineer with Python, TensorFlow, MLOps experience",
        platform="LinkedIn",
        max_new_tokens=128
    )
    print(response)
    
    # ──────────────────────────────────────────────────────────────────────
    # Example 4: Personalized Outreach
    # ──────────────────────────────────────────────────────────────────────
    print("\n\n📧 Example 4: Personalized Outreach")
    print("-" * 80)
    
    response = vetta.create_outreach_message(
        candidate_profile="Senior DevOps engineer at tech startup, Kubernetes expert, speaks at conferences",
        job_info="Lead DevOps Engineer role at fast-growing fintech, Kubernetes infrastructure",
        channel="LinkedIn",
        max_new_tokens=200
    )
    print(response)
    
    # ──────────────────────────────────────────────────────────────────────
    # Example 5: Dynamic Chat with Custom Task
    # ──────────────────────────────────────────────────────────────────────
    print("\n\n💬 Example 5: Market Intelligence")
    print("-" * 80)
    
    response = vetta.chat(
        instruction="What's the salary range for Senior Software Engineers in San Francisco?",
        task_type=TaskType.MARKET,
        max_new_tokens=200
    )
    print(response)
    
    print("\n" + "="*80)
    print("✅ Demo Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
