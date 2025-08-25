# Part 1: Backend Analysis Instructions

## Overview

This document guides the systematic analysis of the Tekton backend codebase. The goal is to understand the architecture deeply enough to know where landmarks should be placed.

## Analysis Framework

### 1. File Discovery and Parsing

```python
# Start with this structure
analysis_results = {
    "components": {},      # Component-level analysis
    "patterns": {},        # Architectural patterns
    "decisions": [],       # Architectural decisions found
    "boundaries": [],      # API/performance boundaries
    "danger_zones": [],    # Complex/risky code
    "dependencies": {},    # Import relationships
}
```

### 2. Component Analysis Order

Analyze in this order (core → periphery):

1. **Core Infrastructure**
   - `shared/` - Shared utilities and patterns
   - `config/` - Configuration management
   - `scripts/` - System scripts

2. **Message Bus & Communication**
   - `Hermes/` - Central message bus
   - WebSocket handlers
   - Event dispatching

3. **Data & State**
   - `Engram/` - Memory/storage system
   - `Athena/` - Knowledge graph
   - State management patterns

4. **CI Integration**
   - `Prometheus/` - LLM management
   - `Sophia/` - Research system
   - MCP implementations

5. **Orchestration**
   - `Apollo/` - Component orchestration
   - `Numa/` - CI system (if exists)
   - Service coordination

6. **UI & User Interaction**
   - `Hephaestus/` - UI backend
   - `Ergon/` - Terminal interface
   - API endpoints

## What to Look For

### Architectural Decisions

Look for comments, docstrings, or code that indicates "why":
```python
# LANDMARK: Chose WebSockets over REST for real-time updates
# Reason: Need <100ms latency for UI responsiveness
```

Signs of decisions:
- "We chose X over Y because..."
- "This approach was selected..."
- "Performance requirement..."
- Alternative implementations commented out
- Major refactoring points

### Performance Boundaries

Identify performance-critical code:
```python
# Performance-critical patterns to find:
- Caching decorators
- Async/await usage
- Connection pooling
- Batch processing
- Rate limiting
- Optimization comments
```

### API Contracts

Document all external interfaces:
- REST endpoints
- WebSocket message formats
- MCP tool definitions
- Inter-component protocols
- Database schemas

### Danger Zones

Complex or risky code that needs careful handling:
- Complex state machines
- Concurrency management
- Security boundaries
- Error recovery logic
- Resource cleanup

### Integration Points

Where components connect:
- Service registration
- Message subscriptions
- Shared resources
- Cross-component calls

## Analysis Tools

### 1. AST Parser Script

Create `analyze_backend.py`:
```python
import ast
import os
import json
from pathlib import Path
from typing import Dict, List, Any

class TektonAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.current_file = None
        self.classes = []
        self.functions = []
        self.decorators = []
        self.imports = []
        self.patterns = []
        
    def analyze_file(self, filepath: Path) -> Dict[str, Any]:
        self.current_file = filepath
        # Reset collections
        self.classes = []
        self.functions = []
        self.decorators = []
        self.imports = []
        
        with open(filepath, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
            
        self.visit(tree)
        
        return {
            "file": str(filepath),
            "classes": self.classes,
            "functions": self.functions,
            "decorators": self.decorators,
            "imports": self.imports,
            "patterns": self.identify_patterns(content)
        }
    
    def visit_ClassDef(self, node):
        self.classes.append({
            "name": node.name,
            "line": node.lineno,
            "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
            "decorators": [self.get_decorator_name(d) for d in node.decorator_list]
        })
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.functions.append({
            "name": node.name,
            "line": node.lineno,
            "async": isinstance(node, ast.AsyncFunctionDef),
            "decorators": [self.get_decorator_name(d) for d in node.decorator_list]
        })
        self.generic_visit(node)
    
    def identify_patterns(self, content: str) -> List[str]:
        patterns = []
        
        # FastAPI patterns
        if "@app." in content or "FastAPI()" in content:
            patterns.append("fastapi_endpoint")
            
        # WebSocket patterns
        if "websocket" in content.lower():
            patterns.append("websocket_handler")
            
        # MCP patterns
        if "@mcp_tool" in content or "mcp.tool" in content:
            patterns.append("mcp_implementation")
            
        # Async patterns
        if "async def" in content:
            patterns.append("async_implementation")
            
        # Caching patterns
        if "@cache" in content or "lru_cache" in content:
            patterns.append("caching")
            
        return patterns
```

### 2. Dependency Mapper

```python
def map_dependencies(root_path: Path) -> Dict[str, List[str]]:
    """Map import dependencies between modules"""
    dependencies = {}
    
    for py_file in root_path.rglob("*.py"):
        module_name = str(py_file.relative_to(root_path)).replace("/", ".").replace(".py", "")
        
        with open(py_file, 'r') as f:
            tree = ast.parse(f.read())
            
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
                    
        dependencies[module_name] = imports
    
    return dependencies
```

### 3. Pattern Extractor

Look for these specific patterns:

```python
PATTERNS_TO_FIND = {
    "singleton": ["_instance", "get_instance", "__new__"],
    "factory": ["create_", "build_", "factory"],
    "observer": ["subscribe", "notify", "dispatch"],
    "decorator": ["@", "wrapper", "functools.wraps"],
    "async_context": ["async with", "__aenter__", "__aexit__"],
    "error_boundary": ["try:", "except", "finally"],
    "resource_management": ["__enter__", "__exit__", "cleanup", "close"],
}
```

## Documentation Format

### Per-Component Analysis

Create a file for each major component:
```markdown
# Component: Hermes

## Overview
Central message bus for inter-component communication

## Architectural Decisions
1. **WebSocket over REST** (Line 45)
   - Reason: Real-time requirement
   - Trade-offs: Complexity vs latency

## API Boundaries
- WebSocket endpoint: `/ws`
- Message format: `{type: str, payload: dict}`

## Performance Considerations
- Connection pooling (Line 120)
- Message batching (Line 200)

## Danger Zones
- Concurrent connection handling (Line 300)
- Message ordering guarantees (Line 400)

## Integration Points
- All components connect here
- Service registry at startup
```

### Pattern Documentation

```markdown
# Architectural Patterns in Tekton

## Communication Patterns
1. **Pub/Sub via Hermes**
   - Used by: All components
   - Implementation: WebSocket + event dispatch

2. **Request/Response via MCP**
   - Used by: Tool implementations
   - Implementation: FastAPI + async handlers

## State Management
1. **Singleton Services**
   - Examples: Hermes, Engram
   - Pattern: `get_instance()` method

## Error Handling
1. **Graceful Degradation**
   - Examples: LLM fallbacks
   - Pattern: Try primary → fallback → error
```

## Output Structure

```
backend_analysis/
├── components/
│   ├── hermes_analysis.md
│   ├── engram_analysis.md
│   ├── prometheus_analysis.md
│   └── ...
├── patterns/
│   ├── communication_patterns.md
│   ├── state_patterns.md
│   └── error_patterns.md
├── landmark_locations.json    # Where to place landmarks
├── dependency_graph.json      # Import relationships
└── analysis_summary.md        # Executive summary
```

## Success Criteria for Part 1

- [ ] Every Python file analyzed
- [ ] All major patterns documented
- [ ] Architectural decisions identified
- [ ] Performance boundaries marked
- [ ] Danger zones cataloged
- [ ] Integration points mapped
- [ ] Clear landmark placement plan

## Transition to Part 2

Before moving to Part 2:
1. Review all analysis with Casey
2. Confirm landmark locations are comprehensive
3. Verify pattern understanding is correct
4. Document any open questions

The output of Part 1 directly drives Part 2 implementation!