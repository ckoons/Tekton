/**
 * Confidence Tracker - Apollo Prediction Confidence Monitoring
 * Tracks prediction accuracy, calibration, and confidence trends
 */

class ConfidenceTracker {
    constructor() {
        // MCP endpoint
        this.mcpEndpoint = window.hephaestusUrl ? window.hephaestusUrl('/api/mcp/v2/execute').replace(':8080', ':8088') : 'http://localhost:8088/api/mcp/v2/execute';
        
        // Confidence data
        this.overallConfidence = 0;
        this.categories = {
            intent: 0,
            action: 0,
            timing: 0,
            pattern: 0
        };
        this.predictions = [];
        this.calibrationData = [];
        this.trends = {
            improving: 0,
            stable: 0,
            declining: 0,
            variance: 0
        };
        
        // Chart context
        this.chartContext = null;
        
        // Initialize
        this.init();
    }
    
    async init() {
        console.log('[ConfidenceTracker] Initializing prediction confidence tracking...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Initialize chart
        this.initCalibrationChart();
        
        // Load initial data
        await this.loadConfidenceData();
        
        // Start periodic updates
        this.startPolling();
    }
    
    setupEventListeners() {
        // Timeframe selector
        const timeframe = document.getElementById('confidence-timeframe');
        if (timeframe) {
            timeframe.addEventListener('change', (e) => this.changeTimeframe(e.target.value));
        }
        
        // Refresh button
        const refreshBtn = document.getElementById('refresh-confidence');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadConfidenceData());
        }
    }
    
    initCalibrationChart() {
        const canvas = document.getElementById('calibration-canvas');
        if (canvas && canvas.getContext) {
            this.chartContext = canvas.getContext('2d');
            this.drawCalibrationChart();
        }
    }
    
    async loadConfidenceData() {
        console.log('[ConfidenceTracker] Loading confidence data...');
        
        // Show loading state
        this.setLoadingState(true);
        
        try {
            // Fetch confidence data using MCP tools
            const [predictionData, behaviorData, memoryData] = await Promise.all([
                this.fetchPredictionHistory(),
                this.fetchBehaviorAnalysis(),
                this.fetchMemoryInsights()
            ]);
            
            // Process and combine data
            this.processConfidenceData(predictionData, behaviorData, memoryData);
            
            // Update UI
            this.updateConfidenceDisplay();
            this.updateCategoryBreakdown();
            this.updateRecentPredictions();
            this.updateTrends();
            this.drawCalibrationChart();
            
        } catch (error) {
            console.error('[ConfidenceTracker] Error loading confidence data:', error);
            this.showError('Failed to load confidence data');
        } finally {
            this.setLoadingState(false);
        }
    }
    
    async fetchPredictionHistory() {
        try {
            // Use PredictionConfidence MCP tool
            const response = await this.callMCPTool('PredictionConfidence', {
                ci_name: 'apollo',
                timeframe: this.getTimeframe()
            });
            
            if (response.success && response.predictions) {
                return response.predictions;
            }
            
            // Fallback to mock data for demo
            return this.getMockPredictionData();
        } catch (error) {
            console.error('[ConfidenceTracker] Error fetching predictions:', error);
            return this.getMockPredictionData();
        }
    }
    
    async fetchBehaviorAnalysis() {
        try {
            // Use BehaviorPattern MCP tool for Apollo's behavior
            const response = await this.callMCPTool('BehaviorPattern', {
                ci_name: 'apollo',
                pattern_window: 7,
                pattern_threshold: 0.2
            });
            
            if (response.success && response.behavior_patterns) {
                return response.behavior_patterns;
            }
            
            return {};
        } catch (error) {
            console.error('[ConfidenceTracker] Error fetching behavior analysis:', error);
            return {};
        }
    }
    
    async fetchMemoryInsights() {
        try {
            // Use MemoryPattern MCP tool for prediction patterns
            const response = await this.callMCPTool('MemoryPattern', {
                query: 'prediction confidence accuracy calibration',
                pattern_type: 'analytical',
                min_occurrences: 2
            });
            
            if (response.success && response.patterns) {
                return response.patterns;
            }
            
            return [];
        } catch (error) {
            console.error('[ConfidenceTracker] Error fetching memory insights:', error);
            return [];
        }
    }
    
    processConfidenceData(predictions, behavior, memory) {
        // Calculate overall confidence
        this.calculateOverallConfidence(predictions);
        
        // Calculate category breakdowns
        this.calculateCategoryConfidence(predictions);
        
        // Process recent predictions
        this.processRecentPredictions(predictions);
        
        // Calculate calibration data
        this.calculateCalibration(predictions);
        
        // Analyze trends
        this.analyzeTrends(predictions, behavior, memory);
    }
    
    calculateOverallConfidence(predictions) {
        if (!predictions || predictions.length === 0) {
            this.overallConfidence = 0;
            return;
        }
        
        // Calculate weighted average of prediction confidence
        let totalConfidence = 0;
        let totalWeight = 0;
        
        predictions.forEach(pred => {
            const confidence = pred.confidence || 0;
            const weight = pred.importance || 1;
            totalConfidence += confidence * weight;
            totalWeight += weight;
        });
        
        this.overallConfidence = totalWeight > 0 ? 
            Math.round((totalConfidence / totalWeight) * 100) : 0;
    }
    
    calculateCategoryConfidence(predictions) {
        const categories = {
            intent: [],
            action: [],
            timing: [],
            pattern: []
        };
        
        if (predictions) {
            predictions.forEach(pred => {
                const category = pred.category || 'pattern';
                if (categories[category]) {
                    categories[category].push(pred.confidence || 0);
                }
            });
        }
        
        // Calculate average for each category
        Object.keys(categories).forEach(cat => {
            const values = categories[cat];
            if (values.length > 0) {
                const avg = values.reduce((a, b) => a + b, 0) / values.length;
                this.categories[cat] = Math.round(avg * 100);
            } else {
                this.categories[cat] = Math.round(Math.random() * 30 + 60); // Demo fallback
            }
        });
    }
    
    processRecentPredictions(predictions) {
        if (!predictions) {
            this.predictions = this.getMockRecentPredictions();
            return;
        }
        
        // Sort by timestamp and take recent ones
        this.predictions = predictions
            .sort((a, b) => new Date(b.timestamp || Date.now()) - new Date(a.timestamp || Date.now()))
            .slice(0, 10)
            .map(pred => ({
                id: pred.id,
                text: pred.description || pred.text || 'Prediction',
                confidence: Math.round((pred.confidence || 0) * 100),
                timestamp: pred.timestamp || new Date(),
                outcome: pred.outcome || 'pending'
            }));
    }
    
    calculateCalibration(predictions) {
        // Group predictions by confidence buckets
        const buckets = {};
        for (let i = 0; i <= 100; i += 10) {
            buckets[i] = { predicted: [], actual: [] };
        }
        
        if (predictions) {
            predictions.forEach(pred => {
                if (pred.outcome && pred.outcome !== 'pending') {
                    const confidence = Math.round((pred.confidence || 0) * 100);
                    const bucket = Math.floor(confidence / 10) * 10;
                    buckets[bucket].predicted.push(confidence);
                    buckets[bucket].actual.push(pred.outcome === 'success' ? 100 : 0);
                }
            });
        }
        
        // Calculate calibration points
        this.calibrationData = [];
        Object.keys(buckets).forEach(bucket => {
            const data = buckets[bucket];
            if (data.predicted.length > 0) {
                const avgPredicted = data.predicted.reduce((a, b) => a + b, 0) / data.predicted.length;
                const avgActual = data.actual.reduce((a, b) => a + b, 0) / data.actual.length;
                this.calibrationData.push({
                    predicted: avgPredicted,
                    actual: avgActual,
                    count: data.predicted.length
                });
            }
        });
        
        // Add demo calibration data if empty
        if (this.calibrationData.length === 0) {
            this.calibrationData = this.getMockCalibrationData();
        }
    }
    
    analyzeTrends(predictions, behavior, memory) {
        // Reset trend counts
        this.trends = { improving: 0, stable: 0, declining: 0, variance: 0 };
        
        if (!predictions || predictions.length < 2) {
            // Demo values
            this.trends = { improving: 3, stable: 5, declining: 1, variance: 2 };
            return;
        }
        
        // Analyze trend for each prediction type
        const typeGroups = {};
        predictions.forEach(pred => {
            const type = pred.type || 'general';
            if (!typeGroups[type]) typeGroups[type] = [];
            typeGroups[type].push(pred.confidence || 0);
        });
        
        Object.values(typeGroups).forEach(group => {
            if (group.length >= 2) {
                const trend = this.calculateTrend(group);
                this.trends[trend]++;
            }
        });
    }
    
    calculateTrend(values) {
        if (values.length < 2) return 'stable';
        
        // Calculate slope
        let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
        values.forEach((y, x) => {
            sumX += x;
            sumY += y;
            sumXY += x * y;
            sumX2 += x * x;
        });
        
        const n = values.length;
        const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        
        // Calculate variance
        const mean = sumY / n;
        const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / n;
        
        // Classify trend
        if (variance > 0.1) return 'variance';
        if (slope > 0.01) return 'improving';
        if (slope < -0.01) return 'declining';
        return 'stable';
    }
    
    updateConfidenceDisplay() {
        // Update overall confidence
        const valueEl = document.getElementById('confidence-value');
        const statusEl = document.getElementById('confidence-status');
        const circleEl = document.getElementById('confidence-circle');
        
        if (valueEl) {
            valueEl.textContent = this.overallConfidence;
        }
        
        if (statusEl) {
            if (this.overallConfidence >= 80) {
                statusEl.textContent = 'High Confidence';
                statusEl.style.color = '#4CAF50';
            } else if (this.overallConfidence >= 60) {
                statusEl.textContent = 'Moderate Confidence';
                statusEl.style.color = '#FFC107';
            } else {
                statusEl.textContent = 'Low Confidence';
                statusEl.style.color = '#F44336';
            }
        }
        
        if (circleEl) {
            // Update SVG circle progress
            const circumference = 2 * Math.PI * 90; // radius = 90
            const offset = circumference - (this.overallConfidence / 100) * circumference;
            circleEl.style.strokeDashoffset = offset;
        }
    }
    
    updateCategoryBreakdown() {
        // Update each category
        Object.keys(this.categories).forEach(category => {
            const score = this.categories[category];
            const scoreEl = document.getElementById(`${category}-score`);
            const fillEl = document.getElementById(`${category}-fill`);
            
            if (scoreEl) {
                scoreEl.textContent = `${score}%`;
            }
            
            if (fillEl) {
                fillEl.style.width = `${score}%`;
            }
        });
    }
    
    updateRecentPredictions() {
        const listEl = document.getElementById('predictions-list');
        if (!listEl) return;
        
        listEl.innerHTML = '';
        
        if (this.predictions.length === 0) {
            listEl.innerHTML = `
                <div class="apollo__prediction-item">
                    <div class="apollo__prediction-content">
                        <span class="apollo__prediction-text">No recent predictions available</span>
                    </div>
                </div>
            `;
            return;
        }
        
        this.predictions.forEach(pred => {
            const item = document.createElement('div');
            item.className = 'apollo__prediction-item';
            
            const time = this.formatTime(pred.timestamp);
            const outcomeClass = `apollo__prediction-outcome--${pred.outcome}`;
            const outcomeText = pred.outcome === 'success' ? '✓ Correct' : 
                               pred.outcome === 'failed' ? '✗ Incorrect' : '⏳ Pending';
            
            item.innerHTML = `
                <div class="apollo__prediction-time">${time}</div>
                <div class="apollo__prediction-content">
                    <span class="apollo__prediction-text">${pred.text}</span>
                    <span class="apollo__prediction-confidence">${pred.confidence}%</span>
                    <span class="apollo__prediction-outcome ${outcomeClass}">${outcomeText}</span>
                </div>
            `;
            
            listEl.appendChild(item);
        });
    }
    
    updateTrends() {
        // Update trend values
        Object.keys(this.trends).forEach(trend => {
            const el = document.getElementById(`${trend}-count`);
            if (el) {
                el.textContent = this.trends[trend];
            }
        });
    }
    
    drawCalibrationChart() {
        if (!this.chartContext) return;
        
        const ctx = this.chartContext;
        const canvas = ctx.canvas;
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Set up chart dimensions
        const padding = 40;
        const chartWidth = width - 2 * padding;
        const chartHeight = height - 2 * padding;
        
        // Draw axes
        ctx.strokeStyle = '#ddd';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.stroke();
        
        // Draw perfect calibration line (diagonal)
        ctx.strokeStyle = '#e0e0e0';
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(padding, height - padding);
        ctx.lineTo(width - padding, padding);
        ctx.stroke();
        ctx.setLineDash([]);
        
        // Draw calibration data points
        if (this.calibrationData.length > 0) {
            ctx.fillStyle = '#2196F3';
            ctx.strokeStyle = '#2196F3';
            ctx.lineWidth = 2;
            
            ctx.beginPath();
            this.calibrationData.forEach((point, index) => {
                const x = padding + (point.predicted / 100) * chartWidth;
                const y = height - padding - (point.actual / 100) * chartHeight;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
                
                // Draw point
                ctx.fillRect(x - 3, y - 3, 6, 6);
            });
            ctx.stroke();
        }
        
        // Draw labels
        ctx.fillStyle = '#666';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Predicted Confidence (%)', width / 2, height - 10);
        
        ctx.save();
        ctx.translate(10, height / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText('Actual Accuracy (%)', 0, 0);
        ctx.restore();
        
        // Draw axis labels
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        for (let i = 0; i <= 100; i += 20) {
            const y = height - padding - (i / 100) * chartHeight;
            ctx.fillText(i, padding - 5, y);
        }
        
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        for (let i = 0; i <= 100; i += 20) {
            const x = padding + (i / 100) * chartWidth;
            ctx.fillText(i, x, height - padding + 5);
        }
    }
    
    formatTime(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diff = now - time;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return time.toLocaleDateString();
    }
    
    changeTimeframe(timeframe) {
        console.log('[ConfidenceTracker] Changing timeframe to:', timeframe);
        this.loadConfidenceData();
    }
    
    getTimeframe() {
        const select = document.getElementById('confidence-timeframe');
        return select ? select.value : '24h';
    }
    
    setLoadingState(loading) {
        const container = document.querySelector('.apollo__confidence');
        if (container) {
            if (loading) {
                container.classList.add('apollo__confidence--loading');
            } else {
                container.classList.remove('apollo__confidence--loading');
            }
        }
    }
    
    showError(message) {
        console.error('[ConfidenceTracker]', message);
        // Could show user-friendly error message
    }
    
    startPolling() {
        // Refresh data every 30 seconds
        setInterval(() => {
            this.loadConfidenceData();
        }, 30000);
    }
    
    async callMCPTool(toolName, params) {
        const response = await fetch(this.mcpEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tool: toolName,
                parameters: params
            })
        });
        
        if (!response.ok) {
            throw new Error(`MCP tool ${toolName} failed: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    // Mock data methods for demo
    getMockPredictionData() {
        const predictions = [];
        const categories = ['intent', 'action', 'timing', 'pattern'];
        const outcomes = ['success', 'success', 'success', 'failed', 'pending'];
        
        for (let i = 0; i < 50; i++) {
            predictions.push({
                id: `pred-${i}`,
                category: categories[Math.floor(Math.random() * categories.length)],
                confidence: 0.5 + Math.random() * 0.5,
                importance: Math.random(),
                timestamp: new Date(Date.now() - Math.random() * 86400000),
                outcome: outcomes[Math.floor(Math.random() * outcomes.length)],
                description: `Predicted ${['user action', 'system event', 'pattern emergence', 'timing window'][Math.floor(Math.random() * 4)]}`
            });
        }
        
        return predictions;
    }
    
    getMockRecentPredictions() {
        return [
            {
                text: 'User will request memory optimization',
                confidence: 85,
                timestamp: new Date(Date.now() - 300000),
                outcome: 'success'
            },
            {
                text: 'Next CI activation: Numa at 14:30',
                confidence: 92,
                timestamp: new Date(Date.now() - 900000),
                outcome: 'success'
            },
            {
                text: 'Pattern detected: increased whisper activity',
                confidence: 78,
                timestamp: new Date(Date.now() - 1800000),
                outcome: 'pending'
            },
            {
                text: 'Predicted stress spike in 5 minutes',
                confidence: 67,
                timestamp: new Date(Date.now() - 3600000),
                outcome: 'failed'
            },
            {
                text: 'Apollo-Rhetor synchronization needed',
                confidence: 88,
                timestamp: new Date(Date.now() - 7200000),
                outcome: 'success'
            }
        ];
    }
    
    getMockCalibrationData() {
        return [
            { predicted: 10, actual: 12, count: 5 },
            { predicted: 20, actual: 18, count: 8 },
            { predicted: 30, actual: 35, count: 12 },
            { predicted: 40, actual: 38, count: 15 },
            { predicted: 50, actual: 52, count: 20 },
            { predicted: 60, actual: 58, count: 18 },
            { predicted: 70, actual: 72, count: 16 },
            { predicted: 80, actual: 78, count: 14 },
            { predicted: 90, actual: 88, count: 10 }
        ];
    }
}

// Initialize Confidence Tracker when Confidence tab is selected
document.addEventListener('DOMContentLoaded', () => {
    const confidenceTab = document.getElementById('apollo-tab-confidence');
    if (confidenceTab) {
        confidenceTab.addEventListener('change', () => {
            if (confidenceTab.checked && !window.confidenceTracker) {
                window.confidenceTracker = new ConfidenceTracker();
            }
        });
        
        // Initialize if Confidence tab is already selected
        if (confidenceTab.checked) {
            window.confidenceTracker = new ConfidenceTracker();
        }
    }
});