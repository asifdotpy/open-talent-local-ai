#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Define the absolute path to your microservices directory.
# !!! IMPORTANT: Make sure this path is correct for your system. !!!
MICROSERVICES_DIR="/root/talent-ai-platform-root/talent-ai-microservices"

# --- Script Execution ---

# Check if the microservices directory exists
if [ ! -d "$MICROSERVICES_DIR" ]; then
  echo "Error: Microservices directory not found at '$MICROSERVICES_DIR'"
  exit 1
fi

# Save the current directory to return to it later
START_DIR=$(pwd)

# Loop through each subdirectory in the microservices directory
for service_dir in "$MICROSERVICES_DIR"/*/; do
  # Check if it is a directory
  if [ -d "$service_dir" ]; then
    echo "-----------------------------------------------------"
    echo "Checking Git status for: $(basename "$service_dir")"
    echo "-----------------------------------------------------"

    # Navigate to the service directory
    cd "$service_dir"

    # Check if the directory is a Git repository
    if [ -d ".git" ]; then
      # Execute git status
      git status
    else
      echo "This directory is not a Git repository."
    fi

    echo "" # Add a blank line for better readability
  fi
done

# Return to the original directory
cd "$START_DIR"

echo "--- Git status check complete for all microservices. ---"
