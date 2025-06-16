# Codex Integration Guide

This guide provides instructions for integrating other Tekton components with Codex, enabling cross-component communication and feature enhancement.

## Overview

Codex is an AI pair programming component based on Aider that can be integrated with other Tekton components to provide:

1. Code generation and editing capabilities
2. Programming assistance and guidance
3. File and repository management
4. Git integration

## Integration Methods

There are three primary methods for integrating with Codex:

1. **HTTP API Integration**: Direct API calls for command-like interactions
2. **WebSocket Integration**: Real-time interaction with streaming responses
3. **Event-Based Integration**: Using Tekton's internal event system

## HTTP API Integration

### Prerequisites

To integrate with Codex's HTTP API:

1. Ensure Codex is running in the Tekton environment
2. Use the base URL `http://localhost:8082` (or the appropriate port)
3. Use JSON for request/response payloads

### Key Endpoints

#### Check Status and Availability

```javascript
// JavaScript example
fetch('http://localhost:8082/api/codex/status')
  .then(response => response.json())
  .then(data => {
    if (data.status === 'active') {
      // Codex is available
      console.log('Codex is active:', data);
    }
  });
```

#### Send Code Generation Requests

```javascript
// JavaScript example
fetch('http://localhost:8082/api/codex/input', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'Generate a function to calculate Fibonacci numbers in Python'
  })
})
.then(response => response.json())
.then(data => console.log('Request sent:', data));
```

### Example: Integrating with Prometheus for Task Automation

```javascript
// In Prometheus component
async function generateCodeForTask(task) {
  // Formulate the code generation request based on task description
  const codeRequest = `Generate code for: ${task.description} in ${task.language}`;
  
  // Send to Codex
  const response = await fetch('http://localhost:8082/api/codex/input', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text: codeRequest
    })
  });
  
  // Process response
  const result = await response.json();
  return {
    requestSent: result.status === 'success',
    sessionId: result.session_id
  };
}
```

## WebSocket Integration

For real-time, streaming interactions with Codex, use the WebSocket API.

### Establishing a Connection

```javascript
// JavaScript example
const socket = new WebSocket('ws://localhost:8082/ws/codex');

socket.onopen = () => {
  console.log('Connected to Codex WebSocket');
};

socket.onclose = () => {
  console.log('Disconnected from Codex WebSocket');
};

socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### Receiving Messages

```javascript
socket.onmessage = (event) => {
  try {
    const message = JSON.parse(event.data);
    
    switch (message.type) {
      case 'output':
        // Handle output from Codex
        processOutput(message.content);
        break;
        
      case 'active_files':
        // Update file list
        updateFiles(message.content);
        break;
        
      case 'error':
        // Handle error
        displayError(message.content);
        break;
        
      // Handle other message types
    }
  } catch (error) {
    console.error('Error parsing message:', error);
  }
};

function processOutput(content) {
  // Extract code blocks, suggestions, etc.
  // Update UI or trigger actions based on the output
}
```

### Sending Requests

```javascript
// Start a session
socket.send(JSON.stringify({
  type: 'start_session',
  content: {
    timestamp: Date.now()
  }
}));

// Send input
function sendToCodex(text) {
  socket.send(JSON.stringify({
    type: 'input',
    content: text
  }));
}
```

### Example: Integrating with Terma for Code Generation

```javascript
// In Terma component
class CodexIntegration {
  constructor() {
    this.socket = null;
    this.callbacks = {
      output: [],
      error: [],
      filesUpdated: []
    };
    this.connect();
  }
  
  connect() {
    this.socket = new WebSocket('ws://localhost:8082/ws/codex');
    
    this.socket.onopen = () => {
      console.log('Connected to Codex');
    };
    
    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      switch (message.type) {
        case 'output':
          this.callbacks.output.forEach(cb => cb(message.content));
          break;
        case 'error':
          this.callbacks.error.forEach(cb => cb(message.content));
          break;
        case 'active_files':
          this.callbacks.filesUpdated.forEach(cb => cb(message.content));
          break;
      }
    };
    
    this.socket.onclose = () => {
      // Try to reconnect after a delay
      setTimeout(() => this.connect(), 5000);
    };
  }
  
  onOutput(callback) {
    this.callbacks.output.push(callback);
  }
  
  onError(callback) {
    this.callbacks.error.push(callback);
  }
  
  onFilesUpdated(callback) {
    this.callbacks.filesUpdated.push(callback);
  }
  
  sendCodeRequest(text) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type: 'input',
        content: text
      }));
      return true;
    }
    return false;
  }
}
```

## Event-Based Integration

Tekton supports internal event-based communication, which can be used to integrate with Codex.

### Publishing Events for Codex

```javascript
// In another component
window.dispatchEvent(new CustomEvent('codex-code-request', {
  detail: {
    text: 'Generate a function to...',
    source: 'component-name',
    requestId: 'unique-request-id'
  }
}));
```

### Subscribing to Codex Events

```javascript
// Listen for Codex responses
window.addEventListener('codex-response', (event) => {
  const { output, requestId, source } = event.detail;
  
  // Process the response
  if (requestId === expectedRequestId) {
    processCodexResponse(output);
  }
});
```

### Example: Integrating with Athena for Knowledge Graph Code Generation

```javascript
// In Athena component
class CodexKnowledgeIntegration {
  constructor() {
    this.requestMap = new Map();
    this.setupEventListeners();
  }
  
  setupEventListeners() {
    // Listen for Codex responses
    window.addEventListener('codex-response', (event) => {
      const { output, requestId } = event.detail;
      
      if (this.requestMap.has(requestId)) {
        const { resolve, reject, timeout } = this.requestMap.get(requestId);
        clearTimeout(timeout);
        this.requestMap.delete(requestId);
        resolve(output);
      }
    });
  }
  
  async generateGraphCode(entity, relationship) {
    const requestId = `graph-code-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const requestPromise = new Promise((resolve, reject) => {
      // Set timeout to handle no response
      const timeout = setTimeout(() => {
        if (this.requestMap.has(requestId)) {
          this.requestMap.delete(requestId);
          reject(new Error('Codex request timed out'));
        }
      }, 30000);
      
      this.requestMap.set(requestId, { resolve, reject, timeout });
    });
    
    // Dispatch event to Codex
    window.dispatchEvent(new CustomEvent('codex-code-request', {
      detail: {
        text: `Generate code to create a knowledge graph node for entity "${entity}" with relationship "${relationship}"`,
        source: 'athena',
        requestId: requestId
      }
    }));
    
    return requestPromise;
  }
}
```

## Integration with Hermes

Codex registers with Hermes for service discovery. Other components can discover Codex through Hermes.

### Retrieving Codex Capabilities

```javascript
// JavaScript example
async function getCodexCapabilities() {
  const response = await fetch('http://localhost:8080/api/hermes/services/codex');
  const data = await response.json();
  
  return data.capabilities; // Returns array of capabilities
}
```

### Example: Dynamic Capability Discovery

```javascript
// In any Tekton component
async function checkCodexAvailability() {
  try {
    const response = await fetch('http://localhost:8080/api/hermes/services/codex');
    
    if (response.ok) {
      const data = await response.json();
      
      // Check for specific capabilities
      const hasCodeGeneration = data.capabilities.includes('code_generation');
      const hasAiPairProgramming = data.capabilities.includes('ai_pair_programming');
      
      // Enable features based on capabilities
      if (hasCodeGeneration) {
        enableCodeGenerationFeatures();
      }
      
      if (hasAiPairProgramming) {
        enablePairProgrammingFeatures();
      }
      
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error checking Codex availability:', error);
    return false;
  }
}
```

## Best Practices

### Handling Large Responses

Codex may generate large amounts of output for complex requests. To handle this:

1. When using WebSockets, process output incrementally as it arrives
2. Implement throttling for rapid sequences of requests
3. Consider batching related code generation requests

```javascript
// Example of incremental processing
let currentResponse = '';

socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'output') {
    // Append to existing response
    currentResponse += message.content;
    
    // Process incrementally
    processIncrementalOutput(message.content);
    
    // Check for completion patterns
    if (isResponseComplete(currentResponse)) {
      finalizeResponse(currentResponse);
      currentResponse = '';
    }
  }
};
```

### Error Handling

Implement robust error handling when integrating with Codex:

1. Handle connection errors and interruptions
2. Implement timeouts for requests
3. Provide fallback mechanisms when Codex is unavailable

```javascript
// Example of error handling with fallback
async function generateCode(prompt) {
  try {
    // Try to use Codex
    const response = await fetch('http://localhost:8082/api/codex/input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: prompt })
    });
    
    if (!response.ok) {
      throw new Error('Codex request failed');
    }
    
    return await response.json();
    
  } catch (error) {
    console.error('Error using Codex:', error);
    
    // Fallback to alternative method
    return fallbackCodeGeneration(prompt);
  }
}
```

### Session Management

Respect Codex's session model:

1. Avoid starting unnecessary new sessions
2. Reuse existing sessions when possible
3. Properly close sessions when finished

```javascript
// Example of session management
class CodexSessionManager {
  constructor() {
    this.activeSession = null;
    this.pendingRequests = [];
  }
  
  async ensureSession() {
    // Check if there's an active session
    const response = await fetch('http://localhost:8082/api/codex/status');
    const data = await response.json();
    
    if (!data.session_active) {
      // Start a new session
      await fetch('http://localhost:8082/api/codex/start', {
        method: 'POST'
      });
    }
  }
  
  async sendRequest(text) {
    await this.ensureSession();
    
    // Send the request
    return fetch('http://localhost:8082/api/codex/input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
  }
  
  async releaseSession() {
    if (this.pendingRequests.length === 0) {
      // No more pending requests, can release the session
      await fetch('http://localhost:8082/api/codex/stop', {
        method: 'POST'
      });
    }
  }
}
```

## Advanced Integration Examples

### Dialog-Based Code Generation

```javascript
// Example: Multi-turn code generation dialog
class CodeDialogSession {
  constructor() {
    this.socket = new WebSocket('ws://localhost:8082/ws/codex');
    this.sessionId = null;
    this.conversation = [];
    
    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === 'session_status' && message.content.active) {
        this.sessionId = message.content.session_id;
      }
      
      if (message.type === 'output') {
        this.conversation.push({
          role: 'assistant',
          content: message.content
        });
        
        this.onOutputCallback?.(message.content);
      }
    };
  }
  
  onOutput(callback) {
    this.onOutputCallback = callback;
  }
  
  async sendMessage(text) {
    this.conversation.push({
      role: 'user',
      content: text
    });
    
    this.socket.send(JSON.stringify({
      type: 'input',
      content: text
    }));
  }
  
  getConversationContext() {
    return this.conversation;
  }
}
```

### File Synchronization

```javascript
// Example: Synchronizing edited files with another component
class CodexFileSyncIntegration {
  constructor(targetComponent) {
    this.targetComponent = targetComponent;
    this.activeFiles = new Set();
    this.socket = new WebSocket('ws://localhost:8082/ws/codex');
    
    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === 'active_files') {
        // Track which files are being edited
        const newFiles = new Set(message.content);
        
        // Find files that were added
        const addedFiles = message.content.filter(file => !this.activeFiles.has(file));
        
        // Find files that were removed
        const removedFiles = Array.from(this.activeFiles)
          .filter(file => !newFiles.has(file));
        
        // Update local tracking
        this.activeFiles = newFiles;
        
        // Notify target component about changes
        if (addedFiles.length > 0) {
          this.targetComponent.onFilesAdded?.(addedFiles);
        }
        
        if (removedFiles.length > 0) {
          this.targetComponent.onFilesRemoved?.(removedFiles);
        }
      }
    };
  }
  
  requestFocus(filename) {
    this.socket.send(JSON.stringify({
      type: 'input',
      content: `/focus ${filename}`
    }));
  }
}
```

## Troubleshooting

### Common Integration Issues

1. **Connection Refused**
   - Ensure Codex is running (`ps aux | grep codex_server`)
   - Verify the correct port is being used (default: 8082)
   - Check for port conflicts

2. **Message Format Errors**
   - Ensure all messages follow the correct JSON format
   - Validate message types match the expected values

3. **Session Management Issues**
   - If responses are inconsistent, check if multiple sessions are being created
   - Ensure sessions are properly managed and not abandoned

4. **Cross-Origin Issues**
   - For browser-based integrations, ensure CORS is properly configured
   - The Codex server allows all origins by default for local development

### Debugging Tools

1. **WebSocket Inspection**
   - Use browser DevTools to inspect WebSocket traffic
   - Monitor the Network tab to see WebSocket frames

2. **Logging**
   - Enable verbose logging in your integration
   - Check Codex logs at `~/.tekton/logs/codex.log`

3. **Status Endpoint**
   - Regularly poll the status endpoint to check component health
   - Use it for debugging session state issues

## Conclusion

Integrating with Codex enables your Tekton component to leverage powerful AI pair programming capabilities. Whether through HTTP APIs, WebSockets, or event-based communication, Codex can enhance your component with code generation, editing, and analysis features.

For additional assistance or specific integration scenarios, refer to the [Codex Technical Documentation](../TECHNICAL_DOCUMENTATION.md) or contact the Tekton development team.