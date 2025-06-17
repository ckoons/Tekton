#!/bin/bash
# Hephaestus UI DevTools MCP Server Launch Script

# ANSI color codes
RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
BLUE="\033[94m"
RESET="\033[0m"

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEKTON_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Setup environment
source "$TEKTON_ROOT/shared/utils/setup_env.sh"
setup_tekton_env "$SCRIPT_DIR" "$TEKTON_ROOT"

# Set component-specific environment
export HEPHAESTUS_MCP_PORT="${HEPHAESTUS_MCP_PORT:-8088}"
export TEKTON_COMPONENT="hephaestus_mcp"

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Hephaestus UI DevTools MCP Server management script"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -r, --remove   Remove/kill existing MCP server and free the port"
    echo ""
    echo "Without options: Kill any existing MCP server and start a new one"
    echo ""
    echo "Port: $HEPHAESTUS_MCP_PORT"
    echo "Component: $TEKTON_COMPONENT"
}

# Function to kill existing MCP server
kill_mcp_server() {
    echo -e "${YELLOW}Checking for existing MCP server on port $HEPHAESTUS_MCP_PORT...${RESET}"
    
    # Find process using the port
    if command -v lsof >/dev/null 2>&1; then
        # Get PID using lsof
        PIDS=$(lsof -ti:$HEPHAESTUS_MCP_PORT)
        if [ ! -z "$PIDS" ]; then
            echo -e "${YELLOW}Found MCP server process(es): $PIDS${RESET}"
            for PID in $PIDS; do
                echo -e "${RED}Killing process $PID...${RESET}"
                kill -9 $PID 2>/dev/null || true
            done
            echo -e "${GREEN}MCP server stopped and port $HEPHAESTUS_MCP_PORT freed${RESET}"
            sleep 1  # Give the OS time to free the port
        else
            echo -e "${GREEN}No MCP server running on port $HEPHAESTUS_MCP_PORT${RESET}"
        fi
    else
        # Fallback: try to find python processes running mcp_server
        PIDS=$(ps aux | grep -E "python.*mcp_server" | grep -v grep | awk '{print $2}')
        if [ ! -z "$PIDS" ]; then
            echo -e "${YELLOW}Found MCP server process(es): $PIDS${RESET}"
            for PID in $PIDS; do
                echo -e "${RED}Killing process $PID...${RESET}"
                kill -9 $PID 2>/dev/null || true
            done
            echo -e "${GREEN}MCP server processes killed${RESET}"
            sleep 1
        else
            echo -e "${GREEN}No MCP server processes found${RESET}"
        fi
    fi
}

# Function to start MCP server
start_mcp_server() {
    echo -e "${BLUE}Starting Hephaestus UI DevTools MCP Server...${RESET}"
    echo "Port: $HEPHAESTUS_MCP_PORT"
    echo "Component: $TEKTON_COMPONENT"
    
    # Ensure log directory exists
    LOG_DIR="${TEKTON_LOG_DIR:-$TEKTON_ROOT/.tekton/logs}"
    mkdir -p "$LOG_DIR"
    
    # Set up log file path
    LOG_FILE="$LOG_DIR/hephaestus_mcp.log"
    
    echo -e "${GREEN}Logging to: $LOG_FILE${RESET}"
    
    # Remove any existing log file
    if [ -f "$LOG_FILE" ]; then
	echo -e "${YELLOW}Removing existing log file...${RESET}"
	rm "$LOG_FILE"
    fi
    
    # Change to script directory and start server
    cd "$SCRIPT_DIR"
    
    # Start server and redirect output to log file
    # Keep stdout/stderr for startup messages, but also log to file
    python -m hephaestus.mcp.mcp_server 2>&1 | tee -a "$LOG_FILE"
}

# Parse command line arguments
case "$1" in
    -h|--help)
        show_usage
        exit 0
        ;;
    -r|--remove)
        kill_mcp_server
        exit 0
        ;;
    "")
        # Default behavior: kill existing and start new
        kill_mcp_server
        start_mcp_server
        ;;
    *)
        echo -e "${RED}Unknown option: $1${RESET}"
        echo ""
        show_usage
        exit 1
        ;;
esac
