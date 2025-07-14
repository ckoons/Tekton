/**
 * Sophia Advanced Analytics UI Module
 * Handles pattern detection, causal analysis, complex events, predictions, and network analysis
 */

(function() {
    'use strict';

    // WebSocket connection for real-time updates
    let ws = null;
    let wsReconnectInterval = null;

    // Chart instances
    const charts = {
        predictions: null,
        network: null,
        ciPerformance: null,
        cognitiveComplexity: null,
        problemSolving: null
    };

    // Initialize WebSocket connection
    function initializeWebSocket() {
        const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
        
        ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log('WebSocket connected for analytics');
            clearInterval(wsReconnectInterval);
            
            // Subscribe to relevant events
            ws.send(JSON.stringify({
                type: 'subscribe',
                event_types: ['pattern_detected', 'complex_event', 'prediction_update', 'ci_update']
            }));
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        ws.onclose = () => {
            console.log('WebSocket disconnected');
            // Attempt to reconnect every 5 seconds
            wsReconnectInterval = setInterval(() => {
                initializeWebSocket();
            }, 5000);
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    // Handle WebSocket messages
    function handleWebSocketMessage(data) {
        switch (data.type) {
            case 'pattern_detected':
                updatePatternResults(data.pattern);
                break;
            case 'complex_event':
                addComplexEvent(data.event);
                break;
            case 'prediction_update':
                updatePredictionChart(data.predictions);
                break;
            case 'ci_update':
                updateCollectiveIntelligenceMetrics(data.metrics);
                break;
        }
    }

    // Analytics Type Change Handler
    function handleAnalyticsTypeChange() {
        const type = document.getElementById('sophia-analytics-type').value;
        
        // Hide all sections
        document.querySelectorAll('.sophia-analytics-section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show selected section
        switch (type) {
            case 'patterns':
                document.getElementById('sophia-patterns-section').style.display = 'block';
                break;
            case 'causality':
                document.getElementById('sophia-causality-section').style.display = 'block';
                loadAvailableMetrics();
                break;
            case 'events':
                document.getElementById('sophia-events-section').style.display = 'block';
                break;
            case 'predictions':
                document.getElementById('sophia-predictions-section').style.display = 'block';
                loadPredictableMetrics();
                break;
            case 'network':
                document.getElementById('sophia-network-section').style.display = 'block';
                break;
        }
    }

    // Run Analysis
    async function runAnalysis() {
        const type = document.getElementById('sophia-analytics-type').value;
        const timeWindow = document.getElementById('sophia-analytics-timewindow').value;
        
        switch (type) {
            case 'patterns':
                await runPatternDetection(timeWindow);
                break;
            case 'causality':
                await runCausalAnalysis(timeWindow);
                break;
            case 'events':
                await runEventDetection(timeWindow);
                break;
            case 'predictions':
                await runPredictions();
                break;
            case 'network':
                await runNetworkAnalysis(timeWindow);
                break;
        }
    }

    // Pattern Detection
    async function runPatternDetection(timeWindow) {
        const dimensions = Array.from(
            document.getElementById('sophia-pattern-dimensions').selectedOptions
        ).map(opt => opt.value);
        
        try {
            const response = await fetch('/api/v1/analytics/patterns/detect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    dimensions,
                    time_window: timeWindow
                })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                displayPatternResults(result.patterns);
            }
        } catch (error) {
            console.error('Error detecting patterns:', error);
            showError('Failed to detect patterns');
        }
    }

    // Display Pattern Results
    function displayPatternResults(patterns) {
        const container = document.getElementById('sophia-pattern-results');
        container.innerHTML = '';
        
        if (patterns.length === 0) {
            container.innerHTML = '<p class="text-muted">No patterns detected</p>';
            return;
        }
        
        patterns.forEach(pattern => {
            const card = document.createElement('div');
            card.className = 'pattern-card';
            card.innerHTML = `
                <div class="pattern-header">
                    <span class="pattern-type">${pattern.pattern_type}</span>
                    <span class="pattern-confidence">${(pattern.confidence * 100).toFixed(1)}% confidence</span>
                </div>
                <div class="pattern-description">${pattern.description}</div>
                <div class="pattern-details">
                    ${Object.entries(pattern.parameters || {}).map(([key, value]) =>
                        `<div class="pattern-param"><strong>${key}:</strong> ${JSON.stringify(value)}</div>`
                    ).join('')}
                </div>
            `;
            container.appendChild(card);
        });
    }

    // Causal Analysis
    async function runCausalAnalysis(timeWindow) {
        const targetMetric = document.getElementById('sophia-causality-target').value;
        const candidateCauses = Array.from(
            document.getElementById('sophia-causality-candidates').selectedOptions
        ).map(opt => opt.value);
        const maxLag = parseInt(document.getElementById('sophia-causality-lag').value);
        
        if (!targetMetric || candidateCauses.length === 0) {
            showError('Please select target metric and candidate causes');
            return;
        }
        
        try {
            const response = await fetch('/api/v1/analytics/causality/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    target_metric: targetMetric,
                    candidate_causes: candidateCauses,
                    time_window: timeWindow,
                    max_lag: maxLag
                })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                displayCausalRelationships(result.relationships);
            }
        } catch (error) {
            console.error('Error analyzing causality:', error);
            showError('Failed to analyze causal relationships');
        }
    }

    // Display Causal Relationships
    function displayCausalRelationships(relationships) {
        const container = document.getElementById('sophia-causality-results');
        container.innerHTML = '';
        
        if (relationships.length === 0) {
            container.innerHTML = '<p class="text-muted">No causal relationships detected</p>';
            return;
        }
        
        // Create causal graph visualization
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '300');
        
        relationships.forEach((rel, index) => {
            const y = 50 + index * 60;
            
            // Draw arrow
            const arrow = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            arrow.setAttribute('x1', '50');
            arrow.setAttribute('y1', y);
            arrow.setAttribute('x2', '250');
            arrow.setAttribute('y2', y);
            arrow.setAttribute('stroke', '#007bff');
            arrow.setAttribute('stroke-width', 2 * rel.strength);
            arrow.setAttribute('marker-end', 'url(#arrowhead)');
            svg.appendChild(arrow);
            
            // Cause label
            const causeText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            causeText.setAttribute('x', '40');
            causeText.setAttribute('y', y + 5);
            causeText.setAttribute('text-anchor', 'end');
            causeText.textContent = rel.cause;
            svg.appendChild(causeText);
            
            // Effect label
            const effectText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            effectText.setAttribute('x', '260');
            effectText.setAttribute('y', y + 5);
            effectText.textContent = rel.effect;
            svg.appendChild(effectText);
            
            // Lag label
            const lagText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            lagText.setAttribute('x', '150');
            lagText.setAttribute('y', y - 10);
            lagText.setAttribute('text-anchor', 'middle');
            lagText.setAttribute('font-size', '12');
            lagText.textContent = `Lag: ${rel.lag}`;
            svg.appendChild(lagText);
        });
        
        container.appendChild(svg);
        
        // Add details table
        const table = document.createElement('table');
        table.className = 'table table-sm mt-3';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Cause</th>
                    <th>Effect</th>
                    <th>Strength</th>
                    <th>Lag</th>
                    <th>Confidence</th>
                    <th>Mechanism</th>
                </tr>
            </thead>
            <tbody>
                ${relationships.map(rel => `
                    <tr>
                        <td>${rel.cause}</td>
                        <td>${rel.effect}</td>
                        <td>${(rel.strength * 100).toFixed(1)}%</td>
                        <td>${rel.lag}</td>
                        <td>${(rel.confidence * 100).toFixed(1)}%</td>
                        <td>${rel.mechanism}</td>
                    </tr>
                `).join('')}
            </tbody>
        `;
        container.appendChild(table);
    }

    // Complex Event Detection
    async function runEventDetection(timeWindow) {
        const eventTypes = Array.from(
            document.getElementById('sophia-event-types').selectedOptions
        ).map(opt => opt.value);
        
        try {
            const response = await fetch('/api/v1/analytics/events/detect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    event_types: eventTypes.length > 0 ? eventTypes : null,
                    time_window: timeWindow
                })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                displayComplexEvents(result.events);
            }
        } catch (error) {
            console.error('Error detecting events:', error);
            showError('Failed to detect complex events');
        }
    }

    // Display Complex Events
    function displayComplexEvents(events) {
        const timeline = document.getElementById('sophia-events-timeline');
        const results = document.getElementById('sophia-events-results');
        
        timeline.innerHTML = '';
        results.innerHTML = '';
        
        if (events.length === 0) {
            timeline.innerHTML = '<p class="text-muted">No complex events detected</p>';
            return;
        }
        
        // Create timeline visualization
        const timelineDiv = document.createElement('div');
        timelineDiv.className = 'event-timeline';
        
        events.forEach(event => {
            const eventMarker = document.createElement('div');
            eventMarker.className = `event-marker event-${event.event_type}`;
            eventMarker.style.left = calculateTimelinePosition(event.start_time) + '%';
            eventMarker.title = event.event_type;
            eventMarker.onclick = () => showEventDetails(event);
            timelineDiv.appendChild(eventMarker);
        });
        
        timeline.appendChild(timelineDiv);
        
        // Show first event details
        if (events.length > 0) {
            showEventDetails(events[0]);
        }
    }

    // Show Event Details
    function showEventDetails(event) {
        const results = document.getElementById('sophia-events-results');
        
        results.innerHTML = `
            <div class="event-detail">
                <h4>${event.event_type}</h4>
                <div class="event-info">
                    <div><strong>Start:</strong> ${new Date(event.start_time).toLocaleString()}</div>
                    <div><strong>End:</strong> ${new Date(event.end_time).toLocaleString()}</div>
                    <div><strong>Magnitude:</strong> ${event.magnitude.toFixed(2)}</div>
                    <div><strong>Components:</strong> ${event.components.join(', ')}</div>
                    <div><strong>Metrics:</strong> ${event.metrics.join(', ')}</div>
                </div>
                <div class="cascading-effects">
                    <h5>Cascading Effects</h5>
                    ${event.cascading_effects.map(effect => 
                        `<div class="effect">${JSON.stringify(effect)}</div>`
                    ).join('')}
                </div>
            </div>
        `;
    }

    // Predictions
    async function runPredictions() {
        const metrics = Array.from(
            document.getElementById('sophia-prediction-metrics').selectedOptions
        ).map(opt => opt.value);
        const horizon = parseInt(document.getElementById('sophia-prediction-horizon').value);
        const confidence = parseFloat(document.getElementById('sophia-prediction-confidence').value);
        
        if (metrics.length === 0) {
            showError('Please select metrics to predict');
            return;
        }
        
        try {
            const response = await fetch('/api/v1/analytics/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    metric_ids: metrics,
                    prediction_horizon: horizon,
                    confidence_level: confidence
                })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                displayPredictions(result.predictions, horizon, confidence);
            }
        } catch (error) {
            console.error('Error generating predictions:', error);
            showError('Failed to generate predictions');
        }
    }

    // Display Predictions
    function displayPredictions(predictions, horizon, confidence) {
        const container = document.getElementById('sophia-predictions-chart');
        
        // Prepare data for chart
        const datasets = [];
        
        Object.entries(predictions).forEach(([metric, data]) => {
            if (data.predictions && data.predictions.length > 0) {
                // Prediction line
                datasets.push({
                    label: `${metric} (Predicted)`,
                    data: data.predictions,
                    borderColor: 'rgb(75, 192, 192)',
                    borderDash: [5, 5],
                    fill: false
                });
                
                // Confidence intervals
                if (data.confidence_intervals) {
                    datasets.push({
                        label: `${metric} (${(confidence * 100)}% CI)`,
                        data: data.confidence_intervals.map(ci => ci[1]),
                        borderColor: 'rgba(75, 192, 192, 0.3)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        fill: '+1'
                    });
                    
                    datasets.push({
                        label: `${metric} (Lower CI)`,
                        data: data.confidence_intervals.map(ci => ci[0]),
                        borderColor: 'rgba(75, 192, 192, 0.3)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        fill: false,
                        showLine: true
                    });
                }
            }
        });
        
        // Create or update chart
        const ctx = container.getContext('2d');
        
        if (charts.predictions) {
            charts.predictions.destroy();
        }
        
        charts.predictions = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array.from({ length: horizon }, (_, i) => `+${i + 1}h`),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Metric Predictions'
                    },
                    legend: {
                        display: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }

    // Network Analysis
    async function runNetworkAnalysis(timeWindow) {
        try {
            const response = await fetch('/api/v1/analytics/network/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    time_window: timeWindow
                })
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                displayNetworkAnalysis(result.analysis);
            }
        } catch (error) {
            console.error('Error analyzing network:', error);
            showError('Failed to analyze network effects');
        }
    }

    // Display Network Analysis
    function displayNetworkAnalysis(analysis) {
        // Display network visualization
        const vizContainer = document.getElementById('sophia-network-visualization');
        vizContainer.innerHTML = '<p class="text-muted">Network visualization would be rendered here using D3.js or similar</p>';
        
        // Display metrics
        const metricsContainer = document.getElementById('sophia-network-metrics');
        metricsContainer.innerHTML = `
            <div class="network-metrics">
                <h4>Network Metrics</h4>
                <div class="metrics-grid">
                    <div class="metric">
                        <h5>Centrality</h5>
                        ${Object.entries(analysis.centrality || {}).map(([type, values]) => `
                            <div class="centrality-type">
                                <strong>${type}:</strong>
                                <ul>
                                    ${Object.entries(values).slice(0, 5).map(([node, value]) =>
                                        `<li>${node}: ${value.toFixed(3)}</li>`
                                    ).join('')}
                                </ul>
                            </div>
                        `).join('')}
                    </div>
                    <div class="metric">
                        <h5>Path Analysis</h5>
                        <div>Average Shortest Path: ${analysis.paths?.average_shortest_path?.toFixed(2) || 'N/A'}</div>
                        <div>Diameter: ${analysis.paths?.diameter || 'N/A'}</div>
                    </div>
                    <div class="metric">
                        <h5>Flow Analysis</h5>
                        <div>Bottlenecks: ${(analysis.flow?.bottlenecks || []).join(', ') || 'None'}</div>
                    </div>
                </div>
            </div>
        `;
    }

    // Collective Intelligence View Mode Change
    function handleCIViewModeChange() {
        const mode = document.getElementById('sophia-ci-view-mode').value;
        
        // Hide all sections
        document.querySelectorAll('.sophia-ci-section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show selected section
        switch (mode) {
            case 'chorus':
                document.getElementById('sophia-chorus-section').style.display = 'block';
                loadGreekChorusData();
                break;
            case 'test-taker':
                document.getElementById('sophia-test-taker-section').style.display = 'block';
                loadTestTakerData();
                break;
            case 'performance':
                document.getElementById('sophia-ci-performance-section').style.display = 'block';
                loadCIPerformanceData();
                break;
            case 'evolution':
                document.getElementById('sophia-ci-evolution-section').style.display = 'block';
                loadEvolutionData();
                break;
        }
    }

    // Load Available Metrics
    async function loadAvailableMetrics() {
        try {
            const response = await fetch('/api/v1/metrics/definitions');
            const result = await response.json();
            
            if (result.status === 'success') {
                const targetSelect = document.getElementById('sophia-causality-target');
                const candidatesSelect = document.getElementById('sophia-causality-candidates');
                const predictionSelect = document.getElementById('sophia-prediction-metrics');
                
                // Clear existing options
                targetSelect.innerHTML = '<option value="">Select target metric...</option>';
                candidatesSelect.innerHTML = '';
                predictionSelect.innerHTML = '';
                
                // Add metric options
                result.data.forEach(metric => {
                    const option = new Option(metric.name, metric.metric_id);
                    targetSelect.add(option.cloneNode(true));
                    candidatesSelect.add(option.cloneNode(true));
                    predictionSelect.add(option.cloneNode(true));
                });
            }
        } catch (error) {
            console.error('Error loading metrics:', error);
        }
    }

    // Utility Functions
    function calculateTimelinePosition(timestamp) {
        // Simple linear mapping for demo
        const date = new Date(timestamp);
        const now = new Date();
        const hourAgo = new Date(now - 3600000);
        
        const position = ((date - hourAgo) / (now - hourAgo)) * 100;
        return Math.max(0, Math.min(100, position));
    }

    function showError(message) {
        // Would show error notification
        console.error(message);
    }

    // Initialize when document is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Set up event listeners
        const analyticsType = document.getElementById('sophia-analytics-type');
        if (analyticsType) {
            analyticsType.addEventListener('change', handleAnalyticsTypeChange);
        }
        
        const runButton = document.getElementById('sophia-analytics-run-btn');
        if (runButton) {
            runButton.addEventListener('click', runAnalysis);
        }
        
        const ciViewMode = document.getElementById('sophia-ci-view-mode');
        if (ciViewMode) {
            ciViewMode.addEventListener('change', handleCIViewModeChange);
        }
        
        // Initialize WebSocket
        initializeWebSocket();
        
        // Load initial data
        loadAvailableMetrics();
    });

    // Export for external use
    window.SophiaAnalytics = {
        runAnalysis,
        handleWebSocketMessage
    };
})();