# UI DevTools Cheat Sheet for Claude

## 🚨 BEFORE YOU START
```python
from ui_devtools_client import UIDevTools, check_and_start_mcp
if not await check_and_start_mcp():
    # Ask user to run: cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh
    return
ui = UIDevTools()
```

## 🔧 THE ONLY 4 COMMANDS YOU NEED

### 1. SEE (Don't Screenshot)
```python
# See whole component
result = await ui.capture("rhetor")

# See specific element  
result = await ui.capture("rhetor", "#footer")
```

### 2. TEST (Before Breaking)
```python
# ALWAYS preview=True first!
result = await ui.sandbox("rhetor", [{
    "type": "html",
    "selector": "#footer",
    "content": "<div>Test</div>", 
    "action": "append"  # or replace, prepend, before, after
}], preview=True)

# If successful, then preview=False
```

### 3. INTERACT (Click/Type)
```python
# Click
await ui.interact("rhetor", "click", "button#submit")

# Type
await ui.interact("rhetor", "type", "input#name", "Hello")

# Select
await ui.interact("rhetor", "select", "select#options", "value1")
```

### 4. CHECK (For Dangers)
```python
analysis = await ui.analyze("rhetor")
if any(analysis['analysis']['frameworks'].values()):
    print("⚠️ DANGER: Frameworks detected!")
```

## 📍 COMMON SELECTORS
```python
# Tekton patterns
f"#{component}-component"  # Main
f"#{component}-content"    # Content
f"#{component}-footer"     # Footer
f"#{component}-header"     # Header
"body"                     # Fallback
```

## ✅ RIGHT vs ❌ WRONG

### Adding Timestamp
```python
# ✅ RIGHT (3 lines)
await ui.sandbox("rhetor", [{
    "type": "html", "selector": "body",
    "content": f"<div>Time: {datetime.now()}</div>",
    "action": "append"
}], preview=False)

# ❌ WRONG
# npm install moment react react-dom...
```

### Adding Status
```python
# ✅ RIGHT
"<span style='color:green'>● Online</span>"

# ❌ WRONG  
# import StatusComponent from './components/Status'
```

## 🚫 FORBIDDEN THOUGHTS
- "I need React for this" → NO
- "Let me install..." → NO
- "I'll refactor..." → NO
- "Screenshot please" → NO

## 🆘 ERRORS

**"component not found"**
```python
# Valid: apollo, athena, budget, engram, ergon, harmonia,
#        hephaestus, hermes, metis, prometheus, rhetor,
#        sophia, synthesis, tekton_core, telos, terma
```

**"change rejected"**
- You tried to add React/Vue/Angular
- Keep it simple HTML only

**"MCP not running"**
```bash
cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh
```

## 🎯 CASEY'S HAPPINESS FORMULA

Simple HTML = Happy Casey
React/npm = `--nuclear-destruction`

**Remember**: When Casey says "add a widget", he means:
```html
<div>Widget</div>
```

NOT a 500-line React component!