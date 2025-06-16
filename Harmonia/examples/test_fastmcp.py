"""
Test script for Harmonia's FastMCP implementation.

This script tests the FastMCP implementation in Harmonia by:
1. Testing workflow definition management tools
2. Testing workflow execution tools
3. Testing template management tools
4. Testing component integration tools
5. Testing the API endpoints (optional)

Usage:
    python -m examples.test_fastmcp
"""

import asyncio
import json
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from harmonia.core.mcp import (
    # Workflow definition tools
    create_workflow_definition, update_workflow_definition, delete_workflow_definition,
    get_workflow_definition, list_workflow_definitions,
    # Workflow execution tools
    execute_workflow, cancel_workflow_execution, pause_workflow_execution,
    resume_workflow_execution, get_workflow_execution_status, list_workflow_executions,
    # Template tools
    create_template, instantiate_template, list_templates,
    # Component tools
    list_components, get_component_actions, execute_component_action,
    # Registration
    register_tools
)

# Optional API testing
API_TEST_ENABLED = False
if API_TEST_ENABLED:
    import httpx


async def create_mock_workflow_engine():
    """Create a mock workflow engine for testing."""
    # In a real scenario, this would be the actual workflow engine
    # For testing purposes, we'll create a mock
    class MockStateManager:
        def __init__(self):
            self.workflows = {}
            self.executions = {}
        
        async def save_workflow_definition(self, workflow_def):
            self.workflows[str(workflow_def.id)] = workflow_def
        
        async def load_workflow_definition(self, workflow_id):
            return self.workflows.get(str(workflow_id))
        
        async def delete_workflow_definition(self, workflow_id):
            self.workflows.pop(str(workflow_id), None)
        
        async def list_workflow_definitions(self, limit, offset):
            return list(self.workflows.values())[offset:offset+limit]
        
        async def list_workflow_executions(self, limit, offset, status=None):
            executions = list(self.executions.values())
            if status:
                executions = [e for e in executions if e.status == status]
            return executions[offset:offset+limit]
    
    class MockComponentRegistry:
        def get_components(self):
            return ["component1", "component2", "component3"]
        
        def has_component(self, name):
            return name in self.get_components()
        
        def get_component(self, name):
            class MockComponent:
                async def get_actions(self):
                    return ["action1", "action2"]
            return MockComponent()
        
        async def execute_action(self, component_name, action, params):
            return {"result": f"Executed {action} on {component_name} with {params}"}
    
    class MockWorkflowEngine:
        def __init__(self):
            self.state_manager = MockStateManager()
            self.component_registry = MockComponentRegistry()
            self.template_manager = None
            self.active_executions = []
        
        async def execute_workflow(self, workflow_def, input_data, metadata):
            from harmonia.models.workflow import WorkflowExecution, WorkflowStatus
            execution = WorkflowExecution(
                id=uuid.uuid4(),
                workflow_id=workflow_def.id,
                status=WorkflowStatus.RUNNING,
                input_data=input_data,
                metadata=metadata
            )
            self.state_manager.executions[str(execution.id)] = execution
            return execution
        
        async def cancel_workflow(self, execution_id):
            execution = self.state_manager.executions.get(str(execution_id))
            if execution:
                execution.status = "CANCELLED"
                return True
            return False
        
        async def pause_workflow(self, execution_id):
            execution = self.state_manager.executions.get(str(execution_id))
            if execution:
                execution.status = "PAUSED"
                return True
            return False
        
        async def resume_workflow(self, execution_id):
            execution = self.state_manager.executions.get(str(execution_id))
            if execution:
                execution.status = "RUNNING"
                return True
            return False
        
        async def get_workflow_status(self, execution_id):
            execution = self.state_manager.executions.get(str(execution_id))
            if execution:
                class MockExecutionSummary:
                    def __init__(self, execution):
                        self.execution_id = execution.id
                        self.workflow_id = execution.workflow_id
                        self.status = execution.status
                        self.progress = 0.5
                        self.started_at = execution.started_at if hasattr(execution, 'started_at') else datetime.now()
                        self.completed_at = execution.completed_at if hasattr(execution, 'completed_at') else None
                        self.task_statuses = {"task1": "COMPLETED", "task2": "RUNNING"}
                        self.error_message = None
                return MockExecutionSummary(execution)
            return None
    
    return MockWorkflowEngine()


async def test_workflow_definition_tools():
    """Test workflow definition management tools."""
    print("\n--- Testing Workflow Definition Management Tools ---")
    
    # Create mock workflow engine
    workflow_engine = await create_mock_workflow_engine()
    
    try:
        # Test create_workflow_definition
        print("\nTesting create_workflow_definition...")
        workflow_result = await create_workflow_definition(
            name="Test Workflow",
            description="A test workflow for FastMCP",
            tasks={
                "task1": {
                    "name": "Task 1",
                    "description": "First task",
                    "component": "test_component",
                    "action": "test_action",
                    "parameters": {}
                },
                "task2": {
                    "name": "Task 2", 
                    "description": "Second task",
                    "component": "test_component",
                    "action": "test_action",
                    "parameters": {},
                    "dependencies": ["task1"]
                }
            },
            input_schema={"type": "object", "properties": {"input1": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"output1": {"type": "string"}}},
            version="1.0",
            metadata={"test": True},
            workflow_engine=workflow_engine
        )
        print(f"Result: {json.dumps(workflow_result, indent=2)}")
        
        # Get the workflow ID for further tests
        if "workflow_id" in workflow_result:
            workflow_id = workflow_result["workflow_id"]
            
            # Test get_workflow_definition
            print("\nTesting get_workflow_definition...")
            get_result = await get_workflow_definition(
                workflow_id=workflow_id,
                workflow_engine=workflow_engine
            )
            print(f"Result: {json.dumps(get_result, indent=2)}")
            
            # Test update_workflow_definition
            print("\nTesting update_workflow_definition...")
            update_result = await update_workflow_definition(
                workflow_id=workflow_id,
                name="Updated Test Workflow",
                description="An updated test workflow for FastMCP",
                version="1.1",
                workflow_engine=workflow_engine
            )
            print(f"Result: {json.dumps(update_result, indent=2)}")
        
        # Test list_workflow_definitions
        print("\nTesting list_workflow_definitions...")
        list_result = await list_workflow_definitions(
            limit=10,
            offset=0,
            workflow_engine=workflow_engine
        )
        print(f"Result: {json.dumps(list_result, indent=2)}")
        
        # Test delete_workflow_definition (if we have a workflow)
        if "workflow_id" in workflow_result:
            print("\nTesting delete_workflow_definition...")
            delete_result = await delete_workflow_definition(
                workflow_id=workflow_id,
                workflow_engine=workflow_engine
            )
            print(f"Result: {json.dumps(delete_result, indent=2)}")
        
    except Exception as e:
        print(f"Error during workflow definition testing: {str(e)}")


async def test_workflow_execution_tools():
    """Test workflow execution tools."""
    print("\n--- Testing Workflow Execution Tools ---")
    
    # Create mock workflow engine
    workflow_engine = await create_mock_workflow_engine()
    
    try:
        # First create a workflow definition to execute
        workflow_result = await create_workflow_definition(
            name="Execution Test Workflow",
            description="A workflow for testing execution",
            tasks={
                "task1": {
                    "name": "Task 1",
                    "description": "First task",
                    "component": "test_component",
                    "action": "test_action",
                    "parameters": {}
                }
            },
            workflow_engine=workflow_engine
        )
        
        if "workflow_id" in workflow_result:
            workflow_id = workflow_result["workflow_id"]
            
            # Test execute_workflow
            print("\nTesting execute_workflow...")
            execution_result = await execute_workflow(
                workflow_id=workflow_id,
                input_data={"input1": "test value"},
                metadata={"test_execution": True},
                workflow_engine=workflow_engine
            )
            print(f"Result: {json.dumps(execution_result, indent=2)}")
            
            # Get the execution ID for further tests
            if "execution_id" in execution_result:
                execution_id = execution_result["execution_id"]
                
                # Test get_workflow_execution_status
                print("\nTesting get_workflow_execution_status...")
                status_result = await get_workflow_execution_status(
                    execution_id=execution_id,
                    workflow_engine=workflow_engine
                )
                print(f"Result: {json.dumps(status_result, indent=2)}")
                
                # Test pause_workflow_execution
                print("\nTesting pause_workflow_execution...")
                pause_result = await pause_workflow_execution(
                    execution_id=execution_id,
                    workflow_engine=workflow_engine
                )
                print(f"Result: {json.dumps(pause_result, indent=2)}")
                
                # Test resume_workflow_execution
                print("\nTesting resume_workflow_execution...")
                resume_result = await resume_workflow_execution(
                    execution_id=execution_id,
                    workflow_engine=workflow_engine
                )
                print(f"Result: {json.dumps(resume_result, indent=2)}")
                
                # Test cancel_workflow_execution
                print("\nTesting cancel_workflow_execution...")
                cancel_result = await cancel_workflow_execution(
                    execution_id=execution_id,
                    workflow_engine=workflow_engine
                )
                print(f"Result: {json.dumps(cancel_result, indent=2)}")
            
            # Test list_workflow_executions
            print("\nTesting list_workflow_executions...")
            list_result = await list_workflow_executions(
                workflow_id=workflow_id,
                limit=10,
                offset=0,
                workflow_engine=workflow_engine
            )
            print(f"Result: {json.dumps(list_result, indent=2)}")
        
    except Exception as e:
        print(f"Error during workflow execution testing: {str(e)}")


async def test_component_integration_tools():
    """Test component integration tools."""
    print("\n--- Testing Component Integration Tools ---")
    
    # Create mock workflow engine
    workflow_engine = await create_mock_workflow_engine()
    
    try:
        # Test list_components
        print("\nTesting list_components...")
        components_result = await list_components(
            workflow_engine=workflow_engine
        )
        print(f"Result: {json.dumps(components_result, indent=2)}")
        
        # Test get_component_actions
        print("\nTesting get_component_actions...")
        actions_result = await get_component_actions(
            component_name="component1",
            workflow_engine=workflow_engine
        )
        print(f"Result: {json.dumps(actions_result, indent=2)}")
        
        # Test execute_component_action
        print("\nTesting execute_component_action...")
        execute_result = await execute_component_action(
            component_name="component1",
            action="action1",
            parameters={"param1": "value1"},
            workflow_engine=workflow_engine
        )
        print(f"Result: {json.dumps(execute_result, indent=2)}")
        
    except Exception as e:
        print(f"Error during component integration testing: {str(e)}")


async def test_api_endpoints():
    """Test FastMCP API endpoints (if enabled)."""
    if not API_TEST_ENABLED:
        print("\n--- API Testing Disabled ---")
        return
    
    print("\n--- Testing FastMCP API Endpoints ---")
    
    # Base URL for FastMCP endpoints
    base_url = "http://localhost:8005/api/mcp/v2"  # Harmonia's port
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            print("\nTesting /health endpoint...")
            health_response = await client.get(f"{base_url}/health")
            print(f"Status: {health_response.status_code}")
            print(f"Response: {json.dumps(health_response.json(), indent=2)}")
            
            # Test workflow-status endpoint
            print("\nTesting /workflow-status endpoint...")
            status_response = await client.get(f"{base_url}/workflow-status")
            print(f"Status: {status_response.status_code}")
            print(f"Response: {json.dumps(status_response.json(), indent=2)}")
            
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
            
    except Exception as e:
        print(f"Error during API testing: {str(e)}")


async def main():
    """Main test function."""
    print("Starting Harmonia FastMCP test...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Test workflow definition tools
        await test_workflow_definition_tools()
        
        # Test workflow execution tools
        await test_workflow_execution_tools()
        
        # Test component integration tools
        await test_component_integration_tools()
        
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