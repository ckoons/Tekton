#!/bin/bash

# Test script for Athena FastMCP implementation
# This script runs the comprehensive test suite for Athena FastMCP

# Set the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPONENT_PATH="$(dirname "$SCRIPT_DIR")"

# Set Python path to include the component and tekton-core
export PYTHONPATH="$COMPONENT_PATH:${PYTHONPATH:-}"

# Set Athena configuration
export ATHENA_STORAGE_BACKEND="${ATHENA_STORAGE_BACKEND:-memory}"
export ATHENA_LOG_LEVEL="${ATHENA_LOG_LEVEL:-info}"

echo "========================================"
echo "Athena FastMCP Test Suite"
echo "========================================"
echo "Component Path: $COMPONENT_PATH"
echo "Storage Backend: $ATHENA_STORAGE_BACKEND"
echo "Log Level: $ATHENA_LOG_LEVEL"
echo "Python Path: $PYTHONPATH"
echo "========================================"

# Check if Athena server is running
ATHENA_URL="${ATHENA_URL:-http://localhost:8001}"
echo "Testing Athena server at: $ATHENA_URL"

# Run the test script
cd "$COMPONENT_PATH"
python examples/test_fastmcp.py --url "$ATHENA_URL" "$@"

echo "========================================"
echo "Athena FastMCP test completed"
echo "========================================"