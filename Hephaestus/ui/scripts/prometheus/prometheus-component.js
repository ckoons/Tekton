/**
 * Prometheus Planning System Component
 * 
 * Provides a comprehensive interface for project planning, timeline management,
 * resource allocation, and critical path analysis.
 */

// Import dependent services
// NOTE: These are loaded via script tags in the HTML, so we access them through window
const PrometheusService = window.PrometheusService;
const TimelineVisualization = window.TimelineVisualization;

class PrometheusComponent {
    constructor() {
        this.debugPrefix = '[PROMETHEUS]';
        console.log(`${this.debugPrefix} Component constructed`);
        
        this.state = {
            activeTab: 'planning',
            projects: [],
            resources: [],
            analysisResults: null,
            loading: {
                projects: false,
                resources: false,
                timeline: false,
                analysis: false
            },
            errors: {
                projects: null,
                resources: null,
                timeline: null,
                analysis: null
            },
            messageDrafts: {
                planningchat: '',
                teamchat: ''
            }
        };

        // Reference to root element
        this.container = document.querySelector('.prometheus');
        
        // Create service instances
        this.service = window.PrometheusService ? new PrometheusService() : null;
        this.timelineService = window.TimelineVisualization ? new TimelineVisualization() : null;
        
        if (!this.service) {
            console.warn(`${this.debugPrefix} PrometheusService not available - some functionality will be limited`);
        }
        
        if (!this.timelineService) {
            console.warn(`${this.debugPrefix} TimelineVisualization not available - timeline visualization will be limited`);
        }
        
        // Bind event handlers
        this.handleSendMessage = this.handleSendMessage.bind(this);
        this.handleSearchProjects = this.handleSearchProjects.bind(this);
        this.handleAddProject = this.handleAddProject.bind(this);
        this.handleRunAnalysis = this.handleRunAnalysis.bind(this);
        this.handleClearAnalysis = this.handleClearAnalysis.bind(this);
        this.handleChangeView = this.handleChangeView.bind(this);
        this.handleApplyFilter = this.handleApplyFilter.bind(this);
        this.handleApplyResourceFilter = this.handleApplyResourceFilter.bind(this);
        this.handleAddResource = this.handleAddResource.bind(this);
    }

    /**
     * Initialize the component
     */
    async init() {
        console.log(`${this.debugPrefix} Initializing component`);
        
        try {
            // Setup event listeners
            this.setupEventListeners();
            
            // Load initial data
            if (this.service) {
                this.loadProjects();
            } else {
                // Show demo data if service is not available
                this.showDemoData();
            }
            
            // Initialize timeline visualization if available
            if (this.timelineService) {
                // Setup timeline options and initialize it
                const timelineContainer = this.container.querySelector('#timeline-container');
                if (timelineContainer) {
                    this.timelineService.init(timelineContainer);
                }
            }
            
            // Try to load state from local storage
            this.loadComponentState();
            
            console.log(`${this.debugPrefix} Component initialized successfully`);
        } catch (error) {
            console.error(`${this.debugPrefix} Error initializing component:`, error);
        }
    }

    /**
     * Set up event listeners for all interactive elements
     */
    setupEventListeners() {
        console.log(`${this.debugPrefix} Setting up event listeners`);
        
        try {
            // Only query elements within this component's container
            if (!this.container) {
                console.error(`${this.debugPrefix} Cannot find prometheus container for event listeners`);
                return;
            }
            
            // Chat input events
            const chatInput = this.container.querySelector('#chat-input');
            const sendButton = this.container.querySelector('#send-button');
            
            if (chatInput && sendButton) {
                chatInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        this.handleSendMessage();
                    }
                });
                
                sendButton.addEventListener('click', () => {
                    this.handleSendMessage();
                });
            }
            
            // Planning tab events
            const searchProjectsButton = this.container.querySelector('#project-search-btn');
            const addProjectButton = this.container.querySelector('#add-project-btn');
            
            if (searchProjectsButton) {
                searchProjectsButton.addEventListener('click', this.handleSearchProjects);
            }
            
            if (addProjectButton) {
                addProjectButton.addEventListener('click', this.handleAddProject);
            }
            
            // Timeline tab events
            const applyViewButton = this.container.querySelector('#apply-view-btn');
            const applyFilterButton = this.container.querySelector('#apply-filter-btn');
            
            if (applyViewButton) {
                applyViewButton.addEventListener('click', this.handleChangeView);
            }
            
            if (applyFilterButton) {
                applyFilterButton.addEventListener('click', this.handleApplyFilter);
            }
            
            // Resources tab events
            const applyResourceFilterButton = this.container.querySelector('#apply-resource-filter-btn');
            const addResourceButton = this.container.querySelector('#add-resource-btn');
            
            if (applyResourceFilterButton) {
                applyResourceFilterButton.addEventListener('click', this.handleApplyResourceFilter);
            }
            
            if (addResourceButton) {
                addResourceButton.addEventListener('click', this.handleAddResource);
            }
            
            // Analysis tab events
            const runAnalysisButton = this.container.querySelector('#run-analysis-btn');
            const clearAnalysisButton = this.container.querySelector('#clear-analysis-btn');
            
            if (runAnalysisButton) {
                runAnalysisButton.addEventListener('click', this.handleRunAnalysis);
            }
            
            if (clearAnalysisButton) {
                clearAnalysisButton.addEventListener('click', this.handleClearAnalysis);
            }
            
            console.log(`${this.debugPrefix} Event listeners set up successfully`);
        } catch (error) {
            console.error(`${this.debugPrefix} Error setting up event listeners:`, error);
        }
    }

    /**
     * Save component state to local storage
     */
    saveComponentState() {
        try {
            // Don't save entire state, just important user-specific parts
            const stateToSave = {
                activeTab: this.state.activeTab,
                messageDrafts: this.state.messageDrafts
            };
            
            localStorage.setItem('prometheusComponentState', JSON.stringify(stateToSave));
            console.log(`${this.debugPrefix} Component state saved to local storage`);
        } catch (error) {
            console.error(`${this.debugPrefix} Error saving component state:`, error);
        }
    }

    /**
     * Load component state from local storage
     */
    loadComponentState() {
        try {
            const savedState = localStorage.getItem('prometheusComponentState');
            
            if (savedState) {
                const parsedState = JSON.parse(savedState);
                
                // Update state with saved values
                if (parsedState.activeTab) {
                    // Don't update UI here, just update the state object
                    this.state.activeTab = parsedState.activeTab;
                }
                
                if (parsedState.messageDrafts) {
                    this.state.messageDrafts = parsedState.messageDrafts;
                }
                
                // Switch to the active tab from saved state
                if (this.state.activeTab) {
                    window.prometheus_switchTab(this.state.activeTab);
                }
                
                console.log(`${this.debugPrefix} Component state loaded from local storage`);
            }
        } catch (error) {
            console.error(`${this.debugPrefix} Error loading component state:`, error);
        }
    }

    /**
     * Update chat placeholder based on active tab
     */
    updateChatPlaceholder(tabId) {
        try {
            const chatInput = this.container.querySelector('#chat-input');
            if (!chatInput) return;
            
            if (tabId === 'planningchat') {
                chatInput.placeholder = 'Enter planning questions or resource requirements...';
            } else if (tabId === 'teamchat') {
                chatInput.placeholder = 'Enter team chat message...';
            } else {
                chatInput.placeholder = 'Enter chat message, project instructions, or planning queries';
            }
            
            // Restore draft message if available
            if (tabId === 'planningchat' || tabId === 'teamchat') {
                chatInput.value = this.state.messageDrafts[tabId] || '';
            }
        } catch (error) {
            console.error(`${this.debugPrefix} Error updating chat placeholder:`, error);
        }
    }

    /**
     * Load content for the specified tab
     */
    loadTabContent(tabId) {
        console.log(`${this.debugPrefix} Loading content for tab:`, tabId);
        
        try {
            switch (tabId) {
                case 'planning':
                    if (!this.state.projects.length && !this.state.loading.projects) {
                        this.loadProjects();
                    }
                    break;
                    
                case 'timeline':
                    if (this.timelineService) {
                        this.timelineService.refreshTimeline();
                    }
                    break;
                    
                case 'resources':
                    if (!this.state.resources.length && !this.state.loading.resources) {
                        this.loadResources();
                    }
                    break;
                    
                case 'analysis':
                    // Nothing to load automatically
                    break;
                    
                case 'planningchat':
                case 'teamchat':
                    // Focus on input field when switching to chat tabs
                    setTimeout(() => {
                        const chatInput = this.container.querySelector('#chat-input');
                        if (chatInput) chatInput.focus();
                    }, 100);
                    break;
            }
        } catch (error) {
            console.error(`${this.debugPrefix} Error loading tab content:`, error);
        }
    }

    /**
     * Load projects data from service
     */
    async loadProjects() {
        console.log(`${this.debugPrefix} Loading projects`);
        
        try {
            // Update loading state
            this.state.loading.projects = true;
            this.updateLoadingUI('projects', true);
            
            // Clear any previous errors
            this.state.errors.projects = null;
            
            // If service is available, fetch projects
            if (this.service) {
                const projects = await this.service.getProjects();
                this.state.projects = projects;
                console.log(`${this.debugPrefix} Loaded ${projects.length} projects`);
            } else {
                // Use sample projects
                this.state.projects = this.getSampleProjects();
                console.log(`${this.debugPrefix} Loaded sample projects`);
            }
            
            // Render projects
            this.renderProjects();
        } catch (error) {
            console.error(`${this.debugPrefix} Error loading projects:`, error);
            this.state.errors.projects = error.message || 'Failed to load projects';
            this.showError('projects', this.state.errors.projects);
        } finally {
            this.state.loading.projects = false;
            this.updateLoadingUI('projects', false);
        }
    }

    /**
     * Render projects to the UI
     */
    renderProjects() {
        console.log(`${this.debugPrefix} Rendering projects`);
        
        try {
            const projectList = this.container.querySelector('#project-list-items');
            if (!projectList) return;
            
            // Show project list
            projectList.style.display = 'block';
            
            // If no projects, show empty state
            if (!this.state.projects.length) {
                projectList.innerHTML = `
                    <div class="prometheus__empty-state">
                        <p>No projects found</p>
                        <button class="prometheus__button prometheus__button--primary" id="create-project-btn">
                            Create a new project
                        </button>
                    </div>
                `;
                
                // Add event listener to create project button
                const createProjectBtn = projectList.querySelector('#create-project-btn');
                if (createProjectBtn) {
                    createProjectBtn.addEventListener('click', this.handleAddProject);
                }
                
                return;
            }
            
            // Generate project items
            const projectItems = this.state.projects.map(project => this.createProjectItem(project)).join('');
            projectList.innerHTML = projectItems;
            
            // Add event listeners to project actions
            this.state.projects.forEach(project => {
                const viewBtn = projectList.querySelector(`#view-project-${project.id}`);
                const editBtn = projectList.querySelector(`#edit-project-${project.id}`);
                
                if (viewBtn) {
                    viewBtn.addEventListener('click', () => this.handleViewProject(project.id));
                }
                
                if (editBtn) {
                    editBtn.addEventListener('click', () => this.handleEditProject(project.id));
                }
            });
        } catch (error) {
            console.error(`${this.debugPrefix} Error rendering projects:`, error);
        }
    }

    /**
     * Create HTML for a project item
     */
    createProjectItem(project) {
        const statusClass = this.getStatusClass(project.status);
        const progressPercent = project.progress || 0;
        
        // Format dates
        let startDate = 'N/A';
        let endDate = 'N/A';
        
        try {
            if (project.start_date) {
                startDate = new Date(project.start_date).toLocaleDateString();
            }
            
            if (project.end_date) {
                endDate = new Date(project.end_date).toLocaleDateString();
            }
        } catch (e) {
            console.warn(`${this.debugPrefix} Error formatting dates for project ${project.id}:`, e);
        }
        
        return `
            <div class="prometheus__project-item" data-project-id="${project.id}">
                <div class="prometheus__project-status ${statusClass}"></div>
                <div class="prometheus__project-details">
                    <div class="prometheus__project-name">${project.name}</div>
                    <div class="prometheus__project-dates">${startDate} - ${endDate}</div>
                    <div class="prometheus__project-progress">
                        <div class="prometheus__progress-bar">
                            <div class="prometheus__progress-fill" style="width: ${progressPercent}%;"></div>
                        </div>
                        <div class="prometheus__progress-text">${progressPercent}% Complete</div>
                    </div>
                </div>
                <div class="prometheus__project-actions">
                    <button class="prometheus__project-action-btn" id="view-project-${project.id}">View</button>
                    <button class="prometheus__project-action-btn" id="edit-project-${project.id}">Edit</button>
                </div>
            </div>
        `;
    }

    /**
     * Get CSS class for project status
     */
    getStatusClass(status) {
        switch (status) {
            case 'on_track':
                return 'prometheus__project-status--on-track';
            case 'at_risk':
                return 'prometheus__project-status--at-risk';
            case 'delayed':
                return 'prometheus__project-status--delayed';
            default:
                return 'prometheus__project-status--on-track';
        }
    }

    /**
     * Load resources from service
     */
    async loadResources() {
        console.log(`${this.debugPrefix} Loading resources`);
        
        try {
            // Update loading state
            this.state.loading.resources = true;
            this.updateLoadingUI('resources', true);
            
            // Clear any previous errors
            this.state.errors.resources = null;
            
            // If service is available, fetch resources
            if (this.service) {
                const resources = await this.service.getResources();
                this.state.resources = resources;
                console.log(`${this.debugPrefix} Loaded ${resources.length} resources`);
            } else {
                // Use sample resources
                this.state.resources = this.getSampleResources();
                console.log(`${this.debugPrefix} Loaded sample resources`);
            }
            
            // Render resources
            this.renderResources();
        } catch (error) {
            console.error(`${this.debugPrefix} Error loading resources:`, error);
            this.state.errors.resources = error.message || 'Failed to load resources';
            this.showError('resources', this.state.errors.resources);
        } finally {
            this.state.loading.resources = false;
            this.updateLoadingUI('resources', false);
        }
    }

    /**
     * Render resources to the UI
     */
    renderResources() {
        console.log(`${this.debugPrefix} Rendering resources`);
        
        try {
            const resourceAllocation = this.container.querySelector('#resource-allocation');
            if (!resourceAllocation) return;
            
            // Show resource allocation
            resourceAllocation.style.display = 'block';
            
            // If no resources, show empty state
            if (!this.state.resources.length) {
                resourceAllocation.innerHTML = `
                    <div class="prometheus__empty-state">
                        <p>No resources found</p>
                        <button class="prometheus__button prometheus__button--primary" id="create-resource-btn">
                            Add a new resource
                        </button>
                    </div>
                `;
                
                // Add event listener to create resource button
                const createResourceBtn = resourceAllocation.querySelector('#create-resource-btn');
                if (createResourceBtn) {
                    createResourceBtn.addEventListener('click', this.handleAddResource);
                }
                
                return;
            }
            
            // Generate resource allocation chart
            resourceAllocation.innerHTML = `
                <div class="prometheus__chart-container">
                    <h3 class="prometheus__section-title">Resource Allocation</h3>
                    <div class="prometheus__resource-chart">
                        ${this.renderResourceChart()}
                    </div>
                </div>
                
                <div class="prometheus__resource-list">
                    <h3 class="prometheus__section-title">Available Resources</h3>
                    ${this.state.resources.map(resource => this.createResourceItem(resource)).join('')}
                </div>
            `;
        } catch (error) {
            console.error(`${this.debugPrefix} Error rendering resources:`, error);
        }
    }

    /**
     * Create HTML for a resource allocation chart
     */
    renderResourceChart() {
        // This is a simplified placeholder chart
        return `
            <div class="prometheus__chart-placeholder">
                <p>Resource allocation chart would be displayed here</p>
                <p>This would include visualization of resource utilization across projects</p>
            </div>
        `;
    }

    /**
     * Create HTML for a resource item
     */
    createResourceItem(resource) {
        return `
            <div class="prometheus__resource-item" data-resource-id="${resource.id}">
                <div class="prometheus__resource-name">${resource.name}</div>
                <div class="prometheus__resource-type">${resource.type}</div>
                <div class="prometheus__resource-availability">
                    Availability: ${resource.availability || 'Unknown'}
                </div>
            </div>
        `;
    }

    /**
     * Run analysis based on form inputs
     */
    async handleRunAnalysis() {
        console.log(`${this.debugPrefix} Running analysis`);
        
        try {
            // Get form values
            const projectSelect = this.container.querySelector('#analysis-project-select');
            const analysisTypeSelect = this.container.querySelector('#analysis-type-select');
            const includeExternal = this.container.querySelector('#include-external');
            const includeResource = this.container.querySelector('#include-resource');
            
            if (!projectSelect || !analysisTypeSelect) {
                console.error(`${this.debugPrefix} Cannot find analysis form fields`);
                return;
            }
            
            const projectId = projectSelect.value;
            const analysisType = analysisTypeSelect.value;
            const options = {
                includeExternalDependencies: includeExternal?.checked || false,
                includeResourceConstraints: includeResource?.checked || false
            };
            
            if (!projectId) {
                alert('Please select a project for analysis');
                return;
            }
            
            // Update loading state
            this.state.loading.analysis = true;
            this.updateLoadingUI('analysis', true);
            
            // Show the results container
            const resultsContainer = this.container.querySelector('#analysis-result-container');
            if (resultsContainer) {
                resultsContainer.style.display = 'block';
            }
            
            // Clear any previous errors
            this.state.errors.analysis = null;
            
            // Run analysis
            if (this.service) {
                const results = await this.service.runAnalysis(projectId, analysisType, options);
                this.state.analysisResults = results;
                console.log(`${this.debugPrefix} Analysis results:`, results);
            } else {
                // Use sample analysis results after a delay to simulate API call
                await new Promise(resolve => setTimeout(resolve, 1500));
                this.state.analysisResults = this.getSampleAnalysisResults(analysisType);
                console.log(`${this.debugPrefix} Sample analysis results generated`);
            }
            
            // Render analysis results
            this.renderAnalysisResults();
        } catch (error) {
            console.error(`${this.debugPrefix} Error running analysis:`, error);
            this.state.errors.analysis = error.message || 'Failed to run analysis';
            this.showError('analysis', this.state.errors.analysis);
        } finally {
            this.state.loading.analysis = false;
            this.updateLoadingUI('analysis', false);
        }
    }

    /**
     * Render analysis results to the UI
     */
    renderAnalysisResults() {
        console.log(`${this.debugPrefix} Rendering analysis results`);
        
        try {
            const resultsElement = this.container.querySelector('#analysis-results');
            if (!resultsElement) return;
            
            const results = this.state.analysisResults;
            
            if (!results) {
                resultsElement.innerHTML = '<p>No analysis results available</p>';
                return;
            }
            
            // Format results based on analysis type
            let content = '';
            
            if (results.type === 'critical-path') {
                content = `
                    <div class="prometheus__analysis-content">
                        <h4>Critical Path Analysis</h4>
                        <p>${results.summary}</p>
                        
                        <h5>Critical Path Tasks:</h5>
                        <ul class="prometheus__critical-tasks">
                            ${results.critical_path.map(task => `
                                <li class="prometheus__critical-task">
                                    <span class="prometheus__task-name">${task.name}</span>
                                    <span class="prometheus__task-duration">${task.duration} ${task.duration_unit}</span>
                                </li>
                            `).join('')}
                        </ul>
                        
                        <h5>Bottlenecks:</h5>
                        <ul class="prometheus__bottlenecks">
                            ${results.bottlenecks.map(bottleneck => `
                                <li class="prometheus__bottleneck">
                                    <span class="prometheus__bottleneck-desc">${bottleneck.description}</span>
                                    <span class="prometheus__bottleneck-impact">Impact: ${bottleneck.impact}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `;
            } else if (results.type === 'resource-constraints') {
                content = `
                    <div class="prometheus__analysis-content">
                        <h4>Resource Constraints Analysis</h4>
                        <p>${results.summary}</p>
                        
                        <h5>Overallocated Resources:</h5>
                        <ul class="prometheus__resource-issues">
                            ${results.overallocated_resources.map(resource => `
                                <li class="prometheus__resource-issue">
                                    <span class="prometheus__resource-name">${resource.name}</span>
                                    <span class="prometheus__allocation">Allocated: ${resource.allocation}%</span>
                                </li>
                            `).join('')}
                        </ul>
                        
                        <h5>Recommendations:</h5>
                        <ul class="prometheus__recommendations">
                            ${results.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                `;
            } else if (results.type === 'risk-assessment') {
                content = `
                    <div class="prometheus__analysis-content">
                        <h4>Risk Assessment</h4>
                        <p>${results.summary}</p>
                        
                        <h5>Identified Risks:</h5>
                        <ul class="prometheus__risks">
                            ${results.risks.map(risk => `
                                <li class="prometheus__risk prometheus__risk--${risk.severity}">
                                    <span class="prometheus__risk-desc">${risk.description}</span>
                                    <div class="prometheus__risk-metrics">
                                        <span class="prometheus__risk-probability">Probability: ${risk.probability}</span>
                                        <span class="prometheus__risk-impact">Impact: ${risk.impact}</span>
                                    </div>
                                </li>
                            `).join('')}
                        </ul>
                        
                        <h5>Mitigation Strategies:</h5>
                        <ul class="prometheus__mitigations">
                            ${results.mitigation_strategies.map(strategy => `
                                <li class="prometheus__mitigation">
                                    <span class="prometheus__mitigation-desc">${strategy.description}</span>
                                    <span class="prometheus__mitigation-effectiveness">Effectiveness: ${strategy.effectiveness}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `;
            } else {
                content = `
                    <div class="prometheus__analysis-content">
                        <h4>Analysis Results</h4>
                        <p>${results.summary}</p>
                        
                        <h5>Key Findings:</h5>
                        <ul class="prometheus__findings">
                            ${results.findings.map(finding => `<li>${finding}</li>`).join('')}
                        </ul>
                        
                        <h5>Recommendations:</h5>
                        <ul class="prometheus__recommendations">
                            ${results.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
            
            resultsElement.innerHTML = content;
        } catch (error) {
            console.error(`${this.debugPrefix} Error rendering analysis results:`, error);
        }
    }

    /**
     * Clear analysis results
     */
    handleClearAnalysis() {
        console.log(`${this.debugPrefix} Clearing analysis results`);
        
        try {
            // Reset form
            const projectSelect = this.container.querySelector('#analysis-project-select');
            const analysisTypeSelect = this.container.querySelector('#analysis-type-select');
            const includeExternal = this.container.querySelector('#include-external');
            const includeResource = this.container.querySelector('#include-resource');
            
            if (projectSelect) projectSelect.value = '';
            if (analysisTypeSelect) analysisTypeSelect.value = 'critical-path';
            if (includeExternal) includeExternal.checked = false;
            if (includeResource) includeResource.checked = false;
            
            // Clear results
            this.state.analysisResults = null;
            
            // Hide results container
            const resultsContainer = this.container.querySelector('#analysis-result-container');
            if (resultsContainer) {
                resultsContainer.style.display = 'none';
            }
            
            // Clear results content
            const resultsElement = this.container.querySelector('#analysis-results');
            if (resultsElement) {
                resultsElement.innerHTML = '';
            }
        } catch (error) {
            console.error(`${this.debugPrefix} Error clearing analysis:`, error);
        }
    }

    /**
     * Handle sending a chat message
     */
    async handleSendMessage() {
        try {
            const chatInput = this.container.querySelector('#chat-input');
            if (!chatInput) return;
            
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Determine which chat we're in
            const activeTab = this.state.activeTab;
            if (activeTab !== 'planningchat' && activeTab !== 'teamchat') {
                console.warn(`${this.debugPrefix} Cannot send message - not in a chat tab`);
                return;
            }
            
            const chatMessagesContainer = this.container.querySelector(`#${activeTab}-messages`);
            if (!chatMessagesContainer) return;
            
            // Add user message to UI
            const userMessageElement = document.createElement('div');
            userMessageElement.classList.add('prometheus__message', 'prometheus__message--user');
            userMessageElement.innerHTML = `<div class="prometheus__message-content"><div class="prometheus__message-text">${this.escapeHtml(message)}</div></div>`;
            chatMessagesContainer.appendChild(userMessageElement);
            
            // Clear input and saved draft
            chatInput.value = '';
            this.state.messageDrafts[activeTab] = '';
            
            // Scroll to bottom
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
            
            // Get response (from service or mock)
            let responseText = '';
            
            if (this.service) {
                try {
                    const response = await this.service.sendChat(message, activeTab === 'teamchat');
                    responseText = response.content || 'No response received';
                } catch (error) {
                    console.error(`${this.debugPrefix} Error getting chat response:`, error);
                    responseText = 'Sorry, there was an error processing your request.';
                }
            } else {
                // Mock response with delay
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                if (activeTab === 'planningchat') {
                    responseText = this.getMockPlanningChatResponse(message);
                } else {
                    responseText = 'This is a mock team chat response. In a full implementation, this would connect to a shared chat service.';
                }
            }
            
            // Add AI response to UI
            const aiMessageElement = document.createElement('div');
            aiMessageElement.classList.add('prometheus__message', 'prometheus__message--ai');
            aiMessageElement.innerHTML = `<div class="prometheus__message-content"><div class="prometheus__message-text">${responseText}</div></div>`;
            chatMessagesContainer.appendChild(aiMessageElement);
            
            // Scroll to bottom again
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        } catch (error) {
            console.error(`${this.debugPrefix} Error sending message:`, error);
        }
    }

    /**
     * Handle project search
     */
    handleSearchProjects() {
        try {
            const searchInput = this.container.querySelector('#project-search');
            if (!searchInput) return;
            
            const searchTerm = searchInput.value.trim().toLowerCase();
            
            // If empty search term, show all projects
            if (!searchTerm) {
                this.renderProjects();
                return;
            }
            
            // Filter projects
            const filteredProjects = this.state.projects.filter(project => 
                project.name.toLowerCase().includes(searchTerm) || 
                (project.description && project.description.toLowerCase().includes(searchTerm))
            );
            
            // Temporarily update state to render filtered projects
            const allProjects = [...this.state.projects];
            this.state.projects = filteredProjects;
            this.renderProjects();
            
            // Restore full project list in state
            this.state.projects = allProjects;
        } catch (error) {
            console.error(`${this.debugPrefix} Error searching projects:`, error);
        }
    }

    /**
     * Handle adding a new project
     */
    handleAddProject() {
        console.log(`${this.debugPrefix} Add project clicked`);
        
        try {
            // In a full implementation, this would open a modal
            alert('Add project functionality would open a form modal in a full implementation');
        } catch (error) {
            console.error(`${this.debugPrefix} Error handling add project:`, error);
        }
    }

    /**
     * Handle viewing a project
     */
    handleViewProject(projectId) {
        console.log(`${this.debugPrefix} View project clicked for project ${projectId}`);
        
        try {
            // In a full implementation, this would show project details
            alert(`View project ${projectId} functionality would show project details in a full implementation`);
        } catch (error) {
            console.error(`${this.debugPrefix} Error handling view project:`, error);
        }
    }

    /**
     * Handle editing a project
     */
    handleEditProject(projectId) {
        console.log(`${this.debugPrefix} Edit project clicked for project ${projectId}`);
        
        try {
            // In a full implementation, this would open an edit form
            alert(`Edit project ${projectId} functionality would open an edit form in a full implementation`);
        } catch (error) {
            console.error(`${this.debugPrefix} Error handling edit project:`, error);
        }
    }

    /**
     * Handle changing the timeline view
     */
    handleChangeView() {
        try {
            const viewSelect = this.container.querySelector('#timeline-view');
            if (!viewSelect) return;
            
            const view = viewSelect.value;
            console.log(`${this.debugPrefix} Changing timeline view to ${view}`);
            
            // Update timeline view
            if (this.timelineService) {
                this.timelineService.setView(view);
            } else {
                // Just update the placeholder text
                const placeholder = this.container.querySelector('#timeline-placeholder .prometheus__placeholder-text');
                if (placeholder) {
                    placeholder.textContent = `The project timeline would be displayed in ${view} view once loaded.`;
                }
            }
        } catch (error) {
            console.error(`${this.debugPrefix} Error handling change view:`, error);
        }
    }

    /**
     * Handle applying a timeline filter
     */
    handleApplyFilter() {
        try {
            const filterSelect = this.container.querySelector('#timeline-filter');
            if (!filterSelect) return;
            
            const filter = filterSelect.value;
            console.log(`${this.debugPrefix} Applying timeline filter: ${filter}`);
            
            // Apply filter
            if (this.timelineService) {
                this.timelineService.setFilter(filter);
            } else {
                // Just update the placeholder text
                const placeholder = this.container.querySelector('#timeline-placeholder .prometheus__placeholder-text');
                if (placeholder) {
                    placeholder.textContent = `The project timeline would be filtered by "${filter}" once loaded.`;
                }
            }
        } catch (error) {
            console.error(`${this.debugPrefix} Error handling apply filter:`, error);
        }
    }

    /**
     * Handle applying a resource filter
     */
    handleApplyResourceFilter() {
        try {
            const filterSelect = this.container.querySelector('#resource-type-filter');
            if (!filterSelect) return;
            
            const filter = filterSelect.value;
            console.log(`${this.debugPrefix} Applying resource filter: ${filter}`);
            
            // In a full implementation, this would filter the resources
            alert(`Resource filter ${filter} applied. In a full implementation, this would filter the resources.`);
        } catch (error) {
            console.error(`${this.debugPrefix} Error handling apply resource filter:`, error);
        }
    }

    /**
     * Handle adding a new resource
     */
    handleAddResource() {
        console.log(`${this.debugPrefix} Add resource clicked`);
        
        try {
            // In a full implementation, this would open a modal
            alert('Add resource functionality would open a form modal in a full implementation');
        } catch (error) {
            console.error(`${this.debugPrefix} Error handling add resource:`, error);
        }
    }

    /**
     * Update loading UI for a specific section
     */
    updateLoadingUI(section, isLoading) {
        try {
            // Find the loading indicator for the section
            let loadingIndicator;
            
            switch (section) {
                case 'projects':
                    loadingIndicator = this.container.querySelector('#project-list-loading');
                    break;
                case 'resources':
                    loadingIndicator = this.container.querySelector('#resource-list-loading');
                    break;
                case 'timeline':
                    // Timeline doesn't have a specific loading indicator yet
                    break;
                case 'analysis':
                    // Use the results container for analysis loading
                    loadingIndicator = this.container.querySelector('#analysis-results');
                    
                    if (loadingIndicator && isLoading) {
                        loadingIndicator.innerHTML = `
                            <div class="prometheus__loading-indicator">
                                <div class="prometheus__spinner"></div>
                                <div class="prometheus__loading-text">Running analysis...</div>
                            </div>
                        `;
                    }
                    return;
            }
            
            // Update visibility if found
            if (loadingIndicator) {
                loadingIndicator.style.display = isLoading ? 'flex' : 'none';
            }
        } catch (error) {
            console.error(`${this.debugPrefix} Error updating loading UI:`, error);
        }
    }

    /**
     * Show an error message for a specific section
     */
    showError(section, errorMessage) {
        try {
            // Find the container for the section
            let container;
            
            switch (section) {
                case 'projects':
                    container = this.container.querySelector('#project-list-items');
                    break;
                case 'resources':
                    container = this.container.querySelector('#resource-allocation');
                    break;
                case 'timeline':
                    container = this.container.querySelector('#timeline-container');
                    break;
                case 'analysis':
                    container = this.container.querySelector('#analysis-results');
                    break;
            }
            
            // Show error in container if found
            if (container) {
                container.innerHTML = `
                    <div class="prometheus__error">
                        <h3>Error</h3>
                        <p>${errorMessage}</p>
                    </div>
                `;
                
                // Show the container
                container.style.display = 'block';
            }
        } catch (error) {
            console.error(`${this.debugPrefix} Error showing error message:`, error);
        }
    }

    /**
     * Show demo data if service is not available
     */
    showDemoData() {
        console.log(`${this.debugPrefix} Showing demo data`);
        
        try {
            // Load sample projects
            this.state.projects = this.getSampleProjects();
            this.renderProjects();
            
            // Load sample resources
            this.state.resources = this.getSampleResources();
        } catch (error) {
            console.error(`${this.debugPrefix} Error showing demo data:`, error);
        }
    }

    /**
     * Get sample projects for demo mode
     */
    getSampleProjects() {
        return [
            {
                id: 'proj1',
                name: 'Clean Slate UI Sprint',
                description: 'Rebuild UI component architecture',
                status: 'on_track',
                progress: 65,
                start_date: '2025-05-10',
                end_date: '2025-05-17'
            },
            {
                id: 'proj2',
                name: 'Component Integration',
                description: 'Integrate all components with new architecture',
                status: 'at_risk',
                progress: 30,
                start_date: '2025-05-18',
                end_date: '2025-05-25'
            },
            {
                id: 'proj3',
                name: 'Tekton Core Refactoring',
                description: 'Refactor core Tekton services',
                status: 'delayed',
                progress: 15,
                start_date: '2025-05-26',
                end_date: '2025-06-05'
            }
        ];
    }

    /**
     * Get sample resources for demo mode
     */
    getSampleResources() {
        return [
            {
                id: 'res1',
                name: 'Frontend Developers',
                type: 'people',
                availability: '80%'
            },
            {
                id: 'res2',
                name: 'Backend Developers',
                type: 'people',
                availability: '60%'
            },
            {
                id: 'res3',
                name: 'QA Engineers',
                type: 'people',
                availability: '90%'
            },
            {
                id: 'res4',
                name: 'Cloud Infrastructure',
                type: 'equipment',
                availability: '100%'
            }
        ];
    }

    /**
     * Get sample analysis results for demo mode
     */
    getSampleAnalysisResults(analysisType) {
        switch (analysisType) {
            case 'critical-path':
                return {
                    type: 'critical-path',
                    summary: 'Analysis identified 4 tasks on the critical path with a total duration of 14 days. There are 2 major bottlenecks that could impact the project timeline.',
                    critical_path: [
                        { name: 'Design Component Architecture', duration: 3, duration_unit: 'days' },
                        { name: 'Implement Core Framework', duration: 5, duration_unit: 'days' },
                        { name: 'Integration Testing', duration: 4, duration_unit: 'days' },
                        { name: 'Deployment', duration: 2, duration_unit: 'days' }
                    ],
                    bottlenecks: [
                        { description: 'Limited resources for integration testing', impact: 'High' },
                        { description: 'Dependencies on external services', impact: 'Medium' }
                    ]
                };
                
            case 'resource-constraints':
                return {
                    type: 'resource-constraints',
                    summary: 'Analysis identified 2 overallocated resources that could impact project completion. Resource reallocation or timeline adjustment is recommended.',
                    overallocated_resources: [
                        { name: 'Frontend Developers', allocation: 120 },
                        { name: 'QA Engineers', allocation: 110 }
                    ],
                    recommendations: [
                        'Adjust timeline for UI implementation tasks',
                        'Consider bringing in additional QA resources for testing phase',
                        'Redistribute some frontend tasks to backend developers with capacity'
                    ]
                };
                
            case 'risk-assessment':
                return {
                    type: 'risk-assessment',
                    summary: 'Analysis identified 3 significant risks that could impact project success. Mitigation strategies have been suggested for each risk.',
                    risks: [
                        { description: 'Integration issues between components', probability: 'High', impact: 'High', severity: 'high' },
                        { description: 'Performance degradation with new architecture', probability: 'Medium', impact: 'High', severity: 'medium' },
                        { description: 'Delayed delivery of dependencies', probability: 'Medium', impact: 'Medium', severity: 'medium' }
                    ],
                    mitigation_strategies: [
                        { description: 'Implement early integration testing', effectiveness: 'High' },
                        { description: 'Add performance tests to CI pipeline', effectiveness: 'Medium' },
                        { description: 'Create dependency fallback plan', effectiveness: 'Medium' }
                    ]
                };
                
            case 'bottlenecks':
                return {
                    type: 'bottlenecks',
                    summary: 'Analysis identified key bottlenecks in the project workflow that could cause delays if not addressed.',
                    findings: [
                        'Limited QA resources during integration phase',
                        'Single developer with knowledge of core systems',
                        'Approval process for external dependencies',
                        'Limited build server capacity'
                    ],
                    recommendations: [
                        'Cross-train team members on core systems',
                        'Establish parallel QA processes',
                        'Pre-approve common dependencies',
                        'Scale build infrastructure before integration phase'
                    ]
                };
                
            default:
                return {
                    type: 'general',
                    summary: 'General analysis of project status and health.',
                    findings: [
                        'Project is currently on track for scheduled delivery',
                        'Resource allocation appears adequate for current phase',
                        'Some upcoming dependencies may need attention',
                        'Documentation needs improvement for knowledge transfer'
                    ],
                    recommendations: [
                        'Continue with current execution plan',
                        'Review upcoming dependencies in next planning session',
                        'Allocate resources for documentation improvement',
                        'Schedule regular cross-team syncs for better coordination'
                    ]
                };
        }
    }

    /**
     * Get a mock response for the planning chat
     */
    getMockPlanningChatResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        if (lowerMessage.includes('timeline') || lowerMessage.includes('schedule')) {
            return 'Based on the current project plans, the timeline looks manageable but there are some potential bottlenecks in the integration phase. I would recommend allocating additional resources for testing during weeks 3-4 to ensure we stay on track.';
        } else if (lowerMessage.includes('resource') || lowerMessage.includes('allocation')) {
            return 'The current resource allocation shows that frontend developers are overallocated at 120% capacity for the next sprint. Consider either extending the timeline for UI tasks or bringing in additional developers to help with the implementation.';
        } else if (lowerMessage.includes('risk') || lowerMessage.includes('issue')) {
            return 'The main risks identified for the current projects are:<ul><li>Integration issues between components (High)</li><li>Performance degradation with new architecture (Medium)</li><li>Delayed delivery of dependencies (Medium)</li></ul>I recommend prioritizing early integration testing to mitigate the highest risk.';
        } else if (lowerMessage.includes('critical path') || lowerMessage.includes('bottleneck')) {
            return 'The critical path analysis shows that integration testing is currently the biggest bottleneck. This phase depends on multiple component completions and has limited resources allocated. Consider implementing a progressive integration strategy to distribute the testing load more evenly.';
        } else {
            return 'I\'m a planning assistant that can help with project timelines, resource allocation, risk assessment, and critical path analysis. Please ask specific questions about your project plans, resources, or potential issues.';
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize and export the component
window.prometheusComponent = new PrometheusComponent();