#!/bin/bash
# Tekton Component Setup with UV

set -e

# ANSI colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m"

COMPONENT_NAME=$1
COMPONENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/$COMPONENT_NAME"

if [ -z "$COMPONENT_NAME" ]; then
    echo -e "${RED}Error: Component name not provided${NC}"
    echo -e "Usage: ./component-setup.sh <component-name>"
    echo -e "Available components:"
    ls -d */ | grep -v "venv\|scripts\|images\|.git" | sed 's#/##g'
    exit 1
fi

if [ ! -d "$COMPONENT_DIR" ]; then
    echo -e "${RED}Error: Component directory not found: $COMPONENT_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}Setting up $COMPONENT_NAME...${NC}"

# Check for UV and install if needed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV not found. Installing...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create environment with UV
if [ ! -d "$COMPONENT_DIR/venv" ]; then
    echo -e "${YELLOW}Creating virtual environment with UV...${NC}"
    uv venv "$COMPONENT_DIR/venv" --python=python3.10
fi

# Install with UV
source "$COMPONENT_DIR/venv/bin/activate"
echo -e "${YELLOW}Installing $COMPONENT_NAME with UV...${NC}"

# If setup.py exists, install with -e
if [ -f "$COMPONENT_DIR/setup.py" ]; then
    uv pip install -e "$COMPONENT_DIR"
# Otherwise, use requirements.txt if it exists
elif [ -f "$COMPONENT_DIR/requirements.txt" ]; then
    uv pip install -r "$COMPONENT_DIR/requirements.txt"
else
    echo -e "${YELLOW}No setup.py or requirements.txt found, skipping package installation${NC}"
fi

# Run component-specific setup if it exists
if [ -f "$COMPONENT_DIR/setup.sh" ]; then
    echo -e "${YELLOW}Running component-specific setup...${NC}"
    bash "$COMPONENT_DIR/setup.sh"
fi

echo -e "${GREEN}$COMPONENT_NAME setup complete!${NC}"
echo -e "To activate the environment: source $COMPONENT_DIR/venv/bin/activate"