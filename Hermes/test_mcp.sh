#!/bin/bash
# Test MCP connectivity for Hermes

echo "Testing Hermes MCP connectivity..."
python3 tests/test_mcp_connectivity.py

exit $?