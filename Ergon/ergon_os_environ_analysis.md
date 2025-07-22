# Ergon Backend Analysis: os.environ and Hardcoded URL Issues

## Summary of Issues Found

### 1. /Users/cskoons/projects/github/Tekton/Ergon/ergon/utils/tekton_integration.py

**Issues Found:**
- **Line 68**: `port_str = os.environ.get(env_var)`
- **Line 93**: `host = host or os.environ.get("TEKTON_HOST", "localhost")`
- **Line 176**: `"host": os.environ.get("TEKTON_HOST", "localhost"),`
- **Line 206**: `"host": os.environ.get("TEKTON_HOST", "localhost"),`

**Required Changes:**
```python
# Add import at top
from shared.utils.env_config import get_env

# Line 68 - Replace:
port_str = os.environ.get(env_var)
# With:
port_str = get_env(env_var)

# Line 93 - Replace:
host = host or os.environ.get("TEKTON_HOST", "localhost")
# With:
host = host or get_env("TEKTON_HOST", "localhost")

# Line 176 - Replace:
"host": os.environ.get("TEKTON_HOST", "localhost"),
# With:
"host": get_env("TEKTON_HOST", "localhost"),

# Line 206 - Replace:
"host": os.environ.get("TEKTON_HOST", "localhost"),
# With:
"host": get_env("TEKTON_HOST", "localhost"),
```

### 2. /Users/cskoons/projects/github/Tekton/Ergon/ergon/core/llm/rhetor_adapter.py

**Issues Found:**
- **Line 41**: `self.model_name = model_name or os.environ.get("RHETOR_DEFAULT_MODEL", "claude-3-sonnet-20240229")`
- **Line 44**: `self.rhetor_url = rhetor_url or os.environ.get("RHETOR_API_URL", tekton_url("rhetor", "/api"))`

**Required Changes:**
```python
# Add import at top
from shared.utils.env_config import get_env

# Line 41 - Replace:
self.model_name = model_name or os.environ.get("RHETOR_DEFAULT_MODEL", "claude-3-sonnet-20240229")
# With:
self.model_name = model_name or get_env("RHETOR_DEFAULT_MODEL", "claude-3-sonnet-20240229")

# Line 44 - Replace:
self.rhetor_url = rhetor_url or os.environ.get("RHETOR_API_URL", tekton_url("rhetor", "/api"))
# With:
self.rhetor_url = rhetor_url or get_env("RHETOR_API_URL", tekton_url("rhetor", "/api"))
```

### 3. /Users/cskoons/projects/github/Tekton/Ergon/ergon/utils/config/settings.py

**Issues Found:**
- **Lines 44-46**: Complex os.environ.get usage in Field default_factory
- **Lines 51-54**: Complex os.environ.get usage in Field default_factory 
- **Lines 55-58**: Complex os.environ.get usage in Field default_factory
- **Line 71**: Complex os.environ.get usage in Field default_factory
- **Line 107**: Direct os.environ assignment

**Required Changes:**
```python
# Add import at top
from shared.utils.env_config import get_env

# Lines 44-46 - Replace:
tekton_home: Path = Field(default_factory=lambda: Path(
    os.environ.get('TEKTON_DATA_DIR', 
                  os.path.join(os.environ.get('TEKTON_ROOT', Path.home()), '.tekton', 'data'))
))
# With:
tekton_home: Path = Field(default_factory=lambda: Path(
    get_env('TEKTON_DATA_DIR', 
           os.path.join(get_env('TEKTON_ROOT', str(Path.home())), '.tekton', 'data'))
))

# Lines 51-54 - Replace:
vector_db_path: str = Field(default_factory=lambda: str(Path(
    os.environ.get('TEKTON_DATA_DIR', 
                  os.path.join(os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton'), '.tekton', 'data'))
) / "vector_store"))
# With:
vector_db_path: str = Field(default_factory=lambda: str(Path(
    get_env('TEKTON_DATA_DIR', 
           os.path.join(get_env('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton'), '.tekton', 'data'))
) / "vector_store"))

# Lines 55-58 - Replace:
data_dir: str = Field(default_factory=lambda: str(Path(
    os.environ.get('TEKTON_DATA_DIR', 
                  os.path.join(os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton'), '.tekton', 'data'))
)))
# With:
data_dir: str = Field(default_factory=lambda: str(Path(
    get_env('TEKTON_DATA_DIR', 
           os.path.join(get_env('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton'), '.tekton', 'data'))
)))

# Line 71 - Replace:
config_path: Path = Field(default_factory=lambda: Path(os.environ.get('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')) / ".tekton" / "ergon")
# With:
config_path: Path = Field(default_factory=lambda: Path(get_env('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')) / ".tekton" / "ergon")

# Line 107 - This is a special case where we're setting an environment variable
# Consider using a different approach or documenting this as intentional
```

**Note**: Lines 53, 57 contain hardcoded path `/Users/cskoons/projects/github/Tekton` which should be replaced with a more dynamic approach.

### 4. /Users/cskoons/projects/github/Tekton/Ergon/ergon/core/a2a_client.py

**Issues Found:**
- **Line 77**: `hermes_host = os.environ.get("HERMES_HOST", "localhost")`
- **Line 79**: `hermes_port = config.hermes.port if hasattr(config, 'hermes') else int(os.environ.get("HERMES_PORT"))`
- **Line 108**: `return int(os.environ.get('ERGON_PORT'))`

**Required Changes:**
```python
# Add import at top
from shared.utils.env_config import get_env

# Line 77 - Replace:
hermes_host = os.environ.get("HERMES_HOST", "localhost")
# With:
hermes_host = get_env("HERMES_HOST", "localhost")

# Line 79 - Replace:
hermes_port = config.hermes.port if hasattr(config, 'hermes') else int(os.environ.get("HERMES_PORT"))
# With:
hermes_port = config.hermes.port if hasattr(config, 'hermes') else int(get_env("HERMES_PORT"))

# Line 108 - Replace:
return int(os.environ.get('ERGON_PORT'))
# With:
return int(get_env('ERGON_PORT'))
```

### 5. /Users/cskoons/projects/github/Tekton/Ergon/ergon/core/llm/adapter.py

**Issues Found:**
- **Line 56**: `rhetor_port = get_env("RHETOR_PORT", "8003")`
- **Line 60**: `self.adapter_url = adapter_url or get_env("LLM_ADAPTER_URL", default_adapter_url)`
- **Line 61**: `self.provider = provider or get_env("LLM_PROVIDER", "anthropic")`
- **Line 62**: `self.model = model or get_env("LLM_MODEL", "claude-3-haiku-20240307")`

**No Changes Required**: This file already uses `get_env` from tekton_llm_client correctly!

### 6. /Users/cskoons/projects/github/Tekton/Ergon/ergon/ui/utils/session.py

**Issues Found:**
- **Line 24**: `if os.environ.get("ERGON_AUTHENTICATION", "true").lower() == "false":`

**Required Changes:**
```python
# Add import at top (after adding Tekton root to path)
import sys
import os
# Add Tekton root to path
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)
from shared.utils.env_config import get_env

# Line 24 - Replace:
if os.environ.get("ERGON_AUTHENTICATION", "true").lower() == "false":
# With:
if get_env("ERGON_AUTHENTICATION", "true").lower() == "false":
```

### 7. /Users/cskoons/projects/github/Tekton/Ergon/ergon/ui/pages/auth.py

**Issues Found:**
- **Line 40**: `if os.environ.get("ERGON_AUTHENTICATION", "true").lower() == "false":`
- **Line 79**: `if os.environ.get("ERGON_AUTHENTICATION", "true").lower() == "false":`

**Required Changes:**
```python
# Add imports at top (after existing imports)
import sys
# Add Tekton root to path
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)
from shared.utils.env_config import get_env

# Line 40 - Replace:
if os.environ.get("ERGON_AUTHENTICATION", "true").lower() == "false":
# With:
if get_env("ERGON_AUTHENTICATION", "true").lower() == "false":

# Line 79 - Replace:
if os.environ.get("ERGON_AUTHENTICATION", "true").lower() == "false":
# With:
if get_env("ERGON_AUTHENTICATION", "true").lower() == "false":
```

### 8. /Users/cskoons/projects/github/Tekton/Ergon/ergon/ui/main.py

**Issues Found:**
- **Line 51**: `if os.environ.get("ERGON_AUTHENTICATION", "true").lower() == "true":`

**Required Changes:**
```python
# Add imports at top (after existing imports)
# Add Tekton root to path
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if tekton_root not in sys.path:
    sys.path.append(tekton_root)
from shared.utils.env_config import get_env

# Line 51 - Replace:
if os.environ.get("ERGON_AUTHENTICATION", "true").lower() == "true":
# With:
if get_env("ERGON_AUTHENTICATION", "true").lower() == "true":
```

### 9. /Users/cskoons/projects/github/Tekton/Ergon/ergon/core/mcp_client.py

**Issues Found:**
- **Line 68**: `hermes_host = os.environ.get("HERMES_HOST", "localhost")`
- **Line 70**: `hermes_port = config.hermes.port if hasattr(config, 'hermes') else int(os.environ.get("HERMES_PORT"))`

**Required Changes:**
```python
# Add import at top
from shared.utils.env_config import get_env

# Line 68 - Replace:
hermes_host = os.environ.get("HERMES_HOST", "localhost")
# With:
hermes_host = get_env("HERMES_HOST", "localhost")

# Line 70 - Replace:
hermes_port = config.hermes.port if hasattr(config, 'hermes') else int(os.environ.get("HERMES_PORT"))
# With:
hermes_port = config.hermes.port if hasattr(config, 'hermes') else int(get_env("HERMES_PORT"))
```

## Summary

Total issues found: 24 instances of os.environ usage across 9 files

### Key Patterns:
1. Most files already have the Tekton root added to sys.path, making it easy to import get_env
2. UI files (in ergon/ui/) need the Tekton root path added before importing get_env
3. One file (adapter.py) already uses get_env correctly from tekton_llm_client
4. Settings.py has one special case where it sets an environment variable (line 107)
5. Settings.py contains hardcoded paths that should be addressed

### No Hardcoded URLs Found
All the files use either:
- `tekton_url()` function from shared.urls
- Dynamic URL construction using host/port variables
- No hardcoded URLs were found in any of the analyzed files