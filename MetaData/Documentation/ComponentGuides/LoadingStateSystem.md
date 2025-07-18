# Loading State System Guide

> ⚠️ **DEPRECATED as of June 2025**
> 
> The Loading State System is no longer used in Hephaestus UI. The new CSS-first architecture pre-loads all components, eliminating the need for loading states.
> 
> **See: [CSS-First Architecture Documentation](/MetaData/TektonDocumentation/Architecture/CSSFirstArchitecture.md)**
> 
> This documentation is preserved for historical reference only.

---

## Overview

The Loading State System provides reliable detection of when UI components are fully loaded and ready for interaction. This system uses semantic HTML attributes to track component loading lifecycle, solving the DynamicContentView problem where DevTools couldn't reliably detect dynamically loaded content.

## How It Works

### Loading State Lifecycle

Components progress through these states:

1. **`pending`** - Component loading has been initiated
2. **`loading`** - Component is actively being fetched and rendered
3. **`loaded`** - Component is fully loaded and ready
4. **`error`** - Component failed to load

### Semantic Attributes

The system uses these `data-tekton-*` attributes on the component container:

```html
<!-- During loading -->
<div id="html-panel" 
     data-tekton-loading-state="loading"
     data-tekton-loading-component="rhetor"
     data-tekton-loading-started="1750456131623">
  Loading rhetor...
</div>

<!-- After successful load -->
<div id="html-panel" 
     data-tekton-loading-state="loaded"
     data-tekton-loading-component="rhetor"
     data-tekton-loading-started="1750456131623">
  <!-- Component content -->
</div>

<!-- On error -->
<div id="html-panel" 
     data-tekton-loading-state="error"
     data-tekton-loading-component="rhetor"
     data-tekton-loading-started="1750456131623"
     data-tekton-loading-error="Failed to load component: 404">
  <!-- Error display -->
</div>
```

## Implementation Details

### MinimalLoader Changes

The MinimalLoader tracks loading states throughout the component lifecycle:

```javascript
// When starting to load a component
container.setAttribute('data-tekton-loading-state', 'pending');
container.setAttribute('data-tekton-loading-component', componentId);
container.setAttribute('data-tekton-loading-started', Date.now());
container.removeAttribute('data-tekton-loading-error');

// When actively loading
container.setAttribute('data-tekton-loading-state', 'loading');

// On successful load
container.setAttribute('data-tekton-loading-state', 'loaded');
container.removeAttribute('data-tekton-loading-error');

// On error
container.setAttribute('data-tekton-loading-state', 'error');
container.setAttribute('data-tekton-loading-error', error.message);
```

### DevTools Navigation

The navigation tools use a two-step process to reliably detect loading:

1. **Wait for loading to start** - Ensures MinimalLoader has begun
2. **Wait for completion** - Waits for either `loaded` or `error` state

```python
# Step 1: Wait for component loading to start
await page.wait_for_selector(
    f'[data-tekton-loading-component="{component}"]',
    timeout=2000
)

# Step 2: Wait for loading to complete
await page.wait_for_selector(
    f'[data-tekton-loading-component="{component}"][data-tekton-loading-state="loaded"]',
    timeout=10000
)
```

### Load Time Tracking

The system automatically calculates and reports load times:

```python
start_time = await container.get_attribute('data-tekton-loading-started')
current_time = await page.evaluate("Date.now()")
load_time = int(current_time) - int(start_time)
```

## Usage in DevTools

### Navigation with Loading States

```python
result = await execute_tool("ui_navigate", {"component": "rhetor"})
# Result includes:
# - message: "Successfully navigated to rhetor (loading state: loaded)"
# - load_time_ms: 527
```

### Capture with Loading Detection

```python
result = await execute_tool("ui_capture", {"area": "hephaestus"})
# Result includes:
# - loading_states: List of all components and their states
# - warnings: If any components are still loading
```

## Benefits

1. **Reliable Detection** - No more guessing when components are ready
2. **Performance Insights** - Track load times for optimization
3. **Error Visibility** - Clear error states with messages
4. **Debugging Aid** - Loading states visible in DOM inspector
5. **Future-Proof** - Foundation for more sophisticated state tracking

## Testing

The loading state system includes comprehensive tests:

```python
# Test that navigation waits for loaded state
result = await execute_tool("ui_navigate", {"component": "rhetor"})
assert "loading state: loaded" in result["message"]
assert result["load_time_ms"] > 0

# Test error detection
# Navigate to non-existent component shows error state
```

## Troubleshooting

### Component Stuck in Loading State
- Check browser console for JavaScript errors
- Verify component HTML file exists
- Check network tab for failed requests

### Loading States Not Detected
- Ensure MinimalLoader is being used for navigation
- Verify the component container has id="html-panel"
- Check that navigation clicks are triggering properly

### Fallback Behavior
If loading states aren't available, DevTools fall back to original detection:
- Wait for component selectors to appear
- Use network idle as a signal
- Still functional but less precise

## Future Enhancements

1. **Component-Specific States** - Components can set their own fine-grained states
2. **Progress Tracking** - `data-tekton-loading-progress="50%"`
3. **Nested Loading** - Track sub-component loading within main components
4. **Performance Metrics** - Aggregate loading statistics across sessions