/**
 * Hermes Service
 * Provides communication with the Hermes message bus and service registry
 */

console.log('[FILE_TRACE] Loading: hermes-service.js');
class HermesService extends window.tektonUI.componentUtils.BaseService {
    constructor() {
        // Call base service with service name and dynamic port from environment
        const hermesPort = window.HERMES_PORT || 8001;
        super('hermesService', `http://localhost:${hermesPort}/api`);
        
        // Track real-time message monitoring
        this.monitoringMessages = false;
        this.messageSocket = null;
        this.isPaused = false;
        
        // Message history for persistence
        this.messageHistory = [];
        this.maxHistorySize = 1000;
        
        // Track service registry
        this.registeredServices = [];
        this.connections = [];
        
        // Refresh interval handler
        this.refreshIntervalId = null;
        this.autoRefreshInterval = 10000; // Default: 10 seconds
        
        // Initialize with persisted state if available
        this._loadPersistedState();
    }

    /**
     * Connect to the Hermes API
     * @returns {Promise<boolean>} - Promise resolving to connection status
     */
    async connect() {
        try {
            // Check if Hermes API is available
            const response = await fetch(`${this.apiUrl}/health`);
            
            if (!response.ok) {
                this.connected = false;
                this.dispatchEvent('connectionFailed', { 
                    error: `Failed to connect to Hermes API: ${response.status} ${response.statusText}` 
                });
                return false;
            }
            
            const data = await response.json();
            this.connected = true;
            this.apiVersion = data.version || 'unknown';
            
            // Dispatch connected event
            this.dispatchEvent('connected', { 
                version: this.apiVersion 
            });
            
            // Set up auto-refresh if enabled
            if (this.autoRefreshInterval > 0) {
                this.startAutoRefresh(this.autoRefreshInterval);
            }
            
            return true;
        } catch (error) {
            this.connected = false;
            this.dispatchEvent('connectionFailed', { 
                error: `Failed to connect to Hermes API: ${error.message}` 
            });
            return false;
        }
    }
    
    /**
     * Set the auto-refresh interval
     * @param {number} interval - Refresh interval in milliseconds (0 to disable)
     */
    setAutoRefreshInterval(interval) {
        this.autoRefreshInterval = interval;
        
        // Clear existing interval if any
        if (this.refreshIntervalId) {
            clearInterval(this.refreshIntervalId);
            this.refreshIntervalId = null;
        }
        
        // Start new interval if enabled
        if (interval > 0) {
            this.startAutoRefresh(interval);
        }
        
        // Persist the setting
        this._persistState();
    }
    
    /**
     * Start auto-refresh of service registry
     * @param {number} interval - Refresh interval in milliseconds
     */
    startAutoRefresh(interval) {
        // Clear existing interval if any
        if (this.refreshIntervalId) {
            clearInterval(this.refreshIntervalId);
        }
        
        // Set up interval for refresh
        this.refreshIntervalId = setInterval(() => {
            this.refreshRegistry();
        }, interval);
    }
    
    /**
     * Stop auto-refresh of service registry
     */
    stopAutoRefresh() {
        if (this.refreshIntervalId) {
            clearInterval(this.refreshIntervalId);
            this.refreshIntervalId = null;
        }
    }

    /**
     * Get list of registered services
     * @returns {Promise<Array>} - Promise resolving to array of services
     */
    async getRegisteredServices() {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/services`);
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to fetch services: ${response.status} ${response.statusText}` 
                });
                return this.registeredServices;
            }
            
            const data = await response.json();
            this.registeredServices = data.services || [];
            
            // Dispatch event with services
            this.dispatchEvent('servicesUpdated', { 
                services: this.registeredServices 
            });
            
            return this.registeredServices;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to fetch services: ${error.message}` 
            });
            return this.registeredServices;
        }
    }
    
    /**
     * Refresh the service registry
     * @returns {Promise<Array>} - Promise resolving to array of services
     */
    async refreshRegistry() {
        return this.getRegisteredServices();
    }
    
    /**
     * Get details for a specific service
     * @param {string} componentId - Component ID
     * @returns {Promise<Object>} - Promise resolving to service details
     */
    async getServiceDetails(componentId) {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/services/${componentId}`);
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to fetch service details: ${response.status} ${response.statusText}` 
                });
                return null;
            }
            
            const data = await response.json();
            return data.service || null;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to fetch service details: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Get service connections
     * @returns {Promise<Array>} - Promise resolving to array of connections
     */
    async getConnections() {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/connections`);
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to fetch connections: ${response.status} ${response.statusText}` 
                });
                return this.connections;
            }
            
            const data = await response.json();
            this.connections = data.connections || [];
            
            // Dispatch event with connections
            this.dispatchEvent('connectionsUpdated', { 
                connections: this.connections 
            });
            
            return this.connections;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to fetch connections: ${error.message}` 
            });
            return this.connections;
        }
    }
    
    /**
     * Start monitoring messages in real-time
     * @returns {boolean} - Whether monitoring started successfully
     */
    startMessageMonitoring() {
        if (this.monitoringMessages) {
            return true; // Already monitoring
        }
        
        try {
            // Create WebSocket connection to Hermes message stream
            // Convert HTTP URL to WebSocket URL
            const wsUrl = this.apiUrl.replace(/^http/, 'ws') + '/messages/stream';
            
            this.messageSocket = new WebSocket(wsUrl);
            
            // Set up WebSocket handlers
            this.messageSocket.onopen = () => {
                this.monitoringMessages = true;
                this.dispatchEvent('monitoringStarted', {});
            };
            
            this.messageSocket.onmessage = (event) => {
                if (this.isPaused) return; // Don't process messages while paused
                
                try {
                    const message = JSON.parse(event.data);
                    
                    // Add timestamp if not present
                    if (!message.timestamp) {
                        message.timestamp = new Date().toISOString();
                    }
                    
                    // Add to history
                    this._addToMessageHistory(message);
                    
                    // Dispatch message event
                    this.dispatchEvent('messageReceived', { message });
                } catch (error) {
                    console.error('Error processing message:', error);
                }
            };
            
            this.messageSocket.onerror = (error) => {
                this.dispatchEvent('error', { 
                    error: `WebSocket error: ${error.message || 'Unknown error'}` 
                });
            };
            
            this.messageSocket.onclose = () => {
                this.monitoringMessages = false;
                this.dispatchEvent('monitoringStopped', {});
            };
            
            return true;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to start message monitoring: ${error.message}` 
            });
            return false;
        }
    }
    
    /**
     * Stop monitoring messages
     */
    stopMessageMonitoring() {
        if (this.messageSocket) {
            this.messageSocket.close();
            this.messageSocket = null;
        }
        
        this.monitoringMessages = false;
        this.isPaused = false;
    }
    
    /**
     * Pause/unpause message processing
     * @param {boolean} paused - Whether to pause message processing
     */
    setPaused(paused) {
        this.isPaused = paused;
        this.dispatchEvent('pauseStateChanged', { isPaused: paused });
    }
    
    /**
     * Get message history
     * @param {Object} filters - Optional filters for message history
     * @returns {Array} - Filtered message history
     */
    getMessageHistory(filters = {}) {
        let filteredHistory = [...this.messageHistory];
        
        // Apply filters if specified
        if (filters.types && filters.types.length > 0) {
            filteredHistory = filteredHistory.filter(msg => 
                filters.types.includes(msg.type)
            );
        }
        
        if (filters.components && filters.components.length > 0) {
            filteredHistory = filteredHistory.filter(msg => 
                filters.components.includes(msg.source) || 
                (msg.target && filters.components.includes(msg.target))
            );
        }
        
        if (filters.startDate) {
            const startTimestamp = new Date(filters.startDate).getTime();
            filteredHistory = filteredHistory.filter(msg => 
                new Date(msg.timestamp).getTime() >= startTimestamp
            );
        }
        
        if (filters.endDate) {
            const endTimestamp = new Date(filters.endDate).getTime();
            filteredHistory = filteredHistory.filter(msg => 
                new Date(msg.timestamp).getTime() <= endTimestamp
            );
        }
        
        if (filters.search) {
            const searchTerm = filters.search.toLowerCase();
            filteredHistory = filteredHistory.filter(msg => 
                JSON.stringify(msg).toLowerCase().includes(searchTerm)
            );
        }
        
        return filteredHistory;
    }
    
    /**
     * Clear message history
     */
    clearMessageHistory() {
        this.messageHistory = [];
        this._persistState();
        this.dispatchEvent('historyCleared', {});
    }
    
    /**
     * Export message history as JSON
     * @returns {string} - JSON string of message history
     */
    exportMessageHistory() {
        return JSON.stringify(this.messageHistory, null, 2);
    }
    
    /**
     * Add connection between components
     * @param {string} sourceId - Source component ID
     * @param {string} targetId - Target component ID
     * @param {Object} options - Connection options
     * @returns {Promise<Object>} - Promise resolving to created connection
     */
    async addConnection(sourceId, targetId, options = {}) {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/connections`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    source: sourceId,
                    target: targetId,
                    type: options.type || 'default',
                    metadata: options.metadata || {}
                })
            });
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to create connection: ${response.status} ${response.statusText}` 
                });
                return null;
            }
            
            const data = await response.json();
            
            // Refresh connections
            await this.getConnections();
            
            return data.connection || null;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to create connection: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Remove connection between components
     * @param {string} connectionId - Connection ID
     * @returns {Promise<boolean>} - Promise resolving to success status
     */
    async removeConnection(connectionId) {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/connections/${connectionId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to remove connection: ${response.status} ${response.statusText}` 
                });
                return false;
            }
            
            // Refresh connections
            await this.getConnections();
            
            return true;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to remove connection: ${error.message}` 
            });
            return false;
        }
    }
    
    /**
     * Add a message to history
     * @param {Object} message - Message object
     */
    _addToMessageHistory(message) {
        // Add to beginning for more recent-first ordering
        this.messageHistory.unshift(message);
        
        // Trim history if it exceeds maximum size
        if (this.messageHistory.length > this.maxHistorySize) {
            this.messageHistory = this.messageHistory.slice(0, this.maxHistorySize);
        }
        
        // Periodically persist state
        this._debouncedPersistState();
    }
    
    /**
     * Set maximum history size
     * @param {number} size - Maximum history size
     */
    setMaxHistorySize(size) {
        this.maxHistorySize = size;
        
        // Trim history if needed
        if (this.messageHistory.length > size) {
            this.messageHistory = this.messageHistory.slice(0, size);
        }
        
        this._persistState();
    }
    
    /**
     * Load persisted state from storage
     */
    _loadPersistedState() {
        try {
            // Use local storage for persistence
            const persistedState = localStorage.getItem('hermes_service_state');
            
            if (persistedState) {
                const state = JSON.parse(persistedState);
                
                // Restore settings
                this.autoRefreshInterval = state.autoRefreshInterval || 10000;
                this.maxHistorySize = state.maxHistorySize || 1000;
                
                // Restore message history
                if (state.messageHistory && Array.isArray(state.messageHistory)) {
                    this.messageHistory = state.messageHistory;
                }
            }
        } catch (error) {
            console.error('Error loading persisted state:', error);
        }
    }
    
    /**
     * Persist state to storage
     */
    _persistState() {
        try {
            // Create state object
            const state = {
                autoRefreshInterval: this.autoRefreshInterval,
                maxHistorySize: this.maxHistorySize,
                messageHistory: this.messageHistory
            };
            
            // Save to local storage
            localStorage.setItem('hermes_service_state', JSON.stringify(state));
        } catch (error) {
            console.error('Error persisting state:', error);
        }
    }
    
    /**
     * Debounced version of persistState to avoid excessive writes
     */
    _debouncedPersistState() {
        if (this._persistTimeout) {
            clearTimeout(this._persistTimeout);
        }
        
        this._persistTimeout = setTimeout(() => {
            this._persistState();
        }, 5000); // Debounce for 5 seconds
    }
    
    /**
     * Clean up resources when service is destroyed
     */
    cleanup() {
        // Stop message monitoring
        this.stopMessageMonitoring();
        
        // Stop auto-refresh
        this.stopAutoRefresh();
        
        // Cancel any pending persistence
        if (this._persistTimeout) {
            clearTimeout(this._persistTimeout);
        }
        
        // Final state persistence
        this._persistState();
    }
}

// Initialize the service when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Create and register the service if not already present
    if (!window.tektonUI?.services?.hermesService) {
        // Register it with the tektonUI global namespace
        window.tektonUI = window.tektonUI || {};
        window.tektonUI.services = window.tektonUI.services || {};
        
        // Create the service instance
        const hermesService = new HermesService();
        
        // Register the service
        window.tektonUI.services.hermesService = hermesService;
        
        console.log('Hermes Service initialized');
    }
});