/**
 * Engram LLM Service
 * 
 * Provides a client for interacting with the Engram LLM API.
 * Handles chat messages, streaming, and memory operations.
 */

(function() {
    'use strict';

    // Service class
    class EngramLLMService {
        constructor() {
            // Service configuration
            const engramPort = window.ENGRAM_PORT || 8000;
            this.baseUrl = `http://localhost:${engramPort}`; // Dynamic Engram port
            this.wsUrl = `ws://localhost:${engramPort}`;
            this.websocket = null;
            this.isConnected = false;
            this.isConnecting = false;
            
            // Chat state
            this.chatHistory = [];
            this.currentStreamResponse = '';
            this.streamingEnabled = true;
            this.currentProvider = 'anthropic';
            this.currentModel = 'claude-3-haiku-20240307';
            this.availableModels = {
                'anthropic': [
                    { id: 'claude-3-haiku-20240307', name: 'Claude 3 Haiku' },
                    { id: 'claude-3-sonnet-20240229', name: 'Claude 3 Sonnet' }
                ]
            };
            
            // Memory namespaces
            this.availableNamespaces = ['conversations', 'thinking', 'longterm'];
            this.activeNamespace = 'conversations';
            
            // Event system
            this.eventListeners = {};
            
            // Saved conversations
            this.savedConversations = [];
            
            // Initialize environment variables
            this._initializeEnvironment();
        }
        
        /**
         * Initialize environment variables from global configuration
         */
        _initializeEnvironment() {
            // Check for global Tekton configuration
            if (window.tektonConfig && window.tektonConfig.engram) {
                const config = window.tektonConfig.engram;
                
                if (config.apiUrl) {
                    this.baseUrl = config.apiUrl;
                    this.wsUrl = this.baseUrl.replace('http://', 'ws://').replace('https://', 'wss://');
                }
                
                if (config.provider) {
                    this.currentProvider = config.provider;
                }
                
                if (config.model) {
                    this.currentModel = config.model;
                }
                
                if (config.namespaces && Array.isArray(config.namespaces)) {
                    this.availableNamespaces = config.namespaces;
                }
            }
            
            // Override with URL parameters if present
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('engram_url')) {
                this.baseUrl = urlParams.get('engram_url');
                this.wsUrl = this.baseUrl.replace('http://', 'ws://').replace('https://', 'wss://');
            }
            
            console.log('Engram LLM Service initialized with:', {
                baseUrl: this.baseUrl,
                wsUrl: this.wsUrl,
                provider: this.currentProvider,
                model: this.currentModel
            });
        }
        
        /**
         * Connect to the Engram service
         * @returns {Promise<boolean>} - Whether connection was successful
         */
        async connect() {
            console.log('Connecting to Engram LLM service...');
            
            if (this.isConnected) {
                console.log('Already connected to Engram LLM service');
                return true;
            }
            
            if (this.isConnecting) {
                console.log('Connection attempt already in progress');
                return false;
            }
            
            this.isConnecting = true;
            
            try {
                // Test connection with a simple models request
                const response = await fetch(`${this.baseUrl}/v1/llm/models`);
                
                if (response.ok) {
                    const models = await response.json();
                    this.availableModels = models;
                    this.isConnected = true;
                    
                    // Trigger connected event
                    this._triggerEvent('connected', {});
                    
                    // Load saved conversations
                    this._loadSavedConversations();
                    
                    console.log('Connected to Engram LLM service');
                    return true;
                } else {
                    throw new Error(`Failed to connect: ${response.status} ${response.statusText}`);
                }
            } catch (error) {
                console.error('Failed to connect to Engram LLM service:', error);
                
                // Trigger connection failed event
                this._triggerEvent('connectionFailed', { error: error.message });
                
                return false;
            } finally {
                this.isConnecting = false;
            }
        }
        
        /**
         * Send a chat message and get a response
         * @param {string} message - User message
         * @param {boolean} useStreaming - Whether to use streaming
         * @param {Object} options - Additional options
         * @returns {Promise<string>} - Response message
         */
        async sendChatMessage(message, useStreaming = true, options = {}) {
            if (!this.isConnected) {
                try {
                    const connected = await this.connect();
                    if (!connected) {
                        throw new Error('Cannot send message: Not connected to Engram LLM service');
                    }
                } catch (error) {
                    console.error('Connection error:', error);
                    throw error;
                }
            }
            
            // Add user message to chat history
            const userMessage = {
                role: 'user',
                content: message,
                timestamp: new Date().toISOString()
            };
            
            this.chatHistory.push(userMessage);
            
            // Trigger message sent event
            this._triggerEvent('messageSent', { message: userMessage });
            
            // Get options
            const model = options.model || this.currentModel;
            const temperature = options.temperature || 0.7;
            const namespace = options.namespace || this.activeNamespace;
            
            // Format messages for API request
            const messages = this.chatHistory.map(msg => ({
                role: msg.role,
                content: msg.content
            }));
            
            // Determine whether to use streaming based on setting and option
            const streamingEnabled = (useStreaming !== undefined) ? useStreaming : this.streamingEnabled;
            
            try {
                if (streamingEnabled) {
                    // Use streaming API
                    return this._streamChatMessage(messages, model, temperature, namespace);
                } else {
                    // Use non-streaming API
                    const requestData = {
                        messages: messages,
                        model: model,
                        temperature: temperature,
                        memory_namespace: namespace
                    };
                    
                    const response = await fetch(`${this.baseUrl}/v1/llm/chat`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(requestData)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`Chat request failed: ${response.status} ${response.statusText}`);
                    }
                    
                    const result = await response.json();
                    const responseMessage = {
                        role: 'assistant',
                        content: result.content,
                        timestamp: new Date().toISOString(),
                        model: result.model
                    };
                    
                    // Add response to chat history
                    this.chatHistory.push(responseMessage);
                    
                    // Trigger message received event
                    this._triggerEvent('messageReceived', { message: responseMessage });
                    
                    return result.content;
                }
            } catch (error) {
                console.error('Chat error:', error);
                
                // Trigger error event
                this._triggerEvent('error', { error: error.message });
                
                throw error;
            }
        }
        
        /**
         * Stream a chat message response
         * @param {Array} messages - Chat messages
         * @param {string} model - Model to use
         * @param {number} temperature - Temperature parameter
         * @param {string} namespace - Memory namespace
         * @returns {Promise<string>} - Full response when complete
         */
        async _streamChatMessage(messages, model, temperature, namespace) {
            // Reset current stream response
            this.currentStreamResponse = '';
            
            try {
                // Create request URL with query parameters
                const requestData = {
                    messages: messages,
                    model: model,
                    temperature: temperature,
                    stream: true,
                    memory_namespace: namespace
                };
                
                // Use fetch with streaming
                const response = await fetch(`${this.baseUrl}/v1/llm/chat/stream`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestData)
                });
                
                if (!response.ok) {
                    throw new Error(`Streaming request failed: ${response.status} ${response.statusText}`);
                }
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                
                let completeResponse = '';
                
                while (true) {
                    const { value, done } = await reader.read();
                    
                    if (done) {
                        break;
                    }
                    
                    // Decode the chunk
                    const chunk = decoder.decode(value);
                    
                    // Process SSE format (data: {...}\n\n)
                    const lines = chunk.split('\n\n');
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                
                                if (data.content) {
                                    // Add to complete response
                                    completeResponse += data.content;
                                    
                                    // Trigger streaming chunk event
                                    this._triggerEvent('streamingChunk', {
                                        chunk: data.content,
                                        fullResponse: completeResponse
                                    });
                                } else if (data.type === 'done') {
                                    // Stream complete
                                    const responseMessage = {
                                        role: 'assistant',
                                        content: completeResponse,
                                        timestamp: new Date().toISOString(),
                                        model: model
                                    };
                                    
                                    // Add to chat history
                                    this.chatHistory.push(responseMessage);
                                    
                                    // Trigger message received event
                                    this._triggerEvent('messageReceived', { message: responseMessage });
                                }
                            } catch (e) {
                                console.error('Error parsing SSE data:', e);
                            }
                        }
                    }
                }
                
                return completeResponse;
                
            } catch (error) {
                console.error('Streaming error:', error);
                
                // Trigger error event
                this._triggerEvent('streamingError', { error: error.message });
                
                throw error;
            }
        }
        
        /**
         * Set provider and model
         * @param {string} provider - Provider ID
         * @param {string} model - Model ID
         */
        setProviderAndModel(provider, model) {
            this.currentProvider = provider;
            this.currentModel = model;
            console.log(`Set model to ${provider}/${model}`);
        }
        
        /**
         * Set active memory namespace
         * @param {string} namespace - Namespace to use
         */
        setNamespace(namespace) {
            if (this.availableNamespaces.includes(namespace)) {
                this.activeNamespace = namespace;
                console.log(`Set namespace to ${namespace}`);
            } else {
                console.error(`Unknown namespace: ${namespace}`);
            }
        }
        
        /**
         * Clear chat history
         */
        clearChat() {
            this.chatHistory = [];
            this._triggerEvent('chatCleared', {});
        }
        
        /**
         * Save current conversation
         * @param {string} name - Conversation name
         * @returns {string} - Conversation ID
         */
        saveConversation(name) {
            if (this.chatHistory.length === 0) {
                throw new Error('Cannot save empty conversation');
            }
            
            const id = Date.now().toString(36) + Math.random().toString(36).substring(2);
            const conversation = {
                id: id,
                name: name,
                timestamp: Date.now(),
                messages: [...this.chatHistory],
                model: this.currentModel
            };
            
            // Add to saved conversations
            this.savedConversations.push(conversation);
            
            // Save to localStorage
            this._saveSavedConversations();
            
            // Trigger event
            this._triggerEvent('conversationSaved', { conversation });
            
            return id;
        }
        
        /**
         * Load a saved conversation
         * @param {string} id - Conversation ID
         */
        loadConversation(id) {
            const conversation = this.savedConversations.find(c => c.id === id);
            
            if (!conversation) {
                throw new Error(`Conversation not found: ${id}`);
            }
            
            // Set as current chat history
            this.chatHistory = [...conversation.messages];
            
            // Update model if needed
            if (conversation.model) {
                this.currentModel = conversation.model;
            }
            
            // Trigger event
            this._triggerEvent('conversationLoaded', { conversation });
        }
        
        /**
         * Delete a saved conversation
         * @param {string} id - Conversation ID
         */
        deleteConversation(id) {
            const index = this.savedConversations.findIndex(c => c.id === id);
            
            if (index === -1) {
                throw new Error(`Conversation not found: ${id}`);
            }
            
            // Remove from array
            this.savedConversations.splice(index, 1);
            
            // Save to localStorage
            this._saveSavedConversations();
            
            // Trigger event
            this._triggerEvent('conversationDeleted', { id });
        }
        
        /**
         * Save conversations to localStorage
         */
        _saveSavedConversations() {
            try {
                localStorage.setItem('engram_conversations', JSON.stringify(this.savedConversations));
            } catch (error) {
                console.error('Error saving conversations:', error);
            }
        }
        
        /**
         * Load saved conversations from localStorage
         */
        _loadSavedConversations() {
            try {
                const saved = localStorage.getItem('engram_conversations');
                if (saved) {
                    this.savedConversations = JSON.parse(saved);
                    console.log(`Loaded ${this.savedConversations.length} saved conversations`);
                }
            } catch (error) {
                console.error('Error loading saved conversations:', error);
            }
        }
        
        /**
         * Add event listener
         * @param {string} event - Event name
         * @param {Function} callback - Callback function
         */
        addEventListener(event, callback) {
            if (!this.eventListeners[event]) {
                this.eventListeners[event] = [];
            }
            
            this.eventListeners[event].push(callback);
        }
        
        /**
         * Remove event listener
         * @param {string} event - Event name
         * @param {Function} callback - Callback function
         */
        removeEventListener(event, callback) {
            if (!this.eventListeners[event]) {
                return;
            }
            
            this.eventListeners[event] = this.eventListeners[event].filter(cb => cb !== callback);
        }
        
        /**
         * Trigger event
         * @param {string} event - Event name
         * @param {Object} data - Event data
         */
        _triggerEvent(event, data) {
            if (!this.eventListeners[event]) {
                return;
            }
            
            const eventObj = new CustomEvent(event, { detail: data });
            
            this.eventListeners[event].forEach(callback => {
                callback(eventObj);
            });
        }
    }
    
    // Create and export service
    if (!window.tektonUI) {
        window.tektonUI = {};
    }
    
    if (!window.tektonUI.services) {
        window.tektonUI.services = {};
    }
    
    // Create singleton instance
    window.tektonUI.services.engramLLMService = new EngramLLMService();
    
    console.log('Engram LLM Service registered');
})();