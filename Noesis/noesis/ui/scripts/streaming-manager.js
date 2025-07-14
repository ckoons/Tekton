/**
 * Streaming Manager for Noesis Dashboard
 * Handles real-time data streaming visualization and live event feeds
 */

class StreamingManager extends EventTarget {
    constructor(apiClient) {
        super();
        this.apiClient = apiClient;
        this.isInitialized = false;
        this.charts = {};
        this.eventBuffer = [];
        this.maxEvents = 100;
        this.isPaused = false;
        this.autoScroll = true;
        this.statisticsUpdateInterval = null;
        
        console.log('🔴 Streaming Manager initialized');
    }
    
    async init() {
        try {
            this.setupEventFeed();
            this.setupLiveMetricsChart();
            this.setupStreamStatistics();
            this.setupControls();
            this.startStatisticsUpdates();
            this.isInitialized = true;
            console.log('✅ Streaming Manager ready');
        } catch (error) {
            console.error('❌ Streaming Manager initialization failed:', error);
            throw error;
        }
    }
    
    setupEventFeed() {
        const container = document.getElementById('live-events');
        if (!container) return;
        
        container.innerHTML = '<p class="text-muted">Waiting for live events...</p>';
        container.scrollTop = container.scrollHeight;
    }
    
    setupLiveMetricsChart() {
        const ctx = document.getElementById('live-metrics-chart');
        if (!ctx) return;
        
        this.charts.liveMetrics = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Event Rate (events/min)',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        yAxisID: 'y',
                        tension: 0.4
                    },
                    {
                        label: 'Memory Observations',
                        data: [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        yAxisID: 'y1',
                        tension: 0.4
                    },
                    {
                        label: 'Analysis Latency (ms)',
                        data: [],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        yAxisID: 'y2',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 200
                },
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
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Event Rate'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Observations'
                        },
                        grid: {
                            drawOnChartArea: false,
                        }
                    },
                    y2: {
                        type: 'linear',
                        display: false
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
                        radius: 2,
                        hoverRadius: 4
                    }
                }
            }
        });
    }
    
    setupStreamStatistics() {
        this.updateStatisticsDisplay({
            event_rate: 0,
            data_rate: 0,
            analysis_latency: 0,
            memory_usage: 0
        });
    }
    
    setupControls() {
        const pauseBtn = document.getElementById('pause-events');
        const clearBtn = document.getElementById('clear-events');
        const autoScrollCheckbox = document.getElementById('auto-scroll');
        
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => {
                this.togglePause();
            });
        }
        
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearEvents();
            });
        }
        
        if (autoScrollCheckbox) {
            autoScrollCheckbox.addEventListener('change', (e) => {
                this.autoScroll = e.target.checked;
            });
        }
    }
    
    startStatisticsUpdates() {
        // Update statistics every 2 seconds
        this.statisticsUpdateInterval = setInterval(async () => {
            await this.updateStreamingStatistics();
        }, 2000);
    }
    
    async updateStreamingStatistics() {
        if (!this.isInitialized) return;
        
        try {
            const stats = await this.apiClient.getStreamingStatistics();
            this.updateStatistics(stats);
        } catch (error) {
            console.error('Failed to update streaming statistics:', error);
        }
    }
    
    updateStatistics(stats) {
        if (!stats) return;
        
        // Update live metrics chart
        this.updateLiveMetricsChart(stats);
        
        // Update statistics display
        this.updateStatisticsDisplay(stats);
        
        // Simulate new events based on statistics
        this.simulateEvents(stats);
    }
    
    updateLiveMetricsChart(stats) {
        if (!this.charts.liveMetrics) return;
        
        const now = new Date();
        const chart = this.charts.liveMetrics;
        
        // Extract metrics
        const eventRate = stats.memory_statistics?.event_rate || 0;
        const observations = stats.memory_statistics?.total_observations || 0;
        const latency = Math.random() * 100; // Simulated latency
        
        // Add new data point
        chart.data.labels.push(now);
        chart.data.datasets[0].data.push(eventRate);
        chart.data.datasets[1].data.push(observations);
        chart.data.datasets[2].data.push(latency);
        
        // Keep only last 20 points for performance
        const maxPoints = 20;
        if (chart.data.labels.length > maxPoints) {
            chart.data.labels.shift();
            chart.data.datasets.forEach(dataset => dataset.data.shift());
        }
        
        chart.update('none');
    }
    
    updateStatisticsDisplay(stats) {
        const eventRateEl = document.getElementById('event-rate');
        const dataRateEl = document.getElementById('data-rate');
        const latencyEl = document.getElementById('analysis-latency');
        const memoryEl = document.getElementById('memory-usage');
        
        if (eventRateEl) {
            const rate = stats.memory_statistics?.event_rate || 0;
            eventRateEl.textContent = `${rate.toFixed(1)} events/min`;
        }
        
        if (dataRateEl) {
            // Simulate data rate based on event rate
            const rate = stats.memory_statistics?.event_rate || 0;
            const dataRate = rate * 0.5; // Approximate KB/s
            dataRateEl.textContent = `${dataRate.toFixed(1)} KB/s`;
        }
        
        if (latencyEl) {
            // Simulate analysis latency
            const latency = Math.random() * 50 + 10; // 10-60ms
            latencyEl.textContent = `${latency.toFixed(0)} ms`;
        }
        
        if (memoryEl) {
            // Simulate memory usage
            const observations = stats.memory_statistics?.total_observations || 0;
            const memUsage = Math.min(observations * 0.1, 100); // MB
            memoryEl.textContent = `${memUsage.toFixed(1)} MB`;
        }
    }
    
    simulateEvents(stats) {
        if (this.isPaused) return;
        
        const eventRate = stats.memory_statistics?.event_rate || 0;
        
        // Probability of generating an event this update cycle
        const eventProbability = eventRate / 30; // events per 2-second interval
        
        if (Math.random() < eventProbability) {
            this.generateSyntheticEvent(stats);
        }
    }
    
    generateSyntheticEvent(stats) {
        const eventTypes = [
            'thought_created',
            'thought_refined', 
            'state_transition',
            'memory_update',
            'analysis_completed',
            'pattern_detected',
            'insight_generated'
        ];
        
        const event = {
            type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
            timestamp: new Date().toISOString(),
            data: this.generateEventData(),
            source: 'engram_stream'
        };
        
        this.addEvent(event);
    }
    
    generateEventData() {
        const thoughtStates = ['initial', 'refining', 'finalized', 'paused'];
        const components = ['collective_intelligence', 'memory_analyzer', 'pattern_detector'];
        
        return {
            thought_id: `thought_${Math.floor(Math.random() * 1000)}`,
            component: components[Math.floor(Math.random() * components.length)],
            state: thoughtStates[Math.floor(Math.random() * thoughtStates.length)],
            confidence: Math.random(),
            metadata: {
                iteration: Math.floor(Math.random() * 10) + 1,
                complexity: Math.random()
            }
        };
    }
    
    addEvent(event) {
        if (this.isPaused) return;
        
        this.eventBuffer.push(event);
        
        // Limit buffer size
        if (this.eventBuffer.length > this.maxEvents) {
            this.eventBuffer.shift();
        }
        
        this.renderEvents();
        
        // Dispatch event for other components
        this.dispatchEvent(new CustomEvent('newEvent', { detail: event }));
    }
    
    renderEvents() {
        const container = document.getElementById('live-events');
        if (!container) return;
        
        if (this.eventBuffer.length === 0) {
            container.innerHTML = '<p class="text-muted">No events received yet</p>';
            return;
        }
        
        const html = this.eventBuffer
            .slice(-50) // Show last 50 events
            .reverse() // Most recent first
            .map(event => this.renderEventItem(event))
            .join('');
        
        container.innerHTML = html;
        
        // Auto-scroll to bottom if enabled
        if (this.autoScroll) {
            container.scrollTop = container.scrollHeight;
        }
    }
    
    renderEventItem(event) {
        const timestamp = this.formatEventTime(event.timestamp);
        const icon = this.getEventIcon(event.type);
        const description = this.getEventDescription(event);
        
        return `
            <div class="event-item ${event.type}">
                <div class="event-icon">${icon}</div>
                <div class="event-content">
                    <div class="event-header">
                        <span class="event-type">${this.formatEventType(event.type)}</span>
                        <span class="event-time">${timestamp}</span>
                    </div>
                    <div class="event-description">${description}</div>
                    ${event.data ? this.renderEventData(event.data) : ''}
                </div>
            </div>
        `;
    }
    
    getEventIcon(type) {
        const icons = {
            'thought_created': '💭',
            'thought_refined': '🔄',
            'state_transition': '⚡',
            'memory_update': '🧠',
            'analysis_completed': '📊',
            'pattern_detected': '🔍',
            'insight_generated': '💡'
        };
        
        return icons[type] || '📡';
    }
    
    formatEventType(type) {
        return type
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }
    
    getEventDescription(event) {
        const descriptions = {
            'thought_created': 'New thought initialized in memory space',
            'thought_refined': 'Thought underwent refinement iteration',
            'state_transition': 'Thought state changed',
            'memory_update': 'Memory state updated with new information',
            'analysis_completed': 'Theoretical analysis completed',
            'pattern_detected': 'New pattern identified in data',
            'insight_generated': 'Theoretical insight generated'
        };
        
        return descriptions[event.type] || 'Stream event occurred';
    }
    
    renderEventData(data) {
        if (!data || typeof data !== 'object') return '';
        
        const keyValues = Object.entries(data)
            .filter(([key, value]) => typeof value !== 'object')
            .map(([key, value]) => `${key}: ${value}`)
            .slice(0, 3) // Limit to first 3 properties
            .join(', ');
        
        return keyValues ? `<div class="event-data">${keyValues}</div>` : '';
    }
    
    formatEventTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffSeconds = Math.floor(diffMs / 1000);
        
        if (diffSeconds < 5) return 'Just now';
        if (diffSeconds < 60) return `${diffSeconds}s ago`;
        
        const diffMinutes = Math.floor(diffSeconds / 60);
        if (diffMinutes < 60) return `${diffMinutes}m ago`;
        
        return date.toLocaleTimeString();
    }
    
    togglePause() {
        this.isPaused = !this.isPaused;
        
        const button = document.getElementById('pause-events');
        if (button) {
            button.textContent = this.isPaused ? 'Resume' : 'Pause';
            button.className = this.isPaused ? 'btn btn-primary' : 'btn btn-secondary';
        }
        
        console.log(`📡 Event stream ${this.isPaused ? 'paused' : 'resumed'}`);
    }
    
    clearEvents() {
        this.eventBuffer = [];
        this.renderEvents();
        
        console.log('🧹 Event buffer cleared');
    }
    
    // Public API for external event injection
    injectEvent(event) {
        this.addEvent({
            ...event,
            timestamp: event.timestamp || new Date().toISOString(),
            source: event.source || 'external'
        });
    }
    
    // Get streaming insights
    getStreamingInsights() {
        if (this.eventBuffer.length === 0) return [];
        
        const insights = [];
        
        // Analyze event patterns
        const recentEvents = this.eventBuffer.slice(-20);
        const eventTypes = recentEvents.map(e => e.type);
        const typeFrequency = {};
        
        eventTypes.forEach(type => {
            typeFrequency[type] = (typeFrequency[type] || 0) + 1;
        });
        
        // Detect high activity
        if (recentEvents.length > 15) {
            insights.push({
                type: 'high_streaming_activity',
                message: 'High real-time activity detected in memory stream',
                confidence: 0.8,
                timestamp: new Date().toISOString()
            });
        }
        
        // Detect dominant patterns
        const dominantType = Object.entries(typeFrequency)
            .sort(([,a], [,b]) => b - a)[0];
        
        if (dominantType && dominantType[1] > recentEvents.length * 0.4) {
            insights.push({
                type: 'dominant_stream_pattern',
                message: `Dominant streaming pattern: ${this.formatEventType(dominantType[0])}`,
                confidence: 0.7,
                timestamp: new Date().toISOString()
            });
        }
        
        return insights;
    }
    
    refresh() {
        if (!this.isInitialized) return;
        
        this.renderEvents();
        
        if (this.charts.liveMetrics) {
            this.charts.liveMetrics.update();
        }
        
        console.log('🔄 Streaming display refreshed');
    }
    
    cleanup() {
        if (this.statisticsUpdateInterval) {
            clearInterval(this.statisticsUpdateInterval);
            this.statisticsUpdateInterval = null;
        }
        
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        this.charts = {};
        this.eventBuffer = [];
        this.isInitialized = false;
        
        console.log('🧹 Streaming Manager cleanup completed');
    }
}

export { StreamingManager };