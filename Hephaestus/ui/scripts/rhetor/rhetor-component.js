/**
 * Rhetor Component JavaScript
 * Main controller for the Rhetor UI component in Hephaestus
 * Updated to use Component Interface Pattern with enhanced debug instrumentation
 * Part of the Clean Slate Sprint
 */

console.log('[FILE_TRACE] Loading: rhetor-component.js');
// Use IIFE for encapsulation and to prevent global namespace pollution
(function() {
  'use strict';
  
  // Debug namespace
  const DEBUG_NAMESPACE = 'rhetor';
  
  /**
   * Component Interface Pattern - Main Component Object
   * @type {Object}
   */
  const RhetorComponent = {
    // Component state
    state: {
      initialized: false,
      loaded: false,
      activeTab: 'dashboard',
      connected: false,
      provider: null,
      model: null,
      documentCount: 0,
      templateCount: 0,
      chatHistory: [],
      debugMode: false,
      // CI Orchestration state
      specialists: [],
      sessions: [],
      orchestrationMode: 'active',
      autoTranslate: true,
      anthropicMax: false,
      specialistConfigs: {}
    },
    
    // DOM element references
    elements: {
      container: null,
      tabs: null,
      content: null,
      chatInput: null,
      sendButton: null,
      statusIndicator: null,
      statusText: null,
      loadingIndicator: null,
      // CI Orchestration elements
      specialistsGrid: null,
      sessionsList: null,
      orchestrationForm: null,
      configForm: null
    },
    
    // Services
    services: {
      rhetorService: null,
      debug: null
    },
    
    /**
     * Initialize the component
     * Called when the component is loaded
     */
    init: function() {
      this.debug('init', 'Initializing component');
      console.log('[RHETOR] Init called, checking for container');
      
      try {
        // Get component container - try multiple selectors
        this.elements.container = document.getElementById('rhetor-component');
        if (!this.elements.container) {
          this.elements.container = document.querySelector('.rhetor-container');
        }
        if (!this.elements.container) {
          this.elements.container = document.querySelector('.rhetor');
        }
        if (!this.elements.container) {
          this.elements.container = document.querySelector('[data-tekton-component="rhetor"]');
        }
        
        if (!this.elements.container) {
          this.error('init', 'Cannot find component container');
          console.error('[RHETOR] Tried: #rhetor-component, .rhetor-container, .rhetor, [data-tekton-component="rhetor"]');
          return;
        }
        
        // Set UI Manager protection
        this.protectFromUIManager();
        
        // Check if debug is available
        if (window.TektonDebug) {
          this.services.debug = window.TektonDebug;
          this.state.debugMode = true;
          this.debug('init', 'Debug service available');
        }
        
        // Initialize the Rhetor service 
        this.initService();
        
        // Initialize UI elements
        this.initElements();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup HTML panel protection
        this.protectHtmlPanel();
        
        // Load initial content
        this.loadContent();
        
        this.state.initialized = true;
        this.info('init', 'Component initialized successfully');
      } catch (err) {
        this.error('init', 'Failed to initialize component', { error: err.message, stack: err.stack });
      }
    },
    
    /**
     * Initialize DOM element references
     */
    initElements: function() {
      this.debug('initElements', 'Initializing DOM elements');
      
      try {
        // Cache DOM elements by selecting only within component container for isolation
        const container = this.elements.container || document.querySelector('.rhetor');
        this.elements.tabs = container.querySelectorAll('.rhetor__tab');
        this.elements.contents = {};
        this.elements.contents.dashboard = container.querySelector('#dashboard-panel');
        this.elements.contents.models = container.querySelector('#models-panel');
        this.elements.contents.prompts = container.querySelector('#prompts-panel');
        this.elements.contents.contexts = container.querySelector('#contexts-panel');
        this.elements.contents.specialists = container.querySelector('#specialists-panel');
        this.elements.contents.orchestration = container.querySelector('#orchestration-panel');
        this.elements.contents.sessions = container.querySelector('#sessions-panel');
        this.elements.contents.configuration = container.querySelector('#configuration-panel');
        this.elements.contents.llmchat = container.querySelector('#llmchat-panel');
        this.elements.contents.teamchat = container.querySelector('#teamchat-panel');
        this.elements.chatInput = container.querySelector('#chat-input');
        this.elements.sendButton = container.querySelector('#send-button');
        this.elements.statusIndicator = container.querySelector('.rhetor__status-indicator');
        this.elements.statusText = container.querySelector('.rhetor__status-text');
        // CI Orchestration elements
        this.elements.specialistsGrid = container.querySelector('#specialists-grid');
        this.elements.sessionsList = container.querySelector('#sessions-list');
        this.elements.orchestrationForm = container.querySelector('#orchestration-panel');
        this.elements.configForm = container.querySelector('#configuration-panel');
        
        this.debug('initElements', 'DOM elements initialized');
        
        // Load initial content based on active tab
        if (this.state.activeTab === 'dashboard') {
          console.log('[RHETOR] Dashboard using static HTML - no dynamic loading needed');
        } else if (this.state.activeTab === 'specialists') {
          setTimeout(() => this.refreshSpecialists(), 100);
        }
      } catch (err) {
        this.error('initElements', 'Failed to initialize DOM elements', { error: err.message });
      }
    },
    
    /**
     * Initialize Rhetor service
     */
    initService: function() {
      this.debug('initService', 'Initializing Rhetor service');
      
      try {
        // Get service from the global registry if available
        if (window.tektonUI?.services?.rhetorService) {
          this.services.rhetorService = window.tektonUI.services.rhetorService;
          this.info('initService', 'Found existing Rhetor service in registry');
        } else {
          // Try to initialize the service
          this.loadService().then(service => {
            this.services.rhetorService = service;
            this.info('initService', 'Loaded Rhetor service');
            
            // Initialize UI from service state
            this.updateUIFromService();
          }).catch(err => {
            this.error('initService', 'Failed to load Rhetor service', { error: err.message });
          });
        }
      } catch (err) {
        this.error('initService', 'Failed to initialize service', { error: err.message });
      }
    },
    
    /**
     * Load the Rhetor service dynamically
     * @returns {Promise} Promise resolving to service object
     */
    loadService: function() {
      return new Promise((resolve, reject) => {
        try {
          // Load the service script
          const script = document.createElement('script');
          script.src = '/scripts/rhetor/rhetor-service.js';
          script.async = true;
          
          script.onload = () => {
            // Check if the service is now available
            if (window.tektonUI?.services?.rhetorService) {
              this.debug('loadService', 'Service script loaded and service registered');
              resolve(window.tektonUI.services.rhetorService);
            } else {
              this.error('loadService', 'Service script loaded but service not registered');
              reject(new Error('Service not registered after script load'));
            }
          };
          
          script.onerror = () => {
            this.error('loadService', 'Failed to load service script');
            reject(new Error('Failed to load service script'));
          };
          
          document.head.appendChild(script);
          this.debug('loadService', 'Service script loading');
        } catch (err) {
          this.error('loadService', 'Error loading service', { error: err.message });
          reject(err);
        }
      });
    },
    
    /**
     * Update UI from service state
     */
    updateUIFromService: function() {
      if (!this.services.rhetorService) return;
      
      try {
        const state = this.services.rhetorService.getState();
        this.debug('updateUIFromService', 'Got service state', { state });
        
        // Update connection status
        this.updateConnectionStatus(state.connected);
        
        // Update selected provider/model
        if (state.selectedProvider) {
          this.state.provider = state.selectedProvider;
        }
        
        if (state.selectedModel) {
          this.state.model = state.selectedModel;
        }
        
        // Update component state
        this.updateUIState();
      } catch (err) {
        this.error('updateUIFromService', 'Failed to update UI from service', { error: err.message });
      }
    },
    
    /**
     * Setup event listeners for component functionality
     */
    setupEventListeners: function() {
      this.debug('setupEventListeners', 'Setting up event listeners');
      
      try {
        // Setup tab switching
        if (this.elements.tabs) {
          this.elements.tabs.forEach(tab => {
            tab.addEventListener('click', this.handleTabClick.bind(this));
          });
        }
        
        // Setup chat input
        if (this.elements.chatInput && this.elements.sendButton) {
          this.elements.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              this.handleSendMessage();
            }
          });
          
          this.elements.sendButton.addEventListener('click', this.handleSendMessage.bind(this));
        }
        
        // Listen for service events if available
        if (this.services.rhetorService) {
          this.setupServiceEvents();
        }
        
        this.debug('setupEventListeners', 'Event listeners setup complete');
      } catch (err) {
        this.error('setupEventListeners', 'Failed to setup event listeners', { error: err.message });
      }
    },
    
    /**
     * Setup service event listeners
     */
    setupServiceEvents: function() {
      if (!this.services.rhetorService) return;
      
      try {
        this.debug('setupServiceEvents', 'Setting up service event listeners');
        
        const service = this.services.rhetorService;
        
        // Basic connection events
        service.addEventListener('connected', this.handleServiceConnected.bind(this));
        service.addEventListener('connectionFailed', this.handleServiceConnectionFailed.bind(this));
        service.addEventListener('error', this.handleServiceError.bind(this));
        
        // Update events
        service.addEventListener('providersUpdated', this.handleProvidersUpdated.bind(this));
        service.addEventListener('modelsUpdated', this.handleModelsUpdated.bind(this));
        service.addEventListener('settingsUpdated', this.handleSettingsUpdated.bind(this));
        service.addEventListener('budgetUpdated', this.handleBudgetUpdated.bind(this));
        
        // WebSocket events
        service.addEventListener('websocketConnected', this.handleWebSocketConnected.bind(this));
        service.addEventListener('websocketDisconnected', this.handleWebSocketDisconnected.bind(this));
        service.addEventListener('message', this.handleServiceMessage.bind(this));
        
        this.debug('setupServiceEvents', 'Service event listeners setup complete');
      } catch (err) {
        this.error('setupServiceEvents', 'Failed to setup service event listeners', { error: err.message });
      }
    },
    
    /**
     * Handle tab click event
     * @param {Event} e - Click event
     */
    handleTabClick: function(e) {
      try {
        const tab = e.currentTarget;
        const tabId = tab.getAttribute('data-tab');
        
        if (!tabId) return;
        
        this.debug('handleTabClick', 'Tab clicked', { tabId });
        
        // Update active tab state
        this.elements.tabs.forEach(tab => {
          if (tab.getAttribute('data-tab') === tabId) {
            tab.classList.add('rhetor-tabs__button--active');
          } else {
            tab.classList.remove('rhetor-tabs__button--active');
          }
        });
        
        // Show the correct content panel
        Object.keys(this.elements.contents).forEach(contentId => {
          const content = this.elements.contents[contentId];
          if (contentId === tabId) {
            content.classList.add('rhetor-tabs__content--active');
          } else {
            content.classList.remove('rhetor-tabs__content--active');
          }
        });
        
        // Update state
        this.state.activeTab = tabId;
        
        // Update chat input placeholder based on active tab
        this.updateChatPlaceholder(tabId);
        
        // Load tab-specific content
        this.loadTabContent(tabId);
        
        this.debug('handleTabClick', 'Tab switch complete', { activeTab: this.state.activeTab });
      } catch (err) {
        this.error('handleTabClick', 'Failed to handle tab click', { error: err.message });
      }
    },
    
    /**
     * Handle send message event
     */
    handleSendMessage: function() {
      try {
        if (!this.elements.chatInput) return;
        
        const message = this.elements.chatInput.value.trim();
        if (!message) return;
        
        this.debug('handleSendMessage', 'Send message', { message, activeTab: this.state.activeTab });
        
        // Clear input
        this.elements.chatInput.value = '';
        
        // Process message based on active tab
        switch (this.state.activeTab) {
          case 'writing':
            this.processWritingInstruction(message);
            break;
          case 'templates':
            this.processTemplateCommand(message);
            break;
          case 'teamchat':
            this.processTeamChatMessage(message);
            break;
          case 'llmchat':
            this.processLLMChatMessage(message);
            break;
          default:
            this.processCommand(message);
            break;
        }
      } catch (err) {
        this.error('handleSendMessage', 'Failed to handle send message', { error: err.message });
      }
    },
    
    /**
     * Process writing instruction
     * @param {string} instruction - Writing instruction
     */
    processWritingInstruction: function(instruction) {
      this.info('processWritingInstruction', 'Processing writing instruction', { instruction });
      
      // Switch to writing tab if not active
      if (this.state.activeTab !== 'writing') {
        this.switchTab('writing');
      }
      
      if (this.services.rhetorService) {
        // Use the service to process the instruction
        this.services.rhetorService.processWritingInstruction(instruction)
          .then(result => {
            this.debug('processWritingInstruction', 'Instruction processed', { result });
            this.updateWritingPanel(result);
          })
          .catch(err => {
            this.error('processWritingInstruction', 'Failed to process instruction', { error: err.message });
            this.showNotification('Failed to process writing instruction', 'error');
          });
      } else {
        // Fallback for demo mode
        this.updateWritingPanel({
          content: `<p>Based on your instruction: "${instruction}"</p><p>[This is a placeholder response - full functionality requires the Rhetor service]</p>`
        });
      }
    },
    
    /**
     * Process template command
     * @param {string} command - Template command
     */
    processTemplateCommand: function(command) {
      this.info('processTemplateCommand', 'Processing template command', { command });
      
      // TODO: Implement template command processing
      this.showNotification('Template commands are not implemented yet', 'info');
    },
    
    /**
     * Process team chat message
     * @param {string} message - Chat message
     */
    processTeamChatMessage: function(message) {
      this.info('processTeamChatMessage', 'Processing team chat message', { message });
      
      // Add message to chat history
      this.state.chatHistory.push({
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      });
      
      // Get chat container
      const chatContainer = this.container.querySelector('.rhetor__chat-messages');
      if (!chatContainer) {
        this.error('processTeamChatMessage', 'Cannot find chat container');
        return;
      }
      
      // Add message to UI
      const messageElement = document.createElement('div');
      messageElement.className = 'rhetor__message rhetor__message--user';
      messageElement.innerHTML = `
        <div class="rhetor__message-content">
          <div class="rhetor__message-text">${this.escapeHtml(message)}</div>
          <div class="rhetor__message-meta">Just now</div>
        </div>
      `;
      chatContainer.appendChild(messageElement);
      
      // Scroll to bottom
      chatContainer.scrollTop = chatContainer.scrollHeight;
      
      if (this.services.rhetorService) {
        // Use the service to process the message
        this.services.rhetorService.sendChatMessage(message)
          .then(response => {
            this.addResponseToChat(response);
          })
          .catch(err => {
            this.error('processTeamChatMessage', 'Failed to process message', { error: err.message });
            this.showNotification('Failed to send message', 'error');
          });
      } else {
        // Fallback for demo mode
        setTimeout(() => {
          this.addResponseToChat('This is a placeholder response. Connect to the Rhetor service for full functionality.');
        }, 1000);
      }
    },
    
    /**
     * Process LLM chat message
     * @param {string} message - Chat message
     */
    processLLMChatMessage: function(message) {
      console.log('[RHETOR] processLLMChatMessage called with:', message);
      this.info('processLLMChatMessage', 'Processing LLM chat message', { message });
      
      // Update CI ready status
      const llmchatPanel = document.querySelector('[data-tekton-chat="rhetor-llm"]');
      if (llmchatPanel) {
        llmchatPanel.setAttribute('data-tekton-ai-ready', 'true');
      }
      
      // Add message to chat history
      this.state.chatHistory.push({
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      });
      
      // Get chat container for llmchat
      const chatContainer = document.querySelector('#llmchat-messages');
      if (!chatContainer) {
        this.error('processLLMChatMessage', 'Cannot find LLM chat container');
        return;
      }
      
      // Add user message to UI
      const messageElement = document.createElement('div');
      messageElement.className = 'rhetor__message rhetor__message--user';
      messageElement.innerHTML = `
        <div class="rhetor__message-content">
          <div class="rhetor__message-text">${this.escapeHtml(message)}</div>
          <div class="rhetor__message-meta">Just now</div>
        </div>
      `;
      chatContainer.appendChild(messageElement);
      
      // Add typing indicator
      const typingIndicator = document.createElement('div');
      typingIndicator.className = 'rhetor__message rhetor__message--ai rhetor__typing-indicator';
      typingIndicator.innerHTML = `
        <div class="rhetor__message-content">
          <div class="rhetor__message-text">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </div>
        </div>
      `;
      chatContainer.appendChild(typingIndicator);
      
      // Scroll to bottom
      chatContainer.scrollTop = chatContainer.scrollHeight;
      
      // Send message to rhetor-orchestrator specialist
      const specialistId = 'rhetor-orchestrator';
      
      fetch(`/api/v1/ai/specialists/${specialistId}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          context_id: 'rhetor-llm-chat',
          streaming: true,
          options: {
            temperature: 0.7,
            max_tokens: 2000
          }
        })
      })
      .then(response => response.json())
      .then(data => {
        // Remove typing indicator
        if (typingIndicator.parentNode) {
          typingIndicator.parentNode.removeChild(typingIndicator);
        }
        
        // Add CI response
        const aiMessage = document.createElement('div');
        aiMessage.className = 'rhetor__message rhetor__message--ai';
        aiMessage.innerHTML = `
          <div class="rhetor__message-content">
            <div class="rhetor__message-sender">Rhetor Orchestrator</div>
            <div class="rhetor__message-text">${this.escapeHtml(data.response || data.message || 'Message sent successfully')}</div>
            <div class="rhetor__message-meta">Just now</div>
          </div>
        `;
        chatContainer.appendChild(aiMessage);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Save to chat history
        this.state.chatHistory.push({
          role: 'assistant',
          content: data.response || data.message,
          timestamp: new Date().toISOString()
        });
      })
      .catch(err => {
        // Remove typing indicator
        if (typingIndicator.parentNode) {
          typingIndicator.parentNode.removeChild(typingIndicator);
        }
        
        this.error('processLLMChatMessage', 'Failed to send message to AI', { error: err.message });
        
        // Show error message in chat
        const errorMessage = document.createElement('div');
        errorMessage.className = 'rhetor__message rhetor__message--system';
        errorMessage.innerHTML = `
          <div class="rhetor__message-content">
            <div class="rhetor__message-text" style="color: #ff6b6b;">
              Failed to connect to CI specialist. Please ensure the Rhetor service is running.
              <br><small>${err.message}</small>
            </div>
          </div>
        `;
        chatContainer.appendChild(errorMessage);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
      });
    },
    
    /**
     * Load dashboard content
     * REMOVED: Dashboard now uses static HTML instead of dynamic DOM manipulation
     */
    /*
    loadDashboard: async function() {
      this.info('loadDashboard', 'Loading dashboard content');
      console.log('[RHETOR] loadDashboard called');
      
      try {
        // Get dashboard elements
        const componentGrid = document.getElementById('component-status-grid');
        const specialistList = document.getElementById('dashboard-specialist-list');
        const tokenStats = document.getElementById('dashboard-token-stats');
        
        console.log('[RHETOR] Dashboard elements:', {
          componentGrid: !!componentGrid,
          specialistList: !!specialistList,
          tokenStats: !!tokenStats
        });
        
        if (!componentGrid || !specialistList || !tokenStats) {
          this.warn('loadDashboard', 'Dashboard elements not found');
          console.log('[RHETOR] Missing elements:', {
            componentGrid: componentGrid,
            specialistList: specialistList,
            tokenStats: tokenStats
          });
          // Try to populate what we have
        }
        
        // Fetch real data from Rhetor backend
        try {
          // Get available models from Rhetor
          const modelsResponse = await fetch('/api/rhetor/models');
          const modelsData = await modelsResponse.json();
          console.log('[RHETOR] Models data:', modelsData);
          
          // Get CI specialists from Rhetor
          const specialistsResponse = await fetch('/api/rhetor/specialists');
          const specialistsData = await specialistsResponse.json();
          console.log('[RHETOR] Specialists data:', specialistsData);
          
          // Get token usage/budget from Rhetor
          const usageResponse = await fetch('/api/rhetor/usage');
          const usageData = await usageResponse.json();
          console.log('[RHETOR] Usage data:', usageData);
        } catch (apiError) {
          console.error('[RHETOR] Failed to fetch data from backend:', apiError);
          // Fall back to demo data for now
        }
        
        // Populate component status grid
        if (componentGrid) {
          const components = [
            { name: 'Rhetor', status: 'active', metrics: ['42 req/min', '3 AIs active'] },
            { name: 'Hermes', status: 'active', metrics: ['WebSocket', '5 clients'] },
            { name: 'Athena', status: 'active', metrics: ['71 entities', 'Graph OK'] },
            { name: 'Apollo', status: 'active', metrics: ['Executing', '2 tasks'] },
            { name: 'Penia', status: 'active', metrics: ['$0.42/hr', '15% budget'] },
            { name: 'Telos', status: 'active', metrics: ['Planning', '1 session'] },
            { name: 'Prometheus', status: 'active', metrics: ['Strategic', '3 analyses'] },
            { name: 'Engram', status: 'inactive', metrics: ['Memory OFF', 'Loading...'] },
            { name: 'Numa', status: 'active', metrics: ['Reasoning', '5 queries'] },
            { name: 'Hephaestus', status: 'active', metrics: ['UI Active', '2 users'] }
          ];
          
          componentGrid.innerHTML = components.map(comp => `
            <div class="rhetor__component-card" data-component="${comp.name.toLowerCase()}">
              <div class="rhetor__component-header">
                <span class="rhetor__component-name">${comp.name}</span>
                <span class="rhetor__component-status rhetor__component-status--${comp.status}">●</span>
              </div>
              <div class="rhetor__component-metrics">
                ${comp.metrics.map(m => `<div class="rhetor__metric">${m}</div>`).join('')}
              </div>
            </div>
          `).join('');
          console.log('[RHETOR] Component grid populated');
        }
        
        // Populate specialist list
        if (specialistList) {
          const specialists = [
            { name: 'rhetor-orchestrator', model: 'Opus' },
            { name: 'apollo-coordinator', model: 'Sonnet' },
            { name: 'hermes-messenger', model: 'Haiku' },
            { name: 'telos-analyst', model: 'Haiku' },
            { name: 'prometheus-strategist', model: 'Sonnet' },
            { name: 'engram-memory', model: 'Haiku' }
          ];
          
          specialistList.innerHTML = specialists.map(spec => `
          <div class="rhetor__specialist-item">
            <span class="rhetor__specialist-name">${spec.name}</span>
            <span class="rhetor__specialist-model">[${spec.model}]</span>
          </div>
          `).join('');
          console.log('[RHETOR] Specialist list populated');
        }
        
        // Populate token stats
        if (tokenStats) {
          tokenStats.innerHTML = `
          <div class="rhetor__token-total">
            <span class="rhetor__token-label">Total:</span>
            <span class="rhetor__token-value">1.2M tokens</span>
          </div>
          <div class="rhetor__token-cost">
            <span class="rhetor__token-label">Cost:</span>
            <span class="rhetor__token-value">$42.50</span>
          </div>
          <div class="rhetor__token-breakdown">
            <div class="rhetor__token-bar">
              <div class="rhetor__token-segment rhetor__token-segment--opus" style="width: 45%;">
                <span class="rhetor__token-percent">Opus 45%</span>
              </div>
              <div class="rhetor__token-segment rhetor__token-segment--sonnet" style="width: 30%;">
                <span class="rhetor__token-percent">Sonnet 30%</span>
              </div>
              <div class="rhetor__token-segment rhetor__token-segment--haiku" style="width: 25%;">
                <span class="rhetor__token-percent">Haiku 25%</span>
              </div>
            </div>
          </div>
          `;
          console.log('[RHETOR] Token stats populated');
        }
        
        this.info('loadDashboard', 'Dashboard loaded successfully');
      } catch (err) {
        this.error('loadDashboard', 'Failed to load dashboard', { error: err.message });
      }
    },
    */
    
    /**
     * Refresh CI specialists list
     */
    refreshSpecialists: function() {
      this.info('refreshSpecialists', 'Refreshing CI specialists');
      
      if (!this.elements.specialistsGrid) {
        this.error('refreshSpecialists', 'Cannot find specialists grid');
        return;
      }
      
      // Show loading state
      this.elements.specialistsGrid.innerHTML = '<div class="rhetor__loading">Loading CI specialists...</div>';
      
      // Fetch specialists from backend
      fetch('/api/v1/ai/specialists')
        .then(response => response.json())
        .then(data => {
          // Handle both array response (simplified) and object response (old format)
          this.state.specialists = Array.isArray(data) ? data : (data.specialists || []);
          this.renderSpecialists();
        })
        .catch(err => {
          this.error('refreshSpecialists', 'Failed to fetch specialists', { error: err.message });
          this.elements.specialistsGrid.innerHTML = '<div class="rhetor__error">Failed to load specialists</div>';
        });
    },
    
    /**
     * Render CI specialists grid
     */
    renderSpecialists: function() {
      if (!this.elements.specialistsGrid) return;
      
      if (this.state.specialists.length === 0) {
        this.elements.specialistsGrid.innerHTML = '<div class="rhetor__empty-state">No CI specialists available</div>';
        return;
      }
      
      let html = '';
      this.state.specialists.forEach(specialist => {
        const icon = this.getSpecialistIcon(specialist.type);
        const statusClass = specialist.active ? 'rhetor__specialist-status--active' : '';
        const cardClass = specialist.active ? 'rhetor__specialist-card rhetor__specialist-card--active' : 'rhetor__specialist-card';
        
        html += `
          <div class="${cardClass}" data-id="${specialist.id}">
            <div class="rhetor__specialist-status ${statusClass}"></div>
            <div class="rhetor__specialist-header">
              <div class="rhetor__specialist-icon">${icon}</div>
              <div class="rhetor__specialist-info">
                <h3 class="rhetor__specialist-name">${this.escapeHtml(specialist.name)}</h3>
                <div class="rhetor__specialist-type">${this.escapeHtml(specialist.type)}</div>
              </div>
            </div>
            <div class="rhetor__specialist-stats">
              <div class="rhetor__specialist-stat">
                <span class="rhetor__specialist-stat-value">${specialist.messages || 0}</span>
                <span class="rhetor__specialist-stat-label">Messages</span>
              </div>
              <div class="rhetor__specialist-stat">
                <span class="rhetor__specialist-stat-value">${specialist.sessions || 0}</span>
                <span class="rhetor__specialist-stat-label">Sessions</span>
              </div>
            </div>
            <div class="rhetor__specialist-actions">
              ${specialist.active 
                ? '<button class="rhetor__specialist-action" onclick="rhetorComponent.deactivateSpecialist(\'' + specialist.id + '\')">Deactivate</button>'
                : '<button class="rhetor__specialist-action rhetor__specialist-action--primary" onclick="rhetorComponent.activateSpecialist(\'' + specialist.id + '\')">Activate</button>'
              }
              <button class="rhetor__specialist-action" onclick="rhetorComponent.messageSpecialist('${specialist.id}')">Message</button>
            </div>
          </div>
        `;
      });
      
      this.elements.specialistsGrid.innerHTML = html;
    },
    
    /**
     * Get specialist icon based on type
     */
    getSpecialistIcon: function(type) {
      const icons = {
        'orchestrator': '🎯',
        'memory': '🧠',
        'coordinator': '👔',
        'analyst': '📊',
        'strategist': '🎯',
        'messenger': '📨'
      };
      return icons[type] || '🤖';
    },
    
    /**
     * Activate a specialist
     */
    activateSpecialist: function(specialistId) {
      this.info('activateSpecialist', 'Activating specialist', { specialistId });
      
      fetch(`/api/v1/ai/specialists/${specialistId}/hire`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
          this.showNotification(`Activated ${data.name}`, 'success');
          this.refreshSpecialists();
        })
        .catch(err => {
          this.error('activateSpecialist', 'Failed to activate specialist', { error: err.message });
          this.showNotification('Failed to activate specialist', 'error');
        });
    },
    
    /**
     * Deactivate a specialist
     */
    deactivateSpecialist: function(specialistId) {
      this.info('deactivateSpecialist', 'Deactivating specialist', { specialistId });
      
      // TODO: Implement deactivation endpoint
      this.showNotification('Deactivation not yet implemented', 'info');
    },
    
    /**
     * Message a specialist
     */
    messageSpecialist: function(specialistId) {
      this.info('messageSpecialist', 'Opening message dialog', { specialistId });
      
      // Switch to LLM chat tab
      window.rhetor_switchTab('llmchat');
      
      // Set context for specialist
      if (this.elements.chatInput) {
        this.elements.chatInput.placeholder = `Message to specialist ${specialistId}...`;
        this.elements.chatInput.focus();
      }
    },
    
    /**
     * Create new specialist
     */
    createSpecialist: function() {
      this.info('createSpecialist', 'Creating new specialist');
      
      // TODO: Show specialist creation dialog
      this.showNotification('Dynamic specialist creation coming soon', 'info');
    },
    
    /**
     * Save orchestration settings
     */
    saveOrchestration: function() {
      this.info('saveOrchestration', 'Saving orchestration settings');
      
      const settings = {
        mode: document.getElementById('orchestration-mode')?.value || 'active',
        autoTranslate: document.getElementById('auto-translate')?.checked || false,
        filterRedundant: document.getElementById('filter-redundant')?.checked || false,
        filterErrors: document.getElementById('filter-errors')?.checked || false,
        summarizeVerbose: document.getElementById('summarize-verbose')?.checked || false
      };
      
      // TODO: Send to backend
      this.state.orchestrationMode = settings.mode;
      this.state.autoTranslate = settings.autoTranslate;
      
      this.showNotification('Orchestration settings saved', 'success');
    },
    
    /**
     * Refresh active sessions
     */
    refreshSessions: function() {
      this.info('refreshSessions', 'Refreshing active sessions');
      
      if (!this.elements.sessionsList) {
        this.error('refreshSessions', 'Cannot find sessions list');
        return;
      }
      
      // TODO: Fetch from backend
      this.state.sessions = [
        {
          id: 'session-1',
          title: 'Rhetor ↔ Engram Memory Sync',
          participants: ['rhetor-orchestrator', 'engram-memory'],
          messages: 15,
          created: new Date(Date.now() - 3600000).toISOString()
        }
      ];
      
      this.renderSessions();
    },
    
    /**
     * Render active sessions
     */
    renderSessions: function() {
      if (!this.elements.sessionsList) return;
      
      if (this.state.sessions.length === 0) {
        this.elements.sessionsList.innerHTML = '<div class="rhetor__empty-state">No active CI sessions</div>';
        return;
      }
      
      let html = '';
      this.state.sessions.forEach(session => {
        const timeAgo = this.formatTimeAgo(session.created);
        
        html += `
          <div class="rhetor__session-item" data-id="${session.id}">
            <div class="rhetor__session-participants">
              ${session.participants.map(p => `<div class="rhetor__session-participant">${this.getSpecialistIcon(p.split('-')[0])}</div>`).join('')}
            </div>
            <div class="rhetor__session-info">
              <h3 class="rhetor__session-title">${this.escapeHtml(session.title)}</h3>
              <div class="rhetor__session-meta">${session.messages} messages • Started ${timeAgo}</div>
            </div>
            <div class="rhetor__session-actions">
              <button class="rhetor__session-action" onclick="rhetorComponent.viewSession('${session.id}')">View</button>
              <button class="rhetor__session-action" onclick="rhetorComponent.joinSession('${session.id}')">Join</button>
            </div>
          </div>
        `;
      });
      
      this.elements.sessionsList.innerHTML = html;
    },
    
    /**
     * Create new session
     */
    createSession: function() {
      this.info('createSession', 'Creating new CI session');
      
      // TODO: Show session creation dialog
      this.showNotification('Session creation dialog coming soon', 'info');
    },
    
    /**
     * Toggle Anthropic Max
     */
    toggleAnthropicMax: function() {
      const checkbox = document.getElementById('anthropic-max');
      this.state.anthropicMax = checkbox?.checked || false;
      
      this.info('toggleAnthropicMax', 'Toggled Anthropic Max', { enabled: this.state.anthropicMax });
      
      if (this.state.anthropicMax) {
        this.showNotification('Anthropic Max enabled - unlimited tokens for testing', 'success');
      } else {
        this.showNotification('Anthropic Max disabled - normal budget limits apply', 'info');
      }
    },
    
    /**
     * Save CI configuration
     */
    saveConfiguration: function() {
      this.info('saveConfiguration', 'Saving CI configuration');
      
      const config = {
        anthropicMax: this.state.anthropicMax,
        models: {
          orchestrator: document.getElementById('model-orchestrator')?.value,
          memory: document.getElementById('model-memory')?.value,
          coordinator: document.getElementById('model-coordinator')?.value
        }
      };
      
      // TODO: Send to backend
      this.showNotification('Configuration saved', 'success');
    },
    
    /**
     * Format time ago
     */
    formatTimeAgo: function(timestamp) {
      const now = Date.now();
      const then = new Date(timestamp).getTime();
      const diff = now - then;
      
      if (diff < 60000) return 'just now';
      if (diff < 3600000) return Math.floor(diff / 60000) + ' minutes ago';
      if (diff < 86400000) return Math.floor(diff / 3600000) + ' hours ago';
      return Math.floor(diff / 86400000) + ' days ago';
    },
    
    /**
     * Add response to chat
     * @param {string} response - Response message
     */
    addResponseToChat: function(response) {
      this.debug('addResponseToChat', 'Adding response to chat', { response });
      
      // Add to chat history
      this.state.chatHistory.push({
        role: 'assistant',
        content: response,
        timestamp: new Date().toISOString()
      });
      
      // Get chat container
      const chatContainer = this.container.querySelector('.rhetor__chat-messages');
      if (!chatContainer) {
        this.error('addResponseToChat', 'Cannot find chat container');
        return;
      }
      
      // Add message to UI
      const messageElement = document.createElement('div');
      messageElement.className = 'rhetor__message rhetor__message--ai';
      messageElement.innerHTML = `
        <div class="rhetor__message-content">
          <div class="rhetor__message-text">Rhetor: ${this.formatResponseText(response)}</div>
          <div class="rhetor__message-meta">Just now</div>
        </div>
      `;
      chatContainer.appendChild(messageElement);
      
      // Scroll to bottom
      chatContainer.scrollTop = chatContainer.scrollHeight;
    },
    
    /**
     * Format response text with markdown support
     * @param {string} text - Response text
     * @returns {string} Formatted HTML
     */
    formatResponseText: function(text) {
      // Basic markdown formatting
      return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n{2,}/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/^/, '<p>')
        .replace(/$/, '</p>');
    },
    
    /**
     * Process generic command
     * @param {string} command - Command string
     */
    processCommand: function(command) {
      this.info('processCommand', 'Processing command', { command });
      
      if (command.startsWith('/')) {
        const parts = command.slice(1).split(' ');
        const cmd = parts[0].toLowerCase();
        const args = parts.slice(1).join(' ');
        
        switch (cmd) {
          case 'help':
            this.showHelp();
            break;
          case 'clear':
            this.clearActivePanel();
            break;
          case 'debug':
            this.toggleDebugMode();
            break;
          case 'status':
            this.showStatus();
            break;
          default:
            this.showNotification(`Unknown command: ${cmd}`, 'error');
            break;
        }
      } else {
        this.showNotification('Enter a writing instruction or use a slash command like /help', 'info');
      }
    },
    
    /**
     * Update writing panel with content
     * @param {Object} data - Content data
     */
    updateWritingPanel: function(data) {
      this.debug('updateWritingPanel', 'Updating writing panel', { data });
      
      const editor = this.container.querySelector('.rhetor__editor');
      if (!editor) {
        this.error('updateWritingPanel', 'Cannot find editor element');
        return;
      }
      
      if (data.content) {
        editor.innerHTML = data.content;
      }
      
      // Update word and character count
      this.updateDocumentStats();
      
      // Show notification
      this.showNotification('Writing updated', 'success');
    },
    
    /**
     * Update document statistics (word count, etc)
     */
    updateDocumentStats: function() {
      const editor = this.container.querySelector('.rhetor__editor');
      const wordCount = this.container.querySelector('.rhetor__word-count');
      const charCount = this.container.querySelector('.rhetor__char-count');
      
      if (!editor) return;
      
      const text = editor.innerText || '';
      const words = text.trim() ? text.trim().split(/\s+/).length : 0;
      const chars = text.length;
      
      if (wordCount) wordCount.textContent = `Words: ${words}`;
      if (charCount) charCount.textContent = `Characters: ${chars}`;
      
      this.debug('updateDocumentStats', 'Updated document stats', { words, chars });
    },
    
    /**
     * Update chat input placeholder based on active tab
     * @param {string} tabId - Active tab ID
     */
    updateChatPlaceholder: function(tabId) {
      if (!this.elements.chatInput) return;
      
      switch (tabId) {
        case 'specialists':
          this.elements.chatInput.placeholder = 'Enter command for CI specialist management...';
          break;
        case 'orchestration':
          this.elements.chatInput.placeholder = 'Configure orchestration settings...';
          break;
        case 'sessions':
          this.elements.chatInput.placeholder = 'Manage CI session...';
          break;
        case 'configuration':
          this.elements.chatInput.placeholder = 'Update CI configuration...';
          break;
        case 'llmchat':
          this.elements.chatInput.placeholder = 'Chat with Rhetor CI orchestrator...';
          break;
        case 'teamchat':
          this.elements.chatInput.placeholder = 'Type a message to the CI team...';
          break;
        default:
          this.elements.chatInput.placeholder = 'Enter a command or message...';
          break;
      }
    },
    
    /**
     * Load content for a specific tab
     * @param {string} tabId - Tab ID to load content for
     */
    loadTabContent: function(tabId) {
      this.debug('loadTabContent', 'Loading content for tab', { tabId });
      
      // Clear the content area
      if (this.elements.content) {
        this.elements.content.innerHTML = '';
      }
      
      // Show loading indicator
      this.showLoading(true);
      
      // Load tab content based on the tab ID
      switch (tabId) {
        case 'dashboard':
          // Dashboard uses static HTML - no dynamic loading needed
          this.showLoading(false);
          break;
        case 'models':
          // Models panel is static for now
          this.showLoading(false);
          break;
        case 'prompts':
          // Prompts panel is static for now
          this.showLoading(false);
          break;
        case 'contexts':
          // Contexts panel is static for now
          this.showLoading(false);
          break;
        case 'specialists':
          this.refreshSpecialists();
          this.showLoading(false);
          break;
        case 'orchestration':
          // Orchestration settings are static HTML, just hide loading
          this.showLoading(false);
          break;
        case 'sessions':
          this.refreshSessions();
          this.showLoading(false);
          break;
        case 'configuration':
          // Configuration is static HTML, just hide loading
          this.showLoading(false);
          break;
        case 'llmchat':
          this.loadLLMChatTabContent();
          break;
        case 'teamchat':
          this.loadTeamChatTabContent();
          break;
        default:
          this.elements.content.innerHTML = `<div class="rhetor__error">Unknown tab: ${tabId}</div>`;
          this.showLoading(false);
          break;
      }
    },
    
    /**
     * Load writing tab content
     */
    loadWritingTabContent: function() {
      this.debug('loadWritingTabContent', 'Loading writing tab content');
      
      const content = `
        <div class="rhetor__writing-panel">
          <div class="rhetor__toolbar">
            <div class="rhetor__document-controls">
              <button class="rhetor__control-button rhetor__control-button--new">New</button>
              <button class="rhetor__control-button rhetor__control-button--save">Save</button>
              <button class="rhetor__control-button rhetor__control-button--export">Export</button>
            </div>
            <div class="rhetor__document-stats">
              <span class="rhetor__word-count">Words: 0</span>
              <span class="rhetor__char-count">Characters: 0</span>
            </div>
          </div>
          
          <div class="rhetor__editor-container">
            <div class="rhetor__format-toolbar">
              <button class="rhetor__format-button rhetor__format-button--bold" title="Bold">B</button>
              <button class="rhetor__format-button rhetor__format-button--italic" title="Italic">I</button>
              <button class="rhetor__format-button rhetor__format-button--underline" title="Underline">U</button>
              <span class="rhetor__toolbar-divider"></span>
              <select class="rhetor__format-select rhetor__format-select--heading">
                <option value="p">Paragraph</option>
                <option value="h1">Heading 1</option>
                <option value="h2">Heading 2</option>
                <option value="h3">Heading 3</option>
              </select>
            </div>
            <div class="rhetor__editor" contenteditable="true">
              <p>Start typing your document here or enter a writing instruction in the input box below.</p>
            </div>
          </div>
          
          <div class="rhetor__document-footer">
            <div class="rhetor__autosave-status">Last saved: Never</div>
          </div>
        </div>
      `;
      
      this.elements.content.innerHTML = content;
      
      // Setup event listeners for the editor
      this.setupEditorEventListeners();
      
      // Hide loading indicator
      this.showLoading(false);
    },
    
    /**
     * Setup editor event listeners
     */
    setupEditorEventListeners: function() {
      const editor = this.container.querySelector('.rhetor__editor');
      if (!editor) return;
      
      // Update counts on input
      editor.addEventListener('input', () => {
        this.updateDocumentStats();
      });
      
      // Format buttons
      const formatButtons = this.container.querySelectorAll('.rhetor__format-button');
      formatButtons.forEach(button => {
        button.addEventListener('click', () => {
          const command = button.classList.contains('rhetor__format-button--bold') ? 'bold' :
                          button.classList.contains('rhetor__format-button--italic') ? 'italic' :
                          button.classList.contains('rhetor__format-button--underline') ? 'underline' : '';
                          
          if (command) {
            document.execCommand(command, false, null);
            editor.focus();
          }
        });
      });
      
      // Heading selector
      const headingSelect = this.container.querySelector('.rhetor__format-select--heading');
      if (headingSelect) {
        headingSelect.addEventListener('change', () => {
          const tag = headingSelect.value;
          document.execCommand('formatBlock', false, `<${tag}>`);
          editor.focus();
        });
      }
      
      // New document button
      const newButton = this.container.querySelector('.rhetor__control-button--new');
      if (newButton) {
        newButton.addEventListener('click', () => {
          if (confirm('Start a new document? Current content will be lost.')) {
            editor.innerHTML = '<p>Start typing your document here...</p>';
            this.updateDocumentStats();
          }
        });
      }
    },
    
    /**
     * Load templates tab content
     */
    loadTemplatesTabContent: function() {
      this.debug('loadTemplatesTabContent', 'Loading templates tab content');
      
      const content = `
        <div class="rhetor__templates-panel">
          <div class="rhetor__templates-toolbar">
            <div class="rhetor__templates-search">
              <input type="text" class="rhetor__search-input" placeholder="Search templates...">
            </div>
            <div class="rhetor__templates-actions">
              <button class="rhetor__template-button rhetor__template-button--new">New Template</button>
            </div>
          </div>
          
          <div class="rhetor__templates-container">
            <div class="rhetor__templates-sidebar">
              <h3 class="rhetor__sidebar-heading">Categories</h3>
              <ul class="rhetor__category-list">
                <li class="rhetor__category-item rhetor__category-item--active" data-category="all">All Templates</li>
                <li class="rhetor__category-item" data-category="business">Business</li>
                <li class="rhetor__category-item" data-category="academic">Academic</li>
                <li class="rhetor__category-item" data-category="creative">Creative</li>
                <li class="rhetor__category-item" data-category="custom">Custom</li>
              </ul>
            </div>
            
            <div class="rhetor__templates-grid">
              <div class="rhetor__templates-loading">Loading templates...</div>
            </div>
          </div>
        </div>
      `;
      
      this.elements.content.innerHTML = content;
      
      // Get templates if service is available
      if (this.services.rhetorService) {
        this.services.rhetorService.getTemplates().then(templates => {
          this.updateTemplatesGrid(templates);
        }).catch(err => {
          this.error('loadTemplatesTabContent', 'Failed to load templates', { error: err.message });
          this.container.querySelector('.rhetor__templates-grid').innerHTML = 
            '<div class="rhetor__error">Failed to load templates. Check console for details.</div>';
        });
      } else {
        // Placeholder for demo
        this.updateTemplatesGrid([
          { id: '1', name: 'Business Proposal', category: 'business', description: 'Template for creating business proposals' },
          { id: '2', name: 'Academic Paper', category: 'academic', description: 'Format for academic research papers' },
          { id: '3', name: 'Creative Story', category: 'creative', description: 'Structure for creative storytelling' }
        ]);
      }
      
      // Setup event listeners for templates
      this.setupTemplatesEventListeners();
      
      // Hide loading indicator
      this.showLoading(false);
    },
    
    /**
     * Update templates grid with data
     * @param {Array} templates - Array of template objects
     */
    updateTemplatesGrid: function(templates) {
      this.debug('updateTemplatesGrid', 'Updating templates grid', { count: templates.length });
      
      const grid = this.container.querySelector('.rhetor__templates-grid');
      if (!grid) return;
      
      if (!templates || templates.length === 0) {
        grid.innerHTML = '<div class="rhetor__empty-state">No templates available. Create a new template to get started.</div>';
        return;
      }
      
      let html = '';
      templates.forEach(template => {
        html += `
          <div class="rhetor__template-card" data-id="${template.id}" data-category="${template.category}">
            <div class="rhetor__template-icon">${this.getTemplateIcon(template.category)}</div>
            <div class="rhetor__template-info">
              <h3 class="rhetor__template-name">${this.escapeHtml(template.name)}</h3>
              <div class="rhetor__template-category">${this.escapeHtml(template.category)}</div>
              <p class="rhetor__template-description">${this.escapeHtml(template.description)}</p>
            </div>
            <div class="rhetor__template-actions">
              <button class="rhetor__template-action rhetor__template-action--use">Use</button>
              <button class="rhetor__template-action rhetor__template-action--edit">Edit</button>
            </div>
          </div>
        `;
      });
      
      grid.innerHTML = html;
      
      // Update template count in state
      this.state.templateCount = templates.length;
    },
    
    /**
     * Get template icon based on category
     * @param {string} category - Template category
     * @returns {string} Icon HTML
     */
    getTemplateIcon: function(category) {
      switch (category.toLowerCase()) {
        case 'business':
          return '📊';
        case 'academic':
          return '📚';
        case 'creative':
          return '✨';
        case 'custom':
          return '🔧';
        default:
          return '📄';
      }
    },
    
    /**
     * Setup templates event listeners
     */
    setupTemplatesEventListeners: function() {
      // Category filter
      const categories = this.container.querySelectorAll('.rhetor__category-item');
      categories.forEach(category => {
        category.addEventListener('click', () => {
          const categoryId = category.getAttribute('data-category');
          
          // Update active category
          categories.forEach(c => c.classList.remove('rhetor__category-item--active'));
          category.classList.add('rhetor__category-item--active');
          
          // Filter templates
          this.filterTemplates(categoryId);
        });
      });
      
      // Search input
      const searchInput = this.container.querySelector('.rhetor__search-input');
      if (searchInput) {
        searchInput.addEventListener('input', () => {
          const searchTerm = searchInput.value.trim().toLowerCase();
          this.searchTemplates(searchTerm);
        });
      }
    },
    
    /**
     * Filter templates by category
     * @param {string} category - Category to filter by
     */
    filterTemplates: function(category) {
      this.debug('filterTemplates', 'Filtering templates by category', { category });
      
      const templateCards = this.container.querySelectorAll('.rhetor__template-card');
      templateCards.forEach(card => {
        const cardCategory = card.getAttribute('data-category');
        if (category === 'all' || cardCategory === category) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    },
    
    /**
     * Search templates by term
     * @param {string} term - Search term
     */
    searchTemplates: function(term) {
      this.debug('searchTemplates', 'Searching templates', { term });
      
      const templateCards = this.container.querySelectorAll('.rhetor__template-card');
      templateCards.forEach(card => {
        const name = card.querySelector('.rhetor__template-name').textContent.toLowerCase();
        const description = card.querySelector('.rhetor__template-description').textContent.toLowerCase();
        
        if (name.includes(term) || description.includes(term)) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    },
    
    /**
     * Load revision tab content
     */
    loadRevisionTabContent: function() {
      this.debug('loadRevisionTabContent', 'Loading revision tab content');
      
      const content = `
        <div class="rhetor__revision-panel">
          <div class="rhetor__revision-header">
            <h3 class="rhetor__panel-title">Document History</h3>
            <select class="rhetor__document-select">
              <option value="current">Current Document</option>
            </select>
          </div>
          
          <div class="rhetor__revision-timeline">
            <div class="rhetor__timeline-empty">No revision history available for this document.</div>
          </div>
          
          <div class="rhetor__revision-diff">
            <div class="rhetor__diff-header">
              <h4 class="rhetor__diff-title">Document Changes</h4>
            </div>
            <div class="rhetor__diff-content"></div>
          </div>
        </div>
      `;
      
      this.elements.content.innerHTML = content;
      
      // TODO: Implement revision history functionality
      
      // Hide loading indicator
      this.showLoading(false);
    },
    
    /**
     * Load format tab content
     */
    loadFormatTabContent: function() {
      this.debug('loadFormatTabContent', 'Loading format tab content');
      
      const content = `
        <div class="rhetor__format-panel">
          <div class="rhetor__format-sections">
            <div class="rhetor__format-section">
              <h3 class="rhetor__section-title">Text Formatting</h3>
              <div class="rhetor__format-controls">
                <div class="rhetor__format-control">
                  <label class="rhetor__format-label">Font Family</label>
                  <select class="rhetor__format-select" data-format="font-family">
                    <option value="default">Default</option>
                    <option value="serif">Serif</option>
                    <option value="sans-serif">Sans Serif</option>
                    <option value="monospace">Monospace</option>
                  </select>
                </div>
                
                <div class="rhetor__format-control">
                  <label class="rhetor__format-label">Font Size</label>
                  <select class="rhetor__format-select" data-format="font-size">
                    <option value="small">Small</option>
                    <option value="medium" selected>Medium</option>
                    <option value="large">Large</option>
                    <option value="xlarge">Extra Large</option>
                  </select>
                </div>
                
                <div class="rhetor__format-control">
                  <label class="rhetor__format-label">Text Alignment</label>
                  <div class="rhetor__button-group">
                    <button class="rhetor__format-btn" data-align="left">Left</button>
                    <button class="rhetor__format-btn" data-align="center">Center</button>
                    <button class="rhetor__format-btn" data-align="right">Right</button>
                    <button class="rhetor__format-btn" data-align="justify">Justify</button>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="rhetor__format-section">
              <h3 class="rhetor__section-title">Document Format</h3>
              <div class="rhetor__format-controls">
                <div class="rhetor__format-control">
                  <label class="rhetor__format-label">Paper Size</label>
                  <select class="rhetor__format-select" data-format="paper-size">
                    <option value="letter" selected>Letter (8.5" x 11")</option>
                    <option value="a4">A4 (210 x 297mm)</option>
                    <option value="legal">Legal (8.5" x 14")</option>
                  </select>
                </div>
                
                <div class="rhetor__format-control">
                  <label class="rhetor__format-label">Margins</label>
                  <select class="rhetor__format-select" data-format="margins">
                    <option value="normal" selected>Normal (1")</option>
                    <option value="narrow">Narrow (0.5")</option>
                    <option value="wide">Wide (1.5")</option>
                  </select>
                </div>
                
                <div class="rhetor__format-control">
                  <label class="rhetor__format-label">Line Spacing</label>
                  <select class="rhetor__format-select" data-format="line-spacing">
                    <option value="single">Single</option>
                    <option value="1.15" selected>1.15</option>
                    <option value="1.5">1.5</option>
                    <option value="double">Double</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div class="rhetor__format-section">
              <h3 class="rhetor__section-title">Export Options</h3>
              <div class="rhetor__format-controls">
                <div class="rhetor__format-control">
                  <label class="rhetor__format-label">Format</label>
                  <select class="rhetor__format-select" data-format="export-format">
                    <option value="docx">Microsoft Word (.docx)</option>
                    <option value="pdf">PDF Document (.pdf)</option>
                    <option value="html">HTML Document (.html)</option>
                    <option value="txt">Plain Text (.txt)</option>
                    <option value="md">Markdown (.md)</option>
                  </select>
                </div>
                
                <div class="rhetor__format-control">
                  <label class="rhetor__format-label">Include Metadata</label>
                  <div class="rhetor__checkbox-group">
                    <label class="rhetor__checkbox">
                      <input type="checkbox" checked> Author Information
                    </label>
                    <label class="rhetor__checkbox">
                      <input type="checkbox" checked> Creation Date
                    </label>
                    <label class="rhetor__checkbox">
                      <input type="checkbox"> Revision History
                    </label>
                  </div>
                </div>
                
                <div class="rhetor__format-actions">
                  <button class="rhetor__primary-button">Export Document</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
      
      this.elements.content.innerHTML = content;
      
      // TODO: Implement format functionality
      
      // Hide loading indicator
      this.showLoading(false);
    },
    
    /**
     * Load LLM chat tab content
     */
    loadLLMChatTabContent: function() {
      this.debug('loadLLMChatTabContent', 'Loading LLM chat tab content');
      
      // LLM chat content is already in the HTML, just hide loading
      this.showLoading(false);
    },
    
    /**
     * Load team chat tab content
     */
    loadTeamChatTabContent: function() {
      this.debug('loadTeamChatTabContent', 'Loading team chat tab content');
      
      // Team chat content is already in the HTML, just hide loading
      this.showLoading(false);
    },
    
    /**
     * Switch to a specific tab
     * @param {string} tabId - Tab ID to switch to
     */
    switchTab: function(tabId) {
      this.debug('switchTab', 'Switching to tab', { tabId });
      
      // Find tab button and trigger click event
      const tabButton = this.container.querySelector(`.rhetor__tab-button[data-tab="${tabId}"]`);
      if (tabButton) {
        tabButton.click();
      } else {
        this.error('switchTab', 'Cannot find tab button', { tabId });
      }
    },
    
    /**
     * Load initial content
     */
    loadContent: function() {
      this.debug('loadContent', 'Loading initial content');
      
      // Show the active tab content
      const tabId = this.state.activeTab;
      
      // Update active tab state in the UI
      this.elements.tabs.forEach(tab => {
        if (tab.getAttribute('data-tab') === tabId) {
          tab.classList.add('rhetor-tabs__button--active');
        } else {
          tab.classList.remove('rhetor-tabs__button--active');
        }
      });
      
      // Show the correct content panel
      Object.keys(this.elements.contents).forEach(contentId => {
        const content = this.elements.contents[contentId];
        if (contentId === tabId) {
          content.classList.add('rhetor-tabs__content--active');
        } else {
          content.classList.remove('rhetor-tabs__content--active');
        }
      });
      
      // Update chat input placeholder
      this.updateChatPlaceholder(tabId);
    },
    
    /**
     * Show/hide loading indicator
     * @param {boolean} show - Whether to show loading indicator
     */
    showLoading: function(show) {
      if (!this.elements.loadingIndicator) return;
      
      this.elements.loadingIndicator.style.display = show ? 'flex' : 'none';
    },
    
    /**
     * Show notification message
     * @param {string} message - Message to show
     * @param {string} type - Notification type (info, success, error)
     */
    showNotification: function(message, type = 'info') {
      this.debug('showNotification', 'Showing notification', { message, type });
      
      // Create notification element
      const notification = document.createElement('div');
      notification.className = `rhetor__notification rhetor__notification--${type}`;
      notification.textContent = message;
      
      // Style the notification
      notification.style.position = 'fixed';
      notification.style.bottom = '20px';
      notification.style.right = '20px';
      notification.style.padding = '10px 20px';
      notification.style.borderRadius = '4px';
      notification.style.zIndex = '10000';
      
      // Set colors based on type
      switch (type) {
        case 'success':
          notification.style.backgroundColor = '#28a745';
          notification.style.color = 'white';
          break;
        case 'error':
          notification.style.backgroundColor = '#dc3545';
          notification.style.color = 'white';
          break;
        default:
          notification.style.backgroundColor = '#007bff';
          notification.style.color = 'white';
          break;
      }
      
      // Add to document body
      document.body.appendChild(notification);
      
      // Remove after 3 seconds
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 3000);
    },
    
    /**
     * Show help information
     */
    showHelp: function() {
      const helpContent = `
        <div class="rhetor__message rhetor__message--system">
          <div class="rhetor__message-content">
            <div class="rhetor__message-text">
              <h3>Rhetor Help</h3>
              <p><strong>Available Commands:</strong></p>
              <ul>
                <li><code>/help</code> - Show this help message</li>
                <li><code>/clear</code> - Clear the current panel</li>
                <li><code>/debug</code> - Toggle debug mode</li>
                <li><code>/status</code> - Show component status</li>
              </ul>
              <p><strong>Writing Instructions:</strong></p>
              <p>Simply type your writing instructions in the input box and press Enter. Rhetor will process your request and generate content.</p>
            </div>
          </div>
        </div>
      `;
      
      // Find appropriate container based on active tab
      let container;
      if (this.state.activeTab === 'team-chat') {
        container = this.container.querySelector('.rhetor__chat-messages');
      } else {
        // Switch to team chat tab to show help
        this.switchTab('team-chat');
        container = this.container.querySelector('.rhetor__chat-messages');
      }
      
      if (container) {
        // Add help message to the container
        container.innerHTML += helpContent;
        
        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
      } else {
        // Fallback to notification
        this.showNotification('Help content not available. Make sure the component is fully loaded.', 'error');
      }
    },
    
    /**
     * Show component status
     */
    showStatus: function() {
      const status = {
        initialized: this.state.initialized,
        activeTab: this.state.activeTab,
        connected: this.state.connected,
        provider: this.state.provider || 'none',
        model: this.state.model || 'none',
        documentCount: this.state.documentCount,
        templateCount: this.state.templateCount,
        debugMode: this.state.debugMode
      };
      
      const statusContent = `
        <div class="rhetor__message rhetor__message--system">
          <div class="rhetor__message-content">
            <div class="rhetor__message-text">
              <h3>Rhetor Status</h3>
              <pre>${JSON.stringify(status, null, 2)}</pre>
            </div>
          </div>
        </div>
      `;
      
      // Find appropriate container based on active tab
      let container;
      if (this.state.activeTab === 'team-chat') {
        container = this.container.querySelector('.rhetor__chat-messages');
      } else {
        // Switch to team chat tab to show status
        this.switchTab('team-chat');
        container = this.container.querySelector('.rhetor__chat-messages');
      }
      
      if (container) {
        // Add status message to the container
        container.innerHTML += statusContent;
        
        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
      } else {
        // Fallback to notification
        this.showNotification('Status not available. Make sure the component is fully loaded.', 'error');
      }
    },
    
    /**
     * Clear the active panel
     */
    clearActivePanel: function() {
      this.debug('clearActivePanel', 'Clearing active panel', { activeTab: this.state.activeTab });
      
      switch (this.state.activeTab) {
        case 'writing':
          const editor = this.container.querySelector('.rhetor__editor');
          if (editor) {
            editor.innerHTML = '<p>Start typing your document here...</p>';
            this.updateDocumentStats();
          }
          break;
        case 'team-chat':
          const chatContainer = this.container.querySelector('.rhetor__chat-messages');
          if (chatContainer) {
            // Keep welcome message
            const welcomeMsg = chatContainer.querySelector('.rhetor__message--system');
            chatContainer.innerHTML = '';
            if (welcomeMsg) {
              chatContainer.appendChild(welcomeMsg);
            }
            
            // Clear chat history
            this.state.chatHistory = [];
          }
          break;
      }
      
      this.showNotification(`Cleared ${this.state.activeTab} panel`, 'success');
    },
    
    /**
     * Toggle debug mode
     */
    toggleDebugMode: function() {
      this.state.debugMode = !this.state.debugMode;
      
      this.debug('toggleDebugMode', 'Debug mode toggled', { debugMode: this.state.debugMode });
      
      this.showNotification(`Debug mode ${this.state.debugMode ? 'enabled' : 'disabled'}`, 'info');
    },
    
    /**
     * Handle service connected event
     */
    handleServiceConnected: function(event) {
      this.debug('handleServiceConnected', 'Service connected', { event });
      
      this.state.connected = true;
      this.updateConnectionStatus(true);
      
      // Initialize UI from current state
      this.updateUIFromService();
      
      this.showNotification('Connected to Rhetor service', 'success');
    },
    
    /**
     * Handle service connection failed event
     */
    handleServiceConnectionFailed: function(event) {
      this.error('handleServiceConnectionFailed', 'Service connection failed', { 
        event, 
        error: event.detail?.error 
      });
      
      this.state.connected = false;
      this.updateConnectionStatus(false);
      
      this.showNotification(`Failed to connect to Rhetor service: ${event.detail?.error || 'Unknown error'}`, 'error');
    },
    
    /**
     * Handle service error event
     */
    handleServiceError: function(event) {
      this.error('handleServiceError', 'Service error', { 
        event, 
        error: event.detail?.error 
      });
      
      this.showNotification(`Rhetor service error: ${event.detail?.error || 'Unknown error'}`, 'error');
    },
    
    /**
     * Handle providers updated event from service
     */
    handleProvidersUpdated: function(event) {
      this.debug('handleProvidersUpdated', 'Providers updated', { providers: event.detail?.providers });
      
      // TODO: Update providers UI
    },
    
    /**
     * Handle models updated event from service
     */
    handleModelsUpdated: function(event) {
      this.debug('handleModelsUpdated', 'Models updated', { 
        provider: event.detail?.provider,
        models: event.detail?.models 
      });
      
      // TODO: Update models UI
    },
    
    /**
     * Handle settings updated event from service
     */
    handleSettingsUpdated: function(event) {
      this.debug('handleSettingsUpdated', 'Settings updated', { settings: event.detail?.settings });
      
      // TODO: Update settings UI
    },
    
    /**
     * Handle budget updated event from service
     */
    handleBudgetUpdated: function(event) {
      this.debug('handleBudgetUpdated', 'Budget updated', { budget: event.detail?.budget });
      
      // TODO: Update budget UI
    },
    
    /**
     * Handle WebSocket connected event from service
     */
    handleWebSocketConnected: function(event) {
      this.debug('handleWebSocketConnected', 'WebSocket connected');
      
      // Update UI if needed
    },
    
    /**
     * Handle WebSocket disconnected event from service
     */
    handleWebSocketDisconnected: function(event) {
      this.debug('handleWebSocketDisconnected', 'WebSocket disconnected');
      
      // Update UI if needed
    },
    
    /**
     * Handle service message event
     */
    handleServiceMessage: function(event) {
      this.debug('handleServiceMessage', 'Message from service', { message: event.detail });
      
      // Process message based on type
      if (event.detail.type === 'TYPING') {
        // Show typing indicator in chat
        // TODO: Implement typing indicator
      } else {
        // Handle other message types
      }
    },
    
    /**
     * Update connection status UI
     * @param {boolean} connected - Connection status
     */
    updateConnectionStatus: function(connected) {
      this.debug('updateConnectionStatus', 'Updating connection status', { connected });
      
      this.state.connected = connected;
      
      if (this.elements.statusIndicator) {
        this.elements.statusIndicator.classList.toggle('rhetor__status-indicator--connected', connected);
        this.elements.statusIndicator.classList.toggle('rhetor__status-indicator--disconnected', !connected);
      }
      
      if (this.elements.statusText) {
        this.elements.statusText.textContent = connected ? 'Connected' : 'Disconnected';
        this.elements.statusText.classList.toggle('rhetor__status-text--connected', connected);
        this.elements.statusText.classList.toggle('rhetor__status-text--disconnected', !connected);
      }
    },
    
    /**
     * Update UI state
     * This updates the UI to reflect the current state
     */
    updateUIState: function() {
      this.debug('updateUIState', 'Updating UI state');
      
      // Update connection status
      this.updateConnectionStatus(this.state.connected);
      
      // TODO: Update other UI elements based on state
    },
    
    /**
     * Protect the component from UI Manager interference
     */
    protectFromUIManager: function() {
      this.debug('protectFromUIManager', 'Setting up UI Manager protection');
      
      // Tell UI Manager to ignore this component
      if (window.uiManager) {
        window.uiManager._ignoreComponent = 'rhetor';
        this.debug('protectFromUIManager', 'Set UI Manager to ignore component');
      }
    },
    
    /**
     * Protect HTML panel from being hidden
     */
    protectHtmlPanel: function() {
      this.debug('protectHtmlPanel', 'Setting up HTML panel protection');
      
      try {
        const htmlPanel = document.getElementById('html-panel');
        if (!htmlPanel) {
          this.warn('protectHtmlPanel', 'Cannot find HTML panel to protect');
          return;
        }
        
        // Force HTML panel to be visible
        htmlPanel.style.display = 'block';
        
        // Store the original display value
        if (!htmlPanel.hasOwnProperty('_rhetorOriginalDisplay')) {
          Object.defineProperty(htmlPanel, '_rhetorOriginalDisplay', {
            value: 'block',
            writable: true,
            configurable: true
          });
        }
        
        // Only define the getter/setter if it hasn't already been defined by this component
        if (!htmlPanel.style._rhetorProtected) {
          // Mark the display property as protected by this component
          Object.defineProperty(htmlPanel.style, '_rhetorProtected', {
            value: true,
            writable: false,
            configurable: true
          });
          
          // Protect the display property
          const originalDescriptor = Object.getOwnPropertyDescriptor(HTMLElement.prototype.style, 'display');
          
          Object.defineProperty(htmlPanel.style, 'display', {
            get: function() { 
              return htmlPanel._rhetorOriginalDisplay; 
            },
            set: function(value) {
              if (value === 'none') {
                this.debug('protectHtmlPanel', 'Blocked attempt to hide HTML panel');
                htmlPanel._rhetorOriginalDisplay = 'block';
              } else {
                htmlPanel._rhetorOriginalDisplay = value;
              }
            }.bind(this),
            configurable: true
          });
          
          this.debug('protectHtmlPanel', 'HTML panel protected from being hidden');
        }
      } catch (err) {
        this.error('protectHtmlPanel', 'Failed to protect HTML panel', { error: err.message });
      }
    },
    
    /**
     * Escape HTML to prevent XSS
     * @param {string} html - HTML string to escape
     * @returns {string} Escaped HTML
     */
    escapeHtml: function(html) {
      if (!html) return '';
      
      const div = document.createElement('div');
      div.textContent = html;
      return div.innerHTML;
    },
    
    /**
     * Get component container element
     * @returns {HTMLElement} Component container
     */
    get container() {
      return this.elements.container;
    },
    
    /**
     * Destroy the component and clean up resources
     */
    destroy: function() {
      this.debug('destroy', 'Destroying component');
      
      try {
        // Clean up service event listeners
        if (this.services.rhetorService) {
          const service = this.services.rhetorService;
          
          // Remove all event listeners
          service.removeEventListener('connected', this.handleServiceConnected.bind(this));
          service.removeEventListener('connectionFailed', this.handleServiceConnectionFailed.bind(this));
          service.removeEventListener('error', this.handleServiceError.bind(this));
          service.removeEventListener('providersUpdated', this.handleProvidersUpdated.bind(this));
          service.removeEventListener('modelsUpdated', this.handleModelsUpdated.bind(this));
          service.removeEventListener('settingsUpdated', this.handleSettingsUpdated.bind(this));
          service.removeEventListener('budgetUpdated', this.handleBudgetUpdated.bind(this));
          service.removeEventListener('websocketConnected', this.handleWebSocketConnected.bind(this));
          service.removeEventListener('websocketDisconnected', this.handleWebSocketDisconnected.bind(this));
          service.removeEventListener('message', this.handleServiceMessage.bind(this));
        }
        
        this.debug('destroy', 'Component destroyed successfully');
      } catch (err) {
        this.error('destroy', 'Failed to destroy component', { error: err.message });
      }
    },
    
    /**
     * Debug logging with instrumentation
     */
    debug: function(method, message, data = {}) {
      // Log to debug service if available
      if (this.services.debug) {
        this.services.debug.debug(DEBUG_NAMESPACE, message, data);
      }
      
      // Always log to console in debug mode
      if (this.state.debugMode) {
        console.debug(`[RHETOR] [${method}] ${message}`, data);
      }
    },
    
    /**
     * Info logging with instrumentation
     */
    info: function(method, message, data = {}) {
      // Log to debug service if available
      if (this.services.debug) {
        this.services.debug.info(DEBUG_NAMESPACE, message, data);
      }
      
      // Always log important info to console
      console.info(`[RHETOR] [${method}] ${message}`, data);
    },
    
    /**
     * Warning logging with instrumentation
     */
    warn: function(method, message, data = {}) {
      // Log to debug service if available
      if (this.services.debug) {
        this.services.debug.warn(DEBUG_NAMESPACE, message, data);
      }
      
      // Always log warnings to console
      console.warn(`[RHETOR] [${method}] ${message}`, data);
    },
    
    /**
     * Error logging with instrumentation
     */
    error: function(method, message, data = {}) {
      // Log to debug service if available
      if (this.services.debug) {
        this.services.debug.error(DEBUG_NAMESPACE, message, data);
      }
      
      // Always log errors to console
      console.error(`[RHETOR] [${method}] ${message}`, data);
    }
  };
  
  /**
   * Initialize the Rhetor component when loaded
   */
  document.addEventListener('DOMContentLoaded', function() {
    if (window.TektonDebug) {
      window.TektonDebug.info(DEBUG_NAMESPACE, 'DOM content loaded, initializing component');
    }
    
    // Register the component to the global namespace for API access
    window.rhetorComponent = RhetorComponent;
    
    // Initialize the component
    RhetorComponent.init();
  });
  
  // Initialize immediately if the document is already loaded
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    if (window.TektonDebug) {
      window.TektonDebug.info(DEBUG_NAMESPACE, 'Document already loaded, initializing component immediately');
    }
    
    // Register the component to the global namespace for API access
    window.rhetorComponent = RhetorComponent;
    
    // Initialize the component
    RhetorComponent.init();
  }
  
  // Also expose for debugging
  window.RhetorComponent = RhetorComponent;
})();