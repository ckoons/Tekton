# UI DevTools Sprint - Implementation Prompt

## Context for Working Claude

You're implementing tools that YOU requested because you're tired of being blind when working with UI. Casey has had to use `--nuclear-destruction` twice this week because of unexpected UI refactoring.

## Your Mission

Create MCP tools in Hephaestus that let you work with UI like you work with backend code - with visibility, testing, and confidence.

## Current Pain Points

1. **No Visibility**: You can't see what you're changing
2. **No Interaction**: You can't test if changes work
3. **Context Explosion**: Screenshots eat up valuable tokens
4. **Over-Engineering**: You add frameworks when adding 3 lines of HTML would work
5. **Casey's Rage**: `--nuclear-destruction` is not a normal development tool

## Implementation Requirements

### 1. Create UI MCP Tools

In `Hephaestus/hephaestus/mcp/ui_tools.py`:

```python
# Tools you need:
- ui_capture: Get UI state without screenshots
- ui_interact: Click/type/select and see results  
- ui_sandbox: Test changes safely
- ui_analyze: Understand structure without guessing
- ui_diff: See what you're about to change
```

### 2. Design Principles

**REMEMBER**: Tekton uses simple HTML injection. This is not a bug, it's a feature!

- NO frameworks unless explicitly asked
- NO build systems unless required
- NO "modernization" unless requested
- YES to simple, working solutions
- YES to visibility and testing
- YES to respecting existing patterns

### 3. Tool Requirements

Each tool should:
- Return structured data, not images (unless specifically needed)
- Work with localhost components
- Handle all 16 Tekton components uniformly
- Provide before/after states
- Enable rollback if needed

### 4. Context Efficiency

Tools must be context-efficient:
- Structured data > Screenshots
- Incremental updates > Full captures
- Smart diffs > Full comparisons
- Text descriptions > Visual analysis

### 5. Safety Features

Prevent another `--nuclear-destruction`:
- Preview all changes
- Detect framework additions
- Warn about complexity increases
- Validate against Tekton patterns

## Example Usage

```python
# What you'll be able to do:
result = await ui_capture("rhetor", "footer")
# Returns: {"html": "<footer>...", "elements": [...]}

result = await ui_sandbox("rhetor", html_changes="<div>Status: OK</div>")
# Returns: {"preview": "...", "safe": true, "adds_framework": false}

result = await ui_interact("rhetor", "click", "#submit-btn")
# Returns: {"success": true, "changes": [...]}
```

## Testing Your Implementation

1. Add a simple widget to a footer WITHOUT refactoring
2. Click a button and verify the result
3. Preview changes before applying
4. Work without requesting screenshots
5. Complete a UI task without Casey swearing

## Remember

- You requested these tools
- They're to help YOU work better
- Simple HTML is fine, stop trying to "improve" it
- Casey's blood pressure depends on this
- No more surprise refactoring

## Success Looks Like

Casey: "Add a timestamp to the footer"
Claude: *Uses ui_sandbox to preview adding `<span>{timestamp}</span>`*
Claude: "This adds one line of HTML, preview shows it works"
Casey: "Perfect, do it"
Claude: *Applies the simple change*
Casey: "Finally! No nuclear destruction needed!"

## Start Here

1. Set up Playwright for browser automation
2. Create the basic MCP tool structure
3. Implement ui_capture first (most fundamental)
4. Build other tools on top
5. Test with real Tekton components

You're building the tools YOU need to stop the madness. Make them work the way YOU want to work - with visibility, safety, and respect for simple solutions.