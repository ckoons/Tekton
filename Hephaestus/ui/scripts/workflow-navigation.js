/**
 * Workflow Navigation Integration
 * 
 * Adds workflow endpoint triggers to Hephaestus navigation
 * using CSS-first approach without DOM manipulation
 */

console.log('[Workflow] Loading workflow navigation integration');

// Import workflow handler
if (!window.WorkflowHandler) {
  // Load the workflow handler if not already loaded
  const script = document.createElement('script');
  script.src = '/shared/workflow/workflow-handler.js';
  document.head.appendChild(script);
}

// Wait for DOM and workflow handler to be ready
document.addEventListener('DOMContentLoaded', function() {
  console.log('[Workflow] Initializing workflow navigation');
  
  // Components that support workflow
  const workflowComponents = [
    'telos', 'prometheus', 'metis', 
    'harmonia', 'synthesis', 'tekton'
  ];
  
  // Add click event listeners to nav items
  const navItems = document.querySelectorAll('.nav-item[data-component]');
  
  navItems.forEach(item => {
    const component = item.getAttribute('data-component');
    
    // Only add workflow trigger for supported components
    if (workflowComponents.includes(component)) {
      // Find the label within the nav item
      const label = item.querySelector('label');
      
      if (label) {
        label.addEventListener('click', async (e) => {
          // Don't prevent default - let CSS navigation work
          
          // Small delay to ensure component loads first
          setTimeout(async () => {
            console.log(`[Workflow] Triggering workflow check for ${component}`);
            
            try {
              // Use the global workflow trigger function
              if (window.triggerWorkflowCheck) {
                await window.triggerWorkflowCheck(component);
              } else if (window.WorkflowHandler) {
                // Fallback to direct handler
                const handler = new WorkflowHandler(component);
                const result = await handler.lookForWork();
                
                console.log(`[Workflow] ${component} check result:`, result);
                
                // Dispatch event for component to handle
                if (result.status === 'success' && result.found > 0) {
                  const event = new CustomEvent('workflow:work-found', {
                    detail: {
                      component: component,
                      count: result.found,
                      items: result.items
                    }
                  });
                  document.dispatchEvent(event);
                }
              }
            } catch (error) {
              console.error(`[Workflow] Error checking ${component}:`, error);
            }
          }, 100); // 100ms delay for component to initialize
        });
        
        // Add visual indicator for workflow-enabled components
        item.classList.add('workflow-enabled');
      }
    }
  });
  
  // Listen for workflow events and update UI accordingly
  document.addEventListener('workflow:work-found', (event) => {
    const { component, count } = event.detail;
    console.log(`[Workflow] Work found for ${component}: ${count} items`);
    
    // Update component's status indicator using CSS
    const statusIndicator = document.querySelector(`.status-indicator[data-component="${component}"]`);
    if (statusIndicator) {
      // Add a data attribute that CSS can use
      statusIndicator.setAttribute('data-work-count', count);
      statusIndicator.classList.add('has-work');
    }
  });
  
  // Add CSS for workflow indicators
  if (!document.getElementById('workflow-nav-styles')) {
    const style = document.createElement('style');
    style.id = 'workflow-nav-styles';
    style.textContent = `
      /* Workflow-enabled components get a subtle indicator */
      .nav-item.workflow-enabled .nav-label::after {
        content: " ●";
        font-size: 0.6em;
        opacity: 0.3;
        vertical-align: super;
      }
      
      /* Components with pending work show a badge */
      .status-indicator.has-work::after {
        content: attr(data-work-count);
        position: absolute;
        top: -4px;
        right: -4px;
        background: #ff6b6b;
        color: white;
        font-size: 10px;
        font-weight: bold;
        padding: 2px 4px;
        border-radius: 10px;
        min-width: 16px;
        text-align: center;
      }
      
      /* Ensure status indicator is positioned for badge */
      .status-indicator.has-work {
        position: relative;
      }
    `;
    document.head.appendChild(style);
  }
  
  console.log('[Workflow] Workflow navigation initialized');
});

// Export for debugging
window.workflowNavigation = {
  checkComponent: async (component) => {
    if (window.triggerWorkflowCheck) {
      return await window.triggerWorkflowCheck(component);
    }
    return null;
  }
};