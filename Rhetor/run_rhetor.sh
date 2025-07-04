#!/bin/bash

# This script starts the Rhetor server with the appropriate environment variables

# Ensure the script is run from the Rhetor directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEKTON_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SCRIPT_DIR"

# Set up environment and Python path
source "$TEKTON_ROOT/shared/utils/setup_env.sh"
setup_tekton_env "$SCRIPT_DIR" "$TEKTON_ROOT"

# Load environment variables if .env file exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# RHETOR_PORT must be set in environment - no hardcoded defaults per Single Port Architecture
if [ -z "$RHETOR_PORT" ]; then
    echo "Error: RHETOR_PORT not set in environment"
    echo "Please configure port in ~/.env.tekton or system environment"
    exit 1
fi

# Parse command line arguments
SKIP_AI_LAUNCH=false
CLEAN_REGISTRY_FIRST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--no-ai-registry)
            SKIP_AI_LAUNCH=true
            echo "Skipping AI specialist launch"
            shift
            ;;
        --clean-registry)
            CLEAN_REGISTRY_FIRST=true
            echo "Will clean entire AI registry before starting"
            shift
            ;;
        *)
            # Pass through other arguments
            break
            ;;
    esac
done

# Clean registry if requested
if [ "$CLEAN_REGISTRY_FIRST" = true ]; then
    echo "Cleaning AI registry..."
    python3 "$TEKTON_ROOT/shared/aish/clean_registry.py" --reset
fi

# Start Rhetor API server
python -m rhetor "$@" &
RHETOR_PID=$!

# Launch AI specialist unless skipped
if [ "$SKIP_AI_LAUNCH" != true ]; then
    echo "Waiting for Rhetor to start..."
    sleep 3
    
    echo "Launching Rhetor AI specialist..."
    python3 "$TEKTON_ROOT/shared/aish/launch_component_ai.py" rhetor
fi

# Wait for Rhetor process
wait $RHETOR_PID
