# Hephaestus UI DevTools Usage Guide

## Overview

The UI DevTools MCP provides Claude with tools to work with UI without destroying everything. No more framework additions, no more webpack configs, just simple HTML manipulation.

## Starting the MCP Server

1. Start Hephaestus UI first:
   ```bash
   ./run_hephaestus.sh
   ```

2. Start the UI DevTools MCP:
   ```bash
   ./run_mcp.sh
   ```

The MCP server runs on port 8088 and registers with Hermes automatically.

## Available Tools

### 1. ui_capture

Get UI state without screenshots eating up context.

```python
result = await ui_capture(
    component="rhetor",
    selector="#rhetor-footer",  # Optional
    include_screenshot=False    # Only if really needed
)
```

Returns structured data about:
- HTML structure
- Forms and inputs
- Buttons and links
- Interactive elements

### 2. ui_interact

Click, type, and interact with UI elements.

```python
result = await ui_interact(
    component="rhetor",
    action="click",  # or "type", "select", "hover"
    selector="#submit-button",
    value="Hello",  # For type/select actions
    capture_changes=True
)
```

Captures:
- Before/after state
- Console messages
- Network requests
- DOM changes

### 3. ui_sandbox

Test changes safely before applying them.

```python
result = await ui_sandbox(
    component="rhetor",
    changes=[
        {
            "type": "html",
            "selector": "#footer",
            "content": '<span>Timestamp: 2024-06-12</span>',
            "action": "append"  # or "replace", "prepend", "before", "after"
        }
    ],
    preview=True  # Set to False to actually apply
)
```

Features:
- Detects and rejects frameworks
- Validates changes before applying
- Provides rollback capability
- Shows what will change

### 4. ui_analyze

Understand UI structure and complexity.

```python
result = await ui_analyze(
    component="rhetor",
    deep_scan=True
)
```

Analyzes:
- DOM structure
- Framework detection
- Complexity assessment
- API calls and forms
- Provides recommendations

## The Acid Test

Task: Add a timestamp to Rhetor's footer

**Good (What these tools enable):**
```html
<span id="timestamp">2024-06-12 17:45:00</span>
```

**Bad (What these tools prevent):**
```javascript
import React from 'react';
import { useState, useEffect } from 'react';

const TimestampComponent = () => {
  const [time, setTime] = useState(new Date());
  // ... 100 more lines of React
```

## Safety Features

1. **Framework Detection**: Automatically detects and rejects React, Vue, Angular, webpack, etc.
2. **Sandbox Mode**: Test all changes before applying
3. **Pattern Validation**: Checks for dangerous patterns
4. **Structured Data**: Returns data, not screenshots

## Testing

Run the test suite:
```bash
python test_ui_devtools.py
```

This tests:
- Tool functionality
- Framework rejection
- Safe HTML injection
- Pattern detection

## Common Patterns

### Adding a Footer Widget
```python
# 1. Capture current state
current = await ui_capture("rhetor", "#rhetor-footer")

# 2. Test the change
result = await ui_sandbox(
    "rhetor",
    [{
        "type": "html",
        "selector": "#rhetor-footer",
        "content": '<div class="widget">My Widget</div>',
        "action": "append"
    }],
    preview=True
)

# 3. Apply if safe
if result["summary"]["successful"] > 0:
    await ui_sandbox(..., preview=False)
```

### Analyzing Before Modifying
```python
# Always analyze first
analysis = await ui_analyze("rhetor", deep_scan=True)

if analysis["analysis"]["frameworks"]["react"]:
    print("Warning: React detected. Proceed with caution.")

if analysis["analysis"]["complexity"]["score"] > 10:
    print("High complexity. Use simple HTML only.")
```

## Remember

- These tools PREVENT the very behavior Claude usually exhibits
- Always use structured data over screenshots
- Test in sandbox before applying
- Keep it simple - HTML, not frameworks
- Save Casey's sanity