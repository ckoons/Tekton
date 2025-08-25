# Tekton UI Semantic Tag Conventions
**Version**: 1.0
**Created**: 2025-01-15
**Purpose**: Define semantic HTML data attributes for CI navigation and UI DevTools

## Overview
This document defines the `data-tekton-*` attribute conventions used throughout the Tekton UI to enable:
- CI assistants to navigate and understand the UI structure
- UI DevTools to identify and interact with components
- Consistent patterns across all Tekton components

## Core Conventions

### 1. Area Tags (Major UI Regions)
- `data-tekton-area="[area-name]"` - Identifies major UI sections
  - Examples: `rhetor`, `athena`, `apollo`, `navigation`, `status-bar`

### 2. Component Tags
- `data-tekton-component="[component-id]"` - Identifies component workspaces
- `data-tekton-type="component-workspace"` - Marks component container

### 3. Navigation Tags
- `data-tekton-nav="main|component|context"` - Navigation areas
- `data-tekton-nav-item="[item-id]"` - Individual navigation items
- `data-tekton-nav-target="[target-component]"` - Navigation destination

### 4. Interactive Elements
- `data-tekton-action="[action-type]"` - Buttons and controls
  - Examples: `create`, `delete`, `refresh`, `submit`, `clear`
- `data-tekton-trigger="[event-name]"` - What the action triggers

### 5. Chat/Communication
- `data-tekton-chat="[chat-id]"` - Chat interface container
- `data-tekton-chat-input="true"` - Chat input field
- `data-tekton-chat-messages="true"` - Message display area
- `data-tekton-chat-send="true"` - Send button

### 6. CI Integration
- `data-tekton-ai="[specialist-id]"` - CI specialist assignment
- `data-tekton-ai-ready="true|false"` - CI connection status
- `data-tekton-ai-model="[model-name]"` - Active model indicator

### 7. Status and State
- `data-tekton-status="[status-type]"` - Status indicators
- `data-tekton-state="active|inactive|loading|error"` - Current state
- `data-tekton-visibility="visible|hidden"` - Visibility state

### 8. Content Organization
- `data-tekton-panel="[panel-name]"` - Content panels
- `data-tekton-tab="[tab-id]"` - Tab navigation
- `data-tekton-section="[section-name]"` - Content sections

### 9. Forms and Inputs
- `data-tekton-form="[form-name]"` - Form containers
- `data-tekton-field="[field-name]"` - Form fields
- `data-tekton-validation="required|optional"` - Field validation

### 10. Data Display
- `data-tekton-list="[list-type]"` - List containers
- `data-tekton-grid="[grid-type]"` - Grid layouts
- `data-tekton-item="[item-type]"` - Individual items
- `data-tekton-id="[unique-id]"` - Unique identifiers

## Usage Examples

### Component Header
```html
<div class="rhetor" 
     data-tekton-area="rhetor" 
     data-tekton-component="rhetor"
     data-tekton-type="component-workspace"
     data-tekton-ai="rhetor-orchestrator"
     data-tekton-ai-ready="false">
```

### Navigation Item
```html
<div class="nav-item" 
     data-tekton-nav-item="rhetor-nav"
     data-tekton-nav-target="rhetor"
     data-tekton-state="active">
  Rhetor
</div>
```

### Chat Interface
```html
<div class="chat-container"
     data-tekton-chat="rhetor-llm"
     data-tekton-ai="rhetor-orchestrator">
  <div data-tekton-chat-messages="true">...</div>
  <input data-tekton-chat-input="true" />
  <button data-tekton-action="send" 
          data-tekton-chat-send="true">Send</button>
</div>
```

### Action Button
```html
<button data-tekton-action="create"
        data-tekton-trigger="create-specialist"
        data-tekton-state="active">
  Create Specialist
</button>
```

## Best Practices

1. **Be Specific**: Use descriptive values that clearly identify the element's purpose
2. **Be Consistent**: Follow the same patterns across all components
3. **Layer Tags**: Use multiple attributes to provide rich context
4. **Maintain State**: Keep state attributes updated dynamically
5. **Think Navigation**: Consider how CI will traverse from element to element

## Tag Hierarchy
When multiple tags apply, use this priority order:
1. `data-tekton-area` (highest level)
2. `data-tekton-component` 
3. `data-tekton-type`
4. Functional tags (chat, form, nav, etc.)
5. State tags (status, visibility)
6. Specific identifiers (lowest level)

## Future Considerations
- Add `data-tekton-version` for component versioning
- Consider `data-tekton-permissions` for access control
- Explore `data-tekton-telemetry` for usage tracking

## Maintenance
This document should be updated when:
- New UI patterns emerge
- New component types are added
- CI navigation requirements change
- DevTools capabilities expand