# Component Management Guide

This guide explains how to add, modify, and manage Tekton components using the centralized configuration system.

## Overview

Tekton uses a centralized configuration system to eliminate duplication and ensure consistency across all tools and scripts. All component information is stored in two primary files:

1. **`/config/tekton_components.yaml`** - Component definitions and metadata
2. **`/config/port_assignments.md`** - Port assignments and environment variables

## Adding a New Component

### Step 1: Add to tekton_components.yaml

Add your component to `/config/tekton_components.yaml`:

```yaml
components:
  my_component:  # Internal ID (lowercase, underscore separated)
    name: "My Component"  # Display name
    port: 8015  # Unique port number
    description: "Brief description of what the component does"
    category: "appropriate_category"  # See categories below
    startup_priority: 3  # 0-5, lower starts first
    dependencies: ["hermes", "engram"]  # Components this depends on
    capabilities:  # Optional: list of capabilities
      - "capability1"
      - "capability2"
```

Available categories:
- `infrastructure` - Core system components
- `memory` - Memory and storage systems
- `knowledge` - Knowledge management
- `ai` - AI and intelligence services
- `planning` - Planning and requirements
- `workflow` - Workflow management
- `execution` - Code execution
- `resources` - Resource management
- `ui` - User interfaces

### Step 2: Update port_assignments.md

Add your component to `/config/port_assignments.md`:

```markdown
| My Component   | 8015 | Brief description                         | `MY_COMPONENT_PORT`    |
```

### Step 3: Component is Automatically Available

Once added to these files, your component:
- Appears in `tekton-status.py` output
- Can be launched with `tekton-launch`
- Is validated for dependencies
- Appears in the correct startup order

## Modifying Existing Components

### Changing Port Numbers

1. Update the port in `/config/tekton_components.yaml`
2. Update the port in `/config/port_assignments.md`
3. No code changes needed - all tools use the configuration

### Adding Dependencies

1. Add to the `dependencies` list in `/config/tekton_components.yaml`
2. Dependencies are automatically validated
3. Startup order is recalculated

### Changing Startup Priority

1. Update `startup_priority` in `/config/tekton_components.yaml`
2. Components are grouped by priority (0 starts first)
3. Within a priority group, components start in parallel

## Using the Configuration in Code

### Python Scripts

```python
# Import the configuration modules
from tekton.utils.component_config import get_component_config
from tekton.utils.port_config import get_component_port

# Get component information
config = get_component_config()
rhetor = config.get_component('rhetor')
print(f"{rhetor.name} runs on port {rhetor.port}")

# Get all components in a category
ai_components = config.get_components_by_category('ai')

# Get startup order
startup_groups = config.get_startup_order()
for priority, components in enumerate(startup_groups):
    print(f"Priority {priority}: {', '.join(components)}")

# Get port for a component
port = get_component_port('hermes')
```

### In Component Code

Components should use the configuration for their own ports:

```python
from tekton.utils.port_config import get_component_port

# Get this component's port
PORT = get_component_port('my_component')

# Or with environment variable override
PORT = int(os.environ.get('MY_COMPONENT_PORT', get_component_port('my_component')))
```

## Validation

The configuration system provides automatic validation:

```python
from tekton.utils.component_config import get_component_config

config = get_component_config()
errors = config.validate_dependencies()
if errors:
    for error in errors:
        print(f"Error: {error}")
```

## Best Practices

1. **Use Meaningful IDs**: Component IDs should be lowercase with underscores
2. **Clear Descriptions**: Write descriptions that explain what the component does
3. **Proper Categories**: Choose the most appropriate category
4. **Minimal Dependencies**: Only list direct dependencies
5. **Startup Priority**: Use the lowest priority that works

## Startup Priority Guidelines

- **0**: Core infrastructure (tekton_core)
- **1**: Service registry (hermes)
- **2**: Memory systems (engram)
- **3**: Base services (athena, rhetor, telos, budget)
- **4**: Higher-level services (sophia, apollo, harmonia, etc.)
- **5**: UI and user-facing services (hephaestus, terma, synthesis)

## Troubleshooting

### Component Not Appearing

1. Check YAML syntax in `/config/tekton_components.yaml`
2. Ensure the component ID uses underscores, not hyphens
3. Verify the port is unique

### Dependency Errors

1. Run validation to see specific errors
2. Check that all dependencies exist
3. Ensure no circular dependencies

### Port Conflicts

1. Check both configuration files for the port
2. Ensure no other component uses the same port
3. Check if the port is available on your system

## Examples

### Adding a New ML Component

```yaml
components:
  neural_net:
    name: "Neural Network Service"
    port: 8016
    description: "Deep learning model inference service"
    category: "ai"
    startup_priority: 4
    dependencies: ["hermes", "sophia"]
    capabilities:
      - "image_classification"
      - "text_generation"
      - "embedding_generation"
```

### Adding a New Tool Component

```yaml
components:
  code_analyzer:
    name: "Code Analyzer"
    port: 8017
    description: "Static code analysis and metrics"
    category: "execution"
    startup_priority: 4
    dependencies: ["hermes", "athena"]
    capabilities:
      - "complexity_analysis"
      - "dependency_mapping"
      - "security_scanning"
```

## Future Enhancements

The configuration system is designed to be extensible:

1. **Schema Validation**: Add JSON Schema for YAML validation
2. **Hot Reloading**: Components detect configuration changes
3. **Version Management**: Track component API versions
4. **Feature Flags**: Enable/disable capabilities dynamically
5. **Resource Requirements**: Specify CPU/memory needs