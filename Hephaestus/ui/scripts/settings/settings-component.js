/**
 * Settings Component Script
 * Handles Settings UI functionality without Shadow DOM
 */

console.log('[Settings] Component script loading...');

// Initialize when DOM is ready
function initSettingsComponent() {
    console.log('[Settings] Initializing component...');
    
    // Setup theme button handlers
    setupThemeHandlers();
    
    // Setup interface handlers
    setupInterfaceHandlers();
    
    // Initialize UI state
    updateSettingsUI();
    
    console.log('[Settings] Component initialized');
}

function setupThemeHandlers() {
    // Theme mode buttons
    const themeModeButtons = document.querySelectorAll('.settings-theme-mode__button');
    themeModeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const mode = this.getAttribute('data-mode');
            if (mode && window.settingsManager) {
                // For pure-black theme, use setThemeBase
                if (mode === 'pure-black') {
                    window.settingsManager.setThemeBase('pure-black');
                } else {
                    window.settingsManager.setThemeBase(mode);
                }
                updateThemeModeButtons(mode);
            }
        });
    });

    // Theme color buttons
    const themeColorButtons = document.querySelectorAll('.settings-theme-color__button');
    themeColorButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const color = this.getAttribute('data-color');
            if (color && window.settingsManager) {
                window.settingsManager.setAccentColor(color);
                updateThemeColorButtons(color);
                
                // Show/hide custom color area
                const customColorArea = document.getElementById('custom-color-area');
                if (customColorArea) {
                    customColorArea.style.display = color === 'custom' ? 'flex' : 'none';
                }
            }
        });
    });

    // Custom color input
    const customColorInput = document.getElementById('custom-color-input');
    if (customColorInput) {
        customColorInput.addEventListener('input', function() {
            updateCustomColor(this.value);
        });
    }

    // Color picker from image
    const colorSampleImage = document.getElementById('color-sample-image');
    if (colorSampleImage) {
        colorSampleImage.addEventListener('click', function(e) {
            pickColorFromImage(e);
        });
    }
}

function setupInterfaceHandlers() {
    // Terminal font size
    const terminalFontSize = document.getElementById('terminal-font-size');
    if (terminalFontSize) {
        terminalFontSize.addEventListener('change', function() {
            if (window.settingsManager) {
                window.settingsManager.settings.terminalFontSize = this.value;
                window.settingsManager.save();
            }
        });
    }
}

function updateSettingsUI() {
    if (!window.settingsManager) {
        console.error('[Settings] SettingsManager not available');
        return;
    }

    const settings = window.settingsManager.settings;

    // Update theme mode buttons
    updateThemeModeButtons(settings.themeMode || 'pure-black');

    // Update theme color buttons
    updateThemeColorButtons(settings.themeColor || 'blue');

    // Update Greek names toggle
    const greekToggle = document.getElementById('greek-names-toggle');
    if (greekToggle) {
        greekToggle.checked = settings.showGreekNames || false;
    }

    // Update terminal font size
    const terminalFontSize = document.getElementById('terminal-font-size');
    if (terminalFontSize) {
        terminalFontSize.value = settings.terminalFontSize || 'medium';
    }
}

function updateThemeModeButtons(activeMode) {
    const themeModeButtons = document.querySelectorAll('.settings-theme-mode__button');
    themeModeButtons.forEach(button => {
        const mode = button.getAttribute('data-mode');
        if (mode === activeMode) {
            button.classList.add('settings-theme-mode__button--active');
        } else {
            button.classList.remove('settings-theme-mode__button--active');
        }
    });
}

function updateThemeColorButtons(activeColor) {
    const themeColorButtons = document.querySelectorAll('.settings-theme-color__button');
    themeColorButtons.forEach(button => {
        const color = button.getAttribute('data-color');
        if (color === activeColor) {
            button.classList.add('settings-theme-color__button--active');
        } else {
            button.classList.remove('settings-theme-color__button--active');
        }
    });
}

function updateCustomColor(color) {
    // Update hex display
    const customColorHex = document.getElementById('custom-color-hex');
    if (customColorHex) {
        customColorHex.textContent = color.toUpperCase();
    }

    // Update color canvas
    const colorCanvas = document.getElementById('color-canvas');
    if (colorCanvas) {
        const ctx = colorCanvas.getContext('2d');
        ctx.fillStyle = color;
        ctx.fillRect(0, 0, colorCanvas.width, colorCanvas.height);
    }

    // Update custom button color
    const customButton = document.querySelector('.settings-theme-color__button[data-color="custom"]');
    if (customButton) {
        customButton.style.setProperty('--color', color);
        const colorDot = customButton.querySelector('.settings-theme-color__dot');
        if (colorDot) {
            colorDot.style.backgroundColor = color;
        }
    }

    // Apply custom color if selected
    if (window.settingsManager && window.settingsManager.settings.themeColor === 'custom') {
        window.settingsManager.setCustomAccentColor(color);
    }
}

function pickColorFromImage(event) {
    const image = event.target;
    const rect = image.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Create temporary canvas
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');
    tempCanvas.width = image.width;
    tempCanvas.height = image.height;
    tempCtx.drawImage(image, 0, 0, tempCanvas.width, tempCanvas.height);

    // Get pixel color
    const pixelData = tempCtx.getImageData(x, y, 1, 1).data;
    const hexColor = '#' + ((1 << 24) + (pixelData[0] << 16) + (pixelData[1] << 8) + pixelData[2]).toString(16).slice(1).toUpperCase();

    // Update color picker
    const customColorInput = document.getElementById('custom-color-input');
    if (customColorInput) {
        customColorInput.value = hexColor;
        updateCustomColor(hexColor);
    }

    // Make sure custom button is active
    if (window.settingsManager) {
        window.settingsManager.setAccentColor('custom');
        updateThemeColorButtons('custom');
        document.getElementById('custom-color-area').style.display = 'flex';
    }
}

// Global functions for onclick handlers
window.settings_switchTab = function(tabId) {
    console.log('[Settings] Switching to tab:', tabId);
    
    // Update tab states
    const tabs = document.querySelectorAll('.settings-tab');
    tabs.forEach(tab => {
        if (tab.getAttribute('data-tab') === tabId) {
            tab.classList.add('settings-tab--active');
        } else {
            tab.classList.remove('settings-tab--active');
        }
    });

    // Update panel visibility
    const panels = document.querySelectorAll('.settings-panel');
    panels.forEach(panel => {
        if (panel.id === tabId + '-panel') {
            panel.style.display = 'block';
            panel.classList.add('settings-panel--active');
        } else {
            panel.style.display = 'none';
            panel.classList.remove('settings-panel--active');
        }
    });

    // Initialize tab-specific settings
    if (tabId === 'interface') {
        const greekToggle = document.getElementById('greek-names-toggle');
        if (greekToggle && window.settingsManager) {
            greekToggle.checked = window.settingsManager.settings.showGreekNames || false;
        }
    }

    return false;
};

window.settings_saveAllSettings = function() {
    console.log('[Settings] Saving all settings...');
    
    if (window.settingsManager) {
        window.settingsManager.save();
        console.log('[Settings] Settings saved successfully');
        
        // Show notification if available
        if (window.notifications) {
            window.notifications.show('Settings saved successfully', 'success');
        }
    }
    
    return false;
};

window.settings_resetAllSettings = function() {
    console.log('[Settings] Resetting all settings...');
    
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
        if (window.settingsManager) {
            window.settingsManager.reset();
            
            // Reinitialize UI
            updateSettingsUI();
            
            console.log('[Settings] Settings reset to defaults');
        }
    }
    
    return false;
};

window.settings_toggleGreekNames = function(checkbox) {
    console.log('[Settings] Greek names toggle:', checkbox.checked);
    
    if (window.settingsManager) {
        window.settingsManager.settings.showGreekNames = checkbox.checked;
        window.settingsManager.save();
        window.settingsManager.applyNames();
    }
    
    return true; // Let checkbox update
};

// Initialize when Settings component is loaded
if (window._currentLoadingComponent === 'settings') {
    // Wait for DOM to be ready
    setTimeout(initSettingsComponent, 100);
}

console.log('[Settings] Component script loaded');