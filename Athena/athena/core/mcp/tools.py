"""
MCP Tools - Tool definitions for Athena MCP service.

This module provides tool definitions for the Athena MCP service,
using the FastMCP decorator-based approach.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

# Import FastMCP decorators if available
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        MCPClient
    )
    fastmcp_available = True
except ImportError:
    # Define dummy decorators for backward compatibility
    def mcp_tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
        
    def mcp_capability(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
            
    fastmcp_available = False

logger = logging.getLogger(__name__)

# Entity Management Tools

@mcp_capability(
    name="entity_management",
    description="Capability for managing entities in the knowledge graph",
    modality="knowledge"
)
@mcp_tool(
    name="SearchEntities",
    description="Search for entities in the knowledge graph",
    tags=["entity", "search", "knowledge_graph"],
    category="entity_management"
)
async def search_entities(
    query: str,
    entity_type: Optional[str] = None,
    limit: int = 10,
    min_confidence: float = 0.5,
    entity_manager: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Search for entities in the knowledge graph.
    
    Args:
        query: Search query
        entity_type: Optional entity type to filter by
        limit: Maximum number of results to return
        min_confidence: Minimum confidence score for entities
        entity_manager: Entity manager to use (injected)
        
    Returns:
        Search results
    """
    if not entity_manager:
        return {
            "error": "Entity manager not provided"
        }
        
    try:
        # Search for entities
        entities = await entity_manager.engine.search_entities(
            query, 
            entity_type=entity_type,
            limit=limit,
            min_confidence=min_confidence
        )
        
        # Format results
        results = []
        for entity in entities:
            results.append({
                "id": entity.entity_id,
                "name": entity.name,
                "type": entity.entity_type,
                "confidence": entity.confidence,
                "properties": entity.properties,
                "aliases": entity.aliases
            })
            
        return {
            "query": query,
            "entity_type": entity_type,
            "count": len(results),
            "entities": results
        }
    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        return {
            "error": f"Error searching entities: {e}"
        }

@mcp_capability(
    name="entity_management",
    description="Capability for managing entities in the knowledge graph",
    modality="knowledge"
)
@mcp_tool(
    name="GetEntityById",
    description="Get an entity by its ID",
    tags=["entity", "retrieval", "knowledge_graph"],
    category="entity_management"
)
async def get_entity_by_id(
    entity_id: str,
    entity_manager: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get an entity by its ID.
    
    Args:
        entity_id: ID of the entity to retrieve
        entity_manager: Entity manager to use (injected)
        
    Returns:
        Entity details
    """
    if not entity_manager:
        return {
            "error": "Entity manager not provided"
        }
        
    try:
        # Get entity
        entity = await entity_manager.engine.get_entity(entity_id)
        
        if not entity:
            return {
                "error": f"Entity with ID '{entity_id}' not found"
            }
            
        # Format result
        return {
            "id": entity.entity_id,
            "name": entity.name,
            "type": entity.entity_type,
            "confidence": entity.confidence,
            "properties": entity.properties,
            "aliases": entity.aliases,
            "source": entity.source
        }
    except Exception as e:
        logger.error(f"Error retrieving entity: {e}")
        return {
            "error": f"Error retrieving entity: {e}"
        }

@mcp_capability(
    name="entity_management",
    description="Capability for managing entities in the knowledge graph",
    modality="knowledge"
)
@mcp_tool(
    name="GetEntityRelationships",
    description="Get relationships for an entity",
    tags=["entity", "relationship", "knowledge_graph"],
    category="entity_management"
)
async def get_entity_relationships(
    entity_id: str,
    direction: str = "both",
    relationship_type: Optional[str] = None,
    limit: int = 10,
    entity_manager: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get relationships for an entity.
    
    Args:
        entity_id: ID of the entity
        direction: Relationship direction ('outgoing', 'incoming', or 'both')
        relationship_type: Optional relationship type to filter by
        limit: Maximum number of relationships to return
        entity_manager: Entity manager to use (injected)
        
    Returns:
        Entity relationships
    """
    if not entity_manager:
        return {
            "error": "Entity manager not provided"
        }
        
    try:
        # Get entity relationships
        relationships = await entity_manager.engine.get_entity_relationships(
            entity_id, 
            direction=direction,
            relationship_type=relationship_type,
            limit=limit
        )
        
        # Format results
        results = []
        for rel, connected_entity in relationships:
            results.append({
                "relationship_id": rel.relationship_id,
                "relationship_type": rel.relationship_type,
                "source_id": rel.source_id,
                "target_id": rel.target_id,
                "properties": rel.properties,
                "confidence": rel.confidence,
                "connected_entity": {
                    "id": connected_entity.entity_id,
                    "name": connected_entity.name,
                    "type": connected_entity.entity_type
                }
            })
            
        return {
            "entity_id": entity_id,
            "direction": direction,
            "relationship_type": relationship_type,
            "count": len(results),
            "relationships": results
        }
    except Exception as e:
        logger.error(f"Error retrieving entity relationships: {e}")
        return {
            "error": f"Error retrieving entity relationships: {e}"
        }

@mcp_capability(
    name="entity_management",
    description="Capability for managing entities in the knowledge graph",
    modality="knowledge"
)
@mcp_tool(
    name="FindEntityPaths",
    description="Find paths between entities in the knowledge graph",
    tags=["entity", "path", "knowledge_graph"],
    category="entity_management"
)
async def find_entity_paths(
    source_id: str,
    target_id: str,
    max_depth: int = 3,
    relationship_types: Optional[List[str]] = None,
    entity_manager: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Find paths between entities in the knowledge graph.
    
    Args:
        source_id: ID of the source entity
        target_id: ID of the target entity
        max_depth: Maximum path depth
        relationship_types: Optional list of relationship types to consider
        entity_manager: Entity manager to use (injected)
        
    Returns:
        Paths between entities
    """
    if not entity_manager:
        return {
            "error": "Entity manager not provided"
        }
        
    try:
        # Find paths
        paths = await entity_manager.engine.find_paths(
            source_id, 
            target_id,
            max_depth=max_depth,
            relationship_types=relationship_types
        )
        
        # Format results
        formatted_paths = []
        for path in paths:
            formatted_path = []
            
            for i, item in enumerate(path):
                if i % 2 == 0:  # Entity
                    entity = item
                    formatted_path.append({
                        "type": "entity",
                        "id": entity.entity_id,
                        "name": entity.name,
                        "entity_type": entity.entity_type
                    })
                else:  # Relationship
                    relationship = item
                    formatted_path.append({
                        "type": "relationship",
                        "id": relationship.relationship_id,
                        "relationship_type": relationship.relationship_type,
                        "source_id": relationship.source_id,
                        "target_id": relationship.target_id
                    })
                    
            formatted_paths.append(formatted_path)
            
        return {
            "source_id": source_id,
            "target_id": target_id,
            "max_depth": max_depth,
            "relationship_types": relationship_types,
            "count": len(formatted_paths),
            "paths": formatted_paths
        }
    except Exception as e:
        logger.error(f"Error finding entity paths: {e}")
        return {
            "error": f"Error finding entity paths: {e}"
        }

@mcp_capability(
    name="entity_management",
    description="Capability for managing entities in the knowledge graph",
    modality="knowledge"
)
@mcp_tool(
    name="MergeEntities",
    description="Merge multiple entities into a single entity",
    tags=["entity", "merge", "knowledge_graph"],
    category="entity_management"
)
async def merge_entities(
    source_entities: List[str],
    target_entity_name: str,
    target_entity_type: Optional[str] = None,
    merge_strategies: Optional[Dict[str, str]] = None,
    entity_manager: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Merge multiple entities into a single entity.
    
    Args:
        source_entities: List of entity IDs to merge
        target_entity_name: Name for the merged entity
        target_entity_type: Optional type for the merged entity
        merge_strategies: Optional field-specific merge strategies
        entity_manager: Entity manager to use (injected)
        
    Returns:
        Merged entity details
    """
    if not entity_manager:
        return {
            "error": "Entity manager not provided"
        }
        
    try:
        # Merge entities
        merged_entity = await entity_manager.merge_entities(
            source_entities=source_entities,
            target_entity_name=target_entity_name,
            target_entity_type=target_entity_type,
            merge_strategies=merge_strategies
        )
        
        if not merged_entity:
            return {
                "error": "Failed to merge entities"
            }
            
        # Format result
        return {
            "source_entities": source_entities,
            "target_entity": {
                "id": merged_entity.entity_id,
                "name": merged_entity.name,
                "type": merged_entity.entity_type,
                "confidence": merged_entity.confidence,
                "properties": merged_entity.properties,
                "aliases": merged_entity.aliases
            },
            "success": True
        }
    except Exception as e:
        logger.error(f"Error merging entities: {e}")
        return {
            "error": f"Error merging entities: {e}",
            "success": False
        }

# Query Engine Tools

@mcp_capability(
    name="knowledge_graph_query",
    description="Capability for querying the knowledge graph",
    modality="query"
)
@mcp_tool(
    name="QueryKnowledgeGraph",
    description="Query the knowledge graph with a specific mode",
    tags=["query", "knowledge_graph"],
    category="query"
)
async def query_knowledge_graph(
    question: str,
    mode: str = "hybrid",
    max_results: int = 10,
    max_entities: int = 5,
    relationship_depth: int = 3,
    query_engine: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Query the knowledge graph with a specific mode.
    
    Args:
        question: Query question
        mode: Query mode ('naive', 'local', 'global', 'hybrid', or 'mix')
        max_results: Maximum number of results
        max_entities: Maximum number of entities to consider
        relationship_depth: Maximum relationship depth for path-based queries
        query_engine: Query engine to use (injected)
        
    Returns:
        Query results
    """
    if not query_engine:
        return {
            "error": "Query engine not provided"
        }
        
    try:
        # Create query parameters
        from tekton.core.query.modes import QueryMode, QueryParameters
        
        # Map mode string to QueryMode enum
        mode_map = {
            "naive": QueryMode.NAIVE,
            "local": QueryMode.LOCAL,
            "global": QueryMode.GLOBAL,
            "hybrid": QueryMode.HYBRID,
            "mix": QueryMode.MIX
        }
        
        query_mode = mode_map.get(mode.lower(), QueryMode.HYBRID)
        
        parameters = QueryParameters(
            mode=query_mode,
            max_results=max_results,
            max_entities=max_entities,
            relationship_depth=relationship_depth
        )
        
        # Execute query
        results = await query_engine.query(question, parameters)
        
        return {
            "question": question,
            "mode": mode,
            "results": results,
            "context_text": results.get("context_text", ""),
            "results_count": results.get("results_count", 0)
        }
    except Exception as e:
        logger.error(f"Error querying knowledge graph: {e}")
        return {
            "error": f"Error querying knowledge graph: {e}"
        }

@mcp_capability(
    name="knowledge_graph_query",
    description="Capability for querying the knowledge graph",
    modality="query"
)
@mcp_tool(
    name="NaiveQuery",
    description="Simple keyword-based query of the knowledge graph",
    tags=["query", "naive", "knowledge_graph"],
    category="query"
)
async def naive_query(
    question: str,
    max_results: int = 10,
    query_engine: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Simple keyword-based query of the knowledge graph.
    
    Args:
        question: Query question
        max_results: Maximum number of results
        query_engine: Query engine to use (injected)
        
    Returns:
        Query results
    """
    return await query_knowledge_graph(
        question=question,
        mode="naive",
        max_results=max_results,
        query_engine=query_engine
    )

@mcp_capability(
    name="knowledge_graph_query",
    description="Capability for querying the knowledge graph",
    modality="query"
)
@mcp_tool(
    name="LocalQuery",
    description="Entity-focused query of the knowledge graph",
    tags=["query", "local", "knowledge_graph"],
    category="query"
)
async def local_query(
    question: str,
    max_results: int = 10,
    max_entities: int = 5,
    query_engine: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Entity-focused query of the knowledge graph.
    
    Args:
        question: Query question
        max_results: Maximum number of results
        max_entities: Maximum number of entities to consider
        query_engine: Query engine to use (injected)
        
    Returns:
        Query results
    """
    return await query_knowledge_graph(
        question=question,
        mode="local",
        max_results=max_results,
        max_entities=max_entities,
        query_engine=query_engine
    )

@mcp_capability(
    name="knowledge_graph_query",
    description="Capability for querying the knowledge graph",
    modality="query"
)
@mcp_tool(
    name="GlobalQuery",
    description="Relationship-focused query of the knowledge graph",
    tags=["query", "global", "knowledge_graph"],
    category="query"
)
async def global_query(
    question: str,
    max_results: int = 10,
    max_entities: int = 5,
    relationship_depth: int = 3,
    query_engine: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Relationship-focused query of the knowledge graph.
    
    Args:
        question: Query question
        max_results: Maximum number of results
        max_entities: Maximum number of entities to consider
        relationship_depth: Maximum relationship depth for path-based queries
        query_engine: Query engine to use (injected)
        
    Returns:
        Query results
    """
    return await query_knowledge_graph(
        question=question,
        mode="global",
        max_results=max_results,
        max_entities=max_entities,
        relationship_depth=relationship_depth,
        query_engine=query_engine
    )

@mcp_capability(
    name="knowledge_graph_query",
    description="Capability for querying the knowledge graph",
    modality="query"
)
@mcp_tool(
    name="HybridQuery",
    description="Combined entity and relationship query of the knowledge graph",
    tags=["query", "hybrid", "knowledge_graph"],
    category="query"
)
async def hybrid_query(
    question: str,
    max_results: int = 10,
    max_entities: int = 5,
    relationship_depth: int = 3,
    query_engine: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Combined entity and relationship query of the knowledge graph.
    
    Args:
        question: Query question
        max_results: Maximum number of results
        max_entities: Maximum number of entities to consider
        relationship_depth: Maximum relationship depth for path-based queries
        query_engine: Query engine to use (injected)
        
    Returns:
        Query results
    """
    return await query_knowledge_graph(
        question=question,
        mode="hybrid",
        max_results=max_results,
        max_entities=max_entities,
        relationship_depth=relationship_depth,
        query_engine=query_engine
    )

# Registration functions

async def register_entity_tools(entity_manager, tool_registry):
    """Register entity management tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, skipping entity tool registration")
        return
        
    # Add entity manager to tool kwargs
    search_entities.entity_manager = entity_manager
    get_entity_by_id.entity_manager = entity_manager
    get_entity_relationships.entity_manager = entity_manager
    find_entity_paths.entity_manager = entity_manager
    merge_entities.entity_manager = entity_manager
    
    # Register tools with tool registry
    await tool_registry.register_tool(search_entities._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(get_entity_by_id._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(get_entity_relationships._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(find_entity_paths._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(merge_entities._mcp_tool_meta.to_dict())
    
    logger.info("Registered entity management tools with MCP service")

async def register_query_tools(query_engine, tool_registry):
    """Register query tools with the MCP service."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, skipping query tool registration")
        return
        
    # Add query engine to tool kwargs
    query_knowledge_graph.query_engine = query_engine
    naive_query.query_engine = query_engine
    local_query.query_engine = query_engine
    global_query.query_engine = query_engine
    hybrid_query.query_engine = query_engine
    
    # Register tools with tool registry
    await tool_registry.register_tool(query_knowledge_graph._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(naive_query._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(local_query._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(global_query._mcp_tool_meta.to_dict())
    await tool_registry.register_tool(hybrid_query._mcp_tool_meta.to_dict())
    
    logger.info("Registered query tools with MCP service")

def get_all_tools(knowledge_engine=None):
    """Get all Athena MCP tools."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, returning empty tools list")
        return []
        
    from tekton.mcp.fastmcp.schema import MCPTool
    
    tools = []
    
    # Entity management tools
    tools.append(search_entities._mcp_tool_meta.to_dict())
    tools.append(get_entity_by_id._mcp_tool_meta.to_dict())
    tools.append(get_entity_relationships._mcp_tool_meta.to_dict())
    tools.append(find_entity_paths._mcp_tool_meta.to_dict())
    tools.append(merge_entities._mcp_tool_meta.to_dict())
    
    # Query tools
    tools.append(query_knowledge_graph._mcp_tool_meta.to_dict())
    tools.append(naive_query._mcp_tool_meta.to_dict())
    tools.append(local_query._mcp_tool_meta.to_dict())
    tools.append(global_query._mcp_tool_meta.to_dict())
    tools.append(hybrid_query._mcp_tool_meta.to_dict())
    
    return tools

def get_all_capabilities(knowledge_engine=None):
    """Get all Athena MCP capabilities."""
    if not fastmcp_available:
        logger.warning("FastMCP not available, returning empty capabilities list")
        return []
        
    from tekton.mcp.fastmcp.schema import MCPCapability
    
    capabilities = []
    
    # Add unique capabilities
    capability_names = set()
    
    # Entity management capability
    if "entity_management" not in capability_names:
        capabilities.append(MCPCapability(
            name="entity_management",
            description="Capability for managing entities in the knowledge graph",
            modality="knowledge"
        ))
        capability_names.add("entity_management")
    
    # Query capability
    if "knowledge_graph_query" not in capability_names:
        capabilities.append(MCPCapability(
            name="knowledge_graph_query",
            description="Capability for querying the knowledge graph",
            modality="query"
        ))
        capability_names.add("knowledge_graph_query")
    
    return capabilities