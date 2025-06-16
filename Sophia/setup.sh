#!/bin/bash

# Sophia Setup Script
# Creates a virtual environment and installs dependencies for Sophia

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ANSI color codes
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}Setting up Sophia...${NC}"

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed or not in the PATH${NC}"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
python_major=$(echo $python_version | cut -d '.' -f 1)
python_minor=$(echo $python_version | cut -d '.' -f 2)

if [ "$python_major" -lt "3" ] || ([ "$python_major" -eq "3" ] && [ "$python_minor" -lt "9" ]); then
    echo -e "${RED}Error: Python 3.9 or higher is required. Found Python $python_version.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements if file exists
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}Installing requirements from requirements.txt...${NC}"
    pip install -r requirements.txt
else
    echo -e "${YELLOW}requirements.txt not found, installing minimal dependencies...${NC}"
    pip install fastapi uvicorn pydantic requests
fi

# Install Sophia in development mode
echo -e "${YELLOW}Installing Sophia in development mode...${NC}"
pip install -e .

# Install optional ML dependencies if available
if pip install torch torchvision --quiet; then
    echo -e "${GREEN}Installed PyTorch${NC}"
else
    echo -e "${YELLOW}Could not install PyTorch. Using minimal ML dependencies.${NC}"
    pip install scikit-learn
fi

# Create necessary directories
echo -e "${YELLOW}Creating data directories...${NC}"
mkdir -p ~/.tekton/data/sophia
mkdir -p "$SCRIPT_DIR/data/metrics"
mkdir -p "$SCRIPT_DIR/data/experiments"
mkdir -p "$SCRIPT_DIR/data/recommendations"
mkdir -p "$SCRIPT_DIR/data/intelligence"
mkdir -p "$SCRIPT_DIR/data/research"
mkdir -p "$SCRIPT_DIR/logs"

# Set permissions for scripts
echo -e "${YELLOW}Setting executable permissions for scripts...${NC}"
chmod +x "$SCRIPT_DIR/scripts/register_with_hermes.py" || echo -e "${YELLOW}Warning: Could not set permissions for register_with_hermes.py${NC}"
chmod +x "$SCRIPT_DIR/../register_with_hermes.py" || echo -e "${YELLOW}Warning: Could not set permissions for register_with_hermes.py${NC}"
chmod +x "$SCRIPT_DIR/../run_sophia.sh" || echo -e "${YELLOW}Warning: Could not set permissions for run_sophia.sh${NC}"

echo -e "${GREEN}Sophia setup complete!${NC}"
echo -e "You can now run Sophia with: ${YELLOW}./run_sophia.sh${NC}"
echo -e "Or register with Hermes using: ${YELLOW}./register_with_hermes.py${NC}"
echo -e "To activate the virtual environment manually, run: ${YELLOW}source venv/bin/activate${NC}\n"

# Deactivate virtual environment
deactivate
