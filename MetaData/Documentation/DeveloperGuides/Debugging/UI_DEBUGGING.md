# Hephaestus UI Debugging Guide

## Overview
Hephaestus UI includes a built-in debug system that helps identify loaded files, track component behavior, and diagnose issues without modifying code or impacting performance when disabled.

## Quick Start

### Enable Debug Output
```javascript
// In browser console:
HephaestusDebug.enableFileTrace()  // See which files are loaded
HephaestusDebug.enableAll()         // See all debug messages
```

### Via URL
```
http://localhost:8080/?debug=fileTrace      // File traces only
http://localhost:8080/?debug=all            // All debug output
http://localhost:8080/?debug=none           // Disable all debug
```

## Debug Categories

| Category | Description | Example Output |
|----------|-------------|----------------|
| `fileTrace` | Shows when JavaScript files are loaded | `[FILE_TRACE] Loading: main.js` |
| `minimalLoader` | Component loading details | `MinimalLoader: Loading component ergon` |
| `uiManager` | UI state changes | `[UIManager] Activating component: athena` |
| `component` | Component-specific messages | `Numa component initialized` |
| `all` | Enable/disable everything | - |

## Common Debugging Tasks

### 1. Identify Which Files Are Actually Used
```javascript
// Enable file tracing
HephaestusDebug.enableFileTrace()

// Reload the page and click through all components
// Copy console output to analyze which files load
```

### 2. Debug Component Loading Issues
```javascript
// Enable loader debugging
HephaestusDebug.enable('minimalLoader')

// Try to load the problematic component
// Check console for loading errors or missing scripts
```

### 3. Track UI State Changes
```javascript
// Enable UI manager debugging
HephaestusDebug.enable('uiManager')

// Navigate between components to see state transitions
```

### 4. Production Debugging
```
// Add debug parameter to production URL
https://your-domain.com/?debug=all

// Debug settings persist in localStorage
// User can disable with: HephaestusDebug.disableAll()
```

## Console Commands Reference

```javascript
// Check current debug configuration
HephaestusDebug.status()

// Enable specific category
HephaestusDebug.enable('fileTrace')
HephaestusDebug.enable('minimalLoader')

// Disable specific category
HephaestusDebug.disable('fileTrace')

// Enable all debug output
HephaestusDebug.enableAll()

// Disable all debug output (default)
HephaestusDebug.disableAll()

// Reset to defaults
HephaestusDebug.reset()
```

## Implementation Details

### How It Works
1. `debug-config.js` loads before all other scripts
2. Overrides `console.log` to filter messages based on patterns
3. Preserves `console.warn` and `console.error` (always visible)
4. Settings persist in localStorage
5. No performance impact when disabled (early return)

### Adding Debug Output to New Files
```javascript
// At the top of any JavaScript file:
console.log('[FILE_TRACE] Loading: my-new-file.js');

// For component-specific debugging:
console.log('MyComponent: Initialization started');

// For loader debugging:
console.log('MinimalLoader: Custom loading step');
```

### File Structure
```
scripts/
  debug-config.js         # Debug system configuration
  debug-shim.js          # Browser compatibility shim
  shared/diagnostic.js   # Additional diagnostic tools
```

## Maintenance Tasks

### Finding Unused Files
1. Enable file tracing: `HephaestusDebug.enableFileTrace()`
2. Clear browser console
3. Reload page and navigate through ALL components
4. Copy console output
5. Extract FILE_TRACE lines: `grep '[FILE_TRACE]' console.log`
6. Compare with actual files to find unused ones

### Component Registry Validation
The `component_registry.json` defines which scripts load for each component:
```json
{
  "id": "ergon",
  "scripts": [
    "scripts/shared/tab-navigation.js",
    "scripts/ergon/ergon-component.js"
  ]
}
```

Check if registry matches actual usage by comparing debug output with registry entries.

## Best Practices

1. **Always include file trace** in new JavaScript files:
   ```javascript
   console.log('[FILE_TRACE] Loading: filename.js');
   ```

2. **Use descriptive prefixes** for debug messages:
   - `[FILE_TRACE]` for file loading
   - `[Component]` for component-specific
   - `[ERROR]` for errors (use console.error)
   - `[WARN]` for warnings (use console.warn)

3. **Default to disabled** - Debug output should be opt-in

4. **Document debug flags** in component documentation

## Troubleshooting

### Debug Not Working?
1. Check that `debug-config.js` is loaded in index.html
2. Clear browser cache and reload
3. Check browser console for errors
4. Try `HephaestusDebug.reset()` then reload

### Too Much Output?
```javascript
// Disable all but specific category
HephaestusDebug.disableAll()
HephaestusDebug.enable('fileTrace')  // Just file traces
```

### Settings Not Persisting?
- Check if localStorage is enabled
- Try incognito/private mode
- Check for browser extensions blocking storage

## For AI Assistants (Claude)

When debugging Hephaestus UI issues:

1. First check debug status:
   ```javascript
   HephaestusDebug.status()
   ```

2. Enable appropriate debugging:
   ```javascript
   HephaestusDebug.enable('fileTrace')     // For file loading issues
   HephaestusDebug.enable('minimalLoader') // For component loading
   HephaestusDebug.enableAll()             // For general debugging
   ```

3. Ask user to:
   - Reload the page
   - Reproduce the issue
   - Copy console output
   - Share the FILE_TRACE entries

4. The debug system helps identify:
   - Which files are actually loaded vs unused
   - Component loading sequence and errors
   - UI state transitions
   - Performance bottlenecks

Remember: Debug output is filtered by `debug-config.js` without modifying the original console.log statements.