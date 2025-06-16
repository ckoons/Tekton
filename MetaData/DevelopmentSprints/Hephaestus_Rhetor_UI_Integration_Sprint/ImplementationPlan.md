# Hephaestus-Rhetor UI Integration - Implementation Plan

## Overview

This document provides the detailed implementation plan for integrating Rhetor AI specialists with Hephaestus UI components. It breaks down each phase into specific tasks with clear technical requirements.

## Phase 1: Foundation & Routing (Days 1-2)

### 1.1 Component Specialist Registry

**Location**: `Rhetor/rhetor/core/component_specialists.py`

```python
# Create new module for component-specialist mapping
class ComponentSpecialistRegistry:
    def __init__(self):
        self.specialists = {}
        self.component_configs = self._load_component_configs()
    
    async def ensure_specialist(self, component_id: str) -> AISpecialist:
        """Create or retrieve specialist for component"""
        if component_id not in self.specialists:
            config = self.component_configs.get(component_id)
            specialist = await self._create_component_specialist(component_id, config)
            self.specialists[component_id] = specialist
        return self.specialists[component_id]
```

**Tasks**:
- [ ] Create ComponentSpecialistRegistry class
- [ ] Load component AI configurations from registry
- [ ] Implement specialist creation with model selection
- [ ] Add lifecycle management (recreate on config change)
- [ ] Add debug instrumentation per guidelines

### 1.2 Hermes Message Routing Enhancement

**Location**: `Hermes/hermes/core/message_bus.py`

```python
# Add component-specific AI routing
AI_CHAT_TOPIC_PATTERN = "ai.chat.{component_id}"

async def route_ai_message(self, component_id: str, message: dict):
    topic = AI_CHAT_TOPIC_PATTERN.format(component_id=component_id)
    await self.publish(topic, message)
```

**Tasks**:
- [ ] Add AI chat topic pattern
- [ ] Implement component-aware routing
- [ ] Add message validation
- [ ] Update subscription handling
- [ ] Add debug logging

### 1.3 Rhetor API Extensions

**Location**: `Rhetor/rhetor/api/endpoints.py`

```python
@router.post("/api/component/{component_id}/chat")
async def component_chat(component_id: str, request: ChatRequest):
    """Route chat request to component's specialist"""
    specialist = await registry.ensure_specialist(component_id)
    response = await specialist.process_message(request.message)
    return response
```

**Tasks**:
- [ ] Add component chat endpoint
- [ ] Add specialist assignment endpoint
- [ ] Add component configuration endpoint
- [ ] Implement streaming support
- [ ] Add error handling

## Phase 2: Right Panel Integration (Days 3-4)

### 2.1 Component AI Chat Service

**Location**: `Hephaestus/ui/scripts/component-ai-chat.js`

```javascript
class ComponentAIChat {
    constructor(componentId) {
        this.componentId = componentId;
        this.rhetorService = new RhetorService();
        this.hermesConnector = window.hermesConnector;
        this.chatHistory = [];
        this.loadSettings();
    }
    
    async sendMessage(message) {
        // Add to chat history if enabled
        if (this.saveHistory) {
            this.addToHistory('user', message);
        }
        
        // Send through Rhetor
        const response = await this.rhetorService.componentChat(
            this.componentId, 
            message
        );
        
        // Handle streaming response
        if (response.streaming) {
            await this.handleStreamingResponse(response);
        }
        
        return response;
    }
}
```

**Tasks**:
- [ ] Create ComponentAIChat class
- [ ] Implement message sending
- [ ] Add streaming response handling
- [ ] Implement chat history management
- [ ] Add settings integration
- [ ] Add TektonDebug instrumentation

### 2.2 Terminal Chat Enhancement

**Location**: `Hephaestus/ui/scripts/terminal-chat-enhanced.js`

```javascript
// Extend existing terminal chat for AI integration
class AITerminalChat extends TerminalChat {
    constructor(container, componentId) {
        super(container);
        this.componentId = componentId;
        this.aiChat = new ComponentAIChat(componentId);
    }
    
    async handleUserInput(message) {
        this.addMessage('user', message);
        this.showTypingIndicator();
        
        try {
            const response = await this.aiChat.sendMessage(message);
            this.hideTypingIndicator();
            this.addMessage('ai', response.content, response.specialist_id);
        } catch (error) {
            this.handleError(error);
        }
    }
}
```

**Tasks**:
- [ ] Extend terminal chat class
- [ ] Integrate ComponentAIChat service
- [ ] Add typing indicators
- [ ] Implement error handling
- [ ] Add specialist identification
- [ ] Update UI bindings

### 2.3 Component Registration Updates

**Location**: `Hephaestus/ui/server/component_registry.json`

```json
{
  "athena": {
    "id": "athena",
    "ai_config": {
      "specialist_id": "athena-assistant",
      "model_preference": "claude-3-haiku-20240307",
      "ollama_fallback": "qwen2.5-coder:7b-instruct",
      "system_prompt": "You are Athena's knowledge assistant, specializing in quick information retrieval and knowledge graph queries.",
      "personality": "efficient, precise, knowledgeable"
    }
  }
}
```

**Tasks**:
- [ ] Update all component entries with AI config
- [ ] Define specialist IDs
- [ ] Set model preferences
- [ ] Create system prompts
- [ ] Add personality traits

## Phase 3: Menu Bar Enhancement (Days 5-6)

### 3.1 Rhetor Menu Component API

**Location**: `Hephaestus/ui/scripts/components/rhetor-component.js`

```javascript
class RhetorMenuComponent {
    async renderContent() {
        // When selected, take over display area
        const content = `
            <div class="rhetor-menu-interface">
                <div class="rhetor-controls">
                    <select id="component-selector">
                        ${this.renderComponentOptions()}
                    </select>
                    <button onclick="this.assignSpecialist()">
                        Assign Specialist
                    </button>
                </div>
                <div class="specialist-status">
                    ${this.renderSpecialistStatus()}
                </div>
                <div class="quick-actions">
                    ${this.renderQuickActions()}
                </div>
            </div>
        `;
        return content;
    }
    
    async assignSpecialist() {
        const componentId = document.getElementById('component-selector').value;
        const specialistId = await this.selectSpecialist();
        await this.rhetorService.assignSpecialist(componentId, specialistId);
    }
}
```

**Tasks**:
- [ ] Implement full display area control
- [ ] Add component selector
- [ ] Add specialist assignment UI
- [ ] Implement quick actions
- [ ] Add status displays
- [ ] Add model configuration

### 3.2 Quick Actions Implementation

**Locations**: Various menu bar controls

**Quick Actions**:
1. **Create Specialist**: Quick creation from templates
2. **Switch Model**: Change model for active specialist  
3. **Clear Context**: Reset conversation for component
4. **View Metrics**: Show specialist performance
5. **Team Chat**: Launch orchestrated discussion

**Tasks**:
- [ ] Implement create specialist dialog
- [ ] Add model switcher
- [ ] Add context management
- [ ] Implement metrics display
- [ ] Add team chat launcher

## Phase 4: Settings & Polish (Day 7)

### 4.1 Chat Persistence Settings

**Location**: `Tekton/.env.tekton`

```bash
# Chat persistence settings
SAVE_CHAT_HISTORY=false
CHAT_HISTORY_MAX_SIZE=1000
CHAT_HISTORY_ROTATION=7d
```

**Location**: `Hephaestus/ui/scripts/settings-manager.js`

```javascript
// Add to existing settings
const chatSettings = {
    saveHistory: env.SAVE_CHAT_HISTORY || false,
    maxHistorySize: env.CHAT_HISTORY_MAX_SIZE || 1000,
    historyRotation: env.CHAT_HISTORY_ROTATION || '7d'
};

// Add UI control near SHOW_GREEK_NAMES
<div class="setting-item">
    <label>
        <input type="checkbox" id="save-chat-history" 
               checked={chatSettings.saveHistory}>
        Save Chat History
    </label>
</div>
```

**Tasks**:
- [ ] Add environment variables
- [ ] Update settings manager
- [ ] Add UI controls
- [ ] Implement localStorage management
- [ ] Add rotation logic
- [ ] Document settings

### 4.2 Integration Testing

**Location**: `tests/integration/test_hephaestus_rhetor.py`

```python
async def test_component_chat_integration():
    """Test full chat flow from UI to AI response"""
    # Start Hephaestus and Rhetor
    # Send chat message to component
    # Verify specialist response
    # Check streaming works
    # Verify history saved/not saved
```

**Tasks**:
- [ ] Create integration test suite
- [ ] Test each component chat
- [ ] Test streaming responses
- [ ] Test error scenarios
- [ ] Test settings persistence
- [ ] Performance benchmarks

### 4.3 Documentation

**Locations**: Various documentation files

**Documentation Updates**:
1. Update Hephaestus user guide
2. Update Rhetor integration guide
3. Create component AI assistant guide
4. Update API documentation
5. Create troubleshooting guide

**Tasks**:
- [ ] Write user documentation
- [ ] Update API references
- [ ] Create examples
- [ ] Document configuration
- [ ] Add troubleshooting section

## Testing Strategy

### Unit Tests
- Component specialist registry
- Message routing logic
- Settings management
- Chat history persistence

### Integration Tests
- End-to-end chat flow
- Streaming responses
- Error handling
- Model fallbacks

### Performance Tests
- Multiple concurrent chats
- Large message handling
- History storage limits
- Streaming latency

## Rollout Plan

1. **Alpha Testing**: Test with single component (Athena)
2. **Beta Testing**: Enable for 3-4 components
3. **Full Rollout**: Enable for all components
4. **Monitoring**: Track usage and performance
5. **Optimization**: Tune based on metrics

## Success Metrics

- All components have working AI chat
- Response time < 2s for first token
- Streaming works smoothly
- Settings persist correctly
- No memory leaks
- 80% test coverage

## Risk Mitigation

- **Fallback Models**: Always have Ollama backup
- **Error Messages**: Clear user feedback
- **Performance**: Queue management for concurrent requests
- **Storage**: Implement history size limits
- **Security**: Validate all inputs