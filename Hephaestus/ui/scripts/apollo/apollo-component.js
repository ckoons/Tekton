/**
 * Apollo Executive Coordinator Component
 * 
 * Provides comprehensive monitoring and control for LLM operations, token budgeting,
 * protocol enforcement, and predictive planning in the Tekton system.
 */

// Import services and utilities
import { ApolloService } from './apollo-service.js';

// Global component state object
window.apolloComponent = window.apolloComponent || {
  state: {
    activeTab: 'dashboard',
    sessions: [],
    tokenBudgets: {},
    protocols: [],
    forecasts: {},
    isInitialized: false
  }
};

/**
 * Initialize the Apollo Component
 */
function initializeApolloComponent() {
  if (window.apolloComponent.isInitialized) {
    console.log('[APOLLO] Component already initialized');
    return;
  }

  console.log('[APOLLO] Initializing Apollo component');
  
  // Create service instance
  window.apolloComponent.service = new ApolloService();
  
  // Initialize event listeners
  setupEventListeners();
  
  // Load initial data
  loadData();
  
  // Mark as initialized
  window.apolloComponent.state.isInitialized = true;
  
  // Debug info
  if (window.TektonDebug) {
    window.TektonDebug.log('apollo', 'Apollo component initialized', 'info');
  }
}

/**
 * Set up all event listeners for the component
 */
function setupEventListeners() {
  const componentContainer = document.querySelector('#apollo-component');
  if (!componentContainer) {
    console.error('[APOLLO] Could not find component container');
    return;
  }
  
  // Settings button
  const settingsButton = componentContainer.querySelector('.apollo__btn-settings');
  if (settingsButton) {
    settingsButton.addEventListener('click', function() {
      console.log('[APOLLO] Settings button clicked');
      // TODO: Implement settings panel toggle
    });
  }
  
  // Attention Chat button
  const attentionChatButton = componentContainer.querySelector('.apollo__chat-option--attention');
  if (attentionChatButton) {
    attentionChatButton.addEventListener('click', function() {
      console.log('[APOLLO] Attention Chat clicked');
      // TODO: Implement Attention Chat functionality
    });
  }
  
  // Team Chat button
  const teamChatButton = componentContainer.querySelector('.apollo__chat-option--team');
  if (teamChatButton) {
    teamChatButton.addEventListener('click', function() {
      console.log('[APOLLO] Team Chat clicked');
      // TODO: Implement Team Chat functionality
    });
  }
}

/**
 * Load data from Apollo service
 */
async function loadData() {
  try {
    // Get system status
    const status = await window.apolloComponent.service.getStatus();
    updateStatusDisplay(status);
    
    // Get active sessions
    const sessions = await window.apolloComponent.service.getSessions();
    window.apolloComponent.state.sessions = sessions;
    updateSessionsDisplay(sessions);
    
    // Get token budgets
    const tokenBudgets = await window.apolloComponent.service.getTokenBudgets();
    window.apolloComponent.state.tokenBudgets = tokenBudgets;
    updateTokenBudgetsDisplay(tokenBudgets);
    
    console.log('[APOLLO] Data loaded successfully');
  } catch (error) {
    console.error('[APOLLO] Error loading data:', error);
    showError('Failed to load Apollo data. Service may be unavailable.');
  }
}

/**
 * Update status display with latest data
 */
function updateStatusDisplay(status) {
  const componentContainer = document.querySelector('#apollo-component');
  if (!componentContainer) return;
  
  // Update session count
  const sessionCountElem = componentContainer.querySelector('.session-count');
  if (sessionCountElem && status.session_count !== undefined) {
    sessionCountElem.textContent = status.session_count;
  }
  
  // Update token count
  const tokenCountElem = componentContainer.querySelector('.token-count');
  if (tokenCountElem && status.total_tokens !== undefined) {
    tokenCountElem.textContent = status.total_tokens.toLocaleString();
  }
}

/**
 * Update sessions display with latest data
 */
function updateSessionsDisplay(sessions) {
  // This would be implemented to update the sessions panel and dashboard
  console.log('[APOLLO] Sessions updated:', sessions.length);
}

/**
 * Update token budgets display with latest data
 */
function updateTokenBudgetsDisplay(tokenBudgets) {
  // This would be implemented to update the token budgets panel and dashboard
  console.log('[APOLLO] Token budgets updated');
}

/**
 * Display an error message to the user
 */
function showError(message, duration = 5000) {
  const componentContainer = document.querySelector('#apollo-component');
  if (!componentContainer) return;
  
  const errorContainer = document.createElement('div');
  errorContainer.className = 'apollo__error-message';
  errorContainer.textContent = message;
  
  componentContainer.appendChild(errorContainer);
  
  setTimeout(() => {
    errorContainer.remove();
  }, duration);
}

/**
 * Display a success message to the user
 */
function showSuccess(message, duration = 3000) {
  const componentContainer = document.querySelector('#apollo-component');
  if (!componentContainer) return;
  
  const successContainer = document.createElement('div');
  successContainer.className = 'apollo__success-message';
  successContainer.textContent = message;
  
  componentContainer.appendChild(successContainer);
  
  setTimeout(() => {
    successContainer.remove();
  }, duration);
}

// Start initialization when DOM is ready
document.addEventListener('DOMContentLoaded', initializeApolloComponent);

// Export functions for external use
export {
  initializeApolloComponent,
  loadData,
  showError,
  showSuccess
};