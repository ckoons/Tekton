# Centralized Configuration for Tekton

This document describes the centralized configuration system for Tekton components, eliminating duplication and providing a single source of truth.

## Configuration Files

### 1. Component Definitions
**File**: `/config/tekton_components.yaml`
- Complete definition of all Tekton components
- Includes metadata: name, port, description, category
- Defines startup priorities and dependencies
- Specifies component capabilities

### 2. Port Assignments
**File**: `/config/port_assignments.md`
- Markdown table of port assignments
- Environment variable names
- Used by `port_config.py` module

## Python Modules

### 1. Component Configuration
**Module**: `tekton.utils.component_config`
- Reads from `tekton_components.yaml`
- Provides `ComponentInfo` and `ServiceInfo` classes
- Functions to query components by various criteria
- Dependency validation
- Startup order calculation

### 2. Port Configuration
**Module**: `tekton.utils.port_config`
- Reads from `port_assignments.md`
- Provides port lookup functions
- Environment variable override support
- Legacy compatibility functions

## Usage Examples

### In Python Scripts
```python
from tekton.utils.component_config import get_component_config
from tekton.utils.port_config import get_component_port

# Get all components
config = get_component_config()
components = config.get_all_components()

# Get specific component info
rhetor = config.get_component('rhetor')
print(f"{rhetor.name} runs on port {rhetor.port}")

# Get port for a component
port = get_component_port('hermes')
```

### In Status Scripts
The `tekton-status.py` script now uses the centralized configuration:
- No hardcoded component lists
- Automatically includes new components
- Shows proper component names and descriptions
- Validates component names against configuration

## Benefits

1. **Single Source of Truth**: All component information in one place
2. **Easy Maintenance**: Add/modify components in one YAML file
3. **Validation**: Automatic dependency checking
4. **Consistency**: Same component names and ports everywhere
5. **Extensibility**: Easy to add new metadata fields
6. **Type Safety**: Python dataclasses provide type hints

## Component Categories

- **infrastructure**: Core system components (tekton_core, hermes)
- **memory**: Memory and storage (engram)
- **knowledge**: Knowledge management (athena)
- **ai**: AI and intelligence (rhetor, sophia, apollo)
- **planning**: Planning and requirements (prometheus, telos, metis)
- **workflow**: Workflow management (harmonia)
- **execution**: Code execution (synthesis, ergon)
- **resources**: Resource management (budget)
- **ui**: User interfaces (hephaestus, terma)

## Adding New Components

1. Add entry to `/config/tekton_components.yaml`:
```yaml
components:
  new_component:
    name: "New Component"
    port: 8015
    description: "Description of the component"
    category: "appropriate_category"
    startup_priority: 3
    dependencies: ["hermes"]
    capabilities: ["capability1", "capability2"]
```

2. The component will automatically be:
   - Included in status checks
   - Available in launch scripts
   - Validated for dependencies
   - Properly ordered for startup

## Future Enhancements

1. **Configuration Validation**: Schema validation for YAML file
2. **Dynamic Reloading**: Hot-reload configuration changes
3. **Component Templates**: Standard templates for new components
4. **Health Check Standards**: Define health check requirements
5. **API Versioning**: Track API versions per component