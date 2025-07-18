# Handoff Document: [Sprint Name]

## Current Status
**Phase**: [Current Phase Name]  
**Progress**: [X]% Complete  
**Last Updated**: [DateTime]

## What Was Just Completed
- Finished implementing X
- Fixed bug in Y
- Updated tests for Z

## What Needs To Be Done Next
1. **IMMEDIATE**: Continue function `foo()` in `/path/to/file.py` line 234
2. **NEXT**: Implement error handling for edge case discovered
3. **THEN**: Run integration tests with main branch

## Current Blockers
- [ ] Waiting for Casey approval on design decision
- [ ] Need clarification on requirement X

## Important Context
- Decision made to use approach A because of B
- File X depends on Y being completed first
- Watch out for edge case in component Z

## Test Status
- Unit tests: 15/20 passing (see failing tests below)
- Integration tests: Not started yet
- Failing tests:
  - `test_feature_x` - needs mock data update
  - `test_integration_y` - waiting for API change

## Files Being Modified
```
/path/to/active/file1.py - Line 234, implementing new method
/path/to/active/file2.js - Needs UI update for new API
/path/to/active/file3.md - Documentation half updated
```

## Commands to Run on Startup
```bash
# Get to the right state
cd $TEKTON_ROOT
git status  # Should show the files listed above

# Run tests to see current state
pytest tests/current_test.py -v

# If needed, restart services
tekton restart component_name
```

## Questions Needing Answers
1. Should we implement caching for X?
2. Is the 5-second timeout acceptable for Y?
3. Do we need backwards compatibility for Z?

## Do NOT Touch
- `/path/to/stable/file` - Working correctly, no changes needed
- Database migrations - Casey will handle separately

## Notes for Next Session
- Remember to update DAILY_LOG.md first
- Check if Casey responded to questions in Slack/Email
- New requirement might be coming for feature X