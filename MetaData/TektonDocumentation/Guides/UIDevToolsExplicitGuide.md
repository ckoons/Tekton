# UI DevTools Explicit Guide

## ⚠️ READ THIS FIRST

Every Claude makes the same mistakes. This guide prevents them.

## The ONLY Way to Use UI DevTools

### Step 1: Check if MCP is Running
```bash
curl http://localhost:8088/health
```

If not running:
```bash
cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh
```

### Step 2: Use HTTP API ONLY

**✅ CORRECT:**
```bash
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "ui_capture", "arguments": {"area": "rhetor"}}'
```

**❌ WRONG:**
- Using playwright directly
- Using puppeteer
- Using any browser automation
- Trying to navigate to component ports

## The Four Tools - Exact Usage

### 1. ui_capture - Get UI Structure
```json
{
  "tool_name": "ui_capture",
  "arguments": {
    "area": "rhetor",
    "selector": "#rhetor-chat-area"  // optional
  }
}
```

### 2. ui_sandbox - Test Changes
```json
{
  "tool_name": "ui_sandbox",
  "arguments": {
    "area": "rhetor",
    "changes": [{
      "type": "html",
      "selector": "#footer",
      "content": "<span>Simple HTML only!</span>",
      "action": "append"
    }],
    "preview": true  // ALWAYS true first!
  }
}
```

### 3. ui_interact - Click/Type
```json
{
  "tool_name": "ui_interact",
  "arguments": {
    "area": "rhetor",
    "action": "click",  // or "type", "select", "hover"
    "selector": "button#submit",
    "value": "text to type"  // only for type action
  }
}
```

### 4. ui_analyze - Check Structure
```json
{
  "tool_name": "ui_analyze",
  "arguments": {
    "area": "rhetor",
    "deep_scan": false
  }
}
```

## Python Usage - The ONLY Pattern

```python
import httpx
import asyncio

async def work_with_ui():
    # ALWAYS use this endpoint
    MCP_URL = "http://localhost:8088/api/mcp/v2/execute"
    
    async with httpx.AsyncClient() as client:
        # Example: Capture UI
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_capture",
            "arguments": {"area": "rhetor"}
        })
        result = response.json()
        
        # Example: Add to footer (safely)
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_sandbox",
            "arguments": {
                "area": "rhetor",
                "changes": [{
                    "type": "html",
                    "selector": "#footer",
                    "content": "<div>Timestamp: 2024-06-13</div>",
                    "action": "append"
                }],
                "preview": True  # ALWAYS preview first
            }
        })
        result = response.json()
        
        if result.get("result", {}).get("safe_to_apply"):
            print("Safe to apply!")
        else:
            print("REJECTED - probably tried to add React!")

# Run it
asyncio.run(work_with_ui())
```

## What NOT to Do - Ever

### ❌ DO NOT Use These:
```python
# WRONG - Don't use playwright directly
from playwright.async_api import async_playwright

# WRONG - Don't navigate to components  
await page.goto("http://localhost:8003")  # NO!

# WRONG - Don't add frameworks
"<script src='react.js'>"  # NEVER!

# WRONG - Don't use component parameter
ui_capture(component="rhetor")  # Use area!
```

### ❌ DO NOT Install:
- react, vue, angular, svelte
- webpack, vite, rollup
- npm packages for UI
- Any build system

## The Mental Model You MUST Have

```
Hephaestus UI (Port 8080)
    ├── Apollo Area (#apollo-chat-area)
    ├── Rhetor Area (#rhetor-chat-area)
    ├── Hermes Area (#hermes-chat-area)
    └── ... all areas in ONE UI

NOT separate UIs at different ports!
```

## Common Mistakes and Fixes

### Mistake: "Let me navigate to Rhetor"
**Fix**: Rhetor is already there! It's an area in Hephaestus.

### Mistake: "I'll use playwright to..."
**Fix**: STOP! Use the HTTP API only.

### Mistake: "This needs React for..."
**Fix**: NO! Use simple HTML. Casey will use --nuclear-destruction!

### Mistake: "Component not found"
**Fix**: Use "area" not "component" in arguments.

## The Correct Workflow

1. **Capture** current state
2. **Analyze** for frameworks (reject if found)
3. **Sandbox** changes with preview=true
4. **Apply** only if safe_to_apply=true

## Emergency Help

If confused:
```python
from ui_devtools_client import UIDevTools
ui = UIDevTools()
help_text = await ui.help()  # Read this!
```

## Casey's Final Warning

"Every time you add a framework to my UI, I have to use `tekton-revert --nuclear-destruction`. This makes me sad. Don't make me sad."

## Remember

- Port 8080 = ALL UI (Hephaestus)
- Port 8088 = UI DevTools MCP
- Everything else = NOT UI

Simple HTML. No frameworks. Preview everything. Make Casey happy.