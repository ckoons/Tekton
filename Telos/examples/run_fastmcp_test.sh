#!/bin/bash

# Test script for Telos FastMCP implementation
# This script runs the comprehensive test suite for Telos FastMCP

# Set the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPONENT_PATH="$(dirname "$SCRIPT_DIR")"

# Set Python path to include the component and tekton-core
export PYTHONPATH="$COMPONENT_PATH:${PYTHONPATH:-}"

# Set Telos configuration
export TELOS_STORAGE_DIR="${TELOS_STORAGE_DIR:-$COMPONENT_PATH/data/requirements}"

# Ensure storage directory exists
mkdir -p "$TELOS_STORAGE_DIR"

echo "========================================"
echo "Telos FastMCP Test Suite"
echo "========================================"
echo "Component Path: $COMPONENT_PATH"
echo "Storage Directory: $TELOS_STORAGE_DIR"
echo "Python Path: $PYTHONPATH"
echo "========================================"

# Check if Telos server is running
TELOS_URL="${TELOS_URL:-http://localhost:8008}"
echo "Testing Telos server at: $TELOS_URL"

# Run the test script
cd "$COMPONENT_PATH"
python examples/test_fastmcp.py --url "$TELOS_URL" "$@"

echo "========================================"
echo "Telos FastMCP test completed"
echo "========================================"