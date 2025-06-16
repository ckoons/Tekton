/**
 * Sophia Component for Hephaestus UI
 * 
 * This script implements the Sophia dashboard component for the Tekton UI.
 */

// Initialize the Sophia component when the DOM is loaded
document.addEventListener('DOMContentLoaded', initSophia);

// Global variables
let sophiaConfig = {
  apiUrl: window.env?.SOPHIA_API_URL || 'http://localhost:8006/api',
  wsUrl: window.env?.SOPHIA_WS_URL || 'ws://localhost:8006/ws',
  refreshInterval: 30000, // 30 seconds
  chartColors: [
    '#4285F4', '#EA4335', '#FBBC05', '#34A853', 
    '#8F8F8F', '#46BFBD', '#F7464A', '#FDB45C'
  ]
};

let sophiaState = {
  components: [],
  metrics: {},
  experiments: [],
  recommendations: [],
  intelligenceProfiles: {},
  researchProjects: [],
  websocket: null,
  refreshTimers: {},
  currentView: 'metrics'
};

/**
 * Initialize the Sophia component
 */
function initSophia() {
  console.log('Initializing Sophia component...');
  
  // Set up view selector
  const viewSelector = document.getElementById('sophia-view-selector');
  if (viewSelector) {
    viewSelector.addEventListener('change', (e) => {
      switchView(e.target.value);
    });
  }
  
  // Set up refresh button
  const refreshBtn = document.getElementById('sophia-refresh-btn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      refreshCurrentView();
    });
  }
  
  // Initialize WebSocket connection
  initWebSocket();
  
  // Load initial data
  loadComponents()
    .then(() => {
      // Load data for current view
      refreshCurrentView();
      
      // Set up auto-refresh
      sophiaState.refreshTimers.main = setInterval(() => {
        refreshCurrentView();
      }, sophiaConfig.refreshInterval);
    })
    .catch(err => {
      console.error('Error initializing Sophia component:', err);
      showNotification('Error initializing Sophia component', 'error');
    });
  
  // Set up event listeners for various UI elements
  setupEventListeners();
  
  console.log('Sophia component initialized');
}

/**
 * Initialize WebSocket connection
 */
function initWebSocket() {
  try {
    sophiaState.websocket = new WebSocket(sophiaConfig.wsUrl);
    
    sophiaState.websocket.onopen = (event) => {
      console.log('WebSocket connection established');
      
      // Subscribe to updates
      sophiaState.websocket.send(JSON.stringify({
        type: 'subscribe',
        channel: 'updates',
        filters: {
          components: []
        }
      }));
    };
    
    sophiaState.websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
      } catch (err) {
        console.error('Error handling WebSocket message:', err);
      }
    };
    
    sophiaState.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    sophiaState.websocket.onclose = (event) => {
      console.log('WebSocket connection closed');
      
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        initWebSocket();
      }, 5000);
    };
  } catch (err) {
    console.error('Error initializing WebSocket:', err);
  }
}

/**
 * Handle WebSocket messages
 * @param {Object} message - The message received from the WebSocket
 */
function handleWebSocketMessage(message) {
  console.log('WebSocket message received:', message);
  
  switch (message.type) {
    case 'metric_update':
      // Update metrics data and refresh charts if on metrics view
      if (sophiaState.currentView === 'metrics') {
        loadMetrics()
          .then(() => {
            updateMetricsCharts();
          });
      }
      break;
      
    case 'experiment_update':
      // Update experiments data if on experiments view
      if (sophiaState.currentView === 'experiments') {
        loadExperiments();
      }
      break;
      
    case 'recommendation_update':
      // Update recommendations data if on recommendations view
      if (sophiaState.currentView === 'recommendations') {
        loadRecommendations();
      }
      break;
      
    case 'intelligence_update':
      // Update intelligence data if on intelligence view
      if (sophiaState.currentView === 'intelligence') {
        loadIntelligenceProfiles();
      }
      break;
      
    case 'research_update':
      // Update research data if on research view
      if (sophiaState.currentView === 'research') {
        loadResearchProjects();
      }
      break;
      
    case 'subscription_confirmed':
      console.log('Subscription confirmed:', message.channel);
      break;
      
    case 'pong':
      // Ping response, no action needed
      break;
      
    case 'error':
      console.error('WebSocket error message:', message.message);
      break;
      
    default:
      console.warn('Unknown WebSocket message type:', message.type);
  }
}

/**
 * Setup event listeners for UI elements
 */
function setupEventListeners() {
  // New experiment button
  const newExperimentBtn = document.getElementById('sophia-new-experiment-btn');
  if (newExperimentBtn) {
    newExperimentBtn.addEventListener('click', () => {
      showExperimentModal();
    });
  }
  
  // New research button
  const newResearchBtn = document.getElementById('sophia-new-research-btn');
  if (newResearchBtn) {
    newResearchBtn.addEventListener('click', () => {
      showResearchModal();
    });
  }
  
  // Component filter for metrics
  const metricsComponentFilter = document.getElementById('sophia-metrics-component-filter');
  if (metricsComponentFilter) {
    metricsComponentFilter.addEventListener('change', () => {
      updateMetricsCharts();
    });
  }
  
  // Component filter for intelligence
  const intelligenceComponentFilter = document.getElementById('sophia-intelligence-component-filter');
  if (intelligenceComponentFilter) {
    intelligenceComponentFilter.addEventListener('change', () => {
      updateIntelligenceCharts();
    });
  }
  
  // Compare button for intelligence
  const compareBtn = document.getElementById('sophia-compare-btn');
  if (compareBtn) {
    compareBtn.addEventListener('click', () => {
      compareIntelligenceProfiles();
    });
  }
}

/**
 * Load registered components
 * @returns {Promise} A promise that resolves when components are loaded
 */
function loadComponents() {
  return fetch(`${sophiaConfig.apiUrl}/components`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      sophiaState.components = data;
      
      // Populate component selector dropdowns
      populateComponentSelectors();
      
      return data;
    })
    .catch(err => {
      console.error('Error loading components:', err);
      showNotification('Error loading components', 'error');
      return [];
    });
}

/**
 * Populate component selector dropdowns
 */
function populateComponentSelectors() {
  const selectors = [
    'sophia-metrics-component-filter',
    'sophia-intelligence-component-filter',
    'sophia-recommendations-component-filter',
    'sophia-comparison-component1',
    'sophia-comparison-component2'
  ];
  
  selectors.forEach(selectorId => {
    const selector = document.getElementById(selectorId);
    if (selector) {
      // Clear existing options except the first one
      while (selector.options.length > 1) {
        selector.remove(1);
      }
      
      // Add new options
      sophiaState.components.forEach(component => {
        const option = document.createElement('option');
        option.value = component.component_id;
        option.textContent = component.name;
        selector.appendChild(option);
      });
    }
  });
}

/**
 * Switch between different views
 * @param {string} viewName - The name of the view to switch to
 */
function switchView(viewName) {
  // Hide all views
  const views = document.querySelectorAll('.sophia-view');
  views.forEach(view => {
    view.style.display = 'none';
  });
  
  // Show the selected view
  const selectedView = document.getElementById(`sophia-${viewName}-view`);
  if (selectedView) {
    selectedView.style.display = 'block';
  }
  
  // Update current view
  sophiaState.currentView = viewName;
  
  // Load data for the selected view
  refreshCurrentView();
}

/**
 * Refresh the current view
 */
function refreshCurrentView() {
  switch (sophiaState.currentView) {
    case 'metrics':
      loadMetrics()
        .then(() => {
          updateMetricsCharts();
        });
      break;
      
    case 'intelligence':
      loadIntelligenceProfiles()
        .then(() => {
          updateIntelligenceCharts();
        });
      break;
      
    case 'experiments':
      loadExperiments()
        .then(() => {
          updateExperimentsList();
        });
      break;
      
    case 'recommendations':
      loadRecommendations()
        .then(() => {
          updateRecommendationsList();
        });
      break;
      
    case 'research':
      loadResearchProjects()
        .then(() => {
          updateResearchList();
        });
      break;
      
    default:
      console.warn(`Unknown view: ${sophiaState.currentView}`);
  }
}

/**
 * Load metrics data
 * @returns {Promise} A promise that resolves when metrics are loaded
 */
function loadMetrics() {
  // Determine the time range
  const timeRangeSelector = document.getElementById('sophia-metrics-timerange');
  const timeRange = timeRangeSelector ? timeRangeSelector.value : '24h';
  
  // Calculate start time based on time range
  const now = new Date();
  let startTime;
  
  switch (timeRange) {
    case '1h':
      startTime = new Date(now.getTime() - 60 * 60 * 1000);
      break;
    case '6h':
      startTime = new Date(now.getTime() - 6 * 60 * 60 * 1000);
      break;
    case '24h':
      startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      break;
    case '7d':
      startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      break;
    case '30d':
      startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      break;
    default:
      startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  }
  
  const startTimeISO = startTime.toISOString();
  const endTimeISO = now.toISOString();
  
  // Determine component filter
  const componentSelector = document.getElementById('sophia-metrics-component-filter');
  const componentFilter = componentSelector && componentSelector.value ? componentSelector.value : '';
  
  // Determine metric type filter
  const typeSelector = document.getElementById('sophia-metrics-type-filter');
  const typeFilter = typeSelector && typeSelector.value ? typeSelector.value : '';
  
  // Build the query URL
  let url = `${sophiaConfig.apiUrl}/metrics?start_time=${startTimeISO}&end_time=${endTimeISO}`;
  
  if (componentFilter) {
    url += `&source=${componentFilter}`;
  }
  
  if (typeFilter) {
    url += `&tags=${typeFilter}`;
  }
  
  return fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      sophiaState.metrics = data;
      return data;
    })
    .catch(err => {
      console.error('Error loading metrics:', err);
      showNotification('Error loading metrics', 'error');
      return [];
    });
}

/**
 * Update metrics charts
 */
function updateMetricsCharts() {
  // This function will be implemented with actual chart library in sophia-charts.js
  console.log('Updating metrics charts...');
  
  // Trigger chart updates (to be implemented with chart library)
  if (typeof updatePerformanceChart === 'function') {
    updatePerformanceChart(sophiaState.metrics);
  }
  
  if (typeof updateResourceChart === 'function') {
    updateResourceChart(sophiaState.metrics);
  }
  
  if (typeof updateCommunicationChart === 'function') {
    updateCommunicationChart(sophiaState.metrics);
  }
  
  if (typeof updateErrorChart === 'function') {
    updateErrorChart(sophiaState.metrics);
  }
}

/**
 * Show a notification message
 * @param {string} message - The message to show
 * @param {string} type - The type of notification (info, success, warning, error)
 */
function showNotification(message, type = 'info') {
  // Check if notification function is available in parent UI
  if (typeof window.showNotification === 'function') {
    window.showNotification(message, type);
  } else {
    // Fallback to console
    switch (type) {
      case 'error':
        console.error(message);
        break;
      case 'warning':
        console.warn(message);
        break;
      case 'success':
        console.log('%c' + message, 'color: green');
        break;
      default:
        console.log(message);
    }
  }
}

// Placeholder functions for other data loading - these would be implemented similarly to loadMetrics
function loadIntelligenceProfiles() {
  return Promise.resolve([]);
}

function updateIntelligenceCharts() {
  console.log('Updating intelligence charts...');
}

function compareIntelligenceProfiles() {
  console.log('Comparing intelligence profiles...');
}

function loadExperiments() {
  return Promise.resolve([]);
}

function updateExperimentsList() {
  console.log('Updating experiments list...');
}

function showExperimentModal() {
  console.log('Showing experiment modal...');
}

function loadRecommendations() {
  return Promise.resolve([]);
}

function updateRecommendationsList() {
  console.log('Updating recommendations list...');
}

function loadResearchProjects() {
  return Promise.resolve([]);
}

function updateResearchList() {
  console.log('Updating research list...');
}

function showResearchModal() {
  console.log('Showing research modal...');
}

// Cleanup when component is unmounted
window.addEventListener('beforeunload', () => {
  // Clear any timers
  Object.values(sophiaState.refreshTimers).forEach(timer => {
    clearInterval(timer);
  });
  
  // Close WebSocket connection
  if (sophiaState.websocket && sophiaState.websocket.readyState === WebSocket.OPEN) {
    sophiaState.websocket.close();
  }
});