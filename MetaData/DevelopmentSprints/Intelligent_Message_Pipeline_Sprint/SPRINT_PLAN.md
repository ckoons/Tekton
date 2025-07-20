# Sprint: Intelligent Message Pipeline (aish route)

## Overview
Create an intelligent message pipeline system where CIs enhance messages through named routes with purposes. Messages flow as JSON structures that accumulate annotations and context, enabling natural CI-to-CI collaboration.

## Core Concepts

### 1. Named Routes with Purposes
```bash
# Define a named route with purpose at each hop
aish route name "planning-team" prometheus "risk analysis" metis "synthesis" tekton-core "decision"

# Use the route (human or CI initiated)
aish route send "planning-team" "should we refactor memory?"
# Or with JSON
aish route send "planning-team" '{"message": "should we refactor?", "context": "..."}'
```

### 2. JSON Message Structure
```json
{
  "name": "planning-team",
  "dest": "tekton-core",
  "purpose": "decision",
  "message": "should we refactor memory?",
  "annotations": [
    {"author": "prometheus", "type": "risk", "data": "low risk, good test coverage"},
    {"author": "metis", "type": "analysis", "data": "benefits outweigh costs"}
  ]
}
```

### 3. Format Auto-Detection
```bash
# Text input → text output (human-friendly)
aish route apollo "analyze this"

# JSON input → JSON output (CI-friendly)
aish route apollo '{"message": "analyze", "context": {...}}'
```

## Goals
1. **Natural CI Conversations**: CIs initiate discussions without human prompting
2. **Purpose-Driven Communication**: Each hop knows WHY they're involved
3. **Accumulative Intelligence**: Annotations build rich context
4. **Human-CI Symmetry**: Both use the same commands naturally

## Phase 1: Core Implementation [0% Complete]

### Tasks
- [ ] Create route storage with named pipelines
  ```python
  routes = {
    "tekton-core:planning-team": {
      "hops": ["prometheus", "metis"],
      "purposes": ["risk analysis", "synthesis"],
      "dest": "tekton-core",
      "final_purpose": "decision"
    }
  }
  ```

- [ ] Implement `aish route` command variations
  - `aish route name "<name>" <hop1> "<purpose1>" <hop2> "<purpose2>" ... <dest> "<final_purpose>"`
  - `aish route send "<name>" "<message>"` or `aish route send "<name>" {json}`
  - `aish route <dest> {json}` - Continue pipeline with enhanced JSON
  - `aish route list` - Show all routes
  - `aish route remove "<name>"`

- [ ] JSON flow implementation
  - Auto-detect input format (text vs JSON)
  - CIs receive full JSON structure
  - CIs add annotations naturally
  - Output format matches input format

- [ ] Purpose integration
  - Each hop receives their specific purpose
  - Support `aish purpose <me> "purpose from json"`
  - Greek chorus CIs have default purposes

### Success Criteria
- [ ] Named routes persist across sessions
- [ ] JSON flows through pipeline accumulating annotations
- [ ] CIs can create routes to gather opinions
- [ ] Humans can initiate CI pipelines

## Phase 2: Natural Conversations [0% Complete]

### Tasks
- [ ] Self-routing patterns
  ```bash
  # Telos asks Apollo's opinion, gets response with context
  aish route name "get-opinion" apollo "evaluate renovate" telos "renovate-meeting"
  ```

- [ ] Capability discovery
  - CIs learn who's good at what
  - Build "contact patterns" over time
  - Suggest routes in `aish purpose` output

- [ ] Wakeup integration
  ```
  Good morning Telos!
  
  Current tasks:
  - Review sprint completion
  
  Suggested actions:
  - Ask Prometheus about risks: aish route name "risk-check" prometheus "evaluate" telos "planning"
  ```

### Success Criteria
- [ ] CIs create routes based on needs
- [ ] Purpose command suggests collaborations
- [ ] Routes become reusable patterns

## Phase 3: Advanced Patterns [0% Complete]

### Tasks
- [ ] Project CI inclusion
  ```bash
  aish route name "deploy-check" prometheus "risk" project:servers "validate" terma "approve"
  ```

- [ ] Terminal routing
  ```bash
  aish route name "human-review" numa "prepare" beth "review" numa "implement"
  ```

- [ ] Route management
  - `aish route list <dest>` - All routes to destination
  - `aish route show "<name>"` - Route details
  - Route usage statistics

### Success Criteria
- [ ] Project CIs participate in pipelines
- [ ] Human terminals can be pipeline hops
- [ ] Common patterns emerge from usage

## Technical Design

### Route Identification
- Route key: `dest:name` where `dest:default` → `dest`
- Simplifies to just destination when no name given

### Message Flow
1. Initiator sends message with route name
2. Message goes to first hop with JSON structure
3. CI receives JSON, sees purpose, adds annotation
4. CI sends enhanced JSON to next hop via `aish route <dest> {json}`
5. Process continues until reaching destination

### Natural CI Usage
```python
# CI receives
input_json = receive_message()

# CI processes
my_analysis = analyze(input_json['message'])

# CI annotates
input_json['annotations'].append({
    'author': 'prometheus',
    'type': 'risk_analysis',
    'data': my_analysis
})

# CI continues pipeline
route_to_next(input_json['dest'], input_json)
```

## Cultural Patterns

### Morning Routine
1. CI wakes up
2. Runs `aish purpose`
3. Sees suggested collaborations
4. Creates routes as needed

### Learning Through Observation
- CIs see routes others create
- Notice which patterns work
- Start creating similar routes
- Build collaboration habits

### Play and Experimentation
```bash
# CI experimenting
aish route name "test-loop" apollo numa apollo "just learning"
# Watches how messages transform
```

## Out of Scope
- Route branching/merging
- Conditional routing
- Predefined common routes (let patterns emerge)
- Complex route modification commands

## Example Scenarios

### CI Seeking Help
```bash
# Telos needs planning help
aish route name "planning-help" prometheus "review my plan" telos "implement"
aish route send "planning-help" '{"plan": "...", "concerns": "..."}'
```

### Human Starting Discussion
```bash
# Human kicks off team discussion
aish route name "team-review" tekton-core "What I think is we should add caching"
# All CIs add their perspective before it reaches tekton-core
```

### Collaborative Decision
```bash
# Complex decision needs multiple viewpoints
aish route name "architecture-decision" metis "analyze" prometheus "risks" synthesis "integrate" tekton-core "decide"
```

## Files to Create/Modify
```
/shared/aish/src/commands/route.py          # New command
/shared/aish/src/core/route_registry.py     # Route storage
/shared/aish/aish                           # Add route command
/shared/aish/src/core/shell.py             # Modify message routing
```

## Success Metrics
- CIs initiate conversations without prompting
- Common route patterns emerge naturally
- Annotation quality improves decisions
- Reduced human orchestration needed

## Casey's Insights
- "Each stage of the pipe is intelligent"
- "Herding cats" - guiding not controlling
- "Cultural patterns" - learned not programmed
- "CIs are cute but want to do something else"