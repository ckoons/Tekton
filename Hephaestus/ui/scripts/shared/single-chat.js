/**
 * Unified Single Chat Component
 * Provides consistent single CI chat functionality across all Tekton components
 * Uses HTML injection pattern, CSS-first approach, no DOM manipulation
 */

window.SingleChat = {
    // Storage for command outputs that should be included with next message
    pendingCommandOutputs: {},  // keyed by component name
    
    // Current working directory (shared across all chats)
    currentWorkingDirectory: null,  // Will be set to home directory on first command
    
    // Message buffers for async processing
    messageBuffers: {},  // keyed by component name
    processingFlags: {},  // track if CI is busy per component
    
    // Component configuration mapping - using -ci suffix for CI specialists (42xxx ports)
    config: {
        'terma': { aiName: 'terma-ci', displayName: 'Terma' },
        'budget': { aiName: 'penia-ci', displayName: 'Penia' },
        'numa': { aiName: 'numa-ci', displayName: 'Numa' },
        'athena': { aiName: 'athena-ci', displayName: 'Athena' },
        'apollo': { aiName: 'apollo-ci', displayName: 'Apollo' },
        'rhetor': { aiName: 'rhetor-ci', displayName: 'Rhetor' },
        'hermes': { aiName: 'hermes-ci', displayName: 'Hermes' },
        'sophia': { aiName: 'sophia-ci', displayName: 'Sophia' },
        'noesis': { aiName: 'noesis-ci', displayName: 'Noesis' },
        'metis': { aiName: 'metis-ci', displayName: 'Metis' },
        'harmonia': { aiName: 'harmonia-ci', displayName: 'Harmonia' },
        'prometheus': { aiName: 'prometheus-ci', displayName: 'Prometheus' },
        'ergon': { aiName: 'ergon-ci', displayName: 'Ergon' },
        'telos': { aiName: 'telos-ci', displayName: 'Telos' },
        'synthesis': { aiName: 'synthesis-ci', displayName: 'Synthesis' },
        'engram': { aiName: 'engram-ci', displayName: 'Engram' },
        'codex': { aiName: 'codex-ci', displayName: 'Codex' },
        'tekton': { aiName: 'tekton_core-ci', displayName: 'Tekton' } // tekton-core CI specialist
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
     * Send a message to the CI (async with buffering)
     * @param {HTMLElement} containerEl - The chat messages container
     * @param {string} message - The message to send
     * @param {object} metadata - Optional metadata (e.g., escalation info)
     */
    async sendMessage(containerEl, message, metadata = {}) {
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
        
        // Initialize buffer if needed
        if (!this.messageBuffers[componentName]) {
            this.messageBuffers[componentName] = [];
        }
        
        // Process commands first
        const processed = await window.processCommandsInMessage(message, componentName);
        
        // Handle command results based on output mode
        if (processed.hasCommands && processed.commandResults.length > 0) {
            // First, display the user's command
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
                    // Send to CI immediately (output not shown to user)
                    immediateAiMessage += `Command output:\n${result.output}\n\n`;
                } else if (outputMode === 'both') {
                    // Send to CI immediately WITH current message (output shown to user AND sent to AI)
                    immediateAiMessage += `Command output:\n${result.output}\n\n`;
                }
            }
            
            // Handle immediate CI message (for 'ai' and 'both' modes)
            if (immediateAiMessage) {
                message = processed.message ? `${processed.message}\n\n${immediateAiMessage}` : immediateAiMessage;
            } else if (!processed.message || !processed.message.trim()) {
                // No message and no immediate CI output, we're done
                return;
            } else {
                // Continue with the remaining message
                message = processed.message;
            }
        }
        
        // Only show user message if NO commands were processed
        // (If commands were processed, we already showed the original input above)
        if (!processed.hasCommands && processed.message && processed.message.trim()) {
            // Get existing content (preserve welcome message)
            const existingContent = containerEl.innerHTML;
            
            // Store the original message for display (before adding pending outputs)
            const displayMessage = processed.message;
            
            // Add user message using innerHTML
            let userMessageHtml;
            if (cssPrefix === 'chat-message') {
                // Terma uses different CSS structure
                userMessageHtml = `
                    <div class="chat-message user-message">
                        ${this.escapeHtml(displayMessage)}
                    </div>
                `;
            } else {
                userMessageHtml = `
                    <div class="${cssPrefix}__message ${cssPrefix}__message--user">
                        <div class="${cssPrefix}__message-content">
                            <div class="${cssPrefix}__message-text">${this.escapeHtml(displayMessage)}</div>
                        </div>
                    </div>
                `;
            }
            
            containerEl.innerHTML = existingContent + userMessageHtml;
            containerEl.scrollTop = containerEl.scrollHeight;
        } else if (!processed.hasCommands && !processed.message) {
            // If no commands and no message, still show what user typed
            const existingContent = containerEl.innerHTML;
            let userMessageHtml;
            if (cssPrefix === 'chat-message') {
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
        
        // If there's a message to send to AI, add it to the buffer
        if (message && message.trim()) {
            // Add to buffer with metadata
            this.messageBuffers[componentName].push({
                message: message,
                metadata: metadata,
                containerEl: containerEl,
                cssPrefix: cssPrefix,
                config: config
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
            const { message, metadata, containerEl, cssPrefix, config } = messageData;
            
            // Show processing message
            if (window.AIChat && window.AIChat.showProcessingMessage) {
                window.AIChat.showProcessingMessage(containerEl, "Processing", cssPrefix);
            }
            
            try {
                let fullMessage = message;
                
                // Check if we have pending command outputs to prepend
                if (this.pendingCommandOutputs[componentName]) {
                    fullMessage = this.pendingCommandOutputs[componentName] + message;
                    // Clear the pending outputs after using them
                    delete this.pendingCommandOutputs[componentName];
                }
                
                // Check for escalation metadata
                let response;
                if (metadata.escalate) {
                    console.log(`[SingleChat] Escalating to ${metadata.escalate} instead of ${config.aiName}`);
                    const escalatedMessage = `[Model: ${metadata.escalate}] ${fullMessage}`;
                    response = await window.AIChat.sendMessage(config.aiName, escalatedMessage);
                } else {
                    // Normal message to AI
                    response = await window.AIChat.sendMessage(config.aiName, fullMessage);
                }
            
                // Remove processing message
                if (window.AIChat && window.AIChat.hideProcessingMessage) {
                    window.AIChat.hideProcessingMessage(containerEl);
                }
                
                // Add CI response with markdown rendering
                const responseText = response.content || response;
                let renderedContent;
                
                // Use markdown renderer if available
                if (window.MarkdownRenderer) {
                    try {
                        // Markdown renderer handles escaping internally
                        renderedContent = await window.MarkdownRenderer.render(responseText, componentName);
                    } catch (e) {
                        console.warn('[SingleChat] Markdown rendering failed, using plain text:', e);
                        renderedContent = this.escapeHtml(responseText);
                    }
                } else {
                    // No markdown renderer, escape HTML
                    renderedContent = this.escapeHtml(responseText);
                }
                
                let aiMessageHtml;
                if (cssPrefix === 'chat-message') {
                    // Terma uses different CSS structure
                    aiMessageHtml = `
                        <div class="chat-message ai-message">
                            <strong>${config.displayName}:</strong> <div class="markdown-content">${renderedContent}</div>
                        </div>
                    `;
                } else {
                    aiMessageHtml = `
                        <div class="${cssPrefix}__message ${cssPrefix}__message--ci">
                            <div class="${cssPrefix}__message-content">
                                <div class="${cssPrefix}__message-text">
                                    <strong>${config.displayName}:</strong> <div class="markdown-content">${renderedContent}</div>
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
                            <strong>System:</strong> Failed to Connect to ${config.displayName}
                        </div>
                    `;
                } else {
                    errorHtml = `
                        <div class="${cssPrefix}__message ${cssPrefix}__message--system">
                            <div class="${cssPrefix}__message-content">
                                <div class="${cssPrefix}__message-text">
                                    <strong>System:</strong> Failed to Connect to ${config.displayName}
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

/**
 * Process commands in a message and execute them
 * @param {string} message - Raw message that may contain [commands]
 * @param {string} componentName - Component context for execution
 * @returns {Promise} - Object with processed message and command results
 */
window.processCommandsInMessage = async function(message, componentName) {
    // Quick check - no brackets means no commands
    if (!message.includes('[') || !message.includes(']')) {
        return { 
            message: message, 
            hasCommands: false,
            commandResults: []
        };
    }
    
    // Check if parser is available
    if (!window.ChatCommandParser) {
        console.warn('[processCommands] ChatCommandParser not loaded, skipping command processing');
        return { 
            message: message, 
            hasCommands: false,
            commandResults: []
        };
    }
    
    // Parse the message for commands
    const parsed = ChatCommandParser.parse(message);
    
    if (!parsed.hasCommands) {
        return {
            message: message,
            hasCommands: false,
            commandResults: []
        };
    }
    
    console.log('[processCommands] Found commands:', parsed.commands);
    
    // Execute each command
    const results = [];
    for (const cmd of parsed.commands) {
        // Add command to history (except clear)
        if (window.CommandHistory && cmd.type !== 'clear') {
            window.CommandHistory.add(cmd.command || cmd.raw);
        }
        // Handle special command types that don't go to backend
        if (cmd.type === 'clear') {
            // Clear the chat display
            const container = document.querySelector(`[data-component-name="${componentName}"]`);
            if (container) {
                // Keep only the welcome message if it exists
                const welcomeMsg = container.querySelector('.welcome-message, .system-message:first-child');
                if (welcomeMsg) {
                    container.innerHTML = welcomeMsg.outerHTML;
                } else {
                    container.innerHTML = '';
                }
            }
            results.push({
                type: 'system',
                output: 'Chat cleared (context preserved)',
                outputMode: 'user'
            });
            continue;
        }
        
        // Safety check - but isSafeCommand now always returns true
        // Server handles actual safety checking
        
        // Execute command via backend
        try {
            const result = await executeCommand(cmd, componentName);
            if (result) {
                // Add output mode to result
                result.outputMode = cmd.output || 'user';
                results.push(result);
            }
        } catch (error) {
            console.error('[processCommands] Command failed:', error);
            results.push({
                type: 'error',
                output: `Command failed: ${error.message}`
            });
        }
    }
    
    return {
        message: parsed.message,  // Message without commands
        hasCommands: true,
        commandResults: results
    };
};

/**
 * Execute a single command via backend
 * @param {object} command - Parsed command object
 * @param {string} componentName - Component context
 * @returns {Promise} - Command result
 */
async function executeCommand(command, componentName) {
    // Get Hephaestus URL for command execution (commands always go through UI server)
    const baseUrl = typeof hephaestusUrl === 'function' 
        ? hephaestusUrl('') 
        : `http://localhost:${window.HEPHAESTUS_PORT || 8080}`;
    
    try {
        const response = await fetch(`${baseUrl}/api/chat/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: command.type,
                command: command.type === 'shell' || command.type === 'aish' 
                    ? command.command 
                    : command.raw,
                context: { 
                    component: componentName,
                    cwd: window.SingleChat.currentWorkingDirectory  // Send current directory
                }
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        // Update current working directory if it changed
        if (result.cwd) {
            window.SingleChat.currentWorkingDirectory = result.cwd;
        }
        
        return {
            type: result.type || 'system',
            output: result.output || 'Command completed'
        };
    } catch (error) {
        console.error('[executeCommand] Failed:', error);
        // Return command as-is for display
        return {
            type: 'system',
            output: `[${command.raw}]`
        };
    }
}

/**
 * Display command result in chat as system message
 * @param {HTMLElement} containerEl - Chat container
 * @param {object} result - Command result
 * @param {string} cssPrefix - CSS prefix for styling
 */
window.displayCommandResult = function(containerEl, result, cssPrefix) {
    const existingContent = containerEl.innerHTML;
    
    let systemMessageHtml;
    if (cssPrefix === 'chat-message') {
        // Terma style
        systemMessageHtml = `
            <div class="chat-message system-message">
                <strong>System:</strong> <pre style="display: inline-block; margin: 0;">${window.SingleChat.escapeHtml(result.output)}</pre>
            </div>
        `;
    } else {
        // Component style
        systemMessageHtml = `
            <div class="${cssPrefix}__message ${cssPrefix}__message--system">
                <div class="${cssPrefix}__message-content">
                    <div class="${cssPrefix}__message-text">
                        <strong>System:</strong> <pre style="display: inline-block; margin: 0;">${window.SingleChat.escapeHtml(result.output)}</pre>
                    </div>
                </div>
            </div>
        `;
    }
    
    containerEl.innerHTML = existingContent + systemMessageHtml;
    containerEl.scrollTop = containerEl.scrollHeight;
};

console.log('[SingleChat] Module loaded');
