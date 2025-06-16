/**
 * Tekton LLM Client
 * 
 * A JavaScript client for interacting with the Tekton LLM service
 * using the standardized LLM integration approach.
 */

class TektonLLMClient {
  /**
   * Initialize the Tekton LLM client
   * @param {string} componentId - The component ID for usage tracking
   * @param {Object} options - Configuration options
   */
  constructor(componentId, options = {}) {
    this.componentId = componentId || 'unknown-component';
    this.baseUrl = options.baseUrl || this._getBaseUrl();
    this.wsBaseUrl = options.wsBaseUrl || this._getWSBaseUrl();
    this.provider = options.provider || 'claude';
    this.model = options.model || 'claude-3-sonnet-20240229';
    this.temperature = options.temperature !== undefined ? options.temperature : 0.7;
    this.debug = options.debug || false;
  }

  /**
   * Get the base URL for the LLM API from environment variables or default
   * @returns {string} The base URL
   * @private
   */
  _getBaseUrl() {
    // Check for environment variables
    if (window.ENV && window.ENV.LLM_API_URL) {
      return window.ENV.LLM_API_URL;
    }
    
    // Use Single Port Architecture with standard port assignment
    const port = '8002'; // Standard port for LLM Adapter in the Single Port Architecture
    return `http://${window.location.hostname}:${port}`;
  }

  /**
   * Get the WebSocket base URL
   * @returns {string} The WebSocket base URL
   * @private
   */
  _getWSBaseUrl() {
    // Check for environment variables
    if (window.ENV && window.ENV.LLM_WS_URL) {
      return window.ENV.LLM_WS_URL;
    }
    
    // Use Single Port Architecture with standard port assignment
    const port = '8002'; // Standard port for LLM Adapter in the Single Port Architecture
    return `ws://${window.location.hostname}:${port}`;
  }

  /**
   * Set the provider to use for LLM requests
   * @param {string} provider - The provider name ('claude', 'gpt4', 'local', etc.)
   */
  setProvider(provider) {
    this.provider = provider;
  }

  /**
   * Set the model to use for LLM requests
   * @param {string} model - The model name ('claude-3-sonnet-20240229', etc.)
   */
  setModel(model) {
    this.model = model;
  }

  /**
   * Set the temperature for LLM requests
   * @param {number} temperature - The temperature value (0.0 to 1.0)
   */
  setTemperature(temperature) {
    this.temperature = temperature;
  }

  /**
   * Log messages when in debug mode
   * @param {string} message - Debug message
   * @param {*} data - Additional data to log
   * @private
   */
  _debug(message, data = null) {
    if (this.debug) {
      console.log(`[TektonLLMClient] ${message}`, data || '');
    }
  }

  /**
   * Check if the LLM service is available
   * @returns {Promise<boolean>} True if available
   */
  async checkAvailability() {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      if (response.ok) {
        const data = await response.json();
        return data.status === 'available' || data.status === 'healthy';
      }
      return false;
    } catch (error) {
      this._debug('LLM service availability check failed:', error);
      return false;
    }
  }

  /**
   * Generate text using the LLM
   * @param {string} prompt - The prompt to send to the LLM
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} The LLM response
   */
  async generateText(prompt, options = {}) {
    const url = `${this.baseUrl}/api/generate`;
    
    const requestBody = {
      prompt,
      provider: options.provider || this.provider,
      model: options.model || this.model,
      temperature: options.temperature !== undefined ? options.temperature : this.temperature,
      max_tokens: options.maxTokens || 1000,
      system_prompt: options.systemPrompt || '',
      component_id: this.componentId
    };
    
    if (options.responseFormat) {
      requestBody.response_format = options.responseFormat;
    }
    
    this._debug('Generating text:', requestBody);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });
    
    if (!response.ok) {
      throw new Error(`LLM request failed: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    this._debug('LLM response:', data);
    
    return data;
  }

  /**
   * Generate a chat response using the LLM
   * @param {Array} messages - The chat messages
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} The LLM response
   */
  async generateChatResponse(messages, options = {}) {
    const url = `${this.baseUrl}/api/chat`;
    
    const requestBody = {
      messages,
      provider: options.provider || this.provider,
      model: options.model || this.model,
      temperature: options.temperature !== undefined ? options.temperature : this.temperature,
      max_tokens: options.maxTokens || 1000,
      system_prompt: options.systemPrompt || '',
      component_id: this.componentId
    };
    
    this._debug('Generating chat response:', requestBody);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });
    
    if (!response.ok) {
      throw new Error(`LLM chat request failed: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    this._debug('LLM chat response:', data);
    
    return data;
  }

  /**
   * Stream text generation from the LLM
   * @param {string} prompt - The prompt to send to the LLM
   * @param {Function} onChunk - Callback for each chunk received
   * @param {Object} options - Additional options
   * @returns {Promise<void>}
   */
  async streamText(prompt, onChunk, options = {}) {
    const systemPrompt = options.systemPrompt || '';
    const provider = options.provider || this.provider;
    const model = options.model || this.model;
    const temperature = options.temperature !== undefined ? options.temperature : this.temperature;
    
    // Use WebSocket for streaming
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(`${this.wsBaseUrl}/ws`);
      
      ws.onopen = () => {
        this._debug('WebSocket connection opened');
        
        // Send request
        ws.send(JSON.stringify({
          type: 'generate',
          data: {
            prompt,
            provider,
            model,
            temperature,
            system_prompt: systemPrompt,
            stream: true,
            component_id: this.componentId
          }
        }));
      };
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'error') {
            reject(new Error(message.error));
            ws.close();
            return;
          }
          
          if (message.type === 'content') {
            const chunk = {
              content: message.content,
              done: false
            };
            onChunk(chunk);
          }
          
          if (message.type === 'done') {
            onChunk({ content: '', done: true });
            ws.close();
            resolve();
          }
        } catch (error) {
          this._debug('Error parsing WebSocket message:', error);
          reject(error);
          ws.close();
        }
      };
      
      ws.onerror = (error) => {
        this._debug('WebSocket error:', error);
        reject(error);
      };
      
      ws.onclose = () => {
        this._debug('WebSocket connection closed');
      };
    });
  }

  /**
   * Stream chat generation from the LLM
   * @param {Array} messages - The chat messages
   * @param {Function} onChunk - Callback for each chunk received
   * @param {Object} options - Additional options
   * @returns {Promise<void>}
   */
  async streamChatResponse(messages, onChunk, options = {}) {
    const systemPrompt = options.systemPrompt || '';
    const provider = options.provider || this.provider;
    const model = options.model || this.model;
    const temperature = options.temperature !== undefined ? options.temperature : this.temperature;
    
    // Use WebSocket for streaming
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(`${this.wsBaseUrl}/ws`);
      
      ws.onopen = () => {
        this._debug('WebSocket connection opened');
        
        // Send request
        ws.send(JSON.stringify({
          type: 'chat',
          data: {
            messages,
            provider,
            model,
            temperature,
            system_prompt: systemPrompt,
            stream: true,
            component_id: this.componentId
          }
        }));
      };
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'error') {
            reject(new Error(message.error));
            ws.close();
            return;
          }
          
          if (message.type === 'content') {
            const chunk = {
              content: message.content,
              done: false
            };
            onChunk(chunk);
          }
          
          if (message.type === 'done') {
            onChunk({ content: '', done: true });
            ws.close();
            resolve();
          }
        } catch (error) {
          this._debug('Error parsing WebSocket message:', error);
          reject(error);
          ws.close();
        }
      };
      
      ws.onerror = (error) => {
        this._debug('WebSocket error:', error);
        reject(error);
      };
      
      ws.onclose = () => {
        this._debug('WebSocket connection closed');
      };
    });
  }
}

export { TektonLLMClient };