/**
 * Athena Component
 * Knowledge graph and entity management interface
 */

class AthenaComponent {
    constructor() {
        this.state = {
            initialized: false,
            activeTab: 'graph', // Default tab is Knowledge Graph
            graphLoaded: false,
            entitiesLoaded: false
        };
    }
    
    /**
     * Initialize the component
     */
    init() {
        console.log('Initializing Athena component');
        
        // If already initialized, just activate
        if (this.state.initialized) {
            console.log('Athena component already initialized, just activating');
            this.activateComponent();
            return this;
        }
        
        // Check SHOW_GREEK_NAMES environment variable
        this.checkGreekNamesVisibility();
        
        // Initialize component functionality
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
        
        // Add a class to our container
        const athenaContainer = document.querySelector('.athena');
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
        
        // Find our component container
        const athenaContainer = document.querySelector('.athena');
        if (athenaContainer) {
            console.log('Athena container found and activated');
        }
    }
    
    /**
     * Set up tab switching functionality
     */
    setupTabs() {
        console.log('Setting up Athena tabs');
        
        // Find Athena container
        const container = document.querySelector('.athena');
        if (!container) {
            console.error('Athena container not found!');
            return;
        }
        
        // Scope all queries to our container
        const tabs = container.querySelectorAll('.athena__tab');
        const panels = container.querySelectorAll('.athena__panel');
        const chatInput = container.querySelector('.athena__chat-input');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update active tab
                tabs.forEach(t => t.classList.remove('athena__tab--active'));
                tab.classList.add('athena__tab--active');
                
                // Show active panel
                const panelId = tab.getAttribute('data-tab') + '-panel';
                panels.forEach(panel => {
                    panel.style.display = 'none';
                    panel.classList.remove('athena__panel--active');
                });
                
                // Use container-scoped query instead of global getElementById
                const activePanel = container.querySelector(`#${panelId}`);
                if (activePanel) {
                    activePanel.style.display = 'block';
                    activePanel.classList.add('athena__panel--active');
                }
                
                // Show/hide the clear chat button in the menu bar based on active tab
                // Use container-scoped query
                const clearChatBtn = container.querySelector('#clear-chat-btn');
                if (clearChatBtn) {
                    const panelType = tab.getAttribute('data-tab');
                    clearChatBtn.style.display = (panelType === 'chat' || panelType === 'teamchat') ? 'block' : 'none';
                }
                
                // Update the active tab in state
                this.state.activeTab = tab.getAttribute('data-tab');
                
                // Update chat input placeholder based on active tab
                this.updateChatPlaceholder(this.state.activeTab);
                
                // Load tab-specific content if needed
                this.loadTabContent(this.state.activeTab);
            });
        });
        
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
        // Find Athena container
        const container = document.querySelector('.athena');
        if (!container) return;
        
        // Get the chat input within our container
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
                // Initialize query panel if needed
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
     * Initialize the graph visualization
     */
    initializeGraph() {
        console.log('Initializing knowledge graph visualization');
        
        // Find Athena container
        const container = document.querySelector('.athena');
        if (!container) return;
        
        // Get the graph placeholder within our container
        const placeholder = container.querySelector('#graph-placeholder');
        if (placeholder) {
            placeholder.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <h2 style="color: #999; margin-bottom: 1rem;">Knowledge Graph View</h2>
                    <p style="color: #777; max-width: 600px; margin: 0 auto;">
                        This is a placeholder for the knowledge graph visualization.
                        In a real implementation, this would show an interactive graph of entities and relationships.
                    </p>
                </div>
            `;
        }
    }
    
    /**
     * Load entities for the entity list
     */
    loadEntities() {
        console.log('Loading entities');
        
        // Find Athena container
        const container = document.querySelector('.athena');
        if (!container) return;
        
        // Get the entity list and loading indicator within our container
        const entityList = container.querySelector('#entity-list-items');
        const loading = container.querySelector('#entity-list-loading');
        
        if (entityList && loading) {
            // Show some sample entities after a delay
            setTimeout(() => {
                loading.style.display = 'none';
                entityList.style.display = 'block';
            }, 1000);
        }
    }
    
    /**
     * Set up chat functionality
     */
    setupChat() {
        console.log('Setting up Athena chat');
        
        // Find Athena container
        const container = document.querySelector('.athena');
        if (!container) return;
        
        // Get the chat input and send button within our container
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
        // Find Athena container
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
            // Keep only the welcome message
            const welcomeMessage = messagesContainer.querySelector('.athena__message--system');
            messagesContainer.innerHTML = '';
            if (welcomeMessage) {
                messagesContainer.appendChild(welcomeMessage);
            }
        }
    }
    
    /**
     * Clean up resources used by this component
     */
    cleanup() {
        console.log('Cleaning up Athena component');
        
        // Find Athena container
        const container = document.querySelector('.athena');
        if (!container) return;
        
        // Clean up event listeners if needed
        // (In a full implementation, you'd want to properly remove event listeners here)
    }
}

// Create global instance
window.athenaComponent = new AthenaComponent();

// Initialize the component when the script loads
window.athenaComponent.init();