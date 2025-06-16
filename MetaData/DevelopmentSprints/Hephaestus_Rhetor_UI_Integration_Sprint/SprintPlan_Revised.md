# Hephaestus-Rhetor UI Integration Sprint - Revised Sprint Plan

## Overview

This sprint implements a unified chat interface system for Hephaestus where each Tekton component has its own AI assistant managed by Rhetor. The UI features a fixed right panel footer with context-aware chat input that routes to the active component's AI or to team chat.

## Sprint Goals

1. **Fixed Right Panel Chat Interface**: Implement a persistent chat footer in the right panel that stays visible across all components
2. **Context-Aware Chat Routing**: Chat input routes to the active component's AI based on left panel navigation selection
3. **Team Chat Integration**: Single team chat implementation that can be accessed from any component, moderated by Rhetor
4. **Chat History Management**: Component-specific chat histories with optional persistence, plus shared team chat history

## Technical Architecture

### UI Structure
```
┌─────────────────────────────────────────────────────────────┐
│                        HEADER (Fixed)                        │
├─────────────────┬────────────────────────────────────────────┤
│                 │                                             │
│   LEFT PANEL    │            RIGHT PANEL                      │
│                 │  ┌─────────────────────────────────────┐  │
│  ┌──────────┐   │  │         MENU BAR (Context-aware)    │  │
│  │ Tekton   │   │  └─────────────────────────────────────┘  │
│  │ Rhetor   │   │  ┌─────────────────────────────────────┐  │
│  │ Apollo   │   │  │                                     │  │
│  │ Engram   │   │  │      COMPONENT CONTENT AREA        │  │
│  │ ...      │   │  │         (Chat Messages)            │  │
│  │          │   │  │                                     │  │
│  └──────────┘   │  └─────────────────────────────────────┘  │
│                 │  ┌─────────────────────────────────────┐  │
│                 │  │   CHAT INPUT FOOTER (Fixed)         │  │
│                 │  │   > [placeholder: "Chat with X AI"] │  │
│                 │  └─────────────────────────────────────┘  │
└─────────────────┴────────────────────────────────────────────┘
```

### Chat Routing Architecture

1. **Component AI Chat**: 
   - Input in footer routes to active component (e.g., "rhetor", "apollo", "engram")
   - Rhetor wraps all component AIs for prompt engineering and context management
   - Each component maintains its own chat history

2. **Team Chat**:
   - Special routing key: "team" 
   - Rhetor moderates all team conversations
   - Shared history across all components

### Message Flow
```
User Input → Chat Widget → Rhetor Router → Component AI (wrapped by Rhetor)
                                      ↓
                                Team Chat → All AIs (moderated by Rhetor)
```

## Implementation Phases

### Phase 1: Right Panel Chat Infrastructure (Day 1-2)
- Create reusable chat widget component
- Implement fixed footer with context-aware placeholder
- Build message bubble UI (left: AI, right: human)
- Add infinite scroll functionality
- Wire up to active component detection

### Phase 2: Rhetor Integration (Day 3-4)
- Connect Rhetor's LLM Chat to the chat widget
- Implement message routing through Rhetor
- Add chat history management for Rhetor
- Test Rhetor AI conversations

### Phase 3: Team Chat Implementation (Day 5)
- Build team chat routing (using "team" identifier)
- Implement Rhetor moderation for team chat
- Add speaker identification in bubbles (e.g., "Team-Apollo", "Team-Rhetor")
- Create shared team chat history

### Phase 4: Chat Persistence & Polish (Day 6-7)
- Implement localStorage chat history per component
- Add SAVE_CHAT_HISTORY setting integration
- Polish UI transitions and loading states
- Complete documentation

## Key Implementation Details

### Chat Widget (Simple HTML Injection)
```javascript
// Simple chat widget for HTML injection
const ChatWidget = {
  activeComponent: 'rhetor',
  
  init: function(componentName) {
    this.activeComponent = componentName;
    this.updatePlaceholder();
    this.loadChatHistory();
  },
  
  updatePlaceholder: function() {
    const input = document.getElementById('chat-input');
    if (this.activeComponent === 'team') {
      input.placeholder = 'Tekton Team Chat (All AIs)';
    } else {
      input.placeholder = `Chat with ${this.capitalize(this.activeComponent)} AI`;
    }
  },
  
  sendMessage: function(message) {
    const payload = {
      component: this.activeComponent,
      message: message,
      timestamp: new Date().toISOString()
    };
    
    // Route through Rhetor
    this.routeToRhetor(payload);
  }
};
```

### Message Bubble Format
```html
<!-- AI Message (left side) -->
<div class="chat-bubble ai">
  <div class="speaker">Rhetor</div>
  <div class="message">Hello! I'm Rhetor, your LLM orchestration assistant.</div>
</div>

<!-- Human Message (right side) -->
<div class="chat-bubble human">
  <div class="message">How can you help me?</div>
</div>

<!-- Team Chat Message -->
<div class="chat-bubble ai team">
  <div class="speaker">Team-Apollo</div>
  <div class="message">I can help with executive coordination...</div>
</div>
```

### Rhetor Message Routing API
```python
# Rhetor handles all message routing
@app.post("/chat/route")
async def route_message(request: RouteRequest):
    """
    Route messages to appropriate AI or team chat
    
    Request format:
    {
        "component": "apollo",  # or "team" for team chat
        "message": "Hello",
        "context_id": "apollo-chat-123",
        "user_id": "user-1"
    }
    """
    if request.component == "team":
        return await orchestrate_team_chat(request)
    else:
        return await route_to_component_ai(request)
```

## Success Criteria

1. **Fixed Chat Interface**: Right panel footer stays visible and updates based on active component
2. **Rhetor LLM Chat**: Works through the new chat interface (not the old UI)
3. **Context Awareness**: Placeholder and routing change based on left panel selection
4. **Team Chat**: Accessible from any component, shows speaker labels
5. **Chat History**: Persists per component with option to save/clear
6. **Clean Integration**: No complex JavaScript frameworks, just simple HTML injection

## Out of Scope (Future Sprints)

- Implementing AI assistants for components other than Rhetor
- Advanced AI-to-AI communication protocols
- Cross-component context sharing
- Voice/multimodal interfaces

## Notes

- All chat messages route through Rhetor for wrapping and prompt engineering
- Team chat is always moderated by Rhetor regardless of which component initiates it
- The existing Rhetor component UI tabs remain but chat happens in the right panel
- Simple, clean implementation without complex state management