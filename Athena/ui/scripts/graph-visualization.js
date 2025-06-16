/**
 * Graph Visualization Component
 * 
 * Interactive visualization of the Athena knowledge graph using D3.js.
 * Provides exploration, filtering, and analysis capabilities.
 */

import { AthenaClient } from './athena-service.js';

class GraphVisualization extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.client = new AthenaClient();
    this.graph = { nodes: [], links: [] };
    this.simulation = null;
    this.svg = null;
    this.nodeElements = null;
    this.linkElements = null;
    this.zoom = null;
    this.dragHandler = null;
    this.selectedNode = null;
    this.highlightedNodes = new Set();
    this.highlightedLinks = new Set();
    this.settings = {
      layout: 'force-directed',
      nodeScale: 1.0,
      colorMap: {
        person: '#4285F4',
        organization: '#34A853',
        location: '#FBBC05',
        concept: '#EA4335',
        event: '#9C27B0',
        product: '#00ACC1',
        technology: '#FF9800',
        default: '#999999'
      },
      relationshipColorMap: {
        works_for: '#4285F4',
        located_in: '#34A853',
        knows: '#FBBC05',
        created: '#EA4335',
        part_of: '#9C27B0',
        uses: '#00ACC1',
        default: '#999999'
      }
    };
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
    this.initializeVisualization();
    this.loadGraph();
  }

  disconnectedCallback() {
    // Clean up resources when component is removed
    if (this.simulation) {
      this.simulation.stop();
    }
  }

  setupEventListeners() {
    // Toolbar buttons
    const searchButton = this.shadowRoot.querySelector('.btn-search');
    searchButton.addEventListener('click', () => this.toggleSearchPanel());
    
    const filterButton = this.shadowRoot.querySelector('.btn-filter');
    filterButton.addEventListener('click', () => this.toggleFilterPanel());
    
    const layoutButton = this.shadowRoot.querySelector('.btn-layout');
    layoutButton.addEventListener('click', () => this.cycleLayout());
    
    const exportButton = this.shadowRoot.querySelector('.btn-export');
    exportButton.addEventListener('click', () => this.exportGraph());
    
    // Search form
    const searchForm = this.shadowRoot.querySelector('.search-form');
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      this.performSearch();
    });
    
    // Filter form
    const filterForm = this.shadowRoot.querySelector('.filter-form');
    filterForm.addEventListener('submit', (e) => {
      e.preventDefault();
      this.applyFilters();
    });
  }

  async loadGraph() {
    try {
      this.showLoading();
      const data = await this.client.getVisualizationData();
      this.graph = this.transformGraphData(data);
      this.updateVisualization();
      this.hideLoading();
    } catch (error) {
      console.error('Failed to load graph data:', error);
      this.showError('Failed to load knowledge graph data');
      this.hideLoading();
    }
  }

  transformGraphData(data) {
    // Transform API response to D3 format
    const nodes = data.entities.map(entity => ({
      id: entity.entity_id,
      name: entity.name,
      type: entity.entity_type,
      properties: entity.properties,
      // Add additional properties for visualization
      radius: this.calculateNodeRadius(entity),
      color: this.getColorByType(entity.entity_type)
    }));

    const links = data.relationships.map(rel => ({
      id: rel.relationship_id,
      source: rel.source_id,
      target: rel.target_id,
      type: rel.relationship_type,
      properties: rel.properties,
      // Add additional properties for visualization
      value: rel.weight || 1,
      color: this.getRelationshipColor(rel.relationship_type)
    }));

    return { nodes, links };
  }

  calculateNodeRadius(entity) {
    // Calculate node size based on properties, connections, etc.
    const baseSize = 10;
    const importanceFactor = entity.properties?.importance || 1;
    
    // Apply the global node scale setting
    return baseSize * Math.sqrt(importanceFactor) * this.settings.nodeScale;
  }

  getColorByType(entityType) {
    // Map entity types to colors using settings
    return this.settings.colorMap[entityType] || this.settings.colorMap.default;
  }

  getRelationshipColor(relType) {
    // Map relationship types to colors using settings
    return this.settings.relationshipColorMap[relType] || this.settings.relationshipColorMap.default;
  }

  initializeVisualization() {
    const container = this.shadowRoot.querySelector('.graph-container');
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Create SVG element
    this.svg = d3.select(container)
      .append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet');

    // Add zoom behavior
    this.zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        this.svg.select('.graph-group')
          .attr('transform', event.transform);
      });

    this.svg.call(this.zoom);

    // Create container for graph elements
    const graphGroup = this.svg.append('g')
      .attr('class', 'graph-group');

    // Add arrow markers for directed relationships
    this.svg.append('defs').selectAll('marker')
      .data(['end'])
      .enter().append('marker')
      .attr('id', d => d)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#999');

    // Create containers for links and nodes
    graphGroup.append('g').attr('class', 'links');
    graphGroup.append('g').attr('class', 'nodes');
    graphGroup.append('g').attr('class', 'node-labels');

    // Create force simulation
    this.simulation = d3.forceSimulation()
      .force('link', d3.forceLink().id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => d.radius + 5))
      .on('tick', () => this.ticked());

    // Create drag behavior
    this.dragHandler = d3.drag()
      .on('start', this.dragStarted.bind(this))
      .on('drag', this.dragged.bind(this))
      .on('end', this.dragEnded.bind(this));

    // Handle clicking on the background to deselect
    this.svg.on('click', (event) => {
      if (event.target === this.svg.node() || event.target === graphGroup.node()) {
        this.deselectNode();
      }
    });
  }

  updateVisualization() {
    const graphGroup = this.svg.select('.graph-group');

    // Update links
    this.linkElements = graphGroup.select('.links')
      .selectAll('line')
      .data(this.graph.links, d => d.id);

    this.linkElements.exit().remove();

    const linkEnter = this.linkElements.enter()
      .append('line')
      .attr('stroke-width', d => Math.sqrt(d.value))
      .attr('stroke', d => d.color)
      .attr('marker-end', 'url(#end)')
      .on('mouseover', this.linkMouseOver.bind(this))
      .on('mouseout', this.linkMouseOut.bind(this));

    this.linkElements = linkEnter.merge(this.linkElements);

    // Update nodes
    this.nodeElements = graphGroup.select('.nodes')
      .selectAll('circle')
      .data(this.graph.nodes, d => d.id);

    this.nodeElements.exit().remove();

    const nodeEnter = this.nodeElements.enter()
      .append('circle')
      .attr('r', d => d.radius)
      .attr('fill', d => d.color)
      .call(this.dragHandler)
      .on('click', this.nodeClicked.bind(this))
      .on('mouseover', this.nodeMouseOver.bind(this))
      .on('mouseout', this.nodeMouseOut.bind(this));

    this.nodeElements = nodeEnter.merge(this.nodeElements);

    // Update labels
    this.labelElements = graphGroup.select('.node-labels')
      .selectAll('text')
      .data(this.graph.nodes, d => d.id);

    this.labelElements.exit().remove();

    const labelEnter = this.labelElements.enter()
      .append('text')
      .attr('class', 'node-label')
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .text(d => d.name)
      .style('pointer-events', 'none')
      .style('opacity', 0);

    this.labelElements = labelEnter.merge(this.labelElements);

    // Update simulation
    this.simulation.nodes(this.graph.nodes);
    this.simulation.force('link').links(this.graph.links);
    this.simulation.alpha(1).restart();
  }

  ticked() {
    if (!this.linkElements || !this.nodeElements || !this.labelElements) return;

    this.linkElements
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);

    this.nodeElements
      .attr('cx', d => d.x)
      .attr('cy', d => d.y);

    this.labelElements
      .attr('x', d => d.x)
      .attr('y', d => d.y);
  }

  dragStarted(event, d) {
    if (!event.active) this.simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  dragEnded(event, d) {
    if (!event.active) this.simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }

  nodeClicked(event, d) {
    // Select node and show details
    this.selectedNode = d;
    this.highlightNodeConnections(d);
    this.showNodeDetails(d);

    // Prevent event from propagating
    event.stopPropagation();
  }

  nodeMouseOver(event, d) {
    // Highlight node and its connections
    this.highlightNode(d, true);
    
    // Show node label
    this.labelElements
      .filter(label => label.id === d.id)
      .transition()
      .duration(200)
      .style('opacity', 1);
  }

  nodeMouseOut(event, d) {
    // Remove highlights if not selected
    if (this.selectedNode !== d) {
      this.highlightNode(d, false);
      
      // Hide node label if not selected
      this.labelElements
        .filter(label => label.id === d.id && this.selectedNode?.id !== d.id)
        .transition()
        .duration(200)
        .style('opacity', 0);
    }
  }

  linkMouseOver(event, d) {
    // Highlight the link
    d3.select(event.currentTarget)
      .transition()
      .duration(200)
      .attr('stroke-width', Math.sqrt(d.value) * 2)
      .attr('stroke-opacity', 1);
    
    // Show link tooltip with type
    const tooltip = this.shadowRoot.querySelector('.tooltip');
    tooltip.textContent = d.type;
    tooltip.style.display = 'block';
    tooltip.style.left = `${event.pageX}px`;
    tooltip.style.top = `${event.pageY - 30}px`;
  }

  linkMouseOut(event, d) {
    // Remove highlight
    d3.select(event.currentTarget)
      .transition()
      .duration(200)
      .attr('stroke-width', Math.sqrt(d.value))
      .attr('stroke-opacity', 0.6);
    
    // Hide tooltip
    const tooltip = this.shadowRoot.querySelector('.tooltip');
    tooltip.style.display = 'none';
  }

  highlightNode(node, highlight) {
    // Skip if a node is already selected
    if (this.selectedNode) return;

    // Highlight the node
    this.nodeElements
      .filter(d => d.id === node.id)
      .transition()
      .duration(200)
      .attr('r', highlight ? node.radius * 1.2 : node.radius)
      .attr('stroke', highlight ? '#000' : '#fff')
      .attr('stroke-width', highlight ? 2 : 1.5);
  }

  highlightNodeConnections(node) {
    // Clear any existing highlights
    this.clearHighlights();

    // Add the current node to highlighted set
    this.highlightedNodes.add(node.id);

    // Find all connections and add them to highlighted sets
    this.graph.links.forEach(link => {
      if (link.source.id === node.id || link.target.id === node.id) {
        this.highlightedLinks.add(link.id);

        if (link.source.id === node.id) {
          this.highlightedNodes.add(link.target.id);
        } else {
          this.highlightedNodes.add(link.source.id);
        }
      }
    });

    // Apply visual highlights
    this.applyHighlights();
    
    // Show labels for highlighted nodes
    this.labelElements
      .transition()
      .duration(200)
      .style('opacity', d => this.highlightedNodes.has(d.id) ? 1 : 0);
  }

  clearHighlights() {
    this.highlightedNodes.clear();
    this.highlightedLinks.clear();

    // Reset all nodes and links to normal style
    this.nodeElements
      .transition()
      .duration(200)
      .attr('r', d => d.radius)
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .attr('opacity', 1);

    this.linkElements
      .transition()
      .duration(200)
      .attr('stroke-width', d => Math.sqrt(d.value))
      .attr('stroke-opacity', 0.6);
      
    // Hide all labels
    this.labelElements
      .transition()
      .duration(200)
      .style('opacity', 0);
  }

  applyHighlights() {
    // Apply highlighting to nodes
    this.nodeElements
      .transition()
      .duration(200)
      .attr('opacity', d => this.highlightedNodes.has(d.id) ? 1 : 0.3)
      .attr('stroke', d => this.highlightedNodes.has(d.id) && d.id === this.selectedNode.id ? '#000' : '#fff')
      .attr('stroke-width', d => this.highlightedNodes.has(d.id) && d.id === this.selectedNode.id ? 2 : 1.5);

    // Apply highlighting to links
    this.linkElements
      .transition()
      .duration(200)
      .attr('stroke-opacity', d => this.highlightedLinks.has(d.id) ? 1 : 0.1)
      .attr('stroke-width', d => this.highlightedLinks.has(d.id) ? Math.sqrt(d.value) * 1.5 : Math.sqrt(d.value));
  }

  showNodeDetails(node) {
    const detailsPanel = this.shadowRoot.querySelector('.details-panel');

    // Show the panel
    detailsPanel.classList.add('open');

    // Populate details
    detailsPanel.innerHTML = `
      <div class="details-header">
        <h3>${node.name}</h3>
        <span class="details-type">${node.type}</span>
        <button class="close-button">&times;</button>
      </div>
      <div class="details-content">
        <div class="detail-section">
          <h4>Properties</h4>
          <table class="properties-table">
            ${Object.entries(node.properties || {}).map(([key, value]) => `
              <tr>
                <td>${key}</td>
                <td>${typeof value === 'object' ? JSON.stringify(value) : value}</td>
              </tr>
            `).join('') || '<tr><td colspan="2">No properties available</td></tr>'}
          </table>
        </div>
        <div class="detail-section">
          <h4>Relationships</h4>
          <ul class="relationships-list">
            ${this.getNodeRelationships(node).map(rel => `
              <li>
                <span class="relationship-type">${rel.type}</span>
                <span class="relationship-direction">${rel.direction}</span>
                <a href="#" data-entity-id="${rel.entityId}" class="entity-link">${rel.entityName}</a>
              </li>
            `).join('') || '<li>No relationships found</li>'}
          </ul>
        </div>
        <div class="actions">
          <button class="btn btn-explore" data-entity-id="${node.id}">Explore</button>
          <button class="btn btn-edit" data-entity-id="${node.id}">Edit</button>
          <button class="btn btn-analyze" data-entity-id="${node.id}">Analyze</button>
        </div>
      </div>
    `;

    // Add event listeners
    detailsPanel.querySelector('.close-button').addEventListener('click', () => {
      this.deselectNode();
    });

    detailsPanel.querySelectorAll('.entity-link').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const entityId = e.target.dataset.entityId;
        const entity = this.graph.nodes.find(n => n.id === entityId);
        if (entity) {
          this.selectedNode = entity;
          this.highlightNodeConnections(entity);
          this.showNodeDetails(entity);
        }
      });
    });

    // Action buttons
    detailsPanel.querySelector('.btn-explore').addEventListener('click', () => {
      this.exploreNode(node);
    });

    detailsPanel.querySelector('.btn-edit').addEventListener('click', () => {
      this.editNode(node);
    });

    detailsPanel.querySelector('.btn-analyze').addEventListener('click', () => {
      this.analyzeNode(node);
    });
  }

  deselectNode() {
    this.selectedNode = null;
    this.clearHighlights();
    
    // Hide details panel
    const detailsPanel = this.shadowRoot.querySelector('.details-panel');
    detailsPanel.classList.remove('open');
  }

  getNodeRelationships(node) {
    const relationships = [];

    this.graph.links.forEach(link => {
      if (link.source.id === node.id) {
        relationships.push({
          type: link.type,
          direction: 'outgoing',
          entityId: link.target.id,
          entityName: this.getNodeName(link.target.id)
        });
      } else if (link.target.id === node.id) {
        relationships.push({
          type: link.type,
          direction: 'incoming',
          entityId: link.source.id,
          entityName: this.getNodeName(link.source.id)
        });
      }
    });

    return relationships;
  }

  getNodeName(nodeId) {
    const node = this.graph.nodes.find(n => n.id === nodeId);
    return node ? node.name : 'Unknown';
  }

  exploreNode(node) {
    // Set this node as the center of a focused subgraph
    this.loadNodeSubgraph(node.id);
  }

  async loadNodeSubgraph(nodeId) {
    try {
      this.showLoading();
      
      // Get a subgraph centered on this node
      const data = await this.client.getVisualizationData({ 
        center_node: nodeId,
        depth: 2
      });
      
      this.graph = this.transformGraphData(data);
      this.updateVisualization();
      
      // Center the graph on this node
      const centerNode = this.graph.nodes.find(n => n.id === nodeId);
      if (centerNode) {
        this.centerOnNode(centerNode);
      }
      
      this.hideLoading();
    } catch (error) {
      console.error('Failed to load subgraph:', error);
      this.showError('Failed to load subgraph data');
      this.hideLoading();
    }
  }

  centerOnNode(node) {
    // Center the view on a specific node
    const container = this.shadowRoot.querySelector('.graph-container');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    const zoom = this.zoom;
    const svg = this.svg;
    
    // Wait for simulation to settle
    setTimeout(() => {
      const scale = 1.5;
      const transform = d3.zoomIdentity
        .translate(width/2 - node.x * scale, height/2 - node.y * scale)
        .scale(scale);
      
      svg.transition()
        .duration(750)
        .call(zoom.transform, transform);
    }, 500);
  }

  editNode(node) {
    // Placeholder for editing functionality
    alert(`Edit functionality for node "${node.name}" will be implemented in a future update.`);
  }

  async analyzeNode(node) {
    // Show loading state in details panel
    const detailsPanel = this.shadowRoot.querySelector('.details-panel .details-content');
    const actionsSection = detailsPanel.querySelector('.actions');
    
    const analysisSection = document.createElement('div');
    analysisSection.className = 'detail-section analysis-section';
    analysisSection.innerHTML = `
      <h4>Analysis</h4>
      <div class="analysis-loading">
        <span>Analyzing entity with LLM...</span>
        <div class="spinner"></div>
      </div>
    `;
    
    // Insert before actions
    detailsPanel.insertBefore(analysisSection, actionsSection);
    
    try {
      // Call API to analyze the entity
      const analysis = await this.client.explainEntity(node.id);
      
      // Update the analysis section
      analysisSection.innerHTML = `
        <h4>Analysis</h4>
        <div class="analysis-content">
          ${analysis.explanation || 'No analysis available'}
        </div>
      `;
    } catch (error) {
      console.error('Failed to analyze entity:', error);
      analysisSection.innerHTML = `
        <h4>Analysis</h4>
        <div class="analysis-error">
          Failed to analyze entity. Please try again later.
        </div>
      `;
    }
  }

  toggleSearchPanel() {
    const searchPanel = this.shadowRoot.querySelector('.search-panel');
    searchPanel.classList.toggle('open');
    
    if (searchPanel.classList.contains('open')) {
      this.shadowRoot.querySelector('.search-input').focus();
    }
  }

  toggleFilterPanel() {
    const filterPanel = this.shadowRoot.querySelector('.filter-panel');
    filterPanel.classList.toggle('open');
  }

  cycleLayout() {
    // Cycle through available layouts
    const layouts = ['force-directed', 'circular', 'hierarchical', 'radial'];
    const currentIndex = layouts.indexOf(this.settings.layout);
    const nextIndex = (currentIndex + 1) % layouts.length;
    
    this.settings.layout = layouts[nextIndex];
    this.applyLayout();
    
    // Show current layout name
    const layoutBtn = this.shadowRoot.querySelector('.btn-layout');
    const oldSpan = layoutBtn.querySelector('span');
    if (oldSpan) {
      oldSpan.remove();
    }
    
    const displayName = this.settings.layout
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
      
    const span = document.createElement('span');
    span.textContent = displayName;
    span.style.position = 'absolute';
    span.style.bottom = '-20px';
    span.style.left = '50%';
    span.style.transform = 'translateX(-50%)';
    span.style.fontSize = '12px';
    span.style.whiteSpace = 'nowrap';
    
    layoutBtn.style.position = 'relative';
    layoutBtn.appendChild(span);
    
    setTimeout(() => {
      span.remove();
    }, 2000);
  }

  applyLayout() {
    // Stop current simulation
    this.simulation.stop();
    
    // Get container dimensions
    const container = this.shadowRoot.querySelector('.graph-container');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    switch (this.settings.layout) {
      case 'circular':
        // Apply circular layout
        d3.forceSimulation(this.graph.nodes)
          .force('center', d3.forceCenter(width / 2, height / 2))
          .force('charge', d3.forceManyBody().strength(-50))
          .force('collide', d3.forceCollide().radius(d => d.radius * 2))
          .force('radial', d3.forceRadial(Math.min(width, height) / 3, width / 2, height / 2))
          .on('tick', () => this.ticked())
          .alpha(1)
          .restart();
        break;
        
      case 'hierarchical':
        // Apply hierarchical layout
        const stratify = d3.stratify()
          .id(d => d.id)
          .parentId(d => {
            // Find parent based on incoming "parent" relationships
            const parentLink = this.graph.links.find(link => 
              link.target.id === d.id && 
              (link.type === 'parent_of' || link.type === 'contains' || link.type === 'part_of')
            );
            return parentLink ? parentLink.source.id : null;
          });
          
        try {
          // Create hierarchy - this may fail if there's no clear hierarchy
          const root = stratify(this.graph.nodes);
          
          // Use tree layout
          const treeLayout = d3.tree()
            .size([width - 100, height - 100]);
            
          const rootWithPosition = treeLayout(root);
          
          // Apply positions
          rootWithPosition.each(node => {
            const original = this.graph.nodes.find(n => n.id === node.id);
            if (original) {
              original.x = node.x + 50;
              original.y = node.y + 50;
              original.fx = node.x + 50;
              original.fy = node.y + 50;
            }
          });
          
          // Update visualization with fixed positions
          this.ticked();
          
          // Release fixed positions after a delay
          setTimeout(() => {
            this.graph.nodes.forEach(node => {
              node.fx = null;
              node.fy = null;
            });
            
            // Start force simulation for fine-tuning
            this.simulation.alpha(0.1).restart();
          }, 2000);
        } catch (e) {
          // Fall back to force-directed if hierarchy fails
          console.warn('Failed to create hierarchy, falling back to force-directed layout', e);
          this.settings.layout = 'force-directed';
          this.applyLayout();
        }
        break;
        
      case 'radial':
        // Group nodes by type
        const nodesByType = {};
        this.graph.nodes.forEach(node => {
          if (!nodesByType[node.type]) {
            nodesByType[node.type] = [];
          }
          nodesByType[node.type].push(node);
        });
        
        const types = Object.keys(nodesByType);
        const angleStep = (2 * Math.PI) / types.length;
        
        // Position nodes in clusters by type
        types.forEach((type, i) => {
          const angle = i * angleStep;
          const radius = Math.min(width, height) / 3;
          const clusterX = width/2 + radius * Math.cos(angle);
          const clusterY = height/2 + radius * Math.sin(angle);
          
          nodesByType[type].forEach(node => {
            // Position near cluster center
            node.x = clusterX + (Math.random() - 0.5) * 50;
            node.y = clusterY + (Math.random() - 0.5) * 50;
          });
        });
        
        // Use force simulation for fine-tuning
        this.simulation
          .force('link', d3.forceLink().id(d => d.id).distance(50))
          .force('charge', d3.forceManyBody().strength(-100))
          .force('center', d3.forceCenter(width / 2, height / 2))
          .force('cluster', this.forceCluster(types, nodesByType, angleStep, Math.min(width, height) / 3))
          .on('tick', () => this.ticked())
          .alpha(1)
          .restart();
        break;
        
      case 'force-directed':
      default:
        // Standard force-directed layout
        this.simulation
          .force('link', d3.forceLink().id(d => d.id).distance(100))
          .force('charge', d3.forceManyBody().strength(-400))
          .force('center', d3.forceCenter(width / 2, height / 2))
          .force('collision', d3.forceCollide().radius(d => d.radius + 5))
          .on('tick', () => this.ticked())
          .alpha(1)
          .restart();
        break;
    }
  }
  
  // Custom force for clustering nodes by type in a radial layout
  forceCluster(types, nodesByType, angleStep, radius) {
    const strength = 0.3;
    const centerX = this.shadowRoot.querySelector('.graph-container').clientWidth / 2;
    const centerY = this.shadowRoot.querySelector('.graph-container').clientHeight / 2;
    
    return function(alpha) {
      types.forEach((type, i) => {
        const angle = i * angleStep;
        const clusterX = centerX + radius * Math.cos(angle);
        const clusterY = centerY + radius * Math.sin(angle);
        
        nodesByType[type].forEach(node => {
          node.vx = (node.vx || 0) + (clusterX - node.x) * strength * alpha;
          node.vy = (node.vy || 0) + (clusterY - node.y) * strength * alpha;
        });
      });
    };
  }

  exportGraph() {
    // Create export options menu
    const exportMenu = document.createElement('div');
    exportMenu.className = 'export-menu';
    exportMenu.innerHTML = `
      <button class="btn export-json">Export as JSON</button>
      <button class="btn export-image">Export as Image</button>
      <button class="btn export-svg">Export as SVG</button>
    `;
    
    // Position the menu
    const button = this.shadowRoot.querySelector('.btn-export');
    const rect = button.getBoundingClientRect();
    
    exportMenu.style.position = 'absolute';
    exportMenu.style.top = `${rect.bottom + 5}px`;
    exportMenu.style.right = `${window.innerWidth - rect.right}px`;
    exportMenu.style.backgroundColor = 'var(--background-color)';
    exportMenu.style.border = '1px solid var(--border-color)';
    exportMenu.style.borderRadius = '4px';
    exportMenu.style.padding = '0.5rem';
    exportMenu.style.display = 'flex';
    exportMenu.style.flexDirection = 'column';
    exportMenu.style.gap = '0.5rem';
    exportMenu.style.zIndex = '1000';
    
    this.shadowRoot.appendChild(exportMenu);
    
    // Handle clicks outside the menu
    const handleOutsideClick = (e) => {
      if (!exportMenu.contains(e.target) && e.target !== button) {
        exportMenu.remove();
        document.removeEventListener('click', handleOutsideClick);
      }
    };
    
    document.addEventListener('click', handleOutsideClick);
    
    // Add event listeners for export options
    exportMenu.querySelector('.export-json').addEventListener('click', () => {
      this.exportAsJSON();
      exportMenu.remove();
    });
    
    exportMenu.querySelector('.export-image').addEventListener('click', () => {
      this.exportAsImage();
      exportMenu.remove();
    });
    
    exportMenu.querySelector('.export-svg').addEventListener('click', () => {
      this.exportAsSVG();
      exportMenu.remove();
    });
  }

  exportAsJSON() {
    // Convert graph data to JSON
    const data = {
      nodes: this.graph.nodes.map(node => ({
        id: node.id,
        name: node.name,
        type: node.type,
        properties: node.properties
      })),
      links: this.graph.links.map(link => ({
        id: link.id,
        source: typeof link.source === 'object' ? link.source.id : link.source,
        target: typeof link.target === 'object' ? link.target.id : link.target,
        type: link.type,
        properties: link.properties
      }))
    };
    
    // Create download link
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "knowledge_graph.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  }

  exportAsImage() {
    // Create a canvas element
    const svg = this.svg.node();
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    // Set canvas dimensions
    const svgRect = svg.getBoundingClientRect();
    canvas.width = svgRect.width;
    canvas.height = svgRect.height;
    
    // Fill background
    context.fillStyle = window.getComputedStyle(this.shadowRoot.host).getPropertyValue('--background-color') || '#ffffff';
    context.fillRect(0, 0, canvas.width, canvas.height);
    
    // Convert SVG to data URL
    const svgData = new XMLSerializer().serializeToString(svg);
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);
    
    // Create image from SVG data
    const img = new Image();
    img.onload = () => {
      // Draw image to canvas
      context.drawImage(img, 0, 0);
      
      // Convert canvas to data URL and trigger download
      const imgURL = canvas.toDataURL('image/png');
      const downloadLink = document.createElement('a');
      downloadLink.href = imgURL;
      downloadLink.download = 'knowledge_graph.png';
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      
      // Clean up
      URL.revokeObjectURL(url);
    };
    
    img.src = url;
  }

  exportAsSVG() {
    // Clone the SVG to avoid modifying the original
    const original = this.svg.node();
    const clone = original.cloneNode(true);
    
    // Set white background for export
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('width', '100%');
    rect.setAttribute('height', '100%');
    rect.setAttribute('fill', 'white');
    clone.insertBefore(rect, clone.firstChild);
    
    // Convert to data URL
    const svgData = new XMLSerializer().serializeToString(clone);
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);
    
    // Trigger download
    const downloadLink = document.createElement('a');
    downloadLink.href = url;
    downloadLink.download = 'knowledge_graph.svg';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
    
    // Clean up
    URL.revokeObjectURL(url);
  }

  performSearch() {
    const searchInput = this.shadowRoot.querySelector('.search-input');
    const searchTerm = searchInput.value.trim();
    
    if (!searchTerm) return;
    
    // Perform client-side search first
    const results = this.graph.nodes.filter(node => 
      node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      node.type.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    if (results.length > 0) {
      // Show results panel
      this.showSearchResults(results);
    } else {
      // Call API for more extensive search
      this.searchViaAPI(searchTerm);
    }
  }

  async searchViaAPI(searchTerm) {
    try {
      this.showLoading();
      
      // Call search API
      const results = await this.client.searchEntities(searchTerm);
      
      // Display results
      if (results && results.length > 0) {
        this.showSearchResults(results);
      } else {
        // No results
        this.showSearchResults([]);
      }
      
      this.hideLoading();
    } catch (error) {
      console.error('Search failed:', error);
      this.showError('Search failed. Please try again.');
      this.hideLoading();
    }
  }

  showSearchResults(results) {
    const resultsContainer = this.shadowRoot.querySelector('.search-results');
    resultsContainer.innerHTML = '';
    
    if (results.length === 0) {
      resultsContainer.innerHTML = '<div class="no-results">No results found</div>';
      return;
    }
    
    // Create result list
    const resultsList = document.createElement('ul');
    resultsList.className = 'results-list';
    
    results.forEach(node => {
      const item = document.createElement('li');
      item.className = 'result-item';
      item.innerHTML = `
        <div class="result-name">${node.name}</div>
        <div class="result-type">${node.type}</div>
      `;
      
      // Add click handler
      item.addEventListener('click', () => {
        // Check if node is in current graph
        const existingNode = this.graph.nodes.find(n => n.id === node.id);
        
        if (existingNode) {
          // Node is in current graph, select it
          this.selectedNode = existingNode;
          this.highlightNodeConnections(existingNode);
          this.showNodeDetails(existingNode);
          
          // Center on node
          this.centerOnNode(existingNode);
        } else {
          // Node is not in current graph, load its subgraph
          this.loadNodeSubgraph(node.id);
        }
        
        // Close search panel
        this.shadowRoot.querySelector('.search-panel').classList.remove('open');
      });
      
      resultsList.appendChild(item);
    });
    
    resultsContainer.appendChild(resultsList);
  }

  applyFilters() {
    // Get filter values
    const entityTypeFilter = this.shadowRoot.querySelector('#filter-entity-type').value;
    const relationshipTypeFilter = this.shadowRoot.querySelector('#filter-relationship-type').value;
    const minConfidenceFilter = parseFloat(this.shadowRoot.querySelector('#filter-min-confidence').value);
    
    // Apply filters to visualization
    this.loadFilteredGraph(entityTypeFilter, relationshipTypeFilter, minConfidenceFilter);
  }

  async loadFilteredGraph(entityType, relationshipType, minConfidence) {
    try {
      this.showLoading();
      
      // Call API with filters
      const data = await this.client.getVisualizationData({
        entity_type: entityType || undefined,
        relationship_type: relationshipType || undefined,
        min_confidence: minConfidence || undefined
      });
      
      this.graph = this.transformGraphData(data);
      this.updateVisualization();
      
      this.hideLoading();
      
      // Close filter panel
      this.shadowRoot.querySelector('.filter-panel').classList.remove('open');
    } catch (error) {
      console.error('Failed to load filtered graph:', error);
      this.showError('Failed to apply filters');
      this.hideLoading();
    }
  }

  showLoading() {
    // Show loading overlay
    const loadingOverlay = this.shadowRoot.querySelector('.loading-overlay');
    if (loadingOverlay) {
      loadingOverlay.style.display = 'flex';
    } else {
      // Create loading overlay if it doesn't exist
      const overlay = document.createElement('div');
      overlay.className = 'loading-overlay';
      overlay.innerHTML = `
        <div class="spinner"></div>
        <div class="loading-text">Loading...</div>
      `;
      
      this.shadowRoot.querySelector('.graph-container').appendChild(overlay);
    }
  }

  hideLoading() {
    // Hide loading overlay
    const loadingOverlay = this.shadowRoot.querySelector('.loading-overlay');
    if (loadingOverlay) {
      loadingOverlay.style.display = 'none';
    }
  }

  showError(message) {
    const errorContainer = document.createElement('div');
    errorContainer.className = 'error-message';
    errorContainer.textContent = message;
    
    this.shadowRoot.appendChild(errorContainer);
    
    setTimeout(() => {
      errorContainer.remove();
    }, 5000);
  }
  
  updateSettings(settings) {
    // Update settings from parent component
    if (settings.layout) {
      this.settings.layout = settings.layout;
      this.applyLayout();
    }
    
    if (settings.nodeScale) {
      this.settings.nodeScale = settings.nodeScale;
      
      // Update node sizes
      if (this.nodeElements) {
        this.nodeElements
          .transition()
          .duration(500)
          .attr('r', d => this.calculateNodeRadius(d));
      }
    }
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        /* Graph Visualization CSS */
        :host {
          display: block;
          height: 100%;
          font-family: var(--font-family, sans-serif);
          --primary-color: #4a86e8;
          --secondary-color: #6c757d;
          --border-color: #dee2e6;
          --hover-color: #f8f9fa;
          --selected-color: #e3f2fd;
          --background-color: #ffffff;
          --node-stroke-width: 1.5px;
          --link-stroke-width: 1px;
        }
        
        /* Theme support */
        :host([data-theme="dark"]) {
          --primary-color: #5c9aff;
          --secondary-color: #adb5bd;
          --border-color: #4b5563;
          --hover-color: #374151;
          --selected-color: #1e3a8a;
          --background-color: #111827;
          --node-stroke-width: 1.5px;
          --link-stroke-width: 1px;
          color: #e5e7eb;
        }

        .graph-visualization {
          display: grid;
          grid-template-columns: 1fr 300px;
          grid-template-rows: auto 1fr;
          grid-template-areas: 
            "toolbar toolbar"
            "graph details";
          height: 100%;
          background-color: var(--background-color);
          color: var(--dark-color);
          position: relative;
        }

        .toolbar {
          grid-area: toolbar;
          padding: 0.5rem;
          border-bottom: 1px solid var(--border-color);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .graph-container {
          grid-area: graph;
          height: 100%;
          overflow: hidden;
          position: relative;
        }

        .details-panel {
          grid-area: details;
          border-left: 1px solid var(--border-color);
          background-color: var(--background-color);
          overflow-y: auto;
          transform: translateX(100%);
          transition: transform 0.3s ease;
        }

        .details-panel.open {
          transform: translateX(0);
        }

        .details-header {
          padding: 1rem;
          border-bottom: 1px solid var(--border-color);
          display: flex;
          justify-content: space-between;
          align-items: center;
          position: sticky;
          top: 0;
          background-color: var(--background-color);
          z-index: 1;
        }
        
        .details-header h3 {
          margin: 0;
          font-size: 1.25rem;
          max-width: 70%;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        
        .details-type {
          font-size: 0.875rem;
          padding: 0.25rem 0.5rem;
          background-color: var(--secondary-color);
          color: white;
          border-radius: 4px;
        }

        .details-content {
          padding: 1rem;
        }

        .detail-section {
          margin-bottom: 1.5rem;
        }
        
        .detail-section h4 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          border-bottom: 1px solid var(--border-color);
          padding-bottom: 0.5rem;
        }

        .properties-table {
          width: 100%;
          border-collapse: collapse;
        }

        .properties-table td {
          padding: 0.25rem;
          border-bottom: 1px solid var(--border-color);
          word-break: break-word;
        }

        .properties-table td:first-child {
          font-weight: bold;
          width: 40%;
        }

        .relationships-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .relationships-list li {
          padding: 0.5rem 0;
          border-bottom: 1px solid var(--border-color);
        }

        .relationship-type {
          font-weight: bold;
          margin-right: 0.5rem;
        }

        .relationship-direction {
          color: var(--secondary-color);
          font-size: 0.8rem;
          margin-right: 0.5rem;
          font-style: italic;
        }

        .entity-link {
          color: var(--primary-color);
          text-decoration: none;
        }

        .entity-link:hover {
          text-decoration: underline;
        }

        .btn {
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--border-color);
          border-radius: 4px;
          background-color: var(--background-color);
          cursor: pointer;
          color: var(--dark-color);
        }

        .btn:hover {
          background-color: var(--hover-color);
        }

        .actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 1rem;
        }

        .error-message {
          position: fixed;
          bottom: 1rem;
          left: 50%;
          transform: translateX(-50%);
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          z-index: 100;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .tooltip {
          position: absolute;
          background-color: rgba(0, 0, 0, 0.7);
          color: white;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          pointer-events: none;
          display: none;
          z-index: 100;
        }

        /* D3 Visualization Styles */
        circle {
          stroke: #fff;
          stroke-width: var(--node-stroke-width);
          cursor: pointer;
        }

        circle:hover {
          stroke: #000;
        }

        line {
          stroke-opacity: 0.6;
          stroke-width: var(--link-stroke-width);
        }
        
        .node-label {
          font-size: 10px;
          pointer-events: none;
          fill: var(--dark-color);
        }

        .close-button {
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          padding: 0;
          line-height: 1;
          color: var(--dark-color);
        }
        
        /* Loading overlay */
        .loading-overlay {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background-color: rgba(0, 0, 0, 0.3);
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }
        
        .spinner {
          border: 4px solid rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          border-top: 4px solid var(--primary-color);
          width: 40px;
          height: 40px;
          animation: spin 1s linear infinite;
        }
        
        .loading-text {
          margin-top: 1rem;
          color: white;
          font-weight: bold;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        /* Analysis section */
        .analysis-loading {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .analysis-loading .spinner {
          width: 20px;
          height: 20px;
        }
        
        .analysis-content {
          background-color: var(--hover-color);
          padding: 0.75rem;
          border-radius: 4px;
          white-space: pre-line;
        }
        
        .analysis-error {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
        }
        
        /* Search panel */
        .search-panel {
          position: absolute;
          top: 50px;
          left: 1rem;
          width: 300px;
          background-color: var(--background-color);
          border: 1px solid var(--border-color);
          border-radius: 4px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
          z-index: 100;
          transform: translateY(-150%);
          transition: transform 0.3s ease;
        }
        
        .search-panel.open {
          transform: translateY(0);
        }
        
        .search-form {
          padding: 1rem;
          border-bottom: 1px solid var(--border-color);
        }
        
        .search-input {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid var(--border-color);
          border-radius: 4px;
          background-color: var(--background-color);
          color: var(--dark-color);
        }
        
        .search-results {
          max-height: 300px;
          overflow-y: auto;
        }
        
        .no-results {
          padding: 1rem;
          text-align: center;
          color: var(--secondary-color);
        }
        
        .results-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .result-item {
          padding: 0.75rem 1rem;
          cursor: pointer;
          border-bottom: 1px solid var(--border-color);
        }
        
        .result-item:hover {
          background-color: var(--hover-color);
        }
        
        .result-name {
          font-weight: bold;
        }
        
        .result-type {
          font-size: 0.875rem;
          color: var(--secondary-color);
        }
        
        /* Filter panel */
        .filter-panel {
          position: absolute;
          top: 50px;
          right: 1rem;
          width: 300px;
          background-color: var(--background-color);
          border: 1px solid var(--border-color);
          border-radius: 4px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
          z-index: 100;
          transform: translateY(-150%);
          transition: transform 0.3s ease;
        }
        
        .filter-panel.open {
          transform: translateY(0);
        }
        
        .filter-form {
          padding: 1rem;
        }
        
        .filter-group {
          margin-bottom: 1rem;
        }
        
        .filter-label {
          display: block;
          margin-bottom: 0.25rem;
          font-weight: bold;
        }
        
        .filter-input {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid var(--border-color);
          border-radius: 4px;
          background-color: var(--background-color);
          color: var(--dark-color);
        }
        
        .filter-actions {
          display: flex;
          justify-content: space-between;
        }
      </style>

      <div class="graph-visualization">
        <div class="toolbar">
          <h2>Knowledge Graph</h2>
          <div class="toolbar-controls">
            <button class="btn btn-search">Search</button>
            <button class="btn btn-filter">Filter</button>
            <button class="btn btn-layout">Layout</button>
            <button class="btn btn-export">Export</button>
          </div>
        </div>

        <div class="graph-container">
          <!-- D3 visualization will be inserted here -->
          <div class="tooltip"></div>
        </div>

        <div class="details-panel">
          <!-- Entity details will be shown here -->
        </div>
        
        <!-- Search panel -->
        <div class="search-panel">
          <form class="search-form">
            <input type="text" class="search-input" placeholder="Search entities..." autocomplete="off">
          </form>
          <div class="search-results">
            <!-- Search results will appear here -->
          </div>
        </div>
        
        <!-- Filter panel -->
        <div class="filter-panel">
          <form class="filter-form">
            <div class="filter-group">
              <label class="filter-label" for="filter-entity-type">Entity Type</label>
              <select class="filter-input" id="filter-entity-type">
                <option value="">All Types</option>
                <option value="person">Person</option>
                <option value="organization">Organization</option>
                <option value="location">Location</option>
                <option value="concept">Concept</option>
                <option value="event">Event</option>
                <option value="product">Product</option>
                <option value="technology">Technology</option>
              </select>
            </div>
            
            <div class="filter-group">
              <label class="filter-label" for="filter-relationship-type">Relationship Type</label>
              <select class="filter-input" id="filter-relationship-type">
                <option value="">All Types</option>
                <option value="works_for">Works For</option>
                <option value="knows">Knows</option>
                <option value="located_in">Located In</option>
                <option value="part_of">Part Of</option>
                <option value="created">Created</option>
                <option value="uses">Uses</option>
              </select>
            </div>
            
            <div class="filter-group">
              <label class="filter-label" for="filter-min-confidence">Minimum Confidence</label>
              <input type="range" class="filter-input" id="filter-min-confidence" min="0" max="1" step="0.1" value="0">
              <div style="display: flex; justify-content: space-between; font-size: 0.75rem;">
                <span>0</span>
                <span>0.5</span>
                <span>1.0</span>
              </div>
            </div>
            
            <div class="filter-actions">
              <button type="button" class="btn btn-clear-filters">Clear</button>
              <button type="submit" class="btn btn-apply-filters">Apply Filters</button>
            </div>
          </form>
        </div>
      </div>
    `;
  }
}

customElements.define('graph-visualization', GraphVisualization);

export { GraphVisualization };