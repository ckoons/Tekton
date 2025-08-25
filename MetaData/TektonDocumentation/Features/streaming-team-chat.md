# Streaming Team Chat Documentation

## Overview

The streaming team chat feature allows CI responses to be returned as they arrive, rather than waiting for all CIs to complete. This provides much better user experience and faster perceived performance.

## Architecture

### Server-Side (Rhetor)

**New Endpoint**: `/api/v2/team-chat/stream`

- Uses Server-Sent Events (SSE) for real-time streaming
- Each CI response is sent immediately when received
- Configurable timeout per CI (default 2 seconds)
- Supports targeting specific CIs or broadcasting to all

### Client-Side (JavaScript)

**Module**: `streaming-team-chat.js`

```javascript
// Stream a message to team chat
const abort = StreamingTeamChat.streamMessage(
    message,
    options,
    onResponse,  // Called for each response
    onError,     // Called for errors
    onComplete   // Called when done
);
```

## Usage Examples

### Basic Usage

```javascript
StreamingTeamChat.streamMessage(
    "What are the key principles of good design?",
    { timeout: 2.0 },
    (response) => {
        console.log(`${response.specialist}: ${response.content}`);
    }
);
```

### With Error Handling

```javascript
StreamingTeamChat.streamMessage(
    "Analyze this code pattern",
    { 
        timeout: 2.0,
        includeErrors: true,
        targetSpecialists: ['apollo-ai', 'athena-ai']
    },
    (response) => {
        // Handle each response
        addMessageToUI(response.specialist, response.content);
    },
    (error) => {
        // Handle errors (timeouts, connection issues)
        console.warn(`${error.specialist} failed: ${error.error}`);
    },
    (stats) => {
        // Final statistics
        console.log(`Got ${stats.totalResponses} responses in ${stats.totalTime}s`);
    }
);
```

### Abort Stream

```javascript
const abort = StreamingTeamChat.streamMessage(...);

// Later, if needed
abort(); // Stop receiving responses
```

## API Reference

### Endpoint

`POST /api/v2/team-chat/stream`

Request body:
```json
{
    "message": "Your message here",
    "target_specialists": ["apollo-ai", "athena-ai"],  // Optional
    "timeout_per_ai": 2.0,  // Seconds
    "include_errors": false  // Include timeout/error events
}
```

### Event Types

1. **start** - Stream initialized
```json
{
    "type": "start",
    "total_specialists": 18,
    "message": "Your message...",
    "timestamp": "2025-07-05T12:00:00Z"
}
```

2. **message** - CI response
```json
{
    "type": "response",
    "specialist_id": "apollo-ai",
    "content": "AI response text...",
    "model": "llama3.3:70b",
    "elapsed_time": 0.523,
    "index": 1
}
```

3. **complete** - Stream finished
```json
{
    "type": "complete",
    "total_responses": 15,
    "total_errors": 3,
    "total_time": 2.1,
    "average_response_time": 0.14
}
```

## Performance Benefits

### Old Team Chat (Wait for All)
```
Send → Wait for ALL CIs → Return all responses
        ↓
      2-10 seconds (depends on slowest AI)
```

### New Streaming Team Chat
```
Send → First response in ~0.5s → More arrive → Complete
        ↓                          ↓
      Immediate feedback      Progressive updates
```

## Integration with UI Components

The Noesis component has been updated to use streaming:

```javascript
// In noesis-component.html
if (window.StreamingTeamChat) {
    // Use streaming for better UX
    StreamingTeamChat.streamMessage(message, options, ...);
} else {
    // Fallback to old method
    AIChat.broadcastMessage(message);
}
```

## Connection Pool Integration

The streaming team chat works seamlessly with the connection pool:

1. **First request**: Establishes connections (may be slower)
2. **Subsequent requests**: Reuses connections (very fast)
3. **Failed connections**: Automatically excluded after timeout

## Troubleshooting

### No Responses
- Check if CI specialists are running: `tekton-status`
- Verify Rhetor is running: `curl http://localhost:8003/health`
- Check individual AI: `curl http://localhost:8003/api/team-chat/sockets`

### Slow Responses
- Reduce timeout: `timeout_per_ai: 1.0`
- Check Ollama performance: `ollama ps`
- Consider running fewer CIs if system is overloaded

### Testing

Test scripts available:
- `scripts/test_streaming_team_chat.py` - Full test suite
- `scripts/simple_debug.py` - Quick diagnostic

## Future Enhancements

1. **WebSocket Support** - For bidirectional communication
2. **Response Aggregation** - Combine similar responses
3. **Smart Routing** - Send to most relevant CIs only
4. **Caching** - Cache common responses

---

*Created by Jill on July 5, 2025 during team chat optimization with Casey*