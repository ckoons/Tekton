"""
Storage factory for Tekton components.

This module provides factory functions for creating storage instances
based on specified storage types and hardware capabilities.
"""

import os
import platform
import importlib
import logging
from typing import Dict, Type, Any, Optional, List, Union

from tekton.core.storage.base import (
    BaseStorage,
    BaseVectorStorage,
    BaseGraphStorage,
    BaseKVStorage
)

logger = logging.getLogger(__name__)

# Registry of available storage implementations
VECTOR_STORAGE_REGISTRY = {
    # Tekton native implementations
    "faiss": "tekton.core.storage.vector.faiss_store.FAISSVectorStore",
    "qdrant": "tekton.core.storage.vector.qdrant_store.QdrantVectorStore",
    
    # LightRAG-inspired implementations
    "milvus": "tekton.core.storage.vector.milvus_store.MilvusVectorStore",
    "chroma": "tekton.core.storage.vector.chroma_store.ChromaVectorStore",
    "nano": "tekton.core.storage.vector.nano_store.NanoVectorStore",
    "pgvector": "tekton.core.storage.vector.pgvector_store.PGVectorStore"
}

GRAPH_STORAGE_REGISTRY = {
    # Tekton native implementations
    "neo4j": "tekton.core.storage.graph.neo4j_store.Neo4jGraphStore",
    "memory": "tekton.core.storage.graph.memory_store.MemoryGraphStore",
    
    # LightRAG-inspired implementations
    "networkx": "tekton.core.storage.graph.networkx_store.NetworkXGraphStore",
    "postgresql": "tekton.core.storage.graph.postgresql_store.PostgreSQLGraphStore",
    "age": "tekton.core.storage.graph.age_store.AGEGraphStore"
}

KV_STORAGE_REGISTRY = {
    # Tekton native implementations
    "json": "tekton.core.storage.kv.json_store.JsonKVStore",
    "memory": "tekton.core.storage.kv.memory_store.MemoryKVStore",
    
    # LightRAG-inspired implementations
    "mongodb": "tekton.core.storage.kv.mongodb_store.MongoDBKVStore",
    "redis": "tekton.core.storage.kv.redis_store.RedisKVStore",
    "postgresql": "tekton.core.storage.kv.postgresql_store.PostgreSQLKVStore"
}

def get_vector_store(
    store_type: Optional[str] = None,
    namespace: str = "default",
    embedding_dim: int = 1536,
    **kwargs
) -> BaseVectorStorage:
    """
    Factory function to create vector storage based on type and hardware.
    
    Automatically selects the best vector store type based on available
    hardware if no specific type is provided.
    
    Args:
        store_type: The type of vector store to use (optional)
        namespace: Namespace for the vector store
        embedding_dim: Dimension of vector embeddings
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured vector storage instance
        
    Raises:
        ValueError: If an unsupported store type is specified
        ImportError: If the implementation could not be loaded
    """
    # Auto-select best store type based on hardware if not specified
    if store_type is None:
        if platform.processor() == "arm" and platform.system() == "Darwin":
            # Use Qdrant for Apple Silicon
            store_type = "qdrant"
        elif os.environ.get("CUDA_VISIBLE_DEVICES") or os.environ.get("GPU_DEVICE_ORDINAL"):
            # NVIDIA GPU available
            store_type = "faiss"
        else:
            # Default to FAISS CPU
            store_type = "faiss"
            
    # Get class path from registry
    class_path = VECTOR_STORAGE_REGISTRY.get(store_type.lower())
    if not class_path:
        # Fall back to faiss if requested type isn't available
        logger.warning(f"Unsupported vector store type: {store_type}, falling back to FAISS")
        class_path = VECTOR_STORAGE_REGISTRY["faiss"]
    
    # Import and instantiate
    try:
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        store_class = getattr(module, class_name)
        
        # Prepare constructor arguments
        init_kwargs = {
            "namespace": namespace,
            "embedding_dim": embedding_dim,
            **kwargs
        }
        
        return store_class(**init_kwargs)
    except (ImportError, AttributeError) as e:
        # Try fallback if the requested implementation failed
        if store_type.lower() != "faiss":
            logger.warning(f"Failed to load {store_type} vector store: {e}, trying FAISS instead")
            return get_vector_store("faiss", namespace, embedding_dim, **kwargs)
        else:
            raise ImportError(f"Failed to load vector store: {e}")

def get_graph_store(
    store_type: Optional[str] = None,
    namespace: str = "default",
    **kwargs
) -> BaseGraphStorage:
    """
    Factory function to create graph storage.
    
    Args:
        store_type: The type of graph store to use (optional)
        namespace: Namespace for the graph store
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured graph storage instance
        
    Raises:
        ValueError: If an unsupported store type is specified
        ImportError: If the implementation could not be loaded
    """
    # Use Neo4j by default if available, otherwise memory store
    if store_type is None:
        if os.environ.get("NEO4J_URI"):
            store_type = "neo4j"
        else:
            store_type = "memory"
            
    # Get class path from registry
    class_path = GRAPH_STORAGE_REGISTRY.get(store_type.lower())
    if not class_path:
        # Fall back to memory if requested type isn't available
        logger.warning(f"Unsupported graph store type: {store_type}, falling back to memory")
        class_path = GRAPH_STORAGE_REGISTRY["memory"]
    
    # Import and instantiate
    try:
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        store_class = getattr(module, class_name)
        
        # Prepare constructor arguments
        init_kwargs = {
            "namespace": namespace,
            **kwargs
        }
        
        return store_class(**init_kwargs)
    except (ImportError, AttributeError) as e:
        # Try fallback if the requested implementation failed
        if store_type.lower() != "memory":
            logger.warning(f"Failed to load {store_type} graph store: {e}, using memory store instead")
            return get_graph_store("memory", namespace, **kwargs)
        else:
            raise ImportError(f"Failed to load graph store: {e}")

def get_kv_store(
    store_type: Optional[str] = None,
    namespace: str = "default",
    **kwargs
) -> BaseKVStorage:
    """
    Factory function to create key-value storage.
    
    Args:
        store_type: The type of KV store to use (optional)
        namespace: Namespace for the KV store
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured KV storage instance
        
    Raises:
        ValueError: If an unsupported store type is specified
        ImportError: If the implementation could not be loaded
    """
    # Use JSON by default if no specific type is specified
    if store_type is None:
        store_type = "json"
            
    # Get class path from registry
    class_path = KV_STORAGE_REGISTRY.get(store_type.lower())
    if not class_path:
        # Fall back to json if requested type isn't available
        logger.warning(f"Unsupported KV store type: {store_type}, falling back to JSON")
        class_path = KV_STORAGE_REGISTRY["json"]
    
    # Import and instantiate
    try:
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        store_class = getattr(module, class_name)
        
        # Prepare constructor arguments
        init_kwargs = {
            "namespace": namespace,
            **kwargs
        }
        
        return store_class(**init_kwargs)
    except (ImportError, AttributeError) as e:
        # Try fallback if the requested implementation failed
        if store_type.lower() != "json":
            logger.warning(f"Failed to load {store_type} KV store: {e}, using JSON store instead")
            return get_kv_store("json", namespace, **kwargs)
        else:
            raise ImportError(f"Failed to load KV store: {e}")

def create_storage_from_config(config: Dict[str, Any]) -> Dict[str, BaseStorage]:
    """
    Create multiple storage instances from a configuration.
    
    Args:
        config: Dictionary with storage configuration
        
    Returns:
        Dictionary mapping storage names to storage instances
    """
    storages = {}
    
    # Create vector storages
    for name, cfg in config.get("vector_stores", {}).items():
        storages[name] = get_vector_store(
            store_type=cfg.get("type"),
            namespace=cfg.get("namespace", name),
            **cfg.get("config", {})
        )
        
    # Create graph storages
    for name, cfg in config.get("graph_stores", {}).items():
        storages[name] = get_graph_store(
            store_type=cfg.get("type"),
            namespace=cfg.get("namespace", name),
            **cfg.get("config", {})
        )
        
    # Create KV storages
    for name, cfg in config.get("kv_stores", {}).items():
        storages[name] = get_kv_store(
            store_type=cfg.get("type"),
            namespace=cfg.get("namespace", name),
            **cfg.get("config", {})
        )
        
    return storages