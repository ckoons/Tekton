/**
 * StateManager.js
 * 
 * Core state management implementation for Tekton components.
 * Provides a centralized, subscription-based state management system 
 * with support for namespaces, persistence, and debugging.
 */

class StateManager {
    constructor() {
        this.state = {};
        this.subscribers = {};
        this.history = {};
        this.persistenceOptions = {};
        this.initialized = false;
        this.debug = false;
        this.namespaces = new Set();
        this.transactionInProgress = false;
        this.transactionChanges = {};
        this.defaultNamespace = 'global';
    }

    /**
     * Initialize the state manager
     * 
     * @param {Object} options - Configuration options
     * @param {boolean} options.debug - Enable debug mode
     * @param {Array} options.initialState - Initial state objects to load
     * @returns {StateManager} - The state manager instance
     */
    init(options = {}) {
        if (this.initialized) return this;
        
        // Register in window.tektonUI
        if (!window.tektonUI) {
            window.tektonUI = {};
        }

        window.tektonUI.stateManager = this;
        
        // Set configuration options
        this.debug = options.debug || false;
        
        // Load initial state if provided
        if (options.initialState) {
            options.initialState.forEach(stateObj => {
                const namespace = stateObj.namespace || this.defaultNamespace;
                this.setState(namespace, stateObj.data, { silent: true });
            });
        }
        
        // Initialize with restored persisted state
        this._restorePersistedState();
        
        this.initialized = true;
        this.log('StateManager initialized', this.state);
        
        return this;
    }
    
    /**
     * Get state from a namespace
     * 
     * @param {string} namespace - State namespace
     * @param {string} key - Optional specific key to retrieve
     * @returns {*} - The requested state
     */
    getState(namespace = this.defaultNamespace, key = null) {
        // Create namespace if it doesn't exist
        if (!this.state[namespace]) {
            this.state[namespace] = {};
            this.namespaces.add(namespace);
        }
        
        // Return the entire namespace if no key specified
        if (key === null) {
            // Return a deep clone to prevent direct state mutations
            return this._deepClone(this.state[namespace]);
        }
        
        // Handle dot notation for nested state
        if (key.includes('.')) {
            return this._getNestedState(this.state[namespace], key);
        }
        
        // Return a deep clone of the requested key
        return this._deepClone(this.state[namespace][key]);
    }
    
    /**
     * Set state for a namespace
     * 
     * @param {string} namespace - State namespace
     * @param {Object} updates - State updates
     * @param {Object} options - Update options
     * @param {boolean} options.silent - Don't trigger subscribers
     * @param {boolean} options.persist - Persist this state change
     * @returns {Object} - The updated state
     */
    setState(namespace = this.defaultNamespace, updates, options = {}) {
        // Create namespace if it doesn't exist
        if (!this.state[namespace]) {
            this.state[namespace] = {};
            this.namespaces.add(namespace);
        }
        
        // Keep track of what actually changed
        const changes = {};
        let hasChanges = false;
        
        // Process updates
        Object.entries(updates).forEach(([key, value]) => {
            // Handle dot notation for nested state
            if (key.includes('.')) {
                const didChange = this._setNestedState(namespace, key, value);
                if (didChange) {
                    changes[key] = value;
                    hasChanges = true;
                }
            } else {
                // Only consider it a change if value is different
                if (!this._isEqual(this.state[namespace][key], value)) {
                    // Add to change set before updating state
                    changes[key] = value;
                    
                    // Update the state
                    this.state[namespace][key] = this._deepClone(value);
                    hasChanges = true;
                }
            }
        });
        
        // If we're in a transaction, store changes for later notification
        if (this.transactionInProgress) {
            if (hasChanges) {
                if (!this.transactionChanges[namespace]) {
                    this.transactionChanges[namespace] = {};
                }
                
                // Merge changes into transaction changes
                Object.assign(this.transactionChanges[namespace], changes);
            }
            
            return this._deepClone(this.state[namespace]);
        }
        
        // No need to proceed if nothing changed or silent option is set
        if (!hasChanges || options.silent) {
            return this._deepClone(this.state[namespace]);
        }
        
        // Record in history for debugging
        if (this.debug) {
            this._recordHistory(namespace, changes);
        }
        
        // Notify subscribers
        this._notifySubscribers(namespace, changes);
        
        // Handle persistence if enabled for this namespace
        if (options.persist || this.persistenceOptions[namespace]) {
            this._persistState(namespace);
        }
        
        return this._deepClone(this.state[namespace]);
    }
    
    /**
     * Start a transaction to batch multiple state updates
     * 
     * @returns {function} - Function to commit the transaction
     */
    startTransaction() {
        if (this.transactionInProgress) {
            this.log('Transaction already in progress', 'warning');
            return () => this.commitTransaction();
        }
        
        this.transactionInProgress = true;
        this.transactionChanges = {};
        this.log('Transaction started');
        
        return () => this.commitTransaction();
    }
    
    /**
     * Commit a transaction and notify subscribers
     */
    commitTransaction() {
        if (!this.transactionInProgress) {
            this.log('No transaction in progress', 'warning');
            return;
        }
        
        this.log('Committing transaction', this.transactionChanges);
        
        // Notify subscribers for each namespace with changes
        Object.entries(this.transactionChanges).forEach(([namespace, changes]) => {
            // Record in history
            if (this.debug) {
                this._recordHistory(namespace, changes);
            }
            
            // Notify subscribers
            this._notifySubscribers(namespace, changes);
            
            // Handle persistence
            if (this.persistenceOptions[namespace]) {
                this._persistState(namespace);
            }
        });
        
        // Clear the transaction
        this.transactionInProgress = false;
        this.transactionChanges = {};
    }
    
    /**
     * Reset a namespace to an empty state or specified initialState
     * 
     * @param {string} namespace - State namespace to reset
     * @param {Object} initialState - Optional initial state to set
     * @param {Object} options - Reset options
     */
    resetState(namespace = this.defaultNamespace, initialState = {}, options = {}) {
        // Reset the state
        this.state[namespace] = this._deepClone(initialState);
        
        // Create history entry for debugging
        if (this.debug) {
            this._recordHistory(namespace, { __reset: true, initialState });
        }
        
        // Notify subscribers unless silent
        if (!options.silent) {
            this._notifySubscribers(namespace, { __reset: true });
        }
        
        // Update persistence if enabled
        if (this.persistenceOptions[namespace]) {
            this._persistState(namespace);
        }
    }
    
    /**
     * Subscribe to state changes for a namespace
     * 
     * @param {string} namespace - State namespace to subscribe to
     * @param {Function} callback - Callback function
     * @param {Object} options - Subscription options
     * @param {Array} options.keys - Specific keys to subscribe to
     * @returns {string} - Subscription ID
     */
    subscribe(namespace = this.defaultNamespace, callback, options = {}) {
        if (typeof callback !== 'function') {
            this.log('Callback must be a function', 'error');
            return null;
        }
        
        // Create subscribers array for namespace if it doesn't exist
        if (!this.subscribers[namespace]) {
            this.subscribers[namespace] = [];
        }
        
        // Generate a unique subscription ID
        const id = this._generateId();
        
        // Create subscription object
        const subscription = {
            id,
            callback,
            keys: options.keys || null, // If null, subscribe to all changes
            options
        };
        
        // Add to subscribers
        this.subscribers[namespace].push(subscription);
        this.log(`Subscribed to ${namespace} state with ID ${id}`);
        
        // Return subscription ID for unsubscribing
        return id;
    }
    
    /**
     * Unsubscribe from state changes
     * 
     * @param {string} id - Subscription ID
     * @returns {boolean} - Success status
     */
    unsubscribe(id) {
        let found = false;
        
        // Search all namespaces for the subscription
        Object.keys(this.subscribers).forEach(namespace => {
            const index = this.subscribers[namespace].findIndex(sub => sub.id === id);
            if (index !== -1) {
                this.subscribers[namespace].splice(index, 1);
                found = true;
                this.log(`Unsubscribed from ${namespace} state with ID ${id}`);
            }
        });
        
        return found;
    }
    
    /**
     * Configure state persistence for a namespace
     * 
     * @param {string} namespace - State namespace
     * @param {Object} options - Persistence options
     * @param {string} options.type - Persistence type (localStorage, sessionStorage)
     * @param {string} options.key - Storage key
     * @param {Array} options.include - Keys to include (null for all)
     * @param {Array} options.exclude - Keys to exclude
     */
    configurePersistence(namespace = this.defaultNamespace, options) {
        if (!options || !options.type) {
            // Remove persistence if no valid options
            delete this.persistenceOptions[namespace];
            return;
        }
        
        // Validate storage type
        if (!['localStorage', 'sessionStorage'].includes(options.type)) {
            this.log(`Invalid storage type: ${options.type}`, 'error');
            return;
        }
        
        // Set persistence options
        this.persistenceOptions[namespace] = {
            type: options.type,
            key: options.key || `tekton_state_${namespace}`,
            include: options.include || null, // If null, include all keys
            exclude: options.exclude || []
        };
        
        this.log(`Configured persistence for ${namespace} state`, this.persistenceOptions[namespace]);
        
        // Immediately persist current state
        this._persistState(namespace);
    }
    
    /**
     * Enable or disable debug mode
     * 
     * @param {boolean} enabled - Whether debug mode should be enabled
     */
    setDebug(enabled) {
        this.debug = enabled;
        this.log(`Debug mode ${enabled ? 'enabled' : 'disabled'}`);
        
        // Clear history if disabling debug
        if (!enabled) {
            this.history = {};
        }
    }
    
    /**
     * Get a snapshot of the current state
     * 
     * @returns {Object} - Complete state snapshot
     */
    getSnapshot() {
        return this._deepClone(this.state);
    }
    
    /**
     * Get history for a namespace
     * 
     * @param {string} namespace - State namespace
     * @param {number} limit - Maximum number of history entries to return
     * @returns {Array} - History entries
     */
    getHistory(namespace = this.defaultNamespace, limit = null) {
        if (!this.debug) {
            this.log('History is only available in debug mode', 'warning');
            return [];
        }
        
        const history = this.history[namespace] || [];
        return limit ? history.slice(-limit) : history;
    }
    
    /**
     * Import state for a namespace
     * 
     * @param {string} namespace - State namespace
     * @param {Object} state - State to import
     * @param {Object} options - Import options
     */
    importState(namespace = this.defaultNamespace, state, options = {}) {
        // Completely replace the namespace state
        this.state[namespace] = this._deepClone(state);
        
        // Record in history
        if (this.debug) {
            this._recordHistory(namespace, { __imported: true });
        }
        
        // Notify subscribers
        if (!options.silent) {
            this._notifySubscribers(namespace, { __imported: true });
        }
        
        // Update persistence if enabled
        if (this.persistenceOptions[namespace]) {
            this._persistState(namespace);
        }
    }
    
    /**
     * Export state for a namespace
     * 
     * @param {string} namespace - State namespace
     * @returns {Object} - Exported state
     */
    exportState(namespace = this.defaultNamespace) {
        return this._deepClone(this.state[namespace] || {});
    }
    
    /**
     * Get a list of all registered namespaces
     * 
     * @returns {Array} - Array of namespace names
     */
    getNamespaces() {
        return Array.from(this.namespaces);
    }
    
    /**
     * Create a derived state that depends on other state keys
     * 
     * @param {string} namespace - State namespace
     * @param {string} key - Derived state key
     * @param {Array} dependencies - State keys this depends on
     * @param {Function} computeFn - Function to compute the derived value
     */
    createDerivedState(namespace = this.defaultNamespace, key, dependencies, computeFn) {
        if (typeof computeFn !== 'function') {
            this.log('Compute function must be a function', 'error');
            return;
        }
        
        // Compute initial value
        const initialValue = computeFn(this.getState(namespace));
        this.setState(namespace, { [key]: initialValue }, { silent: true });
        
        // Subscribe to dependencies
        this.subscribe(namespace, (changes, state) => {
            // Only recompute if any dependencies have changed
            const shouldRecompute = dependencies.some(dep => Object.keys(changes).includes(dep));
            
            if (shouldRecompute) {
                const newValue = computeFn(state);
                this.setState(namespace, { [key]: newValue });
            }
        }, { keys: dependencies });
    }
    
    /* Private methods */
    
    /**
     * Log a message if debug mode is enabled
     * 
     * @param {string} message - Message to log
     * @param {string} level - Log level (log, warn, error)
     * @param {*} data - Additional data to log
     */
    log(message, level = 'log', data) {
        if (!this.debug && level === 'log') return;
        
        const prefix = '[StateManager]';
        
        if (data !== undefined) {
            console[level](prefix, message, data);
        } else {
            console[level](prefix, message);
        }
    }
    
    /**
     * Get nested state using dot notation
     * 
     * @param {Object} state - State object
     * @param {string} path - Dot notation path
     * @returns {*} - Nested state value
     */
    _getNestedState(state, path) {
        const keys = path.split('.');
        let current = state;
        
        for (const key of keys) {
            if (current === undefined || current === null) {
                return undefined;
            }
            current = current[key];
        }
        
        return this._deepClone(current);
    }
    
    /**
     * Set nested state using dot notation
     * 
     * @param {string} namespace - State namespace
     * @param {string} path - Dot notation path
     * @param {*} value - Value to set
     * @returns {boolean} - Whether the state was changed
     */
    _setNestedState(namespace, path, value) {
        const keys = path.split('.');
        const lastKey = keys.pop();
        
        // Start with the namespace state
        let current = this.state[namespace];
        
        // Navigate to the parent object
        for (const key of keys) {
            // Create path if it doesn't exist
            if (current[key] === undefined || current[key] === null || typeof current[key] !== 'object') {
                current[key] = {};
            }
            current = current[key];
        }
        
        // Check if the value is actually changing
        if (!this._isEqual(current[lastKey], value)) {
            current[lastKey] = this._deepClone(value);
            return true;
        }
        
        return false;
    }
    
    /**
     * Notify subscribers of state changes
     * 
     * @param {string} namespace - State namespace
     * @param {Object} changes - State changes
     */
    _notifySubscribers(namespace, changes) {
        if (!this.subscribers[namespace]) return;
        
        const state = this._deepClone(this.state[namespace]);
        
        // Create a set of all changed keys including parent paths
        const changedPathSet = new Set();
        Object.keys(changes).forEach(key => {
            changedPathSet.add(key);
            
            // Add parent paths for nested changes
            if (key.includes('.')) {
                const parts = key.split('.');
                let path = '';
                
                for (let i = 0; i < parts.length - 1; i++) {
                    path = path ? `${path}.${parts[i]}` : parts[i];
                    changedPathSet.add(path);
                }
            }
        });
        
        const changedPaths = Array.from(changedPathSet);
        
        // Notify subscribers
        this.subscribers[namespace].forEach(subscription => {
            let shouldNotify = false;
            
            // Special case for reset and import operations
            if (changes.__reset || changes.__imported) {
                shouldNotify = true;
            } 
            // Check if any of the changed keys match the subscription's keys
            else if (subscription.keys === null) {
                // Null means subscribe to all changes
                shouldNotify = true;
            } else {
                // Check if any subscription keys match changed paths
                shouldNotify = subscription.keys.some(subKey => 
                    changedPaths.some(changedPath => {
                        // Exact match
                        if (subKey === changedPath) return true;
                        
                        // Check if a parent path changed (e.g. sub to 'user' should trigger on 'user.name')
                        if (changedPath.startsWith(`${subKey}.`)) return true;
                        
                        // Check if a child path changed (e.g. sub to 'user.profile' should trigger on 'user')
                        if (subKey.startsWith(`${changedPath}.`)) return true;
                        
                        return false;
                    })
                );
            }
            
            if (shouldNotify) {
                try {
                    subscription.callback(changes, state);
                } catch (error) {
                    this.log(`Error in subscriber callback (ID: ${subscription.id}):`, 'error', error);
                }
            }
        });
    }
    
    /**
     * Record state change in history
     * 
     * @param {string} namespace - State namespace
     * @param {Object} changes - State changes
     */
    _recordHistory(namespace, changes) {
        if (!this.history[namespace]) {
            this.history[namespace] = [];
        }
        
        // Add to history with timestamp
        this.history[namespace].push({
            timestamp: new Date(),
            changes: this._deepClone(changes)
        });
        
        // Trim history if it gets too large
        const maxHistory = 100;
        if (this.history[namespace].length > maxHistory) {
            this.history[namespace] = this.history[namespace].slice(-maxHistory);
        }
    }
    
    /**
     * Persist state to storage
     * 
     * @param {string} namespace - State namespace
     */
    _persistState(namespace) {
        const options = this.persistenceOptions[namespace];
        if (!options) return;
        
        try {
            const storage = window[options.type];
            let stateToStore = this._deepClone(this.state[namespace]);
            
            // Filter state based on include/exclude options
            if (options.include || options.exclude.length > 0) {
                const filteredState = {};
                
                Object.entries(stateToStore).forEach(([key, value]) => {
                    const shouldInclude = 
                        // Include is null (include all) or key is in include list
                        (options.include === null || options.include.includes(key)) && 
                        // Key is not in exclude list
                        !options.exclude.includes(key);
                    
                    if (shouldInclude) {
                        filteredState[key] = value;
                    }
                });
                
                stateToStore = filteredState;
            }
            
            // Store the state as a string
            storage.setItem(options.key, JSON.stringify(stateToStore));
            this.log(`Persisted ${namespace} state to ${options.type}`);
        } catch (error) {
            this.log(`Failed to persist ${namespace} state:`, 'error', error);
        }
    }
    
    /**
     * Restore persisted state
     */
    _restorePersistedState() {
        Object.entries(this.persistenceOptions).forEach(([namespace, options]) => {
            try {
                const storage = window[options.type];
                const storedData = storage.getItem(options.key);
                
                if (storedData) {
                    const parsedData = JSON.parse(storedData);
                    this.setState(namespace, parsedData, { silent: true });
                    this.log(`Restored ${namespace} state from ${options.type}`);
                }
            } catch (error) {
                this.log(`Failed to restore ${namespace} state:`, 'error', error);
            }
        });
    }
    
    /**
     * Deep clone an object to prevent reference issues
     * 
     * @param {*} obj - Object to clone
     * @returns {*} - Cloned object
     */
    _deepClone(obj) {
        if (obj === null || obj === undefined || typeof obj !== 'object') {
            return obj;
        }
        
        try {
            return JSON.parse(JSON.stringify(obj));
        } catch (error) {
            this.log('Failed to deep clone object:', 'error', error);
            
            // Fallback to shallow clone
            return Array.isArray(obj) ? [...obj] : { ...obj };
        }
    }
    
    /**
     * Check if two values are equal
     * 
     * @param {*} a - First value
     * @param {*} b - Second value
     * @returns {boolean} - Whether the values are equal
     */
    _isEqual(a, b) {
        // Handle simple cases
        if (a === b) return true;
        if (a === null || b === null) return a === b;
        if (a === undefined || b === undefined) return a === b;
        
        // Handle different types
        if (typeof a !== typeof b) return false;
        
        // For non-objects, we've already checked equality
        if (typeof a !== 'object') return false;
        
        // Handle arrays
        if (Array.isArray(a) && Array.isArray(b)) {
            if (a.length !== b.length) return false;
            
            // Compare each element
            for (let i = 0; i < a.length; i++) {
                if (!this._isEqual(a[i], b[i])) return false;
            }
            
            return true;
        }
        
        // Handle objects
        if (typeof a === 'object' && typeof b === 'object') {
            const aKeys = Object.keys(a);
            const bKeys = Object.keys(b);
            
            if (aKeys.length !== bKeys.length) return false;
            
            // Check that all keys and values are equal
            return aKeys.every(key => 
                bKeys.includes(key) && this._isEqual(a[key], b[key])
            );
        }
        
        return false;
    }
    
    /**
     * Generate a unique ID
     * 
     * @returns {string} - Unique ID
     */
    _generateId() {
        return Math.random().toString(36).substring(2, 15) + 
               Math.random().toString(36).substring(2, 15);
    }
}

// Create and export the StateManager instance
window.tektonUI = window.tektonUI || {};
window.tektonUI.StateManager = StateManager;

// Export a singleton instance
window.tektonUI.stateManager = new StateManager();

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize with default options
    window.tektonUI.stateManager.init();
});