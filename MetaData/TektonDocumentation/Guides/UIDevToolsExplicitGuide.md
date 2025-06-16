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

## Parameter Discovery Issues

### The "area" vs "component" Confusion
This is the #1 issue every Claude encounters:

```bash
# ❌ WRONG - This will error
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{"tool_name": "ui_sandbox", "arguments": {"component": "all", ...}}'
# Error: ui_sandbox() got an unexpected keyword argument 'component'

# ✅ CORRECT - Use 'area' for ui_sandbox
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{"tool_name": "ui_sandbox", "arguments": {"area": "hephaestus", ...}}'
```

### Different Tools, Different Parameters
```bash
# ui_capture can use 'component' OR 'area'
{"tool_name": "ui_capture", "arguments": {"component": "all"}}  # Works
{"tool_name": "ui_capture", "arguments": {"area": "hephaestus"}}  # Also works

# ui_sandbox ONLY uses 'area'
{"tool_name": "ui_sandbox", "arguments": {"area": "hephaestus"}}  # Only way
```

## Debug Mode for Failed Selectors

### Problem: Selector Returns Empty
When your selector returns no results, you're flying blind:

```bash
# Current behavior - no helpful info
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{"tool_name": "ui_capture", "arguments": {"selector": "[data-component=\"budget\"]"}}'
# Returns: {"element_count": 0, "elements": []}
```

### Proposed Enhancement: Debug Mode
```bash
# Future enhancement - helpful debug info
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{
    "tool_name": "ui_capture",
    "arguments": {
      "selector": "[data-component=\"budget\"]",
      "debug": true
    }
  }'

# Would return:
{
  "element_count": 0,
  "debug": {
    "selector_valid": true,
    "similar_elements": [
      "[data-component=\"profile\"]",
      "[data-component=\"settings\"]"
    ],
    "recommendation": "Element might be in footer section, try broader selector",
    "page_state": "loaded",
    "total_elements_scanned": 47
  }
}
```

## Validation Tool Concept

### Proposed Tool: ui_validate
Check UI consistency and find issues:

```bash
# Future enhancement
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{
    "tool_name": "ui_validate",
    "arguments": {
      "area": "hephaestus",
      "checks": ["navigation", "semantic-tags", "data-attributes"]
    }
  }'

# Would return:
{
  "status": "issues_found",
  "validation_results": {
    "navigation": {
      "missing_attributes": [
        "Element at line 245 missing data-tekton-zone",
        "Nav item 'budget' has emoji but is in greek-chorus zone"
      ],
      "inconsistencies": [
        "Component 'budget' displayed as 'Penia' - consider data-tekton-legacy-name"
      ]
    },
    "semantic_tags": {
      "coverage": "87%",
      "missing": ["Main content area lacks data-tekton-area"]
    }
  },
  "recommendations": [
    "Add zone attributes to all nav items",
    "Remove emoji from Greek components",
    "Document component name migrations"
  ]
}
```

## Proposed Help Endpoint

### Current Problem
No way to discover available tools and parameters without reading docs:

```bash
# This doesn't exist yet but should
curl http://localhost:8088/help
```

### Proposed Implementation
Add to `/Hephaestus/hephaestus/mcp/mcp_server.py`:

```python
@app.get("/help")
async def get_help():
    """Return comprehensive help for all tools."""
    return {
        "version": "0.1.0",
        "base_url": "http://localhost:8088",
        "endpoints": {
            "/health": "Check if DevTools are running",
            "/help": "This help message",
            "/api/mcp/v2/execute": "Execute UI DevTools commands"
        },
        "tools": {
            "ui_capture": {
                "description": "Capture UI structure and content",
                "parameters": {
                    "area": {
                        "type": "string",
                        "required": True,
                        "description": "UI area to capture",
                        "examples": ["hephaestus", "rhetor", "all"]
                    },
                    "selector": {
                        "type": "string", 
                        "required": False,
                        "description": "CSS selector to filter results",
                        "examples": ["[data-component='budget']", ".nav-item", "#footer"]
                    },
                    "debug": {
                        "type": "boolean",
                        "required": False,
                        "description": "Enable debug mode for troubleshooting",
                        "default": False
                    }
                },
                "examples": [
                    {
                        "description": "Capture entire UI",
                        "curl": "curl -X POST http://localhost:8088/api/mcp/v2/execute -d '{\"tool_name\": \"ui_capture\", \"arguments\": {\"area\": \"hephaestus\"}}'"
                    }
                ]
            },
            "ui_sandbox": {
                "description": "Test UI changes safely with preview mode",
                "parameters": {
                    "area": {
                        "type": "string",
                        "required": True,
                        "description": "UI area (NOT 'component'!)"
                    },
                    "changes": {
                        "type": "array",
                        "required": True,
                        "description": "Array of change operations"
                    },
                    "preview": {
                        "type": "boolean",
                        "required": False,
                        "description": "Preview without applying",
                        "default": True
                    }
                },
                "change_types": {
                    "text": "Replace text content",
                    "html": "Replace HTML content", 
                    "attribute": "Update element attributes"
                },
                "actions": {
                    "replace": "Replace entire content",
                    "append": "Add to end",
                    "prepend": "Add to beginning",
                    "remove": "Remove element",
                    "update": "Update attribute value"
                }
            }
        },
        "common_errors": {
            "unexpected_keyword_argument": "You used 'component' instead of 'area' for ui_sandbox",
            "area_not_provided": "The 'area' parameter is required",
            "no_elements_found": "Your selector didn't match any elements"
        }
    }
```

### Usage Example
```bash
# Get help
curl http://localhost:8088/help | jq '.tools.ui_sandbox'

# See common errors
curl http://localhost:8088/help | jq '.common_errors'

# Get examples for specific tool
curl http://localhost:8088/help | jq '.tools.ui_capture.examples'
```

## Emergency Help

If confused:
```python
from ui_devtools_client import UIDevTools
ui = UIDevTools()
help_text = await ui.help()  # Read this!
```

Or check the new resources:
- [UI DevTools Cookbook](UIDevToolsCookbook.md) - Real examples that work
- [UI Navigation Patterns](../Patterns/UINavigationPatterns.md) - Component structure

## Casey's Final Warning

"Every time you add a framework to my UI, I have to use `tekton-revert --nuclear-destruction`. This makes me sad. Don't make me sad."

## Remember

- Port 8080 = ALL UI (Hephaestus)
- Port 8088 = UI DevTools MCP
- Everything else = NOT UI

Simple HTML. No frameworks. Preview everything. Make Casey happy.