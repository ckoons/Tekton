# Budget Analysis Summary

**Generated**: 2025-06-21T17:26:06.275071

## Statistics
- Files analyzed: 45
- Functions: 454
- Classes: 123
- Landmarks identified: 477
- API endpoints: 37
- MCP tools: 14

## Patterns Found
- fastapi
- singleton
- async
- error_handling
- mcp
- websocket

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Budget/examples/websocket_client.py
- create_message (line 23): Public function
- handle_budget_updates (line 44): Async function, Has side effects, High complexity
- send_heartbeats (line 164): Async function, Has side effects
- main (line 188): Async function

### /Users/cskoons/projects/github/Tekton/Budget/budget/core/constants.py
- DebugLog (line 15): Class definition
- DebugLog.dummy_log (line 17): Public function
- log_function (line 22): Public function
- decorator (line 23): Public function

### /Users/cskoons/projects/github/Tekton/Budget/budget/core/policy.py
- DebugLog (line 17): Class definition
- DebugLog.dummy_log (line 19): Public function
- log_function (line 24): Public function
- decorator (line 25): Public function
- PolicyEnforcer (line 48): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/core/engine.py
- DebugLog (line 18): Class definition
- DebugLog.dummy_log (line 20): Public function
- log_function (line 25): Public function
- decorator (line 26): Public function
- BudgetEngine (line 50): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/core/allocation.py
- DebugLog (line 19): Class definition
- DebugLog.dummy_log (line 21): Public function
- log_function (line 26): Public function
- decorator (line 27): Public function
- AllocationManager (line 48): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/core/tracking.py
- DebugLog (line 17): Class definition
- DebugLog.dummy_log (line 19): Public function
- log_function (line 24): Public function
- decorator (line 25): Public function
- UsageTracker (line 42): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/core/budget_component.py
- BudgetComponent (line 13): Class definition
- BudgetComponent.get_capabilities (line 79): Public function
- BudgetComponent.get_metadata (line 94): Public function
- get_budget_engine (line 107): Public function

### /Users/cskoons/projects/github/Tekton/Budget/budget/utils/hermes_helper.py
- DebugLog (line 20): Class definition
- DebugLog.dummy_log (line 22): Public function
- log_function (line 27): Public function
- decorator (line 28): Public function
- HermesRegistrationClient (line 35): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/cli/main.py
- DebugLog (line 26): Class definition
- DebugLog.dummy_log (line 28): Public function
- log_function (line 33): Public function
- decorator (line 34): Public function
- cli (line 50): Public function

### /Users/cskoons/projects/github/Tekton/Budget/budget/adapters/apollo.py
- DebugLog (line 22): Class definition
- DebugLog.dummy_log (line 24): Public function
- log_function (line 29): Public function
- decorator (line 30): Public function
- ApolloAdapter (line 47): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/adapters/rhetor.py
- DebugLog (line 23): Class definition
- DebugLog.dummy_log (line 25): Public function
- log_function (line 30): Public function
- decorator (line 31): Public function
- RhetorAdapter (line 49): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/adapters/price_manager.py
- DebugLog (line 21): Class definition
- DebugLog.dummy_log (line 23): Public function
- log_function (line 28): Public function
- decorator (line 29): Public function
- PriceManager (line 46): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/adapters/llm_adapter.py
- DebugLog (line 25): Class definition
- DebugLog.dummy_log (line 27): Public function
- log_function (line 32): Public function
- decorator (line 33): Public function
- LLMAdapter (line 40): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/adapters/apollo_enhancements.py
- DebugLog (line 22): Class definition
- DebugLog.dummy_log (line 24): Public function
- log_function (line 29): Public function
- decorator (line 30): Public function
- ApolloEnhancedAdapter (line 51): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/api/models.py
- DebugLog (line 20): Class definition
- DebugLog.dummy_log (line 22): Public function
- log_function (line 27): Public function
- decorator (line 28): Public function
- CreateBudgetRequest (line 40): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/api/mcp_endpoints.py
- DebugLog (line 26): Class definition
- DebugLog.dummy_log (line 28): Public function
- log_function (line 33): Public function
- decorator (line 34): Public function
- MCPMessage (line 107): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/api/websocket_server.py
- DebugLog (line 27): Class definition
- DebugLog.dummy_log (line 29): Public function
- log_function (line 34): Public function
- decorator (line 35): Public function
- MessageType (line 46): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/api/assistant_endpoints.py
- DebugLog (line 25): Class definition
- DebugLog.dummy_log (line 27): Public function
- log_function (line 32): Public function
- decorator (line 33): Public function
- AnalysisRequest (line 45): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/api/app.py
- DebugLog (line 52): Class definition
- DebugLog.dummy_log (line 54): Public function
- log_function (line 59): Public function
- decorator (line 60): Public function
- startup_callback (line 91): Async function

### /Users/cskoons/projects/github/Tekton/Budget/budget/api/endpoints.py
- DebugLog (line 19): Class definition
- DebugLog.dummy_log (line 21): Public function
- log_function (line 26): Public function
- decorator (line 27): Public function
- create_budget (line 89): Async function

### /Users/cskoons/projects/github/Tekton/Budget/budget/api/dependencies.py
- DebugLog (line 18): Class definition
- DebugLog.dummy_log (line 20): Public function
- log_function (line 25): Public function
- decorator (line 26): Public function
- get_authenticated_user (line 37): Async function

### /Users/cskoons/projects/github/Tekton/Budget/budget/service/assistant.py
- DebugLog (line 27): Class definition
- DebugLog.dummy_log (line 29): Public function
- log_function (line 34): Public function
- decorator (line 35): Public function
- BudgetAssistant (line 45): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/data/models.py
- DebugLog (line 20): Class definition
- DebugLog.dummy_log (line 22): Public function
- log_function (line 27): Public function
- decorator (line 28): Public function
- BudgetTier (line 33): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/data/db_models.py
- DebugLog (line 28): Class definition
- DebugLog.dummy_log (line 30): Public function
- log_function (line 35): Public function
- decorator (line 36): Public function
- BudgetDBModel (line 58): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/data/repository.py
- DebugLog (line 21): Class definition
- DebugLog.dummy_log (line 23): Public function
- log_function (line 28): Public function
- decorator (line 29): Public function
- Repository (line 51): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/core/mcp/hermes_bridge.py
- BudgetMCPBridge (line 16): Class definition
- BudgetMCPBridge.initialize (line 31): Async function
- BudgetMCPBridge.register_default_tools (line 56): Async function
- BudgetMCPBridge.register_fastmcp_tools (line 71): Async function
- BudgetMCPBridge.register_fastmcp_tool (line 84): Async function

### /Users/cskoons/projects/github/Tekton/Budget/budget/core/mcp/tools.py
- mcp_tool (line 24): Public function
- decorator (line 25): Public function
- mcp_capability (line 29): Public function
- decorator (line 30): Public function
- allocate_budget (line 69): Async function, MCP tool

### /Users/cskoons/projects/github/Tekton/Budget/budget/core/mcp/capabilities.py
- BudgetManagementCapability (line 12): Class definition
- BudgetManagementCapability.get_supported_operations (line 20): Public function
- BudgetManagementCapability.get_capability_metadata (line 35): Public function
- ModelRecommendationCapability (line 50): Class definition
- ModelRecommendationCapability.get_supported_operations (line 58): Public function

### /Users/cskoons/projects/github/Tekton/Budget/budget/adapters/price_sources/web_scraper.py
- DebugLog (line 22): Class definition
- DebugLog.dummy_log (line 24): Public function
- log_function (line 29): Public function
- decorator (line 30): Public function
- WebScraperAdapter (line 37): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/adapters/price_sources/litellm.py
- DebugLog (line 20): Class definition
- DebugLog.dummy_log (line 22): Public function
- log_function (line 27): Public function
- decorator (line 28): Public function
- LiteLLMAdapter (line 35): Class definition

### /Users/cskoons/projects/github/Tekton/Budget/budget/adapters/price_sources/base.py
- DebugLog (line 20): Class definition
- DebugLog.dummy_log (line 22): Public function
- log_function (line 27): Public function
- decorator (line 28): Public function
- PriceSourceAdapter (line 35): Class definition
