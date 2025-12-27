#!/bin/bash

# This script checks for remote updates for all microservice repositories.

# Navigate to the root of the microservices directory
cd "$(dirname "$0")/.." || exit

echo "Checking for remote updates in all microservice repositories..."
echo

# Loop through each directory in the current folder
for service in open-talent-*-service; do
  if [ -d "$service/.git" ]; then
    echo "--- Checking: $service ---"
    (
      cd "$service" || exit
      git fetch --quiet

      # Check if upstream branch is configured
      UPSTREAM=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)
      if [ -z "$UPSTREAM" ]; then
        echo "Status: No upstream branch configured."
      else
        LOCAL=$(git rev-parse @)
        REMOTE=$(git rev-parse "@{u}")
        BASE=$(git merge-base @ "@{u}")

        if [ "$LOCAL" = "$REMOTE" ]; then
          echo "Status: Up-to-date"
        elif [ "$LOCAL" = "$BASE" ]; then
          echo "Status: Needs pull"
        elif [ "$REMOTE" = "$BASE" ]; then
          echo "Status: Needs push"
        else
          echo "Status: Diverged"
        fi
      fi
      echo
    )
  fi
done
