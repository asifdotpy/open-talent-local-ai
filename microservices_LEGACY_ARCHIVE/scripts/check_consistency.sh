#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the reference service directory and its expected files
REFERENCE_SERVICE="avatar-service"
EXPECTED_FILES=(
    ".github"
    ".gitignore"
    "Dockerfile"
    "main.py"
    "pyproject.toml"
    "requirements.txt"
    "test_docker.sh"
    "test_podman.sh"
)

# Get the absolute path to the microservices root directory
MICROSERVICES_ROOT="$(pwd)"

echo "--- Starting Consistency Check for Microservices ---"
echo "Reference service for file structure: $REFERENCE_SERVICE"
echo "Expected files/directories: ${EXPECTED_FILES[@]}"
echo ""

# Loop through each subdirectory that starts with 'open-talent-'
for service_dir in open-talent-*/; do
  if [ -d "$service_dir" ]; then
    service_name=$(basename "$service_dir")
    echo "--- Checking service: $service_name ---"

    cd "$service_dir"

    # Get actual files in the current service directory (excluding .git and logs)
    ACTUAL_FILES=($(ls -A | grep -vE '^\.git$|^logs$'))

    # Check for missing files
    for expected_file in "${EXPECTED_FILES[@]}"; do
      found=false
      for actual_file in "${ACTUAL_FILES[@]}"; do
        if [ "$expected_file" == "$actual_file" ]; then
          found=true
          break
        fi
      done
      if [ "$found" == "false" ]; then
        echo "  MISSING: $expected_file"
      fi
    done

    # Check for extra files
    for actual_file in "${ACTUAL_FILES[@]}"; do
      found=false
      for expected_file in "${EXPECTED_FILES[@]}"; do
        if [ "$actual_file" == "$expected_file" ]; then
          found=true
          break
        fi
      done
      if [ "$found" == "false" ]; then
        echo "  EXTRA: $actual_file"
      fi
    done

    echo ""
    cd "$MICROSERVICES_ROOT"
  fi
done

echo "--- Consistency Check Completed ---"
