/**
 * Budget API Client
 * 
 * Handles communication with the Budget backend service
 * Part of the Budget UI Update Sprint implementation
 */
class BudgetApiClient {
    /**
     * Create a new Budget API client instance
     */
    constructor() {
        this.baseUrl = this._getBaseUrl();
        this.cache = new Map();
        this.cacheTimeout = 60000; // 1 minute cache
        this.pendingRequests = new Map();
        
        // Event emitter for API events
        this.events = {
            listeners: {},
            
            /**
             * Add event listener
             * @param {string} event - Event name
             * @param {Function} callback - Event callback
             */
            on(event, callback) {
                if (!this.listeners[event]) {
                    this.listeners[event] = [];
                }
                this.listeners[event].push(callback);
            },
            
            /**
             * Remove event listener
             * @param {string} event - Event name
             * @param {Function} callback - Event callback
             */
            off(event, callback) {
                if (!this.listeners[event]) return;
                this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
            },
            
            /**
             * Emit event
             * @param {string} event - Event name
             * @param {any} data - Event data
             */
            emit(event, data) {
                if (!this.listeners[event]) return;
                this.listeners[event].forEach(callback => callback(data));
            }
        };
    }
    
    /**
     * Get base URL for API calls using tektonUrl
     * @returns {string} Base URL for Budget API
     */
    _getBaseUrl() {
        return budgetUrl();
    }
    
    /**
     * Generate cache key for request
     * @param {string} endpoint - API endpoint
     * @param {Object} params - Request parameters
     * @returns {string} Cache key
     */
    _getCacheKey(endpoint, params = {}) {
        return `${endpoint}:${JSON.stringify(params)}`;
    }
    
    /**
     * Check if a cached response is still valid
     * @param {string} key - Cache key
     * @returns {boolean} True if cache is valid
     */
    _isCacheValid(key) {
        if (!this.cache.has(key)) return false;
        
        const { timestamp } = this.cache.get(key);
        const now = Date.now();
        
        return now - timestamp < this.cacheTimeout;
    }
    
    /**
     * Store response in cache
     * @param {string} key - Cache key
     * @param {Object} data - Response data
     */
    _cacheResponse(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }
    
    /**
     * Get cached response
     * @param {string} key - Cache key
     * @returns {Object|null} Cached response or null
     */
    _getCachedResponse(key) {
        if (!this._isCacheValid(key)) return null;
        
        return this.cache.get(key).data;
    }
    
    /**
     * Clear cache for specific key or all cache if no key provided
     * @param {string} [key] - Optional cache key
     */
    clearCache(key) {
        if (key) {
            this.cache.delete(key);
        } else {
            this.cache.clear();
        }
    }
    
    /**
     * Make an API request with proper error handling
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Fetch options
     * @param {boolean} [useCache=true] - Whether to use cache
     * @returns {Promise} API response promise
     */
    async request(endpoint, options = {}, useCache = true) {
        const method = options.method || 'GET';
        const cacheKey = this._getCacheKey(endpoint, options.body);
        
        // Check for pending request to the same endpoint
        const pendingKey = `${method}:${cacheKey}`;
        if (this.pendingRequests.has(pendingKey)) {
            return this.pendingRequests.get(pendingKey);
        }
        
        // Check cache for GET requests
        if (useCache && method === 'GET' && this._isCacheValid(cacheKey)) {
            return Promise.resolve(this._getCachedResponse(cacheKey));
        }
        
        // Set up request options
        const requestOptions = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        // Convert body to JSON string if it's an object
        if (requestOptions.body && typeof requestOptions.body === 'object') {
            requestOptions.body = JSON.stringify(requestOptions.body);
        }
        
        // Create the request promise
        const requestPromise = fetch(`${this.baseUrl}${endpoint}`, requestOptions)
            .then(async response => {
                // Handle response
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`API error (${response.status}): ${errorText}`);
                }
                
                // Parse response as JSON
                try {
                    const data = await response.json();
                    
                    // Cache successful GET responses
                    if (useCache && method === 'GET') {
                        this._cacheResponse(cacheKey, data);
                    }
                    
                    // Emit event for response
                    this.events.emit('response', {
                        endpoint,
                        method,
                        data
                    });
                    
                    return data;
                } catch (error) {
                    throw new Error(`Error parsing response: ${error.message}`);
                }
            })
            .catch(error => {
                // Emit event for error
                this.events.emit('error', {
                    endpoint,
                    method,
                    error
                });
                
                throw error;
            })
            .finally(() => {
                // Remove from pending requests
                this.pendingRequests.delete(pendingKey);
            });
        
        // Store pending request
        this.pendingRequests.set(pendingKey, requestPromise);
        
        return requestPromise;
    }
    
    /**
     * Get dashboard summary data
     * @param {string} period - Time period (daily, weekly, monthly)
     * @returns {Promise} Dashboard summary
     */
    async getDashboardSummary(period = 'monthly') {
        return this.request(`/api/budgets/summary?period=${period}`);
    }
    
    /**
     * Get usage records with optional filtering
     * @param {Object} filters - Filter parameters
     * @param {number} page - Page number
     * @param {number} limit - Results per page
     * @returns {Promise} Usage records
     */
    async getUsageRecords(filters = {}, page = 1, limit = 20) {
        // Build query string from filters
        const queryParams = new URLSearchParams({
            page,
            limit
        });
        
        // Add filters to query string
        for (const [key, value] of Object.entries(filters)) {
            if (value !== undefined && value !== null && value !== '') {
                queryParams.append(key, value);
            }
        }
        
        return this.request(`/api/usage/records?${queryParams.toString()}`);
    }
    
    /**
     * Get usage summary data
     * @param {string} period - Time period (daily, weekly, monthly)
     * @param {Object} filters - Filter parameters
     * @returns {Promise} Usage summary
     */
    async getUsageSummary(period = 'monthly', filters = {}) {
        const requestBody = {
            period,
            ...filters
        };
        
        return this.request('/api/usage/summary', {
            method: 'POST',
            body: requestBody
        });
    }
    
    /**
     * Get budget settings
     * @returns {Promise} Budget settings
     */
    async getBudgetSettings() {
        return this.request('/api/budgets');
    }
    
    /**
     * Save budget settings
     * @param {Object} settings - Budget settings
     * @returns {Promise} Updated settings
     */
    async saveBudgetSettings(settings) {
        // Clear settings cache
        this.clearCache(this._getCacheKey('/api/budgets'));
        
        return this.request(`/api/budgets/${settings.budget_id}`, {
            method: 'PUT',
            body: settings
        }, false);
    }
    
    /**
     * Get budget policies
     * @param {string} budgetId - Budget ID
     * @returns {Promise} Budget policies
     */
    async getBudgetPolicies(budgetId) {
        return this.request(`/api/budgets/${budgetId}/policies`);
    }
    
    /**
     * Update a budget policy
     * @param {string} policyId - Policy ID
     * @param {Object} policy - Policy data
     * @returns {Promise} Updated policy
     */
    async updatePolicy(policyId, policy) {
        return this.request(`/api/policies/${policyId}`, {
            method: 'PUT',
            body: policy
        }, false);
    }
    
    /**
     * Get alerts with optional filtering
     * @param {Object} filters - Filter parameters
     * @param {number} page - Page number
     * @param {number} limit - Results per page
     * @returns {Promise} Alerts
     */
    async getAlerts(filters = {}, page = 1, limit = 20) {
        // Build query string from filters
        const queryParams = new URLSearchParams({
            page,
            limit
        });
        
        // Add filters to query string
        for (const [key, value] of Object.entries(filters)) {
            if (value !== undefined && value !== null && value !== '') {
                queryParams.append(key, value);
            }
        }
        
        return this.request(`/api/alerts?${queryParams.toString()}`);
    }
    
    /**
     * Acknowledge an alert
     * @param {string} alertId - Alert ID
     * @returns {Promise} Updated alert
     */
    async acknowledgeAlert(alertId) {
        return this.request(`/api/alerts/${alertId}/acknowledge`, {
            method: 'POST'
        }, false);
    }
    
    /**
     * Get model recommendations
     * @param {Object} params - Recommendation parameters
     * @returns {Promise} Model recommendations
     */
    async getModelRecommendations(params) {
        return this.request('/api/assistant/recommend-model', {
            method: 'POST',
            body: params
        });
    }
    
    /**
     * Get budget analysis
     * @param {Object} params - Analysis parameters
     * @returns {Promise} Budget analysis
     */
    async getBudgetAnalysis(params) {
        return this.request('/api/assistant/analyze', {
            method: 'POST',
            body: params
        });
    }
    
    /**
     * Get optimization recommendations
     * @param {Object} params - Optimization parameters
     * @returns {Promise} Optimization recommendations
     */
    async getOptimizationRecommendations(params) {
        return this.request('/api/assistant/optimize', {
            method: 'POST',
            body: params
        });
    }
    
    /**
     * Get price data
     * @param {string} provider - Provider name (optional)
     * @param {string} model - Model name (optional)
     * @returns {Promise} Price data
     */
    async getPrices(provider, model) {
        let endpoint = '/api/prices';
        
        // Add query parameters if provided
        const queryParams = new URLSearchParams();
        if (provider) queryParams.append('provider', provider);
        if (model) queryParams.append('model', model);
        
        if (queryParams.toString()) {
            endpoint += `?${queryParams.toString()}`;
        }
        
        return this.request(endpoint);
    }
    
    /**
     * Execute a CLI command
     * @param {string} command - Command text
     * @returns {Promise} Command result
     */
    async executeCommand(command) {
        return this.request('/api/command', {
            method: 'POST',
            body: {
                command
            }
        }, false);
    }
    
    /**
     * Get help for a CLI command
     * @param {string} command - Command name (optional)
     * @returns {Promise} Command help
     */
    async getCommandHelp(command = null) {
        let endpoint = '/api/command/help';
        
        if (command) {
            endpoint += `?command=${encodeURIComponent(command)}`;
        }
        
        return this.request(endpoint);
    }
    
    /**
     * Connect to a WebSocket for real-time updates
     * @param {string} endpoint - WebSocket endpoint
     * @returns {WebSocket} WebSocket connection
     */
    connectWebSocket(endpoint) {
        const wsUrl = budgetUrl(endpoint).replace(/^http/, 'ws');
        
        return new WebSocket(wsUrl);
    }
}

// Export as global class
window.BudgetApiClient = BudgetApiClient;