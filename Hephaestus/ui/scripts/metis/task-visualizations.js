/**
 * Task Visualizations
 * 
 * Provides various visualization types for tasks:
 * - List view
 * - Board view (Kanban)
 * - Graph view (Dependency graph)
 */

export class TaskVisualizations {
  constructor(container, metisService) {
    this.container = container;
    this.metisService = metisService;
    this.activeView = 'list';
    this.tasks = [];
    this.sortField = 'created_at';
    this.sortDirection = 'desc';
  }

  // List View
  renderListView(tasks = null) {
    if (tasks) {
      this.tasks = tasks;
    }
    
    const viewContainer = document.createElement('div');
    viewContainer.className = 'metis__list-view';
    
    // Create the table
    const table = document.createElement('table');
    table.className = 'metis__task-list';
    
    // Table header
    const thead = document.createElement('thead');
    thead.innerHTML = `
      <tr>
        <th data-sort="id" class="${this.sortField === 'id' ? `sorted-${this.sortDirection}` : ''}">ID</th>
        <th data-sort="title" class="${this.sortField === 'title' ? `sorted-${this.sortDirection}` : ''}">Title</th>
        <th data-sort="status" class="${this.sortField === 'status' ? `sorted-${this.sortDirection}` : ''}">Status</th>
        <th data-sort="priority" class="${this.sortField === 'priority' ? `sorted-${this.sortDirection}` : ''}">Priority</th>
        <th data-sort="due_date" class="${this.sortField === 'due_date' ? `sorted-${this.sortDirection}` : ''}">Due Date</th>
        <th data-sort="complexity" class="${this.sortField === 'complexity' ? `sorted-${this.sortDirection}` : ''}">Complexity</th>
        <th>Actions</th>
      </tr>
    `;
    
    // Add sort event listeners
    Array.from(thead.querySelectorAll('th[data-sort]')).forEach(th => {
      th.addEventListener('click', () => this.handleSort(th.dataset.sort));
    });
    
    // Table body
    const tbody = document.createElement('tbody');
    
    // Sort tasks
    const sortedTasks = [...this.tasks].sort((a, b) => {
      let valA = a[this.sortField];
      let valB = b[this.sortField];
      
      // Handle special cases for certain fields
      if (this.sortField === 'due_date') {
        valA = valA ? new Date(valA) : new Date(0);
        valB = valB ? new Date(valB) : new Date(0);
      } else if (typeof valA === 'string') {
        valA = valA.toLowerCase();
        valB = valB.toLowerCase();
      }
      
      if (valA < valB) return this.sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return this.sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
    
    // Add rows
    sortedTasks.forEach(task => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${task.id}</td>
        <td>${task.title}</td>
        <td>
          <span class="metis__status metis__status--${task.status.toLowerCase()}">${task.status}</span>
        </td>
        <td>
          <span class="metis__priority metis__priority--${task.priority.toLowerCase()}"></span>
          ${task.priority}
        </td>
        <td>${task.due_date ? new Date(task.due_date).toLocaleDateString() : 'N/A'}</td>
        <td>${task.complexity || 'N/A'}</td>
        <td>
          <button class="metis__btn metis__btn--outline btn-edit" data-task-id="${task.id}">Edit</button>
          <button class="metis__btn metis__btn--outline btn-delete" data-task-id="${task.id}">Delete</button>
        </td>
      `;
      
      // Add click event for row selection
      tr.addEventListener('click', (event) => {
        // Ignore if clicking on buttons
        if (event.target.closest('button')) return;
        
        this.handleTaskSelection(task);
      });
      
      // Add button event listeners
      tr.querySelector('.btn-edit').addEventListener('click', () => {
        this.handleTaskEdit(task);
      });
      
      tr.querySelector('.btn-delete').addEventListener('click', () => {
        this.handleTaskDelete(task);
      });
      
      tbody.appendChild(tr);
    });
    
    table.appendChild(thead);
    table.appendChild(tbody);
    viewContainer.appendChild(table);
    
    // Clear and append to container
    const targetContainer = this.container.querySelector('.metis__list-container');
    if (targetContainer) {
      targetContainer.innerHTML = '';
      targetContainer.appendChild(viewContainer);
    }
  }
  
  handleSort(field) {
    // Toggle sort direction if clicking on the same field
    if (this.sortField === field) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortField = field;
      this.sortDirection = 'asc';
    }
    
    // Refresh the list view
    this.renderListView();
  }

  // Board View (Kanban)
  renderBoardView(tasks = null) {
    if (tasks) {
      this.tasks = tasks;
    }
    
    const viewContainer = document.createElement('div');
    viewContainer.className = 'metis__board';
    
    // Define status columns
    const statuses = ['TODO', 'IN_PROGRESS', 'REVIEW', 'BLOCKED', 'COMPLETED'];
    
    // Create columns for each status
    statuses.forEach(status => {
      const column = document.createElement('div');
      column.className = 'metis__column';
      column.setAttribute('data-status', status);
      
      // Column header
      const header = document.createElement('div');
      header.className = 'metis__column-header';
      header.innerHTML = `
        <span>${status.replace('_', ' ')}</span>
        <span class="metis__task-count">${this.tasks.filter(t => t.status === status).length}</span>
      `;
      
      // Column content
      const content = document.createElement('div');
      content.className = 'metis__column-content';
      
      // Add tasks to column
      this.tasks
        .filter(task => task.status === status)
        .sort((a, b) => {
          // Sort by priority first, then by created date
          const priorityOrder = { HIGH: 0, MEDIUM: 1, LOW: 2 };
          const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
          
          if (priorityDiff !== 0) return priorityDiff;
          
          // Sort by created date (newest first) if same priority
          return new Date(b.created_at) - new Date(a.created_at);
        })
        .forEach(task => {
          const taskCard = document.createElement('div');
          taskCard.className = 'metis__task-card';
          taskCard.setAttribute('data-task-id', task.id);
          taskCard.setAttribute('draggable', 'true');
          
          taskCard.innerHTML = `
            <div class="metis__task-card-title">
              <span class="metis__priority metis__priority--${task.priority.toLowerCase()}"></span>
              ${task.title}
            </div>
            <div class="metis__task-card-description">${task.description.substring(0, 100)}${task.description.length > 100 ? '...' : ''}</div>
            <div class="metis__task-card-meta">
              <span>ID: ${task.id}</span>
              <span>${task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}</span>
            </div>
          `;
          
          // Add click event for card selection
          taskCard.addEventListener('click', () => {
            this.handleTaskSelection(task);
          });
          
          // Add drag events
          taskCard.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', task.id);
            e.dataTransfer.effectAllowed = 'move';
            taskCard.classList.add('dragging');
          });
          
          taskCard.addEventListener('dragend', () => {
            taskCard.classList.remove('dragging');
          });
          
          content.appendChild(taskCard);
        });
      
      // Set up drop zone for this column
      content.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
      });
      
      content.addEventListener('drop', async (e) => {
        e.preventDefault();
        const taskId = e.dataTransfer.getData('text/plain');
        const newStatus = status;
        
        // Update task status
        try {
          const task = this.tasks.find(t => t.id === taskId);
          if (task && task.status !== newStatus) {
            await this.metisService.updateTask(taskId, { ...task, status: newStatus });
            // Task update will be handled by the WebSocket event
          }
        } catch (error) {
          console.error('Failed to update task status:', error);
        }
      });
      
      column.appendChild(header);
      column.appendChild(content);
      viewContainer.appendChild(column);
    });
    
    // Clear and append to container
    const targetContainer = this.container.querySelector('.metis__board-container');
    if (targetContainer) {
      targetContainer.innerHTML = '';
      targetContainer.appendChild(viewContainer);
    }
  }

  // Graph View (Dependencies)
  async renderGraphView(tasks = null) {
    if (tasks) {
      this.tasks = tasks;
    }
    
    const viewContainer = document.createElement('div');
    viewContainer.className = 'metis__graph-container';
    
    // Check if D3.js is available - we'll need to load it for the graph view
    if (!window.d3) {
      viewContainer.innerHTML = `
        <div class="metis__placeholder-content">
          <p>Loading dependency graph visualization...</p>
          <div class="metis__spinner"></div>
        </div>
      `;
      
      // Try to load D3.js
      try {
        await this.loadD3();
      } catch (error) {
        viewContainer.innerHTML = `
          <div class="metis__placeholder-content">
            <p>Failed to load graph visualization library. Please try again later.</p>
            <button class="metis__btn metis__btn--primary btn-retry">Retry</button>
          </div>
        `;
        
        viewContainer.querySelector('.btn-retry').addEventListener('click', () => {
          this.renderGraphView();
        });
        
        const targetContainer = this.container.querySelector('.metis__graph-container');
        if (targetContainer) {
          targetContainer.innerHTML = '';
          targetContainer.appendChild(viewContainer);
        }
        return;
      }
    }
    
    // Prepare graph data
    const nodes = this.tasks.map(task => ({
      id: task.id,
      name: task.title,
      status: task.status,
      priority: task.priority,
      complexity: task.complexity || 1
    }));
    
    const links = [];
    
    // Fetch dependencies for each task
    for (const task of this.tasks) {
      try {
        const dependencies = await this.metisService.getTaskDependencies(task.id);
        dependencies.forEach(dep => {
          links.push({
            source: dep.id,
            target: task.id
          });
        });
      } catch (error) {
        console.error(`Failed to fetch dependencies for task ${task.id}:`, error);
      }
    }
    
    // Create SVG element for the graph
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    viewContainer.appendChild(svg);
    
    // Add controls
    const controls = document.createElement('div');
    controls.className = 'metis__graph-controls';
    controls.innerHTML = `
      <button class="metis__btn metis__btn--outline btn-zoom-in">Zoom In</button>
      <button class="metis__btn metis__btn--outline btn-zoom-out">Zoom Out</button>
      <button class="metis__btn metis__btn--outline btn-reset">Reset</button>
    `;
    viewContainer.appendChild(controls);
    
    // Clear and append to container
    const targetContainer = this.container.querySelector('.metis__graph-container');
    if (targetContainer) {
      targetContainer.innerHTML = '';
      targetContainer.appendChild(viewContainer);
      
      // Initialize the graph with D3
      this.initializeGraph(svg, nodes, links);
    }
  }
  
  async loadD3() {
    return new Promise((resolve, reject) => {
      if (window.d3) {
        resolve(window.d3);
        return;
      }
      
      const script = document.createElement('script');
      script.src = 'https://d3js.org/d3.v7.min.js';
      script.onload = () => resolve(window.d3);
      script.onerror = () => reject(new Error('Failed to load D3.js'));
      document.head.appendChild(script);
    });
  }
  
  initializeGraph(svgElement, nodes, links) {
    const d3 = window.d3;
    const width = svgElement.clientWidth;
    const height = svgElement.clientHeight;
    
    // Create a root group for the graph
    const svg = d3.select(svgElement);
    const g = svg.append('g');
    
    // Set up zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });
    
    svg.call(zoom);
    
    // Initialize the simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .on('tick', ticked);
    
    // Create the links
    const link = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2)
      .attr('marker-end', 'url(#arrow)');
    
    // Add arrow marker for links
    svg.append('defs').append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#999');
    
    // Create the nodes
    const node = g.append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(nodes)
      .enter().append('g')
      .attr('class', 'node')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))
      .on('click', (event, d) => {
        const task = this.tasks.find(t => t.id === d.id);
        if (task) {
          this.handleTaskSelection(task);
        }
      });
    
    // Add circles for the nodes
    node.append('circle')
      .attr('r', d => 10 + d.complexity * 2)
      .attr('fill', d => this.getStatusColor(d.status))
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5);
    
    // Add labels
    node.append('text')
      .attr('dx', 15)
      .attr('dy', 4)
      .text(d => d.name)
      .attr('fill', '#fff')
      .attr('stroke', 'none')
      .attr('font-size', 12);
    
    // Tick function to update positions
    function ticked() {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    }
    
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
    
    // Set up control buttons
    const container = svgElement.parentElement;
    container.querySelector('.btn-zoom-in').addEventListener('click', () => {
      svg.transition().duration(300).call(zoom.scaleBy, 1.5);
    });
    
    container.querySelector('.btn-zoom-out').addEventListener('click', () => {
      svg.transition().duration(300).call(zoom.scaleBy, 0.75);
    });
    
    container.querySelector('.btn-reset').addEventListener('click', () => {
      svg.transition().duration(300).call(
        zoom.transform,
        d3.zoomIdentity.translate(width / 2, height / 2).scale(1)
      );
    });
  }
  
  getStatusColor(status) {
    const colors = {
      'TODO': '#5c6bc0',
      'IN_PROGRESS': '#ffa726',
      'COMPLETED': '#66bb6a',
      'BLOCKED': '#ef5350',
      'REVIEW': '#ab47bc'
    };
    
    return colors[status] || '#666';
  }

  // Task event handlers
  handleTaskSelection(task) {
    const event = new CustomEvent('task-selected', { detail: task });
    this.container.dispatchEvent(event);
  }
  
  handleTaskEdit(task) {
    const event = new CustomEvent('task-edit', { detail: task });
    this.container.dispatchEvent(event);
  }
  
  handleTaskDelete(task) {
    const event = new CustomEvent('task-delete', { detail: task });
    this.container.dispatchEvent(event);
  }
  
  // Switch between views
  switchView(viewType) {
    this.activeView = viewType;
    
    // Hide all view containers
    const containers = [
      this.container.querySelector('.metis__list-container'),
      this.container.querySelector('.metis__board-container'),
      this.container.querySelector('.metis__graph-container')
    ];
    
    containers.forEach(container => {
      if (container) {
        container.style.display = 'none';
      }
    });
    
    // Show the active view container
    const activeContainer = this.container.querySelector(`.metis__${viewType}-container`);
    if (activeContainer) {
      activeContainer.style.display = 'block';
    }
    
    // Update active view button
    const viewButtons = this.container.querySelectorAll('.metis__view-button');
    viewButtons.forEach(button => {
      button.classList.toggle('metis__view-button--active', button.dataset.view === viewType);
    });
    
    // Render the active view
    if (viewType === 'list') {
      this.renderListView();
    } else if (viewType === 'board') {
      this.renderBoardView();
    } else if (viewType === 'graph') {
      this.renderGraphView();
    }
  }
}