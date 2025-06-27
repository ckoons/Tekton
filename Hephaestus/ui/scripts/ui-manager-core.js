/**
 * UI Manager Core (Refactored)
 * Handles core UI functionality including component navigation and panel management
 * Implements a modular architecture with separate component files
 */

class UIManagerCore {
    constructor() {
        this.components = {};
        this.activeComponent = 'numa'; // Default to Numa - Platform AI Mentor
        this.activePanel = 'html'; // Default panel (terminal, html, or settings)
        this.useShadowDOM = false; // Disabled Shadow DOM for direct HTML injection

        // Track component availability
        this.availableComponents = {};
    }
    
    /**
     * Initialize the UI manager
     */
    init() {
        console.log('Initializing UI Manager Core');
        
        // Initialize component utilities if available
        if (window.componentUtils) {
            console.log('Component utilities detected');
        }
        
        // Let settings manager handle all label updates
        // Removed hard-coded label override
        
        // Listen for name changes from settings manager
        window.addEventListener('tekton-names-changed', (event) => {
            console.log('[UIManager] Received names changed event:', event.detail);
            this._updateAllComponentLabels();
        });
        
        // Set up component navigation
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            const componentId = item.getAttribute('data-component');
            if (componentId) {
                item.addEventListener('click', () => {
                    this.activateComponent(componentId);
                });
            }
        });
        
        // Initialize component availability checks
        this.initComponentAvailabilityChecks();
        
        // Profile and Settings components now use the standard component loading process
        // No special handling required as they're loaded via the minimal-loader
        // just like other components
        
        // We don't need to add a click handler for the budget button here.
        // The main.js file already handles this and calls this.activateComponent('budget')
        
        // Set initial active component - ensure Numa loads
        console.log('[UIManager] Loading initial component:', this.activeComponent);
        // Delay initial load to ensure DOM is ready
        setTimeout(() => {
            this.activateComponent('numa'); // Explicitly load Numa
            this.activatePanel('html'); // Switch to HTML panel
        }, 100);
        
        console.log('UI Manager Core initialized (Shadow DOM: ' + (this.useShadowDOM ? 'enabled' : 'disabled') + ')');
        
        // Export core features to global tektonUI for compatibility
        this._exportToTektonUI();
        
        return this;
    }
    
    /**
     * Export core features to global tektonUI object for compatibility
     * with existing code
     */
    _exportToTektonUI() {
        // If tektonUI doesn't exist, create it
        if (!window.tektonUI) {
            window.tektonUI = {};
        }
        
        // Export core properties
        window.tektonUI.activeComponent = this.activeComponent;
        window.tektonUI.activePanel = this.activePanel;
        
        // Export activation methods
        window.tektonUI.activateComponent = (componentId) => this.activateComponent(componentId);
        window.tektonUI.activatePanel = (panelId) => {
            if (window.uiUtils) {
                window.uiUtils.activatePanel(panelId);
            } else {
                this.activatePanel(panelId);
            }
        };
        
        // Export command methods
        window.tektonUI.sendCommand = (command, options = {}) => {
            console.log(`Sending command: ${command}`, options);
            
            // Implement websocket command sending if available
            if (window.websocketManager) {
                websocketManager.sendMessage({
                    type: "COMMAND",
                    source: "UI",
                    target: this.activeComponent || 'SYSTEM',
                    timestamp: new Date().toISOString(),
                    payload: {
                        command: command,
                        ...options
                    }
                });
            } else {
                console.log('WebSocket manager not available, command not sent');
            }
        };
    }
    
    /**
     * Activate a component
     * @param {string} componentId - ID of the component to activate
     */
    activateComponent(componentId) {
        console.log(`Activating component: ${componentId}`);
        
        // Check if this component should be ignored by UI manager
        // This allows components to manage their own UI without interference
        if (this._ignoreComponent === componentId) {
            console.log(`UI Manager: Component ${componentId} has requested to be ignored by UI manager`);
            
            // IMPORTANT FIX: The ignored component is still activated in the navigation menu
            // But we don't interfere with its internal workings
            const navItems = document.querySelectorAll('.nav-item');
            navItems.forEach(item => {
                if (item.getAttribute('data-component') === componentId) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
            
            // Update the component title to reflect the active component
            const componentTitle = document.querySelector('.component-title');
            if (componentTitle && window.settingsManager) {
                // Use settings manager to get the correct label
                componentTitle.textContent = window.settingsManager.getComponentLabel(componentId);
            }
            
            // Just update the active component state and return
            this.activeComponent = componentId;
            if (window.tektonUI) {
                window.tektonUI.activeComponent = componentId;
            }
            
            // We've updated the necessary state, but won't load or modify the component
            return;
        }

        // Use the minimal loader if available (for all components including profile and settings)
        if (window.minimalLoader) {
            console.log(`Using MinimalLoader to load ${componentId}`);
            
            // Activate the HTML panel for component display
            this.activatePanel('html');
            
            window.minimalLoader.loadComponent(componentId);
            return;
        }
        
        // Fallback to ComponentLoader if minimalLoader is not available
        if (window.componentLoader) {
            console.log(`Using ComponentLoader to load ${componentId}`);
            window.componentLoader.loadComponent(componentId);
            return;
        }

        // SPECIAL CASES: Direct component loading for specific components
        // This is the last fallback if both minimalLoader and componentLoader are not available
        const specialComponents = ['rhetor', 'budget', 'hermes', 'engram', 'athena', 'ergon', 'profile', 'settings'];
        if (specialComponents.includes(componentId)) {
            this._loadSpecialComponent(componentId);
            return;
        }
        
        // Update active component in UI
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            if (item.getAttribute('data-component') === componentId) {
                item.classList.add('active');
                // Make status indicator visible for active component
                const statusIndicator = item.querySelector('.status-indicator');
                if (statusIndicator) {
                    statusIndicator.classList.add('active');
                }
            } else {
                item.classList.remove('active');
                // Remove active class from status indicator
                const statusIndicator = item.querySelector('.status-indicator');
                if (statusIndicator) {
                    statusIndicator.classList.remove('active');
                }
            }
        });
        
        // Update component title
        const componentTitle = document.querySelector('.component-title');
        if (componentTitle && window.settingsManager) {
            // Use settings manager to get the correct label
            componentTitle.textContent = window.settingsManager.getComponentLabel(componentId);
        }
        
        // Clear component controls
        const componentControls = document.querySelector('.component-controls');
        if (componentControls) {
            componentControls.innerHTML = '';
        }
        
        // Store the previous component to save its state
        const previousComponent = this.activeComponent;
        
        // Update active component
        this.activeComponent = componentId;
        if (window.tektonUI) {
            window.tektonUI.activeComponent = componentId;
        }
        
        // Save current input for the previous component
        const chatInput = document.getElementById('chat-input');
        if (previousComponent && chatInput) {
            if (window.storageManager) {
                window.storageManager.setInputContext(previousComponent, chatInput.value);
            }
        }
        
        // Load the new component UI if needed
        this.loadComponentUI(componentId);
        
        // Restore input context for the new component
        if (chatInput && window.storageManager) {
            const savedInput = window.storageManager.getInputContext(componentId) || '';
            chatInput.value = savedInput;
            chatInput.style.height = 'auto';
            chatInput.style.height = (chatInput.scrollHeight) + 'px';
        }
        
        // Request current context from the component AI
        if (window.tektonUI) {
            window.tektonUI.sendCommand('get_context');
        }
        
        // Restore terminal history for this component
        if (window.terminalManager) {
            terminalManager.loadHistory(componentId);
        }
    }
    
    /**
     * Load special component types
     * This is for specific components that require special handling
     * @param {string} componentId - ID of the component to load
     */
    _loadSpecialComponent(componentId) {
        console.log(`Loading special component: ${componentId}`);
        
        // Debug log for profile and settings components
        if (componentId === 'profile' || componentId === 'settings') {
            console.log(`SPECIAL COMPONENT DEBUG: Loading ${componentId} via _loadSpecialComponent method`);
        }
        
        // Update active component state first
        this.activeComponent = componentId;
        if (window.tektonUI) {
            window.tektonUI.activeComponent = componentId;
        }
        
        // Special case for Profile and Settings components
        if (componentId === 'profile' || componentId === 'settings') {
            console.log(`Loading ${componentId} component using direct approach...`);
            
            // Get HTML panel for component rendering
            const htmlPanel = document.getElementById('html-panel');
            if (!htmlPanel) {
                console.error('HTML panel not found!');
                return;
            }
            
            // Show loading message
            htmlPanel.innerHTML = `<div style="padding: 20px; text-align: center;">Loading ${componentId} component...</div>`;
            this.activatePanel('html');
            
            // Add cache busting parameter
            const cacheBuster = `?t=${new Date().getTime()}`;
            
            // Load component HTML directly
            fetch(`/components/${componentId}/${componentId}-component.html${cacheBuster}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to load ${componentId} template: ${response.status}`);
                    }
                    return response.text();
                })
                .then(html => {
                    // Clear the panel first
                    htmlPanel.innerHTML = '';
                    
                    // Set innerHTML for the component
                    htmlPanel.innerHTML = html;
                    
                    // Force display styles
                    htmlPanel.style.display = 'block';
                    htmlPanel.style.visibility = 'visible';
                    htmlPanel.style.opacity = '1';
                    
                    console.log(`${componentId} component loaded successfully`);
                    
                    // Force a refresh by triggering a reflow
                    void htmlPanel.offsetWidth;
                    
                    // Debug output
                    console.log(`DEBUG - ${componentId} component HTML:`, html.substring(0, 200) + '...');
                    console.log(`DEBUG - HTML panel now contains:`, htmlPanel.innerHTML.substring(0, 200) + '...');
                })
                .catch(error => {
                    console.error(`Error loading ${componentId} component:`, error);
                    htmlPanel.innerHTML = `<div style="padding: 20px; color: red;">Error loading ${componentId} component: ${error.message}</div>`;
                });
                
            return;
        }

        // Special case for Athena component
        if (componentId === 'athena') {
            console.log('Loading Athena component using direct approach...');
            
            // Get HTML panel for component rendering
            const htmlPanel = document.getElementById('html-panel');
            if (!htmlPanel) {
                console.error('HTML panel not found!');
                return;
            }
            
            // Show loading message
            htmlPanel.innerHTML = '<div style="padding: 20px; text-align: center;">Loading Athena component...</div>';
            this.activatePanel('html');
            
            // Add cache busting parameter
            const cacheBuster = `?t=${new Date().getTime()}`;
            
            // Load component HTML directly
            fetch(`components/athena/athena-component.html${cacheBuster}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to load Athena template: ${response.status}`);
                    }
                    return response.text();
                })
                .then(html => {
                    // Create a container for the component content
                    htmlPanel.innerHTML = html;
                    
                    // Load the component script manually
                    const script = document.createElement('script');
                    script.src = `scripts/athena/athena-component.js${cacheBuster}`;
                    script.onload = () => {
                        console.log('Athena script loaded successfully');
                        // Initialize component if available
                        if (window.athenaComponent) {
                            // Override component initialization to prevent double-loading
                            const originalLoadHtml = window.athenaComponent.loadComponentHTML;
                            window.athenaComponent.loadComponentHTML = function() {
                                console.log('Using pre-loaded HTML for Athena');
                                this.setupTabs();
                                this.setupChat();
                                this.state.initialized = true;
                                return this;
                            };
                            
                            // Initialize the component
                            window.athenaComponent.init();
                        }
                    };
                    document.head.appendChild(script);
                })
                .catch(error => {
                    console.error('Error loading Athena component:', error);
                    htmlPanel.innerHTML = `<div style="padding: 20px; color: red;">Error loading Athena component: ${error.message}</div>`;
                });
            
            return;
        }
        
        // Special case for Ergon component
        if (componentId === 'ergon') {
            console.log('Loading Ergon component using component loader...');
            
            // Get HTML panel for component rendering  
            const htmlPanel = document.getElementById('html-panel');
            if (!htmlPanel) {
                console.error('HTML panel not found!');
                return;
            }
            
            // Set up the panel
            htmlPanel.innerHTML = '<div id="ergon-container" style="width:100%; height:100%;"></div>';
            this.activatePanel('html');
            
            // Use component loader directly
            if (window.componentLoader) {
                const container = document.getElementById('ergon-container');
                window.componentLoader.loadComponent('ergon', container);
            } else {
                console.error('Component loader not available!');
                htmlPanel.innerHTML = '<div style="padding: 20px; color: red;">Component loader not available!</div>';
            }
            return;
        }
        
        // Handle other special components here...
        
        // For components without specific handling, use standard approach
        this.components[componentId] = {
            id: componentId,
            loaded: true,
            usesTerminal: true, // Default to terminal for now
        };
        
        // Activate the appropriate panel for this component
        if (this.components[componentId].usesTerminal) {
            this.activatePanel('terminal');
        } else {
            this.activatePanel('html');
        }
    }
    
    /**
     * Legacy method to load Athena component directly
     * Used as fallback if component class is not available
     */
    _legacyLoadAthenaComponent() {
        console.log('Using legacy method to load Athena component');
        
        // Get HTML panel for component rendering
        const htmlPanel = document.getElementById('html-panel');
        if (!htmlPanel) {
            console.error('HTML panel not found!');
            return;
        }
        
        // Clear the panel and show loading indicator
        if (window.uiUtils) {
            window.uiUtils.showLoadingIndicator(htmlPanel, 'Athena');
        } else {
            htmlPanel.innerHTML = '<div style="padding: 20px;">Loading Athena component...</div>';
        }
        
        // Activate the HTML panel
        if (window.uiUtils) {
            window.uiUtils.activatePanel('html');
        } else {
            this.activatePanel('html');
        }
        
        // Fetch Athena HTML template using standardized nested structure
        const cacheBuster = `?t=${new Date().getTime()}`;
        fetch(`components/athena/athena-component.html`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to load Athena template: ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                // Insert HTML into panel
                htmlPanel.innerHTML = html;
                
                // Setup additional functionality
                this._setupAthenaFunctionality();
                
                // Register component
                this.components['athena'] = {
                    id: 'athena',
                    loaded: true,
                    usesTerminal: false,
                };
                
                console.log('Athena component loaded successfully using legacy method');
            })
            .catch(error => {
                console.error('Error loading Athena component:', error);
                
                // Show error in container
                if (window.uiUtils) {
                    window.uiUtils.showErrorMessage(htmlPanel, 'Athena', error.message);
                } else {
                    htmlPanel.innerHTML = `
                        <div class="error-message">
                            <h3>Error Loading Athena Component</h3>
                            <p>${error.message}</p>
                        </div>
                    `;
                }
                
                // Fallback to terminal panel
                if (window.uiUtils) {
                    window.uiUtils.activatePanel('terminal');
                } else {
                    this.activatePanel('terminal');
                }
            });
    }
    
    /**
     * Setup Athena tab functionality when loaded with legacy method
     */
    _setupAthenaFunctionality() {
        // Set up tabs
        const tabs = document.querySelectorAll('.athena-tab');
        const panels = document.querySelectorAll('.athena-panel');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update active tab
                tabs.forEach(t => {
                    t.classList.remove('active');
                    t.style.borderBottomColor = 'transparent';
                });
                tab.classList.add('active');
                tab.style.borderBottomColor = '#007bff';
                
                // Show active panel
                const panelId = tab.getAttribute('data-panel') + '-panel';
                panels.forEach(panel => {
                    panel.style.display = 'none';
                    panel.classList.remove('active');
                });
                const activePanel = document.getElementById(panelId);
                if (activePanel) {
                    activePanel.style.display = 'block';
                    activePanel.classList.add('active');
                }
                
                // Show/hide the clear chat button
                const clearChatBtn = document.getElementById('clear-chat-btn');
                if (clearChatBtn) {
                    const panelType = tab.getAttribute('data-panel');
                    clearChatBtn.style.display = (panelType === 'chat' || panelType === 'teamchat') ? 'block' : 'none';
                }
            });
        });
    }
    
    /**
     * Legacy method to load Ergon component directly
     * Used as fallback if component class is not available
     */
    _legacyLoadErgonComponent() {
        console.log('Using legacy method to load Ergon component');
        
        // Get HTML panel for component rendering
        const htmlPanel = document.getElementById('html-panel');
        if (!htmlPanel) {
            console.error('HTML panel not found!');
            return;
        }
        
        // Clear the panel and show loading indicator
        if (window.uiUtils) {
            window.uiUtils.showLoadingIndicator(htmlPanel, 'Ergon');
        } else {
            htmlPanel.innerHTML = '<div style="padding: 20px;">Loading Ergon component...</div>';
        }
        
        // Activate the HTML panel
        if (window.uiUtils) {
            window.uiUtils.activatePanel('html');
        } else {
            this.activatePanel('html');
        }
        
        // Fetch Ergon HTML template using standardized nested structure
        const cacheBuster = `?t=${new Date().getTime()}`;
        fetch(`components/ergon/ergon-component.html`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to load Ergon template: ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                // Insert HTML into panel
                htmlPanel.innerHTML = html;
                
                // Setup additional functionality
                this._setupErgonFunctionality();
                
                // Register component
                this.components['ergon'] = {
                    id: 'ergon',
                    loaded: true,
                    usesTerminal: false,
                };
                
                console.log('Ergon component loaded successfully using legacy method');
            })
            .catch(error => {
                console.error('Error loading Ergon component:', error);
                
                // Show error in container
                if (window.uiUtils) {
                    window.uiUtils.showErrorMessage(htmlPanel, 'Ergon', error.message);
                } else {
                    htmlPanel.innerHTML = `
                        <div class="error-message">
                            <h3>Error Loading Ergon Component</h3>
                            <p>${error.message}</p>
                        </div>
                    `;
                }
                
                // Fallback to terminal panel
                if (window.uiUtils) {
                    window.uiUtils.activatePanel('terminal');
                } else {
                    this.activatePanel('terminal');
                }
            });
    }
    
    /**
     * Setup Ergon tab functionality when loaded with legacy method
     */
    _setupErgonFunctionality() {
        // Setup tabs similar to Athena, but for Ergon
        const tabs = document.querySelectorAll('.ergon-tab');
        const panels = document.querySelectorAll('.ergon-panel');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update active tab
                tabs.forEach(t => {
                    t.classList.remove('active');
                    t.style.borderBottomColor = 'transparent';
                });
                tab.classList.add('active');
                tab.style.borderBottomColor = '#007bff';
                
                // Show active panel
                const panelId = tab.getAttribute('data-panel') + '-panel';
                panels.forEach(panel => {
                    panel.style.display = 'none';
                    panel.classList.remove('active');
                });
                const activePanel = document.getElementById(panelId);
                if (activePanel) {
                    activePanel.style.display = 'block';
                    activePanel.classList.add('active');
                }
                
                // Show/hide the clear chat button
                const clearChatBtn = document.getElementById('clear-chat-btn');
                if (clearChatBtn) {
                    const panelType = tab.getAttribute('data-panel');
                    clearChatBtn.style.display = (panelType === 'ergon-chat' || panelType === 'team-chat') ? 'block' : 'none';
                }
            });
        });
    }
    
    /**
     * Load a component's UI
     * @param {string} componentId - ID of the component to load
     */
    async loadComponentUI(componentId) {
        // If we've already loaded this component, just activate it
        if (this.components[componentId]) {
            this.activateComponentUI(componentId);
            return;
        }

        // Get HTML panel for component rendering
        const htmlPanel = document.getElementById('html-panel');
        if (!htmlPanel) {
            console.error('HTML panel not found!');
            return;
        }

        // Use our component loader for all components
        if (window.componentLoader) {
            console.log(`Loading component ${componentId} with component loader`);

            try {
                // Clear any existing content in the HTML panel
                htmlPanel.innerHTML = '';

                // Load the component using the component loader directly
                const component = await window.componentLoader.loadComponent(componentId, htmlPanel);

                if (component) {
                    // Register the component in our local tracking
                    this.components[componentId] = {
                        id: componentId,
                        loaded: true,
                        usesTerminal: false, // Components use HTML panel by default
                        container: htmlPanel
                    };

                    // Activate the HTML panel
                    if (window.uiUtils) {
                        window.uiUtils.activatePanel('html');
                    } else {
                        this.activatePanel('html');
                    }

                    console.log(`Component ${componentId} loaded successfully with component loader`);
                } else {
                    console.error(`Failed to load component ${componentId} with component loader`);

                    // Fallback to terminal panel
                    this.components[componentId] = {
                        id: componentId,
                        loaded: true,
                        usesTerminal: true,
                    };

                    if (window.uiUtils) {
                        window.uiUtils.activatePanel('terminal');
                    } else {
                        this.activatePanel('terminal');
                    }
                }
            } catch (error) {
                console.error(`Error loading component ${componentId} with component loader:`, error);

                // Fallback to terminal panel
                this.components[componentId] = {
                    id: componentId,
                    loaded: true,
                    usesTerminal: true,
                };

                if (window.uiUtils) {
                    window.uiUtils.activatePanel('terminal');
                } else {
                    this.activatePanel('terminal');
                }
            }

            return;
        }

        // Legacy component loading as fallback
        console.log(`Component loader not available, using legacy method for ${componentId}`);

        // Default to terminal for now
        this.components[componentId] = {
            id: componentId,
            loaded: true,
            usesTerminal: true,
        };

        // Activate the terminal panel
        if (window.uiUtils) {
            window.uiUtils.activatePanel('terminal');
        } else {
            this.activatePanel('terminal');
        }
    }
    
    /**
     * Activate a component's UI that was previously loaded
     * @param {string} componentId - ID of the component to activate
     */
    activateComponentUI(componentId) {
        const component = this.components[componentId];
        if (!component) {
            console.error(`Component ${componentId} not found, cannot activate`);
            return;
        }
        
        // Activate the appropriate panel for this component
        if (component.usesTerminal) {
            if (window.uiUtils) {
                window.uiUtils.activatePanel('terminal');
            } else {
                this.activatePanel('terminal');
            }
        } else {
            if (window.uiUtils) {
                window.uiUtils.activatePanel('html');
            } else {
                this.activatePanel('html');
            }
            
            // Special handling for shadow DOM components
            if (component.shadowComponent && component.container) {
                // Make sure only this component's container is visible
                const containers = document.querySelectorAll('.shadow-component-container');
                containers.forEach(container => {
                    if (container.id === `${componentId}-container`) {
                        container.style.display = 'block';
                    } else {
                        container.style.display = 'none';
                    }
                });
            }
        }
        
        console.log(`Activated UI for component: ${componentId}`);
    }
    
    /**
     * Switch between terminal and HTML panels
     * @param {string} panelId - 'terminal' or 'html'
     */
    activatePanel(panelId) {
        console.log(`Activating panel: ${panelId}`);
        
        // Make sure we're dealing with a valid panel ID - we now only support terminal and html panels
        if (!['terminal', 'html'].includes(panelId)) {
            console.error(`Invalid panel ID: ${panelId}`);
            return;
        }
        
        // Get all panels
        const panels = document.querySelectorAll('.panel');
        
        // Hide all panels first
        panels.forEach(panel => {
            panel.classList.remove('active');
            panel.style.display = 'none';
        });
        
        // Now activate the requested panel
        const targetPanel = document.getElementById(`${panelId}-panel`);
        if (targetPanel) {
            // Force display and add active class
            targetPanel.style.display = 'block';
            targetPanel.classList.add('active');
            
            // Update state
            this.activePanel = panelId;
            if (window.tektonUI) {
                window.tektonUI.activePanel = panelId;
            }
        } else {
            console.error(`Panel not found: ${panelId}-panel`);
        }
        
        // Auto-focus on input if terminal panel
        if (panelId === 'terminal') {
            const terminalInput = document.getElementById('simple-terminal-input');
            if (terminalInput) {
                setTimeout(() => {
                    terminalInput.focus();
                }, 100);
            }
        }
    }
    
    // Profile and Settings components now use the standard component loading process via minimal-loader
    // No special panel methods required
    
    /**
     * Initialize component availability checks
     * This sets up periodic checks to see which component backends are available
     */
    initComponentAvailabilityChecks() {
        console.log('Initializing component availability checks');
        
        // Define component health check endpoints
        const componentEndpoints = {
            'numa': '/health',
            'noesis': '/health',
            'hermes': '/health',
            'engram': '/health',
            'ergon': '/health',
            'rhetor': '/health',
            'athena': '/health',
            'prometheus': '/health',
            'harmonia': '/health',
            'sophia': '/health',
            'telos': '/health',
            'codex': '/health',
            'terma': '/health',
            'metis': '/health',
            'apollo': '/health',
            'budget': '/health',
            'synthesis': '/health',
            'tekton': '/health'
        };
        
        // Get port configuration 
        fetch('/api/config/ports')
            .then(response => response.json())
            .catch(error => {
                console.error('Failed to fetch port configuration:', error);
                return {}; // Return empty object if fetch fails
            })
            .then(portConfig => {
                // Convert port config keys to lowercase component IDs
                const normalizedPorts = {};
                Object.keys(portConfig).forEach(key => {
                    // Convert HERMES_PORT to hermes, etc.
                    const componentId = key.replace('_PORT', '').toLowerCase();
                    normalizedPorts[componentId] = portConfig[key];
                });
                
                // Setup periodic health checks for each component
                Object.keys(componentEndpoints).forEach(componentId => {
                    const port = normalizedPorts[componentId] || this._getDefaultPort(componentId);
                    if (port) {
                        this._checkComponentAvailability(componentId, port, componentEndpoints[componentId]);
                        
                        // Setup periodic checks every 15 seconds
                        setInterval(() => {
                            this._checkComponentAvailability(componentId, port, componentEndpoints[componentId]);
                        }, 15000);
                    }
                });
            });
    }
    
    /**
     * Check if a component is available by sending a request to its health endpoint
     * @param {string} componentId - ID of the component to check
     * @param {number} port - Port number the component is listening on
     * @param {string} endpoint - Health check endpoint
     */
    _checkComponentAvailability(componentId, port, endpoint) {
        const url = `http://localhost:${port}${endpoint}`;
        
        fetch(url, { 
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            // Short timeout to avoid long waits
            signal: AbortSignal.timeout(2000)
        })
        .then(response => {
            const available = response.ok;
            this._updateComponentAvailability(componentId, available);
        })
        .catch(error => {
            console.log(`Component ${componentId} health check failed:`, error.name);
            this._updateComponentAvailability(componentId, false);
        });
    }
    
    /**
     * Update the UI to reflect component availability
     * @param {string} componentId - ID of the component
     * @param {boolean} available - Whether the component is available
     */
    _updateComponentAvailability(componentId, available) {
        // Store availability state
        const previouslyAvailable = this.availableComponents[componentId];
        this.availableComponents[componentId] = available;
        
        // Only update UI if availability changed
        if (previouslyAvailable !== available) {
            console.log(`Component ${componentId} availability changed to: ${available}`);
            
            // Update status indicator
            const navItem = document.querySelector(`.nav-item[data-component="${componentId}"]`);
            if (navItem) {
                const statusIndicator = navItem.querySelector('.status-indicator');
                if (statusIndicator) {
                    if (available) {
                        statusIndicator.classList.add('connected');
                    } else {
                        statusIndicator.classList.remove('connected');
                    }
                }
            }
        }
    }
    
    /**
     * Get default port for a component if not found in config
     * @param {string} componentId - ID of the component
     * @returns {number} Port number
     */
    _getDefaultPort(componentId) {
        const defaultPorts = {
            'numa': window.NUMA_PORT || 8016,
            'noesis': window.NOESIS_PORT || 8017,
            'engram': window.ENGRAM_PORT || 8000,
            'hermes': window.HERMES_PORT || 8001,
            'ergon': window.ERGON_PORT || 8002,
            'rhetor': window.RHETOR_PORT || 8003,
            'terma': window.TERMA_PORT || 8004,
            'athena': window.ATHENA_PORT || 8005,
            'prometheus': window.PROMETHEUS_PORT || 8006,
            'harmonia': window.HARMONIA_PORT || 8007,
            'telos': window.TELOS_PORT || 8008,
            'synthesis': window.SYNTHESIS_PORT || 8009,
            'tekton': window.TEKTON_CORE_PORT || 8010,
            'metis': window.METIS_PORT || 8011,
            'apollo': window.APOLLO_PORT || 8012,
            'budget': window.BUDGET_PORT || 8013,
            'sophia': window.SOPHIA_PORT || 8014,
            'codex': window.CODEX_PORT || 8015
        };
        
        return defaultPorts[componentId] || null;
    }
    
    /**
     * Update component controls in the header
     * @param {Object} actions - Array of action objects with id, label, and onClick properties
     */
    updateComponentControls(actions) {
        const controlsContainer = document.querySelector('.component-controls');
        if (!controlsContainer) return;
        
        controlsContainer.innerHTML = '';
        
        if (Array.isArray(actions) && actions.length > 0) {
            actions.forEach(action => {
                const button = document.createElement('button');
                button.className = 'control-button';
                button.textContent = action.label;
                button.addEventListener('click', () => {
                    if (window.tektonUI) {
                        window.tektonUI.sendCommand('execute_action', { actionId: action.id });
                    }
                });
                controlsContainer.appendChild(button);
            });
        }
    }
  
  /**
   * Dynamically load a component from a specific script path
   * This is a specialized method for handling standardized nested structure
   * @param {string} componentId - The component ID (e.g., 'athena')
   * @param {string} scriptPath - The path to the component script file
   */
  _dynamicLoadComponent(componentId, scriptPath) {
    console.log(`Dynamically loading ${componentId} from ${scriptPath}`);
    
    // Update active component in UI
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
      if (item.getAttribute('data-component') === componentId) {
        item.classList.add('active');
        // Make status indicator visible for active component
        const statusIndicator = item.querySelector('.status-indicator');
        if (statusIndicator) {
          statusIndicator.classList.add('active');
        }
      } else {
        item.classList.remove('active');
        // Remove active class from status indicator
        const statusIndicator = item.querySelector('.status-indicator');
        if (statusIndicator) {
          statusIndicator.classList.remove('active');
        }
      }
    });
    
    // Update global state
    this.activeComponent = componentId;
    if (window.tektonUI) {
      window.tektonUI.activeComponent = componentId;
    }
    
    // Access UI panels
    const mainContent = document.querySelector('.main-content');
    const contentMain = document.querySelector('.content-main');
    const terminalPanel = document.getElementById('terminal-panel');
    const htmlPanel = document.getElementById('html-panel');
    
    if (!htmlPanel || !terminalPanel || !mainContent || !contentMain) {
      console.error('Required content panels not found!');
      return;
    }
    
    // First hide all panels
    const panels = document.querySelectorAll('.panel');
    panels.forEach(panel => {
      panel.classList.remove('active');
      panel.style.display = 'none';
    });
    
    // Clear html panel and show loading indicator
    htmlPanel.innerHTML = '<div style="padding: 20px; text-align: center;">Loading component...</div>';
    
    // Show html panel
    htmlPanel.style.display = 'block';
    htmlPanel.classList.add('active');
    
    // Make sure html panel takes full height and width
    htmlPanel.style.width = '100%';
    htmlPanel.style.height = '100%';
    htmlPanel.style.position = 'absolute';
    htmlPanel.style.top = '0';
    htmlPanel.style.left = '0';
    htmlPanel.style.right = '0';
    htmlPanel.style.bottom = '0';
    htmlPanel.style.overflow = 'auto';
    
    // Update active panel state
    this.activePanel = 'html';
    if (window.tektonUI) {
      window.tektonUI.activePanel = 'html';
    }
    
    // For Ergon, we'll use direct HTML loading since the component implementation is completely different
    if (componentId === 'ergon') {
      // Directly load the HTML
      const cacheBuster = `?t=${new Date().getTime()}`;
      fetch(`components/ergon/ergon-component.html${cacheBuster}`)
        .then(response => {
          if (!response.ok) {
            throw new Error(`Failed to load Ergon template: ${response.status}`);
          }
          return response.text();
        })
        .then(html => {
          // Insert HTML into panel
          htmlPanel.innerHTML = html;
          
          // Now load and execute the script for Ergon using a different approach
          const script = document.createElement('script');
          script.src = `${scriptPath}?t=${new Date().getTime()}`;
          script.onload = () => {
            console.log('Ergon script loaded');
            
            // Log what's available in tektonUI
            console.log('tektonUI object contents:', Object.keys(window.tektonUI));
            
            // Create a simple check function to try again after a short delay
            let attempts = 0;
            const maxAttempts = 20; // Try for ~2 seconds max
            
            const checkAndInitialize = () => {
              attempts++;
              if (window.tektonUI && typeof window.tektonUI.initErgonComponent === 'function') {
                console.log('Initialized Ergon component with tektonUI.initErgonComponent');
                window.tektonUI.initErgonComponent(htmlPanel);
              } else if (attempts < maxAttempts) {
                console.log(`tektonUI.initErgonComponent not available yet, trying again in 100ms (attempt ${attempts}/${maxAttempts})`);
                setTimeout(checkAndInitialize, 100);
              } else {
                console.error('Failed to find tektonUI.initErgonComponent after multiple attempts');
                htmlPanel.innerHTML = `<div style="padding: 20px; color: red;">
                  <h3>Error Loading Ergon Component</h3>
                  <p>Could not initialize tektonUI.initErgonComponent after ${maxAttempts} attempts.</p>
                  <p>Please check the console for details.</p>
                </div>`;
              }
            };
            
            // Start checking
            checkAndInitialize();
          };
          document.head.appendChild(script);
        })
        .catch(error => {
          console.error('Error loading Ergon component:', error);
          htmlPanel.innerHTML = `<div style="padding: 20px; color: red;">Error loading Ergon component: ${error.message}</div>`;
        });
      
      return;
    }
    
    // For other components, use the standard approach
    // Dynamically load and execute the script
    const script = document.createElement('script');
    script.src = `${scriptPath}?t=${new Date().getTime()}`; // Cache busting
    script.onload = () => {
      console.log(`${componentId} script loaded successfully`);
      
      // Handle Athena component specially
      if (componentId === 'athena') {
        // Let's re-implement Athena component loading from scratch using nested structure
        console.log('Loading Athena component from nested structure');
        
        // First load the HTML
        const cacheBuster = `?t=${new Date().getTime()}`;
        fetch(`components/athena/athena-component.html${cacheBuster}`)
          .then(response => {
            if (!response.ok) {
              throw new Error(`Failed to load Athena template: ${response.status}`);
            }
            return response.text();
          })
          .then(html => {
            // Insert HTML directly into the panel without any container
            htmlPanel.innerHTML = html;
            
            // Do not add any styles - just let the HTML fill the panel naturally
            
            console.log('Initializing Athena UI elements');
            if (window.athenaComponent) {
              console.log('Calling athenaComponent.loadComponentHTML()');
              // Override loadComponentHTML to avoid conflicting panel manipulation
              const originalLoadHTML = window.athenaComponent.loadComponentHTML;
              window.athenaComponent.loadComponentHTML = function() {
                console.log('Custom loadComponentHTML called - using pre-loaded HTML');
                
                // Skip the HTML loading part but run the setup code
                this.setupTabs();
                this.setupChat();
                
                this.state.initialized = true;
                return this;
              };
              
              // Initialize Athena
              window.athenaComponent.init();
            }
          })
          .catch(error => {
            console.error('Error loading Athena HTML:', error);
            htmlPanel.innerHTML = `<div style="padding: 20px; color: red;">Error loading Athena HTML: ${error.message}</div>`;
          });
      } else {
        console.error(`Global ${componentId} component instance not found after script load or no special handling defined`);
        htmlPanel.innerHTML = `<div style="padding: 20px; color: red;">Error: ${componentId} component not properly initialized</div>`;
      }
    };
    
    script.onerror = (error) => {
      console.error(`Error loading ${componentId} script:`, error);
      htmlPanel.innerHTML = `<div style="padding: 20px; color: red;">Error loading ${componentId} component script</div>`;
    };
    
    // Add the script to the document
    document.head.appendChild(script);
    
    // Register component
    this.components[componentId] = {
      id: componentId,
      loaded: true,
      usesTerminal: false,
    };
  }
  
  /**
   * Update all component labels when naming convention changes
   */
  _updateAllComponentLabels() {
    if (!window.settingsManager) return;
    
    // Update navigation labels
    document.querySelectorAll('.nav-item').forEach(item => {
      const component = item.getAttribute('data-component');
      const label = item.querySelector('.nav-label');
      if (component && label) {
        label.innerHTML = window.settingsManager.getComponentLabel(component);
      }
    });
    
    // Update active component header
    const activeNavItem = document.querySelector('.nav-item.active');
    if (activeNavItem) {
      const componentId = activeNavItem.getAttribute('data-component');
      const componentTitle = document.querySelector('.component-title');
      if (componentTitle && componentId) {
        componentTitle.textContent = window.settingsManager.getComponentLabel(componentId);
      }
    }
    
    // Update any component-specific headers
    document.querySelectorAll('[id$="-container"] .component-title').forEach(title => {
      const container = title.closest('[id$="-container"]');
      if (container) {
        const componentId = container.id.replace('-container', '');
        if (componentId) {
          title.textContent = window.settingsManager.getComponentLabel(componentId);
        }
      }
    });
    
    console.log('[UIManager] Updated all component labels');
  }
}

// Create global instance
window.uiManager = new UIManagerCore();

// Initialize UI Manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.uiManager.init();
});