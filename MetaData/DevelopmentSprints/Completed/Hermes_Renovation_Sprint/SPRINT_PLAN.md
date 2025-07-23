# Sprint: Hermes Renovation

## Overview
Bring Hermes up to current Tekton standards with CSS-first UI patterns, remove technical debt, ensure real data in UI (especially service registry and message monitoring), and integrate with aish MCP for all AI communication.

## Goals
1. **CSS-First UI**: Convert all onclick handlers to CSS-based interactions
2. **Standardize Code**: Follow all current patterns (TektonEnviron, no hardcoding)
3. **Real UI Data**: Remove all mocks, connect to actual backend
4. **MCP Integration**: Use aish MCP for AI communication

## Phase 1: Assessment & Cleanup [0% Complete]

### Tasks
- [ ] Run component and document current state
- [ ] List all mock data locations
- [ ] Find all hardcoded ports/URLs
- [ ] Identify os.environ usage
- [ ] Find unused imports/variables/functions
- [ ] Check test coverage
- [ ] Document UI issues
- [ ] Count onclick handlers (7 found in initial scan)

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
- [ ] Update to use aish MCP for AI calls
- [ ] Remove direct HTTP AI calls
- [ ] Update API documentation
- [ ] Verify all endpoints work
- [ ] Ensure real service registry data
- [ ] Ensure real message monitoring

### Success Criteria
- [ ] All endpoints return real data
- [ ] AI communication through MCP
- [ ] API documentation current
- [ ] Service registry shows actual Tekton services
- [ ] Message monitor shows real inter-component messages

### Blocked On
- [ ] Phase 2 completion
- [ ] aish MCP server availability

## Phase 4: Frontend Updates - CSS-First Conversion [0% Complete]

### Tasks
- [ ] Convert all 6 tabs to CSS-first radio buttons
- [ ] Remove onclick from registry tab (line 27)
- [ ] Remove onclick from messaging tab (line 36)
- [ ] Remove onclick from connections tab (line 45)
- [ ] Remove onclick from history tab (line 54)
- [ ] Remove onclick from chat tab (line 63)
- [ ] Remove onclick from teamchat tab (line 72)
- [ ] Remove onclick from clear button (line 80)
- [ ] Remove onclick from chat input (line 402)
- [ ] Remove onclick from send button (line 403)
- [ ] Convert tab switching to pure CSS with :checked pseudo-class
- [ ] Remove all JavaScript tab switching code
- [ ] Remove all mock data
- [ ] Connect to real backend endpoints
- [ ] Add proper loading states
- [ ] Add proper error handling
- [ ] Test all UI functionality
- [ ] Fix any broken features
- [ ] Update UI to use aish MCP

### Success Criteria
- [ ] No onclick handlers remain
- [ ] Tab switching works with pure CSS
- [ ] UI shows only real data
- [ ] All features work
- [ ] Good error handling

### Blocked On
- [ ] Phase 3 completion

## Phase 5: Testing & Documentation [0% Complete]

### Tasks
- [ ] Write missing unit tests
- [ ] Write integration tests
- [ ] Organize tests in tests/hermes/
- [ ] Update component README
- [ ] Update API documentation
- [ ] Document configuration
- [ ] Run full test suite
- [ ] Document CSS-first pattern for future reference

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
- Database adapter modifications

## Files to Update
```
/Hephaestus/ui/components/hermes/hermes-component.html
/Hephaestus/ui/scripts/hermes/hermes-component.js
/Hephaestus/ui/scripts/hermes-service.js (if exists)
/Hermes/hermes/api/app.py (backend)
/Hermes/hermes/api/endpoints.py (API endpoints)
```

## Known Issues from Initial Assessment
- JavaScript onclick handlers on all 6 tabs
- onclick handlers on clear button and chat interface
- Complex tab switching functions (hermes_switchTab)
- HTML panel protection code that may interfere
- Mock data placeholders in registry and messaging views
- Need to verify service registry API is working
- Need to verify message bus integration is active

## CSS-First Implementation Pattern
Following the pattern established in Apollo and Athena renovations:
1. Use hidden radio inputs for tab state
2. Use labels as tab triggers
3. Use CSS :checked pseudo-class for active states
4. Keep all interactivity in CSS, no JavaScript for basic UI
5. Maintain semantic HTML structure
6. Ensure accessibility with proper ARIA attributes