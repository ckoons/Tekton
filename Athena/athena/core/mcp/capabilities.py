"""
MCP capabilities for Athena Knowledge Graph Engine.

This module defines the Model Context Protocol capabilities that Athena provides
for knowledge management, entity operations, and graph querying.
"""

from typing import Dict, Any, List
from tekton.mcp.fastmcp.schema import MCPCapability


class KnowledgeGraphCapability(MCPCapability):
    """Capability for knowledge graph management and entity operations."""
    
    name: str = "knowledge_graph"
    description: str = "Manage entities, relationships, and knowledge structures"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "search_entities",
            "get_entity_by_id",
            "create_entity",
            "update_entity",
            "delete_entity",
            "get_entity_relationships",
            "create_relationship",
            "find_entity_paths",
            "merge_entities",
            "get_entity_history"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "knowledge_management",
            "provider": "athena",
            "requires_auth": False,
            "rate_limited": True,
            "entity_types": ["person", "concept", "document", "event", "location", "organization"],
            "relationship_types": ["related_to", "part_of", "instance_of", "caused_by", "located_in", "created_by"],
            "search_methods": ["semantic", "keyword", "fuzzy", "exact"],
            "storage_backends": ["memory", "neo4j"],
            "query_languages": ["cypher", "natural_language"]
        }


class QueryEngineCapability(MCPCapability):
    """Capability for advanced querying and graph analysis."""
    
    name: str = "query_engine"
    description: str = "Execute complex queries and analyze knowledge graphs"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "query_knowledge_graph",
            "naive_query",
            "local_query", 
            "global_query",
            "hybrid_query",
            "semantic_search",
            "path_analysis",
            "centrality_analysis",
            "clustering_analysis"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "graph_analysis",
            "provider": "athena",
            "requires_auth": False,
            "query_types": ["semantic", "structural", "path", "aggregate", "temporal"],
            "analysis_methods": ["centrality", "clustering", "community_detection", "similarity"],
            "output_formats": ["json", "graph", "table", "visualization"],
            "optimization_levels": ["naive", "local", "global", "hybrid"],
            "supported_languages": ["english", "natural_language"]
        }


class VisualizationCapability(MCPCapability):
    """Capability for knowledge graph visualization and export."""
    
    name: str = "visualization"
    description: str = "Create visualizations and export knowledge graphs"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "generate_graph_visualization",
            "export_subgraph",
            "create_network_diagram",
            "generate_entity_timeline",
            "create_relationship_matrix",
            "export_graph_data"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "visualization",
            "provider": "athena",
            "requires_auth": False,
            "visualization_types": ["force_directed", "hierarchical", "circular", "timeline", "matrix"],
            "export_formats": ["json", "graphml", "gexf", "csv", "png", "svg"],
            "layout_algorithms": ["spring", "circular", "hierarchical", "random"],
            "customization_options": ["colors", "sizes", "labels", "filters", "clustering"]
        }


class IntegrationCapability(MCPCapability):
    """Capability for integration with other Tekton components."""
    
    name: str = "integration"
    description: str = "Integrate with Hermes, Ergon, and other Tekton components"
    version: str = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "sync_with_hermes",
            "import_from_ergon",
            "export_to_prometheus",
            "connect_to_engram",
            "register_with_hermes",
            "health_check"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "integration",
            "provider": "athena",
            "requires_auth": False,
            "supported_components": ["hermes", "ergon", "prometheus", "engram", "rhetor"],
            "integration_types": ["sync", "import", "export", "stream", "webhook"],
            "data_formats": ["json", "rdf", "owl", "turtle", "n3"],
            "protocol_support": ["http", "websocket", "mcp", "fastmcp"]
        }


# Export all capabilities
__all__ = [
    "KnowledgeGraphCapability",
    "QueryEngineCapability",
    "VisualizationCapability", 
    "IntegrationCapability"
]