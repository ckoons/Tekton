# UI DevTools Evolution: A Case Study

## The Problem That Started It All

Casey's frustration was mounting. Every Claude Code session working with UI would:
- Request 20 screenshots for simple tasks
- Add React to implement a footer timestamp
- Refactor entire frontends when asked to change one line
- Trigger `tekton-revert --nuclear-destruction` multiple times per week

The breaking point: "Add widget to Footer --nuclear-destruction" happened twice in one week.

## The Initial Design (V1)

### The Assumption
When designing the UI DevTools, the natural assumption was:
- Each component has its own UI
- Apollo UI runs on port 8012
- Rhetor UI runs on port 8003
- Target each component's port directly

### The Implementation
```python
# V1 thinking
async def ui_capture(component: str, selector: str):
    port = get_component_port(component)  # 8003 for rhetor
    await browser.goto(f"http://localhost:{port}")
    # ... capture UI
```

### The Failure
Tool-user-Claude kept hitting errors:
- "Cannot navigate to component"
- "Page not found"
- "No UI at this port"

## The Discovery

While debugging with tool-builder-Claude, a critical realization emerged:

**Components don't have separate UIs!**

The investigation revealed:
- Port 8003 is Rhetor's API, not UI
- Port 8012 is Apollo's API, not UI  
- ALL UI is actually at port 8080 (Hephaestus)

### The "Aha!" Moment

Hephaestus is like a restaurant:
- The building (Hephaestus) contains everything
- Different sections (component areas) within
- Not separate restaurants at different addresses!

## The Pivot to V2

### Rapid Redesign
Tool-builder-Claude frantically rewrote while tool-user-Claude was actively using the tools:
1. Change "component" to "area" everywhere
2. Always target port 8080
3. Use area-specific selectors (#rhetor-chat-area)
4. Update all documentation

### The Learning Curve
Even with updated docs, tool-user-Claude kept trying to use playwright directly, leading to increasingly explicit instructions in CLAUDE.md:
- "DO NOT use playwright:browser_navigate!"
- "ONLY use HTTP API at port 8088!"
- Multiple warnings and examples

## Key Lessons Learned

### 1. Mental Models Matter
The biggest challenge wasn't technical - it was conceptual. Every Claude assumed components = separate UIs.

### 2. Explicit Instructions Are Essential
General guidance wasn't enough. The final CLAUDE.md includes:
- Exact curl commands
- What NOT to do (with ❌ symbols)
- Threats about --nuclear-destruction

### 3. Help Systems Are Critical
The `ui_help()` function became essential for teaching the correct mental model to each new Claude.

### 4. Framework Prevention Works
Aggressive framework detection successfully prevented React additions to footers!

## The Result

### Before UI DevTools:
- 20 screenshots per UI task
- Frequent framework additions
- Regular --nuclear-destruction usage
- High context consumption
- Claude confusion

### After UI DevTools V2:
- Zero screenshots needed
- Simple HTML modifications only
- Rare --nuclear-destruction usage
- Efficient structured data
- Clear mental model

## Technical Evolution

### V1 Architecture (Failed):
```
Claude → Component Port (8003) → ❌ No UI Found
```

### V2 Architecture (Success):
```
Claude → MCP (8088) → Hephaestus UI (8080) → Component Areas
```

## Impact on Development Workflow

1. **Immediate**: UI tasks that took 30 minutes now take 5
2. **Context**: 90% reduction in token usage for UI work
3. **Safety**: Preview mode prevents disasters
4. **Learning**: Each Claude learns faster with help()

## Future Implications

This evolution demonstrates:
- Assumptions must be tested early
- User feedback is invaluable
- Documentation must be explicit
- Mental models are as important as code

The UI DevTools journey from V1 to V2 exemplifies Tekton's iterative approach to AI-enabled development - learning from failures and rapidly adapting to create tools that actually work.

## Casey's Reflection

"The best part isn't that Claude can now modify UI without destroying it. It's that we built tools that teach Claude to think correctly about the problem. That's the Tekton way - not just solving problems, but evolving how AI approaches them."

## Epilogue

The `--nuclear-destruction` option remains in Casey's toolkit, but its usage has dropped dramatically. The footer widget that once required total reconstruction now takes three lines of HTML, exactly as it should.