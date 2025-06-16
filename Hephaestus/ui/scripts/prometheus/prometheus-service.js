/**
 * Prometheus Service
 * 
 * Provides communication with the Prometheus API for planning and project management.
 * Follows the Single Port Architecture pattern.
 */

class PrometheusService {
    constructor() {
        this.debugPrefix = '[PROMETHEUS SERVICE]';
        console.log(`${this.debugPrefix} Service constructed`);
        
        // Get API URL from environment or use default
        const prometheusPort = window.PROMETHEUS_PORT || 8006;
        this.apiUrl = window.ENV?.PROMETHEUS_URL || `http://localhost:${prometheusPort}`;
        this.apiBaseUrl = `${this.apiUrl}/api`;
        
        // Get WebSocket URL for streaming responses
        this.wsUrl = window.ENV?.PROMETHEUS_WS_URL || this.apiUrl.replace('http', 'ws');
        this.wsBaseUrl = `${this.wsUrl}/ws`;
        
        this.token = null;
        this.isConnected = false;
        
        // Initialize WebSocket connection if needed
        this.initializeWebSocket();
    }

    /**
     * Initialize WebSocket connection for real-time updates
     */
    initializeWebSocket() {
        try {
            this.ws = new WebSocket(`${this.wsBaseUrl}/updates`);
            
            this.ws.onopen = () => {
                console.log(`${this.debugPrefix} WebSocket connection established`);
                this.isConnected = true;
            };
            
            this.ws.onclose = () => {
                console.log(`${this.debugPrefix} WebSocket connection closed`);
                this.isConnected = false;
                
                // Attempt to reconnect after delay
                setTimeout(() => this.initializeWebSocket(), 5000);
            };
            
            this.ws.onerror = (error) => {
                console.error(`${this.debugPrefix} WebSocket error:`, error);
                this.isConnected = false;
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    console.log(`${this.debugPrefix} Received WebSocket message:`, message);
                    
                    // Dispatch event for components to listen to
                    const customEvent = new CustomEvent('prometheus-update', { detail: message });
                    document.dispatchEvent(customEvent);
                } catch (error) {
                    console.error(`${this.debugPrefix} Error processing WebSocket message:`, error);
                }
            };
        } catch (error) {
            console.error(`${this.debugPrefix} Error initializing WebSocket:`, error);
        }
    }

    /**
     * Make an API request with error handling
     */
    async request(endpoint, method = 'GET', data = null) {
        const url = endpoint.startsWith('http') ? endpoint : `${this.apiBaseUrl}/${endpoint}`;
        
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        
        // Add authorization if token exists
        if (this.token) {
            options.headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        // Add body data for non-GET requests
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
        
        try {
            console.log(`${this.debugPrefix} ${method} request to ${url}`);
            
            const response = await fetch(url, options);
            
            // Check for errors
            if (!response.ok) {
                const errorBody = await response.json().catch(() => ({}));
                throw new Error(errorBody.message || `API request failed: ${response.status} ${response.statusText}`);
            }
            
            // Parse JSON response
            const responseData = await response.json();
            return responseData;
        } catch (error) {
            console.error(`${this.debugPrefix} Request error:`, error);
            throw error;
        }
    }

    /**
     * Get API health status
     */
    async getHealth() {
        return this.request('health');
    }

    /**
     * Get all projects
     */
    async getProjects() {
        return this.request('plans');
    }

    /**
     * Get a specific project by ID
     */
    async getProject(projectId) {
        return this.request(`plans/${projectId}`);
    }

    /**
     * Create a new project
     */
    async createProject(projectData) {
        return this.request('plans', 'POST', projectData);
    }

    /**
     * Update an existing project
     */
    async updateProject(projectId, projectData) {
        return this.request(`plans/${projectId}`, 'PUT', projectData);
    }

    /**
     * Delete a project
     */
    async deleteProject(projectId) {
        return this.request(`plans/${projectId}`, 'DELETE');
    }

    /**
     * Get tasks for a project
     */
    async getTasks(projectId) {
        return this.request(`plans/${projectId}/tasks`);
    }

    /**
     * Get a specific task in a project
     */
    async getTask(projectId, taskId) {
        return this.request(`plans/${projectId}/tasks/${taskId}`);
    }

    /**
     * Create a new task in a project
     */
    async createTask(projectId, taskData) {
        return this.request(`plans/${projectId}/tasks`, 'POST', taskData);
    }

    /**
     * Update an existing task
     */
    async updateTask(projectId, taskId, taskData) {
        return this.request(`plans/${projectId}/tasks/${taskId}`, 'PUT', taskData);
    }

    /**
     * Delete a task
     */
    async deleteTask(projectId, taskId) {
        return this.request(`plans/${projectId}/tasks/${taskId}`, 'DELETE');
    }

    /**
     * Get resources
     */
    async getResources() {
        return this.request('resources');
    }

    /**
     * Get a specific resource
     */
    async getResource(resourceId) {
        return this.request(`resources/${resourceId}`);
    }

    /**
     * Create a new resource
     */
    async createResource(resourceData) {
        return this.request('resources', 'POST', resourceData);
    }

    /**
     * Update an existing resource
     */
    async updateResource(resourceId, resourceData) {
        return this.request(`resources/${resourceId}`, 'PUT', resourceData);
    }

    /**
     * Delete a resource
     */
    async deleteResource(resourceId) {
        return this.request(`resources/${resourceId}`, 'DELETE');
    }

    /**
     * Run a project analysis
     */
    async runAnalysis(projectId, analysisType, options = {}) {
        const endpoint = `plans/${projectId}/analysis`;
        
        const requestData = {
            analysis_type: analysisType,
            options
        };
        
        return this.request(endpoint, 'POST', requestData);
    }

    /**
     * Get critical path for a project
     */
    async getCriticalPath(projectId) {
        return this.request(`plans/${projectId}/critical-path`);
    }

    /**
     * Generate timeline for a project
     */
    async generateTimeline(projectId, options = {}) {
        const endpoint = `plans/${projectId}/timeline`;
        
        // If options provided, send as POST request with options
        if (Object.keys(options).length > 0) {
            return this.request(endpoint, 'POST', options);
        }
        
        // Otherwise use GET request
        return this.request(endpoint);
    }

    /**
     * Generate performance metrics for a project
     */
    async generatePerformanceMetrics(projectId) {
        return this.request(`plans/${projectId}/performance-metrics`);
    }

    /**
     * Generate risk assessment for a project
     */
    async generateRiskAssessment(projectId) {
        return this.request(`plans/${projectId}/risk-assessment`);
    }

    /**
     * Generate resource allocation for a project
     */
    async generateResourceAllocation(projectId) {
        return this.request(`plans/${projectId}/resource-allocation`);
    }

    /**
     * Get project dependencies
     */
    async getProjectDependencies(projectId) {
        return this.request(`plans/${projectId}/dependencies`);
    }

    /**
     * Add a dependency between projects
     */
    async addProjectDependency(projectId, dependencyData) {
        return this.request(`plans/${projectId}/dependencies`, 'POST', dependencyData);
    }

    /**
     * Remove a dependency between projects
     */
    async removeProjectDependency(projectId, dependencyId) {
        return this.request(`plans/${projectId}/dependencies/${dependencyId}`, 'DELETE');
    }

    /**
     * Get retrospectives for a project
     */
    async getRetrospectives(projectId) {
        return this.request(`retrospectives?plan_id=${projectId}`);
    }

    /**
     * Get a specific retrospective
     */
    async getRetrospective(retroId) {
        return this.request(`retrospectives/${retroId}`);
    }

    /**
     * Create a new retrospective
     */
    async createRetrospective(retroData) {
        return this.request('retrospectives', 'POST', retroData);
    }

    /**
     * Add feedback to a retrospective
     */
    async addRetrospectiveFeedback(retroId, feedbackData) {
        return this.request(`retrospectives/${retroId}/feedback`, 'POST', feedbackData);
    }

    /**
     * Generate improvement suggestions for a retrospective
     */
    async generateImprovementSuggestions(retroId) {
        return this.request(`retrospectives/${retroId}/improvement-suggestions`);
    }

    /**
     * Send chat message and get response
     */
    async sendChat(message, isTeamChat = false) {
        const endpoint = isTeamChat ? 'chat/team' : 'chat/planning';
        
        const requestData = {
            message
        };
        
        return this.request(endpoint, 'POST', requestData);
    }

    /**
     * Stream chat response (uses WebSocket)
     */
    async streamChat(message, isTeamChat = false) {
        if (!this.isConnected) {
            throw new Error('WebSocket connection not established');
        }
        
        const requestId = Math.random().toString(36).substring(2, 15);
        
        const request = {
            id: requestId,
            type: isTeamChat ? 'team_chat' : 'planning_chat',
            message
        };
        
        return new Promise((resolve, reject) => {
            try {
                // Set up one-time event listener for this request
                const listener = (event) => {
                    const response = event.detail;
                    
                    if (response.id === requestId) {
                        document.removeEventListener('prometheus-update', listener);
                        resolve(response);
                    }
                };
                
                document.addEventListener('prometheus-update', listener);
                
                // Send request via WebSocket
                this.ws.send(JSON.stringify(request));
                
                // Set timeout to avoid hanging forever
                setTimeout(() => {
                    document.removeEventListener('prometheus-update', listener);
                    reject(new Error('Chat response timeout'));
                }, 30000);
            } catch (error) {
                reject(error);
            }
        });
    }
}

// Make available globally
window.PrometheusService = PrometheusService;