#!/bin/bash
# Setup script for Rhetor LLM Management System

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${BLUE}${BOLD}Setting up Rhetor LLM Management System...${RESET}"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${RESET}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment.${RESET}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${RESET}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${RESET}"
pip install --upgrade pip
pip install -r requirements.txt

# Install Rhetor in development mode
echo -e "${YELLOW}Installing Rhetor in development mode...${RESET}"
pip install -e .

# Add parent directory to PYTHONPATH temporarily for imports
export PYTHONPATH="$SCRIPT_DIR/..:$PYTHONPATH"

# Create directory structure if it doesn't exist
mkdir -p ~/.tekton/data/rhetor/contexts
mkdir -p ~/.tekton/logs
mkdir -p ~/.tekton/config

# Make run scripts executable
echo -e "${YELLOW}Making scripts executable...${RESET}"
chmod +x run_rhetor.sh
chmod +x test_rhetor.py
chmod +x register_with_hermes.py

# Install UI requirements if Hephaestus is being used
if [ -d "../Hephaestus" ]; then
    echo -e "${YELLOW}Hephaestus detected, installing UI dependencies...${RESET}"
    pip install pydantic-settings websockets
fi

echo -e "${GREEN}${BOLD}Rhetor LLM Management System setup complete!${RESET}"
echo -e "${BLUE}Run the following commands to start using Rhetor:${RESET}"
echo -e " - ${YELLOW}Start server:${RESET} ./run_rhetor.sh"
echo -e " - ${YELLOW}Register with Hermes:${RESET} python register_with_hermes.py"
echo -e " - ${YELLOW}Test installation:${RESET} ./test_rhetor.py"
echo -e " - ${YELLOW}Activate environment:${RESET} source $SCRIPT_DIR/venv/bin/activate"
