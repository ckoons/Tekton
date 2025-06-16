"""
FAISS Vector Adapter Utilities

This module provides utility functions for the FAISS vector adapter.
"""

from typing import Dict, Any


def matches_filter(vector: Dict[str, Any], filter: Dict[str, Any]) -> bool:
    """
    Check if a vector matches a metadata filter.
    
    Args:
        vector: Vector data dictionary
        filter: Metadata filter dictionary
        
    Returns:
        True if the vector matches the filter
    """
    metadata = vector.get("metadata", {})
    
    for key, value in filter.items():
        # Handle nested keys
        if "." in key:
            parts = key.split(".")
            current = metadata
            
            for part in parts[:-1]:
                if not isinstance(current, dict) or part not in current:
                    return False
                current = current[part]
            
            last_part = parts[-1]
            
            if not isinstance(current, dict) or last_part not in current:
                return False
            
            if current[last_part] != value:
                return False
        
        # Simple key
        elif key not in metadata or metadata[key] != value:
            return False
    
    return True


def rebuild_id_mappings(vectors: Dict[str, Dict[str, Any]]) -> tuple[Dict[str, int], Dict[int, str]]:
    """
    Rebuild ID to index mappings.
    
    Args:
        vectors: Dictionary of vector data
        
    Returns:
        Tuple of (id_to_index, index_to_id) mappings
    """
    id_to_index = {}
    index_to_id = {}
    
    for i, vector_id in enumerate(vectors.keys()):
        id_to_index[vector_id] = i
        index_to_id[i] = vector_id
    
    return id_to_index, index_to_id