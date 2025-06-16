#!/bin/bash

# Test script for Prometheus FastMCP implementation
# This script starts the Prometheus service and runs comprehensive FastMCP tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m' 
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Prometheus FastMCP Test Suite${NC}"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMETHEUS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if Prometheus is already running
PROMETHEUS_PORT=${PROMETHEUS_PORT:-8006}

echo -e "${YELLOW}📡 Checking if Prometheus is running on port $PROMETHEUS_PORT...${NC}"

if curl -s "http://localhost:$PROMETHEUS_PORT/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus is already running${NC}"
    PROMETHEUS_WAS_RUNNING=true
else
    echo -e "${YELLOW}⚡ Starting Prometheus service...${NC}"
    PROMETHEUS_WAS_RUNNING=false
    
    # Start Prometheus in the background
    cd "$PROMETHEUS_DIR"
    
    # Set up Python environment if needed
    if [[ -f "setup.py" && ! -f ".venv/pyvenv.cfg" ]]; then
        echo -e "${YELLOW}📦 Setting up Python environment...${NC}"
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -e .
    elif [[ -f ".venv/pyvenv.cfg" ]]; then
        source .venv/bin/activate
    fi
    
    # Start Prometheus service
    python -m prometheus.api.app &
    PROMETHEUS_PID=$!
    
    # Wait for Prometheus to start
    echo -e "${YELLOW}⏳ Waiting for Prometheus to start...${NC}"
    for i in {1..30}; do
        if curl -s "http://localhost:$PROMETHEUS_PORT/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Prometheus started successfully${NC}"
            break
        fi
        sleep 1
        if [[ $i -eq 30 ]]; then
            echo -e "${RED}❌ Prometheus failed to start within 30 seconds${NC}"
            kill $PROMETHEUS_PID 2>/dev/null || true
            exit 1
        fi
    done
fi

# Function to stop Prometheus if we started it
cleanup() {
    if [[ $PROMETHEUS_WAS_RUNNING == "false" && -n $PROMETHEUS_PID ]]; then
        echo -e "${YELLOW}🛑 Stopping Prometheus service...${NC}"
        kill $PROMETHEUS_PID 2>/dev/null || true
        wait $PROMETHEUS_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Prometheus service stopped${NC}"
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

# If we started Prometheus, the cleanup trap will stop it
exit $exit_code