#!/bin/bash
# Manual testing script for A2A Protocol v0.2.1

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "A2A Protocol v0.2.1 Manual Testing"
echo "================================================"
echo ""

# Check if Hermes is running
echo -e "${YELLOW}Checking if Hermes is running on port 8001...${NC}"
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Hermes is running${NC}"
    echo -e "${YELLOW}Note: If you see authorization errors, edit .env.tekton and set:${NC}"
    echo -e "${YELLOW}TEKTON_A2A_ENABLE_SECURITY=false${NC}"
    echo -e "${YELLOW}Then restart Hermes with: ./Hermes/run_hermes.sh${NC}"
else
    echo -e "${RED}✗ Hermes is not running. Please start it with:${NC}"
    echo -e "${RED}./Hermes/run_hermes.sh${NC}"
    echo -e "${RED}(Make sure TEKTON_A2A_ENABLE_SECURITY=false in .env.tekton for testing)${NC}"
    exit 1
fi
echo ""

# Test 1: List agents (should be empty initially)
echo -e "${YELLOW}Test 1: List agents${NC}"
echo "Request:"
echo '{"jsonrpc": "2.0", "method": "agent.list", "id": 1}'
echo ""
echo "Response:"
curl -s -X POST http://localhost:8001/api/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agent.list",
    "id": 1
  }' | python -m json.tool
echo ""

# Test 2: Register an agent
echo -e "${YELLOW}Test 2: Register an agent${NC}"
echo "Request:"
echo '{"jsonrpc": "2.0", "method": "agent.register", "params": {"agent_card": {...}}, "id": 2}'
echo ""
echo "Response:"
AGENT_RESPONSE=$(curl -s -X POST http://localhost:8001/api/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agent.register",
    "params": {
      "agent_card": {
        "name": "Test Agent",
        "description": "Manual test agent",
        "version": "1.0.0",
        "capabilities": ["test", "demo"],
        "supported_methods": ["echo", "ping"]
      }
    },
    "id": 2
  }')
echo "$AGENT_RESPONSE" | python -m json.tool

# Extract agent ID
AGENT_ID=$(echo "$AGENT_RESPONSE" | python -c "import json, sys; print(json.load(sys.stdin).get('result', {}).get('agent_id', ''))")
echo ""

# Test 3: List agents again (should show our agent)
echo -e "${YELLOW}Test 3: List agents (after registration)${NC}"
echo "Response:"
curl -s -X POST http://localhost:8001/api/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agent.list",
    "id": 3
  }' | python -m json.tool
echo ""

# Test 4: Create a task
echo -e "${YELLOW}Test 4: Create a task${NC}"
echo "Request:"
echo '{"jsonrpc": "2.0", "method": "task.create", "params": {...}, "id": 4}'
echo ""
echo "Response:"
TASK_RESPONSE=$(curl -s -X POST http://localhost:8001/api/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "task.create",
    "params": {
      "name": "Test Task",
      "description": "A manual test task",
      "input_data": {"message": "Hello A2A"}
    },
    "id": 4
  }')
echo "$TASK_RESPONSE" | python -m json.tool

# Extract task ID
TASK_ID=$(echo "$TASK_RESPONSE" | python -c "import json, sys; print(json.load(sys.stdin).get('result', {}).get('task_id', ''))")
echo ""

# Test 5: Update task state
echo -e "${YELLOW}Test 5: Update task state to 'running'${NC}"
echo "Response:"
curl -s -X POST http://localhost:8001/api/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"task.update_state\",
    \"params\": {
      \"task_id\": \"$TASK_ID\",
      \"state\": \"running\"
    },
    \"id\": 5
  }" | python -m json.tool
echo ""

# Test 6: Get task status
echo -e "${YELLOW}Test 6: Get task status${NC}"
echo "Response:"
curl -s -X POST http://localhost:8001/api/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"task.get\",
    \"params\": {
      \"task_id\": \"$TASK_ID\"
    },
    \"id\": 6
  }" | python -m json.tool
echo ""

# Test 7: Discovery - find agents with capabilities
echo -e "${YELLOW}Test 7: Discovery - find agents with 'test' capability${NC}"
echo "Response:"
curl -s -X POST http://localhost:8001/api/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "discovery.find_for_capability",
    "params": {
      "capability": "test"
    },
    "id": 7
  }' | python -m json.tool
echo ""

# Test 8: Test error handling
echo -e "${YELLOW}Test 8: Test error handling (invalid method)${NC}"
echo "Response:"
curl -s -X POST http://localhost:8001/api/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "invalid.method",
    "id": 8
  }' | python -m json.tool
echo ""

# Test 9: Batch request
echo -e "${YELLOW}Test 9: Batch request${NC}"
echo "Response:"
curl -s -X POST http://localhost:8001/api/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d '[
    {"jsonrpc": "2.0", "method": "agent.list", "id": 9},
    {"jsonrpc": "2.0", "method": "discovery.capability_map", "id": 10}
  ]' | python -m json.tool
echo ""

# Test 10: Well-known agent card
echo -e "${YELLOW}Test 10: Well-known agent card endpoint${NC}"
echo "Response:"
curl -s http://localhost:8001/.well-known/a2a/agent-card.json | python -m json.tool || echo "Not implemented yet"
echo ""

echo "================================================"
echo -e "${GREEN}Manual testing complete!${NC}"
echo "================================================"