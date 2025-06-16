#!/bin/bash
# Test Claude MCP Installation
#
# This script tests the Claude MCP integration with Hermes

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEKTON_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🔍 Testing Claude MCP Installation${NC}"
echo "============================================"

# Step 1: Check if Hermes is running
echo -e "\n${YELLOW}1. Checking Hermes health...${NC}"
if curl -s -f "http://localhost:8001/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Hermes is running${NC}"
else
    echo -e "${RED}❌ Hermes is not running. Please start it first.${NC}"
    exit 1
fi

# Step 2: Test the stdio bridge directly
echo -e "\n${YELLOW}2. Testing STDIO bridge...${NC}"

# Create a test request
TEST_REQUEST='{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}},"id":1}'

# Send the request to the bridge
RESPONSE=$(echo "$TEST_REQUEST" | python "$TEKTON_ROOT/Hermes/hermes/api/mcp_stdio_bridge.py" 2>/dev/null | head -n1)

if echo "$RESPONSE" | jq -e '.result.protocolVersion' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ STDIO bridge responded correctly${NC}"
    echo "   Protocol version: $(echo "$RESPONSE" | jq -r '.result.protocolVersion')"
    echo "   Server name: $(echo "$RESPONSE" | jq -r '.result.serverInfo.name')"
else
    echo -e "${RED}❌ STDIO bridge did not respond correctly${NC}"
    echo "   Response: $RESPONSE"
    exit 1
fi

# Step 3: Test tool listing
echo -e "\n${YELLOW}3. Testing tool listing...${NC}"

TOOLS_REQUEST='{"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}'
TOOLS_RESPONSE=$(echo -e "$TEST_REQUEST\n$TOOLS_REQUEST" | python "$TEKTON_ROOT/Hermes/hermes/api/mcp_stdio_bridge.py" 2>/dev/null | tail -n1)

if echo "$TOOLS_RESPONSE" | jq -e '.result.tools' > /dev/null 2>&1; then
    TOOL_COUNT=$(echo "$TOOLS_RESPONSE" | jq '.result.tools | length')
    echo -e "${GREEN}✅ Successfully listed $TOOL_COUNT tools${NC}"
    
    # Show first 5 tools
    echo "   Sample tools:"
    echo "$TOOLS_RESPONSE" | jq -r '.result.tools[:5] | .[] | "   - \(.name)"'
else
    echo -e "${RED}❌ Failed to list tools${NC}"
    echo "   Response: $TOOLS_RESPONSE"
fi

# Step 4: Check Claude configuration
echo -e "\n${YELLOW}4. Checking Claude configuration...${NC}"

# Check if claude command exists
if command -v claude &> /dev/null; then
    echo -e "${GREEN}✅ Claude CLI is installed${NC}"
    
    # Check if Tekton MCP is configured
    if claude mcp list 2>/dev/null | grep -q "tekton"; then
        echo -e "${GREEN}✅ Tekton MCP is configured in Claude${NC}"
    else
        echo -e "${YELLOW}⚠️  Tekton MCP is not configured in Claude${NC}"
        echo "   Run: ./scripts/install_tekton_mcps.sh"
    fi
else
    echo -e "${YELLOW}⚠️  Claude CLI is not installed${NC}"
fi

# Step 5: Test a simple tool execution
echo -e "\n${YELLOW}5. Testing tool execution...${NC}"

# Test ListComponents tool
EXECUTE_REQUEST='{"jsonrpc":"2.0","method":"tools/call","params":{"name":"ListComponents","arguments":{}},"id":3}'
EXECUTE_RESPONSE=$(echo -e "$TEST_REQUEST\n$EXECUTE_REQUEST" | python "$TEKTON_ROOT/Hermes/hermes/api/mcp_stdio_bridge.py" 2>/dev/null | tail -n1)

if echo "$EXECUTE_RESPONSE" | jq -e '.result.content[0].text' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Successfully executed ListComponents tool${NC}"
    COMPONENT_COUNT=$(echo "$EXECUTE_RESPONSE" | jq -r '.result.content[0].text' | jq '. | length')
    echo "   Found $COMPONENT_COUNT components"
else
    echo -e "${RED}❌ Failed to execute tool${NC}"
    echo "   Response: $EXECUTE_RESPONSE"
fi

echo -e "\n${BLUE}============================================${NC}"
echo -e "${BLUE}Test Summary:${NC}"
echo -e "${BLUE}============================================${NC}"

# Summary based on test results
if [ -f "$TEKTON_ROOT/Hermes/hermes/api/mcp_stdio_bridge.py" ]; then
    echo -e "${GREEN}✅ STDIO bridge script exists${NC}"
else
    echo -e "${RED}❌ STDIO bridge script not found${NC}"
fi

echo ""
echo "To use Tekton tools in Claude:"
echo "1. Ensure all components are running: ./scripts/enhanced_tekton_launcher.py"
echo "2. Install the MCP if needed: ./scripts/install_tekton_mcps.sh"
echo "3. Restart Claude Desktop"
echo "4. In Claude, you should see Tekton tools available"