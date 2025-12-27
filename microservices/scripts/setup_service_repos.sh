#!/bin/bash

# This script completes the workspace setup by initializing each microservice
# subdirectory, connecting it to its remote repository in the OpenTalent org,
# and pulling down the latest code. It uses the SSH protocol for auth.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# The base for constructing the SSH URLs for your service repos.
SERVICE_REPO_BASE="git@github.com:OpenTalent"


# --- Script Execution ---
LOG_FILE="service_repo_setup_log_$(date +%Y-%m-%d_%H-%M-%S).txt"
exec &> >(tee -a "$LOG_FILE")

echo "--- Starting Microservice Repository Setup ---"
echo "This will pull the code for each individual service."
echo "A detailed log will be saved to: $LOG_FILE"
echo ""

# Loop through each subdirectory that starts with '*-service'
for service_dir in ./*-service/; do
  if [ -d "$service_dir" ]; then
    service_name=$(basename "$service_dir")
    echo "--- Processing service: $service_name ---"

    cd "$service_dir"

    # Construct the SSH URL for this specific service
    service_repo_url="$SERVICE_REPO_BASE/$service_name.git"

    # This check is robust: if a .git folder somehow exists, it will
    # simply ensure the remote is correct instead of failing.
    if [ -d ".git" ]; then
        echo "This service is already a Git repository. Ensuring remote is correct."
        git remote set-url origin "$service_repo_url"
    else
        echo "Initializing Git repository..."
        git init
        git branch -m main
        echo "Adding remote origin: $service_repo_url"
        git remote add origin "$service_repo_url"
    fi

    echo "Pulling code from GitHub..."
    # The --allow-unrelated-histories flag is a safeguard in case the remote
    # has a history that's different from a brand new local 'git init'.
    git pull origin main --allow-unrelated-histories
    echo "Service '$service_name' is now synchronized."
    echo ""

    cd ..
  fi
done

echo "-----------------------------------------------------"
echo "--- ALL DONE! Your laptop workspace is fully synchronized. ---"
