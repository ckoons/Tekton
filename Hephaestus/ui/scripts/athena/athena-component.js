/**
 * Athena Component
 * Knowledge graph and entity management interface
 */

console.log('[FILE_TRACE] Loading: athena-component.js');
class AthenaComponent {
    constructor() {
        this.state = {
            initialized: false,
            activeTab: 'graph', // Default tab is now Knowledge Graph
            graphLoaded: false,
            entitiesLoaded: false,
            queryBuilderLoaded: false
        };
    }
    
    /**
     * Initialize the component
     */
    init() {
        console.log('Initializing Athena component');
        if (window.TektonDebug) TektonDebug.info('athenaComponent', 'Initializing Athena component');

        // If already initialized, just activate
        if (this.state.initialized) {
            console.log('Athena component already initialized, just activating');
            if (window.TektonDebug) TektonDebug.debug('athenaComponent', 'Already initialized, just activating');
            this.activateComponent();
            return this;
        }

        // Check SHOW_GREEK_NAMES environment variable
        this.checkGreekNamesVisibility();

        // HTML panel is already active and displayed by the component loader
        // We don't need to manipulate it here

        // Initialize component functionality
        // The HTML is already loaded by the component loader
        this.setupTabs();
        this.setupChat();

        // Mark as initialized
        this.state.initialized = true;

        console.log('Athena component initialized');
        return this;
    }
    
    /**
     * Check if SHOW_GREEK_NAMES environment variable is set
     */
    checkGreekNamesVisibility() {
        // Check if the environment variable is available and set to true
        const showGreekNames = window.env && window.env.SHOW_GREEK_NAMES === 'true';

        // Instead of modifying document.body, add a class to our container
        const athenaContainer = document.querySelector('.athena-container');
        if (athenaContainer) {
            if (showGreekNames) {
                athenaContainer.setAttribute('data-show-greek-names', 'true');
            } else {
                athenaContainer.removeAttribute('data-show-greek-names');
            }
        }

        console.log(`Greek names visibility: ${showGreekNames ? 'visible' : 'hidden'}`);
    }

    /**
     * Activate the component interface
     */
    activateComponent() {
        console.log('Activating Athena component');

        // We no longer need to manipulate the panels or global DOM
        // Our component loader handles this for us

        // Find our component container
        const athenaContainer = document.querySelector('.athena-container');
        if (athenaContainer) {
            // We don't need to set dimensions because the container
            // already has width and height set to 100% in the CSS
            console.log('Athena container found and activated');
        }

        // We don't need to update the status indicator
        // The component loader handles this for us
    }
    
    /**
     * Load the component HTML
     *
     * Note: This method is no longer used with the new component loader.
     * It's retained for backward compatibility but doesn't do anything.
     * The Component Loader now handles loading the HTML.
     */
    async loadComponentHTML() {
        console.log('Legacy loadComponentHTML called - this is handled by the component loader now');

        // Setup component functionality directly
        // The HTML is already loaded by the component loader
        this.setupTabs();
        this.setupClearButton();
        this.setupChat();

        console.log('Athena component functionality initialized');
    }
    
    /**
     * Set up tab switching functionality - THIS METHOD IS DELIBERATELY DISABLED
     * The actual tab switching is handled by the HTML component script directly
     */
    setupTabs() {
        console.log('Athena tab handling now managed by HTML script');
        if (window.TektonDebug) TektonDebug.debug('athenaComponent', 'Athena tab handling now managed by HTML script');

        // Let the HTML-based tab activator handle all the tab switching
        // We'll just update placeholders and load content when needed
        
        // Set initial state to default tab
        this.state.activeTab = 'graph';
        
        // Trigger content loading for default tab
        this.loadTabContent('graph');
        
        // No DOM manipulation here - it's all handled by the HTML script
    }
    
    /**
     * Set up clear chat button and other UI elements
     * This method is called after setupTabs
     */
    setupClearButton() {
        // Find Athena container with BEM naming
        const container = document.querySelector('.athena');
        if (!container) {
            console.error('Athena container not found!');
            return;
        }
        
        // Set up clear chat button - use container-scoped query
        const clearChatBtn = container.querySelector('#clear-chat-btn');
        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', () => this.clearActiveChat());
        }

        // Initial placeholder update
        this.updateChatPlaceholder(this.state.activeTab);
    }
    
    /**
     * Update chat input placeholder based on active tab
     * @param {string} activeTab - The currently active tab
     */
    updateChatPlaceholder(activeTab) {
        // Find Athena container with BEM naming
        const container = document.querySelector('.athena');
        if (!container) return;

        // Get the chat input within our container with BEM class
        const chatInput = container.querySelector('.athena__chat-input');
        if (!chatInput) return;

        switch(activeTab) {
            case 'graph':
                chatInput.placeholder = "Ask about the knowledge graph visualization or search for connections...";
                break;
            case 'entities':
                chatInput.placeholder = "Ask about entities or search for specific information...";
                break;
            case 'query':
                chatInput.placeholder = "Ask about creating queries or interpreting results...";
                break;
            case 'chat':
                chatInput.placeholder = "Enter chat message for Athena knowledge graph queries, entities or information";
                break;
            case 'teamchat':
                chatInput.placeholder = "Enter team chat message for all Tekton components";
                break;
            default:
                chatInput.placeholder = "Enter message...";
        }
    }
    
    /**
     * Load content specific to a tab
     * @param {string} tabId - The ID of the tab to load content for
     */
    loadTabContent(tabId) {
        console.log(`Loading content for ${tabId} tab`);

        switch (tabId) {
            case 'graph':
                if (!this.state.graphLoaded) {
                    this.initializeGraph();
                    this.state.graphLoaded = true;
                }
                break;
            case 'entities':
                if (!this.state.entitiesLoaded) {
                    this.loadEntities();
                    this.state.entitiesLoaded = true;
                }
                break;
            case 'query':
                if (!this.state.queryBuilderLoaded) {
                    this.setupQueryBuilder();
                    this.state.queryBuilderLoaded = true;
                }
                break;
            case 'chat':
                // Chat is loaded by setupChat
                break;
            case 'teamchat':
                // Team chat is loaded by setupChat
                break;
        }
    }

    /**
     * Set up the query builder functionality
     */
    setupQueryBuilder() {
        console.log('Setting up Query Builder');

        // Find Athena container
        const container = document.querySelector('.athena');
        if (!container) return;

        // Get query builder elements
        const buildQueryBtn = container.querySelector('#build-query-btn');
        const clearQueryBtn = container.querySelector('#clear-query-btn');
        const entityTypeSelect = container.querySelector('#entity-type-select');
        const relationshipTypeSelect = container.querySelector('#relationship-type-select');
        const searchTermsInput = container.querySelector('#search-terms-input');
        const includeArchivedCheckbox = container.querySelector('#include-archived');
        const exactMatchCheckbox = container.querySelector('#exact-match');
        const queryResultContainer = container.querySelector('#query-result-container');
        const generatedQueryElem = container.querySelector('#generated-query');
        const copyQueryBtn = container.querySelector('#copy-query-btn');
        const executeQueryBtn = container.querySelector('#execute-query-btn');

        if (!buildQueryBtn || !clearQueryBtn) {
            console.error('Query builder buttons not found');
            return;
        }

        // Build Query button handler
        buildQueryBtn.addEventListener('click', () => {
            const entityType = entityTypeSelect.value;
            const relationshipType = relationshipTypeSelect.value;
            const searchTerms = searchTermsInput.value.trim();
            const includeArchived = includeArchivedCheckbox.checked;
            const exactMatch = exactMatchCheckbox.checked;

            // Generate query string
            let query = 'MATCH ';

            if (entityType !== 'any') {
                query += `(n:${entityType.charAt(0).toUpperCase() + entityType.slice(1)})`;
            } else {
                query += '(n)';
            }

            if (relationshipType !== 'any') {
                query += `-[r:${relationshipType.toUpperCase()}]->(m)`;
            } else {
                query += '-[r]->(m)';
            }

            query += '\nWHERE ';

            if (searchTerms) {
                if (exactMatch) {
                    query += `n.name = "${searchTerms}" OR m.name = "${searchTerms}"`;
                } else {
                    query += `n.name CONTAINS "${searchTerms}" OR m.name CONTAINS "${searchTerms}"`;
                }
            } else {
                query += 'true';
            }

            if (!includeArchived) {
                query += ' AND NOT n.archived AND NOT m.archived';
            }

            query += '\nRETURN n, r, m\nLIMIT 100;';

            // Show the query result container
            queryResultContainer.style.display = 'block';
            generatedQueryElem.textContent = query;

            // Scroll to show the generated query
            queryResultContainer.scrollIntoView({ behavior: 'smooth' });
        });

        // Clear Query button handler
        clearQueryBtn.addEventListener('click', () => {
            entityTypeSelect.value = 'any';
            relationshipTypeSelect.value = 'any';
            searchTermsInput.value = '';
            includeArchivedCheckbox.checked = false;
            exactMatchCheckbox.checked = false;

            queryResultContainer.style.display = 'none';
        });

        // Copy Query button handler
        if (copyQueryBtn) {
            copyQueryBtn.addEventListener('click', () => {
                if (generatedQueryElem) {
                    const textToCopy = generatedQueryElem.textContent;

                    // Use the clipboard API if available
                    if (navigator.clipboard) {
                        navigator.clipboard.writeText(textToCopy)
                            .then(() => {
                                copyQueryBtn.textContent = 'Copied!';
                                setTimeout(() => {
                                    copyQueryBtn.textContent = 'Copy Query';
                                }, 2000);
                            })
                            .catch(err => {
                                console.error('Error copying text: ', err);
                            });
                    } else {
                        // Fallback for browsers without clipboard API
                        const textarea = document.createElement('textarea');
                        textarea.value = textToCopy;
                        textarea.style.position = 'fixed'; // Avoid scrolling to bottom
                        document.body.appendChild(textarea);
                        textarea.focus();
                        textarea.select();

                        try {
                            document.execCommand('copy');
                            copyQueryBtn.textContent = 'Copied!';
                            setTimeout(() => {
                                copyQueryBtn.textContent = 'Copy Query';
                            }, 2000);
                        } catch (err) {
                            console.error('Error copying text: ', err);
                        }

                        document.body.removeChild(textarea);
                    }
                }
            });
        }

        // Execute Query button handler
        if (executeQueryBtn) {
            executeQueryBtn.addEventListener('click', () => {
                // Simulate query execution
                const queryText = generatedQueryElem.textContent;

                // Add a message to the chat
                this.state.activeTab = 'chat'; // Switch to chat tab

                // Get the chat panel and make it active
                const chatPanel = container.querySelector('#chat-panel');
                const queryPanel = container.querySelector('#query-panel');
                if (chatPanel && queryPanel) {
                    queryPanel.style.display = 'none';
                    queryPanel.classList.remove('athena__panel--active');
                    chatPanel.style.display = 'block';
                    chatPanel.classList.add('athena__panel--active');

                    // Update active tab in nav
                    const tabs = container.querySelectorAll('.athena__tab');
                    tabs.forEach(tab => {
                        if (tab.getAttribute('data-tab') === 'chat') {
                            tab.classList.add('athena__tab--active');
                        } else {
                            tab.classList.remove('athena__tab--active');
                        }
                    });
                }

                // Add a user message
                const chatMessages = container.querySelector('#chat-messages');
                if (chatMessages) {
                    this.addUserMessageToChatUI(chatMessages, `Execute query: ${queryText}`);

                    // Simulate AI response
                    setTimeout(() => {
                        const response = 'The query was executed successfully. Found 15 matching relationships. Here are the results...';
                        this.addAIMessageToChatUI(chatMessages, response);
                    }, 1500);
                }
            });
        }
    }
    
    /**
     * Initialize the graph visualization
     */
    async initializeGraph() {
        console.log('Initializing knowledge graph visualization');
        
        const placeholder = document.getElementById('graph-placeholder');
        if (!placeholder) return;
        
        // Check if AthenaService is available
        if (window.AthenaService) {
            try {
                // Try to load actual data from Athena
                const entities = await window.AthenaService.getEntities();
                console.log('Loaded Athena entities:', entities);
                
                placeholder.innerHTML = `
                    <div style="text-align: center; padding: 2rem;">
                        <h2 style="color: #999; margin-bottom: 1rem;">Knowledge Graph Loaded</h2>
                        <p style="color: #777; max-width: 600px; margin: 0 auto;">
                            Successfully loaded ${entities.length} entities from Athena.<br><br>
                            • Components: ${entities.filter(e => e.entityType === 'component').length}<br>
                            • Integration patterns discovered<br>
                            • Knowledge graph ready<br><br>
                            Use the Entities tab to browse all components and relationships.
                        </p>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading Athena data:', error);
                placeholder.innerHTML = `
                    <div style="text-align: center; padding: 2rem;">
                        <h2 style="color: #999; margin-bottom: 1rem;">Knowledge Graph</h2>
                        <p style="color: #777; max-width: 600px; margin: 0 auto;">
                            Unable to connect to Athena service. Please ensure Athena is running on port 8002.<br><br>
                            Error: ${error.message}
                        </p>
                    </div>
                `;
            }
        } else {
            // AthenaService not available
            placeholder.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <h2 style="color: #999; margin-bottom: 1rem;">Knowledge Graph</h2>
                    <p style="color: #777; max-width: 600px; margin: 0 auto;">
                        AthenaService not loaded. The graph visualization will be available once all scripts load properly.
                    </p>
                </div>
            `;
        }
    }
    
    /**
     * Load entities for the entity list
     */
    async loadEntities() {
        console.log('Loading entities');
        
        const entityList = document.getElementById('entity-list-items');
        
        if (!entityList) return;
        
        if (window.AthenaService) {
            try {
                // Load actual entities from Athena
                const entities = await window.AthenaService.getEntities();
                console.log('Loaded entities for list:', entities);
                
                // Clear the loading message and populate with entities
                if (entities.length > 0) {
                    entityList.innerHTML = entities.map(entity => `
                        <div class="athena__entity-item" data-entity-id="${entity.id}">
                            <div class="athena__entity-header">
                                <h4 class="athena__entity-name">${entity.name}</h4>
                                <span class="athena__entity-type">${entity.entityType}</span>
                            </div>
                            <div class="athena__entity-details">
                                <p>${entity.properties?.description || 'No description available'}</p>
                                ${entity.properties?.port ? `<small>Port: ${entity.properties.port}</small>` : ''}
                            </div>
                        </div>
                    `).join('');
                } else {
                    entityList.innerHTML = `
                        <div class="athena__empty-state">
                            <p>No entities found. Run the population script to add Tekton components.</p>
                        </div>
                    `;
                }
                
                entityList.style.display = 'block';
            } catch (error) {
                console.error('Error loading entities:', error);
                entityList.innerHTML = `
                    <div class="athena__error-state">
                        <p>Error loading entities: ${error.message}</p>
                        <p>Please ensure Athena is running and accessible.</p>
                    </div>
                `;
                entityList.style.display = 'block';
            }
        } else {
            // Fallback when AthenaService is not available
            setTimeout(() => {
                entityList.innerHTML = `
                    <div class="athena__error-state">
                        <p>AthenaService not available. Please check console for script loading errors.</p>
                    </div>
                `;
                entityList.style.display = 'block';
            }, 1000);
        }
    }
    
    /**
     * Set up chat functionality
     */
    setupChat() {
        console.log('Setting up Athena chat');

        // Find Athena container with BEM naming
        const container = document.querySelector('.athena');
        if (!container) {
            console.error('Athena container not found!');
            return;
        }

        // Use scoped queries with container
        const input = container.querySelector('#chat-input');
        const button = container.querySelector('#send-button');

        if (!input || !button) {
            console.error('Missing chat input elements');
            return;
        }

        // Send message on button click
        button.addEventListener('click', () => {
            const message = input.value.trim();
            if (!message) return;

            // Determine which chat container to use based on active tab
            let messagesContainer;
            let responsePrefix = '';

            if (this.state.activeTab === 'teamchat') {
                messagesContainer = container.querySelector('#teamchat-messages');
                responsePrefix = 'Team Chat: ';
            } else {
                // Default to knowledge chat for all other tabs
                messagesContainer = container.querySelector('#chat-messages');
                responsePrefix = 'Knowledge: ';
            }

            if (!messagesContainer) {
                console.error('Chat messages container not found');
                return;
            }

            // Add user message to chat
            this.addUserMessageToChatUI(messagesContainer, message);

            // Simulate a response based on the active tab
            setTimeout(() => {
                let response;

                if (this.state.activeTab === 'teamchat') {
                    response = `${responsePrefix}I received your team message: "${message}". This would be shared with all Tekton components.`;
                } else if (this.state.activeTab === 'graph') {
                    response = `${responsePrefix}I received your query about the knowledge graph: "${message}". I can help visualize connections.`;
                } else if (this.state.activeTab === 'entities') {
                    response = `${responsePrefix}I received your entity query: "${message}". I can help find entity information.`;
                } else if (this.state.activeTab === 'query') {
                    response = `${responsePrefix}I received your query builder request: "${message}". I can help construct complex queries.`;
                } else {
                    response = `${responsePrefix}I received your message: "${message}". This is a response from Athena Knowledge system.`;
                }

                this.addAIMessageToChatUI(messagesContainer, response);
            }, 1000);

            // Clear input
            input.value = '';
        });

        // Send message on Enter key (but allow Shift+Enter for new lines)
        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                button.click();
            }
        });
    }
    
    /**
     * Add a user message to the chat UI
     * @param {HTMLElement} messages - The messages container element
     * @param {string} message - The message text
     */
    addUserMessageToChatUI(messages, message) {
        if (!messages) return;

        const userBubble = document.createElement('div');
        userBubble.className = 'athena__message athena__message--user';
        userBubble.textContent = message;
        messages.appendChild(userBubble);
        messages.scrollTop = messages.scrollHeight;
    }

    /**
     * Add an AI message to the chat UI
     * @param {HTMLElement} messages - The messages container element
     * @param {string} message - The message text
     */
    addAIMessageToChatUI(messages, message) {
        if (!messages) return;

        const aiBubble = document.createElement('div');
        aiBubble.className = 'athena__message athena__message--ai';
        aiBubble.textContent = message;
        messages.appendChild(aiBubble);
        messages.scrollTop = messages.scrollHeight;
    }
    
    /**
     * Clear the active chat messages
     */
    clearActiveChat() {
        // Find Athena container with BEM naming
        const container = document.querySelector('.athena');
        if (!container) return;

        let messagesContainer;

        // Determine which chat is active
        if (this.state.activeTab === 'chat') {
            messagesContainer = container.querySelector('#chat-messages');
        } else if (this.state.activeTab === 'teamchat') {
            messagesContainer = container.querySelector('#teamchat-messages');
        }

        if (messagesContainer) {
            // Keep only the welcome message (system message with BEM class)
            const welcomeMessage = messagesContainer.querySelector('.athena__message--system');
            messagesContainer.innerHTML = '';
            if (welcomeMessage) {
                messagesContainer.appendChild(welcomeMessage);
            }
        }
    }
}

// Create global instance
window.athenaComponent = new AthenaComponent();

// Add handler to component activation
document.addEventListener('DOMContentLoaded', function() {
    const athenaTab = document.querySelector('.nav-item[data-component="athena"]');
    if (athenaTab) {
        athenaTab.addEventListener('click', function() {
            // First, make sure the HTML panel is visible
            const htmlPanel = document.getElementById('html-panel');
            if (htmlPanel) {
                // Make it active and visible
                const panels = document.querySelectorAll('.panel');
                panels.forEach(panel => {
                    panel.classList.remove('active');
                    panel.style.display = 'none';
                });
                htmlPanel.classList.add('active');
                htmlPanel.style.display = 'block';
            }
            
            // Initialize component if not already done
            if (window.athenaComponent) {
                window.athenaComponent.init();
            }
        });
    }
});