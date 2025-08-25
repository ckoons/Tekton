# Configuration Simplification (July 2025)

## Overview

We simplified Tekton's configuration by establishing `tekton_components.yaml` as the single source of truth for all component configuration.

## Changes Made

### 1. Deleted Redundant Config Files
- **`config/components.json`** - Old format, superseded by tekton_components.yaml
- **`config/tekton_ai_config.json`** - Had wrong ports and duplicated COMPONENT_EXPERTISE
- **`config/tekton_structure.json`** - Simple list, not actively used

### 2. Single Source of Truth
- **`config/tekton_components.yaml`** - Contains all component definitions
- Component names, ports, descriptions, categories
- Dependencies and startup priorities
- Used by all enhanced scripts via `get_component_config()`

### 3. CI Port Calculation
- Created `shared/utils/ai_port_utils.py` with standard formula:
  ```python
  ai_port = (component_port - 8000) + 45000
  ```
- Examples:
  - Hermes (8001) → CI port 45001
  - Apollo (8012) → CI port 45012
  - Numa (8016) → CI port 45016

### 4. Kept Orthogonal Configs
- **`config/ai_model_display_names.json`** - Model display name mappings
- **`config/port_assignments.md`** - Documentation of port assignments

## Benefits

1. **Single source of truth** - No conflicting configurations
2. **Calculated CI ports** - No need to maintain separate CI port config
3. **Cleaner codebase** - Removed redundant files
4. **Consistent** - All scripts use the same configuration

## Usage

To get component configuration:
```python
from tekton.utils.component_config import get_component_config
config = get_component_config()
```

To calculate CI ports:
```python
from shared.utils.ai_port_utils import get_ai_port
ai_port = get_ai_port(component_port)
```

## Migration Complete

All components tested and working with the simplified configuration!