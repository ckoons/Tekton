/**
 * GitHub Panel Event Handlers for Tekton Dashboard
 * Provides event handling and business logic for the GitHub panel component
 */

(function(component) {
    // Make handler functions available on component
    component.handlers = component.handlers || {};
    component.handlers.github = {};
    
    /**
     * Set up all event handlers
     */
    function setupEventHandlers() {
        // Set up authentication handlers
        setupAuthHandlers();
        
        // Set up repositories tab handlers
        setupRepositoriesTabHandlers();
        
        // Set up project links tab handlers
        setupProjectLinksTabHandlers();
        
        // Set up issues tab handlers
        setupIssuesTabHandlers();
        
        // Set up pull requests tab handlers
        setupPullRequestsTabHandlers();
        
        // Set up settings tab handlers
        setupSettingsTabHandlers();
        
        // Set up modal handlers
        setupModalHandlers();
    }
    
    /**
     * Set up authentication handlers
     */
    function setupAuthHandlers() {
        // Main authenticate button
        if (elements.authenticateButton) {
            elements.authenticateButton.addEventListener('click', openAuthModal);
        }
        
        // Refresh button
        if (elements.refreshButton) {
            elements.refreshButton.addEventListener('click', refreshRepositories);
        }
        
        // Process authentication from URL params (OAuth callback)
        processAuthCallback();
    }
    
    /**
     * Set up repositories tab handlers
     */
    function setupRepositoriesTabHandlers() {
        // Repository search input
        if (elements.repoSearch) {
            elements.repoSearch.addEventListener('input', handleRepositorySearch);
        }
        
        // Repository type filter
        if (elements.repoTypeFilter) {
            elements.repoTypeFilter.addEventListener('change', handleRepositoryTypeFilter);
        }
        
        // Repository language filter
        if (elements.repoLanguageFilter) {
            elements.repoLanguageFilter.addEventListener('change', handleRepositoryLanguageFilter);
        }
        
        // Create repository button
        if (elements.createRepoButton) {
            elements.createRepoButton.addEventListener('click', openCreateRepositoryModal);
        }
        
        // Pagination buttons
        if (elements.repoPrevPage) {
            elements.repoPrevPage.addEventListener('click', () => {
                const currentPage = component.state.get('repositories.page');
                if (currentPage > 1) {
                    component.state.set('repositories.page', currentPage - 1);
                    loadRepositories();
                }
            });
        }
        
        if (elements.repoNextPage) {
            elements.repoNextPage.addEventListener('click', () => {
                component.state.set('repositories.page', component.state.get('repositories.page') + 1);
                loadRepositories();
            });
        }
    }
    
    /**
     * Set up project links tab handlers
     */
    function setupProjectLinksTabHandlers() {
        // Create link button
        if (elements.createLinkButton) {
            elements.createLinkButton.addEventListener('click', openLinkRepositoryModal);
        }
        
        // Sync all repositories button
        if (elements.syncAllRepos) {
            elements.syncAllRepos.addEventListener('click', syncAllRepositories);
        }
    }
    
    /**
     * Set up issues tab handlers
     */
    function setupIssuesTabHandlers() {
        // Issues repository filter
        if (elements.issuesRepositoryFilter) {
            elements.issuesRepositoryFilter.addEventListener('change', handleIssuesRepositoryFilter);
        }
        
        // Issues state filter
        if (elements.issuesStateFilter) {
            elements.issuesStateFilter.addEventListener('change', handleIssuesStateFilter);
        }
        
        // Issues search input
        if (elements.issuesSearch) {
            elements.issuesSearch.addEventListener('input', handleIssuesSearch);
        }
        
        // Create issue button
        if (elements.createIssueButton) {
            elements.createIssueButton.addEventListener('click', openCreateIssueModal);
        }
        
        // Pagination buttons
        if (elements.issuesPrevPage) {
            elements.issuesPrevPage.addEventListener('click', () => {
                const currentPage = component.state.get('issues.page');
                if (currentPage > 1) {
                    component.state.set('issues.page', currentPage - 1);
                    loadIssues();
                }
            });
        }
        
        if (elements.issuesNextPage) {
            elements.issuesNextPage.addEventListener('click', () => {
                component.state.set('issues.page', component.state.get('issues.page') + 1);
                loadIssues();
            });
        }
    }
    
    /**
     * Set up pull requests tab handlers
     */
    function setupPullRequestsTabHandlers() {
        // PRs repository filter
        if (elements.prsRepositoryFilter) {
            elements.prsRepositoryFilter.addEventListener('change', handlePRsRepositoryFilter);
        }
        
        // PRs state filter
        if (elements.prsStateFilter) {
            elements.prsStateFilter.addEventListener('change', handlePRsStateFilter);
        }
        
        // PRs search input
        if (elements.prsSearch) {
            elements.prsSearch.addEventListener('input', handlePRsSearch);
        }
        
        // Create PR button
        if (elements.createPrButton) {
            elements.createPrButton.addEventListener('click', openCreatePRModal);
        }
        
        // Pagination buttons
        if (elements.prsPrevPage) {
            elements.prsPrevPage.addEventListener('click', () => {
                const currentPage = component.state.get('pullRequests.page');
                if (currentPage > 1) {
                    component.state.set('pullRequests.page', currentPage - 1);
                    loadPullRequests();
                }
            });
        }
        
        if (elements.prsNextPage) {
            elements.prsNextPage.addEventListener('click', () => {
                component.state.set('pullRequests.page', component.state.get('pullRequests.page') + 1);
                loadPullRequests();
            });
        }
    }
    
    /**
     * Set up settings tab handlers
     */
    function setupSettingsTabHandlers() {
        // Settings authenticate button
        if (elements.settingsAuthButton) {
            elements.settingsAuthButton.addEventListener('click', openAuthModal);
        }
        
        // Settings logout button
        if (elements.settingsLogoutButton) {
            elements.settingsLogoutButton.addEventListener('click', logout);
        }
        
        // Save enterprise settings button
        if (elements.saveEnterpriseSettings) {
            elements.saveEnterpriseSettings.addEventListener('click', saveEnterpriseSettings);
        }
        
        // Generate webhook secret button
        if (elements.generateWebhookSecret) {
            elements.generateWebhookSecret.addEventListener('click', generateWebhookSecret);
        }
        
        // Save sync settings button
        if (elements.saveSyncSettings) {
            elements.saveSyncSettings.addEventListener('click', saveSyncSettings);
        }
    }
    
    /**
     * Set up modal handlers
     */
    function setupModalHandlers() {
        // Set up repository detail modal handlers
        setupRepositoryDetailModalHandlers();
        
        // Set up create repository modal handlers
        setupCreateRepositoryModalHandlers();
        
        // Set up create issue modal handlers
        setupCreateIssueModalHandlers();
        
        // Set up link repository modal handlers
        setupLinkRepositoryModalHandlers();
        
        // Set up issue detail modal handlers
        setupIssueDetailModalHandlers();
        
        // Set up pull request detail modal handlers
        setupPullRequestDetailModalHandlers();
        
        // Set up clone repository modal handlers
        setupCloneRepositoryModalHandlers();
        
        // Set up clone progress modal handlers
        setupCloneProgressModalHandlers();
        
        // Set up GitHub authentication modal handlers
        setupGitHubAuthModalHandlers();
    }
    
    /**
     * Set up repository detail modal handlers
     */
    function setupRepositoryDetailModalHandlers() {
        const modal = elements.modals.repositoryDetail;
        
        // Close button handler
        if (modal.closeButton) {
            modal.closeButton.addEventListener('click', closeRepositoryDetailModal);
        }
        
        // Cancel button handler
        if (modal.cancelButton) {
            modal.cancelButton.addEventListener('click', closeRepositoryDetailModal);
        }
        
        // Clone button handler
        if (modal.cloneButton) {
            modal.cloneButton.addEventListener('click', () => {
                const repo = component.state.get('modalState.repositoryDetail.repository');
                if (repo) {
                    closeRepositoryDetailModal();
                    openCloneRepositoryModal(repo);
                }
            });
        }
        
        // Link button handler
        if (modal.linkButton) {
            modal.linkButton.addEventListener('click', () => {
                const repo = component.state.get('modalState.repositoryDetail.repository');
                if (repo) {
                    closeRepositoryDetailModal();
                    openLinkRepositoryModal(repo);
                }
            });
        }
        
        // Tab button handlers
        if (modal.tabs) {
            modal.tabs.forEach(tab => {
                tab.addEventListener('click', (e) => {
                    const tabId = e.currentTarget.getAttribute('data-tab');
                    
                    // Update active tab in state
                    component.state.set('modalState.repositoryDetail.activeTab', tabId);
                    
                    // Update active tab UI
                    modal.tabs.forEach(t => t.classList.remove('tekton-dashboard__tab-button--active'));
                    e.currentTarget.classList.add('tekton-dashboard__tab-button--active');
                    
                    // Update active panel UI
                    modal.panels.forEach(panel => {
                        const panelId = panel.getAttribute('data-panel');
                        if (panelId === tabId) {
                            panel.classList.add('tekton-dashboard__tab-panel--active');
                        } else {
                            panel.classList.remove('tekton-dashboard__tab-panel--active');
                        }
                    });
                    
                    // Load tab-specific data
                    loadRepositoryTabData(tabId);
                });
            });
        }
        
        // File browser branch selector handler
        if (modal.branchSelector) {
            modal.branchSelector.addEventListener('change', handleFileBranchChange);
        }
        
        // Commit branch selector handler
        if (modal.commitBranchSelector) {
            modal.commitBranchSelector.addEventListener('change', handleCommitBranchChange);
        }
        
        // Issues state filter handler
        if (modal.issuesStateFilter) {
            modal.issuesStateFilter.addEventListener('change', handleRepoIssuesStateFilter);
        }
        
        // Create issue button handler
        if (modal.createIssue) {
            modal.createIssue.addEventListener('click', () => {
                const repo = component.state.get('modalState.repositoryDetail.repository');
                if (repo) {
                    closeRepositoryDetailModal();
                    openCreateIssueModal(repo);
                }
            });
        }
        
        // PRs state filter handler
        if (modal.prsStateFilter) {
            modal.prsStateFilter.addEventListener('change', handleRepoPRsStateFilter);
        }
        
        // Create PR button handler
        if (modal.createPr) {
            modal.createPr.addEventListener('click', () => {
                const repo = component.state.get('modalState.repositoryDetail.repository');
                if (repo) {
                    closeRepositoryDetailModal();
                    openCreatePRModal(repo);
                }
            });
        }
    }
    
    /**
     * Set up create repository modal handlers
     */
    function setupCreateRepositoryModalHandlers() {
        const modal = elements.modals.createRepository;
        
        // Close button handler
        if (modal.closeButton) {
            modal.closeButton.addEventListener('click', closeCreateRepositoryModal);
        }
        
        // Cancel button handler
        if (modal.cancelButton) {
            modal.cancelButton.addEventListener('click', closeCreateRepositoryModal);
        }
        
        // Submit button handler
        if (modal.submitButton) {
            modal.submitButton.addEventListener('click', handleCreateRepository);
        }
        
        // Form submit handler
        if (modal.form) {
            modal.form.addEventListener('submit', (e) => {
                e.preventDefault();
                handleCreateRepository();
            });
        }
        
        // Name input validation
        if (modal.nameInput) {
            modal.nameInput.addEventListener('input', validateRepositoryName);
        }
    }
    
    /**
     * Set up create issue modal handlers
     */
    function setupCreateIssueModalHandlers() {
        const modal = elements.modals.createIssue;
        
        // Close button handler
        if (modal.closeButton) {
            modal.closeButton.addEventListener('click', closeCreateIssueModal);
        }
        
        // Cancel button handler
        if (modal.cancelButton) {
            modal.cancelButton.addEventListener('click', closeCreateIssueModal);
        }
        
        // Submit button handler
        if (modal.submitButton) {
            modal.submitButton.addEventListener('click', handleCreateIssue);
        }
        
        // Form submit handler
        if (modal.form) {
            modal.form.addEventListener('submit', (e) => {
                e.preventDefault();
                handleCreateIssue();
            });
        }
        
        // Repository select handler
        if (modal.repositorySelect) {
            modal.repositorySelect.addEventListener('change', handleIssueRepositoryChange);
        }
        
        // Labels input handlers
        if (modal.labelsInput) {
            modal.labelsInput.addEventListener('focus', showLabelsSuggestions);
            modal.labelsInput.addEventListener('blur', () => {
                // Delay hiding to allow clicks on suggestions
                setTimeout(hideLabelsSuggestions, 200);
            });
            modal.labelsInput.addEventListener('input', filterLabelsSuggestions);
        }
        
        // Assignees input handlers
        if (modal.assigneesInput) {
            modal.assigneesInput.addEventListener('focus', showAssigneesSuggestions);
            modal.assigneesInput.addEventListener('blur', () => {
                // Delay hiding to allow clicks on suggestions
                setTimeout(hideAssigneesSuggestions, 200);
            });
            modal.assigneesInput.addEventListener('input', filterAssigneesSuggestions);
        }
    }
    
    /**
     * Set up link repository modal handlers
     */
    function setupLinkRepositoryModalHandlers() {
        const modal = elements.modals.linkRepository;
        
        // Close button handler
        if (modal.closeButton) {
            modal.closeButton.addEventListener('click', closeLinkRepositoryModal);
        }
        
        // Cancel button handler
        if (modal.cancelButton) {
            modal.cancelButton.addEventListener('click', closeLinkRepositoryModal);
        }
        
        // Submit button handler
        if (modal.submitButton) {
            modal.submitButton.addEventListener('click', handleLinkRepository);
        }
        
        // Form submit handler
        if (modal.form) {
            modal.form.addEventListener('submit', (e) => {
                e.preventDefault();
                handleLinkRepository();
            });
        }
    }
    
    /**
     * Set up issue detail modal handlers
     */
    function setupIssueDetailModalHandlers() {
        const modal = elements.modals.issueDetail;
        
        // Close button handler
        if (modal.closeButton) {
            modal.closeButton.addEventListener('click', closeIssueDetailModal);
        }
        
        // Cancel button handler
        if (modal.cancelButton) {
            modal.cancelButton.addEventListener('click', closeIssueDetailModal);
        }
        
        // Edit button handler
        if (modal.editButton) {
            modal.editButton.addEventListener('click', () => {
                const issue = component.state.get('modalState.issueDetail.issue');
                if (issue) {
                    closeIssueDetailModal();
                    openEditIssueModal(issue);
                }
            });
        }
        
        // State toggle button handler
        if (modal.stateToggle) {
            modal.stateToggle.addEventListener('click', toggleIssueState);
        }
        
        // Comment submit button handler
        if (modal.commentSubmit) {
            modal.commentSubmit.addEventListener('click', handleAddIssueComment);
        }
    }
    
    /**
     * Set up pull request detail modal handlers
     */
    function setupPullRequestDetailModalHandlers() {
        const modal = elements.modals.pullRequestDetail;
        
        // Close button handler
        if (modal.closeButton) {
            modal.closeButton.addEventListener('click', closePullRequestDetailModal);
        }
        
        // Cancel button handler
        if (modal.cancelButton) {
            modal.cancelButton.addEventListener('click', closePullRequestDetailModal);
        }
        
        // Edit button handler
        if (modal.editButton) {
            modal.editButton.addEventListener('click', () => {
                const pr = component.state.get('modalState.pullRequestDetail.pullRequest');
                if (pr) {
                    closePullRequestDetailModal();
                    openEditPRModal(pr);
                }
            });
        }
        
        // Approve button handler
        if (modal.approveButton) {
            modal.approveButton.addEventListener('click', approvePullRequest);
        }
        
        // Merge button handler
        if (modal.mergeButton) {
            modal.mergeButton.addEventListener('click', mergePullRequest);
        }
        
        // Comment submit button handler
        if (modal.commentSubmit) {
            modal.commentSubmit.addEventListener('click', handleAddPRComment);
        }
        
        // Tab button handlers
        if (modal.tabs) {
            modal.tabs.forEach(tab => {
                tab.addEventListener('click', (e) => {
                    const tabId = e.currentTarget.getAttribute('data-tab');
                    
                    // Update active tab in state
                    component.state.set('modalState.pullRequestDetail.activeTab', tabId);
                    
                    // Update active tab UI
                    modal.tabs.forEach(t => t.classList.remove('tekton-dashboard__tab-button--active'));
                    e.currentTarget.classList.add('tekton-dashboard__tab-button--active');
                    
                    // Update active panel UI
                    modal.panels.forEach(panel => {
                        const panelId = panel.getAttribute('data-panel');
                        if (panelId === tabId) {
                            panel.classList.add('tekton-dashboard__tab-panel--active');
                        } else {
                            panel.classList.remove('tekton-dashboard__tab-panel--active');
                        }
                    });
                    
                    // Load tab-specific data
                    loadPRTabData(tabId);
                });
            });
        }
    }
    
    /**
     * Set up clone repository modal handlers
     */
    function setupCloneRepositoryModalHandlers() {
        const modal = elements.modals.cloneRepository;
        
        // Close button handler
        if (modal.closeButton) {
            modal.closeButton.addEventListener('click', closeCloneRepositoryModal);
        }
        
        // Cancel button handler
        if (modal.cancelButton) {
            modal.cancelButton.addEventListener('click', closeCloneRepositoryModal);
        }
        
        // Submit button handler
        if (modal.submitButton) {
            modal.submitButton.addEventListener('click', handleCloneRepository);
        }
        
        // Form submit handler
        if (modal.form) {
            modal.form.addEventListener('submit', (e) => {
                e.preventDefault();
                handleCloneRepository();
            });
        }
        
        // Clone method radio handlers
        if (modal.methodRadios) {
            modal.methodRadios.forEach(radio => {
                radio.addEventListener('change', updateCloneUrl);
            });
        }
        
        // Copy URL button handler
        if (modal.copyUrlButton) {
            modal.copyUrlButton.addEventListener('click', copyCloneUrl);
        }
    }
    
    /**
     * Set up clone progress modal handlers
     */
    function setupCloneProgressModalHandlers() {
        const modal = elements.modals.cloneProgress;
        
        // Cancel button handler
        if (modal.cancelButton) {
            modal.cancelButton.addEventListener('click', cancelCloneOperation);
        }
        
        // Done button handler
        if (modal.doneButton) {
            modal.doneButton.addEventListener('click', closeCloneProgressModal);
        }
    }
    
    /**
     * Set up GitHub authentication modal handlers
     */
    function setupGitHubAuthModalHandlers() {
        const modal = elements.modals.githubAuth;
        
        // Close button handler
        if (modal.closeButton) {
            modal.closeButton.addEventListener('click', closeGitHubAuthModal);
        }
        
        // Cancel button handler
        if (modal.cancelButton) {
            modal.cancelButton.addEventListener('click', closeGitHubAuthModal);
        }
        
        // Start button handler
        if (modal.startButton) {
            modal.startButton.addEventListener('click', startGitHubAuth);
        }
        
        // GitHub instance radio handlers
        if (modal.instanceRadios) {
            modal.instanceRadios.forEach(radio => {
                radio.addEventListener('change', (e) => {
                    const isEnterprise = e.target.value === 'enterprise';
                    if (modal.enterpriseField) {
                        modal.enterpriseField.style.display = isEnterprise ? 'block' : 'none';
                    }
                });
            });
        }
    }
    
    /**
     * Process GitHub OAuth callback parameters
     */
    function processAuthCallback() {
        // Check for code and state parameters in URL
        const params = new URLSearchParams(window.location.search);
        const code = params.get('code');
        const state = params.get('state');
        
        if (code && state) {
            // Show loading indicator
            showLoading('Completing GitHub authentication...');
            
            // Complete OAuth authentication
            if (githubService) {
                githubService.handleOAuthCallback(code, state)
                    .then(success => {
                        if (success) {
                            showNotification('Authentication successful', 'You are now authenticated with GitHub.', 'success');
                            loadRepositories();
                        } else {
                            showNotification('Authentication failed', 'Failed to complete GitHub authentication.', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('OAuth callback error:', error);
                        showNotification('Authentication failed', `Failed to complete GitHub authentication: ${error.message}`, 'error');
                    })
                    .finally(() => {
                        hideLoading();
                        
                        // Clean up URL
                        const url = new URL(window.location);
                        url.searchParams.delete('code');
                        url.searchParams.delete('state');
                        window.history.replaceState({}, '', url);
                    });
            }
        }
    }
    
    // Export setupEventHandlers to component
    component.handlers.github.setupEventHandlers = setupEventHandlers;
})(component);