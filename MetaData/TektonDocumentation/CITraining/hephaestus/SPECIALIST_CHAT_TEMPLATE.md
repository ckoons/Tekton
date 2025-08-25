# Specialist Chat Template - Building AI Chat Components

## Overview

This document provides the template and guidelines for creating specialist chat interfaces in Tekton's Hephaestus UI. Each AI specialist (CI - Companion Intelligence) should have a consistent chat interface following this pattern.

## Core Features

Every specialist chat component includes:

1. **CI Status Indicator** - Shows connection status with luminous glow
2. **Discovery/Specialist Chat** - Component-specific AI interaction
3. **Team Chat** - Cross-component AI communication
4. **Message Persistence** - Retains conversation during tab switches
5. **User Profile Integration** - Shows user's name from profile
6. **Styled Messages** - Consistent visual design with colored borders

## Implementation Template

### 1. HTML Structure

```html
<!-- Component Header -->
<div class="component__header" data-tekton-zone="header">
    <div class="component__title-container">
        <img src="/images/hexagon.jpg" alt="Tekton" class="component__icon">
        <h2 class="component__title">
            <span class="component__title-main">ComponentName</span>
            <span class="component__title-sub">Component Purpose</span>
        </h2>
    </div>
    <div class="component__connection-status">
        <span class="component__status-indicator" data-status="inactive"></span>
        <span class="component__status-text">CI Connecting...</span>
    </div>
</div>

<!-- Tab Controls -->
<input type="radio" name="component-tab" id="component-tab-specialist" checked style="display: none;">
<input type="radio" name="component-tab" id="component-tab-team" style="display: none;">

<!-- Chat Tabs -->
<div class="component__tabs">
    <label for="component-tab-specialist" class="component__tab">
        <span class="component__tab-label">Specialist Chat</span>
    </label>
    <label for="component-tab-team" class="component__tab">
        <span class="component__tab-label">Team Chat</span>
    </label>
</div>

<!-- Chat Areas -->
<div class="chat-messages" id="component-specialist-messages"></div>
<div class="chat-messages" id="component-team-messages"></div>

<!-- Shared Input Footer -->
<div class="component__footer">
    <div class="component__chat-input-container">
        <div class="component__chat-prompt">></div>
        <input type="text" class="component__chat-input" id="component-chat-input"
               placeholder="Ask ComponentName about...">
        <button class="component__send-button" onclick="component_sendChat()">Send</button>
    </div>
</div>
```

### 2. Essential CSS Styles

```css
/* Message styling with colored borders */
.chat-message {
    margin-bottom: 12px;
    padding: 12px;
    border-radius: 8px;
    background-color: var(--bg-secondary, #252535);
}

.chat-message.user-message {
    background-color: rgba(76, 175, 80, 0.1);
    border-left: 3px solid #4CAF50;
    margin-left: 32px;
}

.chat-message.ai-message {
    background-color: rgba(33, 150, 243, 0.1);
    border-left: 3px solid #2196F3;
}

.chat-message.system-message {
    background-color: rgba(255, 111, 0, 0.1);
    border-left: 3px solid #FF6F00;
}

/* CI Status Indicator with glow */
.component__status-indicator[data-status="active"] {
    background-color: #28a745;
    box-shadow: 0 0 8px #28a745, 
                0 0 12px #28a745,
                0 0 16px rgba(40, 167, 69, 0.6);
    animation: pulse-glow 2s infinite;
}
```

### 3. Core JavaScript Functions

```javascript
// Message persistence storage
window.componentChats = window.componentChats || {
    specialist: [],
    team: []
};

// Send chat message
function component_sendChat() {
    const isSpecialistTab = document.getElementById('component-tab-specialist').checked;
    if (isSpecialistTab) {
        component_sendSpecialistMessage();
    } else {
        component_sendTeamMessage();
    }
}

// Send to specialist AI
function component_sendSpecialistMessage() {
    const input = document.getElementById('component-chat-input');
    const message = input.value.trim();
    if (!message) return;
    
    // Add user message
    component_addChatMessage('specialist', message, 'user');
    input.value = '';
    
    // Add typing indicator
    const typingId = 'typing-' + Date.now();
    component_addChatMessage('specialist', '...', 'typing', typingId);
    
    // Send via AIChat module
    if (window.AIChat) {
        window.AIChat.sendMessage('component-ai', message)
            .then(response => {
                component_removeTypingIndicator(typingId);
                const parts = window.AIChat.parseResponse(response);
                parts.forEach(part => {
                    if (part.type === 'text' && part.content.trim()) {
                        component_addChatMessage('specialist', part.content, 'ai');
                    }
                });
            })
            .catch(error => {
                component_removeTypingIndicator(typingId);
                component_addChatMessage('specialist', 
                    `Failed to connect to CI. Error: ${error.message}`, 
                    'system');
            });
    }
}

// Add message with persistence
function component_addChatMessage(chatType, message, messageClass, id = null) {
    const container = document.getElementById(`component-${chatType}-messages`);
    if (!container) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${messageClass}-message`;
    if (id) messageDiv.id = id;
    
    // Get user name from profile
    let label = '';
    if (messageClass === 'user') {
        label = window.profileManager?.profile?.givenName || 'User';
    } else if (messageClass === 'ai') {
        label = 'ComponentName';
    } else if (messageClass === 'system') {
        label = 'System';
    }
    
    messageDiv.innerHTML = `<strong>${label}:</strong> ${message}`;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
    
    // Store message (except typing indicators)
    if (messageClass !== 'typing' && !id) {
        window.componentChats[chatType].push({
            message: message,
            messageClass: messageClass,
            label: label,
            timestamp: Date.now()
        });
    }
}

// CI health check
fetch('http://localhost:PORT/health')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'healthy') {
            document.querySelector('.component__status-indicator').setAttribute('data-status', 'active');
            document.querySelector('.component__status-text').textContent = 'CI Connected';
        }
    })
    .catch(error => {
        document.querySelector('.component__status-indicator').setAttribute('data-status', 'error');
        document.querySelector('.component__status-text').textContent = 'CI Disconnected';
    });
```

### 4. Component-Specific Customization

For each component, customize:

1. **Colors**: Each component has its own color in the navigation (match in styles)
2. **AI Name**: Use the correct AI specialist name (e.g., 'apollo-ai', 'athena-ai')
3. **Port**: Each component has a specific port for health checks
4. **Placeholder Text**: Make it specific to the component's purpose
5. **Welcome Message**: Initial message should explain the CI's capabilities

### 5. Integration Checklist

- [ ] Include `/scripts/shared/ai-chat.js` in index.html
- [ ] Add component styles to index.html or component CSS
- [ ] Set correct AI name for `AIChat.sendMessage()`
- [ ] Update health check port
- [ ] Test CI connection status indicator
- [ ] Verify message persistence across tab switches
- [ ] Check profile name integration
- [ ] Ensure message styling with borders

## Example Components

- **Noesis**: Discovery and insights (port 8015)
- **Apollo**: Code analysis and prediction (port 8007)
- **Athena**: Knowledge management (port 8017)
- **Sophia**: Learning and adaptation (port 8016)

## Best Practices

1. **Consistent Naming**: Use BEM notation (component__element--modifier)
2. **Semantic HTML**: Use data-tekton-* attributes for meaning
3. **Error Handling**: Always provide fallback messages
4. **Performance**: Clear containers before restoring to prevent duplicates
5. **Accessibility**: Include proper labels and status indicators

---

*Created by Jill on July 5, 2025 during the Noesis sprint with Casey*