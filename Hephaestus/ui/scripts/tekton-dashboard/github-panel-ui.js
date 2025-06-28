/**
 * GitHub Panel UI Functions for Tekton Dashboard
 * Provides UI update functions for the GitHub panel component
 */

console.log('[FILE_TRACE] Loading: github-panel-ui.js');
(function(component) {
    // Make UI functions available on component
    component.ui = component.ui || {};
    component.ui.github = {};
    
    /**
     * Update authentication status display
     * 
     * @param {boolean} authenticated - Whether user is authenticated
     * @param {Object} user - User information if authenticated
     */
    component.ui.github.updateAuthStatus = function(authenticated, user = null) {
        if (!elements) return;
        
        // Get elements
        const authIndicator = elements.authIndicator;
        const authLabel = elements.authLabel;
        const authenticateButton = elements.authenticateButton;
        const refreshButton = elements.refreshButton;
        const settingsAuthIndicator = elements.settingsAuthIndicator;
        const settingsAuthStatus = elements.settingsAuthStatus;
        const settingsAuthButton = elements.settingsAuthButton;
        const settingsLogoutButton = elements.settingsLogoutButton;
        const githubUserInfo = elements.githubUserInfo;
        const githubUsername = elements.githubUsername;
        
        if (authenticated) {
            // Update main auth indicator
            if (authIndicator) {
                authIndicator.className = 'tekton-dashboard__auth-indicator tekton-dashboard__auth-indicator--authenticated';
            }
            
            if (authLabel) {
                authLabel.textContent = user ? `Authenticated as ${user.login}` : 'Authenticated';
            }
            
            if (authenticateButton) {
                authenticateButton.style.display = 'none';
            }
            
            if (refreshButton) {
                refreshButton.style.display = 'inline-flex';
            }
            
            // Update settings auth indicator
            if (settingsAuthIndicator) {
                settingsAuthIndicator.className = 'tekton-dashboard__auth-indicator tekton-dashboard__auth-indicator--authenticated';
            }
            
            if (settingsAuthStatus) {
                settingsAuthStatus.textContent = user ? `Authenticated as ${user.login}` : 'Authenticated';
            }
            
            if (settingsAuthButton) {
                settingsAuthButton.style.display = 'none';
            }
            
            if (settingsLogoutButton) {
                settingsLogoutButton.style.display = 'inline-block';
            }
            
            // Show user info
            if (githubUserInfo) {
                githubUserInfo.style.display = 'block';
            }
            
            if (githubUsername && user) {
                githubUsername.textContent = user.login;
            }
        } else {
            // Update main auth indicator
            if (authIndicator) {
                authIndicator.className = 'tekton-dashboard__auth-indicator tekton-dashboard__auth-indicator--unauthenticated';
            }
            
            if (authLabel) {
                authLabel.textContent = 'Not authenticated';
            }
            
            if (authenticateButton) {
                authenticateButton.style.display = 'inline-flex';
            }
            
            if (refreshButton) {
                refreshButton.style.display = 'none';
            }
            
            // Update settings auth indicator
            if (settingsAuthIndicator) {
                settingsAuthIndicator.className = 'tekton-dashboard__auth-indicator tekton-dashboard__auth-indicator--unauthenticated';
            }
            
            if (settingsAuthStatus) {
                settingsAuthStatus.textContent = 'Not authenticated';
            }
            
            if (settingsAuthButton) {
                settingsAuthButton.style.display = 'inline-block';
            }
            
            if (settingsLogoutButton) {
                settingsLogoutButton.style.display = 'none';
            }
            
            // Hide user info
            if (githubUserInfo) {
                githubUserInfo.style.display = 'none';
            }
        }
    };
    
    /**
     * Render repository cards
     * 
     * @param {Array} repositories - List of repositories
     */
    component.ui.github.renderRepositories = function(repositories) {
        if (!elements || !elements.repositoriesGrid) return;
        
        // Get container
        const container = elements.repositoriesGrid;
        
        // Clear container
        container.innerHTML = '';
        
        // Show message if no repositories
        if (!repositories || repositories.length === 0) {
            container.innerHTML = `
                <div class="tekton-dashboard__empty-state">
                    <div class="tekton-dashboard__empty-icon">📦</div>
                    <div class="tekton-dashboard__empty-title">No repositories found</div>
                    <div class="tekton-dashboard__empty-description">
                        ${component.state.get('repositories.filter.query') ? 
                            'Try changing your search or filter criteria.' :
                            'Authenticate with GitHub to see your repositories or create a new one.'}
                    </div>
                </div>
            `;
            return;
        }
        
        // Create repository cards
        repositories.forEach(repo => {
            const card = document.createElement('div');
            card.className = 'tekton-dashboard__repository-card';
            card.dataset.repo = repo.name;
            card.dataset.owner = repo.owner.login;
            
            const isPrivate = repo.private;
            const updatedAt = new Date(repo.updated_at);
            const updatedDate = updatedAt.toLocaleDateString();
            
            // Format description with fallback
            const description = repo.description ? 
                (repo.description.length > 100 ? repo.description.substring(0, 97) + '...' : repo.description) : 
                'No description provided';
            
            card.innerHTML = `
                <div class="tekton-dashboard__repository-header">
                    <div class="tekton-dashboard__repository-title">
                        <span class="tekton-dashboard__repository-icon">${isPrivate ? '🔒' : '📦'}</span>
                        <span class="tekton-dashboard__repository-name">${repo.name}</span>
                    </div>
                    <div class="tekton-dashboard__repository-visibility ${isPrivate ? 'tekton-dashboard__repository-visibility--private' : ''}">${isPrivate ? 'Private' : 'Public'}</div>
                </div>
                <div class="tekton-dashboard__repository-description">${description}</div>
                <div class="tekton-dashboard__repository-meta">
                    ${repo.language ? `<div class="tekton-dashboard__repository-language">
                        <span class="tekton-dashboard__language-color" style="background-color: ${getLanguageColor(repo.language)}"></span>
                        ${repo.language}
                    </div>` : ''}
                    <div class="tekton-dashboard__repository-stats">
                        <span class="tekton-dashboard__repository-stat">
                            <span class="tekton-dashboard__stat-icon">⭐</span>
                            ${repo.stargazers_count || 0}
                        </span>
                        <span class="tekton-dashboard__repository-stat">
                            <span class="tekton-dashboard__stat-icon">🍴</span>
                            ${repo.forks_count || 0}
                        </span>
                    </div>
                </div>
                <div class="tekton-dashboard__repository-footer">
                    <div class="tekton-dashboard__repository-updated">Updated: ${updatedDate}</div>
                    <div class="tekton-dashboard__repository-actions">
                        <button class="tekton-dashboard__repository-action" data-action="clone" title="Clone Repository">
                            <span class="tekton-dashboard__action-icon">📥</span>
                        </button>
                        <button class="tekton-dashboard__repository-action" data-action="link" title="Link to Project">
                            <span class="tekton-dashboard__action-icon">🔗</span>
                        </button>
                    </div>
                </div>
            `;
            
            // Add event listeners
            const cloneButton = card.querySelector('[data-action="clone"]');
            if (cloneButton) {
                cloneButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    openCloneRepositoryModal(repo);
                });
            }
            
            const linkButton = card.querySelector('[data-action="link"]');
            if (linkButton) {
                linkButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    openLinkRepositoryModal(repo);
                });
            }
            
            // Add click handler for the card itself
            card.addEventListener('click', () => {
                openRepositoryDetailModal(repo);
            });
            
            container.appendChild(card);
        });
    };
    
    /**
     * Update repository pagination controls
     * 
     * @param {number} page - Current page number
     * @param {number} totalPages - Total number of pages
     */
    component.ui.github.updateRepositoryPagination = function(page, totalPages) {
        if (!elements) return;
        
        // Get elements
        const prevButton = elements.repoPrevPage;
        const nextButton = elements.repoNextPage;
        const pageInfo = elements.repoPaginationInfo;
        
        // Update buttons state
        if (prevButton) {
            prevButton.disabled = page <= 1;
        }
        
        if (nextButton) {
            nextButton.disabled = page >= totalPages;
        }
        
        // Update page info
        if (pageInfo) {
            pageInfo.textContent = totalPages > 0 ? `Page ${page} of ${totalPages}` : 'No results';
        }
    };
    
    /**
     * Render project links
     * 
     * @param {Array} links - List of repository-project links
     * @param {Array} projects - List of Tekton projects
     * @param {Array} repositories - List of GitHub repositories
     */
    component.ui.github.renderProjectLinks = function(links, projects, repositories) {
        if (!elements || !elements.projectLinksList) return;
        
        // Get container
        const container = elements.projectLinksList;
        
        // Clear container
        container.innerHTML = '';
        
        // Show message if no links
        if (!links || links.length === 0) {
            container.innerHTML = `
                <div class="tekton-dashboard__empty-state">
                    <div class="tekton-dashboard__empty-icon">🔗</div>
                    <div class="tekton-dashboard__empty-title">No linked repositories</div>
                    <div class="tekton-dashboard__empty-description">
                        Link a GitHub repository to a Tekton project to enable synchronization.
                    </div>
                </div>
            `;
            return;
        }
        
        // Create project link items
        links.forEach(link => {
            // Find associated project and repository
            const project = projects.find(p => p.id === link.projectId);
            const repository = repositories.find(r => 
                r.owner.login === link.owner && r.name === link.repo);
            
            // Skip if project or repository not found
            if (!project || !repository) {
                return;
            }
            
            const item = document.createElement('div');
            item.className = 'tekton-dashboard__project-link-item';
            item.dataset.linkId = link.id;
            
            const lastSyncDate = link.lastSyncTime ? 
                new Date(link.lastSyncTime).toLocaleString() : 'Never';
            
            item.innerHTML = `
                <div class="tekton-dashboard__project-link-header">
                    <div class="tekton-dashboard__project-link-title">
                        <span class="tekton-dashboard__project-icon">📁</span>
                        <span class="tekton-dashboard__project-name">${project.name}</span>
                        <span class="tekton-dashboard__link-icon">🔗</span>
                        <span class="tekton-dashboard__repository-icon">${repository.private ? '🔒' : '📦'}</span>
                        <span class="tekton-dashboard__repository-name">${repository.owner.login}/${repository.name}</span>
                    </div>
                    <div class="tekton-dashboard__project-link-status">
                        <span class="tekton-dashboard__status-indicator ${link.syncEnabled ? 'tekton-dashboard__status-indicator--active' : ''}"></span>
                        ${link.syncEnabled ? 'Auto-sync enabled' : 'Auto-sync disabled'}
                    </div>
                </div>
                <div class="tekton-dashboard__project-link-meta">
                    <div class="tekton-dashboard__project-link-info">
                        <div class="tekton-dashboard__link-detail">
                            <span class="tekton-dashboard__detail-label">Last synchronized:</span>
                            <span class="tekton-dashboard__detail-value">${lastSyncDate}</span>
                        </div>
                        <div class="tekton-dashboard__link-detail">
                            <span class="tekton-dashboard__detail-label">Sync issues:</span>
                            <span class="tekton-dashboard__detail-value">${link.syncIssues ? 'Yes' : 'No'}</span>
                        </div>
                        <div class="tekton-dashboard__link-detail">
                            <span class="tekton-dashboard__detail-label">Sync pull requests:</span>
                            <span class="tekton-dashboard__detail-value">${link.syncPRs ? 'Yes' : 'No'}</span>
                        </div>
                        <div class="tekton-dashboard__link-detail">
                            <span class="tekton-dashboard__detail-label">Webhook:</span>
                            <span class="tekton-dashboard__detail-value">${link.webhookId ? 'Active' : 'Not configured'}</span>
                        </div>
                    </div>
                    <div class="tekton-dashboard__project-link-actions">
                        <button class="tekton-dashboard__button tekton-dashboard__button--secondary" data-action="sync">
                            <span class="tekton-dashboard__button-icon">🔄</span>
                            Sync Now
                        </button>
                        <button class="tekton-dashboard__button" data-action="edit">
                            <span class="tekton-dashboard__button-icon">✏️</span>
                            Edit
                        </button>
                        <button class="tekton-dashboard__button tekton-dashboard__button--danger" data-action="remove">
                            <span class="tekton-dashboard__button-icon">❌</span>
                            Remove
                        </button>
                    </div>
                </div>
            `;
            
            // Add event listeners
            const syncButton = item.querySelector('[data-action="sync"]');
            if (syncButton) {
                syncButton.addEventListener('click', () => {
                    syncRepositoryWithProject(link.projectId, link.owner, link.repo);
                });
            }
            
            const editButton = item.querySelector('[data-action="edit"]');
            if (editButton) {
                editButton.addEventListener('click', () => {
                    openEditLinkModal(link);
                });
            }
            
            const removeButton = item.querySelector('[data-action="remove"]');
            if (removeButton) {
                removeButton.addEventListener('click', () => {
                    confirmRemoveLink(link);
                });
            }
            
            container.appendChild(item);
        });
    };
    
    /**
     * Render sync history
     * 
     * @param {Array} history - Sync history items
     */
    component.ui.github.renderSyncHistory = function(history) {
        if (!elements || !elements.syncHistoryList) return;
        
        // Get container
        const container = elements.syncHistoryList;
        
        // Clear container
        container.innerHTML = '';
        
        // Show message if no history
        if (!history || history.length === 0) {
            container.innerHTML = `
                <div class="tekton-dashboard__empty-state tekton-dashboard__empty-state--small">
                    <div class="tekton-dashboard__empty-description">
                        No synchronization history available.
                    </div>
                </div>
            `;
            return;
        }
        
        // Create history items
        history.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'tekton-dashboard__sync-history-item';
            
            const syncDate = new Date(item.timestamp).toLocaleString();
            const statusClass = item.success ? 
                'tekton-dashboard__sync-status--success' : 
                'tekton-dashboard__sync-status--error';
            
            historyItem.innerHTML = `
                <div class="tekton-dashboard__sync-history-header">
                    <div class="tekton-dashboard__sync-repository">
                        ${item.owner}/${item.repo}
                    </div>
                    <div class="tekton-dashboard__sync-status ${statusClass}">
                        ${item.success ? 'Success' : 'Failed'}
                    </div>
                </div>
                <div class="tekton-dashboard__sync-history-meta">
                    <div class="tekton-dashboard__sync-timestamp">${syncDate}</div>
                    <div class="tekton-dashboard__sync-details">
                        ${item.details || ''}
                    </div>
                </div>
            `;
            
            container.appendChild(historyItem);
        });
    };
    
    /**
     * Render issues list
     * 
     * @param {Array} issues - List of issues
     * @param {Array} repositories - List of repositories
     */
    component.ui.github.renderIssues = function(issues, repositories) {
        if (!elements || !elements.issuesList) return;
        
        // Get container
        const container = elements.issuesList;
        
        // Clear container
        container.innerHTML = '';
        
        // Show message if no issues
        if (!issues || issues.length === 0) {
            container.innerHTML = `
                <div class="tekton-dashboard__empty-state">
                    <div class="tekton-dashboard__empty-icon">🐛</div>
                    <div class="tekton-dashboard__empty-title">No issues found</div>
                    <div class="tekton-dashboard__empty-description">
                        ${component.state.get('issues.filter.query') || component.state.get('issues.filter.repository') !== 'all' ? 
                            'Try changing your search or filter criteria.' :
                            'Create a new issue or link a repository to see its issues.'}
                    </div>
                </div>
            `;
            return;
        }
        
        // Create issue items
        issues.forEach(issue => {
            // Find repository for this issue
            const repoUrl = issue.repository_url;
            const repoUrlParts = repoUrl.split('/');
            const owner = repoUrlParts[repoUrlParts.length - 2];
            const repoName = repoUrlParts[repoUrlParts.length - 1];
            
            const item = document.createElement('div');
            item.className = 'tekton-dashboard__issue-item';
            item.dataset.issueId = issue.id;
            item.dataset.owner = owner;
            item.dataset.repo = repoName;
            
            const createdAt = new Date(issue.created_at);
            const createdDate = createdAt.toLocaleDateString();
            
            const statusClass = issue.state === 'open' ? 
                'tekton-dashboard__issue-status--open' : 
                'tekton-dashboard__issue-status--closed';
            
            item.innerHTML = `
                <div class="tekton-dashboard__issue-header">
                    <div class="tekton-dashboard__issue-status ${statusClass}">
                        <span class="tekton-dashboard__status-icon">${issue.state === 'open' ? '🔴' : '✅'}</span>
                        ${issue.state}
                    </div>
                    <div class="tekton-dashboard__issue-repository">
                        ${owner}/${repoName}
                    </div>
                </div>
                <div class="tekton-dashboard__issue-title">
                    ${issue.title}
                </div>
                <div class="tekton-dashboard__issue-meta">
                    <div class="tekton-dashboard__issue-number">#${issue.number}</div>
                    <div class="tekton-dashboard__issue-created">Created: ${createdDate}</div>
                    ${issue.assignee ? `
                        <div class="tekton-dashboard__issue-assignee">
                            Assigned to: ${issue.assignee.login}
                        </div>
                    ` : ''}
                </div>
                ${issue.labels && issue.labels.length > 0 ? `
                    <div class="tekton-dashboard__issue-labels">
                        ${issue.labels.map(label => `
                            <span class="tekton-dashboard__issue-label" style="background-color: #${label.color}">
                                ${label.name}
                            </span>
                        `).join('')}
                    </div>
                ` : ''}
            `;
            
            // Add click handler
            item.addEventListener('click', () => {
                openIssueDetailModal(issue);
            });
            
            container.appendChild(item);
        });
    };