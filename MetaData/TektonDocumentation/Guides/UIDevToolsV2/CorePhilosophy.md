# Core Philosophy: Code is Truth, Browser is Result

## The Paradigm Shift

The UI DevTools V2 are built on a fundamental principle that changes how we debug UI issues:

> **Code is Truth, Browser is Result to Verify**

This means:
- Your source code files define what SHOULD exist (the truth)
- The browser DOM shows what DOES exist (the result)
- Discrepancies reveal system behavior, not necessarily problems

## Why This Matters

### The Old Way (UI DevTools V1)
```
Browser DOM → "Can't find semantic tags" → Confusion
```

The old tools only looked at the browser. When they couldn't find expected elements, they reported failures without context. This led to:
- Developers thinking components weren't instrumented
- Wasted time adding tags that already existed in source
- No understanding of dynamic behavior

### The New Way (UI DevTools V2)
```
Source Code (Truth) → Browser DOM (Result) → Understanding
       75 tags              146 tags         "71 tags added dynamically"
```

The new tools compare source to browser, revealing:
- Components ARE properly instrumented
- System adds dynamic functionality
- Browser enriches, not corrupts

## The Three Stages of UI Component Life

### 1. Design Time (Source Code)
What you write in your HTML/CSS/JS files:
```html
<div data-tekton-component="rhetor" 
     data-tekton-area="rhetor"
     data-tekton-type="component-workspace">
  <!-- Your designed structure -->
</div>
```

### 2. Load Time (Component Loading)
When MinimalLoader loads your component:
- Reads your source files
- Preserves your semantic tags
- Initializes component structure

### 3. Runtime (Browser DOM)
After component is active:
- System adds navigation tags (`nav-item`, `nav-target`)
- Loading states are tracked (`loading-state`, `loading-component`)
- Runtime states are managed (`state`, `active`)

## Understanding Static vs Dynamic Tags

### Static Tags (From Source)
These are your design decisions:
- `data-tekton-component` - Component identity
- `data-tekton-zone` - Layout structure  
- `data-tekton-action` - Defined behaviors
- `data-tekton-panel` - Content organization

### Dynamic Tags (Added at Runtime)
These are system enhancements:
- `data-tekton-nav-item` - Navigation tracking
- `data-tekton-loading-state` - Load progress
- `data-tekton-state` - Runtime state
- `data-tekton-active` - Current status

## Debugging with This Philosophy

### Scenario 1: "My semantic tags aren't showing"
**Old approach**: Add more tags to the source
**New approach**: 
1. Check source with CodeReader - Are tags there? ✓
2. Check browser with BrowserVerifier - Are they in DOM? 
3. If missing, investigate the loading pipeline

### Scenario 2: "Unexpected tags in browser"
**Old approach**: Confusion, manual DOM inspection
**New approach**:
1. Use Comparator to identify dynamic tags
2. Understand they're system features
3. Work with them, not against them

### Scenario 3: "Component behavior seems wrong"
**Old approach**: Blind modifications
**New approach**:
1. Verify source truth first
2. Check runtime result
3. Understand the transformation

## The Tools Embody This Philosophy

1. **CodeReader**: Establishes truth from source
2. **BrowserVerifier**: Captures result from browser
3. **Comparator**: Reveals the transformation
4. **Navigator**: Works with the system
5. **SafeTester**: Respects both truth and result

## Key Takeaway

> When browser doesn't match expectations of the codebase, it's not always a bug - it might be a feature.

The UI DevTools V2 help you understand which is which.