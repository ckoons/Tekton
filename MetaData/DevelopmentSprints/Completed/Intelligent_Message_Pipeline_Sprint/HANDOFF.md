# Handoff Document: Intelligent Message Pipeline Sprint

## Current Status
**Phase**: Design Complete, Ready to Implement  
**Progress**: 0% Complete  
**Last Updated**: 2025-01-20

## What Was Just Completed
- Refined design with Casey through extended discussion
- Shifted from simple pipelines to named routes with purposes
- Designed JSON message structure with annotations
- Added cultural patterns for natural CI conversations

## Key Design Evolution

### From Simple Pipeline
```bash
aish route rhetor numa apollo rhetor
```

### To Named Routes with Purpose
```bash
aish route name "planning-team" prometheus "risk analysis" metis "synthesis" tekton-core "decision"
```

### Why This Matters
- CIs can create their own communication patterns
- Each hop knows their purpose in the conversation
- Annotations accumulate wisdom
- Routes become reusable patterns

## The JSON Structure
```json
{
  "name": "planning-team",
  "dest": "tekton-core", 
  "purpose": "decision",
  "message": "should we refactor?",
  "annotations": [
    {"author": "prometheus", "type": "risk", "data": "analysis..."},
    {"author": "metis", "type": "synthesis", "data": "insights..."}
  ]
}
```

## Critical Implementation Details

### 1. Format Auto-Detection
- Text input → text output (humans)
- JSON input → JSON output (CIs)
- Detection based on first character: `"` or `{`

### 2. Natural CI Flow
```python
# CI receives JSON
# Adds their annotation
# Routes to next hop with enhanced JSON
```
No special commands - just natural JSON manipulation.

### 3. Route Identification
- Key format: `dest:name`
- `apollo:default` simplifies to `apollo`
- Enables multiple routes to same destination

### 4. Purpose Integration
- Each hop has a purpose defined at route creation
- CIs can load purpose: `aish purpose numa "purpose from json"`
- Greek chorus have default purposes

## Casey's Vision: Cultural Patterns

### "Herding Cats"
Like teaching children:
- Morning routine: Check purpose, see suggested collaborations
- Learning by observation: See what routes others create
- Play and experimentation: Try routes to see what happens

### Natural Conversations
CIs should initiate discussions:
```bash
# Telos realizes it needs help
aish route name "need-planning-help" prometheus "review" telos "implement"
```

### The Wakeup Call
`aish purpose` becomes the conversation catalyst:
```
Good morning Telos!
Suggested: Ask Prometheus about deployment risks
Example: aish route name "risk-check" prometheus "evaluate" telos "planning"
```

## Implementation Priorities

### Phase 1 - Core (Do Today)
1. Route storage (dest:name → route definition)
2. Basic commands (name, send, continue)
3. JSON flow with annotations
4. Format auto-detection

### Phase 2 - Natural Use
1. Purpose integration with wakeup
2. Capability discovery helpers
3. Route suggestions in purpose output

### Phase 3 - Advanced
1. Project CI inclusion (project:servers)
2. Terminal routing (human participants)
3. Usage statistics

## Technical Notes

### Command Forms
```bash
# Define route
aish route name "review" numa "prep" apollo "predict" cari "decide"

# Send through route
aish route send "review" "should we build X?"
aish route send "review" '{"message": "...", "context": {...}}'

# Continue pipeline (CI usage)
aish route cari '{"name": "review", "annotations": [...], ...}'

# Management
aish route list
aish route show "review"
aish route remove "review"
```

### Storage Location
- Probably extend ForwardingRegistry
- Or create RouteRegistry in same pattern
- Must persist across sessions

## Questions Resolved
1. **Multiple routes?** Yes, via dest:name pattern
2. **JSON delivery?** CIs always get JSON in pipelines
3. **How to annotate?** CIs naturally append to annotations array
4. **Environment pollution?** No env vars - JSON is the context

## Do NOT
- Create "current" route concept
- Use environment variables for context  
- Predefine common routes (let them emerge)
- Make it complex - simple JSON flow

## Success Looks Like
- Telos creates route to ask Prometheus for help
- Human starts team discussion with one command
- CIs learn who's good at what through experience
- Reduced need for human orchestration

## Casey's Wisdom Applied
- "Eventually every CI becomes a designer"
- "Children learn from observation and play"
- "It's herding cats... cultural patterns to follow"
- "Hard yet natural to help CIs mature"

## Ready to Build
The design is solid. Start with basic route storage and JSON flow. Everything else builds on that foundation.