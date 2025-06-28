/**
 * GitHub Panel Initialization for Tekton Dashboard
 * Sets up the GitHub panel and initializes its functionality
 */

console.log('[FILE_TRACE] Loading: github-panel-init.js');
(function() {
    // Create initialization function for the GitHub panel
    window.tektonUI = window.tektonUI || {};
    
    window.tektonUI.initGitHubPanel = function(dashboardComponent) {
        // Create a helper to create a component-like object for the GitHub panel
        function createGitHubComponent(dashboardComponent) {
            // Create a sub-component with its own utils but shared state manager
            const githubComponent = {
                // Reference to parent dashboard component
                dashboard: dashboardComponent,
                
                // Element selection helpers (scoped to GitHub panel)
                $: function(selector) {
                    return dashboardComponent.root.querySelector('#github-panel-container ' + selector);
                },
                
                $$: function(selector) {
                    return Array.from(dashboardComponent.root.querySelectorAll('#github-panel-container ' + selector));
                },
                
                // Inherit utils from dashboard component
                utils: dashboardComponent.utils,
                
                // Event handling helper
                on: function(eventType, selector, handler) {
                    const container = dashboardComponent.root.querySelector('#github-panel-container');
                    if (!container) return;
                    
                    container.addEventListener(eventType, function(event) {
                        // Find if the event target matches the selector
                        const matchingElements = Array.from(container.querySelectorAll(selector));
                        const eventTarget = event.target;
                        
                        // Check if the event target or any of its parents match the selector
                        let currentElement = eventTarget;
                        while (currentElement && currentElement !== container) {
                            if (matchingElements.includes(currentElement)) {
                                handler.call(currentElement, event);
                                break;
                            }
                            currentElement = currentElement.parentElement;
                        }
                    });
                },
                
                // Get parent dashboard component's root element
                get root() {
                    return dashboardComponent.root;
                },
                
                // Register cleanup function
                registerCleanup: function(cleanupFn) {
                    // Use parent component's cleanup mechanism
                    dashboardComponent.utils.lifecycle.registerCleanupTask(dashboardComponent, cleanupFn);
                },
                
                // Method to show notifications
                showNotification: function(title, message, type = 'info', duration = 3000) {
                    const notificationsContainer = this.$('#github-notifications');
                    if (!notificationsContainer) return;
                    
                    return this.utils.componentUtils.notifications.show(
                        {root: this.root, $: this.$, $$: this.$$}, 
                        title, 
                        message, 
                        type, 
                        duration
                    );
                }
            };
            
            return githubComponent;
        }
        
        // Create GitHub component
        const component = createGitHubComponent(dashboardComponent);
        
        // Initialize GitHub panel with state management
        if (window.tektonUI.stateManager) {
            component.utils.componentState.connect(component, {
                namespace: 'githubPanel',
                initialState: {
                    activeTab: 'repositories',
                    authenticated: false,
                    currentUser: null,
                    repositories: {
                        items: [],
                        loading: false,
                        page: 1,
                        filter: {
                            type: 'all',
                            query: '',
                            language: 'all'
                        }
                    },
                    issues: {
                        items: {},
                        loading: false,
                        page: 1,
                        filter: {
                            repository: 'all',
                            state: 'open',
                            query: ''
                        }
                    },
                    pullRequests: {
                        items: {},
                        loading: false,
                        page: 1,
                        filter: {
                            repository: 'all',
                            state: 'open',
                            query: ''
                        }
                    },
                    projectLinks: {
                        items: [],
                        loading: false
                    },
                    settings: {
                        enterpriseUrl: '',
                        webhookSecret: '',
                        autoSyncFrequency: 0
                    },
                    modalState: {
                        repositoryDetail: {
                            isOpen: false,
                            repository: null,
                            activeTab: 'repo-overview'
                        },
                        createRepository: {
                            isOpen: false
                        },
                        createIssue: {
                            isOpen: false
                        },
                        issueDetail: {
                            isOpen: false,
                            issue: null
                        },
                        pullRequestDetail: {
                            isOpen: false,
                            pullRequest: null,
                            activeTab: 'pr-overview'
                        },
                        linkRepository: {
                            isOpen: false,
                            repository: null
                        },
                        cloneRepository: {
                            isOpen: false,
                            repository: null
                        },
                        cloneProgress: {
                            isOpen: false,
                            progress: 0,
                            status: ''
                        },
                        githubAuth: {
                            isOpen: false
                        }
                    },
                    cloneOperations: {},
                    languages: []
                },
                persist: true,
                persistenceType: 'localStorage'
            });
        }
        
        // Cache elements
        const elements = {};
        
        // Cache tab buttons
        const tabButtons = component.$$('.github-tabs .tekton-dashboard__tab-button');
        tabButtons.forEach(btn => {
            const tabId = btn.getAttribute('data-tab');
            elements.tabs = elements.tabs || {};
            elements.tabs[tabId] = btn;
        });
        
        // Cache tab panels
        const tabPanels = component.$$('.github-tab-content .tekton-dashboard__tab-panel');
        tabPanels.forEach(panel => {
            const panelId = panel.getAttribute('data-panel');
            elements.panels = elements.panels || {};
            elements.panels[panelId] = panel;
        });
        
        // Make elements available to the component
        component.elements = elements;
        
        // Set up event handlers
        if (component.handlers && component.handlers.github && component.handlers.github.setupEventHandlers) {
            component.handlers.github.setupEventHandlers();
        } else {
            console.error('GitHub panel handlers not available');
        }
        
        // Set up tabs functionality
        setupTabs(component);
        
        // Initialize the GitHub service
        initGitHubService(component);
        
        // Check authentication and load initial data
        checkAuthentication(component);
        
        console.log('GitHub panel initialized');
    };
    
    /**
     * Set up tabs functionality for GitHub panel
     * @param {Object} component - GitHub panel component
     */
    function setupTabs(component) {
        // Add click handlers to tab buttons
        component.on('click', '.github-tabs .tekton-dashboard__tab-button', (event) => {
            const tabId = event.target.closest('.tekton-dashboard__tab-button').getAttribute('data-tab');
            
            // Update active tab in state
            component.state.set('activeTab', tabId);
            
            // Update active tab UI
            component.$$('.github-tabs .tekton-dashboard__tab-button').forEach(tab => {
                tab.classList.remove('tekton-dashboard__tab-button--active');
            });
            
            event.target.closest('.tekton-dashboard__tab-button').classList.add('tekton-dashboard__tab-button--active');
            
            // Update active panel UI
            component.$$('.github-tab-content .tekton-dashboard__tab-panel').forEach(panel => {
                panel.classList.remove('tekton-dashboard__tab-panel--active');
            });
            
            const activePanel = component.$(`.github-tab-content .tekton-dashboard__tab-panel[data-panel="${tabId}"]`);
            if (activePanel) {
                activePanel.classList.add('tekton-dashboard__tab-panel--active');
            }
        });
        
        // Set initial active tab from state
        const activeTab = component.state.get('activeTab');
        const activeTabButton = component.$(`.github-tabs .tekton-dashboard__tab-button[data-tab="${activeTab}"]`);
        const activePanel = component.$(`.github-tab-content .tekton-dashboard__tab-panel[data-panel="${activeTab}"]`);
        
        if (activeTabButton && activePanel) {
            activeTabButton.classList.add('tekton-dashboard__tab-button--active');
            activePanel.classList.add('tekton-dashboard__tab-panel--active');
        }
    }
    
    /**
     * Initialize GitHub service
     * @param {Object} component - GitHub panel component
     */
    function initGitHubService(component) {
        // Check if GitHub service is available
        if (window.tektonUI.services && window.tektonUI.services.githubService) {
            // Service already initialized
            console.log('GitHub service already initialized');
        } else if (window.GitHubService) {
            // Initialize service
            const githubService = new window.GitHubService();
            
            // Register service
            window.tektonUI = window.tektonUI || {};
            window.tektonUI.services = window.tektonUI.services || {};
            window.tektonUI.services.githubService = githubService;
            
            console.log('GitHub service initialized');
        } else {
            console.error('GitHub service class not found');
            component.showNotification('Error', 'GitHub service not available', 'error');
        }
    }
    
    /**
     * Check authentication status and load initial data
     * @param {Object} component - GitHub panel component
     */
    function checkAuthentication(component) {
        const githubService = window.tektonUI.services?.githubService;
        if (!githubService) {
            console.error('GitHub service not available for authentication check');
            return;
        }
        
        // Check if already authenticated in state
        const authenticated = component.state.get('authenticated');
        const currentUser = component.state.get('currentUser');
        
        if (authenticated && currentUser) {
            // Update UI with authentication status
            if (component.ui && component.ui.github) {
                component.ui.github.updateAuthStatus(authenticated, currentUser);
            }
            
            // Load initial data
            loadInitialData(component);
        } else {
            // Try to connect and authenticate
            githubService.connect()
                .then(connected => {
                    if (connected) {
                        // Get current user
                        const user = githubService.currentUser;
                        
                        // Update state
                        component.state.set({
                            authenticated: true,
                            currentUser: user
                        });
                        
                        // Update UI
                        if (component.ui && component.ui.github) {
                            component.ui.github.updateAuthStatus(true, user);
                        }
                        
                        // Load initial data
                        loadInitialData(component);
                    } else {
                        // Not authenticated
                        component.state.set({
                            authenticated: false,
                            currentUser: null
                        });
                        
                        // Update UI
                        if (component.ui && component.ui.github) {
                            component.ui.github.updateAuthStatus(false);
                        }
                    }
                })
                .catch(error => {
                    console.error('Error checking authentication:', error);
                    
                    // Update state
                    component.state.set({
                        authenticated: false,
                        currentUser: null
                    });
                    
                    // Update UI
                    if (component.ui && component.ui.github) {
                        component.ui.github.updateAuthStatus(false);
                    }
                });
        }
    }
    
    /**
     * Load initial data for GitHub panel
     * @param {Object} component - GitHub panel component
     */
    function loadInitialData(component) {
        // Get active tab
        const activeTab = component.state.get('activeTab');
        
        // Load data based on active tab
        switch (activeTab) {
            case 'repositories':
                loadRepositories(component);
                break;
            case 'project-links':
                loadProjectLinks(component);
                break;
            case 'issues':
                loadIssues(component);
                break;
            case 'pull-requests':
                loadPullRequests(component);
                break;
            case 'settings':
                loadSettings(component);
                break;
        }
    }
    
    /**
     * Load repositories data
     * @param {Object} component - GitHub panel component
     */
    function loadRepositories(component) {
        // Check if authenticated
        if (!component.state.get('authenticated')) {
            return;
        }
        
        // Set loading state
        component.state.set('repositories.loading', true);
        
        // Get GitHub service
        const githubService = window.tektonUI.services?.githubService;
        if (!githubService) {
            console.error('GitHub service not available for loading repositories');
            component.state.set('repositories.loading', false);
            return;
        }
        
        // Get filter options from state
        const filter = component.state.get('repositories.filter');
        const page = component.state.get('repositories.page');
        
        // Fetch repositories
        githubService.getRepositories({
            type: filter.type !== 'all' ? filter.type : undefined,
            query: filter.query,
            language: filter.language !== 'all' ? filter.language : undefined,
            page: page,
            perPage: 12,
            sort: 'updated',
            forceRefresh: true
        })
            .then(repositories => {
                // Update state with repositories
                component.state.set({
                    'repositories.items': repositories,
                    'repositories.loading': false
                });
                
                // Update UI
                if (component.ui && component.ui.github) {
                    component.ui.github.renderRepositories(repositories);
                    
                    // Update pagination info
                    const totalPages = Math.ceil(repositories.length / 12); // Approximation
                    component.ui.github.updateRepositoryPagination(page, totalPages);
                }
                
                // Extract languages for filter
                const languages = new Set();
                repositories.forEach(repo => {
                    if (repo.language) {
                        languages.add(repo.language);
                    }
                });
                
                // Update state with languages
                component.state.set('languages', Array.from(languages).sort());
                
                // Update language filter options
                updateLanguageFilterOptions(component, Array.from(languages).sort());
            })
            .catch(error => {
                console.error('Error loading repositories:', error);
                component.state.set('repositories.loading', false);
                component.showNotification('Error', `Failed to load repositories: ${error.message}`, 'error');
            });
    }
    
    /**
     * Update language filter options
     * @param {Object} component - GitHub panel component
     * @param {Array} languages - List of languages
     */
    function updateLanguageFilterOptions(component, languages) {
        const languageFilter = component.$('#repo-language-filter');
        if (!languageFilter) return;
        
        // Keep the first option (All Languages)
        const firstOption = languageFilter.options[0];
        languageFilter.innerHTML = '';
        languageFilter.appendChild(firstOption);
        
        // Add language options
        languages.forEach(language => {
            const option = document.createElement('option');
            option.value = language;
            option.textContent = language;
            languageFilter.appendChild(option);
        });
        
        // Set selected value from state
        const selectedLanguage = component.state.get('repositories.filter.language');
        if (selectedLanguage) {
            languageFilter.value = selectedLanguage;
        }
    }
    
    /**
     * Load project links data
     * @param {Object} component - GitHub panel component
     */
    function loadProjectLinks(component) {
        // Implementation will be added in future updates
        console.log('Loading project links...');
    }
    
    /**
     * Load issues data
     * @param {Object} component - GitHub panel component
     */
    function loadIssues(component) {
        // Implementation will be added in future updates
        console.log('Loading issues...');
    }
    
    /**
     * Load pull requests data
     * @param {Object} component - GitHub panel component
     */
    function loadPullRequests(component) {
        // Implementation will be added in future updates
        console.log('Loading pull requests...');
    }
    
    /**
     * Load settings data
     * @param {Object} component - GitHub panel component
     */
    function loadSettings(component) {
        // Update UI with settings from state
        const enterpriseUrl = component.state.get('settings.enterpriseUrl');
        const webhookSecret = component.state.get('settings.webhookSecret');
        const autoSyncFrequency = component.state.get('settings.autoSyncFrequency');
        
        const enterpriseUrlInput = component.$('#github-enterprise-url');
        const webhookSecretInput = component.$('#webhook-secret');
        const autoSyncFrequencySelect = component.$('#auto-sync-frequency');
        
        if (enterpriseUrlInput && enterpriseUrl) {
            enterpriseUrlInput.value = enterpriseUrl;
        }
        
        if (webhookSecretInput && webhookSecret) {
            webhookSecretInput.value = webhookSecret;
        }
        
        if (autoSyncFrequencySelect && autoSyncFrequency) {
            autoSyncFrequencySelect.value = autoSyncFrequency;
        }
    }
})();