# aish MCP Server - Full Capabilities Documentation

## Overview

The aish MCP (Model Context Protocol) server now provides comprehensive access to ALL CI (Companion Intelligence) functionality in Tekton. This includes CI tools management, context state management, detailed CI information, and registry operations.

## Complete Endpoint Reference

### Base URL
```
http://localhost:8118/api/mcp/v2
```

### 1. CI Tools Management

#### GET /tools/ci-tools
List all available CI tools and their status.

**Response:**
```json
{
  "tools": [
    {
      "name": "claude-code",
      "description": "Claude AI coding assistant",
      "type": "claude-code",
      "port": 8400,
      "status": "running",
      "executable": "claude-code",
      "capabilities": ["code_generation", "debugging"],
      "defined_by": "system"
    }
  ]
}
```

#### POST /tools/ci-tools/launch
Launch a CI tool with optional session and instance.

**Request:**
```json
{
  "tool_name": "claude-code",
  "session_id": "dev-session",
  "instance_name": "reviewer"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully launched claude-code",
  "port": 8400
}
```

#### POST /tools/ci-tools/terminate
Terminate a running CI tool or instance.

**Request:**
```json
{
  "tool_name": "claude-code"
}
```

#### GET /tools/ci-tools/status/{tool_name}
Get detailed status for a specific CI tool.

**Response:**
```json
{
  "name": "claude-code",
  "running": true,
  "pid": 12345,
  "uptime": 3600.5,
  "config": {
    "port": 8400,
    "executable": "claude-code"
  }
}
```

#### GET /tools/ci-tools/instances
List all running CI tool instances.

**Response:**
```json
{
  "instances": [
    {
      "name": "reviewer",
      "tool_type": "claude-code",
      "pid": 12345,
      "session": "dev-session",
      "uptime": 3600.5,
      "running": true
    }
  ]
}
```

#### POST /tools/ci-tools/define
Define a new CI tool dynamically.

**Request:**
```json
{
  "name": "gpt-coder",
  "type": "generic",
  "executable": "/usr/local/bin/gpt",
  "options": {
    "description": "GPT-4 coding assistant",
    "capabilities": ["code_generation", "analysis"],
    "port": "auto",
    "health_check": "ping",
    "launch_args": ["--mode", "stdio"],
    "environment": {
      "GPT_MODEL": "gpt-4"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully defined tool gpt-coder",
  "port": 8405
}
```

#### DELETE /tools/ci-tools/{tool_name}
Remove a user-defined CI tool.

#### GET /tools/ci-tools/capabilities/{tool_name}
Get capabilities for a specific CI tool.

**Response:**
```json
{
  "name": "claude-code",
  "capabilities": {
    "code_generation": true,
    "debugging": true,
    "refactoring": true
  },
  "executable": "claude-code",
  "health_check": "version",
  "port": 8400,
  "base_type": "claude-code"
}
```

### 2. Context State Management

#### GET /tools/context-state/{ci_name}
Get context state for a specific CI.

**Response:**
```json
{
  "ci_name": "numa",
  "last_output": "Previous response from numa",
  "staged_prompt": [
    {"role": "system", "content": "Staged context"}
  ],
  "next_prompt": [
    {"role": "user", "content": "Next prompt"}
  ]
}
```

#### POST /tools/context-state/{ci_name}
Update context state for a specific CI.

**Request:**
```json
{
  "last_output": "New output from CI",
  "staged_prompt": [
    {"role": "system", "content": "New staged prompt"}
  ],
  "next_prompt": [
    {"role": "user", "content": "New next prompt"}
  ]
}
```

#### GET /tools/context-states
Get context states for all CIs.

**Response:**
```json
{
  "context_states": {
    "numa": {
      "last_output": "Output from numa",
      "next_prompt": [{"role": "user", "content": "Next"}]
    },
    "apollo": {
      "last_output": "Output from apollo",
      "staged_prompt": [{"role": "system", "content": "Staged"}]
    }
  }
}
```

#### POST /tools/context-state/{ci_name}/promote-staged
Move staged context prompt to next prompt.

**Response:**
```json
{
  "success": true,
  "message": "Promoted staged context to next prompt"
}
```

### 3. Detailed CI Information

#### GET /tools/ci/{ci_name}
Get full details for a specific CI.

**Response:**
```json
{
  "name": "numa",
  "type": "greek",
  "endpoint": "http://localhost:8316",
  "description": "NUMA - Intelligent Systems Integration",
  "message_format": "rhetor_socket",
  "port": 8316,
  "message_endpoint": "/api/message"
}
```

#### GET /tools/ci-types
Get available CI types.

**Response:**
```json
{
  "types": ["greek", "terminal", "project", "tool"]
}
```

#### GET /tools/cis/type/{ci_type}
Get all CIs of a specific type.

**Response:**
```json
{
  "cis": [
    {
      "name": "numa",
      "type": "greek",
      "endpoint": "http://localhost:8316",
      "description": "NUMA - Intelligent Systems Integration"
    },
    {
      "name": "apollo",
      "type": "greek",
      "endpoint": "http://localhost:8317",
      "description": "Code Development"
    }
  ]
}
```

#### GET /tools/ci/{ci_name}/exists
Check if a CI exists.

**Response:**
```json
{
  "exists": true
}
```

### 4. Registry Management

#### POST /tools/registry/reload
Force reload of CI registry to discover new terminals, projects, and tools.

**Response:**
```json
{
  "success": true,
  "message": "Registry reloaded. CIs: 15 → 18",
  "counts": {
    "total": 18,
    "before": 15,
    "by_type": {
      "greek": 12,
      "terminal": 3,
      "project": 2,
      "tool": 1
    }
  }
}
```

#### GET /tools/registry/status
Get CI registry status and statistics.

**Response:**
```json
{
  "status": "active",
  "counts": {
    "total": 18,
    "by_type": {
      "greek": 12,
      "terminal": 3,
      "project": 2,
      "tool": 1
    }
  },
  "registry_file": "/path/to/.tekton/aish/registry.json",
  "file_exists": true
}
```

#### POST /tools/registry/save
Force save of registry context state to disk.

**Response:**
```json
{
  "success": true,
  "message": "Registry state saved successfully"
}
```

## Usage Examples

### Example 1: Define and Launch a New Tool

```bash
# Define a new tool
curl -X POST http://localhost:8118/api/mcp/v2/tools/ci-tools/define \
  -H "Content-Type: application/json" \
  -d '{
    "name": "openai-assistant",
    "type": "generic",
    "executable": "/usr/local/bin/openai",
    "options": {
      "description": "OpenAI coding assistant",
      "capabilities": ["code_generation", "analysis"],
      "port": "auto"
    }
  }'

# Launch the tool
curl -X POST http://localhost:8118/api/mcp/v2/tools/ci-tools/launch \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "openai-assistant",
    "session_id": "dev-session"
  }'

# Send a message to it
curl -X POST http://localhost:8118/api/mcp/v2/tools/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "ai_name": "openai-assistant",
    "message": "Generate a Python function to parse JSON"
  }'
```

### Example 2: Manage Context State

```bash
# Update context for Apollo
curl -X POST http://localhost:8118/api/mcp/v2/tools/context-state/apollo \
  -H "Content-Type: application/json" \
  -d '{
    "last_output": "Analyzed code patterns",
    "staged_prompt": [
      {"role": "system", "content": "Focus on performance optimization"}
    ]
  }'

# Promote staged to next
curl -X POST http://localhost:8118/api/mcp/v2/tools/context-state/apollo/promote-staged

# Get all context states
curl http://localhost:8118/api/mcp/v2/tools/context-states
```

### Example 3: CI Discovery

```bash
# Get all CI types
curl http://localhost:8118/api/mcp/v2/tools/ci-types

# Get all tool-type CIs
curl http://localhost:8118/api/mcp/v2/tools/cis/type/tool

# Get details for a specific CI
curl http://localhost:8118/api/mcp/v2/tools/ci/claude-code

# Check if CI exists
curl http://localhost:8118/api/mcp/v2/tools/ci/my-tool/exists
```

## JavaScript/UI Integration

```javascript
// Complete AIChat interface with all capabilities
window.AIChat = {
  // Messaging
  sendMessage: async function(aiName, message, stream = false) {
    const response = await fetch(aishUrl("/api/mcp/v2/tools/send-message"), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ai_name: aiName, message, stream })
    });
    return response.json();
  },
  
  // CI Tools Management
  tools: {
    list: async function() {
      const response = await fetch(aishUrl("/api/mcp/v2/tools/ci-tools"));
      return response.json();
    },
    
    launch: async function(toolName, sessionId, instanceName) {
      const response = await fetch(aishUrl("/api/mcp/v2/tools/ci-tools/launch"), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          tool_name: toolName, 
          session_id: sessionId,
          instance_name: instanceName 
        })
      });
      return response.json();
    },
    
    terminate: async function(toolName) {
      const response = await fetch(aishUrl("/api/mcp/v2/tools/ci-tools/terminate"), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool_name: toolName })
      });
      return response.json();
    },
    
    define: async function(name, type, executable, options) {
      const response = await fetch(aishUrl("/api/mcp/v2/tools/ci-tools/define"), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, type, executable, options })
      });
      return response.json();
    }
  },
  
  // Context State Management
  context: {
    get: async function(ciName) {
      const response = await fetch(aishUrl(`/api/mcp/v2/tools/context-state/${ciName}`));
      return response.json();
    },
    
    update: async function(ciName, updates) {
      const response = await fetch(aishUrl(`/api/mcp/v2/tools/context-state/${ciName}`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      return response.json();
    },
    
    getAll: async function() {
      const response = await fetch(aishUrl("/api/mcp/v2/tools/context-states"));
      return response.json();
    }
  },
  
  // CI Discovery
  discovery: {
    getCI: async function(ciName) {
      const response = await fetch(aishUrl(`/api/mcp/v2/tools/ci/${ciName}`));
      return response.json();
    },
    
    getTypes: async function() {
      const response = await fetch(aishUrl("/api/mcp/v2/tools/ci-types"));
      return response.json();
    },
    
    getByType: async function(type) {
      const response = await fetch(aishUrl(`/api/mcp/v2/tools/cis/type/${type}`));
      return response.json();
    }
  },
  
  // Registry Management
  registry: {
    reload: async function() {
      const response = await fetch(aishUrl("/api/mcp/v2/tools/registry/reload"), {
        method: 'POST'
      });
      return response.json();
    },
    
    status: async function() {
      const response = await fetch(aishUrl("/api/mcp/v2/tools/registry/status"));
      return response.json();
    }
  }
};
```

## Benefits of Full MCP Integration

1. **Single API Surface**: All CI functionality accessible through one consistent API
2. **Tool Discovery**: External tools can discover all capabilities
3. **Complete Control**: Launch, manage, and terminate CI tools programmatically
4. **Context Awareness**: Apollo and Rhetor can manage context via MCP
5. **UI Integration**: Web UIs have full access to all CI functionality
6. **Federation Ready**: Remote Tekton instances can manage tools via MCP

## Performance Characteristics

- **Fast endpoints** (<50ms): CI info, types, exists, registry status
- **Medium endpoints** (<100ms): List operations, context state reads
- **Slower endpoints** (<2s): Tool launch, registry reload

## Error Handling

All endpoints return appropriate HTTP status codes:
- **200**: Success
- **400**: Bad request (missing required parameters)
- **404**: Resource not found
- **500**: Internal server error

Error responses include detail:
```json
{
  "detail": "CI not found: unknown-ci"
}
```

## Summary

The aish MCP server now provides complete access to all CI functionality in Tekton, enabling:
- Full CI tools lifecycle management
- Context state management for Apollo-Rhetor coordination
- Comprehensive CI discovery and information
- Registry management and persistence
- Dynamic tool definition without code changes

This makes MCP the true "single source of truth" for all AI/CI operations in Tekton.