/**
 * Budget Service
 * 
 * Service for managing budget data, including usage statistics, 
 * provider allocations, and settings. This service connects to the 
 * Hermes message bus for LLM cost tracking and maintains budget limits.
 */

class BudgetService {
    constructor() {
        this.apiUrl = '/api/budget'; // Budget API endpoint
        this.connected = false;
        this.hermesClient = null;
        
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
            console.log('[BUDGET] Registered budget service globally');
        } else {
            console.log('[BUDGET] Using existing global budget service');
        }
    }
    
    /**
     * Connect to the budget API
     */
    async connect() {
        console.log('[BUDGET] Connecting to budget service');
        
        if (this.connected) {
            return true;
        }
        
        try {
            // Connect to Hermes message bus if available
            if (window.hermesClient) {
                this.hermesClient = window.hermesClient;
                console.log('[BUDGET] Connected to Hermes message bus');
            }
            
            // Test connection with a basic request
            await this.getBudgetData();
            
            this.connected = true;
            console.log('[BUDGET] Successfully connected to budget service');
            return true;
        } catch (error) {
            console.error('[BUDGET] Failed to connect to budget service:', error);
            this.connected = false;
            
            // Create mock data
            console.log('[BUDGET] Using mock data');
            return true;
        }
    }
    
    /**
     * Disconnect from the budget API
     */
    disconnect() {
        console.log('[BUDGET] Disconnecting from budget service');
        this.connected = false;
    }
    
    /**
     * Get budget data
     * @param {string} period - Period to get data for (daily, weekly, monthly)
     */
    async getBudgetData(period = 'monthly') {
        console.log(`[BUDGET] Getting budget data for period: ${period}`);
        
        try {
            // Try to fetch from API if connected
            if (this.hermesClient) {
                const response = await fetch(`${this.apiUrl}?period=${period}`);
                
                if (response.ok) {
                    return await response.json();
                }
            }
            
            // Return mock data if API request fails or not connected
            return this._getMockBudgetData(period);
        } catch (error) {
            console.error('[BUDGET] Error getting budget data:', error);
            
            // Return mock data on error
            return this._getMockBudgetData(period);
        }
    }
    
    /**
     * Get usage details for a specific date range
     * @param {string} startDate - Start date (YYYY-MM-DD)
     * @param {string} endDate - End date (YYYY-MM-DD)
     */
    async getUsageDetails(startDate, endDate) {
        console.log(`[BUDGET] Getting usage details from ${startDate} to ${endDate}`);
        
        try {
            // Try to fetch from API if connected
            if (this.hermesClient) {
                const response = await fetch(`${this.apiUrl}/usage?start=${startDate}&end=${endDate}`);
                
                if (response.ok) {
                    return await response.json();
                }
            }
            
            // Return mock data if API request fails or not connected
            return this._getMockUsageDetails();
        } catch (error) {
            console.error('[BUDGET] Error getting usage details:', error);
            
            // Return mock data on error
            return this._getMockUsageDetails();
        }
    }
    
    /**
     * Save budget settings
     * @param {Object} settings - Budget settings
     */
    async saveBudgetSettings(settings) {
        console.log('[BUDGET] Saving budget settings:', settings);
        
        try {
            // Try to save to API if connected
            if (this.hermesClient) {
                const response = await fetch(`${this.apiUrl}/settings`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(settings)
                });
                
                if (response.ok) {
                    return await response.json();
                }
            }
            
            // Return mock response if API request fails or not connected
            return { success: true };
        } catch (error) {
            console.error('[BUDGET] Error saving budget settings:', error);
            throw error;
        }
    }
    
    /**
     * Save alert settings
     * @param {Object} settings - Alert settings
     */
    async saveAlertSettings(settings) {
        console.log('[BUDGET] Saving alert settings:', settings);
        
        try {
            // Try to save to API if connected
            if (this.hermesClient) {
                const response = await fetch(`${this.apiUrl}/alerts/settings`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(settings)
                });
                
                if (response.ok) {
                    return await response.json();
                }
            }
            
            // Return mock response if API request fails or not connected
            return { success: true };
        } catch (error) {
            console.error('[BUDGET] Error saving alert settings:', error);
            throw error;
        }
    }
    
    /**
     * Get mock budget data for development/testing
     */
    _getMockBudgetData(period) {
        // Return different mock data based on the period
        const currentDate = new Date();
        
        let mockData = {
            daily: {
                current: 2.47,
                limit: 5.00,
                percentage: 49.4,
                start_date: currentDate.toISOString(),
                end_date: currentDate.toISOString()
            },
            weekly: {
                current: 12.89,
                limit: 25.00,
                percentage: 51.6,
                start_date: new Date(currentDate.getTime() - 6 * 24 * 60 * 60 * 1000).toISOString(),
                end_date: currentDate.toISOString()
            },
            monthly: {
                current: 36.75,
                limit: 100.00,
                percentage: 36.8,
                start_date: new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).toISOString(),
                end_date: new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).toISOString()
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
        
        return mockData;
    }
    
    /**
     * Get mock usage details for development/testing
     */
    _getMockUsageDetails() {
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
                },
                {
                    timestamp: '2025-04-20T16:05:00Z',
                    component: 'Terma',
                    provider: 'Anthropic',
                    model: 'Claude 3 Sonnet',
                    task_type: 'chat',
                    input_tokens: 4530,
                    output_tokens: 4200,
                    cost: 0.13
                },
                {
                    timestamp: '2025-04-20T11:47:00Z',
                    component: 'Ergon',
                    provider: 'Anthropic',
                    model: 'Claude 3 Haiku',
                    task_type: 'workflow_planning',
                    input_tokens: 9200,
                    output_tokens: 6480,
                    cost: 0.02
                },
                {
                    timestamp: '2025-04-19T22:15:00Z',
                    component: 'Athena',
                    provider: 'OpenAI',
                    model: 'GPT-4',
                    task_type: 'data_analysis',
                    input_tokens: 2540,
                    output_tokens: 5080,
                    cost: 0.46
                }
            ],
            page: 1,
            total_pages: 14
        };
    }
}

// Create an instance if not already existing
if (!window.tektonUI?.services?.budgetService) {
    window.BudgetService = BudgetService;
    new BudgetService();
}