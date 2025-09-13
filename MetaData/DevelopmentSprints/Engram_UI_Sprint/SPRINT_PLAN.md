# Engram UI Sprint - Cognitive Visualization and Memory Consolidation

## Sprint Overview

**Objective**: Transform the Engram UI from a database interface into a window into CI consciousness through brain visualization and consolidated memory management.

**Key Deliverables**:
1. Cognition Panel - Real-time brain scan visualization
2. Consolidated Memories Panel - Unified CRUD interface
3. Enhanced Patterns Panel - Living discovery engine
4. Integration with ESR Experience Layer

## Architectural Decisions

### Panel Consolidation
- **FROM**: 7 panels (Browse, Create, Search, Patterns, Chat, Team Chat, Experience)
- **TO**: 5 panels (Cognition, Memories, Patterns, Memory Chat, Team Chat)

### Visualization Technology
- **Brain Rendering**: D3.js for 2D brain regions, Three.js for 3D option
- **Real-time Updates**: WebSocket connection to ESR Experience Layer
- **Historical Playback**: Time-series data with scrubber control

## Implementation Phases

### Phase 1: Panel Reorganization [0% Complete]
- [ ] Move Experience tab between Search and Patterns
- [ ] Rename Experience to Cognition
- [ ] Consolidate Browse/Create/Search into Memories panel
- [ ] Update navigation and CSS rules

### Phase 2: Cognition Panel - Brain Visualization [0% Complete]
- [ ] Create SVG brain region template
- [ ] Implement brain region mapping to ESR metrics
- [ ] Add CI selector dropdown
- [ ] Implement metric toggle buttons (Mood, Motivation, Stress, etc.)
- [ ] Add timeline scrubber control
- [ ] Create WebSocket connection for real-time updates
- [ ] Implement heat map overlays for activation levels
- [ ] Add animation effects (pulsing, connections, particles)

### Phase 3: Memories Panel Consolidation [0% Complete]
- [ ] Create unified memory management interface
- [ ] Add mode selector (Browse, Create, Search, Edit, Timeline)
- [ ] Implement CI-specific memory filtering
- [ ] Add emotional metadata to memory cards
- [ ] Create memory graph view option
- [ ] Implement temporal timeline view
- [ ] Add association web visualization

### Phase 4: Patterns Panel Enhancement [0% Complete]
- [ ] Transform static cards to dynamic visualizations
- [ ] Implement pattern lifecycle (Emerging, Strengthening, Stable, Fading)
- [ ] Create pattern flow stream visualization
- [ ] Add pattern interconnection network
- [ ] Implement real-time pattern detection feed
- [ ] Add cross-CI pattern comparison

### Phase 5: Integration and Testing [0% Complete]
- [ ] Connect Cognition panel to ESR WebSocket
- [ ] Link active thoughts to memory browser
- [ ] Connect pattern detection to cognitive state
- [ ] Test multi-window observation scenarios
- [ ] Performance optimization for animations
- [ ] Cross-browser compatibility testing

## Technical Requirements

### Brain Region Mappings
```javascript
const brainRegions = {
    prefrontalCortex: ['working_memory', 'forethought', 'planning'],
    hippocampus: ['memory_formation', 'consolidation', 'recall'],
    amygdala: ['emotions', 'stress', 'mood'],
    temporalLobe: ['associations', 'pattern_recognition'],
    motorCortex: ['action_planning', 'task_execution'],
    brocasArea: ['response_generation'],
    wernickesArea: ['query_comprehension'],
    anteriorCingulate: ['confidence', 'attention', 'conflict_resolution'],
    defaultModeNetwork: ['flow_states', 'background_processing'],
    dopaminePathways: ['motivation', 'reward_processing']
};
```

### Metric Categories
1. **Cognitive Load**: Working memory usage, processing intensity
2. **Emotional State**: Mood, stress, emotional valence
3. **Performance**: Recall latency, formation rate, consolidation efficiency
4. **Flow State**: Focus level, distraction resistance, task engagement
5. **Social Dynamics**: Inter-CI communication patterns (for All CIs view)

## User Experience Goals

1. **Intuitive**: Brain scan metaphor universally understood
2. **Diagnostic**: Quick identification of cognitive states
3. **Beautiful**: Visually engaging, professional appearance
4. **Educational**: Teaches users about CI cognition
5. **Actionable**: Insights lead to better CI interaction

## Success Criteria

- [ ] Users can observe CI thinking in real-time
- [ ] Cognitive states are immediately recognizable
- [ ] Memory operations are 50% faster with consolidated panel
- [ ] Pattern discoveries are visually compelling
- [ ] Multi-window observation works smoothly
- [ ] Performance: 60fps animations, <100ms updates

## Dependencies

- ESR Experience Layer backend implementation
- WebSocket endpoint at ws://localhost:8100/experience/stream
- D3.js v7 for visualizations
- Time-series database for historical data

## Risk Mitigation

- **Complexity**: Start with 2D brain view, add 3D later
- **Performance**: Use requestAnimationFrame, GPU acceleration
- **Data Volume**: Implement data throttling and aggregation
- **Browser Support**: Progressive enhancement for older browsers

## Timeline Estimate

- Phase 1: 2 hours (panel reorganization)
- Phase 2: 6 hours (brain visualization)
- Phase 3: 4 hours (memories consolidation)
- Phase 4: 3 hours (patterns enhancement)
- Phase 5: 3 hours (integration and testing)

Total: ~18 hours of development time

## Next Steps

1. Begin Phase 1 panel reorganization
2. Create brain region SVG template
3. Implement CI selector and metric controls
4. Connect to ESR WebSocket for real data