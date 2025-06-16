/**
 * Settings Environment Bridge
 * Extends SettingsManager to integrate with TektonEnvManager
 */

class SettingsEnvBridge {
    constructor() {
        this.baseUrl = `http://localhost:${window.HEPHAESTUS_PORT || 8080}`;
        this.envEndpoint = '/api/environment';
        this.settingsEndpoint = '/api/settings';
        this.initialized = false;
    }

    /**
     * Initialize and sync settings from environment
     */
    async init() {
        if (this.initialized) return;
        
        try {
            console.log('[SettingsEnvBridge] Initializing...');
            
            // Don't sync from environment on init - let SettingsManager control this
            // await this.syncFromEnvironment();
            
            // Hook into SettingsManager save events
            this.hookSettingsManager();
            
            this.initialized = true;
            console.log('[SettingsEnvBridge] Initialized successfully');
        } catch (error) {
            console.error('[SettingsEnvBridge] Initialization error:', error);
        }
    }

    /**
     * Load environment variables and update SettingsManager
     */
    async syncFromEnvironment() {
        if (!window.settingsManager) {
            console.warn('[SettingsEnvBridge] SettingsManager not available');
            return;
        }

        try {
            const response = await fetch(`${this.baseUrl}${this.envEndpoint}/tekton`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                console.warn('[SettingsEnvBridge] Could not load environment, using defaults');
                return;
            }

            const envVars = await response.json();
            const settings = this.envToSettings(envVars);
            
            // Update SettingsManager with environment values
            Object.assign(window.settingsManager.settings, settings);
            
            // Apply settings to UI
            window.settingsManager.apply();
            
            console.log('[SettingsEnvBridge] Settings synced from environment:', settings);
        } catch (error) {
            console.error('[SettingsEnvBridge] Error syncing from environment:', error);
        }
    }

    /**
     * Save current settings to environment
     */
    async syncToEnvironment() {
        if (!window.settingsManager) {
            console.warn('[SettingsEnvBridge] SettingsManager not available');
            return false;
        }

        try {
            const envVars = this.settingsToEnv(window.settingsManager.settings);
            
            const response = await fetch(`${this.baseUrl}${this.settingsEndpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(envVars)
            });

            if (!response.ok) {
                throw new Error(`Failed to save settings: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('[SettingsEnvBridge] Settings saved to environment:', result);
            return true;
        } catch (error) {
            console.error('[SettingsEnvBridge] Error saving to environment:', error);
            return false;
        }
    }

    /**
     * Hook into SettingsManager to automatically sync changes
     */
    hookSettingsManager() {
        if (!window.settingsManager) return;

        // Override the save method to also sync to environment
        const originalSave = window.settingsManager.save.bind(window.settingsManager);
        window.settingsManager.save = () => {
            // Call original save (to localStorage)
            originalSave();
            
            // Also sync to environment
            this.syncToEnvironment().catch(error => {
                console.error('[SettingsEnvBridge] Auto-sync error:', error);
            });
            
            return window.settingsManager;
        };

        console.log('[SettingsEnvBridge] Hooked into SettingsManager save method');
    }

    /**
     * Convert environment variables to SettingsManager format
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
            terminalScrollbackLines: parseInt(envVars.TEKTON_TERMINAL_SCROLLBACK_LINES) || 1000,
            terminalInheritOS: false // Keep existing default
        };
    }

    /**
     * Convert SettingsManager format to environment variables
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
     */
    parseBool(value) {
        if (typeof value === 'boolean') return value;
        if (typeof value === 'string') {
            return value.toLowerCase() === 'true';
        }
        return false;
    }

    /**
     * Manual save trigger for Settings UI
     */
    async saveSettings() {
        console.log('[SettingsEnvBridge] Manual save triggered');
        const success = await this.syncToEnvironment();
        
        if (success) {
            // Also trigger localStorage save
            if (window.settingsManager) {
                window.settingsManager.save();
            }
            
            // Dispatch save event
            window.dispatchEvent(new CustomEvent('tekton-settings-saved', {
                detail: { success: true }
            }));
            
            return true;
        } else {
            window.dispatchEvent(new CustomEvent('tekton-settings-saved', {
                detail: { success: false, error: 'Failed to save to environment' }
            }));
            
            return false;
        }
    }

    /**
     * Reload settings from environment
     */
    async reloadSettings() {
        console.log('[SettingsEnvBridge] Reloading settings from environment');
        await this.syncFromEnvironment();
        
        // Dispatch reload event
        window.dispatchEvent(new CustomEvent('tekton-settings-reloaded'));
    }
}

// Global instance
window.settingsEnvBridge = null;

// Initialize when DOM is ready and SettingsManager is available
document.addEventListener('DOMContentLoaded', () => {
    // Wait for SettingsManager to be ready
    const initBridge = () => {
        if (window.settingsManager && window.settingsManager.initialized) {
            window.settingsEnvBridge = new SettingsEnvBridge();
            window.settingsEnvBridge.init();
        } else {
            setTimeout(initBridge, 500);
        }
    };
    
    setTimeout(initBridge, 1000);
});

// Global function for Settings UI Save button
window.settings_saveAllSettings = async function() {
    console.log('[Settings] Save All Settings triggered');
    
    if (window.settingsEnvBridge) {
        const success = await window.settingsEnvBridge.saveSettings();
        
        if (success) {
            console.log('[Settings] Settings saved successfully');
            // Show success notification if available
            if (window.notifications) {
                window.notifications.show('Settings saved successfully', 'success');
            }
        } else {
            console.error('[Settings] Failed to save settings');
            // Show error notification if available
            if (window.notifications) {
                window.notifications.show('Failed to save settings', 'error');
            }
        }
    } else {
        console.warn('[Settings] SettingsEnvBridge not available, using fallback save');
        if (window.settingsManager) {
            window.settingsManager.save();
        }
    }
};

// Global function for Settings UI Reset button
window.settings_resetAllSettings = async function() {
    console.log('[Settings] Reset All Settings triggered');
    
    if (window.settingsManager) {
        // Reset to defaults
        const defaultSettings = {
            showGreekNames: true,
            themeMode: 'dark',
            themeColor: 'blue',
            chatHistoryEnabled: true,
            maxChatHistoryEntries: 50,
            terminalFontSize: 'medium',
            terminalMode: 'advanced',
            terminalFontSizePx: 14,
            terminalFontFamily: "'Courier New', monospace",
            terminalTheme: 'default',
            terminalCursorStyle: 'block',
            terminalCursorBlink: true,
            terminalScrollback: true,
            terminalScrollbackLines: 1000,
            terminalInheritOS: false
        };
        
        // Update settings
        Object.assign(window.settingsManager.settings, defaultSettings);
        
        // Apply to UI
        window.settingsManager.apply();
        
        // Save both locally and to environment
        if (window.settingsEnvBridge) {
            await window.settingsEnvBridge.saveSettings();
        } else {
            window.settingsManager.save();
        }
        
        console.log('[Settings] Settings reset to defaults');
        
        // Show notification if available
        if (window.notifications) {
            window.notifications.show('Settings reset to defaults', 'info');
        }
    }
};