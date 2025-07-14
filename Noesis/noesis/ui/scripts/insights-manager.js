/**
 * Insights Manager for Noesis Dashboard
 * Manages and displays theoretical insights with filtering and analysis
 */

class InsightsManager {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.insights = [];
        this.filteredInsights = [];
        this.charts = {};
        this.isInitialized = false;
        
        console.log('💡 Insights Manager initialized');
    }
    
    async init() {
        try {
            this.setupInsightsDisplay();
            this.setupInsightCharts();
            this.setupControls();
            this.isInitialized = true;
            console.log('✅ Insights Manager ready');
        } catch (error) {
            console.error('❌ Insights Manager initialization failed:', error);
            throw error;
        }
    }
    
    setupInsightsDisplay() {
        const container = document.getElementById('insights-container');
        if (!container) return;
        
        container.innerHTML = '<p class="text-muted">Loading insights...</p>';
    }
    
    setupInsightCharts() {
        this.setupInsightTrendsChart();
        this.setupConfidenceDistributionChart();
    }
    
    setupInsightTrendsChart() {
        const ctx = document.getElementById('insight-trends-chart');
        if (!ctx) return;
        
        this.charts.trends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Total Insights',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'High Confidence',
                        data: [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'New Insights',
                        data: [],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
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
                            text: 'Number of Insights'
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
                }
            }
        });
    }
    
    setupConfidenceDistributionChart() {
        const ctx = document.getElementById('confidence-distribution-chart');
        if (!ctx) return;
        
        this.charts.confidence = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['0.0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0'],
                datasets: [{
                    label: 'Number of Insights',
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.6)',   // Low confidence - red
                        'rgba(245, 158, 11, 0.6)',  // Medium-low - amber
                        'rgba(251, 191, 36, 0.6)',  // Medium - yellow
                        'rgba(34, 197, 94, 0.6)',   // Medium-high - green
                        'rgba(16, 185, 129, 0.6)'   // High confidence - emerald
                    ],
                    borderColor: [
                        '#ef4444',
                        '#f59e0b',
                        '#fbbf24',
                        '#22c55e',
                        '#10b981'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Count'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Confidence Range'
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
                                return `Insights: ${context.parsed.y}`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    setupControls() {
        const filterSelect = document.getElementById('insight-filter');
        const confidenceSelect = document.getElementById('confidence-filter');
        const refreshButton = document.getElementById('refresh-insights');
        
        if (filterSelect) {
            filterSelect.addEventListener('change', () => {
                this.applyFilters();
            });
        }
        
        if (confidenceSelect) {
            confidenceSelect.addEventListener('change', () => {
                this.applyFilters();
            });
        }
        
        if (refreshButton) {
            refreshButton.addEventListener('click', async () => {
                await this.refreshInsights();
            });
        }
    }
    
    async refreshInsights() {
        try {
            const insightsData = await this.apiClient.getInsights();
            this.updateInsights(insightsData);
            console.log('🔄 Insights refreshed');
        } catch (error) {
            console.error('Failed to refresh insights:', error);
        }
    }
    
    updateInsights(insightsData) {
        if (!this.isInitialized || !insightsData) return;
        
        this.insights = insightsData.insights || [];
        this.applyFilters();
        this.updateInsightTrends();
        this.updateConfidenceDistribution();
        
        console.log(`💡 Updated with ${this.insights.length} insights`);
    }
    
    applyFilters() {
        const typeFilter = document.getElementById('insight-filter')?.value || 'all';
        const confidenceFilter = document.getElementById('confidence-filter')?.value || 'all';
        
        this.filteredInsights = this.insights.filter(insight => {
            // Type filter
            if (typeFilter !== 'all' && insight.type !== typeFilter) {
                return false;
            }
            
            // Confidence filter
            const confidence = insight.confidence || 0;
            if (confidenceFilter === 'high' && confidence <= 0.8) {
                return false;
            }
            if (confidenceFilter === 'medium' && (confidence <= 0.5 || confidence > 0.8)) {
                return false;
            }
            if (confidenceFilter === 'low' && confidence > 0.5) {
                return false;
            }
            
            return true;
        });
        
        this.renderInsights();
    }
    
    renderInsights() {
        const container = document.getElementById('insights-container');
        if (!container) return;
        
        if (this.filteredInsights.length === 0) {
            container.innerHTML = '<p class="text-muted">No insights match the current filters</p>';
            return;
        }
        
        const html = this.filteredInsights.map(insight => this.renderInsightCard(insight)).join('');
        container.innerHTML = html;
    }
    
    renderInsightCard(insight) {
        const confidencePercent = Math.round((insight.confidence || 0) * 100);
        const confidenceClass = this.getConfidenceClass(insight.confidence);
        const typeIcon = this.getTypeIcon(insight.type);
        const timestamp = insight.timestamp ? this.formatTimestamp(insight.timestamp) : 'Unknown time';
        
        return `
            <div class="insight-card ${confidenceClass}">
                <div class="insight-header">
                    <div class="insight-type">
                        ${typeIcon} ${this.formatType(insight.type)}
                    </div>
                    <div class="insight-confidence">
                        ${confidencePercent}%
                    </div>
                </div>
                <div class="insight-content">
                    <p class="insight-text">${insight.insight}</p>
                    ${insight.implications ? this.renderImplications(insight.implications) : ''}
                </div>
                <div class="insight-footer">
                    <span class="insight-timestamp">${timestamp}</span>
                    ${insight.evidence ? `<span class="insight-evidence">Evidence: ${insight.evidence}</span>` : ''}
                </div>
            </div>
        `;
    }
    
    renderImplications(implications) {
        if (!Array.isArray(implications) || implications.length === 0) {
            return '';
        }
        
        const listItems = implications.map(impl => `<li>${impl}</li>`).join('');
        return `
            <div class="insight-implications">
                <strong>Implications:</strong>
                <ul>${listItems}</ul>
            </div>
        `;
    }
    
    getConfidenceClass(confidence) {
        if (confidence >= 0.8) return 'high-confidence';
        if (confidence >= 0.6) return 'medium-high-confidence';
        if (confidence >= 0.4) return 'medium-confidence';
        if (confidence >= 0.2) return 'low-medium-confidence';
        return 'low-confidence';
    }
    
    getTypeIcon(type) {
        const icons = {
            'manifold_dimensionality': '🌐',
            'manifold_curvature': '🌊',
            'dynamics_instability': '⚡',
            'multiple_attractors': '🎯',
            'phase_transitions': '🔄',
            'bifurcations': '🔱',
            'high_activity': '🔥',
            'dominant_event_pattern': '📊',
            'memory_activity': '🧠',
            'memory_pressure': '⚠️',
            'performance_concern': '🚨',
            'pattern_detection': '🔍',
            'emergence_detection': '✨'
        };
        
        return icons[type] || '💡';
    }
    
    formatType(type) {
        return type
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }
    
    formatTimestamp(timestamp) {
        if (!timestamp) return 'Unknown time';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMinutes = Math.floor(diffMs / 60000);
        
        if (diffMinutes < 1) return 'Just now';
        if (diffMinutes < 60) return `${diffMinutes} min ago`;
        
        const diffHours = Math.floor(diffMinutes / 60);
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        
        return date.toLocaleDateString();
    }
    
    updateInsightTrends() {
        if (!this.charts.trends) return;
        
        // Group insights by time intervals
        const timeGroups = this.groupInsightsByTime();
        
        const labels = Object.keys(timeGroups).sort().map(time => new Date(time));
        const totalCounts = labels.map(time => {
            const group = timeGroups[time.toISOString()];
            return group ? group.length : 0;
        });
        const highConfidenceCounts = labels.map(time => {
            const group = timeGroups[time.toISOString()];
            return group ? group.filter(i => i.confidence >= 0.8).length : 0;
        });
        const newInsightsCounts = labels.map(time => {
            const group = timeGroups[time.toISOString()];
            return group ? group.filter(i => this.isNewInsight(i, time)).length : 0;
        });
        
        this.charts.trends.data.labels = labels;
        this.charts.trends.data.datasets[0].data = totalCounts;
        this.charts.trends.data.datasets[1].data = highConfidenceCounts;
        this.charts.trends.data.datasets[2].data = newInsightsCounts;
        
        this.charts.trends.update('none');
    }
    
    groupInsightsByTime() {
        const groups = {};
        const interval = 5 * 60 * 1000; // 5 minute intervals
        
        this.insights.forEach(insight => {
            const timestamp = new Date(insight.timestamp || Date.now());
            const roundedTime = new Date(Math.floor(timestamp.getTime() / interval) * interval);
            const key = roundedTime.toISOString();
            
            if (!groups[key]) {
                groups[key] = [];
            }
            groups[key].push(insight);
        });
        
        return groups;
    }
    
    isNewInsight(insight, timeWindow) {
        // Define "new" as insights that appeared in this time window
        // This is a simplified implementation
        const insightTime = new Date(insight.timestamp || Date.now());
        const windowStart = new Date(timeWindow.getTime() - 5 * 60 * 1000); // 5 minutes ago
        
        return insightTime >= windowStart && insightTime <= timeWindow;
    }
    
    updateConfidenceDistribution() {
        if (!this.charts.confidence) return;
        
        const buckets = [0, 0, 0, 0, 0]; // 5 confidence ranges
        
        this.insights.forEach(insight => {
            const confidence = insight.confidence || 0;
            const bucketIndex = Math.min(Math.floor(confidence * 5), 4);
            buckets[bucketIndex]++;
        });
        
        this.charts.confidence.data.datasets[0].data = buckets;
        this.charts.confidence.update('none');
    }
    
    getInsightStatistics() {
        if (this.insights.length === 0) {
            return {
                total: 0,
                byType: {},
                byConfidence: {},
                averageConfidence: 0,
                recentCount: 0
            };
        }
        
        const stats = {
            total: this.insights.length,
            byType: {},
            byConfidence: {
                high: 0,
                medium: 0,
                low: 0
            },
            averageConfidence: 0,
            recentCount: 0
        };
        
        let totalConfidence = 0;
        const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
        
        this.insights.forEach(insight => {
            // Type distribution
            stats.byType[insight.type] = (stats.byType[insight.type] || 0) + 1;
            
            // Confidence distribution
            const confidence = insight.confidence || 0;
            totalConfidence += confidence;
            
            if (confidence >= 0.7) {
                stats.byConfidence.high++;
            } else if (confidence >= 0.4) {
                stats.byConfidence.medium++;
            } else {
                stats.byConfidence.low++;
            }
            
            // Recent insights
            const insightTime = new Date(insight.timestamp || Date.now());
            if (insightTime > oneHourAgo) {
                stats.recentCount++;
            }
        });
        
        stats.averageConfidence = totalConfidence / this.insights.length;
        
        return stats;
    }
    
    exportInsights() {
        const data = {
            exportTime: new Date().toISOString(),
            totalInsights: this.insights.length,
            insights: this.insights,
            statistics: this.getInsightStatistics()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `noesis-insights-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
        
        console.log('📄 Insights exported');
    }
    
    refresh() {
        if (!this.isInitialized) return;
        
        this.applyFilters();
        this.updateInsightTrends();
        this.updateConfidenceDistribution();
        
        console.log('🔄 Insights display refreshed');
    }
    
    cleanup() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        this.charts = {};
        this.insights = [];
        this.filteredInsights = [];
        this.isInitialized = false;
        
        console.log('🧹 Insights Manager cleanup completed');
    }
}

export { InsightsManager };