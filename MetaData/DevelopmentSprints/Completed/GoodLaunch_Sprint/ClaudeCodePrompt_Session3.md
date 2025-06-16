# GoodLaunch Sprint - Claude Code Prompt Session 3

## Context

You are Claude (Working), the implementation agent for the GoodLaunch Development Sprint. This sprint focuses on achieving reliable component launch and lifecycle management across the Tekton ecosystem.

## Current State

Based on Session 2's work, we have made progress but introduced some new issues that need immediate attention.

### ✅ Working Components
- **Hermes** - Fully operational (lifecycle manager)
- **Engram** - Fully operational (memory system)
- **Apollo** - Fully operational (attention system)
- **Metis** - Now working! (task management)
- **Hephaestus UI** - Fully operational

### ❌ Failing Components
- **Rhetor** - ToolSchema validation error (our schema→input_schema change broke it)
- **Synthesis** - ToolSchema validation error (same issue as Rhetor)
- **Budget** - Logger not defined error
- **Sophia** - Syntax error from asyncio fix
- **Prometheus** - mcp_tool() unexpected 'capability' argument
- **Athena** - PromptTemplateRegistry missing method
- **Ergon** - Timeout (needs investigation)
- **Harmonia** - Timeout (needs investigation)
- **Telos** - No log file created (script-level failure)

## Session 2 Summary

### What We Fixed
1. Added `TimelineEvent` class to Prometheus
2. Added `get_budget_engine` function to Budget
3. Added `ResourceAllocation` class to Prometheus
4. Fixed capability registration (classes→instances) in multiple components
5. Fixed TektonLLMClient initialization in Athena
6. Fixed log_function decorator in Budget (removed 'operation' parameter)
7. Attempted to fix asyncio.coroutine deprecation

### What We Broke
1. **ToolSchema change** - Renaming schema→input_schema broke tool registration
2. **Syntax error** - Asyncio fix introduced bracket mismatch
3. **Logger issues** - Budget has undefined logger

## CRITICAL FIRST TASK

**REVERT THE SCHEMA CHANGE**: The shadow warning was just a warning, but our fix broke the API.

1. In `/tekton-core/tekton/mcp/fastmcp/schema.py`:
   - Change `input_schema` back to `schema` on line 104
   - Remove the Field(alias="schema") part

2. In `/tekton-core/tekton/mcp/fastmcp/server.py`:
   - Change `input_schema` back to `schema` in the tool_data dictionary

3. DO NOT modify the tool files - they should already be using `schema`

## Immediate Fixes Needed

### 1. Budget Logger (Simple Fix)
In `/Budget/budget/api/mcp_endpoints.py` around line 10-15, add:
```python
import logging
logger = logging.getLogger(__name__)
```

### 2. Sophia Syntax Error (Simple Fix)
In `/tekton-core/tekton/utils/tekton_websocket.py` line 733:
- Current: `handler: Callable[[WebSocket, Dict[str, Any]], Any]`
- There's an extra bracket somewhere, fix the syntax

### 3. Prometheus mcp_tool (Investigation Needed)
Error: `mcp_tool() got an unexpected keyword argument 'capability'`
- Find where mcp_tool is being called with a 'capability' argument
- Remove that argument

### 4. Athena PromptTemplateRegistry (Investigation Needed)
Error: `'PromptTemplateRegistry' object has no attribute 'register_template'`
- Check what methods PromptTemplateRegistry actually has
- Fix the usage in Athena's llm_integration.py

## Understanding Hermes Behavior

Note: Hermes launching Rhetor when it's not available is EXPECTED behavior. Hermes is the lifecycle manager and tries to ensure critical services are running. This is not an error.

## Next Phase Preview

Once we get more components working, we'll move to Phase 2: Component Registration and Communication
- Ensure all components register with Hermes
- Implement health check endpoints
- Standardize service discovery

## Sprint Structure Reference

- **Phase 1**: Fix All Import/Startup Issues (Current Phase)
- **Phase 2**: Component Registration and Communication
- **Phase 3**: Python Launch System
- **Phase 4**: Parallel Launch Optimization
- **Phase 5**: UI Integration

## Key Design Principles (from Casey)

1. **Keep it simple** - Avoid massive code blocks
2. **Write once, reuse often** - Look for shared patterns
3. **Be methodical** - Test each fix before moving on
4. **Communicate** - Discuss approaches before implementing

## Technical Context

- Tekton uses Python 3.12 (asyncio.coroutine is deprecated)
- Mix of Pydantic v1 and v2 patterns causing issues
- Single Port Architecture with designated ports (8000-8014)
- MCP (Model Context Protocol) for component communication

## Latest Launch Log

```
tekton-launch --launch-all
INFO: ====== Tekton Orchestration System ======
INFO: Tekton installation: /Users/cskoons/projects/github/Tekton

SUCCESS: Ensured data directories exist in /Users/cskoons/.tekton
INFO: Hermes will be launched - cleaning up existing environment...
INFO: Ensuring a clean environment before launch...
SUCCESS: All Tekton ports are available

SUCCESS: Launch-all option specified. All available components will be launched.
INFO: Components to launch:
SUCCESS: • hermes
SUCCESS: • synthesis
SUCCESS: • hephaestus
SUCCESS: • engram
SUCCESS: • ergon
SUCCESS: • rhetor
SUCCESS: • telos
SUCCESS: • prometheus
SUCCESS: • harmonia
SUCCESS: • athena
SUCCESS: • sophia
SUCCESS: • metis
SUCCESS: • apollo
SUCCESS: • budget

INFO: Launching Hermes first as lifecycle manager...
INFO: Launching Hermes Database & Messaging as Lifecycle Manager...
INFO: Checking if Hermes port 8001 is available...
INFO: Starting hermes on port 8001...
hermes server started with PID: 58254
INFO: Waiting for Hermes service to be ready...
INFO: Waiting for Hermes Service to respond (timeout: 30s)...
.SUCCESS: Hermes Service is now responding
INFO: Waiting for Hermes to fully initialize...
INFO: LLM Adapter not detected - starting it automatically
INFO: Launching LLM Management System...
INFO: Rhetor is available but not running. Launching Rhetor instead of LLM Adapter...
INFO: Launching Rhetor LLM Management System...
INFO: Checking if port 8003 is available...
INFO: Starting rhetor on port 8003...
WARNING: Error checking for start_server: error: 1 validation error for ToolSchema
schema
  Field required [type=missing, input_value={'name': 'get_available_m...e': {'type': 'object'}}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
rhetor server started with PID: 58284
INFO: Waiting for Rhetor LLM Management System to be ready...
INFO: Waiting for Rhetor LLM Management System to respond (timeout: 20s)...
...................
WARNING: Timeout waiting for Rhetor LLM Management System to respond
ERROR: Rhetor LLM Management System failed to start - check logs at /Users/cskoons/.tekton/logs/rhetor.log
INFO: Launching Engram Memory System...
INFO: Checking if Engram port 8000 is available...
SUCCESS: Found Engram startup script at: /Users/cskoons/projects/github/Tekton/Engram/core/engram_consolidated
INFO: Setting ENGRAM_USE_FALLBACK=1 to use file-based storage
SUCCESS: Started Engram memory service with PID: 58371
INFO: Waiting for Engram service to be ready...
INFO: Waiting for Engram Memory Service to respond (timeout: 60s)...
.SUCCESS: Engram Memory Service is now responding
SUCCESS: Engram memory service is online!
INFO: Launching Ergon Agent System...
INFO: Checking if port 8002 is available...
INFO: Starting ergon on port 8002...
[Ergon startup logs...]
ergon server started with PID: 58396
INFO: Waiting for Ergon Agent System to be ready...
INFO: Waiting for Ergon Agent System to respond (timeout: 20s)...
....................
WARNING: Timeout waiting for Ergon Agent System to respond
ERROR: Ergon Agent System failed to start - check logs at /Users/cskoons/.tekton/logs/ergon.log
INFO: Launching Rhetor LLM Management System...
INFO: Checking if port 8003 is available...
INFO: Starting rhetor on port 8003...
WARNING: Error checking for start_server: error: 1 validation error for ToolSchema
schema
  Field required [type=missing, input_value={'name': 'get_available_m...e': {'type': 'object'}}}, input_type=dict]
rhetor server started with PID: 58492
[Similar failures for other components...]
INFO: Launching Metis Task Management...
INFO: Checking if port 8011 is available...
INFO: Starting metis on port 8011...
metis server started with PID: 59137
INFO: Waiting for Metis Task Management to be ready...
INFO: Waiting for Metis Task Management to respond (timeout: 20s)...
SUCCESS: Metis Task Management is now responding
SUCCESS: Metis Task Management initialized
INFO: Launching Apollo Attention System...
INFO: Checking if port 8012 is available...
INFO: Starting apollo on port 8012...
[Apollo startup logs...]
apollo server started with PID: 59156
INFO: Waiting for Apollo Attention System to be ready...
INFO: Waiting for Apollo Attention System to respond (timeout: 20s)...
SUCCESS: Apollo Attention System is now responding
SUCCESS: Apollo Attention System initialized
INFO: Launching Budget Token/Cost Management...
INFO: Checking if port 8013 is available...
INFO: Starting budget on port 8013...
WARNING: Error checking for start_server: error: name 'logger' is not defined
budget server started with PID: 59171
INFO: Waiting for Budget Token/Cost Management to be ready...
INFO: Waiting for Budget Token/Cost Management to respond (timeout: 20s)...
...................
WARNING: Timeout waiting for Budget Token/Cost Management to respond
ERROR: Budget Token/Cost Management failed to start - check logs at /Users/cskoons/.tekton/logs/budget.log
INFO: Launching Hephaestus UI...
INFO: Checking if Hephaestus ports are available...
SUCCESS: Ports are available. Proceeding with launch.
INFO: Using run_ui.sh script...
SUCCESS: Hephaestus UI started successfully
SUCCESS: Access the UI at: http://localhost:8080
```

## Success Metrics for Session 3

By the end of this session:
- [ ] ToolSchema reverted - Rhetor and Synthesis working
- [ ] Budget logger fixed - Budget starting
- [ ] Sophia syntax fixed - Sophia starting
- [ ] At least 7-8 components fully operational
- [ ] Clear understanding of remaining timeout issues

## Remember

- Casey prefers simple, targeted fixes over large refactors
- Test each fix individually before moving to the next
- The goal is reliable component startup, not perfection
- Hermes launching missing components is expected behavior

## IMPORTANT: Working Methodology

You MUST:
1. **Work methodically with Casey** - Do not rush ahead with fixes
2. **Create a TODO list** using the TodoWrite tool at the start of the session
3. **Discuss all planned changes** with Casey before implementing
4. **Get Casey's approval** before making any code changes
5. **Update the TODO list** as you complete tasks

This collaborative approach ensures:
- Changes align with Tekton's design principles
- No unnecessary or conflicting modifications
- Casey can provide context and guidance
- Better solutions through discussion

Good luck with Session 3!