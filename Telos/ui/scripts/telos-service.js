/**
 * Telos Service
 * 
 * Provides a service layer for interacting with the Telos API,
 * following the Tekton State Management Pattern.
 */

class TelosService {
  constructor() {
    // Initialize environment
    this.apiBaseUrl = this.getApiUrl();
    
    // Initialize state
    this.stateManager = null;
    this.telosReady = false;
    
    // WebSocket connection
    this.websocket = null;
    this.websocketReconnectAttempts = 0;
    this.websocketMaxReconnectAttempts = 5;
    
    // Bind methods
    this.initialize = this.initialize.bind(this);
    this.getApiUrl = this.getApiUrl.bind(this);
    this.setupWebSocket = this.setupWebSocket.bind(this);
    this.handleWebSocketMessage = this.handleWebSocketMessage.bind(this);
    this.reconnectWebSocket = this.reconnectWebSocket.bind(this);
    this.fetchProjects = this.fetchProjects.bind(this);
    this.fetchRequirements = this.fetchRequirements.bind(this);
    this.fetchRequirementDetails = this.fetchRequirementDetails.bind(this);
    this.fetchTraces = this.fetchTraces.bind(this);
    this.createProject = this.createProject.bind(this);
    this.updateProject = this.updateProject.bind(this);
    this.deleteProject = this.deleteProject.bind(this);
    this.createRequirement = this.createRequirement.bind(this);
    this.updateRequirement = this.updateRequirement.bind(this);
    this.deleteRequirement = this.deleteRequirement.bind(this);
    this.validateRequirement = this.validateRequirement.bind(this);
    this.refineRequirement = this.refineRequirement.bind(this);
    this.createTrace = this.createTrace.bind(this);
    this.updateTrace = this.updateTrace.bind(this);
    this.deleteTrace = this.deleteTrace.bind(this);
    this.exportProject = this.exportProject.bind(this);
    this.importProject = this.importProject.bind(this);
  }
  
  /**
   * Initialize the service
   * @param {Object} stateManager - State manager instance
   */
  initialize(stateManager) {
    this.stateManager = stateManager;
    
    // Register service state
    this.stateManager.registerState('telos', {
      ready: false,
      connected: false,
      loading: {
        projects: false,
        requirements: false,
        requirement: false,
        traces: false
      },
      error: null
    });
    
    // Set up WebSocket connection
    this.setupWebSocket();
    
    // Mark service as ready
    this.telosReady = true;
    this.stateManager.updateState('telos', { ready: true });
    
    return true;
  }
  
  /**
   * Get API URL from environment variables
   */
  getApiUrl() {
    // Try to get URL from environment
    const telosPort = window.TELOS_PORT || '8008';
    return `http://localhost:${telosPort}/api`;
  }
  
  /**
   * Set up WebSocket connection
   */
  setupWebSocket() {
    try {
      const telosPort = window.TELOS_PORT || '8008';
      const wsUrl = `ws://localhost:${telosPort}/ws`;
      
      // Close existing connection if any
      if (this.websocket) {
        this.websocket.close();
      }
      
      this.websocket = new WebSocket(wsUrl);
      
      // Set up event handlers
      this.websocket.onopen = () => {
        console.log('WebSocket connection established');
        this.stateManager.updateState('telos', { connected: true });
        this.websocketReconnectAttempts = 0;
        
        // Register with the server
        this.websocket.send(JSON.stringify({
          type: 'REGISTER',
          source: 'UI',
          timestamp: Date.now(),
          payload: {
            client_type: 'hephaestus-ui',
            client_id: `telos-ui-${Date.now()}`
          }
        }));
      };
      
      this.websocket.onmessage = (event) => {
        this.handleWebSocketMessage(event);
      };
      
      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.stateManager.updateState('telos', { connected: false });
      };
      
      this.websocket.onclose = () => {
        console.log('WebSocket connection closed');
        this.stateManager.updateState('telos', { connected: false });
        
        // Try to reconnect
        this.reconnectWebSocket();
      };
      
    } catch (error) {
      console.error('Error setting up WebSocket:', error);
      this.stateManager.updateState('telos', { connected: false });
    }
  }
  
  /**
   * Handle WebSocket messages
   */
  handleWebSocketMessage(event) {
    try {
      const message = JSON.parse(event.data);
      
      // Handle different message types
      switch (message.type) {
        case 'WELCOME':
          console.log('WebSocket server welcomed us:', message.payload.message);
          break;
          
        case 'RESPONSE':
          // Handle responses to specific requests
          console.log('WebSocket response:', message);
          break;
          
        case 'UPDATE':
          // Handle real-time updates
          if (message.payload.type === 'project_update') {
            // Refresh projects
            this.fetchProjects();
          } else if (message.payload.type === 'requirement_update') {
            // Refresh requirements if we're looking at this project
            const currentProject = this.stateManager.getState('projects.selectedProject');
            if (currentProject && currentProject.project_id === message.payload.project_id) {
              this.fetchRequirements(currentProject.project_id);
            }
          }
          break;
          
        case 'ERROR':
          console.error('WebSocket error message:', message.payload.error);
          break;
          
        default:
          console.log('Unknown WebSocket message type:', message.type);
      }
    } catch (error) {
      console.error('Error processing WebSocket message:', error);
    }
  }
  
  /**
   * Attempt to reconnect WebSocket
   */
  reconnectWebSocket() {
    if (this.websocketReconnectAttempts >= this.websocketMaxReconnectAttempts) {
      console.log('Maximum WebSocket reconnect attempts reached');
      return;
    }
    
    this.websocketReconnectAttempts++;
    
    // Exponential backoff
    const delay = Math.min(1000 * Math.pow(2, this.websocketReconnectAttempts), 30000);
    
    console.log(`Attempting to reconnect WebSocket in ${delay}ms (attempt ${this.websocketReconnectAttempts})`);
    
    setTimeout(() => {
      this.setupWebSocket();
    }, delay);
  }
  
  /**
   * Fetch projects
   */
  async fetchProjects() {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    try {
      // Update loading state
      this.stateManager.updateState('telos', { loading: { projects: true } });
      
      // Fetch projects
      const response = await fetch(`${this.apiBaseUrl}/projects`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch projects: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update state
      this.stateManager.updateState('telos', { 
        loading: { projects: false },
        error: null
      });
      
      // Update projects in the application state
      this.stateManager.updateState('projects', {
        list: data.projects || [],
        loaded: true
      });
      
      return { success: true, data };
    } catch (error) {
      console.error('Error fetching projects:', error);
      
      // Update state
      this.stateManager.updateState('telos', { 
        loading: { projects: false },
        error: `Failed to load projects: ${error.message}`
      });
      
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Fetch requirements for a project
   */
  async fetchRequirements(projectId) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId) {
      return { success: false, error: 'Project ID is required' };
    }
    
    try {
      // Update loading state
      this.stateManager.updateState('telos', { loading: { requirements: true } });
      
      // Fetch requirements
      const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}/requirements`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch requirements: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update state
      this.stateManager.updateState('telos', { 
        loading: { requirements: false },
        error: null
      });
      
      // Update requirements in the application state
      this.stateManager.updateState('requirements', {
        list: data.requirements || [],
        loaded: true,
        projectId
      });
      
      return { success: true, data };
    } catch (error) {
      console.error('Error fetching requirements:', error);
      
      // Update state
      this.stateManager.updateState('telos', { 
        loading: { requirements: false },
        error: `Failed to load requirements: ${error.message}`
      });
      
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Fetch requirement details
   */
  async fetchRequirementDetails(projectId, requirementId) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId || !requirementId) {
      return { success: false, error: 'Project ID and Requirement ID are required' };
    }
    
    try {
      // Update loading state
      this.stateManager.updateState('telos', { loading: { requirement: true } });
      
      // Fetch requirement details
      const response = await fetch(
        `${this.apiBaseUrl}/projects/${projectId}/requirements/${requirementId}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch requirement: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update state
      this.stateManager.updateState('telos', { 
        loading: { requirement: false },
        error: null
      });
      
      // Update selected requirement in the application state
      this.stateManager.updateState('requirements', {
        selected: data
      });
      
      return { success: true, data };
    } catch (error) {
      console.error('Error fetching requirement details:', error);
      
      // Update state
      this.stateManager.updateState('telos', { 
        loading: { requirement: false },
        error: `Failed to load requirement details: ${error.message}`
      });
      
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Fetch traces
   */
  async fetchTraces(projectId, requirementId = null) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId) {
      return { success: false, error: 'Project ID is required' };
    }
    
    try {
      // Update loading state
      this.stateManager.updateState('telos', { loading: { traces: true } });
      
      // Build URL
      let url = `${this.apiBaseUrl}/projects/${projectId}/traces`;
      if (requirementId) {
        url += `?requirement_id=${requirementId}`;
      }
      
      // Fetch traces
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch traces: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update state
      this.stateManager.updateState('telos', { 
        loading: { traces: false },
        error: null
      });
      
      // Update traces in the application state
      this.stateManager.updateState('traces', {
        list: data.traces || [],
        loaded: true,
        projectId,
        requirementId
      });
      
      return { success: true, data };
    } catch (error) {
      console.error('Error fetching traces:', error);
      
      // Update state
      this.stateManager.updateState('telos', { 
        loading: { traces: false },
        error: `Failed to load traces: ${error.message}`
      });
      
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Create a new project
   */
  async createProject(name, description = '', metadata = null) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!name) {
      return { success: false, error: 'Project name is required' };
    }
    
    try {
      // Create project
      const response = await fetch(`${this.apiBaseUrl}/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name,
          description,
          metadata
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create project: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Refresh projects
      this.fetchProjects();
      
      return { success: true, data };
    } catch (error) {
      console.error('Error creating project:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Update a project
   */
  async updateProject(projectId, updates) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId) {
      return { success: false, error: 'Project ID is required' };
    }
    
    try {
      // Update project
      const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });
      
      if (!response.ok) {
        throw new Error(`Failed to update project: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Refresh projects
      this.fetchProjects();
      
      return { success: true, data };
    } catch (error) {
      console.error('Error updating project:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Delete a project
   */
  async deleteProject(projectId) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId) {
      return { success: false, error: 'Project ID is required' };
    }
    
    try {
      // Delete project
      const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error(`Failed to delete project: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Refresh projects
      this.fetchProjects();
      
      return { success: true, data };
    } catch (error) {
      console.error('Error deleting project:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Create a new requirement
   */
  async createRequirement(projectId, requirement) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId) {
      return { success: false, error: 'Project ID is required' };
    }
    
    if (!requirement?.title || !requirement?.description) {
      return { success: false, error: 'Requirement title and description are required' };
    }
    
    try {
      // Create requirement
      const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}/requirements`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requirement)
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create requirement: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Refresh requirements for this project
      this.fetchRequirements(projectId);
      
      return { success: true, data };
    } catch (error) {
      console.error('Error creating requirement:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Update a requirement
   */
  async updateRequirement(projectId, requirementId, updates) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId || !requirementId) {
      return { success: false, error: 'Project ID and Requirement ID are required' };
    }
    
    try {
      // Update requirement
      const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}/requirements/${requirementId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });
      
      if (!response.ok) {
        throw new Error(`Failed to update requirement: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Refresh requirements
      this.fetchRequirements(projectId);
      
      // If this is the currently selected requirement, refresh its details
      const selectedRequirement = this.stateManager.getState('requirements.selected');
      if (selectedRequirement && selectedRequirement.requirement_id === requirementId) {
        this.fetchRequirementDetails(projectId, requirementId);
      }
      
      return { success: true, data };
    } catch (error) {
      console.error('Error updating requirement:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Delete a requirement
   */
  async deleteRequirement(projectId, requirementId) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId || !requirementId) {
      return { success: false, error: 'Project ID and Requirement ID are required' };
    }
    
    try {
      // Delete requirement
      const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}/requirements/${requirementId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error(`Failed to delete requirement: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Refresh requirements
      this.fetchRequirements(projectId);
      
      return { success: true, data };
    } catch (error) {
      console.error('Error deleting requirement:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Validate a requirement
   */
  async validateRequirement(projectId, requirementId, criteria = {}) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId || !requirementId) {
      return { success: false, error: 'Project ID and Requirement ID are required' };
    }
    
    try {
      // Validate requirement
      const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}/requirements/${requirementId}/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ criteria })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to validate requirement: ${response.status}`);
      }
      
      const data = await response.json();
      
      return { success: true, data };
    } catch (error) {
      console.error('Error validating requirement:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Refine a requirement
   */
  async refineRequirement(projectId, requirementId, feedback, autoUpdate = false) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId || !requirementId) {
      return { success: false, error: 'Project ID and Requirement ID are required' };
    }
    
    if (!feedback) {
      return { success: false, error: 'Feedback is required' };
    }
    
    try {
      // Refine requirement
      const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}/requirements/${requirementId}/refine`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          feedback,
          auto_update: autoUpdate
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to refine requirement: ${response.status}`);
      }
      
      const data = await response.json();
      
      // If auto-update was enabled, refresh the requirement
      if (autoUpdate) {
        this.fetchRequirementDetails(projectId, requirementId);
      }
      
      return { success: true, data };
    } catch (error) {
      console.error('Error refining requirement:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Create a trace
   */
  async createTrace(projectId, sourceId, targetId, traceType, description = '') {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId || !sourceId || !targetId) {
      return { success: false, error: 'Project ID, Source ID, and Target ID are required' };
    }
    
    if (!traceType) {
      return { success: false, error: 'Trace type is required' };
    }
    
    try {
      // Create trace
      const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}/traces`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          source_id: sourceId,
          target_id: targetId,
          trace_type: traceType,
          description
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create trace: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Refresh traces
      this.fetchTraces(projectId);
      
      return { success: true, data };
    } catch (error) {
      console.error('Error creating trace:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Update a trace
   */
  async updateTrace(projectId, traceId, updates) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId || !traceId) {
      return { success: false, error: 'Project ID and Trace ID are required' };
    }
    
    try {
      // Update trace
      const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}/traces/${traceId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });
      
      if (!response.ok) {
        throw new Error(`Failed to update trace: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Refresh traces
      this.fetchTraces(projectId);
      
      return { success: true, data };
    } catch (error) {
      console.error('Error updating trace:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Delete a trace
   */
  async deleteTrace(projectId, traceId) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId || !traceId) {
      return { success: false, error: 'Project ID and Trace ID are required' };
    }
    
    try {
      // Delete trace
      const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}/traces/${traceId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error(`Failed to delete trace: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Refresh traces
      this.fetchTraces(projectId);
      
      return { success: true, data };
    } catch (error) {
      console.error('Error deleting trace:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Export a project
   */
  async exportProject(projectId, format = 'json', sections = null) {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!projectId) {
      return { success: false, error: 'Project ID is required' };
    }
    
    try {
      // Export project
      const response = await fetch(`${this.apiBaseUrl}/projects/${projectId}/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          format,
          sections
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to export project: ${response.status}`);
      }
      
      const data = await response.json();
      
      return { success: true, data };
    } catch (error) {
      console.error('Error exporting project:', error);
      return { success: false, error: error.message };
    }
  }
  
  /**
   * Import a project
   */
  async importProject(data, format = 'json', mergeStrategy = 'replace') {
    if (!this.telosReady) {
      return { success: false, error: 'Service not initialized' };
    }
    
    if (!data) {
      return { success: false, error: 'Import data is required' };
    }
    
    try {
      // Import project
      const response = await fetch(`${this.apiBaseUrl}/projects/import`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          data,
          format,
          merge_strategy: mergeStrategy
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to import project: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Refresh projects
      this.fetchProjects();
      
      return { success: true, data: result };
    } catch (error) {
      console.error('Error importing project:', error);
      return { success: false, error: error.message };
    }
  }
}

// Export the class
export default TelosService;