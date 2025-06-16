/**
 * Apollo Executive Coordinator Component
 * 
 * Provides a comprehensive interface for managing LLM operations, token budgeting,
 * protocol enforcement, and predictive planning in the Tekton system.
 */

import { ApolloClient } from './apollo-service.js';

class ApolloComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.client = new ApolloClient();
    this.activeTab = 'dashboard';
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
    this.loadSessionData();
  }

  async loadSessionData() {
    try {
      const status = await this.client.getStatus();
      console.log('Apollo Status:', status);
      
      // Update session count in UI
      const sessionCountElem = this.shadowRoot.querySelector('.session-count');
      if (sessionCountElem && status.session_count !== undefined) {
        sessionCountElem.textContent = status.session_count;
      }
      
      // Update token count in UI
      const tokenCountElem = this.shadowRoot.querySelector('.token-count');
      if (tokenCountElem && status.total_tokens !== undefined) {
        tokenCountElem.textContent = status.total_tokens;
      }
    } catch (error) {
      console.error('Error loading Apollo status:', error);
      this.showError('Failed to connect to Apollo service');
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

    // Attention Chat button
    const attentionChatButton = this.shadowRoot.querySelector('.apollo__chat-option--attention');
    attentionChatButton.addEventListener('click', () => {
      console.log('Attention Chat clicked');
      // Implement Attention Chat functionality
    });

    // Team Chat button
    const teamChatButton = this.shadowRoot.querySelector('.apollo__chat-option--team');
    teamChatButton.addEventListener('click', () => {
      console.log('Team Chat clicked');
      // Implement Team Chat functionality
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
      dashboard: {
        refreshRate: parseInt(this.shadowRoot.querySelector('select[name="refresh-rate"]').value),
        displayMode: this.shadowRoot.querySelector('select[name="display-mode"]').value
      },
      tokens: {
        budgetStrategy: this.shadowRoot.querySelector('select[name="budget-strategy"]').value,
        compressionThreshold: parseInt(this.shadowRoot.querySelector('input[name="compression-threshold"]').value)
      },
      display: {
        theme: this.shadowRoot.querySelector('select[name="theme"]').value
      }
    };
    
    // Save to localStorage
    localStorage.setItem('apollo-settings', JSON.stringify(settings));
    
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
    
    // Apply dashboard settings
    if (settings.dashboard) {
      // Update refresh rate if needed
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
      
      if (settings.dashboard.refreshRate > 0) {
        this.refreshInterval = setInterval(() => {
          this.loadSessionData();
        }, settings.dashboard.refreshRate * 1000);
      }
    }
  }
  
  loadSettings() {
    const savedSettings = localStorage.getItem('apollo-settings');
    if (savedSettings) {
      try {
        const settings = JSON.parse(savedSettings);
        this.applySettings(settings);
        
        // Update form controls
        if (settings.dashboard) {
          if (settings.dashboard.refreshRate) {
            this.shadowRoot.querySelector('select[name="refresh-rate"]').value = settings.dashboard.refreshRate;
          }
          if (settings.dashboard.displayMode) {
            this.shadowRoot.querySelector('select[name="display-mode"]').value = settings.dashboard.displayMode;
          }
        }
        
        if (settings.tokens) {
          if (settings.tokens.budgetStrategy) {
            this.shadowRoot.querySelector('select[name="budget-strategy"]').value = settings.tokens.budgetStrategy;
          }
          if (settings.tokens.compressionThreshold) {
            this.shadowRoot.querySelector('input[name="compression-threshold"]').value = settings.tokens.compressionThreshold;
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
        /* Apollo Component CSS */
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

        .apollo-component {
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

        .apollo__menu-bar {
          border-bottom: 1px solid var(--border-color);
        }

        .apollo__chat-options {
          display: flex;
          padding: 0.5rem 1rem;
        }

        .apollo__chat-option {
          padding: 0.5rem 1rem;
          cursor: pointer;
          background-color: var(--background-color);
          border: 1px solid var(--border-color);
          border-radius: 4px;
          margin-right: 0.5rem;
        }

        .apollo__chat-option:hover {
          background-color: var(--light-color);
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

        /* Health status indicators */
        .health-indicator {
          display: inline-block;
          height: 12px;
          width: 12px;
          border-radius: 50%;
          margin-right: 0.5rem;
        }

        .health-indicator--healthy {
          background-color: var(--success-color);
        }

        .health-indicator--warning {
          background-color: var(--warning-color);
        }

        .health-indicator--critical {
          background-color: var(--danger-color);
        }

        /* Grid layout for dashboard */
        .dashboard-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1rem;
          padding: 1rem;
        }

        .dashboard-card {
          background-color: var(--background-color);
          border: 1px solid var(--border-color);
          border-radius: 4px;
          padding: 1rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .dashboard-card__header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .dashboard-card__title {
          font-weight: bold;
          margin: 0;
        }

        .dashboard-card__body {
          margin-bottom: 0.5rem;
        }

        .dashboard-card__footer {
          font-size: 0.875rem;
          color: var(--secondary-color);
        }

        /* Token budget visualization */
        .token-budget {
          height: 8px;
          background-color: var(--light-color);
          border-radius: 4px;
          margin: 0.5rem 0;
          overflow: hidden;
        }

        .token-budget__used {
          height: 100%;
          background-color: var(--primary-color);
          width: 0%; /* Will be set dynamically */
        }

        /* Session list */
        .session-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .session-item {
          padding: 0.75rem;
          border-bottom: 1px solid var(--border-color);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .session-item:last-child {
          border-bottom: none;
        }

        .session-item__name {
          font-weight: bold;
        }

        .session-item__status {
          display: flex;
          align-items: center;
        }
      </style>

      <div class="apollo-component">
        <div class="component-header">
          <div class="component-title">
            <img src="/images/icon.jpg" alt="Apollo" class="logo">
            <h1>Apollo Executive Coordinator</h1>
          </div>
          <div class="header-content">
            <div class="header-stats">
              <div class="stat-item">
                <span>Active Sessions:</span>
                <span class="stat-value session-count">-</span>
              </div>
              <div class="stat-item">
                <span>Total Tokens:</span>
                <span class="stat-value token-count">-</span>
              </div>
            </div>
          </div>
          <div class="header-controls">
            <button class="btn btn-settings">
              <span>Settings</span>
            </button>
          </div>
        </div>

        <div class="apollo__menu-bar">
          <div class="apollo__chat-options">
            <div class="apollo__chat-option apollo__chat-option--attention">Attention Chat</div>
            <div class="apollo__chat-option apollo__chat-option--team">Team Chat</div>
          </div>
        </div>

        <div class="tabs">
          <div class="tab active" data-tab="dashboard">Dashboard</div>
          <div class="tab" data-tab="sessions">Sessions</div>
          <div class="tab" data-tab="tokens">Token Budgets</div>
          <div class="tab" data-tab="protocols">Protocols</div>
          <div class="tab" data-tab="forecasting">Forecasting</div>
          <div class="tab" data-tab="actions">Actions</div>
        </div>

        <div id="dashboard-tab" class="tab-content" style="display: block; height: 100%;">
          <div class="dashboard-grid">
            <div class="dashboard-card">
              <div class="dashboard-card__header">
                <h3 class="dashboard-card__title">System Status</h3>
                <div class="health-indicator health-indicator--healthy"></div>
              </div>
              <div class="dashboard-card__body">
                <p>All systems operational</p>
                <p>4 LLM sessions active</p>
              </div>
              <div class="dashboard-card__footer">
                Last updated: Just now
              </div>
            </div>

            <div class="dashboard-card">
              <div class="dashboard-card__header">
                <h3 class="dashboard-card__title">Token Usage</h3>
              </div>
              <div class="dashboard-card__body">
                <p>Total allocation: 100,000 tokens</p>
                <p>Used: 38,420 tokens</p>
                <div class="token-budget">
                  <div class="token-budget__used" style="width: 38.4%"></div>
                </div>
              </div>
              <div class="dashboard-card__footer">
                Current compression level: None
              </div>
            </div>

            <div class="dashboard-card">
              <div class="dashboard-card__header">
                <h3 class="dashboard-card__title">Active Sessions</h3>
              </div>
              <div class="dashboard-card__body">
                <ul class="session-list">
                  <li class="session-item">
                    <span class="session-item__name">Codex</span>
                    <span class="session-item__status">
                      <div class="health-indicator health-indicator--healthy"></div>
                      Healthy
                    </span>
                  </li>
                  <li class="session-item">
                    <span class="session-item__name">Athena</span>
                    <span class="session-item__status">
                      <div class="health-indicator health-indicator--healthy"></div>
                      Healthy
                    </span>
                  </li>
                  <li class="session-item">
                    <span class="session-item__name">Rhetor</span>
                    <span class="session-item__status">
                      <div class="health-indicator health-indicator--warning"></div>
                      High Usage
                    </span>
                  </li>
                  <li class="session-item">
                    <span class="session-item__name">Engram</span>
                    <span class="session-item__status">
                      <div class="health-indicator health-indicator--healthy"></div>
                      Healthy
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div id="sessions-tab" class="tab-content">
          <div class="placeholder-content">
            <h2>LLM Sessions</h2>
            <p>Detailed session information and metrics will be implemented in the next update.</p>
          </div>
        </div>

        <div id="tokens-tab" class="tab-content">
          <div class="placeholder-content">
            <h2>Token Budget Management</h2>
            <p>Token budget allocation and management tools will be implemented in the next update.</p>
          </div>
        </div>

        <div id="protocols-tab" class="tab-content">
          <div class="placeholder-content">
            <h2>Protocol Management</h2>
            <p>Protocol configuration and enforcement settings will be implemented in the next update.</p>
          </div>
        </div>

        <div id="forecasting-tab" class="tab-content">
          <div class="placeholder-content">
            <h2>Predictive Forecasting</h2>
            <p>LLM behavior forecasting visualizations will be implemented in the next update.</p>
          </div>
        </div>

        <div id="actions-tab" class="tab-content">
          <div class="placeholder-content">
            <h2>LLM Actions</h2>
            <p>Action execution interface will be implemented in the next update.</p>
          </div>
        </div>

        <div class="settings-panel">
          <div class="settings-header">
            <h2>Settings</h2>
            <button class="close-button">&times;</button>
          </div>
          <div class="settings-content">
            <div class="settings-section">
              <h3>Dashboard Settings</h3>
              <div class="setting-item">
                <label class="setting-label" for="refresh-rate">Refresh Rate</label>
                <select class="setting-input" name="refresh-rate" id="refresh-rate">
                  <option value="0">Manual Refresh</option>
                  <option value="5">5 seconds</option>
                  <option value="15">15 seconds</option>
                  <option value="30" selected>30 seconds</option>
                  <option value="60">1 minute</option>
                </select>
              </div>
              <div class="setting-item">
                <label class="setting-label" for="display-mode">Display Mode</label>
                <select class="setting-input" name="display-mode" id="display-mode">
                  <option value="grid" selected>Grid</option>
                  <option value="list">List</option>
                  <option value="compact">Compact</option>
                </select>
              </div>
            </div>

            <div class="settings-section">
              <h3>Token Budget Settings</h3>
              <div class="setting-item">
                <label class="setting-label" for="budget-strategy">Budget Strategy</label>
                <select class="setting-input" name="budget-strategy" id="budget-strategy">
                  <option value="fixed">Fixed Allocation</option>
                  <option value="dynamic" selected>Dynamic Allocation</option>
                  <option value="priority">Priority-Based</option>
                </select>
              </div>
              <div class="setting-item">
                <label class="setting-label" for="compression-threshold">Compression Threshold (%)</label>
                <input type="range" min="50" max="95" step="5" value="85" class="setting-input" name="compression-threshold" id="compression-threshold">
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

customElements.define('apollo-component', ApolloComponent);

// Export the component for external use
export { ApolloComponent };