/**
 * Tekton Dashboard Handlers
 * Event handlers and UI update functions for the Tekton Dashboard component
 */

console.log('[FILE_TRACE] Loading: tekton-dashboard-handlers.js');
(function(component) {
    // Event handlers for system status
    function refreshSystemStatus() {
        if (!tektonService) return;
        
        // Get system status
        tektonService.getSystemStatus().catch(error => {
            console.error('Failed to refresh system status:', error);
            showNotification('Failed to refresh system status', 'error');
        });
    }
    
    function handleAutoRefreshChange(event) {
        const interval = parseInt(event.target.value, 10);
        
        // Update state
        component.state.set('autoRefreshInterval', interval);
        
        // Update service
        if (tektonService) {
            tektonService.setAutoRefreshInterval(interval);
        }
    }
    
    function restartAllComponents() {
        if (!tektonService) return;
        
        // Confirm restart
        if (!confirm('Are you sure you want to restart all components? This may cause disruption to running services.')) {
            return;
        }
        
        // Show notification
        showNotification('Restarting all components...', 'info');
        
        // Restart system
        tektonService.restartSystem()
            .then(success => {
                if (success) {
                    showNotification('System restart initiated successfully', 'success');
                } else {
                    showNotification('Failed to restart system', 'error');
                }
            })
            .catch(error => {
                console.error('Failed to restart system:', error);
                showNotification('Failed to restart system: ' + error.message, 'error');
            });
    }
    
    function runHealthCheck() {
        if (!tektonService) return;
        
        // Show notification
        showNotification('Running system health check...', 'info');
        
        // Run health check
        tektonService.runHealthCheck()
            .then(results => {
                if (results) {
                    showNotification('Health check completed', 'success');
                    
                    // Display results in a modal or in the UI
                    displayHealthCheckResults(results);
                } else {
                    showNotification('Health check failed to return results', 'warning');
                }
            })
            .catch(error => {
                console.error('Failed to run health check:', error);
                showNotification('Failed to run health check: ' + error.message, 'error');
            });
    }
    
    // Event handlers for components tab
    function handleComponentFilterChange(event) {
        const filter = event.target.value;
        
        // Update state
        component.state.set('componentFilter', filter);
        
        // Update component display
        filterComponents();
    }
    
    function handleComponentSearch(event) {
        const searchTerm = event.target.value.toLowerCase();
        
        // Update state
        component.state.set('searchTerms.components', searchTerm);
        
        // Update component display
        filterComponents();
    }
    
    function handleViewModeChange(event) {
        const viewMode = event.target.closest('.tekton-dashboard__view-button').getAttribute('data-view');
        
        // Update state
        component.state.set('viewMode', viewMode);
    }
    
    // Event handlers for logs tab
    function handleLogSettingsChange(event) {
        const target = event.target;
        const setting = target.id.replace('logs-', '').replace('-', '.');
        const value = target.type === 'checkbox' ? target.checked : target.value;
        
        // Update state
        component.state.set(`logSettings.${setting}`, value);
    }
    
    function handleLogComponentFilter(event) {
        const component = event.target.value;
        
        // Update state
        component.state.set('logSettings.component', component === 'all' ? null : component);
        
        // Reload logs with new filter
        loadLogs();
    }
    
    function handleLogLevelFilter(event) {
        const level = event.target.value;
        
        // Update state
        component.state.set('logSettings.level', level);
        
        // Reload logs with new filter
        loadLogs();
    }
    
    function downloadLogs() {
        if (!tektonService) return;
        
        // Get logs from service
        const logs = tektonService.systemLogs;
        
        if (!logs || logs.length === 0) {
            showNotification('No logs to download', 'warning');
            return;
        }
        
        // Format logs as JSON
        const logsJson = JSON.stringify(logs, null, 2);
        
        // Create download link
        const blob = new Blob([logsJson], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        
        a.href = url;
        a.download = `tekton-logs-${timestamp}.json`;
        a.click();
        
        // Clean up
        URL.revokeObjectURL(url);
        
        showNotification('Logs downloaded successfully', 'success');
    }
    
    function clearLogs() {
        if (!tektonService) return;
        
        // Confirm clear
        if (!confirm('Are you sure you want to clear all logs? This cannot be undone.')) {
            return;
        }
        
        // Clear logs
        tektonService.clearLogs();
        
        // Clear log display
        if (elements.containers.logContent) {
            elements.containers.logContent.innerHTML = '<div class="tekton-dashboard__placeholder-message">No logs found</div>';
        }
        
        showNotification('Logs cleared successfully', 'success');
    }
    
    // Event handlers for projects tab
    function handleProjectFilterChange(event) {
        const filter = event.target.value;
        
        // Update state
        component.state.set('projectFilter', filter);
        
        // Update project display
        filterProjects();
    }
    
    function handleProjectSearch(event) {
        const searchTerm = event.target.value.toLowerCase();
        
        // Update state
        component.state.set('searchTerms.projects', searchTerm);
        
        // Update project display
        filterProjects();
    }
    
    // Event handlers for resources tab
    function handleResourceTimeRangeChange(event) {
        const timeRange = event.target.value;
        
        // Update state
        component.state.set('resourceTimeRange', timeRange);
        
        // Update resource charts
        updateResourceCharts();
    }
    
    // Modal event handlers
    function openComponentDetailModal(componentId) {
        if (!tektonService) return;
        
        // Show loading state
        if (elements.modals.componentDetailBody) {
            elements.modals.componentDetailBody.innerHTML = '<div class="tekton-dashboard__loading">Loading component details...</div>';
        }
        
        // Update modal state
        component.state.set('modalState.componentDetail', {
            isOpen: true,
            componentId: componentId
        });
        
        // Load component details
        tektonService.getComponentDetails(componentId)
            .then(details => {
                if (details) {
                    displayComponentDetails(details);
                } else {
                    if (elements.modals.componentDetailBody) {
                        elements.modals.componentDetailBody.innerHTML = '<div class="tekton-dashboard__placeholder-message">Failed to load component details</div>';
                    }
                }
            })
            .catch(error => {
                console.error('Failed to load component details:', error);
                if (elements.modals.componentDetailBody) {
                    elements.modals.componentDetailBody.innerHTML = `<div class="tekton-dashboard__placeholder-message">Error: ${error.message}</div>`;
                }
            });
    }
    
    function closeComponentDetailModal() {
        // Update modal state
        component.state.set('modalState.componentDetail', {
            isOpen: false,
            componentId: null
        });
    }
    
    function handleComponentAction() {
        if (!tektonService) return;
        
        const componentId = component.state.get('modalState.componentDetail.componentId');
        if (!componentId) return;
        
        // Find component in the list
        const componentDetails = tektonService.components.find(c => c.id === componentId);
        if (!componentDetails) return;
        
        // Check if component is running
        const isRunning = componentDetails.status === 'running';
        
        // Show confirmation dialog
        const action = isRunning ? 'stop' : 'start';
        const confirmation = confirm(`Are you sure you want to ${action} the ${componentDetails.name} component?`);
        
        if (!confirmation) return;
        
        // Show notification
        showNotification(`${isRunning ? 'Stopping' : 'Starting'} component ${componentDetails.name}...`, 'info');
        
        // Perform action
        const actionPromise = isRunning ? 
            tektonService.stopComponent(componentId) : 
            tektonService.startComponent(componentId);
        
        actionPromise
            .then(success => {
                if (success) {
                    showNotification(`${isRunning ? 'Stopped' : 'Started'} component ${componentDetails.name} successfully`, 'success');
                    
                    // Close the modal
                    closeComponentDetailModal();
                    
                    // Refresh components list
                    loadComponents();
                } else {
                    showNotification(`Failed to ${action} component ${componentDetails.name}`, 'error');
                }
            })
            .catch(error => {
                console.error(`Failed to ${action} component:`, error);
                showNotification(`Failed to ${action} component: ${error.message}`, 'error');
            });
    }
    
    function openProjectDetailModal(projectId) {
        if (!tektonService) return;
        
        // Show loading state
        if (elements.modals.projectDetailBody) {
            elements.modals.projectDetailBody.innerHTML = '<div class="tekton-dashboard__loading">Loading project details...</div>';
        }
        
        // Update modal state
        component.state.set('modalState.projectDetail', {
            isOpen: true,
            projectId: projectId
        });
        
        // Load project details
        tektonService.getProjectDetails(projectId)
            .then(details => {
                if (details) {
                    displayProjectDetails(details);
                } else {
                    if (elements.modals.projectDetailBody) {
                        elements.modals.projectDetailBody.innerHTML = '<div class="tekton-dashboard__placeholder-message">Failed to load project details</div>';
                    }
                }
            })
            .catch(error => {
                console.error('Failed to load project details:', error);
                if (elements.modals.projectDetailBody) {
                    elements.modals.projectDetailBody.innerHTML = `<div class="tekton-dashboard__placeholder-message">Error: ${error.message}</div>`;
                }
            });
    }
    
    function closeProjectDetailModal() {
        // Update modal state
        component.state.set('modalState.projectDetail', {
            isOpen: false,
            projectId: null
        });
    }
    
    function handleProjectAction() {
        const projectId = component.state.get('modalState.projectDetail.projectId');
        if (!projectId) return;
        
        // TODO: Implement project actions (open in IDE, archive, etc)
        showNotification('Project actions not yet implemented', 'info');
        
        // Close the modal
        closeProjectDetailModal();
    }
    
    function openCreateProjectModal() {
        // Reset form
        if (elements.modals.createProjectForm) {
            elements.modals.createProjectForm.reset();
        }
        
        // Update modal state
        component.state.set('modalState.createProject', {
            isOpen: true
        });
    }
    
    function closeCreateProjectModal() {
        // Update modal state
        component.state.set('modalState.createProject', {
            isOpen: false
        });
    }
    
    function handleCreateProject() {
        if (!tektonService) return;
        
        // Get form data
        const name = document.getElementById('project-name').value;
        const description = document.getElementById('project-description').value;
        const repoUrl = document.getElementById('project-repo-url').value;
        const template = document.getElementById('project-template').value;
        
        if (!name) {
            showNotification('Project name is required', 'error');
            return;
        }
        
        // Show notification
        showNotification('Creating project...', 'info');
        
        // Create project
        tektonService.createProject({
            name,
            description,
            repoUrl,
            template
        })
            .then(project => {
                if (project) {
                    showNotification(`Project ${name} created successfully`, 'success');
                    
                    // Close the modal
                    closeCreateProjectModal();
                    
                    // Refresh projects list
                    loadProjects();
                } else {
                    showNotification('Failed to create project', 'error');
                }
            })
            .catch(error => {
                console.error('Failed to create project:', error);
                showNotification(`Failed to create project: ${error.message}`, 'error');
            });
    }
    
    // Service event handlers
    function handleStatusUpdate(event) {
        const { status, metrics } = event.detail;
        
        // Update status displays
        updateSystemStatus(status);
        
        // Update metrics displays
        if (metrics) {
            updateMetricsDisplay(metrics);
        }
        
        // Update charts if they exist
        updateCharts();
    }
    
    function handleComponentsUpdate(event) {
        const { components } = event.detail;
        
        // Update components display
        updateComponentsDisplay(components);
        
        // Update component status grid on system status tab
        updateComponentStatusGrid(components);
        
        // Update component filter in logs tab
        updateLogComponentFilter(components);
    }
    
    function handleLogsUpdate(event) {
        const { logs } = event.detail;
        
        // Update logs display
        updateLogsDisplay(logs);
    }
    
    function handleProjectsUpdate(event) {
        const { projects } = event.detail;
        
        // Update projects display
        updateProjectsDisplay(projects);
    }
    
    function handleNewLogEntry(event) {
        const { log } = event.detail;
        
        // Check if auto-update is enabled
        if (!component.state.get('logSettings.autoUpdate')) {
            return;
        }
        
        // Check if log matches current filters
        const componentFilter = component.state.get('logSettings.component');
        const levelFilter = component.state.get('logSettings.level');
        
        if (componentFilter && log.component !== componentFilter) {
            return;
        }
        
        if (levelFilter !== 'all' && log.level !== levelFilter) {
            return;
        }
        
        // Add log entry to display
        addLogEntryToDisplay(log);
    }
    
    function handleHealthCheckCompleted(event) {
        const { results } = event.detail;
        
        // Display health check results
        displayHealthCheckResults(results);
    }
    
    function handleServiceError(event) {
        const { error } = event.detail;
        
        // Show notification
        showNotification(`Error: ${error}`, 'error');
    }
    
    function handleConnectionFailure(event) {
        const { error } = event.detail;
        
        // Show notification
        showNotification(`Connection failed: ${error}`, 'error');
        
        // Display connection error in UI
        displayConnectionError();
    }
    
    // Expose handlers to component scope
    Object.assign(component, {
        refreshSystemStatus,
        handleAutoRefreshChange,
        restartAllComponents,
        runHealthCheck,
        handleComponentFilterChange,
        handleComponentSearch,
        handleViewModeChange,
        handleLogSettingsChange,
        handleLogComponentFilter,
        handleLogLevelFilter,
        downloadLogs,
        clearLogs,
        handleProjectFilterChange,
        handleProjectSearch,
        handleResourceTimeRangeChange,
        openComponentDetailModal,
        closeComponentDetailModal,
        handleComponentAction,
        openProjectDetailModal,
        closeProjectDetailModal,
        handleProjectAction,
        openCreateProjectModal,
        closeCreateProjectModal,
        handleCreateProject,
        handleStatusUpdate,
        handleComponentsUpdate,
        handleLogsUpdate,
        handleProjectsUpdate,
        handleNewLogEntry,
        handleHealthCheckCompleted,
        handleServiceError,
        handleConnectionFailure
    });
    
})(component);