#!/bin/bash

# OpenTalent Analytics Service - Quick Start Script

set -e

echo "🚀 Starting OpenTalent Analytics Service..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    # Prefer a Python with widespread wheels for deps (3.12 → 3.11 → fallback)
    if command -v python3.12 >/dev/null 2>&1; then
        PY_BIN="python3.12"
    elif command -v python3.11 >/dev/null 2>&1; then
        PY_BIN="python3.11"
    else
        PY_BIN="python3"
    fi
    echo "   Using interpreter: $PY_BIN"
    "$PY_BIN" -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
# Ensure modern build tooling for wheels
pip install -q --upgrade wheel setuptools
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your service URLs if needed"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting service on http://localhost:8007"
echo "📖 API docs: http://localhost:8007/docs"
echo "❤️  Health check: http://localhost:8007/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the service
python -m uvicorn main:app --host 0.0.0.0 --port 8007 --reload