/**
 * Tekton Core Component
 * 
 * Provides a comprehensive interface for GitHub project management,
 * including repositories, branches, pull requests, and project workflows.
 */

// Import services - Note: In a full implementation, these would be proper ES module imports
// But for simplicity and compatibility with the existing script loading mechanism, we'll define them globally
// The actual service files are still created with ES module export syntax for future compatibility

class TektonComponent {
    constructor() {
        // Initialize services
        this.gitHubService = window.GitHubService ? new window.GitHubService() : null;
        this.projectManager = window.ProjectManager && this.gitHubService ? 
            new window.ProjectManager(this.gitHubService) : null;
            
        // Initialize state
        this.state = {
            activeTab: 'projects',
            projects: [],
            repositories: [],
            branches: [],
            loading: false
        };
        
        console.log('[TEKTON] Component constructed');
        
        // If services aren't available yet, load them
        if (!this.gitHubService || !this.projectManager) {
            this.loadServices();
        }
    }
    
    /**
     * Load GitHub and Project Manager services
     */
    loadServices() {
        console.log('[TEKTON] Loading services...');
        
        // Load GitHub service
        const gitHubServiceScript = document.createElement('script');
        gitHubServiceScript.src = '/scripts/tekton/github-service.js';
        gitHubServiceScript.onload = () => {
            console.log('[TEKTON] GitHub service loaded');
            
            // Create GitHub service instance if available
            if (window.GitHubService) {
                this.gitHubService = new window.GitHubService();
                
                // Try to initialize project manager once GitHub service is loaded
                if (window.ProjectManager) {
                    this.projectManager = new window.ProjectManager(this.gitHubService);
                    
                    // If both services are now loaded, initialize components that depend on them
                    if (this.state.initialized) {
                        this.loadInitialData();
                    }
                }
            }
        };
        
        // Load Project Manager service
        const projectManagerScript = document.createElement('script');
        projectManagerScript.src = '/scripts/tekton/project-manager.js';
        projectManagerScript.onload = () => {
            console.log('[TEKTON] Project Manager service loaded');
            
            // Create Project Manager instance if GitHub service is already loaded
            if (window.ProjectManager && this.gitHubService) {
                this.projectManager = new window.ProjectManager(this.gitHubService);
                
                // If both services are now loaded, initialize components that depend on them
                if (this.state.initialized) {
                    this.loadInitialData();
                }
            }
        };
        
        // Append scripts to document
        document.body.appendChild(gitHubServiceScript);
        document.body.appendChild(projectManagerScript);
    }
    
    async init() {
        console.log('[TEKTON] Initializing component');
        this.setupEventListeners();
        this.loadComponentState();
        
        // Mark as initialized
        this.state.initialized = true;
        
        // Load initial data if services are available
        if (this.gitHubService && this.projectManager) {
            this.loadInitialData();
        }
    }
    
    /**
     * Load initial data for the component
     */
    loadInitialData() {
        console.log('[TEKTON] Loading initial data');
        this.loadTabContent(this.state.activeTab);
    }
    
    setupEventListeners() {
        // Find our component container
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) {
            console.error('[TEKTON] Cannot find tekton container for setting up event listeners');
            return;
        }
        
        // Set up chat input
        const chatInput = tektonContainer.querySelector('#chat-input');
        const sendButton = tektonContainer.querySelector('#send-button');
        
        if (chatInput && sendButton) {
            // Send message on button click
            sendButton.addEventListener('click', () => this.sendChatMessage());
            
            // Send message on Enter key
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendChatMessage();
                }
            });
        }
        
        // Set up Projects tab events
        const newProjectBtn = tektonContainer.querySelector('#new-project-btn');
        if (newProjectBtn) {
            newProjectBtn.addEventListener('click', () => this.createNewProject());
        }
        
        const importProjectBtn = tektonContainer.querySelector('#import-project-btn');
        if (importProjectBtn) {
            importProjectBtn.addEventListener('click', () => this.importProject());
        }
        
        // Set up Repositories tab events
        const cloneRepoBtn = tektonContainer.querySelector('#clone-repo-btn');
        if (cloneRepoBtn) {
            cloneRepoBtn.addEventListener('click', () => this.cloneRepository());
        }
        
        const createRepoBtn = tektonContainer.querySelector('#create-repo-btn');
        if (createRepoBtn) {
            createRepoBtn.addEventListener('click', () => this.createRepository());
        }
        
        // Set up Branches tab events
        const createBranchBtn = tektonContainer.querySelector('#create-branch-btn');
        if (createBranchBtn) {
            createBranchBtn.addEventListener('click', () => this.createBranch());
        }
        
        const mergeBranchBtn = tektonContainer.querySelector('#merge-branch-btn');
        if (mergeBranchBtn) {
            mergeBranchBtn.addEventListener('click', () => this.mergeBranch());
        }
        
        // Setup action card buttons
        this.setupActionCardButtons(tektonContainer);
    }
    
    setupActionCardButtons(tektonContainer) {
        // Repository operations in Actions panel
        const repoCard = tektonContainer.querySelector('#actions-panel .tekton__action-card:nth-child(1)');
        if (repoCard) {
            const buttons = repoCard.querySelectorAll('.tekton__card-action-btn');
            
            // Clone Repository
            if (buttons[0]) {
                buttons[0].addEventListener('click', () => this.cloneRepository());
            }
            
            // Create Repository
            if (buttons[1]) {
                buttons[1].addEventListener('click', () => this.createRepository());
            }
            
            // Fork Repository
            if (buttons[2]) {
                buttons[2].addEventListener('click', () => this.forkRepository());
            }
        }
        
        // Branch operations
        const branchCard = tektonContainer.querySelector('#actions-panel .tekton__action-card:nth-child(2)');
        if (branchCard) {
            const buttons = branchCard.querySelectorAll('.tekton__card-action-btn');
            
            // Create Branch
            if (buttons[0]) {
                buttons[0].addEventListener('click', () => this.createBranch());
            }
            
            // Merge Branch
            if (buttons[1]) {
                buttons[1].addEventListener('click', () => this.mergeBranch());
            }
            
            // Sync Branch
            if (buttons[2]) {
                buttons[2].addEventListener('click', () => this.syncBranch());
            }
            
            // Delete Branch
            if (buttons[3]) {
                buttons[3].addEventListener('click', () => this.deleteBranch());
            }
        }
        
        // Commit operations
        const commitCard = tektonContainer.querySelector('#actions-panel .tekton__action-card:nth-child(3)');
        if (commitCard) {
            const buttons = commitCard.querySelectorAll('.tekton__card-action-btn');
            
            // Create Commit
            if (buttons[0]) {
                buttons[0].addEventListener('click', () => this.createCommit());
            }
            
            // Push Changes
            if (buttons[1]) {
                buttons[1].addEventListener('click', () => this.pushChanges());
            }
            
            // Pull Changes
            if (buttons[2]) {
                buttons[2].addEventListener('click', () => this.pullChanges());
            }
            
            // View History
            if (buttons[3]) {
                buttons[3].addEventListener('click', () => this.viewHistory());
            }
        }
        
        // PR operations
        const prCard = tektonContainer.querySelector('#actions-panel .tekton__action-card:nth-child(4)');
        if (prCard) {
            const buttons = prCard.querySelectorAll('.tekton__card-action-btn');
            
            // Create PR
            if (buttons[0]) {
                buttons[0].addEventListener('click', () => this.createPullRequest());
            }
            
            // List PRs
            if (buttons[1]) {
                buttons[1].addEventListener('click', () => this.listPullRequests());
            }
            
            // Review PR
            if (buttons[2]) {
                buttons[2].addEventListener('click', () => this.reviewPullRequest());
            }
            
            // Merge PR
            if (buttons[3]) {
                buttons[3].addEventListener('click', () => this.mergePullRequest());
            }
        }
    }
    
    async loadProjects() {
        console.log('[TEKTON] Loading projects');
        
        // Ensure project manager is available
        if (!this.projectManager) {
            console.error('[TEKTON] Project manager not available');
            this.showErrorMessage('Project manager not available');
            return;
        }
        
        try {
            // Toggle loading indicator
            this.toggleLoading('project-list', true);
            
            // Fetch projects from the project manager
            const projects = await this.projectManager.getProjects();
            this.state.projects = projects;
            
            // Update the UI with projects
            this.renderProjects();
        } catch (error) {
            console.error('[TEKTON] Error loading projects:', error);
            this.showErrorMessage('Failed to load projects');
        } finally {
            // Hide loading indicator
            this.toggleLoading('project-list', false);
        }
    }
    
    renderProjects() {
        console.log('[TEKTON] Rendering projects:', this.state.projects.length);
        
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) {
            console.error('[TEKTON] Cannot find tekton container for rendering projects');
            return;
        }
        
        const projectList = tektonContainer.querySelector('#project-list');
        if (!projectList) {
            console.error('[TEKTON] Cannot find project list for rendering projects');
            return;
        }
        
        // Clear existing project items
        projectList.innerHTML = '';
        
        // Add projects to the list
        if (this.state.projects.length === 0) {
            projectList.innerHTML = '<div class="tekton__empty-message">No projects found. Create or import a project to get started.</div>';
        } else {
            this.state.projects.forEach(project => {
                const projectItem = document.createElement('div');
                projectItem.className = 'tekton__project-item';
                
                projectItem.innerHTML = `
                    <div class="tekton__project-info">
                        <div class="tekton__project-name">${project.name}</div>
                        <div class="tekton__project-meta">
                            <span class="tekton__project-repo">${project.repository}</span>
                            <span class="tekton__project-branch">${project.branch}</span>
                        </div>
                    </div>
                    <div class="tekton__project-actions">
                        <button class="tekton__project-action-btn" data-action="open" data-project="${project.name}">Open</button>
                        <button class="tekton__project-action-btn" data-action="settings" data-project="${project.name}">Settings</button>
                    </div>
                `;
                
                projectList.appendChild(projectItem);
                
                // Add event listeners to action buttons
                const openBtn = projectItem.querySelector('[data-action="open"]');
                if (openBtn) {
                    openBtn.addEventListener('click', () => this.openProject(project.name));
                }
                
                const settingsBtn = projectItem.querySelector('[data-action="settings"]');
                if (settingsBtn) {
                    settingsBtn.addEventListener('click', () => this.openProjectSettings(project.name));
                }
            });
        }
        
        // Show the project list
        projectList.style.display = 'flex';
    }
    
    async loadRepositories() {
        console.log('[TEKTON] Loading repositories');
        
        // Ensure GitHub service is available
        if (!this.gitHubService) {
            console.error('[TEKTON] GitHub service not available');
            this.showErrorMessage('GitHub service not available');
            return;
        }
        
        try {
            this.toggleLoading('repositories-list', true);
            
            // Fetch repositories from GitHub service
            const repositories = await this.gitHubService.getRepositories();
            this.state.repositories = repositories;
            
            // Render repositories
            this.renderRepositories();
        } catch (error) {
            console.error('[TEKTON] Error loading repositories:', error);
            this.showErrorMessage('Failed to load repositories');
        } finally {
            this.toggleLoading('repositories-list', false);
        }
    }
    
    renderRepositories() {
        console.log('[TEKTON] Rendering repositories:', this.state.repositories.length);
        
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) {
            console.error('[TEKTON] Cannot find tekton container for rendering repositories');
            return;
        }
        
        const repoList = tektonContainer.querySelector('#repositories-list');
        if (!repoList) {
            console.error('[TEKTON] Cannot find repositories list for rendering');
            return;
        }
        
        // Get the table body
        const tableBody = repoList.querySelector('tbody');
        if (!tableBody) {
            console.error('[TEKTON] Cannot find repositories table body for rendering');
            return;
        }
        
        // Clear existing repository rows
        tableBody.innerHTML = '';
        
        // Add repositories to the table
        if (this.state.repositories.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="tekton__empty-message">No repositories found.</td></tr>';
        } else {
            this.state.repositories.forEach(repo => {
                const row = document.createElement('tr');
                row.className = 'tekton__repository-row';
                
                // Format the date
                const updatedDate = repo.updated.toLocaleDateString();
                
                row.innerHTML = `
                    <td>${repo.name}</td>
                    <td>${repo.owner}</td>
                    <td>${repo.branches}</td>
                    <td>${updatedDate}</td>
                    <td>
                        <button class="tekton__table-action-btn" data-action="open" data-repo="${repo.name}">Open</button>
                        <button class="tekton__table-action-btn" data-action="fork" data-repo="${repo.name}">Fork</button>
                    </td>
                `;
                
                tableBody.appendChild(row);
                
                // Add event listeners to action buttons
                const openBtn = row.querySelector('[data-action="open"]');
                if (openBtn) {
                    openBtn.addEventListener('click', () => this.openRepository(repo.name));
                }
                
                const forkBtn = row.querySelector('[data-action="fork"]');
                if (forkBtn) {
                    forkBtn.addEventListener('click', () => this.forkRepository(repo.name, repo.owner));
                }
            });
        }
        
        // Show the repositories list
        repoList.style.display = 'block';
    }
    
    async loadBranches() {
        console.log('[TEKTON] Loading branches');
        
        // Ensure GitHub service is available
        if (!this.gitHubService) {
            console.error('[TEKTON] GitHub service not available');
            this.showErrorMessage('GitHub service not available');
            return;
        }
        
        try {
            this.toggleLoading('branches-list', true);
            
            // Fetch branches from GitHub service
            const branches = await this.gitHubService.getBranches();
            this.state.branches = branches;
            
            // Render branches
            this.renderBranches();
        } catch (error) {
            console.error('[TEKTON] Error loading branches:', error);
            this.showErrorMessage('Failed to load branches');
        } finally {
            this.toggleLoading('branches-list', false);
        }
    }
    
    renderBranches() {
        console.log('[TEKTON] Rendering branches:', this.state.branches.length);
        
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) {
            console.error('[TEKTON] Cannot find tekton container for rendering branches');
            return;
        }
        
        const branchesList = tektonContainer.querySelector('#branches-list');
        if (!branchesList) {
            console.error('[TEKTON] Cannot find branches list for rendering');
            return;
        }
        
        // Get the table body
        const tableBody = branchesList.querySelector('tbody');
        if (!tableBody) {
            console.error('[TEKTON] Cannot find branches table body for rendering');
            return;
        }
        
        // Clear existing branch rows
        tableBody.innerHTML = '';
        
        // Add branches to the table
        if (this.state.branches.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="tekton__empty-message">No branches found.</td></tr>';
        } else {
            this.state.branches.forEach(branch => {
                const row = document.createElement('tr');
                row.className = branch.status === 'Active' ? 'tekton__branch-row tekton__branch-row--active' : 'tekton__branch-row';
                
                // Format the date
                const commitDate = branch.lastCommit.toLocaleDateString();
                
                row.innerHTML = `
                    <td>${branch.name}</td>
                    <td>${branch.repository}</td>
                    <td>${branch.status}</td>
                    <td>${commitDate}</td>
                    <td>
                        <button class="tekton__table-action-btn" data-action="checkout" data-branch="${branch.name}" data-repo="${branch.repository}">Checkout</button>
                        <button class="tekton__table-action-btn" data-action="pull" data-branch="${branch.name}" data-repo="${branch.repository}">Pull</button>
                    </td>
                `;
                
                tableBody.appendChild(row);
                
                // Add event listeners to action buttons
                const checkoutBtn = row.querySelector('[data-action="checkout"]');
                if (checkoutBtn) {
                    checkoutBtn.addEventListener('click', () => this.checkoutBranch(branch.repository, branch.name));
                }
                
                const pullBtn = row.querySelector('[data-action="pull"]');
                if (pullBtn) {
                    pullBtn.addEventListener('click', () => this.pullBranch(branch.repository, branch.name));
                }
            });
        }
        
        // Show the branches list
        branchesList.style.display = 'block';
    }
    
    // Chat Functionality
    
    sendChatMessage() {
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) return;
        
        const chatInput = tektonContainer.querySelector('#chat-input');
        if (!chatInput || !chatInput.value.trim()) return;
        
        const message = chatInput.value.trim();
        const activeTab = this.state.activeTab;
        
        if (activeTab === 'projectchat' || activeTab === 'teamchat') {
            this.addChatMessage(message, activeTab);
            chatInput.value = '';
        }
    }
    
    addChatMessage(message, chatType) {
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) return;
        
        let chatContainer;
        if (chatType === 'projectchat') {
            chatContainer = tektonContainer.querySelector('#projectchat-messages');
        } else if (chatType === 'teamchat') {
            chatContainer = tektonContainer.querySelector('#teamchat-messages');
        }
        
        if (!chatContainer) return;
        
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = 'tekton__message tekton__message--user';
        
        messageEl.innerHTML = `
            <div class="tekton__message-content">
                <div class="tekton__message-text">${message}</div>
            </div>
        `;
        
        // Add to chat container
        chatContainer.appendChild(messageEl);
        
        // Auto-scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Generate a response (mock for now)
        setTimeout(() => {
            this.addAIResponse("I'll help you with that request. This is a placeholder response for now.", chatType);
        }, 1000);
    }
    
    addAIResponse(message, chatType) {
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) return;
        
        let chatContainer;
        if (chatType === 'projectchat') {
            chatContainer = tektonContainer.querySelector('#projectchat-messages');
        } else if (chatType === 'teamchat') {
            chatContainer = tektonContainer.querySelector('#teamchat-messages');
        }
        
        if (!chatContainer) return;
        
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = 'tekton__message tekton__message--ai';
        
        messageEl.innerHTML = `
            <div class="tekton__message-content">
                <div class="tekton__message-text">${message}</div>
            </div>
        `;
        
        // Add to chat container
        chatContainer.appendChild(messageEl);
        
        // Auto-scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Action Functions
    
    openProject(projectName) {
        console.log('[TEKTON] Opening project:', projectName);
        // In a full implementation, this would open the project details
    }
    
    openProjectSettings(projectName) {
        console.log('[TEKTON] Opening project settings:', projectName);
        // In a full implementation, this would open project settings
    }
    
    createNewProject() {
        console.log('[TEKTON] Creating new project');
        // In a full implementation, this would show a project creation dialog
    }
    
    importProject() {
        console.log('[TEKTON] Importing project');
        // In a full implementation, this would show a project import dialog
    }
    
    openRepository(repoName) {
        console.log('[TEKTON] Opening repository:', repoName);
        // In a full implementation, this would open the repository details
    }
    
    cloneRepository(repoName, owner) {
        console.log('[TEKTON] Cloning repository:', repoName, owner);
        // In a full implementation, this would show a repository clone dialog
    }
    
    createRepository() {
        console.log('[TEKTON] Creating repository');
        // In a full implementation, this would show a repository creation dialog
    }
    
    forkRepository(repoName, owner) {
        console.log('[TEKTON] Forking repository:', repoName, owner);
        // In a full implementation, this would fork the repository
    }
    
    checkoutBranch(repoName, branchName) {
        console.log('[TEKTON] Checking out branch:', repoName, branchName);
        // In a full implementation, this would check out the branch
    }
    
    pullBranch(repoName, branchName) {
        console.log('[TEKTON] Pulling branch:', repoName, branchName);
        // In a full implementation, this would pull the latest changes
    }
    
    createBranch() {
        console.log('[TEKTON] Creating branch');
        // In a full implementation, this would show a branch creation dialog
    }
    
    mergeBranch() {
        console.log('[TEKTON] Merging branch');
        // In a full implementation, this would show a branch merge dialog
    }
    
    syncBranch() {
        console.log('[TEKTON] Syncing branch');
        // In a full implementation, this would sync the branch with its upstream
    }
    
    deleteBranch() {
        console.log('[TEKTON] Deleting branch');
        // In a full implementation, this would delete the branch
    }
    
    createCommit() {
        console.log('[TEKTON] Creating commit');
        // In a full implementation, this would show a commit creation dialog
    }
    
    pushChanges() {
        console.log('[TEKTON] Pushing changes');
        // In a full implementation, this would push local changes
    }
    
    pullChanges() {
        console.log('[TEKTON] Pulling changes');
        // In a full implementation, this would pull remote changes
    }
    
    viewHistory() {
        console.log('[TEKTON] Viewing commit history');
        // In a full implementation, this would show commit history
    }
    
    createPullRequest() {
        console.log('[TEKTON] Creating pull request');
        // In a full implementation, this would show a PR creation dialog
    }
    
    listPullRequests() {
        console.log('[TEKTON] Listing pull requests');
        // In a full implementation, this would show a list of PRs
    }
    
    reviewPullRequest() {
        console.log('[TEKTON] Reviewing pull request');
        // In a full implementation, this would show a PR review dialog
    }
    
    mergePullRequest() {
        console.log('[TEKTON] Merging pull request');
        // In a full implementation, this would merge a PR
    }
    
    // Helper methods
    
    toggleLoading(elementId, isLoading) {
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) return;
        
        const loadingIndicator = tektonContainer.querySelector(`#${elementId}-loading`);
        const contentElement = tektonContainer.querySelector(`#${elementId}`);
        
        if (loadingIndicator && contentElement) {
            if (isLoading) {
                loadingIndicator.style.display = 'flex';
                contentElement.style.display = 'none';
            } else {
                loadingIndicator.style.display = 'none';
                contentElement.style.display = '';
            }
        }
    }
    
    showErrorMessage(message) {
        console.error('[TEKTON] Error:', message);
        // In a full implementation, this would show an error UI element
    }
    
    updateChatPlaceholder(tabId) {
        const tektonContainer = document.querySelector('.tekton');
        if (!tektonContainer) return;
        
        const chatInput = tektonContainer.querySelector('#chat-input');
        if (!chatInput) return;
        
        if (tabId === 'projectchat') {
            chatInput.placeholder = 'Ask about GitHub projects, repositories, branches...';
        } else if (tabId === 'teamchat') {
            chatInput.placeholder = 'Chat with your team...';
        } else {
            chatInput.placeholder = 'Enter chat message, project query, or GitHub command';
        }
    }
    
    loadTabContent(tabId) {
        console.log(`[TEKTON] Loading content for ${tabId} tab`);
        
        switch (tabId) {
            case 'projects':
                this.loadProjects();
                break;
            case 'repositories':
                this.loadRepositories();
                break;
            case 'branches':
                this.loadBranches();
                break;
            case 'actions':
                // Nothing to load for actions tab
                break;
        }
    }
    
    saveComponentState() {
        // Save component state to localStorage or similar for persistence
        console.log('[TEKTON] Saving component state');
        try {
            const stateToSave = {
                activeTab: this.state.activeTab
            };
            localStorage.setItem('tektonComponentState', JSON.stringify(stateToSave));
        } catch (error) {
            console.error('[TEKTON] Error saving component state:', error);
        }
    }
    
    loadComponentState() {
        // Load component state from localStorage or similar
        console.log('[TEKTON] Loading component state');
        try {
            const savedState = localStorage.getItem('tektonComponentState');
            if (savedState) {
                const parsedState = JSON.parse(savedState);
                if (parsedState.activeTab) {
                    this.state.activeTab = parsedState.activeTab;
                    window.tekton_switchTab(this.state.activeTab);
                }
            }
        } catch (error) {
            console.error('[TEKTON] Error loading component state:', error);
        }
    }
}

// Expose GitHubService class for simpler service loading/integration
window.GitHubService = class GitHubService {
    constructor() {
        console.log('[TEKTON] GitHubService initialized');
    }
    
    async getRepositories() {
        console.log('[TEKTON] Getting repositories');
        try {
            // Mock data for now
            return [
                { name: 'Tekton', owner: 'cskoons', branches: 4, updated: new Date() },
                { name: 'sample-project', owner: 'cskoons', branches: 1, updated: new Date(Date.now() - 86400000) }
            ];
        } catch (error) {
            console.error('[TEKTON] Error getting repositories:', error);
            throw error;
        }
    }
    
    async getBranches() {
        console.log('[TEKTON] Getting branches');
        try {
            // Mock data for now
            return [
                { name: 'main', repository: 'Tekton', status: 'Current', lastCommit: new Date(Date.now() - 172800000) },
                { name: 'sprint/Clean_Slate_051125', repository: 'Tekton', status: 'Active', lastCommit: new Date() }
            ];
        } catch (error) {
            console.error('[TEKTON] Error getting branches:', error);
            throw error;
        }
    }
};

// Expose ProjectManager class for simpler service loading/integration
window.ProjectManager = class ProjectManager {
    constructor(gitHubService) {
        this.gitHubService = gitHubService;
        console.log('[TEKTON] ProjectManager initialized');
    }
    
    async getProjects() {
        console.log('[TEKTON] Getting projects');
        try {
            // Mock data for now
            return [
                { 
                    name: 'Tekton', 
                    repository: 'cskoons/Tekton', 
                    branch: 'sprint/Clean_Slate_051125' 
                },
                { 
                    name: 'Sample Project', 
                    repository: 'cskoons/sample-project', 
                    branch: 'main' 
                }
            ];
        } catch (error) {
            console.error('[TEKTON] Error getting projects:', error);
            throw error;
        }
    }
};

// Create global instance
window.tektonComponent = new TektonComponent();

// Initialize the component when the script loads
window.tektonComponent.init().catch(err => {
    console.error('[TEKTON] Initialization error:', err);
});