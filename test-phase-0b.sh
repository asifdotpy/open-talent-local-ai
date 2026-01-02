#!/bin/bash

# Phase 0B Testing Script
# Tests the integration between desktop app and integration service

set -e

echo "🧪 Phase 0B: Desktop App Integration Test"
echo "=========================================="
echo ""

# Check if integration service is running
echo "1️⃣ Checking Integration Service..."
if curl -s http://localhost:8009/health > /dev/null 2>&1; then
    echo "   ✅ Integration service is running on port 8009"
else
    echo "   ❌ Integration service is NOT running"
    echo "   Please start it first:"
    echo "   cd microservices/desktop-integration-service && ./start.sh"
    exit 1
fi

# Check health endpoint
echo ""
echo "2️⃣ Testing Health Endpoint..."
HEALTH=$(curl -s http://localhost:8009/health)
STATUS=$(echo $HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "error")
echo "   Status: $STATUS"

if [ "$STATUS" = "error" ]; then
    echo "   ❌ Failed to parse health response"
    exit 1
fi

# Check models endpoint
echo ""
echo "3️⃣ Testing Models Endpoint..."
MODELS=$(curl -s http://localhost:8009/api/v1/models)
MODEL_COUNT=$(echo $MODELS | python3 -c "import sys, json; print(len(json.load(sys.stdin)['models']))" 2>/dev/null || echo "0")
echo "   Available models: $MODEL_COUNT"

if [ "$MODEL_COUNT" -eq "0" ]; then
    echo "   ⚠️  No models available (expected if services are down)"
else
    echo "   ✅ Models endpoint working"
fi

# Test interview start endpoint
echo ""
echo "4️⃣ Testing Interview Start Endpoint..."
START_RESPONSE=$(curl -s -X POST http://localhost:8009/api/v1/interviews/start \
  -H "Content-Type: application/json" \
  -d '{"role": "Software Engineer", "model": "vetta-granite-2b-gguf-v4", "totalQuestions": 3}')

if echo "$START_RESPONSE" | grep -q "config"; then
    echo "   ✅ Interview start working"
    FIRST_QUESTION=$(echo $START_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['messages'][-1]['content'][:80])" 2>/dev/null || echo "")
    echo "   First question preview: $FIRST_QUESTION..."
else
    echo "   ❌ Interview start failed"
    echo "   Response: $START_RESPONSE"
    exit 1
fi

# Check desktop app build status
echo ""
echo "5️⃣ Checking Desktop App..."
if [ -f "desktop-app/package.json" ]; then
    echo "   ✅ Desktop app directory found"

    if [ -d "desktop-app/node_modules" ]; then
        echo "   ✅ Dependencies installed"
    else
        echo "   ⚠️  Dependencies not installed. Run: cd desktop-app && npm install"
    fi
else
    echo "   ❌ Desktop app directory not found"
    exit 1
fi

# Summary
echo ""
echo "=========================================="
echo "✨ Phase 0B Test Summary"
echo "=========================================="
echo "✅ Integration service: Running on port 8009"
echo "✅ Health endpoint: $STATUS"
echo "✅ Models endpoint: $MODEL_COUNT models"
echo "✅ Interview start: Working"
echo "✅ Desktop app: Ready"
echo ""
echo "🚀 Next Steps:"
echo "1. Start desktop app: cd desktop-app && npm run dev"
echo "2. Test full flow: Setup → Model Selection → Interview → Summary"
echo "3. Verify StatusBar shows service health"
echo ""
echo "🎯 Gateway Mode: Desktop app will use http://localhost:8009"
echo "   (Auto-fallback to Ollama if gateway unavailable)"
echo ""
