# Hephaestus Training System - Example Conversations

## Example 1: New Claude Learning UI DevTools

**Claude**: How do I add a timestamp to the Rhetor component?

**Hephaestus AI**: Great question! Let me guide you through adding a timestamp to the Rhetor area in Hephaestus UI.

First, understand that Rhetor is not a separate component - it's an area within the main Hephaestus UI at port 8080.

Here's the simple way to add a timestamp:

```python
from ui_devtools_client import UIDevTools
ui = UIDevTools()

# First, see what's in the Rhetor area
result = await ui.capture("rhetor", "#rhetor-footer")

# Add a timestamp (preview first!)
await ui.sandbox("rhetor", [{
    "type": "html",
    "selector": "#rhetor-footer",  
    "content": f"<div class='timestamp'>Last updated: {datetime.now():%Y-%m-%d %H:%M}</div>",
    "action": "append"
}], preview=True)

# If it looks good, apply it
await ui.sandbox("rhetor", [...], preview=False)
```

⚠️ Important: Do NOT install moment.js or any date library. Python's datetime is all you need!

---

## Example 2: Error Diagnosis

**Claude**: I'm getting "Invalid component 'rhetor-ui'" error. The UI is at port 8003, right?

**Hephaestus AI**: I see the confusion! Let me clarify the architecture:

❌ **What you're thinking**: Each component has its own UI at different ports
✅ **Reality**: ALL UI is in Hephaestus at port 8080

The error happens because:
1. There's no component called 'rhetor-ui' - it's just 'rhetor'
2. Rhetor's API is at port 8003, but its UI is part of Hephaestus at port 8080

Here's the correct approach:

```python
# See all valid area names
areas = await ui.list_areas()
print(areas)  # Shows: rhetor, hermes, navigation, content, etc.

# Capture the Rhetor area within Hephaestus UI
result = await ui.capture("rhetor")  # Correct!
# NOT: await ui.capture("rhetor-ui")  # Wrong!
```

Remember: Use `ui_list_areas()` whenever you're unsure about area names!

---

## Example 3: Framework Prevention

**Claude**: The UI looks outdated. Should I modernize it with React?

**Hephaestus AI**: 🚨 STOP! Let me save you from Casey's wrath! 

Hephaestus UI is intentionally simple and framework-free. Here's why:
- **Performance**: No framework overhead
- **Maintainability**: Anyone can understand HTML/CSS
- **Reliability**: Fewer dependencies = fewer problems
- **Casey's Sanity**: He's 70 and prefers simplicity!

Instead of React, here's how to modernize UI elegantly:

```python
# Add modern styling with pure CSS
await ui.sandbox("rhetor", [{
    "type": "css",
    "content": """
    .rhetor-content {
        backdrop-filter: blur(10px);
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .rhetor-content:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 48px rgba(0,0,0,0.15);
    }
    """
}], preview=True)
```

See? Modern, beautiful, and no npm install! 🎉

---

## Example 4: Task Guidance

**Claude**: I need to add a status indicator that shows when Rhetor is processing.

**Hephaestus AI**: Perfect! I'll guide you through adding a processing indicator to the Rhetor area.

Let's build this step-by-step:

1. **Find where to put it**:
```python
# Check the Rhetor header area
capture = await ui.capture("rhetor", "#rhetor-header")
```

2. **Create the indicator** (simple HTML/CSS):
```python
indicator_html = """
<div id="rhetor-status" class="status-indicator">
    <span class="status-dot"></span>
    <span class="status-text">Ready</span>
</div>
"""

indicator_css = """
.status-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 12px;
    background: rgba(255,255,255,0.1);
    border-radius: 16px;
}
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #4CAF50;
}
.status-dot.processing {
    background: #FFA726;
    animation: pulse 1s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
"""
```

3. **Test it**:
```python
await ui.sandbox("rhetor", [
    {"type": "html", "selector": "#rhetor-header", "content": indicator_html, "action": "append"},
    {"type": "css", "content": indicator_css}
], preview=True)
```

4. **Make it interactive** (if needed):
```python
# Simple JS to toggle states - no frameworks!
toggle_js = """
function setRhetorStatus(processing) {
    const dot = document.querySelector('#rhetor-status .status-dot');
    const text = document.querySelector('#rhetor-status .status-text');
    if (processing) {
        dot.classList.add('processing');
        text.textContent = 'Processing...';
    } else {
        dot.classList.remove('processing');
        text.textContent = 'Ready';
    }
}
"""
```

See how we built a modern, animated status indicator with just 20 lines of simple code? No React needed!

---

## Example 5: Architecture Understanding

**Claude**: I'm confused about the UI architecture. Where exactly is the Rhetor UI?

**Hephaestus AI**: Let me draw you a mental map of the Hephaestus UI architecture:

```
🖥️ Port 8080 - Hephaestus UI (The only UI!)
│
├── 📍 Navigation Area (#left-nav)
│   ├── Component Links
│   └── System Status
│
├── 📍 Content Area (#center-content)
│   ├── 🤖 Rhetor Area (#rhetor-component)
│   ├── 📨 Hermes Area (#hermes-component)
│   ├── 🧠 Athena Area (#athena-component)
│   └── ... other component areas
│
└── 📍 Panel Area (#right-panel)
    └── Component-specific panels
```

**Key Points**:
1. **One UI to Rule Them All**: Everything is at http://localhost:8080
2. **Areas, Not Apps**: Rhetor, Hermes, etc. are areas within Hephaestus
3. **Dynamic Content**: Areas load based on navigation/state
4. **Shared Layout**: All components share the same nav/panel structure

**Component Ports are for APIs, not UIs**:
- Port 8003 (Rhetor) = API endpoints
- Port 8001 (Hermes) = Messaging API
- Port 8080 (Hephaestus) = ALL the UI

When you want to modify Rhetor's UI:
```python
# ✅ Correct: Target the Rhetor area in Hephaestus
await ui.capture("rhetor")  # Looks in Hephaestus UI for Rhetor area

# ❌ Wrong: Trying to connect to Rhetor's API port
# There's no UI at http://localhost:8003!
```

Think of it like a house:
- Hephaestus is the house (port 8080)
- Rhetor, Hermes, etc. are rooms in the house
- You don't go to different addresses to visit different rooms!

---

## Example 6: Best Practices

**Claude**: What are the best practices for modifying Tekton UIs?

**Hephaestus AI**: Excellent question! Here are the golden rules for UI modifications in Tekton:

### 🌟 The Casey-Approved Way™

1. **Start Simple, Stay Simple**
   ```python
   # ✅ Good: Clear, maintainable
   "<div class='alert'>Important message</div>"
   
   # ❌ Bad: Overengineered
   "import Alert from '@mui/material/Alert'..."
   ```

2. **Test Before You Touch**
   ```python
   # Always preview=True first!
   result = await ui.sandbox("area", changes, preview=True)
   # Check the result
   if result['summary']['successful'] > 0:
       # Only then apply
       await ui.sandbox("area", changes, preview=False)
   ```

3. **Use Existing Styles**
   ```python
   # First, see what classes exist
   capture = await ui.capture("rhetor")
   # Then reuse them!
   "<div class='rhetor-message'>...</div>"  # Matches existing style
   ```

4. **Selector Hierarchy**
   ```python
   # Preferred selectors (in order):
   1. "#specific-id"           # Most reliable
   2. ".component-class"       # Good for styling
   3. "[data-component='x']"   # Semantic
   4. "tag"                    # Last resort
   ```

5. **Error Recovery**
   ```python
   try:
       result = await ui.interact("rhetor", "click", "#submit")
   except Exception as e:
       # Ask for help!
       help_response = await ui.help(f"interaction failed: {e}")
       print(help_response)
   ```

### 🚫 What to Avoid

1. **No Framework Installations**
   - No `npm install` anything
   - No `<script src="react...">`
   - No webpack, babel, or build tools

2. **No Complex State Management**
   - Use data attributes for simple state
   - Let the backend handle complex state

3. **No Global Modifications**
   - Target specific areas
   - Avoid modifying body or html tags directly

### 📊 Decision Matrix

| Task | Simple Way | Complex Way | Choose |
|------|------------|-------------|---------|
| Add button | `<button>Click</button>` | React component | Simple! |
| Show/hide | `style="display:none"` | State management | Simple! |
| Animation | CSS transitions | Animation library | Simple! |
| Form | HTML form + fetch | Form library | Simple! |

Remember: Every line of code should make Casey smile, not sigh! 😊