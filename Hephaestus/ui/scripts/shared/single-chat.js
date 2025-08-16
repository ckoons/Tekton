/**
 * Unified Single Chat Component
 * Provides consistent single AI chat functionality across all Tekton components
 * Uses HTML injection pattern, CSS-first approach, no DOM manipulation
 */

window.SingleChat = {
    // Component configuration mapping - using -ai suffix for AI specialists (42xxx ports)
    config: {
        'terma': { aiName: 'terma-ai', displayName: 'Terma' },
        'budget': { aiName: 'penia-ai', displayName: 'Penia' },
        'numa': { aiName: 'numa-ai', displayName: 'Numa' },
        'athena': { aiName: 'athena-ai', displayName: 'Athena' },
        'apollo': { aiName: 'apollo-ai', displayName: 'Apollo' },
        'rhetor': { aiName: 'rhetor-ai', displayName: 'Rhetor' },
        'hermes': { aiName: 'hermes-ai', displayName: 'Hermes' },
        'sophia': { aiName: 'sophia-ai', displayName: 'Sophia' },
        'noesis': { aiName: 'noesis-ai', displayName: 'Noesis' },
        'metis': { aiName: 'metis-ai', displayName: 'Metis' },
        'harmonia': { aiName: 'harmonia-ai', displayName: 'Harmonia' },
        'prometheus': { aiName: 'prometheus-ai', displayName: 'Prometheus' },
        'ergon': { aiName: 'ergon-ai', displayName: 'Ergon' },
        'telos': { aiName: 'telos-ai', displayName: 'Telos' },
        'synthesis': { aiName: 'synthesis-ai', displayName: 'Synthesis' },
        'engram': { aiName: 'engram-ai', displayName: 'Engram' },
        'codex': { aiName: 'codex-ai', displayName: 'Codex' },
        'tekton': { aiName: 'tekton_core-ai', displayName: 'Tekton' } // tekton-core AI specialist
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
        
        // Process commands first
        const processed = await window.processCommandsInMessage(message, componentName);
        
        // Display command results if any
        if (processed.hasCommands && processed.commandResults.length > 0) {
            for (const result of processed.commandResults) {
                window.displayCommandResult(containerEl, result, cssPrefix);
            }
            
            // If no message remains after commands, we're done
            if (!processed.message || !processed.message.trim()) {
                return;
            }
            
            // Continue with the remaining message
            message = processed.message;
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
            // Check for escalation metadata
            let response;
            if (metadata.escalate) {
                console.log(`[SingleChat] Escalating to ${metadata.escalate} instead of ${config.aiName}`);
                // For now, still use the same AI but include escalation in message
                // In future, this could route to a different endpoint
                const escalatedMessage = `[Model: ${metadata.escalate}] ${message}`;
                response = await window.AIChat.sendMessage(config.aiName, escalatedMessage);
            } else {
                // Normal message to AI
                response = await window.AIChat.sendMessage(config.aiName, message);
            }
            
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
        // Check if command is safe
        if (!ChatCommandParser.isSafeCommand(cmd)) {
            results.push({
                type: 'error',
                output: `Command blocked for safety: ${cmd.raw}`
            });
            continue;
        }
        
        // Execute command via backend
        try {
            const result = await executeCommand(cmd, componentName);
            if (result) {
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
    // Get component URL using tektonUrl
    const baseUrl = typeof tektonUrl === 'function' 
        ? tektonUrl(componentName, '') 
        : `http://localhost:8000`;
    
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
                context: { component: componentName }
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
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