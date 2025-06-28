/**
 * Tab Switcher Utility
 *
 * This utility provides functions to help diagnose and fix tab switching issues
 * across components. It can be used from the browser console to manually test
 * tab switching functionality.
 */

console.log('[FILE_TRACE] Loading: tab-switcher.js');
window.TabSwitcher = {
  /**
   * Switch a tab within a component
   * @param {string} componentId - The component ID (e.g., 'athena', 'ergon')
   * @param {string} tabId - The tab ID to switch to
   */
  switchTab: function(componentId, tabId) {
    console.log(`[TabSwitcher] Attempting to switch ${componentId} to tab: ${tabId}`);
    
    // Determine tab selector based on component
    const tabSelector = `.${componentId}__tab`;
    
    // Find the tab
    const tab = document.querySelector(`${tabSelector}[data-tab="${tabId}"]`);
    if (!tab) {
      console.error(`[TabSwitcher] Tab not found: ${tabId} in component ${componentId}`);
      return false;
    }
    
    console.log(`[TabSwitcher] Found tab:`, tab);
    
    // Check if the TabNavigation utility is available
    if (window.TabNavigation) {
      console.log(`[TabSwitcher] Using TabNavigation to force tab switch`);
      return window.TabNavigation.forceSwitch(
        componentId,
        tabSelector,
        `.${componentId}__panel`,
        tabId
      );
    } else {
      // Fallback to direct click
      console.log(`[TabSwitcher] TabNavigation not available, using direct click`);
      if (typeof tab.click === 'function') {
        tab.click();
        return true;
      } else {
        console.error(`[TabSwitcher] Tab does not have click method`);
        return false;
      }
    }
  },
  
  /**
   * Run diagnostics on tab state
   */
  diagnose: function() {
    // Get tab elements for both components
    const athenaTabsEl = document.querySelectorAll('.athena__tab');
    const ergonTabsEl = document.querySelectorAll('.ergon__tab');
    
    // Get tab panels for both components
    const athenaPanelsEl = document.querySelectorAll('.athena__panel');
    const ergonPanelsEl = document.querySelectorAll('.ergon__panel');
    
    // Get component state objects if available
    const athenaState = window.athenaComponent?.state || { activeTab: 'unknown' };
    const ergonState = window.ergonComponent?.state || { activeTab: 'unknown' };
    
    // Collect UI manager state
    const uiManagerState = window.uiManager ? {
      activeComponent: window.uiManager.activeComponent,
      ignoreComponent: window.uiManager._ignoreComponent
    } : 'not available';
    
    // Collect component loading guard state if available
    const guardState = window.ComponentLoadingGuard ? {
      activeComponent: window.ComponentLoadingGuard.activeComponent,
      loadingState: window.ComponentLoadingGuard.loadingState
    } : 'not available';
    
    // Collect tab navigation debug info if available
    const tabNavDebug = window._tabNavDebugLogs ? 
      window._tabNavDebugLogs.slice(-5) : 'not available';
    
    // Build report
    const report = {
      components: {
        athena: {
          tabCount: athenaTabsEl.length,
          panelCount: athenaPanelsEl.length,
          componentState: athenaState,
          activeTabs: Array.from(athenaTabsEl)
            .filter(tab => tab.classList.contains('athena__tab--active'))
            .map(tab => tab.getAttribute('data-tab')),
          activePanels: Array.from(athenaPanelsEl)
            .filter(panel => panel.classList.contains('athena__panel--active'))
            .map(panel => panel.id)
        },
        ergon: {
          tabCount: ergonTabsEl.length,
          panelCount: ergonPanelsEl.length,
          componentState: ergonState,
          activeTabs: Array.from(ergonTabsEl)
            .filter(tab => tab.classList.contains('ergon__tab--active'))
            .map(tab => tab.getAttribute('data-tab')),
          activePanels: Array.from(ergonPanelsEl)
            .filter(panel => panel.classList.contains('ergon__panel--active'))
            .map(panel => panel.id)
        }
      },
      system: {
        uiManager: uiManagerState,
        loadingGuard: guardState,
        tabNavDebug: tabNavDebug
      }
    };
    
    console.log(`[TabSwitcher] Diagnostic report:`, report);
    return report;
  },
  
  /**
   * Try to fix tab switching issues by re-applying tab setup
   */
  fixTabs: function(componentId) {
    if (!componentId) {
      console.error(`[TabSwitcher] Component ID required to fix tabs`);
      return false;
    }
    
    console.log(`[TabSwitcher] Attempting to fix tabs for ${componentId}`);
    
    if (componentId === 'athena') {
      // Re-run athena tab setup
      if (typeof setupAthenaTabs === 'function') {
        console.log(`[TabSwitcher] Re-running setupAthenaTabs`);
        setupAthenaTabs();
        return true;
      } else {
        console.error(`[TabSwitcher] setupAthenaTabs function not found`);
        return false;
      }
    } else if (componentId === 'ergon') {
      // Re-run ergon tab setup
      if (typeof setupErgonTabs === 'function') {
        console.log(`[TabSwitcher] Re-running setupErgonTabs`);
        setupErgonTabs();
        return true;
      } else {
        console.error(`[TabSwitcher] setupErgonTabs function not found`);
        return false;
      }
    } else {
      console.error(`[TabSwitcher] Unknown component: ${componentId}`);
      return false;
    }
  }
};

// Add a global helper for browser console access
window.fixTabs = function(componentId) {
  return window.TabSwitcher.fixTabs(componentId);
};

window.diagnoseTabs = function() {
  return window.TabSwitcher.diagnose();
};

window.switchComponentTab = function(componentId, tabId) {
  return window.TabSwitcher.switchTab(componentId, tabId);
};

console.log('[TabSwitcher] Tab switcher utility loaded - use window.diagnoseTabs(), window.fixTabs(), or window.switchComponentTab() from the console');