/**
 * Registry integration for Ergon UI.
 * 
 * Handles loading, displaying, and interacting with Registry solutions.
 */

// Global registry state
window.ergonRegistry = {
    solutions: [],
    currentFilter: 'all'
};

/**
 * Load solutions from Registry
 */
async function loadRegistrySolutions() {
    try {
        const response = await fetch('/api/ergon/registry/search?limit=100');
        if (!response.ok) {
            throw new Error(`Failed to load solutions: ${response.statusText}`);
        }
        
        const data = await response.json();
        window.ergonRegistry.solutions = data.results || [];
        
        displaySolutions(window.ergonRegistry.solutions);
        updateStatistics(window.ergonRegistry.solutions);
        
    } catch (error) {
        console.error('Failed to load registry solutions:', error);
        displayError('Failed to load solutions. Please try again.');
    }
}

/**
 * Display solutions in the UI
 * @param {Array} solutions - Solutions to display
 */
function displaySolutions(solutions) {
    const container = document.getElementById('registry-solutions');
    if (!container) return;
    
    if (solutions.length === 0) {
        container.innerHTML = `
            <div class="ergon__empty-state">
                <p>No solutions found in Registry</p>
                <button onclick="checkCompletedProjects()" class="ergon__button">
                    Import from TektonCore
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = solutions.map(solution => `
        <div class="ergon__solution-card" data-solution-id="${solution.id}">
            <div class="ergon__solution-header">
                <h4 class="ergon__solution-name">${solution.name || 'Unnamed Solution'}</h4>
                <span class="ergon__solution-type ergon__type-${solution.type}">
                    ${solution.type}
                </span>
            </div>
            <div class="ergon__solution-meta">
                <span class="ergon__solution-version">v${solution.version || '1.0.0'}</span>
                <span class="ergon__solution-date">${formatDate(solution.created)}</span>
                ${solution.meets_standards ? 
                    '<span class="ergon__solution-badge ergon__badge-compliant">✓ Standards</span>' : 
                    '<span class="ergon__solution-badge ergon__badge-noncompliant">⚠ Non-compliant</span>'
                }
            </div>
            ${solution.content?.description ? 
                `<p class="ergon__solution-description">${solution.content.description}</p>` : 
                ''
            }
            <div class="ergon__solution-actions">
                <button class="ergon__button ergon__button--test" data-tekton-action="test-solution">Test</button>
                <button class="ergon__button ergon__button--view" data-tekton-action="view-details">Details</button>
                <button class="ergon__button ergon__button--check" data-tekton-action="check-standards">Check</button>
            </div>
        </div>
    `).join('');
}

/**
 * Update statistics display
 * @param {Array} solutions - Solutions array
 */
function updateStatistics(solutions) {
    const totalEl = document.getElementById('total-solutions');
    const compliantEl = document.getElementById('compliant-solutions');
    
    if (totalEl) {
        totalEl.textContent = `Total Solutions: ${solutions.length}`;
    }
    
    if (compliantEl) {
        const compliant = solutions.filter(s => s.meets_standards).length;
        compliantEl.textContent = `Standards Compliant: ${compliant}`;
    }
}

/**
 * Check for completed projects in TektonCore
 */
async function checkCompletedProjects() {
    const button = document.getElementById('check-completed-projects');
    if (button) {
        button.disabled = true;
        button.textContent = 'Checking...';
    }
    
    try {
        const response = await fetch('/api/ergon/registry/import-completed', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`Import failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.imported > 0) {
            displaySuccess(`Imported ${result.imported} solutions from TektonCore`);
            // Reload solutions
            await loadRegistrySolutions();
        } else {
            displayInfo('No new completed projects found');
        }
        
    } catch (error) {
        console.error('Failed to import projects:', error);
        displayError('Failed to import projects. Please try again.');
    } finally {
        if (button) {
            button.disabled = false;
            button.textContent = 'Check Completed Projects';
        }
    }
}

/**
 * View solution details
 * @param {string} solutionId - Solution ID
 */
async function viewSolutionDetails(solutionId) {
    try {
        const response = await fetch(`/api/ergon/registry/${solutionId}`);
        if (!response.ok) {
            throw new Error(`Failed to load details: ${response.statusText}`);
        }
        
        const solution = await response.json();
        
        // Display in modal or detail panel
        displaySolutionModal(solution);
        
    } catch (error) {
        console.error('Failed to load solution details:', error);
        displayError('Failed to load solution details');
    }
}

/**
 * Check solution standards compliance
 * @param {string} solutionId - Solution ID
 */
async function checkStandards(solutionId) {
    try {
        const response = await fetch(`/api/ergon/registry/${solutionId}/check-standards`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`Standards check failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Update card with results
        const card = document.querySelector(`[data-solution-id="${solutionId}"]`);
        if (card) {
            const badge = card.querySelector('.ergon__solution-badge');
            if (badge) {
                if (result.meets_standards) {
                    badge.className = 'ergon__solution-badge ergon__badge-compliant';
                    badge.textContent = '✓ Standards';
                } else {
                    badge.className = 'ergon__solution-badge ergon__badge-noncompliant';
                    badge.textContent = '⚠ Non-compliant';
                }
            }
        }
        
        // Show detailed results
        displayStandardsResults(result);
        
    } catch (error) {
        console.error('Failed to check standards:', error);
        displayError('Failed to check standards');
    }
}

/**
 * Display solution modal
 * @param {Object} solution - Solution data
 */
function displaySolutionModal(solution) {
    // Create modal HTML
    const modal = document.createElement('div');
    modal.className = 'ergon__modal';
    modal.innerHTML = `
        <div class="ergon__modal-content">
            <div class="ergon__modal-header">
                <h3>${solution.name || 'Solution Details'}</h3>
                <button onclick="this.closest('.ergon__modal').remove()" class="ergon__modal-close">×</button>
            </div>
            <div class="ergon__modal-body">
                <div class="ergon__detail-section">
                    <h4>Metadata</h4>
                    <dl>
                        <dt>ID:</dt><dd>${solution.id}</dd>
                        <dt>Type:</dt><dd>${solution.type}</dd>
                        <dt>Version:</dt><dd>${solution.version}</dd>
                        <dt>Created:</dt><dd>${formatDate(solution.created)}</dd>
                        <dt>Standards:</dt><dd>${solution.meets_standards ? '✓ Compliant' : '⚠ Non-compliant'}</dd>
                    </dl>
                </div>
                ${solution.source ? `
                <div class="ergon__detail-section">
                    <h4>Source</h4>
                    <dl>
                        <dt>Project:</dt><dd>${solution.source.project_id || 'N/A'}</dd>
                        <dt>Sprint:</dt><dd>${solution.source.sprint_id || 'N/A'}</dd>
                        <dt>Location:</dt><dd>${solution.source.location || 'N/A'}</dd>
                    </dl>
                </div>
                ` : ''}
                ${solution.content ? `
                <div class="ergon__detail-section">
                    <h4>Content</h4>
                    <pre class="ergon__code-block">${JSON.stringify(solution.content, null, 2)}</pre>
                </div>
                ` : ''}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

/**
 * Display standards check results
 * @param {Object} results - Standards check results
 */
function displayStandardsResults(results) {
    displayInfo(`Standards Check: ${results.meets_standards ? 'PASSED' : 'FAILED'} (Score: ${results.score}/100)`);
}

/**
 * Display error message
 * @param {string} message - Error message
 */
function displayError(message) {
    showNotification(message, 'error');
}

/**
 * Display success message
 * @param {string} message - Success message
 */
function displaySuccess(message) {
    showNotification(message, 'success');
}

/**
 * Display info message
 * @param {string} message - Info message
 */
function displayInfo(message) {
    showNotification(message, 'info');
}

/**
 * Show notification
 * @param {string} message - Message to show
 * @param {string} type - Notification type
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `ergon__notification ergon__notification--${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('ergon__notification--show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('ergon__notification--show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Format date for display
 * @param {string} dateStr - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString();
}

// Event handlers
document.addEventListener('DOMContentLoaded', () => {
    // Load solutions when Registry tab is selected
    const registryTab = document.getElementById('ergon-tab-registry');
    if (registryTab) {
        registryTab.addEventListener('change', (e) => {
            if (e.target.checked) {
                loadRegistrySolutions();
            }
        });
        
        // Load immediately if already selected
        if (registryTab.checked) {
            loadRegistrySolutions();
        }
    }
    
    // Handle button clicks
    document.addEventListener('click', (e) => {
        const action = e.target.dataset.tektonAction;
        if (!action) return;
        
        const card = e.target.closest('.ergon__solution-card');
        if (!card) return;
        
        const solutionId = card.dataset.solutionId;
        if (!solutionId) return;
        
        switch (action) {
            case 'view-details':
                viewSolutionDetails(solutionId);
                break;
            case 'check-standards':
                checkStandards(solutionId);
                break;
            // test-solution is handled by sandbox-integration.js
        }
    });
    
    // Handle Check Completed Projects button
    const checkButton = document.getElementById('check-completed-projects');
    if (checkButton) {
        checkButton.addEventListener('click', checkCompletedProjects);
    }
});

// Export for debugging
window.ergonRegistry.loadSolutions = loadRegistrySolutions;
window.ergonRegistry.checkProjects = checkCompletedProjects;