# Tekton Shared Visualization Framework

A unified visualization framework for the Tekton CI platform, providing consistent visualizations across Noesis, Sophia, and other components.

## Overview

The Tekton Visualization Framework provides a pluggable architecture that allows different rendering engines to be used while maintaining a consistent API across all Tekton components.

## Architecture

### Core Components

- **`viz-core.js`** - Base visualization framework with abstract renderer interface
- **`tekton-viz.js`** - High-level API for common visualization patterns
- **`renderers/`** - Specific rendering implementations (Canvas, Chart.js, etc.)

### Design Principles

1. **Unified API** - Same interface across all Tekton components
2. **Pluggable Renderers** - Swap rendering engines without changing application code
3. **Performance Optimized** - Efficient handling of large datasets
4. **Accessible** - Built-in accessibility features and alternative representations

## Quick Start

### Basic Usage

```javascript
// Initialize visualizer with preferred renderer
const viz = new TektonViz('chartjs');
await viz.init('chart-container');

// Draw different visualization types
await viz.drawManifold(manifoldData);
await viz.drawTimeSeries(timeSeriesData);
await viz.drawNetwork(networkData);
```

### Renderer Selection

```javascript
// Use Chart.js for standard charts
const chartViz = new TektonViz('chartjs');

// Use Canvas for high-performance visualizations
const canvasViz = new TektonViz('canvas');

// Auto-select best renderer for context
const autoViz = new TektonViz(); // Uses default configured renderer
```

## Visualization Types

### Manifold Projections

Visualize high-dimensional data projected to 2D/3D space:

```javascript
const manifoldData = {
  points: [[x1, y1], [x2, y2], ...],
  connections: [[i, j], [i, j], ...],
  regions: [...],
  metadata: { intrinsic_dimension: 6 }
};

await viz.drawManifold(manifoldData, {
  pointSize: 4,
  connectionColor: 'rgba(150, 150, 150, 0.3)',
  showAxes: true
});
```

### Trajectories

Show paths through state space over time:

```javascript
const trajectory = [
  {x: 0, y: 1.0, time: 0},
  {x: 1, y: 1.5, time: 1},
  {x: 2, y: 0.8, time: 2}
];

await viz.drawTrajectory(trajectory, {
  lineColor: '#2ecc71',
  lineWidth: 2,
  showPoints: true
});
```

### Time Series

Display temporal data with multiple series:

```javascript
const timeSeries = {
  timestamps: [0, 1, 2, 3, 4],
  values: [1.0, 1.5, 2.0, 1.8, 2.2],
  metadata: { metric: 'accuracy', unit: 'percentage' }
};

await viz.drawTimeSeries(timeSeries, {
  color: '#3498db',
  fill: true,
  smooth: true
});
```

### Networks

Visualize graph structures with nodes and edges:

```javascript
const networkData = {
  nodes: [
    {id: 'node1', x: 100, y: 100, label: 'Component A'},
    {id: 'node2', x: 200, y: 150, label: 'Component B'}
  ],
  edges: [
    {source: 'node1', target: 'node2', weight: 0.8}
  ]
};

await viz.drawNetwork(networkData, {
  nodeSize: 10,
  edgeWidth: 2,
  showLabels: true
});
```

### Distributions

Display histograms and probability distributions:

```javascript
const distributionData = [1.2, 1.5, 2.1, 1.8, 2.3, 1.9, 2.0];

await viz.drawDistribution(distributionData, {
  bins: 20,
  color: '#9b59b6',
  showMean: true,
  showStdDev: true
});
```

### Heatmaps

Show 2D data intensity maps:

```javascript
const heatmapData = {
  values: [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
  rowLabels: ['A', 'B', 'C'],
  colLabels: ['X', 'Y', 'Z']
};

await viz.drawHeatmap(heatmapData, {
  colormap: 'viridis',
  showColorbar: true
});
```

## Renderers

### Canvas Renderer

High-performance renderer using HTML5 Canvas:

```javascript
const canvasViz = new TektonViz('canvas');
await canvasViz.init('canvas-container');

// Optimized for:
// - Large datasets (10,000+ points)
// - Real-time updates
// - Custom drawing operations
```

**Capabilities:**
- Dimensions: 2D, 3D (planned)
- Types: scatter, line, manifold, trajectory, network
- Interactive: zoom, pan, selection
- Animated: smooth transitions

### Chart.js Renderer

Standard charts using Chart.js library:

```javascript
const chartViz = new TektonViz('chartjs');
await chartViz.init('chart-container');

// Optimized for:
// - Standard chart types
// - Business dashboards
// - Responsive layouts
```

**Capabilities:**
- Dimensions: 2D
- Types: line, bar, scatter, timeseries, distribution
- Interactive: hover, click, zoom
- Animated: built-in animations

## Integration Guide

### Noesis Integration

For theoretical analysis visualizations:

```javascript
// In Noesis components
class ManifoldAnalyzer {
  constructor() {
    this.viz = new TektonViz('canvas'); // High-performance for complex manifolds
  }
  
  async visualizeManifold(analysis) {
    const manifoldData = {
      points: analysis.embedding_coordinates,
      connections: analysis.topology_connections,
      regions: analysis.identified_regions
    };
    
    await this.viz.drawManifold(manifoldData);
  }
}
```

### Sophia Integration

For experimental validation visualizations:

```javascript
// In Sophia components
class ExperimentVisualizer {
  constructor() {
    this.viz = new TektonViz('chartjs'); // Standard charts for metrics
  }
  
  async visualizeResults(experimentData) {
    // Performance over time
    await this.viz.drawTimeSeries(experimentData.performance_timeline);
    
    // Component comparison
    await this.viz.drawComparison(experimentData.component_metrics);
  }
}
```

## Data Formats

### Standard Formats

All visualizations use standardized data formats for consistency:

```javascript
// Point data
{
  x: number,
  y: number,
  z?: number,        // Optional for 3D
  color?: string,    // Optional color override
  size?: number,     // Optional size override
  label?: string     // Optional label
}

// Time series data
{
  timestamps: number[],
  values: number[],
  metadata?: {
    metric: string,
    unit: string,
    description: string
  }
}

// Network data
{
  nodes: Array<{
    id: string,
    x?: number,
    y?: number,
    label?: string,
    color?: string,
    size?: number
  }>,
  edges: Array<{
    source: string,
    target: string,
    weight?: number,
    color?: string,
    width?: number
  }>
}
```

## Performance Guidelines

### Large Datasets

For datasets with > 1,000 points:

```javascript
// Use Canvas renderer for better performance
const viz = new TektonViz('canvas');

// Enable data decimation
await viz.drawScatter(largeDataset, {
  decimation: {
    enabled: true,
    algorithm: 'distance_based',
    threshold: 5000
  }
});
```

### Real-time Updates

For streaming data:

```javascript
// Minimize redraws by updating incrementally
class RealTimeVisualizer {
  async updateData(newPoint) {
    // Add point without full redraw
    await this.viz.addPoint(newPoint);
    
    // Limit history to maintain performance
    if (this.dataPoints.length > 10000) {
      this.dataPoints = this.dataPoints.slice(-5000);
      await this.viz.redraw();
    }
  }
}
```

## Accessibility

### Color Accessibility

```javascript
// Use colorblind-safe palettes
await viz.drawScatter(data, {
  colorPalette: 'viridis',  // Perceptually uniform
  alternativeEncoding: 'shape'  // Use shapes in addition to color
});
```

### Keyboard Navigation

```javascript
// Enable keyboard navigation
await viz.init('container', {
  accessibility: {
    keyboard: true,
    announcements: true,
    alternativeText: true
  }
});
```

### Screen Reader Support

```javascript
// Provide data table alternative
await viz.drawChart(data, {
  accessibility: {
    description: 'Performance metrics over time',
    dataTable: true,  // Generate accessible data table
    summaryStats: true  // Include summary statistics
  }
});
```

## Error Handling

### Graceful Degradation

```javascript
try {
  const viz = new TektonViz('webgl');  // Preferred renderer
  await viz.init('container');
} catch (error) {
  console.warn('WebGL not available, falling back to Canvas');
  const viz = new TektonViz('canvas');  // Fallback renderer
  await viz.init('container');
}
```

### Data Validation

```javascript
// Automatic data validation and sanitization
const cleanData = VizUtils.validateAndClean(rawData, {
  removeNaN: true,
  removeInfinite: true,
  requireFields: ['x', 'y']
});

await viz.drawScatter(cleanData);
```

## Extension Points

### Custom Renderers

Create custom renderers by extending the base class:

```javascript
class CustomRenderer extends VisualizationRenderer {
  async initialize(containerId, options) {
    // Initialize custom rendering context
  }
  
  async render(data, type, options) {
    // Implement custom rendering logic
  }
  
  getCapabilities() {
    return {
      dimensions: [2, 3],
      types: ['custom_type'],
      interactive: true,
      animated: true
    };
  }
}

// Register custom renderer
VisualizationFactory.registerRenderer('custom', CustomRenderer);
```

### Custom Visualization Types

Add new visualization types:

```javascript
class ExtendedTektonViz extends TektonViz {
  async drawCustomVisualization(data, options) {
    // Prepare data for custom visualization
    const preparedData = this.prepareCustomData(data);
    
    // Render using underlying renderer
    await this.renderer.render(preparedData, 'custom_type', options);
  }
}
```

## Browser Compatibility

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

### Polyfills

For older browsers, include:

```html
<!-- ES6 Promise polyfill -->
<script src="https://cdn.jsdelivr.net/npm/es6-promise@4/dist/es6-promise.auto.min.js"></script>

<!-- Fetch polyfill -->
<script src="https://cdn.jsdelivr.net/npm/whatwg-fetch@3.6.2/dist/fetch.umd.js"></script>
```

## API Reference

See [API_REFERENCE.md](./API_REFERENCE.md) for complete API documentation.

## Examples

See [examples/](./examples/) directory for complete working examples.

## Contributing

1. Follow the established architecture patterns
2. Add tests for new features
3. Update documentation
4. Ensure accessibility compliance
5. Maintain performance benchmarks

## License

Part of the Tekton CI Platform. See project root for license information.