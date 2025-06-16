# Ergon FastMCP Integration

This document describes the FastMCP integration in Ergon, including the implementation approach, available tools, and usage examples.

## Implementation Approach

The Ergon FastMCP integration follows the "parallel implementation" approach, where the FastMCP endpoints are added alongside the existing MCP implementation. This approach ensures backward compatibility while introducing the benefits of the decorator-based FastMCP approach.

## FastMCP Components

### 1. Dependencies

FastMCP is added as a dependency in both `requirements.txt` and `setup.py`:

```python
# In requirements.txt
tekton-llm-client>=1.0.0
tekton-core>=0.1.0  # Added for FastMCP support
jinja2>=3.1.2
```

### 2. MCP Module

The FastMCP implementation is organized into the following structure:

```
ergon/
  core/
    mcp/
      __init__.py  # Exports tools and utilities
      tools.py     # Tool definitions using FastMCP decorators
```

### 3. API Integration

FastMCP endpoints are added to the API under a new path prefix `/api/mcp/v2` to maintain backward compatibility with the existing MCP implementation.

```python
# In app.py
app.include_router(fastmcp_router, prefix="/api/mcp/v2")
```

The FastMCP endpoints provide standard MCP functionality:
- `/api/mcp/v2/health`
- `/api/mcp/v2/capabilities`
- `/api/mcp/v2/tools`
- `/api/mcp/v2/process`

## Available Tools

### Agent Management Tools

Ergon provides the following agent management tools:

1. `CreateAgent` - Create a new autonomous agent
2. `UpdateAgent` - Update an existing agent
3. `DeleteAgent` - Delete an existing agent
4. `GetAgent` - Get information about an agent
5. `ListAgents` - List all registered agents

These tools are defined with the `@mcp_capability("agent_management")` decorator.

### Workflow Management Tools

Ergon provides the following workflow management tools:

1. `CreateWorkflow` - Create a new workflow definition
2. `UpdateWorkflow` - Update an existing workflow definition
3. `ExecuteWorkflow` - Execute a workflow with input parameters
4. `GetWorkflowStatus` - Get status of a workflow execution

These tools are defined with the `@mcp_capability("workflow_management")` decorator.

### Task Management Tools

Ergon provides the following task management tools:

1. `CreateTask` - Create a new task for an agent
2. `AssignTask` - Assign a task to a specific agent
3. `UpdateTaskStatus` - Update the status of a task
4. `GetTask` - Get information about a task
5. `ListTasks` - List tasks with optional filtering

These tools are defined with the `@mcp_capability("task_management")` decorator.

## Usage Examples

### Using the FastMCP API directly

```bash
# Get available tools
curl http://localhost:8003/api/mcp/v2/tools

# Create an agent
curl -X POST http://localhost:8003/api/mcp/v2/process \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "CreateAgent",
    "parameters": {
      "agent_name": "Test Agent",
      "agent_description": "A test agent",
      "capabilities": {"processing": ["test"]}
    }
  }'
```

### Using the FastMCP client from Python

```python
from tekton.mcp.fastmcp import MCPClient

# Create a client
client = MCPClient(url="http://localhost:8003/api/mcp/v2")

# Get available tools
tools = await client.get_tools()

# Create an agent
result = await client.execute_tool(
    "CreateAgent",
    parameters={
        "agent_name": "Test Agent",
        "agent_description": "A test agent",
        "capabilities": {"processing": ["test"]}
    }
)
```

### Using Ergon tools directly

```python
from ergon.core.mcp import create_agent
from ergon.core.a2a_client import A2AClient

# Initialize A2A client for dependency injection
a2a_client = A2AClient(
    agent_id="my-client",
    agent_name="My Client"
)
await a2a_client.initialize()

# Create an agent
result = await create_agent(
    agent_name="Test Agent",
    agent_description="A test agent",
    capabilities={"processing": ["test"]},
    a2a_client=a2a_client
)
```

## Testing

The FastMCP implementation includes a test script that can be run to verify functionality:

```bash
./examples/run_fastmcp_test.sh
```

This script tests all the available tools and their functionality.

## Implementation Details

### Tool Registration

All tools are registered during startup using the `register_tools` function, which automatically registers all the tools with their corresponding decorators.

```python
# In fastmcp_endpoints.py
await register_tools(a2a_client)
```

### Dependency Injection

The FastMCP implementation uses dependency injection to provide the A2A client to tool handlers. This allows tools to have access to the required services without having to create them repeatedly.

```python
# In tools.py
async def create_agent(
    agent_name: str,
    # ...
    a2a_client: Optional[A2AClient] = None
) -> Dict[str, Any]:
    # Tool implementation using a2a_client
```

### Error Handling

All tool implementations include comprehensive error handling to ensure robustness and provide meaningful error messages.

## Conclusion

The FastMCP integration in Ergon provides a modern, decorator-based approach to MCP while maintaining backward compatibility with the existing implementation. The parallel approach allows for a gradual transition to FastMCP without disrupting existing functionality.