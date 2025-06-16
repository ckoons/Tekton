/**
 * State Persistence
 * 
 * Provides enhanced persistence capabilities for the Tekton state management system.
 * Supports local storage, session storage, and custom storage adapters.
 */

class StatePersistence {
    constructor() {
        this.initialized = false;
        this.adapters = {};
        this.defaultAdapter = 'localStorage';
    }
    
    /**
     * Initialize the state persistence system
     * 
     * @param {Object} options - Configuration options
     * @returns {StatePersistence} - The persistence instance
     */
    init(options = {}) {
        if (this.initialized) return this;
        
        // Setup namespace in window.tektonUI
        window.tektonUI = window.tektonUI || {};
        window.tektonUI.statePersistence = this;
        
        // Register built-in storage adapters
        this._registerBuiltInAdapters();
        
        // Register custom adapters if provided
        if (options.adapters) {
            Object.entries(options.adapters).forEach(([name, adapter]) => {
                this.registerAdapter(name, adapter);
            });
        }
        
        // Set default adapter if specified
        if (options.defaultAdapter) {
            this.defaultAdapter = options.defaultAdapter;
        }
        
        // Integrate with StateManager
        this._integrateWithStateManager();
        
        this.initialized = true;
        console.log('State persistence initialized');
        
        return this;
    }
    
    /**
     * Register a storage adapter
     * 
     * @param {string} name - Adapter name
     * @param {Object} adapter - Adapter implementation
     */
    registerAdapter(name, adapter) {
        if (!adapter || typeof adapter.get !== 'function' || typeof adapter.set !== 'function') {
            console.error(`[StatePersistence] Invalid adapter: ${name}`);
            return;
        }
        
        this.adapters[name] = adapter;
        console.log(`[StatePersistence] Registered adapter: ${name}`);
    }
    
    /**
     * Save state to persistent storage
     * 
     * @param {string} key - Storage key
     * @param {*} value - Value to store
     * @param {Object} options - Storage options
     * @returns {boolean} - Success status
     */
    save(key, value, options = {}) {
        const adapterName = options.adapter || this.defaultAdapter;
        const adapter = this.adapters[adapterName];
        
        if (!adapter) {
            console.error(`[StatePersistence] Adapter not found: ${adapterName}`);
            return false;
        }
        
        try {
            adapter.set(key, value, options);
            return true;
        } catch (error) {
            console.error(`[StatePersistence] Error saving to ${adapterName}:`, error);
            return false;
        }
    }
    
    /**
     * Load state from persistent storage
     * 
     * @param {string} key - Storage key
     * @param {Object} options - Storage options
     * @returns {*} - Loaded value or null
     */
    load(key, options = {}) {
        const adapterName = options.adapter || this.defaultAdapter;
        const adapter = this.adapters[adapterName];
        
        if (!adapter) {
            console.error(`[StatePersistence] Adapter not found: ${adapterName}`);
            return null;
        }
        
        try {
            return adapter.get(key, options);
        } catch (error) {
            console.error(`[StatePersistence] Error loading from ${adapterName}:`, error);
            return null;
        }
    }
    
    /**
     * Remove state from persistent storage
     * 
     * @param {string} key - Storage key
     * @param {Object} options - Storage options
     * @returns {boolean} - Success status
     */
    remove(key, options = {}) {
        const adapterName = options.adapter || this.defaultAdapter;
        const adapter = this.adapters[adapterName];
        
        if (!adapter) {
            console.error(`[StatePersistence] Adapter not found: ${adapterName}`);
            return false;
        }
        
        try {
            adapter.remove(key, options);
            return true;
        } catch (error) {
            console.error(`[StatePersistence] Error removing from ${adapterName}:`, error);
            return false;
        }
    }
    
    /**
     * Check if a key exists in persistent storage
     * 
     * @param {string} key - Storage key
     * @param {Object} options - Storage options
     * @returns {boolean} - Whether the key exists
     */
    exists(key, options = {}) {
        const adapterName = options.adapter || this.defaultAdapter;
        const adapter = this.adapters[adapterName];
        
        if (!adapter) {
            console.error(`[StatePersistence] Adapter not found: ${adapterName}`);
            return false;
        }
        
        try {
            return adapter.exists ? adapter.exists(key, options) : adapter.get(key, options) !== null;
        } catch (error) {
            console.error(`[StatePersistence] Error checking existence in ${adapterName}:`, error);
            return false;
        }
    }
    
    /**
     * Get all keys in persistent storage
     * 
     * @param {Object} options - Storage options
     * @returns {Array} - Array of keys or empty array
     */
    keys(options = {}) {
        const adapterName = options.adapter || this.defaultAdapter;
        const adapter = this.adapters[adapterName];
        
        if (!adapter) {
            console.error(`[StatePersistence] Adapter not found: ${adapterName}`);
            return [];
        }
        
        try {
            return adapter.keys ? adapter.keys(options) : [];
        } catch (error) {
            console.error(`[StatePersistence] Error getting keys from ${adapterName}:`, error);
            return [];
        }
    }
    
    /**
     * Clear all persisted state for a namespace
     * 
     * @param {string} namespace - State namespace
     * @param {Object} options - Storage options
     * @returns {boolean} - Success status
     */
    clearNamespace(namespace, options = {}) {
        const adapterName = options.adapter || this.defaultAdapter;
        const adapter = this.adapters[adapterName];
        
        if (!adapter) {
            console.error(`[StatePersistence] Adapter not found: ${adapterName}`);
            return false;
        }
        
        try {
            // If adapter has a clearNamespace method, use it
            if (adapter.clearNamespace) {
                return adapter.clearNamespace(namespace, options);
            }
            
            // Otherwise, find and remove all keys for this namespace
            const allKeys = this.keys(options);
            const namespacePrefix = `tekton_${namespace}_`;
            const namespacedKeys = allKeys.filter(key => key.startsWith(namespacePrefix));
            
            namespacedKeys.forEach(key => {
                this.remove(key, options);
            });
            
            return true;
        } catch (error) {
            console.error(`[StatePersistence] Error clearing namespace from ${adapterName}:`, error);
            return false;
        }
    }
    
    /**
     * Export all persisted state
     * 
     * @param {Object} options - Export options
     * @returns {Object} - Exported state
     */
    exportAll(options = {}) {
        const adapterName = options.adapter || this.defaultAdapter;
        const adapter = this.adapters[adapterName];
        
        if (!adapter) {
            console.error(`[StatePersistence] Adapter not found: ${adapterName}`);
            return {};
        }
        
        try {
            // If adapter has an exportAll method, use it
            if (adapter.exportAll) {
                return adapter.exportAll(options);
            }
            
            // Otherwise, build export manually
            const exportData = {};
            const allKeys = this.keys(options);
            
            allKeys.forEach(key => {
                if (key.startsWith('tekton_')) {
                    exportData[key] = this.load(key, options);
                }
            });
            
            return exportData;
        } catch (error) {
            console.error(`[StatePersistence] Error exporting from ${adapterName}:`, error);
            return {};
        }
    }
    
    /**
     * Import state from exported data
     * 
     * @param {Object} data - Data to import
     * @param {Object} options - Import options
     * @returns {boolean} - Success status
     */
    importAll(data, options = {}) {
        const adapterName = options.adapter || this.defaultAdapter;
        const adapter = this.adapters[adapterName];
        
        if (!adapter) {
            console.error(`[StatePersistence] Adapter not found: ${adapterName}`);
            return false;
        }
        
        try {
            // If adapter has an importAll method, use it
            if (adapter.importAll) {
                return adapter.importAll(data, options);
            }
            
            // Otherwise, import each key individually
            Object.entries(data).forEach(([key, value]) => {
                this.save(key, value, options);
            });
            
            return true;
        } catch (error) {
            console.error(`[StatePersistence] Error importing to ${adapterName}:`, error);
            return false;
        }
    }
    
    /**
     * Register default storage adapters
     */
    _registerBuiltInAdapters() {
        // LocalStorage adapter
        this.registerAdapter('localStorage', {
            get: function(key) {
                const data = localStorage.getItem(key);
                if (!data) return null;
                
                try {
                    return JSON.parse(data);
                } catch (error) {
                    return data;
                }
            },
            
            set: function(key, value) {
                localStorage.setItem(key, JSON.stringify(value));
            },
            
            remove: function(key) {
                localStorage.removeItem(key);
            },
            
            exists: function(key) {
                return localStorage.getItem(key) !== null;
            },
            
            keys: function() {
                return Object.keys(localStorage).filter(key => key.startsWith('tekton_'));
            },
            
            clearNamespace: function(namespace) {
                const namespacePrefix = `tekton_${namespace}_`;
                const keysToRemove = [];
                
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key.startsWith(namespacePrefix)) {
                        keysToRemove.push(key);
                    }
                }
                
                keysToRemove.forEach(key => localStorage.removeItem(key));
                return true;
            }
        });
        
        // SessionStorage adapter
        this.registerAdapter('sessionStorage', {
            get: function(key) {
                const data = sessionStorage.getItem(key);
                if (!data) return null;
                
                try {
                    return JSON.parse(data);
                } catch (error) {
                    return data;
                }
            },
            
            set: function(key, value) {
                sessionStorage.setItem(key, JSON.stringify(value));
            },
            
            remove: function(key) {
                sessionStorage.removeItem(key);
            },
            
            exists: function(key) {
                return sessionStorage.getItem(key) !== null;
            },
            
            keys: function() {
                return Object.keys(sessionStorage).filter(key => key.startsWith('tekton_'));
            },
            
            clearNamespace: function(namespace) {
                const namespacePrefix = `tekton_${namespace}_`;
                const keysToRemove = [];
                
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    if (key.startsWith(namespacePrefix)) {
                        keysToRemove.push(key);
                    }
                }
                
                keysToRemove.forEach(key => sessionStorage.removeItem(key));
                return true;
            }
        });
        
        // Memory adapter (for testing and non-persistent storage)
        this.registerAdapter('memory', {
            _storage: {},
            
            get: function(key) {
                return this._storage[key] || null;
            },
            
            set: function(key, value) {
                this._storage[key] = value;
            },
            
            remove: function(key) {
                delete this._storage[key];
            },
            
            exists: function(key) {
                return Object.prototype.hasOwnProperty.call(this._storage, key);
            },
            
            keys: function() {
                return Object.keys(this._storage).filter(key => key.startsWith('tekton_'));
            },
            
            clearNamespace: function(namespace) {
                const namespacePrefix = `tekton_${namespace}_`;
                Object.keys(this._storage).forEach(key => {
                    if (key.startsWith(namespacePrefix)) {
                        delete this._storage[key];
                    }
                });
                return true;
            },
            
            clearAll: function() {
                this._storage = {};
                return true;
            }
        });
        
        // Cookie adapter
        this.registerAdapter('cookie', {
            get: function(key) {
                const value = document.cookie.match('(^|;)\\s*' + key + '\\s*=\\s*([^;]+)');
                if (!value) return null;
                
                try {
                    return JSON.parse(decodeURIComponent(value.pop()));
                } catch (error) {
                    return decodeURIComponent(value.pop());
                }
            },
            
            set: function(key, value, options = {}) {
                const expires = options.expires || 365; // Default to 1 year
                const date = new Date();
                date.setTime(date.getTime() + (expires * 24 * 60 * 60 * 1000));
                
                const cookieValue = encodeURIComponent(JSON.stringify(value));
                const cookieString = `${key}=${cookieValue}; expires=${date.toUTCString()}; path=/`;
                
                document.cookie = cookieString;
            },
            
            remove: function(key) {
                document.cookie = `${key}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
            },
            
            exists: function(key) {
                return document.cookie.match('(^|;)\\s*' + key + '\\s*=\\s*([^;]+)') !== null;
            },
            
            keys: function() {
                return document.cookie
                    .split(';')
                    .map(cookie => cookie.trim().split('=')[0])
                    .filter(key => key.startsWith('tekton_'));
            }
        });
    }
    
    /**
     * Integrate with the StateManager to provide enhanced persistence
     */
    _integrateWithStateManager() {
        const stateManager = window.tektonUI && window.tektonUI.stateManager;
        if (!stateManager) {
            console.warn('[StatePersistence] StateManager not found for integration');
            return;
        }
        
        // Replace StateManager's internal persistence methods with enhanced versions
        const originalPersist = stateManager._persistState;
        const originalRestore = stateManager._restorePersistedState;
        const self = this;
        
        // Enhanced persist state method
        stateManager._persistState = function(namespace) {
            const options = this.persistenceOptions[namespace];
            if (!options) return;
            
            try {
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
                
                // Use persistence adapter
                self.save(options.key, stateToStore, { adapter: options.type });
                this.log(`Persisted ${namespace} state to ${options.type}`);
            } catch (error) {
                this.log(`Failed to persist ${namespace} state:`, 'error', error);
            }
        };
        
        // Enhanced restore state method
        stateManager._restorePersistedState = function() {
            Object.entries(this.persistenceOptions).forEach(([namespace, options]) => {
                try {
                    const storedData = self.load(options.key, { adapter: options.type });
                    
                    if (storedData) {
                        this.setState(namespace, storedData, { silent: true });
                        this.log(`Restored ${namespace} state from ${options.type}`);
                    }
                } catch (error) {
                    this.log(`Failed to restore ${namespace} state:`, 'error', error);
                }
            });
        };
        
        // Enhanced configure persistence method with additional options
        const originalConfigure = stateManager.configurePersistence;
        stateManager.configurePersistence = function(namespace, options) {
            if (!options || !options.type) {
                // Remove persistence if no valid options
                delete this.persistenceOptions[namespace];
                return;
            }
            
            // Check if the adapter exists
            if (!self.adapters[options.type]) {
                this.log(`Invalid storage type: ${options.type}`, 'error');
                return;
            }
            
            // Set persistence options
            this.persistenceOptions[namespace] = {
                type: options.type,
                key: options.key || `tekton_state_${namespace}`,
                include: options.include || null, // If null, include all keys
                exclude: options.exclude || [],
                // Add extra options for enhanced adapters
                expires: options.expires,
                compress: options.compress || false,
                encrypt: options.encrypt || false
            };
            
            this.log(`Configured persistence for ${namespace} state`, this.persistenceOptions[namespace]);
            
            // Immediately persist current state
            this._persistState(namespace);
        };
        
        // Add new methods to StateManager
        
        /**
         * Clear persisted state for a namespace
         * 
         * @param {string} namespace - State namespace
         */
        stateManager.clearPersistedState = function(namespace) {
            const options = this.persistenceOptions[namespace];
            if (!options) {
                this.log(`No persistence configured for ${namespace}`, 'warning');
                return;
            }
            
            self.remove(options.key, { adapter: options.type });
            this.log(`Cleared persisted state for ${namespace}`);
        };
        
        /**
         * Export all persisted state
         * 
         * @returns {Object} - Exported state
         */
        stateManager.exportPersistedState = function() {
            const exportData = {};
            
            Object.entries(this.persistenceOptions).forEach(([namespace, options]) => {
                const data = self.load(options.key, { adapter: options.type });
                if (data) {
                    exportData[namespace] = data;
                }
            });
            
            return exportData;
        };
        
        /**
         * Import persisted state
         * 
         * @param {Object} data - Exported state data
         * @param {boolean} applyToState - Whether to apply imported data to current state
         */
        stateManager.importPersistedState = function(data, applyToState = true) {
            Object.entries(data).forEach(([namespace, state]) => {
                // Create persistence options if they don't exist
                if (!this.persistenceOptions[namespace]) {
                    this.persistenceOptions[namespace] = {
                        type: self.defaultAdapter,
                        key: `tekton_state_${namespace}`,
                        include: null,
                        exclude: []
                    };
                }
                
                const options = this.persistenceOptions[namespace];
                
                // Save to persistence adapter
                self.save(options.key, state, { adapter: options.type });
                
                // Apply to current state if requested
                if (applyToState) {
                    this.setState(namespace, state, { silent: true });
                }
            });
            
            this.log('Imported persisted state data');
        };
    }
}

// Create and export the StatePersistence instance
window.tektonUI = window.tektonUI || {};
window.tektonUI.StatePersistence = StatePersistence;

// Export a singleton instance
window.tektonUI.statePersistence = new StatePersistence();

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize with default options
    window.tektonUI.statePersistence.init();
});