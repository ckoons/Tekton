# AI Registry Architecture

## Overview

The Tekton AI Registry provides a centralized, thread-safe system for managing AI specialists across the platform. Each component can have an associated AI specialist that provides intelligent assistance and automation capabilities.

## Key Components

### 1. AI Registry Client (`shared/ai/registry_client.py`)

The `AIRegistryClient` manages all AI specialist registrations with thread-safe operations:

- **Port Allocation**: Atomic port assignment (45000-50000 range)
- **Registration**: Thread-safe AI specialist registration
- **Discovery**: Find AI specialists by component
- **Lifecycle**: Track AI process states

### 2. AI Specialist Worker (`shared/ai/specialist_worker.py`)

Base class for all AI specialists providing:

- Socket-based communication protocol
- Health monitoring
- Message handling (ping, health, info, chat)
- Ollama/Anthropic LLM integration
- Automatic model selection (defaults to `llama3.3:70b`)

### 3. Generic AI Specialist (`shared/ai/generic_specialist.py`)

A configurable AI implementation that adapts to any component:

- Component-specific personalities and expertise
- Unified implementation for all components
- Automatic configuration based on component name

## Architecture Flow

```
Component Launch
      ↓
Enhanced Launcher detects AI enabled
      ↓
AI Launcher allocates port (with file lock)
      ↓
Launches Generic AI Specialist process
      ↓
AI registers with Registry (atomic operation)
      ↓
AI starts socket server on allocated port
      ↓
Status checker connects to verify
```

## Thread Safety

All registry operations use file locking to prevent race conditions:

1. **Port Allocation Lock** (`.port_allocation.lock`)
   - Ensures unique port assignment
   - Prevents concurrent allocation conflicts

2. **Registration Lock** (`.registration.lock`)
   - Atomic registry updates
   - Prevents corruption during concurrent writes
   - Shared locks for reads, exclusive for writes

## Registry Structure

Location: `~/.tekton/ai_registry/platform_ai_registry.json`

```json
{
  "component-ai": {
    "port": 45000,
    "component": "component_name",
    "metadata": {
      "description": "AI specialist for Component",
      "pid": 12345
    },
    "registered_at": 1234567890.123
  }
}
```

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

Default model: `llama3.3:70b`

Models can be configured per component:
```bash
export ATHENA_AI_MODEL=llama3.1:70b
export RHETOR_AI_MODEL=qwen2.5-coder:32b
```

## Troubleshooting

### AI Not Showing in Status

1. Check if AI process is running: `ps aux | grep component-ai`
2. Verify registry: `cat ~/.tekton/ai_registry/platform_ai_registry.json`
3. Check for port conflicts in registry
4. Ensure `TEKTON_REGISTER_AI=true` in `.env.tekton`

### Registry Corruption

The registry now has built-in protection:
- Atomic writes prevent partial updates
- File locking prevents concurrent corruption
- Automatic retry with exponential backoff
- Graceful handling of corrupted JSON

### Port Allocation Failures

- Check port range availability (45000-50000)
- Verify no other processes using these ports
- Lock file issues: Remove stale `.port_allocation.lock` if needed

## Integration Points

1. **Enhanced Launcher**: Automatically launches AI when component starts
2. **Status Display**: Shows AI model and health in `tekton-status`
3. **Socket Communication**: Direct AI interaction via socket protocol
4. **MCP Integration**: Future integration with component MCP tools

## Best Practices

1. Always use the generic AI specialist for new components
2. Define component expertise in `COMPONENT_EXPERTISE` dict
3. Let the framework handle port allocation and registration
4. Use default model unless specific requirements exist
5. Monitor AI health through `tekton-status`