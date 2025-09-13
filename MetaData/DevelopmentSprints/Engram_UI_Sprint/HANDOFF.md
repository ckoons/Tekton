# Engram UI Sprint - Handoff Document

## Current State

### What's Been Done
1. **ESR Experience UI Created** - Full HTML/CSS/JS implementation with 6 widgets
2. **Panel Registered** - Experience panel added to Engram navigation
3. **Sprint Planned** - Comprehensive plan for UI transformation

### What's Working
- Experience panel loads in iframe when clicked
- WebSocket connection code ready (needs backend)
- D3.js association graph implemented
- CSS animations for state transitions

### What Needs Work
- Panel needs to be moved left (between Search and Patterns)
- Panel needs renaming from "Experience" to "Cognition"
- Memory panels need consolidation
- Brain visualization not yet implemented

## Next Session Instructions

### PRIORITY 1: Panel Reorganization
1. Edit `/Hephaestus/ui/components/engram/engram-component.html`
2. Move Experience tab between Search and Patterns tabs
3. Rename all instances of "Experience" to "Cognition"
4. Update data attributes and CSS selectors

### PRIORITY 2: Begin Brain Visualization
1. Create new file: `/Hephaestus/ui/components/engram/cognition-brain.js`
2. Implement SVG brain template with regions:
   ```javascript
   const regions = {
       prefrontalCortex: {x: 150, y: 50, r: 30},
       hippocampus: {x: 200, y: 150, r: 25},
       amygdala: {x: 180, y: 180, r: 20},
       // ... etc
   }
   ```
3. Add heat map coloring based on activation levels
4. Connect to existing WebSocket for real-time data

### PRIORITY 3: Consolidate Memory Panels
1. Modify Browse panel to include mode selector
2. Add tabs: Browse | Create | Search | Edit | Timeline
3. Keep content divs, show/hide based on selected mode
4. Add CI selector dropdown to filter memories

### Current File Locations
```
/Users/cskoons/projects/github/Coder-A/
├── Hephaestus/
│   ├── ui/
│   │   ├── components/
│   │   │   └── engram/
│   │   │       ├── engram-component.html (main file to edit)
│   │   │       ├── esr-experience.html (created)
│   │   │       └── esr-experience.js (created)
│   │   └── styles/
│   │       └── engram/
│   │           └── esr-experience.css (created)
└── Engram/
    └── engram/
        └── core/
            └── experience/ (ESR backend code)
```

### Testing Instructions
1. Start Hephaestus UI
2. Navigate to Engram component
3. Click Cognition tab (after renaming)
4. Verify brain visualization loads
5. Test CI selector dropdown
6. Verify WebSocket connection attempts

### Known Issues
- WebSocket will fail until Engram backend implements /experience/stream endpoint
- Some sample data is still hardcoded (intentional for UI testing)
- Performance not yet optimized for complex animations

### Design Decisions to Maintain
- NO emojis/icons in menu navigation
- CSS-first approach for panel switching
- Card-based layout for information chunks
- Real-time updates via WebSocket
- Multi-window observation capability

### Questions for Casey
1. Preferred brain view: lateral (side) or dorsal (top)?
2. Should historical data persist between sessions?
3. Color scheme preferences for brain heat map?
4. Maximum time range for timeline scrubber?

## Success Metrics
- [ ] Cognition panel shows animated brain
- [ ] CI selector works across all panels
- [ ] Memory operations unified in one panel
- [ ] Pattern discovery visually compelling
- [ ] Multi-window observation functional