/**
 * State Debugging Tools
 * 
 * Provides tools for debugging and monitoring state changes in the Tekton
 * state management system. Includes a state inspector, state history viewer,
 * and performance monitoring.
 */

class StateDebug {
    constructor() {
        this.initialized = false;
        this.visible = false;
        this.currentView = 'inspector';
        this.container = null;
        this.historyData = {};
        this.stateSnapshots = [];
        this.performanceData = {
            updates: 0,
            totalTime: 0,
            maxTime: 0,
            startTime: 0
        };
        this.expandedPaths = new Set();
        this.filter = '';
        this.logEnabled = false;
        this.performanceEnabled = false;
    }
    
    /**
     * Initialize the state debugger
     * 
     * @param {Object} options - Configuration options
     * @returns {StateDebug} - The debugger instance
     */
    init(options = {}) {
        if (this.initialized) return this;
        
        // Setup namespace in window.tektonUI
        window.tektonUI = window.tektonUI || {};
        window.tektonUI.stateDebug = this;
        
        // Set default options
        this.logEnabled = options.logEnabled || false;
        this.performanceEnabled = options.performanceEnabled || false;
        
        // Check for StateManager
        const stateManager = window.tektonUI && window.tektonUI.stateManager;
        if (!stateManager) {
            console.warn('[StateDebug] StateManager not found');
            return this;
        }
        
        // Create keyboard shortcut for toggle
        this._setupKeyboardShortcut();
        
        // Create debugger UI container
        this._createDebuggerUI();
        
        // Integrate with StateManager
        this._patchStateManager();
        
        this.initialized = true;
        console.log('[StateDebug] Initialized');
        
        // Take initial snapshot
        this._takeSnapshot();
        
        return this;
    }
    
    /**
     * Toggle the debugger visibility
     */
    toggle() {
        if (!this.initialized) return;
        
        if (this.visible) {
            this.hide();
        } else {
            this.show();
        }
    }
    
    /**
     * Show the debugger
     */
    show() {
        if (!this.initialized || this.visible) return;
        
        this.container.style.display = 'block';
        setTimeout(() => {
            this.container.style.opacity = '1';
        }, 10);
        
        this.visible = true;
        this._refreshView();
    }
    
    /**
     * Hide the debugger
     */
    hide() {
        if (!this.initialized || !this.visible) return;
        
        this.container.style.opacity = '0';
        setTimeout(() => {
            this.container.style.display = 'none';
        }, 300);
        
        this.visible = false;
    }
    
    /**
     * Enable or disable state action logging
     * 
     * @param {boolean} enabled - Whether logging should be enabled
     */
    setLogging(enabled) {
        this.logEnabled = enabled;
        
        if (enabled) {
            console.log('[StateDebug] State logging enabled');
        }
    }
    
    /**
     * Take a snapshot of the current state
     */
    takeSnapshot() {
        if (!this.initialized) return;
        
        this._takeSnapshot();
        console.log('[StateDebug] State snapshot taken');
    }
    
    /**
     * Clear all snapshots and history
     */
    clear() {
        if (!this.initialized) return;
        
        this.historyData = {};
        this.stateSnapshots = [];
        this.performanceData = {
            updates: 0,
            totalTime: 0,
            maxTime: 0,
            startTime: Date.now()
        };
        
        this._refreshView();
        console.log('[StateDebug] State history cleared');
    }
    
    /**
     * Create a development state inspector in the page
     */
    createInspector() {
        if (this.inspectorContainer) {
            // Already exists, just show it
            this.toggle();
            return;
        }
        
        this.init();
        this.show();
    }
    
    /* Private methods */
    
    /**
     * Create the debugger UI container
     */
    _createDebuggerUI() {
        const container = document.createElement('div');
        container.className = 'tekton-state-debugger';
        container.style.display = 'none';
        container.style.opacity = '0';
        
        // Create debugger styles
        const styles = document.createElement('style');
        styles.textContent = `
            .tekton-state-debugger {
                position: fixed;
                top: 0;
                right: 0;
                width: 400px;
                height: 100vh;
                background-color: rgba(30, 30, 30, 0.95);
                color: #f0f0f0;
                font-family: monospace;
                font-size: 12px;
                z-index: 10000;
                box-shadow: -2px 0 10px rgba(0, 0, 0, 0.5);
                display: flex;
                flex-direction: column;
                transition: opacity 0.3s ease;
                opacity: 0;
                overflow: hidden;
            }
            
            .tekton-state-debugger__header {
                padding: 8px;
                background-color: #2a2a2a;
                border-bottom: 1px solid #444;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .tekton-state-debugger__title {
                font-weight: bold;
                margin: 0;
            }
            
            .tekton-state-debugger__close {
                background: none;
                border: none;
                color: #aaa;
                font-size: 16px;
                cursor: pointer;
            }
            
            .tekton-state-debugger__tabs {
                display: flex;
                background-color: #252525;
                border-bottom: 1px solid #444;
            }
            
            .tekton-state-debugger__tab {
                padding: 8px 12px;
                cursor: pointer;
            }
            
            .tekton-state-debugger__tab--active {
                background-color: #333;
                border-bottom: 2px solid #007bff;
            }
            
            .tekton-state-debugger__content {
                flex: 1;
                overflow: auto;
                padding: 8px;
            }
            
            .tekton-state-debugger__footer {
                padding: 8px;
                background-color: #2a2a2a;
                border-top: 1px solid #444;
                display: flex;
                justify-content: space-between;
            }
            
            .tekton-state-debugger__button {
                background-color: #333;
                border: 1px solid #555;
                color: #f0f0f0;
                padding: 4px 8px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 11px;
            }
            
            .tekton-state-debugger__button:hover {
                background-color: #444;
            }
            
            .tekton-state-debugger__toolbar {
                display: flex;
                gap: 8px;
                margin-bottom: 8px;
                padding-bottom: 8px;
                border-bottom: 1px solid #444;
            }
            
            .tekton-state-debugger__search {
                flex: 1;
                background-color: #333;
                border: 1px solid #555;
                color: #f0f0f0;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
            }
            
            .tekton-state-debugger__select {
                background-color: #333;
                border: 1px solid #555;
                color: #f0f0f0;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
            }
            
            .tekton-state-debugger__tree-node {
                margin: 2px 0;
                line-height: 1.5;
            }
            
            .tekton-state-debugger__tree-key {
                color: #bb86fc;
                cursor: pointer;
            }
            
            .tekton-state-debugger__tree-colon {
                color: #aaa;
                margin: 0 4px;
            }
            
            .tekton-state-debugger__tree-value {
                color: #03dac6;
            }
            
            .tekton-state-debugger__tree-string {
                color: #ff7597;
            }
            
            .tekton-state-debugger__tree-number {
                color: #86c1b9;
            }
            
            .tekton-state-debugger__tree-boolean {
                color: #ffa280;
            }
            
            .tekton-state-debugger__tree-null {
                color: #aaa;
                font-style: italic;
            }
            
            .tekton-state-debugger__tree-undefined {
                color: #aaa;
                font-style: italic;
            }
            
            .tekton-state-debugger__tree-expand {
                color: #aaa;
                margin-right: 4px;
                font-family: monospace;
                cursor: pointer;
            }
            
            .tekton-state-debugger__entry {
                border-bottom: 1px solid #444;
                padding: 8px 0;
                margin-bottom: 8px;
            }
            
            .tekton-state-debugger__entry-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 4px;
            }
            
            .tekton-state-debugger__timestamp {
                color: #aaa;
                font-size: 10px;
            }
            
            .tekton-state-debugger__namespace {
                color: #ff7597;
                font-weight: bold;
            }
            
            .tekton-state-debugger__changes {
                margin-top: 4px;
                padding-left: 12px;
            }
            
            .tekton-state-debugger__change {
                margin: 2px 0;
            }
            
            .tekton-state-debugger__change-key {
                color: #bb86fc;
            }
            
            .tekton-state-debugger__snapshot {
                margin-bottom: 12px;
                padding-bottom: 8px;
                border-bottom: 1px solid #444;
            }
            
            .tekton-state-debugger__snapshot-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 4px;
            }
            
            .tekton-state-debugger__snapshot-title {
                font-weight: bold;
                color: #03dac6;
            }
            
            .tekton-state-debugger__performance {
                margin-bottom: 12px;
            }
            
            .tekton-state-debugger__stat {
                display: flex;
                justify-content: space-between;
                margin-bottom: 4px;
            }
            
            .tekton-state-debugger__stat-label {
                color: #bb86fc;
            }
            
            .tekton-state-debugger__stat-value {
                color: #86c1b9;
            }
            
            .tekton-state-debugger__chart {
                width: 100%;
                height: 100px;
                background-color: #333;
                border: 1px solid #555;
                margin-top: 8px;
                position: relative;
            }
            
            .tekton-state-debugger__chart-bar {
                position: absolute;
                bottom: 0;
                width: 4px;
                background-color: #03dac6;
            }
        `;
        
        // Create header
        const header = document.createElement('div');
        header.className = 'tekton-state-debugger__header';
        header.innerHTML = `
            <h3 class="tekton-state-debugger__title">Tekton State Debugger</h3>
            <button class="tekton-state-debugger__close">&times;</button>
        `;
        
        // Create tabs
        const tabs = document.createElement('div');
        tabs.className = 'tekton-state-debugger__tabs';
        tabs.innerHTML = `
            <div class="tekton-state-debugger__tab tekton-state-debugger__tab--active" data-tab="inspector">Inspector</div>
            <div class="tekton-state-debugger__tab" data-tab="history">History</div>
            <div class="tekton-state-debugger__tab" data-tab="snapshots">Snapshots</div>
            <div class="tekton-state-debugger__tab" data-tab="performance">Performance</div>
        `;
        
        // Create content
        const content = document.createElement('div');
        content.className = 'tekton-state-debugger__content';
        
        // Create footer
        const footer = document.createElement('div');
        footer.className = 'tekton-state-debugger__footer';
        footer.innerHTML = `
            <div>
                <label>
                    <input type="checkbox" class="tekton-state-debugger__log-toggle">
                    Log to console
                </label>
            </div>
            <div>
                <button class="tekton-state-debugger__button tekton-state-debugger__snapshot-button">Take Snapshot</button>
                <button class="tekton-state-debugger__button tekton-state-debugger__clear-button">Clear</button>
            </div>
        `;
        
        // Assemble container
        container.appendChild(styles);
        container.appendChild(header);
        container.appendChild(tabs);
        container.appendChild(content);
        container.appendChild(footer);
        
        // Add to document
        document.body.appendChild(container);
        this.container = container;
        
        // Add event listeners
        const closeButton = container.querySelector('.tekton-state-debugger__close');
        closeButton.addEventListener('click', () => this.hide());
        
        const tabButtons = container.querySelectorAll('.tekton-state-debugger__tab');
        tabButtons.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update active tab
                tabButtons.forEach(t => t.classList.remove('tekton-state-debugger__tab--active'));
                tab.classList.add('tekton-state-debugger__tab--active');
                
                // Update current view
                this.currentView = tab.getAttribute('data-tab');
                
                // Refresh view
                this._refreshView();
            });
        });
        
        const snapshotButton = container.querySelector('.tekton-state-debugger__snapshot-button');
        snapshotButton.addEventListener('click', () => this.takeSnapshot());
        
        const clearButton = container.querySelector('.tekton-state-debugger__clear-button');
        clearButton.addEventListener('click', () => this.clear());
        
        const logToggle = container.querySelector('.tekton-state-debugger__log-toggle');
        logToggle.checked = this.logEnabled;
        logToggle.addEventListener('change', () => {
            this.setLogging(logToggle.checked);
        });
    }
    
    /**
     * Set up keyboard shortcut (Ctrl+Shift+S)
     */
    _setupKeyboardShortcut() {
        window.addEventListener('keydown', (event) => {
            if (event.ctrlKey && event.shiftKey && event.key === 'S') {
                event.preventDefault();
                this.toggle();
            }
        });
    }
    
    /**
     * Patch StateManager to integrate debugging
     */
    _patchStateManager() {
        const stateManager = window.tektonUI.stateManager;
        const self = this;
        
        // Save original methods
        const originalSetState = stateManager.setState;
        
        // Enhance setState to track changes
        stateManager.setState = function(namespace, updates, options = {}) {
            // Start timing
            const startTime = performance.now();
            
            // Call original method
            const result = originalSetState.call(this, namespace, updates, options);
            
            // End timing
            const endTime = performance.now();
            const duration = endTime - startTime;
            
            // Track performance
            if (self.performanceEnabled) {
                self.performanceData.updates++;
                self.performanceData.totalTime += duration;
                self.performanceData.maxTime = Math.max(self.performanceData.maxTime, duration);
                
                // Add to chart data
                self._addPerformanceData(namespace, duration);
            }
            
            // Record for debugging if not silent and not in a transaction
            if (!options.silent && !this.transactionInProgress) {
                self._recordStateChange(namespace, updates, duration);
            }
            
            return result;
        };
        
        // Set debug mode
        stateManager.setDebug(true);
    }
    
    /**
     * Record a state change for debugging
     * 
     * @param {string} namespace - State namespace
     * @param {Object} changes - The changes made
     * @param {number} duration - Time taken to apply changes (ms)
     */
    _recordStateChange(namespace, changes, duration) {
        if (!this.historyData[namespace]) {
            this.historyData[namespace] = [];
        }
        
        // Add to history
        this.historyData[namespace].push({
            timestamp: new Date(),
            changes: JSON.parse(JSON.stringify(changes)),
            duration
        });
        
        // Trim history if it gets too large
        const maxHistory = 100;
        if (this.historyData[namespace].length > maxHistory) {
            this.historyData[namespace] = this.historyData[namespace].slice(-maxHistory);
        }
        
        // Refresh view if visible
        if (this.visible && this.currentView === 'history') {
            this._refreshView();
        }
        
        // Log to console if enabled
        if (this.logEnabled) {
            console.group(`[StateDebug] ${namespace} updated (${duration.toFixed(2)}ms)`);
            console.log('Changes:', changes);
            console.groupEnd();
        }
    }
    
    /**
     * Add performance data point
     * 
     * @param {string} namespace - State namespace
     * @param {number} duration - Update duration in ms
     */
    _addPerformanceData(namespace, duration) {
        if (!this.performanceData.updates) {
            this.performanceData.updates = [];
        }
        
        this.performanceData.updates.push({
            timestamp: Date.now(),
            namespace,
            duration
        });
        
        // Limit to 100 data points
        if (this.performanceData.updates.length > 100) {
            this.performanceData.updates.shift();
        }
        
        // Refresh view if visible
        if (this.visible && this.currentView === 'performance') {
            this._refreshView();
        }
    }
    
    /**
     * Take a snapshot of the current state
     */
    _takeSnapshot() {
        const stateManager = window.tektonUI.stateManager;
        if (!stateManager) return;
        
        const snapshot = {
            timestamp: new Date(),
            state: JSON.parse(JSON.stringify(stateManager.getSnapshot()))
        };
        
        this.stateSnapshots.push(snapshot);
        
        // Limit to 10 snapshots
        if (this.stateSnapshots.length > 10) {
            this.stateSnapshots.shift();
        }
        
        // Refresh view if visible
        if (this.visible && this.currentView === 'snapshots') {
            this._refreshView();
        }
    }
    
    /**
     * Refresh the current view
     */
    _refreshView() {
        if (!this.visible) return;
        
        const content = this.container.querySelector('.tekton-state-debugger__content');
        
        // Clear content
        content.innerHTML = '';
        
        // Show current view
        switch (this.currentView) {
            case 'inspector':
                this._renderInspectorView(content);
                break;
            case 'history':
                this._renderHistoryView(content);
                break;
            case 'snapshots':
                this._renderSnapshotsView(content);
                break;
            case 'performance':
                this._renderPerformanceView(content);
                break;
        }
    }
    
    /**
     * Render the state inspector view
     * 
     * @param {HTMLElement} container - The container element
     */
    _renderInspectorView(container) {
        const stateManager = window.tektonUI.stateManager;
        if (!stateManager) return;
        
        // Create toolbar
        const toolbar = document.createElement('div');
        toolbar.className = 'tekton-state-debugger__toolbar';
        
        // Create search input
        const search = document.createElement('input');
        search.type = 'text';
        search.className = 'tekton-state-debugger__search';
        search.placeholder = 'Filter state...';
        search.value = this.filter;
        search.addEventListener('input', () => {
            this.filter = search.value;
            this._refreshView();
        });
        
        // Create namespace select
        const select = document.createElement('select');
        select.className = 'tekton-state-debugger__select';
        
        // Add global option
        const globalOption = document.createElement('option');
        globalOption.value = '_all';
        globalOption.textContent = 'All Namespaces';
        select.appendChild(globalOption);
        
        // Add namespace options
        const namespaces = stateManager.getNamespaces();
        namespaces.forEach(namespace => {
            const option = document.createElement('option');
            option.value = namespace;
            option.textContent = namespace;
            select.appendChild(option);
        });
        
        select.addEventListener('change', () => {
            this._refreshView();
        });
        
        toolbar.appendChild(search);
        toolbar.appendChild(select);
        
        // Add toolbar to container
        container.appendChild(toolbar);
        
        // Get current state
        const state = stateManager.getSnapshot();
        
        // Filter by namespace if selected
        const selectedNamespace = select.value;
        const filteredState = selectedNamespace !== '_all' ? 
            { [selectedNamespace]: state[selectedNamespace] } : 
            state;
        
        // Render state tree
        const tree = document.createElement('div');
        tree.className = 'tekton-state-debugger__tree';
        
        // Render root object
        this._renderStateTree(tree, filteredState, '', this.filter);
        
        container.appendChild(tree);
    }
    
    /**
     * Render a state tree node
     * 
     * @param {HTMLElement} container - The container element
     * @param {*} value - The value to render
     * @param {string} path - The current path
     * @param {string} filter - The current filter text
     */
    _renderStateTree(container, value, path, filter) {
        // Handle null or undefined
        if (value === null || value === undefined) {
            const node = document.createElement('div');
            node.className = 'tekton-state-debugger__tree-node';
            
            if (path) {
                const keySpan = document.createElement('span');
                keySpan.className = 'tekton-state-debugger__tree-key';
                keySpan.textContent = this._getKeyFromPath(path);
                node.appendChild(keySpan);
                
                const colonSpan = document.createElement('span');
                colonSpan.className = 'tekton-state-debugger__tree-colon';
                colonSpan.textContent = ': ';
                node.appendChild(colonSpan);
            }
            
            const valueSpan = document.createElement('span');
            valueSpan.className = value === null ? 
                'tekton-state-debugger__tree-null' : 
                'tekton-state-debugger__tree-undefined';
            valueSpan.textContent = value === null ? 'null' : 'undefined';
            node.appendChild(valueSpan);
            
            container.appendChild(node);
            return;
        }
        
        // Handle arrays and objects
        if (typeof value === 'object') {
            const isArray = Array.isArray(value);
            const keys = Object.keys(value);
            
            // Skip empty objects/arrays if filtered
            if (keys.length === 0 && filter) {
                return;
            }
            
            const node = document.createElement('div');
            node.className = 'tekton-state-debugger__tree-node';
            
            if (path) {
                // Create expand/collapse icon
                const expandSpan = document.createElement('span');
                expandSpan.className = 'tekton-state-debugger__tree-expand';
                expandSpan.textContent = this.expandedPaths.has(path) ? '▼' : '▶';
                expandSpan.addEventListener('click', () => {
                    if (this.expandedPaths.has(path)) {
                        this.expandedPaths.delete(path);
                    } else {
                        this.expandedPaths.add(path);
                    }
                    this._refreshView();
                });
                node.appendChild(expandSpan);
                
                // Create key
                const keySpan = document.createElement('span');
                keySpan.className = 'tekton-state-debugger__tree-key';
                keySpan.textContent = this._getKeyFromPath(path);
                keySpan.addEventListener('click', () => {
                    if (this.expandedPaths.has(path)) {
                        this.expandedPaths.delete(path);
                    } else {
                        this.expandedPaths.add(path);
                    }
                    this._refreshView();
                });
                node.appendChild(keySpan);
                
                // Create colon
                const colonSpan = document.createElement('span');
                colonSpan.className = 'tekton-state-debugger__tree-colon';
                colonSpan.textContent = ': ';
                node.appendChild(colonSpan);
            }
            
            // Create value preview
            const valueSpan = document.createElement('span');
            valueSpan.className = 'tekton-state-debugger__tree-value';
            valueSpan.textContent = isArray ? 
                `Array(${keys.length})` : 
                `Object{${keys.length}}`;
            node.appendChild(valueSpan);
            
            container.appendChild(node);
            
            // Render children if expanded
            if (this.expandedPaths.has(path) || !path) {
                const childContainer = document.createElement('div');
                childContainer.style.paddingLeft = '16px';
                
                let visibleChildren = 0;
                
                keys.forEach(key => {
                    const childPath = path ? `${path}.${key}` : key;
                    const childValue = value[key];
                    
                    // Apply filter
                    if (filter) {
                        if (
                            childPath.toLowerCase().includes(filter.toLowerCase()) ||
                            (typeof childValue === 'string' && childValue.toLowerCase().includes(filter.toLowerCase()))
                        ) {
                            this._renderStateTree(childContainer, childValue, childPath, filter);
                            visibleChildren++;
                        }
                    } else {
                        this._renderStateTree(childContainer, childValue, childPath, filter);
                        visibleChildren++;
                    }
                });
                
                if (visibleChildren > 0) {
                    container.appendChild(childContainer);
                }
            }
            
            return;
        }
        
        // Handle primitive values
        const node = document.createElement('div');
        node.className = 'tekton-state-debugger__tree-node';
        
        // Create key if path exists
        if (path) {
            const keySpan = document.createElement('span');
            keySpan.className = 'tekton-state-debugger__tree-key';
            keySpan.textContent = this._getKeyFromPath(path);
            node.appendChild(keySpan);
            
            const colonSpan = document.createElement('span');
            colonSpan.className = 'tekton-state-debugger__tree-colon';
            colonSpan.textContent = ': ';
            node.appendChild(colonSpan);
        }
        
        // Create value based on type
        const valueSpan = document.createElement('span');
        
        switch (typeof value) {
            case 'string':
                valueSpan.className = 'tekton-state-debugger__tree-string';
                valueSpan.textContent = `"${value}"`;
                break;
            case 'number':
                valueSpan.className = 'tekton-state-debugger__tree-number';
                valueSpan.textContent = value;
                break;
            case 'boolean':
                valueSpan.className = 'tekton-state-debugger__tree-boolean';
                valueSpan.textContent = value ? 'true' : 'false';
                break;
            default:
                valueSpan.textContent = String(value);
        }
        
        node.appendChild(valueSpan);
        
        // Only append if it matches filter
        if (!filter || 
            path.toLowerCase().includes(filter.toLowerCase()) || 
            (typeof value === 'string' && value.toLowerCase().includes(filter.toLowerCase()))
        ) {
            container.appendChild(node);
        }
    }
    
    /**
     * Extract the key from a path
     * 
     * @param {string} path - The full path
     * @returns {string} - The key part
     */
    _getKeyFromPath(path) {
        const parts = path.split('.');
        return parts[parts.length - 1];
    }
    
    /**
     * Render the history view
     * 
     * @param {HTMLElement} container - The container element
     */
    _renderHistoryView(container) {
        // Create toolbar
        const toolbar = document.createElement('div');
        toolbar.className = 'tekton-state-debugger__toolbar';
        
        // Create namespace select
        const select = document.createElement('select');
        select.className = 'tekton-state-debugger__select';
        
        // Add all option
        const allOption = document.createElement('option');
        allOption.value = '_all';
        allOption.textContent = 'All Namespaces';
        select.appendChild(allOption);
        
        // Add namespace options
        Object.keys(this.historyData).forEach(namespace => {
            const option = document.createElement('option');
            option.value = namespace;
            option.textContent = namespace;
            select.appendChild(option);
        });
        
        select.addEventListener('change', () => {
            this._refreshView();
        });
        
        toolbar.appendChild(select);
        
        // Add toolbar to container
        container.appendChild(toolbar);
        
        // No history data
        if (Object.keys(this.historyData).length === 0) {
            const empty = document.createElement('div');
            empty.textContent = 'No state changes recorded yet.';
            empty.style.padding = '16px';
            empty.style.color = '#aaa';
            empty.style.fontStyle = 'italic';
            container.appendChild(empty);
            return;
        }
        
        // Filter history by namespace
        const selectedNamespace = select.value;
        let historyEntries = [];
        
        if (selectedNamespace === '_all') {
            // Collect all entries and sort by timestamp
            Object.entries(this.historyData).forEach(([namespace, entries]) => {
                entries.forEach(entry => {
                    historyEntries.push({
                        namespace,
                        ...entry
                    });
                });
            });
        } else {
            // Only entries for selected namespace
            historyEntries = (this.historyData[selectedNamespace] || []).map(entry => ({
                namespace: selectedNamespace,
                ...entry
            }));
        }
        
        // Sort by timestamp (newest first)
        historyEntries.sort((a, b) => b.timestamp - a.timestamp);
        
        // Render history entries
        historyEntries.forEach(entry => {
            const entryDiv = document.createElement('div');
            entryDiv.className = 'tekton-state-debugger__entry';
            
            // Entry header
            const header = document.createElement('div');
            header.className = 'tekton-state-debugger__entry-header';
            
            const namespace = document.createElement('span');
            namespace.className = 'tekton-state-debugger__namespace';
            namespace.textContent = entry.namespace;
            header.appendChild(namespace);
            
            const timestamp = document.createElement('span');
            timestamp.className = 'tekton-state-debugger__timestamp';
            timestamp.textContent = new Date(entry.timestamp).toLocaleTimeString();
            header.appendChild(timestamp);
            
            entryDiv.appendChild(header);
            
            // Performance info
            if (entry.duration !== undefined) {
                const performance = document.createElement('div');
                performance.textContent = `Update time: ${entry.duration.toFixed(2)}ms`;
                performance.style.fontSize = '11px';
                performance.style.color = '#aaa';
                performance.style.marginBottom = '4px';
                entryDiv.appendChild(performance);
            }
            
            // Changes
            const changes = document.createElement('div');
            changes.className = 'tekton-state-debugger__changes';
            
            Object.entries(entry.changes).forEach(([key, value]) => {
                const change = document.createElement('div');
                change.className = 'tekton-state-debugger__change';
                
                const keySpan = document.createElement('span');
                keySpan.className = 'tekton-state-debugger__change-key';
                keySpan.textContent = key;
                change.appendChild(keySpan);
                
                const colonSpan = document.createElement('span');
                colonSpan.textContent = ': ';
                change.appendChild(colonSpan);
                
                // Render value based on type
                const valueSpan = document.createElement('span');
                
                if (value === null) {
                    valueSpan.className = 'tekton-state-debugger__tree-null';
                    valueSpan.textContent = 'null';
                } else if (value === undefined) {
                    valueSpan.className = 'tekton-state-debugger__tree-undefined';
                    valueSpan.textContent = 'undefined';
                } else if (typeof value === 'object') {
                    valueSpan.className = 'tekton-state-debugger__tree-value';
                    valueSpan.textContent = Array.isArray(value) ? 
                        `Array(${value.length})` : 
                        `Object{${Object.keys(value).length}}`;
                } else if (typeof value === 'string') {
                    valueSpan.className = 'tekton-state-debugger__tree-string';
                    valueSpan.textContent = `"${value}"`;
                } else if (typeof value === 'number') {
                    valueSpan.className = 'tekton-state-debugger__tree-number';
                    valueSpan.textContent = value;
                } else if (typeof value === 'boolean') {
                    valueSpan.className = 'tekton-state-debugger__tree-boolean';
                    valueSpan.textContent = value ? 'true' : 'false';
                } else {
                    valueSpan.textContent = String(value);
                }
                
                change.appendChild(valueSpan);
                changes.appendChild(change);
            });
            
            entryDiv.appendChild(changes);
            container.appendChild(entryDiv);
        });
    }
    
    /**
     * Render the snapshots view
     * 
     * @param {HTMLElement} container - The container element
     */
    _renderSnapshotsView(container) {
        // No snapshots
        if (this.stateSnapshots.length === 0) {
            const empty = document.createElement('div');
            empty.textContent = 'No snapshots taken yet.';
            empty.style.padding = '16px';
            empty.style.color = '#aaa';
            empty.style.fontStyle = 'italic';
            container.appendChild(empty);
            return;
        }
        
        // Create search input
        const search = document.createElement('input');
        search.type = 'text';
        search.className = 'tekton-state-debugger__search';
        search.placeholder = 'Filter snapshots...';
        search.style.marginBottom = '12px';
        search.addEventListener('input', () => {
            this.filter = search.value;
            this._refreshView();
        });
        container.appendChild(search);
        
        // Render snapshots (newest first)
        [...this.stateSnapshots].reverse().forEach((snapshot, index) => {
            const snapshotDiv = document.createElement('div');
            snapshotDiv.className = 'tekton-state-debugger__snapshot';
            
            // Snapshot header
            const header = document.createElement('div');
            header.className = 'tekton-state-debugger__snapshot-header';
            
            const title = document.createElement('span');
            title.className = 'tekton-state-debugger__snapshot-title';
            title.textContent = `Snapshot #${this.stateSnapshots.length - index}`;
            header.appendChild(title);
            
            const timestamp = document.createElement('span');
            timestamp.className = 'tekton-state-debugger__timestamp';
            timestamp.textContent = new Date(snapshot.timestamp).toLocaleString();
            header.appendChild(timestamp);
            
            snapshotDiv.appendChild(header);
            
            // Snapshot state tree
            const tree = document.createElement('div');
            tree.style.paddingLeft = '0';
            this._renderStateTree(tree, snapshot.state, '', search.value);
            
            snapshotDiv.appendChild(tree);
            container.appendChild(snapshotDiv);
        });
    }
    
    /**
     * Render the performance view
     * 
     * @param {HTMLElement} container - The container element
     */
    _renderPerformanceView(container) {
        // Performance stats
        const stats = document.createElement('div');
        stats.className = 'tekton-state-debugger__performance';
        
        // Create stats rows
        const createStat = (label, value) => {
            const row = document.createElement('div');
            row.className = 'tekton-state-debugger__stat';
            
            const labelSpan = document.createElement('span');
            labelSpan.className = 'tekton-state-debugger__stat-label';
            labelSpan.textContent = label;
            row.appendChild(labelSpan);
            
            const valueSpan = document.createElement('span');
            valueSpan.className = 'tekton-state-debugger__stat-value';
            valueSpan.textContent = value;
            row.appendChild(valueSpan);
            
            return row;
        };
        
        // Enable performance monitoring
        const toggleDiv = document.createElement('div');
        toggleDiv.style.marginBottom = '16px';
        
        const toggle = document.createElement('label');
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = this.performanceEnabled;
        checkbox.addEventListener('change', () => {
            this.performanceEnabled = checkbox.checked;
            
            if (this.performanceEnabled) {
                this.performanceData.startTime = Date.now();
            }
        });
        
        toggle.appendChild(checkbox);
        toggle.appendChild(document.createTextNode(' Enable performance monitoring'));
        
        toggleDiv.appendChild(toggle);
        container.appendChild(toggleDiv);
        
        // Show stats if performance monitoring is enabled
        if (this.performanceEnabled) {
            // General stats
            const numUpdates = Array.isArray(this.performanceData.updates) ? 
                this.performanceData.updates.length : 
                this.performanceData.updates;
                
            stats.appendChild(createStat('Total updates', numUpdates));
            
            if (numUpdates > 0) {
                const avgTime = Array.isArray(this.performanceData.updates) ?
                    this.performanceData.updates.reduce((sum, update) => sum + update.duration, 0) / numUpdates :
                    this.performanceData.totalTime / numUpdates;
                    
                stats.appendChild(createStat('Average update time', `${avgTime.toFixed(2)}ms`));
                
                const maxTime = Array.isArray(this.performanceData.updates) ?
                    Math.max(...this.performanceData.updates.map(update => update.duration)) :
                    this.performanceData.maxTime;
                    
                stats.appendChild(createStat('Maximum update time', `${maxTime.toFixed(2)}ms`));
                
                // Time since monitoring started
                const elapsed = Math.floor((Date.now() - this.performanceData.startTime) / 1000);
                stats.appendChild(createStat('Monitoring time', `${elapsed}s`));
                
                // Updates per second
                const updatesPerSecond = numUpdates / (elapsed || 1);
                stats.appendChild(createStat('Updates per second', updatesPerSecond.toFixed(2)));
            }
            
            container.appendChild(stats);
            
            // Performance chart if we have update data
            if (Array.isArray(this.performanceData.updates) && this.performanceData.updates.length > 0) {
                // Chart container
                const chartTitle = document.createElement('h4');
                chartTitle.textContent = 'Update Duration (ms)';
                chartTitle.style.margin = '16px 0 8px 0';
                container.appendChild(chartTitle);
                
                const chart = document.createElement('div');
                chart.className = 'tekton-state-debugger__chart';
                
                // Find max duration for scaling
                const maxDuration = Math.max(...this.performanceData.updates.map(update => update.duration));
                
                // Render bars
                this.performanceData.updates.forEach((update, index) => {
                    const bar = document.createElement('div');
                    bar.className = 'tekton-state-debugger__chart-bar';
                    
                    // Position and size
                    const barWidth = Math.max(1, 100 / this.performanceData.updates.length);
                    const barHeight = (update.duration / maxDuration) * 90; // Max 90% of height
                    
                    bar.style.left = `${index * barWidth}%`;
                    bar.style.height = `${barHeight}%`;
                    bar.style.width = `${barWidth - 1}%`;
                    
                    // Tooltip
                    bar.title = `${update.namespace}: ${update.duration.toFixed(2)}ms`;
                    
                    chart.appendChild(bar);
                });
                
                container.appendChild(chart);
                
                // Chart legend
                const legend = document.createElement('div');
                legend.style.display = 'flex';
                legend.style.justifyContent = 'space-between';
                legend.style.fontSize = '10px';
                legend.style.color = '#aaa';
                legend.style.marginTop = '4px';
                
                const min = document.createElement('div');
                min.textContent = '0ms';
                legend.appendChild(min);
                
                const max = document.createElement('div');
                max.textContent = `${maxDuration.toFixed(2)}ms`;
                legend.appendChild(max);
                
                container.appendChild(legend);
            }
        } else {
            const message = document.createElement('div');
            message.textContent = 'Enable performance monitoring to see stats.';
            message.style.padding = '16px';
            message.style.color = '#aaa';
            message.style.fontStyle = 'italic';
            container.appendChild(message);
        }
    }
}

// Create and export the StateDebug instance
window.tektonUI = window.tektonUI || {};
window.tektonUI.StateDebug = StateDebug;

// Export a singleton instance
window.tektonUI.stateDebug = new StateDebug();

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize with default options
    window.tektonUI.stateDebug.init({
        logEnabled: false,
        performanceEnabled: false
    });
});