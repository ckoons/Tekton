/**
 * Memory Diagnostic Tool for Engram UI
 * Helps identify memory leaks and performance issues
 */

window.engramDiagnostic = {
    // Track memory usage
    memorySnapshots: [],
    
    // Start monitoring
    startMonitoring: function() {
        console.log('[DIAGNOSTIC] Starting memory monitoring...');
        
        // Take initial snapshot
        this.takeSnapshot('initial');
        
        // Monitor every 5 seconds
        this.monitorInterval = setInterval(() => {
            this.takeSnapshot('periodic');
        }, 5000);
        
        // Monitor specific events
        this.attachEventMonitors();
    },
    
    // Stop monitoring
    stopMonitoring: function() {
        if (this.monitorInterval) {
            clearInterval(this.monitorInterval);
            console.log('[DIAGNOSTIC] Stopped memory monitoring');
        }
        this.generateReport();
    },
    
    // Take memory snapshot
    takeSnapshot: function(label) {
        const snapshot = {
            label: label,
            timestamp: Date.now(),
            // Count DOM elements
            domNodes: document.getElementsByTagName('*').length,
            // Count specific elements that might accumulate
            selects: document.getElementsByTagName('select').length,
            options: document.getElementsByTagName('option').length,
            divs: document.getElementsByTagName('div').length,
            // Count event listeners (approximate)
            eventListeners: this.countEventListeners(),
            // Count data attributes
            dataAttributes: this.countDataAttributes(),
            // Check for memory-heavy features
            images: document.getElementsByTagName('img').length,
            scripts: document.getElementsByTagName('script').length,
            iframes: document.getElementsByTagName('iframe').length,
            // Engram-specific counts
            memoryCards: document.querySelectorAll('.engram__memory-card').length,
            ciSelectors: document.querySelectorAll('[id*="ci-select"]').length
        };
        
        // Try to get memory info if available (Chrome with flags)
        if (performance.memory) {
            snapshot.usedJSHeapSize = performance.memory.usedJSHeapSize;
            snapshot.totalJSHeapSize = performance.memory.totalJSHeapSize;
            snapshot.jsHeapSizeLimit = performance.memory.jsHeapSizeLimit;
            snapshot.heapUsage = (performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100;
            
            // Warn if heap usage is high
            if (snapshot.heapUsage > 80) {
                console.warn(`[DIAGNOSTIC] High memory usage: ${snapshot.heapUsage.toFixed(1)}%`);
            }
        } else {
            console.log('[DIAGNOSTIC] Note: performance.memory not available. Using DOM metrics only.');
            console.log('[DIAGNOSTIC] To enable in Chrome: chrome://flags/#enable-precise-memory-info');
        }
        
        this.memorySnapshots.push(snapshot);
        
        // Warn based on DOM metrics
        if (snapshot.domNodes > 5000) {
            console.warn(`[DIAGNOSTIC] High DOM node count: ${snapshot.domNodes}`);
        }
        if (snapshot.eventListeners > 100) {
            console.warn(`[DIAGNOSTIC] High event listener count: ${snapshot.eventListeners}`);
        }
        
        return snapshot;
    },
    
    // Count event listeners (approximate)
    countEventListeners: function() {
        let count = 0;
        const allElements = document.getElementsByTagName('*');
        
        // Check common event properties
        const eventProps = ['onclick', 'onchange', 'onload', 'onerror', 'onsubmit', 'onfocus', 'onblur'];
        
        for (let el of allElements) {
            for (let prop of eventProps) {
                if (el[prop]) count++;
            }
            // Check for stored handlers
            if (el._changeHandler) count++;
            if (el._clickHandler) count++;
        }
        
        return count;
    },
    
    // Count data attributes
    countDataAttributes: function() {
        let count = 0;
        const allElements = document.getElementsByTagName('*');
        
        for (let el of allElements) {
            if (el.attributes) {
                for (let attr of el.attributes) {
                    if (attr.name.startsWith('data-')) {
                        count++;
                    }
                }
            }
        }
        
        return count;
    },
    
    // Attach monitors to specific events
    attachEventMonitors: function() {
        // Monitor CI selector changes
        const selectors = ['memories-ci-select', 'cognition-ci-select'];
        selectors.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('change', () => {
                    console.log(`[DIAGNOSTIC] CI selector changed: ${id}`);
                    this.takeSnapshot(`selector_${id}`);
                });
            }
        });
        
        // Monitor tab changes
        const tabs = document.querySelectorAll('input[name="engram-tabs"]');
        tabs.forEach(tab => {
            tab.addEventListener('change', () => {
                console.log(`[DIAGNOSTIC] Tab changed: ${tab.id}`);
                this.takeSnapshot(`tab_${tab.id}`);
            });
        });
    },
    
    // Generate diagnostic report
    generateReport: function() {
        if (this.memorySnapshots.length === 0) {
            console.log('[DIAGNOSTIC] No snapshots to report');
            return;
        }
        
        const first = this.memorySnapshots[0];
        const last = this.memorySnapshots[this.memorySnapshots.length - 1];
        
        const report = {
            duration: (last.timestamp - first.timestamp) / 1000,
            snapshots: this.memorySnapshots.length,
            domGrowth: last.domNodes - first.domNodes,
            listenerGrowth: last.eventListeners - first.eventListeners,
            dataAttrGrowth: last.dataAttributes - first.dataAttributes,
            selectGrowth: last.selects - first.selects,
            optionGrowth: last.options - first.options,
            memoryCardGrowth: last.memoryCards - first.memoryCards
        };
        
        // Add memory metrics if available
        if (last.usedJSHeapSize && first.usedJSHeapSize) {
            report.memoryGrowth = {
                absolute: last.usedJSHeapSize - first.usedJSHeapSize,
                percentage: ((last.usedJSHeapSize - first.usedJSHeapSize) / first.usedJSHeapSize) * 100
            };
            report.peakUsage = Math.max(...this.memorySnapshots.filter(s => s.heapUsage).map(s => s.heapUsage));
            report.averageUsage = this.memorySnapshots.filter(s => s.heapUsage).reduce((sum, s) => sum + s.heapUsage, 0) / 
                                  this.memorySnapshots.filter(s => s.heapUsage).length;
        }
        
        console.log('[DIAGNOSTIC] === Performance Report ===');
        console.log(`  Duration: ${report.duration}s`);
        console.log(`  Snapshots taken: ${report.snapshots}`);
        
        console.log('\n[DIAGNOSTIC] DOM Metrics:');
        console.log(`  DOM nodes: ${first.domNodes} → ${last.domNodes} (${report.domGrowth > 0 ? '+' : ''}${report.domGrowth})`);
        console.log(`  Event listeners: ${first.eventListeners} → ${last.eventListeners} (${report.listenerGrowth > 0 ? '+' : ''}${report.listenerGrowth})`);
        console.log(`  Data attributes: ${first.dataAttributes} → ${last.dataAttributes} (${report.dataAttrGrowth > 0 ? '+' : ''}${report.dataAttrGrowth})`);
        console.log(`  Select elements: ${first.selects} → ${last.selects} (${report.selectGrowth > 0 ? '+' : ''}${report.selectGrowth})`);
        console.log(`  Option elements: ${first.options} → ${last.options} (${report.optionGrowth > 0 ? '+' : ''}${report.optionGrowth})`);
        console.log(`  Memory cards: ${first.memoryCards} → ${last.memoryCards} (${report.memoryCardGrowth > 0 ? '+' : ''}${report.memoryCardGrowth})`);
        
        if (report.memoryGrowth) {
            console.log('\n[DIAGNOSTIC] Memory Metrics:');
            console.log(`  Heap growth: ${(report.memoryGrowth.absolute / 1024 / 1024).toFixed(2)}MB (${report.memoryGrowth.percentage.toFixed(1)}%)`);
            console.log(`  Peak usage: ${report.peakUsage.toFixed(1)}%`);
            console.log(`  Average usage: ${report.averageUsage.toFixed(1)}%`);
        }
        
        // Analysis
        console.log('\n[DIAGNOSTIC] Analysis:');
        const issues = [];
        
        if (report.memoryGrowth && report.memoryGrowth.percentage > 20) {
            issues.push('Possible memory leak detected (>20% growth)');
        }
        if (report.domGrowth > 100) {
            issues.push(`Excessive DOM growth: ${report.domGrowth} nodes added`);
        }
        if (report.listenerGrowth > 10) {
            issues.push(`Excessive event listeners: ${report.listenerGrowth} added`);
        }
        if (report.optionGrowth > 100) {
            issues.push(`Many option elements created: ${report.optionGrowth} added`);
        }
        if (last.domNodes > 5000) {
            issues.push(`High total DOM nodes: ${last.domNodes}`);
        }
        
        if (issues.length > 0) {
            console.warn('[DIAGNOSTIC] Issues found:');
            issues.forEach(issue => console.warn(`  - ${issue}`));
        } else {
            console.log('  ✓ No major issues detected');
        }
        
        return report;
    },
    
    // Find duplicate event listeners
    findDuplicateListeners: function() {
        const listeners = {};
        
        // Check all selects
        document.querySelectorAll('select').forEach(select => {
            const handlers = select._changeHandler || select.onchange;
            if (handlers) {
                const key = select.id || select.className;
                listeners[key] = (listeners[key] || 0) + 1;
            }
        });
        
        console.log('[DIAGNOSTIC] Event listener counts:', listeners);
        
        // Report duplicates
        Object.entries(listeners).forEach(([key, count]) => {
            if (count > 1) {
                console.warn(`[DIAGNOSTIC] Duplicate listeners on: ${key} (${count})`);
            }
        });
    },
    
    // Clean up orphaned references
    cleanup: function() {
        console.log('[DIAGNOSTIC] Running cleanup...');
        
        // Clear any intervals/timeouts
        for (let i = 1; i < 1000; i++) {
            clearInterval(i);
            clearTimeout(i);
        }
        
        // Clear cached data
        if (window.engram) {
            window.engram._memoriesCache = null;
            window.engram._insightsCache = null;
        }
        
        // Force garbage collection (if available in dev tools)
        if (window.gc) {
            window.gc();
            console.log('[DIAGNOSTIC] Forced garbage collection');
        }
        
        this.takeSnapshot('after_cleanup');
    }
};

// Auto-start if diagnostic mode is enabled
if (window.location.hash === '#diagnostic') {
    console.log('[DIAGNOSTIC] Auto-starting diagnostic mode');
    window.engramDiagnostic.startMonitoring();
}

// Add specific CI selector diagnostic
window.engramDiagnostic.checkCISelectors = function() {
    console.log('[DIAGNOSTIC] Checking CI Selectors...');
    
    const selectors = ['memories-ci-select', 'cognition-ci-select'];
    
    selectors.forEach(id => {
        const select = document.getElementById(id);
        if (select) {
            console.log(`\n[DIAGNOSTIC] ${id}:`);
            console.log(`  Options: ${select.options.length}`);
            console.log(`  Has _changeHandler: ${!!select._changeHandler}`);
            console.log(`  Has onchange: ${!!select.onchange}`);
            
            // Count CI types
            const types = {};
            for (let option of select.options) {
                const type = option.getAttribute('data-ci-type') || 'unknown';
                types[type] = (types[type] || 0) + 1;
            }
            console.log('  CI types:', types);
            
            // Check for duplicates
            const values = {};
            for (let option of select.options) {
                if (option.value) {
                    values[option.value] = (values[option.value] || 0) + 1;
                }
            }
            const duplicates = Object.entries(values).filter(([k, v]) => v > 1);
            if (duplicates.length > 0) {
                console.warn('  Duplicate options found:', duplicates);
            }
        } else {
            console.warn(`[DIAGNOSTIC] ${id} not found`);
        }
    });
    
    // Check if loadEngramCIRegistry function exists
    console.log('\n[DIAGNOSTIC] Function availability:');
    console.log(`  loadEngramCIRegistry: ${typeof loadEngramCIRegistry}`);
    console.log(`  engramCIRegistryLoaded: ${typeof engramCIRegistryLoaded !== 'undefined' ? engramCIRegistryLoaded : 'undefined'}`);
};

// Add console commands
console.log('[DIAGNOSTIC] Available commands:');
console.log('  engramDiagnostic.startMonitoring() - Start monitoring');
console.log('  engramDiagnostic.stopMonitoring() - Stop and generate report');
console.log('  engramDiagnostic.findDuplicateListeners() - Check for duplicate listeners');
console.log('  engramDiagnostic.checkCISelectors() - Check CI selector state');
console.log('  engramDiagnostic.cleanup() - Clean up memory');
console.log('  engramDiagnostic.takeSnapshot("label") - Take single snapshot');