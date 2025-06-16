#!/bin/bash

# Athena Setup Script
# Creates a virtual environment and installs dependencies for Athena using UV

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ANSI color codes
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${GREEN}Setting up Athena...${NC}"

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed or not in the PATH${NC}"
    exit 1
fi

# Check for UV and install if needed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV not found. Installing...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add UV to PATH if not already added by installer
    if ! command -v uv &> /dev/null; then
        echo -e "${YELLOW}Adding UV to PATH...${NC}"
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment with UV...${NC}"
    uv venv venv --python=python3.10
fi

# Activate virtual environment
source venv/bin/activate

# Install Athena in development mode
echo -e "${YELLOW}Installing Athena and dependencies with UV...${NC}"
uv pip install -e .

# Install Neo4j driver if possible
echo -e "${YELLOW}Attempting to install Neo4j dependencies...${NC}"
if uv pip install -e ".[neo4j]" --quiet; then
    echo -e "${GREEN}Installed Neo4j dependencies${NC}"
else
    echo -e "${YELLOW}Could not install Neo4j dependencies. Using memory adapter.${NC}"
fi

# Install development dependencies
uv pip install pytest pytest-asyncio

# Create data directory
mkdir -p ~/.tekton/data/athena

echo -e "${GREEN}Athena setup complete!${NC}"
echo -e "To activate the virtual environment, run:\n  source venv/bin/activate\n"
