/**
 * Catastrophe Analyzer for Noesis Dashboard
 * Creates visualizations for catastrophe theory analysis and phase transitions
 */

class CatastropheAnalyzer {
    constructor() {
        this.data = null;
        this.bifurcationDiagram = null;
        this.controlParameterSpace = null;
        this.charts = {};
        this.isInitialized = false;
        
        console.log('🔱 Catastrophe Analyzer initialized');
    }
    
    async init() {
        try {
            this.setupBifurcationDiagram();
            this.setupControlParameterSpace();
            this.setupTransitionTimeline();
            this.setupCatastropheClassification();
            this.isInitialized = true;
            console.log('✅ Catastrophe Analyzer ready');
        } catch (error) {
            console.error('❌ Catastrophe Analyzer initialization failed:', error);
            throw error;
        }
    }
    
    setupBifurcationDiagram() {
        const container = document.getElementById('bifurcation-diagram');
        if (!container) return;
        
        container.innerHTML = '';
        
        const width = container.clientWidth || 400;
        const height = container.clientHeight || 300;
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .style('background', '#f8fafc')
            .style('border-radius', '8px');
        
        this.bifurcationGroups = {
            background: svg.append('g').attr('class', 'background'),
            branches: svg.append('g').attr('class', 'branches'),
            points: svg.append('g').attr('class', 'bifurcation-points'),
            annotations: svg.append('g').attr('class', 'annotations')
        };
        
        this.bifurcationDimensions = { width, height };
        this.bifurcationDiagram = svg;
    }
    
    setupControlParameterSpace() {
        const container = document.getElementById('control-parameter-space');
        if (!container) return;
        
        container.innerHTML = '';
        
        const width = container.clientWidth || 300;
        const height = container.clientHeight || 200;
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .style('background', '#f8fafc')
            .style('border-radius', '8px');
        
        this.controlSpaceGroups = {
            regions: svg.append('g').attr('class', 'stability-regions'),
            boundaries: svg.append('g').attr('class', 'critical-boundaries'),
            currentPoint: svg.append('g').attr('class', 'current-state')
        };
        
        this.controlSpaceDimensions = { width, height };
        this.controlParameterSpace = svg;
    }
    
    setupTransitionTimeline() {
        const ctx = document.getElementById('transition-timeline-chart');
        if (!ctx) return;
        
        this.charts.transitionTimeline = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Phase Transitions',
                    data: [],
                    backgroundColor: 'rgba(239, 68, 68, 0.6)',
                    borderColor: '#ef4444',
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    showLine: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
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
                        title: {
                            display: true,
                            text: 'Transition Magnitude'
                        },
                        min: 0,
                        max: 1
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const point = context.raw;
                                return `Transition: ${point.magnitude?.toFixed(3)} at ${new Date(point.x).toLocaleTimeString()}`;
                            }
                        }
                    }
                },
                onClick: (event, elements) => {
                    if (elements.length > 0) {
                        const element = elements[0];
                        const dataPoint = this.charts.transitionTimeline.data.datasets[0].data[element.index];
                        this.showTransitionDetails(dataPoint);
                    }
                }
            }
        });
    }
    
    setupCatastropheClassification() {
        const container = document.getElementById('catastrophe-types');
        if (!container) return;
        
        container.innerHTML = '<p class="text-muted">Analyzing catastrophe types...</p>';
    }
    
    updateData(analysisData) {
        if (!this.isInitialized || !analysisData) return;
        
        this.data = analysisData;
        
        try {
            this.updateBifurcationVisualization();
            this.updateControlParameterVisualization();
            this.updatePhaseTransitions();
            this.updateCatastropheClassification();
            
            console.log('🔱 Catastrophe analysis updated');
        } catch (error) {
            console.error('Failed to update catastrophe analysis:', error);
        }
    }
    
    updateBifurcationVisualization() {
        if (!this.bifurcationDiagram || !this.data) return;
        
        // Clear previous visualization
        Object.values(this.bifurcationGroups).forEach(group => {
            group.selectAll('*').remove();
        });
        
        const { width, height } = this.bifurcationDimensions;
        const analysisResults = this.data.data || {};
        
        // Set up scales
        const xScale = d3.scaleLinear()
            .domain([0, 4]) // Control parameter range
            .range([50, width - 50]);
        
        const yScale = d3.scaleLinear()
            .domain([-2, 2]) // State variable range
            .range([height - 50, 50]);
        
        // Draw axes
        this.drawBifurcationAxes(xScale, yScale);
        
        // Generate and draw bifurcation branches
        const bifurcationData = this.generateBifurcationData(analysisResults);
        this.drawBifurcationBranches(bifurcationData, xScale, yScale);
        
        // Mark bifurcation points
        this.drawBifurcationPoints(bifurcationData.bifurcationPoints, xScale, yScale);
    }
    
    drawBifurcationAxes(xScale, yScale) {
        const axesGroup = this.bifurcationGroups.annotations;
        
        // X axis (control parameter)
        axesGroup.append('line')
            .attr('x1', xScale(0))
            .attr('x2', xScale(4))
            .attr('y1', yScale(0))
            .attr('y2', yScale(0))
            .attr('stroke', '#64748b')
            .attr('stroke-width', 1);
        
        // Y axis (state variable)
        axesGroup.append('line')
            .attr('x1', xScale(0))
            .attr('x2', xScale(0))
            .attr('y1', yScale(-2))
            .attr('y2', yScale(2))
            .attr('stroke', '#64748b')
            .attr('stroke-width', 1);
        
        // Axis labels
        axesGroup.append('text')
            .attr('x', xScale(4) - 5)
            .attr('y', yScale(0) - 5)
            .attr('text-anchor', 'end')
            .attr('font-size', '12px')
            .attr('fill', '#64748b')
            .text('Control Parameter (μ)');
        
        axesGroup.append('text')
            .attr('x', xScale(0) + 5)
            .attr('y', yScale(2) + 5)
            .attr('font-size', '12px')
            .attr('fill', '#64748b')
            .text('State (x)');
    }
    
    generateBifurcationData(results) {
        const data = {
            stableBranch: [],
            unstableBranch: [],
            upperBranch: [],
            lowerBranch: [],
            bifurcationPoints: []
        };
        
        const numPoints = 200;
        const bifurcationParam = results.bifurcation_parameter || 2.0;
        
        for (let i = 0; i < numPoints; i++) {
            const mu = (i / numPoints) * 4; // Control parameter
            
            if (mu < bifurcationParam) {
                // Before bifurcation - single stable branch
                const x = Math.sqrt(Math.max(0, mu - 1));
                data.stableBranch.push({ mu, x });
                data.stableBranch.push({ mu, x: -x });
            } else {
                // After bifurcation - multiple branches
                const delta = mu - bifurcationParam;
                const x1 = Math.sqrt(delta) + 0.5;
                const x2 = -Math.sqrt(delta) - 0.5;
                
                data.upperBranch.push({ mu, x: x1 });
                data.lowerBranch.push({ mu, x: x2 });
                
                // Unstable branch
                data.unstableBranch.push({ mu, x: 0 });
            }
        }
        
        // Mark bifurcation points
        data.bifurcationPoints = [
            { mu: bifurcationParam, x: 0, type: 'pitchfork' },
            { mu: bifurcationParam + 1, x: 1, type: 'saddle-node' }
        ];
        
        return data;
    }
    
    drawBifurcationBranches(data, xScale, yScale) {
        const branchesGroup = this.bifurcationGroups.branches;
        
        const line = d3.line()
            .x(d => xScale(d.mu))
            .y(d => yScale(d.x))
            .curve(d3.curveCardinal);
        
        // Draw stable branches
        if (data.stableBranch.length > 0) {
            branchesGroup.append('path')
                .datum(data.stableBranch)
                .attr('d', line)
                .attr('fill', 'none')
                .attr('stroke', '#10b981')
                .attr('stroke-width', 3)
                .attr('opacity', 0.8);
        }
        
        // Draw unstable branch
        if (data.unstableBranch.length > 0) {
            branchesGroup.append('path')
                .datum(data.unstableBranch)
                .attr('d', line)
                .attr('fill', 'none')
                .attr('stroke', '#ef4444')
                .attr('stroke-width', 2)
                .attr('stroke-dasharray', '5,5')
                .attr('opacity', 0.6);
        }
        
        // Draw upper and lower branches
        [data.upperBranch, data.lowerBranch].forEach((branch, index) => {
            if (branch.length > 0) {
                branchesGroup.append('path')
                    .datum(branch)
                    .attr('d', line)
                    .attr('fill', 'none')
                    .attr('stroke', '#3b82f6')
                    .attr('stroke-width', 3)
                    .attr('opacity', 0.8);
            }
        });
    }
    
    drawBifurcationPoints(points, xScale, yScale) {
        const pointsGroup = this.bifurcationGroups.points;
        
        points.forEach(point => {
            const color = point.type === 'pitchfork' ? '#7c3aed' : '#f59e0b';
            
            pointsGroup.append('circle')
                .attr('cx', xScale(point.mu))
                .attr('cy', yScale(point.x))
                .attr('r', 6)
                .attr('fill', color)
                .attr('stroke', '#ffffff')
                .attr('stroke-width', 2)
                .append('title')
                .text(`${point.type} bifurcation at μ=${point.mu.toFixed(2)}`);
        });
    }
    
    updateControlParameterVisualization() {
        if (!this.controlParameterSpace || !this.data) return;
        
        // Clear previous visualization
        Object.values(this.controlSpaceGroups).forEach(group => {
            group.selectAll('*').remove();
        });
        
        const { width, height } = this.controlSpaceDimensions;
        
        // Draw stability regions
        this.drawStabilityRegions(width, height);
        
        // Draw critical boundaries
        this.drawCriticalBoundaries(width, height);
        
        // Mark current system state
        this.drawCurrentState(width, height);
    }
    
    drawStabilityRegions(width, height) {
        const regionsGroup = this.controlSpaceGroups.regions;
        
        // Define regions in parameter space
        const regions = [
            { x: 0, y: 0, width: width * 0.3, height: height * 0.5, 
              color: '#10b981', opacity: 0.3, label: 'Stable' },
            { x: width * 0.3, y: 0, width: width * 0.4, height: height * 0.5, 
              color: '#f59e0b', opacity: 0.3, label: 'Bistable' },
            { x: width * 0.7, y: 0, width: width * 0.3, height: height * 0.5, 
              color: '#ef4444', opacity: 0.3, label: 'Chaotic' },
            { x: 0, y: height * 0.5, width: width, height: height * 0.5, 
              color: '#7c3aed', opacity: 0.2, label: 'Critical' }
        ];
        
        regions.forEach(region => {
            regionsGroup.append('rect')
                .attr('x', region.x)
                .attr('y', region.y)
                .attr('width', region.width)
                .attr('height', region.height)
                .attr('fill', region.color)
                .attr('opacity', region.opacity);
            
            // Add region label
            regionsGroup.append('text')
                .attr('x', region.x + region.width / 2)
                .attr('y', region.y + region.height / 2)
                .attr('text-anchor', 'middle')
                .attr('font-size', '12px')
                .attr('font-weight', 'bold')
                .attr('fill', region.color)
                .text(region.label);
        });
    }
    
    drawCriticalBoundaries(width, height) {
        const boundariesGroup = this.controlSpaceGroups.boundaries;
        
        // Vertical boundaries
        [width * 0.3, width * 0.7].forEach(x => {
            boundariesGroup.append('line')
                .attr('x1', x)
                .attr('x2', x)
                .attr('y1', 0)
                .attr('y2', height)
                .attr('stroke', '#64748b')
                .attr('stroke-width', 2)
                .attr('stroke-dasharray', '3,3')
                .attr('opacity', 0.7);
        });
        
        // Horizontal boundary
        boundariesGroup.append('line')
            .attr('x1', 0)
            .attr('x2', width)
            .attr('y1', height * 0.5)
            .attr('y2', height * 0.5)
            .attr('stroke', '#64748b')
            .attr('stroke-width', 2)
            .attr('stroke-dasharray', '3,3')
            .attr('opacity', 0.7);
        
        // Add axis labels
        boundariesGroup.append('text')
            .attr('x', width - 5)
            .attr('y', height - 5)
            .attr('text-anchor', 'end')
            .attr('font-size', '10px')
            .attr('fill', '#64748b')
            .text('Parameter 1');
        
        boundariesGroup.append('text')
            .attr('x', 5)
            .attr('y', 15)
            .attr('font-size', '10px')
            .attr('fill', '#64748b')
            .text('Parameter 2');
    }
    
    drawCurrentState(width, height) {
        const currentGroup = this.controlSpaceGroups.currentPoint;
        
        // Simulate current system position in parameter space
        const currentX = width * (0.4 + Math.random() * 0.2);
        const currentY = height * (0.3 + Math.random() * 0.4);
        
        currentGroup.append('circle')
            .attr('cx', currentX)
            .attr('cy', currentY)
            .attr('r', 8)
            .attr('fill', '#3b82f6')
            .attr('stroke', '#ffffff')
            .attr('stroke-width', 3)
            .attr('opacity', 0.9);
        
        // Add pulsing animation
        currentGroup.select('circle')
            .append('animate')
            .attr('attributeName', 'r')
            .attr('values', '8;12;8')
            .attr('dur', '2s')
            .attr('repeatCount', 'indefinite');
        
        currentGroup.append('text')
            .attr('x', currentX + 15)
            .attr('y', currentY + 5)
            .attr('font-size', '12px')
            .attr('font-weight', 'bold')
            .attr('fill', '#3b82f6')
            .text('Current State');
    }
    
    updatePhaseTransitions() {
        if (!this.charts.transitionTimeline || !this.data) return;
        
        // Generate synthetic phase transition data
        const transitions = this.generatePhaseTransitions();
        
        this.charts.transitionTimeline.data.datasets[0].data = transitions;
        this.charts.transitionTimeline.update('none');
        
        // Update transition list
        this.updateTransitionList(transitions);
    }
    
    generatePhaseTransitions() {
        const transitions = [];
        const now = new Date();
        const analysisResults = this.data.data || {};
        const numTransitions = analysisResults.phase_transitions?.length || Math.floor(Math.random() * 5) + 1;
        
        for (let i = 0; i < numTransitions; i++) {
            const timeAgo = Math.random() * 60 * 60 * 1000; // Within last hour
            const transitionTime = new Date(now.getTime() - timeAgo);
            
            transitions.push({
                x: transitionTime,
                y: Math.random(),
                magnitude: Math.random(),
                type: this.getRandomTransitionType(),
                description: this.generateTransitionDescription()
            });
        }
        
        return transitions.sort((a, b) => a.x - b.x);
    }
    
    getRandomTransitionType() {
        const types = ['fold', 'cusp', 'swallowtail', 'butterfly', 'hyperbolic', 'elliptic'];
        return types[Math.floor(Math.random() * types.length)];
    }
    
    generateTransitionDescription() {
        const descriptions = [
            'Memory state underwent rapid reorganization',
            'Critical threshold crossed in collective processing',
            'Sudden shift in thought state distribution',
            'Emergence of new cognitive pattern',
            'Collapse of unstable memory configuration'
        ];
        return descriptions[Math.floor(Math.random() * descriptions.length)];
    }
    
    updateTransitionList(transitions) {
        const container = document.getElementById('transition-list');
        if (!container) return;
        
        if (transitions.length === 0) {
            container.innerHTML = '<p class="text-muted">No phase transitions detected</p>';
            return;
        }
        
        const html = transitions
            .sort((a, b) => b.x - a.x) // Most recent first
            .slice(0, 5) // Show last 5
            .map(transition => this.renderTransitionItem(transition))
            .join('');
        
        container.innerHTML = html;
    }
    
    renderTransitionItem(transition) {
        const time = transition.x.toLocaleTimeString();
        const magnitude = (transition.magnitude * 100).toFixed(1);
        
        return `
            <div class="transition-item">
                <div class="transition-header">
                    <span class="transition-type">${transition.type.charAt(0).toUpperCase() + transition.type.slice(1)} Transition</span>
                    <span class="transition-time">${time}</span>
                </div>
                <div class="transition-magnitude">Magnitude: ${magnitude}%</div>
                <div class="transition-description">${transition.description}</div>
            </div>
        `;
    }
    
    showTransitionDetails(transition) {
        // Could open a modal or expand details inline
        console.log('Transition details:', transition);
    }
    
    updateCatastropheClassification() {
        if (!this.data) return;
        
        const container = document.getElementById('catastrophe-types');
        if (!container) return;
        
        const analysisResults = this.data.data || {};
        const classifications = this.generateCatastropheClassifications(analysisResults);
        
        const html = classifications.map(classification => `
            <div class="catastrophe-type-item">
                <div class="catastrophe-header">
                    <span class="catastrophe-name">${classification.name}</span>
                    <span class="catastrophe-probability">${(classification.probability * 100).toFixed(1)}%</span>
                </div>
                <div class="catastrophe-description">${classification.description}</div>
                <div class="catastrophe-indicators">
                    ${classification.indicators.map(ind => `<span class="indicator">${ind}</span>`).join('')}
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    generateCatastropheClassifications(results) {
        const classifications = [
            {
                name: 'Fold Catastrophe',
                probability: Math.random() * 0.4 + 0.1,
                description: 'Simple threshold crossing leading to sudden state change',
                indicators: ['Gradual approach', 'Sudden jump', 'Hysteresis']
            },
            {
                name: 'Cusp Catastrophe',
                probability: Math.random() * 0.6 + 0.2,
                description: 'Bimodal behavior with possible sudden transitions',
                indicators: ['Bimodality', 'Sudden jumps', 'Divergence']
            },
            {
                name: 'Butterfly Catastrophe',
                probability: Math.random() * 0.3 + 0.05,
                description: 'Complex multi-modal behavior with multiple stable states',
                indicators: ['Multiple modes', 'Pocket formation', 'Complex dynamics']
            }
        ];
        
        // Adjust probabilities based on analysis results
        if (results.bifurcations && results.bifurcations.length > 0) {
            classifications[1].probability *= 1.5; // Increase cusp probability
        }
        
        return classifications.sort((a, b) => b.probability - a.probability);
    }
    
    refresh() {
        if (!this.isInitialized) return;
        
        if (this.data) {
            this.updateBifurcationVisualization();
            this.updateControlParameterVisualization();
        }
        
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.update === 'function') {
                chart.update();
            }
        });
        
        console.log('🔄 Catastrophe analysis refreshed');
    }
    
    cleanup() {
        if (this.bifurcationDiagram) {
            this.bifurcationDiagram.selectAll('*').remove();
        }
        
        if (this.controlParameterSpace) {
            this.controlParameterSpace.selectAll('*').remove();
        }
        
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        this.charts = {};
        this.data = null;
        this.isInitialized = false;
        
        console.log('🧹 Catastrophe Analyzer cleanup completed');
    }
}

export { CatastropheAnalyzer };