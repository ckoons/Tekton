/**
 * Command Autocomplete Module
 * Provides tab completion for commands and file paths in chat inputs
 */

window.CommandAutocomplete = {
    currentSuggestions: [],
    currentIndex: -1,
    activeInput: null,
    dropdown: null,
    
    /**
     * Initialize autocomplete for an input
     * @param {HTMLInputElement} input - The input element
     */
    init(input) {
        console.log('[CommandAutocomplete.init] Called with input:', input?.id || input?.placeholder || 'unknown');
        if (!input || input.hasAttribute('data-autocomplete-initialized')) {
            console.log('[CommandAutocomplete.init] Skipping - already initialized or null');
            return;
        }
        
        input.setAttribute('data-autocomplete-initialized', 'true');
        console.log('[CommandAutocomplete.init] Adding event listeners to:', input.id || input.placeholder);
        
        // Add event listeners
        input.addEventListener('keydown', (e) => this.handleKeyDown(e, input));
        input.addEventListener('input', () => this.hideDropdown());
        input.addEventListener('blur', () => setTimeout(() => this.hideDropdown(), 200));
        console.log('[CommandAutocomplete.init] Successfully initialized');
    },
    
    /**
     * Handle keydown events
     * @param {KeyboardEvent} e - The keyboard event
     * @param {HTMLInputElement} input - The input element
     */
    async handleKeyDown(e, input) {
        const value = input.value;
        const cursorPos = input.selectionStart;
        
        // Debug log for Tab key
        if (e.key === 'Tab') {
            console.log('[CommandAutocomplete] Tab pressed. Value:', value, 'Cursor:', cursorPos);
        }
        
        // Check if we're inside brackets
        const beforeCursor = value.substring(0, cursorPos);
        const afterCursor = value.substring(cursorPos);
        
        // Find the last opening bracket before cursor
        const lastOpenBracket = beforeCursor.lastIndexOf('[');
        if (lastOpenBracket === -1) {
            if (e.key === 'Tab') {
                console.log('[CommandAutocomplete] Not in command - no [ found');
            }
            return; // Not in a command
        }
        
        // Check if there's a closing bracket after the opening one
        const textAfterBracket = value.substring(lastOpenBracket);
        const nextCloseBracket = textAfterBracket.indexOf(']');
        console.log('[CommandAutocomplete] Bracket check - lastOpen:', lastOpenBracket, 'nextClose:', nextCloseBracket, 'cursor:', cursorPos);
        
        if (nextCloseBracket !== -1 && lastOpenBracket + nextCloseBracket < cursorPos) {
            console.log('[CommandAutocomplete] Past the command, ignoring');
            return; // We're past the command
        }
        
        // We're inside a command
        const commandStart = lastOpenBracket + 1;
        const commandText = beforeCursor.substring(commandStart);
        
        if (e.key === 'Tab') {
            console.log('[CommandAutocomplete] Inside command. CommandText:', commandText);
            e.preventDefault();
            await this.handleTab(input, commandText, commandStart, cursorPos);
        } else if (e.key === 'Escape' && this.dropdown) {
            e.preventDefault();
            this.hideDropdown();
        } else if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && this.dropdown) {
            e.preventDefault();
            this.navigateDropdown(e.key === 'ArrowDown' ? 1 : -1);
        } else if (e.key === 'Enter' && this.dropdown && this.currentIndex >= 0) {
            e.preventDefault();
            this.selectSuggestion(this.currentIndex);
        }
    },
    
    /**
     * Handle tab key for autocomplete
     */
    async handleTab(input, commandText, commandStart, cursorPos) {
        console.log('[CommandAutocomplete] handleTab called. CommandText:', commandText);
        
        // Parse what type of completion we need
        const parts = commandText.trim().split(/\s+/);
        console.log('[CommandAutocomplete] Command parts:', parts);
        
        if (parts.length === 0 || commandText.trim() === '') {
            // Complete command names
            console.log('[CommandAutocomplete] Showing command suggestions');
            this.showCommandSuggestions(input, commandStart);
        } else {
            // Complete file paths or arguments
            const lastPart = parts[parts.length - 1];
            const isPath = lastPart.includes('/') || parts[0] === 'cd' || parts[0] === 'ls';
            console.log('[CommandAutocomplete] Last part:', lastPart, 'isPath:', isPath);
            
            if (isPath) {
                console.log('[CommandAutocomplete] Showing path completions for:', lastPart);
                await this.showPathCompletions(input, lastPart, commandStart, commandText);
            } else {
                // Could add command-specific completions here
                console.log('[CommandAutocomplete] Showing command suggestions (fallback)');
                this.showCommandSuggestions(input, commandStart);
            }
        }
    },
    
    /**
     * Show command suggestions
     */
    showCommandSuggestions(input, commandStart) {
        console.log('[CommandAutocomplete.showCommandSuggestions] Called');
        const commonCommands = [
            'ls', 'cd', 'pwd', 'git status', 'git diff', 'git log',
            'echo', 'cat', 'grep', 'find', 'clear', 'tree',
            'npm install', 'npm test', 'npm run', 'python', 'node'
        ];
        
        // Get what user has typed so far
        const typed = input.value.substring(commandStart, input.selectionStart).trim();
        console.log('[CommandAutocomplete] User typed:', typed);
        
        // Filter commands that start with what was typed
        const matches = commonCommands.filter(cmd => cmd.startsWith(typed));
        
        if (matches.length === 1) {
            // Single match - complete it
            const completion = matches[0];
            const beforeCmd = input.value.substring(0, commandStart);
            const afterCursor = input.value.substring(input.selectionStart);
            const needsCloseBracket = !afterCursor.includes(']');
            
            input.value = beforeCmd + completion + (needsCloseBracket ? ']' : '') + afterCursor;
            const newPos = beforeCmd.length + completion.length;
            input.setSelectionRange(newPos, newPos);
            
            console.log('[CommandAutocomplete] Completed:', completion);
        } else if (matches.length > 1) {
            // Multiple matches - complete with first one for now
            const completion = matches[0];
            const beforeCmd = input.value.substring(0, commandStart);
            const afterCursor = input.value.substring(input.selectionStart);
            const needsCloseBracket = !afterCursor.includes(']');
            
            input.value = beforeCmd + completion + (needsCloseBracket ? ']' : '') + afterCursor;
            const newPos = beforeCmd.length + completion.length;
            input.setSelectionRange(newPos, newPos);
            
            console.log('[CommandAutocomplete] Multiple matches, used:', completion, 'from:', matches.join(', '));
        }
    },
    
    /**
     * Show path completions from server
     */
    async showPathCompletions(input, partialPath, commandStart, fullCommand) {
        try {
            // Get current working directory
            const cwd = window.SingleChat.currentWorkingDirectory || '~';
            console.log('[CommandAutocomplete] Current directory:', cwd);
            
            // Request completions from server
            const baseUrl = typeof hephaestusUrl === 'function' 
                ? hephaestusUrl('') 
                : `http://localhost:${window.HEPHAESTUS_PORT || 8080}`;
            
            console.log('[CommandAutocomplete] Fetching from:', `${baseUrl}/api/autocomplete`);
            const response = await fetch(`${baseUrl}/api/autocomplete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    path: partialPath,
                    cwd: cwd,
                    command: fullCommand
                })
            });
            
            console.log('[CommandAutocomplete] Response status:', response.status);
            if (response.ok) {
                const data = await response.json();
                console.log('[CommandAutocomplete] Suggestions:', data);
                if (data.suggestions && data.suggestions.length === 1) {
                    // Single suggestion - server now returns full path
                    const suggestion = data.suggestions[0];
                    
                    // Replace the entire partial path with the suggestion
                    const beforePath = fullCommand.substring(0, fullCommand.lastIndexOf(partialPath));
                    const newCommand = beforePath + suggestion;
                    
                    // Update the input value
                    const beforeBracket = input.value.substring(0, commandStart);
                    const afterCursor = input.value.substring(input.selectionStart);
                    
                    // If there's already a closing bracket, don't add another
                    const needsCloseBracket = !afterCursor.includes(']');
                    input.value = beforeBracket + newCommand + (needsCloseBracket ? ']' : '') + afterCursor;
                    
                    // Position cursor after the completion (but before the closing bracket)
                    const newPos = beforeBracket.length + newCommand.length;
                    input.setSelectionRange(newPos, newPos);
                    
                    console.log('[CommandAutocomplete] Single suggestion completed:', suggestion);
                } else if (data.suggestions && data.suggestions.length > 1) {
                    // Multiple suggestions - show them inline as hint
                    console.log('[CommandAutocomplete] Multiple matches:', data.suggestions.join(', '));
                    // For now, just complete with the first one
                    const suggestion = data.suggestions[0];
                    const beforePath = fullCommand.substring(0, fullCommand.lastIndexOf(partialPath));
                    const newCommand = beforePath + suggestion;
                    
                    const beforeBracket = input.value.substring(0, commandStart);
                    const afterCursor = input.value.substring(input.selectionStart);
                    const needsCloseBracket = !afterCursor.includes(']');
                    input.value = beforeBracket + newCommand + (needsCloseBracket ? ']' : '') + afterCursor;
                    
                    const newPos = beforeBracket.length + newCommand.length;
                    input.setSelectionRange(newPos, newPos);
                } else {
                    console.log('[CommandAutocomplete] No suggestions returned');
                }
            } else {
                const error = await response.text();
                console.error('[CommandAutocomplete] Server error:', error);
            }
        } catch (error) {
            console.error('[CommandAutocomplete] Failed to get completions:', error);
        }
    },
    
    /**
     * Show dropdown with suggestions
     */
    showDropdown(input, suggestions, insertPos, replaceLength = 0) {
        console.log('[CommandAutocomplete.showDropdown] Called with:', {
            suggestions: suggestions,
            insertPos: insertPos,
            replaceLength: replaceLength,
            inputValue: input.value
        });
        
        if (suggestions.length === 0) {
            console.log('[CommandAutocomplete.showDropdown] No suggestions, returning');
            return;
        }
        
        this.activeInput = input;
        this.currentSuggestions = suggestions;
        this.currentIndex = 0;
        this.insertPosition = insertPos;
        this.replaceLength = replaceLength;
        console.log('[CommandAutocomplete.showDropdown] State updated');
        
        // Create or update dropdown
        if (!this.dropdown) {
            console.log('[CommandAutocomplete.showDropdown] Creating new dropdown element');
            this.dropdown = document.createElement('div');
            this.dropdown.className = 'autocomplete-dropdown';
            this.dropdown.style.cssText = `
                position: absolute;
                background: var(--bg-secondary, #2a2a2a);
                border: 1px solid var(--border-color, #444);
                border-radius: 4px;
                max-height: 200px;
                overflow-y: auto;
                z-index: 10000;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            `;
            document.body.appendChild(this.dropdown);
        }
        
        // Clear and populate dropdown
        this.dropdown.innerHTML = '';
        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.style.cssText = `
                padding: 8px 12px;
                cursor: pointer;
                color: var(--text-primary, #fff);
                ${index === 0 ? 'background: var(--bg-hover, #3a3a3a);' : ''}
            `;
            item.textContent = suggestion;
            item.onmouseenter = () => this.highlightItem(index);
            item.onclick = () => this.selectSuggestion(index);
            this.dropdown.appendChild(item);
        });
        
        // Position dropdown below input
        const rect = input.getBoundingClientRect();
        console.log('[CommandAutocomplete.showDropdown] Input rect:', rect);
        this.dropdown.style.left = rect.left + 'px';
        this.dropdown.style.top = (rect.bottom + 2) + 'px';
        this.dropdown.style.minWidth = Math.min(rect.width, 300) + 'px';
        this.dropdown.style.display = 'block';
        console.log('[CommandAutocomplete.showDropdown] Dropdown positioned and displayed at:', {
            left: this.dropdown.style.left,
            top: this.dropdown.style.top,
            display: this.dropdown.style.display,
            childCount: this.dropdown.children.length
        });
    },
    
    /**
     * Navigate dropdown with arrow keys
     */
    navigateDropdown(direction) {
        if (!this.dropdown || this.currentSuggestions.length === 0) {
            return;
        }
        
        // Update index
        this.currentIndex += direction;
        if (this.currentIndex < 0) {
            this.currentIndex = this.currentSuggestions.length - 1;
        } else if (this.currentIndex >= this.currentSuggestions.length) {
            this.currentIndex = 0;
        }
        
        this.highlightItem(this.currentIndex);
    },
    
    /**
     * Highlight a dropdown item
     */
    highlightItem(index) {
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        items.forEach((item, i) => {
            if (i === index) {
                item.style.background = 'var(--bg-hover, #3a3a3a)';
            } else {
                item.style.background = '';
            }
        });
        this.currentIndex = index;
    },
    
    /**
     * Select a suggestion
     */
    selectSuggestion(index) {
        if (!this.activeInput || index >= this.currentSuggestions.length) {
            return;
        }
        
        const suggestion = this.currentSuggestions[index];
        const value = this.activeInput.value;
        
        // Insert the suggestion
        let newValue;
        if (this.replaceLength > 0) {
            // Replace partial path
            newValue = value.substring(0, this.insertPosition) + 
                      suggestion + 
                      value.substring(this.insertPosition + this.replaceLength);
        } else {
            // Insert new
            newValue = value.substring(0, this.insertPosition) + 
                      suggestion + 
                      value.substring(this.insertPosition);
        }
        
        this.activeInput.value = newValue;
        
        // Move cursor after the inserted text
        const newCursorPos = this.insertPosition + suggestion.length;
        this.activeInput.setSelectionRange(newCursorPos, newCursorPos);
        
        this.hideDropdown();
        this.activeInput.focus();
    },
    
    /**
     * Hide the dropdown
     */
    hideDropdown() {
        if (this.dropdown) {
            this.dropdown.style.display = 'none';
            this.currentSuggestions = [];
            this.currentIndex = -1;
            this.activeInput = null;
        }
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
            className.includes('numa') ||
            id.includes('chat') ||
            id.includes('numa') ||
            input.hasAttribute('data-chat-input')
        );
    },
    
    /**
     * Initialize all chat inputs on the page and watch for new ones
     */
    initAll() {
        console.log('[CommandAutocomplete] Initializing all inputs...');
        
        // Find all existing chat input fields
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
        
        console.log('[CommandAutocomplete] Found', inputs.length, 'existing inputs');
        inputs.forEach(input => {
            console.log('[CommandAutocomplete] Initializing:', input.placeholder || input.id || input.className);
            this.init(input);
        });
        
        // Watch for new inputs being added dynamically
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        // Check if it's an input
                        if (node.tagName === 'INPUT' && this.isChatInput(node)) {
                            console.log('[CommandAutocomplete] New input detected:', node.placeholder || node.id);
                            this.init(node);
                        }
                        // Check for inputs within the added node
                        if (node.querySelectorAll) {
                            const inputs = node.querySelectorAll('input[type="text"]');
                            inputs.forEach(input => {
                                if (this.isChatInput(input)) {
                                    console.log('[CommandAutocomplete] New input in component:', input.placeholder || input.id);
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
        
        console.log('[CommandAutocomplete] MutationObserver started');
    }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.CommandAutocomplete.initAll();
    });
} else {
    // DOM already loaded
    window.CommandAutocomplete.initAll();
}

console.log('[CommandAutocomplete] Module loaded');