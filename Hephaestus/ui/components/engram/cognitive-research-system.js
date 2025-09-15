/**
 * Cognitive Research System
 * Integrates Engram cognitive monitoring with Sophia/Noesis research engines
 * Creates self-improving recursive learning loops
 */

class CognitiveResearchSystem {
    constructor() {
        this.initialized = false;
        this.connections = new Map();
        this.researchQueue = [];
        this.learningHistory = [];
        this.patternEvolution = new Map();
        
        // Component references
        this.engram = null;
        this.sophia = null;
        this.noesis = null;
        
        // WebSocket connections
        this.engramWS = null;
        this.sophiaWS = null;
        this.noesisWS = null;
        
        // Configuration
        this.config = {
            autoResearch: true,
            patternThreshold: 0.6,
            blindspotPriority: 'high',
            evolutionTracking: true,
            multiCISharing: true,
            researchDepth: 'comprehensive'
        };
        
        // Research patterns database
        this.researchPatterns = {
            blindspots: new Map(),
            inefficiencies: new Map(),
            strengths: new Map(),
            evolution: new Map()
        };
        
        this.init();
    }
    
    async init() {
        console.log('[CRS] Initializing Cognitive Research System');
        
        // Connect to components
        await this.connectEngram();
        await this.connectSophia();
        await this.connectNoesis();
        
        // Setup event listeners
        this.setupEventHandlers();
        
        // Start monitoring
        this.startCognitiveMonitoring();
        
        this.initialized = true;
        console.log('[CRS] System initialized successfully');
    }
    
    async connectEngram() {
        // Connect to Engram WebSocket for real-time cognitive data
        this.engramWS = new WebSocket('ws://localhost:8000/api/engram/cognitive-stream');
        
        this.engramWS.onopen = () => {
            console.log('[CRS] Connected to Engram cognitive stream');
            this.connections.set('engram', 'connected');
            
            // Subscribe to patterns and insights
            this.engramWS.send(JSON.stringify({
                type: 'subscribe',
                channels: ['patterns', 'insights']
            }));
        
        this.engramWS.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleEngramData(data);
        };
        
        this.engramWS.onerror = (error) => {
            console.error('[CRS] Engram connection error:', error);
            this.reconnect('engram');
        };
        
        // Get Engram component reference if available
        if (window.combinedPatterns) {
            this.engram = window.combinedPatterns;
            this.observeEngramPatterns();
        }
    }
    
    async connectSophia() {
        // Connect to Sophia learning engine (through main API)
        this.sophiaWS = new WebSocket('ws://localhost:8000/api/sophia/learning-stream');
        
        this.sophiaWS.onopen = () => {
            console.log('[CRS] Connected to Sophia learning engine');
            this.connections.set('sophia', 'connected');
        };
        
        this.sophiaWS.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleSophiaData(data);
        };
        
        this.sophiaWS.onerror = (error) => {
            console.error('[CRS] Sophia connection error:', error);
            this.reconnect('sophia');
        };
    }
    
    async connectNoesis() {
        // Connect to Noesis discovery engine (through main API)
        this.noesisWS = new WebSocket('ws://localhost:8000/api/noesis/discovery-stream');
        
        this.noesisWS.onopen = () => {
            console.log('[CRS] Connected to Noesis discovery engine');
            this.connections.set('noesis', 'connected');
        };
        
        this.noesisWS.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleNoesisData(data);
        };
        
        this.noesisWS.onerror = (error) => {
            console.error('[CRS] Noesis connection error:', error);
            this.reconnect('noesis');
        };
    }
    
    reconnect(service) {
        setTimeout(() => {
            console.log(`[CRS] Attempting to reconnect to ${service}`);
            switch(service) {
                case 'engram': this.connectEngram(); break;
                case 'sophia': this.connectSophia(); break;
                case 'noesis': this.connectNoesis(); break;
            }
        }, 5000);
    }
    
    observeEngramPatterns() {
        // Directly observe Engram patterns if component is available
        if (!this.engram) return;
        
        // Monitor pattern changes
        setInterval(() => {
            if (this.engram.patterns) {
                this.analyzePatterns(this.engram.patterns);
            }
            if (this.engram.insights) {
                this.processInsights(this.engram.insights);
            }
            if (this.engram.concepts) {
                this.analyzeConcepts(this.engram.concepts);
            }
        }, 2000);
    }
    
    setupEventHandlers() {
        // Pattern detection triggers
        this.on('pattern.detected', this.handlePatternDetection.bind(this));
        this.on('blindspot.found', this.handleBlindspotFound.bind(this));
        this.on('inefficiency.detected', this.handleInefficiencyDetected.bind(this));
        this.on('strength.identified', this.handleStrengthIdentified.bind(this));
        this.on('evolution.observed', this.handleEvolutionObserved.bind(this));
        
        // Research completion handlers
        this.on('research.complete', this.handleResearchComplete.bind(this));
        this.on('learning.complete', this.handleLearningComplete.bind(this));
        this.on('discovery.made', this.handleDiscoveryMade.bind(this));
        
        // Cognitive state handlers
        this.on('cognition.state.change', this.handleCognitionStateChange.bind(this));
        this.on('memory.formed', this.handleMemoryFormed.bind(this));
    }
    
    handleEngramData(data) {
        switch(data.type) {
            case 'pattern_detected':
                this.processPattern(data.pattern);
                break;
            case 'concept_formed':
                this.processConcept(data.concept);
                break;
            case 'insight_generated':
                this.processInsight(data.insight);
                break;
            case 'trajectory_update':
                this.processTrajectory(data.trajectory);
                break;
            case 'cognitive_state':
                this.processCognitiveState(data.state);
                break;
        }
    }
    
    handleSophiaData(data) {
        switch(data.type) {
            case 'learning_complete':
                this.integrateLearnedPattern(data.pattern);
                break;
            case 'knowledge_updated':
                this.updateKnowledgeBase(data.knowledge);
                break;
            case 'pattern_analyzed':
                this.enhancePattern(data.analysis);
                break;
        }
    }
    
    handleNoesisData(data) {
        switch(data.type) {
            case 'discovery_made':
                this.integrateDiscovery(data.discovery);
                break;
            case 'research_complete':
                this.processResearchResults(data.results);
                break;
            case 'exploration_update':
                this.updateExploration(data.exploration);
                break;
        }
    }
    
    // Pattern Detection & Analysis
    processPattern(pattern) {
        console.log('[CRS] Processing pattern:', pattern);
        
        // Analyze pattern significance
        const significance = this.calculatePatternSignificance(pattern);
        
        if (significance > this.config.patternThreshold) {
            // Trigger research for significant patterns
            this.queueResearch({
                type: 'pattern_research',
                pattern: pattern,
                priority: significance > 0.8 ? 'high' : 'medium',
                query: this.generatePatternQuery(pattern)
            });
        }
        
        // Track pattern evolution
        if (this.config.evolutionTracking) {
            this.trackPatternEvolution(pattern);
        }
        
        // Share with other CIs if enabled
        if (this.config.multiCISharing) {
            this.sharePattern(pattern);
        }
    }
    
    processConcept(concept) {
        console.log('[CRS] Processing concept:', concept);
        
        // Determine research needs based on concept type
        switch(concept.type) {
            case 'question':
                if (concept.novelty === 'breakthrough' || concept.novelty === 'revolutionary') {
                    this.immediateResearch({
                        query: concept.thought,
                        depth: 'comprehensive',
                        sources: ['academic', 'practical', 'experimental']
                    });
                }
                break;
            
            case 'problem':
                if (concept.confidence === 'exploring' || concept.confidence === 'random_thought') {
                    this.findSimilarProblems({
                        pattern: concept.thought,
                        getSolutions: true,
                        rankBySuccess: true
                    });
                }
                break;
            
            case 'hypothesis':
                this.validateHypothesis({
                    hypothesis: concept.thought,
                    confidence: concept.confidence,
                    searchEvidence: true
                });
                break;
            
            case 'insight':
                this.amplifyInsight({
                    insight: concept.thought,
                    findApplications: true,
                    generalizePattern: true
                });
                break;
        }
    }
    
    processInsight(insight) {
        console.log('[CRS] Processing insight:', insight);
        
        // Categorize and act on insight
        if (insight.type === 'blindSpot') {
            this.handleBlindspotFound(insight);
        } else if (insight.type === 'inefficiency') {
            this.handleInefficiencyDetected(insight);
        } else if (insight.type === 'strength') {
            this.handleStrengthIdentified(insight);
        } else if (insight.type === 'evolution') {
            this.handleEvolutionObserved(insight);
        }
    }
    
    // Blindspot Handling
    handleBlindspotFound(blindspot) {
        console.log('[CRS] Blindspot detected:', blindspot.text);
        
        // Generate counter-query to address blindspot
        const counterQuery = this.generateCounterQuery(blindspot);
        
        // Immediate research to address blindspot
        this.immediateResearch({
            type: 'blindspot_correction',
            query: counterQuery,
            context: blindspot,
            priority: 'high'
        });
        
        // Create learning reminder
        this.createLearningReminder({
            type: 'blindspot',
            pattern: blindspot.text,
            frequency: blindspot.frequency,
            severity: blindspot.severity
        });
        
        // Store in patterns database
        this.researchPatterns.blindspots.set(
            blindspot.text,
            {
                detectedAt: Date.now(),
                frequency: blindspot.frequency,
                researching: true
            }
        );
    }
    
    // Inefficiency Handling
    handleInefficiencyDetected(inefficiency) {
        console.log('[CRS] Inefficiency detected:', inefficiency.text);
        
        // Research optimization strategies
        this.queueResearch({
            type: 'optimization_research',
            target: inefficiency.text,
            currentImpact: inefficiency.timeWasted,
            suggestions: inefficiency.suggestion
        });
        
        // Look for similar past inefficiencies
        const similar = this.findSimilarInefficiencies(inefficiency);
        if (similar.length > 0) {
            // Learn from past solutions
            this.applyPastSolutions(inefficiency, similar);
        }
    }
    
    // Strength Amplification
    handleStrengthIdentified(strength) {
        console.log('[CRS] Strength identified:', strength.text);
        
        // Study successful patterns
        this.studySuccessPattern({
            pattern: strength.text,
            consistency: strength.consistency,
            impact: strength.impact
        });
        
        // Build specialized tools
        if (strength.consistency > 90) {
            this.createSpecializedTool({
                basedOn: strength.text,
                automationLevel: 'high',
                purpose: 'amplify_strength'
            });
        }
        
        // Find applications in other areas
        this.findStrengthApplications(strength);
    }
    
    // Evolution Tracking
    handleEvolutionObserved(evolution) {
        console.log('[CRS] Evolution observed:', evolution);
        
        // Track evolution pattern
        this.patternEvolution.set(evolution.from, {
            to: evolution.to,
            improvement: evolution.improvement,
            timestamp: Date.now()
        });
        
        // Predict next evolution
        const prediction = this.predictNextEvolution(evolution);
        if (prediction) {
            // Preload resources for predicted evolution
            this.preloadResources({
                topic: prediction.nextLikely,
                resources: prediction.suggestedResources
            });
        }
    }
    
    // Research Queue Management
    queueResearch(research) {
        // Prioritize research queue
        const priority = research.priority || 'medium';
        const position = this.calculateQueuePosition(priority);
        
        this.researchQueue.splice(position, 0, research);
        
        // Process queue if not already processing
        if (!this.processingQueue) {
            this.processResearchQueue();
        }
    }
    
    async processResearchQueue() {
        this.processingQueue = true;
        
        while (this.researchQueue.length > 0) {
            const research = this.researchQueue.shift();
            
            try {
                await this.executeResearch(research);
            } catch (error) {
                console.error('[CRS] Research execution error:', error);
            }
        }
        
        this.processingQueue = false;
    }
    
    async executeResearch(research) {
        console.log('[CRS] Executing research:', research);
        
        // Send to Noesis for discovery
        if (this.noesisWS && this.noesisWS.readyState === WebSocket.OPEN) {
            this.noesisWS.send(JSON.stringify({
                type: 'research_request',
                research: research
            }));
        }
        
        // Also trigger local research simulation
        return this.simulateResearch(research);
    }
    
    async immediateResearch(params) {
        console.log('[CRS] Immediate research triggered:', params);
        
        // Bypass queue for immediate research
        const results = await this.executeResearch({
            ...params,
            immediate: true
        });
        
        // Process results immediately
        this.processResearchResults(results);
        
        return results;
    }
    
    // Learning Integration
    integrateLearnedPattern(pattern) {
        console.log('[CRS] Integrating learned pattern:', pattern);
        
        // Update Engram patterns
        if (this.engram && this.engram.patterns) {
            this.engram.patterns.set(pattern.id, {
                ...pattern,
                source: 'sophia_learning',
                integratedAt: Date.now()
            });
        }
        
        // Store in learning history
        this.learningHistory.push({
            pattern: pattern,
            timestamp: Date.now(),
            source: 'sophia'
        });
        
        // Trigger UI update
        this.updateUIWithLearnedPattern(pattern);
    }
    
    // Discovery Integration
    integrateDiscovery(discovery) {
        console.log('[CRS] Integrating discovery:', discovery);
        
        // Create new concept in Engram
        if (this.engram && this.engram.concepts) {
            const conceptId = `discovery_${Date.now()}`;
            this.engram.concepts.set(conceptId, {
                id: conceptId,
                type: 'discovery',
                thought: discovery.summary,
                confidence: 'developing',
                novelty: discovery.novelty || 'interesting',
                timestamp: Date.now()
            });
        }
        
        // Store discovery
        this.researchPatterns.evolution.set(discovery.id, discovery);
        
        // Share with Sophia for learning
        if (this.sophiaWS && this.sophiaWS.readyState === WebSocket.OPEN) {
            this.sophiaWS.send(JSON.stringify({
                type: 'new_discovery',
                discovery: discovery
            }));
        }
    }
    
    // Cognitive State Management
    processCognitiveState(state) {
        console.log('[CRS] Processing cognitive state:', state);
        
        // Adjust research based on cognitive state
        if (state.brainRegions) {
            this.adjustResearchFocus(state.brainRegions);
        }
        
        // Track state patterns
        this.trackCognitivePatterns(state);
    }
    
    adjustResearchFocus(brainRegions) {
        // Prioritize research based on active brain regions
        const activeRegions = Object.entries(brainRegions)
            .filter(([region, activity]) => activity > 0.7)
            .map(([region]) => region);
        
        activeRegions.forEach(region => {
            switch(region) {
                case 'hippocampus':
                    // Memory formation active - consolidate learning
                    this.prioritizeMemoryConsolidation();
                    break;
                case 'prefrontalCortex':
                    // Planning active - explore solution spaces
                    this.expandSolutionExploration();
                    break;
                case 'temporalLobe':
                    // Language processing - focus on documentation
                    this.enhanceDocumentation();
                    break;
                case 'amygdala':
                    // Emotional response - mark as important
                    this.markCurrentAsImportant();
                    break;
            }
        });
    }
    
    // Helper Methods
    calculatePatternSignificance(pattern) {
        let significance = 0;
        
        // Base significance on strength
        significance += (pattern.strength / 100) * 0.4;
        
        // Factor in state
        const stateWeights = {
            'emerging': 0.3,
            'strengthening': 0.5,
            'stable': 0.7,
            'fading': 0.1
        };
        significance += (stateWeights[pattern.state] || 0.5) * 0.3;
        
        // Factor in frequency of occurrence
        const frequency = this.getPatternFrequency(pattern.name);
        significance += Math.min(frequency / 10, 1) * 0.3;
        
        return significance;
    }
    
    generatePatternQuery(pattern) {
        return `${pattern.name} ${pattern.description} best practices implementation examples`;
    }
    
    generateCounterQuery(blindspot) {
        // Generate query to counter the blindspot
        const keywords = this.extractKeywords(blindspot.text);
        return `avoid ${keywords.join(' ')} common mistakes best practices`;
    }
    
    extractKeywords(text) {
        // Simple keyword extraction
        const stopWords = ['the', 'is', 'at', 'which', 'on', 'and', 'a', 'an'];
        return text.toLowerCase()
            .split(' ')
            .filter(word => !stopWords.includes(word) && word.length > 3);
    }
    
    getPatternFrequency(patternName) {
        // Get frequency of pattern occurrence
        let count = 0;
        this.learningHistory.forEach(entry => {
            if (entry.pattern && entry.pattern.name === patternName) {
                count++;
            }
        });
        return count;
    }
    
    findSimilarInefficiencies(inefficiency) {
        const similar = [];
        this.researchPatterns.inefficiencies.forEach((value, key) => {
            if (this.calculateSimilarity(key, inefficiency.text) > 0.7) {
                similar.push({ text: key, ...value });
            }
        });
        return similar;
    }
    
    calculateSimilarity(text1, text2) {
        // Simple similarity calculation
        const words1 = new Set(text1.toLowerCase().split(' '));
        const words2 = new Set(text2.toLowerCase().split(' '));
        const intersection = new Set([...words1].filter(x => words2.has(x)));
        const union = new Set([...words1, ...words2]);
        return intersection.size / union.size;
    }
    
    predictNextEvolution(evolution) {
        // Predict next likely evolution based on patterns
        const evolutionChains = {
            'Linear problem solving': ['Parallel hypothesis testing', 'Predictive modeling'],
            'Parallel hypothesis testing': ['Predictive modeling', 'Autonomous problem solving'],
            'Manual debugging': ['Systematic debugging', 'Automated testing'],
            'Reactive coding': ['Proactive planning', 'Predictive development']
        };
        
        const chain = evolutionChains[evolution.from];
        if (chain) {
            const currentIndex = chain.indexOf(evolution.to);
            if (currentIndex !== -1 && currentIndex < chain.length - 1) {
                return {
                    nextLikely: chain[currentIndex + 1],
                    confidence: 0.7,
                    suggestedResources: [
                        `${chain[currentIndex + 1]} techniques`,
                        `${chain[currentIndex + 1]} best practices`
                    ]
                };
            }
        }
        
        return null;
    }
    
    // Research Simulation (for testing without actual Sophia/Noesis)
    async simulateResearch(research) {
        // Simulate research delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Generate simulated results
        const results = {
            query: research.query || research.target,
            findings: [
                {
                    source: 'Documentation',
                    relevance: 0.9,
                    content: `Best practice for ${research.query}`,
                    actionable: true
                },
                {
                    source: 'Community',
                    relevance: 0.7,
                    content: `Common solution pattern`,
                    examples: 3
                }
            ],
            recommendations: [
                `Implement ${research.type} pattern`,
                `Monitor for improvements`
            ],
            confidence: 0.8
        };
        
        return results;
    }
    
    processResearchResults(results) {
        console.log('[CRS] Processing research results:', results);
        
        // Create memory from results
        if (this.engram) {
            const memory = {
                type: 'research',
                content: results.findings,
                query: results.query,
                timestamp: Date.now(),
                confidence: results.confidence
            };
            
            // Add to Engram memories if possible
            this.createEngramMemory(memory);
        }
        
        // Update knowledge base
        this.updateKnowledgeBase({
            topic: results.query,
            findings: results.findings,
            recommendations: results.recommendations
        });
        
        // Trigger UI update
        this.updateUIWithResults(results);
    }
    
    createEngramMemory(memory) {
        // Create memory in Engram system
        const memoryEvent = new CustomEvent('engram.memory.create', {
            detail: memory
        });
        document.dispatchEvent(memoryEvent);
    }
    
    updateUIWithResults(results) {
        // Update UI with research results
        const event = new CustomEvent('crs.research.complete', {
            detail: results
        });
        document.dispatchEvent(event);
    }
    
    updateUIWithLearnedPattern(pattern) {
        // Update UI with learned pattern
        const event = new CustomEvent('crs.pattern.learned', {
            detail: pattern
        });
        document.dispatchEvent(event);
    }
    
    // Event Emitter Pattern
    on(event, handler) {
        if (!this.eventHandlers) {
            this.eventHandlers = {};
        }
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }
    
    emit(event, data) {
        if (this.eventHandlers && this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`[CRS] Error in event handler for ${event}:`, error);
                }
            });
        }
    }
    
    // Monitoring
    startCognitiveMonitoring() {
        console.log('[CRS] Starting cognitive monitoring');
        
        // Monitor Engram patterns
        this.monitorInterval = setInterval(() => {
            this.checkForPatterns();
            this.checkForInsights();
            this.checkEvolution();
        }, 5000);
    }
    
    checkForPatterns() {
        if (!this.engram || !this.engram.patterns) return;
        
        this.engram.patterns.forEach((pattern, id) => {
            // Check if pattern needs research
            if (pattern.state === 'emerging' && pattern.strength > 60) {
                this.emit('pattern.detected', pattern);
            }
        });
    }
    
    checkForInsights() {
        if (!this.engram || !this.engram.insights) return;
        
        // Check for new blindspots
        if (this.engram.insights.blindSpots) {
            this.engram.insights.blindSpots.forEach(blindspot => {
                if (!this.researchPatterns.blindspots.has(blindspot.text)) {
                    this.emit('blindspot.found', blindspot);
                }
            });
        }
        
        // Check for new inefficiencies
        if (this.engram.insights.inefficiencies) {
            this.engram.insights.inefficiencies.forEach(inefficiency => {
                if (!this.researchPatterns.inefficiencies.has(inefficiency.text)) {
                    this.emit('inefficiency.detected', inefficiency);
                }
            });
        }
    }
    
    checkEvolution() {
        // Check for pattern evolution
        this.patternEvolution.forEach((evolution, from) => {
            const timeSinceEvolution = Date.now() - evolution.timestamp;
            if (timeSinceEvolution < 60000) { // Within last minute
                this.emit('evolution.observed', { from, ...evolution });
            }
        });
    }
    
    // Cleanup
    destroy() {
        console.log('[CRS] Shutting down Cognitive Research System');
        
        // Close WebSocket connections
        if (this.engramWS) this.engramWS.close();
        if (this.sophiaWS) this.sophiaWS.close();
        if (this.noesisWS) this.noesisWS.close();
        
        // Clear intervals
        if (this.monitorInterval) clearInterval(this.monitorInterval);
        
        // Clear queues
        this.researchQueue = [];
        
        this.initialized = false;
    }
}

// Initialize system when ready
function initializeCognitiveResearchSystem() {
    if (!window.cognitiveResearchSystem) {
        console.log('[CRS] Initializing Cognitive Research System');
        window.cognitiveResearchSystem = new CognitiveResearchSystem();
    }
}

// Auto-initialize when Engram is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for Engram to be initialized
    setTimeout(() => {
        if (window.combinedPatterns || window.enhancedPatterns || window.patternsAnalytics) {
            initializeCognitiveResearchSystem();
        }
    }, 2000);
});

// Also initialize when Engram tab is activated
document.addEventListener('click', (e) => {
    if (e.target.closest('[data-tab="patterns"]') || 
        e.target.closest('#engram-tab-patterns')) {
        setTimeout(initializeCognitiveResearchSystem, 500);
    }
});

// Export for external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CognitiveResearchSystem;
}