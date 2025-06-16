"""
MCP Module for Athena

This module provides Model Context Protocol (MCP) support 
for the Athena knowledge graph engine using FastMCP.
"""

# Import capabilities
from .capabilities import (
    KnowledgeGraphCapability,
    QueryEngineCapability,
    VisualizationCapability,
    IntegrationCapability
)

# Import standardized exports
from .tools import (
    # Knowledge Graph capabilities
    search_entities,
    get_entity_by_id,
    get_entity_relationships,
    find_entity_paths,
    merge_entities,
    
    # Query capabilities
    query_knowledge_graph,
    naive_query,
    local_query,
    global_query,
    hybrid_query,
    
    # Registration functions
    register_entity_tools,
    register_query_tools,
    get_all_tools,
    get_all_capabilities
)

__all__ = [
    # Capabilities
    "KnowledgeGraphCapability",
    "QueryEngineCapability", 
    "VisualizationCapability",
    "IntegrationCapability",
    
    # Tools
    "search_entities",
    "get_entity_by_id",
    "get_entity_relationships",
    "find_entity_paths",
    "merge_entities",
    "query_knowledge_graph",
    "naive_query",
    "local_query",
    "global_query",
    "hybrid_query",
    
    # Registration functions
    "register_entity_tools",
    "register_query_tools",
    "get_all_tools",
    "get_all_capabilities"
]