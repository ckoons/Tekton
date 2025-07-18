# Integrating Hephaestus with the LLM Adapter

This document provides instructions for connecting the Hephaestus UI to the LLM Adapter.

## Overview

The Hephaestus UI needs to be modified to communicate with the LLM Adapter instead of using its built-in mock responses. This involves:

1. Adding WebSocket communication with the LLM Adapter
2. Updating the terminal chat interface to handle real LLM responses

## Prerequisites

- Tekton system is set up and running
- LLM Adapter is installed and configured
- Hephaestus UI is running as part of Tekton

## Integration Steps

### 1. Start the LLM Adapter

First, start the LLM Adapter service:

```bash
cd /Users/cskoons/projects/github/Tekton/LLMAdapter
./run_adapter.sh
```

Verify that the adapter is running by accessing http://localhost:8300 in your browser.

### 2. Modify the Hephaestus Hermes Connector

Edit the `hermes-connector.js` file in Hephaestus to communicate with the LLM Adapter:

1. Open `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/hermes-connector.js`
2. Locate the `sendLLMMessage` method 
3. Modify it to connect to the LLM Adapter WebSocket

Here's the implementation approach:

```javascript
// Add LLM Adapter configuration
const LLM_ADAPTER_CONFIG = {
    wsUrl: 'ws://localhost:8301',
    useStreaming: true,
    options: {
        temperature: 0.7
    }
};

// Add a WebSocket connection property
this.llmSocket = null;

// Modify the sendLLMMessage method
sendLLMMessage(contextId, message, streaming = true, options = {}) {
    console.log(`Sending LLM message in ${contextId} context: ${message.substring(0, 50)}...`);
    
    // Dispatch event to show typing indicator
    this.dispatchEvent('typingStarted', { contextId });
    
    // Create request data
    const llmRequest = {
        type: 'LLM_REQUEST',
        source: 'UI',
        target: 'LLM',
        timestamp: new Date().toISOString(),
        payload: {
            message: message,
            context: contextId,
            streaming: LLM_ADAPTER_CONFIG.useStreaming && streaming,
            options: {
                ...LLM_ADAPTER_CONFIG.options,
                ...options
            }
        }
    };
    
    // Check if WebSocket is already connected
    if (this.llmSocket && this.llmSocket.readyState === WebSocket.OPEN) {
        this.llmSocket.send(JSON.stringify(llmRequest));
    } else {
        this.connectToLLMAdapter(llmRequest);
    }
}

// Add a method to connect to the LLM Adapter
connectToLLMAdapter(initialRequest = null) {
    // Close existing connection if any
    if (this.llmSocket) {
        this.llmSocket.close();
    }
    
    // Create new connection
    this.llmSocket = new WebSocket(LLM_ADAPTER_CONFIG.wsUrl);
    
    // Set up event handlers
    this.llmSocket.onopen = () => {
        console.log("Connected to LLM Adapter");
        
        // Send initial request if any
        if (initialRequest) {
            this.llmSocket.send(JSON.stringify(initialRequest));
        }
    };
    
    this.llmSocket.onmessage = (event) => {
        try {
            // Handle messages from LLM Adapter
            const data = JSON.parse(event.data);
            
            if (data.type === 'UPDATE' && data.payload.chunk) {
                // Handle streaming chunk
                this.dispatchEvent('streamChunk', {
                    contextId: data.payload.context,
                    chunk: data.payload.chunk
                });
            } else if (data.type === 'UPDATE' && data.payload.done) {
                // Handle stream completion
                this.dispatchEvent('streamComplete', {
                    contextId: data.payload.context
                });
            } else if (data.type === 'RESPONSE' && data.payload.message) {
                // Handle complete message
                this.dispatchEvent('messageReceived', {
                    sender: data.source,
                    recipients: [data.target],
                    message: {
                        text: data.payload.message,
                        content: data.payload.message,
                        context: data.payload.context
                    }
                });
            } else if (data.type === 'UPDATE' && data.payload.status === 'typing') {
                // Handle typing status
                if (data.payload.isTyping) {
                    this.dispatchEvent('typingStarted', { 
                        contextId: data.payload.context 
                    });
                } else {
                    this.dispatchEvent('typingEnded', { 
                        contextId: data.payload.context 
                    });
                }
            } else if (data.type === 'ERROR') {
                // Handle error
                console.error("LLM Adapter error:", data.payload.error);
                this.dispatchEvent('messageReceived', {
                    sender: 'system',
                    recipients: ['user', 'terminal'],
                    message: {
                        text: `Error: ${data.payload.error}`,
                        type: 'error',
                        context: data.payload.context
                    }
                });
            }
        } catch (e) {
            console.error("Error handling LLM Adapter message:", e);
        }
    };
    
    this.llmSocket.onerror = (error) => {
        console.error("LLM Adapter connection error:", error);
    };
    
    this.llmSocket.onclose = () => {
        console.log("LLM Adapter connection closed");
    };
}
```

### 3. Test the Integration

Once the changes are made, you can test the integration:

1. Start the Tekton system: `tekton-launch`
2. Start the LLM Adapter: `cd /Users/cskoons/projects/github/Tekton/LLMAdapter && ./run_adapter.sh`
3. Open the Hephaestus UI in your browser: http://localhost:8080
4. Navigate to the Ergon tab and send a message
5. The message should be sent to the LLM Adapter, which will process it and return an LLM response

## Troubleshooting

If you encounter issues:

1. Check the browser console for WebSocket connection errors
2. Verify that the LLM Adapter is running and accessible
3. Check that the WebSocket URL is correct
4. Ensure the Anthropic API key is set correctly if using Claude

## Future Integration with Rhetor

This integration is temporary and will be replaced when Rhetor is implemented. Rhetor will:

1. Manage prompts and context
2. Select appropriate LLMs for different tasks
3. Handle advanced configurations and optimizations

The interface between Hephaestus and the LLM Adapter is designed to be compatible with Rhetor, so the transition should be smooth.