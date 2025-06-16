#!/bin/bash

# Run FastMCP test for Budget component
# This script tests the Budget component's FastMCP implementation

# Determine script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BUDGET_DIR="$(dirname "$SCRIPT_DIR")"

echo "Budget directory: $BUDGET_DIR"

# Run test script
echo "Running FastMCP tests..."
python "$SCRIPT_DIR/test_fastmcp.py"