#!/bin/bash
# Terma setup script

set -e

# ANSI colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}Setting up Terma with UV...${NC}"

# Ensure we have UV
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV not found. Installing...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create venv if it doesn't exist
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}Creating virtual environment with UV...${NC}"
    uv venv "$SCRIPT_DIR/venv" --python=python3.10
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Install dependencies with UV
echo -e "${YELLOW}Installing dependencies with UV...${NC}"
uv pip install -e .

# Create default images directory
if [ ! -f "$SCRIPT_DIR/images/icon.png" ]; then
    echo -e "${YELLOW}Creating placeholder icon image...${NC}"
    mkdir -p "$SCRIPT_DIR/images"
    # This would ideally create or copy a placeholder image, but we'll skip for now
fi

# Create basic Python package structure
mkdir -p "$SCRIPT_DIR/terma"
if [ ! -f "$SCRIPT_DIR/terma/__init__.py" ]; then
    echo -e "${YELLOW}Creating Python package structure...${NC}"
    echo '"""Terma - Terminal integration system for Tekton"""' > "$SCRIPT_DIR/terma/__init__.py"
    echo "__version__ = '0.1.0'" >> "$SCRIPT_DIR/terma/__init__.py"
fi

echo -e "${GREEN}Terma setup complete!${NC}"
echo -e "To activate the environment: source $SCRIPT_DIR/venv/bin/activate"