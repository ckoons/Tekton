/**
 * Prometheus/Epimethius Planning System UI Component
 * 
 * This module provides the UI integration for the Prometheus/Epimethius 
 * Planning System, following the Tekton Single Port Architecture.
 */

class PrometheusUI {
    constructor(options = {}) {
        this.apiBaseUrl = options.apiBaseUrl || 'http://localhost:8006/api';
        this.container = options.container || document.getElementById('prometheus-container');
        this.token = options.token || null;
        this.plans = [];
        this.currentPlan = null;
        this.currentTab = 'plans';
        this.client = new PrometheusClient(this.apiBaseUrl);
        
        // Initialize the UI
        this.initialize();
    }
    
    async initialize() {
        if (!this.container) {
            console.error('Prometheus UI container not found');
            return;
        }
        
        try {
            // Check health
            const health = await this.client.health();
            if (health.status !== 'healthy') {
                this.showError('Prometheus service is not healthy');
                return;
            }
            
            // Load initial UI
            this.renderUI();
            
            // Load plans
            await this.loadPlans();
        } catch (error) {
            this.showError('Failed to initialize Prometheus UI', error);
        }
    }
    
    async loadPlans() {
        try {
            const plansResponse = await this.client.listPlans();
            this.plans = plansResponse.plans || [];
            this.renderPlans();
        } catch (error) {
            this.showError('Failed to load plans', error);
        }
    }
    
    renderUI() {
        this.container.innerHTML = `
            <div class="prometheus-container">
                <div class="prometheus-header">
                    <div>
                        <h2 class="prometheus-title">Prometheus</h2>
                        <p class="prometheus-subtitle">Planning and Retrospective System</p>
                    </div>
                    <div>
                        <button id="prometheus-new-plan" class="prometheus-btn prometheus-btn-primary">
                            <i class="fas fa-plus"></i> New Plan
                        </button>
                    </div>
                </div>
                
                <div class="prometheus-tabs">
                    <div class="prometheus-tab active" data-tab="plans">Plans</div>
                    <div class="prometheus-tab" data-tab="tasks">Tasks</div>
                    <div class="prometheus-tab" data-tab="timeline">Timeline</div>
                    <div class="prometheus-tab" data-tab="retrospectives">Retrospectives</div>
                    <div class="prometheus-tab" data-tab="metrics">Metrics</div>
                </div>
                
                <div id="prometheus-content" class="prometheus-content">
                    <!-- Tab content will be rendered here -->
                    <div id="prometheus-plans" class="prometheus-plans">
                        <div class="prometheus-loading">Loading plans...</div>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners
        document.getElementById('prometheus-new-plan').addEventListener('click', () => this.showNewPlanModal());
        
        const tabs = document.querySelectorAll('.prometheus-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }
    
    renderPlans() {
        const plansContainer = document.getElementById('prometheus-plans');
        
        if (!this.plans.length) {
            plansContainer.innerHTML = `
                <div class="prometheus-empty-state">
                    <p>No plans found</p>
                    <button class="prometheus-btn prometheus-btn-primary" id="prometheus-create-first-plan">
                        Create your first plan
                    </button>
                </div>
            `;
            
            document.getElementById('prometheus-create-first-plan').addEventListener('click', () => this.showNewPlanModal());
            return;
        }
        
        // Generate plan cards
        const planCards = this.plans.map(plan => this.createPlanCard(plan)).join('');
        plansContainer.innerHTML = planCards;
        
        // Add event listeners to cards
        this.plans.forEach(plan => {
            document.getElementById(`plan-${plan.id}`).addEventListener('click', () => this.selectPlan(plan.id));
        });
    }
    
    createPlanCard(plan) {
        const progress = plan.progress || 0;
        const startDate = new Date(plan.start_date).toLocaleDateString();
        const endDate = new Date(plan.end_date).toLocaleDateString();
        
        return `
            <div class="prometheus-plan-card" id="plan-${plan.id}">
                <h3 class="prometheus-plan-title">${plan.name}</h3>
                <div class="prometheus-plan-meta">
                    <span>${startDate} - ${endDate}</span>
                    <span>${plan.tasks?.length || 0} tasks</span>
                </div>
                <p class="prometheus-plan-description">${plan.description}</p>
                <div class="prometheus-plan-progress">
                    <div class="prometheus-plan-progress-bar" style="width: ${progress}%"></div>
                </div>
                <div class="prometheus-plan-footer">
                    <span>${progress}% complete</span>
                    <div>
                        ${plan.tags?.map(tag => `<span class="prometheus-tag">${tag}</span>`).join('') || ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    async selectPlan(planId) {
        try {
            const plan = await this.client.getPlan(planId);
            this.currentPlan = plan;
            this.switchTab('tasks');
        } catch (error) {
            this.showError('Failed to load plan details', error);
        }
    }
    
    async switchTab(tabName) {
        if (tabName === this.currentTab) return;
        
        // Update active tab
        document.querySelectorAll('.prometheus-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        
        this.currentTab = tabName;
        const contentContainer = document.getElementById('prometheus-content');
        
        // Show loading state
        contentContainer.innerHTML = '<div class="prometheus-loading">Loading...</div>';
        
        try {
            switch (tabName) {
                case 'plans':
                    contentContainer.innerHTML = '<div id="prometheus-plans" class="prometheus-plans"></div>';
                    this.renderPlans();
                    break;
                    
                case 'tasks':
                    if (!this.currentPlan) {
                        contentContainer.innerHTML = '<div class="prometheus-info">Please select a plan first</div>';
                        this.switchTab('plans');
                        return;
                    }
                    await this.loadTasks();
                    break;
                    
                case 'timeline':
                    if (!this.currentPlan) {
                        contentContainer.innerHTML = '<div class="prometheus-info">Please select a plan first</div>';
                        this.switchTab('plans');
                        return;
                    }
                    await this.loadTimeline();
                    break;
                    
                case 'retrospectives':
                    if (!this.currentPlan) {
                        contentContainer.innerHTML = '<div class="prometheus-info">Please select a plan first</div>';
                        this.switchTab('plans');
                        return;
                    }
                    await this.loadRetrospectives();
                    break;
                    
                case 'metrics':
                    if (!this.currentPlan) {
                        contentContainer.innerHTML = '<div class="prometheus-info">Please select a plan first</div>';
                        this.switchTab('plans');
                        return;
                    }
                    await this.loadMetrics();
                    break;
            }
        } catch (error) {
            this.showError(`Failed to load ${tabName}`, error);
        }
    }
    
    async loadTasks() {
        if (!this.currentPlan) return;
        
        try {
            const tasksResponse = await this.client.listTasks(this.currentPlan.id);
            const tasks = tasksResponse.tasks || [];
            
            const contentContainer = document.getElementById('prometheus-content');
            
            // Get critical path
            let criticalPath = [];
            try {
                const cpResponse = await this.client.calculateCriticalPath(this.currentPlan.id);
                criticalPath = cpResponse.critical_path || [];
            } catch (e) {
                console.warn('Failed to load critical path', e);
            }
            
            contentContainer.innerHTML = `
                <div class="prometheus-flex-between prometheus-mb-2">
                    <h3>${this.currentPlan.name} - Tasks</h3>
                    <button id="prometheus-new-task" class="prometheus-btn prometheus-btn-outline">
                        <i class="fas fa-plus"></i> Add Task
                    </button>
                </div>
                
                <div class="prometheus-tasks">
                    ${tasks.length === 0 ? '<div class="prometheus-info">No tasks found</div>' : ''}
                    ${tasks.map(task => this.createTaskItem(task, criticalPath.includes(task.id))).join('')}
                </div>
            `;
            
            // Add event listener for new task button
            document.getElementById('prometheus-new-task')?.addEventListener('click', () => this.showNewTaskModal());
            
            // Add event listeners for task actions
            tasks.forEach(task => {
                document.getElementById(`task-edit-${task.id}`)?.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.showEditTaskModal(task);
                });
                
                document.getElementById(`task-delete-${task.id}`)?.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.showDeleteTaskConfirmation(task);
                });
                
                document.getElementById(`task-progress-${task.id}`)?.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.showTaskProgressModal(task);
                });
            });
        } catch (error) {
            this.showError('Failed to load tasks', error);
        }
    }
    
    createTaskItem(task, isCritical) {
        const statusClasses = {
            'pending': 'pending',
            'in_progress': 'in-progress',
            'completed': 'completed',
            'blocked': 'blocked'
        };
        
        const statusClass = statusClasses[task.status] || 'pending';
        const criticalClass = isCritical ? 'prometheus-task-critical' : '';
        
        return `
            <div class="prometheus-task-item ${criticalClass}" id="task-${task.id}">
                <div class="prometheus-task-status ${statusClass}"></div>
                <div class="prometheus-task-content">
                    <div class="prometheus-task-title">
                        ${task.name}
                        ${isCritical ? '<span class="prometheus-badge" style="background-color: var(--prometheus-danger); color: white;">Critical</span>' : ''}
                    </div>
                    <div class="prometheus-task-description">${task.description}</div>
                    <div class="prometheus-task-meta">
                        <span>Duration: ${task.duration} ${task.duration_unit}</span>
                        ${task.assigned_to ? `<span>Assigned: ${task.assigned_to_name || task.assigned_to}</span>` : ''}
                        <span>Priority: ${task.priority}</span>
                    </div>
                </div>
                <div class="prometheus-task-actions">
                    <button id="task-progress-${task.id}" class="prometheus-btn prometheus-btn-outline" title="Update Progress">
                        <i class="fas fa-chart-line"></i>
                    </button>
                    <button id="task-edit-${task.id}" class="prometheus-btn prometheus-btn-outline" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button id="task-delete-${task.id}" class="prometheus-btn prometheus-btn-outline" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    async loadTimeline() {
        if (!this.currentPlan) return;
        
        try {
            const timelineResponse = await this.client.generateTimeline(this.currentPlan.id);
            const timeline = timelineResponse.timeline || { items: [] };
            
            // Get critical path
            let criticalPath = [];
            try {
                const cpResponse = await this.client.calculateCriticalPath(this.currentPlan.id);
                criticalPath = cpResponse.critical_path || [];
            } catch (e) {
                console.warn('Failed to load critical path', e);
            }
            
            const contentContainer = document.getElementById('prometheus-content');
            contentContainer.innerHTML = `
                <div class="prometheus-flex-between prometheus-mb-2">
                    <h3>${this.currentPlan.name} - Timeline</h3>
                    <div>
                        <button id="prometheus-export-timeline" class="prometheus-btn prometheus-btn-outline">
                            <i class="fas fa-download"></i> Export
                        </button>
                    </div>
                </div>
                
                <div class="prometheus-critical-path">
                    <h4>Critical Path</h4>
                    <div class="prometheus-critical-path-legend">
                        <div class="prometheus-legend-item">
                            <div class="prometheus-legend-dot critical"></div>
                            <span>Critical Path Task</span>
                        </div>
                        <div class="prometheus-legend-item">
                            <div class="prometheus-legend-dot normal"></div>
                            <span>Regular Task</span>
                        </div>
                    </div>
                    ${this.renderCriticalPath(criticalPath)}
                </div>
                
                <div class="prometheus-timeline">
                    <div class="prometheus-timeline-line"></div>
                    ${timeline.items.map(item => this.createTimelineItem(item, criticalPath)).join('')}
                </div>
            `;
            
            // Add event listener for export button
            document.getElementById('prometheus-export-timeline')?.addEventListener('click', () => this.exportTimeline());
        } catch (error) {
            this.showError('Failed to load timeline', error);
        }
    }
    
    renderCriticalPath(criticalPath) {
        if (!criticalPath || criticalPath.length === 0) {
            return '<div class="prometheus-info">No critical path available</div>';
        }
        
        // This would ideally be a visual representation of the critical path
        // For now, just list the tasks
        return `
            <div class="prometheus-critical-path-tasks">
                ${criticalPath.map((taskId, index) => `
                    <div class="prometheus-critical-path-task">
                        <span>${index + 1}.</span>
                        <span>${this.getTaskName(taskId)}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    getTaskName(taskId) {
        if (!this.currentPlan || !this.currentPlan.tasks) return `Task ${taskId}`;
        const task = this.currentPlan.tasks.find(t => t.id === taskId);
        return task ? task.name : `Task ${taskId}`;
    }
    
    createTimelineItem(item, criticalPath) {
        const isCritical = criticalPath.includes(item.task_id);
        const date = new Date(item.date).toLocaleDateString();
        
        return `
            <div class="prometheus-timeline-item">
                <div class="prometheus-timeline-dot ${isCritical ? 'critical' : ''}"></div>
                <div class="prometheus-timeline-date">${date}</div>
                <div class="prometheus-timeline-content">
                    <h4>${item.title}</h4>
                    <p>${item.description}</p>
                </div>
            </div>
        `;
    }
    
    async loadRetrospectives() {
        if (!this.currentPlan) return;
        
        try {
            const retrospectivesResponse = await this.client.listRetrospectives(this.currentPlan.id);
            const retrospectives = retrospectivesResponse.retrospectives || [];
            
            const contentContainer = document.getElementById('prometheus-content');
            contentContainer.innerHTML = `
                <div class="prometheus-flex-between prometheus-mb-2">
                    <h3>${this.currentPlan.name} - Retrospectives</h3>
                    <button id="prometheus-new-retrospective" class="prometheus-btn prometheus-btn-outline">
                        <i class="fas fa-plus"></i> New Retrospective
                    </button>
                </div>
                
                <div class="prometheus-retrospectives">
                    ${retrospectives.length === 0 ? '<div class="prometheus-info">No retrospectives found</div>' : ''}
                    ${retrospectives.map(retro => this.createRetrospectiveCard(retro)).join('')}
                </div>
            `;
            
            // Add event listener for new retrospective button
            document.getElementById('prometheus-new-retrospective')?.addEventListener('click', () => this.showNewRetrospectiveModal());
            
            // Add event listeners for retrospective cards
            retrospectives.forEach(retro => {
                document.getElementById(`retrospective-${retro.id}`)?.addEventListener('click', () => this.selectRetrospective(retro.id));
            });
        } catch (error) {
            this.showError('Failed to load retrospectives', error);
        }
    }
    
    createRetrospectiveCard(retrospective) {
        const date = new Date(retrospective.date).toLocaleDateString();
        
        return `
            <div class="prometheus-plan-card" id="retrospective-${retrospective.id}">
                <h3 class="prometheus-plan-title">${retrospective.name}</h3>
                <div class="prometheus-plan-meta">
                    <span>${date}</span>
                    <span>${retrospective.feedback?.length || 0} items</span>
                </div>
                <p class="prometheus-plan-description">${retrospective.description}</p>
                <div class="prometheus-plan-footer">
                    <span>${retrospective.participants?.length || 0} participants</span>
                    <div>
                        ${retrospective.tags?.map(tag => `<span class="prometheus-tag">${tag}</span>`).join('') || ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    async selectRetrospective(retroId) {
        try {
            const retrospective = await this.client.getRetrospective(retroId);
            this.currentRetrospective = retrospective;
            this.renderRetrospectiveDetails(retrospective);
        } catch (error) {
            this.showError('Failed to load retrospective details', error);
        }
    }
    
    renderRetrospectiveDetails(retrospective) {
        const contentContainer = document.getElementById('prometheus-content');
        const date = new Date(retrospective.date).toLocaleDateString();
        
        contentContainer.innerHTML = `
            <div class="prometheus-flex-between prometheus-mb-2">
                <div>
                    <h3>${retrospective.name}</h3>
                    <div class="prometheus-subtitle">${date}</div>
                </div>
                <div>
                    <button id="prometheus-back-to-retros" class="prometheus-btn prometheus-btn-outline">
                        <i class="fas fa-arrow-left"></i> Back
                    </button>
                    <button id="prometheus-add-feedback" class="prometheus-btn prometheus-btn-outline">
                        <i class="fas fa-plus"></i> Add Feedback
                    </button>
                </div>
            </div>
            
            <p class="prometheus-mb-2">${retrospective.description}</p>
            
            <h4>Feedback</h4>
            <div class="prometheus-feedback-list">
                ${retrospective.feedback?.length === 0 ? '<div class="prometheus-info">No feedback items</div>' : ''}
                ${(retrospective.feedback || []).map(feedback => this.createFeedbackItem(feedback)).join('')}
            </div>
            
            <h4>Improvement Suggestions</h4>
            <div id="prometheus-improvements">
                <button id="prometheus-generate-improvements" class="prometheus-btn prometheus-btn-secondary">
                    <i class="fas fa-lightbulb"></i> Generate Suggestions
                </button>
            </div>
        `;
        
        // Add event listeners
        document.getElementById('prometheus-back-to-retros')?.addEventListener('click', () => {
            this.currentRetrospective = null;
            this.loadRetrospectives();
        });
        
        document.getElementById('prometheus-add-feedback')?.addEventListener('click', () => this.showAddFeedbackModal(retrospective.id));
        document.getElementById('prometheus-generate-improvements')?.addEventListener('click', () => this.generateImprovementSuggestions(retrospective.id));
    }
    
    createFeedbackItem(feedback) {
        return `
            <div class="prometheus-feedback-item ${feedback.type}">
                <div class="prometheus-feedback-source">${feedback.source || 'Anonymous'}</div>
                <div class="prometheus-feedback-content">${feedback.description}</div>
            </div>
        `;
    }
    
    async generateImprovementSuggestions(retroId) {
        try {
            const improvementsButton = document.getElementById('prometheus-generate-improvements');
            improvementsButton.disabled = true;
            improvementsButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            
            const suggestions = await this.client.generateImprovementSuggestions(retroId);
            
            const improvementsContainer = document.getElementById('prometheus-improvements');
            improvementsContainer.innerHTML = `
                <div class="prometheus-improvements-list">
                    ${suggestions.length === 0 ? '<div class="prometheus-info">No suggestions found</div>' : ''}
                    ${suggestions.map(suggestion => this.createSuggestionItem(suggestion)).join('')}
                </div>
            `;
        } catch (error) {
            this.showError('Failed to generate improvement suggestions', error);
            
            const improvementsButton = document.getElementById('prometheus-generate-improvements');
            if (improvementsButton) {
                improvementsButton.disabled = false;
                improvementsButton.innerHTML = '<i class="fas fa-lightbulb"></i> Generate Suggestions';
            }
        }
    }
    
    createSuggestionItem(suggestion) {
        return `
            <div class="prometheus-feedback-item positive">
                <div class="prometheus-feedback-content">
                    <strong>${suggestion.description}</strong>
                    <p>${suggestion.rationale}</p>
                    <div class="prometheus-feedback-source">Expected Impact: ${suggestion.expected_impact}</div>
                </div>
            </div>
        `;
    }
    
    async loadMetrics() {
        if (!this.currentPlan) return;
        
        try {
            // Get performance metrics
            const metricsResponse = await this.client.generatePerformanceMetrics(this.currentPlan.id);
            const metrics = metricsResponse || {};
            
            // Get variance analysis
            const varianceResponse = await this.client.generateVarianceAnalysis(this.currentPlan.id);
            const variance = varianceResponse || {};
            
            const contentContainer = document.getElementById('prometheus-content');
            contentContainer.innerHTML = `
                <div class="prometheus-flex-between prometheus-mb-2">
                    <h3>${this.currentPlan.name} - Metrics</h3>
                    <button id="prometheus-export-metrics" class="prometheus-btn prometheus-btn-outline">
                        <i class="fas fa-download"></i> Export Report
                    </button>
                </div>
                
                <div class="prometheus-metrics-grid">
                    <div class="prometheus-metric-card">
                        <div class="prometheus-metric-title">Completion Rate</div>
                        <div class="prometheus-metric-value">${metrics.on_time_completion_rate || 0}%</div>
                    </div>
                    <div class="prometheus-metric-card">
                        <div class="prometheus-metric-title">Average Delay</div>
                        <div class="prometheus-metric-value">${metrics.average_delay || 0} days</div>
                    </div>
                    <div class="prometheus-metric-card">
                        <div class="prometheus-metric-title">Tasks Completed</div>
                        <div class="prometheus-metric-value">${metrics.completed_tasks || 0}/${metrics.total_tasks || 0}</div>
                    </div>
                    <div class="prometheus-metric-card">
                        <div class="prometheus-metric-title">Resource Utilization</div>
                        <div class="prometheus-metric-value">${metrics.resource_utilization || 0}%</div>
                    </div>
                </div>
                
                <div class="prometheus-chart-container prometheus-mb-2">
                    <div class="prometheus-chart-title">Task Variance Analysis</div>
                    <div id="prometheus-variance-chart" style="height: 300px;"></div>
                </div>
                
                <h4>Variance Summary</h4>
                <p>${variance.summary || 'No variance analysis available'}</p>
                
                <h4>Plan Analysis</h4>
                <button id="prometheus-generate-analysis" class="prometheus-btn prometheus-btn-secondary">
                    <i class="fas fa-brain"></i> Generate LLM Analysis
                </button>
                <div id="prometheus-analysis-results" class="prometheus-mb-2"></div>
            `;
            
            // Add event listeners
            document.getElementById('prometheus-export-metrics')?.addEventListener('click', () => this.exportMetricsReport());
            document.getElementById('prometheus-generate-analysis')?.addEventListener('click', () => this.generatePlanAnalysis());
            
            // Render variance chart (placeholder - would need a charting library like Chart.js in a real implementation)
            this.renderVarianceChart(variance.task_variances || []);
        } catch (error) {
            this.showError('Failed to load metrics', error);
        }
    }
    
    renderVarianceChart(taskVariances) {
        const chartContainer = document.getElementById('prometheus-variance-chart');
        if (!chartContainer) return;
        
        // This is just a placeholder - in a real implementation you would use a charting library
        let chartContent = '<div class="prometheus-placeholder-chart">';
        
        taskVariances.forEach(task => {
            const variance = task.duration_variance || 0;
            const barWidth = Math.min(Math.abs(variance) * 10, 100);
            const barColor = variance > 0 ? 'var(--prometheus-danger)' : 'var(--prometheus-success)';
            
            chartContent += `
                <div class="prometheus-chart-row">
                    <div class="prometheus-chart-label">${task.name}</div>
                    <div class="prometheus-chart-bar-container">
                        <div class="prometheus-chart-bar" style="width: ${barWidth}%; background-color: ${barColor};"></div>
                    </div>
                    <div class="prometheus-chart-value">${variance} days</div>
                </div>
            `;
        });
        
        chartContent += '</div>';
        chartContainer.innerHTML = chartContent;
    }
    
    async generatePlanAnalysis() {
        if (!this.currentPlan) return;
        
        try {
            const analysisButton = document.getElementById('prometheus-generate-analysis');
            const resultsContainer = document.getElementById('prometheus-analysis-results');
            
            analysisButton.disabled = true;
            analysisButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            resultsContainer.innerHTML = '<div class="prometheus-loading">Generating analysis...</div>';
            
            const analysisResponse = await this.client.generatePlanAnalysis(this.currentPlan.id);
            const analysis = analysisResponse || {};
            
            resultsContainer.innerHTML = `
                <div class="prometheus-analysis">
                    <h4>Summary</h4>
                    <p>${analysis.summary || 'No analysis available'}</p>
                    
                    <h4>Risks</h4>
                    ${!analysis.risks || analysis.risks.length === 0 ? 
                        '<p>No risks identified</p>' :
                        `<ul>${analysis.risks.map(risk => `
                            <li>
                                <strong>${risk.description}</strong> - 
                                Probability: ${risk.probability}, Impact: ${risk.impact}
                            </li>
                        `).join('')}</ul>`
                    }
                    
                    <h4>Recommendations</h4>
                    ${!analysis.recommendations || analysis.recommendations.length === 0 ?
                        '<p>No recommendations available</p>' :
                        `<ul>${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}</ul>`
                    }
                </div>
            `;
            
            analysisButton.disabled = false;
            analysisButton.innerHTML = '<i class="fas fa-brain"></i> Regenerate Analysis';
        } catch (error) {
            this.showError('Failed to generate plan analysis', error);
            
            const analysisButton = document.getElementById('prometheus-generate-analysis');
            if (analysisButton) {
                analysisButton.disabled = false;
                analysisButton.innerHTML = '<i class="fas fa-brain"></i> Generate LLM Analysis';
            }
            
            const resultsContainer = document.getElementById('prometheus-analysis-results');
            if (resultsContainer) {
                resultsContainer.innerHTML = '<div class="prometheus-error">Analysis generation failed</div>';
            }
        }
    }
    
    // Modal handling methods
    showNewPlanModal() {
        // Implementation would show a modal for creating a new plan
        console.log('Show new plan modal');
    }
    
    showNewTaskModal() {
        // Implementation would show a modal for creating a new task
        console.log('Show new task modal');
    }
    
    showEditTaskModal(task) {
        // Implementation would show a modal for editing a task
        console.log('Show edit task modal', task);
    }
    
    showDeleteTaskConfirmation(task) {
        // Implementation would show a confirmation dialog for deleting a task
        console.log('Show delete task confirmation', task);
    }
    
    showTaskProgressModal(task) {
        // Implementation would show a modal for updating task progress
        console.log('Show task progress modal', task);
    }
    
    showNewRetrospectiveModal() {
        // Implementation would show a modal for creating a new retrospective
        console.log('Show new retrospective modal');
    }
    
    showAddFeedbackModal(retroId) {
        // Implementation would show a modal for adding feedback to a retrospective
        console.log('Show add feedback modal', retroId);
    }
    
    // Utility methods
    exportTimeline() {
        // Implementation would export the timeline as PDF or image
        console.log('Export timeline');
    }
    
    exportMetricsReport() {
        // Implementation would export metrics as PDF or CSV
        console.log('Export metrics report');
    }
    
    showError(message, error = null) {
        console.error(message, error);
        
        // Show error message in the UI
        const contentContainer = document.getElementById('prometheus-content');
        if (contentContainer) {
            contentContainer.innerHTML = `
                <div class="prometheus-error">
                    <h3>Error</h3>
                    <p>${message}</p>
                    ${error ? `<p class="prometheus-error-details">${error.message || error}</p>` : ''}
                </div>
            `;
        }
    }
}

/**
 * PrometheusClient - Client for the Prometheus/Epimethius API
 */
class PrometheusClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
    }
    
    async request(endpoint, method = 'GET', data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        return response.json();
    }
    
    // Health check
    async health() {
        return this.request('health');
    }
    
    // Plan methods
    async listPlans() {
        return this.request('plans');
    }
    
    async getPlan(planId) {
        return this.request(`plans/${planId}`);
    }
    
    async createPlan(planData) {
        return this.request('plans', 'POST', planData);
    }
    
    async updatePlan(planId, planData) {
        return this.request(`plans/${planId}`, 'PUT', planData);
    }
    
    async deletePlan(planId) {
        return this.request(`plans/${planId}`, 'DELETE');
    }
    
    // Task methods
    async listTasks(planId) {
        return this.request(`plans/${planId}/tasks`);
    }
    
    async getTask(planId, taskId) {
        return this.request(`plans/${planId}/tasks/${taskId}`);
    }
    
    async createTask(planId, taskData) {
        return this.request(`plans/${planId}/tasks`, 'POST', taskData);
    }
    
    async updateTask(planId, taskId, taskData) {
        return this.request(`plans/${planId}/tasks/${taskId}`, 'PUT', taskData);
    }
    
    async updateTaskProgress(planId, taskId, progressData) {
        return this.request(`plans/${planId}/tasks/${taskId}/progress`, 'PUT', progressData);
    }
    
    async deleteTask(planId, taskId) {
        return this.request(`plans/${planId}/tasks/${taskId}`, 'DELETE');
    }
    
    // Resource methods
    async listResources(planId) {
        return this.request(`plans/${planId}/resources`);
    }
    
    // Analysis methods
    async calculateCriticalPath(planId) {
        return this.request(`plans/${planId}/critical-path`);
    }
    
    async generateTimeline(planId) {
        return this.request(`plans/${planId}/timeline`);
    }
    
    async generatePlanAnalysis(planId) {
        return this.request(`plans/${planId}/analysis`);
    }
    
    async generatePerformanceMetrics(planId) {
        return this.request(`plans/${planId}/performance-metrics`);
    }
    
    async generateVarianceAnalysis(planId) {
        return this.request(`plans/${planId}/variance-analysis`);
    }
    
    // Retrospective methods
    async listRetrospectives(planId) {
        return this.request(`retrospectives?plan_id=${planId}`);
    }
    
    async getRetrospective(retroId) {
        return this.request(`retrospectives/${retroId}`);
    }
    
    async createRetrospective(retroData) {
        return this.request('retrospectives', 'POST', retroData);
    }
    
    async addRetrospectiveFeedback(retroId, feedbackData) {
        return this.request(`retrospectives/${retroId}/feedback`, 'POST', feedbackData);
    }
    
    async generateImprovementSuggestions(retroId) {
        return this.request(`retrospectives/${retroId}/improvement-suggestions`);
    }
    
    async generateRetrospectiveSummary(retroId) {
        return this.request(`retrospectives/${retroId}/summary`);
    }
}

// Export as a module if in a module environment
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = {
        PrometheusUI,
        PrometheusClient
    };
}