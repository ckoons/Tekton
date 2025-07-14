/**
 * Manifold Analyzer for Noesis Dashboard
 * Creates 3D visualizations and analysis of memory state manifolds
 * Uses shared TektonViz framework for consistent visualization
 */

class ManifoldAnalyzer {
    constructor() {
        this.data = null;
        this.manifold3D = null;
        this.curvatureHeatmap = null;
        this.isInitialized = false;
        this.currentReductionMethod = 'pca';
        
        // Initialize TektonViz for manifold visualizations
        this.tektonViz = new TektonViz('canvas');
        this.heatmapViz = new TektonViz('chartjs');
        
        console.log('🌐 Manifold Analyzer initialized with TektonViz');
    }
    
    async init() {
        try {
            this.setupManifoldVisualization();
            this.setupCurvatureHeatmap();
            this.setupControls();
            this.isInitialized = true;
            console.log('✅ Manifold Analyzer ready');
        } catch (error) {
            console.error('❌ Manifold Analyzer initialization failed:', error);
            throw error;
        }
    }
    
    setupManifoldVisualization() {
        const container = document.getElementById('manifold-3d-viz');
        if (!container) return;
        
        // Clear existing content
        container.innerHTML = '';
        
        // Set up SVG for 3D manifold visualization
        const width = container.clientWidth || 400;
        const height = container.clientHeight || 300;
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .style('background', '#f8fafc')
            .style('border-radius', '8px');
        
        // Create groups for different layers
        this.manifoldGroups = {
            background: svg.append('g').attr('class', 'background'),
            manifold: svg.append('g').attr('class', 'manifold'),
            points: svg.append('g').attr('class', 'points'),
            annotations: svg.append('g').attr('class', 'annotations')
        };
        
        // Set up 3D projection
        this.projection = {
            width: width,
            height: height,
            scale: Math.min(width, height) * 0.3,
            rotation: { x: 15, y: 30, z: 0 },
            center: { x: width / 2, y: height / 2 }
        };
        
        this.manifold3D = svg;
    }
    
    setupCurvatureHeatmap() {
        const container = document.getElementById('curvature-heatmap');
        if (!container) return;
        
        // Clear existing content
        container.innerHTML = '';
        
        const width = container.clientWidth || 300;
        const height = container.clientHeight || 200;
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .style('background', '#f8fafc')
            .style('border-radius', '8px');
        
        this.curvatureHeatmap = svg;
        this.heatmapDimensions = { width, height };
    }
    
    setupControls() {
        const reductionSelect = document.getElementById('reduction-method');
        const updateButton = document.getElementById('update-manifold');
        
        if (reductionSelect) {
            reductionSelect.addEventListener('change', (e) => {
                this.currentReductionMethod = e.target.value;
            });
        }
        
        if (updateButton) {
            updateButton.addEventListener('click', () => {
                this.updateManifoldVisualization();
            });
        }
    }
    
    updateData(analysisData) {
        if (!this.isInitialized || !analysisData) return;
        
        this.data = analysisData;
        
        try {
            this.updateManifoldProperties();
            this.updateManifoldVisualization();
            this.updateCurvatureVisualization();
            
            console.log('🌐 Manifold analysis updated');
        } catch (error) {
            console.error('Failed to update manifold analysis:', error);
        }
    }
    
    updateManifoldProperties() {
        if (!this.data) return;
        
        const analysisResults = this.data.data || {};
        
        // Update property displays
        this.updateProperty('intrinsic-dimension', 
            analysisResults.intrinsic_dimension || '-',
            'dimensions'
        );
        
        this.updateProperty('manifold-curvature', 
            analysisResults.curvature || '-',
            'curvature units'
        );
        
        this.updateProperty('topology-class', 
            analysisResults.topology_class || 'Unknown'
        );
        
        this.updateProperty('manifold-stability', 
            analysisResults.stability || '-',
            'stability index'
        );
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
    
    updateManifoldVisualization() {
        if (!this.manifold3D || !this.data) return;
        
        // Generate synthetic manifold data for visualization
        const manifoldData = this.generateManifoldData();
        
        // Clear previous visualization
        Object.values(this.manifoldGroups).forEach(group => {
            group.selectAll('*').remove();
        });
        
        // Draw manifold surface
        this.drawManifoldSurface(manifoldData);
        
        // Draw data points
        this.drawDataPoints(manifoldData.points);
        
        // Draw coordinate axes
        this.drawAxes();
    }
    
    generateManifoldData() {
        // Generate synthetic manifold data based on analysis results
        const analysisResults = this.data.data || {};
        const dimension = analysisResults.intrinsic_dimension || 2;
        const curvature = analysisResults.curvature || 0;
        
        // Generate points on manifold
        const numPoints = 50;
        const points = [];
        
        for (let i = 0; i < numPoints; i++) {
            const u = (i / numPoints) * 2 * Math.PI;
            
            for (let j = 0; j < numPoints; j++) {
                const v = (j / numPoints) * Math.PI;
                
                // Generate manifold surface based on dimension and curvature
                let x, y, z;
                
                if (dimension <= 2) {
                    // 2D manifold embedded in 3D
                    const radius = 1 + curvature * 0.5;
                    x = radius * Math.cos(u) * Math.sin(v);
                    y = radius * Math.sin(u) * Math.sin(v);
                    z = radius * Math.cos(v) + curvature * Math.sin(2 * u) * 0.2;
                } else {
                    // Higher-dimensional manifold projection
                    const scale = 1 + curvature * 0.3;
                    x = scale * Math.cos(u) * (1 + 0.3 * Math.cos(3 * v));
                    y = scale * Math.sin(u) * (1 + 0.3 * Math.cos(3 * v));
                    z = scale * Math.sin(v) + curvature * Math.sin(2 * u) * 0.1;
                }
                
                points.push({
                    x: x, y: y, z: z,
                    u: u, v: v,
                    intensity: Math.abs(curvature) + Math.random() * 0.2
                });
            }
        }
        
        return {
            points: points,
            dimension: dimension,
            curvature: curvature,
            gridSize: numPoints
        };
    }
    
    drawManifoldSurface(manifoldData) {
        const group = this.manifoldGroups.manifold;
        const { points, gridSize } = manifoldData;
        
        // Create wireframe mesh
        for (let i = 0; i < gridSize - 1; i++) {
            for (let j = 0; j < gridSize - 1; j++) {
                const idx1 = i * gridSize + j;
                const idx2 = i * gridSize + (j + 1);
                const idx3 = (i + 1) * gridSize + j;
                const idx4 = (i + 1) * gridSize + (j + 1);
                
                if (idx1 < points.length && idx2 < points.length && 
                    idx3 < points.length && idx4 < points.length) {
                    
                    const p1 = this.project3D(points[idx1]);
                    const p2 = this.project3D(points[idx2]);
                    const p3 = this.project3D(points[idx3]);
                    const p4 = this.project3D(points[idx4]);
                    
                    // Draw quad as two triangles
                    const pathData = `M ${p1.x} ${p1.y} L ${p2.x} ${p2.y} L ${p4.x} ${p4.y} L ${p3.x} ${p3.y} Z`;
                    
                    group.append('path')
                        .attr('d', pathData)
                        .attr('fill', this.getManifoldColor(points[idx1].intensity))
                        .attr('stroke', '#94a3b8')
                        .attr('stroke-width', 0.5)
                        .attr('opacity', 0.7);
                }
            }
        }
    }
    
    drawDataPoints(points) {
        const group = this.manifoldGroups.points;
        
        // Sample subset of points for clarity
        const sampledPoints = points.filter((_, i) => i % 10 === 0);
        
        sampledPoints.forEach(point => {
            const projected = this.project3D(point);
            
            group.append('circle')
                .attr('cx', projected.x)
                .attr('cy', projected.y)
                .attr('r', 3)
                .attr('fill', '#3b82f6')
                .attr('stroke', '#ffffff')
                .attr('stroke-width', 1)
                .attr('opacity', 0.8)
                .append('title')
                .text(`Point: (${point.x.toFixed(2)}, ${point.y.toFixed(2)}, ${point.z.toFixed(2)})`);
        });
    }
    
    drawAxes() {
        const group = this.manifoldGroups.annotations;
        const center = this.projection.center;
        const scale = this.projection.scale * 0.3;
        
        // X axis (red)
        const xEnd = this.project3D({ x: 1, y: 0, z: 0 });
        group.append('line')
            .attr('x1', center.x)
            .attr('y1', center.y)
            .attr('x2', center.x + scale)
            .attr('y2', center.y)
            .attr('stroke', '#ef4444')
            .attr('stroke-width', 2);
        
        group.append('text')
            .attr('x', center.x + scale + 10)
            .attr('y', center.y + 5)
            .attr('fill', '#ef4444')
            .attr('font-size', '12px')
            .text('X');
        
        // Y axis (green)
        group.append('line')
            .attr('x1', center.x)
            .attr('y1', center.y)
            .attr('x2', center.x)
            .attr('y2', center.y - scale)
            .attr('stroke', '#10b981')
            .attr('stroke-width', 2);
        
        group.append('text')
            .attr('x', center.x + 5)
            .attr('y', center.y - scale - 5)
            .attr('fill', '#10b981')
            .attr('font-size', '12px')
            .text('Y');
        
        // Z axis (blue)
        const zEnd = this.project3D({ x: 0, y: 0, z: 1 });
        group.append('line')
            .attr('x1', center.x)
            .attr('y1', center.y)
            .attr('x2', center.x + scale * 0.5)
            .attr('y2', center.y + scale * 0.5)
            .attr('stroke', '#3b82f6')
            .attr('stroke-width', 2);
        
        group.append('text')
            .attr('x', center.x + scale * 0.5 + 5)
            .attr('y', center.y + scale * 0.5 + 5)
            .attr('fill', '#3b82f6')
            .attr('font-size', '12px')
            .text('Z');
    }
    
    project3D(point) {
        // Simple 3D to 2D projection
        const { rotation, scale, center } = this.projection;
        
        // Apply rotation
        const cosX = Math.cos(rotation.x * Math.PI / 180);
        const sinX = Math.sin(rotation.x * Math.PI / 180);
        const cosY = Math.cos(rotation.y * Math.PI / 180);
        const sinY = Math.sin(rotation.y * Math.PI / 180);
        
        // Rotate around X axis
        const y1 = point.y * cosX - point.z * sinX;
        const z1 = point.y * sinX + point.z * cosX;
        
        // Rotate around Y axis
        const x2 = point.x * cosY + z1 * sinY;
        const z2 = -point.x * sinY + z1 * cosY;
        
        // Project to 2D
        const x = center.x + x2 * scale;
        const y = center.y - y1 * scale;
        
        return { x, y, z: z2 };
    }
    
    getManifoldColor(intensity) {
        // Color scale from blue to red based on intensity
        const normalized = Math.max(0, Math.min(1, intensity));
        const hue = (1 - normalized) * 240; // Blue to red
        return `hsl(${hue}, 70%, 60%)`;
    }
    
    updateCurvatureVisualization() {
        if (!this.curvatureHeatmap || !this.data) return;
        
        this.curvatureHeatmap.selectAll('*').remove();
        
        const { width, height } = this.heatmapDimensions;
        const analysisResults = this.data.data || {};
        const curvature = analysisResults.curvature || 0;
        
        // Generate curvature heatmap data
        const gridSize = 20;
        const cellWidth = width / gridSize;
        const cellHeight = height / gridSize;
        
        for (let i = 0; i < gridSize; i++) {
            for (let j = 0; j < gridSize; j++) {
                const x = (i / gridSize - 0.5) * 2;
                const y = (j / gridSize - 0.5) * 2;
                
                // Simulate curvature field
                const distance = Math.sqrt(x * x + y * y);
                const localCurvature = curvature * Math.exp(-distance * 2) + 
                                    Math.sin(x * 3) * Math.cos(y * 3) * 0.1;
                
                const intensity = Math.abs(localCurvature);
                const color = this.getCurvatureColor(localCurvature);
                
                this.curvatureHeatmap.append('rect')
                    .attr('x', i * cellWidth)
                    .attr('y', j * cellHeight)
                    .attr('width', cellWidth)
                    .attr('height', cellHeight)
                    .attr('fill', color)
                    .attr('opacity', 0.8)
                    .append('title')
                    .text(`Curvature: ${localCurvature.toFixed(3)}`);
            }
        }
        
        // Add color scale legend
        this.addCurvatureLegend();
    }
    
    getCurvatureColor(curvature) {
        const normalized = Math.tanh(curvature * 5) * 0.5 + 0.5;
        const hue = normalized > 0.5 ? 0 : 240; // Red for positive, blue for negative
        const saturation = Math.abs(normalized - 0.5) * 200;
        return `hsl(${hue}, ${saturation}%, 60%)`;
    }
    
    addCurvatureLegend() {
        const { width, height } = this.heatmapDimensions;
        const legendHeight = 20;
        const legendY = height - legendHeight - 10;
        
        // Legend gradient
        const gradient = this.curvatureHeatmap.append('defs')
            .append('linearGradient')
            .attr('id', 'curvature-gradient')
            .attr('x1', '0%')
            .attr('x2', '100%');
        
        gradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', 'hsl(240, 100%, 60%)');
        
        gradient.append('stop')
            .attr('offset', '50%')
            .attr('stop-color', 'hsl(120, 50%, 60%)');
        
        gradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', 'hsl(0, 100%, 60%)');
        
        this.curvatureHeatmap.append('rect')
            .attr('x', 10)
            .attr('y', legendY)
            .attr('width', width - 20)
            .attr('height', legendHeight)
            .attr('fill', 'url(#curvature-gradient)')
            .attr('stroke', '#64748b');
        
        // Legend labels
        this.curvatureHeatmap.append('text')
            .attr('x', 10)
            .attr('y', legendY - 5)
            .attr('font-size', '10px')
            .attr('fill', '#64748b')
            .text('Negative');
        
        this.curvatureHeatmap.append('text')
            .attr('x', width - 10)
            .attr('y', legendY - 5)
            .attr('text-anchor', 'end')
            .attr('font-size', '10px')
            .attr('fill', '#64748b')
            .text('Positive');
    }
    
    refresh() {
        if (!this.isInitialized) return;
        
        if (this.data) {
            this.updateManifoldVisualization();
            this.updateCurvatureVisualization();
        }
        
        console.log('🔄 Manifold analysis refreshed');
    }
    
    cleanup() {
        if (this.manifold3D) {
            this.manifold3D.selectAll('*').remove();
        }
        
        if (this.curvatureHeatmap) {
            this.curvatureHeatmap.selectAll('*').remove();
        }
        
        this.data = null;
        this.isInitialized = false;
        
        console.log('🧹 Manifold Analyzer cleanup completed');
    }
}

export { ManifoldAnalyzer };