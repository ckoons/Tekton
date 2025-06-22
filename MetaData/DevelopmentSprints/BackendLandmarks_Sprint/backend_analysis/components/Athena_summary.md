# Athena Analysis Summary

**Generated**: 2025-06-21T17:26:06.019484

## Statistics
- Files analyzed: 54
- Functions: 252
- Classes: 48
- Landmarks identified: 277
- API endpoints: 39
- MCP tools: 20

## Patterns Found
- fastapi
- singleton
- async
- error_handling
- mcp
- websocket

## High Priority Landmarks

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/query_engine.py
- QueryEngine (line 35): Class definition
- QueryEngine.initialize_mcp (line 61): Async function
- QueryEngine.query (line 71): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/relationship.py
- Relationship (line 11): Class definition
- Relationship.add_property (line 50): Public function
- Relationship.get_property (line 66): Public function
- Relationship.get_property_with_confidence (line 79): Public function
- Relationship.set_bidirectional (line 92): Public function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/engine.py
- KnowledgeEngine (line 45): Class definition
- KnowledgeEngine.initialize (line 73): Async function, High complexity
- KnowledgeEngine.shutdown (line 142): Async function
- KnowledgeEngine.add_entity (line 161): Async function
- KnowledgeEngine.get_entity (line 182): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/entity_manager.py
- EntityMergeStrategy (line 33): Class definition
- EntityManager (line 43): Class definition
- EntityManager.initialize_mcp (line 71): Async function
- EntityManager.merge_entities (line 81): Async function, High complexity
- EntityManager.find_duplicate_entities (line 311): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/entity.py
- Entity (line 11): Class definition
- Entity.add_alias (line 49): Public function
- Entity.add_property (line 59): Public function
- Entity.get_property (line 75): Public function
- Entity.get_property_with_confidence (line 88): Public function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/athena_component.py
- AthenaComponent (line 12): Class definition
- AthenaComponent.get_capabilities (line 36): Public function
- AthenaComponent.get_metadata (line 46): Public function

### /Users/cskoons/projects/github/Tekton/Athena/athena/models/__init__.py
- EntityModel (line 12): Class definition

### /Users/cskoons/projects/github/Tekton/Athena/athena/api/app.py
- startup_callback (line 51): Async function
- health (line 93): Async function
- ready (line 99): Async function
- discovery (line 111): Async function
- global_exception_handler (line 174): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/api/dependencies.py
- get_client_id (line 19): Async function
- get_knowledge_engine (line 25): Async function
- get_entity_manager (line 33): Async function
- get_query_engine (line 40): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/mcp/hermes_bridge.py
- AthenaMCPBridge (line 16): Class definition
- AthenaMCPBridge.initialize (line 31): Async function
- AthenaMCPBridge.register_default_tools (line 56): Async function
- AthenaMCPBridge.register_fastmcp_tools (line 71): Async function
- AthenaMCPBridge.register_fastmcp_tool (line 84): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/mcp/tools.py
- mcp_tool (line 22): Public function
- decorator (line 23): Public function
- mcp_capability (line 27): Public function
- decorator (line 28): Public function
- search_entities (line 49): Async function, MCP tool

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/mcp/capabilities.py
- KnowledgeGraphCapability (line 12): Class definition
- KnowledgeGraphCapability.get_supported_operations (line 20): Public function
- KnowledgeGraphCapability.get_capability_metadata (line 36): Public function
- QueryEngineCapability (line 51): Class definition
- QueryEngineCapability.get_supported_operations (line 59): Public function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/neo4j/config.py
- Neo4jConfig (line 12): Class definition
- Neo4jConfig.from_env (line 29): Public function
- Neo4jConfig.from_dict (line 42): Public function
- Neo4jConfig.to_dict (line 54): Public function
- Neo4jConfig.get_connection_config (line 66): Public function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/neo4j/adapter.py
- Neo4jAdapter (line 34): Class definition
- Neo4jAdapter.connect (line 71): Async function
- GraphDBWrapper (line 115): Class definition
- GraphDBWrapper.add_node (line 116): Async function
- GraphDBWrapper.get_node (line 119): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/memory/persistence.py
- load_data (line 17): Async function, Has side effects, High complexity
- save_data (line 57): Async function, Has side effects, High complexity

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/memory/path_ops.py
- find_paths (line 16): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/memory/entity_ops.py
- create_entity (line 14): Async function
- get_entity (line 29): Async function
- update_entity (line 50): Async function
- delete_entity (line 68): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/memory/adapter.py
- MemoryAdapter (line 38): Class definition
- MemoryAdapter.connect (line 60): Async function
- MemoryAdapter.disconnect (line 79): Async function
- MemoryAdapter.initialize_schema (line 95): Async function
- MemoryAdapter.create_entity (line 106): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/memory/relationship_ops.py
- create_relationship (line 14): Async function
- get_relationship (line 34): Async function
- update_relationship (line 56): Async function
- delete_relationship (line 75): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/memory/query_ops.py
- search_entities (line 15): Async function, High complexity
- get_entity_relationships (line 59): Async function, High complexity
- execute_query (line 107): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/neo4j/operations/path_ops.py
- find_paths (line 16): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/neo4j/operations/entity_ops.py
- create_entity (line 15): Async function
- get_entity (line 47): Async function
- update_entity (line 87): Async function
- delete_entity (line 126): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/neo4j/operations/relationship_ops.py
- create_relationship (line 15): Async function
- get_relationship (line 53): Async function
- update_relationship (line 97): Async function
- delete_relationship (line 136): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/neo4j/operations/query_ops.py
- search_entities (line 16): Async function
- get_entity_relationships (line 66): Async function, High complexity
- execute_query (line 174): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/core/graph/neo4j/operations/count_ops.py
- count_entities (line 11): Async function
- count_relationships (line 32): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/integrations/hermes/knowledge_adapter.py
- HermesKnowledgeAdapter (line 35): Class definition
- HermesKnowledgeAdapter.initialize (line 61): Async function
- HermesKnowledgeAdapter.register_with_hermes (line 75): Async function
- HermesKnowledgeAdapter.unregister_from_hermes (line 202): Async function
- HermesKnowledgeAdapter.add_entity (line 231): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/integrations/hermes/register_capabilities.py
- HermesClient (line 22): Class definition
- HermesClient.register_component (line 25): Async function
- HermesClient.register_capability (line 30): Async function
- register_capabilities (line 37): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/integrations/hermes/memory_adapter.py
- HermesKnowledgeAdapter (line 17): Class definition
- HermesKnowledgeAdapter.initialize (line 35): Async function
- HermesKnowledgeAdapter.verify_fact (line 41): Async function
- HermesKnowledgeAdapter.extract_entities (line 79): Async function
- HermesKnowledgeAdapter.enrich_memory (line 112): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Athena/athena/api/endpoints/query.py
- execute_query (line 22): Async function
- get_available_query_modes (line 67): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/api/endpoints/knowledge_graph.py
- get_engine (line 25): Async function
- get_status (line 30): Async function
- create_entity (line 37): Async function
- get_entity (line 50): Async function
- update_entity (line 61): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/api/endpoints/llm_integration.py
- initialize_templates (line 59): Public function
- get_knowledge_context (line 207): Async function
- knowledge_chat (line 257): Async function
- stream_knowledge_chat (line 323): Async function
- generate_stream (line 332): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/api/endpoints/visualization.py
- get_visualization_data (line 25): Async function, High complexity
- get_subgraph (line 104): Async function
- create_custom_visualization (line 138): Async function, High complexity
- get_available_layouts (line 206): Async function
- get_node_subgraph (line 214): Async function, High complexity

### /Users/cskoons/projects/github/Tekton/Athena/athena/api/endpoints/mcp.py
- AthenaMCPRequest (line 64): Class definition
- AthenaMCPResponse (line 69): Class definition
- process_message (line 77): Async function
- get_capabilities_func (line 164): Async function
- get_tools_func (line 168): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/api/endpoints/entities.py
- create_entity (line 25): Async function
- get_entity (line 45): Async function
- update_entity (line 58): Async function
- delete_entity (line 82): Async function, Has side effects
- search_entities (line 101): Async function

### /Users/cskoons/projects/github/Tekton/Athena/athena/api/models/query.py
- QueryRequest (line 13): Class definition
- QueryResponse (line 61): Class definition

### /Users/cskoons/projects/github/Tekton/Athena/athena/api/models/llm.py
- KnowledgeContextRequest (line 16): Class definition
- KnowledgeContextResponse (line 24): Class definition
- KnowledgeChatRequest (line 37): Class definition
- KnowledgeChatResponse (line 47): Class definition
- EntityExtractionRequest (line 60): Class definition

### /Users/cskoons/projects/github/Tekton/Athena/athena/api/models/visualization.py
- VisualizationLayout (line 17): Class definition
- GraphVisualizationRequest (line 26): Class definition
- GraphVisualizationResponse (line 39): Class definition
- SubgraphRequest (line 49): Class definition
- SubgraphResponse (line 59): Class definition

### /Users/cskoons/projects/github/Tekton/Athena/athena/api/models/entity.py
- EntityBase (line 14): Class definition
- EntityCreate (line 20): Class definition
- EntityCreate.to_domain_entity (line 26): Public function
- EntityUpdate (line 43): Class definition
- EntityResponse (line 49): Class definition
