/**
 * Budget WebSocket Handler
 * 
 * Manages WebSocket connections for real-time updates from the Budget backend
 * Part of the Budget UI Update Sprint implementation
 */
class BudgetWebSocketHandler {
    /**
     * Create a new WebSocket handler instance
     * @param {StateManager} stateManager - State manager instance
     */
    constructor(stateManager) {
        this.stateManager = stateManager;
        this.connections = {};
        this.reconnectTimeouts = {};
        this.reconnectAttempts = {};
        this.maxReconnectAttempts = 5;
        this.reconnectBaseDelay = 1000; // Start with 1 second delay
        this.messageHandlers = {};
        
        // Register message types
        this.registerMessageHandlers();
    }
    
    /**
     * Register message handlers for different WebSocket message types
     */
    registerMessageHandlers() {
        // Budget update handler
        this.messageHandlers['budget_update'] = (message) => {
            console.log('[BUDGET WS] Received budget update', message);
            
            // Update state with budget data
            if (message.payload && message.payload.summaries) {
                this.stateManager.updateBudgetSummaries(message.payload.summaries);
            }
        };
        
        // Alert handler
        this.messageHandlers['alert'] = (message) => {
            console.log('[BUDGET WS] Received alert', message);
            
            // Update state with alert data
            if (message.payload && message.payload.alerts) {
                this.stateManager.addAlerts(message.payload.alerts);
            }
        };
        
        // Allocation update handler
        this.messageHandlers['allocation_update'] = (message) => {
            console.log('[BUDGET WS] Received allocation update', message);
            
            // Update state with allocation data
            if (message.payload && message.payload.allocation) {
                this.stateManager.updateAllocation(message.payload.allocation);
            }
        };
        
        // Price update handler
        this.messageHandlers['price_update'] = (message) => {
            console.log('[BUDGET WS] Received price update', message);
            
            // Update state with price data
            if (message.payload && message.payload.update) {
                this.stateManager.updatePricing(
                    message.payload.provider,
                    message.payload.model,
                    message.payload.update
                );
            }
        };
        
        // Error handler
        this.messageHandlers['error'] = (message) => {
            console.error('[BUDGET WS] Received error', message);
        };
        
        // Heartbeat handler
        this.messageHandlers['heartbeat'] = (message) => {
            // No need to log heartbeats
        };
    }
    
    /**
     * Connect to a WebSocket endpoint
     * @param {string} endpoint - WebSocket endpoint
     * @param {string} topic - Topic identifier
     * @returns {WebSocket} WebSocket connection
     */
    connect(endpoint, topic) {
        if (this.connections[topic]) {
            // Connection already exists
            return this.connections[topic];
        }
        
        // Get WebSocket URL
        const hostname = window.location.hostname || 'localhost';
        const port = window.BUDGET_PORT || 8013;
        const wsUrl = `ws://${hostname}:${port}${endpoint}`;
        
        console.log(`[BUDGET WS] Connecting to ${wsUrl} for topic ${topic}`);
        
        // Create WebSocket connection
        const ws = new WebSocket(wsUrl);
        
        // Store connection
        this.connections[topic] = ws;
        this.reconnectAttempts[topic] = 0;
        
        // Set up event handlers
        ws.onopen = (event) => this.handleOpen(event, topic);
        ws.onclose = (event) => this.handleClose(event, topic);
        ws.onerror = (event) => this.handleError(event, topic);
        ws.onmessage = (event) => this.handleMessage(event, topic);
        
        return ws;
    }
    
    /**
     * Handle WebSocket open event
     * @param {Event} event - WebSocket event
     * @param {string} topic - Topic identifier
     */
    handleOpen(event, topic) {
        console.log(`[BUDGET WS] Connected to ${topic} WebSocket`);
        
        // Reset reconnect attempts
        this.reconnectAttempts[topic] = 0;
        
        // Send subscription message
        this.sendSubscription(topic);
        
        // Update state
        this.stateManager.setWebSocketState(topic, true);
    }
    
    /**
     * Handle WebSocket close event
     * @param {Event} event - WebSocket event
     * @param {string} topic - Topic identifier
     */
    handleClose(event, topic) {
        console.log(`[BUDGET WS] Disconnected from ${topic} WebSocket`, event.code, event.reason);
        
        // Update state
        this.stateManager.setWebSocketState(topic, false);
        
        // Clear connection
        this.connections[topic] = null;
        
        // Attempt to reconnect
        this.scheduleReconnect(topic);
    }
    
    /**
     * Handle WebSocket error event
     * @param {Event} event - WebSocket event
     * @param {string} topic - Topic identifier
     */
    handleError(event, topic) {
        console.error(`[BUDGET WS] Error in ${topic} WebSocket`, event);
        
        // Update state
        this.stateManager.setWebSocketState(topic, false);
    }
    
    /**
     * Handle WebSocket message event
     * @param {MessageEvent} event - WebSocket message event
     * @param {string} topic - Topic identifier
     */
    handleMessage(event, topic) {
        try {
            // Parse message
            const message = JSON.parse(event.data);
            
            // Call appropriate handler based on message type
            if (message.type && this.messageHandlers[message.type]) {
                this.messageHandlers[message.type](message);
            } else {
                console.log(`[BUDGET WS] Received ${topic} message:`, message);
            }
        } catch (error) {
            console.error(`[BUDGET WS] Error parsing ${topic} message:`, error, event.data);
        }
    }
    
    /**
     * Send a message over WebSocket
     * @param {string} topic - Topic identifier
     * @param {Object} message - Message object
     * @returns {boolean} True if message was sent
     */
    send(topic, message) {
        const ws = this.connections[topic];
        
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            console.warn(`[BUDGET WS] Cannot send to ${topic}: WebSocket not open`);
            return false;
        }
        
        try {
            ws.send(JSON.stringify(message));
            return true;
        } catch (error) {
            console.error(`[BUDGET WS] Error sending to ${topic}:`, error);
            return false;
        }
    }
    
    /**
     * Send a subscription message for a topic
     * @param {string} topic - Topic identifier
     */
    sendSubscription(topic) {
        const message = {
            type: 'subscription',
            topic: topic,
            payload: {
                topic: topic
            },
            timestamp: new Date().toISOString()
        };
        
        this.send(topic, message);
    }
    
    /**
     * Schedule a reconnection attempt
     * @param {string} topic - Topic identifier
     */
    scheduleReconnect(topic) {
        // Clear any existing reconnect timeout
        if (this.reconnectTimeouts[topic]) {
            clearTimeout(this.reconnectTimeouts[topic]);
        }
        
        // Increment reconnect attempts
        this.reconnectAttempts[topic] = (this.reconnectAttempts[topic] || 0) + 1;
        
        // Check if max reconnect attempts reached
        if (this.reconnectAttempts[topic] > this.maxReconnectAttempts) {
            console.warn(`[BUDGET WS] Max reconnect attempts reached for ${topic}`);
            return;
        }
        
        // Calculate exponential backoff delay
        const delay = Math.min(
            30000, // Max delay of 30 seconds
            this.reconnectBaseDelay * Math.pow(2, this.reconnectAttempts[topic] - 1)
        );
        
        console.log(`[BUDGET WS] Scheduling reconnect for ${topic} in ${delay}ms`);
        
        // Schedule reconnect
        this.reconnectTimeouts[topic] = setTimeout(() => {
            this.reconnectWebSocket(topic);
        }, delay);
    }
    
    /**
     * Reconnect a WebSocket
     * @param {string} topic - Topic identifier
     */
    reconnectWebSocket(topic) {
        // Get endpoint from topic
        let endpoint = '/ws/budget/updates';
        
        if (topic === 'budget_alerts') {
            endpoint = '/ws/budget/alerts';
        } else if (topic === 'allocation_updates') {
            endpoint = '/ws/budget/allocations';
        } else if (topic === 'price_updates') {
            endpoint = '/ws/budget/prices';
        }
        
        console.log(`[BUDGET WS] Reconnecting to ${topic} (${endpoint})`);
        
        // Connect
        this.connect(endpoint, topic);
    }
    
    /**
     * Close a WebSocket connection
     * @param {string} topic - Topic identifier
     */
    close(topic) {
        const ws = this.connections[topic];
        
        if (!ws) return;
        
        // Clear reconnect timeout
        if (this.reconnectTimeouts[topic]) {
            clearTimeout(this.reconnectTimeouts[topic]);
            this.reconnectTimeouts[topic] = null;
        }
        
        // Close WebSocket
        try {
            ws.close();
        } catch (error) {
            console.error(`[BUDGET WS] Error closing ${topic} WebSocket:`, error);
        }
        
        // Clear connection
        this.connections[topic] = null;
    }
    
    /**
     * Close all WebSocket connections
     */
    closeAll() {
        for (const topic in this.connections) {
            this.close(topic);
        }
    }
    
    /**
     * Connect to all Budget WebSocket endpoints
     */
    connectToAllEndpoints() {
        // Connect to budget updates
        this.connect('/ws/budget/updates', 'budget_events');
        
        // Connect to budget alerts
        this.connect('/ws/budget/alerts', 'budget_alerts');
        
        // Connect to allocation updates
        this.connect('/ws/budget/allocations', 'allocation_updates');
        
        // Connect to price updates
        this.connect('/ws/budget/prices', 'price_updates');
    }
    
    /**
     * Send a heartbeat to all connections
     */
    sendHeartbeats() {
        for (const topic in this.connections) {
            const ws = this.connections[topic];
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                const heartbeat = {
                    type: 'heartbeat',
                    topic: topic,
                    payload: {
                        timestamp: new Date().toISOString()
                    },
                    timestamp: new Date().toISOString()
                };
                
                this.send(topic, heartbeat);
            }
        }
    }
    
    /**
     * Start heartbeat interval
     * @param {number} interval - Heartbeat interval in milliseconds
     */
    startHeartbeat(interval = 30000) {
        // Clear any existing interval
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }
        
        // Set up new interval
        this.heartbeatInterval = setInterval(() => {
            this.sendHeartbeats();
        }, interval);
    }
    
    /**
     * Stop heartbeat interval
     */
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
}

// Export as global class
window.BudgetWebSocketHandler = BudgetWebSocketHandler;