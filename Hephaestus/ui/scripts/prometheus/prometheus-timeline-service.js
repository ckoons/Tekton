/**
 * Prometheus Timeline Service
 * 
 * Provides timeline visualization for project planning and management.
 * This service handles rendering and interaction with the timeline view.
 */

class TimelineVisualization {
    constructor() {
        this.debugPrefix = '[PROMETHEUS TIMELINE]';
        console.log(`${this.debugPrefix} Service constructed`);
        
        // Initialize properties
        this.container = null;
        this.timelineData = null;
        this.options = {
            view: 'month', // day, week, month, quarter
            filter: 'all', // all, active, critical
            projectId: null
        };
        
        // Auto-initialized when PrometheusService available
        this.service = window.PrometheusService ? new window.PrometheusService() : null;
        
        if (!this.service) {
            console.warn(`${this.debugPrefix} PrometheusService not available - using demo data`);
        }
    }

    /**
     * Initialize the timeline visualization
     */
    init(container) {
        console.log(`${this.debugPrefix} Initializing timeline visualization`);
        
        if (!container) {
            console.error(`${this.debugPrefix} No container provided for timeline visualization`);
            return;
        }
        
        this.container = container;
        
        // Set initial state
        this.renderPlaceholder();
        
        // Add event listeners
        this.setupEventListeners();
        
        // Load demo data if service not available
        if (!this.service) {
            this.loadDemoData();
        }
    }

    /**
     * Set up event listeners for timeline interaction
     */
    setupEventListeners() {
        // Add document event listener for timeline updates
        document.addEventListener('prometheus-update', (event) => {
            const update = event.detail;
            
            // Check if this is a timeline update
            if (update.type === 'timeline') {
                console.log(`${this.debugPrefix} Received timeline update:`, update);
                this.timelineData = update.data;
                this.renderTimeline();
            }
        });
    }

    /**
     * Set timeline view (day, week, month, quarter)
     */
    setView(view) {
        if (!['day', 'week', 'month', 'quarter'].includes(view)) {
            console.error(`${this.debugPrefix} Invalid view: ${view}`);
            return;
        }
        
        console.log(`${this.debugPrefix} Setting timeline view to: ${view}`);
        this.options.view = view;
        
        // Re-render timeline with new view
        this.refreshTimeline();
    }

    /**
     * Set timeline filter
     */
    setFilter(filter) {
        if (!['all', 'active', 'critical'].includes(filter)) {
            console.error(`${this.debugPrefix} Invalid filter: ${filter}`);
            return;
        }
        
        console.log(`${this.debugPrefix} Setting timeline filter to: ${filter}`);
        this.options.filter = filter;
        
        // Re-render timeline with new filter
        this.refreshTimeline();
    }

    /**
     * Set project for timeline
     */
    setProject(projectId) {
        console.log(`${this.debugPrefix} Setting timeline project to: ${projectId}`);
        this.options.projectId = projectId;
        
        // Re-render timeline with new project
        this.refreshTimeline();
    }

    /**
     * Refresh the timeline data and view
     */
    async refreshTimeline() {
        console.log(`${this.debugPrefix} Refreshing timeline`);
        
        try {
            // Show loading state
            this.renderLoading();
            
            // If service available, fetch timeline data
            if (this.service && this.options.projectId) {
                try {
                    const apiOptions = {
                        view: this.options.view,
                        filter: this.options.filter
                    };
                    
                    const response = await this.service.generateTimeline(this.options.projectId, apiOptions);
                    this.timelineData = response.timeline || response;
                    console.log(`${this.debugPrefix} Loaded timeline data:`, this.timelineData);
                } catch (error) {
                    console.error(`${this.debugPrefix} Error loading timeline data:`, error);
                    this.showError(error.message || 'Failed to load timeline data');
                    return;
                }
            } else if (!this.timelineData) {
                // Use demo data if no timeline data yet
                this.loadDemoData();
            }
            
            // Render timeline
            this.renderTimeline();
        } catch (error) {
            console.error(`${this.debugPrefix} Error refreshing timeline:`, error);
            this.showError(error.message || 'Failed to refresh timeline');
        }
    }

    /**
     * Load demo timeline data
     */
    loadDemoData() {
        console.log(`${this.debugPrefix} Loading demo timeline data`);
        
        // Generate demo data based on current view
        const now = new Date();
        const items = [];
        
        // Generate demo timeline items
        for (let i = 0; i < 10; i++) {
            const startDate = new Date(now);
            startDate.setDate(startDate.getDate() + (i * 3));
            
            const endDate = new Date(startDate);
            endDate.setDate(endDate.getDate() + Math.floor(Math.random() * 10) + 2);
            
            const isCritical = i < 3; // First 3 items are on critical path
            
            items.push({
                id: `task-${i}`,
                name: `Task ${i + 1}`,
                start_date: startDate.toISOString(),
                end_date: endDate.toISOString(),
                progress: Math.floor(Math.random() * 100),
                critical: isCritical,
                dependencies: i > 0 ? [`task-${i-1}`] : [],
                description: `This is a demo task for the timeline visualization. ${isCritical ? 'This task is on the critical path.' : ''}`,
                assignee: `User ${i % 3 + 1}`
            });
        }
        
        this.timelineData = {
            start_date: now.toISOString(),
            end_date: (() => {
                const date = new Date(now);
                date.setDate(date.getDate() + 30);
                return date.toISOString();
            })(),
            items
        };
    }

    /**
     * Render timeline loading state
     */
    renderLoading() {
        if (!this.container) return;
        
        this.container.innerHTML = `
            <div class="prometheus__loading-indicator">
                <div class="prometheus__spinner"></div>
                <div class="prometheus__loading-text">Loading timeline...</div>
            </div>
        `;
    }

    /**
     * Render placeholder when no timeline data is available
     */
    renderPlaceholder() {
        if (!this.container) return;
        
        this.container.innerHTML = `
            <div class="prometheus__timeline-placeholder">
                <div class="prometheus__placeholder-content">
                    <h3 class="prometheus__placeholder-title">Timeline Visualization</h3>
                    <p class="prometheus__placeholder-text">Select a project to visualize its timeline.</p>
                </div>
            </div>
        `;
    }

    /**
     * Render error message
     */
    showError(errorMessage) {
        if (!this.container) return;
        
        this.container.innerHTML = `
            <div class="prometheus__error">
                <h3>Timeline Error</h3>
                <p>${errorMessage}</p>
            </div>
        `;
    }

    /**
     * Render the timeline visualization
     */
    renderTimeline() {
        console.log(`${this.debugPrefix} Rendering timeline`);
        
        if (!this.container) {
            console.error(`${this.debugPrefix} No container for timeline rendering`);
            return;
        }
        
        if (!this.timelineData || !this.timelineData.items || this.timelineData.items.length === 0) {
            this.renderPlaceholder();
            return;
        }
        
        try {
            // Generate timeline visualization HTML based on view mode
            let timelineHtml = '';
            
            switch (this.options.view) {
                case 'day':
                    timelineHtml = this.renderDayView();
                    break;
                case 'week':
                    timelineHtml = this.renderWeekView();
                    break;
                case 'quarter':
                    timelineHtml = this.renderQuarterView();
                    break;
                case 'month':
                default:
                    timelineHtml = this.renderMonthView();
                    break;
            }
            
            // Update container with timeline HTML
            this.container.innerHTML = `
                <div class="prometheus__timeline-visualization">
                    <div class="prometheus__timeline-legend">
                        <div class="prometheus__legend-item">
                            <div class="prometheus__legend-dot prometheus__legend-dot--critical"></div>
                            <span>Critical Path Task</span>
                        </div>
                        <div class="prometheus__legend-item">
                            <div class="prometheus__legend-dot prometheus__legend-dot--normal"></div>
                            <span>Regular Task</span>
                        </div>
                        <div class="prometheus__legend-item">
                            <div class="prometheus__legend-dot prometheus__legend-dot--completed"></div>
                            <span>Completed Task</span>
                        </div>
                    </div>
                    
                    <div class="prometheus__timeline-content">
                        ${timelineHtml}
                    </div>
                </div>
            `;
            
            // Add event listeners for timeline items
            this.addTimelineItemEventListeners();
        } catch (error) {
            console.error(`${this.debugPrefix} Error rendering timeline:`, error);
            this.showError('Failed to render timeline visualization');
        }
    }

    /**
     * Render a daily view of the timeline
     */
    renderDayView() {
        // Get start and end dates from timeline data
        const startDate = new Date(this.timelineData.start_date || new Date());
        const endDate = new Date(this.timelineData.end_date || (() => {
            const date = new Date(startDate);
            date.setDate(date.getDate() + 14); // two weeks by default
            return date;
        })());
        
        // Generate days between start and end dates
        const days = [];
        const currentDate = new Date(startDate);
        
        while (currentDate <= endDate) {
            days.push(new Date(currentDate));
            currentDate.setDate(currentDate.getDate() + 1);
        }
        
        // Generate HTML for day headers
        const dayHeaders = days.map(day => `
            <div class="prometheus__timeline-header-cell prometheus__day-cell">
                <div class="prometheus__day-name">${day.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                <div class="prometheus__date">${day.getDate()}</div>
            </div>
        `).join('');
        
        // Generate HTML for task rows
        const taskRows = this.timelineData.items.map(task => {
            const taskStart = new Date(task.start_date);
            const taskEnd = new Date(task.end_date);
            
            // Filter out task if it doesn't match current filter
            if (this.options.filter === 'critical' && !task.critical) {
                return '';
            }
            
            // Generate task cells for each day
            const taskCells = days.map(day => {
                const isInRange = day >= taskStart && day <= taskEnd;
                const isStart = day.toDateString() === taskStart.toDateString();
                const isEnd = day.toDateString() === taskEnd.toDateString();
                
                if (isInRange) {
                    const cellClasses = [
                        'prometheus__timeline-task-cell',
                        'prometheus__timeline-task-cell--active',
                        task.critical ? 'prometheus__timeline-task-cell--critical' : '',
                        task.progress >= 100 ? 'prometheus__timeline-task-cell--completed' : '',
                        isStart ? 'prometheus__timeline-task-cell--start' : '',
                        isEnd ? 'prometheus__timeline-task-cell--end' : ''
                    ].filter(Boolean).join(' ');
                    
                    return `<div class="${cellClasses}" data-task-id="${task.id}"></div>`;
                } else {
                    return '<div class="prometheus__timeline-task-cell"></div>';
                }
            }).join('');
            
            return `
                <div class="prometheus__timeline-row" data-task-id="${task.id}">
                    <div class="prometheus__timeline-task-label">
                        <div class="prometheus__task-name">${task.name}</div>
                        <div class="prometheus__task-progress">${task.progress || 0}%</div>
                    </div>
                    <div class="prometheus__timeline-task-cells">
                        ${taskCells}
                    </div>
                </div>
            `;
        }).filter(Boolean).join('');
        
        // Combine headers and rows into complete timeline HTML
        return `
            <div class="prometheus__timeline-view prometheus__day-view">
                <div class="prometheus__timeline-header">
                    <div class="prometheus__timeline-label-header">Task</div>
                    <div class="prometheus__timeline-header-cells">
                        ${dayHeaders}
                    </div>
                </div>
                
                <div class="prometheus__timeline-body">
                    ${taskRows}
                </div>
            </div>
        `;
    }

    /**
     * Render a weekly view of the timeline
     */
    renderWeekView() {
        // Similar to day view but with weeks as columns
        // Simplified for demonstration purposes
        return `
            <div class="prometheus__timeline-view prometheus__week-view">
                <div class="prometheus__timeline-header">
                    <div class="prometheus__timeline-label-header">Task</div>
                    <div class="prometheus__timeline-header-cells">
                        <div class="prometheus__timeline-header-cell">Week 1</div>
                        <div class="prometheus__timeline-header-cell">Week 2</div>
                        <div class="prometheus__timeline-header-cell">Week 3</div>
                        <div class="prometheus__timeline-header-cell">Week 4</div>
                    </div>
                </div>
                
                <div class="prometheus__timeline-body">
                    ${this.timelineData.items.map(task => {
                        // Filter out task if it doesn't match current filter
                        if (this.options.filter === 'critical' && !task.critical) {
                            return '';
                        }
                        
                        return `
                            <div class="prometheus__timeline-row" data-task-id="${task.id}">
                                <div class="prometheus__timeline-task-label">
                                    <div class="prometheus__task-name">${task.name}</div>
                                    <div class="prometheus__task-progress">${task.progress || 0}%</div>
                                </div>
                                <div class="prometheus__timeline-task-cells">
                                    <div class="prometheus__timeline-task-cell"></div>
                                    <div class="prometheus__timeline-task-cell prometheus__timeline-task-cell--active ${task.critical ? 'prometheus__timeline-task-cell--critical' : ''}" data-task-id="${task.id}"></div>
                                    <div class="prometheus__timeline-task-cell prometheus__timeline-task-cell--active ${task.critical ? 'prometheus__timeline-task-cell--critical' : ''}" data-task-id="${task.id}"></div>
                                    <div class="prometheus__timeline-task-cell"></div>
                                </div>
                            </div>
                        `;
                    }).filter(Boolean).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Render a monthly view of the timeline
     */
    renderMonthView() {
        // Generate month view
        return `
            <div class="prometheus__timeline-view prometheus__month-view">
                <div class="prometheus__timeline-header">
                    <div class="prometheus__timeline-label-header">Task</div>
                    <div class="prometheus__timeline-header-cells">
                        <div class="prometheus__timeline-header-cell">May</div>
                        <div class="prometheus__timeline-header-cell">June</div>
                        <div class="prometheus__timeline-header-cell">July</div>
                        <div class="prometheus__timeline-header-cell">August</div>
                    </div>
                </div>
                
                <div class="prometheus__timeline-body">
                    ${this.timelineData.items.map(task => {
                        // Filter out task if it doesn't match current filter
                        if (this.options.filter === 'critical' && !task.critical) {
                            return '';
                        }
                        
                        return `
                            <div class="prometheus__timeline-row" data-task-id="${task.id}">
                                <div class="prometheus__timeline-task-label">
                                    <div class="prometheus__task-name">${task.name}</div>
                                    <div class="prometheus__task-progress">${task.progress || 0}%</div>
                                </div>
                                <div class="prometheus__timeline-task-cells">
                                    <div class="prometheus__timeline-task-cell prometheus__timeline-task-cell--active ${task.critical ? 'prometheus__timeline-task-cell--critical' : ''}" data-task-id="${task.id}"></div>
                                    <div class="prometheus__timeline-task-cell prometheus__timeline-task-cell--active ${task.critical ? 'prometheus__timeline-task-cell--critical' : ''}" data-task-id="${task.id}"></div>
                                    <div class="prometheus__timeline-task-cell"></div>
                                    <div class="prometheus__timeline-task-cell"></div>
                                </div>
                            </div>
                        `;
                    }).filter(Boolean).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Render a quarterly view of the timeline
     */
    renderQuarterView() {
        // Generate quarter view
        return `
            <div class="prometheus__timeline-view prometheus__quarter-view">
                <div class="prometheus__timeline-header">
                    <div class="prometheus__timeline-label-header">Task</div>
                    <div class="prometheus__timeline-header-cells">
                        <div class="prometheus__timeline-header-cell">Q2 2025</div>
                        <div class="prometheus__timeline-header-cell">Q3 2025</div>
                        <div class="prometheus__timeline-header-cell">Q4 2025</div>
                        <div class="prometheus__timeline-header-cell">Q1 2026</div>
                    </div>
                </div>
                
                <div class="prometheus__timeline-body">
                    ${this.timelineData.items.map(task => {
                        // Filter out task if it doesn't match current filter
                        if (this.options.filter === 'critical' && !task.critical) {
                            return '';
                        }
                        
                        return `
                            <div class="prometheus__timeline-row" data-task-id="${task.id}">
                                <div class="prometheus__timeline-task-label">
                                    <div class="prometheus__task-name">${task.name}</div>
                                    <div class="prometheus__task-progress">${task.progress || 0}%</div>
                                </div>
                                <div class="prometheus__timeline-task-cells">
                                    <div class="prometheus__timeline-task-cell prometheus__timeline-task-cell--active ${task.critical ? 'prometheus__timeline-task-cell--critical' : ''}" data-task-id="${task.id}"></div>
                                    <div class="prometheus__timeline-task-cell prometheus__timeline-task-cell--active ${task.critical ? 'prometheus__timeline-task-cell--critical' : ''}" data-task-id="${task.id}"></div>
                                    <div class="prometheus__timeline-task-cell"></div>
                                    <div class="prometheus__timeline-task-cell"></div>
                                </div>
                            </div>
                        `;
                    }).filter(Boolean).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Add event listeners to timeline items
     */
    addTimelineItemEventListeners() {
        if (!this.container) return;
        
        // Find all task cells and add click listeners
        const taskCells = this.container.querySelectorAll('.prometheus__timeline-task-cell--active');
        
        taskCells.forEach(cell => {
            const taskId = cell.getAttribute('data-task-id');
            if (!taskId) return;
            
            cell.addEventListener('click', () => this.handleTaskClick(taskId));
        });
        
        // Find all task rows and add click listeners to labels
        const taskLabels = this.container.querySelectorAll('.prometheus__timeline-task-label');
        
        taskLabels.forEach(label => {
            const row = label.closest('.prometheus__timeline-row');
            if (!row) return;
            
            const taskId = row.getAttribute('data-task-id');
            if (!taskId) return;
            
            label.addEventListener('click', () => this.handleTaskClick(taskId));
        });
    }

    /**
     * Handle click on a timeline task
     */
    handleTaskClick(taskId) {
        console.log(`${this.debugPrefix} Task clicked: ${taskId}`);
        
        // Find task data
        const task = this.timelineData.items.find(item => item.id === taskId);
        
        if (!task) {
            console.error(`${this.debugPrefix} Task not found: ${taskId}`);
            return;
        }
        
        // Show task details popup
        this.showTaskDetailsPopup(task);
    }

    /**
     * Show task details popup
     */
    showTaskDetailsPopup(task) {
        // Create popup element
        const popup = document.createElement('div');
        popup.className = 'prometheus__task-popup';
        
        // Format dates
        const startDate = new Date(task.start_date).toLocaleDateString();
        const endDate = new Date(task.end_date).toLocaleDateString();
        
        // Create popup content
        popup.innerHTML = `
            <div class="prometheus__task-popup-header">
                <h3 class="prometheus__task-popup-title">${task.name}</h3>
                <button class="prometheus__task-popup-close">×</button>
            </div>
            <div class="prometheus__task-popup-content">
                <div class="prometheus__task-popup-progress">
                    <div class="prometheus__progress-bar">
                        <div class="prometheus__progress-fill" style="width: ${task.progress || 0}%;"></div>
                    </div>
                    <div class="prometheus__progress-text">${task.progress || 0}% Complete</div>
                </div>
                
                <div class="prometheus__task-popup-details">
                    <div class="prometheus__task-popup-dates">
                        <div class="prometheus__task-popup-date">
                            <span class="prometheus__task-popup-label">Start:</span>
                            <span class="prometheus__task-popup-value">${startDate}</span>
                        </div>
                        <div class="prometheus__task-popup-date">
                            <span class="prometheus__task-popup-label">End:</span>
                            <span class="prometheus__task-popup-value">${endDate}</span>
                        </div>
                    </div>
                    
                    <div class="prometheus__task-popup-assignee">
                        <span class="prometheus__task-popup-label">Assignee:</span>
                        <span class="prometheus__task-popup-value">${task.assignee || 'Unassigned'}</span>
                    </div>
                    
                    ${task.critical ? '<div class="prometheus__task-popup-critical">Critical Path Task</div>' : ''}
                    
                    <div class="prometheus__task-popup-description">
                        <span class="prometheus__task-popup-label">Description:</span>
                        <div class="prometheus__task-popup-value">${task.description || 'No description available'}</div>
                    </div>
                    
                    ${task.dependencies && task.dependencies.length > 0 ? `
                        <div class="prometheus__task-popup-dependencies">
                            <span class="prometheus__task-popup-label">Dependencies:</span>
                            <div class="prometheus__task-popup-value">
                                ${task.dependencies.map(depId => {
                                    const dep = this.timelineData.items.find(item => item.id === depId);
                                    return dep ? `<div class="prometheus__task-dependency">${dep.name}</div>` : '';
                                }).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
                
                <div class="prometheus__task-popup-actions">
                    <button class="prometheus__task-popup-action prometheus__task-popup-action--edit">Edit</button>
                    <button class="prometheus__task-popup-action prometheus__task-popup-action--view">View Details</button>
                </div>
            </div>
        `;
        
        // Add to DOM
        document.body.appendChild(popup);
        
        // Position the popup
        this.positionPopup(popup);
        
        // Add event listeners
        const closeButton = popup.querySelector('.prometheus__task-popup-close');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                popup.remove();
            });
        }
        
        // Close on click outside
        document.addEventListener('click', (event) => {
            if (!popup.contains(event.target) && popup.parentNode) {
                popup.remove();
            }
        });
        
        // Prevent clicks inside popup from closing it
        popup.addEventListener('click', (event) => {
            event.stopPropagation();
        });
        
        // Handle edit button
        const editButton = popup.querySelector('.prometheus__task-popup-action--edit');
        if (editButton) {
            editButton.addEventListener('click', () => {
                popup.remove();
                this.handleEditTask(task.id);
            });
        }
        
        // Handle view button
        const viewButton = popup.querySelector('.prometheus__task-popup-action--view');
        if (viewButton) {
            viewButton.addEventListener('click', () => {
                popup.remove();
                this.handleViewTask(task.id);
            });
        }
    }

    /**
     * Position popup relative to clicked element
     */
    positionPopup(popup) {
        // Position in center for simplicity
        popup.style.position = 'fixed';
        popup.style.top = '50%';
        popup.style.left = '50%';
        popup.style.transform = 'translate(-50%, -50%)';
        popup.style.maxWidth = '90%';
        popup.style.maxHeight = '90%';
        popup.style.zIndex = '1000';
        popup.style.backgroundColor = 'var(--bg-secondary, #252535)';
        popup.style.borderRadius = '8px';
        popup.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
        popup.style.overflow = 'auto';
    }

    /**
     * Handle edit task action
     */
    handleEditTask(taskId) {
        console.log(`${this.debugPrefix} Edit task: ${taskId}`);
        alert(`Edit task functionality would be implemented here for task ${taskId}`);
    }

    /**
     * Handle view task action
     */
    handleViewTask(taskId) {
        console.log(`${this.debugPrefix} View task: ${taskId}`);
        alert(`View task functionality would be implemented here for task ${taskId}`);
    }
}

// Make available globally
window.TimelineVisualization = TimelineVisualization;