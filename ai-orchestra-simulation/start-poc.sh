#!/bin/bash

# OpenTalent WebGL POC - Quick Start Script
# Automatically sets up and runs the POC environment

set -e

echo "🚀 OpenTalent WebGL Avatar POC - Quick Start"
echo "=========================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo ""

# Navigate to POC directory
cd "$(dirname "$0")/poc-webgl"

# Install dependencies
echo "📦 Installing dependencies (Three.js)..."
npm install
echo "✅ Dependencies installed"
echo ""

# Check if voice service is running
echo "🔍 Checking voice service..."
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "✅ Voice service is running on port 8002"
else
    echo "⚠️  Voice service not detected on port 8002"
    echo ""
    echo "To start voice service, run in a separate terminal:"
    echo "  cd microservices/voice-service"
    echo "  python main.py"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

echo ""
echo "🎯 Starting development server..."
echo ""
echo "📝 POC will be available at: http://localhost:5173"
echo "📝 Voice service should be at: http://localhost:8002"
echo ""
echo "🧪 Testing Steps:"
echo "  1. Open http://localhost:5173 in your browser"
echo "  2. Wait for avatar to load (~2-3 seconds)"
echo "  3. Click 'Speak Question' button"
echo "  4. Verify:"
echo "     - Avatar renders in 3D (or fallback visualization)"
echo "     - Lip movements sync with audio"
echo "     - FPS shows 30-60"
echo "     - Total latency ~1-2 seconds"
echo ""
echo "📝 Server will run in background with nohup"
echo "📝 Check logs: tail -f poc-webgl/nohup.out"
echo "📝 Stop server: pkill -f 'vite'"
echo ""

# Start dev server in background with nohup
cd "$(dirname "$0")/poc-webgl"
nohup npm run dev > nohup.out 2>&1 &
DEV_SERVER_PID=$!

echo "✅ Development server started (PID: $DEV_SERVER_PID)"
echo ""
echo "Waiting for server to initialize..."
sleep 3

# Check if server is running
if curl -s http://localhost:5173 > /dev/null 2>&1; then
  echo "✅ Server is ready at http://localhost:5173"
else
  echo "⚠️  Server may still be starting. Check logs:"
  echo "   tail -f poc-webgl/nohup.out"
fi

echo ""
echo "To view logs in real-time:"
echo "  tail -f poc-webgl/nohup.out"
echo ""
echo "To stop the server:"
echo "  pkill -f 'vite'  # or: kill $DEV_SERVER_PID"
