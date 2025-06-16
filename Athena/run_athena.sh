#!/bin/bash
# Athena Knowledge Graph Engine - Launch Script

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${BLUE}${BOLD}Starting Athena Knowledge Graph Engine...${RESET}"

# Find Tekton root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [[ "$SCRIPT_DIR" == *"/utils" ]]; then
    # Script is running from a symlink in utils
    TEKTON_ROOT=$(cd "$SCRIPT_DIR" && cd "$(readlink "${BASH_SOURCE[0]}" | xargs dirname | xargs dirname)" && pwd)
else
    # Script is running from Athena directory
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
    ${TEKTON_ROOT}/scripts/tekton-register unregister --component athena
    exit 1
}

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Register with Hermes using tekton-register
echo -e "${YELLOW}Registering Athena with Hermes...${RESET}"
${TEKTON_ROOT}/scripts/tekton-register register --component athena --config ${TEKTON_ROOT}/config/components/athena.yaml &
REGISTER_PID=$!

# Give registration a moment to complete
sleep 2

# Start the Athena service
echo -e "${YELLOW}Starting Athena API server...${RESET}"
python -m athena > "$LOG_DIR/athena.log" 2>&1 &
ATHENA_PID=$!

# Trap signals for graceful shutdown
trap "${TEKTON_ROOT}/scripts/tekton-register unregister --component athena; kill $ATHENA_PID 2>/dev/null; exit" EXIT SIGINT SIGTERM

# Wait for the server to start
echo -e "${YELLOW}Waiting for Athena to start...${RESET}"
for i in {1..30}; do
    if curl -s http://localhost:$ATHENA_PORT/health >/dev/null; then
        echo -e "${GREEN}Athena started successfully on port $ATHENA_PORT${RESET}"
        echo -e "${GREEN}API available at: http://localhost:$ATHENA_PORT/api${RESET}"
        echo -e "${GREEN}WebSocket available at: ws://localhost:$ATHENA_PORT/ws${RESET}"
        break
    fi
    
    # Check if the process is still running
    if ! kill -0 $ATHENA_PID 2>/dev/null; then
        echo -e "${RED}Athena process terminated unexpectedly${RESET}"
        cat "$LOG_DIR/athena.log"
        handle_error "Athena failed to start"
    fi
    
    echo -n "."
    sleep 1
done

# Keep the script running to maintain registration
echo -e "${BLUE}Athena is running. Press Ctrl+C to stop.${RESET}"
wait $ATHENA_PID