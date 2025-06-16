#!/bin/bash
# Hephaestus UI - Launch Script

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${BLUE}${BOLD}Starting Hephaestus UI Server...${RESET}"

# Find Tekton root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [[ "$SCRIPT_DIR" == *"/utils" ]]; then
    # Script is running from a symlink in utils
    TEKTON_ROOT=$(cd "$SCRIPT_DIR" && cd "$(readlink "${BASH_SOURCE[0]}" | xargs dirname | xargs dirname)" && pwd)
else
    # Script is running from Hephaestus directory
    TEKTON_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# Ensure we're in the correct directory
cd "$SCRIPT_DIR"

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR:$TEKTON_ROOT:$PYTHONPATH"

# Create log directories
LOG_DIR="${TEKTON_LOG_DIR:-$TEKTON_ROOT/.tekton/logs}"
mkdir -p "$LOG_DIR"

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if port is already in use
if lsof -Pi :$HEPHAESTUS_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}Port $HEPHAESTUS_PORT is already in use. Hephaestus might already be running.${RESET}"
    exit 1
fi

# Start the Hephaestus UI server using the component-based approach
echo -e "${YELLOW}Starting Hephaestus UI server on port $HEPHAESTUS_PORT...${RESET}"
python3 -m hephaestus > "$LOG_DIR/hephaestus.log" 2>&1 &
HEPHAESTUS_PID=$!

# Trap signals for graceful shutdown
trap "kill $HEPHAESTUS_PID 2>/dev/null; exit" EXIT SIGINT SIGTERM

# Wait for the server to start
echo -e "${YELLOW}Waiting for Hephaestus to start...${RESET}"
for i in {1..30}; do
    if curl -s http://localhost:$HEPHAESTUS_PORT/ >/dev/null 2>&1; then
        echo -e "${GREEN}${BOLD}Hephaestus UI started successfully!${RESET}"
        echo -e "${GREEN}UI available at: http://localhost:$HEPHAESTUS_PORT/${RESET}"
        break
    fi
    
    # Check if the process is still running
    if ! kill -0 $HEPHAESTUS_PID 2>/dev/null; then
        echo -e "${RED}Hephaestus process terminated unexpectedly${RESET}"
        echo -e "${RED}Last 20 lines of log:${RESET}"
        tail -20 "$LOG_DIR/hephaestus.log"
        exit 1
    fi
    
    echo -n "."
    sleep 1
done

# Keep the script running
echo -e "${BLUE}Hephaestus is running. Press Ctrl+C to stop.${RESET}"
wait $HEPHAESTUS_PID