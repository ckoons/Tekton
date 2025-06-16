"""
Utility functions for Neo4j graph store.
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple, Union, List

# Configure logger
logger = logging.getLogger(__name__)

def check_neo4j_available():
    """Check if Neo4j client is available."""
    try:
        from neo4j import AsyncGraphDatabase
        return True
    except ImportError:
        return False

def node_to_dict(node) -> Dict[str, Any]:
    """
    Convert a Neo4j node to a dictionary.
    
    Args:
        node: Neo4j node
        
    Returns:
        Dictionary representation
    """
    if node is None:
        return None
        
    # Handle different Neo4j client representations
    if hasattr(node, "properties"):
        # py2neo Node
        return dict(node.properties)
    elif hasattr(node, "items"):
        # neo4j-driver Node
        return dict(node)
    else:
        # Already a dict or similar
        return dict(node)

def relationship_to_dict(relationship) -> Dict[str, Any]:
    """
    Convert a Neo4j relationship to a dictionary.
    
    Args:
        relationship: Neo4j relationship
        
    Returns:
        Dictionary representation
    """
    if relationship is None:
        return None
        
    result = {}
    
    # Handle different Neo4j client representations
    if hasattr(relationship, "properties"):
        # py2neo Relationship
        result = dict(relationship.properties)
        result["type"] = relationship.type
    elif hasattr(relationship, "items"):
        # neo4j-driver Relationship
        result = dict(relationship)
        if hasattr(relationship, "type"):
            result["type"] = relationship.type
    else:
        # Already a dict or similar
        result = dict(relationship)
        
    return result

def parse_cypher_result(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a Neo4j result record.
    
    Args:
        record: Neo4j result record
        
    Returns:
        Dictionary with parsed values
    """
    result = {}
    
    for key, value in record.items():
        if hasattr(value, "properties") or hasattr(value, "items"):
            # Node or Relationship
            if hasattr(value, "type"):
                # Relationship
                result[key] = relationship_to_dict(value)
            else:
                # Node
                result[key] = node_to_dict(value)
        elif isinstance(value, list):
            # List of nodes or relationships
            result[key] = [
                relationship_to_dict(item) if hasattr(item, "type") else node_to_dict(item)
                for item in value
            ]
        else:
            # Primitive value
            result[key] = value
            
    return result