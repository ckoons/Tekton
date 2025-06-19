#!/bin/bash
# Test runner for Hephaestus UI DevTools
# Ensures MCP server is running and runs all tests

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MCP_URL="http://localhost:8088"

echo "🔍 Checking MCP server..."
if ! curl -s "${MCP_URL}/health" > /dev/null; then
    echo "❌ MCP server not running on port 8088"
    echo "📌 Please start it with: ./run_mcp.sh"
    exit 1
fi

echo "✅ MCP server is healthy"
echo ""
echo "🧪 Running tests..."

cd "$SCRIPT_DIR"
python3 run_tests.py

exit $?