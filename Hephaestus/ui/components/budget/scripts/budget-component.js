/**
 * Tekton Budget Component
 * 
 * Responsible for LLM token usage tracking, cost analysis, and budget management
 * Updated to connect with the Budget backend service
 * Part of the Budget UI Update Sprint implementation
 */
window.budgetComponent = (function() {
    // Private state
    let stateManager, apiClient, wsHandler, chartUtils, cliHandler;
    
    /**
     * Initialize the component
     */
    function init() {
        console.log('[BUDGET] Initializing budget component');
        
        // Initialize state manager
        stateManager = new window.BudgetStateManager();
        
        // Initialize API client
        apiClient = new window.BudgetApiClient();
        
        // Initialize chart utilities
        chartUtils = new window.BudgetChartUtils();
        
        // Initialize CLI handler
        cliHandler = new window.BudgetCliHandler(apiClient, stateManager);
        
        // Initialize WebSocket handler
        wsHandler = new window.BudgetWebSocketHandler(stateManager);
        
        // Load saved state
        stateManager.loadFromStorage();
        
        // Set up event handlers
        setupEventHandlers();
        
        // Connect WebSockets
        wsHandler.connectToAllEndpoints();
        wsHandler.startHeartbeat();
        
        // Load initial data
        loadInitialData();
        
        // Update chat placeholder
        updateChatPlaceholder(stateManager.getState().activeTab);
        
        // Update UI with initial state
        updateUI(stateManager.getState());
        
        // Mark as initialized
        stateManager.setInitialized(true);
        console.log('[BUDGET] Budget component initialized');
    }
    
    /**
     * Set up event handlers for component
     */
    function setupEventHandlers() {
        // Listen for state changes
        stateManager.addListener(updateUI);
        
        // Set up chat input handler
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');
        
        if (chatInput && sendButton) {
            // Send message on Enter key
            chatInput.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    sendChatMessage();
                }
            });
            
            // Send message on button click
            sendButton.addEventListener('click', function(event) {
                event.preventDefault();
                sendChatMessage();
            });
        }
        
        // Set up period select handler
        const periodSelect = document.getElementById('period-select');
        if (periodSelect) {
            periodSelect.addEventListener('change', function() {
                refreshDashboard(this.value);
            });
        }
        
        // Set up date filter handler
        const filterUsageButton = document.getElementById('filter-usage');
        if (filterUsageButton) {
            filterUsageButton.addEventListener('click', function(event) {
                event.preventDefault();
                filterUsage();
            });
        }
        
        // Set up settings form handlers
        const saveBudgetSettingsButton = document.getElementById('save-budget-settings');
        if (saveBudgetSettingsButton) {
            saveBudgetSettingsButton.addEventListener('click', function(event) {
                event.preventDefault();
                saveBudgetSettings();
            });
        }
        
        // Set up alert settings form handlers
        const saveAlertSettingsButton = document.getElementById('save-alert-settings');
        if (saveAlertSettingsButton) {
            saveAlertSettingsButton.addEventListener('click', function(event) {
                event.preventDefault();
                saveAlertSettings();
            });
        }
    }
    
    /**
     * Load initial data for all tabs
     */
    async function loadInitialData() {
        console.log('[BUDGET] Loading initial data');
        
        try {
            // Load dashboard data
            await loadDashboardData();
            
            // Load first page of usage data
            await loadUsageData();
            
            // Load settings data
            await loadSettingsData();
            
            // Load alerts data
            await loadAlertsData();
            
        } catch (error) {
            console.error('[BUDGET] Error loading initial data:', error);
        }
    }
    
    /**
     * Update UI with new state
     * @param {Object} state - Current component state
     */
    function updateUI(state) {
        console.log('[BUDGET] Updating UI with state:', state);
        
        // Skip if component is not initialized
        if (!state.isInitialized) return;
        
        // Update based on active tab
        switch (state.activeTab) {
            case 'dashboard':
                updateDashboardTab(state.dashboardData);
                break;
                
            case 'details':
                updateUsageDetailsTab(state.usageData);
                break;
                
            case 'settings':
                updateSettingsTab(state.settingsData);
                break;
                
            case 'alerts':
                updateAlertsTab(state.alertsData);
                break;
                
            case 'budgetchat':
                updateChatTab(state.chatData.budgetchat, 'budgetchat');
                break;
                
            case 'teamchat':
                updateChatTab(state.chatData.teamchat, 'teamchat');
                break;
        }
        
        // Update loading states
        updateLoadingStates(state.isLoading);
        
        // Update error states
        updateErrorStates(state.errors);
        
        // Save state to storage
        stateManager.saveToStorage();
    }
    
    /**
     * Update dashboard tab UI
     * @param {Object} dashboardData - Dashboard data
     */
    function updateDashboardTab(dashboardData) {
        console.log('[BUDGET] Updating dashboard tab:', dashboardData);
        
        // Update summary cards
        updateSummaryCards(dashboardData);
        
        // Update charts
        updateCharts(dashboardData);
        
        // Update top usage table
        updateTopUsageTable(dashboardData.topUsage);
    }
    
    /**
     * Update summary cards with data
     * @param {Object} dashboardData - Dashboard data
     */
    function updateSummaryCards(dashboardData) {
        // Update daily spend card
        updateCard(
            'Daily Spend',
            formatCurrency(dashboardData.dailySpend.amount),
            formatCurrency(dashboardData.dailySpend.limit),
            dashboardData.dailySpend.percentage,
            dashboardData.dailySpend.period
        );
        
        // Update weekly spend card
        updateCard(
            'Weekly Spend',
            formatCurrency(dashboardData.weeklySpend.amount),
            formatCurrency(dashboardData.weeklySpend.limit),
            dashboardData.weeklySpend.percentage,
            dashboardData.weeklySpend.period
        );
        
        // Update monthly spend card
        updateCard(
            'Monthly Spend',
            formatCurrency(dashboardData.monthlySpend.amount),
            formatCurrency(dashboardData.monthlySpend.limit),
            dashboardData.monthlySpend.percentage,
            dashboardData.monthlySpend.period
        );
        
        // Update token usage card
        const tokenCard = document.querySelector(`.budget__card:nth-child(4)`);
        if (tokenCard) {
            const amountEl = tokenCard.querySelector('.budget__card-amount');
            const footerItems = tokenCard.querySelectorAll('.budget__card-footer div');
            
            if (amountEl) {
                amountEl.textContent = formatTokens(dashboardData.tokenUsage.amount);
            }
            
            if (footerItems && footerItems.length >= 2) {
                footerItems[0].textContent = `Input: ${formatTokens(dashboardData.tokenUsage.input)}`;
                footerItems[1].textContent = `Output: ${formatTokens(dashboardData.tokenUsage.output)}`;
            }
        }
    }
    
    /**
     * Update a budget card with data
     * @param {string} title - Card title
     * @param {string} amount - Amount value
     * @param {string} limit - Limit value
     * @param {number} percentage - Usage percentage
     * @param {string} period - Time period
     */
    function updateCard(title, amount, limit, percentage, period) {
        const card = document.querySelector(`.budget__card .budget__card-title:contains("${title}")`).closest('.budget__card');
        
        if (!card) return;
        
        const amountEl = card.querySelector('.budget__card-amount');
        const limitEl = card.querySelector('.budget__card-limit');
        const progressEl = card.querySelector('.budget__card-progress-bar');
        const footerItems = card.querySelectorAll('.budget__card-footer div');
        const periodEl = card.querySelector('.budget__card-period');
        
        if (amountEl) amountEl.textContent = amount;
        if (limitEl) limitEl.textContent = `/ ${limit}`;
        
        if (progressEl) {
            progressEl.style.width = `${percentage}%`;
            
            // Add warning/danger classes based on percentage
            progressEl.classList.remove('budget__card-progress-bar--warning', 'budget__card-progress-bar--danger');
            
            if (percentage > 90) {
                progressEl.classList.add('budget__card-progress-bar--danger');
            } else if (percentage > 70) {
                progressEl.classList.add('budget__card-progress-bar--warning');
            }
        }
        
        if (footerItems && footerItems.length >= 1) {
            footerItems[0].textContent = `${percentage.toFixed(1)}% of ${title.toLowerCase()}`;
        }
        
        if (periodEl) {
            periodEl.textContent = period;
        }
    }
    
    /**
     * Update charts with data
     * @param {Object} dashboardData - Dashboard data
     */
    function updateCharts(dashboardData) {
        // Update provider distribution chart
        if (dashboardData.spendByProvider && dashboardData.spendByProvider.length > 0) {
            // Check if chart exists, otherwise create it
            if (!chartUtils.charts['provider-pie-chart-canvas']) {
                // Create canvas for chart
                chartUtils.createCanvasForChart('provider-pie-chart');
                
                // Create chart
                chartUtils.createDistributionChart('provider-pie-chart-canvas', dashboardData.spendByProvider);
            } else {
                // Update existing chart
                chartUtils.updateChart('provider-pie-chart-canvas', dashboardData.spendByProvider, 'distribution');
            }
            
            // Update legend
            updateChartLegend('provider-pie-chart', dashboardData.spendByProvider, item => 
                `${item.provider}: ${formatCurrency(item.amount)}`
            );
            
        } else {
            // Show placeholder
            chartUtils.createPlaceholder('provider-pie-chart', 'No provider data available');
        }
        
        // Update spend trend chart
        if (dashboardData.spendTrend && dashboardData.spendTrend.length > 0) {
            // Check if chart exists, otherwise create it
            if (!chartUtils.charts['trend-chart-canvas']) {
                // Create canvas for chart
                chartUtils.createCanvasForChart('trend-chart');
                
                // Create chart
                chartUtils.createTrendChart('trend-chart-canvas', dashboardData.spendTrend);
            } else {
                // Update existing chart
                chartUtils.updateChart('trend-chart-canvas', dashboardData.spendTrend, 'trend');
            }
            
        } else {
            // Show placeholder
            chartUtils.createPlaceholder('trend-chart', 'No trend data available');
        }
    }
    
    /**
     * Update chart legend with data
     * @param {string} chartId - Chart container ID
     * @param {Array} data - Chart data
     * @param {Function} labelFormatter - Function to format legend labels
     */
    function updateChartLegend(chartId, data, labelFormatter) {
        const legend = document.querySelector(`#${chartId}`).closest('.budget__chart-card').querySelector('.budget__chart-legend');
        
        if (!legend) return;
        
        // Clear existing legend items
        legend.innerHTML = '';
        
        // Add legend items for each data point
        for (const item of data) {
            const legendItem = document.createElement('div');
            legendItem.className = 'budget__legend-item';
            
            const colorSpan = document.createElement('span');
            colorSpan.className = 'budget__legend-color';
            colorSpan.style.backgroundColor = chartUtils.getProviderColor(item.provider);
            
            const labelSpan = document.createElement('span');
            labelSpan.className = 'budget__legend-label';
            labelSpan.textContent = labelFormatter(item);
            
            legendItem.appendChild(colorSpan);
            legendItem.appendChild(labelSpan);
            legend.appendChild(legendItem);
        }
    }
    
    /**
     * Update top usage table with data
     * @param {Array} topUsage - Top usage data
     */
    function updateTopUsageTable(topUsage) {
        const table = document.querySelector('.budget__detail table.budget__table tbody');
        
        if (!table) return;
        
        // Clear existing rows
        table.innerHTML = '';
        
        // Add rows for each item
        for (const item of topUsage) {
            const row = document.createElement('tr');
            
            // Create cells
            const nameCell = document.createElement('td');
            nameCell.textContent = item.name;
            
            const providerCell = document.createElement('td');
            const providerBadge = document.createElement('span');
            providerBadge.className = `budget__badge budget__badge--${item.provider.toLowerCase()}`;
            providerBadge.textContent = item.provider;
            providerCell.appendChild(providerBadge);
            
            const tokensCell = document.createElement('td');
            tokensCell.textContent = formatTokens(item.tokens);
            
            const costCell = document.createElement('td');
            costCell.textContent = formatCurrency(item.cost);
            
            const percentCell = document.createElement('td');
            percentCell.textContent = `${item.percentage.toFixed(1)}%`;
            
            // Add cells to row
            row.appendChild(nameCell);
            row.appendChild(providerCell);
            row.appendChild(tokensCell);
            row.appendChild(costCell);
            row.appendChild(percentCell);
            
            // Add row to table
            table.appendChild(row);
        }
    }
    
    /**
     * Update usage details tab UI
     * @param {Object} usageData - Usage data
     */
    function updateUsageDetailsTab(usageData) {
        console.log('[BUDGET] Updating usage details tab:', usageData);
        
        const table = document.querySelector('#details-panel table.budget__table tbody');
        const pagination = document.querySelector('#details-panel .budget__pagination-indicator');
        
        if (!table || !pagination) return;
        
        // Clear existing rows
        table.innerHTML = '';
        
        // Add rows for each record
        for (const record of usageData.records) {
            const row = document.createElement('tr');
            
            // Create cells
            const dateCell = document.createElement('td');
            dateCell.textContent = record.timestamp.toLocaleString();
            
            const componentCell = document.createElement('td');
            componentCell.textContent = record.component;
            
            const providerCell = document.createElement('td');
            const providerBadge = document.createElement('span');
            providerBadge.className = `budget__badge budget__badge--${record.provider.toLowerCase()}`;
            providerBadge.textContent = record.model;
            providerCell.appendChild(providerBadge);
            
            const taskCell = document.createElement('td');
            taskCell.textContent = record.taskType;
            
            const tokensCell = document.createElement('td');
            tokensCell.textContent = formatTokens(record.totalTokens);
            
            const costCell = document.createElement('td');
            costCell.textContent = formatCurrency(record.cost);
            
            // Add cells to row
            row.appendChild(dateCell);
            row.appendChild(componentCell);
            row.appendChild(providerCell);
            row.appendChild(taskCell);
            row.appendChild(tokensCell);
            row.appendChild(costCell);
            
            // Add row to table
            table.appendChild(row);
        }
        
        // Update pagination
        pagination.textContent = `Page ${usageData.currentPage} of ${usageData.totalPages}`;
        
        // Enable/disable pagination buttons
        const prevButton = document.querySelector('#details-panel .budget__pagination button:first-child');
        const nextButton = document.querySelector('#details-panel .budget__pagination button:last-child');
        
        if (prevButton) {
            prevButton.disabled = usageData.currentPage <= 1;
        }
        
        if (nextButton) {
            nextButton.disabled = usageData.currentPage >= usageData.totalPages;
        }
    }
    
    /**
     * Update settings tab UI
     * @param {Object} settingsData - Settings data
     */
    function updateSettingsTab(settingsData) {
        console.log('[BUDGET] Updating settings tab:', settingsData);
        
        // Update budget limits
        const dailyLimit = document.getElementById('daily-limit');
        const weeklyLimit = document.getElementById('weekly-limit');
        const monthlyLimit = document.getElementById('monthly-limit');
        const enforcePolicy = document.getElementById('enforce-policy');
        
        if (dailyLimit) dailyLimit.value = settingsData.getDailyBudgetLimit().toFixed(2);
        if (weeklyLimit) weeklyLimit.value = settingsData.getWeeklyBudgetLimit().toFixed(2);
        if (monthlyLimit) monthlyLimit.value = settingsData.getMonthlyBudgetLimit().toFixed(2);
        if (enforcePolicy) enforcePolicy.value = settingsData.getEnforcementPolicy();
        
        // Update provider budgets
        const anthropicLimit = document.getElementById('anthropic-limit');
        const openaiLimit = document.getElementById('openai-limit');
        const enableProviderLimits = document.getElementById('enable-provider-limits');
        
        if (anthropicLimit) anthropicLimit.value = settingsData.getProviderBudget('anthropic').toFixed(2);
        if (openaiLimit) openaiLimit.value = settingsData.getProviderBudget('openai').toFixed(2);
        if (enableProviderLimits) enableProviderLimits.checked = settingsData.isProviderLimitsEnabled();
        
        // Update advanced settings
        const warningThreshold = document.getElementById('warning-threshold');
        const allowFreeModels = document.getElementById('allow-free-models');
        const resetDay = document.getElementById('reset-day');
        
        if (warningThreshold) warningThreshold.value = settingsData.getWarningThreshold();
        if (allowFreeModels) allowFreeModels.checked = settingsData.isFreeModelsAllowed();
        if (resetDay) resetDay.value = settingsData.getResetDay();
    }
    
    /**
     * Update alerts tab UI
     * @param {Object} alertsData - Alerts data
     */
    function updateAlertsTab(alertsData) {
        console.log('[BUDGET] Updating alerts tab:', alertsData);
        
        // Update active alerts
        const alertList = document.querySelector('.budget__alert-list');
        
        if (alertList) {
            // Clear existing alerts
            alertList.innerHTML = '';
            
            // Add alerts
            for (const alert of alertsData.alerts) {
                const alertElement = document.createElement('div');
                alertElement.className = 'budget__alert';
                alertElement.dataset.alertId = alert.id;
                
                // Alert info
                const alertInfo = document.createElement('div');
                alertInfo.className = 'budget__alert-info';
                
                // Alert icon
                const alertIcon = document.createElement('div');
                alertIcon.className = `budget__alert-icon budget__alert-icon--${alert.severity}`;
                alertIcon.textContent = alert.severity === 'warning' ? '!' : 'i';
                alertInfo.appendChild(alertIcon);
                
                // Alert details
                const alertDetails = document.createElement('div');
                alertDetails.className = 'budget__alert-details';
                
                const alertTitle = document.createElement('div');
                alertTitle.className = 'budget__alert-title';
                alertTitle.textContent = alert.title;
                alertDetails.appendChild(alertTitle);
                
                const alertDescription = document.createElement('div');
                alertDescription.className = 'budget__alert-description';
                alertDescription.textContent = alert.description;
                alertDetails.appendChild(alertDescription);
                
                alertInfo.appendChild(alertDetails);
                alertElement.appendChild(alertInfo);
                
                // Alert actions
                const alertActions = document.createElement('div');
                alertActions.className = 'budget__alert-actions';
                
                const dismissButton = document.createElement('button');
                dismissButton.className = 'budget__button budget__button--small';
                dismissButton.textContent = 'Dismiss';
                dismissButton.addEventListener('click', () => dismissAlert(alert.id));
                alertActions.appendChild(dismissButton);
                
                alertElement.appendChild(alertActions);
                alertList.appendChild(alertElement);
            }
            
            // Show "no alerts" message if empty
            if (alertsData.alerts.length === 0) {
                const noAlerts = document.createElement('div');
                noAlerts.className = 'budget__alert';
                noAlerts.textContent = 'No active alerts';
                alertList.appendChild(noAlerts);
            }
        }
        
        // Update alert settings
        const enableEmailAlerts = document.getElementById('enable-email-alerts');
        const alertEmail = document.getElementById('alert-email');
        const alertFrequency = document.getElementById('alert-frequency');
        
        if (enableEmailAlerts) enableEmailAlerts.checked = alertsData.emailAlerts;
        if (alertEmail) alertEmail.value = alertsData.emailAddress;
        if (alertFrequency) alertFrequency.value = alertsData.alertFrequency;
    }
    
    /**
     * Update chat tab UI
     * @param {Object} chatData - Chat data
     * @param {string} chatType - Chat type (budgetchat or teamchat)
     */
    function updateChatTab(chatData, chatType) {
        console.log(`[BUDGET] Updating ${chatType} tab:`, chatData);
        
        const messagesContainer = document.getElementById(`${chatType}-messages`);
        
        if (!messagesContainer) return;
        
        // Clear messages container except for system messages
        const systemMessages = [];
        for (const child of messagesContainer.children) {
            if (child.classList.contains('budget__message--system')) {
                systemMessages.push(child);
            }
        }
        
        messagesContainer.innerHTML = '';
        
        // Re-add system messages
        for (const message of systemMessages) {
            messagesContainer.appendChild(message);
        }
        
        // Add chat messages
        for (const message of chatData.messages) {
            // Skip system messages as they're already added
            if (message.type === 'system') continue;
            
            const messageElement = document.createElement('div');
            messageElement.className = `budget__message budget__message--${message.type}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'budget__message-content';
            
            const textDiv = document.createElement('div');
            textDiv.className = 'budget__message-text';
            
            // Format message text
            if (message.type === 'user' && message.text.startsWith('/')) {
                // Style CLI commands
                const commandSpan = document.createElement('span');
                commandSpan.className = 'budget__command';
                commandSpan.textContent = message.text;
                textDiv.appendChild(commandSpan);
            } else {
                // Regular message
                textDiv.textContent = message.text;
            }
            
            contentDiv.appendChild(textDiv);
            messageElement.appendChild(contentDiv);
            
            // Add timestamp
            const timestamp = document.createElement('div');
            timestamp.className = 'budget__message-timestamp';
            timestamp.textContent = formatMessageTime(message.timestamp);
            messageElement.appendChild(timestamp);
            
            messagesContainer.appendChild(messageElement);
        }
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    /**
     * Update loading states in UI
     * @param {Object} loadingStates - Loading states for different sections
     */
    function updateLoadingStates(loadingStates) {
        // Handle loading state for each tab
        for (const section in loadingStates) {
            const isLoading = loadingStates[section];
            const panelId = `#${section}-panel`;
            
            // Find loading overlay or create it
            let loadingOverlay = document.querySelector(`${panelId} .budget__loading-overlay`);
            
            if (isLoading) {
                if (!loadingOverlay) {
                    // Create loading overlay
                    loadingOverlay = document.createElement('div');
                    loadingOverlay.className = 'budget__loading-overlay';
                    
                    const loadingIndicator = document.createElement('div');
                    loadingIndicator.className = 'budget__loading-indicator';
                    
                    const spinner = document.createElement('div');
                    spinner.className = 'budget__spinner';
                    
                    const loadingText = document.createElement('div');
                    loadingText.className = 'budget__loading-text';
                    loadingText.textContent = 'Loading...';
                    
                    loadingIndicator.appendChild(spinner);
                    loadingIndicator.appendChild(loadingText);
                    loadingOverlay.appendChild(loadingIndicator);
                    
                    // Add to panel
                    const panel = document.querySelector(panelId);
                    if (panel) {
                        panel.appendChild(loadingOverlay);
                    }
                }
            } else if (loadingOverlay) {
                // Remove loading overlay
                loadingOverlay.remove();
            }
        }
    }
    
    /**
     * Update error states in UI
     * @param {Object} errorStates - Error states for different sections
     */
    function updateErrorStates(errorStates) {
        // Handle error state for each tab
        for (const section in errorStates) {
            const error = errorStates[section];
            const panelId = `#${section}-panel`;
            
            // Find error message or create it
            let errorMessage = document.querySelector(`${panelId} .budget__error-message`);
            
            if (error) {
                if (!errorMessage) {
                    // Create error message
                    errorMessage = document.createElement('div');
                    errorMessage.className = 'budget__error-message';
                    
                    // Add to panel
                    const panel = document.querySelector(panelId);
                    if (panel) {
                        panel.appendChild(errorMessage);
                    }
                }
                
                // Update error message
                errorMessage.textContent = `Error: ${error}`;
                
            } else if (errorMessage) {
                // Remove error message
                errorMessage.remove();
            }
        }
    }
    
    /**
     * Load dashboard data from API
     * @param {string} period - Time period (daily, weekly, monthly)
     */
    async function loadDashboardData(period = 'monthly') {
        console.log(`[BUDGET] Loading dashboard data for period: ${period}`);
        
        // Set loading state
        stateManager.setLoading('dashboard', true);
        stateManager.setError('dashboard', null);
        
        try {
            // Load budget summary
            const summaryResponse = await apiClient.getDashboardSummary(period);
            
            // Update dashboard data with budget summary
            stateManager.updateBudgetSummaries(summaryResponse);
            
            // Load provider distribution
            const providersResponse = await apiClient.getUsageSummary(period);
            
            if (providersResponse.providers) {
                stateManager.updateProviderDistribution(providersResponse.providers);
            }
            
            // Load spend trend
            // This would typically come from a dedicated API endpoint, but for now we'll simulate it
            const trendData = generateMockTrendData();
            stateManager.updateSpendTrend(trendData);
            
            // Load top usage
            const topUsageData = providersResponse.models || [];
            stateManager.updateTopUsage(topUsageData);
            
            // Clear loading state
            stateManager.setLoading('dashboard', false);
            
        } catch (error) {
            console.error('[BUDGET] Error loading dashboard data:', error);
            stateManager.setError('dashboard', error.message);
            stateManager.setLoading('dashboard', false);
        }
    }
    
    /**
     * Load usage data from API
     * @param {Object} filters - Filter parameters
     * @param {number} page - Page number
     */
    async function loadUsageData(filters = {}, page = 1) {
        console.log(`[BUDGET] Loading usage data with filters:`, filters);
        
        // Set loading state
        stateManager.setLoading('usage', true);
        stateManager.setError('usage', null);
        
        try {
            // Set filters
            stateManager.setUsageFilters(filters);
            
            // Load usage records
            const response = await apiClient.getUsageRecords(filters, page);
            
            // Update usage data
            stateManager.updateUsageData(response);
            
            // Clear loading state
            stateManager.setLoading('usage', false);
            
        } catch (error) {
            console.error('[BUDGET] Error loading usage data:', error);
            stateManager.setError('usage', error.message);
            stateManager.setLoading('usage', false);
        }
    }
    
    /**
     * Load settings data from API
     */
    async function loadSettingsData() {
        console.log('[BUDGET] Loading settings data');
        
        // Set loading state
        stateManager.setLoading('settings', true);
        stateManager.setError('settings', null);
        
        try {
            // Load budget settings
            const budgetsResponse = await apiClient.getBudgetSettings();
            
            // Update settings data with budgets
            stateManager.updateBudgetSettings(budgetsResponse);
            
            // Load policy settings for first budget
            if (budgetsResponse.items && budgetsResponse.items.length > 0) {
                const budget = budgetsResponse.items[0];
                const policiesResponse = await apiClient.getBudgetPolicies(budget.budget_id);
                
                // Update settings data with policies
                stateManager.updatePolicySettings(policiesResponse);
            }
            
            // Load provider pricing (for provider budget settings)
            const pricesResponse = await apiClient.getPrices();
            
            // Group by provider
            const providers = [];
            const providerMap = {};
            
            for (const price of pricesResponse) {
                if (!providerMap[price.provider]) {
                    providerMap[price.provider] = {
                        name: price.provider,
                        models: [],
                        monthlyBudget: 0,
                        enabled: true
                    };
                    providers.push(providerMap[price.provider]);
                }
                
                providerMap[price.provider].models.push({
                    name: price.model,
                    inputCost: price.input_cost_per_token,
                    outputCost: price.output_cost_per_token
                });
            }
            
            // Update provider settings
            stateManager.updateProviderSettings(providers);
            
            // Clear loading state
            stateManager.setLoading('settings', false);
            
        } catch (error) {
            console.error('[BUDGET] Error loading settings data:', error);
            stateManager.setError('settings', error.message);
            stateManager.setLoading('settings', false);
        }
    }
    
    /**
     * Load alerts data from API
     */
    async function loadAlertsData() {
        console.log('[BUDGET] Loading alerts data');
        
        // Set loading state
        stateManager.setLoading('alerts', true);
        stateManager.setError('alerts', null);
        
        try {
            // Load alerts
            const response = await apiClient.getAlerts({ acknowledged: false });
            
            // Update alerts data
            stateManager.updateAlerts(response);
            
            // Clear loading state
            stateManager.setLoading('alerts', false);
            
        } catch (error) {
            console.error('[BUDGET] Error loading alerts data:', error);
            stateManager.setError('alerts', error.message);
            stateManager.setLoading('alerts', false);
        }
    }
    
    /**
     * Refresh dashboard data
     * @param {string} period - Time period (daily, weekly, monthly)
     */
    async function refreshDashboard(period = 'monthly') {
        console.log(`[BUDGET] Refreshing dashboard for period: ${period}`);
        await loadDashboardData(period);
    }
    
    /**
     * Load tab content when switching tabs
     * @param {string} tabId - Tab ID
     */
    function loadTabContent(tabId) {
        console.log(`[BUDGET] Loading content for tab: ${tabId}`);
        
        switch (tabId) {
            case 'dashboard':
                refreshDashboard();
                break;
                
            case 'details':
                filterUsage();
                break;
                
            case 'settings':
                loadSettingsData();
                break;
                
            case 'alerts':
                loadAlertsData();
                break;
        }
    }
    
    /**
     * Refresh all data for the current tab
     */
    function refreshData() {
        console.log('[BUDGET] Refreshing data');
        
        const activeTab = stateManager.getState().activeTab;
        loadTabContent(activeTab);
    }
    
    /**
     * Filter usage data based on form inputs
     */
    function filterUsage() {
        console.log('[BUDGET] Filtering usage data');
        
        const startDate = document.getElementById('start-date');
        const endDate = document.getElementById('end-date');
        
        const filters = {};
        
        if (startDate && startDate.value) {
            filters.start_date = startDate.value;
        }
        
        if (endDate && endDate.value) {
            filters.end_date = endDate.value;
        }
        
        loadUsageData(filters);
    }
    
    /**
     * Save budget settings from form
     */
    async function saveBudgetSettings() {
        console.log('[BUDGET] Saving budget settings');
        
        // Set loading state
        stateManager.setLoading('settings', true);
        stateManager.setError('settings', null);
        
        try {
            // Get state
            const state = stateManager.getState();
            const settings = state.settingsData;
            
            // Get form values
            const dailyLimit = parseFloat(document.getElementById('daily-limit').value);
            const weeklyLimit = parseFloat(document.getElementById('weekly-limit').value);
            const monthlyLimit = parseFloat(document.getElementById('monthly-limit').value);
            const enforcePolicy = document.getElementById('enforce-policy').value;
            
            const anthropicLimit = parseFloat(document.getElementById('anthropic-limit').value);
            const openaiLimit = parseFloat(document.getElementById('openai-limit').value);
            const enableProviderLimits = document.getElementById('enable-provider-limits').checked;
            
            const warningThreshold = parseInt(document.getElementById('warning-threshold').value);
            const allowFreeModels = document.getElementById('allow-free-models').checked;
            const resetDay = document.getElementById('reset-day').value;
            
            // Find and update the appropriate policies
            let updates = [];
            
            // Update daily limit policy
            const dailyPolicy = settings.policies.find(p => 
                p.period === 'daily' && 
                p.type === 'hard_limit' &&
                !p.provider && !p.tier
            );
            
            if (dailyPolicy) {
                updates.push(apiClient.updatePolicy(dailyPolicy.id, {
                    ...dailyPolicy,
                    costLimit: dailyLimit
                }));
            }
            
            // Update weekly limit policy
            const weeklyPolicy = settings.policies.find(p => 
                p.period === 'weekly' && 
                p.type === 'hard_limit' &&
                !p.provider && !p.tier
            );
            
            if (weeklyPolicy) {
                updates.push(apiClient.updatePolicy(weeklyPolicy.id, {
                    ...weeklyPolicy,
                    costLimit: weeklyLimit
                }));
            }
            
            // Update monthly limit policy
            const monthlyPolicy = settings.policies.find(p => 
                p.period === 'monthly' && 
                p.type === 'hard_limit' &&
                !p.provider && !p.tier
            );
            
            if (monthlyPolicy) {
                updates.push(apiClient.updatePolicy(monthlyPolicy.id, {
                    ...monthlyPolicy,
                    costLimit: monthlyLimit
                }));
            }
            
            // Update warning threshold policy
            const warningPolicy = settings.policies.find(p => 
                p.type === 'warning'
            );
            
            if (warningPolicy) {
                updates.push(apiClient.updatePolicy(warningPolicy.id, {
                    ...warningPolicy,
                    warningThreshold,
                    enabled: enforcePolicy === 'warn' || enforcePolicy === 'enforce'
                }));
            }
            
            // Update downgrade policy
            const downgradePolicy = settings.policies.find(p => 
                p.type === 'downgrade'
            );
            
            if (downgradePolicy) {
                updates.push(apiClient.updatePolicy(downgradePolicy.id, {
                    ...downgradePolicy,
                    enabled: enforcePolicy === 'enforce' && allowFreeModels
                }));
            }
            
            // Update provider policies
            const anthropicPolicy = settings.policies.find(p => 
                p.period === 'monthly' && 
                p.type === 'hard_limit' &&
                p.provider === 'anthropic'
            );
            
            if (anthropicPolicy) {
                updates.push(apiClient.updatePolicy(anthropicPolicy.id, {
                    ...anthropicPolicy,
                    costLimit: anthropicLimit,
                    enabled: enableProviderLimits
                }));
            }
            
            const openaiPolicy = settings.policies.find(p => 
                p.period === 'monthly' && 
                p.type === 'hard_limit' &&
                p.provider === 'openai'
            );
            
            if (openaiPolicy) {
                updates.push(apiClient.updatePolicy(openaiPolicy.id, {
                    ...openaiPolicy,
                    costLimit: openaiLimit,
                    enabled: enableProviderLimits
                }));
            }
            
            // Wait for all updates to complete
            await Promise.all(updates);
            
            // Reload settings data
            await loadSettingsData();
            
            // Clear loading state
            stateManager.setLoading('settings', false);
            
        } catch (error) {
            console.error('[BUDGET] Error saving budget settings:', error);
            stateManager.setError('settings', error.message);
            stateManager.setLoading('settings', false);
        }
    }
    
    /**
     * Save alert settings from form
     */
    async function saveAlertSettings() {
        console.log('[BUDGET] Saving alert settings');
        
        // Set loading state
        stateManager.setLoading('alerts', true);
        stateManager.setError('alerts', null);
        
        try {
            // Get form values
            const emailAlerts = document.getElementById('enable-email-alerts').checked;
            const emailAddress = document.getElementById('alert-email').value;
            const alertFrequency = document.getElementById('alert-frequency').value;
            
            // Validate email if email alerts are enabled
            if (emailAlerts && (!emailAddress || !emailAddress.includes('@'))) {
                throw new Error('Please enter a valid email address');
            }
            
            // Update alert settings
            stateManager.updateAlertSettings({
                emailAlerts,
                emailAddress,
                alertFrequency
            });
            
            // Save alert settings to API
            // This would typically make an API call to save the settings
            // For now, we'll just simulate success
            setTimeout(() => {
                stateManager.setLoading('alerts', false);
            }, 500);
            
        } catch (error) {
            console.error('[BUDGET] Error saving alert settings:', error);
            stateManager.setError('alerts', error.message);
            stateManager.setLoading('alerts', false);
        }
    }
    
    /**
     * Dismiss an alert by ID
     * @param {string} alertId - Alert ID
     */
    async function dismissAlert(alertId) {
        console.log(`[BUDGET] Dismissing alert: ${alertId}`);
        
        try {
            // Call API to acknowledge alert
            await apiClient.acknowledgeAlert(alertId);
            
            // Reload alerts data
            await loadAlertsData();
            
        } catch (error) {
            console.error('[BUDGET] Error dismissing alert:', error);
            stateManager.setError('alerts', error.message);
        }
    }
    
    /**
     * Clear all alerts
     */
    async function clearAlerts() {
        console.log('[BUDGET] Clearing all alerts');
        
        // Set loading state
        stateManager.setLoading('alerts', true);
        stateManager.setError('alerts', null);
        
        try {
            // Get all alerts
            const alertsResponse = await apiClient.getAlerts();
            
            // Acknowledge each alert
            const promises = [];
            for (const alert of alertsResponse.items) {
                promises.push(apiClient.acknowledgeAlert(alert.alert_id));
            }
            
            // Wait for all acknowledgements to complete
            await Promise.all(promises);
            
            // Reload alerts data
            await loadAlertsData();
            
        } catch (error) {
            console.error('[BUDGET] Error clearing alerts:', error);
            stateManager.setError('alerts', error.message);
            stateManager.setLoading('alerts', false);
        }
    }
    
    /**
     * Send a chat message from the input field
     */
    async function sendChatMessage() {
        const chatInput = document.getElementById('chat-input');
        if (!chatInput || !chatInput.value.trim()) return;
        
        const message = chatInput.value.trim();
        const state = stateManager.getState();
        const chatType = state.activeTab === 'budgetchat' ? 'budgetchat' : 'teamchat';
        
        console.log(`[BUDGET] Sending ${chatType} message:`, message);
        
        // Clear input
        chatInput.value = '';
        
        // Check if message is a CLI command
        if (chatType === 'budgetchat' && cliHandler.isCommand(message)) {
            // Add user message to chat
            stateManager.addUserChatMessage(message, chatType);
            
            // Set loading state
            stateManager.setLoading('chat', true);
            
            try {
                // Parse and execute command
                const parsedCommand = cliHandler.parseCommand(message);
                const result = await cliHandler.executeCommand(parsedCommand);
                
                // Add result to chat if not null
                if (result !== null) {
                    stateManager.addAiChatMessage(result, chatType);
                }
                
                // Clear loading state
                stateManager.setLoading('chat', false);
                
            } catch (error) {
                console.error('[BUDGET] CLI error:', error);
                stateManager.addAiChatMessage(`Error: ${error.message}`, chatType);
                stateManager.setLoading('chat', false);
            }
            
        } else if (chatType === 'budgetchat') {
            // Add user message to chat
            stateManager.addUserChatMessage(message, chatType);
            
            // Set loading state
            stateManager.setLoading('chat', true);
            
            try {
                // Send message to LLM assistant
                const response = await apiClient.getBudgetAnalysis({
                    period: 'monthly',
                    days: 30,
                    question: message
                });
                
                // Add response to chat
                if (response.success && response.analysis) {
                    stateManager.addAiChatMessage(response.analysis, chatType);
                } else {
                    stateManager.addAiChatMessage(
                        response.error || 'Sorry, I was unable to process that request.',
                        chatType
                    );
                }
                
                // Clear loading state
                stateManager.setLoading('chat', false);
                
            } catch (error) {
                console.error('[BUDGET] Chat error:', error);
                stateManager.addAiChatMessage(
                    `Sorry, I encountered an error: ${error.message}`,
                    chatType
                );
                stateManager.setLoading('chat', false);
            }
            
        } else if (chatType === 'teamchat') {
            // Add user message to team chat
            stateManager.addUserChatMessage(message, chatType);
            
            // For team chat, we don't send to an LLM
            // This would typically make an API call to send the message to the team
            // For now, we'll just simulate team messages
            
            // Simulate team member response after a delay
            setTimeout(() => {
                const teamResponses = [
                    "Thanks for the update on the budget usage!",
                    "I'll review the current spending and get back to you.",
                    "We should probably optimize our usage of the Anthropic models.",
                    "Have you checked the daily spending pattern? It seems to be increasing."
                ];
                
                const randomResponse = teamResponses[Math.floor(Math.random() * teamResponses.length)];
                stateManager.addAiChatMessage(`Team Member: ${randomResponse}`, chatType);
            }, 1500);
        }
    }
    
    /**
     * Update chat placeholder based on active tab
     * @param {string} tabId - Active tab ID
     */
    function updateChatPlaceholder(tabId) {
        const chatInput = document.getElementById('chat-input');
        if (!chatInput) return;
        
        if (tabId === 'budgetchat') {
            chatInput.placeholder = 'Ask about usage, costs, or budget settings. Type / for commands.';
        } else if (tabId === 'teamchat') {
            chatInput.placeholder = 'Send a message to the team about budget matters';
        } else {
            chatInput.placeholder = 'Switch to a chat tab to send messages';
        }
    }
    
    /**
     * Save component state to persistent storage
     */
    function saveComponentState() {
        stateManager.saveToStorage();
    }
    
    /**
     * Format message timestamp
     * @param {Date} timestamp - Message timestamp
     * @returns {string} Formatted time
     */
    function formatMessageTime(timestamp) {
        if (!(timestamp instanceof Date)) {
            timestamp = new Date(timestamp);
        }
        
        return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    /**
     * Format currency value
     * @param {number} value - Value to format
     * @returns {string} Formatted currency
     */
    function formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    }
    
    /**
     * Format token count with appropriate scaling
     * @param {number} count - Token count
     * @returns {string} Formatted token count
     */
    function formatTokens(count) {
        if (count >= 1000000) {
            return (count / 1000000).toFixed(1) + 'M';
        } else if (count >= 1000) {
            return (count / 1000).toFixed(1) + 'K';
        } else {
            return count.toString();
        }
    }
    
    /**
     * Generate mock trend data for development
     * @returns {Array} Mock trend data
     */
    function generateMockTrendData() {
        const data = [];
        const now = new Date();
        
        for (let i = 30; i >= 0; i--) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            
            // Generate some realistic-looking data
            const amount = Math.random() * 3 + 0.5; // Between $0.50 and $3.50
            
            data.push({
                date,
                amount,
                limit: 5.0
            });
        }
        
        return data;
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
        state: {}
    };
})();