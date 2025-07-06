# Tekton AI Chat Setup Guide

This guide explains how to set up specialist chat and team chat functionality for Tekton components.

## Overview

Tekton provides two types of AI chat interfaces:
- **Specialist Chat**: Direct communication with a single AI specialist (e.g., `aish apollo "message"`)
- **Team Chat**: Broadcast messages to multiple AI specialists through Rhetor (e.g., `aish team-chat "message"`)

## Architecture

### Port Configuration
Each component has a fixed port mapping:
- Component Port: Base port (e.g., Apollo: 8010)
- AI Port: `(component_port - 8000) + 45000` (e.g., Apollo AI: 45010)

### Communication Flow
```
UI Component → AIChat.js → Rhetor API → AI Specialist
                    ↓
             Team Chat → All AI Specialists
```

## Implementation Guide

### 1. Adding Chat to a New Component

#### Step 1: HTML Structure
Add chat panels to your component HTML:

```html
<!-- Specialist Chat Tab -->
<div class="component__panel component__panel--companion" data-tab-content="companion-chat">
    <div class="component__chat-container">
        <div class="component__chat-header">
            <h3>AI Companion Chat</h3>
            <span class="component__ai-status" data-ai-status="inactive">●</span>
        </div>
        <div class="component__chat-messages" id="component-companion-messages"></div>
        <div class="component__chat-input-container">
            <input type="text" class="component__chat-input" id="component-companion-input" 
                   placeholder="Ask your AI companion...">
            <button class="component__chat-send" id="component-companion-send">Send</button>
        </div>
    </div>
</div>

<!-- Team Chat Tab -->
<div class="component__panel component__panel--team" data-tab-content="team-chat">
    <div class="component__chat-container">
        <div class="component__chat-header">
            <h3>Team Chat</h3>
            <span class="component__ai-status" data-ai-status="inactive">●</span>
        </div>
        <div class="component__chat-messages" id="component-team-messages"></div>
        <div class="component__chat-input-container">
            <input type="text" class="component__chat-input" id="component-team-input" 
                   placeholder="Message all AI specialists...">
            <button class="component__chat-send" id="component-team-send">Send</button>
        </div>
    </div>
</div>
```

#### Step 2: JavaScript Integration
Use the shared AIChat functions in your component's JavaScript:

```javascript
// Initialize chat functionality
initChat: function() {
    // Get chat elements
    const companionInput = document.getElementById('component-companion-input');
    const companionSend = document.getElementById('component-companion-send');
    const teamInput = document.getElementById('component-team-input');
    const teamSend = document.getElementById('component-team-send');
    
    // Specialist chat handler
    const handleCompanionChat = async () => {
        const message = companionInput.value.trim();
        if (!message) return;
        
        // Display user message
        this.displayMessage('companion', 'User', message);
        companionInput.value = '';
        
        try {
            // Send to specific AI (e.g., apollo-ai)
            if (window.AIChat) {
                const response = await window.AIChat.sendMessage('component-ai', message);
                this.displayMessage('companion', 'Component AI', response.content);
            }
        } catch (error) {
            this.displayMessage('companion', 'System', `Error: ${error.message}`);
        }
    };
    
    // Team chat handler
    const handleTeamChat = async () => {
        const message = teamInput.value.trim();
        if (!message) return;
        
        // Display user message
        this.displayMessage('team', 'User', message);
        teamInput.value = '';
        
        try {
            // Send to all AI specialists
            if (window.AIChat) {
                const responses = await window.AIChat.teamChat(message, 'component');
                
                // Display all responses
                for (const response of responses) {
                    this.displayMessage('team', response.source, response.content);
                }
            }
        } catch (error) {
            this.displayMessage('team', 'System', `Error: ${error.message}`);
        }
    };
    
    // Add event listeners
    companionSend.addEventListener('click', handleCompanionChat);
    companionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleCompanionChat();
    });
    
    teamSend.addEventListener('click', handleTeamChat);
    teamInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleTeamChat();
    });
}
```

#### Step 3: Message Display Function
Add a function to display chat messages:

```javascript
displayMessage: function(chatType, sender, message) {
    const messagesContainer = document.getElementById(
        chatType === 'companion' ? 'component-companion-messages' : 'component-team-messages'
    );
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'component__chat-message';
    
    const senderSpan = document.createElement('span');
    senderSpan.className = 'component__chat-sender';
    senderSpan.textContent = sender + ':';
    
    const messageSpan = document.createElement('span');
    messageSpan.className = 'component__chat-text';
    messageSpan.textContent = message;
    
    messageDiv.appendChild(senderSpan);
    messageDiv.appendChild(messageSpan);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
```

### 2. Backend Integration

#### For Component APIs
Add chat endpoints to your component's FastAPI app:

```python
from shared.ai.simple_ai import ai_send

@router.post("/api/companion-chat")
async def companion_chat(request: ChatRequest):
    """Handle companion chat requests."""
    try:
        # Calculate AI port
        ai_port = (COMPONENT_PORT - 8000) + 45000
        
        # Send to component's AI
        ai_response = await ai_send(
            f"{COMPONENT_NAME}-ai", 
            request.message, 
            "localhost", 
            ai_port
        )
        
        return {
            "response": ai_response,
            "source": f"{COMPONENT_NAME}-ai"
        }
    except Exception as e:
        logger.error(f"Companion chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Using the AIChat Functions

The shared `ai-chat.js` module provides two main functions:

#### Specialist Chat
```javascript
// Send a message to a specific AI
const response = await window.AIChat.sendMessage('apollo-ai', 'What is your status?');
console.log(response.content);  // AI's response
```

#### Team Chat
```javascript
// Broadcast to all AI specialists
const responses = await window.AIChat.teamChat(
    'Team meeting at 3pm', 
    'ui',           // from_component
    []              // target_sockets (empty = all)
);

// Process multiple responses
responses.forEach(response => {
    console.log(`${response.source}: ${response.content}`);
});
```

### 4. Command Line Usage

#### Specialist Chat (Direct)
```bash
# Send message to specific AI
aish apollo "What is your current status?"

# Send to any specialist
aish numa-ai "Help me understand the platform"
```

#### Team Chat (Broadcast)
```bash
# Send to all AI specialists
aish team-chat "Good morning team!"

# The command routes through Rhetor's team chat endpoint
```

### 5. Current Component Status

| Component | Specialist Chat | Team Chat | AI Port |
|-----------|----------------|-----------|---------|
| Apollo    | ✓ Implemented  | ✓ Via UI  | 45010   |
| Numa      | ✓ Implemented  | ✓ Via UI  | 45016   |
| Noesis    | ✓ Implemented  | ✓ Via UI  | 45015   |
| Rhetor    | ✓ Implemented  | ✓ Native  | 45003   |
| Terma     | ✓ Implemented  | ✓ Via UI  | 45020   |

### 6. Troubleshooting

#### AI Not Responding
1. Check if AI is running: `tekton-status`
2. Verify port calculation: `(component_port - 8000) + 45000`
3. Check Rhetor is running for team chat

#### 404 Errors
- Ensure using correct endpoints:
  - Specialist: `/api/v1/ai/specialists/{name}/message`
  - Team Chat: `/api/v1/ai/team-chat`

#### Connection Errors
- Verify AI specialist is registered in Rhetor's roster
- Check firewall/port availability
- Ensure AI socket server is listening

### 7. Best Practices

1. **Error Handling**: Always wrap chat calls in try-catch blocks
2. **Loading States**: Show loading indicators during API calls
3. **Message History**: Limit displayed messages to prevent memory issues
4. **Timeouts**: Set reasonable timeouts (default: 10 seconds)
5. **User Feedback**: Provide clear error messages to users

### 8. Example Implementation

See the Noesis component for a complete reference implementation:
- HTML: `/Hephaestus/ui/components/noesis/noesis-component.html`
- JavaScript: `/Hephaestus/ui/scripts/noesis/noesis-component.js`

This implementation includes:
- Proper chat UI with color-coded messages
- AI status indicators
- Error handling
- Team chat with broadcast functionality
- Clean message display