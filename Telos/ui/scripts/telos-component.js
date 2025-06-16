/**
 * Telos Requirements Manager Component
 * 
 * This script implements the Shadow DOM component for Telos requirements
 * management, following the established Tekton State Management Pattern.
 */

class TelosComponent extends HTMLElement {
  constructor() {
    super();
    
    // Initialize Shadow DOM
    this.attachShadow({ mode: 'open' });
    
    // Load the template
    const template = document.getElementById('telos-template');
    this.shadowRoot.appendChild(template.content.cloneNode(true));
    
    // State
    this.state = {
      projectsLoaded: false,
      projects: [],
      selectedProject: null,
      selectedRequirement: null,
      requirements: [],
      filteredRequirements: [],
      filters: {
        status: '',
        type: '',
        priority: '',
        search: ''
      },
      view: 'list',
      activeTab: 'requirements', // Added active tab tracking
      traces: [],
      loading: {
        projects: false,
        requirements: false,
        requirement: false,
        traces: false
      },
      error: null,
      dialogs: {
        newProject: false,
        newRequirement: false,
        confirmation: false
      },
      confirmationCallback: null
    };
    
    // Bind methods
    this.initializeComponent = this.initializeComponent.bind(this);
    this.fetchProjects = this.fetchProjects.bind(this);
    this.fetchRequirements = this.fetchRequirements.bind(this);
    this.fetchRequirementDetails = this.fetchRequirementDetails.bind(this);
    this.fetchTraces = this.fetchTraces.bind(this);
    this.createProject = this.createProject.bind(this);
    this.createRequirement = this.createRequirement.bind(this);
    this.updateRequirement = this.updateRequirement.bind(this);
    this.deleteRequirement = this.deleteRequirement.bind(this);
    this.validateRequirement = this.validateRequirement.bind(this);
    this.refineRequirement = this.refineRequirement.bind(this);
    this.createTrace = this.createTrace.bind(this);
    this.renderProjects = this.renderProjects.bind(this);
    this.renderRequirements = this.renderRequirements.bind(this);
    this.renderRequirementDetails = this.renderRequirementDetails.bind(this);
    this.renderTraces = this.renderTraces.bind(this);
    this.handleProjectSelect = this.handleProjectSelect.bind(this);
    this.handleRequirementSelect = this.handleRequirementSelect.bind(this);
    this.handleFilterChange = this.handleFilterChange.bind(this);
    this.handleViewChange = this.handleViewChange.bind(this);
    this.handleTabChange = this.handleTabChange.bind(this);
    this.showDialog = this.showDialog.bind(this);
    this.hideDialog = this.hideDialog.bind(this);
    this.showConfirmation = this.showConfirmation.bind(this);
    
    // Initialize environment
    this.apiBaseUrl = this.getApiUrl();
  }
  
  /**
   * Component lifecycle: connected
   */
  connectedCallback() {
    this.initializeComponent();
  }
  
  /**
   * Component lifecycle: disconnected
   */
  disconnectedCallback() {
    this.removeEventListeners();
  }
  
  /**
   * Initialize the component
   */
  initializeComponent() {
    // Add event listeners
    this.addEventListeners();
    
    // Initial data fetch
    this.fetchProjects();
  }
  
  /**
   * Get API URL from environment variables
   */
  getApiUrl() {
    // Try to get URL from environment
    const telosPort = window.TELOS_PORT || '8008';
    return `http://localhost:${telosPort}/api`;
  }
  
  /**
   * Add event listeners to DOM elements
   */
  addEventListeners() {
    // Main navigation tabs
    const navTabs = this.shadowRoot.querySelectorAll('.telos__nav-tabs .telos__tab');
    if (navTabs) {
      navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
          const tabName = tab.dataset.tab;
          this.handleMainTabChange(tabName);
        });
      });
    }
    
    // Project actions
    const newProjectBtn = this.shadowRoot.getElementById('new-project-btn');
    if (newProjectBtn) {
      newProjectBtn.addEventListener('click', () => this.showDialog('newProject'));
    }
    
    const createProjectBtn = this.shadowRoot.getElementById('create-project');
    if (createProjectBtn) {
      createProjectBtn.addEventListener('click', this.createProject);
    }
    
    const cancelProjectBtn = this.shadowRoot.getElementById('cancel-new-project');
    if (cancelProjectBtn) {
      cancelProjectBtn.addEventListener('click', () => this.hideDialog('newProject'));
    }
    
    const closeProjectDialogBtn = this.shadowRoot.getElementById('close-new-project-dialog');
    if (closeProjectDialogBtn) {
      closeProjectDialogBtn.addEventListener('click', () => this.hideDialog('newProject'));
    }
    
    // Requirement actions
    const addRequirementBtn = this.shadowRoot.getElementById('add-requirement-btn');
    if (addRequirementBtn) {
      addRequirementBtn.addEventListener('click', () => {
        if (this.state.selectedProject) {
          this.showDialog('newRequirement');
          this.populateParentOptions();
        }
      });
    }
    
    const createRequirementBtn = this.shadowRoot.getElementById('create-requirement');
    if (createRequirementBtn) {
      createRequirementBtn.addEventListener('click', this.createRequirement);
    }
    
    const cancelRequirementBtn = this.shadowRoot.getElementById('cancel-new-requirement');
    if (cancelRequirementBtn) {
      cancelRequirementBtn.addEventListener('click', () => this.hideDialog('newRequirement'));
    }
    
    const closeRequirementDialogBtn = this.shadowRoot.getElementById('close-new-requirement-dialog');
    if (closeRequirementDialogBtn) {
      closeRequirementDialogBtn.addEventListener('click', () => this.hideDialog('newRequirement'));
    }
    
    // Filters
    const statusFilter = this.shadowRoot.getElementById('status-filter');
    const typeFilter = this.shadowRoot.getElementById('type-filter');
    const priorityFilter = this.shadowRoot.getElementById('priority-filter');
    const viewMode = this.shadowRoot.getElementById('view-mode');
    
    if (statusFilter) {
      statusFilter.addEventListener('change', () => this.handleFilterChange('status', statusFilter.value));
    }
    
    if (typeFilter) {
      typeFilter.addEventListener('change', () => this.handleFilterChange('type', typeFilter.value));
    }
    
    if (priorityFilter) {
      priorityFilter.addEventListener('change', () => this.handleFilterChange('priority', priorityFilter.value));
    }
    
    if (viewMode) {
      viewMode.addEventListener('change', () => this.handleViewChange(viewMode.value));
    }
    
    // Search
    const searchInput = this.shadowRoot.getElementById('search-input');
    const searchBtn = this.shadowRoot.getElementById('search-btn');
    
    if (searchInput) {
      searchInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
          this.handleFilterChange('search', searchInput.value);
        }
      });
    }
    
    if (searchBtn) {
      searchBtn.addEventListener('click', () => {
        const searchInput = this.shadowRoot.getElementById('search-input');
        this.handleFilterChange('search', searchInput.value);
      });
    }
    
    // Requirement detail view
    const backToProjectBtn = this.shadowRoot.getElementById('back-to-project-btn');
    if (backToProjectBtn) {
      backToProjectBtn.addEventListener('click', () => {
        this.showProjectView();
      });
    }
    
    // Tab switching
    const tabs = this.shadowRoot.querySelectorAll('.telos__tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        this.handleTabChange(tab.dataset.tab);
      });
    });
    
    // Confirmation dialog
    const confirmActionBtn = this.shadowRoot.getElementById('confirm-action');
    const cancelConfirmationBtn = this.shadowRoot.getElementById('cancel-confirmation');
    const closeConfirmationBtn = this.shadowRoot.getElementById('close-confirmation-dialog');
    
    if (confirmActionBtn) {
      confirmActionBtn.addEventListener('click', () => {
        if (this.state.confirmationCallback) {
          this.state.confirmationCallback();
        }
        this.hideDialog('confirmation');
      });
    }
    
    if (cancelConfirmationBtn) {
      cancelConfirmationBtn.addEventListener('click', () => this.hideDialog('confirmation'));
    }
    
    if (closeConfirmationBtn) {
      closeConfirmationBtn.addEventListener('click', () => this.hideDialog('confirmation'));
    }
  }
  
  /**
   * Remove event listeners
   */
  removeEventListeners() {
    // Could implement detailed removal of event listeners if needed
  }
  
  /**
   * Fetch projects from the API
   */
  async fetchProjects() {
    try {
      // Set loading state
      this.state.loading.projects = true;
      this.updateUI();
      
      // Fetch projects
      const response = await fetch(`${this.apiBaseUrl}/projects`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch projects: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update state
      this.state.projects = data.projects || [];
      this.state.projectsLoaded = true;
      this.state.loading.projects = false;
      this.state.error = null;
      
      // Render projects
      this.renderProjects();
    } catch (error) {
      console.error('Error fetching projects:', error);
      
      // Update state
      this.state.loading.projects = false;
      this.state.error = `Failed to load projects: ${error.message}`;
      
      // Show error message
      this.updateUI();
    }
  }
  
  /**
   * Fetch requirements for the selected project
   */
  async fetchRequirements() {
    if (!this.state.selectedProject) {
      return;
    }
    
    try {
      // Set loading state
      this.state.loading.requirements = true;
      this.updateUI();
      
      // Fetch requirements
      const response = await fetch(`${this.apiBaseUrl}/projects/${this.state.selectedProject.project_id}/requirements`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch requirements: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update state
      this.state.requirements = data.requirements || [];
      this.applyFilters(); // This will update filteredRequirements based on current filters
      this.state.loading.requirements = false;
      this.state.error = null;
      
      // Render requirements
      this.renderRequirements();
    } catch (error) {
      console.error('Error fetching requirements:', error);
      
      // Update state
      this.state.loading.requirements = false;
      this.state.error = `Failed to load requirements: ${error.message}`;
      
      // Show error message
      this.updateUI();
    }
  }
  
  /**
   * Fetch details for a specific requirement
   */
  async fetchRequirementDetails(requirementId) {
    if (!this.state.selectedProject || !requirementId) {
      return;
    }
    
    try {
      // Set loading state
      this.state.loading.requirement = true;
      this.updateUI();
      
      // Fetch requirement details
      const response = await fetch(
        `${this.apiBaseUrl}/projects/${this.state.selectedProject.project_id}/requirements/${requirementId}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch requirement: ${response.status}`);
      }
      
      const requirementData = await response.json();
      
      // Update state
      this.state.selectedRequirement = requirementData;
      this.state.loading.requirement = false;
      this.state.error = null;
      
      // Also fetch traces for this requirement
      this.fetchTraces(requirementId);
      
      // Render requirement details
      this.renderRequirementDetails();
    } catch (error) {
      console.error('Error fetching requirement details:', error);
      
      // Update state
      this.state.loading.requirement = false;
      this.state.error = `Failed to load requirement details: ${error.message}`;
      
      // Show error message
      this.updateUI();
    }
  }
  
  /**
   * Fetch traces for a requirement
   */
  async fetchTraces(requirementId) {
    if (!this.state.selectedProject || !requirementId) {
      return;
    }
    
    try {
      // Set loading state
      this.state.loading.traces = true;
      this.updateUI();
      
      // Fetch traces
      const response = await fetch(
        `${this.apiBaseUrl}/projects/${this.state.selectedProject.project_id}/traces?requirement_id=${requirementId}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch traces: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update state
      this.state.traces = data.traces || [];
      this.state.loading.traces = false;
      this.state.error = null;
      
      // Render traces
      this.renderTraces();
    } catch (error) {
      console.error('Error fetching traces:', error);
      
      // Update state
      this.state.loading.traces = false;
      this.state.error = `Failed to load traces: ${error.message}`;
      
      // Show error message
      this.updateUI();
    }
  }
  
  /**
   * Create a new project
   */
  async createProject() {
    // Get form values
    const projectNameInput = this.shadowRoot.getElementById('project-name');
    const projectDescriptionInput = this.shadowRoot.getElementById('project-description');
    
    const projectName = projectNameInput.value.trim();
    const projectDescription = projectDescriptionInput.value.trim();
    
    if (!projectName) {
      alert('Project name is required');
      return;
    }
    
    try {
      // Create project
      const response = await fetch(`${this.apiBaseUrl}/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: projectName,
          description: projectDescription
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create project: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Hide dialog
      this.hideDialog('newProject');
      
      // Clear form
      projectNameInput.value = '';
      projectDescriptionInput.value = '';
      
      // Refresh projects
      this.fetchProjects();
      
      // Select the new project
      this.handleProjectSelect(data.project_id);
    } catch (error) {
      console.error('Error creating project:', error);
      alert(`Failed to create project: ${error.message}`);
    }
  }
  
  /**
   * Create a new requirement
   */
  async createRequirement() {
    if (!this.state.selectedProject) {
      return;
    }
    
    // Get form values
    const titleInput = this.shadowRoot.getElementById('requirement-title');
    const descriptionInput = this.shadowRoot.getElementById('requirement-description');
    const typeSelect = this.shadowRoot.getElementById('requirement-type');
    const prioritySelect = this.shadowRoot.getElementById('requirement-priority');
    const parentSelect = this.shadowRoot.getElementById('requirement-parent');
    const tagsInput = this.shadowRoot.getElementById('requirement-tags');
    
    const title = titleInput.value.trim();
    const description = descriptionInput.value.trim();
    const type = typeSelect.value;
    const priority = prioritySelect.value;
    const parentId = parentSelect.value === '' ? null : parentSelect.value;
    const tags = tagsInput.value.trim() ? tagsInput.value.split(',').map(tag => tag.trim()) : [];
    
    if (!title || !description) {
      alert('Title and description are required');
      return;
    }
    
    try {
      // Create requirement
      const response = await fetch(
        `${this.apiBaseUrl}/projects/${this.state.selectedProject.project_id}/requirements`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            title,
            description,
            requirement_type: type,
            priority,
            parent_id: parentId,
            tags
          })
        }
      );
      
      if (!response.ok) {
        throw new Error(`Failed to create requirement: ${response.status}`);
      }
      
      // Hide dialog
      this.hideDialog('newRequirement');
      
      // Clear form
      titleInput.value = '';
      descriptionInput.value = '';
      typeSelect.value = 'functional';
      prioritySelect.value = 'medium';
      parentSelect.value = '';
      tagsInput.value = '';
      
      // Refresh requirements
      this.fetchRequirements();
    } catch (error) {
      console.error('Error creating requirement:', error);
      alert(`Failed to create requirement: ${error.message}`);
    }
  }
  
  /**
   * Update a requirement
   */
  async updateRequirement(requirementId, updates) {
    if (!this.state.selectedProject || !requirementId) {
      return;
    }
    
    try {
      // Update requirement
      const response = await fetch(
        `${this.apiBaseUrl}/projects/${this.state.selectedProject.project_id}/requirements/${requirementId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(updates)
        }
      );
      
      if (!response.ok) {
        throw new Error(`Failed to update requirement: ${response.status}`);
      }
      
      // Refresh requirements
      this.fetchRequirements();
      
      // If this is the selected requirement, refresh details
      if (this.state.selectedRequirement && this.state.selectedRequirement.requirement_id === requirementId) {
        this.fetchRequirementDetails(requirementId);
      }
      
      return true;
    } catch (error) {
      console.error('Error updating requirement:', error);
      alert(`Failed to update requirement: ${error.message}`);
      return false;
    }
  }
  
  /**
   * Delete a requirement
   */
  async deleteRequirement(requirementId) {
    if (!this.state.selectedProject || !requirementId) {
      return;
    }
    
    try {
      // Delete requirement
      const response = await fetch(
        `${this.apiBaseUrl}/projects/${this.state.selectedProject.project_id}/requirements/${requirementId}`,
        {
          method: 'DELETE'
        }
      );
      
      if (!response.ok) {
        throw new Error(`Failed to delete requirement: ${response.status}`);
      }
      
      // Refresh requirements
      this.fetchRequirements();
      
      // If this was the selected requirement, go back to project view
      if (this.state.selectedRequirement && this.state.selectedRequirement.requirement_id === requirementId) {
        this.showProjectView();
      }
      
      return true;
    } catch (error) {
      console.error('Error deleting requirement:', error);
      alert(`Failed to delete requirement: ${error.message}`);
      return false;
    }
  }
  
  /**
   * Validate a requirement
   */
  async validateRequirement(requirementId) {
    if (!this.state.selectedProject || !requirementId) {
      return;
    }
    
    try {
      // Validate requirement
      const response = await fetch(
        `${this.apiBaseUrl}/projects/${this.state.selectedProject.project_id}/requirements/${requirementId}/validate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            criteria: {
              check_completeness: true,
              check_verifiability: true,
              check_clarity: true
            }
          })
        }
      );
      
      if (!response.ok) {
        throw new Error(`Failed to validate requirement: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Display validation results
      this.renderValidationResults(data);
      
      // Switch to validation tab
      this.handleTabChange('validation');
      
      return data;
    } catch (error) {
      console.error('Error validating requirement:', error);
      alert(`Failed to validate requirement: ${error.message}`);
      return null;
    }
  }
  
  /**
   * Refine a requirement
   */
  async refineRequirement(requirementId, feedback) {
    if (!this.state.selectedProject || !requirementId) {
      return;
    }
    
    try {
      // Refine requirement
      const response = await fetch(
        `${this.apiBaseUrl}/projects/${this.state.selectedProject.project_id}/requirements/${requirementId}/refine`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            feedback,
            auto_update: false
          })
        }
      );
      
      if (!response.ok) {
        throw new Error(`Failed to refine requirement: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Display refinement results
      // Could implement a UI for showing the refinement suggestions
      
      return data;
    } catch (error) {
      console.error('Error refining requirement:', error);
      alert(`Failed to refine requirement: ${error.message}`);
      return null;
    }
  }
  
  /**
   * Create a trace between requirements
   */
  async createTrace(sourceId, targetId, traceType, description) {
    if (!this.state.selectedProject || !sourceId || !targetId) {
      return;
    }
    
    try {
      // Create trace
      const response = await fetch(
        `${this.apiBaseUrl}/projects/${this.state.selectedProject.project_id}/traces`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            source_id: sourceId,
            target_id: targetId,
            trace_type: traceType,
            description
          })
        }
      );
      
      if (!response.ok) {
        throw new Error(`Failed to create trace: ${response.status}`);
      }
      
      // Refresh traces
      if (this.state.selectedRequirement) {
        this.fetchTraces(this.state.selectedRequirement.requirement_id);
      }
      
      return true;
    } catch (error) {
      console.error('Error creating trace:', error);
      alert(`Failed to create trace: ${error.message}`);
      return false;
    }
  }
  
  /**
   * Render projects list
   */
  renderProjects() {
    const projectListEl = this.shadowRoot.getElementById('project-list');
    
    if (!projectListEl) {
      return;
    }
    
    // Clear project list
    projectListEl.innerHTML = '';
    
    // Show loading or error message if needed
    if (this.state.loading.projects) {
      projectListEl.innerHTML = '<div class="telos__loading">Loading projects...</div>';
      return;
    }
    
    if (this.state.error && !this.state.projectsLoaded) {
      projectListEl.innerHTML = `<div class="telos__error">${this.state.error}</div>`;
      return;
    }
    
    // No projects
    if (this.state.projects.length === 0) {
      projectListEl.innerHTML = '<div class="telos__empty">No projects found. Create a new project to get started.</div>';
      return;
    }
    
    // Render projects
    this.state.projects.forEach(project => {
      const projectEl = document.createElement('div');
      projectEl.className = 'telos__project-item';
      
      // Add active class if this is the selected project
      if (this.state.selectedProject && this.state.selectedProject.project_id === project.project_id) {
        projectEl.classList.add('telos__project-item--active');
      }
      
      projectEl.innerHTML = `
        <div class="telos__project-item-name">${project.name}</div>
        <div class="telos__project-item-meta">
          <span>${project.requirement_count} requirements</span>
          <span>${this.formatDate(project.updated_at)}</span>
        </div>
      `;
      
      // Add click handler
      projectEl.addEventListener('click', () => {
        this.handleProjectSelect(project.project_id);
      });
      
      projectListEl.appendChild(projectEl);
    });
  }
  
  /**
   * Render requirements list
   */
  renderRequirements() {
    // Handle different view modes
    switch (this.state.view) {
      case 'list':
        this.renderRequirementsList();
        break;
      case 'board':
        this.renderRequirementsBoard();
        break;
      case 'hierarchy':
        this.renderRequirementsHierarchy();
        break;
      case 'trace':
        this.renderRequirementsTrace();
        break;
    }
  }
  
  /**
   * Render requirements in list view
   */
  renderRequirementsList() {
    const requirementsTableBody = this.shadowRoot.getElementById('requirements-table-body');
    
    if (!requirementsTableBody) {
      return;
    }
    
    // Clear table
    requirementsTableBody.innerHTML = '';
    
    // Show loading or error message if needed
    if (this.state.loading.requirements) {
      requirementsTableBody.innerHTML = `
        <tr>
          <td colspan="6" class="telos__loading">Loading requirements...</td>
        </tr>
      `;
      return;
    }
    
    if (this.state.error && this.state.selectedProject) {
      requirementsTableBody.innerHTML = `
        <tr>
          <td colspan="6" class="telos__error">${this.state.error}</td>
        </tr>
      `;
      return;
    }
    
    // No requirements
    if (this.state.filteredRequirements.length === 0) {
      requirementsTableBody.innerHTML = `
        <tr>
          <td colspan="6" class="telos__empty">No requirements found. Add a new requirement to get started.</td>
        </tr>
      `;
      return;
    }
    
    // Render requirements
    this.state.filteredRequirements.forEach(requirement => {
      const row = document.createElement('tr');
      
      row.innerHTML = `
        <td class="telos__req-id">${requirement.requirement_id}</td>
        <td class="telos__req-title">${requirement.title}</td>
        <td>${requirement.requirement_type}</td>
        <td>
          <div class="telos__priority telos__priority--${requirement.priority}">
            <span class="telos__priority-indicator"></span>
            ${requirement.priority}
          </div>
        </td>
        <td><span class="telos__badge telos__badge--${requirement.status}">${requirement.status}</span></td>
        <td class="telos__req-actions">
          <button class="telos__btn telos__btn--small telos__btn--icon" data-action="edit" title="Edit">
            <span class="icon-edit"></span>
          </button>
          <button class="telos__btn telos__btn--small telos__btn--icon" data-action="view" title="View">
            <span class="icon-view"></span>
          </button>
          <button class="telos__btn telos__btn--small telos__btn--icon telos__btn--danger" data-action="delete" title="Delete">
            <span class="icon-delete"></span>
          </button>
        </td>
      `;
      
      // Add event listeners for actions
      const editBtn = row.querySelector('[data-action="edit"]');
      const viewBtn = row.querySelector('[data-action="view"]');
      const deleteBtn = row.querySelector('[data-action="delete"]');
      
      if (editBtn) {
        editBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          // Could implement edit functionality
          this.handleRequirementSelect(requirement.requirement_id);
        });
      }
      
      if (viewBtn) {
        viewBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.handleRequirementSelect(requirement.requirement_id);
        });
      }
      
      if (deleteBtn) {
        deleteBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.showConfirmation(
            'Delete Requirement',
            `Are you sure you want to delete the requirement "${requirement.title}"?`,
            () => this.deleteRequirement(requirement.requirement_id)
          );
        });
      }
      
      // Add click handler for the row
      row.addEventListener('click', () => {
        this.handleRequirementSelect(requirement.requirement_id);
      });
      
      requirementsTableBody.appendChild(row);
    });
    
    // Show the list view and hide others
    this.shadowRoot.getElementById('requirements-list').classList.remove('hidden');
    this.shadowRoot.getElementById('requirements-board').classList.add('hidden');
    this.shadowRoot.getElementById('requirements-hierarchy').classList.add('hidden');
    this.shadowRoot.getElementById('requirements-trace').classList.add('hidden');
  }
  
  /**
   * Render requirements in board view
   */
  renderRequirementsBoard() {
    // Get board containers
    const boardNew = this.shadowRoot.getElementById('board-new');
    const boardInProgress = this.shadowRoot.getElementById('board-in-progress');
    const boardCompleted = this.shadowRoot.getElementById('board-completed');
    const boardRejected = this.shadowRoot.getElementById('board-rejected');
    
    // Clear boards
    boardNew.innerHTML = '';
    boardInProgress.innerHTML = '';
    boardCompleted.innerHTML = '';
    boardRejected.innerHTML = '';
    
    // Group requirements by status
    const reqByStatus = {
      new: [],
      'in-progress': [],
      completed: [],
      rejected: []
    };
    
    this.state.filteredRequirements.forEach(req => {
      const status = req.status || 'new';
      if (reqByStatus[status]) {
        reqByStatus[status].push(req);
      } else {
        reqByStatus.new.push(req);
      }
    });
    
    // Render each board
    this.renderBoardItems(boardNew, reqByStatus.new);
    this.renderBoardItems(boardInProgress, reqByStatus['in-progress']);
    this.renderBoardItems(boardCompleted, reqByStatus.completed);
    this.renderBoardItems(boardRejected, reqByStatus.rejected);
    
    // Show the board view and hide others
    this.shadowRoot.getElementById('requirements-list').classList.add('hidden');
    this.shadowRoot.getElementById('requirements-board').classList.remove('hidden');
    this.shadowRoot.getElementById('requirements-hierarchy').classList.add('hidden');
    this.shadowRoot.getElementById('requirements-trace').classList.add('hidden');
  }
  
  /**
   * Render items for a specific board column
   */
  renderBoardItems(container, items) {
    if (!container) {
      return;
    }
    
    // No items
    if (items.length === 0) {
      container.innerHTML = '<div class="telos__board-empty">No requirements</div>';
      return;
    }
    
    // Render items
    items.forEach(req => {
      const itemEl = document.createElement('div');
      itemEl.className = 'telos__board-item';
      itemEl.setAttribute('data-id', req.requirement_id);
      
      itemEl.innerHTML = `
        <div class="telos__board-item-title">${req.title}</div>
        <div class="telos__board-item-meta">
          <div class="telos__priority telos__priority--${req.priority}">
            <span class="telos__priority-indicator"></span>
            ${req.priority}
          </div>
          <span>${req.requirement_type}</span>
        </div>
      `;
      
      // Add click handler
      itemEl.addEventListener('click', () => {
        this.handleRequirementSelect(req.requirement_id);
      });
      
      container.appendChild(itemEl);
    });
  }
  
  /**
   * Render requirements in hierarchy view
   */
  renderRequirementsHierarchy() {
    const hierarchyTree = this.shadowRoot.getElementById('requirements-tree');
    
    if (!hierarchyTree) {
      return;
    }
    
    // Clear tree
    hierarchyTree.innerHTML = '';
    
    // Show loading or error message if needed
    if (this.state.loading.requirements) {
      hierarchyTree.innerHTML = '<div class="telos__loading">Loading requirements...</div>';
      return;
    }
    
    if (this.state.error) {
      hierarchyTree.innerHTML = `<div class="telos__error">${this.state.error}</div>`;
      return;
    }
    
    // No requirements
    if (this.state.filteredRequirements.length === 0) {
      hierarchyTree.innerHTML = '<div class="telos__empty">No requirements found. Add a new requirement to get started.</div>';
      return;
    }
    
    // Build hierarchy tree
    this.buildHierarchyTree(hierarchyTree);
    
    // Show the hierarchy view and hide others
    this.shadowRoot.getElementById('requirements-list').classList.add('hidden');
    this.shadowRoot.getElementById('requirements-board').classList.add('hidden');
    this.shadowRoot.getElementById('requirements-hierarchy').classList.remove('hidden');
    this.shadowRoot.getElementById('requirements-trace').classList.add('hidden');
  }
  
  /**
   * Build hierarchy tree visualization
   */
  buildHierarchyTree(container) {
    // Create a map of requirements
    const reqMap = {};
    this.state.filteredRequirements.forEach(req => {
      reqMap[req.requirement_id] = req;
    });
    
    // Create a map of parent-child relationships
    const childrenMap = {};
    this.state.filteredRequirements.forEach(req => {
      if (req.parent_id) {
        if (!childrenMap[req.parent_id]) {
          childrenMap[req.parent_id] = [];
        }
        childrenMap[req.parent_id].push(req.requirement_id);
      }
    });
    
    // Find root nodes
    const rootNodes = this.state.filteredRequirements
      .filter(req => !req.parent_id)
      .map(req => req.requirement_id);
    
    // Render root nodes
    rootNodes.forEach(nodeId => {
      const req = reqMap[nodeId];
      const nodeEl = this.createTreeNode(req, childrenMap, reqMap);
      container.appendChild(nodeEl);
    });
  }
  
  /**
   * Create a tree node for the hierarchy view
   */
  createTreeNode(requirement, childrenMap, reqMap) {
    const nodeEl = document.createElement('div');
    nodeEl.className = 'telos__tree-node';
    nodeEl.setAttribute('data-id', requirement.requirement_id);
    
    // Check if this node has children
    const hasChildren = childrenMap[requirement.requirement_id] && childrenMap[requirement.requirement_id].length > 0;
    
    // Create node header
    const headerEl = document.createElement('div');
    headerEl.className = 'telos__tree-node-header';
    
    headerEl.innerHTML = `
      <div class="telos__tree-toggle">${hasChildren ? '▶' : '　'}</div>
      <div class="telos__tree-label">
        <span class="telos__req-title">${requirement.title}</span>
        <span class="telos__badge telos__badge--${requirement.status}">${requirement.status}</span>
        <span class="telos__priority telos__priority--${requirement.priority}">
          <span class="telos__priority-indicator"></span>
          ${requirement.priority}
        </span>
      </div>
    `;
    
    // Add click handler for the toggle
    if (hasChildren) {
      const toggleEl = headerEl.querySelector('.telos__tree-toggle');
      toggleEl.addEventListener('click', (e) => {
        e.stopPropagation();
        
        // Toggle expanded state
        const isExpanded = toggleEl.textContent === '▼';
        toggleEl.textContent = isExpanded ? '▶' : '▼';
        
        const childrenEl = nodeEl.querySelector('.telos__tree-children');
        if (childrenEl) {
          childrenEl.style.display = isExpanded ? 'none' : 'block';
        }
      });
    }
    
    // Add click handler for the node
    headerEl.addEventListener('click', () => {
      this.handleRequirementSelect(requirement.requirement_id);
    });
    
    nodeEl.appendChild(headerEl);
    
    // Create children container if needed
    if (hasChildren) {
      const childrenEl = document.createElement('div');
      childrenEl.className = 'telos__tree-children';
      childrenEl.style.display = 'none'; // Start collapsed
      
      // Recursively add children
      childrenMap[requirement.requirement_id].forEach(childId => {
        const childReq = reqMap[childId];
        if (childReq) {
          const childNode = this.createTreeNode(childReq, childrenMap, reqMap);
          childrenEl.appendChild(childNode);
        }
      });
      
      nodeEl.appendChild(childrenEl);
    }
    
    return nodeEl;
  }
  
  /**
   * Render requirements in trace view
   */
  renderRequirementsTrace() {
    const traceVisualization = this.shadowRoot.getElementById('trace-visualization');
    
    if (!traceVisualization) {
      return;
    }
    
    // Clear visualization
    traceVisualization.innerHTML = '';
    
    // Show loading or error message if needed
    if (this.state.loading.requirements) {
      traceVisualization.innerHTML = '<div class="telos__loading">Loading requirements...</div>';
      return;
    }
    
    if (this.state.error) {
      traceVisualization.innerHTML = `<div class="telos__error">${this.state.error}</div>`;
      return;
    }
    
    // No requirements
    if (this.state.filteredRequirements.length === 0) {
      traceVisualization.innerHTML = '<div class="telos__empty">No requirements found. Add a new requirement to get started.</div>';
      return;
    }
    
    // TODO: Implement trace visualization
    // This would typically be done with a library like D3.js or a similar visualization library
    traceVisualization.innerHTML = '<div class="telos__info">Trace visualization is not yet implemented.</div>';
    
    // Show the trace view and hide others
    this.shadowRoot.getElementById('requirements-list').classList.add('hidden');
    this.shadowRoot.getElementById('requirements-board').classList.add('hidden');
    this.shadowRoot.getElementById('requirements-hierarchy').classList.add('hidden');
    this.shadowRoot.getElementById('requirements-trace').classList.remove('hidden');
  }
  
  /**
   * Render requirement details
   */
  renderRequirementDetails() {
    if (!this.state.selectedRequirement) {
      return;
    }
    
    const req = this.state.selectedRequirement;
    
    // Update requirement title
    const titleEl = this.shadowRoot.getElementById('requirement-title');
    if (titleEl) {
      titleEl.textContent = req.title;
    }
    
    // Update requirement content
    const contentEl = this.shadowRoot.getElementById('requirement-content');
    if (contentEl) {
      contentEl.innerHTML = `
        <div class="telos__requirement-section">
          <div class="telos__requirement-section-title">Description</div>
          <div class="telos__requirement-description">${req.description}</div>
        </div>
        
        <div class="telos__requirement-properties">
          <div class="telos__requirement-property">
            <div class="telos__requirement-property-label">Type</div>
            <div>${req.requirement_type}</div>
          </div>
          <div class="telos__requirement-property">
            <div class="telos__requirement-property-label">Priority</div>
            <div class="telos__priority telos__priority--${req.priority}">
              <span class="telos__priority-indicator"></span>
              ${req.priority}
            </div>
          </div>
          <div class="telos__requirement-property">
            <div class="telos__requirement-property-label">Status</div>
            <div><span class="telos__badge telos__badge--${req.status}">${req.status}</span></div>
          </div>
          <div class="telos__requirement-property">
            <div class="telos__requirement-property-label">Created</div>
            <div>${this.formatDate(req.created_at)}</div>
          </div>
          <div class="telos__requirement-property">
            <div class="telos__requirement-property-label">Last Updated</div>
            <div>${this.formatDate(req.updated_at)}</div>
          </div>
          <div class="telos__requirement-property">
            <div class="telos__requirement-property-label">ID</div>
            <div class="telos__req-id">${req.requirement_id}</div>
          </div>
        </div>
        
        ${req.tags && req.tags.length > 0 ? `
          <div class="telos__requirement-section">
            <div class="telos__requirement-section-title">Tags</div>
            <div class="telos__requirement-tags">
              ${req.tags.map(tag => `<span class="telos__tag">${tag}</span>`).join('')}
            </div>
          </div>
        ` : ''}
        
        ${req.parent_id ? `
          <div class="telos__requirement-section">
            <div class="telos__requirement-section-title">Parent Requirement</div>
            <div class="telos__requirement-parent">
              <a href="#" data-parent-id="${req.parent_id}">${this.getRequirementTitle(req.parent_id)}</a>
            </div>
          </div>
        ` : ''}
        
        ${req.dependencies && req.dependencies.length > 0 ? `
          <div class="telos__requirement-section">
            <div class="telos__requirement-section-title">Dependencies</div>
            <div class="telos__requirement-dependencies">
              <ul>
                ${req.dependencies.map(depId => `
                  <li><a href="#" data-dependency-id="${depId}">${this.getRequirementTitle(depId)}</a></li>
                `).join('')}
              </ul>
            </div>
          </div>
        ` : ''}
      `;
      
      // Add click handlers for parent/dependency links
      const parentLink = contentEl.querySelector('[data-parent-id]');
      if (parentLink) {
        parentLink.addEventListener('click', (e) => {
          e.preventDefault();
          const parentId = parentLink.getAttribute('data-parent-id');
          this.handleRequirementSelect(parentId);
        });
      }
      
      const dependencyLinks = contentEl.querySelectorAll('[data-dependency-id]');
      dependencyLinks.forEach(link => {
        link.addEventListener('click', (e) => {
          e.preventDefault();
          const depId = link.getAttribute('data-dependency-id');
          this.handleRequirementSelect(depId);
        });
      });
    }
    
    // Update details tab
    const detailsTab = this.shadowRoot.getElementById('details-tab');
    if (detailsTab) {
      // Additional details can be added here
    }
    
    // Update history tab
    const historyTab = this.shadowRoot.getElementById('history-tab');
    if (historyTab) {
      historyTab.innerHTML = `
        <div class="telos__history-timeline">
          ${(req.history || []).map(entry => `
            <div class="telos__history-item">
              <div class="telos__history-meta">
                <span>${entry.action}</span>
                <span>${this.formatDate(entry.timestamp)}</span>
              </div>
              <div class="telos__history-description">${entry.description}</div>
            </div>
          `).join('')}
        </div>
      `;
    }
    
    // Show requirement view and hide project view
    this.shadowRoot.getElementById('project-view').classList.add('hidden');
    this.shadowRoot.getElementById('requirement-view').classList.remove('hidden');
  }
  
  /**
   * Render traces for the selected requirement
   */
  renderTraces() {
    if (!this.state.selectedRequirement) {
      return;
    }
    
    const tracesTab = this.shadowRoot.getElementById('traces-tab');
    if (!tracesTab) {
      return;
    }
    
    // Clear traces tab
    tracesTab.innerHTML = '';
    
    // Show loading or error message if needed
    if (this.state.loading.traces) {
      tracesTab.innerHTML = '<div class="telos__loading">Loading traces...</div>';
      return;
    }
    
    if (this.state.error) {
      tracesTab.innerHTML = `<div class="telos__error">${this.state.error}</div>`;
      return;
    }
    
    // No traces
    if (this.state.traces.length === 0) {
      tracesTab.innerHTML = `
        <div class="telos__empty">
          <p>No traces found for this requirement.</p>
          <button class="telos__btn" id="create-trace-btn-tab">Create Trace</button>
        </div>
      `;
      
      // Add click handler for create trace button
      const createTraceBtn = tracesTab.querySelector('#create-trace-btn-tab');
      if (createTraceBtn) {
        createTraceBtn.addEventListener('click', () => {
          // Could implement a dialog for creating traces
          alert('Create trace functionality is not yet implemented.');
        });
      }
      
      return;
    }
    
    // Render traces
    tracesTab.innerHTML = `
      <div class="telos__traces">
        <div class="telos__trace-actions">
          <button class="telos__btn" id="create-trace-btn-tab">Create Trace</button>
        </div>
        <div class="telos__trace-list">
          <table class="telos__trace-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Source</th>
                <th>Target</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              ${this.state.traces.map(trace => `
                <tr>
                  <td>${trace.trace_type}</td>
                  <td>
                    <a href="#" data-req-id="${trace.source_id}">${this.getRequirementTitle(trace.source_id)}</a>
                  </td>
                  <td>
                    <a href="#" data-req-id="${trace.target_id}">${this.getRequirementTitle(trace.target_id)}</a>
                  </td>
                  <td>${trace.description || ''}</td>
                  <td>
                    <button class="telos__btn telos__btn--small telos__btn--icon" data-action="edit-trace" data-id="${trace.trace_id}">
                      <span class="icon-edit"></span>
                    </button>
                    <button class="telos__btn telos__btn--small telos__btn--icon telos__btn--danger" data-action="delete-trace" data-id="${trace.trace_id}">
                      <span class="icon-delete"></span>
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
    
    // Add click handlers
    const createTraceBtn = tracesTab.querySelector('#create-trace-btn-tab');
    if (createTraceBtn) {
      createTraceBtn.addEventListener('click', () => {
        // Could implement a dialog for creating traces
        alert('Create trace functionality is not yet implemented.');
      });
    }
    
    const reqLinks = tracesTab.querySelectorAll('[data-req-id]');
    reqLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const reqId = link.getAttribute('data-req-id');
        this.handleRequirementSelect(reqId);
      });
    });
  }
  
  /**
   * Render validation results
   */
  renderValidationResults(results) {
    const validationTab = this.shadowRoot.getElementById('validation-tab');
    if (!validationTab) {
      return;
    }
    
    // Format validation results
    validationTab.innerHTML = `
      <div class="telos__validation-results">
        <div class="telos__validation-summary">
          <div class="telos__validation-score">
            ${this.formatScore(results.score)} / 10
          </div>
          <div class="telos__validation-overview">
            <h4>Validation Summary</h4>
            <p>${results.passed ? 'Passed validation' : 'Failed validation'}</p>
          </div>
        </div>
        
        ${results.issues && results.issues.length > 0 ? `
          <div class="telos__validation-issues">
            <h4>Issues Found (${results.issues.length})</h4>
            ${results.issues.map(issue => `
              <div class="telos__validation-issue">
                <div class="telos__validation-issue-title">${issue.type}: ${issue.message}</div>
                ${issue.suggestion ? `<div class="telos__validation-suggestion">${issue.suggestion}</div>` : ''}
              </div>
            `).join('')}
          </div>
        ` : `
          <div class="telos__validation-success">
            <p>No issues found. This requirement meets all validation criteria.</p>
          </div>
        `}
      </div>
    `;
  }
  
  /**
   * Format a date timestamp
   */
  formatDate(timestamp) {
    if (!timestamp) {
      return 'N/A';
    }
    
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  }
  
  /**
   * Format a score as a nice number
   */
  formatScore(score) {
    if (typeof score !== 'number') {
      return 'N/A';
    }
    
    // Scale to 0-10
    const scaled = Math.round(score * 10);
    return scaled;
  }
  
  /**
   * Get a requirement title by ID
   */
  getRequirementTitle(requirementId) {
    const req = this.state.requirements.find(r => r.requirement_id === requirementId);
    return req ? req.title : `Requirement ${requirementId}`;
  }
  
  /**
   * Handle project selection
   */
  handleProjectSelect(projectId) {
    // Find the project
    const project = this.state.projects.find(p => p.project_id === projectId);
    
    if (!project) {
      return;
    }
    
    // Update state
    this.state.selectedProject = project;
    this.state.selectedRequirement = null;
    
    // Update project title
    const projectTitleEl = this.shadowRoot.getElementById('project-title');
    if (projectTitleEl) {
      projectTitleEl.textContent = project.name;
    }
    
    // Update project summary
    this.updateProjectSummary();
    
    // Fetch requirements for this project
    this.fetchRequirements();
    
    // Show project view and hide requirement view
    this.showProjectView();
    
    // Update project list to highlight the selected project
    this.renderProjects();
  }
  
  /**
   * Handle requirement selection
   */
  handleRequirementSelect(requirementId) {
    if (!this.state.selectedProject) {
      return;
    }
    
    // Fetch requirement details
    this.fetchRequirementDetails(requirementId);
  }
  
  /**
   * Update project summary
   */
  updateProjectSummary() {
    if (!this.state.selectedProject) {
      return;
    }
    
    const projectSummaryEl = this.shadowRoot.getElementById('project-summary');
    if (!projectSummaryEl) {
      return;
    }
    
    // For now, just display a loading message or empty state
    if (this.state.loading.requirements) {
      projectSummaryEl.innerHTML = '<div class="telos__loading">Loading project summary...</div>';
      return;
    }
    
    // We'll update this with real metrics when requirements are loaded
    projectSummaryEl.innerHTML = `
      <div class="telos__summary-card">
        <div class="telos__summary-card-title">Total Requirements</div>
        <div class="telos__summary-card-value">${this.state.requirements.length}</div>
      </div>
      <div class="telos__summary-card">
        <div class="telos__summary-card-title">Completed</div>
        <div class="telos__summary-card-value">${this.state.requirements.filter(r => r.status === 'completed').length}</div>
      </div>
      <div class="telos__summary-card">
        <div class="telos__summary-card-title">In Progress</div>
        <div class="telos__summary-card-value">${this.state.requirements.filter(r => r.status === 'in-progress').length}</div>
      </div>
      <div class="telos__summary-card">
        <div class="telos__summary-card-title">Last Updated</div>
        <div class="telos__summary-card-value">${this.formatDate(this.state.selectedProject.updated_at)}</div>
      </div>
    `;
  }
  
  /**
   * Handle filter change
   */
  handleFilterChange(filterType, value) {
    // Update filter state
    this.state.filters[filterType] = value;
    
    // Apply filters and re-render
    this.applyFilters();
    this.renderRequirements();
  }
  
  /**
   * Apply filters to requirements
   */
  applyFilters() {
    // Start with all requirements
    let filteredReqs = [...this.state.requirements];
    
    // Apply status filter
    if (this.state.filters.status) {
      filteredReqs = filteredReqs.filter(req => req.status === this.state.filters.status);
    }
    
    // Apply type filter
    if (this.state.filters.type) {
      filteredReqs = filteredReqs.filter(req => req.requirement_type === this.state.filters.type);
    }
    
    // Apply priority filter
    if (this.state.filters.priority) {
      filteredReqs = filteredReqs.filter(req => req.priority === this.state.filters.priority);
    }
    
    // Apply search filter
    if (this.state.filters.search) {
      const searchTerm = this.state.filters.search.toLowerCase();
      filteredReqs = filteredReqs.filter(req =>
        req.title.toLowerCase().includes(searchTerm) ||
        req.description.toLowerCase().includes(searchTerm)
      );
    }
    
    // Update filtered requirements
    this.state.filteredRequirements = filteredReqs;
  }
  
  /**
   * Handle view change
   */
  handleViewChange(viewMode) {
    // Update state
    this.state.view = viewMode;
    
    // Render requirements in the new view
    this.renderRequirements();
  }
  
  /**
   * Handle tab change
   */
  handleTabChange(tabId) {
    // Update active tab
    const tabs = this.shadowRoot.querySelectorAll('.telos__tab');
    tabs.forEach(tab => {
      if (tab.dataset.tab === tabId) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });
    
    // Update active tab pane
    const tabPanes = this.shadowRoot.querySelectorAll('.telos__tab-pane');
    tabPanes.forEach(pane => {
      if (pane.id === `${tabId}-tab`) {
        pane.classList.add('active');
      } else {
        pane.classList.remove('active');
      }
    });
  }
  
  /**
   * Handle main tab change (between requirements and chat)
   */
  handleMainTabChange(tabName) {
    // Update state
    this.state.activeTab = tabName;
    
    // Update tab buttons
    const tabs = this.shadowRoot.querySelectorAll('.telos__nav-tabs .telos__tab');
    tabs.forEach(tab => {
      if (tab.dataset.tab === tabName) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });
    
    // Show/hide content areas based on the selected tab
    const projectView = this.shadowRoot.getElementById('project-view');
    const requirementView = this.shadowRoot.getElementById('requirement-view');
    const chatView = this.shadowRoot.getElementById('chat-view');
    
    if (tabName === 'chat') {
      // Show chat view, hide requirement views
      if (chatView) chatView.classList.remove('hidden');
      if (projectView) projectView.classList.add('hidden');
      if (requirementView) requirementView.classList.add('hidden');
    } else {
      // Show appropriate requirement view based on state
      if (chatView) chatView.classList.add('hidden');
      
      if (this.state.selectedRequirement) {
        if (projectView) projectView.classList.add('hidden');
        if (requirementView) requirementView.classList.remove('hidden');
      } else {
        if (projectView) projectView.classList.remove('hidden');
        if (requirementView) requirementView.classList.add('hidden');
      }
    }
  }
  
  /**
   * Show project view
   */
  showProjectView() {
    // First ensure we're on the requirements tab
    this.state.activeTab = 'requirements';
    
    // Update tabs
    const tabs = this.shadowRoot.querySelectorAll('.telos__nav-tabs .telos__tab');
    tabs.forEach(tab => {
      if (tab.dataset.tab === 'requirements') {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });
    
    // Show project view and hide requirement view and chat view
    const projectView = this.shadowRoot.getElementById('project-view');
    const requirementView = this.shadowRoot.getElementById('requirement-view');
    const chatView = this.shadowRoot.getElementById('chat-view');
    
    if (projectView) projectView.classList.remove('hidden');
    if (requirementView) requirementView.classList.add('hidden');
    if (chatView) chatView.classList.add('hidden');
  }
  
  /**
   * Show dialog
   */
  showDialog(dialogName) {
    // Update state
    this.state.dialogs[dialogName] = true;
    
    // Show dialog
    const dialog = this.shadowRoot.getElementById(`${dialogName}-dialog`);
    if (dialog) {
      dialog.classList.add('active');
    }
  }
  
  /**
   * Hide dialog
   */
  hideDialog(dialogName) {
    // Update state
    this.state.dialogs[dialogName] = false;
    
    // Hide dialog
    const dialog = this.shadowRoot.getElementById(`${dialogName}-dialog`);
    if (dialog) {
      dialog.classList.remove('active');
    }
  }
  
  /**
   * Show confirmation dialog
   */
  showConfirmation(title, message, callback) {
    // Set confirmation details
    const titleEl = this.shadowRoot.getElementById('confirmation-title');
    const messageEl = this.shadowRoot.getElementById('confirmation-message');
    
    if (titleEl) {
      titleEl.textContent = title;
    }
    
    if (messageEl) {
      messageEl.textContent = message;
    }
    
    // Set callback
    this.state.confirmationCallback = callback;
    
    // Show dialog
    this.showDialog('confirmation');
  }
  
  /**
   * Populate parent options for requirement creation
   */
  populateParentOptions() {
    const parentSelect = this.shadowRoot.getElementById('requirement-parent');
    if (!parentSelect) {
      return;
    }
    
    // Clear options
    parentSelect.innerHTML = '<option value="">None</option>';
    
    // Add options for all requirements
    this.state.requirements.forEach(req => {
      const option = document.createElement('option');
      option.value = req.requirement_id;
      option.textContent = req.title;
      parentSelect.appendChild(option);
    });
  }
  
  /**
   * Update UI based on state
   */
  updateUI() {
    // This method could be expanded to update specific parts of the UI
    // based on state changes
  }
}

// Define the custom element
customElements.define('telos-component', TelosComponent);

// Export the class
export default TelosComponent;