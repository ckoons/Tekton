# Rhetor Quick Reference Guide

## Overview

Rhetor is the LLM management system for Tekton, providing:
- Centralized LLM access through a single port (8300)
- Support for multiple providers (Anthropic, OpenAI, Ollama)
- Intelligent model routing based on task requirements
- Budget management and cost optimization
- Context tracking and persistence

## Key Features

| Feature | Description |
|---------|-------------|
| Single-Port API | Both HTTP and WebSocket on port 8300 |
| Multiple Providers | Claude, GPT, Ollama, and fallback options |
| Task-Based Routing | Selects models based on task requirements |
| Budget Management | Tracks costs and enforces spending limits |
| Context Management | Persists conversation history |
| System Prompts | Manages component-specific prompts |

## API Quick Reference

### HTTP Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Basic server information |
| `/health` | GET | Health check endpoint |
| `/providers` | GET | List available providers and models |
| `/provider` | POST | Set active provider and model |
| `/message` | POST | Send a message to the LLM |
| `/stream` | POST | Get streaming response |
| `/chat` | POST | Send multi-message conversation |
| `/templates` | GET, POST | Manage templates |
| `/prompts` | GET, POST | Manage prompts |
| `/contexts` | GET | List available contexts |
| `/budget` | GET | Get budget status |

### WebSocket

Connect to `ws://localhost:8300/ws` and send JSON messages:

```json
{
  "type": "LLM_REQUEST",
  "source": "UI",
  "payload": {
    "message": "Your message here",
    "context": "context_id",
    "task_type": "chat",
    "streaming": true
  }
}
```

## Task Types

| Task Type | Primary Model | Fallback Model | Use Case |
|-----------|---------------|----------------|----------|
| `code` | Claude 3 Opus | GPT-4 Turbo | Code generation, analysis |
| `planning` | Claude 3 Sonnet | GPT-4o | Planning and design |
| `reasoning` | Claude 3 Sonnet | GPT-4o | Complex reasoning |
| `chat` | Claude 3 Haiku | GPT-3.5-Turbo | Simple conversations |
| `default` | Claude 3 Sonnet | GPT-4o | General purpose |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RHETOR_PORT` | 8300 | Server port |
| `RHETOR_TASK_CONFIG` | ./config/tasks.json | Task configuration file |
| `RHETOR_BUDGET_POLICY` | warn | Default budget policy |
| `RHETOR_BUDGET_DAILY_LIMIT` | 0 | Daily budget limit (USD) |
| `RHETOR_BUDGET_WEEKLY_LIMIT` | 0 | Weekly budget limit (USD) |
| `RHETOR_BUDGET_MONTHLY_LIMIT` | 0 | Monthly budget limit (USD) |
| `HERMES_API_URL` | http://localhost:8100 | Hermes API URL |

## Component Integration

Components can use Rhetor through:

1. HTTP API: Direct API calls to endpoints
2. WebSocket: Real-time bidirectional communication
3. Python Client: `from rhetor.client import get_rhetor_prompt_client`
4. JavaScript Client: `import { RhetorClient } from 'tekton-llm-client'`

## Basic Usage Examples

### HTTP Request
```bash
curl -X POST http://localhost:8300/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a function to calculate Fibonacci numbers",
    "context_id": "code-examples",
    "task_type": "code",
    "streaming": false
  }'
```

### JavaScript WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8300/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: "LLM_REQUEST",
    source: "MyComponent",
    payload: {
      message: "Write a function to calculate Fibonacci numbers",
      context: "code-examples",
      task_type: "code",
      streaming: true
    }
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

### Python Client
```python
import asyncio
from rhetor.client import get_rhetor_prompt_client

async def main():
    client = await get_rhetor_prompt_client()
    
    try:
        prompt = await client.generate_prompt(
            task="Write a function to calculate Fibonacci numbers",
            context={"language": "Python", "efficiency": "high"},
            format="instruction"
        )
        
        print(prompt)
    
    finally:
        await client.close()

asyncio.run(main())
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check Rhetor is running on port 8300 |
| Provider unavailable | Verify API keys are properly configured |
| Budget exceeded | Increase limits or change enforcement policy |
| Context too large | Use summarization or split conversations |
| Rate limiting | Implement retries with backoff strategy |

## Starting/Stopping

```bash
# Start Rhetor
./run_rhetor.sh

# With Tekton launcher
tekton-launch --components rhetor

# Register with Hermes
python register_with_hermes.py

# Stop Rhetor
tekton-kill
```

## Further Documentation

For complete documentation, see:
- [Technical Documentation](./technical_documentation.md)
- [Rhetor Implementation Summary](../IMPLEMENTATION_SUMMARY.md)
- [Phase 1 Completion Report](../PHASE_1_COMPLETED.md)