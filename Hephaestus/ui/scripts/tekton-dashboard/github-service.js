/**
 * GitHub Service
 * Provides communication with the GitHub API for repository management, 
 * issue tracking, and project synchronization
 */

console.log('[FILE_TRACE] Loading: github-service.js');
class GitHubService extends window.tektonUI.componentUtils.BaseService {
    constructor() {
        // Call base service with service name and default API endpoint
        const hermesPort = window.HERMES_PORT || 8001;
        super('githubService', `http://localhost:${hermesPort}/api/github`);
        
        // GitHub data collections
        this.repositories = [];
        this.issues = {};
        this.pullRequests = {};
        this.commits = {};
        this.webhooks = {};
        this.projectLinks = [];
        
        // Authentication state
        this.authenticated = false;
        this.authToken = null;
        this.currentUser = null;
        this.enterpriseUrl = null;
        
        // Rate limiting info
        this.rateLimit = {
            limit: 0,
            remaining: 0,
            resetTime: null
        };
        
        // Cache settings
        this.cacheTTL = 5 * 60 * 1000; // 5 minutes
        this.cache = {
            repositories: {
                data: null,
                timestamp: 0
            },
            issues: {},
            pullRequests: {},
            commits: {},
            branches: {}
        };
        
        // Initialize with persisted state if available
        this._loadPersistedState();
    }

    /**
     * Connect to the GitHub API
     * @returns {Promise<boolean>} - Promise resolving to connection status
     */
    async connect() {
        try {
            // Load authentication from storage
            await this._loadAuthenticationState();
            
            // Check if we have an auth token
            if (!this.authToken) {
                this.authenticated = false;
                this.dispatchEvent('authenticationRequired', {});
                return false;
            }
            
            // Verify auth token is valid by getting user info
            const userInfo = await this._getCurrentUser();
            if (!userInfo) {
                this.authenticated = false;
                this.authToken = null;
                this._persistAuthState();
                this.dispatchEvent('authenticationRequired', {});
                return false;
            }
            
            // Successfully authenticated
            this.authenticated = true;
            this.currentUser = userInfo;
            this.dispatchEvent('connected', { 
                user: this.currentUser
            });
            
            return true;
        } catch (error) {
            console.error('Failed to connect to GitHub API:', error);
            this.authenticated = false;
            this.dispatchEvent('connectionFailed', { 
                error: `Failed to connect to GitHub API: ${error.message}` 
            });
            return false;
        }
    }
    
    /**
     * Start the OAuth authentication flow
     * @param {Object} options - Auth options
     * @returns {string} - OAuth URL to redirect to
     */
    startOAuthFlow(options = {}) {
        // Generate state parameter to prevent CSRF
        const state = Math.random().toString(36).substring(2, 15);
        localStorage.setItem('github_oauth_state', state);
        
        // Set GitHub Enterprise URL if provided
        if (options.enterpriseUrl) {
            this.enterpriseUrl = options.enterpriseUrl;
            this._persistAuthState();
        }
        
        // Construct OAuth URL
        const baseUrl = this.enterpriseUrl ? 
            `${this.enterpriseUrl}/login/oauth/authorize` : 
            'https://github.com/login/oauth/authorize';
        
        const params = new URLSearchParams({
            client_id: options.clientId || '<CLIENT_ID>',
            redirect_uri: options.redirectUri || window.location.origin + '/github/callback',
            scope: options.scope || 'repo user',
            state: state
        });
        
        const oauthUrl = `${baseUrl}?${params.toString()}`;
        
        // Dispatch event for the OAuth URL
        this.dispatchEvent('oauthUrlGenerated', { url: oauthUrl });
        
        return oauthUrl;
    }
    
    /**
     * Handle OAuth callback and complete authentication
     * @param {string} code - OAuth code from callback
     * @param {string} state - OAuth state from callback
     * @returns {Promise<boolean>} - Authentication success
     */
    async handleOAuthCallback(code, state) {
        // Verify state parameter to prevent CSRF
        const storedState = localStorage.getItem('github_oauth_state');
        if (state !== storedState) {
            this.dispatchEvent('error', { 
                error: 'OAuth state mismatch. Authentication failed.' 
            });
            return false;
        }
        
        try {
            // Exchange code for access token
            const response = await fetch(`${this.apiUrl}/oauth/callback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ code, state })
            });
            
            if (!response.ok) {
                throw new Error(`OAuth token exchange failed: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Store the access token
            this.authToken = data.access_token;
            this.authenticated = true;
            
            // Get user info
            await this._getCurrentUser();
            
            // Persist authentication state
            this._persistAuthState();
            
            // Dispatch authentication event
            this.dispatchEvent('authenticated', { 
                user: this.currentUser 
            });
            
            return true;
        } catch (error) {
            console.error('OAuth authentication failed:', error);
            this.dispatchEvent('error', { 
                error: `OAuth authentication failed: ${error.message}` 
            });
            return false;
        } finally {
            // Clean up state parameter
            localStorage.removeItem('github_oauth_state');
        }
    }
    
    /**
     * Logout and clear authentication
     */
    logout() {
        this.authenticated = false;
        this.authToken = null;
        this.currentUser = null;
        this._persistAuthState();
        
        // Clear cached data
        this.repositories = [];
        this.issues = {};
        this.pullRequests = {};
        this.commits = {};
        this.webhooks = {};
        
        this.dispatchEvent('loggedOut', {});
    }
    
    /**
     * Get repositories for authenticated user
     * @param {Object} options - Filter options
     * @returns {Promise<Array>} - List of repositories
     */
    async getRepositories(options = {}) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return [];
            }
        }
        
        // Check cache unless forced refresh
        if (!options.forceRefresh && 
            this.cache.repositories.data && 
            (Date.now() - this.cache.repositories.timestamp < this.cacheTTL)) {
            
            let filteredRepos = this.cache.repositories.data;
            
            // Apply filters
            if (options.type) {
                filteredRepos = filteredRepos.filter(repo => repo.type === options.type);
            }
            
            if (options.query) {
                const query = options.query.toLowerCase();
                filteredRepos = filteredRepos.filter(repo => 
                    repo.name.toLowerCase().includes(query) || 
                    (repo.description && repo.description.toLowerCase().includes(query))
                );
            }
            
            if (options.language) {
                filteredRepos = filteredRepos.filter(repo => 
                    repo.language && repo.language.toLowerCase() === options.language.toLowerCase()
                );
            }
            
            return filteredRepos;
        }
        
        try {
            // Build query parameters
            const queryParams = new URLSearchParams();
            if (options.type) queryParams.append('type', options.type);
            if (options.page) queryParams.append('page', options.page);
            if (options.perPage) queryParams.append('per_page', options.perPage);
            if (options.sort) queryParams.append('sort', options.sort);
            
            // Make API request
            const url = `${this.apiUrl}/repositories?${queryParams.toString()}`;
            const response = await this._githubApiRequest(url);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch repositories: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Update cache
            this.repositories = data.repositories || [];
            this.cache.repositories.data = this.repositories;
            this.cache.repositories.timestamp = Date.now();
            
            // Dispatch event with repositories
            this.dispatchEvent('repositoriesUpdated', { 
                repositories: this.repositories 
            });
            
            // Apply any filters requested
            let filteredRepos = this.repositories;
            
            if (options.query) {
                const query = options.query.toLowerCase();
                filteredRepos = filteredRepos.filter(repo => 
                    repo.name.toLowerCase().includes(query) || 
                    (repo.description && repo.description.toLowerCase().includes(query))
                );
            }
            
            if (options.language) {
                filteredRepos = filteredRepos.filter(repo => 
                    repo.language && repo.language.toLowerCase() === options.language.toLowerCase()
                );
            }
            
            return filteredRepos;
        } catch (error) {
            console.error('Failed to fetch repositories:', error);
            this.dispatchEvent('error', { 
                error: `Failed to fetch repositories: ${error.message}` 
            });
            return [];
        }
    }
    
    /**
     * Get repository details
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @returns {Promise<Object>} - Repository details
     */
    async getRepositoryDetails(owner, repo) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return null;
            }
        }
        
        try {
            const url = `${this.apiUrl}/repositories/${owner}/${repo}`;
            const response = await this._githubApiRequest(url);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch repository details: ${response.status} ${response.statusText}`);
            }
            
            const repository = await response.json();
            
            return repository;
        } catch (error) {
            console.error(`Failed to fetch repository details for ${owner}/${repo}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to fetch repository details: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Get repository branches
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @returns {Promise<Array>} - List of branches
     */
    async getRepositoryBranches(owner, repo) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return [];
            }
        }
        
        // Check cache
        const cacheKey = `${owner}/${repo}`;
        if (this.cache.branches[cacheKey] && 
            (Date.now() - this.cache.branches[cacheKey].timestamp < this.cacheTTL)) {
            return this.cache.branches[cacheKey].data;
        }
        
        try {
            const url = `${this.apiUrl}/repositories/${owner}/${repo}/branches`;
            const response = await this._githubApiRequest(url);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch repository branches: ${response.status} ${response.statusText}`);
            }
            
            const branches = await response.json();
            
            // Update cache
            this.cache.branches[cacheKey] = {
                data: branches,
                timestamp: Date.now()
            };
            
            return branches;
        } catch (error) {
            console.error(`Failed to fetch branches for ${owner}/${repo}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to fetch repository branches: ${error.message}` 
            });
            return [];
        }
    }
    
    /**
     * Get repository issues
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {Object} options - Filter options
     * @returns {Promise<Array>} - List of issues
     */
    async getRepositoryIssues(owner, repo, options = {}) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return [];
            }
        }
        
        // Check cache unless forced refresh
        const cacheKey = `${owner}/${repo}`;
        if (!options.forceRefresh && 
            this.cache.issues[cacheKey] && 
            (Date.now() - this.cache.issues[cacheKey].timestamp < this.cacheTTL)) {
            return this.cache.issues[cacheKey].data;
        }
        
        try {
            // Build query parameters
            const queryParams = new URLSearchParams();
            if (options.state) queryParams.append('state', options.state);
            if (options.labels) queryParams.append('labels', options.labels);
            if (options.assignee) queryParams.append('assignee', options.assignee);
            if (options.page) queryParams.append('page', options.page);
            if (options.perPage) queryParams.append('per_page', options.perPage);
            if (options.sort) queryParams.append('sort', options.sort);
            if (options.direction) queryParams.append('direction', options.direction);
            
            const url = `${this.apiUrl}/repositories/${owner}/${repo}/issues?${queryParams.toString()}`;
            const response = await this._githubApiRequest(url);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch repository issues: ${response.status} ${response.statusText}`);
            }
            
            const issues = await response.json();
            
            // Update cache
            this.cache.issues[cacheKey] = {
                data: issues,
                timestamp: Date.now()
            };
            
            // Update issues collection
            this.issues[cacheKey] = issues;
            
            // Dispatch event with issues
            this.dispatchEvent('issuesUpdated', { 
                owner, 
                repo, 
                issues 
            });
            
            return issues;
        } catch (error) {
            console.error(`Failed to fetch issues for ${owner}/${repo}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to fetch repository issues: ${error.message}` 
            });
            return [];
        }
    }
    
    /**
     * Get repository pull requests
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {Object} options - Filter options
     * @returns {Promise<Array>} - List of pull requests
     */
    async getRepositoryPullRequests(owner, repo, options = {}) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return [];
            }
        }
        
        // Check cache unless forced refresh
        const cacheKey = `${owner}/${repo}`;
        if (!options.forceRefresh && 
            this.cache.pullRequests[cacheKey] && 
            (Date.now() - this.cache.pullRequests[cacheKey].timestamp < this.cacheTTL)) {
            return this.cache.pullRequests[cacheKey].data;
        }
        
        try {
            // Build query parameters
            const queryParams = new URLSearchParams();
            if (options.state) queryParams.append('state', options.state);
            if (options.head) queryParams.append('head', options.head);
            if (options.base) queryParams.append('base', options.base);
            if (options.page) queryParams.append('page', options.page);
            if (options.perPage) queryParams.append('per_page', options.perPage);
            if (options.sort) queryParams.append('sort', options.sort);
            if (options.direction) queryParams.append('direction', options.direction);
            
            const url = `${this.apiUrl}/repositories/${owner}/${repo}/pulls?${queryParams.toString()}`;
            const response = await this._githubApiRequest(url);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch pull requests: ${response.status} ${response.statusText}`);
            }
            
            const pullRequests = await response.json();
            
            // Update cache
            this.cache.pullRequests[cacheKey] = {
                data: pullRequests,
                timestamp: Date.now()
            };
            
            // Update pull requests collection
            this.pullRequests[cacheKey] = pullRequests;
            
            // Dispatch event with pull requests
            this.dispatchEvent('pullRequestsUpdated', { 
                owner, 
                repo, 
                pullRequests 
            });
            
            return pullRequests;
        } catch (error) {
            console.error(`Failed to fetch pull requests for ${owner}/${repo}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to fetch pull requests: ${error.message}` 
            });
            return [];
        }
    }
    
    /**
     * Get repository commits
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {Object} options - Filter options
     * @returns {Promise<Array>} - List of commits
     */
    async getRepositoryCommits(owner, repo, options = {}) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return [];
            }
        }
        
        // Check cache unless forced refresh
        const cacheKey = `${owner}/${repo}`;
        if (!options.forceRefresh && 
            this.cache.commits[cacheKey] && 
            (Date.now() - this.cache.commits[cacheKey].timestamp < this.cacheTTL)) {
            return this.cache.commits[cacheKey].data;
        }
        
        try {
            // Build query parameters
            const queryParams = new URLSearchParams();
            if (options.sha) queryParams.append('sha', options.sha);
            if (options.path) queryParams.append('path', options.path);
            if (options.author) queryParams.append('author', options.author);
            if (options.page) queryParams.append('page', options.page);
            if (options.perPage) queryParams.append('per_page', options.perPage);
            
            const url = `${this.apiUrl}/repositories/${owner}/${repo}/commits?${queryParams.toString()}`;
            const response = await this._githubApiRequest(url);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch commits: ${response.status} ${response.statusText}`);
            }
            
            const commits = await response.json();
            
            // Update cache
            this.cache.commits[cacheKey] = {
                data: commits,
                timestamp: Date.now()
            };
            
            // Update commits collection
            this.commits[cacheKey] = commits;
            
            return commits;
        } catch (error) {
            console.error(`Failed to fetch commits for ${owner}/${repo}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to fetch commits: ${error.message}` 
            });
            return [];
        }
    }
    
    /**
     * Get commit details
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {string} sha - Commit SHA
     * @returns {Promise<Object>} - Commit details
     */
    async getCommitDetails(owner, repo, sha) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return null;
            }
        }
        
        try {
            const url = `${this.apiUrl}/repositories/${owner}/${repo}/commits/${sha}`;
            const response = await this._githubApiRequest(url);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch commit details: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Failed to fetch commit details for ${owner}/${repo}/${sha}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to fetch commit details: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Create a new repository
     * @param {Object} repositoryData - Repository information
     * @returns {Promise<Object>} - Created repository
     */
    async createRepository(repositoryData) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return null;
            }
        }
        
        try {
            const response = await this._githubApiRequest(`${this.apiUrl}/repositories`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(repositoryData)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to create repository: ${response.status} ${response.statusText}`);
            }
            
            const repository = await response.json();
            
            // Invalidate repositories cache
            this.cache.repositories.timestamp = 0;
            
            // Refresh repositories
            await this.getRepositories({ forceRefresh: true });
            
            // Dispatch event for new repository
            this.dispatchEvent('repositoryCreated', { repository });
            
            return repository;
        } catch (error) {
            console.error('Failed to create repository:', error);
            this.dispatchEvent('error', { 
                error: `Failed to create repository: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Fork a repository
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {Object} options - Fork options
     * @returns {Promise<Object>} - Forked repository
     */
    async forkRepository(owner, repo, options = {}) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return null;
            }
        }
        
        try {
            const response = await this._githubApiRequest(`${this.apiUrl}/repositories/${owner}/${repo}/forks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(options)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to fork repository: ${response.status} ${response.statusText}`);
            }
            
            const repository = await response.json();
            
            // Invalidate repositories cache
            this.cache.repositories.timestamp = 0;
            
            // Refresh repositories
            await this.getRepositories({ forceRefresh: true });
            
            // Dispatch event for new repository
            this.dispatchEvent('repositoryForked', { 
                parent: { owner, repo },
                repository 
            });
            
            return repository;
        } catch (error) {
            console.error(`Failed to fork repository ${owner}/${repo}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to fork repository: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Clone a repository to local machine
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {string} directory - Local directory path
     * @returns {Promise<Object>} - Clone result
     */
    async cloneRepository(owner, repo, directory) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return { success: false, error: 'Not authenticated' };
            }
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/repositories/${owner}/${repo}/clone`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ directory })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to clone repository: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            
            // Dispatch event for repository cloned
            this.dispatchEvent('repositoryCloned', { 
                owner, 
                repo, 
                directory, 
                success: true 
            });
            
            return result;
        } catch (error) {
            console.error(`Failed to clone repository ${owner}/${repo}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to clone repository: ${error.message}` 
            });
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Check clone status
     * @param {string} cloneId - Clone operation ID
     * @returns {Promise<Object>} - Clone status
     */
    async getCloneStatus(cloneId) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return { status: 'error', message: 'Not authenticated' };
            }
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/clone-status/${cloneId}`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (!response.ok) {
                throw new Error(`Failed to get clone status: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Failed to get clone status for ${cloneId}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to get clone status: ${error.message}` 
            });
            return { status: 'error', message: error.message };
        }
    }
    
    /**
     * Create a webhook for a repository
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {Object} webhookData - Webhook configuration
     * @returns {Promise<Object>} - Created webhook
     */
    async createWebhook(owner, repo, webhookData) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return null;
            }
        }
        
        try {
            const response = await this._githubApiRequest(`${this.apiUrl}/repositories/${owner}/${repo}/hooks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(webhookData)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to create webhook: ${response.status} ${response.statusText}`);
            }
            
            const webhook = await response.json();
            
            // Add to webhooks collection
            if (!this.webhooks[`${owner}/${repo}`]) {
                this.webhooks[`${owner}/${repo}`] = [];
            }
            this.webhooks[`${owner}/${repo}`].push(webhook);
            
            // Dispatch event for webhook creation
            this.dispatchEvent('webhookCreated', {
                owner,
                repo,
                webhook
            });
            
            return webhook;
        } catch (error) {
            console.error(`Failed to create webhook for ${owner}/${repo}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to create webhook: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Link a repository to a Tekton project
     * @param {string} projectId - Tekton project ID
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @returns {Promise<Object>} - Link details
     */
    async linkRepositoryToProject(projectId, owner, repo) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return null;
            }
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/project-links`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    projectId,
                    owner,
                    repo
                })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to link repository: ${response.status} ${response.statusText}`);
            }
            
            const link = await response.json();
            
            // Add to project links collection
            this.projectLinks.push(link);
            
            // Dispatch event for project link
            this.dispatchEvent('projectLinked', {
                projectId,
                owner,
                repo,
                link
            });
            
            return link;
        } catch (error) {
            console.error(`Failed to link repository ${owner}/${repo} to project ${projectId}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to link repository: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Get linked projects for a repository
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @returns {Promise<Array>} - Linked projects
     */
    async getLinkedProjects(owner, repo) {
        try {
            const response = await fetch(`${this.apiUrl}/repositories/${owner}/${repo}/project-links`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (!response.ok) {
                throw new Error(`Failed to get linked projects: ${response.status} ${response.statusText}`);
            }
            
            const links = await response.json();
            return links;
        } catch (error) {
            console.error(`Failed to get linked projects for ${owner}/${repo}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to get linked projects: ${error.message}` 
            });
            return [];
        }
    }
    
    /**
     * Create a new issue
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {Object} issueData - Issue data
     * @returns {Promise<Object>} - Created issue
     */
    async createIssue(owner, repo, issueData) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return null;
            }
        }
        
        try {
            const response = await this._githubApiRequest(`${this.apiUrl}/repositories/${owner}/${repo}/issues`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(issueData)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to create issue: ${response.status} ${response.statusText}`);
            }
            
            const issue = await response.json();
            
            // Invalidate issues cache
            if (this.cache.issues[`${owner}/${repo}`]) {
                this.cache.issues[`${owner}/${repo}`].timestamp = 0;
            }
            
            // Dispatch event for new issue
            this.dispatchEvent('issueCreated', {
                owner,
                repo,
                issue
            });
            
            return issue;
        } catch (error) {
            console.error(`Failed to create issue in ${owner}/${repo}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to create issue: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Create a pull request
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {Object} prData - Pull request data
     * @returns {Promise<Object>} - Created pull request
     */
    async createPullRequest(owner, repo, prData) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return null;
            }
        }
        
        try {
            const response = await this._githubApiRequest(`${this.apiUrl}/repositories/${owner}/${repo}/pulls`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(prData)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to create pull request: ${response.status} ${response.statusText}`);
            }
            
            const pullRequest = await response.json();
            
            // Invalidate pull requests cache
            if (this.cache.pullRequests[`${owner}/${repo}`]) {
                this.cache.pullRequests[`${owner}/${repo}`].timestamp = 0;
            }
            
            // Dispatch event for new pull request
            this.dispatchEvent('pullRequestCreated', {
                owner,
                repo,
                pullRequest
            });
            
            return pullRequest;
        } catch (error) {
            console.error(`Failed to create pull request in ${owner}/${repo}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to create pull request: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Sync repository with Tekton project
     * @param {string} projectId - Tekton project ID
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @returns {Promise<Object>} - Sync result
     */
    async syncRepositoryWithProject(projectId, owner, repo) {
        try {
            const response = await fetch(`${this.apiUrl}/projects/${projectId}/sync`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    owner,
                    repo
                })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to sync repository: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            
            // Dispatch event for sync completion
            this.dispatchEvent('repositorySynced', {
                projectId,
                owner,
                repo,
                result
            });
            
            return result;
        } catch (error) {
            console.error(`Failed to sync repository ${owner}/${repo} with project ${projectId}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to sync repository: ${error.message}` 
            });
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Get file contents from a repository
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {string} path - File path
     * @param {string} ref - Git reference (branch, tag, commit)
     * @returns {Promise<Object>} - File contents
     */
    async getFileContents(owner, repo, path, ref = 'main') {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return null;
            }
        }
        
        try {
            const url = `${this.apiUrl}/repositories/${owner}/${repo}/contents/${path}?ref=${ref}`;
            const response = await this._githubApiRequest(url);
            
            if (!response.ok) {
                throw new Error(`Failed to get file contents: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Failed to get file contents for ${owner}/${repo}/${path}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to get file contents: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Get repository contents (directory listing)
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {string} path - Directory path
     * @param {string} ref - Git reference (branch, tag, commit)
     * @returns {Promise<Array>} - Directory contents
     */
    async getRepositoryContents(owner, repo, path = '', ref = 'main') {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return [];
            }
        }
        
        try {
            const url = `${this.apiUrl}/repositories/${owner}/${repo}/contents/${path}?ref=${ref}`;
            const response = await this._githubApiRequest(url);
            
            if (!response.ok) {
                throw new Error(`Failed to get repository contents: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Failed to get repository contents for ${owner}/${repo}/${path}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to get repository contents: ${error.message}` 
            });
            return [];
        }
    }
    
    /**
     * Update a file in a repository
     * @param {string} owner - Repository owner
     * @param {string} repo - Repository name
     * @param {string} path - File path
     * @param {string} content - File content (Base64 encoded)
     * @param {string} message - Commit message
     * @param {string} sha - File SHA
     * @param {string} branch - Branch name (default: repository default branch)
     * @returns {Promise<Object>} - Updated file info
     */
    async updateFile(owner, repo, path, content, message, sha, branch = null) {
        if (!this.authenticated) {
            await this.connect();
            if (!this.authenticated) {
                return null;
            }
        }
        
        try {
            const url = `${this.apiUrl}/repositories/${owner}/${repo}/contents/${path}`;
            const data = {
                message,
                content,
                sha
            };
            
            if (branch) {
                data.branch = branch;
            }
            
            const response = await this._githubApiRequest(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to update file: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Failed to update file ${owner}/${repo}/${path}:`, error);
            this.dispatchEvent('error', { 
                error: `Failed to update file: ${error.message}` 
            });
            return null;
        }
    }
    
    /**
     * Helper to make GitHub API requests with auth token
     * @param {string} url - API URL
     * @param {Object} options - Fetch options
     * @returns {Promise<Response>} - Fetch response
     */
    async _githubApiRequest(url, options = {}) {
        // Set up basic options with authentication
        const requestOptions = {
            ...options,
            headers: {
                ...(options.headers || {}),
                'Authorization': `Bearer ${this.authToken}`
            }
        };
        
        // Make the request
        const response = await fetch(url, requestOptions);
        
        // Check for rate limit headers
        this._updateRateLimitInfo(response);
        
        return response;
    }
    
    /**
     * Update rate limit information from response headers
     * @param {Response} response - Fetch response
     */
    _updateRateLimitInfo(response) {
        const limit = response.headers.get('X-RateLimit-Limit');
        const remaining = response.headers.get('X-RateLimit-Remaining');
        const reset = response.headers.get('X-RateLimit-Reset');
        
        if (limit && remaining && reset) {
            this.rateLimit = {
                limit: parseInt(limit, 10),
                remaining: parseInt(remaining, 10),
                resetTime: new Date(parseInt(reset, 10) * 1000)
            };
            
            // Dispatch event for rate limit update
            this.dispatchEvent('rateLimitUpdated', { 
                rateLimit: this.rateLimit 
            });
            
            // Warn if getting close to rate limit
            if (this.rateLimit.remaining < 100) {
                this.dispatchEvent('rateLimitWarning', {
                    remaining: this.rateLimit.remaining,
                    resetTime: this.rateLimit.resetTime
                });
            }
        }
    }
    
    /**
     * Get current authenticated user
     * @returns {Promise<Object>} - User info
     */
    async _getCurrentUser() {
        try {
            const response = await this._githubApiRequest(`${this.apiUrl}/user`);
            
            if (!response.ok) {
                throw new Error(`Failed to get user info: ${response.status} ${response.statusText}`);
            }
            
            this.currentUser = await response.json();
            return this.currentUser;
        } catch (error) {
            console.error('Failed to get user info:', error);
            return null;
        }
    }
    
    /**
     * Load authentication state from storage
     */
    async _loadAuthenticationState() {
        try {
            const authState = localStorage.getItem('github_auth_state');
            
            if (authState) {
                const state = JSON.parse(authState);
                this.authToken = state.token;
                this.enterpriseUrl = state.enterpriseUrl;
            }
        } catch (error) {
            console.error('Failed to load authentication state:', error);
        }
    }
    
    /**
     * Persist authentication state to storage
     */
    _persistAuthState() {
        try {
            if (this.authToken) {
                const state = {
                    token: this.authToken,
                    enterpriseUrl: this.enterpriseUrl
                };
                
                localStorage.setItem('github_auth_state', JSON.stringify(state));
            } else {
                localStorage.removeItem('github_auth_state');
            }
        } catch (error) {
            console.error('Failed to persist authentication state:', error);
        }
    }
    
    /**
     * Load persisted state from storage
     */
    _loadPersistedState() {
        try {
            const persistedState = localStorage.getItem('github_service_state');
            
            if (persistedState) {
                const state = JSON.parse(persistedState);
                
                // Restore settings
                this.cacheTTL = state.cacheTTL || 5 * 60 * 1000;
                this.enterpriseUrl = state.enterpriseUrl || null;
            }
        } catch (error) {
            console.error('Error loading persisted state:', error);
        }
    }
    
    /**
     * Persist state to storage
     */
    _persistState() {
        try {
            // Create state object
            const state = {
                cacheTTL: this.cacheTTL,
                enterpriseUrl: this.enterpriseUrl
            };
            
            // Save to local storage
            localStorage.setItem('github_service_state', JSON.stringify(state));
        } catch (error) {
            console.error('Error persisting state:', error);
        }
    }
    
    /**
     * Clean up resources when service is destroyed
     */
    cleanup() {
        // Persist state
        this._persistState();
    }
}

// Initialize the service when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Create and register the service if not already present
    if (!window.tektonUI?.services?.githubService) {
        // Register it with the tektonUI global namespace
        window.tektonUI = window.tektonUI || {};
        window.tektonUI.services = window.tektonUI.services || {};
        
        // Create the service instance
        const githubService = new GitHubService();
        
        // Register the service
        window.tektonUI.services.githubService = githubService;
        
        console.log('GitHub Service initialized');
    }
});