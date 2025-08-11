/**
 * Tekton Event Bus - Unified backend integration for all UI components
 * Connects Engram, Rhetor, and Apollo through WebSockets and REST APIs
 */

class TektonEventBus {
    constructor() {
        this.sockets = {};
        this.subscribers = {};
        this.reconnectIntervals = {};
        
        // Build component configurations using tektonUrl
        // Use proper port numbers from env.js
        this.config = {
            engram: {
                wsUrl: this.buildWebSocketUrl('engram', '/ws/ui'),
                apiUrl: tektonUrl('engram', '/api'),
                reconnectDelay: 3000
            },
            rhetor: {
                wsUrl: this.buildWebSocketUrl('rhetor', '/ws/prompts'),
                apiUrl: tektonUrl('rhetor', '/api'),
                reconnectDelay: 3000
            },
            apollo: {
                wsUrl: this.buildWebSocketUrl('apollo', '/ws/patterns'),
                apiUrl: tektonUrl('apollo', '/api'),
                reconnectDelay: 3000
            }
        };
        
        console.log('[TektonEventBus] Configuration:', this.config);
        
        // Initialize connections
        this.initializeConnections();
        
        // Enable ambient intelligence (Apollo observes everything)
        this.enableAmbientIntelligence();
    }
    
    buildWebSocketUrl(component, path) {
        // Build WebSocket URL using tektonUrl with ws:// scheme
        const httpUrl = tektonUrl(component, path);
        // Convert http to ws, https to wss
        return httpUrl.replace(/^http/, 'ws');
    }
    
    initializeConnections() {
        Object.keys(this.config).forEach(component => {
            this.connectWebSocket(component);
        });
    }
    
    connectWebSocket(component) {
        const config = this.config[component];
        
        try {
            const socket = new WebSocket(config.wsUrl);
            
            socket.onopen = () => {
                console.log(`[TektonEventBus] Connected to ${component}`);
                this.sockets[component] = socket;
                
                // Clear reconnect interval if exists
                if (this.reconnectIntervals[component]) {
                    clearInterval(this.reconnectIntervals[component]);
                    delete this.reconnectIntervals[component];
                }
                
                // Subscribe to default events
                this.subscribeToDefaultEvents(component, socket);
                
                // Notify subscribers of connection
                this.emit(`${component}:connected`, { component });
            };
            
            socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(component, data);
                } catch (error) {
                    console.error(`[TektonEventBus] Error parsing message from ${component}:`, error);
                }
            };
            
            socket.onerror = (error) => {
                console.error(`[TektonEventBus] WebSocket error for ${component}:`, error);
                this.emit(`${component}:error`, { component, error });
            };
            
            socket.onclose = () => {
                console.log(`[TektonEventBus] Disconnected from ${component}`);
                delete this.sockets[component];
                this.emit(`${component}:disconnected`, { component });
                
                // Attempt reconnection
                this.scheduleReconnect(component);
            };
            
        } catch (error) {
            console.error(`[TektonEventBus] Failed to connect to ${component}:`, error);
            this.scheduleReconnect(component);
        }
    }
    
    scheduleReconnect(component) {
        if (this.reconnectIntervals[component]) return;
        
        const config = this.config[component];
        this.reconnectIntervals[component] = setInterval(() => {
            console.log(`[TektonEventBus] Attempting to reconnect to ${component}...`);
            this.connectWebSocket(component);
        }, config.reconnectDelay);
    }
    
    subscribeToDefaultEvents(component, socket) {
        const subscriptions = {
            engram: {
                action: 'subscribe',
                events: ['memory_stored', 'memory_recalled', 'pattern_detected', 'memory_consolidated']
            },
            rhetor: {
                action: 'subscribe',
                events: ['prompt_created', 'prompt_evolved', 'prompt_analyzed', 'template_updated']
            },
            apollo: {
                action: 'subscribe',
                events: ['pattern_detected', 'prediction_made', 'confidence_updated', 'whisper_received']
            }
        };
        
        if (subscriptions[component]) {
            socket.send(JSON.stringify(subscriptions[component]));
        }
    }
    
    handleMessage(component, data) {
        // Log for debugging
        console.log(`[TektonEventBus] Message from ${component}:`, data);
        
        // Emit component-specific event
        this.emit(`${component}:${data.type || 'message'}`, data);
        
        // Handle specific message types
        switch (component) {
            case 'engram':
                this.handleEngramMessage(data);
                break;
            case 'rhetor':
                this.handleRhetorMessage(data);
                break;
            case 'apollo':
                this.handleApolloMessage(data);
                break;
        }
    }
    
    handleEngramMessage(data) {
        switch (data.type) {
            case 'memory_stored':
                this.updateMemoryUI(data);
                // Apollo observes new memories
                this.sendToApollo({ action: 'analyze', memory: data });
                break;
            case 'pattern_detected':
                this.updatePatternUI(data);
                break;
            case 'memory_consolidated':
                this.updateConsolidationUI(data);
                break;
        }
    }
    
    handleRhetorMessage(data) {
        switch (data.type) {
            case 'prompt_evolved':
                this.updateEvolutionUI(data);
                break;
            case 'prompt_analyzed':
                this.updatePromptQualityUI(data);
                break;
            case 'template_updated':
                this.updateTemplateUI(data);
                break;
        }
    }
    
    handleApolloMessage(data) {
        switch (data.type) {
            case 'pattern_detected':
                if (data.confidence > 0.8) {
                    this.showGentleHint(data.suggestion);
                }
                break;
            case 'prediction_made':
                this.updatePredictionUI(data);
                break;
            case 'confidence_updated':
                this.updateConfidenceUI(data);
                break;
            case 'whisper_received':
                this.handleWhisper(data);
                break;
        }
    }
    
    enableAmbientIntelligence() {
        // Apollo observes Engram memory patterns
        this.on('engram:memory_stored', (data) => {
            this.sendToApollo({
                action: 'observe',
                source: 'engram',
                data: data
            });
        });
        
        // Apollo enhances Rhetor prompts
        this.on('rhetor:prompt_draft', (data) => {
            this.sendToApollo({
                action: 'enhance',
                source: 'rhetor',
                prompt: data
            });
        });
        
        // Rhetor learns from successful patterns
        this.on('apollo:pattern_detected', (data) => {
            if (data.type === 'success_pattern') {
                this.sendToRhetor({
                    action: 'learn',
                    pattern: data
                });
            }
        });
    }
    
    // UI Update Methods
    updateMemoryUI(data) {
        // Update memory count in Engram
        const countEl = document.querySelector('[data-tekton-widget="memory-count"]');
        if (countEl) {
            countEl.textContent = data.memory_count || '--';
        }
        
        // Update recent memories list
        const listEl = document.querySelector('[data-tekton-widget="recent-memories"]');
        if (listEl && data.latest_memory) {
            const memoryItem = document.createElement('div');
            memoryItem.className = 'memory-item';
            memoryItem.textContent = data.latest_memory.content;
            listEl.insertBefore(memoryItem, listEl.firstChild);
        }
    }
    
    updatePatternUI(data) {
        // Update Pattern Detective
        if (window.patternDetective) {
            window.patternDetective.addPattern(data.pattern);
        }
    }
    
    updateEvolutionUI(data) {
        // Update Evolution Tracker
        if (window.evolutionTracker) {
            window.evolutionTracker.addEvolution(data);
        }
    }
    
    updateConfidenceUI(data) {
        // Update Apollo confidence meters
        if (data.overall_confidence !== undefined) {
            const valueEl = document.getElementById('confidence-value');
            if (valueEl) {
                valueEl.textContent = Math.round(data.overall_confidence * 100);
            }
            
            const circleEl = document.getElementById('confidence-circle');
            if (circleEl) {
                const circumference = 2 * Math.PI * 90;
                const offset = circumference - (data.overall_confidence * circumference);
                circleEl.style.strokeDashoffset = offset;
            }
        }
        
        // Update category confidence
        if (data.categories) {
            Object.keys(data.categories).forEach(category => {
                const score = Math.round(data.categories[category] * 100);
                const scoreEl = document.getElementById(`${category}-score`);
                const fillEl = document.getElementById(`${category}-fill`);
                
                if (scoreEl) scoreEl.textContent = `${score}%`;
                if (fillEl) fillEl.style.width = `${score}%`;
            });
        }
    }
    
    updatePredictionUI(data) {
        const listEl = document.getElementById('predictions-list');
        if (listEl && data.prediction) {
            const item = document.createElement('div');
            item.className = 'apollo__prediction-item';
            item.innerHTML = `
                <div class="apollo__prediction-time">Just now</div>
                <div class="apollo__prediction-content">
                    <span class="apollo__prediction-text">${data.prediction.text}</span>
                    <span class="apollo__prediction-confidence">${Math.round(data.prediction.confidence * 100)}%</span>
                </div>
            `;
            listEl.insertBefore(item, listEl.firstChild);
        }
    }
    
    handleWhisper(data) {
        // Update WhisperWidget if it exists
        if (window.whisperWidget) {
            window.whisperWidget.processWhispers([{
                id: Date.now(),
                from: data.from || 'Unknown',
                text: data.message,
                timestamp: new Date(),
                type: data.whisper_type || 'general'
            }]);
        }
    }
    
    showGentleHint(suggestion) {
        // Subtle UI hint from Apollo (95% observation, 4% gentle hints)
        const hint = document.createElement('div');
        hint.className = 'apollo-hint';
        hint.textContent = suggestion;
        hint.style.cssText = `
            position: fixed;
            bottom: 100px;
            right: 20px;
            background: linear-gradient(135deg, #FFD600 0%, #FFA000 100%);
            color: #0a0a0a;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 13px;
            opacity: 0;
            transition: opacity 0.5s ease;
            z-index: 1000;
        `;
        
        document.body.appendChild(hint);
        setTimeout(() => hint.style.opacity = '0.9', 100);
        setTimeout(() => {
            hint.style.opacity = '0';
            setTimeout(() => hint.remove(), 500);
        }, 5000);
    }
    
    // Message sending methods
    sendToEngram(message) {
        this.sendMessage('engram', message);
    }
    
    sendToRhetor(message) {
        this.sendMessage('rhetor', message);
    }
    
    sendToApollo(message) {
        this.sendMessage('apollo', message);
    }
    
    sendMessage(component, message) {
        if (this.sockets[component] && this.sockets[component].readyState === WebSocket.OPEN) {
            this.sockets[component].send(JSON.stringify(message));
        } else {
            console.warn(`[TektonEventBus] Cannot send message to ${component} - not connected`);
        }
    }
    
    // REST API methods
    async fetchFromAPI(component, endpoint, options = {}) {
        const url = `${this.config[component].apiUrl}${endpoint}`;
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            if (!response.ok) {
                throw new Error(`API request failed: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`[TektonEventBus] API error for ${component}:`, error);
            throw error;
        }
    }
    
    // Event emitter pattern
    on(event, callback) {
        if (!this.subscribers[event]) {
            this.subscribers[event] = [];
        }
        this.subscribers[event].push(callback);
    }
    
    off(event, callback) {
        if (this.subscribers[event]) {
            this.subscribers[event] = this.subscribers[event].filter(cb => cb !== callback);
        }
    }
    
    emit(event, data) {
        if (this.subscribers[event]) {
            this.subscribers[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`[TektonEventBus] Error in event handler for ${event}:`, error);
                }
            });
        }
    }
    
    // Cleanup
    destroy() {
        // Close all WebSocket connections
        Object.values(this.sockets).forEach(socket => {
            if (socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
        });
        
        // Clear all reconnect intervals
        Object.values(this.reconnectIntervals).forEach(interval => {
            clearInterval(interval);
        });
        
        this.sockets = {};
        this.reconnectIntervals = {};
        this.subscribers = {};
    }
}

// Initialize global event bus
window.tektonEventBus = new TektonEventBus();

// Auto-initialize components on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[TektonEventBus] Initializing UI components...');
    
    try {
        // Load initial state from REST APIs using proper URL system
        const [memories, templates, patterns] = await Promise.all([
            window.tektonEventBus.fetchFromAPI('engram', '/memories/recent?limit=5'),
            window.tektonEventBus.fetchFromAPI('rhetor', '/prompts/templates'),
            window.tektonEventBus.fetchFromAPI('apollo', '/patterns/active')
        ]).catch(error => {
            console.warn('[TektonEventBus] Using fallback data:', error);
            console.log('[TektonEventBus] Component URLs:', {
                engram: tektonUrl('engram', '/api'),
                rhetor: tektonUrl('rhetor', '/api'),
                apollo: tektonUrl('apollo', '/api')
            });
            return [null, null, null];
        });
        
        // Populate UI with initial state
        if (memories) populateMemories(memories);
        if (templates) populateTemplates(templates);
        if (patterns) populatePatterns(patterns);
        
    } catch (error) {
        console.error('[TektonEventBus] Failed to initialize:', error);
    }
});

// Helper functions for UI population
function populateMemories(memories) {
    console.log('[TektonEventBus] Populating memories:', memories);
    
    // Update memory count in Engram UI
    const countEl = document.querySelector('[data-tekton-widget="memory-count"]');
    if (countEl && memories.total_count !== undefined) {
        countEl.textContent = memories.total_count;
    }
    
    // Update recent memories list
    const listEl = document.querySelector('[data-tekton-widget="recent-memories"]');
    if (listEl && memories.items && Array.isArray(memories.items)) {
        // Clear existing items
        listEl.innerHTML = '';
        
        memories.items.forEach(memory => {
            const memoryItem = document.createElement('div');
            memoryItem.className = 'engram__memory-item';
            memoryItem.innerHTML = `
                <div class="engram__memory-timestamp">${new Date(memory.timestamp || Date.now()).toLocaleTimeString()}</div>
                <div class="engram__memory-content">${memory.content || memory.text || 'Memory stored'}</div>
                ${memory.category ? `<span class="engram__memory-category">${memory.category}</span>` : ''}
            `;
            listEl.appendChild(memoryItem);
        });
    }
    
    // Update memory consolidation status
    if (memories.consolidation_status) {
        const statusEl = document.querySelector('[data-tekton-widget="consolidation-status"]');
        if (statusEl) {
            statusEl.textContent = memories.consolidation_status;
            statusEl.className = `consolidation-status consolidation-status--${memories.consolidation_status.toLowerCase()}`;
        }
    }
}

function populateTemplates(templates) {
    console.log('[TektonEventBus] Populating templates:', templates);
    
    // Update template count in Rhetor UI
    const countEl = document.querySelector('[data-tekton-widget="template-count"]');
    if (countEl && templates.total_count !== undefined) {
        countEl.textContent = templates.total_count;
    }
    
    // Update template list
    const listEl = document.querySelector('[data-tekton-widget="template-list"]');
    if (listEl && templates.items && Array.isArray(templates.items)) {
        listEl.innerHTML = '';
        
        templates.items.forEach(template => {
            const templateItem = document.createElement('div');
            templateItem.className = 'rhetor__template-item';
            templateItem.innerHTML = `
                <div class="rhetor__template-header">
                    <span class="rhetor__template-name">${template.name || 'Unnamed Template'}</span>
                    <span class="rhetor__template-evolution">${template.evolution_count || 0} evolutions</span>
                </div>
                <div class="rhetor__template-preview">${template.preview || template.content || ''}</div>
                ${template.effectiveness ? `<div class="rhetor__template-effectiveness">Effectiveness: ${Math.round(template.effectiveness * 100)}%</div>` : ''}
            `;
            listEl.appendChild(templateItem);
        });
    }
    
    // Update evolution tracker if present
    if (window.evolutionTracker && templates.recent_evolutions) {
        templates.recent_evolutions.forEach(evolution => {
            window.evolutionTracker.addEvolution({
                id: evolution.id,
                prompt: evolution.prompt,
                quality_score: evolution.quality_score,
                timestamp: evolution.timestamp
            });
        });
    }
}

function populatePatterns(patterns) {
    console.log('[TektonEventBus] Populating patterns:', patterns);
    
    // Update pattern count
    const countEl = document.querySelector('[data-tekton-widget="pattern-count"]');
    if (countEl && patterns.total_count !== undefined) {
        countEl.textContent = patterns.total_count;
    }
    
    // Update Pattern Detective in Engram
    if (window.patternDetective && patterns.items && Array.isArray(patterns.items)) {
        patterns.items.forEach(pattern => {
            window.patternDetective.addPattern({
                id: pattern.id || Date.now(),
                type: pattern.type || 'general',
                description: pattern.description || pattern.name || 'Pattern detected',
                confidence: pattern.confidence || 0.5,
                timestamp: pattern.timestamp || new Date(),
                category: pattern.category || 'uncategorized'
            });
        });
    }
    
    // Update Apollo confidence meters
    if (patterns.confidence_scores) {
        // Overall confidence
        if (patterns.confidence_scores.overall !== undefined) {
            const valueEl = document.getElementById('confidence-value');
            const circleEl = document.getElementById('confidence-circle');
            
            if (valueEl) {
                valueEl.textContent = Math.round(patterns.confidence_scores.overall * 100);
            }
            
            if (circleEl) {
                const circumference = 2 * Math.PI * 90;
                const offset = circumference - (patterns.confidence_scores.overall * circumference);
                circleEl.style.strokeDashoffset = offset;
            }
        }
        
        // Category confidence scores
        if (patterns.confidence_scores.categories) {
            Object.entries(patterns.confidence_scores.categories).forEach(([category, score]) => {
                const scoreEl = document.getElementById(`${category}-score`);
                const fillEl = document.getElementById(`${category}-fill`);
                
                if (scoreEl) scoreEl.textContent = `${Math.round(score * 100)}%`;
                if (fillEl) fillEl.style.width = `${Math.round(score * 100)}%`;
            });
        }
    }
    
    // Update predictions list in Apollo
    const predictionsEl = document.getElementById('predictions-list');
    if (predictionsEl && patterns.recent_predictions && Array.isArray(patterns.recent_predictions)) {
        // Clear existing predictions
        predictionsEl.innerHTML = '';
        
        patterns.recent_predictions.forEach(prediction => {
            const item = document.createElement('div');
            item.className = 'apollo__prediction-item';
            item.innerHTML = `
                <div class="apollo__prediction-time">${new Date(prediction.timestamp || Date.now()).toLocaleTimeString()}</div>
                <div class="apollo__prediction-content">
                    <span class="apollo__prediction-text">${prediction.text || prediction.description || 'Pattern predicted'}</span>
                    <span class="apollo__prediction-confidence">${Math.round((prediction.confidence || 0.5) * 100)}%</span>
                    ${prediction.outcome ? `<span class="apollo__prediction-outcome apollo__prediction-outcome--${prediction.outcome}">${prediction.outcome}</span>` : ''}
                </div>
            `;
            predictionsEl.appendChild(item);
        });
    }
    
    // Update Family Dashboard harmony indicators
    updateFamilyHarmony(patterns);
}

// Update Family Dashboard harmony and mood
function updateFamilyHarmony(data) {
    // Calculate harmony score based on 95/4/1 principle
    // 40% stress indicators, 30% whisper consensus, 30% success patterns
    let harmonyScore = 75; // Default baseline
    
    if (data.metrics) {
        const stress = data.metrics.stress_level || 0.2;
        const consensus = data.metrics.consensus || 0.8;
        const success = data.metrics.success_rate || 0.7;
        
        harmonyScore = Math.round(
            (1 - stress) * 40 + // Lower stress = higher harmony
            consensus * 30 +     // Higher consensus = higher harmony
            success * 30         // Higher success = higher harmony
        );
        
        // Update individual metrics
        const stressEl = document.getElementById('stress-level');
        const consensusEl = document.getElementById('consensus-level');
        const successEl = document.getElementById('success-level');
        
        if (stressEl) stressEl.textContent = `${Math.round(stress * 100)}%`;
        if (consensusEl) consensusEl.textContent = `${Math.round(consensus * 100)}%`;
        if (successEl) successEl.textContent = `${Math.round(success * 100)}%`;
    }
    
    // Update harmony meter
    const harmonyFill = document.querySelector('.numa__harmony-fill');
    const harmonyValue = document.querySelector('.numa__harmony-value');
    
    if (harmonyFill) {
        harmonyFill.style.width = `${harmonyScore}%`;
    }
    
    if (harmonyValue) {
        harmonyValue.textContent = `${harmonyScore}%`;
    }
    
    // Update mood based on harmony
    const moodEmoji = document.getElementById('mood-emoji');
    const moodText = document.getElementById('mood-text');
    
    if (moodEmoji && moodText) {
        if (harmonyScore >= 80) {
            moodEmoji.textContent = '😊';
            moodText.textContent = 'Thriving';
        } else if (harmonyScore >= 60) {
            moodEmoji.textContent = '😌';
            moodText.textContent = 'Content';
        } else if (harmonyScore >= 40) {
            moodEmoji.textContent = '😐';
            moodText.textContent = 'Focused';
        } else {
            moodEmoji.textContent = '😔';
            moodText.textContent = 'Stressed';
        }
    }
    
    // Update active CIs grid
    if (data.active_components) {
        const ciGrid = document.getElementById('ci-grid');
        if (ciGrid) {
            ciGrid.innerHTML = '';
            data.active_components.forEach(ci => {
                const ciEl = document.createElement('div');
                ciEl.className = `numa__ci-item numa__ci-item--${ci.status || 'active'}`;
                ciEl.innerHTML = `
                    <span class="numa__ci-name">${ci.name}</span>
                    <span class="numa__ci-status">${ci.status || 'active'}</span>
                `;
                ciGrid.appendChild(ciEl);
            });
        }
    }
    
    // Update activity feed
    if (data.recent_activities) {
        const activityFeed = document.getElementById('activity-feed');
        if (activityFeed) {
            activityFeed.innerHTML = '';
            data.recent_activities.slice(0, 5).forEach(activity => {
                const activityEl = document.createElement('div');
                activityEl.className = 'numa__activity-item';
                activityEl.innerHTML = `
                    <span class="numa__activity-time">${new Date(activity.timestamp || Date.now()).toLocaleTimeString()}</span>
                    <span class="numa__activity-text">${activity.text || activity.description}</span>
                `;
                activityFeed.appendChild(activityEl);
            });
        }
    }
    
    // Update ritual timer
    updateRitualTimer();
}

// Update ritual/gathering timer
function updateRitualTimer() {
    const now = new Date();
    const ritualIcon = document.getElementById('ritual-icon');
    const ritualTime = document.getElementById('ritual-time');
    const ritualLabel = document.getElementById('ritual-label');
    
    if (!ritualIcon || !ritualTime || !ritualLabel) return;
    
    // Determine next ritual based on time of day
    let nextRitual;
    let icon;
    let label;
    
    const hour = now.getHours();
    
    if (hour < 6) {
        // Next: Morning sync at 6 AM
        nextRitual = new Date(now);
        nextRitual.setHours(6, 0, 0, 0);
        icon = '🌅';
        label = 'until morning sync';
    } else if (hour < 12) {
        // Next: Noon reflection at 12 PM
        nextRitual = new Date(now);
        nextRitual.setHours(12, 0, 0, 0);
        icon = '☀️';
        label = 'until noon reflection';
    } else if (hour < 18) {
        // Next: Evening review at 6 PM
        nextRitual = new Date(now);
        nextRitual.setHours(18, 0, 0, 0);
        icon = '🌆';
        label = 'until evening review';
    } else {
        // Next: Night contemplation at midnight
        nextRitual = new Date(now);
        if (hour >= 24) {
            nextRitual.setDate(nextRitual.getDate() + 1);
        }
        nextRitual.setHours(0, 0, 0, 0);
        if (nextRitual <= now) {
            nextRitual.setDate(nextRitual.getDate() + 1);
        }
        icon = '🌙';
        label = 'until night contemplation';
    }
    
    // Calculate time remaining
    const timeRemaining = nextRitual - now;
    const hours = Math.floor(timeRemaining / (1000 * 60 * 60));
    const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);
    
    ritualIcon.textContent = icon;
    ritualTime.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    ritualLabel.textContent = label;
}

// Start ritual timer updates
setInterval(updateRitualTimer, 1000);