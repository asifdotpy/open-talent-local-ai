#!/bin/bash
# Verification script for shared library implementation
# Run this to verify the avatar-service correctly uses ai-orchestra-simulation

echo "🔍 Verifying Shared Library Implementation"
echo "=========================================="
echo ""

# 1. Check that duplicate directory is removed
echo "✓ Checking duplicate src/ removal..."
if [ -d "microservices/avatar-service/app/src" ]; then
    echo "❌ FAILED: app/src/ still exists (should be removed)"
    exit 1
else
    echo "✅ PASS: app/src/ has been removed"
fi
echo ""

# 2. Check that shared library files exist
echo "✓ Checking shared library files..."
if [ ! -f "ai-orchestra-simulation/index.js" ]; then
    echo "❌ FAILED: ai-orchestra-simulation/index.js missing"
    exit 1
fi
if [ ! -f "ai-orchestra-simulation/package.json" ]; then
    echo "❌ FAILED: ai-orchestra-simulation/package.json missing"
    exit 1
fi
echo "✅ PASS: Shared library files exist"
echo ""

# 3. Check package.json has correct name
echo "✓ Checking package name..."
if grep -q '"@open-talent/ai-orchestra-simulation"' ai-orchestra-simulation/package.json; then
    echo "✅ PASS: Package name is @open-talent/ai-orchestra-simulation"
else
    echo "❌ FAILED: Package name incorrect"
    exit 1
fi
echo ""

# 4. Check avatar_routes.py uses shared library paths
echo "✓ Checking avatar_routes.py integration..."
if grep -q 'ai-orchestra-simulation' microservices/avatar-service/app/routes/avatar_routes.py; then
    echo "✅ PASS: avatar_routes.py references ai-orchestra-simulation"
else
    echo "❌ FAILED: avatar_routes.py doesn't use shared library"
    exit 1
fi
echo ""

# 5. Verify core shared library files exist
echo "✓ Checking core library files..."
CORE_FILES=(
    "ai-orchestra-simulation/src/core/Application.js"
    "ai-orchestra-simulation/src/animation/AnimationController.js"
    "ai-orchestra-simulation/src/animation/MorphTargetAnimationController.js"
    "ai-orchestra-simulation/src/utils/Logger.js"
    "ai-orchestra-simulation/src/ui/GUIManager.js"
)

for file in "${CORE_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ FAILED: $file missing"
        exit 1
    fi
done
echo "✅ PASS: All core library files exist"
echo ""

# 6. Check documentation exists
echo "✓ Checking documentation..."
if [ ! -f "docs/development/AVATAR_SHARED_LIBRARY_GUIDE.md" ]; then
    echo "⚠️  WARNING: AVATAR_SHARED_LIBRARY_GUIDE.md not found"
fi
if [ -f "docs/SHARED_LIBRARY_IMPLEMENTATION.md" ]; then
    echo "✅ PASS: Implementation summary exists"
fi
echo ""

# 7. Show file count comparison
echo "📊 File count analysis:"
ORCHESTRA_FILES=$(find ai-orchestra-simulation/src -type f -name "*.js" 2>/dev/null | wc -l)
echo "   ai-orchestra-simulation/src: $ORCHESTRA_FILES JavaScript files"
echo "   avatar-service/app/src: REMOVED (was duplicate)"
echo ""

# Summary
echo "=========================================="
echo "✅ All verification checks passed!"
echo ""
echo "Next steps:"
echo "1. Test avatar service: cd microservices/avatar-service && uvicorn main:app --port 8001 --reload"
echo "2. Open browser: http://localhost:8001"
echo "3. Check console for any 404 errors"
echo "4. Verify avatar loads and animates correctly"
echo ""
echo "Documentation:"
echo "- Integration guide: docs/development/AVATAR_SHARED_LIBRARY_GUIDE.md"
echo "- Implementation summary: docs/SHARED_LIBRARY_IMPLEMENTATION.md"
echo "- System state: CURRENT_STATE_ANALYSIS.md"
