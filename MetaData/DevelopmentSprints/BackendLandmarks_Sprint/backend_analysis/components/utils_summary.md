# utils Analysis Summary

**Generated**: 2025-06-21T17:24:44.543612

## Statistics
- Files analyzed: 20
- Functions: 190
- Classes: 40
- Landmarks identified: 201
- API endpoints: 3
- MCP tools: 0

## Patterns Found
- fastapi
- mcp
- websocket
- error_handling
- async
- singleton

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
