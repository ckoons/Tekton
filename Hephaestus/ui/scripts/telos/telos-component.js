/**
 * Telos Component
 * Requirements management interface
 */

console.log('[FILE_TRACE] Loading: telos-component.js');
class TelosComponent {
    constructor() {
        this.state = {
            initialized: false,
            activeTab: 'dashboard', // Default tab is Dashboard
            dashboardLoaded: false,
            requirementsLoaded: false,
            traceabilityLoaded: false,
            validationLoaded: false,
            proposals: [] // Store loaded proposals
        };
    }
    
    /**
     * Initialize the component
     */
    init() {
        console.log('Initializing Telos component');
        if (window.TektonDebug) TektonDebug.info('telosComponent', 'Initializing Telos component');

        // If already initialized, just activate
        if (this.state.initialized) {
            console.log('Telos component already initialized, just activating');
            if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Already initialized, just activating');
            this.activateComponent();
            return this;
        }

        // Initialize component functionality
        // The HTML is already loaded by the component loader
        this.setupEventListeners();
        this.setupChat();

        // Mark as initialized
        this.state.initialized = true;

        console.log('Telos component initialized');
        return this;
    }

    /**
     * Activate the component interface
     */
    activateComponent() {
        console.log('Activating Telos component');

        // Find our component container
        const telosContainer = document.querySelector('.telos');
        if (telosContainer) {
            console.log('Telos container found and activated');
        }
    }
    
    /**
     * Set up event listeners for all UI elements
     */
    setupEventListeners() {
        console.log('[TELOS] Setting up event listeners');
        if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Setting up event listeners');
        
        // Find Telos container with BEM naming
        const container = document.querySelector('.telos');
        if (!container) {
            console.error('[TELOS] Container not found!');
            return;
        }
        
        // Dashboard Tab Event Listeners
        this.setupDashboardTabListeners(container);
        
        // Requirements Tab Event Listeners
        this.setupRequirementsTabListeners(container);
        
        // Traceability Tab Event Listeners
        this.setupTraceabilityTabListeners(container);
        
        // Validation Tab Event Listeners
        this.setupValidationTabListeners(container);
        
        // Set up clear chat button
        const clearChatBtn = container.querySelector('#clear-chat-btn');
        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', () => this.clearActiveChat());
        }

        // Initial placeholder update
        this.updateChatPlaceholder(this.state.activeTab);
    }
    
    /**
     * Set up Dashboard tab event listeners
     */
    setupDashboardTabListeners(container) {
        // New proposal button
        const newProposalBtn = container.querySelector('#new-proposal-btn');
        if (newProposalBtn) {
            newProposalBtn.addEventListener('click', () => {
                console.log('[TELOS] New proposal button clicked');
                alert('New proposal form would be shown here. This will be implemented as a modal dialog.');
            });
        }
        
        // Simple radio button event listeners for each proposal
        const radioButtons = container.querySelectorAll('.telos__proposal-radio');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', (e) => {
                if (e.target.checked) {
                    const label = container.querySelector(`label[for="${e.target.id}"]`);
                    const action = label.textContent.toLowerCase();
                    const proposalCard = e.target.closest('.telos__proposal-card');
                    const proposalName = proposalCard ? proposalCard.dataset.proposalName : '';
                    
                    console.log(`[TELOS] Action: ${action} on proposal: ${proposalName}`);
                    
                    if (action === 'edit') {
                        alert(`Edit "${proposalName}" - This will open an edit form.`);
                    } else if (action === 'remove') {
                        alert(`Remove "${proposalName}" - This will remove the proposal.`);
                    } else if (action === 'sprint') {
                        alert(`Sprint "${proposalName}" - This will initiate a sprint!`);
                    }
                    
                    // Reset radio button
                    e.target.checked = false;
                }
            });
        });
    }
    
    /**
     * Set up Requirements tab event listeners
     */
    setupRequirementsTabListeners(container) {
        // New requirement button
        const newRequirementBtn = container.querySelector('#new-requirement-btn');
        if (newRequirementBtn) {
            newRequirementBtn.addEventListener('click', () => {
                console.log('[TELOS] New requirement button clicked');
                if (window.TektonDebug) TektonDebug.debug('telosComponent', 'New requirement button clicked');
                // In a real implementation, this would show a form to add a new requirement
                alert('Add requirement functionality would be implemented here.');
            });
        }
        
        // Requirements search button
        const requirementSearchBtn = container.querySelector('#requirement-search-btn');
        if (requirementSearchBtn) {
            requirementSearchBtn.addEventListener('click', () => {
                const searchInput = container.querySelector('#requirement-search');
                if (searchInput) {
                    const query = searchInput.value.trim();
                    console.log(`[TELOS] Requirement search executed with query: ${query}`);
                    if (window.TektonDebug) TektonDebug.debug('telosComponent', `Requirement search executed: ${query}`);
                    // Here you would search requirements
                    this.searchRequirements(query);
                }
            });
        }
        
        // Apply filters button
        const applyFiltersBtn = container.querySelector('#apply-filters-btn');
        if (applyFiltersBtn) {
            applyFiltersBtn.addEventListener('click', () => {
                const projectFilter = container.querySelector('#project-filter');
                const statusFilter = container.querySelector('#status-filter');
                const typeFilter = container.querySelector('#type-filter');
                
                const filters = {
                    project: projectFilter ? projectFilter.value : 'all',
                    status: statusFilter ? statusFilter.value : 'all',
                    type: typeFilter ? typeFilter.value : 'all'
                };
                
                console.log(`[TELOS] Applying filters: ${JSON.stringify(filters)}`);
                if (window.TektonDebug) TektonDebug.debug('telosComponent', `Applying filters: ${JSON.stringify(filters)}`);
                
                // Apply the filters to the requirements list
                this.applyRequirementFilters(filters);
            });
        }
        
        // Requirements list action buttons (using event delegation)
        const requirementsList = container.querySelector('#requirements-list');
        if (requirementsList) {
            requirementsList.addEventListener('click', (e) => {
                const actionBtn = e.target.closest('.telos__table-action-btn');
                if (actionBtn) {
                    const row = actionBtn.closest('.telos__requirement-row');
                    const reqId = row ? row.querySelector('td:first-child').textContent : '';
                    const action = actionBtn.textContent.toLowerCase();
                    
                    console.log(`[TELOS] Requirement action: ${action} on requirement: ${reqId}`);
                    if (window.TektonDebug) TektonDebug.debug('telosComponent', `Requirement action: ${action} on ${reqId}`);
                    
                    // Handle different requirement actions
                    if (action === 'view') {
                        alert(`View requirement details for "${reqId}" would be implemented here.`);
                    } else if (action === 'edit') {
                        alert(`Edit requirement functionality for "${reqId}" would be implemented here.`);
                    }
                }
            });
        }
    }
    
    /**
     * Set up Traceability tab event listeners
     */
    setupTraceabilityTabListeners(container) {
        // Trace apply filter button
        const traceApplyFilterBtn = container.querySelector('#trace-apply-filter-btn');
        if (traceApplyFilterBtn) {
            traceApplyFilterBtn.addEventListener('click', () => {
                const projectFilter = container.querySelector('#trace-project-filter');
                const project = projectFilter ? projectFilter.value : 'all';
                
                console.log(`[TELOS] Applying traceability filter for project: ${project}`);
                if (window.TektonDebug) TektonDebug.debug('telosComponent', `Applying traceability filter: ${project}`);
                
                // Apply the filter to the traceability visualization
                this.updateTraceabilityView(project);
            });
        }
        
        // Matrix/Graph view toggle buttons
        const matrixBtn = container.querySelector('#trace-matrix-btn');
        const graphBtn = container.querySelector('#trace-graph-btn');
        
        if (matrixBtn && graphBtn) {
            matrixBtn.addEventListener('click', () => {
                console.log('[TELOS] Switching to matrix view');
                if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Switching to matrix view');
                
                matrixBtn.classList.add('telos__view-button--active');
                graphBtn.classList.remove('telos__view-button--active');
                
                // Update the visualization to matrix view
                this.switchTraceabilityViewMode('matrix');
            });
            
            graphBtn.addEventListener('click', () => {
                console.log('[TELOS] Switching to graph view');
                if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Switching to graph view');
                
                graphBtn.classList.add('telos__view-button--active');
                matrixBtn.classList.remove('telos__view-button--active');
                
                // Update the visualization to graph view
                this.switchTraceabilityViewMode('graph');
            });
        }
    }
    
    /**
     * Set up Validation tab event listeners
     */
    setupValidationTabListeners(container) {
        // Run validation button
        const runValidationBtn = container.querySelector('#run-validation-btn');
        if (runValidationBtn) {
            runValidationBtn.addEventListener('click', () => {
                console.log('[TELOS] Run validation button clicked');
                if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Run validation button clicked');
                
                // Get validation parameters
                const projectSelect = container.querySelector('#validation-project-select');
                const typeSelect = container.querySelector('#validation-type-select');
                const completenessCheck = container.querySelector('#validate-completeness');
                const clarityCheck = container.querySelector('#validate-clarity');
                const consistencyCheck = container.querySelector('#validate-consistency');
                const testabilityCheck = container.querySelector('#validate-testability');
                const feasibilityCheck = container.querySelector('#validate-feasibility');
                
                const params = {
                    project: projectSelect ? projectSelect.value : '',
                    type: typeSelect ? typeSelect.value : 'all',
                    criteria: {
                        completeness: completenessCheck ? completenessCheck.checked : false,
                        clarity: clarityCheck ? clarityCheck.checked : false,
                        consistency: consistencyCheck ? consistencyCheck.checked : false,
                        testability: testabilityCheck ? testabilityCheck.checked : false,
                        feasibility: feasibilityCheck ? feasibilityCheck.checked : false
                    }
                };
                
                console.log(`[TELOS] Running validation with params: ${JSON.stringify(params)}`);
                if (window.TektonDebug) TektonDebug.info('telosComponent', `Running validation: ${JSON.stringify(params)}`);
                
                // Run the validation and display results
                this.runRequirementsValidation(params);
            });
        }
        
        // Reset validation button
        const resetValidationBtn = container.querySelector('#reset-validation-btn');
        if (resetValidationBtn) {
            resetValidationBtn.addEventListener('click', () => {
                console.log('[TELOS] Reset validation form');
                if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Reset validation form');
                
                // Reset form fields
                const projectSelect = container.querySelector('#validation-project-select');
                const typeSelect = container.querySelector('#validation-type-select');
                
                if (projectSelect) projectSelect.value = '';
                if (typeSelect) typeSelect.value = 'all';
                
                // Reset checkboxes to default state
                const checkboxes = container.querySelectorAll('.telos__checkbox');
                checkboxes.forEach(checkbox => {
                    // Completeness, clarity, consistency, testability checked by default
                    const defaultChecked = ['validate-completeness', 'validate-clarity', 
                                            'validate-consistency', 'validate-testability']
                                            .includes(checkbox.id);
                    checkbox.checked = defaultChecked;
                });
                
                // Hide validation results
                const resultContainer = container.querySelector('#validation-result-container');
                if (resultContainer) {
                    resultContainer.style.display = 'none';
                }
            });
        }
    }
    
    /**
     * Set up chat functionality
     */
    setupChat() {
        console.log('[TELOS] Setting up chat');
        if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Setting up chat');

        // Find Telos container with BEM naming
        const container = document.querySelector('.telos');
        if (!container) {
            console.error('[TELOS] Container not found!');
            return;
        }

        // Use scoped queries with container
        const input = container.querySelector('#chat-input');
        const button = container.querySelector('#send-button');

        if (!input || !button) {
            console.error('[TELOS] Missing chat input elements');
            return;
        }

        // Send message on button click
        button.addEventListener('click', () => {
            const message = input.value.trim();
            if (!message) return;

            // Determine which chat container to use based on active tab
            let messagesContainer;
            let responsePrefix = '';

            if (this.state.activeTab === 'teamchat') {
                messagesContainer = container.querySelector('#teamchat-messages');
                responsePrefix = 'Team Chat: ';
            } else if (this.state.activeTab === 'reqchat') {
                messagesContainer = container.querySelector('#reqchat-messages');
                responsePrefix = 'Requirements: ';
            } else {
                // Default to reqchat for all other tabs
                messagesContainer = container.querySelector('#reqchat-messages');
                responsePrefix = 'Requirements: ';
                
                // Switch to reqchat tab if we're on a different tab
                if (this.state.activeTab !== 'reqchat') {
                    console.log('[TELOS] Auto-switching to requirements chat tab');
                    if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Auto-switching to requirements chat tab');
                    window.telos_switchTab('reqchat');
                }
            }

            if (!messagesContainer) {
                console.error('[TELOS] Chat messages container not found');
                return;
            }

            // Add user message to chat
            this.addUserMessageToChatUI(messagesContainer, message);

            // Clear input immediately for better UX
            input.value = '';

            // Send message via aish MCP
            this.sendChatMessage(message, this.state.activeTab)
                .then(response => {
                    // Add AI response to chat
                    this.addAIMessageToChatUI(messagesContainer, response);
                })
                .catch(error => {
                    console.error('[TELOS] Chat error:', error);
                    // Show error message
                    this.addAIMessageToChatUI(messagesContainer, 
                        `Error: ${error.message || 'Failed to send message. Please try again.'}`);
                });
        });

        // Send message on Enter key (but allow Shift+Enter for new lines)
        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                button.click();
            }
        });
    }
    
    /**
     * Update chat input placeholder based on active tab
     * @param {string} activeTab - The currently active tab
     */
    updateChatPlaceholder(activeTab) {
        // Find Telos container with BEM naming
        const container = document.querySelector('.telos');
        if (!container) return;

        // Get the chat input within our container with BEM class
        const chatInput = container.querySelector('.telos__chat-input');
        if (!chatInput) return;

        switch(activeTab) {
            case 'dashboard':
                chatInput.placeholder = "Ask about proposals, sprint planning, or development ideas...";
                break;
            case 'requirements':
                chatInput.placeholder = "Ask about requirements, filtering, or specific requirements...";
                break;
            case 'traceability':
                chatInput.placeholder = "Ask about requirement relationships, dependencies, or impact analysis...";
                break;
            case 'validation':
                chatInput.placeholder = "Ask about requirements validation, quality criteria, or standards...";
                break;
            case 'reqchat':
                chatInput.placeholder = "Enter chat message for requirements engineering assistance";
                break;
            case 'teamchat':
                chatInput.placeholder = "Enter team chat message for all Tekton components";
                break;
            default:
                chatInput.placeholder = "Enter message...";
        }
    }
    
    /**
     * Load content specific to a tab
     * @param {string} tabId - The ID of the tab to load content for
     */
    loadTabContent(tabId) {
        console.log(`[TELOS] Loading content for ${tabId} tab`);
        if (window.TektonDebug) TektonDebug.debug('telosComponent', `Loading content for ${tabId} tab`);

        switch (tabId) {
            case 'dashboard':
                // Dashboard content is already in HTML
                break;
            case 'requirements':
                if (!this.state.requirementsLoaded) {
                    this.loadRequirements();
                    this.state.requirementsLoaded = true;
                }
                break;
            case 'traceability':
                if (!this.state.traceabilityLoaded) {
                    this.initializeTraceability();
                    this.state.traceabilityLoaded = true;
                }
                break;
            case 'validation':
                if (!this.state.validationLoaded) {
                    this.setupValidation();
                    this.state.validationLoaded = true;
                }
                break;
            case 'reqchat':
            case 'teamchat':
                // Chat is loaded by setupChat
                break;
        }
    }
    
    /**
     * Load projects for the projects panel
     */
    loadProjects() {
        console.log('[TELOS] Loading projects');
        if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Loading projects');
        
        const projectList = document.getElementById('project-list');
        const loading = document.getElementById('project-list-loading');
        
        if (projectList && loading) {
            // Show loading indicator
            loading.style.display = 'flex';
            projectList.style.display = 'none';
            
            // Simulate loading time
            setTimeout(() => {
                // Hide loading indicator, show project list
                loading.style.display = 'none';
                projectList.style.display = 'block';
                
                console.log('[TELOS] Projects loaded');
                if (window.TektonDebug) TektonDebug.info('telosComponent', 'Projects loaded successfully');
            }, 1200);
        }
    }
    
    /**
     * Load requirements for the requirements panel
     */
    loadRequirements() {
        console.log('[TELOS] Loading requirements');
        if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Loading requirements');
        
        const requirementsList = document.getElementById('requirements-list');
        const loading = document.getElementById('requirements-list-loading');
        
        if (requirementsList && loading) {
            // Show loading indicator
            loading.style.display = 'flex';
            requirementsList.style.display = 'none';
            
            // Simulate loading time
            setTimeout(() => {
                // Hide loading indicator, show requirements list
                loading.style.display = 'none';
                requirementsList.style.display = 'block';
                
                console.log('[TELOS] Requirements loaded');
                if (window.TektonDebug) TektonDebug.info('telosComponent', 'Requirements loaded successfully');
            }, 1500);
        }
    }
    
    /**
     * Initialize the traceability visualization
     */
    initializeTraceability() {
        console.log('[TELOS] Initializing traceability visualization');
        if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Initializing traceability visualization');
        
        // For now, just update the placeholder
        const placeholder = document.querySelector('.telos__trace-placeholder');
        if (placeholder) {
            placeholder.innerHTML = `
                <div class="telos__placeholder-content">
                    <h3 class="telos__placeholder-title">Traceability Matrix</h3>
                    <p class="telos__placeholder-text">Select a project and visualization type to view traceability information.</p>
                    <p>In a real implementation, this would show a matrix or graph visualization of requirement relationships.</p>
                </div>
            `;
        }
    }
    
    /**
     * Initialize the validation panel
     */
    setupValidation() {
        console.log('[TELOS] Setting up validation panel');
        if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Setting up validation panel');
        
        // Nothing to do here for the initial setup
        // The form is already in the HTML and event listeners are set in setupValidationTabListeners
    }
    
    /**
     * Search projects by name
     * @param {string} query - Search query for projects
     */
    searchProjects(query) {
        console.log(`[TELOS] Searching projects with query: ${query}`);
        if (window.TektonDebug) TektonDebug.debug('telosComponent', `Searching projects: ${query}`);
        
        // In a real implementation, this would filter the projects list
        // For now, we'll just log the query
        if (query) {
            alert(`Search for projects matching "${query}" would be implemented here.`);
        }
    }
    
    /**
     * View a specific project
     * @param {string} projectName - Name of the project to view
     */
    viewProject(projectName) {
        console.log(`[TELOS] Viewing project: ${projectName}`);
        if (window.TektonDebug) TektonDebug.debug('telosComponent', `Viewing project: ${projectName}`);
        
        // Switch to requirements tab
        window.telos_switchTab('requirements');
        
        // Select the project in the filter dropdown
        const projectFilter = document.querySelector('#project-filter');
        if (projectFilter) {
            // Find option that matches the project name
            const options = Array.from(projectFilter.options);
            const matchingOption = options.find(option => 
                option.text.toLowerCase() === projectName.toLowerCase());
            
            if (matchingOption) {
                projectFilter.value = matchingOption.value;
                
                // Trigger the filter button click
                const applyFiltersBtn = document.querySelector('#apply-filters-btn');
                if (applyFiltersBtn) {
                    applyFiltersBtn.click();
                }
            }
        }
    }
    
    /**
     * Search requirements by keyword
     * @param {string} query - Search query for requirements
     */
    searchRequirements(query) {
        console.log(`[TELOS] Searching requirements with query: ${query}`);
        if (window.TektonDebug) TektonDebug.debug('telosComponent', `Searching requirements: ${query}`);
        
        // In a real implementation, this would filter the requirements list
        // For now, we'll just log the query
        if (query) {
            alert(`Search for requirements matching "${query}" would be implemented here.`);
        }
    }
    
    /**
     * Apply filters to the requirements list
     * @param {Object} filters - Filter criteria
     */
    applyRequirementFilters(filters) {
        console.log(`[TELOS] Applying filters to requirements: ${JSON.stringify(filters)}`);
        if (window.TektonDebug) TektonDebug.info('telosComponent', `Applying filters: ${JSON.stringify(filters)}`);
        
        // In a real implementation, this would filter the requirements table
        // For now, we'll just log the filters
        alert(`Filtering requirements with: ${JSON.stringify(filters)} would be implemented here.`);
    }
    
    /**
     * Update the traceability visualization based on selected project
     * @param {string} project - Project ID to filter by
     */
    updateTraceabilityView(project) {
        console.log(`[TELOS] Updating traceability view for project: ${project}`);
        if (window.TektonDebug) TektonDebug.debug('telosComponent', `Updating traceability for: ${project}`);
        
        // In a real implementation, this would update the visualization
        // For now, we'll just update the placeholder
        const placeholder = document.querySelector('.telos__trace-placeholder');
        if (placeholder) {
            if (project === 'all') {
                placeholder.innerHTML = `
                    <div class="telos__placeholder-content">
                        <h3 class="telos__placeholder-title">All Projects Traceability</h3>
                        <p class="telos__placeholder-text">Showing traceability for all projects would be implemented here.</p>
                    </div>
                `;
            } else {
                placeholder.innerHTML = `
                    <div class="telos__placeholder-content">
                        <h3 class="telos__placeholder-title">${project} Traceability</h3>
                        <p class="telos__placeholder-text">Showing traceability for ${project} would be implemented here.</p>
                    </div>
                `;
            }
        }
    }
    
    /**
     * Switch between matrix and graph view modes for traceability
     * @param {string} mode - View mode ('matrix' or 'graph')
     */
    switchTraceabilityViewMode(mode) {
        console.log(`[TELOS] Switching traceability view mode to: ${mode}`);
        if (window.TektonDebug) TektonDebug.debug('telosComponent', `Switching traceability view to: ${mode}`);
        
        // In a real implementation, this would switch between visualization types
        // For now, we'll just update the placeholder
        const placeholder = document.querySelector('.telos__trace-placeholder');
        if (placeholder) {
            const title = placeholder.querySelector('.telos__placeholder-title');
            const text = placeholder.querySelector('.telos__placeholder-text');
            
            if (title && text) {
                if (mode === 'matrix') {
                    title.textContent = 'Traceability Matrix View';
                    text.textContent = 'Matrix view for requirement traceability would be displayed here.';
                } else if (mode === 'graph') {
                    title.textContent = 'Traceability Graph View';
                    text.textContent = 'Interactive graph visualization for requirement relationships would be displayed here.';
                }
            }
        }
    }
    
    /**
     * Run requirements validation with specified parameters
     * @param {Object} params - Validation parameters
     */
    runRequirementsValidation(params) {
        console.log(`[TELOS] Running requirements validation with params: ${JSON.stringify(params)}`);
        if (window.TektonDebug) TektonDebug.info('telosComponent', `Validating requirements: ${JSON.stringify(params)}`);
        
        // In a real implementation, this would perform validation against the criteria
        // For now, we'll simulate a validation result
        
        const resultContainer = document.getElementById('validation-result-container');
        const resultsDiv = document.getElementById('validation-results');
        
        if (resultContainer && resultsDiv) {
            // Show the results container
            resultContainer.style.display = 'block';
            
            // Clear previous results
            resultsDiv.innerHTML = '';
            
            // Add loading message
            resultsDiv.innerHTML = '<div class="telos__loading-text">Validating requirements...</div>';
            
            // Simulate validation processing time
            setTimeout(() => {
                // Create validation results
                let resultsHtml = '';
                
                if (!params.project) {
                    resultsHtml = `
                        <div class="telos__validation-error">
                            Please select a project to validate.
                        </div>
                    `;
                } else {
                    const criteriaList = Object.entries(params.criteria)
                        .filter(([_, enabled]) => enabled)
                        .map(([name, _]) => name)
                        .join(', ');
                    
                    // Create sample validation results
                    resultsHtml = `
                        <div class="telos__validation-summary">
                            <div class="telos__validation-header">
                                <h3>Validation Results for ${params.project}</h3>
                                <p>Validated against: ${criteriaList}</p>
                            </div>
                            <div class="telos__validation-stats">
                                <div class="telos__validation-stat">
                                    <div class="telos__stat-label">Total Requirements</div>
                                    <div class="telos__stat-value">24</div>
                                </div>
                                <div class="telos__validation-stat">
                                    <div class="telos__stat-label">Passed</div>
                                    <div class="telos__stat-value">18</div>
                                </div>
                                <div class="telos__validation-stat">
                                    <div class="telos__stat-label">Issues</div>
                                    <div class="telos__stat-value">6</div>
                                </div>
                            </div>
                            <div class="telos__validation-details">
                                <h4>Issues Found:</h4>
                                <ul>
                                    <li>REQ-003: Missing acceptance criteria (Completeness)</li>
                                    <li>REQ-007: Ambiguous wording (Clarity)</li>
                                    <li>REQ-012: Conflicts with REQ-009 (Consistency)</li>
                                    <li>REQ-015: Not verifiable (Testability)</li>
                                    <li>REQ-018: Missing priority (Completeness)</li>
                                    <li>REQ-022: Too technical for business requirement (Clarity)</li>
                                </ul>
                            </div>
                        </div>
                    `;
                }
                
                // Update results
                resultsDiv.innerHTML = resultsHtml;
            }, 2000);
        }
    }
    
    /**
     * Add a user message to the chat UI
     * @param {HTMLElement} messages - The messages container element
     * @param {string} message - The message text
     */
    addUserMessageToChatUI(messages, message) {
        if (!messages) return;

        const userBubble = document.createElement('div');
        userBubble.className = 'telos__message telos__message--user';
        userBubble.textContent = message;
        messages.appendChild(userBubble);
        messages.scrollTop = messages.scrollHeight;
    }

    /**
     * Add an AI message to the chat UI
     * @param {HTMLElement} messages - The messages container element
     * @param {string} message - The message text
     */
    addAIMessageToChatUI(messages, message) {
        if (!messages) return;

        const aiBubble = document.createElement('div');
        aiBubble.className = 'telos__message telos__message--ai';
        aiBubble.textContent = message;
        messages.appendChild(aiBubble);
        messages.scrollTop = messages.scrollHeight;
    }
    
    /**
     * Clear the active chat messages
     */
    clearActiveChat() {
        console.log('[TELOS] Clearing active chat');
        if (window.TektonDebug) TektonDebug.debug('telosComponent', 'Clearing active chat');
        
        // Find Telos container with BEM naming
        const container = document.querySelector('.telos');
        if (!container) return;

        let messagesContainer;

        // Determine which chat is active
        if (this.state.activeTab === 'reqchat') {
            messagesContainer = container.querySelector('#reqchat-messages');
        } else if (this.state.activeTab === 'teamchat') {
            messagesContainer = container.querySelector('#teamchat-messages');
        }

        if (messagesContainer) {
            // Keep only the welcome message (system message with BEM class)
            const welcomeMessage = messagesContainer.querySelector('.telos__message--system');
            messagesContainer.innerHTML = '';
            if (welcomeMessage) {
                messagesContainer.appendChild(welcomeMessage);
            }
        }
    }
    
    /**
     * Edit a proposal
     */
    editProposal(proposalCard) {
        const proposalName = proposalCard.dataset.proposalName;
        const titleElement = proposalCard.querySelector('.telos__proposal-title');
        const descElement = proposalCard.querySelector('.telos__proposal-description');
        
        // For now, use prompt for simple editing
        const currentTitle = titleElement.textContent;
        const currentDesc = descElement.textContent;
        
        const newTitle = prompt('Edit proposal title:', currentTitle);
        if (newTitle && newTitle !== currentTitle) {
            titleElement.textContent = newTitle;
        }
        
        const newDesc = prompt('Edit proposal description:', currentDesc);
        if (newDesc && newDesc !== currentDesc) {
            descElement.textContent = newDesc;
        }
        
        console.log(`[TELOS] Edited proposal: ${proposalName}`);
    }
    
    /**
     * Remove a proposal
     */
    removeProposal(proposalCard) {
        const proposalName = proposalCard.dataset.proposalName;
        
        // Add fade-out animation
        proposalCard.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        proposalCard.style.opacity = '0';
        proposalCard.style.transform = 'scale(0.9)';
        
        // Remove after animation
        setTimeout(() => {
            proposalCard.remove();
            console.log(`[TELOS] Removed proposal: ${proposalName}`);
            
            // Check if no proposals left
            const proposalsGrid = document.getElementById('proposals-grid');
            if (proposalsGrid && proposalsGrid.children.length === 0) {
                proposalsGrid.innerHTML = `
                    <div class="telos__empty-state">
                        <h3>No proposals yet</h3>
                        <p>Click "New Proposal" to create your first development sprint proposal.</p>
                    </div>
                `;
            }
        }, 300);
    }
    
    /**
     * Initiate sprint from proposal
     */
    async initiateSprintFromProposal(proposalName, proposalCard) {
        console.log(`[TELOS] Initiating sprint for proposal: ${proposalName}`);
        
        // Get proposal data from card
        const proposalData = {
            name: proposalName,
            title: proposalCard.querySelector('.telos__proposal-title').textContent,
            description: proposalCard.querySelector('.telos__proposal-description').textContent,
            status: proposalCard.querySelector('.telos__proposal-status').textContent
        };
        
        try {
            // Create workflow message
            const workflowMessage = {
                purpose: {
                    "telos": "initiate sprint",
                    "prometheus": "analyze proposal"
                },
                dest: "prometheus",
                payload: {
                    action: "process_sprint",
                    sprint_name: `${proposalName}_Sprint`,
                    proposal: proposalData
                }
            };
            
            // For now, simulate the workflow trigger
            console.log('[TELOS] Workflow message:', workflowMessage);
            
            // Update the proposal card to show it's being processed
            const statusElement = proposalCard.querySelector('.telos__proposal-status');
            statusElement.textContent = 'processing';
            statusElement.style.backgroundColor = 'var(--telos-warning)';
            statusElement.style.color = 'white';
            
            // Simulate workflow processing
            setTimeout(() => {
                statusElement.textContent = 'sprint initiated';
                statusElement.style.backgroundColor = 'var(--telos-info)';
                alert(`Sprint successfully initiated for "${proposalName}"!\n\nThe Planning Team CIs will now process this proposal.`);
            }, 2000);
            
        } catch (error) {
            console.error('[TELOS] Error initiating sprint:', error);
            alert('Error initiating sprint. Please try again.');
        }
    }
}

// Create global instance
window.telosComponent = new TelosComponent();

// Add handler to component activation
document.addEventListener('DOMContentLoaded', function() {
    const telosTab = document.querySelector('.nav-item[data-component="telos"]');
    if (telosTab) {
        telosTab.addEventListener('click', function() {
            // First, make sure the HTML panel is visible
            const htmlPanel = document.getElementById('html-panel');
            if (htmlPanel) {
                // Make it active and visible
                const panels = document.querySelectorAll('.panel');
                panels.forEach(panel => {
                    panel.classList.remove('active');
                    panel.style.display = 'none';
                });
                htmlPanel.classList.add('active');
                htmlPanel.style.display = 'block';
            }
            
            // Initialize component if not already done
            if (window.telosComponent) {
                window.telosComponent.init();
            }
        });
    }
});

// Global tab switching function
window.telos_switchTab = function(tabName) {
    console.log(`[TELOS] Switching to tab: ${tabName}`);
    
    // Update tab states
    const tabs = document.querySelectorAll('.telos__tab');
    tabs.forEach(tab => {
        if (tab.getAttribute('data-tab') === tabName) {
            tab.classList.add('telos__tab--active');
        } else {
            tab.classList.remove('telos__tab--active');
        }
    });
    
    // Update panel visibility
    const panels = document.querySelectorAll('.telos__panel');
    panels.forEach(panel => {
        const panelId = panel.id;
        if (panelId === `${tabName}-panel`) {
            panel.classList.add('telos__panel--active');
        } else {
            panel.classList.remove('telos__panel--active');
        }
    });
    
    // Handle clear button visibility for chat tabs
    const clearButton = document.getElementById('clear-chat-btn');
    if (clearButton) {
        if (tabName === 'reqchat' || tabName === 'teamchat') {
            clearButton.style.display = 'block';
        } else {
            clearButton.style.display = 'none';
        }
    }
    
    // Update component state and load content
    if (window.telosComponent) {
        window.telosComponent.state.activeTab = tabName;
        window.telosComponent.updateChatPlaceholder(tabName);
        window.telosComponent.loadTabContent(tabName);
    }
};

// Global clear chat function
window.telos_clearChat = function() {
    console.log('[TELOS] Clearing chat');
    
    // Find active chat panel
    const activePanel = document.querySelector('.telos__panel--active');
    if (activePanel) {
        const chatMessages = activePanel.querySelector('.chat-messages');
        if (chatMessages) {
            // Keep the system message, remove others
            const systemMessage = chatMessages.querySelector('.system-message');
            chatMessages.innerHTML = '';
            if (systemMessage) {
                chatMessages.appendChild(systemMessage);
            }
        }
    }
};