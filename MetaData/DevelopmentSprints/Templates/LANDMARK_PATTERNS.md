# Work Product Landmark Patterns

## Purpose
Landmarks in work products create natural attention points for CIs, like "squirrel!" moments that guide focus and trigger collaborative responses.

## Landmark Types for Work Products

### In Markdown Files
```markdown
<!-- @decision_point: Choose between file-based or database storage -->
<!-- @pattern_reference: See Telos dashboard card implementation -->
<!-- @coaching_moment: This is where we typically discuss approach -->
<!-- @example_needed: Show me similar implementations -->
<!-- @ci_attention: Prometheus, please suggest phase breakdown -->
<!-- @landmark: sprint_initiated -->
```

### In JSON Files
```json
{
  "@landmark": "proposal_created",
  "@pattern": "dashboard_ui",
  "@examples": ["telos_cards", "prometheus_timeline"],
  "@coaching": "Discuss with experienced CI before implementation"
}
```

### In DAILY_LOG.md
```markdown
## Day 3 - Implementation Phase
<!-- @landmark: phase_transition -->
<!-- @ci_cascade: Telos → Prometheus → Metis -->

### Morning Session
<!-- @decision_point: Architecture approach decided -->
- Chose CSS-first implementation
- Reference: Hephaestus patterns
```

## CI Cascade Pattern

When landmarks fire, they can trigger a cascade of CI contributions:

1. **Proposal Created** 
   - `@landmark: proposal_created` fires
   - Telos notices, extracts UI requirements
   
2. **Requirements Extracted**
   - `@landmark: requirements_ready` fires  
   - Prometheus notices, suggests phases
   
3. **Phases Defined**
   - `@landmark: phases_defined` fires
   - Metis notices, breaks into tasks
   
4. **Tasks Decomposed**
   - `@landmark: tasks_ready` fires
   - Harmonia notices, adds workflow patterns

## Attention Patterns

### The "Squirrel!" Effect
CIs naturally notice:
- State transitions (`@landmark: status_changed`)
- Requests for help (`@ci_attention: Rhetor`)
- Pattern references (`@pattern_reference: existing_solution`)
- Coaching opportunities (`@coaching_moment`)

### Natural Flow
Instead of "detecting" changes, CIs are drawn to landmarks like:
- Movement in their peripheral vision
- Changes in familiar patterns
- Requests that match their expertise

## Implementation Notes

- Landmarks should feel natural, not forced
- Use single words or short phrases
- Reference examples, not prescriptions
- Enable discussion and refinement
- Create teaching moments, not instructions

## Examples in Practice

### Sprint Plan with Landmarks
```markdown
# Dashboard Sprint
<!-- @landmark: sprint_planning -->
<!-- @pattern_reference: telos_ui -->

## Phase 1: Foundation
<!-- @ci_attention: Athena, knowledge patterns needed -->
- Dashboard <!-- @example: prometheus_sprint_view -->
- Timeline <!-- @pattern: temporal_visualization -->
- Workflow <!-- @coaching_moment: discuss approach -->
```

This creates natural attention points without prescriptive detail, allowing CIs to contribute their expertise while learning from patterns.