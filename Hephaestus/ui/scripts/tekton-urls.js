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

function telosUrl(path = "", ...args) {
    return tektonUrl("telos", path, ...args);
}

function metisUrl(path = "", ...args) {
    return tektonUrl("metis", path, ...args);
}

function synthesisUrl(path = "", ...args) {
    return tektonUrl("synthesis", path, ...args);
}

function apolloUrl(path = "", ...args) {
    return tektonUrl("apollo", path, ...args);
}

function budgetUrl(path = "", ...args) {
    return tektonUrl("budget", path, ...args);
}

function sophiaUrl(path = "", ...args) {
    return tektonUrl("sophia", path, ...args);
}

function prometheusUrl(path = "", ...args) {
    return tektonUrl("prometheus", path, ...args);
}

function harmoniaUrl(path = "", ...args) {
    return tektonUrl("harmonia", path, ...args);
}

function engramUrl(path = "", ...args) {
    return tektonUrl("engram", path, ...args);
}

function peniaUrl(path = "", ...args) {
    return tektonUrl("penia", path, ...args);
}

function hephaestusUrl(path = "", ...args) {
    return tektonUrl("hephaestus", path, ...args);
}
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
    window.telosUrl = telosUrl;
    window.metisUrl = metisUrl;
    window.synthesisUrl = synthesisUrl;
    window.apolloUrl = apolloUrl;
    window.budgetUrl = budgetUrl;
    window.sophiaUrl = sophiaUrl;
    window.prometheusUrl = prometheusUrl;
    window.harmoniaUrl = harmoniaUrl;
    window.engramUrl = engramUrl;
    window.peniaUrl = peniaUrl;
    window.hephaestusUrl = hephaestusUrl;
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
        telosUrl,
        metisUrl,
        synthesisUrl,
        apolloUrl,
        budgetUrl,
        sophiaUrl,
        prometheusUrl,
        harmoniaUrl,
        engramUrl,
        peniaUrl,
        hephaestusUrl
    };
}

console.log('[TEKTON_URLS] JavaScript URL utility loaded');