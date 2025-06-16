/**
 * Tab Navigation Helper
 * 
 * Standardized, component-scoped tab switching system that works across 
 * all components with proper BEM class scoping.
 * 
 * This avoids global namespace pollution and timing issues by providing:
 * - Self-contained tab management within components
 * - Consistent behavior across all components
 * - No global variables or setTimeout hacks
 * - Uses ComponentUtils.tabs under the hood for reliability
 */

class TabNavigationHelper {
    /**
     * Initialize tab navigation for a component
     * 
     * @param {Object} options - Configuration options
     * @param {string} options.componentName - The component name (e.g., 'ergon', 'athena')
     * @param {string} options.containerSelector - CSS selector for the component container
     * @param {string} options.tabSelector - CSS selector for tab elements within the container
     * @param {string} options.panelSelector - CSS selector for panel elements within the container
     * @param {string} options.activeTabClass - CSS class for active tabs
     * @param {string} options.activePanelClass - CSS class for active panels
     * @param {string} options.defaultTab - Default tab ID to show initially
     * @param {Function} options.onTabChange - Callback when tab changes (optional)
     */
    constructor(options) {
        this.options = Object.assign({
            componentName: '',
            containerSelector: '',
            tabSelector: '.tab',
            panelSelector: '.panel',
            activeTabClass: 'active',
            activePanelClass: 'active',
            defaultTab: '',
            onTabChange: null
        }, options);

        // Check required options
        if (!this.options.componentName || !this.options.containerSelector) {
            console.error('TabNavigationHelper: componentName and containerSelector are required');
            return;
        }

        // Find container
        this.container = document.querySelector(this.options.containerSelector);
        if (!this.container) {
            console.error(`TabNavigationHelper: Container not found for '${this.options.containerSelector}'`);
            return;
        }

        // Store component-specific tab state in a private variable
        this.activeTabId = this.options.defaultTab;
        
        // Set up tab navigation
        this.setupTabs();
    }

    /**
     * Set up tab navigation
     */
    setupTabs() {
        const tabs = this.container.querySelectorAll(this.options.tabSelector);
        const panels = this.container.querySelectorAll(this.options.panelSelector);
        
        // No tabs found
        if (tabs.length === 0) {
            console.error(`TabNavigationHelper: No tabs found in container for '${this.options.componentName}'`);
            return;
        }
        
        console.log(`TabNavigationHelper: Setting up ${tabs.length} tabs for ${this.options.componentName}`);
        
        // Set up click handlers
        tabs.forEach(tab => {
            tab.addEventListener('click', (event) => {
                // Prevent default behavior and stop event propagation
                event.preventDefault();
                event.stopPropagation();
                
                // Get tab ID
                const tabId = tab.getAttribute('data-tab');
                if (!tabId) return;
                
                // Activate tab
                this.activateTab(tabId);
            });
        });
        
        // Activate default tab
        this.activateTab(this.activeTabId || this.options.defaultTab || tabs[0].getAttribute('data-tab'));
    }
    
    /**
     * Activate a specific tab
     * 
     * @param {string} tabId - ID of the tab to activate
     */
    activateTab(tabId) {
        if (!tabId) return;
        
        const tabs = this.container.querySelectorAll(this.options.tabSelector);
        const panels = this.container.querySelectorAll(this.options.panelSelector);
        
        console.log(`TabNavigationHelper: Activating tab '${tabId}' for ${this.options.componentName}`);
        
        // Deactivate all tabs
        tabs.forEach(tab => {
            tab.classList.remove(this.options.activeTabClass);
        });
        
        // Deactivate all panels
        panels.forEach(panel => {
            panel.classList.remove(this.options.activePanelClass);
            panel.style.display = 'none';
        });
        
        // Activate clicked tab
        const clickedTab = this.container.querySelector(`${this.options.tabSelector}[data-tab="${tabId}"]`);
        if (clickedTab) {
            clickedTab.classList.add(this.options.activeTabClass);
        }
        
        // Activate corresponding panel
        const targetPanel = this.container.querySelector(`#${tabId}-panel`);
        if (targetPanel) {
            targetPanel.classList.add(this.options.activePanelClass);
            targetPanel.style.display = 'block';
        }
        
        // Update active tab ID
        this.activeTabId = tabId;
        
        // Call onTabChange callback if provided
        if (typeof this.options.onTabChange === 'function') {
            this.options.onTabChange(tabId, clickedTab, targetPanel);
        }
    }
    
    /**
     * Get the currently active tab ID
     * 
     * @returns {string} Active tab ID
     */
    getActiveTabId() {
        return this.activeTabId;
    }
}

// Export for use in components
window.TabNavigationHelper = TabNavigationHelper;