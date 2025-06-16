#!/usr/bin/env python3
"""
Test script for Metis FastMCP implementation.

This script tests the FastMCP integration with Metis task management
to ensure all tools work correctly.
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any, List


# Configuration
import os
METIS_PORT = os.environ.get("METIS_PORT")
METIS_BASE_URL = f"http://localhost:{METIS_PORT}"
MCP_BASE_URL = f"{METIS_BASE_URL}/api/mcp/v2"


class MetisMCPTester:
    """Test class for Metis MCP functionality."""
    
    def __init__(self):
        """Initialize the tester."""
        self.session = None
        self.created_task_ids = []
        self.created_dependency_ids = []
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request and return JSON response."""
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.content_type == 'application/json':
                    return await response.json()
                else:
                    text = await response.text()
                    return {
                        "success": False,
                        "error": f"Non-JSON response: {text}",
                        "status_code": response.status
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_health_check(self) -> bool:
        """Test basic health check."""
        print("Testing health check...")
        
        response = await self.make_request("GET", f"{METIS_BASE_URL}/health")
        
        if response.get("status") == "healthy":
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response}")
            return False
    
    async def test_mcp_status(self) -> bool:
        """Test MCP status endpoint."""
        print("Testing MCP status...")
        
        response = await self.make_request("GET", f"{MCP_BASE_URL}/health")
        
        if response.get("success"):
            print("✅ MCP health check passed")
            print(f"   Available capabilities: {response.get('capabilities', [])}")
            print(f"   Available tools: {response.get('tools', [])}")
            return True
        else:
            print(f"❌ MCP health check failed: {response}")
            return False
    
    async def test_mcp_capabilities(self) -> bool:
        """Test MCP capabilities endpoint."""
        print("Testing MCP capabilities...")
        
        response = await self.make_request("GET", f"{MCP_BASE_URL}/capabilities")
        
        if response.get("success"):
            capabilities = response.get("capabilities", [])
            expected_capabilities = [
                "task_management",
                "dependency_management", 
                "task_analytics",
                "telos_integration"
            ]
            
            for cap in expected_capabilities:
                if cap in [c["name"] for c in capabilities]:
                    print(f"✅ Capability '{cap}' found")
                else:
                    print(f"❌ Capability '{cap}' missing")
                    return False
            
            return True
        else:
            print(f"❌ MCP capabilities test failed: {response}")
            return False
    
    async def test_create_task(self) -> bool:
        """Test task creation via MCP."""
        print("Testing task creation...")
        
        task_data = {
            "tool_name": "create_task",
            "arguments": {
                "title": "Test Task via MCP",
                "description": "This is a test task created through the MCP interface",
                "priority": "high",
                "status": "pending",
                "tags": ["test", "mcp"],
                "details": "Implementation details for the test task",
                "test_strategy": "Unit tests and integration tests"
            }
        }
        
        response = await self.make_request(
            "POST", 
            f"{MCP_BASE_URL}/process",
            json=task_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            task = response["result"]["task"]
            self.created_task_ids.append(task["id"])
            print(f"✅ Task created successfully: {task['id']}")
            print(f"   Title: {task['title']}")
            print(f"   Priority: {task['priority']}")
            return True
        else:
            print(f"❌ Task creation failed: {response}")
            return False
    
    async def test_get_task(self) -> bool:
        """Test task retrieval via MCP."""
        print("Testing task retrieval...")
        
        if not self.created_task_ids:
            print("❌ No tasks available for retrieval test")
            return False
        
        task_id = self.created_task_ids[0]
        
        request_data = {
            "tool_name": "get_task",
            "arguments": {
                "task_id": task_id
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process", 
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            task = response["result"]["task"]
            print(f"✅ Task retrieved successfully: {task['id']}")
            print(f"   Title: {task['title']}")
            return True
        else:
            print(f"❌ Task retrieval failed: {response}")
            return False
    
    async def test_list_tasks(self) -> bool:
        """Test task listing via MCP."""
        print("Testing task listing...")
        
        request_data = {
            "tool_name": "list_tasks",
            "arguments": {
                "limit": 10,
                "offset": 0
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            tasks = response["result"]["tasks"]
            print(f"✅ Task listing successful: {len(tasks)} tasks found")
            return True
        else:
            print(f"❌ Task listing failed: {response}")
            return False
    
    async def test_add_subtask(self) -> bool:
        """Test subtask addition via MCP."""
        print("Testing subtask addition...")
        
        if not self.created_task_ids:
            print("❌ No tasks available for subtask test")
            return False
        
        task_id = self.created_task_ids[0]
        
        request_data = {
            "tool_name": "add_subtask",
            "arguments": {
                "task_id": task_id,
                "title": "Test Subtask",
                "description": "This is a test subtask added via MCP",
                "completed": False
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            print(f"✅ Subtask added successfully to task {task_id}")
            return True
        else:
            print(f"❌ Subtask addition failed: {response}")
            return False
    
    async def test_create_dependency(self) -> bool:
        """Test dependency creation via MCP."""
        print("Testing dependency creation...")
        
        if len(self.created_task_ids) < 2:
            # Create another task for dependency testing
            await self.test_create_task()
        
        if len(self.created_task_ids) < 2:
            print("❌ Need at least 2 tasks for dependency test")
            return False
        
        request_data = {
            "tool_name": "create_dependency",
            "arguments": {
                "source_task_id": self.created_task_ids[0],
                "target_task_id": self.created_task_ids[1],
                "dependency_type": "depends_on",
                "description": "Test dependency via MCP"
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            dependency = response["result"]["dependency"]
            self.created_dependency_ids.append(dependency["id"])
            print(f"✅ Dependency created successfully: {dependency['id']}")
            return True
        else:
            print(f"❌ Dependency creation failed: {response}")
            return False
    
    async def test_task_complexity_analysis(self) -> bool:
        """Test task complexity analysis via MCP."""
        print("Testing task complexity analysis...")
        
        if not self.created_task_ids:
            print("❌ No tasks available for complexity analysis")
            return False
        
        task_id = self.created_task_ids[0]
        
        request_data = {
            "tool_name": "analyze_task_complexity",
            "arguments": {
                "task_id": task_id,
                "factors": {
                    "technical_difficulty": 7,
                    "scope": 5,
                    "uncertainty": 6
                }
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            complexity = response["result"]["complexity"]
            print(f"✅ Complexity analysis completed for task {task_id}")
            print(f"   Overall score: {complexity['overall_score']}")
            return True
        else:
            print(f"❌ Complexity analysis failed: {response}")
            return False
    
    async def test_task_statistics(self) -> bool:
        """Test task statistics via MCP."""
        print("Testing task statistics...")
        
        request_data = {
            "tool_name": "get_task_statistics",
            "arguments": {}
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            statistics = response["result"]["statistics"]
            print(f"✅ Task statistics retrieved successfully")
            print(f"   Total tasks: {statistics['total_tasks']}")
            print(f"   Completion rate: {statistics['completion_rate']:.1f}%")
            return True
        else:
            print(f"❌ Task statistics failed: {response}")
            return False
    
    async def test_workflow_execution(self) -> bool:
        """Test workflow execution."""
        print("Testing workflow execution...")
        
        workflow_data = {
            "workflow_name": "create_task_with_subtasks",
            "parameters": {
                "main_task": {
                    "title": "Workflow Test Task",
                    "description": "Task created via workflow execution",
                    "priority": "medium"
                },
                "subtasks": [
                    {
                        "title": "Subtask 1",
                        "description": "First subtask",
                        "completed": False
                    },
                    {
                        "title": "Subtask 2", 
                        "description": "Second subtask",
                        "completed": False
                    }
                ]
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/execute-workflow",
            json=workflow_data
        )
        
        if response.get("success"):
            result = response["result"]
            main_task = result["main_task"]
            self.created_task_ids.append(main_task["id"])
            print(f"✅ Workflow executed successfully")
            print(f"   Created task: {main_task['id']}")
            print(f"   Subtasks created: {result['total_subtasks']}")
            return True
        else:
            print(f"❌ Workflow execution failed: {response}")
            return False
    
    async def cleanup(self):
        """Clean up created resources."""
        print("Cleaning up created resources...")
        
        # Delete created dependencies
        for dep_id in self.created_dependency_ids:
            request_data = {
                "tool_name": "remove_dependency",
                "arguments": {"dependency_id": dep_id}
            }
            await self.make_request("POST", f"{MCP_BASE_URL}/process", json=request_data)
        
        # Delete created tasks
        for task_id in self.created_task_ids:
            request_data = {
                "tool_name": "delete_task",
                "arguments": {"task_id": task_id}
            }
            await self.make_request("POST", f"{MCP_BASE_URL}/process", json=request_data)
        
        print(f"✅ Cleanup completed: {len(self.created_task_ids)} tasks, {len(self.created_dependency_ids)} dependencies")
    
    async def run_all_tests(self) -> bool:
        """Run all tests."""
        print("🚀 Starting Metis FastMCP Tests\n")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("MCP Status", self.test_mcp_status),
            ("MCP Capabilities", self.test_mcp_capabilities),
            ("Create Task", self.test_create_task),
            ("Get Task", self.test_get_task),
            ("List Tasks", self.test_list_tasks),
            ("Add Subtask", self.test_add_subtask),
            ("Create Dependency", self.test_create_dependency),
            ("Task Complexity Analysis", self.test_task_complexity_analysis),
            ("Task Statistics", self.test_task_statistics),
            ("Workflow Execution", self.test_workflow_execution),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            try:
                if await test_func():
                    passed += 1
                else:
                    print(f"Test '{test_name}' failed")
            except Exception as e:
                print(f"❌ Test '{test_name}' error: {e}")
        
        # Cleanup
        await self.cleanup()
        
        print(f"\n🏁 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("❌ Some tests failed")
            return False


async def main():
    """Main test function."""
    async with MetisMCPTester() as tester:
        success = await tester.run_all_tests()
        return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)