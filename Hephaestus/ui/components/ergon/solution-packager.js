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
        // Use the Ergon API endpoint directly
        this.baseUrl = 'http://localhost:8102/api/ergon/packager';

        // Initialize on load
        this.init();

        // Setup communication with parent Ergon
        this.setupParentCommunication();
    }

    init() {
        // Generate session ID
        this.sessionId = 'session-' + Date.now();
        document.getElementById('session_id').value = this.sessionId;

        // Load available standards
        this.loadStandards();

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

    async planSolution() {
        console.log('[PACKAGER] Planning solution...');

        // First get feedback from Ergon
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
                throw new Error('Analysis failed');
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

        // Display the message in the Planning Assistant (no prefix for user input)
        this.addMessage(message, 'analysis');

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

    requestErgonFeedback() {
        const config = this.getConfig();

        // Create structured message for Ergon with clear instructions
        const message = `
=== CONSTRUCT FEEDBACK REQUEST ===

I need you to analyze this Solution Packager configuration and provide recommendations.

CURRENT CONFIGURATION:
- GitHub URL: ${config.github_url || '[Not provided - NEEDS URL]'}
- Apply Standards: ${config.apply_standards ? 'Yes' : 'No'}
  ${config.apply_standards && config.standards ? 'Selected: ' + config.standards.join(', ') : ''}
- Include CI Guide: ${config.include_ci ? 'Yes' : 'No'}
  ${config.include_ci ? `Provider: ${config.ci_provider}, Model: ${config.ci_model}, Name: ${config.ci_name || 'auto'}` : ''}
- Add to Menu: ${config.add_to_menu ? 'Yes' : 'No'}
  ${config.add_to_menu ? `Category: ${config.menu_category}` : ''}

INSTRUCTIONS FOR YOUR ANALYSIS:
1. Check if GitHub URL is valid and accessible
2. Based on the repository type, recommend which standards to apply:
   - extract_hardcoded: For repos with hardcoded URLs/ports/paths
   - split_large_files: For repos with files >500 lines
   - add_documentation: For repos missing README/docs
   - add_error_handling: For production code lacking try/catch
   - enforce_naming: For inconsistent naming conventions
   - add_config_example: For configurable applications

3. Suggest the best CI model based on complexity
4. Identify any potential issues or missing configuration

RESPONSE FORMAT:
Please provide:
1. A brief analysis in plain text
2. Then include a JSON block with your recommendations:

{
  "recommendations": {
    "standards": ["standard_id1", "standard_id2"],
    "ci_model": "recommended-model",
    "ci_provider": "recommended-provider",
    "warnings": ["warning1", "warning2"],
    "suggestions": ["suggestion1", "suggestion2"]
  }
}

The JSON will be automatically parsed and can be applied with the Apply button.
`;

        this.sendToErgon(message);
        this.addMessage('📡 Requesting feedback from Ergon CI...', 'progress');
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