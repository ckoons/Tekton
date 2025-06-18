# Rhetor SSE Streaming Guide

## Overview

Phase 4A of the Rhetor AI Integration Sprint introduces real-time streaming support for AI responses using Server-Sent Events (SSE). This enables immediate feedback during long-running AI operations and provides progress indicators for better user experience.

## Features

### 1. SSE Streaming Endpoint
- **Endpoint**: `POST /api/mcp/v2/stream`
- **Purpose**: Execute MCP tools with real-time streaming responses
- **Benefits**: Immediate feedback, progress tracking, chunked responses

### 2. Streaming-Enabled Tools
Two AI orchestration tools now support streaming:
- `SendMessageToSpecialistStream`: Stream AI specialist responses in real-time
- `OrchestrateTeamChatStream`: Stream multi-specialist conversations as they happen

### 3. Progress Indicators
All tools (even non-streaming ones) now provide progress updates when called through the streaming endpoint:
- Connection status
- Processing stages (starting, processing, finalizing)
- Percentage completion
- Execution time tracking

## API Reference

### Streaming Request Format

```json
POST /api/mcp/v2/stream
Content-Type: application/json

{
  "tool_name": "SendMessageToSpecialistStream",
  "arguments": {
    "specialist_id": "rhetor-orchestrator",
    "message": "Your message here",
    "message_type": "chat"
  },
  "stream_options": {
    "include_progress": true,
    "chunk_size": "sentence"
  }
}
```

### SSE Event Types

The streaming endpoint sends various event types:

1. **connected**: Initial connection established
   ```
   event: connected
   data: {"tool_name": "...", "timestamp": ..., "message": "..."}
   ```

2. **progress**: Progress updates for long operations
   ```
   event: progress
   data: {"stage": "processing", "percentage": 50, "message": "..."}
   ```

3. **chunk**: Streaming content chunks
   ```
   event: chunk
   data: {"content": {"content": "...", "specialist": "...", "progress": 75}}
   ```

4. **message**: Team chat messages
   ```
   event: message
   data: {"speaker": "...", "content": "...", "round": 1}
   ```

5. **complete**: Operation completed
   ```
   event: complete
   data: {"result": {...}, "execution_time": 2.5, "timestamp": ...}
   ```

6. **error**: Error occurred
   ```
   event: error
   data: {"error": "...", "tool_name": "...", "timestamp": ...}
   ```

7. **disconnect**: Connection closing
   ```
   event: disconnect
   data: {"message": "Streaming connection closed", "timestamp": ...}
   ```

## Client Implementation

### Python Client Example

```python
import aiohttp
import json

async def stream_to_specialist(specialist_id, message):
    url = "http://localhost:8003/api/mcp/v2/stream"
    
    payload = {
        "tool_name": "SendMessageToSpecialistStream",
        "arguments": {
            "specialist_id": specialist_id,
            "message": message,
            "message_type": "chat"
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    print(f"Received: {data}")
```

### JavaScript Client Example

```javascript
async function streamToSpecialist(specialistId, message) {
    const response = await fetch('http://localhost:8003/api/mcp/v2/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            tool_name: 'SendMessageToSpecialistStream',
            arguments: {
                specialist_id: specialistId,
                message: message,
                message_type: 'chat'
            }
        })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data:')) {
                const data = JSON.parse(line.slice(5));
                console.log('Received:', data);
            }
        }
    }
}
```

### Using EventSource (Recommended for JavaScript)

```javascript
const eventSource = new EventSource('http://localhost:8003/api/mcp/v2/stream/test');

eventSource.addEventListener('progress', (event) => {
    const data = JSON.parse(event.data);
    console.log(`Progress: ${data.percentage}% - ${data.message}`);
});

eventSource.addEventListener('chunk', (event) => {
    const data = JSON.parse(event.data);
    console.log(`AI Response: ${data.content.content}`);
});

eventSource.addEventListener('complete', (event) => {
    const data = JSON.parse(event.data);
    console.log('Completed:', data.result);
    eventSource.close();
});
```

## Testing

### Quick Test
Test the basic streaming endpoint:
```bash
curl -N http://localhost:8003/api/mcp/v2/stream/test
```

### Python Test Script
Run the comprehensive test script:
```bash
python /Users/cskoons/projects/github/Tekton/Rhetor/tests/test_streaming.py
```

Options:
- `--test basic`: Test basic SSE functionality
- `--test specialist`: Test specialist message streaming
- `--test team`: Test team chat streaming
- `--test all`: Run all tests (default)

### Interactive HTML Client
Open the interactive client in a web browser:
```bash
open /Users/cskoons/projects/github/Tekton/Rhetor/examples/streaming_client.html
```

## Implementation Details

### Adding Streaming to New Tools

To make a tool support native streaming:

1. Import the streaming decorator:
   ```python
   from rhetor.core.mcp.streaming_tools import streaming_tool
   ```

2. Add the decorator and callback parameter:
   ```python
   @mcp_tool(name="YourToolName", ...)
   @streaming_tool
   async def your_tool_function(
       param1: str,
       param2: str,
       _stream_callback: Optional[Callable] = None
   ):
       if _stream_callback:
           # Send streaming updates
           await _stream_callback("progress", {"message": "Starting..."})
           # ... do work ...
           await _stream_callback("chunk", {"content": "Partial result"})
   ```

### Non-Streaming Tools

Tools without native streaming support automatically get:
- Progress indicators (starting, processing, finalizing)
- Execution time tracking
- Proper error handling

## Performance Considerations

1. **Connection Management**: SSE connections are long-lived. Ensure proper cleanup on client disconnect.

2. **Chunking Strategy**: The streaming tools split responses into meaningful chunks (sentences, paragraphs) rather than arbitrary byte boundaries.

3. **Progress Frequency**: Progress updates are throttled to avoid overwhelming clients with too many events.

4. **Error Recovery**: The streaming endpoint handles errors gracefully, sending error events before closing the connection.

## Troubleshooting

### Common Issues

1. **Connection Drops**: Check for proxy timeouts or firewall rules that may close long-lived connections.

2. **No Events Received**: Ensure the Content-Type header includes `text/event-stream` acceptance.

3. **Parsing Errors**: SSE data must be valid JSON after the `data:` prefix.

### Debug Logging

Enable debug logging to see streaming details:
```python
import logging
logging.getLogger("rhetor.api.fastmcp_endpoints").setLevel(logging.DEBUG)
```

## Future Enhancements

Planned improvements for streaming:
- WebSocket support for bidirectional streaming
- Streaming file uploads/downloads
- Real-time collaborative editing
- Stream compression for large responses

## Migration Guide

### Updating Existing Code

To use streaming with existing code:

1. Change the endpoint from `/api/mcp/v2/process` to `/api/mcp/v2/stream`
2. Update response handling to process SSE events instead of JSON
3. Add progress UI elements to show streaming updates

### Backward Compatibility

The original `/api/mcp/v2/process` endpoint remains unchanged. Streaming is opt-in via the new `/stream` endpoint.

## Examples

See the following files for complete examples:
- `/Rhetor/tests/test_streaming.py` - Python test client
- `/Rhetor/examples/streaming_client.html` - Interactive web client
- `/Rhetor/rhetor/core/mcp/streaming_tools.py` - Implementation reference