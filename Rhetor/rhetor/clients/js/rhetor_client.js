/**
 * Rhetor JavaScript Client for Tekton
 * 
 * This client provides a JavaScript interface to the Rhetor LLM Management System,
 * enabling web-based applications to interact with language models seamlessly.
 */

/**
 * Main Rhetor client class
 */
class RhetorClient {
  /**
   * Create a new Rhetor client
   * 
   * @param {Object} options - Configuration options
   * @param {string} [options.rhetorUrl='http://localhost:8003'] - Base URL for Rhetor API
   * @param {string} [options.componentId='frontend'] - Component ID for tracking
   * @param {string} [options.defaultContext=null] - Default context ID to use
   * @param {boolean} [options.autoReconnect=true] - Whether to automatically reconnect WebSocket
   * @param {number} [options.reconnectDelay=2000] - Time in ms to wait before reconnecting
   * @param {number} [options.maxReconnectAttempts=10] - Maximum number of reconnection attempts
   */
  constructor(options = {}) {
    this.rhetorUrl = options.rhetorUrl || 'http://localhost:8003';
    this.wsUrl = options.rhetorUrl?.replace(/^http/, 'ws') || 'ws://localhost:8003';
    this.componentId = options.componentId || 'frontend';
    this.defaultContext = options.defaultContext || `${this.componentId}:default`;
    this.autoReconnect = options.autoReconnect !== false;
    this.reconnectDelay = options.reconnectDelay || 2000;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
    
    // Internal state
    this.ws = null;
    this.wsConnected = false;
    this.reconnectAttempts = 0;
    this.pendingRequests = new Map();
    this.eventHandlers = {
      message: [],
      error: [],
      connection: [],
      typing: []
    };
  }

  /**
   * Connect to Rhetor WebSocket and REST API
   * 
   * @returns {Promise<boolean>} Connection success status
   */
  async connect() {
    try {
      // First check if the HTTP API is available
      const healthCheck = await fetch(`${this.rhetorUrl}/health`);
      if (!healthCheck.ok) {
        console.error('Rhetor API is not available');
        return false;
      }
      
      // Then connect to WebSocket
      await this._connectWebSocket();
      return true;
    } catch (error) {
      console.error('Error connecting to Rhetor:', error);
      return false;
    }
  }
  
  /**
   * Establish WebSocket connection
   * 
   * @private
   * @returns {Promise<void>}
   */
  async _connectWebSocket() {
    return new Promise((resolve, reject) => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.wsConnected = true;
        resolve();
        return;
      }
      
      this.ws = new WebSocket(`${this.wsUrl}/ws`);
      
      this.ws.onopen = () => {
        console.log('Connected to Rhetor WebSocket');
        this.wsConnected = true;
        this.reconnectAttempts = 0;
        
        // Register with server
        this.ws.send(JSON.stringify({
          type: 'REGISTER',
          source: this.componentId,
          timestamp: new Date().toISOString(),
          payload: {
            component_id: this.componentId
          }
        }));
        
        // Call connection handlers
        this.eventHandlers.connection.forEach(handler => {
          try {
            handler(true);
          } catch (error) {
            console.error('Error in connection handler:', error);
          }
        });
        
        resolve();
      };
      
      this.ws.onclose = () => {
        console.log('Disconnected from Rhetor WebSocket');
        this.wsConnected = false;
        
        // Call connection handlers
        this.eventHandlers.connection.forEach(handler => {
          try {
            handler(false);
          } catch (error) {
            console.error('Error in connection handler:', error);
          }
        });
        
        // Try to reconnect
        if (this.autoReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`Reconnecting to Rhetor (attempt ${this.reconnectAttempts})...`);
          setTimeout(() => this._connectWebSocket(), this.reconnectDelay);
        }
        
        reject(new Error('WebSocket connection closed'));
      };
      
      this.ws.onerror = (error) => {
        console.error('Rhetor WebSocket error:', error);
        
        // Call error handlers
        this.eventHandlers.error.forEach(handler => {
          try {
            handler(error);
          } catch (handlerError) {
            console.error('Error in error handler:', handlerError);
          }
        });
        
        reject(error);
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle various message types
          if (data.type === 'RESPONSE') {
            // Handle response to a request
            const requestId = data.req_id;
            if (requestId && this.pendingRequests.has(requestId)) {
              const { resolve } = this.pendingRequests.get(requestId);
              this.pendingRequests.delete(requestId);
              resolve(data.payload);
            }
            
            // Call message handlers
            this.eventHandlers.message.forEach(handler => {
              try {
                handler(data);
              } catch (error) {
                console.error('Error in message handler:', error);
              }
            });
          } else if (data.type === 'UPDATE') {
            // Special handler for typing indicators
            if (data.payload && typeof data.payload.isTyping !== 'undefined') {
              this.eventHandlers.typing.forEach(handler => {
                try {
                  handler(data.payload.isTyping, data.payload.context);
                } catch (error) {
                  console.error('Error in typing handler:', error);
                }
              });
            }
            
            // Call message handlers
            this.eventHandlers.message.forEach(handler => {
              try {
                handler(data);
              } catch (error) {
                console.error('Error in message handler:', error);
              }
            });
          } else if (data.type === 'ERROR') {
            // Handle error response
            const requestId = data.req_id;
            if (requestId && this.pendingRequests.has(requestId)) {
              const { reject } = this.pendingRequests.get(requestId);
              this.pendingRequests.delete(requestId);
              reject(new Error(data.payload.error || 'Unknown error'));
            }
            
            // Call error handlers
            this.eventHandlers.error.forEach(handler => {
              try {
                handler(data.payload);
              } catch (error) {
                console.error('Error in error handler:', error);
              }
            });
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    });
  }
  
  /**
   * Disconnect from Rhetor
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.wsConnected = false;
    }
  }
  
  /**
   * Register an event handler
   * 
   * @param {string} event - Event name ('message', 'error', 'connection', or 'typing')
   * @param {Function} handler - Handler function
   */
  on(event, handler) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].push(handler);
    }
  }
  
  /**
   * Remove an event handler
   * 
   * @param {string} event - Event name
   * @param {Function} handler - Handler to remove
   */
  off(event, handler) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event] = this.eventHandlers[event].filter(h => h !== handler);
    }
  }
  
  /**
   * Get available LLM providers
   * 
   * @returns {Promise<Object>} Available providers and models
   */
  async getProviders() {
    const response = await fetch(`${this.rhetorUrl}/providers`);
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    return response.json();
  }
  
  /**
   * Set the active provider and model
   * 
   * @param {string} providerId - Provider ID
   * @param {string} modelId - Model ID
   * @returns {Promise<boolean>} Success status
   */
  async setProvider(providerId, modelId) {
    const response = await fetch(`${this.rhetorUrl}/provider`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        provider_id: providerId,
        model_id: modelId
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    const result = await response.json();
    return result.success;
  }
  
  /**
   * Send a message and get a response via WebSocket (streaming)
   * 
   * @param {string} message - Message text
   * @param {Object} options - Options
   * @param {string} [options.contextId] - Context ID
   * @param {string} [options.taskType='default'] - Task type
   * @param {Object} [options.llmOptions={}] - LLM-specific options
   * @returns {Promise<string>} Complete response text
   */
  async sendMessage(message, options = {}) {
    if (!this.wsConnected) {
      await this._connectWebSocket();
    }
    
    const contextId = options.contextId || this.defaultContext;
    const taskType = options.taskType || 'default';
    const llmOptions = options.llmOptions || {};
    
    // Create a unique request ID
    const requestId = `${this.componentId}:${Date.now()}`;
    
    // Create request message
    const request = {
      type: 'LLM_REQUEST',
      source: this.componentId,
      req_id: requestId,
      timestamp: new Date().toISOString(),
      payload: {
        message: message,
        context: contextId,
        task_type: taskType,
        component: this.componentId,
        streaming: true,
        options: llmOptions
      }
    };
    
    // Set up promise to track chunks
    return new Promise((resolve, reject) => {
      let fullResponse = '';
      
      // Accumulate chunks
      const chunkHandler = (data) => {
        if (data.req_id === requestId && data.type === 'UPDATE') {
          const payload = data.payload || {};
          
          if (payload.error) {
            // Remove handler
            this.off('message', chunkHandler);
            reject(new Error(payload.error));
            return;
          }
          
          if (payload.chunk) {
            fullResponse += payload.chunk;
          }
          
          if (payload.done) {
            // Remove handler
            this.off('message', chunkHandler);
            resolve(fullResponse);
          }
        }
      };
      
      // Add handler
      this.on('message', chunkHandler);
      
      // Register error handler
      const errorHandler = (errorData) => {
        if (errorData.req_id === requestId) {
          // Remove handlers
          this.off('message', chunkHandler);
          this.off('error', errorHandler);
          reject(new Error(errorData.error || 'Unknown error'));
        }
      };
      
      this.on('error', errorHandler);
      
      // Send the request
      this.ws.send(JSON.stringify(request));
    });
  }
  
  /**
   * Send a message and get a non-streaming response via REST API
   * 
   * @param {string} message - Message text
   * @param {Object} options - Options
   * @param {string} [options.contextId] - Context ID
   * @param {string} [options.taskType='default'] - Task type
   * @param {Object} [options.llmOptions={}] - LLM-specific options
   * @returns {Promise<Object>} Complete response object
   */
  async completeMessage(message, options = {}) {
    const contextId = options.contextId || this.defaultContext;
    const taskType = options.taskType || 'default';
    const llmOptions = options.llmOptions || {};
    
    const response = await fetch(`${this.rhetorUrl}/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: message,
        context_id: contextId,
        task_type: taskType,
        component: this.componentId,
        streaming: false,
        options: llmOptions
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    return response.json();
  }
  
  /**
   * Stream a response via EventSource (Server-Sent Events)
   * 
   * @param {string} message - Message text
   * @param {Object} options - Options
   * @param {string} [options.contextId] - Context ID
   * @param {string} [options.taskType='default'] - Task type
   * @param {Object} [options.llmOptions={}] - LLM-specific options
   * @param {Function} options.onChunk - Callback for each chunk (required)
   * @param {Function} [options.onDone] - Callback when streaming is complete
   * @param {Function} [options.onError] - Callback for errors
   */
  streamMessage(message, options = {}) {
    const contextId = options.contextId || this.defaultContext;
    const taskType = options.taskType || 'default';
    const llmOptions = options.llmOptions || {};
    const onChunk = options.onChunk || (() => {});
    const onDone = options.onDone || (() => {});
    const onError = options.onError || ((error) => { console.error(error); });
    
    // Create request body
    const requestBody = JSON.stringify({
      message: message,
      context_id: contextId,
      task_type: taskType,
      component: this.componentId,
      options: llmOptions
    });
    
    // Create EventSource request
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${this.rhetorUrl}/stream`, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Accept', 'text/event-stream');
    xhr.send(requestBody);
    
    // Set up event handling
    xhr.onreadystatechange = () => {
      if (xhr.readyState > 2) {
        const lines = xhr.responseText.split('\n');
        let fullResponse = '';
        let complete = false;
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6));
              
              if (data.error) {
                onError(new Error(data.error));
                complete = true;
                break;
              }
              
              if (data.chunk) {
                fullResponse += data.chunk;
                onChunk(data.chunk, data);
              }
              
              if (data.done) {
                complete = true;
                break;
              }
            } catch (error) {
              console.warn('Error parsing SSE chunk:', error);
            }
          }
        }
        
        if (complete) {
          onDone(fullResponse);
          xhr.abort();
        }
      }
    };
    
    xhr.onerror = (error) => {
      onError(error);
    };
    
    // Return a function to cancel the stream
    return () => {
      xhr.abort();
    };
  }
  
  /**
   * Convenience method to ask a question and get a response
   * 
   * @param {string} question - Question to ask
   * @param {Object} [options={}] - Options
   * @returns {Promise<string>} Response text
   */
  async ask(question, options = {}) {
    if (options.stream) {
      return this.sendMessage(question, {
        contextId: options.contextId,
        taskType: 'chat',
        llmOptions: options.llmOptions
      });
    } else {
      const response = await this.completeMessage(question, {
        contextId: options.contextId,
        taskType: 'chat',
        llmOptions: options.llmOptions
      });
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      return response.message;
    }
  }
  
  /**
   * Convenience method to generate code
   * 
   * @param {string} task - Coding task description
   * @param {Object} [options={}] - Options
   * @returns {Promise<string>} Generated code
   */
  async code(task, options = {}) {
    // Set default options for code generation
    const codeOptions = {
      temperature: 0.2,
      max_tokens: 2000,
      ...options.llmOptions
    };
    
    if (options.stream) {
      return this.sendMessage(task, {
        contextId: options.contextId,
        taskType: 'code',
        llmOptions: codeOptions
      });
    } else {
      const response = await this.completeMessage(task, {
        contextId: options.contextId,
        taskType: 'code',
        llmOptions: codeOptions
      });
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      return response.message;
    }
  }
}

// Export in a way that works in both browser and Node.js
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
  module.exports = { RhetorClient };
} else {
  window.RhetorClient = RhetorClient;
}