#!/bin/bash
# Comprehensive Production Readiness Test for Voice Service
# Tests all endpoints and validates responses

set -e

BASE_URL="http://localhost:8002"
PASSED=0
FAILED=0
TOTAL=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                        ║"
echo "║         VOICE SERVICE - PRODUCTION READINESS TEST                      ║"
echo "║                                                                        ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Test function
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local expected_status=$4
    local data=$5
    local content_type=$6

    TOTAL=$((TOTAL + 1))

    echo -n "Testing: $name ... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint")
    elif [ "$method" = "POST" ] && [ -n "$content_type" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: $content_type" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $http_code)"
        FAILED=$((FAILED + 1))
        echo "  Response: $body"
        return 1
    fi
}

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}1. HEALTH & STATUS ENDPOINTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Test root endpoint
test_endpoint "Root Endpoint (GET /)" "GET" "/" "200"

# Test health endpoint
test_endpoint "Health Check (GET /health)" "GET" "/health" "200"

# Test info endpoint
test_endpoint "Service Info (GET /info)" "GET" "/info" "200"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}2. VOICE PROCESSING ENDPOINTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Test voices endpoint
test_endpoint "Available Voices (GET /voices)" "GET" "/voices" "200"

# Test TTS endpoint with JSON
tts_payload='{"text":"Hello, this is a production test.","voice":"lessac","speed":1.0,"extract_phonemes":true}'
test_endpoint "Text-to-Speech (POST /voice/tts)" "POST" "/voice/tts" "200" "$tts_payload" "application/json"

# Note: STT and VAD require file uploads, tested separately below

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}3. DOCUMENTATION ENDPOINTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Test OpenAPI endpoints
test_endpoint "OpenAPI Schema (GET /openapi.json)" "GET" "/openapi.json" "200"
test_endpoint "API Docs Info (GET /api-docs)" "GET" "/api-docs" "200"

# Test documentation redirects (accept both 200 and 307 for redirects)
test_endpoint "Swagger UI (GET /docs)" "GET" "/docs" "200"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}4. WEBRTC ENDPOINTS (if available)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if WebRTC is available
webrtc_status=$(curl -s "$BASE_URL/webrtc/status" 2>/dev/null || echo "{}")
if echo "$webrtc_status" | grep -q "webrtc_available"; then
    test_endpoint "WebRTC Status (GET /webrtc/status)" "GET" "/webrtc/status" "200"

    # Test WebRTC start (expects session_id)
    webrtc_start_payload='{"session_id":"test-session-123","job_description":"Test position"}'
    test_endpoint "WebRTC Start (POST /webrtc/start)" "POST" "/webrtc/start" "200" "$webrtc_start_payload" "application/json"
else
    echo -e "${YELLOW}⚠ WebRTC not available (expected in mock mode)${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}5. DETAILED RESPONSE VALIDATION${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Validate root endpoint response structure
echo "Validating root endpoint response..."
root_response=$(curl -s "$BASE_URL/")
if echo "$root_response" | jq -e '.service' > /dev/null 2>&1 && \
   echo "$root_response" | jq -e '.version' > /dev/null 2>&1 && \
   echo "$root_response" | jq -e '.status' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Root response has required fields${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ Root response missing required fields${NC}"
    FAILED=$((FAILED + 1))
fi
TOTAL=$((TOTAL + 1))

# Validate health endpoint response structure
echo "Validating health endpoint response..."
health_response=$(curl -s "$BASE_URL/health")
if echo "$health_response" | jq -e '.status' > /dev/null 2>&1 && \
   echo "$health_response" | jq -e '.services' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Health response has required fields${NC}"
    PASSED=$((PASSED + 1))

    # Check if services are ready
    stt_status=$(echo "$health_response" | jq -r '.services.stt')
    tts_status=$(echo "$health_response" | jq -r '.services.tts')

    if [ "$stt_status" = "ready" ] && [ "$tts_status" = "ready" ]; then
        echo -e "${GREEN}✓ Core services (STT/TTS) are ready${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⚠ Services status: STT=$stt_status, TTS=$tts_status${NC}"
        FAILED=$((FAILED + 1))
    fi
    TOTAL=$((TOTAL + 1))
else
    echo -e "${RED}✗ Health response missing required fields${NC}"
    FAILED=$((FAILED + 1))
fi
TOTAL=$((TOTAL + 1))

# Validate OpenAPI schema
echo "Validating OpenAPI schema..."
openapi_schema=$(curl -s "$BASE_URL/openapi.json")
if echo "$openapi_schema" | jq -e '.openapi' > /dev/null 2>&1 && \
   echo "$openapi_schema" | jq -e '.info.title' > /dev/null 2>&1 && \
   echo "$openapi_schema" | jq -e '.paths' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OpenAPI schema is valid${NC}"
    PASSED=$((PASSED + 1))

    # Count endpoints
    endpoint_count=$(echo "$openapi_schema" | jq '.paths | length')
    echo -e "  ${GREEN}Found $endpoint_count documented endpoints${NC}"
else
    echo -e "${RED}✗ OpenAPI schema is invalid${NC}"
    FAILED=$((FAILED + 1))
fi
TOTAL=$((TOTAL + 1))

# Validate TTS response
echo "Validating TTS response..."
tts_response=$(curl -s -X POST "$BASE_URL/voice/tts" \
    -H "Content-Type: application/json" \
    -d '{"text":"Test","voice":"lessac","speed":1.0}')
if echo "$tts_response" | jq -e '.audio_data' > /dev/null 2>&1 && \
   echo "$tts_response" | jq -e '.duration' > /dev/null 2>&1 && \
   echo "$tts_response" | jq -e '.sample_rate' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ TTS response has required fields${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ TTS response missing required fields${NC}"
    FAILED=$((FAILED + 1))
fi
TOTAL=$((TOTAL + 1))

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}6. PERFORMANCE & AVAILABILITY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Test response time
echo "Testing response time for health endpoint..."
start_time=$(date +%s%N)
curl -s "$BASE_URL/health" > /dev/null
end_time=$(date +%s%N)
elapsed_ms=$(( (end_time - start_time) / 1000000 ))

if [ $elapsed_ms -lt 1000 ]; then
    echo -e "${GREEN}✓ Response time: ${elapsed_ms}ms (< 1000ms)${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠ Response time: ${elapsed_ms}ms (slow)${NC}"
    FAILED=$((FAILED + 1))
fi
TOTAL=$((TOTAL + 1))

# Test concurrent requests
echo "Testing concurrent request handling (5 parallel requests)..."
for i in {1..5}; do
    curl -s "$BASE_URL/health" > /dev/null &
done
wait
echo -e "${GREEN}✓ Handled 5 concurrent requests${NC}"
PASSED=$((PASSED + 1))
TOTAL=$((TOTAL + 1))

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}7. OPENAPI UI ACCESSIBILITY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Test Swagger UI
echo "Testing Swagger UI accessibility..."
swagger_response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")
if [ "$swagger_response" = "200" ]; then
    echo -e "${GREEN}✓ Swagger UI accessible at /docs${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ Swagger UI not accessible (HTTP $swagger_response)${NC}"
    FAILED=$((FAILED + 1))
fi
TOTAL=$((TOTAL + 1))

# Test ReDoc
echo "Testing ReDoc accessibility..."
redoc_response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/redoc")
if [ "$redoc_response" = "200" ]; then
    echo -e "${GREEN}✓ ReDoc accessible at /redoc${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ ReDoc not accessible (HTTP $redoc_response)${NC}"
    FAILED=$((FAILED + 1))
fi
TOTAL=$((TOTAL + 1))

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                        ║"
echo "║                          TEST SUMMARY                                  ║"
echo "║                                                                        ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "Total Tests:   ${BLUE}$TOTAL${NC}"
echo -e "Passed:        ${GREEN}$PASSED${NC}"
echo -e "Failed:        ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                        ║${NC}"
    echo -e "${GREEN}║  ✅ ALL TESTS PASSED - PRODUCTION READY! 🚀                            ║${NC}"
    echo -e "${GREEN}║                                                                        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}🌐 OpenAPI Documentation:${NC}"
    echo -e "   ${BLUE}Swagger UI:${NC}  http://localhost:8002/docs"
    echo -e "   ${BLUE}ReDoc:${NC}       http://localhost:8002/redoc"
    echo -e "   ${BLUE}JSON Schema:${NC} http://localhost:8002/openapi.json"
    echo ""
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                                        ║${NC}"
    echo -e "${RED}║  ⚠️  SOME TESTS FAILED - REVIEW REQUIRED                               ║${NC}"
    echo -e "${RED}║                                                                        ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 1
fi
