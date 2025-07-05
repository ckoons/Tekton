console.log('[FILE_TRACE] Loading: ai-chat.js');
/**
 * Shared AI Chat Module
 * 
 * Provides a unified interface for all Tekton UI components to communicate with AI specialists.
 * Based on the aish proxy pattern - AIs are just sockets!
 * 
 * Usage:
 *   AIChat.sendMessage('apollo-ai', 'Hello Apollo!')
 *     .then(response => console.log(response))
 *   
 *   AIChat.broadcastMessage('Team announcement', ['apollo-ai', 'athena-ai'])
 *     .then(responses => console.log(responses))
 */

window.AIChat = {
    // Rhetor team-chat endpoint
    teamChatUrl: 'http://localhost:8003/api/team-chat',
    
    /**
     * Send a message to a single AI specialist
     * @param {string} aiName - The AI name (e.g., 'noesis-ai', 'apollo-ai')
     * @param {string} message - The message to send
     * @returns {Promise<Object>} The AI's response
     */
    async sendMessage(aiName, message) {
        try {
            // Use the streaming endpoint that actually works!
            const response = await fetch(`http://localhost:8003/api/chat/${aiName}/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message
                })
            });
            
            if (!response.ok) {
                throw new Error(`Chat failed: ${response.statusText}`);
            }
            
            // Read the streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullContent = '';
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.type === 'chunk' && data.content) {
                                fullContent += data.content;
                            } else if (data.type === 'complete' && data.summary) {
                                // Final message
                                fullContent = data.metadata?.total_content || fullContent;
                            }
                        } catch (e) {
                            // Ignore parse errors for incomplete chunks
                        }
                    }
                }
            }
            
            return {
                content: fullContent,
                socket_id: aiName
            };
        } catch (error) {
            console.error(`Failed to send message to ${aiName}:`, error);
            throw error;
        }
    },
    
    /**
     * Broadcast a message to multiple AI specialists
     * @param {string} message - The message to send
     * @param {Array<string>} aiNames - List of AI names (empty for all)
     * @returns {Promise<Array>} Array of responses
     */
    async broadcastMessage(message, aiNames = []) {
        const response = await fetch(this.teamChatUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                moderation_mode: 'pass_through',
                timeout: 10.0,
                target_sockets: aiNames.length > 0 ? aiNames : null  // null means broadcast to all
            })
        });
        
        if (!response.ok) {
            throw new Error(`Team chat failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Broadcast response:', data);
        
        // Convert responses object to array format
        if (data.responses && typeof data.responses === 'object') {
            return Object.entries(data.responses).map(([socketId, response]) => ({
                socket_id: socketId,
                content: response.content || response.message || '',
                ...response
            }));
        }
        
        return [];
    },
    
    
    /**
     * Parse AI response for special formatting
     * Looks for {blocks} to display specially
     */
    parseResponse(response) {
        const content = response.content || response.message || response;
        
        // Look for content between curly braces
        const regex = /{([^}]+)}/g;
        const parts = [];
        let lastIndex = 0;
        let match;
        
        while ((match = regex.exec(content)) !== null) {
            // Add text before the match
            if (match.index > lastIndex) {
                parts.push({
                    type: 'text',
                    content: content.substring(lastIndex, match.index)
                });
            }
            
            // Add the special block
            parts.push({
                type: 'block',
                content: match[1]
            });
            
            lastIndex = match.index + match[0].length;
        }
        
        // Add remaining text
        if (lastIndex < content.length) {
            parts.push({
                type: 'text',
                content: content.substring(lastIndex)
            });
        }
        
        return parts.length > 0 ? parts : [{type: 'text', content: content}];
    }
};

// Export for use in components
window.TektonAIChat = window.AIChat;