#!/usr/bin/env python3
"""
Fallback file-based storage implementation
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Import from the utilities
from ..utils.logging import setup_logger

# Initialize logger
logger = setup_logger("engram.memory.file")

def setup_file_storage(
    data_dir: Path,
    client_id: str,
    namespaces: List[str],
    compartments: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Set up fallback file-based storage.
    
    Args:
        data_dir: Directory for storing file data
        client_id: Client identifier
        namespaces: List of namespaces
        compartments: Dictionary of compartments
        
    Returns:
        Dictionary with file storage setup information
    """
    logger.info(f"Using fallback file-based memory implementation for client {client_id}")
    fallback_file = data_dir / f"{client_id}-memories.json"
    
    # Initialize fallback memories
    fallback_memories = {}
    
    # Load existing memories if available
    if fallback_file.exists():
        try:
            with open(fallback_file, "r") as f:
                fallback_memories = json.load(f)
        except Exception as e:
            logger.error(f"Error loading fallback memories: {e}")
            fallback_memories = {}
    
    # Initialize with empty namespaces if needed
    for namespace in namespaces:
        if namespace not in fallback_memories:
            fallback_memories[namespace] = []
            
    # Initialize compartment storage in fallback memories
    for compartment_id in compartments:
        compartment_ns = f"compartment-{compartment_id}"
        if compartment_ns not in fallback_memories:
            fallback_memories[compartment_ns] = []
    
    return {
        "file": fallback_file,
        "memories": fallback_memories
    }

def ensure_file_compartment(
    compartment_id: str,
    fallback_memories: Dict[str, List[Dict[str, Any]]]
) -> bool:
    """
    Ensure file storage exists for the given compartment.
    
    Args:
        compartment_id: ID of the compartment
        fallback_memories: Dictionary of fallback memories
        
    Returns:
        Boolean indicating success
    """
    try:
        namespace = f"compartment-{compartment_id}"
        if namespace not in fallback_memories:
            fallback_memories[namespace] = []
        return True
    except Exception as e:
        logger.error(f"Error ensuring file compartment {compartment_id}: {e}")
        return False

def add_to_file_store(
    fallback_memories: Dict[str, List[Dict[str, Any]]],
    fallback_file: Path,
    namespace: str,
    memory_id: str,
    content: str,
    metadata: Dict[str, Any]
) -> bool:
    """
    Add a memory to the file store.
    
    Args:
        fallback_memories: Dictionary of fallback memories
        fallback_file: Path to the fallback file
        namespace: Namespace to add to
        memory_id: Unique memory identifier
        content: Memory content
        metadata: Memory metadata
        
    Returns:
        Boolean indicating success
    """
    try:
        memory_obj = {
            "id": memory_id,
            "content": content,
            "metadata": metadata
        }
        
        fallback_memories.setdefault(namespace, []).append(memory_obj)
        
        # Save to file
        with open(fallback_file, "w") as f:
            json.dump(fallback_memories, f, indent=2)
        
        logger.debug(f"Added memory to fallback storage in namespace {namespace}")
        return True
    except Exception as e:
        logger.error(f"Error adding memory to fallback storage: {e}")
        return False

def clear_file_namespace(
    fallback_memories: Dict[str, List[Dict[str, Any]]],
    fallback_file: Path,
    namespace: str
) -> bool:
    """
    Clear all memories in a namespace in the file store.
    
    Args:
        fallback_memories: Dictionary of fallback memories
        fallback_file: Path to the fallback file
        namespace: Namespace to clear
        
    Returns:
        Boolean indicating success
    """
    try:
        fallback_memories[namespace] = []
        
        # Save to file
        with open(fallback_file, "w") as f:
            json.dump(fallback_memories, f, indent=2)
        
        logger.info(f"Cleared namespace {namespace} in fallback storage")
        return True
    except Exception as e:
        logger.error(f"Error clearing namespace in fallback storage: {e}")
        return False