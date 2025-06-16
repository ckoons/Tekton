# Claude Code Prompt: Budget UI Update

## Objective

Update the existing Budget UI component in the Tekton Hephaestus UI to fully integrate with the new Budget backend service. The UI must maintain its current visual structure (RIGHT PANEL, HEADER, MENU BAR, FOOTER) while updating the JavaScript implementation to connect to the Budget API and MCP WebSocket services.

## Background

The Tekton Budget component is responsible for tracking, analyzing, and managing LLM token usage and associated costs across all Tekton components. The Budget backend component was recently developed in the Budget Consolidation Sprint, which merged functionality previously split between Apollo and Rhetor components. The UI component already exists with static data but needs to be updated to connect to the new backend services.

## Technical Requirements

1. **API Integration**
   - Create a dedicated BudgetApiClient class to connect with the Budget backend
   - Implement methods for all Budget API endpoints
   - Replace static data with dynamically loaded data from the API
   - Add proper error handling and loading states

2. **WebSocket Updates**
   - Implement WebSocket connection to Budget MCP service
   - Handle real-time updates for dashboard data and alerts
   - Connect chat functionality to Budget LLM assistant
   - Implement reconnection logic and error handling

3. **CLI Command Support**
   - Add command detection and parsing in chat input
   - Implement command execution logic
   - Create auto-complete functionality for commands
   - Display command help and documentation

4. **State Management**
   - Implement unidirectional data flow with centralized state
   - Create action handlers for all data operations
   - Optimize re-renders and update performance

5. **Chart Visualization**
   - Replace chart placeholders with real chart implementations
   - Create dynamic chart configurations based on backend data
   - Add interactive chart features (tooltips, zooming, etc.)

6. **Error Handling**
   - Implement contextual error messages for different operations
   - Add recovery options for common errors
   - Create fallback UI states for data loading failures

## File Structure

The main files to update or create are:

```
/Hephaestus/ui/components/budget/
├── budget-component.html           # Main component HTML (minor updates needed)
├── scripts/
│   ├── budget-component.js         # Primary component logic (major updates needed)
│   ├── budget-api-client.js        # New file - API client for Budget backend
│   ├── budget-state-manager.js     # New file - State management
│   ├── budget-chart-utils.js       # New file - Chart visualization utilities
│   ├── budget-cli-handler.js       # New file - CLI command parsing and execution
│   └── budget-models.js            # New file - Data models and validation
└── styles/
    └── budget.css                  # Component styles (minor updates needed)
```

## Code Style and Conventions

1. **JavaScript**
   - Use modern ES6+ features, but ensure browser compatibility
   - Follow functional programming principles where possible
   - Use clear, descriptive variable and function names
   - Add comprehensive JSDoc comments for all functions

2. **BEM Naming Convention**
   - Follow BEM (Block-Element-Modifier) for CSS classes
   - Maintain the `.budget__*` naming pattern for all elements
   - Keep CSS scoped to the component to avoid conflicts

3. **Error Handling**
   - Use try/catch blocks for operations that could fail
   - Add clear error messages with solution hints
   - Implement consistent error reporting format

4. **Component Protection**
   - Maintain the UI Manager protection methods
   - Keep all functions scoped to avoid global namespace pollution
   - Ensure the component remains fully self-contained

## Implementation Tasks

### Primary Component Updates (budget-component.js)

```javascript
/**
 * Tekton Budget Component
 * 
 * Responsible for LLM token usage tracking, cost analysis, and budget management
 * Update to connect with the new Budget backend service
 */
window.budgetComponent = (function() {
    // Private state
    let state = {
        isInitialized: false,
        activeTab: 'dashboard',
        dashboardData: null,
        usageData: null,
        settings: null,
        alerts: [],
        chatMessages: {
            budgetchat: [],
            teamchat: []
        },
        isLoading: {
            dashboard: false,
            usage: false,
            settings: false,
            alerts: false
        },
        errors: {
            dashboard: null,
            usage: null,
            settings: null,
            alerts: null,
            chat: null
        },
        webSocket: {
            isConnected: false,
            reconnectAttempts: 0
        }
    };
    
    // Create API client instance
    const apiClient = new BudgetApiClient();
    
    // State manager for handling updates
    const stateManager = new BudgetStateManager(state);
    
    // CLI command handler
    const cliHandler = new BudgetCliHandler();
    
    /**
     * Initialize the component
     */
    function init() {
        // Replace with your initialization code
        // Connect to API and WebSocket services
        // Set up event listeners
        // Load initial data
    }
    
    /**
     * Load data for the specified tab
     * @param {string} tabId - The ID of the tab to load data for
     */
    function loadTabContent(tabId) {
        // Replace with code to load the appropriate data for each tab
        // Handle loading states and error conditions
    }
    
    /**
     * Refresh all dashboard data from the API
     */
    function refreshData() {
        // Replace with data refresh implementation
        // Update loading states
        // Handle errors
    }
    
    /**
     * Handle chat message submission
     * @param {string} message - The message text
     * @param {string} chatType - The chat type (budgetchat or teamchat)
     */
    function handleChatMessage(message, chatType) {
        // Replace with chat message handling
        // Detect and process CLI commands
        // Send messages to appropriate endpoints
    }
    
    /**
     * Update chat placeholder based on active tab
     * @param {string} tabId - The active tab ID
     */
    function updateChatPlaceholder(tabId) {
        // Replace with code to update placeholder text
    }
    
    /**
     * Save component state to persistent storage
     */
    function saveComponentState() {
        // Replace with state persistence code
    }
    
    /**
     * Handle settings form submission
     */
    function saveBudgetSettings() {
        // Replace with settings saving implementation
        // Validate form inputs
        // Send to API
        // Handle response and errors
    }
    
    /**
     * Handle alert settings form submission
     */
    function saveAlertSettings() {
        // Replace with alert settings implementation
    }
    
    /**
     * Clear all alerts
     */
    function clearAlerts() {
        // Replace with alert clearing implementation
    }
    
    /**
     * Filter usage data based on current filters
     */
    function filterUsage() {
        // Replace with filter implementation
        // Get filter values from UI
        // Request filtered data from API
        // Update UI with results
    }
    
    /**
     * Connect to Budget WebSocket for real-time updates
     */
    function connectWebSocket() {
        // Replace with WebSocket connection code
        // Handle connection states
        // Implement reconnection logic
        // Process incoming messages
    }
    
    /**
     * Handle a new CLI command
     * @param {string} command - The command text
     */
    function handleCliCommand(command) {
        // Replace with command handling implementation
        // Parse command syntax
        // Execute command logic
        // Display command results
    }
    
    // Return public API
    return {
        init,
        loadTabContent,
        refreshData,
        updateChatPlaceholder,
        saveComponentState,
        saveBudgetSettings,
        saveAlertSettings,
        clearAlerts,
        filterUsage,
        state
    };
})();
```

### API Client Implementation (budget-api-client.js)

```javascript
/**
 * Budget API Client
 * 
 * Handles all communication with the Budget backend service
 */
class BudgetApiClient {
    constructor() {
        this.baseUrl = this._getBaseUrl();
        this.budgetPort = this._getBudgetPort();
        this.cache = new Map();
        this.cacheTimeout = 60000; // 1 minute cache
    }
    
    /**
     * Get base URL for API calls
     * @returns {string} Base URL
     */
    _getBaseUrl() {
        // Determine the proper base URL based on environment
        // Support local development and production
    }
    
    /**
     * Get Budget service port
     * @returns {number} Port number
     */
    _getBudgetPort() {
        // Get port from environment variables or default
        // Read from window.env configuration if available
    }
    
    /**
     * Make an API request with proper error handling
     * @param {string} endpoint - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise} Response promise
     */
    async _request(endpoint, options = {}) {
        // Implement standardized request handling
        // Add error handling and retry logic
        // Handle response parsing
    }
    
    /**
     * Get dashboard summary data
     * @param {string} period - Time period (daily, weekly, monthly)
     * @returns {Promise} Dashboard data
     */
    async getDashboardData(period = 'monthly') {
        // Implement dashboard data fetching
        // Handle caching
    }
    
    /**
     * Get detailed usage history
     * @param {object} filters - Filter parameters
     * @returns {Promise} Usage history data
     */
    async getUsageHistory(filters = {}) {
        // Implement usage history fetching
        // Support pagination
        // Apply filters
    }
    
    /**
     * Get current budget settings
     * @returns {Promise} Budget settings
     */
    async getBudgetSettings() {
        // Implement settings retrieval
    }
    
    /**
     * Save updated budget settings
     * @param {object} settings - New settings values
     * @returns {Promise} Save result
     */
    async saveBudgetSettings(settings) {
        // Implement settings saving
    }
    
    /**
     * Get current alerts
     * @returns {Promise} Alert list
     */
    async getAlerts() {
        // Implement alerts retrieval
    }
    
    /**
     * Clear an alert by ID
     * @param {string} alertId - Alert identifier
     * @returns {Promise} Operation result
     */
    async dismissAlert(alertId) {
        // Implement alert dismissal
    }
    
    /**
     * Execute a CLI command
     * @param {string} command - Command text
     * @returns {Promise} Command result
     */
    async executeCommand(command) {
        // Implement command execution
    }
    
    /**
     * Get CLI command help documentation
     * @param {string} command - Command name (optional)
     * @returns {Promise} Command help documentation
     */
    async getCommandHelp(command = null) {
        // Implement command help retrieval
    }
}
```

### Chart Utilities Implementation (budget-chart-utils.js)

```javascript
/**
 * Budget Chart Utilities
 * 
 * Handles creation and configuration of chart visualizations
 */
class BudgetChartUtils {
    /**
     * Create a usage trend chart
     * @param {string} elementId - Target element ID
     * @param {Array} data - Chart data
     * @param {object} options - Chart options
     */
    createTrendChart(elementId, data, options = {}) {
        // Implement trend chart creation
        // Configure chart options
        // Handle responsiveness
    }
    
    /**
     * Create a distribution pie chart
     * @param {string} elementId - Target element ID
     * @param {Array} data - Chart data
     * @param {object} options - Chart options
     */
    createDistributionChart(elementId, data, options = {}) {
        // Implement pie chart creation
        // Add interactive features
    }
    
    /**
     * Update an existing chart with new data
     * @param {string} elementId - Target element ID
     * @param {Array} data - New chart data
     */
    updateChart(elementId, data) {
        // Implement chart updating
        // Handle transition animations
    }
    
    /**
     * Format data for chart display
     * @param {object} rawData - Raw API data
     * @param {string} chartType - Type of chart
     * @returns {Array} Formatted chart data
     */
    formatDataForChart(rawData, chartType) {
        // Implement data formatting
        // Handle different chart types
    }
}
```

### CLI Command Handler Implementation (budget-cli-handler.js)

```javascript
/**
 * Budget CLI Command Handler
 * 
 * Parses and processes CLI commands in the chat interface
 */
class BudgetCliHandler {
    constructor() {
        this.commandPrefix = '/';
        this.availableCommands = this._initCommands();
    }
    
    /**
     * Initialize available commands
     * @returns {object} Command definitions
     */
    _initCommands() {
        // Define all available commands
        // Specify parameters and help text
        // Define execution functions
    }
    
    /**
     * Check if text is a CLI command
     * @param {string} text - Input text
     * @returns {boolean} Is command
     */
    isCommand(text) {
        // Detect if input is a command
    }
    
    /**
     * Parse command text into command and arguments
     * @param {string} text - Command text
     * @returns {object} Parsed command
     */
    parseCommand(text) {
        // Parse command syntax
        // Extract command name and arguments
    }
    
    /**
     * Execute a parsed command
     * @param {object} parsedCommand - The parsed command
     * @param {object} apiClient - API client for backend commands
     * @returns {Promise} Command result
     */
    async executeCommand(parsedCommand, apiClient) {
        // Execute the appropriate command
        // Handle execution errors
        // Format command response
    }
    
    /**
     * Get autocompletion suggestions for partial command
     * @param {string} partial - Partial command text
     * @returns {Array} Suggestion list
     */
    getAutocompleteSuggestions(partial) {
        // Generate command suggestions
        // Include parameter hints
    }
    
    /**
     * Get help text for a command
     * @param {string} command - Command name
     * @returns {string} Help text
     */
    getCommandHelp(command) {
        // Return detailed help for command
        // Include examples
    }
}
```

## Specific TAB Implementation Guidelines

### Dashboard Tab
- Replace static card data with dynamic API data
- Implement real chart visualizations
- Add period selection functionality
- Implement auto-refresh with configurable interval

### Usage Details Tab
- Connect table to API data with pagination
- Implement filtering and sorting
- Add date range selection
- Create export functionality for data

### Settings Tab
- Connect all form inputs to API settings
- Implement validation rules
- Add save/cancel functionality
- Show setting change previews

### Alerts Tab
- Connect alert list to WebSocket updates
- Implement alert dismissal and management
- Add alert notification configuration
- Create alert history view

### Chat Tabs
- Connect to Budget LLM assistant via WebSocket (Budget Chat tab)
- Implement message history and formatting for both chat tabs
- Add CLI command support with highlighting
- Create autocomplete for commands

## Testing Requirements

Implement comprehensive testing for all new functionality:

1. **Unit Tests**
   - Create tests for API client methods
   - Test command parsing and execution
   - Validate data transformations

2. **Integration Tests**
   - Test end-to-end flows from UI to backend
   - Verify WebSocket communication
   - Test error scenarios and recovery

3. **UI Tests**
   - Validate rendering in different browsers
   - Test responsive layout behavior
   - Verify accessibility compliance

## Documentation

Add comprehensive documentation for:

1. **Code Comments**
   - Use JSDoc format for all functions
   - Explain complex logic and algorithms
   - Document function parameters and return values

2. **User Guide**
   - Describe how to use each feature
   - Document CLI commands and syntax
   - Explain budget management concepts

3. **API Reference**
   - Document all API endpoints
   - Explain data formats and validations
   - Provide examples of common operations

## Handover Instructions

1. Ensure all code is committed with clear commit messages
2. Document any known limitations or future improvement areas
3. Create a brief summary of implementation decisions
4. Compile a list of remaining tasks or enhancements

## Additional Notes

1. Maintain backward compatibility with existing Tekton integrations
2. Ensure the component works in all supported browsers
3. Follow best practices for security, especially for user input
4. Optimize performance for large datasets and complex visualizations

# APPENDIX: Budget UI Update Sprint Analysis

Based on thorough analysis of the existing codebase, here's the required approach for the Budget UI Update Sprint:

## Current State

- Fully structured Budget UI exists at `/Hephaestus/ui/components/budget/budget-component.html`
- UI has 6 tabs: Dashboard, Usage Details, Settings, Alerts, Budget Chat, and Team Chat
- Currently displays only static placeholder data and mock visualizations
- All UI elements, styling, and layout are already implemented

## Implementation Requirements

### 1. API Integration
- Create `budget-api-client.js` to connect to new Budget backend endpoints
- Replace static data with dynamic data from API endpoints:
  - Dashboard: `/api/usage/summary` 
  - Usage: `/api/usage/records` and `/api/usage/analytics`
  - Settings: `/api/budgets`, `/api/policies`
  - Alerts: `/api/alerts`

### 2. WebSocket Integration
- Connect to WebSocket endpoints for real-time updates:
  - `/ws/budget/updates`
  - `/ws/budget/alerts`
  - `/ws/budget/allocations`
  - `/ws/budget/prices`
- Implement reconnection logic and message handling
- Update UI components in real-time when receiving WebSocket messages

### 3. Budget LLM Assistant Integration
- Connect Budget Chat tab to Budget LLM Assistant via endpoints:
  - `/api/assistant/analyze`
  - `/api/assistant/optimize`
  - `/api/assistant/recommend-model`
- Implement CLI-like command interpretation in chat interface
- Support visualization of assistant recommendations

### 4. Chart Visualization
- Implement dynamic chart rendering for budget data
- Replace static chart placeholders with Chart.js implementation
- Create visualizations for usage, allocations, and cost analytics

## Technical Approach
- Preserve existing UI structure and styling
- Focus on connecting UI elements to real backend data
- Implement state management for component data
- Add error handling and loading states
- Ensure adherence to Single Port Architecture pattern

This approach emphasizes updating the JavaScript implementation while maintaining the existing UI design, creating a connection between the recently developed Budget backend services and the existing UI component.