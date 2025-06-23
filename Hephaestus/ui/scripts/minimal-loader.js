/**
 * Minimal Component Loader
 * 
 * A stripped-down, extremely simple component loader for the Hephaestus UI.
 * Focuses only on loading a component's HTML into the RIGHT PANEL.
 * 
 * IMPORTANT: This is the only loader we need. We have ONE RIGHT PANEL and only
 * ONE COMPONENT AT A TIME. This simplifies everything.
 */

class MinimalLoader {
  constructor() {
    // Standard component paths
    this.componentPaths = {
      'athena': '/components/athena/athena-component.html',
      'ergon': '/components/ergon/ergon-component.html',
      'rhetor': '/components/rhetor/rhetor-component.html',
      'apollo': '/components/apollo/apollo-component.html',
      'metis': '/components/metis/metis-component.html',
      'budget': '/components/budget/budget-component.html',
      'profile': '/components/profile/profile-component.html',
      'settings': '/components/settings/settings-component.html'
    };
    
    // Keep track of the current component to prevent reloading
    this.currentComponent = null;
    
    // Utility libraries that might need to be loaded
    this.utilityLoaded = {
      'tab-navigation': false
    };
  }
  
  /**
   * Load a utility library needed by components
   * @param {string} utilName The name of the utility to load
   * @returns {Promise} A promise that resolves when the utility is loaded
   */
  async loadUtility(utilName) {
    if (this.utilityLoaded[utilName]) {
      console.log(`MinimalLoader: Utility ${utilName} already loaded, reusing`);
      return Promise.resolve();
    }
    
    console.log(`MinimalLoader: Loading utility ${utilName}...`);
    
    return new Promise((resolve, reject) => {
      // Add cache-busting timestamp to ensure we get the latest version
      const timestamp = new Date().getTime();
      const script = document.createElement('script');
      script.src = `/scripts/shared/${utilName}.js?t=${timestamp}`;
      script.async = false; // Use synchronous loading to ensure utilities load in order
      script.onload = () => {
        console.log(`MinimalLoader: Successfully loaded utility ${utilName}`);
        this.utilityLoaded[utilName] = true;
        
        // Add a small delay to ensure script execution completes
        setTimeout(() => resolve(), 20);
      };
      script.onerror = (err) => {
        console.error(`MinimalLoader: Failed to load utility ${utilName}`, err);
        reject(err);
      };
      document.head.appendChild(script);
    });
  }
  
  /**
   * Load a component into the specified container
   */
  async loadComponent(componentId) {
    console.log(`MinimalLoader: Loading component ${componentId} - DEBUG LOG`);
    
    // Debug logging to show which loader is handling the component
    if (componentId === 'profile' || componentId === 'settings') {
      console.log(`MinimalLoader: IMPORTANT DEBUG - Loading ${componentId} component`);
      console.log(`MinimalLoader: Component paths: ${JSON.stringify(this.componentPaths)}`);
      console.log(`MinimalLoader: Path for ${componentId}: ${this.componentPaths[componentId]}`);
    }
    
    // DEBUGGING: Check the Rhetor label in the DOM
    if (componentId === 'rhetor') {
      const rhetorLabel = document.querySelector('.nav-item[data-component="rhetor"] .nav-label');
      console.log('DEBUGGING: Rhetor label in DOM before loading:', rhetorLabel ? rhetorLabel.textContent : 'not found');
    }

    // Get the RIGHT PANEL container
    const container = document.getElementById('html-panel');
    if (!container) {
      console.error('MinimalLoader: RIGHT PANEL (html-panel) not found');
      return null;
    }

    // Don't reload if it's already the current component
    if (this.currentComponent === componentId) {
      console.log(`MinimalLoader: ${componentId} is already loaded, skipping`);
      return;
    }

    // Set initial loading state with timestamp
    container.setAttribute('data-tekton-loading-state', 'pending');
    container.setAttribute('data-tekton-loading-component', componentId);
    container.setAttribute('data-tekton-loading-started', Date.now());
    // Clear any previous error
    container.removeAttribute('data-tekton-loading-error');
    
    try {
      // Show loading indicator and update state to loading
      container.innerHTML = `<div style="padding: 20px; text-align: center;">Loading ${componentId}...</div>`;
      container.setAttribute('data-tekton-loading-state', 'loading');
      console.log(`MinimalLoader: Set loading state to 'loading' for ${componentId}`);

      // Determine component path
      const componentPath = this.componentPaths[componentId] || `/components/${componentId}/${componentId}-component.html`;

      // First, ensure we have the tab navigation utility loaded
      // This helps standardize tab switching across components
      await this.loadUtility('tab-navigation');

      // Now load the component HTML
      const response = await fetch(componentPath);
      if (!response.ok) {
        throw new Error(`Failed to load component: ${response.status} ${response.statusText}`);
      }

      const html = await response.text();

      // Display the component HTML directly in the container
      container.innerHTML = html;

      // Update current component
      this.currentComponent = componentId;

      // Make sure the container is visible
      container.style.display = 'block';

      // Explicitly load TabNavigation and other utilities first to ensure they're available
      // This ensures tabs work even if component_registry.json doesn't include them
      try {
        console.log(`MinimalLoader: Ensuring utilities are loaded before component scripts`);
        
        // Load TabNavigation
        const tabNavScript = document.createElement('script');
        tabNavScript.src = `/scripts/shared/tab-navigation.js?t=${new Date().getTime()}`;
        document.head.appendChild(tabNavScript);
        
        // Load our debugging helpers
        console.log(`MinimalLoader: Loading debugging helpers for TabNavigation`);
        const debugScript = document.createElement('script');
        debugScript.src = `/scripts/shared/tab-navigation-debug.js?t=${new Date().getTime()}`;
        document.head.appendChild(debugScript);
        
        // Load component loading guard
        console.log(`MinimalLoader: Loading component loading guard`);
        const guardScript = document.createElement('script');
        guardScript.src = `/scripts/shared/component-loading-guard.js?t=${new Date().getTime()}`;
        document.head.appendChild(guardScript);
        
        // Load tab switcher utility
        console.log(`MinimalLoader: Loading tab switcher utility`);
        const tabSwitcherScript = document.createElement('script');
        tabSwitcherScript.src = `/scripts/shared/tab-switcher.js?t=${new Date().getTime()}`;
        document.head.appendChild(tabSwitcherScript);
        
        // Small delay to ensure utilities are loaded before running component scripts
        await new Promise(resolve => setTimeout(resolve, 100));
      } catch (error) {
        console.error('MinimalLoader: Error loading utilities:', error);
      }
      
      // Set a global variable so component scripts know what's being loaded
      window._currentLoadingComponent = componentId;
      
      // Run any scripts in the component
      console.log(`MinimalLoader: Running ${componentId} scripts`);
      const scripts = container.querySelectorAll('script');
      
      // Process the scripts in sequence to avoid race conditions
      for (let i = 0; i < scripts.length; i++) {
        const script = scripts[i];
        const newScript = document.createElement('script');
        
        try {
          if (script.src) {
            newScript.src = script.src;
            // For src scripts, we need to wait for them to load
            await new Promise((resolve, reject) => {
              newScript.onload = resolve;
              newScript.onerror = reject;
              document.head.appendChild(newScript);
            });
            console.log(`MinimalLoader: Loaded external script ${newScript.src}`);
          } else {
            // For inline scripts, execute in global scope
            const scriptContent = script.textContent;
            
            // For Settings component, ensure functions are global
            if (componentId === 'settings') {
              // Replace function declarations to ensure they're global
              const globalScript = scriptContent
                .replace(/window\.settings_switchTab\s*=\s*function/g, 'window.settings_switchTab = function')
                .replace(/window\.settings_saveAllSettings\s*=\s*function/g, 'window.settings_saveAllSettings = function')
                .replace(/window\.settings_resetAllSettings\s*=\s*function/g, 'window.settings_resetAllSettings = function')
                .replace(/window\.settings_toggleGreekNames\s*=\s*function/g, 'window.settings_toggleGreekNames = function');
              
              newScript.textContent = globalScript;
            } else {
              newScript.textContent = scriptContent;
            }
            
            document.head.appendChild(newScript);
            console.log(`MinimalLoader: Executed inline script for ${componentId}`);
          }
        } catch (error) {
          console.error(`MinimalLoader: Error loading script for ${componentId}:`, error);
        }
      }

      console.log(`MinimalLoader: ${componentId} loaded successfully`);
      
      // Set loaded state and clear any error attributes
      container.setAttribute('data-tekton-loading-state', 'loaded');
      container.removeAttribute('data-tekton-loading-error');
      
      // Calculate and log loading time
      const startTime = parseInt(container.getAttribute('data-tekton-loading-started'));
      const loadTime = Date.now() - startTime;
      console.log(`MinimalLoader: ${componentId} loaded in ${loadTime}ms`);
      
      // Update component headers based on current naming convention
      if (window.settingsManager && window.settingsManager.updateComponentHeaders) {
        setTimeout(() => {
          window.settingsManager.updateComponentHeaders();
          console.log(`MinimalLoader: Updated component headers for ${componentId}`);
        }, 100);
      }
      
      // For Settings component, ensure script is loaded
      if (componentId === 'settings') {
        const settingsScript = document.createElement('script');
        settingsScript.src = `/scripts/settings/settings-component.js?t=${new Date().getTime()}`;
        settingsScript.onload = () => {
          console.log('MinimalLoader: Settings component script loaded');
        };
        document.head.appendChild(settingsScript);
      }
    } catch (error) {
      console.error(`MinimalLoader: Error loading ${componentId}:`, error);
      
      // Set error state with error details
      container.setAttribute('data-tekton-loading-state', 'error');
      container.setAttribute('data-tekton-loading-error', error.message);
      
      // Calculate loading time even for errors
      const startTime = parseInt(container.getAttribute('data-tekton-loading-started'));
      const loadTime = Date.now() - startTime;
      console.log(`MinimalLoader: ${componentId} failed after ${loadTime}ms`);
      
      container.innerHTML = `
        <div style="padding: 20px; margin: 20px; border: 1px solid #dc3545; border-radius: 8px;">
          <h3 style="color: #dc3545;">Error Loading ${componentId}</h3>
          <p>${error.message}</p>
        </div>
      `;
    }
  }
}

// Create a global instance
window.minimalLoader = new MinimalLoader();