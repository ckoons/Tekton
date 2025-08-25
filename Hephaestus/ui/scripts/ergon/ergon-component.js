/**
 * Ergon Component
 * Agent management and LLM integration interface with BEM naming conventions
 */

console.log('[FILE_TRACE] Loading: ergon-component.js');
class ErgonComponent {
    constructor() {
        this.state = {
            initialized: false,
            activeTab: 'agents', // Default tab
            tabHistory: {},      // History for each tab
            modalStates: {
                agentCreation: false,
                agentDetails: false,
                runAgent: false,
                settings: false
            }
        };
        
        // Message history tracking for chat
        this.messageHistory = {
            'ergon': [],
            'awt-team': [],
            'mcp': []
        };
        this.historyPosition = -1;
        this.currentInput = '';
        this.streamHandlersRegistered = false;
        
        // Configure logging level - set to 'debug', 'info', 'warn', or 'error'
        this.logLevel = 'info';
    }
    
    /**
     * Initialize the component
     */
    init() {
        // Original logging
        this.log('info', 'Initializing Ergon component');
        
        // New debug instrumentation
        if (window.TektonDebug) TektonDebug.info('ergonComponent', 'Initializing Ergon component');
        
        // If already initialized, just activate
        if (this.state.initialized) {
            this.log('info', 'Ergon component already initialized, just activating');
            if (window.TektonDebug) TektonDebug.debug('ergonComponent', 'Already initialized, just activating');
            this.activateComponent();
            return this;
        }
        
        // Setup component functionality
        this.setupTabs();
        this.setupEventListeners();
        this.setupChatInputs();
        this.loadAgentData();
        
        // Ensure LLM adapter connection is established
        if (window.hermesConnector && !window.hermesConnector.llmConnected) {
            console.log("Initializing connection to LLM adapter");
            window.hermesConnector.connectToLLMAdapter();
        }
        
        // Apply Greek name handling
        this.handleGreekNames();
        
        // Mark as initialized
        this.state.initialized = true;
        
        return this;
    }
    
    /**
     * Activate the component interface
     */
    activateComponent() {
        console.log('Activating Ergon component');
        
        // Restore component state
        this.restoreComponentState();
    }
    
    /**
     * Handle Greek vs modern naming based on SHOW_GREEK_NAMES env var
     */
    handleGreekNames() {
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            console.error('Ergon container not found!');
            return;
        }
        
        // Get the title element
        const titleElement = container.querySelector('.ergon__title-main');
        const subtitleElement = container.querySelector('.ergon__title-sub');
        
        if (!titleElement || !subtitleElement) {
            return;
        }
        
        // Check environment setting
        if (window.ENV && window.ENV.SHOW_GREEK_NAMES === 'false') {
            // Hide the Greek name
            titleElement.style.display = 'none';
            // Make the modern name more prominent
            subtitleElement.style.fontWeight = 'bold';
            subtitleElement.style.fontSize = '1.5rem';
        }
    }
    
    /**
     * ERGON TAB SWITCHING IS NOW FULLY DISABLED
     * All tab switching is handled by the HTML component
     */
    setupTabs() {
        console.log('Setting up Ergon tabs - DISABLED - Tab management handled by HTML script');
        if (window.TektonDebug) TektonDebug.debug('ergonComponent', 'Tab switching managed by HTML script');
        
        // Deliberately do nothing - let the HTML script handle everything
        // The default tab is set in the HTML script
        
        // Set the initial state
        this.state.activeTab = 'agents';
    }
    
    /**
     * ERGON TAB ACTIVATION IS NOW FULLY DISABLED
     * All tab activation is handled by the HTML component
     * @param {string} tabId - The ID of the tab to activate
     */
    activateTab(tabId) {
        // State management only, no DOM manipulation whatsoever
        console.log(`Ergon: Tab state updated to: ${tabId}`);
        this.state.activeTab = tabId;
        this.saveComponentState();
        
        // Add notification message to terminal
        if (window.websocketManager) {
            // Only add context switch notification for chat tabs
            if (tabId === 'ergon' || tabId === 'awt-team' || tabId === 'mcp') {
                websocketManager.addToTerminal("", 'white'); // blank line for spacing
                websocketManager.addToTerminal(`Switched to ${tabId} chat interface.`, '#888888');
                websocketManager.addToTerminal(`Type '@${tabId === 'awt-team' ? 'awt' : tabId}' to chat directly`, '#888888');
            } else if (tabId === 'agents' || tabId === 'memory' || tabId === 'tools') {
                websocketManager.addToTerminal(`Viewing ${tabId} panel. Use terminal commands to interact.`, '#888888');
            }
        }
        
        // Special handling for chat tabs
        if (tabId === 'ergon' || tabId === 'awt-team' || tabId === 'mcp') {
            // Ensure LLM adapter is connected
            if (window.hermesConnector) {
                // If we have an LLM adapter connector, make sure it's connected
                // This will attempt reconnection if needed
                if (!window.hermesConnector.llmConnected) {
                    console.log(`Connecting to LLM adapter for ${tabId} chat...`);
                    window.hermesConnector.connectToLLMAdapter();
                    
                    // Add a system message that explains the LLM connection
                    const chatMessages = container.querySelector(`#${tabId}-messages`);
                    if (chatMessages) {
                        const systemMsgEl = document.createElement('div');
                        systemMsgEl.className = 'ergon__message ergon__message--system';
                        systemMsgEl.innerHTML = `
                            <div class="ergon__message-content">
                                <div class="ergon__message-text">
                                    <strong>System:</strong> Connecting to LLM for enhanced chat capabilities.
                                    Type your message and press Enter to chat with the AI.
                                </div>
                                <div class="ergon__message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                            </div>
                        `;
                        
                        // Add system message
                        const welcomeMsgEl = chatMessages.querySelector('.ergon__message--system');
                        if (welcomeMsgEl) {
                            // Insert after existing welcome message
                            welcomeMsgEl.parentNode.insertBefore(systemMsgEl, welcomeMsgEl.nextSibling);
                        } else {
                            // Add to the beginning
                            chatMessages.appendChild(systemMsgEl);
                        }
                        
                        // Scroll to bottom
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                    }
                }
            }
        }
    }
    
    /**
     * Save current component state to localStorage
     */
    saveComponentState() {
        // Save to localStorage if available
        if (window.storageManager) {
            storageManager.setItem('ergon_component_state', JSON.stringify(this.state));
        }
        
        console.log('Ergon component state saved, active tab:', this.state.activeTab);
    }
    
    /**
     * Restore component state from localStorage
     */
    restoreComponentState() {
        // Load state from localStorage if available
        if (window.storageManager) {
            const savedState = storageManager.getItem('ergon_component_state');
            if (savedState) {
                try {
                    const parsedState = JSON.parse(savedState);
                    // Merge with current state
                    this.state = {...this.state, ...parsedState};
                } catch (e) {
                    console.error('Error parsing saved Ergon state:', e);
                }
            }
        }
        
        // Activate the previously active tab
        if (this.state.activeTab) {
            this.activateTab(this.state.activeTab);
        }
    }
    
    /**
     * Set up event listeners for UI elements
     */
    setupEventListeners() {
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            console.error('Ergon container not found!');
            return;
        }
        
        // Create agent button
        const createButton = container.querySelector('#create-agent-button');
        if (createButton) {
            createButton.addEventListener('click', () => {
                const agentCreationForm = container.querySelector('#agent-creation-form');
                if (agentCreationForm) {
                    agentCreationForm.style.display = 'block';
                    this.state.modalStates.agentCreation = true;
                }
            });
        }
        
        // Cancel agent creation
        const cancelButton = container.querySelector('#cancel-creation');
        if (cancelButton) {
            cancelButton.addEventListener('click', () => {
                const agentCreationForm = container.querySelector('#agent-creation-form');
                if (agentCreationForm) {
                    agentCreationForm.style.display = 'none';
                    this.state.modalStates.agentCreation = false;
                }
            });
        }
        
        // Submit agent creation
        const submitButton = container.querySelector('#submit-creation');
        if (submitButton) {
            submitButton.addEventListener('click', () => {
                const name = container.querySelector('#agent-name').value;
                const type = container.querySelector('#agent-type').value;
                const description = container.querySelector('#agent-description').value;
                
                if (name && description) {
                    // Send create agent command
                    if (window.tektonUI && typeof tektonUI.sendCommand === 'function') {
                        tektonUI.sendCommand('create_agent', {
                            name: name,
                            type: type,
                            description: description
                        });
                    } else {
                        console.log('Creating agent:', name, type, description);
                    }
                    
                    // Hide form
                    const agentCreationForm = container.querySelector('#agent-creation-form');
                    if (agentCreationForm) {
                        agentCreationForm.style.display = 'none';
                        this.state.modalStates.agentCreation = false;
                    }
                } else {
                    alert('Please fill in all required fields');
                }
            });
        }
        
        // Agent run buttons
        container.querySelectorAll('.ergon__agent-action-button').forEach(button => {
            if (button.getAttribute('data-action') === 'run') {
                button.addEventListener('click', (e) => {
                    e.stopPropagation(); // Prevent event bubbling to card
                    
                    const agentCard = e.target.closest('.ergon__agent-card');
                    const agentName = agentCard.querySelector('.ergon__agent-name').textContent;
                    
                    // Send run agent command
                    if (window.tektonUI && typeof tektonUI.sendCommand === 'function') {
                        tektonUI.sendCommand('run_agent', {
                            agent_name: agentName
                        });
                    } else {
                        console.log('Running agent:', agentName);
                    }
                    
                    // Update status indicator
                    const statusIndicator = agentCard.querySelector('.ergon__agent-status');
                    if (statusIndicator) {
                        statusIndicator.classList.add('ergon__agent-status--active');
                    }
                });
            } else if (button.getAttribute('data-action') === 'delete') {
                button.addEventListener('click', (e) => {
                    e.stopPropagation(); // Prevent event bubbling to card
                    
                    const agentCard = e.target.closest('.ergon__agent-card');
                    const agentName = agentCard.querySelector('.ergon__agent-name').textContent;
                    
                    if (confirm(`Are you sure you want to delete the agent "${agentName}"?`)) {
                        // Send delete agent command
                        if (window.tektonUI && typeof tektonUI.sendCommand === 'function') {
                            tektonUI.sendCommand('delete_agent', {
                                agent_name: agentName
                            });
                        } else {
                            console.log('Deleting agent:', agentName);
                        }
                        
                        // Remove the card with animation
                        agentCard.style.opacity = '0';
                        setTimeout(() => {
                            agentCard.remove();
                        }, 300);
                    }
                });
            }
        });
        
        // Connect main chat input from footer to active panel
        const chatInput = container.querySelector('#chat-input');
        const sendButton = container.querySelector('#send-button');
        
        if (chatInput && sendButton) {
            // Clicking the send button sends message for active tab
            sendButton.addEventListener('click', () => {
                const message = chatInput.value.trim();
                if (message) {
                    this.sendChatMessage(this.state.activeTab, message);
                    chatInput.value = '';
                }
            });
            
            // Enter key in input sends message
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const message = chatInput.value.trim();
                    if (message) {
                        this.sendChatMessage(this.state.activeTab, message);
                        chatInput.value = '';
                    }
                }
            });
        }
    }
    
    /**
     * Set up chat inputs
     */
    setupChatInputs() {
        console.log("Setting up chat interfaces");
        
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            console.error('Ergon container not found!');
            return;
        }
        
        // We don't need to set up individual chat inputs on each panel now
        // since we're using a single chat input in the footer
    }
    
    /**
     * Send a chat message
     * @param {string} context - The chat context (ergon, awt-team, etc.)
     * @param {string} message - The message to send
     */
    sendChatMessage(context, message) {
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            console.error('Ergon container not found!');
            return;
        }
        
        // Get the chat messages container
        const chatMessages = container.querySelector(`#${context}-messages`);
        if (!chatMessages) return;
        
        console.log(`Sending message in ${context} context:`, message);
        
        // Add user message to chat
        const messageDiv = document.createElement('div');
        messageDiv.className = 'ergon__message ergon__message--user';
        messageDiv.innerHTML = `
            <div class="ergon__message-content">
                <div class="ergon__message-text">${message}</div>
                <div class="ergon__message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'ergon__message ergon__message--typing';
        typingDiv.setAttribute('data-typing', 'true');
        typingDiv.innerHTML = `
            <div class="ergon__message-content">
                <div class="ergon__message-text">Processing...</div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Also echo to main terminal
        if (window.websocketManager) {
            // Format as if it was entered in the main terminal with @ prefix
            const termPrefix = context === 'awt-team' ? '@awt' : `@${context}`;
            websocketManager.addToTerminal(`${termPrefix}: ${message}`, '#2962FF');
        }
        
        // Use LLM integration if available
        if (window.hermesConnector) {
            // Register stream event handlers if not already done
            if (!this.streamHandlersRegistered) {
                this.setupStreamHandlers();
            }
            
            // First check if LLM Adapter is connected
            if (!window.hermesConnector.llmConnected) {
                console.log(`LLM Adapter not connected, attempting to connect for ${context}`);
                
                // Add a message to the chat explaining we're trying to connect
                const connectingDiv = document.createElement('div');
                connectingDiv.className = 'ergon__message ergon__message--system';
                connectingDiv.innerHTML = `
                    <div class="ergon__message-content">
                        <div class="ergon__message-text">
                            <strong>System:</strong> Attempting to connect to LLM service...
                        </div>
                        <div class="ergon__message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                    </div>
                `;
                
                // Hide typing indicator before adding this message
                const typingIndicators = chatMessages.querySelectorAll('[data-typing="true"]');
                typingIndicators.forEach(indicator => indicator.remove());
                
                chatMessages.appendChild(connectingDiv);
                
                // Re-add typing indicator
                chatMessages.appendChild(typingDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Send to LLM via Hermes connector
            window.hermesConnector.sendLLMMessage(context, message, true, {
                // Additional options can be configured here
                temperature: 0.7
            });
        } else {
            // Fallback - simulate response after delay
            setTimeout(() => {
                // Remove typing indicators
                const typingIndicators = chatMessages.querySelectorAll('[data-typing="true"]');
                typingIndicators.forEach(indicator => indicator.remove());
                
                // Add response
                const responseDiv = document.createElement('div');
                responseDiv.className = 'ergon__message ergon__message--ai';
                responseDiv.innerHTML = `
                    <div class="ergon__message-content">
                        <div class="ergon__message-text">
                            <strong>Note:</strong> LLM integration not available. This is a simulated response.<br><br>
                            I received your message: "${message}".<br>How can I assist you further?
                        </div>
                        <div class="ergon__message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                    </div>
                `;
                
                chatMessages.appendChild(responseDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Also echo to main terminal
                if (window.websocketManager) {
                    const targetName = context === 'awt-team' ? 'AWT-Team' : 
                                       context === 'mcp' ? 'MCP' : 'Ergon';
                    websocketManager.addToTerminal(`[${targetName}] I received your message: "${message}". How can I assist you further?`, '#00bfff');
                }
            }, 1000);
        }
    }
    
    /**
     * Set up stream event handlers for streaming LLM responses
     */
    setupStreamHandlers() {
        if (!window.hermesConnector) return;
        
        // Set up stream chunk handler
        window.hermesConnector.addEventListener('streamChunk', (data) => {
            const { contextId, chunk } = data;
            
            // Handle chunk based on context
            if (contextId === 'ergon' || contextId === 'awt-team' || contextId === 'mcp') {
                this.handleStreamChunk(contextId, chunk);
            }
        });
        
        // Set up stream completion handler
        window.hermesConnector.addEventListener('streamComplete', (data) => {
            const { contextId, fullResponse } = data;
            
            // Convert streaming message to regular message
            this.finalizeStreamingMessage(contextId);
            
            // Also echo to main terminal if needed
            if (window.websocketManager) {
                const targetName = contextId === 'awt-team' ? 'AWT-Team' : 
                                   contextId === 'mcp' ? 'MCP' : 'Ergon';
                
                // Extract first 100 chars for terminal summary
                const summary = fullResponse.length > 100 ? 
                    fullResponse.substring(0, 100) + '...' : 
                    fullResponse;
                    
                websocketManager.addToTerminal(`[${targetName}] Response: ${summary}`, '#00bfff');
            }
        });
        
        // Handle typing indicators
        window.hermesConnector.addEventListener('typingStarted', (data) => {
            const { contextId } = data;
            
            // Add typing indicator to specific context
            this.showTypingIndicator(contextId);
        });
        
        window.hermesConnector.addEventListener('typingEnded', (data) => {
            const { contextId } = data;
            
            // Remove typing indicator from specific context
            this.hideTypingIndicator(contextId);
        });
        
        // Mark handlers as registered
        this.streamHandlersRegistered = true;
    }
    
    /**
     * Handle stream chunk for a specific context
     * @param {string} contextId - The chat context
     * @param {string} chunk - The text chunk to add
     */
    handleStreamChunk(contextId, chunk) {
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            console.error('Ergon container not found!');
            return;
        }
        
        // Get the chat messages container
        const chatMessages = container.querySelector(`#${contextId}-messages`);
        if (!chatMessages) return;
        
        // Find or create streaming message element
        let streamingMessage = chatMessages.querySelector('.ergon__streaming-message');
        if (!streamingMessage) {
            // Remove typing indicators first
            const typingIndicators = chatMessages.querySelectorAll('[data-typing="true"]');
            typingIndicators.forEach(indicator => indicator.remove());
            
            // Create new streaming message element
            streamingMessage = document.createElement('div');
            streamingMessage.className = 'ergon__message ergon__message--ai ergon__streaming-message';
            streamingMessage.innerHTML = `
                <div class="ergon__message-content">
                    <div class="ergon__message-text"></div>
                    <div class="ergon__message-time">Just now</div>
                </div>
            `;
            
            chatMessages.appendChild(streamingMessage);
        }
        
        // Add chunk to message
        const messageText = streamingMessage.querySelector('.ergon__message-text');
        if (messageText) {
            messageText.innerHTML += chunk;
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    /**
     * Finalize a streaming message when complete
     * @param {string} contextId - The chat context
     */
    finalizeStreamingMessage(contextId) {
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            console.error('Ergon container not found!');
            return;
        }
        
        // Get the chat messages container
        const chatMessages = container.querySelector(`#${contextId}-messages`);
        if (!chatMessages) return;
        
        // Find streaming message element
        const streamingMessage = chatMessages.querySelector('.ergon__streaming-message');
        if (streamingMessage) {
            // Convert to regular message
            streamingMessage.classList.remove('ergon__streaming-message');
            
            // Update timestamp
            const timeElement = streamingMessage.querySelector('.ergon__message-time');
            if (timeElement) {
                const now = new Date();
                timeElement.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            }
        }
    }
    
    /**
     * Show typing indicator for a specific context
     * @param {string} contextId - The chat context
     */
    showTypingIndicator(contextId) {
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            console.error('Ergon container not found!');
            return;
        }
        
        // Get the chat messages container
        const chatMessages = container.querySelector(`#${contextId}-messages`);
        if (!chatMessages) return;
        
        // Check if typing indicator already exists
        if (chatMessages.querySelector('[data-typing="true"]')) {
            return;
        }
        
        // Create typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'ergon__message ergon__message--typing';
        typingDiv.setAttribute('data-typing', 'true');
        typingDiv.innerHTML = `
            <div class="ergon__message-content">
                <div class="ergon__message-text">Processing...</div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    /**
     * Hide typing indicator for a specific context
     * @param {string} contextId - The chat context
     */
    hideTypingIndicator(contextId) {
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            console.error('Ergon container not found!');
            return;
        }
        
        // Get the chat messages container
        const chatMessages = container.querySelector(`#${contextId}-messages`);
        if (!chatMessages) return;
        
        // Remove typing indicators
        const typingIndicators = chatMessages.querySelectorAll('[data-typing="true"]');
        typingIndicators.forEach(indicator => indicator.remove());
    }
    
    /**
     * Load agent data from the backend
     */
    loadAgentData() {
        // In a real implementation, this would fetch data from the backend
        console.log('Loading agent data');
        
        // Send a command to request agent data if tektonUI exists
        if (window.tektonUI && typeof tektonUI.sendCommand === 'function') {
            tektonUI.sendCommand('get_agents', {});
        }
    }
    
    /**
     * Simple logging function
     * @param {string} level - Log level ('debug', 'info', 'warn', 'error')
     * @param {string} message - The message to log
     */
    log(level, message) {
        // Only log if level is at or above configured level
        const levels = { debug: 0, info: 1, warn: 2, error: 3 };
        if (levels[level] >= levels[this.logLevel]) {
            console.log(`[Ergon:${level}] ${message}`);
        }
    }
    
    /**
     * Handle incoming messages
     * @param {Object} message - The message object
     */
    receiveMessage(message) {
        console.log('Received message in Ergon component:', message);
        
        // Handle different message types
        if (message.type === 'RESPONSE') {
            const payload = message.payload || {};
            
            // Handle chat responses
            if (payload.message && payload.context) {
                this.handleChatResponse(payload.message, payload.context);
            }
            // Handle agent list responses
            else if (payload.agents) {
                // Update agent list
                this.updateAgentList(payload.agents);
            } 
            // Handle agent creation response
            else if (payload.agent_created) {
                // Add new agent to list
                this.addAgentToList(payload.agent_created);
            }
            // Handle general responses
            else if (payload.response) {
                // Find the Ergon container (scope all DOM operations to this container)
                const container = document.querySelector('.ergon');
                if (!container) {
                    console.error('Ergon container not found!');
                    return;
                }
                
                // If we have a active chat tab, show response there
                const activeTab = container.querySelector('.ergon__tab--active');
                if (activeTab) {
                    const tabId = activeTab.getAttribute('data-tab');
                    if (tabId === 'ergon' || tabId === 'awt-team' || tabId === 'mcp') {
                        const chatMessages = container.querySelector(`#${tabId}-messages`);
                        if (chatMessages) {
                            // Add CI message to chat
                            const responseDiv = document.createElement('div');
                            responseDiv.className = 'ergon__message ergon__message--ai';
                            responseDiv.innerHTML = `
                                <div class="ergon__message-content">
                                    <div class="ergon__message-text">${payload.response}</div>
                                    <div class="ergon__message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                                </div>
                            `;
                            
                            chatMessages.appendChild(responseDiv);
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                        }
                    }
                }
            }
        } 
        // Handle typing indicators and status updates
        else if (message.type === 'UPDATE') {
            const payload = message.payload || {};
            
            // Handle typing status
            if (payload.status === 'typing') {
                const context = payload.context || '';
                
                if (context === 'ergon' || context === 'awt-team' || context === 'mcp') {
                    if (payload.isTyping) {
                        this.showTypingIndicator(context);
                    } else {
                        this.hideTypingIndicator(context);
                    }
                }
            }
            // Handle agent status updates
            else if (payload.agent_status) {
                // Update agent status
                this.updateAgentStatus(payload.agent_status);
            }
        }
    }
    
    /**
     * Handle chat responses from AI
     * @param {string} message - The message text
     * @param {string} context - The chat context
     */
    handleChatResponse(message, context) {
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            console.error('Ergon container not found!');
            return;
        }
        
        // Hide typing indicator if still showing
        this.hideTypingIndicator(context);
        
        // Get the chat messages container
        const chatMessages = container.querySelector(`#${context}-messages`);
        if (!chatMessages) return;
        
        // Add CI message to chat
        const responseDiv = document.createElement('div');
        responseDiv.className = 'ergon__message ergon__message--ai';
        responseDiv.innerHTML = `
            <div class="ergon__message-content">
                <div class="ergon__message-text">${message}</div>
                <div class="ergon__message-time">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;
        
        chatMessages.appendChild(responseDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    /**
     * Update the agent list with data from the backend
     * @param {Array} agents - The list of agents
     */
    updateAgentList(agents) {
        // This would update the agent list in a real implementation
        console.log('Would update agent list with:', agents);
        
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            console.error('Ergon container not found!');
            return;
        }
        
        // Get the agents container
        const agentsContainer = container.querySelector('.ergon__agent-grid');
        if (!agentsContainer) return;
        
        // Clear existing agents
        agentsContainer.innerHTML = '';
        
        // Add each agent
        agents.forEach(agent => {
            const agentCard = document.createElement('div');
            agentCard.className = 'ergon__agent-card';
            agentCard.innerHTML = `
                <div class="ergon__agent-header">
                    <div class="ergon__agent-name">${agent.name}</div>
                    <div class="ergon__agent-status ${agent.status === 'active' ? 'ergon__agent-status--active' : ''}"></div>
                </div>
                <div class="ergon__agent-description">
                    ${agent.description || 'No description available.'}
                </div>
                <div class="ergon__agent-actions">
                    <button class="ergon__agent-action-button" data-action="run">Run</button>
                    <button class="ergon__agent-action-button" data-action="delete">Delete</button>
                </div>
            `;
            
            agentsContainer.appendChild(agentCard);
        });
        
        // Re-attach event listeners
        this.setupEventListeners();
    }
    
    /**
     * Add a new agent to the list
     * @param {Object} agent - The agent data
     */
    addAgentToList(agent) {
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            console.error('Ergon container not found!');
            return;
        }
        
        // Get the agents container
        const agentsContainer = container.querySelector('.ergon__agent-grid');
        if (!agentsContainer) return;
        
        // Create agent card
        const agentCard = document.createElement('div');
        agentCard.className = 'ergon__agent-card';
        agentCard.innerHTML = `
            <div class="ergon__agent-header">
                <div class="ergon__agent-name">${agent.name}</div>
                <div class="ergon__agent-status"></div>
            </div>
            <div class="ergon__agent-description">
                ${agent.description || 'No description available.'}
            </div>
            <div class="ergon__agent-actions">
                <button class="ergon__agent-action-button" data-action="run">Run</button>
                <button class="ergon__agent-action-button" data-action="delete">Delete</button>
            </div>
        `;
        
        // Add to container
        agentsContainer.appendChild(agentCard);
        
        // Add event listeners to the new buttons
        const runButton = agentCard.querySelector('[data-action="run"]');
        const deleteButton = agentCard.querySelector('[data-action="delete"]');
        
        if (runButton) {
            runButton.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent event bubbling to card
                
                // Send run agent command
                if (window.tektonUI && typeof tektonUI.sendCommand === 'function') {
                    tektonUI.sendCommand('run_agent', {
                        agent_name: agent.name
                    });
                } else {
                    console.log('Running agent:', agent.name);
                }
                
                // Update status indicator
                const statusIndicator = agentCard.querySelector('.ergon__agent-status');
                if (statusIndicator) {
                    statusIndicator.classList.add('ergon__agent-status--active');
                }
            });
        }
        
        if (deleteButton) {
            deleteButton.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent event bubbling to card
                
                if (confirm(`Are you sure you want to delete the agent "${agent.name}"?`)) {
                    // Send delete agent command
                    if (window.tektonUI && typeof tektonUI.sendCommand === 'function') {
                        tektonUI.sendCommand('delete_agent', {
                            agent_name: agent.name
                        });
                    } else {
                        console.log('Deleting agent:', agent.name);
                    }
                    
                    // Remove the card with animation
                    agentCard.style.opacity = '0';
                    setTimeout(() => {
                        agentCard.remove();
                    }, 300);
                }
            });
        }
    }
    
    /**
     * Update an agent's status
     * @param {Object} status - The agent status data
     */
    updateAgentStatus(status) {
        if (!status || !status.agent_name) return;
        
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            console.error('Ergon container not found!');
            return;
        }
        
        // Find the agent card by name
        const agentCards = container.querySelectorAll('.ergon__agent-card');
        agentCards.forEach(card => {
            const nameElement = card.querySelector('.ergon__agent-name');
            if (nameElement && nameElement.textContent === status.agent_name) {
                // Update status
                const statusIndicator = card.querySelector('.ergon__agent-status');
                if (statusIndicator) {
                    if (status.status === 'active') {
                        statusIndicator.classList.add('ergon__agent-status--active');
                    } else {
                        statusIndicator.classList.remove('ergon__agent-status--active');
                    }
                }
            }
        });
    }
}

// Create global instance
window.ergonComponent = new ErgonComponent();