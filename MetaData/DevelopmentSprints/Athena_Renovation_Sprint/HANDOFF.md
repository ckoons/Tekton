# Handoff Document: Athena Renovation

## Current Status
**Phase**: Not Started  
**Progress**: 0% Complete  
**Last Updated**: 2025-01-20

## What Was Just Completed
- Template copied for Athena
- Initial context document created with detailed analysis
- Sprint plan updated with Athena-specific issues
- Ready to begin renovation

## What Needs To Be Done Next
1. **IMMEDIATE**: Test current Athena functionality
2. **FIRST**: Convert tabs to CSS-first navigation
3. **THEN**: Remove mock data and connect to real backend

## Current Blockers
- [ ] None yet

## Important Context
- Athena is used for: Knowledge graph visualization and entity management
- Key dependencies: Graph visualization library (needs verification)
- Known issues:
  - JavaScript onclick handlers on all 5 tabs
  - Mock entity data hardcoded in HTML
  - Complex tab switching function
  - HTML panel protection code

## Test Status
- Existing tests: Unknown
- Test location: `tests/athena/`

## Files Being Modified
```
/Hephaestus/ui/components/athena/athena-component.html (main UI file)
/Hephaestus/ui/scripts/athena/athena-component.js (component script)
/athena/athena.py (backend - needs assessment)
/athena/routes.py (API endpoints - needs assessment)
```

## Commands to Run on Startup
```bash
# Navigate to UI component
cd $TEKTON_ROOT/Hephaestus/ui/components/athena

# Check backend status
curl -s http://localhost:8105/health || echo "Athena backend not responding"

# Run existing tests if any
pytest tests/athena/ -v || echo "No tests found"
```

## Questions Needing Answers
1. Is a graph visualization library already included?
2. What entity types does the backend support?
3. What query syntax should the Query Builder use?
4. Should we keep the HTML panel protection code?

## Do NOT Touch
- Chat functionality (both Knowledge and Team chat work)
- BEM CSS naming convention (already correct)
- Semantic tags (already present and correct)

## Notes for Next Session
- Start by testing current Athena functionality
- Pay special attention to onclick handlers (lines 17-31)
- Check if graph visualization loads any data
- Test all backend endpoints at port 8105
- Follow Apollo renovation pattern for CSS-first tabs

Remember: "Simple, works, hard to screw up"