# Synthesis Analysis Summary

**Generated**: 2025-06-21T17:26:49.158178

## Statistics
- Files analyzed: 30
- Functions: 206
- Classes: 31
- Landmarks identified: 196
- API endpoints: 15
- MCP tools: 0

## Patterns Found
- fastapi
- singleton
- async
- error_handling
- mcp
- websocket

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/__init__.py
- NullHandler (line 27): Class definition
- NullHandler.emit (line 28): Public function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/step_handlers.py
- handle_command_step (line 24): Async function, High complexity
- handle_function_step (line 135): Async function, High complexity
- handle_api_step (line 224): Async function, High complexity
- handle_condition_step (line 337): Async function
- handle_subprocess_step (line 407): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/execution_engine.py
- ExecutionEngine (line 34): Class definition
- ExecutionEngine.execute_plan (line 91): Async function
- ExecutionEngine.on_before_step (line 419): Async function
- ExecutionEngine.on_after_step (line 424): Async function
- ExecutionEngine.on_step_error (line 430): Async function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/phase_executor.py
- PhaseExecutor (line 20): Class definition
- PhaseExecutor.register_handler (line 41): Public function
- PhaseExecutor.execute_phases (line 59): Async function
- PhaseExecutor.cancel_execution (line 210): Async function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/phase_models.py
- PhaseStatus (line 13): Class definition

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/events.py
- EventManager (line 21): Class definition
- EventManager.get_instance (line 32): Public function
- EventManager.emit (line 50): Async function, High complexity
- EventManager.subscribe (line 109): Public function
- EventManager.unsubscribe (line 126): Public function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/execution_step.py
- ExecutionStep (line 30): Class definition
- ExecutionStep.execute (line 54): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/phase_examples.py
- example (line 16): Async function
- handle_setup (line 33): Async function
- handle_build (line 38): Async function
- handle_test (line 43): Async function
- handle_package (line 48): Async function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/integration_base.py
- ComponentAdapter (line 17): Class definition
- ComponentAdapter.initialize (line 36): Async function
- ComponentAdapter.shutdown (line 46): Async function
- ComponentAdapter.ping (line 56): Async function
- ComponentAdapter.invoke_capability (line 65): Async function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/synthesis_component.py
- SynthesisComponent (line 10): Class definition
- SynthesisComponent.get_capabilities (line 67): Public function
- SynthesisComponent.get_metadata (line 77): Public function
- SynthesisComponent.get_component_status (line 86): Has side effects
- SynthesisComponent.initialize_mcp_bridge (line 105): Async function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/integration.py
- IntegrationManager (line 20): Class definition
- IntegrationManager.initialize (line 44): Async function
- IntegrationManager.shutdown (line 86): Async function
- IntegrationManager.get_adapter (line 106): Public function
- IntegrationManager.invoke_capability (line 118): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/condition_evaluator.py
- evaluate_condition (line 17): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/execution_models.py
- ExecutionStage (line 13): Class definition
- ExecutionStatus (line 23): Class definition
- ExecutionPriority (line 33): Class definition
- ExecutionResult (line 41): Class definition
- ExecutionResult.to_dict (line 64): Public function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/loop_handlers.py
- handle_loop_step (line 19): Async function, High complexity
- handle_for_loop (line 77): Async function, High complexity
- handle_while_loop (line 200): Async function, High complexity
- handle_foreach_loop (line 285): Async function, High complexity
- handle_count_loop (line 411): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/integration_adapters.py
- PrometheusAdapter (line 22): Class definition
- PrometheusAdapter.initialize (line 65): Async function, High complexity
- PrometheusAdapter.invoke_capability (line 115): Async function, High complexity
- AthenaAdapter (line 199): Class definition
- AthenaAdapter.initialize (line 252): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/llm_adapter.py
- LLMAdapter (line 20): Class definition
- LLMAdapter.initialize (line 50): Async function
- LLMAdapter.ensure_initialized (line 82): Async function
- LLMAdapter.shutdown (line 93): Async function
- LLMAdapter.enhance_execution_plan (line 99): Async function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/phase_manager.py
- PhaseManager (line 19): Class definition
- PhaseManager.register_phase (line 32): Public function
- PhaseManager.register_callback (line 70): Public function
- PhaseManager.get_phase (line 91): Public function
- PhaseManager.get_all_phases (line 103): Public function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/api/fastmcp_endpoints.py
- MCPRequest (line 30): Class definition
- MCPResponse (line 36): Class definition
- get_synthesis_status (line 69): Async function
- execute_synthesis_workflow (line 97): Async function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/api/app.py
- APIResponse (line 70): Class definition
- ExecutionRequest (line 78): Class definition
- ExecutionResponse (line 87): Class definition
- VariableRequest (line 96): Class definition
- startup_callback (line 104): Async function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/mcp/hermes_bridge.py
- SynthesisMCPBridge (line 16): Class definition
- SynthesisMCPBridge.initialize (line 31): Async function
- SynthesisMCPBridge.register_default_tools (line 56): Async function
- SynthesisMCPBridge.register_fastmcp_tools (line 71): Async function
- SynthesisMCPBridge.register_fastmcp_tool (line 84): Async function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/mcp/tools.py
- mcp_tool (line 22): Public function
- decorator (line 23): Public function
- synthesize_component_data (line 35): Async function, High complexity
- create_unified_report (line 149): Async function, High complexity
- merge_data_streams (line 268): Async function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/mcp/__init__.py
- get_all_capabilities (line 21): Public function
- get_all_tools (line 30): Public function

### /Users/cskoons/projects/github/Tekton/Synthesis/synthesis/core/mcp/capabilities.py
- DataSynthesisCapability (line 12): Class definition
- DataSynthesisCapability.get_supported_operations (line 20): Public function
- DataSynthesisCapability.get_capability_metadata (line 32): Public function
- IntegrationOrchestrationCapability (line 46): Class definition
- IntegrationOrchestrationCapability.get_supported_operations (line 54): Public function
