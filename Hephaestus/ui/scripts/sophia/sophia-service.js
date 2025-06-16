/**
 * Sophia Service
 * Handles communication with the Sophia API
 */
class SophiaService {
    constructor() {
        const sophiaPort = window.SOPHIA_PORT || 8014;
        this.serviceUrl = window.env?.SOPHIA_API_URL || `http://localhost:${sophiaPort}`;
        this.isConnected = false;
        this.connectionAttempts = 0;
        this.maxConnectionAttempts = 3;
        this.listeners = [];
        
        console.log('[SOPHIA] Initializing Sophia Service with API URL:', this.serviceUrl);
    }
    
    /**
     * Initialize the service and check connection
     */
    async init() {
        console.log('[SOPHIA] Initializing Sophia service...');
        await this.checkConnection();
        return this;
    }
    
    /**
     * Check connection to the Sophia API
     */
    async checkConnection() {
        if (this.connectionAttempts >= this.maxConnectionAttempts) {
            console.warn('[SOPHIA] Max connection attempts reached, using mock data');
            this.isConnected = false;
            return false;
        }
        
        try {
            this.connectionAttempts++;
            console.log(`[SOPHIA] Attempting to connect to Sophia API (attempt ${this.connectionAttempts})...`);
            
            // For now, just simulate a successful connection
            // In the actual implementation, we would make a fetch call to the API
            setTimeout(() => {
                this.isConnected = true;
                console.log('[SOPHIA] Connected to Sophia API');
                this.notifyListeners('connection', { status: 'connected' });
            }, 500);
            
            return true;
        } catch (error) {
            console.error('[SOPHIA] Failed to connect to Sophia API:', error);
            this.isConnected = false;
            return false;
        }
    }
    
    /**
     * Get all Tekton components
     */
    async getComponents() {
        if (!this.isConnected) {
            return this.getMockComponents();
        }
        
        // In a real implementation, we would fetch from the API
        return this.getMockComponents();
    }
    
    /**
     * Get mock components for testing
     */
    getMockComponents() {
        return [
            { id: 'rhetor', name: 'Rhetor', type: 'llm' },
            { id: 'athena', name: 'Athena', type: 'knowledge' },
            { id: 'engram', name: 'Engram', type: 'memory' },
            { id: 'hermes', name: 'Hermes', type: 'communication' },
            { id: 'harmonia', name: 'Harmonia', type: 'workflow' },
            { id: 'ergon', name: 'Ergon', type: 'agent' },
            { id: 'telos', name: 'Telos', type: 'goal' },
            { id: 'terma', name: 'Terma', type: 'terminal' }
        ];
    }
    
    /**
     * Get metrics data
     */
    async getMetricsData(params = {}) {
        if (!this.isConnected) {
            return this.getMockMetricsData(params);
        }
        
        // In a real implementation, we would fetch from the API
        return this.getMockMetricsData(params);
    }
    
    /**
     * Get mock metrics data for testing
     */
    getMockMetricsData(params = {}) {
        const { component, type, timeRange } = params;
        
        // Create sample data for performance metrics
        const performanceData = {
            title: 'Performance Metrics',
            labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
            datasets: [
                {
                    name: 'Response Time (ms)',
                    data: [120, 110, 130, 105, 115, 90, 95]
                },
                {
                    name: 'Throughput (req/s)',
                    data: [45, 50, 48, 52, 53, 55, 58]
                }
            ]
        };
        
        // Create sample data for resource metrics
        const resourceData = {
            title: 'Resource Usage',
            labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
            datasets: [
                {
                    name: 'CPU Usage (%)',
                    data: [65, 72, 68, 70, 75, 73, 71]
                },
                {
                    name: 'Memory Usage (MB)',
                    data: [512, 520, 530, 525, 522, 528, 535]
                }
            ]
        };
        
        // Create sample data for communication metrics
        const communicationData = {
            title: 'Component Communication',
            labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
            datasets: [
                {
                    name: 'Messages Sent',
                    data: [210, 225, 240, 235, 250, 260, 270]
                },
                {
                    name: 'Messages Received',
                    data: [190, 205, 220, 215, 230, 240, 250]
                }
            ]
        };
        
        // Create sample data for error metrics
        const errorData = {
            title: 'Error Rates',
            labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
            datasets: [
                {
                    name: 'Error Rate (%)',
                    data: [2.5, 2.2, 2.0, 1.8, 1.5, 1.3, 1.2]
                },
                {
                    name: 'Recovery Rate (%)',
                    data: [97, 97.5, 98, 98.2, 98.5, 98.7, 98.8]
                }
            ]
        };
        
        return {
            performance: performanceData,
            resource: resourceData,
            communication: communicationData,
            error: errorData
        };
    }
    
    /**
     * Get intelligence data
     */
    async getIntelligenceData(params = {}) {
        if (!this.isConnected) {
            return this.getMockIntelligenceData(params);
        }
        
        // In a real implementation, we would fetch from the API
        return this.getMockIntelligenceData(params);
    }
    
    /**
     * Get mock intelligence data for testing
     */
    getMockIntelligenceData(params = {}) {
        const { component, dimension } = params;
        
        // Create sample radar chart data
        const radarData = {
            labels: [
                'Language Processing',
                'Reasoning',
                'Knowledge',
                'Learning',
                'Creativity',
                'Planning',
                'Problem Solving',
                'Adaptation',
                'Collaboration',
                'Metacognition'
            ],
            datasets: [
                {
                    name: 'Current',
                    data: [85, 90, 80, 75, 82, 88, 92, 78, 83, 79]
                },
                {
                    name: 'Previous',
                    data: [80, 85, 78, 72, 78, 84, 89, 76, 80, 75]
                }
            ]
        };
        
        // Create sample dimension details
        const dimensionDetails = [
            { dimension: 'Language Processing', score: 85, benchmark: 82, percentile: '75th', trend: '+5%' },
            { dimension: 'Reasoning', score: 90, benchmark: 79, percentile: '90th', trend: '+7%' },
            { dimension: 'Knowledge', score: 80, benchmark: 75, percentile: '68th', trend: '+4%' },
            { dimension: 'Learning', score: 75, benchmark: 73, percentile: '65th', trend: '+3%' },
            { dimension: 'Creativity', score: 82, benchmark: 71, percentile: '85th', trend: '+9%' },
            { dimension: 'Planning', score: 88, benchmark: 77, percentile: '82nd', trend: '+6%' },
            { dimension: 'Problem Solving', score: 92, benchmark: 80, percentile: '88th', trend: '+6%' },
            { dimension: 'Adaptation', score: 78, benchmark: 74, percentile: '69th', trend: '+4%' },
            { dimension: 'Collaboration', score: 83, benchmark: 79, percentile: '72nd', trend: '+5%' },
            { dimension: 'Metacognition', score: 79, benchmark: 75, percentile: '70th', trend: '+4%' }
        ];
        
        return {
            radarData,
            dimensionDetails
        };
    }
    
    /**
     * Get component comparison data
     */
    async getComponentComparison(component1, component2) {
        if (!this.isConnected) {
            return this.getMockComponentComparison(component1, component2);
        }
        
        // In a real implementation, we would fetch from the API
        return this.getMockComponentComparison(component1, component2);
    }
    
    /**
     * Get mock component comparison data for testing
     */
    getMockComponentComparison(component1, component2) {
        // Sample comparison data
        const comparisonData = {
            labels: [
                'Language Processing',
                'Reasoning',
                'Knowledge',
                'Learning',
                'Creativity',
                'Planning',
                'Problem Solving',
                'Adaptation',
                'Collaboration',
                'Metacognition'
            ],
            datasets: [
                {
                    name: component1,
                    data: [85, 90, 80, 75, 82, 88, 92, 78, 83, 79]
                },
                {
                    name: component2,
                    data: [82, 88, 85, 80, 78, 84, 87, 81, 79, 82]
                }
            ]
        };
        
        return comparisonData;
    }
    
    /**
     * Get experiments
     */
    async getExperiments(params = {}) {
        if (!this.isConnected) {
            return this.getMockExperiments(params);
        }
        
        // In a real implementation, we would fetch from the API
        return this.getMockExperiments(params);
    }
    
    /**
     * Get mock experiments for testing
     */
    getMockExperiments(params = {}) {
        const { status, type } = params;
        
        const experiments = [
            {
                id: 'exp001',
                name: 'Claude vs GPT Response Quality',
                type: 'A/B Test',
                status: 'completed',
                components: ['Terma', 'Rhetor'],
                created: '2025-04-22',
                results: 'Claude showed 12% higher accuracy on complex reasoning tasks, while GPT was 8% faster on average.'
            },
            {
                id: 'exp002',
                name: 'Memory Retrieval Optimization',
                type: 'Multivariate',
                status: 'running',
                components: ['Engram'],
                created: '2025-05-01',
                results: null
            },
            {
                id: 'exp003',
                name: 'Knowledge Graph Expansion Techniques',
                type: 'Before/After',
                status: 'completed',
                components: ['Athena'],
                created: '2025-04-28',
                results: 'Automated expansion showed 25% higher entity coverage with only 5% increase in false positives.'
            },
            {
                id: 'exp004',
                name: 'Workflow Optimization Strategies',
                type: 'Multivariate',
                status: 'scheduled',
                components: ['Harmonia'],
                created: '2025-05-03',
                results: null
            },
            {
                id: 'exp005',
                name: 'Agent Collaboration Methods',
                type: 'A/B Test',
                status: 'draft',
                components: ['Ergon', 'Telos'],
                created: '2025-05-02',
                results: null
            }
        ];
        
        return experiments;
    }
    
    /**
     * Get recommendations
     */
    async getRecommendations(params = {}) {
        if (!this.isConnected) {
            return this.getMockRecommendations(params);
        }
        
        // In a real implementation, we would fetch from the API
        return this.getMockRecommendations(params);
    }
    
    /**
     * Get mock recommendations for testing
     */
    getMockRecommendations(params = {}) {
        const { status, priority, component } = params;
        
        const recommendations = [
            {
                id: 'rec001',
                title: 'Implement Semantic Search for Engram',
                type: 'Enhancement',
                priority: 'high',
                components: ['Engram'],
                status: 'in_progress',
                description: 'Add semantic search capabilities to the memory system to improve context retrieval.'
            },
            {
                id: 'rec002',
                title: 'Optimize Harmonia Workflow Engine',
                type: 'Performance',
                priority: 'medium',
                components: ['Harmonia'],
                status: 'pending',
                description: 'Reduce latency in workflow transitions and optimize resource allocation during workflow execution.'
            },
            {
                id: 'rec003',
                title: 'Add Multi-Model Support to Rhetor',
                type: 'Feature',
                priority: 'high',
                components: ['Rhetor'],
                status: 'approved',
                description: 'Extend Rhetor to support multiple models simultaneously with automatic failover and load balancing.'
            },
            {
                id: 'rec004',
                title: 'Improve Graph Visualization in Athena',
                type: 'Usability',
                priority: 'medium',
                components: ['Athena'],
                status: 'implemented',
                description: 'Enhance graph visualization with better layouts, filtering, and interactive exploration capabilities.'
            },
            {
                id: 'rec005',
                title: 'Add Comprehensive Monitoring to Tekton Core',
                type: 'Infrastructure',
                priority: 'critical',
                components: ['Tekton Core'],
                status: 'pending',
                description: 'Implement system-wide monitoring and alerting for all Tekton components.'
            }
        ];
        
        return recommendations;
    }
    
    /**
     * Send message to research chat
     */
    async sendResearchChatMessage(message) {
        if (!this.isConnected) {
            return this.getMockResearchChatResponse(message);
        }
        
        // In a real implementation, we would send to the API
        return this.getMockResearchChatResponse(message);
    }
    
    /**
     * Get mock research chat response for testing
     */
    getMockResearchChatResponse(message) {
        // Simulate LLM response
        return {
            id: Date.now().toString(),
            message: message,
            response: 'This is a mock response to your research question. In a real implementation, this would be an AI-generated response based on your specific query and intelligence research data.',
            timestamp: new Date().toISOString()
        };
    }
    
    /**
     * Send message to team chat
     */
    async sendTeamChatMessage(message) {
        if (!this.isConnected) {
            return this.getMockTeamChatResponse(message);
        }
        
        // In a real implementation, we would send to the API
        return this.getMockTeamChatResponse(message);
    }
    
    /**
     * Get mock team chat response for testing
     */
    getMockTeamChatResponse(message) {
        // Simulate chat response
        return {
            id: Date.now().toString(),
            message: message,
            response: 'Message sent to team chat. All connected Tekton components would receive this message.',
            timestamp: new Date().toISOString()
        };
    }
    
    /**
     * Add a listener for service events
     */
    addListener(event, callback) {
        this.listeners.push({ event, callback });
    }
    
    /**
     * Remove a listener
     */
    removeListener(event, callback) {
        this.listeners = this.listeners.filter(
            listener => listener.event !== event || listener.callback !== callback
        );
    }
    
    /**
     * Notify all listeners of an event
     */
    notifyListeners(event, data) {
        this.listeners
            .filter(listener => listener.event === event)
            .forEach(listener => listener.callback(data));
    }
}

// Create a singleton instance
window.sophiaService = window.sophiaService || new SophiaService();