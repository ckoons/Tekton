# Hermes CSS-First Implementation Guide

## Overview
This guide details the conversion of Hermes component from JavaScript onclick handlers to pure CSS interactions, following the pattern established in Apollo and Athena renovations.

## Tab System Conversion

### Current Structure (JavaScript-based)
```html
<div class="hermes__tab" onclick="hermes_switchTab('registry');">
    <span class="hermes__tab-label">Service Registry</span>
</div>
```

### New Structure (CSS-first)
```html
<!-- Hidden radio inputs for tab state -->
<input type="radio" name="hermes-tabs" id="hermes-tab-registry" class="hermes__tab-input" checked>
<input type="radio" name="hermes-tabs" id="hermes-tab-messaging" class="hermes__tab-input">
<input type="radio" name="hermes-tabs" id="hermes-tab-connections" class="hermes__tab-input">
<input type="radio" name="hermes-tabs" id="hermes-tab-history" class="hermes__tab-input">
<input type="radio" name="hermes-tabs" id="hermes-tab-chat" class="hermes__tab-input">
<input type="radio" name="hermes-tabs" id="hermes-tab-teamchat" class="hermes__tab-input">

<!-- Tab labels (clickable) -->
<div class="hermes__tabs">
    <label for="hermes-tab-registry" class="hermes__tab" data-tab="registry">
        <span class="hermes__tab-label">Service Registry</span>
    </label>
    <!-- ... other tabs ... -->
</div>
```

### CSS Rules for Tab Switching
```css
/* Hide radio inputs */
.hermes__tab-input {
    display: none;
}

/* Style inactive tabs */
.hermes__tab {
    cursor: pointer;
    /* existing styles */
}

/* Active tab styling */
#hermes-tab-registry:checked ~ .hermes__menu-bar .hermes__tab[data-tab="registry"],
#hermes-tab-messaging:checked ~ .hermes__menu-bar .hermes__tab[data-tab="messaging"],
/* ... other tabs ... */ {
    border-bottom-color: var(--color-primary, #4285F4);
    font-weight: 500;
}

/* Panel visibility */
.hermes__panel {
    display: none;
}

#hermes-tab-registry:checked ~ .hermes__content #registry-panel,
#hermes-tab-messaging:checked ~ .hermes__content #messaging-panel,
/* ... other panels ... */ {
    display: block;
}
```

## Button Conversions

### Clear Button
```html
<!-- Old -->
<button onclick="hermes_clearChat();">Clear</button>

<!-- New - Use form submission or CSS-only if possible -->
<form class="hermes__clear-form" action="#" onsubmit="return false;">
    <button type="submit" class="hermes__action-button">Clear</button>
</form>
```

### View Toggle (Grid/List)
```html
<!-- Use radio buttons for view state -->
<input type="radio" name="hermes-view" id="hermes-view-grid" class="hermes__view-input" checked>
<input type="radio" name="hermes-view" id="hermes-view-list" class="hermes__view-input">

<div class="hermes__view-controls">
    <label for="hermes-view-grid" class="hermes__view-button">⊞</label>
    <label for="hermes-view-list" class="hermes__view-button">≡</label>
</div>
```

## Special Considerations

### 1. Chat Input Handling
The chat functionality requires JavaScript for sending messages. Keep the JavaScript but remove inline handlers:
```javascript
// Add event listeners in external script
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('hermes-chat-input');
    const sendButton = document.getElementById('hermes-send-button');
    
    if (sendButton) {
        sendButton.addEventListener('click', hermes_sendChat);
    }
    
    if (chatInput) {
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                hermes_sendChat();
            }
        });
    }
});
```

### 2. Clear Button Visibility
Control clear button visibility with CSS based on active tab:
```css
/* Hide by default */
.hermes__action-button[data-action="clear-chat"] {
    display: none;
}

/* Show for chat tabs */
#hermes-tab-chat:checked ~ .hermes__menu-bar .hermes__action-button[data-action="clear-chat"],
#hermes-tab-teamchat:checked ~ .hermes__menu-bar .hermes__action-button[data-action="clear-chat"] {
    display: block;
}
```

### 3. Modal Handling
Keep modal functionality but use CSS for show/hide:
```css
/* Modal hidden by default */
.hermes__modal {
    display: none;
}

/* Show modal with checkbox trick */
#hermes-modal-toggle:checked ~ .hermes__modal {
    display: flex;
}
```

## Implementation Steps

1. **Add Radio Inputs**: Place at the beginning of the component
2. **Convert Tabs to Labels**: Change divs to labels with `for` attributes
3. **Update CSS**: Add rules for :checked states
4. **Remove onclick Handlers**: Delete all inline JavaScript
5. **Update Panel Visibility**: Use CSS sibling selectors
6. **Test Each Tab**: Ensure switching works correctly
7. **Handle Special Cases**: Chat, modals, filters
8. **Clean Up JavaScript**: Remove unused functions

## Testing Checklist

- [ ] All tabs switch correctly without JavaScript
- [ ] Active tab styling updates properly
- [ ] Panels show/hide based on selected tab
- [ ] Clear button appears only on chat tabs
- [ ] Grid/List view toggle works
- [ ] Chat functionality still sends messages
- [ ] Modals can open and close
- [ ] No console errors
- [ ] Accessibility maintained (keyboard navigation)
- [ ] Data attributes preserved for Hephaestus

## Benefits
1. **Performance**: No JavaScript execution for basic UI
2. **Reliability**: Less code to break
3. **Maintainability**: CSS is simpler than JavaScript
4. **Accessibility**: Better keyboard support
5. **Consistency**: Matches Apollo/Athena pattern