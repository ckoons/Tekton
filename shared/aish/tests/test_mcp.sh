#!/bin/bash
# Test script for aish MCP server

echo "=== aish MCP Server Test Suite ==="
echo

# Check if MCP server is running
echo "Checking MCP server status..."
aish status

if [ $? -ne 0 ]; then
    echo "MCP server not running. Please start aish first."
    exit 1
fi

echo
echo "Running MCP tests..."
echo

# Set TEKTON_ROOT if not already set
if [ -z "$TEKTON_ROOT" ]; then
    export TEKTON_ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
    echo "Setting TEKTON_ROOT=$TEKTON_ROOT"
fi

# Run the Python test suite
python3 -m pytest test_mcp_server.py -v

# Also run some quick curl tests
echo
echo "=== Quick curl tests ==="
echo

# Test health
echo "1. Testing health endpoint:"
curl -s http://localhost:8118/api/mcp/v2/health | jq '.'

echo
echo "2. Testing capabilities:"
curl -s http://localhost:8118/api/mcp/v2/capabilities | jq '.capabilities.tools | keys'

echo
echo "3. Testing list-ais:"
curl -s -X POST http://localhost:8118/api/mcp/v2/tools/list-ais \
    -H "Content-Type: application/json" \
    -d '{}' | jq '.ais | length'

echo
echo "=== Test suite complete ==="