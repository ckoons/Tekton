/**
 * Budget Data Models
 * 
 * Defines data models and validation functions for the Budget component
 * Part of the Budget UI Update Sprint implementation
 */

/**
 * Budget period types
 * @enum {string}
 */
const BudgetPeriod = {
    HOURLY: 'hourly',
    DAILY: 'daily',
    WEEKLY: 'weekly',
    MONTHLY: 'monthly'
};

/**
 * Budget tier types
 * @enum {string}
 */
const BudgetTier = {
    LOCAL_LIGHTWEIGHT: 'local_lightweight',
    LOCAL_MIDWEIGHT: 'local_midweight',
    REMOTE_HEAVYWEIGHT: 'remote_heavyweight'
};

/**
 * Budget policy types
 * @enum {string}
 */
const BudgetPolicyType = {
    WARNING: 'warning',
    HARD_LIMIT: 'hard_limit',
    DOWNGRADE: 'downgrade'
};

/**
 * Task priority levels
 * @enum {number}
 */
const TaskPriority = {
    LOW: 1,
    MEDIUM: 5,
    HIGH: 10
};

/**
 * Model for Budget Dashboard data
 */
class DashboardData {
    constructor(data = {}) {
        this.dailySpend = data.dailySpend || { amount: 0, limit: 0, percentage: 0, period: '' };
        this.weeklySpend = data.weeklySpend || { amount: 0, limit: 0, percentage: 0, period: '' };
        this.monthlySpend = data.monthlySpend || { amount: 0, limit: 0, percentage: 0, period: '' };
        this.tokenUsage = data.tokenUsage || { amount: 0, input: 0, output: 0, period: '' };
        this.spendByProvider = data.spendByProvider || [];
        this.spendTrend = data.spendTrend || [];
        this.topUsage = data.topUsage || [];
    }
    
    /**
     * Update dashboard with summary data from API
     * @param {Array} summaries - Budget summaries from API
     * @returns {DashboardData} Updated dashboard data
     */
    updateFromSummaries(summaries) {
        if (!summaries || !Array.isArray(summaries)) return this;
        
        // Process each summary based on period
        for (const summary of summaries) {
            if (!summary) continue;
            
            const period = summary.period;
            
            if (period === BudgetPeriod.DAILY) {
                this.dailySpend = {
                    amount: summary.total_cost || 0,
                    limit: summary.cost_limit || 0,
                    percentage: summary.cost_usage_percentage || 0,
                    period: new Date().toLocaleDateString()
                };
            } else if (period === BudgetPeriod.WEEKLY) {
                // Calculate week start and end dates
                const now = new Date();
                const dayOfWeek = now.getDay();
                const weekStart = new Date(now);
                weekStart.setDate(now.getDate() - dayOfWeek);
                const weekEnd = new Date(weekStart);
                weekEnd.setDate(weekStart.getDate() + 6);
                
                this.weeklySpend = {
                    amount: summary.total_cost || 0,
                    limit: summary.cost_limit || 0,
                    percentage: summary.cost_usage_percentage || 0,
                    period: `${weekStart.toLocaleDateString()} - ${weekEnd.toLocaleDateString()}`
                };
            } else if (period === BudgetPeriod.MONTHLY) {
                // Get month name
                const now = new Date();
                const monthName = now.toLocaleString('default', { month: 'long' });
                const year = now.getFullYear();
                
                this.monthlySpend = {
                    amount: summary.total_cost || 0,
                    limit: summary.cost_limit || 0,
                    percentage: summary.cost_usage_percentage || 0,
                    period: `${monthName} ${year}`
                };
            }
            
            // Update token usage from daily summary if available
            if (period === BudgetPeriod.DAILY) {
                this.tokenUsage = {
                    amount: summary.total_tokens_used || 0,
                    input: summary.input_tokens || 0,
                    output: summary.output_tokens || 0,
                    period: 'Last 24 Hours'
                };
            }
        }
        
        return this;
    }
    
    /**
     * Update provider distribution from API data
     * @param {Array} providerData - Provider distribution data
     * @returns {DashboardData} Updated dashboard data
     */
    updateProviderDistribution(providerData) {
        if (!providerData || !Array.isArray(providerData)) return this;
        
        this.spendByProvider = providerData.map(item => ({
            provider: item.provider,
            amount: item.cost || 0,
            percentage: item.percentage || 0,
            color: getProviderColor(item.provider)
        }));
        
        return this;
    }
    
    /**
     * Update spend trend from API data
     * @param {Array} trendData - Spend trend data
     * @returns {DashboardData} Updated dashboard data
     */
    updateSpendTrend(trendData) {
        if (!trendData || !Array.isArray(trendData)) return this;
        
        this.spendTrend = trendData.map(item => ({
            date: new Date(item.date),
            amount: item.cost || 0,
            limit: item.limit || 0
        }));
        
        return this;
    }
    
    /**
     * Update top usage from API data
     * @param {Array} usageData - Top usage data
     * @returns {DashboardData} Updated dashboard data
     */
    updateTopUsage(usageData) {
        if (!usageData || !Array.isArray(usageData)) return this;
        
        this.topUsage = usageData.map(item => ({
            name: item.model || item.component || '',
            provider: item.provider || '',
            tokens: item.tokens || 0,
            cost: item.cost || 0,
            percentage: item.percentage || 0
        }));
        
        return this;
    }
}

/**
 * Model for Usage Details data
 */
class UsageData {
    constructor(data = {}) {
        this.records = data.records || [];
        this.totalRecords = data.totalRecords || 0;
        this.currentPage = data.currentPage || 1;
        this.totalPages = data.totalPages || 1;
        this.filters = data.filters || {};
    }
    
    /**
     * Update usage data from API response
     * @param {Object} response - API response
     * @returns {UsageData} Updated usage data
     */
    updateFromApiResponse(response) {
        if (!response) return this;
        
        this.records = (response.items || []).map(item => ({
            id: item.record_id,
            timestamp: new Date(item.timestamp),
            component: item.component || '',
            provider: item.provider || '',
            model: item.model || '',
            taskType: item.task_type || '',
            inputTokens: item.input_tokens || 0,
            outputTokens: item.output_tokens || 0,
            totalTokens: (item.input_tokens || 0) + (item.output_tokens || 0),
            cost: item.cost || 0
        }));
        
        this.totalRecords = response.total || 0;
        this.currentPage = response.page || 1;
        this.totalPages = Math.ceil(this.totalRecords / (response.limit || 1));
        
        return this;
    }
    
    /**
     * Set filters for usage data
     * @param {Object} filters - Filter parameters
     * @returns {UsageData} Updated usage data
     */
    setFilters(filters) {
        this.filters = { ...filters };
        return this;
    }
}

/**
 * Model for Budget Settings data
 */
class SettingsData {
    constructor(data = {}) {
        this.budgets = data.budgets || [];
        this.policies = data.policies || [];
        this.providers = data.providers || [];
        this.currentBudget = data.currentBudget || null;
    }
    
    /**
     * Update settings from budgets API response
     * @param {Object} budgetsResponse - Budgets API response
     * @returns {SettingsData} Updated settings data
     */
    updateFromBudgetsResponse(budgetsResponse) {
        if (!budgetsResponse) return this;
        
        this.budgets = (budgetsResponse.items || []).map(item => ({
            id: item.budget_id,
            name: item.name,
            description: item.description,
            isActive: item.is_active
        }));
        
        // Set current budget to first active budget or first budget
        if (this.budgets.length > 0) {
            const activeBudget = this.budgets.find(b => b.isActive);
            this.currentBudget = activeBudget || this.budgets[0];
        }
        
        return this;
    }
    
    /**
     * Update settings from policies API response
     * @param {Object} policiesResponse - Policies API response
     * @returns {SettingsData} Updated settings data
     */
    updateFromPoliciesResponse(policiesResponse) {
        if (!policiesResponse) return this;
        
        this.policies = (policiesResponse.items || []).map(item => ({
            id: item.policy_id,
            budgetId: item.budget_id,
            type: item.type,
            period: item.period,
            tokenLimit: item.token_limit,
            costLimit: item.cost_limit,
            warningThreshold: item.warning_threshold,
            actionThreshold: item.action_threshold,
            enabled: item.enabled,
            tier: item.tier,
            provider: item.provider,
            component: item.component,
            taskType: item.task_type
        }));
        
        return this;
    }
    
    /**
     * Update provider data
     * @param {Array} providers - Provider data
     * @returns {SettingsData} Updated settings data
     */
    updateProviders(providers) {
        if (!providers || !Array.isArray(providers)) return this;
        
        this.providers = providers.map(item => ({
            name: item.provider,
            models: item.models || [],
            monthlyBudget: item.monthly_budget || 0,
            enabled: item.enabled !== false
        }));
        
        return this;
    }
    
    /**
     * Get daily budget limit
     * @returns {number} Daily budget limit
     */
    getDailyBudgetLimit() {
        const policy = this.policies.find(p => 
            p.period === BudgetPeriod.DAILY && 
            p.type === BudgetPolicyType.HARD_LIMIT &&
            !p.provider && !p.tier
        );
        
        return policy ? policy.costLimit : 0;
    }
    
    /**
     * Get weekly budget limit
     * @returns {number} Weekly budget limit
     */
    getWeeklyBudgetLimit() {
        const policy = this.policies.find(p => 
            p.period === BudgetPeriod.WEEKLY && 
            p.type === BudgetPolicyType.HARD_LIMIT &&
            !p.provider && !p.tier
        );
        
        return policy ? policy.costLimit : 0;
    }
    
    /**
     * Get monthly budget limit
     * @returns {number} Monthly budget limit
     */
    getMonthlyBudgetLimit() {
        const policy = this.policies.find(p => 
            p.period === BudgetPeriod.MONTHLY && 
            p.type === BudgetPolicyType.HARD_LIMIT &&
            !p.provider && !p.tier
        );
        
        return policy ? policy.costLimit : 0;
    }
    
    /**
     * Get warning threshold
     * @returns {number} Warning threshold (percentage)
     */
    getWarningThreshold() {
        const policy = this.policies.find(p => 
            p.type === BudgetPolicyType.WARNING
        );
        
        return policy ? policy.warningThreshold : 80;
    }
    
    /**
     * Get enforcement policy
     * @returns {string} Enforcement policy
     */
    getEnforcementPolicy() {
        // Check if downgrade policy is enabled
        const downgradeEnabled = this.policies.find(p => 
            p.type === BudgetPolicyType.DOWNGRADE && 
            p.enabled
        );
        
        if (downgradeEnabled) return 'enforce';
        
        // Check if warning policy is enabled
        const warningEnabled = this.policies.find(p => 
            p.type === BudgetPolicyType.WARNING && 
            p.enabled
        );
        
        if (warningEnabled) return 'warn';
        
        // Otherwise, no enforcement
        return 'ignore';
    }
    
    /**
     * Get provider budget
     * @param {string} provider - Provider name
     * @returns {number} Provider budget
     */
    getProviderBudget(provider) {
        const providerData = this.providers.find(p => p.name === provider);
        return providerData ? providerData.monthlyBudget : 0;
    }
    
    /**
     * Check if provider-specific limits are enabled
     * @returns {boolean} True if provider limits are enabled
     */
    isProviderLimitsEnabled() {
        return this.policies.some(p => 
            p.provider && 
            p.enabled && 
            p.type === BudgetPolicyType.HARD_LIMIT
        );
    }
    
    /**
     * Check if free models are allowed when budget is depleted
     * @returns {boolean} True if free models are allowed
     */
    isFreeModelsAllowed() {
        return this.policies.some(p => 
            p.type === BudgetPolicyType.DOWNGRADE && 
            p.enabled
        );
    }
    
    /**
     * Get budget reset day
     * @returns {string} Reset day setting
     */
    getResetDay() {
        // This would typically be a setting stored in the budget
        // We'll return a default for now
        return '1';
    }
}

/**
 * Model for Alert data
 */
class AlertsData {
    constructor(data = {}) {
        this.alerts = data.alerts || [];
        this.totalAlerts = data.totalAlerts || 0;
        this.currentPage = data.currentPage || 1;
        this.totalPages = data.totalPages || 1;
        this.emailAlerts = data.emailAlerts !== false;
        this.emailAddress = data.emailAddress || '';
        this.alertFrequency = data.alertFrequency || 'daily';
    }
    
    /**
     * Update alerts from API response
     * @param {Object} response - API response
     * @returns {AlertsData} Updated alerts data
     */
    updateFromApiResponse(response) {
        if (!response) return this;
        
        this.alerts = (response.items || []).map(item => ({
            id: item.alert_id,
            title: item.title || '',
            description: item.message || '',
            severity: item.severity || 'info',
            timestamp: new Date(item.timestamp),
            acknowledged: item.acknowledged || false,
            budgetId: item.budget_id,
            type: item.type || 'budget'
        }));
        
        this.totalAlerts = response.total || 0;
        this.currentPage = response.page || 1;
        this.totalPages = Math.ceil(this.totalAlerts / (response.limit || 1));
        
        return this;
    }
    
    /**
     * Update alert settings
     * @param {Object} settings - Alert settings
     * @returns {AlertsData} Updated alerts data
     */
    updateSettings(settings) {
        if (!settings) return this;
        
        this.emailAlerts = settings.emailAlerts !== false;
        this.emailAddress = settings.emailAddress || '';
        this.alertFrequency = settings.alertFrequency || 'daily';
        
        return this;
    }
}

/**
 * Model for Chat data
 */
class ChatData {
    constructor(data = {}) {
        this.messages = data.messages || [];
        this.chatType = data.chatType || 'budgetchat';
    }
    
    /**
     * Add a user message
     * @param {string} text - Message text
     * @returns {ChatData} Updated chat data
     */
    addUserMessage(text) {
        this.messages.push({
            id: Date.now().toString(),
            type: 'user',
            text,
            timestamp: new Date()
        });
        
        return this;
    }
    
    /**
     * Add an CI message
     * @param {string} text - Message text
     * @returns {ChatData} Updated chat data
     */
    addAiMessage(text) {
        this.messages.push({
            id: Date.now().toString(),
            type: 'ai',
            text,
            timestamp: new Date()
        });
        
        return this;
    }
    
    /**
     * Add a system message
     * @param {string} text - Message text
     * @returns {ChatData} Updated chat data
     */
    addSystemMessage(text) {
        this.messages.push({
            id: Date.now().toString(),
            type: 'system',
            text,
            timestamp: new Date()
        });
        
        return this;
    }
    
    /**
     * Clear all messages except for system messages
     * @returns {ChatData} Updated chat data
     */
    clear() {
        this.messages = this.messages.filter(m => m.type === 'system');
        return this;
    }
}

/**
 * Helper function to get provider color
 * @param {string} provider - Provider name
 * @returns {string} Provider color
 */
function getProviderColor(provider) {
    if (!provider) return '#999999';
    
    const providerLower = provider.toLowerCase();
    
    switch (providerLower) {
        case 'anthropic':
            return '#7356BF';
        case 'openai':
            return '#10A283';
        case 'ollama':
            return '#FF6600';
        case 'mistral':
            return '#4A4DB9';
        case 'cohere':
            return '#FF6A95';
        case 'google':
        case 'gemini':
            return '#4285F4';
        case 'local':
            return '#34A853';
        default:
            return '#999999';
    }
}

// Export models as global objects
window.BudgetModels = {
    BudgetPeriod,
    BudgetTier,
    BudgetPolicyType,
    TaskPriority,
    DashboardData,
    UsageData,
    SettingsData,
    AlertsData,
    ChatData,
    getProviderColor
};