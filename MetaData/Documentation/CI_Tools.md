# CI Tools Integration Architecture

## Overview

This document describes the architecture for integrating external CI (Coding Intelligence) tools like Claude Code, Cursor, Continue, and other AI-powered development tools into the Tekton ecosystem. The integration maintains Tekton's core philosophy: "CIs are sockets" - making every CI tool accessible via aish and part of the unified CI registry.

## Design Principles

1. **Unified CI Model**: CI tools are first-class citizens in the CI registry, alongside Greek Chorus CIs, Terminal CIs, and Project CIs
2. **Socket-Based Communication**: All CI tools communicate via sockets, maintaining consistency with existing architecture
3. **Transparent Integration**: CI tools are accessible through standard aish commands without special syntax
4. **Lifecycle Management**: Tekton manages CI tool processes with the same robustness as other components
5. **Interchangeability**: CI tools can be used interchangeably with other CIs for appropriate tasks

## Architecture

### CI Registry Extension

The existing CI registry will be extended to support a new CI type:

```
CI Types:
├── greek     # Greek Chorus AIs (apollo, athena, etc.)
├── terminal  # Terminal sessions (cali, iris, etc.)
├── project   # Project-specific CIs
└── tool      # CI coding tools (claude-code, cursor, etc.)
```

### CI Tool Structure

Each CI tool will have:
- **Name**: Unique identifier (e.g., `claude-code`, `cursor`, `continue`)
- **Type**: `tool`
- **Port**: Allocated from the CI tools range (8400-8449)
- **Socket**: Local socket for bidirectional communication
- **Process**: Managed subprocess of the actual tool
- **Adapter**: Tool-specific translation layer

### Communication Protocol

CI tools will use the same JSON message format as other CIs:

```json
{
  "type": "message|command|response|event",
  "ci": "claude-code",
  "content": "analyze the authentication module",
  "metadata": {
    "session_id": "project-auth-review",
    "context": {...},
    "capabilities": ["code_analysis", "refactoring", "generation"]
  }
}
```

## Implementation Components

### 1. CI Tool Adapter Framework

Located in `shared/ci_tools/`:

```
shared/ci_tools/
├── __init__.py
├── base_adapter.py      # Abstract base for all CI tool adapters
├── registry.py          # CI tool registration and discovery
├── socket_bridge.py     # Socket communication layer
└── adapters/
    ├── claude_code.py   # Claude Code specific adapter
    ├── cursor.py        # Cursor specific adapter
    └── continue.py      # Continue specific adapter
```

### 2. Process Management

CI tools will be managed through:
- **Launcher**: Starts CI tool process with proper environment
- **Monitor**: Health checks and process supervision
- **Bridge**: Stdin/stdout/stderr to socket translation
- **Lifecycle**: Clean startup and shutdown procedures

### 3. aish Extensions

New aish commands will be added while maintaining backward compatibility:

```bash
# Standard CI communication (no changes needed)
aish claude-code "review this pull request"
aish cursor "refactor the user service"

# CI tool specific features
aish list type tool              # Show available CI tools
aish status claude-code          # Check tool health
aish capabilities cursor         # List tool capabilities
```

### 4. Socket Bridge Architecture

The socket bridge provides bidirectional communication:

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│   aish client   │ ←────→  │  Socket Bridge   │ ←────→  │  CI Tool    │
│                 │ socket  │                  │ stdio   │  Process    │
└─────────────────┘         └──────────────────┘         └─────────────┘
                                     ↓
                            ┌──────────────────┐
                            │   CI Registry    │
                            │  (unified view)  │
                            └──────────────────┘
```

## Integration Points

### 1. CI Registry Integration

CI tools register automatically on startup:

```python
# In ci_registry.py
CI_TOOLS = {
    'claude-code': {
        'type': 'tool',
        'port': 8400,
        'description': 'Claude AI coding assistant',
        'executable': 'claude-code',
        'capabilities': ['analysis', 'generation', 'refactoring']
    },
    'cursor': {
        'type': 'tool',
        'port': 8401,
        'description': 'AI-powered code editor',
        'executable': 'cursor',
        'capabilities': ['editing', 'completion', 'chat']
    }
}
```

### 2. Unified Sender Integration

The existing unified sender will route messages to CI tools:

```python
# In unified_sender.py
def send_to_ci(ci_name: str, message: str) -> Optional[str]:
    ci_info = registry.get_ci(ci_name)
    
    if ci_info['type'] == 'tool':
        return send_to_tool(ci_name, message, ci_info['port'])
    # ... existing logic for other CI types
```

### 3. Apollo-Rhetor Coordination

CI tools participate in the context monitoring system:
- Apollo monitors CI tool interactions for patterns
- Rhetor can inject context into CI tool sessions
- Performance metrics tracked across all CI types

### 4. Terma Integration

CI tool sessions can be attached to Terma terminals:
- Forward CI tool output to terminal
- Capture terminal context for CI tools
- Enable collaborative sessions

## Configuration

### Environment Variables

```bash
# CI tool specific settings
CLAUDE_CODE_PATH=/usr/local/bin/claude-code
CLAUDE_CODE_MAX_TOKENS=100000
CURSOR_PATH=/Applications/Cursor.app/Contents/MacOS/Cursor
CONTINUE_CONFIG_PATH=~/.continue/config.json

# General CI tool settings
CI_TOOLS_PORT_BASE=8400
CI_TOOLS_SOCKET_TIMEOUT=30
CI_TOOLS_HEALTH_CHECK_INTERVAL=60
```

### Port Allocation

CI tools use ports 8400-8449 (50 ports allocated):
- 8400: claude-code
- 8401: cursor
- 8402: continue
- 8403-8449: Reserved for future CI tools

## Security Considerations

1. **Process Isolation**: Each CI tool runs in its own process space
2. **Socket Security**: Local sockets only, no network exposure
3. **Input Validation**: All messages validated before forwarding
4. **Resource Limits**: CPU/memory limits per CI tool process
5. **Audit Trail**: All CI tool interactions logged

## Migration Path

### Phase 1: Foundation (Week 1)
- Implement base adapter framework
- Create socket bridge infrastructure
- Extend CI registry for tool type

### Phase 2: Claude Code Integration (Week 2)
- Implement Claude Code adapter
- Test socket communication
- Integrate with aish commands

### Phase 3: Additional Tools (Week 3)
- Add Cursor adapter
- Add Continue adapter
- Standardize capability discovery

### Phase 4: Advanced Features (Week 4)
- Implement session management
- Add Apollo-Rhetor integration
- Enable Terma attachments

## Benefits

1. **Unified Interface**: All CI tools accessible through aish
2. **Automation**: Programmatic control of development tools
3. **Context Sharing**: CI tools benefit from Tekton's context system
4. **Cost Efficiency**: Leverage subscription models (Claude Max, etc.)
5. **Extensibility**: Easy to add new CI tools

## Future Enhancements

1. **Multi-Tool Orchestration**: Coordinate multiple CI tools for complex tasks
2. **Tool Capability Registry**: Dynamic discovery of tool features
3. **Session Persistence**: Save and restore CI tool sessions
4. **Collaborative Mode**: Multiple users sharing CI tool sessions
5. **Performance Optimization**: Intelligent routing based on tool strengths

## Conclusion

The CI Tools integration extends Tekton's "CIs are sockets" philosophy to external development tools, creating a unified interface for all forms of coding intelligence. This architecture maintains simplicity while enabling powerful automation and integration capabilities.