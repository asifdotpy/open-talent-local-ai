#!/bin/bash

# Start script for Granite Interview Service

set -e

echo "🚀 Starting Granite Interview Service..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p models data models/fine-tuned logs

# Set environment variables
export PYTHONPATH=$(pwd)
export HOST=0.0.0.0
export PORT=8005
export DEBUG=true
export DEFAULT_MODEL=granite4:350m-h

# Start the service
echo "🎯 Starting service on http://localhost:8005"
echo "📊 Health check: http://localhost:8005/health"
echo "📚 API docs: http://localhost:8005/docs"

uvicorn app.main:app --host $HOST --port $PORT --reload
