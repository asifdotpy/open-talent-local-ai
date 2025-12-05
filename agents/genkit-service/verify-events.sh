#!/bin/bash

echo "📡 Subscribing to Redis events for 15 seconds..."
echo "Listening to: agents:candidates, agents:pipeline, agents:errors"
echo ""

# Subscribe and capture output
timeout 15 docker exec -i redis-test redis-cli SUBSCRIBE agents:candidates agents:pipeline agents:errors &
SUBSCRIBE_PID=$!

# Wait 2 seconds for subscription
sleep 2

# Send test request
echo "📤 Sending test scan request..."
SCAN_REQUEST='{
  "source_agent": "Scout AI (Verify)",
  "message_type": "SCAN_REQUEST",
  "payload": {
    "pipeline_id": "verify-pipeline-001",
    "job_id": "job-456",
    "platforms": [
      {
        "platform": "linkedin",
        "query": "data scientist",
        "maxResults": 3
      }
    ]
  },
  "correlation_id": "verify-correlation-456",
  "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
}'

docker exec redis-test redis-cli PUBLISH agents:scanning "$SCAN_REQUEST" > /dev/null
echo "✅ Request sent, waiting for events..."
echo ""

# Wait for timeout
wait $SUBSCRIBE_PID

echo ""
echo "✅ Verification complete!"
