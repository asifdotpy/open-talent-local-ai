#!/bin/bash

# Test Redis Pub/Sub Integration
# This script simulates Scout AI sending a scan request to GenKit service

echo "🧪 Testing GenKit Service Redis Integration"
echo "============================================"

# Check if Redis is running
echo "1. Checking Redis connection..."
if ! docker exec redis-test redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Start it with: docker run -d -p 6379:6379 redis:7-alpine"
    exit 1
fi
echo "✅ Redis is running"

# Subscribe to output topics in background
echo ""
echo "2. Subscribing to output topics..."
docker exec -d redis-test redis-cli SUBSCRIBE agents:candidates agents:pipeline agents:errors > /tmp/redis_output.log 2>&1
sleep 2
echo "✅ Subscribed to topics"

# Publish scan request
echo ""
echo "3. Publishing scan request to agents:scanning..."
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

redis-cli -h localhost -p 6379 PUBLISH agents:scanning "$SCAN_REQUEST"
echo "✅ Scan request published"

# Wait for results
echo ""
echo "4. Waiting for results (10 seconds)..."
sleep 10

# Show results
echo ""
echo "5. Results from Redis:"
echo "===================="
cat /tmp/redis_output.log | tail -n 50

# Cleanup
kill $REDIS_PID 2>/dev/null
rm -f /tmp/redis_output.log

echo ""
echo "✅ Test complete!"
echo ""
echo "Expected output:"
echo "  - CANDIDATE_FOUND events (one per platform)"
echo "  - SCAN_COMPLETED event with totals"
echo ""
echo "To run GenKit service:"
echo "  cd agents/genkit-service"
echo "  GOOGLE_GENAI_API_KEY=test npm run dev"
