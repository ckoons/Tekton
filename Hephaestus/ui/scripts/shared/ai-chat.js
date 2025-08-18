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

// Landmark: Unified AI Chat Interface - All UI routes through aish MCP
// This consolidation ensures all AI communication goes through a single
// source of truth (aish MCP server) rather than scattered endpoints.
window.AIChat = {
    // Rhetor endpoints - simple proxy that works
    teamChatUrl: window.rhetorUrl ? window.rhetorUrl('/api/team-chat') : 'http://localhost:8003/api/team-chat',
    specialistUrl: window.rhetorUrl ? window.rhetorUrl('/api/v1/ai/specialists') : 'http://localhost:8003/api/v1/ai/specialists',
    
    // Processing message management
    processingIntervals: new Map(), // Track intervals by container ID
    
    /**
     * Show processing message with animated dots
     * @param {HTMLElement} container - The message container element
     * @param {string} baseText - Base text (default: "Processing")
     * @param {string} componentPrefix - Component CSS prefix (e.g., 'budget', 'terma')
     * @returns {HTMLElement} The processing message element
     */
    showProcessingMessage(container, baseText = "Processing", componentPrefix = null) {
        // Remove any existing processing message
        this.hideProcessingMessage(container);
        
        // Create processing message element
        const processingDiv = document.createElement('div');
        
        // Determine CSS classes based on component
        if (componentPrefix) {
            processingDiv.className = `${componentPrefix}__message ${componentPrefix}__message--system processing-message`;
        } else {
            processingDiv.className = 'chat-message system-message processing-message';
        }
        processingDiv.setAttribute('data-processing', 'true');
        
        // Initial content with proper structure
        let dotCount = 0;
        const updateContent = () => {
            if (componentPrefix) {
                processingDiv.innerHTML = `
                    <div class="${componentPrefix}__message-content">
                        <div class="${componentPrefix}__message-text">
                            <strong>System:</strong> ${baseText}${'.'.repeat(dotCount)}
                        </div>
                    </div>
                `;
            } else {
                processingDiv.innerHTML = `<strong>System:</strong> ${baseText}${'.'.repeat(dotCount)}`;
            }
        };
        
        updateContent();
        
        // Add to container
        container.appendChild(processingDiv);
        
        // Animate dots
        const intervalId = setInterval(() => {
            dotCount = (dotCount + 1) % 4; // Cycles through 0,1,2,3
            updateContent();
        }, 500); // Update every 500ms
        
        // Store interval ID for cleanup
        this.processingIntervals.set(container.id || container, intervalId);
        
        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
        
        return processingDiv;
    },
    
    /**
     * Hide processing message and clear animation
     * @param {HTMLElement} container - The message container element
     */
    hideProcessingMessage(container) {
        // Clear interval
        const intervalId = this.processingIntervals.get(container.id || container);
        if (intervalId) {
            clearInterval(intervalId);
            this.processingIntervals.delete(container.id || container);
        }
        
        // Remove processing message element
        const processingMsg = container.querySelector('[data-processing="true"]');
        if (processingMsg) {
            processingMsg.remove();
        }
    },
    
    /**
     * Send a message to a single AI specialist
     * @param {string} aiName - The AI name (e.g., 'terma-ai', 'apollo-ai') 
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
     * Send team chat message
     * @param {string} message - The message to send
     * @param {string} fromComponent - Which component is sending (e.g., 'rhetor', 'numa')
     * @param {Array<string>} targetAIs - Optional list of specific AIs (empty = all)
     * @returns {Promise<Object>} Team chat response
     */
    async teamChat(message, fromComponent = 'ui', targetAIs = []) {
        try {
            // Use the direct team chat endpoint
            const response = await fetch(this.teamChatUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    from_component: fromComponent,
                    target_ais: targetAIs
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Team chat error:', errorData);
                return {
                    responses: [],
                    error: errorData.detail || `Team chat failed: ${response.statusText}`
                };
            }
            
            const data = await response.json();
            
            // Validate response format
            if (!data.responses || !Array.isArray(data.responses)) {
                console.error('Invalid team chat response format:', data);
                return {
                    responses: [],
                    error: 'Invalid response format from team chat'
                };
            }
            
            return data;
        } catch (error) {
            console.error('Team chat error:', error);
            return {
                responses: [],
                error: 'Network error: ' + error.message
            };
        }
    },
    
    /**
     * Send message with streaming response support
     * @param {string} aiName - The AI name
     * @param {string} message - The message to send
     * @param {function} onChunk - Callback for each chunk
     * @param {function} onComplete - Callback when streaming completes
     * @param {function} onError - Callback for errors
     * @returns {function} Abort function to cancel the stream
     */
    streamMessage(aiName, message, onChunk, onComplete, onError) {
        const url = aishUrl('/api/mcp/v2/tools/send-message');
        
        // Create fetch request with streaming
        const controller = new AbortController();
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ai_name: aiName,
                message: message,
                stream: true
            }),
            signal: controller.signal
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Stream failed: ${response.statusText}`);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            
            const processStream = async () => {
                try {
                    while (true) {
                        const { done, value } = await reader.read();
                        
                        if (done) {
                            if (onComplete) onComplete();
                            break;
                        }
                        
                        buffer += decoder.decode(value, { stream: true });
                        
                        // Process complete SSE messages
                        const lines = buffer.split('\n');
                        buffer = lines.pop() || ''; // Keep incomplete line in buffer
                        
                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                try {
                                    const data = JSON.parse(line.slice(6));
                                    
                                    if (data.error) {
                                        if (onError) onError(data.error);
                                    } else if (!data.done && data.chunk) {
                                        if (onChunk) onChunk(data.chunk);
                                    } else if (data.done) {
                                        if (onComplete) onComplete();
                                    }
                                } catch (e) {
                                    console.error('Failed to parse SSE data:', e);
                                }
                            }
                        }
                    }
                } catch (error) {
                    if (error.name !== 'AbortError') {
                        if (onError) onError(error);
                    }
                }
            };
            
            processStream();
        })
        .catch(error => {
            if (error.name !== 'AbortError') {
                if (onError) onError(error);
            }
        });
        
        // Return abort function
        return () => controller.abort();
    },
    
    /**
     * List available AI specialists
     * @returns {Promise<Array>} List of available AIs
     */
    async listAIs() {
        try {
            const response = await fetch(aishUrl('/api/mcp/v2/tools/list-ais'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            
            if (!response.ok) {
                throw new Error(`Failed to list AIs: ${response.statusText}`);
            }
            
            const data = await response.json();
            return data.ais || [];
        } catch (error) {
            console.error('Failed to list AIs:', error);
            throw error;
        }
    },
    
    /**
     * Send message to terminal via aish MCP
     * @param {string} terminal - Terminal name or 'broadcast'
     * @param {string} message - Message to send
     * @returns {Promise<Object>} Response
     */
    async termaSend(terminal, message) {
        try {
            const response = await fetch(aishUrl('/api/mcp/v2/tools/terma-send'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    terminal: terminal,
                    message: message
                })
            });
            
            if (!response.ok) {
                throw new Error(`Terminal send failed: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Failed to send to terminal ${terminal}:`, error);
            throw error;
        }
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