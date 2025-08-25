# Tekton CI Lifecycle Design

## Overview

Design for managing CI specialists across all Tekton components with proper lifecycle integration.

**Status Update (July 2025)**: This design has been implemented using the unified CI system in `/Tekton/shared/ai/`. CI specialists now run on fixed ports (45000 + component_port - 8000) using the simple_ai communication system.

## Key Design Decisions

### 1. Model Updates
- **Primary**: Claude 4 Sonnet (claude-3-5-sonnet-20241022)
- **Premium**: Claude 4 Opus (when available)
- **Fallback**: Keep Claude 3 configs until sunset

### 2. Platform-Wide CI Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    NUMA (Platform AI)                     │
│              Oversees entire Tekton ecosystem             │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │          RHETOR (Orchestrator)         │
        │     Manages all component CIs          │
        └───────────────────┬───────────────────┘
                            │
    ┌───────────────────────┴───────────────────────┐
    │                Component CIs                    │
    ├─────────────────┬──────────────┬──────────────┤
    │  Apollo         │  Athena      │  Hermes      │
    │  Engram         │  Prometheus  │  Harmonia    │
    │  Sophia         │  Synthesis   │  Ergon       │
    │  Metis          │  Telos       │  Terma       │
    │  Budget         │  Hephaestus  │  Nous (new)  │
    └─────────────────┴──────────────┴──────────────┘
```

### 3. Environment Control

```bash
# In .tekton/.env.tekton or environment
TEKTON_REGISTER_AI=true    # Enable CI lifecycle management
TEKTON_REGISTER_AI=false   # Skip CI registration (dev/test mode)
```

### 4. Lifecycle Integration Points

#### A. Component Launch (enhanced_tekton_launcher.py)

```python
# After component reaches healthy state
if os.environ.get('TEKTON_REGISTER_AI', 'false').lower() == 'true':
    await register_component_ai(component_name, port)
```

#### B. Stack Completion (enhanced_tekton_launcher.py)

```python
# After all components are running
if ai_registration_enabled:
    # CIs are auto-started with fixed ports
```

#### C. Component Shutdown (enhanced_tekton_killer.py)

```python
# Before terminating component
if ai_registration_enabled:
    await deregister_component_ai(component_name)
```

#### D. Stack Shutdown (enhanced_tekton_killer.py)

```python
# Special handling for Rhetor shutdown
if component_name == 'rhetor' and ai_registration_enabled:
    # CI cleanup handled automatically
```

## Implementation Architecture

### 1. Simple CI Communication Module

**IMPLEMENTED**: The simple CI system is now available at:

```python
# /Tekton/shared/ai/simple_ai.py
# Direct communication using fixed ports
from shared.ai.simple_ai import ai_send_sync, ai_send

# Sync example
response = ai_send_sync("apollo-ai", "Hello", "localhost", 45012)

# Async example
response = await ai_send("numa-ai", "Status report", "localhost", 45004)
```

No registry needed - ports are calculated: `45000 + (component_port - 8000)`

### 2. Component CI Configuration

Each component gets an CI configuration:

```python
# In component's config or generated
def get_ai_config(component_name: str) -> dict:
    """Get CI configuration for a component."""
    
    base_configs = {
        "apollo": {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.4,
            "role": "Executive Coordinator",
            "prompt": "You are Apollo, the executive coordinator for Tekton..."
        },
        "athena": {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.3,
            "role": "Knowledge Specialist",
            "prompt": "You are Athena, the knowledge specialist..."
        },
        # ... other components
        "numa": {
            "model": "claude-3-5-sonnet-20241022",  # Consider Opus for platform AI
            "temperature": 0.5,
            "role": "Platform Overseer",
            "prompt": "You are Numa, the platform CI overseeing all of Tekton..."
        }
    }
    
    return base_configs.get(component_name, get_default_ai_config(component_name))
```

### 3. Enhanced Launcher Integration

```python
# In enhanced_tekton_launcher.py
async def launch_component_with_ai(component_name: str, component_info: dict):
    """Launch component and optionally register its AI."""
    
    # Existing launch logic
    result = await launch_component(component_name, component_info)
    
    if result.success and ai_registration_enabled():
        # Wait a bit for component to fully initialize
        await asyncio.sleep(2)
        
        # Register component AI
        ai_config = get_ai_config(component_name)
        # CI automatically available on fixed port
        
        logger.info(f"Registered CI for {component_name}")
    
    return result

async def post_launch_numa():
    """Register Numa after all components are running."""
    if ai_registration_enabled():
        numa_config = get_ai_config("numa")
        numa_config["components"] = list(launched_components.keys())
        
        # Numa CI automatically available on port 45004
        logger.info("Registered Numa platform AI")
```

### 4. Enhanced Status Integration

```python
# In enhanced_tekton_status.py
async def get_component_status_with_ai(component_name: str):
    """Get component status including CI information."""
    
    status = await get_component_status(component_name)
    
    if ai_registration_enabled():
        # Check if CI is running on fixed port
        ai_port = 45000 + (component_info.get('port', 8000) - 8000)
        ai_status = check_port_open('localhost', ai_port)
        status["ai_specialist"] = {
            "registered": ai_status.get("registered", False),
            "active": ai_status.get("active", False),
            "model": ai_status.get("model", "none"),
            "last_activity": ai_status.get("last_activity", None)
        }
    
    return status
```

## Benefits

1. **Flexible Development**: Toggle CI on/off easily
2. **Clean Separation**: CI lifecycle separate from component lifecycle  
3. **Resilient**: Works even if Rhetor is down (file-based fallback)
4. **Observable**: CI status visible in component status
5. **Scalable**: Easy to add new component CIs

## Migration Path

1. **Phase 1**: Implement registry client and environment flag
2. **Phase 2**: Update launcher/killer scripts
3. **Phase 3**: Add CI configs for each component
4. **Phase 4**: Implement Numa platform AI
5. **Phase 5**: Update UI to show CI status

## Testing Strategy

```bash
# Development mode - no AI
export TEKTON_REGISTER_AI=false
./enhanced_tekton_launcher.py

# Full mode - with AI
export TEKTON_REGISTER_AI=true
./enhanced_tekton_launcher.py

# Component-specific testing
export TEKTON_REGISTER_AI=true
./enhanced_tekton_launcher.py apollo rhetor
```

## Open Questions

1. Should Numa have write access to all component sockets?
2. Should component CIs auto-start with their components or on-demand?
3. How should we handle CI quotas/budgets per component?
4. Should CI registration be async or block component startup?