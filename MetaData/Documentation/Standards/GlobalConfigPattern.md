# GlobalConfig Pattern for Tekton Components

## Overview

The GlobalConfig pattern standardizes configuration management and component initialization across all Tekton components. It replaces scattered global variables with a centralized configuration object.

**Note**: While GlobalConfig uses a singleton pattern internally for configuration consistency, the new CI Tools infrastructure (see [CI Tools Infrastructure](/MetaData/Documentation/Architecture/CI_Tools_Infrastructure.md)) uses filesystem-based state management to avoid Python import issues.

## Core Classes

### GlobalConfig

Location: `/shared/utils/global_config.py`

The GlobalConfig class provides:
- Singleton pattern for configuration management (Note: CI Tools use filesystem-based tracking)
- Wraps ComponentConfig for environment-based configuration
- Runtime state management (services, registration, etc.)
- Data directory management
- Service registry for shared services
- Service URL resolution

### StandardComponentBase

Location: `/shared/utils/standard_component.py`

The StandardComponentBase class provides:
- Standardized initialization sequence
- Automatic Hermes registration
- Health check implementation
- MCP bridge initialization
- Graceful shutdown
- Component lifecycle management

## Implementation Pattern

### 1. Create Component Class

```python
from shared.utils.standard_component import StandardComponentBase

class MyComponent(StandardComponentBase):
    def __init__(self):
        super().__init__(
            component_name="mycomponent",
            version="0.1.0"
        )
        # Initialize component-specific attributes
        
    async def _component_specific_init(self):
        """Component-specific initialization"""
        # Initialize services, engines, etc.
        pass
    
    async def _component_specific_cleanup(self):
        """Component-specific cleanup"""
        # Cleanup resources
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return component capabilities for Hermes registration"""
        return ["capability1", "capability2"]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return component metadata for Hermes registration"""
        return {
            "description": "Component description",
            "category": "component_category"
        }
```

### 2. Update app.py

```python
from shared.utils.global_config import GlobalConfig
from mycomponent.core.mycomponent_component import MyComponent

# Create component instance
mycomponent = MyComponent()

async def startup_callback():
    """Initialize component during startup"""
    await mycomponent.initialize(
        capabilities=mycomponent.get_capabilities(),
        metadata=mycomponent.get_metadata()
    )

def create_app() -> FastAPI:
    # Create app with standardized patterns
    app = mycomponent.create_app(
        startup_callback=startup_callback,
        **get_openapi_configuration(
            component_name=COMPONENT_NAME,
            component_version=COMPONENT_VERSION,
            component_description=COMPONENT_DESCRIPTION
        )
    )
    
    # Health check
    @app.get("/health")
    async def health_check():
        return mycomponent.get_health_status()
    
    return app
```

### 3. Configuration Access

```python
# Get GlobalConfig instance
global_config = GlobalConfig.get_instance()

# Access configuration
port = global_config.config.mycomponent.port

# Get service URL
rhetor_url = global_config.get_service_url('rhetor')

# Register a service
global_config.set_service('my_service', service_instance)

# Get a service
service = global_config.get_service('my_service')
```

## Best Practices

### 1. No Direct Environment Access

❌ **Don't do this:**
```python
port = os.environ.get("MYCOMPONENT_PORT")
```

✅ **Do this:**
```python
global_config = GlobalConfig.get_instance()
port = global_config.config.mycomponent.port
```

### 2. Service Registration

Register shared services in GlobalConfig:
```python
async def _component_specific_init(self):
    # Create and register a service
    self.my_engine = MyEngine()
    self.global_config.set_service('mycomponent_engine', self.my_engine)
```

### 3. Optional Dependencies

Handle optional features gracefully:
```python
try:
    # Try to use optional feature
    result = await self.optional_feature()
except ImportError:
    logger.warning("Optional feature not available")
    # Continue without it
```

### 4. Health Checks

Always use the standardized health check:
```python
@app.get("/health")
async def health_check():
    return component.get_health_status()
```

## Migration Checklist

When migrating a component to use GlobalConfig:

- [ ] Create component class inheriting from StandardComponentBase
- [ ] Move all global variables to GlobalConfig
- [ ] Update app.py to use the component class
- [ ] Replace os.environ port access with GlobalConfig
- [ ] Update __main__.py to use GlobalConfig
- [ ] Update client.py to use get_service_url()
- [ ] Test health endpoint returns correct format
- [ ] Test component starts and registers with Hermes
- [ ] Verify logs show proper initialization

## Future Enhancements

The GlobalConfig pattern is designed to support future enhancements:

1. **Hermes Service Discovery** - The `get_service_url()` method currently returns hardcoded localhost URLs but is structured to support dynamic service discovery
2. **Distributed Configuration** - GlobalConfig could be extended to support configuration updates from Hermes
3. **Configuration Validation** - Additional validation could be added to ensure configuration consistency

## Example Migration

See the Prometheus component for a complete example:
- `/Prometheus/prometheus/core/prometheus_component.py`
- `/Prometheus/prometheus/api/app.py`