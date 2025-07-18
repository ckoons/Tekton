# Tekton Port Management Guide

## Overview

Tekton uses a Single Port Architecture where each component is assigned a specific port number. This guide explains how to properly manage port assignments across the Tekton ecosystem.

## Port Assignment Strategy

### Official Port Assignments

All port assignments are defined in a single source of truth:
```
/config/port_assignments.md
```

Current assignments:
- **8080** - Hephaestus UI (Web UI standard)
- **8000** - Engram (Memory system)
- **8001** - Hermes (Service registry & messaging)
- **8002** - Ergon (Agent system)
- **8003** - Rhetor (LLM management)
- **8004** - Terma (Terminal system)
- **8005** - Athena (Knowledge graph)
- **8006** - Prometheus (Planning system)
- **8007** - Harmonia (Workflow system)
- **8008** - Telos (Requirements system)
- **8009** - Synthesis (Execution engine)
- **8010** - Tekton Core (Core orchestration)
- **8011** - Metis (Task management)
- **8012** - Apollo (Attention/Prediction system)
- **8013** - Budget (Token/cost management)
- **8014** - Sophia (Machine learning system)

### Environment Variables

Each port has a corresponding environment variable:
- Pattern: `{COMPONENT_NAME}_PORT`
- Example: `RHETOR_PORT=8003`

## How to Add a New Component

1. **Update port_assignments.md**
   ```markdown
   | NewComponent   | 8015 | Description of component          | `NEWCOMPONENT_PORT`    |
   ```

2. **Set environment variable in launch scripts**
   ```bash
   export NEWCOMPONENT_PORT=8015
   ```

3. **Use centralized port configuration in code**
   ```python
   from tekton.utils.port_config import get_component_port
   port = get_component_port("newcomponent")
   ```

## How to Delete a Component

1. **Remove from port_assignments.md**
   - Delete the entire row for the component

2. **Remove environment variable references**
   - Search for `COMPONENT_PORT` in all shell scripts
   - Remove export statements

3. **Clean up any hardcoded references**
   - Search codebase for the port number
   - Remove or update as needed

## How to Modify Port Assignments

### ⚠️ WARNING: Changing ports requires careful coordination

1. **Update port_assignments.md**
   - Change the port number in the table
   
2. **Update all references**
   - Environment variables in scripts
   - Any configuration files
   - Documentation

3. **Coordinate with running systems**
   - Stop affected components
   - Update configurations
   - Restart components

## Best Practices

### ✅ DO:
1. **Always use the centralized port configuration**
   ```python
   from tekton.utils.port_config import get_component_port
   port = get_component_port("rhetor")
   ```

2. **Use environment variables in shell scripts**
   ```bash
   curl http://localhost:$RHETOR_PORT/health
   ```

3. **Keep port_assignments.md as the single source of truth**

### ❌ DON'T:
1. **Never hardcode port numbers**
   ```python
   # BAD
   port = 8003
   
   # GOOD
   port = get_component_port("rhetor")
   ```

2. **Never create component-specific port_config.py files**
   - Use the centralized `/tekton/utils/port_config.py`

3. **Never duplicate PORT_ASSIGNMENTS dictionaries**
   - All components should import from the central location

## Port Configuration API

The centralized port configuration provides these functions:

### get_component_port(component_id: str) -> int
Returns the port number for a component.
```python
port = get_component_port("rhetor")  # Returns 8003
```

### get_component_url(component_id: str, protocol: str = "http", path: str = "") -> str
Returns the full URL for a component.
```python
url = get_component_url("rhetor", path="/api/health")  
# Returns "http://localhost:8003/api/health"
```

### get_api_url(component_id: str, path: str = "") -> str
Returns the API URL for a component.
```python
url = get_api_url("rhetor", path="/llm/models")
# Returns "http://localhost:8003/api/llm/models"
```

### get_ws_url(component_id: str, path: str = "") -> str
Returns the WebSocket URL for a component.
```python
url = get_ws_url("rhetor")
# Returns "ws://localhost:8003/ws"
```

## Common Issues and Solutions

### Issue: Component can't find its port
**Solution**: Ensure the component is importing from the centralized location:
```python
from tekton.utils.port_config import get_component_port
```

### Issue: Port conflicts on launch
**Solution**: Check that no two components share the same port in port_assignments.md

### Issue: Hardcoded ports in tests
**Solution**: Update test scripts to use environment variables or the port configuration API

### Issue: Component using wrong port
**Solution**: 
1. Check `/config/port_assignments.md` for the correct port
2. Ensure the component's launch script exports the correct environment variable
3. Verify the component is reading from the correct environment variable

## Migration from Distributed to Centralized Ports

If you're updating an existing component:

1. **Delete** the component's `utils/port_config.py` file
2. **Update** all imports:
   ```python
   # Old
   from .utils.port_config import get_rhetor_port
   
   # New
   from tekton.utils.port_config import get_component_port
   ```
3. **Test** that the component still starts correctly

## Conclusion

Centralized port management ensures consistency across the Tekton ecosystem. By following these guidelines, you help maintain a robust and maintainable system where port assignments are clear, conflicts are avoided, and changes can be made safely.