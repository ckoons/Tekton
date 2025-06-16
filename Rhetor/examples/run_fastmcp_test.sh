#!/bin/bash

# run_fastmcp_test.sh - Test script for Rhetor FastMCP implementation

set -e

echo "🚀 Starting Rhetor FastMCP Test"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
RHETOR_PORT=${RHETOR_PORT:-8003}
TEST_TIMEOUT=${TEST_TIMEOUT:-30}

echo "Configuration:"
echo "  - Rhetor Port: $RHETOR_PORT"
echo "  - Test Timeout: ${TEST_TIMEOUT}s"
echo ""

# Check if Rhetor is running
echo "🔍 Checking if Rhetor is running on port $RHETOR_PORT..."
if curl -f -s "http://localhost:$RHETOR_PORT/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Rhetor is running${NC}"
else
    echo -e "${RED}❌ Rhetor is not running on port $RHETOR_PORT${NC}"
    echo ""
    echo "To start Rhetor, run:"
    echo "  cd /path/to/Tekton/Rhetor"
    echo "  ./run_rhetor.sh"
    echo ""
    echo "Or manually:"
    echo "  python -m rhetor.api.app --port $RHETOR_PORT"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "📁 Project paths:"
echo "  - Script dir: $SCRIPT_DIR"
echo "  - Project root: $PROJECT_ROOT"

# Check if test script exists
TEST_SCRIPT="$SCRIPT_DIR/test_fastmcp.py"
if [[ ! -f "$TEST_SCRIPT" ]]; then
    echo -e "${RED}❌ Test script not found: $TEST_SCRIPT${NC}"
    exit 1
fi

echo ""
echo "🧪 Running FastMCP tests..."

# Set Python path to include the project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run the test with timeout
if timeout $TEST_TIMEOUT python3 "$TEST_SCRIPT"; then
    echo ""
    echo -e "${GREEN}🎉 FastMCP tests completed successfully!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ FastMCP tests failed or timed out${NC}"
    exit 1
fi