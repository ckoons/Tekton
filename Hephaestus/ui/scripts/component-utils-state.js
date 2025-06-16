/**
 * Component State Utilities
 * 
 * Provides component-specific state management utilities that integrate
 * with the StateManager system. These utilities make it easy for components
 * to work with state in a standardized way.
 */

class ComponentStateUtils {
    constructor() {
        this.initialized = false;
    }
    
    /**
     * Initialize the component state utilities
     */
    init() {
        if (this.initialized) return this;
        
        // Create utility namespace in global tektonUI
        window.tektonUI = window.tektonUI || {};
        window.tektonUI.componentState = {};
        
        // Initialize all state utilities
        this._initComponentStateSystem();
        this._initStateLifecycle();
        
        this.initialized = true;
        console.log('Component state utilities initialized');
        
        return this;
    }
    
    /**
     * Initialize the component state system
     */
    _initComponentStateSystem() {
        window.tektonUI.componentState.utils = {
            /**
             * Connect a component to the state manager
             * 
             * @param {Object} component - The component context
             * @param {Object} options - State options
             * @param {string} options.namespace - Component state namespace
             * @param {Object} options.initialState - Initial state values
             * @param {Array} options.sharedKeys - Keys to share with global state
             * @param {boolean} options.persist - Whether to persist state
             * @param {string} options.persistenceType - Storage type (localStorage or sessionStorage)
             * @returns {Object} - State utilities for the component
             */
            connect: function(component, options = {}) {
                const stateManager = window.tektonUI.stateManager;
                if (!stateManager) {
                    console.error('[ComponentState] StateManager not initialized');
                    return null;
                }
                
                // Generate component ID if not present
                component.stateId = component.stateId || component.id || `component-${Math.random().toString(36).substring(2, 9)}`;
                
                // Determine namespace
                const namespace = options.namespace || component.stateId;
                
                // Initialize state with defaults
                if (options.initialState) {
                    stateManager.setState(namespace, options.initialState, { silent: true });
                }
                
                // Configure persistence if requested
                if (options.persist) {
                    stateManager.configurePersistence(namespace, {
                        type: options.persistenceType || 'localStorage',
                        key: `tekton_${namespace}_state`,
                        exclude: options.excludeFromPersistence || []
                    });
                }
                
                // Set up shared state if requested
                if (options.sharedKeys && options.sharedKeys.length > 0) {
                    // Initialize shared state with current values
                    const currentState = stateManager.getState(namespace);
                    const sharedState = {};
                    
                    options.sharedKeys.forEach(key => {
                        if (currentState[key] !== undefined) {
                            sharedState[key] = currentState[key];
                        }
                    });
                    
                    // Share current values with global namespace
                    if (Object.keys(sharedState).length > 0) {
                        stateManager.setState('global', sharedState, { silent: true });
                    }
                    
                    // Subscribe to component namespace changes to update global
                    stateManager.subscribe(namespace, (changes) => {
                        const sharedChanges = {};
                        let hasSharedChanges = false;
                        
                        // Check if any shared keys changed
                        Object.keys(changes).forEach(key => {
                            if (options.sharedKeys.includes(key)) {
                                sharedChanges[key] = changes[key];
                                hasSharedChanges = true;
                            }
                        });
                        
                        // Update global state if shared keys changed
                        if (hasSharedChanges) {
                            stateManager.setState('global', sharedChanges);
                        }
                    });
                    
                    // Subscribe to global namespace for shared keys
                    stateManager.subscribe('global', (changes) => {
                        const relevantChanges = {};
                        let hasRelevantChanges = false;
                        
                        // Check if any relevant shared keys changed
                        Object.keys(changes).forEach(key => {
                            if (options.sharedKeys.includes(key)) {
                                relevantChanges[key] = changes[key];
                                hasRelevantChanges = true;
                            }
                        });
                        
                        // Update component state if relevant keys changed
                        if (hasRelevantChanges) {
                            stateManager.setState(namespace, relevantChanges);
                        }
                    }, { keys: options.sharedKeys });
                }
                
                // Create state API for component
                const stateApi = {
                    /**
                     * Get the component's state
                     * 
                     * @param {string} key - Optional state key to get
                     * @returns {*} - The requested state
                     */
                    get: function(key = null) {
                        return stateManager.getState(namespace, key);
                    },
                    
                    /**
                     * Set component state
                     * 
                     * @param {Object|string} keyOrObject - State key or object with updates
                     * @param {*} value - Value to set (if key is a string)
                     * @param {Object} options - Update options
                     * @returns {Object} - Updated state
                     */
                    set: function(keyOrObject, value, options = {}) {
                        // Handle both object and key/value formats
                        let updates = {};
                        
                        if (typeof keyOrObject === 'string') {
                            updates[keyOrObject] = value;
                        } else if (typeof keyOrObject === 'object') {
                            updates = keyOrObject;
                            options = value || {};
                        }
                        
                        return stateManager.setState(namespace, updates, options);
                    },
                    
                    /**
                     * Subscribe to state changes
                     * 
                     * @param {Function} callback - State change callback
                     * @param {Object} options - Subscription options
                     * @returns {string} - Subscription ID
                     */
                    subscribe: function(callback, options = {}) {
                        const subscription = stateManager.subscribe(namespace, callback, options);
                        
                        // Register cleanup to unsubscribe when component unmounts
                        component.utils.lifecycle.registerCleanupTask(component, () => {
                            stateManager.unsubscribe(subscription);
                        });
                        
                        return subscription;
                    },
                    
                    /**
                     * Start a transaction to batch multiple state updates
                     * 
                     * @returns {Function} - Function to commit the transaction
                     */
                    transaction: function() {
                        return stateManager.startTransaction();
                    },
                    
                    /**
                     * Reset state to initial values
                     * 
                     * @param {Object} initialState - State to reset to
                     */
                    reset: function(initialState = {}) {
                        stateManager.resetState(namespace, initialState);
                    },
                    
                    /**
                     * Check if a state key exists
                     * 
                     * @param {string} key - State key
                     * @returns {boolean} - Whether the key exists
                     */
                    has: function(key) {
                        return stateManager.getState(namespace, key) !== undefined;
                    },
                    
                    /**
                     * Create a derived state that depends on other state keys
                     * 
                     * @param {string} key - Derived state key
                     * @param {Array} dependencies - State keys this depends on
                     * @param {Function} computeFn - Function to compute the derived value
                     */
                    derived: function(key, dependencies, computeFn) {
                        stateManager.createDerivedState(namespace, key, dependencies, computeFn);
                    },
                    
                    /**
                     * Create bound handlers that update state when input elements change
                     * 
                     * @param {Object} mappings - Field to state key mappings
                     * @returns {Object} - Bound handlers
                     */
                    bindInputs: function(mappings) {
                        const boundHandlers = {};
                        
                        Object.entries(mappings).forEach(([fieldName, stateKey]) => {
                            // Create event handler for this input
                            boundHandlers[fieldName] = function(event) {
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
                                
                                // Update state
                                stateApi.set(stateKey, value);
                            };
                        });
                        
                        return boundHandlers;
                    },
                    
                    /**
                     * Toggle a boolean state value
                     * 
                     * @param {string} key - State key to toggle
                     * @returns {boolean} - The new value
                     */
                    toggle: function(key) {
                        const currentValue = stateApi.get(key) || false;
                        const newValue = !currentValue;
                        stateApi.set(key, newValue);
                        return newValue;
                    },
                    
                    /**
                     * Clear or remove a state key
                     * 
                     * @param {string} key - State key to clear
                     */
                    clear: function(key) {
                        const update = {};
                        update[key] = undefined;
                        stateManager.setState(namespace, update);
                    },
                    
                    /**
                     * Get the current namespace
                     * 
                     * @returns {string} - Component namespace
                     */
                    getNamespace: function() {
                        return namespace;
                    }
                };
                
                // Add state API to component
                component.state = stateApi;
                
                return stateApi;
            }
        };
    }
    
    /**
     * Initialize state lifecycle management
     */
    _initStateLifecycle() {
        // Add to the existing lifecycle utilities
        const lifecycle = window.tektonUI.componentUtils.lifecycle || {};
        
        /**
         * Register a state effect that runs when specific state changes
         * 
         * @param {Object} component - The component context
         * @param {Array|string} stateKeys - State keys to watch
         * @param {Function} effectFn - Effect function to run
         * @param {Object} options - Effect options
         */
        lifecycle.registerStateEffect = function(component, stateKeys, effectFn, options = {}) {
            if (!component.state) {
                console.error('[ComponentState] Component not connected to state');
                return;
            }
            
            const keys = Array.isArray(stateKeys) ? stateKeys : [stateKeys];
            
            // Run effect immediately if requested
            if (options.runImmediately) {
                try {
                    effectFn(component.state.get(), {});
                } catch (error) {
                    console.error('[ComponentState] Error in immediate state effect:', error);
                }
            }
            
            // Subscribe to state changes
            const subscription = component.state.subscribe((changes, state) => {
                try {
                    effectFn(state, changes);
                } catch (error) {
                    console.error('[ComponentState] Error in state effect:', error);
                }
            }, { keys });
            
            // No need to manually register cleanup as subscribe already does this
            return subscription;
        };
        
        /**
         * Register a state effect that runs only once when mounted
         * 
         * @param {Object} component - The component context
         * @param {Function} effectFn - Effect function to run
         */
        lifecycle.registerMountEffect = function(component, effectFn) {
            if (!component.state) {
                console.error('[ComponentState] Component not connected to state');
                return;
            }
            
            try {
                effectFn(component.state.get());
            } catch (error) {
                console.error('[ComponentState] Error in mount effect:', error);
            }
        };
        
        /**
         * Register an effect that runs when component is unmounted
         * 
         * @param {Object} component - The component context
         * @param {Function} effectFn - Effect function to run
         */
        lifecycle.registerUnmountEffect = function(component, effectFn) {
            component.utils.lifecycle.registerCleanupTask(component, () => {
                try {
                    effectFn(component.state ? component.state.get() : {});
                } catch (error) {
                    console.error('[ComponentState] Error in unmount effect:', error);
                }
            });
        };
        
        // Update the lifecycle utilities
        window.tektonUI.componentUtils.lifecycle = lifecycle;
    }
}

// Initialize the component state utilities on script load
document.addEventListener('DOMContentLoaded', () => {
    // Create and initialize the component state utilities
    window.componentStateUtils = new ComponentStateUtils().init();
});