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
        
        // aish commands
        if (cmdString.startsWith('aish ')) {
            return {
                type: 'aish',
                command: cmdString.slice(5).trim(),
                raw: cmdString
            };
        }
        
        // Shell commands with explicit shell: prefix
        if (cmdString.startsWith('shell:')) {
            return {
                type: 'shell',
                command: cmdString.slice(6).trim(),
                raw: cmdString
            };
        }
        
        // Claude escalation
        if (cmdString === 'claude' || cmdString.startsWith('claude ')) {
            const parts = cmdString.split(' ');
            return {
                type: 'escalate',
                model: 'claude',
                args: parts.slice(1).join(' '),
                raw: cmdString
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
                raw: cmdString
            };
        }
        
        // Think model escalation
        if (cmdString === 'think' || cmdString.startsWith('think ')) {
            const parts = cmdString.split(' ');
            return {
                type: 'escalate',
                model: 'think',
                args: parts.slice(1).join(' '),
                raw: cmdString
            };
        }
        
        // System prompt setting
        if (cmdString.startsWith('system:')) {
            return {
                type: 'system_prompt',
                prompt: cmdString.slice(7).trim(),
                raw: cmdString
            };
        }
        
        // Temperature setting
        if (cmdString.startsWith('temp:')) {
            return {
                type: 'parameter',
                param: 'temperature',
                value: cmdString.slice(5).trim(),
                raw: cmdString
            };
        }
        
        // Safe shell commands (whitelist) - also handle with flags like 'ls -la'
        const safeCommands = ['git', 'ls', 'ps', 'grep', 'pwd', 'date', 'whoami', 'tekton-status'];
        const firstWord = cmdString.split(' ')[0];
        
        // Check if it's a safe command (including with flags)
        if (safeCommands.includes(firstWord)) {
            console.log('[ChatCommandParser] Detected safe shell command:', cmdString);
            return {
                type: 'shell',
                command: cmdString,
                safe: true,
                raw: cmdString
            };
        }
        
        // Also handle explicit commands like 'ls -la' without the shell: prefix
        // Check if the entire command starts with a safe command
        for (const safeCmd of safeCommands) {
            if (cmdString === safeCmd || cmdString.startsWith(safeCmd + ' ')) {
                console.log('[ChatCommandParser] Detected safe shell command (pattern match):', cmdString);
                return {
                    type: 'shell',
                    command: cmdString,
                    safe: true,
                    raw: cmdString
                };
            }
        }
        
        // Unknown command - return null to skip
        console.warn('[ChatCommandParser] Unknown command:', cmdString);
        return null;
    },
    
    /**
     * Check if command is safe to execute
     * @param {object} command - Parsed command object
     * @returns {boolean} - True if safe
     */
    isSafeCommand: function(command) {
        if (command.type === 'aish') {
            // All aish commands are safe
            return true;
        }
        
        if (command.type === 'shell') {
            // Check for dangerous patterns
            const dangerous = [
                'rm -rf', 'sudo', '> /dev/', 'dd if=', 'mkfs',
                '; rm', '&& rm', '| rm', 'format', 'del /f'
            ];
            
            const cmdLower = command.command.toLowerCase();
            for (const pattern of dangerous) {
                if (cmdLower.includes(pattern)) {
                    console.error('[ChatCommandParser] Blocked dangerous command:', command.command);
                    return false;
                }
            }
            
            // Check if explicitly marked as safe
            return command.safe === true;
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