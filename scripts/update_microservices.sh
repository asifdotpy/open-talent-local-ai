#!/bin/bash

set -e

# Define the gitignore content
GITIGNORE_CONTENT=$(cat <<'EOF'
__pycache__/
.venv/
*.log
.env
EOF
)

# Define the requirements content
REQUIREMENTS_CONTENT=$(cat <<'EOF'
fastapi==0.111.0
uvicorn==0.30.1
EOF
)

# Get the absolute path to the microservices directory
MICROSERVICES_DIR="/root/open-talent-platform-root/open-talent-microservices"

# Loop through each service directory in the microservices directory
for service in "$MICROSERVICES_DIR"/*/; do
  if [ -d "$service" ]; then
    echo "--- Updating service: $service ---"

    # Navigate to the service directory
    cd "$service"

    # Update .gitignore
    echo "$GITIGNORE_CONTENT" > .gitignore
    echo ".gitignore updated."

    # Update requirements.txt
    echo "$REQUIREMENTS_CONTENT" > requirements.txt
    echo "requirements.txt updated."

    # Stage the changes
    git add .gitignore requirements.txt
    echo "Changes staged."

    # Check if there are changes to commit
    if ! git diff --staged --quiet; then
      # Commit the changes
      git commit -m "chore: Update .gitignore and requirements.txt with basic setup"
      echo "Changes committed."
    else
      echo "No changes to commit."
    fi

    echo "--- Finished updating service: $service ---"
    echo ""

    # Navigate back to the root directory
    cd /root/open-talent-platform-root
  fi
done

echo "--- All microservices have been updated. ---"
