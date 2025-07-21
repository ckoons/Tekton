# Sprint: Apollo Renovation

## Overview
Bring Apollo up to current Tekton standards, remove technical debt, ensure real data in UI, and integrate with aish MCP for all AI communication.

## Goals
1. **Standardize Code**: Follow all current patterns (TektonEnviron, no hardcoding)
2. **Real UI Data**: Remove all mocks, connect to actual backend
3. **MCP Integration**: Use aish MCP for AI communication

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
- [ ] Update to use aish MCP for AI calls
- [ ] Remove direct HTTP AI calls
- [ ] Update API documentation
- [ ] Verify all endpoints work

### Success Criteria
- [ ] All endpoints return real data
- [ ] AI communication through MCP
- [ ] API documentation current

### Blocked On
- [ ] Phase 2 completion
- [ ] aish MCP server availability

## Phase 4: Frontend Updates [0% Complete]

### Tasks
- [ ] Remove all mock data
- [ ] Connect to real backend endpoints
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
- [ ] Organize tests in tests/apollo/
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
Will be documented during Phase 1
```