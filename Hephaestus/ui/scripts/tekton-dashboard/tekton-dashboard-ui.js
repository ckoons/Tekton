/**
 * Tekton Dashboard UI
 * UI update functions for the Tekton Dashboard component
 */

console.log('[FILE_TRACE] Loading: tekton-dashboard-ui.js');
(function(component) {
    // Load components data
    function loadComponents() {
        if (!tektonService) return;
        
        // Show loading state
        if (elements.containers.componentsGrid) {
            elements.containers.componentsGrid.innerHTML = '<div class="tekton-dashboard__loading">Loading components...</div>';
        }
        
        // Get components from service
        tektonService.getComponents()
            .catch(error => {
                console.error('Failed to load components:', error);
                showNotification('Failed to load components', 'error');
            });
    }
    
    // Update components display
    function updateComponentsDisplay(components) {
        // Update grid view
        updateComponentsGridView(components);
        
        // Update list view
        updateComponentsListView(components);
    }
    
    // Update components grid view
    function updateComponentsGridView(components) {
        if (!elements.containers.componentsGrid) return;
        
        // Apply filters
        const filter = component.state.get('componentFilter');
        const searchTerm = component.state.get('searchTerms.components');
        const filteredComponents = filterComponentsList(components, filter, searchTerm);
        
        // Check if there are components to display
        if (filteredComponents.length === 0) {
            elements.containers.componentsGrid.innerHTML = '<div class="tekton-dashboard__placeholder-message">No components match the current filters</div>';
            return;
        }
        
        // Generate HTML for grid view
        const html = filteredComponents.map(comp => `
            <div class="tekton-dashboard__component-card" data-component-id="${comp.id}">
                <div class="tekton-dashboard__component-header">
                    <div class="tekton-dashboard__component-icon">${comp.icon || '🧩'}</div>
                    <div>
                        <h3 class="tekton-dashboard__component-title">${comp.name}</h3>
                        <div class="tekton-dashboard__component-type">${comp.type || 'Component'}</div>
                    </div>
                </div>
                <div class="tekton-dashboard__component-status">
                    <div class="tekton-dashboard__status-indicator tekton-dashboard__status-indicator--${comp.status || 'unknown'}">
                        <span>${getStatusIcon(comp.status)}</span>
                        <span>${capitalizeFirstLetter(comp.status || 'unknown')}</span>
                    </div>
                </div>
                <div class="tekton-dashboard__component-metrics">
                    <div class="tekton-dashboard__component-metric">
                        <div class="tekton-dashboard__metric-label">CPU</div>
                        <div>${formatMetricValue(comp.metrics?.cpu || 0, '%')}</div>
                    </div>
                    <div class="tekton-dashboard__component-metric">
                        <div class="tekton-dashboard__metric-label">Memory</div>
                        <div>${formatByteSize(comp.metrics?.memory || 0)}</div>
                    </div>
                    <div class="tekton-dashboard__component-metric">
                        <div class="tekton-dashboard__metric-label">Uptime</div>
                        <div>${formatUptime(comp.uptime)}</div>
                    </div>
                </div>
                <div class="tekton-dashboard__component-actions">
                    <button class="tekton-dashboard__action-button" data-action="view" data-component-id="${comp.id}">
                        <span class="tekton-dashboard__action-icon">👁️</span>
                    </button>
                    <button class="tekton-dashboard__action-button" data-action="${comp.status === 'running' ? 'stop' : 'start'}" data-component-id="${comp.id}">
                        <span class="tekton-dashboard__action-icon">${comp.status === 'running' ? '⏹️' : '▶️'}</span>
                    </button>
                    <button class="tekton-dashboard__action-button" data-action="restart" data-component-id="${comp.id}">
                        <span class="tekton-dashboard__action-icon">🔄</span>
                    </button>
                </div>
            </div>
        `).join('');
        
        // Update container
        elements.containers.componentsGrid.innerHTML = html;
        
        // Add event listeners to component cards
        const componentCards = component.$$('.tekton-dashboard__component-card');
        componentCards.forEach(card => {
            card.addEventListener('click', (e) => {
                // Check if clicked on an action button
                if (e.target.closest('.tekton-dashboard__action-button')) {
                    return;
                }
                
                const componentId = card.getAttribute('data-component-id');
                openComponentDetailModal(componentId);
            });
        });
        
        // Add event listeners to action buttons
        const actionButtons = component.$$('.tekton-dashboard__component-actions .tekton-dashboard__action-button');
        actionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent opening the modal
                
                const action = button.getAttribute('data-action');
                const componentId = button.getAttribute('data-component-id');
                
                handleComponentButtonAction(action, componentId);
            });
        });
    }
    
    // Update components list view
    function updateComponentsListView(components) {
        if (!elements.containers.componentsTable) return;
        
        // Apply filters
        const filter = component.state.get('componentFilter');
        const searchTerm = component.state.get('searchTerms.components');
        const filteredComponents = filterComponentsList(components, filter, searchTerm);
        
        // Generate HTML for list view
        const html = filteredComponents.map(comp => `
            <tr>
                <td>
                    <div class="tekton-dashboard__status-indicator tekton-dashboard__status-indicator--${comp.status || 'unknown'}">
                        <span>${getStatusIcon(comp.status)}</span>
                        <span>${capitalizeFirstLetter(comp.status || 'unknown')}</span>
                    </div>
                </td>
                <td>
                    <strong>${comp.name}</strong>
                    <div class="tekton-dashboard__component-id">${comp.id}</div>
                </td>
                <td>${comp.type || 'Component'}</td>
                <td>${comp.version || '-'}</td>
                <td>
                    <div>CPU: ${formatMetricValue(comp.metrics?.cpu || 0, '%')}</div>
                    <div>Memory: ${formatByteSize(comp.metrics?.memory || 0)}</div>
                    <div>Uptime: ${formatUptime(comp.uptime)}</div>
                </td>
                <td>
                    <div class="tekton-dashboard__component-actions">
                        <button class="tekton-dashboard__action-button" data-action="view" data-component-id="${comp.id}">
                            <span class="tekton-dashboard__action-icon">👁️</span>
                        </button>
                        <button class="tekton-dashboard__action-button" data-action="${comp.status === 'running' ? 'stop' : 'start'}" data-component-id="${comp.id}">
                            <span class="tekton-dashboard__action-icon">${comp.status === 'running' ? '⏹️' : '▶️'}</span>
                        </button>
                        <button class="tekton-dashboard__action-button" data-action="restart" data-component-id="${comp.id}">
                            <span class="tekton-dashboard__action-icon">🔄</span>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
        
        // Update container
        elements.containers.componentsTable.innerHTML = html || `
            <tr>
                <td colspan="6">
                    <div class="tekton-dashboard__placeholder-message">No components match the current filters</div>
                </td>
            </tr>
        `;
        
        // Add event listeners to view buttons
        const viewButtons = component.$$('.tekton-dashboard__component-actions .tekton-dashboard__action-button[data-action="view"]');
        viewButtons.forEach(button => {
            button.addEventListener('click', () => {
                const componentId = button.getAttribute('data-component-id');
                openComponentDetailModal(componentId);
            });
        });
        
        // Add event listeners to other action buttons
        const actionButtons = component.$$('.tekton-dashboard__component-actions .tekton-dashboard__action-button:not([data-action="view"])');
        actionButtons.forEach(button => {
            button.addEventListener('click', () => {
                const action = button.getAttribute('data-action');
                const componentId = button.getAttribute('data-component-id');
                
                handleComponentButtonAction(action, componentId);
            });
        });
    }
    
    // Update component status grid on system status tab
    function updateComponentStatusGrid(components) {
        if (!elements.containers.componentGrid) return;
        
        // Generate HTML for component grid
        const html = components.map(comp => `
            <div class="tekton-dashboard__component-card" data-component-id="${comp.id}">
                <div class="tekton-dashboard__component-header">
                    <div class="tekton-dashboard__component-icon">${comp.icon || '🧩'}</div>
                    <div>
                        <h3 class="tekton-dashboard__component-title">${comp.name}</h3>
                        <div class="tekton-dashboard__component-type">${comp.type || 'Component'}</div>
                    </div>
                </div>
                <div class="tekton-dashboard__component-status">
                    <div class="tekton-dashboard__status-indicator tekton-dashboard__status-indicator--${comp.status || 'unknown'}">
                        <span>${getStatusIcon(comp.status)}</span>
                        <span>${capitalizeFirstLetter(comp.status || 'unknown')}</span>
                    </div>
                </div>
                <div class="tekton-dashboard__component-metrics">
                    <div class="tekton-dashboard__component-metric">
                        <div class="tekton-dashboard__metric-label">CPU</div>
                        <div>${formatMetricValue(comp.metrics?.cpu || 0, '%')}</div>
                    </div>
                    <div class="tekton-dashboard__component-metric">
                        <div class="tekton-dashboard__metric-label">Memory</div>
                        <div>${formatByteSize(comp.metrics?.memory || 0)}</div>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Update container
        elements.containers.componentGrid.innerHTML = html || '<div class="tekton-dashboard__placeholder-message">No components found</div>';
        
        // Add event listeners to component cards
        const componentCards = component.$$('#component-status-grid .tekton-dashboard__component-card');
        componentCards.forEach(card => {
            card.addEventListener('click', () => {
                const componentId = card.getAttribute('data-component-id');
                openComponentDetailModal(componentId);
            });
        });
    }
    
    // Filter components based on filter and search term
    function filterComponentsList(components, filter, searchTerm) {
        return components.filter(comp => {
            // Apply type filter
            if (filter !== 'all' && comp.type !== filter) {
                return false;
            }
            
            // Apply search term
            if (searchTerm && !compMatchesSearch(comp, searchTerm)) {
                return false;
            }
            
            return true;
        });
    }
    
    // Check if component matches search term
    function compMatchesSearch(comp, term) {
        return comp.name.toLowerCase().includes(term) || 
               comp.id.toLowerCase().includes(term) || 
               (comp.description && comp.description.toLowerCase().includes(term));
    }
    
    // Handle component action button click
    function handleComponentButtonAction(action, componentId) {
        if (!tektonService) return;
        
        // Find component
        const component = tektonService.components.find(c => c.id === componentId);
        if (!component) return;
        
        // Handle different actions
        switch (action) {
            case 'start':
                // Show notification
                showNotification(`Starting component ${component.name}...`, 'info');
                
                // Start component
                tektonService.startComponent(componentId)
                    .then(success => {
                        if (success) {
                            showNotification(`Started component ${component.name} successfully`, 'success');
                        } else {
                            showNotification(`Failed to start component ${component.name}`, 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Failed to start component:', error);
                        showNotification(`Failed to start component: ${error.message}`, 'error');
                    });
                break;
                
            case 'stop':
                // Confirm stop
                if (!confirm(`Are you sure you want to stop component ${component.name}?`)) {
                    return;
                }
                
                // Show notification
                showNotification(`Stopping component ${component.name}...`, 'info');
                
                // Stop component
                tektonService.stopComponent(componentId)
                    .then(success => {
                        if (success) {
                            showNotification(`Stopped component ${component.name} successfully`, 'success');
                        } else {
                            showNotification(`Failed to stop component ${component.name}`, 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Failed to stop component:', error);
                        showNotification(`Failed to stop component: ${error.message}`, 'error');
                    });
                break;
                
            case 'restart':
                // Confirm restart
                if (!confirm(`Are you sure you want to restart component ${component.name}?`)) {
                    return;
                }
                
                // Show notification
                showNotification(`Restarting component ${component.name}...`, 'info');
                
                // Restart component (stop then start)
                tektonService.stopComponent(componentId)
                    .then(stopSuccess => {
                        if (stopSuccess) {
                            // Wait a bit for component to fully stop
                            setTimeout(() => {
                                tektonService.startComponent(componentId)
                                    .then(startSuccess => {
                                        if (startSuccess) {
                                            showNotification(`Restarted component ${component.name} successfully`, 'success');
                                        } else {
                                            showNotification(`Stopped component ${component.name}, but failed to start it again`, 'error');
                                        }
                                    })
                                    .catch(error => {
                                        console.error('Failed to start component after stop:', error);
                                        showNotification(`Stopped component ${component.name}, but failed to start it again: ${error.message}`, 'error');
                                    });
                            }, 1000);
                        } else {
                            showNotification(`Failed to stop component ${component.name} for restart`, 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Failed to stop component for restart:', error);
                        showNotification(`Failed to restart component: ${error.message}`, 'error');
                    });
                break;
        }
    }
    
    // Load logs data
    function loadLogs() {
        if (!tektonService) return;
        
        // Show loading state
        if (elements.containers.logContent) {
            elements.containers.logContent.innerHTML = '<div class="tekton-dashboard__loading">Loading logs...</div>';
        }
        
        // Get filters from state
        const component = component.state.get('logSettings.component');
        const level = component.state.get('logSettings.level');
        const maxLines = component.state.get('logSettings.maxLines');
        
        // Create filters object
        const filters = {
            limit: maxLines
        };
        
        if (component) {
            filters.component = component;
        }
        
        if (level && level !== 'all') {
            filters.level = level;
        }
        
        // Get logs from service
        tektonService.getSystemLogs(filters)
            .catch(error => {
                console.error('Failed to load logs:', error);
                showNotification('Failed to load logs', 'error');
            });
    }
    
    // Update logs display
    function updateLogsDisplay(logs) {
        if (!elements.containers.logContent) return;
        
        // Apply line wrapping
        const wrapLines = component.state.get('logSettings.wrapLines');
        elements.containers.logContent.style.whiteSpace = wrapLines ? 'pre-wrap' : 'pre';
        
        // Check if there are logs to display
        if (!logs || logs.length === 0) {
            elements.containers.logContent.innerHTML = '<div class="tekton-dashboard__placeholder-message">No logs found</div>';
            return;
        }
        
        // Generate HTML for logs
        const html = logs.map(log => formatLogEntry(log)).join('\n');
        
        // Update container
        elements.containers.logContent.innerHTML = html;
        
        // Scroll to bottom if auto-update is enabled
        if (component.state.get('logSettings.autoUpdate')) {
            elements.containers.logContent.scrollTop = elements.containers.logContent.scrollHeight;
        }
    }
    
    // Add a single log entry to the display
    function addLogEntryToDisplay(log) {
        if (!elements.containers.logContent) return;
        
        // Format log entry
        const formattedLog = formatLogEntry(log);
        
        // Check if container has placeholder
        if (elements.containers.logContent.querySelector('.tekton-dashboard__placeholder-message')) {
            elements.containers.logContent.innerHTML = formattedLog;
        } else {
            // Prepend to container (since logs are in reverse chronological order)
            elements.containers.logContent.innerHTML = formattedLog + '\n' + elements.containers.logContent.innerHTML;
            
            // Trim log entries if they exceed max lines
            const maxLines = component.state.get('logSettings.maxLines');
            const logEntries = elements.containers.logContent.innerHTML.split('\n');
            
            if (logEntries.length > maxLines) {
                elements.containers.logContent.innerHTML = logEntries.slice(0, maxLines).join('\n');
            }
        }
        
        // Scroll to top (since newest logs are at the top)
        elements.containers.logContent.scrollTop = 0;
    }
    
    // Format a log entry for display
    function formatLogEntry(log) {
        const timestamp = new Date(log.timestamp).toLocaleTimeString();
        const level = log.level ? log.level.toUpperCase() : 'INFO';
        const component = log.component || 'system';
        const message = log.message || '';
        
        // Apply color based on log level
        let levelClass = '';
        switch (level) {
            case 'ERROR':
                levelClass = 'color: var(--color-danger);';
                break;
            case 'WARN':
                levelClass = 'color: var(--color-warning);';
                break;
            case 'INFO':
                levelClass = 'color: var(--color-info);';
                break;
            case 'DEBUG':
                levelClass = 'color: var(--text-secondary);';
                break;
        }
        
        return `<span style="color: var(--text-secondary);">[${timestamp}]</span> <span style="${levelClass}">[${level}]</span> <span style="color: var(--color-primary);">[${component}]</span> ${message}`;
    }
    
    // Update log component filter dropdown
    function updateLogComponentFilter(components) {
        if (!elements.buttons.logsComponentFilter) return;
        
        // Get current selected value
        const currentValue = elements.buttons.logsComponentFilter.value;
        
        // Generate options HTML
        const html = `
            <option value="all">All Components</option>
            ${components.map(comp => `<option value="${comp.id}">${comp.name}</option>`).join('')}
        `;
        
        // Update dropdown
        elements.buttons.logsComponentFilter.innerHTML = html;
        
        // Restore selected value if it exists in the new options
        if (currentValue && currentValue !== 'all') {
            const exists = Array.from(elements.buttons.logsComponentFilter.options).some(opt => opt.value === currentValue);
            if (exists) {
                elements.buttons.logsComponentFilter.value = currentValue;
            }
        }
    }
    
    // Load projects data
    function loadProjects() {
        if (!tektonService) return;
        
        // Show loading state
        if (elements.containers.projectsList) {
            elements.containers.projectsList.innerHTML = '<div class="tekton-dashboard__loading">Loading projects...</div>';
        }
        
        // Get projects from service
        tektonService.getProjects()
            .catch(error => {
                console.error('Failed to load projects:', error);
                showNotification('Failed to load projects', 'error');
            });
    }
    
    // Update projects display
    function updateProjectsDisplay(projects) {
        if (!elements.containers.projectsList) return;
        
        // Apply filters
        const filter = component.state.get('projectFilter');
        const searchTerm = component.state.get('searchTerms.projects');
        const filteredProjects = filterProjectsList(projects, filter, searchTerm);
        
        // Check if there are projects to display
        if (filteredProjects.length === 0) {
            elements.containers.projectsList.innerHTML = `
                <div class="tekton-dashboard__placeholder-message">
                    ${searchTerm || filter !== 'all' ? 
                      'No projects match the current filters' : 
                      'No projects found. Create your first project using the "New Project" button.'}
                </div>
            `;
            return;
        }
        
        // Generate HTML for projects
        const html = filteredProjects.map(project => `
            <div class="tekton-dashboard__project-card" data-project-id="${project.id}">
                <div class="tekton-dashboard__project-header">
                    <h3 class="tekton-dashboard__project-title">${project.name}</h3>
                    <div class="tekton-dashboard__status-indicator tekton-dashboard__status-indicator--${project.status === 'archived' ? 'stopped' : 'running'}">
                        <span>${project.status === 'archived' ? '📁' : '🟢'}</span>
                        <span>${capitalizeFirstLetter(project.status || 'active')}</span>
                    </div>
                </div>
                <div class="tekton-dashboard__project-desc">${project.description || 'No description'}</div>
                <div class="tekton-dashboard__project-meta">
                    ${project.repoUrl ? `
                        <div class="tekton-dashboard__project-meta-item">
                            <span>📂</span>
                            <span>Repository</span>
                        </div>
                    ` : ''}
                    <div class="tekton-dashboard__project-meta-item">
                        <span>📅</span>
                        <span>Created: ${formatDate(project.createdAt)}</span>
                    </div>
                    <div class="tekton-dashboard__project-meta-item">
                        <span>🔄</span>
                        <span>Updated: ${formatDate(project.updatedAt)}</span>
                    </div>
                </div>
                <div class="tekton-dashboard__project-actions">
                    <button class="tekton-dashboard__action-button" data-action="open" data-project-id="${project.id}">
                        <span class="tekton-dashboard__action-icon">📂</span>
                    </button>
                    <button class="tekton-dashboard__action-button" data-action="${project.status === 'archived' ? 'restore' : 'archive'}" data-project-id="${project.id}">
                        <span class="tekton-dashboard__action-icon">${project.status === 'archived' ? '🔄' : '📁'}</span>
                    </button>
                </div>
            </div>
        `).join('');
        
        // Update container
        elements.containers.projectsList.innerHTML = html;
        
        // Add event listeners to project cards
        const projectCards = component.$$('.tekton-dashboard__project-card');
        projectCards.forEach(card => {
            card.addEventListener('click', (e) => {
                // Check if clicked on an action button
                if (e.target.closest('.tekton-dashboard__action-button')) {
                    return;
                }
                
                const projectId = card.getAttribute('data-project-id');
                openProjectDetailModal(projectId);
            });
        });
        
        // Add event listeners to action buttons
        const actionButtons = component.$$('.tekton-dashboard__project-actions .tekton-dashboard__action-button');
        actionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent opening the modal
                
                const action = button.getAttribute('data-action');
                const projectId = button.getAttribute('data-project-id');
                
                handleProjectButtonAction(action, projectId);
            });
        });
    }
    
    // Filter projects based on filter and search term
    function filterProjectsList(projects, filter, searchTerm) {
        return projects.filter(project => {
            // Apply status filter
            if (filter === 'active' && project.status === 'archived') {
                return false;
            }
            
            if (filter === 'archived' && project.status !== 'archived') {
                return false;
            }
            
            // Apply search term
            if (searchTerm && !projectMatchesSearch(project, searchTerm)) {
                return false;
            }
            
            return true;
        });
    }
    
    // Check if project matches search term
    function projectMatchesSearch(project, term) {
        return project.name.toLowerCase().includes(term) || 
               project.id.toLowerCase().includes(term) || 
               (project.description && project.description.toLowerCase().includes(term));
    }
    
    // Handle project action button click
    function handleProjectButtonAction(action, projectId) {
        // Find project
        const project = tektonService.projects.find(p => p.id === projectId);
        if (!project) return;
        
        // Handle different actions
        switch (action) {
            case 'open':
                // TODO: Implement open project action
                showNotification('Opening project is not yet implemented', 'info');
                break;
                
            case 'archive':
                // TODO: Implement archive project action
                showNotification('Archiving project is not yet implemented', 'info');
                break;
                
            case 'restore':
                // TODO: Implement restore project action
                showNotification('Restoring project is not yet implemented', 'info');
                break;
        }
    }
    
    // Load resource metrics
    function loadResourceMetrics() {
        if (!tektonService) return;
        
        // Update resource charts with current time range
        updateResourceCharts();
    }
    
    // Update view mode
    function updateViewMode(viewMode) {
        // Update view buttons
        elements.buttons.viewButtons.forEach(btn => {
            const isActive = btn.getAttribute('data-view') === viewMode;
            btn.classList.toggle('tekton-dashboard__view-button--active', isActive);
        });
        
        // Update view displays
        if (elements.containers.componentsGrid && elements.containers.componentsList) {
            if (viewMode === 'grid') {
                elements.containers.componentsGrid.style.display = 'grid';
                elements.containers.componentsList.style.display = 'none';
            } else {
                elements.containers.componentsGrid.style.display = 'none';
                elements.containers.componentsList.style.display = 'block';
            }
        }
    }
    
    // Update system status display
    function updateSystemStatus(status) {
        // Update alert container if there are alerts
        if (elements.containers.systemAlerts) {
            if (status.alerts && status.alerts.length > 0) {
                const alertsHtml = status.alerts.map(alert => `
                    <div class="tekton-dashboard__alert tekton-dashboard__alert--${alert.level || 'info'}">
                        <div class="tekton-dashboard__alert-icon">${getAlertIcon(alert.level)}</div>
                        <div class="tekton-dashboard__alert-content">
                            <div class="tekton-dashboard__alert-title">${alert.title}</div>
                            <div class="tekton-dashboard__alert-message">${alert.message}</div>
                            ${alert.timestamp ? `<div class="tekton-dashboard__alert-time">${formatDate(alert.timestamp)}</div>` : ''}
                        </div>
                    </div>
                `).join('');
                
                elements.containers.systemAlerts.innerHTML = alertsHtml;
            } else {
                elements.containers.systemAlerts.innerHTML = '<div class="tekton-dashboard__placeholder-message">No active alerts</div>';
            }
        }
    }
    
    // Update metrics display
    function updateMetricsDisplay(metrics) {
        // Update main metrics text displays
        if (elements.metrics.cpuUsage && metrics.cpu !== undefined) {
            elements.metrics.cpuUsage.textContent = formatMetricValue(metrics.cpu, '%');
        }
        
        if (elements.metrics.memoryUsage && metrics.memory !== undefined) {
            elements.metrics.memoryUsage.textContent = formatByteSize(metrics.memory);
        }
        
        if (elements.metrics.diskUsage && metrics.disk !== undefined) {
            elements.metrics.diskUsage.textContent = formatMetricValue(metrics.disk, '%');
        }
        
        if (elements.metrics.networkUsage && metrics.network !== undefined) {
            elements.metrics.networkUsage.textContent = formatByteSize(metrics.network) + '/s';
        }
        
        // Update process tables
        if (metrics.processes) {
            updateProcessTables(metrics.processes);
        }
    }
    
    // Update process tables
    function updateProcessTables(processes) {
        // Update CPU processes table
        if (elements.containers.cpuProcesses && processes.cpu) {
            const cpuHtml = processes.cpu.map(proc => `
                <tr>
                    <td>${proc.name || 'Unknown'}</td>
                    <td>${proc.component || 'System'}</td>
                    <td>${formatMetricValue(proc.cpu, '%')}</td>
                    <td>${formatByteSize(proc.memory)}</td>
                    <td>${formatUptime(proc.runtime)}</td>
                </tr>
            `).join('');
            
            elements.containers.cpuProcesses.innerHTML = cpuHtml || `
                <tr>
                    <td colspan="5">
                        <div class="tekton-dashboard__placeholder-message">No process data available</div>
                    </td>
                </tr>
            `;
        }
        
        // Update memory processes table
        if (elements.containers.memoryProcesses && processes.memory) {
            const memoryHtml = processes.memory.map(proc => `
                <tr>
                    <td>${proc.name || 'Unknown'}</td>
                    <td>${proc.component || 'System'}</td>
                    <td>${formatByteSize(proc.memory)}</td>
                    <td>${formatMetricValue(proc.cpu, '%')}</td>
                    <td>${formatUptime(proc.runtime)}</td>
                </tr>
            `).join('');
            
            elements.containers.memoryProcesses.innerHTML = memoryHtml || `
                <tr>
                    <td colspan="5">
                        <div class="tekton-dashboard__placeholder-message">No process data available</div>
                    </td>
                </tr>
            `;
        }
    }
    
    // Display component details in modal
    function displayComponentDetails(component) {
        if (!elements.modals.componentDetailBody || !elements.modals.componentDetailTitle) return;
        
        // Update modal title
        elements.modals.componentDetailTitle.textContent = component.name || 'Component Details';
        
        // Update action button text based on component status
        if (elements.modals.componentDetailAction) {
            elements.modals.componentDetailAction.textContent = component.status === 'running' ? 'Stop' : 'Start';
        }
        
        // Generate component details HTML
        const html = `
            <div class="tekton-dashboard__detail-header">
                <div class="tekton-dashboard__detail-icon">${component.icon || '🧩'}</div>
                <div class="tekton-dashboard__detail-title-container">
                    <h3 class="tekton-dashboard__detail-title">${component.name}</h3>
                    <div class="tekton-dashboard__detail-id">${component.id}</div>
                </div>
                <div class="tekton-dashboard__detail-status">
                    <div class="tekton-dashboard__status-indicator tekton-dashboard__status-indicator--${component.status || 'unknown'}">
                        <span>${getStatusIcon(component.status)}</span>
                        <span>${capitalizeFirstLetter(component.status || 'unknown')}</span>
                    </div>
                </div>
            </div>
            
            <div class="tekton-dashboard__detail-section">
                <h4 class="tekton-dashboard__detail-section-title">Overview</h4>
                <div class="tekton-dashboard__detail-grid">
                    <div class="tekton-dashboard__detail-item">
                        <div class="tekton-dashboard__detail-label">Type:</div>
                        <div class="tekton-dashboard__detail-value">${component.type || 'Component'}</div>
                    </div>
                    <div class="tekton-dashboard__detail-item">
                        <div class="tekton-dashboard__detail-label">Version:</div>
                        <div class="tekton-dashboard__detail-value">${component.version || '-'}</div>
                    </div>
                    <div class="tekton-dashboard__detail-item">
                        <div class="tekton-dashboard__detail-label">Uptime:</div>
                        <div class="tekton-dashboard__detail-value">${formatUptime(component.uptime)}</div>
                    </div>
                    <div class="tekton-dashboard__detail-item">
                        <div class="tekton-dashboard__detail-label">Port:</div>
                        <div class="tekton-dashboard__detail-value">${component.port || '-'}</div>
                    </div>
                </div>
            </div>
            
            <div class="tekton-dashboard__detail-section">
                <h4 class="tekton-dashboard__detail-section-title">Description</h4>
                <div class="tekton-dashboard__detail-text">
                    ${component.description || 'No description available.'}
                </div>
            </div>
            
            <div class="tekton-dashboard__detail-section">
                <h4 class="tekton-dashboard__detail-section-title">Resources</h4>
                <div class="tekton-dashboard__detail-grid">
                    <div class="tekton-dashboard__detail-item">
                        <div class="tekton-dashboard__detail-label">CPU Usage:</div>
                        <div class="tekton-dashboard__detail-value">${formatMetricValue(component.metrics?.cpu || 0, '%')}</div>
                    </div>
                    <div class="tekton-dashboard__detail-item">
                        <div class="tekton-dashboard__detail-label">Memory Usage:</div>
                        <div class="tekton-dashboard__detail-value">${formatByteSize(component.metrics?.memory || 0)}</div>
                    </div>
                    <div class="tekton-dashboard__detail-item">
                        <div class="tekton-dashboard__detail-label">Disk Usage:</div>
                        <div class="tekton-dashboard__detail-value">${formatByteSize(component.metrics?.disk || 0)}</div>
                    </div>
                    <div class="tekton-dashboard__detail-item">
                        <div class="tekton-dashboard__detail-label">Network I/O:</div>
                        <div class="tekton-dashboard__detail-value">${formatByteSize(component.metrics?.network || 0)}/s</div>
                    </div>
                </div>
            </div>
            
            ${component.dependencies?.length > 0 ? `
                <div class="tekton-dashboard__detail-section">
                    <h4 class="tekton-dashboard__detail-section-title">Dependencies</h4>
                    <ul class="tekton-dashboard__detail-list">
                        ${component.dependencies.map(dep => `
                            <li>${dep.name || dep}</li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${component.capabilities?.length > 0 ? `
                <div class="tekton-dashboard__detail-section">
                    <h4 class="tekton-dashboard__detail-section-title">Capabilities</h4>
                    <div class="tekton-dashboard__detail-tags">
                        ${component.capabilities.map(cap => `
                            <span class="tekton-dashboard__detail-tag">${cap}</span>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        `;
        
        // Update modal content
        elements.modals.componentDetailBody.innerHTML = html;
    }
    
    // Display project details in modal
    function displayProjectDetails(project) {
        if (!elements.modals.projectDetailBody || !elements.modals.projectDetailTitle) return;
        
        // Update modal title
        elements.modals.projectDetailTitle.textContent = project.name || 'Project Details';
        
        // Update action button text
        if (elements.modals.projectDetailAction) {
            elements.modals.projectDetailAction.textContent = 'Open Project';
        }
        
        // Generate project details HTML
        const html = `
            <div class="tekton-dashboard__detail-header">
                <div class="tekton-dashboard__detail-icon">📂</div>
                <div class="tekton-dashboard__detail-title-container">
                    <h3 class="tekton-dashboard__detail-title">${project.name}</h3>
                    <div class="tekton-dashboard__detail-id">${project.id}</div>
                </div>
                <div class="tekton-dashboard__detail-status">
                    <div class="tekton-dashboard__status-indicator tekton-dashboard__status-indicator--${project.status === 'archived' ? 'stopped' : 'running'}">
                        <span>${project.status === 'archived' ? '📁' : '🟢'}</span>
                        <span>${capitalizeFirstLetter(project.status || 'active')}</span>
                    </div>
                </div>
            </div>
            
            <div class="tekton-dashboard__detail-section">
                <h4 class="tekton-dashboard__detail-section-title">Description</h4>
                <div class="tekton-dashboard__detail-text">
                    ${project.description || 'No description available.'}
                </div>
            </div>
            
            <div class="tekton-dashboard__detail-section">
                <h4 class="tekton-dashboard__detail-section-title">Details</h4>
                <div class="tekton-dashboard__detail-grid">
                    <div class="tekton-dashboard__detail-item">
                        <div class="tekton-dashboard__detail-label">Created:</div>
                        <div class="tekton-dashboard__detail-value">${formatDate(project.createdAt)}</div>
                    </div>
                    <div class="tekton-dashboard__detail-item">
                        <div class="tekton-dashboard__detail-label">Updated:</div>
                        <div class="tekton-dashboard__detail-value">${formatDate(project.updatedAt)}</div>
                    </div>
                    <div class="tekton-dashboard__detail-item">
                        <div class="tekton-dashboard__detail-label">Type:</div>
                        <div class="tekton-dashboard__detail-value">${project.type || project.template || 'Standard'}</div>
                    </div>
                    <div class="tekton-dashboard__detail-item">
                        <div class="tekton-dashboard__detail-label">Repository:</div>
                        <div class="tekton-dashboard__detail-value">${project.repoUrl || 'Not specified'}</div>
                    </div>
                </div>
            </div>
            
            ${project.components?.length > 0 ? `
                <div class="tekton-dashboard__detail-section">
                    <h4 class="tekton-dashboard__detail-section-title">Components</h4>
                    <ul class="tekton-dashboard__detail-list">
                        ${project.components.map(comp => `
                            <li>${comp.name || comp}</li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
        
        // Update modal content
        elements.modals.projectDetailBody.innerHTML = html;
    }
    
    // Display health check results
    function displayHealthCheckResults(results) {
        // TODO: Implement health check results display
        console.log('Health check results:', results);
        
        // Show notification with summary
        const totalIssues = results.issues?.length || 0;
        if (totalIssues > 0) {
            showNotification(`Health check completed with ${totalIssues} issues detected`, 'warning');
        } else {
            showNotification('Health check completed successfully with no issues detected', 'success');
        }
    }
    
    // Display connection error
    function displayConnectionError() {
        // Update system alerts
        if (elements.containers.systemAlerts) {
            elements.containers.systemAlerts.innerHTML = `
                <div class="tekton-dashboard__alert tekton-dashboard__alert--error">
                    <div class="tekton-dashboard__alert-icon">⚠️</div>
                    <div class="tekton-dashboard__alert-content">
                        <div class="tekton-dashboard__alert-title">Connection Error</div>
                        <div class="tekton-dashboard__alert-message">
                            Failed to connect to the Tekton API. Please check that all services are running.
                            <button id="retry-connection" class="tekton-dashboard__button tekton-dashboard__button--primary" style="margin-top: 10px;">Retry Connection</button>
                        </div>
                    </div>
                </div>
            `;
            
            // Add event listener to retry button
            const retryButton = component.$('#retry-connection');
            if (retryButton) {
                retryButton.addEventListener('click', () => {
                    if (tektonService) {
                        tektonService.connect();
                    }
                });
            }
        }
        
        // Display error message in component grid
        if (elements.containers.componentGrid) {
            elements.containers.componentGrid.innerHTML = '<div class="tekton-dashboard__placeholder-message">Unable to load components: Connection error</div>';
        }
        
        // Display error message in components grid
        if (elements.containers.componentsGrid) {
            elements.containers.componentsGrid.innerHTML = '<div class="tekton-dashboard__placeholder-message">Unable to load components: Connection error</div>';
        }
    }
    
    // Show a notification
    function showNotification(message, type = 'info') {
        if (!elements.containers.notifications) return;
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `tekton-dashboard__notification tekton-dashboard__notification--${type}`;
        
        // Add icon based on type
        let icon = '💬';
        switch (type) {
            case 'success':
                icon = '✅';
                break;
            case 'error':
                icon = '❌';
                break;
            case 'warning':
                icon = '⚠️';
                break;
            case 'info':
                icon = 'ℹ️';
                break;
        }
        
        // Set notification content
        notification.innerHTML = `
            <div class="tekton-dashboard__notification-icon">${icon}</div>
            <div class="tekton-dashboard__notification-message">${message}</div>
            <button class="tekton-dashboard__notification-close">&times;</button>
        `;
        
        // Add to notifications container
        elements.containers.notifications.appendChild(notification);
        
        // Add event listener to close button
        const closeButton = notification.querySelector('.tekton-dashboard__notification-close');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                notification.remove();
            });
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('tekton-dashboard__notification--fade-out');
            
            // Remove after fade animation
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 5000);
    }
    
    // Expose UI functions to component scope
    Object.assign(component, {
        loadComponents,
        updateComponentsDisplay,
        updateComponentsGridView,
        updateComponentsListView,
        updateComponentStatusGrid,
        filterComponentsList,
        handleComponentButtonAction,
        loadLogs,
        updateLogsDisplay,
        addLogEntryToDisplay,
        formatLogEntry,
        updateLogComponentFilter,
        loadProjects,
        updateProjectsDisplay,
        filterProjectsList,
        handleProjectButtonAction,
        loadResourceMetrics,
        updateViewMode,
        updateSystemStatus,
        updateMetricsDisplay,
        displayComponentDetails,
        displayProjectDetails,
        displayHealthCheckResults,
        displayConnectionError,
        showNotification
    });
    
})(component);