/**
 * Dynamics Visualizer for Noesis Dashboard
 * Creates visualizations for dynamical systems analysis
 */

class DynamicsVisualizer {
    constructor() {
        this.data = null;
        this.phaseSpacePlot = null;
        this.flowField = null;
        this.charts = {};
        this.isInitialized = false;
        
        console.log('🌊 Dynamics Visualizer initialized');
    }
    
    async init() {
        try {
            this.setupPhaseSpacePlot();
            this.setupFlowField();
            this.setupAttractorCharts();
            this.setupLyapunovChart();
            this.isInitialized = true;
            console.log('✅ Dynamics Visualizer ready');
        } catch (error) {
            console.error('❌ Dynamics Visualizer initialization failed:', error);
            throw error;
        }
    }
    
    setupPhaseSpacePlot() {
        const container = document.getElementById('phase-space-plot');
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
        
        this.phaseSpaceGroups = {
            trajectories: svg.append('g').attr('class', 'trajectories'),
            attractors: svg.append('g').attr('class', 'attractors'),
            vectors: svg.append('g').attr('class', 'vectors'),
            axes: svg.append('g').attr('class', 'axes')
        };
        
        this.phaseSpaceDimensions = { width, height };
        this.phaseSpacePlot = svg;
    }
    
    setupFlowField() {
        const container = document.getElementById('flow-field');
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
        
        this.flowFieldGroups = {
            vectors: svg.append('g').attr('class', 'flow-vectors'),
            streamlines: svg.append('g').attr('class', 'streamlines')
        };
        
        this.flowFieldDimensions = { width, height };
        this.flowField = svg;
    }
    
    setupAttractorCharts() {
        const basinCtx = document.getElementById('attractor-basin-chart');
        if (!basinCtx) return;
        
        this.charts.attractorBasin = new Chart(basinCtx, {
            type: 'scatter',
            data: {
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'State Dimension 1'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'State Dimension 2'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Basin ${context.datasetIndex + 1}: (${context.parsed.x.toFixed(2)}, ${context.parsed.y.toFixed(2)})`;
                            }
                        }
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
    
    setupLyapunovChart() {
        const ctx = document.getElementById('lyapunov-chart');
        if (!ctx) return;
        
        this.charts.lyapunov = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['λ₁', 'λ₂', 'λ₃', 'λ₄', 'λ₅'],
                datasets: [{
                    label: 'Lyapunov Exponents',
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: function(context) {
                        const value = context.parsed.y;
                        return value > 0 ? 'rgba(239, 68, 68, 0.6)' :   // Positive - red (chaotic)
                               value < -0.1 ? 'rgba(59, 130, 246, 0.6)' : // Negative - blue (stable)
                               'rgba(245, 158, 11, 0.6)';              // Near zero - amber (neutral)
                    },
                    borderColor: function(context) {
                        const value = context.parsed.y;
                        return value > 0 ? '#ef4444' :
                               value < -0.1 ? '#3b82f6' :
                               '#f59e0b';
                    },
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'Exponent Value'
                        },
                        grid: {
                            color: function(context) {
                                return context.tick.value === 0 ? '#64748b' : '#e2e8f0';
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Lyapunov Exponent'
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
                                const value = context.parsed.y;
                                const interpretation = value > 0 ? 'Chaotic' :
                                                     value < -0.1 ? 'Stable' : 'Neutral';
                                return `${context.label}: ${value.toFixed(4)} (${interpretation})`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    updateData(analysisData) {
        if (!this.isInitialized || !analysisData) return;
        
        this.data = analysisData;
        
        try {
            this.updateAttractorAnalysis();
            this.updatePhaseSpace();
            this.updateFlowVisualization();
            this.updateLyapunovExponents();
            
            console.log('🌊 Dynamics analysis updated');
        } catch (error) {
            console.error('Failed to update dynamics analysis:', error);
        }
    }
    
    updateAttractorAnalysis() {
        if (!this.data) return;
        
        const analysisResults = this.data.data || {};
        
        // Update attractor properties
        this.updateProperty('num-attractors', 
            analysisResults.num_attractors || 0
        );
        
        this.updateProperty('stability-index', 
            analysisResults.stability || 0,
            'stability units'
        );
        
        this.updateProperty('dominant-attractor', 
            analysisResults.dominant_attractor || 'None'
        );
        
        // Update attractor basin chart
        this.updateAttractorBasinChart(analysisResults);
    }
    
    updateProperty(elementId, value, unit = '') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        if (typeof value === 'number') {
            element.textContent = `${value.toFixed(3)} ${unit}`.trim();
        } else {
            element.textContent = value;
        }
    }
    
    updateAttractorBasinChart(results) {
        if (!this.charts.attractorBasin) return;
        
        // Generate synthetic attractor basin data
        const numAttractors = results.num_attractors || 2;
        const datasets = [];
        
        const colors = [
            '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#7c3aed'
        ];
        
        for (let i = 0; i < numAttractors; i++) {
            const data = this.generateAttractorBasinData(i, numAttractors);
            
            datasets.push({
                label: `Attractor ${i + 1}`,
                data: data,
                backgroundColor: colors[i % colors.length] + '80',
                borderColor: colors[i % colors.length],
                showLine: false
            });
        }
        
        this.charts.attractorBasin.data.datasets = datasets;
        this.charts.attractorBasin.update('none');
    }
    
    generateAttractorBasinData(attractorIndex, totalAttractors) {
        const data = [];
        const numPoints = 50;
        
        // Generate points in attractor basin
        for (let i = 0; i < numPoints; i++) {
            const angle = (i / numPoints) * 2 * Math.PI;
            const radius = 0.5 + Math.random() * 0.5;
            
            const centerX = (attractorIndex / totalAttractors) * 4 - 2;
            const centerY = Math.sin(attractorIndex * Math.PI) * 1.5;
            
            const x = centerX + radius * Math.cos(angle) + (Math.random() - 0.5) * 0.3;
            const y = centerY + radius * Math.sin(angle) + (Math.random() - 0.5) * 0.3;
            
            data.push({ x, y });
        }
        
        return data;
    }
    
    updatePhaseSpace() {
        if (!this.phaseSpacePlot || !this.data) return;
        
        // Clear previous visualization
        Object.values(this.phaseSpaceGroups).forEach(group => {
            group.selectAll('*').remove();
        });
        
        const { width, height } = this.phaseSpaceDimensions;
        const analysisResults = this.data.data || {};
        
        // Set up scales
        const xScale = d3.scaleLinear()
            .domain([-3, 3])
            .range([50, width - 50]);
        
        const yScale = d3.scaleLinear()
            .domain([-3, 3])
            .range([height - 50, 50]);
        
        // Draw axes
        this.drawPhaseSpaceAxes(xScale, yScale);
        
        // Generate and draw trajectories
        const trajectories = this.generateTrajectories(analysisResults);
        this.drawTrajectories(trajectories, xScale, yScale);
        
        // Draw attractors
        this.drawAttractors(analysisResults, xScale, yScale);
    }
    
    drawPhaseSpaceAxes(xScale, yScale) {
        const axesGroup = this.phaseSpaceGroups.axes;
        
        // X axis
        axesGroup.append('line')
            .attr('x1', xScale(-3))
            .attr('x2', xScale(3))
            .attr('y1', yScale(0))
            .attr('y2', yScale(0))
            .attr('stroke', '#64748b')
            .attr('stroke-width', 1);
        
        // Y axis
        axesGroup.append('line')
            .attr('x1', xScale(0))
            .attr('x2', xScale(0))
            .attr('y1', yScale(-3))
            .attr('y2', yScale(3))
            .attr('stroke', '#64748b')
            .attr('stroke-width', 1);
        
        // Axis labels
        axesGroup.append('text')
            .attr('x', xScale(3) - 5)
            .attr('y', yScale(0) - 5)
            .attr('text-anchor', 'end')
            .attr('font-size', '12px')
            .attr('fill', '#64748b')
            .text('State 1');
        
        axesGroup.append('text')
            .attr('x', xScale(0) + 5)
            .attr('y', yScale(3) + 5)
            .attr('font-size', '12px')
            .attr('fill', '#64748b')
            .text('State 2');
    }
    
    generateTrajectories(results) {
        const numTrajectories = 3;
        const trajectories = [];
        
        for (let i = 0; i < numTrajectories; i++) {
            const trajectory = [];
            let x = (Math.random() - 0.5) * 4;
            let y = (Math.random() - 0.5) * 4;
            
            // Simple dynamics simulation
            for (let t = 0; t < 100; t++) {
                trajectory.push({ x, y, t });
                
                // Simple attractor dynamics
                const dx = -0.1 * x + 0.05 * y + Math.sin(y) * 0.1;
                const dy = -0.1 * y - 0.05 * x + Math.cos(x) * 0.1;
                
                x += dx * 0.1;
                y += dy * 0.1;
                
                // Add some noise
                x += (Math.random() - 0.5) * 0.05;
                y += (Math.random() - 0.5) * 0.05;
            }
            
            trajectories.push(trajectory);
        }
        
        return trajectories;
    }
    
    drawTrajectories(trajectories, xScale, yScale) {
        const trajGroup = this.phaseSpaceGroups.trajectories;
        
        trajectories.forEach((trajectory, index) => {
            const line = d3.line()
                .x(d => xScale(d.x))
                .y(d => yScale(d.y))
                .curve(d3.curveCardinal);
            
            // Draw trajectory
            trajGroup.append('path')
                .datum(trajectory)
                .attr('d', line)
                .attr('fill', 'none')
                .attr('stroke', d3.schemeCategory10[index])
                .attr('stroke-width', 2)
                .attr('opacity', 0.7);
            
            // Draw start point
            const start = trajectory[0];
            trajGroup.append('circle')
                .attr('cx', xScale(start.x))
                .attr('cy', yScale(start.y))
                .attr('r', 4)
                .attr('fill', d3.schemeCategory10[index])
                .attr('stroke', '#ffffff')
                .attr('stroke-width', 2);
            
            // Draw end point with arrow
            const end = trajectory[trajectory.length - 1];
            trajGroup.append('circle')
                .attr('cx', xScale(end.x))
                .attr('cy', yScale(end.y))
                .attr('r', 3)
                .attr('fill', '#ffffff')
                .attr('stroke', d3.schemeCategory10[index])
                .attr('stroke-width', 2);
        });
    }
    
    drawAttractors(results, xScale, yScale) {
        const attractorGroup = this.phaseSpaceGroups.attractors;
        const numAttractors = results.num_attractors || 2;
        
        for (let i = 0; i < numAttractors; i++) {
            const x = (i / numAttractors) * 4 - 2;
            const y = Math.sin(i * Math.PI) * 1.5;
            
            // Draw attractor point
            attractorGroup.append('circle')
                .attr('cx', xScale(x))
                .attr('cy', yScale(y))
                .attr('r', 8)
                .attr('fill', 'none')
                .attr('stroke', '#ef4444')
                .attr('stroke-width', 3)
                .attr('opacity', 0.8);
            
            // Draw attractor basin outline
            attractorGroup.append('circle')
                .attr('cx', xScale(x))
                .attr('cy', yScale(y))
                .attr('r', 30)
                .attr('fill', 'none')
                .attr('stroke', '#ef4444')
                .attr('stroke-width', 1)
                .attr('stroke-dasharray', '5,5')
                .attr('opacity', 0.4);
        }
    }
    
    updateFlowVisualization() {
        if (!this.flowField || !this.data) return;
        
        // Clear previous visualization
        Object.values(this.flowFieldGroups).forEach(group => {
            group.selectAll('*').remove();
        });
        
        const { width, height } = this.flowFieldDimensions;
        
        // Draw flow vectors
        this.drawFlowVectors(width, height);
        
        // Draw streamlines
        this.drawStreamlines(width, height);
    }
    
    drawFlowVectors(width, height) {
        const vectorGroup = this.flowFieldGroups.vectors;
        const gridSize = 15;
        
        for (let i = 0; i < gridSize; i++) {
            for (let j = 0; j < gridSize; j++) {
                const x = (i / (gridSize - 1)) * width;
                const y = (j / (gridSize - 1)) * height;
                
                // Convert to state space coordinates
                const stateX = (x / width) * 6 - 3;
                const stateY = (y / height) * 6 - 3;
                
                // Calculate flow vector
                const dx = -0.1 * stateX + 0.05 * stateY;
                const dy = -0.1 * stateY - 0.05 * stateX;
                
                const magnitude = Math.sqrt(dx * dx + dy * dy);
                const scale = 15; // Arrow scale
                
                if (magnitude > 0.01) {
                    const endX = x + (dx / magnitude) * scale;
                    const endY = y + (dy / magnitude) * scale;
                    
                    // Draw arrow
                    vectorGroup.append('line')
                        .attr('x1', x)
                        .attr('y1', y)
                        .attr('x2', endX)
                        .attr('y2', endY)
                        .attr('stroke', '#7c3aed')
                        .attr('stroke-width', 1)
                        .attr('opacity', 0.7)
                        .attr('marker-end', 'url(#arrow)');
                }
            }
        }
        
        // Add arrow marker definition
        const defs = this.flowField.append('defs');
        const marker = defs.append('marker')
            .attr('id', 'arrow')
            .attr('viewBox', '0 0 10 10')
            .attr('refX', 8)
            .attr('refY', 3)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto');
        
        marker.append('path')
            .attr('d', 'M0,0 L0,6 L9,3 z')
            .attr('fill', '#7c3aed');
    }
    
    drawStreamlines(width, height) {
        const streamGroup = this.flowFieldGroups.streamlines;
        const numStreamlines = 5;
        
        for (let i = 0; i < numStreamlines; i++) {
            const startX = Math.random() * width;
            const startY = Math.random() * height;
            
            const streamline = this.generateStreamline(startX, startY, width, height);
            
            const line = d3.line()
                .x(d => d.x)
                .y(d => d.y)
                .curve(d3.curveCardinal);
            
            streamGroup.append('path')
                .datum(streamline)
                .attr('d', line)
                .attr('fill', 'none')
                .attr('stroke', '#10b981')
                .attr('stroke-width', 2)
                .attr('opacity', 0.5);
        }
    }
    
    generateStreamline(startX, startY, width, height) {
        const points = [];
        let x = startX;
        let y = startY;
        
        for (let step = 0; step < 50; step++) {
            points.push({ x, y });
            
            // Convert to state space
            const stateX = (x / width) * 6 - 3;
            const stateY = (y / height) * 6 - 3;
            
            // Calculate flow
            const dx = -0.1 * stateX + 0.05 * stateY;
            const dy = -0.1 * stateY - 0.05 * stateX;
            
            // Update position
            x += dx * 2;
            y += dy * 2;
            
            // Check bounds
            if (x < 0 || x > width || y < 0 || y > height) break;
        }
        
        return points;
    }
    
    updateLyapunovExponents() {
        if (!this.charts.lyapunov || !this.data) return;
        
        // Generate synthetic Lyapunov exponents
        const analysisResults = this.data.data || {};
        const stability = analysisResults.stability || 0.5;
        
        // Generate exponents based on stability
        const exponents = [];
        for (let i = 0; i < 5; i++) {
            let exponent;
            if (i === 0) {
                // Largest exponent determines chaos/stability
                exponent = stability > 0.7 ? Math.random() * 0.5 - 0.8 : // Stable
                          stability < 0.3 ? Math.random() * 0.3 : // Chaotic
                          (Math.random() - 0.5) * 0.2; // Neutral
            } else {
                // Subsequent exponents are typically smaller
                exponent = exponents[0] - i * 0.1 - Math.random() * 0.2;
            }
            exponents.push(exponent);
        }
        
        this.charts.lyapunov.data.datasets[0].data = exponents;
        this.charts.lyapunov.update('none');
    }
    
    refresh() {
        if (!this.isInitialized) return;
        
        if (this.data) {
            this.updatePhaseSpace();
            this.updateFlowVisualization();
        }
        
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.update === 'function') {
                chart.update();
            }
        });
        
        console.log('🔄 Dynamics visualization refreshed');
    }
    
    cleanup() {
        if (this.phaseSpacePlot) {
            this.phaseSpacePlot.selectAll('*').remove();
        }
        
        if (this.flowField) {
            this.flowField.selectAll('*').remove();
        }
        
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        this.charts = {};
        this.data = null;
        this.isInitialized = false;
        
        console.log('🧹 Dynamics Visualizer cleanup completed');
    }
}

export { DynamicsVisualizer };