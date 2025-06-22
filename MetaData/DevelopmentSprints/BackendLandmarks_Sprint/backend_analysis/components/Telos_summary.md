# Telos Analysis Summary

**Generated**: 2025-06-21T17:26:49.227252

## Statistics
- Files analyzed: 39
- Functions: 241
- Classes: 68
- Landmarks identified: 255
- API endpoints: 30
- MCP tools: 11

## Patterns Found
- fastapi
- singleton
- async
- error_handling
- mcp
- websocket

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Telos/telos/client.py
- TelosClient (line 41): Class definition
- TelosClient.create_project (line 67): Async function
- TelosClient.create_requirement (line 106): Async function
- TelosClient.get_project (line 158): Async function
- TelosClient.get_requirements (line 184): Async function

### /Users/cskoons/projects/github/Tekton/Telos/telos/prometheus_connector.py
- TelosPrometheusConnector (line 19): Class definition
- TelosPrometheusConnector.initialize (line 47): Async function
- TelosPrometheusConnector.prepare_requirements_for_planning (line 64): Async function
- TelosPrometheusConnector.create_plan (line 109): Async function
- TelosPrometheusConnector.request_clarification (line 157): Async function

### /Users/cskoons/projects/github/Tekton/Telos/examples/client_usage.py
- project_management_example (line 34): Async function
- requirements_analysis_example (line 119): Async function, High complexity
- requirement_refinement_example (line 202): Async function
- telos_ui_example (line 253): Async function
- error_handling_example (line 306): Async function

### /Users/cskoons/projects/github/Tekton/Telos/examples/llm_integration_example.py
- analyze_requirement_example (line 27): Async function
- generate_traces_example (line 74): Async function
- initialize_project_example (line 126): Async function
- main (line 168): Async function

### /Users/cskoons/projects/github/Tekton/Telos/telos/ui/interactive_refine.py
- InteractiveRefiner (line 23): Class definition
- InteractiveRefiner.refine_requirement (line 36): Async function, High complexity
- analyze_requirements_for_planning (line 235): Async function
- refine_requirement_cmd (line 297): Public function
- analyze_for_planning_cmd (line 322): High complexity

### /Users/cskoons/projects/github/Tekton/Telos/telos/ui/cli_commands.py
- create_project (line 20): Public function
- list_projects (line 32): Public function
- show_project (line 50): Public function
- delete_project (line 77): Public function
- add_requirement (line 93): Public function

### /Users/cskoons/projects/github/Tekton/Telos/telos/ui/analyzers.py
- RequirementAnalyzer (line 20): Class definition
- RequirementAnalyzer.analyze_requirement (line 79): Async function

### /Users/cskoons/projects/github/Tekton/Telos/telos/ui/formatters.py
- format_detailed_feedback (line 12): Public function
- display_requirement (line 55): Public function

### /Users/cskoons/projects/github/Tekton/Telos/telos/ui/chat_interface.py
- TelosChatInterface (line 23): Class definition
- TelosChatInterface.start (line 93): Public function
- main (line 410): Public function

### /Users/cskoons/projects/github/Tekton/Telos/telos/ui/cli_helpers.py
- format_timestamp (line 11): Public function
- get_status_symbol (line 23): Public function
- get_priority_symbol (line 42): Public function
- visualize_hierarchy (line 60): Has side effects
- print_node (line 70): Public function

### /Users/cskoons/projects/github/Tekton/Telos/telos/ui/cli_parser.py
- create_parser (line 10): Public function
- parse_args (line 120): Public function

### /Users/cskoons/projects/github/Tekton/Telos/telos/ui/cli.py
- TelosCLI (line 33): Class definition
- TelosCLI.run (line 86): Public function
- TelosCLI.create_project (line 140): Public function
- TelosCLI.list_projects (line 143): Public function
- TelosCLI.show_project (line 146): Public function

### /Users/cskoons/projects/github/Tekton/Telos/telos/core/requirement.py
- Requirement (line 14): Class definition
- Requirement.update (line 68): Public function
- Requirement.to_dict (line 98): Public function
- Requirement.from_dict (line 118): Public function

### /Users/cskoons/projects/github/Tekton/Telos/telos/core/telos_component.py
- TelosComponent (line 13): Class definition
- TelosComponent.get_capabilities (line 62): Public function
- TelosComponent.get_metadata (line 73): Public function
- TelosComponent.get_component_status (line 82): Public function

### /Users/cskoons/projects/github/Tekton/Telos/telos/core/llm_adapter.py
- LLMAdapter (line 33): Class definition
- LLMAdapter.chat (line 337): Async function, High complexity
- LLMAdapter.generate_stream (line 427): Async function
- LLMAdapter.error_generator (line 453): Async function
- LLMAdapter.analyze_requirement (line 457): Async function

### /Users/cskoons/projects/github/Tekton/Telos/telos/core/project.py
- Project (line 16): Class definition
- Project.add_requirement (line 46): Public function
- Project.get_requirement (line 59): Public function
- Project.update_requirement (line 70): Has side effects
- Project.delete_requirement (line 88): Public function

### /Users/cskoons/projects/github/Tekton/Telos/telos/core/requirements_manager.py
- RequirementsManager (line 17): Class definition
- RequirementsManager.create_project (line 33): Public function
- RequirementsManager.get_project (line 58): Public function
- RequirementsManager.get_all_projects (line 69): Public function
- RequirementsManager.delete_project (line 77): Public function

### /Users/cskoons/projects/github/Tekton/Telos/telos/utils/hermes_helper.py
- HermesHelper (line 24): Class definition
- HermesHelper.register_service (line 41): Async function, Has side effects, High complexity
- HermesHelper.discover_services (line 138): Async function
- HermesHelper.find_service (line 159): Async function
- HermesHelper.invoke_capability (line 185): Async function

### /Users/cskoons/projects/github/Tekton/Telos/telos/models/trace.py
- TraceBase (line 12): Class definition
- TraceCreate (line 20): Class definition
- TraceUpdate (line 24): Class definition
- TraceModel (line 30): Class definition
- TraceListItem (line 38): Class definition

### /Users/cskoons/projects/github/Tekton/Telos/telos/models/requirement.py
- HistoryEntry (line 12): Class definition
- RequirementBase (line 18): Class definition
- RequirementCreate (line 30): Class definition
- RequirementUpdate (line 34): Class definition
- RequirementModel (line 46): Class definition

### /Users/cskoons/projects/github/Tekton/Telos/telos/models/export.py
- ExportOptions (line 11): Class definition
- ExportResult (line 19): Class definition
- ImportOptions (line 25): Class definition
- ImportResult (line 31): Class definition
- ExportModel (line 39): Class definition

### /Users/cskoons/projects/github/Tekton/Telos/telos/models/project.py
- ProjectBase (line 12): Class definition
- ProjectCreate (line 18): Class definition
- ProjectUpdate (line 22): Class definition
- RequirementSummary (line 28): Class definition
- ProjectHierarchy (line 36): Class definition

### /Users/cskoons/projects/github/Tekton/Telos/telos/models/validation.py
- ValidationCriteria (line 11): Class definition
- ValidationIssue (line 20): Class definition
- RequirementValidationResult (line 27): Class definition
- ValidationSummary (line 35): Class definition
- ValidationModel (line 43): Class definition

### /Users/cskoons/projects/github/Tekton/Telos/telos/api/fastmcp_endpoints.py
- FastMCPAdapter (line 43): Class definition
- FastMCPAdapter.get_requirements_manager (line 51): Async function
- FastMCPAdapter.get_prometheus_connector (line 55): Async function
- get_requirements_manager_dependency (line 64): Public function
- get_prometheus_connector_dependency (line 71): Public function

### /Users/cskoons/projects/github/Tekton/Telos/telos/api/app.py
- ProjectCreateRequest (line 52): Class definition
- ProjectUpdateRequest (line 57): Class definition
- RequirementCreateRequest (line 62): Class definition
- RequirementUpdateRequest (line 74): Class definition
- RequirementRefinementRequest (line 85): Class definition

### /Users/cskoons/projects/github/Tekton/Telos/telos/core/mcp/hermes_bridge.py
- TelosMCPBridge (line 16): Class definition
- TelosMCPBridge.initialize (line 32): Async function
- TelosMCPBridge.register_default_tools (line 57): Async function
- TelosMCPBridge.register_fastmcp_tools (line 72): Async function
- TelosMCPBridge.register_fastmcp_tool (line 85): Async function

### /Users/cskoons/projects/github/Tekton/Telos/telos/core/mcp/tools.py
- mcp_tool (line 19): Public function
- decorator (line 20): Public function
- mcp_capability (line 24): Public function
- decorator (line 25): Public function
- RequirementsManagementCapability (line 38): Class definition

### /Users/cskoons/projects/github/Tekton/Telos/telos/core/mcp/__init__.py
- get_all_capabilities (line 22): Public function
- get_all_tools (line 31): Public function

### /Users/cskoons/projects/github/Tekton/Telos/telos/core/mcp/capabilities.py
- StrategicAnalysisCapability (line 12): Class definition
- StrategicAnalysisCapability.get_supported_operations (line 20): Public function
- StrategicAnalysisCapability.get_capability_metadata (line 32): Public function
- GoalManagementCapability (line 46): Class definition
- GoalManagementCapability.get_supported_operations (line 54): Public function
