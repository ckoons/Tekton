# How Tekton UI Works

*Living Document - Last Updated: 2025-06-23*

This document captures the hard-won lessons about how Tekton's UI system actually works, based on real implementation experience. It will evolve as Tekton evolves.

## Overview

Tekton UI follows a component-based architecture where each AI component (Rhetor, Ergon, Athena, etc.) has its own isolated UI. The system loads one component at a time into the right panel, with all styling and behavior pre-loaded for performance.

### Core Philosophy
- **Static HTML over dynamic DOM manipulation**
- **One component displayed at a time**
- **CSS pre-loaded, not dynamically injected**
- **Minimal complexity, maximum reliability**

## Critical Implementation Details

### 1. CSS Loading (The #1 Gotcha)

**THE RULE**: All CSS must be linked in `index.html`. Period.

```html
<!-- In /ui/index.html -->
<link rel="stylesheet" href="styles/rhetor/rhetor-component.css">
<link rel="stylesheet" href="styles/rhetor/rhetor-dashboard.css">
```

**Why this matters**: 
- The component registry (`component_registry.json`) lists CSS files but does NOT load them
- `minimal-loader.js` loads HTML and JavaScript, but NOT CSS
- If your styles aren't working, check `index.html` first!

### 2. Component Registry

Located at `/ui/server/component_registry.json`, this file:
- ✅ Defines component metadata
- ✅ Lists scripts to load dynamically
- ✅ Controls Shadow DOM settings
- ❌ Does NOT load CSS (despite listing CSS files)

Important settings:
```json
{
  "usesShadowDom": false  // Set to false if content isn't showing
}
```

### 3. Theme System & CSS Variables

CSS variables are defined by the theme system in Settings:
- Variables like `--bg-color-secondary` come from theme files
- Always use fallback values: `var(--bg-color-card, #defaultcolor)`
- Theme files are in `/ui/styles/themes/`

## Component Loading Flow

```
User clicks navigation
    ↓
minimal-loader.js
    ↓
Loads component HTML → Injects into #html-panel
    ↓
Executes component scripts
    ↓
Component renders (CSS already loaded from index.html)
```

## Adding a New Component - Quick Checklist

1. **Create component files**:
   ```
   /ui/components/[name]/[name]-component.html
   /ui/styles/[name]/[name]-component.css
   /ui/scripts/[name]/[name]-component.js
   ```

2. **Link CSS in index.html** ⚠️ CRITICAL!
   ```html
   <link rel="stylesheet" href="styles/[name]/[name]-component.css">
   ```

3. **Register in component_registry.json**:
   ```json
   {
     "id": "yourcomponent",
     "name": "YourComponent",
     "componentPath": "components/[name]/[name]-component.html",
     "scripts": ["scripts/[name]/[name]-component.js"],
     "styles": ["styles/[name]/[name]-component.css"],
     "usesShadowDom": false
   }
   ```

4. **Add to minimal-loader.js**:
   ```javascript
   this.componentPaths = {
     'yourcomponent': '/components/[name]/[name]-component.html'
   };
   ```

## Common Pitfalls & Solutions

### "My CSS isn't working!"
1. Check if CSS is linked in `index.html`
2. Check browser console for 404 errors
3. Verify CSS file path is correct

### "Content not showing in component"
1. Check `usesShadowDom` setting in component_registry.json
2. Set to `false` if content is being blocked
3. Verify HTML structure matches CSS selectors

### "CSS variables undefined"
1. Use fallback values: `var(--variable-name, fallback-value)`
2. Check which theme is active in Settings
3. Verify variable names match theme definitions

### "Grid layout showing as single column"
1. Ensure CSS is loaded (see #1 above)
2. Check if parent container has proper width
3. Verify grid CSS properties are applied

## Component Reference Examples

**Well-implemented components to reference:**
- **Ergon** - Good example of standard component structure
- **Settings** - Shows theme system integration
- **Rhetor** - Complex component with multiple panels

## Debugging Tools

1. **Browser DevTools**:
   - Check Network tab for CSS loading
   - Inspect computed styles
   - Look for console errors

2. **UI DevTools** (when working):
   - Use MCP tools for component inspection
   - Screenshot tool for visual debugging

## Version History

- **2025-06-23**: Initial documentation created
  - Documented CSS loading discovery
  - Added Shadow DOM findings
  - Created component checklist

## Future Sections

- Component Communication Patterns
- Hermes Message Integration
- Advanced Debugging Techniques

---

*Remember: When in doubt, check how Ergon does it - it's our reference implementation.*