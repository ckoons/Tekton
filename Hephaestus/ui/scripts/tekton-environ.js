/**
 * Tekton Environment Manager - JavaScript equivalent of shared.env.TektonEnviron
 * 
 * Manages environment variables for multi-Tekton deployments (Coder-A/B/C).
 * Provides centralized access to ports, hosts, and configuration.
 */

class TektonEnviron {
    constructor() {
        // Cache for environment variables
        this._cache = {};
        
        // Load initial environment from window
        this.loadEnvironment();
        
        // Track current Tekton instance
        this.currentInstance = this.detectInstance();
    }
    
    /**
     * Load environment variables from window object
     */
    loadEnvironment() {
        // Copy all TEKTON-related variables from window
        Object.keys(window).forEach(key => {
            if (key.includes('PORT') || key.includes('HOST') || key.startsWith('TEKTON_')) {
                this._cache[key] = window[key];
            }
        });
        
        console.log('[TektonEnviron] Loaded environment:', this._cache);
    }
    
    /**
     * Detect which Tekton instance we're running on
     * @returns {string} Instance identifier (e.g., 'coder-c', 'coder-a', 'local')
     */
    detectInstance() {
        // Check for explicit TEKTON_INSTANCE variable
        if (window.TEKTON_INSTANCE) {
            return window.TEKTON_INSTANCE;
        }
        
        // Detect from hostname
        const hostname = window.location.hostname;
        if (hostname.includes('coder-a')) {
            return 'coder-a';
        } else if (hostname.includes('coder-b')) {
            return 'coder-b';
        } else if (hostname.includes('coder-c')) {
            return 'coder-c';
        }
        
        // Check for TEKTON_HOST environment variable
        const tektonHost = this.get('TEKTON_HOST');
        if (tektonHost) {
            if (tektonHost.includes('coder-a')) return 'coder-a';
            if (tektonHost.includes('coder-b')) return 'coder-b';
            if (tektonHost.includes('coder-c')) return 'coder-c';
        }
        
        // Default to local
        return 'local';
    }
    
    /**
     * Get environment variable value
     * @param {string} key - Variable name (e.g., 'ENGRAM_PORT')
     * @param {any} defaultValue - Default value if not found
     * @returns {any} Variable value or default
     */
    get(key, defaultValue = null) {
        // Check cache first
        if (key in this._cache) {
            return this._cache[key];
        }
        
        // Check window object
        if (key in window) {
            this._cache[key] = window[key];
            return window[key];
        }
        
        // Check process.env if available (for Node.js compatibility)
        if (typeof process !== 'undefined' && process.env && key in process.env) {
            this._cache[key] = process.env[key];
            return process.env[key];
        }
        
        return defaultValue;
    }
    
    /**
     * Set environment variable value
     * @param {string} key - Variable name
     * @param {any} value - Variable value
     */
    set(key, value) {
        this._cache[key] = value;
        window[key] = value;
    }
    
    /**
     * Get port for a component
     * @param {string} component - Component name (e.g., 'engram', 'rhetor')
     * @returns {number} Port number
     */
    getPort(component) {
        const key = `${component.toUpperCase().replace('-', '_')}_PORT`;
        return this.get(key, 8000);
    }
    
    /**
     * Get host for a component
     * @param {string} component - Component name
     * @returns {string} Host address
     */
    getHost(component) {
        const key = `${component.toUpperCase().replace('-', '_')}_HOST`;
        return this.get(key, this.get('TEKTON_HOST', 'localhost'));
    }
    
    /**
     * Get base port for Tekton components
     * @returns {number} Base port number
     */
    getPortBase() {
        // Different base ports for different instances
        const instancePorts = {
            'local': 8300,
            'coder-a': 8100,
            'coder-b': 8200,
            'coder-c': 8300
        };
        
        return this.get('TEKTON_PORT_BASE', instancePorts[this.currentInstance] || 8300);
    }
    
    /**
     * Get CI port for a component
     * @param {string} component - Component name
     * @returns {number} CI port number
     */
    getAIPort(component) {
        const componentPort = this.getPort(component);
        const portBase = this.getPortBase();
        const aiPortBase = this.get('TEKTON_AI_PORT_BASE', 42000);
        
        return aiPortBase + (componentPort - portBase);
    }
    
    /**
     * Check if we're in a specific environment
     * @param {string} environment - Environment name
     * @returns {boolean} True if in specified environment
     */
    isEnvironment(environment) {
        return this.currentInstance === environment;
    }
    
    /**
     * Get full configuration for a component
     * @param {string} component - Component name
     * @returns {object} Configuration object
     */
    getComponentConfig(component) {
        return {
            name: component,
            port: this.getPort(component),
            host: this.getHost(component),
            aiPort: this.getAIPort(component),
            instance: this.currentInstance,
            httpUrl: tektonUrl(component, ''),
            wsUrl: tektonUrl(component, '').replace(/^http/, 'ws')
        };
    }
    
    /**
     * List all components with their configurations
     * @returns {object} Map of component configurations
     */
    listComponents() {
        const components = [
            'engram', 'hermes', 'ergon', 'rhetor', 'terma',
            'athena', 'prometheus', 'harmonia', 'telos', 'synthesis',
            'tekton-core', 'metis', 'apollo', 'budget', 'sophia',
            'noesis', 'numa', 'aish'
        ];
        
        const configs = {};
        components.forEach(component => {
            configs[component] = this.getComponentConfig(component);
        });
        
        return configs;
    }
    
    /**
     * Debug helper - print environment info
     */
    debug() {
        console.group('[TektonEnviron] Debug Information');
        console.log('Current Instance:', this.currentInstance);
        console.log('Port Base:', this.getPortBase());
        console.log('CI Port Base:', this.get('TEKTON_AI_PORT_BASE', 42000));
        console.log('TEKTON_HOST:', this.get('TEKTON_HOST', 'localhost'));
        console.log('\nComponent Configurations:');
        console.table(this.listComponents());
        console.groupEnd();
    }
}

// Create global instance
window.TektonEnviron = new TektonEnviron();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TektonEnviron;
}

console.log('[TektonEnviron] Initialized for instance:', window.TektonEnviron.currentInstance);