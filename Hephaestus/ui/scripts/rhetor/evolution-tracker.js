/**
 * Evolution Tracker - Prompt Genealogy and Evolution Tracking
 * Tracks prompt mutations, success rates, and genealogical relationships
 */

class EvolutionTracker {
    constructor() {
        // MCP endpoint
        this.mcpEndpoint = 'http://localhost:8088/api/mcp/v2/execute';
        
        // Evolution data
        this.prompts = [];
        this.genealogy = {};
        this.metrics = {};
        
        // View state
        this.currentView = 'tree';
        this.selectedPrompt = null;
        
        // Initialize
        this.init();
    }
    
    async init() {
        console.log('[EvolutionTracker] Initializing prompt evolution tracking...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadEvolutionData();
        
        // Start periodic updates
        this.startPolling();
    }
    
    setupEventListeners() {
        // View mode selector
        const viewMode = document.getElementById('evolution-view-mode');
        if (viewMode) {
            viewMode.addEventListener('change', (e) => this.switchView(e.target.value));
        }
        
        // Refresh button
        const refreshBtn = document.getElementById('refresh-evolution');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadEvolutionData());
        }
        
        // Modal close
        const modalClose = document.querySelector('.rhetor__modal-close');
        if (modalClose) {
            modalClose.addEventListener('click', () => this.closeModal());
        }
    }
    
    async loadEvolutionData() {
        console.log('[EvolutionTracker] Loading evolution data...');
        
        try {
            // Fetch prompt evolution data using MCP tools
            const [promptData, behaviorData, memoryData] = await Promise.all([
                this.fetchPromptHistory(),
                this.fetchBehaviorPatterns(),
                this.fetchMemoryPatterns()
            ]);
            
            // Process and combine data
            this.processEvolutionData(promptData, behaviorData, memoryData);
            
            // Update stats
            this.updateStats();
            
            // Render current view
            this.renderView();
            
        } catch (error) {
            console.error('[EvolutionTracker] Error loading evolution data:', error);
        }
    }
    
    async fetchPromptHistory() {
        try {
            // Use PromptHistory MCP tool
            const response = await this.callMCPTool('PromptHistory', {
                ci_name: 'rhetor',
                limit: 100
            });
            
            if (response.success && response.history) {
                return response.history;
            }
            
            // Fallback to mock data for demo
            return this.getMockPromptHistory();
        } catch (error) {
            console.error('[EvolutionTracker] Error fetching prompt history:', error);
            return this.getMockPromptHistory();
        }
    }
    
    async fetchBehaviorPatterns() {
        try {
            // Use BehaviorPattern MCP tool for prompt success patterns
            const response = await this.callMCPTool('BehaviorPattern', {
                ci_name: 'rhetor',
                pattern_window: 7,
                pattern_threshold: 0.2
            });
            
            if (response.success && response.behavior_patterns) {
                return response.behavior_patterns;
            }
            
            return {};
        } catch (error) {
            console.error('[EvolutionTracker] Error fetching behavior patterns:', error);
            return {};
        }
    }
    
    async fetchMemoryPatterns() {
        try {
            // Use MemoryPattern MCP tool for prompt evolution patterns
            const response = await this.callMCPTool('MemoryPattern', {
                query: 'prompt evolution mutation success',
                pattern_type: 'behavioral',
                min_occurrences: 2
            });
            
            if (response.success && response.patterns) {
                return response.patterns;
            }
            
            return [];
        } catch (error) {
            console.error('[EvolutionTracker] Error fetching memory patterns:', error);
            return [];
        }
    }
    
    processEvolutionData(promptData, behaviorData, memoryData) {
        // Build genealogy tree
        this.buildGenealogy(promptData);
        
        // Calculate metrics
        this.calculateMetrics(promptData, behaviorData, memoryData);
        
        // Identify top performers
        this.identifyTopPerformers(promptData);
    }
    
    buildGenealogy(promptHistory) {
        this.genealogy = {
            root: null,
            generations: [],
            branches: {}
        };
        
        if (!promptHistory || promptHistory.length === 0) {
            return;
        }
        
        // Find root prompts (no parent)
        const roots = promptHistory.filter(p => !p.parent_id);
        if (roots.length > 0) {
            this.genealogy.root = roots[0];
        }
        
        // Build generation layers
        let currentGen = roots;
        let genNumber = 0;
        
        while (currentGen.length > 0) {
            this.genealogy.generations[genNumber] = currentGen;
            
            // Find children of current generation
            const nextGen = [];
            currentGen.forEach(prompt => {
                const children = promptHistory.filter(p => p.parent_id === prompt.id);
                if (children.length > 0) {
                    this.genealogy.branches[prompt.id] = children;
                    nextGen.push(...children);
                }
            });
            
            currentGen = nextGen;
            genNumber++;
        }
    }
    
    calculateMetrics(promptData, behaviorData, memoryData) {
        this.metrics = {
            totalPrompts: promptData ? promptData.length : 0,
            generations: this.genealogy.generations ? this.genealogy.generations.length : 0,
            successRate: this.calculateSuccessRate(promptData),
            activeBranches: Object.keys(this.genealogy.branches).length,
            categorySuccess: this.calculateCategorySuccess(promptData),
            evolutionEffectiveness: this.calculateEvolutionEffectiveness(promptData),
            mutationImpact: this.calculateMutationImpact(promptData)
        };
    }
    
    calculateSuccessRate(prompts) {
        if (!prompts || prompts.length === 0) return '0%';
        
        const successful = prompts.filter(p => p.success || p.score > 0.7).length;
        const rate = (successful / prompts.length) * 100;
        return `${rate.toFixed(1)}%`;
    }
    
    calculateCategorySuccess(prompts) {
        const categories = {};
        
        if (prompts) {
            prompts.forEach(prompt => {
                const category = prompt.category || 'general';
                if (!categories[category]) {
                    categories[category] = { total: 0, success: 0 };
                }
                categories[category].total++;
                if (prompt.success || prompt.score > 0.7) {
                    categories[category].success++;
                }
            });
        }
        
        return categories;
    }
    
    calculateEvolutionEffectiveness(prompts) {
        if (!prompts || prompts.length < 2) return 0;
        
        // Compare parent-child success rates
        let improvements = 0;
        let comparisons = 0;
        
        prompts.forEach(prompt => {
            if (prompt.parent_id) {
                const parent = prompts.find(p => p.id === prompt.parent_id);
                if (parent) {
                    comparisons++;
                    if ((prompt.score || 0) > (parent.score || 0)) {
                        improvements++;
                    }
                }
            }
        });
        
        return comparisons > 0 ? (improvements / comparisons) : 0;
    }
    
    calculateMutationImpact(prompts) {
        const impacts = [];
        
        if (prompts) {
            prompts.forEach(prompt => {
                if (prompt.parent_id) {
                    const parent = prompts.find(p => p.id === prompt.parent_id);
                    if (parent) {
                        const delta = (prompt.score || 0) - (parent.score || 0);
                        impacts.push({
                            prompt: prompt.name || prompt.id,
                            delta: delta,
                            type: prompt.mutation_type || 'refinement'
                        });
                    }
                }
            });
        }
        
        return impacts.sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta)).slice(0, 5);
    }
    
    identifyTopPerformers(prompts) {
        if (!prompts) return;
        
        this.topPerformers = prompts
            .filter(p => p.score !== undefined)
            .sort((a, b) => (b.score || 0) - (a.score || 0))
            .slice(0, 5);
    }
    
    updateStats() {
        // Update stat displays
        this.updateStatValue('total-prompts', this.metrics.totalPrompts);
        this.updateStatValue('prompt-generations', this.metrics.generations);
        this.updateStatValue('prompt-success-rate', this.metrics.successRate);
        this.updateStatValue('active-branches', this.metrics.activeBranches);
    }
    
    updateStatValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            const oldValue = element.textContent;
            element.textContent = value;
            
            // Animate if value changed
            if (oldValue !== value.toString()) {
                element.parentElement.classList.add('rhetor__evolution--animating');
                setTimeout(() => {
                    element.parentElement.classList.remove('rhetor__evolution--animating');
                }, 500);
            }
        }
    }
    
    switchView(viewType) {
        this.currentView = viewType;
        
        // Hide all views
        document.getElementById('genealogy-tree').style.display = 'none';
        document.getElementById('timeline-view').style.display = 'none';
        document.getElementById('metrics-view').style.display = 'none';
        
        // Show selected view
        switch (viewType) {
            case 'tree':
                document.getElementById('genealogy-tree').style.display = 'block';
                this.renderGenealogyTree();
                break;
            case 'timeline':
                document.getElementById('timeline-view').style.display = 'block';
                this.renderTimeline();
                break;
            case 'metrics':
                document.getElementById('metrics-view').style.display = 'block';
                this.renderMetrics();
                break;
        }
    }
    
    renderView() {
        switch (this.currentView) {
            case 'tree':
                this.renderGenealogyTree();
                break;
            case 'timeline':
                this.renderTimeline();
                break;
            case 'metrics':
                this.renderMetrics();
                break;
        }
    }
    
    renderGenealogyTree() {
        const container = document.getElementById('genealogy-tree');
        if (!container) return;
        
        // Clear loading state
        container.innerHTML = '';
        
        if (!this.genealogy.root) {
            container.innerHTML = `
                <div class="rhetor__genealogy-loading">
                    <span>🧬</span>
                    <p>No prompt genealogy data available yet.</p>
                </div>
            `;
            return;
        }
        
        // Create tree visualization
        const tree = document.createElement('div');
        tree.className = 'rhetor__tree-container';
        
        // Render each generation
        this.genealogy.generations.forEach((generation, index) => {
            const genLayer = document.createElement('div');
            genLayer.className = 'rhetor__tree-generation';
            genLayer.style.marginLeft = `${index * 50}px`;
            
            generation.forEach(prompt => {
                const node = this.createTreeNode(prompt, index === 0);
                genLayer.appendChild(node);
            });
            
            tree.appendChild(genLayer);
        });
        
        container.appendChild(tree);
    }
    
    createTreeNode(prompt, isRoot = false) {
        const node = document.createElement('div');
        node.className = `rhetor__tree-node ${isRoot ? 'rhetor__tree-node--root' : ''}`;
        
        if (prompt.success || (prompt.score && prompt.score > 0.7)) {
            node.className += ' rhetor__tree-node--success';
        } else if (prompt.score && prompt.score < 0.3) {
            node.className += ' rhetor__tree-node--failed';
        }
        
        const successRate = prompt.score ? Math.round(prompt.score * 100) : 0;
        
        node.innerHTML = `
            <div class="rhetor__node-title">${prompt.name || `Prompt ${prompt.id}`}</div>
            <div class="rhetor__node-stats">
                <span class="rhetor__node-stat">
                    <span>📊</span> ${successRate}%
                </span>
                <span class="rhetor__node-stat">
                    <span>🔄</span> ${prompt.uses || 0}
                </span>
            </div>
        `;
        
        node.addEventListener('click', () => this.showPromptDetails(prompt));
        
        return node;
    }
    
    renderTimeline() {
        const container = document.getElementById('timeline-view');
        if (!container) return;
        
        container.innerHTML = '';
        
        // Create timeline items
        const timeline = this.genealogy.generations.flat().sort((a, b) => 
            new Date(b.created_at || Date.now()) - new Date(a.created_at || Date.now())
        );
        
        timeline.slice(0, 20).forEach(prompt => {
            const item = document.createElement('div');
            item.className = 'rhetor__timeline-item';
            
            const time = prompt.created_at ? new Date(prompt.created_at).toLocaleString() : 'Recently';
            const successRate = prompt.score ? Math.round(prompt.score * 100) : 0;
            
            item.innerHTML = `
                <div class="rhetor__timeline-marker"></div>
                <div class="rhetor__timeline-content">
                    <div class="rhetor__timeline-time">${time}</div>
                    <div class="rhetor__timeline-title">${prompt.name || `Prompt ${prompt.id}`}</div>
                    <div class="rhetor__timeline-description">
                        Success Rate: ${successRate}% | 
                        Uses: ${prompt.uses || 0} | 
                        ${prompt.mutation_type || 'Original'}
                    </div>
                </div>
            `;
            
            container.appendChild(item);
        });
    }
    
    renderMetrics() {
        // Render category success bars
        this.renderCategorySuccess();
        
        // Render evolution effectiveness chart
        this.renderEvolutionChart();
        
        // Render top performers list
        this.renderTopPerformers();
        
        // Render mutation impact
        this.renderMutationImpact();
    }
    
    renderCategorySuccess() {
        const container = document.getElementById('category-success');
        if (!container) return;
        
        container.innerHTML = '';
        
        Object.entries(this.metrics.categorySuccess).forEach(([category, data]) => {
            const successRate = data.total > 0 ? (data.success / data.total) * 100 : 0;
            
            const bar = document.createElement('div');
            bar.className = 'rhetor__metric-bar';
            bar.innerHTML = `
                <span class="rhetor__metric-label">${category}</span>
                <div class="rhetor__metric-progress">
                    <div class="rhetor__metric-fill" style="width: ${successRate}%">
                        <span class="rhetor__metric-value">${successRate.toFixed(0)}%</span>
                    </div>
                </div>
            `;
            
            container.appendChild(bar);
        });
    }
    
    renderEvolutionChart() {
        const container = document.getElementById('evolution-chart');
        if (!container) return;
        
        const effectiveness = Math.round(this.metrics.evolutionEffectiveness * 100);
        
        container.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 48px; font-weight: 700; 
                            background: linear-gradient(135deg, #673AB7 0%, #2196F3 100%);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;">
                    ${effectiveness}%
                </div>
                <div style="color: #666; margin-top: 10px;">
                    of mutations improve performance
                </div>
            </div>
        `;
    }
    
    renderTopPerformers() {
        const container = document.getElementById('top-prompts');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (!this.topPerformers || this.topPerformers.length === 0) {
            container.innerHTML = '<p style="color: #999;">No performance data available</p>';
            return;
        }
        
        this.topPerformers.forEach((prompt, index) => {
            const item = document.createElement('div');
            item.className = 'rhetor__metric-item';
            
            const score = Math.round((prompt.score || 0) * 100);
            
            item.innerHTML = `
                <span class="rhetor__metric-rank">#${index + 1}</span>
                <span class="rhetor__metric-name">${prompt.name || `Prompt ${prompt.id}`}</span>
                <span class="rhetor__metric-score">${score}%</span>
            `;
            
            container.appendChild(item);
        });
    }
    
    renderMutationImpact() {
        const container = document.getElementById('mutation-impact');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (!this.metrics.mutationImpact || this.metrics.mutationImpact.length === 0) {
            container.innerHTML = '<p style="color: #999;">No mutation data available</p>';
            return;
        }
        
        this.metrics.mutationImpact.forEach(impact => {
            const item = document.createElement('div');
            const isPositive = impact.delta > 0;
            
            item.className = `rhetor__delta-item rhetor__delta-item--${isPositive ? 'positive' : 'negative'}`;
            
            item.innerHTML = `
                <span class="rhetor__delta-label">${impact.type}</span>
                <span class="rhetor__delta-value rhetor__delta-value--${isPositive ? 'positive' : 'negative'}">
                    <span class="rhetor__delta-arrow">${isPositive ? '↑' : '↓'}</span>
                    ${Math.abs(impact.delta * 100).toFixed(1)}%
                </span>
            `;
            
            container.appendChild(item);
        });
    }
    
    showPromptDetails(prompt) {
        const modal = document.getElementById('prompt-detail-modal');
        const body = document.getElementById('prompt-detail-body');
        
        if (!modal || !body) return;
        
        const successRate = prompt.score ? Math.round(prompt.score * 100) : 0;
        
        body.innerHTML = `
            <div><strong>Name:</strong> ${prompt.name || `Prompt ${prompt.id}`}</div>
            <div><strong>Success Rate:</strong> ${successRate}%</div>
            <div><strong>Uses:</strong> ${prompt.uses || 0}</div>
            <div><strong>Created:</strong> ${prompt.created_at ? new Date(prompt.created_at).toLocaleString() : 'Unknown'}</div>
            ${prompt.parent_id ? `<div><strong>Parent:</strong> Prompt ${prompt.parent_id}</div>` : ''}
            ${prompt.mutation_type ? `<div><strong>Mutation Type:</strong> ${prompt.mutation_type}</div>` : ''}
            ${prompt.template ? `
                <div style="margin-top: 15px;">
                    <strong>Template:</strong>
                    <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; 
                               max-height: 200px; overflow-y: auto; font-size: 12px;">
${prompt.template}
                    </pre>
                </div>
            ` : ''}
        `;
        
        modal.style.display = 'flex';
    }
    
    closeModal() {
        const modal = document.getElementById('prompt-detail-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    startPolling() {
        // Refresh data every 60 seconds
        setInterval(() => {
            this.loadEvolutionData();
        }, 60000);
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
    
    // Mock data for demo
    getMockPromptHistory() {
        return [
            {
                id: 'p001',
                name: 'Base Analysis Prompt',
                score: 0.75,
                uses: 145,
                created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
                category: 'analysis',
                template: 'Analyze the following data and provide insights...'
            },
            {
                id: 'p002',
                parent_id: 'p001',
                name: 'Enhanced Analysis v2',
                score: 0.82,
                uses: 89,
                created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
                category: 'analysis',
                mutation_type: 'context_expansion',
                template: 'Analyze the following data with context awareness...'
            },
            {
                id: 'p003',
                parent_id: 'p002',
                name: 'Analysis with Examples',
                score: 0.88,
                uses: 67,
                created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
                category: 'analysis',
                mutation_type: 'example_addition',
                template: 'Analyze the following data using these examples...'
            },
            {
                id: 'p004',
                parent_id: 'p001',
                name: 'Simplified Analysis',
                score: 0.71,
                uses: 34,
                created_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000),
                category: 'analysis',
                mutation_type: 'simplification'
            },
            {
                id: 'p005',
                name: 'Code Generation Base',
                score: 0.65,
                uses: 201,
                created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
                category: 'code_gen'
            },
            {
                id: 'p006',
                parent_id: 'p005',
                name: 'Code Gen with Tests',
                score: 0.79,
                uses: 156,
                created_at: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),
                category: 'code_gen',
                mutation_type: 'test_addition'
            },
            {
                id: 'p007',
                parent_id: 'p006',
                name: 'Code Gen with Docs',
                score: 0.85,
                uses: 98,
                created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
                category: 'code_gen',
                mutation_type: 'documentation'
            },
            {
                id: 'p008',
                name: 'Summary Generator',
                score: 0.70,
                uses: 312,
                created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
                category: 'summary'
            },
            {
                id: 'p009',
                parent_id: 'p008',
                name: 'Bullet Point Summary',
                score: 0.78,
                uses: 189,
                created_at: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000),
                category: 'summary',
                mutation_type: 'format_change'
            },
            {
                id: 'p010',
                parent_id: 'p003',
                name: 'Multi-Modal Analysis',
                score: 0.91,
                uses: 23,
                created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
                category: 'analysis',
                mutation_type: 'capability_expansion'
            }
        ];
    }
}

// Initialize Evolution Tracker when Evolution tab is selected
document.addEventListener('DOMContentLoaded', () => {
    const evolutionTab = document.getElementById('tab-evolution');
    if (evolutionTab) {
        evolutionTab.addEventListener('change', () => {
            if (evolutionTab.checked && !window.evolutionTracker) {
                window.evolutionTracker = new EvolutionTracker();
            }
        });
        
        // Initialize if Evolution tab is already selected
        if (evolutionTab.checked) {
            window.evolutionTracker = new EvolutionTracker();
        }
    }
});