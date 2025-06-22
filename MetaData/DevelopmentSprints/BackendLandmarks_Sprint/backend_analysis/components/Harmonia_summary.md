# Harmonia Analysis Summary

**Generated**: 2025-06-21T17:26:48.705545

## Statistics
- Files analyzed: 30
- Functions: 255
- Classes: 60
- Landmarks identified: 276
- API endpoints: 32
- MCP tools: 34

## Patterns Found
- fastapi
- singleton
- async
- error_handling
- mcp
- websocket

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/client.py
- HarmoniaClient (line 41): Class definition
- HarmoniaClient.create_workflow (line 67): Async function
- HarmoniaClient.execute_workflow (line 116): Async function
- HarmoniaClient.get_workflow_status (line 150): Async function
- HarmoniaClient.cancel_workflow (line 176): Async function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/__main__.py
- parse_args (line 33): Public function
- initialize_engine (line 64): Async function
- run_api_server (line 102): Public function
- main (line 136): Public function

### /Users/cskoons/projects/github/Tekton/Harmonia/examples/client_usage.py
- simple_workflow_example (line 45): Async function, High complexity
- parallel_workflow_example (line 184): Async function
- workflow_state_example (line 289): Async function
- error_handling_example (line 387): Async function
- main (line 420): Async function

### /Users/cskoons/projects/github/Tekton/Harmonia/examples/llm_adapter_example.py
- workflow_creation_example (line 27): Async function
- expression_evaluation_example (line 90): Async function
- state_transition_example (line 137): Async function
- template_expansion_example (line 242): Async function
- workflow_troubleshooting_example (line 322): Async function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/harmonia_component.py
- HarmoniaComponent (line 16): Class definition
- HarmoniaComponent.get_capabilities (line 174): Public function
- HarmoniaComponent.get_metadata (line 194): Public function
- ConnectionManager (line 216): Class definition
- ConnectionManager.cleanup (line 225): Async function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/expressions.py
- evaluate_expression (line 26): High complexity
- get_nested_value (line 102): High complexity
- substitute_parameters (line 144): Public function
- evaluate_condition (line 192): High complexity

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/workflow_startup.py
- WorkflowEngineStartup (line 24): Class definition
- WorkflowEngineStartup.initialize (line 45): Async function
- WorkflowEngineStartup.shutdown (line 157): Async function
- MockComponentAdapter (line 170): Class definition
- MockComponentAdapter.execute_action (line 188): Async function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/engine.py
- WorkflowEngine (line 43): Class definition
- WorkflowEngine.execute_workflow (line 94): Async function
- WorkflowEngine.create_checkpoint (line 772): Async function
- WorkflowEngine.restore_from_checkpoint (line 829): Async function, High complexity
- WorkflowEngine.pause_workflow (line 915): Async function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/startup_instructions.py
- StartUpInstructions (line 29): Class definition
- StartUpInstructions.to_dict (line 70): Public function
- StartUpInstructions.to_json (line 79): Public function
- StartUpInstructions.from_dict (line 89): Public function
- StartUpInstructions.from_json (line 106): Public function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/template.py
- TemplateManager (line 27): Class definition
- TemplateManager.save_template (line 82): Public function
- TemplateManager.get_template (line 103): Public function
- TemplateManager.get_templates (line 115): Public function
- TemplateManager.create_template (line 138): Public function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/workflow.py
- TaskStatus (line 17): Class definition
- WorkflowStatus (line 26): Class definition
- Task (line 37): Class definition
- Task.to_dict (line 65): Public function
- Task.from_dict (line 86): Public function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/component.py
- ActionNotFoundError (line 20): Class definition
- ComponentAdapter (line 28): Class definition
- ComponentAdapter.component_name (line 32): Public function
- ComponentAdapter.execute_action (line 36): Async function
- ComponentAdapter.get_actions (line 49): Async function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/state.py
- StateManager (line 19): Class definition
- StateManager.save_workflow_state (line 51): Async function, Has side effects
- StateManager.load_workflow_state (line 90): Async function, Has side effects
- StateManager.delete_workflow_state (line 136): Async function
- StateManager.list_workflow_states (line 171): Async function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/models/execution.py
- EventType (line 19): Class definition
- ExecutionEvent (line 41): Class definition
- ExecutionMetrics (line 53): Class definition
- ExecutionMetrics.total_duration_seconds (line 68): Public function
- ExecutionMetrics.critical_path (line 73): Public function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/models/webhook.py
- WebhookTriggerType (line 17): Class definition
- WebhookAuthType (line 28): Class definition
- WebhookDefinition (line 39): Class definition
- WebhookDefinition.validate_endpoint (line 57): Public function
- WebhookEvent (line 64): Class definition

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/models/template.py
- ParameterDefinition (line 18): Class definition
- ParameterDefinition.validate_type (line 34): Public function
- TemplateVersion (line 42): Class definition
- TemplateCategory (line 52): Class definition
- Template (line 61): Class definition

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/models/workflow.py
- TaskType (line 17): Class definition
- TaskStatus (line 32): Class definition
- WorkflowStatus (line 44): Class definition
- RetryPolicy (line 55): Class definition
- RetryPolicy.validate_max_retries (line 65): Public function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/api/fastmcp_endpoints.py
- get_workflow_engine (line 34): Async function
- set_workflow_engine (line 51): Public function
- fastmcp_startup (line 62): Async function
- fastmcp_shutdown (line 73): Async function
- health_check (line 84): Async function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/api/app.py
- startup_callback (line 93): Async function
- ConnectionManager (line 204): Class definition
- ConnectionManager.connect (line 212): Async function
- ConnectionManager.disconnect (line 229): Public function
- ConnectionManager.subscribe (line 240): Public function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/llm/adapter.py
- LLMAdapter (line 27): Class definition
- LLMAdapter.generate (line 340): Async function
- LLMAdapter.error_stream (line 400): Async function
- LLMAdapter.generate_with_template (line 406): Async function
- LLMAdapter.error_stream (line 462): Async function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/mcp/hermes_bridge.py
- HarmoniaMCPBridge (line 16): Class definition
- HarmoniaMCPBridge.initialize (line 31): Async function
- HarmoniaMCPBridge.register_default_tools (line 56): Async function
- HarmoniaMCPBridge.register_fastmcp_tools (line 71): Async function
- HarmoniaMCPBridge.register_fastmcp_tool (line 84): Async function

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/mcp/tools.py
- create_workflow_definition (line 40): Async function, MCP tool
- update_workflow_definition (line 117): Async function, High complexity, MCP tool
- delete_workflow_definition (line 204): Async function, MCP tool
- get_workflow_definition (line 253): Async function, MCP tool
- list_workflow_definitions (line 307): Async function, MCP tool

### /Users/cskoons/projects/github/Tekton/Harmonia/harmonia/core/mcp/capabilities.py
- WorkflowDefinitionCapability (line 12): Class definition
- WorkflowDefinitionCapability.get_supported_operations (line 20): Public function
- WorkflowDefinitionCapability.get_capability_metadata (line 35): Public function
- WorkflowExecutionCapability (line 50): Class definition
- WorkflowExecutionCapability.get_supported_operations (line 58): Public function
