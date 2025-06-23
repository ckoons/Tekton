# Semantic UI Navigation Guide
**Version**: 1.0
**Created**: 2025-01-15
**Purpose**: Comprehensive guide for Tekton's semantic UI navigation system

## Overview

Tekton uses a semantic HTML attribute system (`data-tekton-*`) to create a navigable, self-documenting UI infrastructure. This guide documents the conventions, implementation patterns, and best practices for working with Tekton's semantic UI layer.

## Core Philosophy: Map First, Build Second

Following Casey's guidance, we treat the UI as a navigable city:
1. **Build the map** - Document conventions and patterns
2. **Place the signs** - Add semantic tags systematically  
3. **Update the map** - Refine as we learn
4. **Open the roads** - Enable features using the infrastructure

## Semantic Tag Conventions

### Hierarchy and Structure

```
data-tekton-area        → Major functional regions (navigation, content, status)
data-tekton-component   → Component workspaces (rhetor, athena, apollo)
data-tekton-type       → Element classification (workspace, panel, form)
data-tekton-section    → Sub-areas within components
```

### Navigation Tags

```html
<!-- Main navigation -->
<div data-tekton-nav="main" data-tekton-area="navigation">
  <ul data-tekton-list="components">
    <li data-tekton-nav-item="rhetor" 
        data-tekton-nav-target="rhetor"
        data-tekton-state="active">
```

### Component Tags

```html
<!-- Component workspace -->
<div class="rhetor" 
     data-tekton-area="rhetor"
     data-tekton-component="rhetor"
     data-tekton-type="component-workspace"
     data-tekton-ai="rhetor-orchestrator"
     data-tekton-ai-ready="false">
```

### Interactive Elements

```html
<!-- Actions -->
<button data-tekton-action="create"
        data-tekton-trigger="create-specialist">

<!-- Forms -->
<form data-tekton-form="specialist-config">
  <input data-tekton-field="name" 
         data-tekton-validation="required">
```

### Communication Interfaces

```html
<!-- Chat interface -->
<div data-tekton-chat="rhetor-llm"
     data-tekton-ai="rhetor-orchestrator">
  <div data-tekton-chat-messages="true"></div>
  <input data-tekton-chat-input="true">
  <button data-tekton-chat-send="true">Send</button>
</div>
```

## Implementation Patterns

### Pattern 1: Component AI Integration

**Step 1**: Tag the component container
```html
<div class="athena" 
     data-tekton-area="athena"
     data-tekton-component="athena"
     data-tekton-ai="athena-assistant">
```

**Step 2**: Map in component registry
```python
# In /Rhetor/rhetor/core/component_specialists.py
"athena": ComponentAIConfig(
    specialist_id="athena-assistant",
    model_preference="claude-3-haiku-20240307",
    system_prompt="You are Athena's knowledge assistant..."
)
```

**Step 3**: Add message handler
```javascript
// Simple inline handler
window.athena_sendChat = function() {
    const input = document.querySelector('[data-tekton-chat-input="true"]');
    fetch('/api/ai/specialists/athena-assistant/message', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            message: input.value,
            context_id: 'athena-chat'
        })
    });
};
```

### Pattern 2: Navigation State Management

```javascript
// Find active navigation
const activeNav = document.querySelector('[data-tekton-state="active"]');

// Update navigation state
function switchComponent(componentName) {
    // Deactivate current
    document.querySelectorAll('[data-tekton-nav-item]')
        .forEach(item => item.setAttribute('data-tekton-state', 'inactive'));
    
    // Activate new
    document.querySelector(`[data-tekton-nav-target="${componentName}"]`)
        .setAttribute('data-tekton-state', 'active');
}
```

### Pattern 3: AI Readiness Indicators

```javascript
// Update AI connection status
function updateAIStatus(component, ready) {
    const element = document.querySelector(`[data-tekton-component="${component}"]`);
    element?.setAttribute('data-tekton-ai-ready', ready ? 'true' : 'false');
}
```

## Working with UI DevTools

### Finding Elements by Semantic Tags

```bash
# Find all chat interfaces
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{
    "tool_name": "ui_capture",
    "arguments": {
      "selector": "[data-tekton-chat]"
    }
  }'

# Find specific component
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{
    "tool_name": "ui_capture", 
    "arguments": {
      "selector": "[data-tekton-component=\"athena\"]"
    }
  }'
```

### Testing Changes in Sandbox

```bash
# Test adding a status indicator
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -d '{
    "tool_name": "ui_sandbox",
    "arguments": {
      "selector": "[data-tekton-area=\"rhetor\"]",
      "changes": [{
        "type": "html",
        "selector": "[data-tekton-section=\"footer\"]",
        "content": "<span data-tekton-status=\"ai-connected\">AI Ready</span>",
        "action": "append"
      }]
    }
  }'
```

## Verification and Quality

### Using the Verification Script

```bash
cd /Hephaestus/scripts
node verify-semantic-tags.js
```

Expected output:
```
📊 SEMANTIC TAG VERIFICATION REPORT
=====================================

SUMMARY:
✅ Fully Tagged: 18/18
📈 Coverage: 100%
```

### Manual Verification Checklist

- [ ] All navigation items have `data-tekton-nav-item`
- [ ] All components have `data-tekton-component`
- [ ] AI-enabled components have `data-tekton-ai`
- [ ] Interactive elements have `data-tekton-action`
- [ ] Forms have `data-tekton-form`
- [ ] Chat interfaces have `data-tekton-chat`

## Best Practices

### 1. Tag Completeness
Always include the full semantic context:
```html
<!-- Good -->
<button data-tekton-action="submit"
        data-tekton-form="user-settings"
        data-tekton-component="settings">

<!-- Insufficient -->
<button data-tekton-action="submit">
```

### 2. State Consistency
Keep state attributes synchronized:
```javascript
// When showing a panel
panel.style.display = 'block';
panel.setAttribute('data-tekton-state', 'active');
panel.setAttribute('data-tekton-visibility', 'visible');
```

### 3. Hierarchical Context
Maintain parent-child relationships:
```html
<div data-tekton-component="rhetor">
  <div data-tekton-section="toolbar">
    <button data-tekton-action="refresh">
      <!-- Action is scoped to rhetor > toolbar -->
```

## Troubleshooting

### Common Issues

**Issue**: Can't find element with semantic selector
**Solution**: Verify tag spelling and use DevTools to inspect

**Issue**: AI specialist not responding
**Solution**: Check `data-tekton-ai` matches specialist ID in registry

**Issue**: Navigation state not updating
**Solution**: Ensure JavaScript updates both visual and semantic state

## Future Enhancements

### Planned Additions
- `data-tekton-permission` - Access control
- `data-tekton-telemetry` - Usage tracking
- `data-tekton-version` - Component versioning
- `data-tekton-theme` - Theme-specific variations

### UI DevTools Integration
- Semantic tag autocomplete
- Visual tag overlay mode
- Tag validation warnings
- Navigation path tracking

## References

- [Semantic Tag Conventions](/MetaData/UI/SemanticTagConventions.md)
- [Implementation Guide](/MetaData/UI/SemanticTagImplementation.md)
- [Component Specialist Registry](/Rhetor/rhetor/core/component_specialists.py)
- [UI DevTools Guide](/MetaData/TektonDocumentation/Guides/UIDevToolsExplicitGuide.md)

## Conclusion

The semantic UI navigation system transforms Tekton's interface from an uncharted maze into a well-mapped city. Every element has an address, every component has a identity, and every AI knows exactly where it belongs.

Remember: "Build the map, place the signs, update the map, open the roads."