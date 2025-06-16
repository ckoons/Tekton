#!/bin/bash

# Test script for Synthesis FastMCP integration
# This script tests all MCP endpoints and capabilities

echo "=== Synthesis FastMCP Integration Test ==="
echo "Testing Data Synthesis, Integration Orchestration, and Workflow Composition capabilities"

# Configuration
SYNTHESIS_PORT=${SYNTHESIS_PORT:-8009}
BASE_URL="http://localhost:${SYNTHESIS_PORT}"
MCP_BASE_URL="${BASE_URL}/api/mcp/v2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TEST_COUNT=0
PASS_COUNT=0
FAIL_COUNT=0

# Function to run a test
run_test() {
    local test_name="$1"
    local curl_cmd="$2"
    local expected_pattern="$3"
    
    ((TEST_COUNT++))
    echo -e "\n${BLUE}Test $TEST_COUNT: $test_name${NC}"
    echo "Command: $curl_cmd"
    
    # Run the command and capture output
    output=$(eval "$curl_cmd" 2>/dev/null)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        if echo "$output" | grep -q "$expected_pattern"; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((PASS_COUNT++))
        else
            echo -e "${RED}✗ FAIL - Expected pattern '$expected_pattern' not found${NC}"
            echo "Output: $output"
            ((FAIL_COUNT++))
        fi
    else
        echo -e "${RED}✗ FAIL - Command failed with exit code $exit_code${NC}"
        ((FAIL_COUNT++))
    fi
}

# Function to check if Synthesis is running
check_synthesis_running() {
    echo -e "${YELLOW}Checking if Synthesis is running on port $SYNTHESIS_PORT...${NC}"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ Synthesis is running${NC}"
        return 0
    else
        echo -e "${RED}✗ Synthesis is not responding on port $SYNTHESIS_PORT${NC}"
        echo "Please start Synthesis first using: ./run_synthesis.sh"
        exit 1
    fi
}

# Check if Synthesis is running
check_synthesis_running

echo -e "\n${YELLOW}=== Basic Health and Status Tests ===${NC}"

# Test 1: Health check
run_test "Health check" \
    "curl -s '$BASE_URL/health'" \
    "synthesis"

# Test 2: Root endpoint
run_test "Root endpoint" \
    "curl -s '$BASE_URL/'" \
    "Synthesis"

# Test 3: MCP synthesis status
run_test "MCP synthesis status" \
    "curl -s '$MCP_BASE_URL/synthesis-status'" \
    "synthesis-execution-engine"

echo -e "\n${YELLOW}=== MCP Core Endpoints Tests ===${NC}"

# Test 4: MCP capabilities
run_test "List MCP capabilities" \
    "curl -s '$MCP_BASE_URL/capabilities'" \
    "data_synthesis"

# Test 5: MCP tools
run_test "List MCP tools" \
    "curl -s '$MCP_BASE_URL/tools'" \
    "synthesize_component_data"

# Test 6: MCP server info
run_test "MCP server info" \
    "curl -s '$MCP_BASE_URL/server/info'" \
    "synthesis"

echo -e "\n${YELLOW}=== Data Synthesis Tools Tests ===${NC}"

# Test 7: Synthesize component data
run_test "Synthesize component data" \
    "curl -s -X POST '$MCP_BASE_URL/tools/execute' -H 'Content-Type: application/json' -d '{\"tool_name\": \"synthesize_component_data\", \"arguments\": {\"component_ids\": [\"athena\", \"engram\"], \"synthesis_type\": \"contextual\", \"include_metadata\": true}}'" \
    "synthesis_id"

# Test 8: Create unified report
run_test "Create unified report" \
    "curl -s -X POST '$MCP_BASE_URL/tools/execute' -H 'Content-Type: application/json' -d '{\"tool_name\": \"create_unified_report\", \"arguments\": {\"data_sources\": [\"athena\", \"engram\"], \"report_format\": \"comprehensive\", \"include_visualizations\": true}}'" \
    "report_id"

# Test 9: Merge data streams
run_test "Merge data streams" \
    "curl -s -X POST '$MCP_BASE_URL/tools/execute' -H 'Content-Type: application/json' -d '{\"tool_name\": \"merge_data_streams\", \"arguments\": {\"stream_configs\": [{\"source_component\": \"athena\", \"data_types\": [\"knowledge\"], \"priority\": 1.0}], \"merge_strategy\": \"intelligent_merge\"}}'" \
    "merged_stream_id"

echo -e "\n${YELLOW}=== Integration Orchestration Tools Tests ===${NC}"

# Test 10: Orchestrate component integration
run_test "Orchestrate component integration" \
    "curl -s -X POST '$MCP_BASE_URL/tools/execute' -H 'Content-Type: application/json' -d '{\"tool_name\": \"orchestrate_component_integration\", \"arguments\": {\"primary_component\": \"athena\", \"target_components\": [\"engram\"], \"integration_type\": \"bidirectional\"}}'" \
    "integration_id"

# Test 11: Design integration workflow
run_test "Design integration workflow" \
    "curl -s -X POST '$MCP_BASE_URL/tools/execute' -H 'Content-Type: application/json' -d '{\"tool_name\": \"design_integration_workflow\", \"arguments\": {\"component_ids\": [\"athena\", \"engram\"], \"integration_patterns\": [\"data_sync\"], \"workflow_complexity\": \"moderate\"}}'" \
    "workflow_id"

# Test 12: Monitor integration health
run_test "Monitor integration health" \
    "curl -s -X POST '$MCP_BASE_URL/tools/execute' -H 'Content-Type: application/json' -d '{\"tool_name\": \"monitor_integration_health\", \"arguments\": {\"integration_id\": \"test_integration_123\", \"monitoring_metrics\": [\"connectivity\"], \"monitoring_duration\": 30}}'" \
    "health_status"

echo -e "\n${YELLOW}=== Workflow Composition Tools Tests ===${NC}"

# Test 13: Compose multi-component workflow
run_test "Compose multi-component workflow" \
    "curl -s -X POST '$MCP_BASE_URL/tools/execute' -H 'Content-Type: application/json' -d '{\"tool_name\": \"compose_multi_component_workflow\", \"arguments\": {\"component_definitions\": [{\"component_id\": \"athena\", \"role\": \"knowledge_provider\"}], \"workflow_type\": \"sequential\"}}'" \
    "workflow_id"

# Test 14: Execute composed workflow
run_test "Execute composed workflow" \
    "curl -s -X POST '$MCP_BASE_URL/tools/execute' -H 'Content-Type: application/json' -d '{\"tool_name\": \"execute_composed_workflow\", \"arguments\": {\"workflow_id\": \"test_workflow_123\", \"execution_mode\": \"synchronous\"}}'" \
    "execution_id"

echo -e "\n${YELLOW}=== Synthesis Workflow Tests ===${NC}"

# Test 15: Data unification workflow
run_test "Data unification workflow" \
    "curl -s -X POST '$MCP_BASE_URL/execute-synthesis-workflow' -H 'Content-Type: application/json' -d '{\"workflow_name\": \"data_unification\", \"parameters\": {\"component_ids\": [\"athena\", \"engram\"], \"unification_strategy\": \"merge_with_conflict_resolution\"}}'" \
    "workflow_summary"

# Test 16: Component integration workflow
run_test "Component integration workflow" \
    "curl -s -X POST '$MCP_BASE_URL/execute-synthesis-workflow' -H 'Content-Type: application/json' -d '{\"workflow_name\": \"component_integration\", \"parameters\": {\"primary_component\": \"athena\", \"target_components\": [\"engram\"], \"integration_type\": \"bidirectional\"}}'" \
    "workflow_summary"

echo -e "\n${YELLOW}=== Error Handling Tests ===${NC}"

# Test 17: Invalid tool name
run_test "Invalid tool name error handling" \
    "curl -s -X POST '$MCP_BASE_URL/tools/execute' -H 'Content-Type: application/json' -d '{\"tool_name\": \"nonexistent_tool\", \"arguments\": {}}'" \
    "error"

# Test 18: Invalid workflow name
run_test "Invalid workflow name error handling" \
    "curl -s -X POST '$MCP_BASE_URL/execute-synthesis-workflow' -H 'Content-Type: application/json' -d '{\"workflow_name\": \"nonexistent_workflow\", \"parameters\": {}}'" \
    "Unknown workflow"

echo -e "\n${YELLOW}=== Final Results ===${NC}"
echo "Total Tests: $TEST_COUNT"
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Synthesis FastMCP integration is working correctly.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ $FAIL_COUNT test(s) failed. Please check the output above for details.${NC}"
    exit 1
fi