#!/bin/bash
# Tekton Core Orchestration System - Launch Script

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${BLUE}${BOLD}Starting Tekton Core Orchestration System...${RESET}"

# Find Tekton root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [[ "$SCRIPT_DIR" == *"/utils" ]]; then
    # Script is running from a symlink in utils
    TEKTON_ROOT=$(cd "$SCRIPT_DIR" && cd "$(readlink "${BASH_SOURCE[0]}" | xargs dirname | xargs dirname)" && pwd)
else
    # Script is running from Tekton Core directory
    TEKTON_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# Ensure we're in the correct directory
cd "$SCRIPT_DIR"

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR:$TEKTON_ROOT:$PYTHONPATH"

# Create necessary directories
LOG_DIR="${TEKTON_LOG_DIR:-$TEKTON_ROOT/.tekton/logs}"
mkdir -p "$LOG_DIR"
mkdir -p "$TEKTON_ROOT/.tekton/data/tekton_core"

# Error handling function
handle_error() {
    echo -e "${RED}Error: $1${RESET}" >&2
    ${TEKTON_ROOT}/scripts/tekton-register unregister --component tekton-core
    exit 1
}

# Check if config exists
if [ ! -f "${TEKTON_ROOT}/config/components/tekton-core.yaml" ]; then
    echo -e "${YELLOW}Tekton Core component config not found, generating it...${RESET}"
    ${TEKTON_ROOT}/scripts/tekton-register generate --component tekton-core --name "Tekton Core" --port $TEKTON_CORE_PORT --output "${TEKTON_ROOT}/config/components/tekton-core.yaml"
fi

# Register with Hermes using tekton-register
echo -e "${YELLOW}Registering Tekton Core with Hermes...${RESET}"
${TEKTON_ROOT}/scripts/tekton-register register --component tekton-core --config ${TEKTON_ROOT}/config/components/tekton-core.yaml &
REGISTER_PID=$!

# Give registration a moment to complete
sleep 2

# Start the Tekton Core service
echo -e "${YELLOW}Starting Tekton Core API server...${RESET}"
python -m tekton.api.app > "$LOG_DIR/tekton_core.log" 2>&1 &
TEKTON_CORE_PID=$!

# Trap signals for graceful shutdown
trap "${TEKTON_ROOT}/scripts/tekton-register unregister --component tekton-core; kill $TEKTON_CORE_PID 2>/dev/null; exit" EXIT SIGINT SIGTERM

# Wait for the server to start
echo -e "${YELLOW}Waiting for Tekton Core to start...${RESET}"
for i in {1..30}; do
    if curl -s http://localhost:$TEKTON_CORE_PORT/health >/dev/null; then
        echo -e "${GREEN}Tekton Core started successfully on port $TEKTON_CORE_PORT${RESET}"
        echo -e "${GREEN}API available at: http://localhost:$TEKTON_CORE_PORT/api${RESET}"
        break
    fi
    
    # Check if the process is still running
    if ! kill -0 $TEKTON_CORE_PID 2>/dev/null; then
        echo -e "${RED}Tekton Core process terminated unexpectedly${RESET}"
        cat "$LOG_DIR/tekton_core.log"
        handle_error "Tekton Core failed to start"
    fi
    
    echo -n "."
    sleep 1
done

# Keep the script running to maintain registration
echo -e "${BLUE}Tekton Core is running. Press Ctrl+C to stop.${RESET}"
wait $TEKTON_CORE_PID
