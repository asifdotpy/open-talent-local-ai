#!/bin/bash

# Manual Avatar Integration Test Script
# Run this to verify the complete avatar interview system works

echo "🎭 TALENTAI AVATAR INTEGRATION - MANUAL TEST"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check service
check_service() {
    local name=$1
    local url=$2
    local expected=$3

    echo -n "🔍 Checking $name... "
    if curl -s "$url" | grep -q "$expected"; then
        echo -e "${GREEN}✅ PASS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        return 1
    fi
}

# Function to test WebSocket connection
test_websocket() {
    echo -n "🔍 Testing WebSocket connection... "
    # Simple WebSocket test using timeout
    timeout 5 bash -c "</dev/tcp/localhost/3002" 2>/dev/null && echo -e "${GREEN}✅ PASS${NC}" || echo -e "${RED}❌ FAIL${NC}"
}

echo "📋 SERVICE HEALTH CHECKS"
echo "------------------------"

# Check all services
check_service "Avatar Renderer" "http://localhost:3001/health" "healthy"
check_service "R3F Frontend" "http://localhost:5175" "DOCTYPE html"
check_service "Voice Service" "http://localhost:8002/health" "healthy"
test_websocket

echo ""
echo "🎯 MANUAL TESTING INSTRUCTIONS"
echo "------------------------------"
echo ""
echo "1. 🌐 Open your browser and go to:"
echo -e "   ${BLUE}http://localhost:5175${NC}"
echo ""
echo "2. 🎭 You should see:"
echo "   - Avatar selector with 8 diverse avatars (Marcus, Sarah, Alex, Emma, etc.)"
echo "   - Controls panel with Leva debug interface"
echo "   - 3D canvas with avatar rendering"
echo ""
echo "3. 🎤 Test Voice Integration:"
echo "   - Click 'Speak Question' button"
echo "   - Should generate TTS audio and phoneme data"
echo "   - Avatar should animate lip-sync in real-time"
echo ""
echo "4. 🎨 Test Avatar Switching:"
echo "   - Select different avatars from the dropdown"
echo "   - Avatar should change instantly"
echo "   - Lip-sync should work for all avatars"
echo ""
echo "5. 🔧 Debug Panel:"
echo "   - Use Leva controls to adjust avatar position/rotation"
echo "   - Check phoneme timeline in browser console"
echo "   - Monitor WebSocket messages (F12 → Network → WS)"
echo ""

echo "📊 EXPECTED BEHAVIOR"
echo "--------------------"
echo "✅ Avatar loads and displays in 3D"
echo "✅ Voice service generates audio + phonemes"
echo "✅ Real-time lip-sync animation"
echo "✅ Smooth 60 FPS performance"
echo "✅ WebSocket streaming active"
echo "✅ All 8 avatars available"
echo ""

echo "🚨 TROUBLESHOOTING"
echo "------------------"
if ! curl -s http://localhost:3001/health | grep -q "healthy"; then
    echo -e "${RED}❌ Avatar renderer not running${NC}"
    echo "   Run: cd ai-orchestra-simulation && RENDERER_TYPE=r3f node avatar-renderer-v2.js"
fi

if ! curl -s http://localhost:5175 | grep -q "DOCTYPE"; then
    echo -e "${RED}❌ R3F frontend not running${NC}"
    echo "   Run: cd ai-orchestra-simulation/poc-webgl && npm start"
fi

if ! curl -s http://localhost:8002/health | grep -q "healthy"; then
    echo -e "${RED}❌ Voice service not running${NC}"
    echo "   Check microservices/voice-service"
fi

echo ""
echo -e "${YELLOW}🎯 Ready for manual testing! Open http://localhost:5175${NC}"