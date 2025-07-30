/**
 * Noesis Real-time Streaming Integration
 * Minimal JavaScript for WebSocket connections and live updates
 */

class NoesisStreaming {
    constructor() {
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        this.isConnected = false;
        
        this.initialize();
    }
    
    initialize() {
        this.setupEventListeners();
        this.connectWebSocket();
        console.log('[NoesisStreaming] Streaming system initialized');
    }
    
    setupEventListeners() {
        // Listen for manual stream control
        document.addEventListener('noesis-start-stream', () => this.startStream());
        document.addEventListener('noesis-stop-stream', () => this.stopStream());
        document.addEventListener('noesis-pause-stream', () => this.pauseStream());
    }
    
    connectWebSocket() {
        try {
            const wsUrl = noesisUrl('').replace('http', 'ws') + '/ws/analysis';
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus('connected');
                console.log('[NoesisStreaming] WebSocket connected');
            };
            
            this.websocket.onmessage = (event) => {
                this.handleStreamingMessage(JSON.parse(event.data));
            };
            
            this.websocket.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                this.attemptReconnect();
            };
            
            this.websocket.onerror = (error) => {
                console.error('[NoesisStreaming] WebSocket error:', error);
                this.updateConnectionStatus('error');
            };
            
        } catch (error) {
            console.error('[NoesisStreaming] Failed to connect WebSocket:', error);
            this.updateConnectionStatus('error');
        }
    }
    
    handleStreamingMessage(data) {
        switch (data.type) {
            case 'manifold_update':
                this.updateManifoldData(data.analysis);
                break;
            case 'pattern_detected':
                document.dispatchEvent(new CustomEvent('noesis-pattern-detected', {
                    detail: data.pattern
                }));
                break;
            case 'regime_transition':
                this.updateRegimeDisplay(data.regime);
                break;
            case 'memory_stream':
                this.updateMemoryStream(data.memory);
                break;
            case 'metrics_update':
                this.updateMetrics(data.metrics);
                break;
            default:
                console.log('[NoesisStreaming] Unknown message type:', data.type);
        }
    }
    
    updateConnectionStatus(status) {
        // Update status indicator using CSS classes
        const statusElement = document.getElementById('stream-status-indicator');
        if (statusElement) {
            statusElement.textContent = this.getStatusText(status);
            statusElement.setAttribute('data-tekton-state', status);
        }
    }
    
    getStatusText(status) {
        const statusTexts = {
            'connecting': 'Connecting...',
            'connected': 'Live Stream Active',
            'disconnected': 'Disconnected',
            'error': 'Connection Error',
            'paused': 'Stream Paused'
        };
        return statusTexts[status] || 'Unknown';
    }
    
    updateManifoldData(analysis) {
        // Update manifold viewer if available
        if (window.noesisManifoldViewer) {
            window.noesisManifoldViewer.updateManifold(analysis);
        }
        
        // Update manifold properties using innerHTML injection
        this.updateProperty('intrinsic-dimension', analysis.intrinsic_dimension);
        this.updateProperty('manifold-curvature', analysis.curvature);
        this.updateProperty('topology-class', analysis.topology);
        this.updateProperty('manifold-stability', analysis.stability);
    }
    
    updateRegimeDisplay(regime) {
        // Update regime list using innerHTML injection
        const regimeList = document.getElementById('regime-list');
        if (regimeList) {
            const regimeHTML = `
                <div class="noesis__regime-item noesis__regime-item--${regime.type}">
                    <div class="noesis__regime-name">${regime.name}</div>
                    <div class="noesis__regime-confidence">${(regime.confidence * 100).toFixed(1)}%</div>
                    <div class="noesis__regime-duration">${regime.duration}s</div>
                </div>
            `;
            regimeList.insertAdjacentHTML('afterbegin', regimeHTML);
            
            // Keep only recent regimes
            while (regimeList.children.length > 10) {
                regimeList.removeChild(regimeList.lastElementChild);
            }
        }
    }
    
    updateMemoryStream(memory) {
        // Update memory metrics
        this.updateMetric('active-memories-count', memory.active_count);
        this.updateMetric('pattern-strength-value', memory.pattern_strength);
        this.updateMetric('coherence-score-value', memory.coherence_score);
        
        // Update memory visualization if canvas exists
        this.updateMemoryVisualization(memory);
    }
    
    updateMemoryVisualization(memory) {
        const canvas = document.querySelector('#memory-stream-visualization canvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        
        // Simple streaming visualization
        canvas.width = canvas.clientWidth;
        canvas.height = canvas.clientHeight;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#FF6F00';
        
        // Draw simple bars representing memory activity
        if (memory.activity_levels && memory.activity_levels.length > 0) {
            const barWidth = canvas.width / memory.activity_levels.length;
            memory.activity_levels.forEach((level, index) => {
                const barHeight = (level / 100) * (canvas.height - 20);
                ctx.fillRect(index * barWidth, canvas.height - barHeight - 10, barWidth - 2, barHeight);
            });
        }
    }
    
    updateMetrics(metrics) {
        // Update all metrics using helper function
        Object.entries(metrics).forEach(([key, value]) => {
            this.updateMetric(key.replace(/_/g, '-'), value);
        });
    }
    
    updateProperty(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            const formattedValue = this.formatValue(value);
            element.textContent = formattedValue;
            element.setAttribute('data-updated', 'true');
            
            // Remove update indicator after animation
            setTimeout(() => {
                element.removeAttribute('data-updated');
            }, 1000);
        }
    }
    
    updateMetric(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            const formattedValue = this.formatValue(value);
            element.textContent = formattedValue;
            element.setAttribute('data-tekton-metric-updated', 'true');
            
            // Remove update indicator after animation
            setTimeout(() => {
                element.removeAttribute('data-tekton-metric-updated');
            }, 500);
        }
    }
    
    formatValue(value) {
        if (value === null || value === undefined) return '--';
        if (typeof value === 'number') {
            if (value < 0.01 && value > 0) return value.toExponential(2);
            if (value > 1000) return value.toLocaleString();
            return value.toFixed(3).replace(/\.?0+$/, '');
        }
        return String(value);
    }
    
    startStream() {
        if (!this.isConnected) {
            this.connectWebSocket();
            return;
        }
        
        // Send start command to backend
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'start_streaming',
                timestamp: Date.now()
            }));
        }
        
        fetch(noesisUrl('/api/streaming/start'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        }).catch(error => {
            console.error('[NoesisStreaming] Failed to start stream:', error);
        });
    }
    
    stopStream() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'stop_streaming',
                timestamp: Date.now()
            }));
        }
        
        fetch(noesisUrl('/api/streaming/stop'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        }).catch(error => {
            console.error('[NoesisStreaming] Failed to stop stream:', error);
        });
    }
    
    pauseStream() {
        this.updateConnectionStatus('paused');
        
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: 'pause_streaming',
                timestamp: Date.now()
            }));
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('[NoesisStreaming] Max reconnection attempts reached');
            return;
        }
        
        this.reconnectAttempts++;
        this.updateConnectionStatus('connecting');
        
        setTimeout(() => {
            console.log(`[NoesisStreaming] Reconnection attempt ${this.reconnectAttempts}`);
            this.connectWebSocket();
        }, this.reconnectDelay * this.reconnectAttempts);
    }
    
    destroy() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        this.isConnected = false;
        console.log('[NoesisStreaming] Streaming destroyed');
    }
}

// Initialize global streaming system
window.noesisStreaming = new NoesisStreaming();

// Stream control functions for UI buttons
window.noesis_startStream = () => {
    window.noesisStreaming.startStream();
};

window.noesis_stopStream = () => {
    window.noesisStreaming.stopStream();
};

window.noesis_pauseStream = () => {
    window.noesisStreaming.pauseStream();
};