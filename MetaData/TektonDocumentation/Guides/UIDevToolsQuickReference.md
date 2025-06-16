# UI DevTools Quick Reference Card

## MCP Endpoint
```
http://localhost:8088
```

## Four Tools, Four Commands

### 1. SEE without screenshots
```python
result = await ui_capture("rhetor")
# or with selector
result = await ui_capture("rhetor", "#footer")
```

### 2. TEST before breaking
```python
result = await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#footer",
        "content": "<div>New content</div>",
        "action": "append"  # or replace, prepend, before, after
    }],
    preview=True  # ALWAYS True first!
)
```

### 3. INTERACT with UI
```python
result = await ui_interact(
    component="rhetor",
    action="click",  # or type, select, hover
    selector="button#submit",
    value="text to type"  # for type/select actions
)
```

### 4. CHECK for frameworks
```python
result = await ui_analyze("rhetor")
if any(result['analysis']['frameworks'].values()):
    print("WARNING: Frameworks detected!")
```

## Common Selectors Pattern
```python
# Standard Tekton selectors
f"#{component}-component"  # Main wrapper
f"#{component}-content"    # Content area  
f"#{component}-footer"     # Footer
f"#{component}-header"     # Header
```

## Valid Components
```
apollo, athena, budget, engram, ergon, harmonia, 
hephaestus, hermes, metis, prometheus, rhetor, 
sophia, synthesis, tekton_core, telos, terma
```

## The Golden Workflow
```python
# 1. Check what exists
current = await ui_capture("rhetor", "#footer")

# 2. Test your change
test = await ui_sandbox(..., preview=True)

# 3. Apply if safe
if test['summary']['successful'] > 0:
    await ui_sandbox(..., preview=False)
```

## What Gets Rejected
- ❌ `import React`
- ❌ `Vue.component`
- ❌ `angular.module`
- ❌ `webpack`
- ❌ `npm install anything`

## Emergency Commands
```bash
# If MCP not running
./run_mcp.sh

# Run tests
python acid_test.py

# Check MCP health
curl http://localhost:8088/health
```

Remember: **Simple HTML > React Component**

## For Claude Sessions

See these Claude-specific guides:
- `UIDevToolsClaudeInstructions.md` - Detailed instructions for Claude
- `UI_DEVTOOLS_CHEATSHEET.md` - Quick commands cheat sheet
- `ui_devtools_client.py` - Python wrapper for easy usage

Start every UI session with:
```python
from ui_devtools_client import UIDevTools, check_and_start_mcp
```