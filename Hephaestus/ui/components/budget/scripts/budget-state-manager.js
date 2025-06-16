/**
 * Budget State Manager
 * 
 * Manages the state for the Budget component with unidirectional data flow
 * Part of the Budget UI Update Sprint implementation
 */
class BudgetStateManager {
    /**
     * Create a new state manager instance
     * @param {Object} initialState - Initial state (optional)
     */
    constructor(initialState = {}) {
        // Initialize state with defaults
        this.state = {
            isInitialized: false,
            activeTab: initialState.activeTab || 'dashboard',
            
            // Data models
            dashboardData: new window.BudgetModels.DashboardData(),
            usageData: new window.BudgetModels.UsageData(),
            settingsData: new window.BudgetModels.SettingsData(),
            alertsData: new window.BudgetModels.AlertsData(),
            chatData: {
                budgetchat: new window.BudgetModels.ChatData({ chatType: 'budgetchat' }),
                teamchat: new window.BudgetModels.ChatData({ chatType: 'teamchat' })
            },
            
            // UI state
            isLoading: {
                dashboard: false,
                usage: false,
                settings: false,
                alerts: false,
                chat: false
            },
            
            // Error state
            errors: {
                dashboard: null,
                usage: null,
                settings: null,
                alerts: null,
                chat: null
            },
            
            // WebSocket state
            webSocket: {
                budget_events: false,
                budget_alerts: false,
                allocation_updates: false,
                price_updates: false
            }
        };
        
        // Initialize listeners
        this.listeners = [];
        
        // Set for tracking pending updates
        this.pendingUpdates = new Set();
        
        // Whether a state update is scheduled
        this.updateScheduled = false;
    }
    
    /**
     * Get the current state
     * @returns {Object} Current state
     */
    getState() {
        return { ...this.state };
    }
    
    /**
     * Schedule a state update
     * @param {Function} updateFn - Function to update state
     */
    scheduleUpdate(updateFn) {
        // Add update to pending updates
        this.pendingUpdates.add(updateFn);
        
        // Schedule update if not already scheduled
        if (!this.updateScheduled) {
            this.updateScheduled = true;
            
            // Use requestAnimationFrame for efficiency
            window.requestAnimationFrame(() => this.processPendingUpdates());
        }
    }
    
    /**
     * Process all pending updates
     */
    processPendingUpdates() {
        // Make a copy of the current state
        const nextState = { ...this.state };
        
        // Apply all pending updates
        for (const updateFn of this.pendingUpdates) {
            updateFn(nextState);
        }
        
        // Clear pending updates
        this.pendingUpdates.clear();
        this.updateScheduled = false;
        
        // Update state and notify listeners
        this.state = nextState;
        this.notifyListeners();
    }
    
    /**
     * Add a listener for state changes
     * @param {Function} listener - Listener function
     * @returns {Function} Function to remove the listener
     */
    addListener(listener) {
        this.listeners.push(listener);
        
        // Return function to remove listener
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }
    
    /**
     * Notify all listeners of state change
     */
    notifyListeners() {
        // Make a shallow copy of state for listeners
        const stateCopy = { ...this.state };
        
        // Notify all listeners
        for (const listener of this.listeners) {
            listener(stateCopy);
        }
    }
    
    /**
     * Initialize component state
     * @param {boolean} success - Whether initialization was successful
     */
    setInitialized(success = true) {
        this.scheduleUpdate(state => {
            state.isInitialized = success;
        });
    }
    
    /**
     * Set active tab
     * @param {string} tabId - Tab ID
     */
    setActiveTab(tabId) {
        this.scheduleUpdate(state => {
            state.activeTab = tabId;
        });
    }
    
    /**
     * Set loading state for a section
     * @param {string} section - Section name
     * @param {boolean} isLoading - Whether section is loading
     */
    setLoading(section, isLoading) {
        this.scheduleUpdate(state => {
            state.isLoading[section] = isLoading;
        });
    }
    
    /**
     * Set error state for a section
     * @param {string} section - Section name
     * @param {string|null} error - Error message or null
     */
    setError(section, error) {
        this.scheduleUpdate(state => {
            state.errors[section] = error;
        });
    }
    
    /**
     * Set WebSocket connection state
     * @param {string} topic - WebSocket topic
     * @param {boolean} isConnected - Whether WebSocket is connected
     */
    setWebSocketState(topic, isConnected) {
        this.scheduleUpdate(state => {
            state.webSocket[topic] = isConnected;
        });
    }
    
    /**
     * Update budget summaries with data from API
     * @param {Array} summaries - Budget summaries from API
     */
    updateBudgetSummaries(summaries) {
        this.scheduleUpdate(state => {
            state.dashboardData.updateFromSummaries(summaries);
        });
    }
    
    /**
     * Update provider distribution data
     * @param {Array} providerData - Provider distribution data
     */
    updateProviderDistribution(providerData) {
        this.scheduleUpdate(state => {
            state.dashboardData.updateProviderDistribution(providerData);
        });
    }
    
    /**
     * Update spend trend data
     * @param {Array} trendData - Spend trend data
     */
    updateSpendTrend(trendData) {
        this.scheduleUpdate(state => {
            state.dashboardData.updateSpendTrend(trendData);
        });
    }
    
    /**
     * Update top usage data
     * @param {Array} usageData - Top usage data
     */
    updateTopUsage(usageData) {
        this.scheduleUpdate(state => {
            state.dashboardData.updateTopUsage(usageData);
        });
    }
    
    /**
     * Update usage data with API response
     * @param {Object} response - API response
     */
    updateUsageData(response) {
        this.scheduleUpdate(state => {
            state.usageData.updateFromApiResponse(response);
        });
    }
    
    /**
     * Set usage filters
     * @param {Object} filters - Filter parameters
     */
    setUsageFilters(filters) {
        this.scheduleUpdate(state => {
            state.usageData.setFilters(filters);
        });
    }
    
    /**
     * Update settings data with budget response
     * @param {Object} budgetsResponse - Budgets API response
     */
    updateBudgetSettings(budgetsResponse) {
        this.scheduleUpdate(state => {
            state.settingsData.updateFromBudgetsResponse(budgetsResponse);
        });
    }
    
    /**
     * Update settings data with policies response
     * @param {Object} policiesResponse - Policies API response
     */
    updatePolicySettings(policiesResponse) {
        this.scheduleUpdate(state => {
            state.settingsData.updateFromPoliciesResponse(policiesResponse);
        });
    }
    
    /**
     * Update provider settings
     * @param {Array} providers - Provider data
     */
    updateProviderSettings(providers) {
        this.scheduleUpdate(state => {
            state.settingsData.updateProviders(providers);
        });
    }
    
    /**
     * Update alerts data with API response
     * @param {Object} response - API response
     */
    updateAlerts(response) {
        this.scheduleUpdate(state => {
            state.alertsData.updateFromApiResponse(response);
        });
    }
    
    /**
     * Add alerts to the alerts data
     * @param {Array} alerts - Alert data
     */
    addAlerts(alerts) {
        this.scheduleUpdate(state => {
            // Create a new alerts array with the new alerts added
            const allAlerts = [
                ...alerts.map(alert => ({
                    id: alert.alert_id,
                    title: alert.title || '',
                    description: alert.message || '',
                    severity: alert.severity || 'info',
                    timestamp: new Date(alert.timestamp),
                    acknowledged: alert.acknowledged || false,
                    budgetId: alert.budget_id,
                    type: alert.type || 'budget'
                })),
                ...state.alertsData.alerts
            ];
            
            // Update state with the new alerts
            state.alertsData.alerts = allAlerts;
            state.alertsData.totalAlerts = allAlerts.length;
        });
    }
    
    /**
     * Update alert settings
     * @param {Object} settings - Alert settings
     */
    updateAlertSettings(settings) {
        this.scheduleUpdate(state => {
            state.alertsData.updateSettings(settings);
        });
    }
    
    /**
     * Add a chat message from user
     * @param {string} text - Message text
     * @param {string} chatType - Chat type (budgetchat or teamchat)
     */
    addUserChatMessage(text, chatType) {
        this.scheduleUpdate(state => {
            state.chatData[chatType].addUserMessage(text);
        });
    }
    
    /**
     * Add a chat message from AI
     * @param {string} text - Message text
     * @param {string} chatType - Chat type (budgetchat or teamchat)
     */
    addAiChatMessage(text, chatType) {
        this.scheduleUpdate(state => {
            state.chatData[chatType].addAiMessage(text);
        });
    }
    
    /**
     * Add a system message to chat
     * @param {string} text - Message text
     * @param {string} chatType - Chat type (budgetchat or teamchat)
     */
    addSystemChatMessage(text, chatType) {
        this.scheduleUpdate(state => {
            state.chatData[chatType].addSystemMessage(text);
        });
    }
    
    /**
     * Clear chat messages
     * @param {string} chatType - Chat type (budgetchat or teamchat)
     */
    clearChat(chatType) {
        this.scheduleUpdate(state => {
            state.chatData[chatType].clear();
        });
    }
    
    /**
     * Update an allocation
     * @param {Object} allocation - Allocation data
     */
    updateAllocation(allocation) {
        // This would typically update a list of allocations in the state
        // For now, we'll just log it since it's not directly shown in the UI
        console.log('[BUDGET] Allocation updated:', allocation);
    }
    
    /**
     * Update pricing data
     * @param {string} provider - Provider name
     * @param {string} model - Model name
     * @param {Object} update - Price update data
     */
    updatePricing(provider, model, update) {
        // This would typically update a list of prices in the state
        // For now, we'll just log it since it's not directly shown in the UI
        console.log('[BUDGET] Price updated:', provider, model, update);
    }
    
    /**
     * Load settings from localStorage
     */
    loadFromStorage() {
        try {
            const storedData = localStorage.getItem('budgetComponentState');
            
            if (storedData) {
                const parsedData = JSON.parse(storedData);
                
                // Selectively update state with stored data
                if (parsedData.activeTab) {
                    this.setActiveTab(parsedData.activeTab);
                }
            }
        } catch (error) {
            console.error('[BUDGET] Error loading state from localStorage:', error);
        }
    }
    
    /**
     * Save settings to localStorage
     */
    saveToStorage() {
        try {
            // Only store essential state
            const dataToStore = {
                activeTab: this.state.activeTab
            };
            
            localStorage.setItem('budgetComponentState', JSON.stringify(dataToStore));
        } catch (error) {
            console.error('[BUDGET] Error saving state to localStorage:', error);
        }
    }
}

// Export as global class
window.BudgetStateManager = BudgetStateManager;