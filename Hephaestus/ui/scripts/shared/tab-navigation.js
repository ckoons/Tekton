/**
 * DEPRECATED: This file will be removed after CSS-first migration is verified
 * Tab Navigation - Simplified Tab Switching
 * 
 * A minimal, Safari-compatible tab navigation system that uses direct onclick handlers
 * and avoids event listeners for maximum compatibility.
 * 
 * This utility provides a standardized way to implement tab switching across components
 * without creating global namespace pollution or conflicts.
 * 
 * Usage:
 * 1. In your component HTML file, add a script that calls TabNavigation.setup()
 * 2. Pass in your component-specific selector prefixes and callback functions
 * 3. The TabNavigation utility will handle the rest
 */

console.log('[FILE_TRACE] Loading: tab-navigation.js');
// Create a debug log tracker to monitor exactly what happens
const DEBUG_TAB_NAV = true;
window._tabNavDebugLogs = [];
function tabNavLog(message, data) {
  const timestamp = new Date().toISOString();
  const logItem = {
    timestamp,
    message,
    data: data || null,
    callingComponent: window._currentLoadingComponent || 'unknown'
  };
  
  if (DEBUG_TAB_NAV) {
    console.log(`[TabNav ${timestamp}] ${message}`, data || '');
  }
  
  window._tabNavDebugLogs.push(logItem);
  
  // Keep only the last 100 logs
  if (window._tabNavDebugLogs.length > 100) {
    window._tabNavDebugLogs.shift();
  }
}

// Expose the debug logs to the console
window.debugTabNavigation = function() {
  console.log('Tab Navigation Debug Logs:', window._tabNavDebugLogs);
  return window._tabNavDebugLogs;
};

window.TabNavigation = {
  /**
   * Set up tab navigation for a component
   * @param {Object} config The configuration object
   * @param {string} config.tabSelector CSS selector for tab elements
   * @param {string} config.panelSelector CSS selector for panel elements
   * @param {string} config.activeTabClass CSS class for active tabs
   * @param {string} config.activePanelClass CSS class for active panels
   * @param {Function} config.onTabChange Optional callback when tab changes
   * @param {string} config.componentId Identifier for the component for debugging
   */
  setup: function(config) {
    tabNavLog('TabNavigation.setup called', config);
    
    if (!config) {
      tabNavLog('ERROR: Missing config');
      console.error('TabNavigation: Missing config');
      return;
    }
    
    const {
      tabSelector,
      panelSelector,
      activeTabClass = 'active',
      activePanelClass = 'active',
      onTabChange = null,
      componentId = 'unknown'
    } = config;
    
    window._currentLoadingComponent = componentId;
    
    if (!tabSelector || !panelSelector) {
      tabNavLog('ERROR: tabSelector and panelSelector are required');
      console.error('TabNavigation: tabSelector and panelSelector are required');
      return;
    }
    
    tabNavLog(`Setting up tabs for ${componentId}`, { tabSelector, panelSelector });
    console.log(`TabNavigation: Setting up tabs for ${componentId} with selector ${tabSelector}`);
    
    // Record current document state for debugging
    const docState = {
      documentReady: document.readyState,
      bodyChildCount: document.body ? document.body.childNodes.length : 'no-body',
      hasHtmlPanel: !!document.getElementById('html-panel'),
      activePanel: document.querySelector('.panel.active')?.id || 'none'
    };
    tabNavLog('Document state during setup', docState);
    
    // Get all tabs
    var tabs = document.querySelectorAll(tabSelector);
    tabNavLog(`Found ${tabs.length} tabs`, { tab_ids: Array.from(tabs).map(t => t.getAttribute('data-tab')) });
    console.log(`TabNavigation: Found ${tabs.length} tabs for ${componentId}`);
    
    // Tag each tab with component ID for debugging
    for (var i = 0; i < tabs.length; i++) {
      tabs[i]._componentId = componentId;
    }
    
    // Use direct onclick handlers for maximum compatibility
    for (var i = 0; i < tabs.length; i++) {
      // Store the original onclick if it exists
      const originalOnClick = tabs[i].onclick;
      if (originalOnClick) {
        tabNavLog(`Tab already had onclick handler`, { 
          tab: tabs[i].getAttribute('data-tab'),
          handler: originalOnClick.toString()
        });
      }
      
      // Create a closure to capture the current tab
      (function(tab, index) {
        // Preserve any existing handler for diagnostic purposes
      const existingHandler = tab.onclick;
      if (existingHandler) {
        console.log(`[TabNav] Tab already has onclick handler before we set it:`, {
          tab: tab.getAttribute('data-tab'),
          componentId: componentId,
          handler: existingHandler.toString().substring(0, 100) + '...'
        });
      }
      
      tab.onclick = function(event) {
          // Track when this gets called
          const clickTime = new Date().toISOString();
          console.log(`[TabNav-CRITICAL] Tab.onclick called for ${componentId} tab ${this.getAttribute('data-tab')}`, {
            time: clickTime,
            event: event ? {
              type: event.type,
              target: event.target ? event.target.tagName : 'none',
              currentTarget: event.currentTarget ? event.currentTarget.tagName : 'none'
            } : 'no event',
            thisObject: {
              tagName: this.tagName,
              className: this.className,
              dataTab: this.getAttribute('data-tab')
            }
          });
          
          tabNavLog(`Tab clicked at ${clickTime}`, {
            componentId: componentId,
            tabIndex: index, 
            tab: this.getAttribute('data-tab'),
            event: {
              type: event ? event.type : 'none',
              target: event && event.target ? event.target.tagName : 'none',
              currentTarget: event && event.currentTarget ? event.currentTarget.tagName : 'none'
            }
          });
          
          var tabId = this.getAttribute('data-tab');
          if (!tabId) {
            tabNavLog('ERROR: Tab missing data-tab attribute');
            console.error('TabNavigation: Tab missing data-tab attribute');
            return false;
          }
          
          tabNavLog(`Switching ${componentId} tab to ${tabId}`);
          console.log(`TabNavigation: Switching ${componentId} tab to ${tabId}`);
          
          // Update active tab
          var allTabs = document.querySelectorAll(tabSelector);
          for (var j = 0; j < allTabs.length; j++) {
            if (allTabs[j].getAttribute('data-tab') === tabId) {
              allTabs[j].classList.add(activeTabClass);
              tabNavLog(`Added ${activeTabClass} class to tab ${tabId}`);
            } else {
              allTabs[j].classList.remove(activeTabClass);
              tabNavLog(`Removed ${activeTabClass} class from tab ${allTabs[j].getAttribute('data-tab')}`);
            }
          }
          
          // Update panels
          var panels = document.querySelectorAll(panelSelector);
          var targetPanelId = tabId + '-panel';
          
          tabNavLog(`Looking for panels matching ${panelSelector}`, { 
            foundCount: panels.length,
            targetPanelId: targetPanelId,
            panelIds: Array.from(panels).map(p => p.id)
          });
          
          for (var k = 0; k < panels.length; k++) {
            if (panels[k].id === targetPanelId) {
              panels[k].style.display = 'block';
              panels[k].classList.add(activePanelClass);
              tabNavLog(`Made panel ${targetPanelId} visible`);
            } else {
              panels[k].style.display = 'none';
              panels[k].classList.remove(activePanelClass);
              tabNavLog(`Hidden panel ${panels[k].id}`);
            }
          }
          
          // Call the callback if provided
          if (typeof onTabChange === 'function') {
            tabNavLog(`Calling onTabChange callback for ${tabId}`);
            try {
              onTabChange(tabId);
            } catch (err) {
              tabNavLog(`ERROR in onTabChange callback`, { error: err.message });
              console.error('TabNavigation: Error in onTabChange callback', err);
            }
          }
          
          // Prevent default behavior
          return false;
        };
      })(tabs[i], i);
    }
    
    tabNavLog(`Setup complete for ${tabs.length} tabs in ${componentId}`);
    console.log(`TabNavigation: Setup complete for ${tabs.length} tabs in ${componentId}`);
    return tabs.length;
  },
  
  /**
   * Debug function to force a tab switch for testing
   */
  forceSwitch: function(componentId, tabSelector, panelSelector, tabId) {
    tabNavLog(`Force switching ${componentId} tab to ${tabId}`);
    console.log(`TabNavigation: Force switching ${componentId} tab to ${tabId}`);
    
    // Find the tab and trigger its click handler
    const tab = document.querySelector(`${tabSelector}[data-tab="${tabId}"]`);
    if (tab && typeof tab.onclick === 'function') {
      tabNavLog(`Forcing click on tab ${tabId}`);
      tab.onclick({ type: 'forced', target: tab, currentTarget: tab });
      return true;
    } else {
      tabNavLog(`ERROR: Could not find tab ${tabId} to force click`);
      console.error(`TabNavigation: Could not find tab ${tabId} to force click`);
      return false;
    }
  }
};