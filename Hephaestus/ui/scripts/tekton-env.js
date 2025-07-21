/**
 * Tekton Environment - JavaScript equivalent of shared/env.py
 * 
 * Provides a unified way to access environment variables in Tekton UI,
 * with support for defaults and type conversion.
 * 
 * Examples:
 *     const port = TektonEnviron.get("HERMES_PORT", 8301);
 *     const debug = TektonEnviron.getBoolean("DEBUG", false);
 *     const timeout = TektonEnviron.getInt("TIMEOUT", 30);
 */

console.log('[FILE_TRACE] Loading: tekton-env.js');

window.TektonEnviron = {
    /**
     * Get an environment variable value with optional default.
     * Checks window object for the variable.
     * 
     * @param {string} key - Environment variable name
     * @param {*} defaultValue - Default value if not found
     * @returns {*} The environment value or default
     */
    get(key, defaultValue = null) {
        // Check window object for the variable
        const value = window[key];
        
        // Return value if defined (including empty strings)
        if (value !== undefined) {
            return value;
        }
        
        // Check localStorage as fallback (for persistent config)
        try {
            const stored = localStorage.getItem(`TEKTON_${key}`);
            if (stored !== null) {
                return stored;
            }
        } catch (e) {
            // localStorage might not be available
        }
        
        return defaultValue;
    },
    
    /**
     * Get an environment variable as integer.
     * 
     * @param {string} key - Environment variable name
     * @param {number} defaultValue - Default value if not found or invalid
     * @returns {number} The integer value
     */
    getInt(key, defaultValue = 0) {
        const value = this.get(key);
        if (value === null || value === undefined) {
            return defaultValue;
        }
        
        const parsed = parseInt(value, 10);
        return isNaN(parsed) ? defaultValue : parsed;
    },
    
    /**
     * Get an environment variable as float.
     * 
     * @param {string} key - Environment variable name
     * @param {number} defaultValue - Default value if not found or invalid
     * @returns {number} The float value
     */
    getFloat(key, defaultValue = 0.0) {
        const value = this.get(key);
        if (value === null || value === undefined) {
            return defaultValue;
        }
        
        const parsed = parseFloat(value);
        return isNaN(parsed) ? defaultValue : parsed;
    },
    
    /**
     * Get an environment variable as boolean.
     * True values: "true", "1", "yes", "on" (case insensitive)
     * 
     * @param {string} key - Environment variable name
     * @param {boolean} defaultValue - Default value if not found
     * @returns {boolean} The boolean value
     */
    getBoolean(key, defaultValue = false) {
        const value = this.get(key);
        if (value === null || value === undefined) {
            return defaultValue;
        }
        
        // Handle boolean type directly
        if (typeof value === 'boolean') {
            return value;
        }
        
        // Handle string values
        const strValue = String(value).toLowerCase().trim();
        return ['true', '1', 'yes', 'on'].includes(strValue);
    },
    
    /**
     * Set an environment variable in the window object.
     * Also persists to localStorage if available.
     * 
     * @param {string} key - Environment variable name
     * @param {*} value - Value to set
     */
    set(key, value) {
        window[key] = value;
        
        // Try to persist to localStorage
        try {
            localStorage.setItem(`TEKTON_${key}`, String(value));
        } catch (e) {
            // localStorage might not be available
        }
    },
    
    /**
     * Check if an environment variable is defined.
     * 
     * @param {string} key - Environment variable name
     * @returns {boolean} True if defined
     */
    has(key) {
        return window[key] !== undefined || 
               (typeof localStorage !== 'undefined' && 
                localStorage.getItem(`TEKTON_${key}`) !== null);
    },
    
    /**
     * Get all Tekton-related environment variables.
     * 
     * @returns {Object} Object with all Tekton env vars
     */
    getAll() {
        const env = {};
        
        // Get from window object
        for (const key in window) {
            if (key.includes('TEKTON') || key.includes('_PORT') || 
                key.includes('_HOST') || key.includes('_URL')) {
                env[key] = window[key];
            }
        }
        
        // Get from localStorage
        try {
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && key.startsWith('TEKTON_')) {
                    const envKey = key.replace('TEKTON_', '');
                    if (!env[envKey]) {
                        env[envKey] = localStorage.getItem(key);
                    }
                }
            }
        } catch (e) {
            // localStorage might not be available
        }
        
        return env;
    },
    
    /**
     * Load environment variables from a configuration object.
     * Useful for initializing from a config file or API response.
     * 
     * @param {Object} config - Configuration object
     * @param {boolean} overwrite - Whether to overwrite existing values
     */
    load(config, overwrite = false) {
        for (const [key, value] of Object.entries(config)) {
            if (overwrite || !this.has(key)) {
                this.set(key, value);
            }
        }
    }
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.TektonEnviron;
}

console.log('[TEKTON_ENV] JavaScript environment utility loaded');