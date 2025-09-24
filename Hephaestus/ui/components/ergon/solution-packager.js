/**
 * Solution Packager JavaScript
 * Minimal JavaScript - HTML injection only, no DOM manipulation
 */

class SolutionPackager {
    constructor() {
        this.sessionId = null;
        this.eventSource = null;
        this.currentPlan = null;
        this.storedRecommendations = null; // Store Ergon's recommendations
        this.constructContext = null; // Store the CI context metadata
        // Use the Ergon API endpoint directly
        this.baseUrl = 'http://localhost:8102/api/ergon/packager';

        // Initialize on load
        this.init();

        // Setup communication with parent Ergon
        this.setupParentCommunication();

        // Load the Construct context for CI guidance
        this.loadConstructContext();
    }

    init() {
        // Generate session ID
        this.sessionId = 'session-' + Date.now();
        document.getElementById('session_id').value = this.sessionId;

        // Load available standards
        this.loadStandards();

        // Load model providers and models from Rhetor
        this.loadProviders();

        console.log('[PACKAGER] Initialized with session:', this.sessionId);
    }

    async loadStandards() {
        try {
            const response = await fetch(`${this.baseUrl}/standards`);
            const data = await response.json();

            // Build standards HTML
            let html = '';
            for (const [id, standard] of Object.entries(data.standards)) {
                const checked = ['extract_hardcoded', 'add_documentation', 'add_config_example'].includes(id) ? 'checked' : '';
                html += `
                    <label class="standard-item">
                        <input type="checkbox" name="standards" value="${id}" ${checked}>
                        <span>${standard.name}</span>
                    </label>
                `;
            }

            // Inject HTML
            document.getElementById('standards-list').innerHTML = html;
        } catch (error) {
            console.error('[PACKAGER] Failed to load standards:', error);
        }
    }

    async loadProviders() {
        try {
            // Use Rhetor's endpoint to get real providers
            const rhetorUrl = window.rhetorUrl || ((path) => `http://localhost:8003${path}`);
            const response = await fetch(rhetorUrl('/api/providers'));

            if (!response.ok) {
                throw new Error(`Failed to fetch providers: ${response.statusText}`);
            }

            const data = await response.json();
            const providers = data.providers || [];

            // Build provider dropdown HTML
            const providerSelect = document.getElementById('ci_provider');
            if (providerSelect) {
                // Clear existing options
                providerSelect.innerHTML = '<option value="">Select Provider</option>';

                // Add providers from Rhetor
                providers.forEach(provider => {
                    const option = document.createElement('option');
                    option.value = provider.id;
                    option.textContent = provider.name;
                    providerSelect.appendChild(option);
                });

                // Set default to anthropic if available
                if (providers.some(p => p.id === 'anthropic')) {
                    providerSelect.value = 'anthropic';
                    // Load models for default provider
                    this.loadModelsForProvider('anthropic');
                }

                // Add change listener to load models when provider changes
                providerSelect.addEventListener('change', async (e) => {
                    const provider = e.target.value;
                    if (provider) {
                        await this.loadModelsForProvider(provider);
                    } else {
                        // Clear models dropdown
                        const modelSelect = document.getElementById('ci_model');
                        if (modelSelect) {
                            modelSelect.innerHTML = '<option value="">Select Model</option>';
                        }
                    }
                });
            }

            console.log('[PACKAGER] Loaded providers:', providers.length);
        } catch (error) {
            console.error('[PACKAGER] Failed to load providers:', error);
            // Fallback to static list if Rhetor is not available
            this.loadStaticProviders();
        }
    }

    async loadModelsForProvider(provider) {
        try {
            const rhetorUrl = window.rhetorUrl || ((path) => `http://localhost:8003${path}`);
            const response = await fetch(rhetorUrl(`/api/providers/${provider}/models`));

            if (!response.ok) {
                throw new Error(`Failed to fetch models: ${response.statusText}`);
            }

            const data = await response.json();
            const models = data.models || [];

            // Build model dropdown HTML
            const modelSelect = document.getElementById('ci_model');
            if (modelSelect) {
                // Clear existing options
                modelSelect.innerHTML = '<option value="">Select Model</option>';

                // Add models from Rhetor
                models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;
                    // Add deprecated indicator if needed
                    if (model.deprecated) {
                        option.textContent += ' (deprecated)';
                        option.style.color = '#999';
                    }
                    modelSelect.appendChild(option);
                });

                // Set default model based on provider
                if (provider === 'anthropic' && models.some(m => m.id === 'claude-3-5-sonnet')) {
                    modelSelect.value = 'claude-3-5-sonnet';
                } else if (models.length > 0) {
                    // Select first non-deprecated model
                    const firstActive = models.find(m => !m.deprecated);
                    if (firstActive) {
                        modelSelect.value = firstActive.id;
                    }
                }
            }

            console.log(`[PACKAGER] Loaded ${models.length} models for ${provider}`);
        } catch (error) {
            console.error(`[PACKAGER] Failed to load models for ${provider}:`, error);
        }
    }

    loadStaticProviders() {
        // Fallback static provider list
        const providers = [
            { id: 'anthropic', name: 'Anthropic' },
            { id: 'openai', name: 'OpenAI' },
            { id: 'groq', name: 'Groq' },
            { id: 'ollama', name: 'Ollama (Local)' }
        ];

        const providerSelect = document.getElementById('ci_provider');
        if (providerSelect) {
            providerSelect.innerHTML = '<option value="">Select Provider</option>';
            providers.forEach(provider => {
                const option = document.createElement('option');
                option.value = provider.id;
                option.textContent = provider.name;
                providerSelect.appendChild(option);
            });
            providerSelect.value = 'anthropic';
        }

        console.log('[PACKAGER] Using static provider list');
    }

    async planSolution() {
        console.log('[PACKAGER] Planning solution...');

        // Validate input is provided
        const githubUrlInput = document.getElementById('github_url');
        const githubUrl = githubUrlInput ? githubUrlInput.value.trim() : '';

        if (!githubUrl) {
            // Only get feedback from Ergon when no URL/path is provided
            this.clearMessages();
            this.addMessage('Please provide a GitHub repository URL or local directory path to analyze.', 'error');
            this.requestErgonFeedback();
            return;
        }

        // Validate input - accept either GitHub URL or local path
        const isGitHubUrl = githubUrl.match(/^https?:\/\/github\.com\/.+\/.+/);
        const isLocalPath = githubUrl.startsWith('/') || githubUrl.startsWith('~/') || githubUrl.startsWith('./') || githubUrl.startsWith('../');

        if (!isGitHubUrl && !isLocalPath) {
            this.clearMessages();
            this.addMessage('Please provide either:', 'error');
            this.addMessage('• A valid GitHub URL (e.g., https://github.com/owner/repo)', 'info');
            this.addMessage('• A local directory path (e.g., /path/to/project or ~/projects/myapp)', 'info');
            return;
        }

        // Log what type of input we're processing
        console.log('[PACKAGER] Processing:', isGitHubUrl ? 'GitHub URL' : 'Local Path', githubUrl);

        // First get feedback from Ergon with the URL/path
        this.requestErgonFeedback();

        // Update UI state
        this.clearMessages();
        this.addMessage('Starting analysis...', 'analysis');

        // Disable buttons during planning
        document.getElementById('plan-btn').disabled = true;
        document.getElementById('build-btn').disabled = true;

        try {
            // Get form data
            const formData = new FormData(document.getElementById('packager-config'));

            // Start SSE connection for real-time updates
            this.connectEventSource();

            // Send analyze request
            const analyzeResponse = await fetch(`${this.baseUrl}/analyze`, {
                method: 'POST',
                body: formData
            });

            if (!analyzeResponse.ok) {
                let errorMsg = `Analysis failed: ${analyzeResponse.status} ${analyzeResponse.statusText}`;
                try {
                    const errorData = await analyzeResponse.json();
                    if (errorData.detail) {
                        errorMsg = `Analysis failed: ${errorData.detail}`;
                    } else if (errorData.error) {
                        errorMsg = `Analysis failed: ${errorData.error}`;
                    }
                } catch (e) {
                    // If response isn't JSON, use status text
                }
                throw new Error(errorMsg);
            }

            const analysis = await analyzeResponse.json();
            console.log('[PACKAGER] Analysis complete:', analysis);

            // Show analysis results
            this.showAnalysis(analysis);

            // Show recommendations
            if (analysis.recommendations && analysis.recommendations.length > 0) {
                this.showRecommendations(analysis.recommendations);
            }

            // Create plan based on current config
            const config = this.getConfig();
            config.session_id = this.sessionId;

            const planResponse = await fetch(`${this.baseUrl}/plan`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            if (!planResponse.ok) {
                throw new Error('Plan creation failed');
            }

            const planData = await planResponse.json();
            this.currentPlan = planData.plan;
            console.log('[PACKAGER] Plan created:', this.currentPlan);

            // Show plan
            this.showPlan(this.currentPlan);

            // Enable build button
            document.getElementById('build-btn').disabled = false;
            this.addMessage('✅ Plan ready - click BUILD to execute', 'success');

        } catch (error) {
            console.error('[PACKAGER] Planning failed:', error);
            this.addMessage(`Error: ${error.message}`, 'error');
            this.addMessage('❌ Planning failed', 'error');
        } finally {
            // Re-enable plan button
            document.getElementById('plan-btn').disabled = false;
        }
    }

    async buildSolution() {
        if (!this.currentPlan) {
            this.addMessage('No plan available. Click PLAN first.', 'error');
            return;
        }

        console.log('[PACKAGER] Building solution...');

        // Update UI state
        this.addMessage('🔨 Building solution...', 'progress');
        this.addMessage('Starting build process...', 'progress');

        // Disable buttons during build
        document.getElementById('plan-btn').disabled = true;
        document.getElementById('build-btn').disabled = true;

        try {
            // Send build request
            const response = await fetch(`${this.baseUrl}/build`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    plan: this.currentPlan
                })
            });

            if (!response.ok) {
                throw new Error('Build failed');
            }

            const result = await response.json();
            console.log('[PACKAGER] Build complete:', result);

            // Show success
            this.addMessage(`✅ Solution packaged successfully!`, 'success');
            this.addMessage(`New repository: ${result.output_repo}`, 'success');

            // Reset for next package
            setTimeout(() => {
                this.addMessage('Ready to package another project.', 'welcome');
                document.getElementById('plan-btn').disabled = false;
            }, 2000);

        } catch (error) {
            console.error('[PACKAGER] Build failed:', error);
            this.addMessage(`Build failed: ${error.message}`, 'error');
            this.addMessage('❌ Build failed', 'error');

            // Re-enable buttons
            document.getElementById('plan-btn').disabled = false;
            document.getElementById('build-btn').disabled = false;
        }
    }

    connectEventSource() {
        if (this.eventSource) {
            this.eventSource.close();
        }

        this.eventSource = new EventSource(`${this.baseUrl}/stream/${this.sessionId}`);

        this.eventSource.addEventListener('connected', (event) => {
            console.log('[PACKAGER] SSE connected:', event.data);
        });

        this.eventSource.addEventListener('analysis_progress', (event) => {
            const data = JSON.parse(event.data);
            this.addMessage(`Analyzing: ${data.current} (${data.percent}%)`, 'progress');
        });

        this.eventSource.addEventListener('build_progress', (event) => {
            const data = JSON.parse(event.data);
            this.addMessage(`Step ${data.step}/${data.total}: ${data.description}`, 'progress');
            this.showProgress(data.step, data.total);
        });

        this.eventSource.addEventListener('build_complete', (event) => {
            const data = JSON.parse(event.data);
            if (data.success) {
                this.addMessage('✅ Build completed successfully!', 'success');
            }
        });

        this.eventSource.addEventListener('error', (event) => {
            console.error('[PACKAGER] SSE error:', event);
        });
    }

    getConfig() {
        const formData = new FormData(document.getElementById('packager-config'));
        const config = {
            github_url: formData.get('github_url'),
            apply_standards: formData.get('enable_standards') === 'on',
            include_ci: formData.get('enable_ci') === 'on',
            add_to_menu: formData.get('enable_menu') === 'on'
        };

        // Get selected standards
        if (config.apply_standards) {
            config.standards = [];
            document.querySelectorAll('input[name="standards"]:checked').forEach(checkbox => {
                config.standards.push(checkbox.value);
            });
        }

        // Get CI config
        if (config.include_ci) {
            config.ci_provider = formData.get('ci_provider');
            config.ci_model = formData.get('ci_model');
            config.ci_name = formData.get('ci_name') || 'auto';
        }

        // Get menu config
        if (config.add_to_menu) {
            config.menu_category = formData.get('menu_category');
            config.build_command = formData.get('build_command');
            config.run_command = formData.get('run_command');
            config.description = formData.get('description');
        }

        return config;
    }

    showAnalysis(analysis) {
        let html = '<div class="ci-message analysis">';
        html += '<strong>Repository Analysis:</strong><br>';
        html += `• Project Type: ${analysis.analysis.project_type}<br>`;
        html += `• Files: ${analysis.analysis.files.length}<br>`;

        if (analysis.analysis.large_files.length > 0) {
            html += `• Large Files: ${analysis.analysis.large_files.length}<br>`;
        }

        if (analysis.analysis.hardcoded_values.length > 0) {
            html += `• Hardcoded Values: ${analysis.analysis.hardcoded_values.length}<br>`;
        }

        html += '</div>';

        document.getElementById('ci-messages').insertAdjacentHTML('beforeend', html);
        this.scrollToBottom();
    }

    showRecommendations(recommendations) {
        let html = '<div class="ci-message recommendation">';
        html += '<strong>CI Recommendations:</strong><ul>';

        recommendations.forEach(rec => {
            html += `<li>${rec.reason}</li>`;
        });

        html += '</ul>';
        html += '<div class="recommendation-actions">';
        html += `<button class="rec-btn" onclick="packager.applyRecommendations()">Apply Recommendations</button>`;
        html += `<button class="rec-btn" onclick="packager.skipRecommendations()">Skip</button>`;
        html += '</div>';
        html += '</div>';

        document.getElementById('ci-messages').insertAdjacentHTML('beforeend', html);
        this.scrollToBottom();
    }

    async applyRecommendations() {
        try {
            const response = await fetch(`${this.baseUrl}/apply-recommendations`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: this.sessionId })
            });

            const data = await response.json();

            // Check recommended standards
            data.updates.standards.forEach(standardId => {
                const checkbox = document.querySelector(`input[value="${standardId}"]`);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });

            this.addMessage('✓ Recommendations applied to configuration', 'success');

            // Re-plan with updated config
            setTimeout(() => this.planSolution(), 1000);

        } catch (error) {
            console.error('[PACKAGER] Failed to apply recommendations:', error);
        }
    }

    skipRecommendations() {
        this.addMessage('Recommendations skipped', 'analysis');
    }

    showPlan(plan) {
        let html = '<div class="ci-message plan">';
        html += '<strong>Execution Plan (v' + plan.version + '):</strong><br>';
        html += `Summary: ${plan.summary}<br>`;
        html += 'Steps:<ol>';

        plan.steps.forEach(step => {
            html += `<li>${step.description}</li>`;
        });

        html += '</ol>';
        html += `<strong>Output:</strong> ${plan.output_repo}<br>`;
        html += `<strong>Estimated Time:</strong> ${plan.total_time} seconds`;

        if (plan.warnings && plan.warnings.length > 0) {
            html += '<br><strong>Warnings:</strong><ul>';
            plan.warnings.forEach(warning => {
                html += `<li>${warning}</li>`;
            });
            html += '</ul>';
        }

        html += '</div>';

        document.getElementById('ci-messages').insertAdjacentHTML('beforeend', html);
        this.scrollToBottom();
    }

    showProgress(current, total) {
        const percent = Math.round((current / total) * 100);

        let html = '<div class="ci-message progress">';
        html += '<div class="progress-bar">';
        html += `<div class="progress-fill" style="width: ${percent}%">${percent}%</div>`;
        html += '</div>';
        html += '</div>';

        // Replace last progress message
        const messages = document.getElementById('ci-messages');
        const lastProgress = messages.querySelector('.ci-message.progress:last-child');

        if (lastProgress && lastProgress.querySelector('.progress-bar')) {
            lastProgress.outerHTML = html;
        } else {
            messages.insertAdjacentHTML('beforeend', html);
        }

        this.scrollToBottom();
    }

    addMessage(text, type = 'message') {
        const html = `<div class="ci-message ${type}">${text}</div>`;
        document.getElementById('ci-messages').insertAdjacentHTML('beforeend', html);
        this.scrollToBottom();
    }

    clearMessages() {
        const messages = document.getElementById('ci-messages');
        messages.innerHTML = '';
    }

    // Status removed - using Apply button instead

    scrollToBottom() {
        const messages = document.getElementById('ci-messages');
        messages.scrollTop = messages.scrollHeight;
    }

    // Chat handled by parent Ergon component

    setupParentCommunication() {
        // Listen for messages from parent window
        window.addEventListener('message', (event) => {
            if (event.data.type === 'ergon-chat-message') {
                this.handleErgonMessage(event.data.message);
            }
        });

        // Check if we're in an iframe
        if (window.parent !== window) {
            console.log('[PACKAGER] Running in iframe, parent communication enabled');
        }
    }

    handleErgonMessage(message) {
        console.log('[PACKAGER] Received from Ergon:', message);

        // Display the message in the Planning Assistant with Ergon prefix
        this.addMessage(`<strong>Ergon:</strong> ${message}`, 'analysis');

        // Parse for configuration updates if the message contains JSON
        try {
            const jsonMatch = message.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                const suggestions = JSON.parse(jsonMatch[0]);

                // Store recommendations for later apply
                if (suggestions.recommendations) {
                    this.storedRecommendations = suggestions.recommendations;

                    // Show the Apply button
                    const applyBtn = document.getElementById('apply-recommendations-btn');
                    if (applyBtn) {
                        applyBtn.style.display = 'inline-block';
                    }

                    this.addMessage('✅ Recommendations received. Click "Apply Ergon\'s Advice" to update configuration.', 'success');
                }
            }
        } catch (e) {
            // Not JSON, just display as advice
            console.log('[PACKAGER] No JSON found in message');
        }
    }

    sendToErgon(message) {
        // Send message to parent Ergon component
        if (window.parent !== window) {
            window.parent.postMessage({
                type: 'packager-to-ergon',
                message: message
            }, '*');
        }
    }

    async loadConstructContext() {
        try {
            // Load the context file using MCP file operations
            // Note: MCP paths are relative to Tekton root
            this.constructContext = await window.mcp.readFile('Workflows/Ergon/construct-context.md');
            console.log('[PACKAGER] Loaded Construct context for CI guidance');
        } catch (error) {
            console.log('[PACKAGER] Construct context not found, using default instructions');
            // Fallback to basic instructions if file not found
            this.constructContext = 'You are helping users package GitHub repositories into deployable solutions.';
        }
    }

    requestErgonFeedback() {
        const config = this.getConfig();

        // Create message with context and current configuration
        const message = `
${this.constructContext || ''}

=== CURRENT USER CONFIGURATION ===

GitHub Repository URL: ${config.github_url || '[Not provided - User needs to enter a GitHub URL]'}

Apply Programming Standards: ${config.apply_standards ? 'Yes' : 'No'}
${config.apply_standards && config.standards && config.standards.length > 0 ?
  'Currently Selected Standards: ' + config.standards.join(', ') :
  config.apply_standards ? 'No standards selected yet' : ''}

Include CI Guide: ${config.include_ci ? 'Yes' : 'No'}
${config.include_ci ? `
  CI Provider: ${config.ci_provider || 'anthropic'}
  CI Model: ${config.ci_model || 'claude-3-5-sonnet'}
  CI Name: ${config.ci_name === 'Auto-generate from project' ? 'auto-generate' : config.ci_name || 'auto-generate'}` : ''}

Add to Menu of the Day: ${config.add_to_menu ? 'Yes' : 'No'}
${config.add_to_menu ? `
  Category: ${config.menu_category || 'not selected'}
  Build Command: ${config.build_command || 'not specified'}
  Run Command: ${config.run_command || 'not specified'}` : ''}

=== REQUEST ===

The user has clicked PLAN. Please analyze this configuration and provide your recommendations as described in your context guide.

Remember to:
1. Validate the configuration
2. Analyze the repository (if URL provided)
3. Recommend applicable standards
4. Include a JSON recommendations block for the Apply button
5. Explain your reasoning clearly
`;

        this.sendToErgon(message);
        this.addMessage('📡 Requesting analysis from Ergon CI...', 'progress');
    }

    applyStoredRecommendations() {
        if (!this.storedRecommendations) {
            this.addMessage('No recommendations to apply.', 'warning');
            return;
        }

        const rec = this.storedRecommendations;

        // Update standards checkboxes
        if (rec.standards) {
            rec.standards.forEach(standardId => {
                const checkbox = document.querySelector(`input[value="${standardId}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }

        // Update CI model
        if (rec.ci_model) {
            const modelSelect = document.getElementById('ci_model');
            if (modelSelect) modelSelect.value = rec.ci_model;
        }

        // Update CI provider
        if (rec.ci_provider) {
            const providerSelect = document.getElementById('ci_provider');
            if (providerSelect) providerSelect.value = rec.ci_provider;
        }

        // Show warnings
        if (rec.warnings) {
            rec.warnings.forEach(warning => {
                this.addMessage(`⚠️ ${warning}`, 'warning');
            });
        }

        // Show suggestions
        if (rec.suggestions) {
            rec.suggestions.forEach(suggestion => {
                this.addMessage(`💡 ${suggestion}`, 'suggestion');
            });
        }

        this.addMessage('✓ Applied Ergon\'s recommendations to configuration', 'success');

        // Hide the Apply button after applying
        const applyBtn = document.getElementById('apply-recommendations-btn');
        if (applyBtn) {
            applyBtn.style.display = 'none';
        }

        // Clear stored recommendations after applying
        this.storedRecommendations = null;
    }
}

// Utility functions for button clicks
function selectAllStandards() {
    document.querySelectorAll('input[name="standards"]').forEach(checkbox => {
        checkbox.checked = true;
    });
}

function clearAllStandards() {
    document.querySelectorAll('input[name="standards"]').forEach(checkbox => {
        checkbox.checked = false;
    });
}

function planSolution() {
    packager.planSolution();
}

function buildSolution() {
    packager.buildSolution();
}

function applyRecommendations() {
    packager.applyStoredRecommendations();
}

// Initialize on load
let packager;
document.addEventListener('DOMContentLoaded', () => {
    packager = new SolutionPackager();
});