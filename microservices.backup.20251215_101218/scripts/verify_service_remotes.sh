#!/bin/bash

# This is a "dry run" test script. It verifies that the remote repositories
# for each microservice exist on GitHub and are accessible via SSH.
# IT DOES NOT MAKE ANY CHANGES to your local files.

set -e

# --- Configuration ---
# The base for constructing the SSH URLs for your TalentAI service repos.
SERVICE_REPO_BASE="git@github.com:TalentAI"


# --- Script Execution ---
echo "--- Starting Microservice Remote Verification (Dry Run) ---"
echo "This script will not make any changes."
echo ""

# Loop through each subdirectory that starts with 'talent-ai-'
for service_dir in ./talent-ai-*/; do
  if [ -d "$service_dir" ]; then
    service_name=$(basename "$service_dir")
    echo "--- Checking service: $service_name ---"

    # Construct the SSH URL that the main script WILL use
    service_repo_url="$SERVICE_REPO_BASE/$service_name.git"
    
    echo "VERIFICATION: Checking remote URL accessibility..."
    echo "  URL to check: $service_repo_url"

    # 'git ls-remote' is a safe, read-only command to check a remote URL.
    # We hide its normal output and just check if the command succeeded.
    if git ls-remote "$service_repo_url" >/dev/null 2>&1; then
        echo "SUCCESS: Remote service repository found and is accessible."
    else
        echo "FAILURE: Could not access the remote for this service."
        echo "  Please check:"
        echo "  1. The repository '$service_name' exists in the 'TalentAI' GitHub organization."
        echo "  2. Your SSH key has been granted access to the 'TalentAI' organization."
    fi
    echo ""
  fi
done

echo "-----------------------------------------------------"
echo "--- Verification Complete. No changes were made. ---"
