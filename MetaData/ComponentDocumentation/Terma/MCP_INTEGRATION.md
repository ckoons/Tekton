# Terma FastMCP Integration

This document describes Terma's comprehensive FastMCP (Model Context Protocol) integration, providing terminal management, LLM integration, and system integration capabilities.

## Overview

Terma implements FastMCP to provide external systems with programmatic access to terminal management functionality, AI-powered terminal assistance, and system integration capabilities. The implementation includes 16 specialized tools organized into 3 main capability areas.

## Architecture

### MCP Server Configuration

- **Service Name**: `terma`
- **Version**: `0.1.0`
- **Base URL**: `http://localhost:8765/api/mcp/v2`
- **Protocol**: FastMCP over HTTP

### Capabilities

Terma provides three main MCP capabilities:

1. **Terminal Management** - Create, manage, and monitor terminal sessions
2. **LLM Integration** - AI-powered terminal assistance and analysis  
3. **System Integration** - Integration with Tekton ecosystem components

## Capabilities and Tools

### 1. Terminal Management Capability

**Capability Name**: `terminal_management`  
**Description**: Create, manage, and monitor terminal sessions and commands

#### Tools

##### `create_terminal_session`
Create and configure a new terminal session.

**Parameters**:
- `shell_command` (optional): Shell command to execute (defaults to user shell)
- `environment` (optional): Environment variables for the session
- `working_directory` (optional): Initial working directory  
- `session_name` (optional): Optional name for the session

**Example**:
```json
{
  "tool_name": "create_terminal_session",
  "arguments": {
    "shell_command": "/bin/bash",
    "environment": {
      "NODE_ENV": "development"
    },
    "working_directory": "/home/user/project",
    "session_name": "development-session"
  }
}
```

**Response**:
```json
{
  "success": true,
  "session": {
    "session_id": "abc12345",
    "session_name": "development-session",
    "shell_command": "/bin/bash",
    "working_directory": "/home/user/project",
    "created_at": "2024-01-15T10:30:00Z",
    "pid": 1234,
    "status": "active",
    "pty": {
      "rows": 24,
      "cols": 80,
      "term": "xterm-256color"
    }
  },
  "websocket_url": "ws://localhost:8765/ws/abc12345",
  "api_endpoints": {
    "write": "/api/sessions/abc12345/write",
    "read": "/api/sessions/abc12345/read",
    "info": "/api/sessions/abc12345",
    "close": "/api/sessions/abc12345"
  },
  "message": "Terminal session 'development-session' created successfully"
}
```

##### `manage_session_lifecycle`
Manage terminal session lifecycle and state transitions.

**Parameters**:
- `session_id`: ID of the session to manage
- `action`: Lifecycle action ("start", "stop", "pause", "resume", "restart", "kill")
- `parameters` (optional): Additional parameters for the action

##### `execute_terminal_commands` 
Execute commands in a specific terminal session.

**Parameters**:
- `session_id`: ID of the target session
- `commands`: List of commands to execute
- `execution_mode`: How to execute multiple commands ("sequential", "parallel", "interactive")
- `timeout_seconds`: Maximum execution time (default: 30)

##### `monitor_session_performance`
Monitor terminal session performance and resource usage.

**Parameters**:
- `session_ids` (optional): List of session IDs to monitor
- `metrics` (optional): Specific metrics to collect
- `duration_minutes`: Monitoring duration (default: 5)

##### `configure_terminal_settings`
Configure terminal settings, shell preferences, and environment.

**Parameters**:
- `session_id`: ID of the session to configure
- `settings`: Dictionary of settings to apply
- `scope`: Scope of settings ("session", "user", "global")

##### `backup_session_state`
Backup and restore terminal session state and history.

**Parameters**:
- `session_ids` (optional): List of session IDs to backup
- `backup_type`: Type of backup ("full", "incremental", "settings_only", "history_only")
- `include_history`: Whether to include command history
- `compression`: Whether to compress backup data

### 2. LLM Integration Capability

**Capability Name**: `llm_integration`  
**Description**: Provide AI-powered assistance and analysis for terminal operations

#### Tools

##### `provide_command_assistance`
Provide AI-powered assistance for terminal commands.

**Parameters**:
- `command_query`: User's query about a command
- `context` (optional): Current terminal context
- `shell_type`: Type of shell being used (default: "bash")
- `assistance_level`: Level of assistance detail ("basic", "detailed", "expert")

**Example**:
```json
{
  "tool_name": "provide_command_assistance", 
  "arguments": {
    "command_query": "How do I find all Python files modified in the last week?",
    "shell_type": "bash",
    "assistance_level": "detailed"
  }
}
```

**Response**:
```json
{
  "success": true,
  "assistance": {
    "query": "How do I find all Python files modified in the last week?",
    "shell_type": "bash",
    "suggestion": "find . -name '*.py' -mtime -7",
    "explanation": "This command searches for Python files modified within the last 7 days",
    "examples": [
      "find /home/user -name '*.py' -mtime -7",
      "find . -name '*.py' -mtime -7 -exec ls -la {} \\;"
    ],
    "related_commands": ["locate", "grep", "mlocate"],
    "safety_notes": ["Always verify file paths", "Use -maxdepth to limit search scope"]
  },
  "confidence_score": 0.95,
  "message": "Command assistance provided successfully"
}
```

##### `analyze_terminal_output`
Analyze and interpret terminal output and error messages.

##### `suggest_command_improvements`
Suggest command improvements and alternatives.

##### `detect_terminal_issues`
Detect and diagnose terminal issues and problems.

##### `generate_terminal_workflows`
Generate automated terminal command workflows.

##### `optimize_llm_interactions`
Optimize LLM interactions within terminal context.

### 3. System Integration Capability

**Capability Name**: `system_integration`  
**Description**: Integrate terminal sessions with Tekton ecosystem and system components

#### Tools

##### `integrate_with_tekton_components`
Integrate terminal sessions with other Tekton components.

**Parameters**:
- `component_names`: Names of components to integrate with
- `integration_type`: Type of integration ("unidirectional", "bidirectional", "event_driven", "api_based")
- `configuration` (optional): Integration configuration parameters

##### `synchronize_session_data`
Synchronize terminal data and state across components.

##### `manage_terminal_security`
Manage terminal security, permissions, and access control.

##### `track_terminal_metrics`
Track terminal usage metrics and performance analytics.

## Predefined Workflows

Terma provides 4 predefined workflows that combine multiple tools for common use cases:

### 1. Terminal Session Optimization
**Workflow Name**: `terminal_session_optimization`

Comprehensive terminal session setup and optimization workflow.

**Parameters**:
- `session_id`: Target session ID
- `optimization_level`: "conservative", "moderate", "aggressive"

**Usage**:
```bash
curl -X POST http://localhost:8765/api/mcp/v2/execute-terminal-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "terminal_session_optimization",
    "parameters": {
      "session_id": "abc12345",
      "optimization_level": "aggressive"
    }
  }'
```

### 2. LLM Assisted Troubleshooting
**Workflow Name**: `llm_assisted_troubleshooting`

AI-powered terminal troubleshooting workflow.

### 3. Multi-Component Terminal Integration
**Workflow Name**: `multi_component_terminal_integration`

Integrate terminal with multiple Tekton components.

### 4. Terminal Performance Analysis
**Workflow Name**: `terminal_performance_analysis`

Comprehensive terminal performance analysis and improvement.

## API Endpoints

### Standard MCP Endpoints

- `GET /api/mcp/v2/health` - MCP server health check
- `GET /api/mcp/v2/capabilities` - List all capabilities
- `GET /api/mcp/v2/tools` - List all available tools
- `POST /api/mcp/v2/tools/execute` - Execute a specific tool

### Terma-Specific Endpoints

- `GET /api/mcp/v2/terminal-status` - Get terminal system status
- `GET /api/mcp/v2/terminal-health` - Get comprehensive health information
- `POST /api/mcp/v2/execute-terminal-workflow` - Execute predefined workflows
- `POST /api/mcp/v2/terminal-session-bulk-action` - Perform bulk actions on sessions

## Usage Examples

### Python Client Example

```python
import aiohttp
import asyncio

async def test_terma_mcp():
    async with aiohttp.ClientSession() as session:
        # Create a terminal session
        create_payload = {
            "tool_name": "create_terminal_session",
            "arguments": {
                "shell_command": "/bin/bash",
                "session_name": "test-session"
            }
        }
        
        async with session.post(
            "http://localhost:8765/api/mcp/v2/tools/execute",
            json=create_payload
        ) as response:
            result = await response.json()
            session_id = result["session"]["session_id"]
            print(f"Created session: {session_id}")
        
        # Get command assistance
        assistance_payload = {
            "tool_name": "provide_command_assistance", 
            "arguments": {
                "command_query": "How to list files recursively?",
                "shell_type": "bash",
                "assistance_level": "detailed"
            }
        }
        
        async with session.post(
            "http://localhost:8765/api/mcp/v2/tools/execute",
            json=assistance_payload
        ) as response:
            result = await response.json()
            print(f"Command suggestion: {result['assistance']['suggestion']}")

# Run the example
asyncio.run(test_terma_mcp())
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8765/api/mcp/v2';

async function testTermaMCP() {
    try {
        // Execute terminal commands
        const executePayload = {
            tool_name: 'execute_terminal_commands',
            arguments: {
                session_id: 'test-session-1',
                commands: ['ls -la', 'pwd'],
                execution_mode: 'sequential'
            }
        };
        
        const response = await axios.post(`${BASE_URL}/tools/execute`, executePayload);
        console.log('Command execution results:', response.data);
        
        // Analyze terminal output
        const analysisPayload = {
            tool_name: 'analyze_terminal_output',
            arguments: {
                output_text: 'Permission denied: cannot access file.txt',
                analysis_type: 'comprehensive'
            }
        };
        
        const analysisResponse = await axios.post(`${BASE_URL}/tools/execute`, analysisPayload);
        console.log('Output analysis:', analysisResponse.data);
        
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

testTermaMCP();
```

## Integration with Tekton Components

### Hermes Integration
Terma integrates with Hermes for:
- Service discovery and message passing
- Event-driven terminal management
- Cross-component communication

### Hephaestus Integration  
Integration with Hephaestus provides:
- Rich terminal UI components
- WebSocket-based real-time communication
- Visual terminal session management

### Engram Integration
Integration with Engram enables:
- Persistent terminal session memory
- Command history storage and retrieval
- Context-aware terminal assistance

### LLM Adapter Integration
Connection to the LLM Adapter provides:
- Multi-provider LLM access
- AI-powered terminal assistance
- Intelligent command analysis and suggestions

## Testing

### Running Tests

Execute the comprehensive test suite:

```bash
# Bash test script
./examples/run_fastmcp_test.sh

# Python async test client  
python3 examples/test_fastmcp.py

# Save test results to JSON
python3 examples/test_fastmcp.py --save-results
```

### Test Coverage

The test suite covers:
- All 16 MCP tools
- 4 predefined workflows  
- Additional Terma-specific endpoints
- Error handling and edge cases
- Performance and response time validation

## Error Handling

### Common Error Responses

```json
{
  "success": false,
  "error": "Session not found: invalid-session-id"
}
```

```json
{
  "success": false,
  "error": "Invalid action: invalid_action. Valid actions: [start, stop, pause, resume, restart, kill]"
}
```

### HTTP Status Codes

- `200 OK` - Successful tool execution
- `400 Bad Request` - Invalid parameters or tool name
- `404 Not Found` - Tool or resource not found
- `500 Internal Server Error` - Server-side execution error

## Configuration

### Environment Variables

- `TERMA_PORT` - Port for Terma server (default: 8765)
- `TERMA_HOST` - Host binding (default: localhost)
- `MCP_DEBUG` - Enable MCP debug logging
- `REGISTER_WITH_HERMES` - Auto-register with Hermes service

### MCP Server Settings

```python
# terma/api/fastmcp_endpoints.py
fastmcp_server = FastMCPServer(
    name="terma",
    version="0.1.0", 
    description="Terma Terminal Management, LLM Integration, and System Integration MCP Server"
)
```

## Performance Considerations

- **Tool Execution**: Most tools complete within 100-500ms
- **Workflow Execution**: Workflows may take 1-10 seconds depending on complexity
- **WebSocket Communication**: Real-time terminal interaction with <50ms latency
- **Concurrent Sessions**: Supports multiple concurrent terminal sessions
- **Resource Usage**: Optimized for low CPU and memory footprint

## Security

### Access Control
- Optional authentication for tool execution
- Session-based access control for terminal operations
- Configurable command filtering and restrictions

### Audit Logging
- Comprehensive audit logging for all terminal operations
- Security event monitoring and alerting
- Compliance reporting and data retention policies

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure Terma server is running on the correct port
   - Check firewall settings and network connectivity

2. **Tool Execution Failures**
   - Verify tool parameters match the expected schema
   - Check server logs for detailed error information

3. **Session Management Issues**
   - Ensure session IDs are valid and active
   - Monitor session lifecycle and cleanup processes

### Debug Mode

Enable debug logging:
```bash
export MCP_DEBUG=true
python -m terma.cli.main
```

## Version History

- **v0.1.0** - Initial FastMCP integration
  - 16 MCP tools across 3 capabilities
  - 4 predefined workflows
  - Comprehensive test suite
  - Full Tekton ecosystem integration

## Future Enhancements

- Advanced security policies and RBAC
- Real-time terminal collaboration features
- Enhanced LLM model integration
- Performance optimization and caching
- Extended workflow automation capabilities