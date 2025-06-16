/**
 * Harmonia Workflow Orchestration Component
 * 
 * Provides a comprehensive interface for workflow management, including
 * creation, execution, monitoring, and template management.
 */

import { HarmoniaService } from './harmonia-service.js';
import { WorkflowManager } from './workflow-manager.js';

// Debug instrumentation
if (window.debugShim) {
    window.debugShim.registerComponent('harmonia', {
        description: 'Harmonia Workflow Orchestration Component',
        version: '1.0.0'
    });
}

/**
 * Main component class for Harmonia
 */
class HarmoniaComponent {
    constructor() {
        this.debugLog('[HARMONIA] Constructing component');
        
        // Initialize state
        this.state = {
            activeTab: 'workflows',
            workflows: [],
            templates: [],
            executions: [],
            activeExecution: null,
            loading: {
                workflows: false,
                templates: false,
                executions: false
            },
            chatMessages: {
                workflowchat: [],
                teamchat: []
            }
        };
        
        // Create service and workflow manager
        this.service = new HarmoniaService();
        this.workflowManager = new WorkflowManager(this.service);
        
        // Bind methods to maintain 'this' context
        this.init = this.init.bind(this);
        this.setupEventListeners = this.setupEventListeners.bind(this);
        this.loadWorkflows = this.loadWorkflows.bind(this);
        this.loadTemplates = this.loadTemplates.bind(this);
        this.loadExecutions = this.loadExecutions.bind(this);
        this.handleSendMessage = this.handleSendMessage.bind(this);
        this.clearChatMessages = this.clearChatMessages.bind(this);
        this.updateChatPlaceholder = this.updateChatPlaceholder.bind(this);
        this.loadTabContent = this.loadTabContent.bind(this);
        this.saveComponentState = this.saveComponentState.bind(this);
        this.loadComponentState = this.loadComponentState.bind(this);
        
        // Debug logging
        this.debugLog('[HARMONIA] Component constructed');
    }
    
    /**
     * Initialize the component
     */
    async init() {
        this.debugLog('[HARMONIA] Initializing component');
        
        try {
            // Force HTML panel visibility once more
            document.querySelectorAll('#html-panel').forEach(panel => {
                if (panel) panel.style.display = 'block';
            });
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Load stored state if available
            this.loadComponentState();
            
            // Load initial data based on active tab
            this.loadTabContent(this.state.activeTab);
            
            // Update chat placeholder
            this.updateChatPlaceholder(this.state.activeTab);
            
            this.debugLog('[HARMONIA] Component initialized');
        } catch (error) {
            this.debugLog('[HARMONIA] Error initializing component', error);
        }
    }
    
    /**
     * Set up event listeners
     */
    setupEventListeners() {
        this.debugLog('[HARMONIA] Setting up event listeners');
        
        try {
            // Get container
            const harmoniaContainer = document.querySelector('.harmonia');
            if (!harmoniaContainer) {
                this.debugLog('[HARMONIA] Error: Cannot find harmonia container');
                return;
            }
            
            // Chat input and send button
            const chatInput = harmoniaContainer.querySelector('#chat-input');
            const sendButton = harmoniaContainer.querySelector('#send-button');
            
            if (chatInput && sendButton) {
                // Handle send button click
                sendButton.addEventListener('click', this.handleSendMessage);
                
                // Handle Enter key press in chat input
                chatInput.addEventListener('keydown', (event) => {
                    if (event.key === 'Enter' && !event.shiftKey) {
                        event.preventDefault();
                        this.handleSendMessage();
                    }
                });
            }
            
            // Workflow panel buttons
            const addWorkflowBtn = harmoniaContainer.querySelector('#add-workflow-btn');
            if (addWorkflowBtn) {
                addWorkflowBtn.addEventListener('click', () => {
                    this.debugLog('[HARMONIA] Add workflow button clicked');
                    // TODO: Implement workflow creation modal
                });
            }
            
            const workflowSearchBtn = harmoniaContainer.querySelector('#workflow-search-btn');
            if (workflowSearchBtn) {
                workflowSearchBtn.addEventListener('click', () => {
                    const searchInput = harmoniaContainer.querySelector('#workflow-search');
                    if (searchInput) {
                        this.debugLog('[HARMONIA] Search workflows:', searchInput.value);
                        // TODO: Implement workflow search
                    }
                });
            }
            
            // Template panel buttons
            const createTemplateBtn = harmoniaContainer.querySelector('#create-template-btn');
            if (createTemplateBtn) {
                createTemplateBtn.addEventListener('click', () => {
                    this.debugLog('[HARMONIA] Create template button clicked');
                    // TODO: Implement template creation modal
                });
            }
            
            const applyTemplateFilterBtn = harmoniaContainer.querySelector('#apply-template-filter-btn');
            if (applyTemplateFilterBtn) {
                applyTemplateFilterBtn.addEventListener('click', () => {
                    const categoryFilter = harmoniaContainer.querySelector('#template-category-filter');
                    if (categoryFilter) {
                        this.debugLog('[HARMONIA] Apply template filter:', categoryFilter.value);
                        // TODO: Implement template filtering
                    }
                });
            }
            
            // Execution panel buttons
            const applyExecutionFilterBtn = harmoniaContainer.querySelector('#apply-execution-filter-btn');
            if (applyExecutionFilterBtn) {
                applyExecutionFilterBtn.addEventListener('click', () => {
                    const workflowFilter = harmoniaContainer.querySelector('#execution-workflow-filter');
                    const statusFilter = harmoniaContainer.querySelector('#execution-status-filter');
                    if (workflowFilter && statusFilter) {
                        this.debugLog('[HARMONIA] Apply execution filter:', workflowFilter.value, statusFilter.value);
                        // TODO: Implement execution filtering
                    }
                });
            }
            
            // Monitor panel buttons
            const applyViewBtn = harmoniaContainer.querySelector('#apply-view-btn');
            if (applyViewBtn) {
                applyViewBtn.addEventListener('click', () => {
                    const monitorView = harmoniaContainer.querySelector('#monitor-view');
                    if (monitorView) {
                        this.debugLog('[HARMONIA] Apply monitor view:', monitorView.value);
                        // TODO: Implement monitor view switching
                    }
                });
            }
            
            const refreshNowBtn = harmoniaContainer.querySelector('#refresh-now-btn');
            if (refreshNowBtn) {
                refreshNowBtn.addEventListener('click', () => {
                    this.debugLog('[HARMONIA] Refresh monitor');
                    // TODO: Implement monitor refresh
                });
            }
            
            // Auto-refresh select change
            const autoRefreshSelect = harmoniaContainer.querySelector('#auto-refresh');
            if (autoRefreshSelect) {
                autoRefreshSelect.addEventListener('change', () => {
                    this.debugLog('[HARMONIA] Auto-refresh changed:', autoRefreshSelect.value);
                    // TODO: Implement auto-refresh logic
                });
            }
            
            this.debugLog('[HARMONIA] Event listeners set up');
        } catch (error) {
            this.debugLog('[HARMONIA] Error setting up event listeners', error);
        }
    }
    
    /**
     * Load workflows data
     */
    async loadWorkflows() {
        this.debugLog('[HARMONIA] Loading workflows');
        
        try {
            // Update loading state
            this.state.loading.workflows = true;
            this.updateLoadingIndicator('workflow', true);
            
            // Get workflows from service
            const workflows = await this.service.getWorkflows();
            this.state.workflows = workflows;
            
            // Render workflows
            this.renderWorkflows();
            
            this.debugLog('[HARMONIA] Workflows loaded:', workflows.length);
        } catch (error) {
            this.debugLog('[HARMONIA] Error loading workflows', error);
        } finally {
            // Update loading state
            this.state.loading.workflows = false;
            this.updateLoadingIndicator('workflow', false);
        }
    }
    
    /**
     * Render workflows to DOM
     */
    renderWorkflows() {
        this.debugLog('[HARMONIA] Rendering workflows');
        
        try {
            const harmoniaContainer = document.querySelector('.harmonia');
            if (!harmoniaContainer) {
                this.debugLog('[HARMONIA] Error: Cannot find harmonia container');
                return;
            }
            
            const workflowList = harmoniaContainer.querySelector('#workflow-list');
            if (!workflowList) {
                this.debugLog('[HARMONIA] Error: Cannot find workflow list');
                return;
            }
            
            // Clear existing workflows
            workflowList.innerHTML = '';
            
            // If no workflows, show placeholder
            if (this.state.workflows.length === 0) {
                workflowList.innerHTML = `
                    <div class="harmonia__placeholder-content">
                        <h3 class="harmonia__placeholder-title">No Workflows Found</h3>
                        <p class="harmonia__placeholder-text">Create a new workflow to get started.</p>
                    </div>
                `;
                workflowList.style.display = 'flex';
                workflowList.style.justifyContent = 'center';
                workflowList.style.alignItems = 'center';
                return;
            }
            
            // Add workflows to list
            this.state.workflows.forEach(workflow => {
                const workflowElement = document.createElement('div');
                workflowElement.className = 'harmonia__workflow-item';
                
                workflowElement.innerHTML = `
                    <div class="harmonia__workflow-info">
                        <div class="harmonia__workflow-name">${workflow.name}</div>
                        <div class="harmonia__workflow-meta">
                            <span class="harmonia__workflow-tasks">${workflow.taskCount} tasks</span>
                            <span class="harmonia__workflow-status">${workflow.status}</span>
                        </div>
                        <div class="harmonia__workflow-description">${workflow.description}</div>
                    </div>
                    <div class="harmonia__workflow-actions">
                        <button class="harmonia__workflow-action-btn" data-action="view" data-id="${workflow.id}">View</button>
                        <button class="harmonia__workflow-action-btn" data-action="edit" data-id="${workflow.id}">Edit</button>
                        <button class="harmonia__workflow-action-btn" data-action="execute" data-id="${workflow.id}">Execute</button>
                    </div>
                `;
                
                // Add event listeners to buttons
                const viewBtn = workflowElement.querySelector('[data-action="view"]');
                const editBtn = workflowElement.querySelector('[data-action="edit"]');
                const executeBtn = workflowElement.querySelector('[data-action="execute"]');
                
                if (viewBtn) {
                    viewBtn.addEventListener('click', () => {
                        this.debugLog('[HARMONIA] View workflow:', workflow.id);
                        // TODO: Implement workflow view
                    });
                }
                
                if (editBtn) {
                    editBtn.addEventListener('click', () => {
                        this.debugLog('[HARMONIA] Edit workflow:', workflow.id);
                        // TODO: Implement workflow edit
                    });
                }
                
                if (executeBtn) {
                    executeBtn.addEventListener('click', () => {
                        this.debugLog('[HARMONIA] Execute workflow:', workflow.id);
                        // TODO: Implement workflow execution
                    });
                }
                
                workflowList.appendChild(workflowElement);
            });
            
            // Show the list
            workflowList.style.display = 'flex';
            
            this.debugLog('[HARMONIA] Workflows rendered:', this.state.workflows.length);
        } catch (error) {
            this.debugLog('[HARMONIA] Error rendering workflows', error);
        }
    }
    
    /**
     * Load templates data
     */
    async loadTemplates() {
        this.debugLog('[HARMONIA] Loading templates');
        
        try {
            // Update loading state
            this.state.loading.templates = true;
            this.updateLoadingIndicator('template', true);
            
            // Get templates from service
            const templates = await this.service.getTemplates();
            this.state.templates = templates;
            
            // Render templates
            this.renderTemplates();
            
            this.debugLog('[HARMONIA] Templates loaded:', templates.length);
        } catch (error) {
            this.debugLog('[HARMONIA] Error loading templates', error);
        } finally {
            // Update loading state
            this.state.loading.templates = false;
            this.updateLoadingIndicator('template', false);
        }
    }
    
    /**
     * Render templates to DOM
     */
    renderTemplates() {
        this.debugLog('[HARMONIA] Rendering templates');
        
        try {
            const harmoniaContainer = document.querySelector('.harmonia');
            if (!harmoniaContainer) {
                this.debugLog('[HARMONIA] Error: Cannot find harmonia container');
                return;
            }
            
            const templateList = harmoniaContainer.querySelector('#template-list');
            if (!templateList) {
                this.debugLog('[HARMONIA] Error: Cannot find template list');
                return;
            }
            
            // Clear existing templates
            templateList.innerHTML = '';
            
            // If no templates, show placeholder
            if (this.state.templates.length === 0) {
                templateList.innerHTML = `
                    <div class="harmonia__placeholder-content">
                        <h3 class="harmonia__placeholder-title">No Templates Found</h3>
                        <p class="harmonia__placeholder-text">Create a new template to get started.</p>
                    </div>
                `;
                templateList.style.display = 'flex';
                templateList.style.justifyContent = 'center';
                templateList.style.alignItems = 'center';
                return;
            }
            
            // Add templates to list
            this.state.templates.forEach(template => {
                const templateElement = document.createElement('div');
                templateElement.className = 'harmonia__template-item';
                
                templateElement.innerHTML = `
                    <div class="harmonia__template-info">
                        <div class="harmonia__template-name">${template.name}</div>
                        <div class="harmonia__template-meta">
                            <span class="harmonia__template-category">${template.category}</span>
                            <span class="harmonia__template-usage">Used ${template.usageCount} times</span>
                        </div>
                        <div class="harmonia__template-description">${template.description}</div>
                    </div>
                    <div class="harmonia__template-actions">
                        <button class="harmonia__template-action-btn" data-action="view" data-id="${template.id}">View</button>
                        <button class="harmonia__template-action-btn" data-action="use" data-id="${template.id}">Use</button>
                        <button class="harmonia__template-action-btn" data-action="edit" data-id="${template.id}">Edit</button>
                    </div>
                `;
                
                // Add event listeners to buttons
                const viewBtn = templateElement.querySelector('[data-action="view"]');
                const useBtn = templateElement.querySelector('[data-action="use"]');
                const editBtn = templateElement.querySelector('[data-action="edit"]');
                
                if (viewBtn) {
                    viewBtn.addEventListener('click', () => {
                        this.debugLog('[HARMONIA] View template:', template.id);
                        // TODO: Implement template view
                    });
                }
                
                if (useBtn) {
                    useBtn.addEventListener('click', () => {
                        this.debugLog('[HARMONIA] Use template:', template.id);
                        // TODO: Implement template use
                    });
                }
                
                if (editBtn) {
                    editBtn.addEventListener('click', () => {
                        this.debugLog('[HARMONIA] Edit template:', template.id);
                        // TODO: Implement template edit
                    });
                }
                
                templateList.appendChild(templateElement);
            });
            
            // Show the list
            templateList.style.display = 'flex';
            
            this.debugLog('[HARMONIA] Templates rendered:', this.state.templates.length);
        } catch (error) {
            this.debugLog('[HARMONIA] Error rendering templates', error);
        }
    }
    
    /**
     * Load executions data
     */
    async loadExecutions() {
        this.debugLog('[HARMONIA] Loading executions');
        
        try {
            // Update loading state
            this.state.loading.executions = true;
            this.updateLoadingIndicator('execution', true);
            
            // Get executions from service
            const executions = await this.service.getExecutions();
            this.state.executions = executions;
            
            // Render executions
            this.renderExecutions();
            
            this.debugLog('[HARMONIA] Executions loaded:', executions.length);
        } catch (error) {
            this.debugLog('[HARMONIA] Error loading executions', error);
        } finally {
            // Update loading state
            this.state.loading.executions = false;
            this.updateLoadingIndicator('execution', false);
        }
    }
    
    /**
     * Render executions to DOM
     */
    renderExecutions() {
        this.debugLog('[HARMONIA] Rendering executions');
        
        try {
            const harmoniaContainer = document.querySelector('.harmonia');
            if (!harmoniaContainer) {
                this.debugLog('[HARMONIA] Error: Cannot find harmonia container');
                return;
            }
            
            const executionList = harmoniaContainer.querySelector('#execution-list');
            if (!executionList) {
                this.debugLog('[HARMONIA] Error: Cannot find execution list');
                return;
            }
            
            // Clear existing table content
            const tableBody = executionList.querySelector('tbody');
            if (tableBody) {
                tableBody.innerHTML = '';
            }
            
            // If no executions, show placeholder
            if (this.state.executions.length === 0) {
                executionList.innerHTML = `
                    <div class="harmonia__placeholder-content">
                        <h3 class="harmonia__placeholder-title">No Executions Found</h3>
                        <p class="harmonia__placeholder-text">Execute a workflow to see executions here.</p>
                    </div>
                `;
                executionList.style.display = 'flex';
                executionList.style.justifyContent = 'center';
                executionList.style.alignItems = 'center';
                return;
            }
            
            // Keep the table structure intact
            if (!tableBody) {
                executionList.innerHTML = `
                    <table class="harmonia__executions-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Workflow</th>
                                <th>Start Time</th>
                                <th>Duration</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                `;
            }
            
            // Get the table body again if it was just created
            const tbody = executionList.querySelector('tbody');
            if (!tbody) {
                this.debugLog('[HARMONIA] Error: Cannot find execution table body');
                return;
            }
            
            // Add executions to table
            this.state.executions.forEach(execution => {
                const row = document.createElement('tr');
                row.className = 'harmonia__execution-row';
                
                // Determine status class
                let statusClass = '';
                switch (execution.status.toLowerCase()) {
                    case 'completed':
                        statusClass = 'harmonia__status--completed';
                        break;
                    case 'running':
                        statusClass = 'harmonia__status--running';
                        break;
                    case 'failed':
                        statusClass = 'harmonia__status--failed';
                        break;
                    case 'waiting':
                        statusClass = 'harmonia__status--waiting';
                        break;
                    default:
                        statusClass = '';
                }
                
                // Create action buttons based on status
                let actionButtons = `
                    <button class="harmonia__table-action-btn" data-action="view" data-id="${execution.id}">View</button>
                    <button class="harmonia__table-action-btn" data-action="logs" data-id="${execution.id}">Logs</button>
                `;
                
                if (execution.status.toLowerCase() === 'running') {
                    actionButtons += `<button class="harmonia__table-action-btn" data-action="stop" data-id="${execution.id}">Stop</button>`;
                }
                
                row.innerHTML = `
                    <td>${execution.id}</td>
                    <td>${execution.workflowName}</td>
                    <td>${execution.startTime}</td>
                    <td>${execution.duration}</td>
                    <td>
                        <span class="harmonia__status ${statusClass}">${execution.status}</span>
                    </td>
                    <td>
                        ${actionButtons}
                    </td>
                `;
                
                // Add event listeners to buttons
                const viewBtn = row.querySelector('[data-action="view"]');
                const logsBtn = row.querySelector('[data-action="logs"]');
                const stopBtn = row.querySelector('[data-action="stop"]');
                
                if (viewBtn) {
                    viewBtn.addEventListener('click', () => {
                        this.debugLog('[HARMONIA] View execution:', execution.id);
                        // TODO: Implement execution view
                    });
                }
                
                if (logsBtn) {
                    logsBtn.addEventListener('click', () => {
                        this.debugLog('[HARMONIA] View execution logs:', execution.id);
                        // TODO: Implement execution logs view
                    });
                }
                
                if (stopBtn) {
                    stopBtn.addEventListener('click', () => {
                        this.debugLog('[HARMONIA] Stop execution:', execution.id);
                        // TODO: Implement execution stop
                    });
                }
                
                tbody.appendChild(row);
            });
            
            // Show the list
            executionList.style.display = 'block';
            
            this.debugLog('[HARMONIA] Executions rendered:', this.state.executions.length);
        } catch (error) {
            this.debugLog('[HARMONIA] Error rendering executions', error);
        }
    }
    
    /**
     * Handle send message button click or Enter key press
     */
    handleSendMessage() {
        this.debugLog('[HARMONIA] Handle send message');
        
        try {
            const harmoniaContainer = document.querySelector('.harmonia');
            if (!harmoniaContainer) {
                this.debugLog('[HARMONIA] Error: Cannot find harmonia container');
                return;
            }
            
            const chatInput = harmoniaContainer.querySelector('#chat-input');
            if (!chatInput) {
                this.debugLog('[HARMONIA] Error: Cannot find chat input');
                return;
            }
            
            const message = chatInput.value.trim();
            if (!message) {
                return;
            }
            
            // Get active tab
            const activeTab = harmoniaContainer.querySelector('.harmonia__tab--active');
            if (!activeTab) {
                this.debugLog('[HARMONIA] Error: Cannot find active tab');
                return;
            }
            
            const tabId = activeTab.getAttribute('data-tab');
            if (tabId !== 'workflowchat' && tabId !== 'teamchat') {
                this.debugLog('[HARMONIA] Message sent from non-chat tab:', tabId);
                return;
            }
            
            // Add message to chat
            this.addChatMessage(tabId, 'user', message);
            
            // Clear input
            chatInput.value = '';
            
            // Send message to service
            this.service.sendChatMessage(tabId, message)
                .then(response => {
                    // Add response to chat
                    this.addChatMessage(tabId, 'assistant', response);
                })
                .catch(error => {
                    this.debugLog('[HARMONIA] Error sending message', error);
                    // Add error message to chat
                    this.addChatMessage(tabId, 'system', 'Error: Failed to send message. Please try again.');
                });
        } catch (error) {
            this.debugLog('[HARMONIA] Error handling send message', error);
        }
    }
    
    /**
     * Add a message to the chat
     * @param {string} tabId - The ID of the chat tab ('workflowchat' or 'teamchat')
     * @param {string} sender - The sender of the message ('user', 'assistant', or 'system')
     * @param {string} content - The content of the message
     */
    addChatMessage(tabId, sender, content) {
        this.debugLog(`[HARMONIA] Adding ${sender} message to ${tabId}`);
        
        try {
            const harmoniaContainer = document.querySelector('.harmonia');
            if (!harmoniaContainer) {
                this.debugLog('[HARMONIA] Error: Cannot find harmonia container');
                return;
            }
            
            // Get chat container based on tab ID
            const chatMessagesContainer = harmoniaContainer.querySelector(`#${tabId}-messages`);
            if (!chatMessagesContainer) {
                this.debugLog(`[HARMONIA] Error: Cannot find ${tabId} messages container`);
                return;
            }
            
            // Create message element
            const messageElement = document.createElement('div');
            messageElement.className = `harmonia__message harmonia__message--${sender}`;
            
            messageElement.innerHTML = `
                <div class="harmonia__message-content">
                    <div class="harmonia__message-text">${content}</div>
                </div>
            `;
            
            // Add message to container
            chatMessagesContainer.appendChild(messageElement);
            
            // Scroll to bottom
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
            
            // Add message to state
            this.state.chatMessages[tabId].push({
                sender,
                content,
                timestamp: new Date().toISOString()
            });
            
            // Save state
            this.saveComponentState();
            
            this.debugLog(`[HARMONIA] Message added to ${tabId}`);
        } catch (error) {
            this.debugLog('[HARMONIA] Error adding chat message', error);
        }
    }
    
    /**
     * Clear chat messages in a specific tab
     * @param {string} tabId - The ID of the chat tab to clear
     */
    clearChatMessages(tabId) {
        this.debugLog(`[HARMONIA] Clearing messages in ${tabId}`);
        
        try {
            // Get chat container based on tab ID
            const harmoniaContainer = document.querySelector('.harmonia');
            if (!harmoniaContainer) {
                this.debugLog('[HARMONIA] Error: Cannot find harmonia container');
                return;
            }
            
            const chatMessagesContainer = harmoniaContainer.querySelector(`#${tabId}-messages`);
            if (!chatMessagesContainer) {
                this.debugLog(`[HARMONIA] Error: Cannot find ${tabId} messages container`);
                return;
            }
            
            // Keep only system message
            const systemMessages = chatMessagesContainer.querySelectorAll('.harmonia__message--system');
            if (systemMessages.length > 0) {
                const firstSystemMessage = systemMessages[0];
                chatMessagesContainer.innerHTML = '';
                chatMessagesContainer.appendChild(firstSystemMessage);
            } else {
                chatMessagesContainer.innerHTML = '';
            }
            
            // Clear messages in state, except system message
            const systemMessage = this.state.chatMessages[tabId].find(msg => msg.sender === 'system');
            this.state.chatMessages[tabId] = systemMessage ? [systemMessage] : [];
            
            // Save state
            this.saveComponentState();
            
            this.debugLog(`[HARMONIA] Messages cleared in ${tabId}`);
        } catch (error) {
            this.debugLog('[HARMONIA] Error clearing chat messages', error);
        }
    }
    
    /**
     * Update chat input placeholder based on active tab
     * @param {string} tabId - The ID of the active tab
     */
    updateChatPlaceholder(tabId) {
        this.debugLog(`[HARMONIA] Updating chat placeholder for ${tabId}`);
        
        try {
            const harmoniaContainer = document.querySelector('.harmonia');
            if (!harmoniaContainer) {
                this.debugLog('[HARMONIA] Error: Cannot find harmonia container');
                return;
            }
            
            const chatInput = harmoniaContainer.querySelector('#chat-input');
            if (!chatInput) {
                this.debugLog('[HARMONIA] Error: Cannot find chat input');
                return;
            }
            
            // Update placeholder based on tab
            switch (tabId) {
                case 'workflowchat':
                    chatInput.placeholder = 'Ask a question about workflows, templates, or executions...';
                    break;
                case 'teamchat':
                    chatInput.placeholder = 'Send a message to the team...';
                    break;
                default:
                    chatInput.placeholder = 'Enter chat message, workflow questions, or execution queries';
                    break;
            }
            
            // Show/hide chat input based on tab
            const footer = harmoniaContainer.querySelector('.harmonia__footer');
            if (footer) {
                if (tabId === 'workflowchat' || tabId === 'teamchat') {
                    footer.style.display = 'block';
                } else {
                    footer.style.display = 'none';
                }
            }
            
            this.debugLog(`[HARMONIA] Chat placeholder updated for ${tabId}`);
        } catch (error) {
            this.debugLog('[HARMONIA] Error updating chat placeholder', error);
        }
    }
    
    /**
     * Load content based on active tab
     * @param {string} tabId - The ID of the active tab
     */
    loadTabContent(tabId) {
        this.debugLog(`[HARMONIA] Loading content for ${tabId}`);
        
        try {
            switch (tabId) {
                case 'workflows':
                    this.loadWorkflows();
                    break;
                case 'templates':
                    this.loadTemplates();
                    break;
                case 'executions':
                    this.loadExecutions();
                    break;
                case 'monitor':
                    // TODO: Implement monitor tab loading
                    break;
                case 'workflowchat':
                    // Workflow chat already initialized
                    break;
                case 'teamchat':
                    // Team chat already initialized
                    break;
                default:
                    this.debugLog(`[HARMONIA] Unknown tab: ${tabId}`);
                    break;
            }
            
            this.debugLog(`[HARMONIA] Content loaded for ${tabId}`);
        } catch (error) {
            this.debugLog('[HARMONIA] Error loading tab content', error);
        }
    }
    
    /**
     * Update loading indicator for a specific panel
     * @param {string} type - The type of panel ('workflow', 'template', or 'execution')
     * @param {boolean} isLoading - Whether the panel is loading
     */
    updateLoadingIndicator(type, isLoading) {
        this.debugLog(`[HARMONIA] Updating ${type} loading indicator: ${isLoading}`);
        
        try {
            const harmoniaContainer = document.querySelector('.harmonia');
            if (!harmoniaContainer) {
                this.debugLog('[HARMONIA] Error: Cannot find harmonia container');
                return;
            }
            
            const loadingIndicator = harmoniaContainer.querySelector(`#${type}-list-loading`);
            const listContainer = harmoniaContainer.querySelector(`#${type}-list`);
            
            if (loadingIndicator && listContainer) {
                if (isLoading) {
                    loadingIndicator.style.display = 'flex';
                    listContainer.style.display = 'none';
                } else {
                    loadingIndicator.style.display = 'none';
                    listContainer.style.display = 'block';
                }
            }
            
            this.debugLog(`[HARMONIA] ${type} loading indicator updated: ${isLoading}`);
        } catch (error) {
            this.debugLog('[HARMONIA] Error updating loading indicator', error);
        }
    }
    
    /**
     * Save component state to local storage
     */
    saveComponentState() {
        this.debugLog('[HARMONIA] Saving component state');
        
        try {
            // Create save state object
            const saveState = {
                activeTab: this.state.activeTab,
                chatMessages: this.state.chatMessages,
                timestamp: new Date().toISOString()
            };
            
            // Save to local storage
            localStorage.setItem('harmoniaComponentState', JSON.stringify(saveState));
            
            this.debugLog('[HARMONIA] Component state saved');
        } catch (error) {
            this.debugLog('[HARMONIA] Error saving component state', error);
        }
    }
    
    /**
     * Load component state from local storage
     */
    loadComponentState() {
        this.debugLog('[HARMONIA] Loading component state');
        
        try {
            // Get state from local storage
            const savedState = localStorage.getItem('harmoniaComponentState');
            if (!savedState) {
                this.debugLog('[HARMONIA] No saved state found');
                return;
            }
            
            // Parse saved state
            const parsedState = JSON.parse(savedState);
            
            // Update state properties
            if (parsedState.activeTab) {
                this.state.activeTab = parsedState.activeTab;
                
                // Update active tab in DOM
                window.harmonia_switchTab(this.state.activeTab);
            }
            
            if (parsedState.chatMessages) {
                this.state.chatMessages = parsedState.chatMessages;
                
                // Render chat messages
                this.renderChatMessages('workflowchat');
                this.renderChatMessages('teamchat');
            }
            
            this.debugLog('[HARMONIA] Component state loaded');
        } catch (error) {
            this.debugLog('[HARMONIA] Error loading component state', error);
        }
    }
    
    /**
     * Render chat messages for a specific tab
     * @param {string} tabId - The ID of the chat tab to render
     */
    renderChatMessages(tabId) {
        this.debugLog(`[HARMONIA] Rendering messages for ${tabId}`);
        
        try {
            const harmoniaContainer = document.querySelector('.harmonia');
            if (!harmoniaContainer) {
                this.debugLog('[HARMONIA] Error: Cannot find harmonia container');
                return;
            }
            
            const chatMessagesContainer = harmoniaContainer.querySelector(`#${tabId}-messages`);
            if (!chatMessagesContainer) {
                this.debugLog(`[HARMONIA] Error: Cannot find ${tabId} messages container`);
                return;
            }
            
            // Clear existing messages
            chatMessagesContainer.innerHTML = '';
            
            // Render messages
            this.state.chatMessages[tabId].forEach(message => {
                const messageElement = document.createElement('div');
                messageElement.className = `harmonia__message harmonia__message--${message.sender}`;
                
                messageElement.innerHTML = `
                    <div class="harmonia__message-content">
                        <div class="harmonia__message-text">${message.content}</div>
                    </div>
                `;
                
                chatMessagesContainer.appendChild(messageElement);
            });
            
            // If no messages, add system welcome message
            if (chatMessagesContainer.children.length === 0) {
                const welcomeMessage = document.createElement('div');
                welcomeMessage.className = 'harmonia__message harmonia__message--system';
                
                if (tabId === 'workflowchat') {
                    welcomeMessage.innerHTML = `
                        <div class="harmonia__message-content">
                            <div class="harmonia__message-text">
                                <h3 class="harmonia__message-title">Workflow Assistant</h3>
                                <p>This chat provides assistance with workflow creation and management. Ask questions about:</p>
                                <ul>
                                    <li>Creating new workflows and templates</li>
                                    <li>Debugging workflow execution issues</li>
                                    <li>Optimizing workflow performance</li>
                                    <li>Understanding workflow state and transitions</li>
                                </ul>
                            </div>
                        </div>
                    `;
                } else {
                    welcomeMessage.innerHTML = `
                        <div class="harmonia__message-content">
                            <div class="harmonia__message-text">
                                <h3 class="harmonia__message-title">Tekton Team Chat</h3>
                                <p>This chat is shared across all Tekton components. Use this for team communication and coordination.</p>
                            </div>
                        </div>
                    `;
                }
                
                chatMessagesContainer.appendChild(welcomeMessage);
                
                // Add welcome message to state
                this.state.chatMessages[tabId].push({
                    sender: 'system',
                    content: welcomeMessage.querySelector('.harmonia__message-text').innerHTML,
                    timestamp: new Date().toISOString()
                });
            }
            
            // Scroll to bottom
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
            
            this.debugLog(`[HARMONIA] ${tabId} messages rendered`);
        } catch (error) {
            this.debugLog('[HARMONIA] Error rendering chat messages', error);
        }
    }
    
    /**
     * Debug logging with component prefix
     * @param {string} message - The message to log
     * @param {Error} [error] - Optional error object
     */
    debugLog(message, error) {
        // Use debug shim if available
        if (window.debugShim) {
            if (error) {
                window.debugShim.logError('harmonia', message, error);
            } else {
                window.debugShim.log('harmonia', message);
            }
        } else {
            // Fallback to console
            if (error) {
                console.error(message, error);
            } else {
                console.log(message);
            }
        }
    }
}

// Initialize component when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('[HARMONIA] DOM loaded, initializing component');
    
    // Create and initialize component
    window.harmoniaComponent = new HarmoniaComponent();
    window.harmoniaComponent.init();
});

// Export component
export { HarmoniaComponent };