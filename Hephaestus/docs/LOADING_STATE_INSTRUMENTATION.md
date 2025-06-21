# Loading State Instrumentation Reference

## Quick Reference for Claude Sessions

When working with Hephaestus UI components, the loading state system provides reliable detection of component readiness through semantic HTML attributes.

### Key Attributes

```html
data-tekton-loading-state="pending|loading|loaded|error"
data-tekton-loading-component="component-name"
data-tekton-loading-started="timestamp"
data-tekton-loading-error="error message"
```

### How Components Load

1. User clicks navigation item or DevTools triggers navigation
2. MinimalLoader sets `data-tekton-loading-state="pending"`
3. Component fetch begins, state changes to `"loading"`
4. On success: state becomes `"loaded"`
5. On failure: state becomes `"error"` with error message

### DevTools Integration

**Navigation waits for components to load:**
```python
# DevTools automatically wait for loading completion
result = await execute_tool("ui_navigate", {"component": "rhetor"})
# Result includes load_time_ms when using loading states
```

**Capture detects loading states:**
```python
result = await execute_tool("ui_capture", {"area": "hephaestus"})
# Check result["loading_states"] for component status
# Warnings added if components still loading
```

### Important Notes

- Container element is always `#html-panel`
- Loading states persist until next component loads
- Times are in milliseconds since epoch
- All 19 UI components support loading states

### Example DOM During Load

```html
<div id="html-panel" 
     data-tekton-loading-state="loading"
     data-tekton-loading-component="athena"
     data-tekton-loading-started="1750456131623">
  <div>Loading athena...</div>
</div>
```

### Troubleshooting

- If navigation uses fallback, check browser state
- Ensure MinimalLoader is handling navigation
- Clear error states by navigating to valid component
- Check browser console for JavaScript errors

This instrumentation enables reliable component detection, solving the DynamicContentView problem where DevTools couldn't detect when dynamic content was ready.