#!/bin/bash

# test_mcp_installation.sh - Comprehensive MCP Installation Test Suite
# This script tests the complete MCP integration across all Tekton components

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEKTON_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
COMPREHENSIVE=false
JSON_OUTPUT=false
COMPONENT=""
VERBOSE=false
SKIP_STARTUP=false
REPORT_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --comprehensive)
            COMPREHENSIVE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --component)
            COMPONENT="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --skip-startup)
            SKIP_STARTUP=true
            shift
            ;;
        --report)
            REPORT_FILE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --comprehensive    Run comprehensive tool tests for all components"
            echo "  --json            Output results in JSON format"
            echo "  --component NAME   Test only specific component"
            echo "  --verbose         Show detailed output"
            echo "  --skip-startup    Skip component startup check"
            echo "  --report FILE     Save test report to file"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if a component is running
check_component_running() {
    local component=$1
    local port=$2
    
    if curl -s -f "http://localhost:${port}/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to get all component ports
get_component_ports() {
    cat << EOF
hermes:8001
engram:8000
ergon:8002
rhetor:8003
athena:8005
prometheus:8006
harmonia:8007
telos:8008
synthesis:8009
metis:8011
apollo:8012
budget:8013
sophia:8014
EOF
}

# Function to start components if needed
start_components_if_needed() {
    local components_to_start=""
    
    print_color "$BLUE" "\n🔍 Checking component status..."
    
    while IFS=':' read -r comp port; do
        if [ -n "$COMPONENT" ] && [ "$comp" != "$COMPONENT" ]; then
            continue
        fi
        
        if ! check_component_running "$comp" "$port"; then
            print_color "$YELLOW" "   ⚠️  $comp (port $port) is not running"
            components_to_start="$components_to_start $comp"
        else
            print_color "$GREEN" "   ✅ $comp (port $port) is running"
        fi
    done < <(get_component_ports)
    
    if [ -n "$components_to_start" ] && [ "$SKIP_STARTUP" = false ]; then
        print_color "$YELLOW" "\n⚠️  Some components are not running. Starting them..."
        
        # Start Hermes first if needed
        if [[ $components_to_start == *"hermes"* ]]; then
            print_color "$BLUE" "   Starting Hermes first..."
            cd "$TEKTON_ROOT"
            python scripts/enhanced_tekton_launcher.py --components hermes
            sleep 5
            components_to_start=${components_to_start//hermes/}
        fi
        
        # Start remaining components
        if [ -n "$components_to_start" ]; then
            print_color "$BLUE" "   Starting remaining components..."
            cd "$TEKTON_ROOT"
            python scripts/enhanced_tekton_launcher.py --components $(echo $components_to_start | tr ' ' ',')
            sleep 10
        fi
    fi
}

# Function to run Python test with enhanced features
run_python_test() {
    local test_output_file=$(mktemp)
    local python_args=""
    
    if [ "$COMPREHENSIVE" = true ]; then
        python_args="$python_args --comprehensive"
    fi
    
    if [ "$JSON_OUTPUT" = true ]; then
        python_args="$python_args --json"
    fi
    
    if [ -n "$COMPONENT" ]; then
        python_args="$python_args --component $COMPONENT"
    fi
    
    # Create enhanced Python test script
    cat > "$TEKTON_ROOT/tests/test_mcp_installation_enhanced.py" << 'EOF'
#!/usr/bin/env python3
"""
Enhanced MCP Installation Test for Tekton Components
Tests tool registration and execution through Hermes MCP aggregator
"""

import asyncio
import aiohttp
import sys
import os
import argparse
import json
import time
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

async def check_component_health(name: str, port: int, max_retries: int = 3) -> bool:
    """Check if a component is healthy with retry logic."""
    url = f"http://localhost:{port}/health"
    
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        return True
        except Exception:
            pass
        
        if attempt < max_retries - 1:
            await asyncio.sleep(1)
    
    return False

async def get_hermes_tools() -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    """Get all tools registered with Hermes."""
    url = "http://localhost:8001/api/mcp/v2/tools"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Handle both list and dict responses
                    if isinstance(data, list):
                        tools = data
                    else:
                        tools = data.get("tools", [])
                    
                    # Group tools by component
                    tools_by_component = {}
                    name_to_id_map = {}
                    
                    for tool in tools:
                        tool_id = tool.get("id", "")
                        tool_name = tool.get("name", "")
                        
                        # Map tool name to ID
                        name_to_id_map[tool_name] = tool_id
                        
                        # Extract component name from tool name (not ID)
                        if '.' in tool_name:
                            component = tool_name.split('.')[0]
                            tool_short_name = '.'.join(tool_name.split('.')[1:])
                        else:
                            # Try to get component from metadata
                            metadata = tool.get("metadata", {})
                            component = metadata.get("component", "hermes")
                            tool_short_name = tool_name
                        
                        if component not in tools_by_component:
                            tools_by_component[component] = []
                        tools_by_component[component].append(tool_short_name)
                    
                    return tools_by_component, name_to_id_map
    except Exception as e:
        print(f"Error getting tools from Hermes: {e}")
    
    return {}, {}

async def test_tool_execution(tool_id: str, parameters: Dict[str, Any]) -> bool:
    """Test executing a tool through Hermes."""
    url = f"http://localhost:8001/api/mcp/v2/tools/{tool_id}/execute"
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "parameters": parameters
            }
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                return response.status == 200
    except Exception:
        return False

async def main():
    parser = argparse.ArgumentParser(description='Test MCP installation and integration')
    parser.add_argument('--component', type=str, help='Test only specific component')
    parser.add_argument('--comprehensive', action='store_true', help='Run comprehensive tool tests')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    args = parser.parse_args()
    
    # Track timing
    start_time = time.time()
    
    # Track test results
    test_results = []
    test_details = {
        "timestamp": datetime.now().isoformat(),
        "components": {},
        "summary": {}
    }
    
    # Component configuration
    components_to_test = [
        {"name": "Hermes", "port": 8001},
        {"name": "Engram", "port": 8000},
        {"name": "Ergon", "port": 8002},
        {"name": "Rhetor", "port": 8003},
        {"name": "Athena", "port": 8005},
        {"name": "Prometheus", "port": 8006},
        {"name": "Harmonia", "port": 8007},
        {"name": "Telos", "port": 8008},
        {"name": "Synthesis", "port": 8009},
        {"name": "Metis", "port": 8011},
        {"name": "Apollo", "port": 8012},
        {"name": "Budget", "port": 8013},
        {"name": "Sophia", "port": 8014}
    ]
    
    # Filter by component if specified
    if args.component:
        components_to_test = [c for c in components_to_test if c["name"].lower() == args.component.lower()]
    
    if not args.json:
        print("🔍 Testing MCP Installation - Hermes Tool Registration")
        print("=" * 60)
    
    # Step 1: Check component health
    if not args.json:
        print("\n1️⃣ Checking component health...")
    
    healthy_components = []
    unhealthy_components = []
    
    for comp_info in components_to_test:
        name = comp_info["name"]
        port = comp_info["port"]
        
        is_healthy = await check_component_health(name.lower(), port)
        
        if not args.json:
            status_icon = "✅" if is_healthy else "❌"
            print(f"   {status_icon} {name} (port {port}): {'Healthy' if is_healthy else 'Not responding'}")
        
        comp_detail = {
            "name": name,
            "port": port,
            "healthy": is_healthy
        }
        
        if is_healthy:
            healthy_components.append(comp_info)
            test_results.append(True)
        else:
            unhealthy_components.append(comp_info)
            test_results.append(False)
        
        test_details["components"][name.lower()] = comp_detail
    
    # Wait for tool registration
    if not args.json:
        print("\n⏳ Waiting for tool registration to complete...")
    await asyncio.sleep(3)
    
    # Step 2: Check tools registered with Hermes
    if not args.json:
        print("\n2️⃣ Checking tools registered with Hermes...")
    
    tools_by_component, name_to_id_map = await get_hermes_tools()
    
    # Expected tools for each component
    expected_tools = {
        "hermes": ["GetComponentStatus", "ListComponents", "QueryVectorDatabase", 
                   "StoreVectorData", "PublishMessage", "CreateChannel"],
        "apollo": ["health_check", "component_info", "PlanActions", "ExecuteAction", 
                   "AnalyzeContext", "GenerateResponse", "UpdateContext", "PredictNextAction",
                   "PredictOutcome", "OptimizeContext", "AnalyzeMessage", "ValidateProtocol",
                   "EnforceProtocol", "AllocateBudget"],
        "athena": ["health_check", "component_info", "SearchEntities", "GetEntityById", 
                   "GetEntityRelationships", "FindEntityPaths", "MergeEntities", 
                   "QueryKnowledgeGraph", "NaiveQuery", "LocalQuery", "GlobalQuery", "HybridQuery"],
        "budget": ["health_check", "component_info", "AllocateBudget", "CheckBudget", 
                   "RecordUsage", "GetBudgetStatus", "GetModelRecommendations", 
                   "RouteWithBudgetAwareness", "GetUsageAnalytics"],
        "engram": ["health_check", "component_info", "MemoryStore", "MemoryQuery", 
                   "GetContext", "StructuredMemoryAdd", "StructuredMemoryGet", 
                   "StructuredMemoryUpdate", "StructuredMemoryDelete", 
                   "StructuredMemorySearch", "NexusProcess"],
        "ergon": ["health_check", "component_info", "CreateAgent", "UpdateAgent", 
                  "DeleteAgent", "GetAgent", "ListAgents", "CreateTask", "UpdateTaskStatus",
                  "GetTask", "ListTasks", "AssignTask", "CreateWorkflow", "UpdateWorkflow",
                  "ExecuteWorkflow", "GetWorkflowStatus"],
        "harmonia": ["health_check", "component_info", "CreateWorkflowDefinition", 
                     "UpdateWorkflowDefinition", "DeleteWorkflowDefinition",
                     "GetWorkflowDefinition", "ListWorkflowDefinitions", "ExecuteWorkflow",
                     "CancelWorkflowExecution", "PauseWorkflowExecution", 
                     "ResumeWorkflowExecution", "GetWorkflowExecutionStatus", 
                     "ListWorkflowExecutions", "CreateTemplate", "InstantiateTemplate", 
                     "ListTemplates", "ListComponents", "GetComponentActions", 
                     "ExecuteComponentAction"],
        "metis": ["health_check", "component_info", "decompose_task", 
                  "analyze_task_complexity", "suggest_task_order", "generate_subtasks", 
                  "detect_dependencies"],
        "prometheus": ["health_check", "component_info", "create_project_plan", 
                       "analyze_critical_path", "optimize_timeline", "allocate_resources",
                       "create_milestone", "analyze_performance_trends", 
                       "generate_improvement_recommendations", "prioritize_improvements",
                       "analyze_resource_capacity", "conduct_retrospective"],
        "rhetor": ["health_check", "component_info", "GetAvailableModels", 
                   "GetModelCapabilities", "TestModelConnection", "SetDefaultModel",
                   "GetModelPerformance", "ManageModelRotation", "CreatePromptTemplate",
                   "OptimizePrompt", "GetPromptHistory", "ValidatePromptSyntax",
                   "AnalyzePromptPerformance", "ManagePromptLibrary", "CompressContext",
                   "OptimizeContextWindow", "AnalyzeContextUsage", "TrackContextHistory"],
        "sophia": ["health_check", "component_info", "measure_component_intelligence",
                   "track_intelligence_evolution", "compare_intelligence_profiles",
                   "generate_intelligence_insights", "extract_patterns", 
                   "analyze_ecosystem_trends", "forecast_system_evolution",
                   "design_ml_experiment", "manage_experiment_lifecycle",
                   "analyze_component_performance", "predict_optimization_impact",
                   "validate_optimization_results", "create_research_project",
                   "track_research_progress", "generate_research_recommendations",
                   "synthesize_research_findings"],
        "synthesis": ["health_check", "component_info", "synthesize_component_data",
                      "create_unified_report", "merge_data_streams", "detect_data_conflicts",
                      "optimize_data_flow", "orchestrate_component_integration", 
                      "monitor_integration_health", "validate_integration_completeness", 
                      "design_integration_workflow", "execute_composed_workflow",
                      "optimize_workflow_execution", "analyze_workflow_performance",
                      "compose_multi_component_workflow", "optimize_integration_performance",
                      "resolve_integration_conflicts", "validate_synthesis_quality"],
        "telos": ["health_check", "component_info", "create_project", "get_project",
                  "create_requirement", "get_requirement", "update_requirement",
                  "create_trace", "list_traces", "validate_project", 
                  "analyze_requirements", "create_plan"]
    }
    
    # Check for duplicates
    duplicates_found = {}
    
    for component in [c["name"].lower() for c in healthy_components]:
        if component not in expected_tools:
            continue
        
        expected = expected_tools[component]
        registered = tools_by_component.get(component, [])
        
        # Check for duplicates
        tool_counts = {}
        for tool in registered:
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        duplicates = {tool: count for tool, count in tool_counts.items() if count > 1}
        if duplicates:
            duplicates_found[component] = duplicates
        
        # Store tool info
        if component not in test_details["components"]:
            test_details["components"][component] = {}
        
        test_details["components"][component].update({
            "expected_tools": len(expected),
            "registered_tools": len(registered),
            "missing_tools": list(set(expected) - set(registered)),
            "extra_tools": list(set(registered) - set(expected)),
            "duplicates": duplicates
        })
        
        if not args.json:
            print(f"\n   {component.capitalize()}:")
            print(f"   Expected: {len(expected)} tools")
            print(f"   Registered: {len(registered)} tools")
            
            missing = set(expected) - set(registered)
            if missing:
                print(f"   ❌ Missing tools: {', '.join(missing)}")
            else:
                print(f"   ✅ All expected tools registered")
            
            if duplicates:
                print(f"   ⚠️  Duplicate registrations: {duplicates}")
            
            # Show tools in compact format
            if registered and len(registered) <= 10:
                print(f"   Tools: {', '.join(sorted(registered))}")
            elif registered:
                # Show first 10 tools
                sorted_tools = sorted(registered)
                print(f"   Tools: {', '.join(sorted_tools[:10])}")
                print(f"          ... and {len(sorted_tools) - 10} more")
    
    # Step 3: Test tool execution
    if not args.json:
        print("\n3️⃣ Testing tool execution through Hermes...")
    
    # Test health_check for each healthy component
    for comp in healthy_components:
        comp_name = comp["name"].lower()
        
        # Skip Hermes - it doesn't register its own health_check tool
        if comp_name == "hermes":
            continue
            
        tool_name = f"{comp_name}.health_check"
        tool_id = name_to_id_map.get(tool_name)
        
        if tool_id:
            success = await test_tool_execution(tool_id, {})
            test_results.append(success)
            
            if not args.json:
                status = "✅" if success else "❌"
                print(f"   {status} {tool_name}: {'Success' if success else 'Failed'}")
        else:
            # Tool not found
            test_results.append(False)
            if not args.json:
                print(f"   ❌ {tool_name}: Tool ID not found")
    
    # Test Hermes' own tools
    if args.comprehensive:
        if not args.json:
            print("\n   Testing Hermes system tools:")
        
        hermes_tools_to_test = [
            ("ListComponents", {}),
            ("GetComponentStatus", {"component_id": "hermes-api"}),
            ("QueryVectorDatabase", {"query": "test", "limit": 5}),
            ("StoreVectorData", {"data": "test data", "metadata": {"test": True}}),
            ("PublishMessage", {"channel": "test", "message": {"content": "test"}}),
            ("CreateChannel", {"name": "test-channel"})
        ]
        
        for tool_name, params in hermes_tools_to_test:
            tool_id = name_to_id_map.get(tool_name)
            if tool_id:
                success = await test_tool_execution(tool_id, params)
                test_results.append(success)
                
                if not args.json:
                    status = "✅" if success else "❌"
                    print(f"   {status} hermes.{tool_name}: {'Success' if success else 'Failed'}")
            else:
                test_results.append(False)
                if not args.json:
                    print(f"   ❌ hermes.{tool_name}: Tool ID not found")
    
    # Component-specific tool tests
    specific_tests = {
        "athena": ("SearchEntities", {"query": "test", "limit": 5}),
        "budget": ("GetBudgetStatus", {"context_id": "test-context"}),
        "engram": ("MemoryQuery", {"query": "test", "limit": 5}),
        "harmonia": ("ListWorkflowDefinitions", {"limit": 5}),
        "metis": ("analyze_task_complexity", {"task_description": "test task"}),
        "prometheus": ("create_project_plan", {"project_name": "test"}),
        "rhetor": ("GetAvailableModels", {}),
        "sophia": ("measure_component_intelligence", {"component_name": "test"}),
        "synthesis": ("synthesize_component_data", {"component_ids": ["test1", "test2"]}),
        "telos": ("create_project", {"name": "test_project"})
    }
    
    if args.comprehensive:
        if not args.json:
            print("\n   Testing component-specific tools:")
        
        for component, (tool_name_only, params) in specific_tests.items():
            if component in [c["name"].lower() for c in healthy_components]:
                if component in tools_by_component and tool_name_only in tools_by_component[component]:
                    tool_name = f"{component}.{tool_name_only}"
                    tool_id = name_to_id_map.get(tool_name)
                    if tool_id:
                        success = await test_tool_execution(tool_id, params)
                        test_results.append(success)
                        
                        if not args.json:
                            status = "✅" if success else "❌"
                            print(f"   {status} {tool_name}: {'Success' if success else 'Failed'}")
    
    # Calculate statistics
    total_tools = sum(len(tools) for tools in tools_by_component.values())
    total_fastmcp = sum(len([t for t in tools if t not in ['health_check', 'component_info']]) 
                       for tools in tools_by_component.values())
    
    # Categorize components
    fully_integrated = []
    partially_integrated = []
    basic_only = []
    
    for comp in healthy_components:
        comp_name = comp['name'].lower()
        if comp_name in tools_by_component:
            tools = tools_by_component[comp_name]
            expected = expected_tools.get(comp_name, [])
            
            fastmcp_tools = [t for t in tools if t not in ['health_check', 'component_info']]
            
            if len(fastmcp_tools) > 0:
                if set(expected).issubset(set(tools)):
                    fully_integrated.append((comp['name'], len(fastmcp_tools)))
                else:
                    partially_integrated.append((comp['name'], len(fastmcp_tools)))
            else:
                basic_only.append(comp['name'])
    
    # Store summary
    test_details["summary"] = {
        "total_components": len(components_to_test),
        "healthy_components": len(healthy_components),
        "unhealthy_components": len(unhealthy_components),
        "total_tools": total_tools,
        "fastmcp_tools": total_fastmcp,
        "basic_tools": total_tools - total_fastmcp,
        "tests_passed": sum(test_results),
        "tests_total": len(test_results),
        "fully_integrated": [name for name, _ in fully_integrated],
        "partially_integrated": [name for name, _ in partially_integrated],
        "basic_only": basic_only,
        "duplicates_found": duplicates_found,
        "elapsed_time": time.time() - start_time
    }
    
    # Output results
    if args.json:
        print(json.dumps(test_details, indent=2))
    else:
        # Summary
        print("\n" + "=" * 60)
        success_count = sum(test_results)
        total_count = len(test_results)
        
        print(f"📊 Test Results: {success_count}/{total_count} tests passed")
        
        print(f"\n📊 Tool Registration Summary:")
        print(f"   Total tools registered: {total_tools}")
        print(f"   FastMCP tools: {total_fastmcp}")
        print(f"   Basic tools: {total_tools - total_fastmcp}")
        
        if duplicates_found:
            print("\n⚠️  Components with duplicate registrations:")
            for comp, dups in duplicates_found.items():
                print(f"   - {comp}: {dups}")
        
        if unhealthy_components:
            print(f"\n⚠️  {len(unhealthy_components)} component(s) were skipped (not running):")
            for comp in unhealthy_components:
                print(f"   - {comp['name']} (port {comp['port']})")
        
        if healthy_components:
            print(f"\n✅ {len(healthy_components)} component(s) were tested:")
            
            if fully_integrated:
                print("\n   🌟 Fully Integrated (FastMCP + Hermes):")
                for name, tool_count in fully_integrated:
                    print(f"      - {name}: {tool_count} FastMCP tools")
            
            if partially_integrated:
                print("\n   ⚠️  Partially Integrated:")
                for name, tool_count in partially_integrated:
                    print(f"      - {name}: {tool_count} FastMCP tools (some missing)")
            
            if basic_only:
                print("\n   📋 Basic Integration Only:")
                for name in basic_only:
                    print(f"      - {name}: health_check, component_info only")
        
        elapsed = time.time() - start_time
        print(f"\n⏱️  Total test time: {elapsed:.2f} seconds")
        
        if success_count < total_count:
            print("\n🔍 Diagnosis Tips:")
            print("   - Check component logs for FastMCP registration errors")
            print("   - Verify get_all_tools() function exists and returns tools")
            print("   - Ensure MCP bridge is initialized during startup")
            print("   - Check for import errors in tools.py files")
        
        print("\n📝 Note: Components maintain their FastMCP implementation")
        print("   while also registering tools with Hermes for centralized access.")
        
        # Show Hermes-specific details if comprehensive
        if args.comprehensive:
            print("\n🔧 Hermes Tools Tested:")
            print("   - ListComponents: List all registered components")
            print("   - GetComponentStatus: Get status of specific component")
            print("   - QueryVectorDatabase: Search vector database")
            print("   - StoreVectorData: Store data in vector database")
            print("   - PublishMessage: Publish message to channel")
            print("   - CreateChannel: Create new message channel")

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    # Run the Python test
    cd "$TEKTON_ROOT"
    python tests/test_mcp_installation_enhanced.py $python_args | tee "$test_output_file"
    
    # Check exit code
    local exit_code=${PIPESTATUS[0]}
    
    # Save report if requested
    if [ -n "$REPORT_FILE" ]; then
        cp "$test_output_file" "$REPORT_FILE"
        print_color "$GREEN" "\n📄 Test report saved to: $REPORT_FILE"
    fi
    
    # Cleanup
    rm -f "$test_output_file"
    rm -f "$TEKTON_ROOT/tests/test_mcp_installation_enhanced.py"
    
    return $exit_code
}

# Function to generate HTML report
generate_html_report() {
    local json_file=$(mktemp)
    local html_file="${REPORT_FILE%.txt}.html"
    
    # Run test with JSON output
    cd "$TEKTON_ROOT"
    python tests/test_mcp_installation_enhanced.py --json > "$json_file"
    
    # Generate HTML report
    cat > "$html_file" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Tekton MCP Installation Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 30px; }
        .summary { display: flex; gap: 20px; margin: 20px 0; }
        .stat-card { flex: 1; padding: 20px; background-color: #f8f9fa; border-radius: 8px; text-align: center; }
        .stat-card h3 { margin: 0 0 10px 0; color: #666; font-size: 14px; }
        .stat-card .value { font-size: 32px; font-weight: bold; color: #007bff; }
        .component { margin: 10px 0; padding: 15px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff; }
        .healthy { border-left-color: #28a745; }
        .unhealthy { border-left-color: #dc3545; }
        .partial { border-left-color: #ffc107; }
        .tools { margin-top: 10px; font-size: 14px; color: #666; }
        .missing { color: #dc3545; }
        .duplicate { color: #ffc107; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; color: white; }
        .badge-success { background-color: #28a745; }
        .badge-warning { background-color: #ffc107; color: #333; }
        .badge-danger { background-color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Tekton MCP Installation Test Report</h1>
        <p>Generated: <span id="timestamp"></span></p>
        
        <div class="summary">
            <div class="stat-card">
                <h3>Total Components</h3>
                <div class="value" id="total-components">0</div>
            </div>
            <div class="stat-card">
                <h3>Healthy Components</h3>
                <div class="value" id="healthy-components">0</div>
            </div>
            <div class="stat-card">
                <h3>Total Tools</h3>
                <div class="value" id="total-tools">0</div>
            </div>
            <div class="stat-card">
                <h3>Tests Passed</h3>
                <div class="value" id="tests-passed">0</div>
            </div>
        </div>
        
        <h2>Component Status</h2>
        <div id="component-list"></div>
        
        <h2>Integration Summary</h2>
        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Components</th>
                    <th>Count</th>
                </tr>
            </thead>
            <tbody id="integration-summary"></tbody>
        </table>
        
        <h2>Test Details</h2>
        <div id="test-details"></div>
    </div>
    
    <script>
        // Load test data
        const testData = JSON_DATA_PLACEHOLDER;
        
        // Update summary
        document.getElementById('timestamp').textContent = new Date(testData.timestamp).toLocaleString();
        document.getElementById('total-components').textContent = testData.summary.total_components;
        document.getElementById('healthy-components').textContent = testData.summary.healthy_components;
        document.getElementById('total-tools').textContent = testData.summary.total_tools;
        document.getElementById('tests-passed').textContent = testData.summary.tests_passed + '/' + testData.summary.tests_total;
        
        // Update component list
        const componentList = document.getElementById('component-list');
        for (const [name, details] of Object.entries(testData.components)) {
            const div = document.createElement('div');
            div.className = 'component ' + (details.healthy ? 'healthy' : 'unhealthy');
            
            let html = '<h3>' + name.charAt(0).toUpperCase() + name.slice(1) + ' (Port ' + details.port + ')</h3>';
            
            if (details.healthy) {
                html += '<p>Status: <span class="badge badge-success">Healthy</span></p>';
                if (details.registered_tools !== undefined) {
                    html += '<p>Tools: ' + details.registered_tools + ' registered / ' + details.expected_tools + ' expected</p>';
                    
                    if (details.missing_tools && details.missing_tools.length > 0) {
                        html += '<p class="missing">Missing: ' + details.missing_tools.join(', ') + '</p>';
                    }
                    
                    if (details.duplicates && Object.keys(details.duplicates).length > 0) {
                        html += '<p class="duplicate">Duplicates: ' + JSON.stringify(details.duplicates) + '</p>';
                    }
                }
            } else {
                html += '<p>Status: <span class="badge badge-danger">Not Running</span></p>';
            }
            
            div.innerHTML = html;
            componentList.appendChild(div);
        }
        
        // Update integration summary
        const integrationSummary = document.getElementById('integration-summary');
        const categories = [
            { name: 'Fully Integrated', components: testData.summary.fully_integrated, class: 'badge-success' },
            { name: 'Partially Integrated', components: testData.summary.partially_integrated, class: 'badge-warning' },
            { name: 'Basic Only', components: testData.summary.basic_only, class: 'badge-danger' }
        ];
        
        categories.forEach(cat => {
            if (cat.components.length > 0) {
                const row = document.createElement('tr');
                row.innerHTML = '<td><span class="badge ' + cat.class + '">' + cat.name + '</span></td>' +
                               '<td>' + cat.components.join(', ') + '</td>' +
                               '<td>' + cat.components.length + '</td>';
                integrationSummary.appendChild(row);
            }
        });
    </script>
</body>
</html>
EOF
    
    # Replace placeholder with actual JSON data
    local json_content=$(cat "$json_file")
    sed -i.bak "s/JSON_DATA_PLACEHOLDER/${json_content//\//\\/}/g" "$html_file"
    rm -f "${html_file}.bak"
    
    print_color "$GREEN" "📊 HTML report generated: $html_file"
    
    # Cleanup
    rm -f "$json_file"
}

# Main execution
main() {
    print_color "$BLUE" "🚀 Tekton MCP Installation Test Suite"
    print_color "$BLUE" "====================================="
    
    # Change to Tekton root directory
    cd "$TEKTON_ROOT"
    
    # Check and start components if needed
    if [ "$SKIP_STARTUP" = false ]; then
        start_components_if_needed
    fi
    
    # Run the test
    print_color "$BLUE" "\n🧪 Running MCP installation tests..."
    
    if run_python_test; then
        print_color "$GREEN" "\n✅ MCP installation test completed successfully!"
        exit_code=0
    else
        print_color "$RED" "\n❌ MCP installation test failed!"
        exit_code=1
    fi
    
    # Generate HTML report if requested
    if [ -n "$REPORT_FILE" ] && [ "$JSON_OUTPUT" = false ]; then
        generate_html_report
    fi
    
    return $exit_code
}

# Run main function
main
exit $?