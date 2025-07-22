/**
 * Engram Memory Service
 * Handles communication with the Engram Memory API and provides a clean interface for memory operations
 */

console.log('[FILE_TRACE] Loading: engram-service.js');
class EngramService extends window.tektonUI.componentUtils.BaseService {
    /**
     * Initialize the Engram Service
     */
    constructor() {
        // Use engramUrl function from tekton-urls.js
        const baseUrl = window.engramUrl ? window.engramUrl('') : 'http://localhost:8901';
        
        // Configure Single Port Architecture using BaseService
        super('engramService', baseUrl);
        
        // Configure different endpoint paths on the same port
        this.apiUrl = window.engramUrl ? window.engramUrl('/api/v1') : `${baseUrl}/api/v1`;
        this.wsUrl = window.engramUrl ? window.engramUrl('/stream').replace('http', 'ws') : `${baseUrl.replace('http', 'ws')}/stream`;
        
        // State tracking
        this.connected = false;
        this.wsConnection = null;
        this.wsReconnectAttempts = 0;
        this.wsConnectionState = 'disconnected';
        
        // Memory caching
        this.memoryCache = new Map();
        this.compartmentCache = new Map();
        this.statisticsCache = null;
        this.lastCacheUpdate = null;
        
        // Active queries
        this.activeQueries = new Map();
        this.queryId = 0;
        
        console.log('EngramService initialized with base URL:', baseUrl);
    }
    
    /**
     * Connect to the Engram API
     * @returns {Promise<boolean>} - Connection success
     */
    async connect() {
        if (this.connected) {
            return true;
        }
        
        try {
            // Test connection to the Engram API
            console.log('Connecting to Engram API...');
            const response = await fetch(`${this.apiUrl}/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status !== 'ok') {
                throw new Error(`Engram API returned non-ok status: ${data.status}`);
            }
            
            // Connection successful
            this.connected = true;
            this.dispatchEvent('connected', {
                message: 'Connected to Engram API',
                apiVersion: data.version
            });
            
            // Connect WebSocket for real-time updates
            this.connectWebSocket();
            
            console.log('Successfully connected to Engram API');
            return true;
        } catch (error) {
            this.connected = false;
            console.error('Failed to connect to Engram API:', error);
            
            this.dispatchEvent('connectionFailed', {
                message: 'Failed to connect to Engram API',
                error: error.message
            });
            
            return false;
        }
    }
    
    /**
     * Connect to the Engram WebSocket for real-time updates
     */
    connectWebSocket() {
        if (this.wsConnection) {
            console.log('WebSocket already connected');
            return;
        }
        
        console.log('Connecting to Engram WebSocket...');
        this.wsConnectionState = 'connecting';
        
        try {
            this.wsConnection = new WebSocket(this.wsUrl);
            
            this.wsConnection.onopen = () => {
                console.log('Engram WebSocket connected');
                this.wsConnectionState = 'connected';
                this.wsReconnectAttempts = 0;
                
                this.dispatchEvent('websocketConnected', {
                    message: 'WebSocket connected'
                });
                
                // Subscribe to memory updates
                this.sendWebSocketMessage({
                    type: 'subscribe',
                    channel: 'memory_updates'
                });
            };
            
            this.wsConnection.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleWebSocketMessage(message);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.wsConnection.onerror = (error) => {
                console.error('Engram WebSocket error:', error);
                this.wsConnectionState = 'error';
                
                this.dispatchEvent('websocketError', {
                    message: 'WebSocket connection error',
                    error: error
                });
            };
            
            this.wsConnection.onclose = (event) => {
                console.log('Engram WebSocket closed:', event.code, event.reason);
                this.wsConnection = null;
                this.wsConnectionState = 'disconnected';
                
                this.dispatchEvent('websocketDisconnected', {
                    message: 'WebSocket disconnected',
                    code: event.code,
                    reason: event.reason
                });
                
                // Implement exponential backoff for reconnection
                if (this.wsReconnectAttempts < 5) {
                    const delay = Math.min(1000 * Math.pow(2, this.wsReconnectAttempts), 30000);
                    console.log(`Reconnecting WebSocket in ${delay}ms (attempt ${this.wsReconnectAttempts + 1})`);
                    
                    setTimeout(() => {
                        this.wsReconnectAttempts++;
                        this.connectWebSocket();
                    }, delay);
                }
            };
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.wsConnectionState = 'error';
            
            this.dispatchEvent('websocketError', {
                message: 'Failed to create WebSocket connection',
                error: error.message
            });
        }
    }
    
    /**
     * Send a message via the WebSocket connection
     * @param {Object} message - The message to send
     */
    sendWebSocketMessage(message) {
        if (!this.wsConnection || this.wsConnectionState !== 'connected') {
            console.warn('Cannot send WebSocket message: not connected');
            return false;
        }
        
        try {
            this.wsConnection.send(JSON.stringify(message));
            return true;
        } catch (error) {
            console.error('Error sending WebSocket message:', error);
            return false;
        }
    }
    
    /**
     * Handle incoming WebSocket messages
     * @param {Object} message - The message received
     */
    handleWebSocketMessage(message) {
        console.log('Received WebSocket message:', message);
        
        switch (message.type) {
            case 'memory_created':
            case 'memory_updated':
            case 'memory_deleted':
                this.handleMemoryUpdate(message);
                break;
                
            case 'compartment_created':
            case 'compartment_updated':
            case 'compartment_deleted':
                this.handleCompartmentUpdate(message);
                break;
                
            case 'statistics_updated':
                this.handleStatisticsUpdate(message);
                break;
                
            case 'query_result':
                this.handleQueryResult(message);
                break;
                
            case 'error':
                this.handleErrorMessage(message);
                break;
                
            default:
                console.log('Unknown WebSocket message type:', message.type);
        }
    }
    
    /**
     * Handle memory update messages from WebSocket
     * @param {Object} message - The memory update message
     */
    handleMemoryUpdate(message) {
        // Update cache if needed
        if (message.data && message.data.id) {
            if (message.type === 'memory_deleted') {
                this.memoryCache.delete(message.data.id);
            } else {
                this.memoryCache.set(message.data.id, message.data);
            }
        }
        
        // Dispatch event to notify component
        this.dispatchEvent('memoryUpdated', {
            type: message.type,
            data: message.data
        });
    }
    
    /**
     * Handle compartment update messages from WebSocket
     * @param {Object} message - The compartment update message
     */
    handleCompartmentUpdate(message) {
        // Update cache if needed
        if (message.data && message.data.id) {
            if (message.type === 'compartment_deleted') {
                this.compartmentCache.delete(message.data.id);
            } else {
                this.compartmentCache.set(message.data.id, message.data);
            }
        }
        
        // Dispatch event to notify component
        this.dispatchEvent('compartmentUpdated', {
            type: message.type,
            data: message.data
        });
    }
    
    /**
     * Handle statistics update messages from WebSocket
     * @param {Object} message - The statistics update message
     */
    handleStatisticsUpdate(message) {
        // Update cache
        this.statisticsCache = message.data;
        
        // Dispatch event to notify component
        this.dispatchEvent('statisticsUpdated', {
            data: message.data
        });
    }
    
    /**
     * Handle query result messages from WebSocket
     * @param {Object} message - The query result message
     */
    handleQueryResult(message) {
        const queryId = message.query_id;
        
        if (this.activeQueries.has(queryId)) {
            const { resolve, reject } = this.activeQueries.get(queryId);
            
            if (message.error) {
                reject(new Error(message.error));
            } else {
                resolve(message.results);
            }
            
            // Remove from active queries
            this.activeQueries.delete(queryId);
        }
    }
    
    /**
     * Handle error messages from WebSocket
     * @param {Object} message - The error message
     */
    handleErrorMessage(message) {
        console.error('Engram WebSocket error:', message.error);
        
        // Dispatch event to notify component
        this.dispatchEvent('error', {
            message: message.error,
            type: 'websocket'
        });
    }
    
    /**
     * Get all memory entries
     * @param {Object} options - Query options
     * @param {number} options.limit - Maximum number of entries to return
     * @param {number} options.offset - Offset for pagination
     * @param {string} options.sort - Sort field and direction (e.g., 'timestamp:desc')
     * @param {string} options.compartment - Filter by compartment ID
     * @returns {Promise<Array>} - Array of memory entries
     */
    async getEntries(options = {}) {
        await this.ensureConnected();
        
        const limit = options.limit || 50;
        const offset = options.offset || 0;
        const sort = options.sort || 'timestamp:desc';
        
        // Build query parameters
        const params = new URLSearchParams({
            limit,
            offset,
            sort
        });
        
        if (options.compartment && options.compartment !== 'all') {
            params.append('compartment', options.compartment);
        }
        
        if (options.tags && options.tags.length > 0) {
            params.append('tags', options.tags.join(','));
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/memories?${params.toString()}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Cache the results
            data.items.forEach(entry => {
                this.memoryCache.set(entry.id, entry);
            });
            
            return data.items;
        } catch (error) {
            console.error('Error fetching memory entries:', error);
            this.dispatchEvent('error', {
                message: 'Failed to fetch memory entries',
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Get a specific memory entry by ID
     * @param {string} id - The memory entry ID
     * @returns {Promise<Object>} - The memory entry
     */
    async getMemoryEntry(id) {
        await this.ensureConnected();
        
        // Check cache first
        if (this.memoryCache.has(id)) {
            return this.memoryCache.get(id);
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/memories/${id}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const entry = await response.json();
            
            // Cache the result
            this.memoryCache.set(id, entry);
            
            return entry;
        } catch (error) {
            console.error(`Error fetching memory entry ${id}:`, error);
            this.dispatchEvent('error', {
                message: `Failed to fetch memory entry: ${id}`,
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Create a new memory entry
     * @param {Object} entry - The memory entry to create
     * @returns {Promise<Object>} - The created memory entry
     */
    async createMemoryEntry(entry) {
        await this.ensureConnected();
        
        try {
            const response = await fetch(`${this.apiUrl}/memories`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(entry)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const createdEntry = await response.json();
            
            // Cache the result
            this.memoryCache.set(createdEntry.id, createdEntry);
            
            // Dispatch event
            this.dispatchEvent('memoryUpdated', {
                type: 'memory_created',
                data: createdEntry
            });
            
            return createdEntry;
        } catch (error) {
            console.error('Error creating memory entry:', error);
            this.dispatchEvent('error', {
                message: 'Failed to create memory entry',
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Update a memory entry
     * @param {string} id - The memory entry ID
     * @param {Object} updates - The updates to apply
     * @returns {Promise<Object>} - The updated memory entry
     */
    async updateMemoryEntry(id, updates) {
        await this.ensureConnected();
        
        try {
            const response = await fetch(`${this.apiUrl}/memories/${id}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updates)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const updatedEntry = await response.json();
            
            // Update cache
            this.memoryCache.set(id, updatedEntry);
            
            // Dispatch event
            this.dispatchEvent('memoryUpdated', {
                type: 'memory_updated',
                data: updatedEntry
            });
            
            return updatedEntry;
        } catch (error) {
            console.error(`Error updating memory entry ${id}:`, error);
            this.dispatchEvent('error', {
                message: `Failed to update memory entry: ${id}`,
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Delete a memory entry
     * @param {string} id - The memory entry ID
     * @returns {Promise<boolean>} - Success status
     */
    async deleteMemoryEntry(id) {
        await this.ensureConnected();
        
        try {
            const response = await fetch(`${this.apiUrl}/memories/${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            // Remove from cache
            this.memoryCache.delete(id);
            
            // Dispatch event
            this.dispatchEvent('memoryUpdated', {
                type: 'memory_deleted',
                data: { id }
            });
            
            return true;
        } catch (error) {
            console.error(`Error deleting memory entry ${id}:`, error);
            this.dispatchEvent('error', {
                message: `Failed to delete memory entry: ${id}`,
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Get all compartments
     * @returns {Promise<Array>} - Array of compartments
     */
    async getCompartments() {
        await this.ensureConnected();
        
        try {
            const response = await fetch(`${this.apiUrl}/compartments`);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Cache the results
            data.items.forEach(compartment => {
                this.compartmentCache.set(compartment.id, compartment);
            });
            
            return data.items;
        } catch (error) {
            console.error('Error fetching compartments:', error);
            this.dispatchEvent('error', {
                message: 'Failed to fetch compartments',
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Get a specific compartment by ID
     * @param {string} id - The compartment ID
     * @returns {Promise<Object>} - The compartment
     */
    async getCompartment(id) {
        await this.ensureConnected();
        
        // Check cache first
        if (this.compartmentCache.has(id)) {
            return this.compartmentCache.get(id);
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/compartments/${id}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const compartment = await response.json();
            
            // Cache the result
            this.compartmentCache.set(id, compartment);
            
            return compartment;
        } catch (error) {
            console.error(`Error fetching compartment ${id}:`, error);
            this.dispatchEvent('error', {
                message: `Failed to fetch compartment: ${id}`,
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Create a new compartment
     * @param {Object} compartment - The compartment to create
     * @returns {Promise<Object>} - The created compartment
     */
    async createCompartment(compartment) {
        await this.ensureConnected();
        
        try {
            const response = await fetch(`${this.apiUrl}/compartments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(compartment)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const createdCompartment = await response.json();
            
            // Cache the result
            this.compartmentCache.set(createdCompartment.id, createdCompartment);
            
            // Dispatch event
            this.dispatchEvent('compartmentUpdated', {
                type: 'compartment_created',
                data: createdCompartment
            });
            
            return createdCompartment;
        } catch (error) {
            console.error('Error creating compartment:', error);
            this.dispatchEvent('error', {
                message: 'Failed to create compartment',
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Update a compartment
     * @param {string} id - The compartment ID
     * @param {Object} updates - The updates to apply
     * @returns {Promise<Object>} - The updated compartment
     */
    async updateCompartment(id, updates) {
        await this.ensureConnected();
        
        try {
            const response = await fetch(`${this.apiUrl}/compartments/${id}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updates)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const updatedCompartment = await response.json();
            
            // Update cache
            this.compartmentCache.set(id, updatedCompartment);
            
            // Dispatch event
            this.dispatchEvent('compartmentUpdated', {
                type: 'compartment_updated',
                data: updatedCompartment
            });
            
            return updatedCompartment;
        } catch (error) {
            console.error(`Error updating compartment ${id}:`, error);
            this.dispatchEvent('error', {
                message: `Failed to update compartment: ${id}`,
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Delete a compartment
     * @param {string} id - The compartment ID
     * @returns {Promise<boolean>} - Success status
     */
    async deleteCompartment(id) {
        await this.ensureConnected();
        
        try {
            const response = await fetch(`${this.apiUrl}/compartments/${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            // Remove from cache
            this.compartmentCache.delete(id);
            
            // Dispatch event
            this.dispatchEvent('compartmentUpdated', {
                type: 'compartment_deleted',
                data: { id }
            });
            
            return true;
        } catch (error) {
            console.error(`Error deleting compartment ${id}:`, error);
            this.dispatchEvent('error', {
                message: `Failed to delete compartment: ${id}`,
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Search memory entries
     * @param {string} query - The search query
     * @param {Object} options - Search options
     * @param {string} options.type - Search type: 'semantic', 'keyword', 'tag', or 'combined'
     * @param {Array} options.compartments - Compartment IDs to search within
     * @param {number} options.limit - Maximum number of results
     * @param {string} options.startDate - Start date filter
     * @param {string} options.endDate - End date filter
     * @returns {Promise<Array>} - Array of search results
     */
    async searchMemory(query, options = {}) {
        await this.ensureConnected();
        
        const searchType = options.type || 'semantic';
        const limit = options.limit || 50;
        
        // Build query parameters
        const params = new URLSearchParams({
            query,
            type: searchType,
            limit
        });
        
        if (options.compartments && options.compartments.length > 0) {
            params.append('compartments', options.compartments.join(','));
        }
        
        if (options.startDate) {
            params.append('start_date', options.startDate);
        }
        
        if (options.endDate) {
            params.append('end_date', options.endDate);
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/search?${params.toString()}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const results = await response.json();
            
            // Cache memory entries from results
            results.items.forEach(result => {
                if (result.entry) {
                    this.memoryCache.set(result.entry.id, result.entry);
                }
            });
            
            return results.items;
        } catch (error) {
            console.error('Error searching memory:', error);
            this.dispatchEvent('error', {
                message: 'Failed to search memory',
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Get memory statistics
     * @returns {Promise<Object>} - Memory statistics
     */
    async getStatistics() {
        await this.ensureConnected();
        
        try {
            const response = await fetch(`${this.apiUrl}/statistics`);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const statistics = await response.json();
            
            // Cache the result
            this.statisticsCache = statistics;
            
            return statistics;
        } catch (error) {
            console.error('Error fetching memory statistics:', error);
            this.dispatchEvent('error', {
                message: 'Failed to fetch memory statistics',
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Get available memory tags
     * @returns {Promise<Array>} - Array of tags
     */
    async getTags() {
        await this.ensureConnected();
        
        try {
            const response = await fetch(`${this.apiUrl}/tags`);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            return data.items;
        } catch (error) {
            console.error('Error fetching memory tags:', error);
            this.dispatchEvent('error', {
                message: 'Failed to fetch memory tags',
                error: error.message
            });
            
            throw error;
        }
    }
    
    /**
     * Ensure connection to Engram API
     * @private
     */
    async ensureConnected() {
        if (!this.connected) {
            const connected = await this.connect();
            if (!connected) {
                throw new Error('Not connected to Engram API');
            }
        }
    }
    
    /**
     * Disconnect from Engram API and WebSocket
     */
    disconnect() {
        // Close WebSocket connection if open
        if (this.wsConnection) {
            this.wsConnection.close();
            this.wsConnection = null;
            this.wsConnectionState = 'disconnected';
        }
        
        // Clear state
        this.connected = false;
        
        // Dispatch event
        this.dispatchEvent('disconnected', {
            message: 'Disconnected from Engram API'
        });
        
        console.log('Disconnected from Engram API');
    }
    
    /**
     * Clear cached data
     */
    clearCache() {
        this.memoryCache.clear();
        this.compartmentCache.clear();
        this.statisticsCache = null;
        this.lastCacheUpdate = null;
        
        console.log('Engram cache cleared');
    }
}

// Register the service if window.tektonUI is available
if (window.tektonUI && !window.tektonUI.services.engramService) {
    window.tektonUI.services.engramService = new EngramService();
    console.log('EngramService registered globally');
}