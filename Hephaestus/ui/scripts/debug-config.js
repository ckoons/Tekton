/**
 * Debug Configuration for Hephaestus UI
 * 
 * Simple debug control that can filter console output without modifying existing code.
 */

(function() {
  // Save original console methods
  const originalLog = console.log;
  const originalWarn = console.warn;
  const originalError = console.error;
  
  // Debug configuration
  const debugConfig = {
    fileTrace: false,  // Show [FILE_TRACE] messages
    minimalLoader: false,  // Show MinimalLoader messages
    uiManager: false,  // Show UIManager messages
    component: false,  // Show component-specific messages
    all: false  // Show all debug messages
  };
  
  // Load config from localStorage
  const savedConfig = localStorage.getItem('hephaestus_debug');
  if (savedConfig) {
    try {
      Object.assign(debugConfig, JSON.parse(savedConfig));
    } catch (e) {
      console.warn('Invalid debug config in localStorage');
    }
  }
  
  // Check URL parameters
  const params = new URLSearchParams(window.location.search);
  if (params.has('debug')) {
    const debugParam = params.get('debug');
    if (debugParam === 'all' || debugParam === 'true') {
      Object.keys(debugConfig).forEach(key => debugConfig[key] = true);
    } else if (debugParam === 'none' || debugParam === 'false') {
      Object.keys(debugConfig).forEach(key => debugConfig[key] = false);
    } else {
      // Enable specific debug categories
      debugParam.split(',').forEach(cat => {
        if (cat in debugConfig) debugConfig[cat] = true;
      });
    }
  }
  
  // Override console.log to filter messages
  console.log = function(...args) {
    const message = args.join(' ');
    
    // Always show if 'all' is enabled
    if (debugConfig.all) {
      return originalLog.apply(console, args);
    }
    
    // Check specific patterns
    if (!debugConfig.fileTrace && message.includes('[FILE_TRACE]')) return;
    if (!debugConfig.minimalLoader && message.includes('MinimalLoader:')) return;
    if (!debugConfig.uiManager && message.includes('[UIManager]')) return;
    if (!debugConfig.component && message.includes('component')) return;
    
    // Otherwise show the message
    originalLog.apply(console, args);
  };
  
  // Keep warnings and errors visible
  console.warn = originalWarn;
  console.error = originalError;
  
  // Global debug control
  window.HephaestusDebug = {
    // Enable specific debug category
    enable: function(category) {
      if (category in debugConfig) {
        debugConfig[category] = true;
        this.save();
      } else if (category === 'all') {
        Object.keys(debugConfig).forEach(key => debugConfig[key] = true);
        this.save();
      }
    },
    
    // Disable specific debug category
    disable: function(category) {
      if (category in debugConfig) {
        debugConfig[category] = false;
        this.save();
      } else if (category === 'all') {
        Object.keys(debugConfig).forEach(key => debugConfig[key] = false);
        this.save();
      }
    },
    
    // Save config to localStorage
    save: function() {
      localStorage.setItem('hephaestus_debug', JSON.stringify(debugConfig));
      console.log('Debug config saved. Reload page to apply changes.');
    },
    
    // Show current configuration
    status: function() {
      originalLog('=== Hephaestus Debug Configuration ===');
      originalLog('Current settings:', debugConfig);
      originalLog('Available categories:', Object.keys(debugConfig).join(', '));
      originalLog('');
      originalLog('Usage:');
      originalLog('  HephaestusDebug.enable("fileTrace")  - Enable file trace logging');
      originalLog('  HephaestusDebug.enable("all")        - Enable all debug output');
      originalLog('  HephaestusDebug.disable("all")       - Disable all debug output');
      originalLog('  HephaestusDebug.reset()              - Reset to defaults');
      originalLog('');
      originalLog('URL parameter: ?debug=fileTrace,minimalLoader');
      originalLog('              ?debug=all');
      originalLog('              ?debug=none');
    },
    
    // Reset to defaults
    reset: function() {
      Object.keys(debugConfig).forEach(key => debugConfig[key] = false);
      localStorage.removeItem('hephaestus_debug');
      console.log('Debug config reset. Reload page to apply changes.');
    },
    
    // Quick shortcuts
    enableFileTrace: () => HephaestusDebug.enable('fileTrace'),
    disableAll: () => HephaestusDebug.disable('all'),
    enableAll: () => HephaestusDebug.enable('all')
  };
  
  // Show initial status if any debug is enabled
  if (Object.values(debugConfig).some(v => v)) {
    originalLog('[Debug] Active categories:', Object.keys(debugConfig).filter(k => debugConfig[k]).join(', '));
    originalLog('[Debug] Use HephaestusDebug.status() for help');
  }
})();