/**
 * Registry Integration for Ergon UI
 * Connects the Registry panel to the Ergon Registry API
 */

class RegistryIntegration {
    constructor() {
        // Use environment-aware port (8102 for Coder-A)
        this.baseUrl = window.location.port === '8088' 
            ? 'http://localhost:8102/api/ergon/registry'
            : `http://localhost:${window.location.port}/api/ergon/registry`;
        
        this.solutions = [];
        this.filteredSolutions = [];
        this.currentFilters = {
            search: '',
            type: '',
            capability: '',
            meetsStandards: null
        };
    }

    /**
     * Initialize the Registry integration
     */
    async init() {
        console.log('[Registry] Initializing Registry integration...');
        
        // Bind event listeners
        this.bindEventListeners();
        
        // Load initial data
        await this.loadSolutions();
        
        // Check Registry health
        await this.checkHealth();
    }

    /**
     * Bind event listeners for Registry UI
     */
    bindEventListeners() {
        // Search input
        const searchInput = document.getElementById('registry-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.currentFilters.search = e.target.value;
                this.applyFilters();
            });
        }

        // Type filter
        const typeFilter = document.getElementById('registry-type-filter');
        if (typeFilter) {
            typeFilter.addEventListener('change', (e) => {
                this.currentFilters.type = e.target.value;
                this.applyFilters();
            });
        }

        // Capability filter
        const capabilityFilter = document.getElementById('registry-capability-filter');
        if (capabilityFilter) {
            capabilityFilter.addEventListener('change', (e) => {
                this.currentFilters.capability = e.target.value;
                this.applyFilters();
            });
        }
    }

    /**
     * Load solutions from Registry API
     */
    async loadSolutions() {
        try {
            const response = await fetch(`${this.baseUrl}/search?limit=100`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            this.solutions = data.results || [];
            this.filteredSolutions = [...this.solutions];
            
            console.log(`[Registry] Loaded ${this.solutions.length} solutions`);
            this.renderSolutions();
            
        } catch (error) {
            console.error('[Registry] Failed to load solutions:', error);
            this.showError('Failed to load solutions from Registry');
        }
    }

    /**
     * Apply filters to solutions
     */
    applyFilters() {
        this.filteredSolutions = this.solutions.filter(solution => {
            // Search filter
            if (this.currentFilters.search) {
                const search = this.currentFilters.search.toLowerCase();
                const matchesSearch = 
                    solution.name?.toLowerCase().includes(search) ||
                    solution.description?.toLowerCase().includes(search) ||
                    solution.tags?.some(tag => tag.toLowerCase().includes(search));
                
                if (!matchesSearch) return false;
            }

            // Type filter
            if (this.currentFilters.type && solution.type !== this.currentFilters.type) {
                return false;
            }

            // Capability filter (using tags for now)
            if (this.currentFilters.capability) {
                const hasCapability = solution.tags?.includes(this.currentFilters.capability);
                if (!hasCapability) return false;
            }

            // Standards filter
            if (this.currentFilters.meetsStandards !== null) {
                if (solution.meets_standards !== this.currentFilters.meetsStandards) {
                    return false;
                }
            }

            return true;
        });

        this.renderSolutions();
    }

    /**
     * Render solutions in the grid
     */
    renderSolutions() {
        const grid = document.getElementById('solution-grid');
        if (!grid) return;

        // Clear existing content
        grid.innerHTML = '';
        
        if (this.filteredSolutions.length === 0) {
            grid.innerHTML = `
                <div class="ergon__empty-message" data-tekton-type="empty-state">
                    <div class="ergon__message-text">No solutions match your filters</div>
                </div>
            `;
            grid.setAttribute('data-tekton-state', 'empty');
            return;
        }

        grid.setAttribute('data-tekton-state', 'populated');
        
        // Render solution cards
        this.filteredSolutions.forEach(solution => {
            const card = this.createSolutionCard(solution);
            grid.appendChild(card);
        });
    }

    /**
     * Create a solution card element
     */
    createSolutionCard(solution) {
        const card = document.createElement('div');
        card.className = 'ergon__solution-card';
        card.setAttribute('data-tekton-component', 'solution-card');
        card.setAttribute('data-tekton-solution-id', solution.id);
        card.setAttribute('data-tekton-solution-type', solution.type);
        
        // Standards compliance badge
        const complianceBadge = solution.meets_standards 
            ? '<span class="ergon__badge ergon__badge--success" data-tekton-badge="compliant">✓ Standards</span>'
            : '<span class="ergon__badge ergon__badge--warning" data-tekton-badge="non-compliant">⚠ Review</span>';
        
        // Version badge
        const versionBadge = solution.version 
            ? `<span class="ergon__badge ergon__badge--info" data-tekton-badge="version">v${solution.version}</span>`
            : '';
        
        // Tags
        const tags = (solution.tags || []).map(tag => 
            `<span class="ergon__tag" data-tekton-tag="${tag}">${tag}</span>`
        ).join('');
        
        card.innerHTML = `
            <div class="ergon__card-header">
                <h4 class="ergon__card-title" data-tekton-element="solution-name">${solution.name || 'Unnamed Solution'}</h4>
                <div class="ergon__badge-group">
                    ${complianceBadge}
                    ${versionBadge}
                </div>
            </div>
            <div class="ergon__card-body">
                <p class="ergon__card-description" data-tekton-element="solution-description">
                    ${solution.description || 'No description available'}
                </p>
                <div class="ergon__card-meta">
                    <span class="ergon__meta-item" data-tekton-meta="type">
                        Type: <strong>${solution.type}</strong>
                    </span>
                    <span class="ergon__meta-item" data-tekton-meta="created">
                        Created: ${this.formatDate(solution.created)}
                    </span>
                </div>
                ${tags ? `<div class="ergon__tag-list" data-tekton-element="tags">${tags}</div>` : ''}
            </div>
            <div class="ergon__card-actions">
                <button class="ergon__button ergon__button--primary" 
                        onclick="registryIntegration.testSolution('${solution.id}')"
                        data-tekton-action="test-solution"
                        data-tekton-target="${solution.id}">
                    Test
                </button>
                <button class="ergon__button" 
                        onclick="registryIntegration.viewDetails('${solution.id}')"
                        data-tekton-action="view-details"
                        data-tekton-target="${solution.id}">
                    Details
                </button>
                <button class="ergon__button" 
                        onclick="registryIntegration.checkStandards('${solution.id}')"
                        data-tekton-action="check-standards"
                        data-tekton-target="${solution.id}">
                    Check Standards
                </button>
            </div>
        `;
        
        return card;
    }

    /**
     * Test a solution (placeholder for Sandbox integration)
     */
    async testSolution(solutionId) {
        console.log(`[Registry] Testing solution ${solutionId}`);
        alert(`Testing solution ${solutionId}\n\nThis will be connected to the Sandbox in Phase 1.5`);
    }

    /**
     * View solution details
     */
    async viewDetails(solutionId) {
        try {
            const response = await fetch(`${this.baseUrl}/${solutionId}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const solution = await response.json();
            
            // Show details in a modal or console for now
            console.log('[Registry] Solution details:', solution);
            alert(`Solution Details:\n\nName: ${solution.name}\nType: ${solution.type}\nVersion: ${solution.version}\n\nSee console for full details`);
            
        } catch (error) {
            console.error('[Registry] Failed to get solution details:', error);
            this.showError('Failed to load solution details');
        }
    }

    /**
     * Check standards compliance
     */
    async checkStandards(solutionId) {
        try {
            const response = await fetch(`${this.baseUrl}/${solutionId}/check-standards`, {
                method: 'POST'
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const result = await response.json();
            const report = result.report;
            
            // Format compliance report
            const checks = Object.entries(report.checks || {})
                .map(([check, passed]) => `${passed ? '✓' : '✗'} ${check}: ${passed}`)
                .join('\n');
            
            alert(`Standards Compliance Report\n\nSolution: ${report.name}\nScore: ${(report.compliance_score * 100).toFixed(0)}%\n\nChecks:\n${checks}`);
            
            // Reload to update compliance badge
            await this.loadSolutions();
            
        } catch (error) {
            console.error('[Registry] Failed to check standards:', error);
            this.showError('Failed to check standards compliance');
        }
    }

    /**
     * Check Registry health
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const health = await response.json();
            console.log('[Registry] Health check:', health);
            
            // Update UI with health status
            this.updateHealthIndicator(health);
            
        } catch (error) {
            console.error('[Registry] Health check failed:', error);
            this.updateHealthIndicator({ status: 'error' });
        }
    }

    /**
     * Update health indicator in UI
     */
    updateHealthIndicator(health) {
        // Add health indicator to panel header if not exists
        let indicator = document.querySelector('.ergon__health-indicator');
        if (!indicator) {
            const header = document.querySelector('#registry-panel .ergon__panel-header');
            if (header) {
                indicator = document.createElement('div');
                indicator.className = 'ergon__health-indicator';
                indicator.setAttribute('data-tekton-component', 'health-indicator');
                header.appendChild(indicator);
            }
        }
        
        if (indicator) {
            const status = health.status === 'healthy' ? 'healthy' : 'error';
            const stats = health.statistics || {};
            
            indicator.innerHTML = `
                <span class="ergon__health-status ergon__health-status--${status}" 
                      data-tekton-status="${status}">
                    ${status === 'healthy' ? '●' : '○'} Registry ${status}
                </span>
                ${stats.total_units !== undefined ? `
                    <span class="ergon__health-stat" data-tekton-stat="total">
                        ${stats.total_units} solutions
                    </span>
                    <span class="ergon__health-stat" data-tekton-stat="compliance">
                        ${stats.compliance_rate || '0%'} compliant
                    </span>
                ` : ''}
            `;
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const grid = document.getElementById('solution-grid');
        if (grid) {
            grid.innerHTML = `
                <div class="ergon__error-message" data-tekton-type="error-state">
                    <div class="ergon__message-text">${message}</div>
                </div>
            `;
            grid.setAttribute('data-tekton-state', 'error');
        }
    }

    /**
     * Format date for display
     */
    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }
}

// Initialize Registry integration when DOM is ready
let registryIntegration;

document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're on the Ergon component
    if (document.querySelector('#registry-panel')) {
        registryIntegration = new RegistryIntegration();
        
        // Initialize when Registry tab is clicked
        const registryTab = document.querySelector('label[for="ergon-tab-registry"]');
        if (registryTab) {
            registryTab.addEventListener('click', () => {
                setTimeout(() => {
                    if (!registryIntegration.solutions.length) {
                        registryIntegration.init();
                    }
                }, 100);
            });
        }
        
        console.log('[Registry] Integration ready');
    }
});