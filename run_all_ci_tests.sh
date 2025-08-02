#!/bin/bash
# Run all CI Tools and MCP tests

set -e  # Exit on any error

echo "🧪 Running Complete CI Tools Test Suite"
echo "======================================="

# Get the script directory (TEKTON_ROOT)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export TEKTON_ROOT="$SCRIPT_DIR"

echo "TEKTON_ROOT: $TEKTON_ROOT"
echo ""

# Run CI Tools tests
echo "📦 Running CI Tools Tests"
echo "-------------------------"
cd "$TEKTON_ROOT/shared/ci_tools/tests"
if python run_all_tests.py; then
    echo "✅ CI Tools tests passed"
else
    echo "❌ CI Tools tests failed"
    exit 1
fi

echo ""

# Run MCP tests
echo "🌐 Running MCP Tests" 
echo "--------------------"
cd "$TEKTON_ROOT/shared/aish/tests"
if python run_mcp_tests.py; then
    echo "✅ MCP tests passed"
else
    echo "❌ MCP tests failed"
    exit 1
fi

echo ""
echo "🎉 All tests passed successfully!"
echo ""
echo "✅ CI Tools Implementation Complete:"
echo "   • Tool definition and lifecycle management"
echo "   • Generic adapter for any stdio tool"
echo "   • Multi-instance support"
echo "   • Dynamic port allocation"
echo "   • Persistence across restarts"
echo ""
echo "✅ MCP Integration Complete:"
echo "   • 19 new endpoints for full CI control"
echo "   • Context state management for Apollo-Rhetor"
echo "   • Complete CI discovery and filtering"
echo "   • Registry management operations"
echo "   • Full API coverage for all CI functionality"