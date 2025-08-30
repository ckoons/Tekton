/**
 * Apollo Preparation System - JavaScript
 * Handles Context Brief preparation, CI Registry, and Cognitive Guidance
 */

class ApolloPreparation {
    constructor() {
        this.baseUrl = window.TektonConfig ? 
            window.TektonConfig.getApolloUrl('/api/preparation') : 
            'http://localhost:8112/api/preparation';
        
        this.currentBrief = null;
        this.memoryRhythm = {
            state: 'idle',
            shortTermCounter: 0,
            mediumTermCounter: 0,
            lastUpdate: Date.now()
        };
        
        this.ciRegistry = [];
        this.innerVoicePrompts = [];
    }

    /**
     * Initialize the preparation system
     */
    async init() {
        console.log('[Apollo] Initializing Preparation system...');
        
        // Load CI Registry
        await this.loadCIRegistry();
        
        // Bind event handlers
        this.bindEventHandlers();
        
        // Load saved briefs
        await this.loadSavedBriefs();
        
        // Start memory rhythm
        this.startMemoryRhythm();
    }

    /**
     * Load CI Registry from Apollo
     */
    async loadCIRegistry() {
        try {
            // Get registry URL from TektonConfig
            const registryUrl = window.TektonConfig ? 
                window.TektonConfig.getApolloUrl('/api/ci-registry') : 
                'http://localhost:8112/api/ci-registry';
            
            const response = await fetch(registryUrl);
            if (!response.ok) {
                console.warn('[Apollo] CI Registry not available, using defaults');
                this.useDefaultRegistry();
                return;
            }
            
            const data = await response.json();
            this.ciRegistry = data.cis || [];
            
            // Populate CI selectors
            this.populateCISelectors();
            
        } catch (error) {
            console.error('[Apollo] Failed to load CI Registry:', error);
            this.useDefaultRegistry();
        }
    }

    /**
     * Use default CI registry if API unavailable
     */
    useDefaultRegistry() {
        this.ciRegistry = [
            // Core Specialist CIs
            { id: 'ergon-ci', name: 'Ergon', type: 'specialist', role: 'Task Manager' },
            { id: 'rhetor-ci', name: 'Rhetor', type: 'specialist', role: 'Orchestrator' },
            { id: 'noesis-ci', name: 'Noesis', type: 'specialist', role: 'Understanding' },
            { id: 'athena-ci', name: 'Athena', type: 'specialist', role: 'Knowledge Graph' },
            { id: 'hermes-ci', name: 'Hermes', type: 'specialist', role: 'Communication' },
            { id: 'sophia-ci', name: 'Sophia', type: 'specialist', role: 'Wisdom & Guidance' },
            { id: 'apollo-ci', name: 'Apollo', type: 'specialist', role: 'Preparation & Memory' },
            { id: 'hephaestus-ci', name: 'Hephaestus', type: 'specialist', role: 'UI Builder' },
            { id: 'terma-ci', name: 'Terma', type: 'specialist', role: 'Contracts' },
            { id: 'neurosyne-ci', name: 'NeuroSyne', type: 'specialist', role: 'Cognitive Architecture' },
            
            // Worker CIs
            { id: 'worker-1', name: 'Worker 1', type: 'worker', role: 'General Worker' },
            { id: 'worker-2', name: 'Worker 2', type: 'worker', role: 'General Worker' },
            { id: 'worker-3', name: 'Worker 3', type: 'worker', role: 'General Worker' },
            { id: 'specialist-worker', name: 'Specialist Worker', type: 'worker', role: 'Specialist Tasks' },
            
            // Terminal CIs
            { id: 'terminal-ergon', name: 'Terminal Ergon', type: 'terminal', role: 'Task Terminal' },
            { id: 'terminal-rhetor', name: 'Terminal Rhetor', type: 'terminal', role: 'Orchestration Terminal' },
            { id: 'terminal-noesis', name: 'Terminal Noesis', type: 'terminal', role: 'Understanding Terminal' },
            { id: 'terminal-athena', name: 'Terminal Athena', type: 'terminal', role: 'Knowledge Terminal' },
            { id: 'terminal-hermes', name: 'Terminal Hermes', type: 'terminal', role: 'Communication Terminal' },
            { id: 'terminal-sophia', name: 'Terminal Sophia', type: 'terminal', role: 'Wisdom Terminal' },
            { id: 'terminal-apollo', name: 'Terminal Apollo', type: 'terminal', role: 'Preparation Terminal' },
            { id: 'terminal-hephaestus', name: 'Terminal Hephaestus', type: 'terminal', role: 'UI Terminal' },
            
            // Project CIs
            { id: 'project-alpha', name: 'Project Alpha', type: 'project', role: 'Alpha Development' },
            { id: 'project-beta', name: 'Project Beta', type: 'project', role: 'Beta Testing' },
            { id: 'project-gamma', name: 'Project Gamma', type: 'project', role: 'Gamma Research' },
            { id: 'project-delta', name: 'Project Delta', type: 'project', role: 'Delta Integration' }
        ];
        
        this.populateCISelectors();
    }

    /**
     * Populate CI selector dropdowns
     */
    populateCISelectors() {
        const selectors = ['apollo-ci-selector', 'apollo-target-ci'];
        
        selectors.forEach(selectorId => {
            const selector = document.getElementById(selectorId);
            if (!selector) return;
            
            // Clear existing options
            selector.innerHTML = '<option value="">Select CI...</option>';
            
            // Group CIs by type
            const groups = {
                specialist: [],
                terminal: [],
                project: []
            };
            
            this.ciRegistry.forEach(ci => {
                const type = ci.type || 'specialist';
                if (!groups[type]) groups[type] = [];
                groups[type].push(ci);
            });
            
            // Add grouped options
            Object.entries(groups).forEach(([type, cis]) => {
                if (cis.length === 0) return;
                
                const optgroup = document.createElement('optgroup');
                optgroup.label = type.charAt(0).toUpperCase() + type.slice(1) + 's';
                
                cis.forEach(ci => {
                    const option = document.createElement('option');
                    option.value = ci.id;
                    option.textContent = `${ci.name} (${ci.role})`;
                    option.setAttribute('data-ci-type', ci.type);
                    option.setAttribute('data-ci-role', ci.role);
                    optgroup.appendChild(option);
                });
                
                selector.appendChild(optgroup);
            });
        });
    }

    /**
     * Bind event handlers
     */
    bindEventHandlers() {
        // Generate Brief button
        const generateBtn = document.getElementById('apollo-generate-brief');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateBrief());
        }
        
        // Add Prompt button
        const addPromptBtn = document.getElementById('apollo-add-prompt');
        if (addPromptBtn) {
            addPromptBtn.addEventListener('click', () => this.addPrompt());
        }
        
        // Save/Load/Delete Brief buttons
        const saveBriefBtn = document.getElementById('apollo-save-brief');
        if (saveBriefBtn) {
            saveBriefBtn.addEventListener('click', () => this.saveBrief());
        }
        
        const loadBriefBtn = document.getElementById('apollo-load-brief');
        if (loadBriefBtn) {
            loadBriefBtn.addEventListener('click', () => this.loadBrief());
        }
        
        const deleteBriefBtn = document.getElementById('apollo-delete-brief');
        if (deleteBriefBtn) {
            deleteBriefBtn.addEventListener('click', () => this.deleteBrief());
        }
        
        // Template selector
        const templateSelector = document.getElementById('apollo-template-selector');
        if (templateSelector) {
            templateSelector.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.loadTemplate(e.target.value);
                }
            });
        }
        
        // Memory workflow checkboxes
        const workflowCheckboxes = document.querySelectorAll('.apollo-memory-workflow input[type="checkbox"]');
        workflowCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateMemoryRhythm());
        });
    }

    /**
     * Generate Context Brief
     */
    async generateBrief() {
        const ciSource = document.getElementById('apollo-ci-selector').value;
        const targetCI = document.getElementById('apollo-target-ci').value;
        const taskContext = document.getElementById('apollo-task-context').value;
        const nextSteps = document.getElementById('apollo-next-steps').value;
        
        if (!ciSource || !targetCI) {
            this.showMessage('Please select both source and target CIs', 'warning');
            return;
        }
        
        // Gather memory workflow settings
        const memoryWorkflow = {
            shortTerm: document.getElementById('apollo-short-term').checked,
            mediumTerm: document.getElementById('apollo-medium-term').checked,
            longTerm: document.getElementById('apollo-long-term').checked,
            latentSpace: document.getElementById('apollo-latent-space').checked
        };
        
        // Create cognitive guidance package
        const guidancePackage = {
            source_ci: ciSource,
            target_ci: targetCI,
            task_context: taskContext,
            next_steps: nextSteps,
            memory_workflow: memoryWorkflow,
            inner_voice_prompts: this.innerVoicePrompts,
            timestamp: new Date().toISOString()
        };
        
        try {
            const response = await fetch(`${this.baseUrl}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(guidancePackage)
            });
            
            if (!response.ok) throw new Error('Failed to generate brief');
            
            const brief = await response.json();
            this.currentBrief = brief;
            
            // Display the brief
            this.displayBrief(brief);
            
            // Update memory rhythm
            this.updateMemoryRhythm();
            
            this.showMessage('Context Brief generated successfully', 'success');
            
        } catch (error) {
            console.error('[Apollo] Failed to generate brief:', error);
            this.showMessage('Failed to generate Context Brief', 'error');
        }
    }

    /**
     * Display generated brief
     */
    displayBrief(brief) {
        const preview = document.getElementById('apollo-brief-preview');
        if (!preview) return;
        
        const formatMemories = (memories) => {
            if (!memories || memories.length === 0) return '<p>No memories found</p>';
            
            return memories.map(mem => `
                <div class="apollo-memory-item" data-memory-type="${mem.type}">
                    <span class="apollo-memory-type apollo-memory-type--${mem.type}">${mem.type}</span>
                    <div class="apollo-memory-content">${mem.content}</div>
                    <div class="apollo-memory-meta">
                        ${mem.tags ? mem.tags.map(tag => `<span class="apollo-tag">${tag}</span>`).join('') : ''}
                        <span class="apollo-timestamp">${this.formatTimestamp(mem.timestamp)}</span>
                    </div>
                </div>
            `).join('');
        };
        
        const formatPrompts = (prompts) => {
            if (!prompts || prompts.length === 0) return '';
            
            return `
                <div class="apollo-inner-voice">
                    <h4>Inner Voice Prompts</h4>
                    ${prompts.map(prompt => `
                        <div class="apollo-prompt">${prompt}</div>
                    `).join('')}
                </div>
            `;
        };
        
        preview.innerHTML = `
            <div class="apollo-brief-header">
                <h3>Context Brief: ${brief.id || 'New Brief'}</h3>
                <div class="apollo-brief-meta">
                    <span>For: ${brief.target_ci}</span>
                    <span>From: ${brief.source_ci}</span>
                    <span>Tokens: ${brief.token_count || 0}</span>
                </div>
            </div>
            
            <div class="apollo-brief-content">
                ${brief.task_context ? `
                    <div class="apollo-task-section">
                        <h4>Task Context</h4>
                        <p>${brief.task_context}</p>
                        ${brief.next_steps ? `<p><strong>Next Steps:</strong> ${brief.next_steps}</p>` : ''}
                    </div>
                ` : ''}
                
                <div class="apollo-memories-section">
                    <h4>Relevant Memories</h4>
                    ${formatMemories(brief.memories)}
                </div>
                
                ${formatPrompts(brief.inner_voice_prompts)}
                
                ${brief.cognitive_instructions ? `
                    <div class="apollo-instructions">
                        <h4>Cognitive Instructions</h4>
                        <p>${brief.cognitive_instructions}</p>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Enable save button
        const saveBtn = document.getElementById('apollo-save-brief');
        if (saveBtn) saveBtn.disabled = false;
    }

    /**
     * Add inner voice prompt
     */
    addPrompt() {
        const promptInput = document.getElementById('apollo-prompt-input');
        if (!promptInput || !promptInput.value.trim()) return;
        
        const prompt = promptInput.value.trim();
        this.innerVoicePrompts.push(prompt);
        
        // Update prompts list
        const promptsList = document.getElementById('apollo-prompts-list');
        if (promptsList) {
            const promptItem = document.createElement('div');
            promptItem.className = 'apollo-prompt-item';
            promptItem.innerHTML = `
                <span>${prompt}</span>
                <button onclick="apolloPreparation.removePrompt(${this.innerVoicePrompts.length - 1})" 
                        class="apollo-button apollo-button--small">Remove</button>
            `;
            promptsList.appendChild(promptItem);
        }
        
        // Clear input
        promptInput.value = '';
        
        this.showMessage('Prompt added', 'success');
    }

    /**
     * Remove inner voice prompt
     */
    removePrompt(index) {
        this.innerVoicePrompts.splice(index, 1);
        this.updatePromptsList();
    }
    
    /**
     * Update the prompts list display
     */
    updatePromptsList() {
        const promptsList = document.getElementById('apollo-prompts-list');
        if (!promptsList) return;
        
        promptsList.innerHTML = '';
        this.innerVoicePrompts.forEach((prompt, i) => {
            const promptItem = document.createElement('div');
            promptItem.className = 'apollo-prompt-item';
            promptItem.innerHTML = `
                <span>${prompt}</span>
                <button onclick="apolloPreparation.removePrompt(${i})" 
                        class="apollo-button apollo-button--small">Remove</button>
            `;
            promptsList.appendChild(promptItem);
        });
    }

    /**
     * Save current brief
     */
    async saveBrief() {
        if (!this.currentBrief) {
            this.showMessage('No brief to save', 'warning');
            return;
        }
        
        const briefName = prompt('Enter a name for this brief:');
        if (!briefName) return;
        
        try {
            const response = await fetch(`${this.baseUrl}/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: briefName,
                    brief: this.currentBrief
                })
            });
            
            if (!response.ok) throw new Error('Failed to save brief');
            
            this.showMessage('Brief saved successfully', 'success');
            await this.loadSavedBriefs();
            
        } catch (error) {
            console.error('[Apollo] Failed to save brief:', error);
            this.showMessage('Failed to save brief', 'error');
        }
    }

    /**
     * Load saved briefs
     */
    async loadSavedBriefs() {
        try {
            const response = await fetch(`${this.baseUrl}/saved`);
            if (!response.ok) return;
            
            const briefs = await response.json();
            
            const selector = document.getElementById('apollo-saved-briefs');
            if (selector) {
                selector.innerHTML = '<option value="">Select saved brief...</option>';
                briefs.forEach(brief => {
                    const option = document.createElement('option');
                    option.value = brief.id;
                    option.textContent = `${brief.name} (${this.formatTimestamp(brief.created)})`;
                    selector.appendChild(option);
                });
            }
            
        } catch (error) {
            console.error('[Apollo] Failed to load saved briefs:', error);
        }
    }

    /**
     * Load selected brief
     */
    async loadBrief() {
        const selector = document.getElementById('apollo-saved-briefs');
        if (!selector || !selector.value) {
            this.showMessage('Please select a brief to load', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`${this.baseUrl}/saved/${selector.value}`);
            if (!response.ok) throw new Error('Failed to load brief');
            
            const brief = await response.json();
            this.currentBrief = brief;
            this.displayBrief(brief);
            
            this.showMessage('Brief loaded successfully', 'success');
            
        } catch (error) {
            console.error('[Apollo] Failed to load brief:', error);
            this.showMessage('Failed to load brief', 'error');
        }
    }

    /**
     * Delete selected brief
     */
    async deleteBrief() {
        const selector = document.getElementById('apollo-saved-briefs');
        if (!selector || !selector.value) {
            this.showMessage('Please select a brief to delete', 'warning');
            return;
        }
        
        if (!confirm('Are you sure you want to delete this brief?')) return;
        
        try {
            const response = await fetch(`${this.baseUrl}/saved/${selector.value}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('Failed to delete brief');
            
            this.showMessage('Brief deleted successfully', 'success');
            await this.loadSavedBriefs();
            
        } catch (error) {
            console.error('[Apollo] Failed to delete brief:', error);
            this.showMessage('Failed to delete brief', 'error');
        }
    }

    /**
     * Load cognitive workflow template
     */
    loadTemplate(templateName) {
        const templates = {
            'task-start': {
                taskContext: 'Starting new task: [TASK_NAME]',
                nextSteps: 'Understand requirements, gather context, plan approach',
                workflow: { shortTerm: true, mediumTerm: false, longTerm: false, latentSpace: false },
                prompts: [
                    'Remember to check existing code patterns',
                    'Consider edge cases and error handling'
                ]
            },
            'debugging': {
                taskContext: 'Debugging issue: [ISSUE_DESCRIPTION]',
                nextSteps: 'Reproduce issue, identify root cause, implement fix, test',
                workflow: { shortTerm: true, mediumTerm: true, longTerm: false, latentSpace: false },
                prompts: [
                    'Check recent changes that might have caused this',
                    'Look for similar past issues and their solutions'
                ]
            },
            'code-review': {
                taskContext: 'Reviewing code for: [FEATURE_NAME]',
                nextSteps: 'Check standards compliance, test coverage, documentation',
                workflow: { shortTerm: false, mediumTerm: true, longTerm: true, latentSpace: false },
                prompts: [
                    'Verify code follows project conventions',
                    'Ensure adequate test coverage'
                ]
            },
            'phase-completion': {
                taskContext: 'Completing phase: [PHASE_NAME]',
                nextSteps: 'Document decisions, update long-term memory, prepare for next phase',
                workflow: { shortTerm: false, mediumTerm: false, longTerm: true, latentSpace: true },
                prompts: [
                    'Document key decisions and learnings',
                    'Update project knowledge base'
                ]
            }
        };
        
        const template = templates[templateName];
        if (!template) return;
        
        // Apply template values
        document.getElementById('apollo-task-context').value = template.taskContext;
        document.getElementById('apollo-next-steps').value = template.nextSteps;
        
        // Set workflow checkboxes
        document.getElementById('apollo-short-term').checked = template.workflow.shortTerm;
        document.getElementById('apollo-medium-term').checked = template.workflow.mediumTerm;
        document.getElementById('apollo-long-term').checked = template.workflow.longTerm;
        document.getElementById('apollo-latent-space').checked = template.workflow.latentSpace;
        
        // Add template prompts
        this.innerVoicePrompts = [...template.prompts];
        const promptsList = document.getElementById('apollo-prompts-list');
        if (promptsList) {
            promptsList.innerHTML = '';
            this.innerVoicePrompts.forEach((prompt, i) => {
                const promptItem = document.createElement('div');
                promptItem.className = 'apollo-prompt-item';
                promptItem.innerHTML = `
                    <span>${prompt}</span>
                    <button onclick="apolloPreparation.removePrompt(${i})" 
                            class="apollo-button apollo-button--small">Remove</button>
                `;
                promptsList.appendChild(promptItem);
            });
        }
        
        this.updateMemoryRhythm();
        this.showMessage(`Template "${templateName}" loaded`, 'success');
    }

    /**
     * Start memory rhythm monitoring
     */
    startMemoryRhythm() {
        // Update rhythm indicator every second
        setInterval(() => {
            const now = Date.now();
            const elapsed = (now - this.memoryRhythm.lastUpdate) / 1000; // seconds
            
            // Check if any workflow is active
            const shortTerm = document.getElementById('apollo-short-term')?.checked;
            const mediumTerm = document.getElementById('apollo-medium-term')?.checked;
            const longTerm = document.getElementById('apollo-long-term')?.checked;
            
            // Update state based on active workflows
            if (shortTerm && this.memoryRhythm.shortTermCounter > 5) {
                this.memoryRhythm.state = 'update-needed';
                this.pulseRhythmIndicator('Short-term memory update recommended');
            } else if (mediumTerm && this.memoryRhythm.mediumTermCounter > 20) {
                this.memoryRhythm.state = 'update-needed';
                this.pulseRhythmIndicator('Medium-term memory consolidation needed');
            } else if (longTerm && elapsed > 300) { // 5 minutes
                this.memoryRhythm.state = 'phase-complete';
                this.pulseRhythmIndicator('Consider long-term memory update');
            }
            
            // Increment counters
            this.memoryRhythm.shortTermCounter++;
            this.memoryRhythm.mediumTermCounter++;
            
        }, 1000);
    }

    /**
     * Update memory rhythm state
     */
    updateMemoryRhythm() {
        const indicator = document.querySelector('.apollo-rhythm-indicator');
        if (!indicator) return;
        
        const shortTerm = document.getElementById('apollo-short-term')?.checked;
        const mediumTerm = document.getElementById('apollo-medium-term')?.checked;
        const longTerm = document.getElementById('apollo-long-term')?.checked;
        const latentSpace = document.getElementById('apollo-latent-space')?.checked;
        
        // Determine rhythm state
        if (shortTerm || mediumTerm) {
            this.memoryRhythm.state = 'active';
            indicator.setAttribute('data-rhythm-state', 'active');
        } else if (longTerm) {
            this.memoryRhythm.state = 'monitoring';
            indicator.setAttribute('data-rhythm-state', 'monitoring');
        } else {
            this.memoryRhythm.state = 'idle';
            indicator.setAttribute('data-rhythm-state', 'idle');
        }
        
        // Reset counters when workflow changes
        this.memoryRhythm.shortTermCounter = 0;
        this.memoryRhythm.mediumTermCounter = 0;
        this.memoryRhythm.lastUpdate = Date.now();
    }

    /**
     * Pulse rhythm indicator with message
     */
    pulseRhythmIndicator(message) {
        const indicator = document.querySelector('.apollo-rhythm-indicator');
        if (!indicator) return;
        
        indicator.classList.add('apollo-rhythm-pulse');
        indicator.title = message;
        
        setTimeout(() => {
            indicator.classList.remove('apollo-rhythm-pulse');
        }, 2000);
    }

    /**
     * Show status message
     */
    showMessage(message, type = 'info') {
        const container = document.getElementById('apollo-message-container');
        if (!container) return;
        
        const messageEl = document.createElement('div');
        messageEl.className = `apollo-message apollo-message--${type}`;
        messageEl.textContent = message;
        
        container.appendChild(messageEl);
        
        setTimeout(() => {
            messageEl.remove();
        }, 3000);
    }

    /**
     * Format timestamp for display
     */
    formatTimestamp(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleString();
    }
}

// Initialize when DOM is ready
let apolloPreparation;

// Global function for HTML onclick handlers
function apollo_addPrompt(type) {
    if (!apolloPreparation) return;
    
    const prompts = {
        'check_pattern': 'Remember to check existing code patterns and conventions',
        'note_learning': 'This insight might be valuable for future tasks',
        'recall_similar': 'Consider if we\'ve solved similar problems before',
        'consolidate': 'Time to consolidate recent learnings into medium-term memory',
        'collaborate': 'Share this context with other CIs who might benefit',
        'custom': ''
    };
    
    const promptText = prompts[type] || type;
    
    if (type === 'custom') {
        const input = document.getElementById('apollo-prompt-input');
        if (input && input.value.trim()) {
            apolloPreparation.innerVoicePrompts.push(input.value.trim());
            apolloPreparation.updatePromptsList();
            input.value = '';
        }
    } else if (promptText) {
        apolloPreparation.innerVoicePrompts.push(promptText);
        apolloPreparation.updatePromptsList();
    }
    
    apolloPreparation.showMessage(`Added prompt: "${promptText}"`, 'success');
}

document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're on Apollo component with Preparation tab active
    const preparationPanel = document.getElementById('apollo-preparation-panel');
    if (preparationPanel) {
        apolloPreparation = new ApolloPreparation();
        
        // Initialize when Preparation tab is clicked
        const preparationTab = document.querySelector('label[for="apollo-tab-preparation"]');
        if (preparationTab) {
            preparationTab.addEventListener('click', () => {
                setTimeout(() => {
                    if (!apolloPreparation.ciRegistry.length) {
                        apolloPreparation.init();
                    }
                }, 100);
            });
        }
        
        console.log('[Apollo] Preparation system ready');
    }
});