# Hermes Analysis Summary

**Generated**: 2025-06-21T17:26:05.639604

## Statistics
- Files analyzed: 129
- Functions: 651
- Classes: 103
- Landmarks identified: 652
- API endpoints: 57
- MCP tools: 12

## Patterns Found
- fastapi
- singleton
- async
- error_handling
- mcp
- websocket

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Hermes/verify_mcp_changes.py
- check_file_contains (line 10): Has side effects
- main (line 25): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/examples/llm_client_example.py
- message_analysis_example (line 28): Async function
- service_analysis_example (line 81): Async function
- chat_example (line 149): Async function
- streaming_chat_example (line 180): Async function
- handle_chunk (line 186): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/database_example.py
- generate_embedding (line 42): Public function
- vector_database_example (line 52): Async function, Has side effects
- key_value_database_example (line 114): Async function
- graph_database_example (line 197): Async function, High complexity
- main (line 311): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_engram_logging.py
- main (line 20): Has side effects

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_all_components.py
- main (line 36): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/run_registration_server.py
- main (line 22): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/registration_example.py
- register_service (line 28): Async function
- update_service_health (line 54): Async function
- discover_services (line 78): Async function
- registration_example (line 95): Async function
- service_monitoring_simulation (line 190): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/logging_example.py
- basic_logging_example (line 22): Public function
- component_based_logging_example (line 52): Public function
- structured_logging_example (line 84): Public function
- simulated_application_logging (line 138): Public function
- concurrent_logging_example (line 203): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_components/core/args.py
- parse_args (line 10): Public function
- determine_components (line 44): Public function
- determine_tekton_root (line 60): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_components/core/manager.py
- UpdateManager (line 17): Class definition
- UpdateManager.update_components (line 34): Public function
- UpdateManager.print_summary (line 93): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_components/utils/code.py
- is_already_updated (line 10): Public function
- find_import_section_end (line 23): Public function
- replace_logging_imports (line 43): Has side effects
- extract_logger_name (line 85): Public function
- replace_logger_initialization (line 114): High complexity

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_components/utils/file.py
- write_file (line 14): Has side effects
- read_file (line 34): Has side effects
- file_exists (line 52): Public function
- create_directory (line 65): Public function
- copy_file (line 83): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_components/utils/module.py
- import_module_from_file (line 14): Public function
- find_suitable_files (line 39): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_components/updaters/harmonia.py
- update_harmonia (line 18): High complexity

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_components/updaters/engram.py
- update_engram (line 15): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_components/updaters/ergon.py
- update_ergon (line 18): High complexity

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_components/updaters/hermes.py
- update_hermes_itself (line 13): High complexity

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_components/updaters/athena.py
- update_athena (line 18): High complexity

### /Users/cskoons/projects/github/Tekton/Hermes/scripts/update_components/templates/logging_imports.py
- get_logger_init_replacement (line 26): Public function
- get_readme_content (line 77): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/a2a_service.py
- A2AService (line 48): Class definition
- A2AService.initialize (line 121): Async function
- A2AService.agent_forward (line 181): Async function
- A2AService.channel_subscribe (line 210): Async function
- A2AService.channel_unsubscribe (line 231): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/mcp_service.py
- MCPService (line 62): Class definition
- MCPService.initialize (line 111): Async function, High complexity
- MCPService.register_tool (line 202): Async function
- MCPService.unregister_tool (line 270): Async function
- MCPService.register_processor (line 306): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/message_bus.py
- MessageBus (line 18): Class definition
- MessageBus.connect (line 54): Public function
- MessageBus.publish (line 65): Public function
- MessageBus.subscribe (line 116): Public function
- MessageBus.unsubscribe (line 140): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/a2a_service_backup.py
- A2AService (line 33): Class definition
- A2AService.initialize (line 84): Async function
- A2AService.agent_forward (line 122): Async function
- A2AService.channel_subscribe (line 139): Async function
- A2AService.channel_unsubscribe (line 151): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/__init__.py
- DatabaseAdapter (line 32): Class definition
- VectorDatabaseAdapter (line 36): Class definition
- GraphDatabaseAdapter (line 40): Class definition
- KeyValueDatabaseAdapter (line 44): Class definition
- DocumentDatabaseAdapter (line 48): Class definition

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/hermes_component.py
- HermesComponent (line 17): Class definition
- HermesComponent.register_hermes_components (line 124): Async function
- HermesComponent.start_database_mcp_server (line 214): Async function
- HermesComponent.stop_database_mcp_server (line 269): Public function
- HermesComponent.get_capabilities (line 312): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/llm_client.py
- LLMClient (line 27): Class definition
- LLMClient.get_available_providers (line 229): Async function, High complexity
- LLMClient.get_current_provider_and_model (line 293): Public function
- LLMClient.set_provider_and_model (line 302): Public function
- LLMClient.generate (line 318): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/vector_engine.py
- VectorEngine (line 16): Class definition
- VectorEngine.connect (line 51): Public function
- VectorEngine.create_embedding (line 96): Public function
- VectorEngine.store (line 110): Public function
- VectorEngine.search (line 129): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/llm_adapter.py
- LLMAdapter (line 28): Class definition
- LLMAdapter.get_available_providers (line 59): Async function
- LLMAdapter.get_current_provider_and_model (line 69): Public function
- LLMAdapter.set_provider_and_model (line 78): Public function
- LLMAdapter.analyze_message (line 92): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/service_discovery.py
- ServiceRegistry (line 18): Class definition
- ServiceRegistry.start (line 51): Public function
- ServiceRegistry.register (line 62): Public function
- ServiceRegistry.unregister (line 104): Public function
- ServiceRegistry.get_service (line 126): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/utils/registration_helper.py
- ComponentRegistration (line 20): Class definition
- ComponentRegistration.register (line 69): Async function
- ComponentRegistration.unregister (line 78): Async function
- ComponentRegistration.publish_message (line 87): Public function
- ComponentRegistration.subscribe_to_topic (line 108): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/utils/logging_helper.py
- setup_logging (line 25): Public function
- get_component_logger (line 67): Public function
- intercept_python_logging (line 83): High complexity
- TektonLoggingHandler (line 110): Class definition
- TektonLoggingHandler.emit (line 111): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/utils/database_helper.py
- get_database_manager (line 33): Async function
- get_vector_db (line 48): Async function
- get_graph_db (line 68): Async function
- get_key_value_db (line 88): Async function
- get_document_db (line 108): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/llm_endpoints.py
- ChatMessage (line 42): Class definition
- ChatRequest (line 48): Class definition
- ChatResponse (line 56): Class definition
- AnalyzeMessageRequest (line 63): Class definition
- AnalyzeServiceRequest (line 68): Class definition

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/database_client.py
- DatabaseClient (line 27): Class definition
- DatabaseClient.vector_store (line 77): Async function
- DatabaseClient.vector_search (line 81): Async function
- DatabaseClient.vector_delete (line 85): Async function, Has side effects
- DatabaseClient.kv_set (line 91): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/mcp_stdio_bridge.py
- HermesMCPBridge (line 27): Class definition
- HermesMCPBridge.start (line 34): Async function
- HermesMCPBridge.stop (line 39): Async function
- HermesMCPBridge.run (line 44): Async function, Has side effects
- HermesMCPBridge.handle_request (line 80): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/client.py
- HermesClient (line 27): Class definition
- HermesClient.register (line 106): Async function
- HermesClient.unregister (line 127): Async function
- HermesClient.publish_message (line 148): Public function
- HermesClient.subscribe_to_topic (line 178): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/mcp_endpoints.py
- ContentItem (line 29): Class definition
- MCPMessage (line 37): Class definition
- ToolSpec (line 49): Class definition
- ToolRegistrationResponse (line 61): Class definition
- ToolExecutionRequest (line 68): Class definition

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/mcp_auto_approve.py
- AutoApprovedHermesBridge (line 28): Class definition
- AutoApprovedHermesBridge.start (line 37): Async function
- AutoApprovedHermesBridge.stop (line 42): Async function
- AutoApprovedHermesBridge.run (line 47): Async function, Has side effects
- AutoApprovedHermesBridge.handle_request (line 77): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/database_mcp_server.py
- startup_event (line 55): Async function
- shutdown_event (line 79): Async function
- root (line 88): Async function
- health (line 97): Async function
- get_manifest (line 105): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/app.py
- startup_callback (line 52): Async function
- ready (line 99): Async function
- discovery (line 111): Async function
- root (line 149): Async function
- health (line 155): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/a2a_endpoints.py
- JSONRPCRequestModel (line 50): Class definition
- JSONRPCResponseModel (line 58): Class definition
- get_a2a_service (line 66): Async function
- get_a2a_components (line 74): Async function
- handle_jsonrpc (line 92): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/endpoints.py
- get_registration_manager (line 59): Public function
- ComponentRegistrationRequest (line 65): Class definition
- ComponentRegistrationResponse (line 77): Class definition
- HeartbeatRequest (line 84): Class definition
- HeartbeatResponse (line 89): Class definition

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/singleton_fix.py
- get_shared_registration_manager (line 18): Public function
- get_shared_service_registry (line 40): Public function
- get_shared_message_bus (line 46): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/mcp_handlers.py
- handle_vector_request (line 18): Async function, Has side effects, High complexity
- handle_key_value_request (line 91): Async function, Has side effects, High complexity
- handle_graph_request (line 160): Async function, High complexity
- handle_document_request (line 243): Async function, Has side effects, High complexity
- handle_cache_request (line 324): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/mcp_adapter.py
- DatabaseMCPAdapter (line 36): Class definition
- DatabaseMCPAdapter.get_manifest (line 56): Async function
- DatabaseMCPAdapter.handle_request (line 70): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/factory.py
- DatabaseFactory (line 27): Class definition
- DatabaseFactory.create_adapter (line 36): High complexity

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/mcp_capabilities.py
- generate_capabilities (line 11): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/database_types.py
- DatabaseType (line 13): Class definition
- DatabaseType.from_string (line 24): Public function
- DatabaseBackend (line 32): Class definition
- DatabaseBackend.from_string (line 63): Public function
- DatabaseBackend.for_type (line 71): High complexity

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/manager.py
- DatabaseManager (line 31): Class definition
- DatabaseManager.get_connection (line 70): Async function, Has side effects, High complexity
- DatabaseManager.get_vector_db (line 148): Async function
- DatabaseManager.get_graph_db (line 175): Async function
- DatabaseManager.get_key_value_db (line 202): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/registration/client.py
- RegistrationClient (line 19): Class definition
- RegistrationClient.register (line 80): Async function
- RegistrationClient.unregister (line 126): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/registration/handlers.py
- handle_registration_request (line 17): Public function
- handle_revocation_request (line 70): Public function
- handle_heartbeat (line 104): Public function
- handle_registration_response (line 126): Public function
- heartbeat_loop (line 148): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/registration/tokens.py
- RegistrationToken (line 18): Class definition
- RegistrationToken.generate (line 41): Public function
- RegistrationToken.validate (line 74): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/registration/types.py
- TokenData (line 11): Class definition
- TokenPayload (line 18): Class definition
- ComponentData (line 23): Class definition
- HeartbeatData (line 33): Class definition
- RegistrationResponse (line 40): Class definition

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/registration/utils.py
- generate_component_id (line 15): Public function
- is_token_valid (line 30): Public function
- format_component_info (line 46): Public function
- calculate_token_lifetime (line 66): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/registration/manager.py
- RegistrationManager (line 24): Class definition
- RegistrationManager.register_component (line 81): Public function
- RegistrationManager.unregister_component (line 164): Public function
- RegistrationManager.validate_component (line 211): Public function
- RegistrationManager.send_heartbeat (line 239): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/registration/client_api.py
- RegistrationClientAPI (line 18): Class definition
- RegistrationClientAPI.register (line 69): Public function
- RegistrationClientAPI.unregister (line 120): Public function
- RegistrationClientAPI.find_services (line 158): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/mcp/hermes_self_bridge.py
- HermesSelfBridge (line 16): Class definition
- HermesSelfBridge.initialize (line 33): Async function
- HermesSelfBridge.register_default_tools (line 69): Async function, Has side effects
- HermesSelfBridge.shutdown (line 136): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/mcp/tools.py
- mcp_tool (line 22): Public function
- decorator (line 23): Public function
- mcp_capability (line 27): Public function
- decorator (line 28): Public function
- get_component_status (line 49): Async function, MCP tool

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/mcp/__init__.py
- mcp_tool (line 40): Public function
- decorator (line 41): Public function
- mcp_capability (line 45): Public function
- decorator (line 46): Public function
- mcp_processor (line 50): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/mcp/tool_executor.py
- ToolExecutor (line 15): Class definition
- ToolExecutor.register_local_handler (line 24): Public function
- ToolExecutor.set_dependencies (line 29): Public function
- ToolExecutor.execute_tool (line 38): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/mcp/adapters.py
- adapt_legacy_service (line 26): Async function
- LegacyMCPProcessorAdapter (line 78): Class definition
- LegacyMCPProcessorAdapter.process (line 97): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/adapters/key_value.py
- KeyValueDatabaseAdapter (line 15): Class definition
- KeyValueDatabaseAdapter.db_type (line 24): Public function
- KeyValueDatabaseAdapter.set (line 29): Async function
- KeyValueDatabaseAdapter.get (line 47): Async function
- KeyValueDatabaseAdapter.delete (line 60): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/adapters/vector.py
- VectorDatabaseAdapter (line 15): Class definition
- VectorDatabaseAdapter.db_type (line 24): Public function
- VectorDatabaseAdapter.store (line 29): Async function
- VectorDatabaseAdapter.search (line 49): Async function
- VectorDatabaseAdapter.delete (line 67): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/adapters/graph.py
- GraphDatabaseAdapter (line 15): Class definition
- GraphDatabaseAdapter.db_type (line 24): Public function
- GraphDatabaseAdapter.add_node (line 29): Async function
- GraphDatabaseAdapter.add_relationship (line 47): Async function
- GraphDatabaseAdapter.get_node (line 67): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/adapters/cache.py
- CacheDatabaseAdapter (line 15): Class definition
- CacheDatabaseAdapter.db_type (line 24): Public function
- CacheDatabaseAdapter.set (line 29): Async function
- CacheDatabaseAdapter.get (line 47): Async function
- CacheDatabaseAdapter.delete (line 60): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/adapters/relational.py
- RelationalDatabaseAdapter (line 15): Class definition
- RelationalDatabaseAdapter.db_type (line 24): Public function
- RelationalDatabaseAdapter.execute (line 29): Async function
- RelationalDatabaseAdapter.execute_batch (line 45): Async function
- RelationalDatabaseAdapter.begin_transaction (line 61): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/adapters/document.py
- DocumentDatabaseAdapter (line 15): Class definition
- DocumentDatabaseAdapter.db_type (line 24): Public function
- DocumentDatabaseAdapter.insert (line 29): Async function
- DocumentDatabaseAdapter.find (line 47): Async function
- DocumentDatabaseAdapter.find_one (line 69): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/database/adapters/base.py
- DatabaseAdapter (line 14): Class definition
- DatabaseAdapter.connect (line 37): Async function
- DatabaseAdapter.disconnect (line 47): Async function
- DatabaseAdapter.is_connected (line 57): Async function
- DatabaseAdapter.db_type (line 68): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/logging/interface/logger.py
- Logger (line 21): Class definition
- Logger.fatal (line 95): Public function
- Logger.error (line 123): Public function
- Logger.warn (line 151): Public function
- Logger.info (line 176): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/logging/management/manager.py
- LogManager (line 19): Class definition
- LogManager.log (line 66): Public function
- LogManager.query (line 99): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/logging/utils/helpers.py
- init_logging (line 19): Public function
- get_logger (line 51): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/logging/storage/file_storage.py
- LogStorage (line 23): Class definition
- LogStorage.store (line 50): Has side effects
- LogStorage.query (line 92): Has side effects, High complexity

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/logging/base/entry.py
- LogEntry (line 18): Class definition
- LogEntry.to_dict (line 47): Public function
- LogEntry.to_json (line 54): Public function
- LogEntry.from_dict (line 59): Public function
- LogEntry.from_json (line 69): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/core/logging/base/levels.py
- LogLevel (line 11): Class definition
- LogLevel.from_string (line 23): Public function
- LogLevel.to_python_level (line 35): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/adapters/graph/neo4j_adapter.py
- Neo4jGraphAdapter (line 24): Class definition
- Neo4jGraphAdapter.backend (line 51): Public function
- Neo4jGraphAdapter.connect (line 55): Async function
- Neo4jGraphAdapter.disconnect (line 80): Async function
- Neo4jGraphAdapter.is_connected (line 96): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/adapters/key_value/redis_adapter.py
- RedisKeyValueAdapter (line 25): Class definition
- RedisKeyValueAdapter.backend (line 61): Public function
- RedisKeyValueAdapter.connect (line 65): Async function
- RedisKeyValueAdapter.disconnect (line 95): Async function
- RedisKeyValueAdapter.is_connected (line 116): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/adapters/vector/fallback_adapter.py
- FallbackVectorAdapter (line 25): Class definition
- FallbackVectorAdapter.backend (line 66): Public function
- FallbackVectorAdapter.connect (line 70): Async function, Has side effects
- FallbackVectorAdapter.disconnect (line 110): Async function
- FallbackVectorAdapter.is_connected (line 136): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/adapters/vector/faiss/index.py
- create_index (line 16): Async function, High complexity
- add_to_index (line 122): Async function
- remove_from_index (line 169): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/adapters/vector/faiss/adapter.py
- FAISSVectorAdapter (line 32): Class definition
- FAISSVectorAdapter.backend (line 90): Public function
- FAISSVectorAdapter.connect (line 94): Async function, Has side effects
- FAISSVectorAdapter.disconnect (line 150): Async function
- FAISSVectorAdapter.is_connected (line 177): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/adapters/vector/faiss/operations.py
- store_vector (line 20): Async function
- search_vectors (line 80): Async function, High complexity
- delete_vectors (line 161): Async function, High complexity
- get_vector (line 255): Async function
- list_vectors (line 289): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/adapters/vector/faiss/utils.py
- matches_filter (line 10): High complexity
- rebuild_id_mappings (line 49): Public function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/database/document_client.py
- DocumentDatabaseClient (line 11): Class definition
- DocumentDatabaseClient.insert (line 28): Async function
- DocumentDatabaseClient.find (line 60): Async function
- DocumentDatabaseClient.update (line 95): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/database/models.py
- VectorStoreRequest (line 15): Class definition
- VectorSearchRequest (line 22): Class definition
- VectorDeleteRequest (line 29): Class definition
- KeyValueSetRequest (line 36): Class definition
- KeyValueDeleteRequest (line 42): Class definition

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/database/vector_client.py
- VectorDatabaseClient (line 11): Class definition
- VectorDatabaseClient.store (line 27): Async function
- VectorDatabaseClient.search (line 64): Async function
- VectorDatabaseClient.delete (line 100): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/database/client_base.py
- BaseRequest (line 16): Class definition
- BaseRequest.mcp_invoke (line 40): Async function
- BaseRequest.api_request (line 71): Async function
- BaseRequest.execute_request (line 111): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/database/relation_client.py
- RelationalDatabaseClient (line 11): Class definition
- RelationalDatabaseClient.execute (line 27): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/database/graph_client.py
- GraphDatabaseClient (line 11): Class definition
- GraphDatabaseClient.add_node (line 28): Async function
- GraphDatabaseClient.add_relationship (line 63): Async function
- GraphDatabaseClient.query (line 102): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/database/cache_client.py
- CacheDatabaseClient (line 11): Class definition
- CacheDatabaseClient.set (line 28): Async function
- CacheDatabaseClient.get (line 64): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/database/key_value_client.py
- KeyValueDatabaseClient (line 11): Class definition
- KeyValueDatabaseClient.set (line 27): Async function
- KeyValueDatabaseClient.get (line 64): Async function
- KeyValueDatabaseClient.delete (line 96): Async function

### /Users/cskoons/projects/github/Tekton/Hermes/hermes/api/database/routes.py
- get_database_manager (line 37): Async function
- vector_store (line 52): Async function
- vector_search (line 80): Async function
- vector_delete (line 108): Async function, Has side effects
- kv_set (line 134): Async function
