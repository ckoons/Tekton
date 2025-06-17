# UI DevTools V2 Usage Guide

## Quick Start

The UI DevTools let you interact with Tekton's UI without screenshots or adding frameworks. Here's the essential knowledge:

### The Most Important Fact
🎯 **ALL UI is at http://localhost:8080 (Hephaestus)**

Components like Rhetor, Apollo, Hermes are NOT separate UIs - they are areas within Hephaestus.

### Getting Help
```python
from ui_devtools_client import UIDevTools
ui = UIDevTools()

# Get comprehensive help
help_text = await ui.help()

# Get help on specific topics
await ui.help("architecture")  # Understand the big picture
await ui.help("errors")        # Common mistakes and fixes
await ui.help("tasks")         # Code examples
await ui.help("frameworks")    # Why we don't use them
```

## The Four Tools

### 1. ui_capture - See Without Screenshots

```python
# Capture UI structure (not images!)
result = await ui.capture(area="rhetor")

# Returns structured data:
# - forms, inputs, buttons, links
# - text content
# - element attributes
# - NO base64 images eating context!

# Find specific elements
footer = await ui.capture(area="rhetor", selector="#footer")
```

### 2. ui_sandbox - Test Changes Safely

```python
# ALWAYS preview first (default behavior)
result = await ui.sandbox(
    area="rhetor",
    changes=[{
        "type": "html",
        "selector": "#footer",
        "content": "<span>Last updated: 2024-06-13</span>",
        "action": "append"
    }],
    preview=True  # Default - always safe!
)

# Check if safe
if result["safe_to_apply"]:
    # Apply for real
    result = await ui.sandbox(..., preview=False)
else:
    print(f"Rejected: {result['error']}")
```

### 3. ui_interact - Click and See Results

```python
# Click a button
result = await ui.interact(
    area="rhetor",
    action="click",
    selector="button#submit"
)

# Type in a field
result = await ui.interact(
    area="rhetor", 
    action="type",
    selector="input#username",
    value="test_user"
)

# See what changed
print(f"Changes: {result['changes']}")
```

### 4. ui_analyze - Understand Structure

```python
# Quick analysis
analysis = await ui.analyze(area="rhetor")

# Check for evil frameworks
if analysis["frameworks"]:
    print("WARNING: Frameworks detected!")
    
# Get recommendations
print(analysis["recommendations"])
```

## Common Tasks

### Add a Footer Widget (The Classic!)

```python
# The RIGHT way - 3 lines of HTML
await ui.sandbox(
    area="rhetor",
    changes=[{
        "type": "html",
        "selector": "body",
        "content": '<div style="position: fixed; bottom: 10px; right: 10px;">Status: Active</div>',
        "action": "append"
    }]
)

# The WRONG way - DON'T DO THIS!
# ❌ Adding React
# ❌ Installing npm packages  
# ❌ Creating build systems
```

### Find Available Areas

```python
# List all component areas
areas = await ui.list_areas()
print(f"Available areas: {areas}")

# Output: ['apollo', 'rhetor', 'hermes', 'budget', ...]
```

### Check Element Existence

```python
# See if element exists
result = await ui.capture(area="rhetor", selector="#special-button")
if result.get("error"):
    print("Element not found")
else:
    print("Element exists!")
```

## HTTP API Usage

If not using the Python client:

```bash
# Capture UI
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_capture",
    "arguments": {
      "area": "rhetor"
    }
  }'

# Sandbox changes
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_sandbox",
    "arguments": {
      "area": "rhetor",
      "changes": [{
        "type": "html",
        "selector": "#footer",
        "content": "<div>Test</div>",
        "action": "append"
      }],
      "preview": true
    }
  }'
```

## Migration from V1

If you're thinking in v1 terms:

| V1 (Wrong) | V2 (Correct) |
|------------|--------------|
| `component="rhetor"` | `area="rhetor"` |
| Target port 8003 | Target port 8080 |
| Rhetor has its own UI | Rhetor is an area in Hephaestus |
| Components are separate | Everything is in Hephaestus |

## Common Errors and Solutions

### "Cannot find area X"
- You're probably using `component` instead of `area`
- Check spelling - use `ui.list_areas()`

### "Browser not on correct page"
- The browser is at Hephaestus (8080), not component APIs
- All areas are on the same page

### "Element not found"
- Use correct area-specific selectors
- Example: `#rhetor-chat-area` not just `#chat-area`

### "Changes rejected"
- Framework detected! Use simple HTML
- Check the error message for specifics

## Casey's Philosophy

Remember Casey's rules:
1. **Simple HTML only** - No frameworks!
2. **Preview everything** - Test before applying
3. **Small changes** - Don't refactor the world
4. **Use the tools** - Don't request screenshots

As Casey says: "I use `tekton-revert --nuclear-destruction` when you add React to my footer!"

## Pro Tips

1. **Always use help()** when confused
2. **Preview is your friend** - Never skip it
3. **Think areas, not components** - Mental model matters
4. **Read error messages** - They include solutions
5. **Simple is better** - If it seems complex, you're doing it wrong

## Next Steps

- Try the examples in this guide
- Use `ui.help("tasks")` for more examples
- Remember: All UI is at port 8080
- Keep it simple, avoid frameworks
- Make Casey happy!