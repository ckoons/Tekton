# Ergon API Reference

## Introduction

This document provides a comprehensive reference for the Ergon API. It details the available endpoints, request and response formats, and authentication requirements.

## Base URL

The Ergon API is available at:

```
http://localhost:8002/
```

For Tekton's Single Port Architecture:
```
http://localhost:8002/api/
```

## Authentication

Most API endpoints do not require authentication in development mode. In production mode, authentication can be enabled through the `require_authentication` configuration option.

## Common Response Format

Most API responses follow a standard format:

```json
{
  "status": "success|error",
  "data": { ... },
  "error": "Error message (if status is error)"
}
```

## API Endpoints

### Status and Health

#### GET /api

Get API status information.

**Response**:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "database": true,
  "models": ["gpt-4o-mini", "claude-3-sonnet-20240229"],
  "doc_count": 120,
  "port": 8002,
  "single_port_enabled": true
}
```

#### GET /health

Get API health status.

**Response**:
```json
{
  "status": "ok",
  "timestamp": "2025-04-28T14:30:00.000Z",
  "version": "0.1.0"
}
```

### Agents

#### GET /api/agents

List all agents.

**Query Parameters**:
- `skip` (integer, optional): Number of agents to skip (default: 0)
- `limit` (integer, optional): Maximum number of agents to return (default: 100)

**Response**:
```json
[
  {
    "id": 1,
    "name": "github_agent",
    "description": "GitHub operations agent",
    "model_name": "gpt-4o-mini",
    "system_prompt": "You are a GitHub agent...",
    "created_at": "2025-04-28T14:30:00.000Z",
    "updated_at": "2025-04-28T14:30:00.000Z"
  }
]
```

#### POST /api/agents

Create a new agent.

**Request Body**:
```json
{
  "name": "code_assistant",
  "description": "Code assistant for Python development",
  "model_name": "claude-3-sonnet-20240229",
  "tools": [
    {
      "name": "search_code",
      "description": "Search code repository",
      "parameters": {
        "query": {
          "type": "string",
          "description": "Search query"
        }
      }
    }
  ],
  "temperature": 0.7
}
```

**Response**:
```json
{
  "id": 2,
  "name": "code_assistant",
  "description": "Code assistant for Python development",
  "model_name": "claude-3-sonnet-20240229",
  "system_prompt": "You are code_assistant, an CI assistant...",
  "created_at": "2025-04-28T14:35:00.000Z",
  "updated_at": "2025-04-28T14:35:00.000Z"
}
```

#### GET /api/agents/{agent_id}

Get agent by ID.

**Path Parameters**:
- `agent_id` (integer): ID of the agent

**Response**:
```json
{
  "id": 2,
  "name": "code_assistant",
  "description": "Code assistant for Python development",
  "model_name": "claude-3-sonnet-20240229",
  "system_prompt": "You are code_assistant, an CI assistant...",
  "created_at": "2025-04-28T14:35:00.000Z",
  "updated_at": "2025-04-28T14:35:00.000Z"
}
```

#### DELETE /api/agents/{agent_id}

Delete agent by ID.

**Path Parameters**:
- `agent_id` (integer): ID of the agent

**Response**:
```json
{
  "status": "deleted",
  "id": 2
}
```

#### POST /api/agents/{agent_id}/run

Run an agent with the given input.

**Path Parameters**:
- `agent_id` (integer): ID of the agent

**Request Body**:
```json
{
  "content": "Generate a Python function to calculate Fibonacci numbers",
  "stream": false
}
```

**Response** (when `stream` is `false`):
```json
{
  "role": "assistant",
  "content": "Here's a Python function to calculate Fibonacci numbers:\n\n```python\ndef fibonacci(n):\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)\n```\n\nThis is a simple recursive implementation...",
  "timestamp": "2025-04-28T14:40:00.000Z"
}
```

**Response** (when `stream` is `true`):
Server-sent events containing chunks of the response.

### Documentation

#### POST /api/docs/crawl

Crawl documentation from specified source.

**Request Body**:
```json
{
  "source": "all",
  "max_pages": 100
}
```

**Response**:
```json
{
  "status": "ok",
  "pages_crawled": 87,
  "source": "all"
}
```

#### GET /api/docs/search

Search documentation.

**Query Parameters**:
- `query` (string): Search query
- `limit` (integer, optional): Maximum number of results to return (default: 5)

**Response**:
```json
[
  {
    "id": "doc_123",
    "title": "Agent Creation Guide",
    "url": "https://example.com/docs/agent-creation",
    "source": "internal",
    "content": "This guide explains how to create effective agents...",
    "score": 0.92
  }
]
```

### Terminal Interface

#### POST /api/terminal/message

Handle terminal message from UI.

**Request Body**:
```json
{
  "message": "How do I create a new agent?",
  "context_id": "ergon",
  "model": "claude-3-sonnet-20240229",
  "temperature": 0.7,
  "max_tokens": 500,
  "streaming": false,
  "save_to_memory": true
}
```

**Response**:
```json
{
  "status": "success",
  "message": "To create a new agent in Ergon, you can use the CLI or API...",
  "context_id": "ergon"
}
```

#### POST /api/terminal/stream

Stream response from LLM for terminal.

**Request Body**:
Same as `/api/terminal/message` but with `streaming` set to `true`.

**Response**:
Server-sent events with the following format:
```
data: {"chunk": "To create a new agent", "context_id": "ergon"}
```

### Agent-to-Agent (A2A) Protocol

#### POST /api/a2a/message

Send a message from one agent to another.

**Request Body**:
```json
{
  "sender_id": "agent_1",
  "recipient_id": "agent_2",
  "message": "Can you analyze this code?",
  "context": {
    "code": "def example(): return True"
  }
}
```

**Response**:
```json
{
  "status": "delivered",
  "message_id": "msg_12345"
}
```

#### GET /api/a2a/messages/{recipient_id}

Get messages for a specific agent.

**Path Parameters**:
- `recipient_id` (string): ID of the recipient agent

**Query Parameters**:
- `limit` (integer, optional): Maximum number of messages to return (default: 10)
- `since` (string, optional): Return messages after this timestamp

**Response**:
```json
{
  "messages": [
    {
      "id": "msg_12345",
      "sender_id": "agent_1",
      "recipient_id": "agent_2",
      "message": "Can you analyze this code?",
      "context": {
        "code": "def example(): return True"
      },
      "timestamp": "2025-04-28T14:45:00.000Z"
    }
  ]
}
```

### MCP Protocol

#### POST /api/mcp/process

Process content using the MCP protocol.

**Request Body**:
```json
{
  "id": "mcp-msg-12345",
  "client_id": "ergon-client",
  "client_name": "Ergon MCP Client",
  "content": {
    "content_type": "text",
    "content": {
      "text": "Analyze the sentiment of this text."
    }
  },
  "content_type": "text",
  "context": {
    "previous_analysis": "neutral"
  },
  "processing_options": {
    "model": "claude-3-sonnet-20240229",
    "temperature": 0.3
  },
  "tools": [
    {
      "name": "sentiment_analyzer",
      "description": "Analyzes sentiment of text",
      "parameters": {
        "text": {
          "type": "string",
          "description": "Text to analyze"
        }
      }
    }
  ]
}
```

**Response**:
```json
{
  "id": "mcp-resp-67890",
  "original_msg_id": "mcp-msg-12345",
  "status": "success",
  "result": {
    "content_type": "structured",
    "content": {
      "data": {
        "sentiment": "positive",
        "confidence": 0.87,
        "analysis": "The text has a positive tone..."
      }
    }
  }
}
```

#### POST /api/mcp/tools/register

Register a tool with the MCP service.

**Request Body**:
```json
{
  "tool_id": "code_analyzer",
  "name": "Code Analyzer",
  "description": "Analyzes code for quality and security issues",
  "parameters": {
    "code": {
      "type": "string",
      "description": "Code to analyze"
    },
    "language": {
      "type": "string",
      "description": "Programming language",
      "enum": ["python", "javascript", "java"]
    }
  },
  "returns": {
    "type": "object",
    "properties": {
      "issues": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "type": {
              "type": "string"
            },
            "message": {
              "type": "string"
            },
            "line": {
              "type": "integer"
            }
          }
        }
      }
    }
  },
  "client_id": "ergon-client",
  "client_name": "Ergon MCP Client",
  "metadata": {
    "version": "1.0.0"
  }
}
```

**Response**:
```json
{
  "success": true,
  "tool_id": "code_analyzer",
  "message": "Tool registered successfully"
}
```

#### POST /api/mcp/tools/execute

Execute a tool registered with the MCP service.

**Request Body**:
```json
{
  "tool_id": "code_analyzer",
  "parameters": {
    "code": "def example(): return True",
    "language": "python"
  },
  "client_id": "ergon-client",
  "context": {
    "previous_issues": []
  }
}
```

**Response**:
```json
{
  "success": true,
  "result": {
    "issues": [
      {
        "type": "style",
        "message": "Missing docstring",
        "line": 1
      }
    ]
  }
}
```

### WebSocket API

#### /ws

WebSocket endpoint for real-time communication.

**Connection**:
Connect to `ws://localhost:8002/ws`

**Messages**:

Client to Server:
```json
{
  "protocol": "a2a",
  "type": "message",
  "sender": "agent_1",
  "recipient": "agent_2",
  "content": "Hello from agent_1",
  "timestamp": 1714307400
}
```

Server to Client:
```json
{
  "type": "a2a_ack",
  "status": "received",
  "timestamp": 1714307401
}
```

MCP Protocol:
```json
{
  "protocol": "mcp",
  "type": "tool_execution",
  "tool_id": "code_analyzer",
  "parameters": {
    "code": "def example(): return True",
    "language": "python"
  }
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - The request was invalid or cannot be served |
| 401 | Unauthorized - Authentication is required |
| 404 | Not Found - The resource does not exist |
| 422 | Unprocessable Entity - The request was well-formed but could not be processed |
| 500 | Server Error - An error occurred on the server |

## Rate Limiting

The API implements rate limiting to prevent abuse:

- 100 requests per minute per IP address for most endpoints
- 20 requests per minute for agent execution endpoints
- 5 requests per minute for document crawling

## Pagination

List endpoints support pagination through `skip` and `limit` parameters:

```
GET /api/agents?skip=10&limit=5
```

This would return agents 11-15 in the collection.

## Versioning

The current API version is v1, which is implicit in all endpoints. Future versions will be accessible via explicit version prefix:

```
/api/v2/agents
```

## CORS

The API supports Cross-Origin Resource Sharing (CORS) and allows requests from any origin in development mode. In production, this should be restricted to specific domains.

## Example Usage

### Python Client

```python
import requests

# Create an agent
response = requests.post("http://localhost:8002/api/agents", json={
    "name": "code_assistant",
    "description": "Code assistant for Python development",
    "model_name": "claude-3-sonnet-20240229"
})

agent_id = response.json()["id"]

# Run the agent
response = requests.post(f"http://localhost:8002/api/agents/{agent_id}/run", json={
    "content": "Write a Python function to calculate factorial"
})

print(response.json()["content"])
```

### JavaScript Client

```javascript
// Create an agent
fetch("http://localhost:8002/api/agents", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    name: "code_assistant",
    description: "Code assistant for Python development",
    model_name: "claude-3-sonnet-20240229"
  })
})
.then(response => response.json())
.then(data => {
  const agentId = data.id;
  
  // Run the agent
  return fetch(`http://localhost:8002/api/agents/${agentId}/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      content: "Write a Python function to calculate factorial"
    })
  });
})
.then(response => response.json())
.then(data => console.log(data.content));
```

### WebSocket Client

```javascript
const ws = new WebSocket("ws://localhost:8002/ws");

ws.onopen = () => {
  // Send an A2A message
  ws.send(JSON.stringify({
    protocol: "a2a",
    type: "message",
    sender: "agent_1",
    recipient: "agent_2",
    content: "Hello from agent_1",
    timestamp: Math.floor(Date.now() / 1000)
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};
```