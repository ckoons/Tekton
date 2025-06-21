# UI DevTools Comprehensive Guide

## Overview

The UI DevTools are essential tools for working with Hephaestus UI components. They provide a robust HTTP API for capturing, modifying, and interacting with the UI without using traditional browser automation tools.

**Key Benefits:**
- No playwright/puppeteer needed
- Built-in verification and retry logic
- Helpful error messages with suggestions
- Smart workflows that handle common patterns

## Architecture

### Core Components

1. **MCP Server** (`http://localhost:8088`)
   - Handles all DevTools requests
   - Provides HTTP API endpoints
   - Manages browser interaction

2. **Tool Categories**
   - **Navigation**: `ui_navigate` - Switch between components
   - **Capture**: `ui_capture` - Get UI structure and content
   - **Modification**: `ui_sandbox` - Test and apply changes
   - **Interaction**: `ui_interact` - Click/type UI elements
   - **Analysis**: `ui_analyze` - Check for issues
   - **Workflow**: `ui_workflow` - High-level operations (recommended!)

### Important Concepts

**Components vs Areas:**
- **Component**: What you navigate TO (rhetor, hermes, apollo, etc.)
- **Area**: Regions of the page (navigation, content, footer, etc.)
- After navigating to a component, always capture/modify the "content" area

## Quick Start

### 1. Check MCP Server

```bash
# Check if running
curl http://localhost:8088/health

# If not running, start it
cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh
```

### 2. Use Python API (Recommended)

```python
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def devtools_request(tool_name, arguments):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(MCP_URL, json={
            "tool_name": tool_name,
            "arguments": arguments
        })
        return response.json()
```

### 3. The Golden Workflow Pattern

```python
# Use ui_workflow for most tasks - it handles all the complexity!
result = await devtools_request("ui_workflow", {
    "workflow": "modify_component",
    "component": "hermes",
    "changes": [{
        "selector": ".hermes__header",
        "content": '<div class="status">🟢 Connected</div>',
        "action": "append"
    }]
})
```

## Tools Reference

### ui_workflow (Recommended Starting Point)

The high-level tool that bundles common patterns and handles verification.

**Available Workflows:**
- `modify_component` - Make changes to a component
- `add_to_component` - Add new elements
- `verify_component` - Quick verification
- `debug_component` - Smart debugging with recommendations

**Example:**
```python
# Instead of 7+ manual steps, one command:
result = await devtools_request("ui_workflow", {
    "workflow": "modify_component",
    "component": "rhetor",
    "changes": [{
        "selector": ".rhetor__footer",
        "content": '<div>Status: Active</div>',
        "action": "replace"
    }]
})
```

### ui_navigate

Navigate to a specific component.

```python
await devtools_request("ui_navigate", {
    "component": "hermes"  # Navigate TO the hermes component
})
```

### ui_capture

Capture UI structure and content.

```python
# ALWAYS use area="content" after navigation!
capture = await devtools_request("ui_capture", {
    "area": "content"  # NOT the component name!
})

# Access elements
elements = capture["result"]["structure"]["elements"]
```

### ui_sandbox

Test and apply UI changes.

```python
# Always preview first
result = await devtools_request("ui_sandbox", {
    "area": "content",
    "changes": [{
        "type": "text",
        "selector": ".header",
        "content": "New Header",
        "action": "replace"
    }],
    "preview": True  # Set to False to apply
})
```

### ui_interact

Click buttons or type in inputs.

```python
await devtools_request("ui_interact", {
    "selector": "button.submit",
    "action": "click"
})
```

### ui_screenshot

Take screenshots for verification.

```python
result = await devtools_request("ui_screenshot", {
    "component": "hermes",
    "save_to_file": True
})
# Screenshot path: result["result"]["file_path"]
```

## Common Patterns

### Pattern 1: Add Status Indicator

```python
# The easy way with ui_workflow
result = await devtools_request("ui_workflow", {
    "workflow": "modify_component", 
    "component": "hermes",
    "changes": [{
        "selector": ".hermes__header",
        "content": '<span class="status">🟢 Active</span>',
        "action": "append"
    }]
})
```

### Pattern 2: Debug When Confused

```python
# Get comprehensive diagnostics
debug_result = await devtools_request("ui_workflow", {
    "workflow": "debug_component",
    "component": "hermes"
})
print(debug_result["visual_feedback"])
```

### Pattern 3: Manual Workflow (if needed)

```python
# 1. Navigate
await devtools_request("ui_navigate", {"component": "hermes"})

# 2. Wait for load (necessary evil)
await asyncio.sleep(1)

# 3. Capture content area
capture = await devtools_request("ui_capture", {"area": "content"})

# 4. Make changes
await devtools_request("ui_sandbox", {
    "area": "content",
    "changes": [...],
    "preview": False
})
```

## Loading State System

The DevTools include robust component verification:

1. **Automatic Verification**: Checks if component actually loaded
2. **Smart Retries**: Up to 3 attempts with different strategies
3. **Clear Feedback**: Shows what was expected vs what was found

**How it works:**
```python
# The system checks:
# 1. loaded_component field matches expected
# 2. Component-specific classes exist in HTML
# 3. Retries with alternative navigation if needed
```

## Troubleshooting Guide

### Issue 1: "Component not loading"

**Symptoms:**
- Navigation returns success but wrong component shown
- Changes fail with "selector not found"

**Solution:**
```python
# Use debug workflow to diagnose
result = await devtools_request("ui_workflow", {
    "workflow": "debug_component",
    "component": "hermes"
})
# Check the recommendations in visual_feedback
```

### Issue 2: "Area vs Component Confusion"

**Remember:**
- Navigate to `component` (hermes, rhetor, etc.)
- Capture/modify `area` (content, navigation, etc.)
- After navigation, ALWAYS use `area="content"`

### Issue 3: "Response Structure"

**Finding elements:**
```python
# Wrong paths:
elements = result["elements"]  # ❌
elements = result["result"]["elements"]  # ❌

# Correct path:
elements = result["result"]["structure"]["elements"]  # ✅
```

### Issue 4: "Terminal Panel Active"

**Symptom:** Components hidden behind terminal

**Solution:** The debug workflow will detect this and suggest switching to HTML view.

## Best Practices

1. **Always use ui_workflow first** - It handles most complexity
2. **Preview changes** - Set `preview=True` before applying
3. **Use debug workflow when confused** - It provides actionable diagnostics
4. **Check response structure** - Elements are in `result["result"]["structure"]["elements"]`
5. **Wait after navigation** - Use `asyncio.sleep(1)` in manual workflows

## Error Messages

V2 provides helpful error context:

```
Error: Failed to apply changes to rhetor
Details: Selector '.rhetor__footer' not found
Failed selector: .rhetor__footer
Available selectors: ['.rhetor__header', '#rhetor-content', '.rhetor-tab']
Loaded component: profile (expected: rhetor)
Suggestion: The selector '.rhetor__footer' was not found. Try one of these: .rhetor__header, #rhetor-content
```

## Technical Implementation

### Key Files

1. **Core Implementation**
   - `/hephaestus/mcp/workflow_tools.py` - Main workflow implementation
   - `/hephaestus/mcp/workflow_tools_v2.py` - V2 improvements
   - `/hephaestus/mcp/ui_tools_v2.py` - Base UI tools
   - `/hephaestus/mcp/mcp_server.py` - Server registration

2. **Helpers**
   - `/hephaestus/mcp/validation_helpers.py` - Parameter validation
   - `/hephaestus/mcp/help_improvements.py` - Enhanced help content

3. **Examples & Tests**
   - `/examples/ui_devtools_example.py` - Clean usage examples
   - `/tests/test_ui_workflow.py` - Workflow tests

### Design Decisions

1. **Auto-detect area="content"** when component is provided
2. **Always wait after navigation** (1 second default)
3. **Verify component loaded** with retries
4. **Provide visual feedback** in responses
5. **Include debugging workflows** for troubleshooting

## Performance Metrics

**Before improvements:**
- Time to add status indicator: ~45 minutes
- Success rate: ~60% (but reported 100%)
- Error clarity: "Failed: None"

**After V2:**
- Time to add status indicator: ~1 minute with ui_workflow
- Success rate: ~95% (with verification and retries)
- Error clarity: Full context with suggestions
- Debug time: 1-2 minutes with clear next steps

## Future Improvements

1. **Screenshot reliability** - Make optional/graceful fallback
2. **Force component switching** - When navigation fails repeatedly
3. **Configurable timeouts** - Different workflows need different speeds
4. **Better loading signals** - Components could emit "ready" events

---

*This guide represents the current state of UI DevTools after V2 improvements. Built through collaborative iteration based on real-world usage and testing.*