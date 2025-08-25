# Implementation Plan

## 1. SSE Streaming Implementation

### Rhetor SSE Endpoint
```python
# Rhetor/rhetor/api/streaming.py
from fastapi import Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

async def stream_chat(specialist_id: str, message: str, request: Request):
    async def event_generator():
        # Connect to specialist
        specialist = get_specialist(specialist_id)
        
        # Stream tokens from Ollama
        async for token in specialist.stream_generate(message):
            if await request.is_disconnected():
                break
            yield {
                "event": "token",
                "data": json.dumps({"token": token, "specialist_id": specialist_id})
            }
        
        yield {"event": "done", "data": ""}
    
    return EventSourceResponse(event_generator())
```

### Ollama Streaming Integration
```python
# shared/ai/specialist_worker.py
async def stream_generate(self, prompt: str):
    """Stream tokens from Ollama."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{self.ollama_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": True}
        ) as response:
            async for line in response.content:
                if line:
                    data = json.loads(line)
                    if 'response' in data:
                        yield data['response']
```

## 2. Team Chat Fix

### Debug Steps
1. Add logging to track message flow
2. Verify CI registration in registry
3. Check socket connections
4. Fix timeout handling

### Implementation
```python
# Rhetor/rhetor/api/routes.py
@router.post("/api/team-chat")
async def team_chat(request: TeamChatRequest):
    # Get all active specialists
    specialists = await discover_specialists()
    
    # Send to each with proper timeout
    responses = {}
    tasks = []
    
    for spec in specialists:
        task = asyncio.create_task(
            send_with_timeout(spec.id, request.message, timeout=10)
        )
        tasks.append((spec.id, task))
    
    # Collect responses
    for spec_id, task in tasks:
        try:
            response = await task
            responses[spec_id] = response
        except asyncio.TimeoutError:
            logger.warning(f"{spec_id} timed out")
    
    return {"responses": responses}
```

## 3. MCP Tools Implementation

### GetSpecialistConversationHistory
```python
async def get_specialist_conversation_history(self, specialist_id: str, limit: int = 10):
    """Get conversation history from Engram."""
    # Connect to Engram
    engram_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{engram_url}/api/conversations/{specialist_id}",
            params={"limit": limit}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "success": True,
                    "history": data.get("conversations", []),
                    "total": data.get("total", 0)
                }
    
    return {"success": False, "error": "Failed to retrieve history"}
```

### ConfigureOrchestration
```python
async def configure_orchestration(self, settings: Dict[str, Any]):
    """Configure CI orchestration rules."""
    schema = {
        "routing_rules": [
            {
                "pattern": str,  # e.g., "planning"
                "specialists": [str],  # e.g., ["prometheus-ai", "metis-ai"]
                "strategy": str  # e.g., "round-robin", "all", "best"
            }
        ],
        "timeout_settings": {
            "default": float,
            "per_specialist": Dict[str, float]
        },
        "retry_policy": {
            "enabled": bool,
            "max_attempts": int
        }
    }
    
    # Validate settings
    # Store in registry or config service
    # Return success/failure
```

## 4. Pipeline Context Support

### Context Protocol
```python
# Message format with context
{
    "type": "chat",
    "content": "message",
    "context": {
        "session_id": "uuid",
        "previous_specialist": "apollo-ai",
        "previous_response": "...",
        "pipeline_stage": 2,
        "memory_hints": ["remember the optimization discussion"]
    }
}
```

### Implementation in specialist_worker.py
```python
def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
    content = message.get('content', '')
    context = message.get('context', {})
    
    # Build prompt with context
    if context.get('memory_hints'):
        prompt = f"Context: {'; '.join(context['memory_hints'])}\n\n{content}"
    else:
        prompt = content
    
    # Generate response
    response = self.generate_response(prompt)
    
    return {
        "type": "chat_response",
        "content": response,
        "context": {
            "specialist_id": self.ai_id,
            "session_id": context.get('session_id')
        }
    }
```

## 5. Testing Strategy

### SSE Testing
```bash
# Test streaming endpoint
curl -N -H "Accept: text/event-stream" \
  http://localhost:8003/api/chat/athena-ai/stream \
  -d '{"message": "Explain knowledge graphs"}'
```

### Team Chat Testing
```python
# Test team chat with multiple CIs
response = requests.post(
    "http://localhost:8003/api/team-chat",
    json={"message": "What should we optimize?"}
)
assert len(response.json()['responses']) > 0
```

### Pipeline Context Testing
```bash
# Test context passing
echo '{"context": {"memory_hints": ["previous discussion about optimization"]}, "content": "Continue that thought"}' | \
  nc localhost 45003
```