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
    // Rhetor endpoints
    teamChatUrl: 'http://localhost:8003/api/team-chat',
    specialistUrl: 'http://localhost:8003/api/v1/ai/specialists',
    
    /**
     * Send a message to a single AI specialist (like aish apollo "message")
     * @param {string} aiName - The AI name (e.g., 'noesis-ai', 'apollo-ai')
     * @param {string} message - The message to send
     * @returns {Promise<Object>} The AI's response
     */
    async sendMessage(aiName, message) {
        try {
            const response = await fetch(`${this.specialistUrl}/${aiName}/message`, {
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
            
            const data = await response.json();
            
            if (data.success && data.response) {
                return {
                    content: data.response,
                    ai_id: data.ai_id,
                    success: true
                };
            } else {
                throw new Error(data.error || 'No response from AI');
            }
        } catch (error) {
            console.error(`Failed to send message to ${aiName}:`, error);
            throw error;
        }
    },
    
    /**
     * Send team chat message (like aish team-chat "message")
     * @param {string} message - The message to send
     * @param {string} fromComponent - Which component is sending (e.g., 'rhetor', 'numa')
     * @param {Array<string>} targetAIs - Optional list of specific AIs (empty = all)
     * @returns {Promise<Object>} Team chat response
     */
    async teamChat(message, fromComponent = 'ui', targetAIs = []) {
        const response = await fetch(this.teamChatUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                from_component: fromComponent,
                target_sockets: targetAIs.length > 0 ? targetAIs : null,
                timeout: 10.0
            })
        });
        
        if (!response.ok) {
            throw new Error(`Team chat failed: ${response.statusText}`);
        }
        
        return await response.json();
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