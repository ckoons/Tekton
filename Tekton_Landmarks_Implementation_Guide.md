# Tekton Landmarks Implementation Guide

## Overview
This guide provides a systematic approach to adding landmarks to the remaining ~240 backend files across Tekton components.

## Current Coverage Status
- **Total Coverage**: ~20% (60 of 300+ files)
- **Components with Basic Coverage**: All 17 components
- **Components Needing Most Work**: Apollo, Athena, Engram, Ergon, Hermes (30-40 files each)

## Implementation Priority

### Tier 1 - Critical Components (High Priority)
These components are central to Tekton's operation and should be prioritized:

1. **Apollo** (~20 files) - Conversational AI orchestration
   - `api/app.py` - Main API application
   - `core/apollo_component.py` - Component class
   - `core/apollo_manager.py` - Manager class
   - `core/message_handler.py` - Message handling
   - `core/predictive_engine.py` - Predictions
   - `core/context_observer.py` - Context tracking

2. **Hermes** (~40 files) - Message bus & service discovery
   - `api/a2a_endpoints.py` - Agent-to-agent communication
   - `api/mcp_endpoints.py` - MCP integration
   - `core/message_bus.py` - Core messaging
   - `core/registration.py` - Service registration
   - Database adapters (5 files)

3. **Ergon** (~30 files) - Agent orchestration
   - `core/agents/*.py` - Agent implementations
   - `core/flow/*.py` - Workflow management
   - `core/database/*.py` - Persistence layer

### Tier 2 - Core Data & Processing (Medium Priority)
4. **Engram** (~20 files) - Memory management
5. **Athena** (~30 files) - Knowledge graph
6. **Rhetor** (~20 files) - AI response generation
7. **Budget** (~15 files) - Token/resource management

### Tier 3 - Supporting Components (Lower Priority)
8. **Synthesis** (~15 files) - Decision making
9. **Prometheus** (~10 files) - Global state
10. **Telos** (~20 files) - Goal tracking
11. **Metis** (~15 files) - Task management
12. **Harmonia** (~15 files) - Workflow engine
13. **Sophia** (~15 files) - API management
14. **Noesis** (~15 files) - Insight engine
15. **Terma** (~10 files) - Terminal interface
16. **Numa** (~6 files) - Monitoring
17. **Codex** (unknown) - Code assistant

## Landmark Patterns by File Type

### 1. API Application Files (`api/app.py`, `__main__.py`)
```python
@architecture_decision(
    title="Component Service Architecture",
    rationale="Description of the component's role and design choices",
    alternatives_considered=["List alternatives"],
    decided_by="Casey"
)

@state_checkpoint(
    title="Component Service State",
    state_type="service",
    persistence=True/False,
    consistency_requirements="Description",
    recovery_strategy="How state is recovered"
)
```

### 2. Component Classes (`*_component.py`)
```python
@architecture_decision(
    title="Component Design",
    rationale="Core design philosophy",
    alternatives_considered=["Alternatives"],
    decided_by="Casey"
)

@state_checkpoint(
    title="Component State Management",
    state_type="component",
    persistence=True/False,
    consistency_requirements="State requirements",
    recovery_strategy="Recovery approach"
)
```

### 3. API Endpoints (`endpoints/*.py`, `routes.py`)
```python
@api_contract(
    title="Endpoint Name",
    endpoint="/api/path",
    method="GET/POST/etc",
    request_schema={"field": "type"},
    response_schema={"field": "type"}
)

@integration_point(
    title="Integration Name",
    target_component="Component name",
    protocol="HTTP/WebSocket/etc",
    data_flow="Source → Destination"
)
```

### 4. Core Engines/Managers
```python
@architecture_decision(
    title="Engine/Manager Architecture",
    rationale="Design rationale",
    alternatives_considered=["Alternatives"],
    decided_by="Casey"
)

@performance_boundary(
    title="Performance Constraint",
    sla="<Xms latency, Y throughput",
    optimization_notes="Optimization strategies",
    metrics={"metric": "value"}
)
```

### 5. Integration Points
```python
@integration_point(
    title="Integration Name",
    target_component="Target component",
    protocol="Protocol used",
    data_flow="Data flow description"
)
```

### 6. Dangerous Operations
```python
@danger_zone(
    title="Operation Name",
    risk_level="low/medium/high",
    risks=["List of risks"],
    mitigations=["Mitigation strategies"],
    review_required=True/False
)
```

## Implementation Process

### Step 1: Import Landmarks
Add to the top of each file:
```python
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        api_contract,
        state_checkpoint,
        performance_boundary,
        danger_zone
    )
except ImportError:
    # Define no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    # ... repeat for other decorators
```

### Step 2: Analyze File Purpose
Before adding landmarks, understand:
- What is the file's primary responsibility?
- What architectural decisions were made?
- What integrations exist?
- What state is managed?
- What are the performance constraints?
- What operations are risky?

### Step 3: Apply Appropriate Landmarks
- Classes: Usually need `@architecture_decision` and often `@state_checkpoint`
- API endpoints: Need `@api_contract` and often `@integration_point`
- Dangerous operations: Need `@danger_zone`
- Performance-critical code: Need `@performance_boundary`

### Step 4: Document Key Information
Each landmark should capture:
- **Title**: Clear, descriptive name
- **Rationale**: Why this approach was chosen
- **Alternatives**: What other approaches were considered
- **Risks/Mitigations**: For dangerous operations
- **Performance Targets**: For performance-critical code

## Batch Implementation Strategy

### Week 1: Critical Infrastructure (Tier 1)
- Apollo: 5 files/day = 4 days
- Hermes: 8 files/day = 5 days
- Ergon: 6 files/day = 5 days

### Week 2: Core Data Layer (Tier 2)
- Engram: 5 files/day = 4 days
- Athena: 6 files/day = 5 days
- Rhetor: 4 files/day = 5 days

### Week 3: Supporting Components (Tier 3)
- Remaining 10 components: ~100 files total
- 20 files/day = 5 days

## Quality Checklist
For each file with landmarks:
- [ ] Imports are correct with try/except fallback
- [ ] At least one landmark on main class/function
- [ ] API endpoints have `@api_contract`
- [ ] Integrations have `@integration_point`
- [ ] Dangerous operations have `@danger_zone`
- [ ] Performance-critical code has `@performance_boundary`
- [ ] Landmarks provide useful navigation/documentation

## Testing Landmarks
After adding landmarks:
1. Ensure the file still runs without the landmarks package
2. Verify decorators don't break functionality
3. Check that landmark information is accurate
4. Test that the component still starts/operates normally

## Next Steps
1. Start with Tier 1 components (Apollo, Hermes, Ergon)
2. Focus on main entry points and API files first
3. Work through core classes and engines
4. Add to integration and utility files last
5. Update this guide with lessons learned