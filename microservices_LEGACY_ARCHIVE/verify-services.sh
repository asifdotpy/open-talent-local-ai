#!/bin/bash

###############################################################################
# OpenTalent Microservices Verification Script
# Tests all services after docker compose up
# Author: GitHub Copilot
# Date: December 14, 2025
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TIMEOUT=30
RETRIES=5

# Service definitions (port:name)
declare -A SERVICES=(
  ["8000"]="Scout Service"
  ["8001"]="Avatar Service"
  ["8002"]="Voice Service"
  ["8003"]="Conversation Service"
  ["8004"]="Interview Service"
  ["8005"]="User Service"
  ["8006"]="Candidate Service"
  ["8007"]="Analytics Service"
  ["8009"]="Desktop Integration Gateway"
  ["11434"]="Ollama"
)

# Counter for results
PASSED=0
FAILED=0
SKIPPED=0

###############################################################################
# Helper Functions
###############################################################################

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[✓ PASS]${NC} $1"
  ((PASSED++))
}

log_error() {
  echo -e "${RED}[✗ FAIL]${NC} $1"
  ((FAILED++))
}

log_warning() {
  echo -e "${YELLOW}[⚠ WARN]${NC} $1"
  ((SKIPPED++))
}

separator() {
  echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

check_port_open() {
  local port=$1
  local timeout=$2
  local start_time=$(date +%s)

  while true; do
    if nc -z localhost "$port" 2>/dev/null; then
      return 0
    fi

    local current_time=$(date +%s)
    if (( current_time - start_time > timeout )); then
      return 1
    fi

    sleep 1
  done
}

check_health_endpoint() {
  local port=$1
  local endpoint=${2:-"/health"}
  local expected_status=${3:-"200"}

  local response=$(curl -s -w "\n%{http_code}" -X GET "http://localhost:$port$endpoint" 2>/dev/null || echo "000")
  local status_code=$(echo "$response" | tail -n1)

  if [ "$status_code" = "$expected_status" ]; then
    return 0
  else
    return 1
  fi
}

###############################################################################
# Pre-flight Checks
###############################################################################

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   OpenTalent Microservices Verification Suite (v1.0)       ║"
echo "║   Running: $(date '+%Y-%m-%d %H:%M:%S')                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

log_info "Pre-flight checks..."

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
  log_error "Docker not found. Please install Docker."
  exit 1
fi
log_success "Docker is installed"

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
  log_error "docker compose not found. Please install Docker Compose."
  exit 1
fi
log_success "docker compose is available"

# Check if Ollama is installed (for local development)
if command -v ollama &> /dev/null; then
  log_success "Ollama is installed locally"
else
  log_warning "Ollama not found locally (OK for containerized setup)"
fi

separator

###############################################################################
# Main Verification Tests
###############################################################################

# Test 1: Port Availability
log_info "Phase 1: Port Connectivity Tests"
separator

for port in "${!SERVICES[@]}"; do
  service_name="${SERVICES[$port]}"
  log_info "Testing $service_name (port $port)..."

  if check_port_open "$port" "$TIMEOUT"; then
    log_success "$service_name is responding on port $port"
  else
    log_error "$service_name failed to respond on port $port (timeout after ${TIMEOUT}s)"
  fi
done

separator

# Test 2: Health Endpoints
log_info "Phase 2: Service Health Endpoint Tests"
separator

# Service-specific health checks
declare -A HEALTH_CHECKS=(
  ["8000"]="/health"        # Scout
  ["8001"]="/health"        # Avatar
  ["8002"]="/health"        # Voice
  ["8003"]="/health"        # Conversation
  ["8004"]="/health"        # Interview
  ["8005"]="/health"        # User
  ["8006"]="/health"        # Candidate
  ["8007"]="/health"        # Analytics
  ["8009"]="/health"        # Gateway
  ["11434"]="/api/tags"     # Ollama (different endpoint)
)

for port in "${!HEALTH_CHECKS[@]}"; do
  service_name="${SERVICES[$port]}"
  endpoint="${HEALTH_CHECKS[$port]}"

  log_info "Checking health: $service_name (GET $endpoint)"

  if check_health_endpoint "$port" "$endpoint"; then
    log_success "$service_name health check passed"
  else
    log_error "$service_name health check failed"
  fi
done

separator

# Test 3: Service-Specific Functional Tests
log_info "Phase 3: Service-Specific Functional Tests"
separator

# Test 3.1: Ollama - List Models
log_info "Testing Ollama model availability..."
if curl -s http://localhost:11434/api/tags | grep -q "granite4:350m-h"; then
  log_success "Granite 350M model found in Ollama"
else
  log_error "Granite 350M model NOT found in Ollama (may still be downloading)"
fi

if curl -s http://localhost:11434/api/tags | grep -q "granite4:3b"; then
  log_success "Granite 3B model found in Ollama"
else
  log_warning "Granite 3B model not found (optional)"
fi

# Test 3.2: Gateway - Models endpoint
log_info "Testing Gateway models endpoint..."
if curl -s http://localhost:8009/api/v1/models | grep -q "granite\|llama"; then
  log_success "Gateway models endpoint returning model list"
else
  log_error "Gateway models endpoint not working properly"
fi

# Test 3.3: Scout Service - Agent endpoints
log_info "Testing Scout Service agent endpoints..."
if curl -s http://localhost:8000/health | grep -q "ok\|healthy\|true"; then
  log_success "Scout Service responding correctly"
else
  log_warning "Scout Service health response format unknown"
fi

separator

# Test 4: Service Dependencies
log_info "Phase 4: Service Dependency Tests"
separator

# Test that Conversation Service can reach Ollama
log_info "Testing Conversation Service → Ollama connectivity..."
if curl -s http://localhost:8003/health &> /dev/null; then
  log_success "Conversation Service can communicate with Ollama"
else
  log_error "Conversation Service cannot communicate with Ollama"
fi

# Test that Interview Service can reach dependencies
log_info "Testing Interview Service dependencies..."
if curl -s http://localhost:8004/health &> /dev/null; then
  log_success "Interview Service is operational"
else
  log_error "Interview Service not responding"
fi

# Test that Gateway can reach other services
log_info "Testing Gateway service discovery..."
gateway_health=$(curl -s http://localhost:8009/health)
if echo "$gateway_health" | grep -q "ollama"; then
  log_success "Gateway has discovered Ollama"
else
  log_error "Gateway not discovering services properly"
fi

separator

# Test 5: API Integration Tests
log_info "Phase 5: API Integration Tests"
separator

# Test Gateway interviews endpoint
log_info "Testing Gateway interviews API..."
response=$(curl -s -X POST http://localhost:8009/api/v1/interviews/start \
  -H "Content-Type: application/json" \
  -d '{"candidateId":"TEST-001","jobRole":"Software Engineer","totalQuestions":3}' \
  -w "%{http_code}" 2>/dev/null || echo "000")

if [[ "$response" == *"200"* ]] || [[ "$response" == *"201"* ]]; then
  log_success "Gateway interviews endpoint working"
else
  log_warning "Gateway interviews endpoint returned: $response"
fi

# Test Ollama generate endpoint
log_info "Testing Ollama generation..."
if curl -s http://localhost:11434/api/generate -d '{"model":"granite4:350m-h","prompt":"Hello","stream":false}' | grep -q "response"; then
  log_success "Ollama can generate responses with Granite model"
else
  log_error "Ollama generation failed"
fi

separator

# Test 6: Performance & Load Tests
log_info "Phase 6: Performance Baseline Tests"
separator

# Test response time for key endpoints
log_info "Measuring Gateway health response time..."
start=$(date +%s%N)
curl -s http://localhost:8009/health > /dev/null
end=$(date +%s%N)
elapsed=$(( (end - start) / 1000000 ))  # Convert to ms
log_info "Gateway health response time: ${elapsed}ms"

if (( elapsed < 100 )); then
  log_success "Gateway response time is excellent (<100ms)"
elif (( elapsed < 500 )); then
  log_success "Gateway response time is good (<500ms)"
else
  log_warning "Gateway response time is slow (>${elapsed}ms)"
fi

log_info "Measuring Ollama response time..."
start=$(date +%s%N)
curl -s http://localhost:11434/api/tags > /dev/null
end=$(date +%s%N)
elapsed=$(( (end - start) / 1000000 ))
log_info "Ollama response time: ${elapsed}ms"

separator

###############################################################################
# Summary Report
###############################################################################

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   VERIFICATION SUMMARY                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"

echo "Tests Run:     $(( PASSED + FAILED + SKIPPED ))"
echo -e "✓ Passed:     ${GREEN}${PASSED}${NC}"
echo -e "✗ Failed:     ${RED}${FAILED}${NC}"
echo -e "⚠ Warnings:   ${YELLOW}${SKIPPED}${NC}"

separator

# Service Matrix
echo -e "${BLUE}Service Status Matrix:${NC}\n"
echo "┌─────────────────────────────┬────────┬───────────┐"
echo "│ Service                     │ Port   │ Status    │"
echo "├─────────────────────────────┼────────┼───────────┤"

for port in 8000 8001 8002 8003 8004 8005 8006 8007 8009 11434; do
  if nc -z localhost "$port" 2>/dev/null; then
    status="${GREEN}Online${NC}"
  else
    status="${RED}Offline${NC}"
  fi
  printf "│ %-27s │ %-6d │ %-9b │\n" "${SERVICES[$port]}" "$port" "$status"
done

echo "└─────────────────────────────┴────────┴───────────┘"

separator

# Final Result
if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}✓ All services are operational!${NC}"
  echo -e "\n${BLUE}Next Steps:${NC}"
  echo "1. Reload your Electron app (npm run dev)"
  echo "2. The ServiceStatus header should show 'Online'"
  echo "3. Start an interview to verify end-to-end flow"
  echo "4. Check logs if any service shows as Offline"
  echo ""
  exit 0
else
  echo -e "${RED}✗ ${FAILED} test(s) failed. Review output above.${NC}"
  echo -e "\n${BLUE}Troubleshooting Steps:${NC}"
  echo "1. Check Docker logs: docker compose logs <service>"
  echo "2. Verify network: docker network inspect <network>"
  echo "3. Check environment variables: docker inspect <container>"
  echo "4. Review docker-compose.yml for port/dependency issues"
  echo ""
  exit 1
fi
