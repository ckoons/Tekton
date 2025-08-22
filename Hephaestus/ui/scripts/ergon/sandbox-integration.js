/**
 * Sandbox integration for testing Registry solutions.
 * 
 * Handles Test button clicks, sandbox execution, and result display.
 */

// Global sandbox state
window.ergonSandbox = {
    activeSandboxes: new Map(),
    outputPanels: new Map()
};

/**
 * Test a solution in sandbox
 * @param {string} solutionId - Registry solution ID
 * @param {HTMLElement} button - Test button element
 */
async function testSolution(solutionId, button) {
    try {
        // Disable button and show loading
        button.disabled = true;
        button.textContent = 'Starting...';
        
        // Create sandbox
        const response = await fetch('/api/ergon/sandbox/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                solution_id: solutionId,
                timeout: 300,
                memory_limit: '4g'
            })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to start sandbox: ${response.statusText}`);
        }
        
        const { sandbox_id } = await response.json();
        
        // Track sandbox
        window.ergonSandbox.activeSandboxes.set(solutionId, sandbox_id);
        
        // Update button
        button.textContent = 'Running...';
        button.classList.add('ergon__button--running');
        
        // Create output panel
        const outputPanel = createOutputPanel(solutionId, sandbox_id);
        showOutputPanel(outputPanel);
        
        // Start execution and stream output
        await executeSandbox(sandbox_id, outputPanel);
        
        // Get results
        const results = await getSandboxResults(sandbox_id);
        displayResults(outputPanel, results);
        
        // Update button
        if (results.exit_code === 0) {
            button.textContent = 'Success';
            button.classList.remove('ergon__button--running');
            button.classList.add('ergon__button--success');
        } else {
            button.textContent = 'Failed';
            button.classList.remove('ergon__button--running');
            button.classList.add('ergon__button--failed');
        }
        
        // Re-enable after delay
        setTimeout(() => {
            button.disabled = false;
            button.textContent = 'Test';
            button.classList.remove('ergon__button--success', 'ergon__button--failed');
        }, 3000);
        
    } catch (error) {
        console.error('Sandbox test error:', error);
        button.textContent = 'Error';
        button.classList.add('ergon__button--error');
        
        setTimeout(() => {
            button.disabled = false;
            button.textContent = 'Test';
            button.classList.remove('ergon__button--error');
        }, 3000);
        
        alert(`Test failed: ${error.message}`);
    }
}

/**
 * Execute sandbox and stream output
 * @param {string} sandboxId - Sandbox instance ID
 * @param {HTMLElement} outputPanel - Output display panel
 */
async function executeSandbox(sandboxId, outputPanel) {
    const outputArea = outputPanel.querySelector('.ergon__sandbox-output');
    
    try {
        // Start execution with SSE streaming
        const response = await fetch('/api/ergon/sandbox/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sandbox_id: sandboxId })
        });
        
        if (!response.ok) {
            throw new Error(`Execution failed: ${response.statusText}`);
        }
        
        // Read SSE stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    
                    if (data.line) {
                        appendOutput(outputArea, data.line);
                    } else if (data.error) {
                        appendOutput(outputArea, `[error] ${data.error}`, 'error');
                    } else if (data.done) {
                        appendOutput(outputArea, '\n--- Execution Complete ---\n', 'info');
                        break;
                    }
                }
            }
        }
        
    } catch (error) {
        appendOutput(outputArea, `\n[error] ${error.message}`, 'error');
    }
}

/**
 * Get sandbox results
 * @param {string} sandboxId - Sandbox instance ID
 * @returns {Object} Sandbox results
 */
async function getSandboxResults(sandboxId) {
    const response = await fetch(`/api/ergon/sandbox/results/${sandboxId}`);
    if (!response.ok) {
        throw new Error(`Failed to get results: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Create output panel for sandbox
 * @param {string} solutionId - Solution ID
 * @param {string} sandboxId - Sandbox ID
 * @returns {HTMLElement} Output panel element
 */
function createOutputPanel(solutionId, sandboxId) {
    const panel = document.createElement('div');
    panel.className = 'ergon__sandbox-panel';
    panel.dataset.solutionId = solutionId;
    panel.dataset.sandboxId = sandboxId;
    
    panel.innerHTML = `
        <div class="ergon__sandbox-header">
            <h4>Testing Solution: ${solutionId.substring(0, 8)}...</h4>
            <div class="ergon__sandbox-actions">
                <button onclick="stopSandbox('${sandboxId}')" class="ergon__button ergon__button--stop">Stop</button>
                <button onclick="clearSandboxOutput('${sandboxId}')" class="ergon__button">Clear</button>
                <button onclick="closeSandboxPanel('${sandboxId}')" class="ergon__button">Close</button>
            </div>
        </div>
        <div class="ergon__sandbox-status">
            <span class="ergon__status-label">Status:</span>
            <span class="ergon__status-value">Running</span>
            <span class="ergon__sandbox-id">Sandbox: ${sandboxId.substring(0, 8)}...</span>
        </div>
        <div class="ergon__sandbox-output"></div>
        <div class="ergon__sandbox-results" style="display: none;"></div>
    `;
    
    window.ergonSandbox.outputPanels.set(sandboxId, panel);
    return panel;
}

/**
 * Show output panel
 * @param {HTMLElement} panel - Panel to show
 */
function showOutputPanel(panel) {
    // Find or create output container
    let container = document.getElementById('ergon-sandbox-output');
    if (!container) {
        container = document.createElement('div');
        container.id = 'ergon-sandbox-output';
        container.className = 'ergon__sandbox-container';
        
        // Insert after Registry panel
        const registryPanel = document.querySelector('.ergon__registry-panel');
        if (registryPanel) {
            registryPanel.parentNode.insertBefore(container, registryPanel.nextSibling);
        } else {
            document.querySelector('.ergon__panel-content').appendChild(container);
        }
    }
    
    container.appendChild(panel);
}

/**
 * Append output to display area
 * @param {HTMLElement} outputArea - Output area element
 * @param {string} text - Text to append
 * @param {string} type - Output type (stdout, stderr, error, info)
 */
function appendOutput(outputArea, text, type = 'stdout') {
    const line = document.createElement('div');
    line.className = `ergon__output-line ergon__output-${type}`;
    
    // Parse output type from prefix
    if (text.startsWith('[stdout] ')) {
        line.textContent = text.substring(9);
        line.className = 'ergon__output-line ergon__output-stdout';
    } else if (text.startsWith('[stderr] ')) {
        line.textContent = text.substring(9);
        line.className = 'ergon__output-line ergon__output-stderr';
    } else if (text.startsWith('[error] ')) {
        line.textContent = text.substring(8);
        line.className = 'ergon__output-line ergon__output-error';
    } else {
        line.textContent = text;
    }
    
    outputArea.appendChild(line);
    outputArea.scrollTop = outputArea.scrollHeight;
}

/**
 * Display sandbox results
 * @param {HTMLElement} panel - Output panel
 * @param {Object} results - Sandbox results
 */
function displayResults(panel, results) {
    const statusEl = panel.querySelector('.ergon__status-value');
    const resultsEl = panel.querySelector('.ergon__sandbox-results');
    
    // Update status
    statusEl.textContent = results.status;
    statusEl.className = `ergon__status-value ergon__status-${results.status}`;
    
    // Show results
    resultsEl.innerHTML = `
        <h5>Execution Results</h5>
        <div class="ergon__result-item">
            <span>Exit Code:</span> <span>${results.exit_code || 'N/A'}</span>
        </div>
        <div class="ergon__result-item">
            <span>Execution Time:</span> <span>${results.execution_time ? results.execution_time.toFixed(2) + 's' : 'N/A'}</span>
        </div>
        ${results.errors && results.errors.length > 0 ? `
        <div class="ergon__result-item ergon__result-errors">
            <span>Errors:</span>
            <ul>${results.errors.map(e => `<li>${e}</li>`).join('')}</ul>
        </div>
        ` : ''}
    `;
    resultsEl.style.display = 'block';
}

/**
 * Stop a running sandbox
 * @param {string} sandboxId - Sandbox ID to stop
 */
async function stopSandbox(sandboxId) {
    try {
        await fetch(`/api/ergon/sandbox/${sandboxId}`, { method: 'DELETE' });
        
        const panel = window.ergonSandbox.outputPanels.get(sandboxId);
        if (panel) {
            const statusEl = panel.querySelector('.ergon__status-value');
            statusEl.textContent = 'Stopped';
            appendOutput(
                panel.querySelector('.ergon__sandbox-output'),
                '\n--- Sandbox Stopped ---\n',
                'info'
            );
        }
    } catch (error) {
        console.error('Failed to stop sandbox:', error);
    }
}

/**
 * Clear sandbox output
 * @param {string} sandboxId - Sandbox ID
 */
function clearSandboxOutput(sandboxId) {
    const panel = window.ergonSandbox.outputPanels.get(sandboxId);
    if (panel) {
        panel.querySelector('.ergon__sandbox-output').innerHTML = '';
    }
}

/**
 * Close sandbox panel
 * @param {string} sandboxId - Sandbox ID
 */
function closeSandboxPanel(sandboxId) {
    const panel = window.ergonSandbox.outputPanels.get(sandboxId);
    if (panel) {
        panel.remove();
        window.ergonSandbox.outputPanels.delete(sandboxId);
    }
}

// Hook into Registry Test buttons
document.addEventListener('DOMContentLoaded', () => {
    // Listen for Test button clicks
    document.addEventListener('click', (e) => {
        if (e.target.matches('[data-tekton-action="test-solution"]')) {
            const card = e.target.closest('.ergon__solution-card');
            if (card) {
                const solutionId = card.dataset.solutionId;
                if (solutionId) {
                    testSolution(solutionId, e.target);
                }
            }
        }
    });
});

// Export for debugging
window.ergonSandbox.testSolution = testSolution;
window.ergonSandbox.stopSandbox = stopSandbox;