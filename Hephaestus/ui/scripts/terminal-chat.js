/**
 * DEPRECATED: This file will be removed after CSS-first migration is verified
 * Terminal Chat Manager
 * Enhanced terminal with CI chat capabilities for Tekton
 */

console.log('[FILE_TRACE] Loading: terminal-chat.js');
class TerminalChatManager {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = null;
        this.options = {
            showTimestamps: true,
            showTypingIndicator: true,
            markdownFormatting: true,
            ...options
        };
        this.history = {};
        this.isTyping = false;
        this.typingTimer = null;
        this.activeComponent = null;
    }
    
    /**
     * Initialize the chat terminal
     * @param {Object} [options] - Additional initialization options
     * @param {string} [options.welcomeMessage] - Custom welcome message
     * @param {string} [options.componentId] - Component ID for this chat terminal
     */
    init(options = {}) {
        this.container = document.getElementById(this.containerId);
        if (!this.container) {
            console.error(`Terminal chat container #${this.containerId} not found`);
            console.log(`Will try again to find the container when messages are added`);
            // We'll try to re-acquire the container when messages are added
        } else {
            console.log(`Container #${this.containerId} found and initialized`);
            // Add chat class to container
            this.container.classList.add('terminal-chat');
        }
        
        // If component ID provided, set it as active
        if (options.componentId) {
            this.activeComponent = options.componentId;
        }
        
        // Make the container visible
        if (this.container) {
            // Make sure the container is visible
            this.container.style.display = 'flex';
            this.container.style.flexDirection = 'column';
            this.container.style.height = '100%';
            this.container.style.overflow = 'auto';
        }
        
        // Initialize with a welcome message
        this.clear();
        
        if (options.welcomeMessage) {
            this.addSystemMessage(options.welcomeMessage);
        } else {
            this.addSystemMessage("Welcome to Tekton CI Terminal");
        }
        
        // Set up observer to handle chat stream
        this.setupStreamObserver();
        
        console.log(`Terminal Chat Manager initialized for ${this.activeComponent || 'unknown'} component`);
        
        return this; // Enable chaining
    }
    
    /**
     * Setup mutation observer for stream animations
     * This enables us to simulate typing animations for messages
     */
    setupStreamObserver() {
        // Store reference to this for callbacks
        const self = this;
        
        // Create observer to watch for added messages
        this.streamObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach((node) => {
                        // Check if this is an CI message
                        if (node.classList && node.classList.contains('ai-message')) {
                            // Add animation to make it look like it's streaming in
                            if (!node.classList.contains('animated')) {
                                node.classList.add('animated');
                                // More complex animations could be added here
                            }
                        }
                    });
                }
            });
        });
        
        // Start observing the chat container
        if (this.container) {
            this.streamObserver.observe(this.container, { 
                childList: true,
                subtree: true
            });
        }
    }
    
    /**
     * Add a user message to the chat
     * @param {string} text - User message text
     */
    addUserMessage(text) {
        this.addMessage('user', text);
    }
    
    /**
     * Add an CI message to the chat
     * @param {string} text - CI message text
     * @param {string} componentId - Component ID (for styling)
     */
    addAIMessage(text, componentId = null) {
        this.addMessage('ai', text, componentId);
        this.hideTypingIndicator();
    }
    
    /**
     * Add a system message to the chat
     * @param {string} text - System message text
     */
    addSystemMessage(text) {
        this.addMessage('system', text);
    }
    
    /**
     * Add a message to the chat
     * @param {string} type - Message type (user, ai, system)
     * @param {string} text - Message text
     * @param {string} componentId - Component ID (optional)
     */
    addMessage(type, text, componentId = null) {
        if (!this.container) {
            console.error(`Cannot add message, container not found: #${this.containerId}`);
            // Try to get the container again - it might have been added to the DOM after initialization
            this.container = document.getElementById(this.containerId);
            if (!this.container) {
                console.error(`Still cannot find container: #${this.containerId}`);
                return;
            }
            console.log(`Container found on retry: #${this.containerId}`);
        }
        
        // Set active component if not already set
        if (!this.activeComponent && componentId) {
            this.activeComponent = componentId;
        }
        
        // Use passed componentId or the active one
        componentId = componentId || this.activeComponent || 'unknown';
        
        console.log(`Adding ${type} message to ${componentId} chat:`, text.substring(0, 30) + (text.length > 30 ? '...' : ''));
        
        // Create message container
        const messageEl = document.createElement('div');
        messageEl.className = `chat-message ${type}-message`;
        
        // Add component data attribute for CI messages to enable component-specific styling
        if (type === 'ai' && componentId) {
            messageEl.setAttribute('data-component', componentId);
        }
        
        // Record message timestamp
        const msgTimestamp = new Date();
        messageEl.setAttribute('data-timestamp', msgTimestamp.toISOString());
        
        let messageContent = '';
        
        // Add header for user and CI messages
        if (type === 'user' || type === 'ai') {
            const sender = type === 'user' ? 'You' : componentId.charAt(0).toUpperCase() + componentId.slice(1);
            
            const header = document.createElement('div');
            header.className = 'message-header';
            header.innerHTML = `
                <span class="message-sender">${sender}</span>
                ${this.options.showTimestamps ? `<span class="message-timestamp">${this.getFormattedTime(msgTimestamp)}</span>` : ''}
            `;
            messageEl.appendChild(header);
        }
        
        // Create and format message content
        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        
        // Format the text (apply markdown if enabled)
        if (this.options.markdownFormatting) {
            contentEl.innerHTML = this.formatMarkdown(this.sanitizeHtml(text));
        } else {
            contentEl.textContent = text;
        }
        
        messageEl.appendChild(contentEl);
        
        // Add timestamp for system messages (which don't have headers)
        if (type === 'system' && this.options.showTimestamps) {
            const timestamp = document.createElement('div');
            timestamp.className = 'message-timestamp';
            timestamp.textContent = this.getFormattedTime(msgTimestamp);
            messageEl.appendChild(timestamp);
        }
        
        // Add to the container
        this.container.appendChild(messageEl);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Add to history for the current component
        this.addToHistory(componentId, {
            type: type,
            text: text,
            timestamp: new Date().toISOString()
        });
        
        console.log(`Message added successfully to ${componentId} chat`);
    }
    
    /**
     * Show typing indicator
     * @param {string} componentId - Component ID
     */
    showTypingIndicator(componentId = null) {
        if (!this.container || this.isTyping) return;
        
        // Use passed componentId or the active one
        componentId = componentId || this.activeComponent;
        if (!componentId) return;
        
        // Remove any existing typing indicators
        this.hideTypingIndicator();
        
        // Create typing indicator
        const typingEl = document.createElement('div');
        typingEl.className = 'chat-message typing-indicator';
        typingEl.innerHTML = `
            <div class="typing-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
        `;
        
        // Add to container
        this.container.appendChild(typingEl);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Set typing status
        this.isTyping = true;
    }
    
    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        if (!this.container) return;
        
        // Remove any existing typing indicators
        const typingIndicators = this.container.querySelectorAll('.typing-indicator');
        typingIndicators.forEach(el => el.remove());
        
        // Reset typing status
        this.isTyping = false;
        
        // Clear any typing timers
        if (this.typingTimer) {
            clearTimeout(this.typingTimer);
            this.typingTimer = null;
        }
    }
    
    /**
     * Set the active component ID
     * @param {string} componentId - Component ID
     */
    setActiveComponent(componentId) {
        this.activeComponent = componentId;
    }
    
    /**
     * Format text with markdown-like syntax
     * @param {string} text - Text to format
     * @returns {string} Formatted HTML
     */
    formatMarkdown(text) {
        if (!text) return '';
        
        // Process code blocks with language support
        let formatted = text.replace(/```([a-z]*)\n([\s\S]*?)```/g, (match, language, code) => {
            // Add language class if specified
            const langClass = language ? ` class="language-${language}"` : '';
            return `<pre><code${langClass}>${this.escapeHtml(code)}</code></pre>`;
        });
        
        // Replace ```code``` without language specification
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Replace `code` with <code>code</code>
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Replace **bold** with <strong>bold</strong>
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Replace *italic* with <em>italic</em>
        formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        // Process unordered lists
        formatted = formatted.replace(/^\s*[-*]\s+(.+)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        // Process ordered lists
        formatted = formatted.replace(/^\s*(\d+)\.\s+(.+)$/gm, '<li>$2</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>');
        
        // Process headers (h1, h2, h3)
        formatted = formatted.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
        formatted = formatted.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
        formatted = formatted.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');
        
        // Convert line breaks to <br>
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Convert URLs to links
        formatted = formatted.replace(
            /(https?:\/\/[^\s]+)/g, 
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        return formatted;
    }
    
    /**
     * Properly escape HTML to prevent XSS when using in code blocks
     * @param {string} html - HTML to escape
     * @returns {string} Escaped HTML
     */
    escapeHtml(html) {
        const escapeMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        
        return html.replace(/[&<>"']/g, match => escapeMap[match]);
    }
    
    /**
     * Sanitize HTML to prevent injection
     * @param {string} html - HTML string to sanitize
     * @returns {string} Sanitized HTML
     */
    sanitizeHtml(html) {
        const temp = document.createElement('div');
        temp.textContent = html;
        return temp.innerHTML;
    }
    
    /**
     * Get formatted time for timestamps
     * @returns {string} Formatted time (HH:MM AM/PM)
     */
    getFormattedTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    /**
     * Scroll to the bottom of the chat container
     */
    scrollToBottom() {
        if (this.container) {
            this.container.scrollTop = this.container.scrollHeight;
        }
    }
    
    /**
     * Clear the terminal
     */
    clear() {
        // If container isn't available, try to find it again
        if (!this.container) {
            this.container = document.getElementById(this.containerId);
        }
        
        if (this.container) {
            console.log(`Clearing chat container #${this.containerId}`);
            this.container.innerHTML = '';
        } else {
            console.error(`Cannot clear chat - container #${this.containerId} not found`);
        }
    }
    
    /**
     * Add an entry to the terminal history for a specific component
     * @param {string} componentId - Component ID
     * @param {Object} entry - History entry with type and text properties
     */
    addToHistory(componentId, entry) {
        if (!this.history[componentId]) {
            this.history[componentId] = [];
        }
        
        this.history[componentId].push(entry);
        
        // Save history to localStorage if storage manager is available
        this.saveHistory(componentId);
    }
    
    /**
     * Save terminal history to localStorage
     * @param {string} componentId - Component ID
     */
    saveHistory(componentId) {
        if (window.storageManager && this.history[componentId]) {
            storageManager.setItem(`terminal_chat_history_${componentId}`, JSON.stringify(this.history[componentId]));
        }
    }
    
    /**
     * Load terminal history for a component
     * @param {string} componentId - Component ID
     */
    loadHistory(componentId) {
        if (!window.storageManager) return;
        
        // Set active component
        this.activeComponent = componentId;
        
        // Clear terminal
        this.clear();
        
        // Try to load from memory first
        if (this.history[componentId] && this.history[componentId].length > 0) {
            this.replayHistory(this.history[componentId]);
            return;
        }
        
        // Otherwise load from localStorage
        const savedHistory = storageManager.getItem(`terminal_chat_history_${componentId}`);
        if (savedHistory) {
            try {
                const historyEntries = JSON.parse(savedHistory);
                this.history[componentId] = historyEntries;
                this.replayHistory(historyEntries);
            } catch (e) {
                console.error('Error loading terminal history:', e);
                this.addSystemMessage('Error loading conversation history');
            }
        } else {
            // If no history, show appropriate welcome message based on component
            this.showWelcomeMessage(componentId);
        }
    }
    
    /**
     * Show a welcome message appropriate for the component
     * @param {string} componentId - Component ID
     */
    showWelcomeMessage(componentId) {
        // Default welcome message
        let welcomeMessage = `Welcome to ${componentId.charAt(0).toUpperCase() + componentId.slice(1)} CI assistant`;
        
        // Component-specific welcome messages
        const welcomeMessages = {
            'ergon': 'Welcome to Ergon CI Assistant! I can help you with agent creation, configuration, and management.',
            'awt-team': 'Welcome to Advanced Workflow Tools! I can help you design, implement, and manage complex workflows.',
            'tekton': 'Welcome to Tekton Projects! I can help you manage your engineering projects and resources.',
            'prometheus': 'Welcome to Prometheus Planning! I can assist with schedule planning and roadmap development.',
            'athena': 'Welcome to Athena Knowledge Assistant! I can help you search and organize knowledge.',
            'engram': 'Welcome to Engram Memory System! I can help you store and retrieve information across sessions.',
            'rhetor': 'Welcome to Rhetor Context Manager! I can help maintain contextual information across your projects.'
        };
        
        // Use specific message if available
        if (welcomeMessages[componentId]) {
            welcomeMessage = welcomeMessages[componentId];
        }
        
        // Add the welcome message
        this.addSystemMessage(welcomeMessage);
        
        // For Ergon and AWT-Team, add extra helpful information
        if (componentId === 'ergon') {
            setTimeout(() => {
                this.addAIMessage("I can help you with the following tasks:\n\n- Creating new agents for various purposes\n- Configuring agent properties and behaviors\n- Managing agent lifecycles\n- Setting up agent communication patterns\n- Monitoring agent performance\n\nJust let me know what you'd like to do!", 'ergon');
            }, 1000);
        } else if (componentId === 'awt-team') {
            setTimeout(() => {
                this.addAIMessage("The Advanced Workflow Tools team specializes in:\n\n- Creating complex multi-agent workflows\n- Designing event-driven processes\n- Implementing conditional branching logic\n- Handling error recovery in distributed systems\n- Optimizing parallel task execution\n\nHow can I assist with your workflow needs?", 'awt-team');
            }, 1000);
        }
    }
    
    /**
     * Replay a sequence of history entries in the terminal
     * @param {Array} entries - History entries to replay
     */
    replayHistory(entries) {
        if (!entries || !Array.isArray(entries)) return;
        
        // Only replay the last 50 entries to avoid overwhelming the terminal
        const recentEntries = entries.slice(-50);
        
        recentEntries.forEach(entry => {
            if (entry && entry.text) {
                if (entry.type === 'user') {
                    this.addUserMessage(entry.text);
                } else if (entry.type === 'ai') {
                    // Use the active component ID for CI messages
                    this.addAIMessage(entry.text, this.activeComponent);
                } else if (entry.type === 'system') {
                    this.addSystemMessage(entry.text);
                }
            }
        });
    }
    
    /**
     * Get formatted time for timestamps
     * @param {Date|string} [date] - Optional date object or ISO string to format (defaults to now)
     * @returns {string} Formatted time (HH:MM AM/PM)
     */
    getFormattedTime(date = null) {
        const timeDate = date instanceof Date ? date : 
                       typeof date === 'string' ? new Date(date) : 
                       new Date();
        
        return timeDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
}