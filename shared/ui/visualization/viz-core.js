/**
 * Core visualization abstraction layer for Tekton
 * Provides a pluggable architecture for different rendering engines
 */

/**
 * Abstract base class for all visualization renderers
 * All renderers must implement this interface
 */
class VisualizationRenderer {
    /**
     * Initialize the renderer with a container element
     * @param {string} containerId - ID of the DOM element to render into
     * @param {Object} options - Renderer-specific options
     */
    async initialize(containerId, options = {}) {
        throw new Error("Renderer must implement initialize()");
    }
    
    /**
     * Render data using the specified visualization type
     * @param {any} data - Data to visualize
     * @param {string} type - Type of visualization (scatter, trajectory, manifold, etc.)
     * @param {Object} options - Visualization-specific options
     */
    async render(data, type, options = {}) {
        throw new Error("Renderer must implement render()");
    }
    
    /**
     * Clear the current visualization
     */
    async clear() {
        throw new Error("Renderer must implement clear()");
    }
    
    /**
     * Clean up and destroy the renderer
     */
    async destroy() {
        throw new Error("Renderer must implement destroy()");
    }
    
    /**
     * Get renderer capabilities
     * @returns {Object} Object describing what this renderer can do
     */
    getCapabilities() {
        return {
            dimensions: [2], // 2D, 3D, etc.
            types: [],       // scatter, line, manifold, etc.
            interactive: false,
            animated: false
        };
    }
}

/**
 * Factory for creating and managing visualization renderers
 */
class VisualizationFactory {
    static renderers = new Map();
    static defaultRenderer = 'canvas';
    
    /**
     * Register a new renderer
     * @param {string} name - Unique name for the renderer
     * @param {class} rendererClass - Class that extends VisualizationRenderer
     */
    static registerRenderer(name, rendererClass) {
        if (!(rendererClass.prototype instanceof VisualizationRenderer)) {
            throw new Error(`Renderer must extend VisualizationRenderer`);
        }
        this.renderers.set(name, rendererClass);
    }
    
    /**
     * Create a renderer instance
     * @param {string} name - Name of the renderer to create
     * @returns {VisualizationRenderer} Renderer instance
     */
    static createRenderer(name = null) {
        const rendererName = name || this.defaultRenderer;
        const RendererClass = this.renderers.get(rendererName);
        
        if (!RendererClass) {
            throw new Error(`Unknown renderer: ${rendererName}`);
        }
        
        return new RendererClass();
    }
    
    /**
     * Get list of available renderers
     * @returns {string[]} Array of renderer names
     */
    static getAvailableRenderers() {
        return Array.from(this.renderers.keys());
    }
    
    /**
     * Set the default renderer
     * @param {string} name - Name of the renderer to use as default
     */
    static setDefaultRenderer(name) {
        if (!this.renderers.has(name)) {
            throw new Error(`Renderer not found: ${name}`);
        }
        this.defaultRenderer = name;
    }
}

/**
 * Common visualization utilities
 */
class VizUtils {
    /**
     * Scale data to fit within bounds
     * @param {number[]} values - Array of values to scale
     * @param {number} min - Minimum output value
     * @param {number} max - Maximum output value
     * @returns {number[]} Scaled values
     */
    static scaleLinear(values, min, max) {
        const inputMin = Math.min(...values);
        const inputMax = Math.max(...values);
        const scale = (max - min) / (inputMax - inputMin);
        
        return values.map(v => (v - inputMin) * scale + min);
    }
    
    /**
     * Convert high-dimensional point to 2D using first two components
     * @param {number[]} point - High-dimensional point
     * @returns {{x: number, y: number}} 2D point
     */
    static projectTo2D(point) {
        return {
            x: point[0] || 0,
            y: point[1] || 0
        };
    }
    
    /**
     * Generate a color from a continuous value
     * @param {number} value - Value between 0 and 1
     * @param {string} colormap - Name of colormap (viridis, plasma, etc.)
     * @returns {string} CSS color string
     */
    static valueToColor(value, colormap = 'viridis') {
        // Simple viridis approximation
        const r = Math.floor(68 + value * (59 - 68));
        const g = Math.floor(1 + value * (130 - 1));
        const b = Math.floor(84 + value * (121 - 84));
        
        return `rgb(${r}, ${g}, ${b})`;
    }
    
    /**
     * Calculate bounds for a dataset
     * @param {Array<{x: number, y: number}>} points - Array of 2D points
     * @returns {{minX: number, maxX: number, minY: number, maxY: number}} Bounds
     */
    static calculateBounds(points) {
        if (!points.length) {
            return { minX: 0, maxX: 1, minY: 0, maxY: 1 };
        }
        
        const xs = points.map(p => p.x);
        const ys = points.map(p => p.y);
        
        return {
            minX: Math.min(...xs),
            maxX: Math.max(...xs),
            minY: Math.min(...ys),
            maxY: Math.max(...ys)
        };
    }
}

// Export for use in Tekton components
window.VisualizationRenderer = VisualizationRenderer;
window.VisualizationFactory = VisualizationFactory;
window.VizUtils = VizUtils;