#!/bin/bash

echo "--- Git Status Report for talent-ai-platform and its Submodules ---"
echo "Generated: $(date)"
echo ""

# Function to determine expected branch
get_expected_branch() {
    local repo_name="$1"
    if [[ "$repo_name" == "talent-ai-interview-service" || "$repo_name" == "talent-ai-avatar-service" ]]; then
        echo "main"
    elif [[ "$repo_name" == "talent-ai-infrastructure" || "$repo_name" == "quarkdown-specs" || "$repo_name" == "talent-ai-landing-page" || "$repo_name" == "talent-ai-mini" ]]; then
        echo "main" # Assuming these top-level submodules also follow main
    elif [[ "$repo_name" == "talent-ai-microservices" ]]; then
        echo "main" # The microservices *parent* submodule is on main
    else
        echo "dev" # Default for other microservices
    fi
}

# Function to check status and branch
check_repo_status() {
    local repo_path="$1"
    local repo_name="$2"
    local is_microservice_nested="$3" # "true" if nested under talent-ai-microservices

    echo "### Repository: $repo_name ($repo_path)"
    if [ -d "$repo_path" ]; then
        (
            cd "$repo_path" || exit
            current_branch=$(git branch --show-current 2>/dev/null)
            if [ -z "$current_branch" ]; then
                echo "Current Branch: N/A (not a git repo or detached HEAD)"
                echo "Branch Status: ⚠️ Unknown"
            else
                expected_branch=""
                if [ "$is_microservice_nested" == "true" ]; then
                    expected_branch=$(get_expected_branch "$repo_name")
                elif [[ "$repo_name" == "talent-ai-infrastructure" || "$repo_name" == "quarkdown-specs" || "$repo_name" == "talent-ai-landing-page" || "$repo_name" == "talent-ai-mini" || "$repo_name" == "talent-ai-microservices" ]]; then
                    expected_branch="main" # Top-level submodules
                else
                    expected_branch="main" # Default for main repo
                fi

                echo "Current Branch: $current_branch"
                if [ "$current_branch" == "$expected_branch" ]; then
                    echo "Branch Status: ✅ Correct (Expected: $expected_branch)"
                else
                    echo "Branch Status: ⚠️ Incorrect (Expected: $expected_branch, Found: $current_branch)"
                fi
            fi
            echo "Git Status:"
            git status --short
            echo ""
        )
    else
        echo "Error: Directory $repo_path not found or not a git repository."
        echo ""
    fi
}

# Check main talent-ai-platform repository
check_repo_status "." "talent-ai-platform" "false"

# Check top-level submodules
echo "## Top-Level Submodules:"
git submodule status | while read -r line ; do
    repo_path=$(echo "$line" | awk '{print $2}')
    repo_name=$(basename "$repo_path")
    check_repo_status "$repo_path" "$repo_name" "false"
done

# Check microservices submodules
echo "## Microservices Submodules (within talent-ai-microservices/):"
if [ -d "talent-ai-microservices" ]; then
    (
        cd talent-ai-microservices || exit
        git submodule status | while read -r line ; do
            repo_path=$(echo "$line" | awk '{print $2}')
            repo_name=$(basename "$repo_path")
            check_repo_status "$repo_path" "$repo_name" "true"
        done
    )
else
    echo "Error: talent-ai-microservices directory not found."
fi

echo "--- Report End ---"