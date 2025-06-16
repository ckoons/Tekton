#!/bin/bash
# Setup script for Telos component - Requirements Management, Tracing and Validation

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${BLUE}${BOLD}Setting up Telos environment...${RESET}"

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

# Check if requirements.txt exists, create if not
if [ ! -f "requirements.txt" ]; then
    echo -e "${YELLOW}Creating requirements.txt...${RESET}"
    cat > requirements.txt << EOL
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
asyncio
aiohttp
sse-starlette
websockets
matplotlib
networkx
requests
python-multipart
EOL
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${RESET}"
pip install --upgrade pip
pip install -r requirements.txt

# Install Telos in development mode
echo -e "${YELLOW}Installing Telos in development mode...${RESET}"
pip install -e .

# Add parent directory to PYTHONPATH temporarily for imports
export PYTHONPATH="$SCRIPT_DIR/..:$PYTHONPATH"

# Create data directories
echo -e "${YELLOW}Creating data directories...${RESET}"
mkdir -p ~/.tekton/data/telos/requirements

# Create UI directory structure if it doesn't exist
echo -e "${YELLOW}Setting up UI component structure...${RESET}"
mkdir -p ui/templates ui/static/css ui/static/js ui/scripts

# Configure environment variables for Single Port Architecture
echo -e "${YELLOW}Configuring Single Port Architecture...${RESET}"
export TELOS_PORT=8008

# Register with Hermes if available
if command -v python && [ -f "register_with_hermes.py" ]; then
    echo -e "${YELLOW}Registering with Hermes...${RESET}"
    python register_with_hermes.py
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Warning: Hermes registration failed. Will continue anyway.${RESET}"
    fi
else
    echo -e "${YELLOW}Warning: Hermes registration script not found or Python not available.${RESET}"
fi

echo -e "${GREEN}${BOLD}Telos environment setup complete!${RESET}"
echo -e "${BLUE}To activate the environment, run:${RESET}"
echo -e "source $SCRIPT_DIR/venv/bin/activate"
echo -e "\n${BLUE}To start the Telos API server:${RESET}"
echo -e "telos-api"
echo -e "\n${BLUE}To use the Telos CLI:${RESET}"
echo -e "telos --help"
