#!/usr/bin/env python3
"""
Test script for Telos FastMCP implementation.

This script tests all FastMCP tools and capabilities for Telos requirements management,
tracing, validation, and Prometheus integration.
"""

import asyncio
import json
import uuid
from datetime import datetime
from tekton.mcp.fastmcp.client import FastMCPClient


class TelosFastMCPTester:
    """Test suite for Telos FastMCP implementation."""
    
    def __init__(self, base_url="http://localhost:8008"):
        """Initialize the tester with Telos server URL."""
        self.base_url = base_url
        self.fastmcp_url = f"{base_url}/api/mcp/v2"
        self.client = FastMCPClient(self.fastmcp_url)
        self.test_project_id = None
        self.test_requirement_ids = []
        
    async def run_all_tests(self):
        """Run all tests for Telos FastMCP."""
        print("🚀 Starting Telos FastMCP Test Suite")
        print("=" * 50)
        
        try:
            # Test server availability
            await self.test_server_availability()
            
            # Test capabilities and tools
            await self.test_capabilities()
            await self.test_tools_list()
            
            # Test requirements management
            await self.test_requirements_management()
            
            # Test requirement tracing
            await self.test_requirement_tracing()
            
            # Test requirement validation
            await self.test_requirement_validation()
            
            # Test Prometheus integration (if available)
            await self.test_prometheus_integration()
            
            # Test workflow operations
            await self.test_workflow_operations()
            
            print("\n✅ All Telos FastMCP tests completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            raise
    
    async def test_server_availability(self):
        """Test if the Telos FastMCP server is available."""
        print("\n📡 Testing server availability...")
        
        try:
            health = await self.client.get_health()
            print(f"✅ Server health: {health}")
            
            if health.get("status") != "healthy":
                raise Exception(f"Server not healthy: {health}")
                
        except Exception as e:
            print(f"❌ Server availability test failed: {e}")
            raise
    
    async def test_capabilities(self):
        """Test getting capabilities from the server."""
        print("\n🔧 Testing capabilities...")
        
        try:
            capabilities = await self.client.get_capabilities()
            print(f"✅ Retrieved {len(capabilities)} capabilities")
            
            # Verify expected capabilities exist
            expected_capabilities = [
                "requirements_management",
                "requirement_tracing", 
                "requirement_validation",
                "prometheus_integration"
            ]
            
            capability_names = [cap.get("name") for cap in capabilities]
            for expected in expected_capabilities:
                if expected in capability_names:
                    print(f"  ✓ Found capability: {expected}")
                else:
                    print(f"  ⚠ Missing capability: {expected}")
                    
        except Exception as e:
            print(f"❌ Capabilities test failed: {e}")
            raise
    
    async def test_tools_list(self):
        """Test getting tools list from the server."""
        print("\n🛠 Testing tools list...")
        
        try:
            tools = await self.client.get_tools()
            print(f"✅ Retrieved {len(tools)} tools")
            
            # Verify expected tools exist
            expected_tools = [
                "create_project", "get_project", "list_projects",
                "create_requirement", "get_requirement", "update_requirement",
                "create_trace", "list_traces",
                "validate_project",
                "analyze_requirements", "create_plan"
            ]
            
            tool_names = [tool.get("name") for tool in tools]
            for expected in expected_tools:
                if expected in tool_names:
                    print(f"  ✓ Found tool: {expected}")
                else:
                    print(f"  ⚠ Missing tool: {expected}")
                    
        except Exception as e:
            print(f"❌ Tools list test failed: {e}")
            raise
    
    async def test_requirements_management(self):
        """Test requirements management tools."""
        print("\n📋 Testing requirements management...")
        
        try:
            # Test create_project
            print("  Testing create_project...")
            project_name = f"Test Project {uuid.uuid4().hex[:8]}"
            project_result = await self.client.call_tool("create_project", {
                "name": project_name,
                "description": "Test project for FastMCP validation",
                "metadata": {"test": True, "created_by": "fastmcp_test"}
            })
            
            if "error" in project_result:
                raise Exception(f"create_project failed: {project_result['error']}")
            
            self.test_project_id = project_result["project_id"]
            print(f"  ✅ Created project: {self.test_project_id}")
            
            # Test list_projects
            print("  Testing list_projects...")
            projects_result = await self.client.call_tool("list_projects", {})
            
            if "error" in projects_result:
                raise Exception(f"list_projects failed: {projects_result['error']}")
            
            project_count = projects_result.get("count", 0)
            print(f"  ✅ Found {project_count} projects")
            
            # Test get_project
            print("  Testing get_project...")
            get_project_result = await self.client.call_tool("get_project", {
                "project_id": self.test_project_id
            })
            
            if "error" in get_project_result:
                raise Exception(f"get_project failed: {get_project_result['error']}")
            
            print(f"  ✅ Retrieved project details")
            
            # Test create_requirement
            print("  Testing create_requirement...")
            requirement_data = [
                {
                    "title": "User Authentication",
                    "description": "The system must authenticate users with username and password",
                    "requirement_type": "functional",
                    "priority": "high"
                },
                {
                    "title": "Response Time",
                    "description": "The system must respond to user requests within 2 seconds",
                    "requirement_type": "non-functional",
                    "priority": "medium"
                },
                {
                    "title": "Data Security",
                    "description": "All user data must be encrypted at rest and in transit",
                    "requirement_type": "security",
                    "priority": "critical"
                }
            ]
            
            for req_data in requirement_data:
                req_result = await self.client.call_tool("create_requirement", {
                    "project_id": self.test_project_id,
                    **req_data
                })
                
                if "error" in req_result:
                    raise Exception(f"create_requirement failed: {req_result['error']}")
                
                req_id = req_result["requirement_id"]
                self.test_requirement_ids.append(req_id)
                print(f"  ✅ Created requirement: {req_data['title']} ({req_id})")
            
            # Test get_requirement
            print("  Testing get_requirement...")
            get_req_result = await self.client.call_tool("get_requirement", {
                "project_id": self.test_project_id,
                "requirement_id": self.test_requirement_ids[0]
            })
            
            if "error" in get_req_result:
                raise Exception(f"get_requirement failed: {get_req_result['error']}")
            
            print(f"  ✅ Retrieved requirement details")
            
            # Test update_requirement
            print("  Testing update_requirement...")
            update_result = await self.client.call_tool("update_requirement", {
                "project_id": self.test_project_id,
                "requirement_id": self.test_requirement_ids[0],
                "status": "in-progress",
                "tags": ["auth", "security"]
            })
            
            if "error" in update_result:
                raise Exception(f"update_requirement failed: {update_result['error']}")
            
            print(f"  ✅ Updated requirement")
            
        except Exception as e:
            print(f"❌ Requirements management test failed: {e}")
            raise
    
    async def test_requirement_tracing(self):
        """Test requirement tracing tools."""
        print("\n🔗 Testing requirement tracing...")
        
        if not self.test_project_id or len(self.test_requirement_ids) < 2:
            print("  ⚠ Skipping tracing tests - insufficient test data")
            return
        
        try:
            # Test create_trace
            print("  Testing create_trace...")
            trace_result = await self.client.call_tool("create_trace", {
                "project_id": self.test_project_id,
                "source_id": self.test_requirement_ids[0],
                "target_id": self.test_requirement_ids[1],
                "trace_type": "implements",
                "description": "Authentication implements security requirements"
            })
            
            if "error" in trace_result:
                raise Exception(f"create_trace failed: {trace_result['error']}")
            
            trace_id = trace_result["trace_id"]
            print(f"  ✅ Created trace: {trace_id}")
            
            # Test list_traces
            print("  Testing list_traces...")
            traces_result = await self.client.call_tool("list_traces", {
                "project_id": self.test_project_id
            })
            
            if "error" in traces_result:
                raise Exception(f"list_traces failed: {traces_result['error']}")
            
            trace_count = traces_result.get("count", 0)
            print(f"  ✅ Found {trace_count} traces")
            
        except Exception as e:
            print(f"❌ Requirement tracing test failed: {e}")
            raise
    
    async def test_requirement_validation(self):
        """Test requirement validation tools."""
        print("\n✅ Testing requirement validation...")
        
        if not self.test_project_id:
            print("  ⚠ Skipping validation tests - no test project")
            return
        
        try:
            # Test validate_project
            print("  Testing validate_project...")
            validation_result = await self.client.call_tool("validate_project", {
                "project_id": self.test_project_id,
                "check_completeness": True,
                "check_verifiability": True,
                "check_clarity": True
            })
            
            if "error" in validation_result:
                raise Exception(f"validate_project failed: {validation_result['error']}")
            
            summary = validation_result.get("summary", {})
            total_reqs = summary.get("total_requirements", 0)
            passed = summary.get("passed", 0)
            pass_percentage = summary.get("pass_percentage", 0)
            
            print(f"  ✅ Validation completed: {passed}/{total_reqs} passed ({pass_percentage:.1f}%)")
            
        except Exception as e:
            print(f"❌ Requirement validation test failed: {e}")
            raise
    
    async def test_prometheus_integration(self):
        """Test Prometheus integration tools."""
        print("\n🎯 Testing Prometheus integration...")
        
        if not self.test_project_id:
            print("  ⚠ Skipping Prometheus tests - no test project")
            return
        
        try:
            # Test analyze_requirements
            print("  Testing analyze_requirements...")
            analysis_result = await self.client.call_tool("analyze_requirements", {
                "project_id": self.test_project_id
            })
            
            if "error" in analysis_result:
                print(f"  ⚠ analyze_requirements failed (Prometheus may not be available): {analysis_result['error']}")
            else:
                print(f"  ✅ Requirements analysis completed")
            
            # Test create_plan
            print("  Testing create_plan...")
            plan_result = await self.client.call_tool("create_plan", {
                "project_id": self.test_project_id
            })
            
            if "error" in plan_result:
                print(f"  ⚠ create_plan failed (Prometheus may not be available): {plan_result['error']}")
            else:
                print(f"  ✅ Plan creation completed")
                
        except Exception as e:
            print(f"❌ Prometheus integration test failed: {e}")
            # Don't raise here as Prometheus integration is optional
    
    async def test_workflow_operations(self):
        """Test workflow operations."""
        print("\n🔄 Testing workflow operations...")
        
        try:
            # Test create_project_with_requirements workflow
            print("  Testing create_project_with_requirements workflow...")
            workflow_result = await self.client.call_workflow("create_project_with_requirements", {
                "project": {
                    "name": f"Workflow Test Project {uuid.uuid4().hex[:8]}",
                    "description": "Project created via workflow test",
                    "metadata": {"workflow_test": True}
                },
                "requirements": [
                    {
                        "title": "Workflow Requirement 1",
                        "description": "First requirement created via workflow",
                        "requirement_type": "functional",
                        "priority": "medium"
                    },
                    {
                        "title": "Workflow Requirement 2",
                        "description": "Second requirement created via workflow",
                        "requirement_type": "non-functional",
                        "priority": "low"
                    }
                ]
            })
            
            if "error" in workflow_result:
                print(f"  ⚠ create_project_with_requirements workflow failed: {workflow_result['error']}")
            else:
                workflow_project_id = workflow_result.get("project", {}).get("project_id")
                req_count = len(workflow_result.get("requirements", []))
                print(f"  ✅ Workflow created project {workflow_project_id} with {req_count} requirements")
            
            # Test validate_and_analyze_project workflow
            if self.test_project_id:
                print("  Testing validate_and_analyze_project workflow...")
                workflow_result = await self.client.call_workflow("validate_and_analyze_project", {
                    "project_id": self.test_project_id,
                    "check_completeness": True,
                    "check_verifiability": True,
                    "check_clarity": True
                })
                
                if "error" in workflow_result:
                    print(f"  ⚠ validate_and_analyze_project workflow failed: {workflow_result['error']}")
                else:
                    print(f"  ✅ Validation and analysis workflow completed")
            
        except Exception as e:
            print(f"❌ Workflow operations test failed: {e}")
            # Don't raise here as workflows are optional features
    
    async def cleanup(self):
        """Clean up test data."""
        print("\n🧹 Cleaning up test data...")
        
        # Note: In a real implementation, you might want to add delete operations
        # For now, we'll leave the test data as it can be useful for manual inspection
        print("  ℹ Test data preserved for manual inspection")


async def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Telos FastMCP implementation")
    parser.add_argument("--url", default="http://localhost:8008", 
                       help="Telos server URL (default: http://localhost:8008)")
    parser.add_argument("--cleanup", action="store_true",
                       help="Clean up test data after tests")
    
    args = parser.parse_args()
    
    tester = TelosFastMCPTester(args.url)
    
    try:
        await tester.run_all_tests()
        
        if args.cleanup:
            await tester.cleanup()
            
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))