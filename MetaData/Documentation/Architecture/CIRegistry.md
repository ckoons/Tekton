# AI Communication Architecture

## Overview

Tekton's AI system uses a simplified "One Queue, One Socket, One AI" architecture. Each component can have an associated AI specialist that provides intelligent assistance through direct socket communication using fixed ports.

**Important Update**: For CI tools integration (like Claude Code, Cursor, Continue), see the [CI Tools Infrastructure](CI_Tools_Infrastructure.md) documentation which describes the new C-based launcher and message bus system.

## Key Components

### 1. Simple AI Interface (`shared/ai/simple_ai.py`)

The unified interface for all AI communication:

- **Direct Communication**: Both sync (`ai_send_sync`) and async (`ai_send`) methods
- **Configurable Ports**: AI port = TEKTON_AI_PORT_BASE + (component_port - TEKTON_PORT_BASE)
- **Message Tracking**: UUID-based message IDs for reliable request/response matching
- **No Registry**: Direct host:port connections without registry files

### 2. AI Service Simple (`shared/ai/ai_service_simple.py`)

Core service managing AI communication:

- **Queue Management**: One queue per AI for message handling
- **Socket Connections**: Direct socket connections to AI specialists
- **Auto-Registration**: 18 AIs automatically registered on service import
- **Error Handling**: Graceful degradation when AIs are not running
- **No Singletons**: Filesystem-based state management (see CI Tools Infrastructure)

### 3. Generic AI Specialist (`shared/ai/generic_specialist.py`)

A configurable AI implementation that adapts to any component:

- Component-specific personalities and expertise
- Unified implementation for all components
- Automatic configuration based on component name

## Architecture Flow

```
Component Request
      ↓
simple_ai.ai_send() or ai_send_sync()
      ↓
ai_service_simple message queue
      ↓
Direct socket connection (fixed port)
      ↓
AI Specialist processes request
      ↓
Response via same socket
```

## Fixed Port System

All AI ports are calculated using configurable bases:
```
AI Port = TEKTON_AI_PORT_BASE + (Component Port - TEKTON_PORT_BASE)
```

Examples with defaults (TEKTON_PORT_BASE=8000, TEKTON_AI_PORT_BASE=45000):
- Tekton (8000) → AI Port 45000
- Hermes (8001) → AI Port 45001
- Engram (8002) → AI Port 45002

## Component AI Personalities

Each AI specialist has a unique personality defined in `COMPONENT_EXPERTISE`:

- **Hermes**: The Service Orchestrator
- **Engram**: The Memory Curator
- **Rhetor**: The Prompt Architect
- **Athena**: The Knowledge Weaver
- **Prometheus**: The Strategic Planner
- **Numa**: The Specialist Orchestrator
- ...and more

## Configuration

### Environment Variables

- `TEKTON_REGISTER_AI`: Enable/disable AI support globally
- `TEKTON_AI_PROVIDER`: LLM provider (`ollama` or `anthropic`)
- `<COMPONENT>_AI_MODEL`: Override model for specific component

### Model Configuration

Default model: `gpt-oss:20b` (with automatic thinking level detection)

The system now features **dynamic model selection** based on keywords in your queries:
- **Quick tasks**: gpt-oss:20b (default)
- **Problem solving**: gpt-oss:120b with focused parameters
- **Deep thinking**: gpt-oss:120b with maximum reasoning

See [AI Thinking Levels Documentation](./AI_Thinking_Levels.md) for details.

Models can be configured per component:
```bash
export ATHENA_AI_MODEL=gpt-oss:120b
export RHETOR_AI_MODEL=gpt-oss:20b
```

## Usage Examples

### Python - Synchronous
```python
from shared.ai.simple_ai import ai_send_sync
response = ai_send_sync("apollo-ai", "What patterns do you see?", "localhost", 45012)
```

### Python - Asynchronous
```python
from shared.ai.simple_ai import ai_send
response = await ai_send("numa-ai", "Help implement this feature", "localhost", 45004)
```

### Testing Communication
```python
# Quick test
from shared.ai.simple_ai import ai_send_sync
response = ai_send_sync("apollo-ai", "ping", "localhost", 45012)
print(response)
```

## Troubleshooting

### AI Not Responding

1. Check if AI process is running: `ps aux | grep component-ai`
2. Verify port is open: `nc -zv localhost 45000`
3. Check fixed port calculation matches expectation
4. Ensure `TEKTON_REGISTER_AI=true` in `.env.tekton`

### Port Conflicts

- Verify no other processes using ports 45000-45080
- Check component ports are correctly configured (8000-8080)
- Use `scripts/check_port_alignment.py` to verify port mapping

### Testing AI Service

```bash
# Run test suite
python tests/test_ai_service_simple.py
python tests/test_integration_simple.py
python tests/test_unified_ai_communication.py
```

## Integration Points

1. **Enhanced Launcher**: Automatically launches AI when component starts
2. **Status Display**: Shows AI model and health in `tekton-status`
3. **Socket Communication**: Direct AI interaction via socket protocol
4. **aish Integration**: AI shell uses the unified system

## Best Practices

1. Always use the generic AI specialist for new components
2. Define component expertise in `COMPONENT_EXPERTISE` dict
3. Use fixed port formula for consistency
4. Monitor AI health through `tekton-status`
5. Use the simple_ai interface for all communication

## Migration from Registry System

The old ai_registry system has been replaced with this simpler approach:
- No registry files needed
- No complex locking mechanisms
- Direct socket connections only
- Fixed port allocation by formula

This aligns with Tekton's philosophy: "Do it once, do it well, and don't reinvent the wheel."