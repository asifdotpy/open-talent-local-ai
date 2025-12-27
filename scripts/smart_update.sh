#!/bin/bash

set -e

echo "🚀 Smart Update Script - Updating all submodules to correct branches"
echo "=================================================================="

# Update main repository first
echo "📦 Updating main repository..."
git pull

# Update and checkout correct branches for each submodule based on .gitmodules
echo ""
echo "🔧 Updating submodules to correct branches..."

# open-talent-infrastructure (default main branch)
echo "  └─ open-talent-infrastructure (main)..."
cd open-talent-infrastructure
git fetch origin
git checkout main
git pull origin main
cd ..

# open-talent-microservices (and its submodules)
echo "  └─ open-talent-microservices (main)..."
cd open-talent-microservices
git fetch origin
git checkout main
git pull origin main
echo "    └─ Updating nested microservice submodules..."

# Iterate through microservice submodules and checkout correct branches
git submodule status | while read -r line ; do
    repo_path=$(echo "$line" | awk '{print $2}')
    repo_name=$(basename "$repo_path")

    echo "      └─ $repo_name..."
    (
        cd "$repo_path" || exit
        git fetch origin
        if [[ "$repo_name" == "open-talent-interview-service" || "$repo_name" == "open-talent-avatar-service" ]]; then
            echo "        (Expected: main)"
            git checkout main
            git pull origin main
        else
            echo "        (Expected: dev)"
            git checkout dev
            git pull origin dev
        fi
    )
done
cd ..

# quarkdown-specs (override to main branch)
echo "  └─ quarkdown-specs (main)..."
cd quarkdown-specs
git fetch origin
git checkout main
git pull origin main
cd ..

# open-talent-landing-page (default main branch)
echo "  └─ open-talent-landing-page (main)..."
cd open-talent-landing-page
git fetch origin
git checkout main
git pull origin main
cd ..

# open-talent-mini (default main branch)
echo "  └─ open-talent-mini (main)..."
cd open-talent-mini
git fetch origin
git checkout main
git pull origin main
cd ..

echo ""
echo "✅ Smart update complete! All submodules are now on their correct branches."
echo "=================================================================="

# Show current status
echo ""
echo "📊 Current submodule status:"
git submodule status
