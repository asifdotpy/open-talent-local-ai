#!/bin/bash
#
# This script configures submodules to track a specific branch if it exists.
#
set -e

# Find all submodule paths from the .git/config file of this repository
# This is more reliable than just listing directories.
git config --file .git/config --get-regexp 'submodule\..*\.path' |
while read -r key path
do
    echo "--> Checking submodule at path: $path"

    if [ "$path" = "quarkdown-specs" ] || [ "$path" = "open-talent-microservices" ]; then
        TARGET_BRANCH="develop"
    else
        TARGET_BRANCH="dev"
    fi

    # Check if the target branch exists on the submodule's remote
    if git -C "$path" branch -r | grep -q "origin/$TARGET_BRANCH"; then
        echo "  [+] Found '$TARGET_BRANCH' branch. Setting it as the tracking branch."
        git submodule set-branch --branch "$TARGET_BRANCH" -- "$path"
    else
        echo "  [!] '$TARGET_BRANCH' branch not found. Skipping."
    fi
    echo ""
done

echo "✅ Submodule branch configuration is complete."
echo "Please review, commit, and push the updated .gitmodules file."
