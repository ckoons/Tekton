# Rhetor Analysis Summary

**Generated**: 2025-06-21T17:26:48.935537

## Statistics
- Files analyzed: 60
- Functions: 619
- Classes: 90
- Landmarks identified: 630
- API endpoints: 86
- MCP tools: 30

## Patterns Found
- websocket
- fastapi
- async
- error_handling
- mcp
- singleton

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/client.py
- RhetorPromptClient (line 41): Class definition
- RhetorPromptClient.create_prompt_template (line 67): Async function
- RhetorPromptClient.render_prompt (line 119): Async function
- RhetorPromptClient.create_personality (line 153): Async function
- RhetorPromptClient.generate_prompt (line 202): Async function

### /Users/cskoons/projects/github/Tekton/Rhetor/examples/client_usage.py
- prompt_template_example (line 44): Async function
- personality_example (line 125): Async function
- conversation_example (line 210): Async function, High complexity
- error_handling_example (line 293): Async function
- main (line 337): Async function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/registry_fix.py
- apply_fix (line 19): Has side effects, High complexity
- load_from_directory (line 31): Has side effects, High complexity

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/prompt_registry.py
- PromptVersion (line 31): Class definition
- PromptVersion.to_dict (line 57): Public function
- PromptVersion.from_dict (line 68): Public function
- SystemPrompt (line 79): Class definition
- SystemPrompt.current_version (line 123): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/rhetor_component.py
- RhetorComponent (line 11): Class definition
- RhetorComponent.get_capabilities (line 176): Public function
- RhetorComponent.get_metadata (line 188): Public function
- RhetorComponent.get_component_status (line 195): Public function
- RhetorComponent.initialize_mcp_components (line 214): Async function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/context_manager.py
- TokenCounter (line 22): Class definition
- TokenCounter.count_tokens (line 37): Public function
- TokenCounter.count_message_tokens (line 51): Public function
- WindowedContext (line 67): Class definition
- WindowedContext.add_message (line 101): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/specialist_templates.py
- SpecialistTemplate (line 18): Class definition
- SpecialistTemplate.to_specialist_config (line 33): Public function
- SpecialistTemplateRegistry (line 130): Class definition
- SpecialistTemplateRegistry.register_template (line 304): Public function
- SpecialistTemplateRegistry.get_template (line 309): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/model_spawner.py
- AIModelSpawner (line 16): Class definition
- AIModelSpawner.spawn_model (line 43): Has side effects
- AIModelSpawner.spawn_model_pool (line 73): Public function
- AIModelSpawner.get_model_status (line 118): Public function
- example_endpoint (line 144): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/ai_specialist_manager.py
- AISpecialistConfig (line 25): Class definition
- AIMessage (line 37): Class definition
- AISpecialistManager (line 47): Class definition
- AISpecialistManager.create_specialist (line 177): Async function
- AISpecialistManager.send_message (line 216): Async function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/anthropic_max_config.py
- AnthropicMaxConfig (line 16): Class definition
- AnthropicMaxConfig.enabled (line 44): Public function
- AnthropicMaxConfig.enable (line 48): Public function
- AnthropicMaxConfig.disable (line 54): Public function
- AnthropicMaxConfig.get_model_override (line 60): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/ai_messaging_integration.py
- AIMessagingIntegration (line 20): Class definition
- AIMessagingIntegration.initialize (line 47): Async function
- AIMessagingIntegration.cleanup (line 58): Async function
- AIMessagingIntegration.send_specialist_message (line 63): Async function
- AIMessagingIntegration.create_ai_conversation (line 104): Async function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/specialist_router.py
- SpecialistTask (line 20): Class definition
- SpecialistRouter (line 28): Class definition
- SpecialistRouter.set_specialist_manager (line 47): Public function
- SpecialistRouter.allocate_specialist (line 52): Async function, High complexity
- SpecialistRouter.route_to_specialist (line 120): Async function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/template_manager.py
- TemplateVersion (line 21): Class definition
- TemplateVersion.to_dict (line 44): Public function
- TemplateVersion.from_dict (line 54): Public function
- Template (line 64): Class definition
- Template.current_version (line 108): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/component_specialists.py
- ComponentAIConfig (line 20): Class definition
- ComponentSpecialistRegistry (line 29): Class definition
- ComponentSpecialistRegistry.ensure_specialist (line 108): Async function
- ComponentSpecialistRegistry.get_specialist_for_component (line 166): Public function
- ComponentSpecialistRegistry.list_component_specialists (line 171): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/llm_client.py
- LLMClient (line 29): Class definition
- LLMClient.initialize (line 58): Async function
- LLMClient.init_with_timeout (line 98): Async function
- LLMClient.is_initialized (line 122): Public function
- LLMClient.get_provider (line 129): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/communication.py
- Message (line 17): Class definition
- Message.to_dict (line 55): Public function
- Message.from_dict (line 70): Public function
- Conversation (line 85): Class definition
- Conversation.add_message (line 108): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/process_manager.py
- ManagedProcess (line 20): Class definition
- ProcessManager (line 29): Class definition
- ProcessManager.spawn_model (line 48): Has side effects
- ProcessManager.terminate_process (line 108): Public function
- ProcessManager.get_active_processes (line 148): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/model_router.py
- ModelRouter (line 19): Class definition
- ModelRouter.get_config_for_task (line 110): Public function
- ModelRouter.route_request (line 143): Async function, High complexity
- ModelRouter.track_completion (line 215): Async function
- ModelRouter.route_chat_request (line 257): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/prompt_engine.py
- PromptTemplate (line 15): Class definition
- PromptTemplate.format (line 57): Public function
- PromptTemplate.to_dict (line 77): Public function
- PromptTemplate.from_dict (line 88): Public function
- PromptLibrary (line 99): Class definition

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/budget_manager.py
- BudgetPolicy (line 26): Class definition
- BudgetPeriod (line 32): Class definition
- BudgetManager (line 38): Class definition
- BudgetManager.count_tokens (line 204): Public function
- BudgetManager.calculate_cost (line 225): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/utils/engram_helper.py
- EngramClient (line 17): Class definition
- EngramClient.connect (line 49): Async function
- EngramClient.disconnect (line 93): Async function
- EngramClient.ensure_connected (line 100): Async function
- EngramClient.store_memory (line 114): Async function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/cli/cli_commands.py
- list_templates (line 18): High complexity
- create_template (line 65): Has side effects
- get_template (line 117): High complexity
- update_template (line 167): Has side effects
- delete_template (line 207): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/cli/cli_helpers.py
- format_timestamp (line 11): Public function
- parse_key_value_pairs (line 23): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/cli/cli_parser.py
- create_parser (line 10): Public function
- parse_args (line 200): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/cli/main.py
- RhetorCLI (line 39): Class definition
- RhetorCLI.run (line 126): Public function
- RhetorCLI.list_templates (line 199): Public function
- RhetorCLI.create_template (line 206): Public function
- RhetorCLI.get_template (line 213): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/api/app_original.py
- lifespan (line 85): Async function, High complexity
- MessageRequest (line 316): Class definition
- StreamRequest (line 325): Class definition
- ChatRequest (line 333): Class definition
- ProviderModelRequest (line 342): Class definition

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/api/app_simple.py
- root (line 43): Async function
- health (line 52): Async function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/api/app_enhanced.py
- RoleContext (line 117): Class definition
- ProjectContext (line 125): Class definition
- TaskContext (line 133): Class definition
- DataContext (line 140): Class definition
- TektonContext (line 147): Class definition

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/api/fastmcp_endpoints.py
- MCPRequest (line 40): Class definition
- MCPResponse (line 46): Class definition
- MCPStreamRequest (line 53): Class definition
- get_capabilities_func (line 141): Public function
- get_tools_func (line 154): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/api/ai_specialist_endpoints.py
- SpecialistResponse (line 17): Class definition
- SpecialistListResponse (line 31): Class definition
- SpecialistActivateRequest (line 36): Class definition
- SpecialistMessageRequest (line 40): Class definition
- TeamChatRequest (line 47): Class definition

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/api/app.py
- ChatRequest (line 59): Class definition
- ChatResponse (line 73): Class definition
- TemplateRequest (line 82): Class definition
- PromptRequest (line 92): Class definition
- PromptRegistryRequest (line 99): Class definition

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/templates/system_prompts.py
- get_registry (line 20): Public function
- async_get_registry (line 31): Async function
- get_system_prompt (line 39): Public function
- async_get_system_prompt (line 62): Async function
- get_all_component_prompts (line 79): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/clients/python/rhetor_client.py
- StreamingResponse (line 19): Class definition
- CompletionResponse (line 29): Class definition
- RhetorClient (line 37): Class definition
- RhetorClient.connect (line 80): Async function
- RhetorClient.disconnect (line 111): Async function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/mcp/hermes_bridge.py
- RhetorMCPBridge (line 16): Class definition
- RhetorMCPBridge.initialize (line 31): Async function
- RhetorMCPBridge.register_default_tools (line 63): Async function
- RhetorMCPBridge.register_fastmcp_tools (line 78): Async function
- RhetorMCPBridge.register_fastmcp_tool (line 91): Async function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/mcp/dynamic_specialist_tools.py
- mcp_tool (line 21): Public function
- decorator (line 22): Public function
- list_specialist_templates (line 35): Async function, MCP tool
- create_dynamic_specialist (line 78): Async function, High complexity, MCP tool
- clone_specialist (line 199): Async function, Has side effects, High complexity, MCP tool

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/mcp/tools.py
- mcp_tool (line 21): Public function
- decorator (line 22): Public function
- get_available_models (line 39): Async function, MCP tool
- set_default_model (line 94): Async function, MCP tool
- get_model_capabilities (line 134): Async function, MCP tool

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/mcp/__init__.py
- get_all_capabilities (line 23): Public function
- get_all_tools (line 33): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/mcp/streaming_tools.py
- mcp_tool (line 21): Public function
- decorator (line 22): Public function
- streaming_tool (line 29): Public function
- send_message_to_specialist_stream (line 42): Async function, High complexity, MCP tool
- orchestrate_team_chat_stream (line 274): Async function, High complexity, MCP tool

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/mcp/capabilities.py
- LLMManagementCapability (line 12): Class definition
- LLMManagementCapability.get_supported_operations (line 20): Public function
- LLMManagementCapability.get_capability_metadata (line 32): Public function
- PromptEngineeringCapability (line 45): Class definition
- PromptEngineeringCapability.get_supported_operations (line 53): Public function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/mcp/init_integration.py
- initialize_mcp_integration (line 18): Public function
- setup_hermes_subscriptions (line 58): Async function, High complexity
- message_handler (line 78): Async function
- test_mcp_integration (line 110): Async function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/mcp/tools_integration.py
- MCPToolsIntegration (line 39): Class definition
- MCPToolsIntegration.list_ai_specialists (line 90): Async function, High complexity
- MCPToolsIntegration.activate_ai_specialist (line 172): Async function
- MCPToolsIntegration.send_message_to_specialist (line 218): Async function
- MCPToolsIntegration.orchestrate_team_chat (line 304): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/models/providers/simulated.py
- SimulatedProvider (line 16): Class definition
- SimulatedProvider.get_available_models (line 35): Public function
- SimulatedProvider.complete (line 48): Async function, High complexity
- SimulatedProvider.stream (line 116): Async function, High complexity
- SimulatedProvider.chat_complete (line 171): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/models/providers/openai.py
- OpenAIProvider (line 17): Class definition
- OpenAIProvider.get_available_models (line 62): Public function
- OpenAIProvider.complete (line 78): Async function
- OpenAIProvider.stream (line 150): Async function
- OpenAIProvider.chat_complete (line 200): Async function

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/models/providers/anthropic.py
- AnthropicProvider (line 17): Class definition
- AnthropicProvider.get_available_models (line 60): Public function
- AnthropicProvider.complete (line 77): Async function
- AnthropicProvider.stream (line 145): Async function
- AnthropicProvider.chat_complete (line 194): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/models/providers/ollama.py
- OllamaProvider (line 18): Class definition
- OllamaProvider.get_available_models (line 60): Public function
- OllamaProvider.complete (line 80): Async function
- OllamaProvider.stream (line 165): Async function, High complexity
- OllamaProvider.chat_complete (line 241): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Rhetor/rhetor/models/providers/base.py
- LLMProvider (line 13): Class definition
- LLMProvider.initialize (line 29): Async function
- LLMProvider.is_available (line 54): Public function
- LLMProvider.get_available_models (line 64): Public function
- LLMProvider.complete (line 74): Async function
