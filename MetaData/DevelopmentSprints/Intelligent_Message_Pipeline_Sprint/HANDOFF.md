# Handoff Document: Intelligent Message Pipeline Sprint

## Current Status
**Phase**: Design Complete, Not Started  
**Progress**: 0% Complete  
**Last Updated**: 2025-01-19

## What Was Just Completed
- Defined the concept with Casey
- Understood the distinction from `aish forward`
- Designed the pipeline flow
- Created sprint structure

## The Core Idea
Create `aish route` command that sets up intelligent message pipelines where each CI can:
- See messages flowing to a destination
- Enhance them with insights
- Pass them along with `aish route <dest>`
- Or consume them (ending the pipeline)

## Key Design Decisions
1. **Keep `aish forward` untouched** - It means "I'll handle these messages"
2. **New `aish route` command** - For pipeline definition and continuation
3. **Simple command forms**:
   - `aish route <dest> <hop1> <hop2> ... <dest>` - Define pipeline
   - `aish route <dest>` - Continue pipeline when you're in it
4. **Intelligent hops** - Each CI has full agency to enhance, pass, or consume

## Critical Understanding
This is NOT like Unix pipes where data blindly flows. Each hop:
- Knows the message destination
- Can see the full message
- Decides whether to enhance and pass on
- Can detect issues (like hallucinations) and intervene

## Example Flow
```bash
# Setup
aish route rhetor numa apollo rhetor

# Execute  
aish rhetor "design cache"
→ Goes to numa (not rhetor)
→ Numa enhances with implementation details
→ Numa: `aish route rhetor`
→ Goes to apollo  
→ Apollo adds performance predictions
→ Apollo: `aish route rhetor`
→ Finally reaches rhetor with enriched context
```

## Implementation Approach
1. Start with basic pipeline storage and routing
2. Use existing terminal identity (`aish whoami`) for hop detection
3. Integrate with current message forwarding system
4. Test with simple 2-hop pipelines first

## Questions for Next Session
1. Should pipelines be per-environment or global?
2. How to handle offline hops?
3. Should we log pipeline transitions?
4. Named pipelines for common patterns?

## Do NOT
- Change existing `aish forward` behavior
- Over-complicate with features (start simple)
- Add conditional routing yet
- Worry about circular pipeline detection initially

## Casey's Vision
"Each stage of the pipe is intelligent" - This enables:
- Watchdog patterns (Apollo monitoring for issues)
- Enhancement patterns (Tekton adding architecture context)
- Collaborative intelligence (multiple CIs contributing)

## Next Steps
1. Implement basic pipeline storage
2. Create route command parser
3. Modify message routing logic
4. Test with simple pipeline
5. Add management commands