// Synthesis Component JavaScript
// Handles Planning Team Workflow UI functionality

console.log('[SYNTHESIS] Component script loading...');

// Define synthesisComponent immediately on window
window.synthesisComponent = window.synthesisComponent || {};

// Define the full component
window.synthesisComponent = {
    state: {
        activeTab: 'dashboard',
        sprints: [],
        currentSprint: null,
        validationInProgress: false
    },

    init: function() {
        console.log('[SYNTHESIS] Component initializing...');
        console.log('[SYNTHESIS] Current active tab:', this.state.activeTab);
        
        // Wait a moment for DOM to be ready
        setTimeout(() => {
            this.loadSprintsFromDailyLogs();
            this.setupEventListeners();
            console.log('[SYNTHESIS] Component initialized');
        }, 100);
    },

    loadSprintsFromDailyLogs: function() {
        console.log('[SYNTHESIS] Loading Ready-3:Synthesis sprints...');
        
        // Simulate loading sprints - in production this would scan DAILY_LOG.md files
        // For now, we'll add the test sprints we created
        const testSprints = [
            {
                id: 'test-synthesis-validation',
                name: 'Test Synthesis Validation',
                status: 'Ready-3:Synthesis',
                tasks: 8,
                hours: 32,
                description: 'Test sprint created to validate the Synthesis UI implementation.',
                components: ['Hermes', 'Engram', 'Athena', 'Synthesis'],
                path: 'Test_Synthesis_Validation_Sprint'
            },
            {
                id: 'ai-memory-enhancement',
                name: 'CI Memory Enhancement',
                status: 'Ready-3:Synthesis',
                tasks: 12,
                hours: 48,
                description: 'Enhance the Engram memory system with advanced semantic search capabilities.',
                components: ['Engram', 'Hermes', 'Sophia', 'Athena'],
                path: 'AI_Memory_Enhancement_Sprint'
            }
        ];

        this.state.sprints = testSprints;
        this.renderSprintCards();
    },

    renderSprintCards: function() {
        console.log('[SYNTHESIS] renderSprintCards called with', this.state.sprints.length, 'sprints');
        
        const sprintGrid = document.getElementById('sprint-grid');
        const noSprintsDiv = document.getElementById('no-sprints');
        
        console.log('[SYNTHESIS] Sprint grid element:', sprintGrid);
        console.log('[SYNTHESIS] No sprints div element:', noSprintsDiv);
        
        if (!sprintGrid) {
            console.error('[SYNTHESIS] Sprint grid not found - looking for element with id="sprint-grid"');
            // Try to find by class as backup
            const gridByClass = document.querySelector('.synthesis__sprint-grid');
            console.log('[SYNTHESIS] Sprint grid by class:', gridByClass);
            return;
        }

        if (this.state.sprints.length === 0) {
            // Show empty state
            if (noSprintsDiv) {
                noSprintsDiv.style.display = 'block';
            }
            sprintGrid.innerHTML = '';
            return;
        }

        // Hide empty state
        if (noSprintsDiv) {
            noSprintsDiv.style.display = 'none';
        }

        // Clear existing cards
        sprintGrid.innerHTML = '';

        // Render sprint cards
        this.state.sprints.forEach(sprint => {
            const card = this.createSprintCard(sprint);
            sprintGrid.appendChild(card);
        });

        console.log(`[SYNTHESIS] Rendered ${this.state.sprints.length} sprint cards`);
    },

    createSprintCard: function(sprint) {
        const card = document.createElement('div');
        card.className = 'synthesis__sprint-card';
        card.setAttribute('data-sprint-id', sprint.id);
        
        card.innerHTML = `
            <div class="synthesis__card-header">
                <span class="synthesis__sprint-name">${sprint.name}</span>
                <span class="synthesis__sprint-status synthesis__sprint-status--ready">${sprint.status}</span>
            </div>
            <div class="synthesis__card-body">
                <p class="synthesis__sprint-description">${sprint.description}</p>
                <div class="synthesis__sprint-meta">
                    <span class="synthesis__meta-item">
                        <span class="synthesis__meta-label">Tasks:</span>
                        <span class="synthesis__meta-value">${sprint.tasks}</span>
                    </span>
                    <span class="synthesis__meta-item">
                        <span class="synthesis__meta-label">Total Hours:</span>
                        <span class="synthesis__meta-value">${sprint.hours}</span>
                    </span>
                </div>
                <div class="synthesis__sprint-meta">
                    <span class="synthesis__meta-item">
                        <span class="synthesis__meta-label">Components:</span>
                        <span class="synthesis__meta-value">${sprint.components.join(', ')}</span>
                    </span>
                </div>
            </div>
            <div class="synthesis__card-actions">
                <button class="synthesis__button synthesis__button--view"
                        onclick="synthesisComponent.viewSprint('${sprint.id}')"
                        data-tekton-action="view-sprint" data-tekton-trigger="click">View</button>
                <button class="synthesis__button synthesis__button--validate"
                        onclick="synthesisComponent.beginValidation('${sprint.id}')"
                        data-tekton-action="validate-sprint" data-tekton-trigger="click">Validate</button>
                <button class="synthesis__button synthesis__button--secondary"
                        onclick="synthesisComponent.skipToReview('${sprint.id}')"
                        data-tekton-action="skip-to-review" data-tekton-trigger="click">Skip to Review</button>
            </div>
        `;
        
        return card;
    },

    viewSprint: function(sprintId) {
        console.log('[SYNTHESIS] View sprint:', sprintId);
        const sprint = this.state.sprints.find(s => s.id === sprintId);
        if (sprint) {
            this.state.currentSprint = sprint;
            // Switch to validation tab
            synthesis_switchTab('validation');
            this.populateValidationTab(sprint);
        }
    },

    beginValidation: function(sprintId) {
        console.log('[SYNTHESIS] Begin validation for sprint:', sprintId);
        const sprint = this.state.sprints.find(s => s.id === sprintId);
        if (sprint) {
            this.state.currentSprint = sprint;
            synthesis_switchTab('validation');
            this.populateValidationTab(sprint);
            // Auto-start validation
            setTimeout(() => {
                window.startValidation();
            }, 500);
        }
    },

    skipToReview: function(sprintId) {
        console.log('[SYNTHESIS] Skip to review for sprint:', sprintId);
        const sprint = this.state.sprints.find(s => s.id === sprintId);
        if (sprint) {
            this.state.currentSprint = sprint;
            synthesis_switchTab('review');
            this.populateReviewTab(sprint);
        }
    },

    populateValidationTab: function(sprint) {
        // Populate validation sprint select
        const validationSelect = document.getElementById('validation-sprint-select');
        if (validationSelect) {
            validationSelect.innerHTML = `
                <option value="">Select sprint to validate...</option>
                <option value="${sprint.id}" selected>${sprint.name}</option>
            `;
            
            // Add other sprints as options
            this.state.sprints.forEach(s => {
                if (s.id !== sprint.id) {
                    const option = document.createElement('option');
                    option.value = s.id;
                    option.textContent = s.name;
                    validationSelect.appendChild(option);
                }
            });
        }
    },

    populateReviewTab: function(sprint) {
        // Populate review sprint select
        const reviewSelect = document.getElementById('review-sprint-select');
        if (reviewSelect) {
            reviewSelect.innerHTML = `
                <option value="">Select validated sprint...</option>
                <option value="${sprint.id}" selected>${sprint.name}</option>
            `;
        }
        
        // Update validation summary
        const summaryDiv = document.getElementById('validation-summary');
        if (summaryDiv) {
            summaryDiv.innerHTML = `
                <div class="synthesis__summary-item">
                    <strong>Sprint:</strong> ${sprint.name}
                </div>
                <div class="synthesis__summary-item">
                    <strong>Tasks:</strong> ${sprint.tasks} tasks (${sprint.hours} hours)
                </div>
                <div class="synthesis__summary-item">
                    <strong>Components:</strong> ${sprint.components.join(', ')}
                </div>
                <div class="synthesis__summary-item">
                    <strong>Status:</strong> Ready for review (validation skipped)
                </div>
            `;
        }
    },

    loadTabContent: function(tabId) {
        console.log('[SYNTHESIS] Loading content for tab:', tabId);
        
        switch (tabId) {
            case 'dashboard':
                this.loadSprintsFromDailyLogs();
                break;
            case 'results':
                this.loadValidationResults();
                break;
            case 'integration':
                this.loadIntegrationStatus();
                break;
        }
    },

    loadValidationResults: function() {
        console.log('[SYNTHESIS] Loading validation results...');
        // TODO: Load actual validation results
    },

    loadIntegrationStatus: function() {
        console.log('[SYNTHESIS] Loading integration status...');
        // TODO: Load actual integration status
    },

    updateChatPlaceholder: function(tabId) {
        const chatInput = document.getElementById('synthesis-chat-input');
        if (!chatInput) return;
        
        if (tabId === 'workflowchat') {
            chatInput.placeholder = 'Ask about validation testing, dry-run execution, or requirements coverage...';
        } else if (tabId === 'teamchat') {
            chatInput.placeholder = 'Enter team chat message...';
        } else {
            chatInput.placeholder = 'Enter validation questions, testing commands, or chat messages';
        }
    },

    setupEventListeners: function() {
        // Validation mode change
        const modeRadios = document.querySelectorAll('input[name="validation-mode"]');
        modeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                console.log('[SYNTHESIS] Validation mode changed to:', e.target.value);
            });
        });

        // Sprint select changes
        const validationSelect = document.getElementById('validation-sprint-select');
        if (validationSelect) {
            validationSelect.addEventListener('change', (e) => {
                const sprintId = e.target.value;
                if (sprintId) {
                    const sprint = this.state.sprints.find(s => s.id === sprintId);
                    if (sprint) {
                        this.state.currentSprint = sprint;
                        console.log('[SYNTHESIS] Selected sprint:', sprint.name);
                    }
                }
            });
        }
    },

    saveComponentState: function() {
        console.log('[SYNTHESIS] Saving component state...');
        // TODO: Implement state persistence
    }
};

// Override global validation functions with actual implementations
window.startValidation = function() {
    console.log('[SYNTHESIS] Starting validation...');
    const progressDiv = document.getElementById('validation-progress');
    if (progressDiv) {
        progressDiv.style.display = 'block';
    }
    
    const startBtn = document.getElementById('start-validation-btn');
    const stopBtn = document.getElementById('stop-validation-btn');
    if (startBtn) startBtn.style.display = 'none';
    if (stopBtn) stopBtn.style.display = 'block';
    
    synthesisComponent.state.validationInProgress = true;
    
    // TODO: Implement actual validation logic
    console.log('[SYNTHESIS] Validation started for sprint:', synthesisComponent.state.currentSprint?.name);
};

window.stopValidation = function() {
    console.log('[SYNTHESIS] Stopping validation...');
    const startBtn = document.getElementById('start-validation-btn');
    const stopBtn = document.getElementById('stop-validation-btn');
    if (startBtn) startBtn.style.display = 'block';
    if (stopBtn) stopBtn.style.display = 'none';
    
    synthesisComponent.state.validationInProgress = false;
};

// Make sure the component is accessible
window.synthesisComponent = synthesisComponent;

// Add manual debug trigger
window.debugSynthesisCards = function() {
    console.log('[SYNTHESIS DEBUG] Manual card render triggered');
    console.log('[SYNTHESIS DEBUG] Component exists:', !!window.synthesisComponent);
    console.log('[SYNTHESIS DEBUG] Sprint count:', window.synthesisComponent?.state?.sprints?.length);
    
    if (window.synthesisComponent) {
        window.synthesisComponent.loadSprintsFromDailyLogs();
    } else {
        console.error('[SYNTHESIS DEBUG] Component not found!');
    }
};

console.log('[SYNTHESIS] Component script loaded. Use debugSynthesisCards() to manually trigger sprint loading.');
console.log('[SYNTHESIS] synthesisComponent.init exists:', typeof window.synthesisComponent?.init);

// Also try to call init immediately if the DOM is ready
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('[SYNTHESIS] DOM already ready, attempting immediate init...');
    if (window.synthesisComponent && typeof window.synthesisComponent.init === 'function') {
        try {
            window.synthesisComponent.init();
        } catch (e) {
            console.error('[SYNTHESIS] Error during immediate init:', e);
        }
    }
}