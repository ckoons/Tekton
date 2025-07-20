/**
 * Simple Health Monitor for Tekton Components
 * Uses env.js port values to check component health
 */

(function() {
    'use strict';
    
    // Component to port mapping using env.js values
    const componentPorts = {
        'numa': window.NUMA_PORT,
        'tekton_core': window.TEKTON_CORE_PORT,
        'prometheus': window.PROMETHEUS_PORT,
        'telos': window.TELOS_PORT,
        'metis': window.METIS_PORT,
        'harmonia': window.HARMONIA_PORT,
        'synthesis': window.SYNTHESIS_PORT,
        'athena': window.ATHENA_PORT,
        'sophia': window.SOPHIA_PORT,
        'noesis': window.NOESIS_PORT,
        'engram': window.ENGRAM_PORT,
        'apollo': window.APOLLO_PORT,
        'rhetor': window.RHETOR_PORT,
        'penia': window.PENIA_PORT || window.BUDGET_PORT,
        'hermes': window.HERMES_PORT,
        'ergon': window.ERGON_PORT,
        'terma': window.TERMA_PORT,
        // Profile and settings have no backend
        'profile': null,
        'settings': null
    };
    
    /**
     * Check health of a single component
     */
    async function checkComponentHealth(component, port) {
        if (!port) return false;
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2000);
            
            const response = await fetch(`http://localhost:${port}/health`, {
                method: 'GET',
                signal: controller.signal,
                cache: 'no-cache'
            });
            
            clearTimeout(timeoutId);
            return response.ok;
        } catch (error) {
            return false;
        }
    }
    
    /**
     * Update status indicator for a component
     */
    function updateStatusIndicator(component, isHealthy) {
        const indicator = document.querySelector(`.status-indicator[data-component="${component}"]`);
        if (indicator) {
            if (isHealthy) {
                indicator.classList.add('connected');
            } else {
                indicator.classList.remove('connected');
            }
        }
    }
    
    /**
     * Check all components
     */
    async function checkAllComponents() {
        console.log('[Health Monitor] Checking component health...');
        
        for (const [component, port] of Object.entries(componentPorts)) {
            if (port) {
                const isHealthy = await checkComponentHealth(component, port);
                updateStatusIndicator(component, isHealthy);
                
                if (window.TEKTON_DEBUG === 'true') {
                    console.log(`[Health Monitor] ${component}:${port} - ${isHealthy ? 'healthy' : 'unreachable'}`);
                }
            }
        }
    }
    
    /**
     * Initialize health monitoring
     */
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', start);
        } else {
            start();
        }
    }
    
    function start() {
        console.log('[Health Monitor] Starting health monitoring');
        
        // Check immediately
        checkAllComponents();
        
        // Then check every 15 seconds
        setInterval(checkAllComponents, 15000);
    }
    
    // Start monitoring
    init();
})();