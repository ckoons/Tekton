/**
 * Hermes Connector
 * Establishes connection with Hermes message bus for AI communication
 * Also handles connection to the LLM Adapter for terminal chat
 */

// LLM Adapter configuration
const LLM_ADAPTER_CONFIG = {
    // WebSocket endpoint for LLM Adapter 
    wsUrl: `ws://localhost:${window.RHETOR_PORT || 8003}/ws`,
    
    // Whether to use streaming responses (recommended)
    useStreaming: true,
    
    // Default options for LLM
    options: {
        temperature: 0.7,
        max_tokens: 4000
    }
};

class HermesConnector {
    constructor() {
        this.connected = false;
        this.endpoints = {
            register: '/api/register',
            message: '/api/message',
            health: '/health',  // Changed from status to health
            // Add new endpoints for LLM integration
            terminal_message: '/api/terminal/message',
            terminal_stream: '/api/terminal/stream'
        };
        this.terminals = {}; // Terminal registrations by context ID
        this.baseUrl = window.location.origin;
        this.eventListeners = {};
        this.connectionTimeout = null;
        this.retryDelay = 5000; // 5 second initial retry
        this.maxRetryDelay = 30000; // Max 30 second retry
        this.activeStreams = {}; // Track active streaming responses
        
        // LLM Adapter connection
        this.llmSocket = null;
        this.llmConnected = false;
        this.llmConnectionAttempted = false;
    }
    
    /**
     * Initialize the connector and establish connection
     */
    init() {
        console.log('Initializing Hermes connector...');
        
        // Check if settings disable Hermes integration
        if (window.settingsManager && 
            window.settingsManager.settings.hermesIntegration === false) {
            console.log('Hermes integration disabled in settings');
            return this;
        }
        
        // Try to connect to Hermes
        this.connect();
        
        // Also try to connect to LLM Adapter
        this.connectToLLMAdapter();
        
        return this;
    }
    
    /**
     * Connect to the LLM Adapter
     * @param {Object} initialRequest - Optional initial request to send once connected
     */
    connectToLLMAdapter(initialRequest = null) {
        // If already attempted connection, don't retry automatically
        if (this.llmConnectionAttempted && !initialRequest) {
            return;
        }
        
        console.log('Connecting to LLM Adapter...');
        this.llmConnectionAttempted = true;
        
        // Close existing connection if any
        if (this.llmSocket) {
            this.llmSocket.close();
        }
        
        try {
            // Create new connection
            this.llmSocket = new WebSocket(LLM_ADAPTER_CONFIG.wsUrl);
            
            // Set up event handlers
            this.llmSocket.onopen = () => {
                console.log("Connected to LLM Adapter");
                this.llmConnected = true;
                this.dispatchEvent('llmConnected', { status: 'connected' });
                
                // Send initial request if any
                if (initialRequest) {
                    this.llmSocket.send(JSON.stringify(initialRequest));
                }
                
                // Send registration message
                const registrationMsg = {
                    type: 'REGISTER',
                    source: 'HEPHAESTUS',
                    target: 'LLM_ADAPTER',
                    timestamp: new Date().toISOString(),
                    payload: {
                        clientId: 'hephaestus-ui',
                        clientType: 'terminal',
                        supportedContexts: ['ergon', 'awt-team', 'agora']
                    }
                };
                this.llmSocket.send(JSON.stringify(registrationMsg));
            };
            
            this.llmSocket.onmessage = (event) => {
                try {
                    // Handle messages from LLM Adapter
                    const data = JSON.parse(event.data);
                    console.log("Received message from LLM Adapter:", data.type);
                    
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
                                context: data.payload.context || data.source
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
                                context: data.payload.context || 'unknown'
                            }
                        });
                    }
                } catch (e) {
                    console.error("Error handling LLM Adapter message:", e);
                }
            };
            
            this.llmSocket.onerror = (error) => {
                console.error("LLM Adapter connection error:", error);
                this.llmConnected = false;
                this.dispatchEvent('llmConnectionError', { error });
            };
            
            this.llmSocket.onclose = () => {
                console.log("LLM Adapter connection closed");
                this.llmConnected = false;
                this.dispatchEvent('llmDisconnected', { status: 'disconnected' });
            };
        } catch (e) {
            console.error("Error connecting to LLM Adapter:", e);
            this.llmConnected = false;
        }
    }
    
    /**
     * Connect to Hermes
     */
    connect() {
        console.log('Attempting to connect to Hermes message bus...');
        
        // Clear any existing timeout
        if (this.connectionTimeout) {
            clearTimeout(this.connectionTimeout);
        }
        
        // Check Hermes health
        fetch(`${this.baseUrl}${this.endpoints.health}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Hermes health check failed: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Hermes health:', data);
                this.connected = true;
                this.retryDelay = 5000; // Reset retry delay on successful connection
                this.dispatchEvent('connected', data);
                
                // Register any terminals that were added before connection
                Object.values(this.terminals).forEach(terminal => {
                    if (!terminal.registered) {
                        this.registerTerminal(terminal.id, terminal.metadata);
                    }
                });
            })
            .catch(error => {
                console.error('Error connecting to Hermes:', error);
                this.connected = false;
                this.dispatchEvent('connectionError', { error });
                
                // Schedule retry with exponential backoff
                this.connectionTimeout = setTimeout(() => {
                    this.connect();
                }, this.retryDelay);
                
                // Increase retry delay for next attempt (with max limit)
                this.retryDelay = Math.min(this.retryDelay * 1.5, this.maxRetryDelay);
            });
    }
    
    /**
     * Register a terminal with Hermes
     * @param {string} terminalId - ID of the terminal (context ID)
     * @param {Object} metadata - Terminal metadata
     */
    registerTerminal(terminalId, metadata = {}) {
        // Store terminal even if not connected yet
        this.terminals[terminalId] = {
            id: terminalId,
            metadata: metadata,
            registered: false
        };
        
        // If not connected, will register when connection established
        if (!this.connected) {
            console.log(`Terminal ${terminalId} queued for registration when connected`);
            return;
        }
        
        console.log(`Registering terminal ${terminalId} with Hermes`);
        
        // Convert Greek names if needed
        const displayName = this.getDisplayName(terminalId);
        
        // Prepare registration data
        const registrationData = {
            id: terminalId,
            type: 'ui-terminal',
            name: displayName,
            capabilities: ['receive-messages', 'send-messages'],
            ...metadata
        };
        
        // Register with Hermes
        fetch(`${this.baseUrl}${this.endpoints.register}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(registrationData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Registration failed: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`Terminal ${terminalId} registered successfully:`, data);
            this.terminals[terminalId].registered = true;
            this.dispatchEvent('terminalRegistered', { 
                terminalId, 
                response: data 
            });
        })
        .catch(error => {
            console.error(`Error registering terminal ${terminalId}:`, error);
            this.dispatchEvent('registrationError', { 
                terminalId, 
                error 
            });
        });
    }
    
    /**
     * Unregister a terminal with Hermes
     * @param {string} terminalId - ID of the terminal to unregister
     */
    unregisterTerminal(terminalId) {
        if (!this.terminals[terminalId]) {
            console.log(`Terminal ${terminalId} not found for unregistration`);
            return;
        }
        
        if (!this.connected) {
            console.log(`Cannot unregister terminal ${terminalId} - not connected`);
            delete this.terminals[terminalId];
            return;
        }
        
        console.log(`Unregistering terminal ${terminalId}`);
        
        // Send unregister request
        fetch(`${this.baseUrl}${this.endpoints.register}/${terminalId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Unregistration failed: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`Terminal ${terminalId} unregistered successfully`);
            delete this.terminals[terminalId];
            this.dispatchEvent('terminalUnregistered', { terminalId });
        })
        .catch(error => {
            console.error(`Error unregistering terminal ${terminalId}:`, error);
            delete this.terminals[terminalId]; // Remove from local tracking anyway
        });
    }
    
    /**
     * Send a message through Hermes
     * @param {string} sender - Sender terminal ID
     * @param {string|Array} recipients - Recipient terminal ID(s)
     * @param {Object} message - Message data
     */
    sendMessage(sender, recipients, message) {
        if (!this.connected) {
            console.error(`Cannot send message - not connected to Hermes`);
            return;
        }
        
        // Normalize recipients to array
        const recipientList = Array.isArray(recipients) ? recipients : [recipients];
        
        // Prepare message
        const messageData = {
            sender: sender,
            recipients: recipientList,
            timestamp: new Date().toISOString(),
            payload: message
        };
        
        console.log(`Sending message from ${sender} to ${recipientList.join(', ')}:`, message);
        
        // Send message to Hermes
        fetch(`${this.baseUrl}${this.endpoints.message}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(messageData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Message send failed: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`Message sent successfully:`, data);
            this.dispatchEvent('messageSent', { 
                sender, 
                recipients: recipientList, 
                message,
                response: data 
            });
        })
        .catch(error => {
            console.error(`Error sending message from ${sender}:`, error);
            this.dispatchEvent('messageError', { 
                sender, 
                recipients: recipientList, 
                message,
                error 
            });
        });
    }
    
    /**
     * Get a display name for a terminal based on settings
     * @param {string} terminalId - Terminal ID to convert
     * @returns {string} Display name based on current settings
     */
    getDisplayName(terminalId) {
        // Use settings manager if available
        if (window.settingsManager) {
            return window.settingsManager.getChatTabLabel(terminalId);
        }
        
        // Default mappings if settings manager not available
        const displayNames = {
            'ergon': 'Ergon',
            'awt-team': 'Symposium',
            'agora': 'Agora'
        };
        
        return displayNames[terminalId] || terminalId;
    }
    
    /**
     * Register an event listener
     * @param {string} event - Event name
     * @param {Function} callback - Callback function
     */
    addEventListener(event, callback) {
        if (!this.eventListeners[event]) {
            this.eventListeners[event] = [];
        }
        this.eventListeners[event].push(callback);
        return this;
    }
    
    /**
     * Remove an event listener
     * @param {string} event - Event name
     * @param {Function} callback - Callback function to remove
     */
    removeEventListener(event, callback) {
        if (this.eventListeners[event]) {
            this.eventListeners[event] = this.eventListeners[event]
                .filter(cb => cb !== callback);
        }
        return this;
    }
    
    /**
     * Dispatch an event to all listeners
     * @param {string} event - Event name
     * @param {*} data - Event data
     */
    dispatchEvent(event, data) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (e) {
                    console.error(`Error in Hermes event handler for ${event}:`, e);
                }
            });
        }
        return this;
    }
    
    /**
     * Send a message to the LLM and handle the response
     * @param {string} contextId - Context ID (ergon, awt-team, etc)
     * @param {string} message - User message
     * @param {boolean} streaming - Whether to use streaming mode
     * @param {Object} options - Additional options (model, temperature, etc)
     */
    sendLLMMessage(contextId, message, streaming = true, options = {}) {
        console.log(`Sending LLM message in ${contextId} context: ${message.substring(0, 50)}...`);
        
        // First try to use the LLM Adapter if available
        if (this.llmConnected && this.llmSocket && this.llmSocket.readyState === WebSocket.OPEN) {
            console.log(`Using LLM Adapter for ${contextId} message`);
            
            // Create LLM request for the adapter
            const llmRequest = {
                type: 'LLM_REQUEST',
                source: 'HEPHAESTUS',
                target: 'LLM_ADAPTER',
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
            
            // Show typing indicator
            this.dispatchEvent('typingStarted', { contextId });
            
            // Send message to LLM Adapter
            this.llmSocket.send(JSON.stringify(llmRequest));
            return;
        }
        
        // If we can't use the LLM Adapter, try to connect to it
        // This will retry the connection if it's not already attempted
        if (!this.llmConnectionAttempted) {
            console.log(`LLM Adapter not connected, attempting to connect for ${contextId} message`);
            
            // Create request to send after connection
            const initialRequest = {
                type: 'LLM_REQUEST',
                source: 'HEPHAESTUS',
                target: 'LLM_ADAPTER',
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
            
            // Show typing indicator
            this.dispatchEvent('typingStarted', { contextId });
            
            // Try to connect and send message
            this.connectToLLMAdapter(initialRequest);
            return;
        }
        
        // Fall back to the legacy API endpoint if LLM Adapter isn't available
        console.log(`Falling back to legacy API endpoint for ${contextId} message`);
        
        // Prepare request data
        const requestData = {
            message: message,
            context_id: contextId,
            streaming: streaming,
            ...options
        };
        
        // Dispatch event to show typing indicator
        this.dispatchEvent('typingStarted', { contextId });
        
        if (streaming) {
            // Handle streaming response
            this.streamLLMResponse(contextId, requestData);
        } else {
            // Handle regular response
            fetch(`${this.baseUrl}${this.endpoints.terminal_message}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`LLM request failed: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(`Received LLM response for ${contextId}:`, data);
                
                // Hide typing indicator
                this.dispatchEvent('typingEnded', { contextId });
                
                // Dispatch received message event
                this.dispatchEvent('messageReceived', {
                    sender: contextId,
                    recipients: ['user', 'terminal'],
                    message: {
                        text: data.message,
                        content: data.message,
                        type: 'llm_response',
                        context: contextId
                    }
                });
            })
            .catch(error => {
                console.error(`Error in LLM request for ${contextId}:`, error);
                
                // Hide typing indicator
                this.dispatchEvent('typingEnded', { contextId });
                
                // Show error message
                this.dispatchEvent('messageReceived', {
                    sender: 'system',
                    recipients: ['user', 'terminal'],
                    message: {
                        text: `Error: ${error.message}`,
                        type: 'error',
                        context: contextId
                    }
                });
            });
        }
    }
    
    /**
     * Stream an LLM response
     * @param {string} contextId - Context ID
     * @param {Object} requestData - Request data
     */
    streamLLMResponse(contextId, requestData) {
        console.log(`Streaming LLM response for ${contextId}`);
        
        // Cancel any existing stream for this context
        if (this.activeStreams[contextId]) {
            this.activeStreams[contextId].abort();
            delete this.activeStreams[contextId];
        }
        
        // Create abort controller for this stream
        const controller = new AbortController();
        this.activeStreams[contextId] = controller;
        
        // Create response buffer
        const responseBuffer = [];
        
        // Start stream
        fetch(`${this.baseUrl}${this.endpoints.terminal_stream}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            },
            body: JSON.stringify(requestData),
            signal: controller.signal
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`LLM stream request failed: ${response.status}`);
            }
            
            // Get reader from response body
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            // Process stream chunks
            const processStream = ({ done, value }) => {
                if (done) {
                    console.log(`Stream complete for ${contextId}`);
                    
                    // Clean up stream
                    delete this.activeStreams[contextId];
                    
                    // Hide typing indicator
                    this.dispatchEvent('typingEnded', { contextId });
                    
                    // If nothing received, show error
                    if (responseBuffer.length === 0) {
                        this.dispatchEvent('messageReceived', {
                            sender: 'system',
                            recipients: ['user', 'terminal'],
                            message: {
                                text: `No response received from LLM.`,
                                type: 'error',
                                context: contextId
                            }
                        });
                    }
                    
                    // Send complete message event
                    this.dispatchEvent('streamComplete', {
                        contextId,
                        fullResponse: responseBuffer.join('')
                    });
                    
                    return;
                }
                
                // Process chunk
                const chunk = decoder.decode(value, { stream: true });
                
                // Parse and dispatch events
                this.processStreamChunk(contextId, chunk, responseBuffer);
                
                // Continue reading
                return reader.read().then(processStream);
            };
            
            // Start processing the stream
            reader.read().then(processStream);
        })
        .catch(error => {
            if (error.name === 'AbortError') {
                console.log(`Stream for ${contextId} was aborted`);
            } else {
                console.error(`Error streaming LLM response for ${contextId}:`, error);
                
                // Hide typing indicator
                this.dispatchEvent('typingEnded', { contextId });
                
                // Show error message
                this.dispatchEvent('messageReceived', {
                    sender: 'system',
                    recipients: ['user', 'terminal'],
                    message: {
                        text: `Error: ${error.message}`,
                        type: 'error',
                        context: contextId
                    }
                });
            }
            
            // Clean up stream
            delete this.activeStreams[contextId];
        });
    }
    
    /**
     * Process a streaming chunk
     * @param {string} contextId - Context ID
     * @param {string} chunk - Raw chunk data
     * @param {Array} buffer - Response buffer to append to
     */
    processStreamChunk(contextId, chunk, buffer) {
        // Stream data comes as "data: {...}" lines
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (!line.trim() || !line.startsWith('data:')) continue;
            
            try {
                const jsonStr = line.substring(5).trim();
                const data = JSON.parse(jsonStr);
                
                // Check if this is the end of the stream
                if (data.done) {
                    console.log(`Stream end marker received for ${contextId}`);
                    return;
                }
                
                // Check for errors
                if (data.error) {
                    console.error(`Error in stream for ${contextId}:`, data.error);
                    
                    // Dispatch error event
                    this.dispatchEvent('messageError', {
                        contextId,
                        error: data.error
                    });
                    
                    return;
                }
                
                // Handle text chunk
                if (data.chunk) {
                    // Add to buffer
                    buffer.push(data.chunk);
                    
                    // Dispatch chunk event
                    this.dispatchEvent('streamChunk', {
                        contextId,
                        chunk: data.chunk
                    });
                }
            } catch (e) {
                console.error(`Error parsing stream chunk: ${e}`);
            }
        }
    }
}

// Initialize the Hermes connector when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Create global instance
    window.hermesConnector = new HermesConnector();
    
    // Initialize after UI elements and settings are available
    setTimeout(() => {
        window.hermesConnector.init();
    }, 1500);
});