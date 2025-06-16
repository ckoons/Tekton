"""
MCP capabilities for Engram Memory Management System.

This module defines the Model Context Protocol capabilities that Engram provides
for memory operations, structured memory management, and nexus processing.
"""

from typing import Dict, Any, List
from tekton.mcp.fastmcp.schema import MCPCapability


class MemoryOperationsCapability(MCPCapability):
    """Capability for core memory storage and retrieval operations."""
    
    name = "memory_operations"
    description = "Store, retrieve, and manage memories with various storage backends"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "store_memory",
            "query_memory",
            "get_memory_context",
            "update_memory",
            "delete_memory",
            "search_memories",
            "get_memory_by_id",
            "bulk_store_memories",
            "get_memory_statistics"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "memory_management",
            "provider": "engram",
            "requires_auth": False,
            "rate_limited": True,
            "storage_backends": ["faiss", "lancedb", "memory", "file"],
            "memory_types": ["conversation", "fact", "procedure", "episodic", "semantic"],
            "search_methods": ["vector", "keyword", "hybrid", "semantic"],
            "encoding_models": ["sentence_transformers", "openai", "custom"],
            "memory_formats": ["text", "structured", "json", "binary"]
        }


class StructuredMemoryCapability(MCPCapability):
    """Capability for structured and categorized memory operations."""
    
    name = "structured_memory"
    description = "Manage categorized, hierarchical, and structured memory systems"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "add_structured_memory",
            "get_structured_memory",
            "update_structured_memory",
            "delete_structured_memory",
            "search_structured_memory",
            "categorize_memory",
            "create_memory_hierarchy",
            "link_memories",
            "get_memory_category"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "structured_data",
            "provider": "engram",
            "requires_auth": False,
            "structure_types": ["hierarchical", "categorical", "graph", "temporal"],
            "categorization_methods": ["automatic", "manual", "hybrid", "ml_based"],
            "relationship_types": ["parent_child", "sibling", "reference", "temporal"],
            "indexing_strategies": ["category", "hierarchy", "content", "metadata"],
            "query_languages": ["sql_like", "graph", "natural_language"]
        }


class NexusOperationsCapability(MCPCapability):
    """Capability for Nexus message processing and integration."""
    
    name = "nexus_operations"
    description = "Process Nexus messages and integrate with the Tekton ecosystem"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "process_nexus_message",
            "store_nexus_data",
            "query_nexus_memories",
            "integrate_with_hermes",
            "sync_component_memories",
            "extract_memory_insights",
            "correlate_memories",
            "generate_memory_summaries"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "system_integration",
            "provider": "engram",
            "requires_auth": False,
            "message_types": ["component_events", "user_interactions", "system_logs"],
            "integration_protocols": ["http", "websocket", "message_queue"],
            "processing_modes": ["realtime", "batch", "streaming"],
            "correlation_algorithms": ["similarity", "temporal", "semantic", "contextual"],
            "summary_techniques": ["extractive", "abstractive", "statistical"]
        }


class VectorStoreCapability(MCPCapability):
    """Capability for vector-based memory storage and similarity search."""
    
    name = "vector_store"
    description = "Manage vector embeddings and perform similarity-based memory retrieval"
    version = "1.0.0"
    
    @classmethod
    def get_supported_operations(cls) -> List[str]:
        """Get list of supported operations."""
        return [
            "store_vector_memory",
            "similarity_search",
            "vector_query",
            "update_vector_embedding",
            "delete_vector_memory",
            "get_similar_memories",
            "cluster_memories",
            "dimension_reduction",
            "vector_statistics"
        ]
    
    @classmethod
    def get_capability_metadata(cls) -> Dict[str, Any]:
        """Get capability metadata."""
        return {
            "category": "vector_operations",
            "provider": "engram",
            "requires_auth": False,
            "vector_backends": ["faiss", "lancedb", "chroma", "pinecone"],
            "similarity_metrics": ["cosine", "euclidean", "dot_product", "manhattan"],
            "embedding_dimensions": [384, 768, 1024, 1536],
            "indexing_algorithms": ["flat", "ivf", "hnsw", "lsh"],
            "clustering_methods": ["kmeans", "dbscan", "hierarchical", "spectral"]
        }


# Export all capabilities
__all__ = [
    "MemoryOperationsCapability",
    "StructuredMemoryCapability",
    "NexusOperationsCapability",
    "VectorStoreCapability"
]