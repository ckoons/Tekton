/**
 * Unified visualization API for Tekton components
 * Provides high-level visualization methods that work with any renderer
 * 
 * @example
 * // Basic usage with Chart.js renderer
 * const viz = new TektonViz('chartjs');
 * await viz.init('chart-container');
 * await viz.drawTimeSeries(timeSeriesData);
 * 
 * @example
 * // High-performance canvas rendering
 * const viz = new TektonViz('canvas');
 * await viz.init('canvas-container');
 * await viz.drawManifold(manifoldData);
 */

class TektonViz {
    /**
     * Create a new TektonViz instance
     * @param {string} renderEngine - Name of the renderer to use (canvas, chartjs, etc.)
     * @param {Object} options - Global options for the visualizer
     */
    constructor(renderEngine = null, options = {}) {
        // Use configured default or fallback to canvas
        const engine = renderEngine || 
                      window.TEKTON_VIZ_CONFIG?.defaultRenderer || 
                      'canvas';
                      
        this.renderer = VisualizationFactory.createRenderer(engine);
        this.options = options;
        this.initialized = false;
        this.containerId = null;
    }
    
    /**
     * Initialize the visualizer with a container
     * @param {string} containerId - ID of the DOM element to render into
     * @param {Object} options - Initialization options
     */
    async init(containerId, options = {}) {
        this.containerId = containerId;
        const mergedOptions = { ...this.options, ...options };
        await this.renderer.initialize(containerId, mergedOptions);
        this.initialized = true;
    }
    
    /**
     * Ensure the visualizer is initialized
     */
    ensureInitialized() {
        if (!this.initialized) {
            throw new Error("TektonViz not initialized. Call init() first.");
        }
    }
    
    // High-level visualization methods
    
    /**
     * Draw a manifold projection
     * @param {Object} data - Manifold data with points and optional connections
     * @param {Object} options - Visualization options
     */
    async drawManifold(data, options = {}) {
        this.ensureInitialized();
        
        // Prepare data for 2D visualization
        const preparedData = this.prepareManifoldData(data);
        
        // Add default manifold options
        const manifoldOptions = {
            showAxes: true,
            showGrid: false,
            pointSize: 4,
            connectionColor: 'rgba(150, 150, 150, 0.3)',
            ...options
        };
        
        await this.renderer.render(preparedData, 'manifold', manifoldOptions);
    }
    
    /**
     * Draw a trajectory through state space
     * @param {Array} trajectory - Array of points representing a path
     * @param {Object} options - Visualization options
     */
    async drawTrajectory(trajectory, options = {}) {
        this.ensureInitialized();
        
        const points = this.prepareTrajectoryData(trajectory);
        
        const trajectoryOptions = {
            showAxes: true,
            showPoints: true,
            lineColor: '#2ecc71',
            lineWidth: 2,
            pointSize: 3,
            ...options
        };
        
        await this.renderer.render(points, 'trajectory', trajectoryOptions);
    }
    
    /**
     * Draw a scatter plot
     * @param {Array} points - Array of points
     * @param {Object} options - Visualization options
     */
    async drawScatter(points, options = {}) {
        this.ensureInitialized();
        
        const preparedPoints = this.prepareScatterData(points);
        
        await this.renderer.render(preparedPoints, 'scatter', options);
    }
    
    /**
     * Draw a time series
     * @param {Array} data - Time series data
     * @param {Object} options - Visualization options
     */
    async drawTimeSeries(data, options = {}) {
        this.ensureInitialized();
        
        // Use ChartJS for time series if available
        if (this.renderer.constructor.name === 'ChartJSRenderer' ||
            VisualizationFactory.getAvailableRenderers().includes('chartjs')) {
            
            // Create a temporary ChartJS renderer for this
            const chartRenderer = VisualizationFactory.createRenderer('chartjs');
            await chartRenderer.initialize(this.containerId + '-chart', this.options);
            await chartRenderer.render(data, 'timeseries', options);
        } else {
            // Fallback to line chart
            const points = this.prepareTimeSeriesData(data);
            await this.renderer.render(points, 'line', options);
        }
    }
    
    /**
     * Draw a distribution/histogram
     * @param {Array} data - Distribution data
     * @param {Object} options - Visualization options
     */
    async drawDistribution(data, options = {}) {
        this.ensureInitialized();
        
        // Prepare histogram data
        const histogram = this.prepareDistributionData(data);
        
        if (this.renderer.constructor.name === 'ChartJSRenderer') {
            await this.renderer.render(histogram, 'distribution', options);
        } else {
            // Fallback to custom bar chart
            await this.drawBarsAsRects(histogram, options);
        }
    }
    
    /**
     * Draw a heatmap
     * @param {Object} data - Heatmap data with values, rows, cols
     * @param {Object} options - Visualization options
     */
    async drawHeatmap(data, options = {}) {
        this.ensureInitialized();
        
        await this.renderer.render(data, 'heatmap', options);
    }
    
    /**
     * Draw a network/graph
     * @param {Object} data - Network data with nodes and edges
     * @param {Object} options - Visualization options
     */
    async drawNetwork(data, options = {}) {
        this.ensureInitialized();
        
        // Apply force layout if positions not provided
        const layoutData = this.applyNetworkLayout(data);
        
        await this.renderer.render(layoutData, 'network', options);
    }
    
    /**
     * Draw regime transitions
     * @param {Object} data - Regime data with states and transitions
     * @param {Object} options - Visualization options
     */
    async drawRegimeTransitions(data, options = {}) {
        this.ensureInitialized();
        
        // Convert regime data to visualization format
        const vizData = {
            nodes: data.regimes.map((regime, i) => ({
                id: regime.id,
                x: Math.cos(2 * Math.PI * i / data.regimes.length) * 200 + 400,
                y: Math.sin(2 * Math.PI * i / data.regimes.length) * 200 + 300,
                label: regime.name,
                color: regime.color || this.getRegimeColor(i)
            })),
            edges: data.transitions.map(t => ({
                source: t.from,
                target: t.to,
                weight: t.probability
            }))
        };
        
        await this.renderer.render(vizData, 'network', {
            nodeSize: 10,
            edgeWidth: 2,
            showLabels: true,
            ...options
        });
    }
    
    // Data preparation methods
    
    prepareManifoldData(data) {
        if (data.points) {
            // Already structured
            return data;
        }
        
        // Assume array of high-dimensional points
        const projected = this.projectTo2D(data);
        
        return {
            points: projected,
            connections: data.connections || [],
            regions: data.regions || []
        };
    }
    
    prepareTrajectoryData(trajectory) {
        return trajectory.map((point, i) => {
            if (typeof point === 'number') {
                // 1D trajectory
                return { x: i, y: point };
            } else if (Array.isArray(point)) {
                // High-dimensional point
                const projected = this.projectTo2D([point])[0];
                return { ...projected, time: i };
            } else {
                // Already structured
                return point;
            }
        });
    }
    
    prepareScatterData(points) {
        return points.map(point => {
            if (Array.isArray(point)) {
                const projected = this.projectTo2D([point])[0];
                return projected;
            }
            return point;
        });
    }
    
    prepareTimeSeriesData(data) {
        if (Array.isArray(data)) {
            return data.map((value, i) => ({
                x: i,
                y: value
            }));
        }
        
        // Assume {timestamps, values}
        return data.timestamps.map((t, i) => ({
            x: t,
            y: data.values[i]
        }));
    }
    
    prepareDistributionData(data) {
        if (data.bins && data.counts) {
            return {
                labels: data.bins,
                values: data.counts
            };
        }
        
        // Calculate histogram from raw data
        const bins = this.calculateHistogram(data);
        return bins;
    }
    
    // Utility methods
    
    /**
     * Project high-dimensional data to 2D
     * @param {Array} highDimData - Array of high-dimensional points
     * @returns {Array} Array of 2D points
     */
    projectTo2D(highDimData) {
        // Simple projection using first two components
        // In real implementation, this could use PCA results from backend
        return highDimData.map((point, i) => {
            const x = point[0] || 0;
            const y = point[1] || 0;
            
            // Scale to reasonable canvas coordinates
            return {
                x: x * 100 + 400,
                y: y * 100 + 300,
                originalIndex: i,
                originalDimensions: point.length
            };
        });
    }
    
    /**
     * Apply force-directed layout to network
     * @param {Object} networkData - Network with nodes and edges
     * @returns {Object} Network with computed positions
     */
    applyNetworkLayout(networkData) {
        // Simple circular layout for now
        // Could be replaced with force-directed layout
        const nodes = networkData.nodes.map((node, i) => {
            if (node.x !== undefined && node.y !== undefined) {
                return node; // Already has position
            }
            
            const angle = (2 * Math.PI * i) / networkData.nodes.length;
            return {
                ...node,
                x: Math.cos(angle) * 200 + 400,
                y: Math.sin(angle) * 200 + 300
            };
        });
        
        return {
            nodes,
            edges: networkData.edges
        };
    }
    
    /**
     * Calculate histogram bins
     * @param {Array} data - Raw data values
     * @param {number} numBins - Number of bins
     * @returns {Object} Histogram data
     */
    calculateHistogram(data, numBins = 20) {
        const min = Math.min(...data);
        const max = Math.max(...data);
        const binWidth = (max - min) / numBins;
        
        const bins = Array(numBins).fill(0);
        const binLabels = [];
        
        for (let i = 0; i < numBins; i++) {
            const binStart = min + i * binWidth;
            const binEnd = binStart + binWidth;
            binLabels.push(`${binStart.toFixed(2)}-${binEnd.toFixed(2)}`);
            
            data.forEach(value => {
                if (value >= binStart && value < binEnd) {
                    bins[i]++;
                }
            });
        }
        
        return {
            labels: binLabels,
            values: bins
        };
    }
    
    /**
     * Draw bars as rectangles (fallback for canvas renderer)
     * @param {Object} histogram - Histogram data
     * @param {Object} options - Visualization options
     */
    async drawBarsAsRects(histogram, options = {}) {
        const barData = histogram.labels.map((label, i) => ({
            x: i,
            y: histogram.values[i],
            width: 0.8,
            label: label
        }));
        
        // Convert to scatter plot with rectangles
        // This is a simplified version
        const points = [];
        barData.forEach(bar => {
            for (let j = 0; j < bar.y; j++) {
                points.push({
                    x: bar.x,
                    y: j,
                    color: 'rgba(155, 89, 182, 0.6)'
                });
            }
        });
        
        await this.renderer.render(points, 'scatter', options);
    }
    
    /**
     * Get color for regime
     * @param {number} index - Regime index
     * @returns {string} CSS color
     */
    getRegimeColor(index) {
        const colors = [
            '#3498db', '#2ecc71', '#9b59b6', '#f1c40f',
            '#e74c3c', '#e67e22', '#95a5a6', '#1abc9c'
        ];
        
        return colors[index % colors.length];
    }
    
    /**
     * Clear the visualization
     */
    async clear() {
        this.ensureInitialized();
        await this.renderer.clear();
    }
    
    /**
     * Destroy the visualizer
     */
    async destroy() {
        if (this.renderer) {
            await this.renderer.destroy();
        }
        this.initialized = false;
    }
    
    /**
     * Get renderer capabilities
     * @returns {Object} Capabilities object
     */
    getCapabilities() {
        return this.renderer ? this.renderer.getCapabilities() : {};
    }
}

// Global configuration
window.TEKTON_VIZ_CONFIG = {
    defaultRenderer: 'canvas',
    rendererOptions: {
        canvas: {
            antialias: true,
            responsive: true
        },
        chartjs: {
            responsive: true,
            maintainAspectRatio: false
        }
    }
};

// Export for use
window.TektonViz = TektonViz;