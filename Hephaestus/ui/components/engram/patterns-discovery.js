/**
 * Patterns Discovery Engine - Living Pattern Visualization
 * @landmark Component: Pattern Discovery - Real-time pattern emergence and evolution
 * @landmark Visualization: D3.js pattern flow stream
 * @landmark WebSocket: Real-time pattern detection updates
 */

class PatternsDiscoveryEngine {
    constructor(containerId) {
        this.container = document.getElementById(containerId) || document.querySelector('#patterns-panel');
        this.ws = null;
        this.patterns = new Map(); // Pattern ID -> Pattern Object
        this.activeFilter = 'all';
        this.selectedCI = 'all';
        this.visualization = 'stream'; // stream, network, pulse
        this.animationFrame = null;
        this.flowSpeed = 1.0;
        
        this.init();
    }
    
    /**
     * @landmark Initialization: Setup pattern visualization
     */
    init() {
        this.createLayout();
        this.createVisualization();
        this.setupEventHandlers();
        this.connectWebSocket();
        this.startAnimation();
    }
    
    /**
     * @landmark Layout: Create main container structure
     */
    createLayout() {
        this.container.innerHTML = `
            <div class="patterns__header">
                <div class="patterns__title-section">
                    <h3 class="patterns__title">Pattern Discovery Engine</h3>
                    <span class="patterns__status">
                        <span class="patterns__status-dot" data-status="active"></span>
                        <span class="patterns__status-text">Detecting patterns...</span>
                    </span>
                </div>
                
                <div class="patterns__controls">
                    <select id="patterns-ci-select" class="patterns__select">
                        <option value="all">All CIs</option>
                        <option value="apollo">Apollo</option>
                        <option value="athena">Athena</option>
                        <option value="hermes">Hermes</option>
                        <option value="zeus">Zeus</option>
                        <option value="diana">Diana</option>
                    </select>
                    
                    <select id="patterns-filter" class="patterns__select">
                        <option value="all">All Patterns</option>
                        <option value="emerging">Emerging</option>
                        <option value="strengthening">Strengthening</option>
                        <option value="stable">Stable</option>
                        <option value="fading">Fading</option>
                        <option value="cyclical">Cyclical</option>
                    </select>
                    
                    <div class="patterns__viz-toggle">
                        <button class="patterns__viz-btn active" data-viz="stream">Stream</button>
                        <button class="patterns__viz-btn" data-viz="network">Network</button>
                        <button class="patterns__viz-btn" data-viz="pulse">Pulse</button>
                    </div>
                    
                    <button id="patterns-detect-btn" class="patterns__btn patterns__btn--primary">
                        Detect New Patterns
                    </button>
                </div>
            </div>
            
            <div class="patterns__main">
                <div class="patterns__visualization" id="patterns-viz-container">
                    <svg id="patterns-svg" width="100%" height="400"></svg>
                    <canvas id="patterns-canvas" width="1200" height="400" style="display: none;"></canvas>
                </div>
                
                <div class="patterns__legend">
                    <div class="patterns__legend-item">
                        <span class="patterns__legend-icon patterns__legend-icon--emerging"></span>
                        <span>Emerging</span>
                    </div>
                    <div class="patterns__legend-item">
                        <span class="patterns__legend-icon patterns__legend-icon--strengthening"></span>
                        <span>Strengthening</span>
                    </div>
                    <div class="patterns__legend-item">
                        <span class="patterns__legend-icon patterns__legend-icon--stable"></span>
                        <span>Stable</span>
                    </div>
                    <div class="patterns__legend-item">
                        <span class="patterns__legend-icon patterns__legend-icon--fading"></span>
                        <span>Fading</span>
                    </div>
                    <div class="patterns__legend-item">
                        <span class="patterns__legend-icon patterns__legend-icon--cyclical"></span>
                        <span>Cyclical</span>
                    </div>
                </div>
            </div>
            
            <div class="patterns__details" id="pattern-details" style="display: none;">
                <h4 class="patterns__details-title">Pattern Details</h4>
                <div class="patterns__details-content"></div>
            </div>
            
            <div class="patterns__discovery-feed">
                <h4 class="patterns__feed-title">Discovery Feed</h4>
                <div id="patterns-feed" class="patterns__feed">
                    <!-- Real-time pattern events will appear here -->
                </div>
            </div>
        `;
    }
    
    /**
     * @landmark Visualization: Create pattern flow stream
     */
    createVisualization() {
        this.svg = d3.select('#patterns-svg');
        this.canvas = document.getElementById('patterns-canvas');
        this.ctx = this.canvas.getContext('2d');
        
        const width = this.container.offsetWidth;
        const height = 400;
        
        this.svg.attr('viewBox', `0 0 ${width} ${height}`);
        
        // Create gradients for different pattern states
        const defs = this.svg.append('defs');
        
        // Emerging pattern gradient (green, translucent)
        const emergingGradient = defs.append('linearGradient')
            .attr('id', 'emerging-gradient')
            .attr('x1', '0%').attr('y1', '0%')
            .attr('x2', '100%').attr('y2', '0%');
        emergingGradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', '#4CAF50')
            .attr('stop-opacity', 0.2);
        emergingGradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', '#8BC34A')
            .attr('stop-opacity', 0.5);
        
        // Strengthening pattern gradient (yellow to orange)
        const strengtheningGradient = defs.append('linearGradient')
            .attr('id', 'strengthening-gradient')
            .attr('x1', '0%').attr('y1', '0%')
            .attr('x2', '100%').attr('y2', '0%');
        strengtheningGradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', '#FFEB3B')
            .attr('stop-opacity', 0.6);
        strengtheningGradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', '#FF9800')
            .attr('stop-opacity', 0.8);
        
        // Stable pattern gradient (blue, solid)
        const stableGradient = defs.append('linearGradient')
            .attr('id', 'stable-gradient')
            .attr('x1', '0%').attr('y1', '0%')
            .attr('x2', '100%').attr('y2', '0%');
        stableGradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', '#2196F3')
            .attr('stop-opacity', 0.8);
        stableGradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', '#3F51B5')
            .attr('stop-opacity', 0.9);
        
        // Create pattern flow groups
        this.flowGroup = this.svg.append('g')
            .attr('class', 'pattern-flows');
        
        this.nodesGroup = this.svg.append('g')
            .attr('class', 'pattern-nodes');
        
        this.labelsGroup = this.svg.append('g')
            .attr('class', 'pattern-labels');
    }
    
    /**
     * @landmark Pattern Stream: Create flowing river visualization
     */
    createPatternStream(pattern) {
        const width = this.container.offsetWidth;
        const height = 400;
        
        // Calculate Y position based on pattern strength and type
        const yBase = height / 2;
        const yOffset = (Math.random() - 0.5) * height * 0.6;
        const y = yBase + yOffset;
        
        // Create path data for flowing stream
        const pathData = this.generateStreamPath(pattern, y, width);
        
        // Add stream path
        const stream = this.flowGroup.append('path')
            .datum(pattern)
            .attr('class', `pattern-stream pattern-stream--${pattern.state}`)
            .attr('id', `stream-${pattern.id}`)
            .attr('d', pathData)
            .attr('fill', 'none')
            .attr('stroke', this.getPatternColor(pattern))
            .attr('stroke-width', this.getStreamWidth(pattern))
            .attr('stroke-opacity', this.getStreamOpacity(pattern))
            .attr('stroke-linecap', 'round')
            .on('click', (event, d) => this.showPatternDetails(d))
            .on('mouseover', (event, d) => this.highlightPattern(d))
            .on('mouseout', (event, d) => this.unhighlightPattern(d));
        
        // Add flow animation
        this.animateFlow(stream, pattern);
        
        // Add pattern label
        const label = this.labelsGroup.append('text')
            .attr('class', 'pattern-label')
            .attr('x', width * 0.7)
            .attr('y', y - 10)
            .attr('text-anchor', 'middle')
            .attr('font-size', '12px')
            .attr('fill', '#fff')
            .attr('opacity', 0.8)
            .text(pattern.name);
        
        return stream;
    }
    
    /**
     * @landmark Stream Path: Generate flowing path for pattern
     */
    generateStreamPath(pattern, yBase, width) {
        const points = [];
        const segments = 20;
        const segmentWidth = width / segments;
        
        for (let i = 0; i <= segments; i++) {
            const x = i * segmentWidth;
            let y = yBase;
            
            // Add wave motion based on pattern state
            if (pattern.state === 'cyclical') {
                y += Math.sin(i * 0.5 + Date.now() * 0.001) * 20;
            } else if (pattern.state === 'emerging') {
                y += (Math.random() - 0.5) * 10; // Jittery for emerging
            } else if (pattern.state === 'stable') {
                y += Math.sin(i * 0.3) * 5; // Gentle wave for stable
            }
            
            points.push([x, y]);
        }
        
        // Create smooth curve through points
        const line = d3.line()
            .x(d => d[0])
            .y(d => d[1])
            .curve(d3.curveBasis);
        
        return line(points);
    }
    
    /**
     * @landmark Flow Animation: Animate pattern flow
     */
    animateFlow(stream, pattern) {
        if (pattern.state === 'cyclical') {
            // Pulsing animation for cyclical patterns
            stream.transition()
                .duration(2000)
                .attr('stroke-width', this.getStreamWidth(pattern) * 1.3)
                .transition()
                .duration(2000)
                .attr('stroke-width', this.getStreamWidth(pattern))
                .on('end', () => this.animateFlow(stream, pattern));
        } else {
            // Flowing dash animation
            const totalLength = stream.node().getTotalLength();
            
            stream
                .attr('stroke-dasharray', `${totalLength * 0.1} ${totalLength * 0.1}`)
                .attr('stroke-dashoffset', 0)
                .transition()
                .duration(10000 / this.flowSpeed)
                .ease(d3.easeLinear)
                .attr('stroke-dashoffset', -totalLength * 0.2)
                .on('end', () => this.animateFlow(stream, pattern));
        }
    }
    
    /**
     * @landmark Network View: Create node-link pattern network
     */
    createPatternNetwork() {
        const width = this.container.offsetWidth;
        const height = 400;
        
        // Create force simulation
        this.simulation = d3.forceSimulation()
            .force('link', d3.forceLink().id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-200))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(30));
        
        // Convert patterns to nodes
        const nodes = Array.from(this.patterns.values());
        const links = this.detectPatternConnections(nodes);
        
        // Add links
        const link = this.flowGroup.selectAll('.pattern-link')
            .data(links)
            .enter().append('line')
            .attr('class', 'pattern-link')
            .attr('stroke', '#666')
            .attr('stroke-opacity', d => d.strength)
            .attr('stroke-width', d => d.strength * 5);
        
        // Add nodes
        const node = this.nodesGroup.selectAll('.pattern-node')
            .data(nodes)
            .enter().append('g')
            .attr('class', 'pattern-node')
            .call(d3.drag()
                .on('start', (event, d) => this.dragstarted(event, d))
                .on('drag', (event, d) => this.dragged(event, d))
                .on('end', (event, d) => this.dragended(event, d)));
        
        node.append('circle')
            .attr('r', d => 10 + d.strength * 20)
            .attr('fill', d => this.getPatternColor(d))
            .attr('fill-opacity', d => this.getStreamOpacity(d));
        
        node.append('text')
            .attr('dx', 15)
            .attr('dy', 5)
            .text(d => d.name)
            .attr('font-size', '12px')
            .attr('fill', '#fff');
        
        // Start simulation
        this.simulation.nodes(nodes);
        this.simulation.force('link').links(links);
        
        this.simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node.attr('transform', d => `translate(${d.x},${d.y})`);
        });
    }
    
    /**
     * @landmark Pulse View: Create pulsing rhythm visualization
     */
    createPulseVisualization() {
        const canvas = this.canvas;
        const ctx = this.ctx;
        
        canvas.style.display = 'block';
        this.svg.style('display', 'none');
        
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.fillStyle = 'rgba(30, 30, 46, 0.1)';
        ctx.fillRect(0, 0, width, height);
        
        // Draw pulse lines for each pattern
        let y = 50;
        this.patterns.forEach(pattern => {
            this.drawPulseLine(ctx, pattern, y, width);
            y += 60;
        });
    }
    
    /**
     * @landmark Pulse Line: Draw ECG-style pulse for pattern
     */
    drawPulseLine(ctx, pattern, y, width) {
        ctx.strokeStyle = this.getPatternColor(pattern);
        ctx.lineWidth = 2;
        ctx.globalAlpha = this.getStreamOpacity(pattern);
        
        ctx.beginPath();
        ctx.moveTo(0, y);
        
        const frequency = this.getPatternFrequency(pattern);
        const amplitude = pattern.strength * 30;
        
        for (let x = 0; x < width; x += 2) {
            const pulse = Math.sin((x + Date.now() * 0.001 * this.flowSpeed) * frequency) * amplitude;
            ctx.lineTo(x, y + pulse);
        }
        
        ctx.stroke();
        ctx.globalAlpha = 1;
        
        // Add pattern name
        ctx.fillStyle = '#fff';
        ctx.font = '12px monospace';
        ctx.fillText(pattern.name, 10, y - amplitude - 5);
    }
    
    /**
     * @landmark WebSocket: Connect to pattern detection stream
     */
    connectWebSocket() {
        const wsUrl = 'ws://localhost:8100/patterns/stream';
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('Patterns WebSocket connected');
                this.updateStatus('connected');
                this.requestPatterns();
            };
            
            this.ws.onmessage = (event) => {
                this.handleWebSocketMessage(event);
            };
            
            this.ws.onerror = (error) => {
                console.error('Patterns WebSocket error:', error);
                this.updateStatus('error');
            };
            
            this.ws.onclose = () => {
                console.log('Patterns WebSocket closed');
                this.updateStatus('disconnected');
                setTimeout(() => this.connectWebSocket(), 5000);
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.updateStatus('error');
        }
    }
    
    /**
     * @landmark Message Handler: Process pattern updates
     */
    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'pattern_detected':
                    this.addPattern(data.pattern);
                    this.addToFeed(`New pattern detected: ${data.pattern.name}`, 'emerging');
                    break;
                    
                case 'pattern_strengthening':
                    this.updatePattern(data.pattern_id, { 
                        state: 'strengthening',
                        strength: data.strength 
                    });
                    break;
                    
                case 'pattern_stable':
                    this.updatePattern(data.pattern_id, { 
                        state: 'stable' 
                    });
                    break;
                    
                case 'pattern_fading':
                    this.updatePattern(data.pattern_id, { 
                        state: 'fading',
                        strength: data.strength 
                    });
                    break;
                    
                case 'pattern_cyclical':
                    this.updatePattern(data.pattern_id, { 
                        state: 'cyclical',
                        cycle_period: data.period 
                    });
                    break;
                    
                case 'patterns_list':
                    data.patterns.forEach(p => this.addPattern(p));
                    break;
            }
            
            this.updateVisualization();
        } catch (error) {
            console.error('Error handling pattern message:', error);
        }
    }
    
    /**
     * @landmark Pattern Management: Add new pattern
     */
    addPattern(pattern) {
        if (!pattern.id) pattern.id = `pattern_${Date.now()}`;
        
        this.patterns.set(pattern.id, {
            id: pattern.id,
            name: pattern.name || 'Unknown Pattern',
            state: pattern.state || 'emerging',
            strength: pattern.strength || 0.3,
            type: pattern.type || 'behavioral',
            ci_id: pattern.ci_id || 'unknown',
            emotion: pattern.emotion || 'neutral',
            occurrences: pattern.occurrences || 1,
            first_seen: pattern.first_seen || Date.now(),
            last_seen: pattern.last_seen || Date.now(),
            triggers: pattern.triggers || [],
            connections: pattern.connections || []
        });
        
        if (this.visualization === 'stream') {
            this.createPatternStream(this.patterns.get(pattern.id));
        }
    }
    
    /**
     * @landmark Pattern Update: Update existing pattern
     */
    updatePattern(patternId, updates) {
        const pattern = this.patterns.get(patternId);
        if (!pattern) return;
        
        Object.assign(pattern, updates);
        pattern.last_seen = Date.now();
        
        // Update visualization
        if (this.visualization === 'stream') {
            const stream = d3.select(`#stream-${patternId}`);
            stream
                .transition()
                .duration(1000)
                .attr('stroke-width', this.getStreamWidth(pattern))
                .attr('stroke-opacity', this.getStreamOpacity(pattern));
        }
    }
    
    /**
     * @landmark Feed: Add event to discovery feed
     */
    addToFeed(message, type = 'info') {
        const feed = document.getElementById('patterns-feed');
        const item = document.createElement('div');
        item.className = `patterns__feed-item patterns__feed-item--${type}`;
        
        const time = new Date().toLocaleTimeString();
        item.innerHTML = `
            <span class="patterns__feed-time">${time}</span>
            <span class="patterns__feed-message">${message}</span>
        `;
        
        feed.insertBefore(item, feed.firstChild);
        
        // Keep only last 20 items
        while (feed.children.length > 20) {
            feed.removeChild(feed.lastChild);
        }
    }
    
    /**
     * @landmark Details: Show pattern details panel
     */
    showPatternDetails(pattern) {
        const detailsPanel = document.getElementById('pattern-details');
        const content = detailsPanel.querySelector('.patterns__details-content');
        
        content.innerHTML = `
            <div class="patterns__detail-row">
                <label>Name:</label>
                <span>${pattern.name}</span>
            </div>
            <div class="patterns__detail-row">
                <label>State:</label>
                <span class="patterns__state patterns__state--${pattern.state}">${pattern.state}</span>
            </div>
            <div class="patterns__detail-row">
                <label>Strength:</label>
                <div class="patterns__strength-bar">
                    <div class="patterns__strength-fill" style="width: ${pattern.strength * 100}%"></div>
                </div>
                <span>${(pattern.strength * 100).toFixed(0)}%</span>
            </div>
            <div class="patterns__detail-row">
                <label>Type:</label>
                <span>${pattern.type}</span>
            </div>
            <div class="patterns__detail-row">
                <label>CI:</label>
                <span>${pattern.ci_id}</span>
            </div>
            <div class="patterns__detail-row">
                <label>Occurrences:</label>
                <span>${pattern.occurrences}</span>
            </div>
            <div class="patterns__detail-row">
                <label>First Seen:</label>
                <span>${new Date(pattern.first_seen).toLocaleString()}</span>
            </div>
            <div class="patterns__detail-row">
                <label>Triggers:</label>
                <span>${pattern.triggers.join(', ') || 'None identified'}</span>
            </div>
        `;
        
        detailsPanel.style.display = 'block';
    }
    
    /**
     * @landmark Helpers: Utility functions
     */
    getPatternColor(pattern) {
        const colors = {
            emerging: '#4CAF50',
            strengthening: '#FF9800',
            stable: '#2196F3',
            fading: '#9E9E9E',
            cyclical: '#9C27B0'
        };
        return colors[pattern.state] || '#666';
    }
    
    getStreamWidth(pattern) {
        return 5 + (pattern.strength * 25);
    }
    
    getStreamOpacity(pattern) {
        const opacities = {
            emerging: 0.4,
            strengthening: 0.7,
            stable: 0.9,
            fading: 0.3,
            cyclical: 0.8
        };
        return opacities[pattern.state] || 0.5;
    }
    
    getPatternFrequency(pattern) {
        if (pattern.state === 'cyclical') return 0.1;
        if (pattern.state === 'stable') return 0.05;
        return 0.02;
    }
    
    /**
     * @landmark Event Handlers: Setup UI interactions
     */
    setupEventHandlers() {
        // CI selector
        document.getElementById('patterns-ci-select').addEventListener('change', (e) => {
            this.selectedCI = e.target.value;
            this.filterPatterns();
        });
        
        // Filter selector
        document.getElementById('patterns-filter').addEventListener('change', (e) => {
            this.activeFilter = e.target.value;
            this.filterPatterns();
        });
        
        // Visualization toggle
        document.querySelectorAll('.patterns__viz-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.patterns__viz-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.visualization = btn.dataset.viz;
                this.updateVisualization();
            });
        });
        
        // Detect patterns button
        document.getElementById('patterns-detect-btn').addEventListener('click', () => {
            this.detectNewPatterns();
        });
    }
    
    /**
     * @landmark Filter: Filter visible patterns
     */
    filterPatterns() {
        const filtered = Array.from(this.patterns.values()).filter(pattern => {
            if (this.selectedCI !== 'all' && pattern.ci_id !== this.selectedCI) return false;
            if (this.activeFilter !== 'all' && pattern.state !== this.activeFilter) return false;
            return true;
        });
        
        // Update visualization with filtered patterns
        this.updateVisualization(filtered);
    }
    
    /**
     * @landmark Update: Refresh visualization
     */
    updateVisualization(patterns = null) {
        const patternsToShow = patterns || Array.from(this.patterns.values());
        
        // Clear current visualization
        this.flowGroup.selectAll('*').remove();
        this.nodesGroup.selectAll('*').remove();
        this.labelsGroup.selectAll('*').remove();
        
        if (this.visualization === 'stream') {
            this.svg.style('display', 'block');
            this.canvas.style.display = 'none';
            patternsToShow.forEach(p => this.createPatternStream(p));
        } else if (this.visualization === 'network') {
            this.svg.style('display', 'block');
            this.canvas.style.display = 'none';
            this.createPatternNetwork();
        } else if (this.visualization === 'pulse') {
            this.createPulseVisualization();
        }
    }
    
    /**
     * @landmark Animation Loop: Continuous updates
     */
    startAnimation() {
        const animate = () => {
            if (this.visualization === 'pulse') {
                this.createPulseVisualization();
            }
            
            this.animationFrame = requestAnimationFrame(animate);
        };
        
        animate();
    }
    
    /**
     * @landmark Pattern Detection: Request new pattern analysis
     */
    detectNewPatterns() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: 'detect_patterns',
                ci_id: this.selectedCI
            }));
            
            this.addToFeed('Initiating pattern detection...', 'info');
        }
    }
    
    /**
     * @landmark Pattern Connections: Detect relationships
     */
    detectPatternConnections(patterns) {
        const connections = [];
        
        patterns.forEach((p1, i) => {
            patterns.slice(i + 1).forEach(p2 => {
                // Check for connections based on various criteria
                let strength = 0;
                
                // Same CI source
                if (p1.ci_id === p2.ci_id) strength += 0.2;
                
                // Similar emotions
                if (p1.emotion === p2.emotion) strength += 0.3;
                
                // Temporal proximity
                const timeDiff = Math.abs(p1.last_seen - p2.last_seen);
                if (timeDiff < 3600000) strength += 0.3; // Within an hour
                
                // Shared triggers
                const sharedTriggers = p1.triggers.filter(t => p2.triggers.includes(t));
                strength += sharedTriggers.length * 0.1;
                
                if (strength > 0.3) {
                    connections.push({
                        source: p1,
                        target: p2,
                        strength: Math.min(strength, 1)
                    });
                }
            });
        });
        
        return connections;
    }
    
    /**
     * @landmark Status: Update connection status
     */
    updateStatus(status) {
        const statusDot = document.querySelector('.patterns__status-dot');
        const statusText = document.querySelector('.patterns__status-text');
        
        if (statusDot) {
            statusDot.dataset.status = status;
        }
        
        if (statusText) {
            const messages = {
                connected: 'Detecting patterns...',
                disconnected: 'Connection lost',
                error: 'Connection error'
            };
            statusText.textContent = messages[status] || 'Unknown';
        }
    }
    
    /**
     * @landmark Request: Request initial patterns
     */
    requestPatterns() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: 'get_patterns',
                ci_id: this.selectedCI
            }));
        }
    }
    
    /**
     * @landmark Drag: Handle node dragging in network view
     */
    dragstarted(event, d) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    dragended(event, d) {
        if (!event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    /**
     * @landmark Highlight: Highlight pattern on hover
     */
    highlightPattern(pattern) {
        // Highlight connected patterns
        pattern.connections.forEach(connId => {
            d3.select(`#stream-${connId}`)
                .classed('highlighted', true);
        });
    }
    
    unhighlightPattern(pattern) {
        // Remove highlights
        d3.selectAll('.pattern-stream')
            .classed('highlighted', false);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (document.getElementById('patterns-panel')) {
            window.patternsDiscovery = new PatternsDiscoveryEngine('patterns-panel');
        }
    });
} else {
    if (document.getElementById('patterns-panel')) {
        window.patternsDiscovery = new PatternsDiscoveryEngine('patterns-panel');
    }
}

// Export for use in other components
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PatternsDiscoveryEngine;
}