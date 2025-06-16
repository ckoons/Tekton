#!/usr/bin/env python3
"""
FastMCP Test Client for Terma

This script provides comprehensive testing of Terma's FastMCP integration,
including all tools, workflows, and capabilities.
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


class TermaMCPTestClient:
    """Async test client for Terma FastMCP integration."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
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
        url = f"{self.mcp_base_url}/execute-terminal-workflow"
        json_data = {
            "workflow_name": workflow_name,
            "parameters": parameters
        }
        
        return await self.test_endpoint(f"Workflow: {description}", url, "POST", json_data)
    
    async def run_all_tests(self) -> List[TestResult]:
        """Run all tests and return results."""
        print("🚀 Starting Terma FastMCP Test Suite")
        print("=" * 50)
        
        # Basic connectivity tests
        print("\n📡 Testing Basic Connectivity...")
        
        tests = [
            self.test_endpoint("Health check", f"{self.base_url}/health"),
            self.test_endpoint("MCP health", f"{self.mcp_base_url}/health"),
            self.test_endpoint("MCP capabilities", f"{self.mcp_base_url}/capabilities"),
            self.test_endpoint("MCP tools list", f"{self.mcp_base_url}/tools"),
            self.test_endpoint("Terminal status", f"{self.mcp_base_url}/terminal-status"),
            self.test_endpoint("Terminal health", f"{self.mcp_base_url}/terminal-health"),
        ]
        
        # Execute connectivity tests
        connectivity_results = await asyncio.gather(*tests, return_exceptions=True)
        for result in connectivity_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # Terminal Management Tools tests
        print("\n🖥️  Testing Terminal Management Tools...")
        
        terminal_management_tests = [
            self.test_mcp_tool("create_terminal_session", 
                             {"shell_command": "/bin/bash", "session_name": "test-session"},
                             "Create terminal session"),
            self.test_mcp_tool("manage_session_lifecycle",
                             {"session_id": "test-sess-1", "action": "start"},
                             "Manage session lifecycle"),
            self.test_mcp_tool("execute_terminal_commands",
                             {"session_id": "test-sess-1", "commands": ["ls", "pwd"], "execution_mode": "sequential"},
                             "Execute terminal commands"),
            self.test_mcp_tool("monitor_session_performance",
                             {"session_ids": ["test-sess-1"], "metrics": ["cpu", "memory"], "duration_minutes": 1},
                             "Monitor session performance"),
            self.test_mcp_tool("configure_terminal_settings",
                             {"session_id": "test-sess-1", "settings": {"terminal": {"rows": 30, "cols": 120}}},
                             "Configure terminal settings"),
            self.test_mcp_tool("backup_session_state",
                             {"session_ids": ["test-sess-1"], "backup_type": "full", "include_history": True},
                             "Backup session state"),
        ]
        
        terminal_results = await asyncio.gather(*terminal_management_tests, return_exceptions=True)
        for result in terminal_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # LLM Integration Tools tests
        print("\n🤖 Testing LLM Integration Tools...")
        
        llm_integration_tests = [
            self.test_mcp_tool("provide_command_assistance",
                             {"command_query": "How to list files recursively?", "shell_type": "bash", "assistance_level": "detailed"},
                             "Provide command assistance"),
            self.test_mcp_tool("analyze_terminal_output",
                             {"output_text": "bash: command not found: xyz", "analysis_type": "comprehensive"},
                             "Analyze terminal output"),
            self.test_mcp_tool("suggest_command_improvements",
                             {"command": "find . -name \"*.txt\"", "optimization_goals": ["performance", "safety"]},
                             "Suggest command improvements"),
            self.test_mcp_tool("detect_terminal_issues",
                             {"session_id": "test-sess-1", "detection_scope": "comprehensive", "include_predictions": True},
                             "Detect terminal issues"),
            self.test_mcp_tool("generate_terminal_workflows",
                             {"workflow_type": "deployment", "parameters": {"target": "production"}, "complexity_level": "intermediate"},
                             "Generate terminal workflows"),
            self.test_mcp_tool("optimize_llm_interactions",
                             {"session_id": "test-sess-1", "optimization_goals": ["response_time", "accuracy"]},
                             "Optimize LLM interactions"),
        ]
        
        llm_results = await asyncio.gather(*llm_integration_tests, return_exceptions=True)
        for result in llm_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # System Integration Tools tests
        print("\n🔧 Testing System Integration Tools...")
        
        system_integration_tests = [
            self.test_mcp_tool("integrate_with_tekton_components",
                             {"component_names": ["hermes", "hephaestus"], "integration_type": "bidirectional"},
                             "Integrate with Tekton components"),
            self.test_mcp_tool("synchronize_session_data",
                             {"sync_targets": ["hermes", "engram"], "data_types": ["session_state", "command_history"], "sync_mode": "real_time"},
                             "Synchronize session data"),
            self.test_mcp_tool("manage_terminal_security",
                             {"security_policies": {"access_control": {"require_authentication": True}}, "enforcement_level": "standard", "audit_logging": True},
                             "Manage terminal security"),
            self.test_mcp_tool("track_terminal_metrics",
                             {"metric_categories": ["usage", "performance"], "time_period": "1h", "aggregation_level": "detailed"},
                             "Track terminal metrics"),
        ]
        
        system_results = await asyncio.gather(*system_integration_tests, return_exceptions=True)
        for result in system_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # Workflow tests
        print("\n⚡ Testing Predefined Workflows...")
        
        workflow_tests = [
            self.test_workflow("terminal_session_optimization",
                             {"session_id": "test-sess-1", "optimization_level": "aggressive"},
                             "Terminal session optimization"),
            self.test_workflow("llm_assisted_troubleshooting",
                             {"session_id": "test-sess-1", "issue_type": "performance"},
                             "LLM assisted troubleshooting"),
            self.test_workflow("multi_component_terminal_integration",
                             {"components": ["hermes", "hephaestus", "engram"]},
                             "Multi-component integration"),
            self.test_workflow("terminal_performance_analysis",
                             {"duration_minutes": 5, "analysis_depth": "comprehensive"},
                             "Terminal performance analysis"),
        ]
        
        workflow_results = await asyncio.gather(*workflow_tests, return_exceptions=True)
        for result in workflow_results:
            if isinstance(result, TestResult):
                self.results.append(result)
                self._print_result(result)
        
        # Additional endpoint tests
        print("\n🔍 Testing Additional Endpoints...")
        
        additional_tests = [
            self.test_endpoint("Bulk session action", 
                             f"{self.mcp_base_url}/terminal-session-bulk-action",
                             "POST",
                             {"action": "backup", "session_filters": {"status": "active"}, "parameters": {"backup_type": "incremental"}}),
        ]
        
        additional_results = await asyncio.gather(*additional_tests, return_exceptions=True)
        for result in additional_results:
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
    
    def save_results(self, filename: str = "test_results.json"):
        """Save test results to JSON file."""
        results_data = {
            "timestamp": datetime.now().isoformat(),
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
    
    parser = argparse.ArgumentParser(description="Terma FastMCP Test Client")
    parser.add_argument("--host", default="localhost", help="Terma server host")
    parser.add_argument("--port", type=int, default=8765, help="Terma server port")
    parser.add_argument("--save-results", action="store_true", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    try:
        async with TermaMCPTestClient(args.host, args.port) as client:
            # Check if server is reachable
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://{args.host}:{args.port}/health", timeout=5) as response:
                        if response.status != 200:
                            print(f"❌ Terma server not responding correctly (status: {response.status})")
                            return 1
            except Exception as e:
                print(f"❌ Cannot connect to Terma server at {args.host}:{args.port}")
                print(f"   Error: {e}")
                print("\n💡 Make sure Terma is running:")
                print("   cd /path/to/Tekton/Terma")
                print("   python -m terma.cli.main")
                return 1
            
            print(f"🔗 Connected to Terma server at {args.host}:{args.port}")
            
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