#!/bin/bash

# FastMCP Test Suite for Apollo
# Tests all MCP tools and workflows

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APOLLO_HOST="localhost"
APOLLO_PORT="8012"
BASE_URL="http://${APOLLO_HOST}:${APOLLO_PORT}"
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
    log_info "Starting Apollo FastMCP Test Suite"
    log_info "Testing Apollo at ${BASE_URL}"
    
    # Test 1: Basic Health Check
    test_endpoint "Basic health check" "${BASE_URL}/health"
    
    # Test 2: MCP Health Check
    test_endpoint "MCP health check" "${MCP_BASE_URL}/health"
    
    # Test 3: MCP Capabilities
    test_endpoint "MCP capabilities endpoint" "${MCP_BASE_URL}/capabilities"
    
    # Test 4: MCP Tools List
    test_endpoint "MCP tools list" "${MCP_BASE_URL}/tools"
    
    # Test 5: Apollo Status
    test_endpoint "Apollo status endpoint" "${MCP_BASE_URL}/apollo-status"
    
    log_info "Testing Action Planning Tools..."
    
    # Test 6: Plan Actions
    test_mcp_tool "PlanActions" '{"goal": "optimize system performance", "context": {"current_load": "high", "available_resources": "medium"}, "constraints": ["budget", "time"]}' "Plan action sequence"
    
    # Test 7: Optimize Action Sequence
    test_mcp_tool "OptimizeActionSequence" '{"actions": [{"type": "scale_resources", "priority": 1}, {"type": "load_balance", "priority": 2}], "optimization_criteria": ["efficiency", "cost"]}' "Optimize action sequence"
    
    # Test 8: Evaluate Action Feasibility
    test_mcp_tool "EvaluateActionFeasibility" '{"action": {"type": "deploy_service", "requirements": {"memory": "4GB", "cpu": "2 cores"}}, "current_state": {"available_memory": "8GB", "available_cpu": "4 cores"}}' "Evaluate action feasibility"
    
    # Test 9: Generate Action Alternatives
    test_mcp_tool "GenerateActionAlternatives" '{"primary_action": {"type": "database_migration", "complexity": "high"}, "constraints": {"downtime": "< 5 minutes", "risk": "low"}}' "Generate action alternatives"
    
    log_info "Testing Action Execution Tools..."
    
    # Test 10: Execute Action Sequence
    test_mcp_tool "ExecuteActionSequence" '{"actions": [{"type": "backup_data", "timeout": 300}, {"type": "update_config", "timeout": 60}], "execution_mode": "sequential", "rollback_enabled": true}' "Execute action sequence"
    
    # Test 11: Monitor Action Progress
    test_mcp_tool "MonitorActionProgress" '{"execution_id": "exec-001", "monitoring_interval": 30, "progress_metrics": ["completion_percentage", "resource_usage", "error_count"]}' "Monitor action progress"
    
    # Test 12: Adapt Execution Strategy
    test_mcp_tool "AdaptExecutionStrategy" '{"execution_id": "exec-001", "current_performance": {"throughput": "low", "error_rate": "high"}, "adaptation_goals": ["improve_throughput", "reduce_errors"]}' "Adapt execution strategy"
    
    # Test 13: Handle Execution Errors
    test_mcp_tool "HandleExecutionErrors" '{"execution_id": "exec-001", "error_type": "timeout", "error_context": {"action": "data_processing", "duration": 600}, "recovery_strategy": "retry_with_optimization"}' "Handle execution errors"
    
    log_info "Testing Context Observation Tools..."
    
    # Test 14: Observe Context Changes
    test_mcp_tool "ObserveContextChanges" '{"observation_scope": ["system_performance", "user_behavior"], "monitoring_duration": 300, "change_sensitivity": "medium"}' "Observe context changes"
    
    # Test 15: Analyze Context Patterns
    test_mcp_tool "AnalyzeContextPatterns" '{"context_data": {"time_series": [{"timestamp": "2024-01-01T10:00:00Z", "cpu_usage": 0.75}, {"timestamp": "2024-01-01T10:01:00Z", "cpu_usage": 0.82}]}, "pattern_types": ["trends", "cycles", "anomalies"]}' "Analyze context patterns"
    
    # Test 16: Predict Context Evolution
    test_mcp_tool "PredictContextEvolution" '{"current_context": {"load": "increasing", "resources": "stable"}, "prediction_horizon": "1 hour", "confidence_level": 0.85}' "Predict context evolution"
    
    # Test 17: Extract Context Insights
    test_mcp_tool "ExtractContextInsights" '{"context_history": {"duration": "24 hours", "metrics": ["performance", "usage", "errors"]}, "insight_types": ["trends", "correlations", "recommendations"]}' "Extract context insights"
    
    log_info "Testing Message Handling Tools..."
    
    # Test 18: Process Incoming Messages
    test_mcp_tool "ProcessIncomingMessages" '{"messages": [{"type": "system_alert", "priority": "high", "content": "CPU usage above threshold"}, {"type": "user_request", "priority": "medium", "content": "status update"}], "processing_mode": "real_time"}' "Process incoming messages"
    
    # Test 19: Route Messages Intelligently
    test_mcp_tool "RouteMessagesIntelligently" '{"message": {"type": "error_report", "severity": "critical", "component": "database"}, "routing_criteria": ["severity", "component", "expertise"], "available_handlers": ["db_team", "ops_team", "on_call"]}' "Route messages intelligently"
    
    # Test 20: Analyze Message Patterns
    test_mcp_tool "AnalyzeMessagePatterns" '{"message_history": {"time_range": "24 hours", "message_count": 1500}, "pattern_analysis": ["frequency", "topics", "sentiment", "urgency"]}' "Analyze message patterns"
    
    # Test 21: Optimize Message Flow
    test_mcp_tool "OptimizeMessageFlow" '{"current_flow": {"throughput": "1000 msg/min", "latency": "50ms", "error_rate": "0.1%"}, "optimization_targets": {"throughput": "1500 msg/min", "latency": "30ms"}}' "Optimize message flow"
    
    log_info "Testing Predictive Analysis Tools..."
    
    # Test 22: Predict System Behavior
    test_mcp_tool "PredictSystemBehavior" '{"system_metrics": {"cpu_trend": "increasing", "memory_usage": "stable", "network_load": "variable"}, "prediction_scope": ["performance", "capacity", "failures"], "time_horizon": "4 hours"}' "Predict system behavior"
    
    # Test 23: Forecast Resource Needs
    test_mcp_tool "ForecastResourceNeeds" '{"historical_usage": {"cpu": [0.6, 0.7, 0.8], "memory": [0.4, 0.5, 0.6], "storage": [0.3, 0.4, 0.5]}, "growth_factors": ["user_increase", "feature_expansion"], "forecast_period": "30 days"}' "Forecast resource needs"
    
    # Test 24: Analyze Performance Trends
    test_mcp_tool "AnalyzePerformanceTrends" '{"performance_data": {"response_times": [100, 120, 110, 130], "throughput": [1000, 1100, 1050, 1200], "error_rates": [0.1, 0.2, 0.15, 0.25]}, "trend_analysis": ["direction", "velocity", "patterns"]}' "Analyze performance trends"
    
    # Test 25: Identify Optimization Opportunities
    test_mcp_tool "IdentifyOptimizationOpportunities" '{"system_state": {"bottlenecks": ["database_queries", "network_latency"], "utilization": {"cpu": 0.6, "memory": 0.8, "disk": 0.4}}, "optimization_goals": ["performance", "cost", "reliability"]}' "Identify optimization opportunities"
    
    log_info "Testing Protocol Enforcement Tools..."
    
    # Test 26: Enforce Communication Protocols
    test_mcp_tool "EnforceCommunicationProtocols" '{"protocol_rules": ["authentication_required", "encryption_enabled", "rate_limiting"], "enforcement_level": "strict", "violation_actions": ["log", "block", "alert"]}' "Enforce communication protocols"
    
    # Test 27: Validate System Compliance
    test_mcp_tool "ValidateSystemCompliance" '{"compliance_standards": ["security", "performance", "data_protection"], "validation_scope": "full_system", "compliance_level": "enterprise"}' "Validate system compliance"
    
    # Test 28: Monitor Protocol Adherence
    test_mcp_tool "MonitorProtocolAdherence" '{"protocols": ["API_versioning", "error_handling", "logging"], "monitoring_period": "1 hour", "adherence_thresholds": {"minimum": 0.95, "target": 0.99}}' "Monitor protocol adherence"
    
    # Test 29: Handle Protocol Violations
    test_mcp_tool "HandleProtocolViolations" '{"violation": {"type": "authentication_failure", "severity": "medium", "source": "client_app"}, "handling_policy": "graduated_response", "escalation_rules": ["repeat_violations", "high_severity"]}' "Handle protocol violations"
    
    log_info "Testing Token Budgeting Tools..."
    
    # Test 30: Manage Token Budgets
    test_mcp_tool "ManageTokenBudgets" '{"budgets": [{"component": "llm_service", "token_limit": 10000, "current_usage": 7500}, {"component": "analysis_engine", "token_limit": 5000, "current_usage": 2000}], "budget_period": "daily"}' "Manage token budgets"
    
    # Test 31: Optimize Resource Allocation
    test_mcp_tool "OptimizeResourceAllocation" '{"resources": {"tokens": 50000, "compute": "high", "memory": "16GB"}, "demands": [{"service": "chat", "priority": "high", "tokens": 15000}, {"service": "analysis", "priority": "medium", "tokens": 8000}]}' "Optimize resource allocation"
    
    # Test 32: Track Usage Patterns
    test_mcp_tool "TrackUsagePatterns" '{"tracking_scope": ["token_consumption", "api_calls", "resource_utilization"], "time_period": "7 days", "pattern_detection": ["trends", "peaks", "anomalies"]}' "Track usage patterns"
    
    # Test 33: Predict Budget Needs
    test_mcp_tool "PredictBudgetNeeds" '{"historical_usage": {"daily_tokens": [8000, 9000, 7500, 10000], "growth_rate": "15%"}, "prediction_period": "30 days", "confidence_interval": 0.9}' "Predict budget needs"
    
    log_info "Testing Predefined Workflows..."
    
    # Test 34: Intelligent Action Planning Workflow
    local workflow_payload='{"workflow_name": "intelligent_action_planning", "parameters": {"goal": "system_optimization", "constraints": ["budget", "downtime"], "optimization_level": "aggressive"}}'
    increment_test
    log_info "Testing Workflow: Intelligent action planning"
    local workflow_response
    workflow_response=$(curl -s -X POST "${MCP_BASE_URL}/execute-apollo-workflow" \
        -H "Content-Type: application/json" \
        -d "$workflow_payload")
    
    if echo "$workflow_response" | grep -q '"success".*true'; then
        log_success "Workflow: Intelligent action planning"
    else
        log_error "Workflow: Intelligent action planning"
    fi
    
    # Test 35: Context-Aware Resource Management Workflow
    workflow_payload='{"workflow_name": "context_aware_resource_management", "parameters": {"monitoring_scope": "full_system", "adaptation_mode": "proactive", "optimization_goals": ["performance", "cost"]}}'
    increment_test
    log_info "Testing Workflow: Context-aware resource management"
    workflow_response=$(curl -s -X POST "${MCP_BASE_URL}/execute-apollo-workflow" \
        -H "Content-Type: application/json" \
        -d "$workflow_payload")
    
    if echo "$workflow_response" | grep -q '"success".*true'; then
        log_success "Workflow: Context-aware resource management"
    else
        log_error "Workflow: Context-aware resource management"
    fi
    
    # Test 36: Protocol Enforcement and Compliance Workflow
    workflow_payload='{"workflow_name": "protocol_enforcement_compliance", "parameters": {"enforcement_level": "strict", "compliance_standards": ["security", "performance"], "monitoring_duration": "24h"}}'
    increment_test
    log_info "Testing Workflow: Protocol enforcement and compliance"
    workflow_response=$(curl -s -X POST "${MCP_BASE_URL}/execute-apollo-workflow" \
        -H "Content-Type: application/json" \
        -d "$workflow_payload")
    
    if echo "$workflow_response" | grep -q '"success".*true'; then
        log_success "Workflow: Protocol enforcement and compliance"
    else
        log_error "Workflow: Protocol enforcement and compliance"
    fi
    
    # Test 37: Predictive System Management Workflow
    workflow_payload='{"workflow_name": "predictive_system_management", "parameters": {"prediction_horizon": "48h", "management_scope": "comprehensive", "proactive_actions": true}}'
    increment_test
    log_info "Testing Workflow: Predictive system management"
    workflow_response=$(curl -s -X POST "${MCP_BASE_URL}/execute-apollo-workflow" \
        -H "Content-Type: application/json" \
        -d "$workflow_payload")
    
    if echo "$workflow_response" | grep -q '"success".*true'; then
        log_success "Workflow: Predictive system management"
    else
        log_error "Workflow: Predictive system management"
    fi
    
    # Test Summary
    echo
    log_info "=== Test Summary ==="
    log_info "Total Tests: $TOTAL_TESTS"
    log_success "Passed: $PASSED_TESTS"
    
    if [ $FAILED_TESTS -gt 0 ]; then
        log_error "Failed: $FAILED_TESTS"
        echo
        log_error "Some tests failed. Please check the Apollo server and try again."
        exit 1
    else
        echo
        log_success "All tests passed! Apollo FastMCP integration is working correctly."
        exit 0
    fi
}

# Check if Apollo server is running
check_server() {
    log_info "Checking if Apollo server is running..."
    
    if ! curl -s --connect-timeout 5 "${BASE_URL}/health" > /dev/null; then
        log_error "Cannot connect to Apollo server at ${BASE_URL}"
        log_info "Please start the Apollo server first:"
        log_info "  cd /path/to/Tekton/Apollo"
        log_info "  python -m apollo.cli.main"
        exit 1
    fi
    
    log_success "Apollo server is running"
}

# Script execution
echo "Apollo FastMCP Test Suite"
echo "========================="

check_server
main

# End of script