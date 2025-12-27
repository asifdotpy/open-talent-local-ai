#!/bin/bash

echo "--- Git Status Report for open-talent-platform and its Submodules ---"
echo "Generated: $(date)"
echo ""

# Function to determine expected branch
get_expected_branch() {
    local repo_name="$1"
    if [[ "$repo_name" == "open-talent-interview-service" || "$repo_name" == "open-talent-avatar-service" ]]; then
        echo "main"
    elif [[ "$repo_name" == "open-talent-infrastructure" || "$repo_name" == "quarkdown-specs" || "$repo_name" == "open-talent-landing-page" || "$repo_name" == "open-talent-mini" ]]; then
        echo "main" # Assuming these top-level submodules also follow main
    elif [[ "$repo_name" == "open-talent-microservices" ]]; then
        echo "main" # The microservices *parent* submodule is on main
    else
        echo "dev" # Default for other microservices
    fi
}

# Function to check status and branch
check_repo_status() {
    local repo_path="$1"
    local repo_name="$2"
    local is_microservice_nested="$3" # "true" if nested under open-talent-microservices

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
                elif [[ "$repo_name" == "open-talent-infrastructure" || "$repo_name" == "quarkdown-specs" || "$repo_name" == "open-talent-landing-page" || "$repo_name" == "open-talent-mini" || "$repo_name" == "open-talent-microservices" ]]; then
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

# Check main open-talent-platform repository
check_repo_status "." "open-talent-platform" "false"

# Check top-level submodules
echo "## Top-Level Submodules:"
git submodule status | while read -r line ; do
    repo_path=$(echo "$line" | awk '{print $2}')
    repo_name=$(basename "$repo_path")
    check_repo_status "$repo_path" "$repo_name" "false"
done

# Check microservices submodules
echo "## Microservices Submodules (within open-talent-microservices/):"
if [ -d "open-talent-microservices" ]; then
    (
        cd open-talent-microservices || exit
        git submodule status | while read -r line ; do
            repo_path=$(echo "$line" | awk '{print $2}')
            repo_name=$(basename "$repo_path")
            check_repo_status "$repo_path" "$repo_name" "true"
        done
    )
else
    echo "Error: open-talent-microservices directory not found."
fi

echo "--- Report End ---"
