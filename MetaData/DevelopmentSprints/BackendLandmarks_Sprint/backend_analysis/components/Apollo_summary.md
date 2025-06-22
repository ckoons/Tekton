# Apollo Analysis Summary

**Generated**: 2025-06-21T17:26:05.729645

## Statistics
- Files analyzed: 47
- Functions: 367
- Classes: 92
- Landmarks identified: 384
- API endpoints: 34
- MCP tools: 24

## Patterns Found
- fastapi
- singleton
- async
- error_handling
- mcp
- websocket

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Apollo/setup.py
- read (line 11): Has side effects

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/message_handler.py
- get_hermes_url (line 38): Public function
- MessageFilter (line 45): Class definition
- MessageFilter.matches (line 113): High complexity
- HermesClient (line 203): Class definition
- HermesClient.send_message (line 218): Async function

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/predictive_engine.py
- linear_regression (line 32): Public function
- PredictionRule (line 86): Class definition
- PredictionRule.predict (line 102): Async function
- TokenUtilizationRule (line 124): Class definition
- TokenUtilizationRule.predict (line 135): Async function

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/token_budget.py
- TokenBudgetManager (line 33): Class definition
- TokenBudgetManager.start (line 186): Async function
- TokenBudgetManager.stop (line 199): Async function
- TokenBudgetManager.allocate_budget (line 638): Async function
- TokenBudgetManager.record_usage (line 714): High complexity

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/context_observer.py
- ContextObserver (line 31): Class definition
- ContextObserver.start (line 90): Async function
- ContextObserver.stop (line 103): Async function
- ContextObserver.register_callback (line 372): Public function
- ContextObserver.get_context_state (line 387): Public function

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/action_planner.py
- ActionType (line 33): Class definition
- ActionPriority (line 45): Class definition
- ActionRule (line 53): Class definition
- ActionRule.evaluate (line 67): Async function
- TokenUtilizationActionRule (line 87): Class definition

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/apollo_component.py
- ApolloComponent (line 20): Class definition
- ApolloComponent.get_capabilities (line 162): Public function
- ApolloComponent.get_metadata (line 172): Public function

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/apollo_manager.py
- ApolloManager (line 66): Class definition
- ApolloManager.start (line 190): Async function, High complexity
- DummyToolRegistry (line 226): Class definition
- DummyToolRegistry.register_tool (line 227): Async function
- stop (line 258): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/protocol_enforcer.py
- ProtocolValidator (line 38): Class definition
- ProtocolValidator.validate (line 50): Async function
- MessageFormatValidator (line 68): Class definition
- MessageFormatValidator.validate (line 71): Async function, High complexity
- RequestFlowValidator (line 142): Class definition

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/models/budget.py
- BudgetTier (line 15): Class definition
- BudgetPeriod (line 22): Class definition
- BudgetPolicyType (line 32): Class definition
- TaskPriority (line 40): Class definition
- BudgetPolicy (line 48): Class definition

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/models/protocol.py
- ProtocolType (line 15): Class definition
- ProtocolSeverity (line 27): Class definition
- ProtocolScope (line 35): Class definition
- EnforcementMode (line 43): Class definition
- ProtocolDefinition (line 51): Class definition

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/models/message.py
- MessageType (line 16): Class definition
- MessagePriority (line 60): Class definition
- TektonMessage (line 68): Class definition
- ContextMessage (line 87): Class definition
- ActionMessage (line 96): Class definition

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/models/context.py
- ContextHealth (line 15): Class definition
- ContextMetrics (line 24): Class definition
- ContextState (line 49): Class definition
- ContextHistoryRecord (line 64): Class definition
- ContextPrediction (line 73): Class definition

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/cli/main.py
- get_apollo_port (line 29): Public function
- ApolloClient (line 44): Class definition
- ApolloClient.close (line 60): Async function
- ApolloClient.get_health (line 64): Async function
- ApolloClient.get_contexts (line 75): Async function

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/api/models.py
- ResponseStatus (line 14): Class definition
- APIResponse (line 21): Class definition
- MonitoringStatus (line 29): Class definition
- MonitoringMetrics (line 36): Class definition
- SessionInfo (line 47): Class definition

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/api/app.py
- startup_callback (line 65): Async function
- root (line 111): Async function
- health_check (line 124): Async function
- ready (line 134): Async function
- discovery (line 146): Async function, Has side effects

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/api/dependencies.py
- DebugLog (line 13): Class definition
- DebugLog.dummy_log (line 15): Public function
- log_function (line 20): Public function
- decorator (line 21): Public function
- get_apollo_manager (line 27): Public function

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/api/routes.py
- get_all_contexts (line 71): Async function
- get_context (line 117): Async function
- get_context_dashboard (line 174): Async function
- get_all_predictions (line 213): Async function
- get_prediction (line 258): Async function

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/mcp/hermes_bridge.py
- ApolloMCPBridge (line 16): Class definition
- ApolloMCPBridge.initialize (line 31): Async function
- ApolloMCPBridge.register_default_tools (line 56): Async function
- ApolloMCPBridge.register_fastmcp_tools (line 71): Async function
- ApolloMCPBridge.register_fastmcp_tool (line 84): Async function

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/mcp/tools.py
- mcp_tool (line 22): Public function
- decorator (line 23): Public function
- mcp_capability (line 27): Public function
- decorator (line 28): Public function
- plan_actions (line 49): Async function, MCP tool

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/mcp/__init__.py
- get_tools (line 43): Public function
- mcp_tool (line 63): Public function
- decorator (line 64): Public function
- mcp_capability (line 68): Public function
- decorator (line 69): Public function

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/mcp/capabilities.py
- ActionPlanningCapability (line 12): Class definition
- ActionPlanningCapability.get_supported_operations (line 20): Public function
- ActionPlanningCapability.get_capability_metadata (line 30): Public function
- ActionExecutionCapability (line 46): Class definition
- ActionExecutionCapability.get_supported_operations (line 54): Public function

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/core/interfaces/rhetor.py
- get_component_port (line 24): Public function
- get_component_url (line 28): Public function
- RhetorInterface (line 38): Class definition
- RhetorInterface.get_active_sessions (line 131): Async function
- RhetorInterface.get_session_metrics (line 164): Async function

### /Users/cskoons/projects/github/Tekton/Apollo/apollo/api/endpoints/mcp.py
- ApolloMCPRequest (line 56): Class definition
- ApolloMCPResponse (line 61): Class definition
- process_message (line 69): Async function
- process_fastmcp_request (line 97): Async function
- get_capabilities (line 128): Async function
