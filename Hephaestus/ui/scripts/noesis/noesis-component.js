// Noesis Component JavaScript - Following Rhetor's minimal pattern

window.NoesisComponent = {
    apiUrl: window.NOESIS_URL || 'http://localhost:8015',
    
    init: function() {
        console.log('Initializing Noesis component');
        this.setupEventListeners();
        this.checkHealth();
    },
    
    setupEventListeners: function() {
        // Tab switching handled by CSS radio buttons (like Rhetor)
        
        // Discovery chat
        const discoveryInput = document.getElementById('noesis-discovery-input');
        const discoverySend = document.getElementById('noesis-discovery-send');
        
        if (discoveryInput && discoverySend) {
            discoverySend.addEventListener('click', () => this.sendDiscoveryQuery());
            discoveryInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendDiscoveryQuery();
            });
        }
        
        // Team chat
        const teamInput = document.getElementById('noesis-team-input');
        const teamSend = document.getElementById('noesis-team-send');
        
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
                document.getElementById('noesis-status').textContent = 'Active';
                
                // Update mode status
                const statusResponse = await fetch(`${this.apiUrl}/api/status`);
                const statusData = await statusResponse.json();
                document.getElementById('noesis-mode').textContent = 
                    statusData.discovery_mode || 'Placeholder';
            }
        } catch (error) {
            console.error('Noesis health check failed:', error);
            this.updateStatus('error', 'Disconnected');
            document.getElementById('noesis-status').textContent = 'Offline';
        }
    },
    
    updateStatus: function(status, text) {
        const statusIndicator = document.querySelector('#noesis-container .noesis__status-indicator');
        const statusText = document.querySelector('#noesis-container .noesis__status-text');
        
        if (statusIndicator) statusIndicator.setAttribute('data-status', status);
        if (statusText) statusText.textContent = text;
    },
    
    sendDiscoveryQuery: async function() {
        const input = document.getElementById('noesis-discovery-input');
        const scopeSelect = document.getElementById('noesis-search-scope');
        const query = input.value.trim();
        
        if (!query) return;
        
        // Add user query to chat
        this.addMessage('discovery', query, 'user');
        input.value = '';
        
        try {
            const response = await fetch(`${this.apiUrl}/api/discovery-chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    search_scope: scopeSelect.value
                })
            });
            
            const data = await response.json();
            
            // Display discoveries
            if (data.discoveries && data.discoveries.length > 0) {
                const discoveryMsg = data.discoveries.join('\n');
                this.addMessage('discovery', discoveryMsg, 'discovery');
            }
            
            // Display insights if available
            if (data.insights && data.insights.length > 0) {
                const insightMsg = 'Insights:\n' + data.insights.join('\n');
                this.addMessage('discovery', insightMsg, 'insight');
            }
        } catch (error) {
            console.error('Failed to send discovery query:', error);
            this.addMessage('discovery', 'Failed to connect to Noesis', 'system');
        }
    },
    
    sendTeamMessage: async function() {
        const input = document.getElementById('noesis-team-input');
        const message = input.value.trim();
        const broadcast = document.getElementById('noesis-broadcast-mode').checked;
        
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
                    from_component: 'noesis',
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
        const messagesDiv = chatType === 'discovery' 
            ? document.getElementById('noesis-discovery-messages')
            : document.getElementById('noesis-team-messages');
            
        if (!messagesDiv) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${messageType}-message`;
        
        const prefix = messageType === 'user' ? 'You' : 
                      messageType === 'discovery' ? 'Discovery' :
                      messageType === 'insight' ? 'Insight' :
                      messageType === 'ai' ? 'Noesis' : 
                      'System';
                      
        messageDiv.innerHTML = `<strong>${prefix}:</strong> ${message}`;
        
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
};