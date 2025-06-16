# UI DevTools Common Patterns

This guide shows how to accomplish common UI tasks using the UI DevTools. Each pattern shows the RIGHT way (simple HTML) vs the WRONG way (frameworks/over-engineering).

## Pattern 1: Adding a Footer Widget

### ✅ The Right Way (3 lines)

```python
# Add a simple footer widget
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#rhetor-footer",
        "content": '<div class="footer-widget">API Status: Connected</div>',
        "action": "append"
    }],
    preview=False  # After testing with preview=True
)
```

### ❌ The Wrong Way (What Claude usually does)

```javascript
// DON'T DO THIS!
npm install react react-dom webpack babel-loader
// Create FooterWidget.jsx
// Set up build pipeline
// ... 500 lines later
```

## Pattern 2: Adding a Status Indicator

### ✅ The Right Way

```python
# 1. Check where to add it
ui_state = await ui_capture("rhetor", "#rhetor-header")

# 2. Add status indicator
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#rhetor-header",
        "content": '''
            <div class="status-indicator" style="float: right; padding: 5px;">
                <span class="status-dot" style="display: inline-block; width: 10px; height: 10px; 
                      background: #4CAF50; border-radius: 50%;"></span>
                <span class="status-text">Online</span>
            </div>
        ''',
        "action": "append"
    }],
    preview=False
)
```

### ❌ The Wrong Way

```javascript
// DON'T: Create a StatusIndicator component
// DON'T: Add state management
// DON'T: Install Redux for a green dot
```

## Pattern 3: Adding a Timestamp

### ✅ The Right Way

```python
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#rhetor-content",
        "content": f'<div class="last-updated">Last updated: {timestamp}</div>',
        "action": "prepend"
    }],
    preview=False
)
```

## Pattern 4: Updating Navigation

### ✅ The Right Way

```python
# Add a new nav item
await ui_sandbox(
    component="hephaestus",
    changes=[{
        "type": "html",
        "selector": "nav ul",
        "content": '<li><a href="#settings">Settings</a></li>',
        "action": "append"
    }],
    preview=False
)
```

## Pattern 5: Adding a Notification Banner

### ✅ The Right Way

```python
# Add a simple notification
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "body",
        "content": '''
            <div id="notification-banner" style="
                position: fixed; top: 0; left: 0; right: 0;
                background: #2196F3; color: white; padding: 10px;
                text-align: center; z-index: 1000;
            ">
                System maintenance scheduled for midnight
                <button onclick="this.parentElement.remove()" 
                        style="float: right; background: none; border: none; 
                               color: white; cursor: pointer;">✕</button>
            </div>
        ''',
        "action": "prepend"
    }],
    preview=False
)
```

## Pattern 6: Modifying Forms

### ✅ The Right Way

```python
# First, see what's in the form
form_state = await ui_capture("rhetor", "form#settings-form")

# Add a new field
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "form#settings-form",
        "content": '''
            <div class="form-group">
                <label for="theme">Theme:</label>
                <select id="theme" name="theme">
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                </select>
            </div>
        ''',
        "action": "append"
    }],
    preview=False
)
```

## Pattern 7: Adding Loading Indicator

### ✅ The Right Way

```python
# Simple CSS spinner
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#rhetor-content",
        "content": '''
            <div id="loading" style="text-align: center; padding: 20px;">
                <div class="spinner" style="
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #3498db;
                    border-radius: 50%;
                    width: 40px; height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto;
                "></div>
                <style>
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            </div>
        ''',
        "action": "prepend"
    }],
    preview=False
)
```

## Pattern 8: Adding Interactive Elements

### ✅ The Right Way (Vanilla JS)

```python
# Add a collapsible section
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#rhetor-content",
        "content": '''
            <div class="collapsible-section">
                <button onclick="
                    var content = this.nextElementSibling;
                    content.style.display = content.style.display === 'none' ? 'block' : 'none';
                " style="width: 100%; text-align: left; padding: 10px; 
                         background: #f1f1f1; border: none; cursor: pointer;">
                    Advanced Options ▼
                </button>
                <div style="display: none; padding: 10px; border: 1px solid #ddd;">
                    <p>Advanced settings go here...</p>
                </div>
            </div>
        ''',
        "action": "append"
    }],
    preview=False
)
```

## Pattern 9: Status Table

### ✅ The Right Way

```python
# Add a simple status table
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#rhetor-content",
        "content": '''
            <table class="status-table" style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f5f5f5;">
                        <th style="padding: 10px; text-align: left;">Component</th>
                        <th style="padding: 10px; text-align: left;">Status</th>
                        <th style="padding: 10px; text-align: left;">Last Check</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">API</td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; color: #4CAF50;">✓ Active</td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">Just now</td>
                    </tr>
                </tbody>
            </table>
        ''',
        "action": "append"
    }],
    preview=False
)
```

## Pattern 10: Quick Actions Bar

### ✅ The Right Way

```python
# Add action buttons
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#rhetor-header",
        "content": '''
            <div class="quick-actions" style="margin: 10px 0;">
                <button onclick="alert('Refreshing...')" 
                        style="margin-right: 5px; padding: 5px 15px;">
                    Refresh
                </button>
                <button onclick="console.log('Settings clicked')" 
                        style="margin-right: 5px; padding: 5px 15px;">
                    Settings
                </button>
                <button onclick="if(confirm('Clear cache?')) console.log('Clearing...')" 
                        style="padding: 5px 15px;">
                    Clear Cache
                </button>
            </div>
        ''',
        "action": "append"
    }],
    preview=False
)
```

## General Patterns

### Finding the Right Selector

```python
# 1. Use common Tekton patterns
component = "rhetor"
selectors = {
    "main": f"#{component}-component",
    "content": f"#{component}-content",
    "footer": f"#{component}-footer",
    "header": f"#{component}-header"
}

# 2. Explore what's available
ui_state = await ui_capture(component)
print(f"Buttons: {[b['id'] for b in ui_state.get('buttons', []) if b.get('id')]}")
print(f"Forms: {[f['id'] for f in ui_state.get('forms', []) if f.get('id')]}")
```

### Safe Element Removal

```python
# Remove an element safely
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#old-notification",
        "content": "",  # Empty content
        "action": "replace"
    }],
    preview=True  # Test first!
)
```

### Adding CSS Without Frameworks

```python
# Add styles
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "head",
        "content": '''
            <style>
                .custom-widget { 
                    background: #f0f0f0; 
                    padding: 10px; 
                    border-radius: 5px; 
                }
                .status-active { color: #4CAF50; }
                .status-inactive { color: #f44336; }
            </style>
        ''',
        "action": "append"
    }],
    preview=False
)
```

## Remember

For EVERY pattern:
1. **Check First**: Use `ui_capture` to see current state
2. **Test First**: Use `preview=True` before applying
3. **Simple HTML**: No frameworks, no build tools
4. **Small Changes**: One element at a time

These patterns show that you can accomplish ANY UI task with simple HTML/CSS. No React needed!