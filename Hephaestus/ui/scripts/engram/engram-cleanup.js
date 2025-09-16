/**
 * Engram Component Cleanup
 * Ensures all intervals and resources are properly cleaned up
 */

window.engramCleanup = {
    /**
     * Clean up all Engram components
     */
    cleanupAll: function() {
        console.log('[ENGRAM-CLEANUP] Starting cleanup of all components');
        
        // Clean up ESR Experience
        if (window.esrExperience && typeof window.esrExperience.cleanup === 'function') {
            console.log('[ENGRAM-CLEANUP] Cleaning up ESR Experience');
            window.esrExperience.cleanup();
        }
        
        // Clean up Cognitive Research System
        if (window.cognitiveResearchSystem && typeof window.cognitiveResearchSystem.cleanup === 'function') {
            console.log('[ENGRAM-CLEANUP] Cleaning up Cognitive Research System');
            window.cognitiveResearchSystem.cleanup();
        }
        
        // Clean up Patterns Enhanced
        if (window.enhancedPatterns && window.enhancedPatterns.simulationInterval) {
            console.log('[ENGRAM-CLEANUP] Cleaning up Enhanced Patterns');
            clearInterval(window.enhancedPatterns.simulationInterval);
            window.enhancedPatterns.simulationInterval = null;
        }
        
        // Clean up Patterns Analytics
        if (window.patternsAnalytics && window.patternsAnalytics.analysisInterval) {
            console.log('[ENGRAM-CLEANUP] Cleaning up Patterns Analytics');
            clearInterval(window.patternsAnalytics.analysisInterval);
            window.patternsAnalytics.analysisInterval = null;
        }
        
        // Clean up Combined Patterns
        if (window.combinedPatterns && window.combinedPatterns.simulationInterval) {
            console.log('[ENGRAM-CLEANUP] Cleaning up Combined Patterns');
            clearInterval(window.combinedPatterns.simulationInterval);
            window.combinedPatterns.simulationInterval = null;
        }
        
        // Clean up any animation frames
        if (window.cognitionBrain3D && window.cognitionBrain3D.animationId) {
            console.log('[ENGRAM-CLEANUP] Cancelling animation frames');
            cancelAnimationFrame(window.cognitionBrain3D.animationId);
            window.cognitionBrain3D.animationId = null;
        }
        
        // Clear all intervals (nuclear option for any we missed)
        this.clearAllIntervals();
        
        console.log('[ENGRAM-CLEANUP] Cleanup complete');
    },
    
    /**
     * Nuclear option: clear ALL intervals
     */
    clearAllIntervals: function() {
        // Store the original setInterval function
        const originalSetInterval = window.setInterval;
        
        // Clear intervals from 1 to 10000 (should cover all)
        let cleared = 0;
        for (let i = 1; i <= 10000; i++) {
            try {
                clearInterval(i);
                cleared++;
            } catch (e) {
                // Ignore errors
            }
        }
        
        if (cleared > 0) {
            console.log(`[ENGRAM-CLEANUP] Cleared ${cleared} intervals`);
        }
    },
    
    /**
     * Setup automatic cleanup on tab change
     */
    setupAutoCleanup: function() {
        // Clean up when switching away from Engram tab
        document.addEventListener('click', (e) => {
            // Check if clicking on a different tab
            const tabButton = e.target.closest('.component-tab-button');
            if (tabButton && !tabButton.textContent.includes('Engram')) {
                console.log('[ENGRAM-CLEANUP] Switching away from Engram, cleaning up...');
                this.cleanupAll();
            }
        });
        
        // Clean up when page unloads
        window.addEventListener('beforeunload', () => {
            this.cleanupAll();
        });
        
        // Clean up when visibility changes (tab switching)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('[ENGRAM-CLEANUP] Page hidden, cleaning up...');
                this.cleanupAll();
            }
        });
    }
};

// Auto-setup cleanup handlers
window.engramCleanup.setupAutoCleanup();

// Export for manual use
console.log('[ENGRAM-CLEANUP] Cleanup system ready. Use engramCleanup.cleanupAll() to manually clean up.');