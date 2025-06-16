/**
 * Terma Terminal Service
 * 
 * Service component for the Terma terminal that handles:
 * - WebSocket connection management
 * - Terminal session management
 * - LLM assistance communication
 * - Terminal state persistence
 * 
 * Extends the BaseService pattern with Terma-specific functionality.
 */

class TermaService extends window.tektonUI.componentUtils.BaseService {
    /**
     * Create a new Terma service
     * 
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        // Initialize base service with name and API URL
        const termaPort = window.TERMA_PORT || 8004;
        super('termaService', options.serverUrl || `http://localhost:${termaPort}`);
        
        // Configure WebSocket URL (either provided or constructed)
        this.wsUrl = options.wsUrl || this._constructWebSocketUrl();
        
        // Service state
        this.connected = false;
        this.socket = null;
        this.sessionId = null;
        this.sessionList = [];
        this.callbackMap = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectTimeout = null;
        
        // Terminal options (default values that can be overridden)
        this.terminalOptions = Object.assign({
            fontSize: 14,
            fontFamily: "'Courier New', monospace",
            theme: 'default',
            cursorStyle: 'block',
            cursorBlink: true,
            scrollback: 1000
        }, options.terminalOptions || {});
        
        // Initialize session cleanup handler
        this._setupSessionCleanup();
    }
    
    /**
     * Connect to the Terma service
     * 
     * @returns {Promise<boolean>} - Promise resolving to true if connection succeeds
     */
    async connect() {
        if (this.connected) return true;
        
        try {
            // Check API availability
            const response = await fetch(`${this.apiUrl}/api/health`);
            if (!response.ok) {
                throw new Error(`API health check failed: ${response.status}`);
            }
            
            this.connected = true;
            this.dispatchEvent('connected', {});
            
            // Fetch available sessions
            await this.fetchSessions();
            
            return true;
        } catch (error) {
            console.error(`Failed to connect to Terma service: ${error.message}`);
            this.connected = false;
            this.dispatchEvent('connectionFailed', { error });
            throw error;
        }
    }
    
    /**
     * Disconnect from the Terma service
     */
    disconnect() {
        if (!this.connected) return;
        
        // Close websocket connection if open
        this.closeWebSocketConnection();
        
        // Reset state
        this.connected = false;
        
        // Cancel any pending reconnection attempts
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }
        
        this.dispatchEvent('disconnected', {});
    }
    
    /**
     * Fetch available terminal sessions
     * 
     * @returns {Promise<Array>} Available sessions
     */
    async fetchSessions() {
        try {
            const response = await fetch(`${this.apiUrl}/api/sessions`);
            if (!response.ok) {
                throw new Error(`Failed to fetch sessions: ${response.status}`);
            }
            
            const data = await response.json();
            this.sessionList = data.sessions || [];
            
            // Notify listeners
            this.dispatchEvent('sessionsUpdated', { sessions: this.sessionList });
            
            return this.sessionList;
        } catch (error) {
            console.error('Error fetching sessions:', error);
            return [];
        }
    }
    
    /**
     * Create a new terminal session
     * 
     * @param {string} shellCommand - Optional shell command to run
     * @returns {Promise<string>} The ID of the created session
     */
    async createSession(shellCommand = null) {
        try {
            // Close existing WebSocket connection
            this.closeWebSocketConnection();
            
            // Prepare request payload
            const payload = {};
            if (shellCommand) {
                payload.shell_command = shellCommand;
            }
            
            // Create session via API
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
            
            // Update session list
            await this.fetchSessions();
            
            // Notify listeners
            this.dispatchEvent('sessionCreated', { sessionId: this.sessionId });
            
            return this.sessionId;
        } catch (error) {
            console.error('Error creating session:', error);
            this.dispatchEvent('sessionError', { error });
            throw error;
        }
    }
    
    /**
     * Connect to a specific terminal session
     * 
     * @param {string} sessionId - ID of the session to connect to
     * @returns {Promise<boolean>} True if connection succeeds
     */
    async connectToSession(sessionId) {
        try {
            // Close existing connection
            this.closeWebSocketConnection();
            
            // Set the current session ID
            this.sessionId = sessionId;
            
            // Connect WebSocket to this session
            const result = await this.connectWebSocket(sessionId);
            
            // Update session list to reflect current session
            await this.fetchSessions();
            
            // Notify listeners
            this.dispatchEvent('sessionConnected', { sessionId });
            
            return result;
        } catch (error) {
            console.error(`Error connecting to session ${sessionId}:`, error);
            this.dispatchEvent('sessionError', { error, sessionId });
            throw error;
        }
    }
    
    /**
     * Connect a WebSocket to a specific session
     * 
     * @param {string} sessionId - Session ID to connect to
     * @returns {Promise<boolean>} True if connection succeeds
     */
    connectWebSocket(sessionId) {
        return new Promise((resolve, reject) => {
            try {
                // Construct the session-specific WebSocket URL
                const wsUrl = `${this.wsUrl}/${sessionId}`;
                
                // Create and configure WebSocket
                this.socket = new WebSocket(wsUrl);
                
                // Track if connection was actually established
                let connectionEstablished = false;
                
                // Handle WebSocket open event
                this.socket.onopen = () => {
                    this.reconnectAttempts = 0;
                    connectionEstablished = true;
                    this.dispatchEvent('websocketConnected', { sessionId });
                    resolve(true);
                };
                
                // Handle WebSocket close event
                this.socket.onclose = (event) => {
                    this.dispatchEvent('websocketClosed', { code: event.code, reason: event.reason });
                    
                    // Attempt to reconnect if this wasn't a normal closure
                    if (event.code !== 1000 && (connectionEstablished || this.reconnectAttempts > 0)) {
                        this._handleReconnection(sessionId);
                    }
                };
                
                // Handle WebSocket errors
                this.socket.onerror = (error) => {
                    this.dispatchEvent('websocketError', { error });
                    reject(error);
                };
                
                // Handle incoming WebSocket messages
                this.socket.onmessage = (event) => {
                    this._handleWebSocketMessage(event.data);
                };
                
                // Set a connection timeout
                setTimeout(() => {
                    if (!connectionEstablished) {
                        reject(new Error('WebSocket connection timeout'));
                        this.socket.close();
                    }
                }, 10000);
                
            } catch (error) {
                console.error('Error connecting WebSocket:', error);
                reject(error);
            }
        });
    }
    
    /**
     * Handle reconnection attempts
     * 
     * @param {string} sessionId - Session ID to reconnect to
     */
    _handleReconnection(sessionId) {
        // Cancel any existing reconnection timeout
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
        }
        
        // Increment attempts counter
        this.reconnectAttempts++;
        
        // Check if we've reached the maximum number of attempts
        if (this.reconnectAttempts > this.maxReconnectAttempts) {
            this.dispatchEvent('reconnectionFailed', { 
                sessionId, 
                attempts: this.reconnectAttempts 
            });
            return;
        }
        
        // Calculate delay with exponential backoff
        const delay = Math.min(30000, 500 * Math.pow(2, this.reconnectAttempts - 1));
        
        // Notify that we're attempting to reconnect
        this.dispatchEvent('reconnecting', {
            sessionId,
            attempt: this.reconnectAttempts,
            maxAttempts: this.maxReconnectAttempts,
            delay
        });
        
        // Schedule reconnection attempt
        this.reconnectTimeout = setTimeout(async () => {
            try {
                // First check if the session still exists
                await this.fetchSessions();
                const sessionExists = this.sessionList.some(s => s.id === sessionId);
                
                if (sessionExists) {
                    // Try to reconnect to the session
                    await this.connectWebSocket(sessionId);
                } else {
                    // Session no longer exists
                    this.dispatchEvent('sessionExpired', { sessionId });
                }
            } catch (error) {
                console.error(`Reconnection attempt ${this.reconnectAttempts} failed:`, error);
                
                // Try again with next attempt
                this._handleReconnection(sessionId);
            }
        }, delay);
    }
    
    /**
     * Close the WebSocket connection
     */
    closeWebSocketConnection() {
        // Cancel any pending reconnection attempts
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }
        
        // Close the WebSocket if it exists
        if (this.socket) {
            // Check the current state of the socket
            if (this.socket.readyState === WebSocket.OPEN || 
                this.socket.readyState === WebSocket.CONNECTING) {
                
                try {
                    // Attempt to close gracefully
                    this.socket.close(1000, "Client closed connection");
                } catch (error) {
                    console.error('Error closing WebSocket:', error);
                }
            }
            
            // Clear the socket reference
            this.socket = null;
        }
    }
    
    /**
     * Handle incoming WebSocket messages
     * 
     * @param {string} data - Raw message data
     */
    _handleWebSocketMessage(data) {
        try {
            // Parse the message
            const message = JSON.parse(data);
            
            // Process based on message type
            switch (message.type) {
                case 'output':
                    // Terminal output
                    this.dispatchEvent('terminalOutput', { data: message.data });
                    break;
                    
                case 'error':
                    // Error message
                    this.dispatchEvent('terminalError', { message: message.message });
                    break;
                    
                case 'llm_response':
                    // LLM response
                    this.dispatchEvent('llmResponse', {
                        content: message.content,
                        loading: message.loading === true,
                        error: message.error === true
                    });
                    break;
                    
                default:
                    // Unknown message type
                    console.warn('Unknown WebSocket message type:', message.type);
            }
        } catch (error) {
            console.error('Error handling WebSocket message:', error);
        }
    }
    
    /**
     * Send data to the terminal session
     * 
     * @param {string} data - Data to send to the terminal
     * @returns {boolean} True if data was sent successfully
     */
    sendInput(data) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            console.error('WebSocket not connected');
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
    }
    
    /**
     * Resize the terminal
     * 
     * @param {number} rows - Number of rows
     * @param {number} cols - Number of columns
     * @returns {boolean} True if resize message was sent successfully
     */
    resizeTerminal(rows, cols) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            console.error('WebSocket not connected');
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
    }
    
    /**
     * Request LLM assistance for a command
     * 
     * @param {string} command - The command to analyze
     * @param {boolean} isOutputAnalysis - Whether this is an output analysis
     * @returns {boolean} True if request was sent successfully
     */
    requestLlmAssistance(command, isOutputAnalysis = false) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            console.error('WebSocket not connected');
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
    }
    
    /**
     * Load LLM models from adapter
     * 
     * @returns {Promise<Object>} LLM provider and model data
     */
    async loadLlmProviderModels() {
        try {
            // Try direct connection to LLM adapter first
            const rhetorPort = window.RHETOR_PORT || 8003;
            const rhetorUrl = `http://localhost:${rhetorPort}/api/providers`;
            
            try {
                const response = await fetch(rhetorUrl);
                if (response.ok) {
                    const data = await response.json();
                    return data;
                }
            } catch (directError) {
                console.warn('Direct LLM adapter connection failed, falling back to Terma API');
            }
            
            // Fall back to Terma API for LLM providers
            const response = await fetch(`${this.apiUrl}/api/llm/providers`);
            if (!response.ok) {
                throw new Error(`Failed to fetch LLM providers: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error loading LLM providers:', error);
            throw error;
        }
    }
    
    /**
     * Set the LLM provider and model
     * 
     * @param {string} providerId - Provider ID
     * @param {string} modelId - Model ID
     * @returns {Promise<boolean>} True if successfully set
     */
    async setLlmProviderModel(providerId, modelId) {
        try {
            // Try direct LLM adapter first
            const rhetorPort = window.RHETOR_PORT || 8003;
            const rhetorUrl = `http://localhost:${rhetorPort}/api/provider`;
            
            try {
                const directResponse = await fetch(rhetorUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        provider_id: providerId, 
                        model_id: modelId 
                    })
                });
                
                if (directResponse.ok) {
                    return true;
                }
            } catch (directError) {
                console.warn('Direct LLM adapter connection failed, falling back to Terma API');
            }
            
            // Fall back to Terma API
            const response = await fetch(`${this.apiUrl}/api/llm/set`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ provider: providerId, model: modelId })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to set LLM provider and model: ${response.statusText}`);
            }
            
            return true;
        } catch (error) {
            console.error('Error setting LLM provider and model:', error);
            throw error;
        }
    }
    
    /**
     * Save terminal settings
     * 
     * @param {Object} settings - Terminal settings to save
     */
    saveSettings(settings) {
        // Update terminal options
        this.terminalOptions = Object.assign(this.terminalOptions, settings);
        
        // Save to local storage
        localStorage.setItem('terma_terminal_settings', JSON.stringify(this.terminalOptions));
        
        // Notify listeners
        this.dispatchEvent('settingsChanged', { settings: this.terminalOptions });
    }
    
    /**
     * Load terminal settings
     * 
     * @returns {Object} Terminal settings
     */
    loadSettings() {
        try {
            const savedSettings = localStorage.getItem('terma_terminal_settings');
            if (savedSettings) {
                const settings = JSON.parse(savedSettings);
                this.terminalOptions = Object.assign(this.terminalOptions, settings);
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
        
        return this.terminalOptions;
    }
    
    /**
     * Reset terminal settings to defaults
     */
    resetSettings() {
        this.terminalOptions = {
            fontSize: 14,
            fontFamily: "'Courier New', monospace",
            theme: 'default',
            cursorStyle: 'block',
            cursorBlink: true,
            scrollback: 1000
        };
        
        // Save to local storage
        localStorage.setItem('terma_terminal_settings', JSON.stringify(this.terminalOptions));
        
        // Notify listeners
        this.dispatchEvent('settingsChanged', { settings: this.terminalOptions });
    }
    
    /**
     * Check health of the Terma service
     * 
     * @returns {Promise<Object>} Health status
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.apiUrl}/api/health`);
            if (!response.ok) {
                throw new Error(`Health check failed: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Health check error:', error);
            throw error;
        }
    }
    
    /**
     * Get WebSocket URL based on server URL
     * 
     * @returns {string} WebSocket URL
     */
    _constructWebSocketUrl() {
        try {
            // Parse the server URL
            const serverUrl = new URL(this.apiUrl);
            
            // Use hostname from server URL
            const hostname = serverUrl.hostname;
            
            // Determine port - Terma WebSocket port is 2 more than API port
            // (API port is 8765, WebSocket port is 8767)
            const serverPort = serverUrl.port ? parseInt(serverUrl.port) : 80;
            const wsPort = serverPort === 8765 ? 8767 : serverPort + 2;
            
            // Determine protocol (ws or wss)
            const wsProtocol = serverUrl.protocol === 'https:' ? 'wss:' : 'ws:';
            
            // Construct WebSocket URL
            return `${wsProtocol}//${hostname}:${wsPort}/ws`;
        } catch (error) {
            console.error('Error constructing WebSocket URL:', error);
            
            // Use a fallback WebSocket URL with dynamic port
            const hostname = window.location.hostname || 'localhost';
            const termaPort = window.TERMA_PORT || 8004;
            return `ws://${hostname}:${termaPort}/ws`;
        }
    }
    
    /**
     * Set up session cleanup
     */
    _setupSessionCleanup() {
        // Add event listener for beforeunload to clean up sessions
        window.addEventListener('beforeunload', () => {
            this.closeWebSocketConnection();
        });
    }
    
    /**
     * Create a fallback object for when service is unavailable
     * 
     * @returns {Object} Fallback object with stub methods
     */
    createFallback() {
        return {
            connect: async () => {
                console.warn('Using fallback Terma service');
                return true;
            },
            disconnect: () => {},
            fetchSessions: async () => [],
            createSession: async () => null,
            connectToSession: async () => false,
            sendInput: () => false,
            resizeTerminal: () => false,
            requestLlmAssistance: () => false,
            loadLlmProviderModels: async () => ({
                providers: {},
                current_provider: '',
                current_model: ''
            }),
            loadSettings: () => ({
                fontSize: 14,
                fontFamily: "'Courier New', monospace", 
                theme: 'default',
                cursorStyle: 'block', 
                cursorBlink: true,
                scrollback: 1000
            }),
            saveSettings: () => {},
            resetSettings: () => {},
            addEventListener: () => {},
            removeEventListener: () => {}
        };
    }
}

// Register the service globally
window.tektonUI = window.tektonUI || {};
window.tektonUI.services = window.tektonUI.services || {};
window.tektonUI.services.termaService = new TermaService();