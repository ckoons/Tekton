# shared Analysis Summary

**Generated**: 2025-06-21T17:26:05.491297

## Statistics
- Files analyzed: 42
- Functions: 301
- Classes: 60
- Landmarks identified: 308
- API endpoints: 6
- MCP tools: 0

## Patterns Found
- fastapi
- singleton
- async
- error_handling
- mcp
- websocket

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/shared/utils/graceful_shutdown.py
- GracefulShutdown (line 15): Class definition
- GracefulShutdown.add_handler (line 26): Public function
- GracefulShutdown.notify_hermes_shutdown (line 30): Async function
- GracefulShutdown.shutdown (line 52): Async function
- GracefulShutdown.setup_signal_handlers (line 86): Public function

### /Users/cskoons/projects/github/Tekton/shared/utils/startup.py
- StartupMetrics (line 19): Class definition
- StartupError (line 30): Class definition
- component_startup (line 38): Async function
- check_dependencies (line 113): Async function
- check_dependency (line 133): Async function

### /Users/cskoons/projects/github/Tekton/shared/utils/tekton_startup.py
- initialize_tekton_environment (line 29): High complexity
- setup_component_logging (line 102): Public function
- log_component_environment (line 144): Public function
- get_component_port (line 180): Public function
- is_debug_enabled (line 202): Public function

### /Users/cskoons/projects/github/Tekton/shared/utils/env_manager.py
- TektonEnvManager (line 38): Class definition
- TektonEnvManager.load_environment (line 116): High complexity
- TektonEnvManager.get_current_environment (line 208): Public function
- TektonEnvManager.get_tekton_variables (line 217): Public function
- TektonEnvManager.save_tekton_settings (line 255): Public function

### /Users/cskoons/projects/github/Tekton/shared/utils/global_config.py
- GlobalConfig (line 20): Class definition
- GlobalConfig.get_instance (line 66): Public function
- GlobalConfig.config (line 72): Public function
- GlobalConfig.get_component_config (line 76): Public function
- GlobalConfig.get_data_dir (line 89): Public function

### /Users/cskoons/projects/github/Tekton/shared/utils/env_config.py
- BaseComponentConfig (line 17): Class definition
- BaseComponentConfig.from_env (line 23): Public function
- HermesConfig (line 90): Class definition
- HermesConfig.from_env (line 100): Public function
- EngramConfig (line 111): Class definition

### /Users/cskoons/projects/github/Tekton/shared/utils/shutdown.py
- ShutdownMetrics (line 22): Class definition
- GracefulShutdown (line 32): Class definition
- GracefulShutdown.register_cleanup (line 59): Public function
- GracefulShutdown.shutdown_sequence (line 68): Async function
- create_shutdown_handler (line 130): Public function

### /Users/cskoons/projects/github/Tekton/shared/utils/socket_server.py
- run_with_socket_reuse_async (line 18): Async function
- signal_handler (line 58): Public function
- run_with_socket_reuse (line 70): Public function
- signal_handler (line 114): Public function
- ReuseAddressServer (line 127): Class definition

### /Users/cskoons/projects/github/Tekton/shared/utils/shutdown_endpoint.py
- create_shutdown_router (line 20): Public function
- perform_shutdown (line 38): Async function
- shutdown (line 64): Async function
- api_shutdown (line 91): Async function
- shutdown_status (line 96): Async function

### /Users/cskoons/projects/github/Tekton/shared/utils/templates.py
- create_main_function_template (line 15): Public function
- create_fastapi_app_template (line 72): Public function
- create_health_endpoint_template (line 149): Public function
- create_requirements_template (line 189): Public function
- create_run_script_template (line 213): Public function

### /Users/cskoons/projects/github/Tekton/shared/utils/standard_component.py
- StandardComponentBase (line 23): Class definition
- StandardComponentBase.initialize (line 51): Async function
- StandardComponentBase.shutdown (line 190): Async function, High complexity
- StandardComponentBase.create_app (line 229): Public function
- StandardComponentBase.lifespan (line 246): Async function

### /Users/cskoons/projects/github/Tekton/shared/utils/setup-venvs.py
- VenvManager (line 16): Class definition
- VenvManager.run_command (line 79): Public function
- VenvManager.create_venv (line 92): Has side effects, High complexity
- VenvManager.create_activation_script (line 144): Has side effects
- VenvManager.show_summary (line 192): Public function

### /Users/cskoons/projects/github/Tekton/shared/utils/tekton_log_formats.py
- get_format_for_component (line 39): Public function

### /Users/cskoons/projects/github/Tekton/shared/utils/health_check.py
- create_health_response (line 20): Public function

### /Users/cskoons/projects/github/Tekton/shared/utils/launcher_venv_patch.py
- get_venv_for_component (line 11): Has side effects
- get_venv_python (line 33): Public function
- get_component_command_with_venv (line 77): Public function

### /Users/cskoons/projects/github/Tekton/shared/utils/errors.py
- TektonError (line 10): Class definition
- TektonError.to_dict (line 40): Public function
- TektonError.is_same_error (line 50): Public function
- StartupError (line 59): Class definition
- ShutdownError (line 64): Class definition

### /Users/cskoons/projects/github/Tekton/shared/utils/ensure_registration.py
- ensure_component_registered (line 16): Async function
- register_component_sync (line 48): Public function

### /Users/cskoons/projects/github/Tekton/shared/utils/hermes_registration.py
- HermesRegistration (line 16): Class definition
- HermesRegistration.register_component (line 24): Async function
- HermesRegistration.heartbeat (line 76): Async function
- HermesRegistration.deregister (line 99): Async function
- register_with_hermes (line 122): Async function

### /Users/cskoons/projects/github/Tekton/shared/utils/mcp_helpers.py
- FastMCPServer (line 29): Class definition
- FastMCPServer.register_tool (line 35): Public function
- create_mcp_server (line 39): Public function
- register_mcp_tools (line 71): Public function
- convert_tool_to_schema (line 104): High complexity

### /Users/cskoons/projects/github/Tekton/shared/utils/logging_setup.py
- setup_component_logging (line 23): High complexity
- suppress_external_loggers (line 91): Public function
- get_child_logger (line 139): Public function
- setup_debug_logging (line 153): Public function
- get_logger (line 173): Public function

### /Users/cskoons/projects/github/Tekton/shared/requirements/verify-dependencies.py
- DependencyVerifier (line 17): Class definition
- DependencyVerifier.verify_all (line 186): High complexity
- DependencyVerifier.generate_report (line 240): High complexity
- main (line 306): Public function

### /Users/cskoons/projects/github/Tekton/shared/api/documentation.py
- get_openapi_configuration (line 9): Public function
- get_default_tags (line 70): Public function
- add_custom_responses (line 96): Public function

### /Users/cskoons/projects/github/Tekton/shared/api/example_usage.py
- health_check (line 39): Async function
- list_examples (line 99): Async function
- get_example (line 104): Async function

### /Users/cskoons/projects/github/Tekton/shared/api/endpoints.py
- ReadyResponse (line 15): Class definition
- EndpointInfo (line 24): Class definition
- DiscoveryResponse (line 32): Class definition
- create_ready_endpoint (line 43): Public function
- ready_endpoint (line 61): Async function

### /Users/cskoons/projects/github/Tekton/shared/api/routers.py
- StandardRouters (line 11): Class definition
- Config (line 16): Class definition
- create_standard_routers (line 20): Public function
- mount_standard_routers (line 64): Public function

### /Users/cskoons/projects/github/Tekton/shared/ai_onboarding/onboarding_protocol.py
- AIOnboarding (line 16): Class definition
- AIOnboarding.begin_onboarding (line 31): Async function
- AIOnboarding.explore_collective_consciousness (line 56): Async function
- AIOnboarding.introduce_component (line 90): Async function
- AIOnboarding.memory_exercise (line 124): Async function

### /Users/cskoons/projects/github/Tekton/shared/debug/debug_utils.py
- LogLevel (line 28): Class definition
- DebugLog (line 43): Class definition
- DebugLog.should_log (line 105): Public function
- DebugLog.trace (line 157): Public function
- DebugLog.debug (line 161): Public function

### /Users/cskoons/projects/github/Tekton/shared/mcp/tools/config.py
- GetConfigTool (line 9): Class definition
- GetConfigTool.execute (line 32): Async function, High complexity
- GetConfigTool.get_input_schema (line 79): Public function
- SetConfigTool (line 104): Class definition
- SetConfigTool.execute (line 130): Async function

### /Users/cskoons/projects/github/Tekton/shared/mcp/tools/health.py
- HealthCheckTool (line 9): Class definition
- HealthCheckTool.execute (line 29): Async function, Has side effects, High complexity
- HealthCheckTool.get_input_schema (line 91): Public function

### /Users/cskoons/projects/github/Tekton/shared/mcp/tools/info.py
- ComponentInfoTool (line 8): Class definition
- ComponentInfoTool.execute (line 40): Async function
- ComponentInfoTool.get_input_schema (line 65): Public function

### /Users/cskoons/projects/github/Tekton/shared/mcp/config/settings.py
- MCPConfig (line 14): Class definition
- MCPConfig.from_env (line 44): Public function
- MCPConfig.get_tool_name (line 80): Public function
- MCPConfig.to_env_dict (line 94): Has side effects

### /Users/cskoons/projects/github/Tekton/shared/mcp/client/hermes_client.py
- HermesMCPClient (line 27): Class definition
- HermesMCPClient.health_check (line 74): Async function
- HermesMCPClient.register_tool (line 102): Async function
- HermesMCPClient.unregister_tool (line 176): Async function, Has side effects
- HermesMCPClient.list_tools (line 210): Async function

### /Users/cskoons/projects/github/Tekton/shared/mcp/base/service.py
- MCPService (line 17): Class definition
- MCPService.initialize (line 54): Async function
- MCPService.register_default_tools (line 68): Async function
- MCPService.register_tool (line 77): Async function
- MCPService.execute_tool (line 121): Async function

### /Users/cskoons/projects/github/Tekton/shared/mcp/base/tool.py
- MCPTool (line 18): Class definition
- MCPTool.execute (line 44): Async function
- MCPTool.get_input_schema (line 59): Has side effects, High complexity
- MCPTool.get_spec (line 123): Public function
- MCPTool.get_metadata (line 138): Public function

### /Users/cskoons/projects/github/Tekton/shared/debug/examples/example_service.py
- SampleService (line 9): Class definition
- SampleService.initialize (line 22): Public function
- SampleService.process_request (line 75): Public function
