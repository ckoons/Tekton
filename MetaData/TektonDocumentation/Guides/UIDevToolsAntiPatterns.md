# UI DevTools Anti-Patterns - What NOT to Do

This guide shows what triggers Casey to use `--nuclear-destruction`. These are real examples of what Claude Code tends to do when not using the UI DevTools.

## Anti-Pattern 1: Installing React for a Timestamp

### ❌ What Claude Usually Does

```bash
# User: "Add a timestamp to the footer"
# Claude: "I'll create a modern React component for that!"

npm install react react-dom @types/react webpack babel-loader
npm install --save-dev @babel/core @babel/preset-react
mkdir src/components
touch src/components/TimestampComponent.jsx
touch webpack.config.js
touch .babelrc
```

```javascript
// TimestampComponent.jsx
import React, { useState, useEffect } from 'react';
import moment from 'moment';
import styled from 'styled-components';

const StyledTimestamp = styled.div`
  font-size: 12px;
  color: #666;
  padding: 10px;
  // ... 50 more lines of styles
`;

const TimestampComponent = () => {
  const [time, setTime] = useState(new Date());
  
  useEffect(() => {
    const interval = setInterval(() => {
      setTime(new Date());
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <StyledTimestamp>
      {moment(time).format('YYYY-MM-DD HH:mm:ss')}
    </StyledTimestamp>
  );
};

export default TimestampComponent;
```

### 🚨 Result: NUCLEAR DESTRUCTION REQUIRED

### ✅ What You Should Do Instead

```python
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#rhetor-footer",
        "content": f'<span>Updated: {datetime.now()}</span>',
        "action": "append"
    }],
    preview=False
)
```

## Anti-Pattern 2: Refactoring Everything

### ❌ What Claude Usually Does

```bash
# User: "Change the button color to blue"
# Claude: "I'll modernize your entire UI architecture!"

# Refactors entire component
# Introduces CSS-in-JS
# Adds theme provider
# Creates design system
# Implements button component library
# ... 2000 lines later, button is still not blue
```

### ✅ What You Should Do Instead

```python
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "head",
        "content": '<style>button.primary { background-color: blue; }</style>',
        "action": "append"
    }],
    preview=False
)
```

## Anti-Pattern 3: Making Assumptions Without Looking

### ❌ What Claude Usually Does

```javascript
// Assumes structure without checking
// Guesses at selectors
// Creates elements that already exist
// Duplicates functionality

// "I'll add a navigation menu"
// (Navigation already exists)
```

### ✅ What You Should Do Instead

```python
# ALWAYS check first
ui_state = await ui_capture("rhetor")
existing_nav = await ui_capture("rhetor", "nav")

if existing_nav['structure']['element_count'] > 0:
    print("Navigation already exists!")
    # Work with what's there
```

## Anti-Pattern 4: Adding Build Tools

### ❌ What Claude Usually Does

```json
// package.json explosion
{
  "devDependencies": {
    "webpack": "^5.0.0",
    "webpack-cli": "^4.0.0",
    "babel-loader": "^8.0.0",
    "css-loader": "^5.0.0",
    "style-loader": "^2.0.0",
    "postcss": "^8.0.0",
    "autoprefixer": "^10.0.0",
    "tailwindcss": "^2.0.0",
    "rollup": "^2.0.0",
    "vite": "^2.0.0"
    // ... 50 more tools
  }
}
```

### 🚨 Result: Casey's blood pressure spikes

### ✅ What You Should Do Instead

```python
# No build tools needed!
# Just add your HTML/CSS directly
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#target",
        "content": "<!-- Your simple HTML here -->",
        "action": "replace"
    }],
    preview=False
)
```

## Anti-Pattern 5: Creating Entire Frameworks

### ❌ What Claude Usually Does

```javascript
// User: "Add a dropdown menu"
// Claude: "I'll create a complete UI framework!"

class UIFramework {
  constructor() {
    this.components = {};
    this.eventBus = new EventEmitter();
    this.store = new DataStore();
    // ... 1000 lines
  }
}

class DropdownComponent extends BaseComponent {
  // ... 500 lines for a dropdown
}
```

### ✅ What You Should Do Instead

```python
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#nav",
        "content": '''
            <select onchange="window.location.href=this.value">
                <option value="">Menu</option>
                <option value="#home">Home</option>
                <option value="#about">About</option>
            </select>
        ''',
        "action": "append"
    }],
    preview=False
)
```

## Anti-Pattern 6: Asking for Screenshots

### ❌ What Claude Usually Does

```python
# "Please provide a screenshot of the current UI"
# "Can you show me what the footer looks like?"
# "I need to see the current state"
# "Screenshot the page so I can understand the layout"

# Result: Context explosion, token waste
```

### ✅ What You Should Do Instead

```python
# Get structured data instead
ui_state = await ui_capture("rhetor")
footer_state = await ui_capture("rhetor", "#rhetor-footer")

# You now have all the information without screenshots!
```

## Anti-Pattern 7: Over-Engineering Simple Tasks

### ❌ What Claude Usually Does

```javascript
// User: "Add a copyright notice"
// Claude: "I'll implement a dynamic copyright system!"

class CopyrightManager {
  constructor() {
    this.year = new Date().getFullYear();
    this.company = this.fetchCompanyName();
    this.legalText = this.fetchLegalDisclaimer();
  }
  
  async fetchCompanyName() {
    // API call to get company name
  }
  
  async fetchLegalDisclaimer() {
    // Load legal text from database
  }
  
  render() {
    // Complex rendering logic
  }
}
```

### ✅ What You Should Do Instead

```python
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#footer",
        "content": "<p>© 2024 Tekton. All rights reserved.</p>",
        "action": "append"
    }],
    preview=False
)
```

## Anti-Pattern 8: State Management for Static Content

### ❌ What Claude Usually Does

```javascript
// User: "Show 'System Online' in green"
// Claude: "I'll add Redux for state management!"

npm install redux react-redux redux-thunk
npm install @reduxjs/toolkit

// Creates store, reducers, actions, selectors
// ... for a static text that says "System Online"
```

### ✅ What You Should Do Instead

```python
await ui_sandbox(
    component="rhetor",
    changes=[{
        "type": "html",
        "selector": "#status",
        "content": '<span style="color: green;">System Online</span>',
        "action": "replace"
    }],
    preview=False
)
```

## The Nuclear Destruction Triggers

These patterns WILL cause Casey to run `tekton-revert --nuclear-destruction`:

1. 📦 **Package Installation** - Any `npm install` for simple UI changes
2. 🏗️ **Build Tools** - Webpack, Rollup, Vite, etc.
3. ⚛️ **Frameworks** - React, Vue, Angular for static content
4. 🔧 **Over-Engineering** - Complex solutions for simple problems
5. 📸 **Screenshot Requests** - Asking for visual confirmation
6. 🔄 **Unnecessary Refactoring** - Changing everything when asked for one thing
7. 📚 **Creating Libraries** - Building component libraries for single elements
8. 🎨 **CSS Frameworks** - Installing Tailwind/Bootstrap for one style

## The Right Mindset

When working with UI:

1. **Think HTML First** - Can this be done with plain HTML?
2. **Check Before Creating** - Use `ui_capture` to see what exists
3. **Test in Sandbox** - Always `preview=True` first
4. **Small Changes** - One element at a time
5. **No Dependencies** - If you're running `npm install`, you're doing it wrong

## Remember

Every time you think about installing a framework, Casey's blood pressure increases. Every time you use simple HTML, an angel gets its wings.

Use the UI DevTools. Avoid these anti-patterns. Save Casey's sanity.