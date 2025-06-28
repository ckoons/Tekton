/**
 * DEPRECATED: This file will be removed after CSS-first migration is verified
 * Settings UI Handler
 * Manages the settings UI and connects it to the Settings Manager
 */

console.log('[FILE_TRACE] Loading: settings-ui.js');
class SettingsUI {
    constructor() {
        this.initialized = false;
        this.containerId = 'html-panel'; // Use standard Clean Slate html-panel instead of settings-tab-content
        this.container = null;
        this.settingsManager = window.settingsManager;
    }
    
    /**
     * Initialize the settings UI
     */
    init() {
        console.log('Initializing Settings UI...');
        
        // Make sure settings manager exists
        if (!window.settingsManager) {
            console.error('Settings Manager not found, creating a new one');
            window.settingsManager = new SettingsManager().init();
            this.settingsManager = window.settingsManager;
        }
        
        // Find container - the standard for Clean Slate architecture
        this.container = document.getElementById(this.containerId);
        if (!this.container) {
            console.error('HTML panel not found for Settings UI');
            return;
        }
        
        // Always load the settings component on initialization
        // this.loadSettingsComponent();
        
        return this;
    }
    
    /**
     * Load the settings component HTML
     */
    loadSettingsComponent() {
        console.log('Loading settings component...');
        
        // Load the component using fetch with absolute path
        fetch('/components/settings/settings-component.html')
            .then(response => response.text())
            .then(html => {
                this.container.innerHTML = html;
                console.log('Settings component loaded');
                
                // Now that the component is loaded, finish initialization
                this.setupEventListeners();
                this.updateSettingsUI();
                this.initialized = true;
            })
            .catch(error => {
                console.error('Error loading settings component:', error);
            });
    }
    
    /**
     * Set up event listeners for settings controls
     */
    setupEventListeners() {
        // Theme mode buttons
        document.querySelectorAll('.theme-mode-button').forEach(button => {
            button.addEventListener('click', () => {
                const mode = button.getAttribute('data-mode');
                if (mode && this.settingsManager.settings.themeMode !== mode) {
                    this.settingsManager.settings.themeMode = mode;
                    this.settingsManager.save().applyTheme();
                    this.updateSettingsUI();
                }
            });
        });
        
        // Theme color buttons
        document.querySelectorAll('.theme-color-button').forEach(button => {
            button.addEventListener('click', () => {
                const color = button.getAttribute('data-color');
                if (color) {
                    this.settingsManager.setThemeColor(color);
                    this.updateSettingsUI();
                }
            });
        });
        
        // Greek names toggle
        const greekNamesToggle = document.getElementById('greek-names-toggle');
        if (greekNamesToggle) {
            greekNamesToggle.addEventListener('change', () => {
                this.settingsManager.toggleGreekNames();
                this.updateSettingsUI();
            });
        }
        
        // Terminal font size (simple selector for overall terminal size)
        const fontSizeSelect = document.getElementById('terminal-font-size');
        if (fontSizeSelect) {
            fontSizeSelect.addEventListener('change', () => {
                this.settingsManager.settings.terminalFontSize = fontSizeSelect.value;
                this.settingsManager.save();
                this.applyFontSize();
            });
        }
        
        // Advanced Terminal Settings - Terminal Mode
        const terminalModeSelect = document.getElementById('terminal-mode-select');
        if (terminalModeSelect) {
            terminalModeSelect.addEventListener('change', () => {
                this.settingsManager.settings.terminalMode = terminalModeSelect.value;
                this.settingsManager.save();
                
                // Notify components of mode change
                this.settingsManager.dispatchEvent('terminalModeChanged', {
                    mode: terminalModeSelect.value
                });
            });
        }
        
        // Advanced Terminal Settings - Font Size Slider
        const fontSizeSlider = document.getElementById('terminal-font-size-slider');
        const fontSizeValue = document.getElementById('terminal-font-size-value');
        if (fontSizeSlider && fontSizeValue) {
            fontSizeSlider.addEventListener('input', () => {
                const size = fontSizeSlider.value;
                fontSizeValue.textContent = `${size}px`;
                this.settingsManager.settings.terminalFontSizePx = parseInt(size);
                
                // Live update for immediate feedback
                this.settingsManager.dispatchEvent('terminalFontSizeChanged', {
                    size: parseInt(size)
                });
            });
            
            fontSizeSlider.addEventListener('change', () => {
                this.settingsManager.save();
            });
        }
        
        // Advanced Terminal Settings - Font Family
        const fontFamilySelect = document.getElementById('terminal-font-family');
        if (fontFamilySelect) {
            fontFamilySelect.addEventListener('change', () => {
                this.settingsManager.settings.terminalFontFamily = fontFamilySelect.value;
                this.settingsManager.save();
                
                // Notify components of font change
                this.settingsManager.dispatchEvent('terminalFontFamilyChanged', {
                    fontFamily: fontFamilySelect.value
                });
            });
        }
        
        // Advanced Terminal Settings - Theme
        const terminalThemeSelect = document.getElementById('terminal-theme');
        if (terminalThemeSelect) {
            terminalThemeSelect.addEventListener('change', () => {
                this.settingsManager.settings.terminalTheme = terminalThemeSelect.value;
                this.settingsManager.save();
                
                // Notify components of theme change
                this.settingsManager.dispatchEvent('terminalThemeChanged', {
                    theme: terminalThemeSelect.value
                });
            });
        }
        
        // Advanced Terminal Settings - Cursor Style
        const cursorStyleSelect = document.getElementById('terminal-cursor-style');
        if (cursorStyleSelect) {
            cursorStyleSelect.addEventListener('change', () => {
                this.settingsManager.settings.terminalCursorStyle = cursorStyleSelect.value;
                this.settingsManager.save();
                
                // Notify components of cursor style change
                this.settingsManager.dispatchEvent('terminalCursorStyleChanged', {
                    cursorStyle: cursorStyleSelect.value
                });
            });
        }
        
        // Advanced Terminal Settings - Cursor Blink
        const cursorBlinkToggle = document.getElementById('terminal-cursor-blink');
        if (cursorBlinkToggle) {
            cursorBlinkToggle.addEventListener('change', () => {
                this.settingsManager.settings.terminalCursorBlink = cursorBlinkToggle.checked;
                this.settingsManager.save();
                
                // Notify components of cursor blink change
                this.settingsManager.dispatchEvent('terminalCursorBlinkChanged', {
                    cursorBlink: cursorBlinkToggle.checked
                });
            });
        }
        
        // Advanced Terminal Settings - Scrollback
        const scrollbackToggle = document.getElementById('terminal-scrollback');
        if (scrollbackToggle) {
            scrollbackToggle.addEventListener('change', () => {
                this.settingsManager.settings.terminalScrollback = scrollbackToggle.checked;
                this.settingsManager.save();
                
                // Notify components of scrollback change
                this.settingsManager.dispatchEvent('terminalScrollbackChanged', {
                    scrollback: scrollbackToggle.checked
                });
            });
        }
        
        // Advanced Terminal Settings - Scrollback Lines
        const scrollbackLines = document.getElementById('terminal-scrollback-lines');
        if (scrollbackLines) {
            scrollbackLines.addEventListener('change', () => {
                this.settingsManager.settings.terminalScrollbackLines = parseInt(scrollbackLines.value);
                this.settingsManager.save();
                
                // Notify components of scrollback lines change
                this.settingsManager.dispatchEvent('terminalScrollbackLinesChanged', {
                    lines: parseInt(scrollbackLines.value)
                });
            });
        }
        
        // Advanced Terminal Settings - Inherit OS Terminal Settings
        const inheritOSToggle = document.getElementById('terminal-inherit-os');
        if (inheritOSToggle) {
            inheritOSToggle.addEventListener('change', () => {
                this.settingsManager.settings.terminalInheritOS = inheritOSToggle.checked;
                this.settingsManager.save();
                
                // Notify components
                this.settingsManager.dispatchEvent('terminalInheritOSChanged', {
                    inherit: inheritOSToggle.checked
                });
                
                // If turned on, try to detect OS terminal settings
                if (inheritOSToggle.checked) {
                    this.detectOSTerminalSettings();
                }
            });
        }
        
        // Chat history toggle
        const chatHistoryToggle = document.getElementById('chat-history-toggle');
        if (chatHistoryToggle) {
            chatHistoryToggle.addEventListener('change', () => {
                this.settingsManager.settings.chatHistoryEnabled = chatHistoryToggle.checked;
                this.settingsManager.save();
            });
        }
        
        // Chat history limit
        const chatHistoryLimit = document.getElementById('chat-history-limit');
        if (chatHistoryLimit) {
            chatHistoryLimit.addEventListener('change', () => {
                this.settingsManager.settings.maxChatHistoryEntries = parseInt(chatHistoryLimit.value);
                this.settingsManager.save();
            });
        }
        
        // Clear chat history button
        const clearHistoryButton = document.getElementById('clear-chat-history');
        if (clearHistoryButton) {
            clearHistoryButton.addEventListener('click', () => {
                this.clearAllChatHistory();
            });
        }
        
        // Hermes integration toggle
        const hermesToggle = document.getElementById('hermes-integration-toggle');
        if (hermesToggle) {
            hermesToggle.addEventListener('change', () => {
                const enabled = hermesToggle.checked;
                // Handle Hermes integration toggle
                this.settingsManager.settings.hermesIntegration = enabled;
                this.settingsManager.save();
                
                // Notify applicable components
                this.settingsManager.dispatchEvent('hermesIntegrationChanged', {
                    enabled: enabled
                });
            });
        }
        
        // Default message route
        const defaultRouteSelect = document.getElementById('default-message-route');
        if (defaultRouteSelect) {
            defaultRouteSelect.addEventListener('change', () => {
                this.settingsManager.settings.defaultMessageRoute = defaultRouteSelect.value;
                this.settingsManager.save();
            });
        }
        
        // Reset all settings button
        const resetButton = document.getElementById('reset-all-settings');
        if (resetButton) {
            resetButton.addEventListener('click', () => {
                this.resetAllSettings();
            });
        }
        
        // Save all settings button
        const saveButton = document.getElementById('save-all-settings');
        if (saveButton) {
            saveButton.addEventListener('click', () => {
                this.settingsManager.save();
                this.showSaveConfirmation();
            });
        }
    }
    
    /**
     * Update the UI to reflect current settings
     */
    updateSettingsUI() {
        if (!this.initialized) return;
        
        const settings = this.settingsManager.settings;
        
        // Update theme mode buttons
        document.querySelectorAll('.theme-mode-button').forEach(button => {
            const mode = button.getAttribute('data-mode');
            if (mode === settings.themeMode) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
        
        // Update theme color buttons
        document.querySelectorAll('.theme-color-button').forEach(button => {
            const color = button.getAttribute('data-color');
            if (color === settings.themeColor) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
        
        // Update Greek names toggle
        const greekNamesToggle = document.getElementById('greek-names-toggle');
        if (greekNamesToggle) {
            greekNamesToggle.checked = settings.showGreekNames;
        }
        
        // Update terminal font size
        const fontSizeSelect = document.getElementById('terminal-font-size');
        if (fontSizeSelect) {
            fontSizeSelect.value = settings.terminalFontSize || 'medium';
        }
        
        // Advanced Terminal Settings - Terminal Mode
        const terminalModeSelect = document.getElementById('terminal-mode-select');
        if (terminalModeSelect) {
            terminalModeSelect.value = settings.terminalMode || 'advanced';
        }
        
        // Advanced Terminal Settings - Font Size Slider
        const fontSizeSlider = document.getElementById('terminal-font-size-slider');
        const fontSizeValue = document.getElementById('terminal-font-size-value');
        if (fontSizeSlider && fontSizeValue) {
            const fontSize = settings.terminalFontSizePx || 14;
            fontSizeSlider.value = fontSize;
            fontSizeValue.textContent = `${fontSize}px`;
        }
        
        // Advanced Terminal Settings - Font Family
        const fontFamilySelect = document.getElementById('terminal-font-family');
        if (fontFamilySelect) {
            // Find the closest match or default to first option
            let foundMatch = false;
            for (let i = 0; i < fontFamilySelect.options.length; i++) {
                if (fontFamilySelect.options[i].value === settings.terminalFontFamily) {
                    fontFamilySelect.selectedIndex = i;
                    foundMatch = true;
                    break;
                }
            }
            if (!foundMatch && fontFamilySelect.options.length > 0) {
                fontFamilySelect.selectedIndex = 0;
            }
        }
        
        // Advanced Terminal Settings - Theme
        const terminalThemeSelect = document.getElementById('terminal-theme');
        if (terminalThemeSelect) {
            terminalThemeSelect.value = settings.terminalTheme || 'default';
        }
        
        // Advanced Terminal Settings - Cursor Style
        const cursorStyleSelect = document.getElementById('terminal-cursor-style');
        if (cursorStyleSelect) {
            cursorStyleSelect.value = settings.terminalCursorStyle || 'block';
        }
        
        // Advanced Terminal Settings - Cursor Blink
        const cursorBlinkToggle = document.getElementById('terminal-cursor-blink');
        if (cursorBlinkToggle) {
            cursorBlinkToggle.checked = settings.terminalCursorBlink !== false;
        }
        
        // Advanced Terminal Settings - Scrollback
        const scrollbackToggle = document.getElementById('terminal-scrollback');
        if (scrollbackToggle) {
            scrollbackToggle.checked = settings.terminalScrollback !== false;
        }
        
        // Advanced Terminal Settings - Scrollback Lines
        const scrollbackLines = document.getElementById('terminal-scrollback-lines');
        if (scrollbackLines) {
            scrollbackLines.value = settings.terminalScrollbackLines || 1000;
        }
        
        // Advanced Terminal Settings - Inherit OS
        const inheritOSToggle = document.getElementById('terminal-inherit-os');
        if (inheritOSToggle) {
            inheritOSToggle.checked = settings.terminalInheritOS === true;
        }
        
        // Update chat history toggle
        const chatHistoryToggle = document.getElementById('chat-history-toggle');
        if (chatHistoryToggle) {
            chatHistoryToggle.checked = settings.chatHistoryEnabled !== false;
        }
        
        // Update chat history limit
        const chatHistoryLimit = document.getElementById('chat-history-limit');
        if (chatHistoryLimit) {
            chatHistoryLimit.value = settings.maxChatHistoryEntries || '50';
        }
        
        // Update Hermes integration toggle
        const hermesToggle = document.getElementById('hermes-integration-toggle');
        if (hermesToggle) {
            hermesToggle.checked = settings.hermesIntegration !== false;
        }
        
        // Update default message route
        const defaultRouteSelect = document.getElementById('default-message-route');
        if (defaultRouteSelect) {
            defaultRouteSelect.value = settings.defaultMessageRoute || 'team';
        }
        
        this.applyFontSize();
    }
    
    /**
     * Detect OS terminal settings when available
     * Uses a best-effort approach to detect terminal settings from the OS
     */
    detectOSTerminalSettings() {
        // This method uses navigator.userAgent and platform to make educated guesses
        // about appropriate terminal settings for the OS
        
        console.log('Attempting to detect OS terminal settings');
        
        const ua = navigator.userAgent;
        const platform = navigator.platform || '';
        const settings = this.settingsManager.settings;
        let osName = 'unknown';
        let terminalDefaults = {};
        
        // Detect OS
        if (platform.indexOf('Win') !== -1 || ua.indexOf('Windows') !== -1) {
            osName = 'windows';
            terminalDefaults = {
                fontFamily: "'Consolas', monospace",
                theme: 'dark',
                fontSize: 14,
                cursorStyle: 'block'
            };
        } else if (platform.indexOf('Mac') !== -1 || ua.indexOf('Macintosh') !== -1) {
            osName = 'macos';
            terminalDefaults = {
                fontFamily: "'Menlo', monospace",
                theme: 'default',
                fontSize: 13,
                cursorStyle: 'block'
            };
        } else if (platform.indexOf('Linux') !== -1 || ua.indexOf('Linux') !== -1) {
            osName = 'linux';
            terminalDefaults = {
                fontFamily: "'DejaVu Sans Mono', monospace",
                theme: 'dark',
                fontSize: 14,
                cursorStyle: 'block'
            };
        }
        
        console.log(`Detected OS: ${osName}, applying terminal defaults`);
        
        // Apply OS-specific settings if found
        if (osName !== 'unknown') {
            // Find font family select and look for a close match
            const fontFamilySelect = document.getElementById('terminal-font-family');
            if (fontFamilySelect && terminalDefaults.fontFamily) {
                // Look for a close match to the detected font
                let closestMatch = fontFamilySelect.options[0].value;
                const targetFont = terminalDefaults.fontFamily.toLowerCase();
                
                for (let i = 0; i < fontFamilySelect.options.length; i++) {
                    const option = fontFamilySelect.options[i].value.toLowerCase();
                    if (option.indexOf(targetFont.split("'")[1].toLowerCase()) !== -1) {
                        closestMatch = fontFamilySelect.options[i].value;
                        break;
                    }
                }
                
                // Set the closest match
                settings.terminalFontFamily = closestMatch;
                fontFamilySelect.value = closestMatch;
            }
            
            // Apply other default settings
            if (terminalDefaults.theme) {
                settings.terminalTheme = terminalDefaults.theme;
                const themeSelect = document.getElementById('terminal-theme');
                if (themeSelect) themeSelect.value = terminalDefaults.theme;
            }
            
            if (terminalDefaults.fontSize) {
                settings.terminalFontSizePx = terminalDefaults.fontSize;
                const fontSizeSlider = document.getElementById('terminal-font-size-slider');
                const fontSizeValue = document.getElementById('terminal-font-size-value');
                if (fontSizeSlider) fontSizeSlider.value = terminalDefaults.fontSize;
                if (fontSizeValue) fontSizeValue.textContent = `${terminalDefaults.fontSize}px`;
            }
            
            if (terminalDefaults.cursorStyle) {
                settings.terminalCursorStyle = terminalDefaults.cursorStyle;
                const cursorStyleSelect = document.getElementById('terminal-cursor-style');
                if (cursorStyleSelect) cursorStyleSelect.value = terminalDefaults.cursorStyle;
            }
            
            // Save settings
            this.settingsManager.save();
            
            // Notify components of changes
            this.settingsManager.dispatchEvent('terminalSettingsChanged', {
                settings: {
                    fontFamily: settings.terminalFontFamily,
                    theme: settings.terminalTheme,
                    fontSize: settings.terminalFontSizePx,
                    cursorStyle: settings.terminalCursorStyle
                }
            });
        }
    }
    
    /**
     * Apply font size to terminal elements
     */
    applyFontSize() {
        const size = this.settingsManager.settings.terminalFontSize || 'medium';
        
        // Get the base font size
        let fontSize;
        switch (size) {
            case 'small': fontSize = '0.85rem'; break;
            case 'large': fontSize = '1.1rem'; break;
            default: fontSize = '0.95rem'; break;
        }
        
        // Apply to terminals and chat containers
        document.querySelectorAll('.terminal, .terminal-chat-messages').forEach(el => {
            el.style.fontSize = fontSize;
        });
        
        // Also adjust input fields
        document.querySelectorAll('.terminal-input, .terminal-chat-input').forEach(el => {
            el.style.fontSize = fontSize;
        });
    }
    
    /**
     * Clear all chat history from storage
     */
    clearAllChatHistory() {
        // Show confirmation dialog
        if (confirm('Are you sure you want to clear all chat history? This action cannot be undone.')) {
            // Clear all chat history entries from localStorage
            if (window.storageManager) {
                const keys = [];
                
                // Find all chat history keys
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key.startsWith(storageManager.prefix + 'terminal_chat_history_')) {
                        keys.push(key);
                    }
                }
                
                // Remove each key
                keys.forEach(key => {
                    localStorage.removeItem(key);
                });
                
                // Show confirmation
                alert(`Cleared ${keys.length} chat history entries.`);
                
                // Notify components
                this.settingsManager.dispatchEvent('chatHistoryCleared', {});
            }
        }
    }
    
    /**
     * Reset all settings to defaults
     */
    resetAllSettings() {
        // Show confirmation dialog
        if (confirm('Are you sure you want to reset all settings to their default values?')) {
            // Create default settings
            const defaultSettings = {
                showGreekNames: true,
                themeMode: 'dark',
                themeColor: 'blue',
                chatHistoryEnabled: true,
                maxChatHistoryEntries: 50,
                terminalFontSize: 'medium',
                hermesIntegration: true,
                defaultMessageRoute: 'team',
                
                // Terminal Settings
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
            
            // Apply defaults
            this.settingsManager.settings = defaultSettings;
            this.settingsManager.save().apply();
            
            // Update UI
            this.updateSettingsUI();
            
            // Notify components of terminal settings reset
            this.settingsManager.dispatchEvent('terminalSettingsChanged', {
                settings: {
                    mode: defaultSettings.terminalMode,
                    fontFamily: defaultSettings.terminalFontFamily,
                    fontSize: defaultSettings.terminalFontSizePx,
                    theme: defaultSettings.terminalTheme,
                    cursorStyle: defaultSettings.terminalCursorStyle,
                    cursorBlink: defaultSettings.terminalCursorBlink,
                    scrollback: defaultSettings.terminalScrollback,
                    scrollbackLines: defaultSettings.terminalScrollbackLines
                }
            });
            
            // Show confirmation
            alert('All settings have been reset to their defaults.');
        }
    }
    
    /**
     * Show a save confirmation message
     */
    showSaveConfirmation() {
        // Create or get the notification element
        let notification = document.getElementById('settings-saved-notification');
        
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'settings-saved-notification';
            notification.style.position = 'fixed';
            notification.style.bottom = '20px';
            notification.style.right = '20px';
            notification.style.padding = '10px 20px';
            notification.style.background = 'var(--accent-primary)';
            notification.style.color = 'white';
            notification.style.borderRadius = '4px';
            notification.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
            notification.style.zIndex = '9999';
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.3s ease';
            
            document.body.appendChild(notification);
        }
        
        // Set message and show
        notification.textContent = 'Settings saved successfully';
        notification.style.opacity = '1';
        
        // Hide after a delay
        setTimeout(() => {
            notification.style.opacity = '0';
        }, 3000);
    }
}

// Initialize the settings UI when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Create global instance
    window.settingsUI = new SettingsUI();
    
    // Initialize after UI elements are available
    setTimeout(() => {
        window.settingsUI.init();
    }, 1000);
});