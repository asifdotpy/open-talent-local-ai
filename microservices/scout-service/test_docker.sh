#!/bin/bash
# Test script for Agent Agent (Talent Sourcing) Docker build
set -e

echo "Building OpenTalent - Sourcer Service (Talent Sourcing) with Docker..."
docker build -t sourcer-service .

echo "Running basic import test..."
docker run --rm sourcer-service python -c "import main; print('✅ Sourcer imports successfully')"

echo "Testing health endpoint..."
# Note: Would need environment variables for full testing
echo "⚠️  Full API testing requires GITHUB_TOKEN and CONTACTOUT_API_TOKEN environment variables"

echo "✅ Docker build test completed successfully!"
