/**
 * Component Loading Guard
 * 
 * This utility helps manage the loading and initialization of components
 * to prevent conflicts, especially with tab navigation across components.
 */

window.ComponentLoadingGuard = {
  // Current active component 
  activeComponent: null,
  
  // Components that need special handling (i.e., they manage their own tabs)
  specialComponents: ['athena', 'ergon'],
  
  // Loading state tracking
  loadingState: {
    inProgress: false,
    component: null,
    timestamp: null
  },
  
  // Initialize the guard
  init: function() {
    console.log('[ComponentLoadingGuard] Initializing component loading protection');
    this._hookMinimalLoader();
    this._hookUIManager();
  },
  
  // Add a hook to the MinimalLoader to intercept component loading
  _hookMinimalLoader: function() {
    if (!window.minimalLoader) {
      console.warn('[ComponentLoadingGuard] minimalLoader not found');
      return;
    }
    
    const originalLoadComponent = window.minimalLoader.loadComponent;
    
    window.minimalLoader.loadComponent = async function(componentId) {
      console.log(`[ComponentLoadingGuard] Component load requested: ${componentId}`);
      
      if (ComponentLoadingGuard.loadingState.inProgress) {
        console.warn(`[ComponentLoadingGuard] Already loading ${ComponentLoadingGuard.loadingState.component}, blocking load of ${componentId}`);
        return null;
      }
      
      // Set loading state
      ComponentLoadingGuard.loadingState = {
        inProgress: true,
        component: componentId,
        timestamp: new Date().toISOString()
      };
      
      // Update active component
      ComponentLoadingGuard.activeComponent = componentId;
      
      try {
        // Call original method
        const result = await originalLoadComponent.call(this, componentId);
        
        // Short delay to allow component to initialize
        await new Promise(resolve => setTimeout(resolve, 50));
        
        // Reset loading state
        ComponentLoadingGuard.loadingState.inProgress = false;
        
        return result;
      } catch (error) {
        console.error(`[ComponentLoadingGuard] Error loading component ${componentId}:`, error);
        ComponentLoadingGuard.loadingState.inProgress = false;
        throw error;
      }
    };
    
    console.log('[ComponentLoadingGuard] Successfully hooked minimalLoader.loadComponent');
  },
  
  // Add a hook to the UI Manager to handle ignored components properly
  _hookUIManager: function() {
    if (!window.uiManager) {
      console.warn('[ComponentLoadingGuard] uiManager not found');
      return;
    }
    
    // Store the active component and which component is being ignored
    window.ComponentLoadingGuard.getUIManagerState = function() {
      return {
        activeComponent: window.uiManager.activeComponent,
        ignoredComponent: window.uiManager._ignoreComponent
      };
    };
    
    console.log('[ComponentLoadingGuard] Added uiManager state tracking');
  },
  
  // Record component initialization
  recordInitialization: function(componentId) {
    console.log(`[ComponentLoadingGuard] Component initialized: ${componentId}`);
    
    // If this is a special component that manages its own tabs,
    // make sure the UI manager knows to ignore it
    if (this.specialComponents.includes(componentId) && window.uiManager) {
      if (!window.uiManager._ignoreComponent) {
        console.log(`[ComponentLoadingGuard] Setting uiManager._ignoreComponent to ${componentId}`);
        window.uiManager._ignoreComponent = componentId;
      }
    }
  }
};

// Initialize when the document is ready
if (document.readyState === 'complete') {
  ComponentLoadingGuard.init();
} else {
  window.addEventListener('DOMContentLoaded', function() {
    ComponentLoadingGuard.init();
  });
}

console.log('[ComponentLoadingGuard] Component loading guard script loaded');