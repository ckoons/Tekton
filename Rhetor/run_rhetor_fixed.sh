#!/bin/bash
# Rhetor LLM Management System - Launch Script with Process Group Management
# This version properly handles process groups for clean shutdown of all children

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${BLUE}${BOLD}Starting Rhetor LLM Management System...${RESET}"

# Find Tekton root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [[ "$SCRIPT_DIR" == *"/utils" ]]; then
    # Script is running from a symlink in utils
    TEKTON_ROOT=$(cd "$SCRIPT_DIR" && cd "$(readlink "${BASH_SOURCE[0]}" | xargs dirname | xargs dirname)" && pwd)
else
    # Script is running from Rhetor directory
    TEKTON_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# Ensure we're in the correct directory
cd "$SCRIPT_DIR"

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR:$TEKTON_ROOT:$PYTHONPATH"

# Create necessary directories
LOG_DIR="${TEKTON_LOG_DIR:-$TEKTON_ROOT/.tekton/logs}"
mkdir -p "$LOG_DIR"
mkdir -p "$TEKTON_ROOT/.tekton/pids"

# Error handling function
handle_error() {
    echo -e "${RED}Error: $1${RESET}" >&2
    # Clean up PID file
    rm -f "$TEKTON_ROOT/.tekton/pids/rhetor.pid"
    exit 1
}

# Cleanup function for graceful shutdown
cleanup() {
    echo -e "${YELLOW}Cleaning up Rhetor...${RESET}"
    
    # Rhetor will unregister from Hermes automatically in its shutdown event
    
    # Remove PID file
    rm -f "$TEKTON_ROOT/.tekton/pids/rhetor.pid"
    
    echo -e "${GREEN}Rhetor shutdown complete${RESET}"
}

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Rhetor will register with Hermes automatically on startup via HermesRegistration class
echo -e "${YELLOW}Rhetor will register with Hermes on startup...${RESET}"

# Start the Rhetor service in background
echo -e "${YELLOW}Starting Rhetor API server...${RESET}"

# Start Python in background - this works identically on macOS and Linux
python -m rhetor > "$LOG_DIR/rhetor.log" 2>&1 &
RHETOR_PID=$!

# Store the process ID
echo $RHETOR_PID > "$TEKTON_ROOT/.tekton/pids/rhetor.pid"
echo -e "${YELLOW}Rhetor process ID: $RHETOR_PID${RESET}"

# Enhanced signal handling
handle_shutdown() {
    echo -e "\n${YELLOW}Received shutdown signal, terminating Rhetor...${RESET}"
    
    # Send SIGTERM to Rhetor (works on both macOS and Linux)
    if [ -n "$RHETOR_PID" ]; then
        kill -TERM $RHETOR_PID 2>/dev/null
        
        # Wait up to 5 seconds for graceful shutdown
        for i in {1..5}; do
            if ! kill -0 $RHETOR_PID 2>/dev/null; then
                echo -e "${GREEN}Rhetor terminated gracefully${RESET}"
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if kill -0 $RHETOR_PID 2>/dev/null; then
            echo -e "${YELLOW}Force killing Rhetor...${RESET}"
            kill -KILL $RHETOR_PID 2>/dev/null
        fi
    fi
    
    # Run cleanup
    cleanup
    exit 0
}

# Trap signals for graceful shutdown of entire process group
trap 'handle_shutdown' SIGTERM SIGINT SIGHUP

# Wait for the server to start
echo -e "${YELLOW}Waiting for Rhetor to start...${RESET}"
for i in {1..30}; do
    if curl -s http://localhost:$RHETOR_PORT/health >/dev/null; then
        echo -e "${GREEN}Rhetor started successfully on port $RHETOR_PORT${RESET}"
        echo -e "${GREEN}API available at: http://localhost:$RHETOR_PORT/api${RESET}"
        echo -e "${GREEN}WebSocket available at: ws://localhost:$RHETOR_PORT/ws${RESET}"
        echo -e "${BLUE}Rhetor ready for CI model spawning${RESET}"
        break
    fi
    
    # Check if the process is still running
    if ! kill -0 $RHETOR_PID 2>/dev/null; then
        echo -e "${RED}Rhetor process terminated unexpectedly${RESET}"
        tail -n 50 "$LOG_DIR/rhetor.log"
        handle_error "Rhetor failed to start"
    fi
    
    echo -n "."
    sleep 1
done

# Keep the script running to maintain registration and handle signals
echo -e "${BLUE}Rhetor is running. Press Ctrl+C to stop.${RESET}"

# Wait for the Rhetor process
wait $RHETOR_PID

# If we get here, Rhetor exited on its own
echo -e "${YELLOW}Rhetor process exited${RESET}"
cleanup
