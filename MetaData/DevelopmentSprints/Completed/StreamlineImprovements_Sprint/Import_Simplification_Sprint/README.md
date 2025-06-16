# Import Simplification Sprint

## Overview

This sprint simplifies and standardizes import patterns across Tekton, eliminating circular dependencies, reducing import complexity, and creating clear module boundaries. This work builds on the shared utilities and API consistency improvements.

## Current State

Import-related issues discovered during GoodLaunch debugging:
- **Phantom imports**: `tekton.utils.port_config` imported everywhere but doesn't exist
- Circular dependencies between modules
- Missing modules causing startup failures
- Inconsistent import patterns
- Deep import chains
- Unclear module boundaries
- Logging import issues causing component_id formatting errors (Sophia)

## Goals

1. **Eliminate Phantom Imports**: Create missing modules (tekton.utils.port_config)
2. **Eliminate Circular Dependencies**: Clean module hierarchy
3. **Fix Logging Imports**: Resolve component_id formatting issues
4. **Simplify Import Paths**: Shorter, clearer imports
5. **Standard Patterns**: Consistent import organization
6. **Clear Boundaries**: Well-defined module interfaces
7. **Import Performance**: Faster startup times

## Implementation Plan

### Phase 1: Dependency Analysis & Missing Module Creation (0.5 sessions)

- Map current import dependencies
- **PRIORITY**: Create missing `tekton.utils.port_config` module (affects 8+ components)
- Identify circular dependencies
- Document phantom imports across all components
- Fix logging import chains causing component_id errors
- Plan refactoring approach

### Phase 2: Core Refactoring (1 session)

Restructure modules to eliminate issues:
```
# Before: Deep, complex imports
from athena.core.engine.knowledge.graph.entities import Entity
from athena.api.endpoints.llm_integration import template_registry

# After: Clean, simple imports
from athena.core import Entity
from athena.api import get_template_registry
```

### Phase 3: Import Standards (1 session)

Create import utilities and patterns:
```python
# tekton/shared/imports.py
"""Import helpers and lazy loading utilities."""

class LazyImport:
    """Lazy import for heavy dependencies."""
    def __init__(self, module_path: str):
        self._module_path = module_path
        self._module = None
    
    def __getattr__(self, name):
        if self._module is None:
            self._module = importlib.import_module(self._module_path)
        return getattr(self._module, name)

# Usage
torch = LazyImport("torch")  # Only imported when actually used
```

### Phase 4: Component Updates (1.5 sessions)

Update all components with:
- Simplified imports
- Standard organization
- Lazy loading where appropriate
- Clear module boundaries

## Key Patterns

### 1. Import Organization
```python
# Standard import order for all modules
# 1. Standard library
import os
import sys
from typing import Dict, List, Optional

# 2. Third-party libraries
import fastapi
import pydantic
from sqlalchemy import create_engine

# 3. Tekton shared utilities
from tekton.shared.logging import setup_component_logger
from tekton.shared.errors import TektonError

# 4. Component-specific imports
from .core import Engine
from .models import Entity
```

### 2. Module Structure
```python
# Clear module boundaries with __init__.py exports
# athena/__init__.py
from .core import KnowledgeEngine
from .models import Entity, Relationship
from .api import create_app

__all__ = ["KnowledgeEngine", "Entity", "Relationship", "create_app"]

# Clean imports for users
from athena import KnowledgeEngine, Entity
```

### 3. Dependency Injection
```python
# Avoid circular dependencies with injection
# Instead of importing at module level
# from .engine import engine  # Circular!

# Use dependency injection
def get_engine() -> Engine:
    """Get or create engine instance."""
    if not hasattr(get_engine, "_instance"):
        get_engine._instance = Engine()
    return get_engine._instance
```

### 4. Import Guards
```python
# Guard against missing optional dependencies
try:
    from faiss import IndexFlatL2
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    IndexFlatL2 = None

def create_vector_store():
    if not HAS_FAISS:
        logger.warning("FAISS not available, using fallback")
        return FallbackVectorStore()
    return FAISSVectorStore()
```

### 5. Relative vs Absolute
```python
# Use relative imports within component
from .models import Entity  # Good for internal use
from .core import Engine

# Use absolute imports for cross-component
from tekton.shared.logging import logger  # Clear origin
from hermes.client import HermesClient
```

## Anti-Patterns to Fix

1. **Star Imports**
```python
# Bad
from athena.models import *

# Good
from athena.models import Entity, Relationship
```

2. **Deep Import Chains**
```python
# Bad
from athena.core.engine.knowledge.graph.entities.base import BaseEntity

# Good (with proper module exports)
from athena.core import BaseEntity
```

3. **Circular Dependencies**
```python
# Bad: A imports B, B imports A
# engine.py
from .models import Entity  # Models imports engine!

# Good: Use injection or interfaces
# engine.py
def get_entity_class():
    from .models import Entity
    return Entity
```

## Benefits

1. **Faster Startup**: Reduced import time
2. **Clearer Code**: Obvious dependencies
3. **Better Testing**: Easier to mock/isolate
4. **Maintainability**: Clear module boundaries
5. **Fewer Errors**: No circular dependencies

## Success Criteria

- [ ] Zero circular dependencies
- [ ] All imports follow standard pattern
- [ ] 50% reduction in import depth
- [ ] No missing module errors
- [ ] Documented module boundaries

## Timeline

Total effort: 4 sessions
- Dependency Analysis: 0.5 sessions
- Core Refactoring: 1 session
- Import Standards: 1 session
- Component Updates: 1.5 sessions