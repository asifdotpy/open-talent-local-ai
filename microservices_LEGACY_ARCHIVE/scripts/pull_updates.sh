#!/bin/bash

# This script pulls the latest changes for specified microservice repositories.

# Navigate to the root of the microservices directory
cd "$(dirname "$0")/.." || exit

# Array of services to update
services_to_update=(
  "ai-auditing-service"
  "analytics-service"
  "avatar-service"
  "candidate-service"
  "conversation-service"
  "explainability-service"
  "interview-service"
  "notification-service"
  "project-service"
  "security-service"
  "user-service"
)

echo "Pulling latest changes for selected microservices..."
echo

for service in "${services_to_update[@]}"; do
  if [ -d "$service" ]; then
    echo "--- Updating: $service ---"
    (
      cd "$service" || exit
      git pull
      echo
    )
  else
    echo "--- Skipping: $service (directory not found) ---"
    echo
  fi
done
