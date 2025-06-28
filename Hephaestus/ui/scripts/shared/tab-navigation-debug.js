/**
 * Tab Navigation Debug Helper
 * 
 * This script adds diagnostic tools for tracking tab navigation issues
 * between components, specifically focusing on the _ignoreComponent property
 * that isn't being properly respected during component switching.
 */

console.log('[FILE_TRACE] Loading: tab-navigation-debug.js');
// Create a global namespace for our tab navigation debugging
window.TabNavigationDebug = {
  // Keep track of which component should be ignored
  ignoredComponent: null,
  
  // Keep a history of ignored components
  ignoreHistory: [],
  
  // Hook the setter for _ignoreComponent property
  installDebugHooks: function() {
    console.log('[TabNavigationDebug] Installing debug hooks');
    
    // If UI Manager exists, hook into it
    if (window.uiManager) {
      // Save the original setter if it exists
      const originalSetter = Object.getOwnPropertyDescriptor(window.uiManager, '_ignoreComponent');
      
      // Define a new property with a hooked setter
      Object.defineProperty(window.uiManager, '_ignoreComponent', {
        get: function() {
          console.log('[TabNavigationDebug] Getting _ignoreComponent:', this._ignoredComponentValue);
          return this._ignoredComponentValue;
        },
        set: function(value) {
          console.log('[TabNavigationDebug] Setting _ignoreComponent to:', value);
          console.trace('[TabNavigationDebug] Ignoring component - stack trace');
          
          // Store the value
          this._ignoredComponentValue = value;
          
          // Track in our debug object
          TabNavigationDebug.ignoredComponent = value;
          TabNavigationDebug.ignoreHistory.push({
            timestamp: new Date().toISOString(),
            component: value,
            caller: TabNavigationDebug._getCaller()
          });
          
          // Log the state for debugging
          console.log('[TabNavigationDebug] Ignore history:', TabNavigationDebug.ignoreHistory);
        },
        configurable: true
      });
      
      console.log('[TabNavigationDebug] Successfully hooked _ignoreComponent property');
    } else {
      console.warn('[TabNavigationDebug] uiManager not found, cannot install hooks');
    }
  },
  
  // Helper to get caller information from stack trace
  _getCaller: function() {
    try {
      throw new Error();
    } catch (e) {
      const stack = e.stack.split('\n');
      // Get the caller (skipping this function and its caller)
      return stack.length > 3 ? stack[3].trim() : 'unknown';
    }
  },
  
  // Hook into tab navigation setup to track which tabs are being set up
  hookTabSetup: function() {
    console.log('[TabNavigationDebug] Hooking into TabNavigation.setup');
    
    if (window.TabNavigation) {
      // Save the original setup function
      const originalSetup = window.TabNavigation.setup;
      
      // Replace with our hooked version
      window.TabNavigation.setup = function(config) {
        console.log('[TabNavigationDebug] Tab setup called for component:', config.componentId);
        console.log('[TabNavigationDebug] Current ignored component:', TabNavigationDebug.ignoredComponent);
        
        // Track setup attempt
        TabNavigationDebug.ignoreHistory.push({
          timestamp: new Date().toISOString(),
          action: 'setup_tabs',
          component: config.componentId,
          ignoredComponent: TabNavigationDebug.ignoredComponent,
          caller: TabNavigationDebug._getCaller()
        });
        
        // Call the original function
        return originalSetup.call(this, config);
      };
      
      console.log('[TabNavigationDebug] Successfully hooked TabNavigation.setup');
    } else {
      console.warn('[TabNavigationDebug] TabNavigation not found, cannot hook setup');
    }
  },
  
  // Initialize all hooks
  init: function() {
    console.log('[TabNavigationDebug] Initializing debug hooks');
    this.installDebugHooks();
    this.hookTabSetup();
    console.log('[TabNavigationDebug] Debug hooks initialized');
  },
  
  // Get debug report
  getReport: function() {
    return {
      ignoredComponent: this.ignoredComponent,
      ignoreHistory: this.ignoreHistory,
      uiManagerState: window.uiManager ? {
        activeComponent: window.uiManager.activeComponent,
        components: Object.keys(window.uiManager.components || {})
      } : 'uiManager not available'
    };
  }
};

// Auto-initialize if script is loaded directly
if (document.readyState === 'complete') {
  TabNavigationDebug.init();
} else {
  window.addEventListener('DOMContentLoaded', function() {
    TabNavigationDebug.init();
  });
}

// Add a global helper function
window.debugTabs = function() {
  console.log('[TabNavigationDebug] Current debug state:', TabNavigationDebug.getReport());
  return TabNavigationDebug.getReport();
};

console.log('[TabNavigationDebug] Debug script loaded');