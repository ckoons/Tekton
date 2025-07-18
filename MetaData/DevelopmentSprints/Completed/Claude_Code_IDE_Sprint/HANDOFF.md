# Handoff Document: Claude Code IDE Sprint

## Current Status
**Phase**: Not Started  
**Progress**: 0% Complete  
**Last Updated**: 2025-01-18

## What Was Just Completed
- Created sprint structure
- Designed Claude-friendly interface patterns
- Defined introspection approach

## What Needs To Be Done Next
1. **IMMEDIATE**: Create basic introspection engine
2. **FIRST**: Implement `aish introspect` command
3. **THEN**: Add context and explain commands

## Current Blockers
- None yet

## Important Context
- Claude Code currently guesses method names
- Causes AttributeErrors and breaks flow
- Need text-based interface Claude can query
- Must be fast enough for interactive use

## Key Design Decisions
- Use Python's inspect module
- Text output that Claude can read
- Query-based, not push-based
- Cache for performance

## Commands to Run on Startup
```bash
# Navigate to aish
cd $TEKTON_ROOT/shared/aish

# Check current command structure
ls src/commands/

# Find classes that need introspection
grep -r "class.*:" --include="*.py" | head -20
```

## Questions Needing Answers
1. Should introspection be live or cached?
2. Include private methods or just public?
3. How deep into inheritance chains?

## Do NOT Touch
- Existing command functionality
- Current aish interface

## Notes for Next Session
- Start with simple class introspection
- Test with AIShell and MessageHandler first
- Make it work, then make it fast