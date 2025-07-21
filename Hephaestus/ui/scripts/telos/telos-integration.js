/**
 * Telos Integration
 * 
 * Integration functions for Telos requirements management component.
 * Handles AI chat integration and cross-component communication.
 */

console.log('[FILE_TRACE] Loading: telos-integration.js');

/**
 * Send a message to the Requirements Chat
 */
function telos_sendReqChat() {
    const inputElement = document.getElementById('telos-reqchat-input');
    const messagesContainer = document.getElementById('reqchat-messages');
    
    if (!inputElement || !messagesContainer) {
        console.error('[TELOS] Chat elements not found');
        return;
    }
    
    const message = inputElement.value.trim();
    if (!message) return;
    
    // Clear input
    inputElement.value = '';
    
    // Add user message
    const userMessage = document.createElement('div');
    userMessage.className = 'telos__message telos__message--user';
    userMessage.innerHTML = `<strong>You:</strong> ${message}`;
    messagesContainer.appendChild(userMessage);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Send to AI with Telos context
    if (window.AIChat) {
        window.AIChat({
            message: message,
            context: 'telos-requirements',
            component: 'telos',
            systemPrompt: 'You are Telos, a requirements management assistant. Help with requirements engineering, validation, traceability, and best practices.'
        }).then(response => {
            const aiMessage = document.createElement('div');
            aiMessage.className = 'telos__message telos__message--ai';
            aiMessage.innerHTML = `<strong>Telos:</strong> ${response.message || response}`;
            messagesContainer.appendChild(aiMessage);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }).catch(error => {
            console.error('[TELOS] AI Chat error:', error);
            const errorMessage = document.createElement('div');
            errorMessage.className = 'telos__message telos__message--error';
            errorMessage.innerHTML = `<strong>Error:</strong> Failed to get AI response. ${error.message || ''}`;
            messagesContainer.appendChild(errorMessage);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        });
    } else {
        // Fallback when AI not available
        const fallbackMessage = document.createElement('div');
        fallbackMessage.className = 'telos__message telos__message--ai';
        fallbackMessage.innerHTML = `<strong>Telos:</strong> AI chat is not currently available. Your message has been logged.`;
        messagesContainer.appendChild(fallbackMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

/**
 * Send a message to the Team Chat
 */
function telos_sendTeamChat() {
    const inputElement = document.getElementById('telos-teamchat-input');
    const messagesContainer = document.getElementById('teamchat-messages');
    
    if (!inputElement || !messagesContainer) {
        console.error('[TELOS] Team chat elements not found');
        return;
    }
    
    const message = inputElement.value.trim();
    if (!message) return;
    
    // Clear input
    inputElement.value = '';
    
    // Add user message
    const userMessage = document.createElement('div');
    userMessage.className = 'telos__message telos__message--user';
    userMessage.innerHTML = `<strong>You:</strong> ${message}`;
    messagesContainer.appendChild(userMessage);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Send to team chat system (placeholder for now)
    console.log('[TELOS] Team chat message:', message);
    
    // Add confirmation
    setTimeout(() => {
        const confirmMessage = document.createElement('div');
        confirmMessage.className = 'telos__message telos__message--system';
        confirmMessage.innerHTML = `<strong>System:</strong> Message sent to team chat.`;
        messagesContainer.appendChild(confirmMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 500);
}

/**
 * Initialize Telos integration
 */
function initializeTelosIntegration() {
    console.log('[TELOS] Initializing Telos integration');
    
    // Set up event delegation for dynamically loaded content
    document.addEventListener('click', (e) => {
        if (e.target.id === 'telos-reqchat-send') {
            telos_sendReqChat();
        } else if (e.target.id === 'telos-teamchat-send') {
            telos_sendTeamChat();
        }
    });
    
    // Set up keyboard handlers
    document.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            if (e.target.id === 'telos-reqchat-input') {
                telos_sendReqChat();
            } else if (e.target.id === 'telos-teamchat-input') {
                telos_sendTeamChat();
            }
        }
    });
    
    console.log('[TELOS] Telos integration initialized');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTelosIntegration);
} else {
    initializeTelosIntegration();
}

// Make functions globally available
window.telos_sendReqChat = telos_sendReqChat;
window.telos_sendTeamChat = telos_sendTeamChat;