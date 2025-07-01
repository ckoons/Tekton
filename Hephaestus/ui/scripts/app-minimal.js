/**
 * app-minimal.js - Minimal JavaScript for CSS-First Architecture
 * 
 * Handles only essential functionality:
 * 1. Component visibility based on URL hash
 * 2. WebSocket connection for real-time updates
 * 3. Chat input handling
 * 4. Health monitoring
 */

console.log('[app-minimal] Loading minimal JavaScript handler');

// Component visibility handler
function handleComponentVisibility() {
    const hash = window.location.hash.slice(1); // Remove the #
    const components = document.querySelectorAll('.component');
    
    // Hide all components
    components.forEach(comp => {
        comp.style.display = 'none';
    });
    
    if (hash && document.getElementById(hash)) {
        // Show targeted component
        document.getElementById(hash).style.display = 'block';
    } else {
        // Show numa by default when no hash
        const numa = document.getElementById('numa');
        if (numa) {
            numa.style.display = 'block';
        }
    }
}

// Handle hash changes
window.addEventListener('hashchange', handleComponentVisibility);

// Handle initial load
window.addEventListener('DOMContentLoaded', () => {
    console.log('[app-minimal] DOM loaded, setting up handlers');
    
    // Set initial component visibility
    handleComponentVisibility();
    
    // Setup chat input handlers
    setupChatHandlers();
    
    // Start health monitoring
    setupHealthMonitoring();
    
    // Setup WebSocket connection
    setupWebSocket();
});

// Handle page load with existing hash
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', handleComponentVisibility);
} else {
    handleComponentVisibility();
}

// Chat input handler - delegate to all chat inputs
function setupChatHandlers() {
    document.addEventListener('keypress', (e) => {
        if (e.target.classList.contains('chat-input') && e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const componentName = e.target.closest('[data-tekton-component]')?.dataset.tektonComponent;
            if (componentName) {
                console.log(`[app-minimal] Chat input from ${componentName}:`, e.target.value);
                // Component-specific handlers will process the actual chat
            }
        }
    });
}

// Health monitoring
const COMPONENT_PORTS = {
    numa: 45001,
    tekton: 8008,
    prometheus: 8007,
    telos: 8006,
    metis: 8009,
    harmonia: 8010,
    synthesis: 8011,
    athena: 8012,
    sophia: 8013,
    noesis: 8014,
    engram: 8015,
    apollo: 8016,
    rhetor: 8003,
    budget: 8017,
    hermes: 8001,
    ergon: 8002,
    terma: 8004,
    profile: null,
    settings: null
};

function setupHealthMonitoring() {
    // Check health immediately
    checkHealth();
    
    // Then check every 15 seconds
    setInterval(checkHealth, 15000);
}

async function checkHealth() {
    for (const [component, port] of Object.entries(COMPONENT_PORTS)) {
        if (!port) continue;
        
        try {
            const response = await fetch(`http://localhost:${port}/health`, {
                method: 'GET',
                mode: 'cors',
                cache: 'no-cache'
            });
            
            if (response.ok) {
                updateStatusIndicator(component, 'active');
            } else {
                updateStatusIndicator(component, 'inactive');
            }
        } catch (error) {
            updateStatusIndicator(component, 'inactive');
        }
    }
}

function updateStatusIndicator(component, status) {
    const indicator = document.querySelector(`[data-component="${component}"] .status-indicator`);
    if (indicator) {
        indicator.setAttribute('data-status', status);
    }
}

// WebSocket connection
let ws = null;
let reconnectTimeout = null;

function setupWebSocket() {
    try {
        ws = new WebSocket('ws://localhost:8080/ws');
        
        ws.onopen = () => {
            console.log('[app-minimal] WebSocket connected');
            if (reconnectTimeout) {
                clearTimeout(reconnectTimeout);
                reconnectTimeout = null;
            }
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('[app-minimal] WebSocket message:', data);
                
                // Route messages to appropriate handlers
                if (data.type === 'health_update') {
                    updateStatusIndicator(data.component, data.status);
                } else if (data.type === 'chat_message') {
                    // Component-specific handlers will process chat messages
                    const event = new CustomEvent('tekton-chat-message', {
                        detail: data,
                        bubbles: true
                    });
                    document.dispatchEvent(event);
                }
            } catch (error) {
                console.error('[app-minimal] Error parsing WebSocket message:', error);
            }
        };
        
        ws.onerror = (error) => {
            console.error('[app-minimal] WebSocket error:', error);
        };
        
        ws.onclose = () => {
            console.log('[app-minimal] WebSocket disconnected');
            // Attempt to reconnect after 5 seconds
            reconnectTimeout = setTimeout(() => {
                console.log('[app-minimal] Attempting WebSocket reconnection...');
                setupWebSocket();
            }, 5000);
        };
    } catch (error) {
        console.error('[app-minimal] Failed to setup WebSocket:', error);
    }
}

// Theme handling
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme-base', theme);
}

// Export for use by other scripts
window.appMinimal = {
    handleComponentVisibility,
    updateStatusIndicator,
    checkHealth,
    applyTheme
};

console.log('[app-minimal] Initialization complete');