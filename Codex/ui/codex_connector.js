/**
 * Codex (Aider) connector for Tekton UI
 * 
 * This module provides integration between Aider and the Tekton UI,
 * allowing Aider to be displayed in the RIGHT PANEL and receive
 * input from the RIGHT FOOTER chat input area.
 */

const codexConnector = {
  // Component state
  state: {
    connected: false,
    sessionActive: false,
    sessionStarting: false,
    sessionId: null,
    inputHistory: [],
    messages: [],
    activeFiles: [],
    inputRequested: false,
    pendingInput: null,
    lastActivity: Date.now()
  },
  
  // WebSocket connection to backend
  socket: null,
  
  // Ping interval ID
  pingIntervalId: null,
  
  // Initialize the connection to Aider
  initialize: function() {
    // Connect to WebSocket server
    this.connectWebSocket();
    this.checkSessionStatus();
    
    // Setup the RIGHT FOOTER handler (critical for chat input)
    this.setupRightFooterHandler();
    
    // Setup the New Session button handler
    this.setupNewSessionHandler();
    
    // Init ping interval
    this.pingIntervalId = setInterval(() => this.sendPing(), 30000);
  },
  
  
  // Connect to the WebSocket backend
  connectWebSocket: function() {
    // First try direct connection to local codex server
    const wsDirectUrl = 'ws://localhost:8082/ws/codex';
    
    // Close existing connection if any
    if (this.socket && this.socket.readyState !== WebSocket.CLOSED) {
      this.socket.close();
    }
    
    // Create new connection
    try {
      this.socket = new WebSocket(wsDirectUrl);
    } catch (err) {
      return;
    }
    
    this.socket.onopen = () => {
      this.state.connected = true;
      this.updateUI();
      
      // Auto-start session to ensure it's ready for input
      if (!this.state.sessionActive && !this.state.sessionStarting) {
        this.startSession();
      }
      
      // Send pending input if any
      if (this.state.pendingInput) {
        // Add a delay to ensure session has time to start
        setTimeout(() => {
          this.sendInput(this.state.pendingInput);
          this.state.pendingInput = null;
        }, 1000);
      }
    };
    
    this.socket.onclose = () => {
      this.state.connected = false;
      this.updateUI();
      
      // Attempt to reconnect after a delay
      setTimeout(() => this.connectWebSocket(), 5000);
    };
    
    this.socket.onerror = (error) => {
      // If direct connection fails, try proxy URL as fallback
      const wsProxyUrl = `ws://${window.location.host}/ws/codex`;
      
      try {
        this.socket = new WebSocket(wsProxyUrl);
      } catch (err) {
        return;
      }
      
      // Set up same handlers for proxy connection
      this.socket.onopen = () => {
        this.state.connected = true;
        this.updateUI();
        
        // Always auto-start a session
        if (!this.state.sessionActive && !this.state.sessionStarting) {
          this.startSession();
        }
        
        if (this.state.pendingInput) {
          // Add a delay to ensure session has time to start
          setTimeout(() => {
            this.sendInput(this.state.pendingInput);
            this.state.pendingInput = null;
          }, 1000);
        }
      };
      
      this.socket.onclose = () => {
        this.state.connected = false;
        this.updateUI();
        
        setTimeout(() => this.connectWebSocket(), 5000);
      };
      
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          // Silently ignore parse errors
        }
      };
    };
    
    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        // Silently ignore parse errors
      }
    };
  },
  
  // Check the session status
  checkSessionStatus: function() {
    fetch('/api/codex/status')
      .then(response => response.json())
      .then(data => {
        this.state.sessionActive = data.session_active || false;
        this.updateSessionStatus();
      })
      .catch(error => {
        console.error('Error checking session status:', error);
      });
  },
  
  // Handle incoming messages from the backend
  handleMessage: function(data) {
    const type = data.type;
    const content = data.content;
    
    // Update activity timestamp
    this.state.lastActivity = Date.now();
    
    switch (type) {
      case 'output':
        this.addMessage('assistant', content);
        break;
        
      case 'error':
        this.addMessage('error', content);
        break;
        
      case 'warning':
        this.addMessage('warning', content);
        break;
        
      case 'active_files':
        this.state.activeFiles = content;
        this.updateFileList();
        break;
        
      case 'input_request':
        this.state.inputRequested = true;
        // Focus the input field
        this.focusInputField();
        break;
        
      case 'input_received':
        // Flash visual feedback that input was received
        this.showInputFeedback(content.text);
        break;
        
      case 'session_status':
        this.state.sessionActive = content.active;
        this.state.sessionStarting = false;
        this.state.sessionId = content.session_id || null;
        this.updateSessionStatus();
        break;
        
      case 'pong':
        // Silent acknowledgment of ping
        break;
        
      default:
        console.log('Unknown message type:', type, content);
    }
    
    this.updateUI();
  },
  
  // Send a ping to keep the connection alive
  sendPing: function() {
    if (this.state.connected) {
      this.socket.send(JSON.stringify({
        type: 'ping',
        content: ''
      }));
    }
  },
  
  // Add a message to the display
  addMessage: function(role, content) {
    const message = {
      role: role,
      content: content,
      timestamp: new Date().toISOString()
    };
    
    this.state.messages.push(message);
    this.renderMessages();
    
    // Auto-scroll to bottom
    const messagesContainer = document.getElementById('codex-messages');
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // If it's a user message, notify the parent window about it
    if (role === 'user') {
      try {
        window.parent.postMessage({
          type: 'codex_added_message',
          role: role,
          content: content
        }, '*');
      } catch (err) {
        console.warn('Failed to notify parent window of message:', err);
      }
    }
  },
  
  // Start a new Aider session
  startSession: function() {
    if (this.state.sessionStarting) {
      console.log('Session already starting...');
      return;
    }
    
    this.state.sessionStarting = true;
    this.updateSessionStatus();
    
    // Clear existing messages
    this.state.messages = [];
    this.state.activeFiles = [];
    this.renderMessages();
    this.updateFileList();
    
    // Add starting message
    this.addMessage('assistant', 'Starting new Aider session...');
    
    // Send start message via WebSocket
    if (this.state.connected) {
      this.socket.send(JSON.stringify({
        type: 'start_session',
        content: {
          timestamp: Date.now()
        }
      }));
    } else {
      // Use the REST API as fallback
      fetch('/api/codex/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          this.state.sessionActive = true;
          this.state.sessionId = data.session_id || null;
        } else {
          this.addMessage('error', `Failed to start session: ${data.message}`);
          this.state.sessionStarting = false;
        }
        this.updateSessionStatus();
      })
      .catch(error => {
        this.addMessage('error', `Error starting session: ${error.message}`);
        this.state.sessionStarting = false;
        this.updateSessionStatus();
      });
    }
  },
  
  // Stop the current Aider session
  stopSession: function() {
    // Send stop message via WebSocket
    if (this.state.connected) {
      this.socket.send(JSON.stringify({
        type: 'stop_session'
      }));
    } else {
      // Use the REST API as fallback
      fetch('/api/codex/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          this.state.sessionActive = false;
          this.addMessage('assistant', 'Aider session stopped.');
        } else {
          this.addMessage('error', `Failed to stop session: ${data.message}`);
        }
        this.updateSessionStatus();
      })
      .catch(error => {
        this.addMessage('error', `Error stopping session: ${error.message}`);
      });
    }
  },
  
  // Send user input to the backend
  sendInput: function(text) {
    if (!text.trim()) return false;
    
    // Store as pending if not connected
    if (!this.state.connected) {
      console.log('Not connected, storing input as pending');
      this.state.pendingInput = text;
      return false;
    }
    
    // Update activity timestamp
    this.state.lastActivity = Date.now();
    
    // Add to history
    this.state.inputHistory.push(text);
    
    // Add to messages
    this.addMessage('user', text);
    
    // Reset input request flag
    this.state.inputRequested = false;
    
    // Send via WebSocket
    this.socket.send(JSON.stringify({
      type: 'input',
      content: text
    }));
    
    return true;
  },
  
  // Setup RIGHT FOOTER input handler
  setupRightFooterHandler: function() {
    // This will be called by the global event bus when Codex is active
    window.addEventListener('right-footer-input', (event) => {
      const text = event.detail && event.detail.text;
      if (text) {
        // Add to messages immediately to provide visual feedback
        this.addMessage('user', text);
        
        // Show visual feedback immediately
        this.showInputFeedback(text);
        
        // Ensure WebSocket is connected and session is active before sending input
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
          // If no session is active, start one
          if (!this.state.sessionActive && !this.state.sessionStarting) {
            // Start session first
            this.socket.send(JSON.stringify({
              type: 'start_session',
              content: { timestamp: Date.now() }
            }));
            
            // Add a short delay before sending input to allow session to initialize
            setTimeout(() => {
              this.socket.send(JSON.stringify({
                type: 'input',
                content: text
              }));
            }, 1000);
          } else {
            // Session is active, send input directly
            this.socket.send(JSON.stringify({
              type: 'input',
              content: text
            }));
          }
        } else {
          // WebSocket not connected, try to connect and queue the input
          this.state.pendingInput = text;
          this.connectWebSocket();
          
          // Fallback to API in case WebSocket fails
          fetch('/api/codex/input', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
          })
          .then(response => response.json())
          .then(data => {
            if (data.status === 'success') {
              // Update session state if needed
              if (data.session_id && this.state.sessionId !== data.session_id) {
                this.state.sessionId = data.session_id;
                this.state.sessionActive = true;
                this.updateSessionStatus();
              }
            } else {
              this.addMessage('error', `Failed to send input: ${data.message}`);
            }
          })
          .catch(error => {
            this.addMessage('error', `Error sending input: ${error.message}`);
          });
        }
      }
    });
  },
  
  // Setup New Session button handler
  setupNewSessionHandler: function() {
    // Add a new session button to the UI
    window.addEventListener('DOMContentLoaded', () => {
      const container = document.getElementById('codex-root');
      if (container) {
        const header = container.querySelector('.codex-header');
        if (header) {
          const newSessionButton = document.createElement('button');
          newSessionButton.className = 'new-session-button';
          newSessionButton.textContent = 'New Session';
          newSessionButton.onclick = () => this.startSession();
          header.appendChild(newSessionButton);
        }
      }
    });
  },
  
  // Show visual feedback that input was received
  showInputFeedback: function(text) {
    // Find the user message that matches this text
    const messagesContainer = document.getElementById('codex-messages');
    if (!messagesContainer) return;
    
    const userMessages = messagesContainer.querySelectorAll('.codex-message-user');
    for (let i = userMessages.length - 1; i >= 0; i--) {
      const message = userMessages[i];
      if (message.textContent.includes(text)) {
        // Add a brief highlight effect
        message.classList.add('input-received');
        setTimeout(() => {
          message.classList.remove('input-received');
        }, 1000);
        break;
      }
    }
  },
  
  // Focus the input field when input is requested
  focusInputField: function() {
    // This will be connected to the RIGHT FOOTER chat input area
    const inputField = document.querySelector('.chat-input textarea, .chat-input input');
    if (inputField) {
      inputField.focus();
    }
  },
  
  // Update the file list in the UI
  updateFileList: function() {
    const fileListElement = document.getElementById('codex-files');
    if (!fileListElement) return;
    
    // Clear existing list
    fileListElement.innerHTML = '';
    
    // Add each file
    this.state.activeFiles.forEach(file => {
      const fileItem = document.createElement('div');
      fileItem.className = 'codex-file';
      fileItem.textContent = file;
      fileItem.title = file;
      
      // Add click handler to focus on file
      fileItem.addEventListener('click', () => {
        // Send a command to focus on this file
        const focusCommand = `/focus ${file}`;
        this.sendInput(focusCommand);
      });
      
      fileListElement.appendChild(fileItem);
    });
  },
  
  // Update session status UI
  updateSessionStatus: function() {
    const statusElement = document.getElementById('codex-status');
    if (!statusElement) return;
    
    if (this.state.sessionStarting) {
      statusElement.className = 'status starting';
      statusElement.textContent = 'Starting...';
    } else if (this.state.sessionActive) {
      statusElement.className = 'status connected';
      statusElement.textContent = 'Active';
    } else {
      statusElement.className = 'status disconnected';
      statusElement.textContent = 'Inactive';
    }
    
    // Update new session button state
    const newSessionButton = document.querySelector('.new-session-button');
    if (newSessionButton) {
      if (this.state.sessionStarting) {
        newSessionButton.disabled = true;
        newSessionButton.textContent = 'Starting...';
      } else {
        newSessionButton.disabled = false;
        newSessionButton.textContent = this.state.sessionActive ? 'Restart Session' : 'New Session';
      }
    }
  },
  
  // Render all messages to the UI
  renderMessages: function() {
    const messagesContainer = document.getElementById('codex-messages');
    if (!messagesContainer) return;
    
    messagesContainer.innerHTML = '';
    
    this.state.messages.forEach(message => {
      const messageElement = document.createElement('div');
      messageElement.className = `codex-message codex-message-${message.role}`;
      
      // Format the message
      let formattedContent = message.content;
      
      // Convert any Markdown code blocks
      formattedContent = formattedContent.replace(
        /```([\s\S]*?)```/g, 
        (match, code) => `<pre class="codex-code-block">${code}</pre>`
      );
      
      // Convert single backtick code spans
      formattedContent = formattedContent.replace(
        /`([^`]+)`/g,
        (match, code) => `<code>${code}</code>`
      );
      
      messageElement.innerHTML = formattedContent;
      messagesContainer.appendChild(messageElement);
    });
  },
  
  // Update the UI based on current state
  updateUI: function() {
    // Update connection status
    const statusElement = document.getElementById('codex-status');
    if (statusElement) {
      if (!this.state.connected) {
        statusElement.className = 'status disconnected';
        statusElement.textContent = 'Disconnected';
      } else {
        this.updateSessionStatus();
      }
    }
    
    // Update emergency connection status if method exists
    if (this.updateConnectionStatus) {
      this.updateConnectionStatus();
    }
    
    // Render messages
    this.renderMessages();
    
    // Update file list
    this.updateFileList();
    
    // Check for chat input in the RIGHT FOOTER after UI updates
    this.checkForChatInput();
  },
  
  // Clean up resources
  cleanup: function() {
    // Clear ping interval
    if (this.pingIntervalId) {
      clearInterval(this.pingIntervalId);
      this.pingIntervalId = null;
    }
    
    // Close WebSocket connection
    if (this.socket && this.socket.readyState !== WebSocket.CLOSED) {
      this.socket.close();
    }
  },
  
  // Define panels for the Tekton UI
  panels: {
    // Console panel - Main Aider interface
    console: function() {
      return `
        <div class="codex-container">
          <div class="codex-header">
            <div class="header-left">
              <h2>Aider Code Assistant</h2>
              <div id="codex-status" class="status">Initializing...</div>
            </div>
            <!-- New Session button will be added programmatically -->
          </div>
          
          <div class="codex-body">
            <div id="codex-messages" class="codex-messages"></div>
          </div>
          
          <!-- Input is handled by RIGHT FOOTER chat input -->
          
          <style>
            .codex-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
            }
            
            .header-left {
              display: flex;
              align-items: center;
              gap: 10px;
            }
            
            .new-session-button {
              padding: 5px 10px;
              background-color: #2c2c2c;
              color: #ffffff;
              border: 1px solid #444;
              border-radius: 4px;
              cursor: pointer;
            }
            
            .new-session-button:hover {
              background-color: #3c3c3c;
            }
            
            .new-session-button:disabled {
              opacity: 0.5;
              cursor: not-allowed;
            }
            
            .status.starting {
              background-color: rgba(245, 158, 11, 0.2);
              color: #f59e0b;
            }
            
            .codex-message-user.input-received {
              animation: highlight-pulse 1s;
            }
            
            @keyframes highlight-pulse {
              0% { background-color: rgba(59, 130, 246, 0.1); }
              50% { background-color: rgba(59, 130, 246, 0.3); }
              100% { background-color: rgba(59, 130, 246, 0.1); }
            }
            
            code {
              background-color: rgba(255, 255, 255, 0.1);
              padding: 2px 4px;
              border-radius: 3px;
              font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            }
          </style>
        </div>
      `;
    },
    
    // Data panel - Files view
    data: function() {
      return `
        <div class="codex-container">
          <div class="codex-header">
            <h2>Active Files</h2>
            <div><small>Click on a file to focus Aider on it</small></div>
          </div>
          
          <div class="codex-body">
            <div id="codex-files" class="codex-files"></div>
          </div>
          
          <style>
            .codex-file {
              cursor: pointer;
              transition: background-color 0.2s;
            }
            
            .codex-file:hover {
              background-color: rgba(255, 255, 255, 0.15);
            }
          </style>
        </div>
      `;
    },
    
    // Settings panel
    settings: function() {
      return `
        <div class="codex-container">
          <div class="codex-header">
            <h2>Aider Settings</h2>
          </div>
          
          <div class="codex-body" style="padding: 20px;">
            <h3>Quick Commands</h3>
            <ul style="margin-left: 20px; line-height: 1.5;">
              <li><code>/help</code> - Show Aider help</li>
              <li><code>/add &lt;file&gt;</code> - Add a file to the chat</li>
              <li><code>/focus &lt;file&gt;</code> - Focus on a specific file</li>
              <li><code>/ls</code> - List files in current directory</li>
              <li><code>/git</code> - Show git status</li>
              <li><code>/commit</code> - Commit changes</li>
              <li><code>/exit</code> - Exit Aider session</li>
            </ul>
            
            <h3>Usage Tips</h3>
            <ul style="margin-left: 20px; line-height: 1.5;">
              <li>Be specific about the changes you want to make</li>
              <li>Provide file paths when discussing new files</li>
              <li>Use the Files tab to see which files are in the conversation</li>
              <li>Try clicking on a file in the Files tab to focus on it</li>
            </ul>
          </div>
        </div>
      `;
    }
  }
};

// Export the connector
export default codexConnector;