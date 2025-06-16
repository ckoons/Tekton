/**
 * Test Component JavaScript
 * Demonstrates Shadow DOM component isolation in Hephaestus
 */

// Initialize component when loaded
(function() {
  // Set up tabs
  setupTabs();
  
  // Set up interaction demo
  setupInteractionDemo();
  
  // Set up settings form
  setupSettingsForm();
  
  // Register cleanup handler
  registerCleanupHandler();
  
  console.log('Test component initialized in Shadow DOM');
})();

/**
 * Set up tab navigation
 */
function setupTabs() {
  // Get tab buttons and panels using the component context
  const tabButtons = component.$$('.test-tab-button');
  const tabPanels = component.$$('.test-tab-panel');
  
  // Add click handlers using event delegation
  component.on('click', '.test-tab-button', function(event) {
    const tabId = this.getAttribute('data-tab');
    
    // Remove active class from all tabs and panels
    tabButtons.forEach(button => button.classList.remove('active'));
    tabPanels.forEach(panel => panel.classList.remove('active'));
    
    // Add active class to selected tab and panel
    this.classList.add('active');
    component.$(`#${tabId}-panel`).classList.add('active');
    
    console.log(`Tab switched to: ${tabId}`);
  });
}

/**
 * Set up interaction demo
 */
function setupInteractionDemo() {
  const updateButton = component.$('#test-update-button');
  const resultDisplay = component.$('#test-result');
  
  if (updateButton && resultDisplay) {
    // State to track number of clicks
    let clickCount = 0;
    
    // Add click handler
    updateButton.addEventListener('click', () => {
      clickCount++;
      
      // Update result display
      resultDisplay.textContent = `Button clicked ${clickCount} time${clickCount !== 1 ? 's' : ''}!
Update timestamp: ${new Date().toLocaleTimeString()}
Component ID: ${component.id}
DOM is isolated: Shadow boundaries prevent conflicts`;
      
      // Add a class to show visual feedback (removed after animation)
      resultDisplay.classList.add('updated');
      setTimeout(() => {
        resultDisplay.classList.remove('updated');
      }, 1000);
      
      console.log(`Interaction demo clicked: ${clickCount} times`);
    });
  }
}

/**
 * Set up settings form
 */
function setupSettingsForm() {
  const saveButton = component.$('#test-save-button');
  const resetButton = component.$('#test-reset-button');
  const nameInput = component.$('#test-setting-name');
  const modeSelect = component.$('#test-setting-mode');
  
  // Default values
  const defaultSettings = {
    name: 'Test Component',
    mode: 'dark'
  };
  
  // Add save button event handler
  if (saveButton) {
    saveButton.addEventListener('click', () => {
      // Get current values
      const name = nameInput?.value || defaultSettings.name;
      const mode = modeSelect?.value || defaultSettings.mode;
      
      // Save settings (just a simulation)
      console.log('Settings saved:', { name, mode });
      
      // Update UI to show success
      const title = component.$('.test-title');
      if (title) {
        title.textContent = name;
      }
      
      // Show confirmation message
      const tektonUI = component.getTektonUI();
      if (tektonUI) {
        tektonUI.showError(`Settings saved for ${name}`);
      }
    });
  }
  
  // Add reset button event handler
  if (resetButton) {
    resetButton.addEventListener('click', () => {
      // Reset form to defaults
      if (nameInput) nameInput.value = defaultSettings.name;
      if (modeSelect) modeSelect.value = defaultSettings.mode;
      
      console.log('Settings reset to defaults');
    });
  }
}

/**
 * Register cleanup handler for when component is unloaded
 */
function registerCleanupHandler() {
  // Register cleanup function
  component.registerCleanup(() => {
    console.log('Test component cleanup handler executed');
    
    // Any cleanup code would go here (e.g., removing event listeners, stopping timers)
    // Note: Event listeners registered through component.on() are automatically cleaned up
  });
}

// Add a CSS animation for the result display using DOM API
// This demonstrates adding styles programmatically
function addDynamicStyles() {
  const styleElement = document.createElement('style');
  styleElement.textContent = `
    .test-result-display.updated {
      animation: highlight-update 1s ease;
    }
    
    @keyframes highlight-update {
      0% { background-color: var(--color-primary, #007bff); color: white; }
      100% { background-color: var(--bg-tertiary, #333333); color: var(--text-secondary, #aaaaaa); }
    }
  `;
  
  // Append to shadow root
  component.root.appendChild(styleElement);
}

// Execute dynamic styles addition
addDynamicStyles();