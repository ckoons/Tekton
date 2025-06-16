# UI DevTools Guide for Claude Code

## ⚠️ IMPORTANT: Start the MCP First!

The UI DevTools MCP must be running before you can use these tools:

```bash
# Check if running
curl http://localhost:8088/health

# If not running, start it:
cd $TEKTON_ROOT/Hephaestus
./run_mcp.sh
```

See `UIDevToolsStartup.md` for detailed startup instructions.

## Quick Reference

When working with Tekton UI, you now have tools to SEE and TEST changes without breaking things. No more screenshots, no more frameworks, just simple HTML manipulation.

**MCP Endpoint**: `http://localhost:8088` (Hephaestus UI DevTools)

## Available Tools

### 1. ui_capture - See Without Screenshots

Instead of asking for screenshots that eat context, get structured data:

```python
# ❌ OLD WAY: "Show me a screenshot of Rhetor"
# ✅ NEW WAY:
result = await ui_capture(component="rhetor")
print(f"Page has {len(result['buttons'])} buttons")
print(f"Forms: {len(result.get('forms', []))}")

# Target specific elements
result = await ui_capture(
    component="rhetor", 
    selector="#rhetor-footer"
)
print(f"Footer elements: {result['structure']['element_count']}")
```

**What you get**: HTML structure, forms, buttons, links, interactive elements - as data, not pixels.

### 2. ui_sandbox - Test Changes Safely

ALWAYS test changes before applying them. The sandbox detects and rejects frameworks:

```python
# Test adding a timestamp (preview mode)
result = await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#rhetor-footer",
        "content": "<span class='timestamp'>Updated: 2024-06-13 15:30</span>",
        "action": "append"
    }],
    preview=True  # ALWAYS preview first!
)

if result['summary']['successful'] > 0:
    print("✅ Change is safe to apply")
    # Apply for real: preview=False
else:
    print("❌ Change was rejected:", result.get('error'))
```

**Actions**: `append`, `prepend`, `replace`, `before`, `after`

### 3. ui_interact - Click and See Results

Interact with UI elements and capture what happens:

```python
# Click a button and see changes
result = await ui_interact(
    component="rhetor",
    action="click",
    selector="button#submit",
    capture_changes=True
)

print(f"Console messages: {len(result.get('console', []))}")
print(f"Network requests: {len(result.get('network', []))}")
print(f"DOM changes: {result.get('changes', [])}")

# Type in a form field
result = await ui_interact(
    component="rhetor",
    action="type",
    selector="input#search",
    value="test query"
)
```

**Actions**: `click`, `type`, `select`, `hover`

### 4. ui_analyze - Understand Structure

Check the UI before making changes:

```python
# Quick analysis
result = await ui_analyze(component="rhetor")
analysis = result['analysis']

# Check for frameworks (CRITICAL!)
if any(analysis['frameworks'].values()):
    print("⚠️ WARNING: Frameworks detected!")
    print(f"Detected: {[k for k,v in analysis['frameworks'].items() if v]}")
    # BE VERY CAREFUL - Don't add more complexity!

# Check complexity
print(f"Complexity: {analysis['complexity']['level']}")
print(f"Total elements: {analysis['structure']['total_elements']}")
print(f"Forms: {analysis['structure']['forms']}")

# Deep scan for more details
result = await ui_analyze(component="rhetor", deep_scan=True)
# Includes form details, API calls, etc.
```

## Golden Rules

### 1. NO FRAMEWORKS - Simple HTML Only
```python
# ❌ NEVER DO THIS:
changes = [{
    "content": '<script src="react.js"></script>'  # REJECTED!
}]

# ✅ DO THIS:
changes = [{
    "content": '<div class="status">Active</div>'  # Simple HTML
}]
```

### 2. ALWAYS PREVIEW - Test Before Applying
```python
# First: preview=True (test in sandbox)
result = await ui_sandbox(..., preview=True)

# Check if safe
if result['summary']['successful'] > 0:
    # Then: preview=False (apply for real)
    result = await ui_sandbox(..., preview=False)
```

### 3. CHECK FIRST - Analyze Before Changing
```python
# Before any UI work:
analysis = await ui_analyze(component)

# Know what you're working with:
# - Are there frameworks?
# - What's the structure?
# - What selectors exist?
```

### 4. SMALL CHANGES - One Thing at a Time
```python
# ❌ BAD: Complete refactor
# ✅ GOOD: Add one element
changes = [{
    "type": "html",
    "selector": "#footer",
    "content": "<span>© 2024</span>",
    "action": "append"
}]
```

## Common Selectors

Tekton components follow patterns:

```python
# Standard selectors for any component
selectors = {
    "component": f"#{name}-component",    # Main wrapper
    "content": f"#{name}-content",        # Content area
    "footer": f"#{name}-footer",          # Footer section
    "header": f"#{name}-header",          # Header section
    "chat": f"#{name}-chat",              # Chat interface
    "terminal": f"#{name}-terminal",      # Terminal area
    "tabs": f"#{name}-tabs"               # Tab navigation
}

# Example for Rhetor:
# #rhetor-component
# #rhetor-footer
# #rhetor-content
```

## Decision Tree

```
Need to work with UI?
├─ Need to see current state?
│  └─ ui_capture (no screenshots!)
├─ Need to check for frameworks?
│  └─ ui_analyze
├─ Need to add/change HTML?
│  └─ ui_sandbox (preview first!)
└─ Need to interact (click/type)?
   └─ ui_interact
```

## Examples

### Adding a Footer Widget (The Right Way)

```python
# 1. Check current state
footer_state = await ui_capture("rhetor", "#rhetor-footer")

# 2. Test the change
result = await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#rhetor-footer",
        "content": '''
            <div class="footer-widget" style="margin-top: 10px;">
                <span class="status">System Status: Active</span>
                <span class="timestamp" style="float: right;">12:34 PM</span>
            </div>
        ''',
        "action": "append"
    }],
    preview=True
)

# 3. Apply if safe
if result['summary']['successful'] > 0:
    # Actually apply it
    await ui_sandbox(..., preview=False)
```

### Checking Form Fields

```python
# Get all forms and inputs
ui_state = await ui_capture("rhetor")

for form in ui_state.get('forms', []):
    print(f"Form: {form.get('id', 'unnamed')}")
    for input_field in form.get('inputs', []):
        print(f"  - {input_field['name']}: {input_field['type']}")
```

### Safe Status Update

```python
# Find status element
result = await ui_capture("rhetor", ".status-indicator")

if result['structure']['element_count'] > 0:
    # Update existing
    await ui_sandbox(
        component="rhetor",
        changes=[{
            "type": "html",
            "selector": ".status-indicator",
            "content": '<span class="status active">Connected</span>',
            "action": "replace"
        }],
        preview=False  # After testing!
    )
```

## What These Tools Prevent

- 🚫 Installing React to add a timestamp
- 🚫 Adding webpack configs
- 🚫 Refactoring everything when asked for one change
- 🚫 Creating build pipelines for 3 lines of HTML
- 🚫 Context explosion from screenshot analysis

## Remember

These tools exist because Claude Code tends to over-engineer UI changes. When Casey asks for a footer widget, he wants:

```html
<div>Footer Widget</div>
```

Not:
```javascript
import React from 'react';
import { useState, useEffect } from 'react';
// ... 500 more lines
```

Use these tools. Save Casey's sanity. No `--nuclear-destruction` needed!