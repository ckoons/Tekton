/**
 * Terma Component for Hephaestus UI
 * 
 * Terminal component with Shadow DOM isolation that provides:
 * - Advanced terminal with xterm.js integration
 * - Simple terminal fallback mode
 * - WebSocket connection for real-time terminal I/O
 * - Terminal settings management
 * - LLM assistance integration
 */

(function(component) {
    'use strict';
    
    // Utility functions and state references
    const dom = component.utils.dom;
    const notifications = component.utils.notifications;
    const loading = component.utils.loading;
    const lifecycle = component.utils.lifecycle;
    const dialogs = component.utils.dialogs;
    
    // Terminal-specific state
    let termaService = null; // Reference to TermaService
    let advancedTerminal = null; // Reference to xterm.js terminal
    let simpleTerminal = null; // Reference to simple terminal
    let currentTerminalMode = 'advanced'; // 'advanced' or 'simple'
    let llmCollapsed = false; // LLM panel collapsed state
    let loadingIndicator = null; // Terminal loading indicator
    let terminalThemes = {}; // Terminal color themes
    
    // XTerm.js addons
    let fitAddon = null;
    let searchAddon = null;
    let webLinksAddon = null;
    
    /**
     * Initialize the terminal component
     */
    async function initComponent() {
        // Show loading indicator while initializing
        showLoadingIndicator();
        
        try {
            // Get TermaService or create a local instance if not registered globally
            termaService = getTermaService();
            
            // Load required dependencies
            await loadDependencies();
            
            // Setup UI elements and event handlers
            setupUIElements();
            setupEventHandlers();
            
            // Initialize terminals
            await initializeTerminal();
            
            // Initialize settings
            initializeSettings();
            
            // Attach terminal window resize handler
            handleWindowResize();
            
            // Register component cleanup to ensure proper resource management
            registerCleanupHandlers();
            
            // Hide loading indicator
            hideLoadingIndicator();
            
            console.log('Terma component initialized successfully');
        } catch (error) {
            console.error('Error initializing Terma component:', error);
            
            // Show error notification
            notifications.show(component, 'Error', 
                'Failed to initialize terminal component. Check console for details.', 
                'error', 0);
            
            // Hide loading but show error in terminal area
            hideLoadingIndicator();
            showInitializationError(error);
        }
    }
    
    /**
     * Get Terma Service instance
     * @returns {Object} TermaService instance
     */
    function getTermaService() {
        // Check if termaService is registered globally
        if (window.tektonUI && window.tektonUI.services && window.tektonUI.services.termaService) {
            console.log('Using globally registered Terma service');
            return window.tektonUI.services.termaService;
        }
        
        // Create service dynamically if not available globally
        console.log('Creating local Terma service instance');
        
        // Determine URLs based on window location
        const hostname = window.location.hostname || 'localhost';
        const protocol = window.location.protocol || 'http:';
        const serverUrl = `${protocol}//${hostname}:8765`;
        const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${hostname}:8767/ws`;
        
        // Create new service
        const service = new window.tektonUI.componentUtils.BaseService('termaService', serverUrl);
        
        // Extend with necessary methods from terma-service.js
        // This is a minimal implementation for when the full service is not available
        service.wsUrl = wsUrl;
        service.socket = null;
        service.sessionId = null;
        service.sessionList = [];
        service.terminalOptions = {
            fontSize: 14,
            fontFamily: "'Courier New', monospace",
            theme: 'default',
            cursorStyle: 'block',
            cursorBlink: true,
            scrollback: 1000
        };
        
        // Required methods
        service.connectWebSocket = async function(sessionId) {
            try {
                const wsUrl = `${this.wsUrl}/${sessionId}`;
                this.socket = new WebSocket(wsUrl);
                
                // Handle WebSocket events
                this.socket.onopen = () => {
                    console.log(`WebSocket connected to session ${sessionId}`);
                    this.dispatchEvent('websocketConnected', { sessionId });
                };
                
                this.socket.onclose = (event) => {
                    console.log(`WebSocket closed: ${event.code} ${event.reason}`);
                    this.dispatchEvent('websocketClosed', { 
                        code: event.code, 
                        reason: event.reason 
                    });
                };
                
                this.socket.onerror = (error) => {
                    console.error(`WebSocket error: ${error}`);
                    this.dispatchEvent('websocketError', { error });
                };
                
                this.socket.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        switch (message.type) {
                            case 'output':
                                this.dispatchEvent('terminalOutput', { data: message.data });
                                break;
                            case 'error':
                                this.dispatchEvent('terminalError', { message: message.message });
                                break;
                            case 'llm_response':
                                this.dispatchEvent('llmResponse', {
                                    content: message.content,
                                    loading: message.loading === true,
                                    error: message.error === true
                                });
                                break;
                        }
                    } catch (error) {
                        console.error('Error handling WebSocket message:', error);
                    }
                };
                
                // Connect promise
                return new Promise((resolve, reject) => {
                    this.socket.addEventListener('open', () => resolve(true));
                    this.socket.addEventListener('error', reject);
                    
                    // Timeout after 10 seconds
                    setTimeout(() => reject(new Error('WebSocket connection timeout')), 10000);
                });
            } catch (error) {
                console.error('Error connecting WebSocket:', error);
                throw error;
            }
        };
        
        service.closeWebSocketConnection = function() {
            if (this.socket) {
                try {
                    if (this.socket.readyState === WebSocket.OPEN || 
                        this.socket.readyState === WebSocket.CONNECTING) {
                        this.socket.close(1000, "Client closed connection");
                    }
                } catch (error) {
                    console.error('Error closing WebSocket:', error);
                } finally {
                    this.socket = null;
                }
            }
        };
        
        service.sendInput = function(data) {
            if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
                return false;
            }
            
            try {
                const message = JSON.stringify({
                    type: 'input',
                    data: data
                });
                
                this.socket.send(message);
                return true;
            } catch (error) {
                console.error('Error sending input:', error);
                return false;
            }
        };
        
        service.resizeTerminal = function(rows, cols) {
            if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
                return false;
            }
            
            try {
                const message = JSON.stringify({
                    type: 'resize',
                    rows: rows,
                    cols: cols
                });
                
                this.socket.send(message);
                return true;
            } catch (error) {
                console.error('Error sending resize:', error);
                return false;
            }
        };
        
        service.requestLlmAssistance = function(command, isOutputAnalysis = false) {
            if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
                return false;
            }
            
            try {
                const message = JSON.stringify({
                    type: 'llm_assist',
                    command: command,
                    is_output_analysis: isOutputAnalysis
                });
                
                this.socket.send(message);
                return true;
            } catch (error) {
                console.error('Error sending LLM request:', error);
                return false;
            }
        };
        
        service.createSession = async function(shellCommand = null) {
            try {
                this.closeWebSocketConnection();
                
                const payload = {};
                if (shellCommand) {
                    payload.shell_command = shellCommand;
                }
                
                const response = await fetch(`${this.apiUrl}/api/sessions`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to create session: ${response.status}`);
                }
                
                const data = await response.json();
                this.sessionId = data.session_id;
                
                this.dispatchEvent('sessionCreated', { sessionId: this.sessionId });
                
                return this.sessionId;
            } catch (error) {
                console.error('Error creating session:', error);
                this.dispatchEvent('sessionError', { error });
                throw error;
            }
        };
        
        service.fetchSessions = async function() {
            try {
                const response = await fetch(`${this.apiUrl}/api/sessions`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch sessions: ${response.status}`);
                }
                
                const data = await response.json();
                this.sessionList = data.sessions || [];
                
                this.dispatchEvent('sessionsUpdated', { sessions: this.sessionList });
                
                return this.sessionList;
            } catch (error) {
                console.error('Error fetching sessions:', error);
                return [];
            }
        };
        
        service.connectToSession = async function(sessionId) {
            try {
                this.closeWebSocketConnection();
                this.sessionId = sessionId;
                
                const result = await this.connectWebSocket(sessionId);
                
                this.dispatchEvent('sessionConnected', { sessionId });
                
                return result;
            } catch (error) {
                console.error(`Error connecting to session ${sessionId}:`, error);
                this.dispatchEvent('sessionError', { error, sessionId });
                throw error;
            }
        };
        
        service.loadSettings = function() {
            try {
                const savedSettings = localStorage.getItem('terma_terminal_settings');
                if (savedSettings) {
                    this.terminalOptions = {
                        ...this.terminalOptions,
                        ...JSON.parse(savedSettings)
                    };
                }
            } catch (error) {
                console.error('Error loading settings:', error);
            }
            
            return this.terminalOptions;
        };
        
        service.saveSettings = function(settings) {
            this.terminalOptions = {
                ...this.terminalOptions,
                ...settings
            };
            
            localStorage.setItem('terma_terminal_settings', 
                JSON.stringify(this.terminalOptions));
            
            this.dispatchEvent('settingsChanged', { 
                settings: this.terminalOptions 
            });
        };
        
        service.resetSettings = function() {
            this.terminalOptions = {
                fontSize: 14,
                fontFamily: "'Courier New', monospace",
                theme: 'default',
                cursorStyle: 'block',
                cursorBlink: true,
                scrollback: 1000
            };
            
            localStorage.setItem('terma_terminal_settings', 
                JSON.stringify(this.terminalOptions));
            
            this.dispatchEvent('settingsChanged', { 
                settings: this.terminalOptions 
            });
        };
        
        return service;
    }
    
    /**
     * Load required dependencies
     */
    async function loadDependencies() {
        // First, check if xterm.js is already loaded
        if (typeof Terminal === 'undefined') {
            // Load xterm.js and addons
            await loadXtermDependencies();
        }
        
        // Setup terminal themes
        initializeTerminalThemes();
    }
    
    /**
     * Load xterm.js dependencies
     */
    async function loadXtermDependencies() {
        const xtermDependencies = [
            'https://cdn.jsdelivr.net/npm/xterm@5.1.0/lib/xterm.min.js',
            'https://cdn.jsdelivr.net/npm/xterm@5.1.0/css/xterm.css',
            'https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.7.0/lib/xterm-addon-fit.min.js',
            'https://cdn.jsdelivr.net/npm/xterm-addon-web-links@0.8.0/lib/xterm-addon-web-links.min.js',
            'https://cdn.jsdelivr.net/npm/xterm-addon-search@0.12.0/lib/xterm-addon-search.min.js'
        ];
        
        // Create array of promises for loading dependencies
        const loadPromises = xtermDependencies.map(url => {
            return new Promise((resolve, reject) => {
                // Check if already loaded
                if (url.endsWith('.js') && document.querySelector(`script[src="${url}"]`)) {
                    resolve();
                    return;
                }
                
                if (url.endsWith('.css') && document.querySelector(`link[href="${url}"]`)) {
                    resolve();
                    return;
                }
                
                // Create appropriate element based on file type
                const element = url.endsWith('.js') 
                    ? document.createElement('script') 
                    : document.createElement('link');
                
                // Set attributes based on type
                if (url.endsWith('.js')) {
                    element.src = url;
                    element.async = true;
                } else {
                    element.rel = 'stylesheet';
                    element.href = url;
                }
                
                // Handle load events
                element.onload = () => resolve();
                element.onerror = () => reject(new Error(`Failed to load ${url}`));
                
                // Add to shadow DOM or document head
                if (component.root) {
                    component.root.appendChild(element);
                } else {
                    document.head.appendChild(element);
                }
            });
        });
        
        // Wait for all dependencies to load
        await Promise.all(loadPromises);
        
        // Verify that Terminal and addons are available
        if (typeof Terminal === 'undefined') {
            throw new Error('xterm.js failed to load properly');
        }
        
        if (typeof FitAddon === 'undefined') {
            throw new Error('xterm.js FitAddon failed to load properly');
        }
        
        if (typeof WebLinksAddon === 'undefined') {
            throw new Error('xterm.js WebLinksAddon failed to load properly');
        }
        
        if (typeof SearchAddon === 'undefined') {
            throw new Error('xterm.js SearchAddon failed to load properly');
        }
    }
    
    /**
     * Setup UI elements with event handlers
     */
    function setupUIElements() {
        // Make sure the loading state starts hidden
        const loadingElement = component.$('#terma-loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        // Initialize the LLM panel collapsed state
        llmCollapsed = localStorage.getItem('terma_llm_panel_collapsed') === 'true';
        const llmPanel = component.$('.terma__llm-panel');
        if (llmPanel) {
            if (llmCollapsed) {
                llmPanel.classList.add('terma__llm-panel--collapsed');
            }
        }
        
        // Initialize terma container class for current mode
        const termaContainer = component.$('.terma');
        if (termaContainer) {
            currentTerminalMode = localStorage.getItem('terma_terminal_mode') || 'advanced';
            if (currentTerminalMode === 'simple') {
                termaContainer.classList.add('terma--simple-mode');
            }
        }
        
        // Initialize status indicators
        updateConnectionStatus('connecting');
        updateSessionInfo('No active session');
    }
    
    /**
     * Initialize terminal themes
     */
    function initializeTerminalThemes() {
        // Define terminal color themes
        terminalThemes = {
            default: {
                foreground: '#f0f0f0',
                background: '#1a1a1a',
                cursor: '#f0f0f0',
                selection: 'rgba(255, 255, 255, 0.3)',
                black: '#000000',
                red: '#ff5555',
                green: '#50fa7b',
                yellow: '#f1fa8c',
                blue: '#bd93f9',
                magenta: '#ff79c6',
                cyan: '#8be9fd',
                white: '#f8f8f2',
                brightBlack: '#6272a4',
                brightRed: '#ff6e6e',
                brightGreen: '#69ff94',
                brightYellow: '#ffffa5',
                brightBlue: '#d6acff',
                brightMagenta: '#ff92df',
                brightCyan: '#a4ffff',
                brightWhite: '#ffffff'
            },
            light: {
                foreground: '#333',
                background: '#f5f5f5',
                cursor: '#333',
                selection: 'rgba(0, 0, 0, 0.3)',
                black: '#000000',
                red: '#c91b00',
                green: '#00c200',
                yellow: '#c7c400',
                blue: '#0037da',
                magenta: '#c839c5',
                cyan: '#00c5c7',
                white: '#c7c7c7',
                brightBlack: '#767676',
                brightRed: '#e74856',
                brightGreen: '#16c60c',
                brightYellow: '#f9f1a5',
                brightBlue: '#3b78ff',
                brightMagenta: '#b4009e',
                brightCyan: '#61d6d6',
                brightWhite: '#f2f2f2'
            },
            solarized: {
                foreground: '#839496',
                background: '#002b36',
                cursor: '#839496',
                selection: 'rgba(255, 255, 255, 0.3)',
                black: '#073642',
                red: '#dc322f',
                green: '#859900',
                yellow: '#b58900',
                blue: '#268bd2',
                magenta: '#d33682',
                cyan: '#2aa198',
                white: '#eee8d5',
                brightBlack: '#002b36',
                brightRed: '#cb4b16',
                brightGreen: '#586e75',
                brightYellow: '#657b83',
                brightBlue: '#839496',
                brightMagenta: '#6c71c4',
                brightCyan: '#93a1a1',
                brightWhite: '#fdf6e3'
            },
            monokai: {
                foreground: '#f8f8f2',
                background: '#272822',
                cursor: '#f8f8f2',
                selection: 'rgba(255, 255, 255, 0.3)',
                black: '#272822',
                red: '#f92672',
                green: '#a6e22e',
                yellow: '#f4bf75',
                blue: '#66d9ef',
                magenta: '#ae81ff',
                cyan: '#a1efe4',
                white: '#f8f8f2',
                brightBlack: '#75715e',
                brightRed: '#f92672',
                brightGreen: '#a6e22e',
                brightYellow: '#f4bf75',
                brightBlue: '#66d9ef',
                brightMagenta: '#ae81ff',
                brightCyan: '#a1efe4',
                brightWhite: '#f9f8f5'
            }
        };
    }
    
    /**
     * Setup event handlers for UI elements
     */
    function setupEventHandlers() {
        // Terma service event handlers
        if (termaService) {
            // Terminal output
            termaService.addEventListener('terminalOutput', event => {
                // Send output to the active terminal
                if (currentTerminalMode === 'advanced' && advancedTerminal) {
                    advancedTerminal.write(event.data);
                } else if (currentTerminalMode === 'simple' && simpleTerminal) {
                    simpleTerminal.appendOutput(event.data);
                }
            });
            
            // Terminal error
            termaService.addEventListener('terminalError', event => {
                if (currentTerminalMode === 'advanced' && advancedTerminal) {
                    advancedTerminal.writeln(`\r\n\x1b[31mError: ${event.message}\x1b[0m`);
                } else if (currentTerminalMode === 'simple' && simpleTerminal) {
                    simpleTerminal.appendOutput(`\nError: ${event.message}\n`);
                }
                
                // Show notification
                notifications.show(component, 'Error', event.message, 'error');
            });
            
            // WebSocket connected
            termaService.addEventListener('websocketConnected', event => {
                updateConnectionStatus('connected');
                updateSessionInfo(`Session: ${event.sessionId.substring(0, 8)}...`);
            });
            
            // WebSocket closed
            termaService.addEventListener('websocketClosed', event => {
                updateConnectionStatus('disconnected');
                
                if (event.code !== 1000) {
                    // Abnormal closure
                    notifications.show(component, 'Disconnected', 
                        'Terminal connection closed unexpectedly.', 'warning');
                }
            });
            
            // WebSocket error
            termaService.addEventListener('websocketError', event => {
                updateConnectionStatus('disconnected');
                notifications.show(component, 'Connection Error', 
                    'Terminal connection error.', 'error');
            });
            
            // Sessions updated
            termaService.addEventListener('sessionsUpdated', event => {
                updateSessionSelector(event.sessions);
            });
            
            // Session created
            termaService.addEventListener('sessionCreated', event => {
                updateSessionInfo(`Session: ${event.sessionId.substring(0, 8)}...`);
            });
            
            // Session error
            termaService.addEventListener('sessionError', event => {
                notifications.show(component, 'Session Error', 
                    event.error.message || 'Unknown session error', 'error');
            });
            
            // LLM response
            termaService.addEventListener('llmResponse', event => {
                handleLlmResponse(event.content, event.loading, event.error);
            });
            
            // Reconnecting
            termaService.addEventListener('reconnecting', event => {
                updateConnectionStatus('connecting');
                updateSessionInfo(`Reconnecting (${event.attempt}/${event.maxAttempts})...`);
            });
            
            // Reconnection failed
            termaService.addEventListener('reconnectionFailed', event => {
                updateConnectionStatus('disconnected');
                updateSessionInfo('Reconnection failed');
                
                notifications.show(component, 'Reconnection Failed', 
                    'Failed to reconnect after multiple attempts. Please refresh the page.', 
                    'error', 0);
            });
            
            // Session expired
            termaService.addEventListener('sessionExpired', event => {
                updateConnectionStatus('disconnected');
                updateSessionInfo('Session expired');
                
                notifications.show(component, 'Session Expired', 
                    'The terminal session has expired. Please create a new session.', 
                    'warning');
                
                // Refresh session list
                termaService.fetchSessions();
            });
            
            // Settings changed
            termaService.addEventListener('settingsChanged', event => {
                applyTerminalSettings(event.settings);
            });
        }
        
        // UI Button Event Handlers
        
        // Toggle terminal mode button
        const toggleModeBtn = component.$('#terma-toggle-mode-btn');
        if (toggleModeBtn) {
            lifecycle.registerEventHandler(component, toggleModeBtn, 'click', toggleTerminalMode);
        }
        
        // Settings button
        const settingsBtn = component.$('#terma-settings-btn');
        if (settingsBtn) {
            lifecycle.registerEventHandler(component, settingsBtn, 'click', toggleSettingsDialog);
        }
        
        // Settings dialog close button
        const dialogCloseBtn = component.$('.terma__dialog-close');
        if (dialogCloseBtn) {
            lifecycle.registerEventHandler(component, dialogCloseBtn, 'click', hideSettingsDialog);
        }
        
        // Settings save button
        const settingsSaveBtn = component.$('#terma-settings-save');
        if (settingsSaveBtn) {
            lifecycle.registerEventHandler(component, settingsSaveBtn, 'click', saveTerminalSettings);
        }
        
        // Settings reset button
        const settingsResetBtn = component.$('#terma-settings-reset');
        if (settingsResetBtn) {
            lifecycle.registerEventHandler(component, settingsResetBtn, 'click', resetTerminalSettings);
        }
        
        // LLM panel toggle button
        const llmToggleBtn = component.$('#terma-llm-toggle');
        if (llmToggleBtn) {
            lifecycle.registerEventHandler(component, llmToggleBtn, 'click', toggleLlmPanel);
        }
        
        // Detach button
        const detachBtn = component.$('#terma-detach-btn');
        if (detachBtn) {
            lifecycle.registerEventHandler(component, detachBtn, 'click', detachTerminal);
        }
        
        // Session selector
        const sessionSelector = component.$('#terma-session-selector');
        if (sessionSelector) {
            lifecycle.registerEventHandler(component, sessionSelector, 'change', handleSessionChange);
        }
        
        // Terminal type selector
        const terminalTypeSelector = component.$('#terma-terminal-type');
        if (terminalTypeSelector) {
            lifecycle.registerEventHandler(component, terminalTypeSelector, 'change', handleTerminalTypeChange);
        }
        
        // Font size range input
        const fontSizeInput = component.$('#terma-font-size');
        const fontSizeValue = component.$('#terma-font-size-value');
        if (fontSizeInput && fontSizeValue) {
            lifecycle.registerEventHandler(component, fontSizeInput, 'input', () => {
                const value = fontSizeInput.value;
                fontSizeValue.textContent = `${value}px`;
                
                // Update terminal font size in real-time
                if (advancedTerminal) {
                    advancedTerminal.options.fontSize = parseInt(value, 10);
                    fitTerminalToContainer();
                }
            });
        }
        
        // Scrollback checkbox
        const scrollbackCheckbox = component.$('#terma-scrollback');
        const scrollbackContainer = component.$('#terma-scrollback-container');
        if (scrollbackCheckbox && scrollbackContainer) {
            lifecycle.registerEventHandler(component, scrollbackCheckbox, 'change', () => {
                scrollbackContainer.style.display = scrollbackCheckbox.checked ? 'block' : 'none';
            });
        }
        
        // Window resize event
        lifecycle.registerEventHandler(component, window, 'resize', handleWindowResize);
    }
    
    /**
     * Handle LLM response from service
     */
    function handleLlmResponse(content, loading, error) {
        const llmOutput = component.$('#terma-llm-output');
        if (!llmOutput) return;
        
        // Reset classes
        llmOutput.classList.remove('terma__llm-output--loading');
        llmOutput.classList.remove('terma__llm-output--error');
        
        // Add appropriate class based on state
        if (loading) llmOutput.classList.add('terma__llm-output--loading');
        if (error) llmOutput.classList.add('terma__llm-output--error');
        
        // Format the content using marked.js if available
        if (!loading && typeof marked !== 'undefined') {
            try {
                llmOutput.innerHTML = marked.parse(content);
                
                // Apply syntax highlighting to code blocks if hljs is available
                if (typeof hljs !== 'undefined') {
                    const codeBlocks = llmOutput.querySelectorAll('pre code');
                    codeBlocks.forEach(block => {
                        hljs.highlightElement(block);
                    });
                }
            } catch (e) {
                console.error('Error parsing markdown:', e);
                llmOutput.textContent = content;
            }
        } else {
            // For loading messages or if marked.js is not available, use simple text
            llmOutput.textContent = content;
        }
        
        // Make sure the LLM panel is expanded
        if (loading === false && llmCollapsed) {
            toggleLlmPanel();
        }
    }
    
    /**
     * Handle session selector change
     */
    async function handleSessionChange() {
        const sessionSelector = component.$('#terma-session-selector');
        if (!sessionSelector) return;
        
        const selectedValue = sessionSelector.value;
        
        try {
            // Show loading indicator
            showLoadingIndicator();
            
            if (selectedValue === 'new') {
                // Create a new session
                if (currentTerminalMode === 'advanced' && advancedTerminal) {
                    advancedTerminal.writeln('\r\n\x1b[33mCreating new terminal session...\x1b[0m');
                }
                
                // Get the selected terminal type
                const terminalTypeSelector = component.$('#terma-terminal-type');
                const shellCommand = terminalTypeSelector ? 
                    getShellCommandFromType(terminalTypeSelector.value) : null;
                
                // Create a new session
                await termaService.createSession(shellCommand);
                
                // Connect to the new session
                if (termaService.sessionId) {
                    await termaService.connectToSession(termaService.sessionId);
                }
            } else {
                // Connect to existing session
                if (currentTerminalMode === 'advanced' && advancedTerminal) {
                    advancedTerminal.writeln('\r\n\x1b[33mConnecting to session...\x1b[0m');
                }
                
                await termaService.connectToSession(selectedValue);
                
                // Update terminal type selector to match session
                updateTerminalTypeSelector();
            }
            
            // Hide loading indicator
            hideLoadingIndicator();
        } catch (error) {
            console.error('Error handling session change:', error);
            
            // Show notification
            notifications.show(component, 'Error', 
                `Failed to change session: ${error.message}`, 'error');
            
            // Hide loading indicator
            hideLoadingIndicator();
            
            // Reset selector to original value
            await termaService.fetchSessions();
            if (termaService.sessionId) {
                sessionSelector.value = termaService.sessionId;
            } else {
                sessionSelector.value = 'new';
            }
        }
    }
    
    /**
     * Handle terminal type selector change
     */
    async function handleTerminalTypeChange() {
        const terminalTypeSelector = component.$('#terma-terminal-type');
        if (!terminalTypeSelector) return;
        
        const selectedType = terminalTypeSelector.value;
        const shellCommand = getShellCommandFromType(selectedType);
        
        try {
            // Show loading indicator
            showLoadingIndicator();
            
            if (currentTerminalMode === 'advanced' && advancedTerminal) {
                advancedTerminal.writeln(`\r\n\x1b[33mChanging terminal type to ${selectedType}...\x1b[0m`);
            }
            
            // Create a new session with the selected shell
            await termaService.createSession(shellCommand);
            
            // Connect to the new session
            if (termaService.sessionId) {
                await termaService.connectToSession(termaService.sessionId);
            }
            
            // Hide loading indicator
            hideLoadingIndicator();
            
            if (currentTerminalMode === 'advanced' && advancedTerminal) {
                advancedTerminal.writeln('\x1b[32mTerminal type changed successfully.\x1b[0m');
            }
        } catch (error) {
            console.error('Error changing terminal type:', error);
            
            // Show notification
            notifications.show(component, 'Error', 
                `Failed to change terminal type: ${error.message}`, 'error');
            
            // Hide loading indicator
            hideLoadingIndicator();
            
            // Reset the selector to the previous value
            updateTerminalTypeSelector();
        }
    }
    
    /**
     * Toggle terminal settings dialog
     */
    function toggleSettingsDialog() {
        const dialog = component.$('#terma-settings-dialog');
        if (!dialog) return;
        
        const isVisible = dialog.classList.contains('terma__dialog--visible');
        
        if (isVisible) {
            hideSettingsDialog();
        } else {
            showSettingsDialog();
        }
    }
    
    /**
     * Show terminal settings dialog
     */
    function showSettingsDialog() {
        const dialog = component.$('#terma-settings-dialog');
        if (!dialog) return;
        
        // Load current settings into form
        loadSettingsIntoForm();
        
        // Show dialog
        dialog.classList.add('terma__dialog--visible');
    }
    
    /**
     * Hide terminal settings dialog
     */
    function hideSettingsDialog() {
        const dialog = component.$('#terma-settings-dialog');
        if (!dialog) return;
        
        dialog.classList.remove('terma__dialog--visible');
    }
    
    /**
     * Load settings into settings form
     */
    function loadSettingsIntoForm() {
        // Get current settings
        const settings = termaService.loadSettings();
        
        // Update form elements
        const fontSizeInput = component.$('#terma-font-size');
        const fontSizeValue = component.$('#terma-font-size-value');
        const fontFamilySelect = component.$('#terma-font-family');
        const themeSelect = component.$('#terma-theme');
        const cursorStyleSelect = component.$('#terma-cursor-style');
        const cursorBlinkCheckbox = component.$('#terma-cursor-blink');
        const scrollbackCheckbox = component.$('#terma-scrollback');
        const scrollbackLinesInput = component.$('#terma-scrollback-lines');
        const scrollbackContainer = component.$('#terma-scrollback-container');
        
        // Update values
        if (fontSizeInput) fontSizeInput.value = settings.fontSize;
        if (fontSizeValue) fontSizeValue.textContent = `${settings.fontSize}px`;
        if (fontFamilySelect) fontFamilySelect.value = settings.fontFamily;
        if (themeSelect) themeSelect.value = settings.theme;
        if (cursorStyleSelect) cursorStyleSelect.value = settings.cursorStyle;
        if (cursorBlinkCheckbox) cursorBlinkCheckbox.checked = settings.cursorBlink;
        if (scrollbackCheckbox) scrollbackCheckbox.checked = settings.scrollback > 0;
        if (scrollbackLinesInput) scrollbackLinesInput.value = settings.scrollback > 0 ? settings.scrollback : 1000;
        if (scrollbackContainer) scrollbackContainer.style.display = settings.scrollback > 0 ? 'block' : 'none';
    }
    
    /**
     * Save terminal settings from form
     */
    function saveTerminalSettings() {
        // Get form values
        const fontSizeInput = component.$('#terma-font-size');
        const fontFamilySelect = component.$('#terma-font-family');
        const themeSelect = component.$('#terma-theme');
        const cursorStyleSelect = component.$('#terma-cursor-style');
        const cursorBlinkCheckbox = component.$('#terma-cursor-blink');
        const scrollbackCheckbox = component.$('#terma-scrollback');
        const scrollbackLinesInput = component.$('#terma-scrollback-lines');
        
        // Gather settings
        const settings = {
            fontSize: fontSizeInput ? parseInt(fontSizeInput.value, 10) : 14,
            fontFamily: fontFamilySelect ? fontFamilySelect.value : "'Courier New', monospace",
            theme: themeSelect ? themeSelect.value : 'default',
            cursorStyle: cursorStyleSelect ? cursorStyleSelect.value : 'block',
            cursorBlink: cursorBlinkCheckbox ? cursorBlinkCheckbox.checked : true,
            scrollback: scrollbackCheckbox && scrollbackCheckbox.checked && scrollbackLinesInput
                ? parseInt(scrollbackLinesInput.value, 10)
                : 0
        };
        
        // Save settings
        termaService.saveSettings(settings);
        
        // Apply settings to terminal
        applyTerminalSettings(settings);
        
        // Hide settings dialog
        hideSettingsDialog();
        
        // Show notification
        notifications.show(component, 'Settings Saved', 
            'Terminal settings have been saved.', 'success');
    }
    
    /**
     * Reset terminal settings to defaults
     */
    function resetTerminalSettings() {
        // Reset settings
        termaService.resetSettings();
        
        // Apply to form elements
        loadSettingsIntoForm();
        
        // Apply to terminal
        applyTerminalSettings(termaService.terminalOptions);
        
        // Show notification
        notifications.show(component, 'Settings Reset', 
            'Terminal settings have been reset to defaults.', 'info');
    }
    
    /**
     * Apply terminal settings to the active terminal
     */
    function applyTerminalSettings(settings) {
        if (currentTerminalMode === 'advanced' && advancedTerminal) {
            // Apply settings to xterm.js terminal
            advancedTerminal.options.fontSize = settings.fontSize;
            advancedTerminal.options.fontFamily = settings.fontFamily;
            advancedTerminal.options.theme = terminalThemes[settings.theme];
            advancedTerminal.options.cursorStyle = settings.cursorStyle;
            advancedTerminal.options.cursorBlink = settings.cursorBlink;
            advancedTerminal.options.scrollback = settings.scrollback;
            
            // Force terminal to update
            fitTerminalToContainer();
        }
    }
    
    /**
     * Toggle the LLM assistance panel
     */
    function toggleLlmPanel() {
        const llmPanel = component.$('.terma__llm-panel');
        const llmToggleBtn = component.$('#terma-llm-toggle');
        
        if (!llmPanel) return;
        
        // Toggle state
        llmCollapsed = !llmCollapsed;
        
        // Update DOM
        if (llmCollapsed) {
            llmPanel.classList.add('terma__llm-panel--collapsed');
            if (llmToggleBtn) {
                llmToggleBtn.querySelector('svg').style.transform = 'rotate(180deg)';
            }
        } else {
            llmPanel.classList.remove('terma__llm-panel--collapsed');
            if (llmToggleBtn) {
                llmToggleBtn.querySelector('svg').style.transform = 'rotate(0deg)';
            }
        }
        
        // Save preference
        localStorage.setItem('terma_llm_panel_collapsed', llmCollapsed.toString());
        
        // Resize terminal
        if (currentTerminalMode === 'advanced' && advancedTerminal) {
            setTimeout(() => fitTerminalToContainer(), 300);
        }
    }
    
    /**
     * Toggle between terminal modes
     */
    function toggleTerminalMode() {
        const termaContainer = component.$('.terma');
        if (!termaContainer) return;
        
        // Toggle mode
        currentTerminalMode = currentTerminalMode === 'advanced' ? 'simple' : 'advanced';
        
        // Update container class
        if (currentTerminalMode === 'simple') {
            termaContainer.classList.add('terma--simple-mode');
            
            // Initialize simple terminal if not already
            if (!simpleTerminal) {
                initSimpleTerminal();
            }
        } else {
            termaContainer.classList.remove('terma--simple-mode');
            
            // Fit the advanced terminal to container
            if (advancedTerminal) {
                setTimeout(() => fitTerminalToContainer(), 100);
            }
        }
        
        // Save preference
        localStorage.setItem('terma_terminal_mode', currentTerminalMode);
        
        // Show notification
        const modeName = currentTerminalMode === 'advanced' ? 'Advanced' : 'Simple';
        notifications.show(component, 'Terminal Mode', 
            `Switched to ${modeName} terminal mode.`, 'info');
    }
    
    /**
     * Detach terminal to a new window
     */
    function detachTerminal() {
        // Only work with advanced terminal
        if (currentTerminalMode !== 'advanced' || !termaService.sessionId) {
            notifications.show(component, 'Detach Error', 
                'Detach is only available in advanced terminal mode with an active session.', 
                'warning');
            return;
        }
        
        try {
            // Get hostname from the current URL
            const hostname = window.location.hostname || 'localhost';
            const protocol = window.location.protocol || 'http:';
            
            // Create launch URL
            const sessionId = termaService.sessionId;
            const launchUrl = `${protocol}//${hostname}:8765/terminal/launch?session_id=${sessionId}`;
            
            // Calculate window size and position
            const width = Math.min(1200, window.screen.availWidth * 0.8);
            const height = Math.min(800, window.screen.availHeight * 0.8);
            const left = (window.screen.availWidth - width) / 2;
            const top = (window.screen.availHeight - height) / 2;
            
            // Open in a new window
            window.open(
                launchUrl,
                `terma_terminal_${sessionId}`,
                `width=${width},height=${height},left=${left},top=${top},menubar=no,toolbar=no,location=no,status=no`
            );
            
            // Show notification
            notifications.show(component, 'Terminal Detached', 
                'Terminal has been opened in a new window.', 'success');
        } catch (error) {
            console.error('Error detaching terminal:', error);
            notifications.show(component, 'Detach Error', 
                `Failed to detach terminal: ${error.message}`, 'error');
        }
    }
    
    /**
     * Handle window resize event
     */
    function handleWindowResize() {
        // Debounce the resize to improve performance
        if (this.resizeTimer) {
            clearTimeout(this.resizeTimer);
        }
        
        this.resizeTimer = setTimeout(() => {
            if (currentTerminalMode === 'advanced' && advancedTerminal) {
                fitTerminalToContainer();
            }
        }, 100);
    }
    
    /**
     * Initialize the terminal based on preferred mode
     */
    async function initializeTerminal() {
        // Get the preferred terminal mode from localStorage
        currentTerminalMode = localStorage.getItem('terma_terminal_mode') || 'advanced';
        
        // Update the UI to reflect the current mode
        const termaContainer = component.$('.terma');
        if (termaContainer) {
            if (currentTerminalMode === 'simple') {
                termaContainer.classList.add('terma--simple-mode');
            } else {
                termaContainer.classList.remove('terma--simple-mode');
            }
        }
        
        // Initialize appropriate terminal
        if (currentTerminalMode === 'advanced') {
            // Initialize advanced terminal
            await initAdvancedTerminal();
        } else {
            // Initialize simple terminal
            initSimpleTerminal();
        }
        
        // Load existing sessions
        if (termaService) {
            await termaService.fetchSessions();
            
            // Create a new session if needed
            if (termaService.sessionList.length === 0) {
                await termaService.createSession();
            } else {
                // Connect to the first available session
                const firstSession = termaService.sessionList[0];
                await termaService.connectToSession(firstSession.id);
            }
        }
    }
    
    /**
     * Initialize the advanced terminal
     */
    async function initAdvancedTerminal() {
        // Get the element where we'll render the terminal
        const terminalElement = component.$('#terma-terminal');
        if (!terminalElement) {
            throw new Error('Terminal container element not found');
        }
        
        // Create terminal instance with settings from service
        const settings = termaService.loadSettings();
        
        // Initialize terminal
        advancedTerminal = new Terminal({
            fontSize: settings.fontSize,
            fontFamily: settings.fontFamily,
            theme: terminalThemes[settings.theme],
            cursorStyle: settings.cursorStyle,
            cursorBlink: settings.cursorBlink,
            scrollback: settings.scrollback,
            allowTransparency: true,
            convertEol: true,
            disableStdin: false,
            drawBoldTextInBrightColors: true,
            rightClickSelectsWord: true
        });
        
        // Add addons
        fitAddon = new FitAddon.FitAddon();
        searchAddon = new SearchAddon.SearchAddon();
        webLinksAddon = new WebLinksAddon.WebLinksAddon();
        
        advancedTerminal.loadAddon(fitAddon);
        advancedTerminal.loadAddon(searchAddon);
        advancedTerminal.loadAddon(webLinksAddon);
        
        // Open terminal
        advancedTerminal.open(terminalElement);
        
        // Handle user input
        advancedTerminal.onData(data => {
            if (termaService) {
                // Check for special input patterns
                if (data === '?' && isAtCommandPrompt()) {
                    // Show LLM help for the current command line
                    const currentLine = getCurrentLine();
                    termaService.requestLlmAssistance(currentLine, false);
                    return;
                }
                
                // Check for trailing ? for output analysis
                if (data === '?' && !isAtCommandPrompt() && getCurrentLine().trim().length > 0) {
                    // Send enter to execute the command
                    termaService.sendInput('\r');
                    
                    // Wait for output and then analyze
                    setTimeout(() => {
                        termaService.requestLlmAssistance('', true);
                    }, 500);
                    
                    return;
                }
                
                // Regular input - send to service
                termaService.sendInput(data);
            }
        });
        
        // Handle key commands
        advancedTerminal.attachCustomKeyEventHandler(event => {
            // Ctrl+Shift+F: Search
            if (event.ctrlKey && event.shiftKey && event.key === 'F' && event.type === 'keydown') {
                searchAddon.activate();
                return false;
            }
            
            return true;
        });
        
        // Initial fit
        fitTerminalToContainer();
        
        // Display welcome message
        advancedTerminal.writeln('\x1b[1;34mTerma Terminal (Shadow DOM Edition)\x1b[0m');
        advancedTerminal.writeln('\x1b[90mType commands or use ? for assistance\x1b[0m');
        advancedTerminal.writeln('');
    }
    
    /**
     * Initialize the simple terminal
     */
    function initSimpleTerminal() {
        // Get the element where we'll render the simple terminal
        const terminalElement = component.$('#simple-terminal');
        if (!terminalElement) {
            console.error('Simple terminal container element not found');
            return;
        }
        
        // Create a basic terminal implementation
        simpleTerminal = {
            element: terminalElement,
            history: [],
            historyIndex: -1,
            cursorPos: 0,
            inputLine: '',
            
            init: function() {
                this.element.innerHTML = '<div class="terminal-output"></div>' +
                    '<div class="terminal-input-line">' +
                    '<span class="terminal-prompt">$ </span>' +
                    '<span class="terminal-input"></span>' +
                    '<span class="terminal-cursor">█</span>' +
                    '</div>';
                
                this.outputElement = this.element.querySelector('.terminal-output');
                this.inputElement = this.element.querySelector('.terminal-input');
                this.cursorElement = this.element.querySelector('.terminal-cursor');
                this.promptElement = this.element.querySelector('.terminal-prompt');
                
                // Handle keyboard input
                this.element.tabIndex = 0;
                this.element.addEventListener('keydown', this.handleKeyDown.bind(this));
                this.element.addEventListener('click', () => this.element.focus());
                
                // Initialize cursor blink
                this.startCursorBlink();
                
                this.element.focus();
            },
            
            startCursorBlink: function() {
                if (this.cursorBlinkInterval) {
                    clearInterval(this.cursorBlinkInterval);
                }
                
                this.cursorBlinkInterval = setInterval(() => {
                    if (this.cursorElement) {
                        this.cursorElement.style.visibility = 
                            this.cursorElement.style.visibility === 'hidden' ? 'visible' : 'hidden';
                    }
                }, 500);
            },
            
            handleKeyDown: function(event) {
                // Stop default behavior for most keys
                if (event.key !== 'F5' && !event.ctrlKey && !event.metaKey) {
                    event.preventDefault();
                }
                
                switch (event.key) {
                    case 'Enter':
                        this.executeCommand();
                        break;
                    case 'Backspace':
                        this.handleBackspace();
                        break;
                    case 'Delete':
                        this.handleDelete();
                        break;
                    case 'ArrowLeft':
                        this.moveCursorLeft();
                        break;
                    case 'ArrowRight':
                        this.moveCursorRight();
                        break;
                    case 'ArrowUp':
                        this.navigateHistory(-1);
                        break;
                    case 'ArrowDown':
                        this.navigateHistory(1);
                        break;
                    case 'Home':
                        this.cursorPos = 0;
                        this.updateInputDisplay();
                        break;
                    case 'End':
                        this.cursorPos = this.inputLine.length;
                        this.updateInputDisplay();
                        break;
                    case 'Tab':
                        // Tab completion could be implemented here
                        break;
                    case 'c':
                        if (event.ctrlKey) {
                            // Ctrl+C to cancel current command
                            this.inputLine = '';
                            this.cursorPos = 0;
                            this.updateInputDisplay();
                            this.appendOutput('\n^C\n$ ');
                        } else {
                            this.insertAtCursor(event.key);
                        }
                        break;
                    default:
                        if (event.key.length === 1) {
                            this.insertAtCursor(event.key);
                        }
                }
            },
            
            executeCommand: function() {
                if (this.inputLine.trim() === '') {
                    this.appendOutput('\n$ ');
                    return;
                }
                
                // Add to history
                this.history.push(this.inputLine);
                this.historyIndex = this.history.length;
                
                // Show the command in output
                this.appendOutput(`\n${this.inputLine}\n`);
                
                // Send to service
                if (termaService) {
                    termaService.sendInput(this.inputLine + '\n');
                }
                
                // Clear input line
                this.inputLine = '';
                this.cursorPos = 0;
                this.updateInputDisplay();
            },
            
            handleBackspace: function() {
                if (this.cursorPos > 0) {
                    this.inputLine = this.inputLine.substring(0, this.cursorPos - 1) +
                        this.inputLine.substring(this.cursorPos);
                    this.cursorPos--;
                    this.updateInputDisplay();
                }
            },
            
            handleDelete: function() {
                if (this.cursorPos < this.inputLine.length) {
                    this.inputLine = this.inputLine.substring(0, this.cursorPos) +
                        this.inputLine.substring(this.cursorPos + 1);
                    this.updateInputDisplay();
                }
            },
            
            moveCursorLeft: function() {
                if (this.cursorPos > 0) {
                    this.cursorPos--;
                    this.updateInputDisplay();
                }
            },
            
            moveCursorRight: function() {
                if (this.cursorPos < this.inputLine.length) {
                    this.cursorPos++;
                    this.updateInputDisplay();
                }
            },
            
            navigateHistory: function(direction) {
                const newIndex = this.historyIndex + direction;
                if (newIndex >= 0 && newIndex <= this.history.length) {
                    this.historyIndex = newIndex;
                    
                    if (this.historyIndex === this.history.length) {
                        this.inputLine = '';
                    } else {
                        this.inputLine = this.history[this.historyIndex];
                    }
                    
                    this.cursorPos = this.inputLine.length;
                    this.updateInputDisplay();
                }
            },
            
            insertAtCursor: function(char) {
                this.inputLine = this.inputLine.substring(0, this.cursorPos) +
                    char +
                    this.inputLine.substring(this.cursorPos);
                this.cursorPos++;
                this.updateInputDisplay();
            },
            
            updateInputDisplay: function() {
                // Show the input with the cursor at the right position
                const beforeCursor = this.inputLine.substring(0, this.cursorPos);
                const afterCursor = this.inputLine.substring(this.cursorPos);
                
                this.inputElement.textContent = beforeCursor;
                this.cursorElement.textContent = afterCursor.charAt(0) || ' ';
                
                // Create a span for the rest of the text after cursor
                const afterCursorSpan = document.createElement('span');
                afterCursorSpan.textContent = afterCursor.substring(1);
                
                // Clear and rebuild the input line
                const inputLine = this.element.querySelector('.terminal-input-line');
                inputLine.innerHTML = '';
                
                inputLine.appendChild(this.promptElement);
                inputLine.appendChild(this.inputElement);
                inputLine.appendChild(this.cursorElement);
                inputLine.appendChild(afterCursorSpan);
                
                // Reset cursor blink
                this.cursorElement.style.visibility = 'visible';
                clearInterval(this.cursorBlinkInterval);
                this.startCursorBlink();
            },
            
            appendOutput: function(text) {
                // Process ANSI escape sequences for colors
                let processedText = text
                    .replace(/\r/g, '')
                    .replace(/\x1b\[([0-9;]*)m/g, (match, p1) => {
                        const codes = p1.split(';').map(Number);
                        let result = '';
                        
                        for (const code of codes) {
                            switch (code) {
                                case 0: result += '</span><span>'; break; // Reset
                                case 1: result += '<span style="font-weight: bold;">'; break;
                                case 30: result += '<span style="color: black;">'; break;
                                case 31: result += '<span style="color: red;">'; break;
                                case 32: result += '<span style="color: green;">'; break;
                                case 33: result += '<span style="color: yellow;">'; break;
                                case 34: result += '<span style="color: blue;">'; break;
                                case 35: result += '<span style="color: magenta;">'; break;
                                case 36: result += '<span style="color: cyan;">'; break;
                                case 37: result += '<span style="color: white;">'; break;
                                case 90: result += '<span style="color: grey;">'; break;
                                default: break;
                            }
                        }
                        
                        return result;
                    });
                
                // Wrap the text in a span for proper styling
                processedText = `<span>${processedText}</span>`;
                
                // Add to output
                this.outputElement.innerHTML += processedText;
                
                // Update prompt if needed
                if (text.includes('$') && text.includes('\n')) {
                    this.promptElement.textContent = '$ ';
                }
                
                // Scroll to bottom
                this.element.scrollTop = this.element.scrollHeight;
                
                // Focus the terminal
                this.element.focus();
            },
            
            cleanup: function() {
                if (this.cursorBlinkInterval) {
                    clearInterval(this.cursorBlinkInterval);
                }
            }
        };
        
        // Initialize the simple terminal
        simpleTerminal.init();
        
        // Display welcome message
        simpleTerminal.appendOutput('Terma Terminal (Simple Mode)\n');
        simpleTerminal.appendOutput('Type commands or use ? for assistance\n\n$ ');
    }
    
    /**
     * Fit the terminal to its container
     */
    function fitTerminalToContainer() {
        if (currentTerminalMode === 'advanced' && advancedTerminal && fitAddon) {
            try {
                // Fit the terminal to its container
                fitAddon.fit();
                
                // Send terminal size to server
                if (termaService && termaService.sessionId) {
                    termaService.resizeTerminal(
                        advancedTerminal.rows,
                        advancedTerminal.cols
                    );
                }
            } catch (error) {
                console.error('Error fitting terminal:', error);
            }
        }
    }
    
    /**
     * Update the session selector dropdown
     */
    function updateSessionSelector(sessions) {
        const sessionSelector = component.$('#terma-session-selector');
        if (!sessionSelector) return;
        
        // Save the selected value
        const selectedValue = sessionSelector.value;
        
        // Clear existing options except for "New Session"
        while (sessionSelector.options.length > 1) {
            sessionSelector.remove(1);
        }
        
        // Add sessions
        sessions.forEach(session => {
            const option = document.createElement('option');
            option.value = session.id;
            option.text = `Session ${session.id.slice(0, 8)}...`;
            
            // Select if this is the current session
            if (termaService && termaService.sessionId === session.id) {
                option.selected = true;
            }
            
            sessionSelector.add(option);
        });
        
        // Restore selected value if possible
        if (selectedValue !== 'new') {
            // Check if the selected value still exists
            const exists = sessions.some(s => s.id === selectedValue);
            if (exists) {
                sessionSelector.value = selectedValue;
            }
        }
    }
    
    /**
     * Update the terminal type selector based on the current session
     */
    function updateTerminalTypeSelector() {
        const terminalTypeSelector = component.$('#terma-terminal-type');
        if (!terminalTypeSelector) return;
        
        // Get the current session
        if (termaService && termaService.sessionList && termaService.sessionId) {
            const session = termaService.sessionList.find(s => s.id === termaService.sessionId);
            if (session) {
                // Determine terminal type from shell command
                const shellCommand = session.shell_command || '';
                
                if (shellCommand.includes('bash')) {
                    terminalTypeSelector.value = 'bash';
                } else if (shellCommand.includes('python')) {
                    terminalTypeSelector.value = 'python';
                } else if (shellCommand.includes('node')) {
                    terminalTypeSelector.value = 'node';
                } else {
                    terminalTypeSelector.value = 'default';
                }
            }
        }
    }
    
    /**
     * Convert terminal type to shell command
     */
    function getShellCommandFromType(terminalType) {
        switch (terminalType) {
            case 'bash': return '/bin/bash';
            case 'python': return 'python';
            case 'node': return 'node';
            default: return null; // Use default shell
        }
    }
    
    /**
     * Update connection status indicator
     */
    function updateConnectionStatus(status) {
        const statusElement = component.$('#terma-connection-status');
        const statusTextElement = statusElement ? 
            statusElement.querySelector('.terma__status-text') : null;
            
        if (!statusElement || !statusTextElement) return;
        
        // Remove existing status classes
        statusElement.classList.remove('terma__status-item--connected');
        statusElement.classList.remove('terma__status-item--disconnected');
        statusElement.classList.remove('terma__status-item--connecting');
        
        // Add appropriate class and text
        switch (status) {
            case 'connected':
                statusElement.classList.add('terma__status-item--connected');
                statusTextElement.textContent = 'Connected';
                break;
            case 'disconnected':
                statusElement.classList.add('terma__status-item--disconnected');
                statusTextElement.textContent = 'Disconnected';
                break;
            case 'connecting':
                statusElement.classList.add('terma__status-item--connecting');
                statusTextElement.textContent = 'Connecting...';
                break;
        }
    }
    
    /**
     * Update session info in status bar
     */
    function updateSessionInfo(info) {
        const infoElement = component.$('#terma-session-info');
        const textElement = infoElement ? 
            infoElement.querySelector('.terma__status-text') : null;
            
        if (textElement) {
            textElement.textContent = info;
        }
    }
    
    /**
     * Show loading indicator
     */
    function showLoadingIndicator() {
        const loadingElement = component.$('#terma-loading');
        if (loadingElement) {
            loadingElement.style.display = 'flex';
        }
    }
    
    /**
     * Hide loading indicator
     */
    function hideLoadingIndicator() {
        const loadingElement = component.$('#terma-loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }
    
    /**
     * Show initialization error in terminal area
     */
    function showInitializationError(error) {
        const terminalElement = component.$('#terma-terminal');
        if (terminalElement) {
            terminalElement.innerHTML = `
                <div style="padding: 20px; color: #ff6b6b; background: #222; height: 100%; overflow: auto; font-family: monospace;">
                    <h3 style="color: #ff6b6b;">Terminal Initialization Error</h3>
                    <p>${error.message}</p>
                    <pre style="background: #333; padding: 10px; border-radius: 4px; overflow: auto;">${error.stack || 'No stack trace available'}</pre>
                    <hr style="border-color: #444;">
                    <h4>Troubleshooting:</h4>
                    <ul style="list-style-type: disc; margin-left: 20px;">
                        <li>Check that the Terma API server is running (port 8765)</li>
                        <li>Check that WebSocket server is available (port 8767)</li>
                        <li>Check your browser console for detailed error messages</li>
                        <li>Try reloading the page</li>
                    </ul>
                </div>
            `;
        }
    }
    
    /**
     * Get the current line from the terminal
     */
    function getCurrentLine() {
        if (currentTerminalMode === 'advanced' && advancedTerminal) {
            // Get the buffer content of the current line
            const buffer = advancedTerminal._core.buffer;
            const lineY = buffer.active.baseY + buffer.active.cursorY;
            const line = buffer.active.lines.get(lineY);
            
            let text = '';
            for (let i = 0; i < line.length; i++) {
                text += line.getString(i);
            }
            
            return text.trim();
        } else if (currentTerminalMode === 'simple' && simpleTerminal) {
            return simpleTerminal.inputLine;
        }
        
        return '';
    }
    
    /**
     * Check if the terminal cursor is at a command prompt
     */
    function isAtCommandPrompt() {
        if (currentTerminalMode === 'advanced' && advancedTerminal) {
            const currentLine = getCurrentLine();
            return currentLine.endsWith('$') || currentLine.endsWith('>');
        }
        
        return false;
    }
    
    /**
     * Register cleanup handlers for component
     */
    function registerCleanupHandlers() {
        // Create a cleanup function for all resources
        component.registerCleanup(() => {
            console.log('Cleaning up Terma component resources');
            
            // Close WebSocket connection
            if (termaService) {
                termaService.closeWebSocketConnection();
            }
            
            // Clean up simpleTerminal if it exists
            if (simpleTerminal && simpleTerminal.cleanup) {
                simpleTerminal.cleanup();
            }
            
            // Remove event handlers
            if (this.resizeTimer) {
                clearTimeout(this.resizeTimer);
            }
            
            // Clean up advanced terminal
            if (advancedTerminal) {
                advancedTerminal.dispose();
                advancedTerminal = null;
            }
            
            // Clean up addons
            fitAddon = null;
            searchAddon = null;
            webLinksAddon = null;
        });
    }
    
    // Initialize the component
    initComponent();
    
})(component);