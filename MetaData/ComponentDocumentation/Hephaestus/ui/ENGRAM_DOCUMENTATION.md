# Engram UI Documentation

## Overview
Engram is an advanced cognitive interface system that provides real-time visualization and analysis of AI thought processes, memory formation, and pattern recognition. It consists of three main panels: Memories, Cognition, and Patterns.

## Architecture

### Component Structure
```
/Hephaestus/ui/components/engram/
├── engram-component.html       # Main component with tab navigation
├── memories.js                  # Memory management and visualization
├── cognition-brain-3d.js       # 3D brain visualization with Three.js
├── patterns-analytics.js       # Pattern detection and analysis engine
└── patterns-simple.html        # Fallback simple pattern view
```

### Style Structure
```
/Hephaestus/ui/styles/engram/
├── memories.css                # Memory panel styles
├── cognition.css               # Cognition panel styles
└── patterns-discovery.css      # Patterns panel styles
```

## Component Details

### 1. Memories Panel
**Purpose**: Track and visualize memory formation, storage, and retrieval processes.

**Features**:
- Real-time memory card display
- Memory strength indicators
- Temporal organization
- Search and filter capabilities
- Memory type categorization (episodic, semantic, procedural)

**Key Classes**:
- `MemoryManager`: Handles memory CRUD operations
- `MemoryCard`: Individual memory visualization
- `MemoryTimeline`: Temporal memory organization

### 2. Cognition Panel
**Purpose**: 3D visualization of brain activity and cognitive processes.

**Features**:
- Interactive 3D brain model using Three.js
- Anatomical region highlighting
- Real-time activity visualization
- Drag-to-rotate interaction
- Region-specific function display

**Brain Regions Implemented**:
```javascript
{
  prefrontalCortex: ['working_memory', 'planning', 'decision_making'],
  hippocampus: ['encoding', 'consolidation', 'retrieval'],
  amygdala: ['emotional_tagging', 'fear_response', 'memory_modulation'],
  temporalLobe: ['semantic_memory', 'language', 'recognition'],
  parietalLobe: ['spatial_processing', 'attention', 'integration'],
  occipitalLobe: ['visual_processing', 'pattern_recognition'],
  cerebellum: ['procedural_memory', 'motor_learning', 'coordination'],
  basalGanglia: ['habit_formation', 'reward_processing', 'motivation'],
  cingulateCortex: ['error_detection', 'conflict_monitoring', 'attention'],
  thalamus: ['relay_station', 'consciousness', 'alertness']
}
```

**Visualization Details**:
- **Container**: Full-height 3D canvas
- **Camera**: Perspective view at z:300
- **Lighting**: Ambient + 2 directional lights
- **Interaction**: Mouse drag for rotation
- **Animation**: Continuous rotation when idle, region pulsing

### 3. Patterns Panel
**Purpose**: Advanced cognitive pattern analysis and learning trajectory tracking.

**Features**:
- Learning trajectory timeline
- Concept formation graph
- Active pattern detection
- Cognitive insights dashboard
- Cross-panel highlighting system

**Pattern Types**:
- **Emerging**: New patterns being formed
- **Strengthening**: Patterns gaining consistency
- **Stable**: Established cognitive patterns
- **Cyclical**: Recurring thought processes
- **Fading**: Diminishing patterns

## Color Coding System

### Thought Type Colors (Vertex Centers)
```css
.thought-hypothesis { background: #00BCD4; }    /* Cyan - Tentative ideas */
.thought-observation { background: #FFC107; }   /* Amber - Facts noticed */
.thought-insight { background: #9C27B0; }       /* Purple - Breakthroughs */
.thought-question { background: #FF5722; }      /* Deep Orange - Unknowns */
.thought-solution { background: #4CAF50; }      /* Green - Answers */
.thought-problem { background: #F44336; }       /* Red - Issues found */
.thought-pattern { background: #2196F3; }       /* Blue - Recurring structures */
.thought-memory { background: #795548; }        /* Brown - Past experiences */
```

### Relationship Type Colors (Edges)
```css
.edge-causal { stroke: #4CAF50; }              /* Green - A leads to B */
.edge-contradicts { stroke: #F44336; }         /* Red dashed - Conflict */
.edge-supports { stroke: #2196F3; }            /* Blue solid - Evidence */
.edge-questions { stroke: #FF9800; }           /* Orange dotted - Uncertainty */
.edge-transforms { stroke: #9C27B0; }          /* Purple gradient - Evolution */
.edge-recalls { stroke: #607D8B; }             /* Gray faded - Memory link */
.edge-synthesizes { stroke: #00BCD4; }         /* Cyan merged - Combination */
```

### Confidence Levels (Border Styling)
```javascript
const confidenceLevels = {
  random_thought: { width: 1, opacity: 0.3 },
  exploring: { width: 2, opacity: 0.5 },
  developing: { width: 3, opacity: 0.7 },
  confident: { width: 4, opacity: 0.85 },
  certain: { width: 5, opacity: 1.0 }
};
```

### Novelty/Excitement (Border Colors)
```javascript
const noveltyColors = {
  routine: '#607D8B',      // Cool gray
  familiar: '#78909C',     // Blue-gray
  interesting: '#5C6BC0',  // Indigo
  novel: '#AB47BC',        // Purple
  breakthrough: '#EC407A', // Pink
  revolutionary: '#FFD600' // Gold pulse
};
```

## Navigation System

The Engram UI uses a CSS-based tab navigation system:

```html
<!-- Radio inputs for tab selection -->
<input type="radio" name="engram-nav-tab" id="engram-tab-memories" checked>
<input type="radio" name="engram-nav-tab" id="engram-tab-cognition">
<input type="radio" name="engram-nav-tab" id="engram-tab-patterns">

<!-- Tab labels act as navigation buttons -->
<label for="engram-tab-memories" class="engram__tab">Memories</label>
<label for="engram-tab-cognition" class="engram__tab">Cognition</label>
<label for="engram-tab-patterns" class="engram__tab">Patterns</label>

<!-- CSS controls panel visibility -->
#engram-tab-memories:checked ~ .engram #memories-panel { display: block; }
#engram-tab-cognition:checked ~ .engram #cognition-panel { display: block; }
#engram-tab-patterns:checked ~ .engram #patterns-panel { display: block; }
```

## WebSocket Integration

Real-time data streams for each panel:

```javascript
// Cognition WebSocket
ws://localhost:8100/cognition/stream
// Sends: { type: 'region_activation', region: string, intensity: number }

// Patterns WebSocket  
ws://localhost:8100/patterns/stream
// Sends: { type: 'pattern_detected', pattern: object, timestamp: number }

// Memories WebSocket
ws://localhost:8100/memories/stream
// Sends: { type: 'memory_formed', memory: object, strength: number }
```

## Initialization

Each component self-initializes when its panel becomes visible:

```javascript
// Pattern for component initialization
document.addEventListener('click', (e) => {
    if (e.target.closest('[data-tab="patterns"]')) {
        setTimeout(initializePatternsAnalytics, 100);
    }
});
```

## Performance Considerations

1. **Three.js Optimization**: Single renderer instance, dispose on panel switch
2. **Canvas Rendering**: RequestAnimationFrame for smooth animations
3. **Data Updates**: 2-second intervals for pattern detection
4. **Memory Management**: Limit trajectory nodes to last 10 entries
5. **DOM Updates**: Batch updates, use DocumentFragment when possible

## Future Enhancements

1. **Timeline Slider**: Temporal navigation through concept formation
2. **Cross-Panel Highlighting**: Unified selection across all panels
3. **Data Persistence**: Save/load cognitive sessions
4. **Export Capabilities**: Generate reports from pattern analysis
5. **Real CI Integration**: Connect to actual CI cognitive streams
6. **Multi-CI Comparison**: Side-by-side cognitive analysis

## Browser Compatibility

- **Required**: Modern browsers with ES6+ support
- **Three.js**: WebGL support required for 3D visualization
- **Canvas**: 2D context for pattern graphs
- **WebSockets**: For real-time data streaming

## Dependencies

- Three.js r128 (3D visualization)
- D3.js v7 (data visualization)
- Native WebSocket API
- Canvas API
- ES6 modules