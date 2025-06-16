# Harmonia FastMCP Integration

This document describes the FastMCP integration in Harmonia, including the implementation approach, available tools, and usage examples.

## Implementation Approach

The Harmonia FastMCP integration follows the "parallel implementation" approach, where the FastMCP endpoints are added alongside any existing MCP functionality. This approach ensures forward compatibility while introducing the benefits of the decorator-based FastMCP approach for workflow orchestration.

## FastMCP Components

### 1. Dependencies

FastMCP is added as a dependency in both `requirements.txt` and `setup.py`:

```python
# In requirements.txt
tekton-llm-client>=1.0.0
tekton-core>=0.1.0  # Added for FastMCP support
jinja2>=3.1.2

# In setup.py
"tekton-core>=0.1.0",
```

### 2. MCP Module

The FastMCP implementation is organized into the following structure:

```
harmonia/
  core/
    mcp/
      __init__.py  # Exports tools and utilities
      tools.py     # Tool definitions using FastMCP decorators
```

### 3. API Integration

FastMCP endpoints are added to the API under a new path prefix `/api/mcp/v2` to maintain clean separation.

```python
# In app.py
app.include_router(fastmcp_router, prefix="/api/mcp/v2")
```

The FastMCP endpoints provide standard MCP functionality plus custom Harmonia endpoints:
- `/api/mcp/v2/health`
- `/api/mcp/v2/workflow-status`
- `/api/mcp/v2/capabilities`
- `/api/mcp/v2/tools`
- `/api/mcp/v2/process`

## Available Tools

### Workflow Definition Management Tools

Harmonia provides comprehensive workflow definition management:

1. `CreateWorkflowDefinition` - Create a new workflow definition
2. `UpdateWorkflowDefinition` - Update an existing workflow definition
3. `DeleteWorkflowDefinition` - Delete a workflow definition
4. `GetWorkflowDefinition` - Get a workflow definition by ID
5. `ListWorkflowDefinitions` - List all workflow definitions

These tools are defined with the `@mcp_capability("workflow_definition_management")` decorator.

### Workflow Execution Tools

Harmonia provides full workflow execution and monitoring capabilities:

1. `ExecuteWorkflow` - Execute a workflow with input data
2. `CancelWorkflowExecution` - Cancel a running workflow execution
3. `PauseWorkflowExecution` - Pause a running workflow execution
4. `ResumeWorkflowExecution` - Resume a paused workflow execution
5. `GetWorkflowExecutionStatus` - Get the status of a workflow execution
6. `ListWorkflowExecutions` - List workflow executions with optional filtering

These tools are defined with the `@mcp_capability("workflow_execution")` decorator.

### Template Management Tools

Harmonia provides workflow template functionality:

1. `CreateTemplate` - Create a workflow template
2. `InstantiateTemplate` - Instantiate a workflow template with parameters
3. `ListTemplates` - List available workflow templates

These tools are defined with the `@mcp_capability("template_management")` decorator.

### Component Integration Tools

Harmonia provides integration with other Tekton components:

1. `ListComponents` - List available Tekton components
2. `GetComponentActions` - Get available actions for a component
3. `ExecuteComponentAction` - Execute an action on a component

These tools are defined with the `@mcp_capability("component_integration")` decorator.

## Usage Examples

### Using the FastMCP API directly

```bash
# Get workflow engine status
curl http://localhost:8005/api/mcp/v2/workflow-status

# Get available tools
curl http://localhost:8005/api/mcp/v2/tools

# Create a workflow definition
curl -X POST http://localhost:8005/api/mcp/v2/process \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "CreateWorkflowDefinition",
    "parameters": {
      "name": "Test Workflow",
      "description": "A test workflow",
      "tasks": {
        "task1": {
          "name": "Task 1",
          "description": "First task",
          "component": "test_component",
          "action": "test_action",
          "parameters": {}
        }
      }
    }
  }'

# Execute a workflow
curl -X POST http://localhost:8005/api/mcp/v2/process \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "ExecuteWorkflow",
    "parameters": {
      "workflow_id": "workflow-uuid-here",
      "input_data": {"input1": "test value"}
    }
  }'
```

### Using the FastMCP client from Python

```python
from tekton.mcp.fastmcp import MCPClient

# Create a client
client = MCPClient(url="http://localhost:8005/api/mcp/v2")

# Get available tools
tools = await client.get_tools()

# Create a workflow definition
result = await client.execute_tool(
    "CreateWorkflowDefinition",
    parameters={
        "name": "Test Workflow",
        "description": "A test workflow",
        "tasks": {
            "task1": {
                "name": "Task 1",
                "description": "First task",
                "component": "test_component",
                "action": "test_action",
                "parameters": {}
            }
        }
    }
)

# Execute the workflow
execution_result = await client.execute_tool(
    "ExecuteWorkflow",
    parameters={
        "workflow_id": result["workflow_id"],
        "input_data": {"input1": "test value"}
    }
)
```

### Using Harmonia tools directly

```python
from harmonia.core.mcp import create_workflow_definition, execute_workflow
from harmonia.core.engine import WorkflowEngine

# Initialize workflow engine
workflow_engine = WorkflowEngine()

# Create a workflow definition
result = await create_workflow_definition(
    name="Test Workflow",
    description="A test workflow",
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

# Execute the workflow
execution_result = await execute_workflow(
    workflow_id=result["workflow_id"],
    input_data={"input1": "test value"},
    workflow_engine=workflow_engine
)
```

## Testing

The FastMCP implementation includes a comprehensive test script that can be run to verify functionality:

```bash
./examples/run_fastmcp_test.sh
```

This script tests all the available tools and their functionality, including:
- Workflow definition management
- Workflow execution and monitoring
- Template management
- Component integration

## Implementation Details

### Tool Registration

All tools are registered during startup using the `register_tools` function, which automatically registers all the tools with their corresponding decorators.

```python
# In fastmcp_endpoints.py
await register_tools(workflow_engine)
```

### Dependency Injection

The FastMCP implementation uses dependency injection to provide the WorkflowEngine to tool handlers. This allows tools to have access to the workflow engine without having to create or manage it.

```python
# In tools.py
async def create_workflow_definition(
    name: str,
    # ...
    workflow_engine: Optional[WorkflowEngine] = None
) -> Dict[str, Any]:
    # Tool implementation using workflow_engine
```

### Workflow Engine Integration

The FastMCP implementation is tightly integrated with Harmonia's workflow engine, providing direct access to:
- State management for workflows and executions
- Component registry for integration
- Template manager for template operations
- Execution monitoring and control

### Error Handling

All tool implementations include comprehensive error handling to ensure robustness and provide meaningful error messages. The tools gracefully handle cases where the workflow engine is not initialized or when requested resources are not found.

## Conclusion

The FastMCP integration in Harmonia provides comprehensive workflow orchestration capabilities through a modern, decorator-based approach to MCP. The integration covers the full workflow lifecycle from definition creation to execution monitoring, while also providing template management and component integration features. This makes Harmonia a powerful orchestration hub within the Tekton ecosystem.