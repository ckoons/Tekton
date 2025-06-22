# Tekton Landmarks System

## Overview

The Tekton Landmarks System provides persistent architectural memory for Companion Intelligences (CIs) like Numa. It allows developers to mark important decisions, boundaries, and integration points directly in code, creating a living knowledge base that CIs can access across sessions.

## Quick Start

### Installation

```python
# Add to your component's imports
from landmarks import (
    architecture_decision,
    performance_boundary,
    api_contract,
    danger_zone,
    integration_point,
    state_checkpoint
)
```

### Basic Usage

```python
# Mark an architectural decision
@architecture_decision(
    title="Use AsyncIO for concurrency",
    rationale="Need to handle 1000+ concurrent connections",
    alternatives_considered=["threading", "multiprocessing"],
    impacts=["performance", "complexity"],
    decided_by="Casey"
)
async def setup_server():
    """Initialize the async server"""
    pass

# Mark a performance boundary
@performance_boundary(
    title="Message processing",
    sla="<50ms per message",
    optimization_notes="Uses batching and async I/O"
)
async def process_messages(messages):
    """Process incoming messages efficiently"""
    pass

# Mark an API contract
@api_contract(
    title="Component Registration",
    endpoint="/api/register",
    method="POST",
    request_schema={"name": "string", "capabilities": ["string"]},
    response_schema={"id": "string", "status": "string"}
)
async def register_component(request):
    """Register a new component"""
    pass
```

## Landmark Types

### 1. Architecture Decision
Documents why architectural choices were made.

```python
@architecture_decision(
    title="Brief decision title",
    rationale="Why this approach was chosen",
    alternatives_considered=["option1", "option2"],
    impacts=["affected_areas"],
    decided_by="decision_maker"
)
```

### 2. Performance Boundary
Marks performance-critical code sections.

```python
@performance_boundary(
    title="What this boundary protects",
    sla="Performance requirement (e.g., <100ms)",
    optimization_notes="Optimizations applied",
    metrics={"metric": "value"}
)
```

### 3. API Contract
Documents API endpoints and their contracts.

```python
@api_contract(
    title="Endpoint purpose",
    endpoint="/api/path",
    method="GET|POST|PUT|DELETE",
    request_schema={...},
    response_schema={...},
    auth_required=True|False
)
```

### 4. Danger Zone
Marks complex or risky code that needs careful handling.

```python
@danger_zone(
    title="What makes this dangerous",
    risk_level="low|medium|high",
    risks=["specific_risks"],
    mitigation="How risks are mitigated",
    review_required=True|False
)
```

### 5. Integration Point
Marks where components connect.

```python
@integration_point(
    title="Integration purpose",
    target_component="ComponentName",
    protocol="WebSocket|REST|MCP",
    data_flow="Description of data flow"
)
```

### 6. State Checkpoint
Marks important state management points.

```python
@state_checkpoint(
    title="State description",
    state_type="singleton|cache|session",
    persistence=True|False,
    consistency_requirements="Requirements",
    recovery_strategy="How to recover"
)
```

## CI Memory System

The landmark system includes persistent memory for CIs:

```python
from landmarks.memory.ci_memory import NumaMemory

# Initialize Numa's memory
numa = NumaMemory()

# Remember something
numa.remember("key", "value", category="decisions")

# Recall it later (even in different session)
value = numa.recall("key", category="decisions")

# Search landmarks
results = numa.search_landmarks("websocket")

# Get component expertise
hermes_landmarks = numa.get_landmarks_for_component("Hermes")
```

## Querying Landmarks

### From Python Code

```python
from landmarks import LandmarkRegistry

# List all landmarks
all_landmarks = LandmarkRegistry.list()

# Filter by type
decisions = LandmarkRegistry.list(type="architecture_decision")

# Filter by component
hermes_landmarks = LandmarkRegistry.list(component="Hermes")

# Search landmarks
results = LandmarkRegistry.search("websocket")

# Get landmark by ID
landmark = LandmarkRegistry.get(landmark_id)

# Get landmarks near a code location
nearby = LandmarkRegistry.get_by_location(
    file_path="hermes/server.py",
    line_number=150,
    tolerance=20  # Within 20 lines
)
```

### From CLI (Coming Soon)

```bash
# List all landmarks
tekton landmark list

# Search landmarks
tekton landmark search "websocket"

# Add landmark via CLI
tekton landmark add --type=decision --title="..." --file=path.py --line=45
```

## Best Practices

### DO:
- ✅ Mark major architectural decisions
- ✅ Document performance boundaries and SLAs
- ✅ Mark all API contracts
- ✅ Identify integration points between components
- ✅ Flag dangerous or complex code sections
- ✅ Keep descriptions concise but complete
- ✅ Include rationale for decisions

### DON'T:
- ❌ Over-landmark trivial code
- ❌ Duplicate information already in code
- ❌ Create landmarks for temporary code
- ❌ Use landmarks as TODO markers
- ❌ Include sensitive information

## Storage

Landmarks are stored in:
- `/landmarks/data/` - Individual landmark JSON files
- `/ci_memory/{ci_name}/` - CI-specific memories
- `registry.json` - Central index for fast lookup

## Integration with Numa

Numa uses landmarks to:
1. Understand architectural decisions across sessions
2. Know performance boundaries when suggesting changes
3. Respect API contracts when modifying code
4. Navigate complex code sections carefully
5. Coordinate between components effectively

## Examples

See `/landmarks/examples/` for complete examples:
- `landmark_example.py` - Basic usage patterns
- More examples coming soon...

## Contributing

When adding new landmark types:
1. Define the type in `core/landmark.py`
2. Add decorator in `core/decorators.py`
3. Update documentation
4. Add tests

## Future Enhancements

- [ ] Semantic search using embeddings
- [ ] Landmark versioning and history
- [ ] Visual landmark browser
- [ ] IDE integration
- [ ] Automated landmark suggestions

---

*The Tekton Landmarks System transforms code into a living knowledge base, enabling CIs to truly understand and remember the system they work with.*