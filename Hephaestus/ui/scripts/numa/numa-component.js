console.log('[FILE_TRACE] Loading: numa-component.js');
// Numa Component JavaScript - Following Rhetor's minimal pattern

window.NumaComponent = {
    apiUrl: window.NUMA_URL || 'http://localhost:8016',
    
    init: function() {
        console.log('Initializing Numa component');
        this.setupEventListeners();
        this.checkHealth();
    },
    
    setupEventListeners: function() {
        // Tab switching handled by CSS radio buttons (like Rhetor)
        
        // Companion chat
        const companionInput = document.getElementById('numa-companion-input');
        const companionSend = document.getElementById('numa-companion-send');
        
        if (companionInput && companionSend) {
            companionSend.addEventListener('click', () => this.sendCompanionMessage());
            companionInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendCompanionMessage();
            });
        }
        
        // Team chat
        const teamInput = document.getElementById('numa-team-input');
        const teamSend = document.getElementById('numa-team-send');
        
        if (teamInput && teamSend) {
            teamSend.addEventListener('click', () => this.sendTeamMessage());
            teamInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendTeamMessage();
            });
        }
    },
    
    // Tab switching is handled by CSS radio buttons (like Rhetor)
    
    checkHealth: async function() {
        try {
            const response = await fetch(`${this.apiUrl}/health`);
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.updateStatus('active', 'Connected');
                document.getElementById('numa-status').textContent = 'Active';
                
                // Update AI status based on environment
                const statusResponse = await fetch(`${this.apiUrl}/api/status`);
                const statusData = await statusResponse.json();
                document.getElementById('numa-ai-status').textContent = 
                    statusData.ai_enabled ? 'Enabled' : 'Disabled';
            }
        } catch (error) {
            console.error('Numa health check failed:', error);
            this.updateStatus('error', 'Disconnected');
            document.getElementById('numa-status').textContent = 'Offline';
        }
    },
    
    updateStatus: function(status, text) {
        const statusIndicator = document.querySelector('#numa-container .numa__status-indicator');
        const statusText = document.querySelector('#numa-container .numa__status-text');
        
        if (statusIndicator) statusIndicator.setAttribute('data-status', status);
        if (statusText) statusText.textContent = text;
    },
    
    sendCompanionMessage: async function() {
        const input = document.getElementById('numa-companion-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        this.addMessage('companion', message, 'user');
        input.value = '';
        
        try {
            const response = await fetch(`${this.apiUrl}/api/companion-chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    user_id: 'default'
                })
            });
            
            const data = await response.json();
            this.addMessage('companion', data.response, 'ai');
        } catch (error) {
            console.error('Failed to send companion message:', error);
            this.addMessage('companion', 'Failed to connect to Numa', 'system');
        }
    },
    
    sendTeamMessage: async function() {
        const input = document.getElementById('numa-team-input');
        const message = input.value.trim();
        const broadcast = document.getElementById('numa-broadcast-mode').checked;
        
        if (!message) return;
        
        // Add user message to chat
        this.addMessage('team', message, 'user');
        input.value = '';
        
        try {
            const response = await fetch(`${this.apiUrl}/api/team-chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    from_component: 'numa',
                    broadcast: broadcast
                })
            });
            
            const data = await response.json();
            
            // Display responses
            if (data.responses && data.responses.length > 0) {
                data.responses.forEach(resp => {
                    this.addMessage('team', `${resp.from}: ${resp.message}`, 'ai');
                });
            }
        } catch (error) {
            console.error('Failed to send team message:', error);
            this.addMessage('team', 'Failed to send team message', 'system');
        }
    },
    
    addMessage: function(chatType, message, messageType) {
        const messagesDiv = chatType === 'companion' 
            ? document.getElementById('numa-companion-messages')
            : document.getElementById('numa-team-messages');
            
        if (!messagesDiv) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${messageType}-message`;
        
        const prefix = messageType === 'user' ? 'You' : 
                      messageType === 'ai' ? 'Numa' : 
                      'System';
                      
        messageDiv.innerHTML = `<strong>${prefix}:</strong> ${message}`;
        
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
};