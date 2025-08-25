# Semantic Tag Quick Reference

## Essential Tags

### Structure
```html
data-tekton-area="navigation|content|status"
data-tekton-component="rhetor|athena|apollo|..."
data-tekton-type="workspace|panel|form|list"
data-tekton-section="header|main|footer"
```

### Navigation
```html
data-tekton-nav="main|component|context"
data-tekton-nav-item="[component-name]"
data-tekton-nav-target="[destination]"
```

### CI Integration
```html
data-tekton-ai="[specialist-id]"
data-tekton-ai-ready="true|false"
data-tekton-ai-model="[model-name]"
```

### Interaction
```html
data-tekton-action="create|delete|submit|refresh"
data-tekton-trigger="[event-name]"
data-tekton-chat="[chat-id]"
data-tekton-chat-input="true"
data-tekton-chat-send="true"
```

### State
```html
data-tekton-state="active|inactive|loading|error"
data-tekton-visibility="visible|hidden"
data-tekton-status="connected|disconnected|pending"
```

## Quick Patterns

### Find Component
```javascript
document.querySelector('[data-tekton-component="rhetor"]')
```

### Find All Chats
```javascript
document.querySelectorAll('[data-tekton-chat]')
```

### Update State
```javascript
element.setAttribute('data-tekton-state', 'active')
```

### Check CI Ready
```javascript
const ready = element.getAttribute('data-tekton-ai-ready') === 'true'
```

## Component-AI Mapping
- rhetor → rhetor-orchestrator
- athena → athena-assistant
- apollo → apollo-assistant
- budget → budget-assistant
- engram → engram-assistant
- prometheus → prometheus-assistant
- metis → metis-assistant
- harmonia → harmonia-assistant
- synthesis → synthesis-assistant
- sophia → sophia-assistant
- ergon → ergon-assistant
- telos → telos-assistant