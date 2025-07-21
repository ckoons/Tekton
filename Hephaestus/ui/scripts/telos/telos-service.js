/**
 * Telos Service
 * 
 * Provides API communication services for the Telos requirements management component.
 * Handles fetching, creating, updating, and deleting requirements and related data.
 */

console.log('[FILE_TRACE] Loading: telos-service.js');
class TelosClient {
    constructor() {
        // Base URL for the API using tekton_url helper
        this.baseUrl = window.tekton_url ? window.tekton_url('telos', '/api') : '/api/telos';
        
        // Default headers for API requests
        this.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
        
        console.log('[TELOS] TelosClient initialized with baseUrl:', this.baseUrl);
        if (window.TektonDebug) TektonDebug.info('telosService', 'TelosClient initialized');
    }
    
    /**
     * Health check for the Telos service
     * @returns {Promise<Object>} Health status
     */
    async health() {
        try {
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                headers: this.headers
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('[TELOS] Health check:', data);
            return data;
        } catch (error) {
            console.error('[TELOS] Health check failed:', error);
            return { status: 'error', message: error.message };
        }
    }
    
    /**
     * Get a list of all projects
     * @returns {Promise<Array>} Array of project objects
     */
    async getProjects() {
        console.log('[TELOS] Fetching projects');
        if (window.TektonDebug) TektonDebug.debug('telosService', 'Fetching projects');
        
        try {
            const response = await fetch(`${this.baseUrl}/projects`, {
                method: 'GET',
                headers: this.headers
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log(`[TELOS] Fetched projects data:`, data);
            if (window.TektonDebug) TektonDebug.info('telosService', `Fetched projects data`, data);
            
            return data.projects || data;
        } catch (error) {
            console.error('[TELOS] Error fetching projects:', error);
            if (window.TektonDebug) TektonDebug.error('telosService', 'Error fetching projects', error);
            throw error;
        }
    }
    
    /**
     * Get a specific project by ID
     * @param {string} projectId - ID of the project to retrieve
     * @returns {Promise<Object>} Project object
     */
    async getProject(projectId) {
        console.log(`[TELOS] Fetching project: ${projectId}`);
        if (window.TektonDebug) TektonDebug.debug('telosService', `Fetching project: ${projectId}`);
        
        try {
            const response = await fetch(`${this.baseUrl}/projects/${projectId}`, {
                method: 'GET',
                headers: this.headers
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log(`[TELOS] Fetched project ${projectId}:`, data);
            if (window.TektonDebug) TektonDebug.info('telosService', `Fetched project ${projectId}`, data);
            
            return data.project || data;
        } catch (error) {
            console.error(`[TELOS] Error fetching project ${projectId}:`, error);
            if (window.TektonDebug) TektonDebug.error('telosService', `Error fetching project ${projectId}`, error);
            throw error;
        }
    }
    
    /**
     * Create a new project
     * @param {Object} projectData - Project data to create
     * @returns {Promise<Object>} Created project object
     */
    async createProject(projectData) {
        console.log(`[TELOS] Creating project: ${JSON.stringify(projectData)}`);
        if (window.TektonDebug) TektonDebug.info('telosService', 'Creating new project', projectData);
        
        try {
            // Simulate API call
            return new Promise((resolve) => {
                setTimeout(() => {
                    // Generate ID from name if not provided
                    const projectId = projectData.id || projectData.name.toLowerCase().replace(/\s+/g, '-');
                    
                    // Merge with provided data
                    const newProject = {
                        id: projectId,
                        status: 'Active',
                        requirementCount: 0,
                        ...projectData,
                        createdAt: new Date().toISOString()
                    };
                    
                    console.log(`[TELOS] Created project: ${projectId}`);
                    if (window.TektonDebug) TektonDebug.info('telosService', `Created project: ${projectId}`);
                    
                    resolve(newProject);
                }, 1000);
            });
        } catch (error) {
            console.error('[TELOS] Error creating project:', error);
            if (window.TektonDebug) TektonDebug.error('telosService', 'Error creating project', error);
            throw error;
        }
    }
    
    /**
     * Get requirements list with optional filtering
     * @param {Object} filters - Filter criteria
     * @returns {Promise<Array>} Array of requirement objects
     */
    async getRequirements(filters = {}) {
        console.log(`[TELOS] Fetching requirements with filters: ${JSON.stringify(filters)}`);
        if (window.TektonDebug) TektonDebug.debug('telosService', 'Fetching requirements', filters);
        
        try {
            const queryParams = new URLSearchParams();
            Object.keys(filters).forEach(key => {
                if (filters[key]) queryParams.append(key, filters[key]);
            });
            
            const response = await fetch(`${this.baseUrl}/requirements?${queryParams}`, {
                method: 'GET',
                headers: this.headers
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log(`[TELOS] Fetched requirements:`, data);
            if (window.TektonDebug) TektonDebug.info('telosService', 'Fetched requirements', data);
            
            return data.requirements || data;
                        {
                            id: 'REQ-001',
                            title: 'Component Isolation',
                            project: 'Tekton UI Refactoring',
                            type: 'Functional',
                            priority: 'High',
                            status: 'In Progress',
                            description: 'UI components must be fully isolated with no shared state or DOM manipulation.'
                        },
                        {
                            id: 'REQ-002',
                            title: 'BEM Naming Convention',
                            project: 'Tekton UI Refactoring',
                            type: 'Constraint',
                            priority: 'Medium',
                            status: 'Completed',
                            description: 'All UI components must use BEM naming convention for CSS classes.'
                        },
                        {
                            id: 'REQ-003',
                            title: 'Memory Persistence',
                            project: 'Engram Memory System',
                            type: 'Functional',
                            priority: 'High',
                            status: 'In Progress',
                            description: 'System must persist memory across sessions with configurable retention policy.'
                        },
                        {
                            id: 'REQ-004',
                            title: 'Memory Categorization',
                            project: 'Engram Memory System',
                            type: 'Functional',
                            priority: 'Medium',
                            status: 'New',
                            description: 'System must automatically categorize memories by relevance and topic.'
                        },
                        {
                            id: 'REQ-005',
                            title: 'Message Routing',
                            project: 'Hermes Communication Layer',
                            type: 'Functional',
                            priority: 'High',
                            status: 'Completed',
                            description: 'System must route messages to appropriate services based on message type and content.'
                        },
                        {
                            id: 'REQ-006',
                            title: 'Service Discovery',
                            project: 'Hermes Communication Layer',
                            type: 'Functional',
                            priority: 'Medium',
                            status: 'Completed',
                            description: 'System must support automatic service discovery and registration.'
                        }
                    ];
                    
                    // Apply filters if provided
                    let filteredRequirements = [...allRequirements];
                    
                    if (filters.project && filters.project !== 'all') {
                        filteredRequirements = filteredRequirements.filter(req => 
                            req.project.toLowerCase() === filters.project.toLowerCase());
                    }
                    
                    if (filters.status && filters.status !== 'all') {
                        filteredRequirements = filteredRequirements.filter(req => 
                            req.status.toLowerCase().replace(/\s+/g, '-') === filters.status.toLowerCase());
                    }
                    
                    if (filters.type && filters.type !== 'all') {
                        filteredRequirements = filteredRequirements.filter(req => 
                            req.type.toLowerCase() === filters.type.toLowerCase());
                    }
                    
                    if (filters.query) {
                        const query = filters.query.toLowerCase();
                        filteredRequirements = filteredRequirements.filter(req => 
                            req.id.toLowerCase().includes(query) || 
                            req.title.toLowerCase().includes(query) || 
                            req.description.toLowerCase().includes(query));
                    }
                    
                    console.log(`[TELOS] Fetched ${filteredRequirements.length} requirements`);
                    if (window.TektonDebug) TektonDebug.info('telosService', `Fetched ${filteredRequirements.length} requirements`);
                    
                    resolve(filteredRequirements);
                }, 1200);
            });
        } catch (error) {
            console.error('[TELOS] Error fetching requirements:', error);
            if (window.TektonDebug) TektonDebug.error('telosService', 'Error fetching requirements', error);
            throw error;
        }
    }
    
    /**
     * Get a specific requirement by ID
     * @param {string} requirementId - ID of the requirement to retrieve
     * @returns {Promise<Object>} Requirement object
     */
    async getRequirement(requirementId) {
        console.log(`[TELOS] Fetching requirement: ${requirementId}`);
        if (window.TektonDebug) TektonDebug.debug('telosService', `Fetching requirement: ${requirementId}`);
        
        try {
            // Simulate API call
            return new Promise((resolve, reject) => {
                setTimeout(() => {
                    // Mock requirements data (abbreviated for clarity)
                    const requirementsData = {
                        'REQ-001': {
                            id: 'REQ-001',
                            title: 'Component Isolation',
                            project: 'Tekton UI Refactoring',
                            type: 'Functional',
                            priority: 'High',
                            status: 'In Progress',
                            description: 'UI components must be fully isolated with no shared state or DOM manipulation.',
                            acceptanceCriteria: [
                                'Each component has its own CSS namespace using BEM',
                                'No direct DOM manipulation outside component container',
                                'No shared global state between components',
                                'Component works independently when loaded alone'
                            ],
                            created: '2025-03-05T10:30:00Z',
                            updated: '2025-03-15T14:22:00Z',
                            author: 'Casey Koons',
                            assignee: 'UI Team',
                            relatedRequirements: ['REQ-002', 'REQ-007'],
                            attachments: [],
                            comments: [
                                {
                                    author: 'UI Team',
                                    date: '2025-03-10T09:15:00Z',
                                    text: 'We need to clarify what constitutes "shared state"'
                                }
                            ]
                        },
                        'REQ-002': {
                            id: 'REQ-002',
                            title: 'BEM Naming Convention',
                            project: 'Tekton UI Refactoring',
                            type: 'Constraint',
                            priority: 'Medium',
                            status: 'Completed',
                            description: 'All UI components must use BEM naming convention for CSS classes.',
                            acceptanceCriteria: [
                                'All CSS classes follow format: block__element--modifier',
                                'Each component has its own block name',
                                'No generic class names without component prefix',
                                'Style definitions only target BEM classes'
                            ],
                            created: '2025-03-06T11:45:00Z',
                            updated: '2025-03-20T15:30:00Z',
                            author: 'Casey Koons',
                            assignee: 'UI Team',
                            relatedRequirements: ['REQ-001'],
                            attachments: [],
                            comments: []
                        }
                    };
                    
                    if (requirementsData[requirementId]) {
                        console.log(`[TELOS] Fetched requirement: ${requirementId}`);
                        if (window.TektonDebug) TektonDebug.info('telosService', `Fetched requirement: ${requirementId}`);
                        resolve(requirementsData[requirementId]);
                    } else {
                        const error = new Error(`Requirement not found: ${requirementId}`);
                        console.error(`[TELOS] ${error.message}`);
                        if (window.TektonDebug) TektonDebug.error('telosService', error.message);
                        reject(error);
                    }
                }, 800);
            });
        } catch (error) {
            console.error(`[TELOS] Error fetching requirement ${requirementId}:`, error);
            if (window.TektonDebug) TektonDebug.error('telosService', `Error fetching requirement ${requirementId}`, error);
            throw error;
        }
    }
    
    /**
     * Create a new requirement
     * @param {Object} requirementData - Requirement data to create
     * @returns {Promise<Object>} Created requirement object
     */
    async createRequirement(requirementData) {
        console.log(`[TELOS] Creating requirement: ${JSON.stringify(requirementData)}`);
        if (window.TektonDebug) TektonDebug.info('telosService', 'Creating new requirement', requirementData);
        
        try {
            // Simulate API call
            return new Promise((resolve) => {
                setTimeout(() => {
                    // Generate ID from project if not provided
                    const project = requirementData.project.substring(0, 3).toUpperCase();
                    const reqId = `REQ-${Math.floor(Math.random() * 900) + 100}`;
                    
                    // Merge with provided data
                    const newRequirement = {
                        id: reqId,
                        status: 'New',
                        priority: 'Medium',
                        type: 'Functional',
                        ...requirementData,
                        created: new Date().toISOString(),
                        updated: new Date().toISOString(),
                        author: 'Current User',
                        comments: [],
                        attachments: []
                    };
                    
                    console.log(`[TELOS] Created requirement: ${reqId}`);
                    if (window.TektonDebug) TektonDebug.info('telosService', `Created requirement: ${reqId}`);
                    
                    resolve(newRequirement);
                }, 1000);
            });
        } catch (error) {
            console.error('[TELOS] Error creating requirement:', error);
            if (window.TektonDebug) TektonDebug.error('telosService', 'Error creating requirement', error);
            throw error;
        }
    }
    
    /**
     * Update an existing requirement
     * @param {string} requirementId - ID of the requirement to update
     * @param {Object} requirementData - Updated requirement data
     * @returns {Promise<Object>} Updated requirement object
     */
    async updateRequirement(requirementId, requirementData) {
        console.log(`[TELOS] Updating requirement ${requirementId}: ${JSON.stringify(requirementData)}`);
        if (window.TektonDebug) TektonDebug.info('telosService', `Updating requirement ${requirementId}`, requirementData);
        
        try {
            // Simulate API call
            return new Promise((resolve, reject) => {
                setTimeout(() => {
                    // In a real implementation, this would fetch the requirement first
                    // and validate that it exists
                    
                    // For this prototype, we'll just return the updated data
                    const updatedRequirement = {
                        id: requirementId,
                        ...requirementData,
                        updated: new Date().toISOString()
                    };
                    
                    console.log(`[TELOS] Updated requirement: ${requirementId}`);
                    if (window.TektonDebug) TektonDebug.info('telosService', `Updated requirement: ${requirementId}`);
                    
                    resolve(updatedRequirement);
                }, 800);
            });
        } catch (error) {
            console.error(`[TELOS] Error updating requirement ${requirementId}:`, error);
            if (window.TektonDebug) TektonDebug.error('telosService', `Error updating requirement ${requirementId}`, error);
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
        if (window.TektonDebug) TektonDebug.info('telosService', `Deleting requirement: ${requirementId}`);
        
        try {
            // Simulate API call
            return new Promise((resolve) => {
                setTimeout(() => {
                    console.log(`[TELOS] Deleted requirement: ${requirementId}`);
                    if (window.TektonDebug) TektonDebug.info('telosService', `Deleted requirement: ${requirementId}`);
                    
                    resolve(true);
                }, 800);
            });
        } catch (error) {
            console.error(`[TELOS] Error deleting requirement ${requirementId}:`, error);
            if (window.TektonDebug) TektonDebug.error('telosService', `Error deleting requirement ${requirementId}`, error);
            throw error;
        }
    }
    
    /**
     * Get traceability data for requirements
     * @param {string} projectId - Optional project ID to filter by
     * @returns {Promise<Object>} Traceability data structure
     */
    async getTraceabilityData(projectId = 'all') {
        console.log(`[TELOS] Fetching traceability data for project: ${projectId}`);
        if (window.TektonDebug) TektonDebug.debug('telosService', `Fetching traceability for project: ${projectId}`);
        
        try {
            // Simulate API call
            return new Promise((resolve) => {
                setTimeout(() => {
                    // Mock traceability data - simplified for the prototype
                    const traceabilityData = {
                        nodes: [
                            { id: 'REQ-001', label: 'Component Isolation', type: 'requirement' },
                            { id: 'REQ-002', label: 'BEM Naming Convention', type: 'requirement' },
                            { id: 'REQ-003', label: 'Memory Persistence', type: 'requirement' },
                            { id: 'REQ-004', label: 'Memory Categorization', type: 'requirement' },
                            { id: 'REQ-005', label: 'Message Routing', type: 'requirement' },
                            { id: 'REQ-006', label: 'Service Discovery', type: 'requirement' },
                            { id: 'IMPL-001', label: 'Component Isolation Implementation', type: 'implementation' },
                            { id: 'IMPL-002', label: 'BEM Implementation', type: 'implementation' },
                            { id: 'TEST-001', label: 'Component Isolation Test', type: 'test' },
                            { id: 'TEST-002', label: 'BEM Compliance Test', type: 'test' }
                        ],
                        edges: [
                            { source: 'REQ-001', target: 'REQ-002', label: 'depends on' },
                            { source: 'REQ-001', target: 'IMPL-001', label: 'implemented by' },
                            { source: 'REQ-002', target: 'IMPL-002', label: 'implemented by' },
                            { source: 'REQ-001', target: 'TEST-001', label: 'verified by' },
                            { source: 'REQ-002', target: 'TEST-002', label: 'verified by' },
                            { source: 'REQ-003', target: 'REQ-004', label: 'related to' },
                            { source: 'REQ-005', target: 'REQ-006', label: 'related to' }
                        ]
                    };
                    
                    // Filter by project if specified
                    if (projectId !== 'all') {
                        // In a real implementation, we would filter the data based on project
                        // For the prototype, we'll just return the mock data as is
                    }
                    
                    console.log('[TELOS] Fetched traceability data');
                    if (window.TektonDebug) TektonDebug.info('telosService', 'Fetched traceability data');
                    
                    resolve(traceabilityData);
                }, 1200);
            });
        } catch (error) {
            console.error('[TELOS] Error fetching traceability data:', error);
            if (window.TektonDebug) TektonDebug.error('telosService', 'Error fetching traceability data', error);
            throw error;
        }
    }
    
    /**
     * Validate requirements against specified criteria
     * @param {Object} params - Validation parameters
     * @returns {Promise<Object>} Validation results
     */
    async validateRequirements(params) {
        console.log(`[TELOS] Validating requirements: ${JSON.stringify(params)}`);
        if (window.TektonDebug) TektonDebug.info('telosService', 'Validating requirements', params);
        
        try {
            // Simulate API call
            return new Promise((resolve) => {
                setTimeout(() => {
                    // Mock validation results
                    const validationResults = {
                        project: params.project,
                        timestamp: new Date().toISOString(),
                        summary: {
                            total: 24,
                            passed: 18,
                            failed: 6
                        },
                        criteriaResults: {
                            completeness: params.criteria.completeness ? {
                                passed: 20,
                                failed: 4,
                                issues: [
                                    { id: 'REQ-003', message: 'Missing acceptance criteria' },
                                    { id: 'REQ-018', message: 'Missing priority' }
                                ]
                            } : null,
                            clarity: params.criteria.clarity ? {
                                passed: 22,
                                failed: 2,
                                issues: [
                                    { id: 'REQ-007', message: 'Ambiguous wording' },
                                    { id: 'REQ-022', message: 'Too technical for business requirement' }
                                ]
                            } : null,
                            consistency: params.criteria.consistency ? {
                                passed: 23,
                                failed: 1,
                                issues: [
                                    { id: 'REQ-012', message: 'Conflicts with REQ-009' }
                                ]
                            } : null,
                            testability: params.criteria.testability ? {
                                passed: 23,
                                failed: 1,
                                issues: [
                                    { id: 'REQ-015', message: 'Not verifiable' }
                                ]
                            } : null,
                            feasibility: params.criteria.feasibility ? {
                                passed: 24,
                                failed: 0,
                                issues: []
                            } : null
                        }
                    };
                    
                    console.log('[TELOS] Requirements validation completed');
                    if (window.TektonDebug) TektonDebug.info('telosService', 'Requirements validation completed');
                    
                    resolve(validationResults);
                }, 1500);
            });
        } catch (error) {
            console.error('[TELOS] Error validating requirements:', error);
            if (window.TektonDebug) TektonDebug.error('telosService', 'Error validating requirements', error);
            throw error;
        }
    }
}

// Export for module use
export { TelosClient };