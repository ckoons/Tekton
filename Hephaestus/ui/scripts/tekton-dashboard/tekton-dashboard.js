/**
 * Tekton Dashboard Component
 * Central control panel for the Tekton ecosystem with system status, 
 * resource monitoring, and component management
 */

console.log('[FILE_TRACE] Loading: tekton-dashboard.js');
(function(component) {
    // Component state using State Management Pattern
    if (window.tektonUI.stateManager) {
        component.utils.componentState.connect(component, {
            namespace: 'tektonDashboard',
            initialState: {
                activeTab: 'system-status',
                autoRefreshInterval: 10000,
                viewMode: 'grid',
                componentFilter: 'all',
                projectFilter: 'all',
                logSettings: {
                    autoUpdate: true,
                    wrapLines: true,
                    maxLines: 500,
                    component: null,
                    level: 'all'
                },
                resourceTimeRange: '24h',
                searchTerms: {
                    components: '',
                    logs: '',
                    projects: ''
                },
                modalState: {
                    componentDetail: {
                        isOpen: false,
                        componentId: null
                    },
                    projectDetail: {
                        isOpen: false,
                        projectId: null
                    },
                    createProject: {
                        isOpen: false
                    },
                    mergeDetail: {
                        isOpen: false,
                        mergeId: null
                    }
                }
            },
            persist: true,
            persistenceType: 'localStorage'
        });
    }

    // Service references
    let tektonService = null;
    
    // Component elements
    const elements = {
        tabs: {},
        panels: {},
        buttons: {},
        modals: {},
        charts: {}
    };
    
    // Chart references
    const charts = {
        cpu: null,
        memory: null,
        disk: null,
        network: null,
        cpuHistory: null,
        memoryHistory: null,
        diskIO: null,
        networkTraffic: null
    };
    
    // Initialize the dashboard component
    function init() {
        console.log('Initializing Tekton Dashboard Component');
        
        // Cache DOM elements
        cacheElements();
        
        // Set up event handlers
        setupEventHandlers();
        
        // Initialize service
        initService();
        
        // Set up state effects
        setupStateEffects();
        
        // Set up tab switcher
        setupTabs();
        
        // Initialize charts
        initCharts();
    }
    
    // Cache DOM elements for performance
    function cacheElements() {
        // Cache tab buttons
        const tabButtons = component.$$('.tekton-dashboard__tab-button');
        tabButtons.forEach(btn => {
            const tabId = btn.getAttribute('data-tab');
            elements.tabs[tabId] = btn;
        });
        
        // Cache tab panels
        const tabPanels = component.$$('.tekton-dashboard__tab-panel');
        tabPanels.forEach(panel => {
            const panelId = panel.getAttribute('data-panel');
            elements.panels[panelId] = panel;
        });
        
        // Cache buttons
        elements.buttons.refreshSystem = component.$('#refresh-system');
        elements.buttons.autoRefreshInterval = component.$('#auto-refresh-interval');
        elements.buttons.restartAll = component.$('#system-restart-all');
        elements.buttons.healthCheck = component.$('#system-health-check');
        elements.buttons.componentSearch = component.$('#component-search');
        elements.buttons.componentFilter = component.$('#component-filter');
        elements.buttons.viewButtons = component.$$('.tekton-dashboard__view-button');
        elements.buttons.logsAutoUpdate = component.$('#logs-auto-update');
        elements.buttons.logsWrapLines = component.$('#logs-wrap-lines');
        elements.buttons.logsMaxLines = component.$('#logs-max-lines');
        elements.buttons.logsComponentFilter = component.$('#logs-component-filter');
        elements.buttons.logsLevelFilter = component.$('#logs-level-filter');
        elements.buttons.logsDownload = component.$('#logs-download');
        elements.buttons.logsClear = component.$('#logs-clear');
        elements.buttons.createProject = component.$('#create-project');
        elements.buttons.projectFilter = component.$('#projects-filter');
        elements.buttons.projectSearch = component.$('#projects-search');
        elements.buttons.resourcesTimeRange = component.$('#resources-time-range');
        
        // Cache modals
        elements.modals.componentDetail = component.$('#component-detail-modal');
        elements.modals.componentDetailBody = component.$('#component-modal-body');
        elements.modals.componentDetailTitle = component.$('#component-modal-title');
        elements.modals.componentDetailClose = component.$('#close-component-modal');
        elements.modals.componentDetailCancel = component.$('#component-modal-cancel');
        elements.modals.componentDetailAction = component.$('#component-modal-action');
        
        elements.modals.projectDetail = component.$('#project-detail-modal');
        elements.modals.projectDetailBody = component.$('#project-modal-body');
        elements.modals.projectDetailTitle = component.$('#project-modal-title');
        elements.modals.projectDetailClose = component.$('#close-project-modal');
        elements.modals.projectDetailCancel = component.$('#project-modal-cancel');
        elements.modals.projectDetailAction = component.$('#project-modal-action');
        
        elements.modals.createProject = component.$('#create-project-modal');
        elements.modals.createProjectClose = component.$('#close-create-project-modal');
        elements.modals.createProjectCancel = component.$('#create-project-cancel');
        elements.modals.createProjectSubmit = component.$('#create-project-submit');
        elements.modals.createProjectForm = component.$('#create-project-form');
        
        // Cache containers
        elements.containers = {
            componentGrid: component.$('#component-status-grid'),
            componentsList: component.$('#components-list-view'),
            componentsGrid: component.$('#components-grid-view'),
            componentsTable: component.$('#components-table-body'),
            systemAlerts: component.$('#system-alerts'),
            logContent: component.$('#log-content'),
            projectsList: component.$('#projects-list'),
            cpuProcesses: component.$('#cpu-processes-table'),
            memoryProcesses: component.$('#memory-processes-table'),
            notifications: component.$('#tekton-notifications')
        };
        
        // Cache chart containers
        elements.charts.cpu = component.$('#cpu-chart');
        elements.charts.memory = component.$('#memory-chart');
        elements.charts.disk = component.$('#disk-chart');
        elements.charts.network = component.$('#network-chart');
        elements.charts.cpuHistory = component.$('#cpu-history-chart');
        elements.charts.memoryHistory = component.$('#memory-history-chart');
        elements.charts.diskIO = component.$('#disk-io-chart');
        elements.charts.networkTraffic = component.$('#network-traffic-chart');
        
        // Cache metric displays
        elements.metrics = {
            cpuUsage: component.$('#cpu-usage'),
            memoryUsage: component.$('#memory-usage'),
            diskUsage: component.$('#disk-usage'),
            networkUsage: component.$('#network-usage')
        };
    }
    
    // Set up event handlers
    function setupEventHandlers() {
        // System status tab event handlers
        if (elements.buttons.refreshSystem) {
            elements.buttons.refreshSystem.addEventListener('click', refreshSystemStatus);
        }
        
        if (elements.buttons.autoRefreshInterval) {
            elements.buttons.autoRefreshInterval.addEventListener('change', handleAutoRefreshChange);
            // Set initial value from state
            elements.buttons.autoRefreshInterval.value = component.state.get('autoRefreshInterval');
        }
        
        if (elements.buttons.restartAll) {
            elements.buttons.restartAll.addEventListener('click', restartAllComponents);
        }
        
        if (elements.buttons.healthCheck) {
            elements.buttons.healthCheck.addEventListener('click', runHealthCheck);
        }
        
        // Components tab event handlers
        if (elements.buttons.componentFilter) {
            elements.buttons.componentFilter.addEventListener('change', handleComponentFilterChange);
        }
        
        if (elements.buttons.componentSearch) {
            elements.buttons.componentSearch.addEventListener('input', handleComponentSearch);
        }
        
        if (elements.buttons.viewButtons) {
            elements.buttons.viewButtons.forEach(btn => {
                btn.addEventListener('click', handleViewModeChange);
            });
        }
        
        // Logs tab event handlers
        if (elements.buttons.logsAutoUpdate) {
            elements.buttons.logsAutoUpdate.addEventListener('change', handleLogSettingsChange);
            elements.buttons.logsAutoUpdate.checked = component.state.get('logSettings.autoUpdate');
        }
        
        if (elements.buttons.logsWrapLines) {
            elements.buttons.logsWrapLines.addEventListener('change', handleLogSettingsChange);
            elements.buttons.logsWrapLines.checked = component.state.get('logSettings.wrapLines');
            // Apply wrapping immediately
            if (elements.containers.logContent) {
                elements.containers.logContent.style.whiteSpace = component.state.get('logSettings.wrapLines') ? 'pre-wrap' : 'pre';
            }
        }
        
        if (elements.buttons.logsMaxLines) {
            elements.buttons.logsMaxLines.addEventListener('change', handleLogSettingsChange);
            elements.buttons.logsMaxLines.value = component.state.get('logSettings.maxLines');
        }
        
        if (elements.buttons.logsComponentFilter) {
            elements.buttons.logsComponentFilter.addEventListener('change', handleLogComponentFilter);
        }
        
        if (elements.buttons.logsLevelFilter) {
            elements.buttons.logsLevelFilter.addEventListener('change', handleLogLevelFilter);
        }
        
        if (elements.buttons.logsDownload) {
            elements.buttons.logsDownload.addEventListener('click', downloadLogs);
        }
        
        if (elements.buttons.logsClear) {
            elements.buttons.logsClear.addEventListener('click', clearLogs);
        }
        
        // Projects tab event handlers
        if (elements.buttons.createProject) {
            elements.buttons.createProject.addEventListener('click', openCreateProjectModal);
        }
        
        if (elements.buttons.projectFilter) {
            elements.buttons.projectFilter.addEventListener('change', handleProjectFilterChange);
        }
        
        if (elements.buttons.projectSearch) {
            elements.buttons.projectSearch.addEventListener('input', handleProjectSearch);
        }
        
        // Resources tab event handlers
        if (elements.buttons.resourcesTimeRange) {
            elements.buttons.resourcesTimeRange.addEventListener('change', handleResourceTimeRangeChange);
            elements.buttons.resourcesTimeRange.value = component.state.get('resourceTimeRange');
        }
        
        // Merge Queue tab event handlers
        const mergeQueueFilter = component.$('#merge-queue-filter');
        const mergeQueueSearch = component.$('#merge-queue-search');
        const refreshMergeQueue = component.$('#refresh-merge-queue');
        
        if (mergeQueueFilter) {
            mergeQueueFilter.addEventListener('change', handleMergeQueueFilter);
        }
        
        if (mergeQueueSearch) {
            mergeQueueSearch.addEventListener('input', handleMergeQueueSearch);
        }
        
        if (refreshMergeQueue) {
            refreshMergeQueue.addEventListener('click', loadMergeQueue);
        }
        
        // Modal event handlers
        setupModalEventHandlers();
    }
    
    // Set up modal event handlers
    function setupModalEventHandlers() {
        // Component Detail Modal
        if (elements.modals.componentDetailClose) {
            elements.modals.componentDetailClose.addEventListener('click', closeComponentDetailModal);
        }
        
        if (elements.modals.componentDetailCancel) {
            elements.modals.componentDetailCancel.addEventListener('click', closeComponentDetailModal);
        }
        
        if (elements.modals.componentDetailAction) {
            elements.modals.componentDetailAction.addEventListener('click', handleComponentAction);
        }
        
        // Project Detail Modal
        if (elements.modals.projectDetailClose) {
            elements.modals.projectDetailClose.addEventListener('click', closeProjectDetailModal);
        }
        
        if (elements.modals.projectDetailCancel) {
            elements.modals.projectDetailCancel.addEventListener('click', closeProjectDetailModal);
        }
        
        if (elements.modals.projectDetailAction) {
            elements.modals.projectDetailAction.addEventListener('click', handleProjectAction);
        }
        
        // Create Project Modal
        if (elements.modals.createProjectClose) {
            elements.modals.createProjectClose.addEventListener('click', closeCreateProjectModal);
        }
        
        if (elements.modals.createProjectCancel) {
            elements.modals.createProjectCancel.addEventListener('click', closeCreateProjectModal);
        }
        
        if (elements.modals.createProjectSubmit) {
            elements.modals.createProjectSubmit.addEventListener('click', handleCreateProject);
        }
        
        // Merge Detail Modal
        const mergeDetailClose = component.$('#close-merge-modal');
        const mergeDetailCancel = component.$('#merge-modal-cancel');
        const mergeDetailMerge = component.$('#merge-modal-merge');
        const mergeDetailReject = component.$('#merge-modal-reject');
        
        if (mergeDetailClose) {
            mergeDetailClose.addEventListener('click', closeMergeDetailModal);
        }
        
        if (mergeDetailCancel) {
            mergeDetailCancel.addEventListener('click', closeMergeDetailModal);
        }
        
        if (mergeDetailMerge) {
            mergeDetailMerge.addEventListener('click', handleMergeMergeRequest);
        }
        
        if (mergeDetailReject) {
            mergeDetailReject.addEventListener('click', handleRejectMergeRequest);
        }
        
        if (elements.modals.createProjectForm) {
            elements.modals.createProjectForm.addEventListener('submit', (e) => {
                e.preventDefault();
                handleCreateProject();
            });
        }
    }
    
    // Set up state effects for reactive UI updates
    function setupStateEffects() {
        // Set up effect for active tab changes
        component.utils.lifecycle.registerStateEffect(
            component, 
            ['activeTab'],
            (state) => {
                updateActiveTab(state.activeTab);
            }
        );
        
        // Set up effect for view mode changes
        component.utils.lifecycle.registerStateEffect(
            component,
            ['viewMode'],
            (state) => {
                updateViewMode(state.viewMode);
            }
        );
        
        // Set up effect for log settings changes
        component.utils.lifecycle.registerStateEffect(
            component,
            ['logSettings.wrapLines'],
            (state) => {
                if (elements.containers.logContent) {
                    elements.containers.logContent.style.whiteSpace = state.logSettings.wrapLines ? 'pre-wrap' : 'pre';
                }
            }
        );
        
        // Set up effect for modal state changes
        component.utils.lifecycle.registerStateEffect(
            component,
            ['modalState.componentDetail.isOpen'],
            (state) => {
                if (elements.modals.componentDetail) {
                    elements.modals.componentDetail.style.display = state.modalState.componentDetail.isOpen ? 'flex' : 'none';
                }
            }
        );
        
        component.utils.lifecycle.registerStateEffect(
            component,
            ['modalState.projectDetail.isOpen'],
            (state) => {
                if (elements.modals.projectDetail) {
                    elements.modals.projectDetail.style.display = state.modalState.projectDetail.isOpen ? 'flex' : 'none';
                }
            }
        );
        
        component.utils.lifecycle.registerStateEffect(
            component,
            ['modalState.createProject.isOpen'],
            (state) => {
                if (elements.modals.createProject) {
                    elements.modals.createProject.style.display = state.modalState.createProject.isOpen ? 'flex' : 'none';
                }
            }
        );
        
        component.utils.lifecycle.registerStateEffect(
            component,
            ['modalState.mergeDetail.isOpen'],
            (state) => {
                const mergeDetailModal = component.$('#merge-detail-modal');
                if (mergeDetailModal) {
                    mergeDetailModal.style.display = state.modalState.mergeDetail.isOpen ? 'flex' : 'none';
                }
            }
        );
    }
    
    // Initialize the Tekton service
    function initService() {
        // Check if TektonService is available
        if (window.tektonUI?.services?.tektonService) {
            tektonService = window.tektonUI.services.tektonService;
            
            // Set up event listeners
            setupServiceEventListeners();
            
            // Connect to the service
            tektonService.connect().then(() => {
                // Load initial data
                refreshSystemStatus();
                loadComponents();
                loadProjects();
                loadLogs();
            });
            
            // Set auto-refresh interval
            const interval = component.state.get('autoRefreshInterval');
            if (interval > 0) {
                tektonService.setAutoRefreshInterval(interval);
            }
        } else {
            console.error('TektonService not available');
            showNotification('Error: TektonService not available', 'error');
        }
    }
    
    // Set up event listeners for the Tekton service
    function setupServiceEventListeners() {
        if (!tektonService) return;
        
        // Status events
        tektonService.addEventListener('statusUpdated', handleStatusUpdate);
        tektonService.addEventListener('componentsUpdated', handleComponentsUpdate);
        tektonService.addEventListener('logsUpdated', handleLogsUpdate);
        tektonService.addEventListener('projectsUpdated', handleProjectsUpdate);
        tektonService.addEventListener('newLogEntry', handleNewLogEntry);
        
        // Action events
        tektonService.addEventListener('componentStarted', handleComponentAction);
        tektonService.addEventListener('componentStopped', handleComponentAction);
        tektonService.addEventListener('healthCheckCompleted', handleHealthCheckCompleted);
        
        // Error events
        tektonService.addEventListener('error', handleServiceError);
        tektonService.addEventListener('connectionFailed', handleConnectionFailure);
    }
    
    // Set up tab navigation
    function setupTabs() {
        // Add click handlers to tab buttons
        component.on('click', '.tekton-dashboard__tab-button', (event) => {
            const tabId = event.target.closest('.tekton-dashboard__tab-button').getAttribute('data-tab');
            component.state.set('activeTab', tabId);
        });
        
        // Set initial active tab from state
        updateActiveTab(component.state.get('activeTab'));
    }
    
    // Update active tab
    function updateActiveTab(tabId) {
        // Update tab buttons
        Object.values(elements.tabs).forEach(tab => {
            tab.classList.remove('tekton-dashboard__tab-button--active');
        });
        
        if (elements.tabs[tabId]) {
            elements.tabs[tabId].classList.add('tekton-dashboard__tab-button--active');
        }
        
        // Update tab panels
        Object.values(elements.panels).forEach(panel => {
            panel.classList.remove('tekton-dashboard__tab-panel--active');
        });
        
        if (elements.panels[tabId]) {
            elements.panels[tabId].classList.add('tekton-dashboard__tab-panel--active');
        }
        
        // Load tab-specific data
        loadTabData(tabId);
    }
    
    // Load data specific to the active tab
    function loadTabData(tabId) {
        switch (tabId) {
            case 'system-status':
                refreshSystemStatus();
                break;
            case 'components':
                loadComponents();
                break;
            case 'resources':
                loadResourceMetrics();
                break;
            case 'logs':
                loadLogs();
                break;
            case 'projects':
                loadProjects();
                break;
            case 'merge-queue':
                loadMergeQueue();
                break;
            case 'github':
                loadGitHubPanel();
                break;
        }
    }
    
    // Load the GitHub panel
    function loadGitHubPanel() {
        const container = component.$('#github-panel-container');
        if (!container) return;
        
        // Check if GitHub panel has already been loaded
        if (container.querySelector('.tekton-dashboard__github-panel')) {
            return;
        }
        
        // Show loading indicator
        container.innerHTML = '<div class="tekton-dashboard__loading">Loading GitHub integration...</div>';
        
        // Load GitHub panel HTML
        fetch('/components/tekton-dashboard/github-panel.html')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to load GitHub panel: ${response.status} ${response.statusText}`);
                }
                return response.text();
            })
            .then(html => {
                // Insert the HTML
                container.innerHTML = html;
                
                // Initialize GitHub panel
                if (window.tektonUI.initGitHubPanel) {
                    window.tektonUI.initGitHubPanel(component);
                } else {
                    console.error('GitHub panel initialization function not found');
                    showNotification('Error', 'Failed to initialize GitHub integration', 'error');
                }
            })
            .catch(error => {
                console.error('Error loading GitHub panel:', error);
                container.innerHTML = `
                    <div class="tekton-dashboard__error-state">
                        <div class="tekton-dashboard__error-icon">⚠️</div>
                        <div class="tekton-dashboard__error-title">Failed to load GitHub integration</div>
                        <div class="tekton-dashboard__error-message">${error.message}</div>
                    </div>
                `;
            });
    }
    
    // Initialize all charts
    function initCharts() {
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not available. Charts will not be displayed.');
            return;
        }
        
        // Initialize mini charts
        initMiniCharts();
        
        // Initialize detailed resource charts
        initResourceCharts();
    }

    // Register component cleanup
    function cleanup() {
        // Cleanup service event listeners
        if (tektonService) {
            tektonService.removeEventListener('statusUpdated', handleStatusUpdate);
            tektonService.removeEventListener('componentsUpdated', handleComponentsUpdate);
            tektonService.removeEventListener('logsUpdated', handleLogsUpdate);
            tektonService.removeEventListener('projectsUpdated', handleProjectsUpdate);
            tektonService.removeEventListener('newLogEntry', handleNewLogEntry);
            tektonService.removeEventListener('componentStarted', handleComponentAction);
            tektonService.removeEventListener('componentStopped', handleComponentAction);
            tektonService.removeEventListener('healthCheckCompleted', handleHealthCheckCompleted);
            tektonService.removeEventListener('error', handleServiceError);
            tektonService.removeEventListener('connectionFailed', handleConnectionFailure);
        }
        
        // Cleanup charts
        Object.values(charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
    }
    
    // Register cleanup handler
    component.registerCleanup(cleanup);
    
    // Initialize the component
    init();
})(component);