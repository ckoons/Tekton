# UI DevTools Cookbook

*A practical guide for using the Hephaestus UI DevTools - now with working tools!*

Created: 2025-01-16  
Last Updated: 2025-06-17  
Status: Active - Tools are functional with some limitations

## Welcome to UI DevTools!

The Hephaestus UI DevTools help you modify and inspect the UI without diving into code files. They're designed with Casey's philosophy: **"Keep it simple, ask questions when unsure, and state clearly what you know and why."**

### What's Working Well ✅
- **ui_capture** returns full DOM structure with accurate element counts
- **ui_capture** includes raw HTML for searching and debugging
- **ui_sandbox** can successfully modify elements (text, attributes, CSS)
- Clear error messages when selectors aren't found
- Proper handling of complex selectors with quotes

### Current Limitation 🔧
- **DynamicContentView**: Components loaded via JavaScript aren't immediately visible
- **Impact**: After navigating to a component, the content may not be captured
- **Workaround**: For dynamically loaded content, edit component HTML files directly
- **Status**: This is a known limitation we're working on

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
print(f"Found {result['result']['structure']['element_count']} elements")
print(f"Available selectors: {result['result']['selectors_available']}")

# 2. Search the HTML if needed
if ".nav-label" in result['result']['html']:
    print("Found navigation labels!")

# 3. Make changes (preview is optional but recommended)
result = await devtools_request("ui_sandbox", {
    "area": "rhetor",
    "changes": [{
        "type": "text",
        "selector": ".nav-label",
        "content": "New Text",
        "action": "replace"
    }],
    "preview": True  # Preview first to test
})

# 4. Apply if preview succeeds
if result['status'] == 'success' and result['result']['summary']['successful'] > 0:
    result = await devtools_request("ui_sandbox", {
        "area": "rhetor",
        "changes": [...],
        "preview": False
    })
```

### When to Ask Questions

Following Casey's guidance, if you're unsure about:
- Which selector to use → Check `selectors_available` in ui_capture
- Whether a change will work → Use preview mode
- Why something failed → Check the error message
- Whether to use DevTools or edit files → Try DevTools first for simple changes

**Remember**: It's better to ask "Should I use DevTools or edit the HTML file directly?" than to guess!

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

## Things to Know

### 1. DynamicContentView Limitation 📋
**What happens**: Components loaded via JavaScript aren't immediately visible to DevTools
```python
# Example scenario:
await devtools_request("ui_navigate", {"component": "rhetor"})
await asyncio.sleep(2)  # Wait for load
result = await devtools_request("ui_capture", {"area": "rhetor"})
# May still show the initial page content
```

**What to do**: 
- For static content in navigation/headers → DevTools work great!
- For dynamic component content → Edit the component HTML file directly
- Not sure which? Try DevTools first, then fall back to file editing

### 2. Complex DOM Manipulations 🔧
**What works**: Text changes, attributes, CSS, simple HTML additions
**What doesn't**: Moving elements between containers, complex restructuring

**Approach**: Start simple! If you need to restructure the DOM significantly, that's a good time to ask: "Would this be better done in the HTML file?"

### 3. Framework Mentions 🚫
**Current behavior**: The system blocks content containing "React", "Vue", "Angular"
**Why**: Previous sessions tried to add frameworks when asked to keep things simple

**If you need to**: Use alternative wording or ask Casey about the specific use case

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

## Tips for Success

### 💡 Start with ui_capture
Before making changes, always capture first to see what's available:
```python
result = await devtools_request("ui_capture", {"area": "hephaestus"})
# Check selectors_available to see what you can target
# Search the HTML to verify your selector exists
```

### 💡 Use Preview Mode for Testing
Preview mode is your friend - it shows what will happen without applying changes:
```python
# Test first
result = await devtools_request("ui_sandbox", {
    "changes": [...],
    "preview": True  # See what will happen
})
```

### 💡 Keep Selectors Simple
Complex selectors are harder to debug:
```python
# Simple and clear:
"#specific-id"
".specific-class" 
"[data-component='prometheus']"

# Avoid unless necessary:
":nth-child(3) > div:not(.hidden) + span"
```

### 💡 When to Switch to File Editing
If you find yourself:
- Needing to restructure large parts of the DOM
- Working with dynamically loaded component content
- Making changes that require multiple complex operations

Consider asking: "Would this be simpler to do in the HTML file?"

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

### The DevTools Philosophy
Following Casey's approach: **Keep it simple, be clear about what you know, and ask when unsure.**

### Practical Guidelines
1. **Start with ui_capture** - See what's available before making changes
2. **Use the HTML search** - The raw HTML in responses is your friend
3. **Preview when testing** - But don't be afraid to apply changes directly when confident
4. **Keep changes focused** - One clear change is better than five complex ones
5. **Ask when stuck** - "Should I use DevTools or edit the file?" is a great question

### When to Use Each Tool

**ui_capture** ✅ Great for:
- Seeing the page structure and element counts
- Finding available selectors
- Searching for specific content in HTML
- Understanding what you're working with

**ui_sandbox** ✅ Great for:
- Changing text content
- Adding/modifying attributes
- Applying CSS styles
- Testing changes before applying

**Direct file editing** 📝 Better for:
- Major structural changes
- Working with dynamically loaded components
- Creating new components
- Complex multi-step modifications

### Success Metrics
With the recent improvements, you should expect:
- ✅ ui_capture to show actual element counts (not just 1)
- ✅ ui_sandbox to successfully modify elements
- ✅ Clear error messages when selectors aren't found
- ✅ HTML content for searching and debugging

If something seems broken, check the error message first - it's probably trying to tell you something helpful!

---

## Related Documentation

- **What's New**: `UIDevToolsWhatsNew.md` - Recent improvements and fixes
- **API Reference**: `UIDevToolsReference.md` - Complete tool documentation  
- **Semantic Tags**: `SemanticUINavigationGuide.md` - UI tagging standards

Remember: The tools are here to help you work efficiently. When in doubt, ask!