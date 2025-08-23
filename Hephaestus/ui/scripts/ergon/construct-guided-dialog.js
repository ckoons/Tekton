/**
 * Guided Dialog System for Ergon Construct
 * 
 * Progressive questionnaire that intelligently fills from user responses
 */

window.ConstructDialog = {
    // Question definitions
    questions: [
        {
            id: 'purpose',
            question: 'What do you want to build?',
            placeholder: 'Describe the solution you need...',
            required: true,
            parseKeys: ['purpose', 'goal', 'objective']
        },
        {
            id: 'components',
            question: 'Which Registry components should we use?',
            placeholder: 'List components or let me suggest based on your purpose...',
            required: false,
            parseKeys: ['components', 'services', 'modules']
        },
        {
            id: 'dataflow',
            question: 'How should data flow through the system?',
            placeholder: 'Describe inputs, processing, and outputs...',
            required: false,
            parseKeys: ['data', 'flow', 'pipeline', 'connections']
        },
        {
            id: 'constraints',
            question: 'Any specific constraints or requirements?',
            placeholder: 'Performance, security, resource limits...',
            required: false,
            parseKeys: ['constraints', 'requirements', 'limits', 'performance']
        },
        {
            id: 'testing',
            question: 'What test scenarios should we verify?',
            placeholder: 'Describe test cases or accept defaults...',
            required: false,
            parseKeys: ['test', 'verify', 'validate', 'scenarios']
        }
    ],
    
    // Current state
    currentQuestionIndex: 0,
    responses: {},
    workspace: {},
    
    /**
     * Initialize the guided dialog
     */
    init() {
        console.log('[CONSTRUCT-DIALOG] Initializing guided dialog');
        
        // Reset state
        this.currentQuestionIndex = 0;
        this.responses = {};
        this.workspace = {
            components: [],
            connections: [],
            constraints: {},
            metadata: {}
        };
        
        // Render question list
        this.renderQuestionList();
        
        // Show first question
        this.showQuestion(0);
        
        // Set up event handlers
        this.setupEventHandlers();
    },
    
    /**
     * Render the full question list (grayed out future questions)
     */
    renderQuestionList() {
        const container = document.getElementById('construct-question-list');
        if (!container) return;
        
        let html = '<div class="construct-dialog__questions">';
        
        this.questions.forEach((q, index) => {
            const status = index < this.currentQuestionIndex ? 'answered' : 
                          index === this.currentQuestionIndex ? 'current' : 'pending';
            
            html += `
                <div class="construct-dialog__question-item construct-dialog__question-item--${status}" 
                     data-question-index="${index}">
                    <div class="construct-dialog__question-number">${index + 1}</div>
                    <div class="construct-dialog__question-text">
                        ${q.question}
                        ${this.responses[q.id] ? `<div class="construct-dialog__response">${this.responses[q.id]}</div>` : ''}
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    },
    
    /**
     * Show a specific question
     */
    showQuestion(index) {
        if (index < 0 || index >= this.questions.length) return;
        
        this.currentQuestionIndex = index;
        const question = this.questions[index];
        
        // Update current question display
        const display = document.getElementById('construct-current-question');
        if (display) {
            display.innerHTML = `
                <div class="construct-dialog__current">
                    <h4>${question.question}</h4>
                    <div class="construct-dialog__hint">${question.placeholder}</div>
                </div>
            `;
        }
        
        // Update button states
        this.updateButtons();
        
        // Re-render question list to update highlighting
        this.renderQuestionList();
        
        // Focus footer input
        const input = document.getElementById('ergon-chat-input');
        if (input) {
            input.placeholder = question.placeholder;
            input.focus();
        }
    },
    
    /**
     * Process user response from chat input
     */
    processResponse(message) {
        console.log('[CONSTRUCT-DIALOG] Processing response:', message);
        
        const question = this.questions[this.currentQuestionIndex];
        
        // Store response
        this.responses[question.id] = message;
        
        // Parse response for multiple fields
        this.parseAndFillWorkspace(message);
        
        // Update workspace display
        this.updateWorkspaceDisplay();
        
        // Move to next question if not at end
        if (this.currentQuestionIndex < this.questions.length - 1) {
            this.showQuestion(this.currentQuestionIndex + 1);
        } else {
            // All questions answered, enable Build
            this.enableBuild();
        }
    },
    
    /**
     * Parse long responses and fill multiple fields
     */
    parseAndFillWorkspace(message) {
        const lowerMessage = message.toLowerCase();
        
        // Try to extract component mentions
        const componentPatterns = [
            /using\s+(\w+(?:\s+and\s+\w+)*)/gi,
            /with\s+(\w+(?:\s+and\s+\w+)*)/gi,
            /components?:\s*([^.]+)/gi
        ];
        
        componentPatterns.forEach(pattern => {
            const matches = [...message.matchAll(pattern)];
            matches.forEach(match => {
                const components = match[1].split(/\s+and\s+|\s*,\s*/);
                components.forEach(comp => {
                    if (comp && !this.workspace.components.find(c => c.alias === comp)) {
                        this.workspace.components.push({
                            alias: comp.trim(),
                            registry_id: `${comp.trim().toLowerCase()}-pending`
                        });
                    }
                });
            });
        });
        
        // Extract connections
        const connectionPatterns = [
            /(\w+)\s+(?:to|->|→)\s+(\w+)/gi,
            /connect\s+(\w+)\s+to\s+(\w+)/gi
        ];
        
        connectionPatterns.forEach(pattern => {
            const matches = [...message.matchAll(pattern)];
            matches.forEach(match => {
                this.workspace.connections.push({
                    from: `${match[1]}.output`,
                    to: `${match[2]}.input`
                });
            });
        });
        
        // Extract constraints
        if (/\d+\s*(?:gb|mb|g|m)/i.test(message)) {
            const memMatch = message.match(/(\d+)\s*(gb|mb|g|m)/i);
            if (memMatch) {
                this.workspace.constraints.memory = `${memMatch[1]}${memMatch[2].toUpperCase()}`;
            }
        }
        
        if (/\d+\s*(?:second|minute|hour)/i.test(message)) {
            const timeMatch = message.match(/(\d+)\s*(second|minute|hour)/i);
            if (timeMatch) {
                this.workspace.constraints.timeout = parseInt(timeMatch[1]);
            }
        }
    },
    
    /**
     * Update workspace JSON display
     */
    updateWorkspaceDisplay() {
        const display = document.getElementById('construct-workspace-json');
        if (display) {
            display.textContent = JSON.stringify(this.workspace, null, 2);
        }
    },
    
    /**
     * Update navigation buttons
     */
    updateButtons() {
        const prevBtn = document.getElementById('construct-prev-btn');
        const nextBtn = document.getElementById('construct-next-btn');
        const buildBtn = document.getElementById('construct-build-btn');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentQuestionIndex === 0;
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentQuestionIndex >= this.questions.length - 1;
        }
        
        if (buildBtn) {
            // Enable build if we have at least purpose and components
            buildBtn.disabled = !this.responses.purpose || this.workspace.components.length === 0;
        }
    },
    
    /**
     * Navigate to previous question
     */
    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.showQuestion(this.currentQuestionIndex - 1);
        }
    },
    
    /**
     * Navigate to next question (skip with defaults)
     */
    nextQuestion() {
        const question = this.questions[this.currentQuestionIndex];
        
        // If required and no response, explain instead of skipping
        if (question.required && !this.responses[question.id]) {
            const display = document.getElementById('construct-current-question');
            if (display) {
                display.innerHTML += `
                    <div class="construct-dialog__warning">
                        This question is required. Please provide an answer.
                    </div>
                `;
            }
            return;
        }
        
        // Apply default if skipping
        if (!this.responses[question.id]) {
            this.responses[question.id] = '[Using defaults]';
        }
        
        if (this.currentQuestionIndex < this.questions.length - 1) {
            this.showQuestion(this.currentQuestionIndex + 1);
        }
    },
    
    /**
     * Build the composition
     */
    async buildComposition() {
        console.log('[CONSTRUCT-DIALOG] Building composition with:', this.workspace);
        
        // Send to Construct backend
        const request = {
            action: 'compose',
            components: this.workspace.components,
            connections: this.workspace.connections,
            constraints: this.workspace.constraints,
            metadata: {
                purpose: this.responses.purpose,
                created_via: 'guided_dialog'
            }
        };
        
        try {
            const response = await this.sendToConstruct(JSON.stringify(request));
            console.log('[CONSTRUCT-DIALOG] Composition created:', response);
            
            // Show success and switch to action buttons
            this.showCompositionActions();
            
        } catch (error) {
            console.error('[CONSTRUCT-DIALOG] Build failed:', error);
            this.showError(error.message);
        }
    },
    
    /**
     * Send request to Construct system
     */
    async sendToConstruct(message) {
        const apiUrl = window.ergonUrl ? window.ergonUrl('/api/v1/construct/process') : '/api/v1/construct/process';
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                sender_id: 'guided-dialog'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    },
    
    /**
     * Show composition action buttons
     */
    showCompositionActions() {
        const container = document.getElementById('construct-actions');
        if (container) {
            container.innerHTML = `
                <div class="ergon__separator"></div>
                <div class="construct-dialog__actions">
                    <button class="ergon__button ergon__button--validate" onclick="ConstructDialog.validate()">
                        Validate
                    </button>
                    <button class="ergon__button ergon__button--test" onclick="ConstructDialog.test()">
                        Test
                    </button>
                    <button class="ergon__button ergon__button--publish" onclick="ConstructDialog.publish()">
                        Publish
                    </button>
                    <button class="ergon__button ergon__button--revise" onclick="ConstructDialog.revise()">
                        Revise
                    </button>
                </div>
            `;
        }
    },
    
    /**
     * Validate composition
     */
    async validate() {
        console.log('[CONSTRUCT-DIALOG] Validating composition');
        // Implementation for validate
    },
    
    /**
     * Test composition
     */
    async test() {
        console.log('[CONSTRUCT-DIALOG] Testing composition');
        // Implementation for test
    },
    
    /**
     * Publish composition
     */
    async publish() {
        console.log('[CONSTRUCT-DIALOG] Publishing composition');
        // Implementation for publish
    },
    
    /**
     * Revise composition
     */
    revise() {
        console.log('[CONSTRUCT-DIALOG] Revising composition');
        // Return to dialog for revisions
        this.showQuestion(0);
    },
    
    /**
     * Enable build button
     */
    enableBuild() {
        const buildBtn = document.getElementById('construct-build-btn');
        if (buildBtn) {
            buildBtn.disabled = false;
            buildBtn.classList.add('construct-dialog__build-ready');
        }
    },
    
    /**
     * Show error message
     */
    showError(message) {
        const display = document.getElementById('construct-current-question');
        if (display) {
            display.innerHTML += `
                <div class="construct-dialog__error">
                    Error: ${message}
                </div>
            `;
        }
    },
    
    /**
     * Set up event handlers
     */
    setupEventHandlers() {
        // Listen for chat input when on Construct tab
        const input = document.getElementById('ergon-chat-input');
        if (input) {
            // Store original handler
            const originalKeydown = input.onkeydown;
            
            input.addEventListener('keydown', (e) => {
                // Only intercept if Construct tab is active
                const constructTab = document.getElementById('ergon-tab-construct');
                if (constructTab && constructTab.checked) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        const message = input.value.trim();
                        if (message) {
                            this.processResponse(message);
                            input.value = '';
                        }
                    }
                } else if (originalKeydown) {
                    // Use original handler for other tabs
                    originalKeydown.call(input, e);
                }
            });
        }
    }
};

// Export for global access
window.ConstructDialog = ConstructDialog;