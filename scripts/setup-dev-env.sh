#!/bin/bash

################################################################################
# OpenTalent Development Environment Setup
# Installs all development standards and security tools
################################################################################

set +e  # Don't exit on error - we want to see all results

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}     OpenTalent Development Environment Setup${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment exists"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Upgrade pip
echo ""
echo -e "${YELLOW}Upgrading pip, setuptools, and wheel...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} pip upgraded"
else
    echo -e "${RED}✗ pip upgrade failed${NC}"
fi

# Install core dependencies
echo ""
echo -e "${YELLOW}Installing base requirements...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Base requirements installed"
    else
        echo -e "${RED}✗ Base requirements installation failed${NC}"
    fi
fi

# Install development dependencies
echo -e "${YELLOW}Installing development requirements...${NC}"
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Development requirements installed"
    else
        echo -e "${RED}✗ Development requirements installation failed${NC}"
    fi
fi

# Install Vetta AI requirements (optional)
echo -e "${YELLOW}Installing Vetta AI requirements (optional)...${NC}"
if [ -f "requirements-vetta.txt" ]; then
    pip install -r requirements-vetta.txt > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Vetta AI requirements installed"
    else
        echo -e "${YELLOW}⚠${NC} Vetta AI requirements skipped (GPU dependencies optional)"
    fi
fi

# Verify key security tools
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}     Verifying Security Tools${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Check ggshield
if command -v ggshield &> /dev/null; then
    GGSHIELD_VERSION=$(ggshield --version 2>&1 | head -1)
    echo -e "${GREEN}✓${NC} ggshield: $GGSHIELD_VERSION"
else
    echo -e "${RED}✗ ggshield not found${NC}"
fi

# Check bandit
if python3 -m bandit --version &> /dev/null; then
    echo -e "${GREEN}✓${NC} bandit: $(python3 -m bandit --version 2>&1 | awk '{print $2}')"
else
    echo -e "${RED}✗ bandit not found${NC}"
fi

# Check safety
if command -v safety &> /dev/null; then
    echo -e "${GREEN}✓${NC} safety: installed"
else
    echo -e "${RED}✗ safety not found${NC}"
fi

# Check ruff
if command -v ruff &> /dev/null; then
    echo -e "${GREEN}✓${NC} ruff: installed"
else
    echo -e "${RED}✗ ruff not found${NC}"
fi

# Verify code quality tools
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}     Verifying Code Quality Tools${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Check black
if command -v black &> /dev/null; then
    echo -e "${GREEN}✓${NC} black: $(black --version 2>&1)"
else
    echo -e "${RED}✗ black not found${NC}"
fi

# Check isort
if command -v isort &> /dev/null; then
    echo -e "${GREEN}✓${NC} isort: installed"
else
    echo -e "${RED}✗ isort not found${NC}"
fi

# Check mypy
if command -v mypy &> /dev/null; then
    echo -e "${GREEN}✓${NC} mypy: $(mypy --version 2>&1)"
else
    echo -e "${RED}✗ mypy not found${NC}"
fi

# Check pytest
if command -v pytest &> /dev/null; then
    echo -e "${GREEN}✓${NC} pytest: $(pytest --version 2>&1)"
else
    echo -e "${RED}✗ pytest not found${NC}"
fi

# Setup pre-commit hooks if .pre-commit-config.yaml exists
if [ -f ".pre-commit-config.yaml" ]; then
    echo ""
    echo -e "${YELLOW}Setting up pre-commit hooks...${NC}"
    pre-commit install > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Pre-commit hooks installed"
    fi
else
    echo ""
    echo -e "${YELLOW}⚠${NC} .pre-commit-config.yaml not found (pre-commit setup skipped)"
fi

# Summary
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Development environment setup complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "  1. Activate environment: source .venv/bin/activate"
echo "  2. Run security scans: ggshield secret scan repo ."
echo "  3. Format code: black ."
echo "  4. Run tests: pytest tests/"
echo "  5. Run linting: ruff check ."
echo ""
