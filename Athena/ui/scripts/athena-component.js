/**
 * Athena Knowledge Graph Component
 * 
 * Provides a comprehensive interface for working with the Athena knowledge graph,
 * including visualization, entity management, knowledge-enhanced chat, and query building.
 */

import { AthenaClient } from './athena-service.js';
import { GraphVisualization } from './graph-visualization.js';
import { KnowledgeChat } from './knowledge-chat.js';
import { TektonLLMClient } from './tekton-llm-client.js';

class AthenaComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.client = new AthenaClient();
    this.llmClient = new TektonLLMClient('athena-knowledge');
    this.activeTab = 'graph';
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
    this.loadGraphData();
  }

  async loadGraphData() {
    try {
      const status = await this.client.getStatus();
      console.log('Athena Status:', status);
      
      // Update entity count in UI
      const entityCountElem = this.shadowRoot.querySelector('.entity-count');
      if (entityCountElem && status.entity_count !== undefined) {
        entityCountElem.textContent = status.entity_count;
      }
      
      // Update relationship count in UI
      const relationshipCountElem = this.shadowRoot.querySelector('.relationship-count');
      if (relationshipCountElem && status.relationship_count !== undefined) {
        relationshipCountElem.textContent = status.relationship_count;
      }
    } catch (error) {
      console.error('Error loading Athena status:', error);
      this.showError('Failed to connect to Athena service');
    }
  }

  setupEventListeners() {
    // Tab switching
    const tabs = this.shadowRoot.querySelectorAll('.tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        this.switchTab(tab.dataset.tab);
      });
    });

    // Settings button
    const settingsButton = this.shadowRoot.querySelector('.btn-settings');
    settingsButton.addEventListener('click', () => {
      this.toggleSettings();
    });
    
    // Close settings button
    const closeSettingsButton = this.shadowRoot.querySelector('.close-button');
    closeSettingsButton.addEventListener('click', () => {
      this.toggleSettings();
    });
    
    // Save settings button
    const saveSettingsButton = this.shadowRoot.querySelector('.btn-save-settings');
    saveSettingsButton.addEventListener('click', () => {
      this.saveSettings();
    });
  }

  switchTab(tabId) {
    // Update active tab
    this.activeTab = tabId;

    // Update tab UI
    const tabs = this.shadowRoot.querySelectorAll('.tab');
    tabs.forEach(tab => {
      tab.classList.toggle('active', tab.dataset.tab === tabId);
    });

    // Update content sections
    const sections = this.shadowRoot.querySelectorAll('.tab-content');
    sections.forEach(section => {
      section.style.display = section.id === `${tabId}-tab` ? 'block' : 'none';
    });
  }

  toggleSettings() {
    const settingsPanel = this.shadowRoot.querySelector('.settings-panel');
    settingsPanel.classList.toggle('open');
  }
  
  saveSettings() {
    // Collect settings
    const settings = {
      graph: {
        layout: this.shadowRoot.querySelector('select[name="layout-algorithm"]').value,
        nodeScale: parseFloat(this.shadowRoot.querySelector('input[name="node-scale"]').value)
      },
      llm: {
        provider: this.shadowRoot.querySelector('select[name="llm-provider"]').value,
        model: this.shadowRoot.querySelector('select[name="llm-model"]').value,
        temperature: parseFloat(this.shadowRoot.querySelector('input[name="temperature"]').value)
      },
      display: {
        theme: this.shadowRoot.querySelector('select[name="theme"]').value
      }
    };
    
    // Save to localStorage
    localStorage.setItem('athena-settings', JSON.stringify(settings));
    
    // Apply settings
    this.applySettings(settings);
    
    // Close settings panel
    this.toggleSettings();
    
    // Show success message
    this.showMessage('Settings saved successfully');
  }
  
  applySettings(settings) {
    // Apply theme
    if (settings.display && settings.display.theme) {
      document.documentElement.setAttribute('data-theme', settings.display.theme);
      this.shadowRoot.host.setAttribute('data-theme', settings.display.theme);
    }
    
    // Apply LLM settings
    if (settings.llm) {
      if (this.llmClient) {
        this.llmClient.setProvider(settings.llm.provider);
        this.llmClient.setModel(settings.llm.model);
        this.llmClient.setTemperature(settings.llm.temperature);
      }
      
      // Update chat component
      const chatComponent = this.shadowRoot.querySelector('knowledge-chat');
      if (chatComponent) {
        chatComponent.updateLLMSettings(settings.llm);
      }
    }
    
    // Apply graph settings
    if (settings.graph) {
      const graphComponent = this.shadowRoot.querySelector('graph-visualization');
      if (graphComponent) {
        graphComponent.updateSettings(settings.graph);
      }
    }
  }
  
  loadSettings() {
    const savedSettings = localStorage.getItem('athena-settings');
    if (savedSettings) {
      try {
        const settings = JSON.parse(savedSettings);
        this.applySettings(settings);
        
        // Update form controls
        if (settings.graph) {
          if (settings.graph.layout) {
            this.shadowRoot.querySelector('select[name="layout-algorithm"]').value = settings.graph.layout;
          }
          if (settings.graph.nodeScale) {
            this.shadowRoot.querySelector('input[name="node-scale"]').value = settings.graph.nodeScale;
          }
        }
        
        if (settings.llm) {
          if (settings.llm.provider) {
            this.shadowRoot.querySelector('select[name="llm-provider"]').value = settings.llm.provider;
          }
          if (settings.llm.model) {
            this.shadowRoot.querySelector('select[name="llm-model"]').value = settings.llm.model;
          }
          if (settings.llm.temperature !== undefined) {
            this.shadowRoot.querySelector('input[name="temperature"]').value = settings.llm.temperature;
          }
        }
        
        if (settings.display && settings.display.theme) {
          this.shadowRoot.querySelector('select[name="theme"]').value = settings.display.theme;
        }
      } catch (error) {
        console.error('Error parsing saved settings:', error);
      }
    }
  }

  showError(message, duration = 5000) {
    const errorContainer = document.createElement('div');
    errorContainer.className = 'error-message';
    errorContainer.textContent = message;
    
    this.shadowRoot.appendChild(errorContainer);
    
    setTimeout(() => {
      errorContainer.remove();
    }, duration);
  }
  
  showMessage(message, duration = 3000) {
    const messageContainer = document.createElement('div');
    messageContainer.className = 'success-message';
    messageContainer.textContent = message;
    
    this.shadowRoot.appendChild(messageContainer);
    
    setTimeout(() => {
      messageContainer.remove();
    }, duration);
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        /* Athena Component CSS */
        :host {
          display: block;
          height: 100%;
          width: 100%;
          --primary-color: #4a86e8;
          --secondary-color: #6c757d;
          --success-color: #34A853;
          --warning-color: #FBBC05;
          --danger-color: #EA4335;
          --light-color: #f8f9fa;
          --dark-color: #343a40;
          --border-color: #dee2e6;
          --background-color: #ffffff;
          font-family: var(--font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif);
        }

        /* Theme support */
        :host([data-theme="dark"]) {
          --primary-color: #5c9aff;
          --secondary-color: #adb5bd;
          --success-color: #4ade80;
          --warning-color: #fde047;
          --danger-color: #f87171;
          --light-color: #4b5563;
          --dark-color: #e5e7eb;
          --border-color: #4b5563;
          --background-color: #111827;
          color: #e5e7eb;
        }

        .athena-component {
          display: flex;
          flex-direction: column;
          height: 100%;
          background-color: var(--background-color);
          color: var(--dark-color);
        }

        .component-header {
          padding: 1rem;
          border-bottom: 1px solid var(--border-color);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .component-title {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .component-title h1 {
          margin: 0;
          font-size: 1.5rem;
        }

        .logo {
          height: 2rem;
          width: auto;
        }

        .header-controls {
          display: flex;
          gap: 0.5rem;
        }

        .header-stats {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-right: 1rem;
          font-size: 0.875rem;
        }

        .stat-item {
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }

        .stat-value {
          font-weight: bold;
        }

        .tabs {
          display: flex;
          border-bottom: 1px solid var(--border-color);
        }

        .tab {
          padding: 0.75rem 1.5rem;
          cursor: pointer;
          border-bottom: 3px solid transparent;
          transition: all 0.2s ease;
        }

        .tab:hover {
          background-color: var(--light-color);
        }

        .tab.active {
          border-bottom-color: var(--primary-color);
          font-weight: bold;
        }

        .tab-content {
          flex: 1;
          display: none;
          height: 100%;
          overflow: hidden;
        }

        .tab-content.active {
          display: block;
        }

        .btn {
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--border-color);
          border-radius: 4px;
          background-color: var(--background-color);
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          color: var(--dark-color);
        }

        .btn:hover {
          background-color: var(--light-color);
        }

        .btn-primary {
          background-color: var(--primary-color);
          color: white;
          border-color: var(--primary-color);
        }

        .btn-primary:hover {
          opacity: 0.9;
          background-color: var(--primary-color);
        }

        .settings-panel {
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
          overflow-y: auto;
        }

        .settings-panel.open {
          transform: translateX(0);
        }

        .settings-header {
          padding: 1rem;
          border-bottom: 1px solid var(--border-color);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .settings-content {
          padding: 1rem;
        }

        .settings-section {
          margin-bottom: 1.5rem;
        }

        .settings-section h3 {
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
          background-color: var(--background-color);
          color: var(--dark-color);
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
          background-color: var(--danger-color);
          color: white;
          padding: 0.75rem 1rem;
          border-radius: 4px;
          z-index: 1001;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .success-message {
          position: fixed;
          bottom: 1rem;
          left: 50%;
          transform: translateX(-50%);
          background-color: var(--success-color);
          color: white;
          padding: 0.75rem 1rem;
          border-radius: 4px;
          z-index: 1001;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .placeholder-content {
          padding: 2rem;
          text-align: center;
        }

        /* Make sure child components fill the container */
        graph-visualization, knowledge-chat {
          display: block;
          height: 100%;
          width: 100%;
        }
      </style>

      <div class="athena-component">
        <div class="component-header">
          <div class="component-title">
            <img src="/images/icon.jpg" alt="Athena" class="logo">
            <h1>Athena Knowledge Graph</h1>
          </div>
          <div class="header-content">
            <div class="header-stats">
              <div class="stat-item">
                <span>Entities:</span>
                <span class="stat-value entity-count">-</span>
              </div>
              <div class="stat-item">
                <span>Relationships:</span>
                <span class="stat-value relationship-count">-</span>
              </div>
            </div>
          </div>
          <div class="header-controls">
            <button class="btn btn-settings">
              <span>Settings</span>
            </button>
          </div>
        </div>

        <div class="tabs">
          <div class="tab active" data-tab="graph">Knowledge Graph</div>
          <div class="tab" data-tab="chat">Knowledge Chat</div>
          <div class="tab" data-tab="entities">Entities</div>
          <div class="tab" data-tab="query">Query Builder</div>
        </div>

        <div id="graph-tab" class="tab-content" style="display: block; height: 100%;">
          <graph-visualization></graph-visualization>
        </div>

        <div id="chat-tab" class="tab-content" style="height: 100%;">
          <knowledge-chat></knowledge-chat>
        </div>

        <div id="entities-tab" class="tab-content">
          <div class="placeholder-content">
            <h2>Entity Management</h2>
            <p>Entity management interface will be implemented in the next update.</p>
          </div>
        </div>

        <div id="query-tab" class="tab-content">
          <div class="placeholder-content">
            <h2>Query Builder</h2>
            <p>Query builder interface will be implemented in the next update.</p>
          </div>
        </div>

        <div class="settings-panel">
          <div class="settings-header">
            <h2>Settings</h2>
            <button class="close-button">&times;</button>
          </div>
          <div class="settings-content">
            <div class="settings-section">
              <h3>Graph Settings</h3>
              <div class="setting-item">
                <label class="setting-label" for="layout-algorithm">Layout Algorithm</label>
                <select class="setting-input" name="layout-algorithm" id="layout-algorithm">
                  <option value="force-directed">Force-Directed</option>
                  <option value="circular">Circular</option>
                  <option value="hierarchical">Hierarchical</option>
                  <option value="radial">Radial</option>
                </select>
              </div>
              <div class="setting-item">
                <label class="setting-label" for="node-scale">Node Size Scale</label>
                <input type="range" min="0.5" max="2" step="0.1" value="1" class="setting-input" name="node-scale" id="node-scale">
              </div>
            </div>

            <div class="settings-section">
              <h3>LLM Settings</h3>
              <div class="setting-item">
                <label class="setting-label" for="llm-provider">Provider</label>
                <select class="setting-input" name="llm-provider" id="llm-provider">
                  <option value="claude">Claude</option>
                  <option value="gpt4">GPT-4</option>
                  <option value="local">Local LLM</option>
                </select>
              </div>
              <div class="setting-item">
                <label class="setting-label" for="llm-model">Model</label>
                <select class="setting-input" name="llm-model" id="llm-model">
                  <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                  <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                  <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                </select>
              </div>
              <div class="setting-item">
                <label class="setting-label" for="temperature">Temperature</label>
                <input type="range" min="0" max="1" step="0.1" value="0.7" class="setting-input" name="temperature" id="temperature">
              </div>
            </div>

            <div class="settings-section">
              <h3>Display Settings</h3>
              <div class="setting-item">
                <label class="setting-label" for="theme">Theme</label>
                <select class="setting-input" name="theme" id="theme">
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System Default</option>
                </select>
              </div>
            </div>

            <button class="btn btn-primary btn-save-settings" style="width: 100%;">Save Settings</button>
          </div>
        </div>
      </div>
    `;

    // Load saved settings
    this.loadSettings();
  }
}

customElements.define('athena-component', AthenaComponent);

// Export the component for external use
export { AthenaComponent };