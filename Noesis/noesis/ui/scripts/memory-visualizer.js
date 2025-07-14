/**
 * Memory Visualizer for Noesis Dashboard
 * Creates visualizations for memory states, thought distributions, and memory metrics
 * Uses shared TektonViz visualization framework
 */

class MemoryVisualizer {
    constructor() {
        this.charts = {};
        this.data = null;
        this.isInitialized = false;
        
        // Initialize shared visualization components
        this.tektonViz = new TektonViz('chartjs');
        this.canvasViz = new TektonViz('canvas');
        
        console.log('🧠 Memory Visualizer initialized with TektonViz');
    }
    
    async init() {
        try {
            // Initialize TektonViz components
            await this.tektonViz.init('memory-charts-container');
            await this.canvasViz.init('memory-canvas-container');
            
            this.setupCharts();
            this.isInitialized = true;
            console.log('✅ Memory Visualizer ready with TektonViz');
        } catch (error) {
            console.error('❌ Memory Visualizer initialization failed:', error);
            throw error;
        }
    }
    
    setupCharts() {
        // Memory Timeline Chart
        this.setupMemoryTimelineChart();
        
        // Thought States Chart
        this.setupThoughtStatesChart();
        
        // Memory Metrics Chart
        this.setupMemoryMetricsChart();
        
        // Attention Chart
        this.setupAttentionChart();
    }
    
    setupMemoryTimelineChart() {
        const ctx = document.getElementById('memory-timeline-chart');
        if (!ctx) return;
        
        this.charts.memoryTimeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Total Thoughts',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Active Thoughts',
                        data: [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Finalized Thoughts',
                        data: [],
                        borderColor: '#7c3aed',
                        backgroundColor: 'rgba(124, 58, 237, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Thoughts'
                        }
                    },
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
                    }
                },
                plugins: {
                    legend: {
                        display: true
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                elements: {
                    point: {
                        radius: 3,
                        hoverRadius: 6
                    }
                }
            }
        });
    }
    
    setupThoughtStatesChart() {
        const ctx = document.getElementById('thought-states-chart');
        if (!ctx) return;
        
        this.charts.thoughtStates = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Initial', 'Refining', 'Finalized', 'Paused', 'Abandoned', 'Rejected'],
                datasets: [{
                    data: [0, 0, 0, 0, 0, 0],
                    backgroundColor: [
                        '#3b82f6',  // blue - initial
                        '#f59e0b',  // amber - refining
                        '#10b981',  // emerald - finalized
                        '#6b7280',  // gray - paused
                        '#ef4444',  // red - abandoned
                        '#7c2d12'   // dark red - rejected
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    setupMemoryMetricsChart() {
        const ctx = document.getElementById('memory-metrics-chart');
        if (!ctx) return;
        
        this.charts.memoryMetrics = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Utilization', 'Compression', 'Efficiency', 'Latency', 'Activity', 'Stability'],
                datasets: [{
                    label: 'Memory Performance',
                    data: [0, 0, 0, 0, 0, 0],
                    borderColor: '#7c3aed',
                    backgroundColor: 'rgba(124, 58, 237, 0.2)',
                    pointBackgroundColor: '#7c3aed',
                    pointBorderColor: '#ffffff',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 1,
                        ticks: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = (context.parsed.r * 100).toFixed(1);
                                return `${label}: ${value}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    setupAttentionChart() {
        const ctx = document.getElementById('attention-chart');
        if (!ctx) return;
        
        this.charts.attention = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Attention Weight',
                    data: [],
                    backgroundColor: 'rgba(59, 130, 246, 0.6)',
                    borderColor: '#3b82f6',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        title: {
                            display: true,
                            text: 'Attention Weight'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Attention Dimension'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = (context.parsed.y * 100).toFixed(2);
                                return `Weight: ${value}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    updateData(analysisData) {
        if (!this.isInitialized || !analysisData) return;
        
        this.data = analysisData;
        
        try {
            this.updateMemoryTimeline();
            this.updateThoughtStatesDistribution();
            this.updateMemoryMetrics();
            this.updateAttentionVisualization();
            
            console.log('📊 Memory visualizations updated');
        } catch (error) {
            console.error('Failed to update memory visualizations:', error);
        }
    }
    
    updateMemoryTimeline() {
        if (!this.charts.memoryTimeline || !this.data.recent_memory_history) return;
        
        const history = this.data.recent_memory_history.slice(-20); // Last 20 points
        
        const labels = history.map(state => new Date(state.timestamp));
        const totalThoughts = history.map(state => Object.keys(state.thought_states || {}).length);
        const activeThoughts = history.map(state => {
            const states = Object.values(state.thought_states || {});
            return states.filter(s => ['initial', 'refining'].includes(s)).length;
        });
        const finalizedThoughts = history.map(state => {
            const states = Object.values(state.thought_states || {});
            return states.filter(s => s === 'finalized').length;
        });
        
        this.charts.memoryTimeline.data.labels = labels;
        this.charts.memoryTimeline.data.datasets[0].data = totalThoughts;
        this.charts.memoryTimeline.data.datasets[1].data = activeThoughts;
        this.charts.memoryTimeline.data.datasets[2].data = finalizedThoughts;
        
        this.charts.memoryTimeline.update('none');
    }
    
    updateThoughtStatesDistribution() {
        if (!this.charts.thoughtStates || !this.data.current_memory_state) return;
        
        const thoughtStates = this.data.current_memory_state.thought_states || {};
        const states = Object.values(thoughtStates);
        
        const stateCounts = {
            initial: states.filter(s => s === 'initial').length,
            refining: states.filter(s => s === 'refining').length,
            finalized: states.filter(s => s === 'finalized').length,
            paused: states.filter(s => s === 'paused').length,
            abandoned: states.filter(s => s === 'abandoned').length,
            rejected: states.filter(s => s === 'rejected').length
        };
        
        this.charts.thoughtStates.data.datasets[0].data = [
            stateCounts.initial,
            stateCounts.refining,
            stateCounts.finalized,
            stateCounts.paused,
            stateCounts.abandoned,
            stateCounts.rejected
        ];
        
        this.charts.thoughtStates.update('none');
    }
    
    updateMemoryMetrics() {
        if (!this.charts.memoryMetrics || !this.data.current_memory_state) return;
        
        const metrics = this.data.current_memory_state.memory_metrics || {};
        const activityLevels = this.data.current_memory_state.activity_levels || {};
        
        // Normalize metrics to 0-1 scale for radar chart
        const normalizedMetrics = [
            Math.min(metrics.memory_utilization || 0, 1),
            Math.min(metrics.compression_ratio || 0, 1),
            Math.min(metrics.storage_efficiency || 0, 1),
            1 - Math.min(metrics.retrieval_latency || 0, 1), // Invert latency (lower is better)
            Math.min((activityLevels.thought_creation_rate || 0) / 10, 1), // Scale activity
            Math.min(1 - (activityLevels.memory_churn || 0), 1) // Invert churn (lower is better)
        ];
        
        this.charts.memoryMetrics.data.datasets[0].data = normalizedMetrics;
        this.charts.memoryMetrics.update('none');
    }
    
    updateAttentionVisualization() {
        if (!this.charts.attention || !this.data.current_memory_state) return;
        
        const attentionWeights = this.data.current_memory_state.attention_weights || [];
        
        if (attentionWeights.length === 0) return;
        
        // Show top 20 attention dimensions for clarity
        const topWeights = attentionWeights
            .map((weight, index) => ({ weight, index }))
            .sort((a, b) => b.weight - a.weight)
            .slice(0, 20);
        
        const labels = topWeights.map(item => `Dim ${item.index + 1}`);
        const data = topWeights.map(item => item.weight);
        
        this.charts.attention.data.labels = labels;
        this.charts.attention.data.datasets[0].data = data;
        
        this.charts.attention.update('none');
    }
    
    refresh() {
        if (!this.isInitialized) return;
        
        // Refresh all charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.update === 'function') {
                chart.update();
            }
        });
        
        console.log('🔄 Memory visualizations refreshed');
    }
    
    resize() {
        if (!this.isInitialized) return;
        
        // Resize all charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    }
    
    // Helper methods for data processing
    processMemoryHistory(history) {
        if (!Array.isArray(history)) return [];
        
        return history.map(state => ({
            timestamp: new Date(state.timestamp),
            totalThoughts: Object.keys(state.thought_states || {}).length,
            thoughtStates: this.categorizeThoughtStates(state.thought_states || {}),
            memoryMetrics: state.memory_metrics || {},
            activityLevels: state.activity_levels || {},
            attentionWeights: state.attention_weights || []
        }));
    }
    
    categorizeThoughtStates(thoughtStates) {
        const categories = {
            active: 0,
            completed: 0,
            paused: 0,
            failed: 0
        };
        
        Object.values(thoughtStates).forEach(state => {
            switch (state) {
                case 'initial':
                case 'refining':
                case 'reconsidering':
                    categories.active++;
                    break;
                case 'finalized':
                case 'merged':
                    categories.completed++;
                    break;
                case 'paused':
                case 'abandoned':
                    categories.paused++;
                    break;
                case 'rejected':
                case 'superseded':
                    categories.failed++;
                    break;
            }
        });
        
        return categories;
    }
    
    getInsights() {
        if (!this.data) return [];
        
        const insights = [];
        
        // Analyze thought state distribution
        if (this.data.current_memory_state && this.data.current_memory_state.thought_states) {
            const states = Object.values(this.data.current_memory_state.thought_states);
            const activeRatio = states.filter(s => ['initial', 'refining'].includes(s)).length / states.length;
            
            if (activeRatio > 0.7) {
                insights.push({
                    type: 'memory_activity',
                    message: 'High cognitive activity detected - many thoughts in active processing',
                    confidence: 0.8
                });
            }
        }
        
        // Analyze memory metrics
        if (this.data.current_memory_state && this.data.current_memory_state.memory_metrics) {
            const metrics = this.data.current_memory_state.memory_metrics;
            
            if (metrics.memory_utilization > 0.8) {
                insights.push({
                    type: 'memory_pressure',
                    message: 'High memory utilization - system may be at capacity',
                    confidence: 0.9
                });
            }
            
            if (metrics.retrieval_latency > 0.1) {
                insights.push({
                    type: 'performance_concern',
                    message: 'High retrieval latency detected - memory access may be slowing',
                    confidence: 0.7
                });
            }
        }
        
        return insights;
    }
    
    cleanup() {
        // Destroy all charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        this.charts = {};
        this.data = null;
        this.isInitialized = false;
        
        console.log('🧹 Memory Visualizer cleanup completed');
    }
}

export { MemoryVisualizer };