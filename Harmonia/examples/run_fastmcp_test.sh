#!/bin/bash
# Test script for FastMCP implementation in Harmonia

echo "Testing Harmonia FastMCP implementation..."
echo "----------------------------------------"

# Set up Python environment (adjust as needed)
cd $(dirname "$0")/..
PYTHONPATH=$(pwd) python -m examples.test_fastmcp

echo "----------------------------------------"
echo "Test completed."