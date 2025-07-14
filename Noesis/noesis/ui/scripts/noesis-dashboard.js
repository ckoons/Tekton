/**
 * Noesis Dashboard Main Controller
 * Coordinates all dashboard functionality and component interactions
 */

import { APIClient } from './api-client.js';
import { StreamingManager } from './streaming-manager.js';
import { MemoryVisualizer } from './memory-visualizer.js';
import { ManifoldAnalyzer } from './manifold-analyzer.js';
import { DynamicsVisualizer } from './dynamics-visualizer.js';
import { CatastropheAnalyzer } from './catastrophe-analyzer.js';
import { InsightsManager } from './insights-manager.js';

class NoesisDashboard {
    constructor() {
        this.apiClient = new APIClient();
        this.streamingManager = new StreamingManager(this.apiClient);
        this.memoryVisualizer = new MemoryVisualizer();
        this.manifoldAnalyzer = new ManifoldAnalyzer();
        this.dynamicsVisualizer = new DynamicsVisualizer();
        this.catastropheAnalyzer = new CatastropheAnalyzer();
        this.insightsManager = new InsightsManager(this.apiClient);
        
        this.currentTab = 'overview';
        this.updateInterval = null;
        this.isInitialized = false;
        
        console.log('🧠 Noesis Dashboard initialized');
    }
    
    async init() {
        try {
            this.showLoading(true);
            
            // Initialize UI components
            this.setupEventListeners();
            this.setupTabNavigation();
            
            // Initialize API client and check connection
            await this.apiClient.init();
            this.updateConnectionStatus(true);
            
            // Initialize all sub-managers
            await this.streamingManager.init();
            await this.memoryVisualizer.init();
            await this.manifoldAnalyzer.init();
            await this.dynamicsVisualizer.init();
            await this.catastropheAnalyzer.init();
            await this.insightsManager.init();
            
            // Load initial data
            await this.loadInitialData();
            
            // Start periodic updates
            this.startPeriodicUpdates();
            
            this.isInitialized = true;
            console.log('✅ Noesis Dashboard fully initialized');
            
        } catch (error) {
            console.error('❌ Dashboard initialization failed:', error);
            this.showError('Failed to initialize dashboard: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    setupEventListeners() {
        // Streaming controls
        document.getElementById('start-streaming').addEventListener('click', () => {
            this.startStreaming();
        });
        
        document.getElementById('stop-streaming').addEventListener('click', () => {
            this.stopStreaming();
        });
        
        document.getElementById('force-poll').addEventListener('click', () => {
            this.forcePoll();
        });
        
        // Modal controls
        const modal = document.getElementById('error-modal');
        const closeBtn = modal.querySelector('.close');
        const okBtn = document.getElementById('error-ok');
        
        [closeBtn, okBtn].forEach(btn => {
            btn.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        });
        
        // Window events
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
        
        // Handle API connection changes
        this.apiClient.addEventListener('connectionChange', (event) => {
            this.updateConnectionStatus(event.detail.connected);
        });
        
        // Handle streaming state changes
        this.streamingManager.addEventListener('streamingStateChange', (event) => {
            this.updateStreamingControls(event.detail.active);
        });
        
        console.log('📱 Event listeners setup complete');
    }
    
    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabPanels = document.querySelectorAll('.tab-panel');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabId = button.dataset.tab;
                this.switchTab(tabId);
            });
        });
        
        console.log('🗂️ Tab navigation setup complete');
    }
    
    switchTab(tabId) {
        if (this.currentTab === tabId) return;
        
        // Update button states
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
        
        // Update panel visibility
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(`${tabId}-tab`).classList.add('active');
        
        this.currentTab = tabId;
        
        // Trigger tab-specific updates
        this.onTabChange(tabId);
        
        console.log(`📋 Switched to tab: ${tabId}`);
    }
    
    onTabChange(tabId) {
        // Tab-specific initialization and updates
        switch (tabId) {
            case 'overview':
                this.updateOverview();
                break;
            case 'memory-analysis':
                this.memoryVisualizer.refresh();
                break;
            case 'manifold-space':
                this.manifoldAnalyzer.refresh();
                break;
            case 'dynamics':
                this.dynamicsVisualizer.refresh();
                break;
            case 'catastrophe':
                this.catastropheAnalyzer.refresh();
                break;
            case 'insights':
                this.insightsManager.refresh();
                break;
            case 'streaming':
                this.streamingManager.refresh();
                break;
        }
    }
    
    async loadInitialData() {
        try {
            // Load system status
            const status = await this.apiClient.getStatus();
            this.updateSystemStatus(status);
            
            // Load streaming status
            const streamingStatus = await this.apiClient.getStreamingStatus();
            this.updateStreamingStatus(streamingStatus);
            
            // Load initial insights
            const insights = await this.apiClient.getInsights();
            this.insightsManager.updateInsights(insights);
            
            // Load memory analysis if available
            try {
                const memoryAnalysis = await this.apiClient.getMemoryAnalysis();
                this.updateMemoryAnalysis(memoryAnalysis);
            } catch (error) {
                console.warn('No memory analysis data available yet');
            }
            
            console.log('📊 Initial data loaded');
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }
    
    startPeriodicUpdates() {
        // Update every 5 seconds
        this.updateInterval = setInterval(() => {
            this.performPeriodicUpdate();
        }, 5000);
        
        console.log('⏰ Periodic updates started');
    }
    
    async performPeriodicUpdate() {
        if (!this.isInitialized) return;
        
        try {
            // Update based on current tab
            switch (this.currentTab) {
                case 'overview':
                    await this.updateOverview();
                    break;
                case 'memory-analysis':
                    await this.updateMemoryData();
                    break;
                case 'manifold-space':
                    await this.updateManifoldData();
                    break;
                case 'dynamics':
                    await this.updateDynamicsData();
                    break;
                case 'catastrophe':
                    await this.updateCatastropheData();
                    break;
                case 'insights':
                    await this.updateInsightsData();
                    break;
                case 'streaming':
                    await this.updateStreamingData();
                    break;
            }
            
            // Always update quick stats
            await this.updateQuickStats();
            
        } catch (error) {
            console.error('Periodic update failed:', error);
        }
    }
    
    async updateOverview() {
        try {
            // Update system status
            const health = await this.apiClient.getStreamingHealth();
            this.updateSystemStatus(health);
            
            // Update recent activity
            await this.updateRecentActivity();
            
            // Update component health
            this.updateComponentHealth(health);
            
        } catch (error) {
            console.error('Failed to update overview:', error);
        }
    }
    
    updateSystemStatus(status) {
        const frameworkStatus = document.getElementById('framework-status');
        const streamStatus = document.getElementById('stream-status');
        const engramStatus = document.getElementById('engram-status');
        const analyzerStatus = document.getElementById('analyzer-status');
        
        if (status && status.components) {
            const components = status.components;
            
            frameworkStatus.textContent = components.theoretical_framework ? '✅ Active' : '❌ Inactive';
            streamStatus.textContent = components.stream_manager ? '✅ Active' : '❌ Inactive';
            engramStatus.textContent = components.engram_streamer === 'streaming' ? '🔄 Streaming' : 
                                     components.engram_streamer === 'ready' ? '⏸️ Ready' : '❌ Unavailable';
            analyzerStatus.textContent = components.memory_analyzer ? '✅ Active' : '❌ Inactive';
        }
    }
    
    async updateQuickStats() {
        try {
            const stats = await this.apiClient.getStreamingStatistics();
            
            if (stats && stats.memory_statistics) {
                const memStats = stats.memory_statistics;
                
                document.getElementById('total-observations').textContent = 
                    memStats.total_observations || 0;
                document.getElementById('total-events').textContent = 
                    memStats.total_events || 0;
            }
            
            if (stats && stats.stream_status) {
                const streamStats = stats.stream_status;
                
                document.getElementById('uptime-minutes').textContent = 
                    Math.floor(streamStats.uptime_minutes || 0);
            }
            
            // Update insights count
            const insights = await this.apiClient.getInsights();
            document.getElementById('insights-count').textContent = 
                insights.insights ? insights.insights.length : 0;
                
        } catch (error) {
            console.error('Failed to update quick stats:', error);
        }
    }
    
    async updateRecentActivity() {
        const activityContainer = document.getElementById('recent-activity');
        
        try {
            // Get recent memory history
            const history = await this.apiClient.getMemoryHistory(5);
            
            if (history && history.history) {
                const activities = history.history.slice(-5).map(state => ({
                    type: 'memory_state',
                    message: `Memory state updated - ${Object.keys(state.thought_states || {}).length} thoughts`,
                    timestamp: new Date(state.timestamp)
                }));
                
                this.renderActivityFeed(activities, activityContainer);
            }
            
        } catch (error) {
            activityContainer.innerHTML = '<p class="text-muted">No recent activity data available</p>';
        }
    }
    
    renderActivityFeed(activities, container) {
        if (!activities || activities.length === 0) {
            container.innerHTML = '<p class="text-muted">No recent activity</p>';
            return;
        }
        
        const html = activities.map(activity => `
            <div class="activity-item">
                <div>${activity.message}</div>
                <div class="activity-time">${this.formatTime(activity.timestamp)}</div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    updateComponentHealth(health) {
        const healthContainer = document.getElementById('component-health');
        
        if (!health || !health.components) {
            healthContainer.innerHTML = '<p class="text-muted">Health data unavailable</p>';
            return;
        }
        
        const components = health.components;
        const healthItems = Object.entries(components).map(([name, status]) => {
            const statusIcon = status === true || status === 'healthy' || status === 'streaming' ? '✅' : 
                             status === 'ready' ? '⏸️' : '❌';
            const statusText = typeof status === 'string' ? status : (status ? 'Healthy' : 'Unavailable');
            
            return `
                <div class="status-item">
                    <label>${name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</label>
                    <span>${statusIcon} ${statusText}</span>
                </div>
            `;
        }).join('');
        
        healthContainer.innerHTML = healthItems;
    }
    
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('status-indicator');
        const text = document.getElementById('status-text');
        
        if (connected) {
            indicator.className = 'status-indicator connected';
            text.textContent = 'Connected';
        } else {
            indicator.className = 'status-indicator';
            text.textContent = 'Disconnected';
        }
    }
    
    updateStreamingControls(active) {
        const startBtn = document.getElementById('start-streaming');
        const stopBtn = document.getElementById('stop-streaming');
        
        startBtn.disabled = active;
        stopBtn.disabled = !active;
    }
    
    async startStreaming() {
        try {
            const success = await this.apiClient.startStreaming();
            if (success) {
                console.log('✅ Streaming started');
                this.updateStreamingControls(true);
            } else {
                this.showError('Failed to start streaming');
            }
        } catch (error) {
            this.showError('Error starting streaming: ' + error.message);
        }
    }
    
    async stopStreaming() {
        try {
            const success = await this.apiClient.stopStreaming();
            if (success) {
                console.log('⏹️ Streaming stopped');
                this.updateStreamingControls(false);
            } else {
                this.showError('Failed to stop streaming');
            }
        } catch (error) {
            this.showError('Error stopping streaming: ' + error.message);
        }
    }
    
    async forcePoll() {
        try {
            await this.apiClient.forcePoll();
            console.log('🔄 Forced memory poll completed');
            
            // Refresh current tab
            this.onTabChange(this.currentTab);
            
        } catch (error) {
            this.showError('Error forcing poll: ' + error.message);
        }
    }
    
    // Data update methods for specific tabs
    async updateMemoryData() {
        try {
            const analysis = await this.apiClient.getMemoryAnalysis();
            this.memoryVisualizer.updateData(analysis);
        } catch (error) {
            console.error('Failed to update memory data:', error);
        }
    }
    
    async updateManifoldData() {
        try {
            const analysis = await this.apiClient.getMemoryAnalysis();
            if (analysis && analysis.memory_analysis && analysis.memory_analysis.manifold) {
                this.manifoldAnalyzer.updateData(analysis.memory_analysis.manifold);
            }
        } catch (error) {
            console.error('Failed to update manifold data:', error);
        }
    }
    
    async updateDynamicsData() {
        try {
            const analysis = await this.apiClient.getMemoryAnalysis();
            if (analysis && analysis.memory_analysis && analysis.memory_analysis.dynamics) {
                this.dynamicsVisualizer.updateData(analysis.memory_analysis.dynamics);
            }
        } catch (error) {
            console.error('Failed to update dynamics data:', error);
        }
    }
    
    async updateCatastropheData() {
        try {
            const analysis = await this.apiClient.getMemoryAnalysis();
            if (analysis && analysis.memory_analysis && analysis.memory_analysis.catastrophe) {
                this.catastropheAnalyzer.updateData(analysis.memory_analysis.catastrophe);
            }
        } catch (error) {
            console.error('Failed to update catastrophe data:', error);
        }
    }
    
    async updateInsightsData() {
        try {
            const insights = await this.apiClient.getInsights();
            this.insightsManager.updateInsights(insights);
        } catch (error) {
            console.error('Failed to update insights data:', error);
        }
    }
    
    async updateStreamingData() {
        try {
            const stats = await this.apiClient.getStreamingStatistics();
            this.streamingManager.updateStatistics(stats);
        } catch (error) {
            console.error('Failed to update streaming data:', error);
        }
    }
    
    // Utility methods
    formatTime(date) {
        if (!date) return 'Unknown';
        
        if (typeof date === 'string') {
            date = new Date(date);
        }
        
        const now = new Date();
        const diffMs = now - date;
        const diffMinutes = Math.floor(diffMs / 60000);
        
        if (diffMinutes < 1) return 'Just now';
        if (diffMinutes < 60) return `${diffMinutes} min ago`;
        
        const diffHours = Math.floor(diffMinutes / 60);
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        
        return date.toLocaleDateString();
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = show ? 'flex' : 'none';
    }
    
    showError(message) {
        const modal = document.getElementById('error-modal');
        const messageEl = document.getElementById('error-message');
        
        messageEl.textContent = message;
        modal.style.display = 'block';
        
        console.error('Dashboard error:', message);
    }
    
    cleanup() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        // Cleanup all managers
        this.streamingManager?.cleanup();
        this.memoryVisualizer?.cleanup();
        this.manifoldAnalyzer?.cleanup();
        this.dynamicsVisualizer?.cleanup();
        this.catastropheAnalyzer?.cleanup();
        this.insightsManager?.cleanup();
        
        console.log('🧹 Dashboard cleanup completed');
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        window.noesisDashboard = new NoesisDashboard();
        await window.noesisDashboard.init();
    } catch (error) {
        console.error('Failed to initialize Noesis Dashboard:', error);
    }
});

export { NoesisDashboard };