/**
 * Chat Core - First stage processor for all Tekton chat
 * Handles command parsing and execution before message routing
 */

console.log('[FILE_TRACE] Loading: chat-core.js');

window.ChatCore = {
    initialized: false,
    
    /**
     * Initialize chat core
     */
    init: function() {
        if (this.initialized) return;
        
        console.log('[ChatCore] Initializing first stage processor');
        
        // Ensure parser is loaded
        if (!window.ChatCommandParser) {
            console.error('[ChatCore] ChatCommandParser not loaded!');
            return;
        }
        
        // Override SingleChat if it exists
        if (window.SingleChat && window.SingleChat.sendMessage) {
            console.log('[ChatCore] Found SingleChat, wrapping it');
            this.wrapSingleChat();
        } else {
            console.warn('[ChatCore] SingleChat not found, will retry in 500ms');
            setTimeout(() => this.init(), 500);
            return;
        }
        
        // Override TeamChat if it exists
        if (window.TeamChat && window.TeamChat.sendMessage) {
            console.log('[ChatCore] Found TeamChat, wrapping it');
            this.wrapTeamChat();
        }
        
        this.initialized = true;
        console.log('[ChatCore] First stage processor ready - commands will be intercepted');
    },
    
    /**
     * Process chat input through first stage parser
     * @param {string} input - Raw chat input
     * @param {string} chatType - 'single' or 'team'
     * @param {string} componentName - Component sending the message
     * @returns {Promise} - Processed message and results
     */
    async processChatInput: function(input, chatType, componentName) {
        console.log('[ChatCore] Processing input:', input);
        
        // Parse for bracket commands
        const parsed = ChatCommandParser.parse(input);
        console.log('[ChatCore] Parsed:', parsed);
        
        const results = [];
        const metadata = {};
        
        // Execute each command
        for (const cmd of parsed.commands) {
            console.log('[ChatCore] Executing command:', cmd);
            
            // Check safety
            if (!ChatCommandParser.isSafeCommand(cmd)) {
                results.push({
                    type: 'error',
                    output: `Command blocked for safety: ${cmd.raw}`
                });
                continue;
            }
            
            try {
                const result = await this.executeCommand(cmd, componentName);
                if (result) {
                    results.push(result);
                    
                    // Handle escalation metadata
                    if (cmd.type === 'escalate') {
                        metadata.escalate = cmd.model;
                        metadata.escalateArgs = cmd.args;
                    }
                    
                    // Handle system prompt
                    if (cmd.type === 'system_prompt') {
                        metadata.systemPrompt = cmd.prompt;
                    }
                    
                    // Handle parameters
                    if (cmd.type === 'parameter') {
                        metadata[cmd.param] = cmd.value;
                    }
                }
            } catch (error) {
                console.error('[ChatCore] Command execution error:', error);
                results.push({
                    type: 'error',
                    output: `Command failed: ${error.message}`
                });
            }
        }
        
        return {
            message: parsed.message,
            commandResults: results,
            metadata: metadata,
            original: parsed.original
        };
    },
    
    /**
     * Execute a parsed command
     * @param {object} command - Parsed command object
     * @param {string} componentName - Component context
     * @returns {Promise} - Command result
     */
    async executeCommand: function(command, componentName) {
        switch (command.type) {
            case 'aish':
                return await this.executeAishCommand(command.command, componentName);
                
            case 'shell':
                return await this.executeShellCommand(command.command, componentName);
                
            case 'escalate':
                // Escalation is handled via metadata, no immediate execution
                return {
                    type: 'system',
                    output: `Escalating to ${command.model}...`
                };
                
            case 'system_prompt':
                return {
                    type: 'system',
                    output: `System prompt set`
                };
                
            case 'parameter':
                return {
                    type: 'system',
                    output: `${command.param} set to ${command.value}`
                };
                
            default:
                return null;
        }
    },
    
    /**
     * Execute aish command via backend
     * @param {string} command - aish command without 'aish' prefix
     * @param {string} componentName - Component context
     * @returns {Promise} - Command result
     */
    async executeAishCommand: function(command, componentName) {
        try {
            // Determine the backend URL based on component
            const baseUrl = this.getComponentUrl(componentName);
            const response = await fetch(`${baseUrl}/api/chat/command`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: 'aish',
                    command: command,
                    context: componentName
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            return {
                type: 'system',
                output: result.output || result.stdout || 'Command completed'
            };
        } catch (error) {
            console.error('[ChatCore] aish command failed:', error);
            // Fallback to showing command
            return {
                type: 'system',
                output: `[Simulated] aish ${command}`
            };
        }
    },
    
    /**
     * Execute shell command via backend
     * @param {string} command - Shell command
     * @param {string} componentName - Component context
     * @returns {Promise} - Command result
     */
    async executeShellCommand: function(command, componentName) {
        try {
            const baseUrl = this.getComponentUrl(componentName);
            const response = await fetch(`${baseUrl}/api/chat/command`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: 'shell',
                    command: command,
                    context: componentName
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            return {
                type: 'system',
                output: result.output || result.stdout || 'Command completed'
            };
        } catch (error) {
            console.error('[ChatCore] Shell command failed:', error);
            // Fallback to showing command
            return {
                type: 'system',
                output: `[Simulated] ${command}`
            };
        }
    },
    
    /**
     * Get component backend URL
     * @param {string} componentName - Component name
     * @returns {string} - Backend URL
     */
    getComponentUrl: function(componentName) {
        // Map component names to ports
        const portMap = {
            'terma': 8004,
            'apollo': 8012,
            'rhetor': 8002,
            'athena': 8007,
            'sophia': 8013,
            'hermes': 8001,
            'prometheus': 8006,
            'telos': 8008,
            'metis': 8009,
            'harmonia': 8018,
            'synthesis': 8019,
            'numa': 8015,
            'noesis': 8014,
            'engram': 8003,
            'ergon': 8016,
            'penia': 8017
        };
        
        const port = portMap[componentName.toLowerCase()] || 8000;
        return `http://localhost:${port}`;
    },
    
    /**
     * Wrap SingleChat.sendMessage to add first stage processing
     */
    wrapSingleChat: function() {
        const originalSend = window.SingleChat.sendMessage;
        
        window.SingleChat.sendMessage = async function(chatEl, message) {
            // Get component name from chat element
            const componentName = chatEl.getAttribute('data-component') || 
                                 chatEl.closest('[data-tekton-component]')?.getAttribute('data-tekton-component') || 
                                 'unknown';
            
            // Process through first stage
            const processed = await ChatCore.processChatInput(message, 'single', componentName);
            
            // Display command results
            for (const result of processed.commandResults) {
                ChatCore.displaySystemMessage(chatEl, result);
            }
            
            // Send remaining message with metadata
            if (processed.message) {
                console.log('[ChatCore] Sending message with metadata:', processed.metadata);
                
                // If there's escalation metadata, modify the message
                if (processed.metadata.escalate) {
                    // For Claude escalation, we might need to route differently
                    // For now, pass through with metadata
                    console.log('[ChatCore] Escalating to:', processed.metadata.escalate);
                }
                
                // Call original with enhanced context
                originalSend.call(this, chatEl, processed.message, processed.metadata);
            } else if (processed.commandResults.length > 0) {
                // Commands were executed but no message remains
                console.log('[ChatCore] Commands executed, no message to send');
            }
        };
        
        console.log('[ChatCore] SingleChat wrapped');
    },
    
    /**
     * Wrap TeamChat.sendMessage to add first stage processing
     */
    wrapTeamChat: function() {
        const originalSend = window.TeamChat.sendMessage;
        
        window.TeamChat.sendMessage = async function(chatEl, message) {
            // Get component name from chat element
            const componentName = chatEl.getAttribute('data-component') || 
                                 chatEl.closest('[data-tekton-component]')?.getAttribute('data-tekton-component') || 
                                 'unknown';
            
            // Process through first stage
            const processed = await ChatCore.processChatInput(message, 'team', componentName);
            
            // Display command results
            for (const result of processed.commandResults) {
                ChatCore.displaySystemMessage(chatEl, result);
            }
            
            // Send remaining message with metadata
            if (processed.message) {
                // Call original with enhanced context
                originalSend.call(this, chatEl, processed.message, processed.metadata);
            }
        };
        
        console.log('[ChatCore] TeamChat wrapped');
    },
    
    /**
     * Display system message in chat
     * @param {Element} chatEl - Chat container element
     * @param {object} result - Command result
     */
    displaySystemMessage: function(chatEl, result) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message system-message';
        
        const icon = result.type === 'error' ? '⚠️' : '🖥️';
        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-sender">${icon} system</span>
                <span class="message-time">${timestamp}</span>
            </div>
            <div class="message-content">
                <pre>${this.escapeHtml(result.output)}</pre>
            </div>
        `;
        
        // Find messages container
        const messagesContainer = chatEl.querySelector('.chat-messages') || 
                                 chatEl.querySelector('[data-messages]') ||
                                 chatEl;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    },
    
    /**
     * Escape HTML for safe display
     * @param {string} text - Text to escape
     * @returns {string} - Escaped text
     */
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        // Delay initialization to ensure SingleChat is loaded
        setTimeout(function() {
            ChatCore.init();
        }, 100);
    });
} else {
    // Still delay to ensure SingleChat is loaded
    setTimeout(function() {
        ChatCore.init();
    }, 100);
}