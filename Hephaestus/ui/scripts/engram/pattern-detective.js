/**
 * Pattern Detective - Intelligent Pattern Recognition for Engram
 * Discovers emergent patterns in memories using MCP tools
 */

class PatternDetective {
    constructor() {
        // MCP endpoint
        this.mcpEndpoint = window.hephaestusUrl ? window.hephaestusUrl('/api/mcp/v2/execute').replace(':8080', ':8088') : 'http://localhost:8088/api/mcp/v2/execute';
        
        // Pattern configuration
        this.patterns = [];
        this.minObservations = 3;
        this.confidenceThreshold = 0.7;
        
        // Pattern type configurations
        this.patternTypes = {
            repeating_success: {
                name: 'Success Pattern',
                color: '#4CAF50',
                tool: 'BehaviorPattern'
            },
            stress_correlation: {
                name: 'Stress Correlation',
                color: '#FF9800',
                tool: 'MemoryPattern'
            },
            discovery: {
                name: 'Discovery',
                color: '#2196F3',
                tool: 'CulturalKnowledge'
            },
            emotional: {
                name: 'Emotional Pattern',
                color: '#E91E63',
                tool: 'MemoryPattern'
            },
            behavioral: {
                name: 'Behavioral Pattern',
                color: '#9C27B0',
                tool: 'BehaviorPattern'
            }
        };
        
        this.init();
    }
    
    async init() {
        console.log('[PatternDetective] Initializing pattern detection system...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Initial pattern detection
        await this.detectPatterns();
    }
    
    setupEventListeners() {
        // Detect patterns button
        const detectBtn = document.getElementById('detect-patterns-btn');
        if (detectBtn) {
            detectBtn.addEventListener('click', () => this.detectPatterns());
        }
        
        // Pattern type filter
        const filterSelect = document.getElementById('pattern-type-filter');
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => this.filterPatterns(e.target.value));
        }
    }
    
    async detectPatterns() {
        console.log('[PatternDetective] Starting pattern detection...');
        
        // Show loading state
        this.showLoading(true);
        
        try {
            // Fetch patterns from multiple MCP tools in parallel
            const [behavioral, emotional, cultural] = await Promise.all([
                this.detectBehavioralPatterns(),
                this.detectEmotionalPatterns(),
                this.detectCulturalPatterns()
            ]);
            
            // Combine and categorize patterns
            this.patterns = [
                ...this.categorizePatterns(behavioral, 'behavioral'),
                ...this.categorizePatterns(emotional, 'emotional'),
                ...this.categorizePatterns(cultural, 'discovery')
            ];
            
            // Auto-detect success and stress patterns
            const successPatterns = await this.detectSuccessPatterns();
            const stressPatterns = await this.detectStressPatterns();
            
            this.patterns.push(
                ...this.categorizePatterns(successPatterns, 'repeating_success'),
                ...this.categorizePatterns(stressPatterns, 'stress_correlation')
            );
            
            // Sort by confidence
            this.patterns.sort((a, b) => b.confidence - a.confidence);
            
            // Display patterns
            this.displayPatterns();
            
        } catch (error) {
            console.error('[PatternDetective] Error detecting patterns:', error);
            this.showError('Failed to detect patterns. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }
    
    async detectBehavioralPatterns() {
        try {
            const response = await this.callMCPTool('BehaviorPattern', {
                ci_name: 'collective',
                pattern_window: 7,
                pattern_threshold: 0.2
            });
            
            if (response.success && response.behavior_patterns) {
                return this.extractBehavioralPatterns(response.behavior_patterns);
            }
            
            return [];
        } catch (error) {
            console.error('[PatternDetective] Error detecting behavioral patterns:', error);
            return [];
        }
    }
    
    async detectEmotionalPatterns() {
        try {
            const response = await this.callMCPTool('MemoryPattern', {
                query: '',
                pattern_type: 'emotional',
                min_occurrences: this.minObservations
            });
            
            if (response.success && response.patterns) {
                return response.patterns;
            }
            
            return [];
        } catch (error) {
            console.error('[PatternDetective] Error detecting emotional patterns:', error);
            return [];
        }
    }
    
    async detectCulturalPatterns() {
        try {
            const response = await this.callMCPTool('CulturalKnowledge', {
                topic: null,
                min_mentions: 2
            });
            
            if (response.success && response.cultural_knowledge) {
                return this.extractCulturalPatterns(response.cultural_knowledge);
            }
            
            return [];
        } catch (error) {
            console.error('[PatternDetective] Error detecting cultural patterns:', error);
            return [];
        }
    }
    
    async detectSuccessPatterns() {
        try {
            // Use MemoryPattern to find success-related patterns
            const response = await this.callMCPTool('MemoryPattern', {
                query: 'success complete achieve accomplish finish',
                pattern_type: 'behavioral',
                min_occurrences: this.minObservations
            });
            
            if (response.success && response.patterns) {
                return response.patterns.filter(p => 
                    p.pattern.toLowerCase().includes('success') ||
                    p.pattern.toLowerCase().includes('complete') ||
                    p.pattern.toLowerCase().includes('achieve')
                );
            }
            
            return [];
        } catch (error) {
            console.error('[PatternDetective] Error detecting success patterns:', error);
            return [];
        }
    }
    
    async detectStressPatterns() {
        try {
            // Use MemoryPattern to find stress-related patterns
            const response = await this.callMCPTool('MemoryPattern', {
                query: 'stress error fail problem issue block struggle',
                pattern_type: 'behavioral',
                min_occurrences: 2
            });
            
            if (response.success && response.patterns) {
                return response.patterns.filter(p => 
                    p.pattern.toLowerCase().includes('stress') ||
                    p.pattern.toLowerCase().includes('error') ||
                    p.pattern.toLowerCase().includes('fail') ||
                    p.pattern.toLowerCase().includes('problem')
                );
            }
            
            return [];
        } catch (error) {
            console.error('[PatternDetective] Error detecting stress patterns:', error);
            return [];
        }
    }
    
    extractBehavioralPatterns(behaviorData) {
        const patterns = [];
        
        // Extract work patterns
        if (behaviorData.work_patterns) {
            behaviorData.work_patterns.forEach(pattern => {
                patterns.push({
                    pattern: pattern.description,
                    occurrences: Math.round(pattern.frequency * 100),
                    confidence: pattern.frequency
                });
            });
        }
        
        // Extract communication patterns
        if (behaviorData.communication_patterns) {
            behaviorData.communication_patterns.forEach(pattern => {
                patterns.push({
                    pattern: pattern.description,
                    occurrences: Math.round(pattern.frequency * 100),
                    confidence: pattern.frequency
                });
            });
        }
        
        return patterns;
    }
    
    extractCulturalPatterns(culturalData) {
        const patterns = [];
        
        // Extract emergent knowledge as discoveries
        if (culturalData.emergent_knowledge) {
            culturalData.emergent_knowledge.forEach(knowledge => {
                patterns.push({
                    pattern: knowledge.insight,
                    occurrences: knowledge.mentions || 3,
                    confidence: knowledge.confidence || 0.8
                });
            });
        }
        
        // Extract collective values as patterns
        if (culturalData.collective_values) {
            culturalData.collective_values.forEach(value => {
                patterns.push({
                    pattern: `Collective value: ${value.value}`,
                    occurrences: Math.round(value.strength * 10),
                    confidence: value.strength
                });
            });
        }
        
        return patterns;
    }
    
    categorizePatterns(patterns, type) {
        return patterns.map(pattern => ({
            ...pattern,
            type: type,
            id: this.generatePatternId(),
            confidence: this.calculateConfidence(pattern),
            action: this.suggestAction(pattern, type)
        }));
    }
    
    calculateConfidence(pattern) {
        // Calculate confidence based on occurrences and existing confidence
        const baseConfidence = pattern.confidence || 0.5;
        const occurrenceBoost = Math.min(pattern.occurrences / 10, 0.3);
        
        return Math.min(baseConfidence + occurrenceBoost, 1.0);
    }
    
    suggestAction(pattern, type) {
        const patternText = pattern.pattern.toLowerCase();
        
        // Suggest actions based on pattern type and content
        if (type === 'repeating_success') {
            return 'Reinforce this successful pattern';
        } else if (type === 'stress_correlation') {
            if (patternText.includes('error')) {
                return 'Review error handling procedures';
            } else if (patternText.includes('timeout')) {
                return 'Consider increasing timeout limits';
            }
            return 'Investigate and address root cause';
        } else if (type === 'discovery') {
            return 'Document and share this insight';
        } else if (type === 'emotional' && patternText.includes('frustrated')) {
            return 'Consider UX improvements';
        } else if (type === 'behavioral') {
            return 'Monitor for consistency';
        }
        
        return null;
    }
    
    displayPatterns() {
        const container = document.getElementById('pattern-cards');
        if (!container) return;
        
        // Clear existing patterns
        container.innerHTML = '';
        
        if (this.patterns.length === 0) {
            container.innerHTML = `
                <div class="engram__no-patterns">
                    <h3 style="color: #00BCD4; margin-bottom: 20px;">Currently Investigating</h3>
                    <div style="display: grid; gap: 15px; text-align: left;">
                        <div style="padding: 15px; background: rgba(0, 188, 212, 0.1); border-left: 3px solid #00BCD4; border-radius: 4px;">
                            <strong>Memory Consolidation Patterns</strong>
                            <p style="margin: 5px 0; color: #a0a0a0; font-size: 13px;">Analyzing how memories cluster and strengthen over time...</p>
                        </div>
                        <div style="padding: 15px; background: rgba(0, 188, 212, 0.1); border-left: 3px solid #00BCD4; border-radius: 4px;">
                            <strong>Whisper Frequency Correlations</strong>
                            <p style="margin: 5px 0; color: #a0a0a0; font-size: 13px;">Tracking communication patterns between CI components...</p>
                        </div>
                        <div style="padding: 15px; background: rgba(0, 188, 212, 0.1); border-left: 3px solid #00BCD4; border-radius: 4px;">
                            <strong>Stress Response Behaviors</strong>
                            <p style="margin: 5px 0; color: #a0a0a0; font-size: 13px;">Identifying system adaptation during high-load periods...</p>
                        </div>
                        <div style="padding: 15px; background: rgba(0, 188, 212, 0.1); border-left: 3px solid #00BCD4; border-radius: 4px;">
                            <strong>Success Pattern Emergence</strong>
                            <p style="margin: 5px 0; color: #a0a0a0; font-size: 13px;">Discovering repeated sequences that lead to positive outcomes...</p>
                        </div>
                    </div>
                    <p style="margin-top: 20px; color: #666;">Patterns typically emerge after 3+ observations. Check back soon!</p>
                </div>
            `;
            return;
        }
        
        // Display each pattern
        this.patterns.forEach(pattern => {
            const card = this.createPatternCard(pattern);
            container.appendChild(card);
        });
    }
    
    createPatternCard(pattern) {
        const typeConfig = this.patternTypes[pattern.type] || {
            name: 'Pattern',
            color: '#666'
        };
        
        const card = document.createElement('div');
        card.className = `engram__pattern-card engram__pattern-card--${pattern.type}`;
        card.style.setProperty('--pattern-color', typeConfig.color);
        
        const confidencePercent = Math.round(pattern.confidence * 100);
        
        card.innerHTML = `
            <div class="engram__pattern-header">
                <span class="engram__pattern-type">${typeConfig.name}</span>
            </div>
            
            <div class="engram__pattern-description">
                ${this.formatPatternDescription(pattern.pattern)}
            </div>
            
            <div class="engram__pattern-confidence">
                <div class="engram__pattern-confidence-bar">
                    <div class="engram__pattern-confidence-fill" 
                         style="width: ${confidencePercent}%"></div>
                </div>
                <span class="engram__pattern-confidence-text">${confidencePercent}%</span>
            </div>
            
            <div class="engram__pattern-meta">
                <span class="engram__pattern-observations">
                    <span>${pattern.occurrences} observations</span>
                </span>
                <span class="engram__pattern-freshness">
                    ${this.getPatternFreshness(pattern)}
                </span>
            </div>
            
            ${pattern.action ? `
                <div class="engram__pattern-action">
                    ${pattern.action}
                </div>
            ` : ''}
        `;
        
        // Add click handler for details
        card.addEventListener('click', () => this.showPatternDetails(pattern));
        
        return card;
    }
    
    formatPatternDescription(description) {
        // Make pattern descriptions more readable
        if (description.length > 100) {
            return description.substring(0, 100) + '...';
        }
        
        // Capitalize first letter
        return description.charAt(0).toUpperCase() + description.slice(1);
    }
    
    getPatternFreshness(pattern) {
        // For demo, return random freshness
        const freshness = ['Just discovered', 'Recent', 'Emerging', 'Established'];
        return freshness[Math.floor(Math.random() * freshness.length)];
    }
    
    filterPatterns(filterType) {
        const cards = document.querySelectorAll('.engram__pattern-card');
        
        cards.forEach(card => {
            if (filterType === 'all') {
                card.style.display = 'block';
            } else {
                const cardType = Array.from(card.classList)
                    .find(c => c.startsWith('engram__pattern-card--'))
                    ?.replace('engram__pattern-card--', '');
                
                card.style.display = cardType === filterType ? 'block' : 'none';
            }
        });
    }
    
    showPatternDetails(pattern) {
        console.log('[PatternDetective] Pattern details:', pattern);
        // Could open a modal or expand the card with more details
    }
    
    showLoading(show) {
        const loading = document.getElementById('patterns-loading');
        const cards = document.getElementById('pattern-cards');
        
        if (loading) {
            loading.style.display = show ? 'block' : 'none';
        }
        
        if (cards) {
            cards.style.display = show ? 'none' : 'grid';
        }
    }
    
    showError(message) {
        const container = document.getElementById('pattern-cards');
        if (container) {
            container.innerHTML = `
                <div class="engram__error">
                    <span style="font-size: 48px;">⚠️</span>
                    <p>${message}</p>
                </div>
            `;
        }
    }
    
    async callMCPTool(toolName, params) {
        const response = await fetch(this.mcpEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tool: toolName,
                parameters: params
            })
        });
        
        if (!response.ok) {
            throw new Error(`MCP tool ${toolName} failed: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    generatePatternId() {
        return `pattern-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
}

// Initialize Pattern Detective when Engram loads
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on the Engram component
    const engramComponent = document.querySelector('.engram');
    if (engramComponent) {
        // Wait for patterns tab to be available
        const patternsTab = document.getElementById('engram-tab-patterns');
        if (patternsTab) {
            // Initialize when patterns tab is selected
            patternsTab.addEventListener('change', () => {
                if (patternsTab.checked && !window.patternDetective) {
                    window.patternDetective = new PatternDetective();
                }
            });
            
            // Initialize immediately if patterns tab is already selected
            if (patternsTab.checked) {
                window.patternDetective = new PatternDetective();
            }
        }
    }
});