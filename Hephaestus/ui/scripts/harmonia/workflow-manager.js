/**
 * Workflow Manager
 * 
 * Manages workflow operations and state for the Harmonia component
 */

// Debug instrumentation
if (window.debugShim) {
    window.debugShim.registerModule('workflow-manager', {
        description: 'Workflow Manager - Workflow Operations',
        version: '1.0.0'
    });
}

/**
 * Workflow Manager class
 */
class WorkflowManager {
    /**
     * Constructor
     * @param {Object} service - The Harmonia service instance
     */
    constructor(service) {
        this.debugLog('[WORKFLOW-MANAGER] Constructing workflow manager');
        
        // Store service reference
        this.service = service;
        
        // Initialize state
        this.state = {
            workflows: [],
            templates: [],
            executions: [],
            activeExecution: null,
            activeWorkflow: null,
            activeTemplate: null,
            loading: {
                workflows: false,
                templates: false,
                executions: false
            }
        };
        
        this.debugLog('[WORKFLOW-MANAGER] Workflow manager constructed');
    }
    
    /**
     * Load workflows from service
     * @returns {Promise<Array>} - The loaded workflows
     */
    async loadWorkflows() {
        this.debugLog('[WORKFLOW-MANAGER] Loading workflows');
        
        try {
            // Update loading state
            this.state.loading.workflows = true;
            
            // Get workflows from service
            const workflows = await this.service.getWorkflows();
            this.state.workflows = workflows;
            
            this.debugLog('[WORKFLOW-MANAGER] Workflows loaded:', workflows.length);
            
            return workflows;
        } catch (error) {
            this.debugLog('[WORKFLOW-MANAGER] Error loading workflows', error);
            return [];
        } finally {
            // Update loading state
            this.state.loading.workflows = false;
        }
    }
    
    /**
     * Load a workflow by ID
     * @param {string} id - The workflow ID
     * @returns {Promise<Object>} - The loaded workflow
     */
    async loadWorkflow(id) {
        this.debugLog(`[WORKFLOW-MANAGER] Loading workflow ${id}`);
        
        try {
            // Get workflow from service
            const workflow = await this.service.getWorkflow(id);
            
            // Store as active workflow
            this.state.activeWorkflow = workflow;
            
            this.debugLog(`[WORKFLOW-MANAGER] Workflow ${id} loaded`);
            
            return workflow;
        } catch (error) {
            this.debugLog(`[WORKFLOW-MANAGER] Error loading workflow ${id}`, error);
            return null;
        }
    }
    
    /**
     * Create a new workflow
     * @param {Object} workflow - The workflow to create
     * @returns {Promise<Object>} - The created workflow
     */
    async createWorkflow(workflow) {
        this.debugLog('[WORKFLOW-MANAGER] Creating workflow');
        
        try {
            // Create workflow via service
            const createdWorkflow = await this.service.createWorkflow(workflow);
            
            // Add to workflows list
            if (createdWorkflow) {
                this.state.workflows.push(createdWorkflow);
            }
            
            this.debugLog('[WORKFLOW-MANAGER] Workflow created');
            
            return createdWorkflow;
        } catch (error) {
            this.debugLog('[WORKFLOW-MANAGER] Error creating workflow', error);
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
        this.debugLog(`[WORKFLOW-MANAGER] Updating workflow ${id}`);
        
        try {
            // Update workflow via service
            const updatedWorkflow = await this.service.updateWorkflow(id, workflow);
            
            // Update in workflows list
            if (updatedWorkflow) {
                const index = this.state.workflows.findIndex(w => w.id === id);
                if (index !== -1) {
                    this.state.workflows[index] = updatedWorkflow;
                }
                
                // Update active workflow if it's the same
                if (this.state.activeWorkflow && this.state.activeWorkflow.id === id) {
                    this.state.activeWorkflow = updatedWorkflow;
                }
            }
            
            this.debugLog(`[WORKFLOW-MANAGER] Workflow ${id} updated`);
            
            return updatedWorkflow;
        } catch (error) {
            this.debugLog(`[WORKFLOW-MANAGER] Error updating workflow ${id}`, error);
            return null;
        }
    }
    
    /**
     * Delete a workflow
     * @param {string} id - The workflow ID
     * @returns {Promise<boolean>} - Whether the deletion was successful
     */
    async deleteWorkflow(id) {
        this.debugLog(`[WORKFLOW-MANAGER] Deleting workflow ${id}`);
        
        try {
            // Delete workflow via service
            const success = await this.service.deleteWorkflow(id);
            
            // Remove from workflows list
            if (success) {
                this.state.workflows = this.state.workflows.filter(w => w.id !== id);
                
                // Clear active workflow if it's the same
                if (this.state.activeWorkflow && this.state.activeWorkflow.id === id) {
                    this.state.activeWorkflow = null;
                }
            }
            
            this.debugLog(`[WORKFLOW-MANAGER] Workflow ${id} deleted: ${success}`);
            
            return success;
        } catch (error) {
            this.debugLog(`[WORKFLOW-MANAGER] Error deleting workflow ${id}`, error);
            return false;
        }
    }
    
    /**
     * Execute a workflow
     * @param {string} id - The workflow ID
     * @returns {Promise<Object>} - The execution
     */
    async executeWorkflow(id) {
        this.debugLog(`[WORKFLOW-MANAGER] Executing workflow ${id}`);
        
        try {
            // Execute workflow via service
            const execution = await this.service.executeWorkflow(id);
            
            // Add to executions list
            if (execution) {
                this.state.executions.push(execution);
                this.state.activeExecution = execution;
            }
            
            this.debugLog(`[WORKFLOW-MANAGER] Workflow ${id} executed`);
            
            return execution;
        } catch (error) {
            this.debugLog(`[WORKFLOW-MANAGER] Error executing workflow ${id}`, error);
            return null;
        }
    }
    
    /**
     * Load templates from service
     * @returns {Promise<Array>} - The loaded templates
     */
    async loadTemplates() {
        this.debugLog('[WORKFLOW-MANAGER] Loading templates');
        
        try {
            // Update loading state
            this.state.loading.templates = true;
            
            // Get templates from service
            const templates = await this.service.getTemplates();
            this.state.templates = templates;
            
            this.debugLog('[WORKFLOW-MANAGER] Templates loaded:', templates.length);
            
            return templates;
        } catch (error) {
            this.debugLog('[WORKFLOW-MANAGER] Error loading templates', error);
            return [];
        } finally {
            // Update loading state
            this.state.loading.templates = false;
        }
    }
    
    /**
     * Load a template by ID
     * @param {string} id - The template ID
     * @returns {Promise<Object>} - The loaded template
     */
    async loadTemplate(id) {
        this.debugLog(`[WORKFLOW-MANAGER] Loading template ${id}`);
        
        try {
            // Get template from service
            const template = await this.service.getTemplate(id);
            
            // Store as active template
            this.state.activeTemplate = template;
            
            this.debugLog(`[WORKFLOW-MANAGER] Template ${id} loaded`);
            
            return template;
        } catch (error) {
            this.debugLog(`[WORKFLOW-MANAGER] Error loading template ${id}`, error);
            return null;
        }
    }
    
    /**
     * Create a new template
     * @param {Object} template - The template to create
     * @returns {Promise<Object>} - The created template
     */
    async createTemplate(template) {
        this.debugLog('[WORKFLOW-MANAGER] Creating template');
        
        try {
            // Create template via service
            const createdTemplate = await this.service.createTemplate(template);
            
            // Add to templates list
            if (createdTemplate) {
                this.state.templates.push(createdTemplate);
            }
            
            this.debugLog('[WORKFLOW-MANAGER] Template created');
            
            return createdTemplate;
        } catch (error) {
            this.debugLog('[WORKFLOW-MANAGER] Error creating template', error);
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
        this.debugLog(`[WORKFLOW-MANAGER] Updating template ${id}`);
        
        try {
            // Update template via service
            const updatedTemplate = await this.service.updateTemplate(id, template);
            
            // Update in templates list
            if (updatedTemplate) {
                const index = this.state.templates.findIndex(t => t.id === id);
                if (index !== -1) {
                    this.state.templates[index] = updatedTemplate;
                }
                
                // Update active template if it's the same
                if (this.state.activeTemplate && this.state.activeTemplate.id === id) {
                    this.state.activeTemplate = updatedTemplate;
                }
            }
            
            this.debugLog(`[WORKFLOW-MANAGER] Template ${id} updated`);
            
            return updatedTemplate;
        } catch (error) {
            this.debugLog(`[WORKFLOW-MANAGER] Error updating template ${id}`, error);
            return null;
        }
    }
    
    /**
     * Delete a template
     * @param {string} id - The template ID
     * @returns {Promise<boolean>} - Whether the deletion was successful
     */
    async deleteTemplate(id) {
        this.debugLog(`[WORKFLOW-MANAGER] Deleting template ${id}`);
        
        try {
            // Delete template via service
            const success = await this.service.deleteTemplate(id);
            
            // Remove from templates list
            if (success) {
                this.state.templates = this.state.templates.filter(t => t.id !== id);
                
                // Clear active template if it's the same
                if (this.state.activeTemplate && this.state.activeTemplate.id === id) {
                    this.state.activeTemplate = null;
                }
            }
            
            this.debugLog(`[WORKFLOW-MANAGER] Template ${id} deleted: ${success}`);
            
            return success;
        } catch (error) {
            this.debugLog(`[WORKFLOW-MANAGER] Error deleting template ${id}`, error);
            return false;
        }
    }
    
    /**
     * Use a template to create a workflow
     * @param {string} id - The template ID
     * @returns {Promise<Object>} - The created workflow
     */
    async useTemplate(id) {
        this.debugLog(`[WORKFLOW-MANAGER] Using template ${id}`);
        
        try {
            // Use template via service
            const workflow = await this.service.useTemplate(id);
            
            // Add to workflows list
            if (workflow) {
                this.state.workflows.push(workflow);
                this.state.activeWorkflow = workflow;
            }
            
            this.debugLog(`[WORKFLOW-MANAGER] Template ${id} used`);
            
            return workflow;
        } catch (error) {
            this.debugLog(`[WORKFLOW-MANAGER] Error using template ${id}`, error);
            return null;
        }
    }
    
    /**
     * Load executions from service
     * @returns {Promise<Array>} - The loaded executions
     */
    async loadExecutions() {
        this.debugLog('[WORKFLOW-MANAGER] Loading executions');
        
        try {
            // Update loading state
            this.state.loading.executions = true;
            
            // Get executions from service
            const executions = await this.service.getExecutions();
            this.state.executions = executions;
            
            this.debugLog('[WORKFLOW-MANAGER] Executions loaded:', executions.length);
            
            return executions;
        } catch (error) {
            this.debugLog('[WORKFLOW-MANAGER] Error loading executions', error);
            return [];
        } finally {
            // Update loading state
            this.state.loading.executions = false;
        }
    }
    
    /**
     * Load an execution by ID
     * @param {string} id - The execution ID
     * @returns {Promise<Object>} - The loaded execution
     */
    async loadExecution(id) {
        this.debugLog(`[WORKFLOW-MANAGER] Loading execution ${id}`);
        
        try {
            // Get execution from service
            const execution = await this.service.getExecution(id);
            
            // Store as active execution
            this.state.activeExecution = execution;
            
            this.debugLog(`[WORKFLOW-MANAGER] Execution ${id} loaded`);
            
            return execution;
        } catch (error) {
            this.debugLog(`[WORKFLOW-MANAGER] Error loading execution ${id}`, error);
            return null;
        }
    }
    
    /**
     * Load execution logs
     * @param {string} id - The execution ID
     * @returns {Promise<Array>} - The execution logs
     */
    async loadExecutionLogs(id) {
        this.debugLog(`[WORKFLOW-MANAGER] Loading execution logs ${id}`);
        
        try {
            // Get execution logs from service
            const logs = await this.service.getExecutionLogs(id);
            
            this.debugLog(`[WORKFLOW-MANAGER] Execution logs ${id} loaded:`, logs.length);
            
            return logs;
        } catch (error) {
            this.debugLog(`[WORKFLOW-MANAGER] Error loading execution logs ${id}`, error);
            return [];
        }
    }
    
    /**
     * Stop an execution
     * @param {string} id - The execution ID
     * @returns {Promise<boolean>} - Whether the stop was successful
     */
    async stopExecution(id) {
        this.debugLog(`[WORKFLOW-MANAGER] Stopping execution ${id}`);
        
        try {
            // Stop execution via service
            const success = await this.service.stopExecution(id);
            
            // Update execution in list
            if (success) {
                // Reload execution to get updated status
                const updatedExecution = await this.service.getExecution(id);
                
                if (updatedExecution) {
                    const index = this.state.executions.findIndex(e => e.id === id);
                    if (index !== -1) {
                        this.state.executions[index] = updatedExecution;
                    }
                    
                    // Update active execution if it's the same
                    if (this.state.activeExecution && this.state.activeExecution.id === id) {
                        this.state.activeExecution = updatedExecution;
                    }
                }
            }
            
            this.debugLog(`[WORKFLOW-MANAGER] Execution ${id} stopped: ${success}`);
            
            return success;
        } catch (error) {
            this.debugLog(`[WORKFLOW-MANAGER] Error stopping execution ${id}`, error);
            return false;
        }
    }
    
    /**
     * Filter executions by workflow and status
     * @param {string} workflowId - The workflow ID to filter by
     * @param {string} status - The status to filter by
     * @param {Date} fromDate - The from date to filter by
     * @param {Date} toDate - The to date to filter by
     * @returns {Array} - The filtered executions
     */
    filterExecutions(workflowId, status, fromDate, toDate) {
        this.debugLog('[WORKFLOW-MANAGER] Filtering executions');
        
        try {
            let filtered = [...this.state.executions];
            
            // Filter by workflow
            if (workflowId && workflowId !== 'all') {
                filtered = filtered.filter(e => e.workflowId === workflowId);
            }
            
            // Filter by status
            if (status && status !== 'all') {
                filtered = filtered.filter(e => e.status.toLowerCase() === status.toLowerCase());
            }
            
            // Filter by date range
            if (fromDate) {
                const from = new Date(fromDate);
                filtered = filtered.filter(e => new Date(e.startTime) >= from);
            }
            
            if (toDate) {
                const to = new Date(toDate);
                to.setHours(23, 59, 59, 999); // End of day
                filtered = filtered.filter(e => new Date(e.startTime) <= to);
            }
            
            this.debugLog('[WORKFLOW-MANAGER] Executions filtered:', filtered.length);
            
            return filtered;
        } catch (error) {
            this.debugLog('[WORKFLOW-MANAGER] Error filtering executions', error);
            return [];
        }
    }
    
    /**
     * Filter templates by category
     * @param {string} category - The category to filter by
     * @returns {Array} - The filtered templates
     */
    filterTemplates(category) {
        this.debugLog('[WORKFLOW-MANAGER] Filtering templates');
        
        try {
            let filtered = [...this.state.templates];
            
            // Filter by category
            if (category && category !== 'all') {
                filtered = filtered.filter(t => t.category.toLowerCase() === category.toLowerCase());
            }
            
            this.debugLog('[WORKFLOW-MANAGER] Templates filtered:', filtered.length);
            
            return filtered;
        } catch (error) {
            this.debugLog('[WORKFLOW-MANAGER] Error filtering templates', error);
            return [];
        }
    }
    
    /**
     * Search workflows by name or description
     * @param {string} query - The search query
     * @returns {Array} - The matching workflows
     */
    searchWorkflows(query) {
        this.debugLog('[WORKFLOW-MANAGER] Searching workflows');
        
        try {
            if (!query) {
                return [...this.state.workflows];
            }
            
            const lowerQuery = query.toLowerCase();
            const results = this.state.workflows.filter(workflow => 
                workflow.name.toLowerCase().includes(lowerQuery) ||
                workflow.description.toLowerCase().includes(lowerQuery)
            );
            
            this.debugLog('[WORKFLOW-MANAGER] Workflows search results:', results.length);
            
            return results;
        } catch (error) {
            this.debugLog('[WORKFLOW-MANAGER] Error searching workflows', error);
            return [];
        }
    }
    
    /**
     * Search templates by name or description
     * @param {string} query - The search query
     * @returns {Array} - The matching templates
     */
    searchTemplates(query) {
        this.debugLog('[WORKFLOW-MANAGER] Searching templates');
        
        try {
            if (!query) {
                return [...this.state.templates];
            }
            
            const lowerQuery = query.toLowerCase();
            const results = this.state.templates.filter(template => 
                template.name.toLowerCase().includes(lowerQuery) ||
                template.description.toLowerCase().includes(lowerQuery) ||
                template.category.toLowerCase().includes(lowerQuery)
            );
            
            this.debugLog('[WORKFLOW-MANAGER] Templates search results:', results.length);
            
            return results;
        } catch (error) {
            this.debugLog('[WORKFLOW-MANAGER] Error searching templates', error);
            return [];
        }
    }
    
    /**
     * Debug logging with workflow manager prefix
     * @param {string} message - The message to log
     * @param {Error|Object} [extra] - Optional error or object to log
     */
    debugLog(message, extra) {
        // Use debug shim if available
        if (window.debugShim) {
            if (extra instanceof Error) {
                window.debugShim.logError('workflow-manager', message, extra);
            } else if (extra !== undefined) {
                window.debugShim.log('workflow-manager', message, extra);
            } else {
                window.debugShim.log('workflow-manager', message);
            }
        } else {
            // Fallback to console
            if (extra instanceof Error) {
                console.error(message, extra);
            } else if (extra !== undefined) {
                console.log(message, extra);
            } else {
                console.log(message);
            }
        }
    }
}

// Export workflow manager
export { WorkflowManager };