/**
 * WebSocket Service for Ergon
 * 
 * This service manages WebSocket connections for real-time updates
 * from Ergon agents and services.
 */

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectTimer = null;
    this.listeners = new Map();
    this.messageQueue = [];
  }

  /**
   * Connect to the WebSocket server
   * @returns {Promise} Resolves when connected
   */
  connect() {
    return new Promise((resolve, reject) => {
      try {
        // Close existing socket if it exists
        if (this.socket) {
          this.socket.close();
        }

        // Create new WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/ergon`;
        
        this.socket = new WebSocket(wsUrl);
        
        // Setup event handlers
        this.socket.onopen = () => {
          console.log('WebSocket connected');
          this.isConnected = true;
          
          // Send any queued messages
          while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this._sendMessage(message);
          }
          
          resolve();
        };
        
        this.socket.onclose = () => {
          console.log('WebSocket disconnected');
          this.isConnected = false;
          
          // Schedule reconnect
          this._scheduleReconnect();
        };
        
        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
        
        this.socket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this._handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
      } catch (error) {
        console.error('Error connecting to WebSocket:', error);
        reject(error);
        
        // Schedule reconnect
        this._scheduleReconnect();
      }
    });
  }

  /**
   * Schedule a reconnection attempt
   * @private
   */
  _scheduleReconnect() {
    // Clear any existing reconnect timer
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    
    // Schedule reconnect attempt
    this.reconnectTimer = setTimeout(() => {
      console.log('Attempting to reconnect WebSocket...');
      this.connect().catch(() => {
        // If reconnect fails, it will schedule another attempt
      });
    }, 5000); // Try to reconnect after 5 seconds
  }

  /**
   * Handle incoming messages
   * @param {Object} message Parsed message object
   * @private
   */
  _handleMessage(message) {
    const messageType = message.type;
    
    // Notify all listeners for this message type
    if (this.listeners.has(messageType)) {
      const handlers = this.listeners.get(messageType);
      handlers.forEach(handler => {
        try {
          handler(message.data);
        } catch (error) {
          console.error(`Error in WebSocket message handler for ${messageType}:`, error);
        }
      });
    }
    
    // Also notify 'all' listeners
    if (this.listeners.has('all')) {
      const handlers = this.listeners.get('all');
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error('Error in WebSocket catch-all handler:', error);
        }
      });
    }
  }

  /**
   * Send a message through the WebSocket
   * @param {Object} message Message to send
   * @private
   */
  _sendMessage(message) {
    if (this.isConnected && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      // Queue the message for later
      this.messageQueue.push(message);
      
      // Try to connect if not already connected
      if (!this.isConnected) {
        this.connect().catch(() => {
          // If connect fails, the reconnect scheduler will handle it
        });
      }
    }
  }

  /**
   * Send a message to the server
   * @param {string} type Message type
   * @param {Object} data Message data
   * @param {string} [requestId] Optional request ID for tracking responses
   */
  send(type, data, requestId = null) {
    const message = {
      type,
      data,
      requestId: requestId || this._generateRequestId()
    };
    
    this._sendMessage(message);
    return message.requestId;
  }

  /**
   * Generate a unique request ID
   * @returns {string} Unique ID
   * @private
   */
  _generateRequestId() {
    return 'req_' + Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  /**
   * Subscribe to a specific message type
   * @param {string} type Message type to listen for
   * @param {Function} handler Function to call when message is received
   * @returns {Function} Unsubscribe function
   */
  subscribe(type, handler) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    
    const handlers = this.listeners.get(type);
    handlers.add(handler);
    
    // Return unsubscribe function
    return () => {
      if (this.listeners.has(type)) {
        const handlers = this.listeners.get(type);
        handlers.delete(handler);
        
        // Clean up if no handlers left
        if (handlers.size === 0) {
          this.listeners.delete(type);
        }
      }
    };
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    this.isConnected = false;
  }
}

// Create and export a singleton instance
const websocketService = new WebSocketService();
export default websocketService;