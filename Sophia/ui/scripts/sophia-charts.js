/**
 * Sophia Charts Implementation
 * 
 * This script provides visualization capabilities for the Sophia dashboard,
 * including charts for metrics, intelligence profiles, and experiments using D3.js.
 */

// Initialize the charts system when the DOM is loaded
document.addEventListener('DOMContentLoaded', initCharts);

// Global chart references and configurations
const chartConfig = {
  colors: [
    '#4285F4', '#EA4335', '#FBBC05', '#34A853', 
    '#8F8F8F', '#46BFBD', '#F7464A', '#FDB45C'
  ],
  defaultHeight: 300,
  animationDuration: 750,
  fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif"
};

// Chart instances 
let charts = {
  performance: null,
  resource: null,
  communication: null,
  error: null,
  intelligence: null,
  comparison: null,
  experimentResults: null
};

/**
 * Initialize all charts
 */
function initCharts() {
  console.log('Initializing Sophia charts...');
  
  // Load D3.js if not already available
  if (typeof d3 === 'undefined') {
    loadD3();
    return;
  }
  
  // Set up chart containers
  setupChartContainers();
  
  // Create empty charts (will be populated with data later)
  initPerformanceChart();
  initResourceChart();
  initCommunicationChart();
  initErrorChart();
  initIntelligenceRadarChart();
  
  console.log('Sophia charts initialized');
}

/**
 * Load D3.js dynamically if not available
 */
function loadD3() {
  console.log('Loading D3.js library...');
  
  const script = document.createElement('script');
  script.src = 'https://d3js.org/d3.v7.min.js';
  script.onload = initCharts;
  document.head.appendChild(script);
}

/**
 * Set up chart containers with proper dimensions
 */
function setupChartContainers() {
  const chartContainers = document.querySelectorAll('.sophia-chart');
  
  chartContainers.forEach(container => {
    // Ensure container has relative positioning for SVG placement
    if (window.getComputedStyle(container).position === 'static') {
      container.style.position = 'relative';
    }
    
    // Set minimum height for chart areas
    if (container.clientHeight < chartConfig.defaultHeight) {
      container.style.height = `${chartConfig.defaultHeight}px`;
    }
  });
}

/**
 * Initialize the performance metrics chart
 */
function initPerformanceChart() {
  const container = document.getElementById('sophia-performance-chart');
  if (!container) return;
  
  // Clear container
  container.innerHTML = '';
  
  // Create SVG element
  const width = container.clientWidth;
  const height = container.clientHeight;
  
  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width / 20}, ${height / 20})`);
  
  // Add placeholder text
  svg.append('text')
    .attr('x', width / 2 - 50)
    .attr('y', height / 2)
    .text('No performance data available')
    .attr('fill', '#666')
    .attr('font-family', chartConfig.fontFamily);
  
  // Store reference to chart
  charts.performance = {
    svg: svg,
    width: width,
    height: height
  };
}

/**
 * Initialize the resource usage chart
 */
function initResourceChart() {
  const container = document.getElementById('sophia-resource-chart');
  if (!container) return;
  
  // Clear container
  container.innerHTML = '';
  
  // Create SVG element
  const width = container.clientWidth;
  const height = container.clientHeight;
  
  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width / 20}, ${height / 20})`);
  
  // Add placeholder text
  svg.append('text')
    .attr('x', width / 2 - 50)
    .attr('y', height / 2)
    .text('No resource data available')
    .attr('fill', '#666')
    .attr('font-family', chartConfig.fontFamily);
  
  // Store reference to chart
  charts.resource = {
    svg: svg,
    width: width,
    height: height
  };
}

/**
 * Initialize the communication chart
 */
function initCommunicationChart() {
  const container = document.getElementById('sophia-communication-chart');
  if (!container) return;
  
  // Clear container
  container.innerHTML = '';
  
  // Create SVG element
  const width = container.clientWidth;
  const height = container.clientHeight;
  
  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width / 20}, ${height / 20})`);
  
  // Add placeholder text
  svg.append('text')
    .attr('x', width / 2 - 50)
    .attr('y', height / 2)
    .text('No communication data available')
    .attr('fill', '#666')
    .attr('font-family', chartConfig.fontFamily);
  
  // Store reference to chart
  charts.communication = {
    svg: svg,
    width: width,
    height: height
  };
}

/**
 * Initialize the error rates chart
 */
function initErrorChart() {
  const container = document.getElementById('sophia-error-chart');
  if (!container) return;
  
  // Clear container
  container.innerHTML = '';
  
  // Create SVG element
  const width = container.clientWidth;
  const height = container.clientHeight;
  
  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width / 20}, ${height / 20})`);
  
  // Add placeholder text
  svg.append('text')
    .attr('x', width / 2 - 50)
    .attr('y', height / 2)
    .text('No error data available')
    .attr('fill', '#666')
    .attr('font-family', chartConfig.fontFamily);
  
  // Store reference to chart
  charts.error = {
    svg: svg,
    width: width,
    height: height
  };
}

/**
 * Initialize the intelligence radar chart
 */
function initIntelligenceRadarChart() {
  const container = document.getElementById('sophia-radar-chart');
  if (!container) return;
  
  // Clear container
  container.innerHTML = '';
  
  // Create SVG element
  const width = container.clientWidth;
  const height = container.clientHeight;
  
  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width / 2}, ${height / 2})`);
  
  // Add placeholder text
  svg.append('text')
    .attr('x', 0)
    .attr('y', 0)
    .attr('text-anchor', 'middle')
    .text('No intelligence profile available')
    .attr('fill', '#666')
    .attr('font-family', chartConfig.fontFamily);
  
  // Store reference to chart
  charts.intelligence = {
    svg: svg,
    width: width,
    height: height
  };
}

/**
 * Update the performance metrics chart with new data
 * @param {Object} metricsData - Performance metrics data
 */
function updatePerformanceChart(metricsData) {
  console.log('Updating performance chart with data:', metricsData);
  
  if (!charts.performance || !metricsData || !metricsData.performance) {
    console.warn('Performance chart or data not available');
    return;
  }
  
  const svg = charts.performance.svg;
  const width = charts.performance.width;
  const height = charts.performance.height;
  
  // Clear previous content
  svg.selectAll('*').remove();
  
  // Extract performance metrics
  const performanceData = metricsData.performance;
  
  // Check if we have time series data
  if (Array.isArray(performanceData) && performanceData.length > 0) {
    // Create scales
    const timeScale = d3.scaleTime()
      .domain(d3.extent(performanceData, d => new Date(d.timestamp)))
      .range([40, width - 40]);
      
    const valueScale = d3.scaleLinear()
      .domain([0, d3.max(performanceData, d => d.value) * 1.1])
      .range([height - 40, 40]);
      
    // Create line generator
    const line = d3.line()
      .x(d => timeScale(new Date(d.timestamp)))
      .y(d => valueScale(d.value))
      .curve(d3.curveMonotoneX);
      
    // Draw line
    svg.append('path')
      .datum(performanceData)
      .attr('fill', 'none')
      .attr('stroke', chartConfig.colors[0])
      .attr('stroke-width', 2)
      .attr('d', line);
      
    // Add dots for data points
    svg.selectAll('.dot')
      .data(performanceData)
      .enter()
      .append('circle')
      .attr('class', 'dot')
      .attr('cx', d => timeScale(new Date(d.timestamp)))
      .attr('cy', d => valueScale(d.value))
      .attr('r', 4)
      .attr('fill', chartConfig.colors[0]);
      
    // Add axes
    const xAxis = d3.axisBottom(timeScale)
      .ticks(5)
      .tickFormat(d3.timeFormat('%H:%M:%S'));
      
    const yAxis = d3.axisLeft(valueScale)
      .ticks(5);
      
    svg.append('g')
      .attr('transform', `translate(0, ${height - 40})`)
      .call(xAxis);
      
    svg.append('g')
      .attr('transform', 'translate(40, 0)')
      .call(yAxis);
      
    // Add labels
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', height - 5)
      .attr('text-anchor', 'middle')
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '12px')
      .text('Time');
      
    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '12px')
      .text('Latency (ms)');
  } else {
    // No data available
    svg.append('text')
      .attr('x', width / 2 - 50)
      .attr('y', height / 2)
      .text('No performance data available')
      .attr('fill', '#666')
      .attr('font-family', chartConfig.fontFamily);
  }
}

/**
 * Update the resource usage chart with new data
 * @param {Object} metricsData - Resource usage metrics data
 */
function updateResourceChart(metricsData) {
  console.log('Updating resource chart with data:', metricsData);
  
  if (!charts.resource || !metricsData || !metricsData.resource) {
    console.warn('Resource chart or data not available');
    return;
  }
  
  const svg = charts.resource.svg;
  const width = charts.resource.width;
  const height = charts.resource.height;
  
  // Clear previous content
  svg.selectAll('*').remove();
  
  // Extract resource metrics
  const resourceData = metricsData.resource;
  
  // Check if we have component resource data
  if (typeof resourceData === 'object' && Object.keys(resourceData).length > 0) {
    // Convert data for bar chart
    const components = Object.keys(resourceData);
    const barData = components.map(component => ({
      component,
      memory: resourceData[component].memory || 0,
      cpu: resourceData[component].cpu || 0
    }));
    
    // Create scales
    const xScale = d3.scaleBand()
      .domain(components)
      .range([40, width - 40])
      .padding(0.2);
      
    const yScale = d3.scaleLinear()
      .domain([0, d3.max(barData, d => Math.max(d.memory, d.cpu)) * 1.1])
      .range([height - 40, 40]);
      
    // Draw bars
    svg.selectAll('.memory-bar')
      .data(barData)
      .enter()
      .append('rect')
      .attr('class', 'memory-bar')
      .attr('x', d => xScale(d.component))
      .attr('y', d => yScale(d.memory))
      .attr('width', xScale.bandwidth() / 2)
      .attr('height', d => height - 40 - yScale(d.memory))
      .attr('fill', chartConfig.colors[0]);
      
    svg.selectAll('.cpu-bar')
      .data(barData)
      .enter()
      .append('rect')
      .attr('class', 'cpu-bar')
      .attr('x', d => xScale(d.component) + xScale.bandwidth() / 2)
      .attr('y', d => yScale(d.cpu))
      .attr('width', xScale.bandwidth() / 2)
      .attr('height', d => height - 40 - yScale(d.cpu))
      .attr('fill', chartConfig.colors[1]);
      
    // Add axes
    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale).ticks(5);
    
    svg.append('g')
      .attr('transform', `translate(0, ${height - 40})`)
      .call(xAxis)
      .selectAll('text')
      .attr('transform', 'rotate(-45)')
      .attr('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em');
      
    svg.append('g')
      .attr('transform', 'translate(40, 0)')
      .call(yAxis);
      
    // Add legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 120}, 20)`);
      
    legend.append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', chartConfig.colors[0]);
      
    legend.append('text')
      .attr('x', 20)
      .attr('y', 12)
      .text('Memory')
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '12px');
      
    legend.append('rect')
      .attr('x', 0)
      .attr('y', 25)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', chartConfig.colors[1]);
      
    legend.append('text')
      .attr('x', 20)
      .attr('y', 37)
      .text('CPU')
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '12px');
  } else {
    // No data available
    svg.append('text')
      .attr('x', width / 2 - 50)
      .attr('y', height / 2)
      .text('No resource data available')
      .attr('fill', '#666')
      .attr('font-family', chartConfig.fontFamily);
  }
}

/**
 * Update the communication chart with new data
 * @param {Object} metricsData - Communication metrics data
 */
function updateCommunicationChart(metricsData) {
  console.log('Updating communication chart with data:', metricsData);
  
  if (!charts.communication || !metricsData || !metricsData.communication) {
    console.warn('Communication chart or data not available');
    return;
  }
  
  const svg = charts.communication.svg;
  const width = charts.communication.width;
  const height = charts.communication.height;
  
  // Clear previous content
  svg.selectAll('*').remove();
  
  // Extract communication metrics
  const communicationData = metricsData.communication;
  
  // Check if we have node and link data for force-directed graph
  if (communicationData.nodes && communicationData.links) {
    // Create force simulation
    const simulation = d3.forceSimulation(communicationData.nodes)
      .force('link', d3.forceLink(communicationData.links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));
      
    // Draw links
    const links = svg.append('g')
      .selectAll('line')
      .data(communicationData.links)
      .enter()
      .append('line')
      .attr('stroke-width', d => Math.sqrt(d.value))
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6);
      
    // Draw nodes
    const nodes = svg.append('g')
      .selectAll('circle')
      .data(communicationData.nodes)
      .enter()
      .append('circle')
      .attr('r', 10)
      .attr('fill', (d, i) => chartConfig.colors[i % chartConfig.colors.length])
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));
        
    // Add node labels
    const labels = svg.append('g')
      .selectAll('text')
      .data(communicationData.nodes)
      .enter()
      .append('text')
      .text(d => d.id)
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '10px')
      .attr('dx', 12)
      .attr('dy', 4);
      
    // Set up tick function
    simulation.on('tick', () => {
      links
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
        
      nodes
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
        
      labels
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });
    
    // Drag functions
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    
    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }
    
    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
    
    // Add title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 20)
      .attr('text-anchor', 'middle')
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '14px')
      .text('Component Communication Network');
  } else {
    // No data available
    svg.append('text')
      .attr('x', width / 2 - 50)
      .attr('y', height / 2)
      .text('No communication data available')
      .attr('fill', '#666')
      .attr('font-family', chartConfig.fontFamily);
  }
}

/**
 * Update the error rates chart with new data
 * @param {Object} metricsData - Error metrics data
 */
function updateErrorChart(metricsData) {
  console.log('Updating error chart with data:', metricsData);
  
  if (!charts.error || !metricsData || !metricsData.errors) {
    console.warn('Error chart or data not available');
    return;
  }
  
  const svg = charts.error.svg;
  const width = charts.error.width;
  const height = charts.error.height;
  
  // Clear previous content
  svg.selectAll('*').remove();
  
  // Extract error metrics
  const errorData = metricsData.errors;
  
  // Check if we have component error data
  if (Array.isArray(errorData) && errorData.length > 0) {
    // Create pie chart data
    const pieData = d3.pie()
      .value(d => d.count)
      .sort(null)(errorData);
      
    // Create arc generator
    const radius = Math.min(width, height) / 2 - 40;
    const arc = d3.arc()
      .innerRadius(radius * 0.5)
      .outerRadius(radius);
      
    // Move origin to center
    svg.attr('transform', `translate(${width / 2}, ${height / 2})`);
    
    // Draw arcs
    const arcs = svg.selectAll('.arc')
      .data(pieData)
      .enter()
      .append('g')
      .attr('class', 'arc');
      
    arcs.append('path')
      .attr('d', arc)
      .attr('fill', (d, i) => chartConfig.colors[i % chartConfig.colors.length]);
      
    // Add labels
    const labelArc = d3.arc()
      .innerRadius(radius * 0.8)
      .outerRadius(radius * 0.8);
      
    arcs.append('text')
      .attr('transform', d => `translate(${labelArc.centroid(d)})`)
      .attr('dy', '.35em')
      .attr('text-anchor', 'middle')
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '12px')
      .attr('fill', '#fff')
      .text(d => d.data.type);
      
    // Add legend
    const legend = svg.append('g')
      .attr('transform', `translate(${radius + 20}, -${radius})`);
      
    errorData.forEach((d, i) => {
      const legendRow = legend.append('g')
        .attr('transform', `translate(0, ${i * 20})`);
        
      legendRow.append('rect')
        .attr('width', 15)
        .attr('height', 15)
        .attr('fill', chartConfig.colors[i % chartConfig.colors.length]);
        
      legendRow.append('text')
        .attr('x', 20)
        .attr('y', 12)
        .attr('font-family', chartConfig.fontFamily)
        .attr('font-size', '12px')
        .text(`${d.type} (${d.count})`);
    });
    
    // Add title
    svg.append('text')
      .attr('y', -radius - 20)
      .attr('text-anchor', 'middle')
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '14px')
      .text('Error Distribution');
  } else {
    // Reset transform for text
    svg.attr('transform', `translate(0, 0)`);
    
    // No data available
    svg.append('text')
      .attr('x', width / 2 - 50)
      .attr('y', height / 2)
      .text('No error data available')
      .attr('fill', '#666')
      .attr('font-family', chartConfig.fontFamily);
  }
}

/**
 * Update the intelligence radar chart with profile data
 * @param {Object} profileData - Intelligence profile data
 */
function updateIntelligenceRadarChart(profileData) {
  console.log('Updating intelligence radar chart with data:', profileData);
  
  if (!charts.intelligence || !profileData || !profileData.dimensions) {
    console.warn('Intelligence chart or data not available');
    return;
  }
  
  const svg = charts.intelligence.svg;
  const width = charts.intelligence.width;
  const height = charts.intelligence.height;
  
  // Clear previous content
  svg.selectAll('*').remove();
  
  // Extract dimensions and scores
  const dimensions = Object.keys(profileData.dimensions);
  const scores = dimensions.map(d => profileData.dimensions[d].score);
  
  if (dimensions.length > 0) {
    // Set up radar chart parameters
    const radius = Math.min(width, height) / 2 - 40;
    const angleSlice = Math.PI * 2 / dimensions.length;
    
    // Create scales
    const rScale = d3.scaleLinear()
      .domain([0, 1])  // scores are 0-1
      .range([0, radius]);
      
    // Create axes
    const axes = svg.selectAll('.axis')
      .data(dimensions)
      .enter()
      .append('g')
      .attr('class', 'axis');
      
    // Draw axis lines
    axes.append('line')
      .attr('x1', 0)
      .attr('y1', 0)
      .attr('x2', (d, i) => rScale(1) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y2', (d, i) => rScale(1) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr('stroke', 'gray')
      .attr('stroke-width', 1);
      
    // Draw axis labels
    axes.append('text')
      .attr('x', (d, i) => rScale(1.1) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y', (d, i) => rScale(1.1) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr('text-anchor', (d, i) => {
        const angle = angleSlice * i;
        if (angle === 0 || angle === Math.PI) return 'middle';
        return angle < Math.PI ? 'start' : 'end';
      })
      .attr('dy', '0.35em')
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '10px')
      .text(d => d);
      
    // Draw concentric circles
    const levels = 5;
    const circles = svg.selectAll('.level')
      .data(d3.range(1, levels + 1).reverse())
      .enter()
      .append('circle')
      .attr('class', 'level')
      .attr('r', d => radius * d / levels)
      .attr('fill', 'none')
      .attr('stroke', 'gray')
      .attr('stroke-width', 0.5)
      .attr('stroke-opacity', 0.5);
      
    // Create radar line function
    const radarLine = d3.lineRadial()
      .angle((d, i) => angleSlice * i)
      .radius(d => rScale(d))
      .curve(d3.curveLinearClosed);
      
    // Draw radar area
    svg.append('path')
      .datum(scores)
      .attr('class', 'radar-area')
      .attr('d', radarLine)
      .attr('fill', chartConfig.colors[0])
      .attr('fill-opacity', 0.6)
      .attr('stroke', chartConfig.colors[0])
      .attr('stroke-width', 2);
      
    // Draw radar points
    svg.selectAll('.radar-point')
      .data(scores)
      .enter()
      .append('circle')
      .attr('class', 'radar-point')
      .attr('cx', (d, i) => rScale(d) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('cy', (d, i) => rScale(d) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr('r', 4)
      .attr('fill', chartConfig.colors[0]);
      
    // Add title
    svg.append('text')
      .attr('y', -radius - 20)
      .attr('text-anchor', 'middle')
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '14px')
      .text(`Intelligence Profile: ${profileData.component_id}`);
      
    // Add legend with score labels
    const legend = svg.append('g')
      .attr('transform', `translate(${radius + 20}, -20)`);
      
    dimensions.forEach((dim, i) => {
      const score = profileData.dimensions[dim].score;
      const formattedScore = (score * 100).toFixed(0);
      
      const legendRow = legend.append('g')
        .attr('transform', `translate(0, ${i * 20})`);
        
      legendRow.append('rect')
        .attr('width', 12)
        .attr('height', 12)
        .attr('fill', chartConfig.colors[0]);
        
      legendRow.append('text')
        .attr('x', 20)
        .attr('y', 10)
        .attr('font-family', chartConfig.fontFamily)
        .attr('font-size', '10px')
        .text(`${dim}: ${formattedScore}%`);
    });
  } else {
    // No data available
    svg.append('text')
      .attr('x', 0)
      .attr('y', 0)
      .attr('text-anchor', 'middle')
      .text('No intelligence profile available')
      .attr('fill', '#666')
      .attr('font-family', chartConfig.fontFamily);
  }
}

/**
 * Compare intelligence profiles of two components
 * @param {Object} component1 - First component's intelligence profile
 * @param {Object} component2 - Second component's intelligence profile
 */
function compareIntelligenceProfiles(component1, component2) {
  console.log('Comparing intelligence profiles:', component1, component2);
  
  const container = document.getElementById('sophia-comparison-chart');
  if (!container) return;
  
  // Create SVG if not already created
  if (!charts.comparison) {
    // Clear container
    container.innerHTML = '';
    
    // Create SVG element
    const width = container.clientWidth;
    const height = container.clientHeight || 400;
    
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);
      
    // Store reference to chart
    charts.comparison = {
      svg: svg,
      width: width,
      height: height
    };
  }
  
  const svg = charts.comparison.svg;
  const width = charts.comparison.width;
  const height = charts.comparison.height;
  
  // Clear previous content
  svg.selectAll('*').remove();
  
  // Check if we have data for both components
  if (!component1 || !component1.dimensions || !component2 || !component2.dimensions) {
    svg.append('text')
      .attr('x', 0)
      .attr('y', 0)
      .attr('text-anchor', 'middle')
      .text('Unable to compare: missing data')
      .attr('fill', '#666')
      .attr('font-family', chartConfig.fontFamily);
    return;
  }
  
  // Get common dimensions
  const dimensions = Object.keys(component1.dimensions).filter(dim => 
    Object.keys(component2.dimensions).includes(dim));
    
  // Create data arrays for each component
  const scores1 = dimensions.map(d => component1.dimensions[d].score);
  const scores2 = dimensions.map(d => component2.dimensions[d].score);
  
  if (dimensions.length > 0) {
    // Set up radar chart parameters
    const radius = Math.min(width, height) / 2 - 40;
    const angleSlice = Math.PI * 2 / dimensions.length;
    
    // Create scales
    const rScale = d3.scaleLinear()
      .domain([0, 1])
      .range([0, radius]);
      
    // Create axes
    const axes = svg.selectAll('.axis')
      .data(dimensions)
      .enter()
      .append('g')
      .attr('class', 'axis');
      
    // Draw axis lines
    axes.append('line')
      .attr('x1', 0)
      .attr('y1', 0)
      .attr('x2', (d, i) => rScale(1) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y2', (d, i) => rScale(1) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr('stroke', 'gray')
      .attr('stroke-width', 1);
      
    // Draw axis labels
    axes.append('text')
      .attr('x', (d, i) => rScale(1.1) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y', (d, i) => rScale(1.1) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr('text-anchor', (d, i) => {
        const angle = angleSlice * i;
        if (angle === 0 || angle === Math.PI) return 'middle';
        return angle < Math.PI ? 'start' : 'end';
      })
      .attr('dy', '0.35em')
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '10px')
      .text(d => d);
      
    // Draw concentric circles
    const levels = 5;
    const circles = svg.selectAll('.level')
      .data(d3.range(1, levels + 1).reverse())
      .enter()
      .append('circle')
      .attr('class', 'level')
      .attr('r', d => radius * d / levels)
      .attr('fill', 'none')
      .attr('stroke', 'gray')
      .attr('stroke-width', 0.5)
      .attr('stroke-opacity', 0.5);
      
    // Create radar line function
    const radarLine = d3.lineRadial()
      .angle((d, i) => angleSlice * i)
      .radius(d => rScale(d))
      .curve(d3.curveLinearClosed);
      
    // Draw radar area for component 1
    svg.append('path')
      .datum(scores1)
      .attr('class', 'radar-area-1')
      .attr('d', radarLine)
      .attr('fill', chartConfig.colors[0])
      .attr('fill-opacity', 0.3)
      .attr('stroke', chartConfig.colors[0])
      .attr('stroke-width', 2);
      
    // Draw radar area for component 2
    svg.append('path')
      .datum(scores2)
      .attr('class', 'radar-area-2')
      .attr('d', radarLine)
      .attr('fill', chartConfig.colors[1])
      .attr('fill-opacity', 0.3)
      .attr('stroke', chartConfig.colors[1])
      .attr('stroke-width', 2);
      
    // Draw radar points for component 1
    svg.selectAll('.radar-point-1')
      .data(scores1)
      .enter()
      .append('circle')
      .attr('class', 'radar-point-1')
      .attr('cx', (d, i) => rScale(d) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('cy', (d, i) => rScale(d) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr('r', 4)
      .attr('fill', chartConfig.colors[0]);
      
    // Draw radar points for component 2
    svg.selectAll('.radar-point-2')
      .data(scores2)
      .enter()
      .append('circle')
      .attr('class', 'radar-point-2')
      .attr('cx', (d, i) => rScale(d) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('cy', (d, i) => rScale(d) * Math.sin(angleSlice * i - Math.PI / 2))
      .attr('r', 4)
      .attr('fill', chartConfig.colors[1]);
      
    // Add title
    svg.append('text')
      .attr('y', -radius - 20)
      .attr('text-anchor', 'middle')
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '14px')
      .text(`Intelligence Profile Comparison`);
      
    // Add legend
    const legend = svg.append('g')
      .attr('transform', `translate(${radius + 20}, -20)`);
      
    // Component 1 legend
    legend.append('rect')
      .attr('width', 12)
      .attr('height', 12)
      .attr('fill', chartConfig.colors[0]);
      
    legend.append('text')
      .attr('x', 20)
      .attr('y', 10)
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '10px')
      .text(component1.component_id);
      
    // Component 2 legend
    legend.append('rect')
      .attr('width', 12)
      .attr('height', 12)
      .attr('y', 20)
      .attr('fill', chartConfig.colors[1]);
      
    legend.append('text')
      .attr('x', 20)
      .attr('y', 30)
      .attr('font-family', chartConfig.fontFamily)
      .attr('font-size', '10px')
      .text(component2.component_id);
  } else {
    // No common dimensions
    svg.append('text')
      .attr('x', 0)
      .attr('y', 0)
      .attr('text-anchor', 'middle')
      .text('No common intelligence dimensions to compare')
      .attr('fill', '#666')
      .attr('font-family', chartConfig.fontFamily);
  }
}

/**
 * Update experiment results visualization
 * @param {Object} experimentData - Experiment results data
 */
function updateExperimentResults(experimentData) {
  console.log('Updating experiment results visualization:', experimentData);
  
  const container = document.getElementById('sophia-experiment-results');
  if (!container) return;
  
  // Check if experiment has results
  if (!experimentData || !experimentData.results || !experimentData.metrics) {
    container.innerHTML = '<div class="alert alert-info">No results available for this experiment yet.</div>';
    return;
  }
  
  // Clear container
  container.innerHTML = '';
  
  // Create results visualization based on experiment type
  switch (experimentData.experiment_type) {
    case 'a_b_test':
      createABTestVisualization(experimentData, container);
      break;
    case 'multivariate':
      createMultivariateVisualization(experimentData, container);
      break;
    case 'before_after':
      createBeforeAfterVisualization(experimentData, container);
      break;
    default:
      // Generic results table
      createGenericResultsTable(experimentData, container);
  }
}

/**
 * Create A/B test visualization
 * @param {Object} experimentData - Experiment data
 * @param {HTMLElement} container - Container element
 */
function createABTestVisualization(experimentData, container) {
  // Create comparison chart for A/B test
  const chartDiv = document.createElement('div');
  chartDiv.className = 'sophia-experiment-chart';
  chartDiv.style.height = '300px';
  container.appendChild(chartDiv);
  
  // Create SVG element
  const width = chartDiv.clientWidth || 500;
  const height = chartDiv.clientHeight || 300;
  
  const svg = d3.select(chartDiv)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(40, 20)`);
    
  // Get metrics data
  const control = experimentData.results.control || {};
  const treatment = experimentData.results.treatment || {};
  
  // Get metric names
  const metrics = experimentData.metrics || [];
  
  // Create bar chart data
  const barData = metrics.map(metric => ({
    metric,
    control: control[metric] || 0,
    treatment: treatment[metric] || 0,
    difference: ((treatment[metric] || 0) - (control[metric] || 0)),
    percentChange: control[metric] ? (((treatment[metric] || 0) - control[metric]) / control[metric] * 100) : 0
  }));
  
  // Create scales
  const xScale = d3.scaleBand()
    .domain(metrics)
    .range([0, width - 100])
    .padding(0.3);
    
  const maxValue = d3.max(barData, d => Math.max(d.control, d.treatment)) * 1.1;
  
  const yScale = d3.scaleLinear()
    .domain([0, maxValue])
    .range([height - 60, 0]);
    
  // Draw bars for control
  svg.selectAll('.control-bar')
    .data(barData)
    .enter()
    .append('rect')
    .attr('class', 'control-bar')
    .attr('x', d => xScale(d.metric))
    .attr('y', d => yScale(d.control))
    .attr('width', xScale.bandwidth() / 2)
    .attr('height', d => height - 60 - yScale(d.control))
    .attr('fill', chartConfig.colors[0]);
    
  // Draw bars for treatment
  svg.selectAll('.treatment-bar')
    .data(barData)
    .enter()
    .append('rect')
    .attr('class', 'treatment-bar')
    .attr('x', d => xScale(d.metric) + xScale.bandwidth() / 2)
    .attr('y', d => yScale(d.treatment))
    .attr('width', xScale.bandwidth() / 2)
    .attr('height', d => height - 60 - yScale(d.treatment))
    .attr('fill', chartConfig.colors[1]);
    
  // Add axes
  const xAxis = d3.axisBottom(xScale);
  const yAxis = d3.axisLeft(yScale);
  
  svg.append('g')
    .attr('transform', `translate(0, ${height - 60})`)
    .call(xAxis);
    
  svg.append('g')
    .call(yAxis);
    
  // Add legend
  const legend = svg.append('g')
    .attr('transform', `translate(${width - 150}, 10)`);
    
  legend.append('rect')
    .attr('width', 15)
    .attr('height', 15)
    .attr('fill', chartConfig.colors[0]);
    
  legend.append('text')
    .attr('x', 20)
    .attr('y', 12)
    .text('Control')
    .attr('font-family', chartConfig.fontFamily)
    .attr('font-size', '12px');
    
  legend.append('rect')
    .attr('width', 15)
    .attr('height', 15)
    .attr('y', 20)
    .attr('fill', chartConfig.colors[1]);
    
  legend.append('text')
    .attr('x', 20)
    .attr('y', 32)
    .text('Treatment')
    .attr('font-family', chartConfig.fontFamily)
    .attr('font-size', '12px');
    
  // Add title
  svg.append('text')
    .attr('x', (width - 100) / 2)
    .attr('y', -5)
    .attr('text-anchor', 'middle')
    .attr('font-family', chartConfig.fontFamily)
    .attr('font-size', '14px')
    .text('A/B Test Results');
    
  // Add results table
  const tableDiv = document.createElement('div');
  tableDiv.className = 'sophia-results-table';
  container.appendChild(tableDiv);
  
  const table = document.createElement('table');
  table.className = 'table table-striped';
  tableDiv.appendChild(table);
  
  // Create table header
  const thead = document.createElement('thead');
  table.appendChild(thead);
  
  const headerRow = document.createElement('tr');
  thead.appendChild(headerRow);
  
  ['Metric', 'Control', 'Treatment', 'Difference', '% Change', 'Significant'].forEach(heading => {
    const th = document.createElement('th');
    th.textContent = heading;
    headerRow.appendChild(th);
  });
  
  // Create table body
  const tbody = document.createElement('tbody');
  table.appendChild(tbody);
  
  barData.forEach(data => {
    const row = document.createElement('tr');
    tbody.appendChild(row);
    
    // Metric name
    const metricCell = document.createElement('td');
    metricCell.textContent = data.metric;
    row.appendChild(metricCell);
    
    // Control value
    const controlCell = document.createElement('td');
    controlCell.textContent = data.control.toFixed(2);
    row.appendChild(controlCell);
    
    // Treatment value
    const treatmentCell = document.createElement('td');
    treatmentCell.textContent = data.treatment.toFixed(2);
    row.appendChild(treatmentCell);
    
    // Difference
    const diffCell = document.createElement('td');
    diffCell.textContent = data.difference.toFixed(2);
    row.appendChild(diffCell);
    
    // Percent change
    const percentCell = document.createElement('td');
    percentCell.textContent = `${data.percentChange.toFixed(2)}%`;
    // Color based on direction
    if (data.percentChange > 0) {
      percentCell.style.color = 'green';
    } else if (data.percentChange < 0) {
      percentCell.style.color = 'red';
    }
    row.appendChild(percentCell);
    
    // Significance
    const sigCell = document.createElement('td');
    const isSignificant = experimentData.results.significant && 
                          experimentData.results.significant[data.metric];
    sigCell.textContent = isSignificant ? 'Yes' : 'No';
    sigCell.style.fontWeight = isSignificant ? 'bold' : 'normal';
    row.appendChild(sigCell);
  });
}

/**
 * Create a multivariate test visualization
 * @param {Object} experimentData - Experiment data
 * @param {HTMLElement} container - Container element
 */
function createMultivariateVisualization(experimentData, container) {
  // For multivariate tests, create a table of variations and their results
  const tableDiv = document.createElement('div');
  tableDiv.className = 'sophia-results-table';
  container.appendChild(tableDiv);
  
  // Get variations and results
  const variations = experimentData.results.variations || {};
  const metrics = experimentData.metrics || [];
  
  // Create the table
  const table = document.createElement('table');
  table.className = 'table table-striped';
  tableDiv.appendChild(table);
  
  // Create table header
  const thead = document.createElement('thead');
  table.appendChild(thead);
  
  const headerRow = document.createElement('tr');
  thead.appendChild(headerRow);
  
  // Create headers
  const variantHeader = document.createElement('th');
  variantHeader.textContent = 'Variant';
  headerRow.appendChild(variantHeader);
  
  // Add headers for each parameter
  const parameters = experimentData.parameters?.names || [];
  parameters.forEach(param => {
    const th = document.createElement('th');
    th.textContent = param;
    headerRow.appendChild(th);
  });
  
  // Add headers for each metric
  metrics.forEach(metric => {
    const th = document.createElement('th');
    th.textContent = metric;
    headerRow.appendChild(th);
  });
  
  // Create table body
  const tbody = document.createElement('tbody');
  table.appendChild(tbody);
  
  // Add rows for each variation
  Object.keys(variations).forEach(variationId => {
    const variation = variations[variationId];
    const row = document.createElement('tr');
    tbody.appendChild(row);
    
    // Variation ID
    const idCell = document.createElement('td');
    idCell.textContent = variationId;
    row.appendChild(idCell);
    
    // Parameter values
    parameters.forEach(param => {
      const paramCell = document.createElement('td');
      paramCell.textContent = variation.parameters?.[param] || '-';
      row.appendChild(paramCell);
    });
    
    // Metric values
    metrics.forEach(metric => {
      const metricCell = document.createElement('td');
      metricCell.textContent = variation.metrics?.[metric]?.toFixed(2) || '-';
      row.appendChild(metricCell);
    });
  });
  
  // Add best variation highlight
  if (experimentData.results.best_variation) {
    const resultDiv = document.createElement('div');
    resultDiv.className = 'alert alert-success';
    resultDiv.innerHTML = `<strong>Best Variation:</strong> ${experimentData.results.best_variation} (${experimentData.results.confidence_level || 0}% confidence)`;
    container.appendChild(resultDiv);
  }
}

/**
 * Create a before/after test visualization
 * @param {Object} experimentData - Experiment data
 * @param {HTMLElement} container - Container element
 */
function createBeforeAfterVisualization(experimentData, container) {
  // Create comparison chart for before/after test
  const chartDiv = document.createElement('div');
  chartDiv.className = 'sophia-experiment-chart';
  chartDiv.style.height = '300px';
  container.appendChild(chartDiv);
  
  // Create SVG element
  const width = chartDiv.clientWidth || 500;
  const height = chartDiv.clientHeight || 300;
  
  const svg = d3.select(chartDiv)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(40, 20)`);
    
  // Get metrics data
  const before = experimentData.results.before || {};
  const after = experimentData.results.after || {};
  
  // Get metric names
  const metrics = experimentData.metrics || [];
  
  // Create bar chart data
  const barData = metrics.map(metric => ({
    metric,
    before: before[metric] || 0,
    after: after[metric] || 0,
    difference: ((after[metric] || 0) - (before[metric] || 0)),
    percentChange: before[metric] ? (((after[metric] || 0) - before[metric]) / before[metric] * 100) : 0
  }));
  
  // Create scales
  const xScale = d3.scaleBand()
    .domain(metrics)
    .range([0, width - 100])
    .padding(0.3);
    
  const maxValue = d3.max(barData, d => Math.max(d.before, d.after)) * 1.1;
  
  const yScale = d3.scaleLinear()
    .domain([0, maxValue])
    .range([height - 60, 0]);
    
  // Draw bars for before
  svg.selectAll('.before-bar')
    .data(barData)
    .enter()
    .append('rect')
    .attr('class', 'before-bar')
    .attr('x', d => xScale(d.metric))
    .attr('y', d => yScale(d.before))
    .attr('width', xScale.bandwidth() / 2)
    .attr('height', d => height - 60 - yScale(d.before))
    .attr('fill', chartConfig.colors[2]);
    
  // Draw bars for after
  svg.selectAll('.after-bar')
    .data(barData)
    .enter()
    .append('rect')
    .attr('class', 'after-bar')
    .attr('x', d => xScale(d.metric) + xScale.bandwidth() / 2)
    .attr('y', d => yScale(d.after))
    .attr('width', xScale.bandwidth() / 2)
    .attr('height', d => height - 60 - yScale(d.after))
    .attr('fill', chartConfig.colors[3]);
    
  // Add axes
  const xAxis = d3.axisBottom(xScale);
  const yAxis = d3.axisLeft(yScale);
  
  svg.append('g')
    .attr('transform', `translate(0, ${height - 60})`)
    .call(xAxis);
    
  svg.append('g')
    .call(yAxis);
    
  // Add legend
  const legend = svg.append('g')
    .attr('transform', `translate(${width - 150}, 10)`);
    
  legend.append('rect')
    .attr('width', 15)
    .attr('height', 15)
    .attr('fill', chartConfig.colors[2]);
    
  legend.append('text')
    .attr('x', 20)
    .attr('y', 12)
    .text('Before')
    .attr('font-family', chartConfig.fontFamily)
    .attr('font-size', '12px');
    
  legend.append('rect')
    .attr('width', 15)
    .attr('height', 15)
    .attr('y', 20)
    .attr('fill', chartConfig.colors[3]);
    
  legend.append('text')
    .attr('x', 20)
    .attr('y', 32)
    .text('After')
    .attr('font-family', chartConfig.fontFamily)
    .attr('font-size', '12px');
    
  // Add title
  svg.append('text')
    .attr('x', (width - 100) / 2)
    .attr('y', -5)
    .attr('text-anchor', 'middle')
    .attr('font-family', chartConfig.fontFamily)
    .attr('font-size', '14px')
    .text('Before/After Comparison');
    
  // Add results table with percent changes
  const tableDiv = document.createElement('div');
  tableDiv.className = 'sophia-results-table';
  container.appendChild(tableDiv);
  
  const table = document.createElement('table');
  table.className = 'table table-striped';
  tableDiv.appendChild(table);
  
  // Create table header
  const thead = document.createElement('thead');
  table.appendChild(thead);
  
  const headerRow = document.createElement('tr');
  thead.appendChild(headerRow);
  
  ['Metric', 'Before', 'After', 'Difference', '% Change', 'Significant'].forEach(heading => {
    const th = document.createElement('th');
    th.textContent = heading;
    headerRow.appendChild(th);
  });
  
  // Create table body
  const tbody = document.createElement('tbody');
  table.appendChild(tbody);
  
  barData.forEach(data => {
    const row = document.createElement('tr');
    tbody.appendChild(row);
    
    // Metric name
    const metricCell = document.createElement('td');
    metricCell.textContent = data.metric;
    row.appendChild(metricCell);
    
    // Before value
    const beforeCell = document.createElement('td');
    beforeCell.textContent = data.before.toFixed(2);
    row.appendChild(beforeCell);
    
    // After value
    const afterCell = document.createElement('td');
    afterCell.textContent = data.after.toFixed(2);
    row.appendChild(afterCell);
    
    // Difference
    const diffCell = document.createElement('td');
    diffCell.textContent = data.difference.toFixed(2);
    row.appendChild(diffCell);
    
    // Percent change
    const percentCell = document.createElement('td');
    percentCell.textContent = `${data.percentChange.toFixed(2)}%`;
    // Color based on direction (assuming higher is better)
    if (data.percentChange > 0) {
      percentCell.style.color = 'green';
    } else if (data.percentChange < 0) {
      percentCell.style.color = 'red';
    }
    row.appendChild(percentCell);
    
    // Significance
    const sigCell = document.createElement('td');
    const isSignificant = experimentData.results.significant && 
                          experimentData.results.significant[data.metric];
    sigCell.textContent = isSignificant ? 'Yes' : 'No';
    sigCell.style.fontWeight = isSignificant ? 'bold' : 'normal';
    row.appendChild(sigCell);
  });
}

/**
 * Create a generic results table for any experiment type
 * @param {Object} experimentData - Experiment data
 * @param {HTMLElement} container - Container element
 */
function createGenericResultsTable(experimentData, container) {
  const tableDiv = document.createElement('div');
  tableDiv.className = 'sophia-results-table';
  container.appendChild(tableDiv);
  
  // Get metrics and results
  const metrics = experimentData.metrics || [];
  const results = experimentData.results?.metrics || {};
  
  // Create the table
  const table = document.createElement('table');
  table.className = 'table table-striped';
  tableDiv.appendChild(table);
  
  // Create table header
  const thead = document.createElement('thead');
  table.appendChild(thead);
  
  const headerRow = document.createElement('tr');
  thead.appendChild(headerRow);
  
  ['Metric', 'Value', 'Target', 'Status'].forEach(heading => {
    const th = document.createElement('th');
    th.textContent = heading;
    headerRow.appendChild(th);
  });
  
  // Create table body
  const tbody = document.createElement('tbody');
  table.appendChild(tbody);
  
  metrics.forEach(metric => {
    const row = document.createElement('tr');
    tbody.appendChild(row);
    
    // Metric name
    const metricCell = document.createElement('td');
    metricCell.textContent = metric;
    row.appendChild(metricCell);
    
    // Metric value
    const valueCell = document.createElement('td');
    valueCell.textContent = results[metric]?.value?.toFixed(2) || '-';
    row.appendChild(valueCell);
    
    // Target value
    const targetCell = document.createElement('td');
    targetCell.textContent = results[metric]?.target?.toFixed(2) || '-';
    row.appendChild(targetCell);
    
    // Status
    const statusCell = document.createElement('td');
    const metricSuccess = results[metric]?.success || false;
    statusCell.textContent = metricSuccess ? 'Success' : 'Failure';
    statusCell.style.color = metricSuccess ? 'green' : 'red';
    row.appendChild(statusCell);
  });
  
  // Add success summary
  if (experimentData.results.success !== undefined) {
    const resultDiv = document.createElement('div');
    resultDiv.className = experimentData.results.success ? 
                         'alert alert-success' : 
                         'alert alert-danger';
    resultDiv.innerHTML = `<strong>Overall Result:</strong> ${experimentData.results.success ? 'Success' : 'Failure'}`;
    container.appendChild(resultDiv);
  }
}

// Export functions for use in other scripts
window.sophiaCharts = {
  updatePerformanceChart,
  updateResourceChart,
  updateCommunicationChart,
  updateErrorChart,
  updateIntelligenceRadarChart,
  compareIntelligenceProfiles,
  updateExperimentResults
};