/**
 * Patterns Analytics Engine
 * Real-time cognitive pattern analysis and learning trajectory tracking
 */

class PatternsAnalytics {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.patterns = new Map();
        this.learningTrajectory = [];
        this.insights = {
            blindSpots: [],
            inefficiencies: [],
            strengths: [],
            evolution: []
        };
        this.currentSession = {
            startTime: Date.now(),
            concepts: new Map(),
            transitions: [],
            errors: [],
            successes: []
        };
        
        this.init();
    }
    
    init() {
        this.setupUI();
        this.startAnalysis();
    }
    
    setupUI() {
        this.container.innerHTML = `
            <div class="patterns-analytics">
                <div class="analytics-header">
                    <h3>Cognitive Pattern Analytics</h3>
                    <div class="analytics-status">
                        <span class="status-indicator active"></span>
                        <span id="pattern-count">0 patterns detected</span>
                    </div>
                </div>
                
                <div class="analytics-grid">
                    <!-- Learning Trajectory Timeline -->
                    <div class="analytics-section trajectory-section">
                        <h4>Learning Trajectory</h4>
                        <div id="trajectory-timeline" class="timeline-container"></div>
                    </div>
                    
                    <!-- Concept Formation Graph -->
                    <div class="analytics-section concept-section">
                        <h4>Concept Formation</h4>
                        <canvas id="concept-graph" width="400" height="300"></canvas>
                    </div>
                    
                    <!-- Pattern Recognition -->
                    <div class="analytics-section patterns-section">
                        <h4>Active Patterns</h4>
                        <div id="active-patterns" class="patterns-list"></div>
                    </div>
                    
                    <!-- Insights Dashboard -->
                    <div class="analytics-section insights-section">
                        <h4>Cognitive Insights</h4>
                        <div id="insights-dashboard" class="insights-container"></div>
                    </div>
                </div>
            </div>
        `;
        
        this.addStyles();
    }
    
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .patterns-analytics {
                height: 100%;
                display: flex;
                flex-direction: column;
                background: #0a0a0a;
                color: #fff;
                font-family: 'Monaco', 'Menlo', monospace;
            }
            
            .analytics-header {
                padding: 15px 20px;
                background: #111;
                border-bottom: 1px solid #333;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .analytics-header h3 {
                color: #9C27B0;
                margin: 0;
                font-size: 1.1rem;
            }
            
            .analytics-status {
                display: flex;
                align-items: center;
                gap: 8px;
                color: #888;
                font-size: 0.85rem;
            }
            
            .status-indicator {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #4CAF50;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .analytics-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                grid-template-rows: 1fr 1fr;
                gap: 15px;
                padding: 15px;
                height: calc(100% - 60px);
                overflow: hidden;
            }
            
            .analytics-section {
                background: rgba(20, 20, 30, 0.6);
                border: 1px solid #333;
                border-radius: 8px;
                padding: 15px;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .analytics-section h4 {
                margin: 0 0 12px 0;
                color: #00BCD4;
                font-size: 0.95rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .timeline-container {
                flex: 1;
                overflow-y: auto;
                overflow-x: hidden;
            }
            
            .trajectory-node {
                position: relative;
                padding: 10px 10px 10px 35px;
                margin-bottom: 15px;
                background: rgba(0, 0, 0, 0.4);
                border-radius: 4px;
                border-left: 2px solid #4CAF50;
                transition: all 0.3s ease;
            }
            
            .trajectory-node:hover {
                background: rgba(0, 0, 0, 0.6);
                transform: translateX(5px);
            }
            
            .trajectory-node::before {
                content: '';
                position: absolute;
                left: -7px;
                top: 15px;
                width: 12px;
                height: 12px;
                background: #4CAF50;
                border-radius: 50%;
                border: 2px solid #0a0a0a;
            }
            
            .node-time {
                font-size: 0.75rem;
                color: #666;
                margin-bottom: 4px;
            }
            
            .node-stage {
                font-weight: bold;
                color: #00BCD4;
                margin-bottom: 4px;
                font-size: 0.85rem;
            }
            
            .node-thought {
                color: #ccc;
                font-size: 0.82rem;
                line-height: 1.4;
            }
            
            .node-insight {
                color: #4CAF50;
                font-size: 0.8rem;
                margin-top: 6px;
                font-style: italic;
            }
            
            .patterns-list {
                flex: 1;
                overflow-y: auto;
            }
            
            .pattern-card {
                background: rgba(0, 0, 0, 0.4);
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 4px;
                position: relative;
                overflow: hidden;
            }
            
            .pattern-card::before {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 3px;
            }
            
            .pattern-emerging::before { background: #00BCD4; }
            .pattern-strengthening::before { background: #4CAF50; }
            .pattern-stable::before { background: #9C27B0; }
            .pattern-fading::before { background: #FF9800; }
            
            .pattern-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 6px;
            }
            
            .pattern-type {
                font-weight: 500;
                color: #fff;
                font-size: 0.9rem;
            }
            
            .pattern-strength {
                font-size: 0.8rem;
                color: #888;
            }
            
            .pattern-description {
                font-size: 0.8rem;
                color: #aaa;
                line-height: 1.3;
            }
            
            .insights-container {
                flex: 1;
                overflow-y: auto;
            }
            
            .insight-item {
                background: rgba(0, 0, 0, 0.3);
                padding: 8px;
                margin-bottom: 8px;
                border-radius: 4px;
                font-size: 0.82rem;
            }
            
            .insight-blind-spot {
                border-left: 3px solid #F44336;
                background: rgba(244, 67, 54, 0.1);
            }
            
            .insight-inefficiency {
                border-left: 3px solid #FF9800;
                background: rgba(255, 152, 0, 0.1);
            }
            
            .insight-strength {
                border-left: 3px solid #4CAF50;
                background: rgba(76, 175, 80, 0.1);
            }
            
            .insight-evolution {
                border-left: 3px solid #9C27B0;
                background: rgba(156, 39, 176, 0.1);
            }
            
            .insight-label {
                font-weight: 500;
                margin-bottom: 4px;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            
            .insight-text {
                color: #ccc;
                line-height: 1.3;
            }
            
            #concept-graph {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
                width: 100%;
                height: auto;
                max-height: 250px;
            }
        `;
        document.head.appendChild(style);
    }
    
    startAnalysis() {
        // Start real-time analysis
        this.analysisInterval = setInterval(() => {
            this.detectPatterns();
            this.updateTrajectory();
            this.generateInsights();
            this.updateVisualization();
        }, 2000);
        
        // Initial data
        this.seedInitialData();
    }
    
    seedInitialData() {
        // Add initial learning trajectory
        this.addTrajectoryNode('INITIALIZATION', 'System starting, loading cognitive models', 'Establishing baseline patterns');
        
        setTimeout(() => {
            this.addTrajectoryNode('EXPLORATION', 'Analyzing user request patterns', 'Identifying communication style');
        }, 1000);
        
        // Add initial patterns
        this.addPattern('problem_decomposition', 'emerging', 'Breaking complex tasks into smaller components');
        this.addPattern('error_recovery', 'strengthening', 'Quick adaptation when initial approach fails');
        this.addPattern('context_switching', 'stable', 'Maintaining state across multiple file operations');
    }
    
    detectPatterns() {
        // Simulate pattern detection
        const patternTypes = [
            { id: 'abstraction_building', state: 'emerging', desc: 'Creating mental models from concrete examples' },
            { id: 'solution_synthesis', state: 'strengthening', desc: 'Combining multiple approaches into unified solution' },
            { id: 'assumption_validation', state: 'stable', desc: 'Verifying assumptions before implementing' },
            { id: 'iterative_refinement', state: 'strengthening', desc: 'Progressive enhancement of initial solution' },
            { id: 'knowledge_transfer', state: 'emerging', desc: 'Applying patterns from similar problems' }
        ];
        
        // Randomly detect new patterns
        if (Math.random() > 0.7) {
            const pattern = patternTypes[Math.floor(Math.random() * patternTypes.length)];
            if (!this.patterns.has(pattern.id)) {
                this.addPattern(pattern.id, pattern.state, pattern.desc);
            }
        }
        
        // Update pattern strengths
        this.patterns.forEach((pattern, id) => {
            pattern.strength = Math.min(100, pattern.strength + Math.random() * 5);
            if (pattern.strength > 80 && pattern.state === 'emerging') {
                pattern.state = 'strengthening';
            } else if (pattern.strength > 95 && pattern.state === 'strengthening') {
                pattern.state = 'stable';
            }
        });
    }
    
    addPattern(id, state, description) {
        this.patterns.set(id, {
            id,
            state,
            description,
            strength: Math.random() * 30 + 20,
            detectedAt: Date.now()
        });
    }
    
    addTrajectoryNode(stage, thought, insight = null) {
        const node = {
            stage,
            thought,
            insight,
            timestamp: Date.now()
        };
        this.learningTrajectory.push(node);
        
        // Keep only last 10 nodes
        if (this.learningTrajectory.length > 10) {
            this.learningTrajectory.shift();
        }
    }
    
    updateTrajectory() {
        // Simulate trajectory updates
        const stages = [
            { stage: 'PATTERN_RECOGNITION', thought: 'Identifying recurring solution structures' },
            { stage: 'HYPOTHESIS_FORMATION', thought: 'Formulating approach based on detected patterns' },
            { stage: 'VALIDATION', thought: 'Testing assumptions against actual behavior' },
            { stage: 'INTEGRATION', thought: 'Incorporating new understanding into knowledge base' },
            { stage: 'OPTIMIZATION', thought: 'Refining approach for efficiency' }
        ];
        
        if (Math.random() > 0.6) {
            const stage = stages[Math.floor(Math.random() * stages.length)];
            const insight = Math.random() > 0.5 ? `✓ Pattern confirmed: ${this.generateInsightText()}` : null;
            this.addTrajectoryNode(stage.stage, stage.thought, insight);
        }
    }
    
    generateInsightText() {
        const insights = [
            'User prefers visual feedback for operations',
            'Complex problems benefit from incremental validation',
            'Structure verification precedes functional debugging',
            'Context preservation crucial for multi-step tasks',
            'Simplified approaches often more effective'
        ];
        return insights[Math.floor(Math.random() * insights.length)];
    }
    
    generateInsights() {
        // Generate dynamic insights
        if (Math.random() > 0.8) {
            // Blind spots
            if (this.insights.blindSpots.length < 3) {
                this.insights.blindSpots.push({
                    text: 'Tendency to overlook edge cases in initial implementation',
                    frequency: Math.floor(Math.random() * 5) + 1
                });
            }
            
            // Inefficiencies
            if (this.insights.inefficiencies.length < 3) {
                this.insights.inefficiencies.push({
                    text: 'Redundant file reads when information already cached',
                    impact: 'Medium',
                    suggestion: 'Implement local state tracking'
                });
            }
            
            // Strengths
            if (this.insights.strengths.length < 3) {
                this.insights.strengths.push({
                    text: 'Excellent pattern recognition in debugging scenarios',
                    consistency: '92%'
                });
            }
            
            // Evolution
            if (this.insights.evolution.length < 3) {
                this.insights.evolution.push({
                    from: 'Linear problem solving',
                    to: 'Parallel hypothesis testing',
                    improvement: '+40% efficiency'
                });
            }
        }
    }
    
    updateVisualization() {
        // Update pattern count
        document.getElementById('pattern-count').textContent = `${this.patterns.size} patterns detected`;
        
        // Update timeline
        this.renderTimeline();
        
        // Update patterns list
        this.renderPatterns();
        
        // Update insights
        this.renderInsights();
        
        // Update concept graph
        this.renderConceptGraph();
    }
    
    renderTimeline() {
        const container = document.getElementById('trajectory-timeline');
        if (!container) return;
        
        container.innerHTML = this.learningTrajectory.map(node => `
            <div class="trajectory-node">
                <div class="node-time">${this.formatTime(node.timestamp)}</div>
                <div class="node-stage">${node.stage.replace(/_/g, ' ')}</div>
                <div class="node-thought">${node.thought}</div>
                ${node.insight ? `<div class="node-insight">${node.insight}</div>` : ''}
            </div>
        `).join('');
    }
    
    renderPatterns() {
        const container = document.getElementById('active-patterns');
        if (!container) return;
        
        container.innerHTML = Array.from(this.patterns.values()).map(pattern => `
            <div class="pattern-card pattern-${pattern.state}">
                <div class="pattern-header">
                    <span class="pattern-type">${pattern.id.replace(/_/g, ' ').toUpperCase()}</span>
                    <span class="pattern-strength">${Math.round(pattern.strength)}%</span>
                </div>
                <div class="pattern-description">${pattern.description}</div>
            </div>
        `).join('');
    }
    
    renderInsights() {
        const container = document.getElementById('insights-dashboard');
        if (!container) return;
        
        let html = '';
        
        // Render blind spots
        this.insights.blindSpots.forEach(spot => {
            html += `
                <div class="insight-item insight-blind-spot">
                    <div class="insight-label">🔴 Blind Spot</div>
                    <div class="insight-text">${spot.text}</div>
                </div>
            `;
        });
        
        // Render inefficiencies
        this.insights.inefficiencies.forEach(item => {
            html += `
                <div class="insight-item insight-inefficiency">
                    <div class="insight-label">⚠️ Inefficiency</div>
                    <div class="insight-text">${item.text}</div>
                </div>
            `;
        });
        
        // Render strengths
        this.insights.strengths.forEach(strength => {
            html += `
                <div class="insight-item insight-strength">
                    <div class="insight-label">✅ Strength</div>
                    <div class="insight-text">${strength.text}</div>
                </div>
            `;
        });
        
        // Render evolution
        this.insights.evolution.forEach(evo => {
            html += `
                <div class="insight-item insight-evolution">
                    <div class="insight-label">🔄 Evolution</div>
                    <div class="insight-text">${evo.from} → ${evo.to}</div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    renderConceptGraph() {
        const canvas = document.getElementById('concept-graph');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw concept connections
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        
        // Generate random concept nodes
        const concepts = [];
        const numConcepts = 8;
        
        for (let i = 0; i < numConcepts; i++) {
            concepts.push({
                x: Math.random() * (width - 40) + 20,
                y: Math.random() * (height - 40) + 20,
                radius: Math.random() * 15 + 10,
                connections: Math.floor(Math.random() * 3)
            });
        }
        
        // Draw connections
        concepts.forEach((concept, i) => {
            for (let j = 0; j < concept.connections; j++) {
                const target = concepts[(i + j + 1) % numConcepts];
                ctx.beginPath();
                ctx.moveTo(concept.x, concept.y);
                ctx.lineTo(target.x, target.y);
                ctx.stroke();
            }
        });
        
        // Draw concept nodes
        concepts.forEach(concept => {
            // Glow effect
            const gradient = ctx.createRadialGradient(
                concept.x, concept.y, 0,
                concept.x, concept.y, concept.radius
            );
            gradient.addColorStop(0, 'rgba(156, 39, 176, 0.8)');
            gradient.addColorStop(1, 'rgba(156, 39, 176, 0.1)');
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(concept.x, concept.y, concept.radius, 0, Math.PI * 2);
            ctx.fill();
            
            // Inner core
            ctx.fillStyle = '#9C27B0';
            ctx.beginPath();
            ctx.arc(concept.x, concept.y, concept.radius * 0.3, 0, Math.PI * 2);
            ctx.fill();
        });
    }
    
    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', { 
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
    
    destroy() {
        if (this.analysisInterval) {
            clearInterval(this.analysisInterval);
        }
    }
}

// Initialize when patterns panel is shown
function initializePatternsAnalytics() {
    const container = document.getElementById('patterns-container');
    if (container) {
        // Clean up any existing instance
        if (window.patternsAnalytics) {
            window.patternsAnalytics.destroy();
        }
        
        console.log('Initializing Patterns Analytics Engine');
        window.patternsAnalytics = new PatternsAnalytics('patterns-container');
    }
}

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if patterns panel is visible
    const patternsPanel = document.getElementById('patterns-panel');
    if (patternsPanel && patternsPanel.style.display !== 'none') {
        setTimeout(initializePatternsAnalytics, 100);
    }
});

// Initialize when patterns tab is clicked
document.addEventListener('click', (e) => {
    if (e.target.closest('[data-tab="patterns"]') || 
        e.target.closest('#engram-tab-patterns') ||
        e.target.closest('[data-tekton-menu-panel="patterns-panel"]')) {
        setTimeout(initializePatternsAnalytics, 100);
    }
});