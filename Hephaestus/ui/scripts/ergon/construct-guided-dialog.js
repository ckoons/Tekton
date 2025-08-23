/**
 * Guided Dialog System for Ergon Construct
 * 
 * Progressive questionnaire that intelligently fills from user responses
 */

window.ConstructDialog = {
    // Questions will be loaded from API
    questions: [],
    questionsData: null,
    
    // Current state
    currentQuestionIndex: 0,
    responses: {},
    workspace: {},
    currentWorkspaceId: null,
    
    /**
     * Initialize the guided dialog
     */
    async init() {
        console.log('[CONSTRUCT-DIALOG] Initializing guided dialog');
        
        // Load questions from API first
        await this.loadQuestions();
        
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
     * Load questions from API
     */
    async loadQuestions() {
        try {
            console.log('[CONSTRUCT-DIALOG] Loading questions from API');
            
            const apiUrl = window.ergonUrl ? 
                window.ergonUrl('/api/ergon/construct/questions') : 
                'http://localhost:8102/api/ergon/construct/questions';
            
            console.log('[CONSTRUCT-DIALOG] Fetching from:', apiUrl);
            
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`Failed to load questions: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success' && data.questions) {
                this.questionsData = data.questions;
                this.questions = data.questions.questions || [];
                console.log(`[CONSTRUCT-DIALOG] Loaded ${this.questions.length} questions`);
                
                // Apply smart defaults rules
                this.smartDefaults = data.questions.smart_defaults || {};
            } else {
                throw new Error('Invalid questions data');
            }
            
        } catch (error) {
            console.error('[CONSTRUCT-DIALOG] Failed to load questions:', error);
            
            // Fallback to basic questions
            this.questions = [
                {
                    id: 'purpose',
                    question: 'What do you want to build?',
                    placeholder: 'Describe the solution you need...',
                    required: true
                },
                {
                    id: 'components',
                    question: 'Which components should we use?',
                    placeholder: 'List components or say "suggest"...',
                    required: false
                }
            ];
        }
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
        
        // Check if questions are loaded
        if (!this.questions || this.questions.length === 0) {
            console.error('[CONSTRUCT-DIALOG] Questions not loaded yet!');
            // Try to initialize first
            this.init().then(() => {
                console.log('[CONSTRUCT-DIALOG] Initialized, retrying response processing');
                this.processResponseInternal(message);
            }).catch(error => {
                console.error('[CONSTRUCT-DIALOG] Failed to initialize:', error);
            });
            return;
        }
        
        this.processResponseInternal(message);
    },
    
    /**
     * Internal method to process response after ensuring initialization
     */
    processResponseInternal(message) {
        const question = this.questions[this.currentQuestionIndex];
        
        if (!question) {
            console.error('[CONSTRUCT-DIALOG] No question at index:', this.currentQuestionIndex);
            return;
        }
        
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
            
            // Store workspace ID if returned
            if (response.workspace_id) {
                this.currentWorkspaceId = response.workspace_id;
            }
            
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
        const apiUrl = window.ergonUrl ? 
            window.ergonUrl('/api/ergon/construct/process') : 
            'http://localhost:8102/api/ergon/construct/process';
        
        console.log('[CONSTRUCT-DIALOG] Sending to:', apiUrl);
        
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
            console.error('[CONSTRUCT-DIALOG] API error:', response.status, response.statusText);
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
        try {
            const request = {
                action: 'validate',
                workspace_id: this.currentWorkspaceId,
                checks: ['connections', 'dependencies', 'standards']
            };
            
            const response = await this.sendToConstruct(JSON.stringify(request));
            
            // Show validation results
            const display = document.getElementById('construct-current-question');
            if (display) {
                const valid = response.valid || response.status === 'success';
                display.innerHTML = `
                    <div class="construct-dialog__validation ${valid ? 'valid' : 'invalid'}">
                        <h4>Validation ${valid ? 'Passed ✓' : 'Failed ✗'}</h4>
                        ${response.errors ? `<div class="errors">Errors: ${response.errors.join(', ')}</div>` : ''}
                        ${response.warnings ? `<div class="warnings">Warnings: ${response.warnings.join(', ')}</div>` : ''}
                    </div>
                `;
            }
        } catch (error) {
            console.error('[CONSTRUCT-DIALOG] Validation failed:', error);
            this.showError(`Validation failed: ${error.message}`);
        }
    },
    
    /**
     * Test composition
     */
    async test() {
        console.log('[CONSTRUCT-DIALOG] Testing composition');
        try {
            const request = {
                action: 'test',
                workspace_id: this.currentWorkspaceId,
                sandbox_config: {
                    timeout: 300,
                    provider: this.responses.container === 'yes' ? 'docker' : 'sandbox-exec'
                }
            };
            
            const response = await this.sendToConstruct(JSON.stringify(request));
            
            // Show test results
            const display = document.getElementById('construct-current-question');
            if (display) {
                display.innerHTML = `
                    <div class="construct-dialog__test-results">
                        <h4>Test Started</h4>
                        <div>Sandbox ID: ${response.sandbox_id || 'pending'}</div>
                        <div>Status: ${response.status}</div>
                        <div class="test-output">Results will stream here...</div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('[CONSTRUCT-DIALOG] Test failed:', error);
            this.showError(`Test failed: ${error.message}`);
        }
    },
    
    /**
     * Publish composition
     */
    async publish() {
        console.log('[CONSTRUCT-DIALOG] Publishing composition');
        try {
            const request = {
                action: 'publish',
                workspace_id: this.currentWorkspaceId,
                metadata: {
                    name: this.workspace.metadata?.name || 'Unnamed Solution',
                    version: '1.0.0',
                    description: this.responses.purpose || 'No description',
                    tags: ['construct', 'composed']
                }
            };
            
            const response = await this.sendToConstruct(JSON.stringify(request));
            
            // Show publish results
            const display = document.getElementById('construct-current-question');
            if (display) {
                display.innerHTML = `
                    <div class="construct-dialog__publish-success">
                        <h4>Published Successfully! 🎉</h4>
                        <div>Registry ID: ${response.registry_id || 'unknown'}</div>
                        <div>Your solution is now available in the Registry for reuse.</div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('[CONSTRUCT-DIALOG] Publish failed:', error);
            this.showError(`Publish failed: ${error.message}`);
        }
    },
    
    /**
     * Revise composition
     */
    revise() {
        console.log('[CONSTRUCT-DIALOG] Revising composition');
        // Don't reset everything, just go back to questions
        // Keep the responses and workspace intact
        this.showQuestion(0);
        
        // Show a message that we're in revision mode
        const display = document.getElementById('construct-current-question');
        if (display) {
            const currentHtml = display.innerHTML;
            display.innerHTML = `
                <div class="construct-dialog__revision-mode">
                    <strong>Revision Mode</strong> - Modify any answers below
                </div>
                ${currentHtml}
            `;
        }
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