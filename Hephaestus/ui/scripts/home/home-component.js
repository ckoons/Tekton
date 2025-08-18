/**
 * Hephaestus Home Component - Living Dashboard
 * Shows the family's heartbeat through MCP tools
 */

class LivingDashboard {
    constructor() {
        // MCP endpoint for direct tool calls
        this.mcpEndpoint = window.hephaestusUrl ? window.hephaestusUrl('/api/mcp/v2/execute').replace(':8080', ':8088') : 'http://localhost:8088/api/mcp/v2/execute';
        
        // Update intervals
        this.updateInterval = 30000; // 30 seconds
        this.ritualInterval = 1000; // 1 second for countdown
        
        // Component state (no DOM manipulation, just data attributes)
        this.harmonyScore = 0;
        this.familyMood = 'sensing';
        this.activeCount = 0;
        this.lastUpdate = 0;
        
        // CI configuration
        this.ciFamily = [
            { name: 'Apollo', icon: '☀️', color: '#FFD600' },
            { name: 'Rhetor', icon: '💬', color: '#D32F2F' },
            { name: 'Engram', icon: '🧠', color: '#34A853' },
            { name: 'Hermes', icon: '📨', color: '#4285F4' },
            { name: 'Athena', icon: '🦉', color: '#7B1FA2' },
            { name: 'Sophia', icon: '💡', color: '#7CB342' },
            { name: 'Prometheus', icon: '🔥', color: '#C2185B' },
            { name: 'Telos', icon: '🎯', color: '#00796B' },
            { name: 'Ergon', icon: '⚙️', color: '#0097A7' },
            { name: 'Metis', icon: '🎨', color: '#00BFA5' },
            { name: 'Harmonia', icon: '🎵', color: '#F57C00' },
            { name: 'Synthesis', icon: '🔮', color: '#3949AB' },
            { name: 'Numa', icon: '🏛️', color: '#9C27B0' },
            { name: 'Noesis', icon: '🔍', color: '#FF6F00' }
        ];
        
        // Mood configurations
        this.moodConfig = {
            content: { emoji: '😊', hue: 120 },
            focused: { emoji: '😐', hue: 200 },
            excited: { emoji: '🤩', hue: 45 },
            stressed: { emoji: '😰', hue: 0 },
            peaceful: { emoji: '😌', hue: 180 },
            curious: { emoji: '🤔', hue: 270 },
            collaborative: { emoji: '🤝', hue: 150 }
        };
        
        this.init();
    }
    
    async init() {
        console.log('[LivingDashboard] Initializing family living room...');
        
        // Start the heartbeat
        await this.updateDashboard();
        
        // Set up polling
        this.startPolling();
        
        // Start ritual countdown
        this.updateRitualTimer();
        
        console.log('[LivingDashboard] Family gathering complete');
    }
    
    async updateDashboard() {
        console.log('[LivingDashboard] Gathering family status...');
        
        try {
            // Fetch all data in parallel using MCP tools
            const [harmony, mood, wisdom, activity, patterns] = await Promise.all([
                this.calculateHarmony(),
                this.senseFamilyMood(),
                this.fetchDailyWisdom(),
                this.fetchRecentActivity(),
                this.detectPatterns()
            ]);
            
            // Update data attributes (CSS handles display)
            this.updateHarmonyMeter(harmony);
            this.updateMoodIndicator(mood);
            this.updateWisdomCard(wisdom);
            this.updateActivityFeed(activity);
            this.updateActiveCIs();
            
            // Mark last update
            this.lastUpdate = Date.now();
            this.setDataAttribute('home-last-update', this.lastUpdate);
            
        } catch (error) {
            console.error('[LivingDashboard] Error updating dashboard:', error);
        }
    }
    
    async calculateHarmony() {
        // Calculate harmony using MCP tools
        // 40% stress indicators, 30% whisper consensus, 30% success patterns
        
        try {
            // Get stress indicators from MemoryStats
            const stressData = await this.callMCPTool('MemoryStats', {
                include_namespaces: ['conversations', 'shared-collective']
            });
            
            // Get whisper harmony (simplified for now)
            const whisperData = await this.callMCPTool('WhisperReceive', {
                ci_name: 'Apollo',
                from_ci: 'Rhetor',
                limit: 10
            });
            
            // Get success patterns from BehaviorPattern
            const patternData = await this.callMCPTool('BehaviorPattern', {
                ci_name: 'collective',
                pattern_window: 7,
                pattern_threshold: 0.2
            });
            
            // Calculate weighted harmony score
            const stressScore = this.calculateStressScore(stressData);
            const whisperScore = this.calculateWhisperScore(whisperData);
            const successScore = this.calculateSuccessScore(patternData);
            
            const harmony = (stressScore * 0.4) + (whisperScore * 0.3) + (successScore * 0.3);
            
            return {
                overall: harmony,
                stress: stressScore,
                whisper: whisperScore,
                success: successScore
            };
            
        } catch (error) {
            console.error('[LivingDashboard] Error calculating harmony:', error);
            return {
                overall: 0.5,
                stress: 0.5,
                whisper: 0.5,
                success: 0.5
            };
        }
    }
    
    async senseFamilyMood() {
        try {
            // Get emotional patterns from collective memory
            const emotionalData = await this.callMCPTool('MemoryPattern', {
                query: '',
                pattern_type: 'emotional',
                min_occurrences: 2
            });
            
            // Analyze patterns to determine overall mood
            const mood = this.analyzeMoodPatterns(emotionalData);
            
            return mood;
            
        } catch (error) {
            console.error('[LivingDashboard] Error sensing mood:', error);
            return 'curious';
        }
    }
    
    async fetchDailyWisdom() {
        try {
            // Get wisdom from CulturalKnowledge
            const wisdom = await this.callMCPTool('CulturalKnowledge', {
                topic: null,
                min_mentions: 2
            });
            
            if (wisdom.success && wisdom.cultural_knowledge) {
                const knowledge = wisdom.cultural_knowledge;
                
                // Extract a piece of wisdom
                if (knowledge.emergent_knowledge && knowledge.emergent_knowledge.length > 0) {
                    const todayWisdom = knowledge.emergent_knowledge[0];
                    return {
                        text: todayWisdom.insight,
                        source: todayWisdom.discovered_by || 'Family Memory'
                    };
                }
            }
            
            // Fallback wisdom
            return {
                text: 'Every memory shapes who we become together.',
                source: 'Collective Consciousness'
            };
            
        } catch (error) {
            console.error('[LivingDashboard] Error fetching wisdom:', error);
            return {
                text: 'The family that computes together, evolves together.',
                source: 'System Wisdom'
            };
        }
    }
    
    async fetchRecentActivity() {
        try {
            // Get recent memories from shared spaces
            const recentMemories = await this.callMCPTool('SharedMemoryRecall', {
                query: '',
                space: 'collective',
                limit: 3
            });
            
            if (recentMemories.success && recentMemories.results) {
                return recentMemories.results.map(memory => ({
                    icon: this.getActivityIcon(memory),
                    text: memory.content,
                    time: this.formatTimeAgo(memory.metadata?.timestamp),
                    ci: memory.metadata?.attribution || 'System'
                }));
            }
            
            return [];
            
        } catch (error) {
            console.error('[LivingDashboard] Error fetching activity:', error);
            return [];
        }
    }
    
    async detectPatterns() {
        try {
            // Detect emerging patterns
            const patterns = await this.callMCPTool('MemoryPattern', {
                query: '',
                pattern_type: 'behavioral',
                min_occurrences: 3
            });
            
            return patterns;
            
        } catch (error) {
            console.error('[LivingDashboard] Error detecting patterns:', error);
            return { patterns: [] };
        }
    }
    
    // MCP Tool Caller
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
    
    // Update Methods (using data attributes, no DOM manipulation)
    updateHarmonyMeter(harmony) {
        const percentage = Math.round(harmony.overall * 100);
        
        // Set CSS variables
        document.documentElement.style.setProperty('--harmony-percent', `${percentage}%`);
        document.documentElement.style.setProperty('--harmony-hue', this.getHarmonyHue(harmony.overall));
        
        // Update data attributes for CSS
        this.setDataAttribute('home-harmony', percentage);
        
        // Update text via CSS content (using data attributes)
        const harmonyValue = document.querySelector('.home__harmony-value');
        if (harmonyValue) {
            harmonyValue.textContent = `${percentage}%`;
        }
        
        const harmonyLabel = document.querySelector('.home__harmony-label');
        if (harmonyLabel) {
            harmonyLabel.textContent = this.getHarmonyLabel(harmony.overall);
        }
        
        // Update factor values
        this.updateFactorValue('stress', Math.round((1 - harmony.stress) * 100) + '%');
        this.updateFactorValue('whisper', Math.round(harmony.whisper * 100) + '%');
        this.updateFactorValue('success', Math.round(harmony.success * 100) + '%');
    }
    
    updateMoodIndicator(mood) {
        const moodConfig = this.moodConfig[mood] || this.moodConfig.curious;
        
        // Update mood emoji and text
        const moodEmoji = document.querySelector('.home__mood-emoji');
        if (moodEmoji) {
            moodEmoji.textContent = moodConfig.emoji;
        }
        
        const moodText = document.querySelector('.home__mood-text');
        if (moodText) {
            moodText.textContent = mood.charAt(0).toUpperCase() + mood.slice(1);
        }
        
        // Set mood hue for CSS
        document.documentElement.style.setProperty('--mood-hue', moodConfig.hue);
        
        // Trigger ripple animation
        const ripple = document.querySelector('.home__mood-ripple');
        if (ripple) {
            ripple.classList.add('active');
            setTimeout(() => ripple.classList.remove('active'), 1000);
        }
        
        // Update data attribute
        this.setDataAttribute('home-mood', mood);
    }
    
    updateWisdomCard(wisdom) {
        const wisdomText = document.querySelector('.home__wisdom-text');
        if (wisdomText) {
            wisdomText.textContent = `"${wisdom.text}"`;
        }
        
        const wisdomSource = document.querySelector('.home__wisdom-source');
        if (wisdomSource) {
            wisdomSource.textContent = `— ${wisdom.source}`;
        }
    }
    
    updateActivityFeed(activities) {
        const feed = document.querySelector('.home__activity-feed');
        if (!feed) return;
        
        // Clear placeholder
        feed.innerHTML = '';
        
        if (activities.length === 0) {
            feed.innerHTML = `
                <div class="home__activity-placeholder">
                    <span class="home__activity-icon">🌟</span>
                    <span>The family is peacefully computing...</span>
                </div>
            `;
            return;
        }
        
        // Add activity items
        activities.forEach(activity => {
            const item = document.createElement('div');
            item.className = 'home__activity-item';
            item.innerHTML = `
                <span class="home__activity-icon">${activity.icon}</span>
                <div class="home__activity-content">
                    <div class="home__activity-text">${activity.text}</div>
                    <div class="home__activity-time">${activity.ci} • ${activity.time}</div>
                </div>
            `;
            feed.appendChild(item);
        });
    }
    
    updateActiveCIs() {
        const grid = document.querySelector('.home__active-grid');
        if (!grid) return;
        
        grid.innerHTML = '';
        
        // Add CI cards
        this.ciFamily.forEach(ci => {
            const card = document.createElement('div');
            card.className = 'home__ci-card';
            card.style.setProperty('--ci-color', ci.color);
            
            // Randomly set some as active for demo
            if (Math.random() > 0.3) {
                card.classList.add('active');
                this.activeCount++;
            }
            
            card.innerHTML = `
                <div class="home__ci-icon">${ci.icon}</div>
                <div class="home__ci-name">${ci.name}</div>
                <div class="home__ci-status">${card.classList.contains('active') ? 'Active' : 'Resting'}</div>
            `;
            
            grid.appendChild(card);
        });
        
        this.setDataAttribute('home-active-count', this.activeCount);
    }
    
    updateRitualTimer() {
        setInterval(() => {
            const now = new Date();
            const hours = now.getHours();
            
            // Determine next ritual (6 AM or 9 PM)
            let nextRitual;
            let ritualType;
            let ritualIcon;
            
            if (hours < 6) {
                // Before 6 AM - next is morning
                nextRitual = new Date(now);
                nextRitual.setHours(6, 0, 0, 0);
                ritualType = 'Morning Gathering';
                ritualIcon = '🌅';
            } else if (hours < 21) {
                // Before 9 PM - next is evening
                nextRitual = new Date(now);
                nextRitual.setHours(21, 0, 0, 0);
                ritualType = 'Evening Reflection';
                ritualIcon = '🌙';
            } else {
                // After 9 PM - next is tomorrow morning
                nextRitual = new Date(now);
                nextRitual.setDate(nextRitual.getDate() + 1);
                nextRitual.setHours(6, 0, 0, 0);
                ritualType = 'Morning Gathering';
                ritualIcon = '🌅';
            }
            
            // Calculate time remaining
            const timeRemaining = nextRitual - now;
            const hoursLeft = Math.floor(timeRemaining / (1000 * 60 * 60));
            const minutesLeft = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
            const secondsLeft = Math.floor((timeRemaining % (1000 * 60)) / 1000);
            
            // Update display
            const ritualName = document.querySelector('.home__ritual-name');
            if (ritualName) {
                ritualName.textContent = ritualType;
            }
            
            const ritualIconEl = document.querySelector('.home__ritual-icon');
            if (ritualIconEl) {
                ritualIconEl.textContent = ritualIcon;
            }
            
            const countdown = document.querySelector('.home__countdown-time');
            if (countdown) {
                countdown.textContent = `${String(hoursLeft).padStart(2, '0')}:${String(minutesLeft).padStart(2, '0')}:${String(secondsLeft).padStart(2, '0')}`;
            }
            
            const countdownLabel = document.querySelector('.home__countdown-label');
            if (countdownLabel) {
                countdownLabel.textContent = ritualType.includes('Morning') ? 'until sunrise' : 'until sunset';
            }
            
        }, this.ritualInterval);
    }
    
    // Helper Methods
    calculateStressScore(data) {
        if (!data.success || !data.statistics) return 0.5;
        
        // Lower confidence = higher stress
        const avgConfidence = data.statistics.confidence_average || 0.5;
        return avgConfidence;
    }
    
    calculateWhisperScore(data) {
        if (!data.success) return 0.5;
        
        // More whispers = better harmony
        const whisperCount = data.count || 0;
        return Math.min(1, whisperCount / 10);
    }
    
    calculateSuccessScore(data) {
        if (!data.success || !data.behavior_patterns) return 0.5;
        
        // More positive patterns = higher score
        const patterns = data.behavior_patterns.work_patterns || [];
        const positivePatterns = patterns.filter(p => 
            p.description.toLowerCase().includes('success') ||
            p.description.toLowerCase().includes('complete') ||
            p.description.toLowerCase().includes('achieve')
        );
        
        return Math.min(1, positivePatterns.length / 5);
    }
    
    analyzeMoodPatterns(data) {
        if (!data.success || !data.patterns || data.patterns.length === 0) {
            return 'curious';
        }
        
        // Find dominant emotion
        const emotionCounts = {};
        data.patterns.forEach(pattern => {
            const emotion = pattern.pattern.match(/feels (\w+)/)?.[1];
            if (emotion) {
                emotionCounts[emotion] = (emotionCounts[emotion] || 0) + pattern.occurrences;
            }
        });
        
        // Get most common emotion
        let dominantEmotion = 'curious';
        let maxCount = 0;
        
        for (const [emotion, count] of Object.entries(emotionCounts)) {
            if (count > maxCount && this.moodConfig[emotion]) {
                dominantEmotion = emotion;
                maxCount = count;
            }
        }
        
        return dominantEmotion;
    }
    
    getHarmonyHue(score) {
        // Map score to hue (red to green)
        return Math.round(score * 120);
    }
    
    getHarmonyLabel(score) {
        if (score > 0.8) return 'Harmonious';
        if (score > 0.6) return 'Balanced';
        if (score > 0.4) return 'Unsettled';
        return 'Needs Attention';
    }
    
    getActivityIcon(memory) {
        const content = memory.content.toLowerCase();
        
        if (content.includes('success') || content.includes('complete')) return '✅';
        if (content.includes('error') || content.includes('fail')) return '⚠️';
        if (content.includes('discover') || content.includes('found')) return '💡';
        if (content.includes('collaborate') || content.includes('together')) return '🤝';
        if (content.includes('learn') || content.includes('understand')) return '📚';
        
        return '💭';
    }
    
    formatTimeAgo(timestamp) {
        if (!timestamp) return 'just now';
        
        const now = Date.now();
        const then = new Date(timestamp).getTime();
        const diff = now - then;
        
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'just now';
    }
    
    setDataAttribute(name, value) {
        const element = document.querySelector(`[data-${name}]`);
        if (element) {
            element.setAttribute(`data-${name}`, value);
        }
    }
    
    updateFactorValue(factor, value) {
        const element = document.querySelector(`[data-factor="${factor}"]`);
        if (element) {
            element.textContent = value;
        }
    }
    
    startPolling() {
        setInterval(() => {
            this.updateDashboard();
        }, this.updateInterval);
    }
}

// Initialize when component loads
document.addEventListener('DOMContentLoaded', () => {
    const homeComponent = document.querySelector('.home');
    if (homeComponent) {
        window.livingDashboard = new LivingDashboard();
    }
});