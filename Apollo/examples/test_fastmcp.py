#!/usr/bin/env python3
"""
FastMCP Test Client for Apollo

This script provides comprehensive testing of Apollo's FastMCP integration,
including all action planning, execution, context observation, and protocol management tools.
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestResult:
    """Data class for storing test results."""
    name: str
    success: bool
    duration: float
    error: Optional[str] = None
    response: Optional[Dict[str, Any]] = None


class ApolloMCPTestClient:
    """Async test client for Apollo FastMCP integration."""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.mcp_base_url = f"{self.base_url}/api/mcp/v2"
        self.session: Optional[aiohttp.ClientSession] = None
        self.results: List[TestResult] = []
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, name: str, url: str, method: str = "GET", 
                          json_data: Optional[Dict[str, Any]] = None,
                          expected_status: int = 200) -> TestResult:
        """Test a single endpoint."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    status = response.status
                    data = await response.json() if response.content_type == 'application/json' else await response.text()
            elif method.upper() == "POST":
                async with self.session.post(url, json=json_data) as response:
                    status = response.status
                    data = await response.json() if response.content_type == 'application/json' else await response.text()
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            duration = asyncio.get_event_loop().time() - start_time
            success = status == expected_status
            
            if not success:
                error = f"Expected status {expected_status}, got {status}"
            else:
                error = None
                
            return TestResult(name, success, duration, error, data)
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return TestResult(name, False, duration, str(e))
    
    async def test_mcp_tool(self, tool_name: str, arguments: Dict[str, Any], 
                           description: str) -> TestResult:
        """Test an MCP tool."""
        url = f"{self.mcp_base_url}/tools/execute"
        json_data = {
            "tool_name": tool_name,
            "arguments": arguments
        }
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with self.session.post(url, json=json_data) as response:
                status = response.status
                data = await response.json()
                duration = asyncio.get_event_loop().time() - start_time
                
                # Check if the tool execution was successful
                success = (status == 200 and 
                          isinstance(data, dict) and 
                          data.get("success") is True)
                
                error = None if success else f"Tool execution failed: {data.get('error', 'Unknown error')}"
                
                return TestResult(f"MCP Tool: {description}", success, duration, error, data)
                
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            return TestResult(f"MCP Tool: {description}", False, duration, str(e))
    
    async def test_workflow(self, workflow_name: str, parameters: Dict[str, Any],
                           description: str) -> TestResult:
        """Test a predefined workflow."""
        url = f"{self.mcp_base_url}/execute-apollo-workflow"
        json_data = {
            "workflow_name": workflow_name,
            "parameters": parameters
        }
        
        return await self.test_endpoint(f"Workflow: {description}", url, "POST", json_data)
    
    async def run_all_tests(self) -> List[TestResult]:
        """Run all tests and return results."""
        print("🚀 Starting Apollo FastMCP Test Suite")
        print("=" * 50)
        
        # Basic connectivity tests
        print("\n📡 Testing Basic Connectivity...")
        
        tests = [
            self.test_endpoint("Health check", f"{self.base_url}/health"),
            self.test_endpoint("MCP health", f"{self.mcp_base_url}/health"),
            self.test_endpoint("MCP capabilities", f"{self.mcp_base_url}/capabilities"),
            self.test_endpoint("MCP tools list", f"{self.mcp_base_url}/tools"),
            self.test_endpoint("Apollo status", f"{self.mcp_base_url}/apollo-status"),
        ]
        
        # Execute connectivity tests
        connectivity_results = await asyncio.gather(*tests, return_exceptions=True)
        for result in connectivity_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # Action Planning Tools tests
        print("\n🎯 Testing Action Planning Tools...")
        
        action_planning_tests = [
            self.test_mcp_tool("PlanActions", 
                             {"goal": "optimize system performance", "context": {"current_load": "high", "available_resources": "medium"}, "constraints": ["budget", "time"]},
                             "Plan action sequence"),
            self.test_mcp_tool("OptimizeActionSequence",
                             {"actions": [{"type": "scale_resources", "priority": 1}, {"type": "load_balance", "priority": 2}], "optimization_criteria": ["efficiency", "cost"]},
                             "Optimize action sequence"),
            self.test_mcp_tool("EvaluateActionFeasibility",
                             {"action": {"type": "deploy_service", "requirements": {"memory": "4GB", "cpu": "2 cores"}}, "current_state": {"available_memory": "8GB", "available_cpu": "4 cores"}},
                             "Evaluate action feasibility"),
            self.test_mcp_tool("GenerateActionAlternatives",
                             {"primary_action": {"type": "database_migration", "complexity": "high"}, "constraints": {"downtime": "< 5 minutes", "risk": "low"}},
                             "Generate action alternatives"),
        ]
        
        planning_results = await asyncio.gather(*action_planning_tests, return_exceptions=True)
        for result in planning_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # Action Execution Tools tests
        print("\n⚡ Testing Action Execution Tools...")
        
        action_execution_tests = [
            self.test_mcp_tool("ExecuteActionSequence",
                             {"actions": [{"type": "backup_data", "timeout": 300}, {"type": "update_config", "timeout": 60}], "execution_mode": "sequential", "rollback_enabled": True},
                             "Execute action sequence"),
            self.test_mcp_tool("MonitorActionProgress",
                             {"execution_id": "exec-001", "monitoring_interval": 30, "progress_metrics": ["completion_percentage", "resource_usage", "error_count"]},
                             "Monitor action progress"),
            self.test_mcp_tool("AdaptExecutionStrategy",
                             {"execution_id": "exec-001", "current_performance": {"throughput": "low", "error_rate": "high"}, "adaptation_goals": ["improve_throughput", "reduce_errors"]},
                             "Adapt execution strategy"),
            self.test_mcp_tool("HandleExecutionErrors",
                             {"execution_id": "exec-001", "error_type": "timeout", "error_context": {"action": "data_processing", "duration": 600}, "recovery_strategy": "retry_with_optimization"},
                             "Handle execution errors"),
        ]
        
        execution_results = await asyncio.gather(*action_execution_tests, return_exceptions=True)
        for result in execution_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # Context Observation Tools tests
        print("\n👁️  Testing Context Observation Tools...")
        
        context_observation_tests = [
            self.test_mcp_tool("ObserveContextChanges",
                             {"observation_scope": ["system_performance", "user_behavior"], "monitoring_duration": 300, "change_sensitivity": "medium"},
                             "Observe context changes"),
            self.test_mcp_tool("AnalyzeContextPatterns",
                             {"context_data": {"time_series": [{"timestamp": "2024-01-01T10:00:00Z", "cpu_usage": 0.75}, {"timestamp": "2024-01-01T10:01:00Z", "cpu_usage": 0.82}]}, "pattern_types": ["trends", "cycles", "anomalies"]},
                             "Analyze context patterns"),
            self.test_mcp_tool("PredictContextEvolution",
                             {"current_context": {"load": "increasing", "resources": "stable"}, "prediction_horizon": "1 hour", "confidence_level": 0.85},
                             "Predict context evolution"),
            self.test_mcp_tool("ExtractContextInsights",
                             {"context_history": {"duration": "24 hours", "metrics": ["performance", "usage", "errors"]}, "insight_types": ["trends", "correlations", "recommendations"]},
                             "Extract context insights"),
        ]
        
        context_results = await asyncio.gather(*context_observation_tests, return_exceptions=True)
        for result in context_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # Message Handling Tools tests
        print("\n📨 Testing Message Handling Tools...")
        
        message_handling_tests = [
            self.test_mcp_tool("ProcessIncomingMessages",
                             {"messages": [{"type": "system_alert", "priority": "high", "content": "CPU usage above threshold"}, {"type": "user_request", "priority": "medium", "content": "status update"}], "processing_mode": "real_time"},
                             "Process incoming messages"),
            self.test_mcp_tool("RouteMessagesIntelligently",
                             {"message": {"type": "error_report", "severity": "critical", "component": "database"}, "routing_criteria": ["severity", "component", "expertise"], "available_handlers": ["db_team", "ops_team", "on_call"]},
                             "Route messages intelligently"),
            self.test_mcp_tool("AnalyzeMessagePatterns",
                             {"message_history": {"time_range": "24 hours", "message_count": 1500}, "pattern_analysis": ["frequency", "topics", "sentiment", "urgency"]},
                             "Analyze message patterns"),
            self.test_mcp_tool("OptimizeMessageFlow",
                             {"current_flow": {"throughput": "1000 msg/min", "latency": "50ms", "error_rate": "0.1%"}, "optimization_targets": {"throughput": "1500 msg/min", "latency": "30ms"}},
                             "Optimize message flow"),
        ]
        
        message_results = await asyncio.gather(*message_handling_tests, return_exceptions=True)
        for result in message_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # Predictive Analysis Tools tests
        print("\n🔮 Testing Predictive Analysis Tools...")
        
        predictive_tests = [
            self.test_mcp_tool("PredictSystemBehavior",
                             {"system_metrics": {"cpu_trend": "increasing", "memory_usage": "stable", "network_load": "variable"}, "prediction_scope": ["performance", "capacity", "failures"], "time_horizon": "4 hours"},
                             "Predict system behavior"),
            self.test_mcp_tool("ForecastResourceNeeds",
                             {"historical_usage": {"cpu": [0.6, 0.7, 0.8], "memory": [0.4, 0.5, 0.6], "storage": [0.3, 0.4, 0.5]}, "growth_factors": ["user_increase", "feature_expansion"], "forecast_period": "30 days"},
                             "Forecast resource needs"),
            self.test_mcp_tool("AnalyzePerformanceTrends",
                             {"performance_data": {"response_times": [100, 120, 110, 130], "throughput": [1000, 1100, 1050, 1200], "error_rates": [0.1, 0.2, 0.15, 0.25]}, "trend_analysis": ["direction", "velocity", "patterns"]},
                             "Analyze performance trends"),
            self.test_mcp_tool("IdentifyOptimizationOpportunities",
                             {"system_state": {"bottlenecks": ["database_queries", "network_latency"], "utilization": {"cpu": 0.6, "memory": 0.8, "disk": 0.4}}, "optimization_goals": ["performance", "cost", "reliability"]},
                             "Identify optimization opportunities"),
        ]
        
        predictive_results = await asyncio.gather(*predictive_tests, return_exceptions=True)
        for result in predictive_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # Protocol Enforcement Tools tests
        print("\n🛡️  Testing Protocol Enforcement Tools...")
        
        protocol_tests = [
            self.test_mcp_tool("EnforceCommunicationProtocols",
                             {"protocol_rules": ["authentication_required", "encryption_enabled", "rate_limiting"], "enforcement_level": "strict", "violation_actions": ["log", "block", "alert"]},
                             "Enforce communication protocols"),
            self.test_mcp_tool("ValidateSystemCompliance",
                             {"compliance_standards": ["security", "performance", "data_protection"], "validation_scope": "full_system", "compliance_level": "enterprise"},
                             "Validate system compliance"),
            self.test_mcp_tool("MonitorProtocolAdherence",
                             {"protocols": ["API_versioning", "error_handling", "logging"], "monitoring_period": "1 hour", "adherence_thresholds": {"minimum": 0.95, "target": 0.99}},
                             "Monitor protocol adherence"),
            self.test_mcp_tool("HandleProtocolViolations",
                             {"violation": {"type": "authentication_failure", "severity": "medium", "source": "client_app"}, "handling_policy": "graduated_response", "escalation_rules": ["repeat_violations", "high_severity"]},
                             "Handle protocol violations"),
        ]
        
        protocol_results = await asyncio.gather(*protocol_tests, return_exceptions=True)
        for result in protocol_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # Token Budgeting Tools tests
        print("\n💰 Testing Token Budgeting Tools...")
        
        budget_tests = [
            self.test_mcp_tool("ManageTokenBudgets",
                             {"budgets": [{"component": "llm_service", "token_limit": 10000, "current_usage": 7500}, {"component": "analysis_engine", "token_limit": 5000, "current_usage": 2000}], "budget_period": "daily"},
                             "Manage token budgets"),
            self.test_mcp_tool("OptimizeResourceAllocation",
                             {"resources": {"tokens": 50000, "compute": "high", "memory": "16GB"}, "demands": [{"service": "chat", "priority": "high", "tokens": 15000}, {"service": "analysis", "priority": "medium", "tokens": 8000}]},
                             "Optimize resource allocation"),
            self.test_mcp_tool("TrackUsagePatterns",
                             {"tracking_scope": ["token_consumption", "api_calls", "resource_utilization"], "time_period": "7 days", "pattern_detection": ["trends", "peaks", "anomalies"]},
                             "Track usage patterns"),
            self.test_mcp_tool("PredictBudgetNeeds",
                             {"historical_usage": {"daily_tokens": [8000, 9000, 7500, 10000], "growth_rate": "15%"}, "prediction_period": "30 days", "confidence_interval": 0.9},
                             "Predict budget needs"),
        ]
        
        budget_results = await asyncio.gather(*budget_tests, return_exceptions=True)
        for result in budget_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # Workflow tests
        print("\n🔄 Testing Predefined Workflows...")
        
        workflow_tests = [
            self.test_workflow("intelligent_action_planning",
                             {"goal": "system_optimization", "constraints": ["budget", "downtime"], "optimization_level": "aggressive"},
                             "Intelligent action planning"),
            self.test_workflow("context_aware_resource_management",
                             {"monitoring_scope": "full_system", "adaptation_mode": "proactive", "optimization_goals": ["performance", "cost"]},
                             "Context-aware resource management"),
            self.test_workflow("protocol_enforcement_compliance",
                             {"enforcement_level": "strict", "compliance_standards": ["security", "performance"], "monitoring_duration": "24h"},
                             "Protocol enforcement and compliance"),
            self.test_workflow("predictive_system_management",
                             {"prediction_horizon": "48h", "management_scope": "comprehensive", "proactive_actions": True},
                             "Predictive system management"),
        ]
        
        workflow_results = await asyncio.gather(*workflow_tests, return_exceptions=True)
        for result in workflow_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        return self.results
    
    def _print_result(self, result: TestResult):
        """Print a test result."""
        status_icon = "✅" if result.success else "❌"
        print(f"{status_icon} {result.name} ({result.duration:.3f}s)")
        
        if not result.success and result.error:
            print(f"   Error: {result.error}")
    
    def print_summary(self):
        """Print test summary."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print(f"Success Rate: {(passed/total)*100:.1f}%")
            print("\nFailed Tests:")
            for result in self.results:
                if not result.success:
                    print(f"  ❌ {result.name}: {result.error}")
        else:
            print("🎉 All tests passed!")
        
        avg_duration = sum(r.duration for r in self.results) / total if total > 0 else 0
        print(f"Average Response Time: {avg_duration:.3f}s")
    
    def save_results(self, filename: str = "apollo_test_results.json"):
        """Save test results to JSON file."""
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "component": "apollo",
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r.success),
            "failed": sum(1 for r in self.results if not r.success),
            "results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "duration": r.duration,
                    "error": r.error,
                    "response_keys": list(r.response.keys()) if r.response else None
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n💾 Results saved to {filename}")


async def main():
    """Main test execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Apollo FastMCP Test Client")
    parser.add_argument("--host", default="localhost", help="Apollo server host")
    parser.add_argument("--port", type=int, default=8000, help="Apollo server port")
    parser.add_argument("--save-results", action="store_true", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    try:
        async with ApolloMCPTestClient(args.host, args.port) as client:
            # Check if server is reachable
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://{args.host}:{args.port}/health", timeout=5) as response:
                        if response.status != 200:
                            print(f"❌ Apollo server not responding correctly (status: {response.status})")
                            return 1
            except Exception as e:
                print(f"❌ Cannot connect to Apollo server at {args.host}:{args.port}")
                print(f"   Error: {e}")
                print("\n💡 Make sure Apollo is running:")
                print("   cd /path/to/Tekton/Apollo")
                print("   python -m apollo.cli.main")
                return 1
            
            print(f"🔗 Connected to Apollo server at {args.host}:{args.port}")
            
            # Run all tests
            await client.run_all_tests()
            
            # Print summary
            client.print_summary()
            
            # Save results if requested
            if args.save_results:
                client.save_results()
            
            # Return exit code based on test results
            failed_count = sum(1 for r in client.results if not r.success)
            return 1 if failed_count > 0 else 0
            
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)