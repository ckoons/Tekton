#!/bin/bash

# FastMCP Test Suite for Terma
# Tests all MCP tools and workflows

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TERMA_HOST="localhost"
TERMA_PORT="8765"
BASE_URL="http://${TERMA_HOST}:${TERMA_PORT}"
MCP_BASE_URL="${BASE_URL}/api/mcp/v2"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED_TESTS++))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED_TESTS++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

increment_test() {
    ((TOTAL_TESTS++))
}

# Function to make MCP API calls
call_mcp_tool() {
    local tool_name="$1"
    local arguments="$2"
    local endpoint="${MCP_BASE_URL}/tools/execute"
    
    local payload=$(cat <<EOF
{
    "tool_name": "${tool_name}",
    "arguments": ${arguments}
}
EOF
)
    
    curl -s -X POST "${endpoint}" \
        -H "Content-Type: application/json" \
        -d "${payload}"
}

# Function to test MCP endpoint
test_endpoint() {
    local description="$1"
    local url="$2"
    local method="${3:-GET}"
    local expected_status="${4:-200}"
    
    increment_test
    log_info "Testing: ${description}"
    
    local response
    local status_code
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" "$url")
        status_code="${response: -3}"
        response="${response%???}"
    else
        response=$(curl -s -w "%{http_code}" -X "$method" "$url")
        status_code="${response: -3}"
        response="${response%???}"
    fi
    
    if [ "$status_code" = "$expected_status" ]; then
        log_success "$description"
        return 0
    else
        log_error "$description (Expected: $expected_status, Got: $status_code)"
        return 1
    fi
}

# Function to test MCP tool
test_mcp_tool() {
    local tool_name="$1"
    local arguments="$2"
    local description="$3"
    
    increment_test
    log_info "Testing MCP Tool: ${description}"
    
    local response
    response=$(call_mcp_tool "$tool_name" "$arguments")
    local status=$?
    
    if [ $status -eq 0 ] && echo "$response" | grep -q '"success".*true'; then
        log_success "MCP Tool: $description"
        return 0
    else
        log_error "MCP Tool: $description"
        echo "Response: $response"
        return 1
    fi
}

# Main test execution
main() {
    log_info "Starting Terma FastMCP Test Suite"
    log_info "Testing Terma at ${BASE_URL}"
    
    # Test 1: Basic Health Check
    test_endpoint "Basic health check" "${BASE_URL}/health"
    
    # Test 2: MCP Health Check
    test_endpoint "MCP health check" "${MCP_BASE_URL}/health"
    
    # Test 3: MCP Capabilities
    test_endpoint "MCP capabilities endpoint" "${MCP_BASE_URL}/capabilities"
    
    # Test 4: MCP Tools List
    test_endpoint "MCP tools list" "${MCP_BASE_URL}/tools"
    
    # Test 5: Terminal Status
    test_endpoint "Terminal status endpoint" "${MCP_BASE_URL}/terminal-status"
    
    # Test 6: Terminal Health  
    test_endpoint "Terminal health endpoint" "${MCP_BASE_URL}/terminal-health"
    
    log_info "Testing Terminal Management Tools..."
    
    # Test 7: Create Terminal Session
    test_mcp_tool "create_terminal_session" '{"shell_command": "/bin/bash", "session_name": "test-session"}' "Create terminal session"
    
    # Test 8: Manage Session Lifecycle
    test_mcp_tool "manage_session_lifecycle" '{"session_id": "test-sess-1", "action": "start"}' "Manage session lifecycle"
    
    # Test 9: Execute Terminal Commands
    test_mcp_tool "execute_terminal_commands" '{"session_id": "test-sess-1", "commands": ["ls", "pwd"], "execution_mode": "sequential"}' "Execute terminal commands"
    
    # Test 10: Monitor Session Performance
    test_mcp_tool "monitor_session_performance" '{"session_ids": ["test-sess-1"], "metrics": ["cpu", "memory"], "duration_minutes": 1}' "Monitor session performance"
    
    # Test 11: Configure Terminal Settings
    test_mcp_tool "configure_terminal_settings" '{"session_id": "test-sess-1", "settings": {"terminal": {"rows": 30, "cols": 120}}}' "Configure terminal settings"
    
    # Test 12: Backup Session State
    test_mcp_tool "backup_session_state" '{"session_ids": ["test-sess-1"], "backup_type": "full", "include_history": true}' "Backup session state"
    
    log_info "Testing LLM Integration Tools..."
    
    # Test 13: Provide Command Assistance
    test_mcp_tool "provide_command_assistance" '{"command_query": "How to list files recursively?", "shell_type": "bash", "assistance_level": "detailed"}' "Provide command assistance"
    
    # Test 14: Analyze Terminal Output
    test_mcp_tool "analyze_terminal_output" '{"output_text": "bash: command not found: xyz", "analysis_type": "comprehensive"}' "Analyze terminal output"
    
    # Test 15: Suggest Command Improvements
    test_mcp_tool "suggest_command_improvements" '{"command": "find . -name \"*.txt\"", "optimization_goals": ["performance", "safety"]}' "Suggest command improvements"
    
    # Test 16: Detect Terminal Issues
    test_mcp_tool "detect_terminal_issues" '{"session_id": "test-sess-1", "detection_scope": "comprehensive", "include_predictions": true}' "Detect terminal issues"
    
    # Test 17: Generate Terminal Workflows
    test_mcp_tool "generate_terminal_workflows" '{"workflow_type": "deployment", "parameters": {"target": "production"}, "complexity_level": "intermediate"}' "Generate terminal workflows"
    
    # Test 18: Optimize LLM Interactions
    test_mcp_tool "optimize_llm_interactions" '{"session_id": "test-sess-1", "optimization_goals": ["response_time", "accuracy"]}' "Optimize LLM interactions"
    
    log_info "Testing System Integration Tools..."
    
    # Test 19: Integrate with Tekton Components
    test_mcp_tool "integrate_with_tekton_components" '{"component_names": ["hermes", "hephaestus"], "integration_type": "bidirectional"}' "Integrate with Tekton components"
    
    # Test 20: Synchronize Session Data
    test_mcp_tool "synchronize_session_data" '{"sync_targets": ["hermes", "engram"], "data_types": ["session_state", "command_history"], "sync_mode": "real_time"}' "Synchronize session data"
    
    # Test 21: Manage Terminal Security
    test_mcp_tool "manage_terminal_security" '{"security_policies": {"access_control": {"require_authentication": true}}, "enforcement_level": "standard", "audit_logging": true}' "Manage terminal security"
    
    # Test 22: Track Terminal Metrics
    test_mcp_tool "track_terminal_metrics" '{"metric_categories": ["usage", "performance"], "time_period": "1h", "aggregation_level": "detailed"}' "Track terminal metrics"
    
    log_info "Testing Predefined Workflows..."
    
    # Test 23: Terminal Session Optimization Workflow
    local workflow_payload='{"workflow_name": "terminal_session_optimization", "parameters": {"session_id": "test-sess-1", "optimization_level": "aggressive"}}'
    increment_test
    log_info "Testing Workflow: Terminal session optimization"
    local workflow_response
    workflow_response=$(curl -s -X POST "${MCP_BASE_URL}/execute-terminal-workflow" \
        -H "Content-Type: application/json" \
        -d "$workflow_payload")
    
    if echo "$workflow_response" | grep -q '"success".*true'; then
        log_success "Workflow: Terminal session optimization"
    else
        log_error "Workflow: Terminal session optimization"
    fi
    
    # Test 24: LLM Assisted Troubleshooting Workflow  
    workflow_payload='{"workflow_name": "llm_assisted_troubleshooting", "parameters": {"session_id": "test-sess-1", "issue_type": "performance"}}'
    increment_test
    log_info "Testing Workflow: LLM assisted troubleshooting"
    workflow_response=$(curl -s -X POST "${MCP_BASE_URL}/execute-terminal-workflow" \
        -H "Content-Type: application/json" \
        -d "$workflow_payload")
    
    if echo "$workflow_response" | grep -q '"success".*true'; then
        log_success "Workflow: LLM assisted troubleshooting"
    else
        log_error "Workflow: LLM assisted troubleshooting"
    fi
    
    # Test 25: Multi-Component Integration Workflow
    workflow_payload='{"workflow_name": "multi_component_terminal_integration", "parameters": {"components": ["hermes", "hephaestus", "engram"]}}'
    increment_test
    log_info "Testing Workflow: Multi-component integration"
    workflow_response=$(curl -s -X POST "${MCP_BASE_URL}/execute-terminal-workflow" \
        -H "Content-Type: application/json" \
        -d "$workflow_payload")
    
    if echo "$workflow_response" | grep -q '"success".*true'; then
        log_success "Workflow: Multi-component integration"
    else
        log_error "Workflow: Multi-component integration"
    fi
    
    # Test 26: Terminal Performance Analysis Workflow
    workflow_payload='{"workflow_name": "terminal_performance_analysis", "parameters": {"duration_minutes": 5, "analysis_depth": "comprehensive"}}'
    increment_test
    log_info "Testing Workflow: Terminal performance analysis"
    workflow_response=$(curl -s -X POST "${MCP_BASE_URL}/execute-terminal-workflow" \
        -H "Content-Type: application/json" \
        -d "$workflow_payload")
    
    if echo "$workflow_response" | grep -q '"success".*true'; then
        log_success "Workflow: Terminal performance analysis"
    else
        log_error "Workflow: Terminal performance analysis"
    fi
    
    # Test 27: Bulk Session Action
    local bulk_payload='{"action": "backup", "session_filters": {"status": "active"}, "parameters": {"backup_type": "incremental"}}'
    increment_test
    log_info "Testing: Bulk session action"
    local bulk_response
    bulk_response=$(curl -s -X POST "${MCP_BASE_URL}/terminal-session-bulk-action" \
        -H "Content-Type: application/json" \
        -d "$bulk_payload")
    
    if echo "$bulk_response" | grep -q '"success".*true'; then
        log_success "Bulk session action"
    else
        log_error "Bulk session action"
    fi
    
    # Test Summary
    echo
    log_info "=== Test Summary ==="
    log_info "Total Tests: $TOTAL_TESTS"
    log_success "Passed: $PASSED_TESTS"
    
    if [ $FAILED_TESTS -gt 0 ]; then
        log_error "Failed: $FAILED_TESTS"
        echo
        log_error "Some tests failed. Please check the Terma server and try again."
        exit 1
    else
        echo
        log_success "All tests passed! Terma FastMCP integration is working correctly."
        exit 0
    fi
}

# Check if Terma server is running
check_server() {
    log_info "Checking if Terma server is running..."
    
    if ! curl -s --connect-timeout 5 "${BASE_URL}/health" > /dev/null; then
        log_error "Cannot connect to Terma server at ${BASE_URL}"
        log_info "Please start the Terma server first:"
        log_info "  cd /path/to/Tekton/Terma"
        log_info "  python -m terma.cli.main"
        exit 1
    fi
    
    log_success "Terma server is running"
}

# Script execution
echo "Terma FastMCP Test Suite"
echo "========================"

check_server
main

# End of script