/**
 * Terma Terminal Component
 * Implementation of xterm.js-based terminal for Tekton
 */

/**
 * Enhanced debugging utility for the Terma Terminal Component
 * 
 * Provides multiple logging channels with visual indicators:
 * - Console logging with appropriate level methods
 * - Optional DOM-based logging if debug container is present
 * - Contextual information including component, timestamp, and log level
 * - Support for object inspection and pretty printing
 * 
 * @param {string|object} message - Message to log or object to inspect
 * @param {string} level - Log level (error, warn, success, info, debug, trace)
 * @param {object} options - Additional options for logging
 */
function debugLog(message, level = 'info', options = {}) {
    // Default options
    const defaults = {
        component: 'Terma',           // Component name for prefix
        toConsole: true,              // Log to browser console
        toDom: true,                  // Log to DOM if container exists
        inspect: false,               // Pretty print objects
        stackTrace: false,            // Include stack trace (error only)
        domLimit: 100                 // Maximum DOM entries to keep
    };
    
    // Merge with provided options
    const config = {...defaults, ...options};
    
    // Format timestamp
    const now = new Date();
    const timestamp = now.toLocaleTimeString() + '.' + now.getMilliseconds().toString().padStart(3, '0');
    
    // Create base message prefix
    const prefix = `[${config.component}][${timestamp}]`;
    
    // Format message for display
    let displayMessage = message;
    
    // If message is an object and we should inspect it
    if (typeof message === 'object' && message !== null && config.inspect) {
        try {
            // Try to use JSON.stringify with indentation for readability
            displayMessage = JSON.stringify(message, null, 2);
        } catch (e) {
            // Fallback to toString() if JSON serialization fails
            displayMessage = String(message);
        }
    }
    
    // Console output with visual indicators and appropriate methods
    if (config.toConsole) {
        switch (level) {
            case 'error':
                console.error(`${prefix} 🔴 ERROR: ${displayMessage}`);
                // Add stack trace for errors if requested
                if (config.stackTrace) {
                    console.groupCollapsed('Error Stack Trace');
                    console.trace();
                    console.groupEnd();
                }
                break;
            case 'warn':
                console.warn(`${prefix} 🟠 WARNING: ${displayMessage}`);
                break;
            case 'success':
                console.log(`${prefix} 🟢 SUCCESS: ${displayMessage}`);
                break;
            case 'debug':
                console.debug(`${prefix} 🔍 DEBUG: ${displayMessage}`);
                break;
            case 'trace':
                console.debug(`${prefix} 📋 TRACE: ${displayMessage}`);
                break;
            case 'info':
            default:
                console.log(`${prefix} ℹ️ ${displayMessage}`);
                break;
        }
    }
    
    // DOM logging if container exists and DOM logging is enabled
    if (config.toDom) {
        // First look for component-specific debug container
        let debugContainer = document.getElementById('terma-debug-log');
        
        // Try fallback to generic debug container if component-specific one doesn't exist
        if (!debugContainer) {
            debugContainer = document.getElementById('debug-log');
        }
        
        if (debugContainer) {
            // Create entry with appropriate styling
            const entry = document.createElement('div');
            entry.className = `debug-entry debug-${level}`;
            
            // Create formatted HTML content
            let content = `<span class="debug-time">${timestamp}</span> `;
            
            // Add visual indicator based on level
            switch (level) {
                case 'error': content += '<span class="debug-icon">🔴</span> '; break;
                case 'warn': content += '<span class="debug-icon">🟠</span> '; break;
                case 'success': content += '<span class="debug-icon">🟢</span> '; break;
                case 'debug': content += '<span class="debug-icon">🔍</span> '; break;
                case 'trace': content += '<span class="debug-icon">📋</span> '; break;
                default: content += '<span class="debug-icon">ℹ️</span> '; break;
            }
            
            // Add component name for context
            content += `<span class="debug-component">[${config.component}]</span> `;
            
            // Add the message - format as preformatted text if it's an inspected object
            if (typeof message === 'object' && message !== null && config.inspect) {
                content += `<pre class="debug-message">${displayMessage}</pre>`;
            } else {
                content += `<span class="debug-message">${displayMessage}</span>`;
            }
            
            // Set the HTML content
            entry.innerHTML = content;
            
            // Add to debug container
            debugContainer.appendChild(entry);
            
            // Scroll to the bottom
            debugContainer.scrollTop = debugContainer.scrollHeight;
            
            // Limit entries
            while (debugContainer.children.length > config.domLimit) {
                debugContainer.removeChild(debugContainer.firstChild);
            }
        }
    }
    
    // Return the message to allow chaining or further processing
    return displayMessage;
}

class TermaTerminal {
    /**
     * Initialize the terminal
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        // Enable debug mode with detailed logging
        this.debug = true;
        this.debugLevel = 'info'; // Default debug level (can be error, warn, info, debug, trace)
        
        // Create a debug container for DOM-based logging if it doesn't exist
        this._setupDebugContainer();
        
        // Log initialization with component info
        debugLog('Initializing Terma Terminal component', 'info', {
            component: 'TermaTerminal',
            inspect: false
        });
        
        // Default options
        this.options = Object.assign({
            containerId: 'terma-terminal',
            fontSize: 14,
            fontFamily: "'Courier New', monospace",
            theme: 'default',
            cursorStyle: 'block',
            cursorBlink: true,
            scrollback: 1000,
            serverUrl: 'http://localhost:8765',
            wsUrl: null, // Will be constructed dynamically based on window.location
            debug: true, // Enable/disable debug mode
            debugLevel: 'info' // Default debug level
        }, options);
        
        // Set debug level from options
        this.debugLevel = this.options.debugLevel;
        
        // Log configuration options
        if (this.debug) {
            debugLog('Terminal configuration options', 'debug', {
                component: 'TermaTerminal',
                inspect: true,
                toConsole: true,
                toDom: false
            });
            
            // Log important configuration settings
            debugLog(`Server URL: ${this.options.serverUrl}`, 'debug');
            debugLog(`WebSocket URL: ${this.options.wsUrl || 'Not provided - will be constructed dynamically'}`, 'debug');
        }
        
        // If wsUrl is not provided, construct it dynamically
        if (!this.options.wsUrl) {
            this._setupWebSocketUrl();
        }
        
        // Terminal state
        this.terminal = null;
        this.fitAddon = null;
        this.searchAddon = null;
        this.webLinksAddon = null;
        this.socket = null;
        this.sessionId = null;
        this.sessionList = [];
        this.connected = false;
        this.llmCollapsed = false;
        
        // DOM elements
        this.elements = {
            container: null,
            terminalEl: null,
            sessionSelector: null,
            terminalType: null,
            detachBtn: null,
            settingsBtn: null,
            settingsModal: null,
            settingsClose: null,
            settingsSave: null,
            settingsReset: null,
            llmToggle: null,
            llmContent: null,
            llmOutput: null,
            fontSizeInput: null,
            fontSizeValue: null,
            fontFamilySelect: null,
            themeSelect: null,
            cursorStyleSelect: null,
            cursorBlinkCheckbox: null,
            scrollbackCheckbox: null,
            scrollbackLinesInput: null
        };
        
        // Terminal themes
        this.themes = {
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
            dark: {
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
            }
        };
    }
    
    /**
     * Initialize the terminal component
     */
    async init() {
        console.log('Initializing Terma Terminal...');
        
        // Get DOM elements
        this.getElements();
        
        // Initialize terminal
        this.initXterm();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load settings from localStorage
        this.loadSettings();
        
        // Initialize LLM assistance panel
        this.initLlmAssistancePanel();
        
        // Load LLM options (unified dropdown)
        await this.loadLlmOptions();
        
        // Get available sessions
        await this.fetchSessions();
        
        // Create a new session
        if (this.sessionList.length === 0) {
            await this.createSession();
        } else {
            // Connect to the first available session
            this.connectToSession(this.sessionList[0].id);
        }
        
        // Apply terminal size
        this.fitTerminal();
        
        // Set up resize handler
        window.addEventListener('resize', this.handleResize.bind(this));
        
        console.log('Terma Terminal initialized');
    }
    
    /**
     * Initialize the LLM assistance panel
     */
    initLlmAssistancePanel() {
        const assistancePanel = document.querySelector('.terma-llm-assistance');
        const toggleButton = document.getElementById('terma-llm-toggle');
        const llmHeader = document.querySelector('.terma-llm-header');
        
        if (!assistancePanel || !toggleButton || !llmHeader) {
            console.warn('LLM assistance panel elements not found');
            return;
        }
        
        // Check saved preference
        const savedCollapsed = localStorage.getItem('terma_llm_panel_collapsed');
        if (savedCollapsed === 'true') {
            this.llmCollapsed = true;
            assistancePanel.classList.add('terma-llm-collapsed');
            toggleButton.classList.add('terma-llm-toggle-collapsed');
            toggleButton.querySelector('svg').style.transform = 'rotate(180deg)';
        } else {
            this.llmCollapsed = false;
        }
        
        // Add click handler to header for toggling
        llmHeader.addEventListener('click', () => {
            this.toggleLlmPanel();
        });
        
        // Configure marked.js if available
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (typeof hljs !== 'undefined') {
                        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                        return hljs.highlight(code, { language }).value;
                    }
                    return code;
                },
                langPrefix: 'hljs language-',
                gfm: true,
                breaks: true
            });
        }
    }
    
    /**
     * Get DOM elements
     */
    getElements() {
        this.elements.container = document.querySelector('.terma-terminal-container');
        this.elements.terminalEl = document.getElementById(this.options.containerId);
        this.elements.sessionSelector = document.getElementById('terma-session-selector');
        this.elements.terminalType = document.getElementById('terma-terminal-type');
        this.elements.detachBtn = document.getElementById('terma-detach-btn');
        this.elements.settingsBtn = document.getElementById('terma-settings-btn');
        this.elements.settingsModal = document.getElementById('terma-settings-modal');
        this.elements.settingsClose = document.getElementById('terma-settings-close');
        this.elements.settingsSave = document.getElementById('terma-settings-save');
        this.elements.settingsReset = document.getElementById('terma-settings-reset');
        this.elements.llmToggle = document.getElementById('terma-llm-toggle');
        this.elements.llmContent = document.getElementById('terma-llm-content');
        this.elements.llmOutput = document.getElementById('terma-llm-output');
        this.elements.fontSizeInput = document.getElementById('terma-font-size');
        this.elements.fontSizeValue = document.getElementById('terma-font-size-value');
        this.elements.fontFamilySelect = document.getElementById('terma-font-family');
        this.elements.themeSelect = document.getElementById('terma-theme');
        this.elements.cursorStyleSelect = document.getElementById('terma-cursor-style');
        this.elements.cursorBlinkCheckbox = document.getElementById('terma-cursor-blink');
        this.elements.scrollbackCheckbox = document.getElementById('terma-scroll-back');
        this.elements.scrollbackLinesInput = document.getElementById('terma-scrollback-lines');
    }
    
    /**
     * Initialize xterm.js terminal
     */
    initXterm() {
        // Create terminal instance
        this.terminal = new Terminal({
            fontSize: this.options.fontSize,
            fontFamily: this.options.fontFamily,
            theme: this.themes[this.options.theme],
            cursorStyle: this.options.cursorStyle,
            cursorBlink: this.options.cursorBlink,
            scrollback: this.options.scrollback,
            allowTransparency: true,
            convertEol: true,
            disableStdin: false,
            drawBoldTextInBrightColors: true,
            rightClickSelectsWord: true
        });
        
        // Add addons
        this.fitAddon = new FitAddon.FitAddon();
        this.searchAddon = new SearchAddon.SearchAddon();
        this.webLinksAddon = new WebLinksAddon.WebLinksAddon();
        
        this.terminal.loadAddon(this.fitAddon);
        this.terminal.loadAddon(this.searchAddon);
        this.terminal.loadAddon(this.webLinksAddon);
        
        // Open terminal
        this.terminal.open(this.elements.terminalEl);
        
        // Handle user input
        this.terminal.onData(data => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                // Handle leading ? for command help
                if (data === '?' && this.terminal._core.buffer.normal.baseY + this.terminal.rows === this.terminal._core.buffer.normal.viewportY + this.terminal.rows) {
                    // Show LLM help for the current command
                    const currentLine = this.getCurrentLine();
                    this.requestLlmAssistance(currentLine, false);
                    return;
                }
                
                // Handle trailing ? for output analysis
                if (data === '?' && this.getCurrentLine().trim().length > 0) {
                    // First send the command to the terminal
                    const message = JSON.stringify({
                        type: 'input',
                        data: '\r' // send a return to execute the command
                    });
                    this.socket.send(message);
                    
                    // Wait a bit for output to appear, then analyze
                    setTimeout(() => {
                        this.requestLlmAssistance('', true);
                    }, 500);
                    
                    return;
                }
                
                // Send the data to the terminal session
                const message = JSON.stringify({
                    type: 'input',
                    data: data
                });
                this.socket.send(message);
            }
        });
        
        // Handle key commands
        this.terminal.attachCustomKeyEventHandler(event => {
            // Ctrl+Shift+F: Search
            if (event.ctrlKey && event.shiftKey && event.key === 'F' && event.type === 'keydown') {
                this.searchAddon.activate();
                return false;
            }
            
            return true;
        });
    }
    
    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Session selector
        if (this.elements.sessionSelector) {
            this.elements.sessionSelector.addEventListener('change', async () => {
                const value = this.elements.sessionSelector.value;
                const previousValue = this.sessionId || 'new';
                
                try {
                    if (value === 'new') {
                        // Create a new session
                        this.terminal.writeln('\r\n\x1b[33mCreating new terminal session...\x1b[0m');
                        const sessionId = await this.createSession();
                        
                        if (!sessionId) {
                            throw new Error('Failed to create new session');
                        }
                    } else {
                        // Connect to existing session
                        this.terminal.writeln('\r\n\x1b[33mConnecting to session...\x1b[0m');
                        
                        // Check if the session exists
                        const sessionExists = this.sessionList.some(s => s.id === value);
                        if (!sessionExists) {
                            throw new Error(`Session ${value} not found, it may have expired`);
                        }
                        
                        // Connect to the session
                        this.connectToSession(value);
                        
                        // Update terminal type selector to match new session
                        if (this.elements.terminalType) {
                            const terminalType = this.getCurrentTerminalType();
                            this.elements.terminalType.value = terminalType;
                        }
                    }
                } catch (error) {
                    console.error('Session selection error:', error);
                    this.terminal.writeln(`\x1b[31mError: ${error.message}\x1b[0m`);
                    
                    // Revert the selection
                    setTimeout(() => {
                        for (let i = 0; i < this.elements.sessionSelector.options.length; i++) {
                            if (this.elements.sessionSelector.options[i].value === previousValue) {
                                this.elements.sessionSelector.selectedIndex = i;
                                break;
                            }
                        }
                    }, 0);
                    
                    // Refresh session list in case sessions have expired
                    this.fetchSessions();
                }
            });
        }
        
        // Terminal type selector
        if (this.elements.terminalType) {
            this.elements.terminalType.addEventListener('change', async () => {
                const selectedType = this.elements.terminalType.value;
                const shellCommand = this.getShellCommandFromType(selectedType);
                
                try {
                    // Show a status message in the terminal
                    this.terminal.writeln('\r\n\x1b[33mChanging terminal type to ' + selectedType + '...\x1b[0m');
                    
                    // Create a new session with the selected shell
                    const sessionId = await this.createSession(shellCommand);
                    
                    if (sessionId) {
                        this.terminal.writeln('\x1b[32mTerminal type changed successfully.\x1b[0m');
                    } else {
                        this.terminal.writeln('\x1b[31mFailed to change terminal type. Please try again.\x1b[0m');
                        
                        // Reset the selector to the previous value
                        const currentType = this.getCurrentTerminalType();
                        if (currentType) {
                            this.elements.terminalType.value = currentType;
                        }
                    }
                } catch (error) {
                    console.error('Error changing terminal type:', error);
                    this.terminal.writeln('\x1b[31mError changing terminal type: ' + error.message + '\x1b[0m');
                    
                    // Reset the selector to the previous value
                    const currentType = this.getCurrentTerminalType();
                    if (currentType) {
                        this.elements.terminalType.value = currentType;
                    }
                }
            });
        }
        
        // Detach button
        if (this.elements.detachBtn) {
            this.elements.detachBtn.addEventListener('click', () => {
                this.detachTerminal();
            });
        }
        
        // Settings button
        if (this.elements.settingsBtn) {
            this.elements.settingsBtn.addEventListener('click', () => {
                this.showSettingsModal();
            });
        }
        
        // Settings close button
        if (this.elements.settingsClose) {
            this.elements.settingsClose.addEventListener('click', () => {
                this.hideSettingsModal();
            });
        }
        
        // Settings save button
        if (this.elements.settingsSave) {
            this.elements.settingsSave.addEventListener('click', () => {
                this.saveSettings();
                this.hideSettingsModal();
            });
        }
        
        // Settings reset button
        if (this.elements.settingsReset) {
            this.elements.settingsReset.addEventListener('click', () => {
                this.resetSettings();
            });
        }
        
        // LLM toggle button
        if (this.elements.llmToggle) {
            this.elements.llmToggle.addEventListener('click', () => {
                this.toggleLlmPanel();
            });
        }
        
        // Font size input
        if (this.elements.fontSizeInput && this.elements.fontSizeValue) {
            this.elements.fontSizeInput.addEventListener('input', () => {
                const value = this.elements.fontSizeInput.value;
                this.elements.fontSizeValue.textContent = `${value}px`;
                this.updateTerminalOption('fontSize', parseInt(value, 10));
            });
        }
    }
    
    /**
     * Update terminal option
     * @param {string} option - The option name
     * @param {any} value - The option value
     */
    updateTerminalOption(option, value) {
        if (!this.terminal) return;
        
        switch (option) {
            case 'fontSize':
                this.terminal.options.fontSize = value;
                break;
            case 'fontFamily':
                this.terminal.options.fontFamily = value;
                break;
            case 'theme':
                this.terminal.options.theme = this.themes[value];
                break;
            case 'cursorStyle':
                this.terminal.options.cursorStyle = value;
                break;
            case 'cursorBlink':
                this.terminal.options.cursorBlink = value;
                break;
            case 'scrollback':
                this.terminal.options.scrollback = value;
                break;
        }
        
        // Save the option to local settings
        this.options[option] = value;
        
        // Force xterm to reload with new options
        this.fitTerminal();
    }
    
    /**
     * Load settings from localStorage
     */
    loadSettings() {
        try {
            const savedSettings = localStorage.getItem('terma_terminal_settings');
            if (savedSettings) {
                const settings = JSON.parse(savedSettings);
                
                // Apply settings
                this.options = { ...this.options, ...settings };
                
                // Update UI to match settings
                if (this.elements.fontSizeInput) {
                    this.elements.fontSizeInput.value = this.options.fontSize;
                    this.elements.fontSizeValue.textContent = `${this.options.fontSize}px`;
                }
                
                if (this.elements.fontFamilySelect) {
                    this.elements.fontFamilySelect.value = this.options.fontFamily;
                }
                
                if (this.elements.themeSelect) {
                    this.elements.themeSelect.value = this.options.theme;
                }
                
                if (this.elements.cursorStyleSelect) {
                    this.elements.cursorStyleSelect.value = this.options.cursorStyle;
                }
                
                if (this.elements.cursorBlinkCheckbox) {
                    this.elements.cursorBlinkCheckbox.checked = this.options.cursorBlink;
                }
                
                if (this.elements.scrollbackCheckbox) {
                    this.elements.scrollbackCheckbox.checked = this.options.scrollback > 0;
                }
                
                if (this.elements.scrollbackLinesInput) {
                    this.elements.scrollbackLinesInput.value = this.options.scrollback > 0 ? this.options.scrollback : 1000;
                }
                
                // Apply settings to terminal
                if (this.terminal) {
                    this.terminal.options.fontSize = this.options.fontSize;
                    this.terminal.options.fontFamily = this.options.fontFamily;
                    this.terminal.options.theme = this.themes[this.options.theme];
                    this.terminal.options.cursorStyle = this.options.cursorStyle;
                    this.terminal.options.cursorBlink = this.options.cursorBlink;
                    this.terminal.options.scrollback = this.options.scrollback;
                }
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }
    
    /**
     * Save settings to localStorage
     */
    saveSettings() {
        try {
            // Get settings from UI
            if (this.elements.fontSizeInput) {
                this.options.fontSize = parseInt(this.elements.fontSizeInput.value, 10);
            }
            
            if (this.elements.fontFamilySelect) {
                this.options.fontFamily = this.elements.fontFamilySelect.value;
            }
            
            if (this.elements.themeSelect) {
                this.options.theme = this.elements.themeSelect.value;
            }
            
            if (this.elements.cursorStyleSelect) {
                this.options.cursorStyle = this.elements.cursorStyleSelect.value;
            }
            
            if (this.elements.cursorBlinkCheckbox) {
                this.options.cursorBlink = this.elements.cursorBlinkCheckbox.checked;
            }
            
            if (this.elements.scrollbackCheckbox && this.elements.scrollbackLinesInput) {
                this.options.scrollback = this.elements.scrollbackCheckbox.checked ? parseInt(this.elements.scrollbackLinesInput.value, 10) : 0;
            }
            
            // Apply settings to terminal
            this.terminal.options.fontSize = this.options.fontSize;
            this.terminal.options.fontFamily = this.options.fontFamily;
            this.terminal.options.theme = this.themes[this.options.theme];
            this.terminal.options.cursorStyle = this.options.cursorStyle;
            this.terminal.options.cursorBlink = this.options.cursorBlink;
            this.terminal.options.scrollback = this.options.scrollback;
            
            // Save settings to localStorage
            localStorage.setItem('terma_terminal_settings', JSON.stringify({
                fontSize: this.options.fontSize,
                fontFamily: this.options.fontFamily,
                theme: this.options.theme,
                cursorStyle: this.options.cursorStyle,
                cursorBlink: this.options.cursorBlink,
                scrollback: this.options.scrollback
            }));
            
            // Force terminal to update
            this.fitTerminal();
            
            console.log('Settings saved');
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    }
    
    /**
     * Reset settings to defaults
     */
    resetSettings() {
        // Reset to default values
        this.options.fontSize = 14;
        this.options.fontFamily = "'Courier New', monospace";
        this.options.theme = 'default';
        this.options.cursorStyle = 'block';
        this.options.cursorBlink = true;
        this.options.scrollback = 1000;
        
        // Update UI
        if (this.elements.fontSizeInput) {
            this.elements.fontSizeInput.value = this.options.fontSize;
            this.elements.fontSizeValue.textContent = `${this.options.fontSize}px`;
        }
        
        if (this.elements.fontFamilySelect) {
            this.elements.fontFamilySelect.value = this.options.fontFamily;
        }
        
        if (this.elements.themeSelect) {
            this.elements.themeSelect.value = this.options.theme;
        }
        
        if (this.elements.cursorStyleSelect) {
            this.elements.cursorStyleSelect.value = this.options.cursorStyle;
        }
        
        if (this.elements.cursorBlinkCheckbox) {
            this.elements.cursorBlinkCheckbox.checked = this.options.cursorBlink;
        }
        
        if (this.elements.scrollbackCheckbox) {
            this.elements.scrollbackCheckbox.checked = true;
        }
        
        if (this.elements.scrollbackLinesInput) {
            this.elements.scrollbackLinesInput.value = this.options.scrollback;
        }
        
        // Apply settings to terminal
        this.terminal.options.fontSize = this.options.fontSize;
        this.terminal.options.fontFamily = this.options.fontFamily;
        this.terminal.options.theme = this.themes[this.options.theme];
        this.terminal.options.cursorStyle = this.options.cursorStyle;
        this.terminal.options.cursorBlink = this.options.cursorBlink;
        this.terminal.options.scrollback = this.options.scrollback;
        
        // Force terminal to update
        this.fitTerminal();
        
        console.log('Settings reset to defaults');
    }
    
    /**
     * Show the settings modal
     */
    showSettingsModal() {
        if (this.elements.settingsModal) {
            this.elements.settingsModal.style.display = 'block';
        }
    }
    
    /**
     * Hide the settings modal
     */
    hideSettingsModal() {
        if (this.elements.settingsModal) {
            this.elements.settingsModal.style.display = 'none';
        }
    }
    
    /**
     * Toggle the LLM assistance panel
     */
    toggleLlmPanel() {
        const assistancePanel = document.querySelector('.terma-llm-assistance');
        const toggleButton = document.getElementById('terma-llm-toggle');
        
        if (assistancePanel) {
            if (this.llmCollapsed) {
                // Expand panel
                assistancePanel.classList.remove('terma-llm-collapsed');
                if (toggleButton) {
                    toggleButton.classList.remove('terma-llm-toggle-collapsed');
                    toggleButton.querySelector('svg').style.transform = 'rotate(0deg)';
                }
            } else {
                // Collapse panel
                assistancePanel.classList.add('terma-llm-collapsed');
                if (toggleButton) {
                    toggleButton.classList.add('terma-llm-toggle-collapsed');
                    toggleButton.querySelector('svg').style.transform = 'rotate(180deg)';
                }
            }
            
            this.llmCollapsed = !this.llmCollapsed;
            
            // Save preference
            localStorage.setItem('terma_llm_panel_collapsed', this.llmCollapsed.toString());
            
            // Fit terminal to adjusted size
            setTimeout(() => this.fitTerminal(), 300);
        }
    }
    
    /**
     * Set up debug container for DOM-based logging
     * Creates a hidden debug container if it doesn't exist
     * @private
     */
    _setupDebugContainer() {
        // Only create if it doesn't exist and we're in debug mode
        if (!document.getElementById('terma-debug-log') && this.debug) {
            // Create a container for debug output
            const debugContainer = document.createElement('div');
            debugContainer.id = 'terma-debug-log';
            debugContainer.className = 'terma-debug-log';
            
            // Style to be hidden by default but available for inspection
            debugContainer.style.display = 'none';
            debugContainer.style.position = 'fixed';
            debugContainer.style.bottom = '0';
            debugContainer.style.right = '0';
            debugContainer.style.width = '400px';
            debugContainer.style.height = '300px';
            debugContainer.style.backgroundColor = 'rgba(0,0,0,0.85)';
            debugContainer.style.color = '#f0f0f0';
            debugContainer.style.border = '1px solid #555';
            debugContainer.style.padding = '8px';
            debugContainer.style.overflow = 'auto';
            debugContainer.style.fontFamily = 'monospace';
            debugContainer.style.fontSize = '12px';
            debugContainer.style.zIndex = '9999';
            
            // Add a title and toggle button
            const debugHeader = document.createElement('div');
            debugHeader.style.display = 'flex';
            debugHeader.style.justifyContent = 'space-between';
            debugHeader.style.marginBottom = '8px';
            debugHeader.style.borderBottom = '1px solid #555';
            debugHeader.style.paddingBottom = '4px';
            
            const debugTitle = document.createElement('div');
            debugTitle.innerText = 'Terma Terminal Debug Log';
            debugTitle.style.fontWeight = 'bold';
            
            const debugClear = document.createElement('button');
            debugClear.innerText = 'Clear';
            debugClear.style.background = '#333';
            debugClear.style.color = '#fff';
            debugClear.style.border = '1px solid #555';
            debugClear.style.padding = '2px 6px';
            debugClear.style.cursor = 'pointer';
            debugClear.style.marginLeft = '8px';
            debugClear.onclick = () => {
                // Clear all log entries except the header
                while (debugContainer.childNodes.length > 1) {
                    debugContainer.removeChild(debugContainer.lastChild);
                }
            };
            
            debugHeader.appendChild(debugTitle);
            debugHeader.appendChild(debugClear);
            debugContainer.appendChild(debugHeader);
            
            // Add to document body
            document.body.appendChild(debugContainer);
            
            // Add keyboard shortcut (Alt+D) to toggle debug panel
            document.addEventListener('keydown', (e) => {
                if (e.altKey && e.key === 'd') {
                    debugContainer.style.display = 
                        debugContainer.style.display === 'none' ? 'block' : 'none';
                }
            });
        }
    }

    /**
     * Load LLM options with unified provider:model dropdown
     */
    async loadLlmOptions() {
        debugLog('Loading LLM provider options', 'info', {component: 'TermaTerminal'});
        const providerModelSelect = document.getElementById('terma-llm-provider-model');

        if (!providerModelSelect) {
            debugLog('LLM provider-model selector not found in the DOM', 'warn', {
                component: 'TermaTerminal',
                stackTrace: true
            });
            return;
        }

        debugLog('LLM selector found, clearing existing options', 'debug', {component: 'TermaTerminal'});
        // Clear existing options
        providerModelSelect.innerHTML = '';

        // Add loading option
        const loadingOption = document.createElement('option');
        loadingOption.value = 'loading';
        loadingOption.text = 'Connecting to LLM service...';
        providerModelSelect.appendChild(loadingOption);

        try {
            // For direct access to Rhetor (alternative method)
            const rhetorUrl = "http://localhost:8003";
            debugLog(`Attempting direct connection to Rhetor at ${rhetorUrl}/api/providers`, 'debug', {
                component: 'TermaTerminal'
            });
            
            // Try direct LLM adapter access first
            let response;
            let data;
            let useDirectAccess = false;
            
            try {
                // Try direct connection to LLM adapter
                response = await fetch(`${rhetorUrl}/api/providers`);
                if (response.ok) {
                    data = await response.json();
                    debugLog('Direct LLM Adapter connection successful', 'success', {
                        component: 'TermaTerminal'
                    });
                    debugLog(data, 'debug', {
                        component: 'TermaTerminal',
                        inspect: true,
                        toDom: false // Don't clutter DOM with the full response
                    });
                    useDirectAccess = true;
                }
            } catch (directError) {
                debugLog(`Direct LLM Adapter connection failed: ${directError.message}`, 'warn', {
                    component: 'TermaTerminal'
                });
                debugLog('Falling back to Terma API for LLM providers', 'info', {
                    component: 'TermaTerminal'
                });
            }
            
            // If direct access failed, try through Terma API
            if (!useDirectAccess) {
                const apiUrl = `${this.options.serverUrl}/api/llm/providers`;
                debugLog(`Fetching LLM providers from Terma API: ${apiUrl}`, 'info', {
                    component: 'TermaTerminal'
                });
                
                response = await fetch(apiUrl);
                if (!response.ok) {
                    throw new Error(`Failed to fetch LLM providers: ${response.statusText} (${response.status})`);
                }
                data = await response.json();
                
                debugLog('Successfully fetched LLM providers from Terma API', 'success', {
                    component: 'TermaTerminal'
                });
            }
            
            // Log response data at debug level
            debugLog('LLM providers response received', 'debug', {
                component: 'TermaTerminal'
            });
            
            // Extract provider data
            const providers = data.providers;
            const currentProvider = data.current_provider;
            const currentModel = data.current_model;

            // Clear loading option
            providerModelSelect.innerHTML = '';

            // Add options for each provider and model
            for (const providerId in providers) {
                const provider = providers[providerId];

                // Add each model as "Provider: Model"
                for (const model of provider.models) {
                    const option = document.createElement('option');
                    option.value = `${providerId}:${model.id}`;
                    option.text = `${provider.name}: ${model.name}`;

                    // Mark as selected if this is the current provider and model
                    if (providerId === currentProvider && model.id === currentModel) {
                        option.selected = true;
                    }

                    providerModelSelect.appendChild(option);
                }
            }

            // Log the available models
            debugLog(`Added ${providerModelSelect.options.length} provider/model options to dropdown`, 'info', {
                component: 'TermaTerminal'
            });

            // Add event listener
            providerModelSelect.addEventListener('change', async () => {
                const selectedValue = providerModelSelect.value;
                const [providerId, modelId] = selectedValue.split(':');
                debugLog(`User selected provider: ${providerId}, model: ${modelId}`, 'info', {
                    component: 'TermaTerminal'
                });
                await this.setLlmProviderModel(providerId, modelId);
            });

        } catch (error) {
            debugLog(`Error loading LLM providers: ${error.message}`, 'error', {
                component: 'TermaTerminal',
                stackTrace: true
            });

            // Show error option
            providerModelSelect.innerHTML = '';
            const errorOption = document.createElement('option');
            errorOption.value = 'error';
            errorOption.text = 'LLM service unavailable';
            providerModelSelect.appendChild(errorOption);
        }
    }
    
    /**
     * Load LLM models for a specific provider
     * @param {string} providerId - The provider ID
     * @param {string} currentModel - The current model ID
     */
    async loadLlmModels(providerId, currentModel = null) {
        try {
            const modelSelect = document.getElementById('terma-llm-model');
            if (!modelSelect) {
                console.warn('LLM model selector not found');
                return;
            }
            
            let response;
            let data;
            let useDirectAccess = false;
            
            // Try direct connection to Rhetor first
            const rhetorUrl = "http://localhost:8003";
            
            try {
                // The LLM Adapter doesn't have a specific endpoint for models by provider
                // but we can use the providers endpoint and filter the results
                const directResponse = await fetch(`${rhetorUrl}/api/providers`);
                
                if (directResponse.ok) {
                    const providerData = await directResponse.json();
                    
                    // Check if this provider exists in the response
                    if (providerData.providers && providerData.providers[providerId]) {
                        // Extract models for this provider
                        const models = providerData.providers[providerId].models || [];
                        useDirectAccess = true;
                        
                        // Build our own data structure
                        data = {
                            models: models,
                            current_model: providerData.current_model || ""
                        };
                    }
                }
            } catch (directError) {
                console.warn('Direct LLM models fetch failed, falling back to API:', directError);
            }
            
            // Fall back to Terma API if direct access failed
            if (!useDirectAccess) {
                // Fetch models from the server
                response = await fetch(`${this.options.serverUrl}/api/llm/models/${providerId}`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch LLM models: ${response.statusText}`);
                }
                
                data = await response.json();
            }
            
            // Use the data however we got it
            const models = data.models;
            currentModel = currentModel || data.current_model;
            
            // Clear model options
            modelSelect.innerHTML = '';
            
            // Add model options
            for (const model of models) {
                const option = document.createElement('option');
                option.value = model.id;
                option.text = model.name;
                if (model.id === currentModel) {
                    option.selected = true;
                }
                modelSelect.appendChild(option);
            }
            
        } catch (error) {
            console.error(`Error loading LLM models for provider ${providerId}:`, error);
        }
    }
    
    /**
     * Set the LLM provider and model on the server
     * @param {string} provider - The provider ID
     * @param {string} model - The model ID
     */
    async setLlmProviderModel(provider, model) {
        debugLog(`Setting LLM provider to ${provider} and model to ${model}`, 'info', {
            component: 'TermaTerminal'
        });
        
        try {
            // First try direct connection to Rhetor
            const rhetorUrl = "http://localhost:8003";
            
            debugLog(`Attempting direct connection to Rhetor at ${rhetorUrl}/api/provider`, 'debug', {
                component: 'TermaTerminal'
            });
            
            // Create request payload
            const payload = { provider_id: provider, model_id: model };
            
            // Log payload at trace level
            debugLog('Request payload:', 'trace', {
                component: 'TermaTerminal'
            });
            
            debugLog(payload, 'trace', {
                component: 'TermaTerminal',
                inspect: true,
                toDom: false // Don't clutter DOM with simple objects
            });
            
            try {
                // Try through direct LLM Adapter connection
                const directResponse = await fetch(`${rhetorUrl}/api/provider`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                if (directResponse.ok) {
                    const data = await directResponse.json();
                    
                    debugLog(`Set LLM provider to ${provider} and model to ${model} via direct connection`, 'success', {
                        component: 'TermaTerminal'
                    });
                    
                    // Log response data at debug level
                    debugLog('LLM adapter response:', 'debug', {
                        component: 'TermaTerminal'
                    });
                    
                    debugLog(data, 'debug', {
                        component: 'TermaTerminal',
                        inspect: true, 
                        toDom: false // Don't clutter DOM with response data
                    });
                    
                    return;
                } else {
                    // Log error response for debugging
                    const errorText = await directResponse.text();
                    throw new Error(`LLM adapter returned status ${directResponse.status}: ${errorText}`);
                }
            } catch (directError) {
                debugLog(`Direct LLM provider set failed: ${directError.message}`, 'warn', {
                    component: 'TermaTerminal'
                });
                
                debugLog('Falling back to Terma API for setting LLM provider/model', 'info', {
                    component: 'TermaTerminal'
                });
            }
            
            // Fall back to Terma API if direct connection fails
            const apiUrl = `${this.options.serverUrl}/api/llm/set`;
            
            debugLog(`Sending request to Terma API: ${apiUrl}`, 'debug', {
                component: 'TermaTerminal'
            });
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ provider, model })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Failed to set LLM provider and model: ${response.statusText} (${response.status}) - ${errorText}`);
            }
            
            debugLog(`Successfully set LLM provider to ${provider} and model to ${model} via Terma API`, 'success', {
                component: 'TermaTerminal'
            });
            
            // Try to get and log response data
            try {
                const data = await response.json();
                debugLog('Terma API response:', 'debug', {
                    component: 'TermaTerminal'
                });
                
                debugLog(data, 'debug', {
                    component: 'TermaTerminal',
                    inspect: true,
                    toDom: false
                });
            } catch (jsonError) {
                // Non-JSON response or empty response is ok
                debugLog('Non-JSON response from Terma API (this may be normal)', 'debug', {
                    component: 'TermaTerminal'
                });
            }
            
        } catch (error) {
            debugLog(`Error setting LLM provider and model: ${error.message}`, 'error', {
                component: 'TermaTerminal',
                stackTrace: true
            });
            
            // Display user-friendly message in terminal
            if (this.terminal) {
                this.terminal.writeln(`\r\n\x1b[31mError setting LLM provider/model: ${error.message}\x1b[0m`);
            }
            
            // Also show in LLM panel if available
            const llmOutput = document.getElementById('terma-llm-output');
            if (llmOutput) {
                llmOutput.innerHTML = `<div class="terma-llm-error">Error setting LLM provider and model: ${error.message}</div>`;
            }
        }
    }
    
    /**
     * Fit the terminal to the container
     */
    fitTerminal() {
        if (this.fitAddon) {
            try {
                this.fitAddon.fit();
                
                // Send terminal size to server if connected
                if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                    const message = JSON.stringify({
                        type: 'resize',
                        cols: this.terminal.cols,
                        rows: this.terminal.rows
                    });
                    this.socket.send(message);
                }
            } catch (error) {
                console.error('Error fitting terminal:', error);
            }
        }
    }
    
    /**
     * Handle window resize event
     */
    handleResize() {
        this.fitTerminal();
    }
    
    /**
     * Set up WebSocket URL based on current location using fixed port
     * Handles various server URL formats and environment-specific port configurations
     * @private
     */
    _setupWebSocketUrl() {
        // Skip if wsUrl is explicitly provided in options
        if (this.options.wsUrl) {
            debugLog(`Using provided WebSocket URL: ${this.options.wsUrl}`, 'info', {
                component: 'TermaTerminal'
            });
            return;
        }
        
        try {
            debugLog(`Constructing WebSocket URL from server URL: ${this.options.serverUrl}`, 'debug', {
                component: 'TermaTerminal'
            });
            
            // Parse the current server URL
            let serverUrlObj;
            
            // Different URL format handling
            if (this.options.serverUrl.startsWith('http')) {
                // If a full URL is provided, parse it
                serverUrlObj = new URL(this.options.serverUrl);
                debugLog(`Parsed server URL from HTTP URL: ${this.options.serverUrl}`, 'debug', {
                    component: 'TermaTerminal'
                });
            } else {
                // Otherwise, assume it's relative to the current location
                serverUrlObj = new URL(this.options.serverUrl, window.location.origin);
                debugLog(`Parsed server URL from relative path: ${this.options.serverUrl} with origin ${window.location.origin}`, 'debug', {
                    component: 'TermaTerminal'
                });
            }
            
            // Get hostname from server URL or window location
            const hostname = serverUrlObj.hostname || window.location.hostname;
            debugLog(`Using hostname: ${hostname}`, 'debug', {
                component: 'TermaTerminal'
            });
            
            // Extract port information
            // First check if the serverUrl contains a port specification
            const serverPort = serverUrlObj.port ? parseInt(serverUrlObj.port) : 
                              (serverUrlObj.protocol === 'https:' ? 443 : 80);
            
            debugLog(`Server port identified as: ${serverPort}`, 'debug', {
                component: 'TermaTerminal'
            });
                
            // Use the port specified in options if available, fallback to environment port
            // The server port is likely 8765 (TERMA_API_PORT) so we need WS_PORT (8767)
            const wsPort = serverPort === 8765 ? 8767 : serverPort + 2;
            
            debugLog(`WebSocket port calculated as: ${wsPort} (${serverPort === 8765 ? 
                'Standard Terma ports 8765/8767' : 
                `Server port ${serverPort} + 2`})`, 'debug', {
                component: 'TermaTerminal'
            });
            
            // Get protocol from server URL, convert http -> ws and https -> wss
            const protocol = serverUrlObj.protocol.startsWith('https') ? 'wss:' : 'ws:';
            
            // Construct the WebSocket URL with dynamic port
            this.options.wsUrl = `${protocol}//${hostname}:${wsPort}/ws`;
            
            debugLog(`WebSocket URL constructed successfully: ${this.options.wsUrl}`, 'success', {
                component: 'TermaTerminal'
            });
            
        } catch (error) {
            debugLog(`Error constructing WebSocket URL: ${error.message}`, 'error', {
                component: 'TermaTerminal',
                stackTrace: true
            });
            
            // Create fallback WebSocket URL
            // Determine hostname for fallback (use current hostname instead of hardcoded localhost)
            const fallbackHost = window.location.hostname || 'localhost';
            
            // Fallback but still use dynamic hostname with standard Terma WebSocket port
            this.options.wsUrl = `ws://${fallbackHost}:8767/ws`;
            
            debugLog(`Using fallback WebSocket URL: ${this.options.wsUrl}`, 'warn', {
                component: 'TermaTerminal'
            });
            
            // Log additional diagnostic information
            debugLog('Connection details for troubleshooting:', 'debug', {
                component: 'TermaTerminal'
            });
            
            debugLog(`Current location: ${window.location.href}`, 'trace', {
                component: 'TermaTerminal',
                toDom: false
            });
            
            debugLog(`Server URL: ${this.options.serverUrl}`, 'trace', {
                component: 'TermaTerminal',
                toDom: false
            });
            
            debugLog(`Fallback hostname: ${fallbackHost}`, 'trace', {
                component: 'TermaTerminal',
                toDom: false
            });
        }
        
        // Add WebSocket URL test
        this._testWebSocketUrl();
    }
    
    /**
     * Test the WebSocket URL for basic connectivity
     * Doesn't establish a full connection, just tests if the endpoint is reachable
     * @private
     */
    _testWebSocketUrl() {
        if (!this.options.wsUrl) return;
        
        debugLog(`Testing WebSocket connectivity to: ${this.options.wsUrl}`, 'debug', {
            component: 'TermaTerminal'
        });
        
        // Create a test WebSocket connection
        try {
            const testSocket = new WebSocket(this.options.wsUrl.replace('/ws', '/ping'));
            
            // Set a timeout to close the connection if it doesn't connect or error out
            const timeout = setTimeout(() => {
                if (testSocket.readyState !== WebSocket.CLOSED && 
                    testSocket.readyState !== WebSocket.CLOSING) {
                    testSocket.close();
                    debugLog('WebSocket test timed out - server may not support ping endpoint', 'warn', {
                        component: 'TermaTerminal'
                    });
                }
            }, 2000);
            
            // Set up event handlers
            testSocket.onopen = () => {
                debugLog('WebSocket test connection successful', 'success', {
                    component: 'TermaTerminal'
                });
                
                // Close after successful test
                testSocket.close();
                clearTimeout(timeout);
            };
            
            testSocket.onerror = (error) => {
                debugLog(`WebSocket test connection failed: ${error ? error.message : 'Unknown error'}`, 'warn', {
                    component: 'TermaTerminal'
                });
                
                // Provide fallback suggestion
                debugLog('This may be normal if the /ping endpoint is not implemented', 'info', {
                    component: 'TermaTerminal'
                });
                
                clearTimeout(timeout);
            };
            
            testSocket.onclose = () => {
                clearTimeout(timeout);
            };
        } catch (error) {
            debugLog(`Error creating test WebSocket: ${error.message}`, 'error', {
                component: 'TermaTerminal'
            });
        }
    }
    
    /**
     * Fetch available sessions from the server
     */
    async fetchSessions() {
        try {
            const response = await fetch(`${this.options.serverUrl}/api/sessions`);
            if (response.ok) {
                const data = await response.json();
                this.sessionList = data.sessions || [];
                
                // Update session selector
                this.updateSessionSelector();
                
                return this.sessionList;
            } else {
                console.error('Error fetching sessions:', response.statusText);
                return [];
            }
        } catch (error) {
            console.error('Error fetching sessions:', error);
            return [];
        }
    }
    
    /**
     * Update the session selector dropdown
     */
    updateSessionSelector() {
        if (!this.elements.sessionSelector) return;
        
        // Clear existing options (except "New Session")
        while (this.elements.sessionSelector.options.length > 1) {
            this.elements.sessionSelector.remove(1);
        }
        
        // Add sessions
        this.sessionList.forEach(session => {
            const option = document.createElement('option');
            option.value = session.id;
            option.text = `Session ${session.id.slice(0, 8)}...`;
            if (this.sessionId === session.id) {
                option.selected = true;
            }
            this.elements.sessionSelector.add(option);
        });
    }
    
    /**
     * Create a new terminal session
     * @param {string} shellCommand - Optional shell command to run
     */
    async createSession(shellCommand = null) {
        try {
            // Close existing connection
            this.closeConnection();
            
            // Determine shell command
            if (!shellCommand && this.elements.terminalType) {
                shellCommand = this.getShellCommandFromType(this.elements.terminalType.value);
            }
            
            // Create payload
            const payload = {};
            if (shellCommand) {
                payload.shell_command = shellCommand;
            }
            
            // Make request to create session
            const response = await fetch(`${this.options.serverUrl}/api/sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            if (response.ok) {
                const data = await response.json();
                this.sessionId = data.session_id;
                
                // Update session list
                await this.fetchSessions();
                
                // Connect to the session
                this.connectToSession(this.sessionId);
                
                console.log(`Created new session: ${this.sessionId}`);
                return this.sessionId;
            } else {
                const errorText = await response.text();
                console.error('Error creating session:', errorText);
                return null;
            }
        } catch (error) {
            console.error('Error creating session:', error);
            return null;
        }
    }
    
    /**
     * Get shell command from terminal type
     * @param {string} terminalType - Terminal type
     * @returns {string} Shell command
     */
    getShellCommandFromType(terminalType) {
        switch (terminalType) {
            case 'bash':
                return '/bin/bash';
            case 'python':
                return 'python';
            case 'node':
                return 'node';
            default:
                return null;
        }
    }
    
    /**
     * Get the current terminal type based on the session's shell command
     * @returns {string} Terminal type identifier (bash, python, node, or default)
     */
    getCurrentTerminalType() {
        // If we don't have a session list or current session ID, return default
        if (!this.sessionList || !this.sessionId) {
            return 'default';
        }
        
        // Find the current session
        const session = this.sessionList.find(s => s.id === this.sessionId);
        if (!session) {
            return 'default';
        }
        
        // Determine type from shell command
        const shellCommand = session.shell_command;
        
        if (shellCommand.includes('bash')) {
            return 'bash';
        } else if (shellCommand.includes('python')) {
            return 'python';
        } else if (shellCommand.includes('node')) {
            return 'node';
        } else {
            return 'default';
        }
    }
    
    /**
     * Connect to a terminal session
     * @param {string} sessionId - Session ID
     */
    connectToSession(sessionId) {
        // Close existing connection
        this.closeConnection();
        
        // Set session ID
        this.sessionId = sessionId;
        
        // Update session selector
        if (this.elements.sessionSelector) {
            for (let i = 0; i < this.elements.sessionSelector.options.length; i++) {
                if (this.elements.sessionSelector.options[i].value === sessionId) {
                    this.elements.sessionSelector.selectedIndex = i;
                    break;
                }
            }
        }
        
        // Clear terminal
        this.terminal.clear();
        
        // Connect WebSocket
        this._connectWebSocket(sessionId);
    }
    
    /**
     * Connect to WebSocket for terminal session
     * @param {string} sessionId - Session ID
     * @param {boolean} isReconnect - Whether this is a reconnection attempt
     * @param {number} reconnectAttempt - The current reconnection attempt number
     */
    _connectWebSocket(sessionId, isReconnect = false, reconnectAttempt = 0) {
        // Create WebSocket connection
        const wsUrl = `${this.options.wsUrl}/${sessionId}`;
        
        // Track connection status for this attempt
        let connectionEstablished = false;
        
        try {
            this.socket = new WebSocket(wsUrl);
            
            // Set up WebSocket event handlers
            this.socket.onopen = () => {
                this.connected = true;
                connectionEstablished = true;
                console.log(`Connected to session: ${sessionId}`);
                
                // Only show message if this isn't a silent reconnect
                if (!isReconnect || reconnectAttempt > 0) {
                    this.terminal.writeln('\x1b[32mConnected to terminal session\x1b[0m');
                }
                
                // Reset any reconnection data
                this._resetReconnectionAttempts();
                
                // Resize the terminal to ensure correct dimensions
                this.fitTerminal();
            };
            
            this.socket.onclose = (event) => {
                const wasConnected = this.connected;
                this.connected = false;
                console.log(`Disconnected from session: ${sessionId}, code: ${event.code}, reason: ${event.reason}`);
                
                // Show disconnection message if we were previously connected
                if (wasConnected && !isReconnect) {
                    this.terminal.writeln('\x1b[31mDisconnected from terminal session\x1b[0m');
                }
                
                // Attempt to reconnect if the session might still be active
                // Don't reconnect if this was a normal closure or if we never connected
                if (event.code !== 1000 && (connectionEstablished || isReconnect)) {
                    this._handleReconnection(sessionId, reconnectAttempt);
                }
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                
                // Only show error message if this isn't a reconnection attempt
                if (!isReconnect) {
                    this.terminal.writeln('\x1b[31mError connecting to terminal session\x1b[0m');
                }
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    
                    // Handle different message types
                    switch (message.type) {
                        case 'output':
                            // Write output to terminal
                            this.terminal.write(message.data);
                            break;
                            
                        case 'error':
                            // Write error to terminal
                            this.terminal.writeln(`\x1b[31mError: ${message.message}\x1b[0m`);
                            break;
                            
                        case 'llm_response':
                            // Display LLM response in the assistance panel
                            const isLoading = message.loading === true;
                            const isError = message.error === true;
                            this.displayLlmResponse(message.content, isLoading, isError);
                            break;
                            
                        default:
                            console.warn('Unknown message type:', message.type);
                    }
                } catch (error) {
                    console.error('Error handling message:', error);
                }
            };
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            
            if (!isReconnect) {
                this.terminal.writeln(`\x1b[31mError creating WebSocket connection: ${error.message}\x1b[0m`);
            }
            
            // Attempt to reconnect on failure to create socket
            this._handleReconnection(sessionId, reconnectAttempt);
        }
    }
    
    /**
     * Handle WebSocket reconnection
     * @param {string} sessionId - Session ID to reconnect to
     * @param {number} currentAttempt - Current reconnection attempt
     */
    _handleReconnection(sessionId, currentAttempt) {
        // Maximum reconnection attempts
        const MAX_RECONNECT_ATTEMPTS = 5;
        
        // Calculate delay with exponential backoff: 500ms, 1000ms, 2000ms, 4000ms, etc.
        const nextAttempt = currentAttempt + 1;
        const delay = Math.min(30000, 500 * Math.pow(2, currentAttempt));
        
        if (nextAttempt <= MAX_RECONNECT_ATTEMPTS) {
            console.log(`Reconnecting to session ${sessionId}, attempt ${nextAttempt} in ${delay}ms`);
            
            // Only show reconnection message on first attempt
            if (currentAttempt === 0) {
                this.terminal.writeln(`\x1b[33mConnection lost. Attempting to reconnect...\x1b[0m`);
            }
            
            // Schedule reconnection
            this._reconnectTimeout = setTimeout(() => {
                // Check if the session is still in the session list
                this.fetchSessions().then(sessions => {
                    const sessionExists = sessions.some(s => s.id === sessionId);
                    
                    if (sessionExists) {
                        // Session still exists, reconnect
                        this._connectWebSocket(sessionId, true, nextAttempt);
                    } else {
                        // Session no longer exists
                        this.terminal.writeln(`\x1b[31mSession no longer exists. Please create a new session.\x1b[0m`);
                        this._resetReconnectionAttempts();
                    }
                }).catch(error => {
                    console.error('Error fetching sessions for reconnection:', error);
                    
                    // Try to reconnect anyway
                    this._connectWebSocket(sessionId, true, nextAttempt);
                });
            }, delay);
        } else {
            // Max reconnection attempts reached
            this.terminal.writeln(`\x1b[31mFailed to reconnect after ${MAX_RECONNECT_ATTEMPTS} attempts. Please refresh the page.\x1b[0m`);
            this._resetReconnectionAttempts();
        }
    }
    
    /**
     * Reset reconnection attempt data
     */
    _resetReconnectionAttempts() {
        if (this._reconnectTimeout) {
            clearTimeout(this._reconnectTimeout);
            this._reconnectTimeout = null;
        }
    }
    
    /**
     * Close current WebSocket connection
     */
    closeConnection() {
        // Reset any pending reconnection attempts
        this._resetReconnectionAttempts();
        
        // Close the WebSocket connection if it's open
        if (this.socket) {
            try {
                // Only attempt a clean close if the socket is still open
                if (this.socket.readyState === WebSocket.OPEN ||
                    this.socket.readyState === WebSocket.CONNECTING) {
                    this.socket.close(1000, "Closed by user");
                }
            } catch (error) {
                console.error('Error closing WebSocket connection:', error);
            } finally {
                this.socket = null;
            }
        }
        
        this.connected = false;
    }
    
    /**
     * Detach the terminal to a standalone window
     */
    detachTerminal() {
        if (!this.sessionId) return;
        
        // Generate a proper URL to launch the terminal
        const serverHost = this.options.serverUrl.replace(/^https?:\/\//, '').split(':')[0];
        const serverPort = this.options.serverUrl.split(':')[2] || '8765';
        
        // Create a proper URL with protocol
        const protocol = window.location.protocol;
        const launchUrl = `${protocol}//${serverHost}:${serverPort}/terminal/launch?session_id=${this.sessionId}`;
        
        // Open in a new window with a specific size
        const width = Math.min(1200, window.screen.availWidth * 0.8);
        const height = Math.min(800, window.screen.availHeight * 0.8);
        const left = (window.screen.availWidth - width) / 2;
        const top = (window.screen.availHeight - height) / 2;
        
        window.open(
            launchUrl, 
            `terma_terminal_${this.sessionId}`,
            `width=${width},height=${height},left=${left},top=${top},menubar=no,toolbar=no,location=no,status=no`
        );
    }
    
    /**
     * Get the current command line text
     * @param {boolean} includeOutput - Whether to include recent output
     * @returns {string} Current command line or command with output
     */
    getCurrentLine(includeOutput = false) {
        // Get the buffer content of the current line
        const buffer = this.terminal._core.buffer;
        const lineY = buffer.normal.baseY + buffer.normal.cursorY;
        const line = buffer.normal.lines.get(lineY);
        
        let text = '';
        for (let i = 0; i < line.length; i++) {
            text += line.getString(i);
        }
        
        const currentLine = text.trim();
        
        // If we don't need to include output, just return the current line
        if (!includeOutput) {
            return currentLine;
        }
        
        // Otherwise, try to gather the previous command and its output
        try {
            // Number of lines to look back for output context
            const MAX_OUTPUT_LINES = 15;
            
            // Check if there's a command prompt in the current line
            const promptIndex = currentLine.indexOf('$');
            if (promptIndex >= 0) {
                // Extract just the command after the prompt
                return currentLine.substring(promptIndex + 1).trim();
            }
            
            // Look back for the previous command prompt and gather output
            let command = '';
            let output = [];
            let foundCommand = false;
            
            // Start at current line and go up to find command + output
            for (let i = 0; i < MAX_OUTPUT_LINES; i++) {
                const checkLineY = lineY - i;
                if (checkLineY < 0) break;
                
                const checkLine = buffer.normal.lines.get(checkLineY);
                if (!checkLine) break;
                
                let lineText = '';
                for (let j = 0; j < checkLine.length; j++) {
                    lineText += checkLine.getString(j);
                }
                lineText = lineText.trim();
                
                // Skip empty lines
                if (!lineText) continue;
                
                // Check if this line has a prompt
                const promptIdx = lineText.indexOf('$');
                if (promptIdx >= 0 && !foundCommand) {
                    // We found the command line
                    command = lineText.substring(promptIdx + 1).trim();
                    foundCommand = true;
                    continue;
                }
                
                // If we already found a command, add this line to output (in reverse order)
                if (foundCommand) {
                    output.unshift(lineText);
                }
            }
            
            // If we found a command, return it with some of its output
            if (foundCommand) {
                if (output.length > 0) {
                    return `${command}\n\nOutput:\n${output.join('\n')}`;
                }
                return command;
            }
            
            // Fallback to just the current line if we couldn't identify a command
            return currentLine;
        } catch (error) {
            console.error('Error getting command and output:', error);
            return currentLine;
        }
    }
    
    /**
     * Request LLM assistance for a command
     * @param {string} command - The command to analyze
     * @param {boolean} isOutputAnalysis - Whether this is an output analysis request
     */
    async requestLlmAssistance(command, isOutputAnalysis = false) {
        if (!command) return;
        
        try {
            // Ensure the LLM panel is visible
            if (this.llmCollapsed) {
                this.toggleLlmPanel();
            }
            
            // Get the output context if this is an output analysis
            if (isOutputAnalysis) {
                command = this.getCurrentLine(true);
            }
            
            // Show loading state
            this.displayLlmResponse("Analyzing command and generating response...", true, false);
            
            // Send WebSocket message for LLM assistance
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                const message = JSON.stringify({
                    type: 'llm_assist',
                    command: command,
                    is_output_analysis: isOutputAnalysis
                });
                this.socket.send(message);
            } else {
                this.displayLlmResponse("Error: WebSocket not connected. Make sure your terminal session is active.", false, true);
            }
        } catch (error) {
            console.error('Error requesting LLM assistance:', error);
            this.displayLlmResponse(`Error: ${error.message}`, false, true);
        }
    }
    
    /**
     * Display LLM response in the assistance panel
     * @param {string} response - The LLM response
     * @param {boolean} loading - Whether this is a loading message
     * @param {boolean} error - Whether this is an error message
     */
    displayLlmResponse(response, loading = false, error = false) {
        const llmOutput = document.getElementById('terma-llm-output');
        if (!llmOutput) return;
        
        // Add appropriate CSS classes
        llmOutput.className = 'terma-llm-output';
        if (loading) llmOutput.classList.add('terma-llm-loading');
        if (error) llmOutput.classList.add('terma-llm-error');
        
        // Format the response using marked.js if available
        if (!loading && typeof marked !== 'undefined') {
            try {
                llmOutput.innerHTML = marked.parse(response);
                
                // Apply syntax highlighting to code blocks if hljs is available
                if (typeof hljs !== 'undefined') {
                    const codeBlocks = llmOutput.querySelectorAll('pre code');
                    codeBlocks.forEach(block => {
                        hljs.highlightElement(block);
                    });
                }
            } catch (e) {
                console.error('Error parsing markdown:', e);
                llmOutput.textContent = response;
            }
        } else {
            // For loading messages or if marked.js is not available, use simple text
            llmOutput.textContent = response;
        }
        
        // Make sure the LLM panel is visible
        if (this.llmCollapsed) {
            this.toggleLlmPanel();
        }
    }
}

// Initialize the terminal when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Get server hostname from current window location
    const hostname = window.location.hostname || 'localhost';
    
    // Use explicit ports that match the values in tekton-launch
    const terminalOptions = {
        containerId: 'terma-terminal',
        serverUrl: `http://${hostname}:8765`, // TERMA_API_PORT
        wsUrl: `ws://${hostname}:8767/ws`     // TERMA_WS_PORT
    };
    
    const terminal = new TermaTerminal(terminalOptions);
    terminal.init();
    
    // Expose terminal to global scope for debugging
    window.termaTerminal = terminal;
});