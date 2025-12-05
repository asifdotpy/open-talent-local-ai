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

# talent-ai-infrastructure (default main branch)
echo "  └─ talent-ai-infrastructure (main)..."
cd talent-ai-infrastructure
git fetch origin
git checkout main
git pull origin main
cd ..

# talent-ai-microservices (and its submodules)
echo "  └─ talent-ai-microservices (main)..."
cd talent-ai-microservices
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
        if [[ "$repo_name" == "talent-ai-interview-service" || "$repo_name" == "talent-ai-avatar-service" ]]; then
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

# talent-ai-landing-page (default main branch)
echo "  └─ talent-ai-landing-page (main)..."
cd talent-ai-landing-page
git fetch origin
git checkout main
git pull origin main
cd ..

# talent-ai-mini (default main branch)
echo "  └─ talent-ai-mini (main)..."
cd talent-ai-mini
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