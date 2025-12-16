#!/bin/bash

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  TalentAI - Lightweight Persona Setup & Test                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

echo "🎭 TalentAI Lightweight Interviewer Personas Setup"
echo "=================================================="

# Check if Ollama is running
if ! ollama list > /dev/null 2>&1; then
    echo "❌ Ollama is not running. Please start Ollama first:"
    echo "   ollama serve"
    exit 1
fi

echo "✅ Ollama is running"

# Run persona setup
echo ""
echo "🔧 Setting up interviewer personas..."
./setup_personas.sh

echo ""
echo "🚀 Starting conversation service..."

# Update .env to use technical interviewer as default
if [ -f ".env" ]; then
    sed -i 's/LLM_MODEL=.*/LLM_MODEL=technical-interviewer/' .env
    echo "✅ Updated .env to use technical-interviewer"
else
    echo "⚠️  No .env file found. Please create one from .env.example"
fi

# Start the service
echo ""
echo "🌟 Starting conversation service..."
python3 main.py &
SERVICE_PID=$!

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 5

# Test the service
echo ""
echo "🧪 Testing persona switching..."

# Test 1: Check current persona
echo "1. Checking current persona:"
curl -s http://localhost:8003/api/v1/persona/current | python3 -m json.tool

echo ""
echo "2. Switching to behavioral interviewer:"
curl -s -X POST http://localhost:8003/api/v1/persona/switch \
  -H 'Content-Type: application/json' \
  -d '{"persona": "behavioral"}' | python3 -m json.tool

echo ""
echo "3. Switching to HR interviewer:"
curl -s -X POST http://localhost:8003/api/v1/persona/switch \
  -H 'Content-Type: application/json' \
  -d '{"persona": "hr"}' | python3 -m json.tool

echo ""
echo "4. Back to technical interviewer:"
curl -s -X POST http://localhost:8003/api/v1/persona/switch \
  -H 'Content-Type: application/json' \
  -d '{"persona": "technical"}' | python3 -m json.tool

echo ""
echo "5. Testing question generation with current persona:"
curl -s -X POST http://localhost:8003/api/v1/conversation/generate-questions \
  -H 'Content-Type: application/json' \
  -d '{"job_requirements": "Python, Django, React", "num_questions": 2}' | python3 -m json.tool

echo ""
echo "🎉 Setup complete! Service is running with persona switching."
echo ""
echo "📋 Available endpoints:"
echo "  GET  /api/v1/persona/current     - Check current persona"
echo "  POST /api/v1/persona/switch      - Switch personas"
echo "  POST /api/v1/conversation/generate-questions - Generate questions"
echo ""
echo "🔄 Persona options: technical, behavioral, hr"
echo ""
echo "🛑 To stop the service: kill $SERVICE_PID"

# Keep service running
wait $SERVICE_PID