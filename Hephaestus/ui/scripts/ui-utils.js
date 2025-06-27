/**
 * DEPRECATED: This file will be removed after CSS-first migration is verified
 * UI Utilities
 * Shared utility functions for UI components
 */

/**
 * UI Utilities class
 * Provides shared functionality for UI operations across components
 */
class UIUtils {
  constructor() {
    // Store state that might be needed across components
    this.activePanel = 'terminal'; // Default panel
  }

  /**
   * Initialize UI utilities
   * @returns {UIUtils} The initialized instance for chaining
   */
  init() {
    console.log('Initializing UI utilities');
    
    // Register global instance
    window.uiUtils = this;
    
    return this;
  }
  
  /**
   * Switch between terminal, HTML, settings, and profile panels
   * @param {string} panelId - 'terminal', 'html', 'settings', or 'profile'
   */
  activatePanel(panelId) {
    console.log(`Activating panel: ${panelId}`);
    
    // Make sure we're dealing with a valid panel ID
    if (!['terminal', 'html', 'settings', 'profile'].includes(panelId)) {
      console.error(`Invalid panel ID: ${panelId}`);
      return;
    }
    
    // Get all panels
    const panels = document.querySelectorAll('.panel');
    console.log(`Found ${panels.length} panels`);
    
    // Hide all panels first
    panels.forEach(panel => {
      panel.classList.remove('active');
      panel.style.display = 'none';
    });
    
    // Now activate the requested panel
    const targetPanel = document.getElementById(`${panelId}-panel`);
    if (targetPanel) {
      console.log(`Found target panel: ${targetPanel.id}`);
      
      // Force display and add active class
      targetPanel.style.display = 'block';
      targetPanel.classList.add('active');
      
      // This ensures panels don't show up hidden when they should be visible
      targetPanel.style.visibility = 'visible';
      targetPanel.style.opacity = '1';
      
      console.log(`Set panel ${targetPanel.id} to active, display: ${targetPanel.style.display}`);
      
      // Special handling for HTML panel - we need to make sure the content is properly shown
      if (panelId === 'html') {
        console.log('HTML panel activated, checking containers');
        
        // If we have an active component, make sure its container is visible
        const activeComponent = window.tektonUI?.activeComponent;
        if (activeComponent) {
          // For Rhetor and Budget, the container completely replaces the panel contents
          // So if we have these components active, we don't need to do anything else
          if (['rhetor', 'budget'].includes(activeComponent)) {
            console.log(`Special component ${activeComponent} is active, no additional container management needed`);
          } else {
            // For other components with containers, show the appropriate container
            const activeContainer = document.getElementById(`${activeComponent}-container`);
            if (activeContainer) {
              console.log(`Found active container for ${activeComponent}, showing it`);
              activeContainer.style.display = 'block';
              activeContainer.style.visibility = 'visible';
            }
          }
        }
      }
    } else {
      console.error(`Panel not found: ${panelId}-panel`);
    }
    
    // Update state
    this.activePanel = panelId;
    if (window.tektonUI) {
      window.tektonUI.activePanel = panelId;
    }
    
    // Auto-focus on input if terminal panel
    if (panelId === 'terminal') {
      const terminalInput = document.getElementById('simple-terminal-input');
      if (terminalInput) {
        console.log('Focusing terminal input');
        setTimeout(() => {
          terminalInput.focus();
        }, 100);
      }
    }
  }
  
  /**
   * Auto-resize a textarea input based on its content
   * @param {HTMLElement} input - The textarea element to resize
   */
  autoResizeTextarea(input) {
    if (!input) return;
    
    const minHeight = 36; // Minimum height in pixels
    const maxHeight = 200; // Maximum height before scrolling
    
    // Reset height to get proper scrollHeight
    input.style.height = 'auto';
    
    // Calculate new height within min/max bounds
    const newHeight = Math.min(Math.max(input.scrollHeight, minHeight), maxHeight);
    
    // Set the height
    input.style.height = newHeight + 'px';
    
    // Add scrolling if content exceeds max height
    if (input.scrollHeight > maxHeight) {
      input.style.overflowY = 'auto';
    } else {
      input.style.overflowY = 'hidden';
    }
  }
  
  /**
   * Create a standardized HTML container for a component
   * @param {string} componentId - ID of the component
   * @param {HTMLElement} parentElement - Parent element to append to
   * @returns {HTMLElement} The created container
   */
  createComponentContainer(componentId, parentElement) {
    if (!componentId || !parentElement) {
      console.error('Cannot create component container: missing required parameters');
      return null;
    }
    
    // Create container
    const container = document.createElement('div');
    container.id = `${componentId}-container`;
    container.className = 'component-container';
    container.style.height = '100%';
    container.style.width = '100%';
    container.style.overflow = 'auto';
    container.setAttribute('data-component', componentId);
    
    // Append to parent
    parentElement.appendChild(container);
    
    return container;
  }
  
  /**
   * Show a notification message to the user
   * @param {string} message - The message to display
   * @param {string} type - Message type: 'info', 'success', 'warning', or 'error'
   * @param {number} duration - Duration in milliseconds (default 3000)
   */
  showNotification(message, type = 'info', duration = 3000) {
    if (!message) return;
    
    // Create notification element if it doesn't exist
    let notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
      notificationContainer = document.createElement('div');
      notificationContainer.id = 'notification-container';
      notificationContainer.style.position = 'fixed';
      notificationContainer.style.top = '20px';
      notificationContainer.style.right = '20px';
      notificationContainer.style.zIndex = '9999';
      document.body.appendChild(notificationContainer);
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style based on type
    const colors = {
      info: { bg: '#2196F3', text: 'white' },
      success: { bg: '#4CAF50', text: 'white' },
      warning: { bg: '#FF9800', text: 'black' },
      error: { bg: '#F44336', text: 'white' }
    };
    
    const typeColor = colors[type] || colors.info;
    
    // Apply styles
    Object.assign(notification.style, {
      padding: '12px 16px',
      marginBottom: '10px',
      borderRadius: '4px',
      backgroundColor: typeColor.bg,
      color: typeColor.text,
      boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
      opacity: '0',
      transition: 'opacity 0.3s ease-in-out'
    });
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
      notification.style.opacity = '1';
    }, 10);
    
    // Auto remove after duration
    setTimeout(() => {
      notification.style.opacity = '0';
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, duration);
  }
}

// Create global instance
window.uiUtils = new UIUtils().init();

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = window.uiUtils;
}