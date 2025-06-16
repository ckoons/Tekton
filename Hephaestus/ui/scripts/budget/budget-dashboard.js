/**
 * Budget Dashboard JavaScript
 * Controller for the Budget Dashboard UI component in Hephaestus
 * Updated to work with Shadow DOM isolation
 */

(function(component) {
  'use strict';
  
  // Budget Manager will be initialized with the shared service
  let budgetManager = null;
  
  /**
   * Initialize the Budget Dashboard component
   */
  function initBudgetDashboard() {
    setupTabNavigation();
    initBudgetService();
    setupEventListeners();
    initCharts();
    
    // Register cleanup function that will be called when the component is unmounted
    component.registerCleanup(function() {
      cleanupComponent();
    });
  }
  
  /**
   * Set up tab navigation for the Budget component
   */
  function setupTabNavigation() {
    const tabButtons = component.$$('.budget-tabs__button');
    const tabContents = component.$$('.budget-tabs__content');
    
    tabButtons.forEach(button => {
      button.addEventListener('click', () => {
        const tabName = button.getAttribute('data-tab');
        
        // Deactivate all tabs
        tabButtons.forEach(btn => btn.classList.remove('budget-tabs__button--active'));
        tabContents.forEach(content => content.classList.remove('budget-tabs__content--active'));
        
        // Activate selected tab
        button.classList.add('budget-tabs__button--active');
        component.$(`#${tabName}-content`).classList.add('budget-tabs__content--active');
      });
    });
  }
  
  /**
   * Initialize Budget Service
   * This is decoupled from RhetorClient for better component isolation
   */
  function initBudgetService() {
    // Create budget manager with the shared service
    budgetManager = new BudgetManager();
    
    // Connect to the service
    connectToBudgetService();
  }
  
  /**
   * Connect to the Budget service
   */
  async function connectToBudgetService() {
    try {
      await budgetManager.connect();
      fetchBudgetData();
    } catch (error) {
      console.error('Failed to connect to Budget service:', error);
      showConnectionError();
    }
  }
  
  /**
   * Show connection error message
   */
  function showConnectionError() {
    // Display error in dashboard
    const dashboardContent = component.$('#dashboard-content');
    
    if (dashboardContent) {
      const errorMsg = document.createElement('div');
      errorMsg.className = 'budget-connection-error';
      errorMsg.innerHTML = `
        <h3 class="budget-connection-error__title">Connection Error</h3>
        <p class="budget-connection-error__message">Failed to connect to Budget service. Budget data cannot be displayed.</p>
        <button class="budget-button" id="retry-connection">Retry Connection</button>
      `;
      
      // Add to top of dashboard
      dashboardContent.insertBefore(errorMsg, dashboardContent.firstChild);
      
      // Add retry event listener
      component.$('#retry-connection')?.addEventListener('click', () => {
        errorMsg.remove();
        connectToBudgetService();
      });
    }
  }
  
  /**
   * Set up event listeners for the dashboard
   */
  function setupEventListeners() {
    // Period selector
    component.on('change', '#period-select', function() {
      fetchBudgetData();
    });
    
    // Refresh button
    component.on('click', '#refresh-dashboard', function() {
      fetchBudgetData();
    });
    
    // Chart selectors
    component.on('change', '.budget-form__select', function() {
      updateCharts();
    });
    
    // Budget settings save button
    component.on('click', '#save-budget-settings', function() {
      saveBudgetSettings();
    });
    
    // Date filters in details tab
    component.on('click', '#filter-usage', function() {
      fetchUsageDetails();
    });
    
    // Clear alerts button
    component.on('click', '#clear-alerts', function() {
      clearAllAlerts();
    });
    
    // Save alert settings button
    component.on('click', '#save-alert-settings', function() {
      saveAlertSettings();
    });
    
    // Dismiss alert buttons
    component.on('click', '.budget-alert__actions button', function(event) {
      const alertItem = event.target.closest('.budget-alert');
      if (alertItem) {
        alertItem.remove();
      }
    });
  }
  
  /**
   * Initialize chart placeholders
   */
  function initCharts() {
    // In a real implementation, this would initialize Chart.js or another library
    // For the demo, we'll just update the placeholders
    
    const providerChart = component.$('#provider-pie-chart');
    const trendChart = component.$('#trend-chart');
    
    if (providerChart) {
      providerChart.innerHTML = 'Provider Distribution Chart<br>(Placeholder)';
    }
    
    if (trendChart) {
      trendChart.innerHTML = 'Daily Spend Trend Chart<br>(Placeholder)';
    }
  }
  
  /**
   * Update charts based on selected options
   */
  function updateCharts() {
    // In a real implementation, this would update the charts with new data
    console.log('Updating charts with new options');
  }
  
  /**
   * Fetch budget data from service
   */
  async function fetchBudgetData() {
    if (!budgetManager) return;
    
    // Show loading indication
    showLoading(true);
    
    try {
      const data = await budgetManager.fetchBudgetData();
      showLoading(false);
      
      // Update UI with the data
      if (data) {
        updateBudgetUI(data);
      }
    } catch (error) {
      console.error('Failed to fetch budget data:', error);
      showLoading(false);
      showNotification('Error', 'Failed to fetch budget data. Please try again.', 'error');
    }
  }
  
  /**
   * Fetch usage details for the selected date range
   */
  async function fetchUsageDetails() {
    if (!budgetManager) return;
    
    const startDate = component.$('#start-date')?.value;
    const endDate = component.$('#end-date')?.value;
    
    if (startDate && endDate) {
      showLoading(true);
      
      try {
        const data = await budgetManager.fetchUsageDetails(startDate, endDate);
        showLoading(false);
        
        // Update UI with the usage details
        if (data) {
          updateUsageDetailsUI(data);
        }
      } catch (error) {
        console.error('Failed to fetch usage details:', error);
        showLoading(false);
        showNotification('Error', 'Failed to fetch usage details. Please try again.', 'error');
      }
    }
  }
  
  /**
   * Save budget settings
   */
  async function saveBudgetSettings() {
    if (!budgetManager) return;
    
    // Get form values using scoped selectors
    const dailyLimit = component.$('#daily-limit')?.value;
    const weeklyLimit = component.$('#weekly-limit')?.value;
    const monthlyLimit = component.$('#monthly-limit')?.value;
    const enforcePolicy = component.$('#enforce-policy')?.value;
    
    const anthropicLimit = component.$('#anthropic-limit')?.value;
    const openaiLimit = component.$('#openai-limit')?.value;
    const enableProviderLimits = component.$('#enable-provider-limits')?.checked;
    
    const warningThreshold = component.$('#warning-threshold')?.value;
    const allowFreeModels = component.$('#allow-free-models')?.checked;
    const resetDay = component.$('#reset-day')?.value;
    
    const settings = {
      limits: {
        daily: parseFloat(dailyLimit),
        weekly: parseFloat(weeklyLimit),
        monthly: parseFloat(monthlyLimit)
      },
      enforcement_policy: enforcePolicy,
      provider_limits: {
        enabled: enableProviderLimits,
        anthropic: parseFloat(anthropicLimit),
        openai: parseFloat(openaiLimit)
      },
      warning_threshold: parseInt(warningThreshold, 10),
      allow_free_models: allowFreeModels,
      reset_day: resetDay
    };
    
    showLoading(true);
    
    try {
      await budgetManager.saveBudgetSettings(settings);
      showLoading(false);
      showNotification('Success', 'Budget settings saved successfully.', 'success');
    } catch (error) {
      console.error('Failed to save budget settings:', error);
      showLoading(false);
      showNotification('Error', 'Failed to save budget settings: ' + error.message, 'error');
    }
  }
  
  /**
   * Clear all alerts
   */
  function clearAllAlerts() {
    const alertList = component.$('.budget-alert-list');
    
    if (alertList) {
      alertList.innerHTML = '';
      showNotification('Success', 'All alerts cleared.', 'success');
    }
  }
  
  /**
   * Save alert settings
   */
  async function saveAlertSettings() {
    if (!budgetManager) return;
    
    const enableEmailAlerts = component.$('#enable-email-alerts')?.checked;
    const alertEmail = component.$('#alert-email')?.value;
    const alertFrequency = component.$('#alert-frequency')?.value;
    
    const settings = {
      email_alerts: {
        enabled: enableEmailAlerts,
        email: alertEmail,
        frequency: alertFrequency
      }
    };
    
    showLoading(true);
    
    try {
      await budgetManager.saveAlertSettings(settings);
      showLoading(false);
      showNotification('Success', 'Alert settings saved successfully.', 'success');
    } catch (error) {
      console.error('Failed to save alert settings:', error);
      showLoading(false);
      showNotification('Error', 'Failed to save alert settings: ' + error.message, 'error');
    }
  }
  
  /**
   * Update the budget UI with fetched data
   */
  function updateBudgetUI(data) {
    if (!data) return;
    
    // Update budget summary cards
    updateBudgetSummary(data);
    
    // Update charts
    updateChartsData(data);
    
    // Update top usage table
    updateTopUsage(data);
  }
  
  /**
   * Update budget summary cards
   */
  function updateBudgetSummary(data) {
    const { daily, weekly, monthly, tokens } = data || {};
    
    // Update daily card
    if (daily) {
      updateBudgetCard('Daily Spend', 'Today', daily.current, daily.limit, daily.percentage);
    }
    
    // Update weekly card
    if (weekly) {
      const weekRange = formatDateRange(weekly.start_date, weekly.end_date);
      updateBudgetCard('Weekly Spend', 'This Week', weekly.current, weekly.limit, weekly.percentage, weekRange);
    }
    
    // Update monthly card
    if (monthly) {
      const monthName = new Date().toLocaleString('default', { month: 'long' });
      const year = new Date().getFullYear();
      const monthRange = formatDateRange(monthly.start_date, monthly.end_date);
      updateBudgetCard('Monthly Spend', `${monthName} ${year}`, monthly.current, monthly.limit, monthly.percentage, monthRange);
    }
    
    // Update token usage card
    if (tokens) {
      const summaryCards = component.$$('.budget-card');
      const tokenCard = summaryCards[3]; // Fourth card
      
      if (tokenCard) {
        const amountElem = tokenCard.querySelector('.budget-card__amount');
        const footerElem = tokenCard.querySelector('.budget-card__footer');
        
        if (amountElem) {
          amountElem.textContent = formatTokens(tokens.total);
        }
        
        if (footerElem) {
          footerElem.innerHTML = `
            <div>Input: ${formatTokens(tokens.input)}</div>
            <div>Output: ${formatTokens(tokens.output)}</div>
          `;
        }
      }
    }
  }
  
  /**
   * Update a specific budget card
   */
  function updateBudgetCard(title, period, current, limit, percentage, dateRange = null) {
    const summaryCards = component.$$('.budget-card');
    let targetCard = null;
    
    for (const card of summaryCards) {
      const titleElem = card.querySelector('.budget-card__title');
      if (titleElem && titleElem.textContent === title) {
        targetCard = card;
        break;
      }
    }
    
    if (!targetCard) return;
    
    const periodElem = targetCard.querySelector('.budget-card__period');
    const amountElem = targetCard.querySelector('.budget-card__amount');
    const limitElem = targetCard.querySelector('.budget-card__limit');
    const progressBar = targetCard.querySelector('.budget-card__progress-bar');
    const footerElem = targetCard.querySelector('.budget-card__footer');
    
    if (periodElem) periodElem.textContent = period;
    if (amountElem) amountElem.textContent = `$${current.toFixed(2)}`;
    if (limitElem) limitElem.textContent = `/ $${limit.toFixed(2)}`;
    
    if (progressBar) {
      progressBar.style.width = `${percentage}%`;
      
      // Add warning/danger classes
      progressBar.classList.remove('budget-card__progress-bar--warning', 'budget-card__progress-bar--danger');
      if (percentage >= 90) {
        progressBar.classList.add('budget-card__progress-bar--danger');
      } else if (percentage >= 70) {
        progressBar.classList.add('budget-card__progress-bar--warning');
      }
    }
    
    if (footerElem) {
      footerElem.innerHTML = `
        <div>${percentage.toFixed(1)}% of ${title.toLowerCase()} limit</div>
        ${dateRange ? `<div>${dateRange}</div>` : ''}
      `;
    }
  }
  
  /**
   * Update charts with budget data
   */
  function updateChartsData(data) {
    // In a real implementation, this would update Chart.js or another charting library
    // For the demo, we'll just update the legends
    
    if (!data || !data.breakdown) return;
    
    const { by_provider } = data.breakdown;
    
    if (by_provider) {
      const legend = component.$('.budget-chart-card__legend');
      
      if (legend) {
        const legendHTML = Object.entries(by_provider).map(([provider, amount]) => {
          const colorStyle = getProviderColor(provider);
          return `
            <div class="budget-legend-item">
              <span class="budget-legend-item__color" style="background-color: ${colorStyle};"></span>
              <span class="budget-legend-item__label">${provider}: $${amount.toFixed(2)}</span>
            </div>
          `;
        }).join('');
        
        legend.innerHTML = legendHTML;
      }
    }
  }
  
  /**
   * Update top usage table
   */
  function updateTopUsage(data) {
    if (!data || !data.top_usage) return;
    
    const { by_model } = data.top_usage;
    
    if (by_model) {
      const tableBody = component.$('.budget-table tbody');
      
      if (tableBody) {
        const totalCost = by_model.reduce((sum, item) => sum + item.cost, 0);
        
        const rowsHTML = by_model.map(item => {
          const percentage = (item.cost / totalCost * 100).toFixed(1);
          return `
            <tr>
              <td>${item.model}</td>
              <td><span class="budget-badge budget-badge--${item.provider.toLowerCase()}">${item.provider}</span></td>
              <td>${formatTokens(item.tokens)}</td>
              <td>$${item.cost.toFixed(2)}</td>
              <td>${percentage}%</td>
            </tr>
          `;
        }).join('');
        
        tableBody.innerHTML = rowsHTML;
      }
    }
  }
  
  /**
   * Update usage details table
   */
  function updateUsageDetailsUI(data) {
    if (!data) return;
    
    const tableBody = component.$('#details-content .budget-table tbody');
    
    if (tableBody && data.items) {
      const rowsHTML = data.items.map(item => {
        const timestamp = new Date(item.timestamp).toLocaleString();
        const tokensFormatted = formatTokens(item.input_tokens + item.output_tokens);
        
        return `
          <tr>
            <td>${timestamp}</td>
            <td>${item.component}</td>
            <td><span class="budget-badge budget-badge--${item.provider.toLowerCase()}">${item.model}</span></td>
            <td>${item.task_type}</td>
            <td>${tokensFormatted}</td>
            <td>$${item.cost.toFixed(2)}</td>
          </tr>
        `;
      }).join('');
      
      tableBody.innerHTML = rowsHTML;
      
      // Update pagination
      const pagination = component.$('.budget-pagination');
      if (pagination) {
        const span = pagination.querySelector('.budget-pagination__indicator');
        if (span) {
          span.textContent = `Page ${data.page} of ${data.total_pages}`;
        }
      }
    }
  }
  
  /**
   * Format tokens for display (e.g., 1.2M, 542K)
   */
  function formatTokens(tokens) {
    if (tokens >= 1000000) {
      return `${(tokens / 1000000).toFixed(1)}M`;
    } else if (tokens >= 1000) {
      return `${(tokens / 1000).toFixed(0)}K`;
    } else {
      return tokens.toString();
    }
  }
  
  /**
   * Format date range for display
   */
  function formatDateRange(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    const format = (date) => {
      return `${date.getMonth() + 1}/${date.getDate()}`;
    };
    
    return `${format(start)} - ${format(end)}`;
  }
  
  /**
   * Get color for provider
   */
  function getProviderColor(provider) {
    const colors = {
      anthropic: '#7356BF',
      openai: '#10A283',
      ollama: '#FF6600',
      default: '#AAAAAA'
    };
    
    return colors[provider.toLowerCase()] || colors.default;
  }
  
  /**
   * Show loading indicator
   */
  function showLoading(isLoading) {
    const loadingElement = component.$('.budget-loading');
    
    if (isLoading) {
      if (!loadingElement) {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'budget-loading';
        loadingDiv.innerHTML = `
          <div class="budget-loading__spinner"></div>
          <div class="budget-loading__message">Loading...</div>
        `;
        
        // Append to container
        component.root.appendChild(loadingDiv);
      }
    } else if (loadingElement) {
      loadingElement.remove();
    }
  }
  
  /**
   * Show notification
   */
  function showNotification(title, message, type = 'info') {
    // Remove existing notifications
    const existingNotification = component.$('.budget-notification');
    if (existingNotification) {
      existingNotification.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `budget-notification budget-notification--${type}`;
    notification.innerHTML = `
      <button class="budget-notification__close">&times;</button>
      <h4 class="budget-notification__title">${title}</h4>
      <p class="budget-notification__message">${message}</p>
    `;
    
    // Append to shadow DOM
    component.root.appendChild(notification);
    
    // Show notification with a small delay for animation
    setTimeout(() => {
      notification.classList.add('budget-notification--visible');
    }, 10);
    
    // Add close button functionality
    notification.querySelector('.budget-notification__close').addEventListener('click', () => {
      notification.classList.remove('budget-notification--visible');
      setTimeout(() => {
        notification.remove();
      }, 300);
    });
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.classList.remove('budget-notification--visible');
        setTimeout(() => {
          if (notification.parentNode) {
            notification.remove();
          }
        }, 300);
      }
    }, 5000);
  }
  
  /**
   * Clean up component resources
   */
  function cleanupComponent() {
    // Disconnect from service if needed
    if (budgetManager) {
      budgetManager.disconnect();
    }
    
    // Remove event listeners (handled by component unloading)
    console.log('Budget component cleaned up');
  }
  
  /**
   * Budget Manager class
   * Decoupled from RhetorClient for better component isolation
   */
  class BudgetManager {
    constructor() {
      this.connected = false;
      this.budgetData = null;
      this.usageDetails = null;
      
      // Attempt to get the shared budget service
      this.budgetService = window.tektonUI?.services?.budgetService || this._createFallbackService();
    }
    
    /**
     * Connect to the budget service
     */
    async connect() {
      if (this.connected) return true;
      
      try {
        // Try to connect through the service
        await this.budgetService.connect();
        this.connected = true;
        return true;
      } catch (error) {
        console.error('Failed to connect to budget service:', error);
        this.connected = false;
        throw error;
      }
    }
    
    /**
     * Disconnect from the budget service
     */
    disconnect() {
      if (!this.connected) return;
      
      try {
        this.budgetService.disconnect();
      } catch (error) {
        console.error('Error disconnecting from budget service:', error);
      } finally {
        this.connected = false;
      }
    }
    
    /**
     * Fetch budget data
     */
    async fetchBudgetData() {
      if (!this.connected) {
        await this.connect();
      }
      
      const period = component.$('#period-select')?.value || 'monthly';
      
      try {
        const data = await this.budgetService.getBudgetData(period);
        this.budgetData = data;
        return data;
      } catch (error) {
        console.error('Failed to fetch budget data:', error);
        throw error;
      }
    }
    
    /**
     * Fetch usage details for a date range
     */
    async fetchUsageDetails(startDate, endDate) {
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const data = await this.budgetService.getUsageDetails(startDate, endDate);
        this.usageDetails = data;
        return data;
      } catch (error) {
        console.error('Failed to fetch usage details:', error);
        throw error;
      }
    }
    
    /**
     * Save budget settings
     */
    async saveBudgetSettings(settings) {
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const result = await this.budgetService.saveBudgetSettings(settings);
        return result;
      } catch (error) {
        console.error('Failed to save budget settings:', error);
        throw error;
      }
    }
    
    /**
     * Save alert settings
     */
    async saveAlertSettings(settings) {
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const result = await this.budgetService.saveAlertSettings(settings);
        return result;
      } catch (error) {
        console.error('Failed to save alert settings:', error);
        throw error;
      }
    }
    
    /**
     * Create a fallback service when the global service is not available
     * This provides a way to fetch mock data for development/testing
     */
    _createFallbackService() {
      console.warn('Using fallback Budget service - functionality will be limited');
      
      return {
        connect: async function() {
          return Promise.resolve(true);
        },
        
        disconnect: function() {
          // No-op
        },
        
        getBudgetData: async function(period) {
          console.log(`Mock: Fetching budget data for period ${period}`);
          
          // Return mock data for development
          return {
            daily: {
              current: 2.47,
              limit: 5.00,
              percentage: 49.4,
              start_date: new Date().toISOString(),
              end_date: new Date().toISOString()
            },
            weekly: {
              current: 12.89,
              limit: 25.00,
              percentage: 51.6,
              start_date: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
              end_date: new Date().toISOString()
            },
            monthly: {
              current: 36.75,
              limit: 100.00,
              percentage: 36.8,
              start_date: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString(),
              end_date: new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).toISOString()
            },
            tokens: {
              total: 1200000,
              input: 542000,
              output: 658000
            },
            breakdown: {
              by_provider: {
                'Anthropic': 27.50,
                'OpenAI': 9.25,
                'Ollama': 0.00
              }
            },
            top_usage: {
              by_model: [
                {
                  model: 'Claude 3 Sonnet',
                  provider: 'Anthropic',
                  tokens: 230450,
                  cost: 3.46
                },
                {
                  model: 'Claude 3 Haiku',
                  provider: 'Anthropic',
                  tokens: 543120,
                  cost: 0.68
                },
                {
                  model: 'GPT-4',
                  provider: 'OpenAI',
                  tokens: 104300,
                  cost: 6.26
                },
                {
                  model: 'Llama 3',
                  provider: 'Ollama',
                  tokens: 1250680,
                  cost: 0.00
                }
              ]
            }
          };
        },
        
        getUsageDetails: async function(startDate, endDate) {
          console.log(`Mock: Fetching usage details from ${startDate} to ${endDate}`);
          
          // Return mock data for development
          return {
            items: [
              {
                timestamp: '2025-04-21T15:42:00Z',
                component: 'Terma',
                provider: 'Anthropic',
                model: 'Claude 3 Sonnet',
                task_type: 'chat',
                input_tokens: 1500,
                output_tokens: 2820,
                cost: 0.06
              },
              {
                timestamp: '2025-04-21T14:15:00Z',
                component: 'Ergon',
                provider: 'Anthropic',
                model: 'Claude 3 Haiku',
                task_type: 'agent_creation',
                input_tokens: 8000,
                output_tokens: 4450,
                cost: 0.02
              },
              {
                timestamp: '2025-04-21T10:33:00Z',
                component: 'Athena',
                provider: 'OpenAI',
                model: 'GPT-4',
                task_type: 'knowledge_retrieval',
                input_tokens: 1200,
                output_tokens: 2080,
                cost: 0.19
              },
              {
                timestamp: '2025-04-20T18:22:00Z',
                component: 'Codex',
                provider: 'Ollama',
                model: 'Llama 3',
                task_type: 'code_completion',
                input_tokens: 12000,
                output_tokens: 33320,
                cost: 0.00
              }
            ],
            page: 1,
            total_pages: 14
          };
        },
        
        saveBudgetSettings: async function(settings) {
          console.log('Mock: Saving budget settings', settings);
          return { success: true };
        },
        
        saveAlertSettings: async function(settings) {
          console.log('Mock: Saving alert settings', settings);
          return { success: true };
        }
      };
    }
  }
  
  /**
   * Shared BudgetService for use across components
   * This should be registered in the global scope for other components to use
   */
  class BudgetService {
    constructor() {
      const budgetPort = window.BUDGET_PORT || 8013;
      this.apiUrl = `http://localhost:${budgetPort}/budget`; // Dedicated Budget API endpoint
      this.connected = false;
      
      // Register service globally
      if (!window.tektonUI) {
        window.tektonUI = {};
      }
      
      if (!window.tektonUI.services) {
        window.tektonUI.services = {};
      }
      
      // Only register if not already registered
      if (!window.tektonUI.services.budgetService) {
        window.tektonUI.services.budgetService = this;
      }
    }
    
    /**
     * Connect to the Budget API
     */
    async connect() {
      if (this.connected) return true;
      
      try {
        // Test connection with a simple ping
        const response = await fetch(`${this.apiUrl}/ping`);
        
        if (!response.ok) {
          throw new Error(`Failed to connect to Budget API: ${response.status} ${response.statusText}`);
        }
        
        this.connected = true;
        return true;
      } catch (error) {
        console.error('Failed to connect to Budget API:', error);
        this.connected = false;
        throw error;
      }
    }
    
    /**
     * Disconnect from the Budget API
     */
    disconnect() {
      this.connected = false;
    }
    
    /**
     * Get budget data for a specific period
     */
    async getBudgetData(period = 'monthly') {
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}?period=${period}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch budget data: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error('Failed to fetch budget data:', error);
        throw error;
      }
    }
    
    /**
     * Get usage details for a specific date range
     */
    async getUsageDetails(startDate, endDate) {
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/usage?start=${startDate}&end=${endDate}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch usage details: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error('Failed to fetch usage details:', error);
        throw error;
      }
    }
    
    /**
     * Save budget settings
     */
    async saveBudgetSettings(settings) {
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/settings`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(settings)
        });
        
        if (!response.ok) {
          throw new Error(`Failed to save budget settings: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error('Failed to save budget settings:', error);
        throw error;
      }
    }
    
    /**
     * Save alert settings
     */
    async saveAlertSettings(settings) {
      if (!this.connected) {
        await this.connect();
      }
      
      try {
        const response = await fetch(`${this.apiUrl}/alerts/settings`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(settings)
        });
        
        if (!response.ok) {
          throw new Error(`Failed to save alert settings: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error('Failed to save alert settings:', error);
        throw error;
      }
    }
  }
  
  // Register the service globally (will only register if not already present)
  new BudgetService();
  
  // Initialize the component when the Shadow DOM is ready
  initBudgetDashboard();
  
})(component);