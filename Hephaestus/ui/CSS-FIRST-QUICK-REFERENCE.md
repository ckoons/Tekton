# CSS-First Architecture Quick Reference

## 🚀 The Big Change (June 2025)

We eliminated ~90% of JavaScript complexity by using CSS for navigation!

## How It Works Now

### Navigation
```html
<!-- Click this -->
<a href="#rhetor">Rhetor</a>

<!-- Shows this component instantly via CSS -->
<div id="rhetor" class="component">...</div>
```

### The Magic CSS
```css
/* Hide all components */
.component { display: none; }

/* Show targeted component */
.component:target { display: block; }

/* Show Numa by default */
#numa { display: block; }
:target ~ #numa { display: none; }
```

## Key Files

1. **`app-minimal.js`** - ALL the JavaScript (~300 lines)
   - WebSocket connection
   - Chat input handling
   - Health check dots

2. **`build-simplified.py`** - Builds index.html
   ```bash
   python3 build-simplified.py
   ```

3. **`index.html`** - Has ALL components pre-loaded

## Adding/Changing Components

1. Edit: `components/[name]/[name]-component.html`
2. Run: `python3 build-simplified.py`
3. Test: Open browser, click nav links

## What's Gone (Deprecated)

- ❌ minimal-loader.js
- ❌ ui-manager-core.js
- ❌ component-loading-guard.js
- ❌ Dynamic loading
- ❌ Race conditions
- ❌ Loading delays

## Benefits

- ✅ Instant navigation
- ✅ No loading failures
- ✅ View source shows everything
- ✅ ~90% less JavaScript

## Full Documentation

📖 [CSS-First Architecture Documentation](/MetaData/TektonDocumentation/Architecture/CSSFirstArchitecture.md)