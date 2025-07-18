/**
 * DEPRECATED: This file will be removed after CSS-first migration is verified
 * Settings Manager
 * Manages user preferences and settings for the Tekton UI
 */

console.log('[FILE_TRACE] Loading: settings-manager.js');
class SettingsManager {
    constructor() {
        this.settings = {
            showGreekNames: true,
            themeBase: 'pure-black',     // 'pure-black', 'dark', 'light', 'high-contrast'
            accentColor: '#007bff',     // Hex color for accent
            accentPreset: 'blue',       // 'blue', 'green', 'purple', 'orange', 'red', 'custom'
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
        const root = document.documentElement;
        
        // Apply base theme
        root.setAttribute('data-theme-base', this.settings.themeBase);
        
        // Apply accent color
        this.applyAccentColor(this.settings.accentColor);
        
        // Load theme CSS files
        this.loadThemeStyles();
        
        console.log(`Applied theme: ${this.settings.themeBase} with accent ${this.settings.accentColor}`);
        return this;
    }
    
    /**
     * Apply accent color dynamically
     */
    applyAccentColor(color) {
        const root = document.documentElement;
        
        // Convert hex to HSL for dynamic variations
        const hsl = this.hexToHSL(color);
        
        // Set CSS variables
        root.style.setProperty('--accent-h', hsl.h);
        root.style.setProperty('--accent-s', `${hsl.s}%`);
        root.style.setProperty('--accent-l', `${hsl.l}%`);
        
        // Set direct color values for older browsers
        root.style.setProperty('--color-accent', color);
        
        return this;
    }
    
    /**
     * Load theme stylesheets
     */
    loadThemeStyles() {
        // Get or create theme link elements
        let baseThemeLink = document.getElementById('theme-base-stylesheet');
        if (!baseThemeLink) {
            baseThemeLink = document.createElement('link');
            baseThemeLink.id = 'theme-base-stylesheet';
            baseThemeLink.rel = 'stylesheet';
            document.head.appendChild(baseThemeLink);
        }
        
        let themeLink = document.getElementById('theme-stylesheet');
        if (!themeLink) {
            themeLink = document.createElement('link');
            themeLink.id = 'theme-stylesheet';
            themeLink.rel = 'stylesheet';
            document.head.appendChild(themeLink);
        }
        
        // Load base theme variables
        baseThemeLink.href = 'styles/themes/theme-base.css';
        
        // Load specific theme
        themeLink.href = `styles/themes/theme-${this.settings.themeBase}.css`;
        
        return this;
    }
    
    /**
     * Convert hex color to HSL
     */
    hexToHSL(hex) {
        // Remove # if present
        hex = hex.replace('#', '');
        
        // Convert to RGB
        const r = parseInt(hex.substr(0, 2), 16) / 255;
        const g = parseInt(hex.substr(2, 2), 16) / 255;
        const b = parseInt(hex.substr(4, 2), 16) / 255;
        
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;
        
        if (max === min) {
            h = s = 0; // achromatic
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            
            switch (max) {
                case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
                case g: h = ((b - r) / d + 2) / 6; break;
                case b: h = ((r - g) / d + 4) / 6; break;
            }
        }
        
        return {
            h: Math.round(h * 360),
            s: Math.round(s * 100),
            l: Math.round(l * 100)
        };
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
     * Set base theme
     * @param {string} theme - Theme to set ('pure-black', 'dark', 'light', 'high-contrast')
     */
    setThemeBase(theme) {
        const validThemes = ['pure-black', 'dark', 'light', 'high-contrast'];
        if (validThemes.includes(theme)) {
            this.settings.themeBase = theme;
            this.save().applyTheme();
            this.dispatchEvent('themeChanged', this.settings);
        }
        return this;
    }
    
    /**
     * Set accent color
     * @param {string} color - Hex color code
     * @param {string} preset - Preset name or 'custom'
     */
    setAccentColor(color, preset = 'custom') {
        // Validate hex color
        if (/^#[0-9A-F]{6}$/i.test(color)) {
            this.settings.accentColor = color;
            this.settings.accentPreset = preset;
            this.save();
            this.applyAccentColor(color);
            this.dispatchEvent('accentChanged', {color, preset});
        }
        return this;
    }
    
    /**
     * Set accent preset
     * @param {string} preset - Preset name
     */
    setAccentPreset(preset) {
        const presets = {
            'blue': '#007bff',
            'green': '#28a745',
            'purple': '#6f42c1',
            'orange': '#fd7e14',
            'red': '#dc3545',
            'teal': '#20c997',
            'pink': '#e83e8c',
            'yellow': '#ffc107'
        };
        
        if (presets[preset]) {
            this.setAccentColor(presets[preset], preset);
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
        // Define the header configurations based on SHOW_GREEK_NAMES setting
        const headerConfigs = this.settings.showGreekNames ? {
            // When SHOW_GREEK_NAMES is true: show "Greek Name - Description"
            'numa': { main: 'Numa', sub: 'Companion AI for Tekton Platform' },
            'tekton': { main: 'Tekton', sub: 'Project Management' },
            'prometheus': { main: 'Prometheus', sub: 'Planning' },
            'telos': { main: 'Telos', sub: 'Requirements' },
            'metis': { main: 'Metis', sub: 'Workflows' },
            'harmonia': { main: 'Harmonia', sub: 'Orchestration' },
            'synthesis': { main: 'Synthesis', sub: 'Integration Execution Engine' },
            'athena': { main: 'Athena', sub: 'Knowledge' },
            'sophia': { main: 'Sophia', sub: 'Learning' },
            'noesis': { main: 'Noesis', sub: 'Discovery' },
            'engram': { main: 'Engram', sub: 'Memory' },
            'apollo': { main: 'Apollo', sub: 'Attention/Prediction' },
            'rhetor': { main: 'Rhetor', sub: 'LLM/Prompt/Context' },
            'budget': { main: 'Penia', sub: 'LLM Cost Management' },
            'penia': { main: 'Penia', sub: 'LLM Cost Management' },
            'hermes': { main: 'Hermes', sub: 'Messages/Data' },
            'ergon': { main: 'Ergon', sub: 'Agents/Tools/Mcp' },
            'terma': { main: 'Terma', sub: 'AI Terminals' },
            'profile': { main: 'Profile', sub: '' },
            'settings': { main: 'Settings', sub: '' }
        } : {
            // When SHOW_GREEK_NAMES is false: show only the functional description
            'numa': { main: '', sub: 'Companion AI for Tekton Platform' },
            'tekton': { main: '', sub: 'Project Management' },
            'prometheus': { main: '', sub: 'Planning' },
            'telos': { main: '', sub: 'Requirements' },
            'metis': { main: '', sub: 'Workflows' },
            'harmonia': { main: '', sub: 'Orchestration' },
            'synthesis': { main: '', sub: 'Integration Execution Engine' },
            'athena': { main: '', sub: 'Knowledge' },
            'sophia': { main: '', sub: 'Learning' },
            'noesis': { main: '', sub: 'Discovery' },
            'engram': { main: '', sub: 'Memory' },
            'apollo': { main: '', sub: 'Attention/Prediction' },
            'rhetor': { main: '', sub: 'LLM/Prompt/Context' },
            'budget': { main: '', sub: 'LLM Cost Management' },
            'penia': { main: '', sub: 'LLM Cost Management' },
            'hermes': { main: '', sub: 'Messages/Data' },
            'ergon': { main: '', sub: 'Agents/Tools/Mcp' },
            'terma': { main: '', sub: 'AI Terminals' },
            'profile': { main: 'Profile', sub: '' },
            'settings': { main: 'Settings', sub: '' }
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
                mainElement.textContent = config.main;
                mainElement.style.display = config.main ? 'inline' : 'none';
            }
            
            if (subElement) {
                // Just show the subtitle without any separator
                subElement.textContent = config.sub;
                
                if (config.sub) {
                    subElement.style.display = 'inline';
                } else {
                    subElement.style.display = 'none';
                }
            }
        });
        
        console.log('Updated component headers for naming convention:', this.settings.showGreekNames ? 'Greek names' : 'Function names');
    }

    /**
     * Get component header for RIGHT panel
     * @param {string} component - Component ID
     * @returns {string} Formatted component header for right panel
     */
    getRightPanelHeader(component) {
        if (this.settings.showGreekNames) {
            // When SHOW_GREEK_NAMES is true: return "Greek Name - Description"
            switch(component) {
                case 'numa': return 'Numa - Companion AI for Tekton Platform';
                case 'tekton': return 'Tekton - Project Management';
                case 'prometheus': return 'Prometheus - Planning';
                case 'telos': return 'Telos - Requirements';
                case 'metis': return 'Metis - Workflows';
                case 'harmonia': return 'Harmonia - Orchestration';
                case 'synthesis': return 'Synthesis - Integration Execution Engine';
                case 'athena': return 'Athena - Knowledge';
                case 'sophia': return 'Sophia - Learning';
                case 'noesis': return 'Noesis - Discovery';
                case 'engram': return 'Engram - Memory';
                case 'apollo': return 'Apollo - Attention/Prediction';
                case 'rhetor': return 'Rhetor - LLM/Prompt/Context';
                case 'budget': return 'Penia - LLM Cost Management';
                case 'penia': return 'Penia - LLM Cost Management';
                case 'hermes': return 'Hermes - Messages/Data';
                case 'ergon': return 'Ergon - Agents/Tools/Mcp';
                case 'terma': return 'Terma - AI Terminals';
                case 'profile': return 'Profile';
                case 'settings': return 'Settings';
                default: return component;
            }
        } else {
            // When SHOW_GREEK_NAMES is false: return only the functional description
            switch(component) {
                case 'numa': return 'Companion AI for Tekton Platform';
                case 'tekton': return 'Project Management';
                case 'prometheus': return 'Planning';
                case 'telos': return 'Requirements';
                case 'metis': return 'Workflows';
                case 'harmonia': return 'Orchestration';
                case 'synthesis': return 'Integration Execution Engine';
                case 'athena': return 'Knowledge';
                case 'sophia': return 'Learning';
                case 'noesis': return 'Discovery';
                case 'engram': return 'Memory';
                case 'apollo': return 'Attention/Prediction';
                case 'rhetor': return 'LLM/Prompt/Context';
                case 'budget': return 'LLM Cost Management';
                case 'penia': return 'LLM Cost Management';
                case 'hermes': return 'Messages/Data';
                case 'ergon': return 'Agents/Tools/Mcp';
                case 'terma': return 'AI Terminals';
                case 'profile': return 'Profile';
                case 'settings': return 'Settings';
                default: return component;
            }
        }
    }

    /**
     * Get component label based on current naming convention
     * @param {string} component - Component ID
     * @returns {string} Formatted component label
     */
    getComponentLabel(component) {
        if (this.settings.showGreekNames) {
            // Return Greek + function format with styled spans
            switch(component) {
                case 'numa': return 'Numa<span class="nav-label-sub"> - Companion</span>';
                case 'tekton': return 'Tekton<span class="nav-label-sub"> - Projects</span>';
                case 'prometheus': return 'Prometheus<span class="nav-label-sub"> - Planning</span>';
                case 'telos': return 'Telos<span class="nav-label-sub"> - Requirements</span>';
                case 'metis': return 'Metis<span class="nav-label-sub"> - Workflows</span>';
                case 'harmonia': return 'Harmonia<span class="nav-label-sub"> - Orchestration</span>';
                case 'synthesis': return 'Synthesis<span class="nav-label-sub"> - Integration</span>';
                case 'athena': return 'Athena<span class="nav-label-sub"> - Knowledge</span>';
                case 'sophia': return 'Sophia<span class="nav-label-sub"> - Learning</span>';
                case 'noesis': return 'Noesis<span class="nav-label-sub"> - Discovery</span>';
                case 'engram': return 'Engram<span class="nav-label-sub"> - Memory</span>';
                case 'apollo': return 'Apollo<span class="nav-label-sub"> - Attention/Prediction</span>';
                case 'rhetor': return 'Rhetor<span class="nav-label-sub"> - LLM/Prompt/Context</span>';
                case 'budget': return 'Penia<span class="nav-label-sub"> - LLM Cost</span>';
                case 'penia': return 'Penia<span class="nav-label-sub"> - LLM Cost</span>';
                case 'hermes': return 'Hermes<span class="nav-label-sub"> - Messages/Data</span>';
                case 'ergon': return 'Ergon<span class="nav-label-sub"> - Agents/Tools/MCP</span>';
                case 'terma': return 'Terma<span class="nav-label-sub"> - Terminal</span>';
                case 'profile': return 'Profile';
                case 'settings': return 'Settings';
                default: return component;
            }
        } else {
            // Return function only
            switch(component) {
                case 'numa': return 'Companion';
                case 'tekton': return 'Projects';
                case 'prometheus': return 'Planning';
                case 'telos': return 'Requirements';
                case 'metis': return 'Workflows';
                case 'harmonia': return 'Orchestration';
                case 'synthesis': return 'Integration';
                case 'athena': return 'Knowledge';
                case 'sophia': return 'Learning';
                case 'noesis': return 'Discovery';
                case 'engram': return 'Memory';
                case 'apollo': return 'Attention/Prediction';
                case 'rhetor': return 'LLM/Prompt/Context';
                case 'hermes': return 'Messages/Data';
                case 'ergon': return 'Agents/Tools/MCP';
                case 'terma': return 'Terminal';
                case 'budget': return 'LLM Cost';
                case 'penia': return 'LLM Cost';
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
