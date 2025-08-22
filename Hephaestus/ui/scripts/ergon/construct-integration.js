/**
 * Construct Integration for Ergon Component
 * 
 * Handles the bilingual (JSON/text) Construct interface for CI solution composition
 */

// Global construct state
window.ErgonConstruct = {
    currentWorkspace: null,
    lastResponse: null,
    isProcessing: false,
    chatHistory: []
};

/**
 * Initialize Construct interface
 */
function ergon_initConstruct() {
    console.log('[ERGON-CONSTRUCT] Initializing Construct interface...');
    
    // Set up event listeners
    const buildButton = document.getElementById('construct-build-btn');
    const validateButton = document.getElementById('construct-validate-btn');
    const testButton = document.getElementById('construct-test-btn');
    const publishButton = document.getElementById('construct-publish-btn');
    const clearButton = document.getElementById('construct-clear-btn');
    const chatInput = document.getElementById('construct-chat-input');
    
    if (buildButton) {
        buildButton.addEventListener('click', ergon_constructBuild);
    }
    if (validateButton) {
        validateButton.addEventListener('click', ergon_constructValidate);
    }
    if (testButton) {
        testButton.addEventListener('click', ergon_constructTest);
    }
    if (publishButton) {
        publishButton.addEventListener('click', ergon_constructPublish);
    }
    if (clearButton) {
        clearButton.addEventListener('click', ergon_constructClear);
    }
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                ergon_constructBuild();
            }
        });
    }
    
    // Update initial state
    ergon_updateConstructState('ready', null);
    console.log('[ERGON-CONSTRUCT] Construct interface initialized');
}

/**
 * Build/compose solution from chat input
 */
async function ergon_constructBuild() {
    const input = document.getElementById('construct-chat-input');
    const message = input.value.trim();
    
    if (!message) {
        ergon_showConstructMessage('Please enter a description or JSON request.', 'warning');
        return;
    }
    
    try {
        ergon_updateConstructState('processing', null);
        ergon_showConstructMessage(`Processing: ${message}`, 'info');
        
        // Send to Construct system
        const response = await ergon_sendToConstruct(message);
        
        // Update UI with response
        ergon_handleConstructResponse(response);
        
        // Clear input
        input.value = '';
        
    } catch (error) {
        console.error('[ERGON-CONSTRUCT] Build failed:', error);
        ergon_showConstructMessage(`Error: ${error.message}`, 'error');
        ergon_updateConstructState('error', null);
    }
}

/**
 * Validate current composition
 */
async function ergon_constructValidate() {
    if (!window.ErgonConstruct.currentWorkspace) {
        ergon_showConstructMessage('No workspace to validate. Create a composition first.', 'warning');
        return;
    }
    
    try {
        ergon_updateConstructState('processing', null);
        
        const request = {
            action: 'validate',
            workspace_id: window.ErgonConstruct.currentWorkspace,
            checks: ['connections', 'dependencies', 'standards'],
            sender_id: 'hephaestus-ui'
        };
        
        const response = await ergon_sendToConstruct(JSON.stringify(request));
        ergon_handleConstructResponse(response);
        
    } catch (error) {
        console.error('[ERGON-CONSTRUCT] Validation failed:', error);
        ergon_showConstructMessage(`Validation error: ${error.message}`, 'error');
        ergon_updateConstructState('error', null);
    }
}

/**
 * Test current composition
 */
async function ergon_constructTest() {
    if (!window.ErgonConstruct.currentWorkspace) {
        ergon_showConstructMessage('No workspace to test. Create a composition first.', 'warning');
        return;
    }
    
    try {
        ergon_updateConstructState('processing', null);
        
        const request = {
            action: 'test',
            workspace_id: window.ErgonConstruct.currentWorkspace,
            sandbox_config: {
                timeout: 300
            },
            sender_id: 'hephaestus-ui'
        };
        
        const response = await ergon_sendToConstruct(JSON.stringify(request));
        ergon_handleConstructResponse(response);
        
    } catch (error) {
        console.error('[ERGON-CONSTRUCT] Test failed:', error);
        ergon_showConstructMessage(`Test error: ${error.message}`, 'error');
        ergon_updateConstructState('error', null);
    }
}

/**
 * Publish current composition
 */
async function ergon_constructPublish() {
    if (!window.ErgonConstruct.currentWorkspace) {
        ergon_showConstructMessage('No workspace to publish. Create a composition first.', 'warning');
        return;
    }
    
    try {
        ergon_updateConstructState('processing', null);
        
        const request = {
            action: 'publish',
            workspace_id: window.ErgonConstruct.currentWorkspace,
            metadata: {
                name: 'UI Composition',
                version: '1.0.0',
                description: 'Created via Hephaestus UI'
            },
            sender_id: 'hephaestus-ui'
        };
        
        const response = await ergon_sendToConstruct(JSON.stringify(request));
        ergon_handleConstructResponse(response);
        
    } catch (error) {
        console.error('[ERGON-CONSTRUCT] Publish failed:', error);
        ergon_showConstructMessage(`Publish error: ${error.message}`, 'error');
        ergon_updateConstructState('error', null);
    }
}

/**
 * Clear current workspace
 */
function ergon_constructClear() {
    window.ErgonConstruct.currentWorkspace = null;
    window.ErgonConstruct.lastResponse = null;
    window.ErgonConstruct.chatHistory = [];
    
    // Clear UI elements
    const jsonState = document.getElementById('construct-json-state');
    const composition = document.getElementById('construct-composition');
    const activity = document.getElementById('construct-activity');
    const input = document.getElementById('construct-chat-input');
    
    if (jsonState) jsonState.textContent = '{}';
    if (composition) composition.innerHTML = '<div class="ergon__empty-state">No composition yet</div>';
    if (activity) activity.innerHTML = '';
    if (input) input.value = '';
    
    ergon_updateConstructState('ready', null);
    ergon_showConstructMessage('Workspace cleared', 'info');
}

/**
 * Send message to Construct system
 */
async function ergon_sendToConstruct(message) {
    const apiUrl = window.ergonUrl ? window.ergonUrl('/api/v1/construct/process') : '/api/v1/construct/process';
    
    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            sender_id: 'hephaestus-ui'
        })
    });
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
}

/**
 * Handle response from Construct system
 */
function ergon_handleConstructResponse(response) {
    console.log('[ERGON-CONSTRUCT] Response:', response);
    
    window.ErgonConstruct.lastResponse = response;
    
    // Try to parse as JSON if it's a string
    let jsonResponse = response;
    if (typeof response === 'string') {
        try {
            jsonResponse = JSON.parse(response);
        } catch (e) {
            // Response is natural text - show it as message
            ergon_showConstructMessage(response, 'success');
            ergon_updateConstructState('ready', null);
            return;
        }
    }
    
    // Handle JSON response
    if (jsonResponse.workspace_id) {
        window.ErgonConstruct.currentWorkspace = jsonResponse.workspace_id;
    }
    
    // Update JSON state display
    ergon_updateJsonState(jsonResponse);
    
    // Update composition display
    if (jsonResponse.composition) {
        ergon_updateCompositionDisplay(jsonResponse.composition);
    }
    
    // Show status message
    const status = jsonResponse.status || 'completed';
    const message = jsonResponse.message || `Operation ${status}`;
    ergon_showConstructMessage(message, status === 'error' ? 'error' : 'success');
    
    // Add to activity log
    ergon_addToActivityLog(jsonResponse);
    
    // Update state
    ergon_updateConstructState(status === 'error' ? 'error' : 'ready', jsonResponse);
}

/**
 * Update JSON state display
 */
function ergon_updateJsonState(data) {
    const jsonState = document.getElementById('construct-json-state');
    if (jsonState) {
        jsonState.textContent = JSON.stringify(data, null, 2);
    }
}

/**
 * Update composition display
 */
function ergon_updateCompositionDisplay(composition) {
    const display = document.getElementById('construct-composition');
    if (!display) return;
    
    // Build visual representation of composition
    let html = '<div class="ergon__composition-view">';
    
    // Show components
    if (composition.components && composition.components.length > 0) {
        html += '<div class="ergon__composition-section"><h4>Components</h4><ul>';
        composition.components.forEach(comp => {
            html += `<li><strong>${comp.alias || comp.registry_id}</strong> (${comp.registry_id})</li>`;
        });
        html += '</ul></div>';
    }
    
    // Show connections
    if (composition.connections && composition.connections.length > 0) {
        html += '<div class="ergon__composition-section"><h4>Connections</h4><ul>';
        composition.connections.forEach(conn => {
            html += `<li>${conn.from} → ${conn.to}</li>`;
        });
        html += '</ul></div>';
    }
    
    html += '</div>';
    display.innerHTML = html;
}

/**
 * Add entry to activity log
 */
function ergon_addToActivityLog(data) {
    const activity = document.getElementById('construct-activity');
    if (!activity) return;
    
    const timestamp = new Date().toLocaleTimeString();
    const action = data.action || 'unknown';
    const status = data.status || 'completed';
    
    const entry = document.createElement('div');
    entry.className = `ergon__activity-entry ergon__activity-entry--${status}`;
    entry.innerHTML = `
        <div class="ergon__activity-time">${timestamp}</div>
        <div class="ergon__activity-action">${action}</div>
        <div class="ergon__activity-status">${status}</div>
    `;
    
    activity.insertBefore(entry, activity.firstChild);
    
    // Keep only last 10 entries
    while (activity.children.length > 10) {
        activity.removeChild(activity.lastChild);
    }
}

/**
 * Show message to user
 */
function ergon_showConstructMessage(message, type = 'info') {
    console.log(`[ERGON-CONSTRUCT] ${type.toUpperCase()}: ${message}`);
    
    // You could enhance this to show a toast notification
    // For now, we'll add it to the activity log
    const activity = document.getElementById('construct-activity');
    if (activity) {
        const timestamp = new Date().toLocaleTimeString();
        const entry = document.createElement('div');
        entry.className = `ergon__activity-entry ergon__activity-entry--${type}`;
        entry.innerHTML = `
            <div class="ergon__activity-time">${timestamp}</div>
            <div class="ergon__activity-action">system</div>
            <div class="ergon__activity-message">${message}</div>
        `;
        activity.insertBefore(entry, activity.firstChild);
    }
}

/**
 * Update construct state
 */
function ergon_updateConstructState(state, data) {
    window.ErgonConstruct.isProcessing = (state === 'processing');
    
    // Update button states
    const buttons = ['construct-build-btn', 'construct-validate-btn', 'construct-test-btn', 'construct-publish-btn'];
    buttons.forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.disabled = (state === 'processing');
            if (state === 'processing') {
                btn.textContent = btn.textContent.replace(/^(Validate|Test|Publish|Build)/, '$1ing...');
            } else {
                // Restore original text
                const originalText = {
                    'construct-build-btn': 'Build',
                    'construct-validate-btn': 'Validate', 
                    'construct-test-btn': 'Test',
                    'construct-publish-btn': 'Publish'
                };
                if (originalText[id]) {
                    btn.textContent = originalText[id];
                }
            }
        }
    });
    
    // Update workspace availability buttons
    const workspaceButtons = ['construct-validate-btn', 'construct-test-btn', 'construct-publish-btn'];
    const hasWorkspace = !!window.ErgonConstruct.currentWorkspace;
    
    workspaceButtons.forEach(id => {
        const btn = document.getElementById(id);
        if (btn && state !== 'processing') {
            btn.disabled = !hasWorkspace;
        }
    });
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for other initialization to complete
    setTimeout(ergon_initConstruct, 100);
});

// Export functions for global access
window.ergon_initConstruct = ergon_initConstruct;
window.ergon_constructBuild = ergon_constructBuild;
window.ergon_constructValidate = ergon_constructValidate;
window.ergon_constructTest = ergon_constructTest;
window.ergon_constructPublish = ergon_constructPublish;
window.ergon_constructClear = ergon_constructClear;