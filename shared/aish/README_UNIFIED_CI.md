# Unified CI System for aish

## Overview

The Unified CI System provides a single, consistent interface for communicating with all types of Companion Intelligences in Tekton. This replaces the previous approach of having separate code paths for different CI types.

## Key Features

1. **Single Registry**: All CIs (Greek Chorus, Terminals, Projects) in one place
2. **Configuration-Driven**: Each CI specifies how it wants to be contacted
3. **Extensible**: Easy to add new CI types or communication protocols
4. **Federation-Ready**: Designed to support cross-Tekton communication

## Quick Start

### List all CIs
```bash
aish list
```

### Send a message to any CI
```bash
# Greek Chorus AI
aish numa "Hello"

# Terminal
aish sandi "Can you help?"

# Project CI
aish myproject "Status?"
```

### Filter lists
```bash
aish list type terminal
aish list type greek
aish list json
```

## Architecture

### Registry Structure

Each CI in the registry has:
```json
{
    "name": "numa",
    "type": "greek",
    "host": "localhost",
    "port": 8316,
    "endpoint": "http://localhost:8316",
    "message_endpoint": "/rhetor/socket",
    "message_format": "rhetor_socket",
    "description": "Companion AI"
}
```

### Message Formats

- `rhetor_socket`: Greek Chorus CIs via Rhetor
- `terma_route`: Terminal-to-terminal messaging
- `json_simple`: Direct JSON API calls
- Custom formats can be added

### File Structure

```
shared/aish/
├── src/
│   ├── registry/
│   │   └── ci_registry.py      # Unified registry
│   ├── core/
│   │   └── unified_sender.py   # Message routing
│   └── commands/
│       └── list.py             # List command handler
└── tests/
    ├── test_unified.py         # Unit tests
    └── test_unified.sh         # Functional tests
```

## Testing

Run tests:
```bash
# All unified tests
aish test unified

# Functional test script
./shared/aish/tests/test_unified.sh

# Python unit tests
python -m pytest shared/aish/tests/test_unified_ci.py
```

## Future Roadmap

### Phase 2: Self-Registration
CIs will register themselves with their preferred communication settings.

### Phase 3: Federation
Enable communication between different Tekton installations.

## Migration Notes

- All existing commands continue to work
- No changes needed to existing scripts
- New features available immediately

## See Also

- [Unified CI Architecture](../../MetaData/Documentation/unified_ci_architecture.md)
- [Tekton Federation Sprint](../../MetaData/DevelopmentSprints/tekton_federation.md)
- [aish Command Reference](../../MetaData/TektonDocumentation/AITraining/aish/COMMAND_REFERENCE.md)