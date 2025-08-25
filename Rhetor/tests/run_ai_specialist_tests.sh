#!/bin/bash

echo "=================================="
echo "Running CI Specialist Tests"
echo "=================================="

# Ensure we're in the Rhetor directory
cd "$(dirname "$0")/.." || exit 1

# Check if Rhetor is running
if ! curl -s http://localhost:8003/health > /dev/null 2>&1; then
    echo "⚠️  Warning: Rhetor doesn't appear to be running on port 8003"
    echo "   Please start Rhetor first with: ./run_rhetor.sh"
    echo ""
fi

# Run the test script
echo "Starting CI Specialist integration tests..."
python -m tests.test_ai_specialists

echo ""
echo "Test run completed!"