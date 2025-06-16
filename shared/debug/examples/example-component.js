/**
 * Ergon Component with Debug Shim Example
 * This file demonstrates how to use the debug shim for instrumenting components
 */

// Example use of debug shim in Ergon component
class ErgonComponentWithDebug {
    constructor() {
        // Log construction with component context
        TektonDebug.debug('ergon', 'Component constructor called');
        
        this.state = {
            initialized: false,
            activeTab: 'agents',
            tabHistory: {},
            modalStates: {
                agentCreation: false,
                agentDetails: false,
                runAgent: false,
                settings: false
            }
        };
        
        this.messageHistory = {
            'ergon': [],
            'awt-team': [],
            'mcp': []
        };
        this.historyPosition = -1;
        this.currentInput = '';
        this.streamHandlersRegistered = false;
    }
    
    /**
     * Initialize the component
     */
    init() {
        // Log initialization
        TektonDebug.info('ergon', 'Initializing Ergon component');
        
        // Log state for debugging
        TektonDebug.trace('ergon', 'Initial state', this.state);
        
        if (this.state.initialized) {
            TektonDebug.debug('ergon', 'Already initialized, just activating');
            this.activateComponent();
            return this;
        }
        
        // Setup component functionality
        this.setupTabs();
        this.setupEventListeners();
        this.setupChatInputs();
        this.loadAgentData();
        
        // Ensure LLM adapter connection is established
        if (window.hermesConnector && !window.hermesConnector.llmConnected) {
            TektonDebug.debug('ergon', 'Initializing connection to LLM adapter');
            window.hermesConnector.connectToLLMAdapter();
        }
        
        // Apply Greek name handling
        this.handleGreekNames();
        
        // Mark as initialized
        this.state.initialized = true;
        TektonDebug.info('ergon', 'Component successfully initialized');
        
        return this;
    }
    
    /**
     * Set up tab switching functionality
     */
    setupTabs() {
        TektonDebug.debug('ergon', 'Setting up Ergon tabs');
        
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            TektonDebug.error('ergon', 'Ergon container not found!');
            return;
        }
        
        // Get tabs within the container
        const tabs = container.querySelectorAll('.ergon__tab');
        TektonDebug.debug('ergon', `Found ${tabs.length} tabs`);
        
        // Add click handlers to tabs
        tabs.forEach(tab => {
            const tabId = tab.getAttribute('data-tab');
            TektonDebug.trace('ergon', `Setting up click handler for tab: ${tabId}`);
            
            tab.addEventListener('click', () => {
                TektonDebug.debug('ergon', `Tab clicked: ${tabId}`);
                this.activateTab(tabId);
            });
        });
        
        // Activate the default tab
        const defaultTab = this.state.activeTab || 'agents';
        TektonDebug.debug('ergon', `Activating default tab: ${defaultTab}`);
        this.activateTab(defaultTab);
    }
    
    /**
     * Activate a specific tab
     * @param {string} tabId - The ID of the tab to activate
     */
    activateTab(tabId) {
        TektonDebug.debug('ergon', `Activating tab: ${tabId}`);
        
        // Find the Ergon container (scope all DOM operations to this container)
        const container = document.querySelector('.ergon');
        if (!container) {
            TektonDebug.error('ergon', 'Ergon container not found!');
            return;
        }
        
        // Update active tab - remove active class from all tabs
        container.querySelectorAll('.ergon__tab').forEach(t => {
            t.classList.remove('ergon__tab--active');
        });
        
        // Add active class to the selected tab
        const tabButton = container.querySelector(`.ergon__tab[data-tab="${tabId}"]`);
        if (tabButton) {
            tabButton.classList.add('ergon__tab--active');
        } else {
            TektonDebug.error('ergon', `Tab button not found for tab: ${tabId}`);
            return; // Exit early if we can't find the tab
        }
        
        // Hide all panels by removing active class
        container.querySelectorAll('.ergon__panel').forEach(panel => {
            panel.classList.remove('ergon__panel--active');
        });
        
        // Show the specific tab panel by adding active class
        const tabPanel = container.querySelector(`#${tabId}-panel`);
        if (tabPanel) {
            tabPanel.classList.add('ergon__panel--active');
        } else {
            TektonDebug.error('ergon', `Panel not found for tab: ${tabId}`);
        }
        
        // Save active tab to state
        this.state.activeTab = tabId;
        
        // Log state change for debugging
        TektonDebug.trace('ergon', 'Updated state after tab activation', { 
            activeTab: this.state.activeTab
        });
    }
    
    // Additional methods would follow the same pattern...
}

// This is just an example file and not meant to replace the actual component
TektonDebug.info('ergon', 'Ergon shim component loaded - this is an example only');