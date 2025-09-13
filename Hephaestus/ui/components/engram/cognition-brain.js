/**
 * Cognition Brain Visualization Component
 * @landmark Component: Brain Monitor - Real-time CI cognitive state visualization
 * @landmark Visualization: D3.js brain region heat map
 * @landmark WebSocket: Real-time connection to ESR Experience Layer
 */

class CognitionBrainVisualization {
    constructor(containerId) {
        this.container = document.getElementById(containerId) || document.querySelector('.cognition__container');
        this.ws = null;
        this.selectedCI = 'apollo'; // Default CI
        this.activeMetrics = new Set(['working_memory', 'processing']);
        this.timeMode = 'live'; // 'live' or timestamp for historical
        this.playbackSpeed = 1.0;
        this.brainRegions = this.initializeBrainRegions();
        this.regionActivations = {};
        this.activityFeed = [];
        
        this.init();
    }
    
    /**
     * @landmark Initialization: Setup brain visualization and controls
     */
    init() {
        this.createLayout();
        this.createBrainSVG();
        this.createControls();
        this.createTimeline();
        this.createActivityFeed();
        this.connectWebSocket();
        this.startAnimationLoop();
    }
    
    /**
     * @landmark Brain Regions: Map CI functions to anatomical regions
     */
    initializeBrainRegions() {
        return {
            prefrontalCortex: {
                name: 'Prefrontal Cortex',
                functions: ['working_memory', 'forethought', 'planning'],
                position: { x: 200, y: 100 },
                size: 40,
                activation: 0
            },
            hippocampus: {
                name: 'Hippocampus',
                functions: ['memory_formation', 'consolidation', 'recall'],
                position: { x: 250, y: 200 },
                size: 35,
                activation: 0
            },
            amygdala: {
                name: 'Amygdala',
                functions: ['emotions', 'stress', 'mood'],
                position: { x: 220, y: 240 },
                size: 30,
                activation: 0
            },
            temporalLobe: {
                name: 'Temporal Lobe',
                functions: ['associations', 'pattern_recognition'],
                position: { x: 150, y: 180 },
                size: 45,
                activation: 0
            },
            motorCortex: {
                name: 'Motor Cortex',
                functions: ['action_planning', 'task_execution'],
                position: { x: 200, y: 50 },
                size: 35,
                activation: 0
            },
            brocasArea: {
                name: "Broca's Area",
                functions: ['response_generation'],
                position: { x: 120, y: 150 },
                size: 25,
                activation: 0
            },
            wernickesArea: {
                name: "Wernicke's Area",
                functions: ['query_comprehension'],
                position: { x: 280, y: 150 },
                size: 25,
                activation: 0
            },
            anteriorCingulate: {
                name: 'Anterior Cingulate',
                functions: ['confidence', 'attention', 'conflict_resolution'],
                position: { x: 200, y: 140 },
                size: 30,
                activation: 0
            },
            defaultModeNetwork: {
                name: 'Default Mode Network',
                functions: ['flow_states', 'background_processing'],
                position: { x: 250, y: 100 },
                size: 50,
                activation: 0
            },
            dopaminePathways: {
                name: 'Dopamine Pathways',
                functions: ['motivation', 'reward_processing'],
                position: { x: 200, y: 280 },
                size: 20,
                activation: 0
            }
        };
    }
    
    /**
     * @landmark Layout: Create main container structure
     */
    createLayout() {
        this.container.innerHTML = `
            <div class="cognition__header">
                <h3 class="cognition__title">Cognition</h3>
                <div class="cognition__ci-selector">
                    <label>CI:</label>
                    <select id="cognition-ci-select" class="cognition__select">
                        <option value="all">All CIs</option>
                        <option value="apollo" selected>Apollo</option>
                        <option value="athena">Athena</option>
                        <option value="hermes">Hermes</option>
                        <option value="zeus">Zeus</option>
                        <option value="diana">Diana</option>
                    </select>
                </div>
            </div>
            
            <div class="cognition__main">
                <div class="cognition__brain-container">
                    <svg id="cognition-brain-svg" width="400" height="350"></svg>
                </div>
                
                <div class="cognition__controls">
                    <div class="cognition__metrics">
                        <h4>Metrics</h4>
                        <div class="cognition__metric-buttons"></div>
                    </div>
                    
                    <div class="cognition__regions">
                        <h4>Regions</h4>
                        <div class="cognition__region-buttons"></div>
                    </div>
                </div>
            </div>
            
            <div class="cognition__timeline-container">
                <div class="cognition__timeline">
                    <input type="range" id="cognition-timeline" min="0" max="3600" value="3600" />
                    <div class="cognition__timeline-labels">
                        <span>1hr ago</span>
                        <span id="cognition-time-current">Now</span>
                    </div>
                </div>
                <div class="cognition__playback">
                    <button id="cognition-play">▶</button>
                    <button id="cognition-pause">⏸</button>
                    <select id="cognition-speed">
                        <option value="0.1">0.1x</option>
                        <option value="0.5">0.5x</option>
                        <option value="1" selected>1x</option>
                        <option value="2">2x</option>
                        <option value="5">5x</option>
                        <option value="10">10x</option>
                    </select>
                </div>
            </div>
            
            <div class="cognition__activity">
                <h4>Activity Feed</h4>
                <div id="cognition-activity-feed" class="cognition__feed"></div>
            </div>
        `;
        
        // Add event listeners
        document.getElementById('cognition-ci-select').addEventListener('change', (e) => {
            this.selectedCI = e.target.value;
            this.updateVisualization();
        });
        
        document.getElementById('cognition-timeline').addEventListener('input', (e) => {
            this.handleTimelineChange(e.target.value);
        });
        
        document.getElementById('cognition-play').addEventListener('click', () => {
            this.startPlayback();
        });
        
        document.getElementById('cognition-pause').addEventListener('click', () => {
            this.pausePlayback();
        });
        
        document.getElementById('cognition-speed').addEventListener('change', (e) => {
            this.playbackSpeed = parseFloat(e.target.value);
        });
    }
    
    /**
     * @landmark Brain SVG: Create D3.js brain visualization
     */
    createBrainSVG() {
        const svg = d3.select('#cognition-brain-svg');
        
        // Create gradient definitions for different activation states
        const defs = svg.append('defs');
        
        // High activation - red/orange
        const highGradient = defs.append('radialGradient')
            .attr('id', 'high-gradient');
        highGradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', '#FF6B6B');
        highGradient.append('stop')
            .attr('offset', '50%')
            .attr('stop-color', '#FF4444');
        highGradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', '#CC0000')
            .attr('stop-opacity', 0.3);
        
        // Medium activation - yellow/green
        const medGradient = defs.append('radialGradient')
            .attr('id', 'med-gradient');
        medGradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', '#FFD93D');
        medGradient.append('stop')
            .attr('offset', '50%')
            .attr('stop-color', '#6BCF7C');
        medGradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', '#4CAF50')
            .attr('stop-opacity', 0.3);
        
        // Low activation - blue/purple
        const lowGradient = defs.append('radialGradient')
            .attr('id', 'low-gradient');
        lowGradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', '#6B9EFF');
        lowGradient.append('stop')
            .attr('offset', '50%')
            .attr('stop-color', '#4444FF');
        lowGradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', '#9C27B0')
            .attr('stop-opacity', 0.3);
        
        // Draw brain outline (lateral view of cranium/skull)
        // This represents the skull outline containing the brain
        const brainOutline = svg.append('path')
            .attr('d', 'M 100 150 Q 100 50, 200 30 Q 300 50, 320 150 Q 300 250, 200 320 Q 100 250, 100 150')
            .attr('fill', 'none')  // Transparent fill to show regions inside
            .attr('stroke', '#666')
            .attr('stroke-width', 2)
            .attr('opacity', 0.9);
        
        // Add brain tissue background
        const brainTissue = svg.append('path')
            .attr('d', 'M 110 150 Q 110 60, 200 40 Q 290 60, 310 150 Q 290 240, 200 310 Q 110 240, 110 150')
            .attr('fill', '#2a2a3a')  // Slightly lighter than background
            .attr('opacity', 0.5);
        
        // Create region groups
        const regions = svg.selectAll('.brain-region')
            .data(Object.entries(this.brainRegions))
            .enter()
            .append('g')
            .attr('class', 'brain-region')
            .attr('id', d => `region-${d[0]}`);
        
        // Add region circles
        regions.append('circle')
            .attr('cx', d => d[1].position.x)
            .attr('cy', d => d[1].position.y)
            .attr('r', d => d[1].size)
            .attr('fill', '#444')
            .attr('stroke', '#666')
            .attr('stroke-width', 1)
            .attr('opacity', 0.6)
            .on('mouseover', (event, d) => this.showRegionTooltip(event, d))
            .on('mouseout', () => this.hideTooltip())
            .on('click', (event, d) => this.handleRegionClick(d));
        
        // Add region activation overlays
        regions.append('circle')
            .attr('class', 'activation-overlay')
            .attr('cx', d => d[1].position.x)
            .attr('cy', d => d[1].position.y)
            .attr('r', d => d[1].size)
            .attr('fill', 'url(#heat-gradient)')
            .attr('opacity', 0);
        
        // Add connection lines (will be animated)
        this.connectionLines = svg.append('g')
            .attr('class', 'connections');
    }
    
    /**
     * @landmark Controls: Create metric and region toggle buttons
     */
    createControls() {
        // Metric buttons
        const metrics = [
            { id: 'mood', label: 'Mood' },
            { id: 'working_memory', label: 'Working Memory' },
            { id: 'stress', label: 'Stress' },
            { id: 'processing', label: 'Processing' },
            { id: 'flow', label: 'Flow' },
            { id: 'confidence', label: 'Confidence' },
            { id: 'motivation', label: 'Motivation' },
            { id: 'associations', label: 'Associations' },
            { id: 'recall', label: 'Recall' },
            { id: 'forethought', label: 'Forethought' },
            { id: 'performance', label: 'Performance' }
        ];
        
        const metricContainer = document.querySelector('.cognition__metric-buttons');
        metrics.forEach(metric => {
            const button = document.createElement('button');
            button.className = 'cognition__toggle';
            button.dataset.metric = metric.id;
            button.textContent = metric.label;
            button.classList.toggle('active', this.activeMetrics.has(metric.id));
            
            button.addEventListener('click', () => {
                if (this.activeMetrics.has(metric.id)) {
                    this.activeMetrics.delete(metric.id);
                    button.classList.remove('active');
                } else {
                    this.activeMetrics.add(metric.id);
                    button.classList.add('active');
                }
                this.updateVisualization();
            });
            
            metricContainer.appendChild(button);
        });
        
        // Region filter buttons
        const regionFilters = [
            { id: 'all', label: 'All' },
            { id: 'frontal', label: 'Frontal' },
            { id: 'temporal', label: 'Temporal' },
            { id: 'limbic', label: 'Limbic' },
            { id: 'motor', label: 'Motor' }
        ];
        
        const regionContainer = document.querySelector('.cognition__region-buttons');
        regionFilters.forEach(filter => {
            const button = document.createElement('button');
            button.className = 'cognition__toggle';
            button.dataset.region = filter.id;
            button.textContent = filter.label;
            if (filter.id === 'all') button.classList.add('active');
            
            button.addEventListener('click', () => {
                document.querySelectorAll('.cognition__region-buttons button').forEach(b => {
                    b.classList.remove('active');
                });
                button.classList.add('active');
                this.filterRegions(filter.id);
            });
            
            regionContainer.appendChild(button);
        });
    }
    
    /**
     * @landmark Timeline: Create timeline scrubber
     */
    createTimeline() {
        // Timeline markers for events
        const timeline = document.querySelector('.cognition__timeline');
        
        // Add event markers (sample data for now)
        const events = [
            { time: 600, type: 'consolidation', label: 'Memory Consolidation' },
            { time: 1800, type: 'emotional_peak', label: 'Emotional Peak' },
            { time: 2700, type: 'pattern', label: 'Pattern Detected' }
        ];
        
        events.forEach(event => {
            const marker = document.createElement('div');
            marker.className = `cognition__marker cognition__marker--${event.type}`;
            marker.style.left = `${(event.time / 3600) * 100}%`;
            marker.title = event.label;
            timeline.appendChild(marker);
        });
    }
    
    /**
     * @landmark Activity Feed: Create scrolling activity display
     */
    createActivityFeed() {
        // Will be populated by WebSocket events
        this.addActivityItem('System initialized', 'system');
    }
    
    /**
     * @landmark WebSocket: Connect to ESR Experience Layer
     */
    connectWebSocket() {
        const wsUrl = 'ws://localhost:8100/cognition/stream';
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('Cognition WebSocket connected');
                this.addActivityItem('Connected to ESR Experience Layer', 'success');
                this.sendWebSocketMessage({
                    action: 'subscribe',
                    ci: this.selectedCI,
                    metrics: Array.from(this.activeMetrics)
                });
            };
            
            this.ws.onmessage = (event) => {
                this.handleWebSocketMessage(event);
            };
            
            this.ws.onerror = (error) => {
                console.error('Cognition WebSocket error:', error);
                this.addActivityItem('Connection error', 'error');
            };
            
            this.ws.onclose = () => {
                console.log('Cognition WebSocket closed');
                this.addActivityItem('Connection lost, retrying...', 'warning');
                setTimeout(() => this.connectWebSocket(), 5000);
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.addActivityItem('WebSocket connection failed', 'error');
        }
    }
    
    /**
     * @landmark Message Handler: Process WebSocket messages
     */
    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'region_activation':
                    this.updateRegionActivation(data.region, data.activation);
                    break;
                    
                case 'thought_flow':
                    this.showThoughtFlow(data.from, data.to, data.thought);
                    break;
                    
                case 'consolidation':
                    this.showConsolidation(data.memories);
                    break;
                    
                case 'emotional_state':
                    this.updateEmotionalState(data.emotion);
                    break;
                    
                case 'pattern_detected':
                    this.highlightPattern(data.pattern);
                    break;
                    
                case 'metrics_update':
                    this.updateMetrics(data.metrics);
                    break;
            }
        } catch (error) {
            console.error('Error handling WebSocket message:', error);
        }
    }
    
    /**
     * @landmark Update Visualization: Refresh brain display
     */
    updateVisualization() {
        // Update region activations based on active metrics
        Object.entries(this.brainRegions).forEach(([key, region]) => {
            let activation = 0;
            
            region.functions.forEach(func => {
                if (this.activeMetrics.has(func)) {
                    activation = Math.max(activation, this.getActivationLevel(func));
                }
            });
            
            this.updateRegionActivation(key, activation);
        });
    }
    
    /**
     * @landmark Region Activation: Update heat map for specific region
     */
    updateRegionActivation(regionKey, level) {
        const region = this.brainRegions[regionKey];
        if (!region) return;
        
        region.activation = level;
        
        // Update visualization
        const regionGroup = d3.select(`#region-${regionKey}`);
        
        // Update activation overlay
        regionGroup.select('.activation-overlay')
            .transition()
            .duration(200)
            .attr('opacity', level)
            .attr('fill', this.getHeatColor(level));
        
        // Add pulsing effect for high activation
        if (level > 0.7) {
            regionGroup.select('.activation-overlay')
                .attr('r', region.size)
                .transition()
                .duration(500)
                .attr('r', region.size * 1.2)
                .transition()
                .duration(500)
                .attr('r', region.size)
                .on('end', function repeat() {
                    if (region.activation > 0.7) {
                        d3.select(this)
                            .transition()
                            .duration(500)
                            .attr('r', region.size * 1.2)
                            .transition()
                            .duration(500)
                            .attr('r', region.size)
                            .on('end', repeat);
                    }
                });
        }
    }
    
    /**
     * @landmark Thought Flow: Animate thought movement between regions
     */
    showThoughtFlow(fromRegion, toRegion, thought) {
        const from = this.brainRegions[fromRegion];
        const to = this.brainRegions[toRegion];
        if (!from || !to) return;
        
        // Create particle
        const svg = d3.select('#cognition-brain-svg');
        const particle = svg.append('circle')
            .attr('class', 'thought-particle')
            .attr('cx', from.position.x)
            .attr('cy', from.position.y)
            .attr('r', 3)
            .attr('fill', '#00BCD4')
            .attr('opacity', 0.8);
        
        // Animate movement
        particle.transition()
            .duration(1000)
            .attr('cx', to.position.x)
            .attr('cy', to.position.y)
            .on('end', function() {
                d3.select(this).remove();
            });
        
        // Add to activity feed
        this.addActivityItem(`Thought: "${thought}" → ${to.name}`, 'thought');
    }
    
    /**
     * @landmark Helper: Get heat gradient based on activation level
     */
    getHeatColor(level) {
        if (level > 0.7) return 'url(#high-gradient)';
        if (level > 0.4) return 'url(#med-gradient)';
        return 'url(#low-gradient)';
    }
    
    /**
     * @landmark Helper: Get activation level for metric
     */
    getActivationLevel(metric) {
        // Return stored activation level for this metric
        return this.regionActivations[metric] || 0;
    }
    
    /**
     * @landmark Activity Feed: Add item to feed
     */
    addActivityItem(text, type = 'info') {
        const feed = document.getElementById('cognition-activity-feed');
        const item = document.createElement('div');
        item.className = `cognition__feed-item cognition__feed-item--${type}`;
        
        const time = new Date().toLocaleTimeString();
        item.innerHTML = `<span class="time">${time}</span> ${text}`;
        
        feed.insertBefore(item, feed.firstChild);
        
        // Keep only last 10 items
        while (feed.children.length > 10) {
            feed.removeChild(feed.lastChild);
        }
    }
    
    
    /**
     * @landmark Animation Loop: Continuous visual updates
     */
    startAnimationLoop() {
        const animate = () => {
            // Update any continuous animations
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }
    
    /**
     * @landmark WebSocket Helper: Send message
     */
    sendWebSocketMessage(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }
    
    /**
     * @landmark Timeline Control: Handle timeline changes
     */
    handleTimelineChange(value) {
        const secondsAgo = 3600 - value;
        const timeLabel = secondsAgo === 0 ? 'Now' : `${Math.floor(secondsAgo / 60)} min ago`;
        document.getElementById('cognition-time-current').textContent = timeLabel;
        
        if (secondsAgo > 0) {
            this.timeMode = Date.now() - (secondsAgo * 1000);
            this.loadHistoricalData(this.timeMode);
        } else {
            this.timeMode = 'live';
        }
    }
    
    /**
     * @landmark Playback: Start historical playback
     */
    startPlayback() {
        // Implement playback logic
        this.addActivityItem('Starting playback...', 'system');
    }
    
    /**
     * @landmark Playback: Pause playback
     */
    pausePlayback() {
        // Implement pause logic
        this.addActivityItem('Playback paused', 'system');
    }
    
    /**
     * @landmark Region Click: Handle region selection
     */
    handleRegionClick(regionData) {
        const [key, region] = regionData;
        this.addActivityItem(`Selected: ${region.name}`, 'info');
        // Could show detailed metrics for this region
    }
    
    /**
     * @landmark Tooltip: Show region information
     */
    showRegionTooltip(event, regionData) {
        const [key, region] = regionData;
        // Implement tooltip display
    }
    
    /**
     * @landmark Tooltip: Hide tooltip
     */
    hideTooltip() {
        // Implement tooltip hiding
    }
    
    /**
     * @landmark Filter: Filter visible regions
     */
    filterRegions(filter) {
        // Implement region filtering
        this.addActivityItem(`Filtering: ${filter} regions`, 'info');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Check if we're in the cognition panel
        if (document.getElementById('cognition-panel')) {
            window.cognitionBrain = new CognitionBrainVisualization('cognition-panel');
        }
    });
} else {
    // Check if we're in the cognition panel
    if (document.getElementById('cognition-panel')) {
        window.cognitionBrain = new CognitionBrainVisualization('cognition-panel');
    }
}

// Export for use in other components
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CognitionBrainVisualization;
}