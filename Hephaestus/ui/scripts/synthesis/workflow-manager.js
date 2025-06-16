/**
 * Workflow Manager
 * 
 * Manages workflows, their configurations, and lifecycle.
 */

import { SynthesisService } from './synthesis-service.js';

class WorkflowManager {
    constructor() {
        // Initialize service
        this.service = new SynthesisService();
        
        // State
        this.state = {
            workflows: [],
            loading: false,
            error: null
        };
        
        console.log('[SYNTHESIS] Workflow Manager initialized');
    }
    
    /**
     * Load all workflows
     */
    async loadWorkflows() {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            console.log('[SYNTHESIS] Loading workflows');
            const workflows = await this.service.getWorkflows();
            
            this.state.workflows = workflows;
            this.state.loading = false;
            
            return workflows;
        } catch (error) {
            console.error('[SYNTHESIS] Error loading workflows:', error);
            this.state.error = error.message;
            this.state.loading = false;
            throw error;
        }
    }
    
    /**
     * Get a specific workflow
     */
    async getWorkflow(id) {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            console.log(`[SYNTHESIS] Loading workflow ${id}`);
            const workflow = await this.service.getWorkflow(id);
            
            this.state.loading = false;
            return workflow;
        } catch (error) {
            console.error(`[SYNTHESIS] Error loading workflow ${id}:`, error);
            this.state.error = error.message;
            this.state.loading = false;
            throw error;
        }
    }
    
    /**
     * Create a new workflow
     */
    async createWorkflow(workflow) {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            console.log('[SYNTHESIS] Creating workflow:', workflow.name);
            const result = await this.service.createWorkflow(workflow);
            
            // Update local state
            this.state.workflows = [...this.state.workflows, result];
            this.state.loading = false;
            
            return result;
        } catch (error) {
            console.error('[SYNTHESIS] Error creating workflow:', error);
            this.state.error = error.message;
            this.state.loading = false;
            throw error;
        }
    }
    
    /**
     * Update an existing workflow
     */
    async updateWorkflow(id, workflow) {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            console.log(`[SYNTHESIS] Updating workflow ${id}`);
            const result = await this.service.updateWorkflow(id, workflow);
            
            // Update local state
            this.state.workflows = this.state.workflows.map(wf => 
                wf.id === id ? result : wf
            );
            this.state.loading = false;
            
            return result;
        } catch (error) {
            console.error(`[SYNTHESIS] Error updating workflow ${id}:`, error);
            this.state.error = error.message;
            this.state.loading = false;
            throw error;
        }
    }
    
    /**
     * Delete a workflow
     */
    async deleteWorkflow(id) {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            console.log(`[SYNTHESIS] Deleting workflow ${id}`);
            await this.service.deleteWorkflow(id);
            
            // Update local state
            this.state.workflows = this.state.workflows.filter(wf => wf.id !== id);
            this.state.loading = false;
            
            return true;
        } catch (error) {
            console.error(`[SYNTHESIS] Error deleting workflow ${id}:`, error);
            this.state.error = error.message;
            this.state.loading = false;
            throw error;
        }
    }
    
    /**
     * Import a workflow from JSON
     */
    async importWorkflow(workflowJson) {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            // Parse workflow if it's a string
            let workflow;
            if (typeof workflowJson === 'string') {
                try {
                    workflow = JSON.parse(workflowJson);
                } catch (parseError) {
                    throw new Error('Invalid workflow JSON');
                }
            } else {
                workflow = workflowJson;
            }
            
            // Validate required fields
            if (!workflow.name) {
                throw new Error('Workflow must have a name');
            }
            
            // Remove any ID to ensure it's treated as a new workflow
            delete workflow.id;
            
            console.log('[SYNTHESIS] Importing workflow:', workflow.name);
            
            // Create the workflow
            const result = await this.createWorkflow(workflow);
            return result;
        } catch (error) {
            console.error('[SYNTHESIS] Error importing workflow:', error);
            this.state.error = error.message;
            this.state.loading = false;
            throw error;
        }
    }
    
    /**
     * Export a workflow to JSON
     */
    async exportWorkflow(id) {
        try {
            // Get the workflow
            const workflow = await this.getWorkflow(id);
            
            // Format as JSON
            const jsonString = JSON.stringify(workflow, null, 2);
            
            // Create a Blob with the workflow data
            const blob = new Blob([jsonString], { type: 'application/json' });
            
            // Create a filename with workflow name and ID
            const safeWorkflowName = workflow.name.replace(/[^a-z0-9]/gi, '_').toLowerCase();
            const fileName = `workflow_${safeWorkflowName}_${id}.json`;
            
            // Create a download link
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = fileName;
            link.style.visibility = 'hidden';
            
            // Append, click, and remove the link
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            return true;
        } catch (error) {
            console.error(`[SYNTHESIS] Error exporting workflow ${id}:`, error);
            this.state.error = error.message;
            throw error;
        }
    }
    
    /**
     * Clone a workflow
     */
    async cloneWorkflow(id, newName) {
        try {
            // Get the original workflow
            const workflow = await this.getWorkflow(id);
            
            // Create a new workflow object with a new name
            const clonedWorkflow = {
                ...workflow,
                name: newName || `${workflow.name} (Clone)`,
                description: `Clone of: ${workflow.description || workflow.name}`
            };
            
            // Remove id, createdAt, and updatedAt from cloned workflow
            delete clonedWorkflow.id;
            delete clonedWorkflow.createdAt;
            delete clonedWorkflow.updatedAt;
            
            // Create the cloned workflow
            return await this.createWorkflow(clonedWorkflow);
        } catch (error) {
            console.error(`[SYNTHESIS] Error cloning workflow ${id}:`, error);
            this.state.error = error.message;
            throw error;
        }
    }
    
    /**
     * Filter workflows by category and status
     */
    filterWorkflows(category = '', status = '') {
        if (!this.state.workflows.length) {
            return [];
        }
        
        return this.state.workflows.filter(workflow => {
            // Check category filter
            const categoryMatch = !category || workflow.category === category;
            
            // Check status filter
            const statusMatch = !status || workflow.status === status;
            
            return categoryMatch && statusMatch;
        });
    }
    
    /**
     * Search workflows by name, category, or description
     */
    searchWorkflows(query = '') {
        if (!query || !this.state.workflows.length) {
            return this.state.workflows;
        }
        
        const searchTerms = query.toLowerCase().split(' ');
        
        return this.state.workflows.filter(workflow => {
            const workflowText = `${workflow.name} ${workflow.category} ${workflow.description || ''}`.toLowerCase();
            
            // Match all search terms
            return searchTerms.every(term => workflowText.includes(term));
        });
    }
    
    /**
     * Get unique categories from all workflows
     */
    getCategories() {
        if (!this.state.workflows.length) {
            return [];
        }
        
        const categories = this.state.workflows.map(workflow => workflow.category);
        return [...new Set(categories)].filter(category => category);
    }
    
    /**
     * Validate a workflow structure
     * Returns { valid: boolean, errors: string[] }
     */
    validateWorkflow(workflow) {
        const errors = [];
        
        // Check required fields
        if (!workflow.name) {
            errors.push('Workflow must have a name');
        }
        
        if (!workflow.category) {
            errors.push('Workflow must have a category');
        }
        
        // Check steps
        if (!workflow.steps || !Array.isArray(workflow.steps) || workflow.steps.length === 0) {
            errors.push('Workflow must have at least one step');
        } else {
            // Validate each step
            workflow.steps.forEach((step, index) => {
                if (!step.name) {
                    errors.push(`Step ${index + 1} must have a name`);
                }
                
                if (!step.type) {
                    errors.push(`Step ${index + 1} must have a type`);
                }
            });
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
}

// Export the manager class
export { WorkflowManager };