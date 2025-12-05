#!/bin/bash

set -e

IMAGE_NAME="voice-service-local:latest"
CONTAINER_NAME="voice-service-test"
VOICE_PORT=8002
WEBRTC_PORT=8005

echo "--- Building Docker image with Docker ---"
docker build -t $IMAGE_NAME .

echo "--- Running container with Docker ---"
# Mount models directory and expose WebRTC port
docker run -d \
    --name $CONTAINER_NAME \
    -p $VOICE_PORT:8002 \
    -p $WEBRTC_PORT:8005 \
    -v $(pwd)/models:/app/models \
    -e PYTHONPATH=/app \
    $IMAGE_NAME

echo "--- Waiting for service to start (10 seconds) ---"
sleep 10

echo "--- Performing health check ---"
HEALTH_CHECK_URL="http://localhost:$VOICE_PORT/health"
echo "Checking health at: $HEALTH_CHECK_URL"

# Retry health check up to 5 times
for i in {1..5}; do
    if curl -f -s $HEALTH_CHECK_URL > /dev/null 2>&1; then
        echo "✅ Health check PASSED on attempt $i"
        break
    else
        echo "Health check attempt $i failed, retrying in 3 seconds..."
        sleep 3
        if [ $i -eq 5 ]; then
            echo "❌ Health check FAILED after 5 attempts"
            docker logs $CONTAINER_NAME
            docker stop $CONTAINER_NAME
            docker rm $CONTAINER_NAME
            exit 1
        fi
    fi
done

echo "--- Running WebRTC integration tests ---"
# Run the WebRTC test suite
if ./run_webrtc_tests.sh; then
    echo "✅ WebRTC integration tests PASSED"
else
    echo "❌ WebRTC integration tests FAILED"
    docker logs $CONTAINER_NAME
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    exit 1
fi

echo "--- Stopping and removing container ---"
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME

echo "--- Docker integration test completed successfully ---"
