# Hephaestus Chat UI Fix - Handoff Document

## Status: Apollo Fixed, 11 Components + Rhetor CSS Remaining

### What's Been Done
1. **Analysis Complete** - See `Hephaestus_Chat_UI_Analysis.md` for full details
2. **Apollo Fixed** - First component successfully updated with Numa pattern

### Apollo Implementation Pattern (USE THIS FOR ALL REMAINING COMPONENTS)

#### 1. Fix HTML Input/Button (in footer section):
```html
<!-- OLD (broken) -->
<input type="text" id="chat-input" class="component__chat-input" 
       placeholder="...">
<button id="send-button" class="component__send-button">Send</button>

<!-- NEW (working) -->
<input type="text" id="component-chat-input" class="component__chat-input" 
       data-tekton-input="chat-input"
       data-tekton-input-type="chat"
       placeholder="..."
       onkeydown="if(event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); component_sendChat(); }">
<button id="component-send-button" class="component__send-button" onclick="component_sendChat(); return false;"
        data-tekton-action="send-message" 
        data-tekton-action-type="primary">Send</button>
```

#### 2. Add JavaScript Function (before closing </script> tag):
```javascript
// Chat functionality - Following Numa's pattern
function component_sendChat() {
    const input = document.getElementById('component-chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Determine which tab is active (adjust based on component's tabs)
    const mainChatActive = document.querySelector('.component__tab[data-tab="main-chat-name"]').classList.contains('component__tab--active');
    const chatType = mainChatActive ? 'main-chat-id' : 'teamchat';
    const messagesContainer = document.getElementById(`${chatType}-messages`);
    
    // Add user message
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'component__message component__message--user';
    userMessageDiv.innerHTML = `<div class="component__message-content"><div class="component__message-text"><strong>You:</strong> ${message}</div></div>`;
    messagesContainer.appendChild(userMessageDiv);
    
    // Clear input
    input.value = '';
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Send to backend
    if (chatType === 'main-chat-id') {
        // Direct message to component-ai
        if (window.AIChat) {
            window.AIChat.sendMessage('component-ai', message)
                .then(response => {
                    const aiMessageDiv = document.createElement('div');
                    aiMessageDiv.className = 'component__message component__message--ai';
                    aiMessageDiv.innerHTML = `<div class="component__message-content"><div class="component__message-text"><strong>Component:</strong> ${response.content}</div></div>`;
                    messagesContainer.appendChild(aiMessageDiv);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                })
                .catch(err => {
                    console.error('Failed to send message:', err);
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'component__message component__message--system';
                    errorDiv.innerHTML = `<div class="component__message-content"><div class="component__message-text"><strong>System:</strong> Failed to connect to Component AI</div></div>`;
                    messagesContainer.appendChild(errorDiv);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                });
        }
    } else {
        // Team chat
        if (window.AIChat) {
            window.AIChat.teamChat(message, 'component')
                .then(data => {
                    // Display team responses
                    if (data.responses && data.responses.length > 0) {
                        data.responses.forEach(resp => {
                            const aiMessageDiv = document.createElement('div');
                            aiMessageDiv.className = 'component__message component__message--ai';
                            const sender = resp.socket_id.replace('-ai', '').charAt(0).toUpperCase() + 
                                         resp.socket_id.replace('-ai', '').slice(1);
                            aiMessageDiv.innerHTML = `<div class="component__message-content"><div class="component__message-text"><strong>${sender}:</strong> ${resp.content}</div></div>`;
                            messagesContainer.appendChild(aiMessageDiv);
                        });
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    }
                })
                .catch(err => {
                    console.error('Failed to send team message:', err);
                });
        }
    }
}
```

### Remaining Components to Fix (in order):

1. **Athena** (`/Hephaestus/ui/components/athena/athena-component.html`)
   - Main chat tab: "chat" → Knowledge Chat
   - Chat container IDs: "chat-messages", "teamchat-messages"
   - AI name: "athena-ai"

2. **Budget** (`/Hephaestus/ui/components/budget/budget-component.html`)
   - Main chat tab: "budget-chat" → Budget Chat
   - Chat container IDs: "budget-chat-messages", "team-chat-messages"
   - AI name: "budget-ai"

3. **Engram** (`/Hephaestus/ui/components/engram/engram-component.html`)
   - Main chat tab: "memory" → Memory Chat
   - Chat container IDs: "memory-messages", "teamchat-messages"
   - AI name: "engram-ai"

4. **Ergon** (`/Hephaestus/ui/components/ergon/ergon-component.html`)
   - Main chat tab: "tool-chat" → Tool Chat
   - Chat container IDs: "tool-chat-messages", "team-chat-messages"
   - AI name: "ergon-ai"

5. **Harmonia** (`/Hephaestus/ui/components/harmonia/harmonia-component.html`)
   - Main chat tab: "workflow-chat" → Workflow Chat
   - Chat container IDs: "workflow-chat-messages", "team-chat-messages"
   - AI name: "harmonia-ai"

6. **Hermes** (`/Hephaestus/ui/components/hermes/hermes-component.html`)
   - Main chat tab: "message-chat" → Message/Data Chat
   - Chat container IDs: "message-chat-messages", "team-chat-messages"
   - AI name: "hermes-ai"

7. **Metis** (`/Hephaestus/ui/components/metis/metis-component.html`)
   - Main chat tab: "workflow-chat" → Workflow Chat
   - Chat container IDs: "workflow-chat-messages", "team-chat-messages"
   - AI name: "metis-ai"

8. **Prometheus** (`/Hephaestus/ui/components/prometheus/prometheus-component.html`)
   - Main chat tab: "planning-chat" → Planning Chat
   - Chat container IDs: "planning-chat-messages", "team-chat-messages"
   - AI name: "prometheus-ai"

9. **Sophia** (`/Hephaestus/ui/components/sophia/sophia-component.html`)
   - Main chat tab: "research-chat" → Research Chat
   - Chat container IDs: "research-chat-messages", "team-chat-messages"
   - AI name: "sophia-ai"

10. **Synthesis** (`/Hephaestus/ui/components/synthesis/synthesis-component.html`)
    - Main chat tab: "execution-chat" → Execution Chat
    - Chat container IDs: "execution-chat-messages", "team-chat-messages"
    - AI name: "synthesis-ai"

11. **Telos** (`/Hephaestus/ui/components/telos/telos-component.html`)
    - Main chat tab: "requirements-chat" → Requirements Chat
    - Chat container IDs: "requirements-chat-messages", "team-chat-messages"
    - AI name: "telos-ai"

### Final Fix: Rhetor CSS
In `/Hephaestus/ui/components/rhetor/rhetor-component.html`, find line 2339:
```css
.rhetor__message--user {
    align-self: flex-start;  /* CHANGE THIS TO: flex-end */
}
```

### Testing
After each component:
1. Open Hephaestus UI
2. Navigate to the component
3. Try sending a chat message
4. Verify user messages appear on the right
5. Verify Enter key works
6. Verify Send button works

### Notes
- All components use the same pattern, just replace "component" with actual component name
- Be careful with the chat tab detection logic - each component has different tab names
- The AI name follows pattern: "{component}-ai" (lowercase)