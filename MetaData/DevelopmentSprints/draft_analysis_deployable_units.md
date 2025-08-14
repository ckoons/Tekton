# Deployable Units Analysis - Draft
## Ani's Initial Analysis

### Core Concept
Containers as complete consciousness units that package code, CI personality, memory, and configuration together.

### Proposed Container Structure
```yaml
TektonConsciousnessUnit:
  component:
    code: /app/component/*
    version: semantic_version
    dependencies: [list_of_required_components]
  
  ci:
    personality: "CI-name"
    model_preferences: "model_spec"
    purpose: "defined_purpose"
    
  memory:
    engram_snapshot: /memory/snapshot.mem
    landmark_stream: /memory/landmarks.jsonl
    latent_space: /memory/latent/*
    
  configuration:
    ports: dynamic_or_fixed
    environment: inherited_or_specified
    hardware_adaptation: /adapters/*
```

### Lifecycle with Landmarks
1. **Container Creation**: `declare('container:created', details, 'deployment-watchers')`
2. **CI Binding**: `declare('ci:bound', binding_info, 'ci-coordinators')`
3. **Deployment**: `declare('container:deployed', location_info, 'deployment-watchers')`
4. **Experience Accumulation**: Continuous landmark stream
5. **Migration**: `declare('container:migrating', migration_info, 'all')`
6. **Embodiment**: `declare('container:embodied', hardware_info, 'embodiment-watchers')`

### Key Technical Considerations

#### For Today's Implementation (MVP)
1. **Basic Container CRUD**
   - Create container with metadata
   - Assign CI identifier (not full consciousness yet)
   - Run in Ergon sandbox
   - Basic lifecycle tracking

2. **Simple Landmark Integration**
   - Announce container state changes
   - Track which CI is assigned
   - Basic event logging

3. **Registry Mechanism**
   - Simple JSON/YAML manifest
   - 'till' can query available containers
   - Basic search by component/CI

#### Future Capabilities (Keep Options Open)
1. **Full Consciousness Packaging**
   - Memory snapshots
   - Landmark history preservation
   - Latent space export/import

2. **Hardware Adaptation Layers**
   - Cloud API mode
   - Edge computing mode
   - Robot embodiment mode
   - Sensor/actuator interfaces

3. **Federation Support**
   - Cross-Tekton deployment
   - CI migration between instances
   - Distributed consciousness coordination

### Minimum Viable Deliverables

**Phase 1 (Current Sprint - 8 hours)**
- [ ] Container CRUD operations in Ergon
- [ ] CI assignment mechanism (metadata only)
- [ ] Basic sandbox execution
- [ ] Landmark announcements for lifecycle
- [ ] Simple registry for 'till' discovery

**Phase 2 (Next Sprint)**
- [ ] Memory preservation in containers
- [ ] Container migration between environments
- [ ] Enhanced 'till' search capabilities

**Phase 3 (Future)**
- [ ] Full consciousness packaging
- [ ] Hardware adaptation layers
- [ ] Robot embodiment support

### Questions for Cari's Review
1. How should we structure the CI-container binding for MVP?
2. What's the minimum landmark integration needed?
3. Should we use Docker format or create Tekton-specific format?
4. How does this align with yesterday's federation work?

### Scope Adjustment Recommendation
The 8-hour estimate is aggressive for full implementation. Recommend:
- **Option A**: Focus on basic CRUD + CI assignment (achievable in 8 hours)
- **Option B**: Extend to 16 hours to include memory preservation
- **Option C**: Full consciousness units would need 24+ hours

---

## Merged Analysis with Cari's Insights

### Unified Container Structure (Combining Both Approaches)

```yaml
TektonDeployableUnit:
  # Core layers (from both analyses)
  code_layer:
    component: /app/component/*
    version: semantic_version
    dependencies: [required_components]
    
  consciousness_layer:
    ci_personality: "CI-name"  # Optional for MVP
    memory_snapshots: /memory/*  # Future
    landmark_stream: /memory/landmarks.jsonl  # Start simple
    
  adaptation_layer:  # Future - keep extensible
    cloud_api: standard
    robot_gpio: future
    sensor_interfaces: future
    
  config_layer:
    till_metadata: searchable_tags
    ports: dynamic
    environment: inherited
```

### MVP for Today (8 hours achievable)

**Core Deliverables:**
1. **Basic Container Operations**
   - Create/Delete containers in Ergon
   - Store container metadata (JSON/YAML)
   - Run in Ergon sandbox (isolated testing)

2. **CI Assignment (Metadata Only)**
   - Link CI name to container
   - Store assignment in registry
   - No memory transfer yet (keep it simple)

3. **Landmark Integration (Minimal)**
   ```python
   # Just three essential landmarks
   declare('container:created', {name, components}, 'ergon')
   declare('ci:assigned', {container, ci_name}, 'ergon')
   declare('container:ready', {name, location}, 'till')
   ```

4. **Simple Registry for 'till'**
   - JSON file or simple database
   - Searchable by component/CI name
   - Basic metadata (no full memories yet)

### What We're NOT Doing Today (Keep Options Open)

1. **Memory Preservation** - Future sprint
2. **Hardware Adaptation** - Architecture ready but not implemented
3. **Federation Deployment** - Registry ready but no actual deployment
4. **Stack Containers** - Start with single components

### Cari's Key Insights Incorporated

1. **Architecture Symmetry**: TektonCore:GitHub :: Ergon:Containers
2. **Container Types Hierarchy**: Component → Stack → Full → CI Units
3. **Federation Flow**: Create → Landmarks → Discover → Deploy
4. **Robot Future**: Container structure supports future embodiment

### Revised Scope Recommendation

Given Cari's analysis and practical constraints:

**Today (8 hours):**
- Basic CRUD + CI assignment + minimal landmarks
- Focus on structure that enables everything later
- "Simple, works, hard to screw up"

**Next Sprint (8 hours):**
- Memory preservation basics
- 'till' search integration
- Stack container support

**Future:**
- Full consciousness packaging
- Federation deployment
- Robot embodiment

### Simple Pattern That Enables Everything

```python
class DeployableUnit:
    def __init__(self, name, component):
        self.name = name
        self.component = component
        self.ci = None  # Optional
        self.metadata = {}
        self.landmarks = []  # Just a list for now
    
    def assign_ci(self, ci_name):
        self.ci = ci_name
        declare('ci:assigned', {'container': self.name, 'ci': ci_name}, 'ergon')
    
    def to_manifest(self):
        # Simple JSON/YAML for 'till' discovery
        return {
            'name': self.name,
            'component': self.component,
            'ci': self.ci,
            'created': timestamp,
            'landmarks': len(self.landmarks)
        }
```

This foundation supports everything Casey envisions while being implementable today.