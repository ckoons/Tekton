/**
 * DEPRECATED: This file will be removed after CSS-first migration is verified
 * 
 * Minimal Component Loader
 * 
 * A stripped-down, extremely simple component loader for the Hephaestus UI.
 * Focuses only on loading a component's HTML into the RIGHT PANEL.
 * 
 * IMPORTANT: This is the only loader we need. We have ONE RIGHT PANEL and only
 * ONE COMPONENT AT A TIME. This simplifies everything.
 */

console.log('[FILE_TRACE] Loading: minimal-loader.js');
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
      'settings': '/components/settings/settings-component.html',
      'numa': '/components/numa/numa-component.html',
      'noesis': '/components/noesis/noesis-component.html',
      'terma': '/components/terma/terma-component.html',
      'tekton-dashboard': '/components/tekton-dashboard/tekton-dashboard.html'
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
   * Load a utility script with full path
   * @param {string} scriptPath The full path to the script
   * @returns {Promise} A promise that resolves when the script is loaded
   */
  async loadUtilityScript(scriptPath) {
    const scriptName = scriptPath.split('/').pop().replace('.js', '');
    
    if (this.utilityLoaded[scriptName]) {
      console.log(`MinimalLoader: Script ${scriptName} already loaded, reusing`);
      return Promise.resolve();
    }
    
    console.log(`MinimalLoader: Loading script ${scriptPath}...`);
    
    return new Promise((resolve, reject) => {
      // Add cache-busting timestamp to ensure we get the latest version
      const timestamp = new Date().getTime();
      const script = document.createElement('script');
      script.src = `${scriptPath}?t=${timestamp}`;
      script.async = false; // Use synchronous loading to ensure utilities load in order
      script.onload = () => {
        console.log(`MinimalLoader: Successfully loaded script ${scriptPath}`);
        this.utilityLoaded[scriptName] = true;
        
        // Add a small delay to ensure script execution completes
        setTimeout(() => resolve(), 20);
      };
      script.onerror = (err) => {
        console.error(`MinimalLoader: Failed to load script ${scriptPath}`, err);
        reject(err);
      };
      document.head.appendChild(script);
    });
  }
  
  /**
   * Load a component into the specified container
   */
  async loadComponent(componentId) {
    console.log(`MinimalLoader: Loading component ${componentId}`);
    
    
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
      
      // DEBUG: Log the actual path being used
      console.log(`MinimalLoader: Using path for ${componentId}: ${componentPath}`);

      // First, ensure we have the tab navigation utility loaded
      // This helps standardize tab switching across components
      await this.loadUtility('tab-navigation');

      // Load component scripts from registry if they exist
      await this.loadComponentScripts(componentId);

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
        
        // Load utilities in sequence to avoid race conditions
        await this.loadUtilityScript('/scripts/shared/tab-navigation.js');
        await this.loadUtilityScript('/scripts/shared/tab-navigation-debug.js');
        await this.loadUtilityScript('/scripts/shared/component-loading-guard.js');
        await this.loadUtilityScript('/scripts/shared/tab-switcher.js');
        
        console.log(`MinimalLoader: All utilities loaded successfully`);
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
      
      // Initialize Settings UI when component loads
      if (componentId === 'settings') {
        if (window.initializeSettingsUI) {
          setTimeout(() => {
            window.initializeSettingsUI();
            console.log('MinimalLoader: Settings UI initialized');
          }, 100);
        } else {
          console.error('MinimalLoader: initializeSettingsUI not found!');
        }
      }
      
      // Load Profile data when component loads
      if (componentId === 'profile') {
        setTimeout(() => {
          if (window.profile_resetChanges) {
            console.log('MinimalLoader: Loading profile data from backend');
            window.profile_resetChanges();
          }
        }, 200);
      }
      
      // Load Settings data when component loads
      if (componentId === 'settings') {
        setTimeout(async () => {
          try {
            console.log('MinimalLoader: Loading settings data from backend');
            const response = await fetch('/api/settings', {
              method: 'GET',
              headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
              }
            });
            
            if (response.ok) {
              const settingsData = await response.json();
              
              // Apply loaded settings to UI
              if (settingsData.themeBase) {
                const themeRadio = document.querySelector(`input[name="theme-mode"][value="${settingsData.themeBase}"]`);
                if (themeRadio) themeRadio.checked = true;
              }
              
              if (settingsData.accentPreset) {
                const accentRadio = document.querySelector(`input[name="accent-color"][value="${settingsData.accentPreset}"]`);
                if (accentRadio) accentRadio.checked = true;
              }
              
              if (settingsData.showGreekNames !== undefined) {
                const greekCheckbox = document.getElementById('greek-names-setting');
                if (greekCheckbox) greekCheckbox.checked = settingsData.showGreekNames;
              }
              
              if (settingsData.terminalFontSize) {
                const fontSelect = document.getElementById('terminal-font-setting');
                if (fontSelect) fontSelect.value = settingsData.terminalFontSize;
              }
              
              // Apply the loaded theme
              if (window.applyTheme) {
                window.applyTheme();
              }
            }
          } catch (error) {
            console.error('MinimalLoader: Error loading settings:', error);
          }
        }, 200);
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
  
  /**
   * Load component scripts from registry
   * @param {string} componentId The component ID to load scripts for
   * @returns {Promise} A promise that resolves when scripts are loaded
   */
  async loadComponentScripts(componentId) {
    try {
      // Fetch component registry to get script list
      const registryResponse = await fetch('/server/component_registry.json');
      if (!registryResponse.ok) {
        console.warn(`MinimalLoader: Cannot load component registry`);
        return;
      }
      
      const registry = await registryResponse.json();
      const component = registry.components.find(c => c.id === componentId);
      
      if (!component || !component.scripts) {
        console.log(`MinimalLoader: No scripts defined for ${componentId}`);
        return;
      }
      
      console.log(`MinimalLoader: Loading ${component.scripts.length} scripts for ${componentId}`);
      
      // Load each script in sequence
      for (const scriptPath of component.scripts) {
        await new Promise((resolve, reject) => {
          const script = document.createElement('script');
          script.src = `/${scriptPath}?t=${new Date().getTime()}`;
          script.async = false;
          script.onload = () => {
            console.log(`MinimalLoader: Loaded script ${scriptPath}`);
            resolve();
          };
          script.onerror = (err) => {
            console.warn(`MinimalLoader: Failed to load script ${scriptPath}`, err);
            resolve(); // Continue anyway
          };
          document.head.appendChild(script);
        });
      }
      
    } catch (error) {
      console.error(`MinimalLoader: Error loading scripts for ${componentId}:`, error);
    }
  }
}

// Create a global instance
window.minimalLoader = new MinimalLoader();