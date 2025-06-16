"""
Database API Models - Request and response models for database endpoints.

This module defines the Pydantic models used for request validation and 
response serialization in the database API endpoints.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import Field
from tekton.models import TektonBaseModel


# Vector database models

class VectorStoreRequest(TektonBaseModel):
    """Model for vector storage requests."""
    vectors: List[List[float]] = Field(..., description="List of vector embeddings to store")
    metadatas: Optional[List[Dict[str, Any]]] = Field(None, description="Metadata for each vector")
    ids: Optional[List[str]] = Field(None, description="IDs for each vector")
    backend: Optional[str] = Field(None, description="Specific backend to use")

class VectorSearchRequest(TektonBaseModel):
    """Model for vector search requests."""
    query_vector: List[float] = Field(..., description="Query vector to search for")
    top_k: int = Field(5, description="Number of results to return")
    filter: Optional[Dict[str, Any]] = Field(None, description="Metadata filter")
    backend: Optional[str] = Field(None, description="Specific backend to use")

class VectorDeleteRequest(TektonBaseModel):
    """Model for vector deletion requests."""
    ids: List[str] = Field(..., description="IDs of vectors to delete")
    backend: Optional[str] = Field(None, description="Specific backend to use")

# Key-value database models

class KeyValueSetRequest(TektonBaseModel):
    """Model for key-value set requests."""
    value: Any = Field(..., description="Value to store")
    ttl: Optional[int] = Field(None, description="Time-to-live in seconds")
    backend: Optional[str] = Field(None, description="Specific backend to use")

class KeyValueDeleteRequest(TektonBaseModel):
    """Model for key-value deletion requests."""
    backend: Optional[str] = Field(None, description="Specific backend to use")

# Graph database models

class GraphAddNodeRequest(TektonBaseModel):
    """Model for graph node addition requests."""
    node_id: str = Field(..., description="ID for the node")
    labels: List[str] = Field(..., description="Labels/types for the node")
    properties: Dict[str, Any] = Field(..., description="Node properties")
    backend: Optional[str] = Field(None, description="Specific backend to use")

class GraphAddRelationshipRequest(TektonBaseModel):
    """Model for graph relationship addition requests."""
    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    type: str = Field(..., description="Relationship type")
    properties: Optional[Dict[str, Any]] = Field({}, description="Relationship properties")
    backend: Optional[str] = Field(None, description="Specific backend to use")

class GraphQueryRequest(TektonBaseModel):
    """Model for graph query requests."""
    query: str = Field(..., description="Query string (e.g., Cypher for Neo4j)")
    parameters: Optional[Dict[str, Any]] = Field({}, description="Query parameters")
    backend: Optional[str] = Field(None, description="Specific backend to use")

# Document database models

class DocumentInsertRequest(TektonBaseModel):
    """Model for document insertion requests."""
    document: Dict[str, Any] = Field(..., description="Document to insert")
    backend: Optional[str] = Field(None, description="Specific backend to use")

class DocumentFindRequest(TektonBaseModel):
    """Model for document find requests."""
    query: Dict[str, Any] = Field(..., description="Query filter")
    limit: int = Field(10, description="Maximum number of results")
    backend: Optional[str] = Field(None, description="Specific backend to use")

class DocumentUpdateRequest(TektonBaseModel):
    """Model for document update requests."""
    query: Dict[str, Any] = Field(..., description="Query filter")
    update: Dict[str, Any] = Field(..., description="Update operations")
    backend: Optional[str] = Field(None, description="Specific backend to use")

# Cache database models

class CacheSetRequest(TektonBaseModel):
    """Model for cache set requests."""
    value: Any = Field(..., description="Value to cache")
    ttl: int = Field(3600, description="Time-to-live in seconds")
    backend: Optional[str] = Field(None, description="Specific backend to use")

# Relational database models

class SqlExecuteRequest(TektonBaseModel):
    """Model for SQL execution requests."""
    query: str = Field(..., description="SQL query to execute")
    parameters: Optional[List[Any]] = Field(None, description="Query parameters")
    backend: Optional[str] = Field(None, description="Specific backend to use")