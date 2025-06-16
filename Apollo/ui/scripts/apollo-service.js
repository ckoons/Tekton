/**
 * Apollo API Client
 * 
 * Provides a JavaScript interface for interacting with the Apollo Executive Coordinator API.
 */

class ApolloClient {
  /**
   * Initialize the Apollo API client
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.baseUrl = options.baseUrl || this._getBaseUrl();
    this.apiPath = options.apiPath || '';
    this.debug = options.debug || false;
  }

  /**
   * Get the base URL for the Apollo API from environment variables or default
   * @returns {string} The base URL
   * @private
   */
  _getBaseUrl() {
    // Check for environment variables
    if (window.ENV && window.ENV.APOLLO_API_URL) {
      return window.ENV.APOLLO_API_URL;
    }
    
    // Use Single Port Architecture with standard port assignment
    const port = '8001'; // Standard port for Apollo in the Single Port Architecture
    return `http://${window.location.hostname}:${port}`;
  }

  /**
   * Log messages when in debug mode
   * @param {string} message - Debug message
   * @param {*} data - Additional data to log
   * @private
   */
  _debug(message, data = null) {
    if (this.debug) {
      console.log(`[ApolloClient] ${message}`, data || '');
    }
  }

  /**
   * Make a request to the Apollo API
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Fetch options
   * @returns {Promise<Object>} API response
   * @private
   */
  async _request(endpoint, options = {}) {
    const url = `${this.baseUrl}${this.apiPath}${endpoint}`;
    
    // Ensure headers exist
    options.headers = options.headers || {};
    
    // Add JSON content type if method is not GET
    if (options.method && options.method !== 'GET' && !options.headers['Content-Type']) {
      options.headers['Content-Type'] = 'application/json';
    }
    
    this._debug(`Request: ${options.method || 'GET'} ${url}`, options.body);
    
    try {
      const response = await fetch(url, options);
      
      // Handle non-2xx responses
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      // Return JSON response if available, otherwise return text
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        this._debug('Response:', data);
        return data;
      } else {
        const text = await response.text();
        this._debug('Response (text):', text);
        return text;
      }
    } catch (error) {
      this._debug('Request error:', error);
      throw error;
    }
  }

  /**
   * Get the status of the Apollo service
   * @returns {Promise<Object>} Status information
   */
  async getStatus() {
    return this._request('/api/status');
  }

  /**
   * Get a list of active LLM sessions
   * @returns {Promise<Array>} List of active sessions
   */
  async getSessions() {
    return this._request('/api/sessions');
  }

  /**
   * Get details for a specific LLM session
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Session details
   */
  async getSession(sessionId) {
    return this._request(`/api/sessions/${sessionId}`);
  }

  /**
   * Get token budget information
   * @returns {Promise<Object>} Token budget information
   */
  async getTokenBudgets() {
    return this._request('/api/tokens');
  }

  /**
   * Update token budget for a session
   * @param {string} sessionId - Session ID
   * @param {number} budget - New token budget
   * @returns {Promise<Object>} Updated budget information
   */
  async updateTokenBudget(sessionId, budget) {
    return this._request(`/api/tokens/${sessionId}`, {
      method: 'PUT',
      body: JSON.stringify({ budget })
    });
  }

  /**
   * Get protocol settings
   * @returns {Promise<Array>} List of protocols
   */
  async getProtocols() {
    return this._request('/api/protocols');
  }

  /**
   * Update a protocol setting
   * @param {string} protocolId - Protocol ID
   * @param {Object} settings - Protocol settings
   * @returns {Promise<Object>} Updated protocol
   */
  async updateProtocol(protocolId, settings) {
    return this._request(`/api/protocols/${protocolId}`, {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }

  /**
   * Get forecasting data for a session
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Forecasting data
   */
  async getForecast(sessionId) {
    return this._request(`/api/forecasts/${sessionId}`);
  }

  /**
   * Execute an action on a session
   * @param {string} sessionId - Session ID
   * @param {string} action - Action to execute (reset, compress, rebuild)
   * @param {Object} parameters - Action parameters
   * @returns {Promise<Object>} Action result
   */
  async executeAction(sessionId, action, parameters = {}) {
    return this._request(`/api/actions/${sessionId}/${action}`, {
      method: 'POST',
      body: JSON.stringify(parameters)
    });
  }

  /**
   * Reset an LLM session
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Reset result
   */
  async resetSession(sessionId) {
    return this.executeAction(sessionId, 'reset');
  }

  /**
   * Compress the context for an LLM session
   * @param {string} sessionId - Session ID
   * @param {number} level - Compression level (1-3)
   * @returns {Promise<Object>} Compression result
   */
  async compressSession(sessionId, level = 1) {
    return this.executeAction(sessionId, 'compress', { level });
  }

  /**
   * Rebuild the prompt for an LLM session
   * @param {string} sessionId - Session ID
   * @param {Object} options - Rebuild options
   * @returns {Promise<Object>} Rebuild result
   */
  async rebuildPrompt(sessionId, options = {}) {
    return this.executeAction(sessionId, 'rebuild', options);
  }
}

// Export the client class
export { ApolloClient };