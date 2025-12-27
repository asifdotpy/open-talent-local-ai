#!/bin/bash

# This script sets up the upstream branch for all microservice repositories.

# Navigate to the root of the microservices directory
cd "$(dirname "$0")/.." || exit

echo "Setting up upstream branches for all microservice repositories..."
echo

# Loop through each directory in the current folder
for service in open-talent-*-service; do
  if [ -d "$service/.git" ]; then
    echo "--- Setting up: $service ---"
    (
      cd "$service" || exit
      # Set the local 'main' branch to track the 'main' branch on the 'origin' remote
      git branch --set-upstream-to=origin/main main
    )
  fi
done

echo
echo "Upstream branches configured. You can now run 'check_remote_updates.sh'."
