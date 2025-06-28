/**
 * GitHub Panel Component for Tekton Dashboard
 * Provides GitHub integration functionality including repository management,
 * issue tracking, and project synchronization
 */

console.log('[FILE_TRACE] Loading: github-panel.js');
(function(component) {
    // Component state using State Management Pattern
    if (window.tektonUI.stateManager) {
        component.utils.componentState.connect(component, {
            namespace: 'githubPanel',
            initialState: {
                activeTab: 'repositories',
                authenticated: false,
                currentUser: null,
                repositories: {
                    items: [],
                    loading: false,
                    page: 1,
                    filter: {
                        type: 'all',
                        query: '',
                        language: 'all'
                    }
                },
                issues: {
                    items: {},
                    loading: false,
                    page: 1,
                    filter: {
                        repository: 'all',
                        state: 'open',
                        query: ''
                    }
                },
                pullRequests: {
                    items: {},
                    loading: false,
                    page: 1,
                    filter: {
                        repository: 'all',
                        state: 'open',
                        query: ''
                    }
                },
                projectLinks: {
                    items: [],
                    loading: false
                },
                settings: {
                    enterpriseUrl: '',
                    webhookSecret: '',
                    autoSyncFrequency: 0
                },
                modalState: {
                    repositoryDetail: {
                        isOpen: false,
                        repository: null,
                        activeTab: 'repo-overview'
                    },
                    createRepository: {
                        isOpen: false
                    },
                    createIssue: {
                        isOpen: false
                    },
                    issueDetail: {
                        isOpen: false,
                        issue: null
                    },
                    pullRequestDetail: {
                        isOpen: false,
                        pullRequest: null,
                        activeTab: 'pr-overview'
                    },
                    linkRepository: {
                        isOpen: false,
                        repository: null
                    },
                    cloneRepository: {
                        isOpen: false,
                        repository: null
                    },
                    cloneProgress: {
                        isOpen: false,
                        progress: 0,
                        status: ''
                    },
                    githubAuth: {
                        isOpen: false
                    }
                },
                cloneOperations: {},
                languages: []
            },
            persist: true,
            persistenceType: 'localStorage'
        });
    }

    // Service references
    let githubService = null;
    let tektonService = null;
    
    // Component elements
    const elements = {
        tabs: {},
        panels: {},
        buttons: {},
        modals: {},
        containers: {},
        forms: {}
    };
    
    // Initialize the GitHub panel component
    function init() {
        console.log('Initializing GitHub Panel Component');
        
        // Cache DOM elements
        cacheElements();
        
        // Set up event handlers
        setupEventHandlers();
        
        // Initialize services
        initServices();
        
        // Set up state effects
        setupStateEffects();
        
        // Set up tabs
        setupTabs();
    }
    
    // Cache DOM elements for performance
    function cacheElements() {
        // Cache tab buttons
        const tabButtons = component.$$('.github-tabs .tekton-dashboard__tab-button');
        tabButtons.forEach(btn => {
            const tabId = btn.getAttribute('data-tab');
            elements.tabs[tabId] = btn;
        });
        
        // Cache tab panels
        const tabPanels = component.$$('.github-tab-content .tekton-dashboard__tab-panel');
        tabPanels.forEach(panel => {
            const panelId = panel.getAttribute('data-panel');
            elements.panels[panelId] = panel;
        });
        
        // Cache authentication elements
        elements.authStatus = component.$('#github-auth-status');
        elements.authIndicator = component.$('#github-auth-indicator');
        elements.authLabel = component.$('#github-auth-label');
        elements.authenticateButton = component.$('#github-authenticate');
        elements.refreshButton = component.$('#github-refresh');
        
        // Cache repositories tab elements
        elements.repoSearch = component.$('#repo-search');
        elements.repoTypeFilter = component.$('#repo-type-filter');
        elements.repoLanguageFilter = component.$('#repo-language-filter');
        elements.createRepoButton = component.$('#create-repo-button');
        elements.repositoriesGrid = component.$('#repositories-grid');
        elements.repositoriesLoading = component.$('#repositories-loading');
        elements.repoPrevPage = component.$('#repo-prev-page');
        elements.repoNextPage = component.$('#repo-next-page');
        elements.repoPaginationInfo = component.$('#repo-pagination-info');
        
        // Cache project links tab elements
        elements.createLinkButton = component.$('#create-link-button');
        elements.projectLinksList = component.$('#project-links-list');
        elements.projectLinksLoading = component.$('#project-links-loading');
        elements.syncAllRepos = component.$('#sync-all-repos');
        elements.syncStatus = component.$('#sync-status');
        elements.syncHistoryList = component.$('#sync-history-list');
        
        // Cache issues tab elements
        elements.issuesRepositoryFilter = component.$('#issues-repository-filter');
        elements.issuesStateFilter = component.$('#issues-state-filter');
        elements.issuesSearch = component.$('#issues-search');
        elements.createIssueButton = component.$('#create-issue-button');
        elements.issuesList = component.$('#issues-list');
        elements.issuesLoading = component.$('#issues-loading');
        elements.issuesPrevPage = component.$('#issues-prev-page');
        elements.issuesNextPage = component.$('#issues-next-page');
        elements.issuesPaginationInfo = component.$('#issues-pagination-info');
        
        // Cache pull requests tab elements
        elements.prsRepositoryFilter = component.$('#prs-repository-filter');
        elements.prsStateFilter = component.$('#prs-state-filter');
        elements.prsSearch = component.$('#prs-search');
        elements.createPrButton = component.$('#create-pr-button');
        elements.prsList = component.$('#prs-list');
        elements.prsLoading = component.$('#prs-loading');
        elements.prsPrevPage = component.$('#prs-prev-page');
        elements.prsNextPage = component.$('#prs-next-page');
        elements.prsPaginationInfo = component.$('#prs-pagination-info');
        
        // Cache settings tab elements
        elements.settingsAuthIndicator = component.$('#settings-auth-indicator');
        elements.settingsAuthStatus = component.$('#settings-auth-status');
        elements.settingsAuthButton = component.$('#settings-auth-button');
        elements.settingsLogoutButton = component.$('#settings-logout-button');
        elements.githubUsername = component.$('#github-username');
        elements.githubUserInfo = component.$('#github-user-info');
        elements.githubEnterpriseUrl = component.$('#github-enterprise-url');
        elements.saveEnterpriseSettings = component.$('#save-enterprise-settings');
        elements.autoSyncFrequency = component.$('#auto-sync-frequency');
        elements.webhookSecret = component.$('#webhook-secret');
        elements.generateWebhookSecret = component.$('#generate-webhook-secret');
        elements.saveSyncSettings = component.$('#save-sync-settings');
        
        // Cache modal elements
        cacheModalElements();
        
        // Cache notification container
        elements.notifications = component.$('#github-notifications');
    }
    
    // Cache modal elements
    function cacheModalElements() {
        // Repository Detail Modal
        elements.modals.repositoryDetail = {
            modal: component.$('#repository-detail-modal'),
            title: component.$('#repository-modal-title'),
            overview: component.$('#repo-overview'),
            tabs: component.$$('#repo-detail-tabs .tekton-dashboard__tab-button'),
            panels: component.$$('#repository-detail .tekton-dashboard__tab-panel'),
            closeButton: component.$('#close-repository-modal'),
            cancelButton: component.$('#repository-modal-close'),
            cloneButton: component.$('#repository-clone-button'),
            linkButton: component.$('#repository-link-button'),
            fileBrowser: component.$('#repo-file-browser'),
            filePath: component.$('#repo-file-path'),
            branchSelector: component.$('#repo-branch-selector'),
            commitBranchSelector: component.$('#commit-branch-selector'),
            commitList: component.$('#repo-commit-list'),
            branches: component.$('#repo-branches'),
            issuesList: component.$('#repo-issues-list'),
            issuesStateFilter: component.$('#repo-issues-state-filter'),
            createIssue: component.$('#repo-create-issue'),
            prList: component.$('#repo-pr-list'),
            prsStateFilter: component.$('#repo-prs-state-filter'),
            createPr: component.$('#repo-create-pr')
        };
        
        // Create Repository Modal
        elements.modals.createRepository = {
            modal: component.$('#create-repository-modal'),
            form: component.$('#create-repository-form'),
            nameInput: component.$('#repository-name'),
            nameError: component.$('#repository-name-error'),
            descriptionInput: component.$('#repository-description'),
            visibilityRadios: component.$$('input[name="repository-visibility"]'),
            initCheckbox: component.$('#repository-init'),
            gitignoreSelect: component.$('#repository-gitignore'),
            licenseSelect: component.$('#repository-license'),
            closeButton: component.$('#close-create-repository-modal'),
            cancelButton: component.$('#create-repository-cancel'),
            submitButton: component.$('#create-repository-submit')
        };
        
        // Create Issue Modal
        elements.modals.createIssue = {
            modal: component.$('#create-issue-modal'),
            form: component.$('#create-issue-form'),
            repositorySelect: component.$('#issue-repository'),
            titleInput: component.$('#issue-title'),
            descriptionInput: component.$('#issue-description'),
            labelsInput: component.$('#issue-labels'),
            labelsSelected: component.$('#issue-labels-selected'),
            labelsSuggestions: component.$('#issue-labels-suggestions'),
            assigneesInput: component.$('#issue-assignees'),
            assigneesSelected: component.$('#issue-assignees-selected'),
            assigneesSuggestions: component.$('#issue-assignees-suggestions'),
            closeButton: component.$('#close-create-issue-modal'),
            cancelButton: component.$('#create-issue-cancel'),
            submitButton: component.$('#create-issue-submit')
        };
        
        // Link Repository Modal
        elements.modals.linkRepository = {
            modal: component.$('#link-repository-modal'),
            form: component.$('#link-repository-form'),
            projectSelect: component.$('#link-project'),
            repositorySelect: component.$('#link-repository'),
            syncIssuesCheckbox: component.$('#link-sync-issues'),
            syncPrsCheckbox: component.$('#link-sync-prs'),
            autoSyncCheckbox: component.$('#link-auto-sync'),
            createWebhookCheckbox: component.$('#link-create-webhook'),
            closeButton: component.$('#close-link-repository-modal'),
            cancelButton: component.$('#link-repository-cancel'),
            submitButton: component.$('#link-repository-submit')
        };
        
        // Issue Detail Modal
        elements.modals.issueDetail = {
            modal: component.$('#issue-detail-modal'),
            title: component.$('#issue-modal-title'),
            detail: component.$('#issue-detail'),
            commentsList: component.$('#issue-comments-list'),
            commentInput: component.$('#issue-comment-input'),
            commentSubmit: component.$('#issue-comment-submit'),
            closeButton: component.$('#close-issue-modal'),
            cancelButton: component.$('#issue-modal-close'),
            editButton: component.$('#issue-edit-button'),
            stateToggle: component.$('#issue-state-toggle')
        };
        
        // Pull Request Detail Modal
        elements.modals.pullRequestDetail = {
            modal: component.$('#pr-detail-modal'),
            title: component.$('#pr-modal-title'),
            tabs: component.$$('#pr-detail-tabs .tekton-dashboard__tab-button'),
            panels: component.$$('#pr-detail .tekton-dashboard__tab-panel'),
            overview: component.$('#pr-overview'),
            commentsList: component.$('#pr-comments-list'),
            commentInput: component.$('#pr-comment-input'),
            commentSubmit: component.$('#pr-comment-submit'),
            commitList: component.$('#pr-commit-list'),
            fileChanges: component.$('#pr-file-changes'),
            checksList: component.$('#pr-checks-list'),
            closeButton: component.$('#close-pr-modal'),
            cancelButton: component.$('#pr-modal-close'),
            editButton: component.$('#pr-edit-button'),
            approveButton: component.$('#pr-approve-button'),
            mergeButton: component.$('#pr-merge-button')
        };
        
        // Clone Repository Modal
        elements.modals.cloneRepository = {
            modal: component.$('#clone-repository-modal'),
            form: component.$('#clone-repository-form'),
            repositoryName: component.$('#clone-repository-name'),
            methodRadios: component.$$('input[name="clone-method"]'),
            urlInput: component.$('#clone-url'),
            copyUrlButton: component.$('#copy-clone-url'),
            directoryInput: component.$('#clone-directory'),
            recursiveCheckbox: component.$('#clone-recursive'),
            singleBranchCheckbox: component.$('#clone-single-branch'),
            closeButton: component.$('#close-clone-repository-modal'),
            cancelButton: component.$('#clone-repository-cancel'),
            submitButton: component.$('#clone-repository-submit')
        };
        
        // Clone Progress Modal
        elements.modals.cloneProgress = {
            modal: component.$('#clone-progress-modal'),
            progressBar: component.$('#clone-progress-bar'),
            status: component.$('#clone-progress-status'),
            details: component.$('#clone-progress-details'),
            cancelButton: component.$('#clone-progress-cancel'),
            doneButton: component.$('#clone-progress-done')
        };
        
        // GitHub Authentication Modal
        elements.modals.githubAuth = {
            modal: component.$('#github-auth-modal'),
            instanceRadios: component.$$('input[name="github-instance"]'),
            enterpriseField: component.$('#github-enterprise-field'),
            enterpriseUrl: component.$('#auth-enterprise-url'),
            scopeRepo: component.$('#auth-scope-repo'),
            scopeUser: component.$('#auth-scope-user'),
            scopeWorkflow: component.$('#auth-scope-workflow'),
            closeButton: component.$('#close-github-auth-modal'),
            cancelButton: component.$('#github-auth-cancel'),
            startButton: component.$('#github-auth-start')
        };
    }