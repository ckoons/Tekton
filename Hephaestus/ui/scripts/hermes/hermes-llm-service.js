/**
 * Hermes LLM Service
 * Provides communication with the Hermes LLM adapter
 */

class HermesLLMService extends window.tektonUI.componentUtils.BaseService {
    constructor() {
        // Call base service with service name and default API endpoint
        const hermesPort = window.HERMES_PORT || 8001;
        super('hermesLLMService', `http://localhost:${hermesPort}/api/llm`);
        
        // Track active chat
        this.chatHistory = [];
        this.isStreaming = false;
        this.currentStreamingMessage = '';
        this.currentRequestId = null;
        
        // WebSocket for streaming
        const hermesPort2 = window.HERMES_PORT || 8001;
        this.wsUrl = `ws://localhost:${hermesPort2}/api/llm/ws/chat`;
        this.ws = null;
        this.wsConnected = false;
        this.wsCallbacks = {};
        
        // Model configuration
        this.availableModels = [];
        this.currentProvider = 'anthropic';
        this.currentModel = 'claude-3-haiku-20240307';
        
        // Saved conversations
        this.savedConversations = [];
        
        // Initialize with persisted state if available
        this._loadPersistedState();
    }
    
    /**
     * Connect to the Hermes LLM API
     * @returns {Promise<boolean>} - Promise resolving to connection status
     */
    async connect() {
        try {
            // Get available providers and models
            const response = await fetch(`${this.apiUrl}/providers`);
            
            if (!response.ok) {
                this.connected = false;
                this.dispatchEvent('connectionFailed', { 
                    error: `Failed to connect to Hermes LLM API: ${response.status} ${response.statusText}` 
                });
                return false;
            }
            
            const data = await response.json();
            this.availableModels = data.providers;
            this.currentProvider = data.current_provider;
            this.currentModel = data.current_model;
            
            this.connected = true;
            this.dispatchEvent('connected', { providers: data.providers });
            
            // Connect to WebSocket for streaming if not already connected
            this._connectWebSocket();
            
            return true;
        } catch (error) {
            this.connected = false;
            this.dispatchEvent('connectionFailed', { error: `Failed to connect to Hermes LLM API: ${error.message}` });
            return false;
        }
    }
    
    /**
     * Connect to WebSocket for streaming
     * @private
     */
    _connectWebSocket() {
        if (this.ws) {
            return;
        }
        
        try {
            this.ws = new WebSocket(this.wsUrl);
            
            this.ws.onopen = () => {
                this.wsConnected = true;
                this.dispatchEvent('wsConnected');
            };
            
            this.ws.onclose = () => {
                this.wsConnected = false;
                this.ws = null;
                
                // Try to reconnect after a delay
                setTimeout(() => {
                    if (!this.ws) {
                        this._connectWebSocket();
                    }
                }, 5000);
                
                this.dispatchEvent('wsDisconnected');
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.dispatchEvent('wsError', { error });
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    
                    // Check if this is a response to a specific request
                    if (this.wsCallbacks[data.requestId]) {
                        this.wsCallbacks[data.requestId](data);
                        
                        // Clean up completed requests
                        if (data.done) {
                            delete this.wsCallbacks[data.requestId];
                        }
                    } else {
                        // Broadcast general message
                        this.dispatchEvent('wsMessage', { data });
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
        } catch (error) {
            console.error('Error connecting to WebSocket:', error);
            this.dispatchEvent('wsConnectionFailed', { error: error.message });
        }
    }
    
    /**
     * Send a chat message to the LLM
     * @param {string} message - The message to send
     * @param {boolean} useStreaming - Whether to use streaming for the response
     * @param {Object} options - Additional options (model, history, etc.)
     * @returns {Promise<Object>} - Promise resolving to the response
     */
    async sendChatMessage(message, useStreaming = true, options = {}) {
        if (!this.connected) {
            await this.connect();
        }
        
        // Prepare chat history
        const history = options.history || this.chatHistory;
        
        // Add user message to chat history
        const userMessage = {
            role: 'user',
            content: message,
            timestamp: Date.now()
        };
        
        this.chatHistory.push(userMessage);
        this.dispatchEvent('messageSent', { message: userMessage });
        
        if (useStreaming) {
            // Use WebSocket for streaming if available
            if (this.wsConnected) {
                return this._sendStreamingMessageWS(message, history, options);
            }
            
            // Fall back to SSE streaming
            return this._sendStreamingMessageSSE(message, history, options);
        } else {
            // Use regular HTTP request
            return this._sendRegularMessage(message, history, options);
        }
    }
    
    /**
     * Send a message using WebSocket streaming
     * @param {string} message - The message to send
     * @param {Array} history - Chat history
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} - Promise resolving when complete
     * @private
     */
    _sendStreamingMessageWS(message, history, options = {}) {
        return new Promise((resolve, reject) => {
            if (!this.wsConnected) {
                reject(new Error('WebSocket not connected'));
                return;
            }
            
            // Generate a request ID
            const requestId = Math.random().toString(36).substring(2, 15);
            
            // Track streaming state
            this.isStreaming = true;
            this.currentStreamingMessage = '';
            this.currentRequestId = requestId;
            
            // Prepare message data
            const messageData = {
                requestId,
                message,
                history: history.slice(0, -1), // Exclude the message we just added
                provider: options.provider || this.currentProvider,
                model: options.model || this.currentModel,
                topic: options.topic || 'general',
                style: options.style || 'balanced'
            };
            
            // Register callback for this request
            let fullResponse = '';
            
            this.wsCallbacks[requestId] = (data) => {
                if (data.error) {
                    this.isStreaming = false;
                    this.currentRequestId = null;
                    
                    this.dispatchEvent('streamingError', { 
                        error: data.error, 
                        requestId 
                    });
                    
                    reject(new Error(data.error));
                    return;
                }
                
                if (data.chunk) {
                    fullResponse += data.chunk;
                    this.currentStreamingMessage = fullResponse;
                    
                    this.dispatchEvent('streamingChunk', { 
                        chunk: data.chunk, 
                        fullResponse, 
                        requestId 
                    });
                }
                
                if (data.done) {
                    // Add assistant message to chat history
                    const assistantMessage = {
                        role: 'assistant',
                        content: fullResponse,
                        timestamp: Date.now(),
                        model: data.model || this.currentModel,
                        provider: data.provider || this.currentProvider
                    };
                    
                    this.chatHistory.push(assistantMessage);
                    
                    // Reset streaming state
                    this.isStreaming = false;
                    this.currentStreamingMessage = '';
                    this.currentRequestId = null;
                    
                    this.dispatchEvent('messageReceived', { message: assistantMessage });
                    this._persistState();
                    
                    resolve(assistantMessage);
                }
            };
            
            // Send the message via WebSocket
            this.ws.send(JSON.stringify(messageData));
        });
    }
    
    /**
     * Send a message using SSE streaming
     * @param {string} message - The message to send
     * @param {Array} history - Chat history
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} - Promise resolving when complete
     * @private
     */
    async _sendStreamingMessageSSE(message, history, options = {}) {
        try {
            // Track streaming state
            this.isStreaming = true;
            this.currentStreamingMessage = '';
            
            // Convert history format
            const formattedHistory = history.slice(0, -1).map(msg => ({
                role: msg.role,
                content: msg.content,
                timestamp: msg.timestamp
            }));
            
            // Prepare request parameters
            const requestParams = {
                message,
                history: formattedHistory,
                stream: true,
                model: options.model || this.currentModel,
                provider: options.provider || this.currentProvider
            };
            
            // Make streaming request
            const response = await fetch(`${this.apiUrl}/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestParams)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            // Read the stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullResponse = '';
            
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) {
                    break;
                }
                
                // Decode the chunk
                const chunk = decoder.decode(value, { stream: true });
                
                // Process SSE format (lines starting with "data: ")
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.substring(6); // Remove "data: " prefix
                        
                        if (data === '[DONE]') {
                            // End of stream
                            continue;
                        }
                        
                        try {
                            const parsed = JSON.parse(data);
                            
                            if (parsed.chunk) {
                                fullResponse += parsed.chunk;
                                this.currentStreamingMessage = fullResponse;
                                
                                this.dispatchEvent('streamingChunk', { 
                                    chunk: parsed.chunk, 
                                    fullResponse 
                                });
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                }
            }
            
            // Add assistant message to chat history
            const assistantMessage = {
                role: 'assistant',
                content: fullResponse,
                timestamp: Date.now(),
                model: this.currentModel,
                provider: this.currentProvider
            };
            
            this.chatHistory.push(assistantMessage);
            
            // Reset streaming state
            this.isStreaming = false;
            this.currentStreamingMessage = '';
            
            this.dispatchEvent('messageReceived', { message: assistantMessage });
            this._persistState();
            
            return assistantMessage;
        } catch (error) {
            this.isStreaming = false;
            this.dispatchEvent('streamingError', { error: error.message });
            throw error;
        }
    }
    
    /**
     * Send a message using regular HTTP request (no streaming)
     * @param {string} message - The message to send
     * @param {Array} history - Chat history
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} - Promise resolving to the response
     * @private
     */
    async _sendRegularMessage(message, history, options = {}) {
        try {
            // Convert history format
            const formattedHistory = history.slice(0, -1).map(msg => ({
                role: msg.role,
                content: msg.content,
                timestamp: msg.timestamp
            }));
            
            // Prepare request parameters
            const requestParams = {
                message,
                history: formattedHistory,
                stream: false,
                model: options.model || this.currentModel,
                provider: options.provider || this.currentProvider
            };
            
            // Make request
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestParams)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Add assistant message to chat history
            const assistantMessage = {
                role: 'assistant',
                content: data.message,
                timestamp: Date.now(),
                model: data.model,
                provider: data.provider
            };
            
            this.chatHistory.push(assistantMessage);
            this.dispatchEvent('messageReceived', { message: assistantMessage });
            this._persistState();
            
            return assistantMessage;
        } catch (error) {
            this.dispatchEvent('error', { error: error.message });
            throw error;
        }
    }
    
    /**
     * Cancel an ongoing streaming request
     * @returns {boolean} - Whether cancellation was successful
     */
    cancelStreaming() {
        if (!this.isStreaming) {
            return false;
        }
        
        if (this.wsConnected && this.currentRequestId) {
            // Send cancellation via WebSocket
            this.ws.send(JSON.stringify({
                requestId: this.currentRequestId,
                action: 'cancel'
            }));
            
            // Clean up
            delete this.wsCallbacks[this.currentRequestId];
        }
        
        // Reset streaming state
        this.isStreaming = false;
        this.currentStreamingMessage = '';
        this.currentRequestId = null;
        
        this.dispatchEvent('streamingCancelled');
        return true;
    }
    
    /**
     * Set the LLM provider and model
     * @param {string} provider - Provider ID
     * @param {string} model - Model ID
     * @returns {Promise<boolean>} - Promise resolving to success status
     */
    async setProviderAndModel(provider, model) {
        try {
            const response = await fetch(`${this.apiUrl}/provider?provider=${provider}&model=${model}`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.currentProvider = provider;
                this.currentModel = model;
                this.dispatchEvent('providerChanged', { provider, model });
                this._persistState();
                return true;
            }
            
            throw new Error('Failed to set provider and model');
        } catch (error) {
            this.dispatchEvent('error', { error: error.message });
            return false;
        }
    }
    
    /**
     * Clear the chat history
     */
    clearChat() {
        this.chatHistory = [];
        this.dispatchEvent('chatCleared');
        this._persistState();
    }
    
    /**
     * Save the current conversation
     * @param {string} name - Name for the saved conversation
     * @returns {string} - Conversation ID
     */
    saveConversation(name) {
        if (this.chatHistory.length === 0) {
            return null;
        }
        
        const id = Math.random().toString(36).substring(2, 15);
        const conversation = {
            id,
            name: name || `Conversation ${this.savedConversations.length + 1}`,
            timestamp: Date.now(),
            messages: [...this.chatHistory]
        };
        
        this.savedConversations.push(conversation);
        this.dispatchEvent('conversationSaved', { conversation });
        this._persistState();
        
        return id;
    }
    
    /**
     * Load a saved conversation
     * @param {string} id - Conversation ID
     * @returns {boolean} - Whether loading was successful
     */
    loadConversation(id) {
        const conversation = this.savedConversations.find(c => c.id === id);
        
        if (!conversation) {
            return false;
        }
        
        this.chatHistory = [...conversation.messages];
        this.dispatchEvent('conversationLoaded', { conversation });
        
        return true;
    }
    
    /**
     * Delete a saved conversation
     * @param {string} id - Conversation ID
     * @returns {boolean} - Whether deletion was successful
     */
    deleteConversation(id) {
        const index = this.savedConversations.findIndex(c => c.id === id);
        
        if (index === -1) {
            return false;
        }
        
        const conversation = this.savedConversations[index];
        this.savedConversations.splice(index, 1);
        
        this.dispatchEvent('conversationDeleted', { conversation });
        this._persistState();
        
        return true;
    }
    
    /**
     * Load persisted state
     * @private
     */
    _loadPersistedState() {
        try {
            const savedState = localStorage.getItem('hermesLLMService');
            
            if (!savedState) {
                return;
            }
            
            const state = JSON.parse(savedState);
            
            // Restore state properties
            this.currentProvider = state.currentProvider || this.currentProvider;
            this.currentModel = state.currentModel || this.currentModel;
            this.savedConversations = state.savedConversations || [];
            
            // Don't restore chat history by default, only saved conversations
        } catch (error) {
            console.error('Error loading persisted state:', error);
        }
    }
    
    /**
     * Persist current state
     * @private
     */
    _persistState() {
        try {
            const state = {
                currentProvider: this.currentProvider,
                currentModel: this.currentModel,
                savedConversations: this.savedConversations
            };
            
            localStorage.setItem('hermesLLMService', JSON.stringify(state));
        } catch (error) {
            console.error('Error persisting state:', error);
        }
    }
}

// Register service
window.tektonUI.componentUtils.registerService('HermesLLMService', HermesLLMService);