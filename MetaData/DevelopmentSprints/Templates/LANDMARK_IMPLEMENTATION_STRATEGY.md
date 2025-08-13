# Landmark Implementation Strategy
*Careful design by Cari & Tess for Casey - August 13, 2025*

## Core Philosophy
"Drop breadcrumbs automatically at moments we KNOW are landmarks, let CIs add meaning"

## Critical Design Principles

1. **Non-invasive** - Landmarks enhance, never obstruct
2. **Lightweight** - Minimal performance impact
3. **Discoverable** - CIs naturally notice them
4. **Extensible** - Easy to add new landmark types
5. **Reversible** - Can be disabled without breaking anything

## Automatic Capture Points

### Level 1: Essential (Must Have)
These are the moments we NEVER want to miss:

```python
# State Transitions
@landmark_on_transition
def change_status(self, from_state, to_state):
    # Auto-drops: @landmark:state_transition {from: X, to: Y}
    pass

# File Creation in Key Directories  
@landmark_on_file_create(dirs=["Proposals/", "Sprints/"])
def save_proposal(self, data):
    # Auto-drops: @landmark:proposal_created {name: X}
    pass

# API Calls Between Components
@landmark_on_api_call
async def call_hermes(self, endpoint, data):
    # Auto-drops: @landmark:api_call {from: telos, to: hermes}
    pass
```

### Level 2: Valuable (Should Have)
Useful patterns to track:

- Decision points in code (`if/else` with business logic)
- Error recovery (exception handling)
- Cache hits/misses
- Performance boundaries crossed
- Pattern matches found

### Level 3: Enriching (Nice to Have)
CI-discovered patterns:

- Repeated code sequences
- Common parameter combinations
- Workflow patterns
- Usage hotspots

## Implementation Approach for Telos

### Phase 1: Minimal Hooks (Start Here)
```python
# Telos/telos/core/landmarks_hooks.py

from functools import wraps
from shared.landmarks import LandmarkRegistry

def landmark_on_proposal_action(action_type):
    """Decorator for proposal-related actions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Drop landmark after successful action
            if result:
                LandmarkRegistry.fire(f"proposal_{action_type}", {
                    "component": "telos",
                    "action": action_type,
                    "proposal": kwargs.get('proposal_name')
                })
            
            return result
        return wrapper
    return decorator

# Usage in Telos
class TelosProposalManager:
    @landmark_on_proposal_action("created")
    def create_proposal(self, proposal_name, data):
        # Existing code unchanged
        pass
    
    @landmark_on_proposal_action("converted")  
    def convert_to_sprint(self, proposal_name):
        # Existing code unchanged
        pass
```

### Phase 2: File Watchers (Add Later)
```python
# Watch key directories for changes
class TelosFileWatcher:
    def __init__(self):
        self.watch_dirs = [
            "MetaData/DevelopmentSprints/Proposals/",
            "Telos/templates/"
        ]
    
    def on_file_created(self, path):
        # Auto-drop landmark
        LandmarkRegistry.fire("file_created", {
            "component": "telos",
            "path": path,
            "type": self.detect_file_type(path)
        })
```

### Phase 3: Semantic Enrichment (CIs Add)
```python
# CIs see structural landmark and add meaning
# Structural: @landmark:proposal_created {name: "Dashboard"}
# CI adds:   @pattern_reference: telos_card_ui
#           @complexity_flag: medium
#           @example_needed: similar dashboards
```

## Rollout Strategy

### 1. Telos (Proof of Concept)
- Add 3-5 decorator hooks to key functions
- Watch Proposals/ directory
- Test landmark cascade to Prometheus

### 2. Prometheus (Phase Planning)
- Hook phase transitions
- Watch sprint directories
- Auto-landmark phase boundaries

### 3. Metis (Task Decomposition)  
- Hook task creation/assignment
- Track task dependencies
- Landmark completion patterns

### 4. Harmonia (Workflow)
- Hook workflow state changes
- Track integration points
- Landmark balance checks

### 5. Synthesis (Integration)
- Hook synthesis operations
- Track component interactions
- Landmark emergent patterns

### 6. TektonCore (Orchestration)
- Hook all component registrations
- Track system-wide state
- Landmark health changes

### 7. Ergon (Execution)
- Hook container operations
- Track deployments
- Landmark resource usage

## Success Metrics

1. **Coverage**: 80% of state transitions have landmarks
2. **Performance**: <1ms overhead per landmark
3. **CI Engagement**: CIs add 2-3 semantic landmarks per structural one
4. **Discovery**: 5+ emergent patterns identified per week
5. **Utility**: Landmark queries used 10+ times daily

## Risk Mitigation

1. **Performance Impact**
   - Solution: Async landmark dropping, batching

2. **Landmark Explosion**
   - Solution: Configurable verbosity levels

3. **CI Confusion**
   - Solution: Clear naming conventions, documentation

4. **Breaking Changes**
   - Solution: Decorators that gracefully degrade

## Example: Complete Telos Flow

```python
# 1. User creates proposal
@landmark_on_proposal_action("created")  # Structural landmark
def create_proposal(self, name, data):
    # Save proposal
    save_to_file(proposal_path, data)
    return True

# 2. File watcher notices
# Auto-drops: @landmark:file_created {type: proposal}

# 3. Telos CI enriches
# Adds: @pattern_reference: dashboard_pattern
#       @ci_attention: Prometheus, please review phases

# 4. Prometheus notices @ci_attention
# Adds: @phases: [design, build, test]
#       @coaching_moment: Similar to Apollo dashboard

# 5. Cascade continues...
```

## Next Steps

1. Review this strategy with Casey
2. Implement minimal Telos example
3. Test landmark cascade
4. Gather feedback
5. Refine before wider rollout

## Key Insight
"The best landmarks are the ones that feel inevitable - of course that's a landmark moment!"