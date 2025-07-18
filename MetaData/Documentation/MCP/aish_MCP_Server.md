# aish MCP Server Documentation

## Overview

The aish MCP (Model Context Protocol) server provides a unified interface for all AI communication in Tekton. It runs on port 8118 and handles message routing, forwarding, and team coordination.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   UI Components │     │  External Tools │     │   Claude Code   │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                         │
         └───────────────────────┼─────────────────────────┘
                                 │
                          ┌──────▼──────┐
                          │  aish MCP   │
                          │ Port: 8118  │
                          └──────┬──────┘
                                 │
         ┌───────────────────────┼─────────────────────────┐
         │                       │                         │
    ┌────▼────┐           ┌──────▼──────┐          ┌──────▼──────┐
    │  numa   │           │   apollo    │          │   athena    │
    │Port:8201│           │ Port: 8202  │          │ Port: 8203  │
    └─────────┘           └─────────────┘          └─────────────┘
```

## Endpoints

### Discovery & Health

#### GET /api/mcp/v2/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "aish-mcp",
  "version": "2.0",
  "capabilities": ["streaming", "tools", "messages"]
}
```

#### GET /api/mcp/v2/capabilities
MCP capability discovery.

**Response:**
```json
{
  "mcp_version": "1.0",
  "server_name": "aish",
  "capabilities": {
    "tools": {
      "send-message": "Send message to specific AI",
      "team-chat": "Broadcast to all team members",
      "forward": "Manage AI forwarding",
      "list-ais": "List available AIs",
      "purpose": "Get/set terminal purpose"
    },
    "streaming": true
  }
}
```

### Messaging

#### POST /api/mcp/v2/tools/send-message
Send a message to a specific AI.

**Request:**
```json
{
  "ai_name": "numa",
  "message": "Hello from MCP",
  "stream": false  // optional, defaults to false
}
```

**Response (non-streaming):**
```json
{
  "response": "AI response text"
}
```

**Response (streaming):**
Server-Sent Events stream with chunks:
```
data: {"done": false, "delta": "Partial "}
data: {"done": false, "delta": "response "}
data: {"done": true, "delta": "text"}
```

#### POST /api/mcp/v2/tools/team-chat
Broadcast message to all team members.

**Request:**
```json
{
  "message": "Team update from MCP"
}
```

**Response:**
```json
{
  "responses": [
    {
      "specialist_id": "numa",
      "content": "Response from numa",
      "socket_id": "numa"
    },
    {
      "specialist_id": "apollo", 
      "content": "Response from apollo",
      "socket_id": "apollo"
    }
  ]
}
```

### AI Management

#### POST /api/mcp/v2/tools/list-ais
List all available AIs.

**Response:**
```json
{
  "ais": [
    {
      "name": "numa",
      "port": 8201,
      "status": "active",
      "purpose": "NUMA - Intelligent Systems Integration"
    },
    {
      "name": "apollo",
      "port": 8202,
      "status": "active", 
      "purpose": "Code Development"
    }
  ]
}
```

### Forwarding

#### POST /api/mcp/v2/tools/forward
Manage AI forwarding rules.

**List forwards:**
```json
{
  "action": "list"
}
```

**Add forward:**
```json
{
  "action": "add",
  "ai_name": "numa",
  "terminal": "term-123"
}
```

**Remove forward:**
```json
{
  "action": "remove",
  "ai_name": "numa"
}
```

## UI Integration

All UI components use the aish MCP server through `window.AIChat`:

```javascript
// In tekton-urls.js
function aishUrl(path = "", ...args) {
    const host = args[0] || "localhost";
    const scheme = args[1] || "http";
    const port = window.AISH_MCP_PORT || 8118;
    return `${scheme}://${host}:${port}${path}`;
}

// In ai-chat.js
window.AIChat = {
    sendMessage: async function(aiName, message) {
        const response = await fetch(aishUrl("/api/mcp/v2/tools/send-message"), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ai_name: aiName, message: message })
        });
        const data = await response.json();
        return data.response;
    }
};
```

## Management Commands

### Command Line
```bash
# Check MCP server status
aish status

# Restart MCP server
aish restart

# View MCP server logs
aish logs

# Debug MCP operations
aish debug-mcp
```

### Interactive Shell
```
aish> /status
MCP server is running on port 8118
Process ID: 12345

aish> /restart
Stopping MCP server...
Starting MCP server on port 8118...
MCP server started successfully

aish> /logs
[Recent MCP server logs]

aish> /debug-mcp
MCP Debug Mode enabled - verbose logging active
```

## Testing

Run the comprehensive test suite:

```bash
cd $TEKTON_ROOT/shared/aish/tests
./test_mcp.sh
```

Or run Python tests directly:
```bash
python3 -m pytest test_mcp_server.py -v
```

## Important Notes

1. **AI Names**: Use the base AI name without suffix (e.g., `numa` not `numa-ai`)
2. **Port**: MCP server runs on AISH_MCP_PORT (8118), not AISH_PORT (8117)
3. **Single Source**: All message routing goes through aish MCP
4. **Error Handling**: Unknown AI names return 500 with "Unknown AI: [name]"
5. **Streaming**: Set `stream: true` for SSE responses

## Migration from Direct HTTP

Before (direct HTTP):
```javascript
// Old way - direct to specialist
fetch("http://localhost:8201/api/v1/ai/specialists/numa/message", {
    method: 'POST',
    body: JSON.stringify({ message: "Hello" })
});
```

After (MCP):
```javascript
// New way - through aish MCP
fetch(aishUrl("/api/mcp/v2/tools/send-message"), {
    method: 'POST', 
    body: JSON.stringify({ ai_name: "numa", message: "Hello" })
});
```

## Environment Variables

Set by tekton-clean-launch.c:
- `AISH_PORT`: 8117 (aish shell port)
- `AISH_MCP_PORT`: 8118 (MCP server port)

Available in UI as:
- `window.AISH_PORT`
- `window.AISH_MCP_PORT`