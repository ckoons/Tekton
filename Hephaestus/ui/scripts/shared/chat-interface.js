/**
 * Chat Interface - A standardized chat interface component for Tekton components.
 * 
 * This module provides a reusable chat interface that can be used by any Tekton
 * component to implement LLM chat functionality with a consistent user experience.
 */

console.log('[FILE_TRACE] Loading: chat-interface.js');
/**
 * Creates a chat interface component that can be integrated into any Tekton component.
 * 
 * @param {HTMLElement} container - The container element to render the chat interface in
 * @param {Object} options - Configuration options
 * @returns {Object} - Chat interface API for controlling the component
 */
function createChatInterface(container, options = {}) {
    // Configuration options with defaults
    const config = {
        // Content
        initialMessages: options.initialMessages || [],
        systemPrompt: options.systemPrompt || '',
        placeholder: options.placeholder || 'Send a message...',
        
        // LLM configuration
        llmAdapterClient: options.llmAdapterClient,
        webSocket: options.webSocket || null,
        defaultModel: options.defaultModel || (window.DEFAULT_LLM_MODEL || 'claude-3-sonnet-20240229'),
        modelOptions: options.modelOptions || [
            { id: 'claude-3-haiku-20240307', name: 'Claude 3 Haiku' },
            { id: 'claude-3-sonnet-20240229', name: 'Claude 3 Sonnet' },
            { id: 'claude-3-opus-20240229', name: 'Claude 3 Opus' },
            { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
            { id: 'gpt-4', name: 'GPT-4' }
        ],
        
        // Appearance
        theme: options.theme || 'light',
        showAvatar: options.showAvatar !== undefined ? options.showAvatar : true,
        showTimestamp: options.showTimestamp !== undefined ? options.showTimestamp : true,
        showTypingIndicator: options.showTypingIndicator !== undefined ? options.showTypingIndicator : true,
        showToolbar: options.showToolbar !== undefined ? options.showToolbar : true,
        showModelSelector: options.showModelSelector !== undefined ? options.showModelSelector : true,
        
        // Behavior
        enableMarkdown: options.enableMarkdown !== undefined ? options.enableMarkdown : true,
        showThinking: options.showThinking !== undefined ? options.showThinking : false,
        autoScroll: options.autoScroll !== undefined ? options.autoScroll : true,
        
        // Callbacks
        onSend: options.onSend || null,
        onMessageReceived: options.onMessageReceived || null,
        onError: options.onError || null,
        onModelChange: options.onModelChange || null,
        onThemeChange: options.onThemeChange || null
    };
    
    // Element references
    let elements = {
        container: null,
        messagesContainer: null,
        inputContainer: null,
        textarea: null,
        sendButton: null,
        modelSelector: null,
        toolbar: null,
        clearButton: null,
        themeToggle: null
    };
    
    // Internal state
    let state = {
        messages: [...config.initialMessages],
        isGenerating: false,
        currentRequestId: null,
        fullResponse: '',
        model: config.defaultModel,
        theme: config.theme
    };
    
    /**
     * Initialize the chat interface.
     */
    function initialize() {
        if (!config.llmAdapterClient) {
            console.error('LLM adapter client is required. Please provide an instance of LLMAdapterClient.');
            return;
        }
        
        createElements();
        renderMessages();
        setupEventListeners();
        applyTheme(config.theme);
    }
    
    /**
     * Create the DOM elements for the chat interface.
     */
    function createElements() {
        // Clear the container
        container.innerHTML = '';
        
        // Create the main container
        elements.container = document.createElement('div');
        elements.container.className = 'chat-interface';
        
        // Create messages container
        elements.messagesContainer = document.createElement('div');
        elements.messagesContainer.className = 'chat-messages';
        
        // Create toolbar
        if (config.showToolbar) {
            elements.toolbar = document.createElement('div');
            elements.toolbar.className = 'chat-toolbar';
            
            // Create model selector
            if (config.showModelSelector) {
                elements.modelSelector = document.createElement('select');
                elements.modelSelector.className = 'chat-model-selector';
                
                // Add model options
                config.modelOptions.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;
                    option.selected = model.id === state.model;
                    elements.modelSelector.appendChild(option);
                });
                
                elements.toolbar.appendChild(elements.modelSelector);
            }
            
            // Clear button
            elements.clearButton = document.createElement('button');
            elements.clearButton.className = 'chat-clear-button';
            elements.clearButton.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"></path></svg>';
            elements.clearButton.title = 'Clear conversation';
            elements.toolbar.appendChild(elements.clearButton);
            
            // Theme toggle
            elements.themeToggle = document.createElement('button');
            elements.themeToggle.className = 'chat-theme-toggle';
            elements.themeToggle.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"></path></svg>';
            elements.themeToggle.title = 'Toggle dark mode';
            elements.toolbar.appendChild(elements.themeToggle);
            
            elements.container.appendChild(elements.toolbar);
        }
        
        elements.container.appendChild(elements.messagesContainer);
        
        // Create input container
        elements.inputContainer = document.createElement('div');
        elements.inputContainer.className = 'chat-input-container';
        
        // Create textarea
        elements.textarea = document.createElement('textarea');
        elements.textarea.className = 'chat-input';
        elements.textarea.placeholder = config.placeholder;
        elements.textarea.rows = 1;
        
        // Create send button
        elements.sendButton = document.createElement('button');
        elements.sendButton.className = 'chat-send-button';
        elements.sendButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24"><path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>';
        elements.sendButton.title = 'Send message';
        
        // Assemble the input container
        elements.inputContainer.appendChild(elements.textarea);
        elements.inputContainer.appendChild(elements.sendButton);
        
        // Add input container to main container
        elements.container.appendChild(elements.inputContainer);
        
        // Add everything to the provided container
        container.appendChild(elements.container);
    }
    
    /**
     * Set up event listeners for user interactions.
     */
    function setupEventListeners() {
        // Send button click
        elements.sendButton.addEventListener('click', handleSend);
        
        // Textarea keydown (Enter to send, Shift+Enter for new line)
        elements.textarea.addEventListener('keydown', handleInputKeydown);
        
        // Auto-resize textarea as user types
        elements.textarea.addEventListener('input', handleTextareaInput);
        
        // Model selector change
        if (elements.modelSelector) {
            elements.modelSelector.addEventListener('change', event => {
                state.model = event.target.value;
                if (config.onModelChange) {
                    config.onModelChange(state.model);
                }
            });
        }
        
        // Clear button click
        if (elements.clearButton) {
            elements.clearButton.addEventListener('click', clearMessages);
        }
        
        // Theme toggle click
        if (elements.themeToggle) {
            elements.themeToggle.addEventListener('click', () => {
                const newTheme = state.theme === 'light' ? 'dark' : 'light';
                applyTheme(newTheme);
                if (config.onThemeChange) {
                    config.onThemeChange(newTheme);
                }
            });
        }
    }
    
    /**
     * Handle keydown events in the textarea.
     * 
     * @param {KeyboardEvent} event - Keyboard event
     */
    function handleInputKeydown(event) {
        // Enter without shift to send
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSend();
        }
    }
    
    /**
     * Handle input events in the textarea to auto-resize.
     */
    function handleTextareaInput() {
        elements.textarea.style.height = 'auto';
        elements.textarea.style.height = `${Math.min(elements.textarea.scrollHeight, 150)}px`;
    }
    
    /**
     * Handle send button click or Enter key press.
     */
    function handleSend() {
        const message = elements.textarea.value.trim();
        
        if (!message || state.isGenerating) {
            return;
        }
        
        // Add user message
        addMessage('user', message);
        
        // Clear textarea and reset height
        elements.textarea.value = '';
        elements.textarea.style.height = 'auto';
        
        // Call onSend callback if provided
        if (config.onSend) {
            config.onSend(message);
        }
        
        // Generate a response
        generateResponse(message);
    }
    
    /**
     * Generate a response from the LLM.
     * 
     * @param {string} message - User message
     */
    function generateResponse(message) {
        // Set generating state
        state.isGenerating = true;
        state.fullResponse = '';
        
        // Show typing indicator
        if (config.showTypingIndicator) {
            addTypingIndicator();
        }
        
        // Prepare chat history for context
        const chatHistory = state.messages
            .filter(msg => msg.role !== 'system' && msg.role !== 'thinking')
            .map(msg => ({
                role: msg.role,
                content: msg.content
            }));
        
        // Use WebSocket if available, otherwise use HTTP streaming
        if (config.webSocket && config.webSocket.readyState === WebSocket.OPEN) {
            // Use WebSocket streaming
            state.currentRequestId = config.llmAdapterClient.generateWebSocketStream(
                config.webSocket,
                {
                    prompt: message,
                    systemPrompt: config.systemPrompt,
                    model: state.model,
                    chatHistory: chatHistory.slice(0, -1), // Exclude the last message (already in prompt)
                    onChunk: handleResponseChunk,
                    onComplete: handleResponseComplete,
                    onError: handleResponseError
                }
            );
        } else {
            // Use HTTP streaming
            state.currentRequestId = config.llmAdapterClient.generateStream({
                prompt: message,
                systemPrompt: config.systemPrompt,
                model: state.model,
                chatHistory: chatHistory.slice(0, -1), // Exclude the last message (already in prompt)
                onChunk: handleResponseChunk,
                onComplete: handleResponseComplete,
                onError: handleResponseError
            });
        }
    }
    
    /**
     * Handle a chunk of the response.
     * 
     * @param {Object} chunk - Response chunk data
     */
    function handleResponseChunk(chunk) {
        // Remove typing indicator
        removeTypingIndicator();
        
        // Extract content from chunk
        let content = '';
        if (typeof chunk === 'string') {
            content = chunk;
        } else if (chunk.content) {
            content = chunk.content;
        } else if (chunk.chunk) {
            content = chunk.chunk;
        } else if (chunk.delta && chunk.delta.content) {
            content = chunk.delta.content;
        }
        
        // Skip empty chunks
        if (!content) return;
        
        // Add to full response
        state.fullResponse += content;
        
        // Show thinking if enabled
        if (config.showThinking && chunk.thinking) {
            // Add or update thinking message
            updateThinkingMessage(chunk.thinking);
        }
        
        // Update or create assistant message
        updateOrCreateAssistantMessage();
        
        // Call onMessageReceived callback if provided
        if (config.onMessageReceived) {
            config.onMessageReceived(chunk);
        }
    }
    
    /**
     * Update or create the thinking message.
     * 
     * @param {string} thinking - Thinking content
     */
    function updateThinkingMessage(thinking) {
        const thinkingMsg = state.messages.find(msg => msg.role === 'thinking');
        
        if (thinkingMsg) {
            // Update existing thinking message
            thinkingMsg.content = thinking;
            renderMessages();
        } else {
            // Create new thinking message
            addMessage('thinking', thinking, { skipRender: true });
            renderMessages();
        }
    }
    
    /**
     * Update or create the assistant message with the current response.
     */
    function updateOrCreateAssistantMessage() {
        const assistantMsg = state.messages.find(
            msg => msg.role === 'assistant' && msg.timestamp > state.messages.find(m => m.role === 'user').timestamp
        );
        
        if (assistantMsg) {
            // Update existing assistant message
            assistantMsg.content = state.fullResponse;
            renderMessageContent(assistantMsg);
        } else {
            // Create new assistant message
            addMessage('assistant', state.fullResponse);
        }
    }
    
    /**
     * Handle response completion.
     */
    function handleResponseComplete() {
        // Update state
        state.isGenerating = false;
        state.currentRequestId = null;
        
        // Ensure the message is in the state with final content
        updateOrCreateAssistantMessage();
        
        // Remove any thinking message now that we're done
        if (config.showThinking) {
            state.messages = state.messages.filter(msg => msg.role !== 'thinking');
            renderMessages();
        }
    }
    
    /**
     * Handle response error.
     * 
     * @param {Error} error - Error object
     */
    function handleResponseError(error) {
        console.error('Error generating response:', error);
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add error message
        addMessage('assistant', `Sorry, I encountered an error: ${error.message}`);
        
        // Update state
        state.isGenerating = false;
        state.currentRequestId = null;
        
        // Call onError callback if provided
        if (config.onError) {
            config.onError(error);
        }
    }
    
    /**
     * Add a typing indicator to show the assistant is generating a response.
     */
    function addTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'chat-message chat-message-assistant chat-typing-indicator';
        
        // Add avatar if enabled
        if (config.showAvatar) {
            const avatar = document.createElement('div');
            avatar.className = 'chat-avatar';
            avatar.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#5436DA" /></svg>';
            typingIndicator.appendChild(avatar);
        }
        
        // Add content container
        const contentContainer = document.createElement('div');
        contentContainer.className = 'chat-content';
        
        // Add typing animation
        const dots = document.createElement('div');
        dots.className = 'typing-dots';
        dots.innerHTML = '<span></span><span></span><span></span>';
        contentContainer.appendChild(dots);
        
        typingIndicator.appendChild(contentContainer);
        elements.messagesContainer.appendChild(typingIndicator);
        
        // Scroll to bottom
        if (config.autoScroll) {
            scrollToBottom();
        }
    }
    
    /**
     * Remove the typing indicator.
     */
    function removeTypingIndicator() {
        const typingIndicator = elements.messagesContainer.querySelector('.chat-typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    /**
     * Add a message to the chat.
     * 
     * @param {string} role - Message role ('user', 'assistant', 'system', 'thinking')
     * @param {string} content - Message content
     * @param {Object} options - Additional options
     * @param {boolean} [options.skipRender=false] - Whether to skip rendering the message
     * @returns {Object} - The added message object
     */
    function addMessage(role, content, options = {}) {
        const message = {
            role,
            content,
            timestamp: Date.now(),
            id: Date.now().toString(36) + Math.random().toString(36).substring(2, 5)
        };
        
        state.messages.push(message);
        
        if (!options.skipRender) {
            renderMessage(message);
            
            // Scroll to bottom
            if (config.autoScroll) {
                scrollToBottom();
            }
        }
        
        return message;
    }
    
    /**
     * Render all messages in the chat.
     */
    function renderMessages() {
        // Clear messages container
        elements.messagesContainer.innerHTML = '';
        
        // Render each message
        state.messages.forEach(message => {
            renderMessage(message);
        });
        
        // Scroll to bottom
        if (config.autoScroll) {
            scrollToBottom();
        }
    }
    
    /**
     * Render a single message.
     * 
     * @param {Object} message - Message object
     */
    function renderMessage(message) {
        // Skip system messages in the UI
        if (message.role === 'system') {
            return;
        }
        
        // Create message element
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message chat-message-${message.role}`;
        messageElement.dataset.messageId = message.id;
        
        // Add avatar if enabled
        if (config.showAvatar) {
            const avatar = document.createElement('div');
            avatar.className = 'chat-avatar';
            
            // Different avatars for different roles
            let avatarContent = '';
            if (message.role === 'user') {
                avatarContent = '<svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#41C2C4" /><path fill="#FFFFFF" d="M12 12c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-2.67 0-8 1.34-8 4v1h16v-1c0-2.66-5.33-4-8-4z"/></svg>';
            } else if (message.role === 'assistant') {
                avatarContent = '<svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#5436DA" /><path fill="#FFFFFF" d="M12 12c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-2.67 0-8 1.34-8 4v1h16v-1c0-2.66-5.33-4-8-4z"/></svg>';
            } else if (message.role === 'thinking') {
                avatarContent = '<svg width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#FFB6C1" /><path fill="#FFFFFF" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-4h2v2h-2zm0-10h2v8h-2z"/></svg>';
            }
            
            avatar.innerHTML = avatarContent;
            messageElement.appendChild(avatar);
        }
        
        // Add content container
        const contentContainer = document.createElement('div');
        contentContainer.className = 'chat-content';
        
        // Add timestamp if enabled
        if (config.showTimestamp) {
            const timestamp = document.createElement('div');
            timestamp.className = 'chat-timestamp';
            timestamp.textContent = formatTimestamp(message.timestamp);
            contentContainer.appendChild(timestamp);
        }
        
        // Add message content
        const contentElement = document.createElement('div');
        contentElement.className = 'chat-text';
        
        // Add thinking label if it's a thinking message
        if (message.role === 'thinking') {
            const thinkingLabel = document.createElement('div');
            thinkingLabel.className = 'chat-thinking-label';
            thinkingLabel.textContent = 'Thinking...';
            contentContainer.appendChild(thinkingLabel);
        }
        
        // Apply markdown if enabled
        if (config.enableMarkdown && ['assistant', 'thinking'].includes(message.role)) {
            if (window.marked) {
                contentElement.innerHTML = window.marked.parse(message.content);
            } else {
                contentElement.textContent = message.content;
            }
        } else {
            contentElement.textContent = message.content;
        }
        
        contentContainer.appendChild(contentElement);
        messageElement.appendChild(contentContainer);
        
        // Add to the messages container
        elements.messagesContainer.appendChild(messageElement);
    }
    
    /**
     * Update the content of an existing message.
     * 
     * @param {Object} message - Message object to update
     */
    function renderMessageContent(message) {
        // Find the message element
        const messageElement = elements.messagesContainer.querySelector(`[data-message-id="${message.id}"]`);
        if (!messageElement) return;
        
        // Find the content element
        const contentElement = messageElement.querySelector('.chat-text');
        if (!contentElement) return;
        
        // Update the content
        if (config.enableMarkdown && ['assistant', 'thinking'].includes(message.role)) {
            if (window.marked) {
                contentElement.innerHTML = window.marked.parse(message.content);
            } else {
                contentElement.textContent = message.content;
            }
        } else {
            contentElement.textContent = message.content;
        }
        
        // Scroll to bottom
        if (config.autoScroll) {
            scrollToBottom();
        }
    }
    
    /**
     * Format a timestamp for display.
     * 
     * @param {number} timestamp - Timestamp in milliseconds
     * @returns {string} - Formatted timestamp string
     */
    function formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    /**
     * Scroll the messages container to the bottom.
     */
    function scrollToBottom() {
        elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
    }
    
    /**
     * Apply theme to the chat interface.
     * 
     * @param {string} theme - Theme name ('light' or 'dark')
     */
    function applyTheme(theme) {
        state.theme = theme;
        
        // Add theme class to container
        elements.container.classList.remove('chat-theme-light', 'chat-theme-dark');
        elements.container.classList.add(`chat-theme-${theme}`);
        
        // Update theme toggle icon
        if (elements.themeToggle) {
            if (theme === 'dark') {
                elements.themeToggle.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2c5.52 0 10 4.48 10 10s-4.48 10-10 10-10-4.48-10-10 4.48-10 10-10zm0 2c-4.41 0-8 3.59-8 8s3.59 8 8 8 8-3.59 8-8-3.59-8-8-8zm0 2.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5.67-1.5 1.5-1.5zm3.5 7.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5.67-1.5 1.5-1.5zm-7 0c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5.67-1.5 1.5-1.5zm3.5-3.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5.67-1.5 1.5-1.5z"></path></svg>';
            } else {
                elements.themeToggle.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"></path></svg>';
            }
        }
    }
    
    /**
     * Clear all messages from the chat.
     */
    function clearMessages() {
        // Cancel any ongoing generation
        if (state.isGenerating && state.currentRequestId) {
            if (config.webSocket && config.webSocket.readyState === WebSocket.OPEN) {
                config.llmAdapterClient.cancelWebSocketRequest(config.webSocket, state.currentRequestId);
            } else {
                config.llmAdapterClient.cancelRequest(state.currentRequestId);
            }
        }
        
        // Clear messages (keeping system messages)
        state.messages = state.messages.filter(msg => msg.role === 'system');
        state.isGenerating = false;
        state.currentRequestId = null;
        
        // Render empty messages
        renderMessages();
    }
    
    /**
     * Add a system message to the chat.
     * 
     * @param {string} content - System message content
     */
    function setSystemPrompt(content) {
        // Find existing system message
        const systemMessageIndex = state.messages.findIndex(msg => msg.role === 'system');
        
        if (systemMessageIndex >= 0) {
            // Update existing system message
            state.messages[systemMessageIndex].content = content;
        } else {
            // Add new system message
            state.messages.unshift({
                role: 'system',
                content,
                timestamp: Date.now(),
                id: 'system-' + Date.now().toString(36)
            });
        }
        
        // Update config
        config.systemPrompt = content;
    }
    
    /**
     * Set the LLM model to use.
     * 
     * @param {string} modelId - Model ID
     */
    function setModel(modelId) {
        state.model = modelId;
        
        // Update model selector if it exists
        if (elements.modelSelector) {
            elements.modelSelector.value = modelId;
        }
        
        // Call onModelChange callback if provided
        if (config.onModelChange) {
            config.onModelChange(modelId);
        }
    }
    
    /**
     * Focus the input textarea.
     */
    function focusInput() {
        if (elements.textarea) {
            elements.textarea.focus();
        }
    }
    
    // Initialize the component
    initialize();
    
    // Return public API
    return {
        // State getters
        getMessages: () => [...state.messages],
        getModel: () => state.model,
        getTheme: () => state.theme,
        isGenerating: () => state.isGenerating,
        
        // Actions
        addMessage,
        clearMessages,
        setSystemPrompt,
        setModel,
        applyTheme,
        focusInput,
        
        // Advanced control
        cancelGeneration: () => {
            if (state.isGenerating && state.currentRequestId) {
                if (config.webSocket && config.webSocket.readyState === WebSocket.OPEN) {
                    config.llmAdapterClient.cancelWebSocketRequest(config.webSocket, state.currentRequestId);
                } else {
                    config.llmAdapterClient.cancelRequest(state.currentRequestId);
                }
                state.isGenerating = false;
                state.currentRequestId = null;
                removeTypingIndicator();
                return true;
            }
            return false;
        }
    };
}

// Add the CSS for the chat interface
function addChatInterfaceStyles() {
    // Only add styles once
    if (document.getElementById('chat-interface-styles')) return;
    
    const styleElement = document.createElement('style');
    styleElement.id = 'chat-interface-styles';
    styleElement.textContent = `
        /* Chat Interface Styles */
        .chat-interface {
            display: flex;
            flex-direction: column;
            height: 100%;
            min-height: 300px;
            border-radius: 8px;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-primary, #1a1a2a);
            color: var(--text-primary, #f0f0f0);
        }
        
        /* Themes */
        .chat-theme-light {
            background-color: var(--bg-primary, #1a1a2a);
            color: var(--text-primary, #f0f0f0);
        }
        
        .chat-theme-dark {
            background-color: #1e1e2e;
            color: #e0e0e0;
        }
        
        /* Toolbar */
        .chat-toolbar {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding: 8px 16px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            gap: 12px;
        }
        
        .chat-theme-dark .chat-toolbar {
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .chat-model-selector {
            flex-grow: 1;
            padding: 6px 10px;
            border-radius: 4px;
            border: 1px solid #d0d0d0;
            background-color: var(--bg-secondary, #252535);
            font-size: 14px;
        }
        
        .chat-theme-dark .chat-model-selector {
            background-color: #2d2d3d;
            border-color: #444;
            color: #e0e0e0;
        }
        
        .chat-clear-button, .chat-theme-toggle {
            background: none;
            border: none;
            cursor: pointer;
            border-radius: 4px;
            padding: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #555;
        }
        
        .chat-theme-dark .chat-clear-button, 
        .chat-theme-dark .chat-theme-toggle {
            color: #aaa;
        }
        
        .chat-clear-button:hover, .chat-theme-toggle:hover {
            background-color: rgba(0, 0, 0, 0.05);
        }
        
        .chat-theme-dark .chat-clear-button:hover, 
        .chat-theme-dark .chat-theme-toggle:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        
        /* Messages Container */
        .chat-messages {
            flex-grow: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        /* Message */
        .chat-message {
            display: flex;
            gap: 12px;
            max-width: 90%;
            position: relative;
        }
        
        .chat-message-user {
            align-self: flex-end;
        }
        
        .chat-message-assistant, .chat-message-thinking {
            align-self: flex-start;
        }
        
        /* Avatar */
        .chat-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        
        /* Message Content */
        .chat-content {
            padding: 10px 14px;
            border-radius: 8px;
            position: relative;
            min-width: 50px;
            max-width: 100%;
        }
        
        .chat-message-user .chat-content {
            background-color: #e7f5ff;
            margin-left: auto;
            border-bottom-right-radius: 2px;
        }
        
        .chat-theme-dark .chat-message-user .chat-content {
            background-color: #2a4365;
        }
        
        .chat-message-assistant .chat-content {
            background-color: #f0f0f0;
            margin-right: auto;
            border-bottom-left-radius: 2px;
        }
        
        .chat-theme-dark .chat-message-assistant .chat-content {
            background-color: #313449;
        }
        
        .chat-message-thinking .chat-content {
            background-color: var(--bg-tertiary, #333345);
            margin-right: auto;
            border: 1px dashed #ffb6c1;
            border-bottom-left-radius: 2px;
        }
        
        .chat-theme-dark .chat-message-thinking .chat-content {
            background-color: #3d2c3a;
            border-color: #6f4a59;
        }
        
        /* Thinking Label */
        .chat-thinking-label {
            font-size: 12px;
            font-weight: bold;
            color: #ff69b4;
            margin-bottom: 4px;
        }
        
        .chat-theme-dark .chat-thinking-label {
            color: #ffb6c1;
        }
        
        /* Timestamp */
        .chat-timestamp {
            font-size: 11px;
            color: #999;
            margin-bottom: 4px;
        }
        
        .chat-theme-dark .chat-timestamp {
            color: #777;
        }
        
        /* Message Text */
        .chat-text {
            font-size: 14px;
            line-height: 1.5;
            word-break: break-word;
            overflow-wrap: break-word;
        }
        
        .chat-text p {
            margin: 0 0 8px 0;
        }
        
        .chat-text p:last-child {
            margin-bottom: 0;
        }
        
        .chat-text pre {
            background-color: rgba(0, 0, 0, 0.05);
            padding: 8px;
            border-radius: 4px;
            overflow-x: auto;
            font-family: monospace;
            margin: 8px 0;
        }
        
        .chat-theme-dark .chat-text pre {
            background-color: rgba(0, 0, 0, 0.2);
        }
        
        .chat-text code {
            font-family: monospace;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 12px;
            background-color: rgba(0, 0, 0, 0.05);
        }
        
        .chat-theme-dark .chat-text code {
            background-color: rgba(0, 0, 0, 0.2);
        }
        
        /* Typing Indicator */
        .chat-typing-indicator {
            opacity: 0.8;
        }
        
        .typing-dots {
            display: inline-flex;
            align-items: center;
            column-gap: 4px;
            margin: 4px 0;
        }
        
        .typing-dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #888;
            animation: typingAnimation 1.4s infinite ease-in-out;
            animation-fill-mode: both;
        }
        
        .typing-dots span:nth-child(1) {
            animation-delay: 0s;
        }
        
        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typingAnimation {
            0% { transform: scale(0.5); opacity: 0.3; }
            20% { transform: scale(1); opacity: 1; }
            100% { transform: scale(0.5); opacity: 0.3; }
        }
        
        /* Input Container */
        .chat-input-container {
            display: flex;
            padding: 12px 16px;
            border-top: 1px solid rgba(0, 0, 0, 0.1);
            background-color: var(--bg-secondary, #252535);
            gap: 12px;
            position: relative;
        }
        
        .chat-theme-dark .chat-input-container {
            background-color: #2d2d3d;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Textarea */
        .chat-input {
            flex-grow: 1;
            padding: 10px 14px;
            border-radius: 8px;
            border: 1px solid #d0d0d0;
            font-size: 14px;
            line-height: 1.5;
            resize: none;
            min-height: 24px;
            max-height: 150px;
            overflow-y: auto;
            background-color: var(--bg-secondary, #252535);
            color: var(--text-primary, #f0f0f0);
        }
        
        .chat-theme-dark .chat-input {
            background-color: #363646;
            border-color: #444;
            color: #e0e0e0;
        }
        
        .chat-input:focus {
            outline: none;
            border-color: #7e9ed4;
            box-shadow: 0 0 0 1px rgba(126, 158, 212, 0.4);
        }
        
        .chat-theme-dark .chat-input:focus {
            border-color: #7e9ed4;
            box-shadow: 0 0 0 1px rgba(126, 158, 212, 0.4);
        }
        
        /* Send Button */
        .chat-send-button {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            background-color: #5665c0;
            color: white;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            padding: 0;
        }
        
        .chat-send-button:hover {
            background-color: #4556b1;
        }
        
        .chat-send-button:active {
            background-color: #3a4999;
        }
        
        .chat-theme-dark .chat-send-button {
            background-color: #5665c0;
        }
        
        .chat-theme-dark .chat-send-button:hover {
            background-color: #4556b1;
        }
        
        /* Scrollbar */
        .chat-messages::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-messages::-webkit-scrollbar-track {
            background-color: transparent;
        }
        
        .chat-messages::-webkit-scrollbar-thumb {
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }
        
        .chat-theme-dark .chat-messages::-webkit-scrollbar-thumb {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .chat-input::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-input::-webkit-scrollbar-track {
            background-color: transparent;
        }
        
        .chat-input::-webkit-scrollbar-thumb {
            background-color: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }
        
        .chat-theme-dark .chat-input::-webkit-scrollbar-thumb {
            background-color: rgba(255, 255, 255, 0.2);
        }
    `;
    
    document.head.appendChild(styleElement);
}

// Add chat styles when the module is loaded
if (typeof document !== 'undefined') {
    addChatInterfaceStyles();
}

// Export the createChatInterface function
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = { createChatInterface };
}