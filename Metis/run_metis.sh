#!/bin/bash

# Run script for Metis component
# This script starts the Metis API server

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${BLUE}${BOLD}Starting Metis Task Decomposition Service...${RESET}"

# Find Tekton root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [[ "$SCRIPT_DIR" == *"/utils" ]]; then
    # Script is running from a symlink in utils
    TEKTON_ROOT=$(cd "$SCRIPT_DIR" && cd "$(readlink "${BASH_SOURCE[0]}" | xargs dirname | xargs dirname)" && pwd)
else
    # Script is running from Metis directory
    TEKTON_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# Ensure we're in the correct directory
cd "$SCRIPT_DIR"

# Set up environment and Python path
source "$TEKTON_ROOT/shared/utils/setup_env.sh"
setup_tekton_env "$SCRIPT_DIR" "$TEKTON_ROOT"

# Create log directories
LOG_DIR="${TEKTON_LOG_DIR:-$TEKTON_ROOT/.tekton/logs}"
mkdir -p "$LOG_DIR"

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if port is already in use
if lsof -Pi :$METIS_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}Port $METIS_PORT is already in use. Metis might already be running.${RESET}"
    exit 1
fi

# Start the Metis service
echo -e "${YELLOW}Starting Metis API server on port $METIS_PORT...${RESET}"
python -m metis > "$LOG_DIR/metis.log" 2>&1 &
METIS_PID=$!

# Trap signals for graceful shutdown
trap "kill $METIS_PID 2>/dev/null; exit" EXIT SIGINT SIGTERM

# Wait for the server to start
echo -e "${YELLOW}Waiting for Metis to start...${RESET}"
for i in {1..30}; do
    if curl -s http://localhost:$METIS_PORT/health >/dev/null 2>&1; then
        echo -e "${GREEN}${BOLD}Metis started successfully!${RESET}"
        echo -e "${GREEN}Service endpoints:${RESET}"
        echo -e "  ${BLUE}Main API:${RESET} http://localhost:$METIS_PORT/api"
        echo -e "  ${BLUE}Health:${RESET} http://localhost:$METIS_PORT/health"
        echo -e "  ${BLUE}Task Decomposition:${RESET} http://localhost:$METIS_PORT/api/tasks/decompose"
        echo -e "  ${BLUE}Telos Integration:${RESET} http://localhost:$METIS_PORT/api/telos"
        break
    fi
    
    # Check if the process is still running
    if ! kill -0 $METIS_PID 2>/dev/null; then
        echo -e "${RED}Metis process terminated unexpectedly${RESET}"
        echo -e "${RED}Last 20 lines of log:${RESET}"
        tail -20 "$LOG_DIR/metis.log"
        exit 1
    fi
    
    echo -n "."
    sleep 1
done

# Keep the script running
echo -e "${BLUE}Metis is running. Press Ctrl+C to stop.${RESET}"
wait $METIS_PID