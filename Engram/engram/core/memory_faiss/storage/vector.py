#!/usr/bin/env python3
"""
Vector storage implementation using FAISS
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Import from the utilities
from ..utils.logging import setup_logger

# Initialize logger
logger = setup_logger("engram.memory.vector")

# Check if fallback mode is forced
USE_FALLBACK = os.environ.get('ENGRAM_USE_FALLBACK', '').lower() in ('1', 'true', 'yes')

# Try to import vector database components (optional dependencies)
HAS_VECTOR_DB = False
VECTOR_DB_NAME = None
VECTOR_DB_VERSION = None

if not USE_FALLBACK:
    # Import FAISS for vector-based memory
    try:
        import faiss
        import numpy as np
        from engram.core.vector_store import VectorStore
        from engram.core.simple_embedding import SimpleEmbedding
        
        HAS_VECTOR_DB = True
        VECTOR_DB_NAME = "faiss"
        
        # Get version if available
        try:
            VECTOR_DB_VERSION = faiss.__version__
        except AttributeError:
            VECTOR_DB_VERSION = "unknown"
        
        logger.info(f"Vector storage library found: {VECTOR_DB_NAME} {VECTOR_DB_VERSION}")
        logger.info("Using vector-based memory implementation with FAISS")
    except ImportError:
        HAS_VECTOR_DB = False
        logger.warning("FAISS not found, using fallback file-based implementation")
        logger.info("Memory will still work but without vector search capabilities")

def setup_vector_storage(
    data_dir: Path,
    client_id: str,
    namespaces: List[str],
    compartments: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Set up vector storage using FAISS.
    
    Args:
        data_dir: Directory for storing vector data
        client_id: Client identifier
        namespaces: List of namespaces
        compartments: Dictionary of compartments
        
    Returns:
        Dictionary with vector storage setup information
    """
    if not HAS_VECTOR_DB:
        return {
            "available": False,
            "store": None,
            "model": None,
            "collections": {},
            "dimension": 128
        }
    
    vector_db_path = str(data_dir / "vector_db")
    os.makedirs(vector_db_path, exist_ok=True)
    
    # Initialize SimpleEmbedding for embeddings
    vector_dim = 128
    vector_model = SimpleEmbedding(vector_size=vector_dim)
    
    # Initialize VectorStore
    try:
        vector_store = VectorStore(
            data_path=vector_db_path,
            dimension=vector_dim
        )
        
        # Initialize namespace collections
        namespace_collections = {}
        
        # Initialize collections for each namespace
        for namespace in namespaces:
            collection_name = f"engram-{client_id}-{namespace}"
            namespace_collections[namespace] = collection_name
            
            # Try to load existing compartment
            loaded = vector_store.load(collection_name)
            if not loaded:
                # Create empty compartment with placeholder
                logger.info(f"Creating new FAISS index for {collection_name}")
                vector_store.add(
                    compartment=collection_name,
                    texts=[""],
                    metadatas=[{"placeholder": True}]
                )
                # Save the compartment
                vector_store.save(collection_name)
        
        # Initialize collections for existing compartments
        for compartment_id in compartments:
            namespace = f"compartment-{compartment_id}"
            collection_name = f"engram-{client_id}-{namespace}"
            namespace_collections[namespace] = collection_name
            
            # Try to load existing compartment
            loaded = vector_store.load(collection_name)
            if not loaded:
                # Create empty compartment with placeholder
                logger.info(f"Creating new FAISS index for compartment {compartment_id}")
                vector_store.add(
                    compartment=collection_name,
                    texts=[""],
                    metadatas=[{"placeholder": True}]
                )
                vector_store.save(collection_name)
        
        logger.info(f"Initialized FAISS vector database for client {client_id}")
        logger.info(f"Using dimension: {vector_dim}")
        
        return {
            "available": True,
            "store": vector_store,
            "model": vector_model,
            "collections": namespace_collections,
            "dimension": vector_dim
        }
    except Exception as e:
        logger.error(f"Error initializing vector database: {e}")
        return {
            "available": False,
            "store": None,
            "model": None,
            "collections": {},
            "dimension": vector_dim
        }

def ensure_vector_compartment(
    compartment_id: str,
    client_id: str,
    vector_store: Any,
    namespace_collections: Dict[str, str]
) -> bool:
    """
    Ensure vector collection exists for the given compartment.
    
    Args:
        compartment_id: ID of the compartment
        client_id: Client identifier
        vector_store: Vector store instance
        namespace_collections: Mapping of namespaces to collections
        
    Returns:
        Boolean indicating success
    """
    try:
        namespace = f"compartment-{compartment_id}"
        collection_name = f"engram-{client_id}-{namespace}"
        
        # Add to namespace collections mapping
        namespace_collections[namespace] = collection_name
        
        # Try to load existing compartment
        loaded = vector_store.load(collection_name)
        if not loaded:
            # Create empty compartment with placeholder
            logger.info(f"Creating new FAISS index for compartment {compartment_id}")
            vector_store.add(
                compartment=collection_name,
                texts=[""],
                metadatas=[{"placeholder": True}]
            )
            vector_store.save(collection_name)
            
        return True
    except Exception as e:
        logger.error(f"Error creating vector collection for compartment {compartment_id}: {e}")
        return False

def add_to_vector_store(
    vector_store: Any,
    namespace: str,
    namespace_collections: Dict[str, str],
    client_id: str,
    memory_id: str,
    content: str,
    metadata: Dict[str, Any]
) -> bool:
    """
    Add a memory to the vector store.
    
    Args:
        vector_store: Vector store instance
        namespace: Namespace to add to
        namespace_collections: Mapping of namespaces to collections
        client_id: Client identifier
        memory_id: Unique memory identifier
        content: Memory content
        metadata: Memory metadata
        
    Returns:
        Boolean indicating success
    """
    try:
        # Get the appropriate collection
        collection_name = namespace_collections.get(namespace)
        if not collection_name and namespace.startswith("compartment-"):
            compartment_id = namespace[len("compartment-"):]
            collection_name = f"engram-{client_id}-compartment-{compartment_id}"
        
        if not collection_name:
            raise ValueError(f"No collection found for namespace: {namespace}")
        
        # Add to vector store
        vector_store.add(
            compartment=collection_name,
            texts=[content],
            metadatas=[{
                "id": memory_id,
                "timestamp": metadata.get("timestamp", ""),
                "client_id": metadata.get("client_id", ""),
                "namespace": namespace,
                **metadata
            }]
        )
        
        # Save the updated collection
        vector_store.save(collection_name)
        
        logger.debug(f"Added memory to vector store in namespace {namespace} with ID {memory_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding memory to vector store: {e}")
        return False

def clear_vector_namespace(
    vector_store: Any,
    namespace: str,
    namespace_collections: Dict[str, str],
    client_id: str
) -> bool:
    """
    Clear all memories in a namespace in the vector store.
    
    Args:
        vector_store: Vector store instance
        namespace: Namespace to clear
        namespace_collections: Mapping of namespaces to collections
        client_id: Client identifier
        
    Returns:
        Boolean indicating success
    """
    try:
        # Get the appropriate collection name
        collection_name = namespace_collections.get(namespace)
        if not collection_name and namespace.startswith("compartment-"):
            compartment_id = namespace[len("compartment-"):]
            collection_name = f"engram-{client_id}-compartment-{compartment_id}"
        
        if collection_name:
            # Delete and recreate the collection
            vector_store.delete(collection_name)
            
            # Create a new empty collection
            vector_store.add(
                compartment=collection_name,
                texts=[""],
                metadatas=[{"placeholder": True}]
            )
            vector_store.save(collection_name)
            
            logger.info(f"Cleared namespace {namespace} in vector storage")
            return True
        return False
    except Exception as e:
        logger.error(f"Error clearing namespace in vector storage: {e}")
        return False