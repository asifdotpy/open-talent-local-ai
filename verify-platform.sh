#!/bin/bash

# OpenTalent Platform Verifier
# Programmatically validates stabilization, data integrity, and environmental parity.

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}==================================================${NC}"
echo -e "${CYAN}🔍 OpenTalent Platform Verification Scan${NC}"
echo -e "${CYAN}==================================================${NC}"

FAILURES=0

# 1. Service Connectivity Audit
echo -e "\n${YELLOW}1. Connectivity Audit (15 Services)${NC}"
SERVICES=(
    "scout-service:8000" "user-service:8001" "conversation-service:8002"
    "voice-service:8003" "avatar-service:8004" "granite-interview-service:8005"
    "candidate-service:8006" "analytics-service:8007" "desktop-integration-service:8009"
    "security-service:8010" "notification-service:8011" "ai-auditing-service:8012"
    "explainability-service:8013" "interview-service:8014" "project-service:8015"
)

for s in "${SERVICES[@]}"; do
    name="${s%:*}"
    port="${s#*:}"
    if curl -s --connect-timeout 5 "http://localhost:$port/health" &> /dev/null || \
       curl -s --connect-timeout 5 "http://localhost:$port/" &> /dev/null; then
        echo -e "  [${GREEN}PASS${NC}] $name (Port $port)"
    else
        echo -e "  [${RED}FAIL${NC}] $name (Port $port) - Service Offline"
        FAILURES=$((FAILURES + 1))
    fi
done

# 2. Data Integrity Audit (Project Service - No Mocks)
echo -e "\n${YELLOW}2. Data Integrity Audit (project-service)${NC}"
PROJECT_RESP=$(curl -s "http://localhost:8015/jobs/project-001")
if [[ "$PROJECT_RESP" == *"Senior AI Architect"* ]]; then
    echo -e "  [${GREEN}PASS${NC}] project-service returning real database record (project-001)"
else
    echo -e "  [${RED}FAIL${NC}] project-service failed to return seeded DB record"
    FAILURES=$((FAILURES + 1))
fi

# 3. Security Audit (Candidate Service - Mock Rejection)
echo -e "\n${YELLOW}3. Mock Rejection Audit (candidate-service)${NC}"
CANDIDATE_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8006/api/v1/candidate-profiles/mock-id")
if [ "$CANDIDATE_CODE" == "404" ] || [ "$CANDIDATE_CODE" == "503" ]; then
    echo -e "  [${GREEN}PASS${NC}] candidate-service correctly rejected legacy mock-id (Code: $CANDIDATE_CODE)"
else
    echo -e "  [${RED}FAIL${NC}] candidate-service still responding to mock-id (Code: $CANDIDATE_CODE)"
    FAILURES=$((FAILURES + 1))
fi

# 4. Environmental Standardization Audit
echo -e "\n${YELLOW}4. Environmental Standardization Audit${NC}"
# Check user-service metadata
USER_NAME=$(curl -s "http://localhost:8001/health" | grep -o "user" || echo "missing")
if [ "$USER_NAME" == "user" ]; then
    echo -e "  [${GREEN}PASS${NC}] user-service metadata verified"
else
    echo -e "  [${RED}FAIL${NC}] user-service metadata inconsistency"
    FAILURES=$((FAILURES + 1))
fi

echo -e "\n${CYAN}==================================================${NC}"
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ PLATFORM VERIFIED: All stabilization checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ VERIFICATION FAILED: $FAILURES issue(s) detected.${NC}"
    exit 1
fi
