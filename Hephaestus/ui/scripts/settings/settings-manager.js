/**
 * Settings Manager
 * Manages user preferences and settings for the Tekton UI
 */

class SettingsManager {
    constructor() {
        this.settings = {
            showGreekNames: true,
            themeMode: 'dark',     // 'dark' or 'light'
            themeColor: 'blue',    // 'blue', 'green', or 'purple'
            chatHistoryEnabled: true,
            maxChatHistoryEntries: 50,
            terminalFontSize: 'medium',  // 'small', 'medium', 'large'
            
            // Terminal Settings
            terminalMode: 'advanced',  // 'advanced' or 'simple'
            terminalFontSizePx: 14,    // pixel size (8-24)
            terminalFontFamily: "'Courier New', monospace",
            terminalTheme: 'default',  // 'default', 'light', 'dark', 'monokai', 'solarized'
            terminalCursorStyle: 'block', // 'block', 'bar', 'underline'
            terminalCursorBlink: true,
            terminalScrollback: true,
            terminalScrollbackLines: 1000,
            terminalInheritOS: false
        };
        this.eventListeners = {};
        this.initialized = false;
    }

    /**
     * Initialize settings
     * Loads settings from storage and applies them
     */
    init() {
        this.load();
        this.apply();
        this.initialized = true;
        console.log('Settings manager initialized');
        
        // Dispatch an initialization event
        this.dispatchEvent('initialized', this.settings);
        
        return this;
    }

    /**
     * Load settings from localStorage
     */
    load() {
        if (window.storageManager) {
            const savedSettings = storageManager.getItem('ui_settings');
            if (savedSettings) {
                try {
                    const parsed = JSON.parse(savedSettings);
                    // Update settings, preserving defaults for any missing values
                    this.settings = {
                        ...this.settings,
                        ...parsed
                    };
                    console.log('Settings loaded from storage', this.settings);
                    
                    // DEBUGGING: Force Rhetor label to LLM/Prompt/Context
                    console.log('DEBUG: Forcing Rhetor label update');
                    storageManager.removeItem('ui_settings');
                } catch (e) {
                    console.error('Error parsing settings:', e);
                }
            } else {
                console.log('No saved settings found, using defaults');
            }
        }
        return this.settings;
    }

    /**
     * Save settings to localStorage
     */
    save() {
        if (window.storageManager) {
            storageManager.setItem('ui_settings', JSON.stringify(this.settings));
            console.log('Settings saved to storage');
        }
        return this;
    }

    /**
     * Apply all settings to the UI
     */
    apply() {
        // Apply all settings
        this.applyTheme();
        this.applyNames();
        
        // Dispatch a change event
        this.dispatchEvent('changed', this.settings);
        
        return this;
    }

    /**
     * Apply theme settings
     */
    applyTheme() {
        const themeName = `${this.settings.themeMode}-${this.settings.themeColor}`;
        
        // Remove all existing theme classes
        document.documentElement.removeAttribute('data-theme');
        
        // Set the new theme attribute
        document.documentElement.setAttribute('data-theme', themeName);
        
        // Update theme stylesheet
        const themeLink = document.getElementById('theme-stylesheet');
        if (themeLink) {
            themeLink.href = `styles/themes/${themeName}.css`;
        }
        
        console.log(`Applied theme: ${themeName}`);
        return this;
    }

    /**
     * Apply component and chat tab naming
     */
    applyNames() {
        // Update component names in navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            const component = item.getAttribute('data-component');
            const label = item.querySelector('.nav-label');
            if (component && label) {
                label.innerHTML = this.getComponentLabel(component);
            }
        });

        // Update the header if a component is active
        const activeNavItem = document.querySelector('.nav-item.active');
        if (activeNavItem) {
            const componentId = activeNavItem.getAttribute('data-component');
            const componentTitle = document.querySelector('.component-title');
            if (componentTitle && componentId) {
                componentTitle.textContent = this.getComponentLabel(componentId);
            }
        }

        // Update chat tab names
        document.querySelectorAll('.tab-button').forEach(tab => {
            const context = tab.getAttribute('data-tab');
            if (context === 'ergon' || context === 'awt-team' || context === 'agora') {
                tab.textContent = this.getChatTabLabel(context);
            }
        });
        
        // Update any component-specific headers that might exist within component containers
        document.querySelectorAll('[id$="-container"] .component-title').forEach(title => {
            const container = title.closest('[id$="-container"]');
            if (container) {
                const componentId = container.id.replace('-container', '');
                if (componentId) {
                    title.textContent = this.getComponentLabel(componentId);
                }
            }
        });
        
        console.log(`Applied naming convention: ${this.settings.showGreekNames ? 'Greek names' : 'Function names'}`);
        
        // Update component headers inside loaded components
        this.updateComponentHeaders();
        
        // Also update again after a delay to catch dynamically loaded components
        setTimeout(() => {
            this.updateComponentHeaders();
        }, 500);
        
        // Dispatch a custom event to notify UI Manager to update its labels
        window.dispatchEvent(new CustomEvent('tekton-names-changed', {
            detail: { showGreekNames: this.settings.showGreekNames }
        }));
        
        return this;
    }

    /**
     * Toggle between light and dark mode
     */
    toggleThemeMode() {
        this.settings.themeMode = this.settings.themeMode === 'dark' ? 'light' : 'dark';
        this.save().applyTheme();
        this.dispatchEvent('themeChanged', this.settings);
        return this;
    }

    /**
     * Set theme color
     * @param {string} color - Color to set ('blue', 'green', or 'purple')
     */
    setThemeColor(color) {
        if (['blue', 'green', 'purple'].includes(color)) {
            this.settings.themeColor = color;
            this.save().applyTheme();
            this.dispatchEvent('themeChanged', this.settings);
        }
        return this;
    }

    /**
     * Toggle Greek names
     */
    toggleGreekNames() {
        this.settings.showGreekNames = !this.settings.showGreekNames;
        this.save().applyNames();
        this.dispatchEvent('namesChanged', this.settings);
        return this;
    }

    /**
     * Update component headers inside loaded components
     */
    updateComponentHeaders() {
        const headerConfigs = {
            'athena': { main: 'Athena', sub: this.settings.showGreekNames ? 'Knowledge Graph' : 'Knowledge' },
            'ergon': { main: this.settings.showGreekNames ? 'Ergon' : '', sub: 'Agents/Tools/MCP' },
            'prometheus': { main: this.settings.showGreekNames ? 'Prometheus' : '', sub: this.settings.showGreekNames ? 'Planning System' : 'Planning' },
            'telos': { main: this.settings.showGreekNames ? 'Telos' : '', sub: this.settings.showGreekNames ? 'Requirements Manager' : 'Requirements' },
            'metis': { main: this.settings.showGreekNames ? 'Metis' : '', sub: this.settings.showGreekNames ? 'Task Management' : 'Workflows' },
            'harmonia': { main: this.settings.showGreekNames ? 'Harmonia' : '', sub: this.settings.showGreekNames ? 'Workflow Orchestration' : 'Orchestration' },
            'synthesis': { main: this.settings.showGreekNames ? 'Synthesis' : '', sub: this.settings.showGreekNames ? 'Execution Engine' : 'Integration' },
            'sophia': { main: this.settings.showGreekNames ? 'Sophia' : '', sub: this.settings.showGreekNames ? 'Intelligence Measurement' : 'Learning' },
            'engram': { main: this.settings.showGreekNames ? 'Engram' : '', sub: this.settings.showGreekNames ? 'Memory System' : 'Memory' },
            'apollo': { main: this.settings.showGreekNames ? 'Apollo' : '', sub: 'Attention/Prediction' },
            'rhetor': { main: this.settings.showGreekNames ? 'Rhetor' : '', sub: 'LLM/Prompt/Context' },
            'hermes': { main: this.settings.showGreekNames ? 'Hermes' : '', sub: 'Messages/Data' },
            'codex': { main: this.settings.showGreekNames ? 'Codex' : '', sub: 'Coding' },
            'tekton': { main: this.settings.showGreekNames ? 'Tekton' : '', sub: this.settings.showGreekNames ? 'Project Management' : 'Projects' },
            'terma': { main: this.settings.showGreekNames ? 'Terma' : '', sub: 'Terminal' },
            'budget': { main: this.settings.showGreekNames ? 'Budget' : '', sub: this.settings.showGreekNames ? 'LLM Cost Management' : 'LLM Cost' },
            'profile': { main: 'Profile', sub: this.settings.showGreekNames ? 'User Information' : '' },
            'settings': { main: 'Settings', sub: this.settings.showGreekNames ? 'Tekton Configuration' : '' }
        };
        
        // Update each component's header if it exists
        Object.keys(headerConfigs).forEach(componentId => {
            const config = headerConfigs[componentId];
            
            // Try multiple selectors to find the elements
            let mainElement = document.querySelector(`.${componentId}__title-main`);
            let subElement = document.querySelector(`.${componentId}__title-sub`);
            
            // Special case for Apollo which has an ID
            if (componentId === 'apollo' && !mainElement) {
                mainElement = document.getElementById('apollo-title-text');
            }
            
            // Also try within component containers
            const container = document.querySelector(`.${componentId}`);
            if (container && !mainElement) {
                mainElement = container.querySelector('[class*="title-main"]');
            }
            if (container && !subElement) {
                subElement = container.querySelector('[class*="title-sub"]');
            }
            
            if (mainElement) {
                if (config.main) {
                    mainElement.textContent = config.main;
                    mainElement.style.display = 'inline';
                } else {
                    // For functional names only, hide the Greek name part
                    mainElement.style.display = 'none';
                }
            }
            
            if (subElement) {
                subElement.textContent = config.sub;
            }
        });
        
        console.log('Updated component headers for naming convention:', this.settings.showGreekNames ? 'Greek names' : 'Function names');
    }

    /**
     * Get component label based on current naming convention
     * @param {string} component - Component ID
     * @returns {string} Formatted component label
     */
    getComponentLabel(component) {
        if (this.settings.showGreekNames) {
            // Return Greek + function format
            switch(component) {
                case 'ergon': return 'Ergon - Agents/Tools/MCP';
                case 'prometheus': return 'Prometheus - Planning';
                case 'telos': return 'Telos - Requirements';
                case 'metis': return 'Metis - Workflows';
                case 'harmonia': return 'Harmonia - Orchestration';
                case 'synthesis': return 'Synthesis - Integration';
                case 'athena': return 'Athena - Knowledge';
                case 'sophia': return 'Sophia - Learning';
                case 'engram': return 'Engram - Memory';
                case 'apollo': return 'Apollo - Attention/Prediction';
                case 'rhetor': return 'Rhetor - LLM/Prompt/Context';
                case 'hermes': return 'Hermes - Messages/Data';
                case 'codex': return 'Codex - Coding';
                case 'tekton': return 'Tekton - Projects';
                case 'terma': return 'Terma - Terminal';
                case 'budget': return 'Budget - LLM Cost';
                case 'profile': return 'Profile';
                case 'settings': return 'Settings';
                default: return component;
            }
        } else {
            // Return function only
            switch(component) {
                case 'ergon': return 'Agents/Tools/MCP';
                case 'prometheus': return 'Planning';
                case 'telos': return 'Requirements';
                case 'metis': return 'Workflows';
                case 'harmonia': return 'Orchestration';
                case 'synthesis': return 'Integration';
                case 'athena': return 'Knowledge';
                case 'sophia': return 'Learning';
                case 'engram': return 'Memory';
                case 'apollo': return 'Attention/Prediction';
                case 'rhetor': return 'LLM/Prompt/Context';
                case 'hermes': return 'Messages/Data';
                case 'codex': return 'Coding';
                case 'tekton': return 'Projects';
                case 'terma': return 'Terminal';
                case 'budget': return 'LLM Cost';
                case 'profile': return 'Profile';
                case 'settings': return 'Settings';
                default: return component;
            }
        }
    }

    /**
     * Get chat tab label based on current naming convention
     * @param {string} context - Chat context identifier
     * @returns {string} Formatted chat tab label
     */
    getChatTabLabel(context) {
        if (this.settings.showGreekNames) {
            switch(context) {
                case 'ergon': return 'Ergon - Tools';
                case 'awt-team': return 'Team Chat';
                case 'agora': return 'Team Chat';
                default: return context;
            }
        } else {
            switch(context) {
                case 'ergon': return 'Tools';
                case 'awt-team': return 'Team Chat';
                case 'agora': return 'Team Chat';
                default: return context;
            }
        }
    }

    /**
     * Get the appropriate welcome message for a chat context
     * @param {string} context - Chat context identifier
     * @returns {string} Welcome message based on current naming convention
     */
    getChatWelcomeMessage(context) {
        if (this.settings.showGreekNames) {
            switch(context) {
                case 'ergon': 
                    return 'Welcome to Ergon AI Assistant. I specialize in agent management, workflow automation, and tool configuration.';
                case 'awt-team': 
                    return 'Welcome to Team Chat. This is where multiple AI specialists collaborate on complex problems.';
                case 'agora': 
                    return 'Welcome to Team Chat. This is where multiple AI specialists collaborate on complex problems.';
                default: 
                    return `Welcome to ${context.charAt(0).toUpperCase() + context.slice(1)}`;
            }
        } else {
            switch(context) {
                case 'ergon': 
                    return 'Welcome to the Tool Chat. I can help you with agents, workflows, and tool configuration.';
                case 'awt-team': 
                    return 'Welcome to Team Chat. Here, multiple AI specialists collaborate on complex problems.';
                case 'agora': 
                    return 'Welcome to Team Chat. Here, multiple AI specialists collaborate on complex problems.';
                default: 
                    return `Welcome to ${context.charAt(0).toUpperCase() + context.slice(1)}`;
            }
        }
    }

    /**
     * Register an event listener
     * @param {string} event - Event name
     * @param {Function} callback - Callback function
     */
    addEventListener(event, callback) {
        if (!this.eventListeners[event]) {
            this.eventListeners[event] = [];
        }
        this.eventListeners[event].push(callback);
        return this;
    }

    /**
     * Remove an event listener
     * @param {string} event - Event name
     * @param {Function} callback - Callback function to remove
     */
    removeEventListener(event, callback) {
        if (this.eventListeners[event]) {
            this.eventListeners[event] = this.eventListeners[event].filter(cb => cb !== callback);
        }
        return this;
    }

    /**
     * Dispatch an event to all listeners
     * @param {string} event - Event name
     * @param {*} data - Event data
     */
    dispatchEvent(event, data) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (e) {
                    console.error(`Error in ${event} event handler:`, e);
                }
            });
        }
        return this;
    }
}

// Create and initialize the settings manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Create global instance
    window.settingsManager = new SettingsManager();
    
    // Initialize after UI elements are available
    setTimeout(() => {
        window.settingsManager.init();
        
        // Re-apply names after components may have loaded
        setTimeout(() => {
            window.settingsManager.applyNames();
        }, 1000);
    }, 500);
    
    // Set up MutationObserver to watch for dynamically loaded components
    const observer = new MutationObserver((mutations) => {
        // Check if any component headers were added
        let componentHeadersAdded = false;
        
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check if this node or its children contain component headers
                        if (node.classList && (
                            node.classList.contains('harmonia') ||
                            node.classList.contains('apollo') ||
                            node.classList.contains('athena') ||
                            node.classList.contains('ergon') ||
                            node.classList.contains('rhetor') ||
                            node.classList.contains('metis') ||
                            node.querySelector && (
                                node.querySelector('[class*="__title-main"]') ||
                                node.querySelector('[class*="__title-sub"]')
                            )
                        )) {
                            componentHeadersAdded = true;
                        }
                    }
                });
            }
        });
        
        // If component headers were added, update them
        if (componentHeadersAdded && window.settingsManager) {
            setTimeout(() => {
                window.settingsManager.updateComponentHeaders();
                console.log('SettingsManager: Updated component headers after DOM change');
            }, 100);
        }
    });
    
    // Start observing the html-panel for changes
    const htmlPanel = document.getElementById('html-panel');
    if (htmlPanel) {
        observer.observe(htmlPanel, {
            childList: true,
            subtree: true
        });
    }
});

// Global function to update component headers (can be called from anywhere)
window.updateComponentHeaders = function() {
    if (window.settingsManager && window.settingsManager.updateComponentHeaders) {
        window.settingsManager.updateComponentHeaders();
    }
};