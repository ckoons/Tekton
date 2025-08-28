# Memory System Activation Guide

## Activation Methods

There are three ways to activate the Memory Hooks System for Tekton CIs:

### Method 1: Manual Activation (Testing/Development)

```bash
# One-time activation for all CIs
python scripts/enable_ci_memory.py enable --all --save

# Activate for specific CI
python scripts/enable_ci_memory.py enable --ci ergon

# Check status
python scripts/enable_ci_memory.py status --verbose
```

### Method 2: Automatic Startup (Production)

Add to Tekton's main initialization file:

```python
# In Tekton's startup sequence (e.g., __main__.py or tekton.py)
import asyncio
from Rhetor.rhetor.core.memory_middleware.system_integration import initialize_tekton_memory

async def startup_sequence():
    # ... existing startup code ...
    
    # Initialize memory system for all CIs
    print("Initializing CI memory system...")
    memory_system = await initialize_tekton_memory()
    
    if memory_system:
        print(f"✓ Memory enabled for {len(memory_system.adapter.enabled_cis)} CIs")
    else:
        print("⚠ Memory system initialization failed (non-critical)")
    
    # ... rest of startup ...
```

### Method 3: Settings Integration (User Control)

Add to Settings UI or configuration:

```python
# In Settings handler (e.g., settings_manager.py)
class TektonSettings:
    def __init__(self):
        self.memory_settings = {
            'enabled': True,
            'auto_initialize': True,
            'training_mode': 'progressive',  # or 'manual'
            'sharing_level': 'team'  # 'private', 'team', or 'tribal'
        }
    
    async def toggle_memory_system(self, enabled: bool):
        """Enable/disable memory for all CIs."""
        from Rhetor.rhetor.core.memory_middleware.system_integration import TektonMemorySystem
        
        memory_system = TektonMemorySystem()
        memory_system.config['global']['enabled'] = enabled
        memory_system.save_config()
        
        if enabled:
            await memory_system.initialize_all_ci_memory()
            return "Memory system enabled"
        else:
            # Disable memory hooks
            for manager in memory_system.adapter.memory_managers.values():
                manager.hook_manager.toggle(False)
            return "Memory system disabled"
    
    def configure_ci_memory(self, ci_name: str, settings: dict):
        """Configure memory for specific CI."""
        from Rhetor.rhetor.core.memory_middleware.system_integration import TektonMemorySystem
        
        memory_system = TektonMemorySystem()
        memory_system.update_ci_config(ci_name, settings)
```

## Settings UI Integration

### Add to Settings Menu

```yaml
# settings_menu.yaml or equivalent
memory_settings:
  title: "CI Memory System"
  icon: "🧠"
  sections:
    - global:
        title: "Global Settings"
        options:
          - enabled:
              type: toggle
              label: "Enable Memory System"
              default: true
          - auto_initialize:
              type: toggle
              label: "Auto-initialize on Startup"
              default: true
          - consolidation_interval:
              type: number
              label: "Memory Consolidation (seconds)"
              default: 300
              min: 60
              max: 3600
    
    - training:
        title: "Training Settings"
        options:
          - default_stage:
              type: select
              label: "Default Training Stage"
              options: [explicit, shortened, minimal, occasional, autonomous]
              default: explicit
          - advancement_mode:
              type: select
              label: "Advancement Mode"
              options: [automatic, manual]
              default: automatic
    
    - privacy:
        title: "Privacy Settings"
        options:
          - default_sharing:
              type: select
              label: "Default Memory Sharing"
              options: [private, team, tribal]
              default: team
    
    - ci_specific:
        title: "Per-CI Settings"
        type: dynamic_list
        source: get_all_cis()
        template:
          - injection_style:
              type: select
              options: [natural, structured, minimal]
          - training_stage:
              type: select
              options: [explicit, shortened, minimal, occasional, autonomous]
          - enabled:
              type: toggle
```

### Command-Line Settings

```bash
# Add to tekton CLI
tekton config memory --enable
tekton config memory --disable
tekton config memory --status
tekton config memory --ci ergon --stage minimal
```

## Configuration File Locations

The memory system uses these configuration files:

1. **Main Config**: `~/.tekton/memory_config.yaml`
2. **Training Progress**: `~/.engram/training_progress.json`
3. **Memory Storage**: `~/.engram/[ci_name]/memories/`

## Environment Variables

Optional environment variables for override:

```bash
# Enable/disable globally
export TEKTON_MEMORY_ENABLED=true

# Set default training stage
export TEKTON_MEMORY_DEFAULT_STAGE=minimal

# Set memory consolidation interval (seconds)
export TEKTON_MEMORY_CONSOLIDATION=300

# Set default privacy level
export TEKTON_MEMORY_PRIVACY=team
```

## Integration Points

### Where to Add Activation

1. **Main Tekton Entry Point**
   - File: `Tekton/__main__.py` or `tekton.py`
   - Function: `main()` or `startup()`
   - Add: `await initialize_tekton_memory()`

2. **Component Initialization**
   - File: `Rhetor/rhetor/__init__.py`
   - Function: `initialize_rhetor()`
   - Add: Memory system initialization

3. **Settings Module**
   - File: `shared/settings/settings_manager.py` (or equivalent)
   - Add: Memory configuration section

4. **CI Registry**
   - File: `shared/aish/src/registry/ci_registry.py`
   - Add: Memory initialization on CI registration

## Activation Verification

To verify memory is activated:

```python
# In Python
from Rhetor.rhetor.core.memory_middleware.universal_adapter import get_universal_adapter

adapter = get_universal_adapter()
status = adapter.get_memory_status()
print(f"Memory enabled for: {list(adapter.enabled_cis)}")
```

```bash
# From command line
python -c "from Rhetor.rhetor.core.memory_middleware.universal_adapter import get_universal_adapter; print(get_universal_adapter().enabled_cis)"
```

## Startup Sequence

Recommended initialization order:

1. Load environment variables
2. Initialize CI Registry
3. **Initialize Memory System** ← Add here
4. Start CI handlers
5. Begin message processing

## Performance Considerations

- Memory initialization adds ~100-500ms to startup
- Each message adds <100ms for memory injection
- Extraction is async (non-blocking)
- Consolidation runs every 5 minutes (configurable)

## Rollback

To disable memory if issues occur:

```bash
# Disable immediately
echo "global:\n  enabled: false" > ~/.tekton/memory_config.yaml

# Or via script
python scripts/enable_ci_memory.py enable --all --save
# Then edit ~/.tekton/memory_config.yaml and set enabled: false
```

## Next Steps

1. **Add to Tekton startup** (Method 2 above)
2. **Create Settings UI** (if desired)
3. **Test with one CI first** (e.g., Ergon)
4. **Enable for all CIs** once validated
5. **Monitor metrics** for optimization