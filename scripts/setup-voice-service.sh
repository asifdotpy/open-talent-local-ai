#!/bin/bash

###############################################################################
# Voice Service Setup Script
# Downloads and configures Piper TTS binary for the voice service
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PIPER_VERSION="2023.11.14-2"
PIPER_PLATFORM="linux_x86_64"
PIPER_TARBALL="piper_${PIPER_PLATFORM}.tar.gz"
PIPER_URL="https://github.com/rhasspy/piper/releases/download/${PIPER_VERSION}/piper_${PIPER_PLATFORM}.tar.gz"
VOICE_SERVICE_DIR="$(dirname "$0")/../microservices/voice-service"
PIPER_DIR="${VOICE_SERVICE_DIR}/piper"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Voice Service Setup Script${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if running from correct directory
if [ ! -d "$(dirname "$0")/../microservices/voice-service" ]; then
    echo -e "${RED}Error: This script must be run from the scripts/ directory${NC}"
    echo -e "${YELLOW}Usage: ./scripts/setup-voice-service.sh${NC}"
    exit 1
fi

# Create piper directory if it doesn't exist
echo -e "${YELLOW}Creating Piper directory...${NC}"
mkdir -p "${PIPER_DIR}"

# Check if Piper is already installed
if [ -f "${PIPER_DIR}/piper" ]; then
    echo -e "${GREEN}Piper is already installed at ${PIPER_DIR}/piper${NC}"
    read -p "Do you want to re-download and reinstall? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Setup cancelled. Existing installation will be used.${NC}"
        exit 0
    fi
    echo -e "${YELLOW}Removing existing installation...${NC}"
    rm -rf "${PIPER_DIR}"/*
fi

# Download Piper TTS binary
echo -e "${YELLOW}Downloading Piper TTS binary...${NC}"
echo -e "URL: ${PIPER_URL}"

cd "${VOICE_SERVICE_DIR}"
if ! curl -L -o "${PIPER_TARBALL}" "${PIPER_URL}"; then
    echo -e "${RED}Error: Failed to download Piper binary${NC}"
    echo -e "${YELLOW}Please check your internet connection and try again${NC}"
    exit 1
fi

# Verify download
if [ ! -f "${PIPER_TARBALL}" ]; then
    echo -e "${RED}Error: Downloaded file not found${NC}"
    exit 1
fi

echo -e "${GREEN}Download complete!${NC}"

# Extract tarball
echo -e "${YELLOW}Extracting Piper binary...${NC}"
if ! tar -xzf "${PIPER_TARBALL}" -C "${PIPER_DIR}"; then
    echo -e "${RED}Error: Failed to extract tarball${NC}"
    rm -f "${PIPER_TARBALL}"
    exit 1
fi

# Clean up tarball (it's gitignored)
echo -e "${YELLOW}Cleaning up downloaded tarball...${NC}"
rm -f "${PIPER_TARBALL}"

# Verify extraction
if [ ! -f "${PIPER_DIR}/piper" ]; then
    echo -e "${RED}Error: Piper binary not found after extraction${NC}"
    echo -e "${YELLOW}Expected location: ${PIPER_DIR}/piper${NC}"
    exit 1
fi

# Make binary executable
echo -e "${YELLOW}Making Piper binary executable...${NC}"
chmod +x "${PIPER_DIR}/piper"

# Download default voice model (optional)
echo -e "\n${YELLOW}Do you want to download the default English voice model? (Recommended)${NC}"
read -p "Download en_US-lessac-medium voice model? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    VOICE_MODEL="en_US-lessac-medium"
    VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
    CONFIG_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
    
    mkdir -p "${VOICE_SERVICE_DIR}/models/voices"
    
    echo -e "${YELLOW}Downloading voice model...${NC}"
    cd "${VOICE_SERVICE_DIR}/models/voices"
    
    if ! curl -L -o "${VOICE_MODEL}.onnx" "${VOICE_URL}"; then
        echo -e "${RED}Warning: Failed to download voice model${NC}"
    else
        echo -e "${GREEN}Voice model downloaded!${NC}"
    fi
    
    if ! curl -L -o "${VOICE_MODEL}.onnx.json" "${CONFIG_URL}"; then
        echo -e "${RED}Warning: Failed to download voice config${NC}"
    else
        echo -e "${GREEN}Voice config downloaded!${NC}"
    fi
fi

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"
if "${PIPER_DIR}/piper" --version 2>&1 | grep -q "piper"; then
    echo -e "${GREEN}✓ Piper installation verified successfully!${NC}"
else
    echo -e "${RED}Warning: Could not verify Piper installation${NC}"
fi

# Display summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"
echo -e "Piper binary location: ${GREEN}${PIPER_DIR}/piper${NC}"
echo -e "Voice models location: ${GREEN}${VOICE_SERVICE_DIR}/models/voices/${NC}\n"

echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Update your voice service configuration to use: ${PIPER_DIR}/piper"
echo -e "2. Configure voice models in voice service settings"
echo -e "3. Start the voice service: ${GREEN}cd microservices/voice-service && python main.py${NC}\n"

echo -e "${GREEN}For more information, see: microservices/voice-service/README.md${NC}\n"
