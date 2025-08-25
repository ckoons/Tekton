/**
 * DEPRECATED: This file will be removed after CSS-first migration is verified
 * Enhanced Terminal Chat Manager
 * 
 * Features:
 * - Persistent chat history with localStorage
 * - Hermes message bus integration
 * - Support for Greek/functional naming based on settings
 * - Terminal registration with message capabilities
 */

console.log('[FILE_TRACE] Loading: terminal-chat-enhanced.js');
class EnhancedTerminalChat {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = null;
        this.options = {
            showTimestamps: true,
            showTypingIndicator: true,
            markdownFormatting: true,
            contextId: null, // ergon, awt-team, agora
            maxHistoryEntries: 50,
            ...options
        };
        this.history = [];
        this.isTyping = false;
        this.typingTimer = null;
        this.registeredWithHermes = false;
        
        // Bind methods
        this.handleHermesMessage = this.handleHermesMessage.bind(this);
    }
    
    /**
     * Initialize the enhanced terminal chat
     * @param {Object} [options] - Additional initialization options
     * @returns {EnhancedTerminalChat} This instance for chaining
     */
    init(options = {}) {
        // Merge options
        Object.assign(this.options, options);
        
        // Find the container
        this.container = document.getElementById(this.containerId);
        if (!this.container) {
            console.error(`Terminal chat container #${this.containerId} not found`);
            return this;
        }
        
        console.log(`Initializing enhanced terminal chat for ${this.options.contextId}`);
        
        // Initialize UI
        this.setupUI();
        
        // Load history
        this.loadHistory();
        
        // Register with Hermes if available
        this.registerWithHermes();
        
        // Listen for settings changes
        this.listenForSettingsChanges();
        
        return this;
    }
    
    /**
     * Set up the UI elements
     */
    setupUI() {
        // Add listeners to the input field
        const input = this.container.querySelector('.terminal-chat-input');
        if (input) {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const message = input.value.trim();
                    if (message) {
                        this.sendMessage(message);
                        input.value = '';
                    }
                }
            });
            
            // Auto-focus when clicked
            this.container.addEventListener('click', () => {
                input.focus();
            });
        }
        
        // Add listener to clear chat button if present
        const clearButton = document.querySelector(`#clear-${this.options.contextId}-chat`);
        if (clearButton) {
            clearButton.addEventListener('click', () => {
                this.clearChat();
            });
        }
    }
    
    /**
     * Register with Hermes message bus
     */
    registerWithHermes() {
        if (!window.hermesConnector) {
            console.log('Hermes connector not available for terminal registration');
            return;
        }
        
        // Skip if already registered
        if (this.registeredWithHermes) return;
        
        // Get contextId
        const contextId = this.options.contextId;
        if (!contextId) {
            console.error('Cannot register with Hermes: no contextId provided');
            return;
        }
        
        // Register as message recipient
        window.hermesConnector.registerTerminal(contextId, {
            displayName: this.getDisplayName(),
            type: 'chat-terminal',
            capabilities: ['receive-messages', 'send-messages', 'user-input']
        });
        
        // Listen for incoming messages
        window.hermesConnector.addEventListener('messageReceived', this.handleHermesMessage);
        
        this.registeredWithHermes = true;
        console.log(`Terminal ${contextId} registered with Hermes`);
    }
    
    /**
     * Listen for settings changes
     */
    listenForSettingsChanges() {
        if (!window.settingsManager) return;
        
        // Listen for naming convention changes
        window.settingsManager.addEventListener('namesChanged', () => {
            // Update display name with Hermes if registered
            if (this.registeredWithHermes && window.hermesConnector) {
                const contextId = this.options.contextId;
                window.hermesConnector.registerTerminal(contextId, {
                    displayName: this.getDisplayName(),
                    type: 'chat-terminal',
                    capabilities: ['receive-messages', 'send-messages', 'user-input']
                });
            }
            
            // Update welcome message if applicable
            this.updateWelcomeMessage();
        });
        
        // Listen for chat history being cleared
        window.settingsManager.addEventListener('chatHistoryCleared', () => {
            this.clearChat(true); // true = don't save the clear action
        });
        
        // Update max history entries setting
        if (window.settingsManager.settings.maxChatHistoryEntries) {
            this.options.maxHistoryEntries = window.settingsManager.settings.maxChatHistoryEntries;
        }
    }
    
    /**
     * Get the appropriate display name based on settings
     * @returns {string} Display name
     */
    getDisplayName() {
        if (!window.settingsManager) {
            return this.options.contextId;
        }
        
        return window.settingsManager.getChatTabLabel(this.options.contextId);
    }
    
    /**
     * Update the welcome message based on current settings
     */
    updateWelcomeMessage() {
        if (!window.settingsManager) return;
        
        // Find the first system message (usually welcome)
        const welcomeMsg = this.container.querySelector('.chat-message.system');
        if (welcomeMsg) {
            const messageText = welcomeMsg.querySelector('.message-text');
            if (messageText) {
                // Get context-appropriate welcome message
                const newWelcome = window.settingsManager.getChatWelcomeMessage(this.options.contextId);
                messageText.textContent = newWelcome;
            }
        }
    }
    
    /**
     * Handle incoming message from Hermes
     * @param {Object} event - Message event from Hermes
     */
    handleHermesMessage(event) {
        const { sender, recipients, message } = event;
        
        // Check if this terminal is a recipient
        const contextId = this.options.contextId;
        if (!recipients.includes(contextId)) return;
        
        console.log(`Terminal ${contextId} received message from ${sender}:`, message);
        
        // Add the message to the chat
        this.addAIMessage(message.text || message.content || JSON.stringify(message), sender);
    }
    
    /**
     * Send a message from the user
     * @param {string} text - Message text
     */
    sendMessage(text) {
        // Add to UI
        this.addUserMessage(text);
        
        // Get context ID
        const contextId = this.options.contextId;
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Send message to LLM if Hermes connector is available
        if (window.hermesConnector) {
            console.log(`Sending message to LLM via Hermes: ${text}`);
            
            // Use LLM integration
            window.hermesConnector.sendLLMMessage(contextId, text, true, {
                // Additional options can be configured here
                temperature: 0.7,
                // model: "anthropic/claude-3-sonnet-20240229", // Can be configured based on settings
            });
            
            // Listen for stream events if not already listening
            if (!this._streamListenersAttached) {
                this._attachStreamListeners();
            }
        } else {
            console.log(`Hermes not available, message handled locally: ${text}`);
            
            // Simulate response locally (temporary until real backend)
            setTimeout(() => {
                this.hideTypingIndicator();
                this.addAIMessage(`I received your message: "${text}".<br>How can I assist you further?`, contextId);
            }, 1500);
        }
        
        // Save to history
        this.saveHistory();
    }
    
    /**
     * Attach stream event listeners
     * @private
     */
    _attachStreamListeners() {
        if (!window.hermesConnector) return;
        
        const contextId = this.options.contextId;
        
        // Listen for typing started events
        window.hermesConnector.addEventListener('typingStarted', (data) => {
            if (data.contextId === contextId) {
                this.showTypingIndicator();
            }
        });
        
        // Listen for typing ended events
        window.hermesConnector.addEventListener('typingEnded', (data) => {
            if (data.contextId === contextId) {
                this.hideTypingIndicator();
            }
        });
        
        // Listen for stream chunks
        window.hermesConnector.addEventListener('streamChunk', (data) => {
            if (data.contextId === contextId) {
                this._handleStreamChunk(data.chunk);
            }
        });
        
        // Mark listeners as attached
        this._streamListenersAttached = true;
    }
    
    /**
     * Handle a streaming response chunk
     * @param {string} chunk - Text chunk
     * @private
     */
    _handleStreamChunk(chunk) {
        const messagesContainer = this.container.querySelector('.terminal-chat-messages');
        if (!messagesContainer) return;
        
        // Find or create the streaming message element
        let streamMsgEl = messagesContainer.querySelector('.llm-streaming-message');
        if (!streamMsgEl) {
            // Hide any typing indicators first
            this.hideTypingIndicator();
            
            // Create new message element
            streamMsgEl = document.createElement('div');
            streamMsgEl.className = 'chat-message agent llm-streaming-message';
            streamMsgEl.innerHTML = `
                <div class="message-content">
                    <div class="message-text"></div>
                    <div class="message-time">${this.formatTimestamp(new Date().toISOString())}</div>
                </div>
            `;
            
            messagesContainer.appendChild(streamMsgEl);
        }
        
        // Append chunk to the message text
        const textEl = streamMsgEl.querySelector('.message-text');
        if (textEl) {
            textEl.innerHTML += chunk;
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
    
    /**
     * Get appropriate recipients based on context
     * @param {string} contextId - The context ID
     * @returns {Array} Array of recipient IDs
     */
    getRecipients(contextId) {
        switch(contextId) {
            case 'ergon':
                // Direct to Ergon only
                return ['ergon'];
            case 'awt-team':
                // Team chat goes to multiple specialists
                return ['agent-specialist', 'workflow-specialist', 'tool-specialist'];
            case 'agora':
                // Agora goes to all CI components
                return ['broadcast'];
            default:
                return [contextId];
        }
    }
    
    /**
     * Load chat history from storage
     */
    loadHistory() {
        if (!window.storageManager) return;
        
        // Get storage settings
        const historyEnabled = window.settingsManager ? 
            window.settingsManager.settings.chatHistoryEnabled !== false : true;
        
        if (!historyEnabled) {
            console.log('Chat history disabled in settings');
            return;
        }
        
        // Get the context ID
        const contextId = this.options.contextId;
        if (!contextId) return;
        
        // Try to load history from storage
        const historyKey = `terminal_chat_history_${contextId}`;
        const savedHistory = window.storageManager.getItem(historyKey);
        
        if (savedHistory) {
            try {
                const history = JSON.parse(savedHistory);
                
                // Show in the UI
                this.displaySavedHistory(history);
                
                console.log(`Loaded ${history.length} messages from history for ${contextId}`);
            } catch (e) {
                console.error(`Error parsing chat history for ${contextId}:`, e);
            }
        } else {
            console.log(`No saved history for ${contextId}`);
        }
    }
    
    /**
     * Save chat history to storage
     */
    saveHistory() {
        if (!window.storageManager) return;
        
        // Get storage settings
        const historyEnabled = window.settingsManager ? 
            window.settingsManager.settings.chatHistoryEnabled !== false : true;
        
        if (!historyEnabled) {
            console.log('Chat history disabled in settings, not saving');
            return;
        }
        
        // Get the context ID
        const contextId = this.options.contextId;
        if (!contextId) return;
        
        // Get messages from the UI
        const messages = this.collectMessages();
        
        // Limit to maximum entries
        const maxEntries = this.options.maxHistoryEntries;
        const limitedMessages = messages.slice(-maxEntries);
        
        // Save to storage
        const historyKey = `terminal_chat_history_${contextId}`;
        window.storageManager.setItem(historyKey, JSON.stringify(limitedMessages));
        
        console.log(`Saved ${limitedMessages.length} messages to history for ${contextId}`);
    }
    
    /**
     * Collect messages from the UI into a serializable format
     * @returns {Array} Array of message objects
     */
    collectMessages() {
        const messages = [];
        
        // Get all message elements
        const messageElements = this.container.querySelectorAll('.chat-message');
        
        messageElements.forEach(el => {
            // Skip typing indicators
            if (el.classList.contains('typing')) return;
            
            // Determine message type
            let type = 'system';
            if (el.classList.contains('user')) type = 'user';
            else if (el.classList.contains('agent')) type = 'ai';
            
            // Get content
            const contentEl = el.querySelector('.message-text');
            if (!contentEl) return;
            
            // Get sender for CI messages
            let sender = null;
            if (type === 'ai') {
                const senderMatch = contentEl.innerHTML.match(/<strong>([^<]+):<\/strong>/);
                if (senderMatch) {
                    sender = senderMatch[1];
                }
            }
            
            // Get timestamp if available
            const timestampEl = el.querySelector('.message-time');
            const timestamp = timestampEl ? 
                new Date().toISOString() : // Fallback to current time
                new Date().toISOString();  // Current time is default
            
            // Create message object
            messages.push({
                type,
                content: contentEl.innerHTML,
                sender,
                timestamp
            });
        });
        
        return messages;
    }
    
    /**
     * Display saved history in the UI
     * @param {Array} messages - Array of message objects
     */
    displaySavedHistory(messages) {
        // Clear existing messages except welcome
        const welcomeMsg = this.container.querySelector('.chat-message.system');
        const messagesContainer = this.container.querySelector('.terminal-chat-messages');
        
        if (messagesContainer) {
            // Keep only the welcome message
            messagesContainer.innerHTML = '';
            if (welcomeMsg) {
                messagesContainer.appendChild(welcomeMsg);
            }
            
            // Add each message
            messages.forEach(msg => {
                const { type, content, sender, timestamp } = msg;
                
                // Create message element
                const messageEl = document.createElement('div');
                messageEl.className = `chat-message ${type === 'user' ? 'user' : 'agent'}`;
                
                if (type === 'system') {
                    messageEl.classList.add('system');
                    messageEl.classList.remove('agent');
                }
                
                // Create content
                let messageContent = `
                    <div class="message-content">
                        <div class="message-text">${content}</div>
                        <div class="message-time">${this.formatTimestamp(timestamp)}</div>
                    </div>
                `;
                
                messageEl.innerHTML = messageContent;
                messagesContainer.appendChild(messageEl);
            });
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
    
    /**
     * Format a timestamp for display
     * @param {string} timestamp - ISO timestamp
     * @returns {string} Formatted time
     */
    formatTimestamp(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            return 'Unknown time';
        }
    }
    
    /**
     * Add a user message to the chat
     * @param {string} text - Message text
     */
    addUserMessage(text) {
        if (!text) return;
        
        const messagesContainer = this.container.querySelector('.terminal-chat-messages');
        if (!messagesContainer) return;
        
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = 'chat-message user';
        
        // Add message content
        messageEl.innerHTML = `
            <div class="message-content">
                <div class="message-text">${text}</div>
                <div class="message-time">${this.formatTimestamp(new Date().toISOString())}</div>
            </div>
        `;
        
        // Add to container
        messagesContainer.appendChild(messageEl);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Save to history
        this.saveHistory();
    }
    
    /**
     * Add an CI message to the chat
     * @param {string} text - Message text
     * @param {string} sender - Sender ID or name
     */
    addAIMessage(text, sender) {
        if (!text) return;
        
        // Hide typing indicator first
        this.hideTypingIndicator();
        
        const messagesContainer = this.container.querySelector('.terminal-chat-messages');
        if (!messagesContainer) return;
        
        // Format sender name
        let senderName = sender;
        if (sender === this.options.contextId) {
            senderName = '';
        } else if (sender && sender !== 'system') {
            // Try to get a nice display name
            if (window.settingsManager) {
                senderName = window.settingsManager.getComponentLabel(sender)
                    .replace(/<[^>]*>/g, '') // Remove HTML tags
                    .replace(/\s*-\s*.*$/, ''); // Remove everything after dash
            }
            
            // Add colon and strong formatting if sender provided
            if (senderName) {
                senderName = `<strong>${senderName}:</strong> `;
            }
        }
        
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = 'chat-message agent';
        
        // Set data attribute for sender
        if (sender) {
            messageEl.setAttribute('data-sender', sender);
        }
        
        // Add message content
        messageEl.innerHTML = `
            <div class="message-content">
                <div class="message-text">${senderName}${text}</div>
                <div class="message-time">${this.formatTimestamp(new Date().toISOString())}</div>
            </div>
        `;
        
        // Add to container
        messagesContainer.appendChild(messageEl);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Save to history
        this.saveHistory();
    }
    
    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        if (this.isTyping) return;
        
        const messagesContainer = this.container.querySelector('.terminal-chat-messages');
        if (!messagesContainer) return;
        
        // Create typing indicator
        const typingEl = document.createElement('div');
        typingEl.className = 'chat-message agent typing';
        
        typingEl.innerHTML = `
            <div class="message-content">
                <div class="message-text">Processing...</div>
            </div>
        `;
        
        // Add to container
        messagesContainer.appendChild(typingEl);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        this.isTyping = true;
        
        // Auto-hide after timeout (safety)
        this.typingTimer = setTimeout(() => {
            this.hideTypingIndicator();
        }, 30000); // 30 seconds max
    }
    
    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        const messagesContainer = this.container.querySelector('.terminal-chat-messages');
        if (!messagesContainer) return;
        
        // Remove typing indicators
        const typingIndicators = messagesContainer.querySelectorAll('.typing');
        typingIndicators.forEach(el => el.remove());
        
        this.isTyping = false;
        
        // Clear timeout
        if (this.typingTimer) {
            clearTimeout(this.typingTimer);
            this.typingTimer = null;
        }
    }
    
    /**
     * Clear the chat history
     * @param {boolean} [skipSave=false] - Whether to skip saving the cleared state
     */
    clearChat(skipSave = false) {
        const messagesContainer = this.container.querySelector('.terminal-chat-messages');
        if (!messagesContainer) return;
        
        // Get the welcome/system message
        const welcomeMsg = messagesContainer.querySelector('.chat-message.system');
        
        // Clear the container
        messagesContainer.innerHTML = '';
        
        // Re-add welcome message if it exists
        if (welcomeMsg) {
            messagesContainer.appendChild(welcomeMsg);
        } else {
            // Create a new welcome message
            const newWelcome = document.createElement('div');
            newWelcome.className = 'chat-message system';
            
            // Get appropriate welcome message based on settings
            let welcomeText = 'Welcome to the chat';
            if (window.settingsManager) {
                welcomeText = window.settingsManager.getChatWelcomeMessage(this.options.contextId);
            }
            
            newWelcome.innerHTML = `
                <div class="message-content">
                    <div class="message-text">${welcomeText}</div>
                    <div class="message-time">${this.formatTimestamp(new Date().toISOString())}</div>
                </div>
            `;
            
            messagesContainer.appendChild(newWelcome);
        }
        
        // Save the cleared state
        if (!skipSave) {
            this.saveHistory();
        }
    }
}

// Initialize all terminal chats when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Wait for settings to load
    setTimeout(() => {
        // Find all terminal chat containers
        const containers = [
            { id: 'ergon-chat-container', context: 'ergon' },
            { id: 'awt-team-chat-container', context: 'awt-team' },
            { id: 'agora-chat-container', context: 'agora' }
        ];
        
        // Initialize each container
        containers.forEach(container => {
            if (document.getElementById(container.id)) {
                window[`${container.context}Chat`] = new EnhancedTerminalChat(container.id, {
                    contextId: container.context
                }).init();
            }
        });
    }, 1000);
});