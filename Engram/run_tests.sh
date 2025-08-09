#!/bin/bash
# Run Engram MCP Tools test suite

echo "================================"
echo "Running Engram MCP Tools Tests"
echo "================================"

# Install pytest and pytest-asyncio if not installed
pip install -q pytest pytest-asyncio

# Run the MCP tools tests
echo ""
echo "Testing MCP Tools..."
python -m pytest tests/test_mcp_tools.py -v --tb=short

# Check if other tests should run
if [ "$1" == "--all" ]; then
    echo ""
    echo "Running all Engram tests..."
    python -m pytest tests/ -v --tb=short
fi

echo ""
echo "================================"
echo "Test run complete!"
echo "================================"