// HEPHAESTUS UI - MINIMAL JAVASCRIPT
// This replaces the complex loading system with a simple, CSS-first approach
// Only handles: WebSocket, Chat Input, and Health Checks

// Component port mapping for health checks
const COMPONENT_PORTS = {
  numa: 7001,
  tekton: 7002,
  prometheus: 7003,
  telos: 7004,
  metis: 7005,
  harmonia: 7006,
  synthesis: 7007,
  athena: 7008,
  sophia: 7009,
  noesis: 7010,
  engram: 7011,
  apollo: 7012,
  rhetor: 7013,
  hermes: 7015,
  ergon: 7016,
  terma: 7017,
  codex: 7018,
  budget: 7019
};

// WebSocket connection
let ws = null;
const messageHandlers = new Map();

function connectWebSocket() {
  try {
    ws = new WebSocket('ws://localhost:8080/ws');
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      document.body.setAttribute('data-ws-connected', 'true');
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      document.body.setAttribute('data-ws-connected', 'false');
      // Reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const handler = messageHandlers.get(data.target);
        if (handler) {
          handler(data);
        } else {
          console.log('No handler for target:', data.target);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  } catch (error) {
    console.error('Error creating WebSocket:', error);
    setTimeout(connectWebSocket, 3000);
  }
}

// Send message via WebSocket
function sendMessage(message) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message));
  } else {
    console.warn('WebSocket not connected');
  }
}

// Chat input handling - single delegated handler
document.addEventListener('keypress', (e) => {
  // Check if it's a chat input
  if (e.target.classList.contains('chat-input') || 
      e.target.id.includes('chat-input') ||
      e.target.hasAttribute('data-tekton-input')) {
    
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      
      const input = e.target;
      const message = input.value.trim();
      
      if (message) {
        // Find component name from input ID or data attribute
        let component = input.dataset.component || 
                       input.id.split('-')[0] || 
                       input.closest('[data-tekton-component]')?.dataset.tektonComponent;
        
        if (component) {
          // Add message to chat display
          const messagesContainer = document.querySelector(`#${component}-messages, #${component}-companion-messages`);
          if (messagesContainer) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'chat-message user';
            messageDiv.innerHTML = `<strong>You:</strong> ${message}`;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
          }
          
          // Send via WebSocket
          sendMessage({
            type: 'CHAT',
            source: 'UI',
            target: component.toUpperCase(),
            timestamp: new Date().toISOString(),
            payload: { message }
          });
          
          // Clear input
          input.value = '';
        }
      }
    }
  }
});

// Health check for glowing dots
function checkHealth() {
  Object.entries(COMPONENT_PORTS).forEach(([component, port]) => {
    fetch(`http://localhost:${port}/health`)
      .then(response => {
        if (response.ok) {
          // Update all status indicators for this component
          const indicators = document.querySelectorAll(
            `[data-component="${component}"] .status-indicator, ` +
            `.${component}__status-indicator`
          );
          indicators.forEach(indicator => {
            indicator.classList.add('connected');
            indicator.setAttribute('data-status', 'connected');
          });
          
          // Update status text if exists
          const statusText = document.querySelector(`.${component}__status-text`);
          if (statusText) {
            statusText.textContent = 'Connected';
          }
        }
      })
      .catch(() => {
        // Component not available
        const indicators = document.querySelectorAll(
          `[data-component="${component}"] .status-indicator, ` +
          `.${component}__status-indicator`
        );
        indicators.forEach(indicator => {
          indicator.classList.remove('connected');
          indicator.setAttribute('data-status', 'inactive');
        });
        
        const statusText = document.querySelector(`.${component}__status-text`);
        if (statusText) {
          statusText.textContent = 'Offline';
        }
      });
  });
}

// Register component message handlers
function registerHandlers() {
  // Generic handler for all components
  const componentNames = Object.keys(COMPONENT_PORTS);
  
  componentNames.forEach(component => {
    messageHandlers.set(component.toUpperCase(), (data) => {
      // Find the appropriate messages container
      const containers = [
        document.getElementById(`${component}-messages`),
        document.getElementById(`${component}-companion-messages`),
        document.getElementById(`${component}-team-messages`)
      ].filter(Boolean);
      
      containers.forEach(container => {
        if (container) {
          const messageDiv = document.createElement('div');
          messageDiv.className = 'chat-message assistant';
          messageDiv.innerHTML = `<strong>${component}:</strong> ${data.payload.message || data.payload.response || 'Response received'}`;
          container.appendChild(messageDiv);
          container.scrollTop = container.scrollHeight;
        }
      });
    });
  });
}

// Handle component visibility based on URL hash
function handleHashChange() {
  const hash = window.location.hash.slice(1) || 'numa'; // Default to numa
  
  // Update nav item states
  document.querySelectorAll('.nav-item').forEach(item => {
    if (item.getAttribute('data-component') === hash) {
      item.classList.add('active');
      item.setAttribute('data-tekton-state', 'active');
    } else {
      item.classList.remove('active');
      item.setAttribute('data-tekton-state', 'inactive');
    }
  });
  
  // Update component visibility states
  document.querySelectorAll('.component').forEach(component => {
    const componentId = component.id;
    if (componentId === hash) {
      component.setAttribute('data-tekton-visibility', 'visible');
      component.setAttribute('data-tekton-state', 'active');
    } else {
      component.setAttribute('data-tekton-visibility', 'hidden');
      component.setAttribute('data-tekton-state', 'inactive');
    }
  });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('Minimal Hephaestus UI initializing...');
  
  // Connect WebSocket
  connectWebSocket();
  
  // Register message handlers
  registerHandlers();
  
  // Start health checks
  checkHealth();
  setInterval(checkHealth, 15000);
  
  // Handle initial hash
  handleHashChange();
  
  // Listen for hash changes
  window.addEventListener('hashchange', handleHashChange);
  
  // Update navigation links to use hash navigation
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const component = item.getAttribute('data-component');
      if (component) {
        window.location.hash = component;
      }
    });
  });
  
  // If no hash, default to numa
  if (!window.location.hash) {
    window.location.hash = 'numa';
  }
  
  console.log('Minimal Hephaestus UI initialized');
});

// Generic send chat function for all components
window.sendComponentChat = function(componentName) {
  const input = document.getElementById(`${componentName}-chat-input`);
  const message = input.value.trim();
  
  if (!message) return;
  
  // Find the active messages container for this component
  let messagesContainer = null;
  
  // Check for tabbed components (like numa with companion/team tabs)
  const companionMessages = document.getElementById(`${componentName}-companion-messages`);
  const teamMessages = document.getElementById(`${componentName}-team-messages`);
  
  if (companionMessages && companionMessages.offsetParent !== null) {
    messagesContainer = companionMessages;
  } else if (teamMessages && teamMessages.offsetParent !== null) {
    messagesContainer = teamMessages;
  } else {
    // Simple components with single message area
    messagesContainer = document.getElementById(`${componentName}-messages`);
  }
  
  if (!messagesContainer) {
    console.error(`No messages container found for ${componentName}`);
    return;
  }
  
  // Add user message
  const userMessageDiv = document.createElement('div');
  userMessageDiv.className = 'chat-message user';
  userMessageDiv.innerHTML = `<strong>You:</strong> ${message}`;
  messagesContainer.appendChild(userMessageDiv);
  
  // Clear input
  input.value = '';
  
  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  
  // Send via WebSocket
  sendMessage({
    type: 'CHAT',
    source: 'UI',
    target: componentName.toUpperCase(),
    timestamp: new Date().toISOString(),
    payload: { message }
  });
};

// Create component-specific chat functions
['numa', 'rhetor', 'athena', 'hermes', 'sophia', 'noesis', 'apollo', 'metis', 
 'prometheus', 'harmonia', 'synthesis', 'ergon', 'terma', 'engram', 'codex',
 'tekton', 'telos', 'budget'].forEach(component => {
  window[`${component}_sendChat`] = () => window.sendComponentChat(component);
});

// Expose minimal API for components that need it
window.tektonMinimal = {
  sendMessage,
  checkHealth,
  sendComponentChat
};