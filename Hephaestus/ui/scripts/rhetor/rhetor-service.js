/**
 * Rhetor Service
 * Provides communication with the Rhetor API for LLM management, prompt engineering, and budget tracking
 * Enhanced with debug instrumentation and follows Single Port Architecture
 */

console.log('[FILE_TRACE] Loading: rhetor-service.js');
(function() {
  'use strict';
  
  // Debug namespace
  const DEBUG_NAMESPACE = 'rhetor-service';
  
  /**
   * Rhetor Service class
   * Implements BaseService pattern and Single Port Architecture
   */
  class RhetorService {
    /**
     * Constructor for Rhetor Service
     */
    constructor() {
      // Initialize debug service if available
      this.debugService = window.TektonDebug || null;
      this.debugMode = false;
      
      this.debug('constructor', 'Initializing Rhetor service');
      
      // Service configuration
      this.serviceName = 'rhetorService';
      this.servicePort = window.RHETOR_PORT || 8003;
      this.apiUrl = `http://localhost:${this.servicePort}/api`;
      this.wsUrl = `ws://localhost:${this.servicePort}/ws`;
      this.apiVersion = null;
      
      // Connection state
      this.connected = false;
      this.ws = null;
      this.wsConnected = false;
      this.reconnectAttempts = 0;
      this.maxReconnectAttempts = 5;
      this.reconnectInterval = 2000; // Start with 2 seconds
      this.reconnecting = false;
      
      // Event handler registry
      this.eventListeners = {
        connected: [],
        connectionFailed: [],
        error: [],
        websocketConnected: [],
        websocketDisconnected: [],
        providersUpdated: [],
        modelsUpdated: [],
        settingsUpdated: [],
        budgetUpdated: [],
        templatesUpdated: [],
        conversationsUpdated: [],
        message: []
      };
      
      // Set up caches with expiration
      this.caches = {
        providers: {
          data: [],
          timestamp: 0,
          ttl: 5 * 60 * 1000 // 5 minutes
        },
        models: {
          data: {},
          timestamp: 0,
          ttl: 5 * 60 * 1000 // 5 minutes
        },
        settings: {
          data: null,
          timestamp: 0,
          ttl: 5 * 60 * 1000 // 5 minutes
        },
        budget: {
          data: null,
          timestamp: 0,
          ttl: 60 * 1000 // 1 minute
        },
        templates: {
          data: [],
          timestamp: 0,
          ttl: 5 * 60 * 1000 // 5 minutes
        },
        conversations: {
          data: [],
          timestamp: 0,
          ttl: 60 * 1000 // 1 minute
        }
      };
      
      // State for LLM configuration
      this.state = {
        providers: [],
        selectedProvider: null,
        selectedModel: null,
        connected: false,
        status: 'disconnected',
        lastError: null,
        budget: {
          limit: 0,
          used: 0,
          remaining: 0,
          period: 'monthly',
          alerts: {
            enabled: false,
            threshold: 80
          }
        },
        templates: [],
        conversations: []
      };
      
      // Initialize with persisted state if available
      this._loadPersistedState();
      
      // Auto-connect
      setTimeout(() => {
        this._autoConnect();
      }, 0);
      
      this.info('constructor', 'Rhetor service initialized');
    }
    
    /**
     * Auto-connect to Rhetor API and WebSocket
     * @private
     */
    async _autoConnect() {
      this.debug('_autoConnect', 'Attempting auto-connect');
      
      try {
        // Check if Rhetor API is available
        await this.connect();
        
        // Connect to WebSocket if API is available
        if (this.connected) {
          this.connectWebSocket();
        }
      } catch (error) {
        this.error('_autoConnect', 'Failed to auto-connect', { error: error.message });
      }
    }
    
    /**
     * Load persisted state from storage
     * @private
     */
    _loadPersistedState() {
      this.debug('_loadPersistedState', 'Loading persisted state');
      
      try {
        // Use local storage for persistence
        const persistedState = localStorage.getItem('rhetor_service_state');
        
        if (persistedState) {
          const state = JSON.parse(persistedState);
          
          // Apply stored values to current state
          if (state.selectedProvider) {
            this.state.selectedProvider = state.selectedProvider;
          }
          
          if (state.selectedModel) {
            this.state.selectedModel = state.selectedModel;
          }
          
          this.debug('_loadPersistedState', 'Loaded persisted state', { state });
        } else {
          this.debug('_loadPersistedState', 'No persisted state found');
        }
      } catch (error) {
        this.error('_loadPersistedState', 'Error loading persisted state', { error: error.message });
      }
    }
    
    /**
     * Persist state to storage
     * @private
     */
    _persistState() {
      this.debug('_persistState', 'Persisting state');
      
      try {
        // Create state object for persistence
        const state = {
          selectedProvider: this.state.selectedProvider,
          selectedModel: this.state.selectedModel
        };
        
        // Save to local storage
        localStorage.setItem('rhetor_service_state', JSON.stringify(state));
        
        this.debug('_persistState', 'State persisted successfully');
      } catch (error) {
        this.error('_persistState', 'Error persisting state', { error: error.message });
      }
    }
    
    /**
     * Connect to the Rhetor API
     * @returns {Promise<boolean>} - Promise resolving to connection status
     */
    async connect() {
      this.debug('connect', 'Connecting to Rhetor API', { url: this.apiUrl });
      
      try {
        // Check if Rhetor API is available
        const response = await fetch(`${this.apiUrl}/health`);
        
        if (!response.ok) {
          this.connected = false;
          this.state.connected = false;
          this.state.status = 'disconnected';
          this.state.lastError = `Failed to connect to Rhetor API: ${response.status} ${response.statusText}`;
          
          this.dispatchEvent('connectionFailed', { 
            error: this.state.lastError
          });
          
          this.error('connect', 'Connection failed', { 
            status: response.status,
            statusText: response.statusText
          });
          
          return false;
        }
        
        const data = await response.json();
        this.connected = true;
        this.state.connected = true;
        this.state.status = 'connected';
        this.state.lastError = null;
        this.apiVersion = data.version || 'unknown';
        
        // Dispatch connected event
        this.dispatchEvent('connected', { 
          version: this.apiVersion 
        });
        
        this.info('connect', 'Connected to Rhetor API', { version: this.apiVersion });
        
        // Load initial data
        await Promise.all([
          this.getProviders(),
          this.getSettings(),
          this.getBudget()
        ]);
        
        return true;
      } catch (error) {
        this.connected = false;
        this.state.connected = false;
        this.state.status = 'disconnected';
        this.state.lastError = `Failed to connect to Rhetor API: ${error.message}`;
        
        this.dispatchEvent('connectionFailed', { 
          error: this.state.lastError
        });
        
        this.error('connect', 'Connection failed with error', { error: error.message });
        
        return false;
      }
    }
    
    /**
     * Connect to Rhetor WebSocket for real-time updates
     * @returns {boolean} Success status
     */
    connectWebSocket() {
      this.debug('connectWebSocket', 'Connecting to WebSocket', { url: this.wsUrl });
      
      if (this.ws) {
        this.debug('connectWebSocket', 'WebSocket already exists, not connecting again');
        return true; // Already connected or connecting
      }
      
      try {
        this.ws = new WebSocket(this.wsUrl);
        
        this.ws.onopen = () => {
          this.wsConnected = true;
          this.reconnectAttempts = 0;
          this.reconnectInterval = 2000; // Reset reconnect interval
          this.reconnecting = false;
          this.state.status = 'connected';
          
          this.info('connectWebSocket', 'WebSocket connected');
          this.dispatchEvent('websocketConnected', {});
        };
        
        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            
            this.debug('onWebSocketMessage', 'Received WebSocket message', { 
              type: message.type 
            });
            
            // Handle different message types
            switch (message.type) {
              case 'STATUS':
                this.state.status = message.data.status;
                this.dispatchEvent('statusUpdate', message.data);
                break;
                
              case 'TYPING':
                this.dispatchEvent('typing', message.data);
                break;
                
              case 'ERROR':
                this.state.lastError = message.data.message;
                this.dispatchEvent('error', message.data);
                this.error('onWebSocketMessage', 'Error message from server', { 
                  error: message.data.message 
                });
                break;
                
              default:
                this.dispatchEvent('message', message);
                break;
            }
          } catch (error) {
            this.error('onWebSocketMessage', 'Error processing WebSocket message', { 
              error: error.message 
            });
          }
        };
        
        this.ws.onerror = (error) => {
          this.state.lastError = `WebSocket error: ${error.message || 'Unknown error'}`;
          
          this.error('onWebSocketError', 'WebSocket error', { 
            error: this.state.lastError 
          });
          
          this.dispatchEvent('error', { 
            error: this.state.lastError
          });
        };
        
        this.ws.onclose = () => {
          this.wsConnected = false;
          this.state.status = this.connected ? 'connected' : 'disconnected';
          
          this.warn('onWebSocketClose', 'WebSocket closed');
          this.dispatchEvent('websocketDisconnected', {});
          
          // Attempt to reconnect if not intentionally closed
          if (!this.reconnecting && this.connected) {
            this._attemptReconnect();
          }
        };
        
        return true;
      } catch (error) {
        this.wsConnected = false;
        this.state.lastError = `Failed to connect to WebSocket: ${error.message}`;
        
        this.error('connectWebSocket', 'Failed to connect to WebSocket', { 
          error: error.message 
        });
        
        this.dispatchEvent('error', { 
          error: this.state.lastError
        });
        
        return false;
      }
    }
    
    /**
     * Attempt to reconnect to WebSocket
     * @private
     */
    _attemptReconnect() {
      if (this.reconnecting || this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.error('_attemptReconnect', 'Max reconnect attempts reached', {
          attempts: this.reconnectAttempts,
          maxAttempts: this.maxReconnectAttempts
        });
        return;
      }
      
      this.reconnecting = true;
      this.reconnectAttempts++;
      
      // Use exponential backoff for reconnection
      const delay = Math.min(30000, this.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1));
      
      this.debug('_attemptReconnect', 'Attempting to reconnect', {
        attempt: this.reconnectAttempts,
        maxAttempts: this.maxReconnectAttempts,
        delay: delay
      });
      
      this.dispatchEvent('reconnecting', { 
        attempt: this.reconnectAttempts,
        maxAttempts: this.maxReconnectAttempts,
        delay
      });
      
      setTimeout(() => {
        this.reconnecting = false;
        this.connectWebSocket();
      }, delay);
    }
    
    /**
     * Disconnect from WebSocket
     */
    disconnectWebSocket() {
      this.debug('disconnectWebSocket', 'Disconnecting WebSocket');
      
      if (this.ws) {
        this.ws.close();
        this.ws = null;
        this.wsConnected = false;
        this.debug('disconnectWebSocket', 'WebSocket disconnected');
      }
    }
    
    /**
     * Reset connection
     * @returns {Promise<boolean>} Connection success
     */
    async resetConnection() {
      this.debug('resetConnection', 'Resetting connection');
      
      this.disconnectWebSocket();
      
      // Clear caches
      for (const cache of Object.values(this.caches)) {
        cache.timestamp = 0;
      }
      
      return this.connect();
    }
    
    /**
     * Get available LLM providers
     * @param {boolean} [forceRefresh=false] - Force refresh from server
     * @returns {Promise<Array>} Available providers
     */
    async getProviders(forceRefresh = false) {
      this.debug('getProviders', 'Getting providers', { forceRefresh });
      
      // Check cache first
      const cache = this.caches.providers;
      const now = Date.now();
      
      if (!forceRefresh && cache.timestamp > 0 && now - cache.timestamp < cache.ttl) {
        this.debug('getProviders', 'Using cached providers', { 
          count: cache.data.length,
          cacheAge: now - cache.timestamp
        });
        return cache.data;
      }
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        this.debug('getProviders', 'Fetching providers from API');
        const response = await fetch(`${this.apiUrl}/providers`);
        
        if (!response.ok) {
          this.error('getProviders', 'Failed to fetch providers', { 
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to fetch providers: ${response.status} ${response.statusText}` 
          });
          
          return cache.data;
        }
        
        const data = await response.json();
        const providers = data.providers || [];
        
        // Update cache
        cache.data = providers;
        cache.timestamp = now;
        
        // Update state
        this.state.providers = providers;
        
        this.debug('getProviders', 'Providers updated', { count: providers.length });
        
        // Dispatch event
        this.dispatchEvent('providersUpdated', { providers });
        
        return providers;
      } catch (error) {
        this.error('getProviders', 'Error fetching providers', { error: error.message });
        
        this.dispatchEvent('error', { 
          error: `Failed to fetch providers: ${error.message}` 
        });
        
        return cache.data;
      }
    }
    
    /**
     * Get model assignments matrix
     * @returns {Promise<Object>} Model assignments (defaults and components)
     */
    async getModelAssignments() {
      this.debug('getModelAssignments', 'Getting model assignments');
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/models/assignments`);
        
        if (!response.ok) {
          this.error('getModelAssignments', 'Failed to fetch assignments', { 
            status: response.status,
            statusText: response.statusText
          });
          throw new Error(`Failed to fetch assignments: ${response.status}`);
        }
        
        const data = await response.json();
        this.debug('getModelAssignments', 'Assignments fetched', { 
          defaults: Object.keys(data.defaults || {}),
          components: Object.keys(data.components || {}).length
        });
        
        return data;
      } catch (error) {
        this.error('getModelAssignments', 'Error fetching assignments', { error: error.message });
        throw error;
      }
    }
    
    /**
     * Update model assignment for a component
     * @param {string} component - Component name
     * @param {string} capability - Capability (code, planning, reasoning, chat)
     * @param {string} modelId - Model ID or "use_default"
     * @returns {Promise<Object>} Update result
     */
    async updateModelAssignment(component, capability, modelId) {
      this.debug('updateModelAssignment', 'Updating model assignment', { 
        component, capability, modelId 
      });
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/models/assignments/component`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            component,
            capability,
            model_id: modelId
          })
        });
        
        if (!response.ok) {
          this.error('updateModelAssignment', 'Failed to update assignment', { 
            status: response.status,
            statusText: response.statusText
          });
          throw new Error(`Failed to update assignment: ${response.status}`);
        }
        
        const data = await response.json();
        this.debug('updateModelAssignment', 'Assignment updated', data);
        
        // Dispatch event for UI update
        this.dispatchEvent('assignmentUpdated', { component, capability, modelId });
        
        return data;
      } catch (error) {
        this.error('updateModelAssignment', 'Error updating assignment', { error: error.message });
        throw error;
      }
    }
    
    /**
     * Get all available models (across all providers)
     * @param {boolean} [includeDeprecated=false] - Include deprecated models
     * @returns {Promise<Array>} Available models
     */
    async getAllModels(includeDeprecated = false) {
      this.debug('getAllModels', 'Getting all available models', { includeDeprecated });
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const url = `${this.apiUrl}/models${includeDeprecated ? '?include_deprecated=true' : ''}`;
        const response = await fetch(url);
        
        if (!response.ok) {
          this.error('getAllModels', 'Failed to fetch models', { 
            status: response.status,
            statusText: response.statusText
          });
          throw new Error(`Failed to fetch models: ${response.status}`);
        }
        
        const models = await response.json();
        this.debug('getAllModels', 'Models fetched', { count: models.length });
        
        return models;
      } catch (error) {
        this.error('getAllModels', 'Error fetching models', { error: error.message });
        throw error;
      }
    }
    
    /**
     * Get models for a specific provider
     * @param {string} provider - Provider name
     * @param {boolean} [forceRefresh=false] - Force refresh from server
     * @returns {Promise<Array>} Available models
     */
    async getModels(provider, forceRefresh = false) {
      this.debug('getModels', 'Getting models for provider', { provider, forceRefresh });
      
      // Check cache first
      const cache = this.caches.models;
      const now = Date.now();
      
      if (!forceRefresh && cache.data[provider] && now - cache.timestamp < cache.ttl) {
        this.debug('getModels', 'Using cached models', { 
          provider,
          count: cache.data[provider].length,
          cacheAge: now - cache.timestamp
        });
        return cache.data[provider];
      }
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        this.debug('getModels', 'Fetching models from API');
        const response = await fetch(`${this.apiUrl}/providers/${provider}/models`);
        
        if (!response.ok) {
          this.error('getModels', 'Failed to fetch models', { 
            provider,
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to fetch models: ${response.status} ${response.statusText}` 
          });
          
          return cache.data[provider] || [];
        }
        
        const data = await response.json();
        const models = data.models || [];
        
        // Update cache
        cache.data[provider] = models;
        cache.timestamp = now;
        
        this.debug('getModels', 'Models updated', { provider, count: models.length });
        
        // Dispatch event
        this.dispatchEvent('modelsUpdated', { provider, models });
        
        return models;
      } catch (error) {
        this.error('getModels', 'Error fetching models', { 
          provider,
          error: error.message
        });
        
        this.dispatchEvent('error', { 
          error: `Failed to fetch models: ${error.message}` 
        });
        
        return cache.data[provider] || [];
      }
    }
    
    /**
     * Get Rhetor settings
     * @param {boolean} [forceRefresh=false] - Force refresh from server
     * @returns {Promise<Object>} Settings object
     */
    async getSettings(forceRefresh = false) {
      this.debug('getSettings', 'Getting settings', { forceRefresh });
      
      // Check cache first
      const cache = this.caches.settings;
      const now = Date.now();
      
      if (!forceRefresh && cache.data && now - cache.timestamp < cache.ttl) {
        this.debug('getSettings', 'Using cached settings', { 
          cacheAge: now - cache.timestamp
        });
        return cache.data;
      }
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        this.debug('getSettings', 'Fetching settings from API');
        const response = await fetch(`${this.apiUrl}/settings`);
        
        if (!response.ok) {
          this.error('getSettings', 'Failed to fetch settings', { 
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to fetch settings: ${response.status} ${response.statusText}` 
          });
          
          return cache.data || {};
        }
        
        const settings = await response.json();
        
        // Update cache
        cache.data = settings;
        cache.timestamp = now;
        
        // Update selected provider and model from settings
        if (settings.defaultProvider) {
          this.state.selectedProvider = settings.defaultProvider;
        }
        
        if (settings.defaultModel) {
          this.state.selectedModel = settings.defaultModel;
        }
        
        this.debug('getSettings', 'Settings updated', { settings });
        
        // Dispatch event
        this.dispatchEvent('settingsUpdated', { settings });
        
        return settings;
      } catch (error) {
        this.error('getSettings', 'Error fetching settings', { error: error.message });
        
        this.dispatchEvent('error', { 
          error: `Failed to fetch settings: ${error.message}` 
        });
        
        return cache.data || {};
      }
    }
    
    /**
     * Save Rhetor settings
     * @param {Object} settings - Settings to save
     * @returns {Promise<Object>} Updated settings
     */
    async saveSettings(settings) {
      this.debug('saveSettings', 'Saving settings', { settings });
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/settings`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(settings)
        });
        
        if (!response.ok) {
          this.error('saveSettings', 'Failed to save settings', { 
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to save settings: ${response.status} ${response.statusText}` 
          });
          
          return null;
        }
        
        const updatedSettings = await response.json();
        
        // Update cache
        this.caches.settings.data = updatedSettings;
        this.caches.settings.timestamp = Date.now();
        
        // Update selected provider and model if in settings
        if (updatedSettings.defaultProvider) {
          this.state.selectedProvider = updatedSettings.defaultProvider;
        }
        
        if (updatedSettings.defaultModel) {
          this.state.selectedModel = updatedSettings.defaultModel;
        }
        
        // Persist state
        this._persistState();
        
        this.debug('saveSettings', 'Settings saved successfully', { updatedSettings });
        
        // Dispatch event
        this.dispatchEvent('settingsUpdated', { settings: updatedSettings });
        
        return updatedSettings;
      } catch (error) {
        this.error('saveSettings', 'Error saving settings', { error: error.message });
        
        this.dispatchEvent('error', { 
          error: `Failed to save settings: ${error.message}` 
        });
        
        return null;
      }
    }
    
    /**
     * Test connection to provider/model
     * @param {string} provider - Provider name
     * @param {string} model - Model name
     * @param {Object} [options={}] - Additional options
     * @returns {Promise<Object>} Test result
     */
    async testConnection(provider, model, options = {}) {
      this.debug('testConnection', 'Testing connection', { provider, model, options });
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/test_connection`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            provider,
            model,
            ...options
          })
        });
        
        if (!response.ok) {
          this.error('testConnection', 'Connection test failed', { 
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Connection test failed: ${response.status} ${response.statusText}` 
          });
          
          return {
            success: false,
            error: `HTTP Error ${response.status}: ${response.statusText}`
          };
        }
        
        const result = await response.json();
        
        this.debug('testConnection', 'Connection test result', { result });
        
        // Dispatch event
        this.dispatchEvent('connectionTested', { provider, model, result });
        
        return result;
      } catch (error) {
        this.error('testConnection', 'Error testing connection', { error: error.message });
        
        this.dispatchEvent('error', { 
          error: `Connection test failed: ${error.message}` 
        });
        
        return {
          success: false,
          error: error.message
        };
      }
    }
    
    /**
     * Get budget information
     * @param {string} [period='monthly'] - Period for budget data ('daily', 'weekly', 'monthly')
     * @param {boolean} [forceRefresh=false] - Force refresh from server
     * @returns {Promise<Object>} Budget data
     */
    async getBudget(period = 'monthly', forceRefresh = false) {
      this.debug('getBudget', 'Getting budget', { period, forceRefresh });
      
      // Check cache first
      const cache = this.caches.budget;
      const now = Date.now();
      
      // Always refresh budget data if the period changes
      const currPeriod = cache.data?.period;
      forceRefresh = forceRefresh || (currPeriod && currPeriod !== period);
      
      if (!forceRefresh && cache.data && now - cache.timestamp < cache.ttl) {
        this.debug('getBudget', 'Using cached budget', { 
          period: cache.data.period,
          cacheAge: now - cache.timestamp
        });
        return cache.data;
      }
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        this.debug('getBudget', 'Fetching budget from API');
        const response = await fetch(`${this.apiUrl}/budget?period=${period}`);
        
        if (!response.ok) {
          this.error('getBudget', 'Failed to fetch budget', { 
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to fetch budget: ${response.status} ${response.statusText}` 
          });
          
          return cache.data || this.state.budget;
        }
        
        const budget = await response.json();
        
        // Add period to budget data
        budget.period = period;
        
        // Update cache
        cache.data = budget;
        cache.timestamp = now;
        
        // Update state
        this.state.budget = {
          ...this.state.budget,
          ...budget,
          period
        };
        
        this.debug('getBudget', 'Budget updated', { budget });
        
        // Dispatch event
        this.dispatchEvent('budgetUpdated', { budget });
        
        return budget;
      } catch (error) {
        this.error('getBudget', 'Error fetching budget', { error: error.message });
        
        this.dispatchEvent('error', { 
          error: `Failed to fetch budget: ${error.message}` 
        });
        
        return cache.data || this.state.budget;
      }
    }
    
    /**
     * Save budget settings
     * @param {Object} settings - Budget settings to save
     * @returns {Promise<Object>} Updated budget settings
     */
    async saveBudgetSettings(settings) {
      this.debug('saveBudgetSettings', 'Saving budget settings', { settings });
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/budget/settings`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(settings)
        });
        
        if (!response.ok) {
          this.error('saveBudgetSettings', 'Failed to save budget settings', { 
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to save budget settings: ${response.status} ${response.statusText}` 
          });
          
          return null;
        }
        
        const updatedSettings = await response.json();
        
        // Update state
        this.state.budget = {
          ...this.state.budget,
          limit: updatedSettings.limit,
          alerts: updatedSettings.alerts
        };
        
        // Invalidate cache to force refresh on next getBudget call
        this.caches.budget.timestamp = 0;
        
        this.debug('saveBudgetSettings', 'Budget settings saved successfully', { updatedSettings });
        
        // Dispatch event
        this.dispatchEvent('budgetSettingsUpdated', { settings: updatedSettings });
        
        return updatedSettings;
      } catch (error) {
        this.error('saveBudgetSettings', 'Error saving budget settings', { error: error.message });
        
        this.dispatchEvent('error', { 
          error: `Failed to save budget settings: ${error.message}` 
        });
        
        return null;
      }
    }
    
    /**
     * Get templates
     * @param {boolean} [forceRefresh=false] - Force refresh from server
     * @returns {Promise<Array>} Templates array
     */
    async getTemplates(forceRefresh = false) {
      this.debug('getTemplates', 'Getting templates', { forceRefresh });
      
      // Check cache first
      const cache = this.caches.templates;
      const now = Date.now();
      
      if (!forceRefresh && cache.timestamp > 0 && now - cache.timestamp < cache.ttl) {
        this.debug('getTemplates', 'Using cached templates', { 
          count: cache.data.length,
          cacheAge: now - cache.timestamp
        });
        return cache.data;
      }
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        this.debug('getTemplates', 'Fetching templates from API');
        const response = await fetch(`${this.apiUrl}/templates`);
        
        if (!response.ok) {
          this.error('getTemplates', 'Failed to fetch templates', { 
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to fetch templates: ${response.status} ${response.statusText}` 
          });
          
          return cache.data;
        }
        
        const data = await response.json();
        const templates = data.templates || [];
        
        // Update cache
        cache.data = templates;
        cache.timestamp = now;
        
        // Update state
        this.state.templates = templates;
        
        this.debug('getTemplates', 'Templates updated', { count: templates.length });
        
        // Dispatch event
        this.dispatchEvent('templatesUpdated', { templates });
        
        return templates;
      } catch (error) {
        this.error('getTemplates', 'Error fetching templates', { error: error.message });
        
        this.dispatchEvent('error', { 
          error: `Failed to fetch templates: ${error.message}` 
        });
        
        return cache.data;
      }
    }
    
    /**
     * Get template by ID
     * @param {string} templateId - Template ID
     * @returns {Promise<Object>} Template object
     */
    async getTemplate(templateId) {
      this.debug('getTemplate', 'Getting template', { templateId });
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/templates/${templateId}`);
        
        if (!response.ok) {
          this.error('getTemplate', 'Failed to fetch template', { 
            templateId,
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to fetch template: ${response.status} ${response.statusText}` 
          });
          
          return null;
        }
        
        const template = await response.json();
        
        this.debug('getTemplate', 'Template retrieved', { template });
        
        return template;
      } catch (error) {
        this.error('getTemplate', 'Error fetching template', { 
          templateId,
          error: error.message
        });
        
        this.dispatchEvent('error', { 
          error: `Failed to fetch template: ${error.message}` 
        });
        
        return null;
      }
    }
    
    /**
     * Save template
     * @param {Object} template - Template to save
     * @returns {Promise<Object>} Saved template
     */
    async saveTemplate(template) {
      this.debug('saveTemplate', 'Saving template', { template });
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const method = template.id ? 'PUT' : 'POST';
        const url = template.id ? 
          `${this.apiUrl}/templates/${template.id}` : 
          `${this.apiUrl}/templates`;
        
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(template)
        });
        
        if (!response.ok) {
          this.error('saveTemplate', 'Failed to save template', { 
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to save template: ${response.status} ${response.statusText}` 
          });
          
          return null;
        }
        
        const savedTemplate = await response.json();
        
        // Invalidate cache to force refresh on next getTemplates call
        this.caches.templates.timestamp = 0;
        
        this.debug('saveTemplate', 'Template saved successfully', { savedTemplate });
        
        // Dispatch event
        this.dispatchEvent('templateSaved', { template: savedTemplate });
        
        // Refresh templates
        await this.getTemplates(true);
        
        return savedTemplate;
      } catch (error) {
        this.error('saveTemplate', 'Error saving template', { error: error.message });
        
        this.dispatchEvent('error', { 
          error: `Failed to save template: ${error.message}` 
        });
        
        return null;
      }
    }
    
    /**
     * Delete template
     * @param {string} templateId - Template ID to delete
     * @returns {Promise<boolean>} Success status
     */
    async deleteTemplate(templateId) {
      this.debug('deleteTemplate', 'Deleting template', { templateId });
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/templates/${templateId}`, {
          method: 'DELETE'
        });
        
        if (!response.ok) {
          this.error('deleteTemplate', 'Failed to delete template', { 
            templateId,
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to delete template: ${response.status} ${response.statusText}` 
          });
          
          return false;
        }
        
        // Invalidate cache to force refresh on next getTemplates call
        this.caches.templates.timestamp = 0;
        
        this.debug('deleteTemplate', 'Template deleted successfully', { templateId });
        
        // Dispatch event
        this.dispatchEvent('templateDeleted', { templateId });
        
        // Refresh templates
        await this.getTemplates(true);
        
        return true;
      } catch (error) {
        this.error('deleteTemplate', 'Error deleting template', { 
          templateId,
          error: error.message
        });
        
        this.dispatchEvent('error', { 
          error: `Failed to delete template: ${error.message}` 
        });
        
        return false;
      }
    }
    
    /**
     * Get conversations
     * @param {boolean} [forceRefresh=false] - Force refresh from server
     * @returns {Promise<Array>} Conversations array
     */
    async getConversations(forceRefresh = false) {
      this.debug('getConversations', 'Getting conversations', { forceRefresh });
      
      // Check cache first
      const cache = this.caches.conversations;
      const now = Date.now();
      
      if (!forceRefresh && cache.timestamp > 0 && now - cache.timestamp < cache.ttl) {
        this.debug('getConversations', 'Using cached conversations', { 
          count: cache.data.length,
          cacheAge: now - cache.timestamp
        });
        return cache.data;
      }
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        this.debug('getConversations', 'Fetching conversations from API');
        const response = await fetch(`${this.apiUrl}/conversations`);
        
        if (!response.ok) {
          this.error('getConversations', 'Failed to fetch conversations', { 
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to fetch conversations: ${response.status} ${response.statusText}` 
          });
          
          return cache.data;
        }
        
        const data = await response.json();
        const conversations = data.conversations || [];
        
        // Update cache
        cache.data = conversations;
        cache.timestamp = now;
        
        // Update state
        this.state.conversations = conversations;
        
        this.debug('getConversations', 'Conversations updated', { count: conversations.length });
        
        // Dispatch event
        this.dispatchEvent('conversationsUpdated', { conversations });
        
        return conversations;
      } catch (error) {
        this.error('getConversations', 'Error fetching conversations', { error: error.message });
        
        this.dispatchEvent('error', { 
          error: `Failed to fetch conversations: ${error.message}` 
        });
        
        return cache.data;
      }
    }
    
    /**
     * Get conversation by ID
     * @param {string} conversationId - Conversation ID
     * @returns {Promise<Object>} Conversation data
     */
    async getConversation(conversationId) {
      this.debug('getConversation', 'Getting conversation', { conversationId });
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/conversations/${conversationId}`);
        
        if (!response.ok) {
          this.error('getConversation', 'Failed to fetch conversation', { 
            conversationId,
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to fetch conversation: ${response.status} ${response.statusText}` 
          });
          
          return null;
        }
        
        const conversation = await response.json();
        
        this.debug('getConversation', 'Conversation retrieved', { conversation });
        
        // Dispatch event
        this.dispatchEvent('conversationLoaded', { conversation });
        
        return conversation;
      } catch (error) {
        this.error('getConversation', 'Error fetching conversation', { 
          conversationId,
          error: error.message
        });
        
        this.dispatchEvent('error', { 
          error: `Failed to fetch conversation: ${error.message}` 
        });
        
        return null;
      }
    }
    
    /**
     * Process writing instruction
     * @param {string} instruction - Writing instruction
     * @returns {Promise<Object>} Response object
     */
    async processWritingInstruction(instruction) {
      this.debug('processWritingInstruction', 'Processing writing instruction', { instruction });
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/writing/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            instruction,
            provider: this.state.selectedProvider,
            model: this.state.selectedModel
          })
        });
        
        if (!response.ok) {
          this.error('processWritingInstruction', 'Failed to process instruction', { 
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to process writing instruction: ${response.status} ${response.statusText}` 
          });
          
          return {
            success: false,
            error: `HTTP Error ${response.status}: ${response.statusText}`,
            content: `<p>Error: Failed to process writing instruction. Server returned status ${response.status}.</p>`
          };
        }
        
        const result = await response.json();
        
        this.debug('processWritingInstruction', 'Instruction processed successfully', { result });
        
        return {
          success: true,
          content: result.content,
          metadata: result.metadata
        };
      } catch (error) {
        this.error('processWritingInstruction', 'Error processing instruction', { error: error.message });
        
        this.dispatchEvent('error', { 
          error: `Failed to process writing instruction: ${error.message}` 
        });
        
        return {
          success: false,
          error: error.message,
          content: `<p>Error: ${error.message}</p>`
        };
      }
    }
    
    /**
     * Send chat message
     * @param {string} message - Message to send
     * @returns {Promise<string>} Response message
     */
    async sendChatMessage(message) {
      this.debug('sendChatMessage', 'Sending chat message', { message });
      
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message,
            provider: this.state.selectedProvider,
            model: this.state.selectedModel
          })
        });
        
        if (!response.ok) {
          this.error('sendChatMessage', 'Failed to send chat message', { 
            status: response.status,
            statusText: response.statusText
          });
          
          this.dispatchEvent('error', { 
            error: `Failed to send chat message: ${response.status} ${response.statusText}` 
          });
          
          return `Error: Failed to send chat message. Server returned status ${response.status}.`;
        }
        
        const result = await response.json();
        
        this.debug('sendChatMessage', 'Chat message sent successfully', { result });
        
        return result.response || 'No response from server';
      } catch (error) {
        this.error('sendChatMessage', 'Error sending chat message', { error: error.message });
        
        this.dispatchEvent('error', { 
          error: `Failed to send chat message: ${error.message}` 
        });
        
        return `Error: ${error.message}`;
      }
    }
    
    /**
     * Select provider and model
     * @param {string} provider - Provider name
     * @param {string} model - Model name
     */
    selectProviderModel(provider, model) {
      this.debug('selectProviderModel', 'Selecting provider and model', { provider, model });
      
      this.state.selectedProvider = provider;
      this.state.selectedModel = model;
      
      // Persist the selection
      this._persistState();
      
      // Dispatch event
      this.dispatchEvent('providerModelSelected', { provider, model });
    }
    
    /**
     * Get current selection
     * @returns {Object} Selected provider and model
     */
    getSelection() {
      return {
        provider: this.state.selectedProvider,
        model: this.state.selectedModel
      };
    }
    
    /**
     * Get current service state
     * @returns {Object} Current state
     */
    getState() {
      return { ...this.state };
    }
    
    /**
     * Add event listener
     * @param {string} event - Event name
     * @param {Function} listener - Event listener function
     */
    addEventListener(event, listener) {
      this.debug('addEventListener', 'Adding event listener', { event });
      
      if (!this.eventListeners[event]) {
        this.eventListeners[event] = [];
      }
      
      this.eventListeners[event].push(listener);
    }
    
    /**
     * Remove event listener
     * @param {string} event - Event name
     * @param {Function} listener - Event listener function to remove
     */
    removeEventListener(event, listener) {
      this.debug('removeEventListener', 'Removing event listener', { event });
      
      if (!this.eventListeners[event]) return;
      
      this.eventListeners[event] = this.eventListeners[event].filter(l => l !== listener);
    }
    
    /**
     * Dispatch event
     * @param {string} event - Event name
     * @param {Object} data - Event data
     */
    dispatchEvent(event, data) {
      this.debug('dispatchEvent', 'Dispatching event', { event, data });
      
      if (!this.eventListeners[event]) return;
      
      // Create custom event
      const customEvent = new CustomEvent(event, { detail: data });
      
      // Call all listeners
      this.eventListeners[event].forEach(listener => {
        try {
          listener(customEvent);
        } catch (error) {
          this.error('dispatchEvent', 'Error in event listener', { 
            event, 
            error: error.message
          });
        }
      });
    }
    
    /**
     * Clean up resources when service is destroyed
     */
    cleanup() {
      this.debug('cleanup', 'Cleaning up service');
      
      // Disconnect WebSocket
      this.disconnectWebSocket();
      
      // Clear event listeners
      for (const event in this.eventListeners) {
        this.eventListeners[event] = [];
      }
      
      // Persist state
      this._persistState();
      
      this.debug('cleanup', 'Service cleaned up');
    }
    
    /**
     * Debug logging with instrumentation
     */
    debug(method, message, data = {}) {
      // Log to debug service if available
      if (this.debugService) {
        this.debugService.debug(DEBUG_NAMESPACE, message, data);
      }
      
      // Log to console in debug mode
      if (this.debugMode) {
        console.debug(`[RHETOR-SERVICE] [${method}] ${message}`, data);
      }
    }
    
    /**
     * Info logging with instrumentation
     */
    info(method, message, data = {}) {
      // Log to debug service if available
      if (this.debugService) {
        this.debugService.info(DEBUG_NAMESPACE, message, data);
      }
      
      // Always log important info
      console.info(`[RHETOR-SERVICE] [${method}] ${message}`, data);
    }
    
    /**
     * Warning logging with instrumentation
     */
    warn(method, message, data = {}) {
      // Log to debug service if available
      if (this.debugService) {
        this.debugService.warn(DEBUG_NAMESPACE, message, data);
      }
      
      // Always log warnings
      console.warn(`[RHETOR-SERVICE] [${method}] ${message}`, data);
    }
    
    /**
     * Error logging with instrumentation
     */
    error(method, message, data = {}) {
      // Log to debug service if available
      if (this.debugService) {
        this.debugService.error(DEBUG_NAMESPACE, message, data);
      }
      
      // Always log errors
      console.error(`[RHETOR-SERVICE] [${method}] ${message}`, data);
    }
  }
  
  /**
   * Initialize the Rhetor service when the page loads
   */
  document.addEventListener('DOMContentLoaded', () => {
    // Check if the debug service is available
    if (window.TektonDebug) {
      window.TektonDebug.info(DEBUG_NAMESPACE, 'DOM loaded, initializing service');
    } else {
      console.info('[RHETOR-SERVICE] DOM loaded, initializing service');
    }
    
    // Create and register the service if not already present
    if (!window.tektonUI?.services?.rhetorService) {
      // Create the tektonUI global namespace if needed
      window.tektonUI = window.tektonUI || {};
      window.tektonUI.services = window.tektonUI.services || {};
      
      // Create the service instance
      const rhetorService = new RhetorService();
      
      // Register the service
      window.tektonUI.services.rhetorService = rhetorService;
      
      if (window.TektonDebug) {
        window.TektonDebug.info(DEBUG_NAMESPACE, 'Service initialized and registered');
      } else {
        console.info('[RHETOR-SERVICE] Service initialized and registered');
      }
    } else {
      if (window.TektonDebug) {
        window.TektonDebug.info(DEBUG_NAMESPACE, 'Service already registered');
      } else {
        console.info('[RHETOR-SERVICE] Service already registered');
      }
    }
  });
  
  // Initialize immediately if the document is already loaded
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    // Check if the debug service is available
    if (window.TektonDebug) {
      window.TektonDebug.info(DEBUG_NAMESPACE, 'Document already loaded, initializing service immediately');
    } else {
      console.info('[RHETOR-SERVICE] Document already loaded, initializing service immediately');
    }
    
    // Create and register the service if not already present
    if (!window.tektonUI?.services?.rhetorService) {
      // Create the tektonUI global namespace if needed
      window.tektonUI = window.tektonUI || {};
      window.tektonUI.services = window.tektonUI.services || {};
      
      // Create the service instance
      const rhetorService = new RhetorService();
      
      // Register the service
      window.tektonUI.services.rhetorService = rhetorService;
      
      if (window.TektonDebug) {
        window.TektonDebug.info(DEBUG_NAMESPACE, 'Service initialized and registered');
      } else {
        console.info('[RHETOR-SERVICE] Service initialized and registered');
      }
    } else {
      if (window.TektonDebug) {
        window.TektonDebug.info(DEBUG_NAMESPACE, 'Service already registered');
      } else {
        console.info('[RHETOR-SERVICE] Service already registered');
      }
    }
  }
})();