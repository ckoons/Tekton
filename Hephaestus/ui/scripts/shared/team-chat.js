/**
 * Unified Team Chat Component
 * Provides consistent team chat functionality across all Tekton components
 * Uses HTML injection pattern, CSS-first approach, no DOM manipulation
 */

window.TeamChat = {
    // Message buffers for async processing
    messageBuffers: {},  // keyed by component name
    processingFlags: {},  // track if team broadcast is in progress
    
    /**
     * Initialize team chat for a component
     * @param {HTMLElement} containerEl - The chat messages container
     * @param {string} componentName - Component identifier (e.g., 'terma', 'budget')
     * @param {string} cssPrefix - CSS class prefix (e.g., 'terma', 'budget')
     */
    init(containerEl, componentName, cssPrefix) {
        if (!containerEl) {
            console.error('[TeamChat] Container element not found');
            return;
        }
        
        // Store configuration on the element for later use
        containerEl.setAttribute('data-team-chat', 'true');
        containerEl.setAttribute('data-component-name', componentName);
        containerEl.setAttribute('data-css-prefix', cssPrefix);
        
        console.log(`[TeamChat] Initialized for ${componentName}`);
    },
    
    /**
     * Send a message to the team (async with buffering)
     * @param {HTMLElement} containerEl - The chat messages container
     * @param {string} message - The message to send
     */
    async sendMessage(containerEl, message) {
        if (!containerEl || !message || !message.trim()) {
            return;
        }
        
        const componentName = containerEl.getAttribute('data-component-name');
        const cssPrefix = containerEl.getAttribute('data-css-prefix');
        
        // Initialize buffer if needed
        if (!this.messageBuffers[componentName]) {
            this.messageBuffers[componentName] = [];
        }
        
        // Process commands first
        const processed = await window.processCommandsInMessage(message, componentName);
        
        // Handle command results if any
        if (processed.hasCommands && processed.commandResults.length > 0) {
            // First, display the user's original command
            const existingContent = containerEl.innerHTML;
            let userCommandHtml;
            if (cssPrefix === 'chat-message') {
                userCommandHtml = `
                    <div class="chat-message user-message">
                        ${this.escapeHtml(message)}
                    </div>
                `;
            } else {
                userCommandHtml = `
                    <div class="${cssPrefix}__message ${cssPrefix}__message--user">
                        <div class="${cssPrefix}__message-content">
                            <div class="${cssPrefix}__message-text">${this.escapeHtml(message)}</div>
                        </div>
                    </div>
                `;
            }
            containerEl.innerHTML = existingContent + userCommandHtml;
            containerEl.scrollTop = containerEl.scrollHeight;
            
            // Then handle the command results
            let immediateAiMessage = '';  // For 'ai' and 'both' modes (send now)
            
            for (const result of processed.commandResults) {
                const outputMode = result.outputMode || 'user';
                
                if (outputMode === 'user' || outputMode === 'both') {
                    // Show to user
                    window.displayCommandResult(containerEl, result, cssPrefix);
                }
                
                if (outputMode === 'ai') {
                    // Send to AI immediately (output not shown to user)
                    immediateAiMessage += `Command output:\n${result.output}\n\n`;
                } else if (outputMode === 'both') {
                    // Send to AI immediately WITH current message (output shown to user AND sent to AI)
                    immediateAiMessage += `Command output:\n${result.output}\n\n`;
                }
            }
            
            // Handle immediate AI message (for 'ai' and 'both' modes)
            if (immediateAiMessage) {
                message = processed.message ? `${processed.message}\n\n${immediateAiMessage}` : immediateAiMessage;
            } else if (!processed.message || !processed.message.trim()) {
                // No message and no immediate AI output, we're done
                return;
            } else {
                // Continue with the remaining message
                message = processed.message;
            }
        }
        
        // Only show user message if NO commands were processed
        // (If commands were processed, we already showed the original input above)
        if (!processed.hasCommands && message && message.trim()) {
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
        }
        
        // Add to buffer for async processing
        if (message && message.trim()) {
            this.messageBuffers[componentName].push({
                message: message,
                containerEl: containerEl,
                cssPrefix: cssPrefix,
                componentName: componentName
            });
            
            // Process buffer if not already processing
            if (!this.processingFlags[componentName]) {
                this.processMessageBuffer(componentName);
            }
        }
    },
    
    /**
     * Process queued messages asynchronously
     * @param {string} componentName - The component name
     */
    async processMessageBuffer(componentName) {
        // Mark as processing
        this.processingFlags[componentName] = true;
        
        while (this.messageBuffers[componentName] && this.messageBuffers[componentName].length > 0) {
            const messageData = this.messageBuffers[componentName].shift();
            const { message, containerEl, cssPrefix } = messageData;
            
            // Show processing message
            if (window.AIChat && window.AIChat.showProcessingMessage) {
                window.AIChat.showProcessingMessage(containerEl, "Broadcasting to team", cssPrefix);
            }
            
            try {
                // Send message to team
                const data = await window.AIChat.teamChat(message, componentName);
            
                // Remove processing message
                if (window.AIChat && window.AIChat.hideProcessingMessage) {
                    window.AIChat.hideProcessingMessage(containerEl);
                }
                
                // Check for responses
                if (data.responses && data.responses.length > 0) {
                // Build HTML for all responses
                let responsesHtml = '';
                
                for (const resp of data.responses) {
                    // Extract sender name and format it
                    const sender = this.formatSenderName(resp.specialist_id || resp.socket_id);
                    
                    // Render markdown if available
                    let renderedContent;
                    if (window.MarkdownRenderer) {
                        try {
                            // Markdown renderer handles escaping internally
                            renderedContent = await window.MarkdownRenderer.render(resp.content, componentName);
                        } catch (e) {
                            console.warn('[TeamChat] Markdown rendering failed, using plain text:', e);
                            renderedContent = this.escapeHtml(resp.content);
                        }
                    } else {
                        renderedContent = this.escapeHtml(resp.content);
                    }
                    
                    if (cssPrefix === 'chat-message') {
                        // Terma uses different CSS structure
                        responsesHtml += `
                            <div class="chat-message ai-message">
                                <strong>${sender}:</strong> <div class="markdown-content">${renderedContent}</div>
                            </div>
                        `;
                    } else {
                        responsesHtml += `
                            <div class="${cssPrefix}__message ${cssPrefix}__message--ai">
                                <div class="${cssPrefix}__message-content">
                                    <div class="${cssPrefix}__message-text">
                                        <strong>${sender}:</strong> <div class="markdown-content">${renderedContent}</div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                }
                
                // Add all responses at once
                containerEl.innerHTML = containerEl.innerHTML + responsesHtml;
                containerEl.scrollTop = containerEl.scrollHeight;
                
            } else if (data.error) {
                // Show error message
                let errorHtml;
                if (cssPrefix === 'chat-message') {
                    errorHtml = `
                        <div class="chat-message system-message">
                            <strong>System:</strong> ${this.escapeHtml(data.error)}
                        </div>
                    `;
                } else {
                    errorHtml = `
                        <div class="${cssPrefix}__message ${cssPrefix}__message--system">
                            <div class="${cssPrefix}__message-content">
                                <div class="${cssPrefix}__message-text">
                                    <strong>System:</strong> ${this.escapeHtml(data.error)}
                                </div>
                            </div>
                        </div>
                    `;
                }
                
                containerEl.innerHTML = containerEl.innerHTML + errorHtml;
                containerEl.scrollTop = containerEl.scrollHeight;
            } else {
                // No responses received
                let noResponseHtml;
                if (cssPrefix === 'chat-message') {
                    noResponseHtml = `
                        <div class="chat-message system-message">
                            <strong>System:</strong> No responses received from team
                        </div>
                    `;
                } else {
                    noResponseHtml = `
                        <div class="${cssPrefix}__message ${cssPrefix}__message--system">
                            <div class="${cssPrefix}__message-content">
                                <div class="${cssPrefix}__message-text">
                                    <strong>System:</strong> No responses received from team
                                </div>
                            </div>
                        </div>
                    `;
                }
                
                containerEl.innerHTML = containerEl.innerHTML + noResponseHtml;
                containerEl.scrollTop = containerEl.scrollHeight;
            }
            
        } catch (error) {
            // Remove processing message
            if (window.AIChat && window.AIChat.hideProcessingMessage) {
                window.AIChat.hideProcessingMessage(containerEl);
            }
            
            console.error('[TeamChat] Error sending message:', error);
            
            // Show error message
            let errorHtml;
            if (cssPrefix === 'chat-message') {
                errorHtml = `
                    <div class="chat-message system-message">
                        <strong>System:</strong> Failed to broadcast message to team
                    </div>
                `;
            } else {
                errorHtml = `
                    <div class="${cssPrefix}__message ${cssPrefix}__message--system">
                        <div class="${cssPrefix}__message-content">
                            <div class="${cssPrefix}__message-text">
                                <strong>System:</strong> Failed to broadcast message to team
                            </div>
                        </div>
                    </div>
                `;
            }
            
            containerEl.innerHTML = containerEl.innerHTML + errorHtml;
            containerEl.scrollTop = containerEl.scrollHeight;
        }
        }
        
        // Mark as not processing
        this.processingFlags[componentName] = false;
    },
    
    /**
     * Format sender name from AI identifier
     * @param {string} aiId - AI identifier (e.g., 'terma-ai', 'terma')
     * @returns {string} Formatted name
     */
    formatSenderName(aiId) {
        if (!aiId) return 'Unknown';
        
        // Remove '-ai' suffix if present
        const cleanId = aiId.replace(/-ai$/, '');
        
        // Capitalize first letter
        return cleanId.charAt(0).toUpperCase() + cleanId.slice(1);
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

console.log('[TeamChat] Module loaded');