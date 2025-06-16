# Rhetor Implementation Summary

This document provides a high-level overview of the Rhetor LLM Management System implementation.

## Architecture

Rhetor is built with a single-port architecture that simplifies deployment and integration:

```
┌─────────────────────────────────┐
│          Rhetor Server          │
│   (HTTP + WebSocket on Port 8300)  │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│         Model Router            │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│          LLM Client             │
└─────────────┬───────────────────┘
              │
        ┌─────┴─────┐
        │           │
        ▼           ▼
┌─────────────┐  ┌─────────────┐
│  Provider 1 │  │  Provider 2 │ ...
└─────────────┘  └─────────────┘
```

## Key Components

### API Server
- Single FastAPI application serving both HTTP and WebSocket endpoints
- Unified port for all LLM interactions
- Support for streaming via Server-Sent Events and WebSockets
- Health and status endpoints

### LLM Client
- Central manager for all LLM providers
- Handles provider initialization and availability checking
- Routes requests to appropriate providers
- Implements fallback mechanisms

### Model Router
- Selects the best model based on task requirements
- Configurable via JSON configuration file
- Support for component-specific model selection
- Override capability for special cases

### Context Manager
- Tracks conversation history across requests
- Persists conversations to disk and Engram (if available)
- Formats messages for different LLM providers
- Provides context windowing and pruning

### Providers
- `AnthropicProvider`: Access to Claude API
- `OpenAIProvider`: Access to GPT API
- `OllamaProvider`: Local LLM support
- `SimulatedProvider`: Fallback when no APIs are available

## Integration Points

### Hermes Registration
Rhetor registers itself with Hermes to enable discovery by other components:
```json
{
  "id": "rhetor",
  "name": "Rhetor",
  "description": "LLM Management System for Tekton",
  "version": "0.1.0",
  "url": "http://localhost:8300",
  "capabilities": [
    "llm_management",
    "prompt_engineering",
    "context_management",
    "model_selection"
  ],
  "endpoints": {
    "http": "http://localhost:8300",
    "ws": "ws://localhost:8300/ws"
  }
}
```

### Single Port Access
All clients connect to port 8300 for:
- HTTP API (`/message`, `/stream`, etc.)
- WebSocket (`/ws`)
- Server status (`/health`, `/providers`)

### Consistent Communication Format
All responses follow a consistent format:
```json
{
  "message": "Response content",
  "model": "claude-3-sonnet-20240229",
  "provider": "anthropic",
  "context": "context_id",
  "finished": true,
  "timestamp": "2025-04-24T12:34:56.789Z"
}
```

## File Structure

```
rhetor/
├── __init__.py
├── __main__.py              # Entry point
├── api/
│   ├── __init__.py
│   └── app.py               # FastAPI application
├── core/
│   ├── __init__.py
│   ├── context_manager.py   # Context tracking
│   ├── llm_client.py        # LLM provider management
│   ├── model_router.py      # Model selection
│   └── prompt_engine.py     # Prompt management
├── models/
│   ├── __init__.py
│   └── providers/
│       ├── __init__.py
│       ├── anthropic.py     # Claude provider
│       ├── base.py          # Base provider interface
│       ├── ollama.py        # Ollama provider
│       ├── openai.py        # OpenAI provider
│       └── simulated.py     # Simulated provider
├── config/                  # Configuration files
├── utils/                   # Utility modules
└── templates/               # Prompt templates
```

## Usage

### Starting the Server
```bash
./run_rhetor.sh
```

### Sending a Message
```bash
curl -X POST http://localhost:8300/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, world!",
    "context_id": "test",
    "task_type": "chat",
    "streaming": false
  }'
```

### WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8300/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
ws.send(JSON.stringify({
  type: "LLM_REQUEST",
  source: "UI",
  payload: {
    message: "Hello, world!",
    context: "test",
    task_type: "chat",
    streaming: true
  }
}));
```