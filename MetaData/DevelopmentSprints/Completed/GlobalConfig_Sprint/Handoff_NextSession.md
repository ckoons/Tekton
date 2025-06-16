# GlobalConfig Sprint - Handoff to Next Session

## Current State

The GlobalConfig sprint is progressing well. We have successfully implemented the core classes and migrated the first component (Prometheus).

## What's Been Done

1. **Core Implementation**
   - `GlobalConfig` class in `/shared/utils/global_config.py`
   - `StandardComponentBase` class in `/shared/utils/standard_component.py`
   - Both classes are tested and working

2. **First Component Migration**
   - Prometheus successfully migrated and tested
   - Pattern proven to work

## Migration Pattern for Next Component

### Step 1: Create Component Class
Create a file like `metis/core/metis_component.py`:

```python
from shared.utils.standard_component import StandardComponentBase

class MetisComponent(StandardComponentBase):
    def __init__(self):
        super().__init__(component_name="metis", version="0.1.0")
        # Component-specific attributes
    
    async def _component_specific_init(self):
        # Initialize component-specific services
        pass
    
    async def _component_specific_cleanup(self):
        # Cleanup component-specific resources
        pass
    
    def get_capabilities(self) -> List[str]:
        return ["task_management", "etc"]
    
    def get_metadata(self) -> Dict[str, Any]:
        return {"description": "Task management system"}
```

### Step 2: Update app.py
1. Import GlobalConfig instead of get_component_config
2. Create component instance
3. Use component.create_app() with startup_callback
4. Update health endpoint to use component.get_health_status()
5. Remove global variables and move to GlobalConfig

### Step 3: Update __main__.py
Replace os.environ.get("COMPONENT_PORT") with GlobalConfig.get_instance().config.component.port

### Step 4: Update client.py (if exists)
Use GlobalConfig.get_service_url() instead of hardcoded URLs

## Next Components Order

1. **Metis** - Task management (should be straightforward)
2. **Apollo** - Has latent reasoning like Prometheus
3. Then alphabetically: Athena, Budget, Ergon, Harmonia, Hephaestus, Sophia, Synthesis, Telos
4. Leave for last: Engram, Hermes, Rhetor (most complex)

## Important Notes

1. **NO os.environ for ports** - Always use GlobalConfig or env_config
2. **Latent reasoning is optional** - Components should work without it
3. **Test after each migration** - Use `python -m component_name`
4. **Check health endpoint** - Should return proper format

## Common Issues and Solutions

1. **TypeError: FastAPI() got multiple values for 'version'**
   - StandardComponentBase already handles this, should not occur

2. **Health check format error**
   - Use component.get_health_status() which returns correct format

3. **Latent reasoning errors**
   - Already fixed to be warnings, components work in standalone mode

## Commands for Testing

```bash
# Launch component
python -m metis

# Check status
tekton-status -c metis

# Kill if needed
tekton-kill -c metis
```

## Files to Reference

- `/shared/utils/global_config.py` - GlobalConfig implementation
- `/shared/utils/standard_component.py` - Base class implementation
- `/Prometheus/prometheus/core/prometheus_component.py` - Example component
- `/Prometheus/prometheus/api/app.py` - Example of migrated app.py

Good luck with the next components!