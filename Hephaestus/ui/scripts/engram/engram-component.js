/**
 * Engram Component
 * 
 * Provides a UI for interacting with the Engram memory system and LLM chat capabilities.
 * Implements memory search, chat interface, and analytics.
 */

console.log('[FILE_TRACE] Loading: engram-component.js');
(function(component) {
    'use strict';
    
    // Component-specific utilities
    const dom = component.utils.dom;
    const notifications = component.utils.notifications;
    const loading = component.utils.loading;
    const lifecycle = component.utils.lifecycle;
    
    // Service references
    let engramService = null;
    let engramLLMService = null;
    
    // Initialize state
    const initialState = {
        // UI State
        activeTab: 'memory',
        isModalOpen: false,
        modalContent: null,
        
        // Memory State
        memoryNamespace: 'conversations',
        memorySearch: '',
        memories: [],
        
        // Chat State
        chat: {
            isTyping: false,
            selectedModel: 'claude-3-haiku-20240307',
            useMemoryContext: true,
            useStreaming: true,
            conversations: []
        },
        
        // Structured Memory State
        structuredCategory: 'all',
        structuredSearch: '',
        structuredMemories: [],
        
        // Analytics State
        analyticsType: 'usage',
        analytics: null
    };
    
    /**
     * Initialize the Engram component
     */
    function initEngramComponent() {
        console.log('Initializing Engram component...');
        
        // Connect component to state system
        component.utils.componentState.utils.connect(component, {
            namespace: 'engram',
            initialState: initialState,
            persist: true, // Persist state between sessions
            persistenceType: 'localStorage',
            excludeFromPersistence: ['memories', 'isModalOpen', 'modalContent', 'analytics'] // Don't persist ephemeral data
        });
        
        // Initialize Engram services
        initEngramServices();
        
        // Set up UI event handlers
        setupEventHandlers();
        
        // Set up state effects
        setupStateEffects();
        
        // Register cleanup function
        component.registerCleanup(cleanupComponent);
        
        console.log('Engram component initialized');
    }
    
    /**
     * Initialize or get the Engram and LLM services
     */
    function initEngramServices() {
        // Check if LLM service already exists globally
        if (window.tektonUI?.services?.engramLLMService) {
            engramLLMService = window.tektonUI.services.engramLLMService;
            
            // Connect to service now if possible
            connectToEngramLLMService();
        } else {
            // Dynamically load and initialize the service
            const script = document.createElement('script');
            script.src = '/scripts/engram/engram-llm-service.js';
            document.head.appendChild(script);
            
            // Create a polling mechanism to wait for service initialization
            const checkServiceInterval = setInterval(() => {
                if (window.tektonUI?.services?.engramLLMService) {
                    engramLLMService = window.tektonUI.services.engramLLMService;
                    clearInterval(checkServiceInterval);
                    
                    // Connect to service when available
                    connectToEngramLLMService();
                }
            }, 100);
            
            // Give up after 5 seconds
            setTimeout(() => {
                if (\!window.tektonUI?.services?.engramLLMService) {
                    clearInterval(checkServiceInterval);
                    notifications.show(component, 'Error', 'Failed to load Engram LLM service. Chat features may not work.', 'error');
                }
            }, 5000);
        }
    }
    
    /**
     * Connect to the Engram LLM service and set up listeners
     */
    function connectToEngramLLMService() {
        if (\!engramLLMService) return;
        
        // Set up service event listeners
        engramLLMService.addEventListener('connected', handleLLMServiceConnected);
        engramLLMService.addEventListener('connectionFailed', handleLLMConnectionFailed);
        engramLLMService.addEventListener('messageReceived', handleLLMMessageReceived);
        engramLLMService.addEventListener('messageSent', handleLLMMessageSent);
        engramLLMService.addEventListener('streamingChunk', handleLLMStreamingChunk);
        engramLLMService.addEventListener('streamingError', handleLLMStreamingError);
        engramLLMService.addEventListener('streamingCancelled', handleLLMStreamingCancelled);
        engramLLMService.addEventListener('conversationSaved', handleLLMConversationSaved);
        engramLLMService.addEventListener('conversationLoaded', handleLLMConversationLoaded);
        engramLLMService.addEventListener('chatCleared', handleLLMChatCleared);
        engramLLMService.addEventListener('error', handleLLMServiceError);
        
        // Connect to service
        engramLLMService.connect().then(connected => {
            if (connected) {
                // Update available models
                updateLLMModels();
                
                // Initialize chat interface
                initializeChatInterface();
            }
        });
    }
    
    /**
     * Set up UI event handlers
     */
    function setupEventHandlers() {
        // Tab switching
        component.on('click', '.engram-tabs__button', function(event) {
            const tabId = this.getAttribute('data-tab');
            switchTab(tabId);
        });
        
        // Memory search
        const memorySearch = component.$('#memory-search');
        const memoryNamespace = component.$('#memory-namespace');
        const searchMemoryButton = component.$('#search-memory');
        
        if (memorySearch && memoryNamespace && searchMemoryButton) {
            // Update state on input
            memorySearch.addEventListener('input', (event) => {
                component.state.set('memorySearch', event.target.value);
            });
            
            // Update state on namespace change
            memoryNamespace.addEventListener('change', (event) => {
                component.state.set('memoryNamespace', event.target.value);
            });
            
            // Search button click
            searchMemoryButton.addEventListener('click', () => {
                searchMemories();
            });
            
            // Set initial values from state
            memorySearch.value = component.state.get('memorySearch') || '';
            memoryNamespace.value = component.state.get('memoryNamespace') || 'conversations';
        }
        
        // Add memory button
        const addMemoryButton = component.$('#add-memory');
        if (addMemoryButton) {
            addMemoryButton.addEventListener('click', () => {
                showAddMemoryModal();
            });
        }
        
        // Structured memory search
        const structuredSearch = component.$('#structured-search');
        const structuredCategory = component.$('#structured-category');
        const searchStructuredButton = component.$('#search-structured');
        
        if (structuredSearch && structuredCategory && searchStructuredButton) {
            // Update state on input
            structuredSearch.addEventListener('input', (event) => {
                component.state.set('structuredSearch', event.target.value);
            });
            
            // Update state on category change
            structuredCategory.addEventListener('change', (event) => {
                component.state.set('structuredCategory', event.target.value);
            });
            
            // Search button click
            searchStructuredButton.addEventListener('click', () => {
                searchStructuredMemories();
            });
            
            // Set initial values from state
            structuredSearch.value = component.state.get('structuredSearch') || '';
            structuredCategory.value = component.state.get('structuredCategory') || 'all';
        }
        
        // Add structured memory button
        const addStructuredButton = component.$('#add-structured');
        if (addStructuredButton) {
            addStructuredButton.addEventListener('click', () => {
                showAddStructuredMemoryModal();
            });
        }
        
        // Analytics
        const analyticsType = component.$('#analytics-type');
        const refreshAnalyticsButton = component.$('#refresh-analytics');
        
        if (analyticsType && refreshAnalyticsButton) {
            // Update state on type change
            analyticsType.addEventListener('change', (event) => {
                component.state.set('analyticsType', event.target.value);
                loadAnalytics();
            });
            
            // Refresh button click
            refreshAnalyticsButton.addEventListener('click', () => {
                loadAnalytics();
            });
            
            // Set initial value from state
            analyticsType.value = component.state.get('analyticsType') || 'usage';
        }
        
        // Export analytics button
        const exportAnalyticsButton = component.$('#export-analytics');
        if (exportAnalyticsButton) {
            exportAnalyticsButton.addEventListener('click', () => {
                exportAnalytics();
            });
        }
        
        // Chat input
        const chatInput = component.$('#chat-input');
        const sendButton = component.$('#send-message');
        
        if (chatInput && sendButton) {
            // Send on Enter (without Shift)
            chatInput.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' && \!event.shiftKey) {
                    event.preventDefault();
                    sendChatMessage();
                }
                
                // Auto resize textarea
                setTimeout(() => {
                    chatInput.style.height = 'auto';
                    chatInput.style.height = Math.min(chatInput.scrollHeight, 150) + 'px';
                }, 0);
            });
            
            // Send on button click
            sendButton.addEventListener('click', () => {
                sendChatMessage();
            });
        }
        
        // Model selection
        const modelSelect = component.$('#llm-model-select');
        if (modelSelect) {
            modelSelect.addEventListener('change', (event) => {
                const selectedModel = event.target.value;
                
                // Update state
                component.state.set({
                    chat: {
                        ...component.state.get('chat'),
                        selectedModel
                    }
                });
                
                // Update LLM service
                if (engramLLMService) {
                    engramLLMService.setProviderAndModel('anthropic', selectedModel);
                }
            });
        }
        
        // Memory namespace selection for chat
        const namespaceSelect = component.$('#memory-namespace-select');
        if (namespaceSelect) {
            namespaceSelect.addEventListener('change', (event) => {
                const namespace = event.target.value;
                
                // Update state
                component.state.set('memoryNamespace', namespace);
                
                // Update LLM service
                if (engramLLMService) {
                    engramLLMService.setNamespace(namespace);
                }
            });
        }
        
        // Use memory context checkbox
        const useMemoryContext = component.$('#use-memory-context');
        if (useMemoryContext) {
            useMemoryContext.addEventListener('change', (event) => {
                component.state.set({
                    chat: {
                        ...component.state.get('chat'),
                        useMemoryContext: event.target.checked
                    }
                });
            });
        }
        
        // Streaming option
        const chatStreaming = component.$('#chat-streaming');
        if (chatStreaming) {
            chatStreaming.addEventListener('change', (event) => {
                component.state.set({
                    chat: {
                        ...component.state.get('chat'),
                        useStreaming: event.target.checked
                    }
                });
            });
        }
        
        // Clear chat button
        const clearChatButton = component.$('#clear-chat');
        if (clearChatButton) {
            clearChatButton.addEventListener('click', () => {
                clearChat();
            });
        }
        
        // Save conversation button
        const saveConversationButton = component.$('#save-conversation');
        if (saveConversationButton) {
            saveConversationButton.addEventListener('click', () => {
                saveCurrentConversation();
            });
        }
        
        // Modal close buttons
        component.on('click', '#close-modal, #modal-cancel', function(event) {
            closeModal();
        });
        
        // Close modal when clicking overlay
        component.on('click', '.engram-modal__overlay', function(event) {
            closeModal();
        });
    }
    
    /**
     * Set up state effects
     */
    function setupStateEffects() {
        // Handle tab changes
        lifecycle.registerStateEffect(component, 
            ['activeTab'], 
            (state) => {
                updateActiveTab(state.activeTab);
            },
            { runImmediately: true }
        );
        
        // Handle memory updates
        lifecycle.registerStateEffect(component, 
            ['memories'], 
            (state) => {
                renderMemories(state.memories);
            }
        );
        
        // Handle structured memory updates
        lifecycle.registerStateEffect(component, 
            ['structuredMemories'], 
            (state) => {
                renderStructuredMemories(state.structuredMemories);
            }
        );
        
        // Handle analytics updates
        lifecycle.registerStateEffect(component, 
            ['analytics', 'analyticsType'], 
            (state) => {
                renderAnalytics(state.analytics, state.analyticsType);
            }
        );
        
        // Handle modal state changes
        lifecycle.registerStateEffect(component, 
            ['isModalOpen', 'modalContent'], 
            (state) => {
                updateModal(state.isModalOpen, state.modalContent);
            }
        );
        
        // Handle chat typing indicator
        lifecycle.registerStateEffect(component, 
            ['chat.isTyping'], 
            (state) => {
                updateTypingIndicator(state.chat.isTyping);
            }
        );
    }
    
    /**
     * Switch to a different tab
     * @param {string} tabId - Tab ID to switch to
     */
    function switchTab(tabId) {
        // Update state with new active tab
        component.state.set('activeTab', tabId);
        
        // Load data for the selected tab if needed
        if (tabId === 'memory') {
            searchMemories();
        } else if (tabId === 'structured') {
            searchStructuredMemories();
        } else if (tabId === 'analytics') {
            loadAnalytics();
        }
    }
    
    /**
     * Update active tab in the UI
     * @param {string} tabId - Active tab ID
     */
    function updateActiveTab(tabId) {
        // Update tab buttons
        component.$$('.engram-tabs__button').forEach(button => {
            if (button.getAttribute('data-tab') === tabId) {
                button.classList.add('engram-tabs__button--active');
            } else {
                button.classList.remove('engram-tabs__button--active');
            }
        });
        
        // Update tab panels
        component.$$('.engram-tab-panel').forEach(panel => {
            if (panel.getAttribute('data-panel') === tabId) {
                panel.classList.add('engram-tab-panel--active');
            } else {
                panel.classList.remove('engram-tab-panel--active');
            }
        });
    }
    
    /**
     * Search memories based on current state
     */
    function searchMemories() {
        // Get search parameters from state
        const searchQuery = component.state.get('memorySearch');
        const namespace = component.state.get('memoryNamespace');
        
        // Show loading indicator
        loading.show(component, 'Searching memories...');
        
        // TODO: Implement actual API call to Engram service
        // For now, use placeholder data
        setTimeout(() => {
            const memories = [
                {
                    id: '1',
                    content: 'Memory about the project requirements and architecture decisions',
                    namespace: 'conversations',
                    timestamp: new Date().toISOString(),
                    metadata: {
                        type: 'conversation',
                        importance: 'high'
                    }
                },
                {
                    id: '2',
                    content: 'Discussion about implementing the LLM adapter pattern across components',
                    namespace: 'conversations',
                    timestamp: new Date(Date.now() - 3600000).toISOString(),
                    metadata: {
                        type: 'conversation',
                        importance: 'medium'
                    }
                }
            ];
            
            // Update state with results
            component.state.set('memories', memories);
            
            // Hide loading indicator
            loading.hide(component);
        }, 500);
    }
    
    /**
     * Render memories in the UI
     * @param {Array} memories - List of memories
     */
    function renderMemories(memories) {
        const memoryContainer = component.$('#memory-results');
        if (\!memoryContainer) return;
        
        // Check if we have memories
        if (\!memories || memories.length === 0) {
            memoryContainer.innerHTML = `
                <div class="engram-memory-container__placeholder">
                    No memories found. Try a different search or namespace.
                </div>
            `;
            return;
        }
        
        // Create HTML for memories
        let html = '';
        memories.forEach(memory => {
            const date = new Date(memory.timestamp).toLocaleString();
            html += `
                <div class="engram-memory-item" data-id="${memory.id}">
                    <div class="engram-memory-item__header">
                        <div class="engram-memory-item__namespace">${memory.namespace}</div>
                        <div class="engram-memory-item__timestamp">${date}</div>
                    </div>
                    <div class="engram-memory-item__content">${memory.content}</div>
                    <div class="engram-memory-item__footer">
                        <button class="engram-button engram-button--small view-memory" data-id="${memory.id}">View</button>
                        <button class="engram-button engram-button--small delete-memory" data-id="${memory.id}">Delete</button>
                    </div>
                </div>
            `;
        });
        
        memoryContainer.innerHTML = html;
        
        // Add event listeners for memory actions
        component.$$('.view-memory').forEach(button => {
            button.addEventListener('click', () => {
                const memoryId = button.getAttribute('data-id');
                viewMemory(memoryId);
            });
        });
        
        component.$$('.delete-memory').forEach(button => {
            button.addEventListener('click', () => {
                const memoryId = button.getAttribute('data-id');
                deleteMemory(memoryId);
            });
        });
    }
    
    /**
     * Show modal for adding a memory
     */
    function showAddMemoryModal() {
        // Create modal content
        const modalContent = {
            title: 'Add Memory',
            body: `
                <div class="engram-modal__form">
                    <div class="engram-modal__form-group">
                        <label class="engram-modal__label">Content:</label>
                        <textarea id="memory-content" class="engram-textarea" rows="4" placeholder="Enter memory content"></textarea>
                    </div>
                    
                    <div class="engram-modal__form-group">
                        <label class="engram-modal__label">Namespace:</label>
                        <select id="modal-memory-namespace" class="engram-select">
                            <option value="conversations">Conversations</option>
                            <option value="thinking">Thinking</option>
                            <option value="longterm">Long-term</option>
                        </select>
                    </div>
                </div>
            `,
            actionButton: {
                label: 'Add Memory',
                callback: () => {
                    addMemory();
                }
            }
        };
        
        // Show the modal
        showModal(modalContent);
    }
    
    /**
     * Add a memory from the modal
     */
    function addMemory() {
        const content = component.$('#memory-content')?.value.trim();
        const namespace = component.$('#modal-memory-namespace')?.value;
        
        if (\!content) {
            notifications.show(component, 'Error', 'Memory content is required', 'error');
            return;
        }
        
        // TODO: Implement actual API call to Engram service
        // For now, just update the UI
        closeModal();
        notifications.show(component, 'Success', 'Memory added', 'success');
        
        // Refresh memories
        searchMemories();
    }
    
    /**
     * View memory details
     * @param {string} memoryId - Memory ID
     */
    function viewMemory(memoryId) {
        // Find memory in state
        const memories = component.state.get('memories');
        const memory = memories.find(m => m.id === memoryId);
        
        if (\!memory) {
            notifications.show(component, 'Error', 'Memory not found', 'error');
            return;
        }
        
        // Format metadata for display
        let metadataHtml = '<p>None</p>';
        if (memory.metadata && Object.keys(memory.metadata).length > 0) {
            metadataHtml = `
                <dl class="engram-metadata-list">
                    ${Object.entries(memory.metadata).map(([key, value]) => `
                        <dt>${key}:</dt>
                        <dd>${value}</dd>
                    `).join('')}
                </dl>
            `;
        }
        
        // Show memory details in modal
        showModal({
            title: 'Memory Details',
            body: `
                <div class="engram-modal__section">
                    <h4 class="engram-modal__section-title">Content</h4>
                    <div class="engram-modal__content">
                        ${memory.content}
                    </div>
                </div>
                
                <div class="engram-modal__section">
                    <h4 class="engram-modal__section-title">Metadata</h4>
                    <div class="engram-modal__metadata">
                        <p><strong>Namespace:</strong> ${memory.namespace}</p>
                        <p><strong>Created:</strong> ${new Date(memory.timestamp).toLocaleString()}</p>
                        ${metadataHtml}
                    </div>
                </div>
            `,
            actionButton: {
                label: 'Close',
                callback: () => {
                    closeModal();
                }
            }
        });
    }
    
    /**
     * Delete a memory
     * @param {string} memoryId - Memory ID
     */
    function deleteMemory(memoryId) {
        // Show confirmation dialog
        showConfirmationDialog(
            'Delete Memory',
            'Are you sure you want to delete this memory? This cannot be undone.',
            () => {
                // TODO: Implement actual API call to Engram service
                
                // Update state by removing the memory
                const memories = component.state.get('memories');
                const updatedMemories = memories.filter(m => m.id \!== memoryId);
                component.state.set('memories', updatedMemories);
                
                notifications.show(component, 'Success', 'Memory deleted', 'success');
            }
        );
    }
    
    /**
     * Search structured memories based on current state
     */
    function searchStructuredMemories() {
        // Get search parameters from state
        const searchQuery = component.state.get('structuredSearch');
        const category = component.state.get('structuredCategory');
        
        // Show loading indicator
        loading.show(component, 'Searching structured memories...');
        
        // TODO: Implement actual API call to Engram service
        // For now, use placeholder data
        setTimeout(() => {
            const memories = [
                {
                    id: '1',
                    content: 'Claude is an AI assistant created by Anthropic',
                    category: 'fact',
                    timestamp: new Date().toISOString(),
                    tags: ['ai', 'claude', 'anthropic'],
                    importance: 4
                },
                {
                    id: '2',
                    content: 'Casey Koons is the developer working on the Tekton project',
                    category: 'person',
                    timestamp: new Date(Date.now() - 3600000).toISOString(),
                    tags: ['person', 'developer', 'tekton'],
                    importance: 3
                }
            ];
            
            // Update state with results
            component.state.set('structuredMemories', memories);
            
            // Hide loading indicator
            loading.hide(component);
        }, 500);
    }
    
    /**
     * Render structured memories in the UI
     * @param {Array} memories - List of structured memories
     */
    function renderStructuredMemories(memories) {
        const container = component.$('#structured-results');
        if (\!container) return;
        
        // Check if we have memories
        if (\!memories || memories.length === 0) {
            container.innerHTML = `
                <div class="engram-structured-container__placeholder">
                    No structured memories found. Try a different search or category.
                </div>
            `;
            return;
        }
        
        // Create HTML for memories
        let html = '';
        memories.forEach(memory => {
            const date = new Date(memory.timestamp).toLocaleString();
            
            // Format tags
            const tags = memory.tags?.map(tag => {
                return `<span class="engram-tag">${tag}</span>`;
            }).join('') || '';
            
            // Format importance as stars
            const importance = '⭐'.repeat(memory.importance || 0);
            
            html += `
                <div class="engram-structured-item" data-id="${memory.id}">
                    <div class="engram-structured-item__header">
                        <div class="engram-structured-item__category">${memory.category}</div>
                        <div class="engram-structured-item__importance">${importance}</div>
                    </div>
                    <div class="engram-structured-item__content">${memory.content}</div>
                    <div class="engram-structured-item__tags">${tags}</div>
                    <div class="engram-structured-item__footer">
                        <div class="engram-structured-item__timestamp">${date}</div>
                        <div class="engram-structured-item__actions">
                            <button class="engram-button engram-button--small view-structured" data-id="${memory.id}">View</button>
                            <button class="engram-button engram-button--small delete-structured" data-id="${memory.id}">Delete</button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
        // Add event listeners for memory actions
        component.$$('.view-structured').forEach(button => {
            button.addEventListener('click', () => {
                const memoryId = button.getAttribute('data-id');
                viewStructuredMemory(memoryId);
            });
        });
        
        component.$$('.delete-structured').forEach(button => {
            button.addEventListener('click', () => {
                const memoryId = button.getAttribute('data-id');
                deleteStructuredMemory(memoryId);
            });
        });
    }
    
    /**
     * Show modal for adding a structured memory
     */
    function showAddStructuredMemoryModal() {
        // Create modal content
        const modalContent = {
            title: 'Add Structured Memory',
            body: `
                <div class="engram-modal__form">
                    <div class="engram-modal__form-group">
                        <label class="engram-modal__label">Content:</label>
                        <textarea id="structured-content" class="engram-textarea" rows="4" placeholder="Enter memory content"></textarea>
                    </div>
                    
                    <div class="engram-modal__form-group">
                        <label class="engram-modal__label">Category:</label>
                        <select id="modal-category" class="engram-select">
                            <option value="person">Person</option>
                            <option value="concept">Concept</option>
                            <option value="fact">Fact</option>
                            <option value="session">Session</option>
                        </select>
                    </div>
                    
                    <div class="engram-modal__form-group">
                        <label class="engram-modal__label">Importance (1-5):</label>
                        <input type="number" id="structured-importance" class="engram-input" min="1" max="5" value="3">
                    </div>
                    
                    <div class="engram-modal__form-group">
                        <label class="engram-modal__label">Tags (comma separated):</label>
                        <input type="text" id="structured-tags" class="engram-input" placeholder="e.g. person, developer, tekton">
                    </div>
                </div>
            `,
            actionButton: {
                label: 'Add Memory',
                callback: () => {
                    addStructuredMemory();
                }
            }
        };
        
        // Show the modal
        showModal(modalContent);
    }
    
    /**
     * Add a structured memory from the modal
     */
    function addStructuredMemory() {
        const content = component.$('#structured-content')?.value.trim();
        const category = component.$('#modal-category')?.value;
        const importance = parseInt(component.$('#structured-importance')?.value || '3', 10);
        const tagsInput = component.$('#structured-tags')?.value.trim();
        
        if (\!content) {
            notifications.show(component, 'Error', 'Memory content is required', 'error');
            return;
        }
        
        // Parse tags
        const tags = tagsInput ? tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag) : [];
        
        // TODO: Implement actual API call to Engram service
        // For now, just update the UI
        closeModal();
        notifications.show(component, 'Success', 'Structured memory added', 'success');
        
        // Refresh structured memories
        searchStructuredMemories();
    }
    
    /**
     * View structured memory details
     * @param {string} memoryId - Memory ID
     */
    function viewStructuredMemory(memoryId) {
        // Find memory in state
        const memories = component.state.get('structuredMemories');
        const memory = memories.find(m => m.id === memoryId);
        
        if (\!memory) {
            notifications.show(component, 'Error', 'Memory not found', 'error');
            return;
        }
        
        // Format tags
        const tags = memory.tags?.map(tag => {
            return `<span class="engram-tag">${tag}</span>`;
        }).join(' ') || 'None';
        
        // Format importance as stars
        const importance = '⭐'.repeat(memory.importance || 0);
        
        // Show memory details in modal
        showModal({
            title: 'Structured Memory Details',
            body: `
                <div class="engram-modal__section">
                    <h4 class="engram-modal__section-title">Content</h4>
                    <div class="engram-modal__content">
                        ${memory.content}
                    </div>
                </div>
                
                <div class="engram-modal__section">
                    <h4 class="engram-modal__section-title">Metadata</h4>
                    <div class="engram-modal__metadata">
                        <p><strong>Category:</strong> ${memory.category}</p>
                        <p><strong>Importance:</strong> ${importance}</p>
                        <p><strong>Created:</strong> ${new Date(memory.timestamp).toLocaleString()}</p>
                        <p><strong>Tags:</strong> ${tags}</p>
                    </div>
                </div>
            `,
            actionButton: {
                label: 'Close',
                callback: () => {
                    closeModal();
                }
            }
        });
    }
    
    /**
     * Delete a structured memory
     * @param {string} memoryId - Memory ID
     */
    function deleteStructuredMemory(memoryId) {
        // Show confirmation dialog
        showConfirmationDialog(
            'Delete Structured Memory',
            'Are you sure you want to delete this structured memory? This cannot be undone.',
            () => {
                // TODO: Implement actual API call to Engram service
                
                // Update state by removing the memory
                const memories = component.state.get('structuredMemories');
                const updatedMemories = memories.filter(m => m.id \!== memoryId);
                component.state.set('structuredMemories', updatedMemories);
                
                notifications.show(component, 'Success', 'Structured memory deleted', 'success');
            }
        );
    }
    
    /**
     * Load analytics data
     */
    function loadAnalytics() {
        const analyticsType = component.state.get('analyticsType');
        
        // Show loading indicator
        loading.show(component, 'Loading analytics...');
        
        // TODO: Implement actual API call to Engram service
        // For now, use placeholder data
        setTimeout(() => {
            let analytics = null;
            
            if (analyticsType === 'usage') {
                analytics = {
                    memoryOperations: {
                        reads: 235,
                        writes: 89,
                        relevancyScores: [0.78, 0.65, 0.92]
                    },
                    namespaceUsage: {
                        conversations: 120,
                        thinking: 45,
                        longterm: 60
                    },
                    timeRange: {
                        start: new Date(Date.now() - 7 * 24 * 3600 * 1000).toISOString(),
                        end: new Date().toISOString()
                    }
                };
            } else if (analyticsType === 'retrieval') {
                analytics = {
                    averageLatency: 58, // ms
                    retrievalAccuracy: 0.82,
                    contextEnhancement: 0.37,
                    sampleQueries: [
                        { query: "project architecture", latency: 45, results: 5 },
                        { query: "phase 11.5 implementation", latency: 62, results: 3 },
                        { query: "LLM adapter integration", latency: 51, results: 7 }
                    ]
                };
            } else if (analyticsType === 'storage') {
                analytics = {
                    totalMemories: 324,
                    byNamespace: {
                        conversations: 153,
                        thinking: 98,
                        longterm: 73
                    },
                    byCategory: {
                        person: 45,
                        concept: 62,
                        fact: 87,
                        session: 130
                    },
                    averageMemorySize: 512 // bytes
                };
            }
            
            // Update state with analytics
            component.state.set('analytics', analytics);
            
            // Hide loading indicator
            loading.hide(component);
        }, 500);
    }
    
    /**
     * Render analytics in the UI
     * @param {Object} analytics - Analytics data
     * @param {string} analyticsType - Type of analytics to render
     */
    function renderAnalytics(analytics, analyticsType) {
        const container = component.$('#analytics-content');
        if (\!container) return;
        
        // Check if we have analytics data
        if (\!analytics) {
            container.innerHTML = `
                <div class="engram-analytics-container__placeholder">
                    No analytics data available. Try refreshing.
                </div>
            `;
            return;
        }
        
        // Render based on analytics type
        if (analyticsType === 'usage') {
            container.innerHTML = `
                <div class="engram-analytics-section">
                    <h3 class="engram-analytics-section__title">Memory Usage</h3>
                    <div class="engram-analytics-metrics">
                        <div class="engram-analytics-metric">
                            <div class="engram-analytics-metric__label">Total Reads</div>
                            <div class="engram-analytics-metric__value">${analytics.memoryOperations.reads}</div>
                        </div>
                        <div class="engram-analytics-metric">
                            <div class="engram-analytics-metric__label">Total Writes</div>
                            <div class="engram-analytics-metric__value">${analytics.memoryOperations.writes}</div>
                        </div>
                        <div class="engram-analytics-metric">
                            <div class="engram-analytics-metric__label">Avg. Relevancy</div>
                            <div class="engram-analytics-metric__value">${(analytics.memoryOperations.relevancyScores.reduce((a, b) => a + b, 0) / analytics.memoryOperations.relevancyScores.length).toFixed(2)}</div>
                        </div>
                    </div>
                </div>
                
                <div class="engram-analytics-section">
                    <h3 class="engram-analytics-section__title">Namespace Distribution</h3>
                    <div class="engram-analytics-chart">
                        <div class="engram-chart-placeholder">
                            [Namespace Distribution Chart - ${analytics.namespaceUsage.conversations} conversations, ${analytics.namespaceUsage.thinking} thinking, ${analytics.namespaceUsage.longterm} longterm]
                        </div>
                    </div>
                </div>
                
                <div class="engram-analytics-section">
                    <h3 class="engram-analytics-section__title">Time Range</h3>
                    <div class="engram-analytics-info">
                        <p><strong>Start:</strong> ${new Date(analytics.timeRange.start).toLocaleString()}</p>
                        <p><strong>End:</strong> ${new Date(analytics.timeRange.end).toLocaleString()}</p>
                    </div>
                </div>
            `;
        } else if (analyticsType === 'retrieval') {
            // Create sample queries table
            const queriesTable = analytics.sampleQueries.map(query => {
                return `
                    <tr>
                        <td>${query.query}</td>
                        <td>${query.latency} ms</td>
                        <td>${query.results}</td>
                    </tr>
                `;
            }).join('');
            
            container.innerHTML = `
                <div class="engram-analytics-section">
                    <h3 class="engram-analytics-section__title">Retrieval Performance</h3>
                    <div class="engram-analytics-metrics">
                        <div class="engram-analytics-metric">
                            <div class="engram-analytics-metric__label">Avg. Latency</div>
                            <div class="engram-analytics-metric__value">${analytics.averageLatency} ms</div>
                        </div>
                        <div class="engram-analytics-metric">
                            <div class="engram-analytics-metric__label">Retrieval Accuracy</div>
                            <div class="engram-analytics-metric__value">${(analytics.retrievalAccuracy * 100).toFixed(1)}%</div>
                        </div>
                        <div class="engram-analytics-metric">
                            <div class="engram-analytics-metric__label">Context Enhancement</div>
                            <div class="engram-analytics-metric__value">+${(analytics.contextEnhancement * 100).toFixed(1)}%</div>
                        </div>
                    </div>
                </div>
                
                <div class="engram-analytics-section">
                    <h3 class="engram-analytics-section__title">Sample Queries</h3>
                    <table class="engram-table">
                        <thead>
                            <tr>
                                <th>Query</th>
                                <th>Latency</th>
                                <th>Results</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${queriesTable}
                        </tbody>
                    </table>
                </div>
            `;
        } else if (analyticsType === 'storage') {
            container.innerHTML = `
                <div class="engram-analytics-section">
                    <h3 class="engram-analytics-section__title">Storage Overview</h3>
                    <div class="engram-analytics-metrics">
                        <div class="engram-analytics-metric">
                            <div class="engram-analytics-metric__label">Total Memories</div>
                            <div class="engram-analytics-metric__value">${analytics.totalMemories}</div>
                        </div>
                        <div class="engram-analytics-metric">
                            <div class="engram-analytics-metric__label">Avg. Memory Size</div>
                            <div class="engram-analytics-metric__value">${analytics.averageMemorySize} bytes</div>
                        </div>
                    </div>
                </div>
                
                <div class="engram-analytics-section">
                    <h3 class="engram-analytics-section__title">Distribution by Namespace</h3>
                    <div class="engram-analytics-chart">
                        <div class="engram-chart-placeholder">
                            [Namespace Distribution Chart - ${analytics.byNamespace.conversations} conversations, ${analytics.byNamespace.thinking} thinking, ${analytics.byNamespace.longterm} longterm]
                        </div>
                    </div>
                </div>
                
                <div class="engram-analytics-section">
                    <h3 class="engram-analytics-section__title">Distribution by Category</h3>
                    <div class="engram-analytics-chart">
                        <div class="engram-chart-placeholder">
                            [Category Distribution Chart - ${analytics.byCategory.person} person, ${analytics.byCategory.concept} concept, ${analytics.byCategory.fact} fact, ${analytics.byCategory.session} session]
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    /**
     * Export analytics data
     */
    function exportAnalytics() {
        const analytics = component.state.get('analytics');
        
        if (\!analytics) {
            notifications.show(component, 'Error', 'No analytics data to export', 'error');
            return;
        }
        
        // Convert to JSON
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(analytics, null, 2));
        
        // Create download link
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `engram-analytics-${component.state.get('analyticsType')}-${new Date().toISOString().slice(0, 10)}.json`);
        
        // Add to document, click, and remove
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    }
    
    /**
     * Update LLM models dropdown
     */
    function updateLLMModels() {
        if (\!engramLLMService) return;
        
        const modelSelect = component.$('#llm-model-select');
        if (\!modelSelect) return;
        
        // Clear current options
        modelSelect.innerHTML = '';
        
        // Get available models from LLM service
        const providers = engramLLMService.availableModels;
        
        // Add options for each provider and model
        for (const providerId in providers) {
            const provider = providers[providerId];
            
            if (provider.models && provider.models.length > 0) {
                // Add provider group
                const optgroup = document.createElement('optgroup');
                optgroup.label = providerId.charAt(0).toUpperCase() + providerId.slice(1);
                
                // Add models
                provider.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name || model.id;
                    
                    // Set as selected if it's the current model
                    if (model.id === engramLLMService.currentModel) {
                        option.selected = true;
                        
                        // Update state
                        component.state.set({
                            chat: {
                                ...component.state.get('chat'),
                                selectedModel: model.id
                            }
                        });
                    }
                    
                    optgroup.appendChild(option);
                });
                
                modelSelect.appendChild(optgroup);
            }
        }
        
        // If no models were found, add a default option
        if (modelSelect.options.length === 0) {
            const option = document.createElement('option');
            option.value = engramLLMService.currentModel;
            option.textContent = engramLLMService.currentModel;
            option.selected = true;
            modelSelect.appendChild(option);
        }
    }
    
    /**
     * Initialize the chat interface
     */
    function initializeChatInterface() {
        // Set up event handlers for chat UI
        setupChatEventHandlers();
        
        // Update saved conversations list
        updateSavedConversations();
        
        // Restore chat history if available
        if (engramLLMService && engramLLMService.chatHistory && engramLLMService.chatHistory.length > 0) {
            // Clear default welcome message
            const chatMessages = component.$('#chat-messages');
            if (chatMessages) {
                chatMessages.innerHTML = '';
            }
            
            // Render all messages from chat history
            engramLLMService.chatHistory.forEach(message => {
                renderChatMessage(message);
            });
        }
    }
    
    /**
     * Set up chat event handlers
     */
    function setupChatEventHandlers() {
        // These are already set up in the main setupEventHandlers function
    }
    
    /**
     * Send a chat message
     */
    function sendChatMessage() {
        if (\!engramLLMService) return;
        
        const chatInput = component.$('#chat-input');
        if (\!chatInput) return;
        
        const message = chatInput.value.trim();
        if (\!message) return;
        
        // Clear input
        chatInput.value = '';
        chatInput.style.height = 'auto';
        
        // Get chat settings
        const chatSettings = component.state.get('chat');
        const namespace = component.state.get('memoryNamespace');
        
        // Send message via LLM service
        engramLLMService.sendChatMessage(
            message,
            chatSettings.useStreaming,
            {
                model: chatSettings.selectedModel,
                namespace: namespace,
                useMemoryContext: chatSettings.useMemoryContext
            }
        ).catch(error => {
            console.error('Error sending message:', error);
            notifications.show(component, 'Error', `Failed to send message: ${error.message}`, 'error');
        });
    }
    
    /**
     * Render a chat message in the UI
     * @param {Object} message - Message object
     */
    function renderChatMessage(message) {
        const chatMessages = component.$('#chat-messages');
        if (\!chatMessages) return;
        
        // Check if message with same timestamp already exists
        if (message.timestamp) {
            const existingMessage = chatMessages.querySelector(`.engram-message[data-timestamp="${message.timestamp}"]`);
            if (existingMessage) {
                return; // Skip duplicate messages
            }
        }
        
        // Create message element
        const messageElement = document.createElement('div');
        messageElement.className = `engram-message engram-message--${message.role}`;
        messageElement.setAttribute('data-timestamp', message.timestamp || Date.now());
        
        // Format timestamp
        const timestampText = message.timestamp ? formatTimestamp(message.timestamp) : formatTimestamp(Date.now());
        
        // Create message HTML
        messageElement.innerHTML = `
            <div class="engram-message__content">
                ${message.content}
            </div>
            <div class="engram-message__timestamp">${timestampText}</div>
        `;
        
        // Add to chat
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        scrollChatToBottom();
    }
    
    /**
     * Update streaming message in the UI
     * @param {string} content - Updated message content
     */
    function updateStreamingMessage(content) {
        const chatMessages = component.$('#chat-messages');
        if (\!chatMessages) return;
        
        // Find or create assistant message element
        let assistantMessage = chatMessages.querySelector('.engram-message--assistant:last-child');
        
        if (\!assistantMessage) {
            // Create new message element
            assistantMessage = document.createElement('div');
            assistantMessage.className = 'engram-message engram-message--assistant';
            assistantMessage.innerHTML = `
                <div class="engram-message__content"></div>
                <div class="engram-message__timestamp">${formatTimestamp(Date.now())}</div>
            `;
            chatMessages.appendChild(assistantMessage);
        }
        
        // Update content
        const contentElement = assistantMessage.querySelector('.engram-message__content');
        if (contentElement) {
            contentElement.innerHTML = content;
        }
        
        // Scroll to bottom if near the bottom
        if (isScrolledNearBottom(chatMessages)) {
            scrollChatToBottom();
        }
    }
    
    /**
     * Update typing indicator in the chat UI
     * @param {boolean} isTyping - Whether the assistant is typing
     */
    function updateTypingIndicator(isTyping) {
        const chatMessages = component.$('#chat-messages');
        if (\!chatMessages) return;
        
        // Find existing typing indicator or create a new one
        let typingIndicator = chatMessages.querySelector('.engram-typing-indicator');
        
        if (isTyping) {
            if (\!typingIndicator) {
                // Create typing indicator
                typingIndicator = document.createElement('div');
                typingIndicator.className = 'engram-typing-indicator';
                typingIndicator.innerHTML = `
                    <div class="engram-typing-indicator__dot"></div>
                    <div class="engram-typing-indicator__dot"></div>
                    <div class="engram-typing-indicator__dot"></div>
                `;
                chatMessages.appendChild(typingIndicator);
                
                // Scroll to show typing indicator
                scrollChatToBottom();
            }
        } else {
            // Remove typing indicator if it exists
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }
    }
    
    /**
     * Scroll chat to bottom
     */
    function scrollChatToBottom() {
        const chatMessages = component.$('#chat-messages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    /**
     * Check if element is scrolled near the bottom
     * @param {HTMLElement} element - Element to check
     * @param {number} threshold - Threshold in pixels
     * @returns {boolean} - Whether element is scrolled near the bottom
     */
    function isScrolledNearBottom(element, threshold = 100) {
        return element.scrollHeight - element.scrollTop - element.clientHeight < threshold;
    }
    
    /**
     * Clear the chat history
     */
    function clearChat() {
        if (\!engramLLMService) return;
        
        // Show confirmation dialog
        showConfirmationDialog(
            'Clear Chat',
            'Are you sure you want to clear the chat history? This cannot be undone.',
            () => {
                engramLLMService.clearChat();
            }
        );
    }
    
    /**
     * Save the current conversation
     */
    function saveCurrentConversation() {
        if (\!engramLLMService || \!engramLLMService.chatHistory || engramLLMService.chatHistory.length === 0) {
            notifications.show(component, 'Error', 'No messages to save', 'error');
            return;
        }
        
        // Show prompt for conversation name
        showModal({
            title: 'Save Conversation',
            body: `
                <div class="engram-modal__form">
                    <div class="engram-modal__form-group">
                        <label class="engram-modal__label">Conversation Name:</label>
                        <input type="text" id="conversation-name" class="engram-input" value="Conversation ${new Date().toLocaleString()}">
                    </div>
                </div>
            `,
            actionButton: {
                label: 'Save',
                callback: () => {
                    const nameInput = component.$('#conversation-name');
                    const name = nameInput ? nameInput.value.trim() : '';
                    
                    if (\!name) {
                        notifications.show(component, 'Error', 'Conversation name is required', 'error');
                        return;
                    }
                    
                    // Save conversation
                    engramLLMService.saveConversation(name);
                    closeModal();
                }
            }
        });
    }
    
    /**
     * Update saved conversations list
     */
    function updateSavedConversations() {
        if (\!engramLLMService) return;
        
        const savedConversationsList = component.$('#saved-conversations');
        if (\!savedConversationsList) return;
        
        // Get saved conversations
        const conversations = engramLLMService.savedConversations || [];
        
        if (conversations.length === 0) {
            savedConversationsList.innerHTML = `
                <div class="engram-chat-history__empty">
                    No saved conversations yet
                </div>
            `;
            return;
        }
        
        // Sort conversations by timestamp (newest first)
        conversations.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
        
        // Create list items
        let html = '';
        conversations.forEach(conversation => {
            const date = conversation.timestamp ? new Date(conversation.timestamp).toLocaleDateString() : 'Unknown';
            html += `
                <div class="engram-chat-history__item" data-id="${conversation.id}">
                    <div class="engram-chat-history__item-name">${conversation.name}</div>
                    <div class="engram-chat-history__item-date">${date}</div>
                    <div class="engram-chat-history__item-actions">
                        <button class="engram-button engram-button--small load-conversation" data-id="${conversation.id}">Load</button>
                        <button class="engram-button engram-button--small engram-button--danger delete-conversation" data-id="${conversation.id}">Delete</button>
                    </div>
                </div>
            `;
        });
        
        savedConversationsList.innerHTML = html;
        
        // Add event listeners
        component.$$('.load-conversation').forEach(button => {
            button.addEventListener('click', () => {
                const conversationId = button.getAttribute('data-id');
                loadConversation(conversationId);
            });
        });
        
        component.$$('.delete-conversation').forEach(button => {
            button.addEventListener('click', () => {
                const conversationId = button.getAttribute('data-id');
                deleteConversation(conversationId);
            });
        });
    }
    
    /**
     * Load a conversation
     * @param {string} conversationId - Conversation ID
     */
    function loadConversation(conversationId) {
        if (\!engramLLMService) return;
        
        // Load conversation
        engramLLMService.loadConversation(conversationId);
    }
    
    /**
     * Delete a conversation
     * @param {string} conversationId - Conversation ID
     */
    function deleteConversation(conversationId) {
        if (\!engramLLMService) return;
        
        // Get conversation name for confirmation
        const conversation = engramLLMService.savedConversations.find(c => c.id === conversationId);
        const name = conversation ? conversation.name : 'this conversation';
        
        // Show confirmation dialog
        showConfirmationDialog(
            'Delete Conversation',
            `Are you sure you want to delete "${name}"? This cannot be undone.`,
            () => {
                engramLLMService.deleteConversation(conversationId);
                updateSavedConversations();
            }
        );
    }
    
    /**
     * Show a modal dialog
     * @param {Object} content - Modal content
     */
    function showModal(content) {
        component.state.set({
            isModalOpen: true,
            modalContent: content
        });
    }
    
    /**
     * Update the modal with content
     * @param {boolean} isOpen - Whether the modal is open
     * @param {Object} content - Modal content
     */
    function updateModal(isOpen, content) {
        const modal = component.$('#engram-modal');
        
        if (\!modal) return;
        
        if (isOpen && content) {
            // Set modal content
            const modalTitle = component.$('#modal-title');
            const modalBody = component.$('#modal-body');
            const modalAction = component.$('#modal-action');
            
            if (modalTitle) modalTitle.textContent = content.title || 'Details';
            if (modalBody) modalBody.innerHTML = content.body || '';
            
            // Update action button if provided
            if (content.actionButton && modalAction) {
                modalAction.textContent = content.actionButton.label || 'OK';
                modalAction.onclick = content.actionButton.callback || closeModal;
                modalAction.style.display = 'block';
            } else if (modalAction) {
                modalAction.style.display = 'none';
            }
            
            // Show modal
            modal.style.display = 'flex';
        } else {
            // Hide modal
            modal.style.display = 'none';
        }
    }
    
    /**
     * Close the modal dialog
     */
    function closeModal() {
        component.state.set({
            isModalOpen: false,
            modalContent: null
        });
    }
    
    /**
     * Show a confirmation dialog
     * @param {string} title - Dialog title
     * @param {string} message - Dialog message
     * @param {Function} onConfirm - Function to call when confirmed
     */
    function showConfirmationDialog(title, message, onConfirm) {
        const modalContent = {
            title: title,
            body: `<p>${message}</p>`,
            actionButton: {
                label: 'Confirm',
                callback: () => {
                    closeModal();
                    if (typeof onConfirm === 'function') {
                        onConfirm();
                    }
                }
            }
        };
        
        showModal(modalContent);
    }
    
    /**
     * Format timestamp for display
     * @param {string|number} timestamp - Timestamp (ISO string or ms)
     * @returns {string} - Formatted timestamp
     */
    function formatTimestamp(timestamp) {
        if (\!timestamp) return 'Unknown';
        
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString();
        } catch (error) {
            return 'Invalid time';
        }
    }
    
    /* Event handlers for LLM service */
    
    /**
     * Handle LLM service connected event
     * @param {Object} event - Event object
     */
    function handleLLMServiceConnected(event) {
        notifications.show(component, 'Connected', 'Connected to Engram LLM service', 'success');
    }
    
    /**
     * Handle LLM connection failed event
     * @param {Object} event - Event object
     */
    function handleLLMConnectionFailed(event) {
        notifications.show(component, 'Connection Failed', event.detail.error, 'warning');
    }
    
    /**
     * Handle LLM message received event
     * @param {Object} event - Event object
     */
    function handleLLMMessageReceived(event) {
        // Update chat UI with assistant message
        renderChatMessage(event.detail.message);
        
        // Update typing indicator
        component.state.set({
            chat: {
                ...component.state.get('chat'),
                isTyping: false
            }
        });
        
        // Scroll to bottom of chat
        scrollChatToBottom();
    }
    
    /**
     * Handle LLM message sent event
     * @param {Object} event - Event object
     */
    function handleLLMMessageSent(event) {
        // Update chat UI with user message
        renderChatMessage(event.detail.message);
        
        // Update typing indicator
        component.state.set({
            chat: {
                ...component.state.get('chat'),
                isTyping: true
            }
        });
        
        // Scroll to bottom of chat
        scrollChatToBottom();
    }
    
    /**
     * Handle LLM streaming chunk event
     * @param {Object} event - Event object
     */
    function handleLLMStreamingChunk(event) {
        // Update streaming message in the UI
        updateStreamingMessage(event.detail.fullResponse);
    }
    
    /**
     * Handle LLM streaming error event
     * @param {Object} event - Event object
     */
    function handleLLMStreamingError(event) {
        notifications.show(component, 'Error', event.detail.error, 'error');
        
        // Update typing indicator
        component.state.set({
            chat: {
                ...component.state.get('chat'),
                isTyping: false
            }
        });
    }
    
    /**
     * Handle LLM streaming cancelled event
     * @param {Object} event - Event object
     */
    function handleLLMStreamingCancelled(event) {
        // Update typing indicator
        component.state.set({
            chat: {
                ...component.state.get('chat'),
                isTyping: false
            }
        });
    }
    
    /**
     * Handle LLM conversation saved event
     * @param {Object} event - Event object
     */
    function handleLLMConversationSaved(event) {
        // Update saved conversations list
        updateSavedConversations();
        
        notifications.show(component, 'Conversation Saved', `Conversation saved as "${event.detail.conversation.name}"`, 'success');
    }
    
    /**
     * Handle LLM conversation loaded event
     * @param {Object} event - Event object
     */
    function handleLLMConversationLoaded(event) {
        // Clear chat UI
        const chatMessages = component.$('#chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = '';
        }
        
        // Render all messages from the loaded conversation
        if (engramLLMService && engramLLMService.chatHistory) {
            engramLLMService.chatHistory.forEach(message => {
                renderChatMessage(message);
            });
        }
        
        notifications.show(component, 'Conversation Loaded', `Loaded conversation "${event.detail.conversation.name}"`, 'success');
    }
    
    /**
     * Handle LLM chat cleared event
     * @param {Object} event - Event object
     */
    function handleLLMChatCleared(event) {
        // Clear chat UI
        const chatMessages = component.$('#chat-messages');
        if (chatMessages) {
            chatMessages.innerHTML = '<div class="engram-message engram-message--system"><div class="engram-message__content"><p>Chat history cleared. How can I help you?</p></div></div>';
        }
    }
    
    /**
     * Handle LLM service error event
     * @param {Object} event - Event object
     */
    function handleLLMServiceError(event) {
        notifications.show(component, 'LLM Error', event.detail.error, 'error');
    }
    
    /**
     * Clean up component resources
     */
    function cleanupComponent() {
        console.log('Cleaning up Engram component');
        
        // Remove LLM service event listeners
        if (engramLLMService) {
            engramLLMService.removeEventListener('connected', handleLLMServiceConnected);
            engramLLMService.removeEventListener('connectionFailed', handleLLMConnectionFailed);
            engramLLMService.removeEventListener('messageReceived', handleLLMMessageReceived);
            engramLLMService.removeEventListener('messageSent', handleLLMMessageSent);
            engramLLMService.removeEventListener('streamingChunk', handleLLMStreamingChunk);
            engramLLMService.removeEventListener('streamingError', handleLLMStreamingError);
            engramLLMService.removeEventListener('streamingCancelled', handleLLMStreamingCancelled);
            engramLLMService.removeEventListener('conversationSaved', handleLLMConversationSaved);
            engramLLMService.removeEventListener('conversationLoaded', handleLLMConversationLoaded);
            engramLLMService.removeEventListener('chatCleared', handleLLMChatCleared);
            engramLLMService.removeEventListener('error', handleLLMServiceError);
        }
    }
    
    // Initialize the component
    initEngramComponent();
    
})(component);
EOF < /dev/null