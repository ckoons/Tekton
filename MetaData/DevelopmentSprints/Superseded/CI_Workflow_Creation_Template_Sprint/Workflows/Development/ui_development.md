# Workflow: UI Development

## When to Use
- Working on Hephaestus UI components
- Debugging React/frontend issues
- Testing UI hot reload
- Investigating browser-specific problems
- Developing new UI features

## Prerequisites
- [ ] Hephaestus running (`tekton status hephaestus`)
- [ ] Browser developer tools knowledge
- [ ] Understanding of React/TypeScript basics

## Steps

1. Start UI development environment → Ensure everything is running
   ```bash
   # Check Hephaestus
   tekton status hephaestus
   
   # Check the port is accessible  
   curl -I http://localhost:$(tekton status hephaestus --json | jq -r .port)/
   
   # Open in browser
   open http://localhost:8317  # Or your Hephaestus port
   ```

2. Enable hot reload → Set up for rapid development
   ```bash
   # Check if watching for changes
   ps aux | grep -i "watch\|webpack\|vite"
   
   # If using the dev server
   cd $TEKTON_ROOT/ui/hephaestus
   npm run dev  # or yarn dev
   ```

3. Browser setup → Configure for development
   ```javascript
   // In browser console
   // Enable React DevTools
   window.__REACT_DEVTOOLS_GLOBAL_HOOK__.enabled = true
   
   // Check React version
   React.version
   
   // Enable verbose logging
   localStorage.setItem('debug', '*')
   ```

4. Component inspection → Use React DevTools
   ```
   1. Open React DevTools (browser extension)
   2. Select component in tree
   3. Check props and state
   4. Use Profiler for performance
   ```

5. Network debugging → Monitor API calls
   ```
   1. Open Network tab
   2. Filter by XHR/Fetch
   3. Check request/response payloads
   4. Look for failed requests (red)
   5. Verify CORS headers if needed
   ```

6. Test changes → Verify hot reload works
   ```bash
   # Make a visible change
   echo "/* Test comment */" >> src/App.css
   
   # Should auto-reload in browser
   # If not, check:
   - WebSocket connection in Network tab
   - Console for HMR errors
   - Build process logs
   ```

## UI Development Patterns

### Component Isolation Pattern
```bash
# Develop component in isolation
cd $TEKTON_ROOT/ui/hephaestus
npm run storybook  # If configured

# Or create test harness
cat > src/test-harness.tsx << 'EOF'
import React from 'react'
import { MyComponent } from './MyComponent'

export function TestHarness() {
  return (
    <div style={{ padding: '20px' }}>
      <MyComponent testProp="test value" />
    </div>
  )
}
EOF
```

### Console Debugging Pattern
```javascript
// In component code
useEffect(() => {
  console.log('[MyComponent] Mounted', { props })
  return () => console.log('[MyComponent] Unmounted')
}, [])

// Track state changes
useEffect(() => {
  console.log('[MyComponent] State changed:', state)
}, [state])
```

### API Mocking Pattern
```javascript
// Mock API responses for development
if (process.env.NODE_ENV === 'development') {
  window.fetch = new Proxy(window.fetch, {
    apply(target, thisArg, args) {
      console.log('[API]', args[0], args[1])
      // Mock specific endpoints
      if (args[0].includes('/api/status')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ status: 'mocked' })
        })
      }
      return target.apply(thisArg, args)
    }
  })
}
```

### Browser State Reset Pattern
```javascript
// Clear all browser state
function resetBrowserState() {
  localStorage.clear()
  sessionStorage.clear()
  // Clear IndexedDB if used
  indexedDB.databases().then(dbs => {
    dbs.forEach(db => indexedDB.deleteDatabase(db.name))
  })
  // Clear cookies
  document.cookie.split(";").forEach(c => {
    document.cookie = c.trim().split("=")[0] + "=;expires=Thu, 01 Jan 1970 00:00:00 UTC;"
  })
  location.reload()
}
```

## Common Issues

- **Issue**: Changes not appearing (hot reload broken)
  - **Fix**: Check WebSocket connection
  - **Browser Console**: Look for HMR errors
  - **Terminal**: Check build process output
  - **Last resort**: Restart dev server

- **Issue**: CORS errors
  - **Fix**: Check proxy configuration
  - **Config**: Usually in `package.json` or `vite.config.js`
  ```json
  "proxy": "http://localhost:8003"
  ```

- **Issue**: Component not re-rendering
  - **Fix**: Check React DevTools
  - **Common causes**:
    - State mutation instead of new object
    - Missing dependency in useEffect
    - Incorrect key prop in lists

- **Issue**: Browser cache issues
  - **Fix**: Hard reload
  - **Chrome**: Cmd+Shift+R (Mac) / Ctrl+Shift+R (PC)
  - **DevTools**: Network tab → Disable cache
  - **Nuclear option**: Incognito/Private window

## Performance Debugging

### React Profiler Pattern
```
1. Open React DevTools → Profiler
2. Click "Start profiling"
3. Interact with slow UI
4. Click "Stop profiling"
5. Analyze flame graph
```

### Network Waterfall Analysis
```
1. Network tab → Sort by time
2. Look for:
   - Long TTFB (server slow)
   - Large downloads (optimize size)
   - Waterfall stairs (parallelize)
   - Failed requests (fix errors)
```

### Memory Leak Detection
```javascript
// Monitor memory usage
const startMemory = performance.memory.usedJSHeapSize
// ... do actions ...
const endMemory = performance.memory.usedJSHeapSize
console.log('Memory delta:', endMemory - startMemory)

// Use Chrome DevTools Memory Profiler for detailed analysis
```

## Success Verification
- [ ] Hot reload works: Changes appear immediately
- [ ] No console errors: Check browser console
- [ ] Network requests succeed: Check Network tab
- [ ] Performance acceptable: < 100ms interactions
- [ ] Works in target browsers: Test Chrome, Firefox, Safari

## AI Integration for UI Development
```bash
# Use Claude in terminal for React help
# After /compact if needed

# Get component suggestions
"I need a React component that displays Tekton status with auto-refresh"

# Debug React errors
aish explain "Cannot read property 'map' of undefined in React"

# Get performance optimization tips
aish apollo "optimize this React component: [paste code]"
```

## Next Workflows
- If performance issues: [Performance Optimization workflow]
- If state management complex: [State Management workflow]
- If ready to ship: [UI Testing workflow]

## Real Example
```bash
$ cd $TEKTON_ROOT/ui/hephaestus
$ npm run dev

> hephaestus@1.0.0 dev
> vite

  VITE v4.3.9  ready in 512 ms
  
  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/

# In browser console
> localStorage.setItem('debug', 'hephaestus:*')
> location.reload()

# Now see debug output
[hephaestus:api] Fetching /api/status
[hephaestus:ws] Connected to WebSocket
[hephaestus:state] Status updated: {healthy: true}

# Make a change to App.tsx
# Browser auto-reloads with HMR
[vite] hot updated: /src/App.tsx
```

## Notes
- Browser DevTools are your best friend
- Console.log is still valuable - use it liberally during development
- React DevTools essential for component debugging
- Network tab reveals API issues quickly
- Casey's wisdom: "The UI should be a thin layer - logic belongs in the backend"
- Hot reload saves hours - make sure it works before starting