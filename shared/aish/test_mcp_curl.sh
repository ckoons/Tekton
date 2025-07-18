#!/bin/bash
# Quick curl tests for aish MCP server

# Load TektonEnviron to get correct port
source ~/.env 2>/dev/null
source $TEKTON_ROOT/.env.tekton 2>/dev/null
source $TEKTON_ROOT/.env.local 2>/dev/null

# Get port from environment or use default
MCP_PORT="${AISH_MCP_PORT:-3100}"
BASE_URL="http://localhost:${MCP_PORT}/api/mcp/v2"

echo "Testing aish MCP server on port ${MCP_PORT}"
echo "================================"

# Test 1: Health check
echo -e "\n1. Health Check:"
curl -s "${BASE_URL}/health" | jq .

# Test 2: Capabilities
echo -e "\n2. Capabilities:"
curl -s "${BASE_URL}/capabilities" | jq '.capabilities.tools | keys'

# Test 3: List AIs
echo -e "\n3. List AIs:"
curl -s -X POST "${BASE_URL}/tools/list-ais" \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.ais[].name'

# Test 4: Send message (non-streaming)
echo -e "\n4. Send Message to numa (non-streaming):"
curl -s -X POST "${BASE_URL}/tools/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "ai_name": "numa",
    "message": "Hello from curl test",
    "stream": false
  }' | jq '.response' | head -c 100
echo "..."

# Test 5: Send message (streaming)
echo -e "\n\n5. Send Message to numa (streaming):"
echo "Sending streaming request..."
curl -N -X POST "${BASE_URL}/tools/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "ai_name": "numa",
    "message": "Hello from curl streaming test",
    "stream": true
  }' 2>/dev/null | head -5

# Test 6: Forward list
echo -e "\n\n6. List Forwards:"
curl -s -X POST "${BASE_URL}/tools/forward" \
  -H "Content-Type: application/json" \
  -d '{"action": "list"}' | jq .

# Test 7: Terminal inbox
echo -e "\n7. Terminal Inbox:"
curl -s "${BASE_URL}/tools/terma-inbox" | jq '.new | length'

echo -e "\n================================"
echo "Tests complete!"