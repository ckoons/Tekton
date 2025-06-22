# Terma Analysis Summary

**Generated**: 2025-06-21T17:26:49.280829

## Statistics
- Files analyzed: 25
- Functions: 177
- Classes: 27
- Landmarks identified: 147
- API endpoints: 23
- MCP tools: 0

## Patterns Found
- fastapi
- async
- error_handling
- mcp
- websocket

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Terma/terma/core/terminal.py
- TerminalSession (line 21): Class definition
- TerminalSession.start (line 40): High complexity
- TerminalSession.stop (line 222): Public function
- TerminalSession.write (line 248): Has side effects
- TerminalSession.read (line 272): Public function

### /Users/cskoons/projects/github/Tekton/Terma/terma/core/session_manager.py
- SessionManager (line 17): Class definition
- SessionManager.start (line 35): Public function
- SessionManager.stop (line 42): Public function
- SessionManager.create_session_async (line 93): Async function
- SessionManager.create_session (line 139): Public function

### /Users/cskoons/projects/github/Tekton/Terma/terma/core/llm_adapter.py
- LLMAdapter (line 24): Class definition
- LLMAdapter.add_message (line 154): Public function
- LLMAdapter.clear_context (line 170): Public function
- LLMAdapter.set_provider_and_model (line 181): Public function
- LLMAdapter.get_available_providers (line 204): Async function

### /Users/cskoons/projects/github/Tekton/Terma/terma/utils/logging.py
- setup_logging (line 7): Public function

### /Users/cskoons/projects/github/Tekton/Terma/terma/utils/config.py
- Config (line 45): Class definition
- Config.get (line 100): Public function
- Config.set (line 126): Public function
- Config.get_all_llm_providers (line 142): Public function
- Config.get_provider_models (line 150): Public function

### /Users/cskoons/projects/github/Tekton/Terma/terma/cli/launch.py
- launch_tmux_terminal (line 23): Has side effects
- launch_screen_terminal (line 104): Has side effects
- launch_native_terminal (line 185): Has side effects, High complexity
- launch_browser_terminal (line 278): Public function
- create_or_get_session (line 315): Public function

### /Users/cskoons/projects/github/Tekton/Terma/terma/cli/main.py
- main (line 25): High complexity
- check_port (line 85): Public function

### /Users/cskoons/projects/github/Tekton/Terma/terma/integrations/hermes_integration.py
- HermesIntegration (line 14): Class definition
- HermesIntegration.register_capabilities (line 169): Public function
- HermesIntegration.handle_message (line 277): Async function
- HermesIntegration.publish_event (line 337): Async function

### /Users/cskoons/projects/github/Tekton/Terma/terma/api/fastmcp_endpoints.py
- MCPRequest (line 30): Class definition
- MCPResponse (line 36): Class definition
- get_terminal_status (line 69): Async function
- execute_terminal_workflow (line 99): Async function
- get_terminal_health (line 143): Async function

### /Users/cskoons/projects/github/Tekton/Terma/terma/api/app.py
- SessionCreate (line 32): Class definition
- SessionResponse (line 36): Class definition
- SessionInfo (line 41): Class definition
- SessionsResponse (line 50): Class definition
- WriteRequest (line 54): Class definition

### /Users/cskoons/projects/github/Tekton/Terma/terma/api/ui_server.py
- root (line 36): Async function
- get_terminal_ui (line 41): Async function
- launch_terminal (line 55): Async function
- get_terminal_session (line 69): Async function
- get_image (line 74): Async function

### /Users/cskoons/projects/github/Tekton/Terma/terma/api/websocket.py
- TerminalWebSocketHandler (line 27): Class definition
- TerminalWebSocketHandler.add_websocket (line 43): Async function
- TerminalWebSocketHandler.remove_websocket (line 64): Async function
- TerminalWebSocketHandler.handle_message (line 119): Async function
- TerminalWebSocketServer (line 240): Class definition

### /Users/cskoons/projects/github/Tekton/Terma/terma/core/mcp/tools.py
- create_terminal_session (line 22): Async function, Has side effects
- manage_session_lifecycle (line 95): Async function, High complexity
- execute_terminal_commands (line 169): Async function, Has side effects
- monitor_session_performance (line 252): Async function, High complexity
- configure_terminal_settings (line 356): Async function

### /Users/cskoons/projects/github/Tekton/Terma/terma/core/mcp/__init__.py
- get_all_capabilities (line 21): Public function
- get_all_tools (line 30): Public function

### /Users/cskoons/projects/github/Tekton/Terma/terma/core/mcp/capabilities.py
- TerminalManagementCapability (line 12): Class definition
- TerminalManagementCapability.get_supported_operations (line 19): Public function
- TerminalManagementCapability.get_capability_metadata (line 31): Public function
- LLMIntegrationCapability (line 47): Class definition
- LLMIntegrationCapability.get_supported_operations (line 54): Public function

### /Users/cskoons/projects/github/Tekton/Terma/venv/lib/python3.10/site-packages/_virtualenv.py
- patch_dist (line 9): Public function
- parse_config_files (line 19): Public function
- _Finder (line 40): Class definition
- _Finder.find_spec (line 50): High complexity
- _Finder.exec_module (line 88): Public function
