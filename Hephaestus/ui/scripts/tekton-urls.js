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
    const normalizedComponent = component.replace(/-/g, "_").toUpperCase();
    
    // Host resolution order (matching Python shared.urls)
    if (!host) {
        // 1. Check for component-specific host
        const componentHostVar = `${normalizedComponent}_HOST`;
        host = window[componentHostVar];
        
        // 2. Check for global TEKTON_HOST
        if (!host) {
            host = window.TEKTON_HOST;
        }
        
        // 3. Default to localhost
        if (!host) {
            host = "localhost";
        }
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

// Landmark: aish MCP URL Builder - Routes UI to port 8118
// Critical distinction: aish shell runs on 8117, MCP server on 8118.
// This function ensures all UI components connect to the MCP server.
function aishUrl(path = "", ...args) {
    // aish MCP server runs on AISH_MCP_PORT, not AISH_PORT
    const host = args[0] || "localhost";
    const scheme = args[1] || "http";
    const port = window.AISH_MCP_PORT || 8118;
    return `${scheme}://${host}:${port}${path}`;
}

function ergonUrl(path = "", ...args) {
    return tektonUrl("ergon", path, ...args);
}

<<<<<<< HEAD
// Additional convenience functions for missing components
function engramUrl(path = "", ...args) {
    return tektonUrl("engram", path, ...args);
}

function prometheusUrl(path = "", ...args) {
    return tektonUrl("prometheus", path, ...args);
}

function harmoniaUrl(path = "", ...args) {
    return tektonUrl("harmonia", path, ...args);
}

=======
>>>>>>> a4c91167004194c4a593e7f3d300e63b0ca04dc6
function telosUrl(path = "", ...args) {
    return tektonUrl("telos", path, ...args);
}

<<<<<<< HEAD
function synthesisUrl(path = "", ...args) {
    return tektonUrl("synthesis", path, ...args);
}

function metisUrl(path = "", ...args) {
    return tektonUrl("metis", path, ...args);
}

function apolloUrl(path = "", ...args) {
    return tektonUrl("apollo", path, ...args);
}

function budgetUrl(path = "", ...args) {
    return tektonUrl("budget", path, ...args);
}

function peniaUrl(path = "", ...args) {
    return tektonUrl("penia", path, ...args);
}

function sophiaUrl(path = "", ...args) {
    return tektonUrl("sophia", path, ...args);
}

function hephaestusUrl(path = "", ...args) {
    return tektonUrl("hephaestus", path, ...args);
}

// Special case for Hephaestus MCP
function hephaestusMcpUrl(path = "", ...args) {
    const host = args[0] || window.HEPHAESTUS_HOST || window.TEKTON_HOST || "localhost";
    const scheme = args[1] || "http";
    const port = window.HEPHAESTUS_MCP_PORT || 8388;
    return `${scheme}://${host}:${port}${path}`;
}

// Special case for DB MCP
function dbMcpUrl(path = "", ...args) {
    const host = args[0] || window.DB_HOST || window.TEKTON_HOST || "localhost";
    const scheme = args[1] || "http";
    const port = window.DB_MCP_PORT || 8503;
    return `${scheme}://${host}:${port}${path}`;
}

=======
>>>>>>> a4c91167004194c4a593e7f3d300e63b0ca04dc6
// Make functions globally available
if (typeof window !== 'undefined') {
    // Core function
    window.tektonUrl = tektonUrl;
    
    // Existing component URLs
    window.hermesUrl = hermesUrl;
    window.athenaUrl = athenaUrl;
    window.rhetorUrl = rhetorUrl;
    window.termaUrl = termaUrl;
    window.tektonCoreUrl = tektonCoreUrl;
    window.noesisUrl = noesisUrl;
    window.numaUrl = numaUrl;
    window.aishUrl = aishUrl;
    window.ergonUrl = ergonUrl;
<<<<<<< HEAD
    
    // New component URLs
    window.engramUrl = engramUrl;
    window.prometheusUrl = prometheusUrl;
    window.harmoniaUrl = harmoniaUrl;
    window.telosUrl = telosUrl;
    window.synthesisUrl = synthesisUrl;
    window.metisUrl = metisUrl;
    window.apolloUrl = apolloUrl;
    window.budgetUrl = budgetUrl;
    window.peniaUrl = peniaUrl;
    window.sophiaUrl = sophiaUrl;
    window.hephaestusUrl = hephaestusUrl;
    window.hephaestusMcpUrl = hephaestusMcpUrl;
    window.dbMcpUrl = dbMcpUrl;
=======
    window.telosUrl = telosUrl;
>>>>>>> a4c91167004194c4a593e7f3d300e63b0ca04dc6
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        // Core function
        tektonUrl,
        
        // Component URLs
        hermesUrl,
        athenaUrl,
        rhetorUrl,
        termaUrl,
        tektonCoreUrl,
        noesisUrl,
        numaUrl,
        aishUrl,
        ergonUrl,
<<<<<<< HEAD
        engramUrl,
        prometheusUrl,
        harmoniaUrl,
        telosUrl,
        synthesisUrl,
        metisUrl,
        apolloUrl,
        budgetUrl,
        peniaUrl,
        sophiaUrl,
        hephaestusUrl,
        hephaestusMcpUrl,
        dbMcpUrl
=======
        telosUrl
>>>>>>> a4c91167004194c4a593e7f3d300e63b0ca04dc6
    };
}

console.log('[TEKTON_URLS] JavaScript URL utility loaded');