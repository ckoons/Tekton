# Instrumentation Handoff for Next Claude

## Welcome, Next Claude! 👋

Casey wants to "finish the instrumentation of the codebase" - a critical task for making Tekton fully AI/CI-friendly. This document will guide you through what needs to be done.

## Current State

### What's Already Done ✅
1. **UI DevTools** - Powerful tools for UI manipulation (ui_capture, ui_workflow, etc.)
2. **Semantic Analysis Tools** - Can analyze and score semantic completeness
3. **Component Architecture Mapping** - Understands relationships between components
4. **Screenshot Capabilities** - CIs can now take their own screenshots

### What's Missing 🔍
1. **Incomplete Semantic Tagging** - Many components lack proper `data-tekton-*` attributes
2. **Navigation Reliability** - Components don't always load when clicked
3. **Component Discovery** - No consistent way for AI/CI to find all editable parts
4. **State Management Visibility** - Component states aren't exposed for AI inspection

## Phase 5: Complete UI Instrumentation

### Goal
Make every UI element discoverable, identifiable, and editable by AI/CI tools.

### 1. Semantic Tag Completion

**Current Coverage**: ~40% (based on validation scans)

**Target Coverage**: 100%

**Priority Components to Instrument**:
```bash
# Run this to see current coverage
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{"tool_name":"ui_semantic_scan","arguments":{}}'
```

**Required Tags for Each Component**:
```html
<!-- Root container -->
<div class="rhetor" data-tekton-area="rhetor" data-tekton-type="component">
  
  <!-- Header zone -->
  <div class="rhetor__header" data-tekton-zone="header">
    <h2 data-tekton-element="title">Rhetor - LLM Interface</h2>
  </div>
  
  <!-- Menu zone -->
  <div class="rhetor__menu" data-tekton-zone="menu">
    <div class="rhetor__tab" data-tekton-action="switch-tab" data-tekton-target="chat">
      Chat
    </div>
  </div>
  
  <!-- Content zone -->
  <div class="rhetor__content" data-tekton-zone="content">
    <!-- Interactive elements -->
    <button data-tekton-action="send-message" data-tekton-state="enabled">
      Send
    </button>
  </div>
  
  <!-- Footer zone -->
  <div class="rhetor__footer" data-tekton-zone="footer">
    <span data-tekton-status="connection">Connected</span>
  </div>
</div>
```

### 2. Navigation Reliability Fix

**Problem**: Navigation clicks report success but components don't load
**Root Cause**: Terminal panel vs HTML panel switching issues

**Solution Approach**:
1. Add explicit panel management
2. Force HTML panel visibility when navigating
3. Add component load verification

**Implementation**:
```javascript
// In each component's initialization
window.addEventListener('component-navigate', (e) => {
  if (e.detail.component === 'rhetor') {
    // Force HTML panel visible
    document.getElementById('html-panel').style.display = 'block';
    document.getElementById('terminal-panel').style.display = 'none';
    
    // Load component
    loadRhetorComponent();
    
    // Report successful load
    window.postMessage({
      type: 'component-loaded',
      component: 'rhetor',
      timestamp: Date.now()
    }, '*');
  }
});
```

### 3. Component Registry

**Create a central registry for all components**:

```javascript
// shared/component-registry.js
window.TektonComponents = {
  rhetor: {
    path: '/components/rhetor-component.html',
    selector: '.rhetor',
    zones: ['header', 'menu', 'content', 'footer'],
    actions: ['send-message', 'clear-chat', 'switch-model'],
    states: ['connected', 'disconnected', 'loading']
  },
  hermes: {
    path: '/components/hermes-component.html',
    selector: '.hermes',
    zones: ['header', 'menu', 'content', 'footer'],
    actions: ['subscribe', 'unsubscribe', 'send-event'],
    states: ['active', 'paused', 'error']
  },
  // ... all other components
};
```

### 4. State Exposure for AI

**Add data attributes that expose component state**:

```html
<!-- Component state attributes -->
<div class="rhetor" 
     data-tekton-area="rhetor"
     data-tekton-state-loaded="true"
     data-tekton-state-active="true"
     data-tekton-state-mode="chat"
     data-tekton-state-model="claude-3">
```

**Update states dynamically**:
```javascript
function updateComponentState(component, key, value) {
  const element = document.querySelector(`[data-tekton-area="${component}"]`);
  if (element) {
    element.setAttribute(`data-tekton-state-${key}`, value);
    // Notify DevTools
    window.postMessage({
      type: 'state-changed',
      component,
      key,
      value
    }, '*');
  }
}
```

## Phase 6: Full Codebase Instrumentation

### Goal
Make the entire Tekton codebase AI/CI-friendly for editing, understanding, and modification.

### 1. File Header Instrumentation

**Add AI-readable headers to all files**:

```python
"""
@tekton-component: rhetor
@tekton-type: api-handler
@tekton-dependencies: [hermes, athena]
@tekton-description: Handles LLM communication and prompt management
@tekton-owner: rhetor-team
@tekton-tests: tests/test_rhetor_api.py
"""
```

```javascript
/**
 * @tekton-component: rhetor
 * @tekton-type: ui-component
 * @tekton-zones: [header, menu, content, footer]
 * @tekton-events-in: [model-changed, message-received]
 * @tekton-events-out: [send-message, clear-chat]
 * @tekton-state-keys: [connected, model, mode]
 */
```

### 2. Function/Method Instrumentation

```python
def send_message(self, message: str, context: dict) -> dict:
    """
    @tekton-action: send-llm-message
    @tekton-inputs: {message: string, context: object}
    @tekton-outputs: {response: string, tokens: number}
    @tekton-errors: [RateLimitError, ModelError, NetworkError]
    @tekton-sideeffects: [updates-message-history, consumes-tokens]
    """
```

### 3. Configuration Instrumentation

```yaml
# config/rhetor.yaml
rhetor:
  # @tekton-configurable: true
  # @tekton-restart-required: false
  # @tekton-validation: port_number
  port: 8003
  
  # @tekton-configurable: true
  # @tekton-restart-required: true
  # @tekton-options: [claude-3, gpt-4, llama-2]
  default_model: claude-3
```

### 4. Test Instrumentation

```python
class TestRhetor:
    """
    @tekton-test-component: rhetor
    @tekton-test-type: integration
    @tekton-test-coverage: [api, websocket, state-management]
    @tekton-test-dependencies: [mock-hermes, test-db]
    """
    
    def test_send_message(self):
        """
        @tekton-test-target: rhetor.send_message
        @tekton-test-scenario: successful-message-send
        @tekton-test-validates: [message-format, response-structure, token-counting]
        """
```

### 5. Error & Logging Instrumentation

```python
logger.info(
    "Message sent successfully",
    extra={
        "tekton_component": "rhetor",
        "tekton_action": "send_message", 
        "tekton_metadata": {
            "model": model_name,
            "tokens": token_count,
            "latency_ms": latency
        }
    }
)
```

## Implementation Strategy

### Week 1: UI Semantic Tagging
1. Complete semantic tags for navigation components
2. Add tags to top 5 most-used components (rhetor, hermes, athena, engram, apollo)
3. Create validation report

### Week 2: Navigation & State Management
1. Fix navigation reliability issues
2. Implement component registry
3. Add state exposure attributes

### Week 3: Codebase Headers & Documentation
1. Add instrumentation headers to all Python files
2. Add instrumentation headers to all JavaScript files
3. Generate AI-readable component map

### Week 4: Testing & Validation
1. Run full semantic validation scan
2. Test AI/CI editing scenarios
3. Create instrumentation coverage report

## Success Metrics

1. **UI Coverage**: 100% of components have semantic tags
2. **Navigation Success**: 100% reliable component loading
3. **State Visibility**: All component states exposed via data attributes
4. **Code Coverage**: 100% of files have instrumentation headers
5. **AI Discoverability**: Any AI can find and understand any component/function

## Tools to Use

1. **ui_semantic_scan** - Find components missing tags
2. **ui_component_map** - Understand component relationships
3. **ui_workflow** - Test component interactions
4. **grep/glob** - Find files missing instrumentation

## Example Workflow

```bash
# 1. Scan current state
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{"tool_name":"ui_semantic_scan","arguments":{}}'

# 2. Pick a component with low score
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{"tool_name":"ui_workflow","arguments":{"workflow":"debug_component","component":"rhetor"}}'

# 3. Add semantic tags
# Edit rhetor-component.html to add data-tekton-* attributes

# 4. Validate improvements
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{"tool_name":"ui_semantic_analysis","arguments":{"component":"rhetor"}}'
```

## Casey's Vision

Remember Casey's goals:
- **Simple is better** - Don't over-engineer
- **No frameworks** - Keep it vanilla HTML/CSS/JS
- **AI-friendly** - Every element should be discoverable
- **CI empowerment** - CIs should be able to modify anything

## Questions to Ask Casey

1. "Should we prioritize UI instrumentation or codebase instrumentation first?"
2. "Which components are most critical for the CIs to modify?"
3. "Do you want instrumentation to include performance metrics?"
4. "Should we create an instrumentation style guide?"

---

## Update: Progress Made (2025-06-20)

### What Was Accomplished
1. **Fixed Navigation Tools** - Added JavaScript component loading to ui_navigate
2. **Instrumented Profile Component** - Added 43 semantic tags following Rhetor patterns
3. **Created Documentation**:
   - INSTRUMENTATION_PATTERNS.md - Complete guide to semantic tagging
   - INSTRUMENTATION_STATUS.md - Current status of all components
4. **Analyzed All Components** - Found 2 fully, 11 partially, and 10 not instrumented

### Key Learnings
- The DevTools navigation issue persists despite fixes
- Direct file editing is more reliable than UI-based tools
- Many components (11) already have basic instrumentation started
- The patterns from Rhetor work well and are easy to apply

### Recommended Next Steps
1. Complete the 11 partially instrumented components (just add zones)
2. Use direct file editing rather than fighting with DevTools
3. Consider creating an automation script for repetitive tagging

Good luck! The foundation is solid - now it's time to make every pixel and every line of code AI-accessible! 🚀