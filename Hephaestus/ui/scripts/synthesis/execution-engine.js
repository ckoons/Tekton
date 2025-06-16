/**
 * Execution Engine
 * 
 * Manages workflow executions, tracks progress, and handles execution lifecycle.
 */

import { SynthesisService } from './synthesis-service.js';

class ExecutionEngine {
    constructor() {
        // Initialize service
        this.service = new SynthesisService();
        
        // Execution tracking
        this.activeExecutions = new Map();
        this.pollingInterval = null;
        this.pollingTime = 5000; // 5 seconds
        
        // State
        this.state = {
            loading: false,
            error: null
        };
        
        // Event callbacks
        this.onExecutionUpdated = null;
        this.onExecutionCompleted = null;
        
        console.log('[SYNTHESIS] Execution Engine initialized');
    }
    
    /**
     * Start polling for execution updates
     */
    startPolling() {
        if (this.pollingInterval) {
            return; // Already polling
        }
        
        console.log('[SYNTHESIS] Starting execution polling');
        
        this.pollingInterval = setInterval(() => {
            this.pollExecutions();
        }, this.pollingTime);
    }
    
    /**
     * Stop polling for execution updates
     */
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
            console.log('[SYNTHESIS] Stopped execution polling');
        }
    }
    
    /**
     * Poll for updates to all active executions
     */
    async pollExecutions() {
        if (this.activeExecutions.size === 0) {
            return; // No active executions to poll
        }
        
        try {
            // Get all active executions
            const executions = await this.service.getExecutions();
            
            // Update tracked executions
            executions.forEach(execution => {
                const id = execution.id;
                
                // Check if we're already tracking this execution
                if (this.activeExecutions.has(id)) {
                    const current = this.activeExecutions.get(id);
                    
                    // Check if status has changed
                    if (current.status !== execution.status || 
                        current.progress !== execution.progress) {
                        // Update the tracked execution
                        this.activeExecutions.set(id, execution);
                        
                        // Trigger callback if set
                        if (this.onExecutionUpdated) {
                            this.onExecutionUpdated(execution);
                        }
                        
                        // Check if execution completed
                        if (execution.status === 'completed' || 
                            execution.status === 'failed' || 
                            execution.status === 'cancelled') {
                            // Trigger completed callback if set
                            if (this.onExecutionCompleted) {
                                this.onExecutionCompleted(execution);
                            }
                            
                            // Remove from tracking
                            this.activeExecutions.delete(id);
                        }
                    }
                } else if (execution.status === 'running') {
                    // New running execution we're not tracking yet
                    this.activeExecutions.set(id, execution);
                }
            });
            
            // Check if we should stop polling
            if (this.activeExecutions.size === 0) {
                this.stopPolling();
            }
        } catch (error) {
            console.error('[SYNTHESIS] Error polling executions:', error);
        }
    }
    
    /**
     * Get all current executions
     */
    async getExecutions() {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            const executions = await this.service.getExecutions();
            
            // Update tracking of active executions
            executions.forEach(execution => {
                if (execution.status === 'running') {
                    this.activeExecutions.set(execution.id, execution);
                }
            });
            
            // Start polling if there are active executions
            if (this.activeExecutions.size > 0 && !this.pollingInterval) {
                this.startPolling();
            }
            
            this.state.loading = false;
            return executions;
        } catch (error) {
            console.error('[SYNTHESIS] Error getting executions:', error);
            this.state.error = error.message;
            this.state.loading = false;
            throw error;
        }
    }
    
    /**
     * Get execution details by ID
     */
    async getExecution(id) {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            const execution = await this.service.getExecution(id);
            
            this.state.loading = false;
            return execution;
        } catch (error) {
            console.error(`[SYNTHESIS] Error getting execution ${id}:`, error);
            this.state.error = error.message;
            this.state.loading = false;
            throw error;
        }
    }
    
    /**
     * Create and start a new execution
     */
    async startExecution(workflowId, params = {}) {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            console.log(`[SYNTHESIS] Starting execution for workflow ${workflowId}`);
            const execution = await this.service.startExecution(workflowId, params);
            
            // Add to active executions tracking
            if (execution.status === 'running') {
                this.activeExecutions.set(execution.id, execution);
                this.startPolling();
            }
            
            this.state.loading = false;
            return execution;
        } catch (error) {
            console.error(`[SYNTHESIS] Error starting execution:`, error);
            this.state.error = error.message;
            this.state.loading = false;
            throw error;
        }
    }
    
    /**
     * Cancel an execution
     */
    async cancelExecution(id) {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            console.log(`[SYNTHESIS] Cancelling execution ${id}`);
            const result = await this.service.cancelExecution(id);
            
            // Remove from active executions tracking
            this.activeExecutions.delete(id);
            
            // Check if we should stop polling
            if (this.activeExecutions.size === 0) {
                this.stopPolling();
            }
            
            this.state.loading = false;
            return result;
        } catch (error) {
            console.error(`[SYNTHESIS] Error cancelling execution ${id}:`, error);
            this.state.error = error.message;
            this.state.loading = false;
            throw error;
        }
    }
    
    /**
     * Get execution history with optional filters
     */
    async getExecutionHistory(filters = {}) {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            const history = await this.service.getExecutionHistory(filters);
            
            this.state.loading = false;
            return history;
        } catch (error) {
            console.error(`[SYNTHESIS] Error getting execution history:`, error);
            this.state.error = error.message;
            this.state.loading = false;
            throw error;
        }
    }
    
    /**
     * Export execution history to CSV
     */
    async exportExecutionHistory(filters = {}) {
        try {
            // Get execution history
            const history = await this.getExecutionHistory(filters);
            
            // Parse the history into CSV format
            const csvData = this.formatExecutionHistoryAsCsv(history.executions);
            
            // Create and download the CSV file
            const fileName = `synthesis_execution_history_${this.formatDate(new Date())}.csv`;
            this.downloadCsv(csvData, fileName);
            
            return true;
        } catch (error) {
            console.error(`[SYNTHESIS] Error exporting execution history:`, error);
            this.state.error = error.message;
            throw error;
        }
    }
    
    /**
     * Format execution history data as CSV
     */
    formatExecutionHistoryAsCsv(executions) {
        // CSV headers
        const headers = ['ID', 'Workflow', 'Started', 'Ended', 'Duration', 'Status', 'Steps Completed', 'Total Steps'];
        
        // CSV data rows
        const rows = executions.map(exec => [
            exec.id,
            exec.workflow.name,
            exec.startTime,
            exec.endTime || '',
            exec.duration,
            exec.status,
            exec.steps.completed,
            exec.steps.total
        ]);
        
        // Combine headers and rows
        return [headers, ...rows]
            .map(row => row.map(value => `"${value}"`).join(','))
            .join('\n');
    }
    
    /**
     * Download data as a CSV file
     */
    downloadCsv(data, fileName) {
        // Create a Blob with the CSV data
        const blob = new Blob([data], { type: 'text/csv;charset=utf-8;' });
        
        // Create a link element to download the file
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', fileName);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    /**
     * Format date as YYYY-MM-DD
     */
    formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        
        return `${year}-${month}-${day}`;
    }
    
    /**
     * Get monitoring data
     */
    async getMonitoringData(timeRange = '24h', interval = '5m') {
        try {
            this.state.loading = true;
            this.state.error = null;
            
            const monitoringData = await this.service.getMonitoringData(timeRange, interval);
            
            this.state.loading = false;
            return monitoringData;
        } catch (error) {
            console.error(`[SYNTHESIS] Error getting monitoring data:`, error);
            this.state.error = error.message;
            this.state.loading = false;
            throw error;
        }
    }
    
    /**
     * Register callback for execution updates
     */
    registerExecutionUpdateCallback(callback) {
        if (typeof callback === 'function') {
            this.onExecutionUpdated = callback;
        }
    }
    
    /**
     * Register callback for execution completion
     */
    registerExecutionCompletedCallback(callback) {
        if (typeof callback === 'function') {
            this.onExecutionCompleted = callback;
        }
    }
}

// Export the engine class
export { ExecutionEngine };