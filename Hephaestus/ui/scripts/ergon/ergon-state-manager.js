/**
 * ErgonStateManager.js
 * 
 * Specialized state management implementation for Ergon components
 * with reactive patterns and optimized for agent state handling.
 * Extends the core Tekton state manager with agent-specific enhancements.
 */

class ErgonStateManager {
    constructor() {
        // Core state is managed by the main StateManager
        this.coreStateManager = window.tektonUI.stateManager;
        this.initialized = false;
        this.derivedStates = {};
        this.stateSubscriptions = {};
        this.agentNamespace = 'ergon_agents';
        this.agentSettingsNamespace = 'ergon_settings';
        this.agentExecutionsNamespace = 'ergon_executions';
        this.agentTypesNamespace = 'ergon_types';
        this.agentNamespaces = new Set();
        this.agentCache = new Map();
    }

    /**
     * Initialize the Ergon state manager
     * 
     * @param {Object} options - Configuration options
     * @returns {ErgonStateManager} - The state manager instance
     */
    init(options = {}) {
        if (this.initialized) return this;
        
        // Register in window.tektonUI
        if (!window.tektonUI) {
            window.tektonUI = {};
        }

        window.tektonUI.ergonStateManager = this;
        
        // Initialize namespaces in core state manager
        this.coreStateManager.setState(this.agentNamespace, {}, { silent: true });
        this.coreStateManager.setState(this.agentSettingsNamespace, {}, { silent: true });
        this.coreStateManager.setState(this.agentExecutionsNamespace, {}, { silent: true });
        this.coreStateManager.setState(this.agentTypesNamespace, {}, { silent: true });
        
        // Configure persistence for settings
        this.coreStateManager.configurePersistence(this.agentSettingsNamespace, {
            type: 'localStorage',
            key: 'tekton_ergon_settings',
            exclude: ['temporarySettings']
        });
        
        // Set default agent collections
        this._initializeCollections();
        
        // Create commonly needed derived states
        this._initializeDerivedStates();
        
        this.initialized = true;
        this._log('ErgonStateManager initialized');
        
        return this;
    }
    
    /**
     * Initialize agent state collections
     * @private
     */
    _initializeCollections() {
        // Set up agent collections with indices
        const collections = {
            agentList: [],
            agentIndex: {},
            agentFilters: {
                search: '',
                type: 'all',
                status: 'all',
                sortBy: 'name'
            },
            activeAgent: null,
            isLoading: false,
            lastError: null,
            lastUpdated: new Date().toISOString()
        };
        
        this.coreStateManager.setState(this.agentNamespace, collections, { silent: true });
        
        // Set up execution tracking
        const executions = {
            activeExecutions: {},
            historicalExecutions: {},
            executionFilters: {
                agentId: null,
                status: 'all',
                timeRange: 'all',
                sortBy: 'timestamp'
            },
            isLoading: false,
            lastError: null
        };
        
        this.coreStateManager.setState(this.agentExecutionsNamespace, executions, { silent: true });
        
        // Set up agent type categories
        const typeCollections = {
            types: [],
            typeIndex: {},
            typeCategories: [],
            isLoading: false
        };
        
        this.coreStateManager.setState(this.agentTypesNamespace, typeCollections, { silent: true });
        
        // Set up default settings
        const defaultSettings = {
            defaultModel: 'gpt-4',
            autoRefreshInterval: 30,
            defaultTemperature: 0.7,
            defaultMaxTokens: 2000,
            showAdvancedOptions: false,
            developerMode: false,
            apiEndpoint: '/api/ergon',
            preferredAgentTypes: [],
            ui: {
                theme: 'system',
                compactMode: false,
                showExecutionDetails: true,
                showAgentDetails: true
            }
        };
        
        this.coreStateManager.setState(this.agentSettingsNamespace, defaultSettings, { silent: true });
    }
    
    /**
     * Initialize commonly needed derived states
     * @private
     */
    _initializeDerivedStates() {
        // Create filtered agents list as derived state
        this.coreStateManager.createDerivedState(
            this.agentNamespace,
            'filteredAgents',
            ['agentList', 'agentFilters'],
            (state) => {
                const { agentList, agentFilters } = state;
                
                if (!agentList || !agentList.length) {
                    return [];
                }
                
                // Apply filters
                let filtered = [...agentList];
                
                // Search filter
                if (agentFilters.search) {
                    const searchLower = agentFilters.search.toLowerCase();
                    filtered = filtered.filter(agent => 
                        agent.name.toLowerCase().includes(searchLower) || 
                        (agent.description && agent.description.toLowerCase().includes(searchLower))
                    );
                }
                
                // Type filter
                if (agentFilters.type && agentFilters.type !== 'all') {
                    filtered = filtered.filter(agent => agent.type === agentFilters.type);
                }
                
                // Status filter
                if (agentFilters.status && agentFilters.status !== 'all') {
                    filtered = filtered.filter(agent => agent.status === agentFilters.status);
                }
                
                // Apply sorting
                if (agentFilters.sortBy) {
                    const sortField = agentFilters.sortBy;
                    const direction = agentFilters.sortDirection === 'desc' ? -1 : 1;
                    
                    filtered.sort((a, b) => {
                        if (a[sortField] < b[sortField]) return -1 * direction;
                        if (a[sortField] > b[sortField]) return 1 * direction;
                        return 0;
                    });
                }
                
                return filtered;
            }
        );
        
        // Create active executions count as derived state
        this.coreStateManager.createDerivedState(
            this.agentExecutionsNamespace,
            'activeExecutionsCount',
            ['activeExecutions'],
            (state) => {
                const { activeExecutions } = state;
                return Object.keys(activeExecutions || {}).length;
            }
        );
        
        // Create filtered executions list as derived state
        this.coreStateManager.createDerivedState(
            this.agentExecutionsNamespace,
            'filteredExecutions',
            ['historicalExecutions', 'executionFilters'],
            (state) => {
                const { historicalExecutions, executionFilters } = state;
                
                if (!historicalExecutions) {
                    return [];
                }
                
                // Convert executions object to array
                let executionArray = Object.values(historicalExecutions);
                
                // Apply filters
                if (executionFilters.agentId) {
                    executionArray = executionArray.filter(
                        execution => execution.agentId === executionFilters.agentId
                    );
                }
                
                if (executionFilters.status && executionFilters.status !== 'all') {
                    executionArray = executionArray.filter(
                        execution => execution.status === executionFilters.status
                    );
                }
                
                if (executionFilters.timeRange && executionFilters.timeRange !== 'all') {
                    const now = new Date();
                    let cutoff = new Date();
                    
                    switch(executionFilters.timeRange) {
                        case 'today':
                            cutoff.setHours(0, 0, 0, 0);
                            break;
                        case 'week':
                            cutoff.setDate(now.getDate() - 7);
                            break;
                        case 'month':
                            cutoff.setMonth(now.getMonth() - 1);
                            break;
                    }
                    
                    executionArray = executionArray.filter(execution => {
                        const executionDate = new Date(execution.timestamp);
                        return executionDate >= cutoff;
                    });
                }
                
                // Apply sorting
                const sortField = executionFilters.sortBy || 'timestamp';
                const direction = executionFilters.sortDirection === 'asc' ? 1 : -1;
                
                executionArray.sort((a, b) => {
                    if (a[sortField] < b[sortField]) return -1 * direction;
                    if (a[sortField] > b[sortField]) return 1 * direction;
                    return 0;
                });
                
                return executionArray;
            }
        );
    }
    
    /**
     * Get all agent state
     * 
     * @param {string} key - Optional specific key to retrieve
     * @returns {*} - The requested state
     */
    getAgentState(key = null) {
        return this.coreStateManager.getState(this.agentNamespace, key);
    }
    
    /**
     * Set agent state
     * 
     * @param {Object} updates - State updates
     * @param {Object} options - Update options
     * @returns {Object} - The updated state
     */
    setAgentState(updates, options = {}) {
        return this.coreStateManager.setState(this.agentNamespace, updates, options);
    }
    
    /**
     * Get Ergon settings
     * 
     * @param {string} key - Optional specific key to retrieve
     * @returns {*} - The requested settings
     */
    getSettings(key = null) {
        return this.coreStateManager.getState(this.agentSettingsNamespace, key);
    }
    
    /**
     * Update Ergon settings
     * 
     * @param {Object} updates - Settings updates
     * @param {Object} options - Update options
     * @returns {Object} - The updated settings
     */
    setSettings(updates, options = {}) {
        return this.coreStateManager.setState(this.agentSettingsNamespace, updates, options);
    }
    
    /**
     * Get agent executions state
     * 
     * @param {string} key - Optional specific key to retrieve
     * @returns {*} - The requested state
     */
    getExecutionState(key = null) {
        return this.coreStateManager.getState(this.agentExecutionsNamespace, key);
    }
    
    /**
     * Set agent executions state
     * 
     * @param {Object} updates - State updates
     * @param {Object} options - Update options
     * @returns {Object} - The updated state
     */
    setExecutionState(updates, options = {}) {
        return this.coreStateManager.setState(this.agentExecutionsNamespace, updates, options);
    }
    
    /**
     * Get agent types state
     * 
     * @param {string} key - Optional specific key to retrieve
     * @returns {*} - The requested state
     */
    getAgentTypes(key = null) {
        return this.coreStateManager.getState(this.agentTypesNamespace, key);
    }
    
    /**
     * Set agent types state
     * 
     * @param {Object} updates - State updates
     * @param {Object} options - Update options
     * @returns {Object} - The updated state
     */
    setAgentTypes(updates, options = {}) {
        return this.coreStateManager.setState(this.agentTypesNamespace, updates, options);
    }
    
    /**
     * Update agent list
     * 
     * @param {Array} agents - List of agents
     * @returns {Object} - Updated agent state
     */
    updateAgentList(agents) {
        // Start transaction for batch update
        const commit = this.coreStateManager.startTransaction();
        
        // Update list and build index
        const agentIndex = {};
        agents.forEach(agent => {
            agentIndex[agent.id] = agent;
        });
        
        // Update agent state
        this.setAgentState({
            agentList: agents,
            agentIndex,
            lastUpdated: new Date().toISOString(),
            isLoading: false
        });
        
        // Commit transaction
        commit();
        
        return this.getAgentState();
    }
    
    /**
     * Get an agent by ID
     * 
     * @param {string|number} agentId - Agent ID
     * @returns {Object|null} - Agent object or null if not found
     */
    getAgentById(agentId) {
        const agentIndex = this.getAgentState('agentIndex');
        return agentIndex?.[agentId] || null;
    }
    
    /**
     * Add or update an agent
     * 
     * @param {Object} agent - Agent object
     * @returns {Object} - Updated agent state
     */
    addOrUpdateAgent(agent) {
        // Get current agent list
        const agentList = [...(this.getAgentState('agentList') || [])];
        const agentIndex = {...(this.getAgentState('agentIndex') || {})};
        
        // Check if agent already exists
        const existingIndex = agentList.findIndex(a => a.id === agent.id);
        
        if (existingIndex !== -1) {
            // Update existing agent
            agentList[existingIndex] = agent;
        } else {
            // Add new agent
            agentList.push(agent);
        }
        
        // Update index
        agentIndex[agent.id] = agent;
        
        // Update state
        return this.setAgentState({
            agentList,
            agentIndex,
            lastUpdated: new Date().toISOString()
        });
    }
    
    /**
     * Remove an agent
     * 
     * @param {string|number} agentId - Agent ID
     * @returns {Object} - Updated agent state
     */
    removeAgent(agentId) {
        // Get current agent list
        const agentList = (this.getAgentState('agentList') || [])
            .filter(agent => agent.id !== agentId);
        
        const agentIndex = {...(this.getAgentState('agentIndex') || {})};
        
        // Remove from index
        delete agentIndex[agentId];
        
        // Update state
        return this.setAgentState({
            agentList,
            agentIndex,
            lastUpdated: new Date().toISOString()
        });
    }
    
    /**
     * Set active agent
     * 
     * @param {string|number|null} agentId - Agent ID or null to clear
     * @returns {Object|null} - Active agent or null
     */
    setActiveAgent(agentId) {
        if (!agentId) {
            this.setAgentState({ activeAgent: null });
            return null;
        }
        
        const agent = this.getAgentById(agentId);
        if (agent) {
            this.setAgentState({ activeAgent: agent });
        }
        return agent;
    }
    
    /**
     * Get active agent
     * 
     * @returns {Object|null} - Active agent or null
     */
    getActiveAgent() {
        return this.getAgentState('activeAgent');
    }
    
    /**
     * Update agent filters
     * 
     * @param {Object} filters - Filter updates
     * @returns {Object} - Updated filters
     */
    updateAgentFilters(filters) {
        const currentFilters = this.getAgentState('agentFilters') || {};
        const updatedFilters = { ...currentFilters, ...filters };
        
        this.setAgentState({ agentFilters: updatedFilters });
        return updatedFilters;
    }
    
    /**
     * Track an active execution
     * 
     * @param {Object} execution - Execution object
     * @returns {Object} - Updated executions state
     */
    trackExecution(execution) {
        const activeExecutions = { 
            ...(this.getExecutionState('activeExecutions') || {})
        };
        
        activeExecutions[execution.id] = {
            ...execution,
            status: 'running',
            startTime: new Date().toISOString()
        };
        
        return this.setExecutionState({ activeExecutions });
    }
    
    /**
     * Complete an execution
     * 
     * @param {string|number} executionId - Execution ID
     * @param {Object} result - Execution result
     * @returns {Object} - Updated executions state
     */
    completeExecution(executionId, result) {
        const commit = this.coreStateManager.startTransaction();
        
        // Get current executions
        const activeExecutions = { 
            ...(this.getExecutionState('activeExecutions') || {})
        };
        
        const historicalExecutions = { 
            ...(this.getExecutionState('historicalExecutions') || {})
        };
        
        // Get the execution
        const execution = activeExecutions[executionId];
        if (!execution) {
            commit();
            return this.getExecutionState();
        }
        
        // Remove from active executions
        delete activeExecutions[executionId];
        
        // Add to historical executions with result
        historicalExecutions[executionId] = {
            ...execution,
            ...result,
            status: 'completed',
            endTime: new Date().toISOString(),
            duration: new Date() - new Date(execution.startTime)
        };
        
        // Update state
        this.setExecutionState({
            activeExecutions,
            historicalExecutions
        });
        
        commit();
        return this.getExecutionState();
    }
    
    /**
     * Add an error to an execution
     * 
     * @param {string|number} executionId - Execution ID
     * @param {Object} error - Error object
     * @returns {Object} - Updated executions state
     */
    setExecutionError(executionId, error) {
        const commit = this.coreStateManager.startTransaction();
        
        // Get current executions
        const activeExecutions = { 
            ...(this.getExecutionState('activeExecutions') || {})
        };
        
        const historicalExecutions = { 
            ...(this.getExecutionState('historicalExecutions') || {})
        };
        
        // Get the execution
        const execution = activeExecutions[executionId];
        if (!execution) {
            commit();
            return this.getExecutionState();
        }
        
        // Remove from active executions
        delete activeExecutions[executionId];
        
        // Add to historical executions with error
        historicalExecutions[executionId] = {
            ...execution,
            error,
            status: 'error',
            endTime: new Date().toISOString(),
            duration: new Date() - new Date(execution.startTime)
        };
        
        // Update state
        this.setExecutionState({
            activeExecutions,
            historicalExecutions
        });
        
        commit();
        return this.getExecutionState();
    }
    
    /**
     * Clear historical executions for an agent
     * 
     * @param {string|number} agentId - Agent ID
     * @returns {Object} - Updated executions state
     */
    clearAgentExecutions(agentId) {
        // Get current historical executions
        const historicalExecutions = { 
            ...(this.getExecutionState('historicalExecutions') || {})
        };
        
        // Remove agent executions
        for (const executionId in historicalExecutions) {
            if (historicalExecutions[executionId].agentId === agentId) {
                delete historicalExecutions[executionId];
            }
        }
        
        // Update state
        return this.setExecutionState({ historicalExecutions });
    }
    
    /**
     * Update execution filters
     * 
     * @param {Object} filters - Filter updates
     * @returns {Object} - Updated filters
     */
    updateExecutionFilters(filters) {
        const currentFilters = this.getExecutionState('executionFilters') || {};
        const updatedFilters = { ...currentFilters, ...filters };
        
        this.setExecutionState({ executionFilters: updatedFilters });
        return updatedFilters;
    }
    
    /**
     * Subscribe to agent state changes
     * 
     * @param {Function} callback - State change callback
     * @param {Object} options - Subscription options
     * @returns {string} - Subscription ID
     */
    subscribeToAgentState(callback, options = {}) {
        return this.coreStateManager.subscribe(this.agentNamespace, callback, options);
    }
    
    /**
     * Subscribe to execution state changes
     * 
     * @param {Function} callback - State change callback
     * @param {Object} options - Subscription options
     * @returns {string} - Subscription ID
     */
    subscribeToExecutionState(callback, options = {}) {
        return this.coreStateManager.subscribe(this.agentExecutionsNamespace, callback, options);
    }
    
    /**
     * Subscribe to settings changes
     * 
     * @param {Function} callback - State change callback
     * @param {Object} options - Subscription options
     * @returns {string} - Subscription ID
     */
    subscribeToSettings(callback, options = {}) {
        return this.coreStateManager.subscribe(this.agentSettingsNamespace, callback, options);
    }
    
    /**
     * Subscribe to agent type changes
     * 
     * @param {Function} callback - State change callback
     * @param {Object} options - Subscription options
     * @returns {string} - Subscription ID
     */
    subscribeToAgentTypes(callback, options = {}) {
        return this.coreStateManager.subscribe(this.agentTypesNamespace, callback, options);
    }
    
    /**
     * Create reactive UI with auto rebinding to DOM
     * 
     * @param {Object} component - Component object
     * @param {Object} templates - Map of UI element selectors to template functions
     * @param {Array} stateKeys - State keys to watch
     * @param {string} namespace - State namespace
     * @returns {Object} - Reactive bindings
     */
    createReactiveUI(component, templates, stateKeys, namespace = this.agentNamespace) {
        if (!component || !templates) {
            this._log('Invalid component or templates for reactive UI', 'error');
            return null;
        }
        
        const bindings = {};
        
        // Create update function for each template
        Object.entries(templates).forEach(([selector, templateFn]) => {
            const updateFn = (state) => {
                try {
                    // Get the target element
                    const element = component.$(selector);
                    if (!element) return;
                    
                    // Call template function with state
                    const result = templateFn(state);
                    
                    // Update element
                    element.innerHTML = result;
                } catch (error) {
                    this._log(`Error updating reactive UI for ${selector}:`, 'error', error);
                }
            };
            
            // Call immediately with current state
            updateFn(this.coreStateManager.getState(namespace));
            
            // Subscribe to state changes
            const subscription = this.coreStateManager.subscribe(namespace, (changes, state) => {
                updateFn(state);
            }, { keys: stateKeys });
            
            // Store binding with unsubscribe function
            bindings[selector] = {
                update: () => updateFn(this.coreStateManager.getState(namespace)),
                subscription,
                unsubscribe: () => this.coreStateManager.unsubscribe(subscription)
            };
        });
        
        return bindings;
    }
    
    /**
     * Create form bindings with validation
     * 
     * @param {Object} component - Component object
     * @param {Object} config - Form configuration
     * @param {function} onSubmit - Submit callback
     * @returns {Object} - Form controller with validate, submit, reset functions
     */
    createForm(component, config, onSubmit) {
        if (!component || !config || !config.fields) {
            this._log('Invalid form configuration', 'error');
            return null;
        }
        
        // Create form state in component namespace
        const formNamespace = `ergon_form_${Math.random().toString(36).substring(2, 9)}`;
        
        // Initialize form state
        const formState = {
            values: {},
            errors: {},
            touched: {},
            dirty: {},
            isSubmitting: false,
            isValid: false,
            submitCount: 0,
            submitError: null
        };
        
        // Initialize field values and validation
        Object.entries(config.fields).forEach(([fieldName, fieldConfig]) => {
            formState.values[fieldName] = fieldConfig.initialValue !== undefined ? 
                fieldConfig.initialValue : '';
            formState.touched[fieldName] = false;
            formState.dirty[fieldName] = false;
            formState.errors[fieldName] = null;
        });
        
        // Set initial form state
        this.coreStateManager.setState(formNamespace, formState, { silent: true });
        
        // Validate the form
        const validateForm = () => {
            const state = this.coreStateManager.getState(formNamespace);
            const { values } = state;
            const errors = {};
            let isValid = true;
            
            // Validate each field
            Object.entries(config.fields).forEach(([fieldName, fieldConfig]) => {
                if (fieldConfig.validate) {
                    const error = fieldConfig.validate(values[fieldName], values);
                    errors[fieldName] = error;
                    if (error) {
                        isValid = false;
                    }
                }
            });
            
            // Update form state
            this.coreStateManager.setState(formNamespace, {
                errors,
                isValid
            });
            
            return isValid;
        };
        
        // Create form controller
        const formController = {
            namespace: formNamespace,
            
            // Get form state
            getState: (key = null) => {
                return this.coreStateManager.getState(formNamespace, key);
            },
            
            // Set form values
            setValues: (values, options = {}) => {
                const current = this.coreStateManager.getState(formNamespace);
                const newValues = { ...current.values, ...values };
                
                // Mark fields as dirty
                const dirty = { ...current.dirty };
                Object.keys(values).forEach(key => {
                    dirty[key] = true;
                });
                
                // Update form state
                this.coreStateManager.setState(formNamespace, {
                    values: newValues,
                    dirty
                });
                
                // Validate if not silent
                if (!options.silent) {
                    validateForm();
                }
                
                return newValues;
            },
            
            // Set a single field value
            setFieldValue: (field, value, options = {}) => {
                const current = this.coreStateManager.getState(formNamespace);
                const newValues = { ...current.values, [field]: value };
                const dirty = { ...current.dirty, [field]: true };
                
                // Update form state
                this.coreStateManager.setState(formNamespace, {
                    values: newValues,
                    dirty
                });
                
                // Validate if not silent
                if (!options.silent) {
                    validateForm();
                }
                
                return newValues;
            },
            
            // Mark field as touched
            touchField: (field) => {
                const current = this.coreStateManager.getState(formNamespace);
                const touched = { ...current.touched, [field]: true };
                
                // Update form state
                this.coreStateManager.setState(formNamespace, { touched });
                return touched;
            },
            
            // Reset form
            reset: () => {
                const initialValues = {};
                const touched = {};
                const dirty = {};
                const errors = {};
                
                // Reset to initial values
                Object.entries(config.fields).forEach(([fieldName, fieldConfig]) => {
                    initialValues[fieldName] = fieldConfig.initialValue !== undefined ? 
                        fieldConfig.initialValue : '';
                    touched[fieldName] = false;
                    dirty[fieldName] = false;
                    errors[fieldName] = null;
                });
                
                // Update form state
                this.coreStateManager.setState(formNamespace, {
                    values: initialValues,
                    touched,
                    dirty,
                    errors,
                    isSubmitting: false,
                    isValid: true,
                    submitError: null
                });
            },
            
            // Validate form
            validate: validateForm,
            
            // Submit form
            submit: async () => {
                // Validate first
                const isValid = validateForm();
                
                // Update form state
                this.coreStateManager.setState(formNamespace, {
                    isSubmitting: true,
                    submitCount: this.coreStateManager.getState(formNamespace).submitCount + 1
                });
                
                if (!isValid) {
                    // Mark all fields as touched
                    const touched = {};
                    Object.keys(config.fields).forEach(fieldName => {
                        touched[fieldName] = true;
                    });
                    
                    this.coreStateManager.setState(formNamespace, {
                        touched,
                        isSubmitting: false
                    });
                    
                    return { success: false, reason: 'validation' };
                }
                
                // Call submit handler
                try {
                    const result = await onSubmit(this.coreStateManager.getState(formNamespace).values);
                    
                    // Update form state
                    this.coreStateManager.setState(formNamespace, {
                        isSubmitting: false,
                        submitError: null
                    });
                    
                    return { success: true, result };
                } catch (error) {
                    // Update form state with error
                    this.coreStateManager.setState(formNamespace, {
                        isSubmitting: false,
                        submitError: error.message || String(error)
                    });
                    
                    return { success: false, error };
                }
            },
            
            // Subscribe to form state
            subscribe: (callback, options = {}) => {
                return this.coreStateManager.subscribe(formNamespace, callback, options);
            },
            
            // Create field event handlers
            bindInputs: () => {
                const handlers = {};
                
                Object.keys(config.fields).forEach(fieldName => {
                    handlers[fieldName] = (event) => {
                        const target = event.target;
                        let value;
                        
                        // Handle different input types
                        if (target.type === 'checkbox') {
                            value = target.checked;
                        } else if (target.type === 'number' || target.hasAttribute('data-number-input')) {
                            value = parseFloat(target.value);
                            if (isNaN(value)) {
                                value = 0;
                            }
                        } else {
                            value = target.value;
                        }
                        
                        // Update field value
                        formController.setFieldValue(fieldName, value);
                        
                        // Mark as touched
                        formController.touchField(fieldName);
                    };
                    
                    // Add blur handler to mark field as touched
                    handlers[`${fieldName}Blur`] = () => {
                        formController.touchField(fieldName);
                        validateForm();
                    };
                });
                
                return handlers;
            },
            
            // Cleanup form state
            cleanup: () => {
                // Delete form namespace
                this.coreStateManager.resetState(formNamespace, {});
            }
        };
        
        // Set up submission handler
        if (config.formSelector) {
            const form = component.$(config.formSelector);
            if (form) {
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    return await formController.submit();
                });
            }
        }
        
        return formController;
    }
    
    /**
     * Log a message if debug mode is enabled
     * 
     * @param {string} message - Message to log
     * @param {string} level - Log level (log, warn, error)
     * @param {*} data - Additional data to log
     * @private
     */
    _log(message, level = 'log', data) {
        if (!this.coreStateManager?.debug && level === 'log') return;
        
        const prefix = '[ErgonStateManager]';
        
        if (data !== undefined) {
            console[level](prefix, message, data);
        } else {
            console[level](prefix, message);
        }
    }
}

// Create and export the ErgonStateManager instance
window.tektonUI = window.tektonUI || {};
window.tektonUI.ErgonStateManager = ErgonStateManager;

// Export a singleton instance
window.tektonUI.ergonStateManager = new ErgonStateManager();

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize with default options
    window.tektonUI.ergonStateManager.init();
});