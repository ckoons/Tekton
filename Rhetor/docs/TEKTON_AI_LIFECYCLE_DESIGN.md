# Tekton AI Lifecycle Design

## Overview

Design for managing AI specialists across all Tekton components with proper lifecycle integration.

## Key Design Decisions

### 1. Model Updates
- **Primary**: Claude 4 Sonnet (claude-3-5-sonnet-20241022)
- **Premium**: Claude 4 Opus (when available)
- **Fallback**: Keep Claude 3 configs until sunset

### 2. Platform-Wide AI Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    NUMA (Platform AI)                     │
│              Oversees entire Tekton ecosystem             │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │          RHETOR (Orchestrator)         │
        │     Manages all component AIs          │
        └───────────────────┬───────────────────┘
                            │
    ┌───────────────────────┴───────────────────────┐
    │                Component AIs                    │
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
TEKTON_REGISTER_AI=true    # Enable AI lifecycle management
TEKTON_REGISTER_AI=false   # Skip AI registration (dev/test mode)
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
    await register_numa_platform_ai()
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
    # Export AI registry state before Rhetor terminates
    await export_ai_registry_state()
```

## Implementation Architecture

### 1. Shared AI Registry Module

Create a shared module that doesn't require Rhetor to be running:

```python
# tekton/utils/ai_registry_client.py
class AIRegistryClient:
    """Client for AI registration that works independently of Rhetor."""
    
    def __init__(self):
        self.rhetor_url = "http://localhost:8003"
        self.registry_file = "$TEKTON_ROOT/.tekton/ai_registry.json"
    
    async def register_component_ai(self, component_name: str, config: dict):
        """Register AI for a component."""
        try:
            # Try Rhetor API first
            if await self._is_rhetor_available():
                return await self._register_via_api(component_name, config)
            else:
                # Fallback to file-based registration
                return await self._register_via_file(component_name, config)
        except Exception as e:
            logger.error(f"Failed to register AI for {component_name}: {e}")
    
    async def deregister_component_ai(self, component_name: str):
        """Deregister AI for a component."""
        # Similar dual approach
```

### 2. Component AI Configuration

Each component gets an AI configuration:

```python
# In component's config or generated
def get_ai_config(component_name: str) -> dict:
    """Get AI configuration for a component."""
    
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
            "prompt": "You are Numa, the platform AI overseeing all of Tekton..."
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
        await ai_registry_client.register_component_ai(component_name, ai_config)
        
        logger.info(f"Registered AI for {component_name}")
    
    return result

async def post_launch_numa():
    """Register Numa after all components are running."""
    if ai_registration_enabled():
        numa_config = get_ai_config("numa")
        numa_config["components"] = list(launched_components.keys())
        
        await ai_registry_client.register_component_ai("numa", numa_config)
        logger.info("Registered Numa platform AI")
```

### 4. Enhanced Status Integration

```python
# In enhanced_tekton_status.py
async def get_component_status_with_ai(component_name: str):
    """Get component status including AI information."""
    
    status = await get_component_status(component_name)
    
    if ai_registration_enabled():
        ai_status = await ai_registry_client.get_ai_status(component_name)
        status["ai_specialist"] = {
            "registered": ai_status.get("registered", False),
            "active": ai_status.get("active", False),
            "model": ai_status.get("model", "none"),
            "last_activity": ai_status.get("last_activity", None)
        }
    
    return status
```

## Benefits

1. **Flexible Development**: Toggle AI on/off easily
2. **Clean Separation**: AI lifecycle separate from component lifecycle  
3. **Resilient**: Works even if Rhetor is down (file-based fallback)
4. **Observable**: AI status visible in component status
5. **Scalable**: Easy to add new component AIs

## Migration Path

1. **Phase 1**: Implement registry client and environment flag
2. **Phase 2**: Update launcher/killer scripts
3. **Phase 3**: Add AI configs for each component
4. **Phase 4**: Implement Numa platform AI
5. **Phase 5**: Update UI to show AI status

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
2. Should component AIs auto-start with their components or on-demand?
3. How should we handle AI quotas/budgets per component?
4. Should AI registration be async or block component startup?