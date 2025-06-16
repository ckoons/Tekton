# UI DevTools Sprint Plan

## Sprint Overview

**Sprint Name**: UI_DevTools_Sprint  
**Duration**: 5-7 days  
**Priority**: CRITICAL (Casey is about to ban Claude from UI work)  
**Risk Level**: Low (Adding tools, not changing existing UI)

## The Core Problem

Claude is effectively blind when working with UI, leading to:
1. Over-engineering simple changes
2. Requesting excessive screenshots
3. Making changes without seeing results
4. Context explosion from image analysis
5. Frequent `--nuclear-destruction` usage

## Objectives

### Primary Objectives
1. Create MCP tools in Hephaestus for UI interaction
2. Enable Claude to see and verify UI changes
3. Reduce context usage from screenshots
4. Prevent unwanted refactoring
5. Establish sandboxed UI development

### Secondary Objectives
1. Document UI patterns for Claude
2. Create UI component catalog
3. Build confidence in UI modifications
4. Improve development velocity

## Technical Approach

### Phase 1: Core MCP Tool Implementation

Create in `Hephaestus/hephaestus/mcp/ui_tools.py`:

```python
from mcp import tool
import asyncio
from playwright.async_api import async_playwright

class UIDevTools:
    """MCP tools for UI development and testing."""
    
    def __init__(self):
        self.browser = None
        self.contexts = {}  # component -> browser context
    
    @tool()
    async def ui_capture(self, component: str, selector: str = "body", 
                        format: str = "structured") -> dict:
        """
        Capture UI state without screenshots.
        
        Args:
            component: Component name (e.g., "rhetor")
            selector: CSS selector to capture
            format: "structured" | "visual" | "both"
            
        Returns:
            {
                "html": str,
                "text": str,
                "elements": [...],
                "styles": {...},
                "screenshot": base64 (if visual)
            }
        """
    
    @tool()
    async def ui_interact(self, component: str, action: str, 
                         target: str, value: str = None) -> dict:
        """
        Interact with UI elements.
        
        Args:
            action: "click" | "type" | "select" | "hover"
            target: CSS selector
            value: Value for type/select actions
            
        Returns:
            {
                "success": bool,
                "before": {...},
                "after": {...},
                "changes": [...]
            }
        """
    
    @tool()
    async def ui_sandbox(self, component: str, html_changes: str = None,
                        css_changes: str = None, js_changes: str = None) -> dict:
        """
        Test changes in isolated environment.
        
        Returns:
            {
                "preview_url": str,
                "differences": [...],
                "safe_to_apply": bool
            }
        """
    
    @tool()
    async def ui_analyze(self, component: str) -> dict:
        """
        Analyze UI structure and patterns.
        
        Returns:
            {
                "structure": {...},
                "patterns": [...],
                "api_calls": [...],
                "dependencies": [...],
                "complexity": "simple|moderate|complex"
            }
        """
```

### Phase 2: Integration Layer

Create integration with Tekton components:
- Auto-detect component URLs from GlobalConfig
- Handle authentication if needed
- Manage browser contexts efficiently
- Provide caching for common operations

### Phase 3: Safety Features

Implement safeguards:
- Change detection and preview
- Rollback capabilities
- Pattern validation
- Framework detection and warning

### Phase 4: Context Optimization

Reduce token usage:
- Structured data instead of images
- Incremental updates
- Smart diffing
- Compressed representations

## Implementation Strategy

### Day 1-2: Core Tool Development
- Set up Playwright for headless browser automation
- Implement basic capture and interact tools
- Create MCP tool registration

### Day 3-4: Sandbox Environment
- Build isolated testing environment
- Implement change preview system
- Add rollback capabilities

### Day 5: Integration & Testing
- Connect to all Tekton components
- Test with real UI modifications
- Verify context usage reduction

### Day 6-7: Documentation & Training
- Create usage examples
- Document patterns to follow
- Build Claude-specific guidelines

## Success Metrics

1. **90% reduction** in screenshot requests
2. **Zero** framework additions to simple changes
3. **50% reduction** in UI-related context usage
4. **100% preview** before committing changes
5. **Retirement** of `--nuclear-destruction` for UI work

## Risk Mitigation

1. **Browser automation complexity**: Use Playwright for reliability
2. **Performance impact**: Implement smart caching
3. **Security concerns**: Sandbox all operations
4. **Context growth**: Use structured data, not images

## Long-term Benefits

1. **Claude can evolve UI** like backend code
2. **Consistent UI improvements** across components
3. **Reduced developer frustration**
4. **Faster feature development**
5. **Better Claude-human collaboration**

## Casey's Note

"I want Claude to be as confident and capable with UI as with backend. No more blindfolded brain surgery on my frontends!"