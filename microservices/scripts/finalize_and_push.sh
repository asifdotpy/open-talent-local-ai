#!/bin/bash

# This script stages all changes, commits them with a standard message,
# and pushes the commits to the remote repository. It logs all actions.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# The absolute path to your microservices directory.
MICROSERVICES_DIR="/root/open-talent-platform-root/open-talent-microservices"

# The commit message to be used for these maintenance changes.
COMMIT_MESSAGE="chore: Update Git remotes and add utility scripts"

# The log file for this operation.
LOG_FILE="/root/open-talent-platform-root/open-talent-microservices/push_log_$(date +%Y-%m-%d_%H-%M-%S).txt"

# --- Script Execution ---

# Redirect all output (stdout and stderr) to both the console and the log file.
exec &> >(tee -a "$LOG_FILE")

echo "--- Starting Final Add, Commit, and Push Process ---"
echo "Log file will be saved to: $LOG_FILE"
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
    echo "Processing: $service_name"
    echo "-----------------------------------------------------"

    # Navigate to the service directory
    cd "$service_dir"

    # Check if the directory is a Git repository
    if [ -d ".git" ]; then
      # Stage all new and modified files
      echo "Staging all changes..."
      git add .

      # Commit the staged changes.
      # The 'git commit ... || true' part prevents the script from exiting if
      # there are no changes to commit, allowing it to continue to the push.
      echo "Committing with message: '$COMMIT_MESSAGE'..."
      if git commit -m "$COMMIT_MESSAGE"; then
        echo "Commit successful."
      else
        echo "No new changes to commit. Proceeding to push."
      fi

      # Push the changes to the remote repository.
      echo "Pushing to origin main..."
      git push origin main
      echo "Push successful for $service_name."

    else
      echo "Skipping: Not a Git repository."
    fi

    echo "" # Add a blank line for better readability
  fi
done

# Return to the original directory
cd "$START_DIR"

echo "--- Final push process complete for all microservices. ---"
echo "Review the log file for details: $LOG_FILE"
