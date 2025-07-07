# Tekton Home Directory References Report

This report documents all locations in the Tekton codebase where files/directories are being created in the user's home directory (~/.tekton, ~/.aish, ~/.terma) instead of using $TEKTON_ROOT.

## Summary

Found multiple files creating directories in the home directory:
- **ai_registry**: Created by AI launcher scripts
- **aish**: Created by aish history and forwarding 
- **bin**: Created by orphan cleanup scripts
- **logs**: Created by various components
- **terma**: Created by terminal launcher
- **data**: Created by multiple components

## Detailed Findings

### 1. AI Registry Directory (~/.tekton/ai_registry)

**Files creating this directory:**
- `/Rhetor/rhetor/api/app.py` - Line 227: `registry_path = Path.home() / '.tekton' / 'ai_registry' / 'platform_ai_registry.json'`
- `/shared/aish/launch_component_ai.py` - Lines 38, 53: Registry path using `Path.home() / '.tekton' / 'ai_registry'`
- `/shared/aish/cleanup_orphan_processes.py` - Line 91: Same pattern

### 2. AISH Directories (~/.aish, ~/.tekton/aish)

**Files creating these directories:**
- `/shared/aish/src/core/history.py` - Lines 41, 43, 234: 
  - `.aish_history` file
  - `.aish/sessions/` directory
- `/shared/aish/src/forwarding/forwarding_registry.py` - Line 25: `self.config_dir = Path.home() / '.tekton' / 'aish'`
- `/shared/aish/src/core/shell.py` - Line 50: `self.history_file = Path.home() / '.aish_history'`

### 3. Terma Directories (~/.tekton/terma, ~/.terma)

**Files creating these directories:**
- `/Terma/terma/core/terminal_launcher_impl.py` - Lines 114, 133: `shared_dir = Path.home() / ".tekton" / "terma"`
- `/Terma/terma/utils/config.py` - Line 54: `self.config_path = config_path or os.path.expanduser("~/.terma/config.json")`
- `/shared/aish/test_inbox_simple.py` - Line 41: `inbox_dir = Path.home() / '.tekton' / 'terma'`
- `/shared/aish/src/commands/terma.py` - Multiple lines using `os.path.expanduser("~/.tekton/terma/...")`

### 4. Logs Directory (~/.tekton/logs)

**Files creating this directory:**
- `/shared/aish/cleanup_orphan_processes.py` - Line 215: `log_path = Path.home() / '.tekton' / 'logs' / 'orphan_cleanup.log'`
- `/shared/utils/env_manager.py` - Line 132: Sets default `TEKTON_LOG_DIR` to `$TEKTON_ROOT/.tekton/logs`

### 5. Bin Directory (~/.tekton/bin)

**Files creating this directory:**
- `/shared/aish/cleanup_orphan_processes.py` - Line 244: `script_path = Path.home() / '.tekton' / 'bin' / 'cleanup_tekton_orphans.sh'`

### 6. Data Directory (~/.tekton/data)

**Pattern found in multiple files using:**
```python
os.path.join(os.environ.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')
```

**Files with this pattern:**
- `/Rhetor/rhetor/core/prompt_registry.py` - Line 263
- `/Rhetor/rhetor/core/context_manager.py`
- `/Rhetor/rhetor/core/template_manager.py`
- `/Rhetor/rhetor/utils/engram_helper.py`
- `/tekton-core/tekton/core/component_lifecycle/registry/core.py`
- `/Synthesis/synthesis/core/execution_engine.py`
- `/Apollo/apollo/core/*.py` - Multiple files
- `/Ergon/ergon/utils/config/settings.py` - Using `Path.home()` variant
- `/shared/utils/global_config.py` - Lines 91-92

### 7. Special Cases

**Hardcoded TEKTON_ROOT:**
- `/Ergon/scripts/tekton/startup.py` - Line 23: `TEKTON_ROOT = Path.home() / ".tekton"`

**Vector Store Paths:**
- `/tekton-core/tekton/core/storage/vector/*.py` - Multiple files using `~/.tekton/vector_store`
- `/tekton-core/tekton/core/storage/kv/json_store.py` - `~/.tekton/kv_stores`
- `/tekton-core/tekton/core/storage/graph/memory/store.py` - `~/.tekton/graph_stores`

**Startup Coordinator:**
- `/tekton-core/tekton/core/startup_coordinator.py` - Line 53: `self.data_dir = data_dir or os.path.expanduser("~/.tekton/startup")`
- `/tekton-core/tekton/core/startup_process.py` - Similar pattern

## Recommendations

1. **Use $TEKTON_ROOT consistently**: All paths should be relative to `$TEKTON_ROOT` instead of the home directory
2. **Update default paths**: Change from `os.path.expanduser('~')` to `os.environ.get('TEKTON_ROOT', '.')`
3. **Create a central path utility**: Consider creating a utility function that returns the correct base path for all Tekton data
4. **Update env_manager.py**: Ensure it sets all necessary directory environment variables

## Impact

These hardcoded paths are causing Tekton to create directories in the user's home directory instead of keeping everything contained within the project directory. This affects:
- Project portability
- Clean uninstallation
- Multiple Tekton installations
- User directory organization