/**
 * DEPRECATED: This file will be removed after CSS-first migration is verified
 * Terminal Manager
 * Handles the terminal interface with history, command processing, and input capabilities
 */

class TerminalManager {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = null;
        this.history = {}; // Component-specific terminal history
        this.maxHistoryLines = 1000; // Maximum number of lines to keep in history
        this.commandHistory = []; // Command history for up/down navigation
        this.historyPosition = -1; // Current position in command history
        this.currentInput = ""; // Current input when navigating history
        this.inputPrompt = "> "; // Command prompt character
        this.inputLine = null; // Reference to the current input line
        this.debugMode = true; // Enable debug logging
    }
    
    /**
     * Log debug message to console
     * @param {string} message - Message to log
     * @param {any} data - Optional data to log
     */
    debug(message, data = null) {
        if (!this.debugMode) return;
        
        const timestamp = new Date().toISOString();
        const component = "TerminalManager";
        
        if (data) {
            console.log(`[${timestamp}] [${component}] ${message}`, data);
        } else {
            console.log(`[${timestamp}] [${component}] ${message}`);
        }
    }
    
    /**
     * Initialize the terminal
     */
    init() {
        this.container = document.getElementById(this.containerId);
        if (!this.container) {
            console.error(`Terminal container #${this.containerId} not found`);
            return;
        }
        
        // Set terminal styles directly without debug colors
        this.container.style.height = "100%";
        this.container.style.width = "100%";
        this.container.style.padding = "20px";
        this.container.style.display = "flex";
        this.container.style.flexDirection = "column";
        this.container.style.justifyContent = "flex-start";
        
        // Initialize with a welcome message
        this.clear();
        this.write("Welcome to Tekton Terminal", false);
        this.write("How can I help you today?", false);
        this.write("-----------------------------------", false);
        
        // Create initial input line
        this.createInputLine();
        
        // Add event listener for terminal clicks to focus input
        this.container.addEventListener('click', (e) => {
            this.focusInput();
            console.log('Terminal clicked, focusing input');
        });
        
        // Show a message about the input area
        this.write("Type your commands below ↓", false);
        
        // Make sure container is focused on load
        setTimeout(() => {
            this.focusInput();
            console.log('Focused input on load');
        }, 500);
        
        // Log debug info
        console.log('Terminal initialized with container:', this.container);
        this.debug('Terminal Manager initialized');
    }
    
    /**
     * Create an input line in the terminal
     */
    createInputLine() {
        console.log('Creating terminal input line');
        
        // Create an input container
        const inputContainer = document.createElement('div');
        inputContainer.className = 'terminal-input-container';
        inputContainer.style.display = 'flex';
        inputContainer.style.alignItems = 'center';
        inputContainer.style.marginTop = '10px';
        inputContainer.style.marginBottom = '10px';
        inputContainer.style.padding = '10px';
        inputContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.3)';
        inputContainer.style.borderRadius = '4px';
        inputContainer.style.border = '1px solid #3a7bd5';
        
        // Create prompt element
        const promptElement = document.createElement('span');
        promptElement.innerHTML = '&gt; ';
        promptElement.style.color = '#3a7bd5';
        promptElement.style.fontWeight = 'bold';
        promptElement.style.marginRight = '8px';
        
        // Create input element - VERY SIMPLE VERSION
        const inputElement = document.createElement('input');
        inputElement.type = 'text';
        inputElement.id = 'terminal-input-field';
        inputElement.placeholder = 'Type your command here...';
        inputElement.style.flex = '1';
        inputElement.style.backgroundColor = '#1a1a1a';
        inputElement.style.border = '1px solid #666';
        inputElement.style.padding = '8px';
        inputElement.style.color = 'white';
        inputElement.style.fontSize = '14px';
        
        // Add event listeners for Enter key
        inputElement.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const command = inputElement.value.trim();
                if (command) {
                    console.log('Command entered:', command);
                    this.processCommand();
                }
            }
        });
        
        // Append elements
        inputContainer.appendChild(promptElement);
        inputContainer.appendChild(inputElement);
        
        // Add to terminal
        this.container.appendChild(inputContainer);
        
        // Save reference to input line
        this.inputLine = {
            container: inputContainer,
            prompt: promptElement,
            input: inputElement
        };
        
        // Focus the input
        setTimeout(() => {
            console.log('Focusing input element after delay');
            inputElement.focus();
        }, 100);
        
        // Log for debugging
        console.log('Created terminal input line with input element:', inputElement);
        this.debug('Created terminal input line');
        
        // Update UI for better visibility
        this.write('Terminal ready - Type commands below ↓', false);
    }
    
    /**
     * Focus the terminal input
     */
    focusInput() {
        if (this.inputLine && this.inputLine.input) {
            // Simple focus approach
            console.log('Focusing input element directly');
            
            // Highlight the input container
            this.inputLine.container.style.borderColor = '#00aaff';
            
            // Focus the input directly
            this.inputLine.input.focus();
            
            // Make sure we're scrolled to it
            this.scrollToBottom();
            
            // Reset border color after delay
            setTimeout(() => {
                this.inputLine.container.style.borderColor = '#3a7bd5';
            }, 1000);
        } else {
            console.log('Input line not found, creating a new one');
            this.createInputLine();
        }
    }
    
    /**
     * Handle key down events in the terminal input
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeyDown(event) {
        this.debug(`Key pressed: ${event.key}`, {code: event.keyCode, ctrl: event.ctrlKey, shift: event.shiftKey});
        
        switch (event.key) {
            case 'Enter':
                this.processCommand();
                event.preventDefault();
                break;
                
            case 'ArrowUp':
                this.navigateHistory(-1); // Navigate back in history
                event.preventDefault();
                break;
                
            case 'ArrowDown':
                this.navigateHistory(1); // Navigate forward in history
                event.preventDefault();
                break;
                
            case 'Tab':
                // Command completion could be implemented here
                event.preventDefault();
                break;
                
            case 'c':
                if (event.ctrlKey) {
                    // Handle Ctrl+C to cancel current input
                    this.inputLine.input.value = '';
                    event.preventDefault();
                    this.debug('Input canceled (Ctrl+C)');
                }
                break;
                
            case 'l':
                if (event.ctrlKey) {
                    // Handle Ctrl+L to clear screen
                    this.clear();
                    this.createInputLine();
                    event.preventDefault();
                    this.debug('Terminal cleared (Ctrl+L)');
                }
                break;
        }
    }
    
    /**
     * Navigate through command history
     * @param {number} direction - Direction to navigate (-1 for back, 1 for forward)
     */
    navigateHistory(direction) {
        if (this.commandHistory.length === 0) return;
        
        // Save current input when starting to navigate
        if (this.historyPosition === -1 && direction === -1) {
            this.currentInput = this.inputLine.input.value;
        }
        
        // Calculate new position
        let newPosition = this.historyPosition + direction;
        
        // Constrain to valid range
        if (newPosition >= this.commandHistory.length) {
            newPosition = this.commandHistory.length - 1;
        } else if (newPosition < -1) {
            newPosition = -1;
        }
        
        // Update position
        this.historyPosition = newPosition;
        
        // Set input value based on position
        if (newPosition === -1) {
            // Return to current input
            this.inputLine.input.value = this.currentInput;
        } else {
            // Set to history item
            this.inputLine.input.value = this.commandHistory[this.commandHistory.length - 1 - newPosition];
        }
        
        // Move cursor to end
        setTimeout(() => {
            this.inputLine.input.selectionStart = this.inputLine.input.selectionEnd = this.inputLine.input.value.length;
        }, 0);
        
        this.debug(`History navigation: position ${this.historyPosition}`);
    }
    
    /**
     * Process the current command
     */
    processCommand() {
        if (!this.inputLine || !this.inputLine.input) {
            console.log('No input line found during command processing');
            return;
        }
        
        const command = this.inputLine.input.value.trim();
        if (!command) return;
        
        console.log(`Processing command: ${command}`);
        
        // Add to command history
        this.commandHistory.push(command);
        if (this.commandHistory.length > 100) {
            this.commandHistory.shift(); // Keep history limited
        }
        this.historyPosition = -1; // Reset position
        
        // Add the command to terminal as a line
        this.write(command, true);
        
        // Handle built-in commands
        if (command === 'clear') {
            this.clear();
        } else if (command === 'help') {
            this.showHelp();
        } else {
            // Send command to backend
            this.sendCommand(command);
        }
        
        // Clear the input value
        this.inputLine.input.value = '';
        
        // Re-focus the input
        this.inputLine.input.focus();
    }
    
    /**
     * Send a command to the backend
     * @param {string} command - Command to send
     */
    sendCommand(command) {
        this.debug(`Sending command to backend: ${command}`);
        
        // Get active component
        const componentId = tektonUI.activeComponent;
        
        if (window.websocketManager) {
            websocketManager.sendMessage({
                type: "COMMAND",
                source: "UI",
                target: componentId,
                timestamp: new Date().toISOString(),
                payload: {
                    command: "process_message",
                    message: command
                }
            });
        } else {
            console.error("WebSocket not initialized");
            this.write("Error: Cannot connect to server", false);
        }
    }
    
    /**
     * Display help information
     */
    showHelp() {
        this.write("Available Commands:");
        this.write("  clear       - Clear the terminal");
        this.write("  help        - Show this help");
        this.write("  <message>   - Send a message to the current component");
        this.write("");
        this.write("Navigation:");
        this.write("  Up/Down     - Navigate command history");
        this.write("  Ctrl+C      - Cancel current input");
        this.write("  Ctrl+L      - Clear screen");
    }
    
    /**
     * Write content to the terminal
     * @param {string} text - Text to write
     * @param {boolean} isCommand - Whether this is a user command (prefixed with >)
     */
    write(text, isCommand = false) {
        if (!this.container) return;
        
        // Create a new line element
        const line = document.createElement('div');
        line.className = isCommand ? 'terminal-command' : 'terminal-output';
        
        // Format the text based on its type
        const formattedText = this.formatText(text, isCommand);
        line.innerHTML = formattedText;
        
        // Add to the terminal
        this.container.appendChild(line);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Add to history for the current component
        const componentId = tektonUI.activeComponent;
        this.addToHistory(componentId, {
            type: isCommand ? 'command' : 'output',
            text: text
        });
        
        this.debug(`Wrote ${isCommand ? 'command' : 'output'} to terminal: ${text.substring(0, 50)}${text.length > 50 ? '...' : ''}`);
    }
    
    /**
     * Scroll to the bottom of the terminal
     */
    scrollToBottom() {
        if (this.container) {
            this.container.scrollTop = this.container.scrollHeight;
        }
    }
    
    /**
     * Format text for display in the terminal
     * @param {string} text - Text to format
     * @param {boolean} isCommand - Whether this is a user command
     * @returns {string} Formatted text
     */
    formatText(text, isCommand) {
        // Sanitize the text to prevent HTML injection
        let sanitized = this.sanitizeHtml(text);
        
        // Apply basic markdown-like formatting
        // Replace ```code``` with <pre><code>code</code></pre>
        sanitized = sanitized.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Replace `code` with <code>code</code>
        sanitized = sanitized.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Replace **bold** with <strong>bold</strong>
        sanitized = sanitized.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Replace *italic* with <em>italic</em>
        sanitized = sanitized.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        // Add command prefix
        if (isCommand) {
            sanitized = `<span class="command-prefix">&gt;</span> ${sanitized}`;
        }
        
        return sanitized;
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
     * Clear the terminal
     */
    clear() {
        if (this.container) {
            this.container.innerHTML = '';
            this.debug('Terminal cleared');
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
        
        // Trim history if it exceeds the maximum size
        if (this.history[componentId].length > this.maxHistoryLines) {
            this.history[componentId] = this.history[componentId].slice(
                this.history[componentId].length - this.maxHistoryLines
            );
        }
        
        // Save history to localStorage
        this.saveHistory(componentId);
    }
    
    /**
     * Save terminal history to localStorage
     * @param {string} componentId - Component ID
     */
    saveHistory(componentId) {
        if (window.storageManager && this.history[componentId]) {
            storageManager.setItem(`terminal_history_${componentId}`, JSON.stringify(this.history[componentId]));
            this.debug(`Saved history for component: ${componentId}`);
        }
    }
    
    /**
     * Load terminal history for a component
     * @param {string} componentId - Component ID
     */
    loadHistory(componentId) {
        if (!window.storageManager) return;
        
        this.debug(`Loading history for component: ${componentId}`);
        
        // Clear terminal
        this.clear();
        
        // Try to load from memory first
        if (this.history[componentId] && this.history[componentId].length > 0) {
            this.replayHistory(this.history[componentId]);
            return;
        }
        
        // Otherwise load from localStorage
        const savedHistory = storageManager.getItem(`terminal_history_${componentId}`);
        if (savedHistory) {
            try {
                const historyEntries = JSON.parse(savedHistory);
                this.history[componentId] = historyEntries;
                this.replayHistory(historyEntries);
            } catch (e) {
                console.error('Error loading terminal history:', e);
                this.write('Error loading history');
            }
        } else {
            // If no history, just show a welcome message
            this.write(`Terminal ready for ${componentId}`);
        }
        
        // Create input line after loading history
        this.createInputLine();
    }
    
    /**
     * Replay a sequence of history entries in the terminal
     * @param {Array} entries - History entries to replay
     */
    replayHistory(entries) {
        if (!entries || !Array.isArray(entries)) return;
        
        this.debug(`Replaying ${entries.length} history entries`);
        
        // Only replay the last 50 entries to avoid overwhelming the terminal
        const recentEntries = entries.slice(-50);
        
        recentEntries.forEach(entry => {
            if (entry && entry.text) {
                this.write(entry.text, entry.type === 'command');
            }
        });
    }
}