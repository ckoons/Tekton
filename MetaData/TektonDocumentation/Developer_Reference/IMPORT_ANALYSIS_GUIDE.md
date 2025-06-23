# Import Analysis and Correction Process

This guide documents the tools and processes for maintaining clean import patterns across the Tekton codebase.

## Overview

Tekton provides two scripts for periodic import health checks:
1. **tekton_import_analyzer.py** - Identifies import issues
2. **tekton_import_fixer.py** - Interactively fixes identified issues

These tools should be run quarterly or after major development sprints to maintain code quality.

## Import Analysis Tool

### Purpose
The analyzer identifies:
- Circular dependencies between modules
- Star imports (`from X import *`)
- Deep import chains (5+ levels)
- Missing or broken imports
- Flattening opportunities (frequently imported items)

### Usage
```bash
# Show help
python scripts/tekton_import_analyzer.py --help

# Analyze all components
python scripts/tekton_import_analyzer.py --all

# Analyze specific components
python scripts/tekton_import_analyzer.py Engram Prometheus Hermes
```

### Output
- **import_analysis_report.md** - Human-readable markdown report
- **import_analysis_results.json** - Machine-readable data for the fixer tool

### Example Report
```markdown
## Engram
### Star Imports (2)
- Engram/engram/core/__init__.py:8
  - `from .models import *`

### Deep Imports (depth ≥ 5) (12)
- `from engram.core.memory.storage.backend.implementations import FileBackend` (used in 8 files)

### Top Flattening Candidates
- **MemoryService** from `engram.core.memory` (imported 14 times)
```

## Import Fixer Tool

### Purpose
The fixer provides interactive fixes for:
- Converting star imports to explicit imports
- Adding frequently imported items to `__init__.py` for easier access
- Showing suggestions for breaking circular dependencies

### Usage
```bash
# Show help
python scripts/tekton_import_fixer.py --help

# Run interactive fixer (after running analyzer)
python scripts/tekton_import_fixer.py

# Run without backups (not recommended)
python scripts/tekton_import_fixer.py --no-backup
```

### Interactive Options
- **y** = yes, fix this issue
- **n** = no, skip this issue
- **s** = skip all remaining in this category
- **a** = auto-fix all similar issues (where available)
- **q** = quit

### Safety Features
- Automatic backups created in `.import_fixes_backup/`
- Shows changes before applying
- Provides summary of all modifications

## Workflow

### 1. Run Analysis
```bash
cd /Users/cskoons/projects/github/Tekton
python scripts/tekton_import_analyzer.py --all
```

### 2. Review Report
```bash
# View the generated report
cat import_analysis_report.md

# Look for:
# - Components with many deep imports
# - Star imports that should be explicit
# - Circular dependencies that need breaking
```

### 3. Run Fixer
```bash
python scripts/tekton_import_fixer.py

# Example interaction:
# === Star Imports in Prometheus ===
# [1/2] prometheus/core/mcp/__init__.py:8
#   from .tools import *
# Fix this star import? (y/n/s/a): y
#   ✓ Fixed: from .tools import planning_tool, get_plan_tool
```

### 4. Test Changes
Always test components after import changes:
```bash
# Test individual component
cd Prometheus
python -m prometheus

# Or use Tekton launcher
python scripts/enhanced_tekton_launcher.py
```

### 5. Commit Changes
If all tests pass:
```bash
git add -A
git commit -m "fix: Clean up imports based on analysis

- Fixed star imports in Prometheus and Metis
- Flattened frequently imported items
- No functional changes"
```

## Best Practices

### Import Organization
```python
# Standard import order for all modules
# 1. Standard library
import os
import sys
from typing import Dict, List

# 2. Third-party libraries
import fastapi
from pydantic import BaseModel

# 3. Tekton shared utilities
from shared.utils.logging_setup import setup_component_logging
from tekton.utils.port_config import get_component_port

# 4. Component-specific imports
from .core import Engine
from .models import Entity
```

### Avoiding Issues

1. **No Star Imports**
   ```python
   # Bad
   from .models import *
   
   # Good
   from .models import User, Task, Project
   ```

2. **Reasonable Import Depth**
   ```python
   # Bad (depth 5+)
   from component.core.subsystem.module.submodule.implementation import Thing
   
   # Good (depth 3 or less)
   from component.core import Thing
   ```

3. **No Circular Dependencies**
   ```python
   # Bad: A imports B, B imports A
   
   # Good: Use dependency injection or interfaces
   from .interfaces import ThingInterface
   ```

## Maintenance Schedule

### Quarterly Review
Run the analysis tool every 3 months:
1. After major feature development
2. Before release cycles
3. When onboarding new developers

### Sprint Reviews
Run after development sprints that:
- Add new components
- Refactor existing components
- Merge large feature branches

### Metrics to Track
- Total star imports (goal: 0)
- Average import depth (goal: <4)
- Circular dependencies (goal: 0)
- Components with 20+ deep imports (goal: 0)

## Troubleshooting

### Common Issues

1. **Fixer can't determine star import replacements**
   - Manually specify the imports needed
   - Check the module's `__all__` definition

2. **Circular dependency suggestions don't work**
   - Consider extracting shared interfaces
   - Use dependency injection patterns
   - Move shared code to a common module

3. **Import changes break tests**
   - Ensure all imports are explicit
   - Check for namespace conflicts
   - Verify virtual environments are correct

### Getting Help
- Review this guide
- Check component-specific documentation
- Ask in development channels

## Integration with CI/CD

Consider adding import checks to CI:
```yaml
# .github/workflows/import-check.yml
- name: Check imports
  run: |
    python scripts/tekton_import_analyzer.py --all
    # Fail if issues found
    if grep -q "star imports\|circular dependencies" import_analysis_report.md; then
      exit 1
    fi
```