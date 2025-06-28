/**
 * Chart.js integration for Tekton
 * This file ensures Chart.js is loaded for components that need it
 */

console.log('[FILE_TRACE] Loading: chart.js');
// Check if Chart.js is already loaded
if (typeof Chart === 'undefined') {
    console.log('[TEKTON] Loading Chart.js library...');
    
    // Create script element
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js';
    script.integrity = 'sha256-+8RZJua0aEWg+QVVKg4LEzEEm/8RFez5Tb4JBNiV5xA=';
    script.crossOrigin = 'anonymous';
    
    // Load Chart.js
    document.head.appendChild(script);
    
    // Log when loaded
    script.onload = function() {
        console.log('[TEKTON] Chart.js loaded successfully');
    };
    
    script.onerror = function() {
        console.error('[TEKTON] Error loading Chart.js');
    };
} else {
    console.log('[TEKTON] Chart.js already loaded');
}