# UI DevTools Cookbook

*A practical guide for using the Hephaestus UI DevTools based on real experience*

Created: 2025-01-16  
Last Updated: 2025-01-17  
Status: Active - Reflects current tool capabilities and known issues

## 🚨 CRITICAL: Read This First

**The UI DevTools are REQUIRED for all Hephaestus UI work. NO BLIND CHANGES.**

### Known Major Issue: DynamicContentView Problem
- **Issue**: DevTools cannot see dynamically loaded component content
- **Symptom**: `ui_navigate` reports success but `ui_capture` only sees initial HTML
- **Workaround**: Edit component HTML files directly for structural changes
- **Status**: Under investigation

## Table of Contents
1. [Quick Start](#quick-start)
2. [Common Operations](#common-operations)
3. [Known Issues & Workarounds](#known-issues--workarounds)
4. [Pattern Library](#pattern-library)
5. [Anti-Patterns](#anti-patterns)
6. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Always Start the MCP Server
```bash
# Check if running
curl http://localhost:8088/health

# If not, start it
cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh
```

### 2. Python Setup (Recommended over curl)
```python
import httpx
import asyncio

MCP_URL = "http://localhost:8088/api/mcp/v2/execute"

async def devtools_request(tool_name, arguments):
    async with httpx.AsyncClient() as client:
        response = await client.post(MCP_URL, json={
            "tool_name": tool_name,
            "arguments": arguments
        })
        return response.json()
```

### 3. Basic Workflow
```python
# 1. Capture current state
result = await devtools_request("ui_capture", {"area": "rhetor"})

# 2. Test changes with preview
result = await devtools_request("ui_sandbox", {
    "area": "rhetor",
    "changes": [{
        "type": "text",
        "selector": ".nav-label",
        "content": "New Text",
        "action": "replace"
    }],
    "preview": True  # ALWAYS preview first!
})

# 3. Apply if preview succeeds
if result['status'] == 'success':
    result = await devtools_request("ui_sandbox", {
        "area": "rhetor",
        "changes": [...],
        "preview": False
    })
```

## Common Operations

### Renaming a Component (Working Example)
```python
# Successfully renamed Budget → Penia
changes = [
    {
        "type": "text",
        "selector": "[data-component='budget'] .nav-label",
        "content": "Penia - LLM Cost",
        "action": "replace"
    },
    {
        "type": "attribute", 
        "selector": "[data-component='budget'] .nav-label",
        "attribute": "data-greek-name",
        "value": "Penia - LLM Cost"
    }
]
```

### Adding Semantic Tags
```python
# Add data-tekton attributes
changes = [{
    "type": "attribute",
    "selector": ".rhetor__header",
    "attribute": "data-tekton-zone",
    "value": "header"
}]
```

### Modifying Component Footer
```python
# Add to footer (simple HTML only)
changes = [{
    "type": "html",
    "selector": "#rhetor-footer",
    "content": '<span style="color: #666;">Status: Ready</span>',
    "action": "append"
}]
```

## Known Issues & Workarounds

### 1. DynamicContentView Problem ⚠️
**Issue**: Cannot capture dynamically loaded components
```python
# This sequence SHOULD work but doesn't:
await devtools_request("ui_navigate", {"component": "rhetor"})
await asyncio.sleep(2)  # Wait for load
result = await devtools_request("ui_capture", {"area": "rhetor"})
# Result shows profile/initial page, not rhetor!
```

**Workaround**: Edit component files directly
```python
# Instead of DevTools, edit the file:
with open('ui/components/rhetor/rhetor-component.html', 'r+') as f:
    content = f.read()
    # Make changes
    f.write(content)
```

### 2. Structural Changes Limited
**Issue**: Moving elements between containers often fails
```python
# This typically fails:
changes = [{
    "type": "move",
    "selector": "#element",
    "target": "#new-container"
}]
```

**Workaround**: Use replace operations or edit HTML directly

### 3. Framework Detection Overzealous
**Issue**: Any mention of React/Vue/Angular triggers rejection
```python
# Even comments with "React" get rejected!
```

**Workaround**: Use alternative wording in content

## Pattern Library

### Pattern: Safe Text Updates
```python
# Always use preview first
async def safe_text_update(selector, new_text):
    # Preview
    result = await devtools_request("ui_sandbox", {
        "area": "hephaestus",
        "changes": [{
            "type": "text",
            "selector": selector,
            "content": new_text,
            "action": "replace"
        }],
        "preview": True
    })
    
    if result['status'] == 'success':
        # Apply
        result['preview'] = False
        return await devtools_request("ui_sandbox", result['arguments'])
    return result
```

### Pattern: Batch Operations
```python
# Group related changes
changes = [
    {"type": "text", "selector": ".title", "content": "New Title", "action": "replace"},
    {"type": "attribute", "selector": ".title", "attribute": "data-updated", "value": "true"},
    {"type": "css", "selector": ".title", "property": "color", "value": "#007bff"}
]
```

### Pattern: Component Discovery
```python
# Find all components in navigation
result = await devtools_request("ui_capture", {
    "area": "hephaestus",
    "selector": "[data-component]"
})
```

## Anti-Patterns

### ❌ DON'T: Use DevTools for Major Structural Changes
```python
# This won't work reliably
# DON'T try to rebuild component structure via DevTools
```

### ❌ DON'T: Skip Preview
```python
# WRONG - Always preview first!
await devtools_request("ui_sandbox", {
    "changes": [...],
    "preview": False  # NO!
})
```

### ❌ DON'T: Add Frameworks
```python
# This gets rejected immediately
content = '<script src="react.js"></script>'  # BLOCKED
```

### ❌ DON'T: Use Complex Selectors
```python
# Keep selectors simple
# BAD: ":nth-child(3) > div:not(.hidden) + span"
# GOOD: "#specific-id" or ".specific-class"
```

## Troubleshooting

### MCP Not Responding
```bash
# Check if running
lsof -i :8088

# Restart if needed
pkill -f "mcp_server"
cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh
```

### Changes Not Visible
1. Check preview succeeded first
2. Verify selector matches exactly one element
3. Check browser cache (force refresh)
4. Verify Hephaestus UI is running

### "Cannot read property" Errors
- Usually means selector didn't match any elements
- Use ui_capture first to verify element exists
- Check for typos in selector

### Framework Rejection
- Remove ALL mentions of React/Vue/Angular
- Check content for framework-related terms
- Use vanilla JS/HTML only

## Best Practices Summary

1. **Always use preview mode first**
2. **Keep changes simple and atomic**
3. **Use semantic tags (data-tekton-*)**
4. **Test one change at a time**
5. **For structural changes, edit files directly**
6. **Document what you did for next Claude session**

## When to Use What

- **ui_capture**: Understanding current state, finding elements
- **ui_sandbox**: Text changes, attributes, simple HTML additions
- **ui_analyze**: Checking for framework contamination
- **Direct file editing**: Structural changes, new components, major updates

---

For complete API reference, see: `UIDevToolsReference.md`  
For semantic tagging standards, see: `SemanticUINavigationGuide.md`