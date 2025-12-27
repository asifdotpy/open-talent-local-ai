#!/bin/bash
# scripts/release.sh

SUBMODULE=$1
VERSION=$2
ENVIRONMENT=${3:-staging}

# Run full test suite
echo "Running tests for $SUBMODULE..."
cd "$SUBMODULE"

if [[ -f "package.json" ]]; then
    npm test
    npm run build
elif [[ -f "requirements.txt" ]]; then
    python -m pytest tests/ -v
fi

# Security scan
echo "Running security scan..."
# Run security tools based on language
if [[ -f "package.json" ]]; then
    npm audit
    # Run SAST tool
elif [[ -f "requirements.txt" ]]; then
    safety check
    bandit -r .
fi

# Create release artifacts
echo "Creating release artifacts..."
mkdir -p "../../releases/$SUBMODULE/$VERSION"

if [[ -f "package.json" ]]; then
    npm pack
    mv *.tgz "../../releases/$SUBMODULE/$VERSION/"
elif [[ -f "Dockerfile" ]]; then
    # Build and push Docker image
    docker build -t "open-talent/$SUBMODULE:$VERSION" .
    docker push "open-talent/$SUBMODULE:$VERSION"
fi

# Tag release
git tag "$SUBMODULE-v$VERSION"
git push origin "$SUBMODULE-v$VERSION"

echo "Released $SUBMODULE v$VERSION to $ENVIRONMENT"
