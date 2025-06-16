# Athena MCP Integration

This document describes the Model Context Protocol (MCP) integration for Athena, the knowledge graph engine and semantic analysis system in the Tekton ecosystem.

## Overview

Athena implements FastMCP (Fast Model Context Protocol) to provide a standardized interface for knowledge graph management, entity operations, semantic querying, and graph visualization. This integration allows external systems and AI models to interact with Athena's knowledge graph capabilities through a consistent, well-defined API.

## Architecture

### Integration Approach

Athena uses an **integrated implementation** approach for MCP integration:

- **Main API Server** (`/api/*`): Provides the full Athena REST API on port 8001
- **FastMCP Integration** (`/api/mcp/v2/*`): Integrated FastMCP endpoints within the main server
- **Dual Storage Support**: Works with both in-memory and Neo4j backends

This approach ensures seamless integration while providing modern FastMCP capabilities for knowledge graph operations.

### FastMCP Implementation

The FastMCP integration includes:

1. **Tool Registration**: All tools are registered with the FastMCP registry using decorators
2. **Dependency Injection**: Core services (EntityManager, QueryEngine) are injected into tools
3. **Capability Grouping**: Tools are organized into logical capabilities for knowledge management
4. **Error Handling**: Comprehensive error handling with meaningful error messages
5. **Backend Abstraction**: Works with multiple storage backends (memory, Neo4j)

## Capabilities and Tools

### Knowledge Graph Capability

The `knowledge_graph` capability provides comprehensive CRUD operations for entities and relationships.

#### Tools

1. **search_entities**
   - Search for entities using various methods
   - Parameters: `query`, `entity_type` (optional), `search_method`, `limit`
   - Returns: Array of matching entities with relevance scores

2. **get_entity_by_id**
   - Retrieve a specific entity by its ID
   - Parameters: `entity_id`
   - Returns: Complete entity details including properties and metadata

3. **create_entity**
   - Create a new entity in the knowledge graph
   - Parameters: `name`, `type`, `properties`, `metadata` (optional)
   - Returns: Entity ID and creation details

4. **update_entity**
   - Update an existing entity's properties
   - Parameters: `entity_id`, `properties`, `metadata` (optional)
   - Returns: Update status and details

5. **delete_entity**
   - Remove an entity from the knowledge graph
   - Parameters: `entity_id`, `cascade` (optional)
   - Returns: Deletion confirmation

6. **get_entity_relationships**
   - Get all relationships for an entity
   - Parameters: `entity_id`, `direction` (optional), `relationship_type` (optional)
   - Returns: Array of relationships with connected entities

7. **create_relationship**
   - Create a relationship between two entities
   - Parameters: `source_entity_id`, `target_entity_id`, `relationship_type`, `properties`
   - Returns: Relationship ID and creation details

8. **find_entity_paths**
   - Find paths between two entities in the graph
   - Parameters: `source_entity_id`, `target_entity_id`, `max_depth`, `path_type`
   - Returns: Array of paths with nodes and relationships

9. **merge_entities**
   - Merge duplicate entities into a single entity
   - Parameters: `primary_entity_id`, `secondary_entity_ids`, `merge_strategy`
   - Returns: Merged entity details

### Query Engine Capability

The `query_engine` capability provides advanced querying and semantic analysis.

#### Tools

1. **query_knowledge_graph**
   - Execute complex queries against the knowledge graph
   - Parameters: `query`, `query_type`, `parameters`, `limit`
   - Returns: Query results with entities and relationships

2. **naive_query**
   - Simple, unoptimized query execution
   - Parameters: `query`, `entity_type`, `limit`
   - Returns: Basic query results

3. **local_query**
   - Optimized local search within entity neighborhoods
   - Parameters: `query`, `center_entity_id`, `radius`, `limit`
   - Returns: Local search results

4. **global_query**
   - Global search across the entire knowledge graph
   - Parameters: `query`, `similarity_threshold`, `limit`
   - Returns: Global search results with relevance scores

5. **hybrid_query**
   - Combination of local and global search strategies
   - Parameters: `query`, `strategy_weights`, `limit`
   - Returns: Hybrid search results

6. **semantic_search**
   - Semantic similarity-based search
   - Parameters: `query`, `embedding_model`, `similarity_threshold`, `limit`
   - Returns: Semantically similar entities

### Visualization Capability

The `visualization` capability provides graph visualization and export functions.

#### Tools

1. **generate_graph_visualization**
   - Create visual representations of graph data
   - Parameters: `entity_ids`, `layout`, `format`, `style_options`
   - Returns: Visualization data or image

2. **export_subgraph**
   - Export a portion of the graph in various formats
   - Parameters: `center_entity_id`, `radius`, `format`, `include_properties`
   - Returns: Exported graph data

3. **create_network_diagram**
   - Generate network diagrams for relationships
   - Parameters: `entity_ids`, `relationship_types`, `layout`, `format`
   - Returns: Network diagram data

4. **export_graph_data**
   - Export complete graph data in standard formats
   - Parameters: `format`, `filters`, `include_metadata`
   - Returns: Exported graph in requested format

### Integration Capability

The `integration` capability manages connections with other Tekton components.

#### Tools

1. **sync_with_hermes**
   - Synchronize knowledge graph with Hermes message bus
   - Parameters: `sync_type`, `filters`
   - Returns: Synchronization status and statistics

2. **import_from_ergon**
   - Import agent knowledge from Ergon
   - Parameters: `agent_id`, `knowledge_types`, `merge_strategy`
   - Returns: Import results and entity mappings

3. **export_to_prometheus**
   - Export planning-relevant knowledge to Prometheus
   - Parameters: `planning_context`, `export_format`
   - Returns: Export status and data summary

4. **connect_to_engram**
   - Connect with Engram for memory integration
   - Parameters: `connection_type`, `sync_settings`
   - Returns: Connection status

5. **register_with_hermes**
   - Register Athena capabilities with Hermes
   - Parameters: `service_info`, `capabilities`
   - Returns: Registration confirmation

6. **health_check**
   - Check health status of knowledge graph and connections
   - Parameters: None
   - Returns: Health status and component availability

## API Endpoints

### Standard FastMCP Endpoints

- `GET /api/mcp/v2/capabilities` - List all capabilities
- `GET /api/mcp/v2/tools` - List all tools
- `POST /api/mcp/v2/process` - Execute tools
- `GET /api/mcp/v2/health` - Health check

### Knowledge Graph Statistics

- `GET /api/mcp/v2/stats` - Get knowledge graph statistics

## Usage Examples

### Python Client Example

```python
from tekton.mcp.fastmcp.client import FastMCPClient

# Connect to Athena FastMCP
client = FastMCPClient("http://localhost:8001/api/mcp/v2")

# Create entities
ai_result = await client.call_tool("create_entity", {
    "name": "Artificial Intelligence",
    "type": "concept",
    "properties": {
        "description": "The simulation of human intelligence processes by machines",
        "category": "technology"
    }
})

ml_result = await client.call_tool("create_entity", {
    "name": "Machine Learning", 
    "type": "concept",
    "properties": {
        "description": "A subset of AI that enables computers to learn",
        "category": "technology"
    }
})

# Create relationship
relationship_result = await client.call_tool("create_relationship", {
    "source_entity_id": ai_result["entity_id"],
    "target_entity_id": ml_result["entity_id"],
    "relationship_type": "contains",
    "properties": {
        "description": "AI contains Machine Learning as a subfield"
    }
})

# Search entities
search_result = await client.call_tool("search_entities", {
    "query": "artificial intelligence",
    "search_method": "semantic",
    "limit": 10
})

print(f"Found {len(search_result['entities'])} entities")
```

### Query Examples

```python
# Semantic search
semantic_result = await client.call_tool("semantic_search", {
    "query": "machine learning algorithms",
    "similarity_threshold": 0.7,
    "limit": 20
})

# Complex graph query
query_result = await client.call_tool("query_knowledge_graph", {
    "query": "Find all concepts related to AI with high importance",
    "query_type": "semantic",
    "parameters": {
        "importance_threshold": 0.8,
        "relationship_types": ["related_to", "part_of"]
    },
    "limit": 50
})

# Find paths between entities
path_result = await client.call_tool("find_entity_paths", {
    "source_entity_id": "ai_entity_id",
    "target_entity_id": "ml_entity_id", 
    "max_depth": 3,
    "path_type": "shortest"
})
```

### Visualization Examples

```python
# Generate graph visualization
viz_result = await client.call_tool("generate_graph_visualization", {
    "entity_ids": ["entity1", "entity2", "entity3"],
    "layout": "force_directed",
    "format": "json",
    "style_options": {
        "node_colors": {"concept": "blue", "person": "green"},
        "edge_thickness": "relationship_weight"
    }
})

# Export subgraph
export_result = await client.call_tool("export_subgraph", {
    "center_entity_id": "central_concept_id",
    "radius": 2,
    "format": "graphml",
    "include_properties": True
})
```

## Installation and Setup

### Dependencies

Athena FastMCP requires:
```
tekton-core>=0.1.0
```

### Storage Backend Configuration

#### Memory Backend (Default)
```bash
export ATHENA_STORAGE_BACKEND=memory
```

#### Neo4j Backend
```bash
export ATHENA_STORAGE_BACKEND=neo4j
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password
```

### Running the Server

```bash
# Start Athena with integrated FastMCP
./run_athena.sh
```

FastMCP endpoints available at: `http://localhost:8001/api/mcp/v2`

### Configuration

Environment variables:
- `ATHENA_STORAGE_BACKEND`: Storage backend (memory, neo4j)
- `ATHENA_LOG_LEVEL`: Logging level (default: info)
- `ATHENA_PORT`: Port for server (default: 8001)
- `ATHENA_EMBEDDING_MODEL`: Model for semantic search
- `NEO4J_URI`: Neo4j connection URI (if using Neo4j backend)

## Testing

Run the comprehensive test suite:

```bash
# Test FastMCP integration
./examples/run_fastmcp_test.sh

# Test with custom URL
./examples/run_fastmcp_test.sh --url http://localhost:8001

# Test with cleanup
./examples/run_fastmcp_test.sh --cleanup
```

The test suite validates:
- Server availability and health
- All capabilities and tools
- Entity creation and management
- Relationship operations
- Query engine functionality
- Visualization capabilities
- Integration features
- Error handling

## Error Handling

All tools return consistent error responses:

```json
{
  "error": "Description of what went wrong"
}
```

Common error scenarios:
- **Entity manager not available**: Core service initialization failed
- **Entity not found**: Invalid entity ID provided
- **Storage backend error**: Database connection or operation failed
- **Invalid query**: Malformed query syntax or parameters
- **Visualization not supported**: Requested visualization format unavailable

## Integration with Other Components

### Hermes Integration

Athena automatically registers with Hermes for service discovery:

```json
{
  "name": "athena",
  "type": "knowledge_graph",
  "port": 8001,
  "health_endpoint": "/health",
  "capabilities": ["knowledge_graph", "semantic_search", "visualization"]
}
```

### Ergon Integration

Import agent knowledge and workflow data:
- Agent decision trees → Knowledge graph
- Task dependencies → Entity relationships
- Workflow patterns → Conceptual relationships

### Engram Integration

Synchronize with memory systems:
- Entity embeddings → Vector storage
- Relationship patterns → Memory associations
- Query history → Learning data

### Prometheus Integration

Export planning-relevant knowledge:
- Project entities → Planning contexts
- Dependency relationships → Task precedence
- Resource entities → Capacity planning

## Performance Considerations

- **Storage Backend**: Neo4j provides better performance for large graphs
- **Caching**: Entity and relationship caching for frequent queries
- **Indexing**: Automatic indexing of entity names and properties
- **Query Optimization**: Different query strategies for different scenarios
- **Batch Operations**: Bulk entity and relationship operations

## Security

- **Input Validation**: All tool parameters validated using Pydantic models
- **Query Sanitization**: Cypher injection protection for Neo4j queries
- **Access Control**: Configurable read/write permissions
- **Data Encryption**: Support for encrypted storage backends

## Future Enhancements

Planned improvements:
1. **Advanced Analytics**: Community detection, centrality analysis
2. **Real-time Updates**: WebSocket support for live graph changes
3. **Temporal Knowledge**: Time-based entity and relationship tracking
4. **Multi-modal Data**: Support for images, documents, and multimedia
5. **Federated Graphs**: Distributed knowledge graph support
6. **Automated Reasoning**: Logic-based inference and knowledge expansion

## Troubleshooting

### Common Issues

1. **Storage backend connection failed**
   - Check database connectivity
   - Verify credentials and permissions
   - Ensure database is running

2. **Entity not found errors**
   - Verify entity IDs are correct
   - Check if entities were successfully created
   - Ensure proper indexing

3. **Query timeout**
   - Optimize query complexity
   - Add appropriate indexes
   - Consider query strategy changes

4. **Visualization errors**
   - Check if visualization dependencies are installed
   - Verify requested format is supported
   - Reduce graph size for complex visualizations

### Debug Mode

Enable debug logging:
```bash
export ATHENA_LOG_LEVEL=debug
./run_athena.sh
```

### Health Monitoring

Monitor knowledge graph health:
```python
health_result = await client.call_tool("health_check", {})
print(f"Knowledge graph status: {health_result}")
```

## Support

For issues related to Athena FastMCP integration:
1. Check server logs for detailed error messages
2. Run the test suite to identify specific failing operations
3. Verify storage backend connectivity
4. Ensure proper environment configuration

## Conclusion

Athena FastMCP integration provides a powerful, standardized interface for knowledge graph operations within the Tekton ecosystem. The comprehensive tool set, flexible storage backends, and seamless integration capabilities make it an essential component for knowledge management, semantic analysis, and graph-based AI applications.

The integrated implementation approach ensures optimal performance while maintaining compatibility with the broader Tekton architecture, enabling sophisticated knowledge-driven applications and AI system integrations.