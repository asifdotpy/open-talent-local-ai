#!/bin/bash

# This is a "dry run" script. It will not make any changes.
# Its purpose is to show you what the 'update_remotes.sh' script *would* do.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# The absolute path to your microservices directory.
MICROSERVICES_DIR="/root/talent-ai-platform-root/talent-ai-microservices"

# The base of the new, correct URL for your repositories.
NEW_URL_BASE="https://github.com/TalentAI"

# --- Script Execution ---

echo "--- Starting Git Remote URL Test (Dry Run) ---"
echo "This script will not make any changes."
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
    echo "Checking: $service_name"
    echo "-----------------------------------------------------"

    # Navigate to the service directory
    cd "$service_dir"

    # Check if the directory is a Git repository
    if [ -d ".git" ]; then
      # Get the current remote URL for 'origin'
      current_url=$(git remote get-url origin)

      # Construct the proposed new URL based on the directory name
      proposed_url="$NEW_URL_BASE/talent-ai-$service_name.git"

      # Print both for comparison
      echo "  Current URL:      $current_url"
      echo "  Proposed New URL: $proposed_url"

      # Add a status message for clarity
      if [ "$current_url" == "$proposed_url" ]; then
        echo "  STATUS: Looks correct. No change needed."
      else
        echo "  STATUS: Update is required."
      fi

    else
      echo "  Skipping: Not a Git repository."
    fi

    echo "" # Add a blank line for better readability
  fi
done

# Return to the original directory
cd "$START_DIR"

echo "--- Test complete. No changes were made to any repository. ---"
