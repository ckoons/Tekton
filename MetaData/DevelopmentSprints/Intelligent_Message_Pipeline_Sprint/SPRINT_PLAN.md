# Sprint: Intelligent Message Pipeline (aish route)

## Overview
Create an intelligent message pipeline system that allows CIs to enhance messages as they flow toward their destination. Each CI in the pipeline can observe, enhance, or consume messages, enabling sophisticated multi-AI collaboration.

## Core Concept
```bash
# Define a pipeline
aish route rhetor numa apollo synthesis rhetor

# Send message through pipeline
aish rhetor "design a caching system"
# Goes: numa → apollo → synthesis → rhetor

# Each hop decides what to do
aish route rhetor  # Continue to next hop
```

## Goals
1. **Enable CI Collaboration**: CIs can enhance each other's work in-flight
2. **Maintain Simplicity**: Just two commands - define pipeline, continue pipeline
3. **Preserve Agency**: Each CI decides whether to pass, enhance, or consume
4. **Support Watchdog Patterns**: CIs can monitor for issues (hallucinations, etc.)

## Phase 1: Core Implementation [0% Complete]

### Tasks
- [ ] Design pipeline storage mechanism
  - Store in ForwardingRegistry or separate PipelineRegistry?
  - Format: `{destination: [hop1, hop2, ..., destination]}`
  
- [ ] Implement `aish route` command parser
  - `aish route <dest> <hop1> <hop2> ... <dest>` - Define pipeline
  - `aish route <dest>` - Continue pipeline (when in pipeline)
  
- [ ] Create pipeline execution logic
  - Intercept messages to pipelined destinations
  - Route to first hop instead of destination
  - Track current position in pipeline
  
- [ ] Implement hop detection
  - Use `aish whoami` to identify current hop
  - Look up next hop in pipeline
  - Forward to next hop or final destination

### Success Criteria
- [ ] Can define multi-hop pipeline
- [ ] Messages flow through pipeline correctly
- [ ] Each hop can continue with `aish route <dest>`
- [ ] Pipeline completes at destination

## Phase 2: Pipeline Management [0% Complete]

### Tasks
- [ ] Add pipeline inspection
  - `aish route list` - Show all active pipelines
  - `aish route show <dest>` - Show specific pipeline
  
- [ ] Add pipeline removal
  - `aish route remove <dest>` - Remove pipeline
  - `aish route clear` - Remove all pipelines
  
- [ ] Add pipeline testing
  - `aish route test <dest>` - Trace message path
  - Show each hop in sequence

### Success Criteria
- [ ] Can view active pipelines
- [ ] Can remove pipelines cleanly
- [ ] Can test pipeline flow

## Phase 3: Advanced Features [0% Complete]

### Tasks
- [ ] Add positional modifiers (future)
  - `aish route <dest> <hop> first` - Insert at beginning
  - `aish route <dest> <hop> last` - Append to end
  - `aish route <dest> <hop> after <other>` - Insert after specific hop
  
- [ ] Add conditional routing (future)
  - Based on message content
  - Based on CI availability
  
- [ ] Add pipeline persistence
  - Save pipelines across sessions
  - Named pipeline templates

### Success Criteria
- [ ] Pipelines can be modified dynamically
- [ ] Pipelines persist appropriately
- [ ] Complex routing patterns work

## Technical Design

### Storage Structure
```python
# In PipelineRegistry or extended ForwardingRegistry
pipelines = {
    "rhetor": ["numa", "apollo", "synthesis", "rhetor"],
    "tekton": ["metis", "tekton"]
}
```

### Message Flow
```
1. User: aish rhetor "message"
2. System: Check if rhetor has pipeline
3. If yes: Forward to first hop (numa)
4. Numa receives: "Message for rhetor: message"
5. Numa processes and decides
6. Numa: aish route rhetor
7. System: Numa is hop[0], forward to hop[1] (apollo)
8. Continue until reaching destination
```

### Integration Points
- Modify message routing in `aish` command handler
- Extend or create registry for pipeline storage
- Add hop detection using terminal identity
- Integrate with existing forwarding system

## Out of Scope
- Circular pipeline detection (for now)
- Pipeline branching/merging
- Conditional routing based on content
- GUI pipeline builder

## Example Use Cases

### CI Health Monitoring
```bash
# Apollo watches for hallucinations
aish route numa apollo numa
# Apollo sees all numa traffic, can intervene if needed
```

### Enhanced Analysis
```bash
# Complex queries get multi-AI treatment
aish route synthesis metis prometheus synthesis
# Metis adds analysis, Prometheus adds predictions
```

### Context Enrichment
```bash
# Tekton adds architectural context
aish route numa tekton numa
# All numa queries get architecture insights
```

## Files to Create/Modify
```
/shared/aish/src/commands/route.py          # New command
/shared/aish/src/core/pipeline_registry.py  # Pipeline storage
/shared/aish/aish                           # Add route command
/shared/aish/src/core/shell.py             # Modify message routing
```

## Notes
- Keep it simple - just two command forms initially
- Don't break existing `aish forward` behavior
- Pipeline should be transparent to end users
- Each CI maintains full agency in the pipeline
- Casey's insight: "Each stage of the pipe is intelligent"