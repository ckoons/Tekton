"""
Neo4j Graph Adapter for Athena Knowledge Graph

This package provides integration with Neo4j graph database 
for the Athena knowledge graph through Hermes database services.
"""

from .adapter import Neo4jAdapter
from .config import Neo4jConfig

# Export main classes
__all__ = [
    'Neo4jAdapter',
    'Neo4jConfig'
]