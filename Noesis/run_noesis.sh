#!/bin/bash

# This script starts the Noesis server with the appropriate environment variables

# Ensure the script is run from the Noesis directory
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

# NOESIS_PORT must be set in environment - no hardcoded defaults per Single Port Architecture
if [ -z "$NOESIS_PORT" ]; then
    echo "Error: NOESIS_PORT not set in environment"
    echo "Please configure port in ~/.env.tekton or system environment"
    exit 1
fi

# Start Noesis API server
echo "Starting Noesis on port $NOESIS_PORT..."
echo "TEKTON_REGISTER_AI: ${TEKTON_REGISTER_AI:-false}"
python -m noesis.api "$@"