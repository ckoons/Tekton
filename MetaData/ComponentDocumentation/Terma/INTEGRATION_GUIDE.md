# Terma Integration Guide

This guide provides detailed information on integrating Terma with other Tekton components and external systems.

## Overview

Terma is designed to integrate seamlessly with the Tekton ecosystem through:

1. **Hermes Integration**: Service registration and discovery
2. **LLM Adapter**: Integration with CI services
3. **Hephaestus UI**: Web component integration
4. **HTTP API**: REST API for programmatic access
5. **WebSocket API**: Real-time communication
6. **Single Port Architecture**: Standardized communication patterns

## Integration with Tekton Components

### Hermes Integration

Terma registers with Hermes to enable service discovery and message passing:

```python
# Registration with Hermes
from hermes.api.client import HermesClient

async def register_with_hermes():
    client = HermesClient(base_url="http://localhost:8000/api")
    
    service_data = {
        "component_id": "terma",
        "service_id": "terma.terminal",
        "name": "Terma Terminal Service",
        "description": "Terminal service for the Tekton ecosystem",
        "capabilities": ["terminal", "terminal_assistance", "shell_execution"],
        "endpoints": {
            "http": "http://localhost:8767/api",
            "ws": "ws://localhost:8767/ws",
            "ui": "http://localhost:8767/terminal/launch"
        },
        "metadata": {
            "supports_llm_assistance": True,
            "ui_component": "terma-terminal"
        }
    }
    
    result = await client.register_service(service_data)
    return result.get("success", False)
```

#### Event Communication

Terma can publish events and subscribe to events from other components:

```python
# Publish event
async def publish_session_created_event(session_id):
    event = {
        "event_type": "terma.session.created",
        "source": "terma.terminal",
        "timestamp": datetime.now().isoformat(),
        "payload": {
            "session_id": session_id,
            "created_at": datetime.now().isoformat()
        }
    }
    
    result = await hermes_client.publish_event(event)
    return result.get("success", False)

# Subscribe to events
async def subscribe_to_events():
    event_types = [
        "tekton.startup.complete",
        "tekton.shutdown.initiated"
    ]
    
    result = await hermes_client.subscribe_to_events(
        service_id="terma.terminal", 
        event_types=event_types
    )
    return result.get("success", False)
```

### LLM Adapter Integration

Terma integrates with Tekton's LLM Adapter for CI assistance capabilities:

```python
from tekton_llm_client import TektonLLMClient

class LLMAdapter:
    def __init__(self):
        self.client = None
        self.default_provider = os.environ.get("TERMA_LLM_PROVIDER", "rhetor")
        self.default_model = os.environ.get("TERMA_LLM_MODEL", None)
    
    async def initialize(self):
        self.client = TektonLLMClient()
        await self.client.initialize()
        
        # Get available providers
        providers = await self.client.list_providers()
        self.providers = {p["id"]: p for p in providers}
        
        return bool(self.providers)
    
    async def get_assistance(self, query, context=None, model=None, stream=False):
        # Prepare prompt
        prompt = self._prepare_terminal_prompt(query, context)
        
        # Use specified model or default
        provider = self.default_provider
        provider_model = model or self.default_model
        
        if stream:
            return self._stream_completion(prompt, provider, provider_model)
        else:
            return await self._get_completion(prompt, provider, provider_model)
```

#### Fallback Mechanisms

Terma implements fallback mechanisms for when the preferred LLM services are unavailable:

```python
class RhetorFallbackClient:
    """Fallback client for direct Rhetor connection."""
    
    def __init__(self):
        self.base_url = os.environ.get("RHETOR_URL", "http://localhost:8003/api")
        self.client = None
    
    async def initialize(self):
        # Create HTTP client
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)
        return True
    
    async def generate_completion(self, prompt, provider=None, model=None, **kwargs):
        # Simplified request to Rhetor
        response = await self.client.post("/completions", json={
            "prompt": prompt,
            "model": model,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7)
        })
        
        response.raise_for_status()
        data = response.json()
        
        # Return in standard format
        return CompletionResponse(
            completion=data.get("text", ""),
            model=data.get("model", "unknown"),
            usage=data.get("usage", {})
        )
```

### Hephaestus UI Integration

Terma provides a web component that can be integrated into the Hephaestus UI:

#### Component Registration

```javascript
// Register Terma component with Hephaestus
document.addEventListener('DOMContentLoaded', function() {
    if (window.HephaestusComponentRegistry) {
        window.HephaestusComponentRegistry.register({
            name: 'terma-terminal',
            displayName: 'Terminal',
            description: 'Interactive terminal with LLM assistance',
            icon: 'terminal',
            component: 'terma-terminal',
            scriptSrc: '/terminal/static/js/terma-terminal.js',
            styleSrc: '/terminal/static/css/terma-terminal.css',
            defaultConfig: {
                theme: 'dark',
                fontSize: 14,
                showAssistButton: true
            }
        });
    }
});
```

#### Component Usage in Hephaestus

```html
<!-- Basic usage -->
<terma-terminal></terma-terminal>

<!-- Advanced configuration -->
<terma-terminal
  id="myTerminal"
  theme="dark"
  font-size="14"
  shell-command="/bin/bash"
  initial-directory="/home/user/projects"
  show-assist-button="true">
</terma-terminal>
```

#### State Integration

```javascript
// Integrate with Hephaestus state management
class TermaStateManager {
    constructor() {
        this.stateManager = null;
    }
    
    initialize(stateManager) {
        this.stateManager = stateManager;
        
        // Register state
        this.stateManager.registerState('terma', {
            ready: false,
            sessions: [],
            activeSession: null,
            connectionStatus: 'disconnected',
            lastError: null
        });
        
        // Mark as ready
        this.stateManager.updateState('terma', { ready: true });
        
        return true;
    }
    
    updateSessionList(sessions) {
        this.stateManager.updateState('terma', { 
            sessions: sessions 
        });
    }
    
    setActiveSession(sessionId) {
        this.stateManager.updateState('terma', { 
            activeSession: sessionId 
        });
    }
    
    updateConnectionStatus(status) {
        this.stateManager.updateState('terma', { 
            connectionStatus: status 
        });
    }
    
    handleError(error) {
        this.stateManager.updateState('terma', { 
            lastError: error 
        });
    }
}
```

## Single Port Architecture

Terma follows the Tekton Single Port Architecture pattern for consolidated communication:

### Path-Based Routing

```
Terma Service (Port 8767)
├── /api/*            - REST API endpoints
├── /ws/{session_id}  - WebSocket endpoint for terminal I/O
└── /terminal/*       - UI endpoints
    ├── /launch       - Terminal UI application
    ├── /component    - Terminal web component
    └── /static/*     - Static assets
```

### Environment Variables

```bash
# Configure Terma port
export TERMA_PORT=8767
export TERMA_HOST=0.0.0.0

# Configure Hermes URL
export HERMES_URL=http://localhost:8000/api

# Configure LLM provider
export TERMA_LLM_PROVIDER=rhetor
export TERMA_LLM_MODEL=claude-3-sonnet-20240229
```

### URL Construction

```javascript
// Construct URL for Terma API
function getTermaApiUrl(endpoint) {
    const host = process.env.TERMA_HOST || 'localhost';
    const port = process.env.TERMA_PORT || '8767';
    return `http://${host}:${port}/api/${endpoint}`;
}

// Construct WebSocket URL
function getTermaWebSocketUrl(sessionId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.TERMA_HOST || window.location.hostname;
    const port = process.env.TERMA_PORT || '8767';
    return `${protocol}//${host}:${port}/ws/${sessionId}`;
}
```

## Client Libraries

### Python Client

```python
class TermaClient:
    """Client for interacting with the Terma API."""
    
    def __init__(self, base_url=None):
        """Initialize the client."""
        self.base_url = base_url or "http://localhost:8767/api"
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        self.ws_connections = {}
    
    async def create_session(self, shell_command=None, cwd=None, env=None, cols=80, rows=24):
        """Create a new terminal session."""
        response = await self.client.post("/sessions", json={
            "shell_command": shell_command,
            "cwd": cwd,
            "env": env,
            "cols": cols,
            "rows": rows
        })
        response.raise_for_status()
        return response.json()
    
    async def list_sessions(self):
        """List all terminal sessions."""
        response = await self.client.get("/sessions")
        response.raise_for_status()
        return response.json()
    
    async def get_session(self, session_id):
        """Get a terminal session by ID."""
        response = await self.client.get(f"/sessions/{session_id}")
        response.raise_for_status()
        return response.json()
    
    async def close_session(self, session_id):
        """Close a terminal session."""
        response = await self.client.delete(f"/sessions/{session_id}")
        response.raise_for_status()
        return response.json()
    
    async def send_input(self, session_id, data):
        """Send input to a terminal session."""
        response = await self.client.post(f"/sessions/{session_id}/input", json={
            "data": data
        })
        response.raise_for_status()
        return response.json()
    
    async def get_output(self, session_id, timeout=0.1):
        """Get output from a terminal session."""
        response = await self.client.get(
            f"/sessions/{session_id}/output",
            params={"timeout": timeout}
        )
        response.raise_for_status()
        return response.json()
    
    async def resize_terminal(self, session_id, cols, rows):
        """Resize a terminal session."""
        response = await self.client.post(f"/sessions/{session_id}/resize", json={
            "cols": cols,
            "rows": rows
        })
        response.raise_for_status()
        return response.json()
    
    async def get_llm_assistance(self, session_id, query, context=None, model=None):
        """Get LLM assistance for a terminal query."""
        response = await self.client.post(f"/sessions/{session_id}/llm-assist", json={
            "query": query,
            "context": context,
            "model": model
        })
        response.raise_for_status()
        return response.json()
    
    async def connect_websocket(self, session_id, message_callback=None):
        """Connect to a terminal session via WebSocket."""
        if session_id in self.ws_connections:
            return
        
        # Determine WebSocket URL
        ws_url = self.base_url.replace("http", "ws").replace("/api", f"/ws/{session_id}")
        
        # Create WebSocket connection
        ws = await websockets.connect(ws_url)
        
        # Store connection
        self.ws_connections[session_id] = {
            "ws": ws,
            "callback": message_callback,
            "task": None
        }
        
        # Start message handler task
        if message_callback:
            self.ws_connections[session_id]["task"] = asyncio.create_task(
                self._handle_websocket_messages(session_id, ws, message_callback)
            )
        
        return ws
    
    async def _handle_websocket_messages(self, session_id, ws, callback):
        """Handle WebSocket messages."""
        try:
            async for message in ws:
                try:
                    data = json.loads(message)
                    await callback(session_id, data)
                except json.JSONDecodeError:
                    continue
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if session_id in self.ws_connections:
                del self.ws_connections[session_id]
    
    async def send_websocket_message(self, session_id, message):
        """Send a message to a WebSocket connection."""
        if session_id not in self.ws_connections:
            raise ValueError(f"No WebSocket connection for session {session_id}")
        
        ws = self.ws_connections[session_id]["ws"]
        await ws.send(json.dumps(message))
    
    async def disconnect_websocket(self, session_id):
        """Disconnect a WebSocket connection."""
        if session_id in self.ws_connections:
            connection = self.ws_connections[session_id]
            
            # Cancel task
            if connection["task"]:
                connection["task"].cancel()
                try:
                    await connection["task"]
                except asyncio.CancelledError:
                    pass
            
            # Close WebSocket
            await connection["ws"].close()
            
            # Remove from connections
            del self.ws_connections[session_id]
    
    async def close(self):
        """Close the client."""
        # Close all WebSocket connections
        for session_id in list(self.ws_connections.keys()):
            await self.disconnect_websocket(session_id)
        
        # Close HTTP client
        await self.client.aclose()
```

### JavaScript Client

```javascript
class TermaClient {
    /**
     * Client for interacting with the Terma API.
     * @param {string} baseUrl - The base URL for the API
     */
    constructor(baseUrl = 'http://localhost:8767/api') {
        this.baseUrl = baseUrl;
        this.wsConnections = {};
    }
    
    /**
     * Create a new terminal session.
     * @param {Object} options - Session options
     * @returns {Promise<Object>} Session data
     */
    async createSession(options = {}) {
        const response = await fetch(`${this.baseUrl}/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                shell_command: options.shellCommand,
                cwd: options.cwd,
                env: options.env,
                cols: options.cols || 80,
                rows: options.rows || 24
            })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to create session: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * List all terminal sessions.
     * @returns {Promise<Object>} List of sessions
     */
    async listSessions() {
        const response = await fetch(`${this.baseUrl}/sessions`);
        
        if (!response.ok) {
            throw new Error(`Failed to list sessions: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Get a terminal session by ID.
     * @param {string} sessionId - The session ID
     * @returns {Promise<Object>} Session data
     */
    async getSession(sessionId) {
        const response = await fetch(`${this.baseUrl}/sessions/${sessionId}`);
        
        if (!response.ok) {
            throw new Error(`Failed to get session: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Close a terminal session.
     * @param {string} sessionId - The session ID
     * @returns {Promise<Object>} Result
     */
    async closeSession(sessionId) {
        const response = await fetch(`${this.baseUrl}/sessions/${sessionId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`Failed to close session: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Send input to a terminal session.
     * @param {string} sessionId - The session ID
     * @param {string} data - The input data
     * @returns {Promise<Object>} Result
     */
    async sendInput(sessionId, data) {
        const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/input`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to send input: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Get output from a terminal session.
     * @param {string} sessionId - The session ID
     * @param {number} timeout - Timeout in seconds
     * @returns {Promise<Object>} Output data
     */
    async getOutput(sessionId, timeout = 0.1) {
        const response = await fetch(
            `${this.baseUrl}/sessions/${sessionId}/output?timeout=${timeout}`
        );
        
        if (!response.ok) {
            throw new Error(`Failed to get output: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Resize a terminal session.
     * @param {string} sessionId - The session ID
     * @param {number} cols - Terminal width in columns
     * @param {number} rows - Terminal height in rows
     * @returns {Promise<Object>} Result
     */
    async resizeTerminal(sessionId, cols, rows) {
        const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/resize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cols, rows })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to resize terminal: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Get LLM assistance for a terminal query.
     * @param {string} sessionId - The session ID
     * @param {string} query - The query for the LLM
     * @param {string} context - Optional additional context
     * @param {string} model - The LLM model to use
     * @returns {Promise<Object>} LLM response
     */
    async getLlmAssistance(sessionId, query, context = null, model = null) {
        const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/llm-assist`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, context, model })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to get LLM assistance: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Connect to a terminal session via WebSocket.
     * @param {string} sessionId - The session ID
     * @param {Function} messageCallback - Callback for incoming messages
     * @returns {WebSocket} WebSocket connection
     */
    connectWebSocket(sessionId, messageCallback = null) {
        if (this.wsConnections[sessionId]) {
            return this.wsConnections[sessionId];
        }
        
        // Determine WebSocket URL
        const wsUrl = this.baseUrl
            .replace('http', 'ws')
            .replace('/api', `/ws/${sessionId}`);
        
        // Create WebSocket connection
        const ws = new WebSocket(wsUrl);
        
        // Store connection
        this.wsConnections[sessionId] = ws;
        
        // Set up event handlers
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (messageCallback) {
                    messageCallback(sessionId, data);
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        ws.onclose = () => {
            if (this.wsConnections[sessionId] === ws) {
                delete this.wsConnections[sessionId];
            }
        };
        
        return ws;
    }
    
    /**
     * Send a message to a WebSocket connection.
     * @param {string} sessionId - The session ID
     * @param {Object} message - The message to send
     */
    sendWebSocketMessage(sessionId, message) {
        if (!this.wsConnections[sessionId]) {
            throw new Error(`No WebSocket connection for session ${sessionId}`);
        }
        
        this.wsConnections[sessionId].send(JSON.stringify(message));
    }
    
    /**
     * Disconnect a WebSocket connection.
     * @param {string} sessionId - The session ID
     */
    disconnectWebSocket(sessionId) {
        if (this.wsConnections[sessionId]) {
            this.wsConnections[sessionId].close();
            delete this.wsConnections[sessionId];
        }
    }
    
    /**
     * Close the client.
     */
    close() {
        // Close all WebSocket connections
        Object.keys(this.wsConnections).forEach(sessionId => {
            this.disconnectWebSocket(sessionId);
        });
    }
}
```

## Integration Examples

### Basic Terminal Integration

```javascript
// Create a basic terminal integration
async function integrateTerminal(containerElement) {
    // Create Terma client
    const client = new TermaClient();
    
    // Create session
    const session = await client.createSession({
        shellCommand: '/bin/bash',
        cols: 80,
        rows: 24
    });
    
    // Store session ID
    const sessionId = session.session_id;
    
    // Create terminal UI
    const terminal = new Terminal({
        cols: 80,
        rows: 24,
        fontFamily: 'monospace',
        fontSize: 14,
        theme: {
            background: '#1e1e1e',
            foreground: '#f0f0f0'
        }
    });
    
    // Open terminal in container
    terminal.open(containerElement);
    
    // Connect to WebSocket
    const ws = client.connectWebSocket(sessionId, (_, message) => {
        if (message.type === 'output') {
            terminal.write(message.data);
        }
    });
    
    // Handle input
    terminal.onData(data => {
        client.sendWebSocketMessage(sessionId, {
            type: 'input',
            data: data
        });
    });
    
    // Handle resize
    terminal.onResize(({ cols, rows }) => {
        client.sendWebSocketMessage(sessionId, {
            type: 'resize',
            cols: cols,
            rows: rows
        });
    });
    
    // Clean up function
    return () => {
        client.disconnectWebSocket(sessionId);
        client.closeSession(sessionId);
        terminal.dispose();
    };
}
```

### LLM-Assisted Terminal

```javascript
// Create an LLM-assisted terminal
async function integrateLlmTerminal(containerElement, assistContainer) {
    // Create Terma client
    const client = new TermaClient();
    
    // Create session
    const session = await client.createSession();
    const sessionId = session.session_id;
    
    // Create terminal UI
    const terminal = new Terminal({
        fontFamily: 'monospace',
        fontSize: 14
    });
    
    terminal.open(containerElement);
    
    // Connect to WebSocket
    client.connectWebSocket(sessionId, (_, message) => {
        if (message.type === 'output') {
            terminal.write(message.data);
        } else if (message.type === 'llm_response') {
            showLlmResponse(assistContainer, message.data);
        }
    });
    
    // Handle input
    terminal.onData(data => {
        client.sendWebSocketMessage(sessionId, {
            type: 'input',
            data: data
        });
    });
    
    // Create assist function
    const getLlmAssistance = (query) => {
        client.sendWebSocketMessage(sessionId, {
            type: 'llm_assist',
            data: query
        });
    };
    
    // Return interface
    return {
        terminal,
        getLlmAssistance,
        dispose: () => {
            client.disconnectWebSocket(sessionId);
            client.closeSession(sessionId);
            terminal.dispose();
        }
    };
}

// Display LLM response
function showLlmResponse(container, markdown) {
    // Render markdown
    container.innerHTML = marked.parse(markdown);
    
    // Highlight code blocks
    container.querySelectorAll('pre code').forEach(block => {
        hljs.highlightBlock(block);
    });
}
```

### Web Component Integration

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terma Web Component Integration</title>
    <script src="/terminal/static/js/terma-terminal.js"></script>
    <link rel="stylesheet" href="/terminal/static/css/terma-terminal.css">
    <style>
        body, html {
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        .container {
            display: flex;
            flex-direction: column;
            height: 100%;
            padding: 16px;
            box-sizing: border-box;
        }
        .terminal-container {
            flex: 1;
            min-height: 300px;
            border: 1px solid #ccc;
            border-radius: 4px;
            overflow: hidden;
        }
        .controls {
            margin-top: 16px;
            display: flex;
            gap: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Terma Terminal Integration</h1>
        
        <div class="terminal-container">
            <terma-terminal
                id="terminal"
                theme="dark"
                font-size="14"
                auto-connect="true"
                show-assist-button="true">
            </terma-terminal>
        </div>
        
        <div class="controls">
            <button id="newSession">New Session</button>
            <button id="clearTerminal">Clear Terminal</button>
            <button id="assistButton">Ask Assistant</button>
            <select id="themeSelect">
                <option value="dark">Dark Theme</option>
                <option value="light">Light Theme</option>
            </select>
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const terminal = document.getElementById('terminal');
            
            // Handle terminal events
            terminal.addEventListener('terminalReady', function(event) {
                console.log('Terminal ready:', event.detail);
            });
            
            terminal.addEventListener('terminalConnected', function(event) {
                console.log('Terminal connected:', event.detail);
            });
            
            terminal.addEventListener('llmResponse', function(event) {
                console.log('LLM response:', event.detail);
            });
            
            // Handle button clicks
            document.getElementById('newSession').addEventListener('click', function() {
                terminal.createSession();
            });
            
            document.getElementById('clearTerminal').addEventListener('click', function() {
                terminal.clear();
            });
            
            document.getElementById('assistButton').addEventListener('click', function() {
                const query = prompt('How can I help you with the terminal?');
                if (query) {
                    terminal.getLlmAssistance(query);
                }
            });
            
            // Handle theme selection
            document.getElementById('themeSelect').addEventListener('change', function() {
                terminal.setTheme(this.value);
            });
        });
    </script>
</body>
</html>
```

## External System Integration

### Integration with Text Editors and IDEs

```javascript
class TermaEditorIntegration {
    constructor(options = {}) {
        this.client = new TermaClient(options.baseUrl);
        this.sessionId = null;
        this.terminal = null;
        this.editor = options.editor;
    }
    
    async initialize() {
        // Create session
        const session = await this.client.createSession({
            shellCommand: options.shellCommand,
            cwd: options.workingDirectory
        });
        
        this.sessionId = session.session_id;
        
        // Create terminal in editor container
        this.terminal = new Terminal({
            fontSize: options.fontSize || 14,
            fontFamily: options.fontFamily || 'monospace',
            theme: this.getTheme(options.theme)
        });
        
        this.terminal.open(options.container);
        
        // Connect WebSocket
        this.client.connectWebSocket(this.sessionId, (_, message) => {
            if (message.type === 'output') {
                this.terminal.write(message.data);
            }
        });
        
        // Handle input
        this.terminal.onData(data => {
            this.client.sendWebSocketMessage(this.sessionId, {
                type: 'input',
                data: data
            });
        });
        
        // Add commands to editor
        this.registerEditorCommands();
        
        return this;
    }
    
    registerEditorCommands() {
        // Run current file
        this.editor.addCommand('terma.runCurrentFile', () => {
            const filePath = this.editor.getCurrentFilePath();
            this.runFile(filePath);
        });
        
        // Run selected text
        this.editor.addCommand('terma.runSelectedText', () => {
            const text = this.editor.getSelectedText();
            this.runCode(text);
        });
        
        // Toggle terminal
        this.editor.addCommand('terma.toggleTerminal', () => {
            this.toggleTerminal();
        });
    }
    
    runFile(filePath) {
        if (!this.sessionId) return;
        
        const command = this.getRunCommand(filePath);
        this.client.sendWebSocketMessage(this.sessionId, {
            type: 'input',
            data: `${command}\n`
        });
    }
    
    runCode(code) {
        if (!this.sessionId) return;
        
        // Use heredoc for multi-line code
        const command = `cat << 'EOF' | bash\n${code}\nEOF\n`;
        this.client.sendWebSocketMessage(this.sessionId, {
            type: 'input',
            data: command
        });
    }
    
    toggleTerminal() {
        const container = this.terminal.element.parentElement;
        container.style.display = container.style.display === 'none' ? 'block' : 'none';
    }
    
    getRunCommand(filePath) {
        // Determine command based on file extension
        const ext = filePath.split('.').pop().toLowerCase();
        
        switch (ext) {
            case 'js': return `node "${filePath}"`;
            case 'py': return `python "${filePath}"`;
            case 'sh': return `bash "${filePath}"`;
            case 'rb': return `ruby "${filePath}"`;
            case 'php': return `php "${filePath}"`;
            case 'ts': return `ts-node "${filePath}"`;
            case 'java': return `java "${filePath}"`;
            case 'go': return `go run "${filePath}"`;
            case 'rust': case 'rs': return `rustc "${filePath}" && ./a.out`;
            default: return `cat "${filePath}"`;
        }
    }
    
    getTheme(theme) {
        return theme === 'light' ? {
            background: '#ffffff',
            foreground: '#333333',
            cursor: '#333333'
        } : {
            background: '#1e1e1e',
            foreground: '#f0f0f0',
            cursor: '#f0f0f0'
        };
    }
    
    dispose() {
        if (this.sessionId) {
            this.client.disconnectWebSocket(this.sessionId);
            this.client.closeSession(this.sessionId);
        }
        
        if (this.terminal) {
            this.terminal.dispose();
        }
        
        this.client.close();
    }
}
```

### CI/CD Integration

```bash
#!/bin/bash
# Example script for CI/CD integration with Terma

# Start a headless terminal session
SESSION_ID=$(curl -s -X POST http://localhost:8767/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"shell_command": "/bin/bash", "cwd": "'$PWD'"}' | jq -r '.session_id')

echo "Created terminal session: $SESSION_ID"

# Function to send commands to the terminal
send_command() {
  curl -s -X POST http://localhost:8767/api/sessions/$SESSION_ID/input \
    -H "Content-Type: application/json" \
    -d '{"data": "'"$1"'\n"}'
  
  # Wait for command to complete
  sleep 2
  
  # Get output
  OUTPUT=$(curl -s "http://localhost:8767/api/sessions/$SESSION_ID/output?timeout=1")
  echo "$OUTPUT" | jq -r '.output'
}

# Run tests
echo "Running tests..."
TEST_OUTPUT=$(send_command "npm test")

# Check if tests passed
if echo "$TEST_OUTPUT" | grep -q "PASS"; then
  echo "Tests passed, building..."
  BUILD_OUTPUT=$(send_command "npm run build")
  
  # Check if build succeeded
  if [ $? -eq 0 ]; then
    echo "Build succeeded, deploying..."
    DEPLOY_OUTPUT=$(send_command "npm run deploy")
    echo "Deployment complete"
  else
    echo "Build failed"
    exit 1
  fi
else
  echo "Tests failed"
  exit 1
fi

# Clean up session
curl -s -X DELETE http://localhost:8767/api/sessions/$SESSION_ID
echo "Cleaned up session: $SESSION_ID"
```

## Advanced Integration Topics

### Securing Integration Points

When integrating Terma with external systems, consider these security measures:

1. **Authentication Token**: Add token-based authentication for REST API access
   ```http
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

2. **WebSocket Authentication**: Implement handshake authentication for WebSocket connections
   ```javascript
   // Client-side authentication
   const ws = new WebSocket(`ws://localhost:8767/ws/${sessionId}?token=${authToken}`);
   ```

3. **Command Restrictions**: Limit which commands can be executed
   ```python
   def validate_command(command, allowed_commands):
       # Parse the command to get the base executable
       parts = shlex.split(command)
       if not parts:
           return False
       
       executable = os.path.basename(parts[0])
       return executable in allowed_commands
   ```

4. **Resource Limitations**: Enforce resource usage limits
   ```python
   # Limit the number of sessions per user
   async def create_session(user_id):
       user_sessions = await get_user_sessions(user_id)
       if len(user_sessions) >= MAX_SESSIONS_PER_USER:
           raise TooManySessions("Maximum sessions limit reached")
   ```

### High Availability Setup

For production deployments, consider these high-availability configurations:

1. **Session Persistence**: Store session metadata in a persistent database
   ```python
   async def store_session_metadata(session_id, metadata):
       await db.sessions.insert_one({
           "session_id": session_id,
           "metadata": metadata,
           "created_at": datetime.now()
       })
   ```

2. **Load Balancing**: Configure load balancing across multiple Terma instances
   ```nginx
   upstream terma_backend {
       server terma1:8767;
       server terma2:8767;
       server terma3:8767;
   }
   
   server {
       listen 80;
       server_name terma.example.com;
       
       location / {
           proxy_pass http://terma_backend;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

3. **Session Recovery**: Implement session recovery mechanisms
   ```python
   async def recover_session(session_id):
       # Get session metadata from database
       metadata = await db.sessions.find_one({"session_id": session_id})
       if not metadata:
           return None
       
       # Create new session with same parameters
       new_session = await create_session(
           shell_command=metadata["shell_command"],
           cwd=metadata["cwd"],
           env=metadata["env"]
       )
       
       # Link new session with old session ID
       await db.session_links.insert_one({
           "old_session_id": session_id,
           "new_session_id": new_session.session_id
       })
       
       return new_session
   ```

## Troubleshooting Integration Issues

### Common Issues and Solutions

1. **WebSocket Connection Failures**
   - **Symptoms**: Unable to connect to WebSocket, connection closed unexpectedly
   - **Possible Causes**: Network issues, proxy configuration, server not running
   - **Solutions**: 
     - Check that the Terma service is running
     - Verify WebSocket URL is correct (ws:// vs wss://)
     - Ensure proxy is configured for WebSocket upgrade
     - Check for firewall restrictions

2. **Command Execution Problems**
   - **Symptoms**: Commands don't execute as expected, no output
   - **Possible Causes**: Permission issues, shell configuration, environment variables
   - **Solutions**:
     - Check shell command is available
     - Verify working directory exists and is accessible
     - Check environment variables
     - Look for error messages in server logs

3. **LLM Assistance Not Working**
   - **Symptoms**: LLM responses not appearing, errors when requesting assistance
   - **Possible Causes**: LLM service unavailable, network issues, configuration issues
   - **Solutions**:
     - Check LLM Adapter is running
     - Verify LLM provider configuration
     - Check network connectivity to LLM service
     - Look for error messages in server logs

### Debugging Integration

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("terma")

# Debug HTTP requests
async def debug_request(method, url, data=None):
    logger.debug(f"Request: {method} {url}")
    if data:
        logger.debug(f"Request body: {data}")
    
    # Make request
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, json=data)
    
    logger.debug(f"Response status: {response.status_code}")
    logger.debug(f"Response body: {response.text}")
    
    return response

# Debug WebSocket messages
def debug_websocket(ws):
    original_send = ws.send
    original_onmessage = ws.onmessage
    
    # Override send
    ws.send = lambda message: logger.debug(f"WS Send: {message}") or original_send(message)
    
    # Override onmessage
    ws.onmessage = lambda event: logger.debug(f"WS Receive: {event.data}") or (original_onmessage and original_onmessage(event))
    
    return ws
```

## Conclusion

Terma is designed to integrate seamlessly with the Tekton ecosystem and external systems. By following the patterns and examples in this guide, you can effectively incorporate terminal functionality into your applications and create rich terminal experiences with LLM assistance.

For more detailed information, refer to the [Technical Documentation](./TECHNICAL_DOCUMENTATION.md), [API Reference](./API_REFERENCE.md), and [User Guide](./USER_GUIDE.md).