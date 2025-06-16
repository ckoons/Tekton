/**
 * Sophia Intelligence Service
 * Handles intelligence measurements, dimensions, and analysis
 */
class SophiaIntelligenceService {
    constructor() {
        const sophiaPort = window.SOPHIA_PORT || 8014;
        this.serviceUrl = window.env?.SOPHIA_API_URL || `http://localhost:${sophiaPort}`;
        this.dimensions = [
            'language_processing',
            'reasoning',
            'knowledge',
            'learning',
            'creativity',
            'planning',
            'problem_solving',
            'adaptation',
            'collaboration',
            'metacognition'
        ];
        
        console.log('[SOPHIA] Initializing Intelligence Service');
    }
    
    /**
     * Initialize the service
     */
    async init() {
        console.log('[SOPHIA] Initializing Intelligence Service...');
        return this;
    }
    
    /**
     * Get all intelligence dimensions
     */
    async getDimensions() {
        try {
            if (window.sophiaService && window.sophiaService.isConnected) {
                // In a real implementation, this would fetch from the API via sophiaService
                return this.dimensions;
            } else {
                return this.dimensions;
            }
        } catch (error) {
            console.error('[SOPHIA] Error getting intelligence dimensions:', error);
            return this.dimensions;
        }
    }
    
    /**
     * Get intelligence dimension details
     * @param {string} dimension - The dimension to get details for
     */
    async getDimensionDetails(dimension) {
        try {
            // Sample dimension details
            const dimensionDetails = {
                language_processing: {
                    name: 'Language Processing',
                    description: 'Ability to understand and generate natural language',
                    metrics: [
                        { name: 'Comprehension', score: 87, benchmark: 82 },
                        { name: 'Generation', score: 85, benchmark: 80 },
                        { name: 'Contextual Understanding', score: 83, benchmark: 78 }
                    ],
                    trends: [
                        { period: '1 Month', change: '+5%' },
                        { period: '3 Months', change: '+12%' },
                        { period: '6 Months', change: '+18%' }
                    ]
                },
                reasoning: {
                    name: 'Reasoning',
                    description: 'Ability to apply logical thinking to solve problems',
                    metrics: [
                        { name: 'Deductive', score: 92, benchmark: 81 },
                        { name: 'Inductive', score: 89, benchmark: 79 },
                        { name: 'Analogical', score: 86, benchmark: 77 }
                    ],
                    trends: [
                        { period: '1 Month', change: '+7%' },
                        { period: '3 Months', change: '+15%' },
                        { period: '6 Months', change: '+22%' }
                    ]
                },
                knowledge: {
                    name: 'Knowledge',
                    description: 'Breadth and depth of information available',
                    metrics: [
                        { name: 'Factual Recall', score: 88, benchmark: 83 },
                        { name: 'Conceptual Understanding', score: 84, benchmark: 79 },
                        { name: 'Domain Expertise', score: 80, benchmark: 75 }
                    ],
                    trends: [
                        { period: '1 Month', change: '+4%' },
                        { period: '3 Months', change: '+10%' },
                        { period: '6 Months', change: '+16%' }
                    ]
                },
                learning: {
                    name: 'Learning',
                    description: 'Ability to acquire new knowledge and skills',
                    metrics: [
                        { name: 'Acquisition Rate', score: 82, benchmark: 75 },
                        { name: 'Retention', score: 79, benchmark: 73 },
                        { name: 'Transfer', score: 76, benchmark: 71 }
                    ],
                    trends: [
                        { period: '1 Month', change: '+3%' },
                        { period: '3 Months', change: '+8%' },
                        { period: '6 Months', change: '+12%' }
                    ]
                },
                creativity: {
                    name: 'Creativity',
                    description: 'Ability to generate novel and valuable ideas',
                    metrics: [
                        { name: 'Originality', score: 85, benchmark: 73 },
                        { name: 'Flexibility', score: 82, benchmark: 71 },
                        { name: 'Elaboration', score: 79, benchmark: 69 }
                    ],
                    trends: [
                        { period: '1 Month', change: '+9%' },
                        { period: '3 Months', change: '+16%' },
                        { period: '6 Months', change: '+24%' }
                    ]
                },
                planning: {
                    name: 'Planning',
                    description: 'Ability to create and execute effective plans',
                    metrics: [
                        { name: 'Goal Setting', score: 90, benchmark: 78 },
                        { name: 'Strategy Development', score: 87, benchmark: 77 },
                        { name: 'Adaptation', score: 83, benchmark: 74 }
                    ],
                    trends: [
                        { period: '1 Month', change: '+6%' },
                        { period: '3 Months', change: '+13%' },
                        { period: '6 Months', change: '+19%' }
                    ]
                },
                problem_solving: {
                    name: 'Problem Solving',
                    description: 'Ability to identify and resolve problems',
                    metrics: [
                        { name: 'Problem Recognition', score: 93, benchmark: 82 },
                        { name: 'Solution Generation', score: 91, benchmark: 80 },
                        { name: 'Implementation', score: 88, benchmark: 77 }
                    ],
                    trends: [
                        { period: '1 Month', change: '+6%' },
                        { period: '3 Months', change: '+12%' },
                        { period: '6 Months', change: '+18%' }
                    ]
                },
                adaptation: {
                    name: 'Adaptation',
                    description: 'Ability to adjust to new conditions and circumstances',
                    metrics: [
                        { name: 'Flexibility', score: 81, benchmark: 75 },
                        { name: 'Recovery', score: 79, benchmark: 73 },
                        { name: 'Innovation', score: 76, benchmark: 71 }
                    ],
                    trends: [
                        { period: '1 Month', change: '+4%' },
                        { period: '3 Months', change: '+9%' },
                        { period: '6 Months', change: '+13%' }
                    ]
                },
                collaboration: {
                    name: 'Collaboration',
                    description: 'Ability to work effectively with others',
                    metrics: [
                        { name: 'Communication', score: 85, benchmark: 80 },
                        { name: 'Coordination', score: 82, benchmark: 78 },
                        { name: 'Integration', score: 80, benchmark: 75 }
                    ],
                    trends: [
                        { period: '1 Month', change: '+5%' },
                        { period: '3 Months', change: '+10%' },
                        { period: '6 Months', change: '+15%' }
                    ]
                },
                metacognition: {
                    name: 'Metacognition',
                    description: 'Ability to understand and regulate own cognitive processes',
                    metrics: [
                        { name: 'Self-Awareness', score: 82, benchmark: 76 },
                        { name: 'Self-Regulation', score: 79, benchmark: 74 },
                        { name: 'Self-Evaluation', score: 77, benchmark: 73 }
                    ],
                    trends: [
                        { period: '1 Month', change: '+4%' },
                        { period: '3 Months', change: '+8%' },
                        { period: '6 Months', change: '+12%' }
                    ]
                }
            };
            
            if (dimension && dimensionDetails[dimension]) {
                return dimensionDetails[dimension];
            } else {
                return Object.values(dimensionDetails);
            }
        } catch (error) {
            console.error('[SOPHIA] Error getting dimension details:', error);
            return null;
        }
    }
    
    /**
     * Get component intelligence profile
     * @param {string} componentId - The component ID to get profile for
     */
    async getComponentProfile(componentId) {
        try {
            // Sample intelligence profiles for components
            const componentProfiles = {
                rhetor: {
                    name: 'Rhetor',
                    dimensions: {
                        language_processing: 95,
                        reasoning: 85,
                        knowledge: 80,
                        learning: 75,
                        creativity: 90,
                        planning: 70,
                        problem_solving: 82,
                        adaptation: 78,
                        collaboration: 88,
                        metacognition: 72
                    },
                    overall: 82
                },
                athena: {
                    name: 'Athena',
                    dimensions: {
                        language_processing: 88,
                        reasoning: 90,
                        knowledge: 98,
                        learning: 85,
                        creativity: 75,
                        planning: 82,
                        problem_solving: 89,
                        adaptation: 80,
                        collaboration: 83,
                        metacognition: 86
                    },
                    overall: 86
                },
                engram: {
                    name: 'Engram',
                    dimensions: {
                        language_processing: 85,
                        reasoning: 80,
                        knowledge: 95,
                        learning: 92,
                        creativity: 78,
                        planning: 85,
                        problem_solving: 88,
                        adaptation: 86,
                        collaboration: 80,
                        metacognition: 85
                    },
                    overall: 85
                },
                hermes: {
                    name: 'Hermes',
                    dimensions: {
                        language_processing: 92,
                        reasoning: 85,
                        knowledge: 80,
                        learning: 78,
                        creativity: 75,
                        planning: 82,
                        problem_solving: 85,
                        adaptation: 90,
                        collaboration: 98,
                        metacognition: 80
                    },
                    overall: 84
                },
                harmonia: {
                    name: 'Harmonia',
                    dimensions: {
                        language_processing: 85,
                        reasoning: 88,
                        knowledge: 82,
                        learning: 80,
                        creativity: 75,
                        planning: 95,
                        problem_solving: 90,
                        adaptation: 92,
                        collaboration: 88,
                        metacognition: 85
                    },
                    overall: 86
                },
                ergon: {
                    name: 'Ergon',
                    dimensions: {
                        language_processing: 80,
                        reasoning: 85,
                        knowledge: 78,
                        learning: 82,
                        creativity: 80,
                        planning: 88,
                        problem_solving: 92,
                        adaptation: 85,
                        collaboration: 90,
                        metacognition: 78
                    },
                    overall: 84
                },
                telos: {
                    name: 'Telos',
                    dimensions: {
                        language_processing: 82,
                        reasoning: 90,
                        knowledge: 85,
                        learning: 80,
                        creativity: 75,
                        planning: 95,
                        problem_solving: 92,
                        adaptation: 85,
                        collaboration: 88,
                        metacognition: 90
                    },
                    overall: 86
                },
                terma: {
                    name: 'Terma',
                    dimensions: {
                        language_processing: 92,
                        reasoning: 85,
                        knowledge: 80,
                        learning: 82,
                        creativity: 88,
                        planning: 80,
                        problem_solving: 85,
                        adaptation: 82,
                        collaboration: 90,
                        metacognition: 78
                    },
                    overall: 84
                }
            };
            
            if (componentId && componentProfiles[componentId]) {
                return componentProfiles[componentId];
            } else if (componentId) {
                console.warn(`[SOPHIA] No intelligence profile found for component: ${componentId}`);
                return null;
            } else {
                return componentProfiles;
            }
        } catch (error) {
            console.error('[SOPHIA] Error getting component profile:', error);
            return null;
        }
    }
    
    /**
     * Compare components
     * @param {string} component1Id - First component ID
     * @param {string} component2Id - Second component ID
     */
    async compareComponents(component1Id, component2Id) {
        try {
            const profile1 = await this.getComponentProfile(component1Id);
            const profile2 = await this.getComponentProfile(component2Id);
            
            if (!profile1 || !profile2) {
                console.error('[SOPHIA] Unable to compare components - missing profiles');
                return null;
            }
            
            // Convert to format suitable for visualization
            const result = {
                component1: {
                    id: component1Id,
                    name: profile1.name,
                    dimensions: Object.entries(profile1.dimensions).map(([key, value]) => ({
                        id: key,
                        name: this.getDimensionName(key),
                        score: value
                    })),
                    overall: profile1.overall
                },
                component2: {
                    id: component2Id,
                    name: profile2.name,
                    dimensions: Object.entries(profile2.dimensions).map(([key, value]) => ({
                        id: key,
                        name: this.getDimensionName(key),
                        score: value
                    })),
                    overall: profile2.overall
                },
                comparison: {
                    dimensions: Object.keys(profile1.dimensions).map(key => ({
                        id: key,
                        name: this.getDimensionName(key),
                        diff: profile1.dimensions[key] - profile2.dimensions[key]
                    })),
                    overallDiff: profile1.overall - profile2.overall
                }
            };
            
            return result;
        } catch (error) {
            console.error('[SOPHIA] Error comparing components:', error);
            return null;
        }
    }
    
    /**
     * Get the display name for a dimension ID
     * @param {string} dimensionId - The dimension ID
     * @returns {string} The display name
     */
    getDimensionName(dimensionId) {
        const dimensionNames = {
            language_processing: 'Language Processing',
            reasoning: 'Reasoning',
            knowledge: 'Knowledge',
            learning: 'Learning',
            creativity: 'Creativity',
            planning: 'Planning',
            problem_solving: 'Problem Solving',
            adaptation: 'Adaptation',
            collaboration: 'Collaboration',
            metacognition: 'Metacognition'
        };
        
        return dimensionNames[dimensionId] || dimensionId;
    }
    
    /**
     * Get measurement methods for a dimension
     * @param {string} dimensionId - The dimension ID
     */
    async getMeasurementMethods(dimensionId) {
        try {
            // Sample measurement methods for dimensions
            const measurementMethods = {
                language_processing: [
                    { id: 'lp_001', name: 'Text Comprehension Test', description: 'Evaluates ability to understand complex texts and answer questions about them' },
                    { id: 'lp_002', name: 'Language Generation Quality', description: 'Measures fluency, coherence, and appropriateness of generated language' },
                    { id: 'lp_003', name: 'Contextual Understanding', description: 'Assesses ability to understand language in different contexts' }
                ],
                reasoning: [
                    { id: 'r_001', name: 'Logical Problem Solving', description: 'Measures ability to solve logic puzzles and problems' },
                    { id: 'r_002', name: 'Inductive Reasoning Test', description: 'Evaluates pattern recognition and generalization abilities' },
                    { id: 'r_003', name: 'Syllogistic Reasoning', description: 'Assesses ability to draw valid conclusions from premises' }
                ],
                knowledge: [
                    { id: 'k_001', name: 'Factual Recall Test', description: 'Measures ability to accurately retrieve factual information' },
                    { id: 'k_002', name: 'Knowledge Mapping', description: 'Evaluates the interconnections between knowledge elements' },
                    { id: 'k_003', name: 'Domain Expertise Assessment', description: 'Assesses depth of knowledge in specific domains' }
                ],
                learning: [
                    { id: 'l_001', name: 'Learning Rate Measurement', description: 'Measures speed of acquiring new information' },
                    { id: 'l_002', name: 'Knowledge Retention Test', description: 'Evaluates ability to retain learned information over time' },
                    { id: 'l_003', name: 'Transfer Assessment', description: 'Assesses ability to apply learning to new contexts' }
                ],
                creativity: [
                    { id: 'c_001', name: 'Divergent Thinking Test', description: 'Measures ability to generate multiple solutions to a problem' },
                    { id: 'c_002', name: 'Creative Output Evaluation', description: 'Assesses originality and value of creative products' },
                    { id: 'c_003', name: 'Combinatorial Creativity', description: 'Evaluates ability to combine existing ideas in novel ways' }
                ],
                planning: [
                    { id: 'p_001', name: 'Plan Quality Assessment', description: 'Evaluates the effectiveness and efficiency of created plans' },
                    { id: 'p_002', name: 'Plan Execution Test', description: 'Measures ability to execute plans successfully' },
                    { id: 'p_003', name: 'Plan Adaptation', description: 'Assesses ability to modify plans in response to changing circumstances' }
                ],
                problem_solving: [
                    { id: 'ps_001', name: 'Complex Problem Solving', description: 'Measures ability to solve multi-step problems' },
                    { id: 'ps_002', name: 'Solution Quality Assessment', description: 'Evaluates effectiveness and efficiency of solutions' },
                    { id: 'ps_003', name: 'Problem Identification', description: 'Assesses ability to identify and define problems accurately' }
                ],
                adaptation: [
                    { id: 'a_001', name: 'Adaptation Speed Test', description: 'Measures how quickly the system can adjust to new conditions' },
                    { id: 'a_002', name: 'Flexibility Assessment', description: 'Evaluates ability to change approaches when needed' },
                    { id: 'a_003', name: 'Novel Situation Performance', description: 'Assesses performance in previously unseen situations' }
                ],
                collaboration: [
                    { id: 'col_001', name: 'Communication Effectiveness', description: 'Measures clarity and usefulness of communications' },
                    { id: 'col_002', name: 'Coordination Assessment', description: 'Evaluates ability to coordinate activities with others' },
                    { id: 'col_003', name: 'Resource Sharing', description: 'Assesses willingness and effectiveness in sharing resources' }
                ],
                metacognition: [
                    { id: 'mc_001', name: 'Self-Monitoring Test', description: 'Measures ability to monitor own cognitive processes' },
                    { id: 'mc_002', name: 'Calibration Assessment', description: 'Evaluates accuracy of confidence in own knowledge' },
                    { id: 'mc_003', name: 'Strategy Selection', description: 'Assesses ability to select appropriate cognitive strategies' }
                ]
            };
            
            if (dimensionId && measurementMethods[dimensionId]) {
                return measurementMethods[dimensionId];
            } else if (dimensionId) {
                console.warn(`[SOPHIA] No measurement methods found for dimension: ${dimensionId}`);
                return [];
            } else {
                return measurementMethods;
            }
        } catch (error) {
            console.error('[SOPHIA] Error getting measurement methods:', error);
            return [];
        }
    }
    
    /**
     * Create new measurement
     * @param {Object} measurement - The measurement data
     */
    async createMeasurement(measurement) {
        try {
            console.log('[SOPHIA] Creating new measurement:', measurement);
            
            // In a real implementation, this would send to the API
            // For now, just return a success response
            return {
                success: true,
                message: 'Measurement created successfully',
                measurement: {
                    id: 'm_' + Date.now().toString(),
                    ...measurement,
                    timestamp: new Date().toISOString()
                }
            };
        } catch (error) {
            console.error('[SOPHIA] Error creating measurement:', error);
            return {
                success: false,
                message: 'Failed to create measurement',
                error: error.message
            };
        }
    }
}

// Create a singleton instance
window.sophiaIntelligenceService = window.sophiaIntelligenceService || new SophiaIntelligenceService();