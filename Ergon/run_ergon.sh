#!/bin/bash
# Ergon Agent System - Launch Script

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${BLUE}${BOLD}Starting Ergon Agent System...${RESET}"

# Find Tekton root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [[ "$SCRIPT_DIR" == *"/utils" ]]; then
    # Script is running from a symlink in utils
    TEKTON_ROOT=$(cd "$SCRIPT_DIR" && cd "$(readlink "${BASH_SOURCE[0]}" | xargs dirname | xargs dirname)" && pwd)
else
    # Script is running from Ergon directory
    TEKTON_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# Ensure we're in the correct directory
cd "$SCRIPT_DIR"

# Set up environment and Python path
source "$TEKTON_ROOT/shared/utils/setup_env.sh"
setup_tekton_env "$SCRIPT_DIR" "$TEKTON_ROOT"

# Load environment configuration
[ -f "$TEKTON_ROOT/.env.tekton" ] && export $(grep -v '^#' "$TEKTON_ROOT/.env.tekton" | xargs)

# Create log directories
LOG_DIR="${TEKTON_LOG_DIR:-$TEKTON_ROOT/.tekton/logs}"
mkdir -p "$LOG_DIR"

# Error handling function
handle_error() {
    echo -e "${RED}Error: $1${RESET}" >&2
    ${TEKTON_ROOT}/scripts/tekton-register unregister --component ergon_core
    exit 1
}

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Register with Hermes using tekton-register
echo -e "${YELLOW}Registering Ergon Core with Hermes...${RESET}"
${TEKTON_ROOT}/scripts/tekton-register register --component ergon_core --config ${TEKTON_ROOT}/config/components/ergon_core.yaml &
REGISTER_PID=$!

# Register Ergon Memory component
echo -e "${YELLOW}Registering Ergon Memory with Hermes...${RESET}"
${TEKTON_ROOT}/scripts/tekton-register register --component ergon_memory --config ${TEKTON_ROOT}/config/components/ergon_memory.yaml &
MEMORY_REGISTER_PID=$!

# Register Ergon Workflow component
echo -e "${YELLOW}Registering Ergon Workflow with Hermes...${RESET}"
${TEKTON_ROOT}/scripts/tekton-register register --component ergon_workflow --config ${TEKTON_ROOT}/config/components/ergon_workflow.yaml &
WORKFLOW_REGISTER_PID=$!

# Give registration a moment to complete
sleep 2

# Start the Ergon service
echo -e "${YELLOW}Starting Ergon API server...${RESET}"
python -m ergon > "$LOG_DIR/ergon.log" 2>&1 &
ERGON_PID=$!

# Trap signals for graceful shutdown
trap "${TEKTON_ROOT}/scripts/tekton-register unregister --component ergon_core; ${TEKTON_ROOT}/scripts/tekton-register unregister --component ergon_memory; ${TEKTON_ROOT}/scripts/tekton-register unregister --component ergon_workflow; kill $ERGON_PID 2>/dev/null; exit" EXIT SIGINT SIGTERM

# Wait for the server to start
echo -e "${YELLOW}Waiting for Ergon to start...${RESET}"
for i in {1..30}; do
    if curl -s http://localhost:$ERGON_PORT/health >/dev/null; then
        echo -e "${GREEN}Ergon started successfully on port $ERGON_PORT${RESET}"
        echo -e "${GREEN}API available at: http://localhost:$ERGON_PORT/api${RESET}"
        echo -e "${GREEN}WebSocket available at: ws://localhost:$ERGON_PORT/ws${RESET}"
        break
    fi
    
    # Check if the process is still running
    if ! kill -0 $ERGON_PID 2>/dev/null; then
        echo -e "${RED}Ergon process terminated unexpectedly${RESET}"
        cat "$LOG_DIR/ergon.log"
        handle_error "Ergon failed to start"
    fi
    
    echo -n "."
    sleep 1
done

# Keep the script running to maintain registration
echo -e "${BLUE}Ergon is running. Press Ctrl+C to stop.${RESET}"
wait $ERGON_PID