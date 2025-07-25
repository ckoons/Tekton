# Unified CI Architecture

## Overview

The Unified CI Architecture provides a single, consistent interface for communicating with all types of Companion Intelligences (CIs) in the Tekton ecosystem. This includes Greek Chorus AIs, Terma terminals, Project CIs, and future federated Tekton stacks.

## Core Principles

1. **Configuration-Driven**: Each CI carries its own communication preferences
2. **Protocol Agnostic**: Support for multiple messaging formats and protocols
3. **Federation Ready**: Designed to support cross-Tekton communication
4. **Simple Interface**: One command pattern for all CI types

## Architecture Components

### 1. Unified CI Registry (`src/registry/ci_registry.py`)

The central registry maintains information about all available CIs:

```python
{
    "name": "numa",
    "type": "greek",              # CI category
    "host": "localhost",
    "port": 8316,
    "endpoint": "http://localhost:8316",
    
    # Messaging configuration
    "message_endpoint": "/rhetor/socket",
    "message_format": "rhetor_socket",
    
    # Optional fields
    "headers": {},                # Custom headers if needed
    "description": "Companion AI",
    "forward_to": null,          # Forwarding destination
    "created": "2025-01-24T12:00:00Z",
    "last_seen": "2025-01-24T12:00:00Z"
}
```

### 2. Message Formats

The system supports multiple message formats:

- **`rhetor_socket`**: For Greek Chorus AIs communicating through Rhetor
- **`terma_route`**: For terminal-to-terminal messaging via Terma
- **`json_simple`**: Simple JSON API calls for direct communication
- **Custom formats**: Extensible for future protocols

### 3. Unified Sender (`src/core/unified_sender.py`)

A single function handles all CI communication:

```python
def send_to_ci(ci_name: str, message: str) -> bool:
    # Get CI configuration from registry
    # Format message according to CI preferences
    # Send to appropriate endpoint
    # Handle response based on format
```

## Usage

### Basic Commands

```bash
# List all CIs
aish list

# List specific types
aish list type terminal
aish list type greek
aish list type project

# JSON output
aish list json
aish list json terminal

# Send messages (works for any CI type)
aish numa "Hello"
aish sandi "Hi terminal"
aish project-ci "Status update"
```

### Registry API

```python
from registry.ci_registry import get_registry

registry = get_registry()

# Get CI by name
ci = registry.get_by_name('numa')

# Get all CIs of a type
terminals = registry.get_by_type('terminal')

# Get all CIs
all_cis = registry.get_all()
```

## Message Flow

1. User types: `aish <ci-name> "message"`
2. System looks up CI in unified registry
3. Registry provides endpoint and format information
4. Message is formatted according to CI's preference
5. Message is sent to appropriate endpoint
6. Response is handled based on expected format

## Benefits

1. **Simplicity**: One interface for all CI types
2. **Extensibility**: New CI types just need registry entries
3. **Maintainability**: No hardcoded routing logic
4. **Federation**: External Tekton stacks are just CIs with remote endpoints
5. **Discovery**: CIs can self-register their preferences

## Future Extensions

### Phase 2: Self-Registration

CIs will register themselves on startup:

```python
POST /api/registry/register
{
    "name": "my-ci",
    "type": "custom",
    "message_endpoint": "/api/v2/message",
    "message_format": "custom_json"
}
```

### Phase 3: Federation

Enable cross-Tekton communication:

```python
{
    "name": "tekton-west",
    "type": "tekton",
    "host": "tekton-west.company.com",
    "federation": {
        "shared_cis": ["numa-west", "apollo-west"],
        "mcp_endpoints": {
            "resources": "/mcp/resources",
            "tools": "/mcp/tools"
        }
    }
}
```

## Testing

Run the test suite:

```bash
# Unit tests
python -m pytest shared/aish/tests/test_unified_ci.py

# Functional tests
./shared/aish/tests/test_unified.sh

# Or via aish
aish test unified
```

## Migration Guide

### For Existing Code

The system maintains backward compatibility:
- `aish numa "message"` still works
- `aish terma broadcast` still works
- All existing commands function as before

### For New Features

Use the unified approach:
- Add new CIs to the registry with proper configuration
- Use `send_to_ci()` for all messaging
- Let configuration drive behavior, not code

## See Also

- [Tekton Federation Sprint](../DevelopmentSprints/tekton_federation.md)
- [aish Command Reference](../TektonDocumentation/AITraining/aish/COMMAND_REFERENCE.md)