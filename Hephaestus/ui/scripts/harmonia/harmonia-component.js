/**
 * Harmonia Component
 * Workflow orchestration and management interface
 */

console.log('[FILE_TRACE] Loading: harmonia-component.js');

class HarmoniaComponent {
    constructor() {
        this.state = {
            initialized: false,
            activeTab: 'workflows',
            workflows: [],
            templates: [],
            executions: [],
            loading: {
                workflows: false,
                templates: false,
                executions: false
            }
        };
        
        // API configuration
        const harmoniaPort = window.HARMONIA_PORT || 8002;
        this.apiUrl = `http://localhost:${harmoniaPort}/api`;
    }
    
    /**
     * Initialize the component
     */
    init() {
        console.log('Initializing Harmonia component');
        
        if (this.state.initialized) {
            console.log('Harmonia component already initialized');
            this.activateComponent();
            return this;
        }
        
        // Setup tabs and event handlers
        this.setupTabs();
        this.setupEventHandlers();
        
        // Load initial data
        this.loadInitialData();
        
        this.state.initialized = true;
        console.log('Harmonia component initialized');
        return this;
    }
    
    /**
     * Activate the component
     */
    activateComponent() {
        console.log('Activating Harmonia component');
        // Refresh data when component is activated
        this.refreshCurrentTab();
    }
    
    /**
     * Setup tab navigation
     */
    setupTabs() {
        const tabButtons = document.querySelectorAll('.harmonia__tab');
        const panels = document.querySelectorAll('.harmonia__panel');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.getAttribute('data-tab');
                
                // Update active states
                tabButtons.forEach(btn => btn.classList.remove('harmonia__tab--active'));
                panels.forEach(panel => panel.style.display = 'none');
                
                button.classList.add('harmonia__tab--active');
                const activePanel = document.getElementById(`${tabName}-panel`);
                if (activePanel) {
                    activePanel.style.display = 'block';
                    this.state.activeTab = tabName;
                    this.loadTabData(tabName);
                }
            });
        });
    }
    
    /**
     * Setup event handlers for buttons and forms
     */
    setupEventHandlers() {
        // New workflow button
        const newWorkflowBtn = document.getElementById('new-workflow-btn');
        if (newWorkflowBtn) {
            newWorkflowBtn.addEventListener('click', () => this.createNewWorkflow());
        }
        
        // Search workflows
        const searchWorkflowBtn = document.getElementById('search-workflow-btn');
        if (searchWorkflowBtn) {
            searchWorkflowBtn.addEventListener('click', () => this.searchWorkflows());
        }
        
        // Refresh buttons
        const refreshBtns = document.querySelectorAll('[data-tekton-action="refresh"]');
        refreshBtns.forEach(btn => {
            btn.addEventListener('click', () => this.refreshCurrentTab());
        });
        
        // Template search
        const templateSearchBtn = document.getElementById('template-search-btn');
        if (templateSearchBtn) {
            templateSearchBtn.addEventListener('click', () => this.searchTemplates());
        }
        
        // New template button
        const newTemplateBtn = document.getElementById('new-template-btn');
        if (newTemplateBtn) {
            newTemplateBtn.addEventListener('click', () => this.createNewTemplate());
        }
        
        // Auto-refresh for monitor tab
        const autoRefreshSelect = document.getElementById('auto-refresh');
        if (autoRefreshSelect) {
            autoRefreshSelect.addEventListener('change', (e) => {
                this.setAutoRefresh(parseInt(e.target.value));
            });
        }
    }
    
    /**
     * Load initial data
     */
    async loadInitialData() {
        // Load data for the active tab
        const activeTab = this.state.activeTab;
        await this.loadTabData(activeTab);
    }
    
    /**
     * Load data for specific tab
     */
    async loadTabData(tabName) {
        switch (tabName) {
            case 'workflows':
                await this.loadWorkflows();
                break;
            case 'templates':
                await this.loadTemplates();
                break;
            case 'executions':
                await this.loadExecutions();
                break;
            case 'monitor':
                await this.loadMonitorData();
                break;
        }
    }
    
    /**
     * Refresh current tab data
     */
    async refreshCurrentTab() {
        await this.loadTabData(this.state.activeTab);
    }
    
    /**
     * Load workflows from API
     */
    async loadWorkflows() {
        const container = document.getElementById('workflow-list');
        const loadingIndicator = document.getElementById('workflow-list-loading');
        
        if (!container || !loadingIndicator) return;
        
        // Show loading
        this.state.loading.workflows = true;
        loadingIndicator.style.display = 'flex';
        container.style.display = 'none';
        
        try {
            const response = await fetch(`${this.apiUrl}/workflows`);
            if (!response.ok) {
                throw new Error(`Failed to load workflows: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.state.workflows = data.workflows || [];
            
            // Render workflows
            this.renderWorkflows();
            
            // Show container
            loadingIndicator.style.display = 'none';
            container.style.display = 'block';
            
        } catch (error) {
            console.error('Error loading workflows:', error);
            this.showError('Failed to load workflows', error.message);
            loadingIndicator.style.display = 'none';
        } finally {
            this.state.loading.workflows = false;
        }
    }
    
    /**
     * Render workflows to UI
     */
    renderWorkflows() {
        const container = document.getElementById('workflow-list');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (this.state.workflows.length === 0) {
            container.innerHTML = `
                <div class="harmonia__empty-state">
                    <p>No workflows found. Create your first workflow to get started.</p>
                </div>
            `;
            return;
        }
        
        this.state.workflows.forEach(workflow => {
            const workflowElement = this.createWorkflowElement(workflow);
            container.appendChild(workflowElement);
        });
    }
    
    /**
     * Create workflow element
     */
    createWorkflowElement(workflow) {
        const div = document.createElement('div');
        div.className = 'harmonia__workflow-item';
        
        div.innerHTML = `
            <div class="harmonia__workflow-info">
                <div class="harmonia__workflow-name">${workflow.name}</div>
                <div class="harmonia__workflow-meta">
                    <span class="harmonia__workflow-tasks">${workflow.task_count || 0} tasks</span>
                    <span class="harmonia__workflow-status">${workflow.status || 'Draft'}</span>
                </div>
                <div class="harmonia__workflow-description">${workflow.description || ''}</div>
            </div>
            <div class="harmonia__workflow-actions">
                <button class="harmonia__workflow-action-btn" data-workflow-id="${workflow.id}" data-action="view">View</button>
                <button class="harmonia__workflow-action-btn" data-workflow-id="${workflow.id}" data-action="edit">Edit</button>
                <button class="harmonia__workflow-action-btn" data-workflow-id="${workflow.id}" data-action="execute">Execute</button>
            </div>
        `;
        
        // Add event handlers
        const buttons = div.querySelectorAll('[data-workflow-id]');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const workflowId = e.target.getAttribute('data-workflow-id');
                const action = e.target.getAttribute('data-action');
                this.handleWorkflowAction(workflowId, action);
            });
        });
        
        return div;
    }
    
    /**
     * Handle workflow action
     */
    async handleWorkflowAction(workflowId, action) {
        switch (action) {
            case 'view':
                // TODO: Implement view workflow
                console.log('View workflow:', workflowId);
                break;
            case 'edit':
                // TODO: Implement edit workflow
                console.log('Edit workflow:', workflowId);
                break;
            case 'execute':
                await this.executeWorkflow(workflowId);
                break;
        }
    }
    
    /**
     * Execute workflow
     */
    async executeWorkflow(workflowId) {
        try {
            const response = await fetch(`${this.apiUrl}/workflows/${workflowId}/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            
            if (!response.ok) {
                throw new Error(`Failed to execute workflow: ${response.statusText}`);
            }
            
            const result = await response.json();
            this.showSuccess('Workflow execution started', `Execution ID: ${result.execution_id}`);
            
            // Switch to executions tab
            this.switchToTab('executions');
            
        } catch (error) {
            console.error('Error executing workflow:', error);
            this.showError('Failed to execute workflow', error.message);
        }
    }
    
    /**
     * Load templates from API
     */
    async loadTemplates() {
        const container = document.getElementById('template-list');
        const loadingIndicator = document.getElementById('template-list-loading');
        
        if (!container || !loadingIndicator) return;
        
        // Show loading
        this.state.loading.templates = true;
        loadingIndicator.style.display = 'flex';
        container.style.display = 'none';
        
        try {
            const response = await fetch(`${this.apiUrl}/templates`);
            if (!response.ok) {
                throw new Error(`Failed to load templates: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.state.templates = data.templates || [];
            
            // Render templates
            this.renderTemplates();
            
            // Show container
            loadingIndicator.style.display = 'none';
            container.style.display = 'block';
            
        } catch (error) {
            console.error('Error loading templates:', error);
            this.showError('Failed to load templates', error.message);
            loadingIndicator.style.display = 'none';
        } finally {
            this.state.loading.templates = false;
        }
    }
    
    /**
     * Render templates to UI
     */
    renderTemplates() {
        const container = document.getElementById('template-list');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (this.state.templates.length === 0) {
            container.innerHTML = `
                <div class="harmonia__empty-state">
                    <p>No templates found. Create your first template to get started.</p>
                </div>
            `;
            return;
        }
        
        this.state.templates.forEach(template => {
            const templateElement = this.createTemplateElement(template);
            container.appendChild(templateElement);
        });
    }
    
    /**
     * Create template element
     */
    createTemplateElement(template) {
        const div = document.createElement('div');
        div.className = 'harmonia__template-item';
        
        div.innerHTML = `
            <div class="harmonia__template-info">
                <div class="harmonia__template-name">${template.name}</div>
                <div class="harmonia__template-meta">
                    <span class="harmonia__template-category">${template.category || 'General'}</span>
                    <span class="harmonia__template-usage">Used ${template.usage_count || 0} times</span>
                </div>
                <div class="harmonia__template-description">${template.description || ''}</div>
            </div>
            <div class="harmonia__template-actions">
                <button class="harmonia__template-action-btn" data-template-id="${template.id}" data-action="view">View</button>
                <button class="harmonia__template-action-btn" data-template-id="${template.id}" data-action="use">Use</button>
                <button class="harmonia__template-action-btn" data-template-id="${template.id}" data-action="edit">Edit</button>
            </div>
        `;
        
        // Add event handlers
        const buttons = div.querySelectorAll('[data-template-id]');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const templateId = e.target.getAttribute('data-template-id');
                const action = e.target.getAttribute('data-action');
                this.handleTemplateAction(templateId, action);
            });
        });
        
        return div;
    }
    
    /**
     * Handle template action
     */
    async handleTemplateAction(templateId, action) {
        switch (action) {
            case 'view':
                // TODO: Implement view template
                console.log('View template:', templateId);
                break;
            case 'use':
                await this.useTemplate(templateId);
                break;
            case 'edit':
                // TODO: Implement edit template
                console.log('Edit template:', templateId);
                break;
        }
    }
    
    /**
     * Use template to create new workflow
     */
    async useTemplate(templateId) {
        try {
            const response = await fetch(`${this.apiUrl}/templates/${templateId}/instantiate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: `New workflow from template`
                })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to instantiate template: ${response.statusText}`);
            }
            
            const result = await response.json();
            this.showSuccess('Workflow created from template', `Workflow ID: ${result.workflow_id}`);
            
            // Switch to workflows tab
            this.switchToTab('workflows');
            
        } catch (error) {
            console.error('Error using template:', error);
            this.showError('Failed to use template', error.message);
        }
    }
    
    /**
     * Load executions from API
     */
    async loadExecutions() {
        const tableBody = document.getElementById('execution-table-body');
        const loadingIndicator = document.getElementById('execution-list-loading');
        
        if (!tableBody) return;
        
        // Show loading
        this.state.loading.executions = true;
        if (loadingIndicator) {
            loadingIndicator.style.display = 'flex';
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/executions`);
            if (!response.ok) {
                throw new Error(`Failed to load executions: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.state.executions = data.executions || [];
            
            // Render executions
            this.renderExecutions();
            
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
            
        } catch (error) {
            console.error('Error loading executions:', error);
            this.showError('Failed to load executions', error.message);
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
        } finally {
            this.state.loading.executions = false;
        }
    }
    
    /**
     * Render executions to table
     */
    renderExecutions() {
        const tableBody = document.getElementById('execution-table-body');
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        if (this.state.executions.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 20px;">
                        No executions found. Execute a workflow to see it here.
                    </td>
                </tr>
            `;
            return;
        }
        
        this.state.executions.forEach(execution => {
            const row = this.createExecutionRow(execution);
            tableBody.appendChild(row);
        });
    }
    
    /**
     * Create execution table row
     */
    createExecutionRow(execution) {
        const tr = document.createElement('tr');
        tr.className = 'harmonia__execution-row';
        
        const statusClass = `harmonia__status--${execution.status.toLowerCase()}`;
        const startTime = new Date(execution.started_at).toLocaleString();
        const duration = this.formatDuration(execution.started_at, execution.completed_at);
        
        tr.innerHTML = `
            <td>${execution.id}</td>
            <td>${execution.workflow_name}</td>
            <td>${startTime}</td>
            <td>${duration}</td>
            <td>
                <span class="harmonia__status ${statusClass}">${execution.status}</span>
            </td>
            <td>
                <button class="harmonia__table-action-btn" data-execution-id="${execution.id}" data-action="view">View</button>
                <button class="harmonia__table-action-btn" data-execution-id="${execution.id}" data-action="logs">Logs</button>
                ${execution.status === 'Running' ? 
                    `<button class="harmonia__table-action-btn" data-execution-id="${execution.id}" data-action="stop">Stop</button>` : 
                    ''}
            </td>
        `;
        
        // Add event handlers
        const buttons = tr.querySelectorAll('[data-execution-id]');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const executionId = e.target.getAttribute('data-execution-id');
                const action = e.target.getAttribute('data-action');
                this.handleExecutionAction(executionId, action);
            });
        });
        
        return tr;
    }
    
    /**
     * Handle execution action
     */
    async handleExecutionAction(executionId, action) {
        switch (action) {
            case 'view':
                // TODO: Implement view execution details
                console.log('View execution:', executionId);
                break;
            case 'logs':
                // TODO: Implement view execution logs
                console.log('View logs for execution:', executionId);
                break;
            case 'stop':
                await this.stopExecution(executionId);
                break;
        }
    }
    
    /**
     * Stop execution
     */
    async stopExecution(executionId) {
        try {
            const response = await fetch(`${this.apiUrl}/executions/${executionId}/stop`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error(`Failed to stop execution: ${response.statusText}`);
            }
            
            this.showSuccess('Execution stopped', `Execution ${executionId} has been stopped`);
            
            // Reload executions
            await this.loadExecutions();
            
        } catch (error) {
            console.error('Error stopping execution:', error);
            this.showError('Failed to stop execution', error.message);
        }
    }
    
    /**
     * Load monitor data
     */
    async loadMonitorData() {
        // TODO: Implement real-time monitoring
        console.log('Loading monitor data');
    }
    
    /**
     * Format duration
     */
    formatDuration(startTime, endTime) {
        if (!startTime) return 'N/A';
        
        const start = new Date(startTime);
        const end = endTime ? new Date(endTime) : new Date();
        const diff = end - start;
        
        const hours = Math.floor(diff / 3600000);
        const minutes = Math.floor((diff % 3600000) / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${seconds}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds}s`;
        } else {
            return `${seconds}s`;
        }
    }
    
    /**
     * Switch to tab
     */
    switchToTab(tabName) {
        const tabButton = document.querySelector(`.harmonia__tab[data-tab="${tabName}"]`);
        if (tabButton) {
            tabButton.click();
        }
    }
    
    /**
     * Show error message
     */
    showError(title, message) {
        // TODO: Implement proper error notification
        console.error(`${title}: ${message}`);
        alert(`${title}\n\n${message}`);
    }
    
    /**
     * Show success message
     */
    showSuccess(title, message) {
        // TODO: Implement proper success notification
        console.log(`${title}: ${message}`);
    }
    
    /**
     * Create new workflow
     */
    async createNewWorkflow() {
        // TODO: Implement workflow creation dialog
        console.log('Create new workflow');
    }
    
    /**
     * Search workflows
     */
    async searchWorkflows() {
        const searchInput = document.getElementById('workflow-search');
        if (!searchInput) return;
        
        const searchTerm = searchInput.value.trim();
        // TODO: Implement search functionality
        console.log('Search workflows:', searchTerm);
    }
    
    /**
     * Create new template
     */
    async createNewTemplate() {
        // TODO: Implement template creation dialog
        console.log('Create new template');
    }
    
    /**
     * Search templates
     */
    async searchTemplates() {
        const searchInput = document.getElementById('template-search');
        if (!searchInput) return;
        
        const searchTerm = searchInput.value.trim();
        // TODO: Implement search functionality
        console.log('Search templates:', searchTerm);
    }
    
    /**
     * Set auto-refresh interval
     */
    setAutoRefresh(seconds) {
        // Clear existing interval
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        
        if (seconds > 0) {
            this.autoRefreshInterval = setInterval(() => {
                if (this.state.activeTab === 'monitor' || this.state.activeTab === 'executions') {
                    this.refreshCurrentTab();
                }
            }, seconds * 1000);
        }
    }
}

// Register component
if (window.tektonUI) {
    window.tektonUI.registerComponent('harmonia', HarmoniaComponent);
} else {
    // Fallback for standalone testing
    window.HarmoniaComponent = HarmoniaComponent;
}

console.log('[FILE_TRACE] Completed: harmonia-component.js');