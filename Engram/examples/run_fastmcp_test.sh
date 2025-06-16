#!/bin/bash

# Run FastMCP test for Engram component
# This script tests the Engram component's FastMCP implementation

# Determine script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENGRAM_DIR="$(dirname "$SCRIPT_DIR")"

echo "Engram directory: $ENGRAM_DIR"

# Set environment variables
export ENGRAM_URL=${ENGRAM_URL:-"http://localhost:8001/mcp"}
export PYTHONPATH="${ENGRAM_DIR}:${PYTHONPATH}"

echo "Using Engram MCP URL: $ENGRAM_URL"

# Run test script
echo "Running FastMCP tests..."
python "$SCRIPT_DIR/test_fastmcp.py"