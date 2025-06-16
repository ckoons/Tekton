/**
 * Sophia Component
 * AI Intelligence Measurement & Continuous Improvement interface
 */

class SophiaComponent {
    constructor() {
        this.state = {
            initialized: false,
            activeTab: 'metrics', // Default tab is Metrics
            metricsLoaded: false,
            intelligenceLoaded: false,
            experimentsLoaded: false,
            recommendationsLoaded: false,
            components: []
        };
    }
    
    /**
     * Initialize the component
     */
    init() {
        console.log('[SOPHIA] Initializing Sophia component');
        if (window.TektonDebug) TektonDebug.info('sophiaComponent', 'Initializing Sophia component');

        // If already initialized, just activate
        if (this.state.initialized) {
            console.log('[SOPHIA] Sophia component already initialized, just activating');
            if (window.TektonDebug) TektonDebug.debug('sophiaComponent', 'Already initialized, just activating');
            this.activateComponent();
            return this;
        }

        // HTML panel is already active and displayed by the component loader
        // We don't need to manipulate it here

        // Initialize component functionality
        // The HTML is already loaded by the component loader
        this.setupEventListeners();
        this.loadComponents();

        // Mark as initialized
        this.state.initialized = true;

        console.log('[SOPHIA] Sophia component initialized');
        return this;
    }
    
    /**
     * Activate the component interface
     */
    activateComponent() {
        console.log('[SOPHIA] Activating Sophia component');

        // We no longer need to manipulate the panels or global DOM
        // Our component loader handles this for us

        // Find our component container
        const sophiaContainer = document.querySelector('.sophia');
        if (sophiaContainer) {
            // We don't need to set dimensions because the container
            // already has width and height set to 100% in the CSS
            console.log('[SOPHIA] Sophia container found and activated');
        }

        // Load initial data for default tab
        this.loadTabContent(this.state.activeTab);
    }
    
    /**
     * Set up event listeners for the component
     */
    setupEventListeners() {
        try {
            // Find Sophia container with BEM naming
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) {
                console.error('[SOPHIA] Could not find sophia container');
                return;
            }
            
            // Set up send button for chat
            const sendButton = sophiaContainer.querySelector('#send-button');
            if (sendButton) {
                sendButton.addEventListener('click', () => this.handleChatSend());
            }
            
            // Set up chat input for Enter key
            const chatInput = sophiaContainer.querySelector('#chat-input');
            if (chatInput) {
                chatInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        this.handleChatSend();
                    }
                });
            }
            
            // Set up refresh metrics button
            const refreshButton = sophiaContainer.querySelector('#refresh-metrics-btn');
            if (refreshButton) {
                refreshButton.addEventListener('click', () => this.refreshMetrics());
            }
            
            // Set up add measurement button
            const addMeasurementBtn = sophiaContainer.querySelector('#add-measurement-btn');
            if (addMeasurementBtn) {
                addMeasurementBtn.addEventListener('click', () => this.showNewMeasurementForm());
            }
            
            // Set up compare button
            const compareBtn = sophiaContainer.querySelector('#sophia-compare-btn');
            if (compareBtn) {
                compareBtn.addEventListener('click', () => this.compareComponents());
            }
            
            // Set up new experiment button
            const newExperimentBtn = sophiaContainer.querySelector('#new-experiment-btn');
            if (newExperimentBtn) {
                newExperimentBtn.addEventListener('click', () => this.showNewExperimentForm());
            }
            
            // Set up new recommendation button
            const newRecommendationBtn = sophiaContainer.querySelector('#new-recommendation-btn');
            if (newRecommendationBtn) {
                newRecommendationBtn.addEventListener('click', () => this.showNewRecommendationForm());
            }
            
            // Setup filters
            this.setupFilters(sophiaContainer);
            
            console.log('[SOPHIA] Event listeners set up');
        } catch (error) {
            console.error('[SOPHIA] Error setting up event listeners:', error);
        }
    }
    
    /**
     * Set up filter event listeners
     * @param {HTMLElement} container - The Sophia container element
     */
    setupFilters(container) {
        try {
            // Metrics filters
            const metricsComponentFilter = container.querySelector('#sophia-metrics-component-filter');
            const metricsTypeFilter = container.querySelector('#sophia-metrics-type-filter');
            const metricsTimeRangeFilter = container.querySelector('#sophia-metrics-timerange');
            
            if (metricsComponentFilter) {
                metricsComponentFilter.addEventListener('change', () => this.filterMetrics());
            }
            
            if (metricsTypeFilter) {
                metricsTypeFilter.addEventListener('change', () => this.filterMetrics());
            }
            
            if (metricsTimeRangeFilter) {
                metricsTimeRangeFilter.addEventListener('change', () => this.filterMetrics());
            }
            
            // Intelligence filters
            const intelligenceComponentFilter = container.querySelector('#sophia-intelligence-component-filter');
            const intelligenceDimensionFilter = container.querySelector('#sophia-intelligence-dimension-filter');
            
            if (intelligenceComponentFilter) {
                intelligenceComponentFilter.addEventListener('change', () => this.filterIntelligence());
            }
            
            if (intelligenceDimensionFilter) {
                intelligenceDimensionFilter.addEventListener('change', () => this.filterIntelligence());
            }
            
            // Experiments filters
            const experimentsStatusFilter = container.querySelector('#sophia-experiments-status-filter');
            const experimentsTypeFilter = container.querySelector('#sophia-experiments-type-filter');
            
            if (experimentsStatusFilter) {
                experimentsStatusFilter.addEventListener('change', () => this.filterExperiments());
            }
            
            if (experimentsTypeFilter) {
                experimentsTypeFilter.addEventListener('change', () => this.filterExperiments());
            }
            
            // Recommendations filters
            const recommendationsStatusFilter = container.querySelector('#sophia-recommendations-status-filter');
            const recommendationsPriorityFilter = container.querySelector('#sophia-recommendations-priority-filter');
            const recommendationsComponentFilter = container.querySelector('#sophia-recommendations-component-filter');
            
            if (recommendationsStatusFilter) {
                recommendationsStatusFilter.addEventListener('change', () => this.filterRecommendations());
            }
            
            if (recommendationsPriorityFilter) {
                recommendationsPriorityFilter.addEventListener('change', () => this.filterRecommendations());
            }
            
            if (recommendationsComponentFilter) {
                recommendationsComponentFilter.addEventListener('change', () => this.filterRecommendations());
            }
            
            console.log('[SOPHIA] Filters set up');
        } catch (error) {
            console.error('[SOPHIA] Error setting up filters:', error);
        }
    }
    
    /**
     * Load Tekton components list
     */
    async loadComponents() {
        try {
            console.log('[SOPHIA] Loading components list');
            
            // Sample components list - in a real implementation this would be retrieved from API
            this.state.components = [
                { id: 'rhetor', name: 'Rhetor' },
                { id: 'athena', name: 'Athena' },
                { id: 'engram', name: 'Engram' },
                { id: 'hermes', name: 'Hermes' },
                { id: 'harmonia', name: 'Harmonia' },
                { id: 'ergon', name: 'Ergon' },
                { id: 'telos', name: 'Telos' },
                { id: 'terma', name: 'Terma' }
            ];
            
            // Update component selectors in the UI
            this.updateComponentSelectors();
            
            console.log('[SOPHIA] Components loaded:', this.state.components.length);
        } catch (error) {
            console.error('[SOPHIA] Error loading components:', error);
        }
    }
    
    /**
     * Update component selectors in the UI
     */
    updateComponentSelectors() {
        try {
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            // Get all selectors that need to be populated with components
            const selectors = [
                '#sophia-metrics-component-filter',
                '#sophia-intelligence-component-filter',
                '#sophia-recommendations-component-filter',
                '#sophia-comparison-component1',
                '#sophia-comparison-component2'
            ];
            
            selectors.forEach(selector => {
                const selectElement = sophiaContainer.querySelector(selector);
                if (!selectElement) return;
                
                // Save current value if any
                const currentValue = selectElement.value;
                
                // Clear options (except the first one)
                while (selectElement.options.length > 1) {
                    selectElement.remove(1);
                }
                
                // Add component options
                this.state.components.forEach(component => {
                    const option = document.createElement('option');
                    option.value = component.id;
                    option.textContent = component.name;
                    selectElement.appendChild(option);
                });
                
                // Restore selected value if possible
                if (currentValue && Array.from(selectElement.options).some(opt => opt.value === currentValue)) {
                    selectElement.value = currentValue;
                }
            });
            
            console.log('[SOPHIA] Component selectors updated');
        } catch (error) {
            console.error('[SOPHIA] Error updating component selectors:', error);
        }
    }
    
    /**
     * Load content specific to a tab
     * @param {string} tabId - The ID of the tab to load content for
     */
    loadTabContent(tabId) {
        console.log(`[SOPHIA] Loading content for ${tabId} tab`);

        switch (tabId) {
            case 'metrics':
                if (!this.state.metricsLoaded) {
                    this.loadMetricsData();
                    this.state.metricsLoaded = true;
                }
                break;
            case 'intelligence':
                if (!this.state.intelligenceLoaded) {
                    this.loadIntelligenceData();
                    this.state.intelligenceLoaded = true;
                }
                break;
            case 'experiments':
                if (!this.state.experimentsLoaded) {
                    this.loadExperiments();
                    this.state.experimentsLoaded = true;
                }
                break;
            case 'recommendations':
                if (!this.state.recommendationsLoaded) {
                    this.loadRecommendations();
                    this.state.recommendationsLoaded = true;
                }
                break;
            case 'researchchat':
                // Research chat is already set up by default
                break;
            case 'teamchat':
                // Team chat is already set up by default
                break;
        }
    }
    
    /**
     * Update chat input placeholder based on active tab
     * @param {string} activeTab - The currently active tab
     */
    updateChatPlaceholder(activeTab) {
        // Find Sophia container with BEM naming
        const container = document.querySelector('.sophia');
        if (!container) return;

        // Get the chat input within our container with BEM class
        const chatInput = container.querySelector('.sophia__chat-input');
        if (!chatInput) return;

        switch(activeTab) {
            case 'metrics':
                chatInput.placeholder = "Ask about metrics, trends, or performance insights...";
                break;
            case 'intelligence':
                chatInput.placeholder = "Ask about intelligence dimensions, measurements, or comparisons...";
                break;
            case 'experiments':
                chatInput.placeholder = "Ask about experiments, test strategies, or results...";
                break;
            case 'recommendations':
                chatInput.placeholder = "Ask about recommendations or improvement suggestions...";
                break;
            case 'researchchat':
                chatInput.placeholder = "Enter research questions or AI intelligence queries...";
                break;
            case 'teamchat':
                chatInput.placeholder = "Enter team chat message for all Tekton components";
                break;
            default:
                chatInput.placeholder = "Enter message...";
        }
    }
    
    /**
     * Load metrics data for the Metrics tab
     */
    async loadMetricsData() {
        try {
            console.log('[SOPHIA] Loading metrics data');
            
            // Simulate API call to get metrics data
            setTimeout(() => {
                // Render sample metrics charts
                this.renderMetricsCharts();
                console.log('[SOPHIA] Metrics data loaded and charts rendered');
            }, 1000);
        } catch (error) {
            console.error('[SOPHIA] Error loading metrics data:', error);
        }
    }
    
    /**
     * Refresh metrics data
     */
    refreshMetrics() {
        console.log('[SOPHIA] Refreshing metrics data');
        this.loadMetricsData();
    }
    
    /**
     * Filter metrics based on selected filters
     */
    filterMetrics() {
        try {
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            const componentFilter = sophiaContainer.querySelector('#sophia-metrics-component-filter');
            const typeFilter = sophiaContainer.querySelector('#sophia-metrics-type-filter');
            const timeRangeFilter = sophiaContainer.querySelector('#sophia-metrics-timerange');
            
            if (!componentFilter || !typeFilter || !timeRangeFilter) return;
            
            const component = componentFilter.value;
            const type = typeFilter.value;
            const timeRange = timeRangeFilter.value;
            
            console.log(`[SOPHIA] Filtering metrics - Component: ${component || 'All'}, Type: ${type || 'All'}, Time Range: ${timeRange}`);
            
            // In a real implementation, this would reload the charts with filtered data
            // For now, let's simulate reloading the charts
            this.renderMetricsCharts();
        } catch (error) {
            console.error('[SOPHIA] Error filtering metrics:', error);
        }
    }
    
    /**
     * Render metrics charts with sample data
     */
    renderMetricsCharts() {
        try {
            console.log('[SOPHIA] Rendering metrics charts');
            
            // For this implementation, just insert placeholders in the chart containers
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            const chartContainers = [
                '#sophia-performance-chart',
                '#sophia-resource-chart',
                '#sophia-communication-chart',
                '#sophia-error-chart'
            ];
            
            chartContainers.forEach(selector => {
                const container = sophiaContainer.querySelector(selector);
                if (!container) return;
                
                const chartTitle = selector.split('-')[1];
                
                container.innerHTML = `
                    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
                        <div style="font-size: 16px; color: #666; margin-bottom: 10px;">${chartTitle.charAt(0).toUpperCase() + chartTitle.slice(1)} Chart</div>
                        <div style="color: #999; font-size: 14px;">Sample ${chartTitle} data visualization</div>
                    </div>
                `;
            });
        } catch (error) {
            console.error('[SOPHIA] Error rendering metrics charts:', error);
        }
    }
    
    /**
     * Load intelligence data for the Intelligence tab
     */
    async loadIntelligenceData() {
        try {
            console.log('[SOPHIA] Loading intelligence data');
            
            // Simulate API call to get intelligence data
            setTimeout(() => {
                // Render radar chart and dimension table
                this.renderIntelligenceCharts();
                console.log('[SOPHIA] Intelligence data loaded and visualizations rendered');
            }, 1000);
        } catch (error) {
            console.error('[SOPHIA] Error loading intelligence data:', error);
        }
    }
    
    /**
     * Filter intelligence data based on selected filters
     */
    filterIntelligence() {
        try {
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            const componentFilter = sophiaContainer.querySelector('#sophia-intelligence-component-filter');
            const dimensionFilter = sophiaContainer.querySelector('#sophia-intelligence-dimension-filter');
            
            if (!componentFilter || !dimensionFilter) return;
            
            const component = componentFilter.value;
            const dimension = dimensionFilter.value;
            
            console.log(`[SOPHIA] Filtering intelligence - Component: ${component || 'All'}, Dimension: ${dimension || 'All'}`);
            
            // In a real implementation, this would reload the charts with filtered data
            // For now, let's simulate reloading the charts
            this.renderIntelligenceCharts();
        } catch (error) {
            console.error('[SOPHIA] Error filtering intelligence:', error);
        }
    }
    
    /**
     * Render intelligence visualizations with sample data
     */
    renderIntelligenceCharts() {
        try {
            console.log('[SOPHIA] Rendering intelligence visualizations');
            
            // For this implementation, just insert placeholders in the chart containers
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            // Radar chart
            const radarChart = sophiaContainer.querySelector('#sophia-radar-chart');
            if (radarChart) {
                radarChart.innerHTML = `
                    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
                        <div style="font-size: 16px; color: #666; margin-bottom: 10px;">Intelligence Radar Chart</div>
                        <div style="color: #999; font-size: 14px;">Sample intelligence dimension visualization</div>
                    </div>
                `;
            }
            
            // Dimension table
            const dimensionTable = sophiaContainer.querySelector('#sophia-dimension-table');
            if (dimensionTable) {
                dimensionTable.innerHTML = `
                    <table class="sophia__table">
                        <thead>
                            <tr>
                                <th>Dimension</th>
                                <th>Score</th>
                                <th>Benchmark</th>
                                <th>Percentile</th>
                                <th>Trend</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Language Processing</td>
                                <td>87</td>
                                <td>82</td>
                                <td>75th</td>
                                <td>+5%</td>
                            </tr>
                            <tr>
                                <td>Reasoning</td>
                                <td>92</td>
                                <td>79</td>
                                <td>90th</td>
                                <td>+7%</td>
                            </tr>
                            <tr>
                                <td>Learning</td>
                                <td>78</td>
                                <td>73</td>
                                <td>65th</td>
                                <td>+3%</td>
                            </tr>
                            <tr>
                                <td>Creativity</td>
                                <td>84</td>
                                <td>71</td>
                                <td>85th</td>
                                <td>+9%</td>
                            </tr>
                            <tr>
                                <td>Problem Solving</td>
                                <td>91</td>
                                <td>80</td>
                                <td>88th</td>
                                <td>+6%</td>
                            </tr>
                        </tbody>
                    </table>
                `;
            }
            
            // Comparison chart
            const comparisonChart = sophiaContainer.querySelector('#sophia-comparison-chart');
            if (comparisonChart) {
                comparisonChart.innerHTML = `
                    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
                        <div style="font-size: 16px; color: #666; margin-bottom: 10px;">Component Comparison Chart</div>
                        <div style="color: #999; font-size: 14px;">Select components above to compare intelligence dimensions</div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('[SOPHIA] Error rendering intelligence charts:', error);
        }
    }
    
    /**
     * Show new measurement form
     */
    showNewMeasurementForm() {
        console.log('[SOPHIA] Showing new measurement form');
        alert('New Intelligence Measurement form would appear here');
    }
    
    /**
     * Compare components based on selected options
     */
    compareComponents() {
        try {
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            const component1Select = sophiaContainer.querySelector('#sophia-comparison-component1');
            const component2Select = sophiaContainer.querySelector('#sophia-comparison-component2');
            
            if (!component1Select || !component2Select) return;
            
            const component1 = component1Select.value;
            const component2 = component2Select.value;
            
            if (!component1 || !component2) {
                alert('Please select two components to compare');
                return;
            }
            
            console.log(`[SOPHIA] Comparing components: ${component1} vs ${component2}`);
            
            // In a real implementation, this would load and render the comparison data
            // For now, just update the comparison chart with a message
            const comparisonChart = sophiaContainer.querySelector('#sophia-comparison-chart');
            if (comparisonChart) {
                const component1Name = component1Select.options[component1Select.selectedIndex].text;
                const component2Name = component2Select.options[component2Select.selectedIndex].text;
                
                comparisonChart.innerHTML = `
                    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
                        <div style="font-size: 16px; color: #9C27B0; margin-bottom: 10px;">Comparing ${component1Name} vs ${component2Name}</div>
                        <div style="color: #666; font-size: 14px;">Sample comparison visualization</div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('[SOPHIA] Error comparing components:', error);
        }
    }
    
    /**
     * Load experiments for the Experiments tab
     */
    async loadExperiments() {
        try {
            console.log('[SOPHIA] Loading experiments');
            
            // Get the loading indicator and table
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            const loadingIndicator = sophiaContainer.querySelector('#experiments-loading');
            const experimentsTable = sophiaContainer.querySelector('#sophia-experiments-tbody');
            
            if (!loadingIndicator || !experimentsTable) return;
            
            // Show loading indicator
            loadingIndicator.style.display = 'flex';
            
            // Simulate API call delay
            setTimeout(() => {
                // Hide loading indicator
                loadingIndicator.style.display = 'none';
                
                // Experiments are already in the HTML for demonstration purposes
                
                console.log('[SOPHIA] Experiments loaded');
            }, 1500);
        } catch (error) {
            console.error('[SOPHIA] Error loading experiments:', error);
        }
    }
    
    /**
     * Filter experiments based on selected filters
     */
    filterExperiments() {
        try {
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            const statusFilter = sophiaContainer.querySelector('#sophia-experiments-status-filter');
            const typeFilter = sophiaContainer.querySelector('#sophia-experiments-type-filter');
            
            if (!statusFilter || !typeFilter) return;
            
            const status = statusFilter.value;
            const type = typeFilter.value;
            
            console.log(`[SOPHIA] Filtering experiments - Status: ${status || 'All'}, Type: ${type || 'All'}`);
            
            // In a real implementation, this would reload the experiment list with filtered data
            
            // For this example, let's simulate by showing/hiding rows
            const rows = sophiaContainer.querySelectorAll('#sophia-experiments-tbody tr');
            rows.forEach(row => {
                const rowType = row.querySelector('td:nth-child(2)').textContent.toLowerCase().replace(/ /g, '_');
                const rowStatus = row.querySelector('td:nth-child(3) .sophia__status').textContent.toLowerCase();
                
                const typeMatch = !type || rowType.includes(type);
                const statusMatch = !status || rowStatus.includes(status);
                
                if (typeMatch && statusMatch) {
                    row.style.display = 'table-row';
                } else {
                    row.style.display = 'none';
                }
            });
        } catch (error) {
            console.error('[SOPHIA] Error filtering experiments:', error);
        }
    }
    
    /**
     * Show new experiment form
     */
    showNewExperimentForm() {
        console.log('[SOPHIA] Showing new experiment form');
        alert('New Experiment form would appear here');
    }
    
    /**
     * Load recommendations for the Recommendations tab
     */
    async loadRecommendations() {
        try {
            console.log('[SOPHIA] Loading recommendations');
            
            // Get the loading indicator and table
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            const loadingIndicator = sophiaContainer.querySelector('#recommendations-loading');
            const recommendationsTable = sophiaContainer.querySelector('#sophia-recommendations-tbody');
            
            if (!loadingIndicator || !recommendationsTable) return;
            
            // Show loading indicator
            loadingIndicator.style.display = 'flex';
            
            // Simulate API call delay
            setTimeout(() => {
                // Hide loading indicator
                loadingIndicator.style.display = 'none';
                
                // Recommendations are already in the HTML for demonstration purposes
                
                console.log('[SOPHIA] Recommendations loaded');
            }, 1500);
        } catch (error) {
            console.error('[SOPHIA] Error loading recommendations:', error);
        }
    }
    
    /**
     * Filter recommendations based on selected filters
     */
    filterRecommendations() {
        try {
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            const statusFilter = sophiaContainer.querySelector('#sophia-recommendations-status-filter');
            const priorityFilter = sophiaContainer.querySelector('#sophia-recommendations-priority-filter');
            const componentFilter = sophiaContainer.querySelector('#sophia-recommendations-component-filter');
            
            if (!statusFilter || !priorityFilter || !componentFilter) return;
            
            const status = statusFilter.value;
            const priority = priorityFilter.value;
            const component = componentFilter.value;
            
            console.log(`[SOPHIA] Filtering recommendations - Status: ${status || 'All'}, Priority: ${priority || 'All'}, Component: ${component || 'All'}`);
            
            // In a real implementation, this would reload the recommendation list with filtered data
            
            // For this example, let's simulate by showing/hiding rows
            const rows = sophiaContainer.querySelectorAll('#sophia-recommendations-tbody tr');
            rows.forEach(row => {
                const rowType = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                const rowPriority = row.querySelector('td:nth-child(3) .sophia__priority').textContent.toLowerCase();
                const rowComponent = row.querySelector('td:nth-child(4)').textContent.toLowerCase();
                const rowStatus = row.querySelector('td:nth-child(5) .sophia__status').textContent.toLowerCase();
                
                const statusMatch = !status || rowStatus.includes(status);
                const priorityMatch = !priority || rowPriority.includes(priority);
                const componentMatch = !component || rowComponent.includes(component);
                
                if (statusMatch && priorityMatch && componentMatch) {
                    row.style.display = 'table-row';
                } else {
                    row.style.display = 'none';
                }
            });
        } catch (error) {
            console.error('[SOPHIA] Error filtering recommendations:', error);
        }
    }
    
    /**
     * Show new recommendation form
     */
    showNewRecommendationForm() {
        console.log('[SOPHIA] Showing new recommendation form');
        alert('New Recommendation form would appear here');
    }
    
    /**
     * Handle sending chat messages
     */
    handleChatSend() {
        try {
            const sophiaContainer = document.querySelector('.sophia');
            if (!sophiaContainer) return;
            
            const chatInput = sophiaContainer.querySelector('#chat-input');
            if (!chatInput) return;
            
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Get the active tab
            const activeTab = this.state.activeTab;
            
            // Determine which chat container to use
            let chatContainer;
            if (activeTab === 'researchchat') {
                chatContainer = sophiaContainer.querySelector('#researchchat-messages');
            } else if (activeTab === 'teamchat') {
                chatContainer = sophiaContainer.querySelector('#teamchat-messages');
            } else {
                // If not in a chat tab, do nothing
                return;
            }
            
            if (!chatContainer) return;
            
            // Add user message to chat
            this.addUserMessage(chatContainer, message);
            
            // Clear input
            chatInput.value = '';
            
            // Simulate AI response
            this.simulateAIResponse(chatContainer, message, activeTab);
        } catch (error) {
            console.error('[SOPHIA] Error handling chat send:', error);
        }
    }
    
    /**
     * Add user message to chat
     * @param {HTMLElement} container - The chat container
     * @param {string} message - The message text
     */
    addUserMessage(container, message) {
        try {
            // Create message element
            const messageEl = document.createElement('div');
            messageEl.className = 'sophia__message sophia__message--user';
            messageEl.textContent = message;
            
            // Add to container
            container.appendChild(messageEl);
            
            // Scroll to bottom
            container.scrollTop = container.scrollHeight;
            
            console.log('[SOPHIA] Added user message to chat');
        } catch (error) {
            console.error('[SOPHIA] Error adding user message:', error);
        }
    }
    
    /**
     * Simulate AI response
     * @param {HTMLElement} container - The chat container
     * @param {string} userMessage - The user's message
     * @param {string} chatType - The type of chat ('researchchat' or 'teamchat')
     */
    simulateAIResponse(container, userMessage, chatType) {
        try {
            // Show typing indicator temporarily
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'sophia__message sophia__message--typing';
            typingIndicator.innerHTML = '<div class="sophia__typing-indicator"><span></span><span></span><span></span></div>';
            container.appendChild(typingIndicator);
            
            // Scroll to bottom
            container.scrollTop = container.scrollHeight;
            
            // Generate response based on chat type
            let response;
            if (chatType === 'researchchat') {
                response = this.generateResearchResponse(userMessage);
            } else {
                response = this.generateTeamChatResponse(userMessage);
            }
            
            // Simulate typing delay
            setTimeout(() => {
                // Remove typing indicator
                container.removeChild(typingIndicator);
                
                // Create AI message element
                const messageEl = document.createElement('div');
                messageEl.className = 'sophia__message sophia__message--ai';
                messageEl.textContent = response;
                
                // Add to container
                container.appendChild(messageEl);
                
                // Scroll to bottom
                container.scrollTop = container.scrollHeight;
                
                console.log('[SOPHIA] Added AI response to chat');
            }, 1500);
        } catch (error) {
            console.error('[SOPHIA] Error simulating AI response:', error);
        }
    }
    
    /**
     * Generate research chat response
     * @param {string} userMessage - The user's message
     * @returns {string} The AI response
     */
    generateResearchResponse(userMessage) {
        // Simple keyword-based response generation for demonstration purposes
        if (userMessage.toLowerCase().includes('intelligence')) {
            return 'Intelligence in AI systems can be measured across multiple dimensions including language understanding, reasoning ability, learning capacity, and problem-solving capabilities. Our research suggests that a balanced approach across these dimensions leads to more robust AI systems.';
        } else if (userMessage.toLowerCase().includes('experiment')) {
            return 'Designing effective AI experiments requires careful consideration of metrics, control groups, and statistical significance. I recommend starting with clear hypotheses and ensuring your measurement framework captures both quantitative and qualitative aspects of performance.';
        } else if (userMessage.toLowerCase().includes('metrics')) {
            return 'Metrics for AI systems should capture both technical performance (accuracy, latency, resource usage) and more qualitative aspects (helpfulness, alignment with human values, safety). We're currently developing a comprehensive framework for intelligence metrics that balances these considerations.';
        } else {
            return 'That's an interesting research question. Our AI intelligence measurement framework suggests examining this from multiple dimensions including performance metrics, behavioral analysis, and alignment with intended goals. Would you like me to provide more specific information about any particular aspect?';
        }
    }
    
    /**
     * Generate team chat response
     * @param {string} userMessage - The user's message
     * @returns {string} The AI response
     */
    generateTeamChatResponse(userMessage) {
        return `I've shared your message with the team: "${userMessage}". In a full implementation, this would be visible to all connected Tekton components. [Team Chat Simulation]`;
    }
    
    /**
     * Save component state to localStorage
     */
    saveComponentState() {
        try {
            const state = {
                activeTab: this.state.activeTab,
                // Add other state properties as needed
            };
            
            localStorage.setItem('sophia_component_state', JSON.stringify(state));
            console.log('[SOPHIA] Component state saved to localStorage');
        } catch (error) {
            console.error('[SOPHIA] Error saving component state:', error);
        }
    }
    
    /**
     * Load component state from localStorage
     */
    loadComponentState() {
        try {
            const savedState = localStorage.getItem('sophia_component_state');
            if (savedState) {
                const state = JSON.parse(savedState);
                
                // Restore active tab if different from default
                if (state.activeTab && state.activeTab !== 'metrics') {
                    this.state.activeTab = state.activeTab;
                    window.sophia_switchTab(state.activeTab);
                }
                
                // Restore other state properties as needed
                
                console.log('[SOPHIA] Component state loaded from localStorage');
            }
        } catch (error) {
            console.error('[SOPHIA] Error loading component state:', error);
        }
    }
}

// Create global instance
window.sophiaComponent = new SophiaComponent();

// DOM ready handler
document.addEventListener('DOMContentLoaded', function() {
    if (window.sophiaComponent) {
        // Initialize component
        window.sophiaComponent.init();
        
        // Load saved state
        window.sophiaComponent.loadComponentState();
    }
});