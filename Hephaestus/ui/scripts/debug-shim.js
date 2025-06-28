/**
 * Debug Shim for Tekton
 * 
 * This lightweight shim provides debug instrumentation that can evolve over time
 * without requiring code changes in components. It allows for immediate
 * instrumentation with minimal overhead, while supporting future expansion.
 * 
 * It's designed to work with both UI components and backend systems by bridging
 * to existing logger() functions when available.
 */

console.log('[FILE_TRACE] Loading: debug-shim.js');
// Simple global debug object
window.TektonDebug = {
  // Configuration (can be updated by future logging system)
  config: {
    enabled: true,                 // Master switch - ENABLED BY DEFAULT
    logLevel: 'DEBUG',             // Default log level - set to DEBUG
    componentLevels: {},           // Component-specific overrides
    timestampFormat: 'HH:MM:SS.mmm', // How to format timestamps
    backendIntegration: true,      // Whether to forward logs to backend when possible
    consoleOutput: true            // Whether to output to browser console
  },
  
  // Level values for comparison
  LEVELS: {
    TRACE: 0,
    DEBUG: 1,
    INFO: 2,
    WARN: 3,
    ERROR: 4,
    FATAL: 5,
    OFF: 6
  },
  
  // Initialize from environment if available
  init: function() {
    // Enable if environment requests it
    if (window.TEKTON_DEBUG === 'true') {
      this.config.enabled = true;
    }
    
    // Set log level from environment if available
    if (window.TEKTON_LOG_LEVEL) {
      this.config.logLevel = window.TEKTON_LOG_LEVEL;
    }
    
    return this;
  },
  
  // Check if a message should be logged
  shouldLog: function(level, component) {
    if (!this.config.enabled) return false;
    
    // Get numeric values for comparison
    const levelValue = this.LEVELS[level] !== undefined ? 
                     this.LEVELS[level] : this.LEVELS.INFO;
    
    // Get threshold for this component or global default
    const levelName = component && this.config.componentLevels[component] ?
                     this.config.componentLevels[component] : this.config.logLevel;
    const threshold = this.LEVELS[levelName] !== undefined ?
                     this.LEVELS[levelName] : this.LEVELS.INFO;
    
    // Log if level meets or exceeds threshold
    return levelValue >= threshold;
  },
  
  // Core log method - supports both console and backend integration
  log: function(level, component, message, data) {
    // Skip if disabled or below threshold
    if (!this.shouldLog(level, component)) return;
    
    // Format timestamp - can be enhanced later
    const timestamp = new Date().toLocaleTimeString();
    
    // Format prefix
    const prefix = `[${timestamp}] [${level}] [${component}]`;
    
    // Format full message for possible backend transmission
    const formattedMessage = data !== undefined ? 
      `${prefix} ${message} ${JSON.stringify(data)}` : 
      `${prefix} ${message}`;
    
    // Backend integration - attempt to use existing logger() if available
    if (this.config.backendIntegration) {
      this.sendToBackendLogger(level, component, formattedMessage);
    }
    
    // Console output if enabled
    if (this.config.consoleOutput) {
      // Select console method based on level
      let method = 'log';
      switch(level) {
        case 'TRACE':
        case 'DEBUG': 
          method = 'debug'; 
          break;
        case 'INFO': 
          method = 'info'; 
          break;
        case 'WARN': 
          method = 'warn'; 
          break;
        case 'ERROR':
        case 'FATAL': 
          method = 'error'; 
          break;
      }
      
      // Log to console
      if (data !== undefined) {
        console[method](prefix, message, data);
      } else {
        console[method](prefix, message);
      }
    }
    
    // Return true to indicate logging occurred (useful for testing)
    return true;
  },
  
  /**
   * Attempt to send log to backend logger system if available
   * This can integrate with existing logger() functions or websocket connections
   */
  sendToBackendLogger: function(level, component, message) {
    // Check for different possible backend logging mechanisms
    
    // 1. Check for websocket manager (used in many Tekton components)
    if (window.websocketManager && typeof window.websocketManager.sendLog === 'function') {
      try {
        // Use the existing sendLog method if available
        window.websocketManager.sendLog({
          level: level,
          component: component,
          message: message,
          timestamp: new Date().toISOString()
        });
        return true;
      } catch (e) {
        // Failed to use websocket manager, fall back to other methods
      }
    }
    
    // 2. Check for global logger function (common in Tekton backend)
    if (typeof window.logger === 'function') {
      try {
        // Map our levels to whatever the logger function expects
        const mappedLevel = this.mapLevelToBackend(level);
        window.logger(mappedLevel, `[${component}] ${message}`);
        return true;
      } catch (e) {
        // Failed to use global logger, continue to other methods
      }
    }
    
    // 3. Check for tektonUI.log method
    if (window.tektonUI && typeof window.tektonUI.log === 'function') {
      try {
        window.tektonUI.log(level, component, message);
        return true;
      } catch (e) {
        // Failed to use tektonUI.log
      }
    }
    
    // No backend logging mechanism available
    return false;
  },
  
  /**
   * Map our log levels to backend log levels if they differ
   * This can be customized based on your backend logging system
   */
  mapLevelToBackend: function(level) {
    // This mapping can be customized based on your backend system
    const mapping = {
      'TRACE': 'debug',   // Many systems don't have TRACE
      'DEBUG': 'debug',
      'INFO': 'info',
      'WARN': 'warning',  // Some systems use 'warning' instead of 'warn'
      'ERROR': 'error',
      'FATAL': 'critical' // Some systems use 'critical' for fatal errors
    };
    
    return mapping[level] || 'info';
  },
  
  // Convenience methods for different log levels
  trace: function(component, message, data) {
    return this.log('TRACE', component, message, data);
  },
  
  debug: function(component, message, data) {
    return this.log('DEBUG', component, message, data);
  },
  
  info: function(component, message, data) {
    return this.log('INFO', component, message, data);
  },
  
  warn: function(component, message, data) {
    return this.log('WARN', component, message, data);
  },
  
  error: function(component, message, data) {
    return this.log('ERROR', component, message, data);
  },
  
  fatal: function(component, message, data) {
    return this.log('FATAL', component, message, data);
  }
};

// Auto-initialize
window.TektonDebug.init();

// Export for module use if needed
if (typeof module !== 'undefined' && module.exports) {
  module.exports = window.TektonDebug;
}