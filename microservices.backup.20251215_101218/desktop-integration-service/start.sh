#!/bin/bash

# OpenTalent Desktop Integration Service - Quick Start Script

set -e

echo "🚀 Starting OpenTalent Desktop Integration Service..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
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
echo "🌐 Starting service on http://localhost:8009"
echo "📖 API docs: http://localhost:8009/docs"
echo "❤️  Health check: http://localhost:8009/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8009 --reload
