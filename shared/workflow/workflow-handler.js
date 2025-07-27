/**
 * Workflow Handler for Tekton Components
 * 
 * Implements the client-side workflow standard for component communication.
 * Uses CSS-first approach with minimal JavaScript and no DOM manipulation.
 */

/**
 * Build URL for any Tekton component with smart host resolution.
 * This is a client-side implementation matching the Python tekton_url function.
 * 
 * @param {string} component - Component name (e.g., "hermes", "athena", "ui-devtools")
 * @param {string} path - URL path to append (e.g., "/api/mcp/v2")
 * @param {object} options - Optional parameters {host, scheme}
 * @returns {string} Complete URL string
 */
window.tektonUrl = function(component, path = "", options = {}) {
  const { host, scheme = "http" } = options;
  
  // Normalize component name for environment lookup
  const envComponent = component.replace(/-/g, '_').toUpperCase();
  
  // Host resolution with proper precedence
  let resolvedHost = host;
  if (!resolvedHost) {
    // Check component-specific host first
    const componentHost = window[`${envComponent}_HOST`];
    if (componentHost) {
      resolvedHost = componentHost;
    } else {
      // Fall back to global TEKTON_HOST or localhost
      resolvedHost = window.TEKTON_HOST || 'localhost';
    }
  }
  
  // Get port from environment
  const port = window[`${envComponent}_PORT`] || window.TEKTON_ROOT ? getDefaultPort(component) : '8000';
  
  return `${scheme}://${resolvedHost}:${port}${path}`;
  
  function getDefaultPort(comp) {
    const ports = {
      'telos': '8011',
      'prometheus': '8012',
      'metis': '8013',
      'harmonia': '8014',
      'synthesis': '8015',
      'tekton': '8080',
      'tekton-core': '8080',
      'hermes': '8000'
    };
    return ports[comp] || '8000';
  }
};

class WorkflowHandler {
  constructor(componentName) {
    this.componentName = componentName;
    this.baseUrl = this._getComponentUrl();
    this.dataThreshold = 10 * 1024; // 10KB threshold
  }
  
  /**
   * Get component base URL using tektonUrl function
   */
  _getComponentUrl() {
    // Use tektonUrl function if available
    if (window.tektonUrl) {
      return window.tektonUrl(this.componentName);
    }
    
    // Fallback to environment variables
    const envComponent = this.componentName.replace(/-/g, '_').toUpperCase();
    const host = window[`${envComponent}_HOST`] || window.TEKTON_HOST || 'localhost';
    const port = window[`${envComponent}_PORT`] || this._getDefaultPort();
    
    return `http://${host}:${port}`;
  }
  
  /**
   * Get default port for component
   */
  _getDefaultPort() {
    const ports = {
      'telos': window.TELOS_PORT || '8011',
      'prometheus': window.PROMETHEUS_PORT || '8012',
      'metis': window.METIS_PORT || '8013',
      'harmonia': window.HARMONIA_PORT || '8014',
      'synthesis': window.SYNTHESIS_PORT || '8015',
      'tekton': window.TEKTONCORE_PORT || '8080',
      'hermes': window.HERMES_PORT || '8000'
    };
    
    return ports[this.componentName] || '8000';
  }
  
  /**
   * Send workflow message to a component
   * 
   * @param {string} dest - Target component name
   * @param {string} purpose - Human-readable purpose
   * @param {object} payload - Action payload
   * @returns {Promise<object>} Response from component
   */
  async sendWorkflow(dest, purpose, payload) {
    const message = {
      purpose: {[dest]: purpose},
      dest: dest,
      payload: payload
    };
    
    try {
      const response = await fetch(`${this.baseUrl}/workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(message)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`[WorkflowHandler] Error sending to ${dest}:`, error);
      throw error;
    }
  }
  
  /**
   * Check for pending work
   * 
   * @returns {Promise<object>} Work items found
   */
  async lookForWork() {
    return this.sendWorkflow(
      this.componentName,
      "Check for pending work",
      {action: "look_for_work"}
    );
  }
  
  /**
   * Process a sprint
   * 
   * @param {string} sprintName - Name of sprint to process
   * @param {string} status - Current sprint status
   * @returns {Promise<object>} Processing result
   */
  async processSprint(sprintName, status) {
    return this.sendWorkflow(
      this.componentName,
      `Process sprint at ${status}`,
      {
        action: "process_sprint",
        sprint_name: sprintName,
        status: status
      }
    );
  }
  
  /**
   * Update sprint status
   * 
   * @param {string} sprintName - Sprint to update
   * @param {string} oldStatus - Previous status
   * @param {string} newStatus - New status
   * @returns {Promise<object>} Update result
   */
  async updateStatus(sprintName, oldStatus, newStatus) {
    return this.sendWorkflow(
      this.componentName,
      "Update sprint status",
      {
        action: "update_status",
        sprint_name: sprintName,
        old_status: oldStatus,
        new_status: newStatus
      }
    );
  }
  
  /**
   * Generate workflow ID
   * 
   * @param {string} sprintName - Sprint name
   * @returns {string} Workflow ID
   */
  generateWorkflowId(sprintName) {
    const timestamp = new Date().toISOString().replace(/[-:T.]/g, '_').slice(0, -5);
    const cleanName = sprintName.replace(/_Sprint$/, '').toLowerCase().replace(/\s+/g, '_');
    return `${cleanName}_${timestamp}`;
  }
  
  /**
   * Prepare data payload based on size
   * 
   * @param {any} data - Data to prepare
   * @returns {object} Data payload
   */
  prepareDataPayload(data) {
    const dataStr = JSON.stringify(data);
    const sizeBytes = new Blob([dataStr]).size;
    
    if (sizeBytes < this.dataThreshold) {
      return {
        type: "embedded",
        content: data
      };
    } else {
      return {
        type: "reference",
        size_bytes: sizeBytes,
        content: data // Caller will handle saving
      };
    }
  }
  
  /**
   * Notify next component in pipeline
   * 
   * @param {string} nextComponent - Target component
   * @param {string} sprintName - Sprint name
   * @param {string} newStatus - New sprint status
   * @param {object} data - Data to pass
   * @param {string} workflowId - Optional workflow ID
   * @returns {Promise<object>} Response from next component
   */
  async notifyNextComponent(nextComponent, sprintName, newStatus, data, workflowId = null) {
    // Generate workflow ID if not provided
    if (!workflowId) {
      workflowId = this.generateWorkflowId(sprintName);
    }
    
    // Prepare data payload
    let dataPayload = this.prepareDataPayload(data);
    
    // If data needs reference, we need to save it first
    // In browser context, we'll let the backend handle this
    if (dataPayload.type === "reference") {
      // First export the data
      const exportResult = await this.sendWorkflow(
        this.componentName,
        "Export workflow data",
        {
          action: "export_data",
          sprint_name: sprintName,
          workflow_id: workflowId,
          data: data
        }
      );
      
      if (exportResult.status === "success") {
        dataPayload = {
          type: "reference",
          workflow_id: exportResult.workflow_id,
          path: `${this.componentName}_output`
        };
      }
    }
    
    // Update status
    await this.updateStatus(sprintName, `Processing:${this.componentName}`, newStatus);
    
    const message = {
      purpose: {[nextComponent]: `Process ${this.componentName} output for ${sprintName}`},
      dest: nextComponent,
      payload: {
        action: "process_sprint",
        sprint_name: sprintName,
        status: newStatus,
        from_component: this.componentName,
        workflow_id: workflowId,
        data: dataPayload
      }
    };
    
    // Build the full URL for the workflow endpoint
    const nextUrl = this._getComponentUrl(nextComponent);
    const workflowUrl = `${nextUrl}/workflow`;
    
    try {
      const response = await fetch(workflowUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(message)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`[WorkflowHandler] Error notifying ${nextComponent}:`, error);
      throw error;
    }
  }
  
  /**
   * Helper to get URL for another component
   */
  _getComponentUrl(componentName) {
    if (!componentName) return this.baseUrl;
    
    // Use tektonUrl function if available
    if (window.tektonUrl) {
      return window.tektonUrl(componentName);
    }
    
    // Fallback to environment variables
    const envComponent = componentName.replace(/-/g, '_').toUpperCase();
    const host = window[`${envComponent}_HOST`] || window.TEKTON_HOST || 'localhost';
    const port = window[`${envComponent}_PORT`] || this._getDefaultPortForComponent(componentName);
    
    return `http://${host}:${port}`;
  }
  
  /**
   * Get default port for a specific component
   */
  _getDefaultPortForComponent(componentName) {
    const ports = {
      'telos': window.TELOS_PORT || '8011',
      'prometheus': window.PROMETHEUS_PORT || '8012',
      'metis': window.METIS_PORT || '8013',
      'harmonia': window.HARMONIA_PORT || '8014',
      'synthesis': window.SYNTHESIS_PORT || '8015',
      'tekton': window.TEKTONCORE_PORT || '8080',
      'hermes': window.HERMES_PORT || '8000'
    };
    
    return ports[componentName] || '8000';
  }
}

/**
 * Component-specific workflow handler example
 * 
 * Each component should extend this pattern:
 */
class TelosWorkflowHandler extends WorkflowHandler {
  constructor() {
    super('telos');
  }
  
  /**
   * Check for new proposals or work items
   */
  async checkForProposals() {
    const result = await this.lookForWork();
    
    if (result.status === 'success' && result.proposals) {
      // Update UI with CSS classes (no DOM manipulation)
      const dashboard = document.querySelector('.telos__dashboard');
      if (dashboard && result.proposals.length > 0) {
        dashboard.classList.add('has-proposals');
        dashboard.dataset.proposalCount = result.proposals.length;
      }
    }
    
    return result;
  }
  
  /**
   * Convert proposal to sprint and notify Prometheus
   */
  async createSprint(proposalName) {
    // First create the sprint
    const createResult = await this.sendWorkflow(
      'telos',
      'Create sprint from proposal',
      {
        action: 'create_sprint',
        proposal_name: proposalName
      }
    );
    
    if (createResult.status === 'success') {
      // Notify Prometheus
      await this.notifyNextComponent(
        'prometheus',
        createResult.sprint_name,
        {
          proposal: proposalName,
          created_at: new Date().toISOString()
        }
      );
    }
    
    return createResult;
  }
}

// Export for use in components
window.WorkflowHandler = WorkflowHandler;

// Convenience function for navigation integration
window.triggerWorkflowCheck = async function(componentName) {
  if (!componentName) return;
  
  const workflowComponents = [
    'telos', 'prometheus', 'metis', 
    'harmonia', 'synthesis', 'tekton'
  ];
  
  if (!workflowComponents.includes(componentName)) {
    console.log(`[Workflow] ${componentName} does not support workflow`);
    return;
  }
  
  try {
    const handler = new WorkflowHandler(componentName);
    const result = await handler.lookForWork();
    
    console.log(`[Workflow] ${componentName} check result:`, result);
    
    // Let component handle UI updates via CSS
    if (result.status === 'success' && result.found > 0) {
      const event = new CustomEvent('workflow:work-found', {
        detail: {
          component: componentName,
          count: result.found,
          items: result.items
        }
      });
      document.dispatchEvent(event);
    }
  } catch (error) {
    console.error(`[Workflow] Error checking ${componentName}:`, error);
  }
};