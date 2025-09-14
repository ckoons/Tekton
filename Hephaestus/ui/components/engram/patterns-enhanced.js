/**
 * Enhanced Patterns Analytics Engine
 * Advanced cognitive pattern analysis with interactive concept formation graph
 */

class EnhancedPatternsAnalytics {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.concepts = new Map();
        this.edges = [];
        this.timeline = [];
        this.currentTime = 0;
        this.selectedConcept = null;
        
        // Color schemes
        this.thoughtColors = {
            hypothesis: '#00BCD4',
            observation: '#FFC107',
            insight: '#9C27B0',
            question: '#FF5722',
            solution: '#4CAF50',
            problem: '#F44336',
            pattern: '#2196F3',
            memory: '#795548'
        };
        
        this.edgeColors = {
            causal: '#4CAF50',
            contradicts: '#F44336',
            supports: '#2196F3',
            questions: '#FF9800',
            transforms: '#9C27B0',
            recalls: '#607D8B',
            synthesizes: '#00BCD4'
        };
        
        this.confidenceLevels = {
            random_thought: { width: 1, opacity: 0.3, glow: false },
            exploring: { width: 2, opacity: 0.5, glow: 'subtle' },
            developing: { width: 3, opacity: 0.7, glow: 'medium' },
            confident: { width: 4, opacity: 0.85, glow: 'strong' },
            certain: { width: 5, opacity: 1.0, glow: 'pulse' }
        };
        
        this.noveltyColors = {
            routine: '#607D8B',
            familiar: '#78909C',
            interesting: '#5C6BC0',
            novel: '#AB47BC',
            breakthrough: '#EC407A',
            revolutionary: '#FFD600'
        };
        
        this.init();
    }
    
    init() {
        this.setupUI();
        this.initD3();
        this.startSimulation();
        this.setupInteractions();
    }
    
    setupUI() {
        this.container.innerHTML = `
            <div class="patterns-enhanced">
                <div class="analytics-header">
                    <h3>Cognitive Pattern Analytics</h3>
                    <div class="analytics-controls">
                        <div class="timeline-control">
                            <span class="timeline-label">Timeline:</span>
                            <input type="range" id="timeline-slider" min="0" max="100" value="100">
                            <span id="timeline-time">Now</span>
                        </div>
                        <div class="analytics-status">
                            <span class="status-indicator active"></span>
                            <span id="pattern-count">0 concepts</span>
                        </div>
                    </div>
                </div>
                
                <div class="analytics-grid-enhanced">
                    <!-- Concept Formation Graph (LEFT - Visual Priority) -->
                    <div class="analytics-section concept-graph-section">
                        <h4>Concept Formation</h4>
                        <div id="concept-graph-container">
                            <svg id="concept-graph-svg"></svg>
                        </div>
                        <div class="graph-legend">
                            <div class="legend-section">
                                <span class="legend-title">Thought Types:</span>
                                <div class="legend-items thought-types"></div>
                            </div>
                            <div class="legend-section">
                                <span class="legend-title">Relationships:</span>
                                <div class="legend-items edge-types"></div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Learning Trajectory Timeline (RIGHT - Text Detail) -->
                    <div class="analytics-section trajectory-section">
                        <h4>Learning Trajectory</h4>
                        <div id="trajectory-timeline" class="timeline-container"></div>
                    </div>
                    
                    <!-- Active Patterns -->
                    <div class="analytics-section patterns-section">
                        <h4>Active Patterns</h4>
                        <div id="active-patterns" class="patterns-list"></div>
                    </div>
                    
                    <!-- Cognitive Insights -->
                    <div class="analytics-section insights-section">
                        <h4>Cognitive Insights</h4>
                        <div id="insights-dashboard" class="insights-container"></div>
                    </div>
                </div>
                
                <!-- Concept Detail Tooltip -->
                <div id="concept-tooltip" class="concept-tooltip" style="display: none;">
                    <div class="tooltip-header">
                        <span class="tooltip-type"></span>
                        <span class="tooltip-confidence"></span>
                    </div>
                    <div class="tooltip-content"></div>
                    <div class="tooltip-meta">
                        <span class="tooltip-time"></span>
                        <span class="tooltip-connections"></span>
                    </div>
                </div>
            </div>
        `;
        
        this.addStyles();
        this.createLegend();
    }
    
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .patterns-enhanced {
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
            
            .analytics-controls {
                display: flex;
                align-items: center;
                gap: 20px;
            }
            
            .timeline-control {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .timeline-label {
                color: #888;
                font-size: 0.85rem;
            }
            
            #timeline-slider {
                width: 200px;
                height: 4px;
                background: #333;
                outline: none;
                -webkit-appearance: none;
            }
            
            #timeline-slider::-webkit-slider-thumb {
                -webkit-appearance: none;
                appearance: none;
                width: 12px;
                height: 12px;
                background: #9C27B0;
                cursor: pointer;
                border-radius: 50%;
            }
            
            #timeline-time {
                color: #00BCD4;
                font-size: 0.85rem;
                min-width: 60px;
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
            
            .analytics-grid-enhanced {
                display: grid;
                grid-template-columns: 1.5fr 1fr;
                grid-template-rows: 1fr 1fr;
                gap: 15px;
                padding: 15px;
                height: calc(100% - 60px);
                overflow: hidden;
            }
            
            .concept-graph-section {
                grid-row: span 2;
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
            
            #concept-graph-container {
                flex: 1;
                position: relative;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
                overflow: hidden;
            }
            
            #concept-graph-svg {
                width: 100%;
                height: 100%;
            }
            
            .concept-node {
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .concept-node.highlighted {
                filter: brightness(1.5);
            }
            
            .concept-node.dimmed {
                opacity: 0.3;
            }
            
            .concept-label {
                font-size: 10px;
                fill: #fff;
                text-anchor: middle;
                pointer-events: none;
                user-select: none;
            }
            
            .concept-edge {
                fill: none;
                stroke-width: 1.5;
                opacity: 0.6;
            }
            
            .concept-edge.highlighted {
                stroke-width: 3;
                opacity: 1;
            }
            
            .concept-edge.dimmed {
                opacity: 0.1;
            }
            
            .graph-legend {
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid #333;
                display: flex;
                gap: 20px;
                font-size: 0.75rem;
            }
            
            .legend-section {
                flex: 1;
            }
            
            .legend-title {
                color: #888;
                display: block;
                margin-bottom: 5px;
            }
            
            .legend-items {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }
            
            .legend-item {
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .legend-color {
                width: 12px;
                height: 12px;
                border-radius: 2px;
            }
            
            .legend-label {
                color: #aaa;
                font-size: 0.7rem;
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
                cursor: pointer;
            }
            
            .trajectory-node.highlighted {
                background: rgba(156, 39, 176, 0.2);
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
            
            .node-concepts {
                margin-top: 6px;
                display: flex;
                gap: 6px;
                flex-wrap: wrap;
            }
            
            .node-concept-tag {
                background: rgba(156, 39, 176, 0.3);
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 0.7rem;
                color: #ddd;
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
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .pattern-card.highlighted {
                background: rgba(156, 39, 176, 0.2);
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
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .insight-item.highlighted {
                background: rgba(156, 39, 176, 0.2);
            }
            
            .concept-tooltip {
                position: absolute;
                background: rgba(20, 20, 30, 0.95);
                border: 1px solid #9C27B0;
                border-radius: 6px;
                padding: 12px;
                max-width: 300px;
                z-index: 1000;
                box-shadow: 0 4px 12px rgba(156, 39, 176, 0.3);
            }
            
            .tooltip-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
                padding-bottom: 8px;
                border-bottom: 1px solid #333;
            }
            
            .tooltip-type {
                font-weight: bold;
                color: #00BCD4;
                text-transform: uppercase;
                font-size: 0.8rem;
            }
            
            .tooltip-confidence {
                font-size: 0.75rem;
                color: #888;
            }
            
            .tooltip-content {
                color: #ddd;
                font-size: 0.85rem;
                line-height: 1.4;
                margin-bottom: 8px;
            }
            
            .tooltip-meta {
                display: flex;
                justify-content: space-between;
                font-size: 0.75rem;
                color: #666;
            }
            
            @keyframes glow-pulse {
                0%, 100% { box-shadow: 0 0 5px currentColor; }
                50% { box-shadow: 0 0 20px currentColor, 0 0 30px currentColor; }
            }
            
            .glow-strong {
                animation: glow-pulse 2s infinite;
            }
        `;
        document.head.appendChild(style);
    }
    
    createLegend() {
        // Create thought type legend
        const thoughtLegend = document.querySelector('.thought-types');
        Object.entries(this.thoughtColors).forEach(([type, color]) => {
            thoughtLegend.innerHTML += `
                <div class="legend-item">
                    <div class="legend-color" style="background: ${color}"></div>
                    <span class="legend-label">${type}</span>
                </div>
            `;
        });
        
        // Create edge type legend
        const edgeLegend = document.querySelector('.edge-types');
        Object.entries(this.edgeColors).forEach(([type, color]) => {
            edgeLegend.innerHTML += `
                <div class="legend-item">
                    <div class="legend-color" style="background: ${color}; width: 20px; height: 2px;"></div>
                    <span class="legend-label">${type}</span>
                </div>
            `;
        });
    }
    
    initD3() {
        const container = document.getElementById('concept-graph-container');
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        this.svg = d3.select('#concept-graph-svg')
            .attr('viewBox', `0 0 ${width} ${height}`);
        
        // Create layers
        this.edgeLayer = this.svg.append('g').attr('class', 'edges');
        this.nodeLayer = this.svg.append('g').attr('class', 'nodes');
        this.labelLayer = this.svg.append('g').attr('class', 'labels');
        
        // Initialize force simulation
        this.simulation = d3.forceSimulation()
            .force('link', d3.forceLink().id(d => d.id).distance(80))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(30));
        
        // Setup zoom
        const zoom = d3.zoom()
            .scaleExtent([0.5, 3])
            .on('zoom', (event) => {
                this.svg.selectAll('g').attr('transform', event.transform);
            });
        
        d3.select('#concept-graph-svg').call(zoom);
    }
    
    startSimulation() {
        // Generate initial concepts
        this.generateInitialConcepts();
        
        // Start real-time updates
        this.simulationInterval = setInterval(() => {
            this.addNewConcept();
            this.updateConnections();
            this.updateVisualization();
        }, 3000);
        
        // Initial render
        this.updateVisualization();
    }
    
    generateInitialConcepts() {
        const initialConcepts = [
            { id: 'c1', type: 'problem', thought: 'UI panels overlapping', confidence: 'exploring', novelty: 'familiar' },
            { id: 'c2', type: 'hypothesis', thought: 'Missing HTML structure', confidence: 'developing', novelty: 'interesting' },
            { id: 'c3', type: 'observation', thought: 'Patterns panel inside Memories', confidence: 'certain', novelty: 'novel' },
            { id: 'c4', type: 'solution', thought: 'Add missing closing div', confidence: 'certain', novelty: 'breakthrough' },
            { id: 'c5', type: 'insight', thought: 'Structure before styling', confidence: 'confident', novelty: 'revolutionary' }
        ];
        
        initialConcepts.forEach((concept, i) => {
            concept.x = Math.random() * 400 + 100;
            concept.y = Math.random() * 300 + 100;
            concept.timestamp = Date.now() - (5 - i) * 60000;
            this.concepts.set(concept.id, concept);
        });
        
        // Create initial connections
        this.edges = [
            { source: 'c1', target: 'c2', type: 'questions' },
            { source: 'c2', target: 'c3', type: 'supports' },
            { source: 'c3', target: 'c4', type: 'causal' },
            { source: 'c4', target: 'c5', type: 'transforms' }
        ];
    }
    
    addNewConcept() {
        const types = Object.keys(this.thoughtColors);
        const confidences = Object.keys(this.confidenceLevels);
        const novelties = Object.keys(this.noveltyColors);
        
        const id = `c${this.concepts.size + 1}`;
        const concept = {
            id,
            type: types[Math.floor(Math.random() * types.length)],
            thought: this.generateThought(),
            confidence: confidences[Math.floor(Math.random() * confidences.length)],
            novelty: novelties[Math.floor(Math.random() * novelties.length)],
            timestamp: Date.now(),
            x: Math.random() * 400 + 100,
            y: Math.random() * 300 + 100
        };
        
        this.concepts.set(id, concept);
        
        // Add to timeline
        this.addToTimeline(concept);
        
        // Create connections to existing concepts
        if (this.concepts.size > 1) {
            const existingIds = Array.from(this.concepts.keys()).filter(k => k !== id);
            const targetId = existingIds[Math.floor(Math.random() * existingIds.length)];
            const edgeTypes = Object.keys(this.edgeColors);
            this.edges.push({
                source: id,
                target: targetId,
                type: edgeTypes[Math.floor(Math.random() * edgeTypes.length)]
            });
        }
    }
    
    generateThought() {
        const thoughts = [
            'Pattern emerging in error handling',
            'User preference for visual feedback',
            'Recursive structure detected',
            'Memory allocation optimization',
            'Context switching overhead',
            'Parallel processing opportunity',
            'Cache invalidation issue',
            'State management complexity',
            'Async flow optimization',
            'Component lifecycle pattern'
        ];
        return thoughts[Math.floor(Math.random() * thoughts.length)];
    }
    
    addToTimeline(concept) {
        const timelineContainer = document.getElementById('trajectory-timeline');
        const node = document.createElement('div');
        node.className = 'trajectory-node';
        node.dataset.conceptId = concept.id;
        
        node.innerHTML = `
            <div class="node-time">${this.formatTime(concept.timestamp)}</div>
            <div class="node-stage">${concept.type.toUpperCase()}</div>
            <div class="node-thought">${concept.thought}</div>
            <div class="node-concepts">
                <span class="node-concept-tag">${concept.confidence}</span>
                <span class="node-concept-tag">${concept.novelty}</span>
            </div>
        `;
        
        node.addEventListener('click', () => this.highlightConcept(concept.id));
        node.addEventListener('mouseenter', () => this.highlightConcept(concept.id));
        node.addEventListener('mouseleave', () => this.clearHighlight());
        
        timelineContainer.insertBefore(node, timelineContainer.firstChild);
        
        // Keep only last 10 entries
        while (timelineContainer.children.length > 10) {
            timelineContainer.removeChild(timelineContainer.lastChild);
        }
    }
    
    updateConnections() {
        // Randomly strengthen or weaken connections
        this.edges.forEach(edge => {
            edge.strength = (edge.strength || 0.5) + (Math.random() - 0.5) * 0.1;
            edge.strength = Math.max(0.1, Math.min(1, edge.strength));
        });
    }
    
    updateVisualization() {
        const nodes = Array.from(this.concepts.values());
        const links = this.edges.map(e => ({
            ...e,
            source: this.concepts.get(e.source),
            target: this.concepts.get(e.target)
        })).filter(e => e.source && e.target);
        
        // Update edges
        const edgeSelection = this.edgeLayer.selectAll('.concept-edge')
            .data(links, d => `${d.source.id}-${d.target.id}`);
        
        edgeSelection.enter()
            .append('line')
            .attr('class', 'concept-edge')
            .merge(edgeSelection)
            .attr('stroke', d => this.edgeColors[d.type] || '#666')
            .attr('stroke-dasharray', d => d.type === 'contradicts' ? '5,5' : 
                                           d.type === 'questions' ? '2,2' : null)
            .attr('opacity', d => d.strength || 0.6);
        
        edgeSelection.exit().remove();
        
        // Update nodes
        const nodeSelection = this.nodeLayer.selectAll('.concept-node')
            .data(nodes, d => d.id);
        
        const nodeEnter = nodeSelection.enter()
            .append('g')
            .attr('class', 'concept-node')
            .on('click', (event, d) => this.highlightConcept(d.id))
            .on('mouseenter', (event, d) => this.showTooltip(event, d))
            .on('mouseleave', () => this.hideTooltip());
        
        // Add circles
        nodeEnter.append('circle')
            .attr('r', 20);
        
        // Add inner circles for confidence
        nodeEnter.append('circle')
            .attr('class', 'confidence-ring')
            .attr('r', 18)
            .attr('fill', 'none');
        
        // Update all nodes
        const nodeUpdate = nodeEnter.merge(nodeSelection);
        
        nodeUpdate.select('circle:first-child')
            .attr('fill', d => this.thoughtColors[d.type] || '#666')
            .attr('opacity', d => this.confidenceLevels[d.confidence].opacity);
        
        nodeUpdate.select('.confidence-ring')
            .attr('stroke', d => this.noveltyColors[d.novelty] || '#666')
            .attr('stroke-width', d => this.confidenceLevels[d.confidence].width);
        
        nodeSelection.exit().remove();
        
        // Update labels
        const labelSelection = this.labelLayer.selectAll('.concept-label')
            .data(nodes, d => d.id);
        
        labelSelection.enter()
            .append('text')
            .attr('class', 'concept-label')
            .merge(labelSelection)
            .text(d => this.truncateText(d.thought, 15))
            .attr('y', 30);
        
        labelSelection.exit().remove();
        
        // Update simulation
        this.simulation.nodes(nodes);
        this.simulation.force('link').links(links);
        this.simulation.alpha(0.3).restart();
        
        this.simulation.on('tick', () => {
            this.edgeLayer.selectAll('.concept-edge')
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            this.nodeLayer.selectAll('.concept-node')
                .attr('transform', d => `translate(${d.x},${d.y})`);
            
            this.labelLayer.selectAll('.concept-label')
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        });
        
        // Update count
        document.getElementById('pattern-count').textContent = `${nodes.length} concepts`;
    }
    
    highlightConcept(conceptId) {
        this.selectedConcept = conceptId;
        const concept = this.concepts.get(conceptId);
        if (!concept) return;
        
        // Highlight node
        this.nodeLayer.selectAll('.concept-node')
            .classed('highlighted', d => d.id === conceptId)
            .classed('dimmed', d => d.id !== conceptId);
        
        // Highlight connected edges
        this.edgeLayer.selectAll('.concept-edge')
            .classed('highlighted', d => d.source.id === conceptId || d.target.id === conceptId)
            .classed('dimmed', d => d.source.id !== conceptId && d.target.id !== conceptId);
        
        // Highlight timeline entry
        document.querySelectorAll('.trajectory-node').forEach(node => {
            node.classList.toggle('highlighted', node.dataset.conceptId === conceptId);
        });
        
        // Highlight related patterns
        this.highlightRelatedPatterns(concept);
    }
    
    clearHighlight() {
        this.selectedConcept = null;
        
        this.nodeLayer.selectAll('.concept-node')
            .classed('highlighted', false)
            .classed('dimmed', false);
        
        this.edgeLayer.selectAll('.concept-edge')
            .classed('highlighted', false)
            .classed('dimmed', false);
        
        document.querySelectorAll('.trajectory-node').forEach(node => {
            node.classList.remove('highlighted');
        });
        
        document.querySelectorAll('.pattern-card').forEach(card => {
            card.classList.remove('highlighted');
        });
        
        document.querySelectorAll('.insight-item').forEach(item => {
            item.classList.remove('highlighted');
        });
    }
    
    highlightRelatedPatterns(concept) {
        // Highlight patterns that match concept type
        document.querySelectorAll('.pattern-card').forEach(card => {
            const shouldHighlight = card.textContent.toLowerCase().includes(concept.type);
            card.classList.toggle('highlighted', shouldHighlight);
        });
        
        // Highlight insights related to concept
        document.querySelectorAll('.insight-item').forEach(item => {
            const shouldHighlight = Math.random() > 0.5; // Simulate relevance
            item.classList.toggle('highlighted', shouldHighlight);
        });
    }
    
    showTooltip(event, concept) {
        const tooltip = document.getElementById('concept-tooltip');
        tooltip.querySelector('.tooltip-type').textContent = concept.type;
        tooltip.querySelector('.tooltip-confidence').textContent = `${concept.confidence} (${Math.round(this.confidenceLevels[concept.confidence].opacity * 100)}%)`;
        tooltip.querySelector('.tooltip-content').textContent = concept.thought;
        tooltip.querySelector('.tooltip-time').textContent = this.formatTime(concept.timestamp);
        
        const connections = this.edges.filter(e => e.source === concept.id || e.target === concept.id).length;
        tooltip.querySelector('.tooltip-connections').textContent = `${connections} connections`;
        
        // Position tooltip
        const rect = this.container.getBoundingClientRect();
        tooltip.style.left = `${event.pageX - rect.left + 10}px`;
        tooltip.style.top = `${event.pageY - rect.top - 30}px`;
        tooltip.style.display = 'block';
    }
    
    hideTooltip() {
        document.getElementById('concept-tooltip').style.display = 'none';
    }
    
    setupInteractions() {
        // Timeline slider
        const slider = document.getElementById('timeline-slider');
        const timeDisplay = document.getElementById('timeline-time');
        
        slider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.currentTime = value;
            
            if (value === 100) {
                timeDisplay.textContent = 'Now';
            } else {
                const minutesAgo = Math.round((100 - value) * 0.6);
                timeDisplay.textContent = `-${minutesAgo}min`;
            }
            
            this.filterByTime(value);
        });
    }
    
    filterByTime(timeValue) {
        const cutoffTime = Date.now() - ((100 - timeValue) * 60000);
        
        // Filter nodes by time
        this.nodeLayer.selectAll('.concept-node')
            .style('display', d => d.timestamp >= cutoffTime ? null : 'none');
        
        // Filter edges connected to visible nodes
        this.edgeLayer.selectAll('.concept-edge')
            .style('display', d => {
                const sourceVisible = this.concepts.get(d.source.id).timestamp >= cutoffTime;
                const targetVisible = this.concepts.get(d.target.id).timestamp >= cutoffTime;
                return sourceVisible && targetVisible ? null : 'none';
            });
        
        // Filter labels
        this.labelLayer.selectAll('.concept-label')
            .style('display', d => d.timestamp >= cutoffTime ? null : 'none');
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
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
        if (this.simulationInterval) {
            clearInterval(this.simulationInterval);
        }
        if (this.simulation) {
            this.simulation.stop();
        }
    }
}

// Initialize when patterns panel is shown
function initializeEnhancedPatterns() {
    const container = document.getElementById('patterns-container');
    if (container) {
        // Clean up any existing instance
        if (window.enhancedPatterns) {
            window.enhancedPatterns.destroy();
        }
        
        console.log('Initializing Enhanced Patterns Analytics');
        window.enhancedPatterns = new EnhancedPatternsAnalytics('patterns-container');
    }
}

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    const patternsPanel = document.getElementById('patterns-panel');
    if (patternsPanel && patternsPanel.style.display !== 'none') {
        setTimeout(initializeEnhancedPatterns, 100);
    }
});

// Initialize when patterns tab is clicked
document.addEventListener('click', (e) => {
    if (e.target.closest('[data-tab="patterns"]') || 
        e.target.closest('#engram-tab-patterns') ||
        e.target.closest('[data-tekton-menu-panel="patterns-panel"]')) {
        setTimeout(initializeEnhancedPatterns, 100);
    }
});