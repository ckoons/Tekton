# Metis MCP Integration

This document describes the FastMCP (Model Context Protocol) integration for Metis, the task management system in the Tekton ecosystem.

## Overview

Metis integrates with FastMCP to provide external systems (like Claude Code and other CI tools) with programmatic access to task management capabilities. This integration allows CI systems to create, read, update, and delete tasks, manage dependencies, analyze complexity, and execute workflows.

## Architecture

The MCP integration follows the established Tekton FastMCP pattern:

- **FastMCP Server**: Integrated into the Metis API server on startup
- **Tool Definitions**: Decorator-based tool definitions using `@mcp_tool`
- **Capability Organization**: Tools grouped into logical capabilities
- **Endpoint Integration**: Standard MCP endpoints under `/api/mcp/v2`

## Capabilities

### 1. Task Management (`task_management`)

Core CRUD operations for task management:

- **create_task**: Create new tasks with full metadata
- **get_task**: Retrieve task details by ID
- **update_task**: Update existing task properties
- **delete_task**: Remove tasks from the system
- **list_tasks**: Query tasks with filtering and pagination
- **add_subtask**: Add subtasks to existing tasks
- **update_subtask**: Modify subtask properties

### 2. Dependency Management (`dependency_management`)

Task relationship and dependency management:

- **create_dependency**: Create dependencies between tasks
- **get_task_dependencies**: Retrieve all dependencies for a task
- **remove_dependency**: Delete dependency relationships

### 3. Task Analytics (`task_analytics`)

Analysis and reporting on task data:

- **analyze_task_complexity**: Score task complexity based on factors
- **get_task_statistics**: Retrieve system-wide task metrics

### 4. Telos Integration (`telos_integration`)

Integration with the Telos requirements management system:

- **import_requirement_as_task**: Convert Telos requirements to tasks
- **link_task_to_requirement**: Create traceability links

## Tool Reference

### Task Management Tools

#### create_task

Creates a new task in the Metis system.

**Parameters:**
- `title` (string, required): Task title
- `description` (string, required): Detailed description
- `priority` (string, optional): Priority level (low, medium, high, urgent)
- `status` (string, optional): Task status (pending, in_progress, completed, cancelled)
- `assignee` (string, optional): Person assigned to the task
- `due_date` (string, optional): Due date in ISO format
- `tags` (list[string], optional): Tags for categorization
- `details` (string, optional): Implementation details
- `test_strategy` (string, optional): Testing approach

**Returns:**
- `success` (boolean): Operation success status
- `task` (object): Created task details
- `message` (string): Operation result message

**Example:**
```json
{
  "tool_name": "create_task",
  "arguments": {
    "title": "Implement user authentication",
    "description": "Add login and registration functionality",
    "priority": "high",
    "status": "pending",
    "assignee": "dev_team",
    "tags": ["authentication", "security"],
    "details": "Use JWT tokens for session management",
    "test_strategy": "Unit tests for auth service, integration tests for login flow"
  }
}
```

#### get_task

Retrieves details of a specific task.

**Parameters:**
- `task_id` (string, required): Unique task identifier

**Returns:**
- `success` (boolean): Operation success status
- `task` (object): Task details
- `message` (string): Operation result message

#### update_task

Updates an existing task's properties.

**Parameters:**
- `task_id` (string, required): Task ID to update
- Additional parameters: Any combination of create_task parameters

**Returns:**
- `success` (boolean): Operation success status
- `task` (object): Updated task details
- `message` (string): Operation result message

#### list_tasks

Retrieves a list of tasks with optional filtering.

**Parameters:**
- `status` (string, optional): Filter by status
- `priority` (string, optional): Filter by priority
- `assignee` (string, optional): Filter by assignee
- `tags` (list[string], optional): Filter by tags
- `limit` (integer, optional): Maximum results (default: 50)
- `offset` (integer, optional): Results offset (default: 0)

**Returns:**
- `success` (boolean): Operation success status
- `tasks` (list): List of matching tasks
- `count` (integer): Number of tasks returned
- `pagination` (object): Pagination information

### Dependency Management Tools

#### create_dependency

Creates a dependency relationship between two tasks.

**Parameters:**
- `source_task_id` (string, required): Source task ID
- `target_task_id` (string, required): Target task ID  
- `dependency_type` (string, optional): Type (depends_on, blocks, related_to)
- `description` (string, optional): Dependency description

**Returns:**
- `success` (boolean): Operation success status
- `dependency` (object): Created dependency details
- `message` (string): Operation result message

### Analytics Tools

#### analyze_task_complexity

Analyzes and scores task complexity.

**Parameters:**
- `task_id` (string, required): Task to analyze
- `factors` (object, optional): Custom complexity factors

**Returns:**
- `success` (boolean): Operation success status
- `complexity` (object): Complexity analysis results
- `message` (string): Operation result message

**Example:**
```json
{
  "tool_name": "analyze_task_complexity",
  "arguments": {
    "task_id": "task-123",
    "factors": {
      "technical_difficulty": 8,
      "scope": 6,
      "uncertainty": 7
    }
  }
}
```

## Workflow Execution

The MCP integration supports predefined workflows that combine multiple operations:

### create_task_with_subtasks

Creates a main task with multiple subtasks in a single operation.

**Parameters:**
- `main_task` (object): Main task creation parameters
- `subtasks` (list): List of subtask definitions

### import_and_analyze_requirement

Imports a requirement from Telos and performs complexity analysis.

**Parameters:**
- `requirement_id` (string): Telos requirement ID
- `priority` (string): Task priority
- `assignee` (string, optional): Task assignee
- `complexity_factors` (object, optional): Custom complexity factors

### batch_update_tasks

Updates multiple tasks matching specified criteria.

**Parameters:**
- `filters` (object): Task filter criteria
- `updates` (object): Updates to apply

### analyze_project_complexity

Performs complexity analysis on all tasks in a project.

**Parameters:**
- `filters` (object): Project task filters

## API Endpoints

### Standard MCP Endpoints

- `GET /api/mcp/v2/health` - MCP server health check
- `GET /api/mcp/v2/capabilities` - List available capabilities
- `GET /api/mcp/v2/tools` - List available tools
- `POST /api/mcp/v2/process` - Execute MCP tools

### Metis-Specific Endpoints

- `GET /api/mcp/v2/task-status` - Get task management status
- `POST /api/mcp/v2/execute-workflow` - Execute predefined workflows

## Usage Examples

### Basic Task Operations

```python
import aiohttp
import asyncio

async def create_and_manage_task():
    async with aiohttp.ClientSession() as session:
        # Create a task
        create_request = {
            "tool_name": "create_task",
            "arguments": {
                "title": "Fix critical bug",
                "description": "Database connection timeout issue",
                "priority": "urgent",
                "assignee": "alice"
            }
        }
        
        async with session.post(
            "http://localhost:8011/api/mcp/v2/process",
            json=create_request
        ) as response:
            result = await response.json()
            task_id = result["result"]["task"]["id"]
        
        # Add a subtask
        subtask_request = {
            "tool_name": "add_subtask", 
            "arguments": {
                "task_id": task_id,
                "title": "Identify root cause",
                "description": "Debug the connection timeout"
            }
        }
        
        async with session.post(
            "http://localhost:8011/api/mcp/v2/process",
            json=subtask_request
        ) as response:
            result = await response.json()
            print("Subtask added:", result["result"]["message"])

asyncio.run(create_and_manage_task())
```

### Workflow Execution

```python
async def execute_workflow():
    async with aiohttp.ClientSession() as session:
        workflow_request = {
            "workflow_name": "create_task_with_subtasks",
            "parameters": {
                "main_task": {
                    "title": "Implement feature X",
                    "description": "Complete implementation of feature X",
                    "priority": "high"
                },
                "subtasks": [
                    {
                        "title": "Design phase",
                        "description": "Create design documents"
                    },
                    {
                        "title": "Implementation phase", 
                        "description": "Code the feature"
                    },
                    {
                        "title": "Testing phase",
                        "description": "Write and run tests"
                    }
                ]
            }
        }
        
        async with session.post(
            "http://localhost:8011/api/mcp/v2/execute-workflow",
            json=workflow_request
        ) as response:
            result = await response.json()
            print("Workflow executed:", result["message"])
            print("Main task ID:", result["result"]["main_task"]["id"])

asyncio.run(execute_workflow())
```

## Testing

The Metis MCP integration includes comprehensive testing:

### Run Tests

```bash
# Run the test suite
cd /path/to/Tekton/Metis
./examples/run_fastmcp_test.sh
```

### Test Coverage

The test suite covers:

- Health check and MCP status verification
- Capability and tool discovery
- All task management operations
- Dependency management
- Complexity analysis
- Task statistics
- Workflow execution
- Error handling and edge cases

### Manual Testing

You can also test individual tools using curl:

```bash
# Test task creation
curl -X POST "http://localhost:8011/api/mcp/v2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "create_task",
    "arguments": {
      "title": "Test Task",
      "description": "A test task created via MCP",
      "priority": "medium"
    }
  }'

# Test task listing
curl -X POST "http://localhost:8011/api/mcp/v2/process" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "list_tasks",
    "arguments": {
      "limit": 5
    }
  }'
```

## Integration with Other Tekton Components

### Telos Requirements Integration

Metis can import requirements from Telos and maintain traceability:

```python
# Import requirement as task
import_request = {
    "tool_name": "import_requirement_as_task",
    "arguments": {
        "requirement_id": "REQ-001",
        "priority": "high",
        "assignee": "dev_team"
    }
}

# Link existing task to requirement
link_request = {
    "tool_name": "link_task_to_requirement",
    "arguments": {
        "task_id": "task-123",
        "requirement_id": "REQ-002",
        "relationship_type": "implements"
    }
}
```

### Hermes Message Bus Integration

Metis automatically registers with the Hermes message bus for service discovery and can send task-related events.

### Prometheus Planning Integration

Task data from Metis can be used by Prometheus for project planning and timeline estimation.

## Error Handling

All MCP tools include comprehensive error handling:

- **Tool Errors**: Specific error messages for tool execution failures
- **Validation Errors**: Input parameter validation with descriptive messages
- **Service Errors**: Graceful handling of service unavailability
- **Dependency Errors**: Clear error messages for dependency-related issues

Example error response:
```json
{
  "success": false,
  "error": "Task with ID 'invalid-id' not found",
  "tool_name": "get_task"
}
```

## Development

### Adding New Tools

To add new MCP tools to Metis:

1. Define the tool function in `metis/core/mcp/tools.py`
2. Add the `@mcp_tool` decorator with appropriate metadata
3. Register the tool in the appropriate capability list
4. Add tests in `examples/test_fastmcp.py`
5. Update this documentation

### Capability Extensions

To add new capabilities:

1. Define the capability in `metis/core/mcp/capabilities.py`
2. Create tools that reference the capability
3. Register the capability in `fastmcp_endpoints.py`
4. Update documentation

## Troubleshooting

### Common Issues

1. **MCP Server Not Starting**
   - Check that tekton-core is properly installed
   - Verify no port conflicts
   - Check server logs for initialization errors

2. **Tool Execution Failures**
   - Ensure Metis service is running
   - Verify task manager is properly initialized
   - Check for missing dependencies

3. **Import Errors**
   - Install missing dependencies: `pip install -e .`
   - Ensure tekton-core is in the Python path

### Debugging

Enable debug logging for detailed MCP operation logs:

```python
import logging
logging.getLogger("tekton.mcp").setLevel(logging.DEBUG)
```

## Security Considerations

- MCP endpoints are currently unauthenticated - implement authentication for production use
- Input validation is performed on all tool parameters
- SQL injection protection through Pydantic models
- Rate limiting should be implemented for production deployments

## Performance

- Tool execution is asynchronous for optimal performance
- Database operations use efficient queries with proper indexing
- Large result sets support pagination
- Batch operations available for bulk updates

## Conclusion

The Metis MCP integration provides a comprehensive and flexible interface for task management operations, enabling seamless integration with CI tools and external systems while maintaining the robustness and reliability of the core task management functionality.

For more information, see:
- [Metis API Reference](docs/api_reference.md)
- [Tekton FastMCP Documentation](../tekton-core/tekton/mcp/fastmcp/README.md)
- [MCP Unified Integration Sprint Progress](../MetaData/DevelopmentSprints/MCP_Unified_Integration_Sprint/ProgressSummary.md)