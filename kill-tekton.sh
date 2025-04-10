#!/bin/bash
# kill-tekton.sh - Master script to stop all Tekton components and AI services
# Created: April 11, 2025

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

# Find Tekton root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Display information
echo -e "${BLUE}${BOLD}====== Tekton Shutdown ======${RESET}"
echo -e "${BLUE}Tekton installation: ${YELLOW}$SCRIPT_DIR${RESET}"
echo ""

# Function to check if a process is running
is_running() {
    pgrep -f "$1" >/dev/null
    return $?
}

# Function to kill all processes matching a pattern
kill_processes() {
    local pattern="$1"
    local description="$2"
    
    if is_running "$pattern"; then
        echo -e "${YELLOW}Shutting down $description...${RESET}"
        pkill -f "$pattern"
        sleep 1
        
        # Check if it was killed
        if ! is_running "$pattern"; then
            echo -e "${GREEN}✓ Successfully shut down $description${RESET}"
            return 0
        else
            echo -e "${RED}✗ Failed to shut down $description gracefully, using SIGKILL${RESET}"
            pkill -9 -f "$pattern"
            if ! is_running "$pattern"; then
                echo -e "${GREEN}✓ Successfully force-killed $description${RESET}"
                return 0
            else
                echo -e "${RED}✗ Failed to kill $description${RESET}"
                return 1
            fi
        fi
    else
        echo -e "${GREEN}$description not running${RESET}"
        return 0
    fi
}

# Kill Claude AI processes
kill_processes "claude" "Claude AI"

# Kill Ollama processes that might have been launched by Tekton
kill_processes "ollama_bridge.py" "Ollama bridge"

# Kill Tekton components in reverse dependency order
kill_processes "sophia.core" "Sophia (ML Engine)"
kill_processes "athena.core" "Athena (Knowledge Graph)"
kill_processes "prometheus.core" "Prometheus (Planning)"
kill_processes "harmonia.core" "Harmonia (Workflow)"
kill_processes "telos.core" "Telos (User Interface)"
kill_processes "rhetor.core" "Rhetor (Context Manager)"
kill_processes "ergon.core" "Ergon (Agent System)"
kill_processes "engram_with_ollama" "Engram+Ollama"
kill_processes "engram_with_claude" "Engram+Claude"
kill_processes "engram.api.consolidated_server" "Engram Memory Server"
kill_processes "hermes.*database_manager" "Hermes Database"
kill_processes "hephaestus.ui.main" "Hephaestus UI"

# Kill any Python processes related to Tekton
echo -e "${YELLOW}Checking for any remaining Tekton Python processes...${RESET}"
if pgrep -f "$SCRIPT_DIR.*python" >/dev/null; then
    echo -e "${YELLOW}Killing remaining Python processes in Tekton directory...${RESET}"
    pkill -f "$SCRIPT_DIR.*python"
    sleep 1
    if pgrep -f "$SCRIPT_DIR.*python" >/dev/null; then
        echo -e "${RED}Some Python processes could not be killed. You may want to check them manually:${RESET}"
        ps aux | grep "$SCRIPT_DIR.*python" | grep -v grep
    else
        echo -e "${GREEN}✓ All remaining Python processes killed${RESET}"
    fi
else
    echo -e "${GREEN}No remaining Tekton Python processes found${RESET}"
fi

# Kill any Node.js processes related to Hephaestus UI if running
if pgrep -f "node.*$SCRIPT_DIR/Hephaestus" >/dev/null; then
    echo -e "${YELLOW}Killing Hephaestus UI Node.js processes...${RESET}"
    pkill -f "node.*$SCRIPT_DIR/Hephaestus"
    sleep 1
    if ! pgrep -f "node.*$SCRIPT_DIR/Hephaestus" >/dev/null; then
        echo -e "${GREEN}✓ Successfully killed Hephaestus UI Node.js processes${RESET}"
    else
        echo -e "${RED}Failed to kill some Hephaestus UI Node.js processes${RESET}"
    fi
fi

echo ""
echo -e "${GREEN}${BOLD}Tekton shutdown complete.${RESET}"