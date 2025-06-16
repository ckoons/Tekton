# Telos MCP Integration

This document describes the Model Context Protocol (MCP) integration for Telos, the requirements management and tracing system in the Tekton ecosystem.

## Overview

Telos implements FastMCP (Fast Model Context Protocol) to provide a standardized interface for requirements management, tracing, validation, and strategic planning operations. This integration allows external systems and AI models to interact with Telos's requirements management capabilities through a consistent, well-defined API.

## Architecture

### Integration Approach

Telos uses a **parallel implementation** approach for MCP integration:

- **Main API Server** (`/api/*`): Provides the full Telos REST API on port 8008
- **FastMCP Integration** (`/api/mcp/v2/*`): Integrated FastMCP endpoints within the main server
- **Separate FastMCP Server** (`run_fastmcp.sh`): Optional dedicated FastMCP server on port 8009

This approach ensures backward compatibility while providing modern FastMCP capabilities.

### FastMCP Implementation

The FastMCP integration includes:

1. **Tool Registration**: All tools are registered with the FastMCP registry using decorators
2. **Dependency Injection**: Core services (RequirementsManager, PrometheusConnector) are injected into tools
3. **Capability Grouping**: Tools are organized into logical capabilities
4. **Error Handling**: Comprehensive error handling with meaningful error messages
5. **Workflow Support**: Complex multi-step operations via workflow endpoints

## Capabilities and Tools

### Requirements Management Capability

The `requirements_management` capability provides comprehensive CRUD operations for projects and requirements.

#### Tools

1. **create_project**
   - Create a new requirements project
   - Parameters: `name`, `description` (optional), `metadata` (optional)
   - Returns: Project ID and creation details

2. **get_project**
   - Retrieve a project with its requirements and hierarchy
   - Parameters: `project_id`
   - Returns: Complete project details including requirement hierarchy

3. **list_projects**
   - List all requirements projects
   - Parameters: None
   - Returns: Array of projects with summary information

4. **create_requirement**
   - Create a new requirement in a project
   - Parameters: `project_id`, `title`, `description`, plus optional fields
   - Returns: Requirement ID and creation details

5. **get_requirement**
   - Retrieve a specific requirement
   - Parameters: `project_id`, `requirement_id`
   - Returns: Complete requirement details

6. **update_requirement**
   - Update a requirement with new information
   - Parameters: `project_id`, `requirement_id`, plus optional update fields
   - Returns: Update status and details

### Requirement Tracing Capability

The `requirement_tracing` capability manages bidirectional traces and dependencies between requirements.

#### Tools

1. **create_trace**
   - Create a trace between two requirements
   - Parameters: `project_id`, `source_id`, `target_id`, `trace_type`, `description` (optional)
   - Returns: Trace ID and creation details

2. **list_traces**
   - List all traces for a project
   - Parameters: `project_id`
   - Returns: Array of traces with details

### Requirement Validation Capability

The `requirement_validation` capability provides quality assurance and validation for requirements.

#### Tools

1. **validate_project**
   - Validate all requirements in a project against quality criteria
   - Parameters: `project_id`, validation flags (`check_completeness`, `check_verifiability`, `check_clarity`)
   - Returns: Validation results with detailed analysis and summary

### Prometheus Integration Capability

The `prometheus_integration` capability provides strategic planning and analysis through Prometheus integration.

#### Tools

1. **analyze_requirements**
   - Analyze requirements for planning readiness
   - Parameters: `project_id`
   - Returns: Analysis results from Prometheus

2. **create_plan**
   - Create a strategic plan for the project
   - Parameters: `project_id`
   - Returns: Plan creation results

## Workflows

Telos FastMCP provides several predefined workflows for complex operations:

### create_project_with_requirements

Creates a project and adds multiple requirements in a single operation.

**Parameters:**
```json
{
  "project": {
    "name": "Project Name",
    "description": "Project Description",
    "metadata": {}
  },
  "requirements": [
    {
      "title": "Requirement Title",
      "description": "Requirement Description",
      "requirement_type": "functional",
      "priority": "medium"
    }
  ]
}
```

### validate_and_analyze_project

Validates a project and analyzes it for planning readiness.

**Parameters:**
```json
{
  "project_id": "project-uuid",
  "check_completeness": true,
  "check_verifiability": true,
  "check_clarity": true
}
```

### bulk_requirement_update

Updates multiple requirements at once.

**Parameters:**
```json
{
  "project_id": "project-uuid",
  "updates": [
    {
      "requirement_id": "req-uuid",
      "updates": {
        "status": "in-progress",
        "priority": "high"
      }
    }
  ]
}
```

### trace_analysis

Analyzes requirement traces and dependency patterns.

**Parameters:**
```json
{
  "project_id": "project-uuid"
}
```

## API Endpoints

### Standard FastMCP Endpoints

- `GET /api/mcp/v2/capabilities` - List all capabilities
- `GET /api/mcp/v2/tools` - List all tools
- `POST /api/mcp/v2/process` - Execute tools
- `GET /api/mcp/v2/health` - Health check

### Custom Endpoints

- `POST /api/mcp/v2/workflow` - Execute predefined workflows

## Usage Examples

### Python Client Example

```python
from tekton.mcp.fastmcp.client import FastMCPClient

# Connect to Telos FastMCP
client = FastMCPClient("http://localhost:8008/api/mcp/v2")

# Create a project
project_result = await client.call_tool("create_project", {
    "name": "My Requirements Project",
    "description": "A test project for requirements management"
})

project_id = project_result["project_id"]

# Add a requirement
requirement_result = await client.call_tool("create_requirement", {
    "project_id": project_id,
    "title": "User Authentication",
    "description": "Users must be able to authenticate with username and password",
    "requirement_type": "functional",
    "priority": "high"
})

# Validate the project
validation_result = await client.call_tool("validate_project", {
    "project_id": project_id,
    "check_completeness": True,
    "check_verifiability": True,
    "check_clarity": True
})

print(f"Validation pass rate: {validation_result['summary']['pass_percentage']}%")
```

### Workflow Example

```python
# Create project with multiple requirements
workflow_result = await client.call_workflow("create_project_with_requirements", {
    "project": {
        "name": "E-commerce Platform",
        "description": "Requirements for new e-commerce platform"
    },
    "requirements": [
        {
            "title": "User Registration",
            "description": "Users must be able to register with email and password",
            "requirement_type": "functional",
            "priority": "high"
        },
        {
            "title": "Product Catalog",
            "description": "System must display product catalog with search",
            "requirement_type": "functional", 
            "priority": "high"
        },
        {
            "title": "Performance",
            "description": "System must respond within 2 seconds",
            "requirement_type": "non-functional",
            "priority": "medium"
        }
    ]
})
```

## Installation and Setup

### Dependencies

Add to your `requirements.txt`:
```
tekton-core>=0.1.0
```

### Running the Server

#### Option 1: Main API with FastMCP Integration (Recommended)

```bash
# Start Telos with integrated FastMCP
./run_telos.sh
```

FastMCP endpoints available at: `http://localhost:8008/api/mcp/v2`

#### Option 2: Separate FastMCP Server

```bash
# Start dedicated FastMCP server
./run_fastmcp.sh
```

FastMCP endpoints available at: `http://localhost:8009/api/mcp/v2`

### Configuration

Environment variables:
- `TELOS_STORAGE_DIR`: Directory for requirements storage (default: `./data/requirements`)
- `TELOS_LOG_LEVEL`: Logging level (default: `info`)
- `TELOS_PORT`: Port for main server (default: 8008)

## Testing

Run the comprehensive test suite:

```bash
# Test integrated FastMCP
./examples/run_fastmcp_test.sh

# Test with custom URL
./examples/run_fastmcp_test.sh --url http://localhost:8008

# Test with cleanup
./examples/run_fastmcp_test.sh --cleanup
```

The test suite validates:
- Server availability and health
- All capabilities and tools
- Requirements management operations
- Requirement tracing functionality
- Validation capabilities
- Prometheus integration (if available)
- Workflow operations
- Error handling

## Error Handling

All tools return consistent error responses:

```json
{
  "error": "Description of what went wrong"
}
```

Common error scenarios:
- **Requirements manager not available**: Core service initialization failed
- **Project not found**: Invalid project ID provided
- **Requirement not found**: Invalid requirement ID provided
- **Prometheus connector not available**: Prometheus integration not initialized

## Integration with Other Components

### Hermes Integration

Telos automatically registers with Hermes for service discovery:

```json
{
  "name": "telos",
  "type": "requirements_management",
  "port": 8008,
  "health_endpoint": "/health",
  "capabilities": ["requirements", "tracing", "validation", "planning"]
}
```

### Prometheus Integration

When available, Telos integrates with Prometheus for:
- Requirements analysis for planning
- Strategic plan creation
- Resource allocation planning

### Ergon Integration

Telos can import requirements from Ergon agents and export them for workflow planning.

## Performance Considerations

- **Dependency Injection**: Minimal overhead through async dependency resolution
- **Tool Registration**: One-time registration during startup
- **Caching**: Requirements and projects cached in memory
- **Batch Operations**: Workflows reduce API round-trips for complex operations

## Security

- **Input Validation**: All tool parameters validated using Pydantic models
- **Error Sanitization**: Internal errors sanitized before returning to clients
- **CORS Configuration**: Configurable for production environments
- **Dependency Isolation**: Tools receive only required dependencies

## Future Enhancements

Planned improvements:
1. **Real-time Updates**: WebSocket support for live requirement updates
2. **Advanced Validation**: Integration with external validation services
3. **Requirement Templates**: Predefined requirement patterns
4. **Export Formats**: Support for additional export formats (PDF, Excel)
5. **Collaboration Features**: Multi-user editing and commenting
6. **Integration APIs**: Direct integration with popular requirements tools

## Troubleshooting

### Common Issues

1. **FastMCP tools not registered**
   - Check tekton-core installation
   - Verify PYTHONPATH includes component directory
   - Check startup logs for initialization errors

2. **Prometheus integration failing**
   - Prometheus connector is optional
   - Check Prometheus service availability
   - Verify Hermes service registration

3. **Storage directory errors**
   - Ensure TELOS_STORAGE_DIR is writable
   - Check directory permissions
   - Verify disk space availability

### Debug Mode

Enable debug logging:
```bash
export TELOS_LOG_LEVEL=debug
./run_telos.sh
```

## Support

For issues related to Telos FastMCP integration:
1. Check server logs for detailed error messages
2. Run the test suite to identify specific failing operations
3. Verify all dependencies are correctly installed
4. Ensure proper environment configuration

## Conclusion

Telos FastMCP integration provides a robust, standardized interface for requirements management operations. The combination of comprehensive tools, workflow support, and flexible deployment options makes it suitable for both standalone use and integration with larger Tekton-based systems.

The parallel implementation approach ensures backward compatibility while enabling modern MCP capabilities, making Telos a powerful component in the Tekton ecosystem for requirements management and strategic planning.