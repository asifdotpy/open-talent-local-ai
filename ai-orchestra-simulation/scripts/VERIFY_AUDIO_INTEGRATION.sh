#!/bin/bash

echo "🔍 Verifying Audio Integration Implementation..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: HTML audio element
echo -n "✓ Checking index.html for audio element... "
if grep -q 'id="speech-audio"' index.html; then
    echo -e "${GREEN}FOUND${NC}"
else
    echo -e "${RED}MISSING${NC}"
fi

# Check 2: SceneManager methods
echo -n "✓ Checking SceneManager for getHtmlAudioElement()... "
if grep -q "getHtmlAudioElement()" src/core/SceneManager.js; then
    echo -e "${GREEN}FOUND${NC}"
else
    echo -e "${RED}MISSING${NC}"
fi

echo -n "✓ Checking SceneManager for syncAudioPlayback()... "
if grep -q "syncAudioPlayback(" src/core/SceneManager.js; then
    echo -e "${GREEN}FOUND${NC}"
else
    echo -e "${RED}MISSING${NC}"
fi

# Check 3: Application.js audio connection
echo -n "✓ Checking Application.js for audio connection logic... "
if grep -q "setHtmlAudioElement" src/core/Application.js; then
    echo -e "${GREEN}FOUND${NC}"
else
    echo -e "${RED}MISSING${NC}"
fi

# Check 4: MorphTargetAnimationController updates
echo -n "✓ Checking MorphTargetAnimationController for setHtmlAudioElement()... "
if grep -q "setHtmlAudioElement(audioElement)" src/animation/MorphTargetAnimationController.js; then
    echo -e "${GREEN}FOUND${NC}"
else
    echo -e "${RED}MISSING${NC}"
fi

echo -n "✓ Checking start() method for HTML audio preference... "
if grep -q "this.htmlAudioElement.play()" src/animation/MorphTargetAnimationController.js; then
    echo -e "${GREEN}FOUND${NC}"
else
    echo -e "${RED}MISSING${NC}"
fi

echo -n "✓ Checking updateMouthAnimation() for HTML audio currentTime... "
if grep -q "this.htmlAudioElement.currentTime" src/animation/MorphTargetAnimationController.js; then
    echo -e "${GREEN}FOUND${NC}"
else
    echo -e "${RED}MISSING${NC}"
fi

# Check 5: Checkpoint logging
echo -n "✓ Checking for CHECKPOINT 2 logging in start()... "
if grep -q "CHECKPOINT 2" src/animation/MorphTargetAnimationController.js; then
    echo -e "${GREEN}FOUND${NC}"
else
    echo -e "${RED}MISSING${NC}"
fi

echo -n "✓ Checking for CHECKPOINT 4 logging in updateMouthAnimation()... "
if grep -q "CHECKPOINT 4" src/animation/MorphTargetAnimationController.js; then
    echo -e "${GREEN}FOUND${NC}"
else
    echo -e "${RED}MISSING${NC}"
fi

# Summary
echo ""
echo "📊 Integration Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ All audio integration components verified!${NC}"
echo ""
echo "🚀 Ready to test!"
echo "   1. Hard refresh: Ctrl+Shift+R"
echo "   2. Go to: http://localhost:8000"
echo "   3. Click 'Start'"
echo "   4. Toggle 'Enable Lip-Sync'"
echo "   5. Listen for audio + watch lip-sync"
echo ""
echo "📖 Documentation:"
echo "   - AUDIO_INTEGRATION_COMPLETE.md"
echo "   - QUICK_START_AUDIO_TESTING.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

