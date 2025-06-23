# UI DevTools V2 Documentation

## Overview

The UI DevTools V2 represent a fundamental shift in how we approach UI development debugging. Based on the philosophy **"Code is Truth, Browser is Result"**, these tools help you understand not just what's in the browser, but WHY it differs from your source code.

## Key Discovery

Our investigation revealed that Hephaestus components are working perfectly:
- **Source Code**: 75 semantic tags (in rhetor component)
- **Browser DOM**: 146 semantic tags 
- **Difference**: Browser ADDS 71 dynamic tags for navigation, loading states, and runtime behavior

This was the opposite of what we expected - components aren't broken, they're being enriched!

## Documentation Guide

### Getting Started
- [**QuickStart.md**](QuickStart.md) - Get up and running in 5 minutes
- [**CorePhilosophy.md**](CorePhilosophy.md) - Understanding "Code is Truth, Browser is Result"

### Core Concepts  
- [**StaticVsDynamicTags.md**](StaticVsDynamicTags.md) - Why browser has 146 tags when source has 75
- [**Migration.md**](Migration.md) - What changed from the old UI DevTools

### Technical Reference
- [**APIReference.md**](APIReference.md) - Complete API documentation with examples
- [**Troubleshooting.md**](Troubleshooting.md) - Common issues and solutions

### Practical Guides
- [**UIDevToolsCookbook.md**](../UIDevToolsCookbook.md) - Common UI development tasks
- [**UIDevToolsReference.md**](../UIDevToolsReference.md) - Tool usage patterns

### Related Documentation
- [**LoadingStateSystem.md**](../LoadingStateSystem.md) - Understanding dynamic content loading
- [**SemanticUINavigationGuide.md**](../SemanticUINavigationGuide.md) - Navigation patterns and semantic tags

## The Five Tools

1. **CodeReader** - Reads component source files to establish ground truth
2. **BrowserVerifier** - Checks actual DOM state in the browser
3. **Comparator** - Analyzes differences between source and DOM
4. **Navigator** - Reliably navigates to components
5. **SafeTester** - Tests changes in isolation before applying

## Quick Example

```bash
# Launch the tools
cd /Users/cskoons/projects/github/Tekton/Hephaestus
./run_mcp.sh

# In another terminal, try the tools
python ui_dev_tools/try_comparator.py
```

You'll see:
- Source: 75 tags (what you wrote)
- Browser: 146 tags (what's running)
- Difference: 71 dynamic tags added by the system

## Why This Matters

The old tools would report "semantic tags not found" because they only looked at the browser. The new tools reveal:
1. Your components ARE properly instrumented
2. The system ENRICHES them with dynamic functionality
3. Missing tags might be a loading issue, not a source code issue

## For Implementers

When adding technical details to this documentation:
- Add specific API examples to the Reference
- Include error handling patterns in the Cookbook
- Document any edge cases discovered during implementation