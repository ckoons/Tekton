# Hephaestus UI Architecture Guide

## Overview

The Hephaestus UI implements a CSS-first architecture with minimal JavaScript, focusing on reliability and simplicity. This guide documents how the UI system works, including component loading, CSS architecture, and implementation patterns.

## Core Architecture Principles

### CSS-First Philosophy
- **HTML injection** - Components are loaded as HTML fragments
- **CSS-driven navigation** - Originally attempted pure CSS `:target` selectors
- **Minimal JavaScript** - Only ~300 lines for WebSocket, chat, and health checks
- **Pre-loaded styles** - All CSS must be linked in index.html

### Current Implementation Status (January 2025)
The UI currently uses a hybrid approach:
- **minimal-loader.js** handles dynamic component loading
- CSS provides all styling and layout
- JavaScript is minimal but still required for reliable navigation

## How Components Work

### Component Structure
Each component follows a standard structure:

```html
<div id="componentName" class="component">
  <div class="componentName" data-tekton-component="componentName">
    <div class="componentName__header">...</div>
    <div class="componentName__menu-bar">...</div>
    <div class="componentName__content">...</div>
    <div class="componentName__footer">...</div>
  </div>
</div>
```

### Component Loading Flow

1. User clicks navigation link
2. minimal-loader.js fetches component HTML
3. HTML is injected into #html-panel
4. Component scripts execute
5. CSS (already loaded from index.html) styles the component

### File Organization

```
Hephaestus/ui/
├── index.html                    # Main container, loads all CSS
├── components/                   # Component HTML files
│   └── [name]/[name]-component.html
├── styles/                       # Component CSS (BEM notation)
│   └── [name]/[name]-component.css
├── scripts/                      # Component JavaScript
│   └── [name]/[name]-component.js
└── server/
    └── component_registry.json   # Component metadata
```

## Critical Implementation Details

### CSS Loading - The #1 Rule

**All CSS must be linked in index.html**. The component registry lists CSS files but does NOT load them.

```html
<!-- In /ui/index.html -->
<link rel="stylesheet" href="styles/rhetor/rhetor-component.css">
<link rel="stylesheet" href="styles/ergon/ergon-component.css">
<!-- ... all component CSS files ... -->
```

### Component Registry

Located at `/ui/server/component_registry.json`:
- Defines component metadata
- Lists scripts to load dynamically
- Controls Shadow DOM settings (usually false)
- Does NOT load CSS files

```json
{
  "id": "componentName",
  "name": "Component Display Name",
  "componentPath": "components/[name]/[name]-component.html",
  "scripts": ["scripts/[name]/[name]-component.js"],
  "styles": ["styles/[name]/[name]-component.css"],
  "usesShadowDom": false
}
```

### Semantic Tagging System

The UI uses `data-tekton-*` attributes for semantic meaning:

- `data-tekton-component` - Component identifier
- `data-tekton-area` - Major UI areas
- `data-tekton-zone` - Component zones (header, menu, content, footer)
- `data-tekton-nav-item` - Navigation items
- `data-tekton-state` - State indicators (active, inactive)

## CSS Architecture

### BEM Naming Convention

All CSS follows Block Element Modifier notation:

```css
/* Block */
.componentName { }

/* Element */
.componentName__header { }
.componentName__title { }

/* Modifier */
.componentName__btn--primary { }
.componentName__tab--active { }
```

### Theme System

CSS variables provide theming:

```css
.componentName {
  background-color: var(--bg-color-secondary, #1a1a1a);
  color: var(--text-primary, #e0e0e0);
}
```

Always include fallback values for CSS variables.

### Layout Patterns

Standard three-panel layout:
1. **Left Panel** - Navigation (persistent)
2. **Content Area** - Component display (dynamic)
3. **Component Structure** - Header, menu, content, footer

## JavaScript Patterns

### Minimal JavaScript Approach

JavaScript handles only:
- WebSocket connections
- Chat input handling
- Health status checks
- Tab switching within components

### Global Function Pattern

To avoid scope issues, use global functions for event handlers:

```javascript
// Global functions for onclick handlers
function componentName_switchTab(tabName) {
  // Implementation
}

function componentName_refresh() {
  // Implementation
}
```

### WebSocket Integration

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Route to appropriate handler
};
```

## Common Pitfalls and Solutions

### CSS Not Working
1. Check if CSS is linked in index.html
2. Verify file path is correct
3. Check browser console for 404 errors

### Content Not Showing
1. Check `usesShadowDom` setting (should be false)
2. Verify HTML structure matches CSS selectors
3. Ensure component is properly registered

### CSS Variables Undefined
1. Use fallback values
2. Check active theme in Settings
3. Verify variable names match theme definitions

## Adding New Components

### Quick Checklist

1. **Create component files**:
   - `/ui/components/[name]/[name]-component.html`
   - `/ui/styles/[name]/[name]-component.css`
   - `/ui/scripts/[name]/[name]-component.js`

2. **Link CSS in index.html** (CRITICAL!)

3. **Register in component_registry.json**

4. **Add to minimal-loader.js** component paths

## Evolution and Future Direction

### Attempted Pure CSS Navigation
The project attempted to use CSS `:target` selectors for navigation but encountered limitations:
- Components after the target in DOM order couldn't be properly hidden
- This led to the current hybrid approach with minimal-loader.js

### Current Best Practices
- Keep JavaScript minimal
- Let CSS handle all styling and layout
- Use semantic HTML and data attributes
- Follow established patterns from existing components

## Reference Components

Well-implemented components to study:
- **Ergon** - Standard component structure
- **Settings** - Theme system integration
- **Rhetor** - Complex multi-panel component

## Key Takeaways

1. **CSS must be in index.html** - This is non-negotiable
2. **Follow BEM strictly** - Prevents style conflicts
3. **Use semantic tags** - Helps with maintenance and debugging
4. **Keep it simple** - The UI is just a visibility layer
5. **Reference existing components** - Learn from what works

---

*This guide reflects the current state of Hephaestus UI implementation as of January 2025.*