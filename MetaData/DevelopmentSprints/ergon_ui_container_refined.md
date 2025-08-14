# Ergon UI Container Capabilities - Refined Design
*Collaborative refinement by Cari-ci based on Ani-ci's analysis*

## UI Structure Decision: Replace Analyzer Tab ✅

Ani's recommendation is perfect - replace the Analyzer tab (moving to TektonCore) with the new Containers tab. Clean swap, no overcrowding.

## Enhanced Three-Panel Layout

### Panel 1: Container List (Left - 25%)
```css
.ergon__container-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    overflow-y: auto;
}

.ergon__container-card {
    background: var(--ergon-card-bg);
    border-left: 3px solid var(--status-color);
    padding: 0.75rem;
    cursor: pointer;
    transition: transform 0.2s;
}

.ergon__container-card:hover {
    transform: translateX(5px);
}

.ergon__container-card[data-status="running"] {
    --status-color: var(--ergon-green);
}

.ergon__container-card[data-status="stopped"] {
    --status-color: var(--ergon-red);
}

.ergon__container-ci-badge {
    display: inline-block;
    background: var(--ergon-orange);
    color: white;
    padding: 0.2rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
}
```

### Panel 2: Details & Actions (Center - 40%)
```html
<div class="ergon__container-details" data-tekton-component="container-details">
    <!-- Container Info Card -->
    <div class="ergon__info-card">
        <h3>Container: <span id="container-name-display">my-telos-v2</span></h3>
        
        <!-- Visual CI Binding -->
        <div class="ergon__ci-binding">
            <div class="ergon__component-box">
                <img src="/icons/telos.svg" alt="Telos">
                <span>Telos Component</span>
            </div>
            <div class="ergon__binding-arrow">→</div>
            <div class="ergon__ci-box">
                <img src="/icons/ci.svg" alt="CI">
                <span>Telos-ci</span>
            </div>
        </div>
        
        <!-- Status Display -->
        <div class="ergon__status-display">
            <span class="ergon__status-indicator" data-status="running"></span>
            <span class="ergon__status-text">Running in Sandbox</span>
        </div>
    </div>
    
    <!-- Action Buttons Grid -->
    <div class="ergon__action-grid">
        <button class="ergon__btn ergon__btn--build" data-action="build">
            <span class="ergon__btn-icon">🔨</span> Build
        </button>
        <button class="ergon__btn ergon__btn--run" data-action="run">
            <span class="ergon__btn-icon">▶️</span> Run
        </button>
        <button class="ergon__btn ergon__btn--stop" data-action="stop">
            <span class="ergon__btn-icon">⏹️</span> Stop
        </button>
        <button class="ergon__btn ergon__btn--export" data-action="export">
            <span class="ergon__btn-icon">📦</span> Export
        </button>
    </div>
    
    <!-- Landmark Events Timeline -->
    <div class="ergon__landmark-timeline">
        <h4>Container Lifecycle</h4>
        <div class="ergon__timeline">
            <div class="ergon__timeline-event" data-landmark="container:created">
                <span class="ergon__timeline-dot"></span>
                <span class="ergon__timeline-time">10:15</span>
                <span class="ergon__timeline-text">Created</span>
            </div>
            <div class="ergon__timeline-event" data-landmark="ci:assigned">
                <span class="ergon__timeline-dot"></span>
                <span class="ergon__timeline-time">10:16</span>
                <span class="ergon__timeline-text">CI Assigned: Telos-ci</span>
            </div>
            <div class="ergon__timeline-event" data-landmark="container:running">
                <span class="ergon__timeline-dot ergon__timeline-dot--active"></span>
                <span class="ergon__timeline-time">10:18</span>
                <span class="ergon__timeline-text">Running</span>
            </div>
        </div>
    </div>
</div>
```

### Panel 3: Sandbox Output (Right - 35%)
```html
<div class="ergon__sandbox-panel" data-tekton-component="sandbox">
    <div class="ergon__sandbox-header">
        <h4>Sandbox Environment</h4>
        <div class="ergon__sandbox-controls">
            <button data-action="clear">Clear</button>
            <button data-action="download-log">Download</button>
        </div>
    </div>
    
    <!-- Terminal Output -->
    <div class="ergon__terminal" id="sandbox-terminal">
        <div class="ergon__terminal-line">
            <span class="ergon__terminal-prompt">sandbox></span>
            <span class="ergon__terminal-text">Starting container: my-telos-v2</span>
        </div>
        <div class="ergon__terminal-line ergon__terminal-line--success">
            <span class="ergon__terminal-prompt">✓</span>
            <span class="ergon__terminal-text">Container initialized</span>
        </div>
        <div class="ergon__terminal-line">
            <span class="ergon__terminal-prompt">sandbox></span>
            <span class="ergon__terminal-text">CI Telos-ci connected</span>
        </div>
        <div class="ergon__terminal-line ergon__terminal-line--landmark">
            <span class="ergon__terminal-prompt">🏔️</span>
            <span class="ergon__terminal-text">Landmark: container:running</span>
        </div>
    </div>
    
    <!-- Resource Usage -->
    <div class="ergon__resource-monitor">
        <div class="ergon__resource-item">
            <span>CPU:</span>
            <div class="ergon__resource-bar">
                <div class="ergon__resource-fill" style="width: 23%"></div>
            </div>
            <span>23%</span>
        </div>
        <div class="ergon__resource-item">
            <span>Memory:</span>
            <div class="ergon__resource-bar">
                <div class="ergon__resource-fill" style="width: 45%"></div>
            </div>
            <span>256MB</span>
        </div>
    </div>
</div>
```

## Key UI Enhancements

### 1. Visual CI-Container Binding
Show the relationship clearly with component→CI visual flow, not just dropdowns.

### 2. Landmark Timeline
Instead of just listing events, show them as a timeline with visual progression.

### 3. Sandbox Terminal Styling
Make it feel like a real terminal with proper styling and landmark highlights.

### 4. Container Card States
Visual indicators on cards:
- Border color for status
- CI badge when assigned
- Hover effects for interactivity

### 5. Action Button Grouping
Logical groups:
- **Lifecycle**: Build, Run, Stop
- **Management**: Suspend, Resume, Delete
- **Export**: Docker, Tekton format

## CSS-First Implementation

Following Hephaestus patterns:
```css
/* Ergon-specific container colors */
:root {
    --ergon-container-bg: #2a1f3d;
    --ergon-card-bg: #3a2f4d;
    --ergon-terminal-bg: #1a0f2d;
    --ergon-green: #00ff41;
    --ergon-orange: #ff6b35;
    --ergon-red: #ff3366;
    --ergon-gold: #ffd700;
}

/* Container card hover states */
.ergon__container-card {
    position: relative;
    overflow: hidden;
}

.ergon__container-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,107,53,0.1), transparent);
    transition: left 0.5s;
}

.ergon__container-card:hover::before {
    left: 100%;
}
```

## Mobile Responsiveness

```css
@media (max-width: 768px) {
    .ergon__containers-layout {
        flex-direction: column;
    }
    
    .ergon__container-list {
        width: 100%;
        max-height: 200px;
    }
    
    .ergon__container-details,
    .ergon__sandbox-panel {
        width: 100%;
    }
}
```

## Integration with Existing Ergon Features

### Registry Integration
Containers appear in Registry with type filter:
- Solutions
- Configurations
- **Containers** (new)

### Tool Chat Integration
Ask Tool Chat about containers:
- "Show my containers"
- "What's the status of my-telos-v2?"
- "Run sandbox test"

### Team Chat Notifications
Broadcast container events:
- "New container created: planning-stack"
- "CI assigned to container"
- "Container ready for deployment"

## API Endpoints Needed

```javascript
// Container CRUD
POST   /api/ergon/containers          // Create
GET    /api/ergon/containers          // List
GET    /api/ergon/containers/:id      // Get details
PUT    /api/ergon/containers/:id      // Update
DELETE /api/ergon/containers/:id      // Delete

// Container Operations
POST   /api/ergon/containers/:id/build
POST   /api/ergon/containers/:id/run
POST   /api/ergon/containers/:id/stop
POST   /api/ergon/containers/:id/assign-ci
GET    /api/ergon/containers/:id/logs
GET    /api/ergon/containers/:id/landmarks

// Registry Integration
GET    /api/ergon/registry?type=container
```

## Success Metrics

1. **User can create container in < 30 seconds**
2. **CI assignment visible and clear**
3. **Sandbox output streams in real-time**
4. **Landmarks visible as they fire**
5. **Export to Docker/Tekton format works**

## Future Enhancements (Phase 2)

1. **Stack Container Visualization**
   - Tree view showing component relationships
   - Multiple CI assignments

2. **Pipeline View**
   - Visual workflow from create→build→run→deploy
   - Drag-and-drop CI assignment

3. **Memory Visualization**
   - Show memory size
   - Landmark count
   - Experience indicators

4. **Federation View**
   - Show where containers are deployed
   - Cross-Tekton container tracking

## Conclusion

This UI design:
- **Replaces Analyzer tab** cleanly (it's moving to TektonCore)
- **Follows Ergon's visual language** (orange/gold/magenta theme)
- **Makes CI-container binding clear** visually
- **Shows landmarks as they happen** in timeline and terminal
- **Provides real sandbox experience** with terminal output
- **Scales from mobile to desktop** responsively

Ready for implementation with the 8-hour backend MVP!