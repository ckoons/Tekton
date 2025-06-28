/**
 * Component Ergon State Utilities
 * 
 * Provides Ergon-specific state management utilities for components.
 * These utilities make it easier for components to work with the Ergon state system,
 * handling agent state, execution tracking, and reactive UI patterns.
 */

console.log('[FILE_TRACE] Loading: component-utils-ergon-state.js');
class ComponentErgonStateUtils {
    constructor() {
        this.initialized = false;
    }
    
    /**
     * Initialize the component Ergon state utilities
     */
    init() {
        if (this.initialized) return this;
        
        // Create utility namespace in global tektonUI
        window.tektonUI = window.tektonUI || {};
        window.tektonUI.componentErgonState = {};
        
        // Initialize all Ergon state utilities
        this._initErgonStateSystem();
        this._initErgonStateLifecycle();
        
        this.initialized = true;
        console.log('Component Ergon state utilities initialized');
        
        return this;
    }
    
    /**
     * Initialize the Ergon component state system
     * @private
     */
    _initErgonStateSystem() {
        window.tektonUI.componentErgonState.utils = {
            /**
             * Connect a component to the Ergon state manager
             * 
             * @param {Object} component - The component context
             * @param {Object} options - State options
             * @returns {Object} - State utilities for the component
             */
            connect: function(component, options = {}) {
                const ergonStateManager = window.tektonUI.ergonStateManager;
                const coreStateManager = window.tektonUI.stateManager;
                
                if (!ergonStateManager || !coreStateManager) {
                    console.error('[ComponentErgonState] State managers not initialized');
                    return null;
                }
                
                // Generate component ID if not present
                component.stateId = component.stateId || component.id || `ergon-component-${Math.random().toString(36).substring(2, 9)}`;
                
                // Create component-specific namespace for local state
                const namespace = `ergon_component_${component.stateId}`;
                
                // Initialize local state
                if (options.initialState) {
                    coreStateManager.setState(namespace, options.initialState, { silent: true });
                }
                
                // Configure persistence if requested
                if (options.persist) {
                    coreStateManager.configurePersistence(namespace, {
                        type: options.persistenceType || 'localStorage',
                        key: `tekton_${namespace}_state`,
                        exclude: options.excludeFromPersistence || []
                    });
                }
                
                // Create state API for component
                const ergonStateApi = {
                    /**
                     * Get the local component state
                     * 
                     * @param {string} key - Optional state key to get
                     * @returns {*} - The requested state
                     */
                    getLocal: function(key = null) {
                        return coreStateManager.getState(namespace, key);
                    },
                    
                    /**
                     * Set local component state
                     * 
                     * @param {Object|string} keyOrObject - State key or object with updates
                     * @param {*} value - Value to set (if key is a string)
                     * @param {Object} options - Update options
                     * @returns {Object} - Updated state
                     */
                    setLocal: function(keyOrObject, value, options = {}) {
                        // Handle both object and key/value formats
                        let updates = {};
                        
                        if (typeof keyOrObject === 'string') {
                            updates[keyOrObject] = value;
                        } else if (typeof keyOrObject === 'object') {
                            updates = keyOrObject;
                            options = value || {};
                        }
                        
                        return coreStateManager.setState(namespace, updates, options);
                    },
                    
                    /**
                     * Subscribe to local state changes
                     * 
                     * @param {Function} callback - State change callback
                     * @param {Object} options - Subscription options
                     * @returns {string} - Subscription ID
                     */
                    subscribeLocal: function(callback, options = {}) {
                        const subscription = coreStateManager.subscribe(namespace, callback, options);
                        
                        // Register cleanup to unsubscribe when component unmounts
                        component.utils.lifecycle.registerCleanupTask(component, () => {
                            coreStateManager.unsubscribe(subscription);
                        });
                        
                        return subscription;
                    },
                    
                    /**
                     * Get agent state
                     * 
                     * @param {string} key - Optional state key to get
                     * @returns {*} - The requested state
                     */
                    getAgentState: function(key = null) {
                        return ergonStateManager.getAgentState(key);
                    },
                    
                    /**
                     * Set agent state
                     * 
                     * @param {Object} updates - State updates
                     * @param {Object} options - Update options
                     * @returns {Object} - Updated state
                     */
                    setAgentState: function(updates, options = {}) {
                        return ergonStateManager.setAgentState(updates, options);
                    },
                    
                    /**
                     * Subscribe to agent state changes
                     * 
                     * @param {Function} callback - State change callback
                     * @param {Object} options - Subscription options
                     * @returns {string} - Subscription ID
                     */
                    subscribeAgentState: function(callback, options = {}) {
                        const subscription = ergonStateManager.subscribeToAgentState(callback, options);
                        
                        // Register cleanup to unsubscribe when component unmounts
                        component.utils.lifecycle.registerCleanupTask(component, () => {
                            coreStateManager.unsubscribe(subscription);
                        });
                        
                        return subscription;
                    },
                    
                    /**
                     * Get Ergon settings
                     * 
                     * @param {string} key - Optional specific key to retrieve
                     * @returns {*} - The requested settings
                     */
                    getSettings: function(key = null) {
                        return ergonStateManager.getSettings(key);
                    },
                    
                    /**
                     * Update Ergon settings
                     * 
                     * @param {Object} updates - Settings updates
                     * @param {Object} options - Update options
                     * @returns {Object} - The updated settings
                     */
                    setSettings: function(updates, options = {}) {
                        return ergonStateManager.setSettings(updates, options);
                    },
                    
                    /**
                     * Subscribe to settings changes
                     * 
                     * @param {Function} callback - State change callback
                     * @param {Object} options - Subscription options
                     * @returns {string} - Subscription ID
                     */
                    subscribeSettings: function(callback, options = {}) {
                        const subscription = ergonStateManager.subscribeToSettings(callback, options);
                        
                        // Register cleanup to unsubscribe when component unmounts
                        component.utils.lifecycle.registerCleanupTask(component, () => {
                            coreStateManager.unsubscribe(subscription);
                        });
                        
                        return subscription;
                    },
                    
                    /**
                     * Get agent executions state
                     * 
                     * @param {string} key - Optional specific key to retrieve
                     * @returns {*} - The requested state
                     */
                    getExecutionState: function(key = null) {
                        return ergonStateManager.getExecutionState(key);
                    },
                    
                    /**
                     * Set agent executions state
                     * 
                     * @param {Object} updates - State updates
                     * @param {Object} options - Update options
                     * @returns {Object} - The updated state
                     */
                    setExecutionState: function(updates, options = {}) {
                        return ergonStateManager.setExecutionState(updates, options);
                    },
                    
                    /**
                     * Subscribe to execution state changes
                     * 
                     * @param {Function} callback - State change callback
                     * @param {Object} options - Subscription options
                     * @returns {string} - Subscription ID
                     */
                    subscribeExecutionState: function(callback, options = {}) {
                        const subscription = ergonStateManager.subscribeToExecutionState(callback, options);
                        
                        // Register cleanup to unsubscribe when component unmounts
                        component.utils.lifecycle.registerCleanupTask(component, () => {
                            coreStateManager.unsubscribe(subscription);
                        });
                        
                        return subscription;
                    },
                    
                    /**
                     * Get agent types state
                     * 
                     * @param {string} key - Optional specific key to retrieve
                     * @returns {*} - The requested state
                     */
                    getAgentTypes: function(key = null) {
                        return ergonStateManager.getAgentTypes(key);
                    },
                    
                    /**
                     * Subscribe to agent type changes
                     * 
                     * @param {Function} callback - State change callback
                     * @param {Object} options - Subscription options
                     * @returns {string} - Subscription ID
                     */
                    subscribeAgentTypes: function(callback, options = {}) {
                        const subscription = ergonStateManager.subscribeToAgentTypes(callback, options);
                        
                        // Register cleanup to unsubscribe when component unmounts
                        component.utils.lifecycle.registerCleanupTask(component, () => {
                            coreStateManager.unsubscribe(subscription);
                        });
                        
                        return subscription;
                    },
                    
                    // Agent operations
                    
                    /**
                     * Get an agent by ID
                     * 
                     * @param {string|number} agentId - Agent ID
                     * @returns {Object|null} - Agent object or null if not found
                     */
                    getAgentById: function(agentId) {
                        return ergonStateManager.getAgentById(agentId);
                    },
                    
                    /**
                     * Add or update an agent
                     * 
                     * @param {Object} agent - Agent object
                     * @returns {Object} - Updated agent state
                     */
                    addOrUpdateAgent: function(agent) {
                        return ergonStateManager.addOrUpdateAgent(agent);
                    },
                    
                    /**
                     * Remove an agent
                     * 
                     * @param {string|number} agentId - Agent ID
                     * @returns {Object} - Updated agent state
                     */
                    removeAgent: function(agentId) {
                        return ergonStateManager.removeAgent(agentId);
                    },
                    
                    /**
                     * Set active agent
                     * 
                     * @param {string|number|null} agentId - Agent ID or null to clear
                     * @returns {Object|null} - Active agent or null
                     */
                    setActiveAgent: function(agentId) {
                        return ergonStateManager.setActiveAgent(agentId);
                    },
                    
                    /**
                     * Get active agent
                     * 
                     * @returns {Object|null} - Active agent or null
                     */
                    getActiveAgent: function() {
                        return ergonStateManager.getActiveAgent();
                    },
                    
                    /**
                     * Update agent filters
                     * 
                     * @param {Object} filters - Filter updates
                     * @returns {Object} - Updated filters
                     */
                    updateAgentFilters: function(filters) {
                        return ergonStateManager.updateAgentFilters(filters);
                    },
                    
                    // Execution operations
                    
                    /**
                     * Track an active execution
                     * 
                     * @param {Object} execution - Execution object
                     * @returns {Object} - Updated executions state
                     */
                    trackExecution: function(execution) {
                        return ergonStateManager.trackExecution(execution);
                    },
                    
                    /**
                     * Complete an execution
                     * 
                     * @param {string|number} executionId - Execution ID
                     * @param {Object} result - Execution result
                     * @returns {Object} - Updated executions state
                     */
                    completeExecution: function(executionId, result) {
                        return ergonStateManager.completeExecution(executionId, result);
                    },
                    
                    /**
                     * Add an error to an execution
                     * 
                     * @param {string|number} executionId - Execution ID
                     * @param {Object} error - Error object
                     * @returns {Object} - Updated executions state
                     */
                    setExecutionError: function(executionId, error) {
                        return ergonStateManager.setExecutionError(executionId, error);
                    },
                    
                    /**
                     * Clear historical executions for an agent
                     * 
                     * @param {string|number} agentId - Agent ID
                     * @returns {Object} - Updated executions state
                     */
                    clearAgentExecutions: function(agentId) {
                        return ergonStateManager.clearAgentExecutions(agentId);
                    },
                    
                    /**
                     * Update execution filters
                     * 
                     * @param {Object} filters - Filter updates
                     * @returns {Object} - Updated filters
                     */
                    updateExecutionFilters: function(filters) {
                        return ergonStateManager.updateExecutionFilters(filters);
                    },
                    
                    // Advanced features
                    
                    /**
                     * Create reactive UI with auto rebinding to DOM
                     * 
                     * @param {Object} templates - Map of UI element selectors to template functions
                     * @param {Array} stateKeys - State keys to watch
                     * @param {string} namespace - State namespace (default: agents)
                     * @returns {Object} - Reactive bindings
                     */
                    createReactiveUI: function(templates, stateKeys, namespace) {
                        return ergonStateManager.createReactiveUI(component, templates, stateKeys, namespace);
                    },
                    
                    /**
                     * Create form bindings with validation
                     * 
                     * @param {Object} config - Form configuration
                     * @param {function} onSubmit - Submit callback
                     * @returns {Object} - Form controller with validate, submit, reset functions
                     */
                    createForm: function(config, onSubmit) {
                        const form = ergonStateManager.createForm(component, config, onSubmit);
                        
                        // Register cleanup to remove form state when component unmounts
                        component.utils.lifecycle.registerCleanupTask(component, () => {
                            form.cleanup();
                        });
                        
                        return form;
                    }
                };
                
                // Add ergon state API to component
                component.ergonState = ergonStateApi;
                
                return ergonStateApi;
            }
        };
    }
    
    /**
     * Initialize Ergon state lifecycle management
     * @private
     */
    _initErgonStateLifecycle() {
        // Add to the existing lifecycle utilities
        const lifecycle = window.tektonUI.componentUtils.lifecycle || {};
        
        /**
         * Register a state effect that runs when specific agent state changes
         * 
         * @param {Object} component - The component context
         * @param {Array|string} stateKeys - Agent state keys to watch
         * @param {Function} effectFn - Effect function to run
         * @param {Object} options - Effect options
         */
        lifecycle.registerAgentStateEffect = function(component, stateKeys, effectFn, options = {}) {
            if (!component.ergonState) {
                console.error('[ComponentErgonState] Component not connected to Ergon state');
                return;
            }
            
            const keys = Array.isArray(stateKeys) ? stateKeys : [stateKeys];
            
            // Run effect immediately if requested
            if (options.runImmediately) {
                try {
                    effectFn(component.ergonState.getAgentState(), {});
                } catch (error) {
                    console.error('[ComponentErgonState] Error in immediate agent state effect:', error);
                }
            }
            
            // Subscribe to state changes
            const subscription = component.ergonState.subscribeAgentState((changes, state) => {
                try {
                    effectFn(state, changes);
                } catch (error) {
                    console.error('[ComponentErgonState] Error in agent state effect:', error);
                }
            }, { keys });
            
            // No need to manually register cleanup as subscribe already does this
            return subscription;
        };
        
        /**
         * Register a state effect that runs when specific execution state changes
         * 
         * @param {Object} component - The component context
         * @param {Array|string} stateKeys - Execution state keys to watch
         * @param {Function} effectFn - Effect function to run
         * @param {Object} options - Effect options
         */
        lifecycle.registerExecutionStateEffect = function(component, stateKeys, effectFn, options = {}) {
            if (!component.ergonState) {
                console.error('[ComponentErgonState] Component not connected to Ergon state');
                return;
            }
            
            const keys = Array.isArray(stateKeys) ? stateKeys : [stateKeys];
            
            // Run effect immediately if requested
            if (options.runImmediately) {
                try {
                    effectFn(component.ergonState.getExecutionState(), {});
                } catch (error) {
                    console.error('[ComponentErgonState] Error in immediate execution state effect:', error);
                }
            }
            
            // Subscribe to state changes
            const subscription = component.ergonState.subscribeExecutionState((changes, state) => {
                try {
                    effectFn(state, changes);
                } catch (error) {
                    console.error('[ComponentErgonState] Error in execution state effect:', error);
                }
            }, { keys });
            
            // No need to manually register cleanup as subscribe already does this
            return subscription;
        };
        
        /**
         * Register a state effect that runs when specific settings change
         * 
         * @param {Object} component - The component context
         * @param {Array|string} stateKeys - Settings keys to watch
         * @param {Function} effectFn - Effect function to run
         * @param {Object} options - Effect options
         */
        lifecycle.registerSettingsEffect = function(component, stateKeys, effectFn, options = {}) {
            if (!component.ergonState) {
                console.error('[ComponentErgonState] Component not connected to Ergon state');
                return;
            }
            
            const keys = Array.isArray(stateKeys) ? stateKeys : [stateKeys];
            
            // Run effect immediately if requested
            if (options.runImmediately) {
                try {
                    effectFn(component.ergonState.getSettings(), {});
                } catch (error) {
                    console.error('[ComponentErgonState] Error in immediate settings effect:', error);
                }
            }
            
            // Subscribe to state changes
            const subscription = component.ergonState.subscribeSettings((changes, state) => {
                try {
                    effectFn(state, changes);
                } catch (error) {
                    console.error('[ComponentErgonState] Error in settings effect:', error);
                }
            }, { keys });
            
            // No need to manually register cleanup as subscribe already does this
            return subscription;
        };
        
        // Update the lifecycle utilities
        window.tektonUI.componentUtils.lifecycle = lifecycle;
    }
}

// Initialize the component Ergon state utilities on script load
document.addEventListener('DOMContentLoaded', () => {
    // Create and initialize the component Ergon state utilities
    window.componentErgonStateUtils = new ComponentErgonStateUtils().init();
});