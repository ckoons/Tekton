#!/bin/bash

# FastMCP Test Suite for Sophia
# Tests all MCP tools and workflows

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SOPHIA_HOST="localhost"
SOPHIA_PORT="8014"
BASE_URL="http://${SOPHIA_HOST}:${SOPHIA_PORT}"
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
    log_info "Starting Sophia FastMCP Test Suite"
    log_info "Testing Sophia at ${BASE_URL}"
    
    # Test 1: Basic Health Check
    test_endpoint "Basic health check" "${BASE_URL}/health"
    
    # Test 2: MCP Health Check
    test_endpoint "MCP health check" "${MCP_BASE_URL}/health"
    
    # Test 3: MCP Capabilities
    test_endpoint "MCP capabilities endpoint" "${MCP_BASE_URL}/capabilities"
    
    # Test 4: MCP Tools List
    test_endpoint "MCP tools list" "${MCP_BASE_URL}/tools"
    
    # Test 5: Sophia Status
    test_endpoint "Sophia status endpoint" "${MCP_BASE_URL}/sophia-status"
    
    log_info "Testing Intelligence Analysis Tools..."
    
    # Test 6: Analyze Component Intelligence
    test_mcp_tool "analyze_component_intelligence" '{"component_id": "athena", "analysis_depth": "comprehensive", "metrics": ["performance", "adaptability", "learning_rate"]}' "Analyze component intelligence"
    
    # Test 7: Measure System Intelligence
    test_mcp_tool "measure_system_intelligence" '{"measurement_scope": "ecosystem", "intelligence_dimensions": ["reasoning", "learning", "adaptation"], "baseline_period": "30 days"}' "Measure system intelligence"
    
    # Test 8: Compare Intelligence Metrics
    test_mcp_tool "compare_intelligence_metrics" '{"components": ["athena", "engram", "apollo"], "comparison_metrics": ["iq_score", "learning_efficiency", "problem_solving"], "time_period": "7 days"}' "Compare intelligence metrics"
    
    # Test 9: Detect Intelligence Patterns
    test_mcp_tool "detect_intelligence_patterns" '{"data_sources": ["component_metrics", "system_logs"], "pattern_types": ["learning_trends", "adaptation_cycles"], "detection_sensitivity": "medium"}' "Detect intelligence patterns"
    
    # Test 10: Generate Intelligence Report
    test_mcp_tool "generate_intelligence_report" '{"report_type": "comprehensive", "target_audience": "technical", "include_recommendations": true, "analysis_period": "30 days"}' "Generate intelligence report"
    
    log_info "Testing Research and Experimentation Tools..."
    
    # Test 11: Design Intelligence Experiment
    test_mcp_tool "design_intelligence_experiment" '{"research_question": "Does increasing context window improve reasoning?", "hypothesis": "Larger context improves performance", "experiment_type": "controlled"}' "Design intelligence experiment"
    
    # Test 12: Execute Research Experiment
    test_mcp_tool "execute_research_experiment" '{"experiment_id": "exp-001", "execution_mode": "automated", "monitoring_level": "detailed", "duration_hours": 24}' "Execute research experiment"
    
    # Test 13: Analyze Experimental Data
    test_mcp_tool "analyze_experimental_data" '{"experiment_id": "exp-001", "analysis_methods": ["statistical", "ml_based"], "significance_level": 0.05}' "Analyze experimental data"
    
    # Test 14: Validate Research Findings
    test_mcp_tool "validate_research_findings" '{"findings": {"improvement": "15%", "confidence": 0.95}, "validation_methods": ["cross_validation", "peer_review"], "reproducibility_tests": true}' "Validate research findings"
    
    # Test 15: Generate Research Insights
    test_mcp_tool "generate_research_insights" '{"research_domain": "machine_intelligence", "insight_types": ["patterns", "correlations", "predictions"], "actionability_focus": true}' "Generate research insights"
    
    log_info "Testing Recommendation and Optimization Tools..."
    
    # Test 16: Generate Intelligence Recommendations
    test_mcp_tool "generate_intelligence_recommendations" '{"target_component": "athena", "improvement_areas": ["reasoning", "memory"], "recommendation_type": "actionable", "priority_level": "high"}' "Generate intelligence recommendations"
    
    # Test 17: Optimize Component Performance
    test_mcp_tool "optimize_component_performance" '{"component_id": "apollo", "optimization_goals": ["intelligence", "efficiency"], "constraints": ["resource_limits", "stability"], "optimization_method": "genetic_algorithm"}' "Optimize component performance"
    
    # Test 18: Suggest System Improvements
    test_mcp_tool "suggest_system_improvements" '{"system_scope": "full_ecosystem", "improvement_dimensions": ["collective_intelligence", "emergent_behavior"], "innovation_level": "moderate"}' "Suggest system improvements"
    
    # Test 19: Evaluate Improvement Impact
    test_mcp_tool "evaluate_improvement_impact" '{"proposed_changes": [{"component": "engram", "change": "memory_expansion"}], "impact_metrics": ["intelligence_gain", "resource_cost"], "evaluation_method": "simulation"}' "Evaluate improvement impact"
    
    log_info "Testing Machine Learning and Pattern Detection Tools..."
    
    # Test 20: Train Intelligence Models
    test_mcp_tool "train_intelligence_models" '{"model_type": "neural_network", "training_data": "component_intelligence_metrics", "training_parameters": {"epochs": 100, "learning_rate": 0.001}, "validation_split": 0.2}' "Train intelligence models"
    
    # Test 21: Detect Cognitive Patterns
    test_mcp_tool "detect_cognitive_patterns" '{"pattern_sources": ["reasoning_traces", "decision_patterns"], "detection_algorithms": ["clustering", "time_series"], "pattern_complexity": "medium"}' "Detect cognitive patterns"
    
    # Test 22: Analyze Learning Behavior
    test_mcp_tool "analyze_learning_behavior" '{"learning_subjects": ["athena", "engram"], "learning_metrics": ["adaptation_speed", "retention_rate"], "behavior_period": "14 days"}' "Analyze learning behavior"
    
    # Test 23: Predict Intelligence Evolution
    test_mcp_tool "predict_intelligence_evolution" '{"prediction_horizon": "90 days", "evolution_factors": ["learning_data", "system_changes"], "prediction_confidence": 0.85}' "Predict intelligence evolution"
    
    log_info "Testing Component Analysis and Metrics Tools..."
    
    # Test 24: Monitor Component Intelligence
    test_mcp_tool "monitor_component_intelligence" '{"monitoring_scope": ["athena", "apollo", "engram"], "monitoring_frequency": "hourly", "alert_thresholds": {"intelligence_drop": 0.1, "anomaly_score": 0.8}}' "Monitor component intelligence"
    
    # Test 25: Benchmark Component Capabilities
    test_mcp_tool "benchmark_component_capabilities" '{"benchmark_suite": "standard_intelligence", "components": ["athena", "engram"], "benchmark_categories": ["reasoning", "memory", "learning"]}' "Benchmark component capabilities"
    
    # Test 26: Track Intelligence Metrics
    test_mcp_tool "track_intelligence_metrics" '{"metrics": ["iq_equivalent", "learning_rate", "adaptation_speed"], "tracking_period": "30 days", "granularity": "daily"}' "Track intelligence metrics"
    
    # Test 27: Generate Component Reports
    test_mcp_tool "generate_component_reports" '{"report_components": ["athena", "apollo"], "report_sections": ["performance", "intelligence", "recommendations"], "format": "detailed"}' "Generate component reports"
    
    log_info "Testing Predefined Workflows..."
    
    # Test 28: Comprehensive Intelligence Analysis Workflow
    local workflow_payload='{"workflow_name": "comprehensive_intelligence_analysis", "parameters": {"analysis_scope": "ecosystem_wide", "depth": "deep", "include_predictions": true}}'
    increment_test
    log_info "Testing Workflow: Comprehensive intelligence analysis"
    local workflow_response
    workflow_response=$(curl -s -X POST "${MCP_BASE_URL}/execute-sophia-workflow" \
        -H "Content-Type: application/json" \
        -d "$workflow_payload")
    
    if echo "$workflow_response" | grep -q '"success".*true'; then
        log_success "Workflow: Comprehensive intelligence analysis"
    else
        log_error "Workflow: Comprehensive intelligence analysis"
    fi
    
    # Test 29: Intelligent Research and Experimentation Workflow
    workflow_payload='{"workflow_name": "intelligent_research_experimentation", "parameters": {"research_domain": "collective_intelligence", "experiment_design": "automated", "validation_required": true}}'
    increment_test
    log_info "Testing Workflow: Intelligent research and experimentation"
    workflow_response=$(curl -s -X POST "${MCP_BASE_URL}/execute-sophia-workflow" \
        -H "Content-Type: application/json" \
        -d "$workflow_payload")
    
    if echo "$workflow_response" | grep -q '"success".*true'; then
        log_success "Workflow: Intelligent research and experimentation"
    else
        log_error "Workflow: Intelligent research and experimentation"
    fi
    
    # Test 30: System Optimization and Enhancement Workflow
    workflow_payload='{"workflow_name": "system_optimization_enhancement", "parameters": {"optimization_scope": "full_system", "enhancement_goals": ["intelligence", "efficiency"], "deployment_mode": "gradual"}}'
    increment_test
    log_info "Testing Workflow: System optimization and enhancement"
    workflow_response=$(curl -s -X POST "${MCP_BASE_URL}/execute-sophia-workflow" \
        -H "Content-Type: application/json" \
        -d "$workflow_payload")
    
    if echo "$workflow_response" | grep -q '"success".*true'; then
        log_success "Workflow: System optimization and enhancement"
    else
        log_error "Workflow: System optimization and enhancement"
    fi
    
    # Test 31: Predictive Intelligence Modeling Workflow
    workflow_payload='{"workflow_name": "predictive_intelligence_modeling", "parameters": {"modeling_horizon": "6 months", "model_complexity": "advanced", "continuous_learning": true}}'
    increment_test
    log_info "Testing Workflow: Predictive intelligence modeling"
    workflow_response=$(curl -s -X POST "${MCP_BASE_URL}/execute-sophia-workflow" \
        -H "Content-Type: application/json" \
        -d "$workflow_payload")
    
    if echo "$workflow_response" | grep -q '"success".*true'; then
        log_success "Workflow: Predictive intelligence modeling"
    else
        log_error "Workflow: Predictive intelligence modeling"
    fi
    
    # Test Summary
    echo
    log_info "=== Test Summary ==="
    log_info "Total Tests: $TOTAL_TESTS"
    log_success "Passed: $PASSED_TESTS"
    
    if [ $FAILED_TESTS -gt 0 ]; then
        log_error "Failed: $FAILED_TESTS"
        echo
        log_error "Some tests failed. Please check the Sophia server and try again."
        exit 1
    else
        echo
        log_success "All tests passed! Sophia FastMCP integration is working correctly."
        exit 0
    fi
}

# Check if Sophia server is running
check_server() {
    log_info "Checking if Sophia server is running..."
    
    if ! curl -s --connect-timeout 5 "${BASE_URL}/health" > /dev/null; then
        log_error "Cannot connect to Sophia server at ${BASE_URL}"
        log_info "Please start the Sophia server first:"
        log_info "  cd /path/to/Tekton/Sophia"
        log_info "  python -m sophia.__main__"
        exit 1
    fi
    
    log_success "Sophia server is running"
}

# Script execution
echo "Sophia FastMCP Test Suite"
echo "========================="

check_server
main

# End of script