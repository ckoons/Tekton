/**
 * DEPRECATED: This file will be removed after CSS-first migration is verified
 * Main JavaScript file for Tekton UI
 * Handles core functionality and initialization
 */

console.log('[FILE_TRACE] Loading: main.js');
// Global tektonUI object for public API
window.tektonUI = {
    activeComponent: 'numa',
    activePanel: 'html',
    debug: true, // Enable debug logging
    
    // Debug logging
    log: function(message, data = null) {
        if (!this.debug) return;
        
        const timestamp = new Date().toISOString();
        const component = "TektonUI";
        
        if (data) {
            console.log(`[${timestamp}] [${component}] ${message}`, data);
        } else {
            console.log(`[${timestamp}] [${component}] ${message}`);
        }
    },
    
    // Methods that will be exposed to component UIs
    sendCommand: function(command, params = {}) {
        this.log(`Sending command: ${command}`, params);
        
        if (window.websocketManager) {
            websocketManager.sendMessage({
                type: "COMMAND",
                source: "UI",
                target: this.activeComponent,
                timestamp: new Date().toISOString(),
                payload: {
                    command: command,
                    ...params
                }
            });
        } else {
            console.error("WebSocket not initialized");
            if (window.terminalManager) {
                terminalManager.write("Error: WebSocket not initialized. Command could not be sent.", false);
            }
        }
    },
    
    switchComponent: function(componentId) {
        if (componentId && componentId !== this.activeComponent) {
            this.log(`Switching component from ${this.activeComponent} to ${componentId}`);
            // Use CSS-first navigation
            const navRadio = document.getElementById(`nav-${componentId}`);
            if (navRadio) {
                navRadio.checked = true;
                navRadio.dispatchEvent(new Event('change'));
                this.activeComponent = componentId;
            } else {
                console.error(`Component navigation radio not found: nav-${componentId}`);
            }
        }
    },
    
    updateTerminal: function(text, isCommand = false) {
        if (window.terminalManager) {
            this.log(`Updating terminal${isCommand ? ' (command)' : ''}: ${text.substring(0, 50)}${text.length > 50 ? '...' : ''}`);
            terminalManager.write(text, isCommand);
        } else {
            console.error("Terminal manager not initialized");
        }
    },
    
    showError: function(message) {
        this.log(`Showing error: ${message}`);
        
        // Also write to terminal if available
        if (window.terminalManager) {
            terminalManager.write(`ERROR: ${message}`, false);
        }
        
        const errorContainer = document.getElementById('error-container');
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 5000);
    },
    
    showModal: function(title, content) {
        this.log(`Showing modal: ${title}`);
        
        const modal = document.getElementById('system-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        
        modalTitle.textContent = title;
        modalBody.innerHTML = content;
        modal.style.display = 'block';
    },
    
    hideModal: function() {
        this.log('Hiding modal');
        
        const modal = document.getElementById('system-modal');
        modal.style.display = 'none';
    }
};

// Initialize the application when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // For testing purposes, let's fetch the component files directly here
    console.log('DEBUGGING: Testing direct fetch of component files');
    
    // Test fetching the component registry
    fetch('server/component_registry.json')
        .then(response => {
            console.log('Registry response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Registry data:', data);
        })
        .catch(error => {
            console.error('Error fetching registry:', error);
        });
    
    // Test fetching the Rhetor component HTML
    fetch('components/rhetor/rhetor-component.html')
        .then(response => {
            console.log('Rhetor HTML response status:', response.status);
            return response.text();
        })
        .then(html => {
            console.log('Rhetor HTML (first 100 chars):', html.substring(0, 100));
        })
        .catch(error => {
            console.error('Error fetching Rhetor HTML:', error);
        });
    
    // Check for cache-busting version to ensure fresh content
    fetch('./.cache-version?' + new Date().getTime())
        .then(response => response.text())
        .then(version => {
            console.log('UI Version:', version);
            
            if (window.terminalManager) {
                terminalManager.write(`Tekton UI Version: ${version}`);
            }
        })
        .catch(() => console.log('No cache version file found, using existing files'));
    
    // Initialize component loader (must be initialized before UI manager)
    if (!window.componentLoader) {
        console.error('Component loader not initialized, will be using legacy component loading');
    }
    
    // Initialize UI manager
    window.uiManager = new UIManager();
    uiManager.init();
    
    // Initialize terminal
    window.terminalManager = new TerminalManager('terminal');
    terminalManager.init();
    
    // Connect radio navigation to component loader
    console.log('Setting up navigation event listeners...');
    document.querySelectorAll('input[name="component-nav"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.checked) {
                const componentId = e.target.id.replace('nav-', '');
                console.log(`Navigation changed to: ${componentId}`);
                if (window.minimalLoader) {
                    window.minimalLoader.loadComponent(componentId);
                } else {
                    console.error('MinimalLoader not available');
                }
            }
        });
    });
    
    // Load initial component (numa is checked by default)
    console.log('Loading initial component: numa');
    if (window.minimalLoader) {
        window.minimalLoader.loadComponent('numa');
    } else {
        console.error('MinimalLoader not available for initial load');
    }
    
    // Initialize localStorage manager
    window.storageManager = new StorageManager();
    
    // Initialize WebSocket connection
    window.websocketManager = new WebSocketManager();
    websocketManager.connect();
    
    // Override the budget button to use our component instead of a modal
    function setupBudgetButton() {
        console.log('Setting up budget button handler...');
        const budgetButton = document.getElementById('budget-button');
        
        if (!budgetButton) {
            console.error('Budget button not found in DOM!');
            return;
        }
        
        console.log('Found budget button:', budgetButton);
        
        // Remove previous click listeners
        budgetButton.removeEventListener('click', handleBudgetClick);
        
        // Define our handler
        function handleBudgetClick(event) {
            console.log('BUDGET BUTTON CLICKED!', event);
            alert('Budget button clicked!');
            
            if (window.uiManager) {
                console.log('UI Manager found, activating budget component...');
                window.uiManager.activateComponent('budget');
            } else {
                console.error('UI Manager not found!');
                if (window.tektonUI) {
                    tektonUI.showModal('Budget', '<div class="budget-panel"><h3>Resource Usage</h3><p>CI Credits: 2,450 / 5,000</p><p>Storage: 1.2 GB / 10 GB</p><p>API Calls: 325 / 1,000</p></div>');
                }
            }
            
            // Prevent event propagation and default
            event.stopPropagation();
            event.preventDefault();
            return false;
        }
        
        // Add our click listener directly
        budgetButton.addEventListener('click', handleBudgetClick);
        console.log('Budget button click handler added');
    }
    
    // Run setup now
    setupBudgetButton();
    
    // Also set up again after a short delay to ensure it's applied 
    // after any other scripts might overwrite it
    setTimeout(setupBudgetButton, 1000);
    
    // Set up status indicators for demo
    setTimeout(() => {
        // Add some status indicators for demonstration
        document.querySelector('.nav-item[data-component="telos"] .status-indicator').classList.add('active');
        
        // After a bit longer, add an alert
        setTimeout(() => {
            document.querySelector('.nav-item[data-component="engram"] .status-indicator').classList.add('alert');
        }, 5000);
    }, 2000);
    
    // Set up modal close button
    document.querySelector('.close-modal').addEventListener('click', function() {
        tektonUI.hideModal();
    });
    
    // Close modal when clicking outside of it
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('system-modal');
        if (event.target === modal) {
            tektonUI.hideModal();
        }
    });
    
    // Theme and settings will now be handled by the settings manager
    // Load saved debug mode preference for compatibility
    const savedDebugMode = storageManager.getItem('debug_mode');
    if (savedDebugMode !== null) {
        tektonUI.debug = savedDebugMode === 'true';
        
        if (window.terminalManager) {
            terminalManager.debugMode = tektonUI.debug;
        }
    }
    
    // Notify user of initialization in terminal
    if (window.terminalManager) {
        terminalManager.write("Tekton Terminal UI initialized");
        terminalManager.write(`Debug mode: ${tektonUI.debug ? 'enabled' : 'disabled'}`);
        terminalManager.write("Type 'help' for available commands");
        
        // Focus terminal input when the terminal container is clicked
        const terminalContainer = document.getElementById('terminal');
        if (terminalContainer) {
            terminalContainer.addEventListener('click', (e) => {
                console.log('Terminal container clicked, focusing input');
                if (window.terminalManager) {
                    terminalManager.focusInput();
                }
                
                // Prevent event propagation
                e.stopPropagation();
            });
        }
        
        // Also focus on document click
        document.addEventListener('click', (e) => {
            // If the terminal panel is active, try to focus the input
            if (tektonUI.activePanel === 'terminal' && window.terminalManager) {
                console.log('Document clicked, focusing terminal input');
                setTimeout(() => terminalManager.focusInput(), 10);
            }
        });
    }
    
// Test function to verify onclick works
window.testClick = function() {
    alert('Click works!');
    return false;
};

// Global Settings Functions - Simple like Rhetor
window.settings_showPanel = function(panelId) {
    console.log('[Settings] Showing panel:', panelId);
    console.log('[Settings] Function called! Panel elements:', document.querySelectorAll('.settings__panel'));
    
    // Update tab states
    const tabs = document.querySelectorAll('.settings__tab');
    console.log('[Settings] Found tabs:', tabs.length);
    tabs.forEach(tab => {
        if (tab.getAttribute('data-tab') === panelId) {
            tab.classList.add('settings__tab--active');
        } else {
            tab.classList.remove('settings__tab--active');
        }
    });
    
    // Update panel visibility
    const panels = document.querySelectorAll('.settings__panel');
    console.log('[Settings] Found panels:', panels.length);
    panels.forEach(panel => {
        panel.classList.remove('settings__panel--active');
    });
    
    const targetPanel = document.getElementById(panelId + '-panel');
    console.log('[Settings] Target panel:', targetPanel);
    if (targetPanel) {
        targetPanel.classList.add('settings__panel--active');
    }
    
    return false; // Prevent default
};

window.settings_setThemeMode = function(mode) {
    console.log('[Settings] Setting theme mode:', mode);
    console.log('[Settings] settingsManager available?', !!window.settingsManager);
    
    // Update button states
    const buttons = document.querySelectorAll('.settings__theme-mode-button');
    buttons.forEach(button => {
        if (button.getAttribute('data-mode') === mode) {
            button.classList.add('settings__theme-mode-button--active');
        } else {
            button.classList.remove('settings__theme-mode-button--active');
        }
    });
    
    // Apply theme
    if (window.settingsManager) {
        window.settingsManager.setThemeBase(mode);
    } else {
        console.error('[Settings] settingsManager not available!');
    }
    
    return false; // Prevent default
};

window.settings_setAccentColor = function(color) {
    console.log('[Settings] Setting accent color:', color);
    
    // Update button states
    const buttons = document.querySelectorAll('.settings__theme-color-button');
    buttons.forEach(button => {
        if (button.getAttribute('data-color') === color) {
            button.classList.add('settings__theme-color-button--active');
        } else {
            button.classList.remove('settings__theme-color-button--active');
        }
    });
    
    // Apply color
    if (window.settingsManager) {
        window.settingsManager.setAccentColor(color);
    }
};

window.settings_toggleGreekNames = function(checked) {
    console.log('[Settings] Toggle Greek names:', checked);
    
    if (window.settingsManager) {
        window.settingsManager.settings.showGreekNames = checked;
        window.settingsManager.save();
        window.settingsManager.applyNames();
    }
};

window.settings_setTerminalFontSize = function(size) {
    console.log('[Settings] Setting terminal font size:', size);
    
    if (window.settingsManager) {
        window.settingsManager.settings.terminalFontSize = size;
        window.settingsManager.save();
    }
};

window.settings_saveAll = function() {
    console.log('[Settings] Saving all settings');
    
    if (window.settingsManager) {
        window.settingsManager.save();
        alert('Settings saved successfully!');
    }
};

window.settings_resetAll = function() {
    if (confirm('Reset all settings to defaults?')) {
        console.log('[Settings] Resetting all settings');
        
        if (window.settingsManager) {
            window.settingsManager.reset();
            
            // Update UI to reflect defaults
            settings_setThemeMode('pure-black');
            settings_setAccentColor('blue');
            
            const greekToggle = document.getElementById('greek-names-toggle');
            if (greekToggle) greekToggle.checked = false;
            
            const fontSelect = document.getElementById('terminal-font-size');
            if (fontSelect) fontSelect.value = 'medium';
        }
    }
};

// Initialize Settings UI when component loads
window.initializeSettingsUI = function() {
    console.log('[Settings] Initializing Settings UI...');
    
    // Add event listeners since onclick might not work
    setTimeout(() => {
        // Tab clicks
        document.querySelectorAll('.settings__tab').forEach(tab => {
            const tabId = tab.getAttribute('data-tab');
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('[Settings] Tab clicked:', tabId);
                settings_showPanel(tabId);
            });
        });
        
        // Theme mode buttons
        document.querySelectorAll('.settings__theme-mode-button').forEach(button => {
            const mode = button.getAttribute('data-mode');
            button.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('[Settings] Theme mode clicked:', mode);
                settings_setThemeMode(mode);
            });
        });
        
        // Accent color buttons
        document.querySelectorAll('.settings__theme-color-button').forEach(button => {
            const color = button.getAttribute('data-color');
            button.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('[Settings] Accent color clicked:', color);
                settings_setAccentColor(color);
            });
        });
        
        // Save button
        const saveBtn = document.querySelector('[onclick*="settings_saveAll"]');
        if (saveBtn) {
            saveBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('[Settings] Save clicked');
                settings_saveAll();
            });
        }
        
        // Reset button
        const resetBtn = document.querySelector('[onclick*="settings_resetAll"]');
        if (resetBtn) {
            resetBtn.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('[Settings] Reset clicked');
                settings_resetAll();
            });
        }
        
        // Greek names toggle
        const greekToggle = document.getElementById('greek-names-toggle');
        if (greekToggle) {
            greekToggle.addEventListener('change', (e) => {
                console.log('[Settings] Greek names toggled:', e.target.checked);
                settings_toggleGreekNames(e.target.checked);
            });
        }
        
        // Terminal font size
        const fontSelect = document.getElementById('terminal-font-size');
        if (fontSelect) {
            fontSelect.addEventListener('change', (e) => {
                console.log('[Settings] Font size changed:', e.target.value);
                settings_setTerminalFontSize(e.target.value);
            });
        }
        
        console.log('[Settings] Event listeners added');
    }, 200);
    
    // Initialize values
    if (window.settingsManager) {
        const settings = window.settingsManager.settings;
        
        // Set initial theme mode
        settings_setThemeMode(settings.themeMode || 'pure-black');
        
        // Set initial accent color
        settings_setAccentColor(settings.themeColor || 'blue');
        
        // Set Greek names toggle
        const greekToggle = document.getElementById('greek-names-toggle');
        if (greekToggle) {
            greekToggle.checked = settings.showGreekNames || false;
        }
        
        // Set terminal font size
        const fontSelect = document.getElementById('terminal-font-size');
        if (fontSelect) {
            fontSelect.value = settings.terminalFontSize || 'medium';
        }
    }
};
    tektonUI.log('Tekton UI initialized');
});