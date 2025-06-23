# UI DevTools V2 API Reference

## Overview

This document provides complete API reference for the UI DevTools V2. All tools follow consistent patterns and return standardized results.

## Tool Result Format

All tools return a `ToolResult` object with this structure:

```python
{
    "tool": "tool_name",
    "status": "success" | "warning" | "error",
    "component": "component_name",  # Optional
    "data": {...},                  # Tool-specific data
    "error": "error message",       # Only on error
    "warnings": ["warning1", ...]   # Optional warnings
}
```

## CodeReader API

### Purpose
Read component source files to establish ground truth.

### Methods

#### `read_component(component_name: str) -> ToolResult`
Read a component's HTML file and basic info.

```python
result = code_reader.read_component("rhetor")
# Returns:
{
    "tool": "CodeReader",
    "status": "success",
    "component": "rhetor",
    "data": {
        "file_path": "/path/to/rhetor-component.html",
        "exists": true,
        "content_size": 43726,
        "semantic_tags": {
            "total_count": 75,
            "by_name": {...},
            "summary": {...}
        }
    }
}
```

#### `list_semantic_tags(component_name: str) -> ToolResult`
Extract all data-tekton-* attributes from component.

```python
result = code_reader.list_semantic_tags("rhetor")
# Returns:
{
    "tool": "CodeReader",
    "status": "success",
    "component": "rhetor",
    "data": {
        "semantic_tags": {
            "total_count": 75,
            "by_name": {
                "action": [
                    {"value": "clear-chat", "element": "button", "full_name": "data-tekton-action"},
                    {"value": "send-message", "element": "button", "full_name": "data-tekton-action"}
                ],
                "area": [
                    {"value": "rhetor", "element": "div", "full_name": "data-tekton-area"}
                ]
                // ... more tags
            },
            "summary": {
                "action": ["clear-chat", "send-message", ...],
                "area": ["rhetor"],
                // ... more summaries
            }
        },
        "summary": {
            "total_tags": 75,
            "unique_tag_types": 24,
            "tag_types": ["action", "area", "component", ...]
        }
    }
}
```

#### `get_component_structure(component_name: str) -> ToolResult`
Get parsed HTML structure (limited depth).

```python
result = code_reader.get_component_structure("rhetor")
# Returns:
{
    "tool": "CodeReader",
    "status": "success",
    "component": "rhetor",
    "data": {
        "structure": {
            "tag": "div",
            "attributes": {
                "data-tekton-area": "rhetor",
                "data-tekton-component": "rhetor",
                "id": "rhetor-area"
            },
            "children": [...]
        },
        "has_component_root": true,
        "file_path": "/path/to/rhetor-component.html"
    }
}
```

#### `list_components() -> ToolResult`
List all available components.

```python
result = code_reader.list_components()
# Returns:
{
    "tool": "CodeReader",
    "status": "success",
    "data": {
        "components": ["apollo", "athena", "rhetor", ...],
        "count": 18,
        "base_path": "/path/to/ui/components"
    }
}
```

## BrowserVerifier API

### Purpose
Check what's actually in the browser DOM.

### Methods

#### `verify_component_loaded(component_name: str) -> ToolResult`
Check if component is loaded in DOM.

```python
result = await browser_verifier.verify_component_loaded("rhetor")
# Returns:
{
    "tool": "BrowserVerifier",
    "status": "success",
    "component": "rhetor",
    "data": {
        "loaded": true,
        "url": "http://localhost:8080/",
        "component_info": {
            "tagName": "div",
            "id": "rhetor-area",
            "className": "component-area",
            "hasChildren": true
        }
    }
}
```

#### `get_dom_semantic_tags(component_name: str) -> ToolResult`
Extract semantic tags from DOM.

```python
result = await browser_verifier.get_dom_semantic_tags("rhetor")
# Returns:
{
    "tool": "BrowserVerifier",
    "status": "success",
    "component": "rhetor",
    "data": {
        "semantic_tags": {
            "total_count": 146,
            "by_name": {...},  // Similar to CodeReader
            "summary": {...},
            "found": ["action", "area", "nav-item", ...],
            "count_by_type": {
                "nav-item": 18,
                "nav-target": 18,
                "action": 8,
                // ...
            }
        },
        "total_elements_with_tags": 57,
        "component_specific_tags_found": true
    }
}
```

#### `capture_dom_state(component_name: str) -> ToolResult`
Capture current DOM structure.

```python
result = await browser_verifier.capture_dom_state("rhetor")
# Returns:
{
    "tool": "BrowserVerifier",
    "status": "success",
    "component": "rhetor",
    "data": {
        "dom_structure": {
            "tag": "div",
            "attributes": {...},
            "children": [...]
        },
        "element_count": 121,
        "captured": true
    }
}
```

## Comparator API

### Purpose
Compare source code vs browser to understand differences.

### Methods

#### `compare_component(component_name: str) -> ToolResult`
Full comparison of component.

```python
result = await comparator.compare_component("rhetor")
# Returns:
{
    "tool": "Comparator",
    "status": "success",
    "component": "rhetor",
    "data": {
        "comparison": {
            "code_only_tags": [],  // Tags only in source
            "dom_only_tags": ["nav-item", "nav-target", "loading-state", ...],
            "in_both": ["action", "area", "component", ...],
            "tag_count_comparison": {
                "code": 75,
                "browser": 146,
                "difference": 71
            }
        },
        "dynamic_tag_categories": {
            "navigation": ["nav-item", "nav-target"],
            "loading": ["loading-component", "loading-started", "loading-state"],
            "state": ["state"],
            "list": ["list"],
            "unknown": []
        },
        "insights": [
            "✓ Browser enriches component with 71 additional tags",
            "✓ All static tag types from source are preserved in DOM",
            "📊 System adds 7 types of dynamic tags at runtime:",
            "  • Navigation: 2 types (nav-item, nav-target, etc.)",
            "  • Loading states: 3 types (loading indicators)",
            "  • Runtime state: 1 types (component state tracking)",
            "🎯 Component shows signs of healthy dynamic behavior"
        ],
        "summary": {
            "code_tags": 75,
            "browser_tags": 146,
            "static_tags_preserved": 24,
            "dynamic_tags_added": 7,
            "missing_from_dom": 0
        }
    }
}
```

#### `diagnose_missing_tags(component_name: str) -> ToolResult`
Diagnose why tags might be missing.

```python
result = await comparator.diagnose_missing_tags("rhetor")
# Returns:
{
    "tool": "Comparator",
    "status": "success",
    "component": "rhetor",
    "data": {
        "diagnosis": "All source tags are present in DOM"
        // OR if tags are missing:
        "diagnosis": {
            "missing_tags": ["menu-panel", "panel-active"],
            "missing_count": 2,
            "possible_causes": [
                "Panel tags may only appear when panels are active"
            ],
            "recommendations": [
                "Activate panels before verification",
                "Check component initialization"
            ]
        }
    }
}
```

#### `suggest_fixes(component_name: str) -> ToolResult`
Get fix suggestions based on comparison.

```python
result = await comparator.suggest_fixes("rhetor")
# Returns:
{
    "tool": "Comparator",
    "status": "success",
    "component": "rhetor",
    "data": {
        "suggestions": [
            {
                "type": "success",
                "message": "All static tags from source are present in DOM",
                "action": "No fixes needed for static tags"
            },
            {
                "type": "info",
                "message": "Found 2 navigation-related dynamic tags",
                "action": "These are expected for navigation functionality"
            }
        ]
    }
}
```

## Navigator API

### Purpose
Navigate to components reliably.

### Methods

#### `navigate_to_component(component_name: str, wait_for_ready: bool = True) -> ToolResult`
Navigate to a component.

```python
result = await navigator.navigate_to_component("rhetor", wait_for_ready=True)
# Returns:
{
    "tool": "Navigator",
    "status": "success",
    "component": "rhetor",
    "data": {
        "component_exists": true,
        "navigation_success": true,
        "component_ready": true,
        "current_url": "http://localhost:8080/",
        "load_method": "hash_navigation"
    }
}
```

#### `get_current_component() -> ToolResult`
Get currently loaded component.

```python
result = await navigator.get_current_component()
# Returns:
{
    "tool": "Navigator",
    "status": "success",
    "data": {
        "current_component": "rhetor",
        "loaded_components": ["rhetor"],
        "current_url": "http://localhost:8080/"
    }
}
```

#### `list_navigable_components() -> ToolResult`
List all navigable components.

```python
result = await navigator.list_navigable_components()
# Returns:
{
    "tool": "Navigator",
    "status": "success",
    "data": {
        "available_in_code": ["apollo", "athena", "rhetor", ...],
        "available_in_nav": ["apollo", "athena", "rhetor", ...],
        "total_components": 18
    }
}
```

## SafeTester API

### Purpose
Test changes without breaking production.

### Methods

#### `preview_change(component_name: str, changes: List[Dict]) -> ToolResult`
Preview changes without applying.

```python
changes = [
    {
        "type": "text",
        "selector": "[data-tekton-action='send-message']",
        "content": "Send Test Message"
    },
    {
        "type": "attribute",
        "selector": "[data-tekton-component='rhetor']",
        "name": "data-tekton-test",
        "value": "true"
    }
]

result = await safe_tester.preview_change("rhetor", changes)
# Returns:
{
    "tool": "SafeTester",
    "status": "success",
    "component": "rhetor",
    "data": {
        "preview_mode": true,
        "changes": 2,
        "would_break": false,
        "preview_results": [
            {
                "change_type": "text",
                "selector": "[data-tekton-action='send-message']",
                "would_break": false,
                "impact": "low",
                "description": "Would change text content of 1 element(s)",
                "elements_affected": 1,
                "new_value": "Send Test Message"
            },
            {
                "change_type": "attribute",
                "selector": "[data-tekton-component='rhetor']",
                "would_break": false,
                "impact": "medium",
                "description": "Would modify semantic tag 'data-tekton-test'",
                "elements_affected": 1
            }
        ]
    }
}
```

#### `validate_change(component_name: str, changes: List[Dict]) -> ToolResult`
Validate if changes are safe.

```python
result = await safe_tester.validate_change("rhetor", changes)
# Returns:
{
    "tool": "SafeTester",
    "status": "success",
    "component": "rhetor",
    "data": {
        "changes_validated": 2,
        "all_safe": true,
        "critical_issues": 0,
        "validations": [...],
        "recommendation": "All changes are safe to apply"
    }
}
```

#### `test_in_sandbox(component_name: str, changes: List[Dict]) -> ToolResult`
Test changes in isolated sandbox.

```python
result = await safe_tester.test_in_sandbox("rhetor", changes)
# Returns:
{
    "tool": "SafeTester",
    "status": "success",
    "component": "rhetor",
    "data": {
        "sandbox_mode": true,
        "changes_requested": 2,
        "changes_applied": 2,
        "changes_failed": 0,
        "validation": {
            "safe": true,
            "issues": [],
            "metrics": {
                "element_diff": 0,
                "semantic_tag_diff": 1
            }
        }
    }
}
```

## Change Types for SafeTester

### Text Changes
```python
{
    "type": "text",
    "selector": ".button-text",
    "content": "New Button Text"
}
```

### Attribute Changes
```python
{
    "type": "attribute",
    "selector": "#my-element",
    "name": "data-tekton-state",
    "value": "active"
}
```

### Style Changes
```python
{
    "type": "style",
    "selector": ".my-class",
    "styles": {
        "color": "red",
        "font-size": "16px"
    }
}
```

### Class Changes
```python
{
    "type": "class",
    "selector": ".element",
    "action": "add",  // or "remove", "toggle"
    "classes": ["active", "highlighted"]
}
```

### Element Changes
```python
{
    "type": "element",
    "selector": ".to-remove",
    "action": "remove"  // or "add"
}
```

## MCP Server Endpoints

### Execute Tool
```
POST http://localhost:8088/api/mcp/v2/execute
Content-Type: application/json

{
    "tool_name": "code_list_components",
    "arguments": {}
}
```

### List Tools
```
GET http://localhost:8088/api/mcp/v2/tools
```

### Health Check
```
GET http://localhost:8088/health
```

## Error Handling

All tools handle errors gracefully:

```python
# Example error response
{
    "tool": "CodeReader",
    "status": "error",
    "component": "nonexistent",
    "error": "Component 'nonexistent' not found in codebase"
}

# Example warning response
{
    "tool": "SafeTester",
    "status": "warning",
    "component": "rhetor",
    "warnings": ["Some changes are not safe to apply"],
    "data": {...}
}
```

## Best Practices

1. **Always check status** before accessing data
2. **Handle all three statuses**: success, warning, error
3. **Use type hints** when working with results
4. **Clean up browser resources** after use
5. **Log errors** for debugging

## Complete Example

```python
import asyncio
from ui_dev_tools.tools.code_reader import CodeReader
from ui_dev_tools.tools.browser_verifier import BrowserVerifier
from ui_dev_tools.tools.comparator import Comparator
from ui_dev_tools.core.models import ToolStatus

async def analyze_component(component_name: str):
    """Complete analysis of a component"""
    
    # 1. Read source
    code_reader = CodeReader()
    source_result = code_reader.list_semantic_tags(component_name)
    
    if source_result.status != ToolStatus.SUCCESS:
        print(f"Error reading source: {source_result.error}")
        return
    
    source_tags = source_result.data['semantic_tags']['total_count']
    print(f"Source has {source_tags} tags")
    
    # 2. Check browser
    browser_verifier = BrowserVerifier()
    browser_result = await browser_verifier.get_dom_semantic_tags(component_name)
    
    if browser_result.status != ToolStatus.SUCCESS:
        print(f"Error checking browser: {browser_result.error}")
        await browser_verifier.cleanup()
        return
    
    browser_tags = browser_result.data['semantic_tags']['total_count']
    print(f"Browser has {browser_tags} tags")
    
    # 3. Compare
    comparator = Comparator()
    compare_result = await comparator.compare_component(component_name)
    
    if compare_result.status == ToolStatus.SUCCESS:
        insights = compare_result.data['insights']
        for insight in insights:
            print(insight)
    
    # Cleanup
    await browser_verifier.cleanup()

# Run the analysis
asyncio.run(analyze_component("rhetor"))
```

This will output:
```
Source has 75 tags
Browser has 146 tags
✓ Browser enriches component with 71 additional tags
✓ All static tag types from source are preserved in DOM
📊 System adds 7 types of dynamic tags at runtime:
  • Navigation: 2 types (nav-item, nav-target, etc.)
  • Loading states: 3 types (loading indicators)
  • Runtime state: 1 types (component state tracking)
🎯 Component shows signs of healthy dynamic behavior
```