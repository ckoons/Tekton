#!/bin/bash

# FastMCP Server run script for Telos
# This script runs the FastMCP-enabled Telos server on a separate port

# Set the script directory and component path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPONENT_PATH="$SCRIPT_DIR"

# Set Python path to include the component
export PYTHONPATH="$COMPONENT_PATH:${PYTHONPATH:-}"

# Set Telos storage directory
export TELOS_STORAGE_DIR="${TELOS_STORAGE_DIR:-$COMPONENT_PATH/data/requirements}"

# Ensure storage directory exists
mkdir -p "$TELOS_STORAGE_DIR"

# Set log level
export TELOS_LOG_LEVEL="${TELOS_LOG_LEVEL:-info}"

echo "========================================"
echo "Starting Telos FastMCP Server"
echo "========================================"
echo "Component Path: $COMPONENT_PATH"
echo "Storage Directory: $TELOS_STORAGE_DIR"
echo "Log Level: $TELOS_LOG_LEVEL"
echo "Python Path: $PYTHONPATH"
echo "========================================"

# Run the FastMCP server
cd "$COMPONENT_PATH"
python -m telos.api.fastmcp_endpoints