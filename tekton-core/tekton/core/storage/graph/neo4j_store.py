"""
Neo4j storage adapter for Tekton.

This module provides a Neo4j implementation of the BaseGraphStorage
interface, allowing Tekton components to store and query graph data.
"""

from tekton.core.storage.graph.neo4j import Neo4jGraphStore

# Re-export for backward compatibility
__all__ = ["Neo4jGraphStore"]