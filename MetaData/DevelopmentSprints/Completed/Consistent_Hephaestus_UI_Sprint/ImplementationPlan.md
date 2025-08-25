# Consistent Hephaestus UI Sprint - Implementation Plan

## Overview

This document provides the detailed implementation plan for the Consistent Hephaestus UI Development Sprint. It outlines the specific steps, code patterns, and migration strategies needed to achieve the sprint goals.

## Phase 1: Framework Migration

### Component Migration Order

We'll migrate components in order of complexity, starting with simpler components to establish patterns:

1. **Tekton** - Main dashboard, good first candidate
2. **Prometheus** - Planning component, relatively simple
3. **Telos** - Requirements tracking, straightforward structure
4. **Metis** - Workflow management
5. **Harmonia** - Orchestration
6. **Synthesis** - Integration
7. **Apollo** - Attention/Prediction (more complex)
8. **Athena** - Knowledge management
9. **Sophia** - Learning/Adaptation
10. **Engram** - Memory (complex state)
11. **Ergon** - Agents/Tools (complex interactions)
12. **Hermes** - Messaging (real-time features)
13. **Budget/Penia** - Budget tracking
14. **Codex** - Documentation
15. **Tekton-Dashboard** - Special case, may need different approach

### Migration Steps for Each Component

#### Step 1: Analyze Current Implementation

```bash
# For each component, document:
1. Current tab structure
2. JavaScript functions used
3. Event handlers present
4. State management approach
5. Any component-specific features
```

#### Step 2: Create Radio Button Structure

```html
<!-- Add at the beginning of component HTML -->
<input type="radio" name="[component]-tab" id="tab-dashboard" checked style="display: none;">
<input type="radio" name="[component]-tab" id="tab-[tabname]" style="display: none;">
<!-- Add one radio for each tab -->
```

#### Step 3: Convert Tab Navigation

Replace onclick handlers:
```html
<!-- OLD -->
<div class="apollo__tab" onclick="apollo_switchTab('dashboard')">
  <span class="apollo__tab-label">Dashboard</span>
</div>

<!-- NEW -->
<label for="tab-dashboard" class="apollo__tab" data-tab="dashboard">
  <span class="apollo__tab-label">Dashboard</span>
</label>
```

#### Step 4: Update CSS for State Management

```css
/* Remove JavaScript-dependent classes */
.component__panel--active { /* DELETE THIS */ }

/* Add radio-button-based visibility */
.component__panel {
  display: none;
}

#tab-dashboard:checked ~ .component__content #dashboard-panel {
  display: block;
}

/* Update active tab styling */
#tab-dashboard:checked ~ .component__menu-bar label[for="tab-dashboard"] {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}
```

#### Step 5: Remove JavaScript Functions

Delete these functions from component JavaScript:
- `component_switchTab()`
- Any tab-related event handlers
- Tab initialization code

#### Step 6: Update Semantic Tags

Ensure consistent tagging:
```html
<div class="component" 
     data-tekton-area="component"
     data-tekton-component="componentName"
     data-tekton-type="component-workspace">
```

#### Step 7: Test Navigation

1. Click each tab to verify switching works
2. Refresh page to ensure default tab shows
3. Test keyboard navigation (Tab + Space/Enter on labels)
4. Verify no console errors

### Common Patterns to Apply

#### Radio Button Pattern
```html
<!-- Hidden radios before component -->
<input type="radio" name="comp-tab" id="tab-1" checked style="display: none;">
<input type="radio" name="comp-tab" id="tab-2" style="display: none;">

<!-- Labels in menu -->
<label for="tab-1" class="comp__tab">Tab 1</label>
<label for="tab-2" class="comp__tab">Tab 2</label>

<!-- Panels in content -->
<div id="panel-1" class="comp__panel">Content 1</div>
<div id="panel-2" class="comp__panel">Content 2</div>
```

#### CSS Visibility Pattern
```css
/* Hide all panels by default */
.comp__panel { display: none; }

/* Show checked panel */
#tab-1:checked ~ .comp__content #panel-1 { display: block; }
#tab-2:checked ~ .comp__content #panel-2 { display: block; }

/* Style active tab */
#tab-1:checked ~ .comp__menu-bar label[for="tab-1"] {
  background: var(--active-bg);
}
```

## Phase 2: Chat Implementation

### Team Chat Integration

#### Step 1: Create Shared Team Chat Component

Location: `/Hephaestus/ui/shared/team-chat.html`

```html
<!-- Team Chat Panel -->
<div id="teamchat-panel" class="component__panel" 
     data-tekton-panel="teamchat"
     data-tekton-panel-for="Team Chat">
  <div class="component__chat-container">
    <div class="component__chat-messages" id="team-chat-messages">
      <!-- Messages will appear here -->
    </div>
    <div class="component__chat-input-container">
      <input type="text" 
             class="component__chat-input" 
             id="team-chat-input"
             placeholder="Message all CI specialists..."
             data-tekton-chat-input="team">
      <button class="component__chat-send" 
              onclick="sendTeamMessage(); return false;">
        Send
      </button>
    </div>
  </div>
</div>
```

#### Step 2: Add Team Chat Tab to Each Component

```html
<!-- Add to component's tab navigation -->
<input type="radio" name="comp-tab" id="tab-teamchat" style="display: none;">

<!-- Add to menu bar -->
<label for="tab-teamchat" class="comp__tab" data-tab="teamchat">
  <span class="comp__tab-label">Team Chat</span>
</label>
```

#### Step 3: Include Team Chat in Build Process

Update build script to include shared team chat in each component.

### Specialist Chat Implementation

#### Step 1: Add Specialist Chat Tab

```html
<!-- Add radio button -->
<input type="radio" name="comp-tab" id="tab-specialist" style="display: none;">

<!-- Add menu item (customize label per component) -->
<label for="tab-specialist" class="comp__tab" data-tab="specialist">
  <span class="comp__tab-label">[Component] Chat</span>
</label>
```

#### Step 2: Create Specialist Chat Panel

```html
<div id="specialist-panel" class="component__panel"
     data-tekton-panel="specialist"
     data-tekton-panel-for="[Component] Chat">
  <div class="component__chat-container">
    <div class="component__chat-messages" id="specialist-chat-messages">
      <!-- CI specialist responses here -->
    </div>
    <div class="component__chat-input-container">
      <input type="text"
             class="component__chat-input"
             id="specialist-chat-input"
             placeholder="Ask [Component] AI..."
             data-tekton-chat-input="specialist"
             data-tekton-ai="[component]-ai">
      <button class="component__chat-send"
              onclick="sendSpecialistMessage(); return false;">
        Send
      </button>
    </div>
  </div>
</div>
```

#### Step 3: Configure CI Endpoint

Each specialist chat needs configuration:
```javascript
// In component's minimal JavaScript
const SPECIALIST_CONFIG = {
  endpoint: `ws://localhost:${COMPONENT_PORTS.[component]}/ws`,
  ai_name: '[Component] Specialist',
  ai_id: '[component]-ai'
};
```

### WebSocket Integration

#### Shared WebSocket Handler

```javascript
// Minimal WebSocket code for chat functionality
function initializeChat(config) {
  const ws = new WebSocket(config.endpoint);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'chat_response') {
      appendMessage(data.message, data.sender);
    }
  };
  
  return ws;
}
```

## Phase 3: Testing and Refinement

### Component Testing Checklist

For each migrated component:

- [ ] All tabs switch correctly without JavaScript
- [ ] Default tab displays on page load
- [ ] Keyboard navigation works (Tab + Space/Enter)
- [ ] No JavaScript console errors
- [ ] Specialist chat connects to correct AI
- [ ] Team chat is accessible and functional
- [ ] Visual styling matches original
- [ ] Semantic tags are consistent
- [ ] Clear button works in chat interfaces

### Browser Testing Matrix

Test in:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Integration Testing

1. **Navigation Flow**: User can navigate between all components
2. **Chat Persistence**: Chat history maintained during session
3. **AI Communication**: Messages reach correct CI specialists
4. **Team Chat Sync**: Same team chat across all components
5. **WebSocket Stability**: Connections remain stable

### Performance Verification

- [ ] Page load time not significantly impacted
- [ ] Tab switching is instant (<16ms)
- [ ] No memory leaks from removed JavaScript
- [ ] CSS parsing remains efficient

## Migration Utilities

### Quick Reference Sed Commands

```bash
# Replace onclick with label pattern
sed -i 's/onclick=".*_switchTab(\(.*\))"/for="tab-\1"/g' component.html

# Remove --active classes
sed -i 's/component__tab--active//g' component.html
sed -i 's/component__panel--active//g' component.html
```

### Validation Script

```python
# validate_component.py
def validate_migration(component_path):
    with open(component_path, 'r') as f:
        content = f.read()
    
    issues = []
    
    # Check for onclick handlers
    if 'onclick=' in content and 'onclick="return false;"' not in content:
        issues.append("Found onclick handlers")
    
    # Check for radio buttons
    if 'type="radio"' not in content:
        issues.append("No radio buttons found")
    
    # Check for labels
    if '<label for="tab-' not in content:
        issues.append("No tab labels found")
    
    return issues
```

## Rollback Strategy

If a component migration fails:

1. Git stash changes: `git stash`
2. Fix identified issues
3. Re-apply changes: `git stash pop`
4. Re-test thoroughly

Never commit a partially migrated component.

## Documentation Updates

After each component migration:

1. Update component README if exists
2. Add migration notes to sprint status
3. Document any component-specific quirks
4. Update the master component list

## Success Metrics

- **Zero JavaScript Errors**: Console remains clean
- **Instant Navigation**: <16ms tab switches
- **100% Feature Parity**: No lost functionality
- **Consistent Experience**: Same patterns everywhere
- **Working Chat**: Both chat types functional

## Next Steps

After all components are migrated:

1. Run full integration test suite
2. Update main documentation
3. Create developer guide for pattern
4. Plan Phase 2 improvements (animations, etc.)