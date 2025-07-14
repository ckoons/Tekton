/**
 * Canvas-based renderer for Tekton visualizations
 * Simple, performant, no dependencies
 */

class CanvasRenderer extends VisualizationRenderer {
    constructor() {
        super();
        this.canvas = null;
        this.ctx = null;
        this.container = null;
        this.animationId = null;
    }
    
    async initialize(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container element not found: ${containerId}`);
        }
        
        // Create canvas element
        this.canvas = document.createElement('canvas');
        this.canvas.width = options.width || this.container.clientWidth || 800;
        this.canvas.height = options.height || this.container.clientHeight || 600;
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        
        // Clear container and add canvas
        this.container.innerHTML = '';
        this.container.appendChild(this.canvas);
        
        // Get context
        this.ctx = this.canvas.getContext('2d');
        
        // Set default styles
        this.ctx.strokeStyle = options.strokeStyle || '#333';
        this.ctx.fillStyle = options.fillStyle || '#3498db';
        this.ctx.lineWidth = options.lineWidth || 1;
        
        // Handle resize
        if (options.responsive !== false) {
            this.handleResize();
        }
    }
    
    async render(data, type, options = {}) {
        if (!this.ctx) {
            throw new Error("Renderer not initialized");
        }
        
        // Clear before rendering
        if (options.clear !== false) {
            this.clear();
        }
        
        switch (type) {
            case 'scatter':
                return this.renderScatter(data, options);
            case 'line':
            case 'trajectory':
                return this.renderLine(data, options);
            case 'manifold':
                return this.renderManifold(data, options);
            case 'heatmap':
                return this.renderHeatmap(data, options);
            case 'network':
                return this.renderNetwork(data, options);
            default:
                throw new Error(`Unsupported visualization type: ${type}`);
        }
    }
    
    renderScatter(points, options = {}) {
        const { width, height } = this.canvas;
        const padding = options.padding || 40;
        
        // Calculate bounds
        const bounds = VizUtils.calculateBounds(points);
        
        // Scale points to canvas
        const scaleX = (width - 2 * padding) / (bounds.maxX - bounds.minX || 1);
        const scaleY = (height - 2 * padding) / (bounds.maxY - bounds.minY || 1);
        
        // Draw axes if requested
        if (options.showAxes) {
            this.drawAxes(bounds, padding);
        }
        
        // Draw points
        points.forEach(point => {
            const x = padding + (point.x - bounds.minX) * scaleX;
            const y = height - padding - (point.y - bounds.minY) * scaleY;
            
            this.ctx.fillStyle = point.color || options.pointColor || '#3498db';
            this.ctx.beginPath();
            this.ctx.arc(x, y, point.size || options.pointSize || 3, 0, 2 * Math.PI);
            this.ctx.fill();
            
            // Label if provided
            if (point.label && options.showLabels) {
                this.ctx.fillStyle = '#333';
                this.ctx.font = '10px sans-serif';
                this.ctx.fillText(point.label, x + 5, y - 5);
            }
        });
    }
    
    renderLine(points, options = {}) {
        if (points.length < 2) return;
        
        const { width, height } = this.canvas;
        const padding = options.padding || 40;
        
        // Calculate bounds
        const bounds = VizUtils.calculateBounds(points);
        
        // Scale points
        const scaleX = (width - 2 * padding) / (bounds.maxX - bounds.minX || 1);
        const scaleY = (height - 2 * padding) / (bounds.maxY - bounds.minY || 1);
        
        // Draw axes if requested
        if (options.showAxes) {
            this.drawAxes(bounds, padding);
        }
        
        // Draw line
        this.ctx.strokeStyle = options.lineColor || '#2ecc71';
        this.ctx.lineWidth = options.lineWidth || 2;
        this.ctx.beginPath();
        
        points.forEach((point, i) => {
            const x = padding + (point.x - bounds.minX) * scaleX;
            const y = height - padding - (point.y - bounds.minY) * scaleY;
            
            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        });
        
        this.ctx.stroke();
        
        // Draw points if requested
        if (options.showPoints) {
            this.renderScatter(points, { 
                ...options, 
                showAxes: false,
                pointSize: options.pointSize || 4 
            });
        }
    }
    
    renderManifold(data, options = {}) {
        // Manifold visualization: points with optional connections
        const { points, connections, regions } = data;
        
        // Draw regions first (background)
        if (regions) {
            regions.forEach(region => {
                this.ctx.fillStyle = region.color || 'rgba(52, 152, 219, 0.1)';
                this.ctx.beginPath();
                // Simple convex hull visualization
                region.points.forEach((pointIdx, i) => {
                    const point = points[pointIdx];
                    if (i === 0) {
                        this.ctx.moveTo(point.x, point.y);
                    } else {
                        this.ctx.lineTo(point.x, point.y);
                    }
                });
                this.ctx.closePath();
                this.ctx.fill();
            });
        }
        
        // Draw connections
        if (connections) {
            this.ctx.strokeStyle = options.connectionColor || 'rgba(150, 150, 150, 0.3)';
            this.ctx.lineWidth = options.connectionWidth || 1;
            
            connections.forEach(([i, j]) => {
                this.ctx.beginPath();
                this.ctx.moveTo(points[i].x, points[i].y);
                this.ctx.lineTo(points[j].x, points[j].y);
                this.ctx.stroke();
            });
        }
        
        // Draw points
        this.renderScatter(points, options);
    }
    
    renderHeatmap(data, options = {}) {
        const { values, rows, cols } = data;
        const { width, height } = this.canvas;
        
        const cellWidth = width / cols;
        const cellHeight = height / rows;
        
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                const value = values[i * cols + j];
                const color = VizUtils.valueToColor(value, options.colormap);
                
                this.ctx.fillStyle = color;
                this.ctx.fillRect(
                    j * cellWidth,
                    i * cellHeight,
                    cellWidth,
                    cellHeight
                );
            }
        }
    }
    
    renderNetwork(data, options = {}) {
        const { nodes, edges } = data;
        
        // Draw edges first
        this.ctx.strokeStyle = options.edgeColor || 'rgba(150, 150, 150, 0.5)';
        this.ctx.lineWidth = options.edgeWidth || 1;
        
        edges.forEach(edge => {
            const source = nodes.find(n => n.id === edge.source);
            const target = nodes.find(n => n.id === edge.target);
            
            if (source && target) {
                this.ctx.beginPath();
                this.ctx.moveTo(source.x, source.y);
                this.ctx.lineTo(target.x, target.y);
                this.ctx.stroke();
            }
        });
        
        // Draw nodes
        this.renderScatter(nodes, {
            ...options,
            pointSize: options.nodeSize || 5
        });
    }
    
    drawAxes(bounds, padding) {
        const { width, height } = this.canvas;
        
        this.ctx.strokeStyle = '#666';
        this.ctx.lineWidth = 1;
        
        // X axis
        this.ctx.beginPath();
        this.ctx.moveTo(padding, height - padding);
        this.ctx.lineTo(width - padding, height - padding);
        this.ctx.stroke();
        
        // Y axis
        this.ctx.beginPath();
        this.ctx.moveTo(padding, padding);
        this.ctx.lineTo(padding, height - padding);
        this.ctx.stroke();
        
        // Labels
        this.ctx.fillStyle = '#666';
        this.ctx.font = '12px sans-serif';
        
        // X labels
        this.ctx.textAlign = 'center';
        this.ctx.fillText(bounds.minX.toFixed(2), padding, height - padding + 20);
        this.ctx.fillText(bounds.maxX.toFixed(2), width - padding, height - padding + 20);
        
        // Y labels
        this.ctx.textAlign = 'right';
        this.ctx.fillText(bounds.maxY.toFixed(2), padding - 10, padding);
        this.ctx.fillText(bounds.minY.toFixed(2), padding - 10, height - padding);
    }
    
    async clear() {
        if (this.ctx) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    }
    
    async destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.canvas && this.canvas.parentElement) {
            this.canvas.remove();
        }
        
        this.canvas = null;
        this.ctx = null;
        this.container = null;
    }
    
    handleResize() {
        const resizeObserver = new ResizeObserver(entries => {
            for (let entry of entries) {
                const { width, height } = entry.contentRect;
                this.canvas.width = width;
                this.canvas.height = height;
            }
        });
        
        resizeObserver.observe(this.container);
    }
    
    getCapabilities() {
        return {
            dimensions: [2],
            types: ['scatter', 'line', 'trajectory', 'manifold', 'heatmap', 'network'],
            interactive: false,
            animated: true,
            responsive: true
        };
    }
}

// Register the renderer
VisualizationFactory.registerRenderer('canvas', CanvasRenderer);