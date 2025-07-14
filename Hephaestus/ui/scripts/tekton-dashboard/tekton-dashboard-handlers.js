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
    
    // Project management functions
    async function loadProjects() {
        if (!tektonService) return;
        
        try {
            const projects = await tektonService.getProjects();
            updateProjectsDisplay(projects);
        } catch (error) {
            console.error('Failed to load projects:', error);
            showNotification('Failed to load projects', 'error');
        }
    }
    
    function filterProjects() {
        const filter = component.state.get('projectFilter');
        const searchTerm = component.state.get('searchTerms.projects').toLowerCase();
        
        const projectCards = component.$$('.tekton-dashboard__project-card');
        
        projectCards.forEach(card => {
            const projectName = card.getAttribute('data-project-name')?.toLowerCase() || '';
            const projectState = card.getAttribute('data-project-state') || '';
            
            let showCard = true;
            
            // Apply filter
            if (filter !== 'all') {
                if (filter === 'active' && !['active', 'approved', 'planning'].includes(projectState)) {
                    showCard = false;
                } else if (filter === 'archived' && projectState !== 'archived') {
                    showCard = false;
                }
            }
            
            // Apply search
            if (searchTerm && !projectName.includes(searchTerm)) {
                showCard = false;
            }
            
            card.style.display = showCard ? 'block' : 'none';
        });
    }
    
    function updateProjectsDisplay(projects) {
        const container = elements.containers.projectsList;
        if (!container) return;
        
        if (!projects || projects.length === 0) {
            container.innerHTML = '<div class="tekton-dashboard__placeholder-message">No projects found. Create your first project using the "New Project" button.</div>';
            return;
        }
        
        // Create project bubbles
        const projectBubbles = projects.map(project => createProjectBubble(project)).join('');
        
        container.innerHTML = `
            <div class="tekton-dashboard__projects-grid">
                ${projectBubbles}
            </div>
        `;
        
        // Add click handlers to project cards
        container.addEventListener('click', (event) => {
            const projectCard = event.target.closest('.tekton-dashboard__project-card');
            if (projectCard) {
                const projectId = projectCard.getAttribute('data-project-id');
                if (projectId) {
                    openProjectDetailModal(projectId);
                }
            }
        });
        
        // Apply current filters
        filterProjects();
    }
    
    function createProjectBubble(project) {
        const stateClass = `tekton-dashboard__project-card--${project.state}`;
        const progressClass = getProgressClass(project.task_count || 0);
        
        return `
            <div class="tekton-dashboard__project-card ${stateClass}" 
                 data-project-id="${project.id}" 
                 data-project-name="${project.name}"
                 data-project-state="${project.state}">
                <div class="tekton-dashboard__project-bubble">
                    <div class="tekton-dashboard__project-header">
                        <h3 class="tekton-dashboard__project-name">${escapeHtml(project.name)}</h3>
                        <span class="tekton-dashboard__project-state tekton-dashboard__project-state--${project.state}">
                            ${project.state.replace('_', ' ')}
                        </span>
                    </div>
                    
                    <div class="tekton-dashboard__project-description">
                        ${escapeHtml(project.description || 'No description')}
                    </div>
                    
                    <div class="tekton-dashboard__project-stats">
                        <div class="tekton-dashboard__project-stat">
                            <span class="tekton-dashboard__project-stat-label">Tasks:</span>
                            <span class="tekton-dashboard__project-stat-value">${project.task_count || 0}</span>
                        </div>
                        <div class="tekton-dashboard__project-stat">
                            <span class="tekton-dashboard__project-stat-label">AI:</span>
                            <span class="tekton-dashboard__project-stat-value">${project.companion_ai || 'Unassigned'}</span>
                        </div>
                    </div>
                    
                    <div class="tekton-dashboard__project-meta">
                        <div class="tekton-dashboard__project-updated">
                            Updated: ${formatDate(project.updated_at)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    function displayProjectDetails(project) {
        if (!elements.modals.projectDetailBody) return;
        
        const projectData = project.project || project;
        const taskStats = project.task_stats || {};
        const activeTasks = project.active_tasks || [];
        const readyTasks = project.ready_tasks || [];
        
        elements.modals.projectDetailBody.innerHTML = `
            <div class="tekton-dashboard__project-details">
                <div class="tekton-dashboard__project-overview">
                    <div class="tekton-dashboard__project-info">
                        <h4>Project Information</h4>
                        <div class="tekton-dashboard__info-grid">
                            <div class="tekton-dashboard__info-item">
                                <label>Name:</label>
                                <span>${escapeHtml(projectData.name)}</span>
                            </div>
                            <div class="tekton-dashboard__info-item">
                                <label>State:</label>
                                <span class="tekton-dashboard__project-state--${projectData.state}">
                                    ${projectData.state.replace('_', ' ')}
                                </span>
                            </div>
                            <div class="tekton-dashboard__info-item">
                                <label>Companion AI:</label>
                                <span>${projectData.companion_ai || 'Unassigned'}</span>
                            </div>
                            <div class="tekton-dashboard__info-item">
                                <label>Repository:</label>
                                <span>${projectData.repo_url ? `<a href="${projectData.repo_url}" target="_blank">${projectData.repo_url}</a>` : 'None'}</span>
                            </div>
                            <div class="tekton-dashboard__info-item">
                                <label>Created:</label>
                                <span>${formatDate(projectData.created_at)}</span>
                            </div>
                            <div class="tekton-dashboard__info-item">
                                <label>Last Activity:</label>
                                <span>${formatDate(projectData.last_activity)}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="tekton-dashboard__project-description">
                        <h4>Description</h4>
                        <p>${escapeHtml(projectData.description || 'No description available')}</p>
                    </div>
                </div>
                
                <div class="tekton-dashboard__task-summary">
                    <h4>Task Summary</h4>
                    <div class="tekton-dashboard__task-stats">
                        <div class="tekton-dashboard__task-stat">
                            <span class="tekton-dashboard__task-stat-value">${taskStats.total || 0}</span>
                            <span class="tekton-dashboard__task-stat-label">Total</span>
                        </div>
                        <div class="tekton-dashboard__task-stat">
                            <span class="tekton-dashboard__task-stat-value">${taskStats.in_progress || 0}</span>
                            <span class="tekton-dashboard__task-stat-label">In Progress</span>
                        </div>
                        <div class="tekton-dashboard__task-stat">
                            <span class="tekton-dashboard__task-stat-value">${taskStats.ready_for_merge || 0}</span>
                            <span class="tekton-dashboard__task-stat-label">Ready for Merge</span>
                        </div>
                        <div class="tekton-dashboard__task-stat">
                            <span class="tekton-dashboard__task-stat-value">${taskStats.completed || 0}</span>
                            <span class="tekton-dashboard__task-stat-label">Completed</span>
                        </div>
                    </div>
                    
                    <div class="tekton-dashboard__progress-bar">
                        <div class="tekton-dashboard__progress-fill" style="width: ${project.progress || 0}%"></div>
                        <span class="tekton-dashboard__progress-text">${Math.round(project.progress || 0)}% Complete</span>
                    </div>
                </div>
                
                ${activeTasks.length > 0 ? `
                    <div class="tekton-dashboard__active-tasks">
                        <h4>Active Tasks</h4>
                        <div class="tekton-dashboard__task-list">
                            ${activeTasks.map(task => `
                                <div class="tekton-dashboard__task-item">
                                    <div class="tekton-dashboard__task-header">
                                        <span class="tekton-dashboard__task-title">${escapeHtml(task.title)}</span>
                                        <span class="tekton-dashboard__task-state tekton-dashboard__task-state--${task.state}">
                                            ${task.state.replace('_', ' ')}
                                        </span>
                                    </div>
                                    <div class="tekton-dashboard__task-meta">
                                        <span class="tekton-dashboard__task-ai">AI: ${task.assigned_ai || 'Unassigned'}</span>
                                        <span class="tekton-dashboard__task-branch">Branch: ${task.branch || 'None'}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${readyTasks.length > 0 ? `
                    <div class="tekton-dashboard__ready-tasks">
                        <h4>Ready for Merge</h4>
                        <div class="tekton-dashboard__task-list">
                            ${readyTasks.map(task => `
                                <div class="tekton-dashboard__task-item">
                                    <div class="tekton-dashboard__task-header">
                                        <span class="tekton-dashboard__task-title">${escapeHtml(task.title)}</span>
                                        <button class="tekton-dashboard__task-merge-btn" data-task-id="${task.id}">
                                            Merge
                                        </button>
                                    </div>
                                    <div class="tekton-dashboard__task-meta">
                                        <span class="tekton-dashboard__task-ai">AI: ${task.assigned_ai || 'Unassigned'}</span>
                                        <span class="tekton-dashboard__task-branch">Branch: ${task.branch || 'None'}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Add event handlers for merge buttons
        elements.modals.projectDetailBody.addEventListener('click', (event) => {
            if (event.target.classList.contains('tekton-dashboard__task-merge-btn')) {
                const taskId = event.target.getAttribute('data-task-id');
                if (taskId) {
                    handleTaskMerge(projectData.id, taskId);
                }
            }
        });
    }
    
    async function handleTaskMerge(projectId, taskId) {
        try {
            showNotification('Submitting merge request...', 'info');
            
            // For MVP, we'll simulate merge request submission
            // In production, this would get the actual repo path and branch info
            const mergeData = {
                project_id: projectId,
                task_id: taskId,
                ai_worker: 'current_ai', // Would be determined from task
                branch: `sprint/task-${taskId}`, // Would be from task data
                repo_path: process.cwd() // Would be from project data
            };
            
            const result = await tektonService.submitMergeRequest(mergeData);
            
            if (result) {
                showNotification('Merge request submitted successfully', 'success');
                // Refresh project details
                const projectId = component.state.get('modalState.projectDetail.projectId');
                if (projectId) {
                    const details = await tektonService.getProjectDetails(projectId);
                    if (details) {
                        displayProjectDetails(details);
                    }
                }
            } else {
                showNotification('Failed to submit merge request', 'error');
            }
        } catch (error) {
            console.error('Failed to submit merge request:', error);
            showNotification(`Failed to submit merge request: ${error.message}`, 'error');
        }
    }
    
    // Utility functions
    function getProgressClass(taskCount) {
        if (taskCount === 0) return 'tekton-dashboard__progress--empty';
        if (taskCount < 5) return 'tekton-dashboard__progress--low';
        if (taskCount < 10) return 'tekton-dashboard__progress--medium';
        return 'tekton-dashboard__progress--high';
    }
    
    function formatDate(dateString) {
        if (!dateString) return 'Unknown';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        } catch (error) {
            return 'Invalid date';
        }
    }
    
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
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
    
    // Merge Queue Event Handlers
    function loadMergeQueue() {
        if (!tektonService) return;
        
        showNotification('Loading merge queue...', 'info');
        
        tektonService.getMergeQueue()
            .then(queue => {
                updateMergeQueueDisplay(queue);
            })
            .catch(error => {
                console.error('Failed to load merge queue:', error);
                showNotification('Failed to load merge queue', 'error');
            });
    }
    
    function updateMergeQueueDisplay(queue) {
        const container = document.getElementById('merge-queue-container');
        if (!container) return;
        
        if (!queue || queue.length === 0) {
            container.innerHTML = '<div class="tekton-dashboard__placeholder-message">No merge requests in queue</div>';
            return;
        }
        
        container.innerHTML = queue.map(mr => createMergeRequestCard(mr)).join('');
        
        // Add click handlers
        container.addEventListener('click', (event) => {
            const card = event.target.closest('.tekton-dashboard__merge-request-card');
            if (card) {
                const mergeId = card.getAttribute('data-merge-id');
                if (mergeId) {
                    openMergeDetailModal(mergeId);
                }
            }
            
            // Handle quick actions
            if (event.target.classList.contains('tekton-dashboard__merge-action-btn')) {
                event.stopPropagation();
                const action = event.target.getAttribute('data-action');
                const mergeId = event.target.getAttribute('data-merge-id');
                
                if (action === 'merge') {
                    handleQuickMerge(mergeId);
                } else if (action === 'reject') {
                    handleQuickReject(mergeId);
                }
            }
        });
    }
    
    function createMergeRequestCard(mergeRequest) {
        const stateClass = `tekton-dashboard__merge-request-card--${mergeRequest.state}`;
        const canMerge = mergeRequest.state === 'clean' || mergeRequest.state === 'conflicted';
        
        return `
            <div class="tekton-dashboard__merge-request-card ${stateClass}" data-merge-id="${mergeRequest.id}">
                <div class="tekton-dashboard__merge-request-header">
                    <div class="tekton-dashboard__merge-request-info">
                        <h4 class="tekton-dashboard__merge-request-title">
                            ${escapeHtml(mergeRequest.ai_worker)} - Task ${mergeRequest.task_id.substring(0, 8)}
                        </h4>
                        <div class="tekton-dashboard__merge-request-branch">
                            ${escapeHtml(mergeRequest.branch)}
                        </div>
                    </div>
                    <div class="tekton-dashboard__merge-request-status">
                        <span class="tekton-dashboard__merge-state tekton-dashboard__merge-state--${mergeRequest.state}">
                            ${mergeRequest.state.replace('_', ' ')}
                        </span>
                        ${mergeRequest.state === 'conflicted' ? `
                            <span style="color: var(--color-danger); font-size: var(--font-size-sm);">
                                ${mergeRequest.conflicts_count} conflicts
                            </span>
                        ` : ''}
                    </div>
                </div>
                
                <div class="tekton-dashboard__merge-request-meta">
                    <div class="tekton-dashboard__merge-request-meta-item">
                        <span>Project:</span>
                        <strong>${mergeRequest.project_id.substring(0, 8)}</strong>
                    </div>
                    <div class="tekton-dashboard__merge-request-meta-item">
                        <span>Created:</span>
                        <strong>${formatDate(mergeRequest.created_at)}</strong>
                    </div>
                    ${mergeRequest.analyzed_at ? `
                        <div class="tekton-dashboard__merge-request-meta-item">
                            <span>Analyzed:</span>
                            <strong>${formatDate(mergeRequest.analyzed_at)}</strong>
                        </div>
                    ` : ''}
                </div>
                
                ${canMerge ? `
                    <div class="tekton-dashboard__merge-request-actions">
                        <button class="tekton-dashboard__merge-action-btn tekton-dashboard__merge-action-btn--view">
                            View Details
                        </button>
                        ${mergeRequest.state === 'clean' ? `
                            <button class="tekton-dashboard__merge-action-btn tekton-dashboard__merge-action-btn--merge"
                                    data-action="merge" 
                                    data-merge-id="${mergeRequest.id}">
                                Merge
                            </button>
                        ` : ''}
                        <button class="tekton-dashboard__merge-action-btn tekton-dashboard__merge-action-btn--reject"
                                data-action="reject" 
                                data-merge-id="${mergeRequest.id}">
                            Reject
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    function handleMergeQueueFilter(event) {
        const filter = event.target.value;
        const cards = document.querySelectorAll('.tekton-dashboard__merge-request-card');
        
        cards.forEach(card => {
            const state = card.getAttribute('data-merge-id');
            // Note: We'd need to store state as data attribute for proper filtering
            card.style.display = filter === 'all' || card.classList.contains(`tekton-dashboard__merge-request-card--${filter}`) ? 'block' : 'none';
        });
    }
    
    function handleMergeQueueSearch(event) {
        const searchTerm = event.target.value.toLowerCase();
        const cards = document.querySelectorAll('.tekton-dashboard__merge-request-card');
        
        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(searchTerm) ? 'block' : 'none';
        });
    }
    
    function openMergeDetailModal(mergeId) {
        if (!tektonService) return;
        
        // Show loading state
        const modalBody = document.getElementById('merge-modal-body');
        if (modalBody) {
            modalBody.innerHTML = '<div class="tekton-dashboard__loading">Loading merge request details...</div>';
        }
        
        // Update modal state
        component.state.set('modalState.mergeDetail', {
            isOpen: true,
            mergeId: mergeId
        });
        
        // Show modal
        const modal = document.getElementById('merge-detail-modal');
        if (modal) {
            modal.style.display = 'flex';
        }
        
        // Load merge details
        tektonService.getMergeRequestDetails(mergeId)
            .then(details => {
                displayMergeDetails(details);
            })
            .catch(error => {
                console.error('Failed to load merge details:', error);
                if (modalBody) {
                    modalBody.innerHTML = `<div class="tekton-dashboard__placeholder-message">Error: ${error.message}</div>`;
                }
            });
    }
    
    function closeMergeDetailModal() {
        // Update modal state
        component.state.set('modalState.mergeDetail', {
            isOpen: false,
            mergeId: null
        });
        
        // Hide modal
        const modal = document.getElementById('merge-detail-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    function displayMergeDetails(mergeRequest) {
        const modalBody = document.getElementById('merge-modal-body');
        if (!modalBody) return;
        
        const modalTitle = document.getElementById('merge-modal-title');
        if (modalTitle) {
            modalTitle.textContent = `Merge Request: ${mergeRequest.ai_worker} - ${mergeRequest.branch}`;
        }
        
        modalBody.innerHTML = `
            <div class="tekton-dashboard__merge-details">
                <div class="tekton-dashboard__project-info">
                    <h4>Merge Request Information</h4>
                    <div class="tekton-dashboard__info-grid">
                        <div class="tekton-dashboard__info-item">
                            <label>ID:</label>
                            <span>${mergeRequest.id}</span>
                        </div>
                        <div class="tekton-dashboard__info-item">
                            <label>Project:</label>
                            <span>${mergeRequest.project_id}</span>
                        </div>
                        <div class="tekton-dashboard__info-item">
                            <label>Task:</label>
                            <span>${mergeRequest.task_id}</span>
                        </div>
                        <div class="tekton-dashboard__info-item">
                            <label>AI Worker:</label>
                            <span>${mergeRequest.ai_worker}</span>
                        </div>
                        <div class="tekton-dashboard__info-item">
                            <label>Branch:</label>
                            <span style="font-family: var(--font-family-mono);">${mergeRequest.branch}</span>
                        </div>
                        <div class="tekton-dashboard__info-item">
                            <label>State:</label>
                            <span class="tekton-dashboard__merge-state tekton-dashboard__merge-state--${mergeRequest.state}">
                                ${mergeRequest.state.replace('_', ' ')}
                            </span>
                        </div>
                        <div class="tekton-dashboard__info-item">
                            <label>Created:</label>
                            <span>${formatDate(mergeRequest.created_at)}</span>
                        </div>
                        ${mergeRequest.analyzed_at ? `
                            <div class="tekton-dashboard__info-item">
                                <label>Analyzed:</label>
                                <span>${formatDate(mergeRequest.analyzed_at)}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                ${mergeRequest.conflicts && mergeRequest.conflicts.length > 0 ? `
                    <div class="tekton-dashboard__merge-conflict-section">
                        <h4>Conflicts (${mergeRequest.conflicts.length})</h4>
                        <div class="tekton-dashboard__conflict-list">
                            ${mergeRequest.conflicts.map(conflict => `
                                <div class="tekton-dashboard__conflict-item">
                                    <div class="tekton-dashboard__conflict-header">
                                        <span class="tekton-dashboard__conflict-type">
                                            ${conflict.type.replace('_', ' ')}
                                        </span>
                                        <span class="tekton-dashboard__conflict-severity tekton-dashboard__conflict-severity--${conflict.severity}">
                                            ${conflict.severity}
                                        </span>
                                    </div>
                                    <p>${escapeHtml(conflict.description)}</p>
                                    <div class="tekton-dashboard__conflict-files">
                                        Files: ${conflict.files.join(', ')}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${mergeRequest.options && mergeRequest.options.length > 0 ? `
                    <div class="tekton-dashboard__merge-options-section">
                        <h4>Resolution Options</h4>
                        <div class="tekton-dashboard__merge-options-container">
                            ${mergeRequest.options.map((option, index) => `
                                <div class="tekton-dashboard__merge-option ${mergeRequest.resolution_choice === option.id ? 'tekton-dashboard__merge-option--selected' : ''}" 
                                     data-option-id="${option.id}">
                                    <div class="tekton-dashboard__merge-option-header">
                                        <h5 class="tekton-dashboard__merge-option-title">
                                            Option ${String.fromCharCode(65 + index)}: ${escapeHtml(option.approach)}
                                        </h5>
                                        <span class="tekton-dashboard__merge-option-source">
                                            ${option.ai_worker} / ${option.branch}
                                        </span>
                                    </div>
                                    
                                    <div class="tekton-dashboard__merge-option-stats">
                                        <div class="tekton-dashboard__merge-option-stat">
                                            <span class="tekton-dashboard__stat-label">Code Quality:</span>
                                            <span class="tekton-dashboard__stat-value">${option.code_quality}</span>
                                        </div>
                                        <div class="tekton-dashboard__merge-option-stat">
                                            <span class="tekton-dashboard__stat-label">Test Coverage:</span>
                                            <span class="tekton-dashboard__stat-value">${option.test_coverage}</span>
                                        </div>
                                        <div class="tekton-dashboard__merge-option-stat">
                                            <span class="tekton-dashboard__stat-label">Changes:</span>
                                            <span class="tekton-dashboard__stat-value">+${option.lines_added} / -${option.lines_removed}</span>
                                        </div>
                                    </div>
                                    
                                    <div class="tekton-dashboard__merge-option-pros-cons">
                                        <div class="tekton-dashboard__pros">
                                            <h6>Pros:</h6>
                                            <ul>
                                                ${option.pros.map(pro => `<li>${escapeHtml(pro)}</li>`).join('')}
                                            </ul>
                                        </div>
                                        <div class="tekton-dashboard__cons">
                                            <h6>Cons:</h6>
                                            <ul>
                                                ${option.cons.map(con => `<li>${escapeHtml(con)}</li>`).join('')}
                                            </ul>
                                        </div>
                                    </div>
                                    
                                    <div class="tekton-dashboard__merge-option-files">
                                        <details>
                                            <summary>Files Changed (${option.files_changed.length})</summary>
                                            <ul class="tekton-dashboard__file-list">
                                                ${option.files_changed.map(file => `<li>${escapeHtml(file)}</li>`).join('')}
                                            </ul>
                                        </details>
                                    </div>
                                    
                                    <button class="tekton-dashboard__option-select-btn" data-option-id="${option.id}">
                                        Select Option ${String.fromCharCode(65 + index)}
                                    </button>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${mergeRequest.metadata ? `
                    <div class="tekton-dashboard__project-info">
                        <h4>Additional Information</h4>
                        <pre style="font-size: var(--font-size-sm); overflow: auto;">${JSON.stringify(mergeRequest.metadata, null, 2)}</pre>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Add event handlers for option selection
        modalBody.addEventListener('click', (event) => {
            if (event.target.classList.contains('tekton-dashboard__option-select-btn')) {
                const optionId = event.target.getAttribute('data-option-id');
                selectMergeOption(mergeRequest.id, optionId);
            }
        });
        
        // Update button states based on merge state
        const mergeBtn = document.getElementById('merge-modal-merge');
        const rejectBtn = document.getElementById('merge-modal-reject');
        
        if (mergeBtn) {
            // For conflicted merges, only show merge button if an option is selected
            if (mergeRequest.state === 'conflicted') {
                mergeBtn.style.display = mergeRequest.resolution_choice ? 'inline-flex' : 'none';
                mergeBtn.textContent = mergeRequest.resolution_choice ? 'Merge with Selected Option' : 'Merge';
            } else {
                mergeBtn.style.display = mergeRequest.state === 'clean' ? 'inline-flex' : 'none';
            }
        }
        if (rejectBtn) {
            rejectBtn.style.display = (mergeRequest.state !== 'merged' && mergeRequest.state !== 'rejected') ? 'inline-flex' : 'none';
        }
    }
    
    function selectMergeOption(mergeId, optionId) {
        // Update UI to show selected option
        const options = document.querySelectorAll('.tekton-dashboard__merge-option');
        options.forEach(opt => {
            opt.classList.remove('tekton-dashboard__merge-option--selected');
            if (opt.getAttribute('data-option-id') === optionId) {
                opt.classList.add('tekton-dashboard__merge-option--selected');
            }
        });
        
        // Store selected option in component state
        const currentState = component.state.get('modalState.mergeDetail');
        component.state.set('modalState.mergeDetail', {
            ...currentState,
            selectedOption: optionId
        });
        
        // Enable merge button
        const mergeBtn = document.getElementById('merge-modal-merge');
        if (mergeBtn) {
            mergeBtn.style.display = 'inline-flex';
            mergeBtn.textContent = 'Merge with Selected Option';
        }
        
        showNotification(`Selected Option ${optionId === 'option_a' ? 'A' : 'B'}`, 'info');
    }
    
    async function handleMergeMergeRequest() {
        const mergeId = component.state.get('modalState.mergeDetail.mergeId');
        const selectedOption = component.state.get('modalState.mergeDetail.selectedOption');
        if (!mergeId || !tektonService) return;
        
        // Check if we need to resolve conflicts first
        const mergeDetails = await tektonService.getMergeRequestDetails(mergeId);
        if (mergeDetails.state === 'conflicted' && !selectedOption && !mergeDetails.resolution_choice) {
            showNotification('Please select a resolution option first', 'warning');
            return;
        }
        
        if (!confirm('Are you sure you want to merge this request?')) {
            return;
        }
        
        try {
            // If conflicted and option selected, resolve first
            if (mergeDetails.state === 'conflicted' && selectedOption) {
                showNotification('Resolving conflicts...', 'info');
                
                const resolveResult = await tektonService.resolveConflict(mergeId, selectedOption);
                if (!resolveResult) {
                    showNotification('Failed to resolve conflicts', 'error');
                    return;
                }
            }
            
            showNotification('Executing merge...', 'info');
            
            const result = await tektonService.executeMerge(mergeId);
            
            if (result) {
                showNotification('Merge executed successfully', 'success');
                closeMergeDetailModal();
                loadMergeQueue(); // Refresh the queue
            } else {
                showNotification('Failed to execute merge', 'error');
            }
        } catch (error) {
            console.error('Failed to execute merge:', error);
            showNotification(`Failed to execute merge: ${error.message}`, 'error');
        }
    }
    
    async function handleRejectMergeRequest() {
        const mergeId = component.state.get('modalState.mergeDetail.mergeId');
        if (!mergeId || !tektonService) return;
        
        const reason = prompt('Please provide a reason for rejecting this merge request:');
        if (!reason) {
            return;
        }
        
        try {
            showNotification('Rejecting merge request...', 'info');
            
            const result = await tektonService.rejectMergeRequest(mergeId, reason);
            
            if (result) {
                showNotification('Merge request rejected', 'success');
                closeMergeDetailModal();
                loadMergeQueue(); // Refresh the queue
            } else {
                showNotification('Failed to reject merge request', 'error');
            }
        } catch (error) {
            console.error('Failed to reject merge request:', error);
            showNotification(`Failed to reject merge request: ${error.message}`, 'error');
        }
    }
    
    async function handleQuickMerge(mergeId) {
        if (!confirm('Are you sure you want to merge this request?')) {
            return;
        }
        
        try {
            showNotification('Executing merge...', 'info');
            const result = await tektonService.executeMerge(mergeId);
            
            if (result) {
                showNotification('Merge executed successfully', 'success');
                loadMergeQueue();
            } else {
                showNotification('Failed to execute merge', 'error');
            }
        } catch (error) {
            console.error('Failed to execute merge:', error);
            showNotification(`Failed to execute merge: ${error.message}`, 'error');
        }
    }
    
    async function handleQuickReject(mergeId) {
        const reason = prompt('Please provide a reason for rejecting this merge request:');
        if (!reason) {
            return;
        }
        
        try {
            showNotification('Rejecting merge request...', 'info');
            const result = await tektonService.rejectMergeRequest(mergeId, reason);
            
            if (result) {
                showNotification('Merge request rejected', 'success');
                loadMergeQueue();
            } else {
                showNotification('Failed to reject merge request', 'error');
            }
        } catch (error) {
            console.error('Failed to reject merge request:', error);
            showNotification(`Failed to reject merge request: ${error.message}`, 'error');
        }
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
        handleConnectionFailure,
        loadMergeQueue,
        handleMergeQueueFilter,
        handleMergeQueueSearch,
        openMergeDetailModal,
        closeMergeDetailModal,
        handleMergeMergeRequest,
        handleRejectMergeRequest
    });
    
})(component);