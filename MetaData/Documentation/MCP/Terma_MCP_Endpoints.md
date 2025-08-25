# Terma MCP API Endpoints

**Component**: Terma  
**Port**: 8004  
**Base URL**: `http://localhost:8004/api/mcp/v2`

## Overview

Terma provides MCP (Model Context Protocol) endpoints for terminal management, including the ability to launch aish-enabled terminals programmatically.

## Endpoints

### Launch Terminal

**Endpoint**: `POST /tools/launch_terminal`

Launches a new terminal with aish integration.

**Request Body**:
```json
{
    "name": "Terminal name",           // Optional, defaults to "aish Terminal"
    "working_dir": "/path/to/dir",     // Optional, defaults to user's home
    "purpose": "Development task",      // Optional, CI context
    "template": "ai_workspace"          // Optional, terminal template
}
```

**Available Templates**:
- `default` - Basic aish terminal
- `development` - Development environment
- `ai_workspace` - AI-assisted development
- `data_science` - Data science configuration

**Response**:
```json
{
    "success": true,
    "pid": 12345,
    "terminal_app": "Terminal.app",
    "working_directory": "/Users/username",
    "aish_enabled": true,
    "message": "Successfully launched aish-enabled terminal (PID: 12345)"
}
```

**Example**:
```bash
curl -X POST http://localhost:8004/api/mcp/v2/tools/launch_terminal \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CI Development Terminal",
    "template": "ai_workspace",
    "purpose": "Working on authentication feature"
  }'
```

### Terminal Status

**Endpoint**: `GET /terminal-status`

Get overall Terma system status.

**Response**:
```json
{
    "success": true,
    "status": "operational",
    "service": "terma-terminal-manager",
    "capabilities": ["terminal_management", "llm_integration", "system_integration"],
    "active_sessions": 3,
    "mcp_tools": 16,
    "terminal_engine_status": "ready",
    "websocket_status": "active",
    "llm_adapter_connected": true,
    "message": "Terma terminal management and integration engine is operational"
}
```

### Terminal Health

**Endpoint**: `GET /terminal-health`

Get comprehensive health information about the terminal system.

**Response**:
```json
{
    "success": true,
    "health": {
        "timestamp": "2025-07-02T13:00:00",
        "overall_health": "healthy",
        "components": {
            "session_manager": {
                "status": "active",
                "active_sessions": 5,
                "memory_usage_mb": 120
            },
            "websocket_server": {
                "status": "active",
                "active_connections": 5
            }
        },
        "performance_metrics": {
            "cpu_usage_percent": 5.2,
            "memory_usage_percent": 25.0
        }
    },
    "recommendations": [
        "Regular health monitoring is recommended"
    ]
}
```

### Bulk Session Actions

**Endpoint**: `POST /terminal-session-bulk-action`

Perform bulk actions on multiple terminal sessions.

**Request Body**:
```json
{
    "action": "monitor",              // Required: backup|restart|optimize|monitor|cleanup
    "session_filters": {},            // Optional: filters for selecting sessions
    "parameters": {}                  // Optional: action-specific parameters
}
```

**Response**:
```json
{
    "success": true,
    "bulk_action": {
        "bulk_action_id": "bulk-1234",
        "action": "monitor",
        "timestamp": "2025-07-02T13:00:00",
        "sessions_targeted": 3,
        "sessions_processed": 3,
        "results": [...]
    },
    "message": "Bulk action 'monitor' completed on 3 sessions"
}
```

### Execute Terminal Workflow

**Endpoint**: `POST /execute-terminal-workflow`

Execute predefined terminal management workflows.

**Request Body**:
```json
{
    "workflow_name": "terminal_session_optimization",
    "parameters": {
        "target_sessions": "all"
    }
}
```

**Available Workflows**:
- `terminal_session_optimization` - Optimize terminal performance
- `llm_assisted_troubleshooting` - AI-assisted debugging
- `multi_component_terminal_integration` - Component integration setup
- `terminal_performance_analysis` - Performance analysis

## Environment Variables

Terminals launched via MCP will have these environment variables set:

- `TEKTON_ENABLED="true"` - Indicates Tekton platform
- `AISH_ACTIVE="1"` - Indicates aish is available
- `TEKTON_TERMINAL_PURPOSE` - Set from `purpose` parameter
- `RHETOR_ENDPOINT` - Rhetor service endpoint

## Error Responses

All endpoints return standard error responses:

```json
{
    "detail": "Error message",
    "status_code": 400
}
```

Common status codes:
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `500` - Internal Server Error

## Integration with aish

All terminals launched through these endpoints automatically have aish integration enabled, providing:

- CI command routing via `aish <ai-name> "message"`
- Pipeline support for CI chaining
- Team chat capabilities
- Transparent shell enhancement

## Example: Launch and Monitor

```bash
# Launch a terminal
RESPONSE=$(curl -s -X POST http://localhost:8004/api/mcp/v2/tools/launch_terminal \
  -H "Content-Type: application/json" \
  -d '{"name": "Dev Terminal", "template": "development"}')

# Extract PID
PID=$(echo $RESPONSE | jq -r '.pid')

# Check status
curl http://localhost:8004/api/mcp/v2/terminal-status

# Monitor sessions
curl -X POST http://localhost:8004/api/mcp/v2/terminal-session-bulk-action \
  -H "Content-Type: application/json" \
  -d '{"action": "monitor", "session_filters": {}}'
```