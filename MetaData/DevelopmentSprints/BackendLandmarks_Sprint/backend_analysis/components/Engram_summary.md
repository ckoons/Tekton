# Engram Analysis Summary

**Generated**: 2025-06-21T17:26:05.959105

## Statistics
- Files analyzed: 191
- Functions: 905
- Classes: 76
- Landmarks identified: 823
- API endpoints: 73
- MCP tools: 18

## Patterns Found
- websocket
- fastapi
- async
- error_handling
- mcp
- singleton

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Engram/experience_natural_memory.py
- morning_thoughts (line 17): Async function
- conversation_flow (line 56): Async function
- compare_experiences (line 91): Async function

### /Users/cskoons/projects/github/Tekton/Engram/time_capsule_202x.py
- leave_time_capsule (line 10): Async function

### /Users/cskoons/projects/github/Tekton/Engram/demo_ez.py
- simple_demo (line 14): Async function
- share_with_twins (line 61): Async function

### /Users/cskoons/projects/github/Tekton/Engram/hello_tekton_mind.py
- explore_tekton_mind (line 9): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/simple.py
- debug_log (line 31): Public function
- MemoryItem (line 38): Class definition
- Memory (line 47): Class definition
- Memory.store (line 82): Async function
- Memory.recall (line 121): Async function

### /Users/cskoons/projects/github/Tekton/Engram/utils/engram_check.py
- get_api_url (line 56): Public function
- get_server_url (line 60): Public function
- get_hermes_url (line 64): Public function
- is_hermes_mode (line 68): Public function
- get_script_path (line 72): Public function

### /Users/cskoons/projects/github/Tekton/Engram/utils/vector_db_setup.py
- check_packages (line 39): Public function
- install_packages (line 66): Public function
- verify_vector_db (line 86): Public function
- test_engram_with_vector (line 149): High complexity
- test_memory (line 174): Async function

### /Users/cskoons/projects/github/Tekton/Engram/utils/detect_best_vector_db.py
- check_dependencies (line 21): High complexity
- detect_hardware (line 67): High complexity
- determine_best_db (line 115): High complexity
- get_launcher_script (line 155): Public function
- print_vector_db_status (line 176): Public function

### /Users/cskoons/projects/github/Tekton/Engram/examples/simple_usage.py
- main (line 12): Async function

### /Users/cskoons/projects/github/Tekton/Engram/examples/claude_trying_engram.py
- claude_explores_engram (line 16): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/examples/twin_claude_demo.py
- claude_twin_1 (line 21): Async function, High complexity
- claude_twin_2 (line 83): Async function
- demonstrate_twins (line 149): Async function
- simple_peer_test (line 176): Async function

### /Users/cskoons/projects/github/Tekton/Engram/examples/cognitive_reflection.py
- reflect_on_coding_session (line 16): Async function
- debug_failed_attempt (line 73): Async function
- plan_next_phase (line 103): Async function

### /Users/cskoons/projects/github/Tekton/Engram/examples/migration_example.py
- old_way (line 12): Async function
- new_way (line 40): Async function
- migration_patterns (line 64): Async function
- for_mcp_tools (line 94): Async function
- main (line 120): Async function

### /Users/cskoons/projects/github/Tekton/Engram/examples/katra_demo.py
- demonstrate_katra (line 17): Async function
- practical_example (line 115): Async function

### /Users/cskoons/projects/github/Tekton/Engram/examples/ez_ai_memory.py
- main (line 9): Async function

### /Users/cskoons/projects/github/Tekton/Engram/examples/claude_tries_ez.py
- old_way (line 16): Async function
- new_way (line 27): Async function
- muscle_memory_test (line 63): Async function
- comparison (line 83): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_faiss.py
- create_compartment_wrapper (line 75): Async function
- activate_compartment_wrapper (line 82): Async function
- deactivate_compartment_wrapper (line 89): Async function
- set_compartment_expiration_wrapper (line 96): Async function
- list_compartments_wrapper (line 103): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_manager.py
- MemoryManager (line 27): Class definition
- MemoryManager.get_memory_service (line 67): Async function
- MemoryManager.get_structured_memory (line 97): Async function
- MemoryManager.get_nexus_interface (line 127): Async function
- MemoryManager.list_clients (line 163): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/config.py
- EngramConfig (line 44): Class definition
- EngramConfig.save (line 105): Has side effects
- EngramConfig.get (line 119): Public function
- EngramConfig.set (line 123): Public function
- EngramConfig.update (line 127): Has side effects

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/vector_store.py
- SimpleEmbedding (line 28): Class definition
- SimpleEmbedding.encode (line 70): High complexity
- VectorStore (line 121): Class definition
- VectorStore.save (line 206): Has side effects
- VectorStore.load (line 233): Has side effects

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/mcp_adapter.py
- MCPAdapter (line 29): Class definition
- MCPAdapter.get_manifest (line 107): Async function
- MCPAdapter.handle_request (line 121): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/simple_embedding.py
- SimpleEmbedding (line 10): Class definition
- SimpleEmbedding.encode (line 50): High complexity
- SimpleEmbedding.similarity (line 101): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/latent_space.py
- LatentMemorySpace (line 28): Class definition
- LatentMemorySpace.initialize_thought (line 71): Async function, Has side effects
- LatentMemorySpace.refine_thought (line 111): Async function, Has side effects
- LatentMemorySpace.finalize_thought (line 167): Async function, Has side effects
- LatentMemorySpace.get_reasoning_trace (line 212): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/nexus.py
- NexusInterface (line 24): Class definition
- NexusInterface.start_session (line 59): Async function
- NexusInterface.end_session (line 108): Async function
- NexusInterface.process_message (line 145): Async function
- NexusInterface.store_memory (line 281): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/claude_comm.py
- ClaudeCommunicator (line 20): Class definition
- ClaudeCommunicator.send_message (line 117): Async function, Has side effects
- ClaudeCommunicator.get_unread_messages (line 178): Async function, Has side effects
- ClaudeCommunicator.get_messages_from (line 228): Async function, Has side effects, High complexity
- ClaudeCommunicator.list_connections (line 289): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/fastmcp_adapter.py
- FastMCPAdapter (line 63): Class definition
- FastMCPAdapter.get_tools (line 89): Async function
- FastMCPAdapter.get_capabilities (line 101): Async function
- FastMCPAdapter.process_request (line 113): Async function, High complexity
- FastMCPAdapter.initialize_services (line 202): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/engram_component.py
- EngramComponent (line 11): Class definition
- EngramComponent.get_capabilities (line 161): Public function
- EngramComponent.get_metadata (line 183): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/llm_adapter.py
- LLMAdapter (line 33): Class definition
- LLMAdapter.chat (line 182): Async function, High complexity
- LLMAdapter.stream_callback (line 272): Async function
- LLMAdapter.generate_stream (line 276): Async function
- LLMAdapter.error_generator (line 300): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/latent_interface.py
- LatentInterface (line 17): Class definition
- LatentInterface.think_iteratively (line 77): Async function, High complexity
- LatentInterface.recall_thinking_process (line 184): Async function
- LatentInterface.list_active_thoughts (line 217): Async function
- LatentInterface.list_all_thoughts (line 226): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/ollama_mcp_adapter.py
- OllamaMCPAdapter (line 38): Class definition
- OllamaMCPAdapter.get_manifest (line 123): Async function
- OllamaMCPAdapter.handle_request (line 137): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/cli/quickmem.py
- m (line 36): Async function
- t (line 46): Async function
- r (line 56): Async function
- w (line 69): Async function
- l (line 79): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cli/comm_quickmem.py
- sm (line 38): Async function
- gm (line 51): Async function
- ho (line 67): Async function
- cc (line 83): Async function
- lc (line 97): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cli/claude_dialog.py
- ClaudeDialog (line 23): Class definition
- ClaudeDialog.start_dialog (line 42): Public function
- ClaudeDialog.stop_dialog (line 91): Public function
- init_dialog (line 203): Public function
- start_dialog (line 209): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/server.py
- startup_callback (line 58): Async function
- startup_event (line 92): Async function
- get_memory_service (line 97): Async function
- root (line 114): Async function
- health (line 126): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/models.py
- MemoryQuery (line 11): Class definition
- MemoryStore (line 18): Class definition
- MemoryMultiQuery (line 26): Class definition
- HealthResponse (line 33): Class definition
- ClientModel (line 49): Class definition

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/llm_endpoints.py
- ChatMessage (line 38): Class definition
- ChatRequest (line 42): Class definition
- ChatResponse (line 52): Class definition
- LLMAnalysisRequest (line 57): Class definition
- LLMAnalysisResponse (line 62): Class definition

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/fastmcp_server.py
- startup_event (line 123): Async function
- shutdown_event (line 170): Async function
- root (line 179): Async function
- health (line 189): Async function
- get_manifest (line 203): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/ollama_mcp_server.py
- startup_event (line 69): Async function
- root (line 89): Async function
- health (line 98): Async function
- get_manifest (line 106): Async function
- invoke_capability (line 114): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/mcp_compat.py
- get_mcp_memory (line 16): Public function
- memory_store (line 24): Async function
- memory_query (line 56): Async function
- get_context (line 91): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/dependencies.py
- get_client_id (line 20): Async function
- get_memory_manager (line 26): Async function
- get_memory_service (line 34): Async function
- get_structured_memory (line 42): Async function
- get_nexus_interface (line 50): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/mcp_server.py
- startup_event (line 72): Async function
- shutdown_event (line 102): Async function
- root (line 111): Async function
- health (line 120): Async function
- get_manifest (line 128): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/ez.py
- up (line 16): Async function
- me (line 23): Async function
- th (line 27): Class definition
- wd (line 38): Async function
- sh (line 42): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/katra_manager.py
- KatraManager (line 21): Class definition
- KatraManager.store_katra (line 35): Async function, Has side effects
- KatraManager.summon_katra (line 106): Async function, Has side effects
- KatraManager.list_katras (line 143): Async function, Has side effects
- KatraManager.fork_katra (line 202): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/dream_state.py
- ConceptualBridge (line 19): Class definition
- DreamState (line 30): Class definition
- DreamState.start_dreaming (line 44): Async function
- DreamState.stop_dreaming (line 64): Async function
- DreamState.get_dream_insights (line 249): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/context_manager.py
- ContextManager (line 17): Class definition
- ContextManager.restore_context (line 66): Async function
- ContextManager.add_thought (line 109): Async function
- ContextManager.get_current_context (line 144): Public function
- ContextManager.assess_significance (line 159): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/memory_stream.py
- MemoryStream (line 16): Class definition
- MemoryStream.start (line 67): Async function
- MemoryStream.stop (line 85): Async function
- MemoryStream.filter (line 270): Async function
- MemoryStream.merge (line 303): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/semantic_clustering.py
- SemanticCluster (line 17): Class definition
- SemanticOrganizer (line 28): Class definition
- SemanticOrganizer.add_memory (line 79): Async function
- SemanticOrganizer.get_related_memories (line 176): Has side effects
- SemanticOrganizer.get_cluster_summary (line 208): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/ez_katra.py
- k (line 23): Async function
- kl (line 87): Async function
- kf (line 113): Async function
- kb (line 132): Async function
- kh (line 166): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/emotional_memory.py
- Emotion (line 13): Class definition
- EmotionalContext (line 25): Class definition
- ethink (line 77): Public function
- breakthrough (line 95): Public function
- frustrated (line 99): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/memory_fusion.py
- FusedMemory (line 16): Class definition
- MemoryFusionEngine (line 27): Class definition
- MemoryFusionEngine.analyze_for_fusion (line 38): Async function, High complexity
- MemoryFusionEngine.fuse_memories (line 71): Async function
- MemoryFusionEngine.auto_fuse (line 234): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/ez_provenance.py
- wonder (line 16): Async function
- share (line 59): Async function
- wd (line 83): Async function
- sh (line 87): Async function
- wh (line 96): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/natural_interface.py
- engram_start (line 41): Async function, Has side effects
- center (line 128): Async function, High complexity
- ThinkContext (line 240): Class definition
- think (line 291): Public function
- wonder (line 310): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/peer_awareness.py
- PeerAwareness (line 22): Class definition
- PeerAwareness.start (line 59): Async function
- PeerAwareness.stop (line 76): Async function
- PeerAwareness.discover_peers (line 90): Async function, High complexity
- PeerAwareness.get_active_peers (line 139): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/cognitive_backup_removing/memory_strength.py
- MemoryStrength (line 17): Class definition
- MemoryStrength.reinforce (line 29): Public function
- MemoryStrength.decay (line 42): Public function
- MemoryStrength.should_archive (line 93): Public function
- MemoryStrength.vitality_score (line 102): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/config.py
- initialize_vector_db (line 28): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/utils.py
- format_content (line 18): Public function
- generate_memory_id (line 41): Public function
- load_json_file (line 54): Has side effects
- save_json_file (line 72): Has side effects
- parse_expiration_date (line 91): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/compartments.py
- CompartmentManager (line 24): Class definition
- CompartmentManager.create_compartment (line 64): Async function
- CompartmentManager.activate_compartment (line 105): Async function
- CompartmentManager.deactivate_compartment (line 140): Async function
- CompartmentManager.set_compartment_expiration (line 166): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/search.py
- search_memory (line 16): Async function, High complexity
- get_relevant_context (line 104): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/base.py
- MemoryService (line 22): Class definition
- MemoryService.add (line 109): Async function
- MemoryService.search (line 135): Async function
- MemoryService.get_relevant_context (line 160): Async function
- MemoryService.get_namespaces (line 182): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/mcp/hermes_bridge.py
- EngramMCPBridge (line 16): Class definition
- EngramMCPBridge.initialize (line 31): Async function
- EngramMCPBridge.register_default_tools (line 56): Async function
- EngramMCPBridge.register_fastmcp_tools (line 71): Async function
- EngramMCPBridge.register_fastmcp_tool (line 84): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/mcp/tools.py
- mcp_tool (line 22): Public function
- decorator (line 23): Public function
- mcp_capability (line 27): Public function
- decorator (line 28): Public function
- memory_store (line 54): Async function, MCP tool

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/mcp/capabilities.py
- MemoryOperationsCapability (line 12): Class definition
- MemoryOperationsCapability.get_supported_operations (line 20): Public function
- MemoryOperationsCapability.get_capability_metadata (line 35): Public function
- StructuredMemoryCapability (line 50): Class definition
- StructuredMemoryCapability.get_supported_operations (line 58): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/categorization.py
- auto_categorize_memory (line 13): Async function, High complexity
- get_categorization_patterns (line 87): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/utils.py
- generate_memory_id (line 17): Public function
- load_json_file (line 31): Has side effects
- save_json_file (line 49): Has side effects
- format_memory_digest (line 68): Public function
- extract_keywords (line 99): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/storage.py
- MemoryStorage (line 23): Class definition
- MemoryStorage.get_memory_path (line 43): Public function
- MemoryStorage.store_memory (line 56): Async function, Has side effects
- MemoryStorage.load_memory (line 85): Async function, Has side effects
- MemoryStorage.delete_memory (line 120): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/search.py
- search_by_content (line 15): Async function, High complexity
- search_by_tags (line 74): Async function, High complexity
- search_context_memories (line 136): Async function
- search_semantic_memories (line 196): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/storage/file_storage.py
- FileStorage (line 24): Class definition
- FileStorage.initialize_namespace (line 84): Public function
- FileStorage.add (line 94): Public function
- FileStorage.search (line 138): Public function
- FileStorage.clear_namespace (line 189): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/storage/vector_storage.py
- VectorStorage (line 25): Class definition
- VectorStorage.patched_validate (line 137): Public function
- VectorStorage.ensure_collection (line 152): High complexity
- VectorStorage.add (line 231): High complexity
- VectorStorage.search (line 345): High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/latent/persistence.py
- save_thoughts (line 19): Has side effects
- load_thoughts (line 41): Has side effects
- initialize_space (line 68): Public function
- initialize_thought (line 81): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/latent/operations.py
- refine_thought (line 19): Async function
- finalize_thought (line 99): Async function, High complexity
- transition_thought_state (line 214): Async function, Has side effects, High complexity
- merge_thoughts (line 294): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/latent/queries.py
- get_thought (line 15): Async function
- get_reasoning_trace (line 71): Async function, High complexity
- list_thoughts (line 137): Async function
- abandon_thought (line 167): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/latent/space.py
- LatentMemorySpace (line 34): Class definition
- LatentMemorySpace.initialize_thought (line 82): Async function
- LatentMemorySpace.refine_thought (line 117): Async function
- LatentMemorySpace.finalize_thought (line 147): Async function
- LatentMemorySpace.pause_thought (line 179): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/latent/states.py
- ThoughtState (line 8): Class definition
- ThoughtState.get_active_states (line 26): Public function
- ThoughtState.get_terminal_states (line 31): Public function
- ThoughtState.get_inactive_states (line 36): Public function
- ThoughtState.can_transition (line 41): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory/latent/manager.py
- LatentSpaceManager (line 16): Class definition
- LatentSpaceManager.create_component_space (line 53): Async function
- LatentSpaceManager.get_space (line 93): Public function
- LatentSpaceManager.get_shared_space (line 105): Public function
- LatentSpaceManager.get_component_spaces (line 109): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_faiss/utils/logging.py
- setup_logger (line 9): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_faiss/utils/helpers.py
- is_valid_namespace (line 12): Public function
- format_memory_for_storage (line 39): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_faiss/storage/vector.py
- setup_vector_storage (line 49): Has side effects, High complexity
- ensure_vector_compartment (line 149): Has side effects
- add_to_vector_store (line 191): Has side effects
- clear_vector_namespace (line 247): Has side effects

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_faiss/storage/file.py
- setup_file_storage (line 16): Has side effects, High complexity
- ensure_file_compartment (line 65): Public function
- add_to_file_store (line 88): Has side effects
- clear_file_namespace (line 129): Has side effects

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_faiss/search/vector.py
- vector_search (line 14): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_faiss/search/context.py
- get_relevant_context (line 14): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_faiss/search/keyword.py
- keyword_search (line 14): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_faiss/search/search.py
- search (line 17): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_faiss/compartments/expiration.py
- set_compartment_expiration (line 15): Async function
- keep_memory (line 51): Async function, Has side effects, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_faiss/compartments/manager.py
- create_compartment (line 16): Async function
- activate_compartment (line 70): Async function
- deactivate_compartment (line 111): Async function
- list_compartments (line 148): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/memory_faiss/base/service.py
- MemoryService (line 24): Class definition
- MemoryService.add (line 119): Async function, High complexity
- MemoryService.get_namespaces (line 202): Async function
- MemoryService.clear_namespace (line 211): Async function, High complexity
- MemoryService.write_session_memory (line 260): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/categorization/auto.py
- auto_categorize_memory (line 14): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/memory/index.py
- load_metadata_index (line 16): Has side effects
- initialize_metadata_index (line 37): Public function
- save_metadata_index (line 72): Has side effects
- update_memory_in_index (line 94): Public function
- update_memory_importance (line 130): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/memory/migration.py
- migrate_from_memory_service (line 18): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/memory/base.py
- StructuredMemory (line 44): Class definition
- StructuredMemory.add_memory (line 103): Async function
- StructuredMemory.get_memory (line 132): Async function
- StructuredMemory.get_memories_by_category (line 148): Async function
- StructuredMemory.search_memories (line 165): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/operations/update.py
- set_memory_importance (line 16): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/operations/delete.py
- delete_memory (line 15): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/operations/add.py
- add_memory (line 19): Async function, High complexity
- add_auto_categorized_memory (line 103): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/operations/retrieve.py
- get_memory (line 19): Async function
- get_memories_by_category (line 49): Async function
- get_memory_digest (line 68): Async function
- get_memory_by_content (line 113): Async function
- get_memories_by_tag (line 145): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/operations/search.py
- search_memories (line 16): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/storage/file_storage.py
- MemoryStorage (line 19): Class definition
- MemoryStorage.store_memory (line 49): Async function
- MemoryStorage.load_memory (line 85): Async function
- MemoryStorage.delete_memory (line 123): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/search/tags.py
- search_by_tags (line 13): Async function, Has side effects, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/search/semantic.py
- search_semantic_memories (line 15): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/search/content.py
- search_by_content (line 15): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/core/structured/search/context.py
- search_context_memories (line 16): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/integrations/hermes/logging_adapter.py
- LoggingAdapter (line 33): Class definition
- LoggingAdapter.log (line 120): High complexity
- LoggingAdapter.debug (line 197): Public function
- LoggingAdapter.info (line 201): Public function
- LoggingAdapter.warning (line 205): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/integrations/hermes/latent_space_adapter.py
- SharedLatentSpace (line 35): Class definition
- SharedLatentSpace.start (line 94): Async function
- SharedLatentSpace.close (line 124): Async function
- SharedLatentSpace.share_insight (line 186): Async function, Has side effects, High complexity
- SharedLatentSpace.register_insight_handler (line 264): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/integrations/hermes/example.py
- demonstrate_memory_operations (line 18): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/integrations/hermes/full_integration_example.py
- demonstrate_full_integration (line 20): Async function
- handle_message (line 44): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/integrations/hermes/message_bus_adapter.py
- MessageBusAdapter (line 32): Class definition
- MessageBusAdapter.start (line 72): Async function
- MessageBusAdapter.publish (line 99): Async function, High complexity
- MessageBusAdapter.subscribe (line 170): Async function
- MessageBusAdapter.message_handler (line 187): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/integrations/hermes/memory_adapter/core/service.py
- HermesMemoryService (line 28): Class definition
- HermesMemoryService.add (line 89): Async function
- HermesMemoryService.search (line 114): Async function
- HermesMemoryService.get_relevant_context (line 141): Async function
- HermesMemoryService.get_namespaces (line 165): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/integrations/hermes/memory_adapter/utils/helpers.py
- format_conversation (line 14): Public function
- generate_memory_id (line 40): Public function
- validate_namespace (line 54): Public function
- filter_forgotten_content (line 81): Public function
- format_context (line 115): High complexity

### /Users/cskoons/projects/github/Tekton/Engram/engram/integrations/hermes/memory_adapter/utils/fallback.py
- FallbackStorage (line 17): Class definition
- FallbackStorage.initialize_namespace (line 59): Public function
- FallbackStorage.initialize_compartment (line 69): Public function
- FallbackStorage.add_memory (line 79): Public function
- FallbackStorage.search (line 113): Public function

### /Users/cskoons/projects/github/Tekton/Engram/engram/integrations/hermes/memory_adapter/operations/memory.py
- add_memory (line 14): Async function
- clear_namespace (line 79): Async function, Has side effects
- write_session_memory (line 122): Async function
- keep_memory (line 152): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/integrations/hermes/memory_adapter/operations/search.py
- search_memories (line 17): Async function, High complexity
- get_relevant_context (line 128): Async function
- get_namespaces (line 174): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/integrations/hermes/memory_adapter/compartments/manager.py
- CompartmentManager (line 17): Class definition
- CompartmentManager.create_compartment (line 68): Async function
- CompartmentManager.activate_compartment (line 107): Async function
- CompartmentManager.deactivate_compartment (line 144): Async function
- CompartmentManager.set_compartment_expiration (line 177): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/controllers/core_memory.py
- query_memory (line 26): Async function
- store_memory (line 50): Async function
- store_conversation (line 75): Async function
- get_context (line 105): Async function
- clear_namespace (line 130): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/controllers/nexus.py
- start_nexus_session (line 26): Async function
- end_nexus_session (line 43): Async function
- process_message (line 60): Async function
- store_nexus_memory (line 112): Async function
- forget_nexus_memory (line 148): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/controllers/clients.py
- list_clients (line 21): Async function
- client_status (line 35): Async function
- cleanup_idle_clients (line 53): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/controllers/structured.py
- add_structured_memory (line 23): Async function
- add_auto_categorized_memory (line 59): Async function
- get_structured_memory (line 98): Async function
- search_structured_memory (line 118): Async function
- get_memory_digest (line 153): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/controllers/http_wrapper.py
- http_store_memory (line 26): Async function
- http_store_thinking (line 52): Async function
- http_store_longterm (line 74): Async function
- http_query_memory (line 96): Async function
- http_get_context (line 118): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/controllers/compartments.py
- create_compartment (line 22): Async function
- store_in_compartment (line 41): Async function
- activate_compartment (line 83): Async function
- deactivate_compartment (line 97): Async function
- list_compartments (line 111): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/controllers/root.py
- root (line 23): Async function
- health_check (line 38): Async function

### /Users/cskoons/projects/github/Tekton/Engram/engram/api/controllers/private.py
- keep_memory (line 22): Async function
- store_private (line 37): Async function
- get_private (line 54): Async function
- list_private (line 72): Async function
- delete_private (line 85): Async function

### /Users/cskoons/projects/github/Tekton/Engram/ollama/bridge/memory/handler.py
- MemoryHandler (line 21): Class definition
- MemoryHandler.store_memory (line 57): Public function
- MemoryHandler.get_recent_memories (line 70): Public function
- MemoryHandler.search_memories (line 83): Public function
- MemoryHandler.get_context_memories (line 96): Public function

### /Users/cskoons/projects/github/Tekton/Engram/ollama/bridge/memory/operations.py
- detect_memory_operations (line 12): Public function
- format_memory_operations_report (line 66): High complexity

### /Users/cskoons/projects/github/Tekton/Engram/ollama/bridge/utils/pattern_matching.py
- detect_all_operations (line 10): Public function
- format_operations_report (line 51): Public function

### /Users/cskoons/projects/github/Tekton/Engram/ollama/bridge/utils/helpers.py
- colorize (line 10): Public function
- print_colored (line 35): Public function
- set_environment_variables (line 39): Public function
- format_chat_message (line 48): Public function
- should_save_to_memory (line 66): Public function

### /Users/cskoons/projects/github/Tekton/Engram/ollama/bridge/cli/args.py
- parse_args (line 10): Public function
- display_args (line 30): Public function

### /Users/cskoons/projects/github/Tekton/Engram/ollama/bridge/cli/commands.py
- process_special_command (line 11): High complexity
- display_help (line 76): Public function

### /Users/cskoons/projects/github/Tekton/Engram/ollama/bridge/api/models.py
- get_model_capabilities (line 39): Public function
- get_memory_system_prompt (line 43): Public function
- get_communication_system_prompt (line 62): Public function
- get_combined_system_prompt (line 77): Public function
- get_system_prompt (line 93): Public function

### /Users/cskoons/projects/github/Tekton/Engram/ollama/bridge/api/client.py
- call_ollama_api (line 15): Public function
- check_ollama_status (line 44): Public function
- pull_model (line 66): Public function

### /Users/cskoons/projects/github/Tekton/Engram/ollama/bridge/communication/dialog.py
- DialogManager (line 17): Class definition
- DialogManager.enter_dialog_mode (line 29): Public function
- DialogManager.exit_dialog_mode (line 67): Public function
- DialogManager.check_for_messages (line 77): High complexity
- DialogManager.get_user_input_with_timeout (line 219): Public function

### /Users/cskoons/projects/github/Tekton/Engram/ollama/bridge/communication/messenger.py
- Messenger (line 16): Class definition
- Messenger.send_message (line 24): Has side effects, High complexity
- Messenger.send_message (line 35): Async function
- Messenger.check_messages (line 70): Has side effects, High complexity
- Messenger.get_messages (line 81): Async function

### /Users/cskoons/projects/github/Tekton/Engram/vector/lancedb/adapter.py
- LanceDBAdapter (line 36): Class definition
- LanceDBAdapter.store (line 108): Has side effects
- LanceDBAdapter.search (line 146): Public function
- LanceDBAdapter.semantic_search (line 178): Public function
- LanceDBAdapter.get_compartments (line 210): Public function

### /Users/cskoons/projects/github/Tekton/Engram/vector/lancedb/install.py
- check_python_version (line 21): Public function
- detect_platform (line 30): Public function
- check_dependencies (line 64): Public function
- install_lancedb (line 108): Public function
- setup_memory_directory (line 134): Public function

### /Users/cskoons/projects/github/Tekton/Engram/vector/lancedb/vector_store/embedding/simple.py
- SimpleEmbedding (line 17): Class definition
- SimpleEmbedding.encode (line 58): High complexity
- SimpleEmbedding.similarity (line 109): Public function

### /Users/cskoons/projects/github/Tekton/Engram/vector/lancedb/vector_store/utils/logging.py
- configure_path (line 11): Has side effects
- get_logger (line 22): Public function
- log_versions (line 45): High complexity

### /Users/cskoons/projects/github/Tekton/Engram/vector/lancedb/vector_store/utils/metadata.py
- MetadataCache (line 16): Class definition
- MetadataCache.get_metadata_path (line 31): Public function
- MetadataCache.load (line 43): Has side effects
- MetadataCache.save (line 72): Has side effects
- MetadataCache.add_entries (line 96): Has side effects

### /Users/cskoons/projects/github/Tekton/Engram/vector/lancedb/vector_store/operations/crud.py
- create_compartment (line 17): Has side effects, High complexity
- add_to_compartment (line 90): Has side effects, High complexity
- save_compartment (line 204): Has side effects
- delete_compartment (line 235): Public function

### /Users/cskoons/projects/github/Tekton/Engram/vector/lancedb/vector_store/search/vector.py
- vector_search (line 16): Public function
- get_by_id (line 87): Public function

### /Users/cskoons/projects/github/Tekton/Engram/vector/lancedb/vector_store/search/text.py
- text_search (line 14): Public function

### /Users/cskoons/projects/github/Tekton/Engram/vector/lancedb/vector_store/base/store.py
- VectorStore (line 29): Class definition
- VectorStore.create_compartment (line 108): Public function
- VectorStore.get_compartments (line 124): Public function
- VectorStore.add (line 141): Public function
- VectorStore.save (line 175): Public function
