# UI DevTools Cookbook V2

*A practical guide for using the Hephaestus UI DevTools V2 - with the revolutionary "Code is Truth, Browser is Result" approach*

Created: 2025-01-16  
Last Updated: 2025-06-21  
Status: Active - New V2 tools with enhanced diagnostic capabilities

## Welcome to UI DevTools V2!

The new UI DevTools V2 revolutionize how we debug UI issues. Built on the philosophy **"Code is Truth, Browser is Result"**, they help you understand not just what's in the browser, but WHY it differs from your source code.

### Major Discovery 🎉
- **Source Code**: Components have 75+ semantic tags (rhetor example)
- **Browser DOM**: Shows 146 tags - MORE than source!
- **Key Insight**: Browser ADDS 71 dynamic tags for navigation, loading, and state
- **Reality**: Your components work perfectly - the system enriches them!

### What's New in V2 ✅
- **CodeReader** - Shows exactly what's in your source files (the truth)
- **BrowserVerifier** - Shows what's actually in the DOM (the result)
- **Comparator** - Reveals why they're different (dynamic enrichment)
- **Navigator** - Reliable component navigation
- **SafeTester** - Test changes without breaking production

### Philosophy Shift 🔄
- **Old Way**: "Can't find tags in browser" → Confusion
- **New Way**: "75 tags in source, 146 in browser" → Understanding

## Table of Contents
1. [Quick Start](#quick-start)
2. [Core Workflow](#core-workflow)
3. [Common Operations](#common-operations)
4. [Understanding Static vs Dynamic Tags](#understanding-static-vs-dynamic-tags)
5. [Pattern Library](#pattern-library)
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

### 3. Basic V2 Workflow
```python
# 1. Check source code (TRUTH)
result = await devtools_request("code_reader", {
    "component": "rhetor"
})
print(f"Source has {result['result']['semantic_tags']['total_count']} tags")

# 2. Check browser (RESULT)
result = await devtools_request("browser_verifier", {
    "component": "rhetor"
})
print(f"Browser has {result['result']['semantic_tags']['count']} tags")

# 3. Compare and understand (INSIGHT)
result = await devtools_request("comparator", {
    "component": "rhetor"
})
print(f"Browser added {len(result['result']['discrepancies']['dom_only_tags'])} dynamic tags")

# 4. Navigate safely
result = await devtools_request("navigator", {
    "component": "rhetor",
    "wait_for_ready": True
})

# 5. Test changes safely
result = await devtools_request("safe_tester", {
    "component": "rhetor",
    "changes": [{"selector": ".nav-label", "attribute": "data-test", "value": "true"}],
    "preview": True
})
```

### When to Use Each Tool

Following Casey's philosophy and the new approach:
- **Debugging missing tags** → Start with CodeReader (they're probably in source!)
- **Verifying changes worked** → Use BrowserVerifier 
- **Understanding differences** → Use Comparator
- **Making UI changes** → Use SafeTester with preview first
- **Navigating components** → Use Navigator with wait_for_ready

**Remember**: Always check source truth before assuming browser problems!

## Core Workflow

### The Three-Step Debug Process

1. **Read Source (Truth)**
   ```python
   # See what SHOULD be there
   source = await devtools_request("code_reader", {"component": "rhetor"})
   print(f"Source tags: {source['result']['semantic_tags']['total_count']}")
   ```

2. **Verify Browser (Result)**
   ```python
   # See what IS there
   browser = await devtools_request("browser_verifier", {"component": "rhetor"})
   print(f"Browser tags: {browser['result']['semantic_tags']['count']}")
   ```

3. **Compare (Understanding)**
   ```python
   # Understand WHY they're different
   comparison = await devtools_request("comparator", {"component": "rhetor"})
   print(comparison['result']['insights'])
   ```

### Key Discovery: Browser Enrichment

When you run the comparator on rhetor:
- Source: 75 tags (your design)
- Browser: 146 tags (runtime reality)
- Difference: 71 tags ADDED by the system

These added tags include:
- Navigation: `nav-item`, `nav-target` (36 instances)
- Loading: `loading-state`, `loading-component` (9 instances)
- State: `state`, `active` (26 instances)

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

## Understanding Static vs Dynamic Tags

### Static Tags (You Write These)
```html
<!-- In your component HTML -->
<div data-tekton-component="rhetor"
     data-tekton-area="rhetor"
     data-tekton-zone="header">
  <button data-tekton-action="send">Send</button>
</div>
```

These represent your design decisions:
- Component identity and structure
- Defined actions and behaviors
- Layout zones and panels

### Dynamic Tags (System Adds These)
```html
<!-- What appears in browser -->
<div data-tekton-component="rhetor"
     data-tekton-area="rhetor"
     data-tekton-zone="header"
     data-tekton-loading-state="loaded"      <!-- ADDED -->
     data-tekton-state="active">             <!-- ADDED -->
  <button data-tekton-action="send"
          data-tekton-nav-item="send-action"  <!-- ADDED -->
          data-tekton-active="false">         <!-- ADDED -->
    Send
  </button>
</div>
```

The system adds:
- Loading lifecycle tracking
- Navigation wiring
- State management
- Runtime behavior

### Why This Matters

**Old thinking**: "My tags are missing!" → Add more tags to source
**New thinking**: "Which tags should be static vs dynamic?" → Let system handle dynamic ones

## Things to Know

### 1. Components Load Correctly ✅
**Discovery**: All static tags from source DO load into the browser
**Reality**: The "missing tags" issue was a misunderstanding - tags were there all along!
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