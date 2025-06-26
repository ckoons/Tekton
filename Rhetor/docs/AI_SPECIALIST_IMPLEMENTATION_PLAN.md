# AI Specialist Implementation Plan

## Overview

We need to implement real AI specialists that can:
1. Connect to actual LLMs (Claude, GPT-4, etc.)
2. Read messages from their sockets
3. Process them with their specialized prompts
4. Write responses back to their sockets

## Current Architecture

### What We Have
1. **Socket Registry** ✅
   - Unix-philosophy design: AIs just read/write
   - Automatic header management
   - Persistence via Engram
   - Broadcasting support

2. **Team Chat API** ✅
   - `/api/team-chat` endpoint
   - Multiple moderation modes
   - Streaming support

3. **AI Specialist Manager** ✅
   - Configuration management
   - Specialist definitions in `config/ai_specialists.json`
   - Socket integration ready

### What We Need
1. **AI Specialist Process**
   - Actual process/thread that runs the AI
   - Connects to LLM via existing `LLMClient`
   - Polls socket for messages
   - Sends responses back

## Implementation Design

### Option 1: Threaded Specialists (Recommended for Start)
```python
class AISpecialistWorker:
    def __init__(self, specialist_id, config, socket_registry, llm_client):
        self.specialist_id = specialist_id
        self.config = config
        self.socket_registry = socket_registry
        self.llm_client = llm_client
        self.running = False
        
    async def run(self):
        """Main loop - read from socket, process, respond."""
        while self.running:
            # Read messages from socket
            messages = await self.socket_registry.read(self.specialist_id)
            
            for msg in messages:
                # Strip header, get content
                content = msg['content']
                
                # Process with LLM
                response = await self.llm_client.complete(
                    prompt=content,
                    system_prompt=self.config.model_config['system_prompt'],
                    model=self.config.model_config['model']
                )
                
                # Write response to socket
                await self.socket_registry.write(
                    self.specialist_id,
                    response
                )
            
            await asyncio.sleep(0.1)  # Poll interval
```

### Option 2: Subprocess Specialists (Future)
- Each specialist runs as separate process
- Better isolation and resource management
- More complex to implement

## Implementation Steps

### Phase 1: Basic Rhetor-Apollo Communication

1. **Create Specialist Worker Base Class**
   - Read/write loop
   - LLM integration
   - Error handling

2. **Implement Rhetor Specialist**
   - Use Rhetor's orchestrator prompt
   - Connect to Claude-3-Opus
   - Handle team chat moderation

3. **Implement Apollo Specialist**
   - Use Apollo's executive coordinator prompt
   - Connect to Claude-3-Sonnet
   - Focus on strategic responses

4. **Test Basic Conversation**
   - Start both specialists
   - Send team chat message
   - Verify they respond and interact

### Phase 2: Enhanced Features

1. **Context Management**
   - Maintain conversation history per specialist
   - Use Rhetor's existing context manager

2. **Specialized Behaviors**
   - Rhetor: Moderation modes (synthesis, consensus, etc.)
   - Apollo: Strategic analysis and decision-making

3. **Performance Optimization**
   - Batch message processing
   - Async LLM calls
   - Response caching

## Code Structure

```
rhetor/core/
├── ai_specialist_worker.py      # Base worker class
├── specialists/
│   ├── __init__.py
│   ├── rhetor_specialist.py    # Rhetor implementation
│   └── apollo_specialist.py    # Apollo implementation
└── specialist_launcher.py       # Start/stop specialists
```

## Configuration

Specialists already defined in `config/ai_specialists.json`:

**Rhetor**:
- Model: claude-3-opus-20240229
- Role: Meta-AI Orchestrator
- Capabilities: Team coordination, message filtering, conflict resolution

**Apollo**:
- Model: claude-3-sonnet-20240229  
- Role: Executive Coordinator
- Capabilities: Strategic planning, resource allocation, decision making

## Testing Plan

1. **Unit Tests**
   - Test worker read/write loop
   - Mock LLM responses
   - Verify socket operations

2. **Integration Tests**
   - Start both specialists
   - Send messages via team chat
   - Verify conversation flow

3. **UI Testing**
   - Use Rhetor UI Team Chat
   - Verify real-time responses
   - Test different moderation modes

## Benefits of This Approach

1. **Simple**: Follows Unix philosophy
2. **Flexible**: Easy to add new specialists
3. **Scalable**: Can move to subprocesses later
4. **Testable**: Clear interfaces and separation
5. **Maintainable**: Each specialist is self-contained

## Next Steps

1. Review and approve this design
2. Implement base worker class
3. Create Rhetor specialist
4. Create Apollo specialist
5. Test basic conversation
6. Iterate and enhance