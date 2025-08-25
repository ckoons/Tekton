# Component Renovation Checklist: [COMPONENT_NAME]

## Pre-Start Verification
- [ ] Component builds successfully
- [ ] Existing tests pass (or document which fail)
- [ ] UI loads (even if with mocks)

## Code Standards [0% Complete]

### Configuration
- [ ] No hardcoded ports - use TektonEnviron
- [ ] No hardcoded URLs - use tekton_url() 
- [ ] No os.environ direct access - use TektonEnviron
- [ ] Observe $TEKTON_ROOT boundary
- [ ] No '~' usage except in Terma terminal templates

### Code Quality
- [ ] Remove unused imports
- [ ] Remove unused variables
- [ ] Remove unused functions
- [ ] Remove commented-out code
- [ ] Fix all linting warnings

## Backend Updates [0% Complete]

### API Compliance
- [ ] All endpoints return proper status codes
- [ ] Error responses follow standard format
- [ ] API documentation is current
- [ ] Remove mock endpoints

### MCP Integration
- [ ] Update to use aish MCP for CI communication
- [ ] Remove direct HTTP CI calls
- [ ] Update MCP capability descriptions
- [ ] Test all MCP tools work

## Frontend Updates [0% Complete]

### Remove Mocks
- [ ] Identify all mock data
- [ ] Connect to real backend endpoints
- [ ] Handle loading states properly
- [ ] Handle error states properly

### UI Functionality
- [ ] All buttons work
- [ ] All displays show real data
- [ ] Forms submit correctly
- [ ] Navigation works

## Testing [0% Complete]

### Test Structure
- [ ] Tests organized in `tests/[component]/`
- [ ] Test files follow naming convention
- [ ] All test imports work

### Test Coverage
- [ ] Write missing unit tests
- [ ] Write integration tests
- [ ] All tests pass
- [ ] Document any flaky tests

### Test Execution
```bash
# Commands to run tests
cd $TEKTON_ROOT
pytest tests/[component]/ -v
```

## Documentation [0% Complete]

### Code Documentation
- [ ] All functions have docstrings
- [ ] Complex logic is commented
- [ ] API endpoints documented
- [ ] Configuration documented

### User Documentation
- [ ] Update component README
- [ ] Update API documentation
- [ ] Update configuration guide
- [ ] Add troubleshooting section

## Integration Testing [0% Complete]

### With Main Branch
- [ ] Merge main into feature branch
- [ ] Resolve any conflicts
- [ ] All tests still pass
- [ ] Component works with other components

### End-to-End Testing
- [ ] Test primary use case
- [ ] Test error conditions
- [ ] Test with forwarding enabled
- [ ] Test performance is acceptable

## Final Verification [0% Complete]

### Code Review Prep
- [ ] All checklist items complete
- [ ] Code follows patterns
- [ ] No temporary/debug code
- [ ] Commits are clean

### Ready to Merge
- [ ] Casey approved approach
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No merge conflicts

## Component-Specific Items

### [Add component-specific checks here]
- [ ] Special requirement 1
- [ ] Special requirement 2

## Notes
[Document any special considerations, gotchas, or decisions made]

## Files Modified
```
List all files changed during renovation
```