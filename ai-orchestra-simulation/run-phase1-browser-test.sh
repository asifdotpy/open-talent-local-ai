#!/bin/bash

# Phase 1 Browser Integration Test - Quick Starter
# Usage: ./run-phase1-browser-test.sh

set -e

PROJECT_ROOT="/home/asif1/talent-ai-platform"
ORCHESTRA_DIR="$PROJECT_ROOT/ai-orchestra-simulation"
VENV="$PROJECT_ROOT/.venv/bin/activate"

echo "🎬 Phase 1 Browser Integration Test - Startup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Virtual Environment
echo "1️⃣  Checking Virtual Environment..."
if [ ! -f "$VENV" ]; then
    echo "❌ Virtual environment not found at $VENV"
    exit 1
fi
echo "   ✓ Found at $VENV"
echo ""

# Check Python Dependencies
echo "2️⃣  Checking Python Dependencies..."
source "$VENV"
python3 -c "import fastapi, uvicorn, pydub" 2>/dev/null && echo "   ✓ All dependencies installed" || {
    echo "   ⚠ Installing dependencies..."
    pip install -q fastapi uvicorn pydub python-multipart pydantic
    echo "   ✓ Dependencies installed"
}
echo ""

# Start Voice Service if not running
echo "3️⃣  Checking Voice Service (port 8002)..."
if ! curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "   ℹ Starting Voice Service..."
    cd "$PROJECT_ROOT/microservices/voice-service"
    USE_MOCK_SERVICES=true python main.py > /tmp/voice-service.log 2>&1 &
    VOICE_PID=$!
    echo $VOICE_PID > /tmp/voice-service.pid
    sleep 2
    
    # Check if service started
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        echo "   ✓ Voice Service started (PID: $VOICE_PID)"
    else
        echo "   ❌ Failed to start Voice Service"
        cat /tmp/voice-service.log
        exit 1
    fi
else
    echo "   ✓ Voice Service already running"
fi
echo ""

# Start HTTP Server if not running
echo "4️⃣  Checking HTTP Server (port 9000)..."
if ! curl -s http://localhost:9000/test-phase1-browser.html > /dev/null 2>&1; then
    echo "   ℹ Starting HTTP Server..."
    cd "$ORCHESTRA_DIR"
    python3 -m http.server 9000 > /tmp/http-server.log 2>&1 &
    HTTP_PID=$!
    echo $HTTP_PID > /tmp/http-server.pid
    sleep 1
    
    if curl -s http://localhost:9000/test-phase1-browser.html > /dev/null 2>&1; then
        echo "   ✓ HTTP Server started (PID: $HTTP_PID)"
    else
        echo "   ❌ Failed to start HTTP Server"
        exit 1
    fi
else
    echo "   ✓ HTTP Server already running"
fi
echo ""

# Run Node.js verification
echo "5️⃣  Running Module Verification (Node.js)..."
cd "$ORCHESTRA_DIR"
if node run-phase1-verification.js > /tmp/verification-output.txt 2>&1; then
    echo "   ✓ Module verification passed"
    echo ""
    grep "^✅" /tmp/verification-output.txt
else
    echo "   ⚠ Module verification had issues"
    cat /tmp/verification-output.txt | tail -20
fi
echo ""

# Display status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PHASE 1 INTEGRATION TESTING READY"
echo ""
echo "🌐 Browser Test Interface:"
echo "   URL: http://localhost:9000/test-phase1-browser.html"
echo "   "
echo "   Open this URL in your browser to start testing"
echo ""
echo "🔧 Services Running:"
echo "   • Voice Service (port 8002): $(curl -s http://localhost:8002/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
echo "   • HTTP Server (port 9000): ✓"
echo ""
echo "📊 Test Steps:"
echo "   1. Open http://localhost:9000/test-phase1-browser.html"
echo "   2. Enter text to synthesize (or use default)"
echo "   3. Click 'Start Test' button"
echo "   4. Monitor test progress and results"
echo "   5. Check FPS, sync error, and performance metrics"
echo ""
echo "📝 Logs:"
echo "   Voice Service: tail -f /tmp/voice-service.log"
echo "   HTTP Server: tail -f /tmp/http-server.log"
echo ""
echo "🛑 Stopping Services:"
echo "   kill \$(cat /tmp/voice-service.pid 2>/dev/null)"
echo "   kill \$(cat /tmp/http-server.pid 2>/dev/null)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏳ Waiting for services... Press Ctrl+C to exit"
wait
