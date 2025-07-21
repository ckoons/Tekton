# Harmonia Component Sprint Brief
*Prepared for Claude in Coder-C*

## Component Overview
- **Purpose**: Workflow orchestration and state management
- **Complexity**: Low-Medium (3 tabs)
- **Location**: `/Hephaestus/ui/components/harmonia/`
- **Port**: 8107

## Current State Summary
- Simpler component with 3 tabs
- Workflow visualization features
- Mock workflow data
- State management functionality

## Your Mission
1. Convert 3-tab navigation to CSS-first pattern
2. Connect to real Harmonia workflow API
3. Ensure workflow state updates work
4. Maintain workflow visualizations
5. Add landmarks and semantic tags

## Key Patterns to Follow
```html
<!-- Radio button pattern from Terma -->
<input type="radio" name="harmonia-tab" id="harmonia-tab-workflows" checked style="display: none;">
<input type="radio" name="harmonia-tab" id="harmonia-tab-states" style="display: none;">
<input type="radio" name="harmonia-tab" id="harmonia-tab-history" style="display: none;">
```

## API Endpoints to Connect
- GET `/api/v1/workflows` - List workflows
- GET `/api/v1/workflows/{id}/state` - Workflow state
- POST `/api/v1/workflows/{id}/transition` - State transitions
- GET `/api/v1/history` - Workflow history

## Special Considerations
- Workflow diagrams should remain interactive
- State transitions must update in real-time
- Keep the UI simple and clean
- Footer visibility is crucial!

## Success Criteria
- Zero onclick handlers remain
- Real workflow data from API
- All 3 tabs functional with CSS-first navigation
- State management working properly
- Clean code following established patterns

## Time Estimate: 2-3 hours

This is a great starter component - simpler than Prometheus but still meaningful. Focus on getting the patterns right, and the rest will follow naturally.

Remember: "Simple, works, hard to screw up!"