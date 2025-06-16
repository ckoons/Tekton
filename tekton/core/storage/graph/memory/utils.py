"""
Utility functions for memory graph store.
"""

import os
import json
import logging
import copy
from typing import Dict, Any, List, Optional, Set, Tuple, Union

# Configure logger
logger = logging.getLogger(__name__)

def save_to_json(data: Dict[str, Any], filepath: str) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        filepath: Path to save file
        
    Returns:
        True if successful
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving data to {filepath}: {e}")
        return False

def load_from_json(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load data from a JSON file.
    
    Args:
        filepath: Path to load file from
        
    Returns:
        Loaded data or None if error
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Error loading data from {filepath}: {e}")
        return None

def get_edge_key(source_id: str, target_id: str, edge_type: str) -> tuple:
    """
    Create a unique key for an edge.
    
    Args:
        source_id: Source node ID
        target_id: Target node ID
        edge_type: Edge type
        
    Returns:
        Tuple key
    """
    return (source_id, target_id, edge_type)

def create_deep_copy(data: Any) -> Any:
    """
    Create a deep copy of data to avoid reference issues.
    
    Args:
        data: Data to copy
        
    Returns:
        Deep copy of data
    """
    return copy.deepcopy(data)

def generate_edge_id(source_id: str, edge_type: str, target_id: str) -> str:
    """
    Generate a deterministic edge ID.
    
    Args:
        source_id: Source node ID
        edge_type: Edge type
        target_id: Target node ID
        
    Returns:
        Generated edge ID
    """
    return f"{source_id}__{edge_type}__{target_id}"