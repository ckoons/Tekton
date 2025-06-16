/**
 * Apollo Service
 * 
 * Provides API communications for the Apollo Executive Coordinator Component.
 * Handles interactions with the Apollo backend services.
 */

class ApolloService {
  /**
   * Initialize the Apollo Service
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.baseUrl = options.baseUrl || this._getBaseUrl();
    this.apiPath = options.apiPath || '/api';
    this.debug = options.debug || false;
    
    // Set up mock data for development
    this.useMockData = options.useMockData || true; // Set to false when Apollo backend is ready
    
    console.log(`[APOLLO] Service initialized with base URL: ${this.baseUrl}`);
    if (this.useMockData) {
      console.log('[APOLLO] Using mock data for development');
    }
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
    
    // Use Single Port Architecture with dynamic port assignment
    const port = window.APOLLO_PORT || 8012; // Dynamic port for Apollo in the Single Port Architecture
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
      console.log(`[ApolloService] ${message}`, data || '');
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
    // If using mock data, return mock response
    if (this.useMockData) {
      return this._getMockResponse(endpoint, options);
    }
    
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
   * Generate mock response for development
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Mock response
   * @private
   */
  async _getMockResponse(endpoint, options = {}) {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Status endpoint
    if (endpoint === '/status') {
      return {
        status: 'healthy',
        version: '1.0.0',
        session_count: 4,
        total_tokens: 102536,
        active_models: ['claude-3-opus', 'claude-3-sonnet', 'gpt-4', 'llama-3-70b']
      };
    }
    
    // Sessions endpoint
    if (endpoint === '/sessions') {
      return [
        {
          id: 'session-001',
          name: 'Codex',
          model: 'claude-3-opus',
          status: 'healthy',
          tokens_used: 12420,
          token_budget: 30000,
          last_active: '2025-05-18T12:42:18Z',
          health_score: 0.98
        },
        {
          id: 'session-002',
          name: 'Athena',
          model: 'claude-3-sonnet',
          status: 'healthy',
          tokens_used: 8765,
          token_budget: 25000,
          last_active: '2025-05-18T12:45:32Z',
          health_score: 0.95
        },
        {
          id: 'session-003',
          name: 'Rhetor',
          model: 'claude-3-opus',
          status: 'warning',
          tokens_used: 21584,
          token_budget: 25000,
          last_active: '2025-05-18T12:51:07Z',
          health_score: 0.72
        },
        {
          id: 'session-004',
          name: 'Engram',
          model: 'gpt-4',
          status: 'healthy',
          tokens_used: 5651,
          token_budget: 20000,
          last_active: '2025-05-18T12:48:55Z',
          health_score: 0.94
        }
      ];
    }
    
    // Token budgets endpoint
    if (endpoint === '/tokens') {
      return {
        total_allocation: 100000,
        total_used: 38420,
        per_session: {
          'session-001': { budget: 30000, used: 12420 },
          'session-002': { budget: 25000, used: 8765 },
          'session-003': { budget: 25000, used: 21584 },
          'session-004': { budget: 20000, used: 5651 }
        },
        compression_threshold: 85,
        current_compression_level: 0
      };
    }

    // Protocols endpoint
    if (endpoint === '/protocols') {
      return [
        {
          id: 'protocol-001',
          name: 'Memory Management',
          status: 'active',
          description: 'Controls memory fetch and compression operations',
          config: {
            prefetch_threshold: 0.75,
            compression_levels: [0.85, 0.92, 0.98],
            memory_priority: ['recent', 'relevant', 'foundational']
          }
        },
        {
          id: 'protocol-002',
          name: 'LLM Reset',
          status: 'active',
          description: 'Manages when to reset LLM context',
          config: {
            token_threshold: 0.95,
            hallucination_threshold: 0.8,
            memory_refresh: true
          }
        },
        {
          id: 'protocol-003',
          name: 'Context Compression',
          status: 'active',
          description: 'Handles dynamic context compression',
          config: {
            light_compression: 0.85,
            medium_compression: 0.92,
            heavy_compression: 0.98,
            preserve_latest_exchange: true
          }
        }
      ];
    }
    
    // Forecasts endpoint
    if (endpoint === '/forecasts') {
      return {
        'session-001': {
          id: 'session-001',
          name: 'Codex',
          token_exhaustion_prediction: {
            time_remaining: '6h 42m',
            tokens_remaining: 17580,
            usage_rate: 2600
          },
          health_forecast: 'stable',
          recommendations: []
        },
        'session-002': {
          id: 'session-002',
          name: 'Athena',
          token_exhaustion_prediction: {
            time_remaining: '8h 15m',
            tokens_remaining: 16235,
            usage_rate: 1900
          },
          health_forecast: 'stable',
          recommendations: []
        },
        'session-003': {
          id: 'session-003',
          name: 'Rhetor',
          token_exhaustion_prediction: {
            time_remaining: '45m',
            tokens_remaining: 3416,
            usage_rate: 4500
          },
          health_forecast: 'degrading',
          recommendations: [
            {
              type: 'compression',
              level: 'medium',
              reason: 'High token usage rate'
            },
            {
              type: 'reset',
              reason: 'Context nearing exhaustion'
            }
          ]
        },
        'session-004': {
          id: 'session-004',
          name: 'Engram',
          token_exhaustion_prediction: {
            time_remaining: '12h 22m',
            tokens_remaining: 14349,
            usage_rate: 1100
          },
          health_forecast: 'stable',
          recommendations: []
        }
      };
    }
    
    // Default empty response
    return {};
  }

  /**
   * Get the status of the Apollo service
   * @returns {Promise<Object>} Status information
   */
  async getStatus() {
    return this._request('/status');
  }

  /**
   * Get a list of active LLM sessions
   * @returns {Promise<Array>} List of active sessions
   */
  async getSessions() {
    return this._request('/sessions');
  }

  /**
   * Get details for a specific LLM session
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Session details
   */
  async getSession(sessionId) {
    return this._request(`/sessions/${sessionId}`);
  }

  /**
   * Get token budget information
   * @returns {Promise<Object>} Token budget information
   */
  async getTokenBudgets() {
    return this._request('/tokens');
  }

  /**
   * Update token budget for a session
   * @param {string} sessionId - Session ID
   * @param {number} budget - New token budget
   * @returns {Promise<Object>} Updated budget information
   */
  async updateTokenBudget(sessionId, budget) {
    return this._request(`/tokens/${sessionId}`, {
      method: 'PUT',
      body: JSON.stringify({ budget })
    });
  }

  /**
   * Get protocol settings
   * @returns {Promise<Array>} List of protocols
   */
  async getProtocols() {
    return this._request('/protocols');
  }

  /**
   * Update a protocol setting
   * @param {string} protocolId - Protocol ID
   * @param {Object} settings - Protocol settings
   * @returns {Promise<Object>} Updated protocol
   */
  async updateProtocol(protocolId, settings) {
    return this._request(`/protocols/${protocolId}`, {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }

  /**
   * Get forecasting data for all sessions
   * @returns {Promise<Object>} Forecasting data
   */
  async getForecasts() {
    return this._request('/forecasts');
  }

  /**
   * Get forecasting data for a session
   * @param {string} sessionId - Session ID
   * @returns {Promise<Object>} Forecasting data
   */
  async getForecast(sessionId) {
    return this._request(`/forecasts/${sessionId}`);
  }

  /**
   * Execute an action on a session
   * @param {string} sessionId - Session ID
   * @param {string} action - Action to execute (reset, compress, rebuild)
   * @param {Object} parameters - Action parameters
   * @returns {Promise<Object>} Action result
   */
  async executeAction(sessionId, action, parameters = {}) {
    return this._request(`/actions/${sessionId}/${action}`, {
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
export { ApolloService };