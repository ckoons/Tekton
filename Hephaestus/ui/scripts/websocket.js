/**
 * DEPRECATED: This file will be removed after CSS-first migration is verified
 * WebSocket Manager
 * Handles WebSocket communication with the Tekton backend
 */

console.log('[FILE_TRACE] Loading: websocket.js');
class WebSocketManager {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000;
        this.url = this.getWebSocketUrl();
        this.messageQueue = [];
    }
    
    /**
     * Get WebSocket URL based on current location
     * @returns {string} WebSocket URL
     */
    getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.hostname;
        // Get port from environment variable with fallback
        // In the new Single Port Architecture, WebSocket uses the same port as HTTP
        // but with a specific path (/ws)
        const port = window.HEPHAESTUS_PORT || 8080;
        console.log(`Connecting to WebSocket server on port ${port}`);
        return `${protocol}//${host}:${port}/ws`;
    }
    
    /**
     * Connect to the WebSocket server
     */
    connect() {
        try {
            console.log('Connecting to WebSocket server at:', this.url);
            this.socket = new WebSocket(this.url);
            
            this.socket.onopen = () => {
                console.log('WebSocket connected successfully');
                this.connected = true;
                this.reconnectAttempts = 0;
                
                // Register the UI
                this.sendMessage({
                    type: 'REGISTER',
                    source: 'UI',
                    target: 'SYSTEM',
                    timestamp: new Date().toISOString(),
                    payload: {
                        clientId: 'ui-client-' + Date.now(),
                        capabilities: ['UI', 'USER_INTERACTION']
                    }
                });
                
                // Process any queued messages
                this.processQueue();
                
                // Display connection status in UI
                this.updateConnectionStatus(true);
                
                // Call onNextConnect callback if defined
                if (typeof this.onNextConnect === 'function') {
                    console.log('Calling onNextConnect callback');
                    this.onNextConnect();
                    // Clear the callback
                    this.onNextConnect = null;
                }
            };
            
            this.socket.onmessage = (event) => {
                console.log('WebSocket message received:', event.data.substring(0, 100) + '...');
                this.handleMessage(event.data);
            };
            
            this.socket.onclose = () => {
                console.log('WebSocket disconnected');
                this.connected = false;
                
                // Display disconnection in UI
                this.updateConnectionStatus(false);
                
                // Try to reconnect
                this.attemptReconnect();
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.connected = false;
                
                // Display error in UI
                this.updateConnectionStatus(false, error);
            };
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            // Since we can't connect, set up a fake connection for demo purposes
            this.setupFakeConnection();
        }
    }
    
    /**
     * Set up a fake connection for demo purposes when no real backend is available
     */
    setupFakeConnection() {
        console.log('Setting up fake WebSocket connection for demo purposes');
        this.connected = true;
        
        // Show a message to the user
        if (window.terminalManager) {
            terminalManager.write('⚠️ Running in demo mode - no backend connection available');
            terminalManager.write('Some features may be limited or simulated');
        }
        
        // Set up fake processing for messages
        this.fakeSendMessage = this.sendMessage;
        this.sendMessage = (message) => {
            console.log('Fake WebSocket message sent:', message);
            
            // Simulate a response after a delay
            setTimeout(() => {
                this.simulateResponse(message);
            }, 500);
        };
    }
    
    /**
     * Simulate a response to a message in demo mode
     * @param {Object} message - The message to respond to
     */
    simulateResponse(message) {
        if (!message || !message.type) return;
        
        if (window.tektonUI) {
            tektonUI.log("Simulating response for message", message);
        }
        
        switch (message.type) {
            case 'COMMAND':
                if (message.payload && message.payload.command === 'process_message') {
                    const userMessage = message.payload.message;
                    const componentId = message.target;
                    const context = message.payload.context || componentId;
                    
                    // Show processing message immediately
                    this.addToTerminal(`[${componentId}] Processing: "${userMessage}"`, '#888888');
                    
                    // Show typing indicator after a slight delay
                    setTimeout(() => {
                        // Send typing indicator
                        const typingUpdate = {
                            type: 'UPDATE',
                            source: componentId,
                            target: 'UI',
                            timestamp: new Date().toISOString(),
                            payload: {
                                status: 'typing',
                                isTyping: true,
                                context: context
                            }
                        };
                        this.handleMessage(JSON.stringify(typingUpdate));
                        
                        // Then send the response after a delay
                        setTimeout(() => {
                            const response = this.generateFakeResponse(userMessage, componentId, context);
                            
                            // Create AI response message
                            const responseMessage = {
                                type: 'RESPONSE',
                                source: componentId,
                                target: 'UI',
                                timestamp: new Date().toISOString(),
                                payload: {
                                    message: response,
                                    context: context
                                }
                            };
                            
                            this.handleMessage(JSON.stringify(responseMessage));
                        }, 800 + Math.random() * 800); // Random delay between 0.8-1.6 seconds for response
                    }, 200); // Small delay before processing starts
                    
                } else if (message.payload && message.payload.command === 'get_context') {
                    // Simulate context response
                    const componentId = message.target;
                    
                    if (window.terminalManager) {
                        terminalManager.write(`Loaded context for ${componentId} component`);
                    }
                } else {
                    // General command
                    if (window.terminalManager) {
                        terminalManager.write(`Command "${message.payload.command}" sent to ${message.target}`);
                        
                        // After a small delay, send a response
                        setTimeout(() => {
                            const responseMessage = {
                                type: 'RESPONSE',
                                source: message.target,
                                target: 'UI',
                                timestamp: new Date().toISOString(),
                                payload: {
                                    message: `Command "${message.payload.command}" executed successfully`,
                                }
                            };
                            
                            this.handleMessage(JSON.stringify(responseMessage));
                        }, 500);
                    }
                }
                break;
                
            case 'REGISTER':
                if (window.terminalManager) {
                    terminalManager.write('UI client registered with Tekton system');
                    terminalManager.write('Running in demo mode - type "help" for available commands');
                }
                break;
        }
    }
    
    /**
     * Generate a fake response for demo mode
     * @param {string} message - User message to respond to
     * @param {string} componentId - The component ID
     * @param {string} context - The context/tab (optional)
     * @returns {string} Generated response
     */
    generateFakeResponse(message, componentId, context = null) {
        const contextId = context || componentId;
        
        // Check for special keywords in the message for more contextual responses
        if (message.toLowerCase().includes('hello') || message.toLowerCase().includes('hi')) {
            return `Hello! I'm the ${componentId} AI assistant. How can I help you today?`;
        }
        
        if (message.toLowerCase().includes('help')) {
            return `I can help you with various ${componentId} tasks. What specific aspect do you need assistance with?`;
        }
        
        // Context-specific responses
        const responses = {
            ergon: [
                "I can help you create and manage agents for various tasks. Would you like me to explain the agent types?",
                `The Ergon system manages AI agents that can perform tasks across different domains. Your message "${message}" is being processed.`,
                "I can help you set up workflows between agents or execute specific tasks. What would you like to accomplish?"
            ],
            'awt-team': [
                "The Advanced Workflow Tools team provides specialized workflow automation. Your request is being processed.",
                "AWT systems are designed for complex process orchestration. I can help you design optimal workflows for your needs.",
                "Advanced Workflow Tools can integrate with multiple data sources and processing systems. How can I assist you today?"
            ],
            tekton: [
                "I'm managing your projects. What would you like to do?",
                "This is the Tekton Projects component. I can help with project management.",
                "Your project dashboard is ready. Ask me to create or modify projects."
            ],
            prometheus: [
                "Prometheus Planning System active. I can help with scheduling and planning.",
                "Let me assist with your project timeline and roadmap.",
                "I'm analyzing your planning needs. How can I assist with scheduling?"
            ],
            engram: [
                "Engram Memory System active. I can help you retrieve past information.",
                "I'm searching through our conversation history for relevant context.",
                "Memory systems online. What would you like to remember?"
            ]
        };
        
        // Default responses if component/context isn't specifically handled
        const defaultResponses = [
            `The ${componentId} component received your message: "${message}"`,
            `I'm processing your request in the ${componentId} system.`,
            `${componentId} component is active and responding to your input.`
        ];
        
        // Get appropriate response list
        const responseList = responses[contextId] || defaultResponses;
        
        // Select a random response
        return responseList[Math.floor(Math.random() * responseList.length)];
    }
    
    /**
     * Attempt to reconnect to the WebSocket server
     */
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Max reconnect attempts reached');
            
            // Set up fake connection since we can't connect
            this.setupFakeConnection();
            return;
        }
        
        this.reconnectAttempts++;
        
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
        
        setTimeout(() => {
            this.connect();
        }, this.reconnectInterval);
    }
    
    /**
     * Send a message through the WebSocket
     * @param {Object} message - Message to send (will be JSON stringified)
     */
    sendMessage(message) {
        if (!message) {
            console.error("Cannot send empty message");
            return;
        }
        
        // Ensure message has required fields for Tekton protocol
        if (typeof message === 'object' && !message.type) {
            console.error("Message missing required 'type' field:", message);
            // Add default type if missing
            message.type = 'COMMAND';
        }
        
        if (typeof message === 'object' && !message.source) {
            message.source = 'UI';
        }
        
        if (typeof message === 'object' && !message.timestamp) {
            message.timestamp = new Date().toISOString();
        }
        
        // Log the message we're sending
        console.log('Sending WebSocket message:', 
          typeof message === 'object' ? 
            `Type: ${message.type}, Target: ${message.target || 'SYSTEM'}` : 
            'Raw message');
        
        if (this.connected && this.socket && this.socket.readyState === WebSocket.OPEN) {
            const serializedMessage = typeof message === 'string' ? message : JSON.stringify(message);
            try {
                this.socket.send(serializedMessage);
                console.log('Message sent successfully');
            } catch (e) {
                console.error('Error sending message:', e);
                // Queue the message for retry
                this.messageQueue.push(message);
            }
        } else {
            console.log('WebSocket not connected, queueing message for later');
            // Queue the message for later
            this.messageQueue.push(message);
            
            // Try to connect if not connected
            if (!this.connected) {
                console.log('Attempting to reconnect WebSocket');
                this.connect();
            }
        }
    }
    
    /**
     * Process queued messages after connection is established
     */
    processQueue() {
        if (this.messageQueue.length === 0) return;
        
        console.log(`Processing ${this.messageQueue.length} queued messages`);
        
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.sendMessage(message);
        }
    }
    
    /**
     * Handle an incoming WebSocket message
     * @param {string} data - Message data (JSON string)
     */
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            
            console.log('Received message:', message);
            
            switch (message.type) {
                case 'RESPONSE':
                    this.handleResponse(message);
                    break;
                    
                case 'UPDATE':
                    this.handleUpdate(message);
                    break;
                    
                case 'NOTIFICATION':
                    this.handleNotification(message);
                    break;
                    
                case 'ERROR':
                    this.handleError(message);
                    break;
                    
                default:
                    console.log('Unknown message type:', message.type);
            }
        } catch (error) {
            console.error('Error parsing message:', error);
        }
    }
    
    /**
     * Handle a response message
     * @param {Object} message - Response message
     */
    handleResponse(message) {
        const payload = message.payload || {};
        
        if (window.tektonUI) {
            tektonUI.log("Handling response message", message);
        }
        
        // Handle AI response to a message
        if (payload.message !== undefined) {
            this.addToTerminal(payload.message, '#00bfff');
        } else if (payload.response !== undefined) {
            this.addToTerminal(payload.response, '#00bfff');
        }
        
        // Handle context response
        if (payload.context && window.uiManager) {
            // Update UI based on context
            
            // Set terminal mode if specified
            if (payload.context.mode === 'terminal') {
                uiManager.activatePanel('terminal');
            } else if (payload.context.mode === 'html') {
                uiManager.activatePanel('html');
            }
            
            // Display context summary
            if (payload.context.summary) {
                this.addToTerminal(payload.context.summary, '#aaaaaa');
            }
        }
    }
    
    /**
     * Add message to terminal content
     * @param {string} message - The message text
     * @param {string} color - Text color (hex or name)
     */
    addToTerminal(message, color = 'white') {
        // Add message to the terminal content div instead of using terminalManager
        const terminalContent = document.getElementById('terminal-content');
        if (!terminalContent) return;
        
        // Create message element
        const msgDiv = document.createElement('div');
        msgDiv.style.color = color;
        msgDiv.style.padding = '5px 0';
        msgDiv.style.marginBottom = '10px';
        msgDiv.style.whiteSpace = 'pre-wrap';
        msgDiv.style.wordBreak = 'break-word';
        msgDiv.textContent = message;
        
        // Add to terminal
        terminalContent.appendChild(msgDiv);
        
        // Scroll to bottom
        terminalContent.scrollTop = terminalContent.scrollHeight;
    }
    
    /**
     * Handle an update message
     * @param {Object} message - Update message
     */
    handleUpdate(message) {
        const payload = message.payload || {};
        
        if (window.tektonUI) {
            tektonUI.log("Handling update message", message);
        }
        
        // Update terminal if terminal update included
        if (payload.terminal) {
            if (typeof payload.terminal === 'string') {
                this.addToTerminal(payload.terminal);
            } else if (payload.terminal.text) {
                this.addToTerminal(
                    payload.terminal.text, 
                    payload.terminal.isCommand ? '#00ff00' : 'white'
                );
            }
        }
        
        // Handle typing status (used to be for chat UI)
        if (payload.status === 'typing') {
            const isTyping = !!payload.isTyping;
            if (isTyping) {
                // Find and remove any existing processing messages
                const terminalContent = document.getElementById('terminal-content');
                if (terminalContent) {
                    const existingProcessing = terminalContent.querySelectorAll('div[data-processing="true"]');
                    existingProcessing.forEach(el => el.remove());
                    
                    // Add new processing message
                    const processingDiv = document.createElement('div');
                    processingDiv.setAttribute('data-processing', 'true');
                    processingDiv.style.color = '#888';
                    processingDiv.style.padding = '5px 0';
                    processingDiv.style.marginBottom = '10px';
                    processingDiv.textContent = 'Processing request...';
                    terminalContent.appendChild(processingDiv);
                    terminalContent.scrollTop = terminalContent.scrollHeight;
                }
            }
        }
        
        // Handle message updates
        if (payload.message) {
            this.addToTerminal(payload.message);
        }
        
        // Update HTML elements if specified
        if (payload.elements && window.uiManager) {
            Object.entries(payload.elements).forEach(([elementId, update]) => {
                const element = document.getElementById(elementId);
                if (!element) return;
                
                if (update.text) element.textContent = update.text;
                if (update.html) element.innerHTML = update.html;
                if (update.value) element.value = update.value;
                if (update.classes) {
                    if (update.classes.add) {
                        update.classes.add.forEach(cls => element.classList.add(cls));
                    }
                    if (update.classes.remove) {
                        update.classes.remove.forEach(cls => element.classList.remove(cls));
                    }
                }
            });
        }
    }
    
    /**
     * Handle a notification message
     * @param {Object} message - Notification message
     */
    handleNotification(message) {
        const payload = message.payload || {};
        
        if (window.tektonUI) {
            tektonUI.log("Handling notification message", message);
        }
        
        if (payload.message) {
            // Get notification prefix and color based on type
            let prefix, color;
            
            switch(payload.type) {
                case 'error':
                    prefix = 'ERROR: ';
                    color = '#ff3333';
                    break;
                case 'warning':
                    prefix = 'WARNING: ';
                    color = '#ffaa00';
                    break;
                case 'success':
                    prefix = 'SUCCESS: ';
                    color = '#33cc33';
                    break;
                default:
                    prefix = 'NOTIFICATION: ';
                    color = '#aaaaaa';
            }
            
            // Add to terminal
            this.addToTerminal(`${prefix}${payload.message}`, color);
            
            // Also show in UI if specified
            if (payload.type === 'error') {
                if (window.tektonUI) {
                    tektonUI.showError(payload.message);
                }
            } else if (payload.type === 'modal') {
                if (window.tektonUI) {
                    tektonUI.showModal(payload.title || 'Notification', payload.message);
                }
            }
        }
    }
    
    /**
     * Handle an error message
     * @param {Object} message - Error message
     */
    handleError(message) {
        const payload = message.payload || {};
        
        if (window.tektonUI) {
            tektonUI.log("Handling error message", message);
        }
        
        console.error('Error from server:', payload);
        
        if (payload.message) {
            // Add error to terminal with red color
            this.addToTerminal(`ERROR: ${payload.message}`, '#ff3333');
            
            // Also show in UI
            if (window.tektonUI) {
                tektonUI.showError(payload.message);
            }
        }
    }
    
    /**
     * Update connection status in the UI
     * @param {boolean} connected - Whether connected
     * @param {Object} error - Optional error object
     */
    updateConnectionStatus(connected, error = null) {
        // This could update a status indicator in the UI
        if (!connected && error) {
            console.error('Connection error:', error);
            
            if (window.tektonUI) {
                tektonUI.showError('Connection to Tekton server lost. Attempting to reconnect...');
            }
        }
    }
    
    /**
     * Disconnect from the WebSocket server
     */
    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }
}