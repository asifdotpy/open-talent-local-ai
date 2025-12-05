#!/bin/bash
# Start WebRTC signaling, voice worker, and conversation services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting WebRTC and conversation services..."

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv"
fi

source "$PROJECT_ROOT/.venv/bin/activate"

# Install dependencies
echo "Installing interview-service dependencies..."
pip install -q -r "$PROJECT_ROOT/microservices/interview-service/requirements-webrtc.txt"

echo "Installing voice-service dependencies..."
pip install -q -r "$PROJECT_ROOT/microservices/voice-service/requirements-webrtc.txt"

echo "Installing conversation-service dependencies..."
pip install -q -r "$PROJECT_ROOT/microservices/conversation-service/requirements.txt"

# Start conversation service in background
echo "Starting conversation-service on port 8003..."
cd "$PROJECT_ROOT/microservices/conversation-service"
uvicorn main:app --host 0.0.0.0 --port 8003 --reload &
CONVERSATION_PID=$!

# Start signaling server in background
echo "Starting interview-service signaling server on port 8004..."
cd "$PROJECT_ROOT/microservices/interview-service"
uvicorn webrtc_signal:app --host 0.0.0.0 --port 8004 --reload &
SIGNAL_PID=$!

# Start voice worker in background
echo "Starting voice-service worker on port 8002..."
cd "$PROJECT_ROOT/microservices/voice-service"
uvicorn webrtc_worker:app --host 0.0.0.0 --port 8002 --reload &
WORKER_PID=$!

echo ""
echo "✓ Services started:"
echo "  - Conversation service: http://localhost:8003 (PID: $CONVERSATION_PID)"
echo "  - Signaling server: http://localhost:8004 (PID: $SIGNAL_PID)"
echo "  - Voice worker: http://localhost:8002 (PID: $WORKER_PID)"
echo ""
echo "To stop services, run: kill $CONVERSATION_PID $SIGNAL_PID $WORKER_PID"
echo "Or use: pkill -f 'uvicorn.*main\|uvicorn.*webrtc'"
echo ""
echo "Logs will appear below. Press Ctrl+C to stop all services."
echo "================================================"

# Wait for all processes
wait
