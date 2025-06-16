/**
 * Knowledge Chat Component
 * 
 * Interactive chat interface that leverages the knowledge graph to provide
 * enhanced responses by incorporating structured knowledge.
 */

import { AthenaClient } from './athena-service.js';
import { TektonLLMClient } from './tekton-llm-client.js';

class KnowledgeChat extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.client = new AthenaClient();
    this.llmClient = new TektonLLMClient('athena-knowledge');
    this.messages = [];
    this.isTyping = false;
    this.fullResponse = '';
    this.activeEntities = new Set();
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
    this.checkLLMAvailability();
  }

  setupEventListeners() {
    // Message form submission
    const form = this.shadowRoot.querySelector('.chat-input-form');
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = this.shadowRoot.querySelector('.chat-input');
      const message = input.value.trim();

      if (message && !this.isTyping) {
        this.sendMessage(message);
        input.value = '';
        this.resizeTextarea(input);
      }
    });
    
    // Auto-resize textarea
    const textarea = this.shadowRoot.querySelector('.chat-input');
    textarea.addEventListener('input', () => {
      this.resizeTextarea(textarea);
    });
    
    // Clear chat button
    const clearButton = this.shadowRoot.querySelector('.btn-clear');
    clearButton.addEventListener('click', () => {
      this.clearChat();
    });
    
    // Settings button
    const settingsButton = this.shadowRoot.querySelector('.btn-settings');
    settingsButton.addEventListener('click', () => {
      this.toggleChatSettings();
    });
  }
  
  resizeTextarea(textarea) {
    textarea.style.height = 'auto';
    const height = Math.min(textarea.scrollHeight, 120);
    textarea.style.height = `${height}px`;
  }
  
  async checkLLMAvailability() {
    try {
      const available = await this.llmClient.checkAvailability();
      
      if (!available) {
        this.addMessage('system', 'LLM service is not available. Chat responses will be limited.');
      }
    } catch (error) {
      console.error('Error checking LLM availability:', error);
      this.addMessage('system', 'Unable to connect to LLM service. Chat responses will be limited.');
    }
  }

  async sendMessage(text) {
    // Add user message to chat
    this.addMessage('user', text);

    // Show typing indicator
    this.showTypingIndicator();

    try {
      // First, get knowledge context from API
      const knowledgeContext = await this.getKnowledgeContext(text);
      
      // Use knowledge-enhanced chat
      this.fullResponse = '';
      
      try {
        // Try streaming response first
        await this.client.streamKnowledgeChat(
          text,
          this.handleResponseChunk.bind(this)
        );
      } catch (streamError) {
        console.warn('Streaming chat failed, falling back to non-streaming:', streamError);
        
        // Fall back to non-streaming request
        const response = await this.client.knowledgeChat(text);
        this.hideTypingIndicator();
        
        if (response && response.answer) {
          this.addMessage('assistant', response.answer, true, knowledgeContext.entities);
        } else {
          throw new Error('Invalid response format');
        }
      }
    } catch (error) {
      console.error('Error in chat response:', error);
      
      // Try LLM client directly as a fallback
      try {
        this.fullResponse = '';
        await this.fallbackToDirectLLM(text);
      } catch (llmError) {
        console.error('Direct LLM fallback failed:', llmError);
        this.hideTypingIndicator();
        this.addMessage('system', 'Error: Failed to get a response. Please try again.');
      }
    }
  }

  async getKnowledgeContext(query) {
    try {
      // Call the API to get knowledge context
      const context = await this.client._request('/llm/knowledge/context', {
        method: 'POST',
        body: JSON.stringify({ query })
      });
      
      return context;
    } catch (error) {
      console.error('Failed to get knowledge context:', error);
      // Return empty context if API fails
      return { entities: [], relationships: [], context: {} };
    }
  }

  handleResponseChunk(chunk) {
    // Remove typing indicator if it exists
    this.hideTypingIndicator();

    // Check if we already have started a message
    const assistantMessage = this.shadowRoot.querySelector('.message.assistant:last-child');

    if (chunk.content) {
      this.fullResponse += chunk.content;

      if (assistantMessage) {
        // Update existing message content
        const contentEl = assistantMessage.querySelector('.message-content');
        if (contentEl) {
          contentEl.innerHTML = this.formatMessage(this.fullResponse);
        }
      } else {
        // Create new message
        this.addMessage('assistant', this.fullResponse, false);
      }

      // Scroll to bottom
      this.scrollToBottom();
    }

    // If this is the final chunk
    if (chunk.done) {
      // Make sure the message was added
      if (!assistantMessage) {
        this.addMessage('assistant', this.fullResponse);
      }
      
      // Process entity references
      if (chunk.entities) {
        this.processEntityReferences(chunk.entities);
      }

      // Reset state
      this.isTyping = false;
      this.fullResponse = '';
    }
  }
  
  async fallbackToDirectLLM(text) {
    // Use direct LLM client as fallback
    this.hideTypingIndicator();
    this.showTypingIndicator();
    
    try {
      // Create a simple system prompt
      const systemPrompt = `You are a knowledge assistant. Please answer the user's question in a helpful and informative way. If you don't know the answer, just say so.`;
      
      // Stream the response
      await this.llmClient.streamText(
        text,
        (chunk) => {
          // Hide typing indicator on first chunk
          this.hideTypingIndicator();
          
          // Update response
          this.fullResponse += chunk.content || '';
          
          // Update or create message
          const assistantMessage = this.shadowRoot.querySelector('.message.assistant:last-child');
          if (assistantMessage) {
            const contentEl = assistantMessage.querySelector('.message-content');
            if (contentEl) {
              contentEl.innerHTML = this.formatMessage(this.fullResponse);
            }
          } else {
            this.addMessage('assistant', this.fullResponse, false);
          }
          
          // Scroll to bottom
          this.scrollToBottom();
          
          // Reset when done
          if (chunk.done) {
            this.isTyping = false;
            this.fullResponse = '';
          }
        },
        {
          systemPrompt,
          temperature: 0.7
        }
      );
    } catch (error) {
      throw error;
    }
  }

  addMessage(role, content, shouldScroll = true, entities = []) {
    const messagesContainer = this.shadowRoot.querySelector('.chat-messages');
    const message = document.createElement('div');
    message.className = `message ${role}`;

    let formattedContent = this.formatMessage(content);
    
    // Store entities for this message
    if (entities && entities.length > 0) {
      message.dataset.entities = JSON.stringify(entities.map(e => e.entity_id));
      
      // Add entity IDs to active set
      entities.forEach(entity => {
        this.activeEntities.add(entity.entity_id);
      });
    }

    message.innerHTML = `
      <div class="message-header">
        <span class="message-sender">${role === 'user' ? 'You' : role === 'assistant' ? 'Knowledge Assistant' : 'System'}</span>
        <span class="message-time">${new Date().toLocaleTimeString()}</span>
      </div>
      <div class="message-content">${formattedContent}</div>
    `;

    messagesContainer.appendChild(message);

    // Store the message
    this.messages.push({
      role,
      content,
      timestamp: new Date().toISOString(),
      entities: entities ? entities.map(e => e.entity_id) : []
    });

    if (shouldScroll) {
      this.scrollToBottom();
    }
    
    // Add event listeners for entity references
    if (role === 'assistant') {
      setTimeout(() => {
        const entityRefs = message.querySelectorAll('.entity-reference');
        entityRefs.forEach(ref => {
          ref.addEventListener('click', (e) => {
            const entityId = e.target.dataset.entityId;
            if (entityId) {
              this.showEntityDetails(entityId);
            }
          });
          
          ref.addEventListener('mouseover', (e) => {
            const rect = e.target.getBoundingClientRect();
            const tooltip = this.shadowRoot.querySelector('.entity-tooltip');
            tooltip.textContent = e.target.dataset.entityType || e.target.textContent;
            tooltip.style.display = 'block';
            tooltip.style.left = `${rect.left}px`;
            tooltip.style.top = `${rect.top - 25}px`;
          });
          
          ref.addEventListener('mouseout', () => {
            const tooltip = this.shadowRoot.querySelector('.entity-tooltip');
            tooltip.style.display = 'none';
          });
        });
      }, 0);
    }
  }

  showTypingIndicator() {
    this.isTyping = true;

    const messagesContainer = this.shadowRoot.querySelector('.chat-messages');
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';

    typingIndicator.innerHTML = `
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    `;

    messagesContainer.appendChild(typingIndicator);
    this.scrollToBottom();
  }

  hideTypingIndicator() {
    const typingIndicator = this.shadowRoot.querySelector('.typing-indicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }

  formatMessage(text) {
    if (!text) return '';
    
    // Process entity references - looks for [[Entity Name:entity_id:entity_type]] format
    text = text.replace(/\[\[(.*?):(.*?):(.*?)\]\]/g, 
      '<span class="entity-reference" data-entity-id="$2" data-entity-type="$3">$1</span>'
    );
    
    // Also handle simpler format [[Entity Name]]
    text = text.replace(/\[\[(.*?)\]\]/g, '<span class="entity-reference">$1</span>');

    // Process relationship references ((...)) format
    text = text.replace(/\(\((.*?)\)\)/g, '<span class="relationship-reference">$1</span>');

    // Basic formatting with markdown-like syntax
    return text
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
  }
  
  processEntityReferences(entities) {
    // Update entity references with proper IDs and add event listeners
    const message = this.shadowRoot.querySelector('.message.assistant:last-child');
    if (!message) return;
    
    const contentEl = message.querySelector('.message-content');
    if (!contentEl) return;
    
    // Store entities for this message
    if (entities && entities.length > 0) {
      message.dataset.entities = JSON.stringify(entities.map(e => e.entity_id));
      
      // Add entity IDs to active set
      entities.forEach(entity => {
        this.activeEntities.add(entity.entity_id);
      });
    }
    
    // Re-format the message content to ensure entity references are properly linked
    const entityRefs = contentEl.querySelectorAll('.entity-reference');
    entityRefs.forEach((ref, index) => {
      if (index < entities.length) {
        ref.dataset.entityId = entities[index].entity_id;
        ref.dataset.entityType = entities[index].entity_type;
      }
    });
  }

  scrollToBottom() {
    const messagesContainer = this.shadowRoot.querySelector('.chat-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  clearChat() {
    // Clear chat messages
    const messagesContainer = this.shadowRoot.querySelector('.chat-messages');
    
    // Keep only system messages
    const systemMessages = Array.from(messagesContainer.querySelectorAll('.message.system'));
    messagesContainer.innerHTML = '';
    
    // Add back system messages
    systemMessages.forEach(msg => {
      messagesContainer.appendChild(msg);
    });
    
    // Add welcome message if no system messages
    if (systemMessages.length === 0) {
      this.addMessage('system', 'Welcome to Knowledge Chat. Ask me anything about the knowledge graph!');
    }
    
    // Clear stored messages except system ones
    this.messages = this.messages.filter(msg => msg.role === 'system');
    
    // Clear active entities
    this.activeEntities.clear();
  }
  
  toggleChatSettings() {
    const settingsPanel = this.shadowRoot.querySelector('.chat-settings-panel');
    settingsPanel.classList.toggle('open');
  }
  
  updateLLMSettings(settings) {
    if (this.llmClient && settings) {
      if (settings.provider) {
        this.llmClient.setProvider(settings.provider);
      }
      
      if (settings.model) {
        this.llmClient.setModel(settings.model);
      }
      
      if (settings.temperature !== undefined) {
        this.llmClient.setTemperature(settings.temperature);
      }
    }
  }
  
  async showEntityDetails(entityId) {
    try {
      // Get entity details
      const entity = await this.client.getEntity(entityId);
      
      if (!entity) {
        throw new Error('Entity not found');
      }
      
      // Show entity details popup
      const detailsPopup = document.createElement('div');
      detailsPopup.className = 'entity-details-popup';
      
      detailsPopup.innerHTML = `
        <div class="entity-details-header">
          <h3>${entity.name}</h3>
          <span class="entity-type-badge">${entity.entity_type}</span>
          <button class="close-button">&times;</button>
        </div>
        <div class="entity-details-content">
          <div class="entity-details-section">
            <h4>Properties</h4>
            <table class="entity-properties">
              ${Object.entries(entity.properties || {}).map(([key, value]) => `
                <tr>
                  <td>${key}</td>
                  <td>${typeof value === 'object' ? JSON.stringify(value) : value}</td>
                </tr>
              `).join('') || '<tr><td colspan="2">No properties</td></tr>'}
            </table>
          </div>
          <div class="entity-details-actions">
            <button class="btn btn-explore-entity" data-entity-id="${entity.entity_id}">
              Explore in Graph
            </button>
            <button class="btn btn-ask-about" data-entity-id="${entity.entity_id}">
              Ask About
            </button>
          </div>
        </div>
      `;
      
      this.shadowRoot.appendChild(detailsPopup);
      
      // Add event listeners
      detailsPopup.querySelector('.close-button').addEventListener('click', () => {
        detailsPopup.remove();
      });
      
      detailsPopup.querySelector('.btn-explore-entity').addEventListener('click', () => {
        // Dispatch custom event to notify parent component
        const event = new CustomEvent('explore-entity', {
          bubbles: true,
          composed: true,
          detail: { entityId: entity.entity_id }
        });
        this.dispatchEvent(event);
        
        detailsPopup.remove();
      });
      
      detailsPopup.querySelector('.btn-ask-about').addEventListener('click', () => {
        const input = this.shadowRoot.querySelector('.chat-input');
        input.value = `Tell me about ${entity.name}`;
        this.resizeTextarea(input);
        input.focus();
        
        detailsPopup.remove();
      });
      
      // Close on click outside
      setTimeout(() => {
        const handleOutsideClick = (e) => {
          if (!detailsPopup.contains(e.target)) {
            detailsPopup.remove();
            document.removeEventListener('click', handleOutsideClick);
          }
        };
        
        document.addEventListener('click', handleOutsideClick);
      }, 0);
      
    } catch (error) {
      console.error('Error fetching entity details:', error);
      this.showError('Failed to load entity details');
    }
  }
  
  showError(message) {
    const errorContainer = document.createElement('div');
    errorContainer.className = 'error-message';
    errorContainer.textContent = message;
    
    this.shadowRoot.appendChild(errorContainer);
    
    setTimeout(() => {
      errorContainer.remove();
    }, 5000);
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        /* Knowledge Chat CSS */
        :host {
          display: block;
          height: 100%;
          font-family: var(--font-family, sans-serif);
          --primary-color: #4a86e8;
          --secondary-color: #6c757d;
          --success-color: #34A853;
          --user-message-bg: #e3f2fd;
          --assistant-message-bg: #f8f9fa;
          --system-message-bg: #fff3cd;
          --border-color: #dee2e6;
          --background-color: #ffffff;
        }
        
        /* Theme support */
        :host([data-theme="dark"]) {
          --primary-color: #5c9aff;
          --secondary-color: #adb5bd;
          --success-color: #4ade80;
          --user-message-bg: #1e3a8a;
          --assistant-message-bg: #374151;
          --system-message-bg: #4b5563;
          --border-color: #4b5563;
          --background-color: #111827;
          color: #e5e7eb;
        }

        .knowledge-chat {
          display: flex;
          flex-direction: column;
          height: 100%;
          position: relative;
          background-color: var(--background-color);
        }

        .chat-header {
          padding: 1rem;
          border-bottom: 1px solid var(--border-color);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .header-title {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .header-title h2 {
          margin: 0;
        }
        
        .header-controls {
          display: flex;
          gap: 0.5rem;
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .message {
          display: flex;
          flex-direction: column;
          max-width: 80%;
          padding: 0.75rem;
          border-radius: 8px;
          position: relative;
        }

        .message.user {
          align-self: flex-end;
          background-color: var(--user-message-bg);
          border-bottom-right-radius: 0;
          color: var(--dark-color);
        }

        .message.assistant {
          align-self: flex-start;
          background-color: var(--assistant-message-bg);
          border-bottom-left-radius: 0;
          color: var(--dark-color);
        }

        .message.system {
          align-self: center;
          background-color: var(--system-message-bg);
          width: auto;
          max-width: 90%;
          text-align: center;
          font-style: italic;
          color: var(--dark-color);
        }

        .message-header {
          display: flex;
          justify-content: space-between;
          font-size: 0.8rem;
          margin-bottom: 0.5rem;
        }

        .message-sender {
          font-weight: bold;
        }

        .message-time {
          color: #666;
        }

        .message-content {
          word-break: break-word;
        }

        .entity-reference {
          color: var(--primary-color);
          border-bottom: 1px dotted var(--primary-color);
          cursor: pointer;
        }

        .relationship-reference {
          color: #9c27b0;
          font-style: italic;
        }

        .typing-indicator {
          align-self: flex-start;
          display: flex;
          gap: 0.5rem;
          padding: 1rem;
          background-color: var(--assistant-message-bg);
          border-radius: 8px;
          border-bottom-left-radius: 0;
        }

        .typing-indicator .dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: #333;
          animation: typing-dot 1.4s infinite ease-in-out both;
        }

        .typing-indicator .dot:nth-child(1) {
          animation-delay: 0s;
        }

        .typing-indicator .dot:nth-child(2) {
          animation-delay: 0.2s;
        }

        .typing-indicator .dot:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes typing-dot {
          0%, 80%, 100% { 
            transform: scale(0.8);
            opacity: 0.8;
          }
          40% { 
            transform: scale(1.2);
            opacity: 1;
          }
        }

        .chat-input-container {
          padding: 1rem;
          border-top: 1px solid var(--border-color);
        }

        .chat-input-form {
          display: flex;
          gap: 0.5rem;
        }

        .chat-input {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid var(--border-color);
          border-radius: 4px;
          resize: none;
          min-height: 44px;
          max-height: 120px;
          overflow-y: auto;
          background-color: var(--background-color);
          color: var(--dark-color);
        }

        .send-button {
          padding: 0.75rem 1.5rem;
          background-color: var(--primary-color);
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .send-button:hover {
          opacity: 0.9;
        }
        
        .btn {
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--border-color);
          border-radius: 4px;
          background-color: var(--background-color);
          cursor: pointer;
          color: var(--dark-color);
        }

        .btn:hover {
          background-color: var(--light-color);
        }
        
        .entity-tooltip {
          position: absolute;
          background-color: rgba(0, 0, 0, 0.7);
          color: white;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          pointer-events: none;
          display: none;
          z-index: 1000;
        }
        
        .entity-details-popup {
          position: fixed;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          background-color: var(--background-color);
          border: 1px solid var(--border-color);
          border-radius: 8px;
          width: 400px;
          max-width: 90%;
          max-height: 90%;
          overflow-y: auto;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          z-index: 1001;
        }
        
        .entity-details-header {
          padding: 1rem;
          border-bottom: 1px solid var(--border-color);
          display: flex;
          align-items: center;
          position: sticky;
          top: 0;
          background-color: var(--background-color);
          z-index: 1;
        }
        
        .entity-details-header h3 {
          margin: 0;
          flex: 1;
        }
        
        .entity-type-badge {
          background-color: var(--secondary-color);
          color: white;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          margin: 0 0.5rem;
        }
        
        .entity-details-content {
          padding: 1rem;
        }
        
        .entity-details-section {
          margin-bottom: 1rem;
        }
        
        .entity-details-section h4 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          border-bottom: 1px solid var(--border-color);
          padding-bottom: 0.25rem;
        }
        
        .entity-properties {
          width: 100%;
          border-collapse: collapse;
        }
        
        .entity-properties td {
          padding: 0.25rem;
          border-bottom: 1px solid var(--border-color);
        }
        
        .entity-properties td:first-child {
          font-weight: bold;
          width: 40%;
        }
        
        .entity-details-actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 1rem;
        }
        
        .chat-settings-panel {
          position: absolute;
          top: 0;
          right: 0;
          width: 300px;
          height: 100%;
          background-color: var(--background-color);
          border-left: 1px solid var(--border-color);
          transform: translateX(100%);
          transition: transform 0.3s ease;
          z-index: 1000;
        }
        
        .chat-settings-panel.open {
          transform: translateX(0);
        }
        
        .chat-settings-header {
          padding: 1rem;
          border-bottom: 1px solid var(--border-color);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .chat-settings-content {
          padding: 1rem;
        }
        
        .chat-settings-section {
          margin-bottom: 1.5rem;
        }
        
        .chat-settings-section h3 {
          margin-top: 0;
          margin-bottom: 0.5rem;
          border-bottom: 1px solid var(--border-color);
          padding-bottom: 0.5rem;
        }
        
        .setting-item {
          margin-bottom: 1rem;
        }
        
        .setting-label {
          display: block;
          margin-bottom: 0.25rem;
          font-weight: bold;
        }
        
        .setting-input {
          width: 100%;
          padding: 0.375rem;
          border: 1px solid var(--border-color);
          border-radius: 4px;
        }
        
        .close-button {
          background: none;
          border: none;
          font-size: 1.25rem;
          cursor: pointer;
          padding: 0;
          line-height: 1;
          color: var(--dark-color);
        }
        
        .error-message {
          position: fixed;
          bottom: 1rem;
          left: 50%;
          transform: translateX(-50%);
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem 1rem;
          border-radius: 4px;
          z-index: 1001;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
      </style>

      <div class="knowledge-chat">
        <div class="chat-header">
          <div class="header-title">
            <h2>Knowledge Chat</h2>
          </div>
          <div class="header-controls">
            <button class="btn btn-clear">Clear</button>
            <button class="btn btn-settings">Settings</button>
          </div>
        </div>

        <div class="chat-messages">
          <div class="message system">
            <div class="message-content">
              Welcome to Knowledge Chat. Ask me anything about the knowledge graph!
            </div>
          </div>
        </div>

        <div class="chat-input-container">
          <form class="chat-input-form">
            <textarea 
              class="chat-input" 
              placeholder="Ask a question about the knowledge graph..." 
              rows="1"></textarea>
            <button type="submit" class="send-button">Send</button>
          </form>
        </div>
        
        <div class="entity-tooltip"></div>
        
        <div class="chat-settings-panel">
          <div class="chat-settings-header">
            <h3>Chat Settings</h3>
            <button class="close-button">&times;</button>
          </div>
          <div class="chat-settings-content">
            <div class="chat-settings-section">
              <h3>Knowledge Enhancement</h3>
              <div class="setting-item">
                <label class="setting-label" for="knowledge-threshold">Knowledge Relevance Threshold</label>
                <input type="range" class="setting-input" id="knowledge-threshold" min="0" max="1" step="0.1" value="0.7">
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem;">
                  <span>Low</span>
                  <span>High</span>
                </div>
              </div>
              <div class="setting-item">
                <label class="setting-label" for="max-entities">Maximum Entities</label>
                <input type="number" class="setting-input" id="max-entities" min="1" max="20" value="5">
              </div>
            </div>
            
            <div class="chat-settings-section">
              <h3>Display Settings</h3>
              <div class="setting-item">
                <label class="setting-label" for="highlight-entities">Highlight Entities</label>
                <input type="checkbox" id="highlight-entities" checked>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }
}

customElements.define('knowledge-chat', KnowledgeChat);

export { KnowledgeChat };