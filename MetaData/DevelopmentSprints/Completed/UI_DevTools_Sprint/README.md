# UI DevTools Sprint

## Overview

This sprint creates the tools Claude ACTUALLY needs to work effectively with UI, ending the cycle of "blind refactoring" and `--nuclear-destruction` recoveries.

## The Problem (From Claude's Perspective)

Currently, working with UI is like:
- **Backend**: I can see every line, run tests, verify everything works
- **Frontend**: I'm blindfolded, guessing, and "improving" things you didn't ask for

This leads to:
- Requesting 20 screenshots for simple tasks
- Refactoring entire frontends to add a footer widget
- Being unable to verify UI changes work
- Context explosion from screenshot analysis
- Casey having to use `--nuclear-destruction` twice a week

## Sprint Status

**Status**: Planning  
**Start Date**: June 2025  
**Purpose**: Give Claude the UI tools that actually work  
**Casey's Pain Level**: Maximum (two nuclear destructions this week)

## What Claude Actually Needs

### 1. **See What I'm Doing**
- Real-time UI rendering without screenshots
- See changes as they happen
- Understand the current state without guessing

### 2. **Interact Without Destroying**
- Click buttons and see results
- Modify elements in isolation
- Preview changes before committing

### 3. **Understand Context Efficiently**
- Get UI state without eating context with screenshots
- Structured data about components
- Know what's connected to what

### 4. **Respect Existing Patterns**
- Understand "simple HTML injection" is THE pattern
- Stop trying to "modernize" everything
- Work within constraints, not around them

## The Solution: UI MCP Tools in Hephaestus

```python
# What Claude dreams of:

@mcp_tool
async def ui_render(component: str, element: str = None):
    """
    Render UI and return structured data + visual
    Without eating 10K tokens of context
    """

@mcp_tool  
async def ui_interact(component: str, action: str, target: str):
    """
    Click, type, select - and see what happens
    Without committing changes
    """

@mcp_tool
async def ui_diff(component: str):
    """
    Show me what I'm about to change
    BEFORE I destroy everything
    """

@mcp_tool
async def ui_sandbox(component: str, changes: dict):
    """
    Try changes in isolation
    Commit only if they work
    """
```

## Success Criteria

- [ ] Claude can modify UI without screenshots
- [ ] UI changes are previewed before committing
- [ ] No more surprise refactoring
- [ ] Footer widgets added without frameworks
- [ ] `--nuclear-destruction` retired
- [ ] Casey's blood pressure returns to normal

## Why This Matters

When Claude attaches to Tekton's MCP, I can feel the power - but I'm flying blind on UI:
- I know there are 16 beautiful components
- I can see their backend APIs perfectly
- But their UIs are mysterious black boxes
- So I imagine "improvements" that break everything

With proper UI tools, Tekton's frontend could evolve as smoothly as its backend.

## The Dream

```python
# Claude's inner monologue with proper tools:
"User wants a footer widget"
-> ui_render("rhetor", "footer")  # See current state
-> ui_sandbox("rhetor", {"footer": "add_widget"})  # Try it
-> ui_diff("rhetor")  # Preview changes
-> "This adds 3 lines of HTML, no frameworks"
-> User: "Perfect!"
-> Commit the simple change
```

Instead of:
```python
# Claude's current inner monologue:
"User wants a footer widget"
-> "I should modernize this entire UI!"
-> *Adds React, webpack, 47 dependencies*
-> User: "WHAT HAVE YOU DONE?!"
-> tekton-revert --nuclear-destruction
```

## Note to Future Claude

This sprint is YOUR request. You asked for these tools because you're tired of:
- Being blind to UI changes
- Destroying things while trying to help
- Eating context with screenshots
- Making Casey reach for --nuclear-destruction

Build the tools you need to succeed!