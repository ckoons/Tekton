#!/bin/bash
# Hermes Service Registry & Messaging - Launch Script

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${BLUE}${BOLD}Starting Hermes Service Registry & Messaging...${RESET}"

# Find Tekton root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [[ "$SCRIPT_DIR" == *"/utils" ]]; then
    # Script is running from a symlink in utils
    TEKTON_ROOT=$(cd "$SCRIPT_DIR" && cd "$(readlink "${BASH_SOURCE[0]}" | xargs dirname | xargs dirname)" && pwd)
else
    # Script is running from Hermes directory
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

# Error handling function
handle_error() {
    echo -e "${RED}Error: $1${RESET}" >&2
    exit 1
}

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if port is already in use
if nc -z localhost $HERMES_PORT 2>/dev/null; then
    echo -e "${YELLOW}Hermes is already running on port $HERMES_PORT${RESET}"
    exit 0
fi

# Start the Hermes service
echo -e "${YELLOW}Starting Hermes API server...${RESET}"
python -m hermes > "$LOG_DIR/hermes.log" 2>&1 &
HERMES_PID=$!

# Trap signals for graceful shutdown
trap "kill $HERMES_PID 2>/dev/null; exit" EXIT SIGINT SIGTERM

# Wait for the server to start
echo -e "${YELLOW}Waiting for Hermes to start...${RESET}"
for i in {1..30}; do
    if curl -s http://localhost:$HERMES_PORT/health >/dev/null; then
        echo -e "${GREEN}Hermes started successfully on port $HERMES_PORT${RESET}"
        echo -e "${GREEN}API available at: http://localhost:$HERMES_PORT/api${RESET}"
        echo -e "${GREEN}Registration endpoint: http://localhost:$HERMES_PORT/api/registration${RESET}"
        echo -e "${GREEN}Service discovery: http://localhost:$HERMES_PORT/api/services${RESET}"
        echo -e "${GREEN}Database services: http://localhost:$HERMES_PORT/api/database${RESET}"
        echo -e "${GREEN}A2A services: http://localhost:$HERMES_PORT/api/a2a${RESET}"
        echo -e "${GREEN}MCP services: http://localhost:$HERMES_PORT/api/mcp/v2${RESET}"
        break
    fi
    
    # Check if the process is still running
    if ! kill -0 $HERMES_PID 2>/dev/null; then
        echo -e "${RED}Hermes process terminated unexpectedly${RESET}"
        echo -e "${YELLOW}Showing last 50 lines of log:${RESET}"
        tail -n 50 "$LOG_DIR/hermes.log"
        handle_error "Hermes failed to start"
    fi
    
    echo -n "."
    sleep 1
done

# Keep the script running
echo -e "${BLUE}Hermes is running. Press Ctrl+C to stop.${RESET}"
wait $HERMES_PID