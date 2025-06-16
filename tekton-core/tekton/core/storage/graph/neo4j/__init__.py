"""
Neo4j graph storage implementation for Tekton.

This package provides a Neo4j implementation of the BaseGraphStorage
interface, allowing Tekton components to store and query graph data.
"""

from tekton.core.storage.graph.neo4j.store import Neo4jGraphStore

__all__ = ["Neo4jGraphStore"]