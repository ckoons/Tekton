/**
 * Tekton Configuration for UI Components
 * 
 * This file provides centralized URL configuration for all Tekton components
 * Used by UI components to avoid hardcoded ports
 */

// Get base configuration from environment or use defaults
const TEKTON_HOST = window.TEKTON_HOST || 'localhost';
const TEKTON_PORT_BASE = window.TEKTON_PORT_BASE || 8100;

// Component port mapping - matches .env.local
const COMPONENT_PORTS = {
    engram: 8100,
    hermes: 8101,
    ergon: 8102,
    rhetor: 8103,
    terma: 8104,
    athena: 8105,
    prometheus: 8106,
    harmonia: 8107,
    telos: 8108,
    synthesis: 8109,
    tekton_core: 8110,
    metis: 8111,
    apollo: 8112,
    budget: 8113,
    penia: 8113,
    sophia: 8114,
    noesis: 8115,
    numa: 8116,
    aish: 8117,
    aish_mcp: 8118,
    hephaestus: 8180,
    hephaestus_mcp: 8188,
    db_mcp: 8501
};

/**
 * Get the URL for a Tekton component
 * @param {string} component - Component name (e.g., 'rhetor', 'apollo')
 * @param {string} path - Optional path to append
 * @returns {string} Full URL for the component
 */
function getTektonUrl(component, path = '') {
    const normalizedComponent = component.toLowerCase().replace(/-/g, '_');
    const port = COMPONENT_PORTS[normalizedComponent] || 8000;
    return `http://${TEKTON_HOST}:${port}${path}`;
}

// Export for use in other scripts
window.TektonConfig = {
    getTektonUrl,
    COMPONENT_PORTS,
    TEKTON_HOST,
    
    // Convenience methods for common components
    getRhetorUrl: (path = '') => getTektonUrl('rhetor', path),
    getApolloUrl: (path = '') => getTektonUrl('apollo', path),
    getErgonUrl: (path = '') => getTektonUrl('ergon', path),
    getPrometheusUrl: (path = '') => getTektonUrl('prometheus', path),
    getHermesUrl: (path = '') => getTektonUrl('hermes', path),
    getAthenaUrl: (path = '') => getTektonUrl('athena', path),
    getSophiaUrl: (path = '') => getTektonUrl('sophia', path),
    getTektonCoreUrl: (path = '') => getTektonUrl('tekton_core', path)
};

// Also export as module if supported
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.TektonConfig;
}