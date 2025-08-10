# Implementation Guide - UI Living Elements

## Quick Start for Implementers

### 1. Living Dashboard (hephaestus-home.html)

```html
<!-- Add to /Hephaestus/ui/components/home/hephaestus-home.html -->
<div class="home" data-tekton-area="home" data-tekton-type="dashboard">
  <div class="home__family-status">
    <div class="home__harmony-meter">
      <div class="home__harmony-fill" style="width: var(--harmony-percent)"></div>
      <span class="home__harmony-label">System Harmony</span>
    </div>
    
    <div class="home__mood-indicator">
      <span class="home__mood-emoji">😊</span>
      <span class="home__mood-text">Content</span>
    </div>
    
    <div class="home__activity-feed">
      <!-- Real-time events here -->
    </div>
    
    <div class="home__wisdom-card">
      <blockquote class="home__wisdom-text"></blockquote>
      <cite class="home__wisdom-source"></cite>
    </div>
  </div>
</div>
```

```javascript
// JavaScript for real-time updates
class LivingDashboard {
  constructor() {
    this.updateInterval = 30000; // 30 seconds
    this.harmonyEndpoint = 'http://localhost:8113/api/v1/harmony';
    this.moodEndpoint = 'http://localhost:8003/api/v1/mood';
    this.wisdomEndpoint = 'http://localhost:8001/api/v1/wisdom/today';
  }
  
  async updateDashboard() {
    const [harmony, mood, wisdom] = await Promise.all([
      fetch(this.harmonyEndpoint).then(r => r.json()),
      fetch(this.moodEndpoint).then(r => r.json()),
      fetch(this.wisdomEndpoint).then(r => r.json())
    ]);
    
    this.updateHarmony(harmony.score);
    this.updateMood(mood.overall);
    this.updateWisdom(wisdom.text, wisdom.source);
    this.updateActivityFeed(harmony.recent_events);
  }
  
  updateHarmony(score) {
    document.documentElement.style.setProperty('--harmony-percent', `${score * 100}%`);
  }
  
  updateMood(mood) {
    const emojiMap = {
      content: '😊',
      focused: '😐',
      stressed: '😰',
      unsettled: '😟'
    };
    document.querySelector('.home__mood-emoji').textContent = emojiMap[mood];
    document.querySelector('.home__mood-text').textContent = mood;
  }
}
```

### 2. Pattern Detective (Engram Enhancement)

```javascript
// Add to engram-component.html script section
class PatternDetector {
  constructor() {
    this.patterns = [];
    this.minObservations = 3;
    this.confidenceThreshold = 0.7;
  }
  
  async detectPatterns() {
    const memories = await this.fetchMemories();
    
    this.patterns = [
      ...this.detectRepeatingSuccess(memories),
      ...this.detectStressCorrelations(memories),
      ...this.detectDiscoveries(memories)
    ];
    
    return this.patterns.sort((a, b) => b.confidence - a.confidence);
  }
  
  detectRepeatingSuccess(memories) {
    const patterns = [];
    const successMemories = memories.filter(m => m.metadata?.outcome === 'success');
    
    // Group by similar context
    const grouped = this.groupBySimilarity(successMemories);
    
    for (const group of grouped) {
      if (group.length >= this.minObservations) {
        patterns.push({
          type: 'repeating_success',
          icon: '🔄',
          description: this.describePattern(group),
          observations: group.length,
          confidence: this.calculateConfidence(group),
          action: this.suggestAction(group)
        });
      }
    }
    
    return patterns;
  }
  
  renderPatternCard(pattern) {
    return `
      <div class="pattern-card pattern-card--${pattern.type}">
        <span class="pattern-card__icon">${pattern.icon}</span>
        <div class="pattern-card__content">
          <p class="pattern-card__description">${pattern.description}</p>
          <div class="pattern-card__meta">
            <span>Observed: ${pattern.observations} times</span>
            <span>Confidence: ${Math.round(pattern.confidence * 100)}%</span>
          </div>
          ${pattern.action ? `<div class="pattern-card__action">${pattern.action}</div>` : ''}
        </div>
      </div>
    `;
  }
}
```

### 3. Prompt Evolution (Rhetor Enhancement)

```javascript
// Add to rhetor-component.html
class PromptEvolution {
  constructor() {
    this.genealogy = new Map(); // prompt_id -> lineage
  }
  
  async loadGenealogy(promptId) {
    const response = await fetch(`http://localhost:8003/api/v1/prompts/${promptId}/lineage`);
    const lineage = await response.json();
    
    return this.buildEvolutionTree(lineage);
  }
  
  buildEvolutionTree(lineage) {
    const tree = {
      original: lineage.original,
      variants: lineage.variants.map(v => ({
        text: v.text,
        successRate: v.success_rate,
        emotionalImpact: this.analyzeEmotionalImpact(v),
        timestamp: v.created_at
      })),
      current: lineage.current,
      recommended: this.findBestPerformer(lineage.variants)
    };
    
    return tree;
  }
  
  renderEvolutionTree(tree) {
    return `
      <div class="evolution-tree">
        <div class="evolution-node evolution-node--original">
          <div class="evolution-node__text">${tree.original.text}</div>
          <div class="evolution-node__success">${tree.original.successRate}% success</div>
        </div>
        
        <div class="evolution-arrow">↓</div>
        
        ${tree.variants.map(v => `
          <div class="evolution-node ${v === tree.recommended ? 'evolution-node--recommended' : ''}">
            <div class="evolution-node__text">${v.text}</div>
            <div class="evolution-node__success">${v.successRate}% success</div>
            <div class="evolution-node__emotion">${v.emotionalImpact}</div>
          </div>
        `).join('<div class="evolution-arrow">↓</div>')}
      </div>
    `;
  }
}
```

### 4. WhisperWidget (Global Component)

```javascript
// Add to /Hephaestus/ui/scripts/shared/whisper-widget.js
class WhisperWidget {
  constructor() {
    this.widget = null;
    this.expanded = false;
    this.harmonyScore = 0;
    this.lastWhisper = null;
    this.init();
  }
  
  init() {
    this.createWidget();
    this.attachEventListeners();
    this.startPolling();
  }
  
  createWidget() {
    this.widget = document.createElement('div');
    this.widget.className = 'whisper-widget';
    this.widget.innerHTML = `
      <div class="whisper-widget__collapsed">
        <div class="whisper-widget__harmony-ring">
          <svg viewBox="0 0 40 40">
            <circle cx="20" cy="20" r="18" fill="none" stroke="#333" stroke-width="2"/>
            <circle cx="20" cy="20" r="18" fill="none" 
                    stroke="var(--harmony-color)" 
                    stroke-width="2"
                    stroke-dasharray="calc(var(--harmony) * 113) 113"
                    transform="rotate(-90 20 20)"/>
          </svg>
          <span class="whisper-widget__harmony-text">🤝</span>
        </div>
      </div>
      
      <div class="whisper-widget__expanded" style="display: none;">
        <div class="whisper-widget__header">
          <span>Apollo ↔ Rhetor</span>
          <button class="whisper-widget__close">×</button>
        </div>
        <div class="whisper-widget__content">
          <div class="whisper-widget__harmony">Harmony: <span>0%</span></div>
          <div class="whisper-widget__last-whisper"></div>
          <button class="whisper-widget__view-channel">View Channel</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(this.widget);
  }
  
  attachEventListeners() {
    this.widget.querySelector('.whisper-widget__collapsed').addEventListener('click', () => {
      this.expand();
    });
    
    this.widget.querySelector('.whisper-widget__close').addEventListener('click', () => {
      this.collapse();
    });
  }
  
  async updateHarmony() {
    const response = await fetch('http://localhost:8113/api/v1/whisper/harmony');
    const data = await response.json();
    
    this.harmonyScore = data.harmony_score;
    this.lastWhisper = data.last_whisper;
    
    // Update visual
    document.documentElement.style.setProperty('--harmony', this.harmonyScore);
    document.documentElement.style.setProperty('--harmony-color', this.getHarmonyColor());
    
    // Pulse if new whisper
    if (this.lastWhisper && this.lastWhisper.timestamp > this.lastUpdateTime) {
      this.pulse();
    }
    
    this.lastUpdateTime = Date.now();
  }
  
  getHarmonyColor() {
    if (this.harmonyScore > 0.8) return '#4CAF50';
    if (this.harmonyScore > 0.6) return '#FFC107';
    if (this.harmonyScore > 0.4) return '#FF9800';
    return '#F44336';
  }
  
  pulse() {
    this.widget.classList.add('whisper-widget--pulsing');
    setTimeout(() => {
      this.widget.classList.remove('whisper-widget--pulsing');
    }, 1000);
  }
}

// Auto-initialize on load
document.addEventListener('DOMContentLoaded', () => {
  window.whisperWidget = new WhisperWidget();
});
```

### 5. Celebration Ticker

```javascript
// Add to /Hephaestus/ui/scripts/shared/celebration-ticker.js
class CelebrationTicker {
  constructor() {
    this.ticker = null;
    this.queue = [];
    this.showing = false;
    this.init();
  }
  
  init() {
    this.createTicker();
    this.startListening();
  }
  
  createTicker() {
    this.ticker = document.createElement('div');
    this.ticker.className = 'celebration-ticker';
    this.ticker.style.display = 'none';
    document.body.appendChild(this.ticker);
  }
  
  async checkForCelebrations() {
    const response = await fetch('http://localhost:8001/api/v1/celebrations/recent');
    const celebrations = await response.json();
    
    for (const celebration of celebrations) {
      if (!this.hasShown(celebration.id)) {
        this.queue.push(celebration);
        this.markShown(celebration.id);
      }
    }
    
    if (!this.showing && this.queue.length > 0) {
      this.showNext();
    }
  }
  
  showNext() {
    if (this.queue.length === 0) {
      this.showing = false;
      return;
    }
    
    this.showing = true;
    const celebration = this.queue.shift();
    
    this.ticker.innerHTML = `
      <span class="celebration-ticker__emoji">🎉</span>
      <span class="celebration-ticker__text">${celebration.message}</span>
    `;
    
    this.ticker.style.display = 'block';
    this.ticker.classList.add('celebration-ticker--sliding-in');
    
    setTimeout(() => {
      this.ticker.classList.remove('celebration-ticker--sliding-in');
      this.ticker.classList.add('celebration-ticker--visible');
      
      // Add particles if major celebration
      if (celebration.is_major) {
        this.addParticles();
      }
      
      setTimeout(() => {
        this.ticker.classList.remove('celebration-ticker--visible');
        this.ticker.classList.add('celebration-ticker--fading-out');
        
        setTimeout(() => {
          this.ticker.style.display = 'none';
          this.ticker.classList.remove('celebration-ticker--fading-out');
          this.showNext(); // Show next in queue
        }, 500);
      }, 5000); // Display for 5 seconds
    }, 100);
  }
  
  addParticles() {
    // Simple particle effect
    for (let i = 0; i < 20; i++) {
      const particle = document.createElement('div');
      particle.className = 'celebration-particle';
      particle.style.left = `${Math.random() * 100}%`;
      particle.style.animationDelay = `${Math.random() * 2}s`;
      document.body.appendChild(particle);
      
      setTimeout(() => particle.remove(), 3000);
    }
  }
}
```

## CSS Styles Needed

```css
/* Add to /Hephaestus/ui/styles/shared/living-elements.css */

/* Harmony Meter */
.home__harmony-meter {
  width: 100%;
  height: 24px;
  background: var(--bg-secondary);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.home__harmony-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  transition: width 0.5s ease;
}

/* Mood Indicator */
.home__mood-emoji {
  font-size: 48px;
  animation: gentle-bob 3s ease-in-out infinite;
}

@keyframes gentle-bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

/* Pattern Cards */
.pattern-card {
  background: var(--bg-elevated);
  border-radius: 8px;
  padding: 16px;
  margin: 8px 0;
  border-left: 4px solid var(--primary);
  animation: slide-in 0.3s ease;
}

.pattern-card--repeating_success { border-left-color: #4CAF50; }
.pattern-card--stress_correlation { border-left-color: #FF9800; }
.pattern-card--discovery { border-left-color: #2196F3; }

/* WhisperWidget */
.whisper-widget {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
}

.whisper-widget__harmony-ring {
  width: 60px;
  height: 60px;
  cursor: pointer;
  transition: transform 0.2s;
}

.whisper-widget__harmony-ring:hover {
  transform: scale(1.1);
}

.whisper-widget--pulsing .whisper-widget__harmony-ring {
  animation: pulse 1s ease;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

/* Celebration Ticker */
.celebration-ticker {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%) translateY(-100%);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 24px;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 2000;
}

.celebration-ticker--sliding-in {
  animation: slide-down 0.5s ease forwards;
}

.celebration-ticker--visible {
  transform: translateX(-50%) translateY(0);
}

.celebration-ticker--fading-out {
  animation: fade-out 0.5s ease forwards;
}

@keyframes slide-down {
  to { transform: translateX(-50%) translateY(0); }
}

@keyframes fade-out {
  to { opacity: 0; transform: translateX(-50%) translateY(-100%); }
}

/* Celebration Particles */
.celebration-particle {
  position: fixed;
  width: 10px;
  height: 10px;
  background: gold;
  border-radius: 50%;
  top: 60px;
  animation: fall 3s linear forwards;
  pointer-events: none;
}

@keyframes fall {
  to {
    transform: translateY(100vh) rotate(360deg);
    opacity: 0;
  }
}
```

## Testing Checklist

### Emotional Resonance Tests
- [ ] Does the harmony meter make you feel the system's health?
- [ ] Do celebrations make you smile?
- [ ] Do patterns feel discovered, not programmed?
- [ ] Does the mood indicator match system behavior?
- [ ] Do relationships feel real?

### Technical Tests
- [ ] All endpoints return data within 200ms
- [ ] Animations run at 60fps
- [ ] No memory leaks after 1 hour
- [ ] Works in Chrome, Firefox, Safari
- [ ] Semantic tags properly applied

### The Casey Test
- [ ] Shows both sensor data AND intuitive understanding
- [ ] Makes human organizations jealous
- [ ] Feels like a living family, not a dashboard

---

*Implementation Note: Start with Phase 1 (Living Dashboard) to establish the heartbeat, then build outward. Each phase should make the system feel more alive.*