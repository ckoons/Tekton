/**
 * Settings Component
 * 
 * Manages the settings UI and connects it to the Settings Manager
 * Updated to work within Shadow DOM isolation
 */

(function(component) {
    'use strict';
    
    // Component-specific utilities
    const dom = component.utils.dom;
    const notifications = component.utils.notifications;
    const loading = component.utils.loading;
    const lifecycle = component.utils.lifecycle;
    
    // Service reference
    let settingsService = null;
    
    /**
     * Initialize the settings component
     */
    function initSettingsComponent() {
        console.log('Initializing Settings component...');
        
        // Get or create the settings service
        initSettingsService();
        
        // Set up event listeners
        setupEventListeners();
        
        // Update UI to reflect current settings
        updateSettingsUI();
        
        // Register cleanup function
        component.registerCleanup(cleanupComponent);
        
        console.log('Settings component initialized');
    }
    
    /**
     * Initialize or get the settings service
     */
    function initSettingsService() {
        // Check if the service already exists globally
        if (window.tektonUI?.services?.settingsService) {
            settingsService = window.tektonUI.services.settingsService;
        } else {
            // Dynamically load and initialize the service
            const script = document.createElement('script');
            script.src = '/scripts/settings/settings-service.js';
            document.head.appendChild(script);
            
            // Create a placeholder service until the real one loads
            settingsService = {
                settings: {},
                addEventListener: () => {},
                save: () => ({ apply: () => ({}) }),
                applyTheme: () => {},
                applyNames: () => {},
                setThemeMode: () => {},
                setThemeColor: () => {},
                setGreekNames: () => {},
                resetToDefaults: () => {}
            };
            
            // Poll for service availability
            const checkService = setInterval(() => {
                if (window.tektonUI?.services?.settingsService) {
                    settingsService = window.tektonUI.services.settingsService;
                    updateSettingsUI();
                    clearInterval(checkService);
                }
            }, 100);
            
            // Give up after 5 seconds
            setTimeout(() => {
                clearInterval(checkService);
                if (!window.tektonUI?.services?.settingsService) {
                    notifications.show(component, 'Error', 'Failed to load settings service. Some features may not work correctly.', 'error');
                }
            }, 5000);
        }
        
        return settingsService;
    }
    
    /**
     * Set up event listeners for settings controls
     */
    function setupEventListeners() {
        // Theme mode buttons
        component.on('click', '.settings-theme-mode__button', function(event) {
            const mode = this.getAttribute('data-mode');
            if (mode && settingsService.settings.themeMode !== mode) {
                settingsService.setThemeMode(mode);
                updateSettingsUI();
            }
        });
        
        // Theme color buttons
        component.on('click', '.settings-theme-color__button', function(event) {
            const color = this.getAttribute('data-color');
            if (color) {
                settingsService.setThemeColor(color);
                updateSettingsUI();
            }
        });
        
        // Greek names toggle
        const greekNamesToggle = component.$('#greek-names-toggle');
        if (greekNamesToggle) {
            greekNamesToggle.addEventListener('change', () => {
                settingsService.setGreekNames(greekNamesToggle.checked);
                updateSettingsUI();
            });
        }
        
        // Terminal font size
        const fontSizeSelect = component.$('#terminal-font-size');
        if (fontSizeSelect) {
            fontSizeSelect.addEventListener('change', () => {
                settingsService.settings.terminalFontSize = fontSizeSelect.value;
                settingsService.save();
                applyFontSize();
            });
        }
        
        // Terminal Mode
        const terminalModeSelect = component.$('#terminal-mode-select');
        if (terminalModeSelect) {
            terminalModeSelect.addEventListener('change', () => {
                settingsService.settings.terminalMode = terminalModeSelect.value;
                settingsService.save();
            });
        }
        
        // Font Size Slider
        const fontSizeSlider = component.$('#terminal-font-size-slider');
        const fontSizeValue = component.$('#terminal-font-size-value');
        if (fontSizeSlider && fontSizeValue) {
            fontSizeSlider.addEventListener('input', () => {
                const size = fontSizeSlider.value;
                fontSizeValue.textContent = `${size}px`;
                settingsService.settings.terminalFontSizePx = parseInt(size);
            });
            
            fontSizeSlider.addEventListener('change', () => {
                settingsService.save();
            });
        }
        
        // Font Family
        const fontFamilySelect = component.$('#terminal-font-family');
        if (fontFamilySelect) {
            fontFamilySelect.addEventListener('change', () => {
                settingsService.settings.terminalFontFamily = fontFamilySelect.value;
                settingsService.save();
            });
        }
        
        // Terminal Theme
        const terminalThemeSelect = component.$('#terminal-theme');
        if (terminalThemeSelect) {
            terminalThemeSelect.addEventListener('change', () => {
                settingsService.settings.terminalTheme = terminalThemeSelect.value;
                settingsService.save();
            });
        }
        
        // Cursor Style
        const cursorStyleSelect = component.$('#terminal-cursor-style');
        if (cursorStyleSelect) {
            cursorStyleSelect.addEventListener('change', () => {
                settingsService.settings.terminalCursorStyle = cursorStyleSelect.value;
                settingsService.save();
            });
        }
        
        // Cursor Blink
        const cursorBlinkToggle = component.$('#terminal-cursor-blink');
        if (cursorBlinkToggle) {
            cursorBlinkToggle.addEventListener('change', () => {
                settingsService.settings.terminalCursorBlink = cursorBlinkToggle.checked;
                settingsService.save();
            });
        }
        
        // Scrollback
        const scrollbackToggle = component.$('#terminal-scrollback');
        if (scrollbackToggle) {
            scrollbackToggle.addEventListener('change', () => {
                settingsService.settings.terminalScrollback = scrollbackToggle.checked;
                settingsService.save();
            });
        }
        
        // Scrollback Lines
        const scrollbackLines = component.$('#terminal-scrollback-lines');
        if (scrollbackLines) {
            scrollbackLines.addEventListener('change', () => {
                settingsService.settings.terminalScrollbackLines = parseInt(scrollbackLines.value);
                settingsService.save();
            });
        }
        
        // Inherit OS Terminal Settings
        const inheritOSToggle = component.$('#terminal-inherit-os');
        if (inheritOSToggle) {
            inheritOSToggle.addEventListener('change', () => {
                settingsService.settings.terminalInheritOS = inheritOSToggle.checked;
                settingsService.save();
                
                // If turned on, try to detect OS terminal settings
                if (inheritOSToggle.checked) {
                    detectOSTerminalSettings();
                }
            });
        }
        
        // Chat history toggle
        const chatHistoryToggle = component.$('#chat-history-toggle');
        if (chatHistoryToggle) {
            chatHistoryToggle.addEventListener('change', () => {
                settingsService.settings.chatHistoryEnabled = chatHistoryToggle.checked;
                settingsService.save();
            });
        }
        
        // Chat history limit
        const chatHistoryLimit = component.$('#chat-history-limit');
        if (chatHistoryLimit) {
            chatHistoryLimit.addEventListener('change', () => {
                settingsService.settings.maxChatHistoryEntries = parseInt(chatHistoryLimit.value);
                settingsService.save();
            });
        }
        
        // Clear chat history button
        const clearHistoryButton = component.$('#clear-chat-history');
        if (clearHistoryButton) {
            clearHistoryButton.addEventListener('click', () => {
                clearAllChatHistory();
            });
        }
        
        // Hermes integration toggle
        const hermesToggle = component.$('#hermes-integration-toggle');
        if (hermesToggle) {
            hermesToggle.addEventListener('change', () => {
                settingsService.settings.hermesIntegration = hermesToggle.checked;
                settingsService.save();
            });
        }
        
        // Default message route
        const defaultRouteSelect = component.$('#default-message-route');
        if (defaultRouteSelect) {
            defaultRouteSelect.addEventListener('change', () => {
                settingsService.settings.defaultMessageRoute = defaultRouteSelect.value;
                settingsService.save();
            });
        }
        
        // Reset all settings button
        const resetButton = component.$('#reset-all-settings');
        if (resetButton) {
            resetButton.addEventListener('click', () => {
                resetAllSettings();
            });
        }
        
        // Save all settings button
        const saveButton = component.$('#save-all-settings');
        if (saveButton) {
            saveButton.addEventListener('click', () => {
                settingsService.save();
                showSaveConfirmation();
            });
        }
    }
    
    /**
     * Update the UI to reflect current settings
     */
    function updateSettingsUI() {
        const settings = settingsService.settings;
        
        // Update theme mode buttons
        component.$$('.settings-theme-mode__button').forEach(button => {
            const mode = button.getAttribute('data-mode');
            if (mode === settings.themeMode) {
                button.classList.add('settings-theme-mode__button--active');
            } else {
                button.classList.remove('settings-theme-mode__button--active');
            }
        });
        
        // Update theme color buttons
        component.$$('.settings-theme-color__button').forEach(button => {
            const color = button.getAttribute('data-color');
            if (color === settings.themeColor) {
                button.classList.add('settings-theme-color__button--active');
            } else {
                button.classList.remove('settings-theme-color__button--active');
            }
        });
        
        // Update Greek names toggle
        const greekNamesToggle = component.$('#greek-names-toggle');
        if (greekNamesToggle) {
            greekNamesToggle.checked = settings.showGreekNames;
        }
        
        // Update terminal font size
        const fontSizeSelect = component.$('#terminal-font-size');
        if (fontSizeSelect) {
            fontSizeSelect.value = settings.terminalFontSize || 'medium';
        }
        
        // Terminal Mode
        const terminalModeSelect = component.$('#terminal-mode-select');
        if (terminalModeSelect) {
            terminalModeSelect.value = settings.terminalMode || 'advanced';
        }
        
        // Font Size Slider
        const fontSizeSlider = component.$('#terminal-font-size-slider');
        const fontSizeValue = component.$('#terminal-font-size-value');
        if (fontSizeSlider && fontSizeValue) {
            const fontSize = settings.terminalFontSizePx || 14;
            fontSizeSlider.value = fontSize;
            fontSizeValue.textContent = `${fontSize}px`;
        }
        
        // Font Family
        const fontFamilySelect = component.$('#terminal-font-family');
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
        
        // Terminal Theme
        const terminalThemeSelect = component.$('#terminal-theme');
        if (terminalThemeSelect) {
            terminalThemeSelect.value = settings.terminalTheme || 'default';
        }
        
        // Cursor Style
        const cursorStyleSelect = component.$('#terminal-cursor-style');
        if (cursorStyleSelect) {
            cursorStyleSelect.value = settings.terminalCursorStyle || 'block';
        }
        
        // Cursor Blink
        const cursorBlinkToggle = component.$('#terminal-cursor-blink');
        if (cursorBlinkToggle) {
            cursorBlinkToggle.checked = settings.terminalCursorBlink !== false;
        }
        
        // Scrollback
        const scrollbackToggle = component.$('#terminal-scrollback');
        if (scrollbackToggle) {
            scrollbackToggle.checked = settings.terminalScrollback !== false;
        }
        
        // Scrollback Lines
        const scrollbackLines = component.$('#terminal-scrollback-lines');
        if (scrollbackLines) {
            scrollbackLines.value = settings.terminalScrollbackLines || 1000;
        }
        
        // Inherit OS
        const inheritOSToggle = component.$('#terminal-inherit-os');
        if (inheritOSToggle) {
            inheritOSToggle.checked = settings.terminalInheritOS === true;
        }
        
        // Chat history toggle
        const chatHistoryToggle = component.$('#chat-history-toggle');
        if (chatHistoryToggle) {
            chatHistoryToggle.checked = settings.chatHistoryEnabled !== false;
        }
        
        // Chat history limit
        const chatHistoryLimit = component.$('#chat-history-limit');
        if (chatHistoryLimit) {
            chatHistoryLimit.value = settings.maxChatHistoryEntries || '50';
        }
        
        // Hermes integration toggle
        const hermesToggle = component.$('#hermes-integration-toggle');
        if (hermesToggle) {
            hermesToggle.checked = settings.hermesIntegration !== false;
        }
        
        // Default message route
        const defaultRouteSelect = component.$('#default-message-route');
        if (defaultRouteSelect) {
            defaultRouteSelect.value = settings.defaultMessageRoute || 'team';
        }
    }
    
    /**
     * Detect OS terminal settings when available
     * Uses a best-effort approach to detect terminal settings from the OS
     */
    function detectOSTerminalSettings() {
        // This method uses navigator.userAgent and platform to make educated guesses
        // about appropriate terminal settings for the OS
        
        console.log('Attempting to detect OS terminal settings');
        
        const ua = navigator.userAgent;
        const platform = navigator.platform || '';
        const settings = settingsService.settings;
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
            const fontFamilySelect = component.$('#terminal-font-family');
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
                const themeSelect = component.$('#terminal-theme');
                if (themeSelect) themeSelect.value = terminalDefaults.theme;
            }
            
            if (terminalDefaults.fontSize) {
                settings.terminalFontSizePx = terminalDefaults.fontSize;
                const fontSizeSlider = component.$('#terminal-font-size-slider');
                const fontSizeValue = component.$('#terminal-font-size-value');
                if (fontSizeSlider) fontSizeSlider.value = terminalDefaults.fontSize;
                if (fontSizeValue) fontSizeValue.textContent = `${terminalDefaults.fontSize}px`;
            }
            
            if (terminalDefaults.cursorStyle) {
                settings.terminalCursorStyle = terminalDefaults.cursorStyle;
                const cursorStyleSelect = component.$('#terminal-cursor-style');
                if (cursorStyleSelect) cursorStyleSelect.value = terminalDefaults.cursorStyle;
            }
            
            // Save settings
            settingsService.save();
            
            // Show confirmation
            notifications.show(component, 'OS Settings Applied', `Applied terminal settings from detected ${osName} operating system.`, 'info');
        }
    }
    
    /**
     * Apply font size to terminal elements
     */
    function applyFontSize() {
        // This is now handled by the service and events
        // Just update the UI to match the settings
        updateSettingsUI();
    }
    
    /**
     * Clear all chat history from storage
     */
    function clearAllChatHistory() {
        // Show confirmation dialog using a custom dialog
        showConfirmationDialog(
            'Clear Chat History',
            'Are you sure you want to clear all chat history? This action cannot be undone.',
            () => {
                // Show loading indicator
                loading.show(component, 'Clearing chat history...');
                
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
                    
                    // Hide loading indicator
                    loading.hide(component);
                    
                    // Show confirmation
                    notifications.show(component, 'History Cleared', `Cleared ${keys.length} chat history entries.`, 'success');
                } else {
                    // Hide loading indicator
                    loading.hide(component);
                    
                    // Show error
                    notifications.show(component, 'Error', 'Storage manager not available. Could not clear chat history.', 'error');
                }
            },
            () => {
                // Cancelled - do nothing
            }
        );
    }
    
    /**
     * Reset all settings to defaults
     */
    function resetAllSettings() {
        // Show confirmation dialog
        showConfirmationDialog(
            'Reset Settings',
            'Are you sure you want to reset all settings to their default values?',
            () => {
                // Show loading indicator
                loading.show(component, 'Resetting settings...');
                
                // Reset settings
                setTimeout(() => {
                    settingsService.resetToDefaults();
                    
                    // Hide loading indicator
                    loading.hide(component);
                    
                    // Update UI
                    updateSettingsUI();
                    
                    // Show confirmation
                    notifications.show(component, 'Settings Reset', 'All settings have been reset to their default values.', 'success');
                }, 500);
            },
            () => {
                // Cancelled - do nothing
            }
        );
    }
    
    /**
     * Show a confirmation dialog
     * 
     * @param {string} title - Dialog title
     * @param {string} message - Dialog message
     * @param {Function} onConfirm - Function to call when confirmed
     * @param {Function} onCancel - Function to call when cancelled
     */
    function showConfirmationDialog(title, message, onConfirm, onCancel) {
        // Create dialog element if it doesn't exist
        let dialog = component.$('.settings-dialog');
        if (!dialog) {
            dialog = document.createElement('div');
            dialog.className = 'settings-dialog';
            dialog.innerHTML = `
                <div class="settings-dialog__overlay"></div>
                <div class="settings-dialog__content">
                    <h3 class="settings-dialog__title"></h3>
                    <p class="settings-dialog__message"></p>
                    <div class="settings-dialog__buttons">
                        <button class="settings-button settings-button--secondary settings-dialog__cancel">Cancel</button>
                        <button class="settings-button settings-button--danger settings-dialog__confirm">Confirm</button>
                    </div>
                </div>
            `;
            
            // Add styles if they don't exist
            if (!component.$('#settings-dialog-styles')) {
                const styleElement = document.createElement('style');
                styleElement.id = 'settings-dialog-styles';
                styleElement.textContent = `
                    .settings-dialog {
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        z-index: 2000;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    
                    .settings-dialog__overlay {
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background-color: rgba(0, 0, 0, 0.5);
                    }
                    
                    .settings-dialog__content {
                        position: relative;
                        background-color: var(--bg-card);
                        border-radius: var(--border-radius-md);
                        padding: var(--spacing-md);
                        width: 400px;
                        max-width: 90%;
                        box-shadow: var(--box-shadow-lg);
                    }
                    
                    .settings-dialog__title {
                        margin-top: 0;
                        color: var(--text-primary);
                    }
                    
                    .settings-dialog__message {
                        margin-bottom: var(--spacing-lg);
                        color: var(--text-primary);
                    }
                    
                    .settings-dialog__buttons {
                        display: flex;
                        justify-content: flex-end;
                        gap: var(--spacing-sm);
                    }
                `;
                component.root.appendChild(styleElement);
            }
            
            component.root.appendChild(dialog);
        }
        
        // Set content
        dialog.querySelector('.settings-dialog__title').textContent = title;
        dialog.querySelector('.settings-dialog__message').textContent = message;
        
        // Set event handlers
        const confirmButton = dialog.querySelector('.settings-dialog__confirm');
        const cancelButton = dialog.querySelector('.settings-dialog__cancel');
        const overlay = dialog.querySelector('.settings-dialog__overlay');
        
        // Remove any existing event listeners
        const newConfirmButton = confirmButton.cloneNode(true);
        const newCancelButton = cancelButton.cloneNode(true);
        const newOverlay = overlay.cloneNode(true);
        
        confirmButton.parentNode.replaceChild(newConfirmButton, confirmButton);
        cancelButton.parentNode.replaceChild(newCancelButton, cancelButton);
        overlay.parentNode.replaceChild(newOverlay, overlay);
        
        // Add new event listeners
        newConfirmButton.addEventListener('click', () => {
            dialog.remove();
            if (typeof onConfirm === 'function') {
                onConfirm();
            }
        });
        
        newCancelButton.addEventListener('click', () => {
            dialog.remove();
            if (typeof onCancel === 'function') {
                onCancel();
            }
        });
        
        newOverlay.addEventListener('click', () => {
            dialog.remove();
            if (typeof onCancel === 'function') {
                onCancel();
            }
        });
    }
    
    /**
     * Show a save confirmation message
     */
    function showSaveConfirmation() {
        notifications.show(component, 'Settings Saved', 'Settings saved successfully', 'success');
    }
    
    /**
     * Clean up component resources
     */
    function cleanupComponent() {
        console.log('Cleaning up Settings component');
        
        // No specific cleanup needed as event listeners are scoped to the shadow DOM
        // and will be automatically removed when the component is removed
    }
    
    // Initialize the component
    initSettingsComponent();
    
})(component);