/**
 * Component Template
 * Base template for all Tekton components
 * 
 * Replace 'component' with your component name throughout this file
 */

class ComponentTemplate {
    constructor() {
        this.state = {
            initialized: false,
            activeTab: 'main',
            isLoading: false
        };
    }
    
    /**
     * Initialize the component
     */
    init() {
        console.log('Initializing component');
        
        // If already initialized, just activate
        if (this.state.initialized) {
            console.log('Component already initialized, just activating');
            this.activateComponent();
            return this;
        }
        
        // Find component container
        const container = document.querySelector('.component');
        if (!container) {
            console.error('Component container not found!');
            return this;
        }
        
        // Initialize component functionality
        this.setupTabs();
        this.setupActions();
        
        // Mark as initialized
        this.state.initialized = true;
        
        console.log('Component initialized');
        return this;
    }
    
    /**
     * Activate the component interface
     */
    activateComponent() {
        console.log('Activating component');
        
        // Find component container
        const container = document.querySelector('.component');
        if (container) {
            console.log('Component container found and activated');
        }
    }
    
    /**
     * Set up tab switching functionality
     */
    setupTabs() {
        console.log('Setting up component tabs');
        
        // Find component container
        const container = document.querySelector('.component');
        if (!container) {
            console.error('Component container not found!');
            return;
        }
        
        // Scope all queries to component container
        const tabs = container.querySelectorAll('.component__tab');
        const panels = container.querySelectorAll('.component__panel');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update active tab
                tabs.forEach(t => {
                    t.classList.remove('component__tab--active');
                });
                tab.classList.add('component__tab--active');
                
                // Show active panel
                const panelId = tab.getAttribute('data-tab') + '-panel';
                panels.forEach(panel => {
                    panel.classList.remove('component__panel--active');
                });
                
                // Use container-scoped query
                const activePanel = container.querySelector(`#${panelId}`);
                if (activePanel) {
                    activePanel.classList.add('component__panel--active');
                }
                
                // Update the active tab in state
                this.state.activeTab = tab.getAttribute('data-tab');
                
                // Load tab-specific content if needed
                this.loadTabContent(this.state.activeTab);
            });
        });
    }
    
    /**
     * Set up action buttons
     */
    setupActions() {
        console.log('Setting up component actions');
        
        // Find component container
        const container = document.querySelector('.component');
        if (!container) {
            console.error('Component container not found!');
            return;
        }
        
        // Set up refresh button
        const refreshBtn = container.querySelector('#component-refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshComponent());
        }
    }
    
    /**
     * Load content specific to a tab
     * 
     * @param {string} tabId - The ID of the tab to load content for
     */
    loadTabContent(tabId) {
        console.log(`Loading content for ${tabId} tab`);
        
        // Override this method in your component class
        // to load specific content for each tab
    }
    
    /**
     * Refresh component data
     */
    refreshComponent() {
        console.log('Refreshing component data');
        this.loadTabContent(this.state.activeTab);
    }
    
    /**
     * Clean up any resources used by this component
     */
    cleanup() {
        console.log('Cleaning up component');
        
        // Override this method in your component class
        // to clean up any resources (event listeners, timeouts, etc.)
    }
}

// In your actual component, create a class that extends ComponentTemplate
// and update your component's name and functionality: