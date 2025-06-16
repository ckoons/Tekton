/**
 * Tekton Service
 * Provides communication with the Tekton system for monitoring and managing components
 */

class TektonService extends window.tektonUI.componentUtils.BaseService {
    constructor() {
        // Call base service with service name and default API endpoint
        const tektonCorePort = window.TEKTON_CORE_PORT || 8010;
        super('tektonService', `http://localhost:${tektonCorePort}/api`);
        
        // System status and metrics
        this.systemStatus = {};
        this.systemMetrics = {
            cpu: [],
            memory: [],
            disk: [],
            network: []
        };
        
        // Component registry
        this.components = [];
        
        // System logs
        this.systemLogs = [];
        this.maxLogEntries = 500;
        
        // Projects registry
        this.projects = [];
        
        // Refresh interval handler
        this.refreshIntervalId = null;
        this.autoRefreshInterval = 10000; // Default: 10 seconds
        this.metricHistoryLength = 50; // Number of historical data points to keep
        
        // WebSocket for real-time updates
        this.statusSocket = null;
        this.logSocket = null;
        
        // Initialize with persisted state if available
        this._loadPersistedState();
    }

    /**
     * Connect to the Tekton API
     * @returns {Promise<boolean>} - Promise resolving to connection status
     */
    async connect() {
        try {
            // Check if Tekton API is available
            const response = await fetch(`${this.apiUrl}/status`);
            
            if (!response.ok) {
                this.connected = false;
                this.dispatchEvent('connectionFailed', { 
                    error: `Failed to connect to Tekton API: ${response.status} ${response.statusText}` 
                });
                return false;
            }
            
            const data = await response.json();
            this.connected = true;
            this.apiVersion = data.version || 'unknown';
            this.systemStatus = data.status || {};
            
            // Dispatch connected event
            this.dispatchEvent('connected', { 
                version: this.apiVersion,
                status: this.systemStatus
            });
            
            // Set up auto-refresh if enabled
            if (this.autoRefreshInterval > 0) {
                this.startAutoRefresh(this.autoRefreshInterval);
            }
            
            // Start real-time status monitoring
            this.startStatusMonitoring();
            
            return true;
        } catch (error) {
            this.connected = false;
            this.dispatchEvent('connectionFailed', { 
                error: `Failed to connect to Tekton API: ${error.message}` 
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
     * Start auto-refresh of system status
     * @param {number} interval - Refresh interval in milliseconds
     */
    startAutoRefresh(interval) {
        // Clear existing interval if any
        if (this.refreshIntervalId) {
            clearInterval(this.refreshIntervalId);
        }
        
        // Set up interval for refresh
        this.refreshIntervalId = setInterval(() => {
            this.getSystemStatus();
            this.getComponents();
        }, interval);
    }
    
    /**
     * Stop auto-refresh of system status
     */
    stopAutoRefresh() {
        if (this.refreshIntervalId) {
            clearInterval(this.refreshIntervalId);
            this.refreshIntervalId = null;
        }
    }
    
    /**
     * Get system status
     * @returns {Promise<Object>} - Promise resolving to system status
     */
    async getSystemStatus() {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/status`);
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to fetch system status: ${response.status} ${response.statusText}` 
                });
                return this.systemStatus;
            }
            
            const data = await response.json();
            this.systemStatus = data.status || {};
            
            // Update metrics history
            if (data.metrics) {
                this._updateMetricsHistory(data.metrics);
            }
            
            // Dispatch event with status
            this.dispatchEvent('statusUpdated', { 
                status: this.systemStatus,
                metrics: data.metrics
            });
            
            return this.systemStatus;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to fetch system status: ${error.message}` 
            });
            return this.systemStatus;
        }
    }
    
    /**
     * Get list of components
     * @returns {Promise<Array>} - Promise resolving to array of components
     */
    async getComponents() {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/components`);
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to fetch components: ${response.status} ${response.statusText}` 
                });
                return this.components;
            }
            
            const data = await response.json();
            this.components = data.components || [];
            
            // Dispatch event with components
            this.dispatchEvent('componentsUpdated', { 
                components: this.components 
            });
            
            return this.components;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to fetch components: ${error.message}` 
            });
            return this.components;
        }
    }
    
    /**
     * Get details for a specific component
     * @param {string} componentId - Component ID
     * @returns {Promise<Object>} - Promise resolving to component details
     */
    async getComponentDetails(componentId) {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/components/${componentId}`);
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to fetch component details: ${response.status} ${response.statusText}` 
                });
                return null;
            }
            
            const data = await response.json();
            return data.component || null;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to fetch component details: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Start or restart a component
     * @param {string} componentId - Component ID
     * @returns {Promise<boolean>} - Promise resolving to success status
     */
    async startComponent(componentId) {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/components/${componentId}/start`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to start component: ${response.status} ${response.statusText}` 
                });
                return false;
            }
            
            // Update components list
            await this.getComponents();
            
            this.dispatchEvent('componentStarted', { componentId });
            
            return true;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to start component: ${error.message}` 
            });
            return false;
        }
    }
    
    /**
     * Stop a component
     * @param {string} componentId - Component ID
     * @returns {Promise<boolean>} - Promise resolving to success status
     */
    async stopComponent(componentId) {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/components/${componentId}/stop`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to stop component: ${response.status} ${response.statusText}` 
                });
                return false;
            }
            
            // Update components list
            await this.getComponents();
            
            this.dispatchEvent('componentStopped', { componentId });
            
            return true;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to stop component: ${error.message}` 
            });
            return false;
        }
    }
    
    /**
     * Get system logs
     * @param {Object} filters - Optional filters for logs
     * @returns {Promise<Array>} - Promise resolving to array of log entries
     */
    async getSystemLogs(filters = {}) {
        if (!this.connected) {
            await this.connect();
        }
        
        // Build query parameters
        const queryParams = new URLSearchParams();
        if (filters.component) queryParams.append('component', filters.component);
        if (filters.level) queryParams.append('level', filters.level);
        if (filters.startDate) queryParams.append('start', filters.startDate);
        if (filters.endDate) queryParams.append('end', filters.endDate);
        if (filters.limit) queryParams.append('limit', filters.limit);
        
        try {
            const url = `${this.apiUrl}/logs?${queryParams.toString()}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to fetch logs: ${response.status} ${response.statusText}` 
                });
                return this.systemLogs;
            }
            
            const data = await response.json();
            this.systemLogs = data.logs || [];
            
            // Dispatch event with logs
            this.dispatchEvent('logsUpdated', { 
                logs: this.systemLogs 
            });
            
            return this.systemLogs;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to fetch logs: ${error.message}` 
            });
            return this.systemLogs;
        }
    }
    
    /**
     * Start monitoring logs in real-time
     * @param {string} component - Optional component ID to filter logs
     * @returns {boolean} - Whether monitoring started successfully
     */
    startLogMonitoring(component = null) {
        if (this.logSocket) {
            this.stopLogMonitoring(); // Stop existing monitoring
        }
        
        try {
            // Create WebSocket connection to log stream
            // Convert HTTP URL to WebSocket URL
            let wsUrl = this.apiUrl.replace(/^http/, 'ws') + '/logs/stream';
            
            // Add component filter if specified
            if (component) {
                wsUrl += `?component=${encodeURIComponent(component)}`;
            }
            
            this.logSocket = new WebSocket(wsUrl);
            
            // Set up WebSocket handlers
            this.logSocket.onopen = () => {
                this.dispatchEvent('logMonitoringStarted', {});
            };
            
            this.logSocket.onmessage = (event) => {
                try {
                    const logEntry = JSON.parse(event.data);
                    
                    // Add to logs
                    this._addLogEntry(logEntry);
                    
                    // Dispatch log event
                    this.dispatchEvent('newLogEntry', { log: logEntry });
                } catch (error) {
                    console.error('Error processing log message:', error);
                }
            };
            
            this.logSocket.onerror = (error) => {
                this.dispatchEvent('error', { 
                    error: `WebSocket error: ${error.message || 'Unknown error'}` 
                });
            };
            
            this.logSocket.onclose = () => {
                this.dispatchEvent('logMonitoringStopped', {});
            };
            
            return true;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to start log monitoring: ${error.message}` 
            });
            return false;
        }
    }
    
    /**
     * Stop monitoring logs
     */
    stopLogMonitoring() {
        if (this.logSocket) {
            this.logSocket.close();
            this.logSocket = null;
        }
    }
    
    /**
     * Start monitoring system status in real-time
     * @returns {boolean} - Whether monitoring started successfully
     */
    startStatusMonitoring() {
        if (this.statusSocket) {
            return true; // Already monitoring
        }
        
        try {
            // Create WebSocket connection to status stream
            // Convert HTTP URL to WebSocket URL
            const wsUrl = this.apiUrl.replace(/^http/, 'ws') + '/status/stream';
            
            this.statusSocket = new WebSocket(wsUrl);
            
            // Set up WebSocket handlers
            this.statusSocket.onopen = () => {
                this.dispatchEvent('statusMonitoringStarted', {});
            };
            
            this.statusSocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    
                    // Update system status
                    if (data.status) {
                        this.systemStatus = data.status;
                    }
                    
                    // Update metrics history
                    if (data.metrics) {
                        this._updateMetricsHistory(data.metrics);
                    }
                    
                    // Update components if included
                    if (data.components) {
                        this.components = data.components;
                        this.dispatchEvent('componentsUpdated', {
                            components: this.components
                        });
                    }
                    
                    // Dispatch status event
                    this.dispatchEvent('statusUpdated', {
                        status: this.systemStatus,
                        metrics: data.metrics
                    });
                } catch (error) {
                    console.error('Error processing status message:', error);
                }
            };
            
            this.statusSocket.onerror = (error) => {
                this.dispatchEvent('error', { 
                    error: `WebSocket error: ${error.message || 'Unknown error'}` 
                });
            };
            
            this.statusSocket.onclose = () => {
                this.statusSocket = null;
                this.dispatchEvent('statusMonitoringStopped', {});
                
                // Try to reconnect after a delay
                setTimeout(() => {
                    if (!this.statusSocket) {
                        this.startStatusMonitoring();
                    }
                }, 5000);
            };
            
            return true;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to start status monitoring: ${error.message}` 
            });
            return false;
        }
    }
    
    /**
     * Get the list of projects
     * @returns {Promise<Array>} - Promise resolving to array of projects
     */
    async getProjects() {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/projects`);
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to fetch projects: ${response.status} ${response.statusText}` 
                });
                return this.projects;
            }
            
            const data = await response.json();
            this.projects = data.projects || [];
            
            // Dispatch event with projects
            this.dispatchEvent('projectsUpdated', { 
                projects: this.projects 
            });
            
            return this.projects;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to fetch projects: ${error.message}` 
            });
            return this.projects;
        }
    }
    
    /**
     * Get project details
     * @param {string} projectId - Project ID
     * @returns {Promise<Object>} - Promise resolving to project details
     */
    async getProjectDetails(projectId) {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/projects/${projectId}`);
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to fetch project details: ${response.status} ${response.statusText}` 
                });
                return null;
            }
            
            const data = await response.json();
            return data.project || null;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to fetch project details: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Create a new project
     * @param {Object} projectData - Project data
     * @returns {Promise<Object>} - Promise resolving to created project
     */
    async createProject(projectData) {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/projects`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(projectData)
            });
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to create project: ${response.status} ${response.statusText}` 
                });
                return null;
            }
            
            const data = await response.json();
            
            // Update projects list
            await this.getProjects();
            
            return data.project || null;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to create project: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Run system health check
     * @returns {Promise<Object>} - Promise resolving to health check results
     */
    async runHealthCheck() {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/health-check`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to run health check: ${response.status} ${response.statusText}` 
                });
                return null;
            }
            
            const data = await response.json();
            
            // Dispatch health check event
            this.dispatchEvent('healthCheckCompleted', { 
                results: data.results
            });
            
            return data.results || null;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to run health check: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Restart the entire system
     * @returns {Promise<boolean>} - Promise resolving to success status
     */
    async restartSystem() {
        if (!this.connected) {
            await this.connect();
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/restart`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                this.dispatchEvent('error', { 
                    error: `Failed to restart system: ${response.status} ${response.statusText}` 
                });
                return false;
            }
            
            // Dispatch restart event
            this.dispatchEvent('systemRestarting', {});
            
            return true;
        } catch (error) {
            this.dispatchEvent('error', { 
                error: `Failed to restart system: ${error.message}` 
            });
            return false;
        }
    }
    
    /**
     * Update metrics history with new data
     * @param {Object} metrics - Metrics data
     */
    _updateMetricsHistory(metrics) {
        // Get current timestamp
        const timestamp = new Date().getTime();
        
        // Update CPU metrics
        if (metrics.cpu !== undefined) {
            this.systemMetrics.cpu.push({
                timestamp: timestamp,
                value: metrics.cpu
            });
            
            // Trim history if needed
            if (this.systemMetrics.cpu.length > this.metricHistoryLength) {
                this.systemMetrics.cpu = this.systemMetrics.cpu.slice(-this.metricHistoryLength);
            }
        }
        
        // Update memory metrics
        if (metrics.memory !== undefined) {
            this.systemMetrics.memory.push({
                timestamp: timestamp,
                value: metrics.memory
            });
            
            // Trim history if needed
            if (this.systemMetrics.memory.length > this.metricHistoryLength) {
                this.systemMetrics.memory = this.systemMetrics.memory.slice(-this.metricHistoryLength);
            }
        }
        
        // Update disk metrics
        if (metrics.disk !== undefined) {
            this.systemMetrics.disk.push({
                timestamp: timestamp,
                value: metrics.disk
            });
            
            // Trim history if needed
            if (this.systemMetrics.disk.length > this.metricHistoryLength) {
                this.systemMetrics.disk = this.systemMetrics.disk.slice(-this.metricHistoryLength);
            }
        }
        
        // Update network metrics
        if (metrics.network !== undefined) {
            this.systemMetrics.network.push({
                timestamp: timestamp,
                value: metrics.network
            });
            
            // Trim history if needed
            if (this.systemMetrics.network.length > this.metricHistoryLength) {
                this.systemMetrics.network = this.systemMetrics.network.slice(-this.metricHistoryLength);
            }
        }
    }
    
    /**
     * Add a log entry to the logs
     * @param {Object} logEntry - Log entry object
     */
    _addLogEntry(logEntry) {
        // Add to beginning for more recent-first ordering
        this.systemLogs.unshift(logEntry);
        
        // Trim logs if they exceed maximum size
        if (this.systemLogs.length > this.maxLogEntries) {
            this.systemLogs = this.systemLogs.slice(0, this.maxLogEntries);
        }
    }
    
    /**
     * Get historical metrics
     * @param {string} metricType - Type of metric (cpu, memory, disk, network)
     * @param {Object} options - Options for filtering (timeRange, interval)
     * @returns {Array} - Array of metric data points
     */
    getMetricHistory(metricType, options = {}) {
        // Default to returning all history if no options
        if (!options.timeRange) {
            return this.systemMetrics[metricType] || [];
        }
        
        // Calculate cutoff time
        const now = new Date().getTime();
        let cutoffTime;
        
        switch (options.timeRange) {
            case '1h':
                cutoffTime = now - (60 * 60 * 1000);
                break;
            case '6h':
                cutoffTime = now - (6 * 60 * 60 * 1000);
                break;
            case '24h':
                cutoffTime = now - (24 * 60 * 60 * 1000);
                break;
            case '7d':
                cutoffTime = now - (7 * 24 * 60 * 60 * 1000);
                break;
            case '30d':
                cutoffTime = now - (30 * 24 * 60 * 60 * 1000);
                break;
            default:
                cutoffTime = now - (24 * 60 * 60 * 1000); // Default to 24 hours
        }
        
        // Filter metrics by cutoff time
        return (this.systemMetrics[metricType] || []).filter(
            metric => metric.timestamp >= cutoffTime
        );
    }
    
    /**
     * Load persisted state from storage
     */
    _loadPersistedState() {
        try {
            // Use local storage for persistence
            const persistedState = localStorage.getItem('tekton_service_state');
            
            if (persistedState) {
                const state = JSON.parse(persistedState);
                
                // Restore settings
                this.autoRefreshInterval = state.autoRefreshInterval || 10000;
                this.maxLogEntries = state.maxLogEntries || 500;
                this.metricHistoryLength = state.metricHistoryLength || 50;
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
                maxLogEntries: this.maxLogEntries,
                metricHistoryLength: this.metricHistoryLength
            };
            
            // Save to local storage
            localStorage.setItem('tekton_service_state', JSON.stringify(state));
        } catch (error) {
            console.error('Error persisting state:', error);
        }
    }
    
    /**
     * Clean up resources when service is destroyed
     */
    cleanup() {
        // Stop status monitoring
        if (this.statusSocket) {
            this.statusSocket.close();
            this.statusSocket = null;
        }
        
        // Stop log monitoring
        if (this.logSocket) {
            this.logSocket.close();
            this.logSocket = null;
        }
        
        // Stop auto-refresh
        this.stopAutoRefresh();
        
        // Final state persistence
        this._persistState();
    }
}

// Initialize the service when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Create and register the service if not already present
    if (!window.tektonUI?.services?.tektonService) {
        // Register it with the tektonUI global namespace
        window.tektonUI = window.tektonUI || {};
        window.tektonUI.services = window.tektonUI.services || {};
        
        // Create the service instance
        const tektonService = new TektonService();
        
        // Register the service
        window.tektonUI.services.tektonService = tektonService;
        
        console.log('Tekton Service initialized');
    }
});