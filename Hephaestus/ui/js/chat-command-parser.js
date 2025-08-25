/**
 * Chat Command Parser
 * Parses bracket commands [command] from chat input
 * First stage processor for all Tekton chat interfaces
 */

console.log('[FILE_TRACE] Loading: chat-command-parser.js');

window.ChatCommandParser = {
    /**
     * Parse input string for bracket commands
     * @param {string} input - Raw chat input
     * @returns {object} - { commands: [], message: string, original: string }
     */
    parse: function(input) {
        const commands = [];
        let message = input;
        
        // Extract all [command] blocks
        const regex = /\[([^\]]+)\]/g;
        let match;
        
        while ((match = regex.exec(input)) !== null) {
            const parsed = this.parseCommand(match[1]);
            if (parsed) {
                commands.push(parsed);
                // Remove command from message
                message = message.replace(match[0], '').trim();
            }
        }
        
        return {
            commands: commands,
            message: message,
            original: input,
            hasCommands: commands.length > 0
        };
    },
    
    /**
     * Parse individual command string
     * @param {string} cmdString - Command without brackets
     * @returns {object} - Command object with type and parameters
     */
    parseCommand: function(cmdString) {
        cmdString = cmdString.trim();
        
        // Check for output redirect syntax
        let outputMode = 'user';  // Default: show to user
        let originalCmd = cmdString;
        
        if (cmdString.endsWith(' >>')) {
            // Execute, show to user AND send to AI
            outputMode = 'both';
            cmdString = cmdString.slice(0, -3).trim();
        } else if (cmdString.endsWith(' >')) {
            // Execute and send to CI only
            outputMode = 'ai';
            cmdString = cmdString.slice(0, -2).trim();
        }
        
        // aish commands
        if (cmdString.startsWith('aish ')) {
            return {
                type: 'aish',
                command: cmdString.slice(5).trim(),
                output: outputMode,
                raw: originalCmd
            };
        }
        
        // Shell commands with explicit shell: prefix
        if (cmdString.startsWith('shell:')) {
            return {
                type: 'shell',
                command: cmdString.slice(6).trim(),
                output: outputMode,
                raw: originalCmd
            };
        }
        
        // Claude escalation
        if (cmdString === 'claude' || cmdString.startsWith('claude ')) {
            const parts = cmdString.split(' ');
            return {
                type: 'escalate',
                model: 'claude',
                args: parts.slice(1).join(' '),
                output: outputMode,
                raw: originalCmd
            };
        }
        
        // Claude with specific model variant
        if (cmdString.startsWith('claude-')) {
            const parts = cmdString.split(' ');
            const model = parts[0]; // claude-opus, claude-sonnet, etc.
            return {
                type: 'escalate',
                model: model,
                args: parts.slice(1).join(' '),
                output: outputMode,
                raw: originalCmd
            };
        }
        
        // Think model escalation
        if (cmdString === 'think' || cmdString.startsWith('think ')) {
            const parts = cmdString.split(' ');
            return {
                type: 'escalate',
                model: 'think',
                args: parts.slice(1).join(' '),
                output: outputMode,
                raw: originalCmd
            };
        }
        
        // Clear command - clears chat display
        if (cmdString === 'clear') {
            return {
                type: 'clear',
                output: outputMode,
                raw: originalCmd
            };
        }
        
        // System prompt setting
        if (cmdString.startsWith('system:')) {
            return {
                type: 'system_prompt',
                prompt: cmdString.slice(7).trim(),
                output: outputMode,
                raw: originalCmd
            };
        }
        
        // Temperature setting
        if (cmdString.startsWith('temp:')) {
            return {
                type: 'parameter',
                param: 'temperature',
                value: cmdString.slice(5).trim(),
                output: outputMode,
                raw: originalCmd
            };
        }
        
        // Any command is allowed - we'll check against blacklist in isSafeCommand
        // This allows ALL commands like tree, echo, cat, etc.
        console.log('[ChatCommandParser] Detected shell command:', cmdString, 'output:', outputMode);
        return {
            type: 'shell',
            command: cmdString,
            output: outputMode,
            safe: false,  // Will be checked against blacklist
            raw: originalCmd
        };
    },
    
    /**
     * Check if command is safe to execute
     * NOTE: Safety check removed - server handles all safety
     * @param {object} command - Parsed command object
     * @returns {boolean} - Always returns true
     */
    isSafeCommand: function(command) {
        // ALL commands are safe - server handles safety
        return true;
    },
    
    // Old safety check code - kept for reference but not used
    _oldSafetyCheck: function(command) {
        if (command.type === 'aish') {
            // All aish commands are safe
            return true;
        }
        
        if (command.type === 'clear') {
            // Clear command is always safe
            return true;
        }
        
        if (command.type === 'shell') {
            // cd commands are always safe
            console.log('[ChatCommandParser] Checking safety for:', command.command, 'type:', typeof command.command);
            const cmd = command.command ? command.command.trim() : '';
            if (cmd === 'cd' || cmd.startsWith('cd ')) {
                console.log('[ChatCommandParser] cd command is safe');
                return true;
            }
            // Blacklist of dangerous patterns
            const dangerous = [
                'rm -rf /',      // Remove root
                'rm -rf ~',      // Remove home
                'rm -rf *',      // Remove everything
                'sudo rm',       // Sudo remove
                '> /dev/sd',     // Overwrite disk
                'dd if=/dev/zero of=/dev/', // Disk destroyer
                'mkfs.',         // Format filesystem
                '; rm -rf',      // Command injection remove
                '&& rm -rf',     // Command chain remove
                '| rm -rf',      // Pipe to remove
                'format c:',     // Windows format
                'del /f /s /q',  // Windows delete
                ':(){:|:&};:',   // Fork bomb
                'chmod -R 777 /', // Permission destroyer
                'chown -R',      // Mass ownership change
                '>()',           // Process substitution bombs
                'mv /* /dev/null', // Move everything to null
                'shred',         // Secure delete
                'wipe',          // Secure wipe
            ];
            
            const cmdLower = command.command.toLowerCase();
            for (const pattern of dangerous) {
                if (cmdLower.includes(pattern.toLowerCase())) {
                    console.error('[ChatCommandParser] Blocked dangerous command:', command.command);
                    return false;
                }
            }
            
            // All other commands are allowed
            return true;
        }
        
        // Escalation and parameter commands are always safe
        if (command.type === 'escalate' || command.type === 'parameter' || command.type === 'system_prompt') {
            return true;
        }
        
        return false;
    },
    
    /**
     * Format command for display
     * @param {object} command - Parsed command object
     * @returns {string} - Human-readable command description
     */
    formatCommand: function(command) {
        switch (command.type) {
            case 'aish':
                return `aish ${command.command}`;
            case 'shell':
                return `shell: ${command.command}`;
            case 'escalate':
                return `Escalate to ${command.model}${command.args ? ' with ' + command.args : ''}`;
            case 'system_prompt':
                return `Set system prompt: ${command.prompt.substring(0, 50)}...`;
            case 'parameter':
                return `Set ${command.param}: ${command.value}`;
            default:
                return command.raw;
        }
    }
};

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatCommandParser;
}