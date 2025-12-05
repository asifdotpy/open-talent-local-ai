#!/bin/bash

# Test Redis Pub/Sub Integration
# This script simulates Scout AI sending a scan request to GenKit service

echo "🧪 Testing GenKit Service Redis Integration"
echo "============================================"

# Check if Redis is running
echo "1. Checking Redis connection..."
if ! docker exec redis-test redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis container 'redis-test' is not running"
    exit 1
fi
echo "✅ Redis is running"

# Publish scan request
echo ""
echo "2. Publishing scan request to agents:scanning..."
SCAN_REQUEST='{
  "source_agent": "Scout AI (Test)",
  "message_type": "SCAN_REQUEST",
  "payload": {
    "pipeline_id": "test-pipeline-001",
    "job_id": "job-123",
    "platforms": [
      {
        "platform": "linkedin",
        "query": "software engineer python",
        "maxResults": 5
      },
      {
        "platform": "github",
        "query": "python",
        "maxResults": 5
      }
    ]
  },
  "correlation_id": "test-correlation-123",
  "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
}'

# Use docker exec to publish
RESULT=$(docker exec redis-test redis-cli PUBLISH agents:scanning "$SCAN_REQUEST")
echo "✅ Scan request published (received by $RESULT subscriber(s))"

# Wait for processing
echo ""
echo "3. Waiting for GenKit service to process (5 seconds)..."
sleep 5

echo ""
echo "✅ Test complete!"
echo ""
echo "To verify the events were published, check the GenKit service logs."
echo "Expected events:"
echo "  - Processing scan request for linkedin and github"
echo "  - Published CANDIDATE_FOUND events"
echo "  - Published SCAN_COMPLETED event"
