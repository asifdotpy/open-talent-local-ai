#!/bin/bash

# Terminate the script immediately if any command fails
set -e

# --- Configuration ---

# Define the absolute path to the directory containing your microservices.
# IMPORTANT: Make sure to update this path to the correct location on your system.
MICROSERVICES_DIR="/root/open-talent-platform-root/open-talent-microservices"

# Define the content for the .gitignore file using a heredoc for readability.
GITIGNORE_CONTENT=$(cat <<'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual Environment
.venv/
venv/
env/

# IDE/Editor Specific
.vscode/
.idea/

# Log files
*.log

# Environment variables
.env
EOF
)

# Define the content for the requirements.txt file.
REQUIREMENTS_CONTENT=$(cat <<'EOF'
fastapi==0.111.0
uvicorn==0.30.1
EOF
)

# --- Script Execution ---

# Verify that the microservices directory exists
if [ ! -d "$MICROSERVICES_DIR" ]; then
  echo "Error: The microservices directory was not found at '$MICROSERVICES_DIR'"
  exit 1
fi

# Save the current directory to return to it after the script finishes
START_DIR=$(pwd)

# Iterate through each item in the microservices directory
for service_dir in "$MICROSERVICES_DIR"/*/; do
  # Confirm that the item is a directory
  if [ -d "$service_dir" ]; then
    echo "--- Updating service: $service_dir ---"

    # Move into the service directory
    cd "$service_dir"

    # Check if the directory is a Git repository
    if [ -d ".git" ]; then
      # Create or update the .gitignore file
      echo "$GITIGNORE_CONTENT" > .gitignore
      echo ".gitignore has been updated."

      # Create or update the requirements.txt file
      echo "$REQUIREMENTS_CONTENT" > requirements.txt
      echo "requirements.txt has been updated."

      # Stage the changes in Git
      git add .gitignore requirements.txt
      echo "Changes have been staged."

      # Commit the staged changes
      # The '|| true' part ensures that the script doesn't stop if there are no changes to commit.
      git commit -m "chore: Update .gitignore and requirements.txt" || true
      echo "Changes have been committed."
    else
      echo "Skipping... not a Git repository."
    fi

    echo "--- Finished updating service: $service_dir ---"
    echo ""
  fi
done

# Go back to the original directory
cd "$START_DIR"

echo "--- All microservices have been successfully updated. ---"
