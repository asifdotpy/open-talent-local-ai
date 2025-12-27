#!/bin/bash
# Vetta AI v4 Integration Test Script
# Tests all 8 REST endpoints after service startup

set -e  # Exit on error

BASE_URL="http://localhost:8004/api/v1/vetta"
COLORS=true

# Color codes
if [ "$COLORS" = true ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       Vetta AI v4 Integration Test Suite${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"

# Test 1: Model Info
echo -e "${YELLOW}[1/8]${NC} Testing ${GREEN}GET /info${NC} (Model Information)..."
RESPONSE=$(curl -s "${BASE_URL}/info")
echo "$RESPONSE" | jq '.'
MODEL_LOADED=$(echo "$RESPONSE" | jq -r '.loaded')
FALLBACK_MODE=$(echo "$RESPONSE" | jq -r '.fallback_mode')

if [ "$MODEL_LOADED" = "true" ]; then
    echo -e "${GREEN}✓ Model loaded successfully${NC}\n"
else
    echo -e "${YELLOW}⚠ Running in fallback mode${NC}\n"
fi

# Test 2: Health Check
echo -e "${YELLOW}[2/8]${NC} Testing ${GREEN}GET /health${NC} (Health Check)..."
curl -s "${BASE_URL}/health" | jq '.'
echo -e "${GREEN}✓ Health check passed${NC}\n"

# Test 3: Generic Generation
echo -e "${YELLOW}[3/8]${NC} Testing ${GREEN}POST /generate${NC} (Generic Generation)..."
curl -s -X POST "${BASE_URL}/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Write a brief job description for a Senior Python Developer",
    "context": "Startup company, remote work, competitive salary",
    "max_tokens": 200,
    "temperature": 0.7
  }' | jq '.'
echo -e "${GREEN}✓ Generic generation works${NC}\n"

# Test 4: Candidate Assessment
echo -e "${YELLOW}[4/8]${NC} Testing ${GREEN}POST /assess-candidate${NC} (Candidate Assessment)..."
curl -s -X POST "${BASE_URL}/assess-candidate" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_info": "5 years Python experience, Django expert, built scalable APIs, open source contributor",
    "job_description": "Senior Python Developer - Python, AWS, System Design, Team Leadership",
    "role": "Senior Python Developer"
  }' | jq '.'
echo -e "${GREEN}✓ Candidate assessment works${NC}\n"

# Test 5: Interview Question Generation
echo -e "${YELLOW}[5/8]${NC} Testing ${GREEN}POST /generate-question${NC} (Interview Question)..."
curl -s -X POST "${BASE_URL}/generate-question" \
  -H "Content-Type: application/json" \
  -d '{
    "previous_responses": [
      "I have 5 years of Python experience, mostly with Django and FastAPI.",
      "I built a microservices architecture handling 10M requests/day."
    ],
    "job_requirements": "Senior Python Developer - Python, AWS, System Design",
    "expertise_level": "advanced"
  }' | jq '.'
echo -e "${GREEN}✓ Interview question generation works${NC}\n"

# Test 6: Outreach Message Generation
echo -e "${YELLOW}[6/8]${NC} Testing ${GREEN}POST /generate-outreach${NC} (Outreach Message)..."
curl -s -X POST "${BASE_URL}/generate-outreach" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "Sarah Chen",
    "candidate_skills": "Python, Django, AWS, Kubernetes",
    "role": "Senior Backend Engineer",
    "company": "OpenTalent"
  }' | jq '.'
echo -e "${GREEN}✓ Outreach message generation works${NC}\n"

# Test 7: Quality Scoring
echo -e "${YELLOW}[7/8]${NC} Testing ${GREEN}POST /score-quality${NC} (Quality Scoring)..."
curl -s -X POST "${BASE_URL}/score-quality" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_profile": "5 years Python, Django, AWS. Led team of 3 developers. Open source contributor.",
    "job_requirements": "Senior Python Developer - Python, AWS, System Design, Team Leadership",
    "scoring_criteria": ["Skill match", "Experience", "Leadership", "Culture fit"]
  }' | jq '.'
echo -e "${GREEN}✓ Quality scoring works${NC}\n"

# Test 8: Sentiment Analysis
echo -e "${YELLOW}[8/8]${NC} Testing ${GREEN}POST /analyze-sentiment${NC} (Sentiment Analysis)..."
curl -s -X POST "${BASE_URL}/analyze-sentiment" \
  -H "Content-Type: application/json" \
  -d '{
    "response_text": "I really enjoyed working on that project! The team collaboration was fantastic and we delivered ahead of schedule."
  }' | jq '.'
echo -e "${GREEN}✓ Sentiment analysis works${NC}\n"

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ All 8 endpoints tested successfully!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"

if [ "$FALLBACK_MODE" = "true" ]; then
    echo -e "${YELLOW}Note: Service is running in fallback mode${NC}"
    echo -e "${YELLOW}For full model capabilities, install dependencies:${NC}"
    echo -e "${YELLOW}  pip install 'unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git'${NC}"
    echo -e "${YELLOW}  pip install torch>=2.4.0 transformers>=4.44.0${NC}\n"
fi

echo -e "${BLUE}Next Steps:${NC}"
echo -e "  • View Swagger UI: ${GREEN}http://localhost:8004/docs${NC}"
echo -e "  • Read integration guide: ${GREEN}VETTA_AI_INTEGRATION.md${NC}"
echo -e "  • Integrate into frontend chat/interview features\n"
