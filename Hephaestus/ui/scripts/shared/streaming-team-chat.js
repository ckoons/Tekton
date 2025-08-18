/**
 * Streaming Team Chat Module
 * 
 * Handles team chat with responses arriving as they come, instead of waiting for all.
 * This provides much better user experience for team chat.
 */

window.StreamingTeamChat = {
    /**
     * Send a message to team chat and stream responses
     * @param {string} message - The message to send
     * @param {Object} options - Options for the request
     * @param {function} onResponse - Callback for each response (specialist, content)
     * @param {function} onError - Callback for errors
     * @param {function} onComplete - Callback when streaming completes
     * @returns {function} Abort function to cancel the stream
     */
    streamMessage(message, options = {}, onResponse, onError, onComplete) {
        const {
            timeout = 2.0,
            includeErrors = false,
            targetSpecialists = null
        } = options;
        
        // Build URL with query parameters
        const params = new URLSearchParams({
            message: message,
            timeout: timeout,
            include_errors: includeErrors
        });
        
        if (targetSpecialists && targetSpecialists.length > 0) {
            params.append('targets', targetSpecialists.join(','));
        }
        
        const baseUrl = window.rhetorUrl ? window.rhetorUrl('/api/v2/team-chat/stream') : 'http://localhost:8003/api/v2/team-chat/stream';
        const url = `${baseUrl}?${params}`;
        
        // Create EventSource for SSE
        const eventSource = new EventSource(url);
        
        let responseCount = 0;
        let errorCount = 0;
        let startTime = Date.now();
        
        // Handle different event types
        eventSource.addEventListener('start', (event) => {
            const data = JSON.parse(event.data);
            console.log(`Team chat started with ${data.total_specialists} specialists`);
        });
        
        eventSource.addEventListener('message', (event) => {
            const data = JSON.parse(event.data);
            const elapsed = (Date.now() - startTime) / 1000;
            
            if (data.type === 'response') {
                responseCount++;
                if (onResponse) {
                    onResponse({
                        specialist: data.specialist_id,
                        content: data.content,
                        model: data.model,
                        elapsed: elapsed,
                        index: responseCount
                    });
                }
            } else if (data.type === 'error' || data.type === 'timeout') {
                errorCount++;
                if (onError) {
                    onError({
                        specialist: data.specialist_id,
                        error: data.error,
                        type: data.type,
                        elapsed: elapsed
                    });
                }
            }
        });
        
        eventSource.addEventListener('complete', (event) => {
            const data = JSON.parse(event.data);
            eventSource.close();
            
            if (onComplete) {
                onComplete({
                    totalResponses: data.total_responses,
                    totalErrors: data.total_errors,
                    totalTime: data.total_time,
                    averageTime: data.average_response_time
                });
            }
        });
        
        eventSource.addEventListener('error', (event) => {
            if (event.eventPhase === EventSource.CLOSED) {
                console.log('Team chat stream closed');
            } else {
                console.error('Team chat stream error:', event);
                if (onError) {
                    onError({
                        specialist: 'system',
                        error: 'Stream connection error',
                        type: 'connection'
                    });
                }
            }
            eventSource.close();
        });
        
        // Return abort function
        return () => {
            eventSource.close();
            console.log('Team chat stream aborted');
        };
    },
    
    /**
     * Example usage function for UI components
     */
    example() {
        // Example: Stream team chat to a UI element
        const messagesDiv = document.getElementById('team-messages');
        
        const abort = this.streamMessage(
            "What are the key principles of good software architecture?",
            { timeout: 2.0, includeErrors: true },
            
            // On each response
            (response) => {
                const messageEl = document.createElement('div');
                messageEl.className = 'team-response';
                messageEl.innerHTML = `
                    <strong>${response.specialist}</strong> (${response.elapsed.toFixed(2)}s):
                    <p>${response.content}</p>
                `;
                messagesDiv.appendChild(messageEl);
            },
            
            // On error
            (error) => {
                const errorEl = document.createElement('div');
                errorEl.className = 'team-error';
                errorEl.innerHTML = `
                    <strong>${error.specialist}</strong>: ${error.error}
                `;
                messagesDiv.appendChild(errorEl);
            },
            
            // On complete
            (stats) => {
                const summaryEl = document.createElement('div');
                summaryEl.className = 'team-summary';
                summaryEl.innerHTML = `
                    <hr>
                    Team chat complete: ${stats.totalResponses} responses in ${stats.totalTime.toFixed(2)}s
                    (Average: ${stats.averageTime.toFixed(2)}s per AI)
                `;
                messagesDiv.appendChild(summaryEl);
            }
        );
        
        // Can abort if needed
        // setTimeout(() => abort(), 5000);
    }
};

// Make it available globally
window.TektonStreamingTeamChat = window.StreamingTeamChat;