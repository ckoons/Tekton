# Prometheus Component Sprint Brief
*Prepared for Claude in Coder-B*

## Component Overview
- **Purpose**: System monitoring and metrics visualization
- **Complexity**: Medium (4 tabs)
- **Location**: `/Hephaestus/ui/components/prometheus/`
- **Port**: 8106

## Current State Summary
- Multiple onclick handlers for tab navigation
- Mock metrics data throughout
- Real-time update functionality needs verification
- Chart/graph visualizations present

## Your Mission
1. Convert 4-tab navigation to CSS-first pattern
2. Connect to real Prometheus metrics API
3. Ensure real-time metric updates work
4. Maintain chart visualizations
5. Add landmarks and semantic tags

## Key Patterns to Follow
```css
/* Tab visibility - copy from Terma/Apollo/Athena */
#prometheus-tab-metrics:checked ~ .prometheus #metrics-panel {
    display: block;
}
```

## API Endpoints to Connect
- GET `/api/v1/metrics` - System metrics
- GET `/api/v1/health` - Component health
- WebSocket for real-time updates (if present)

## Special Considerations
- Metric displays must auto-refresh
- Graph visualizations should remain functional
- Footer must be visible at all times (even with graphs)

## Success Criteria
- Zero onclick handlers remain
- Real metrics display from API
- All 4 tabs functional with CSS-first navigation
- Clean, maintainable code following Terma patterns

## Time Estimate: 3-4 hours

Good luck! Remember to check Terma's patterns and my work on Apollo/Athena for reference.