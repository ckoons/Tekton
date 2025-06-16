/**
 * Synthesis Component
 * 
 * UI component for interacting with the Synthesis execution engine
 */

class SynthesisComponent {
    /**
     * Initialize the component
     */
    constructor() {
        // Configuration
        this.apiBaseUrl = this.getSynthesisUrl();
        this.wsUrl = this.getSynthesisWsUrl();
        this.pollInterval = 5000; // ms
        this.chartUpdateInterval = 5000; // ms
        
        // State
        this.activeExecutions = [];
        this.executionHistory = [];
        this.selectedExecution = null;
        this.websocket = null;
        this.metrics = {
            activeCount: 0,
            capacity: 10,
            load: 0,
            totalExecutions: 0,
            history: []
        };
        
        // Charts
        this.executionChart = null;
        
        // Initialize
        this.setupEventListeners();
        this.initializeWebSocket();
        this.loadExecutions();
        this.setupChart();
        this.startMetricsPolling();
    }
    
    /**
     * Get the base URL for the Synthesis API
     */
    getSynthesisUrl() {
        // Check for environment variable
        if (window.SYNTHESIS_PORT) {
            return `http://localhost:${window.SYNTHESIS_PORT}/api`;
        }
        // Fallback to environment variable lookup
        throw new Error('SYNTHESIS_PORT environment variable not configured');
    }
    
    /**
     * Get the WebSocket URL for Synthesis
     */
    getSynthesisWsUrl() {
        // Check for environment variable
        if (window.SYNTHESIS_PORT) {
            return `ws://localhost:${window.SYNTHESIS_PORT}/ws`;
        }
        // Fallback to environment variable lookup
        throw new Error('SYNTHESIS_PORT environment variable not configured');
    }
    
    /**
     * Set up event listeners for the UI
     */
    setupEventListeners() {
        // New execution button
        document.getElementById('synthesis-new-execution').addEventListener('click', () => {
            this.showExecutionModal();
        });
        
        // Refresh button
        document.getElementById('synthesis-refresh').addEventListener('click', () => {
            this.loadExecutions();
            this.loadMetrics();
        });
        
        // Execute plan button
        document.getElementById('synthesis-execute-plan').addEventListener('click', () => {
            this.executePlan();
        });
        
        // Apply filters button
        document.getElementById('synthesis-apply-filters').addEventListener('click', () => {
            this.loadExecutionHistory();
        });
        
        // Tab change listeners
        const tabs = document.querySelectorAll('#synthesis-component .nav-link');
        tabs.forEach(tab => {
            tab.addEventListener('shown.bs.tab', (event) => {
                const tabId = event.target.id;
                
                if (tabId === 'monitoring-tab') {
                    this.loadMetrics();
                    if (this.executionChart) {
                        this.executionChart.update();
                    }
                } else if (tabId === 'history-tab') {
                    this.loadExecutionHistory();
                }
            });
        });
    }
    
    /**
     * Initialize WebSocket connection for real-time updates
     */
    initializeWebSocket() {
        // Close any existing connection
        if (this.websocket) {
            this.websocket.close();
        }
        
        try {
            // Create new WebSocket connection
            this.websocket = new WebSocket(this.wsUrl);
            
            // Connection opened
            this.websocket.addEventListener('open', (event) => {
                console.log('Connected to Synthesis WebSocket');
                
                // Subscribe to execution events
                this.websocket.send(JSON.stringify({
                    type: 'subscribe',
                    event_types: ['execution_update', 'execution_complete']
                }));
            });
            
            // Listen for messages
            this.websocket.addEventListener('message', (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            });
            
            // Connection closed
            this.websocket.addEventListener('close', (event) => {
                console.log('Disconnected from Synthesis WebSocket');
                
                // Attempt to reconnect after delay
                setTimeout(() => {
                    this.initializeWebSocket();
                }, 5000);
            });
            
            // Handle errors
            this.websocket.addEventListener('error', (error) => {
                console.error('WebSocket error:', error);
            });
            
        } catch (error) {
            console.error('Failed to connect to WebSocket:', error);
        }
    }
    
    /**
     * Handle WebSocket messages
     */
    handleWebSocketMessage(data) {
        // Check message type
        if (data.type === 'event') {
            const event = data.event;
            
            // Handle execution update events
            if (event.type === 'execution_update') {
                this.updateExecution(event.data);
            }
            
            // Handle execution complete events
            else if (event.type === 'execution_complete') {
                this.loadExecutions();
                this.loadMetrics();
                
                // Show notification if not the current execution
                if (this.selectedExecution !== event.data.execution_id) {
                    this.showNotification(
                        `Execution ${event.data.execution_id.substr(0, 8)} completed`,
                        `Status: ${event.data.status}`
                    );
                }
            }
        }
        
        // Handle connected message
        else if (data.type === 'connected') {
            console.log('WebSocket client connected:', data.client_id);
        }
        
        // Handle pong messages
        else if (data.type === 'pong') {
            console.log('Received pong from server');
        }
    }
    
    /**
     * Show a notification
     */
    showNotification(title, message) {
        // Use Hephaestus notification system if available
        if (window.Hephaestus && window.Hephaestus.showNotification) {
            window.Hephaestus.showNotification(title, message);
        }
        // Fallback to console
        else {
            console.log(`Notification: ${title} - ${message}`);
        }
    }
    
    /**
     * Load active executions from the API
     */
    async loadExecutions() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/executions`);
            const data = await response.json();
            
            if (data.status === 'success' && data.data && data.data.executions) {
                this.activeExecutions = data.data.executions.filter(
                    exec => exec.status === 'pending' || exec.status === 'in_progress'
                );
                this.renderActiveExecutions();
                
                // Update metrics
                this.metrics.activeCount = this.activeExecutions.length;
                this.updateMetricsDisplay();
                
                // If we have a selected execution, refresh its details
                if (this.selectedExecution) {
                    this.loadExecutionDetails(this.selectedExecution);
                }
            } else {
                console.error('Failed to load executions:', data);
            }
        } catch (error) {
            console.error('Error loading executions:', error);
        }
    }
    
    /**
     * Render active executions list
     */
    renderActiveExecutions() {
        const container = document.getElementById('synthesis-active-executions');
        
        // Clear container
        container.innerHTML = '';
        
        // Show message if no executions
        if (this.activeExecutions.length === 0) {
            container.innerHTML = '<div class="empty-state">No active executions</div>';
            return;
        }
        
        // Render each execution
        this.activeExecutions.forEach(execution => {
            const card = document.createElement('div');
            card.className = `execution-card ${this.selectedExecution === execution.context_id ? 'active' : ''}`;
            card.dataset.executionId = execution.context_id;
            
            const executionName = execution.plan_id || execution.context_id.substr(0, 8);
            const startTime = execution.start_time ? new Date(execution.start_time * 1000).toLocaleTimeString() : 'N/A';
            
            card.innerHTML = `
                <div class="execution-card-header">
                    <div class="execution-card-title">${executionName}</div>
                    <div class="execution-status status-${execution.status.replace('_', '-')}">${execution.status}</div>
                </div>
                <div class="execution-card-info">
                    <div>Started: ${startTime}</div>
                </div>
            `;
            
            // Add click handler
            card.addEventListener('click', () => {
                this.selectExecution(execution.context_id);
            });
            
            container.appendChild(card);
        });
    }
    
    /**
     * Select an execution to view details
     */
    selectExecution(executionId) {
        this.selectedExecution = executionId;
        
        // Update selected state in UI
        const cards = document.querySelectorAll('.execution-card');
        cards.forEach(card => {
            card.classList.toggle('active', card.dataset.executionId === executionId);
        });
        
        // Load execution details
        this.loadExecutionDetails(executionId);
    }
    
    /**
     * Load execution details
     */
    async loadExecutionDetails(executionId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/executions/${executionId}`);
            const data = await response.json();
            
            if (data.execution_id === executionId) {
                this.renderExecutionDetails(data);
            } else {
                console.error('Execution details mismatch:', data);
            }
            
            // Also load results
            this.loadExecutionResults(executionId);
            
        } catch (error) {
            console.error('Error loading execution details:', error);
        }
    }
    
    /**
     * Load execution results
     */
    async loadExecutionResults(executionId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/executions/${executionId}/results`);
            const data = await response.json();
            
            if (data.status === 'success' && data.data && data.data.results) {
                this.renderExecutionResults(data.data.results);
            }
        } catch (error) {
            console.error('Error loading execution results:', error);
        }
    }
    
    /**
     * Render execution details
     */
    renderExecutionDetails(execution) {
        const container = document.getElementById('synthesis-execution-details');
        
        // Format datetime
        const startTime = execution.data.start_time 
            ? new Date(execution.data.start_time * 1000).toLocaleString() 
            : 'N/A';
        const endTime = execution.data.end_time 
            ? new Date(execution.data.end_time * 1000).toLocaleString() 
            : 'N/A';
        
        // Calculate duration
        let duration = 'N/A';
        if (execution.data.start_time) {
            const end = execution.data.end_time || Date.now() / 1000;
            const seconds = Math.floor(end - execution.data.start_time);
            
            if (seconds < 60) {
                duration = `${seconds}s`;
            } else if (seconds < 3600) {
                duration = `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
            } else {
                duration = `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
            }
        }
        
        container.innerHTML = `
            <div class="execution-details-header">
                <div class="execution-details-title">
                    Execution ${execution.execution_id.substr(0, 8)}
                </div>
                <div class="execution-details-status status-${execution.status.replace('_', '-')}">
                    ${execution.status}
                </div>
            </div>
            
            <div class="execution-details-info">
                <div class="info-item">
                    <div class="info-label">Plan ID</div>
                    <div class="info-value">${execution.data.plan_id || 'N/A'}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Started</div>
                    <div class="info-value">${startTime}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Completed</div>
                    <div class="info-value">${endTime}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Duration</div>
                    <div class="info-value">${duration}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Current Stage</div>
                    <div class="info-value">${execution.data.current_stage || 'N/A'}</div>
                </div>
            </div>
            
            <h4 class="mt-4">Execution Steps</h4>
            <div class="step-list">
                <div class="loading-indicator">Loading steps...</div>
            </div>
            
            <div class="execution-actions mt-4">
                ${execution.status === 'in_progress' || execution.status === 'pending' ? 
                    `<button class="btn btn-danger btn-sm" onclick="synthesisComponent.cancelExecution('${execution.execution_id}')">
                        Cancel Execution
                    </button>` : 
                    ''
                }
            </div>
        `;
    }
    
    /**
     * Render execution results/steps
     */
    renderExecutionResults(results) {
        const container = document.querySelector('#synthesis-execution-details .step-list');
        
        if (!results || results.length === 0) {
            container.innerHTML = '<div class="empty-state">No steps executed yet</div>';
            return;
        }
        
        container.innerHTML = '';
        
        // Render each step
        results.forEach((result, index) => {
            const stepCard = document.createElement('div');
            stepCard.className = 'step-card';
            
            const stepId = result.step_id || `step-${index}`;
            const success = result.success ? 'success' : 'failed';
            
            stepCard.innerHTML = `
                <div class="step-header">
                    <div class="step-title">${stepId}</div>
                    <div class="step-status status-${success}">${success}</div>
                </div>
                
                ${result.data ? `
                <div class="step-result">
                    ${JSON.stringify(result.data, null, 2)}
                </div>
                ` : ''}
            `;
            
            container.appendChild(stepCard);
        });
    }
    
    /**
     * Show the execution modal
     */
    showExecutionModal() {
        // Get modal element
        const modal = document.getElementById('synthesis-execution-modal');
        
        // Set default values
        document.getElementById('synthesis-plan-name').value = `Plan-${new Date().toISOString().substr(0, 10)}`;
        document.getElementById('synthesis-plan-description').value = '';
        document.getElementById('synthesis-plan-steps').value = JSON.stringify([
            {
                "id": "step1",
                "type": "command",
                "parameters": {
                    "command": "echo Hello, World!"
                }
            }
        ], null, 2);
        document.getElementById('synthesis-wait-completion').checked = false;
        
        // Show the modal
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        
        // Store modal instance for later
        this.executionModal = modalInstance;
    }
    
    /**
     * Execute a plan
     */
    async executePlan() {
        try {
            // Get plan data
            const name = document.getElementById('synthesis-plan-name').value.trim();
            const description = document.getElementById('synthesis-plan-description').value.trim();
            const stepsJson = document.getElementById('synthesis-plan-steps').value.trim();
            const waitForCompletion = document.getElementById('synthesis-wait-completion').checked;
            
            // Validate
            if (!name) {
                alert('Please enter a plan name');
                return;
            }
            
            if (!stepsJson) {
                alert('Please enter plan steps');
                return;
            }
            
            let steps;
            try {
                steps = JSON.parse(stepsJson);
            } catch (error) {
                alert('Invalid JSON for plan steps');
                return;
            }
            
            // Create plan object
            const plan = {
                name,
                description,
                steps: Array.isArray(steps) ? steps : [steps]
            };
            
            // Prepare request
            const requestData = {
                plan,
                wait_for_completion: waitForCompletion,
                timeout: waitForCompletion ? 300 : undefined
            };
            
            // Execute plan
            const response = await fetch(`${this.apiBaseUrl}/executions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            
            if (data.execution_id) {
                // Hide modal
                if (this.executionModal) {
                    this.executionModal.hide();
                }
                
                // Show success notification
                this.showNotification(
                    'Execution Started',
                    `Execution ID: ${data.execution_id.substr(0, 8)}`
                );
                
                // Refresh execution list
                this.loadExecutions();
                
                // Select this execution
                this.selectExecution(data.execution_id);
                
            } else {
                alert(`Failed to start execution: ${data.message || 'Unknown error'}`);
            }
            
        } catch (error) {
            console.error('Error executing plan:', error);
            alert(`Error executing plan: ${error.message}`);
        }
    }
    
    /**
     * Cancel an execution
     */
    async cancelExecution(executionId) {
        if (!confirm('Are you sure you want to cancel this execution?')) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/executions/${executionId}/cancel`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification(
                    'Execution Cancelled',
                    `Execution ${executionId.substr(0, 8)} cancelled successfully`
                );
                
                // Refresh execution list
                this.loadExecutions();
                
                // Refresh details if this is the selected execution
                if (this.selectedExecution === executionId) {
                    this.loadExecutionDetails(executionId);
                }
                
            } else {
                alert(`Failed to cancel execution: ${data.message || 'Unknown error'}`);
            }
            
        } catch (error) {
            console.error('Error cancelling execution:', error);
            alert(`Error cancelling execution: ${error.message}`);
        }
    }
    
    /**
     * Update execution data when received from WebSocket
     */
    updateExecution(executionData) {
        // Update active executions list
        const existingIndex = this.activeExecutions.findIndex(
            exec => exec.context_id === executionData.context_id
        );
        
        if (existingIndex >= 0) {
            this.activeExecutions[existingIndex] = executionData;
        } else {
            this.activeExecutions.push(executionData);
        }
        
        // Re-render active executions
        this.renderActiveExecutions();
        
        // Update details if this is the selected execution
        if (this.selectedExecution === executionData.context_id) {
            this.loadExecutionDetails(executionData.context_id);
        }
    }
    
    /**
     * Load execution history
     */
    async loadExecutionHistory() {
        try {
            // Get filter values
            const status = document.getElementById('synthesis-history-status').value;
            const limit = document.getElementById('synthesis-history-limit').value;
            
            // Build query params
            const params = new URLSearchParams();
            if (status) {
                params.append('status', status);
            }
            params.append('limit', limit);
            
            // Fetch execution history
            const response = await fetch(`${this.apiBaseUrl}/executions?${params.toString()}`);
            const data = await response.json();
            
            if (data.status === 'success' && data.data && data.data.executions) {
                this.executionHistory = data.data.executions;
                this.renderExecutionHistory();
                
                // Update metrics
                this.metrics.totalExecutions = this.executionHistory.length;
                this.updateMetricsDisplay();
                
            } else {
                console.error('Failed to load execution history:', data);
            }
            
        } catch (error) {
            console.error('Error loading execution history:', error);
        }
    }
    
    /**
     * Render execution history
     */
    renderExecutionHistory() {
        const tbody = document.getElementById('synthesis-history-rows');
        
        // Clear container
        tbody.innerHTML = '';
        
        // Show message if no history
        if (this.executionHistory.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No execution history</td></tr>';
            return;
        }
        
        // Render each execution
        this.executionHistory.forEach(execution => {
            const row = document.createElement('tr');
            
            const executionId = execution.context_id;
            const planName = execution.plan_id || 'Unknown';
            const status = execution.status;
            
            // Format dates
            const startTime = execution.start_time 
                ? new Date(execution.start_time * 1000).toLocaleString() 
                : 'N/A';
                
            // Calculate duration
            let duration = 'N/A';
            if (execution.start_time) {
                const end = execution.end_time || Date.now() / 1000;
                const seconds = Math.floor(end - execution.start_time);
                
                if (seconds < 60) {
                    duration = `${seconds}s`;
                } else if (seconds < 3600) {
                    duration = `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
                } else {
                    duration = `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
                }
            }
            
            row.innerHTML = `
                <td>${executionId.substr(0, 8)}...</td>
                <td>${planName}</td>
                <td><span class="execution-status status-${status.replace('_', '-')}">${status}</span></td>
                <td>${startTime}</td>
                <td>${duration}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="synthesisComponent.selectExecution('${executionId}')">
                        View
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    /**
     * Load metrics from the API
     */
    async loadMetrics() {
        try {
            const response = await fetch(`${this.apiBaseUrl.replace('/api', '')}/metrics`);
            const data = await response.json();
            
            if (data && !data.errors) {
                // Update metrics
                this.metrics.activeCount = data.active_executions || 0;
                this.metrics.capacity = data.execution_capacity || 10;
                this.metrics.load = data.execution_load || 0;
                this.metrics.totalExecutions = data.total_executions || 0;
                
                // Add to history
                this.metrics.history.push({
                    timestamp: data.timestamp || Date.now() / 1000,
                    activeCount: this.metrics.activeCount,
                    load: this.metrics.load
                });
                
                // Keep only last 60 data points
                if (this.metrics.history.length > 60) {
                    this.metrics.history = this.metrics.history.slice(-60);
                }
                
                // Update UI
                this.updateMetricsDisplay();
                
                // Update chart
                this.updateChart();
                
            } else {
                console.error('Failed to load metrics:', data);
            }
            
        } catch (error) {
            console.error('Error loading metrics:', error);
        }
    }
    
    /**
     * Update metrics display
     */
    updateMetricsDisplay() {
        // Update metric cards
        document.getElementById('synthesis-active-count').querySelector('.metric-value').textContent = 
            this.metrics.activeCount;
            
        document.getElementById('synthesis-capacity').querySelector('.metric-value').textContent = 
            this.metrics.capacity;
            
        document.getElementById('synthesis-load').querySelector('.metric-value').textContent = 
            `${Math.round(this.metrics.load * 100)}%`;
            
        document.getElementById('synthesis-total-executions').querySelector('.metric-value').textContent = 
            this.metrics.totalExecutions;
    }
    
    /**
     * Set up metrics chart
     */
    setupChart() {
        // Check if Chart.js is available
        if (!window.Chart) {
            console.warn('Chart.js not available, skipping chart setup');
            return;
        }
        
        const ctx = document.getElementById('synthesis-execution-chart');
        if (!ctx) {
            console.warn('Chart canvas not found');
            return;
        }
        
        this.executionChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Active Executions',
                        data: [],
                        borderColor: '#0066cc',
                        backgroundColor: 'rgba(0, 102, 204, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3
                    },
                    {
                        label: 'System Load',
                        data: [],
                        borderColor: '#e67e22',
                        backgroundColor: 'rgba(230, 126, 34, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute',
                            displayFormats: {
                                minute: 'HH:mm'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Active Executions'
                        },
                        suggestedMax: this.metrics.capacity
                    },
                    y1: {
                        beginAtZero: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'System Load (%)'
                        },
                        suggestedMax: 100,
                        grid: {
                            drawOnChartArea: false
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                animation: {
                    duration: 0
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                }
            }
        });
    }
    
    /**
     * Update metrics chart
     */
    updateChart() {
        if (!this.executionChart) {
            return;
        }
        
        // Update chart data
        this.executionChart.data.labels = this.metrics.history.map(
            point => new Date(point.timestamp * 1000)
        );
        
        this.executionChart.data.datasets[0].data = this.metrics.history.map(
            point => point.activeCount
        );
        
        this.executionChart.data.datasets[1].data = this.metrics.history.map(
            point => Math.round(point.load * 100)
        );
        
        // Update chart
        this.executionChart.update();
    }
    
    /**
     * Start polling for metrics
     */
    startMetricsPolling() {
        // Ensure it's defined before using it
        if (typeof window !== 'undefined') {
            // Poll for metrics
            window.setInterval(() => {
                this.loadMetrics();
            }, this.chartUpdateInterval);
            
            // Poll for executions
            window.setInterval(() => {
                this.loadExecutions();
            }, this.pollInterval);
        }
    }
}

// Initialize component when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.synthesisComponent = new SynthesisComponent();
});