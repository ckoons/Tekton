/**
 * Tekton LLM Client for Browser
 * A unified client for interacting with the Tekton LLM services in the browser.
 */

class TektonLLMClient {
    /**
     * Create a new TektonLLMClient instance.
     * @param {Object} options - Configuration options
     * @param {string} options.componentId - ID of the component using the client (for tracking)
     * @param {string} [options.rhetorUrl='/api/llm'] - URL for the Rhetor API
     * @param {string} [options.rhetorWsUrl] - WebSocket URL for Rhetor API (defaults to converted HTTP URL)
     * @param {string} [options.providerId] - Default provider ID
     * @param {string} [options.modelId] - Default model ID
     * @param {number} [options.timeout=30] - Request timeout in seconds
     * @param {string} [options.authToken] - Authentication token for Rhetor API
     */
    constructor(options = {}) {
        // Initialize properties
        this.componentId = options.componentId || 'browser-client';
        this.rhetorUrl = options.rhetorUrl || '/api/llm';
        this.providerId = options.providerId || 'anthropic';
        this.modelId = options.modelId || null;
        this.timeout = options.timeout || 30;
        this.authToken = options.authToken || null;
        
        // Compute WebSocket URL if not provided
        if (!options.rhetorWsUrl) {
            if (this.rhetorUrl.startsWith('https://')) {
                this.rhetorWsUrl = this.rhetorUrl.replace('https://', 'wss://');
            } else if (this.rhetorUrl.startsWith('http://')) {
                this.rhetorWsUrl = this.rhetorUrl.replace('http://', 'ws://');
            } else {
                // Assume it's a relative path
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const host = window.location.host;
                this.rhetorWsUrl = `${protocol}//${host}${this.rhetorUrl}`;
            }
            
            // Append /ws if not already present
            if (!this.rhetorWsUrl.endsWith('/ws')) {
                this.rhetorWsUrl = this.rhetorWsUrl.replace(/\/$/, '') + '/ws';
            }
        } else {
            this.rhetorWsUrl = options.rhetorWsUrl;
        }
        
        // Initialize WebSocket connection (lazy, will connect when needed)
        this.ws = null;
        this.wsConnected = false;
        this.wsConnecting = false;
        this.wsCallbacks = new Map();
        this.pendingRequests = new Map();
        
        // Debug level
        this.debug = options.debug || false;
        
        this._log('Initialized TektonLLMClient', {
            componentId: this.componentId,
            rhetorUrl: this.rhetorUrl,
            rhetorWsUrl: this.rhetorWsUrl,
            providerId: this.providerId,
            modelId: this.modelId
        });
    }
    
    /**
     * Generate text using the LLM.
     * @param {string} prompt - The user prompt
     * @param {Object} [options] - Additional options
     * @param {string} [options.systemPrompt] - System instructions
     * @param {string} [options.providerId] - Provider ID (overrides default)
     * @param {string} [options.modelId] - Model ID (overrides default)
     * @param {string} [options.contextId] - Context ID (defaults to componentId)
     * @param {number} [options.temperature=0.7] - Temperature parameter
     * @param {number} [options.maxTokens] - Maximum tokens to generate
     * @param {Array<string>} [options.stopSequences] - Sequences to stop generation
     * @param {number} [options.timeout] - Request timeout in seconds
     * @returns {Promise<Object>} - The LLM response
     */
    async generateText(prompt, options = {}) {
        // Create message from prompt
        const message = { role: 'user', content: prompt };
        
        // Process system prompt if provided
        const messages = [];
        if (options.systemPrompt) {
            messages.push({ role: 'system', content: options.systemPrompt });
        }
        messages.push(message);
        
        // Use the chat method with a single user message
        return this.generateChatResponse(messages, options);
    }
    
    /**
     * Generate a chat response using the LLM.
     * @param {Array<Object>} messages - Array of message objects with role and content
     * @param {Object} [options] - Additional options
     * @param {string} [options.providerId] - Provider ID (overrides default)
     * @param {string} [options.modelId] - Model ID (overrides default)
     * @param {string} [options.contextId] - Context ID (defaults to componentId)
     * @param {number} [options.temperature=0.7] - Temperature parameter
     * @param {number} [options.maxTokens] - Maximum tokens to generate
     * @param {Array<string>} [options.stopSequences] - Sequences to stop generation
     * @param {number} [options.timeout] - Request timeout in seconds
     * @returns {Promise<Object>} - The LLM response
     */
    async generateChatResponse(messages, options = {}) {
        const contextId = options.contextId || this.componentId;
        const providerId = options.providerId || this.providerId;
        const modelId = options.modelId || this.modelId;
        const temperature = options.temperature ?? 0.7;
        
        // Construct request payload
        const payload = {
            messages,
            context_id: contextId,
            provider_id: providerId,
            streaming: false,
            options: {
                temperature
            }
        };
        
        if (modelId) {
            payload.model_id = modelId;
        }
        
        if (options.maxTokens) {
            payload.options.max_tokens = options.maxTokens;
        }
        
        if (options.stopSequences) {
            payload.options.stop = options.stopSequences;
        }
        
        // Create AbortController for timeout
        const controller = new AbortController();
        const timeoutMs = (options.timeout || this.timeout) * 1000;
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
        
        try {
            // Send the request
            const response = await fetch(`${this.rhetorUrl}/api/v1/chat`, {
                method: 'POST',
                headers: this._getHeaders(),
                body: JSON.stringify(payload),
                signal: controller.signal
            });
            
            // Clear timeout
            clearTimeout(timeoutId);
            
            // Check for errors
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(`HTTP error ${response.status}: ${errorData.error || 'Unknown error'}`);
            }
            
            // Parse response
            const data = await response.json();
            
            return {
                content: data.content || '',
                model: data.model || modelId,
                provider: data.provider || providerId,
                finishReason: data.finish_reason,
                usage: data.usage,
                contextId: data.context_id || contextId,
                timestamp: data.timestamp || new Date().toISOString()
            };
        } catch (error) {
            this._log('Error generating chat response', error);
            
            if (error.name === 'AbortError') {
                throw new Error(`Request timed out after ${timeoutMs / 1000} seconds`);
            }
            
            throw error;
        }
    }
    
    /**
     * Stream text using the LLM.
     * @param {string} prompt - The user prompt
     * @param {function} onChunk - Callback for each chunk of text
     * @param {Object} [options] - Additional options
     * @param {string} [options.systemPrompt] - System instructions
     * @param {string} [options.providerId] - Provider ID (overrides default)
     * @param {string} [options.modelId] - Model ID (overrides default)
     * @param {string} [options.contextId] - Context ID (defaults to componentId)
     * @param {number} [options.temperature=0.7] - Temperature parameter
     * @param {number} [options.maxTokens] - Maximum tokens to generate
     * @param {Array<string>} [options.stopSequences] - Sequences to stop generation
     * @param {function} [options.onComplete] - Callback when streaming is complete
     * @param {function} [options.onError] - Callback for streaming errors
     * @returns {string} - Request ID that can be used to cancel the request
     */
    streamText(prompt, onChunk, options = {}) {
        // Create message from prompt
        const message = { role: 'user', content: prompt };
        
        // Process system prompt if provided
        const messages = [];
        if (options.systemPrompt) {
            messages.push({ role: 'system', content: options.systemPrompt });
        }
        messages.push(message);
        
        // Use the chat stream method with a single user message
        return this.streamChatResponse(messages, onChunk, options);
    }
    
    /**
     * Stream a chat response using the LLM.
     * @param {Array<Object>} messages - Array of message objects with role and content
     * @param {function} onChunk - Callback for each chunk of text
     * @param {Object} [options] - Additional options
     * @param {string} [options.providerId] - Provider ID (overrides default)
     * @param {string} [options.modelId] - Model ID (overrides default)
     * @param {string} [options.contextId] - Context ID (defaults to componentId)
     * @param {number} [options.temperature=0.7] - Temperature parameter
     * @param {number} [options.maxTokens] - Maximum tokens to generate
     * @param {Array<string>} [options.stopSequences] - Sequences to stop generation
     * @param {function} [options.onComplete] - Callback when streaming is complete
     * @param {function} [options.onError] - Callback for streaming errors
     * @returns {string} - Request ID that can be used to cancel the request
     */
    streamChatResponse(messages, onChunk, options = {}) {
        const contextId = options.contextId || this.componentId;
        const providerId = options.providerId || this.providerId;
        const modelId = options.modelId || this.modelId;
        const temperature = options.temperature ?? 0.7;
        const onComplete = options.onComplete || (() => {});
        const onError = options.onError || ((error) => console.error('Streaming error:', error));
        
        // Generate request ID
        const requestId = `${this.componentId}_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;
        
        // Try to use WebSocket if available (preferred for streaming)
        if (this._canUseWebSocket()) {
            this._streamViaWebSocket(requestId, messages, contextId, providerId, modelId, 
                                     temperature, options, onChunk, onComplete, onError);
            return requestId;
        }
        
        // Fall back to HTTP streaming if WebSocket is unavailable
        this._streamViaHttp(requestId, messages, contextId, providerId, modelId, 
                           temperature, options, onChunk, onComplete, onError);
        return requestId;
    }
    
    /**
     * Cancel an ongoing streaming request.
     * @param {string} requestId - The request ID to cancel
     * @returns {boolean} - True if the request was cancelled, false otherwise
     */
    cancelRequest(requestId) {
        // Check if it's a WebSocket request
        if (this.wsCallbacks.has(requestId)) {
            this._cancelWebSocketRequest(requestId);
            return true;
        }
        
        // Check if it's an HTTP request
        if (this.pendingRequests.has(requestId)) {
            const controller = this.pendingRequests.get(requestId);
            controller.abort();
            this.pendingRequests.delete(requestId);
            return true;
        }
        
        return false;
    }
    
    /**
     * Get available LLM providers and models.
     * @returns {Promise<Object>} - Information about available providers and models
     */
    async getProviders() {
        try {
            const response = await fetch(`${this.rhetorUrl}/api/v1/providers`, {
                method: 'GET',
                headers: this._getHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            this._log('Error fetching providers', error);
            
            // Return minimal fallback info
            return {
                providers: {
                    anthropic: {
                        name: "Anthropic Claude",
                        available: false,
                        models: [
                            { id: "claude-3-opus-20240229", name: "Claude 3 Opus" },
                            { id: "claude-3-sonnet-20240229", name: "Claude 3 Sonnet" },
                            { id: "claude-3-haiku-20240307", name: "Claude 3 Haiku" }
                        ]
                    }
                },
                default_provider: "anthropic",
                default_model: "claude-3-haiku-20240307"
            };
        }
    }
    
    /**
     * Stream chat response using HTTP streaming.
     * @private
     */
    _streamViaHttp(requestId, messages, contextId, providerId, modelId, temperature, options, onChunk, onComplete, onError) {
        // Construct request payload
        const payload = {
            messages,
            context_id: contextId,
            provider_id: providerId,
            streaming: true,
            options: {
                temperature
            }
        };
        
        if (modelId) {
            payload.model_id = modelId;
        }
        
        if (options.maxTokens) {
            payload.options.max_tokens = options.maxTokens;
        }
        
        if (options.stopSequences) {
            payload.options.stop = options.stopSequences;
        }
        
        // Create AbortController for timeout and cancellation
        const controller = new AbortController();
        const timeoutMs = (options.timeout || this.timeout) * 1000;
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
        
        // Store the controller for potential cancellation
        this.pendingRequests.set(requestId, controller);
        
        // Send the streaming request
        fetch(`${this.rhetorUrl}/api/v1/chat/stream`, {
            method: 'POST',
            headers: this._getHeaders(),
            body: JSON.stringify(payload),
            signal: controller.signal
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            // Get the reader for streaming
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            
            // Process chunks
            const processChunks = ({ done, value }) => {
                if (done) {
                    clearTimeout(timeoutId);
                    this.pendingRequests.delete(requestId);
                    onComplete();
                    return;
                }
                
                // Decode the chunk and add to buffer
                const chunk = decoder.decode(value, { stream: true });
                buffer += chunk;
                
                // Process any complete lines in the buffer
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // Keep the last incomplete line in the buffer
                
                for (const line of lines) {
                    if (line.trim() === '') continue;
                    
                    if (line.startsWith('data: ')) {
                        const data = line.substring(6); // Remove 'data: ' prefix
                        
                        if (data === '[DONE]') {
                            clearTimeout(timeoutId);
                            this.pendingRequests.delete(requestId);
                            onComplete();
                            return;
                        }
                        
                        try {
                            const parsedData = JSON.parse(data);
                            onChunk({
                                chunk: parsedData.chunk || '',
                                contextId: parsedData.context_id || contextId,
                                model: parsedData.model || modelId,
                                provider: parsedData.provider || providerId,
                                timestamp: parsedData.timestamp || new Date().toISOString(),
                                done: parsedData.done || false,
                                error: parsedData.error
                            });
                            
                            if (parsedData.done) {
                                clearTimeout(timeoutId);
                                this.pendingRequests.delete(requestId);
                                onComplete();
                                return;
                            }
                        } catch (error) {
                            this._log('Error parsing SSE data', error, data);
                        }
                    }
                }
                
                // Continue reading
                return reader.read().then(processChunks);
            };
            
            reader.read().then(processChunks);
        })
        .catch(error => {
            clearTimeout(timeoutId);
            this.pendingRequests.delete(requestId);
            
            if (error.name === 'AbortError') {
                if (timeoutId) {
                    onError(new Error(`Request timed out after ${timeoutMs / 1000} seconds`));
                } else {
                    // Request was cancelled by user
                    return;
                }
            } else {
                onError(error);
            }
        });
    }
    
    /**
     * Check if WebSocket can be used for streaming.
     * @private
     */
    _canUseWebSocket() {
        return typeof WebSocket !== 'undefined';
    }
    
    /**
     * Stream chat response using WebSocket.
     * @private
     */
    _streamViaWebSocket(requestId, messages, contextId, providerId, modelId, temperature, options, onChunk, onComplete, onError) {
        // Connect to WebSocket if needed
        this._connectWebSocket()
            .then(() => {
                // Register callbacks for this request
                this.wsCallbacks.set(requestId, { onChunk, onComplete, onError });
                
                // Construct request payload
                const payload = {
                    type: 'CHAT_STREAM',
                    request_id: requestId,
                    messages,
                    context_id: contextId,
                    provider_id: providerId,
                    options: {
                        temperature
                    }
                };
                
                if (modelId) {
                    payload.model_id = modelId;
                }
                
                if (options.maxTokens) {
                    payload.options.max_tokens = options.maxTokens;
                }
                
                if (options.stopSequences) {
                    payload.options.stop = options.stopSequences;
                }
                
                // Send the request
                this.ws.send(JSON.stringify(payload));
                
                // Set up timeout
                const timeoutMs = (options.timeout || this.timeout) * 1000;
                const timeoutId = setTimeout(() => {
                    const callbacks = this.wsCallbacks.get(requestId);
                    if (callbacks) {
                        this.wsCallbacks.delete(requestId);
                        callbacks.onError(new Error(`Request timed out after ${timeoutMs / 1000} seconds`));
                    }
                }, timeoutMs);
                
                // Store timeout ID for cleanup
                this.wsCallbacks.set(requestId, { ...this.wsCallbacks.get(requestId), timeoutId });
            })
            .catch(error => {
                this._log('WebSocket connection failed, falling back to HTTP', error);
                
                // Fall back to HTTP streaming
                this._streamViaHttp(requestId, messages, contextId, providerId, modelId, 
                                   temperature, options, onChunk, onComplete, onError);
            });
    }
    
    /**
     * Cancel a WebSocket streaming request.
     * @private
     */
    _cancelWebSocketRequest(requestId) {
        if (!this.ws || !this.wsConnected) {
            this.wsCallbacks.delete(requestId);
            return;
        }
        
        // Get callbacks for cleanup
        const callbacks = this.wsCallbacks.get(requestId);
        if (callbacks && callbacks.timeoutId) {
            clearTimeout(callbacks.timeoutId);
        }
        
        // Send cancellation request
        try {
            this.ws.send(JSON.stringify({
                type: 'CANCEL',
                request_id: requestId
            }));
        } catch (error) {
            this._log('Error sending cancellation request', error);
        }
        
        // Remove callbacks
        this.wsCallbacks.delete(requestId);
    }
    
    /**
     * Connect to the WebSocket server.
     * @private
     */
    async _connectWebSocket() {
        if (this.wsConnected) {
            return;
        }
        
        if (this.wsConnecting) {
            // Wait for connection to complete
            return new Promise((resolve, reject) => {
                const checkInterval = setInterval(() => {
                    if (this.wsConnected) {
                        clearInterval(checkInterval);
                        resolve();
                    } else if (!this.wsConnecting) {
                        clearInterval(checkInterval);
                        reject(new Error('WebSocket connection failed'));
                    }
                }, 100);
                
                // Timeout after 5 seconds
                setTimeout(() => {
                    clearInterval(checkInterval);
                    if (!this.wsConnected) {
                        reject(new Error('WebSocket connection timed out'));
                    }
                }, 5000);
            });
        }
        
        this.wsConnecting = true;
        
        return new Promise((resolve, reject) => {
            try {
                // Create WebSocket connection
                this.ws = new WebSocket(this.rhetorWsUrl);
                
                // Add auth token if available
                if (this.authToken) {
                    // Note: WebSocket doesn't support custom headers, but some implementations
                    // allow URL parameters for auth
                    // For more secure auth, use a connection handshake protocol
                }
                
                // Set up event handlers
                this.ws.onopen = () => {
                    this._log('WebSocket connected');
                    
                    // Register with the server
                    this.ws.send(JSON.stringify({
                        type: 'REGISTER',
                        component_id: this.componentId,
                        capabilities: ['chat', 'stream']
                    }));
                    
                    // Wait for registration acknowledgment
                    // This would ideally be more robust, checking for an actual ack message
                    setTimeout(() => {
                        this.wsConnected = true;
                        this.wsConnecting = false;
                        resolve();
                    }, 500);
                };
                
                this.ws.onmessage = (event) => {
                    this._handleWebSocketMessage(event.data);
                };
                
                this.ws.onerror = (error) => {
                    this._log('WebSocket error', error);
                    this.wsConnected = false;
                    this.wsConnecting = false;
                    reject(error);
                    
                    // Notify all pending requests
                    for (const [requestId, callbacks] of this.wsCallbacks.entries()) {
                        if (callbacks.onError) {
                            callbacks.onError(new Error('WebSocket error'));
                        }
                        
                        if (callbacks.timeoutId) {
                            clearTimeout(callbacks.timeoutId);
                        }
                    }
                    
                    this.wsCallbacks.clear();
                };
                
                this.ws.onclose = () => {
                    this._log('WebSocket closed');
                    this.wsConnected = false;
                    this.wsConnecting = false;
                    
                    // Notify all pending requests
                    for (const [requestId, callbacks] of this.wsCallbacks.entries()) {
                        if (callbacks.onError) {
                            callbacks.onError(new Error('WebSocket connection closed'));
                        }
                        
                        if (callbacks.timeoutId) {
                            clearTimeout(callbacks.timeoutId);
                        }
                    }
                    
                    this.wsCallbacks.clear();
                };
            } catch (error) {
                this._log('Error creating WebSocket', error);
                this.wsConnected = false;
                this.wsConnecting = false;
                reject(error);
            }
        });
    }
    
    /**
     * Handle incoming WebSocket messages.
     * @private
     */
    _handleWebSocketMessage(data) {
        try {
            const message = JSON.parse(data);
            const type = message.type || '';
            const requestId = message.request_id || '';
            
            if (type === 'CHUNK' && requestId) {
                // Handle streaming chunk
                const callbacks = this.wsCallbacks.get(requestId);
                if (callbacks && callbacks.onChunk) {
                    callbacks.onChunk({
                        chunk: message.chunk || '',
                        contextId: message.context_id || '',
                        model: message.model || '',
                        provider: message.provider || '',
                        timestamp: message.timestamp || new Date().toISOString(),
                        done: message.done || false,
                        error: message.error
                    });
                    
                    // If this is the last chunk, complete the request
                    if (message.done) {
                        if (callbacks.timeoutId) {
                            clearTimeout(callbacks.timeoutId);
                        }
                        
                        if (callbacks.onComplete) {
                            callbacks.onComplete();
                        }
                        
                        this.wsCallbacks.delete(requestId);
                    }
                }
            } else if (type === 'ERROR' && requestId) {
                // Handle error
                const callbacks = this.wsCallbacks.get(requestId);
                if (callbacks) {
                    if (callbacks.timeoutId) {
                        clearTimeout(callbacks.timeoutId);
                    }
                    
                    if (callbacks.onError) {
                        callbacks.onError(new Error(message.error || 'Unknown error'));
                    }
                    
                    this.wsCallbacks.delete(requestId);
                }
            } else if (type === 'REGISTER_ACK') {
                this._log('Registration acknowledged');
            } else if (type === 'PING') {
                // Respond to ping with pong
                if (this.ws && this.wsConnected) {
                    this.ws.send(JSON.stringify({ type: 'PONG' }));
                }
            }
        } catch (error) {
            this._log('Error parsing WebSocket message', error, data);
        }
    }
    
    /**
     * Get headers for HTTP requests.
     * @private
     */
    _getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
        
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        
        return headers;
    }
    
    /**
     * Log message if debug is enabled.
     * @private
     */
    _log(message, ...args) {
        if (this.debug) {
            console.log(`[TektonLLMClient] ${message}`, ...args);
        }
    }
}

// Export for CommonJS and ES modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TektonLLMClient };
} else if (typeof define === 'function' && define.amd) {
    define([], function() { return { TektonLLMClient }; });
} else if (typeof window !== 'undefined') {
    window.TektonLLMClient = TektonLLMClient;
}