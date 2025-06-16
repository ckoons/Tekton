/**
 * Requirements Manager
 * 
 * Provides specialized functionality for managing requirements within the Telos component.
 * Handles requirement lifecycle, validation, and traceability operations.
 */

import { TelosClient } from './telos-service.js';

class RequirementsManager {
    constructor(client) {
        // Use provided client or create a new one
        this.client = client || new TelosClient();
        
        // Initialize cache for requirements data
        this.requirementsCache = new Map();
        this.projectsCache = new Map();
        
        // Track current filters
        this.currentFilters = {
            project: 'all',
            status: 'all',
            type: 'all'
        };
        
        console.log('[TELOS] RequirementsManager initialized');
        if (window.TektonDebug) TektonDebug.info('telosRequirements', 'RequirementsManager initialized');
    }
    
    /**
     * Load projects and cache them
     * @returns {Promise<Array>} Array of projects
     */
    async loadProjects() {
        console.log('[TELOS] Loading projects data');
        if (window.TektonDebug) TektonDebug.debug('telosRequirements', 'Loading projects data');
        
        try {
            const projects = await this.client.getProjects();
            
            // Cache projects by ID for quick lookup
            projects.forEach(project => {
                this.projectsCache.set(project.id, project);
            });
            
            return projects;
        } catch (error) {
            console.error('[TELOS] Error loading projects:', error);
            if (window.TektonDebug) TektonDebug.error('telosRequirements', 'Error loading projects', error);
            throw error;
        }
    }
    
    /**
     * Create a new project
     * @param {Object} projectData - Project data
     * @returns {Promise<Object>} Created project
     */
    async createProject(projectData) {
        console.log('[TELOS] Creating new project');
        if (window.TektonDebug) TektonDebug.info('telosRequirements', 'Creating new project', projectData);
        
        try {
            const newProject = await this.client.createProject(projectData);
            
            // Add to cache
            this.projectsCache.set(newProject.id, newProject);
            
            return newProject;
        } catch (error) {
            console.error('[TELOS] Error creating project:', error);
            if (window.TektonDebug) TektonDebug.error('telosRequirements', 'Error creating project', error);
            throw error;
        }
    }
    
    /**
     * Load requirements with optional filtering
     * @param {Object} filters - Filter criteria
     * @returns {Promise<Array>} Array of requirements
     */
    async loadRequirements(filters = {}) {
        // Merge with current filters or use defaults
        const appliedFilters = { ...this.currentFilters, ...filters };
        this.currentFilters = appliedFilters;
        
        console.log(`[TELOS] Loading requirements with filters: ${JSON.stringify(appliedFilters)}`);
        if (window.TektonDebug) TektonDebug.debug('telosRequirements', 'Loading requirements with filters', appliedFilters);
        
        try {
            const requirements = await this.client.getRequirements(appliedFilters);
            
            // Cache requirements by ID for quick lookup
            requirements.forEach(req => {
                this.requirementsCache.set(req.id, req);
            });
            
            return requirements;
        } catch (error) {
            console.error('[TELOS] Error loading requirements:', error);
            if (window.TektonDebug) TektonDebug.error('telosRequirements', 'Error loading requirements', error);
            throw error;
        }
    }
    
    /**
     * Get a specific requirement, using cache when available
     * @param {string} requirementId - ID of the requirement
     * @param {boolean} forceRefresh - Whether to force a refresh from server
     * @returns {Promise<Object>} Requirement object
     */
    async getRequirement(requirementId, forceRefresh = false) {
        console.log(`[TELOS] Getting requirement: ${requirementId}, force refresh: ${forceRefresh}`);
        if (window.TektonDebug) TektonDebug.debug('telosRequirements', `Getting requirement: ${requirementId}`);
        
        try {
            // Return from cache if available and not forcing refresh
            if (!forceRefresh && this.requirementsCache.has(requirementId)) {
                const cachedRequirement = this.requirementsCache.get(requirementId);
                console.log(`[TELOS] Returning requirement ${requirementId} from cache`);
                return cachedRequirement;
            }
            
            // Otherwise fetch from server
            const requirement = await this.client.getRequirement(requirementId);
            
            // Update cache
            this.requirementsCache.set(requirementId, requirement);
            
            return requirement;
        } catch (error) {
            console.error(`[TELOS] Error getting requirement ${requirementId}:`, error);
            if (window.TektonDebug) TektonDebug.error('telosRequirements', `Error getting requirement ${requirementId}`, error);
            throw error;
        }
    }
    
    /**
     * Create a new requirement
     * @param {Object} requirementData - Requirement data
     * @returns {Promise<Object>} Created requirement
     */
    async createRequirement(requirementData) {
        console.log('[TELOS] Creating new requirement');
        if (window.TektonDebug) TektonDebug.info('telosRequirements', 'Creating new requirement', requirementData);
        
        try {
            const newRequirement = await this.client.createRequirement(requirementData);
            
            // Update cache
            this.requirementsCache.set(newRequirement.id, newRequirement);
            
            // Update project requirement count if we have the project in cache
            const projectId = requirementData.project;
            if (this.projectsCache.has(projectId)) {
                const project = this.projectsCache.get(projectId);
                project.requirementCount = (project.requirementCount || 0) + 1;
                this.projectsCache.set(projectId, project);
            }
            
            return newRequirement;
        } catch (error) {
            console.error('[TELOS] Error creating requirement:', error);
            if (window.TektonDebug) TektonDebug.error('telosRequirements', 'Error creating requirement', error);
            throw error;
        }
    }
    
    /**
     * Update an existing requirement
     * @param {string} requirementId - ID of the requirement to update
     * @param {Object} requirementData - Updated requirement data
     * @returns {Promise<Object>} Updated requirement
     */
    async updateRequirement(requirementId, requirementData) {
        console.log(`[TELOS] Updating requirement: ${requirementId}`);
        if (window.TektonDebug) TektonDebug.info('telosRequirements', `Updating requirement: ${requirementId}`, requirementData);
        
        try {
            const updatedRequirement = await this.client.updateRequirement(requirementId, requirementData);
            
            // Update cache
            this.requirementsCache.set(requirementId, updatedRequirement);
            
            return updatedRequirement;
        } catch (error) {
            console.error(`[TELOS] Error updating requirement ${requirementId}:`, error);
            if (window.TektonDebug) TektonDebug.error('telosRequirements', `Error updating requirement ${requirementId}`, error);
            throw error;
        }
    }
    
    /**
     * Delete a requirement
     * @param {string} requirementId - ID of the requirement to delete
     * @returns {Promise<boolean>} Success indicator
     */
    async deleteRequirement(requirementId) {
        console.log(`[TELOS] Deleting requirement: ${requirementId}`);
        if (window.TektonDebug) TektonDebug.info('telosRequirements', `Deleting requirement: ${requirementId}`);
        
        try {
            // Get requirement to determine project before deletion
            let projectId;
            if (this.requirementsCache.has(requirementId)) {
                const requirement = this.requirementsCache.get(requirementId);
                projectId = requirement.project;
            }
            
            const success = await this.client.deleteRequirement(requirementId);
            
            if (success) {
                // Remove from cache
                this.requirementsCache.delete(requirementId);
                
                // Update project requirement count if we have the project in cache
                if (projectId && this.projectsCache.has(projectId)) {
                    const project = this.projectsCache.get(projectId);
                    project.requirementCount = Math.max(0, (project.requirementCount || 0) - 1);
                    this.projectsCache.set(projectId, project);
                }
            }
            
            return success;
        } catch (error) {
            console.error(`[TELOS] Error deleting requirement ${requirementId}:`, error);
            if (window.TektonDebug) TektonDebug.error('telosRequirements', `Error deleting requirement ${requirementId}`, error);
            throw error;
        }
    }
    
    /**
     * Load traceability data for visualization
     * @param {string} projectId - Optional project ID to filter by
     * @returns {Promise<Object>} Traceability data
     */
    async loadTraceabilityData(projectId = 'all') {
        console.log(`[TELOS] Loading traceability data for project: ${projectId}`);
        if (window.TektonDebug) TektonDebug.debug('telosRequirements', `Loading traceability for project: ${projectId}`);
        
        try {
            const traceabilityData = await this.client.getTraceabilityData(projectId);
            return traceabilityData;
        } catch (error) {
            console.error('[TELOS] Error loading traceability data:', error);
            if (window.TektonDebug) TektonDebug.error('telosRequirements', 'Error loading traceability data', error);
            throw error;
        }
    }
    
    /**
     * Validate requirements against quality criteria
     * @param {Object} params - Validation parameters
     * @returns {Promise<Object>} Validation results
     */
    async validateRequirements(params) {
        console.log(`[TELOS] Validating requirements with params: ${JSON.stringify(params)}`);
        if (window.TektonDebug) TektonDebug.info('telosRequirements', 'Validating requirements', params);
        
        try {
            const validationResults = await this.client.validateRequirements(params);
            return validationResults;
        } catch (error) {
            console.error('[TELOS] Error validating requirements:', error);
            if (window.TektonDebug) TektonDebug.error('telosRequirements', 'Error validating requirements', error);
            throw error;
        }
    }
    
    /**
     * Generate a requirement ID for a new requirement
     * @param {string} projectId - ID of the project
     * @returns {Promise<string>} Generated requirement ID
     */
    async generateRequirementId(projectId) {
        console.log(`[TELOS] Generating requirement ID for project: ${projectId}`);
        
        try {
            // Load requirements for this project
            const requirements = await this.loadRequirements({ project: projectId });
            
            // Find the highest existing ID number
            let maxNumber = 0;
            const idRegex = /REQ-(\d+)/;
            
            requirements.forEach(req => {
                const match = req.id.match(idRegex);
                if (match && match[1]) {
                    const num = parseInt(match[1], 10);
                    if (num > maxNumber) {
                        maxNumber = num;
                    }
                }
            });
            
            // Generate new ID with next number
            const nextNumber = maxNumber + 1;
            const paddedNumber = nextNumber.toString().padStart(3, '0');
            const newId = `REQ-${paddedNumber}`;
            
            console.log(`[TELOS] Generated requirement ID: ${newId}`);
            return newId;
        } catch (error) {
            console.error(`[TELOS] Error generating requirement ID:`, error);
            if (window.TektonDebug) TektonDebug.error('telosRequirements', 'Error generating requirement ID', error);
            
            // Fallback to a timestamp-based ID if needed
            const timestamp = Date.now().toString().slice(-6);
            return `REQ-${timestamp}`;
        }
    }
    
    /**
     * Export requirements to different formats
     * @param {Array} requirements - Requirements to export
     * @param {string} format - Export format ('csv', 'json', 'pdf')
     * @returns {Promise<string|Blob>} Exported data or file URL
     */
    async exportRequirements(requirements, format = 'csv') {
        console.log(`[TELOS] Exporting ${requirements.length} requirements to ${format} format`);
        if (window.TektonDebug) TektonDebug.info('telosRequirements', `Exporting requirements to ${format}`);
        
        try {
            // Handle different export formats
            switch (format.toLowerCase()) {
                case 'csv':
                    return this.exportToCsv(requirements);
                case 'json':
                    return this.exportToJson(requirements);
                case 'pdf':
                    return this.exportToPdf(requirements);
                default:
                    throw new Error(`Unsupported export format: ${format}`);
            }
        } catch (error) {
            console.error(`[TELOS] Error exporting requirements to ${format}:`, error);
            if (window.TektonDebug) TektonDebug.error('telosRequirements', `Error exporting to ${format}`, error);
            throw error;
        }
    }
    
    /**
     * Export requirements to CSV format
     * @param {Array} requirements - Requirements to export
     * @returns {string} CSV content
     */
    exportToCsv(requirements) {
        // Define CSV headers
        const headers = ['ID', 'Title', 'Project', 'Type', 'Priority', 'Status', 'Description'];
        
        // Create CSV content
        let csv = headers.join(',') + '\n';
        
        requirements.forEach(req => {
            // Escape fields with quotes and handle commas
            const row = [
                req.id,
                `"${req.title.replace(/"/g, '""')}"`,
                `"${req.project.replace(/"/g, '""')}"`,
                req.type,
                req.priority,
                req.status,
                `"${req.description.replace(/"/g, '""')}"`
            ];
            
            csv += row.join(',') + '\n';
        });
        
        return csv;
    }
    
    /**
     * Export requirements to JSON format
     * @param {Array} requirements - Requirements to export
     * @returns {string} JSON content
     */
    exportToJson(requirements) {
        return JSON.stringify(requirements, null, 2);
    }
    
    /**
     * Export requirements to PDF (simulated)
     * @param {Array} requirements - Requirements to export
     * @returns {Promise<string>} Message about PDF generation
     */
    exportToPdf(requirements) {
        // In a real implementation, this would generate a PDF
        // For this prototype, we'll return a message
        return Promise.resolve(`PDF export would include ${requirements.length} requirements in a real implementation.`);
    }
    
    /**
     * Clear the requirement and project caches
     */
    clearCache() {
        console.log('[TELOS] Clearing requirements and projects cache');
        if (window.TektonDebug) TektonDebug.debug('telosRequirements', 'Clearing cache');
        
        this.requirementsCache.clear();
        this.projectsCache.clear();
    }
}

// Export for module use
export { RequirementsManager };