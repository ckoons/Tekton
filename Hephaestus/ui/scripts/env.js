/**
 * Environment variables for Tekton UI
 * This script sets up window environment variables for port access
 */

console.log('[FILE_TRACE] Loading: env.js');
// Single Port Architecture environment variables
window.HEPHAESTUS_PORT = 8080;  // Default Hephaestus port
window.ENGRAM_PORT = 8000;      // Default Engram port
window.HERMES_PORT = 8001;      // Default Hermes port
window.ERGON_PORT = 8002;       // Default Ergon port
window.RHETOR_PORT = 8003;      // Default Rhetor port
window.TERMA_PORT = 8004;       // Default Terma port
window.ATHENA_PORT = 8005;      // Default Athena port
window.PROMETHEUS_PORT = 8006;  // Default Prometheus port
window.HARMONIA_PORT = 8007;    // Default Harmonia port
window.TELOS_PORT = 8008;       // Default Telos port
window.SYNTHESIS_PORT = 8009;   // Default Synthesis port
window.TEKTON_CORE_PORT = 8010; // Default Tekton Core port
window.METIS_PORT = 8011;       // Default Metis port
window.APOLLO_PORT = 8012;      // Default Apollo port
window.BUDGET_PORT = 8013;      // Default Budget port
window.PENIA_PORT = 8013;       // Default Penia port (same as budget)
window.SOPHIA_PORT = 8014;      // Default Sophia port
window.NOESIS_PORT = 8015;      // Default Noesis port
window.NUMA_PORT = 8016;        // Default Numa port

// UI Display settings - now managed by SettingsManager
// window.SHOW_GREEK_NAMES is set dynamically from saved settings

// Debug settings
window.TEKTON_DEBUG = 'true';        // Master switch for debug instrumentation
window.TEKTON_LOG_LEVEL = 'DEBUG';   // Default log level (TRACE, DEBUG, INFO, WARN, ERROR, FATAL, OFF)

// Function to update port values from server 
function updatePortsFromServer() {
    // Try to fetch port configuration from server
    fetch('/api/config/ports')
        .then(response => {
            if (!response.ok) {
                console.warn('Could not fetch port configuration from server. Using defaults.');
                return;
            }
            return response.json();
        })
        .then(config => {
            if (!config) return;
            
            // Update all port values
            Object.keys(config).forEach(key => {
                if (key.endsWith('_PORT') && window.hasOwnProperty(key)) {
                    window[key] = config[key];
                    console.log(`Set ${key} to ${config[key]}`);
                }
            });
            
            // Dispatch event to notify components that ports are updated
            window.dispatchEvent(new CustomEvent('ports-updated'));
        })
        .catch(error => {
            console.error('Error fetching port configuration:', error);
        });
}

// Try to update ports when the page loads
document.addEventListener('DOMContentLoaded', updatePortsFromServer);