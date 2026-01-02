#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Get current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Get commit message from argument or prompt
COMMIT_MESSAGE="$1"
if [ -z "$COMMIT_MESSAGE" ]; then
  read -p "Enter commit message: " COMMIT_MESSAGE
fi

# Get branch name from argument or prompt, default to current branch
BRANCH_NAME="$2"
if [ -z "$BRANCH_NAME" ]; then
  read -p "Enter branch name to push to (default: $CURRENT_BRANCH): " USER_BRANCH_INPUT
  BRANCH_NAME=${USER_BRANCH_INPUT:-$CURRENT_BRANCH}
fi

echo "--- Adding all changes ---"
git add .

echo "--- Committing changes ---"
git commit -m "$COMMIT_MESSAGE"

echo "--- Pushing to origin/$BRANCH_NAME ---"
git push origin "$BRANCH_NAME"

echo "--- Git operations completed successfully ---"
