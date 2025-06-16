# GlobalConfig Sprint - Initial Implementation Prompt

## Context

You are Working Claude, tasked with implementing the GlobalConfig system for Tekton. This sprint aims to replace scattered global variables across all Tekton components with a unified, centralized configuration object.

## Current Situation

Currently, Tekton components use multiple global variables:
```python
# Example from Rhetor
llm_client = None
rhetor_port = None
is_registered_with_hermes = False
start_time = None
# ... many more
```

This pattern is repeated across all components, leading to maintenance issues and bugs.

## Your Task

Implement a GlobalConfig system that:

1. **Creates a GlobalConfig class** in `shared/utils/global_config.py` that:
   - Holds all component configuration in one place
   - Is initialized once at startup
   - Provides easy access to configuration values
   - Supports component-specific sections
   - Includes debug instrumentation

2. **Updates all Tekton components** to use GlobalConfig:
   - Start with Rhetor (has known issues)
   - Systematically update each component
   - Maintain all existing functionality
   - Remove individual global variables

3. **Ensures quality**:
   - Add comprehensive tests
   - Include debug instrumentation per guidelines
   - Document usage patterns
   - Maintain backward compatibility

## Technical Requirements

### GlobalConfig Class Design

```python
class GlobalConfig:
    """Centralized configuration for Tekton components."""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.config = get_component_config()  # Existing config loader
        self.port = None
        self.version = None
        self.is_registered = False
        self.start_time = None
        self.services = {}  # Store service instances
        # ... other common fields
    
    def get_service(self, name: str):
        """Get a service instance by name."""
        return self.services.get(name)
    
    def set_service(self, name: str, instance):
        """Register a service instance."""
        self.services[name] = instance
```

### Component Update Pattern

Each component's app.py should change from:
```python
# Multiple globals
llm_client = None
port = None
is_registered = False

async def lifespan(app: FastAPI):
    global llm_client, port, is_registered
    # ... initialization
```

To:
```python
# Single global
config = None

async def lifespan(app: FastAPI):
    global config
    config = GlobalConfig("component_name")
    # ... initialization using config
```

## Implementation Order

1. Create GlobalConfig class with tests
2. Update Rhetor (pilot component)
3. Verify Rhetor works correctly
4. Update remaining components in order:
   - Apollo
   - Hermes
   - Budget
   - Telos
   - Others...

## Debug Instrumentation

Follow the [Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md):
- Add debug_log calls for configuration loading
- Use @log_function decorators for key methods
- Include component name in all debug output

## Testing Requirements

1. Unit tests for GlobalConfig class
2. Integration tests for each migrated component
3. System tests to ensure no regressions

## Success Criteria

- All components use GlobalConfig
- No individual configuration globals remain
- All existing functionality preserved
- All tests pass
- Debug instrumentation included

## Notes

- Maintain backward compatibility during migration
- Each component can be migrated independently
- Focus on correctness over speed
- Document any decisions or trade-offs

Begin by creating the GlobalConfig class and migrating Rhetor as the pilot implementation.