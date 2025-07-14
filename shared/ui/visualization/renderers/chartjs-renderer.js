/**
 * Chart.js-based renderer for standard plots
 * Handles line charts, bar charts, scatter plots, etc.
 */

class ChartJSRenderer extends VisualizationRenderer {
    constructor() {
        super();
        this.chart = null;
        this.container = null;
        this.canvas = null;
    }
    
    async initialize(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container element not found: ${containerId}`);
        }
        
        // Create canvas for Chart.js
        this.canvas = document.createElement('canvas');
        this.container.innerHTML = '';
        this.container.appendChild(this.canvas);
        
        // Store default options
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            ...options
        };
    }
    
    async render(data, type, options = {}) {
        if (!this.canvas) {
            throw new Error("Renderer not initialized");
        }
        
        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }
        
        // Map visualization type to Chart.js type
        const chartType = this.mapChartType(type);
        const chartData = this.prepareData(data, type);
        const chartOptions = this.mergeOptions(options, type);
        
        // Create new chart
        this.chart = new Chart(this.canvas, {
            type: chartType,
            data: chartData,
            options: chartOptions
        });
    }
    
    mapChartType(type) {
        const mapping = {
            'scatter': 'scatter',
            'line': 'line',
            'trajectory': 'line',
            'timeseries': 'line',
            'bar': 'bar',
            'distribution': 'bar',
            'histogram': 'bar',
            'pie': 'pie',
            'doughnut': 'doughnut',
            'radar': 'radar',
            'bubble': 'bubble'
        };
        
        return mapping[type] || 'scatter';
    }
    
    prepareData(data, type) {
        // Handle different data formats
        if (Array.isArray(data)) {
            return this.prepareArrayData(data, type);
        } else if (data.datasets) {
            // Already in Chart.js format
            return data;
        } else {
            // Assume object with specific structure
            return this.prepareStructuredData(data, type);
        }
    }
    
    prepareArrayData(data, type) {
        switch (type) {
            case 'scatter':
            case 'bubble':
                return {
                    datasets: [{
                        label: 'Data',
                        data: data.map(point => ({
                            x: point.x,
                            y: point.y,
                            r: point.size || point.r || 5
                        })),
                        backgroundColor: 'rgba(52, 152, 219, 0.6)',
                        borderColor: 'rgba(52, 152, 219, 1)'
                    }]
                };
                
            case 'line':
            case 'trajectory':
            case 'timeseries':
                return {
                    labels: data.map((_, i) => i),
                    datasets: [{
                        label: 'Data',
                        data: data.map(point => point.y || point),
                        borderColor: 'rgba(46, 204, 113, 1)',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        fill: false
                    }]
                };
                
            case 'bar':
            case 'distribution':
            case 'histogram':
                return {
                    labels: data.map(item => item.label || item.x || item.bin),
                    datasets: [{
                        label: 'Count',
                        data: data.map(item => item.count || item.y || item.value),
                        backgroundColor: 'rgba(155, 89, 182, 0.6)',
                        borderColor: 'rgba(155, 89, 182, 1)',
                        borderWidth: 1
                    }]
                };
                
            default:
                // Generic format
                return {
                    datasets: [{
                        label: 'Data',
                        data: data
                    }]
                };
        }
    }
    
    prepareStructuredData(data, type) {
        // Handle structured data with labels, values, etc.
        if (data.labels && data.values) {
            return {
                labels: data.labels,
                datasets: [{
                    label: data.label || 'Data',
                    data: data.values,
                    backgroundColor: data.backgroundColor || 'rgba(52, 152, 219, 0.6)',
                    borderColor: data.borderColor || 'rgba(52, 152, 219, 1)'
                }]
            };
        }
        
        // Multi-dataset support
        if (data.series) {
            return {
                labels: data.labels || [],
                datasets: data.series.map((series, i) => ({
                    label: series.name || `Series ${i + 1}`,
                    data: series.data,
                    backgroundColor: series.color || this.getDefaultColor(i, 0.6),
                    borderColor: series.color || this.getDefaultColor(i, 1),
                    fill: series.fill !== undefined ? series.fill : false
                }))
            };
        }
        
        return { datasets: [] };
    }
    
    mergeOptions(customOptions, type) {
        const baseOptions = {
            ...this.defaultOptions,
            plugins: {
                legend: {
                    display: customOptions.showLegend !== false
                },
                tooltip: {
                    enabled: customOptions.showTooltip !== false
                }
            },
            scales: {}
        };
        
        // Type-specific options
        switch (type) {
            case 'scatter':
            case 'bubble':
            case 'line':
            case 'trajectory':
                baseOptions.scales = {
                    x: {
                        type: customOptions.xType || 'linear',
                        display: customOptions.showAxes !== false,
                        title: {
                            display: !!customOptions.xLabel,
                            text: customOptions.xLabel
                        }
                    },
                    y: {
                        type: customOptions.yType || 'linear',
                        display: customOptions.showAxes !== false,
                        title: {
                            display: !!customOptions.yLabel,
                            text: customOptions.yLabel
                        }
                    }
                };
                break;
                
            case 'bar':
            case 'distribution':
                baseOptions.scales = {
                    x: {
                        display: customOptions.showAxes !== false,
                        title: {
                            display: !!customOptions.xLabel,
                            text: customOptions.xLabel
                        }
                    },
                    y: {
                        beginAtZero: true,
                        display: customOptions.showAxes !== false,
                        title: {
                            display: !!customOptions.yLabel,
                            text: customOptions.yLabel
                        }
                    }
                };
                break;
        }
        
        // Merge with custom options
        return this.deepMerge(baseOptions, customOptions);
    }
    
    deepMerge(target, source) {
        const output = { ...target };
        
        if (this.isObject(target) && this.isObject(source)) {
            Object.keys(source).forEach(key => {
                if (this.isObject(source[key])) {
                    if (!(key in target)) {
                        output[key] = source[key];
                    } else {
                        output[key] = this.deepMerge(target[key], source[key]);
                    }
                } else {
                    output[key] = source[key];
                }
            });
        }
        
        return output;
    }
    
    isObject(item) {
        return item && typeof item === 'object' && !Array.isArray(item);
    }
    
    getDefaultColor(index, alpha = 1) {
        const colors = [
            `rgba(52, 152, 219, ${alpha})`,   // Blue
            `rgba(46, 204, 113, ${alpha})`,   // Green
            `rgba(155, 89, 182, ${alpha})`,   // Purple
            `rgba(241, 196, 15, ${alpha})`,   // Yellow
            `rgba(231, 76, 60, ${alpha})`,    // Red
            `rgba(230, 126, 34, ${alpha})`,   // Orange
            `rgba(149, 165, 166, ${alpha})`,  // Gray
            `rgba(26, 188, 156, ${alpha})`    // Turquoise
        ];
        
        return colors[index % colors.length];
    }
    
    async clear() {
        if (this.chart) {
            this.chart.clear();
        }
    }
    
    async destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
        
        if (this.canvas && this.canvas.parentElement) {
            this.canvas.remove();
        }
        
        this.canvas = null;
        this.container = null;
    }
    
    getCapabilities() {
        return {
            dimensions: [2],
            types: [
                'scatter', 'line', 'trajectory', 'timeseries',
                'bar', 'distribution', 'histogram',
                'pie', 'doughnut', 'radar', 'bubble'
            ],
            interactive: true,
            animated: true,
            responsive: true
        };
    }
}

// Register the renderer
VisualizationFactory.registerRenderer('chartjs', ChartJSRenderer);