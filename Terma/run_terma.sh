#!/bin/bash
# Terma Terminal System - Launch Script

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${BLUE}${BOLD}Starting Terma Terminal System...${RESET}"

# Find Tekton root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [[ "$SCRIPT_DIR" == *"/utils" ]]; then
    # Script is running from a symlink in utils
    TEKTON_ROOT=$(cd "$SCRIPT_DIR" && cd "$(readlink "${BASH_SOURCE[0]}" | xargs dirname | xargs dirname)" && pwd)
else
    # Script is running from Terma directory
    TEKTON_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# Ensure we're in the correct directory
cd "$SCRIPT_DIR"

# Set up environment and Python path
source "$TEKTON_ROOT/shared/utils/setup_env.sh"
setup_tekton_env "$SCRIPT_DIR" "$TEKTON_ROOT"

# Set environment variables
export TERMA_WS_PORT=8767
export REGISTER_WITH_HERMES=1

# Create log directories
LOG_DIR="${TEKTON_LOG_DIR:-$TEKTON_ROOT/.tekton/logs}"
mkdir -p "$LOG_DIR"

# Error handling function
handle_error() {
    echo -e "${RED}Error: $1${RESET}" >&2
    ${TEKTON_ROOT}/scripts/tekton-register unregister --component terma
    exit 1
}

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Register with Hermes using tekton-register
echo -e "${YELLOW}Registering Terma with Hermes...${RESET}"
${TEKTON_ROOT}/scripts/tekton-register register --component terma --config ${TEKTON_ROOT}/config/components/terma.yaml &
REGISTER_PID=$!

# Give registration a moment to complete
sleep 2

# Start the Terma service
echo -e "${YELLOW}Starting Terma API server...${RESET}"
python -m terma.api.app --port $TERMA_PORT > "$LOG_DIR/terma.log" 2>&1 &
TERMA_PID=$!

# Trap signals for graceful shutdown
trap "${TEKTON_ROOT}/scripts/tekton-register unregister --component terma; kill $TERMA_PID 2>/dev/null; exit" EXIT SIGINT SIGTERM

# Wait for the server to start
echo -e "${YELLOW}Waiting for Terma to start...${RESET}"
for i in {1..30}; do
    if curl -s http://localhost:$TERMA_PORT/health >/dev/null; then
        echo -e "${GREEN}Terma started successfully on port $TERMA_PORT${RESET}"
        echo -e "${GREEN}API available at: http://localhost:$TERMA_PORT/api${RESET}"
        echo -e "${GREEN}WebSocket available at: ws://localhost:$TERMA_PORT/ws${RESET}"
        break
    fi
    
    # Check if the process is still running
    if ! kill -0 $TERMA_PID 2>/dev/null; then
        echo -e "${RED}Terma process terminated unexpectedly${RESET}"
        cat "$LOG_DIR/terma.log"
        handle_error "Terma failed to start"
    fi
    
    echo -n "."
    sleep 1
done

# Keep the script running to maintain registration
echo -e "${BLUE}Terma is running. Press Ctrl+C to stop.${RESET}"
wait $TERMA_PID