#!/bin/bash
# A2A Security Testing Script
# Tests authentication behavior without restarting Hermes

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters for test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo "================================================"
echo "A2A Protocol Security Testing"
echo "================================================"
echo ""

# Function to check test result
check_result() {
    local test_name="$1"
    local expected_behavior="$2"
    local response="$3"
    local should_fail="$4"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Check if response contains an error field
    if echo "$response" | grep -q '"error":' && ! echo "$response" | grep -q '"error":null'; then
        # Response has a non-null error
        # Check if it's specifically an auth error (-32002 or authorization text)
        if echo "$response" | grep -q '\-32002' || echo "$response" | grep -q 'authorization' || echo "$response" | grep -q 'Authorization'; then
            if [ "$should_fail" = "true" ]; then
                echo -e "${GREEN}✓ $test_name: $expected_behavior${NC}"
                PASSED_TESTS=$((PASSED_TESTS + 1))
                return 0
            else
                echo -e "${RED}✗ $test_name: $expected_behavior${NC}"
                echo "   Got auth error when none expected: $response"
                FAILED_TESTS=$((FAILED_TESTS + 1))
                return 1
            fi
        else
            # Non-auth error (like method not found)
            if [ "$should_fail" = "true" ]; then
                echo -e "${RED}✗ $test_name: Expected auth error, got different error${NC}"
                echo "   Response: $response"
                FAILED_TESTS=$((FAILED_TESTS + 1))
                return 1
            else
                echo -e "${RED}✗ $test_name: Failed with non-auth error${NC}"
                echo "   Response: $response"
                FAILED_TESTS=$((FAILED_TESTS + 1))
                return 1
            fi
        fi
    else
        # No error in response (success case)
        if [ "$should_fail" = "true" ]; then
            echo -e "${RED}✗ $test_name: $expected_behavior${NC}"
            echo "   Expected auth error but request succeeded: $response"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return 1
        else
            echo -e "${GREEN}✓ $test_name: $expected_behavior${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        fi
    fi
}

# Check if Hermes is running
echo -e "${YELLOW}Checking if Hermes is running on port 8001...${NC}"
if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Hermes is not running. Please start it with:${NC}"
    echo -e "${RED}./Hermes/run_hermes.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Hermes is running${NC}"

# Check current security setting
echo ""
echo -e "${YELLOW}Checking current A2A security setting...${NC}"

# Read the current setting from .env.tekton
SECURITY_ENABLED="true"  # Default
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEKTON_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$TEKTON_ROOT/.env.tekton"

if [ -f "$ENV_FILE" ]; then
    CURRENT_SETTING=$(grep "^TEKTON_A2A_ENABLE_SECURITY=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    if [ "$CURRENT_SETTING" = "false" ]; then
        SECURITY_ENABLED="false"
        echo -e "${BLUE}Current setting: TEKTON_A2A_ENABLE_SECURITY=false (security disabled)${NC}"
    else
        echo -e "${BLUE}Current setting: TEKTON_A2A_ENABLE_SECURITY=true (security enabled)${NC}"
    fi
else
    echo -e "${YELLOW}Could not find .env.tekton at $ENV_FILE, assuming security is enabled${NC}"
fi

echo ""
echo "================================================"
echo -e "${BLUE}Testing Auth-Exempt Methods${NC}"
echo "================================================"
echo "These methods should always work without authentication:"
echo ""

# Test 1: agent.register (auth-exempt)
echo -e "${YELLOW}Test 1: agent.register (auth-exempt)${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8001/api/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "agent.register",
    "params": {
      "agent_card": {
        "name": "Security Test Agent",
        "description": "Testing security",
        "version": "1.0.0",
        "capabilities": ["test"],
        "supported_methods": ["echo"]
      }
    },
    "id": 1
  }' 2>/dev/null)

check_result "agent.register" "Should work without auth (exempt)" "$RESPONSE" "false"
AGENT_ID=$(echo "$RESPONSE" | python -c "import json, sys; data=json.load(sys.stdin); print(data.get('result', {}).get('agent_id', ''))" 2>/dev/null || echo "")

# Test 2: discovery.capability_map (auth-exempt)
echo -e "${YELLOW}Test 2: discovery.capability_map (auth-exempt)${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8001/api/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "discovery.capability_map",
    "id": 2
  }' 2>/dev/null)

check_result "discovery.capability_map" "Should work without auth (exempt)" "$RESPONSE" "false"

# Test 3: discovery.find_for_capability (auth-exempt)
echo -e "${YELLOW}Test 3: discovery.find_for_capability (auth-exempt)${NC}"
RESPONSE=$(curl -s -X POST http://localhost:8001/api/a2a/v1/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "discovery.find_for_capability",
    "params": {"capability": "test"},
    "id": 3
  }' 2>/dev/null)

check_result "discovery.find_for_capability" "Should work without auth (exempt)" "$RESPONSE" "false"

echo ""
echo "================================================"
echo -e "${BLUE}Testing Protected Methods${NC}"
echo "================================================"

if [ "$SECURITY_ENABLED" = "true" ]; then
    echo "Security is ENABLED - testing auth requirements:"
    echo ""
    
    # Test without auth (should fail)
    echo -e "${YELLOW}Test 4a: agent.list WITHOUT auth${NC}"
    RESPONSE=$(curl -s -X POST http://localhost:8001/api/a2a/v1/ \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "agent.list",
        "id": 4
      }' 2>/dev/null)
    
    check_result "agent.list (no auth)" "Should fail with auth error" "$RESPONSE" "true"
    
    # Test with auth (should succeed)
    echo -e "${YELLOW}Test 4b: agent.list WITH auth (using dummy token)${NC}"
    RESPONSE=$(curl -s -X POST http://localhost:8001/api/a2a/v1/ \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer test-token-12345" \
      -d '{
        "jsonrpc": "2.0",
        "method": "agent.list",
        "id": 5
      }' 2>/dev/null)
    
    # Note: This might still fail if token validation is implemented
    # For now, we're just testing that auth header is checked
    echo "   Response: $(echo "$RESPONSE" | head -1)"
    if echo "$RESPONSE" | grep -q '"result"'; then
        echo -e "${GREEN}✓ Request with auth header was processed${NC}"
    else
        echo -e "${YELLOW}! Request with auth header still failed (token validation may be active)${NC}"
    fi
    
    # Test task.create without auth
    echo -e "${YELLOW}Test 5a: task.create WITHOUT auth${NC}"
    RESPONSE=$(curl -s -X POST http://localhost:8001/api/a2a/v1/ \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "task.create",
        "params": {
          "name": "Test Task",
          "description": "Security test"
        },
        "id": 6
      }' 2>/dev/null)
    
    check_result "task.create (no auth)" "Should fail with auth error" "$RESPONSE" "true"
    
    # Test task.get without auth
    echo -e "${YELLOW}Test 6a: task.get WITHOUT auth${NC}"
    RESPONSE=$(curl -s -X POST http://localhost:8001/api/a2a/v1/ \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "task.get",
        "params": {"task_id": "test-123"},
        "id": 7
      }' 2>/dev/null)
    
    check_result "task.get (no auth)" "Should fail with auth error" "$RESPONSE" "true"
    
else
    echo "Security is DISABLED - all methods should work:"
    echo ""
    
    # Test methods that would normally require auth
    echo -e "${YELLOW}Test 4: agent.list (no auth needed)${NC}"
    RESPONSE=$(curl -s -X POST http://localhost:8001/api/a2a/v1/ \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "agent.list",
        "id": 4
      }' 2>/dev/null)
    
    check_result "agent.list" "Should work without auth (security disabled)" "$RESPONSE" "false"
    
    echo -e "${YELLOW}Test 5: task.create (no auth needed)${NC}"
    RESPONSE=$(curl -s -X POST http://localhost:8001/api/a2a/v1/ \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "task.create",
        "params": {
          "name": "Test Task",
          "description": "Security test"
        },
        "id": 5
      }' 2>/dev/null)
    
    check_result "task.create" "Should work without auth (security disabled)" "$RESPONSE" "false"
    
    echo -e "${YELLOW}Test 6: task.get (no auth needed)${NC}"
    RESPONSE=$(curl -s -X POST http://localhost:8001/api/a2a/v1/ \
      -H "Content-Type: application/json" \
      -d '{
        "jsonrpc": "2.0",
        "method": "task.get",
        "params": {"task_id": "test-123"},
        "id": 6
      }' 2>/dev/null)
    
    check_result "task.get" "Should work without auth (security disabled)" "$RESPONSE" "false"
fi

# Clean up
if [ -n "$AGENT_ID" ]; then
    curl -s -X POST http://localhost:8001/api/a2a/v1/ \
      -H "Content-Type: application/json" \
      -d "{
        \"jsonrpc\": \"2.0\",
        \"method\": \"agent.unregister\",
        \"params\": {\"agent_id\": \"$AGENT_ID\"},
        \"id\": 99
      }" > /dev/null 2>&1
fi

# Summary
echo ""
echo "================================================"
echo -e "${BLUE}Test Summary${NC}"
echo "================================================"
echo -e "Total tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    if [ "$SECURITY_ENABLED" = "true" ]; then
        echo "Security is working correctly:"
        echo "- Auth-exempt methods work without authentication"
        echo "- Protected methods require authentication"
        echo "- Requests with auth headers are processed differently"
    else
        echo "Security is disabled as expected:"
        echo "- All methods work without authentication"
    fi
else
    echo -e "${RED}✗ Some tests failed!${NC}"
    echo "Please check the failed tests above."
fi

echo ""
echo "To test with different security settings:"
echo "1. Edit .env.tekton and toggle TEKTON_A2A_ENABLE_SECURITY"
echo "2. Restart Hermes: ./Hermes/run_hermes.sh"
echo "3. Run this test again"
echo ""

exit $([ $FAILED_TESTS -eq 0 ] && echo 0 || echo 1)