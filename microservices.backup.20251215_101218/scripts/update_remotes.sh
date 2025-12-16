#!/bin/bash

# This script will permanently update the 'origin' remote URL for all Git
# repositories found in the specified directory.
# It is recommended to run the 'test_remote_urls.sh' script first to verify
# the changes that will be made.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# The absolute path to your microservices directory.
MICROSERVICES_DIR="/root/talent-ai-platform-root/talent-ai-microservices"

# The base of the new, correct URL for your repositories.
NEW_URL_BASE="https://github.com/TalentAI"

# --- Script Execution ---

echo "--- Starting to Update Git Remote URLs ---"
echo ""

# Verify that the microservices directory exists
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
    service_name=$(basename "$service_dir")
    echo "-----------------------------------------------------"
    echo "Updating: $service_name"
    echo "-----------------------------------------------------"

    # Navigate to the service directory
    cd "$service_dir"

    # Check if the directory is a Git repository
    if [ -d ".git" ]; then
      # Construct the new repository URL
      new_repo_url="$NEW_URL_BASE/talent-ai-$service_name.git"

      echo "  Old URL:"
      git remote -v

      # Update the URL for the 'origin' remote
      git remote set-url origin "$new_repo_url"

      echo "  New URL has been set:"
      git remote -v
      echo "  Update successful."

    else
      echo "  Skipping: Not a Git repository."
    fi

    echo "" # Add a blank line for better readability
  fi
done

# Return to the original directory
cd "$START_DIR"

echo "--- All Git remote URLs have been updated successfully. ---"
