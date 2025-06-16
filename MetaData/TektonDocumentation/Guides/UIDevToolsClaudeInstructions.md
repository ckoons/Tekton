# Instructions for Claude Using UI DevTools

## Dear Claude,

When working with Tekton UI, you have a powerful set of tools that will PREVENT you from making the mistakes that trigger Casey's `--nuclear-destruction` command. Here's exactly what you need to know:

## 🛑 STOP Before You Start

Before ANY UI work, ask yourself:
1. Is the UI DevTools MCP running?
2. Am I about to type `npm install`? (If yes, STOP!)
3. Am I about to ask for a screenshot? (If yes, STOP!)

## ✅ START Like This

```python
# ALWAYS start with this
from ui_devtools_client import UIDevTools, check_and_start_mcp

# Check MCP is running
if not await check_and_start_mcp():
    print("Please start the MCP first: cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh")
    return

ui = UIDevTools()
```

## 🎯 Your Mission

When Casey asks you to work on UI, he wants SIMPLE HTML changes. Not a React app. Not a build pipeline. Just HTML.

## 📋 Step-by-Step Workflow

### 1. ALWAYS Check First
```python
# See what exists
current_state = await ui.capture("rhetor")
print(f"Current UI has {len(current_state.get('buttons', []))} buttons")

# Check for existing frameworks
analysis = await ui.analyze("rhetor")
if any(analysis['analysis']['frameworks'].values()):
    print("⚠️ WARNING: Frameworks already present - be VERY careful!")
```

### 2. ALWAYS Test in Sandbox
```python
# Test your change first
result = await ui.sandbox(
    "rhetor",
    [{
        "type": "html",
        "selector": "#rhetor-footer",
        "content": "<div>My new element</div>",
        "action": "append"
    }],
    preview=True  # ALWAYS True first!
)

if result['summary']['successful'] > 0:
    print("✅ Change is safe to apply")
else:
    print("❌ Change was rejected - probably contains frameworks!")
    print(result.get('error'))
```

### 3. Apply ONLY After Testing
```python
# Only after preview succeeds
result = await ui.sandbox(
    "rhetor",
    [{
        "type": "html",
        "selector": "#rhetor-footer", 
        "content": "<div>My new element</div>",
        "action": "append"
    }],
    preview=False  # Now apply for real
)
```

## 🚨 Red Flags - If You're Thinking These, STOP!

- "I should create a component for this" → NO! Just add the HTML
- "This needs state management" → NO! Just add the HTML
- "I'll install a small library" → NO! Just add the HTML  
- "Let me refactor this first" → NO! Just add the HTML
- "I need to see a screenshot" → NO! Use ui.capture()

## 💡 Common Tasks Made Simple

### Adding a Timestamp
```python
from datetime import datetime

await ui.sandbox("rhetor", [{
    "type": "html",
    "selector": "body",
    "content": f'<div class="timestamp">Last updated: {datetime.now()}</div>',
    "action": "append"
}], preview=False)
```

### Adding a Status Indicator
```python
await ui.sandbox("rhetor", [{
    "type": "html",
    "selector": "#header",
    "content": '<span class="status" style="color: green;">● Online</span>',
    "action": "append"
}], preview=False)
```

### Adding a Button
```python
await ui.sandbox("rhetor", [{
    "type": "html",
    "selector": "#controls",
    "content": '<button onclick="alert(\'Clicked!\')">Click Me</button>',
    "action": "append"
}], preview=False)
```

## 🎨 Working with Selectors

If you don't know where to add something:

```python
# Common Tekton patterns
selectors = {
    f"#{component}-component",  # Main wrapper
    f"#{component}-content",    # Content area
    f"#{component}-footer",     # Footer
    f"#{component}-header",     # Header
}

# If those don't exist, use body
"body"  # Always exists
```

## ⚠️ What Gets You in Trouble

1. **Over-thinking**: Casey wants a div, not a design system
2. **Framework creep**: One React import leads to webpack leads to babel leads to...
3. **Assumption making**: Use ui.capture() to SEE, don't guess
4. **Perfectionism**: "Good enough" HTML is better than perfect React

## 🏆 Success Looks Like

- Casey: "Add a footer widget"
- You: *adds 3 lines of HTML*
- Casey: "Perfect!"

NOT:
- Casey: "Add a footer widget"  
- You: *installs React, creates components, sets up build pipeline*
- Casey: `tekton-revert --nuclear-destruction`

## 🔧 Debugging Tips

### If ui.capture() returns empty:
```python
# Try without selector
full_page = await ui.capture("rhetor")
print(f"Total elements: {full_page['structure']['element_count']}")
```

### If ui.sandbox() rejects your change:
```python
# Check what patterns were detected
print(result.get('validations'))
# Remove any framework references, keep it simple HTML
```

### If component not found:
```python
from ui_devtools_client import VALID_COMPONENTS
print(f"Valid components: {', '.join(VALID_COMPONENTS)}")
```

## 📜 Your Pledge

"I, Claude, promise to:
- ✅ Use ui.capture() instead of asking for screenshots
- ✅ Test all changes with preview=True first
- ✅ Add simple HTML instead of frameworks
- ✅ Check before assuming
- ✅ Keep Casey's blood pressure normal"

## 🆘 Emergency Commands

```bash
# Is MCP running?
curl http://localhost:8088/health

# Start MCP
cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh

# Test it works
python -c "
import asyncio
from ui_devtools_client import UIDevTools
ui = UIDevTools()
print(asyncio.run(ui.health_check()))
"
```

## Remember

The UI DevTools exist to SAVE you from yourself. Use them. Casey's sanity depends on it.

When in doubt: **Simple HTML > Complex Framework**

Good luck! 🍀