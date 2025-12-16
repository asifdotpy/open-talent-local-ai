#!/bin/bash

set -e

IMAGE_NAME="interview-service-local:latest"
CONTAINER_NAME="interview-service-test"
PORT=8080 # Use a different port for local testing to avoid conflicts

echo "--- Building Docker image with Docker ---"
docker build -t $IMAGE_NAME .

echo "--- Running container with Docker ---"
docker run -d --name $CONTAINER_NAME -p $PORT:80 $IMAGE_NAME

echo "--- Waiting for service to start (5 seconds) ---"
sleep 5

echo "--- Performing health check ---"
HEALTH_CHECK_URL="http://localhost:$PORT/health"
RESPONSE=$(curl -s $HEALTH_CHECK_URL)

if echo "$RESPONSE" | grep -q "healthy"; then
    echo "Health check PASSED: $RESPONSE"
else
    echo "Health check FAILED: $RESPONSE"
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    exit 1
fi

echo "--- Stopping and removing container ---"
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME

echo "--- Docker test completed successfully ---"
