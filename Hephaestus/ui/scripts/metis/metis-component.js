/**
 * Metis Component - Task Management and Visualization
 * Follows Clean Slate UI architecture pattern
 * Connected to Metis Backend API
 */

console.log('[FILE_TRACE] Loading: metis-component.js');

// Define the component namespace
window.metisComponent = window.metisComponent || {};

// Component state
window.metisComponent.state = {
    activeTab: 'tasks',
    activeView: 'list',
    tasks: [],
    dependencies: [],
    complexityData: {},
    ws: null,
    wsConnected: false
};

/**
 * Initialize the component
 */
window.metisComponent.init = async function() {
    console.log('[METIS] Initializing component');
    
    // Setup event listeners for task actions
    window.metisComponent.setupEventListeners();
    
    // Initialize WebSocket connection
    window.metisComponent.initWebSocket();
    
    // Load initial data
    await window.metisComponent.loadInitialData();
    
    // Keep footer visible per Tekton rules
    const chatFooter = document.querySelector('.metis__footer');
    if (chatFooter) {
        chatFooter.style.display = 'block';
    }
    
    console.log('[METIS] Component initialized');
};

/**
 * Initialize WebSocket connection for real-time updates
 */
window.metisComponent.initWebSocket = function() {
    try {
        const wsUrl = metisUrl('/ws').replace(/^http/, 'ws');
        console.log('[METIS] Connecting to WebSocket:', wsUrl);
        
        window.metisComponent.state.ws = new WebSocket(wsUrl);
        
        window.metisComponent.state.ws.onopen = function() {
            console.log('[METIS] WebSocket connected');
            window.metisComponent.state.wsConnected = true;
            
            // Subscribe to updates
            window.metisComponent.state.ws.send(JSON.stringify({
                action: 'subscribe',
                entity_types: ['task', 'dependency']
            }));
        };
        
        window.metisComponent.state.ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('[METIS] WebSocket message:', data);
            
            // Handle different event types
            switch(data.event) {
                case 'task_created':
                case 'task_updated':
                    window.metisComponent.refreshTasks();
                    break;
                case 'dependency_created':
                case 'dependency_updated':
                    window.metisComponent.refreshDependencies();
                    break;
            }
        };
        
        window.metisComponent.state.ws.onclose = function() {
            console.log('[METIS] WebSocket disconnected');
            window.metisComponent.state.wsConnected = false;
            
            // Attempt to reconnect after 5 seconds
            setTimeout(() => {
                window.metisComponent.initWebSocket();
            }, 5000);
        };
        
        window.metisComponent.state.ws.onerror = function(error) {
            console.error('[METIS] WebSocket error:', error);
        };
        
    } catch (error) {
        console.error('[METIS] Failed to initialize WebSocket:', error);
    }
};

/**
 * Load initial data from the API
 */
window.metisComponent.loadInitialData = async function() {
    console.log('[METIS] Loading initial data');
    
    try {
        // Load tasks
        await window.metisComponent.refreshTasks();
        
        // Load dependencies
        await window.metisComponent.refreshDependencies();
        
    } catch (error) {
        console.error('[METIS] Error loading initial data:', error);
    }
};

/**
 * Refresh tasks from the API
 */
window.metisComponent.refreshTasks = async function() {
    try {
        const response = await fetch(metisUrl('/api/v1/tasks'), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        window.metisComponent.state.tasks = data.tasks || [];
        
        console.log('[METIS] Loaded tasks:', window.metisComponent.state.tasks.length);
        
        // Update the UI
        window.metisComponent.renderTasks();
        
    } catch (error) {
        console.error('[METIS] Error loading tasks:', error);
        // Show error in UI
        window.metisComponent.showError('Failed to load tasks. Please check if the backend is running.');
    }
};

/**
 * Render tasks in the current view
 */
window.metisComponent.renderTasks = function() {
    const activeView = window.metisComponent.state.activeView;
    
    switch(activeView) {
        case 'list':
            window.metisComponent.renderTaskList();
            break;
        case 'board':
            window.metisComponent.renderTaskBoard();
            break;
        case 'graph':
            window.metisComponent.renderTaskGraph();
            break;
    }
    
    // Update task count in columns for board view
    window.metisComponent.updateColumnCounts();
};

/**
 * Render task list view
 */
window.metisComponent.renderTaskList = function() {
    const tbody = document.getElementById('task-list-items');
    const loadingIndicator = document.getElementById('task-list-loading');
    const taskTable = document.getElementById('task-table');
    
    if (!tbody) return;
    
    // Hide loading, show table
    if (loadingIndicator) loadingIndicator.style.display = 'none';
    if (taskTable) taskTable.style.display = 'table';
    
    // Clear existing rows
    tbody.innerHTML = '';
    
    // Render each task
    window.metisComponent.state.tasks.forEach(task => {
        const row = document.createElement('tr');
        row.className = 'metis__task-row';
        row.innerHTML = `
            <td class="metis__task-cell">${task.id}</td>
            <td class="metis__task-cell">${task.title || 'Untitled'}</td>
            <td class="metis__task-cell">
                <span class="metis__status metis__status--${task.status}">${task.status}</span>
            </td>
            <td class="metis__task-cell">
                <span class="metis__priority metis__priority--${task.priority}">${task.priority}</span>
            </td>
            <td class="metis__task-cell">${task.complexity_score || '-'}</td>
            <td class="metis__task-cell">${task.due_date || '-'}</td>
            <td class="metis__task-cell metis__task-actions">
                <button class="metis__task-action-btn" onclick="metis_viewTask('${task.id}')" data-tekton-action="view-task">View</button>
                <button class="metis__task-action-btn" onclick="metis_editTask('${task.id}')" data-tekton-action="edit-task">Edit</button>
                <button class="metis__task-action-btn" onclick="metis_deleteTask('${task.id}')" data-tekton-action="delete-task">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    // Show empty state if no tasks
    if (window.metisComponent.state.tasks.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    No tasks found. Click "Add Task" to create your first task.
                </td>
            </tr>
        `;
    }
};

/**
 * Render task board view
 */
window.metisComponent.renderTaskBoard = function() {
    const columns = ['pending', 'in_progress', 'completed', 'blocked'];
    
    columns.forEach(status => {
        const columnContent = document.querySelector(`.metis__column[data-status="${status}"] .metis__column-content`);
        if (!columnContent) return;
        
        // Clear existing cards
        columnContent.innerHTML = '';
        
        // Filter and render tasks for this column
        const columnTasks = window.metisComponent.state.tasks.filter(task => task.status === status);
        
        columnTasks.forEach(task => {
            const card = document.createElement('div');
            card.className = 'metis__task-card';
            card.draggable = true;
            card.setAttribute('data-task-id', task.id);
            card.innerHTML = `
                <div class="metis__card-header">
                    <span class="metis__task-id">${task.id}</span>
                    <span class="metis__priority metis__priority--${task.priority}">${task.priority}</span>
                </div>
                <div class="metis__card-title">${task.title || 'Untitled'}</div>
                <div class="metis__card-footer">
                    <span class="metis__due-date">Due: ${task.due_date || 'Not set'}</span>
                    <span class="metis__complexity">Complexity: ${task.complexity_score || '-'}</span>
                </div>
            `;
            
            // Add drag event listeners
            card.addEventListener('dragstart', window.metisComponent.handleDragStart);
            card.addEventListener('dragend', window.metisComponent.handleDragEnd);
            
            columnContent.appendChild(card);
        });
    });
};

/**
 * Update column counts in board view
 */
window.metisComponent.updateColumnCounts = function() {
    const columns = ['pending', 'in_progress', 'completed', 'blocked'];
    
    columns.forEach(status => {
        const countElement = document.querySelector(`.metis__column[data-status="${status}"] .metis__column-count`);
        if (countElement) {
            const count = window.metisComponent.state.tasks.filter(task => task.status === status).length;
            countElement.textContent = count;
        }
    });
};

/**
 * Refresh dependencies from the API
 */
window.metisComponent.refreshDependencies = async function() {
    try {
        const response = await fetch(metisUrl('/api/v1/dependencies'), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        window.metisComponent.state.dependencies = data.dependencies || [];
        
        console.log('[METIS] Loaded dependencies:', window.metisComponent.state.dependencies.length);
        
        // Update the UI
        window.metisComponent.renderDependencies();
        
    } catch (error) {
        console.error('[METIS] Error loading dependencies:', error);
    }
};

/**
 * Render dependencies
 */
window.metisComponent.renderDependencies = function() {
    const tbody = document.getElementById('dependency-list-items');
    if (!tbody) return;
    
    // Clear existing rows
    tbody.innerHTML = '';
    
    // Render each dependency
    window.metisComponent.state.dependencies.forEach(dep => {
        const row = document.createElement('tr');
        row.className = 'metis__dependency-row';
        row.innerHTML = `
            <td>${dep.from_task_id}: ${window.metisComponent.getTaskTitle(dep.from_task_id)}</td>
            <td>${dep.dependency_type}</td>
            <td>${dep.to_task_id}: ${window.metisComponent.getTaskTitle(dep.to_task_id)}</td>
            <td>
                <button class="metis__dependency-action-btn" onclick="metis_removeDependency('${dep.id}')" data-tekton-action="remove-dependency">Remove</button>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    // Show empty state if no dependencies
    if (window.metisComponent.state.dependencies.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    No dependencies defined yet.
                </td>
            </tr>
        `;
    }
};

/**
 * Get task title by ID
 */
window.metisComponent.getTaskTitle = function(taskId) {
    const task = window.metisComponent.state.tasks.find(t => t.id === taskId);
    return task ? task.title : taskId;
};

/**
 * Add a new task
 */
window.metis_addTask = async function() {
    console.log('[METIS] Add task clicked');
    
    try {
        const modal = document.getElementById('task-detail-modal');
        const modalTitle = document.getElementById('modal-title');
        
        // Clear form fields
        document.getElementById('task-name-input').value = '';
        document.getElementById('task-description-input').value = '';
        document.getElementById('task-status-input').value = 'pending';
        document.getElementById('task-priority-input').value = 'medium';
        document.getElementById('task-due-date-input').value = '';
        document.getElementById('task-assigned-to-input').value = '';
        
        // Update modal title
        modalTitle.textContent = 'Add New Task';
        
        // Show the modal
        modal.style.display = 'flex';
        
        // Setup save button action
        const saveButton = document.getElementById('save-task-btn');
        saveButton.onclick = async function() {
            const taskData = {
                title: document.getElementById('task-name-input').value,
                description: document.getElementById('task-description-input').value,
                status: document.getElementById('task-status-input').value,
                priority: document.getElementById('task-priority-input').value,
                due_date: document.getElementById('task-due-date-input').value || null,
                assigned_to: document.getElementById('task-assigned-to-input').value || null
            };
            
            try {
                const response = await fetch(metisUrl('/api/v1/tasks'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(taskData)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                console.log('[METIS] Task created:', result);
                
                // Refresh tasks
                await window.metisComponent.refreshTasks();
                
                // Close modal
                metis_closeModal();
                
            } catch (error) {
                console.error('[METIS] Error creating task:', error);
                alert('Failed to create task. Please try again.');
            }
        };
    } catch (err) {
        console.error('[METIS] Error in add task:', err);
    }
    
    return false;
};

/**
 * Edit an existing task
 */
window.metis_editTask = async function(taskId) {
    console.log('[METIS] Edit task clicked for:', taskId);
    
    try {
        // Fetch task details
        const response = await fetch(metisUrl(`/api/v1/tasks/${taskId}`), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const task = await response.json();
        
        const modal = document.getElementById('task-detail-modal');
        const modalTitle = document.getElementById('modal-title');
        
        // Populate form fields
        document.getElementById('task-name-input').value = task.title || '';
        document.getElementById('task-description-input').value = task.description || '';
        document.getElementById('task-status-input').value = task.status || 'pending';
        document.getElementById('task-priority-input').value = task.priority || 'medium';
        document.getElementById('task-due-date-input').value = task.due_date || '';
        document.getElementById('task-assigned-to-input').value = task.assigned_to || '';
        
        // Update modal title
        modalTitle.textContent = 'Edit Task: ' + taskId;
        
        // Show the modal
        modal.style.display = 'flex';
        
        // Setup save button action
        const saveButton = document.getElementById('save-task-btn');
        saveButton.onclick = async function() {
            const taskData = {
                title: document.getElementById('task-name-input').value,
                description: document.getElementById('task-description-input').value,
                status: document.getElementById('task-status-input').value,
                priority: document.getElementById('task-priority-input').value,
                due_date: document.getElementById('task-due-date-input').value || null,
                assigned_to: document.getElementById('task-assigned-to-input').value || null
            };
            
            try {
                const updateResponse = await fetch(metisUrl(`/api/v1/tasks/${taskId}`), {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(taskData)
                });
                
                if (!updateResponse.ok) {
                    throw new Error(`HTTP error! status: ${updateResponse.status}`);
                }
                
                const result = await updateResponse.json();
                console.log('[METIS] Task updated:', result);
                
                // Refresh tasks
                await window.metisComponent.refreshTasks();
                
                // Close modal
                metis_closeModal();
                
            } catch (error) {
                console.error('[METIS] Error updating task:', error);
                alert('Failed to update task. Please try again.');
            }
        };
        
    } catch (error) {
        console.error('[METIS] Error fetching task:', error);
        alert('Failed to load task details. Please try again.');
    }
    
    return false;
};

/**
 * Delete a task
 */
window.metis_deleteTask = async function(taskId) {
    console.log('[METIS] Delete task clicked for:', taskId);
    
    if (confirm('Are you sure you want to delete task ' + taskId + '?')) {
        try {
            const response = await fetch(metisUrl(`/api/v1/tasks/${taskId}`), {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            console.log('[METIS] Task deleted:', taskId);
            
            // Refresh tasks
            await window.metisComponent.refreshTasks();
            
        } catch (error) {
            console.error('[METIS] Error deleting task:', error);
            alert('Failed to delete task. Please try again.');
        }
    }
    
    return false;
};

/**
 * View task details (read-only)
 */
window.metis_viewTask = function(taskId) {
    console.log('[METIS] View task clicked for:', taskId);
    
    // For now, reuse edit function in read-only mode
    metis_editTask(taskId);
    
    return false;
};

/**
 * Close modal
 */
window.metis_closeModal = function() {
    console.log('[METIS] Close modal clicked');
    
    try {
        const modal = document.getElementById('task-detail-modal');
        modal.style.display = 'none';
    } catch (err) {
        console.error('[METIS] Error closing modal:', err);
    }
    
    return false;
};

/**
 * Add task dependency
 */
window.metisComponent.addDependency = async function() {
    console.log('[METIS] Adding dependency');
    
    // Get form values
    const taskSelect = document.getElementById('dependency-task-select');
    const dependsOnSelect = document.getElementById('dependency-depends-on-select');
    const typeSelect = document.getElementById('dependency-type-select');
    
    if (taskSelect && dependsOnSelect && typeSelect) {
        const fromTaskId = taskSelect.value;
        const toTaskId = dependsOnSelect.value;
        const dependencyType = typeSelect.value;
        
        if (!fromTaskId || !toTaskId) {
            alert('Please select both tasks');
            return;
        }
        
        if (fromTaskId === toTaskId) {
            alert('A task cannot depend on itself');
            return;
        }
        
        try {
            const response = await fetch(metisUrl('/api/v1/dependencies'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    from_task_id: fromTaskId,
                    to_task_id: toTaskId,
                    dependency_type: dependencyType
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('[METIS] Dependency created:', result);
            
            // Refresh dependencies
            await window.metisComponent.refreshDependencies();
            
            // Reset form
            taskSelect.value = '';
            dependsOnSelect.value = '';
            typeSelect.value = 'blocks';
            
        } catch (error) {
            console.error('[METIS] Error creating dependency:', error);
            alert('Failed to create dependency. Please try again.');
        }
    }
};

/**
 * Remove dependency
 */
window.metis_removeDependency = async function(dependencyId) {
    console.log('[METIS] Removing dependency:', dependencyId);
    
    if (confirm('Are you sure you want to remove this dependency?')) {
        try {
            const response = await fetch(metisUrl(`/api/v1/dependencies/${dependencyId}`), {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            console.log('[METIS] Dependency removed:', dependencyId);
            
            // Refresh dependencies
            await window.metisComponent.refreshDependencies();
            
        } catch (error) {
            console.error('[METIS] Error removing dependency:', error);
            alert('Failed to remove dependency. Please try again.');
        }
    }
    
    return false;
};

/**
 * Analyze task complexity
 */
window.metisComponent.analyzeComplexity = async function() {
    console.log('[METIS] Analyzing complexity');
    
    const taskSelect = document.getElementById('complexity-task-select');
    if (!taskSelect || !taskSelect.value) {
        alert('Please select a task to analyze');
        return;
    }
    
    const taskId = taskSelect.value;
    
    try {
        const response = await fetch(metisUrl(`/api/v1/tasks/${taskId}/analyze-complexity`), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('[METIS] Complexity analysis:', result);
        
        // Update UI with results
        window.metisComponent.displayComplexityAnalysis(result);
        
    } catch (error) {
        console.error('[METIS] Error analyzing complexity:', error);
        alert('Failed to analyze complexity. Please try again.');
    }
};

/**
 * Display complexity analysis results
 */
window.metisComponent.displayComplexityAnalysis = function(analysis) {
    // Update complexity factors display
    const factors = analysis.factors || {};
    const overallScore = analysis.overall_score || 0;
    
    // Update factor bars
    Object.entries(factors).forEach(([factor, value]) => {
        const factorElement = document.querySelector(`[data-factor="${factor}"]`);
        if (factorElement) {
            const bar = factorElement.querySelector('.metis__factor-bar');
            const valueElement = factorElement.querySelector('.metis__factor-value');
            if (bar) bar.style.width = `${value * 10}%`;
            if (valueElement) valueElement.textContent = value.toFixed(1);
        }
    });
    
    // Update overall score
    const scoreElement = document.querySelector('.metis__summary-value');
    if (scoreElement) {
        scoreElement.textContent = overallScore.toFixed(1);
    }
    
    // Update summary text
    const summaryText = document.querySelector('.metis__summary-text');
    if (summaryText && analysis.recommendations) {
        summaryText.textContent = analysis.recommendations.join(' ');
    }
};

/**
 * Setup event listeners
 */
window.metisComponent.setupEventListeners = function() {
    console.log('[METIS] Setting up event listeners');
    
    // Add dependency button
    const addDepButton = document.getElementById('add-dependency-btn');
    if (addDepButton) {
        addDepButton.onclick = function() {
            window.metisComponent.addDependency();
            return false;
        };
    }
    
    // Analyze complexity button
    const analyzeButton = document.getElementById('analyze-complexity-btn');
    if (analyzeButton) {
        analyzeButton.onclick = function() {
            window.metisComponent.analyzeComplexity();
            return false;
        };
    }
    
    // Parse PRD button
    const parseButton = document.getElementById('parse-prd-btn');
    if (parseButton) {
        parseButton.onclick = function() {
            window.metisComponent.parsePRD();
            return false;
        };
    }
    
    // Import tasks button
    const importButton = document.getElementById('import-tasks-btn');
    if (importButton) {
        importButton.onclick = function() {
            window.metisComponent.importParsedTasks();
            return false;
        };
    }
    
    // Reset parser button
    const resetButton = document.getElementById('reset-parser-btn');
    if (resetButton) {
        resetButton.onclick = function() {
            window.metisComponent.resetPRDParser();
            return false;
        };
    }
    
    // File upload handlers
    const fileInput = document.getElementById('prd-file-input');
    const uploadArea = document.getElementById('prd-upload-area');
    
    if (fileInput && uploadArea) {
        fileInput.addEventListener('change', function(event) {
            if (event.target.files.length > 0) {
                const fileName = event.target.files[0].name;
                console.log('[METIS] File selected:', fileName);
                
                uploadArea.innerHTML = `
                    <div class="metis__upload-icon">📄</div>
                    <div class="metis__upload-text">Selected file: <strong>${fileName}</strong></div>
                    <div class="metis__upload-text">Click "Parse Document" to extract tasks</div>
                `;
                
                if (parseButton) {
                    parseButton.disabled = false;
                }
            }
        });
        
        // Drag and drop handlers
        uploadArea.addEventListener('dragover', function(event) {
            event.preventDefault();
            event.stopPropagation();
            uploadArea.style.borderColor = 'var(--color-primary, #7B1FA2)';
        });
        
        uploadArea.addEventListener('dragleave', function(event) {
            event.preventDefault();
            event.stopPropagation();
            uploadArea.style.borderColor = 'var(--border-color, #444444)';
        });
        
        uploadArea.addEventListener('drop', function(event) {
            event.preventDefault();
            event.stopPropagation();
            uploadArea.style.borderColor = 'var(--border-color, #444444)';
            
            const files = event.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                const changeEvent = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(changeEvent);
            }
        });
    }
    
    // Apply filters button
    const applyFilterBtn = document.getElementById('apply-filter-btn');
    if (applyFilterBtn) {
        applyFilterBtn.onclick = function() {
            window.metisComponent.applyFilters();
            return false;
        };
    }
    
    // Search button
    const searchBtn = document.getElementById('task-search-btn');
    if (searchBtn) {
        searchBtn.onclick = function() {
            window.metisComponent.searchTasks();
            return false;
        };
    }
    
    // Task table header sorting
    const taskHeaders = document.querySelectorAll('.metis__task-header[data-sort]');
    taskHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const sortBy = this.getAttribute('data-sort');
            window.metisComponent.sortTasks(sortBy);
        });
    });
    
    // Populate task selects
    window.metisComponent.populateTaskSelects();
};

/**
 * Populate task select dropdowns
 */
window.metisComponent.populateTaskSelects = function() {
    const selects = [
        'dependency-task-select',
        'dependency-depends-on-select',
        'complexity-task-select'
    ];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            // Clear existing options except the first
            while (select.options.length > 1) {
                select.remove(1);
            }
            
            // Add task options
            window.metisComponent.state.tasks.forEach(task => {
                const option = document.createElement('option');
                option.value = task.id;
                option.textContent = `${task.id}: ${task.title || 'Untitled'}`;
                select.appendChild(option);
            });
        }
    });
};

/**
 * Apply filters to task list
 */
window.metisComponent.applyFilters = function() {
    const statusFilter = document.getElementById('task-status-filter').value;
    const priorityFilter = document.getElementById('task-priority-filter').value;
    
    console.log('[METIS] Applying filters:', { status: statusFilter, priority: priorityFilter });
    
    // Filter tasks in memory and re-render
    // This is a simple implementation - could be enhanced
    window.metisComponent.renderTasks();
};

/**
 * Search tasks
 */
window.metisComponent.searchTasks = function() {
    const searchInput = document.getElementById('task-search');
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    
    console.log('[METIS] Searching tasks:', searchTerm);
    
    // Simple search implementation
    if (searchTerm) {
        const filteredTasks = window.metisComponent.state.tasks.filter(task => 
            task.title.toLowerCase().includes(searchTerm) ||
            task.description?.toLowerCase().includes(searchTerm) ||
            task.id.toLowerCase().includes(searchTerm)
        );
        
        // Temporarily store original tasks and show filtered
        window.metisComponent.state.originalTasks = window.metisComponent.state.tasks;
        window.metisComponent.state.tasks = filteredTasks;
        window.metisComponent.renderTasks();
    } else {
        // Restore original tasks
        if (window.metisComponent.state.originalTasks) {
            window.metisComponent.state.tasks = window.metisComponent.state.originalTasks;
            delete window.metisComponent.state.originalTasks;
            window.metisComponent.renderTasks();
        }
    }
};

/**
 * Sort tasks
 */
window.metisComponent.sortTasks = function(sortBy) {
    console.log('[METIS] Sorting tasks by:', sortBy);
    
    const sortFunctions = {
        id: (a, b) => a.id.localeCompare(b.id),
        name: (a, b) => (a.title || '').localeCompare(b.title || ''),
        status: (a, b) => a.status.localeCompare(b.status),
        priority: (a, b) => {
            const priorities = { critical: 0, high: 1, medium: 2, low: 3 };
            return priorities[a.priority] - priorities[b.priority];
        },
        complexity: (a, b) => (b.complexity_score || 0) - (a.complexity_score || 0),
        due_date: (a, b) => (a.due_date || '').localeCompare(b.due_date || '')
    };
    
    if (sortFunctions[sortBy]) {
        window.metisComponent.state.tasks.sort(sortFunctions[sortBy]);
        window.metisComponent.renderTasks();
    }
};

/**
 * Parse PRD document
 */
window.metisComponent.parsePRD = async function() {
    console.log('[METIS] Parsing PRD document');
    
    const fileInput = document.getElementById('prd-file-input');
    if (!fileInput || fileInput.files.length === 0) {
        alert('Please select a file first');
        return;
    }
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Show loading state
        const preview = document.getElementById('prd-preview');
        const prdContent = document.getElementById('prd-content');
        
        if (preview && prdContent) {
            preview.style.display = 'block';
            prdContent.innerHTML = '<div class="metis__loading-text">Parsing document...</div>';
        }
        
        // Note: The PRD parser endpoint would need to be implemented in the backend
        const response = await fetch(metisUrl('/api/v1/prd/parse'), {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('[METIS] PRD parsed:', result);
        
        // Display results
        window.metisComponent.displayParsedTasks(result.tasks || []);
        
    } catch (error) {
        console.error('[METIS] Error parsing PRD:', error);
        alert('Failed to parse document. This feature may not be implemented in the backend yet.');
        
        // Show demo results for now
        window.metisComponent.displayParsedTasks([
            { title: 'Implement User Authentication', priority: 'high', description: 'User login system' },
            { title: 'Create Dashboard UI', priority: 'medium', description: 'Main dashboard' },
            { title: 'Setup Database Schema', priority: 'high', description: 'Database design' }
        ]);
    }
};

/**
 * Display parsed tasks from PRD
 */
window.metisComponent.displayParsedTasks = function(tasks) {
    const parsedTasksContainer = document.getElementById('parsed-tasks-container');
    const parsedTaskList = document.getElementById('parsed-task-list');
    
    if (!parsedTasksContainer || !parsedTaskList) return;
    
    parsedTaskList.innerHTML = tasks.map((task, index) => `
        <div class="metis__parsed-task-item">
            <h4>Task ${index + 1}: ${task.title}</h4>
            <p>Priority: ${task.priority}</p>
            <p>Description: ${task.description}</p>
        </div>
    `).join('');
    
    parsedTasksContainer.style.display = 'block';
    
    // Store parsed tasks for import
    window.metisComponent.state.parsedTasks = tasks;
};

/**
 * Import parsed tasks
 */
window.metisComponent.importParsedTasks = async function() {
    console.log('[METIS] Importing parsed tasks');
    
    if (!window.metisComponent.state.parsedTasks || window.metisComponent.state.parsedTasks.length === 0) {
        alert('No tasks to import');
        return;
    }
    
    try {
        // Create each task
        for (const task of window.metisComponent.state.parsedTasks) {
            await fetch(metisUrl('/api/v1/tasks'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: task.title,
                    description: task.description,
                    priority: task.priority,
                    status: 'pending'
                })
            });
        }
        
        alert('Tasks imported successfully!');
        
        // Switch to tasks tab
        window.metis_switchTab('tasks');
        
        // Refresh tasks
        await window.metisComponent.refreshTasks();
        
        // Reset parser
        window.metisComponent.resetPRDParser();
        
    } catch (error) {
        console.error('[METIS] Error importing tasks:', error);
        alert('Failed to import tasks. Please try again.');
    }
};

/**
 * Reset PRD parser
 */
window.metisComponent.resetPRDParser = function() {
    console.log('[METIS] Resetting PRD parser');
    
    const fileInput = document.getElementById('prd-file-input');
    const uploadArea = document.getElementById('prd-upload-area');
    const preview = document.getElementById('prd-preview');
    const parsedTasksContainer = document.getElementById('parsed-tasks-container');
    const parseButton = document.getElementById('parse-prd-btn');
    
    if (fileInput) fileInput.value = '';
    
    if (uploadArea) {
        uploadArea.innerHTML = `
            <div class="metis__upload-icon">📄</div>
            <div class="metis__upload-text">Drag & drop a PRD document here or</div>
            <label for="prd-file-input" class="metis__upload-button">Browse Files</label>
            <input type="file" id="prd-file-input" class="metis__file-input" accept=".md,.txt,.docx,.pdf">
        `;
    }
    
    if (preview) preview.style.display = 'none';
    if (parsedTasksContainer) parsedTasksContainer.style.display = 'none';
    if (parseButton) parseButton.disabled = true;
    
    // Clear parsed tasks
    delete window.metisComponent.state.parsedTasks;
};

/**
 * Render task graph view
 */
window.metisComponent.renderTaskGraph = function() {
    const graphContainer = document.getElementById('graph-placeholder');
    if (!graphContainer) return;
    
    // This would integrate with a graph library like D3.js or vis.js
    // For now, show a placeholder
    graphContainer.innerHTML = `
        <div class="metis__placeholder-content">
            <h3 class="metis__placeholder-title">Task Dependency Graph</h3>
            <p class="metis__placeholder-text">Graph visualization would show ${window.metisComponent.state.tasks.length} tasks and ${window.metisComponent.state.dependencies.length} dependencies.</p>
        </div>
    `;
};

/**
 * Handle drag start
 */
window.metisComponent.handleDragStart = function(e) {
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.target.innerHTML);
    e.dataTransfer.setData('taskId', e.target.getAttribute('data-task-id'));
    e.target.style.opacity = '0.5';
};

/**
 * Handle drag end
 */
window.metisComponent.handleDragEnd = function(e) {
    e.target.style.opacity = '';
};

/**
 * Show error message
 */
window.metisComponent.showError = function(message) {
    console.error('[METIS]', message);
    
    // Could show a toast notification or update UI
    // For now, check if we're in the tasks view and show message there
    const tbody = document.getElementById('task-list-items');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-error, #ef4444);">
                    ${message}
                </td>
            </tr>
        `;
    }
};

/**
 * Load content for a specific tab
 */
window.metisComponent.loadTabContent = function(tabId) {
    console.log('[METIS] Loading content for tab:', tabId);
    
    // Refresh data based on tab
    switch(tabId) {
        case 'tasks':
            window.metisComponent.refreshTasks();
            break;
        case 'dependency':
            window.metisComponent.refreshDependencies();
            break;
        case 'complexity':
            // Complexity analysis is loaded on demand
            break;
        case 'prd':
            // PRD parser is interactive
            break;
        case 'workflow':
        case 'teamchat':
            // Chat tabs don't need data loading
            break;
    }
};

/**
 * Send chat message
 */
window.metisComponent.sendMessage = function(chatType, message) {
    console.log('[METIS] Sending message:', chatType, message);
    
    // This is handled by the global metis_sendChat function
    // which integrates with window.AIChat
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        window.metisComponent.init();
    });
} else {
    window.metisComponent.init();
}

console.log('[METIS] Component script loaded');