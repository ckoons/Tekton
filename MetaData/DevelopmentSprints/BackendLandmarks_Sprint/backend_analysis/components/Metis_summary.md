# Metis Analysis Summary

**Generated**: 2025-06-21T17:26:48.759669

## Statistics
- Files analyzed: 35
- Functions: 230
- Classes: 56
- Landmarks identified: 252
- API endpoints: 32
- MCP tools: 0

## Patterns Found
- fastapi
- singleton
- async
- error_handling
- mcp
- websocket

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Metis/metis/config.py
- get_config (line 46): Public function

### /Users/cskoons/projects/github/Tekton/Metis/examples/ai_features_demo.py
- demo_ai_features (line 28): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Metis/metis/core/telos_integration.py
- TelosClient (line 17): Class definition
- TelosClient.get_requirement (line 36): Async function
- TelosClient.search_requirements (line 69): Async function, High complexity
- TelosClient.create_requirement_reference (line 129): Async function
- TelosClient.close (line 156): Async function

### /Users/cskoons/projects/github/Tekton/Metis/metis/core/complexity.py
- ComplexityAnalyzer (line 80): Class definition
- ComplexityAnalyzer.create_standard_factor (line 89): Public function
- ComplexityAnalyzer.create_template (line 112): Public function
- ComplexityAnalyzer.create_score_from_template (line 145): Public function
- ComplexityAnalyzer.create_empty_score (line 162): Public function

### /Users/cskoons/projects/github/Tekton/Metis/metis/core/connection_manager.py
- ConnectionManager (line 10): Class definition
- ConnectionManager.connect (line 18): Async function
- ConnectionManager.disconnect (line 31): Public function
- ConnectionManager.disconnect_all (line 42): Async function
- ConnectionManager.subscribe (line 54): Has side effects

### /Users/cskoons/projects/github/Tekton/Metis/metis/core/task_manager.py
- TaskManager (line 27): Class definition
- TaskManager.create_task (line 52): Async function
- TaskManager.get_task (line 79): Async function
- TaskManager.update_task (line 91): Async function
- TaskManager.delete_task (line 120): Async function

### /Users/cskoons/projects/github/Tekton/Metis/metis/core/dependency.py
- DependencyResolver (line 13): Class definition
- DependencyResolver.get_execution_order (line 22): Public function
- DependencyResolver.check_dependency_issues (line 47): Public function
- DependencyResolver.get_critical_path (line 85): High complexity
- DependencyResolver.calculate_earliest_finish (line 112): Public function

### /Users/cskoons/projects/github/Tekton/Metis/metis/core/storage.py
- InMemoryStorage (line 22): Class definition
- InMemoryStorage.create_task (line 39): Public function
- InMemoryStorage.get_task (line 63): Public function
- InMemoryStorage.update_task (line 76): Has side effects
- InMemoryStorage.delete_task (line 105): High complexity

### /Users/cskoons/projects/github/Tekton/Metis/metis/core/metis_component.py
- MetisComponent (line 13): Class definition
- MetisComponent.get_capabilities (line 135): Public function
- MetisComponent.get_metadata (line 152): Public function

### /Users/cskoons/projects/github/Tekton/Metis/metis/core/llm_adapter.py
- MetisLLMAdapter (line 33): Class definition
- MetisLLMAdapter.decompose_task (line 243): Async function
- MetisLLMAdapter.analyze_task_complexity (line 328): Async function
- MetisLLMAdapter.suggest_task_order (line 415): Async function
- MetisLLMAdapter.test_connection (line 494): Async function

### /Users/cskoons/projects/github/Tekton/Metis/metis/core/task_decomposer.py
- TaskDecomposer (line 22): Class definition
- TaskDecomposer.decompose_task (line 40): Async function
- TaskDecomposer.analyze_decomposition_quality (line 157): Async function

### /Users/cskoons/projects/github/Tekton/Metis/metis/utils/__init__.py
- get_port (line 9): Public function
- get_service_url (line 22): Public function

### /Users/cskoons/projects/github/Tekton/Metis/metis/utils/hermes_helper.py
- HermesClient (line 18): Class definition
- HermesClient.register (line 49): Async function
- HermesClient.deregister (line 101): Async function, Has side effects
- HermesClient.send_heartbeat (line 132): Async function
- HermesClient.get_service (line 161): Async function

### /Users/cskoons/projects/github/Tekton/Metis/metis/models/task.py
- Task (line 19): Class definition
- Task.status_must_be_valid (line 45): Public function
- Task.priority_must_be_valid (line 53): Public function
- Task.update_status (line 59): Public function
- Task.update (line 85): High complexity

### /Users/cskoons/projects/github/Tekton/Metis/metis/models/enums.py
- TaskStatus (line 12): Class definition
- TaskStatus.allowed_transitions (line 26): Public function
- TaskStatus.is_valid_transition (line 43): Public function
- Priority (line 61): Class definition
- ComplexityLevel (line 72): Class definition

### /Users/cskoons/projects/github/Tekton/Metis/metis/models/requirement.py
- RequirementRef (line 15): Class definition
- RequirementRef.update (line 32): Public function
- RequirementSyncStatus (line 47): Class definition

### /Users/cskoons/projects/github/Tekton/Metis/metis/models/complexity.py
- ComplexityFactor (line 17): Class definition
- ComplexityFactor.calculate_weighted_score (line 31): Public function
- ComplexityScore (line 41): Class definition
- ComplexityScore.add_factor (line 55): Public function
- ComplexityScore.update_factor (line 65): Public function

### /Users/cskoons/projects/github/Tekton/Metis/metis/models/subtask.py
- Subtask (line 18): Class definition
- Subtask.update (line 36): Public function
- SubtaskTemplate (line 59): Class definition
- SubtaskTemplate.create_subtasks (line 72): Public function

### /Users/cskoons/projects/github/Tekton/Metis/metis/models/dependency.py
- DependencyType (line 15): Class definition
- Dependency (line 22): Class definition
- Dependency.update (line 37): Public function
- DependencyManager (line 52): Class definition
- DependencyManager.validate_new_dependency (line 61): High complexity

### /Users/cskoons/projects/github/Tekton/Metis/metis/api/controllers.py
- TaskController (line 25): Class definition
- TaskController.create_task (line 45): Async function
- TaskController.get_task (line 78): Async function
- TaskController.update_task (line 104): Async function
- TaskController.delete_task (line 143): Async function

### /Users/cskoons/projects/github/Tekton/Metis/metis/api/fastmcp_endpoints.py
- MCPRequest (line 31): Class definition
- MCPResponse (line 37): Class definition
- get_task_status (line 81): Async function
- execute_task_workflow (line 119): Async function

### /Users/cskoons/projects/github/Tekton/Metis/metis/api/schemas.py
- ApiResponse (line 18): Class definition
- SubtaskCreate (line 25): Class definition
- SubtaskUpdate (line 33): Class definition
- SubtaskResponse (line 41): Class definition
- ComplexityFactorCreate (line 53): Class definition

### /Users/cskoons/projects/github/Tekton/Metis/metis/api/app.py
- startup_callback (line 50): Async function
- ready (line 93): Async function
- discovery (line 105): Async function
- root (line 145): Async function
- health (line 158): Async function

### /Users/cskoons/projects/github/Tekton/Metis/metis/api/routes.py
- get_task_controller (line 27): Public function
- create_task (line 49): Async function
- get_task (line 64): Async function
- update_task (line 79): Async function
- delete_task (line 95): Async function, Has side effects

### /Users/cskoons/projects/github/Tekton/Metis/metis/core/mcp/hermes_bridge.py
- MetisMCPBridge (line 18): Class definition
- MetisMCPBridge.initialize (line 33): Async function
- MetisMCPBridge.register_default_tools (line 73): Async function
- MetisMCPBridge.register_fastmcp_tools (line 88): Async function
- MetisMCPBridge.register_fastmcp_tool (line 101): Async function

### /Users/cskoons/projects/github/Tekton/Metis/metis/core/mcp/tools.py
- get_task_manager (line 25): Public function
- get_llm_adapter (line 32): Public function
- get_task_decomposer (line 39): Public function
- decompose_task (line 48): Async function
- analyze_task_complexity (line 103): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Metis/metis/core/mcp/capabilities.py
- TaskManagementCapability (line 16): Class definition
- DependencyManagementCapability (line 28): Class definition
- TaskAnalyticsCapability (line 40): Class definition
- TelosIntegrationCapability (line 52): Class definition
