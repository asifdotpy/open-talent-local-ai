#!/bin/bash
# scripts/prepare-release.sh

SUBMODULE=$1
VERSION=$2

# Validate version format
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Invalid version format. Use MAJOR.MINOR.PATCH"
    exit 1
fi

# Check submodule exists
if [[ ! -d "$SUBMODULE" ]]; then
    echo "Submodule $SUBMODULE not found"
    exit 1
fi

# Update version files
cd "$SUBMODULE"
echo "$VERSION" > VERSION

# Update package.json if it exists
if [[ -f "package.json" ]]; then
    npm version "$VERSION" --no-git-tag-version
fi

# Update setup.py if it exists
if [[ -f "setup.py" ]]; then
    sed -i "s/version='[^']*'/version='$VERSION'/" setup.py
fi

echo "Prepared $SUBMODULE for release $VERSION"