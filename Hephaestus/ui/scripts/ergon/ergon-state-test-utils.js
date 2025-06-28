/**
 * ErgonStateTestUtils.js
 * 
 * Testing utilities for the Ergon state management system.
 * These utilities help with testing state transitions, validating state shapes,
 * and mocking state-related behaviors.
 */

console.log('[FILE_TRACE] Loading: ergon-state-test-utils.js');
class ErgonStateTestUtils {
    constructor() {
        this.initialized = false;
        this.recordedActions = [];
        this.snapshots = {};
        this.mockResponses = {};
        this.testAgentData = [];
        this.testExecutions = [];
        this.assertions = [];
        this.subscriptionMocks = {};
    }
    
    /**
     * Initialize the test utilities
     * 
     * @param {Object} options - Configuration options
     * @returns {ErgonStateTestUtils} - The test utilities instance
     */
    init(options = {}) {
        if (this.initialized) return this;
        
        // Register in window.tektonUI
        if (!window.tektonUI) {
            window.tektonUI = {};
        }
        
        if (!window.tektonUI.testing) {
            window.tektonUI.testing = {};
        }
        
        window.tektonUI.testing.ergonState = this;
        
        // Configure test options
        this.recordState = options.recordState !== false;
        this.mockMode = options.mockMode === true;
        
        // Set up state recording if real state managers are available
        this._setupStateRecording();
        
        // Initialize test data
        this._initializeTestData();
        
        this.initialized = true;
        console.log('[ErgonStateTestUtils] Initialized');
        
        return this;
    }
    
    /**
     * Set up state recording to track changes
     * @private
     */
    _setupStateRecording() {
        const ergonStateManager = window.tektonUI.ergonStateManager;
        const stateManager = window.tektonUI.stateManager;
        
        if (!ergonStateManager || !stateManager) {
            console.warn('[ErgonStateTestUtils] State managers not available for recording');
            return;
        }
        
        // Create wrappers for state methods to record actions
        if (this.recordState) {
            // Wrap agent state methods
            const originalSetAgentState = ergonStateManager.setAgentState;
            ergonStateManager.setAgentState = (updates, options = {}) => {
                this._recordAction('setAgentState', updates, options);
                return originalSetAgentState.call(ergonStateManager, updates, options);
            };
            
            // Wrap execution state methods
            const originalSetExecutionState = ergonStateManager.setExecutionState;
            ergonStateManager.setExecutionState = (updates, options = {}) => {
                this._recordAction('setExecutionState', updates, options);
                return originalSetExecutionState.call(ergonStateManager, updates, options);
            };
            
            // Wrap settings methods
            const originalSetSettings = ergonStateManager.setSettings;
            ergonStateManager.setSettings = (updates, options = {}) => {
                this._recordAction('setSettings', updates, options);
                return originalSetSettings.call(ergonStateManager, updates, options);
            };
            
            console.log('[ErgonStateTestUtils] State recording enabled');
        }
    }
    
    /**
     * Initialize test data for mocking responses
     * @private
     */
    _initializeTestData() {
        // Create sample agents for testing
        this.testAgentData = [
            {
                id: '1',
                name: 'Test Agent 1',
                description: 'A test agent for unit testing',
                type: 'browser',
                model_name: 'gpt-4',
                status: 'active',
                created_at: new Date(Date.now() - 86400000).toISOString()
            },
            {
                id: '2',
                name: 'Test Agent 2',
                description: 'Another test agent',
                type: 'mail',
                model_name: 'claude-3',
                status: 'active',
                created_at: new Date(Date.now() - 43200000).toISOString()
            },
            {
                id: '3',
                name: 'Test Agent 3',
                description: 'Inactive test agent',
                type: 'github',
                model_name: 'gpt-4',
                status: 'inactive',
                created_at: new Date(Date.now() - 172800000).toISOString()
            }
        ];
        
        // Create sample executions for testing
        this.testExecutions = [
            {
                id: 'exec-1',
                agentId: '1',
                agentName: 'Test Agent 1',
                input: 'Test input 1',
                output: 'Test output 1',
                status: 'completed',
                startTime: new Date(Date.now() - 3600000).toISOString(),
                endTime: new Date(Date.now() - 3590000).toISOString(),
                duration: 10000
            },
            {
                id: 'exec-2',
                agentId: '1',
                agentName: 'Test Agent 1',
                input: 'Test input 2',
                output: 'Test output 2',
                status: 'completed',
                startTime: new Date(Date.now() - 7200000).toISOString(),
                endTime: new Date(Date.now() - 7180000).toISOString(),
                duration: 20000
            },
            {
                id: 'exec-3',
                agentId: '2',
                agentName: 'Test Agent 2',
                input: 'Test input 3',
                error: { message: 'Test error' },
                status: 'error',
                startTime: new Date(Date.now() - 1800000).toISOString(),
                endTime: new Date(Date.now() - 1790000).toISOString(),
                duration: 10000
            }
        ];
        
        // Set up mock responses for service methods
        this.mockResponses = {
            fetchAgents: this.testAgentData,
            fetchAgentById: (id) => this.testAgentData.find(agent => agent.id === id),
            createAgent: (data) => ({
                id: `${Date.now()}`,
                ...data,
                created_at: new Date().toISOString(),
                status: 'active'
            }),
            deleteAgent: () => ({ success: true }),
            runAgent: () => ({
                executionId: `exec-${Date.now()}`,
                status: 'running'
            }),
            fetchExecutionStatus: (id) => {
                const execution = this.testExecutions.find(exec => exec.id === id);
                return execution || { status: 'not_found' };
            },
            fetchAgentTypes: [
                { id: 'browser', name: 'Browser Agent', category: 'web' },
                { id: 'mail', name: 'Mail Agent', category: 'communication' },
                { id: 'github', name: 'GitHub Agent', category: 'development' }
            ],
            fetchSettings: {
                defaultModel: 'gpt-4',
                autoRefreshInterval: 30,
                defaultTemperature: 0.7,
                defaultMaxTokens: 2000,
                showAdvancedOptions: false,
                developerMode: false,
                apiEndpoint: '/api/ergon',
                ui: {
                    theme: 'system',
                    compactMode: false,
                    showExecutionDetails: true,
                    showAgentDetails: true
                }
            }
        };
    }
    
    /**
     * Record a state action for testing
     * 
     * @param {string} actionType - Type of action
     * @param {Object} data - Action data
     * @param {Object} options - Action options
     * @private
     */
    _recordAction(actionType, data, options = {}) {
        if (!this.recordState) return;
        
        this.recordedActions.push({
            type: actionType,
            data,
            options,
            timestamp: Date.now()
        });
        
        // Limit stored actions to prevent memory issues
        if (this.recordedActions.length > 100) {
            this.recordedActions = this.recordedActions.slice(-100);
        }
    }
    
    /**
     * Create a state snapshot
     * 
     * @param {string} name - Snapshot name
     * @returns {Object} - The snapshot data
     */
    takeSnapshot(name = `snapshot-${Date.now()}`) {
        const ergonStateManager = window.tektonUI.ergonStateManager;
        
        if (!ergonStateManager) {
            console.warn('[ErgonStateTestUtils] State manager not available for snapshot');
            return null;
        }
        
        const snapshot = {
            agentState: ergonStateManager.getAgentState(),
            executionState: ergonStateManager.getExecutionState(),
            settings: ergonStateManager.getSettings(),
            agentTypes: ergonStateManager.getAgentTypes(),
            timestamp: Date.now()
        };
        
        this.snapshots[name] = snapshot;
        return snapshot;
    }
    
    /**
     * Get a state snapshot
     * 
     * @param {string} name - Snapshot name
     * @returns {Object} - The snapshot data
     */
    getSnapshot(name) {
        return this.snapshots[name] || null;
    }
    
    /**
     * Compare two snapshots
     * 
     * @param {string} snapshot1Name - First snapshot name
     * @param {string} snapshot2Name - Second snapshot name
     * @param {Array} keyPaths - Specific key paths to compare (dot notation)
     * @returns {Object} - Comparison results
     */
    compareSnapshots(snapshot1Name, snapshot2Name, keyPaths = []) {
        const snapshot1 = this.snapshots[snapshot1Name];
        const snapshot2 = this.snapshots[snapshot2Name];
        
        if (!snapshot1 || !snapshot2) {
            return { success: false, error: 'Snapshot not found' };
        }
        
        const differences = {};
        let hasChanges = false;
        
        // Helper function to get nested value
        const getNestedValue = (obj, path) => {
            const keys = path.split('.');
            let current = obj;
            
            for (const key of keys) {
                if (current === undefined || current === null) {
                    return undefined;
                }
                current = current[key];
            }
            
            return current;
        };
        
        // Compare specific paths if provided
        if (keyPaths.length > 0) {
            keyPaths.forEach(path => {
                const value1 = getNestedValue(snapshot1, path);
                const value2 = getNestedValue(snapshot2, path);
                
                if (JSON.stringify(value1) !== JSON.stringify(value2)) {
                    differences[path] = {
                        before: value1,
                        after: value2
                    };
                    hasChanges = true;
                }
            });
        } else {
            // Compare entire snapshots
            ['agentState', 'executionState', 'settings', 'agentTypes'].forEach(section => {
                if (JSON.stringify(snapshot1[section]) !== JSON.stringify(snapshot2[section])) {
                    differences[section] = {
                        before: snapshot1[section],
                        after: snapshot2[section]
                    };
                    hasChanges = true;
                }
            });
        }
        
        return {
            success: true,
            hasChanges,
            differences,
            snapshot1Time: snapshot1.timestamp,
            snapshot2Time: snapshot2.timestamp,
            timeDiff: snapshot2.timestamp - snapshot1.timestamp
        };
    }
    
    /**
     * Clear all recorded actions
     */
    clearActions() {
        this.recordedActions = [];
    }
    
    /**
     * Get all recorded actions
     * 
     * @param {Object} options - Filter options
     * @returns {Array} - Recorded actions
     */
    getActions(options = {}) {
        let actions = [...this.recordedActions];
        
        // Apply filters if provided
        if (options.type) {
            actions = actions.filter(action => action.type === options.type);
        }
        
        if (options.after) {
            actions = actions.filter(action => action.timestamp > options.after);
        }
        
        if (options.before) {
            actions = actions.filter(action => action.timestamp < options.before);
        }
        
        if (options.limit) {
            actions = actions.slice(-options.limit);
        }
        
        return actions;
    }
    
    /**
     * Create a test agent in the state
     * 
     * @param {Object} agentData - Agent data
     * @returns {Object} - Created agent
     */
    createTestAgent(agentData = {}) {
        const ergonStateManager = window.tektonUI.ergonStateManager;
        
        if (!ergonStateManager) {
            console.warn('[ErgonStateTestUtils] State manager not available for test agent creation');
            return null;
        }
        
        // Create agent with default test data and provided overrides
        const agent = {
            id: `test-${Date.now()}`,
            name: `Test Agent ${Date.now()}`,
            description: 'Test agent created by ErgonStateTestUtils',
            type: 'test',
            model_name: 'test-model',
            status: 'active',
            created_at: new Date().toISOString(),
            ...agentData
        };
        
        // Add to test agent data
        this.testAgentData.push(agent);
        
        // Add to state
        ergonStateManager.addOrUpdateAgent(agent);
        
        return agent;
    }
    
    /**
     * Create a test execution in the state
     * 
     * @param {Object} executionData - Execution data
     * @returns {Object} - Created execution
     */
    createTestExecution(executionData = {}) {
        const ergonStateManager = window.tektonUI.ergonStateManager;
        
        if (!ergonStateManager) {
            console.warn('[ErgonStateTestUtils] State manager not available for test execution creation');
            return null;
        }
        
        // Create execution with default test data and provided overrides
        const executionId = executionData.id || `test-exec-${Date.now()}`;
        const execution = {
            id: executionId,
            agentId: executionData.agentId || 'test-agent',
            agentName: executionData.agentName || 'Test Agent',
            input: executionData.input || 'Test input',
            status: executionData.status || 'running',
            startTime: executionData.startTime || new Date().toISOString()
        };
        
        // Add to test execution data
        this.testExecutions.push(execution);
        
        // Add to state based on status
        if (execution.status === 'running') {
            ergonStateManager.trackExecution(execution);
        } else if (execution.status === 'completed') {
            ergonStateManager.trackExecution({
                ...execution,
                status: 'running'
            });
            
            ergonStateManager.completeExecution(executionId, {
                output: executionData.output || 'Test output',
                status: 'completed',
                endTime: executionData.endTime || new Date().toISOString(),
                duration: executionData.duration || 1000
            });
        } else if (execution.status === 'error') {
            ergonStateManager.trackExecution({
                ...execution,
                status: 'running'
            });
            
            ergonStateManager.setExecutionError(executionId, {
                message: executionData.error?.message || 'Test error',
                endTime: executionData.endTime || new Date().toISOString(),
                duration: executionData.duration || 1000
            });
        }
        
        return execution;
    }
    
    /**
     * Create a mock subscription that can be tested
     * 
     * @param {string} name - Subscription name
     * @param {function} callback - Subscription callback
     * @param {Object} options - Subscription options
     * @returns {Object} - Subscription object
     */
    createTestSubscription(name, callback, options = {}) {
        // Create subscription info
        const subscriptionInfo = {
            name,
            callback,
            options,
            callCount: 0,
            lastCalledWith: null,
            created: Date.now(),
            calls: []
        };
        
        // Create wrapper for the callback
        const wrappedCallback = (changes, state) => {
            subscriptionInfo.callCount++;
            subscriptionInfo.lastCalledWith = { changes, state };
            subscriptionInfo.calls.push({ 
                changes, 
                state, 
                timestamp: Date.now() 
            });
            
            // Ensure calls array doesn't grow too large
            if (subscriptionInfo.calls.length > 50) {
                subscriptionInfo.calls = subscriptionInfo.calls.slice(-50);
            }
            
            // Call the original callback
            return callback(changes, state);
        };
        
        // Create the actual subscription based on namespace
        let subscription;
        const ergonStateManager = window.tektonUI.ergonStateManager;
        
        if (!ergonStateManager) {
            console.warn('[ErgonStateTestUtils] State manager not available for test subscription');
            return null;
        }
        
        if (options.namespace === 'agent' || !options.namespace) {
            subscription = ergonStateManager.subscribeToAgentState(wrappedCallback, options);
        } else if (options.namespace === 'execution') {
            subscription = ergonStateManager.subscribeToExecutionState(wrappedCallback, options);
        } else if (options.namespace === 'settings') {
            subscription = ergonStateManager.subscribeToSettings(wrappedCallback, options);
        } else if (options.namespace === 'agentTypes') {
            subscription = ergonStateManager.subscribeToAgentTypes(wrappedCallback, options);
        }
        
        // Store subscription info
        subscriptionInfo.id = subscription;
        this.subscriptionMocks[name] = subscriptionInfo;
        
        return subscriptionInfo;
    }
    
    /**
     * Get information about a test subscription
     * 
     * @param {string} name - Subscription name
     * @returns {Object} - Subscription info
     */
    getSubscription(name) {
        return this.subscriptionMocks[name] || null;
    }
    
    /**
     * Assert a condition about the state
     * 
     * @param {string} name - Assertion name
     * @param {function} conditionFn - Condition function that returns boolean
     * @returns {Object} - Assertion result
     */
    assert(name, conditionFn) {
        const ergonStateManager = window.tektonUI.ergonStateManager;
        
        if (!ergonStateManager) {
            const result = {
                name,
                success: false,
                error: 'State manager not available',
                timestamp: Date.now()
            };
            this.assertions.push(result);
            return result;
        }
        
        try {
            const result = !!conditionFn({
                agentState: ergonStateManager.getAgentState(),
                executionState: ergonStateManager.getExecutionState(),
                settings: ergonStateManager.getSettings(),
                agentTypes: ergonStateManager.getAgentTypes()
            });
            
            const assertion = {
                name,
                success: result,
                timestamp: Date.now()
            };
            
            this.assertions.push(assertion);
            return assertion;
        } catch (error) {
            const result = {
                name,
                success: false,
                error: error.message || String(error),
                timestamp: Date.now()
            };
            this.assertions.push(result);
            return result;
        }
    }
    
    /**
     * Get all assertions or filtered by name
     * 
     * @param {string} name - Optional assertion name filter
     * @returns {Array} - Assertion results
     */
    getAssertions(name = null) {
        if (name) {
            return this.assertions.filter(a => a.name === name);
        }
        return this.assertions;
    }
    
    /**
     * Reset the state for testing
     * 
     * @param {Object} options - Reset options
     */
    resetTestState(options = {}) {
        const ergonStateManager = window.tektonUI.ergonStateManager;
        
        if (!ergonStateManager) {
            console.warn('[ErgonStateTestUtils] State manager not available for reset');
            return;
        }
        
        // Clear recorded data
        this.clearActions();
        
        if (options.clearAssertions !== false) {
            this.assertions = [];
        }
        
        if (options.clearSnapshots !== false) {
            this.snapshots = {};
        }
        
        // Reset state namespaces
        ergonStateManager.setAgentState({
            agentList: [],
            agentIndex: {},
            agentFilters: {
                search: '',
                type: 'all',
                status: 'all',
                sortBy: 'name'
            },
            activeAgent: null,
            isLoading: false,
            lastError: null,
            lastUpdated: new Date().toISOString()
        });
        
        ergonStateManager.setExecutionState({
            activeExecutions: {},
            historicalExecutions: {},
            executionFilters: {
                agentId: null,
                status: 'all',
                timeRange: 'all',
                sortBy: 'timestamp'
            },
            isLoading: false,
            lastError: null
        });
        
        // Only reset UI settings, keep server settings
        const currentSettings = ergonStateManager.getSettings();
        if (currentSettings) {
            ergonStateManager.setSettings({
                ui: {
                    theme: 'system',
                    compactMode: false,
                    showExecutionDetails: true,
                    showAgentDetails: true
                }
            });
        }
        
        console.log('[ErgonStateTestUtils] State reset completed');
    }
    
    /**
     * Mock a service method in ErgonService
     * 
     * @param {string} methodName - Method name to mock
     * @param {function|*} mockImplementation - Mock implementation or return value
     * @returns {function} - Function to restore original method
     */
    mockServiceMethod(methodName, mockImplementation) {
        const ergonService = window.tektonUI.ergonService;
        
        if (!ergonService) {
            console.warn('[ErgonStateTestUtils] ErgonService not available for mocking');
            return () => {};
        }
        
        // Save original method
        const originalMethod = ergonService[methodName];
        
        if (!originalMethod) {
            console.warn(`[ErgonStateTestUtils] Method ${methodName} not found in ErgonService`);
            return () => {};
        }
        
        // Create mock
        if (typeof mockImplementation === 'function') {
            ergonService[methodName] = mockImplementation;
        } else {
            ergonService[methodName] = () => Promise.resolve(mockImplementation);
        }
        
        // Return function to restore original
        return () => {
            ergonService[methodName] = originalMethod;
        };
    }
    
    /**
     * Restore all mocked methods
     */
    restoreAllMocks() {
        console.log('[ErgonStateTestUtils] Mock restoration not implemented yet');
    }
}

// Create and export the ErgonStateTestUtils instance
window.tektonUI = window.tektonUI || {};
window.tektonUI.ErgonStateTestUtils = ErgonStateTestUtils;

// Conditionally export a singleton instance in development environments
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('[ErgonStateTestUtils] Creating test utilities instance in development environment');
    window.tektonUI.ergonStateTest = new ErgonStateTestUtils();
    
    // Auto-initialize in development
    document.addEventListener('DOMContentLoaded', () => {
        // Initialize after state manager is ready
        const checkStateManager = () => {
            if (window.tektonUI.ergonStateManager && window.tektonUI.stateManager) {
                // Initialize with default options
                window.tektonUI.ergonStateTest.init();
            } else {
                // Wait for state manager to initialize
                setTimeout(checkStateManager, 100);
            }
        };
        
        checkStateManager();
    });
}