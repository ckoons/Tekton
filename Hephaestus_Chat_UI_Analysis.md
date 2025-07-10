# Hephaestus Chat UI Analysis
## Comparing All Components to Numa Pattern

### Reference Implementation: Numa (WORKING)
- **Structure**: Radio button tabs, chat panels with messages div, footer with input
- **User Message Positioning**: 
  - CSS class: `.chat-message.user-message`
  - Positioning: `margin-left: 0;` (pushes to right)
  - Background: `rgba(76, 175, 80, 0.05)` with green border
- **AI Message Positioning**:
  - CSS class: `.chat-message.ai-message`  
  - Positioning: `margin-right: 0;` (stays on left)
  - Background: `rgba(156, 39, 176, 0.05)` with purple border
- **Chat Input**: In footer with prompt symbol `>`
- **JavaScript**: Uses `window.AIChat` module for communication

### Components Analysis

#### Summary Table

| Component | Has Chat | User Message Class | User Positioning | Status |
|-----------|----------|-------------------|------------------|---------|
| **Rhetor** | ✓ LLM Chat, Team Chat | `.rhetor__message--user` | `align-self: flex-start` ❌ | **NEEDS FIX** |
| **Apollo** | ✓ Attention Chat, Team Chat | `.apollo__message--user` | `align-self: flex-end` ✓ | OK |
| **Athena** | ✓ Knowledge Chat, Team Chat | `.athena__message--user` | `align-self: flex-end` ✓ | OK |
| **Budget** | ✓ Budget Chat, Team Chat | `.budget__message--user` | `align-self: flex-end` ✓ | OK |
| **Engram** | ✓ Memory Chat, Team Chat | `.engram__message--user` | `align-self: flex-end` ✓ | OK |
| **Ergon** | ✓ Tool Chat, Team Chat | `.ergon__message--user` | `align-self: flex-end` ✓ | OK |
| **Harmonia** | ✓ Workflow Chat, Team Chat | `.harmonia__message--user` | `justify-content: flex-end` (parent) ✓ | OK (different pattern) |
| **Hermes** | ✓ Message Chat, Team Chat | `.hermes__message--user` | `align-self: flex-end` ✓ | OK |
| **Metis** | ✓ Workflow Chat, Team Chat | `.metis__message--user` | `align-self: flex-end` ✓ | OK |
| **Prometheus** | ✓ Planning Chat, Team Chat | `.prometheus__message--user` | `align-self: flex-end` ✓ | OK |
| **Sophia** | ✓ Research Chat, Team Chat | `.sophia__message--user` | `align-self: flex-end` ✓ | OK |
| **Synthesis** | ✓ Execution Chat, Team Chat | `.synthesis__message--user` | `align-self: flex-end` ✓ | OK |
| **Telos** | ✓ Requirements Chat, Team Chat | `.telos__message--user` | `align-self: flex-end` ✓ | OK |

### Critical Findings

#### 1. Rhetor User Message Position Fix Needed
**Issue (Line 2339)**: 
```css
.rhetor__message--user {
    align-self: flex-start;  /* WRONG - aligns to left */
}
```
Should be:
```css
.rhetor__message--user {
    align-self: flex-end;  /* Correct - aligns to right */
}
```

#### 2. Missing Chat Functionality in 12 Components

**Working Components (have proper chat implementation):**
- ✅ Numa (reference implementation)  
- ✅ Noesis
- ✅ Terma
- ✅ Rhetor (only needs CSS fix above)

**Broken Components (missing chat event handlers and functions):**
All these components have chat UI elements but NO functional implementation:
- ❌ Apollo - missing onkeydown, onclick, apollo_sendChat()
- ❌ Athena - missing onkeydown, onclick, athena_sendChat()
- ❌ Budget - missing onkeydown, onclick, budget_sendChat()
- ❌ Engram - missing onkeydown, onclick, engram_sendChat()
- ❌ Ergon - missing onkeydown, onclick, ergon_sendChat()
- ❌ Harmonia - missing onkeydown, onclick, harmonia_sendChat()
- ❌ Hermes - missing onkeydown, onclick, hermes_sendChat()
- ❌ Metis - missing onkeydown, onclick, metis_sendChat()
- ❌ Prometheus - missing onkeydown, onclick, prometheus_sendChat()
- ❌ Sophia - missing onkeydown, onclick, sophia_sendChat()
- ❌ Synthesis - missing onkeydown, onclick, synthesis_sendChat()
- ❌ Telos - missing onkeydown, onclick, telos_sendChat()

### Required Pattern from Numa:

#### HTML (chat input and button):
```html
<input type="text" class="component__chat-input" id="component-chat-input"
       data-tekton-input="chat-input"
       data-tekton-input-type="chat"
       placeholder="Chat with Component"
       onkeydown="if(event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); component_sendChat(); }">
<button class="component__send-button" id="component-send-button" 
        onclick="component_sendChat(); return false;"
        data-tekton-action="send-message"
        data-tekton-action-type="primary">Send</button>
```

#### JavaScript (chat function):
```javascript
function component_sendChat() {
    const input = document.getElementById('component-chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Determine which tab is active
    const isMainChatActive = document.getElementById('component-tab-main').checked;
    const chatType = isMainChatActive ? 'main' : 'team';
    const messagesContainer = document.getElementById(`component-${chatType}-messages`);
    
    // Add user message
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'chat-message user-message';
    userMessageDiv.innerHTML = `<strong>You:</strong> ${message}`;
    messagesContainer.appendChild(userMessageDiv);
    
    // Clear input
    input.value = '';
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Send to backend using AIChat
    if (window.AIChat) {
        window.AIChat.sendMessage('component-ai', message)
            .then(response => {
                // Add AI response
            })
            .catch(error => {
                // Handle error
            });
    }
}
```

### Summary of Required Changes

#### For Rhetor (1 component):
1. Fix CSS: Change `align-self: flex-start` to `align-self: flex-end` on line 2339

#### For 12 Broken Components (Apollo, Athena, Budget, Engram, Ergon, Harmonia, Hermes, Metis, Prometheus, Sophia, Synthesis, Telos):
1. Add `onkeydown` handler to chat input
2. Add `onclick` handler to send button  
3. Add JavaScript `component_sendChat()` function
4. Ensure proper integration with `window.AIChat` module

### Implementation Approach
1. Start with one component (e.g., Apollo) as a test case
2. Apply the Numa pattern exactly
3. Test functionality
4. If successful, apply same pattern to remaining 11 components
5. Finally, fix Rhetor's CSS issue

### Key Patterns to Match from Numa:
1. HTML structure with radio buttons for tabs
2. Chat messages container with proper flex layout
3. Message classes following pattern: `{component}__message {component}__message--user/ai/system`
4. User messages right-aligned, AI messages left-aligned
5. Footer with chat input using prompt symbol
6. Integration with `window.AIChat` module
7. Proper event handlers and JavaScript functions