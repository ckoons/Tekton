"""
Test script for Ergon's FastMCP implementation.

This script tests the FastMCP implementation in Ergon by:
1. Initializing the FastMCP-compatible tools
2. Testing various tool calls
3. Testing the API endpoints (optional)

Usage:
    python -m examples.test_fastmcp
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from ergon.core.a2a_client import A2AClient
from ergon.utils.tekton_integration import get_component_api_url
from ergon.core.mcp import (
    # Agent tools
    create_agent, update_agent, delete_agent, get_agent, list_agents,
    # Workflow tools
    create_workflow, update_workflow, execute_workflow, get_workflow_status,
    # Task management tools
    create_task, assign_task, update_task_status, get_task, list_tasks,
    # Registration
    register_tools
)

# Optional API testing
API_TEST_ENABLED = False
if API_TEST_ENABLED:
    import httpx


async def test_agent_tools():
    """Test agent management tools."""
    print("\n--- Testing Agent Management Tools ---")
    
    # Initialize the A2A client for testing
    a2a_client = A2AClient(
        agent_id="ergon-test",
        agent_name="Ergon Test Client",
        capabilities={"processing": ["agent_management", "workflow_management", "task_management"]}
    )
    await a2a_client.initialize()
    
    try:
        # Test create_agent
        print("\nTesting create_agent...")
        agent_result = await create_agent(
            agent_name="Test Agent",
            agent_description="A test agent for FastMCP",
            capabilities={"processing": ["test"]},
            metadata={"test": True},
            a2a_client=a2a_client
        )
        print(f"Result: {json.dumps(agent_result, indent=2)}")
        
        # Get the agent ID for further tests
        if "agent_id" in agent_result:
            agent_id = agent_result["agent_id"]
            
            # Test get_agent
            print("\nTesting get_agent...")
            get_result = await get_agent(
                agent_id=agent_id,
                a2a_client=a2a_client
            )
            print(f"Result: {json.dumps(get_result, indent=2)}")
            
            # Test update_agent
            print("\nTesting update_agent...")
            update_result = await update_agent(
                agent_id=agent_id,
                agent_name="Updated Test Agent",
                agent_description="An updated test agent for FastMCP",
                capabilities={"processing": ["test", "updated"]},
                metadata={"test": True, "updated": True},
                a2a_client=a2a_client
            )
            print(f"Result: {json.dumps(update_result, indent=2)}")
            
            # Test delete_agent
            print("\nTesting delete_agent...")
            delete_result = await delete_agent(
                agent_id=agent_id,
                a2a_client=a2a_client
            )
            print(f"Result: {json.dumps(delete_result, indent=2)}")
        
        # Test list_agents
        print("\nTesting list_agents...")
        list_result = await list_agents(
            a2a_client=a2a_client
        )
        print(f"Result: {json.dumps(list_result, indent=2)}")
        
    finally:
        # Clean up
        await a2a_client.close()


async def test_workflow_tools():
    """Test workflow management tools."""
    print("\n--- Testing Workflow Management Tools ---")
    
    # Initialize the A2A client for testing
    a2a_client = A2AClient(
        agent_id="ergon-test",
        agent_name="Ergon Test Client",
        capabilities={"processing": ["agent_management", "workflow_management", "task_management"]}
    )
    await a2a_client.initialize()
    
    try:
        # Test create_workflow
        print("\nTesting create_workflow...")
        workflow_result = await create_workflow(
            name="Test Workflow",
            description="A test workflow for FastMCP",
            tasks={
                "task1": {
                    "name": "Task 1",
                    "description": "First task in the workflow",
                    "type": "process",
                    "parameters": {}
                },
                "task2": {
                    "name": "Task 2",
                    "description": "Second task in the workflow",
                    "type": "process",
                    "parameters": {},
                    "dependencies": ["task1"]
                }
            },
            input_schema={"type": "object", "properties": {"input1": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"output1": {"type": "string"}}},
            metadata={"test": True},
            a2a_client=a2a_client
        )
        print(f"Result: {json.dumps(workflow_result, indent=2)}")
        
        # Get the workflow ID for further tests
        if "workflow_id" in workflow_result:
            workflow_id = workflow_result["workflow_id"]
            
            # Test update_workflow
            print("\nTesting update_workflow...")
            update_result = await update_workflow(
                workflow_id=workflow_id,
                name="Updated Test Workflow",
                description="An updated test workflow for FastMCP",
                tasks={
                    "task1": {
                        "name": "Updated Task 1",
                        "description": "Updated first task in the workflow",
                        "type": "process",
                        "parameters": {}
                    },
                    "task2": {
                        "name": "Updated Task 2",
                        "description": "Updated second task in the workflow",
                        "type": "process",
                        "parameters": {},
                        "dependencies": ["task1"]
                    },
                    "task3": {
                        "name": "Task 3",
                        "description": "Third task in the workflow",
                        "type": "process",
                        "parameters": {},
                        "dependencies": ["task2"]
                    }
                },
                a2a_client=a2a_client
            )
            print(f"Result: {json.dumps(update_result, indent=2)}")
            
            # Test execute_workflow
            print("\nTesting execute_workflow...")
            execution_result = await execute_workflow(
                workflow_id=workflow_id,
                input_data={"input1": "test value"},
                execution_options={"priority": "high"},
                a2a_client=a2a_client
            )
            print(f"Result: {json.dumps(execution_result, indent=2)}")
            
            # Get the execution ID for further tests
            if "execution_id" in execution_result:
                execution_id = execution_result["execution_id"]
                
                # Test get_workflow_status
                print("\nTesting get_workflow_status...")
                status_result = await get_workflow_status(
                    execution_id=execution_id,
                    a2a_client=a2a_client
                )
                print(f"Result: {json.dumps(status_result, indent=2)}")
        
    finally:
        # Clean up
        await a2a_client.close()


async def test_task_tools():
    """Test task management tools."""
    print("\n--- Testing Task Management Tools ---")
    
    # Initialize the A2A client for testing
    a2a_client = A2AClient(
        agent_id="ergon-test",
        agent_name="Ergon Test Client",
        capabilities={"processing": ["agent_management", "workflow_management", "task_management"]}
    )
    await a2a_client.initialize()
    
    try:
        # Test create_task
        print("\nTesting create_task...")
        task_result = await create_task(
            name="Test Task",
            description="A test task for FastMCP",
            required_capabilities=["test"],
            parameters={"param1": "value1"},
            priority="normal",
            metadata={"test": True},
            a2a_client=a2a_client
        )
        print(f"Result: {json.dumps(task_result, indent=2)}")
        
        # Get the task ID for further tests
        if "task_id" in task_result:
            task_id = task_result["task_id"]
            
            # Test get_task
            print("\nTesting get_task...")
            get_result = await get_task(
                task_id=task_id,
                a2a_client=a2a_client
            )
            print(f"Result: {json.dumps(get_result, indent=2)}")
            
            # Test assign_task
            print("\nTesting assign_task...")
            assign_result = await assign_task(
                task_id=task_id,
                agent_id="agent-test",
                a2a_client=a2a_client
            )
            print(f"Result: {json.dumps(assign_result, indent=2)}")
            
            # Test update_task_status
            print("\nTesting update_task_status...")
            update_result = await update_task_status(
                task_id=task_id,
                status="in_progress",
                a2a_client=a2a_client
            )
            print(f"Result: {json.dumps(update_result, indent=2)}")
            
            # Test update_task_status to completed
            print("\nTesting update_task_status to completed...")
            complete_result = await update_task_status(
                task_id=task_id,
                status="completed",
                result={"output": "Task completed successfully"},
                a2a_client=a2a_client
            )
            print(f"Result: {json.dumps(complete_result, indent=2)}")
        
        # Test list_tasks
        print("\nTesting list_tasks...")
        list_result = await list_tasks(
            status="completed",
            limit=10,
            a2a_client=a2a_client
        )
        print(f"Result: {json.dumps(list_result, indent=2)}")
        
    finally:
        # Clean up
        await a2a_client.close()


async def test_api_endpoints():
    """Test FastMCP API endpoints (if enabled)."""
    if not API_TEST_ENABLED:
        print("\n--- API Testing Disabled ---")
        return
    
    print("\n--- Testing FastMCP API Endpoints ---")
    
    # Base URL for FastMCP endpoints
    base_url = f"{get_component_api_url('rhetor')}/mcp/v2"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            print("\nTesting /health endpoint...")
            health_response = await client.get(f"{base_url}/health")
            print(f"Status: {health_response.status_code}")
            print(f"Response: {json.dumps(health_response.json(), indent=2)}")
            
            # Test capabilities endpoint
            print("\nTesting /capabilities endpoint...")
            capabilities_response = await client.get(f"{base_url}/capabilities")
            print(f"Status: {capabilities_response.status_code}")
            print(f"Response: {json.dumps(capabilities_response.json(), indent=2)}")
            
            # Test tools endpoint
            print("\nTesting /tools endpoint...")
            tools_response = await client.get(f"{base_url}/tools")
            print(f"Status: {tools_response.status_code}")
            print(f"Response: {json.dumps(tools_response.json(), indent=2)}")
            
            # Test process endpoint with create_agent tool
            print("\nTesting /process endpoint with create_agent tool...")
            process_response = await client.post(
                f"{base_url}/process",
                json={
                    "tool": "CreateAgent",
                    "parameters": {
                        "agent_name": "API Test Agent",
                        "agent_description": "An agent created via API testing",
                        "capabilities": {"processing": ["api_test"]}
                    }
                }
            )
            print(f"Status: {process_response.status_code}")
            print(f"Response: {json.dumps(process_response.json(), indent=2)}")
            
    except Exception as e:
        print(f"Error during API testing: {str(e)}")


async def main():
    """Main test function."""
    print("Starting Ergon FastMCP test...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Test agent tools
        await test_agent_tools()
        
        # Test workflow tools
        await test_workflow_tools()
        
        # Test task tools
        await test_task_tools()
        
        # Test API endpoints
        await test_api_endpoints()
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    ret_code = asyncio.run(main())
    sys.exit(ret_code)