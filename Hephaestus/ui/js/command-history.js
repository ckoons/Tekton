/**
 * Command History Manager
 * Manages command history for all Tekton chat interfaces
 * Stores history in ~/.tekton/command_history
 */

window.CommandHistory = {
    history: [],
    historyIndex: -1,
    historyFile: null,  // Will be set from backend
    maxHistory: 1000,   // Maximum commands to keep
    
    /**
     * Initialize history system
     */
    async init() {
        try {
            // Load existing history from backend
            const response = await fetch('/api/command-history', {
                method: 'GET'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.history = data.history || [];
                this.historyFile = data.file;
                console.log(`[CommandHistory] Loaded ${this.history.length} commands from ${this.historyFile}`);
            }
        } catch (error) {
            console.error('[CommandHistory] Failed to load history:', error);
            this.history = [];
        }
        
        this.historyIndex = this.history.length;
    },
    
    /**
     * Add a command to history
     * @param {string} command - The command (without brackets)
     */
    async add(command) {
        // Don't add empty commands or duplicates of the last command
        if (!command || command === this.history[this.history.length - 1]) {
            return;
        }
        
        // Add to local history
        this.history.push(command);
        
        // Trim history if too long
        if (this.history.length > this.maxHistory) {
            this.history = this.history.slice(-this.maxHistory);
        }
        
        // Reset index to end
        this.historyIndex = this.history.length;
        
        // Save to backend
        try {
            await fetch('/api/command-history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    command: command
                })
            });
        } catch (error) {
            console.error('[CommandHistory] Failed to save command:', error);
        }
    },
    
    /**
     * Get previous command (up arrow)
     * @returns {string|null} Previous command or null
     */
    getPrevious() {
        if (this.history.length === 0) {
            return null;
        }
        
        if (this.historyIndex > 0) {
            this.historyIndex--;
        }
        
        return this.history[this.historyIndex] || null;
    },
    
    /**
     * Get next command (down arrow)
     * @returns {string|null} Next command or null
     */
    getNext() {
        if (this.history.length === 0) {
            return null;
        }
        
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            return this.history[this.historyIndex];
        } else {
            this.historyIndex = this.history.length;
            return null;  // Clear input when at end
        }
    },
    
    /**
     * Search history for commands starting with prefix
     * @param {string} prefix - Command prefix to search for
     * @returns {array} Matching commands
     */
    search(prefix) {
        if (!prefix) {
            return [];
        }
        
        // Search backwards through history for matches
        const matches = [];
        for (let i = this.history.length - 1; i >= 0; i--) {
            if (this.history[i].startsWith(prefix)) {
                if (!matches.includes(this.history[i])) {
                    matches.push(this.history[i]);
                }
                if (matches.length >= 10) {  // Limit results
                    break;
                }
            }
        }
        
        return matches;
    },
    
    /**
     * Clear history (both local and file)
     */
    async clear() {
        this.history = [];
        this.historyIndex = 0;
        
        try {
            await fetch('/api/command-history', {
                method: 'DELETE'
            });
            console.log('[CommandHistory] History cleared');
        } catch (error) {
            console.error('[CommandHistory] Failed to clear history:', error);
        }
    }
};

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => CommandHistory.init());
} else {
    CommandHistory.init();
}

console.log('[CommandHistory] Module loaded');