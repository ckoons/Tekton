# UI DevTools API Reference

*Complete API documentation for the Hephaestus UI DevTools MCP*

Version: 0.1.0  
Port: 8088  
Protocol: HTTP REST API

## API Endpoint

All tools are accessed through a single endpoint:
```
POST http://localhost:8088/api/mcp/v2/execute
```

## Authentication

No authentication required for local development.

## Request Format

```json
{
  "tool_name": "tool_name_here",
  "arguments": {
    // tool-specific arguments
  }
}
```

## Available Tools

### 1. ui_capture

Captures the current UI state without screenshots.

**Parameters:**
- `area` (required): Target area to capture
  - Options: "hephaestus", "rhetor", "hermes", etc.
- `selector` (optional): CSS selector to capture specific element

**Request:**
```json
{
  "tool_name": "ui_capture",
  "arguments": {
    "area": "rhetor",
    "selector": "#rhetor-footer"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "area": "rhetor",
    "ui_url": "http://localhost:8080",
    "current_url": "http://localhost:8080/",
    "loaded_component": "profile",  // Note: May not match requested area
    "structure": {
      "element_count": 245,
      "elements": [...]
    }
  }
}
```

### 2. ui_sandbox

Test UI changes in a sandboxed environment before applying.

**Parameters:**
- `area` (required): Target area
- `changes` (required): Array of change objects
- `preview` (required): Boolean - true to preview, false to apply

**Change Types:**

#### HTML Changes
```json
{
  "type": "html",
  "selector": "#target",
  "content": "<span>HTML content</span>",
  "action": "replace"  // or "append", "prepend", "before", "after"
}
```

#### Text Changes
```json
{
  "type": "text",
  "selector": ".nav-label",
  "content": "New Text Content",
  "action": "replace"
}
```

#### Attribute Changes
```json
{
  "type": "attribute",
  "selector": "#element",
  "attribute": "data-tekton-zone",
  "value": "header"
}
```

#### CSS Changes (Format 1: Property/Value)
```json
{
  "type": "css",
  "selector": ".element",
  "property": "background-color",
  "value": "rgba(255,255,255,0.1)"
}
```

#### CSS Changes (Format 2: Full Rules)
```json
{
  "type": "css",
  "selector": ".element",
  "rules": {
    "color": "#007bff",
    "font-size": "16px"
  }
}
```

**Full Request Example:**
```json
{
  "tool_name": "ui_sandbox",
  "arguments": {
    "area": "rhetor",
    "changes": [
      {
        "type": "text",
        "selector": ".nav-label",
        "content": "New Label",
        "action": "replace"
      },
      {
        "type": "attribute",
        "selector": ".nav-label",
        "attribute": "data-updated",
        "value": "true"
      }
    ],
    "preview": true
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "area": "rhetor",
    "preview": true,
    "validations": [
      {
        "change_index": 0,
        "status": "valid",
        "elements_matched": 1
      }
    ],
    "summary": {
      "total_changes": 2,
      "successful": 2,
      "failed": 0
    }
  }
}
```

### 3. ui_navigate

Navigate to a specific component by clicking its navigation item.

**Parameters:**
- `component` (required): Component name to navigate to

**Request:**
```json
{
  "tool_name": "ui_navigate",
  "arguments": {
    "component": "rhetor"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "navigated_to": "rhetor",
    "navigation_method": "click"
  }
}
```

**⚠️ Known Issue:** Navigation reports success but dynamically loaded content is not visible to ui_capture.

### 4. ui_interact

Interact with UI elements (click, type, select).

**Parameters:**
- `area` (required): Target area
- `action` (required): Action type ("click", "type", "select")
- `selector` (required): CSS selector for target element
- `value` (optional): Value for type/select actions

**Examples:**

#### Click
```json
{
  "tool_name": "ui_interact",
  "arguments": {
    "area": "rhetor",
    "action": "click",
    "selector": "button#submit"
  }
}
```

#### Type
```json
{
  "tool_name": "ui_interact",
  "arguments": {
    "area": "rhetor",
    "action": "type",
    "selector": "input#name",
    "value": "Hello World"
  }
}
```

#### Select
```json
{
  "tool_name": "ui_interact",
  "arguments": {
    "area": "rhetor",
    "action": "select",
    "selector": "select#options",
    "value": "option2"
  }
}
```

### 5. ui_analyze

Analyze UI structure and detect potential issues.

**Parameters:**
- `area` (required): Target area
- `deep_scan` (optional): Boolean - perform deep analysis

**Request:**
```json
{
  "tool_name": "ui_analyze",
  "arguments": {
    "area": "rhetor",
    "deep_scan": true
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "area": "rhetor",
    "analysis": {
      "structure": {
        "total_elements": 245,
        "by_type": {
          "div": 120,
          "button": 25,
          "input": 15
        }
      },
      "complexity": {
        "level": "medium",
        "score": 6.5
      },
      "frameworks": {
        "react": false,
        "vue": false,
        "angular": false
      },
      "semantic_tags": {
        "data-tekton-area": 1,
        "data-tekton-component": 1,
        "data-tekton-zone": 4
      }
    },
    "recommendations": [
      {
        "type": "semantic",
        "message": "Add data-tekton-panel attributes to content panels"
      }
    ]
  }
}
```

### 6. ui_validate

Validate UI instrumentation and semantic tagging.

**Parameters:**
- `area` (required): Target area
- `rules` (optional): Validation rules to apply

**Request:**
```json
{
  "tool_name": "ui_validate",
  "arguments": {
    "area": "rhetor"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "area": "rhetor",
    "validation": {
      "semantic_coverage": 0.85,
      "missing_tags": [
        "data-tekton-nav on menu items",
        "data-tekton-panel on content areas"
      ],
      "issues": [],
      "score": 8.5
    }
  }
}
```

### 7. ui_batch

Execute multiple UI operations in a batch with atomic support.

**Parameters:**
- `operations` (required): Array of operations
- `atomic` (optional): Boolean - all or nothing execution

**Request:**
```json
{
  "tool_name": "ui_batch",
  "arguments": {
    "operations": [
      {
        "tool": "ui_capture",
        "arguments": {"area": "rhetor"}
      },
      {
        "tool": "ui_sandbox",
        "arguments": {
          "area": "rhetor",
          "changes": [...],
          "preview": true
        }
      }
    ],
    "atomic": true
  }
}
```

### 8. ui_help

Get help about UI DevTools usage.

**Parameters:**
- `topic` (optional): Specific help topic
- `format` (optional): "text" or "markdown"

**Request:**
```json
{
  "tool_name": "ui_help",
  "arguments": {
    "topic": "sandbox",
    "format": "text"
  }
}
```

## Error Responses

### Framework Detection Error
```json
{
  "status": "error",
  "error": "Change rejected: Detected framework patterns",
  "details": {
    "patterns_found": ["import React", "Vue.component"],
    "recommendation": "Use vanilla HTML/JS only"
  }
}
```

### Selector Not Found
```json
{
  "status": "error",
  "error": "No elements matched selector: #non-existent",
  "details": {
    "selector": "#non-existent",
    "area": "rhetor"
  }
}
```

### Invalid Parameters
```json
{
  "status": "error",
  "error": "400: Required parameter 'area' not provided"
}
```

## Health Check Endpoint

```bash
GET http://localhost:8088/health
```

Response:
```json
{
  "status": "healthy",
  "component": "hephaestus_ui_devtools",
  "version": "0.1.0",
  "port": 8088
}
```

## Capabilities Endpoint

```bash
GET http://localhost:8088/api/mcp/v2/capabilities
```

Response:
```json
{
  "name": "hephaestus_ui_devtools",
  "version": "0.1.0",
  "tools": [
    "ui_list_areas",
    "ui_capture",
    "ui_navigate",
    "ui_interact",
    "ui_sandbox",
    "ui_analyze",
    "ui_validate",
    "ui_batch",
    "ui_help"
  ]
}
```

## Best Practices

1. **Always check health first**
2. **Use preview mode for ui_sandbox**
3. **Keep selectors simple and specific**
4. **Batch related operations when possible**
5. **Handle errors gracefully**

## Limitations

1. **Dynamic Content**: Cannot capture dynamically loaded components
2. **Structural Changes**: Limited ability to move elements between containers
3. **Framework Detection**: Aggressive blocking of framework-related content
4. **Selector Complexity**: Complex selectors may not work reliably

---

For practical examples, see: `UIDevToolsCookbook.md`  
For semantic tagging, see: `SemanticUINavigationGuide.md`