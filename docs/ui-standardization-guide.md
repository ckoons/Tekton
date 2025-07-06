# Tekton UI Standardization Guide

This guide outlines the UI standards for all Tekton components to ensure consistent chat interfaces across the platform.

## Component Color Scheme

| Component | Primary Color | Hex Code | RGB Values |
|-----------|--------------|----------|------------|
| Rhetor    | Red          | #D32F2F  | 211, 47, 47 |
| Terma     | Brown        | #5D4037  | 93, 64, 55 |
| Noesis    | Orange       | #FF6F00  | 255, 111, 0 |
| Numa      | Purple       | #9C27B0  | 156, 39, 176 |

## UI Standards

### 1. Chat Message Styling

All chat messages should use a consistent left-border accent pattern:

```css
/* User messages - always green */
.component__chat-message--user {
    background-color: rgba(76, 175, 80, 0.1);
    border-left: 3px solid #4CAF50;
    padding: 8px 12px;
    margin: 4px 0;
}

/* AI messages - component color */
.component__chat-message--ai {
    background-color: rgba(COMPONENT_RGB, 0.1);
    border-left: 3px solid COMPONENT_COLOR;
    padding: 8px 12px;
    margin: 4px 0;
}

/* System messages - component color */
.component__chat-message--system {
    background-color: rgba(COMPONENT_RGB, 0.05);
    border-left: 3px solid COMPONENT_COLOR;
    padding: 8px 12px;
    margin: 4px 0;
    font-style: italic;
}
```

### 2. Chat Sender Labels

Sender labels should use partial color on the left:

```css
.component__chat-sender {
    color: COMPONENT_COLOR;
    font-weight: 600;
    margin-right: 8px;
}

/* User sender is always green */
.component__chat-sender--user {
    color: #4CAF50;
}
```

### 3. AI Status Indicator

All components must have a luminous status indicator in the chat header:

```html
<div class="component__chat-header">
    <h3>AI Companion Chat</h3>
    <span class="component__ai-status" data-ai-status="inactive">●</span>
</div>
```

```css
.component__ai-status {
    font-size: 14px;
    transition: all 0.3s ease;
}

.component__ai-status[data-ai-status="active"] {
    color: #28a745;
    text-shadow: 0 0 8px #28a745;
    animation: pulse-glow 2s infinite;
}

.component__ai-status[data-ai-status="inactive"] {
    color: #6c757d;
    opacity: 0.5;
}

@keyframes pulse-glow {
    0%, 100% {
        text-shadow: 0 0 8px #28a745, 
                     0 0 12px #28a745,
                     0 0 16px rgba(40, 167, 69, 0.6);
    }
    50% {
        text-shadow: 0 0 10px #28a745, 
                     0 0 15px #28a745,
                     0 0 20px rgba(40, 167, 69, 0.8);
    }
}
```

### 4. Chat Input Area

The chat input area should match the component's theme:

```css
.component__chat-input-container {
    border-top: 2px solid rgba(COMPONENT_RGB, 0.2);
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.component__chat-prompt {
    color: COMPONENT_COLOR;
    font-weight: bold;
    margin-right: 8px;
}

.component__chat-input {
    flex: 1;
    border: 1px solid rgba(COMPONENT_RGB, 0.3);
    border-radius: 4px;
    padding: 8px 12px;
}

.component__chat-input:focus {
    outline: none;
    border-color: COMPONENT_COLOR;
    box-shadow: 0 0 0 2px rgba(COMPONENT_RGB, 0.1);
}

.component__chat-send {
    background-color: COMPONENT_COLOR;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.component__chat-send:hover {
    background-color: rgba(COMPONENT_RGB, 0.8);
    transform: translateY(-1px);
}
```

## Implementation Status

### Current Status by Component:

| Feature | Numa | Noesis | Rhetor | Terma |
|---------|------|--------|--------|-------|
| Left-border message styling | ✓ | ✓ | ✗ | ✓ |
| Luminous AI status indicator | ✗ | ✓ | ✗ | ✗ |
| Correct prompt color | ✓ | ✓ | ✗ | ✓ |
| Component-themed chat area | ✓ | ✓ | ✗ | ✓ |

### Required Updates:

#### Rhetor (Priority: High)
1. Change chat prompt color from green (#4CAF50) to red (#D32F2F)
2. Update message styling to use left-border accent pattern
3. Add AI status indicator to chat headers
4. Update send button and input focus colors to red theme

#### Numa (Priority: Medium)
1. Add luminous glow effect to AI status indicator
2. Ensure consistent animation timing

#### Terma (Priority: Medium)
1. Add AI status indicator to chat headers
2. Implement luminous glow effect

#### Noesis (Priority: Low)
- Already implements all standards correctly
- Can be used as reference implementation

## Example Implementation

Here's a complete example for a standardized chat message:

```html
<div class="component__chat-message component__chat-message--ai">
    <span class="component__chat-sender">Apollo AI:</span>
    <span class="component__chat-text">I'm analyzing your request...</span>
</div>
```

With corresponding CSS:

```css
/* For Apollo (example) with primary color #1976D2 */
.apollo__chat-message--ai {
    background-color: rgba(25, 118, 210, 0.1);
    border-left: 3px solid #1976D2;
    padding: 8px 12px;
    margin: 4px 0;
}

.apollo__chat-sender {
    color: #1976D2;
    font-weight: 600;
    margin-right: 8px;
}
```

## Testing Checklist

When implementing these standards, verify:

- [ ] User messages have green left border
- [ ] AI messages have component-colored left border
- [ ] System messages use lighter component color
- [ ] Chat prompt '>' matches component color
- [ ] Send button uses component color
- [ ] Input focus state shows component color
- [ ] AI status indicator shows luminous glow when active
- [ ] All animations are smooth and consistent
- [ ] Colors match the official component palette

## Migration Guide

To update an existing component:

1. **Update CSS classes** to match the standardized naming
2. **Add status indicator** to chat headers if missing
3. **Replace full backgrounds** with left-border accents
4. **Update color variables** to match official palette
5. **Test all states** (active, inactive, hover, focus)
6. **Verify animations** work smoothly

## Reference Implementation

See `/Hephaestus/ui/components/noesis/noesis-component.html` for a complete reference implementation that follows all standards.