# Single Environment Read Architecture

## Overview

The Single Environment Read architecture ensures that all Tekton components read environment configuration from a single, unified source. This solves the critical issue of environment variables being read from multiple unpredictable locations throughout the codebase.

## Problem Statement

Previously, Tekton had 714+ direct calls to `os.environ` scattered across the codebase. This created several issues:
- Environment configuration could be read at any time, leading to inconsistent state
- Module-level imports would read environment before proper setup
- Different components could see different environment states
- Testing and multi-instance support was extremely difficult

## Solution Architecture

### Core Components

#### 1. C Launcher (`tekton-clean-launch`)
A small C program that handles environment setup before Python starts:
- Loads environment files in the correct order
- Sets up the frozen environment state
- Passes control to Python scripts with properly configured environment
- Supports the `--coder` flag for multiple Tekton instances

#### 2. TektonEnviron System
Three Python classes that manage environment access:

**TektonEnvironLock** - Environment loader (only for main tekton script)
- Loads environment from multiple sources in order:
  1. Current os.environ
  2. ~/.env (user settings)
  3. $TEKTON_ROOT/.env.tekton (project settings)
  4. $TEKTON_ROOT/.env.local (local secrets)
- Sets `_TEKTON_ENV_FROZEN=1` marker
- Freezes the environment state

**TektonEnviron** - Read-only environment access (for all modules)
- Provides `get()`, `all()`, and `is_loaded()` methods
- Returns frozen environment state
- Logs attempts to modify environment
- Single source of truth for all configuration

**TektonEnvironUpdate** - Hidden updater (use with extreme caution)
- Allows controlled updates to frozen environment
- Not exposed in normal imports
- Logs all modifications

### Implementation Flow

1. **User runs `tekton` command**
   - C launcher parses arguments (including --coder flag)
   - Loads environment files in correct order
   - Sets _TEKTON_ENV_FROZEN=1
   - Executes Python script with frozen environment

2. **Python scripts check environment**
   ```python
   from shared.env import TektonEnviron
   if not TektonEnviron.is_loaded():
       # Subprocess with passed environment
       pass
   else:
       # Use frozen environment
       os.environ = TektonEnviron.all()
   ```

3. **All modules use TektonEnviron**
   ```python
   from shared.env import TektonEnviron
   port = TektonEnviron.get(f"{component}_PORT")
   ```

## Benefits

1. **Consistency**: All components see the same environment state
2. **Predictability**: Environment is loaded once at startup
3. **Multi-Instance Support**: Different Tekton instances can run simultaneously
4. **Testing**: Environment can be easily mocked/controlled
5. **Performance**: No repeated file I/O for environment loading

## Migration Path

To migrate existing code:

1. Replace direct `os.environ` calls:
   ```python
   # Old
   port = os.environ.get('HERMES_PORT', '8006')
   
   # New
   from shared.env import TektonEnviron
   port = TektonEnviron.get('HERMES_PORT', '8006')
   ```

2. Update module-level environment reads:
   ```python
   # Old (at module level)
   API_KEY = os.environ.get('API_KEY')
   
   # New
   from shared.env import TektonEnviron
   def get_api_key():
       return TektonEnviron.get('API_KEY')
   ```

3. Use TektonEnviron in configuration modules:
   ```python
   # In port_config.py, component_config.py, etc.
   from shared.env import TektonEnviron
   # Read all configuration from TektonEnviron
   ```

## Technical Details

### Environment Loading Order
1. System environment variables
2. User-level configuration (~/.env)
3. Project configuration ($TEKTON_ROOT/.env.tekton)
4. Local overrides ($TEKTON_ROOT/.env.local)

Each file overwrites values from previous sources.

### The _TEKTON_ENV_FROZEN Marker
This internal environment variable indicates that the environment has been properly loaded and frozen. It allows subprocesses to detect they're running with the frozen environment.

### C Launcher Architecture
Similar to Git, Docker, and other tools, Tekton uses a compiled launcher to:
- Avoid Python import timing issues
- Handle environment setup in a clean room
- Parse command-line arguments before Python starts
- Support multiple instances via --coder flag

## Usage Examples

### Running Different Instances
```bash
# Main Tekton instance (ports 8000-8080)
tekton status

# Coder-A instance (ports 7000-7080)  
tekton --coder a status

# Coder-B instance (ports 6000-6080)
tekton --coder b start
```

### Checking Environment in Scripts
```python
#!/usr/bin/env python3
from shared.env import TektonEnviron

if not TektonEnviron.is_loaded():
    print("Please run this script via the 'tekton' command")
    sys.exit(1)

# Now safe to use environment
port = TektonEnviron.get('HERMES_PORT')
```

## Future Improvements

1. Identify and fix remaining module-level environment reads
2. Add environment validation on load
3. Support for environment variable type conversion
4. Enhanced debugging for environment issues