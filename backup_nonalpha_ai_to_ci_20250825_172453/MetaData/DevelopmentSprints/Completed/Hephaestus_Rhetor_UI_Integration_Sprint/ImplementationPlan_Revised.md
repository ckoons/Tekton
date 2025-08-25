# Hephaestus-Rhetor UI Integration - Implementation Plan

## Phase 1: Right Panel Chat Infrastructure

### 1.1 Create Chat Widget HTML Structure

**File**: `/Hephaestus/ui/components/shared/chat-widget.html`
```html
<div class="chat-widget">
  <div class="chat-messages" id="chat-messages">
    <!-- Messages will be injected here -->
  </div>
  <div class="chat-input-footer">
    <div class="chat-prompt">></div>
    <input type="text" class="chat-input" id="chat-input" 
           placeholder="Chat with Rhetor AI" 
           onkeypress="if(event.key==='Enter') ChatWidget.handleSend()">
    <button class="chat-send" onclick="ChatWidget.handleSend()">Send</button>
  </div>
</div>
```

### 1.2 Create Chat Widget JavaScript

**File**: `/Hephaestus/ui/scripts/chat-widget.js`
```javascript
// Global chat widget for all components
window.ChatWidget = {
  activeComponent: 'rhetor',
  messages: {},  // Store messages per component
  
  init: function(componentName) {
    console.log(`[ChatWidget] Initializing for ${componentName}`);
    this.activeComponent = componentName;
    this.updatePlaceholder();
    this.loadMessages();
    this.scrollToBottom();
  },
  
  updatePlaceholder: function() {
    const input = document.getElementById('chat-input');
    if (!input) return;
    
    if (this.activeComponent === 'team') {
      input.placeholder = 'Tekton Team Chat (All CIs)';
    } else {
      const componentTitle = this.activeComponent.charAt(0).toUpperCase() + 
                            this.activeComponent.slice(1);
      input.placeholder = `Chat with ${componentTitle} AI`;
    }
  },
  
  handleSend: function() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;
    
    // Add user message to chat
    this.addMessage('human', message);
    
    // Clear input
    input.value = '';
    
    // Send to Rhetor
    this.sendToRhetor(message);
  },
  
  addMessage: function(type, content, speaker = null) {
    const messagesDiv = document.getElementById('chat-messages');
    if (!messagesDiv) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-bubble ${type}`;
    
    let html = '';
    if (speaker) {
      html += `<div class="speaker">${speaker}</div>`;
    }
    html += `<div class="message">${this.escapeHtml(content)}</div>`;
    html += `<div class="timestamp">${new Date().toLocaleTimeString()}</div>`;
    
    messageDiv.innerHTML = html;
    messagesDiv.appendChild(messageDiv);
    
    // Save to history
    this.saveMessage(type, content, speaker);
    
    // Scroll to bottom
    this.scrollToBottom();
  },
  
  sendToRhetor: function(message) {
    const payload = {
      type: 'COMPONENT_CHAT',
      source: 'UI',
      component: this.activeComponent,
      message: message,
      context_id: `${this.activeComponent}-chat`,
      timestamp: new Date().toISOString()
    };
    
    // Show typing indicator
    this.showTyping();
    
    // Send via WebSocket if available
    if (window.websocketManager && window.websocketManager.isConnected()) {
      window.websocketManager.sendMessage(payload);
    } else {
      // Fallback to HTTP
      this.sendViaHttp(payload);
    }
  },
  
  sendViaHttp: async function(payload) {
    try {
      const response = await fetch('http://localhost:8003/chat/route', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          component: payload.component,
          message: payload.message,
          context_id: payload.context_id
        })
      });
      
      const data = await response.json();
      this.hideTyping();
      
      // Add CI response
      const speaker = payload.component === 'team' ? 
        `Team-${data.speaker || 'Rhetor'}` : 
        this.capitalize(payload.component);
      
      this.addMessage('ai', data.message, speaker);
      
    } catch (error) {
      console.error('[ChatWidget] Error sending message:', error);
      this.hideTyping();
      this.addMessage('system', 'Error: Could not send message. Please try again.');
    }
  },
  
  showTyping: function() {
    const typingId = 'typing-indicator';
    if (document.getElementById(typingId)) return;
    
    const messagesDiv = document.getElementById('chat-messages');
    if (!messagesDiv) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.id = typingId;
    typingDiv.className = 'chat-bubble ai typing';
    typingDiv.innerHTML = `
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    `;
    
    messagesDiv.appendChild(typingDiv);
    this.scrollToBottom();
  },
  
  hideTyping: function() {
    const typing = document.getElementById('typing-indicator');
    if (typing) {
      typing.remove();
    }
  },
  
  saveMessage: function(type, content, speaker) {
    const component = this.activeComponent;
    if (!this.messages[component]) {
      this.messages[component] = [];
    }
    
    this.messages[component].push({
      type: type,
      content: content,
      speaker: speaker,
      timestamp: new Date().toISOString()
    });
    
    // Save to localStorage if enabled
    if (this.shouldSaveHistory()) {
      localStorage.setItem(
        `tekton-chat-${component}`, 
        JSON.stringify(this.messages[component])
      );
    }
  },
  
  loadMessages: function() {
    const component = this.activeComponent;
    
    // Try to load from localStorage
    if (this.shouldSaveHistory()) {
      const saved = localStorage.getItem(`tekton-chat-${component}`);
      if (saved) {
        this.messages[component] = JSON.parse(saved);
      }
    }
    
    // Clear and repopulate chat
    const messagesDiv = document.getElementById('chat-messages');
    if (!messagesDiv) return;
    
    messagesDiv.innerHTML = '';
    
    // Add saved messages
    const messages = this.messages[component] || [];
    messages.forEach(msg => {
      this.addMessage(msg.type, msg.content, msg.speaker);
    });
    
    // Add welcome message if empty
    if (messages.length === 0) {
      this.addWelcomeMessage();
    }
  },
  
  addWelcomeMessage: function() {
    const welcomeMessages = {
      rhetor: "Hello! I'm Rhetor, your LLM orchestration and prompt engineering assistant. How can I help you today?",
      team: "Welcome to Tekton Team Chat! All CI assistants are here to collaborate. What would you like to discuss?",
      apollo: "Greetings! I'm Apollo, ready to help with executive coordination and prediction.",
      engram: "Hello! I'm Engram, your memory and context management specialist.",
      // Add more components as needed
    };
    
    const message = welcomeMessages[this.activeComponent] || 
      `Hello! I'm the ${this.capitalize(this.activeComponent)} CI assistant.`;
    
    const speaker = this.activeComponent === 'team' ? 'Team-Rhetor' : this.capitalize(this.activeComponent);
    this.addMessage('ai', message, speaker);
  },
  
  shouldSaveHistory: function() {
    // Check global setting
    return window.SAVE_CHAT_HISTORY !== false;
  },
  
  clearHistory: function() {
    const component = this.activeComponent;
    this.messages[component] = [];
    localStorage.removeItem(`tekton-chat-${component}`);
    this.loadMessages();
  },
  
  scrollToBottom: function() {
    const messagesDiv = document.getElementById('chat-messages');
    if (messagesDiv) {
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
  },
  
  capitalize: function(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  },
  
  escapeHtml: function(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
};
```

### 1.3 Update Component HTML Templates

Each component needs to include the chat widget. Example for Rhetor:

**Update**: `/Hephaestus/ui/components/rhetor/rhetor-component.html`
```html
<!-- Add to the bottom of rhetor component, replacing the existing footer -->
<div class="rhetor__content-with-chat">
  <!-- Existing content panels here -->
  
  <!-- Chat Widget Footer -->
  <div id="chat-widget-container"></div>
</div>

<script>
// Load chat widget when component loads
document.addEventListener('DOMContentLoaded', function() {
  // Load chat widget HTML
  fetch('/components/shared/chat-widget.html')
    .then(response => response.text())
    .then(html => {
      document.getElementById('chat-widget-container').innerHTML = html;
      // Initialize for this component
      if (window.ChatWidget) {
        window.ChatWidget.init('rhetor');
      }
    });
});
</script>
```

### 1.4 Chat Widget Styles

**File**: `/Hephaestus/ui/styles/chat-widget.css`
```css
/* Chat Widget Styles */
.chat-widget {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--bg-primary, #1e1e2e);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  position: relative;
  animation: fadeIn 0.3s ease;
}

.chat-bubble.human {
  align-self: flex-end;
  background-color: var(--color-primary, #673AB7);
  color: white;
  border-bottom-right-radius: 4px;
}

.chat-bubble.ai {
  align-self: flex-start;
  background-color: var(--bg-secondary, #252535);
  color: var(--text-primary, #f0f0f0);
  border-bottom-left-radius: 4px;
}

.chat-bubble.system {
  align-self: center;
  background-color: var(--bg-tertiary, #333345);
  color: var(--text-secondary, #aaaaaa);
  max-width: 80%;
  text-align: center;
  font-size: 0.9em;
}

.speaker {
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--text-secondary, #aaaaaa);
  font-size: 0.85em;
}

.timestamp {
  font-size: 0.75em;
  color: var(--text-secondary, #666);
  margin-top: 4px;
}

.chat-input-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background-color: var(--bg-secondary, #252535);
  border-top: 1px solid var(--border-color, #444);
  position: sticky;
  bottom: 0;
}

.chat-prompt {
  color: #4CAF50;
  font-weight: bold;
  font-size: 18px;
}

.chat-input {
  flex: 1;
  background-color: var(--bg-tertiary, #333345);
  border: 1px solid var(--border-color, #444);
  border-radius: 8px;
  padding: 8px 16px;
  color: var(--text-primary, #f0f0f0);
  font-size: 14px;
  outline: none;
}

.chat-input:focus {
  border-color: var(--color-primary, #673AB7);
  box-shadow: 0 0 0 2px rgba(103, 58, 183, 0.2);
}

.chat-send {
  padding: 8px 20px;
  background-color: var(--color-primary, #673AB7);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.chat-send:hover {
  background-color: var(--color-primary-hover, #5E35B1);
}

/* Typing indicator */
.typing .typing-dots {
  display: flex;
  align-items: center;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background-color: var(--text-secondary, #aaa);
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.3;
  }
  30% {
    opacity: 1;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scrollbar styling */
.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: var(--bg-secondary, #252535);
}

.chat-messages::-webkit-scrollbar-thumb {
  background: var(--border-color, #444);
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary, #666);
}
```

## Phase 2: Rhetor Integration

### 2.1 Add Chat Routing Endpoint to Rhetor

**File**: `/Rhetor/rhetor/api/app.py` (additions)
```python
class RouteRequest(TektonBaseModel):
    component: str  # Component name or "team"
    message: str
    context_id: str
    user_id: Optional[str] = None

@app.post("/chat/route")
async def route_chat_message(request: RouteRequest):
    """Route chat messages to component CIs or team chat"""
    
    if not ai_specialist_manager:
        raise HTTPException(status_code=503, detail="AI Specialist Manager not initialized")
    
    try:
        # Handle team chat
        if request.component == "team":
            # Get all active specialists for team chat
            specialists = await ai_specialist_manager.get_active_specialists()
            
            # Rhetor moderates team chat
            moderated_response = await ai_specialist_manager.moderate_team_chat(
                message=request.message,
                participants=specialists,
                context_id=request.context_id
            )
            
            return {
                "success": True,
                "component": "team",
                "speaker": moderated_response.get("primary_speaker", "Rhetor"),
                "message": moderated_response.get("message"),
                "participants": moderated_response.get("participants", [])
            }
        
        else:
            # Route to specific component AI
            specialist_id = f"{request.component}-assistant"
            
            # Ensure specialist exists
            specialist = await ai_specialist_manager.get_or_create_specialist(
                specialist_id=specialist_id,
                component=request.component
            )
            
            # Wrap with Rhetor for prompt engineering
            enhanced_prompt = await prompt_engine.enhance_for_component(
                message=request.message,
                component=request.component,
                context_id=request.context_id
            )
            
            # Get response from specialist
            response = await ai_specialist_manager.send_to_specialist(
                specialist_id=specialist_id,
                message=enhanced_prompt,
                context_id=request.context_id
            )
            
            return {
                "success": True,
                "component": request.component,
                "message": response.get("message"),
                "model": response.get("model"),
                "provider": response.get("provider")
            }
            
    except Exception as e:
        logger.error(f"Error routing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 2.2 WebSocket Handler Updates

**Update**: `/Hephaestus/ui/scripts/websocket.js`
```javascript
// Add handler for component chat responses
websocketManager.messageHandlers.COMPONENT_CHAT_RESPONSE = function(message) {
  console.log('[WebSocket] Component chat response:', message);
  
  const payload = message.payload;
  if (!payload) return;
  
  // Hide typing indicator
  if (window.ChatWidget) {
    window.ChatWidget.hideTyping();
    
    // Add CI response
    const speaker = payload.component === 'team' ? 
      `Team-${payload.speaker || 'Rhetor'}` : 
      window.ChatWidget.capitalize(payload.component);
    
    window.ChatWidget.addMessage('ai', payload.message, speaker);
  }
};

// Add handler for streaming responses
websocketManager.messageHandlers.COMPONENT_CHAT_STREAM = function(message) {
  const payload = message.payload;
  if (!payload || !window.ChatWidget) return;
  
  // Handle streaming chunks
  if (payload.chunk) {
    window.ChatWidget.appendToLastMessage(payload.chunk);
  }
  
  if (payload.done) {
    window.ChatWidget.hideTyping();
  }
};
```

### 2.3 Update Main Navigation Handler

**Update**: `/Hephaestus/ui/scripts/main.js`
```javascript
// Modify the navigation click handler to update chat widget
navItems.forEach(item => {
  item.addEventListener('click', function() {
    const componentId = this.getAttribute('data-component');
    if (!componentId) return;
    
    // ... existing navigation code ...
    
    // Update chat widget context
    if (window.ChatWidget) {
      window.ChatWidget.init(componentId);
    }
  });
});
```

## Phase 3: Team Chat Implementation

### 3.1 Team Chat Navigation

Add team chat access to the Rhetor component's Team Chat tab:

**Update**: `/Hephaestus/ui/components/rhetor/rhetor-component.html`
```javascript
// Update the team chat tab click handler
window.rhetor_switchTab = function(tabId) {
  // ... existing code ...
  
  if (tabId === 'teamchat' && window.ChatWidget) {
    // Switch chat widget to team mode
    window.ChatWidget.init('team');
  }
  
  // ... rest of existing code ...
};
```

### 3.2 Team Chat Orchestration

**File**: `/Rhetor/rhetor/core/team_chat_orchestrator.py`
```python
class TeamChatOrchestrator:
    """Orchestrates team chat with multiple CI specialists"""
    
    async def moderate_discussion(
        self,
        message: str,
        participants: List[str],
        context_id: str
    ) -> Dict[str, Any]:
        """
        Rhetor moderates team discussions
        
        1. Analyzes the message topic
        2. Determines which specialists should respond
        3. Collects responses
        4. Synthesizes a coherent team response
        """
        # Implementation details...
```

## Phase 4: Chat Persistence & Settings

### 4.1 Settings Integration

**Update**: `/Hephaestus/ui/scripts/settings/settings-manager.js`
```javascript
// Add chat history setting
SettingsManager.DEFAULTS.SAVE_CHAT_HISTORY = true;

SettingsManager.saveSettings = function() {
  // ... existing code ...
  
  // Update chat widget setting
  if (window.ChatWidget) {
    window.SAVE_CHAT_HISTORY = this.settings.SAVE_CHAT_HISTORY;
  }
};
```

### 4.2 Clear Chat History Option

Add to settings panel:
```html
<div class="setting-item">
  <label>Save Chat History</label>
  <input type="checkbox" id="save-chat-history" checked>
  <button onclick="ChatWidget.clearHistory()">Clear Current Chat</button>
</div>
```

## Testing Plan

### Phase 1 Tests
- [ ] Chat widget loads in right panel
- [ ] Input placeholder updates with component name
- [ ] Messages display with correct styling
- [ ] Scroll to bottom works
- [ ] Enter key sends message

### Phase 2 Tests
- [ ] Messages route to Rhetor
- [ ] CI responses appear in chat
- [ ] Typing indicator shows/hides
- [ ] Error handling works

### Phase 3 Tests
- [ ] Team chat mode activates
- [ ] Speaker labels show correctly
- [ ] Multiple CI responses display

### Phase 4 Tests
- [ ] Chat history persists on refresh
- [ ] Clear history works
- [ ] Settings toggle works

## Migration Notes

- Existing Rhetor component UI remains unchanged
- Chat functionality moves to right panel footer
- Team Chat tab in Rhetor switches widget to team mode
- All components will use the same chat widget pattern