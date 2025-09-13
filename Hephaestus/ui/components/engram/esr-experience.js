/**
 * ESR Experience Layer UI Component
 * @landmark Component: ESR Experience UI - Real-time memory visualization for CIs
 * @landmark WebSocket: Real-time connection to Engram service
 * @landmark Visualization: D3.js memory association graph
 */

class ESRExperienceUI {
    constructor() {
        this.ws = null;
        this.workingMemory = [];
        this.currentMood = { valence: 0, arousal: 0.5, dominance: 0.5 };
        this.promises = new Map();
        this.consolidationQueue = [];
        this.metrics = {};
        this.associationGraph = null;
        
        this.init();
    }
    
    /**
     * @landmark Initialization: Setup WebSocket and event handlers
     */
    init() {
        // Initialize WebSocket connection
        this.connectWebSocket();
        
        // Setup UI event handlers
        this.setupEventHandlers();
        
        // Initialize visualizations
        this.initEmotionGraph();
        this.initDecayCurve();
        this.initAssociationGraph();
        
        // Start update loops
        this.startMetricsUpdate();
        this.startMemoryDecay();
    }
    
    /**
     * @landmark WebSocket: Establish connection to Engram service
     */
    connectWebSocket() {
        const wsUrl = 'ws://localhost:8100/experience/stream';
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('ESR Experience WebSocket connected');
                this.updateConnectionStatus('connected');
            };
            
            this.ws.onmessage = (event) => {
                this.handleWebSocketMessage(event);
            };
            
            this.ws.onerror = (error) => {
                console.error('ESR WebSocket error:', error);
                this.updateConnectionStatus('error');
            };
            
            this.ws.onclose = () => {
                console.log('ESR WebSocket closed, reconnecting...');
                this.updateConnectionStatus('disconnected');
                setTimeout(() => this.connectWebSocket(), 5000);
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.updateConnectionStatus('error');
        }
    }
    
    /**
     * @landmark Message Handler: Process incoming WebSocket messages
     */
    handleWebSocketMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'working_memory_update':
                    this.updateWorkingMemory(data.thoughts);
                    break;
                    
                case 'boundary_detected':
                    this.showBoundaryDetection(data.boundary_type, data.confidence);
                    break;
                    
                case 'emotion_change':
                    this.updateEmotionalContext(data.mood);
                    break;
                    
                case 'memory_consolidated':
                    this.handleConsolidation(data.memories);
                    break;
                    
                case 'promise_update':
                    this.updatePromise(data.promise_id, data.stage, data.confidence);
                    break;
                    
                case 'metrics_update':
                    this.updateMetrics(data.metrics);
                    break;
                    
                case 'association_formed':
                    this.addAssociation(data.source, data.target, data.strength);
                    break;
                    
                default:
                    console.log('Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('Error handling WebSocket message:', error);
        }
    }
    
    /**
     * @landmark Working Memory: Update display with current thoughts
     */
    updateWorkingMemory(thoughts) {
        const container = document.getElementById('esr-active-thoughts');
        if (!container) return;
        
        // Clear existing thoughts
        container.innerHTML = '';
        
        // Update capacity meter
        const capacity = thoughts.length / 7;
        this.updateCapacityMeter(capacity);
        
        // Add each thought
        thoughts.forEach(thought => {
            const thoughtEl = this.createThoughtElement(thought);
            container.appendChild(thoughtEl);
        });
        
        this.workingMemory = thoughts;
    }
    
    /**
     * @landmark Thought Creation: Generate thought DOM element
     */
    createThoughtElement(thought) {
        const div = document.createElement('div');
        div.className = 'esr__thought';
        div.dataset.thoughtId = thought.id;
        div.dataset.state = thought.state;
        div.dataset.accessCount = thought.access_count;
        
        const attentionWidth = Math.min(100, thought.access_count * 15);
        
        div.innerHTML = `
            <div class="esr__thought-content">
                <span class="esr__thought-text">${thought.content}</span>
                <span class="esr__access-count">×${thought.access_count}</span>
            </div>
            <div class="esr__attention-bar">
                <div class="esr__attention-fill" style="width: ${attentionWidth}%"></div>
            </div>
        `;
        
        return div;
    }
    
    /**
     * @landmark Capacity Meter: Update working memory capacity display
     */
    updateCapacityMeter(usage) {
        const fill = document.getElementById('esr-capacity-fill');
        const label = document.getElementById('esr-capacity-label');
        
        if (fill) {
            fill.style.width = `${usage * 100}%`;
        }
        
        if (label) {
            const count = Math.round(usage * 7);
            label.textContent = `${count}/7 thoughts`;
        }
    }
    
    /**
     * @landmark Emotional Context: Update mood display
     */
    updateEmotionalContext(mood) {
        this.currentMood = mood;
        
        // Update mood label
        const moodLabel = document.getElementById('esr-mood-label');
        if (moodLabel) {
            moodLabel.textContent = `${mood.primary_emotion} (${mood.intensity.toFixed(1)})`;
        }
        
        // Update emotion axes
        this.updateEmotionAxis('valence', mood.valence);
        this.updateEmotionAxis('arousal', mood.arousal);
        this.updateEmotionAxis('dominance', mood.dominance);
        
        // Update primary emotion display
        const primaryEl = document.querySelector('.esr__primary-emotion');
        if (primaryEl) {
            const emoji = this.getEmotionEmoji(mood.primary_emotion);
            primaryEl.querySelector('.esr__emotion-icon').textContent = emoji;
            primaryEl.querySelector('.esr__emotion-name').textContent = mood.primary_emotion;
            primaryEl.querySelector('.esr__emotion-intensity').textContent = 
                `${mood.intensity > 0.7 ? 'High' : mood.intensity > 0.3 ? 'Medium' : 'Low'} (${mood.intensity.toFixed(1)})`;
        }
        
        // Update emotion graph
        this.addEmotionDataPoint(mood);
    }
    
    /**
     * @landmark Emotion Axis: Update individual emotion dimension
     */
    updateEmotionAxis(axis, value) {
        const fill = document.querySelector(`.esr__${axis}-fill`);
        const valueEl = document.querySelector(`.esr__${axis}-axis .esr__axis-value`);
        
        if (fill) {
            const percentage = axis === 'valence' ? 
                (value + 1) * 50 : // Convert -1..1 to 0..100
                value * 100;       // Convert 0..1 to 0..100
            fill.style.width = `${percentage}%`;
        }
        
        if (valueEl) {
            const displayValue = axis === 'valence' && value > 0 ? `+${value.toFixed(1)}` : value.toFixed(1);
            valueEl.textContent = displayValue;
        }
    }
    
    /**
     * @landmark Boundary Detection: Show interstitial processing event
     */
    showBoundaryDetection(boundaryType, confidence) {
        const detector = document.querySelector('.esr__boundary-current');
        if (!detector) return;
        
        // Update current boundary
        detector.querySelector('.esr__boundary-type').textContent = 
            boundaryType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        detector.querySelector('.esr__boundary-fill').style.width = `${confidence * 100}%`;
        detector.querySelector('.esr__boundary-confidence').textContent = `${Math.round(confidence * 100)}% confidence`;
        
        // Add to history
        this.addBoundaryToHistory(boundaryType);
        
        // Trigger consolidation animation
        this.animateConsolidation();
    }
    
    /**
     * @landmark Consolidation: Handle memory consolidation event
     */
    handleConsolidation(memories) {
        const statusEl = document.getElementById('esr-consolidation-status');
        if (!statusEl) return;
        
        statusEl.querySelector('.esr__consolidation-text').textContent = 
            `Consolidating ${memories.length} related thoughts...`;
        
        // Animate consolidation progress
        const progressFill = statusEl.querySelector('.esr__consolidation-fill');
        if (progressFill) {
            progressFill.style.width = '0%';
            setTimeout(() => {
                progressFill.style.transition = 'width 2s ease-out';
                progressFill.style.width = '100%';
            }, 100);
        }
        
        // Update consolidation queue
        const queueEl = document.querySelector('.esr__queue-count');
        if (queueEl) {
            const remaining = Math.max(0, parseInt(queueEl.textContent) - memories.length);
            queueEl.textContent = remaining;
        }
    }
    
    /**
     * @landmark Promise Update: Track memory promise resolution
     */
    updatePromise(promiseId, stage, confidence) {
        let promiseEl = document.querySelector(`[data-promise-id="${promiseId}"]`);
        
        if (!promiseEl) {
            promiseEl = this.createPromiseElement(promiseId);
            document.getElementById('esr-promise-list').appendChild(promiseEl);
        }
        
        // Update stage indicators
        const stages = promiseEl.querySelectorAll('.esr__stage');
        const stageIndex = ['cache', 'fast_search', 'deep_synthesis'].indexOf(stage);
        
        stages.forEach((stageEl, i) => {
            if (i < stageIndex) {
                stageEl.classList.add('complete');
                stageEl.textContent = '✓ ' + stageEl.textContent.replace(/[→○✓] /, '');
            } else if (i === stageIndex) {
                stageEl.classList.add('active');
                stageEl.classList.remove('pending');
                stageEl.textContent = '→ ' + stageEl.textContent.replace(/[→○✓] /, '');
            }
        });
        
        // Update confidence
        promiseEl.querySelector('.esr__confidence-fill').style.width = `${confidence * 100}%`;
        promiseEl.querySelector('.esr__confidence-text').textContent = `${Math.round(confidence * 100)}% confidence`;
        
        // Mark as resolved if complete
        if (stage === 'deep_synthesis' && confidence > 0.9) {
            promiseEl.dataset.state = 'resolved';
            setTimeout(() => promiseEl.classList.add('fade-out'), 3000);
        }
    }
    
    /**
     * @landmark Metrics Update: Refresh performance metrics
     */
    updateMetrics(metrics) {
        this.metrics = metrics;
        
        // Update metric values
        Object.entries(metrics).forEach(([key, value]) => {
            const metricEl = document.querySelector(`[data-metric="${key}"] .esr__metric-value`);
            if (metricEl) {
                metricEl.textContent = this.formatMetricValue(key, value);
            }
        });
        
        // Update decay curve if needed
        if (metrics.decay_curve) {
            this.updateDecayCurve(metrics.decay_curve);
        }
    }
    
    /**
     * @landmark Event Handlers: Setup UI interaction handlers
     */
    setupEventHandlers() {
        // Research control handlers
        document.querySelectorAll('.esr__control-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.onclick ? null : e.target.dataset.action;
                if (action) {
                    this.handleControlAction(action, e.target);
                }
            });
        });
        
        // Emotion slider
        const valenceSlider = document.getElementById('esr-valence-control');
        if (valenceSlider) {
            valenceSlider.addEventListener('input', (e) => {
                this.previewEmotionChange(parseFloat(e.target.value));
            });
        }
        
        // Replay speed control
        const replaySpeed = document.getElementById('esr-replay-speed');
        if (replaySpeed) {
            replaySpeed.addEventListener('input', (e) => {
                const speed = parseFloat(e.target.value);
                document.querySelector('.esr__speed-label').textContent = `${speed}x`;
            });
        }
    }
    
    /**
     * @landmark Control Actions: Handle research control interactions
     */
    triggerBoundary(type) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: 'trigger_boundary',
                boundary_type: type
            }));
        }
    }
    
    injectEmotion() {
        const valence = parseFloat(document.getElementById('esr-valence-control').value);
        const emotionType = document.getElementById('esr-emotion-type').value;
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: 'inject_emotion',
                emotion: {
                    valence: valence,
                    primary_emotion: emotionType,
                    arousal: 0.5 + Math.abs(valence) * 0.5,
                    dominance: 0.5
                }
            }));
        }
    }
    
    triggerDreamState() {
        const dreamEl = document.querySelector('.esr__dream-state');
        if (dreamEl) {
            dreamEl.dataset.active = 'true';
            dreamEl.querySelector('.esr__dream-text').textContent = 'Dream recombination active...';
            
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    action: 'trigger_dream'
                }));
            }
            
            // Auto-disable after 10 seconds
            setTimeout(() => {
                dreamEl.dataset.active = 'false';
                dreamEl.querySelector('.esr__dream-text').textContent = 'Dream recombination inactive';
            }, 10000);
        }
    }
    
    startReplay() {
        const speed = parseFloat(document.getElementById('esr-replay-speed').value);
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: 'start_replay',
                speed: speed
            }));
        }
    }
    
    refreshMetrics() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                action: 'refresh_metrics'
            }));
        }
    }
    
    filterByEmotion(emotion) {
        if (this.associationGraph) {
            this.associationGraph.filterByEmotion(emotion);
        }
    }
    
    showClusters() {
        if (this.associationGraph) {
            this.associationGraph.showClusters();
        }
    }
    
    /**
     * @landmark Visualization: Initialize emotion history graph
     */
    initEmotionGraph() {
        const canvas = document.getElementById('esr-emotion-graph');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        this.emotionGraphData = {
            valence: [],
            arousal: [],
            timestamps: []
        };
        
        this.emotionGraphCtx = ctx;
        this.drawEmotionGraph();
    }
    
    /**
     * @landmark Visualization: Initialize decay curve graph
     */
    initDecayCurve() {
        const canvas = document.getElementById('esr-decay-curve');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        this.decayCurveCtx = ctx;
        this.drawDecayCurve();
    }
    
    /**
     * @landmark Association Graph: Initialize D3.js memory network
     */
    initAssociationGraph() {
        const svg = d3.select('#esr-association-graph');
        if (!svg.node()) return;
        
        const width = svg.node().getBoundingClientRect().width;
        const height = 300;
        
        // Create force simulation
        this.associationGraph = {
            nodes: [],
            links: [],
            simulation: d3.forceSimulation()
                .force('link', d3.forceLink().id(d => d.id).distance(50))
                .force('charge', d3.forceManyBody().strength(-100))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(20)),
            
            svg: svg,
            width: width,
            height: height,
            
            update: function() {
                // Update links
                const link = this.svg.selectAll('.esr__association-link')
                    .data(this.links, d => `${d.source.id}-${d.target.id}`);
                
                link.enter()
                    .append('line')
                    .attr('class', 'esr__association-link')
                    .style('stroke', '#666')
                    .style('stroke-opacity', d => d.strength)
                    .style('stroke-width', d => Math.sqrt(d.strength * 10));
                
                link.exit().remove();
                
                // Update nodes
                const node = this.svg.selectAll('.esr__association-node')
                    .data(this.nodes, d => d.id);
                
                const nodeEnter = node.enter()
                    .append('g')
                    .attr('class', 'esr__association-node')
                    .call(d3.drag()
                        .on('start', (event, d) => {
                            if (!event.active) this.simulation.alphaTarget(0.3).restart();
                            d.fx = d.x;
                            d.fy = d.y;
                        })
                        .on('drag', (event, d) => {
                            d.fx = event.x;
                            d.fy = event.y;
                        })
                        .on('end', (event, d) => {
                            if (!event.active) this.simulation.alphaTarget(0);
                            d.fx = null;
                            d.fy = null;
                        }));
                
                nodeEnter.append('circle')
                    .attr('r', d => 5 + d.importance * 15)
                    .style('fill', d => this.getEmotionColor(d.emotion));
                
                nodeEnter.append('text')
                    .attr('dx', 12)
                    .attr('dy', 4)
                    .style('font-size', '10px')
                    .text(d => d.label ? d.label.substring(0, 20) : '');
                
                node.exit().remove();
                
                // Update simulation
                this.simulation.nodes(this.nodes);
                this.simulation.force('link').links(this.links);
                this.simulation.alpha(1).restart();
                
                this.simulation.on('tick', () => {
                    this.svg.selectAll('.esr__association-link')
                        .attr('x1', d => d.source.x)
                        .attr('y1', d => d.source.y)
                        .attr('x2', d => d.target.x)
                        .attr('y2', d => d.target.y);
                    
                    this.svg.selectAll('.esr__association-node')
                        .attr('transform', d => `translate(${d.x},${d.y})`);
                });
            },
            
            getEmotionColor: function(emotion) {
                const colors = {
                    joy: '#4CAF50',
                    sadness: '#2196F3',
                    anger: '#F44336',
                    fear: '#9C27B0',
                    surprise: '#FF9800',
                    trust: '#00BCD4',
                    neutral: '#9E9E9E'
                };
                return colors[emotion] || colors.neutral;
            },
            
            filterByEmotion: function(emotion) {
                if (emotion === 'all') {
                    this.svg.selectAll('.esr__association-node')
                        .style('opacity', 1);
                    this.svg.selectAll('.esr__association-link')
                        .style('opacity', d => d.strength);
                } else {
                    this.svg.selectAll('.esr__association-node')
                        .style('opacity', d => d.emotion === emotion ? 1 : 0.2);
                    this.svg.selectAll('.esr__association-link')
                        .style('opacity', d => 
                            (d.source.emotion === emotion || d.target.emotion === emotion) ? 
                            d.strength : 0.1);
                }
            },
            
            showClusters: function() {
                // Color nodes by cluster
                const clusters = this.detectClusters();
                const clusterColors = d3.scaleOrdinal(d3.schemeCategory10);
                
                this.svg.selectAll('.esr__association-node circle')
                    .style('fill', d => clusterColors(clusters[d.id] || 0));
            },
            
            detectClusters: function() {
                // Simple community detection (placeholder)
                const clusters = {};
                let clusterIndex = 0;
                
                this.nodes.forEach(node => {
                    if (!clusters[node.id]) {
                        clusters[node.id] = clusterIndex++;
                        // Assign connected nodes to same cluster
                        this.links.forEach(link => {
                            if (link.source.id === node.id) {
                                clusters[link.target.id] = clusters[node.id];
                            }
                        });
                    }
                });
                
                return clusters;
            }
        };
        
        // Add sample data for testing
        this.addSampleAssociationData();
    }
    
    /**
     * @landmark Sample Data: Add test data for association graph
     */
    addSampleAssociationData() {
        if (!this.associationGraph) return;
        
        // Add sample nodes
        const sampleNodes = [
            { id: 'auth', label: 'Authentication', emotion: 'trust', importance: 0.9 },
            { id: 'oauth', label: 'OAuth Bug', emotion: 'fear', importance: 0.8 },
            { id: 'fix', label: 'Bug Fix', emotion: 'joy', importance: 0.7 },
            { id: 'quantum', label: 'Quantum Topic', emotion: 'surprise', importance: 0.6 },
            { id: 'deadline', label: 'Project Deadline', emotion: 'anger', importance: 0.85 }
        ];
        
        const sampleLinks = [
            { source: 'auth', target: 'oauth', strength: 0.9 },
            { source: 'oauth', target: 'fix', strength: 0.8 },
            { source: 'auth', target: 'deadline', strength: 0.6 },
            { source: 'quantum', target: 'auth', strength: 0.3 }
        ];
        
        this.associationGraph.nodes = sampleNodes;
        this.associationGraph.links = sampleLinks;
        this.associationGraph.update();
    }
    
    /**
     * @landmark Helper: Get emoji for emotion type
     */
    getEmotionEmoji(emotion) {
        const emojis = {
            joy: '😊',
            sadness: '😢',
            anger: '😠',
            fear: '😨',
            surprise: '😮',
            trust: '🤝',
            anticipation: '🤔',
            disgust: '😒'
        };
        return emojis[emotion] || '😐';
    }
    
    /**
     * @landmark Helper: Format metric values for display
     */
    formatMetricValue(key, value) {
        if (key.includes('rate')) return `${value}/hr`;
        if (key.includes('latency')) return `${value}ms`;
        if (key.includes('memory')) return `${Math.round(value * 100)}%`;
        if (typeof value === 'number') return value.toFixed(2);
        return value;
    }
    
    /**
     * @landmark Helper: Update connection status indicator
     */
    updateConnectionStatus(status) {
        const indicator = document.querySelector('.esr__status-indicator');
        const text = document.querySelector('.esr__status-text');
        
        if (indicator) {
            indicator.dataset.esrStatus = status;
        }
        
        if (text) {
            const messages = {
                connected: 'Memory Formation Active',
                disconnected: 'Connection Lost',
                error: 'Connection Error'
            };
            text.textContent = messages[status] || 'Unknown Status';
        }
    }
    
    /**
     * @landmark Update Loop: Periodic metrics refresh
     */
    startMetricsUpdate() {
        setInterval(() => {
            this.refreshMetrics();
        }, 30000); // Every 30 seconds
    }
    
    /**
     * @landmark Memory Decay: Simulate natural forgetting
     */
    startMemoryDecay() {
        setInterval(() => {
            // Decay working memory attention
            this.workingMemory.forEach(thought => {
                const thoughtEl = document.querySelector(`[data-thought-id="${thought.id}"]`);
                if (thoughtEl && thought.state === 'active') {
                    const attentionBar = thoughtEl.querySelector('.esr__attention-fill');
                    if (attentionBar) {
                        const currentWidth = parseFloat(attentionBar.style.width);
                        const newWidth = Math.max(0, currentWidth - 5);
                        attentionBar.style.width = `${newWidth}%`;
                    }
                }
            });
        }, 5000); // Every 5 seconds
    }
    
    /**
     * @landmark Animation: Consolidation visual effect
     */
    animateConsolidation() {
        const thoughts = document.querySelectorAll('.esr__thought[data-state="rehearsing"]');
        thoughts.forEach(thought => {
            thought.classList.add('consolidating-animation');
            setTimeout(() => {
                thought.classList.remove('consolidating-animation');
                thought.dataset.state = 'consolidating';
            }, 1000);
        });
    }
    
    /**
     * @landmark Helper: Add boundary event to history
     */
    addBoundaryToHistory(boundaryType) {
        const historyContainer = document.querySelector('.esr__boundary-history');
        if (!historyContainer) return;
        
        const newItem = document.createElement('div');
        newItem.className = 'esr__boundary-item';
        newItem.dataset.type = boundaryType;
        newItem.innerHTML = `
            <span class="esr__boundary-time">just now</span>
            <span class="esr__boundary-label">${boundaryType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
        `;
        
        // Add at the beginning
        historyContainer.insertBefore(newItem, historyContainer.firstChild);
        
        // Keep only last 5 items
        while (historyContainer.children.length > 5) {
            historyContainer.removeChild(historyContainer.lastChild);
        }
    }
    
    /**
     * @landmark Helper: Create promise element
     */
    createPromiseElement(promiseId) {
        const div = document.createElement('div');
        div.className = 'esr__promise';
        div.dataset.promiseId = promiseId;
        div.dataset.state = 'resolving';
        
        div.innerHTML = `
            <div class="esr__promise-query">
                "Recalling memory ${promiseId}..."
            </div>
            <div class="esr__promise-stages">
                <span class="esr__stage pending">○ Cache</span>
                <span class="esr__stage pending">○ Fast Search</span>
                <span class="esr__stage pending">○ Deep Synthesis</span>
            </div>
            <div class="esr__promise-confidence">
                <div class="esr__confidence-bar">
                    <div class="esr__confidence-fill" style="width: 0%"></div>
                </div>
                <span class="esr__confidence-text">0% confidence</span>
            </div>
        `;
        
        return div;
    }
    
    /**
     * @landmark Emotion Graph: Draw emotion history
     */
    drawEmotionGraph() {
        if (!this.emotionGraphCtx) return;
        
        const ctx = this.emotionGraphCtx;
        const canvas = ctx.canvas;
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw axes
        ctx.strokeStyle = '#666';
        ctx.beginPath();
        ctx.moveTo(0, height / 2);
        ctx.lineTo(width, height / 2);
        ctx.stroke();
        
        // Draw data if available
        if (this.emotionGraphData && this.emotionGraphData.valence.length > 0) {
            // Draw valence line
            ctx.strokeStyle = '#4CAF50';
            ctx.beginPath();
            this.emotionGraphData.valence.forEach((val, i) => {
                const x = (i / this.emotionGraphData.valence.length) * width;
                const y = height / 2 - (val * height / 2);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.stroke();
            
            // Draw arousal line
            ctx.strokeStyle = '#FF9800';
            ctx.beginPath();
            this.emotionGraphData.arousal.forEach((val, i) => {
                const x = (i / this.emotionGraphData.arousal.length) * width;
                const y = height - (val * height);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.stroke();
        }
    }
    
    /**
     * @landmark Decay Curve: Draw memory decay visualization
     */
    drawDecayCurve() {
        if (!this.decayCurveCtx) return;
        
        const ctx = this.decayCurveCtx;
        const canvas = ctx.canvas;
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw exponential decay curve
        ctx.strokeStyle = '#2196F3';
        ctx.beginPath();
        
        for (let x = 0; x < width; x++) {
            const t = x / width * 24; // 24 hours
            const retention = Math.exp(-0.1 * t); // Exponential decay
            const y = height - (retention * height);
            
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        
        ctx.stroke();
        
        // Draw reference lines
        ctx.strokeStyle = '#ccc';
        ctx.setLineDash([5, 5]);
        
        // 50% retention line
        ctx.beginPath();
        ctx.moveTo(0, height / 2);
        ctx.lineTo(width, height / 2);
        ctx.stroke();
        
        ctx.setLineDash([]);
    }
    
    /**
     * @landmark Data Point: Add emotion data to history
     */
    addEmotionDataPoint(mood) {
        if (!this.emotionGraphData) return;
        
        // Keep last 100 points
        if (this.emotionGraphData.valence.length > 100) {
            this.emotionGraphData.valence.shift();
            this.emotionGraphData.arousal.shift();
            this.emotionGraphData.timestamps.shift();
        }
        
        this.emotionGraphData.valence.push(mood.valence);
        this.emotionGraphData.arousal.push(mood.arousal);
        this.emotionGraphData.timestamps.push(Date.now());
        
        this.drawEmotionGraph();
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.esrExperience = new ESRExperienceUI();
    });
} else {
    window.esrExperience = new ESRExperienceUI();
}

// Export for use in other components
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ESRExperienceUI;
}