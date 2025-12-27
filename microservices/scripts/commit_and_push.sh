#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Define the absolute path to your microservices directory.
MICROSERVICES_DIR="/root/open-talent-platform-root/open-talent-microservices"

# Define the log file path. The script will create this file and append logs to it.
LOG_FILE="/root/open-talent-platform-root/open-talent-microservices/deployment_log_$(date +%Y-%m-%d_%H-%M-%S).txt"

# --- Script Execution ---

# Redirect all output (stdout and stderr) to the log file and the console
exec &> >(tee -a "$LOG_FILE")

echo "Starting the commit and push process for all microservices..."
echo "Log file created at: $LOG_FILE"
echo ""

# Check if the microservices directory exists
if [ ! -d "$MICROSERVICES_DIR" ]; then
  echo "Error: Microservices directory not found at '$MICROSERVICES_DIR'"
  exit 1
fi

# Save the current directory to return to it later
START_DIR=$(pwd)

# --- Special Handling for project-service ---
PROJECT_SERVICE_DIR="$MICROSERVICES_DIR/project-service"
echo "--- Handling special case: project-service ---"

if [ -d "$PROJECT_SERVICE_DIR" ]; then
  cd "$PROJECT_SERVICE_DIR"
  if [ -d ".git" ]; then
    echo "Staging changes in project-service..."
    # Add the modified and untracked files
    git add Dockerfile main.py pyproject.toml

    echo "Committing changes in project-service..."
    # Commit the changes with a descriptive message
    git commit -m "feat: Add Dockerfile and pyproject.toml, update main.py"
    echo "Commit successful for project-service."
  else
    echo "project-service is not a Git repository."
  fi
  echo "--- Finished handling project-service ---"
  echo ""
else
  echo "Warning: project-service directory not found."
  echo ""
fi

# --- Loop Through All Services to Push ---
echo "--- Starting to push all services ---"

for service_dir in "$MICROSERVICES_DIR"/*/; do
  if [ -d "$service_dir" ]; then
    echo "-----------------------------------------------------"
    echo "Processing: $(basename "$service_dir")"
    echo "-----------------------------------------------------"
    cd "$service_dir"

    if [ -d ".git" ]; then
      # Check if the local branch is ahead of the remote
      if git status | grep -q "Your branch is ahead of"; then
        echo "Pushing changes for $(basename "$service_dir")..."
        git push
        echo "Push successful."
      else
        echo "No changes to push for $(basename "$service_dir")."
      fi
    else
      echo "Not a Git repository."
    fi
    echo ""
  fi
done

# Return to the original directory
cd "$START_DIR"

echo "--- All microservices have been processed. ---"
echo "Review the log file for details: $LOG_FILE"
