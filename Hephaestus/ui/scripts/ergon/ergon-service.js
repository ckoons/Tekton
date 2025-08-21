/**
 * ErgonService.js
 * 
 * Service abstraction layer for the Ergon API that integrates with the state management system.
 * This service provides methods to interact with Ergon agents, executions, and settings,
 * while automatically updating the state system with the results.
 */

console.log('[FILE_TRACE] Loading: ergon-service.js');
class ErgonService {
    constructor() {
        this.initialized = false;
        this.apiBase = window.ergonUrl ? window.ergonUrl('/api/v1') : 'http://localhost:8002/api/v1';
        this.pendingRequests = new Map();
        this.requestTimeouts = {};
        this.cache = {
            agents: {
                data: null,
                timestamp: 0,
                ttl: 30000 // 30 seconds
            },
            agentTypes: {
                data: null,
                timestamp: 0,
                ttl: 300000 // 5 minutes
            },
            settings: {
                data: null,
                timestamp: 0,
                ttl: 60000 // 1 minute
            }
        };
        this.autoRefreshIntervals = {};
        this.isPollingForUpdates = false;
        this.webSocketConnections = {};
    }
    
    /**
     * Initialize the Ergon service
     * 
     * @param {Object} options - Configuration options
     * @returns {ErgonService} - The service instance
     */
    init(options = {}) {
        if (this.initialized) return this;
        
        // Register in window.tektonUI
        if (!window.tektonUI) {
            window.tektonUI = {};
        }
        
        window.tektonUI.ergonService = this;
        
        // Set configuration options
        this.apiBase = options.apiBase || this.apiBase;
        
        // Check if we have a state manager
        this.stateManager = window.tektonUI.stateManager;
        this.ergonStateManager = window.tektonUI.ergonStateManager;
        
        if (!this.stateManager || !this.ergonStateManager) {
            console.error('[ErgonService] State managers not available');
            return this;
        }
        
        // Start auto-refresh based on settings, if enabled
        this._initializeAutoRefresh();
        
        // Subscribe to settings changes to update auto-refresh
        this.ergonStateManager.subscribeToSettings((changes) => {
            if (changes.autoRefreshInterval) {
                this._updateAutoRefreshInterval();
            }
        }, { keys: ['autoRefreshInterval'] });
        
        this.initialized = true;
        console.log('[ErgonService] Initialized');
        
        return this;
    }
    
    /**
     * Initialize auto-refresh based on settings
     * @private
     */
    _initializeAutoRefresh() {
        const settings = this.ergonStateManager.getSettings();
        
        if (settings && settings.autoRefreshInterval) {
            const interval = settings.autoRefreshInterval * 1000; // Convert to ms
            
            if (interval > 0) {
                // Set up auto-refresh for agents
                this.autoRefreshIntervals.agents = setInterval(() => {
                    this.fetchAgents({ bypassCache: true });
                }, interval);
                
                // Set up auto-refresh for executions
                this.autoRefreshIntervals.executions = setInterval(() => {
                    const activeExecutions = this.ergonStateManager.getExecutionState('activeExecutions');
                    
                    if (activeExecutions && Object.keys(activeExecutions).length > 0) {
                        // Only fetch execution updates if there are active executions
                        this._pollActiveExecutions();
                    }
                }, Math.min(interval, 5000)); // Poll executions more frequently, max every 5s
            }
        }
    }
    
    /**
     * Update auto-refresh interval based on new settings
     * @private
     */
    _updateAutoRefreshInterval() {
        // Clear existing intervals
        Object.values(this.autoRefreshIntervals).forEach(interval => {
            clearInterval(interval);
        });
        
        this.autoRefreshIntervals = {};
        
        // Reinitialize with new settings
        this._initializeAutoRefresh();
    }
    
    /**
     * Poll for active execution updates
     * @private
     */
    async _pollActiveExecutions() {
        if (this.isPollingForUpdates) return;
        
        this.isPollingForUpdates = true;
        
        try {
            const activeExecutions = this.ergonStateManager.getExecutionState('activeExecutions');
            if (!activeExecutions || Object.keys(activeExecutions).length === 0) {
                return;
            }
            
            // Get execution IDs
            const executionIds = Object.keys(activeExecutions);
            
            // Fetch status for each execution
            const statusPromises = executionIds.map(id => this.fetchExecutionStatus(id));
            
            // Wait for all status requests to complete
            await Promise.all(statusPromises);
            
        } catch (error) {
            console.error('[ErgonService] Error polling executions:', error);
        } finally {
            this.isPollingForUpdates = false;
        }
    }
    
    /**
     * Fetch all agents
     * 
     * @param {Object} options - Fetch options
     * @returns {Promise<Array>} - List of agents
     */
    async fetchAgents(options = {}) {
        try {
            // Set loading state
            this.ergonStateManager.setAgentState({ isLoading: true });
            
            // Check cache if not bypassing
            if (!options.bypassCache && this.cache.agents.data) {
                const now = Date.now();
                if (now - this.cache.agents.timestamp < this.cache.agents.ttl) {
                    // Return cached data
                    this.ergonStateManager.updateAgentList(this.cache.agents.data);
                    this.ergonStateManager.setAgentState({ isLoading: false });
                    return this.cache.agents.data;
                }
            }
            
            // Fetch agents from API
            const response = await fetch(`${this.apiBase}/agents`);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            const data = await response.json();
            const agents = data.agents || data; // Handle different API response formats
            
            // Update state
            this.ergonStateManager.updateAgentList(agents);
            
            // Update cache
            this.cache.agents.data = agents;
            this.cache.agents.timestamp = Date.now();
            
            return agents;
            
        } catch (error) {
            // Update error state
            this.ergonStateManager.setAgentState({ 
                isLoading: false,
                lastError: error.message || String(error)
            });
            throw error;
        } finally {
            // Ensure loading state is updated even if error occurs
            this.ergonStateManager.setAgentState({ isLoading: false });
        }
    }
    
    /**
     * Fetch a specific agent by ID
     * 
     * @param {string|number} agentId - Agent ID
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} - Agent details
     */
    async fetchAgentById(agentId, options = {}) {
        try {
            // Check if agent is in state already
            const existingAgent = this.ergonStateManager.getAgentById(agentId);
            
            // If agent exists and we're not forcing refresh, return it
            if (existingAgent && !options.forceRefresh) {
                return existingAgent;
            }
            
            // Fetch agent from API
            const response = await fetch(`${this.apiBase}/agents/${agentId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            const agent = await response.json();
            
            // Update agent in state
            this.ergonStateManager.addOrUpdateAgent(agent);
            
            return agent;
            
        } catch (error) {
            console.error(`[ErgonService] Error fetching agent ${agentId}:`, error);
            throw error;
        }
    }
    
    /**
     * Create a new agent
     * 
     * @param {Object} agentData - Agent configuration
     * @returns {Promise<Object>} - Created agent
     */
    async createAgent(agentData) {
        try {
            // Set loading state
            this.ergonStateManager.setAgentState({ isLoading: true });
            
            // Create agent via API - RESTful endpoint
            const response = await fetch(`${this.apiBase}/agents`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(agentData),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            const agent = await response.json();
            
            // Add agent to state
            this.ergonStateManager.addOrUpdateAgent(agent);
            
            return agent;
            
        } catch (error) {
            console.error('[ErgonService] Error creating agent:', error);
            throw error;
        } finally {
            // Ensure loading state is updated even if error occurs
            this.ergonStateManager.setAgentState({ isLoading: false });
        }
    }
    
    /**
     * Delete an agent
     * 
     * @param {string|number} agentId - Agent ID
     * @param {boolean} force - Force deletion
     * @returns {Promise<Object>} - Response data
     */
    async deleteAgent(agentId, force = false) {
        try {
            // Set loading state
            this.ergonStateManager.setAgentState({ isLoading: true });
            
            // Delete agent via API - RESTful endpoint
            const response = await fetch(`${this.apiBase}/agents/${agentId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ force }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            const result = await response.json();
            
            // Remove agent from state
            this.ergonStateManager.removeAgent(agentId);
            
            // Clear agent executions
            this.ergonStateManager.clearAgentExecutions(agentId);
            
            return result;
            
        } catch (error) {
            console.error(`[ErgonService] Error deleting agent ${agentId}:`, error);
            throw error;
        } finally {
            // Ensure loading state is updated even if error occurs
            this.ergonStateManager.setAgentState({ isLoading: false });
        }
    }
    
    /**
     * Run an agent with optional parameters
     * 
     * @param {string|number} agentId - Agent ID
     * @param {Object} options - Run options (input, interactive, timeout, etc.)
     * @returns {Promise<Object>} - Execution object with ID
     */
    async runAgent(agentId, options = {}) {
        try {
            // Create execution object
            const executionId = `execution-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
            const agent = this.ergonStateManager.getAgentById(agentId);
            
            if (!agent) {
                throw new Error(`Agent with ID ${agentId} not found`);
            }
            
            // Create execution tracking
            const execution = {
                id: executionId,
                agentId,
                agentName: agent.name,
                input: options.input || '',
                status: 'starting',
                startTime: new Date().toISOString()
            };
            
            // Track execution in state
            this.ergonStateManager.trackExecution(execution);
            
            // Run agent via API (but don't wait for it to complete here) - RESTful endpoint
            const runPromise = fetch(`${this.apiBase}/agents/${agentId}/run`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(options),
            }).then(async response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                
                if (options.streaming) {
                    return { 
                        executionId, 
                        streaming: true, 
                        status: 'running'
                    };
                }
                
                const result = await response.json();
                
                // Complete execution in state
                this.ergonStateManager.completeExecution(executionId, {
                    output: result.content,
                    status: 'completed'
                });
                
                return {
                    executionId,
                    output: result.content,
                    status: 'completed'
                };
            }).catch(error => {
                // Set execution error
                this.ergonStateManager.setExecutionError(executionId, {
                    message: error.message || String(error)
                });
                
                throw error;
            });
            
            // Don't wait for completion, return execution ID immediately
            return { 
                executionId, 
                execution,
                // Attach promise but don't make caller wait for it
                promise: runPromise
            };
            
        } catch (error) {
            console.error(`[ErgonService] Error running agent ${agentId}:`, error);
            throw error;
        }
    }
    
    /**
     * Run an agent with streaming response
     * 
     * @param {string|number} agentId - Agent ID
     * @param {Object} options - Run options
     * @param {Function} onChunk - Callback for each chunk of streaming response
     * @returns {Promise<Object>} - Execution details
     */
    async runAgentWithStreaming(agentId, options = {}, onChunk = null) {
        try {
            // Create execution object
            const executionId = `execution-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
            const agent = this.ergonStateManager.getAgentById(agentId);
            
            if (!agent) {
                throw new Error(`Agent with ID ${agentId} not found`);
            }
            
            // Create execution tracking
            const execution = {
                id: executionId,
                agentId,
                agentName: agent.name,
                input: options.input || '',
                status: 'streaming',
                startTime: new Date().toISOString()
            };
            
            // Track execution in state
            this.ergonStateManager.trackExecution(execution);
            
            // Run agent via API with streaming - RESTful endpoint
            const response = await fetch(`${this.apiBase}/agents/${agentId}/run`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ...options,
                    streaming: true
                }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            // Set up streaming response reader
            const reader = response.body.getReader();
            let chunks = [];
            let decoder = new TextDecoder();
            
            // Process the stream
            while (true) {
                const { value, done } = await reader.read();
                
                if (done) {
                    break;
                }
                
                // Convert bytes to text
                const chunkText = decoder.decode(value, { stream: true });
                
                // Parse SSE data
                const lines = chunkText.split('\n\n');
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const eventData = line.substring(6);
                        
                        if (eventData === '[DONE]') {
                            // Stream is complete
                            continue;
                        }
                        
                        try {
                            const parsedData = JSON.parse(eventData);
                            chunks.push(parsedData.chunk || parsedData.text || '');
                            
                            // Call chunk callback if provided
                            if (onChunk && typeof onChunk === 'function') {
                                onChunk(parsedData.chunk || parsedData.text || '', false);
                            }
                        } catch (e) {
                            console.warn('Error parsing streaming data:', e);
                        }
                    }
                }
            }
            
            // Complete execution in state
            const fullOutput = chunks.join('');
            this.ergonStateManager.completeExecution(executionId, {
                output: fullOutput,
                status: 'completed'
            });
            
            // Call chunk callback one last time with done=true
            if (onChunk && typeof onChunk === 'function') {
                onChunk(fullOutput, true);
            }
            
            return {
                executionId,
                output: fullOutput,
                status: 'completed'
            };
            
        } catch (error) {
            console.error(`[ErgonService] Error running agent ${agentId} with streaming:`, error);
            throw error;
        }
    }
    
    /**
     * Fetch the status of an execution
     * 
     * @param {string|number} executionId - Execution ID
     * @returns {Promise<Object>} - Execution status
     */
    async fetchExecutionStatus(executionId) {
        try {
            // Fetch execution status from API
            const response = await fetch(`${this.apiBase}/executions/${executionId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            const status = await response.json();
            
            // Update execution state based on status
            if (status.status === 'completed' || status.status === 'success') {
                this.ergonStateManager.completeExecution(executionId, {
                    output: status.output || status.result,
                    status: 'completed'
                });
            } else if (status.status === 'error' || status.status === 'failed') {
                this.ergonStateManager.setExecutionError(executionId, {
                    message: status.error || 'Execution failed'
                });
            }
            
            return status;
            
        } catch (error) {
            console.error(`[ErgonService] Error fetching execution status ${executionId}:`, error);
            throw error;
        }
    }
    
    /**
     * Fetch all agent types
     * 
     * @param {Object} options - Fetch options
     * @returns {Promise<Array>} - List of agent types
     */
    async fetchAgentTypes(options = {}) {
        try {
            // Set loading state
            this.ergonStateManager.setAgentTypes({ isLoading: true });
            
            // Check cache if not bypassing
            if (!options.bypassCache && this.cache.agentTypes.data) {
                const now = Date.now();
                if (now - this.cache.agentTypes.timestamp < this.cache.agentTypes.ttl) {
                    // Return cached data
                    this.ergonStateManager.setAgentTypes({
                        types: this.cache.agentTypes.data,
                        isLoading: false
                    });
                    return this.cache.agentTypes.data;
                }
            }
            
            // Fetch agent types from API
            const response = await fetch(`${this.apiBase}/agent-types`);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            const data = await response.json();
            const types = data.types || data; // Handle different API response formats
            
            // Build type index and categories
            const typeIndex = {};
            const typeCategories = new Set();
            
            types.forEach(type => {
                typeIndex[type.id] = type;
                if (type.category) {
                    typeCategories.add(type.category);
                }
            });
            
            // Update state
            this.ergonStateManager.setAgentTypes({
                types,
                typeIndex,
                typeCategories: Array.from(typeCategories),
                isLoading: false
            });
            
            // Update cache
            this.cache.agentTypes.data = types;
            this.cache.agentTypes.timestamp = Date.now();
            
            return types;
            
        } catch (error) {
            // Update error state
            console.error('[ErgonService] Error fetching agent types:', error);
            this.ergonStateManager.setAgentTypes({ isLoading: false });
            throw error;
        }
    }
    
    /**
     * Fetch server settings
     * 
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} - Settings
     */
    async fetchSettings(options = {}) {
        try {
            // Check cache if not bypassing
            if (!options.bypassCache && this.cache.settings.data) {
                const now = Date.now();
                if (now - this.cache.settings.timestamp < this.cache.settings.ttl) {
                    // Return cached data
                    return this.cache.settings.data;
                }
            }
            
            // Fetch settings from API
            const response = await fetch(`${this.apiBase}/settings`);
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            const serverSettings = await response.json();
            
            // Get current UI settings
            const currentSettings = this.ergonStateManager.getSettings();
            const uiSettings = currentSettings.ui || {};
            
            // Merge server settings with UI settings
            const mergedSettings = {
                ...serverSettings,
                ui: uiSettings
            };
            
            // Update settings in state
            this.ergonStateManager.setSettings(mergedSettings);
            
            // Update cache
            this.cache.settings.data = mergedSettings;
            this.cache.settings.timestamp = Date.now();
            
            return mergedSettings;
            
        } catch (error) {
            console.error('[ErgonService] Error fetching settings:', error);
            throw error;
        }
    }
    
    /**
     * Update settings
     * 
     * @param {Object} settings - Settings to update
     * @returns {Promise<Object>} - Updated settings
     */
    async updateSettings(settings) {
        try {
            // Send update to server
            const response = await fetch(`${this.apiBase}/settings`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            const updatedSettings = await response.json();
            
            // Get current UI settings
            const currentSettings = this.ergonStateManager.getSettings();
            const uiSettings = currentSettings.ui || {};
            
            // Merge updated settings with UI settings
            const mergedSettings = {
                ...updatedSettings,
                ui: {
                    ...uiSettings,
                    ...(settings.ui || {})
                }
            };
            
            // Update settings in state
            this.ergonStateManager.setSettings(mergedSettings);
            
            // Update cache
            this.cache.settings.data = mergedSettings;
            this.cache.settings.timestamp = Date.now();
            
            return mergedSettings;
            
        } catch (error) {
            console.error('[ErgonService] Error updating settings:', error);
            throw error;
        }
    }
    
    /**
     * Update UI settings only (not sent to server)
     * 
     * @param {Object} uiSettings - UI settings to update
     * @returns {Object} - Updated UI settings
     */
    updateUISettings(uiSettings) {
        try {
            // Get current settings
            const currentSettings = this.ergonStateManager.getSettings();
            const currentUISettings = currentSettings.ui || {};
            
            // Merge UI settings
            const mergedUISettings = {
                ...currentUISettings,
                ...uiSettings
            };
            
            // Update settings in state
            this.ergonStateManager.setSettings({
                ui: mergedUISettings
            });
            
            // Update cache if it exists
            if (this.cache.settings.data) {
                this.cache.settings.data.ui = mergedUISettings;
                this.cache.settings.timestamp = Date.now();
            }
            
            return mergedUISettings;
            
        } catch (error) {
            console.error('[ErgonService] Error updating UI settings:', error);
            throw error;
        }
    }
}

// Create and export the ErgonService instance
window.tektonUI = window.tektonUI || {};
window.tektonUI.ErgonService = ErgonService;

// Export a singleton instance
window.tektonUI.ergonService = new ErgonService();

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize after state manager is ready
    const checkStateManager = () => {
        if (window.tektonUI.ergonStateManager && window.tektonUI.stateManager) {
            // Initialize with default options
            window.tektonUI.ergonService.init();
        } else {
            // Wait for state manager to initialize
            setTimeout(checkStateManager, 100);
        }
    };
    
    checkStateManager();
});
