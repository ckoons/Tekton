#!/bin/bash
# launch-tekton.sh - Unified script to launch all Tekton components in the correct order
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
TEKTON_DIR="$SCRIPT_DIR"

# Default values
MODEL_TYPE="claude" 
MODEL="claude-3-sonnet-20240229"
CLIENT_ID="tekton"
LAUNCH_UI=true
LAUNCH_ALL=false
INTERACTIVE=true
COMPONENTS=()
DEFAULT_COMPONENTS=("engram" "hermes")

# Save the original working directory
ORIGINAL_DIR="$(pwd)"

# Component directories
HEPHAESTUS_DIR="${TEKTON_DIR}/Hephaestus"
ENGRAM_DIR="${TEKTON_DIR}/Engram"
HERMES_DIR="${TEKTON_DIR}/Hermes"
ERGON_DIR="${TEKTON_DIR}/Ergon"
RHETOR_DIR="${TEKTON_DIR}/Rhetor"
ATHENA_DIR="${TEKTON_DIR}/Athena"
PROMETHEUS_DIR="${TEKTON_DIR}/Prometheus"
HARMONIA_DIR="${TEKTON_DIR}/Harmonia"
SOPHIA_DIR="${TEKTON_DIR}/Sophia"
TELOS_DIR="${TEKTON_DIR}/Telos"

# Function to display usage information
show_usage() {
    echo "Tekton - Unified launcher for all Tekton components"
    echo ""
    echo "Usage: launch-tekton.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --components COMP        Comma-separated list of components to launch:"
    echo "                           all: All available components"
    echo "                           Individual: engram,hermes,ergon,rhetor,athena,prometheus,"
    echo "                                       harmonia,sophia,telos,hephaestus"
    echo "  --model-type TYPE        Type of model to launch: claude, ollama (default: claude)"
    echo "  --model MODEL            Specific model to use (defaults depend on model type)"
    echo "  --client-id ID           Client ID for Engram (default: tekton)"
    echo "  --no-ui                  Don't launch the Hephaestus UI"
    echo "  --non-interactive        Run in non-interactive mode (use defaults for unspecified options)"
    echo "  --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  Launch all components:                 launch-tekton.sh --components all"
    echo "  Launch selected components:            launch-tekton.sh --components engram,hermes,ergon"
    echo "  Launch with Ollama and custom model:   launch-tekton.sh --model-type ollama --model llama3"
}

# Function to check if a process is running
is_running() {
    pgrep -f "$1" >/dev/null
    return $?
}

# Function to prompt user for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local options="$3"
    local response
    
    # If options are provided, show them
    if [ -n "$options" ]; then
        prompt="$prompt ($options)"
    fi
    
    # Show prompt with default
    echo -en "${YELLOW}$prompt ${RESET}[${GREEN}$default${RESET}]: "
    read -r response
    
    # Return user input or default if empty
    echo "${response:-$default}"
}

# Function to prompt for yes/no with default
prompt_yes_no() {
    local prompt="$1"
    local default="$2"
    local response
    
    # Prepare default indicator
    if [ "$default" = "y" ]; then
        local options="Y/n"
    else
        local options="y/N"
    fi
    
    # Show prompt with default
    echo -en "${YELLOW}$prompt ${RESET}[$options]: "
    read -r response
    response=$(echo "$response" | tr '[:upper:]' '[:lower:]')
    
    # Return true (0) for yes, false (1) for no
    if [ -z "$response" ]; then
        [ "$default" = "y" ]
        return $?
    else
        [ "$response" = "y" ] || [ "$response" = "yes" ]
        return $?
    fi
}

# Function to detect and list available components
detect_components() {
    echo -e "${BLUE}Detecting Tekton components...${RESET}"
    
    local components=()
    
    # Check for Hephaestus
    if [ -d "$HEPHAESTUS_DIR" ] && [ -f "$HEPHAESTUS_DIR/hephaestus/ui/main.py" ]; then
        components+=("hephaestus")
        echo -e "${GREEN}✓ Hephaestus (UI System)${RESET}"
    else
        echo -e "${RED}✗ Hephaestus not found or incomplete${RESET}"
    fi
    
    # Check for Engram
    if [ -d "$ENGRAM_DIR" ] && [ -f "$ENGRAM_DIR/core/engram_consolidated" ]; then
        components+=("engram")
        echo -e "${GREEN}✓ Engram (Memory System)${RESET}"
    else
        echo -e "${RED}✗ Engram not found or incomplete${RESET}"
    fi
    
    # Check for Hermes
    if [ -d "$HERMES_DIR" ] && [ -f "$HERMES_DIR/hermes/core/service_discovery.py" ]; then
        components+=("hermes")
        echo -e "${GREEN}✓ Hermes (Database & Messaging)${RESET}"
    else
        echo -e "${YELLOW}⚠ Hermes not found or incomplete${RESET}"
    fi
    
    # Check for Ergon
    if [ -d "$ERGON_DIR" ]; then
        if [ -d "$ERGON_DIR/ergon" ] && [ -f "$ERGON_DIR/ergon/__init__.py" ]; then
            components+=("ergon")
            echo -e "${GREEN}✓ Ergon (Agent System)${RESET}"
        else
            echo -e "${YELLOW}⚠ Ergon found but not fully implemented${RESET}"
        fi
    fi
    
    # Check for Rhetor
    if [ -d "$RHETOR_DIR" ]; then
        if [ -d "$RHETOR_DIR/rhetor" ] && [ -f "$RHETOR_DIR/rhetor/__init__.py" ]; then
            components+=("rhetor")
            echo -e "${GREEN}✓ Rhetor (Communication)${RESET}"
        else
            echo -e "${YELLOW}⚠ Rhetor found but not fully implemented${RESET}"
        fi
    fi
    
    # Check for Telos
    if [ -d "$TELOS_DIR" ]; then
        if [ -d "$TELOS_DIR/telos" ] && [ -f "$TELOS_DIR/telos/__init__.py" ]; then
            components+=("telos")
            echo -e "${GREEN}✓ Telos (User Interface)${RESET}"
        else
            echo -e "${YELLOW}⚠ Telos found but not fully implemented${RESET}"
        fi
    fi
    
    # Check for Prometheus
    if [ -d "$PROMETHEUS_DIR" ] && [ -f "$PROMETHEUS_DIR/prometheus/core/planning_engine.py" ]; then
        components+=("prometheus")
        echo -e "${GREEN}✓ Prometheus (Planning)${RESET}"
    else
        echo -e "${YELLOW}⚠ Prometheus not found or incomplete${RESET}"
    fi
    
    # Check for Harmonia
    if [ -d "$HARMONIA_DIR" ]; then
        if [ -d "$HARMONIA_DIR/harmonia" ] && [ -f "$HARMONIA_DIR/harmonia/core/workflow.py" ]; then
            components+=("harmonia")
            echo -e "${GREEN}✓ Harmonia (Workflow)${RESET}"
        else
            echo -e "${YELLOW}⚠ Harmonia found but not fully implemented${RESET}"
        fi
    fi
    
    # Check for Athena
    if [ -d "$ATHENA_DIR" ]; then
        if [ -d "$ATHENA_DIR/athena" ] && [ -f "$ATHENA_DIR/athena/core/entity.py" ]; then
            components+=("athena")
            echo -e "${GREEN}✓ Athena (Knowledge Graph)${RESET}"
        else
            echo -e "${YELLOW}⚠ Athena found but not fully implemented${RESET}"
        fi
    fi
    
    # Check for Sophia
    if [ -d "$SOPHIA_DIR" ]; then
        if [ -d "$SOPHIA_DIR/sophia" ] && [ -f "$SOPHIA_DIR/sophia/core/ml_engine.py" ]; then
            components+=("sophia")
            echo -e "${GREEN}✓ Sophia (Machine Learning)${RESET}"
        else
            echo -e "${YELLOW}⚠ Sophia found but not fully implemented${RESET}"
        fi
    fi
    
    # Return the list of components
    echo "${components[@]}"
}

# Interactive component selection
select_components() {
    local all_components=("$@")
    local selected_components=()
    
    echo -e "${BLUE}${BOLD}Select components to launch:${RESET}"
    
    # Ask about Hephaestus (UI)
    if [[ " ${all_components[*]} " == *" hephaestus "* ]]; then
        if prompt_yes_no "Launch Hephaestus (UI System)?" "y"; then
            selected_components+=("hephaestus")
        fi
    fi
    
    # Ask about Engram (Memory)
    if [[ " ${all_components[*]} " == *" engram "* ]]; then
        if prompt_yes_no "Launch Engram (Memory System)?" "y"; then
            selected_components+=("engram")
        fi
    fi
    
    # Ask about Hermes (Database)
    if [[ " ${all_components[*]} " == *" hermes "* ]]; then
        if prompt_yes_no "Launch Hermes (Database & Messaging)?" "y"; then
            selected_components+=("hermes")
        fi
    fi
    
    # Ask about Ergon (Agents)
    if [[ " ${all_components[*]} " == *" ergon "* ]]; then
        if prompt_yes_no "Launch Ergon (Agent System)?" "y"; then
            selected_components+=("ergon")
        fi
    fi
    
    # Ask about Rhetor (Communication)
    if [[ " ${all_components[*]} " == *" rhetor "* ]]; then
        if prompt_yes_no "Launch Rhetor (Communication)?" "n"; then
            selected_components+=("rhetor")
        fi
    fi
    
    # Ask about Telos (User Interface)
    if [[ " ${all_components[*]} " == *" telos "* ]]; then
        if prompt_yes_no "Launch Telos (User Interface)?" "n"; then
            selected_components+=("telos")
        fi
    fi
    
    # Ask about Prometheus (Planning)
    if [[ " ${all_components[*]} " == *" prometheus "* ]]; then
        if prompt_yes_no "Launch Prometheus (Planning)?" "n"; then
            selected_components+=("prometheus")
        fi
    fi
    
    # Ask about Harmonia (Workflow)
    if [[ " ${all_components[*]} " == *" harmonia "* ]]; then
        if prompt_yes_no "Launch Harmonia (Workflow)?" "n"; then
            selected_components+=("harmonia")
        fi
    fi
    
    # Ask about Athena (Knowledge Graph)
    if [[ " ${all_components[*]} " == *" athena "* ]]; then
        if prompt_yes_no "Launch Athena (Knowledge Graph)?" "n"; then
            selected_components+=("athena")
        fi
    fi
    
    # Ask about Sophia (Machine Learning)
    if [[ " ${all_components[*]} " == *" sophia "* ]]; then
        if prompt_yes_no "Launch Sophia (Machine Learning)?" "n"; then
            selected_components+=("sophia")
        fi
    fi
    
    echo "${selected_components[@]}"
}

# Launch Hephaestus UI
launch_hephaestus() {
    echo -e "${BLUE}${BOLD}Launching Hephaestus UI...${RESET}"
    
    # Check if Hephaestus is already running
    if is_running "hephaestus.ui.main"; then
        echo -e "${GREEN}Hephaestus UI is already running${RESET}"
        return 0
    fi
    
    # Use the existing Hephaestus launch script
    if [ -x "$TEKTON_DIR/hephaestus_launch" ]; then
        echo -e "${BLUE}Using hephaestus_launch script...${RESET}"
        "$TEKTON_DIR/hephaestus_launch" --port 8080 > "$HOME/.tekton/logs/hephaestus.log" 2>&1 &
        HEPHAESTUS_PID=$!
        
        # Wait briefly to see if it crashed
        sleep 2
        if ps -p $HEPHAESTUS_PID > /dev/null; then
            echo -e "${GREEN}✓ Hephaestus UI started successfully with PID: $HEPHAESTUS_PID${RESET}"
            echo -e "${GREEN}  Access the UI at: http://localhost:8080${RESET}"
            return 0
        else
            echo -e "${RED}✗ Hephaestus UI failed to start${RESET}"
            cat "$HOME/.tekton/logs/hephaestus.log"
            return 1
        fi
    elif [ -x "$HEPHAESTUS_DIR/run_ui.sh" ]; then
        echo -e "${BLUE}Using run_ui.sh script...${RESET}"
        
        # Set up Python path
        export PYTHONPATH="$TEKTON_DIR:$PYTHONPATH"
        
        # Launch the UI server
        (cd "$HEPHAESTUS_DIR" && "./run_ui.sh" --port 8080 > "$HOME/.tekton/logs/hephaestus.log" 2>&1) &
        HEPHAESTUS_PID=$!
        
        # Wait briefly to see if it crashed
        sleep 2
        if ps -p $HEPHAESTUS_PID > /dev/null; then
            echo -e "${GREEN}✓ Hephaestus UI started successfully${RESET}"
            echo -e "${GREEN}  Access the UI at: http://localhost:8080${RESET}"
            return 0
        else
            echo -e "${RED}✗ Hephaestus UI failed to start${RESET}"
            cat "$HOME/.tekton/logs/hephaestus.log"
            return 1
        fi
    else
        echo -e "${RED}✗ No Hephaestus launch script found${RESET}"
        return 1
    fi
}

# Launch Engram component
launch_engram() {
    echo -e "${BLUE}${BOLD}Launching Engram Memory System...${RESET}"
    
    # Check if Engram memory service is already running
    if is_running "engram.api.consolidated_server"; then
        echo -e "${GREEN}Engram memory service is already running${RESET}"
        return 0
    fi
    
    # Find the consolidated server script
    ENGRAM_STARTUP="$ENGRAM_DIR/core/engram_consolidated"
    
    if [ -x "$ENGRAM_STARTUP" ]; then
        # Create data directory
        mkdir -p "$HOME/.tekton/data"
        mkdir -p "$HOME/.tekton/logs"
        
        # First check if Engram is in the Python path
        python3 -c "import engram" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}Adding Engram to Python path...${RESET}"
            export PYTHONPATH="$ENGRAM_DIR:$PYTHONPATH"
            
            # Install Engram package if needed
            if [ -f "$ENGRAM_DIR/setup.py" ]; then
                echo -e "${YELLOW}Installing Engram package...${RESET}"
                (cd "$ENGRAM_DIR" && pip install -e . --quiet)
            fi
        fi
        
        # Start the service
        "$ENGRAM_STARTUP" --data-dir "$HOME/.tekton/data" > "$HOME/.tekton/logs/engram.log" 2>&1 &
        ENGRAM_PID=$!
        
        echo -e "${GREEN}Started Engram memory service with PID: $ENGRAM_PID${RESET}"
        
        # Wait for service to be ready
        echo -e "${BLUE}Waiting for Engram service to be ready...${RESET}"
        for i in {1..15}; do  # Increased timeout
            sleep 2  # Longer sleep
            if ! ps -p $ENGRAM_PID > /dev/null; then
                echo -e "${RED}Memory service failed to start${RESET}"
                cat "$HOME/.tekton/logs/engram.log"
                return 1
            fi
            
            # Try connecting to health endpoint (silent curl)
            if curl -s "http://127.0.0.1:8000/health" > /dev/null 2>&1; then
                echo -e "${GREEN}Engram memory service is online!${RESET}"
                return 0
            fi
            
            echo -n "."
        done
        
        echo ""
        echo -e "${YELLOW}Engram service may not be fully ready, but continuing...${RESET}"
        return 0
    else
        echo -e "${RED}Engram consolidated server script not found at $ENGRAM_STARTUP${RESET}"
        return 1
    fi
}

# Launch Hermes component
launch_hermes() {
    echo -e "${BLUE}${BOLD}Launching Hermes Database & Messaging...${RESET}"
    
    # Check if Hermes is already running
    if is_running "hermes.*database_manager"; then
        echo -e "${GREEN}Hermes services are already running${RESET}"
        return 0
    fi
    
    # Set up Python path
    export PYTHONPATH="$HERMES_DIR:$PYTHONPATH"
    
    # Create data directory
    mkdir -p "$HOME/.tekton/data/hermes"
    
    # Create log directories
    mkdir -p "$HOME/.tekton/logs"

    # Prepare environment variables for Python script
    HERMES_PY_DIR="$HERMES_DIR"
    HOME_PY_DIR="$HOME"
    
    # Launch the database manager
    python3 -c "
import sys, os, subprocess, asyncio
sys.path.insert(0, '$HERMES_DIR')

# Start in a separate process
subprocess.Popen(
    [sys.executable, '-c', '''
import sys, asyncio, os
sys.path.insert(0, \"$HERMES_PY_DIR\")
from hermes.core.database.manager import DatabaseManager

async def run():
    os.makedirs(\"$HOME_PY_DIR/.tekton/data/hermes\", exist_ok=True)
    db_manager = DatabaseManager(
        root_dir=\"$HOME_PY_DIR/.tekton/data/hermes\",
        log_level=\"INFO\"
    )
    await db_manager.start()
    while True:
        await asyncio.sleep(1)

asyncio.run(run())
'''],
    stdout=open(\"$HOME_PY_DIR/.tekton/logs/hermes_db.log\", 'w'),
    stderr=open(\"$HOME_PY_DIR/.tekton/logs/hermes_db.log\", 'w'),
    close_fds=True
)

# Start service registry in a separate process
subprocess.Popen(
    [sys.executable, '-c', '''
import sys, asyncio, os
sys.path.insert(0, \"$HERMES_PY_DIR\")
from hermes.core.service_discovery import ServiceRegistry

async def run():
    registry = ServiceRegistry()
    await registry.start()
    while True:
        await asyncio.sleep(1)

asyncio.run(run())
'''],
    stdout=open(\"$HOME_PY_DIR/.tekton/logs/hermes_registry.log\", 'w'),
    stderr=open(\"$HOME_PY_DIR/.tekton/logs/hermes_registry.log\", 'w'),
    close_fds=True
)

print('${GREEN}Hermes services started successfully${RESET}')
" &
    
    # Give services time to start
    sleep 2
    
    # Check if services started successfully
    if is_running "hermes.*database_manager"; then
        echo -e "${GREEN}Hermes Database Manager is running${RESET}"
        return 0
    else
        echo -e "${RED}Failed to start Hermes services${RESET}"
        cat "$HOME/.tekton/logs/hermes_db.log"
        return 1
    fi
}

# Launch Ergon component
launch_ergon() {
    echo -e "${BLUE}${BOLD}Launching Ergon Agent System...${RESET}"
    
    # Check if Ergon is already running
    if is_running "ergon.core"; then
        echo -e "${GREEN}Ergon services are already running${RESET}"
        return 0
    fi
    
    # Check if Ergon is implemented
    if [ -d "$ERGON_DIR/ergon" ] && [ -f "$ERGON_DIR/ergon/__init__.py" ]; then
        # Set up Python path
        export PYTHONPATH="$ERGON_DIR:$PYTHONPATH"
        
        # Launch Ergon server
        python3 -c "
import sys, os, subprocess
sys.path.insert(0, '$ERGON_DIR')

try:
    # Start Ergon server in a separate process
    subprocess.Popen(
        [sys.executable, '-c', f'''
import sys, asyncio
sys.path.insert(0, '{ERGON_DIR}')
from ergon.core.server import start_server
import os

async def run():
    await start_server()

asyncio.run(run())
'''],
        stdout=open(f'{HOME}/.tekton/logs/ergon.log', 'w'),
        stderr=open(f'{HOME}/.tekton/logs/ergon.log', 'w'),
        close_fds=True
    )
    print('${GREEN}Ergon server started successfully${RESET}')
except Exception as e:
    print(f'${RED}Error starting Ergon server: {e}${RESET}')
" &
        
        # Give services time to start
        sleep 2
        
        echo -e "${GREEN}Ergon agent system initialized${RESET}"
        return 0
    else
        echo -e "${YELLOW}Ergon component is not yet fully implemented${RESET}"
        echo -e "${YELLOW}Skipping Ergon launch${RESET}"
        return 0
    fi
}

# Launch Rhetor component
launch_rhetor() {
    echo -e "${BLUE}${BOLD}Launching Rhetor Communication System...${RESET}"
    
    # Check if Rhetor is already running
    if is_running "rhetor.core"; then
        echo -e "${GREEN}Rhetor services are already running${RESET}"
        return 0
    fi
    
    # Check if Rhetor is implemented
    if [ -d "$RHETOR_DIR/rhetor" ] && [ -f "$RHETOR_DIR/rhetor/__init__.py" ]; then
        # Set up Python path
        export PYTHONPATH="$RHETOR_DIR:$PYTHONPATH"
        
        # Launch Rhetor server if the startup module exists
        if [ -f "$RHETOR_DIR/rhetor/core/server.py" ]; then
            python3 -c "
import sys, os, subprocess
sys.path.insert(0, '$RHETOR_DIR')

try:
    # Start Rhetor server in a separate process
    subprocess.Popen(
        [sys.executable, '-c', f'''
import sys, asyncio
sys.path.insert(0, '{RHETOR_DIR}')
from rhetor.core.server import start_server
import os

async def run():
    await start_server()

asyncio.run(run())
'''],
        stdout=open(f'{HOME}/.tekton/logs/rhetor.log', 'w'),
        stderr=open(f'{HOME}/.tekton/logs/rhetor.log', 'w'),
        close_fds=True
    )
    print('${GREEN}Rhetor server started successfully${RESET}')
except Exception as e:
    print(f'${RED}Error starting Rhetor server: {e}${RESET}')
" &
            
            # Give services time to start
            sleep 2
        fi
        
        echo -e "${GREEN}Rhetor communication system initialized${RESET}"
        return 0
    else
        echo -e "${YELLOW}Rhetor component is not yet fully implemented${RESET}"
        echo -e "${YELLOW}Skipping Rhetor launch${RESET}"
        return 0
    fi
}

# Launch Prometheus component
launch_prometheus() {
    echo -e "${BLUE}${BOLD}Launching Prometheus Planning System...${RESET}"
    
    # Check if Prometheus is already running
    if is_running "prometheus.core"; then
        echo -e "${GREEN}Prometheus services are already running${RESET}"
        return 0
    fi
    
    # Check if Prometheus is implemented
    if [ -d "$PROMETHEUS_DIR/prometheus" ] && [ -f "$PROMETHEUS_DIR/prometheus/core/planning_engine.py" ]; then
        # Set up Python path
        export PYTHONPATH="$PROMETHEUS_DIR:$PYTHONPATH"
        
        # Launch Prometheus if server module exists
        if [ -f "$PROMETHEUS_DIR/prometheus/core/server.py" ]; then
            python3 -c "
import sys, os, subprocess
sys.path.insert(0, '$PROMETHEUS_DIR')

try:
    # Start Prometheus server in a separate process
    subprocess.Popen(
        [sys.executable, '-c', f'''
import sys, asyncio
sys.path.insert(0, '{PROMETHEUS_DIR}')
from prometheus.core.server import start_server
import os

async def run():
    await start_server()

asyncio.run(run())
'''],
        stdout=open(f'{HOME}/.tekton/logs/prometheus.log', 'w'),
        stderr=open(f'{HOME}/.tekton/logs/prometheus.log', 'w'),
        close_fds=True
    )
    print('${GREEN}Prometheus server started successfully${RESET}')
except Exception as e:
    print(f'${RED}Error starting Prometheus server: {e}${RESET}')
" &
            
            # Give services time to start
            sleep 2
        fi
        
        echo -e "${GREEN}Prometheus planning system initialized${RESET}"
        return 0
    else
        echo -e "${YELLOW}Prometheus planning engine is not fully implemented${RESET}"
        echo -e "${YELLOW}Skipping Prometheus launch${RESET}"
        return 0
    fi
}

# Launch Harmonia component
launch_harmonia() {
    echo -e "${BLUE}${BOLD}Launching Harmonia Workflow System...${RESET}"
    
    # Check if Harmonia is already running
    if is_running "harmonia.core"; then
        echo -e "${GREEN}Harmonia services are already running${RESET}"
        return 0
    fi
    
    # Check if Harmonia is implemented
    if [ -d "$HARMONIA_DIR/harmonia" ] && [ -f "$HARMONIA_DIR/harmonia/core/workflow.py" ]; then
        # Set up Python path
        export PYTHONPATH="$HARMONIA_DIR:$PYTHONPATH"
        
        # Launch Harmonia if server module exists
        if [ -f "$HARMONIA_DIR/harmonia/core/server.py" ]; then
            python3 -c "
import sys, os, subprocess
sys.path.insert(0, '$HARMONIA_DIR')

try:
    # Start Harmonia server in a separate process
    subprocess.Popen(
        [sys.executable, '-c', f'''
import sys, asyncio
sys.path.insert(0, '{HARMONIA_DIR}')
from harmonia.core.server import start_server
import os

async def run():
    await start_server()

asyncio.run(run())
'''],
        stdout=open(f'{HOME}/.tekton/logs/harmonia.log', 'w'),
        stderr=open(f'{HOME}/.tekton/logs/harmonia.log', 'w'),
        close_fds=True
    )
    print('${GREEN}Harmonia server started successfully${RESET}')
except Exception as e:
    print(f'${RED}Error starting Harmonia server: {e}${RESET}')
" &
            
            # Give services time to start
            sleep 2
        fi
        
        echo -e "${GREEN}Harmonia workflow system initialized${RESET}"
        return 0
    else
        echo -e "${YELLOW}Harmonia workflow engine is not fully implemented${RESET}"
        echo -e "${YELLOW}Skipping Harmonia launch${RESET}"
        return 0
    fi
}

# Launch Athena component
launch_athena() {
    echo -e "${BLUE}${BOLD}Launching Athena Knowledge Graph...${RESET}"
    
    # Check if Athena is already running
    if is_running "athena.core"; then
        echo -e "${GREEN}Athena services are already running${RESET}"
        return 0
    fi
    
    # Check if Athena is implemented
    if [ -d "$ATHENA_DIR/athena" ] && [ -f "$ATHENA_DIR/athena/core/entity.py" ]; then
        # Set up Python path
        export PYTHONPATH="$ATHENA_DIR:$PYTHONPATH"
        
        # Launch Athena if server module exists
        if [ -f "$ATHENA_DIR/athena/core/server.py" ]; then
            python3 -c "
import sys, os, subprocess
sys.path.insert(0, '$ATHENA_DIR')

try:
    # Start Athena server in a separate process
    subprocess.Popen(
        [sys.executable, '-c', f'''
import sys, asyncio
sys.path.insert(0, '{ATHENA_DIR}')
from athena.core.server import start_server
import os

async def run():
    await start_server()

asyncio.run(run())
'''],
        stdout=open(f'{HOME}/.tekton/logs/athena.log', 'w'),
        stderr=open(f'{HOME}/.tekton/logs/athena.log', 'w'),
        close_fds=True
    )
    print('${GREEN}Athena server started successfully${RESET}')
except Exception as e:
    print(f'${RED}Error starting Athena server: {e}${RESET}')
" &
            
            # Give services time to start
            sleep 2
        fi
        
        echo -e "${GREEN}Athena knowledge graph initialized${RESET}"
        return 0
    else
        echo -e "${YELLOW}Athena knowledge graph is not fully implemented${RESET}"
        echo -e "${YELLOW}Skipping Athena launch${RESET}"
        return 0
    fi
}

# Launch Sophia component
launch_sophia() {
    echo -e "${BLUE}${BOLD}Launching Sophia Machine Learning System...${RESET}"
    
    # Check if Sophia is already running
    if is_running "sophia.core"; then
        echo -e "${GREEN}Sophia services are already running${RESET}"
        return 0
    fi
    
    # Check if Sophia is implemented
    if [ -d "$SOPHIA_DIR/sophia" ] && [ -f "$SOPHIA_DIR/sophia/core/ml_engine.py" ]; then
        # Set up Python path
        export PYTHONPATH="$SOPHIA_DIR:$PYTHONPATH"
        
        # Launch Sophia if server module exists
        if [ -f "$SOPHIA_DIR/sophia/core/server.py" ]; then
            python3 -c "
import sys, os, subprocess
sys.path.insert(0, '$SOPHIA_DIR')

try:
    # Start Sophia server in a separate process
    subprocess.Popen(
        [sys.executable, '-c', f'''
import sys, asyncio
sys.path.insert(0, '{SOPHIA_DIR}')
from sophia.core.server import start_server
import os

async def run():
    await start_server()

asyncio.run(run())
'''],
        stdout=open(f'{HOME}/.tekton/logs/sophia.log', 'w'),
        stderr=open(f'{HOME}/.tekton/logs/sophia.log', 'w'),
        close_fds=True
    )
    print('${GREEN}Sophia server started successfully${RESET}')
except Exception as e:
    print(f'${RED}Error starting Sophia server: {e}${RESET}')
" &
            
            # Give services time to start
            sleep 2
        fi
        
        echo -e "${GREEN}Sophia machine learning system initialized${RESET}"
        return 0
    else
        echo -e "${YELLOW}Sophia machine learning system is not fully implemented${RESET}"
        echo -e "${YELLOW}Skipping Sophia launch${RESET}"
        return 0
    fi
}

# Launch Telos component
launch_telos() {
    echo -e "${BLUE}${BOLD}Launching Telos User Interface...${RESET}"
    
    # Check if Telos is already running
    if is_running "telos.core"; then
        echo -e "${GREEN}Telos services are already running${RESET}"
        return 0
    fi
    
    # Check if Telos is implemented
    if [ -d "$TELOS_DIR/telos" ] && [ -f "$TELOS_DIR/telos/__init__.py" ]; then
        # Set up Python path
        export PYTHONPATH="$TELOS_DIR:$PYTHONPATH"
        
        # Launch Telos if server module exists
        if [ -f "$TELOS_DIR/telos/core/server.py" ]; then
            python3 -c "
import sys, os, subprocess
sys.path.insert(0, '$TELOS_DIR')

try:
    # Start Telos server in a separate process
    subprocess.Popen(
        [sys.executable, '-c', f'''
import sys, asyncio
sys.path.insert(0, '{TELOS_DIR}')
from telos.core.server import start_server
import os

async def run():
    await start_server()

asyncio.run(run())
'''],
        stdout=open(f'{HOME}/.tekton/logs/telos.log', 'w'),
        stderr=open(f'{HOME}/.tekton/logs/telos.log', 'w'),
        close_fds=True
    )
    print('${GREEN}Telos server started successfully${RESET}')
except Exception as e:
    print(f'${RED}Error starting Telos server: {e}${RESET}')
" &
            
            # Give services time to start
            sleep 2
        fi
        
        echo -e "${GREEN}Telos user interface initialized${RESET}"
        return 0
    else
        echo -e "${YELLOW}Telos user interface is not fully implemented${RESET}"
        echo -e "${YELLOW}Skipping Telos launch${RESET}"
        return 0
    fi
}

# Launch AI model (Claude or Ollama)
launch_ai_model() {
    echo -e "${BLUE}${BOLD}Launching $MODEL_TYPE model: $MODEL${RESET}"
    
    case "$MODEL_TYPE" in
        "claude")
            # Check if model is available
            if [ "$MODEL" = "claude-3-sonnet-20240229" ] || [ "$MODEL" = "claude-3-opus-20240229" ] || [ "$MODEL" = "claude-3-5-sonnet" ]; then
                echo -e "${GREEN}Using Claude model: $MODEL${RESET}"
            else
                echo -e "${YELLOW}Requested model '$MODEL' may not be available, attempting to use anyway${RESET}"
            fi
            
            # Set model via env var
            export ANTHROPIC_API_MODEL="$MODEL"
            
            # Launch Claude
            echo -e "${GREEN}Starting Claude with model: $MODEL${RESET}"
            echo -e "${YELLOW}To exit Claude, press Ctrl+D${RESET}"
            echo -e "${BLUE}-----------------------------------------------${RESET}"
            claude --allowedTools='Bash(*),Edit,View,Replace,BatchTool,GlobTool,GrepTool,LS,ReadNotebook,NotebookEditCell,WebFetchTool'
            ;;
            
        "ollama")
            # Check if Ollama is running
            if ! curl -s http://localhost:11434/api/tags > /dev/null; then
                echo -e "${RED}Error: Ollama is not running. Please start Ollama first.${RESET}"
                return 1
            fi
            
            # Find the Ollama bridge script
            OLLAMA_BRIDGE="$ENGRAM_DIR/ollama/ollama_bridge.py"
            
            # Verify the bridge file exists
            if [ ! -f "$OLLAMA_BRIDGE" ]; then
                echo -e "${RED}Error: Ollama bridge script not found at $OLLAMA_BRIDGE${RESET}"
                return 1
            fi
            
            # Add paths to PYTHONPATH
            export PYTHONPATH="$ENGRAM_DIR/ollama:$ENGRAM_DIR:$PYTHONPATH"
            
            # Build command
            CMD="python3 $OLLAMA_BRIDGE $MODEL --prompt-type combined --client-id $CLIENT_ID --temperature 0.7 --max-tokens 2048 --memory-functions"
            
            # Execute the command
            echo -e "${GREEN}Starting Ollama with model: $MODEL${RESET}"
            $CMD
            ;;
            
        *)
            echo -e "${RED}Unknown model type: $MODEL_TYPE${RESET}"
            echo -e "${YELLOW}Supported model types: claude, ollama${RESET}"
            return 1
            ;;
    esac
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --components)
      IFS=',' read -r -a COMPONENTS <<< "$2"
      shift 2
      ;;
    --model-type)
      MODEL_TYPE="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --client-id)
      CLIENT_ID="$2"
      shift 2
      ;;
    --no-ui)
      LAUNCH_UI=false
      shift
      ;;
    --non-interactive)
      INTERACTIVE=false
      shift
      ;;
    --help)
      show_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Try 'launch-tekton.sh --help' for more information."
      exit 1
      ;;
  esac
done

# Display banner
echo -e "${BLUE}${BOLD}====== Tekton Orchestration System ======${RESET}"
echo -e "${GREEN}Tekton installation: $TEKTON_DIR${RESET}"
echo ""

# Create necessary directories
mkdir -p "$HOME/.tekton/data"
mkdir -p "$HOME/.tekton/logs"
echo -e "${GREEN}Ensured data directories exist in $HOME/.tekton${RESET}"

# Detect available components
AVAILABLE_COMPONENTS=($(detect_components))

# If no components specified, check if we're in interactive mode
if [ ${#COMPONENTS[@]} -eq 0 ]; then
    if [ "$INTERACTIVE" = true ]; then
        # Ask user to select components
        COMPONENTS=($(select_components "${AVAILABLE_COMPONENTS[@]}"))
    else
        # Use default components in non-interactive mode
        COMPONENTS=("${DEFAULT_COMPONENTS[@]}")
    fi
fi

# Special case for "all" components
if [[ " ${COMPONENTS[*]} " == *" all "* ]]; then
    COMPONENTS=("${AVAILABLE_COMPONENTS[@]}")
    LAUNCH_ALL=true
fi

# If UI is explicitly disabled, remove hephaestus from components
if [ "$LAUNCH_UI" = false ]; then
    NEW_COMPONENTS=()
    for comp in "${COMPONENTS[@]}"; do
        if [ "$comp" != "hephaestus" ]; then
            NEW_COMPONENTS+=("$comp")
        fi
    done
    COMPONENTS=("${NEW_COMPONENTS[@]}")
fi

# If we're launching all components and UI is not explicitly disabled, ensure hephaestus is in the list
if [ "$LAUNCH_ALL" = true ] && [ "$LAUNCH_UI" = true ]; then
    if [[ ! " ${COMPONENTS[*]} " == *" hephaestus "* ]]; then
        COMPONENTS+=("hephaestus")
    fi
fi

# Display selected components
echo -e "${BLUE}${BOLD}Components to launch:${RESET}"
for comp in "${COMPONENTS[@]}"; do
    echo -e "${GREEN}• $comp${RESET}"
done
echo ""

# Launch components in the correct dependency order
# First: core infrastructure (Engram, Hermes)
for comp in "${COMPONENTS[@]}"; do
    if [ "$comp" = "engram" ]; then
        launch_engram
    elif [ "$comp" = "hermes" ]; then
        launch_hermes
    fi
done

# Second: mid-level components (Ergon, Rhetor, Prometheus, Harmonia)
for comp in "${COMPONENTS[@]}"; do
    if [ "$comp" = "ergon" ]; then
        launch_ergon
    elif [ "$comp" = "rhetor" ]; then
        launch_rhetor
    elif [ "$comp" = "prometheus" ]; then
        launch_prometheus
    elif [ "$comp" = "harmonia" ]; then
        launch_harmonia
    fi
done

# Third: high-level components (Athena, Sophia, Telos)
for comp in "${COMPONENTS[@]}"; do
    if [ "$comp" = "athena" ]; then
        launch_athena
    elif [ "$comp" = "sophia" ]; then
        launch_sophia
    elif [ "$comp" = "telos" ]; then
        launch_telos
    fi
done

# Finally: UI component (Hephaestus)
for comp in "${COMPONENTS[@]}"; do
    if [ "$comp" = "hephaestus" ]; then
        launch_hephaestus
    fi
done

# Ask the user if they want to launch an AI model
if [ "$INTERACTIVE" = true ]; then
    if prompt_yes_no "Would you like to launch an AI model?" "y"; then
        # Ask about model type
        MODEL_TYPE=$(prompt_with_default "Which AI model type would you like to use?" "$MODEL_TYPE" "claude, ollama")
        
        # Ask about specific model
        case "$MODEL_TYPE" in
            "claude")
                MODEL=$(prompt_with_default "Which Claude model would you like to use?" "$MODEL" "claude-3-sonnet-20240229, claude-3-opus-20240229, claude-3-5-sonnet")
                ;;
            "ollama")
                # Try to list available Ollama models
                if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
                    MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    models = data.get('models', [])
    print(', '.join([model.get('name') for model in models]))
except:
    print('llama3, mistral, gemma')
")
                    MODEL=$(prompt_with_default "Which Ollama model would you like to use?" "llama3" "$MODELS")
                else
                    echo -e "${YELLOW}Ollama doesn't appear to be running. Please start it first.${RESET}"
                    MODEL=$(prompt_with_default "Which Ollama model would you like to use?" "llama3" "llama3, mistral, gemma")
                fi
                ;;
        esac
        
        # Launch the selected AI model
        launch_ai_model
    fi
fi

echo ""
echo -e "${GREEN}${BOLD}Tekton components launched successfully!${RESET}"

if [[ " ${COMPONENTS[*]} " == *" hephaestus "* ]]; then
    echo -e "${GREEN}Tekton UI is available at: http://localhost:8080${RESET}"
fi

echo -e "${YELLOW}To stop all Tekton components, run: ./kill-tekton.sh${RESET}"