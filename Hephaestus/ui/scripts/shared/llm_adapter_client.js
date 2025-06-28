/**
 * LLM Adapter Client - A standardized client for interacting with the Rhetor LLM adapter.
 * 
 * This client provides a consistent interface for communicating with the Rhetor LLM
 * adapter API from Tekton components. It supports both synchronous requests and
 * streaming responses.
 */

console.log('[FILE_TRACE] Loading: llm_adapter_client.js');
class LLMAdapterClient {
    /**
     * Initialize the LLM adapter client.
     * 
     * @param {Object} options - Configuration options
     * @param {string} options.apiUrl - Base URL for the Rhetor API (default: from environment or /api/llm)
     * @param {string} options.defaultModel - Default model to use (default: from environment or claude-3-sonnet)
     * @param {number} options.timeout - Request timeout in seconds (default: 60)
     * @param {Object} options.defaultHeaders - Default headers to include in requests
     */
    constructor(options = {}) {
        // Get API URL from options, environment, or default
        const rhetorPort = window.RHETOR_PORT || 8003;
        this.apiUrl = options.apiUrl || 
                    (window.RHETOR_API_URL || `http://localhost:${rhetorPort}`);
        
        // Add path if not already included
        if (!this.apiUrl.endsWith('/api/v1')) {
            this.apiUrl = `${this.apiUrl}/api/v1`;
        }
        
        // Default model and parameters
        this.defaultModel = options.defaultModel || 
                          (window.DEFAULT_LLM_MODEL || 'claude-3-sonnet-20240229');
        this.timeout = options.timeout || 60;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            ...options.defaultHeaders
        };
        
        // Track pending requests for cancellation
        this.pendingRequests = new Map();
    }

    /**
     * Generate a completion using the LLM adapter.
     * 
     * @param {Object} params - Request parameters
     * @param {string} params.prompt - The user prompt
     * @param {string} [params.systemPrompt] - Optional system instructions
     * @param {string} [params.model] - Model to use (defaults to this.defaultModel)
     * @param {number} [params.temperature=0.7] - Sampling temperature (0.0 to 1.0)
     * @param {number} [params.maxTokens] - Maximum tokens to generate
     * @param {Array} [params.stopSequences] - Optional stop sequences
     * @param {Array} [params.chatHistory] - Optional chat history for context
     * @returns {Promise<Object>} Promise resolving to the response
     */
    async generateText(params) {
        const { 
            prompt, 
            systemPrompt, 
            model = this.defaultModel, 
            temperature = 0.7,
            maxTokens,
            stopSequences,
            chatHistory = []
        } = params;
        
        const url = `${this.apiUrl}/generate`;
        
        const messages = this._formatMessages(prompt, systemPrompt, chatHistory);
        
        const payload = {
            model: model,
            messages: messages,
            temperature: temperature
        };
        
        if (maxTokens) {
            payload.max_tokens = maxTokens;
        }
        
        if (stopSequences && stopSequences.length > 0) {
            payload.stop = stopSequences;
        }
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout * 1000);
            
            const requestId = Math.random().toString(36).substring(2, 15);
            this.pendingRequests.set(requestId, controller);
            
            const response = await fetch(url, {
                method: 'POST',
                headers: this.defaultHeaders,
                body: JSON.stringify(payload),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            this.pendingRequests.delete(requestId);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error ${response.status}: ${errorText}`);
            }
            
            const result = await response.json();
            return {
                content: result.content || '',
                model: result.model || model,
                usage: result.usage || {},
                success: true
            };
        } catch (error) {
            console.error('Error calling LLM adapter:', error);
            return {
                error: error.message,
                success: false,
                content: 'Sorry, I encountered an error while processing your request.'
            };
        }
    }
    
    /**
     * Generate a streaming response from the LLM adapter.
     * 
     * @param {Object} params - Request parameters
     * @param {string} params.prompt - The user prompt
     * @param {Function} params.onChunk - Callback for each chunk received
     * @param {Function} [params.onComplete] - Callback when generation is complete
     * @param {Function} [params.onError] - Callback for errors
     * @param {string} [params.systemPrompt] - Optional system instructions
     * @param {string} [params.model] - Model to use (defaults to this.defaultModel)
     * @param {number} [params.temperature=0.7] - Sampling temperature (0.0 to 1.0)
     * @param {number} [params.maxTokens] - Maximum tokens to generate
     * @param {Array} [params.stopSequences] - Optional stop sequences
     * @param {Array} [params.chatHistory] - Optional chat history for context
     * @returns {string} Request ID that can be used to cancel the request
     */
    generateStream(params) {
        const { 
            prompt,
            onChunk,
            onComplete,
            onError,
            systemPrompt, 
            model = this.defaultModel, 
            temperature = 0.7,
            maxTokens,
            stopSequences,
            chatHistory = []
        } = params;
        
        if (!onChunk) {
            throw new Error('onChunk callback is required for streaming');
        }
        
        const url = `${this.apiUrl}/generate_stream`;
        
        const messages = this._formatMessages(prompt, systemPrompt, chatHistory);
        
        const payload = {
            model: model,
            messages: messages,
            temperature: temperature
        };
        
        if (maxTokens) {
            payload.max_tokens = maxTokens;
        }
        
        if (stopSequences && stopSequences.length > 0) {
            payload.stop = stopSequences;
        }
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout * 1000);
        
        const requestId = Math.random().toString(36).substring(2, 15);
        this.pendingRequests.set(requestId, controller);
        
        fetch(url, {
            method: 'POST',
            headers: this.defaultHeaders,
            body: JSON.stringify(payload),
            signal: controller.signal
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            
            const processChunks = ({done, value}) => {
                if (done) {
                    clearTimeout(timeoutId);
                    this.pendingRequests.delete(requestId);
                    if (onComplete) onComplete();
                    return;
                }
                
                // Decode the chunk and append to buffer
                const chunk = decoder.decode(value, {stream: true});
                buffer += chunk;
                
                // Process any complete lines in the buffer
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // Keep the last (potentially incomplete) line in the buffer
                
                for (const line of lines) {
                    if (line.trim() === '') continue;
                    
                    if (line.startsWith('data: ')) {
                        const data = line.substring(6); // Remove 'data: ' prefix
                        
                        if (data === '[DONE]') {
                            clearTimeout(timeoutId);
                            this.pendingRequests.delete(requestId);
                            if (onComplete) onComplete();
                            return;
                        }
                        
                        try {
                            const parsedData = JSON.parse(data);
                            onChunk(parsedData);
                        } catch (error) {
                            console.error('Error parsing SSE data:', error, data);
                        }
                    }
                }
                
                // Continue reading
                return reader.read().then(processChunks);
            };
            
            return reader.read().then(processChunks);
        })
        .catch(error => {
            clearTimeout(timeoutId);
            this.pendingRequests.delete(requestId);
            console.error('Error streaming from LLM adapter:', error);
            if (onError) {
                onError(error);
            }
        });
        
        return requestId;
    }
    
    /**
     * Connect to the LLM adapter via WebSocket for real-time streaming.
     * 
     * @param {Object} options - Connection options
     * @param {string} [options.wsUrl] - WebSocket URL (default: derived from apiUrl)
     * @param {Function} [options.onOpen] - Callback when connection opens
     * @param {Function} [options.onClose] - Callback when connection closes
     * @param {Function} [options.onError] - Callback when connection errors
     * @returns {WebSocket} WebSocket connection
     */
    connectWebSocket(options = {}) {
        const wsUrl = options.wsUrl || this.apiUrl.replace('http', 'ws').replace('https', 'wss').replace('/api/v1', '/ws/generate');
        
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log('WebSocket connection established');
            if (options.onOpen) options.onOpen();
        };
        
        ws.onclose = (event) => {
            console.log(`WebSocket closed: ${event.code} - ${event.reason}`);
            if (options.onClose) options.onClose(event);
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (options.onError) options.onError(error);
        };
        
        return ws;
    }
    
    /**
     * Generate a streaming response using WebSocket.
     * 
     * @param {WebSocket} ws - WebSocket connection
     * @param {Object} params - Request parameters
     * @param {string} params.prompt - The user prompt
     * @param {Function} params.onChunk - Callback for each chunk received
     * @param {Function} [params.onComplete] - Callback when generation is complete
     * @param {Function} [params.onError] - Callback for errors
     * @param {string} [params.systemPrompt] - Optional system instructions
     * @param {string} [params.model] - Model to use (defaults to this.defaultModel)
     * @param {number} [params.temperature=0.7] - Sampling temperature (0.0 to 1.0)
     * @param {number} [params.maxTokens] - Maximum tokens to generate
     * @param {Array} [params.stopSequences] - Optional stop sequences
     * @param {Array} [params.chatHistory] - Optional chat history for context
     * @returns {string} Request ID that can be used to cancel the request
     */
    generateWebSocketStream(ws, params) {
        const { 
            prompt,
            onChunk,
            onComplete,
            onError,
            systemPrompt, 
            model = this.defaultModel, 
            temperature = 0.7,
            maxTokens,
            stopSequences,
            chatHistory = []
        } = params;
        
        if (!onChunk) {
            throw new Error('onChunk callback is required for WebSocket streaming');
        }
        
        const messages = this._formatMessages(prompt, systemPrompt, chatHistory);
        const requestId = Math.random().toString(36).substring(2, 15);
        
        const payload = {
            request_id: requestId,
            model: model,
            messages: messages,
            temperature: temperature
        };
        
        if (maxTokens) {
            payload.max_tokens = maxTokens;
        }
        
        if (stopSequences && stopSequences.length > 0) {
            payload.stop = stopSequences;
        }
        
        // Set up message handler for this request
        const messageHandler = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                // Check if this response is for our request
                if (data.request_id === requestId) {
                    // Process the chunk
                    onChunk(data);
                    
                    // If this is the final chunk, clean up
                    if (data.done) {
                        ws.removeEventListener('message', messageHandler);
                        if (onComplete) onComplete(data);
                    }
                }
            } catch (error) {
                console.error('Error handling WebSocket message:', error);
                if (onError) onError(error);
            }
        };
        
        // Add the message handler
        ws.addEventListener('message', messageHandler);
        
        // Send the request
        try {
            ws.send(JSON.stringify(payload));
        } catch (error) {
            console.error('Error sending WebSocket message:', error);
            ws.removeEventListener('message', messageHandler);
            if (onError) onError(error);
        }
        
        return requestId;
    }
    
    /**
     * Cancel an ongoing generation request.
     * 
     * @param {string} requestId - The request ID to cancel
     * @returns {boolean} Whether the request was successfully cancelled
     */
    cancelRequest(requestId) {
        const controller = this.pendingRequests.get(requestId);
        if (controller) {
            controller.abort();
            this.pendingRequests.delete(requestId);
            return true;
        }
        return false;
    }
    
    /**
     * Cancel a WebSocket generation request.
     * 
     * @param {WebSocket} ws - WebSocket connection
     * @param {string} requestId - The request ID to cancel
     * @returns {boolean} Whether the cancel request was sent successfully
     */
    cancelWebSocketRequest(ws, requestId) {
        try {
            ws.send(JSON.stringify({
                request_id: requestId,
                action: 'cancel'
            }));
            return true;
        } catch (error) {
            console.error('Error canceling WebSocket request:', error);
            return false;
        }
    }
    
    /**
     * Get available models from the LLM adapter.
     * 
     * @returns {Promise<Array>} Promise resolving to the list of available models
     */
    async getAvailableModels() {
        try {
            const response = await fetch(`${this.apiUrl}/models`, {
                headers: this.defaultHeaders
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching available models:', error);
            return [];
        }
    }
    
    /**
     * Format messages for the API request.
     * 
     * @private
     * @param {string} prompt - User prompt
     * @param {string} systemPrompt - System prompt
     * @param {Array} chatHistory - Previous chat messages
     * @returns {Array} Formatted messages array
     */
    _formatMessages(prompt, systemPrompt, chatHistory) {
        const messages = [...chatHistory]; // Clone the chat history
        
        // Add system prompt if provided
        if (systemPrompt) {
            // Check if there's already a system message
            const hasSystemMessage = messages.some(msg => msg.role === 'system');
            
            if (!hasSystemMessage) {
                messages.unshift({ role: 'system', content: systemPrompt });
            }
        }
        
        // Add user prompt if not already in the chat history
        if (!messages.length || messages[messages.length - 1].role !== 'user') {
            messages.push({ role: 'user', content: prompt });
        }
        
        return messages;
    }
}

// Export the client for module usage
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = { LLMAdapterClient };
}