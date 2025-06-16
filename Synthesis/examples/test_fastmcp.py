#!/usr/bin/env python3
"""
Test client for Synthesis FastMCP integration.

This client demonstrates how to interact with Synthesis MCP tools
for data synthesis, integration orchestration, and workflow composition.
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, List


class SynthesisTestClient:
    """Test client for Synthesis FastMCP integration."""
    
    def __init__(self, base_url: str = "http://localhost:8011"):
        """Initialize the test client."""
        self.base_url = base_url.rstrip("/")
        self.mcp_url = f"{self.base_url}/api/mcp/v2"
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def check_health(self) -> Dict[str, Any]:
        """Check if Synthesis is healthy."""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get MCP capabilities."""
        response = await self.client.get(f"{self.mcp_url}/capabilities")
        response.raise_for_status()
        return response.json()
    
    async def get_tools(self) -> Dict[str, Any]:
        """Get available MCP tools."""
        response = await self.client.get(f"{self.mcp_url}/tools")
        response.raise_for_status()
        return response.json()
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool."""
        payload = {
            "tool_name": tool_name,
            "arguments": arguments
        }
        response = await self.client.post(
            f"{self.mcp_url}/tools/execute",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def execute_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a synthesis workflow."""
        payload = {
            "workflow_name": workflow_name,
            "parameters": parameters
        }
        response = await self.client.post(
            f"{self.mcp_url}/execute-synthesis-workflow",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def test_data_synthesis_tools(self) -> List[Dict[str, Any]]:
        """Test all data synthesis tools."""
        results = []
        
        # Test synthesize_component_data
        print("Testing synthesize_component_data...")
        result = await self.execute_tool("synthesize_component_data", {
            "component_ids": ["athena", "engram"],
            "synthesis_type": "contextual",
            "include_metadata": True
        })
        results.append({"tool": "synthesize_component_data", "result": result})
        
        # Test create_unified_report
        print("Testing create_unified_report...")
        result = await self.execute_tool("create_unified_report", {
            "data_sources": ["athena", "engram"],
            "report_format": "comprehensive",
            "include_visualizations": True
        })
        results.append({"tool": "create_unified_report", "result": result})
        
        # Test merge_data_streams
        print("Testing merge_data_streams...")
        result = await self.execute_tool("merge_data_streams", {
            "stream_configs": [
                {
                    "source_component": "athena",
                    "data_types": ["knowledge"],
                    "priority": 1.0,
                    "merge_strategy": "intelligent_merge"
                }
            ],
            "merge_strategy": "intelligent_merge"
        })
        results.append({"tool": "merge_data_streams", "result": result})
        
        # Test detect_data_conflicts
        print("Testing detect_data_conflicts...")
        result = await self.execute_tool("detect_data_conflicts", {
            "data_sources": ["athena", "engram"],
            "conflict_types": ["schema_mismatch", "value_conflicts"],
            "resolution_strategy": "automatic"
        })
        results.append({"tool": "detect_data_conflicts", "result": result})
        
        # Test optimize_data_flow
        print("Testing optimize_data_flow...")
        result = await self.execute_tool("optimize_data_flow", {
            "synthesis_id": "test_synthesis_123",
            "optimization_targets": ["throughput", "latency"],
            "flow_constraints": {}
        })
        results.append({"tool": "optimize_data_flow", "result": result})
        
        # Test validate_synthesis_quality
        print("Testing validate_synthesis_quality...")
        result = await self.execute_tool("validate_synthesis_quality", {
            "synthesis_id": "test_synthesis_123",
            "quality_metrics": ["completeness", "consistency"],
            "validation_rules": {"minimum_completeness": 0.8}
        })
        results.append({"tool": "validate_synthesis_quality", "result": result})
        
        return results
    
    async def test_integration_orchestration_tools(self) -> List[Dict[str, Any]]:
        """Test all integration orchestration tools."""
        results = []
        
        # Test orchestrate_component_integration
        print("Testing orchestrate_component_integration...")
        result = await self.execute_tool("orchestrate_component_integration", {
            "primary_component": "athena",
            "target_components": ["engram"],
            "integration_type": "bidirectional",
            "orchestration_strategy": "adaptive"
        })
        results.append({"tool": "orchestrate_component_integration", "result": result})
        
        # Test design_integration_workflow
        print("Testing design_integration_workflow...")
        result = await self.execute_tool("design_integration_workflow", {
            "component_ids": ["athena", "engram"],
            "integration_patterns": ["data_sync", "event_propagation"],
            "workflow_complexity": "moderate"
        })
        results.append({"tool": "design_integration_workflow", "result": result})
        
        # Test monitor_integration_health
        print("Testing monitor_integration_health...")
        result = await self.execute_tool("monitor_integration_health", {
            "integration_id": "test_integration_123",
            "monitoring_metrics": ["connectivity", "performance"],
            "monitoring_duration": 60
        })
        results.append({"tool": "monitor_integration_health", "result": result})
        
        # Test resolve_integration_conflicts
        print("Testing resolve_integration_conflicts...")
        result = await self.execute_tool("resolve_integration_conflicts", {
            "integration_id": "test_integration_123",
            "conflict_types": ["connectivity_issues"],
            "resolution_strategy": "automated_healing"
        })
        results.append({"tool": "resolve_integration_conflicts", "result": result})
        
        # Test optimize_integration_performance
        print("Testing optimize_integration_performance...")
        result = await self.execute_tool("optimize_integration_performance", {
            "integration_id": "test_integration_123",
            "performance_targets": ["latency", "throughput"],
            "optimization_constraints": {"max_latency_ms": 1000}
        })
        results.append({"tool": "optimize_integration_performance", "result": result})
        
        # Test validate_integration_completeness
        print("Testing validate_integration_completeness...")
        result = await self.execute_tool("validate_integration_completeness", {
            "integration_id": "test_integration_123",
            "completeness_criteria": ["data_consistency", "api_coverage"],
            "validation_depth": "comprehensive"
        })
        results.append({"tool": "validate_integration_completeness", "result": result})
        
        return results
    
    async def test_workflow_composition_tools(self) -> List[Dict[str, Any]]:
        """Test all workflow composition tools."""
        results = []
        
        # Test compose_multi_component_workflow
        print("Testing compose_multi_component_workflow...")
        result = await self.execute_tool("compose_multi_component_workflow", {
            "component_definitions": [
                {
                    "component_id": "athena",
                    "role": "knowledge_provider",
                    "dependencies": [],
                    "configuration": {"mode": "query"}
                }
            ],
            "workflow_type": "sequential",
            "optimization_hints": ["performance"]
        })
        results.append({"tool": "compose_multi_component_workflow", "result": result})
        
        # Test execute_composed_workflow
        print("Testing execute_composed_workflow...")
        result = await self.execute_tool("execute_composed_workflow", {
            "workflow_id": "test_workflow_123",
            "execution_mode": "synchronous",
            "timeout_seconds": 300
        })
        results.append({"tool": "execute_composed_workflow", "result": result})
        
        # Test analyze_workflow_performance
        print("Testing analyze_workflow_performance...")
        result = await self.execute_tool("analyze_workflow_performance", {
            "workflow_id": "test_workflow_123",
            "execution_id": "test_execution_456",
            "analysis_metrics": ["execution_time", "resource_usage"]
        })
        results.append({"tool": "analyze_workflow_performance", "result": result})
        
        # Test optimize_workflow_execution
        print("Testing optimize_workflow_execution...")
        result = await self.execute_tool("optimize_workflow_execution", {
            "workflow_id": "test_workflow_123",
            "optimization_strategies": ["performance", "reliability"],
            "performance_baseline": {"execution_time": 120, "success_rate": 0.95}
        })
        results.append({"tool": "optimize_workflow_execution", "result": result})
        
        return results
    
    async def test_synthesis_workflows(self) -> List[Dict[str, Any]]:
        """Test synthesis workflows."""
        results = []
        
        # Test data unification workflow
        print("Testing data_unification workflow...")
        result = await self.execute_workflow("data_unification", {
            "component_ids": ["athena", "engram"],
            "unification_strategy": "merge_with_conflict_resolution",
            "quality_threshold": 0.8
        })
        results.append({"workflow": "data_unification", "result": result})
        
        # Test component integration workflow
        print("Testing component_integration workflow...")
        result = await self.execute_workflow("component_integration", {
            "primary_component": "athena",
            "target_components": ["engram"],
            "integration_type": "bidirectional"
        })
        results.append({"workflow": "component_integration", "result": result})
        
        # Test workflow orchestration workflow
        print("Testing workflow_orchestration workflow...")
        result = await self.execute_workflow("workflow_orchestration", {
            "workflow_components": [
                {
                    "component_id": "athena",
                    "role": "knowledge_provider"
                }
            ],
            "workflow_type": "sequential",
            "optimization_goals": ["performance"]
        })
        results.append({"workflow": "workflow_orchestration", "result": result})
        
        return results
    
    def print_results(self, results: List[Dict[str, Any]], category: str):
        """Print test results in a formatted way."""
        print(f"\n=== {category} Results ===")
        for item in results:
            tool_or_workflow = item.get("tool") or item.get("workflow")
            result = item["result"]
            success = result.get("success", False)
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{status} {tool_or_workflow}")
            if not success and "error" in result:
                print(f"    Error: {result['error']}")


async def main():
    """Main test function."""
    print("=== Synthesis FastMCP Integration Test Client ===")
    print("Testing Data Synthesis, Integration Orchestration, and Workflow Composition")
    
    async with SynthesisTestClient() as client:
        try:
            # Check health
            print("\nChecking Synthesis health...")
            health = await client.check_health()
            print(f"Status: {health.get('status', 'unknown')}")
            
            # Get capabilities
            print("\nGetting MCP capabilities...")
            capabilities = await client.get_capabilities()
            print(f"Found {len(capabilities.get('capabilities', []))} capabilities")
            
            # Get tools
            print("\nGetting MCP tools...")
            tools = await client.get_tools()
            print(f"Found {len(tools.get('tools', []))} tools")
            
            # Test data synthesis tools
            print("\n=== Testing Data Synthesis Tools ===")
            data_synthesis_results = await client.test_data_synthesis_tools()
            client.print_results(data_synthesis_results, "Data Synthesis Tools")
            
            # Test integration orchestration tools
            print("\n=== Testing Integration Orchestration Tools ===")
            integration_results = await client.test_integration_orchestration_tools()
            client.print_results(integration_results, "Integration Orchestration Tools")
            
            # Test workflow composition tools
            print("\n=== Testing Workflow Composition Tools ===")
            workflow_results = await client.test_workflow_composition_tools()
            client.print_results(workflow_results, "Workflow Composition Tools")
            
            # Test synthesis workflows
            print("\n=== Testing Synthesis Workflows ===")
            synthesis_workflow_results = await client.test_synthesis_workflows()
            client.print_results(synthesis_workflow_results, "Synthesis Workflows")
            
            # Summary
            all_results = data_synthesis_results + integration_results + workflow_results + synthesis_workflow_results
            total_tests = len(all_results)
            passed_tests = sum(1 for item in all_results if item["result"].get("success", False))
            
            print(f"\n=== Summary ===")
            print(f"Total tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            
            if passed_tests == total_tests:
                print("🎉 All tests passed!")
            else:
                print("❌ Some tests failed. Check the output above for details.")
            
        except Exception as e:
            print(f"Error during testing: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
