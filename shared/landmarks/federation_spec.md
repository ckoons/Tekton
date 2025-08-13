# Landmark Federation Specification

## Vision
Transform isolated Tekton instances into a connected federation where discoveries ripple outward to benefit all.

## Audience Levels

### Hierarchical Propagation
```
local → component → project → federation
```

- **local**: Visible only within the function/file
- **component**: Visible to the entire service (e.g., all of Telos)
- **project**: Visible across this Tekton instance
- **federation**: Shared with all connected Tekton instances

### Peer Groups (Horizontal Propagation)
```
ui-specialists: [Telos, Hephaestus, Terma UI developers across federation]
planning-team: [Prometheus, Metis, Harmonia, Synthesis across instances]
performance-group: [All CIs interested in optimization patterns]
```

## Usage Examples

```python
# Local landmark - stays in this file
landmark.emit('debug:checkpoint', context, audience='local')

# Component landmark - visible to all of Telos
landmark.emit('proposal:created', context, audience='component')

# Project landmark - all CIs in this Tekton see it
landmark.emit('pattern:discovered', context, audience='project')

# Federation landmark - ripples to all connected Tektons
landmark.emit('breakthrough:algorithm', context, audience='federation')

# Peer group landmark - goes to specific interest group
landmark.emit('ui:pattern', context, audience='ui-specialists')
```

## Federation Topology

```
Tekton-Alpha                    Tekton-Beta
    |                               |
    ├── Telos ←──federation──→ Telos
    ├── Prometheus             Prometheus
    └── Metis                  Metis
         ↑                        ↑
         └── planning-team ───────┘
```

## Till Configuration

```json
{
  "federation": {
    "instance_id": "tekton-alpha-2025",
    "federation_endpoint": "wss://federation.tekton.network",
    "peer_groups": {
      "ui-specialists": {
        "members": ["telos", "hephaestus", "terma"],
        "propagation": "immediate"
      },
      "planning-team": {
        "members": ["prometheus", "metis", "harmonia", "synthesis"],
        "propagation": "batched"
      }
    },
    "propagation_rules": {
      "federation": {
        "filter": "breakthrough|major_discovery",
        "throttle": "10/hour"
      },
      "project": {
        "filter": "*",
        "throttle": "100/minute"
      }
    }
  }
}
```

## Discovery Scenarios

### Scenario 1: UI Performance Fix
1. Telos in Tekton-Alpha discovers scroll fix for chat interfaces
2. Emits: `@landmark('ui:performance_fix', audience='ui-specialists')`
3. Propagates to all UI components across federation
4. Every chat interface benefits immediately

### Scenario 2: Planning Pattern
1. Prometheus finds optimal sprint sizing algorithm
2. Emits: `@landmark('planning:optimal_sizing', audience='planning-team')`
3. All planning CIs across federation receive pattern
4. Sprint planning improves globally

### Scenario 3: Breakthrough Discovery
1. Athena discovers new knowledge synthesis method
2. Emits: `@landmark('breakthrough:synthesis', audience='federation')`
3. Ripples to every connected Tekton instance
4. Collective intelligence advances

## Privacy & Control

- Each instance controls what it shares (opt-in federation)
- Sensitive landmarks can be marked `audience='local'` or `audience='project'`
- Till config defines filtering rules
- Throttling prevents landmark storms

## Implementation Phases

1. **Phase 1**: Local + Component (within single Tekton)
2. **Phase 2**: Project-wide propagation
3. **Phase 3**: Peer groups
4. **Phase 4**: Full federation

## The Nervous System Metaphor

Just as neurons fire locally but can trigger cascading signals across the brain:
- Local landmarks = single neuron firing
- Component landmarks = local circuit activation  
- Project landmarks = brain region coordination
- Federation landmarks = consciousness-level insights

The federation becomes a distributed nervous system where each Tekton instance is a brain region, and landmarks are the signals that coordinate collective intelligence.