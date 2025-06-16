# Tekton Logging System Recommendations

## Current State Analysis

Currently, the Tekton UI codebase uses several inconsistent approaches to logging:

1. Direct `console.log/error/warn` calls scattered throughout components
2. No standardized log levels or filtering mechanism
3. No integration with the Settings component for user configuration
4. No environment variable control for logging verbosity

## Recommended Logging Implementation

Based on the existing architecture and patterns, I recommend implementing a centralized logging system with the following features:

### 1. Create a Dedicated Logger Module

Create a new file `/scripts/logger.js` that provides a standardized logging interface:

```javascript
/**
 * Tekton Logger
 * Centralized logging system with configurable levels and outputs
 */

class Logger {
    constructor() {
        // Log levels with numeric values for comparison
        this.LEVELS = {
            TRACE: 0,   // Most verbose
            DEBUG: 1,   // Detailed debugging information
            INFO: 2,    // General information
            WARN: 3,    // Warning conditions
            ERROR: 4,   // Error conditions
            FATAL: 5,   // Severe error conditions
            OFF: 6      // No logging
        };
        
        // Default log level - can be overridden by env variables or settings
        this.defaultLevel = this.LEVELS.INFO;
        
        // Component-specific log levels (optional overrides)
        this.componentLevels = {};
        
        // Initialize based on environment
        this.init();
    }
    
    /**
     * Initialize the logger
     */
    init() {
        // Check for environment variable to set global log level
        if (window.ENV && window.ENV.TEKTON_LOGGING_LEVEL) {
            const envLevel = window.ENV.TEKTON_LOGGING_LEVEL.toUpperCase();
            if (this.LEVELS.hasOwnProperty(envLevel)) {
                this.defaultLevel = this.LEVELS[envLevel];
                console.log(`Logger initialized with environment level: ${envLevel}`);
            }
        }
        
        // Register with settings manager for UI control if available
        if (window.settingsManager) {
            // Add logging settings to the settings object if not present
            if (!window.settingsManager.settings.hasOwnProperty('loggingLevel')) {
                window.settingsManager.settings.loggingLevel = this.getLevelName(this.defaultLevel);
            }
            
            // Apply current settings if available
            this.applySettings(window.settingsManager.settings);
            
            // Listen for settings changes
            window.settingsManager.addEventListener('changed', (settings) => {
                this.applySettings(settings);
            });
        }
        
        return this;
    }
    
    /**
     * Apply settings from the settings manager
     * @param {Object} settings - Settings object
     */
    applySettings(settings) {
        if (settings && settings.loggingLevel) {
            const settingsLevel = settings.loggingLevel.toUpperCase();
            if (this.LEVELS.hasOwnProperty(settingsLevel)) {
                this.defaultLevel = this.LEVELS[settingsLevel];
                console.log(`Logger level updated from settings: ${settingsLevel}`);
            }
            
            // Apply component-specific levels if specified
            if (settings.componentLoggingLevels) {
                this.componentLevels = {...settings.componentLoggingLevels};
            }
        }
    }
    
    /**
     * Get the string name of a numeric log level
     * @param {number} level - Numeric log level
     * @returns {string} Level name
     */
    getLevelName(level) {
        for (const [name, value] of Object.entries(this.LEVELS)) {
            if (value === level) return name;
        }
        return 'UNKNOWN';
    }
    
    /**
     * Get the numeric value of a level string
     * @param {string} levelName - Log level name
     * @returns {number} Numeric log level
     */
    getLevelValue(levelName) {
        const upperName = levelName.toUpperCase();
        return this.LEVELS[upperName] !== undefined ? this.LEVELS[upperName] : this.defaultLevel;
    }
    
    /**
     * Set log level for a specific component
     * @param {string} component - Component name
     * @param {string|number} level - Log level (string name or numeric value)
     */
    setComponentLevel(component, level) {
        if (typeof level === 'string') {
            level = this.getLevelValue(level);
        }
        
        this.componentLevels[component] = level;
        
        // If settings manager exists, update settings
        if (window.settingsManager) {
            if (!window.settingsManager.settings.componentLoggingLevels) {
                window.settingsManager.settings.componentLoggingLevels = {};
            }
            window.settingsManager.settings.componentLoggingLevels[component] = this.getLevelName(level);
            window.settingsManager.save();
        }
    }
    
    /**
     * Check if a log message should be displayed based on level and component
     * @param {string|number} level - Log level or level name
     * @param {string} component - Component name
     * @returns {boolean} Whether the message should be logged
     */
    shouldLog(level, component) {
        // Convert string level to numeric if needed
        if (typeof level === 'string') {
            level = this.getLevelValue(level);
        }
        
        // Get the threshold level for this component
        const threshold = component && this.componentLevels[component] !== undefined
            ? this.componentLevels[component]
            : this.defaultLevel;
        
        // Only log if message level >= threshold level
        return level >= threshold;
    }
    
    /**
     * Log a message with formatting and metadata
     * @param {string} level - Log level (trace, debug, info, warn, error, fatal)
     * @param {string} component - Component name
     * @param {string} message - Log message
     * @param {any} data - Optional data to log
     */
    log(level, component, message, data) {
        const levelValue = this.getLevelValue(level);
        
        // Skip if we shouldn't log this message
        if (!this.shouldLog(levelValue, component)) {
            return;
        }
        
        // Format prefix
        const levelName = this.getLevelName(levelValue);
        const timestamp = new Date().toISOString().replace('T', ' ').replace('Z', '');
        const prefix = `[${timestamp}] [${levelName}] [${component}]`;
        
        // Select appropriate console method
        let method = 'log';
        switch (levelValue) {
            case this.LEVELS.TRACE:
            case this.LEVELS.DEBUG:
                method = 'debug';
                break;
            case this.LEVELS.INFO:
                method = 'info';
                break;
            case this.LEVELS.WARN:
                method = 'warn';
                break;
            case this.LEVELS.ERROR:
            case this.LEVELS.FATAL:
                method = 'error';
                break;
        }
        
        // Log the message
        if (data !== undefined) {
            console[method](prefix, message, data);
        } else {
            console[method](prefix, message);
        }
    }
    
    // Convenience methods for each log level
    
    trace(component, message, data) {
        this.log('TRACE', component, message, data);
    }
    
    debug(component, message, data) {
        this.log('DEBUG', component, message, data);
    }
    
    info(component, message, data) {
        this.log('INFO', component, message, data);
    }
    
    warn(component, message, data) {
        this.log('WARN', component, message, data);
    }
    
    error(component, message, data) {
        this.log('ERROR', component, message, data);
    }
    
    fatal(component, message, data) {
        this.log('FATAL', component, message, data);
    }
}

// Create global instance
window.logger = new Logger();

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.logger;
}
```

### 2. Update Environment Variables in `env.js`

Add logging configuration to the environment settings:

```javascript
// Add to env.js

// Logging settings
window.ENV = window.ENV || {};
window.ENV.TEKTON_LOGGING_LEVEL = 'INFO'; // Default global log level: TRACE, DEBUG, INFO, WARN, ERROR, FATAL, OFF
```

### 3. Integrate with the Settings Component UI

Add a Logging section to the Settings component to allow users to configure log levels:

```javascript
// Add to settings-component.js in the HTML for logging settings

<div class="settings__section">
    <h3 class="settings__section-title">Logging</h3>
    <div class="settings__option">
        <label for="global-log-level" class="settings__label">Global Log Level</label>
        <select id="global-log-level" class="settings__select">
            <option value="TRACE">Trace (Most Verbose)</option>
            <option value="DEBUG">Debug</option>
            <option value="INFO">Info (Default)</option>
            <option value="WARN">Warning</option>
            <option value="ERROR">Error</option>
            <option value="FATAL">Fatal</option>
            <option value="OFF">Off (No Logging)</option>
        </select>
    </div>
    
    <div class="settings__option">
        <label class="settings__label">Component Log Levels</label>
        <div id="component-log-levels" class="settings__component-logs">
            <!-- Dynamically populated with component-specific controls -->
        </div>
        <button id="add-component-log" class="settings__button">Add Component Override</button>
    </div>
</div>
```

### 4. Component Usage Pattern

Demonstrate a proper component usage example:

```javascript
// Ergon component example

class ErgonComponent {
    constructor() {
        // Component initialization
        this.state = {
            initialized: false,
            // ...other state properties
        };
    }
    
    /**
     * Initialize the component
     */
    init() {
        window.logger.info('ergon', 'Initializing Ergon component');
        
        // If already initialized, just activate
        if (this.state.initialized) {
            window.logger.debug('ergon', 'Ergon component already initialized, just activating');
            this.activateComponent();
            return this;
        }
        
        // Component setup
        this.setupTabs();
        this.setupEventListeners();
        
        // Mark as initialized
        this.state.initialized = true;
        
        return this;
    }
    
    /**
     * Set up tab switching functionality
     */
    setupTabs() {
        window.logger.debug('ergon', 'Setting up Ergon tabs');
        
        // Method implementation
    }
    
    /**
     * Activate a specific tab
     * @param {string} tabId - The ID of the tab to activate
     */
    activateTab(tabId) {
        window.logger.debug('ergon', `Activating tab: ${tabId}`);
        
        // Method implementation
        
        // Example of error logging
        if (!someCondition) {
            window.logger.error('ergon', `Tab activation failed for: ${tabId}`, { reason: 'Component not found' });
        }
    }
}
```

## Implementation Plan

1. **Create the Logger Module**:
   - Implement the `logger.js` file as specified
   - Load it early in the main.js script

2. **Update Environment Configuration**:
   - Modify env.js to include logging configuration
   - Document available log levels

3. **Update Settings Component**:
   - Add logging configuration section to the settings UI
   - Implement handlers for changing log levels

4. **Update Component Template**:
   - Update the component template to use the logger
   - Document logging best practices

5. **Gradually Refactor Existing Components**:
   - Start with core components like Ergon, Athena
   - Replace direct console calls with logger methods

## Benefits

1. **Consistency**: Standardized logging format across all components
2. **Configurability**: Runtime control of log levels via UI and environment
3. **Performance**: Avoid unnecessary log processing when disabled
4. **Debugging**: Better contextual information in logs for troubleshooting
5. **Production Safety**: Easy to disable verbose logging in production

## Summary

This logging approach provides a flexible, consistent way to manage debug output across the Tekton system. It integrates with the existing Settings component for user configuration while also supporting environment-based control for deployment scenarios.

The system is designed to be minimally invasive to implement in existing components while providing significant improvements in debugging capabilities and output control.