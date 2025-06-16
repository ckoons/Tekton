# UI Implementation Guide

## Overview

This guide covers implementing the Hephaestus UI component for your Tekton component. The UI serves as a visibility layer, with LLMs handling complex interactions through chat interfaces.

## ⚠️ Important Update

Following the Shared Utilities Sprint, ensure your UI component:
- ✅ Connects to the backend using environment variables (no hardcoded ports)
- ✅ Shows health status from the standardized `/health` endpoint
- ✅ Displays status information from the `/status` endpoint
- ✅ Uses consistent error handling for disconnected components
- ✅ Follows the component color scheme in UI_Styling_Standards.md

## UI Architecture Principles

1. **Direct HTML Injection** - No Shadow DOM, direct component injection
2. **BEM CSS Naming** - Block Element Modifier convention
3. **Self-Contained Components** - No shared utilities between components
4. **Simple Visibility Layer** - UI shows state, LLMs handle complexity
5. **Chat Integration** - Every panel includes LLM chat capabilities

## File Structure

```
ui/
├── mycomponent-component.html    # Main component HTML
├── scripts/
│   └── mycomponent.js           # Component JavaScript
└── styles/
    └── mycomponent.css          # Component styles (BEM)
```

## Component HTML Structure

### mycomponent-component.html

```html
<!-- 
  MyComponent UI Component
  This component provides a web interface for MyComponent functionality
-->
<div id="mycomponent-component">
  <div class="mycomponent">
    <!-- Header Section -->
    <div class="mycomponent__header">
      <div class="mycomponent__title">
        <img src="/images/icon.jpg" alt="MyComponent" class="mycomponent__logo">
        <h1>MyComponent</h1>
      </div>
      <div class="mycomponent__header-content">
        <div class="mycomponent__stats">
          <div class="mycomponent__stat-item">
            <span>Status:</span>
            <span class="mycomponent__stat-value" id="mycomponent-status">-</span>
          </div>
          <div class="mycomponent__stat-item">
            <span>Operations:</span>
            <span class="mycomponent__stat-value" id="mycomponent-operations">0</span>
          </div>
        </div>
      </div>
      <div class="mycomponent__controls">
        <button class="mycomponent__btn mycomponent__btn--refresh" onclick="mycomponent_refresh()">
          <span>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Chat Options Bar -->
    <div class="mycomponent__menu-bar">
      <div class="mycomponent__chat-options">
        <div class="mycomponent__chat-option mycomponent__chat-option--active" 
             onclick="mycomponent_switchChat('main')">Main Chat</div>
        <div class="mycomponent__chat-option" 
             onclick="mycomponent_switchChat('help')">Help Chat</div>
      </div>
    </div>

    <!-- Tab Navigation -->
    <div class="mycomponent__tabs">
      <div class="mycomponent__tab mycomponent__tab--active" 
           data-tab="overview" 
           onclick="mycomponent_switchTab('overview')">Overview</div>
      <div class="mycomponent__tab" 
           data-tab="operations" 
           onclick="mycomponent_switchTab('operations')">Operations</div>
      <div class="mycomponent__tab" 
           data-tab="settings" 
           onclick="mycomponent_switchTab('settings')">Settings</div>
    </div>

    <!-- Content Panels -->
    <div class="mycomponent__content">
      <!-- Overview Panel -->
      <div id="mycomponent-overview-panel" class="mycomponent__panel mycomponent__panel--active">
        <div class="mycomponent__panel-header">
          <h2>Overview</h2>
        </div>
        <div class="mycomponent__panel-body">
          <div class="mycomponent__info-grid">
            <div class="mycomponent__info-item">
              <label>Component Version:</label>
              <span id="mycomponent-version">0.1.0</span>
            </div>
            <div class="mycomponent__info-item">
              <label>Health Status:</label>
              <span id="mycomponent-health" class="mycomponent__health-badge mycomponent__health-badge--healthy">
                Healthy
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Operations Panel -->
      <div id="mycomponent-operations-panel" class="mycomponent__panel" style="display: none;">
        <div class="mycomponent__panel-header">
          <h2>Operations</h2>
        </div>
        <div class="mycomponent__panel-body">
          <div class="mycomponent__operations-grid">
            <!-- Operation controls go here -->
            <button class="mycomponent__btn mycomponent__btn--primary" 
                    onclick="mycomponent_executeOperation()">
              Execute Operation
            </button>
          </div>
          <div class="mycomponent__results" id="mycomponent-results">
            <!-- Results display here -->
          </div>
        </div>
      </div>

      <!-- Settings Panel -->
      <div id="mycomponent-settings-panel" class="mycomponent__panel" style="display: none;">
        <div class="mycomponent__panel-header">
          <h2>Settings</h2>
        </div>
        <div class="mycomponent__panel-body">
          <div class="mycomponent__settings-form">
            <!-- Settings controls go here -->
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Interface (appears on all panels) -->
    <div class="mycomponent__chat-container" id="mycomponent-chat-container">
      <!-- Chat interface is injected here by tekton-llm-client.js -->
    </div>
  </div>
</div>

<!-- Component Scripts -->
<script src="/scripts/mycomponent.js"></script>
```

## Component JavaScript

### scripts/mycomponent.js

```javascript
/**
 * MyComponent UI Controller
 * Handles UI interactions and API communication
 */

// Component namespace to avoid conflicts
const MyComponentUI = {
    // Configuration
    config: {
        apiUrl: window.MYCOMPONENT_API_URL || `http://localhost:${window.MYCOMPONENT_PORT || 8015}`,
        wsUrl: window.MYCOMPONENT_WS_URL || `ws://localhost:${window.MYCOMPONENT_PORT || 8015}/ws`,
        refreshInterval: 30000, // 30 seconds
        component: 'mycomponent'
    },

    // State
    state: {
        connected: false,
        currentTab: 'overview',
        currentChat: 'main',
        refreshTimer: null,
        ws: null
    },

    // Initialize component
    init() {
        console.log('Initializing MyComponent UI');
        
        // Set up WebSocket connection
        this.connectWebSocket();
        
        // Load initial data
        this.loadStatus();
        
        // Set up auto-refresh
        this.startAutoRefresh();
        
        // Initialize chat
        this.initializeChat();
    },

    // WebSocket connection
    connectWebSocket() {
        try {
            this.state.ws = new WebSocket(this.config.wsUrl);
            
            this.state.ws.onopen = () => {
                console.log('MyComponent WebSocket connected');
                this.state.connected = true;
                this.updateConnectionStatus(true);
            };
            
            this.state.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.state.ws.onclose = () => {
                console.log('MyComponent WebSocket disconnected');
                this.state.connected = false;
                this.updateConnectionStatus(false);
                // Reconnect after 5 seconds
                setTimeout(() => this.connectWebSocket(), 5000);
            };
            
            this.state.ws.onerror = (error) => {
                console.error('MyComponent WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
        }
    },

    // Handle WebSocket messages
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'status_update':
                this.updateStatus(data.payload);
                break;
            case 'operation_result':
                this.displayResult(data.payload);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    },

    // Load component status
    async loadStatus() {
        try {
            const response = await fetch(`${this.config.apiUrl}/health`);
            if (response.ok) {
                const data = await response.json();
                this.updateHealthDisplay(data);
            }
        } catch (error) {
            console.error('Failed to load status:', error);
            this.updateHealthDisplay({ status: 'error' });
        }
    },

    // Update health display
    updateHealthDisplay(health) {
        const statusEl = document.getElementById('mycomponent-status');
        const healthEl = document.getElementById('mycomponent-health');
        
        if (statusEl) {
            statusEl.textContent = health.status || 'Unknown';
        }
        
        if (healthEl) {
            healthEl.textContent = health.status || 'Unknown';
            healthEl.className = `mycomponent__health-badge mycomponent__health-badge--${health.status}`;
        }
    },

    // Start auto-refresh
    startAutoRefresh() {
        this.state.refreshTimer = setInterval(() => {
            this.loadStatus();
        }, this.config.refreshInterval);
    },

    // Stop auto-refresh
    stopAutoRefresh() {
        if (this.state.refreshTimer) {
            clearInterval(this.state.refreshTimer);
            this.state.refreshTimer = null;
        }
    },

    // Initialize chat interface
    initializeChat() {
        // Chat is handled by tekton-llm-client.js
        // Just ensure the container is ready
        const chatContainer = document.getElementById('mycomponent-chat-container');
        if (chatContainer && window.TektonLLMClient) {
            window.TektonLLMClient.initializeChat('mycomponent', chatContainer);
        }
    },

    // Execute an operation
    async executeOperation() {
        try {
            const response = await fetch(`${this.config.apiUrl}/api/operation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    // Operation parameters
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.displayResult(result);
            }
        } catch (error) {
            console.error('Operation failed:', error);
            this.displayError(error.message);
        }
    },

    // Display operation result
    displayResult(result) {
        const resultsEl = document.getElementById('mycomponent-results');
        if (resultsEl) {
            resultsEl.innerHTML = `
                <div class="mycomponent__result">
                    <div class="mycomponent__result-header">Operation Complete</div>
                    <div class="mycomponent__result-body">
                        ${JSON.stringify(result, null, 2)}
                    </div>
                </div>
            `;
        }
    },

    // Display error
    displayError(message) {
        const resultsEl = document.getElementById('mycomponent-results');
        if (resultsEl) {
            resultsEl.innerHTML = `
                <div class="mycomponent__error">
                    <div class="mycomponent__error-header">Error</div>
                    <div class="mycomponent__error-body">${message}</div>
                </div>
            `;
        }
    },

    // Update connection status
    updateConnectionStatus(connected) {
        // Update UI to show connection status
        const statusEl = document.getElementById('mycomponent-status');
        if (statusEl) {
            statusEl.textContent = connected ? 'Connected' : 'Disconnected';
        }
    },

    // Cleanup
    cleanup() {
        this.stopAutoRefresh();
        if (this.state.ws) {
            this.state.ws.close();
        }
    }
};

// Global functions for onclick handlers
function mycomponent_switchTab(tabName) {
    // Hide all panels
    document.querySelectorAll('.mycomponent__panel').forEach(panel => {
        panel.style.display = 'none';
        panel.classList.remove('mycomponent__panel--active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.mycomponent__tab').forEach(tab => {
        tab.classList.remove('mycomponent__tab--active');
    });
    
    // Show selected panel
    const panel = document.getElementById(`mycomponent-${tabName}-panel`);
    if (panel) {
        panel.style.display = 'block';
        panel.classList.add('mycomponent__panel--active');
    }
    
    // Mark tab as active
    const tab = document.querySelector(`[data-tab="${tabName}"]`);
    if (tab) {
        tab.classList.add('mycomponent__tab--active');
    }
    
    MyComponentUI.state.currentTab = tabName;
}

function mycomponent_switchChat(chatType) {
    // Update chat option styling
    document.querySelectorAll('.mycomponent__chat-option').forEach(option => {
        option.classList.remove('mycomponent__chat-option--active');
    });
    
    event.target.classList.add('mycomponent__chat-option--active');
    
    // Notify chat system of context switch
    if (window.TektonLLMClient) {
        window.TektonLLMClient.switchContext('mycomponent', chatType);
    }
    
    MyComponentUI.state.currentChat = chatType;
}

function mycomponent_refresh() {
    MyComponentUI.loadStatus();
}

function mycomponent_executeOperation() {
    MyComponentUI.executeOperation();
}

// Initialize when component is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're in the MyComponent context
    if (document.getElementById('mycomponent-component')) {
        MyComponentUI.init();
    }
});

// Cleanup when component is unloaded
window.addEventListener('beforeunload', () => {
    MyComponentUI.cleanup();
});
```

## Component Styles (BEM)

### styles/mycomponent.css

```css
/**
 * MyComponent Styles
 * Following BEM naming convention: block__element--modifier
 */

/* Block: Main component container */
.mycomponent {
    display: flex;
    flex-direction: column;
    height: 100%;
    background-color: var(--component-bg, #1a1a1a);
    color: var(--component-text, #e0e0e0);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Element: Header */
.mycomponent__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    background-color: var(--header-bg, #2a2a2a);
    border-bottom: 1px solid var(--border-color, #3a3a3a);
}

.mycomponent__title {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.mycomponent__logo {
    width: 32px;
    height: 32px;
    border-radius: 4px;
}

.mycomponent__header h1 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
}

/* Element: Stats */
.mycomponent__stats {
    display: flex;
    gap: 2rem;
}

.mycomponent__stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.mycomponent__stat-item span:first-child {
    font-size: 0.75rem;
    color: var(--text-secondary, #999);
    text-transform: uppercase;
}

.mycomponent__stat-value {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--accent-color, #4a9eff);
}

/* Element: Controls */
.mycomponent__controls {
    display: flex;
    gap: 0.5rem;
}

.mycomponent__btn {
    padding: 0.5rem 1rem;
    border: 1px solid var(--border-color, #3a3a3a);
    border-radius: 4px;
    background-color: var(--button-bg, #2a2a2a);
    color: var(--button-text, #e0e0e0);
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.mycomponent__btn:hover {
    background-color: var(--button-hover-bg, #3a3a3a);
    border-color: var(--accent-color, #4a9eff);
}

.mycomponent__btn--primary {
    background-color: var(--accent-color, #4a9eff);
    border-color: var(--accent-color, #4a9eff);
    color: white;
}

.mycomponent__btn--primary:hover {
    background-color: var(--accent-hover, #357abd);
}

/* Element: Menu Bar */
.mycomponent__menu-bar {
    display: flex;
    padding: 0 1rem;
    background-color: var(--menu-bg, #252525);
    border-bottom: 1px solid var(--border-color, #3a3a3a);
}

.mycomponent__chat-options {
    display: flex;
    gap: 1rem;
}

.mycomponent__chat-option {
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.2s ease;
}

.mycomponent__chat-option:hover {
    color: var(--accent-color, #4a9eff);
}

.mycomponent__chat-option--active {
    color: var(--accent-color, #4a9eff);
    border-bottom-color: var(--accent-color, #4a9eff);
}

/* Element: Tabs */
.mycomponent__tabs {
    display: flex;
    background-color: var(--tabs-bg, #1f1f1f);
    border-bottom: 1px solid var(--border-color, #3a3a3a);
}

.mycomponent__tab {
    padding: 1rem 1.5rem;
    font-size: 0.875rem;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.2s ease;
}

.mycomponent__tab:hover {
    background-color: var(--tab-hover-bg, #2a2a2a);
}

.mycomponent__tab--active {
    color: var(--accent-color, #4a9eff);
    border-bottom-color: var(--accent-color, #4a9eff);
    background-color: var(--tab-active-bg, #252525);
}

/* Element: Content */
.mycomponent__content {
    flex: 1;
    overflow-y: auto;
    position: relative;
}

/* Element: Panel */
.mycomponent__panel {
    padding: 1.5rem;
    min-height: 100%;
}

.mycomponent__panel-header {
    margin-bottom: 1.5rem;
}

.mycomponent__panel-header h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
}

.mycomponent__panel-body {
    /* Panel-specific content */
}

/* Element: Info Grid */
.mycomponent__info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.mycomponent__info-item {
    padding: 1rem;
    background-color: var(--card-bg, #2a2a2a);
    border-radius: 4px;
    border: 1px solid var(--border-color, #3a3a3a);
}

.mycomponent__info-item label {
    display: block;
    font-size: 0.75rem;
    color: var(--text-secondary, #999);
    margin-bottom: 0.5rem;
}

/* Element: Health Badge */
.mycomponent__health-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}

.mycomponent__health-badge--healthy {
    background-color: var(--success-bg, #1a4d1a);
    color: var(--success-text, #4ade80);
}

.mycomponent__health-badge--degraded {
    background-color: var(--warning-bg, #4d3a1a);
    color: var(--warning-text, #fbbf24);
}

.mycomponent__health-badge--error {
    background-color: var(--error-bg, #4d1a1a);
    color: var(--error-text, #f87171);
}

/* Element: Results */
.mycomponent__results {
    margin-top: 1.5rem;
}

.mycomponent__result,
.mycomponent__error {
    padding: 1rem;
    border-radius: 4px;
    border: 1px solid var(--border-color, #3a3a3a);
    margin-bottom: 1rem;
}

.mycomponent__result {
    background-color: var(--result-bg, #1a2d1a);
    border-color: var(--success-border, #2d4d2d);
}

.mycomponent__error {
    background-color: var(--error-bg, #2d1a1a);
    border-color: var(--error-border, #4d2d2d);
}

/* Element: Chat Container */
.mycomponent__chat-container {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 350px;
    background-color: var(--chat-bg, #1f1f1f);
    border-left: 1px solid var(--border-color, #3a3a3a);
    display: none; /* Hidden by default, shown by chat system */
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .mycomponent__header {
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .mycomponent__stats {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .mycomponent__chat-container {
        width: 100%;
        position: static;
    }
}
```

## Integration with Hephaestus

### 1. Register Component in Hephaestus

The component needs to be registered in Hephaestus's component registry. This happens automatically when the component registers with Hermes.

### 2. Navigation Tab

A navigation tab is automatically added to the LEFT PANEL when the component is discovered through Hermes.

### 3. Chat Integration

The chat interface is provided by `tekton-llm-client.js` and automatically integrates with your component when initialized.

## AI Interface Implementation Details

### Chat Interface Setup

The Tekton LLM Client provides a sophisticated chat interface that can be customized for each component:

```javascript
// Advanced chat initialization with options
initializeChat() {
    const chatConfig = {
        component: 'mycomponent',
        container: document.getElementById('mycomponent-chat-container'),
        contexts: {
            main: {
                systemPrompt: "You are helping with MyComponent operations...",
                tools: ['analyze_data', 'execute_operation', 'get_status']
            },
            help: {
                systemPrompt: "You are providing help for MyComponent...",
                tools: ['get_documentation', 'explain_feature']
            },
            debug: {
                systemPrompt: "You are debugging MyComponent issues...",
                tools: ['analyze_logs', 'trace_operation', 'get_metrics']
            }
        },
        onMessage: this.handleChatMessage.bind(this),
        onToolCall: this.handleToolCall.bind(this)
    };
    
    if (window.TektonLLMClient) {
        this.chatInterface = window.TektonLLMClient.createChat(chatConfig);
    }
}

// Handle incoming chat messages
handleChatMessage(message) {
    console.log('Chat message received:', message);
    // Update UI based on chat interactions
    if (message.intent === 'show_panel') {
        mycomponent_switchTab(message.panel);
    }
}

// Handle tool calls from chat
async handleToolCall(toolName, parameters) {
    console.log('Tool call:', toolName, parameters);
    
    // Execute the tool via MCP
    const response = await fetch(`${this.config.apiUrl}/api/mcp/v2/tools/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: toolName,
            arguments: parameters
        })
    });
    
    return await response.json();
}
```

### AI-Powered UI Elements

#### 1. Smart Command Palette

```html
<!-- AI-powered command palette -->
<div class="mycomponent__command-palette" id="mycomponent-command-palette">
    <input type="text" 
           class="mycomponent__command-input"
           id="mycomponent-command-input"
           placeholder="Ask me anything or type a command..."
           autocomplete="off">
    <div class="mycomponent__suggestions" id="mycomponent-suggestions">
        <!-- AI-generated suggestions appear here -->
    </div>
</div>
```

```javascript
// Smart command palette with AI suggestions
class CommandPalette {
    constructor(component) {
        this.component = component;
        this.input = document.getElementById('mycomponent-command-input');
        this.suggestions = document.getElementById('mycomponent-suggestions');
        this.setupListeners();
    }
    
    setupListeners() {
        this.input.addEventListener('input', this.debounce(this.getSuggestions.bind(this), 300));
        this.input.addEventListener('keydown', this.handleKeyDown.bind(this));
    }
    
    async getSuggestions(event) {
        const query = event.target.value;
        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }
        
        // Get AI-powered suggestions
        const response = await fetch(`${this.component.config.apiUrl}/api/ai/suggestions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                query,
                context: this.component.state
            })
        });
        
        const suggestions = await response.json();
        this.displaySuggestions(suggestions);
    }
    
    displaySuggestions(suggestions) {
        this.suggestions.innerHTML = suggestions.map((s, i) => `
            <div class="mycomponent__suggestion" data-index="${i}">
                <span class="mycomponent__suggestion-icon">${s.icon}</span>
                <span class="mycomponent__suggestion-text">${s.text}</span>
                <span class="mycomponent__suggestion-hint">${s.hint}</span>
            </div>
        `).join('');
        
        this.suggestions.style.display = 'block';
    }
    
    // Debounce helper
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}
```

#### 2. AI Insights Dashboard

```html
<!-- AI insights dashboard -->
<div class="mycomponent__ai-dashboard">
    <div class="mycomponent__ai-metrics">
        <div class="mycomponent__metric-card">
            <h4>Performance Score</h4>
            <div class="mycomponent__metric-value" id="ai-performance-score">
                <span class="mycomponent__metric-number">--</span>
                <span class="mycomponent__metric-trend"></span>
            </div>
            <div class="mycomponent__metric-insight" id="ai-performance-insight">
                <!-- AI-generated insight appears here -->
            </div>
        </div>
        
        <div class="mycomponent__metric-card">
            <h4>Optimization Opportunities</h4>
            <ul class="mycomponent__opportunities" id="ai-opportunities">
                <!-- AI-identified opportunities -->
            </ul>
        </div>
    </div>
    
    <div class="mycomponent__ai-actions">
        <button class="mycomponent__btn mycomponent__btn--ai" 
                onclick="mycomponent_runAIAnalysis()">
            <span class="mycomponent__btn-icon">🤖</span>
            Run AI Analysis
        </button>
        <button class="mycomponent__btn mycomponent__btn--ai"
                onclick="mycomponent_getRecommendations()">
            <span class="mycomponent__btn-icon">💡</span>
            Get Recommendations
        </button>
    </div>
</div>
```

#### 3. Conversational Forms

```javascript
// AI-powered form filling
class ConversationalForm {
    constructor(formId, component) {
        this.form = document.getElementById(formId);
        this.component = component;
        this.currentField = null;
        this.setupConversationalMode();
    }
    
    setupConversationalMode() {
        // Add chat-like interface to form
        const chatHelper = document.createElement('div');
        chatHelper.className = 'mycomponent__form-chat';
        chatHelper.innerHTML = `
            <div class="mycomponent__form-chat-messages" id="form-chat-messages"></div>
            <input type="text" 
                   class="mycomponent__form-chat-input" 
                   id="form-chat-input"
                   placeholder="Tell me about your configuration...">
        `;
        this.form.appendChild(chatHelper);
        
        // Handle conversational input
        const chatInput = document.getElementById('form-chat-input');
        chatInput.addEventListener('keypress', this.handleChatInput.bind(this));
    }
    
    async handleChatInput(event) {
        if (event.key !== 'Enter') return;
        
        const input = event.target.value;
        event.target.value = '';
        
        // Add user message to chat
        this.addMessage(input, 'user');
        
        // Process with AI
        const response = await this.processFormInput(input);
        
        // Add AI response
        this.addMessage(response.message, 'ai');
        
        // Update form fields based on AI extraction
        if (response.fields) {
            this.updateFormFields(response.fields);
        }
    }
    
    async processFormInput(input) {
        const response = await fetch(`${this.component.config.apiUrl}/api/ai/extract-form-data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                input,
                formSchema: this.getFormSchema(),
                context: this.component.state
            })
        });
        
        return await response.json();
    }
    
    addMessage(text, sender) {
        const messages = document.getElementById('form-chat-messages');
        const message = document.createElement('div');
        message.className = `mycomponent__form-message mycomponent__form-message--${sender}`;
        message.textContent = text;
        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;
    }
}
```

### WebSocket Integration for Real-time AI

```javascript
// Enhanced WebSocket handling for AI features
class AIWebSocketHandler {
    constructor(component) {
        this.component = component;
        this.connect();
    }
    
    connect() {
        this.ws = new WebSocket(this.component.config.wsUrl);
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            switch (data.type) {
                case 'ai_insight':
                    this.handleAIInsight(data.payload);
                    break;
                case 'ai_alert':
                    this.handleAIAlert(data.payload);
                    break;
                case 'ai_recommendation':
                    this.handleAIRecommendation(data.payload);
                    break;
                case 'pattern_detected':
                    this.handlePatternDetection(data.payload);
                    break;
            }
        };
    }
    
    handleAIInsight(insight) {
        // Update UI with new insight
        const insightEl = document.getElementById(`ai-${insight.metric}-insight`);
        if (insightEl) {
            insightEl.innerHTML = `
                <p>${insight.text}</p>
                <span class="mycomponent__insight-confidence">
                    Confidence: ${insight.confidence}%
                </span>
            `;
        }
        
        // Show notification
        this.component.showNotification({
            type: 'insight',
            title: 'New AI Insight',
            message: insight.summary
        });
    }
    
    handleAIAlert(alert) {
        // Display AI-generated alert
        const alertContainer = document.getElementById('mycomponent-alerts');
        const alertEl = document.createElement('div');
        alertEl.className = `mycomponent__alert mycomponent__alert--${alert.severity}`;
        alertEl.innerHTML = `
            <div class="mycomponent__alert-header">
                <span class="mycomponent__alert-icon">⚠️</span>
                <span class="mycomponent__alert-title">${alert.title}</span>
            </div>
            <div class="mycomponent__alert-body">
                <p>${alert.description}</p>
                <div class="mycomponent__alert-actions">
                    ${alert.suggestedActions.map(action => `
                        <button class="mycomponent__btn mycomponent__btn--small"
                                onclick="mycomponent_executeAction('${action.id}')">
                            ${action.label}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
        alertContainer.prepend(alertEl);
    }
}
```

### AI-Enhanced Error Handling

```javascript
// Intelligent error handling with AI assistance
class AIErrorHandler {
    constructor(component) {
        this.component = component;
        window.addEventListener('error', this.handleError.bind(this));
    }
    
    async handleError(event) {
        const errorInfo = {
            message: event.message,
            source: event.filename,
            line: event.lineno,
            column: event.colno,
            stack: event.error?.stack,
            componentState: this.component.state,
            timestamp: new Date().toISOString()
        };
        
        // Get AI analysis of the error
        const analysis = await this.analyzeError(errorInfo);
        
        // Display AI-enhanced error message
        this.displayError(analysis);
    }
    
    async analyzeError(errorInfo) {
        try {
            const response = await fetch(`${this.component.config.apiUrl}/api/ai/analyze-error`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(errorInfo)
            });
            
            return await response.json();
        } catch (e) {
            // Fallback if AI analysis fails
            return {
                summary: errorInfo.message,
                suggestions: ['Check the console for more details'],
                severity: 'error'
            };
        }
    }
    
    displayError(analysis) {
        const errorModal = document.createElement('div');
        errorModal.className = 'mycomponent__error-modal';
        errorModal.innerHTML = `
            <div class="mycomponent__error-content">
                <h3>Error Detected</h3>
                <p class="mycomponent__error-summary">${analysis.summary}</p>
                
                <div class="mycomponent__error-analysis">
                    <h4>AI Analysis</h4>
                    <p>${analysis.explanation}</p>
                    
                    <h4>Suggested Solutions</h4>
                    <ul>
                        ${analysis.suggestions.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                    
                    ${analysis.similarIssues ? `
                        <h4>Similar Issues</h4>
                        <p>${analysis.similarIssues.length} similar issues found in history</p>
                    ` : ''}
                </div>
                
                <div class="mycomponent__error-actions">
                    <button onclick="this.parentElement.parentElement.remove()">
                        Dismiss
                    </button>
                    <button onclick="mycomponent_reportError('${analysis.id}')">
                        Report Issue
                    </button>
                    ${analysis.autoFix ? `
                        <button class="mycomponent__btn--primary" 
                                onclick="mycomponent_applyAutoFix('${analysis.autoFix.id}')">
                            Apply Auto-Fix
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
        
        document.body.appendChild(errorModal);
    }
}
```

## Best Practices

1. **Keep UI Simple** - It's just a visibility layer
2. **Use Semantic HTML** - Proper elements for accessibility
3. **Follow BEM Strictly** - Prevents style conflicts
4. **No External Dependencies** - Self-contained components
5. **Responsive Design** - Works on various screen sizes
6. **Dark Theme Default** - Consistent with Tekton UI
7. **Let LLMs Handle Complexity** - UI just displays state

## Common UI Patterns

### Status Indicators
- Use color-coded badges for health status
- Show real-time updates via WebSocket
- Display connection status prominently

### Data Display
- Use tables for structured data
- Cards for grouped information
- JSON viewers for complex data

### User Actions
- Clear, labeled buttons
- Confirmation for destructive actions
- Loading states for async operations

### Error Handling
- Clear error messages
- Actionable error descriptions
- Retry mechanisms where appropriate

---

*Next: [Step By Step Tutorial](./Step_By_Step_Tutorial.md)*