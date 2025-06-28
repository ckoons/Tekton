/**
 * Metis Component - Task Management and Visualization
 * Follows Clean Slate UI architecture pattern
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
    complexityData: {}
};

/**
 * Initialize the component
 */
window.metisComponent.init = function() {
    console.log('[METIS] Initializing component');
    
    // Setup event listeners for task actions
    window.metisComponent.setupEventListeners();
    
    // Load initial data
    window.metisComponent.loadInitialData();
    
    // Hide chat footer by default (only show for chat tabs)
    const chatFooter = document.querySelector('.metis__footer');
    if (chatFooter) {
        chatFooter.style.display = 'none';
    }
    
    console.log('[METIS] Component initialized');
};

/**
 * Setup event listeners for component interactions
 */
window.metisComponent.setupEventListeners = function() {
    console.log('[METIS] Setting up event listeners');
    
    try {
        // Chat input handler
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');
        
        if (chatInput && sendButton) {
            // Enter key in chat input
            chatInput.addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    window.metisComponent.sendChatMessage();
                }
            });
            
            // Send button click
            sendButton.addEventListener('click', function() {
                window.metisComponent.sendChatMessage();
            });
        }
        
        // File upload handler for PRD parser
        const fileInput = document.getElementById('prd-file-input');
        const uploadArea = document.getElementById('prd-upload-area');
        const parseButton = document.getElementById('parse-prd-btn');
        
        if (fileInput && uploadArea) {
            // File input change handler
            fileInput.addEventListener('change', function(event) {
                if (event.target.files.length > 0) {
                    const fileName = event.target.files[0].name;
                    console.log('[METIS] File selected:', fileName);
                    
                    // Update UI to show selected file
                    uploadArea.innerHTML = `
                        <div class="metis__upload-icon">📄</div>
                        <div class="metis__upload-text">Selected file: <strong>${fileName}</strong></div>
                        <div class="metis__upload-text">Click "Parse Document" to extract tasks</div>
                    `;
                    
                    // Enable parse button
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
                
                if (event.dataTransfer.files.length > 0) {
                    fileInput.files = event.dataTransfer.files;
                    const fileName = event.dataTransfer.files[0].name;
                    console.log('[METIS] File dropped:', fileName);
                    
                    // Update UI to show selected file
                    uploadArea.innerHTML = `
                        <div class="metis__upload-icon">📄</div>
                        <div class="metis__upload-text">Selected file: <strong>${fileName}</strong></div>
                        <div class="metis__upload-text">Click "Parse Document" to extract tasks</div>
                    `;
                    
                    // Enable parse button
                    if (parseButton) {
                        parseButton.disabled = false;
                    }
                }
            });
        }
        
        // Parse button handler
        if (parseButton) {
            parseButton.addEventListener('click', function() {
                console.log('[METIS] Parse document clicked');
                window.metisComponent.parsePRD();
            });
        }
        
        // Setup handlers for task table headers (sorting)
        const taskHeaders = document.querySelectorAll('.metis__task-header');
        taskHeaders.forEach(header => {
            if (header.getAttribute('data-sort')) {
                header.addEventListener('click', function() {
                    const sortBy = this.getAttribute('data-sort');
                    console.log('[METIS] Sort by:', sortBy);
                    window.metisComponent.sortTasks(sortBy);
                });
            }
        });
        
        // Setup analysis button handler
        const analyzeBtn = document.getElementById('analyze-complexity-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', function() {
                const taskSelect = document.getElementById('complexity-task-select');
                if (taskSelect && taskSelect.value) {
                    console.log('[METIS] Analyze complexity for:', taskSelect.value);
                    window.metisComponent.analyzeComplexity(taskSelect.value);
                } else {
                    alert('Please select a task to analyze.');
                }
            });
        }
        
        // Import tasks button handler
        const importBtn = document.getElementById('import-tasks-btn');
        if (importBtn) {
            importBtn.addEventListener('click', function() {
                console.log('[METIS] Import parsed tasks clicked');
                window.metisComponent.importParsedTasks();
            });
        }
        
        // Reset parser button handler
        const resetBtn = document.getElementById('reset-parser-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                console.log('[METIS] Reset parser clicked');
                window.metisComponent.resetPRDParser();
            });
        }
        
        // Add dependency button handler
        const addDependencyBtn = document.getElementById('add-dependency-btn');
        if (addDependencyBtn) {
            addDependencyBtn.addEventListener('click', function() {
                console.log('[METIS] Add dependency clicked');
                window.metisComponent.addDependency();
            });
        }

    } catch (err) {
        console.error('[METIS] Error setting up event listeners:', err);
    }
};

/**
 * Load initial data for the component
 */
window.metisComponent.loadInitialData = function() {
    console.log('[METIS] Loading initial data');
    
    // In a real implementation, this would load data from the Metis API
    // For now, we'll use the sample data in the HTML
    
    // Could simulate API calls for demonstration purposes
    /*
    setTimeout(function() {
        // Show sample tasks after loading
        const loadingIndicator = document.getElementById('task-list-loading');
        const taskTable = document.getElementById('task-table');
        
        if (loadingIndicator && taskTable) {
            loadingIndicator.style.display = 'none';
            taskTable.style.display = 'table';
        }
    }, 1500);
    */
};

/**
 * Load content for a specific tab
 * @param {string} tabId - The ID of the selected tab
 */
window.metisComponent.loadTabContent = function(tabId) {
    console.log('[METIS] Loading content for tab:', tabId);
    
    // In a real implementation, this would load tab-specific data from the API
    // For demonstration purposes, we'll use the static HTML content
};

/**
 * Load content for a specific view within the Tasks tab
 * @param {string} viewId - The ID of the selected view
 */
window.metisComponent.loadViewContent = function(viewId) {
    console.log('[METIS] Loading content for view:', viewId);
    
    // In a real implementation, this would load different task visualizations
    // For demonstration purposes, we'll use the static HTML content
};

/**
 * Sort tasks based on a column
 * @param {string} sortBy - The column to sort by
 */
window.metisComponent.sortTasks = function(sortBy) {
    console.log('[METIS] Sorting tasks by:', sortBy);
    
    // In a real implementation, this would sort the tasks
    // For demonstration purposes, we'll just add a visual indicator
    
    const taskHeaders = document.querySelectorAll('.metis__task-header');
    taskHeaders.forEach(header => {
        if (header.getAttribute('data-sort') === sortBy) {
            header.textContent = header.textContent + ' ↓';
        } else if (header.getAttribute('data-sort')) {
            header.textContent = header.textContent.replace(' ↓', '').replace(' ↑', '');
        }
    });
};

/**
 * Analyze task complexity
 * @param {string} taskId - The ID of the task to analyze
 */
window.metisComponent.analyzeComplexity = function(taskId) {
    console.log('[METIS] Analyzing complexity for task:', taskId);
    
    // In a real implementation, this would call the API to analyze the task
    // For demonstration purposes, we'll just show the pre-defined complexity data
    
    // Simulate API call delay
    setTimeout(function() {
        // Just demonstrate the UI since we have pre-populated data
        alert('Complexity analysis complete for task ' + taskId);
    }, 1000);
};

/**
 * Parse PRD document into tasks
 */
window.metisComponent.parsePRD = function() {
    console.log('[METIS] Parsing PRD document');
    
    // In a real implementation, this would call the API to parse the document
    // For demonstration purposes, we'll show a simulated result
    
    // Get file input and preview container
    const fileInput = document.getElementById('prd-file-input');
    const preview = document.getElementById('prd-preview');
    const prdContent = document.getElementById('prd-content');
    const parsedTasksContainer = document.getElementById('parsed-tasks-container');
    const parsedTaskList = document.getElementById('parsed-task-list');
    
    if (fileInput && fileInput.files.length > 0 && preview && prdContent && parsedTasksContainer && parsedTaskList) {
        // Show loading state
        prdContent.innerHTML = '<div class="metis__loading-text">Parsing document...</div>';
        preview.style.display = 'block';
        
        // Simulate API call delay
        setTimeout(function() {
            // Display document preview (simulated)
            const fileName = fileInput.files[0].name;
            prdContent.innerHTML = `# ${fileName}\n\nThis is a simulated document preview. In a real implementation, this would show the actual document content.`;
            
            // Generate sample tasks
            parsedTaskList.innerHTML = `
                <div class="metis__parsed-task-item">
                    <h4>Task 1: Implement User Authentication</h4>
                    <p>Priority: High</p>
                    <p>Description: Implement user authentication system with login, logout, and password reset functionality.</p>
                </div>
                <div class="metis__parsed-task-item">
                    <h4>Task 2: Create Dashboard UI</h4>
                    <p>Priority: Medium</p>
                    <p>Description: Design and implement the main dashboard UI with data visualization.</p>
                </div>
                <div class="metis__parsed-task-item">
                    <h4>Task 3: Setup Database Schema</h4>
                    <p>Priority: High</p>
                    <p>Description: Design and implement the database schema for user accounts and application data.</p>
                </div>
            `;
            
            // Show the parsed tasks
            parsedTasksContainer.style.display = 'block';
            
        }, 2000);
    }
};

/**
 * Import parsed PRD tasks
 */
window.metisComponent.importParsedTasks = function() {
    console.log('[METIS] Importing parsed tasks');
    
    // In a real implementation, this would call the API to import the tasks
    // For demonstration purposes, we'll just switch to the Tasks tab
    
    alert('Tasks imported successfully!');
    
    // Switch to Tasks tab and reset the PRD parser
    window.metis_switchTab('tasks');
    window.metisComponent.resetPRDParser();
};

/**
 * Reset PRD parser
 */
window.metisComponent.resetPRDParser = function() {
    console.log('[METIS] Resetting PRD parser');
    
    // Reset the file input and hide the preview
    const fileInput = document.getElementById('prd-file-input');
    const uploadArea = document.getElementById('prd-upload-area');
    const preview = document.getElementById('prd-preview');
    const parsedTasksContainer = document.getElementById('parsed-tasks-container');
    const parseButton = document.getElementById('parse-prd-btn');
    
    if (fileInput) {
        fileInput.value = '';
    }
    
    if (uploadArea) {
        uploadArea.innerHTML = `
            <div class="metis__upload-icon">📄</div>
            <div class="metis__upload-text">Drag & drop a PRD document here or</div>
            <label for="prd-file-input" class="metis__upload-button">Browse Files</label>
            <input type="file" id="prd-file-input" class="metis__file-input" accept=".md,.txt,.docx,.pdf">
        `;
    }
    
    if (preview) {
        preview.style.display = 'none';
    }
    
    if (parsedTasksContainer) {
        parsedTasksContainer.style.display = 'none';
    }
    
    if (parseButton) {
        parseButton.disabled = true;
    }
};

/**
 * Add task dependency
 */
window.metisComponent.addDependency = function() {
    console.log('[METIS] Adding dependency');
    
    // Get form values
    const taskSelect = document.getElementById('dependency-task-select');
    const dependsOnSelect = document.getElementById('dependency-depends-on-select');
    const typeSelect = document.getElementById('dependency-type-select');
    
    if (taskSelect && dependsOnSelect && typeSelect) {
        const taskId = taskSelect.value;
        const dependsOnId = dependsOnSelect.value;
        const type = typeSelect.value;
        
        if (!taskId || !dependsOnId) {
            alert('Please select both task and dependency.');
            return;
        }
        
        if (taskId === dependsOnId) {
            alert('A task cannot depend on itself.');
            return;
        }
        
        console.log('[METIS] Adding dependency:', taskId, 'depends on', dependsOnId, 'with type', type);
        
        // In a real implementation, this would call the API to add the dependency
        // For demonstration purposes, we'll just show a confirmation
        
        alert('Dependency added successfully!');
        
        // Reset the form
        taskSelect.value = '';
        dependsOnSelect.value = '';
        typeSelect.value = 'blocks';
    }
};

/**
 * Send chat message from input field
 */
window.metisComponent.sendChatMessage = function() {
    const chatInput = document.getElementById('chat-input');
    if (!chatInput || !chatInput.value.trim()) return;
    
    const message = chatInput.value.trim();
    console.log('[METIS] Sending chat message:', message);
    
    // Clear input field
    chatInput.value = '';
    
    // Get active tab to determine which chat panel to update
    const activeTab = window.metisComponent.state.activeTab;
    let messageContainer;
    
    if (activeTab === 'workflow') {
        messageContainer = document.getElementById('workflow-messages');
    } else if (activeTab === 'teamchat') {
        messageContainer = document.getElementById('teamchat-messages');
    } else {
        // If we're not in a chat tab, use teamchat as default
        messageContainer = document.getElementById('teamchat-messages');
        // Switch to teamchat tab
        window.metis_switchTab('teamchat');
    }
    
    if (messageContainer) {
        // Create and add user message
        const userMessageElement = document.createElement('div');
        userMessageElement.className = 'metis__message metis__message--user';
        userMessageElement.textContent = message;
        messageContainer.appendChild(userMessageElement);
        
        // Scroll to bottom of chat
        messageContainer.scrollTop = messageContainer.scrollHeight;
        
        // Simulate AI response after a delay
        setTimeout(function() {
            // Create and add AI response
            const aiMessageElement = document.createElement('div');
            aiMessageElement.className = 'metis__message metis__message--ai';
            
            // Different response based on chat type
            if (activeTab === 'workflow') {
                aiMessageElement.textContent = 'I can help you with your workflow queries. This is a simulated response to demonstrate the chat functionality.';
            } else {
                aiMessageElement.textContent = 'This is a team chat message that would be shared across all Tekton components. This is a simulated response to demonstrate the chat functionality.';
            }
            
            messageContainer.appendChild(aiMessageElement);
            
            // Scroll to bottom again
            messageContainer.scrollTop = messageContainer.scrollHeight;
        }, 1000);
    }
};

/**
 * Save component state (for persistence between page loads)
 */
window.metisComponent.saveComponentState = function() {
    console.log('[METIS] Saving component state');
    
    // In a real implementation, this would save the state to localStorage or another persistence mechanism
    // For demonstration purposes, we'll just log the state
    
    console.log('[METIS] Current state:', window.metisComponent.state);
};