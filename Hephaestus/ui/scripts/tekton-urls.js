/**
 * Tekton URL Builder - JavaScript equivalent of shared/urls.py
 * 
 * Provides a unified way to build URLs for Tekton components that works
 * across different environments (local, Coder-A/B/C, remote deployments).
 * 
 * Examples:
 *     const url = tektonUrl("hermes", "/api/mcp/v2");
 *     const url = tektonUrl("athena", "/api/v1/query", "remote.tekton.io");
 */

console.log('[FILE_TRACE] Loading: tekton-urls.js');

/**
 * Build URL for any Tekton component using window environment variables.
 * 
 * @param {string} component - Component name (e.g., "hermes", "athena", "tekton-core")
 * @param {string} path - URL path to append (e.g., "/api/mcp/v2") 
 * @param {string} host - Explicit host override (optional)
 * @param {string} scheme - URL scheme (default: "http")
 * @returns {string} Complete URL string
 */
function tektonUrl(component, path = "", host = null, scheme = "http") {
    // Normalize component name for window variable lookup
    const normalizedComponent = component.replace("-", "_").toUpperCase();
    
    // Host resolution
    if (!host) {
        host = "localhost";
    }
    
    // Get port from window environment variable
    const portVariable = `${normalizedComponent}_PORT`;
    const port = window[portVariable] || 8000;
    
    return `${scheme}://${host}:${port}${path}`;
}


// Convenience functions for common components
function hermesUrl(path = "", ...args) {
    return tektonUrl("hermes", path, ...args);
}

function athenaUrl(path = "", ...args) {
    return tektonUrl("athena", path, ...args);
}

function rhetorUrl(path = "", ...args) {
    return tektonUrl("rhetor", path, ...args);
}

function termaUrl(path = "", ...args) {
    return tektonUrl("terma", path, ...args);
}

function tektonCoreUrl(path = "", ...args) {
    return tektonUrl("tekton-core", path, ...args);
}

function noesisUrl(path = "", ...args) {
    return tektonUrl("noesis", path, ...args);
}

function numaUrl(path = "", ...args) {
    return tektonUrl("numa", path, ...args);
}

// Make functions globally available
if (typeof window !== 'undefined') {
    window.tektonUrl = tektonUrl;
    window.hermesUrl = hermesUrl;
    window.athenaUrl = athenaUrl;
    window.rhetorUrl = rhetorUrl;
    window.termaUrl = termaUrl;
    window.tektonCoreUrl = tektonCoreUrl;
    window.noesisUrl = noesisUrl;
    window.numaUrl = numaUrl;
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        tektonUrl,
        hermesUrl,
        athenaUrl,
        rhetorUrl,
        termaUrl,
        tektonCoreUrl,
        noesisUrl,
        numaUrl
    };
}

console.log('[TEKTON_URLS] JavaScript URL utility loaded');