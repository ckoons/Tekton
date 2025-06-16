/**
 * Budget CLI Command Handler
 * 
 * Parses and processes CLI commands in the chat interface
 * Part of the Budget UI Update Sprint implementation
 */
class BudgetCliHandler {
    /**
     * Create a new CLI command handler instance
     * @param {BudgetApiClient} apiClient - API client for backend commands
     * @param {BudgetStateManager} stateManager - State manager
     */
    constructor(apiClient, stateManager) {
        this.apiClient = apiClient;
        this.stateManager = stateManager;
        this.commandPrefix = '/';
        this.availableCommands = this._initCommands();
    }
    
    /**
     * Initialize available commands
     * @returns {Object} Command definitions
     */
    _initCommands() {
        return {
            // General commands
            'help': {
                description: 'Show available commands or get help for a specific command',
                usage: '/help [command]',
                params: [
                    { name: 'command', optional: true, description: 'Command name to get help for' }
                ],
                execute: async (params) => this._executeHelpCommand(params)
            },
            
            // Budget commands
            'budget': {
                description: 'Show budget summary or get details for a specific period',
                usage: '/budget [period]',
                params: [
                    { name: 'period', optional: true, description: 'Budget period (daily, weekly, monthly)' }
                ],
                execute: async (params) => this._executeBudgetCommand(params)
            },
            'limits': {
                description: 'Show budget limits or set a new budget limit',
                usage: '/limits [period] [amount]',
                params: [
                    { name: 'period', optional: true, description: 'Budget period (daily, weekly, monthly)' },
                    { name: 'amount', optional: true, description: 'New budget limit amount' }
                ],
                execute: async (params) => this._executeLimitsCommand(params)
            },
            
            // Usage commands
            'usage': {
                description: 'Show usage statistics for a period or component',
                usage: '/usage [period] [component]',
                params: [
                    { name: 'period', optional: true, description: 'Time period (daily, weekly, monthly)' },
                    { name: 'component', optional: true, description: 'Component name' }
                ],
                execute: async (params) => this._executeUsageCommand(params)
            },
            'query': {
                description: 'Query usage records with filtering',
                usage: '/query [filters]',
                params: [
                    { name: 'filters', optional: true, description: 'Filter parameters as key=value pairs' }
                ],
                execute: async (params) => this._executeQueryCommand(params)
            },
            
            // Model commands
            'models': {
                description: 'List available models or get details for a specific model',
                usage: '/models [provider] [model]',
                params: [
                    { name: 'provider', optional: true, description: 'Provider name' },
                    { name: 'model', optional: true, description: 'Model name' }
                ],
                execute: async (params) => this._executeModelsCommand(params)
            },
            'prices': {
                description: 'Show pricing information for models',
                usage: '/prices [provider] [model]',
                params: [
                    { name: 'provider', optional: true, description: 'Provider name' },
                    { name: 'model', optional: true, description: 'Model name' }
                ],
                execute: async (params) => this._executePricesCommand(params)
            },
            'recommend': {
                description: 'Get model recommendations based on task description',
                usage: '/recommend <task_description>',
                params: [
                    { name: 'task_description', optional: false, description: 'Description of the task' }
                ],
                execute: async (params) => this._executeRecommendCommand(params)
            },
            
            // Analysis commands
            'analyze': {
                description: 'Analyze budget usage patterns',
                usage: '/analyze [period] [days]',
                params: [
                    { name: 'period', optional: true, description: 'Budget period (daily, weekly, monthly)' },
                    { name: 'days', optional: true, description: 'Number of days to analyze' }
                ],
                execute: async (params) => this._executeAnalyzeCommand(params)
            },
            'optimize': {
                description: 'Get optimization recommendations',
                usage: '/optimize [period] [days]',
                params: [
                    { name: 'period', optional: true, description: 'Budget period (daily, weekly, monthly)' },
                    { name: 'days', optional: true, description: 'Number of days to analyze' }
                ],
                execute: async (params) => this._executeOptimizeCommand(params)
            },
            
            // Alert commands
            'alerts': {
                description: 'Show active alerts or clear alerts',
                usage: '/alerts [action]',
                params: [
                    { name: 'action', optional: true, description: 'Action to perform (list, clear)' }
                ],
                execute: async (params) => this._executeAlertsCommand(params)
            },
            
            // Utility commands
            'refresh': {
                description: 'Refresh all data',
                usage: '/refresh',
                params: [],
                execute: async () => this._executeRefreshCommand()
            },
            'clear': {
                description: 'Clear chat messages',
                usage: '/clear',
                params: [],
                execute: async () => this._executeClearCommand()
            }
        };
    }
    
    /**
     * Check if text is a CLI command
     * @param {string} text - Input text
     * @returns {boolean} Is command
     */
    isCommand(text) {
        return text && text.trim().startsWith(this.commandPrefix);
    }
    
    /**
     * Parse command text into command and arguments
     * @param {string} text - Command text
     * @returns {Object} Parsed command
     */
    parseCommand(text) {
        if (!this.isCommand(text)) {
            return null;
        }
        
        // Remove prefix and split into parts
        const parts = text.trim().substring(this.commandPrefix.length).split(/\s+/);
        const commandName = parts[0].toLowerCase();
        const args = parts.slice(1);
        
        // Get command definition
        const command = this.availableCommands[commandName];
        
        if (!command) {
            return {
                valid: false,
                name: commandName,
                error: `Unknown command: ${commandName}`
            };
        }
        
        // Parse parameters according to command definition
        const params = {};
        const requiredParams = command.params.filter(p => !p.optional);
        
        if (args.length < requiredParams.length) {
            return {
                valid: false,
                name: commandName,
                error: `Missing required parameters. Usage: ${command.usage}`
            };
        }
        
        // Assign arguments to parameters
        for (let i = 0; i < command.params.length; i++) {
            if (i < args.length) {
                params[command.params[i].name] = args[i];
            }
        }
        
        return {
            valid: true,
            name: commandName,
            params
        };
    }
    
    /**
     * Execute a parsed command
     * @param {Object} parsedCommand - The parsed command
     * @returns {Promise<string>} Command result message
     */
    async executeCommand(parsedCommand) {
        if (!parsedCommand || !parsedCommand.valid) {
            return parsedCommand.error || 'Invalid command';
        }
        
        const { name, params } = parsedCommand;
        const command = this.availableCommands[name];
        
        if (!command) {
            return `Unknown command: ${name}`;
        }
        
        try {
            return await command.execute(params);
        } catch (error) {
            console.error('[BUDGET CLI] Command execution error:', error);
            return `Error executing command: ${error.message}`;
        }
    }
    
    /**
     * Get autocompletion suggestions for partial command
     * @param {string} partial - Partial command text
     * @returns {Array} Suggestion list
     */
    getAutocompleteSuggestions(partial) {
        if (!partial || !partial.startsWith(this.commandPrefix)) {
            return [];
        }
        
        // Remove prefix and get command part
        const parts = partial.substring(this.commandPrefix.length).split(/\s+/);
        const commandPart = parts[0].toLowerCase();
        
        // Check if we're autocompleting a command name
        if (parts.length === 1) {
            return Object.keys(this.availableCommands)
                .filter(cmd => cmd.startsWith(commandPart))
                .map(cmd => `${this.commandPrefix}${cmd}`);
        }
        
        // Check if we're autocompleting command parameters
        const commandName = commandPart;
        const command = this.availableCommands[commandName];
        
        if (!command) {
            return [];
        }
        
        // Get parameter suggestions based on parameter position
        const paramIndex = parts.length - 2; // -1 for 0-based index, -1 for command name
        
        if (paramIndex >= command.params.length) {
            return [];
        }
        
        const param = command.params[paramIndex];
        
        // Generate suggestions based on parameter type
        switch (param.name) {
            case 'period':
                return ['daily', 'weekly', 'monthly']
                    .filter(p => p.startsWith(parts[parts.length - 1].toLowerCase()))
                    .map(p => `${partial.substring(0, partial.lastIndexOf(' ') + 1)}${p}`);
                
            case 'action':
                return ['list', 'clear']
                    .filter(a => a.startsWith(parts[parts.length - 1].toLowerCase()))
                    .map(a => `${partial.substring(0, partial.lastIndexOf(' ') + 1)}${a}`);
                
            default:
                return [];
        }
    }
    
    /**
     * Get help text for a command
     * @param {string} commandName - Command name
     * @returns {string} Help text
     */
    getCommandHelp(commandName) {
        if (!commandName) {
            // List all commands
            const categories = {
                'General Commands': ['help'],
                'Budget Commands': ['budget', 'limits'],
                'Usage Commands': ['usage', 'query'],
                'Model Commands': ['models', 'prices', 'recommend'],
                'Analysis Commands': ['analyze', 'optimize'],
                'Alert Commands': ['alerts'],
                'Utility Commands': ['refresh', 'clear']
            };
            
            let helpText = 'Available Commands:\n\n';
            
            for (const category in categories) {
                helpText += `${category}:\n`;
                
                for (const cmd of categories[category]) {
                    const command = this.availableCommands[cmd];
                    
                    if (command) {
                        helpText += `  ${this.commandPrefix}${cmd} - ${command.description}\n`;
                    }
                }
                
                helpText += '\n';
            }
            
            helpText += 'Type /help <command> for more details on a specific command.';
            
            return helpText;
        }
        
        // Get help for specific command
        const command = this.availableCommands[commandName];
        
        if (!command) {
            return `Unknown command: ${commandName}`;
        }
        
        let helpText = `Command: ${this.commandPrefix}${commandName}\n\n`;
        helpText += `Description: ${command.description}\n\n`;
        helpText += `Usage: ${command.usage}\n\n`;
        
        if (command.params.length > 0) {
            helpText += 'Parameters:\n';
            
            for (const param of command.params) {
                helpText += `  ${param.name}${param.optional ? ' (optional)' : ''}: ${param.description}\n`;
            }
        }
        
        return helpText;
    }
    
    // --- Command Implementations ---
    
    /**
     * Execute help command
     * @param {Object} params - Command parameters
     * @returns {Promise<string>} Command result
     */
    async _executeHelpCommand(params) {
        return this.getCommandHelp(params.command);
    }
    
    /**
     * Execute budget command
     * @param {Object} params - Command parameters
     * @returns {Promise<string>} Command result
     */
    async _executeBudgetCommand(params) {
        try {
            let period = 'monthly';
            
            if (params.period) {
                if (['daily', 'weekly', 'monthly'].includes(params.period.toLowerCase())) {
                    period = params.period.toLowerCase();
                } else {
                    return `Invalid period: ${params.period}. Use 'daily', 'weekly', or 'monthly'.`;
                }
            }
            
            const response = await this.apiClient.getDashboardSummary(period);
            
            // Format the response
            let result = `Budget Summary (${period}):\n\n`;
            
            for (const summary of response) {
                result += `Budget: ${summary.name || 'Default Budget'}\n`;
                result += `Period: ${period}\n`;
                result += `Total Spend: ${formatCurrency(summary.total_cost || 0)}\n`;
                result += `Budget Limit: ${formatCurrency(summary.cost_limit || 0)}\n`;
                result += `Usage: ${summary.cost_usage_percentage || 0}%\n`;
                result += `Tokens Used: ${formatTokens(summary.total_tokens_used || 0)}\n`;
                result += `Token Limit: ${formatTokens(summary.token_limit || 0)}\n\n`;
            }
            
            // If empty, create default response
            if (!response || response.length === 0) {
                result = `No budget data found for ${period} period.`;
            }
            
            return result;
            
        } catch (error) {
            console.error('[BUDGET CLI] Budget command error:', error);
            return `Error retrieving budget data: ${error.message}`;
        }
    }
    
    /**
     * Execute limits command
     * @param {Object} params - Command parameters
     * @returns {Promise<string>} Command result
     */
    async _executeLimitsCommand(params) {
        try {
            // If no parameters, show current limits
            if (!params.period) {
                const settings = this.stateManager.getState().settingsData;
                
                return 'Current Budget Limits:\n\n' +
                    `Daily Limit: ${formatCurrency(settings.getDailyBudgetLimit())}\n` +
                    `Weekly Limit: ${formatCurrency(settings.getWeeklyBudgetLimit())}\n` +
                    `Monthly Limit: ${formatCurrency(settings.getMonthlyBudgetLimit())}\n` +
                    `Warning Threshold: ${settings.getWarningThreshold()}%\n` +
                    `Enforcement Policy: ${settings.getEnforcementPolicy()}`;
            }
            
            // Check if period parameter is valid
            if (!['daily', 'weekly', 'monthly'].includes(params.period.toLowerCase())) {
                return `Invalid period: ${params.period}. Use 'daily', 'weekly', or 'monthly'.`;
            }
            
            // Check if amount parameter is provided and valid
            if (!params.amount) {
                return 'Missing amount parameter. Usage: /limits [period] [amount]';
            }
            
            // Parse amount
            const amount = parseFloat(params.amount);
            
            if (isNaN(amount) || amount < 0) {
                return `Invalid amount: ${params.amount}. Must be a positive number.`;
            }
            
            // Get settings data
            const settings = this.stateManager.getState().settingsData;
            
            // Find and update the appropriate policy
            const policy = settings.policies.find(p => 
                p.period === params.period.toLowerCase() && 
                p.type === 'hard_limit' &&
                !p.provider && !p.tier
            );
            
            if (!policy) {
                return `Could not find policy for ${params.period} period.`;
            }
            
            // Update policy
            const updatedPolicy = {
                ...policy,
                costLimit: amount
            };
            
            // Send update to API
            await this.apiClient.updatePolicy(policy.id, updatedPolicy);
            
            return `Successfully updated ${params.period} budget limit to ${formatCurrency(amount)}.`;
            
        } catch (error) {
            console.error('[BUDGET CLI] Limits command error:', error);
            return `Error updating budget limits: ${error.message}`;
        }
    }
    
    /**
     * Execute usage command
     * @param {Object} params - Command parameters
     * @returns {Promise<string>} Command result
     */
    async _executeUsageCommand(params) {
        try {
            let period = 'monthly';
            let component = null;
            
            if (params.period) {
                if (['daily', 'weekly', 'monthly'].includes(params.period.toLowerCase())) {
                    period = params.period.toLowerCase();
                } else if (!params.component) {
                    // If component is not specified, treat the first parameter as component
                    component = params.period;
                }
            }
            
            if (params.component) {
                component = params.component;
            }
            
            // Prepare request
            const requestParams = {
                period,
                ...(component ? { component } : {})
            };
            
            const response = await this.apiClient.getUsageSummary(period, requestParams);
            
            // Format the response
            let result = `Usage Summary (${period}):\n\n`;
            
            if (component) {
                result = `Usage Summary for ${component} (${period}):\n\n`;
            }
            
            result += `Total Tokens: ${formatTokens(response.total_tokens || 0)}\n`;
            result += `Input Tokens: ${formatTokens(response.input_tokens || 0)}\n`;
            result += `Output Tokens: ${formatTokens(response.output_tokens || 0)}\n`;
            result += `Total Cost: ${formatCurrency(response.total_cost || 0)}\n\n`;
            
            if (response.providers && response.providers.length > 0) {
                result += 'Usage by Provider:\n';
                
                for (const provider of response.providers) {
                    result += `- ${provider.name}: ${formatTokens(provider.tokens || 0)} tokens, ${formatCurrency(provider.cost || 0)}\n`;
                }
                
                result += '\n';
            }
            
            if (response.models && response.models.length > 0) {
                result += 'Usage by Model:\n';
                
                for (const model of response.models) {
                    result += `- ${model.provider}/${model.name}: ${formatTokens(model.tokens || 0)} tokens, ${formatCurrency(model.cost || 0)}\n`;
                }
                
                result += '\n';
            }
            
            if (response.components && response.components.length > 0) {
                result += 'Usage by Component:\n';
                
                for (const comp of response.components) {
                    result += `- ${comp.name}: ${formatTokens(comp.tokens || 0)} tokens, ${formatCurrency(comp.cost || 0)}\n`;
                }
            }
            
            return result;
            
        } catch (error) {
            console.error('[BUDGET CLI] Usage command error:', error);
            return `Error retrieving usage data: ${error.message}`;
        }
    }
    
    /**
     * Execute query command
     * @param {Object} params - Command parameters
     * @returns {Promise<string>} Command result
     */
    async _executeQueryCommand(params) {
        try {
            const filters = {};
            
            // Parse filters
            if (params.filters) {
                const filterParts = params.filters.split(' ');
                
                for (const part of filterParts) {
                    if (part.includes('=')) {
                        const [key, value] = part.split('=');
                        filters[key] = value;
                    }
                }
            }
            
            // Get usage records
            const response = await this.apiClient.getUsageRecords(filters);
            
            if (!response || !response.items || response.items.length === 0) {
                return 'No usage records found matching your query.';
            }
            
            // Format the response
            let result = `Usage Records (Page ${response.page} of ${Math.ceil(response.total / response.limit)}):\n\n`;
            
            for (const record of response.items) {
                const date = new Date(record.timestamp);
                result += `${date.toLocaleString()}: ${record.component || 'Unknown'}\n`;
                result += `  Provider: ${record.provider || 'Unknown'}, Model: ${record.model || 'Unknown'}\n`;
                result += `  Tokens: ${formatTokens(record.input_tokens + record.output_tokens)}, Cost: ${formatCurrency(record.cost || 0)}\n\n`;
            }
            
            result += `Showing ${response.items.length} of ${response.total} records.`;
            
            return result;
            
        } catch (error) {
            console.error('[BUDGET CLI] Query command error:', error);
            return `Error querying usage records: ${error.message}`;
        }
    }
    
    /**
     * Execute models command
     * @param {Object} params - Command parameters
     * @returns {Promise<string>} Command result
     */
    async _executeModelsCommand(params) {
        try {
            const provider = params.provider;
            const model = params.model;
            
            // Get prices
            const prices = await this.apiClient.getPrices(provider, model);
            
            if (!prices || prices.length === 0) {
                return 'No model data found.';
            }
            
            // Format the response
            let result = 'Available Models:\n\n';
            
            if (provider && model) {
                result = `Model Information for ${provider}/${model}:\n\n`;
            } else if (provider) {
                result = `Models for ${provider}:\n\n`;
            }
            
            // Group by provider
            const providers = {};
            
            for (const price of prices) {
                if (!providers[price.provider]) {
                    providers[price.provider] = [];
                }
                
                providers[price.provider].push(price);
            }
            
            // Format providers and models
            for (const providerName in providers) {
                result += `${providerName}:\n`;
                
                for (const price of providers[providerName]) {
                    result += `  ${price.model}\n`;
                    result += `    Input: ${formatCurrency(price.input_cost_per_token)} per token\n`;
                    result += `    Output: ${formatCurrency(price.output_cost_per_token)} per token\n`;
                    
                    if (price.context_window_tokens) {
                        result += `    Context Window: ${formatTokens(price.context_window_tokens)} tokens\n`;
                    }
                    
                    result += '\n';
                }
            }
            
            return result;
            
        } catch (error) {
            console.error('[BUDGET CLI] Models command error:', error);
            return `Error retrieving model data: ${error.message}`;
        }
    }
    
    /**
     * Execute prices command
     * @param {Object} params - Command parameters
     * @returns {Promise<string>} Command result
     */
    async _executePricesCommand(params) {
        try {
            const provider = params.provider;
            const model = params.model;
            
            // Get prices
            const prices = await this.apiClient.getPrices(provider, model);
            
            if (!prices || prices.length === 0) {
                return 'No pricing data found.';
            }
            
            // Format the response
            let result = 'Model Pricing:\n\n';
            
            if (provider && model) {
                result = `Pricing for ${provider}/${model}:\n\n`;
            } else if (provider) {
                result = `Pricing for ${provider} models:\n\n`;
            }
            
            // Sort by provider and model
            const sortedPrices = [...prices].sort((a, b) => {
                if (a.provider !== b.provider) {
                    return a.provider.localeCompare(b.provider);
                }
                
                return a.model.localeCompare(b.model);
            });
            
            // Format pricing table
            for (const price of sortedPrices) {
                result += `${price.provider}/${price.model}:\n`;
                result += `  Input: ${formatCurrency(price.input_cost_per_token)} per token\n`;
                result += `  Output: ${formatCurrency(price.output_cost_per_token)} per token\n`;
                result += `  Example 1K tokens (in/out): ${formatCurrency(price.input_cost_per_token * 1000 + price.output_cost_per_token * 1000)}\n`;
                
                if (price.context_window_tokens) {
                    result += `  Context Window: ${formatTokens(price.context_window_tokens)} tokens\n`;
                }
                
                result += '\n';
            }
            
            return result;
            
        } catch (error) {
            console.error('[BUDGET CLI] Prices command error:', error);
            return `Error retrieving pricing data: ${error.message}`;
        }
    }
    
    /**
     * Execute recommend command
     * @param {Object} params - Command parameters
     * @returns {Promise<string>} Command result
     */
    async _executeRecommendCommand(params) {
        try {
            if (!params.task_description) {
                return 'Missing task description. Usage: /recommend <task_description>';
            }
            
            // Prepare recommendations request
            const requestParams = {
                task_description: params.task_description,
                input_length: 2000, // Assume reasonable defaults
                output_length: 2000,
                usage_frequency: 5,
                budget_limit: 5.0,
                priority_areas: 'accuracy, value'
            };
            
            // Get recommendations
            const response = await this.apiClient.getModelRecommendations(requestParams);
            
            if (!response.success) {
                return `Error getting recommendations: ${response.error}`;
            }
            
            // Display the response directly
            return response.recommendations;
            
        } catch (error) {
            console.error('[BUDGET CLI] Recommend command error:', error);
            return `Error getting model recommendations: ${error.message}`;
        }
    }
    
    /**
     * Execute analyze command
     * @param {Object} params - Command parameters
     * @returns {Promise<string>} Command result
     */
    async _executeAnalyzeCommand(params) {
        try {
            let period = 'monthly';
            let days = 30;
            
            if (params.period && ['daily', 'weekly', 'monthly'].includes(params.period.toLowerCase())) {
                period = params.period.toLowerCase();
            }
            
            if (params.days) {
                const parsedDays = parseInt(params.days);
                if (!isNaN(parsedDays) && parsedDays > 0) {
                    days = parsedDays;
                }
            }
            
            // Prepare request
            const requestParams = {
                period,
                days
            };
            
            // Get analysis
            const response = await this.apiClient.getBudgetAnalysis(requestParams);
            
            if (!response.success) {
                return `Error analyzing budget usage: ${response.error}`;
            }
            
            // Display the response directly
            return response.analysis;
            
        } catch (error) {
            console.error('[BUDGET CLI] Analyze command error:', error);
            return `Error analyzing budget usage: ${error.message}`;
        }
    }
    
    /**
     * Execute optimize command
     * @param {Object} params - Command parameters
     * @returns {Promise<string>} Command result
     */
    async _executeOptimizeCommand(params) {
        try {
            let period = 'monthly';
            let days = 30;
            
            if (params.period && ['daily', 'weekly', 'monthly'].includes(params.period.toLowerCase())) {
                period = params.period.toLowerCase();
            }
            
            if (params.days) {
                const parsedDays = parseInt(params.days);
                if (!isNaN(parsedDays) && parsedDays > 0) {
                    days = parsedDays;
                }
            }
            
            // Prepare request
            const requestParams = {
                period,
                days
            };
            
            // Get optimization recommendations
            const response = await this.apiClient.getOptimizationRecommendations(requestParams);
            
            if (!response.success) {
                return `Error getting optimization recommendations: ${response.error}`;
            }
            
            // Display the response directly
            return response.recommendations;
            
        } catch (error) {
            console.error('[BUDGET CLI] Optimize command error:', error);
            return `Error getting optimization recommendations: ${error.message}`;
        }
    }
    
    /**
     * Execute alerts command
     * @param {Object} params - Command parameters
     * @returns {Promise<string>} Command result
     */
    async _executeAlertsCommand(params) {
        try {
            let action = 'list';
            
            if (params.action && ['list', 'clear'].includes(params.action.toLowerCase())) {
                action = params.action.toLowerCase();
            }
            
            if (action === 'list') {
                // Get alerts
                const response = await this.apiClient.getAlerts();
                
                if (!response || !response.items || response.items.length === 0) {
                    return 'No active alerts found.';
                }
                
                // Format the response
                let result = 'Active Alerts:\n\n';
                
                for (const alert of response.items) {
                    const date = new Date(alert.timestamp);
                    const severity = alert.severity.toUpperCase();
                    result += `[${severity}] ${alert.title}\n`;
                    result += `  ${alert.message}\n`;
                    result += `  Time: ${date.toLocaleString()}\n`;
                    
                    if (alert.budget_id) {
                        result += `  Budget: ${alert.budget_id}\n`;
                    }
                    
                    result += '\n';
                }
                
                return result;
            } else if (action === 'clear') {
                // Clear all alerts by acknowledging them
                const alerts = await this.apiClient.getAlerts();
                
                if (!alerts || !alerts.items || alerts.items.length === 0) {
                    return 'No active alerts to clear.';
                }
                
                let clearedCount = 0;
                
                for (const alert of alerts.items) {
                    await this.apiClient.acknowledgeAlert(alert.alert_id);
                    clearedCount++;
                }
                
                return `Successfully cleared ${clearedCount} alert(s).`;
            }
            
        } catch (error) {
            console.error('[BUDGET CLI] Alerts command error:', error);
            return `Error processing alerts: ${error.message}`;
        }
    }
    
    /**
     * Execute refresh command
     * @returns {Promise<string>} Command result
     */
    async _executeRefreshCommand() {
        try {
            // Update state to trigger refresh through parent component
            this.stateManager.scheduleUpdate(state => {
                state.refreshTriggered = Date.now();
            });
            
            return 'Refreshing all budget data...';
            
        } catch (error) {
            console.error('[BUDGET CLI] Refresh command error:', error);
            return `Error refreshing data: ${error.message}`;
        }
    }
    
    /**
     * Execute clear command
     * @returns {Promise<string>} Command result
     */
    async _executeClearCommand() {
        try {
            const state = this.stateManager.getState();
            const chatType = state.activeTab === 'budgetchat' ? 'budgetchat' : 'teamchat';
            
            // Clear chat messages
            this.stateManager.clearChat(chatType);
            
            return null; // Don't show any message since chat is cleared
            
        } catch (error) {
            console.error('[BUDGET CLI] Clear command error:', error);
            return `Error clearing chat: ${error.message}`;
        }
    }
}

// Helper functions for formatting
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

function formatTokens(count) {
    if (count >= 1000000) {
        return (count / 1000000).toFixed(1) + 'M';
    } else if (count >= 1000) {
        return (count / 1000).toFixed(1) + 'K';
    } else {
        return count.toString();
    }
}

// Export as global class
window.BudgetCliHandler = BudgetCliHandler;