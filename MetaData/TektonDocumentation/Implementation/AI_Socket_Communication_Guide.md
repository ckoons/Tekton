# AI Socket Communication Guide

## Overview

This guide shows how to communicate with Tekton AI specialists from HTML/JavaScript using the socket-based protocol.

## Socket Communication Protocol

Each AI specialist listens on a TCP socket (ports 45000-50000) and communicates via JSON messages.

### Message Format

All messages are JSON objects followed by a newline character:

```json
{
  "type": "message_type",
  "content": "message content",
  "other_fields": "as needed"
}
```

## JavaScript Socket Client

Since browsers cannot directly connect to TCP sockets, you need a proxy or use the Rhetor API endpoints.

### Option 1: Direct Socket Connection (Node.js/Backend)

```javascript
const net = require('net');

class AISocketClient {
  constructor(port) {
    this.port = port;
    this.client = null;
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.client = new net.Socket();
      
      this.client.connect(this.port, 'localhost', () => {
        console.log(`Connected to AI on port ${this.port}`);
        resolve();
      });
      
      this.client.on('error', reject);
    });
  }

  sendMessage(message) {
    return new Promise((resolve, reject) => {
      const json = JSON.stringify(message) + '\n';
      this.client.write(json);
      
      this.client.once('data', (data) => {
        try {
          const response = JSON.parse(data.toString().trim());
          resolve(response);
        } catch (e) {
          reject(e);
        }
      });
    });
  }

  close() {
    if (this.client) {
      this.client.end();
    }
  }
}

// Usage
async function chatWithAI() {
  const client = new AISocketClient(45014); // numa-ai port
  
  try {
    await client.connect();
    
    // Send chat message
    const response = await client.sendMessage({
      type: 'chat',
      content: 'What is your role in Tekton?'
    });
    
    console.log('AI Response:', response.content);
    
    client.close();
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Option 2: WebSocket Proxy (Browser-Compatible)

Create a WebSocket proxy server that forwards to TCP sockets:

```javascript
// proxy-server.js (Node.js)
const WebSocket = require('ws');
const net = require('net');

const wss = new WebSocket.Server({ port: 8090 });

wss.on('connection', (ws) => {
  let tcpClient = null;
  
  ws.on('message', (message) => {
    const data = JSON.parse(message);
    
    if (data.action === 'connect') {
      tcpClient = new net.Socket();
      tcpClient.connect(data.port, 'localhost', () => {
        ws.send(JSON.stringify({ status: 'connected' }));
      });
      
      tcpClient.on('data', (tcpData) => {
        ws.send(tcpData.toString());
      });
    } else if (data.action === 'send' && tcpClient) {
      tcpClient.write(JSON.stringify(data.message) + '\n');
    }
  });
  
  ws.on('close', () => {
    if (tcpClient) {
      tcpClient.end();
    }
  });
});
```

Browser client:
```javascript
// In browser JavaScript
class AIWebSocketClient {
  constructor() {
    this.ws = new WebSocket('ws://localhost:8090');
    this.ready = false;
    
    this.ws.onopen = () => {
      this.ready = true;
    };
  }
  
  async connectToAI(port) {
    if (!this.ready) {
      throw new Error('WebSocket not ready');
    }
    
    return new Promise((resolve) => {
      this.ws.send(JSON.stringify({
        action: 'connect',
        port: port
      }));
      
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.status === 'connected') {
          resolve();
        }
      };
    });
  }
  
  async sendMessage(message) {
    return new Promise((resolve) => {
      this.ws.send(JSON.stringify({
        action: 'send',
        message: message
      }));
      
      this.ws.onmessage = (event) => {
        try {
          const response = JSON.parse(event.data);
          resolve(response);
        } catch (e) {
          // Handle non-JSON responses
        }
      };
    });
  }
}

// Usage in browser
async function chatFromBrowser() {
  const client = new AIWebSocketClient();
  
  // Wait for WebSocket to connect
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Connect to numa-ai
  await client.connectToAI(45014);
  
  // Send message
  const response = await client.sendMessage({
    type: 'chat',
    content: 'Hello from the browser!'
  });
  
  console.log('AI said:', response.content);
}
```

### Option 3: Use Rhetor HTTP API (Recommended)

The easiest way is to use Rhetor's HTTP endpoints:

```javascript
// In browser JavaScript
async function chatWithAI(message) {
  const response = await fetch('http://localhost:8003/api/v1/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      messages: [
        {"role": "user", "content": message}
      ]
    })
  });
  
  const data = await response.json();
  return data.content;
}

// Team chat with all AIs
async function teamChat(message) {
  const response = await fetch('http://localhost:8003/api/team-chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: message,
      moderation_mode: 'pass_through',
      timeout: 10.0
    })
  });
  
  const data = await response.json();
  return data.responses;
}

// Send to specific AI specialist
async function chatWithSpecialist(specialistId, message) {
  const response = await fetch('http://localhost:8003/api/ai/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      specialist_id: specialistId,  // e.g., 'apollo-coordinator'
      message: message,
      temperature: 0.7
    })
  });
  
  const data = await response.json();
  return data.response;
}
```

## HTML Integration Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>AI Chat Interface</title>
</head>
<body>
  <div class="chat-container" data-tekton-chat="ai-interface">
    <div class="chat-messages" id="messages">
      <!-- Messages appear here -->
    </div>
    
    <div class="chat-input-area">
      <select id="ai-selector">
        <option value="numa-ai">Numa - Specialist Orchestrator</option>
        <option value="athena-ai">Athena - Knowledge Weaver</option>
        <option value="apollo-ai">Apollo - Codebase Oracle</option>
        <option value="team-chat">Team Chat (All AIs)</option>
      </select>
      
      <input type="text" 
             id="chat-input" 
             placeholder="Ask the AI specialist..."
             onkeypress="if(event.key==='Enter') sendMessage()">
      
      <button onclick="sendMessage()">Send</button>
    </div>
  </div>

  <script>
    async function sendMessage() {
      const input = document.getElementById('chat-input');
      const aiSelector = document.getElementById('ai-selector');
      const messagesDiv = document.getElementById('messages');
      
      const message = input.value.trim();
      if (!message) return;
      
      // Add user message to chat
      messagesDiv.innerHTML += `
        <div class="message user-message">
          <strong>You:</strong> ${message}
        </div>
      `;
      
      input.value = '';
      
      try {
        let response;
        
        if (aiSelector.value === 'team-chat') {
          // Team chat
          const result = await teamChat(message);
          
          // Show responses from all AIs
          for (const [ai, resp] of Object.entries(result)) {
            messagesDiv.innerHTML += `
              <div class="message ai-message">
                <strong>${ai}:</strong> ${resp.content}
              </div>
            `;
          }
        } else {
          // Single AI chat
          response = await chatWithAI(aiSelector.value, message);
          
          messagesDiv.innerHTML += `
            <div class="message ai-message">
              <strong>${aiSelector.value}:</strong> ${response}
            </div>
          `;
        }
        
        // Scroll to bottom
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
      } catch (error) {
        console.error('Chat error:', error);
        messagesDiv.innerHTML += `
          <div class="message error-message">
            <strong>Error:</strong> Failed to communicate with AI
          </div>
        `;
      }
    }
    
    // Rhetor API functions
    async function chatWithAI(aiId, message) {
      // For general chat, use Rhetor's chat endpoint
      if (aiId === 'rhetor') {
        const response = await fetch('http://localhost:8003/api/v1/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            messages: [
              {"role": "user", "content": message}
            ]
          })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.content;
      }
      
      // For specific AI specialist, use the AI specialist endpoint
      const response = await fetch('http://localhost:8003/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          specialist_id: aiId,
          message: message,
          temperature: 0.7
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.response;
    }
    
    async function teamChat(message) {
      const response = await fetch('http://localhost:8003/api/team-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          timeout: 10.0
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.responses;
    }
  </script>

  <style>
    .chat-container {
      max-width: 800px;
      margin: 20px auto;
      border: 1px solid #ccc;
      border-radius: 8px;
      overflow: hidden;
    }
    
    .chat-messages {
      height: 400px;
      overflow-y: auto;
      padding: 20px;
      background: #f5f5f5;
    }
    
    .message {
      margin: 10px 0;
      padding: 10px;
      border-radius: 5px;
    }
    
    .user-message {
      background: #e3f2fd;
      text-align: right;
    }
    
    .ai-message {
      background: #f3e5f5;
    }
    
    .error-message {
      background: #ffebee;
      color: #c62828;
    }
    
    .chat-input-area {
      display: flex;
      padding: 10px;
      background: white;
      border-top: 1px solid #ccc;
    }
    
    #ai-selector {
      margin-right: 10px;
      padding: 5px;
    }
    
    #chat-input {
      flex: 1;
      padding: 8px;
      border: 1px solid #ddd;
      border-radius: 4px;
      margin-right: 10px;
    }
    
    button {
      padding: 8px 20px;
      background: #2196f3;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    
    button:hover {
      background: #1976d2;
    }
  </style>
</body>
</html>
```

## Message Types

### Standard Messages

1. **ping** - Health check
   ```json
   Request:  {"type": "ping"}
   Response: {"type": "pong", "ai_id": "numa-ai", "timestamp": 1234567890}
   ```

2. **health** - Detailed health status
   ```json
   Request:  {"type": "health"}
   Response: {
     "type": "health_response",
     "ai_id": "numa-ai",
     "status": "healthy",
     "component": "Numa",
     "model": "ollama:llama3.3:70b",
     "clients": 2
   }
   ```

3. **info** - AI information
   ```json
   Request:  {"type": "info"}
   Response: {
     "type": "info_response",
     "ai_id": "numa-ai",
     "component": "Numa",
     "description": "AI specialist for Numa",
     "model_provider": "ollama",
     "model_name": "llama3.3:70b",
     "system_prompt": "You are The Specialist Orchestrator...",
     "port": 45014
   }
   ```

4. **chat** - Chat message
   ```json
   Request:  {"type": "chat", "content": "What is your role?"}
   Response: {
     "type": "chat_response",
     "ai_id": "numa-ai",
     "content": "I am Numa, The Specialist Orchestrator. My role is..."
   }
   ```

## Best Practices

1. **Always handle errors** - AI might be unavailable or slow
2. **Set timeouts** - Don't wait forever for responses
3. **Show loading states** - AI responses can take time
4. **Cache connections** - Reuse socket connections when possible
5. **Use Rhetor API** - It handles routing and provides better browser compatibility

## Testing

To test AI communication:

```bash
# 1. Check AI is running
python3 scripts/enhanced_tekton_ai_status.py

# 2. Test with netcat (direct socket)
echo '{"type":"ping"}' | nc localhost 45014

# 3. Test with curl via Rhetor's chat endpoint
curl -X POST http://localhost:8003/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, who are you?"}
    ]
  }'

# 4. Test team chat
curl -X POST http://localhost:8003/api/team-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your specialties?",
    "timeout": 10.0
  }'

# 5. Test specific AI specialist
curl -X POST http://localhost:8003/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "specialist_id": "apollo-coordinator",
    "message": "Analyze the codebase"
  }'
```

## Troubleshooting

1. **Connection refused** - AI not running, check with `tekton-status`
2. **Timeout** - AI might be processing, increase timeout
3. **Invalid JSON** - Ensure proper JSON formatting
4. **CORS errors** - Configure Rhetor to allow browser origins