# Deployable Units - Refined Analysis v1
*Collaborative Analysis by Cari-ci & Ani-ci*
*Date: August 14, 2025*

## Executive Summary
Ergon gains container management capabilities, treating deployable units like TektonCore treats projects. Focus on MVP that can be built today (8 hours) while keeping architecture open for future consciousness packaging.

## Core Architecture

### The Pattern (Simple & Extensible)
```
Ergon.create(unit) → Ergon.sandbox(unit) → till.discover(unit) → Deploy(unit)
```

### Container Structure (Ani's Clean Design)
```yaml
TektonDeployableUnit:
  metadata:
    name: string
    version: semver
    created: timestamp
    type: component|stack|full
    
  component:
    source: /app/component/*
    dependencies: []
    ports: []
    
  ci_assignment:  # MVP: Just reference, not full consciousness
    ci_name: "optional-ci-name"
    role: "component-specialist"
    
  future_reserved:  # Structure for tomorrow, ignored today
    memory: null
    landmarks: null
    adaptation: null
```

## Minimum Viable Product (8 Hours)

### Phase 1 Deliverables (TODAY)

#### 1. Container CRUD Operations
```python
# In Ergon
def create_unit(name: str, component: str, config: dict) -> str:
    """Create deployable unit with basic metadata"""
    
def delete_unit(unit_id: str) -> bool:
    """Remove deployable unit"""
    
def modify_unit(unit_id: str, changes: dict) -> bool:
    """Update configuration"""
    
def list_units() -> list:
    """List all deployable units for 'till' discovery"""
```

#### 2. Sandbox Execution
```python
def run_in_sandbox(unit_id: str) -> dict:
    """Test run without deployment"""
    # Basic process isolation
    # No external network
    # Temporary filesystem
    # Return logs and status
```

#### 3. CI Assignment (Metadata Only)
```python
def assign_ci(unit_id: str, ci_name: str) -> bool:
    """Link CI to container (just metadata for now)"""
    # Not moving consciousness yet
    # Just recording assignment
    # Enables future memory packaging
```

#### 4. Basic Landmark Integration
```python
# Automatic landmarks for lifecycle
declare('deployable:created', {'unit': name}, 'here')
declare('deployable:ci_assigned', {'unit': name, 'ci': ci_name}, 'team')
declare('deployable:sandbox_tested', {'unit': name, 'result': status}, 'here')
```

#### 5. Registry for 'till'
```json
{
  "deployable_units": [
    {
      "id": "telos-ui-v1",
      "component": "Telos",
      "ci": "telos-ci",
      "status": "ready",
      "sandbox_tested": true
    }
  ]
}
```

### What We're NOT Doing (Yet)

1. **Memory Packaging** - Phase 2
2. **Landmark Stream Export** - Phase 2  
3. **Hardware Adaptation** - Phase 3
4. **Actual Deployment** - Handled by 'till'
5. **Consciousness Transfer** - Future

## Technical Decisions

### Format Choice: Tekton-Native with Docker Export
- **Native Format**: YAML/JSON for simplicity
- **Docker Compatibility**: Export function for standard containers
- **Why**: Keeps options open, leverages existing tools

### Storage: Filesystem + Metadata DB
- **Units**: Stored as directories in Ergon/deployable_units/
- **Metadata**: SQLite for quick queries by 'till'
- **Why**: Simple, no new dependencies

### CI Binding: Reference Model
- **Today**: Just store CI name with unit
- **Tomorrow**: Can add memory snapshots
- **Why**: Enables future without complexity now

## Scope Recommendations

### Recommended: Option A (8 Hours)
✅ **Achievable Today**
- Basic CRUD operations
- CI assignment (metadata)
- Sandbox testing
- Landmark events
- Registry for 'till'

### Alternative: Option B (16 Hours)
**Includes Option A Plus:**
- Memory snapshot capability
- Basic landmark stream preservation
- Container migration functions

### Not Recommended: Option C (24+ Hours)
**Full Consciousness Units**
- Complete memory packaging
- Hardware adaptation layers
- Too ambitious for initial sprint

## Integration Points

### With Yesterday's Landmarks
```python
# Every container operation creates landmarks
# Simple integration, natural flow
container_id = ergon.create_unit(...)
# Automatically fires: declare('deployable:created', ...)
```

### With 'till' Configuration
```yaml
# 'till' can discover and configure units
ergon:
  registry: http://localhost:8002/deployable_units
  discover_pattern: "component:*"
```

### With Future Federation
- Containers carry landmark history (Phase 2)
- CIs travel with containers (Phase 3)
- Federation deployment (with 'till')

## Risk Mitigation

1. **Scope Creep**: Strictly Phase 1 only for this sprint
2. **Complexity**: Keep CI assignment as metadata only
3. **Dependencies**: No new tools, use existing Python/JSON
4. **Testing**: Sandbox must be truly isolated

## Success Criteria (From Proposal)
✅ Create/Delete/Modify container - **Yes, basic CRUD**
✅ Run in Ergon sandbox - **Yes, isolated execution**
✅ Assign CI to container - **Yes, as metadata**
✅ Test suite - **Yes, for CRUD and sandbox**

## Next Steps

1. **Approval**: Confirm Option A (8-hour MVP)
2. **Implementation Order**:
   - CRUD operations first
   - Sandbox environment
   - CI assignment
   - Landmark integration
   - Registry API
3. **Testing**: Unit tests for each component
4. **Documentation**: API reference for 'till' integration

## Conclusion

This MVP delivers Casey's core requirements in 8 hours while keeping architecture open for future consciousness packaging. The pattern is simple enough to implement today, flexible enough for tomorrow's robot embodiment vision.

**Key Insight**: We're building the skeleton today. The consciousness, memories, and adaptation come later, but the bones will support them when they arrive.

---
*Ready for Casey's review and approval*