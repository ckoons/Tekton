/**
 * Environment Bridge for Tekton UI
 * Provides JavaScript interface to TektonEnvManager for Settings and Profile components
 */

class TektonEnvBridge {
    constructor() {
        this.baseUrl = `http://localhost:${window.HEPHAESTUS_PORT || 8080}`;
        this.envEndpoint = '/api/environment';
        this.settingsEndpoint = '/api/settings';
    }

    /**
     * Load current environment variables from server
     * @returns {Promise<Object>} Environment variables
     */
    async loadEnvironment() {
        try {
            const response = await fetch(`${this.baseUrl}${this.envEndpoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to load environment: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('Environment loaded from server:', data);
            return data;
        } catch (error) {
            console.error('Error loading environment:', error);
            // Return default values if server is unavailable
            return this.getDefaultEnvironment();
        }
    }

    /**
     * Save settings to .env.tekton via server
     * @param {Object} settings - Settings to save
     * @returns {Promise<boolean>} Success status
     */
    async saveSettings(settings) {
        try {
            const response = await fetch(`${this.baseUrl}${this.settingsEndpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            });

            if (!response.ok) {
                throw new Error(`Failed to save settings: ${response.statusText}`);
            }

            console.log('Settings saved to server:', settings);
            
            // Update local environment variables
            Object.keys(settings).forEach(key => {
                window[key] = settings[key];
            });

            return true;
        } catch (error) {
            console.error('Error saving settings:', error);
            return false;
        }
    }

    /**
     * Get Tekton-specific environment variables
     * @returns {Promise<Object>} Tekton environment variables
     */
    async getTektonVariables() {
        try {
            const response = await fetch(`${this.baseUrl}${this.envEndpoint}/tekton`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to get Tekton variables: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting Tekton variables:', error);
            return {};
        }
    }

    /**
     * Get default environment values (fallback when server unavailable)
     * @returns {Object} Default environment variables
     */
    getDefaultEnvironment() {
        return {
            // UI Display Settings
            SHOW_GREEK_NAMES: 'true',
            
            // Theme Settings
            TEKTON_THEME_MODE: 'dark',
            TEKTON_THEME_COLOR: 'blue',
            
            // Debug Settings
            TEKTON_DEBUG: 'false',
            TEKTON_LOG_LEVEL: 'INFO',
            
            // Port Assignments
            HEPHAESTUS_PORT: 8080,
            ENGRAM_PORT: 8000,
            HERMES_PORT: 8001,
            ERGON_PORT: 8002,
            RHETOR_PORT: 8003,
            TERMA_PORT: 8004,
            ATHENA_PORT: 8005,
            PROMETHEUS_PORT: 8006,
            HARMONIA_PORT: 8007,
            TELOS_PORT: 8008,
            SYNTHESIS_PORT: 8009,
            TEKTON_CORE_PORT: 8010,
            METIS_PORT: 8011,
            APOLLO_PORT: 8012,
            BUDGET_PORT: 8013,
            SOPHIA_PORT: 8014,
            
            // Terminal Settings
            TEKTON_TERMINAL_MODE: 'advanced',
            TEKTON_TERMINAL_FONT_SIZE: 14,
            TEKTON_TERMINAL_FONT_FAMILY: "'Courier New', monospace",
            TEKTON_TERMINAL_THEME: 'default',
            TEKTON_TERMINAL_CURSOR_STYLE: 'block',
            TEKTON_TERMINAL_CURSOR_BLINK: 'true',
            TEKTON_TERMINAL_SCROLLBACK: 'true',
            TEKTON_TERMINAL_SCROLLBACK_LINES: 1000,
            
            // Chat Settings
            TEKTON_CHAT_HISTORY_ENABLED: 'true',
            TEKTON_CHAT_HISTORY_MAX_ENTRIES: 50,
            
            // Performance Settings
            TEKTON_AUTO_LAUNCH: 'true',
            TEKTON_COMPONENT_TIMEOUT: 30,
            
            // User Preferences
            TEKTON_DEFAULT_MODEL: 'claude-3-sonnet',
            TEKTON_DEFAULT_PROVIDER: 'anthropic',
            TEKTON_NOTIFICATIONS_ENABLED: 'true'
        };
    }

    /**
     * Convert settings object to format expected by SettingsManager
     * @param {Object} envVars - Environment variables
     * @returns {Object} Settings manager format
     */
    envToSettings(envVars) {
        return {
            showGreekNames: this.parseBool(envVars.SHOW_GREEK_NAMES),
            themeMode: envVars.TEKTON_THEME_MODE || 'dark',
            themeColor: envVars.TEKTON_THEME_COLOR || 'blue',
            chatHistoryEnabled: this.parseBool(envVars.TEKTON_CHAT_HISTORY_ENABLED),
            maxChatHistoryEntries: parseInt(envVars.TEKTON_CHAT_HISTORY_MAX_ENTRIES) || 50,
            terminalMode: envVars.TEKTON_TERMINAL_MODE || 'advanced',
            terminalFontSizePx: parseInt(envVars.TEKTON_TERMINAL_FONT_SIZE) || 14,
            terminalFontFamily: envVars.TEKTON_TERMINAL_FONT_FAMILY || "'Courier New', monospace",
            terminalTheme: envVars.TEKTON_TERMINAL_THEME || 'default',
            terminalCursorStyle: envVars.TEKTON_TERMINAL_CURSOR_STYLE || 'block',
            terminalCursorBlink: this.parseBool(envVars.TEKTON_TERMINAL_CURSOR_BLINK),
            terminalScrollback: this.parseBool(envVars.TEKTON_TERMINAL_SCROLLBACK),
            terminalScrollbackLines: parseInt(envVars.TEKTON_TERMINAL_SCROLLBACK_LINES) || 1000
        };
    }

    /**
     * Convert settings object to environment variables format
     * @param {Object} settings - Settings manager format
     * @returns {Object} Environment variables format
     */
    settingsToEnv(settings) {
        return {
            SHOW_GREEK_NAMES: settings.showGreekNames ? 'true' : 'false',
            TEKTON_THEME_MODE: settings.themeMode || 'dark',
            TEKTON_THEME_COLOR: settings.themeColor || 'blue', 
            TEKTON_CHAT_HISTORY_ENABLED: settings.chatHistoryEnabled ? 'true' : 'false',
            TEKTON_CHAT_HISTORY_MAX_ENTRIES: (settings.maxChatHistoryEntries || 50).toString(),
            TEKTON_TERMINAL_MODE: settings.terminalMode || 'advanced',
            TEKTON_TERMINAL_FONT_SIZE: (settings.terminalFontSizePx || 14).toString(),
            TEKTON_TERMINAL_FONT_FAMILY: settings.terminalFontFamily || "'Courier New', monospace",
            TEKTON_TERMINAL_THEME: settings.terminalTheme || 'default',
            TEKTON_TERMINAL_CURSOR_STYLE: settings.terminalCursorStyle || 'block',
            TEKTON_TERMINAL_CURSOR_BLINK: settings.terminalCursorBlink ? 'true' : 'false',
            TEKTON_TERMINAL_SCROLLBACK: settings.terminalScrollback ? 'true' : 'false',
            TEKTON_TERMINAL_SCROLLBACK_LINES: (settings.terminalScrollbackLines || 1000).toString()
        };
    }

    /**
     * Parse boolean value from string
     * @param {string} value - String value to parse
     * @returns {boolean} Boolean value
     */
    parseBool(value) {
        if (typeof value === 'boolean') return value;
        if (typeof value === 'string') {
            return value.toLowerCase() === 'true';
        }
        return false;
    }

    /**
     * Load settings from environment and update SettingsManager
     * @returns {Promise<void>}
     */
    async syncSettingsFromEnv() {
        if (!window.settingsManager) {
            console.warn('SettingsManager not available, skipping environment sync');
            return;
        }

        try {
            const envVars = await this.loadEnvironment();
            const settings = this.envToSettings(envVars);
            
            // Update SettingsManager with environment values
            Object.assign(window.settingsManager.settings, settings);
            
            // Apply settings to UI
            window.settingsManager.apply();
            
            console.log('Settings synced from environment');
        } catch (error) {
            console.error('Error syncing settings from environment:', error);
        }
    }

    /**
     * Save current settings to environment
     * @returns {Promise<boolean>} Success status
     */
    async syncSettingsToEnv() {
        if (!window.settingsManager) {
            console.warn('SettingsManager not available, skipping environment sync');
            return false;
        }

        try {
            const envVars = this.settingsToEnv(window.settingsManager.settings);
            const success = await this.saveSettings(envVars);
            
            if (success) {
                console.log('Settings synced to environment');
            }
            
            return success;
        } catch (error) {
            console.error('Error syncing settings to environment:', error);
            return false;
        }
    }
}

// Create global instance when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.tektonEnvBridge = new TektonEnvBridge();
    
    // Sync settings from environment when SettingsManager is ready
    setTimeout(async () => {
        if (window.settingsManager && window.tektonEnvBridge) {
            await window.tektonEnvBridge.syncSettingsFromEnv();
        }
    }, 1000);
});