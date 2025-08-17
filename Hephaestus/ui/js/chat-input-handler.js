/**
 * Chat Input Handler
 * Handles keyboard shortcuts for all chat inputs (history, autocomplete, etc.)
 */

window.ChatInputHandler = {
    /**
     * Initialize input handler for a chat input element
     * @param {HTMLInputElement} input - The input element
     */
    init(input) {
        if (!input || input.hasAttribute('data-chat-input-initialized')) {
            return;
        }
        
        input.setAttribute('data-chat-input-initialized', 'true');
        
        // Handle keyboard events
        input.addEventListener('keydown', (e) => this.handleKeyDown(e, input));
    },
    
    /**
     * Handle keydown events
     * @param {KeyboardEvent} e - The keyboard event
     * @param {HTMLInputElement} input - The input element
     */
    handleKeyDown(e, input) {
        switch(e.key) {
            case 'ArrowUp':
                // Get previous command from history
                if (window.CommandHistory) {
                    e.preventDefault();
                    const command = window.CommandHistory.getPrevious();
                    if (command !== null) {
                        // Check if we're in bracket mode or should add brackets
                        const currentValue = input.value.trim();
                        if (currentValue.startsWith('[') || command.startsWith('[')) {
                            input.value = `[${command}]`;
                        } else {
                            input.value = `[${command}]`;
                        }
                        // Move cursor to end
                        input.setSelectionRange(input.value.length, input.value.length);
                    }
                }
                break;
                
            case 'ArrowDown':
                // Get next command from history
                if (window.CommandHistory) {
                    e.preventDefault();
                    const command = window.CommandHistory.getNext();
                    if (command !== null) {
                        input.value = `[${command}]`;
                        input.setSelectionRange(input.value.length, input.value.length);
                    } else {
                        // Clear input when at end of history
                        input.value = '';
                    }
                }
                break;
                
            case 'Tab':
                // Tab completion (future feature)
                // For now, just prevent default tab behavior in chat inputs
                if (input.value.includes('[') && !input.value.includes(']')) {
                    e.preventDefault();
                    // TODO: Implement file path completion
                    console.log('[ChatInputHandler] Tab completion not yet implemented');
                }
                break;
                
            case 'ArrowLeft':
            case 'ArrowRight':
                // Edit in place (future feature)
                // For now, just allow normal cursor movement
                break;
        }
    },
    
    /**
     * Initialize all chat inputs on the page
     */
    initAll() {
        // Find all chat input fields
        const inputs = document.querySelectorAll([
            'input[type="text"][placeholder*="message"]',
            'input[type="text"][placeholder*="Message"]',
            'input[type="text"][placeholder*="chat"]',
            'input[type="text"][placeholder*="Chat"]',
            'input[type="text"][placeholder*="command"]',
            'input[type="text"][placeholder*="Command"]',
            'input.chat-input',
            'input.numa-input',
            '#numa-chat-input',
            '#team-chat-input',
            '#project-chat-input',
            '#footer-input',
            '.footer-input',
            '.command-input',
            'input[data-chat-input]'
        ].join(', '));
        
        inputs.forEach(input => this.init(input));
        
        // Watch for new inputs being added dynamically
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        // Check if it's an input
                        if (node.tagName === 'INPUT' && this.isChatInput(node)) {
                            this.init(node);
                        }
                        // Check for inputs within the added node
                        if (node.querySelectorAll) {
                            const inputs = node.querySelectorAll('input[type="text"]');
                            inputs.forEach(input => {
                                if (this.isChatInput(input)) {
                                    this.init(input);
                                }
                            });
                        }
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    },
    
    /**
     * Check if an input is likely a chat input
     * @param {HTMLInputElement} input - The input to check
     * @returns {boolean} True if it's likely a chat input
     */
    isChatInput(input) {
        const placeholder = (input.placeholder || '').toLowerCase();
        const className = (input.className || '').toLowerCase();
        const id = (input.id || '').toLowerCase();
        
        return (
            placeholder.includes('message') ||
            placeholder.includes('chat') ||
            placeholder.includes('type') ||
            placeholder.includes('command') ||
            className.includes('chat') ||
            className.includes('message') ||
            className.includes('footer') ||
            className.includes('command') ||
            id.includes('chat') ||
            id.includes('message') ||
            id.includes('footer') ||
            id.includes('command') ||
            input.hasAttribute('data-chat-input')
        );
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ChatInputHandler.initAll());
} else {
    ChatInputHandler.initAll();
}

console.log('[ChatInputHandler] Module loaded');