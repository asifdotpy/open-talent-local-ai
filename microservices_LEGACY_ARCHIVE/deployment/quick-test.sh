#!/bin/bash

# Quick test script for the hybrid integration
# Run this to validate everything is working before full deployment

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

echo "🧪 Quick Hybrid Integration Test"
echo "================================"

# Test 1: Check if Ollama is running
print_test "Checking Ollama service..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_pass "Ollama is running"
else
    print_fail "Ollama is not running. Please start: 'ollama serve'"
    exit 1
fi

# Test 2: Check if model is available
print_test "Checking Llama model availability..."
if ollama list | grep -q "granite4:350m-h"; then
    print_pass "Llama model is available"
else
    print_fail "Llama model not found. Please run: 'ollama pull granite4:350m-h'"
    exit 1
fi

# Test 3: Run Python integration test
print_test "Running hybrid integration test..."
cd /home/asif/open-talent-platform/open-talent-microservices/open-talent-avatar-service
if python test_hybrid_integration.py; then
    print_pass "Integration test passed"
else
    print_fail "Integration test failed"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
echo "Ready for production deployment."
echo ""
echo "To deploy: ./deploy-hybrid-llm.sh"
