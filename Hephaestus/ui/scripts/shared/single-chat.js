/**
 * Unified Single Chat Component
 * Provides consistent single AI chat functionality across all Tekton components
 * Uses HTML injection pattern, CSS-first approach, no DOM manipulation
 */

window.SingleChat = {
    // Component configuration mapping
    config: {
        'terma': { aiName: 'terma', displayName: 'Terma' },
        'budget': { aiName: 'penia', displayName: 'Penia' },
        'numa': { aiName: 'numa', displayName: 'Numa' },
        'athena': { aiName: 'athena', displayName: 'Athena' },
        'apollo': { aiName: 'apollo', displayName: 'Apollo' },
        'rhetor': { aiName: 'rhetor', displayName: 'Rhetor' },
        'hermes': { aiName: 'hermes', displayName: 'Hermes' },
        'sophia': { aiName: 'sophia', displayName: 'Sophia' },
        'noesis': { aiName: 'noesis', displayName: 'Noesis' },
        'metis': { aiName: 'metis', displayName: 'Metis' },
        'harmonia': { aiName: 'harmonia', displayName: 'Harmonia' },
        'prometheus': { aiName: 'prometheus', displayName: 'Prometheus' },
        'ergon': { aiName: 'ergon', displayName: 'Ergon' },
        'telos': { aiName: 'telos', displayName: 'Telos' },
        'synthesis': { aiName: 'synthesis', displayName: 'Synthesis' },
        'engram': { aiName: 'engram', displayName: 'Engram' },
        'codex': { aiName: 'codex', displayName: 'Codex' }
    },
    
    /**
     * Initialize single chat for a component
     * @param {HTMLElement} containerEl - The chat messages container
     * @param {string} componentName - Component identifier (e.g., 'terma', 'budget')
     * @param {string} cssPrefix - CSS class prefix (e.g., 'terma', 'budget')
     */
    init(containerEl, componentName, cssPrefix) {
        if (!containerEl) {
            console.error('[SingleChat] Container element not found');
            return;
        }
        
        // Store configuration on the element for later use
        containerEl.setAttribute('data-single-chat', 'true');
        containerEl.setAttribute('data-component-name', componentName);
        containerEl.setAttribute('data-css-prefix', cssPrefix);
        
        console.log(`[SingleChat] Initialized for ${componentName}`);
    },
    
    /**
     * Send a message to the AI
     * @param {HTMLElement} containerEl - The chat messages container
     * @param {string} message - The message to send
     */
    async sendMessage(containerEl, message) {
        if (!containerEl || !message || !message.trim()) {
            return;
        }
        
        const componentName = containerEl.getAttribute('data-component-name');
        const cssPrefix = containerEl.getAttribute('data-css-prefix');
        const config = this.config[componentName];
        
        if (!config) {
            console.error(`[SingleChat] No configuration found for component: ${componentName}`);
            return;
        }
        
        // Get existing content (preserve welcome message)
        const existingContent = containerEl.innerHTML;
        
        // Add user message using innerHTML
        let userMessageHtml;
        if (cssPrefix === 'chat-message') {
            // Terma uses different CSS structure
            userMessageHtml = `
                <div class="chat-message user-message">
                    ${this.escapeHtml(message)}
                </div>
            `;
        } else {
            userMessageHtml = `
                <div class="${cssPrefix}__message ${cssPrefix}__message--user">
                    <div class="${cssPrefix}__message-content">
                        <div class="${cssPrefix}__message-text">${this.escapeHtml(message)}</div>
                    </div>
                </div>
            `;
        }
        
        containerEl.innerHTML = existingContent + userMessageHtml;
        containerEl.scrollTop = containerEl.scrollHeight;
        
        // Show processing message
        if (window.AIChat && window.AIChat.showProcessingMessage) {
            window.AIChat.showProcessingMessage(containerEl, "Processing", cssPrefix);
        }
        
        try {
            // Send message to AI
            const response = await window.AIChat.sendMessage(config.aiName, message);
            
            // Remove processing message
            if (window.AIChat && window.AIChat.hideProcessingMessage) {
                window.AIChat.hideProcessingMessage(containerEl);
            }
            
            // Add AI response
            let aiMessageHtml;
            if (cssPrefix === 'chat-message') {
                // Terma uses different CSS structure
                aiMessageHtml = `
                    <div class="chat-message ai-message">
                        <strong>${config.displayName}:</strong> ${this.escapeHtml(response.content || response)}
                    </div>
                `;
            } else {
                aiMessageHtml = `
                    <div class="${cssPrefix}__message ${cssPrefix}__message--ai">
                        <div class="${cssPrefix}__message-content">
                            <div class="${cssPrefix}__message-text">
                                <strong>${config.displayName}:</strong> ${this.escapeHtml(response.content || response)}
                            </div>
                        </div>
                    </div>
                `;
            }
            
            containerEl.innerHTML = containerEl.innerHTML + aiMessageHtml;
            containerEl.scrollTop = containerEl.scrollHeight;
            
        } catch (error) {
            // Remove processing message
            if (window.AIChat && window.AIChat.hideProcessingMessage) {
                window.AIChat.hideProcessingMessage(containerEl);
            }
            
            console.error('[SingleChat] Error sending message:', error);
            
            // Show error message
            let errorHtml;
            if (cssPrefix === 'chat-message') {
                // Terma uses different CSS structure
                errorHtml = `
                    <div class="chat-message system-message">
                        <strong>System:</strong> Failed to connect to ${config.displayName} AI
                    </div>
                `;
            } else {
                errorHtml = `
                    <div class="${cssPrefix}__message ${cssPrefix}__message--system">
                        <div class="${cssPrefix}__message-content">
                            <div class="${cssPrefix}__message-text">
                                <strong>System:</strong> Failed to connect to ${config.displayName} AI
                            </div>
                        </div>
                    </div>
                `;
            }
            
            containerEl.innerHTML = containerEl.innerHTML + errorHtml;
            containerEl.scrollTop = containerEl.scrollHeight;
        }
    },
    
    /**
     * Escape HTML to prevent injection
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

console.log('[SingleChat] Module loaded');