# Handoff Document: MCP & Distributed Tekton

## Current Status
**Phase**: Not Started  
**Progress**: 0% Complete  
**Last Updated**: 2025-01-18

## What Was Just Completed
- Sprint planning created
- Directory structure set up
- Ready to begin implementation

## What Needs To Be Done Next
1. **IMMEDIATE**: Start Phase 1 - Create aish MCP server
2. **FIRST**: Set up `/shared/aish/src/mcp/server.py`
3. **THEN**: Implement first endpoint `/mcp/capabilities`

## Current Blockers
- [ ] Need Casey to confirm approach
- [ ] Need to decide on MCP server port

## Important Context
- This sprint fundamentally changes how Tekton components communicate
- All UI components will need updates after MCP server is ready
- Forwarding must work exactly as it does now
- This enables future distributed Tekton systems

## Test Status
- No tests yet - need to create MCP test suite

## Files Being Modified
```
None yet - starting fresh
```

## Commands to Run on Startup
```bash
# Get to the right directory
cd $TEKTON_ROOT/shared/aish

# Check current aish functionality
aish numa "test message"
aish forward list

# These should work identically after MCP migration
```

## Questions Needing Answers
1. What port should aish MCP server use?
2. Should MCP server run as separate process or part of aish?
3. Do we need authentication for local MCP access?

## Do NOT Touch
- Current aish functionality must remain unchanged
- MessageHandler forwarding logic is working correctly

## Notes for Next Session
- Read MCP specification docs first
- Check how other tools implement MCP servers
- Consider using existing MCP libraries if available