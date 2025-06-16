"""
Neo4j Graph Adapter for Athena

This module has been refactored into the neo4j/ directory structure.
This file remains as a compatibility layer for backward compatibility.
"""

from .neo4j.adapter import Neo4jAdapter
from .neo4j.config import Neo4jConfig

# Re-export main classes for backward compatibility
__all__ = ['Neo4jAdapter', 'Neo4jConfig']