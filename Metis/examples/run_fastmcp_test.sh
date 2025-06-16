#!/bin/bash

# Test script for Metis FastMCP implementation
# This script starts the Metis service and runs comprehensive FastMCP tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m' 
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Metis FastMCP Test Suite${NC}"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
METIS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if Metis is already running
METIS_PORT=${METIS_PORT:-8011}

echo -e "${YELLOW}📡 Checking if Metis is running on port $METIS_PORT...${NC}"

if curl -s "http://localhost:$METIS_PORT/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Metis is already running${NC}"
    METIS_WAS_RUNNING=true
else
    echo -e "${YELLOW}⚡ Starting Metis service...${NC}"
    METIS_WAS_RUNNING=false
    
    # Start Metis in the background
    cd "$METIS_DIR"
    
    # Set up Python environment if needed
    if [[ -f "requirements.txt" && ! -f ".venv/pyvenv.cfg" ]]; then
        echo -e "${YELLOW}📦 Setting up Python environment...${NC}"
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -e .
    elif [[ -f ".venv/pyvenv.cfg" ]]; then
        source .venv/bin/activate
    fi
    
    # Start Metis service
    python -m metis &
    METIS_PID=$!
    
    # Wait for Metis to start
    echo -e "${YELLOW}⏳ Waiting for Metis to start...${NC}"
    for i in {1..30}; do
        if curl -s "http://localhost:$METIS_PORT/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Metis started successfully${NC}"
            break
        fi
        sleep 1
        if [[ $i -eq 30 ]]; then
            echo -e "${RED}❌ Metis failed to start within 30 seconds${NC}"
            kill $METIS_PID 2>/dev/null || true
            exit 1
        fi
    done
fi

# Function to stop Metis if we started it
cleanup() {
    if [[ $METIS_WAS_RUNNING == "false" && -n $METIS_PID ]]; then
        echo -e "${YELLOW}🛑 Stopping Metis service...${NC}"
        kill $METIS_PID 2>/dev/null || true
        wait $METIS_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Metis service stopped${NC}"
    fi
}

# Set trap to cleanup on script exit
trap cleanup EXIT

# Run the FastMCP tests
echo -e "${YELLOW}🧪 Running FastMCP tests...${NC}"
cd "$SCRIPT_DIR"

# Make sure we have the required dependencies
if ! python -c "import aiohttp" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
    pip install aiohttp
fi

# Run the tests
if python test_fastmcp.py; then
    echo -e "${GREEN}🎉 All FastMCP tests passed!${NC}"
    exit_code=0
else
    echo -e "${RED}❌ Some FastMCP tests failed${NC}"
    exit_code=1
fi

# If we started Metis, the cleanup trap will stop it
exit $exit_code