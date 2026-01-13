#!/bin/bash
################################################################################
# OpenTalent Release Verification Script
# Version: 1.0.0
# Purpose: Automated verification for v1.0.0-mvp release
################################################################################

set -e  # Exit on any error

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║         OpenTalent v1.0.0 Release Verification Suite                  ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=4
PASSED=0
FAILED=0

# Function to print stage header
print_stage() {
    local stage_num=$1
    local stage_name=$2
    echo ""
    echo "${BLUE}[$stage_num/$TOTAL_CHECKS]${NC} $stage_name"
    echo "─────────────────────────────────────────────────────────────────────────"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    PASSED=$((PASSED + 1))
}

# Function to print error and exit
print_error() {
    echo -e "${RED}❌ $1${NC}"
    FAILED=$((FAILED + 1))
    exit 1
}

# Stage 0: Environment Check
print_stage 0 "Checking Environment Configuration"
if [ -f ".env.shared" ]; then
    print_success ".env.shared exists"
else
    print_error ".env.shared NOT found. Please run setup."
fi

# Stage 1: Desktop App Compilation
print_stage 1 "Checking Desktop App TypeScript Compilation"

cd desktop-app || print_error "desktop-app directory not found"

if [ ! -d "node_modules" ]; then
    echo "${YELLOW}⚠️  node_modules not found. Installing dependencies...${NC}"
    npm install
fi

if [ ! -f "node_modules/.bin/tsc" ]; then
    print_error "TypeScript compiler not found. Run 'npm install' in desktop-app/"
fi

echo "Running: tsc --noEmit"
if ./node_modules/.bin/tsc --noEmit; then
    print_success "Desktop TypeScript compilation passed (0 errors)"
else
    print_error "Desktop TypeScript compilation failed"
fi

# Stage 2: Desktop App Tests
print_stage 2 "Running Desktop App Test Suite"

if [ ! -f "node_modules/.bin/jest" ]; then
    print_error "Jest not found. Run 'npm install' in desktop-app/"
fi

echo "Running: jest --watchAll=false --passWithNoTests"
if ./node_modules/.bin/jest --watchAll=false --passWithNoTests; then
    print_success "Desktop test suite passed"
else
    print_error "Desktop test suite failed"
fi

# Return to project root
cd ..

# Stage 3: Backend Gateway Health & Service Registration
print_stage 3 "Verifying API Gateway & Service Discovery"

GATEWAY_DIR="services/desktop-integration-service"
if [ ! -d "$GATEWAY_DIR" ]; then
    print_error "Gateway directory not found: $GATEWAY_DIR"
fi

echo "Checking scout-service registration..."
if grep -q "scout-service" "$GATEWAY_DIR/app/core/service_discovery.py"; then
    print_success "scout-service is registered in service discovery"
else
    print_error "scout-service NOT found in service discovery"
fi

echo "Checking voice-service registration..."
if grep -q "voice-service" "$GATEWAY_DIR/app/core/service_discovery.py"; then
    print_success "voice-service is registered in service discovery"
else
    print_error "voice-service NOT found in service discovery"
fi

echo "Checking gateway routes are exposed..."
if grep -q "/api/v1/scout/search" "$GATEWAY_DIR/app/main.py"; then
    print_success "Scout search endpoint is exposed via gateway"
else
    print_error "Scout search endpoint NOT exposed via gateway"
fi

if grep -q "/api/v1/voice/transcribe" "$GATEWAY_DIR/app/main.py"; then
    print_success "Voice transcribe endpoint is exposed via gateway"
else
    print_error "Voice transcribe endpoint NOT exposed via gateway"
fi

# Stage 4: Schema Verification
print_stage 4 "Verifying Critical Service Schemas"

echo "Checking Security Service schemas..."
if [ -f "services/security-service/schemas.py" ]; then
    print_success "Security Service schemas.py exists"
else
    print_error "Security Service schemas.py NOT found"
fi

echo "Checking Notification Service schemas..."
if [ -f "services/notification-service/schemas.py" ]; then
    print_success "Notification Service schemas.py exists"
else
    print_error "Notification Service schemas.py NOT found"
fi

# Final Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                    VERIFICATION COMPLETE                               ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "Total Checks: $TOTAL_CHECKS"
echo -e "${GREEN}Passed: $((TOTAL_CHECKS))${NC}"
echo -e "${RED}Failed: 0${NC}"
echo ""
echo -e "${GREEN}🚀 ALL SYSTEMS GO: OpenTalent is ready for v1.0.0 release!${NC}"
echo ""
echo "Next steps:"
echo "  1. Tag the release: git tag v1.0.0-release"
echo "  2. Push the tag: git push origin v1.0.0-release"
echo "  3. Create release notes"
echo ""

exit 0
