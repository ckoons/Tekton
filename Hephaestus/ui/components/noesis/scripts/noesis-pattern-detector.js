/**
 * Noesis Pattern Detection System
 * Minimal JavaScript following HTML injection, CSS first approach
 */

class NoesisPatternDetector {
    constructor() {
        this.patterns = new Map();
        this.patternTypes = {
            'scaling_law': { icon: '📈', color: '#4CAF50', priority: 'high' },
            'phase_transition': { icon: '🔄', color: '#FF9800', priority: 'high' },
            'manifold_structure': { icon: '🌐', color: '#2196F3', priority: 'medium' },
            'regime_change': { icon: '⚡', color: '#F44336', priority: 'high' },
            'correlation_pattern': { icon: '🔗', color: '#9C27B0', priority: 'medium' },
            'anomaly_detected': { icon: '🚨', color: '#FF5722', priority: 'critical' }
        };
        
        this.initialize();
    }
    
    initialize() {
        this.setupEventListeners();
        console.log('[NoesisPatternDetector] Pattern detection system initialized');
    }
    
    setupEventListeners() {
        // Listen for pattern detection events from backend
        document.addEventListener('noesis-pattern-detected', (event) => {
            this.handlePatternDetected(event.detail);
        });
    }
    
    addPattern(pattern) {
        if (!pattern || !pattern.id || !pattern.type) return;
        
        this.patterns.set(pattern.id, {
            ...pattern,
            timestamp: new Date(),
            displayed: false
        });
        
        // Use innerHTML injection instead of DOM manipulation
        this.displayPatternAlert(pattern);
        
        console.log(`[NoesisPatternDetector] Pattern detected: ${pattern.type} (${(pattern.confidence * 100).toFixed(1)}% confidence)`);
    }
    
    displayPatternAlert(pattern) {
        const alertContainer = document.getElementById('noesis-pattern-alerts');
        if (!alertContainer) return;
        
        const config = this.patternTypes[pattern.type] || {
            icon: '🔍', color: '#FF6F00', priority: 'medium'
        };
        
        const confidencePercent = (pattern.confidence * 100).toFixed(1);
        const description = pattern.description || this.generatePatternDescription(pattern);
        
        // Use innerHTML injection
        const alertHTML = `
            <div class="noesis__pattern-alert noesis__pattern-alert--${config.priority}" 
                 data-pattern-id="${pattern.id}" 
                 style="border-left-color: ${config.color}">
                <div class="noesis__alert-icon" style="color: ${config.color}">
                    ${config.icon}
                </div>
                <div class="noesis__alert-content">
                    <h5 class="noesis__alert-title">${this.formatPatternType(pattern.type)}</h5>
                    <p class="noesis__alert-description">${description}</p>
                    <div class="noesis__alert-metadata">
                        <span class="noesis__alert-confidence" style="color: ${config.color}">
                            ${confidencePercent}% confidence
                        </span>
                        <span class="noesis__alert-timestamp">
                            ${new Date().toLocaleTimeString()}
                        </span>
                    </div>
                </div>
                <div class="noesis__alert-actions">
                    <button class="noesis__alert-action" onclick="noesisPatternDetector.explorePattern('${pattern.id}')" 
                            title="Explore this pattern">🔍</button>
                    <button class="noesis__alert-action" onclick="noesisPatternDetector.dismissAlert('${pattern.id}')" 
                            title="Dismiss alert">✕</button>
                </div>
            </div>
        `;
        
        // Inject at the beginning
        alertContainer.insertAdjacentHTML('afterbegin', alertHTML);
        
        // Limit alerts by removing excess from end
        while (alertContainer.children.length > 5) {
            alertContainer.removeChild(alertContainer.lastElementChild);
        }
        
        // Auto-dismiss after timeout
        setTimeout(() => this.dismissAlert(pattern.id), 10000);
    }
    
    generatePatternDescription(pattern) {
        const descriptions = {
            'scaling_law': `Scaling relationship detected: ${pattern.equation || 'D(N) ∝ N^α'}`,
            'phase_transition': `System transition detected at ${pattern.threshold || 'critical point'}`,
            'manifold_structure': `${pattern.dimension || 'Multi'}-dimensional manifold structure identified`,
            'regime_change': `Dynamics regime shift: ${pattern.from_regime || 'unknown'} → ${pattern.to_regime || 'new state'}`,
            'correlation_pattern': `Strong correlation detected (r=${pattern.correlation || '0.8+'})`,
            'anomaly_detected': `Anomalous behavior detected in ${pattern.component || 'system'}`
        };
        return descriptions[pattern.type] || `${pattern.type} pattern detected`;
    }
    
    formatPatternType(type) {
        return type.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }
    
    dismissAlert(patternId) {
        const alertElement = document.querySelector(`[data-pattern-id="${patternId}"]`);
        if (alertElement) {
            alertElement.style.opacity = '0';
            alertElement.style.transform = 'translateX(20px)';
            setTimeout(() => {
                if (alertElement.parentNode) {
                    alertElement.parentNode.removeChild(alertElement);
                }
            }, 300);
        }
    }
    
    explorePattern(patternId) {
        const pattern = this.patterns.get(patternId);
        if (!pattern) return;
        
        const chatInput = document.getElementById('noesis-chat-input');
        if (chatInput) {
            chatInput.value = this.generateExplorationQuery(pattern);
            
            // Switch to discovery tab
            const discoveryTab = document.getElementById('noesis-tab-discovery');
            if (discoveryTab) discoveryTab.checked = true;
            
            chatInput.focus();
        }
    }
    
    generateExplorationQuery(pattern) {
        const queries = {
            'scaling_law': `Analyze the scaling law pattern detected. What are the implications of this ${pattern.equation || 'scaling relationship'}?`,
            'phase_transition': `Investigate the phase transition detected. What caused this system state change?`,
            'manifold_structure': `Examine the manifold structure pattern. How does this affect system behavior?`,
            'regime_change': `Explore the regime change. What are the underlying dynamics?`,
            'correlation_pattern': `Investigate the correlation pattern. What systems are interacting and why?`,
            'anomaly_detected': `Analyze the anomaly detected. Is this a concern or an opportunity?`
        };
        return queries[pattern.type] || `Explain the ${pattern.type} pattern detected`;
    }
    
    handlePatternDetected(patternData) {
        this.addPattern(patternData);
    }
    
    // Testing function
    simulatePattern(type = 'scaling_law') {
        const mockPattern = {
            id: `pattern_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            type: type,
            confidence: 0.7 + Math.random() * 0.3,
            description: null,
            source: 'simulation'
        };
        this.addPattern(mockPattern);
        return mockPattern;
    }
}

// Initialize global pattern detector
window.noesisPatternDetector = new NoesisPatternDetector();