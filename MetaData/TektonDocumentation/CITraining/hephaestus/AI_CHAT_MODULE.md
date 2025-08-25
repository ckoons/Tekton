# AI Chat Module - Unified Communication for Hephaestus UI

## Overview

The AI Chat module (`/Hephaestus/ui/scripts/shared/ai-chat.js`) provides a unified interface for all Tekton UI components to communicate with AI specialists. This follows Casey's principle: "AIs are just sockets" - treating all AI communication as simple socket connections with a unified interface.

## Design Philosophy

1. **One Set of Routines**: All UI components use the same communication layer
2. **Socket-First**: Treats AIs as socket connections (with HTTP fallback)
3. **Based on aish**: Follows the same patterns as the CLI tool
4. **Transparent Routing**: Automatically routes to socket or HTTP based on AI type

## Usage Guide

### Basic Usage

```javascript
// Send message to a single AI
AIChat.sendMessage('noesis-ai', 'Hello Noesis!')
    .then(response => {
        console.log(response);
        // response = { content: "AI's response", status: "success", ... }
    });

// Broadcast to multiple AIs
AIChat.broadcastMessage('Team update', ['apollo-ai', 'athena-ai'])
    .then(responses => {
        // responses = [{ socket_id: 'apollo-ai', content: '...' }, ...]
    });

// Broadcast to ALL AIs
AIChat.broadcastMessage('System announcement', [])
    .then(responses => {
        // Empty array means broadcast to all
    });
```

### Integration Example (Noesis)

```javascript
function sendDiscoveryChat() {
    const message = input.value.trim();
    
    // Add typing indicator
    const typingId = 'typing-' + Date.now();
    addChatMessage('...', 'typing', typingId);
    
    // Send to AI
    AIChat.sendMessage('noesis-ai', message)
        .then(response => {
            removeTypingIndicator(typingId);
            
            // Parse for special formatting
            const parts = AIChat.parseResponse(response);
            parts.forEach(part => {
                if (part.type === 'text') {
                    addChatMessage(part.content, 'ai');
                } else if (part.type === 'block') {
                    // Special insight block
                    addChatMessage(part.content, 'insight');
                }
            });
        })
        .catch(error => {
            removeTypingIndicator(typingId);
            addChatMessage('Failed to connect', 'system');
        });
}
```

### Special Response Formatting

The module automatically parses responses for special blocks:

```
Normal text here...
{This will be displayed as a special insight block}
More normal text...
```

Use `AIChat.parseResponse(response)` to get an array of parts:
```javascript
[
    { type: 'text', content: 'Normal text here...' },
    { type: 'block', content: 'This will be displayed as a special insight block' },
    { type: 'text', content: 'More normal text...' }
]
```

## Architecture

### Communication Flow

1. **UI Component** calls `AIChat.sendMessage()`
2. **AIChat** discovers AI connection info (cached)
3. **Route Decision**:
   - Greek Chorus AIs (ports 45000-50000) → Socket proxy
   - Rhetor-managed specialists → HTTP API
4. **Response** parsed and returned to UI

### AI Discovery

The module maintains a cache of AI connection information:
- First checks cached info
- Falls back to discovery through Rhetor
- Has hardcoded port map as final fallback

### Error Handling

- Automatic fallback to team-chat endpoint if direct connection fails
- Clear error messages for debugging
- Graceful degradation when services are unavailable

## Adding to New Components

1. **Ensure ai-chat.js is loaded** (already in index.html)

2. **Update your component's chat function**:
```javascript
// Instead of direct fetch() calls
fetch('/api/some-endpoint', {...})

// Use AIChat
AIChat.sendMessage('your-component-ai', message)
```

3. **Handle responses with formatting**:
```javascript
const parts = AIChat.parseResponse(response);
parts.forEach(part => {
    if (part.type === 'text') {
        addChatMessage(part.content, 'ai');
    } else if (part.type === 'block') {
        addChatMessage(part.content, 'special');
    }
});
```

## Benefits

1. **Unified Debugging**: One place to debug all AI communication
2. **Consistent Behavior**: All components work the same way
3. **Easy Updates**: Change communication logic in one place
4. **Fallback Support**: Multiple connection methods tried automatically
5. **Future-Proof**: Easy to add new AI types or connection methods

## Debugging Tips

1. **Check browser console** for connection attempts
2. **Verify AI is running**: `aish -l` in terminal
3. **Check Rhetor health**: http://localhost:8003/health
4. **Enable debug mode** in ai-chat.js (uncomment console.logs)

## Future Enhancements

- WebSocket support for streaming responses
- Direct socket connections (when browser APIs allow)
- Connection pooling for performance
- Automatic reconnection logic

## Important Notes

- Currently requires Rhetor as a proxy for socket connections
- Team chat always goes through Rhetor's team-chat endpoint
- Port mappings are hardcoded as fallback (should match AI launcher)

---

*Created by Jill on July 5, 2025 during the Noesis sprint with Casey*