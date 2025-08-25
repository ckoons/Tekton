# Tekton Component Chat Interface Design Guide

## Overview

This document outlines how to implement AI-powered chat interfaces for all Tekton components in Hephaestus. Each component will have its own dedicated CI assistant accessible through a consistent chat interface in the right panel footer.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    HEPHAESTUS UI                             │
├─────────────────┬────────────────────────────────────────────┤
│   LEFT PANEL    │            RIGHT PANEL                      │
│                 │  ┌─────────────────────────────────────┐  │
│  ⚡ Tekton      │  │    Component-Specific Content        │  │
│  🎭 Rhetor      │  │    (Apollo Dashboard, Athena KB,     │  │
│  🏛️ Apollo      │  │     Engram Memory View, etc.)        │  │
│  🧠 Engram      │  │                                      │  │
│  🦉 Athena      │  │                                      │  │
│  💰 Budget      │  │                                      │  │
│  🔄 Synthesis   │  └─────────────────────────────────────┘  │
│  🎯 Telos       │  ┌─────────────────────────────────────┐  │
│  ⚙️ Ergon       │  │  FIXED CHAT FOOTER (Always Visible)  │  │
│  🎨 Sophia      │  │  > Chat with [Component] CI ...      │  │
│  🔥 Prometheus  │  └─────────────────────────────────────┘  │
└─────────────────┴────────────────────────────────────────────┘
```

## Component CI Assignments

Each component gets a dedicated CI assistant with specific expertise:

| Component | CI Assistant ID | Primary Focus | Personality |
|-----------|----------------|---------------|-------------|
| Apollo | apollo-assistant | Executive coordination, predictions, planning | Professional, strategic, forward-thinking |
| Athena | athena-assistant | Knowledge queries, entity relationships | Wise, analytical, precise |
| Engram | engram-assistant | Memory management, context retrieval | Thoughtful, organized, detail-oriented |
| Budget | budget-assistant | Cost optimization, usage tracking | Practical, efficient, advisory |
| Synthesis | synthesis-assistant | Data integration, workflow composition | Systematic, interconnected, holistic |
| Telos | telos-assistant | Requirements management, traceability | Methodical, thorough, quality-focused |
| Ergon | ergon-assistant | Agent coordination, task management | Collaborative, process-oriented |
| Sophia | sophia-assistant | ML experiments, intelligence insights | Innovative, research-focused, curious |
| Prometheus | prometheus-assistant | Strategic planning, metrics analysis | Visionary, data-driven, improvement-focused |
| Metis | metis-assistant | Task decomposition, complexity analysis | Logical, structured, problem-solving |

## Implementation Pattern

### 1. Component HTML Structure

Each component needs to add the chat widget container at the bottom of their main content area:

```html
<!-- Example: /Hephaestus/ui/components/apollo/apollo-component.html -->
<div class="apollo__container">
  <!-- Existing Apollo content (dashboard, predictions, etc.) -->
  <div class="apollo__main-content">
    <!-- Current Apollo UI remains unchanged -->
  </div>
  
  <!-- Add chat widget container -->
  <div id="chat-widget-container" class="component-chat-container"></div>
</div>

<script>
// Initialize chat for this component
document.addEventListener('DOMContentLoaded', function() {
  // Load shared chat widget
  fetch('/components/shared/chat-widget.html')
    .then(response => response.text())
    .then(html => {
      document.getElementById('chat-widget-container').innerHTML = html;
      // Initialize with component name
      if (window.ChatWidget) {
        window.ChatWidget.init('apollo');
      }
    })
    .catch(error => {
      console.error('Failed to load chat widget:', error);
    });
});
</script>
```

### 2. Component-Specific CSS Adjustments

Add to each component's CSS to ensure proper layout:

```css
/* Example: /Hephaestus/ui/styles/components/apollo.css */
.apollo__container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.apollo__main-content {
  flex: 1;
  overflow-y: auto;
  /* Ensure content doesn't hide behind chat footer */
  padding-bottom: 20px;
}

.component-chat-container {
  /* Chat widget will be fixed at bottom */
  position: relative;
  z-index: 100;
}
```

### 3. Component Context Injection

Each component can provide context to their CI assistant:

```javascript
// Example: Apollo providing context to its AI
function initializeApolloChat() {
  if (window.ChatWidget) {
    // Set component-specific context
    window.ChatWidget.setContext({
      component: 'apollo',
      currentView: 'predictions', // or 'planning', 'context', etc.
      activeData: {
        // Any relevant data the CI should know about
        currentPredictions: getPredictionCount(),
        activeContexts: getActiveContexts()
      }
    });
  }
}
```

## Component-Specific Implementations

### Apollo (Executive Coordination)

```javascript
// Additional Apollo-specific chat features
window.ApolloChat = {
  // Quick actions for Apollo AI
  quickActions: [
    { label: "Analyze Current Context", action: "analyze_context" },
    { label: "Generate Prediction", action: "predict_next" },
    { label: "Plan Actions", action: "plan_actions" }
  ],
  
  // Handle Apollo-specific commands
  handleCommand: function(command) {
    if (command.startsWith('/predict')) {
      ChatWidget.sendMessage(`Please predict: ${command.substring(8)}`, {
        task_type: 'prediction'
      });
    }
  }
};
```

### Athena (Knowledge Graph)

```javascript
// Athena can show entity references in chat
window.AthenaChat = {
  // Enhanced message rendering for entity links
  renderMessage: function(message) {
    // Convert entity references to clickable links
    return message.replace(/\[Entity:([^\]]+)\]/g, function(match, entityId) {
      return `<a href="#" onclick="AthenaUI.showEntity('${entityId}')">${entityId}</a>`;
    });
  }
};
```

### Engram (Memory Management)

```javascript
// Engram chat integration with memory system
window.EngramChat = {
  // Auto-save important chat messages to memory
  onAIResponse: function(message) {
    if (message.includes('[REMEMBER]')) {
      EngramAPI.storeMemory({
        content: message,
        type: 'chat_insight',
        context: 'engram_assistant'
      });
    }
  }
};
```

### Budget (Cost Tracking)

```javascript
// Budget assistant with cost awareness
window.BudgetChat = {
  // Include current usage in context
  getChatContext: function() {
    return {
      daily_usage: BudgetUI.getCurrentUsage('daily'),
      remaining_budget: BudgetUI.getRemainingBudget(),
      active_models: BudgetUI.getActiveModels()
    };
  }
};
```

## Shared Chat Features

### 1. Component-Aware Placeholder Text

The chat input placeholder updates based on active component:

- Apollo: "Ask Apollo CI about predictions or planning..."
- Athena: "Query Athena CI about knowledge entities..."
- Engram: "Chat with Engram CI about memories..."
- Budget: "Get cost optimization advice from Budget AI..."

### 2. Chat History Management

Each component maintains separate chat history:

```javascript
// Chat histories stored by component
localStorage.setItem('tekton-chat-apollo', JSON.stringify(messages));
localStorage.setItem('tekton-chat-athena', JSON.stringify(messages));
// etc.
```

### 3. Component Switch Behavior

When switching between components:

1. Current chat minimizes but preserves state
2. New component's chat history loads
3. Placeholder text updates
4. CI context switches to new component

### 4. Team Chat Access

Team chat is accessible from any component via special command:

```javascript
// User types: @team Let's discuss the current system state
if (message.startsWith('@team')) {
  ChatWidget.switchToTeamChat();
  ChatWidget.sendMessage(message.substring(5));
}
```

## Error Handling

Each component should handle chat errors gracefully:

```javascript
// Component-specific error handling
window.ComponentChat = {
  onError: function(error) {
    if (error.type === 'ai_unavailable') {
      // Show component-specific fallback
      ChatWidget.showMessage(
        'AI assistant temporarily unavailable. ' +
        'You can still use manual features.',
        'system'
      );
    }
  }
};
```

## Accessibility Features

1. **Keyboard Navigation**: Tab through chat interface
2. **Screen Reader Support**: ARIA labels for all chat elements
3. **High Contrast Mode**: Respects system preferences
4. **Text Scaling**: Chat scales with browser zoom

## Testing Requirements

For each component integration:

- [ ] Chat widget loads without errors
- [ ] Placeholder text is component-specific
- [ ] Messages route to correct CI assistant
- [ ] Chat history persists across refreshes
- [ ] Component context is included in CI requests
- [ ] Team chat is accessible
- [ ] Errors are handled gracefully
- [ ] UI remains responsive during chat

## Migration Guide

For existing components without chat:

1. Add chat container div to component HTML
2. Include initialization script
3. Update component CSS for proper layout
4. Test chat functionality
5. Add component-specific enhancements

## Next Steps

1. Implement base chat widget (shared)
2. Add to Rhetor component first (reference implementation)
3. Roll out to other components in phases:
   - Phase 1: Apollo, Athena, Engram (core components)
   - Phase 2: Budget, Prometheus, Metis (analysis components)
   - Phase 3: Telos, Ergon, Synthesis, Sophia (specialized components)

This design ensures consistent chat UI across all components while allowing component-specific customizations.