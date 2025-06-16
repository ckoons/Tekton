#!/usr/bin/env python3
"""
Test script for Prometheus FastMCP implementation.

This script tests the FastMCP integration with Prometheus planning and analysis
to ensure all tools work correctly.
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any, List


# Configuration
PROMETHEUS_BASE_URL = "http://localhost:8006"  # Default Prometheus port
MCP_BASE_URL = f"{PROMETHEUS_BASE_URL}/api/mcp/v2"


class PrometheusMCPTester:
    """Test class for Prometheus MCP functionality."""
    
    def __init__(self):
        """Initialize the tester."""
        self.session = None
        self.created_plan_ids = []
        self.created_milestone_ids = []
    
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
        
        response = await self.make_request("GET", f"{PROMETHEUS_BASE_URL}/health")
        
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
                "planning",
                "retrospective_analysis",
                "resource_management",
                "improvement_recommendations"
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
    
    async def test_create_project_plan(self) -> bool:
        """Test project plan creation via MCP."""
        print("Testing project plan creation...")
        
        plan_data = {
            "tool_name": "create_project_plan",
            "arguments": {
                "project_name": "Test Project via MCP",
                "description": "This is a test project created through the MCP interface",
                "start_date": "2024-06-01",
                "end_date": "2024-12-31",
                "objectives": [
                    "Deliver high-quality software",
                    "Meet all deadlines",
                    "Stay within budget"
                ],
                "constraints": ["Limited budget", "Fixed deadline"],
                "priority": "high",
                "budget": 100000.0
            }
        }
        
        response = await self.make_request(
            "POST", 
            f"{MCP_BASE_URL}/process",
            json=plan_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            plan = response["result"]["plan"]
            self.created_plan_ids.append(plan.get("plan_id", "temp"))
            print(f"✅ Project plan created successfully")
            print(f"   Project: {plan.get('project_name')}")
            print(f"   Milestones: {response['result']['milestones_count']}")
            return True
        else:
            print(f"❌ Project plan creation failed: {response}")
            return False
    
    async def test_critical_path_analysis(self) -> bool:
        """Test critical path analysis via MCP."""
        print("Testing critical path analysis...")
        
        tasks = [
            {
                "id": "task1",
                "name": "Design Phase",
                "duration": 10,
                "dependencies": []
            },
            {
                "id": "task2", 
                "name": "Development Phase",
                "duration": 20,
                "dependencies": ["task1"]
            },
            {
                "id": "task3",
                "name": "Testing Phase",
                "duration": 15,
                "dependencies": ["task2"]
            },
            {
                "id": "task4",
                "name": "Documentation",
                "duration": 5,
                "dependencies": ["task1"]
            }
        ]
        
        request_data = {
            "tool_name": "analyze_critical_path",
            "arguments": {
                "plan_id": "test_plan",
                "tasks": tasks
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process", 
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            result = response["result"]
            print(f"✅ Critical path analysis completed")
            print(f"   Project duration: {result['project_duration']} days")
            print(f"   Critical path length: {result['critical_path_length']} tasks")
            return True
        else:
            print(f"❌ Critical path analysis failed: {response}")
            return False
    
    async def test_resource_allocation(self) -> bool:
        """Test resource allocation via MCP."""
        print("Testing resource allocation...")
        
        resources = [
            {
                "id": "dev1",
                "name": "Senior Developer",
                "skills": ["python", "javascript", "architecture"],
                "hourly_rate": 150,
                "capacity": 100
            },
            {
                "id": "dev2",
                "name": "Junior Developer", 
                "skills": ["python", "testing"],
                "hourly_rate": 80,
                "capacity": 100
            },
            {
                "id": "qa1",
                "name": "QA Engineer",
                "skills": ["testing", "automation"],
                "hourly_rate": 100,
                "capacity": 100
            }
        ]
        
        tasks = [
            {
                "id": "task1",
                "name": "Backend Development",
                "required_skills": ["python"],
                "duration": 10,
                "effort_required": 80
            },
            {
                "id": "task2",
                "name": "Testing",
                "required_skills": ["testing"],
                "duration": 5,
                "effort_required": 100
            }
        ]
        
        request_data = {
            "tool_name": "allocate_resources",
            "arguments": {
                "plan_id": "test_plan",
                "resources": resources,
                "tasks": tasks,
                "optimization_strategy": "balanced"
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            result = response["result"]
            print(f"✅ Resource allocation completed")
            print(f"   Allocations made: {result['total_allocations']}")
            print(f"   Estimated cost: ${result['estimated_total_cost']}")
            return True
        else:
            print(f"❌ Resource allocation failed: {response}")
            return False
    
    async def test_capacity_analysis(self) -> bool:
        """Test resource capacity analysis via MCP."""
        print("Testing resource capacity analysis...")
        
        resources = [
            {
                "id": "team1",
                "name": "Development Team",
                "capacity": 100,
                "current_utilization": 85,
                "skills": ["development"]
            },
            {
                "id": "team2",
                "name": "QA Team",
                "capacity": 100,
                "current_utilization": 95,
                "skills": ["testing"]
            },
            {
                "id": "team3",
                "name": "DevOps Team",
                "capacity": 100,
                "current_utilization": 60,
                "skills": ["infrastructure"]
            }
        ]
        
        request_data = {
            "tool_name": "analyze_resource_capacity",
            "arguments": {
                "resources": resources,
                "time_period": "monthly"
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            result = response["result"]
            analysis = result["analysis"]
            print(f"✅ Capacity analysis completed")
            print(f"   Total resources: {analysis['total_resources']}")
            print(f"   Bottlenecks identified: {len(analysis['bottlenecks'])}")
            return True
        else:
            print(f"❌ Capacity analysis failed: {response}")
            return False
    
    async def test_retrospective_analysis(self) -> bool:
        """Test retrospective analysis via MCP."""
        print("Testing retrospective analysis...")
        
        planned_metrics = {
            "duration": 60,  # days
            "budget": 80000,  # dollars
            "quality_score": 95,  # percentage
            "team_satisfaction": 85  # percentage
        }
        
        actual_metrics = {
            "duration": 70,  # 10 days over
            "budget": 85000,  # 5k over budget
            "quality_score": 92,  # slightly under
            "team_satisfaction": 88  # better than expected
        }
        
        request_data = {
            "tool_name": "conduct_retrospective",
            "arguments": {
                "project_id": "completed_project_1",
                "planned_metrics": planned_metrics,
                "actual_metrics": actual_metrics,
                "team_feedback": [
                    "Communication could be improved",
                    "Technical challenges were underestimated",
                    "Good team collaboration"
                ]
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            result = response["result"]
            retrospective = result["retrospective"]
            print(f"✅ Retrospective analysis completed")
            print(f"   Overall rating: {retrospective['overall_rating']}")
            print(f"   Insights found: {len(retrospective['insights'])}")
            return True
        else:
            print(f"❌ Retrospective analysis failed: {response}")
            return False
    
    async def test_improvement_recommendations(self) -> bool:
        """Test improvement recommendations via MCP."""
        print("Testing improvement recommendations...")
        
        project_data = {
            "metrics": {
                "planning_accuracy": 75,
                "on_time_delivery": 80,
                "defect_rate": 8,
                "resource_utilization": 70
            },
            "project_type": "software_development",
            "team_size": 8,
            "duration_weeks": 12
        }
        
        request_data = {
            "tool_name": "generate_improvement_recommendations",
            "arguments": {
                "project_data": project_data,
                "focus_areas": ["planning", "execution", "quality"],
                "constraint_types": ["time", "budget"]
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/process",
            json=request_data
        )
        
        if response.get("success") and response.get("result", {}).get("success"):
            result = response["result"]
            recommendations = result["recommendations"]
            total_recommendations = recommendations["total_count"]
            print(f"✅ Improvement recommendations generated")
            print(f"   Total recommendations: {total_recommendations}")
            print(f"   High priority: {len(recommendations['high_priority'])}")
            return True
        else:
            print(f"❌ Improvement recommendations failed: {response}")
            return False
    
    async def test_workflow_execution(self) -> bool:
        """Test analysis workflow execution."""
        print("Testing workflow execution...")
        
        workflow_data = {
            "workflow_name": "full_project_analysis",
            "parameters": {
                "project_data": {
                    "name": "Workflow Test Project",
                    "description": "Project created via workflow execution",
                    "start_date": "2024-07-01",
                    "end_date": "2024-12-31",
                    "objectives": ["Complete analysis workflow test"],
                    "planned_metrics": {
                        "duration": 90,
                        "budget": 120000
                    },
                    "actual_metrics": {
                        "duration": 95,
                        "budget": 125000
                    }
                },
                "focus_areas": ["planning", "execution"]
            }
        }
        
        response = await self.make_request(
            "POST",
            f"{MCP_BASE_URL}/execute-analysis-workflow",
            json=workflow_data
        )
        
        if response.get("success"):
            result = response["result"]
            workflow_summary = result["workflow_summary"]
            print(f"✅ Analysis workflow executed successfully")
            print(f"   Steps completed: {workflow_summary['steps_completed']}")
            print(f"   Analysis confidence: {workflow_summary['analysis_confidence']}")
            return True
        else:
            print(f"❌ Workflow execution failed: {response}")
            return False
    
    async def test_planning_status(self) -> bool:
        """Test planning status endpoint."""
        print("Testing planning status...")
        
        response = await self.make_request("GET", f"{MCP_BASE_URL}/planning-status")
        
        if response.get("success"):
            print(f"✅ Planning status retrieved successfully")
            print(f"   Service status: {response['status']}")
            print(f"   MCP tools available: {response['mcp_tools']}")
            return True
        else:
            print(f"❌ Planning status failed: {response}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests."""
        print("🚀 Starting Prometheus FastMCP Tests\n")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("MCP Status", self.test_mcp_status),
            ("MCP Capabilities", self.test_mcp_capabilities),
            ("Create Project Plan", self.test_create_project_plan),
            ("Critical Path Analysis", self.test_critical_path_analysis),
            ("Resource Allocation", self.test_resource_allocation),
            ("Capacity Analysis", self.test_capacity_analysis),
            ("Retrospective Analysis", self.test_retrospective_analysis),
            ("Improvement Recommendations", self.test_improvement_recommendations),
            ("Workflow Execution", self.test_workflow_execution),
            ("Planning Status", self.test_planning_status),
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
        
        print(f"\n🏁 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("❌ Some tests failed")
            return False


async def main():
    """Main test function."""
    async with PrometheusMCPTester() as tester:
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