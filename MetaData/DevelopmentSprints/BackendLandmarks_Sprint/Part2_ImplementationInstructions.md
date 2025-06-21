# Part 2: Landmark Implementation Instructions

## Overview

Using the analysis from Part 1, implement the landmark system and instrument the backend. This creates the persistent memory layer for Companion Intelligences.

## Prerequisites

Before starting Part 2:
- [ ] Part 1 analysis complete
- [ ] Landmark locations identified
- [ ] Patterns documented
- [ ] Architecture understood

## Implementation Order

### Phase 1: Core Infrastructure (Days 1-2)

#### 1.1 Create Landmark System

Directory structure:
```
Tekton/
├── landmarks/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── landmark.py        # Landmark class
│   │   ├── registry.py        # Registry management
│   │   └── decorators.py      # Python decorators
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── file_store.py      # File-based storage
│   │   └── index.py           # Fast lookup index
│   └── tools/
│       ├── __init__.py
│       ├── cli.py             # CLI tools
│       └── analyzer.py        # Analysis tools
```

#### 1.2 Landmark Base Class

```python
# landmarks/core/landmark.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

@dataclass
class Landmark:
    """Base landmark class"""
    id: str
    type: str  # architecture_decision, performance_boundary, etc.
    title: str
    description: str
    file_path: str
    line_number: int
    timestamp: datetime
    author: str
    metadata: Dict[str, Any]
    
    @classmethod
    def create(cls, type: str, title: str, **kwargs) -> 'Landmark':
        """Factory method for creating landmarks"""
        return cls(
            id=str(uuid.uuid4()),
            type=type,
            title=title,
            timestamp=datetime.now(),
            **kwargs
        )
```

#### 1.3 Landmark Types

Based on Part 1 findings, create specific types:

```python
# landmarks/core/types.py
class ArchitectureDecision(Landmark):
    """Marks architectural decisions"""
    alternatives_considered: List[str]
    rationale: str
    impacts: List[str]
    
class PerformanceBoundary(Landmark):
    """Marks performance-critical code"""
    sla: str  # e.g., "<100ms response time"
    optimization_notes: str
    
class APIContract(Landmark):
    """Marks API boundaries"""
    endpoint: str
    method: str
    request_schema: Dict
    response_schema: Dict
    
class DangerZone(Landmark):
    """Marks complex/risky code"""
    risk_level: str  # high, medium, low
    mitigation: str
    
class IntegrationPoint(Landmark):
    """Marks where components connect"""
    source_component: str
    target_component: str
    protocol: str
```

#### 1.4 Decorator Implementation

```python
# landmarks/core/decorators.py
import functools
import inspect
from typing import Callable, Any

from .landmark import Landmark
from .registry import LandmarkRegistry

def landmark(type: str, title: str, **metadata):
    """Decorator for marking functions/classes with landmarks"""
    def decorator(func: Callable) -> Callable:
        # Get source info
        filepath = inspect.getfile(func)
        line_number = inspect.getsourcelines(func)[1]
        
        # Create landmark
        lm = Landmark.create(
            type=type,
            title=title,
            description=func.__doc__ or "",
            file_path=filepath,
            line_number=line_number,
            author=metadata.get('author', 'system'),
            metadata=metadata
        )
        
        # Register it
        LandmarkRegistry.register(lm)
        
        # Attach to function for runtime access
        func._landmark = lm
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
            
        return wrapper
    return decorator

# Specific decorators for each type
def architecture_decision(title: str, rationale: str, **kwargs):
    """Mark an architectural decision"""
    return landmark(
        type="architecture_decision",
        title=title,
        rationale=rationale,
        **kwargs
    )

def performance_boundary(title: str, sla: str, **kwargs):
    """Mark performance-critical code"""
    return landmark(
        type="performance_boundary",
        title=title,
        sla=sla,
        **kwargs
    )
```

### Phase 2: CI Memory System (Days 3-4)

#### 2.1 Memory Persistence

```python
# landmarks/memory/ci_memory.py
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class CIMemory:
    """Persistent memory for Companion Intelligences"""
    
    def __init__(self, ci_name: str):
        self.ci_name = ci_name
        self.memory_dir = Path(f"ci_memory/{ci_name}")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.memory_dir / "current_session.json"
        self.context_file = self.memory_dir / "context.json"
        self.working_memory = self.load_session()
        
    def remember(self, key: str, value: Any, category: str = "general"):
        """Store information in memory"""
        if category not in self.working_memory:
            self.working_memory[category] = {}
        self.working_memory[category][key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0
        }
        self.save_session()
        
    def recall(self, key: str, category: str = "general") -> Optional[Any]:
        """Retrieve from memory"""
        if category in self.working_memory and key in self.working_memory[category]:
            memory = self.working_memory[category][key]
            memory["access_count"] += 1
            memory["last_accessed"] = datetime.now().isoformat()
            self.save_session()
            return memory["value"]
        return None
        
    def search_landmarks(self, query: str) -> List[Landmark]:
        """Search landmarks relevant to query"""
        # Integration with landmark registry
        from ..core.registry import LandmarkRegistry
        return LandmarkRegistry.search(query)
```

#### 2.2 Multi-CI Coordination

```python
# landmarks/memory/ci_coordinator.py
from typing import Dict, List, Optional
import json

class CICoordinator:
    """Coordinates multiple CIs and their domains"""
    
    def __init__(self):
        self.registry = self.load_ci_registry()
        
    def load_ci_registry(self) -> Dict:
        """Load CI capabilities and domains"""
        return {
            "Numa": {
                "role": "project_overseer",
                "domains": ["architecture", "decisions", "coordination"],
                "capabilities": ["remember_decisions", "track_progress", "coordinate_cis"]
            },
            "Component_CIs": {
                "Hermes-CI": {"domain": "messaging", "capabilities": ["protocol_expert"]},
                "Engram-CI": {"domain": "memory", "capabilities": ["storage_expert"]},
                "Prometheus-CI": {"domain": "ai", "capabilities": ["llm_expert"]}
            }
        }
    
    def route_query(self, query: str) -> str:
        """Route query to appropriate CI based on domain"""
        # Simple keyword-based routing for now
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["architecture", "decision", "why"]):
            return "Numa"
        elif "message" in query_lower or "websocket" in query_lower:
            return "Hermes-CI"
        elif "memory" in query_lower or "storage" in query_lower:
            return "Engram-CI"
        elif "llm" in query_lower or "ai" in query_lower:
            return "Prometheus-CI"
        
        return "Numa"  # Default to overseer
```

### Phase 3: Landmark Placement (Days 5-6)

#### 3.1 Instrumentation Strategy

Based on Part 1 findings, systematically add landmarks:

1. **Start with Core Components**
   ```python
   # Example: Hermes WebSocket decision
   @architecture_decision(
       title="WebSocket for Real-time Communication",
       rationale="Need <100ms latency for UI updates",
       alternatives_considered=["REST polling", "Server-sent events"],
       decided_by="Casey",
       date="2024-03-15"
   )
   async def setup_websocket(self):
       """Initialize WebSocket connection handler"""
   ```

2. **Mark Performance Boundaries**
   ```python
   @performance_boundary(
       title="Message Processing Pipeline",
       sla="<50ms per message",
       optimization_notes="Uses async processing and batching"
   )
   async def process_messages(self, messages: List[Message]):
       """Process incoming messages efficiently"""
   ```

3. **Document API Contracts**
   ```python
   @api_contract(
       title="Component Registration",
       endpoint="/api/register",
       method="POST",
       request_schema={"name": "str", "capabilities": "list"},
       response_schema={"id": "str", "status": "str"}
   )
   async def register_component(self, request: RegisterRequest):
       """Register a new component with Hermes"""
   ```

#### 3.2 Placement Guidelines

- **One landmark per major decision** - Don't over-instrument
- **Focus on "why" not "what"** - Code shows what, landmarks show why
- **Include context** - Future readers need background
- **Link related landmarks** - Use `supersedes` and `related_to`

### Phase 4: Developer Tools (Days 7-8)

#### 4.1 CLI Implementation

```python
# landmarks/tools/cli.py
import click
from ..core.registry import LandmarkRegistry

@click.group()
def landmark():
    """Tekton landmark management"""
    pass

@landmark.command()
@click.option('--type', required=True, help='Landmark type')
@click.option('--title', required=True, help='Landmark title')
@click.option('--file', required=True, help='File to mark')
@click.option('--line', required=True, type=int, help='Line number')
def add(type, title, file, line):
    """Add a new landmark"""
    # Implementation
    
@landmark.command()
@click.option('--type', help='Filter by type')
@click.option('--component', help='Filter by component')
def list(type, component):
    """List landmarks"""
    landmarks = LandmarkRegistry.list(type=type, component=component)
    for lm in landmarks:
        click.echo(f"{lm.type}: {lm.title} ({lm.file_path}:{lm.line_number})")

@landmark.command()
@click.argument('query')
def search(query):
    """Search landmarks"""
    results = LandmarkRegistry.search(query)
    # Display results
```

#### 4.2 Integration with Existing Tools

Add to `tekton` CLI:
```bash
# New commands
tekton landmark add --type=decision --title="..."
tekton landmark list --component=hermes
tekton landmark search "websocket"

# CI interaction
tekton ci remember "The WebSocket decision was made because..."
tekton ci ask "Why did we choose async over threading?"
```

### Phase 5: Testing & Validation (Days 9-10)

#### 5.1 Test Landmark System

```python
# tests/test_landmarks.py
def test_landmark_creation():
    """Test creating and retrieving landmarks"""
    
def test_landmark_search():
    """Test searching landmarks"""
    
def test_ci_memory():
    """Test CI memory persistence"""
```

#### 5.2 Validate Coverage

Checklist:
- [ ] All major architectural decisions marked
- [ ] Performance boundaries identified
- [ ] API contracts documented
- [ ] Danger zones marked
- [ ] Integration points clear

## Success Criteria

### Infrastructure Success
- [ ] Landmark system operational
- [ ] Decorators working correctly
- [ ] Storage and retrieval fast
- [ ] CI memory persists

### Instrumentation Success
- [ ] 50+ meaningful landmarks placed
- [ ] All components have landmarks
- [ ] Patterns are documented
- [ ] Decisions are traceable

### Developer Experience Success
- [ ] CLI tools functional
- [ ] Landmarks easy to add
- [ ] Search works well
- [ ] CI interactions natural

## Common Issues and Solutions

### Issue: "Where should this landmark go?"
Solution: If you're asking, it probably deserves a landmark. Mark the decision point.

### Issue: "Too many landmarks cluttering code"
Solution: Focus on decisions and boundaries, not implementation details.

### Issue: "Landmark maintenance burden"
Solution: Landmarks are for permanent decisions. They shouldn't change often.

## Final Deliverables

1. **Working Landmark System**
   - Core infrastructure
   - Storage/retrieval
   - Developer tools

2. **Instrumented Backend**
   - All major decisions marked
   - Patterns documented
   - Knowledge preserved

3. **CI Memory System**
   - Persistence across sessions
   - Multi-CI coordination
   - Natural interaction

4. **Documentation**
   - How to use landmarks
   - CI interaction guide
   - Pattern catalog

## Handoff to Numa Sprint

This infrastructure enables Numa to:
- Remember architectural decisions
- Understand system evolution
- Maintain context across sessions
- Coordinate with other CIs
- Provide intelligent assistance

The backend is no longer just code - it's a living system with memory!