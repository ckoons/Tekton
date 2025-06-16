# GoodLaunch Sprint - Claude Code Prompt Session 4

## Context

You are Claude (Working), the implementation agent for the GoodLaunch Development Sprint. This sprint focuses on achieving reliable component launch and lifecycle management across the Tekton ecosystem. This is Session 4, building on the significant progress from previous sessions.

## Current State

Session 3 brought us to 9/14 components working (64% success rate). We're close to achieving full system startup!

### ✅ Working Components (9/14)
- Hermes - Lifecycle manager
- Engram - Memory system
- Synthesis - Execution engine
- Metis - Task management
- Apollo - Attention system
- Hephaestus UI - Web interface
- Athena - Knowledge graph
- Rhetor - LLM management (running with warnings)
- Harmonia - Workflow system (running but not responding to HTTP)

### ❌ Remaining Failures (5/14)
1. **Sophia** - Syntax error at line 552 in tekton_websocket.py
2. **Prometheus** - `'function' object has no attribute 'name'` error
3. **Budget** - Timeout (despite logger fix from Session 3)
4. **Ergon** - Timeout
5. **Telos** - Script failure (no log file created)

## Primary Objectives

Get the remaining 5 components working to achieve 100% startup success.

## Specific Issues to Fix

### 1. Sophia Syntax Error (High Priority)
**Error**: `closing parenthesis ')' does not match opening parenthesis '[' on line 551 (tekton_websocket.py, line 552)`
**Action**: Check line 552 and surrounding lines for mismatched brackets

### 2. Prometheus Function Attribute Error (High Priority)
**Error**: `'function' object has no attribute 'name'`
**Context**: Occurs during capability registration
**Action**: Find where a function is being passed instead of a capability instance

### 3. Budget Timeout (Medium Priority)
**Symptom**: Component starts but times out during initialization
**Previous Fix**: Logger was added in Session 3
**Action**: Investigate startup sequence, check for blocking operations

### 4. Ergon Timeout (Medium Priority)
**Symptom**: Consistent timeout after 20 seconds
**Action**: Check initialization sequence, look for blocking calls

### 5. Telos Script Failure (Low Priority)
**Symptom**: Won't even start, no log file created
**Action**: Check the launch script itself

## Investigation Needed

### HTTP Response Issues
- Why are Rhetor and Harmonia running but not responding to HTTP?
- Missing health check endpoints?
- Wrong response format?

### Timeout Pattern
- What's common between Ergon and Budget that causes timeouts?
- Are they waiting for unavailable services?
- Blocking operations during startup?

## Latest Launch Output

```
Working Components Summary:
✓ Engram Memory System - port 8000
✓ Hermes Messaging System - port 8001
✓ Rhetor LLM Manager - port 8003 (not responding to HTTP)
✓ Athena Knowledge Graph - port 8005
✓ Harmonia Workflow System - port 8007 (not responding to HTTP)
✓ Synthesis Execution Engine - port 8009
✓ Metis Task Management - port 8011
✓ Apollo Attention System - port 8012
✓ Hephaestus UI - port 8080

Failed Components:
✗ Ergon - port 8002 (timeout)
✗ Prometheus - port 8006 (function attribute error)
✗ Telos - port 8008 (script failure)
✗ Budget - port 8013 (timeout)
✗ Sophia - port 8014 (syntax error)
```

## Working Methodology

1. **Start with Quick Fixes**: Sophia syntax error and Prometheus attribute error
2. **Then Investigate Timeouts**: Budget and Ergon
3. **Finally Script Issues**: Telos startup script
4. **Test Incrementally**: Run `tekton-launch` after each fix
5. **Document Findings**: Note any patterns for future improvements

## Success Criteria

- All 14 components starting successfully
- No Python syntax or import errors
- Components responding to health checks where implemented
- Clear documentation of any remaining non-critical issues

## Important Context

- Pydantic field shadowing warnings are expected (will be fixed in future sprint)
- Focus on startup success, not warning elimination
- Some components may not have health checks implemented yet
- Timeouts might indicate missing dependencies or services

## Tips from Previous Sessions

- Check log files in `~/.tekton/logs/` for detailed error messages
- Components timing out might be waiting for other services
- Syntax errors often have additional instances nearby
- Function vs instance errors usually happen in registration code

Good luck achieving 100% component startup!