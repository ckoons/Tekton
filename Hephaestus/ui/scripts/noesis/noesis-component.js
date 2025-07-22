console.log('[FILE_TRACE] Loading: noesis-component.js');
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
        
        const messagesDiv = document.getElementById('noesis-discovery-messages');
        
        // Add user message - just the text, no prefix
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'chat-message user-message';
        userMessageDiv.innerHTML = query;
        messagesDiv.appendChild(userMessageDiv);
        
        input.value = '';
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
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
                const aiMessageDiv = document.createElement('div');
                aiMessageDiv.className = 'chat-message ai-message';
                aiMessageDiv.innerHTML = `<strong>Noesis:</strong> ${data.discoveries.join('\n')}`;
                messagesDiv.appendChild(aiMessageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            // Display insights if available
            if (data.insights && data.insights.length > 0) {
                const insightDiv = document.createElement('div');
                insightDiv.className = 'chat-message ai-message';
                insightDiv.innerHTML = `<strong>Insights:</strong> ${data.insights.join('\n')}`;
                messagesDiv.appendChild(insightDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        } catch (error) {
            console.error('Failed to send discovery query:', error);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'chat-message system-message';
            errorDiv.innerHTML = '<strong>System:</strong> Failed to connect to Noesis';
            messagesDiv.appendChild(errorDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    },
    
    sendTeamMessage: async function() {
        const input = document.getElementById('noesis-team-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        const messagesDiv = document.getElementById('noesis-team-messages');
        
        // Add user message - just the text, no prefix
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'chat-message user-message';
        userMessageDiv.innerHTML = message;
        messagesDiv.appendChild(userMessageDiv);
        
        input.value = '';
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        try {
            // Use Rhetor's team chat endpoint
            const response = await fetch('http://localhost:8003/api/team-chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    from_component: 'noesis',
                    broadcast: true  // Always broadcast to team
                })
            });
            
            const data = await response.json();
            
            // Display responses
            if (data.responses && data.responses.length > 0) {
                data.responses.forEach(resp => {
                    const aiMessageDiv = document.createElement('div');
                    aiMessageDiv.className = 'chat-message ai-message';
                    aiMessageDiv.innerHTML = `<strong>${resp.from}:</strong> ${resp.message}`;
                    messagesDiv.appendChild(aiMessageDiv);
                });
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        } catch (error) {
            console.error('Failed to send team message:', error);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'chat-message system-message';
            errorDiv.innerHTML = '<strong>System:</strong> Failed to send team message';
            messagesDiv.appendChild(errorDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    },
};