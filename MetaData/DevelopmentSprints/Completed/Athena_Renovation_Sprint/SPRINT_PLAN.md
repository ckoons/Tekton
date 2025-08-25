# Sprint: Athena Renovation

## Overview
Bring Athena up to current Tekton standards, remove technical debt, ensure real data in UI (especially knowledge graph and entities), and integrate with aish MCP for all CI communication.

## Goals
1. **Standardize Code**: Follow all current patterns (TektonEnviron, no hardcoding)
2. **Real UI Data**: Remove all mocks, connect to actual backend
3. **MCP Integration**: Use aish MCP for CI communication

## Phase 1: Assessment & Cleanup [0% Complete]

### Tasks
- [ ] Run component and document current state
- [ ] List all mock data locations
- [ ] Find all hardcoded ports/URLs
- [ ] Identify os.environ usage
- [ ] Find unused imports/variables/functions
- [ ] Check test coverage
- [ ] Document UI issues

### Success Criteria
- [ ] Complete inventory of issues
- [ ] Component still runs
- [ ] No code changed yet

### Blocked On
- [ ] Nothing

## Phase 2: Code Standardization [0% Complete]

### Tasks
- [ ] Replace hardcoded ports with TektonEnviron
- [ ] Replace hardcoded URLs with tekton_url()
- [ ] Replace os.environ with TektonEnviron
- [ ] Remove unused imports
- [ ] Remove unused variables  
- [ ] Remove unused functions
- [ ] Fix linting warnings
- [ ] Update error handling

### Success Criteria
- [ ] No hardcoded values
- [ ] Clean linting report
- [ ] Component still works

### Blocked On
- [ ] Phase 1 completion

## Phase 3: Backend Updates [0% Complete]

### Tasks
- [ ] Update API endpoints to standard format
- [ ] Remove mock endpoints
- [ ] Add proper error responses
- [ ] Update to use aish MCP for CI calls
- [ ] Remove direct HTTP CI calls
- [ ] Update API documentation
- [ ] Verify all endpoints work

### Success Criteria
- [ ] All endpoints return real data
- [ ] CI communication through MCP
- [ ] API documentation current

### Blocked On
- [ ] Phase 2 completion
- [ ] aish MCP server availability

## Phase 4: Frontend Updates [0% Complete]

### Tasks
- [ ] Convert tabs to CSS-first radio buttons
- [ ] Remove onclick handlers from all tabs
- [ ] Update tab switching to pure CSS
- [ ] Remove all mock entity data
- [ ] Connect to real backend endpoints
- [ ] Implement real graph visualization
- [ ] Add proper loading states
- [ ] Add proper error handling
- [ ] Test all UI functionality
- [ ] Fix any broken features
- [ ] Update UI to use aish MCP

### Success Criteria
- [ ] UI shows only real data
- [ ] All features work
- [ ] Good error handling

### Blocked On
- [ ] Phase 3 completion

## Phase 5: Testing & Documentation [0% Complete]

### Tasks
- [ ] Write missing unit tests
- [ ] Write integration tests
- [ ] Organize tests in tests/[component]/
- [ ] Update component README
- [ ] Update API documentation
- [ ] Document configuration
- [ ] Run full test suite

### Success Criteria
- [ ] All tests pass
- [ ] Documentation complete
- [ ] Ready for review

### Blocked On
- [ ] Phase 4 completion

## Technical Decisions
[Record as made]

## Out of Scope
- Major feature additions
- UI redesign
- Performance optimization (unless critical)

## Files to Update
```
/Hephaestus/ui/components/athena/athena-component.html
/Hephaestus/ui/scripts/athena/athena-component.js
/athena/athena.py (backend)
/athena/routes.py (API endpoints)
```

## Known Issues from Initial Assessment
- JavaScript onclick handlers on all tabs (lines 17-31)
- Mock entity data in UI (lines 94-119)
- Complex tab switching function (athena_switchTab)
- HTML panel protection code that may interfere
- No real graph visualization connected
- Need to verify graph library availability