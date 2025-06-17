# UI DevTools Cookbook

*A practical guide based on real experience using the Hephaestus UI DevTools*

Created: 2025-01-16  
Author: Claude (with Casey Koons)  
Based on: Actual experience renaming Budget → Penia

## Table of Contents
1. [Quick Start - The Golden Path](#quick-start---the-golden-path)
2. [Common Operations](#common-operations)
3. [What I Learned the Hard Way](#what-i-learned-the-hard-way)
4. [When to Use What](#when-to-use-what)
5. [Working Examples](#working-examples)
6. [Troubleshooting](#troubleshooting)
7. [Proposed Enhancements](#proposed-enhancements)

## Quick Start - The Golden Path

Here's the exact sequence that successfully renamed Budget → Penia:

### 1. Always Start with Health Check
```bash
curl -s http://localhost:8088/health
# Expected: {"status":"healthy","component":"hephaestus_ui_devtools","version":"0.1.0","port":8088}
```

### 2. Capture Current State (Know What You're Working With)
```bash
# Capture with specific selector:
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_capture",
    "arguments": {
      "area": "hephaestus",
      "selector": "[data-component=\"budget\"]"
    }
  }'

# Capture entire UI:
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_capture", 
    "arguments": {
      "area": "hephaestus"
    }
  }'

# Important: All tools use 'area' parameter, never 'component'!
```

### 3. Preview Changes in Sandbox
```bash
# This taught me about required parameters:
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_sandbox",
    "arguments": {
      "area": "hephaestus",  # NOT "component" - this is required!
      "changes": [
        {
          "type": "text",
          "selector": "[data-component=\"budget\"] .nav-label",
          "content": "Penia - LLM Cost",
          "action": "replace"
        }
      ],
      "preview": true
    }
  }'
```

### 4. Realize Some Things Need Manual Work
Moving elements between containers? DevTools can't do that elegantly yet. Time for manual editing.

### 5. Apply Changes Manually
```bash
# Edit the file directly for structural changes
vim /Users/cskoons/projects/github/Tekton/Hephaestus/ui/index.html
```

### 6. Verify Your Work
```bash
# Simple verification - grep the actual file
curl -s http://localhost:8080 | grep -B2 -A2 "Penia"
```

## Common Operations

### Renaming a Component (Text Only)
**When to use**: Changing display names without affecting functionality

```bash
# Preview the change first
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_sandbox",
    "arguments": {
      "area": "hephaestus",
      "changes": [{
        "type": "text",
        "selector": "[data-component=\"budget\"] .nav-label",
        "content": "Penia - LLM Cost",
        "action": "replace"
      }],
      "preview": true
    }
  }'

# Apply if preview looks good (preview: false)
```

### Removing Elements (Like Emojis)
**When to use**: Cleaning up UI elements

```bash
# Attempt to remove emoji (this partially worked)
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_sandbox",
    "arguments": {
      "area": "hephaestus",
      "changes": [{
        "type": "html",
        "selector": "[data-component=\"budget\"] .button-icon",
        "content": "",
        "action": "replace"
      }],
      "preview": true
    }
  }'
```

**Note**: For complex removals, manual editing is more reliable.

### Updating Attributes
**When to use**: Changing data attributes, classes, or IDs

```bash
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_sandbox",
    "arguments": {
      "area": "hephaestus",
      "changes": [{
        "type": "attribute",
        "selector": "[data-component=\"budget\"]",
        "attribute": "data-component",
        "value": "penia",
        "action": "update"
      }],
      "preview": true
    }
  }'
```

## What I Learned the Hard Way

### 1. `area` is Required, Not `component` for ui_sandbox
```bash
# WRONG - This will error
"arguments": {
  "component": "all",  # ❌ Error: unexpected keyword argument
  ...
}

# CORRECT
"arguments": {
  "area": "hephaestus",  # ✅ This works
  ...
}
```

### 2. Empty Capture Results Don't Mean Failure
When `ui_capture` returns `"element_count": 0`, it doesn't mean your selector is wrong. The DevTools might not be capturing dynamic content or the element might not exist in the current view state.

### 3. Moving Elements Between Parents is Complex
DevTools excel at in-place modifications but struggle with structural changes:
- ❌ Moving a nav item from footer to main nav
- ✅ Changing text within a nav item
- ✅ Adding/removing classes
- ❌ Reordering siblings across different parent containers

### 4. Preview Mode Shows Partial Success
The response `"successful": 1, "failed": 1` tells you exactly which changes worked. Use this to understand what DevTools can and cannot do.

## When to Use What

### Use DevTools For:
- **Text changes**: Renaming labels, updating content
- **Attribute updates**: Changing data attributes, IDs, classes  
- **Style modifications**: Adding inline styles
- **Content removal**: Emptying elements
- **Quick verification**: Checking current state

### Use Manual Editing For:
- **Structural changes**: Moving elements between containers
- **Complex refactoring**: Multiple related changes
- **Parent-child reorganization**: Changing the DOM hierarchy
- **Batch operations**: Multiple similar changes across files

### Use Both:
1. DevTools to verify current state
2. Manual edit for the change
3. DevTools to confirm success

## Working Examples

### Example 1: CSS Changes (Two Formats)
```bash
# Format 1: Property/Value (for single CSS property)
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_sandbox",
    "arguments": {
      "area": "hephaestus",
      "changes": [{
        "type": "css",
        "selector": ".nav-item",
        "property": "border",
        "value": "2px solid blue"
      }],
      "preview": true
    }
  }'

# Format 2: Full CSS Rules (for multiple properties)
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_sandbox",
    "arguments": {
      "area": "hephaestus",
      "changes": [{
        "type": "css",
        "content": ".nav-item { border: 2px solid blue; padding: 10px; }"
      }],
      "preview": true
    }
  }'
```

### Example 2: Simple Text Change (Success)
```bash
# This works perfectly for in-place text updates
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_sandbox",
    "arguments": {
      "area": "hephaestus",
      "changes": [{
        "type": "text",
        "selector": ".nav-label",
        "content": "New Label Text",
        "action": "replace"
      }],
      "preview": true
    }
  }'
```

### Example 2: Parameter Confusion (Failure → Success)
```bash
# FAILS - Wrong parameter name
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{"tool_name": "ui_capture", "arguments": {"component": "all"}}'  # ❌ No 'component' param!
# Error: 400: Required parameter 'area' not provided

# SUCCEEDS - Correct parameter
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{"tool_name": "ui_capture", "arguments": {"area": "hephaestus"}}'
```

### Example 3: Complex Operation (Manual Required)
```bash
# Task: Move Budget from footer to main nav
# DevTools can't elegantly handle this

# Step 1: Capture current HTML
curl -s http://localhost:8080 | grep -A5 "data-component=\"budget\""

# Step 2: Manually edit the file
# - Cut the <li> element from footer section
# - Paste it in the main nav section
# - Save the file

# Step 3: Verify the change
curl -s http://localhost:8080 | grep -B2 -A2 "Penia"
```

## Troubleshooting

### "Required parameter 'area' not provided"
**Problem**: Using wrong parameter names  
**Solution**: Use `area` not `component` for ui_sandbox

### Empty Capture Results
**Problem**: `ui_capture` returns no elements  
**Solution**: 
- Try broader selectors
- Use `"area": "hephaestus"` instead of specific selectors
- Check if the UI is actually running on port 8080

### Selector Not Working
**Problem**: Your CSS selector doesn't match any elements  
**Solution**:
- Verify selector syntax
- Use browser DevTools to test selectors first
- Try simpler selectors: `[data-component="budget"]` instead of complex chains

### Changes Not Applying
**Problem**: Preview works but actual changes don't stick  
**Solution**:
- Some changes require page reload
- Complex changes might need manual editing
- Check browser console for JavaScript errors

## Batch Operations (IMPLEMENTED)

### ui_batch - Execute Multiple Operations

The `ui_batch` tool allows you to perform multiple UI operations in a single call, with optional atomic rollback support.

#### Basic Usage
```bash
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_batch",
    "arguments": {
      "area": "hephaestus",
      "operations": [
        {"action": "rename", "from": "Budget", "to": "Penia"},
        {"action": "remove", "selector": "[data-component=\"penia\"] .button-icon"},
        {"action": "style", "selector": ".penia", "styles": {"border": "2px solid green"}}
      ],
      "atomic": true
    }
  }'
```

#### Available Actions

1. **rename** - Change text content
   ```json
   {"action": "rename", "from": "Old Text", "to": "New Text"}
   ```

2. **remove** - Remove elements
   ```json
   {"action": "remove", "selector": ".element-to-remove"}
   ```

3. **add_class** - Add CSS classes
   ```json
   {"action": "add_class", "selector": ".nav-item", "class": "highlight"}
   ```

4. **remove_class** - Remove CSS classes
   ```json
   {"action": "remove_class", "selector": ".nav-item", "class": "highlight"}
   ```

5. **style** - Apply CSS styles
   ```json
   {"action": "style", "selector": ".element", "styles": {"color": "red", "font-size": "16px"}}
   ```

6. **navigate** - Navigate to component
   ```json
   {"action": "navigate", "component": "rhetor"}
   ```

7. **click** - Click elements
   ```json
   {"action": "click", "selector": "button.submit"}
   ```

#### Atomic Mode

- **atomic: true** (default) - All operations must succeed or all are rolled back
- **atomic: false** - Each operation is independent, partial success allowed

#### Example: Complete UI Refactoring
```bash
# Rename component, remove emoji, update styles - all atomic
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_batch",
    "arguments": {
      "area": "hephaestus",
      "operations": [
        {"action": "navigate", "component": "budget"},
        {"action": "rename", "from": "Budget", "to": "Penia - LLM Cost"},
        {"action": "remove", "selector": "[data-component=\"budget\"] .button-icon"},
        {"action": "add_class", "selector": "[data-component=\"budget\"]", "class": "updated"},
        {"action": "style", "selector": ".updated", "styles": {"background": "rgba(0,255,0,0.1)"}}
      ],
      "atomic": true
    }
  }'
```

## Proposed Enhancements

### 1. Help Endpoint
Add to `/Hephaestus/hephaestus/mcp/mcp_server.py`:

```python
@app.get("/help")
async def help():
    """Return available tools and their parameters."""
    return {
        "tools": {
            "ui_capture": {
                "description": "Capture UI structure and content",
                "parameters": {
                    "area": "UI area to capture (required) - use 'hephaestus' for main UI",
                    "selector": "CSS selector to filter results (optional)"
                },
                "examples": [
                    {
                        "description": "Capture entire UI",
                        "arguments": {"area": "hephaestus"}
                    },
                    {
                        "description": "Capture specific component",
                        "arguments": {"area": "hephaestus", "selector": "[data-component='budget']"}
                    }
                ]
            },
            "ui_sandbox": {
                "description": "Test UI changes safely with preview mode",
                "parameters": {
                    "area": "UI area (required)",
                    "changes": "Array of change operations",
                    "preview": "Boolean - if true, shows what would change without applying"
                },
                "change_types": ["text", "html", "attribute"],
                "actions": ["replace", "append", "prepend", "remove", "update"]
            },
            "ui_interact": {
                "description": "Interact with UI elements",
                "parameters": {
                    "area": "UI area (required)",
                    "action": "click, type, select, etc.",
                    "selector": "Target element selector",
                    "value": "Value for type actions (optional)"
                }
            },
            "ui_analyze": {
                "description": "Analyze UI for frameworks and patterns",
                "parameters": {
                    "area": "UI area (required)",
                    "deep_scan": "Boolean - perform detailed analysis"
                }
            }
        }
    }
```

### 2. Move Operation
Add support for moving elements:

```json
{
  "type": "move",
  "selector": "[data-component=\"budget\"]",
  "target": "[data-component=\"rhetor\"]",
  "position": "after"  // or "before", "prepend", "append"
}
```

### 3. Batch Operations
Allow multiple operations in a transaction:

```json
{
  "tool_name": "ui_batch",
  "arguments": {
    "area": "hephaestus",
    "operations": [
      {"action": "rename", "from": "Budget", "to": "Penia"},
      {"action": "remove_emoji", "component": "penia"},
      {"action": "move", "component": "penia", "after": "rhetor"}
    ],
    "atomic": true  // All succeed or all fail
  }
}
```

### 4. Debug Mode
Add debug information for failed selectors:

```json
{
  "tool_name": "ui_capture",
  "arguments": {
    "area": "hephaestus",
    "selector": "[data-component=\"budget\"]",
    "debug": true  // Returns why selector failed
  }
}
```

### 5. Validation Tool
Check UI consistency:

```json
{
  "tool_name": "ui_validate",
  "arguments": {
    "area": "hephaestus",
    "checks": ["navigation", "semantic-tags", "data-attributes"]
  }
}
```

## New Features (Added 2025-06-16)

### Navigation Tool
Navigate to components before working with them:

```bash
# Navigate to a component
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_navigate",
    "arguments": {
      "component": "prometheus"
    }
  }'
```

**Important**: The nav item might not show as "active" due to UI implementation, but the component will be loaded.

### Component State Detection
Every ui_capture now includes state information:

```json
{
  "active_nav_item": "tekton",        // What nav shows as active
  "loaded_component": "prometheus",    // What's actually loaded
  "working_with": "prometheus",        // What you should work with
  "state_mismatch": true,             // If nav and content don't match
  "state_note": "Navigation shows 'tekton' but content shows 'prometheus'"
}
```

### Better Selector Feedback
When selectors fail, you now get suggestions:

```bash
# If selector not found
{
  "selector_error": "No matches for '.prometheus-header'. Try: .prometheus__header, .prometheus__title-container, .prometheus__menu-bar",
  "suggestions": [
    ".prometheus__header",
    ".prometheus__title-container", 
    ".prometheus__menu-bar"
  ]
}
```

### Updated Workflow
The recommended workflow is now:

1. **Navigate** to the component you want to work with
2. **Capture** to see structure and verify state
3. **Modify** using ui_sandbox
4. **Verify** changes took effect

```bash
# Complete example
# 1. Navigate
curl -X POST http://localhost:8088/api/mcp/v2/execute -d '{"tool_name":"ui_navigate","arguments":{"component":"rhetor"}}'

# 2. Capture and check state
curl -X POST http://localhost:8088/api/mcp/v2/execute -d '{"tool_name":"ui_capture","arguments":{"area":"rhetor"}}' | jq '.result.working_with'

# 3. Make changes
curl -X POST http://localhost:8088/api/mcp/v2/execute -d '{"tool_name":"ui_sandbox","arguments":{"area":"rhetor","changes":[{"type":"text","selector":".rhetor__title","content":"Updated Title","action":"replace"}],"preview":true}}'
```

## Related Documentation

- [UI Navigation Patterns](../Patterns/UINavigationPatterns.md) - Component structure and naming conventions
- [UI DevTools Explicit Guide](UIDevToolsExplicitGuide.md) - Complete tool reference
- [Semantic UI Navigation Guide](SemanticUINavigationGuide.md) - Semantic tagging system
- [Hephaestus UI Architecture](../../Architecture/HephaestusUIArchitecture.md) - How the UI works

---

*Remember: The best tool is the one that gets the job done. Sometimes that's a curl command, sometimes it's vim.*