/**
 * Noesis Enhanced API Integration
 * Minimal JavaScript for backend API communication
 */

class NoesisAPI {
    constructor() {
        this.baseUrl = noesisUrl('');
        this.requestTimeout = 10000;
        this.initialize();
    }
    
    initialize() {
        this.setupPeriodicUpdates();
        console.log('[NoesisAPI] Enhanced API integration initialized');
    }
    
    setupPeriodicUpdates() {
        // Poll for analysis updates every 5 seconds
        setInterval(() => {
            this.fetchAnalysisUpdate();
        }, 5000);
        
        // Poll for metrics every 2 seconds
        setInterval(() => {
            this.fetchMetricsUpdate();
        }, 2000);
    }
    
    async fetchAnalysisUpdate() {
        try {
            const response = await fetch(`${this.baseUrl}/api/analysis/current`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                signal: AbortSignal.timeout(this.requestTimeout)
            });
            
            if (response.ok) {
                const data = await response.json();
                this.handleAnalysisUpdate(data);
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.warn('[NoesisAPI] Analysis update failed:', error.message);
            }
        }
    }
    
    async fetchMetricsUpdate() {
        try {
            const response = await fetch(`${this.baseUrl}/api/metrics/current`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                signal: AbortSignal.timeout(this.requestTimeout)
            });
            
            if (response.ok) {
                const data = await response.json();
                this.handleMetricsUpdate(data);
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.warn('[NoesisAPI] Metrics update failed:', error.message);
            }
        }
    }
    
    handleAnalysisUpdate(data) {
        // Update manifold analysis
        if (data.manifold && window.noesisManifoldViewer) {
            window.noesisManifoldViewer.updateManifold(data.manifold);
        }
        
        // Update manifold properties
        if (data.manifold) {
            this.updateElement('intrinsic-dimension', data.manifold.intrinsic_dimension);
            this.updateElement('manifold-curvature', data.manifold.curvature);
            this.updateElement('topology-class', data.manifold.topology);
            this.updateElement('manifold-stability', data.manifold.stability);
        }
        
        // Update dynamics
        if (data.dynamics) {
            this.updateRegimesList(data.dynamics.regimes);
        }
        
        // Update catastrophe warnings
        if (data.catastrophe) {
            this.updateElement('critical-transitions-count', data.catastrophe.critical_transitions);
            this.updateElement('warning-signals-count', data.catastrophe.warning_signals);
            this.updateElement('stability-index-value', data.catastrophe.stability_index);
        }
        
        // Check for new patterns
        if (data.patterns && data.patterns.length > 0) {
            data.patterns.forEach(pattern => {
                if (window.noesisPatternDetector) {
                    window.noesisPatternDetector.addPattern(pattern);
                }
            });
        }
    }
    
    handleMetricsUpdate(data) {
        // Update memory metrics
        if (data.memory) {
            this.updateElement('active-memories-count', data.memory.active_count);
            this.updateElement('pattern-strength-value', data.memory.pattern_strength);
            this.updateElement('coherence-score-value', data.memory.coherence_score);
        }
        
        // Update streaming status
        if (data.stream_status) {
            this.updateElement('stream-status-indicator', data.stream_status.status);
        }
    }
    
    updateElement(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            const formattedValue = this.formatValue(value);
            element.textContent = formattedValue;
            
            // Add update animation class
            element.classList.add('noesis__value-updated');
            setTimeout(() => {
                element.classList.remove('noesis__value-updated');
            }, 500);
        }
    }
    
    updateRegimesList(regimes) {
        const regimeList = document.getElementById('regime-list');
        if (!regimeList || !regimes) return;
        
        // Clear and rebuild list using innerHTML
        const regimesHTML = regimes.map(regime => `
            <div class="noesis__regime-item noesis__regime-item--${regime.type || 'unknown'}">
                <div class="noesis__regime-header">
                    <span class="noesis__regime-name">${regime.name || 'Unknown Regime'}</span>
                    <span class="noesis__regime-confidence">${(regime.confidence * 100).toFixed(1)}%</span>
                </div>
                <div class="noesis__regime-details">
                    <span class="noesis__regime-duration">Duration: ${regime.duration || 0}s</span>
                    <span class="noesis__regime-transition">→ ${regime.next_regime || 'Unknown'}</span>
                </div>
            </div>
        `).join('');
        
        regimeList.innerHTML = regimesHTML;
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
    
    async updateManifoldAnalysis(dimension, method) {
        try {
            const response = await fetch(`${this.baseUrl}/api/analysis/manifold`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    target_dimension: dimension,
                    reduction_method: method
                }),
                signal: AbortSignal.timeout(this.requestTimeout)
            });
            
            if (response.ok) {
                const data = await response.json();
                this.handleAnalysisUpdate(data);
                return true;
            } else {
                console.error('[NoesisAPI] Manifold update failed:', response.status);
                return false;
            }
        } catch (error) {
            console.error('[NoesisAPI] Manifold update error:', error);
            return false;
        }
    }
    
    async queryMemories(query) {
        try {
            const response = await fetch(`${this.baseUrl}/api/memories/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query }),
                signal: AbortSignal.timeout(this.requestTimeout)
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.results || [];
            } else {
                console.error('[NoesisAPI] Memory query failed:', response.status);
                return [];
            }
        } catch (error) {
            console.error('[NoesisAPI] Memory query error:', error);
            return [];
        }
    }
    
    async getPatternLibrary() {
        try {
            const response = await fetch(`${this.baseUrl}/api/patterns/library`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                signal: AbortSignal.timeout(this.requestTimeout)
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.patterns || [];
            } else {
                console.error('[NoesisAPI] Pattern library fetch failed:', response.status);
                return [];
            }
        } catch (error) {
            console.error('[NoesisAPI] Pattern library error:', error);
            return [];
        }
    }
    
    async getAnalysisHistory(timeRange = '1h') {
        try {
            const response = await fetch(`${this.baseUrl}/api/analysis/history?range=${timeRange}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                signal: AbortSignal.timeout(this.requestTimeout)
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.history || [];
            } else {
                console.error('[NoesisAPI] Analysis history fetch failed:', response.status);
                return [];
            }
        } catch (error) {
            console.error('[NoesisAPI] Analysis history error:', error);
            return [];
        }
    }
}

// Initialize global API instance
window.noesisAPI = new NoesisAPI();

// UI event handlers for analysis controls
window.noesis_updateManifoldAnalysis = async () => {
    const dimensionSelect = document.getElementById('manifold-dimension');
    const methodSelect = document.getElementById('reduction-method');
    
    if (dimensionSelect && methodSelect) {
        const dimension = parseInt(dimensionSelect.value);
        const method = methodSelect.value;
        
        // Update button state
        const updateButton = document.getElementById('update-manifold');
        if (updateButton) {
            updateButton.textContent = 'Updating...';
            updateButton.disabled = true;
        }
        
        const success = await window.noesisAPI.updateManifoldAnalysis(dimension, method);
        
        // Restore button state
        if (updateButton) {
            updateButton.textContent = 'Update Analysis';
            updateButton.disabled = false;
        }
        
        if (!success) {
            console.warn('[NoesisAPI] Manifold analysis update failed');
        }
    }
};

// Attach event listeners when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Attach manifold update handler
    const updateButton = document.getElementById('update-manifold');
    if (updateButton) {
        updateButton.addEventListener('click', window.noesis_updateManifoldAnalysis);
    }
});