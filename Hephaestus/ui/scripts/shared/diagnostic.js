/**
 * Diagnostic Tools
 * 
 * This module provides diagnostic tools to help identify and resolve the tab switching issue
 * between Ergon and Athena components.
 */

console.log('[FILE_TRACE] Loading: diagnostic.js');
// Create a global diagnostic object
window.Diagnostics = {
  // Create a DOM inspector that watches for changes
  watchDOM: function(selector, description) {
    const elements = document.querySelectorAll(selector);
    console.log(`[DIAGNOSTIC] Watching ${elements.length} ${description} elements:`, 
      Array.from(elements).map(el => ({
        id: el.id,
        className: el.className,
        display: el.style.display,
        tagName: el.tagName
      }))
    );
    
    // Monitor visibility changes
    const observer = new MutationObserver((mutations) => {
      mutations.forEach(mutation => {
        if (mutation.type === 'attributes' && 
            (mutation.attributeName === 'style' || 
             mutation.attributeName === 'class' ||
             mutation.attributeName === 'display')) {
          const target = mutation.target;
          console.log(`[DIAGNOSTIC] DOM change detected on ${description}:`, {
            element: target.id || target.className,
            attributeChanged: mutation.attributeName,
            newValue: target.style.display || target.className,
            stack: new Error().stack
          });
        }
      });
    });
    
    // Observe all matching elements
    elements.forEach(element => {
      observer.observe(element, { 
        attributes: true, 
        attributeFilter: ['style', 'class', 'display']
      });
    });
    
    return observer;
  },
  
  // Track all tab click handlers to see if they're being overwritten
  monitorTabHandlers: function(tabSelector) {
    const tabs = document.querySelectorAll(tabSelector);
    console.log(`[DIAGNOSTIC] Monitoring ${tabs.length} tabs:`, 
      Array.from(tabs).map(tab => ({
        dataTab: tab.getAttribute('data-tab'),
        hasClickHandler: !!tab.onclick
      }))
    );
    
    // Patch onclick setters to track when they change
    tabs.forEach(tab => {
      const tabId = tab.getAttribute('data-tab');
      const originalOnClick = tab.onclick;
      
      // Create a property descriptor
      Object.defineProperty(tab, 'onclick', {
        get: function() {
          return this._onclick;
        },
        set: function(newHandler) {
          console.log(`[DIAGNOSTIC] Tab ${tabId} onclick handler being set:`, {
            hadHandler: !!this._onclick,
            stack: new Error().stack.split('\n').slice(1,4).join('\n')
          });
          this._onclick = newHandler;
        },
        configurable: true
      });
      
      // Restore original handler
      if (originalOnClick) {
        tab._onclick = originalOnClick;
      }
    });
  },
  
  // Track component activations
  trackComponentActivation: function() {
    if (!window.uiManager) {
      console.error('[DIAGNOSTIC] Cannot track component activation: uiManager not found');
      return;
    }
    
    const originalActivate = window.uiManager.activateComponent;
    
    window.uiManager.activateComponent = function(componentId) {
      console.log(`[DIAGNOSTIC] UI Manager activating component: ${componentId}`, {
        ignoreComponent: this._ignoreComponent,
        willIgnore: this._ignoreComponent === componentId,
        activeComponent: this.activeComponent,
        stack: new Error().stack.split('\n').slice(1,4).join('\n')
      });
      
      return originalActivate.call(this, componentId);
    };
    
    console.log('[DIAGNOSTIC] Component activation tracking enabled');
  },
  
  // Track the tab navigation utility
  trackTabNavigation: function() {
    if (!window.TabNavigation) {
      console.error('[DIAGNOSTIC] Cannot track TabNavigation: not found');
      return;
    }
    
    const originalSetup = window.TabNavigation.setup;
    
    window.TabNavigation.setup = function(config) {
      console.log(`[DIAGNOSTIC] TabNavigation.setup called for ${config.componentId}`, {
        tabSelector: config.tabSelector,
        panelSelector: config.panelSelector,
        tabCount: document.querySelectorAll(config.tabSelector).length,
        panelCount: document.querySelectorAll(config.panelSelector).length,
        stack: new Error().stack.split('\n').slice(1,4).join('\n')
      });
      
      const result = originalSetup.call(this, config);
      
      console.log(`[DIAGNOSTIC] TabNavigation.setup result: ${result}`);
      
      // Check handlers after setup
      const tabs = document.querySelectorAll(config.tabSelector);
      console.log(`[DIAGNOSTIC] Tab handlers after setup:`, 
        Array.from(tabs).map(tab => ({
          dataTab: tab.getAttribute('data-tab'),
          hasClickHandler: !!tab.onclick,
          handlerType: tab.onclick ? typeof tab.onclick : 'none'
        }))
      );
      
      return result;
    };
    
    console.log('[DIAGNOSTIC] TabNavigation tracking enabled');
  },
  
  // Initialize all diagnostic tools
  init: function() {
    console.log('[DIAGNOSTIC] Initializing diagnostic tools');
    
    // Track HTML panel visibility
    this.htmlPanelObserver = this.watchDOM('#html-panel', 'HTML panel');
    
    // Track Ergon tabs
    this.ergonTabsObserver = this.monitorTabHandlers('.ergon__tab');
    
    // Track Athena tabs
    this.athenaTabsObserver = this.monitorTabHandlers('.athena__tab');
    
    // Track component activation
    this.trackComponentActivation();
    
    // Track tab navigation
    this.trackTabNavigation();
    
    console.log('[DIAGNOSTIC] All diagnostic monitors initialized');
  }
};

// Initialize immediately
window.Diagnostics.init();