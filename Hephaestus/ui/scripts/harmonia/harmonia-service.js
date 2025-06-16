/**
 * Harmonia Service
 * 
 * Provides API communication for the Harmonia component
 */

// Debug instrumentation
if (window.debugShim) {
    window.debugShim.registerModule('harmonia-service', {
        description: 'Harmonia Service - API Communication',
        version: '1.0.0'
    });
}

/**
 * Harmonia Service class
 */
class HarmoniaService {
    constructor() {
        this.debugLog('[HARMONIA-SERVICE] Constructing service');
        
        // Set API base URL - use environment configuration if available
        const harmoniaPort = window.HARMONIA_PORT || 8007;
        this.baseUrl = window.env && window.env.HARMONIA_API_URL 
            ? window.env.HARMONIA_API_URL 
            : `http://localhost:${harmoniaPort}/api`;
            
        // Set WebSocket URL - use environment configuration if available
        const harmoniaPort2 = window.HARMONIA_PORT || 8007;
        this.wsUrl = window.env && window.env.HARMONIA_WS_URL 
            ? window.env.HARMONIA_WS_URL 
            : `ws://localhost:${harmoniaPort2}/ws`;
            
        // Initialize WebSocket connection
        this.ws = null;
        this.wsConnected = false;
        this.wsQueue = [];
        this.wsCallbacks = new Map();
        
        // Initialize demo data (for UI testing)
        this.initDemoData();
        
        this.debugLog('[HARMONIA-SERVICE] Service constructed');
    }
    
    /**
     * Initialize WebSocket connection
     */
    initWebSocket() {
        this.debugLog('[HARMONIA-SERVICE] Initializing WebSocket connection');
        
        try {
            // Close existing connection if open
            if (this.ws) {
                this.ws.close();
            }
            
            // Create new WebSocket connection
            this.ws = new WebSocket(this.wsUrl);
            
            // Set up event handlers
            this.ws.onopen = () => {
                this.debugLog('[HARMONIA-SERVICE] WebSocket connected');
                this.wsConnected = true;
                
                // Process queued messages
                while (this.wsQueue.length > 0) {
                    const [message, callback] = this.wsQueue.shift();
                    this.sendWebSocketMessage(message, callback);
                }
            };
            
            this.ws.onmessage = (event) => {
                this.debugLog('[HARMONIA-SERVICE] WebSocket message received');
                
                try {
                    const data = JSON.parse(event.data);
                    
                    // Check if message has request ID
                    if (data.requestId && this.wsCallbacks.has(data.requestId)) {
                        // Call callback with message data
                        const callback = this.wsCallbacks.get(data.requestId);
                        callback(data);
                        
                        // Remove callback from map
                        this.wsCallbacks.delete(data.requestId);
                    } else {
                        this.debugLog('[HARMONIA-SERVICE] WebSocket message has no request ID or callback');
                    }
                } catch (error) {
                    this.debugLog('[HARMONIA-SERVICE] Error parsing WebSocket message', error);
                }
            };
            
            this.ws.onclose = () => {
                this.debugLog('[HARMONIA-SERVICE] WebSocket disconnected');
                this.wsConnected = false;
                
                // Reconnect after delay
                setTimeout(() => {
                    this.initWebSocket();
                }, 5000);
            };
            
            this.ws.onerror = (error) => {
                this.debugLog('[HARMONIA-SERVICE] WebSocket error', error);
                this.wsConnected = false;
            };
        } catch (error) {
            this.debugLog('[HARMONIA-SERVICE] Error initializing WebSocket', error);
        }
    }
    
    /**
     * Send a message via WebSocket
     * @param {Object} message - The message to send
     * @param {Function} callback - The callback to call when response is received
     */
    sendWebSocketMessage(message, callback) {
        this.debugLog('[HARMONIA-SERVICE] Sending WebSocket message');
        
        try {
            // Generate request ID if not provided
            if (!message.requestId) {
                message.requestId = this.generateRequestId();
            }
            
            // Register callback
            if (callback) {
                this.wsCallbacks.set(message.requestId, callback);
            }
            
            // Send message if connected, otherwise queue it
            if (this.wsConnected) {
                this.ws.send(JSON.stringify(message));
            } else {
                this.wsQueue.push([message, callback]);
                
                // Initialize WebSocket if not already
                if (!this.ws) {
                    this.initWebSocket();
                }
            }
        } catch (error) {
            this.debugLog('[HARMONIA-SERVICE] Error sending WebSocket message', error);
            
            // Call callback with error
            if (callback) {
                callback({
                    error: true,
                    message: 'Failed to send WebSocket message',
                    requestId: message.requestId
                });
            }
        }
    }
    
    /**
     * Generate a random request ID
     * @returns {string} - The generated request ID
     */
    generateRequestId() {
        return `req_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
    }
    
    /**
     * Make HTTP request to API
     * @param {string} endpoint - The API endpoint
     * @param {Object} options - The fetch options
     * @returns {Promise<Object>} - The API response
     */
    async makeRequest(endpoint, options = {}) {
        this.debugLog(`[HARMONIA-SERVICE] Making API request to ${endpoint}`);
        
        try {
            // Set default options
            const defaultOptions = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            
            // Merge options
            const mergedOptions = {
                ...defaultOptions,
                ...options,
                headers: {
                    ...defaultOptions.headers,
                    ...options.headers
                }
            };
            
            // Format endpoint URL
            const url = endpoint.startsWith('http')
                ? endpoint
                : `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
            
            // Make request with optional simulated delay
            if (this.useDemoData) {
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 500));
                
                // Check if demo data exists for this endpoint
                const key = `${mergedOptions.method.toLowerCase()}:${endpoint}`;
                if (this.demoData[key]) {
                    return this.demoData[key];
                }
                
                // Return empty response if no demo data
                return { data: [], success: true };
            }
            
            // Make real API request
            const response = await fetch(url, mergedOptions);
            
            // Check if response is OK
            if (!response.ok) {
                throw new Error(`API request failed with status ${response.status}`);
            }
            
            // Parse response
            const data = await response.json();
            
            this.debugLog(`[HARMONIA-SERVICE] API request to ${endpoint} successful`);
            
            return data;
        } catch (error) {
            this.debugLog(`[HARMONIA-SERVICE] API request to ${endpoint} failed`, error);
            
            // Use demo data if API request fails
            const key = `${options.method || 'get'}:${endpoint}`;
            if (this.demoData[key]) {
                return this.demoData[key];
            }
            
            throw error;
        }
    }
    
    /**
     * Get workflows
     * @returns {Promise<Array>} - The list of workflows
     */
    async getWorkflows() {
        this.debugLog('[HARMONIA-SERVICE] Getting workflows');
        
        try {
            const response = await this.makeRequest('/workflows');
            return response.data || [];
        } catch (error) {
            this.debugLog('[HARMONIA-SERVICE] Error getting workflows', error);
            return this.demoData['get:/workflows'].data || [];
        }
    }
    
    /**
     * Get a workflow by ID
     * @param {string} id - The workflow ID
     * @returns {Promise<Object>} - The workflow
     */
    async getWorkflow(id) {
        this.debugLog(`[HARMONIA-SERVICE] Getting workflow ${id}`);
        
        try {
            const response = await this.makeRequest(`/workflows/${id}`);
            return response.data || null;
        } catch (error) {
            this.debugLog(`[HARMONIA-SERVICE] Error getting workflow ${id}`, error);
            return this.demoData['get:/workflows/1'].data || null;
        }
    }
    
    /**
     * Create a new workflow
     * @param {Object} workflow - The workflow to create
     * @returns {Promise<Object>} - The created workflow
     */
    async createWorkflow(workflow) {
        this.debugLog('[HARMONIA-SERVICE] Creating workflow');
        
        try {
            const response = await this.makeRequest('/workflows', {
                method: 'POST',
                body: JSON.stringify(workflow)
            });
            return response.data || null;
        } catch (error) {
            this.debugLog('[HARMONIA-SERVICE] Error creating workflow', error);
            return null;
        }
    }
    
    /**
     * Update a workflow
     * @param {string} id - The workflow ID
     * @param {Object} workflow - The updated workflow
     * @returns {Promise<Object>} - The updated workflow
     */
    async updateWorkflow(id, workflow) {
        this.debugLog(`[HARMONIA-SERVICE] Updating workflow ${id}`);
        
        try {
            const response = await this.makeRequest(`/workflows/${id}`, {
                method: 'PUT',
                body: JSON.stringify(workflow)
            });
            return response.data || null;
        } catch (error) {
            this.debugLog(`[HARMONIA-SERVICE] Error updating workflow ${id}`, error);
            return null;
        }
    }
    
    /**
     * Delete a workflow
     * @param {string} id - The workflow ID
     * @returns {Promise<boolean>} - Whether the deletion was successful
     */
    async deleteWorkflow(id) {
        this.debugLog(`[HARMONIA-SERVICE] Deleting workflow ${id}`);
        
        try {
            const response = await this.makeRequest(`/workflows/${id}`, {
                method: 'DELETE'
            });
            return response.success || false;
        } catch (error) {
            this.debugLog(`[HARMONIA-SERVICE] Error deleting workflow ${id}`, error);
            return false;
        }
    }
    
    /**
     * Execute a workflow
     * @param {string} id - The workflow ID
     * @returns {Promise<Object>} - The execution
     */
    async executeWorkflow(id) {
        this.debugLog(`[HARMONIA-SERVICE] Executing workflow ${id}`);
        
        try {
            const response = await this.makeRequest(`/workflows/${id}/execute`, {
                method: 'POST'
            });
            return response.data || null;
        } catch (error) {
            this.debugLog(`[HARMONIA-SERVICE] Error executing workflow ${id}`, error);
            return null;
        }
    }
    
    /**
     * Get templates
     * @returns {Promise<Array>} - The list of templates
     */
    async getTemplates() {
        this.debugLog('[HARMONIA-SERVICE] Getting templates');
        
        try {
            const response = await this.makeRequest('/templates');
            return response.data || [];
        } catch (error) {
            this.debugLog('[HARMONIA-SERVICE] Error getting templates', error);
            return this.demoData['get:/templates'].data || [];
        }
    }
    
    /**
     * Get a template by ID
     * @param {string} id - The template ID
     * @returns {Promise<Object>} - The template
     */
    async getTemplate(id) {
        this.debugLog(`[HARMONIA-SERVICE] Getting template ${id}`);
        
        try {
            const response = await this.makeRequest(`/templates/${id}`);
            return response.data || null;
        } catch (error) {
            this.debugLog(`[HARMONIA-SERVICE] Error getting template ${id}`, error);
            return this.demoData['get:/templates/1'].data || null;
        }
    }
    
    /**
     * Create a new template
     * @param {Object} template - The template to create
     * @returns {Promise<Object>} - The created template
     */
    async createTemplate(template) {
        this.debugLog('[HARMONIA-SERVICE] Creating template');
        
        try {
            const response = await this.makeRequest('/templates', {
                method: 'POST',
                body: JSON.stringify(template)
            });
            return response.data || null;
        } catch (error) {
            this.debugLog('[HARMONIA-SERVICE] Error creating template', error);
            return null;
        }
    }
    
    /**
     * Update a template
     * @param {string} id - The template ID
     * @param {Object} template - The updated template
     * @returns {Promise<Object>} - The updated template
     */
    async updateTemplate(id, template) {
        this.debugLog(`[HARMONIA-SERVICE] Updating template ${id}`);
        
        try {
            const response = await this.makeRequest(`/templates/${id}`, {
                method: 'PUT',
                body: JSON.stringify(template)
            });
            return response.data || null;
        } catch (error) {
            this.debugLog(`[HARMONIA-SERVICE] Error updating template ${id}`, error);
            return null;
        }
    }
    
    /**
     * Delete a template
     * @param {string} id - The template ID
     * @returns {Promise<boolean>} - Whether the deletion was successful
     */
    async deleteTemplate(id) {
        this.debugLog(`[HARMONIA-SERVICE] Deleting template ${id}`);
        
        try {
            const response = await this.makeRequest(`/templates/${id}`, {
                method: 'DELETE'
            });
            return response.success || false;
        } catch (error) {
            this.debugLog(`[HARMONIA-SERVICE] Error deleting template ${id}`, error);
            return false;
        }
    }
    
    /**
     * Use a template to create a workflow
     * @param {string} id - The template ID
     * @returns {Promise<Object>} - The created workflow
     */
    async useTemplate(id) {
        this.debugLog(`[HARMONIA-SERVICE] Using template ${id}`);
        
        try {
            const response = await this.makeRequest(`/templates/${id}/use`, {
                method: 'POST'
            });
            return response.data || null;
        } catch (error) {
            this.debugLog(`[HARMONIA-SERVICE] Error using template ${id}`, error);
            return null;
        }
    }
    
    /**
     * Get executions
     * @returns {Promise<Array>} - The list of executions
     */
    async getExecutions() {
        this.debugLog('[HARMONIA-SERVICE] Getting executions');
        
        try {
            const response = await this.makeRequest('/executions');
            return response.data || [];
        } catch (error) {
            this.debugLog('[HARMONIA-SERVICE] Error getting executions', error);
            return this.demoData['get:/executions'].data || [];
        }
    }
    
    /**
     * Get an execution by ID
     * @param {string} id - The execution ID
     * @returns {Promise<Object>} - The execution
     */
    async getExecution(id) {
        this.debugLog(`[HARMONIA-SERVICE] Getting execution ${id}`);
        
        try {
            const response = await this.makeRequest(`/executions/${id}`);
            return response.data || null;
        } catch (error) {
            this.debugLog(`[HARMONIA-SERVICE] Error getting execution ${id}`, error);
            return this.demoData['get:/executions/1'].data || null;
        }
    }
    
    /**
     * Get execution logs
     * @param {string} id - The execution ID
     * @returns {Promise<Array>} - The execution logs
     */
    async getExecutionLogs(id) {
        this.debugLog(`[HARMONIA-SERVICE] Getting execution logs ${id}`);
        
        try {
            const response = await this.makeRequest(`/executions/${id}/logs`);
            return response.data || [];
        } catch (error) {
            this.debugLog(`[HARMONIA-SERVICE] Error getting execution logs ${id}`, error);
            return [];
        }
    }
    
    /**
     * Stop an execution
     * @param {string} id - The execution ID
     * @returns {Promise<boolean>} - Whether the stop was successful
     */
    async stopExecution(id) {
        this.debugLog(`[HARMONIA-SERVICE] Stopping execution ${id}`);
        
        try {
            const response = await this.makeRequest(`/executions/${id}/stop`, {
                method: 'POST'
            });
            return response.success || false;
        } catch (error) {
            this.debugLog(`[HARMONIA-SERVICE] Error stopping execution ${id}`, error);
            return false;
        }
    }
    
    /**
     * Send a chat message
     * @param {string} chatType - The type of chat ('workflowchat' or 'teamchat')
     * @param {string} message - The message to send
     * @returns {Promise<string>} - The response message
     */
    async sendChatMessage(chatType, message) {
        this.debugLog(`[HARMONIA-SERVICE] Sending chat message to ${chatType}`);
        
        try {
            // For demo, simulate a response
            if (this.useDemoData) {
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 500));
                
                // Return demo response
                if (chatType === 'workflowchat') {
                    return 'I can help you with workflow creation and management. What specific assistance do you need?';
                } else {
                    return 'Your message has been shared with the team. Someone will respond shortly.';
                }
            }
            
            // For real implementation, use WebSocket
            return new Promise((resolve, reject) => {
                this.sendWebSocketMessage({
                    type: 'chat',
                    chatType,
                    message
                }, (response) => {
                    if (response.error) {
                        reject(new Error(response.message));
                    } else {
                        resolve(response.message);
                    }
                });
            });
        } catch (error) {
            this.debugLog('[HARMONIA-SERVICE] Error sending chat message', error);
            
            // Return fallback response
            if (chatType === 'workflowchat') {
                return 'I apologize, but I experienced an error processing your request. Please try again later.';
            } else {
                return 'Your message could not be delivered due to a service error. Please try again later.';
            }
        }
    }
    
    /**
     * Initialize demo data for UI testing
     */
    initDemoData() {
        this.debugLog('[HARMONIA-SERVICE] Initializing demo data');
        
        // Set flag to use demo data
        this.useDemoData = true;
        
        // Create demo data store
        this.demoData = {
            // Workflows
            'get:/workflows': {
                data: [
                    {
                        id: '1',
                        name: 'Data Processing Pipeline',
                        description: 'Process and analyze data from multiple sources',
                        status: 'Active',
                        taskCount: 12,
                        lastModified: '2025-05-14T08:30:22Z'
                    },
                    {
                        id: '2',
                        name: 'Content Generation',
                        description: 'Generate content using various LLM models',
                        status: 'Active',
                        taskCount: 8,
                        lastModified: '2025-05-14T09:15:45Z'
                    },
                    {
                        id: '3',
                        name: 'Deployment Pipeline',
                        description: 'Automated deployment with testing and monitoring',
                        status: 'Inactive',
                        taskCount: 16,
                        lastModified: '2025-05-13T14:20:10Z'
                    }
                ],
                success: true
            },
            
            // Single workflow
            'get:/workflows/1': {
                data: {
                    id: '1',
                    name: 'Data Processing Pipeline',
                    description: 'Process and analyze data from multiple sources',
                    status: 'Active',
                    taskCount: 12,
                    lastModified: '2025-05-14T08:30:22Z',
                    tasks: [
                        { id: '1', name: 'Extract Data', type: 'extract', status: 'completed' },
                        { id: '2', name: 'Transform', type: 'transform', status: 'completed' },
                        { id: '3', name: 'Load', type: 'load', status: 'pending' }
                    ]
                },
                success: true
            },
            
            // Templates
            'get:/templates': {
                data: [
                    {
                        id: '1',
                        name: 'Data Processing Template',
                        description: 'Standard pipeline for processing and analyzing data',
                        category: 'Data Processing',
                        usageCount: 24,
                        lastModified: '2025-05-10T11:20:33Z'
                    },
                    {
                        id: '2',
                        name: 'Content Generation Template',
                        description: 'Template for generating content with various LLMs',
                        category: 'Content Generation',
                        usageCount: 18,
                        lastModified: '2025-05-12T15:45:12Z'
                    },
                    {
                        id: '3',
                        name: 'Deployment Template',
                        description: 'Standard deployment with testing and monitoring',
                        category: 'Deployment',
                        usageCount: 32,
                        lastModified: '2025-05-09T09:30:45Z'
                    }
                ],
                success: true
            },
            
            // Single template
            'get:/templates/1': {
                data: {
                    id: '1',
                    name: 'Data Processing Template',
                    description: 'Standard pipeline for processing and analyzing data',
                    category: 'Data Processing',
                    usageCount: 24,
                    lastModified: '2025-05-10T11:20:33Z',
                    tasks: [
                        { id: '1', name: 'Extract Data', type: 'extract' },
                        { id: '2', name: 'Transform', type: 'transform' },
                        { id: '3', name: 'Load', type: 'load' }
                    ]
                },
                success: true
            },
            
            // Executions
            'get:/executions': {
                data: [
                    {
                        id: 'EXEC-001',
                        workflowId: '1',
                        workflowName: 'Data Processing Pipeline',
                        startTime: '2025-05-14 08:30:22',
                        duration: '12m 34s',
                        status: 'Completed'
                    },
                    {
                        id: 'EXEC-002',
                        workflowId: '2',
                        workflowName: 'Content Generation',
                        startTime: '2025-05-14 09:15:45',
                        duration: 'Running (5m 22s)',
                        status: 'Running'
                    },
                    {
                        id: 'EXEC-003',
                        workflowId: '1',
                        workflowName: 'Data Processing Pipeline',
                        startTime: '2025-05-13 14:20:10',
                        duration: '15m 02s',
                        status: 'Failed'
                    }
                ],
                success: true
            },
            
            // Single execution
            'get:/executions/1': {
                data: {
                    id: 'EXEC-001',
                    workflowId: '1',
                    workflowName: 'Data Processing Pipeline',
                    startTime: '2025-05-14 08:30:22',
                    endTime: '2025-05-14 08:42:56',
                    duration: '12m 34s',
                    status: 'Completed',
                    taskResults: [
                        { id: '1', name: 'Extract Data', status: 'Completed', duration: '3m 12s' },
                        { id: '2', name: 'Transform', status: 'Completed', duration: '5m 22s' },
                        { id: '3', name: 'Load', status: 'Completed', duration: '4m 00s' }
                    ]
                },
                success: true
            }
        };
        
        this.debugLog('[HARMONIA-SERVICE] Demo data initialized');
    }
    
    /**
     * Debug logging with service prefix
     * @param {string} message - The message to log
     * @param {Error} [error] - Optional error object
     */
    debugLog(message, error) {
        // Use debug shim if available
        if (window.debugShim) {
            if (error) {
                window.debugShim.logError('harmonia-service', message, error);
            } else {
                window.debugShim.log('harmonia-service', message);
            }
        } else {
            // Fallback to console
            if (error) {
                console.error(message, error);
            } else {
                console.log(message);
            }
        }
    }
}

// Export service
export { HarmoniaService };