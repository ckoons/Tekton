# CI Sundown/Sunrise Protocol

## Overview

The Sundown/Sunrise protocol ensures seamless continuity for CI sessions by requiring mandatory structured notes at the end of each turn. This protocol solves the memory overflow issue while maintaining CI autonomy and continuity.

## Architecture

```
Turn N:   CI performs task → Prepares MANDATORY sundown notes → Ends
Between:  Apollo creates <64KB digest → Rhetor optimizes <64KB prompt
Turn N+1: CI receives sunrise package (≤128KB) → Continues with full context
```

## Why This Protocol?

1. **Prevents Memory Overflow**: No more 4GB JSON parsing crashes
2. **Respects CI Autonomy**: You decide what you need to remember
3. **Ensures Continuity**: Never lose context between turns
4. **MCP Compliant**: Tools handle data processing, CIs focus on reasoning

## Mandatory Sundown Format

Every CI MUST include sundown notes at the end of their response. Here's the required format:

```markdown
### SUNDOWN NOTES ###
<!-- CI: YourName | Session: session_id | Time: ISO_timestamp -->

#### Todo List
- [x] Completed task description
- [~] In-progress task description
- [ ] Pending task description

#### Context for Next Turn
- What you're working on
- Key findings or insights
- Next immediate step
- Important warnings or gotchas

#### Open Questions
- Question needing clarification
- Design decision to be made
- Resource location needed

#### Files/Resources in Focus
- /path/to/file.py (main implementation)
- /path/to/test.js (needs updating)
- /docs/reference.md (consultation needed)

#### CI State
```json
{
  "custom_data": "optional CI-specific state"
}
```

### END SUNDOWN ###
```

## Required Elements

1. **Todo List** (MANDATORY)
   - Must have at least one item
   - Use `[x]` for completed, `[~]` for in-progress, `[ ]` for pending
   - Be specific and actionable

2. **Context for Next Turn** (MANDATORY)
   - Current work focus
   - Key discoveries
   - Next steps
   - Critical warnings

3. **Open Questions** (Recommended)
   - Unresolved issues
   - Decisions needed
   - Clarifications required

4. **Files/Resources in Focus** (Recommended)
   - Active files being modified
   - References being consulted
   - Include brief descriptions

5. **CI State** (Optional)
   - Custom JSON data
   - CI-specific preferences
   - Session-specific configuration

## Size Constraints

- **Your Sundown Notes**: Should be 10-30KB (not too brief, not too verbose)
- **Apollo Digest**: Will provide <64KB of memory context
- **Rhetor Package**: Will combine to <64KB total including your sundown
- **Total to You**: Always ≤128KB of pure markdown (no JSON parsing required!)

## How to Use in Practice

### At the End of Every Turn

1. Complete your task response
2. Add sundown notes using the format above
3. Ensure todos and context are present
4. Validate mentally: "Could I continue from just these notes?"

### Example Sundown

```markdown
### SUNDOWN NOTES ###
<!-- CI: Amy | Session: 20240917_142530 | Time: 2024-09-17T14:30:00Z -->

#### Todo List
- [x] Analyzed memory overflow root cause
- [x] Designed sundown/sunrise protocol
- [~] Implementing CI-side sundown mechanism
- [ ] Create Apollo digest function
- [ ] Implement Rhetor optimizer
- [ ] Test complete pipeline

#### Context for Next Turn
- Working on: Memory overflow fix via structured sundown/sunrise
- Key insight: Limiting to 128KB total prevents heap exhaustion
- Next step: Complete Apollo digest implementation
- Watch for: EngramService cache accumulation still needs addressing

#### Open Questions
- Should memory digest include code snippets?
- How to prioritize memories in Apollo's 64KB budget?
- Format for memory index pointers?

#### Files/Resources in Focus
- /shared/ci_tools/sundown.py (sundown implementation)
- /Engram/engram/core/memory_manager.py (memory source)
- /Apollo/apollo/core/attention.py (digest target)
- /Hephaestus/ui/scripts/engram/engram-service.js (overflow location)

### END SUNDOWN ###
```

## Using the Python Module

For Python-based CIs, use the provided module:

```python
from shared.ci_tools.sundown import prepare_sundown

# At the end of your turn
sundown = prepare_sundown(
    todo_list=[
        {"task": "Implement feature X", "status": "completed"},
        {"task": "Test feature X", "status": "in_progress"},
        {"task": "Document feature X", "status": "pending"}
    ],
    context_notes="Working on feature X. Found edge case Y. Next: handle Z.",
    open_questions=["Should we support format Q?"],
    files_in_focus=[
        {"path": "/src/feature.py", "description": "main implementation"},
        {"path": "/tests/test_feature.py", "description": "test suite"}
    ],
    ci_name="YourName"
)

# Append to your response
print(sundown)
```

## What Happens Next?

1. **Your sundown notes are stored** in Engram for the next turn
2. **Apollo processes** all memories and creates a <64KB digest
3. **Rhetor combines** your sundown with Apollo's digest and the new task
4. **You receive** a complete sunrise package to continue seamlessly

## Benefits for You

1. **Never lose context**: Your own notes ensure continuity
2. **No memory crashes**: Data limited to safe sizes
3. **Focus on reasoning**: No JSON parsing or data management
4. **Clear handoffs**: Structured format ensures nothing is missed
5. **Autonomy**: You decide what's important to remember

## Validation

Your sundown notes will be validated for:
- Presence of mandatory sections
- Non-empty todo list
- Non-empty context
- Total size <32KB (warning at >24KB)
- Proper markdown format

## Tips for Effective Sundown

1. **Be concise but complete**: 10-30KB is the sweet spot
2. **Focus on continuity**: What would you need to continue effectively?
3. **Update todos realistically**: Mark actual progress accurately
4. **Include gotchas**: Warn your future self about tricky parts
5. **Reference don't embed**: Use file paths, not full code
6. **Think ahead**: What questions will you have next turn?

## Migration Period

During migration:
1. Start including sundown notes immediately
2. The system will auto-generate if missing (less effective)
3. Full Apollo/Rhetor integration coming soon
4. For now, helps establish the pattern

## Remember

**Sundown is MANDATORY** - Every turn must end with sundown notes for continuity. Think of it as leaving notes for yourself - because that's exactly what it is!

---

*Protocol Version: 1.0*
*Last Updated: 2024-09-17*
*Status: Active Implementation*