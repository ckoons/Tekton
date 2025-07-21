# Component Renovation Checklist: Apollo

## Pre-Start Verification
- [ ] Component location: `$TEKTON_ROOT/Apollo`
- [ ] Component builds successfully
- [ ] Existing tests pass (or document failures)
- [ ] UI loads (even if with mocks)
- [ ] Document current issues:
  ```
  List issues found
  ```

## Code Standards [0% Complete]

### Configuration
- [ ] No hardcoded ports - use TektonEnviron
  - [ ] Found in: [list files]
- [ ] No hardcoded URLs - use tekton_url() 
  - [ ] Found in: [list files]
- [ ] No os.environ direct access - use TektonEnviron
  - [ ] Found in: [list files]
- [ ] Observe $TEKTON_ROOT boundary
- [ ] No '~' usage except in Terma terminal templates

### Code Quality
- [ ] Remove unused imports
  - [ ] Found in: [list files]
- [ ] Remove unused variables
  - [ ] Found in: [list files]
- [ ] Remove unused functions
  - [ ] Found in: [list files]
- [ ] Remove commented-out code
- [ ] Fix all linting warnings

## Backend Updates [0% Complete]

### API Compliance
- [ ] All endpoints return proper status codes
- [ ] Error responses follow standard format:
  ```json
  {"error": "message", "details": {...}}
  ```
- [ ] API documentation is current
- [ ] Remove mock endpoints:
  - [ ] Found: [list endpoints]

### MCP Integration
- [ ] Update to use aish MCP for AI communication
  - [ ] Current HTTP calls: [list locations]
- [ ] Remove direct HTTP AI calls
- [ ] Update MCP capability descriptions
- [ ] Test all MCP tools work

## Frontend Updates [0% Complete]

### Remove Mocks
- [ ] Identify all mock data:
  - [ ] File: [location] - [description]
  - [ ] File: [location] - [description]
- [ ] Connect to real backend endpoints
- [ ] Handle loading states properly
- [ ] Handle error states properly

### UI Functionality
- [ ] All buttons work
- [ ] All displays show real data
- [ ] Forms submit correctly
- [ ] Navigation works
- [ ] Keyboard shortcuts work
- [ ] Accessibility features work

## Testing [0% Complete]

### Test Structure
- [ ] Tests organized in `tests/apollo/`
- [ ] Test files follow naming: `test_*.py` or `*.test.js`
- [ ] All test imports work
- [ ] Create `tests/apollo/__init__.py`

### Test Coverage
- [ ] List missing unit tests:
  - [ ] [Feature] needs test
  - [ ] [Feature] needs test
- [ ] Write missing unit tests
- [ ] Write integration tests
- [ ] All tests pass
- [ ] Document any flaky tests

### Test Execution
```bash
# Backend tests
cd $TEKTON_ROOT
pytest tests/apollo/ -v

# Frontend tests (if applicable)
cd $TEKTON_ROOT/apollo
npm test
```

## Documentation [0% Complete]

### Code Documentation
- [ ] All functions have docstrings
- [ ] Complex logic is commented
- [ ] API endpoints documented
- [ ] Configuration documented

### User Documentation
- [ ] Update `apollo/README.md`
- [ ] Update API documentation
- [ ] Update configuration guide
- [ ] Add troubleshooting section

### Example Configuration
```python
# Document required configuration
APOLLO_CONFIG = {
    'port': TektonEnviron.get('APOLLO_PORT', '8112'),
    'api_base': tekton_url('apollo', '')
}
```

## Integration Testing [0% Complete]

### With Main Branch
- [ ] Merge main into feature branch
- [ ] Resolve any conflicts
- [ ] All tests still pass
- [ ] Component works with other components

### End-to-End Testing
- [ ] Test primary use case: [describe]
- [ ] Test error conditions
- [ ] Test with forwarding enabled
- [ ] Test performance is acceptable

### Integration Test Commands
```bash
# Start full Tekton system
tekton start all

# Test specific integration
[commands to test integration]
```

## Final Verification [0% Complete]

### Code Review Prep
- [ ] All checklist items complete
- [ ] Code follows patterns
- [ ] No temporary/debug code
- [ ] Commits are clean and logical

### Ready to Merge
- [ ] Casey approved approach
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] PR description complete

## Component-Specific Items

### Apollo Special Requirements
- [ ] Convert onclick handlers to CSS-first radio button pattern
- [ ] Ensure predictive engine and token budget work correctly
- [ ] Test attention monitoring and protocol enforcement UI

## Issues Found
```
Document any issues discovered during renovation
```

## Decisions Made
```
Document any technical decisions and reasoning
```

## Files Modified
```
# Configuration changes
[file path] - [what changed]

# Backend changes
[file path] - [what changed]

# Frontend changes
[file path] - [what changed]

# Test changes
[file path] - [what changed]

# Documentation changes
[file path] - [what changed]
```