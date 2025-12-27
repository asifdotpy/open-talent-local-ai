# Vetta AI v4 - Interview Service Integration Example
# How to integrate the fine-tuned model into your existing interview service

"""
INTEGRATION STEPS:

1. Install dependencies:
   pip install -r requirements-vetta.txt

2. Add VettaService to interview service:
   Copy microservices/shared/vetta_service.py to your service

3. Update your interview endpoint to use Vetta AI

4. Test with sample requests

5. Deploy and monitor
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE: FastAPI Interview Service Integration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Import Vetta AI
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

sys.path.append("/home/asif1/open-talent-platform")
from microservices.shared.vetta_service import VettaService

# Initialize FastAPI app
app = FastAPI(title="OpenTalent Interview Service", version="4.0.0")

# Initialize Vetta AI (do this ONCE at startup)
print("🚀 Loading Vetta AI v4 model...")
vetta = VettaService(model_path="asifdotpy/vetta-granite-2b-lora-v4")
print("✅ Vetta AI ready!")

# ──────────────────────────────────────────────────────────────────────────
# Request/Response Models
# ──────────────────────────────────────────────────────────────────────────


class InterviewQuestion(BaseModel):
    """Request model for interview questions"""

    candidate_id: str
    job_id: str
    candidate_info: str
    job_requirements: str
    question_type: str = "technical_assessment"  # or "behavioral", "closing", etc.


class CandidateAssessment(BaseModel):
    """Request model for candidate assessment"""

    candidate_id: str
    job_id: str
    candidate_profile: str
    job_requirements: str
    interview_responses: Optional[list[str]] = None


class InterviewResponse(BaseModel):
    """Response model"""

    candidate_id: str
    job_id: str
    response: str
    metadata: dict = {}


# ──────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "OpenTalent Interview Service",
        "version": "4.0.0",
        "model": "Vetta AI v4 (Granite 3.0 2B LoRA)",
        "status": "ready",
    }


@app.post("/interview/ask", response_model=InterviewResponse)
async def ask_interview_question(request: InterviewQuestion):
    """
    Generate interview question for candidate

    Example request:
    {
        "candidate_id": "cand_123",
        "job_id": "job_456",
        "candidate_info": "5 years Python, Django expert, AWS certified",
        "job_requirements": "Senior Backend Engineer - Python, AWS, Microservices",
        "question_type": "technical_assessment"
    }
    """
    try:
        # Build instruction based on question type
        question_prompts = {
            "technical_assessment": "Generate a technical interview question to assess this candidate's skills",
            "behavioral": "Generate a behavioral interview question for this candidate",
            "system_design": "Generate a system design question appropriate for this role",
            "closing": "Generate appropriate closing questions for the interview",
        }

        instruction = question_prompts.get(
            request.question_type, "Generate an appropriate interview question"
        )

        context = f"Candidate: {request.candidate_info}\n\nRole: {request.job_requirements}"

        # Generate using Vetta AI
        response = vetta.generate(
            instruction=instruction, context=context, max_tokens=256, temperature=0.7
        )

        return InterviewResponse(
            candidate_id=request.candidate_id,
            job_id=request.job_id,
            response=response,
            metadata={"question_type": request.question_type},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")


@app.post("/interview/assess", response_model=InterviewResponse)
async def assess_candidate(request: CandidateAssessment):
    """
    Assess candidate fit and generate comprehensive evaluation

    Example request:
    {
        "candidate_id": "cand_123",
        "job_id": "job_456",
        "candidate_profile": "5 years Python, Django expert, AWS certified, built scalable APIs",
        "job_requirements": "Senior Backend Engineer - Python, AWS, Microservices, System Design",
        "interview_responses": [
            "Described microservices architecture with message queues",
            "Explained database scaling with sharding and caching"
        ]
    }
    """
    try:
        # Build instruction
        instruction = (
            "Assess this candidate's fit for the role and provide comprehensive evaluation"
        )

        # Build context
        context_parts = [
            f"Candidate Profile: {request.candidate_profile}",
            f"Role Requirements: {request.job_requirements}",
        ]

        if request.interview_responses:
            responses_text = "\n".join([f"- {r}" for r in request.interview_responses])
            context_parts.append(f"Interview Responses:\n{responses_text}")

        context = "\n\n".join(context_parts)

        # Generate assessment using Vetta AI
        assessment = vetta.generate(
            instruction=instruction, context=context, max_tokens=512, temperature=0.7
        )

        return InterviewResponse(
            candidate_id=request.candidate_id,
            job_id=request.job_id,
            response=assessment,
            metadata={
                "assessment_type": "comprehensive",
                "num_responses": len(request.interview_responses)
                if request.interview_responses
                else 0,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing candidate: {str(e)}")


@app.post("/interview/evaluate-response")
async def evaluate_response(
    candidate_id: str, job_id: str, question: str, candidate_response: str, job_requirements: str
):
    """
    Evaluate a candidate's response to a specific interview question

    Example request:
    {
        "candidate_id": "cand_123",
        "job_id": "job_456",
        "question": "How would you design a scalable microservices architecture?",
        "candidate_response": "I would use Docker containers, Kubernetes orchestration, message queues for async communication...",
        "job_requirements": "Senior Backend Engineer - Microservices, System Design"
    }
    """
    try:
        instruction = "Evaluate this candidate's interview response"
        context = f"""Question: {question}

Candidate Response: {candidate_response}

Role Requirements: {job_requirements}"""

        evaluation = vetta.generate(
            instruction=instruction, context=context, max_tokens=300, temperature=0.7
        )

        return InterviewResponse(
            candidate_id=candidate_id,
            job_id=job_id,
            response=evaluation,
            metadata={"evaluation_type": "response_assessment"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating response: {str(e)}")


# ──────────────────────────────────────────────────────────────────────────
# Additional Recruiting Endpoints
# ──────────────────────────────────────────────────────────────────────────


@app.post("/sourcing/boolean-query")
async def generate_boolean_query(job_description: str, platform: str = "LinkedIn"):
    """Generate boolean search query for sourcing"""
    try:
        instruction = f"Generate a {platform} boolean search query for this role"
        context = f"Job Description:\n{job_description}"

        query = vetta.generate(
            instruction=instruction, context=context, max_tokens=128, temperature=0.5
        )

        return {"platform": platform, "query": query}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/engagement/outreach")
async def generate_outreach(candidate_profile: str, job_info: str, channel: str = "Email"):
    """Generate personalized candidate outreach"""
    try:
        instruction = f"Create a personalized {channel} outreach message for this candidate"
        context = f"Candidate: {candidate_profile}\n\nOpportunity: {job_info}"

        message = vetta.generate(
            instruction=instruction, context=context, max_tokens=200, temperature=0.8
        )

        return {"channel": channel, "message": message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────
# Run Server
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "interview_service_example:app",
        host="0.0.0.0",
        port=8004,
        reload=False,  # Set to True for development
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTING THE SERVICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
# Start the service
python interview_service_example.py

# Test with curl
curl -X POST "http://localhost:8004/interview/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "cand_123",
    "job_id": "job_456",
    "candidate_profile": "5 years Python, Django expert, AWS certified",
    "job_requirements": "Senior Backend Engineer - Python, AWS, Microservices"
  }'

# Or with Python requests
import requests

response = requests.post(
    "http://localhost:8004/interview/assess",
    json={
        "candidate_id": "cand_123",
        "job_id": "job_456",
        "candidate_profile": "5 years Python, Django expert, AWS certified",
        "job_requirements": "Senior Backend Engineer - Python, AWS, Microservices"
    }
)

print(response.json())
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DEPLOYMENT NOTES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
Production Deployment Checklist:

1. Environment Setup:
   - Install CUDA drivers if using GPU
   - Install Python 3.10+
   - pip install -r requirements-vetta.txt

2. Model Caching:
   - Pre-download model on deployment:
     python -c "from microservices.shared.vetta_service import VettaService; VettaService()"

3. Resource Allocation:
   - GPU: 4-8GB VRAM minimum (T4, RTX 3060, or better)
   - CPU: 4+ cores, 8GB+ RAM
   - Disk: 5GB for model files

4. Performance Tuning:
   - Use GPU for production (10x faster)
   - Set worker count based on GPU memory
   - Monitor inference latency
   - Cache common queries if applicable

5. Monitoring:
   - Log inference times
   - Track GPU memory usage
   - Monitor response quality
   - Alert on errors

6. Scaling:
   - Horizontal: Multiple service instances with load balancer
   - Vertical: Larger GPU (A100, RTX 4090)
   - Batch processing: For bulk assessments
"""
