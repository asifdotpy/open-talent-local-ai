#!/bin/bash

# This is a "dry run" test script for your HP laptop.
# It checks if the required remote repositories exist on GitHub and are accessible.
# IT DOES NOT MAKE ANY CHANGES to your local files.

set -e

# --- Configuration ---
# !!! IMPORTANT: Please verify these URLs match your GitHub setup !!!

# 1. The URL for the PARENT management repository.
PARENT_REPO_URL="https//github.com/TalentAI/talent-ai-microservices-management.git"

# 2. The base GitHub URL for your individual services.
SERVICE_REPO_BASE_URL="https://github.com/TalentAI"


# --- Script Execution ---
echo "--- Starting Laptop Setup Verification (Dry Run) ---"
echo "This script will not make any changes."
echo ""


# --- Part 1: Verifying the Parent 'talent-ai-microservices' Repository ---

echo "-----------------------------------------------------"
echo "Part 1: Checking Parent Repository..."
echo "-----------------------------------------------------"

if [ -d ".git" ]; then
    echo "STATUS: This directory is already a Git repository. OK."
else
    echo "STATUS: This directory is NOT a Git repository."
    echo "ACTION: The real script would run 'git init' here."
fi

echo "VERIFICATION: Checking remote URL accessibility..."
echo "  URL to check: $PARENT_REPO_URL"

# 'git ls-remote' is a safe command to check a remote URL without cloning/pulling.
# We hide its output ('>/dev/null 2>&1') and just check if it succeeded or failed.
if git ls-remote "$PARENT_REPO_URL" >/dev/null 2>&1; then
    echo "SUCCESS: Remote parent repository found and is accessible."
else
    echo "FAILURE: Could not access the remote parent repository. Please check the PARENT_REPO_URL in the script."
fi
echo ""


# --- Part 2: Verifying the Microservice Sub-Repositories ---

echo "-----------------------------------------------------"
echo "Part 2: Checking all Microservice Sub-Repositories..."
echo "-----------------------------------------------------"

# Loop through each subdirectory that starts with 'talent-ai-'
for service_dir in ./talent-ai-*/; do
  if [ -d "$service_dir" ]; then
    service_name=$(basename "$service_dir")
    echo "--- Checking service: $service_name ---"

    # Navigate into the service's directory
    cd "$service_dir"

    if [ -d ".git" ]; then
        echo "STATUS: This service is already a Git repository. OK."
    else
        echo "STATUS: This service is NOT a Git repository."
        echo "ACTION: The real script would run 'git init' here."
    fi

    # Construct the unique URL for this specific service
    service_repo_url="$SERVICE_REPO_BASE_URL/$service_name.git"
    
    echo "VERIFICATION: Checking remote URL accessibility..."
    echo "  URL to check: $service_repo_url"

    if git ls-remote "$service_repo_url" >/dev/null 2>&1; then
        echo "SUCCESS: Remote service repository found and is accessible."
    else
        echo "FAILURE: Could not access the remote for this service. Check your GitHub repository name and the SERVICE_REPO_BASE_URL."
    fi
    echo ""

    # Navigate back up to the parent directory
    cd ..
  fi
done

echo "-----------------------------------------------------"
echo "--- Verification Complete. No changes were made. ---"
